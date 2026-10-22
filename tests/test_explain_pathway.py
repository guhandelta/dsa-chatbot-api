import json
import shutil
import subprocess

import pytest
from fastapi import HTTPException

from app.services import content_catalog, debug_challenges, explain_pathway, learning_path
from tests.test_study_room import ask, model, register


def test_js_units_have_ordered_prerequisites_and_real_easy_medium_practice():
    data = explain_pathway.authored()
    assert [t['id'] for t in data['tiers']] == [1, 2, 3]
    assert len(data['units']) == 29
    nodes = {n['id'] for n in learning_path.nodes('javascript')}
    problems = {p.id: p for p in content_catalog.filter_content(track='dsa') if p.track == 'dsa'}
    seen = set()
    for unit in data['units']:
        assert unit['id'] not in seen and unit['id'].startswith('explain:javascript:')
        assert set(unit['prerequisite_ids']) <= seen
        seen.add(unit['id'])
        assert all(unit[key] for key in ('objective', 'mental_model', 'applied_task', 'pitfall', 'dsa_bridge'))
        if unit['assessment_node_id']:
            assert unit['assessment_node_id'] in nodes
        for pid in unit['practice_ids']:
            assert pid in problems and problems[pid].difficulty in ('Easy', 'Medium')
    assert {'arrays', 'strings', 'objects', 'maps', 'sets', 'arrays-strings', 'strings-objects', 'objects-map'} <= {u['slug'] for u in data['units']}


@pytest.mark.skipif(shutil.which('node') is None, reason='Node needed to verify authored worked examples')
def test_authored_js_examples_produce_the_documented_outputs():
    # Only committed author examples run here, never submissions or database code.
    for unit in explain_pathway.authored()['units']:
        result = subprocess.run(['node', '--input-type=module', '-e', unit['structure']['code']],
                                capture_output=True, text=True, timeout=5)
        assert result.returncode == 0, (unit['id'], result.stderr)
        assert result.stdout.strip() == unit['structure']['expected_output'], unit['id']


async def test_course_is_subscription_scoped_and_other_languages_are_not_auto_translated(client, db):
    headers, _ = await register(client, db, 'explain-course@example.com', ('javascript', 'python'))
    response = await client.get('/study/explain-pathway', headers=headers, params={'language': 'javascript'})
    assert response.status_code == 200
    course = response.json()
    assert len(course['units']) == 29
    arrays = next(u for u in course['units'] if u['slug'] == 'arrays')
    assert arrays['assessment']['node_id'] == 'javascript:stage-06'
    assert not arrays['assessment']['checks_passed']
    combined = next(u for u in course['units'] if u['slug'] == 'arrays-strings')
    assert combined['assessment'] is None
    assert (await client.get('/study/explain-pathway', headers=headers, params={'language': 'java'})).status_code == 403
    python = (await client.get('/study/explain-pathway', headers=headers, params={'language': 'python'})).json()
    assert python['status'] == 'awaiting-language-review' and python['units'] == []


async def test_coach_uses_selected_unit_and_rejects_foreign_unit_before_model_call(client, db, model):
    headers, _ = await register(client, db, 'explain-focus@example.com', ('javascript', 'python'))
    focus = 'explain:javascript:objects-map'
    response = await client.post('/study/message', headers=headers, json=ask(
        language='javascript', focus_id=focus, message='Why do the record and its Map entry share a reference?'))
    assert response.status_code == 200 and response.json()['focus']['id'] == focus
    system = model.calls[0][0].content
    assert 'Objects with Map' in system and 'const byId = new Map' in system
    assert 'Do not solve the applied task' in system
    forbidden = await client.post('/study/message', headers=headers, json=ask(language='python', focus_id=focus))
    assert forbidden.status_code == 403 and len(model.calls) == 1


async def test_missing_combination_debug_content_does_not_substitute_foundation_cases(client, db):
    headers, _ = await register(client, db, 'explain-debug@example.com', ('javascript',))
    focus = 'explain:javascript:arrays-strings'
    catalog = await client.get('/study/debug/challenges', headers=headers,
                               params={'language': 'javascript', 'focus_id': focus})
    assert catalog.status_code == 200
    assert catalog.json()['subjects'] == []
    assert catalog.json()['scope']['title'] == 'Arrays with Strings'
    drawn = await client.post('/study/debug/challenges/next', headers=headers, json={
        'language': 'javascript', 'subject': 'javascript', 'difficulty': 'easy', 'focus_id': focus})
    assert drawn.status_code == 409
    basic = debug_challenges.selected_scope('javascript', 'explain:javascript:arrays')
    assert basic['id'] == 'javascript:stage-06'


