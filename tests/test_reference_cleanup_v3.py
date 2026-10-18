"""Reference cleanup v3: noise removal, heading chunks and retagging stay deterministic."""
import json

from app.services.knowledge_hygiene import (clean_reference_rows, normalize_reference, reference_id,
                                            section_chunks, strip_contents)


def row(rid, document, subject='c', payload=None, kind='reference'):
    return {'id': rid, 'document': document, 'provenance': ['source.jsonl'], 'payload': payload or {},
            'metadata': {'language': 'c', 'subject': subject, 'kind': kind, 'contains_answer': False,
                         'verified': False, 'executable': False, 'origin': 'source.jsonl'}}


def test_legacy_header_and_chunk_id_move_to_metadata():
    r, _ = normalize_reference(row('a', 'Imported reference; not locally executed. Subject: c; platform: AVR\n'
                                        'C · Queue\nUse it for: BFS\nChunk: c-queue-bfs'))
    assert r['document'] == 'Context: platform: AVR\nC · Queue\nUse it for: BFS'
    assert r['metadata']['chunk_id'] == 'c-queue-bfs'
    again, _ = normalize_reference(json.loads(json.dumps(r)))
    assert again['document'] == r['document']


def test_strategy_rows_from_anti_pattern_tables_are_relabelled():
    meta = {'doc': 'ruby_adjlist', 'section': 'algorithms-and-strategies'}
    r, _ = normalize_reference(row('a', 'Signal in the problem: Edge\nStrategy: Store both directions\nWhy: Store one direction',
                                   'ruby', {'metadata': meta}))
    assert 'Watch out for: Store one direction' in r['document'] and 'Why:' not in r['document']
    python = {'doc': 'py_algdp', 'section': 'algorithms-and-strategies'}
    kept, _ = normalize_reference(row('b', 'Strategy: Bottom-up\nWhy: No recursion limit', 'python', {'metadata': python}))
    assert 'Why: No recursion limit' in kept['document']


def test_embedded_rows_under_plain_c_are_retagged_with_importer_ids():
    payload = {'id': 'ec-adc-1', 'metadata': {'track': 'embedded_c', 'level': 'Beginner', 'level_code': 'L1',
                                              'data_structure': 'adc and dac sampling'}}
    r, previous = normalize_reference(row(reference_id('c', 'ec-adc-1'), 'ADC text', 'c', payload))
    assert r['metadata']['subject'] == 'embedded-c' and r['id'] == reference_id('embedded-c', 'ec-adc-1')
    assert previous == reference_id('c', 'ec-adc-1')
    assert r['metadata']['level'] == 'L1' and r['metadata']['level_label'] == 'Beginner'
    assert r['metadata']['data_structure_id'] == 'adc-and-dac-sampling'


def test_contents_entries_do_not_stop_or_split_the_document():
    text = ('Ruby Stack: Training Data for the DSA Mentor RAG Chatbot\nContents\n\x7f 1. How to use this document\n'
            '\x7f 2. Overview\n\x7f 3. Core practice exercises with answer key\nPage 2\n1. How to use this document\n'
            'This document is source material for the RAG collection.\n2. Overview\n'
            + 'A stack is last in, first out, and push and pop are constant time operations.\n' * 2
            + '2.5 Practice with answers\nex1 answer: [1, 2]\n3. Gotchas\n'
            + 'Popping an empty array returns nil instead of raising an error in Ruby code.\n' * 2)
    chunks = section_chunks(strip_contents(text))
    joined = '\n'.join(chunks)
    assert chunks[0].startswith('Ruby Stack · 2. Overview')
    assert 'last in, first out' in joined and 'Popping an empty array' in joined
    assert 'answer' not in joined.lower() and 'RAG' not in joined and 'Page 2' not in joined


def test_template_copies_collapse_to_one_row_per_subject():
    a = row('a', 'Python / Django LRU Cache · 6. Gotchas\nAliasing: Define LRU Cache state explicitly.', 'python-django',
            {'source_sha256': '1', 'chunking': 'heading-sections-v1'})
    b = row('b', 'Python / Django Trie · 6. Gotchas\nAliasing: Define Trie state explicitly.', 'python-django',
            {'source_sha256': '2', 'chunking': 'heading-sections-v1'})
    active, quarantine, aliases = clean_reference_rows([a, b])
    assert [r['id'] for r in active] == ['a'] and aliases == {'b': 'a'}
    assert active[0]['document'].startswith('Python / Django · 6. Gotchas')
    assert quarantine[0]['record']['id'] == 'b'
