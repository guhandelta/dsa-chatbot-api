import json
from copy import deepcopy

import pytest

from tools.validate_connected_tutor_eval import PATH, validate


def test_draft_eval_cases_resolve_to_their_sections():
    data = json.loads(PATH.read_text(encoding='utf-8'))
    assert validate(data) == 5
    assert {case['section'] for case in data['cases']} == {'language', 'dsa', 'design-patterns'}


@pytest.mark.parametrize('edit', [
    lambda d: d.update(version=2),
    lambda d: d.update(cases=[]),
    lambda d: d['cases'].append(None),
    lambda d: d['cases'][1].update(id=d['cases'][0]['id']),
    lambda d: d['cases'][1].update(section='language'),
    lambda d: d['cases'][1].update(focus_id='missing'),
    lambda d: d['cases'][1].update(review_points=[]),
])
def test_invalid_eval_set_is_rejected(edit):
    data = deepcopy(json.loads(PATH.read_text(encoding='utf-8')))
    edit(data)
    with pytest.raises(ValueError):
        validate(data)