def test_debug_publisher_accepts_exact_unit_tags_and_keeps_them_private(tmp_path, monkeypatch):
    from tools import compile_debug_knowledge as compiler
    unit_id = 'explain:javascript:arrays-strings'
    source = tmp_path / 'debug.json'
    source.write_text(json.dumps({'items': [{
        'language': 'javascript', 'subject': 'javascript', 'difficulty': 'easy',
        'title': 'A text list loses its empty entries',
        'code': 'const words = ["", "a"]; const kept = words.filter(Boolean);',
        'failure': 'The contract says to preserve empty strings.',
        'goal': 'Identify which transformation violates the contract.',
        'private_solution': 'The truthiness filter removes empty strings.',
        'explain_unit_ids': [unit_id],
    }]}))
    monkeypatch.setattr(compiler, 'BANK_PATH', source)
    monkeypatch.setattr(compiler, 'quiz_languages', lambda: ())
    monkeypatch.setattr(compiler.reference_library, 'records', lambda: [])
    monkeypatch.setattr(compiler.curriculum, 'records', lambda: [])
    item = next(iter(compiler.collect().values()))
    assert item['explain_unit_ids'] == [unit_id]
    assert debug_challenges.in_scope(item, debug_challenges.selected_scope('javascript', unit_id))
    public = debug_challenges.public(item)
    assert 'explain_unit_ids' not in public and 'solution' not in public


async def test_dedicated_debug_unit_tags_do_not_widen_to_other_units(client, db, monkeypatch):
    headers, _ = await register(client, db, 'tagged-unit-debug@example.com', ('javascript',))
    item = dict(next(i for i in debug_challenges.bank().values() if i['language'] == 'javascript'))
    item['explain_unit_ids'] = ['explain:javascript:arrays-strings']
    monkeypatch.setattr(debug_challenges, 'bank', lambda: {item['id']: item})
    matched = await client.get('/study/debug/challenges', headers=headers,
        params={'language': 'javascript', 'focus_id': 'explain:javascript:arrays-strings'})
    assert len(matched.json()['subjects']) == 1
    unrelated = await client.get('/study/debug/challenges', headers=headers,
        params={'language': 'javascript', 'focus_id': 'explain:javascript:objects-map'})
    assert unrelated.json()['subjects'] == []


def test_depth_banks_and_reusable_activity_contract():
    from collections import Counter
    from tools.audit_explain_pathway import audit
    data = explain_pathway.authored()
    assert Counter(u['tier'] for u in data['units']) == {1: 8, 2: 14, 3: 7}
    assert sum(len(u['activities']) for u in data['units']) == 180
    assert audit()['errors'] == []
    for unit in data['units']:
        for activity in unit['activities']:
            selected_unit, selected_activity = explain_pathway.resolve_unit_focus('javascript', unit['id'] + '/' + activity['id'])
            assert selected_unit['id'] == unit['id'] and selected_activity == activity
    arrays = explain_pathway.find_unit('javascript', 'explain:javascript:arrays')
    with pytest.raises(HTTPException) as invalid:
        explain_pathway.resolve_unit_focus('javascript', arrays['id'] + '/maps-01')
    assert invalid.value.status_code == 404


async def test_activity_focus_is_exact_and_does_not_accept_another_units_task(client, db, model):
    headers, _ = await register(client, db, 'activity-focus@example.com', ('javascript', 'python'))
    focus = 'explain:javascript:arrays/arrays-11'
    response = await client.post('/study/message', headers=headers, json=ask(
        language='javascript', focus_id=focus, message='How should I reason about repeated maximum values?'))
    assert response.status_code == 200 and response.json()['focus']['id'] == focus
    assert 'second-largest distinct' in model.calls[0][0].content
    changed = await client.post('/study/message', headers=headers, json=ask(
        language='javascript', focus_id='explain:javascript:arrays/arrays-03', thread_id=response.json()['thread_id']))
    assert changed.status_code == 409
    invalid = await client.post('/study/message', headers=headers, json=ask(
        language='javascript', focus_id='explain:javascript:arrays/maps-11'))
    assert invalid.status_code == 404
    forbidden = await client.post('/study/message', headers=headers, json=ask(language='python', focus_id=focus))
    assert forbidden.status_code == 403 and len(model.calls) == 1
    scope = debug_challenges.selected_scope('javascript', focus)
    assert scope['id'] == 'javascript:stage-06'
