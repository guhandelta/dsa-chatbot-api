from copy import deepcopy

import pytest

from app.services import pathway_evidence, quiz


def test_javascript_pilot_links_every_evidence_role_without_promoting_it():
    data = pathway_evidence.load_pilot()
    result = pathway_evidence.audit(data)
    assert result == {'errors': [], 'gaps': [], 'evidence_links_complete': True}
    # Complete links are an authoring status, not a publication or mastery flag.
    assert data['status'] == 'authoring-draft'
    unit = data['units'][0]
    assert all(ref['source'] == 'quiz' and ref['independent'] for ref in unit['evidence'].values())
    assert unit['application']['source'] == 'explain' and 'independent' not in unit['application']


async def test_javascript_pilot_choice_and_transfer_items_are_gradable():
    items = quiz.items('javascript')
    choose, transfer = items['js-s06-choose-copy'], items['js-s06-transfer-peaks']
    assert (choose['role'], transfer['role']) == ('explain', 'implement')
    assert quiz.keyword_grade(choose, choose['answer'])[0] == 1.0
    assert quiz.keyword_grade(choose, 'Change it in place, it is faster and uses less memory.')[0] < quiz.PASS_SCORE
    passed = await quiz.grade(transfer, transfer['solution'])
    assert passed['correct'] and passed['tests']['passed'] == passed['tests']['total'] == 10
    ends_counted = 'function countPeaks(values) {\n  return values.filter((v, i) => (i === 0 || v >= values[i - 1]) && (i === values.length - 1 || v >= values[i + 1])).length;\n}'
    assert not (await quiz.grade(transfer, ends_counted))['correct']
    assert not (await quiz.grade(transfer, transfer['starter']))['correct']


def test_checker_catches_out_of_order_foreign_and_unsupported_links():
    data = deepcopy(pathway_evidence.load_pilot())
    unit = data['units'][0]
    unit['prerequisite_ids'] = ['explain:javascript:maps']
    unit['external_prerequisite_nodes'] = ['javascript:stage-07']
    unit['application']['requires_capabilities'] = ['unknown-capability']
    unit['evidence']['trace']['id'] = 'py-s07-code'
    unit['evidence']['use']['id'] = 'js-s06-short'
    unit['evidence']['transfer'] = {'source': 'explain', 'id': 'arrays-11', 'family': 'distinct-reading', 'independent': True}
    result = pathway_evidence.audit(data)
    assert any('Out-of-order prerequisite' in error for error in result['errors'])
    assert any('not earlier' in error for error in result['errors'])
    assert any('untaught capability' in error for error in result['errors'])
    assert any('Missing language quiz item' in error for error in result['errors'])
    assert any('Quiz role does not match' in error for error in result['errors'])
    assert any('Ungraded activity claims independence' in error for error in result['errors'])
    assert result['evidence_links_complete'] is False


def test_empty_and_unknown_paths_do_not_pass():
    assert pathway_evidence.audit({'language': 'unknown'})['evidence_links_complete'] is False
    result = pathway_evidence.audit({'language': 'python', 'units': [], 'status': 'published'})
    assert result['errors'] == ['No units']
    assert result['evidence_links_complete'] is False


@pytest.mark.parametrize(('change', 'expected'), [
    (lambda d: d['units'].append(deepcopy(d['units'][0])), 'Invalid or duplicate unit'),
    (lambda d: d['units'][0].update(id='explain:javascript:nonexistent'), 'Missing language-owned Explain unit'),
    (lambda d: d['units'][0].update(external_prerequisite_nodes=['missing']), 'Missing path prerequisite'),
    (lambda d: d['units'][0].update(capabilities=[]), 'Missing capability'),
    (lambda d: d['units'][0].update(capabilities=['ordered-traversal'] * 2), 'Duplicate capability'),
    (lambda d: d['units'][0]['recovery'][0].update(id='missing'), 'Missing Explain activity'),
    (lambda d: d['units'][0]['evidence']['choose'].update(source='explain', id='arrays-09', independent=False),
     'choose needs an independent assessment'),
    (lambda d: d['units'][0]['evidence']['use'].update(id='js-s07-code'), 'Quiz item belongs to another node'),
    (lambda d: d['units'][0]['evidence']['trace'].update(source='unknown'), 'Unknown evidence source'),
    (lambda d: d['units'][0]['evidence']['use'].update(family='array-aliasing'), 'reused evidence family'),
    (lambda d: d['units'][0]['evidence']['use'].update(id='js-s06-short'), 'Reused assessment item'),
    (lambda d: d['units'][0].update(application=None), 'missing application'),
    (lambda d: d['units'][0]['application'].update(requires_capabilities=[]), 'Application lacks capability requirements'),
    (lambda d: d['units'][0].update(recovery=[]), 'missing recovery activities'),
    (lambda d: d['units'][0]['recovery'][0].update(when=''), 'Recovery lacks trigger'),
    (lambda d: d['units'][0]['evidence'].pop('trace'), 'missing trace evidence'),
])
def test_authoring_checker_reports_broken_contracts(change, expected):
    data = deepcopy(pathway_evidence.load_pilot())
    change(data)
    result = pathway_evidence.audit(data)
    assert any(expected in message for message in result['errors'] + result['gaps']), result
