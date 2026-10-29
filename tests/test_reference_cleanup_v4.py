"""Reference cleanup v4: template filler is archived or stripped, and fixes are idempotent."""
import json

from app.services.knowledge_hygiene import clean_reference_rows, normalize_reference, quarantine_reason


def row(rid, document, subject='rust', language='rust', origin='source.jsonl', kind='reference'):
    return {'id': rid, 'document': document, 'provenance': ['source.jsonl'], 'payload': {},
            'metadata': {'language': language, 'subject': subject, 'kind': kind, 'contains_answer': False,
                         'verified': False, 'executable': False, 'origin': origin}}


def test_keyword_stubs_and_framework_lens_templates_are_archived():
    stub = row('a', "Context: rust_edition: 2021\nRc Refcell Node Graphs concept 3\n"
                    "Recognition signals: Rc<RefCell<T>>, graph node.\n['Rc<RefCell<T>>', 'graph node']")
    assert quarantine_reason(stub).startswith('Keyword stub')
    lens = row('b', 'Python / Flask Heap Sort · 1. Reusable learning lenses (continued)\nTesting / debugging',
               'python-flask', 'python')
    assert quarantine_reason(lens).startswith('Generic framework')
    real = row('c', 'Rust Fenwick Tree\nUse 1-based indices; index zero never advances i += i & i.wrapping_neg().')
    assert quarantine_reason(real) is None


def test_filler_is_stripped_and_tags_move_to_metadata():
    r, _ = normalize_reference(row('a', "Context: platform: RP2040_SDK\nWs2812 Bitbang reference guide\n"
                                        "Timing-critical LED signalling by bit-banging.\n['WS2812', 'bit-bang']",
                                   'embedded-c', 'c'))
    assert r['document'].endswith('by bit-banging.') and r['metadata']['tags'] == 'WS2812, bit-bang'
    r, _ = normalize_reference(row('b', 'Ruby Stack · 4. Strategies\n4. Strategies\n'
                                        'These chunks cover the main patterns. Every row is backed by a tested chunk.\n'
                                        '4.1 Algorithm catalogue\npush\nO(1)\n4.2 Live outputs on sample inputs\nCall\n'
                                        'Result\nst.size\n4.3 Strategy chooser\nSignal\nChoose', 'ruby', 'ruby'))
    assert 'tested chunk' not in r['document'] and 'Live outputs' not in r['document']
    assert '4.1 Algorithm catalogue' in r['document'] and '4.3 Strategy chooser' in r['document']
    r, _ = normalize_reference(row('c', 'Rust Gcd Euclid\nPurpose\nRecognition vocabulary\n'
                                        'GCD: learner should recognize and explain this term in a Rust implementation.\n'
                                        'lcm: learner should recognize and explain this term in a Rust implementation.'))
    assert r['document'].endswith('Recognition vocabulary: GCD, lcm.')
    again, _ = normalize_reference(json.loads(json.dumps(r)))
    assert again['document'] == r['document']


def test_known_wrong_statements_are_corrected():
    sentence = ('CPU-bound work blocks the event loop; choose sync endpoints, thread/process offload, streaming, '
                'bounded state, and safe cache lifetimes deliberately.')
    r, _ = normalize_reference(row('a', 'Python / Django Heap\nProduction\n' + sentence, 'python-django', 'python'))
    assert 'event loop' not in r['document'] and 'occupies a worker' in r['document']
    fastapi, _ = normalize_reference(row('b', 'Python / FastAPI Heap\nProduction\n' + sentence, 'python-fastapi', 'python'))
    assert sentence in fastapi['document']


def test_debug_exercise_tier_copies_collapse_and_shifted_fields_are_repaired():
    body = ('## CSS-T-0N: motion sickness\n- Difficulty: D\n- Concept: motion sickness\n'
            '- Diagnostic goal: Check the boundary contract before styling around the symptom.\n### Buggy code\n'
            '```css\nRespect the user media preference.\n```\n### Expected diagnosis\n.panel { transition: transform .4s; }\n'
            '### Corrected code\n```css\n.panel { transition: none; }\n```')
    origin = 'debug-exercises/css3-debug-exercises.md'
    easy = row('e', 'CSS3 Debug Exercises · Animation\n' + body.replace('T-0N', 'E-028').replace('D\n', 'Easy\n', 1), 'css', 'css', origin)
    hard = row('h', 'CSS3 Debug Exercises · Animation\n' + body.replace('T-0N', 'H-068').replace('D\n', 'Hard\n', 1), 'css', 'css', origin)
    active, quarantine, aliases = clean_reference_rows([easy, hard])
    assert [r['id'] for r in active] == ['e'] and aliases == {'h': 'e'}
    doc = active[0]['document']
    assert '```css\n.panel { transition: transform .4s; }\n```' in doc and 'reduced motion' in doc
    assert 'Respect the user media preference.\n```' not in doc
