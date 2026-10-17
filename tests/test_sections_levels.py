"""Learner-facing sections, Language Fundamentals levels, and pattern cross-links.

The design these assert:
  * three SECTIONS are shown to learners; the internal `algorithm` track is
    folded into `dsa`, because a learner sees problems and the techniques
    behind them as one subject
  * Language Fundamentals is the only language-scoped section
  * `level` orders Language Fundamentals; `difficulty` orders DSA. They are
    separate axes and must not be conflated
  * a `patterns` tag links a language idiom page to its Design Patterns page,
    so neither section has to duplicate the other
  * no two content files share an id — a shadowed problem loses its test
    cases and silently becomes unverifiable
"""
import pytest

from app.services.content_catalog import (
    LEVELS,
    SECTIONS,
    filter_content,
    known_patterns,
    level_summary,
    list_content,
    track_summary,
)


# ---------------- sections ----------------

def test_three_learner_facing_sections():
    assert [s["track"] for s in track_summary()] == [
        "language", "dsa", "design-patterns",
    ]


def test_algorithm_track_is_not_its_own_section():
    assert "algorithm" not in [s["track"] for s in track_summary()]
    assert "algorithm" in SECTIONS["dsa"]


def test_dsa_section_aggregates_problems_and_techniques():
    items = filter_content(track="dsa")
    tracks = {c.track for c in items}
    assert tracks <= set(SECTIONS["dsa"])
    assert "dsa" in tracks and "algorithm" in tracks


def test_internal_track_name_still_resolves():
    """Callers that know the internal name keep working after the split."""
    assert all(c.track == "algorithm" for c in filter_content(track="algorithm"))


def test_sections_report_availability_honestly():
    for section in track_summary():
        assert section["available"] == (section["count"] > 0)


def test_unknown_section_is_empty_not_an_error():
    assert filter_content(track="nonexistent") == []


# ---------------- duplicate ids ----------------

def test_no_two_items_share_an_id():
    """A shadowed file is unreachable: the catalog keys by stem, so the first
    directory scanned wins and the other file's test cases and reference
    solution disappear with it."""
    ids = [c.id for c in list_content()]
    duplicates = {i for i in ids if ids.count(i) > 1}
    assert not duplicates, f"shadowed content ids: {sorted(duplicates)}"


# ---------------- levels ----------------

def test_level_summary_returns_three_levels_in_order():
    assert [l["level"] for l in level_summary("python")] == list(LEVELS)


@pytest.mark.parametrize("level", LEVELS)
def test_level_filter_returns_only_that_level(level):
    for item in filter_content(track="language", level=level):
        assert item.level == level


def test_level_and_difficulty_are_separate_axes():
    """DSA items are ordered by difficulty and must never carry a level."""
    for item in filter_content(track="dsa"):
        assert item.level is None, f"{item.id} should not be level-scoped"


def test_language_section_is_language_scoped():
    for item in filter_content(track="language", language="python"):
        assert item.language in (None, "python")


def test_dsa_is_not_language_scoped():
    """DSA problems ship solutions in every language, so they match any."""
    baseline = len(filter_content(track="dsa"))
    for lang in ("python", "rust", "c"):
        assert len(filter_content(track="dsa", language=lang)) == baseline


# ---------------- pattern cross-linking ----------------

def test_every_known_pattern_resolves():
    for tag in known_patterns():
        assert filter_content(pattern=tag), f"pattern tag '{tag}' matches nothing"


def test_unknown_pattern_is_empty():
    assert filter_content(pattern="not-a-real-pattern") == []


def test_pattern_filter_is_pure():
    for tag in known_patterns():
        for item in filter_content(pattern=tag):
            assert tag in item.patterns


def test_patterns_and_algorithms_are_independent_tags():
    """A pattern tag must not leak into the algorithm filter, or the two
    sections would start cross-contaminating each other's listings."""
    for tag in known_patterns():
        if tag in {a for c in list_content() for a in c.algorithms}:
            continue
        assert filter_content(algorithm=tag) == []


# ---------------- endpoints ----------------

async def _reg(client, email):
    r = await client.post("/auth/register",
                          json={"email": email, "password": "password123"})
    return r.json()


async def test_tracks_endpoint_returns_sections(client):
    body = await _reg(client, "sec@x.com")
    h = {"Authorization": f"Bearer {body['access_token']}"}
    r = await client.get("/tracks/", headers=h)
    assert r.status_code == 200
    payload = r.json()
    assert [t["track"] for t in payload["tracks"]] == [
        "language", "dsa",
    ]
    assert "browse" in payload["modes"]


async def test_language_levels_endpoint(client):
    body = await _reg(client, "lvl@x.com")
    h = {"Authorization": f"Bearer {body['access_token']}"}
    r = await client.get("/tracks/language/levels", headers=h)
    assert r.status_code == 200
    payload = r.json()
    assert [l["level"] for l in payload["levels"]] == list(LEVELS)
    assert payload["language"] == "javascript"


async def test_language_levels_respects_query_language(client):
    body = await _reg(client, "lvl2@x.com")
    h = {"Authorization": f"Bearer {body['access_token']}"}
    r = await client.get("/tracks/language/levels?language=rust", headers=h)
    assert r.json()["language"] == "rust"


async def test_invalid_level_rejected(client):
    body = await _reg(client, "badlvl@x.com")
    h = {"Authorization": f"Bearer {body['access_token']}"}
    r = await client.get("/tracks/language/items?level=wizard", headers=h)
    assert r.status_code == 400
    assert "wizard" in r.json()["detail"]


async def test_unknown_section_returns_404(client):
    body = await _reg(client, "badsec@x.com")
    h = {"Authorization": f"Bearer {body['access_token']}"}
    r = await client.get("/tracks/nonsense/items", headers=h)
    assert r.status_code == 404


async def test_pattern_tags_endpoint(client):
    body = await _reg(client, "pat@x.com")
    h = {"Authorization": f"Bearer {body['access_token']}"}
    r = await client.get("/tracks/patterns/tags", headers=h)
    assert r.status_code == 200
    assert "patterns" in r.json()


async def test_pattern_related_endpoint(client):
    body = await _reg(client, "patrel@x.com")
    h = {"Authorization": f"Bearer {body['access_token']}"}
    r = await client.get("/tracks/patterns/strategy/related", headers=h)
    assert r.status_code == 200
    assert isinstance(r.json(), list)


async def test_sections_require_auth(client):
    assert (await client.get("/tracks/")).status_code == 401
    assert (await client.get("/tracks/language/levels")).status_code == 401
    assert (await client.get("/tracks/patterns/tags")).status_code == 401
