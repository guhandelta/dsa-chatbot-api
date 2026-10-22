"""Offline release audit of every quiz, path assignment and learner content view.

Does not execute learner code, read credentials, call models, or use the network.
Syntax fingerprints detect obvious language swaps, not arbitrary semantic errors.
"""
from collections import Counter
import json
from pathlib import Path
import re
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from app.services import content_catalog as catalog, course_catalog, learning_path, quiz, reference_library
from app.services.content_access import CODE_LANGUAGES, LANGUAGE_ALIASES, learner_document

# Distinctive syntax only: `let`, `def`, `std::`, etc. alone are ambiguous.
MARKERS = {
    'python': r'(?m)^\s*(?:async\s+)?def\s+\w+\s*\([^\n]*\)\s*(?:->[^\n]+)?:',
    'javascript': r'\bconsole\.log\s*\(|\bfunction\s+\w+\s*\(',
    'java': r'System\.out\.print', 'rust': r'\bfn\s+\w+\s*\(|println!',
    'go': r'\bfunc\s+\w+\s*\(|fmt\.Print', 'ruby': r'(?m)^\s*puts\s',
    'csharp': r'Console\.Write', 'cpp': r'#include\s*<iostream>|\bstd::cout\b',
    'c': r'#include\s*<stdio.h>|\bprintf\s*\(',
}


def audit():
    errors, counts = [], Counter()
    languages = list(learning_path.LANGUAGE_LABELS)
    content = {c.id: c for c in catalog.list_content()}
    references = {r['id']: r for r in reference_library.records()}

    def error(kind, language, identifier, detail):
        errors.append(dict(kind=kind, language=language, id=identifier, detail=detail))

    def fences(text, language, identifier):
        for tag in re.findall(r'^```([^\s`]+)', text, re.M):
            tag = LANGUAGE_ALIASES.get(tag.lower(), tag.lower())
            if tag in CODE_LANGUAGES and tag != language:
                error('foreign_code_fence', language, identifier, tag)

    def syntax(code, language, identifier):
        for detected, pattern in MARKERS.items():
            if detected == language or (language, detected) in (('typescript', 'javascript'), ('cpp', 'c')):
                continue
            if re.search(pattern, code):
                error('foreign_syntax', language, identifier, detected)

    for item in content.values():
        if item.starter_code and item.language:
            counts['starter_code'] += 1
            syntax(item.starter_code, item.language, item.id)
        # Inspect every authored fenced example/solution, before display filtering.
        for tag, code in re.findall(r'^```([^\s`]+)[^\n]*\n(.*?)^```[ \t]*$', catalog.read_content(item.id), re.M | re.S):
            tag = LANGUAGE_ALIASES.get(tag.lower(), tag.lower())
            if tag in MARKERS or tag == 'typescript':
                counts['authored_code_blocks'] += 1
                syntax(code, tag, item.id)

    for language in languages:
        path = quiz.BANK_DIR / f'{language}.json'
        raw = json.loads(path.read_text())
        if raw.get('language') != language:
            error('bank_language', language, str(path), raw.get('language'))
        ids = [i['id'] for i in raw['items']]
        if len(ids) != len(set(ids)):
            error('duplicate_quiz_ids', language, str(path), 'duplicate IDs')
        bank = quiz.items(language)
        counts[f'quiz:{language}'] = len(bank)
        for item in bank.values():
            counts['quiz_items'] += 1
            if item['language'] != language or (item.get('node_id') and not item['node_id'].startswith(language + ':')):
                error('quiz_scope', language, item['id'], item.get('node_id'))
            for field in ('code', 'starter', 'solution', 'prompt', 'answer', 'explanation'):
                value = str(item.get(field, ''))
                fences(value, language, item['id'])
                if field not in ('code', 'starter', 'solution'):
                    continue
                for detected, pattern in MARKERS.items():
                    if detected == language or (language, detected) in (('typescript', 'javascript'), ('cpp', 'c')):
                        continue
                    if re.search(pattern, value):
                        error('foreign_syntax', language, item['id'], f'{field}: {detected}')
        for node in learning_path.nodes(language):
            counts['path_nodes'] += 1
            if not node['id'].startswith(language + ':'):
                error('node_scope', language, node['id'], 'wrong namespace')
            if node['kind'] == 'stage':
                for cid in node['lesson_ids'] + ([node['exercise_id']] if node.get('exercise_id') else []):
                    if cid not in content or content[cid].language != language:
                        error('stage_source', language, node['id'], cid)
            for source in node.get('lesson_sources', []):
                counts['module_sources'] += 1
                row = references.get(source['id'])
                if row is None or row['metadata'].get('language') != language:
                    error('module_source', language, node['id'], source['id'])
                elif row:
                    fences(row['document'], language, source['id'])
            for item in quiz.pool(language, node['id']):
                counts['quiz_pool_assignments'] += 1
                if item['language'] != language:
                    error('quiz_pool', language, node['id'], item['id'])
        for item in content.values():
            if item.language not in (None, language):
                continue
            counts['learner_content_views'] += 1
            text = learner_document(item.id, language)
            fences(text, language, item.id)
            if item.language:
                # Audit original authored content as well, before display filtering.
                fences(learner_document(item.id), language, item.id)
        course = course_catalog.get_course(language)
        for module in (course or {}).get('modules', []):
            for source in module['sources']:
                counts['course_sources'] += 1
                lesson = course_catalog.get_lesson(language, module['id'], source['id'])
                if lesson is None or lesson['metadata'].get('language') != language:
                    error('course_source', language, source['id'], 'source unavailable or wrong language')
                else:
                    fences(lesson['document'], language, source['id'])
    # HTML/CSS references also have subscription scope, though no executable path.
    for language in ('html', 'css'):
        for c in content.values():
            if c.language == language:
                counts['learner_content_views'] += 1
                fences(learner_document(c.id, language), language, c.id)
    return {'status': 'pass' if not errors else 'fail', 'languages': languages + ['html', 'css'],
            'counts': dict(sorted(counts.items())), 'errors': errors,
            'limits': 'Static syntax, metadata, source links and learner views; not a semantic proof or live LLM evaluation.'}


if __name__ == '__main__':
    result = audit()
    output = json.dumps(result, indent=2) + '\n'
    if len(sys.argv) > 1:
        Path(sys.argv[1]).write_text(output)
    print(output)
    sys.exit(bool(result['errors']))
