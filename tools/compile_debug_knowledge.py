"""Rebuild the dedicated debug bank from local authored sources; run its audit before publishing."""
import json
from pathlib import Path
import re
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from app.services import curriculum, quiz, reference_library
from app.services.debug_challenges import DIFFICULTIES, LEVEL_DIFFICULTY, _fingerprint, _mapped_nodes, quiz_languages
BANK_PATH = Path(__file__).resolve().parents[1] / 'data/curriculum/debug-challenges.json'


def collect():
    quiz_versions = tuple((lang, quiz._bank_version(lang)) for lang in quiz_languages())
    out = {}
    def add(language, subject, difficulty, title, code, failure, goal, source, private_solution='', code_language=None, node_ids=(), source_ids=(), task_kind='repair', explain_unit_ids=()):
        if not code.strip() or len(code) > 16000 or difficulty not in DIFFICULTIES:
            return
        from app.services.explain_pathway import find_unit
        for unit_id in explain_unit_ids:
            find_unit(language, unit_id)
        key = _fingerprint(language, subject, code)
        if key in out:
            out[key]['node_ids'] = sorted(set(out[key]['node_ids']) | set(node_ids))
            out[key]['source_ids'] = sorted(set(out[key]['source_ids']) | set(source_ids))
            if explain_unit_ids:
                out[key]['explain_unit_ids'] = sorted(set(out[key].get('explain_unit_ids', [])) | set(explain_unit_ids))
            return
        out[key] = dict(id=key, language=language, subject=subject, difficulty=difficulty,
                        title=title, code=code.strip(), failure=failure, goal=goal,
                        source=source, code_language=code_language or language,
                        node_ids=sorted(set(node_ids)), source_ids=sorted(set(source_ids)), task_kind=task_kind,
                        # Private: never in a response or a tutor prompt.
                        solution=private_solution)
        if explain_unit_ids:
            out[key]['explain_unit_ids'] = sorted(set(explain_unit_ids))

    authored = json.loads(BANK_PATH.read_text())
    for item in authored['items']:
        add(**item, source='authored')
    for language, version in quiz_versions:
        for item in quiz._authored(language, version):
            if item['type'] not in ('fix_bug', 'mcq_code', 'short_answer') or not item.get('code'):
                continue
            stage = re.search(r'stage-(\d+)', item['node'])
            number = int(stage[1]) if stage else 99
            difficulty = 'easy' if number <= 3 else 'medium' if number <= 6 else 'hard' if number <= 10 else 'expert'
            repair = item['type'] == 'fix_bug'
            brief = item['prompt']
            if item.get('choices'):
                brief += '\n' + '\n'.join(f"{n+1}. {choice}" for n, choice in enumerate(item['choices']))
            answer = item.get('solution') or (str(item.get('answer')) + '\n' + item.get('explanation', ''))
            add(language, language, difficulty, f"{'Investigate' if repair else 'Trace'} {item['concept'].replace('-', ' ')}",
                item['code'], brief,
                ('Repair the bug and describe a regression test, including a boundary case.' if repair else
                 'Trace the program and justify its output, type error, or state changes. Do not assume every snippet contains a bug; support your diagnosis with an execution trace.'),
                'authored-quiz', answer, node_ids=[f"{language}:{item['node']}"],
                task_kind='repair' if repair else 'trace')
    rows = (*reference_library.records(), *curriculum.records())
    for row in rows:
        meta = row['metadata']
        if meta.get('kind') != 'concept' or meta.get('contains_answer') is not False:
            continue
        if meta.get('source') == 'reference-library' and not reference_library.eligible(row):
            continue
        payload = quiz._inner(row.get('payload') or {})
        bad, good = payload.get('example_bad'), payload.get('example_good')
        if not isinstance(bad, str) or not isinstance(good, str) or bad.strip() == good.strip():
            continue
        language = meta.get('language')
        subject = meta.get('subject') or language
        level = meta.get('level') or payload.get('level', 'L2')
        difficulty = LEVEL_DIFFICULTY.get(level)
        if language not in quiz_languages() or not difficulty:
            continue
        topic = str(meta.get('data_structure') or payload.get('data_structure') or 'program behavior')
        claim = str(payload.get('misconception') or 'This implementation handles all valid inputs.')
        add(language, subject, difficulty, f'Investigate {topic}', bad,
            f'A teammate claims: {claim}',
            'Find a counterexample or failing execution trace, diagnose the defect, and propose a regression test. The snippet may need its usual imports or enclosing program.',
            'reference-example', good,
            node_ids=_mapped_nodes(language, topic, meta, payload),
            source_ids=[row['id'], payload.get('id', '')])
    return out


if __name__ == '__main__':
    target = Path(__file__).resolve().parents[1] / 'data/debug/knowledge-base.json'
    target.write_text(json.dumps({'version': 1, 'assessment': 'self-review', 'items': list(collect().values())}, indent=2, ensure_ascii=False) + '\n')
    print('Published local debugging knowledge base. Run tools/audit_debug_challenges.py next.')
