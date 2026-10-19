"""Draft integrity, live eligibility and module-scoped learner access."""
import json

import pytest

from app.services import course_catalog as catalog, reference_library, curriculum

LANGUAGES = {'c', 'cpp', 'csharp', 'css', 'go', 'html', 'java',
             'javascript', 'python', 'ruby', 'rust', 'typescript'}


def test_inventory_and_honest_draft_status():
    summaries = catalog.list_courses()
    assert {c['language'] for c in summaries} == LANGUAGES
    assert len(summaries) == 12
    sequences = []
    for summary in summaries:
        course = catalog.get_course(summary['language'])
        assert course['status'] == summary['status'] == 'draft'
        assert course['assessment_status'] == course['capstone']['assessment_status'] == 'missing'
        assert course['prerequisites'] and course['limitations']
        assert course['capstone']['brief'] and course['capstone']['deliverables']
        assert summary['module_count'] == len(course['modules'])
        assert summary['source_count'] == course['coverage']['selected_sources']
        seen = set()
        for module in course['modules']:
            assert module['id'] not in seen
            assert set(module['prerequisites']) <= seen
            seen.add(module['id'])
            assert module['objectives'] and module['practice_brief']
            assert module['source_status'] == 'available' and module['sources']
        sequences.append(tuple(m['title'] for m in course['modules']))
    assert len(set(sequences)) == 12


@pytest.mark.parametrize('language', sorted(LANGUAGES))
def test_every_pinned_source_resolves_to_current_safe_text(language):
    course = catalog.get_course(language)
    for module in course['modules']:
        for source in module['sources']:
            lesson = catalog.get_lesson(language, module['id'], source['id'])
            assert lesson and lesson['document'].strip()
            assert lesson['metadata']['language'] == language
            assert lesson['metadata']['contains_answer'] is False
            assert lesson['metadata']['kind'] in {'concept', 'reference'}
            assert lesson['status'] == 'draft'
            assert 'payload' not in lesson
            assert not lesson['document'].startswith('---')
            if source['collection'] == 'reference_library':
                row = next(r for r in reference_library.records() if r['id'] == source['id'])
                assert reference_library.eligible(row)
                assert row['metadata']['subject'] == language
                assert lesson['document'] == row['document']
            elif source['collection'] == 'curriculum':
                row = next(r for r in curriculum.records() if 'corpus-' + r['id'] == source['id'])
                assert reference_library.eligible(row)
                assert lesson['document'] == row['document']


@pytest.mark.parametrize('alias,language', [('cs','csharp'),('C#','csharp'),('c++','cpp'),
    ('JS','javascript'),('ts','typescript'),('scss','css'),('sass','css'),(' HTML5 ','html')])
def test_aliases(alias, language):
    assert catalog.get_course(alias) == catalog.get_course(language)


def test_unknown_and_unassigned_sources_cannot_be_read():
    assert catalog.get_course('bootstrap') is None
    assert catalog.get_course('embedded-c') is None
    assert catalog.get_course('not-a-language') is None
    course = catalog.get_course('c')
    first, second = course['modules'][:2]
    sid = second['sources'][0]['id']
    assert catalog.get_lesson('c', first['id'], sid) is None
    assert catalog.get_lesson('python', second['id'], sid) is None
    assert catalog.get_lesson('c', '../c', sid) is None
    assert catalog.get_lesson('c', second['id'], '../../.env') is None
    unsafe = next(r for r in reference_library.records() if not reference_library.eligible(r))
    assert catalog.get_lesson('c', second['id'], unsafe['id']) is None


def test_new_quarantine_removes_source_and_marks_gap(monkeypatch):
    original = reference_library.eligible
    course = catalog.get_course('c')
    module = course['modules'][1]
    sid = module['sources'][0]['id']
    monkeypatch.setattr(reference_library, 'eligible', lambda r: r['id'] != sid and original(r))
    assert catalog.get_lesson('c', module['id'], sid) is None
    updated = catalog.get_course('c')['modules'][1]
    assert updated['source_status'] == 'missing'
    assert updated['sources'] == []


def test_results_cannot_mutate_other_requests():
    course = catalog.get_course('java')
    course['modules'].clear()
    assert catalog.get_course('java')['modules']
    course = catalog.get_course('java')
    module = course['modules'][1]
    source = module['sources'][0]
    lesson = catalog.get_lesson('java', module['id'], source['id'])
    lesson['metadata']['language'] = 'secret'
    assert catalog.get_lesson('java', module['id'], source['id'])['metadata']['language'] == 'java'


def test_audit_snapshot_matches_corpus_and_collections_are_separate():
    data = json.loads(catalog.OUTLINES_PATH.read_text())
    assert data['audit']['reference_rows'] == len(reference_library.records())
    assert data['audit']['curriculum_rows'] == len(curriculum.records())
    extras = {x['subject'] for x in data['audit']['excluded_subjects']}
    assert {'sass','embedded-c','embedded-python','bootstrap','python-flask','spring-core'} <= extras
    assert not extras & LANGUAGES


def test_empty_assignment_is_missing(monkeypatch):
    raw = catalog._outlines()
    raw[0]['modules'][0]['sources'] = []
    monkeypatch.setattr(catalog, '_outlines', lambda: json.loads(json.dumps(raw)))
    module = catalog.get_course(raw[0]['language'])['modules'][0]
    assert module['source_status'] == 'missing'
    assert module['sources'] == []


def test_catalog_projection_removes_hidden_sections(monkeypatch, tmp_path):
    from app.services import content_catalog
    path = tmp_path / 'c-fundamentals.md'
    path.write_text('---\ntrack: language\nlanguage: c\nsecret: PRIVATE\n---\n'
                    '# C basics\nVisible explanation\n## Solutions\nSECRET ANSWER\n')
    monkeypatch.setattr(content_catalog, 'find_path', lambda _: path)
    lesson = catalog.get_lesson('c', 'c-00', 'c-fundamentals')
    assert lesson and 'Visible explanation' in lesson['document']
    assert 'PRIVATE' not in lesson['document']
    assert 'SECRET ANSWER' not in lesson['document']
    path.write_text('---\ntrack: language\nlanguage: python\n---\nWrong course\n')
    assert catalog.get_lesson('c', 'c-00', 'c-fundamentals') is None


def test_partial_source_status(monkeypatch):
    original = reference_library.eligible
    course = catalog.get_course('java')
    module = next(m for m in course['modules'] if len(m['sources']) == 2)
    sid = module['sources'][0]['id']
    monkeypatch.setattr(reference_library, 'eligible', lambda r: r['id'] != sid and original(r))
    updated = next(m for m in catalog.get_course('java')['modules'] if m['id'] == module['id'])
    assert updated['source_status'] == 'partial'
    assert len(updated['sources']) == 1
