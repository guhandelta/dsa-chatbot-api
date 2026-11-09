from copy import deepcopy

import pytest

from app.services import pathway_evidence


def test_javascript_pilot_is_consistent_but_not_publish_ready():
    result = pathway_evidence.audit(pathway_evidence.load_pilot())
    assert result['errors'] == []
    assert result['gaps'] == [
        'explain:javascript:arrays: choose needs an independent assessment',
        'explain:javascript:arrays: transfer needs an independent assessment',
    ]
    assert result['evidence_links_complete'] is False


def test_checker_catches_out_of_order_foreign_and_unsupported_links():
    data = deepcopy(pathway_evidence.load_pilot())
    unit = data['units'][0]
    unit['prerequisite_ids'] = ['explain:javascript:maps']
    unit['external_prerequisite_nodes'] = ['javascript:stage-07']
    unit['application']['requires_capabilities'] = ['unknown-capability']
    unit['evidence']['trace']['id'] = 'py-s07-code'
    unit['evidence']['use']['id'] = 'js-s06-short'
    unit['evidence']['transfer']['independent'] = True
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
    (lambda d: d['units'][0]['evidence']['choose'].update(id='missing'), 'Missing Explain activity'),
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
