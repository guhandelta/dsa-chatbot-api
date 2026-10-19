"""Offline draft course plans. Eligibility is checked against current source rows.

No generated answers, arbitrary file reads, database calls or network operations.
The outline is authored data; this service never synthesizes a lesson.
"""
from copy import deepcopy
from functools import lru_cache
import json
from pathlib import Path

from app.services import curriculum, reference_library

OUTLINES_PATH = Path(__file__).resolve().parents[2] / 'data/curriculum/course-outlines.json'
ALIASES = {'c++': 'cpp', 'c#': 'csharp', 'cs': 'csharp', 'js': 'javascript',
           'ts': 'typescript', 'py': 'python', 'golang': 'go', 'html5': 'html',
           'css3': 'css', 'scss': 'css', 'sass': 'css'}


def _language(value):
    key = value.strip().lower()
    return ALIASES.get(key, key)


def _outlines():
    # Small file read afresh so edited draft plans are immediately visible.
    return json.loads(OUTLINES_PATH.read_text(encoding='utf-8'))['courses']


@lru_cache(maxsize=2)
def _source_index(reference_version, curriculum_version):
    return {
        'reference_library': {r['id']: r for r in reference_library.records()},
        'curriculum': {'corpus-' + r['id']: r for r in curriculum.records()},
    }


def _resolve(language, source):
    collection = source['collection']
    if collection == 'content_catalog':
        # Only pinned course sources reach this branch; never accept a request
        # path as a filename. Front matter and protected sections stay private.
        from app.services.content_catalog import find_path, parse_file
        from app.services.content_access import public_text
        path = find_path(source['id'])
        if path is None:
            return None
        meta = parse_file(path)
        if meta.track != 'language' or meta.language != language:
            return None
        document = public_text(path.read_text(encoding='utf-8'))
        if not document.strip():
            return None
        return {'document': document, 'metadata': {
            'language': language, 'track': 'language', 'kind': 'reference',
            'contains_answer': False, 'verified': False, 'source': 'content_catalog',
        }}
    index = _source_index(reference_library.version(), curriculum.version())
    row = index.get(collection, {}).get(source['id'])
    if row is None or not reference_library.eligible(row):
        return None
    meta = row['metadata']
    if meta.get('language') != language:
        return None
    if collection == 'reference_library' and meta.get('subject') != language:
        return None
    if collection == 'curriculum' and language not in curriculum.RELEASE_LANGUAGES:
        return None
    return {'document': row['document'], 'metadata': deepcopy(meta)}


def get_course(language: str) -> dict | None:
    """Return an isolated full draft; unavailable sources are omitted honestly."""
    language = _language(language)
    course = next((c for c in _outlines() if c['language'] == language), None)
    if course is None:
        return None
    for module in course['modules']:
        assigned = module['sources']
        module['sources'] = [s for s in assigned if _resolve(language, s) is not None]
        module['source_status'] = ('available' if assigned and len(module['sources']) == len(assigned)
                                   else 'partial' if module['sources'] else 'missing')
    course['coverage']['selected_sources'] = sum(len(m['sources']) for m in course['modules'])
    return course


def list_courses() -> list[dict]:
    """Return stable summaries, including HTML/CSS but excluding collections."""
    result = []
    for raw in _outlines():
        course = get_course(raw['language'])
        result.append({**{k: course[k] for k in (
            'language', 'title', 'description', 'status', 'assessment_status')},
            'module_count': len(course['modules']),
            'source_count': course['coverage']['selected_sources']})
    return result


def get_lesson(language: str, module_id: str, source_id: str) -> dict | None:
    """Resolve only a source explicitly assigned to this course and module."""
    language = _language(language)
    course = next((c for c in _outlines() if c['language'] == language), None)
    if course is None:
        return None
    module = next((m for m in course['modules'] if m['id'] == module_id), None)
    if module is None:
        return None
    source = next((s for s in module['sources'] if s['id'] == source_id), None)
    if source is None:
        return None
    resolved = _resolve(language, source)
    if resolved is None:
        return None
    return dict(language=language, module_id=module_id, source_id=source_id,
                title=source['title'], **resolved, status='draft')
