"""Contract checks for the advisory cross-section pilot."""

from copy import deepcopy

import pytest

from app.services.concept_links import pilot, validate


def test_pilot_resolves_without_claiming_review():
    data = pilot()
    assert {node["section"] for node in data["nodes"]} == {"language", "dsa", "design-patterns"}
    assert all(link["review"] == "pending" for link in data["links"])
    assert next(node for node in data["nodes"] if node["id"] == "language:javascript:function-values")["content_id"] is None
    assert not any(link["from"] == "dsa:binary-search" and link["to"] == "design-patterns:strategy:javascript" for link in data["links"])


@pytest.mark.parametrize("change", [
    lambda d: d.update(version=2),
    lambda d: d.update(nodes=[]),
    lambda d: d["nodes"].append(None),
    lambda d: d["nodes"][0].update(id=d["nodes"][1]["id"]),
    lambda d: d["nodes"][0].update(content_id="absent-content"),
    lambda d: d["nodes"][0].update(content_id="strategy-pattern"),
    lambda d: d["nodes"][0].update(section=[]),
    lambda d: d["nodes"][2].update(review="reviewed"),
    lambda d: d["links"][0].update(to="absent-node"),
    lambda d: d["links"][0].update(type=[]),
    lambda d: d["links"].append(None),
    lambda d: d["links"][0].update(type="grants-mastery"),
    lambda d: d["links"].append(dict(d["links"][0])),
    lambda d: d["links"].append({"from": "language:javascript:functions", "to": "language:javascript:function-values", "type": "requires", "review": "pending"}),
])
def test_invalid_pilot_fails_closed(change):
    data = deepcopy(pilot())
    change(data)
    with pytest.raises(ValueError):
        validate(data)
