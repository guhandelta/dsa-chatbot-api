# The three-track structure: filtering, language preference, and the
# algorithm→practice-problem progression.
from app.services.content_catalog import (
    TRACKS,
    filter_content,
    known_algorithms,
    list_content,
)


def test_all_three_tracks_present():
    tracks = {c.track for c in list_content()}
    assert tracks.issubset(set(TRACKS))
    assert "dsa" in tracks


def test_language_track_items_declare_language():
    for c in filter_content(track="language"):
        assert c.language is not None


def test_language_filter_excludes_other_languages():
    py = filter_content(track="language", language="python")
    assert all(c.language == "python" for c in py)
    rust = filter_content(track="language", language="rust")
    assert all(c.language == "rust" for c in rust)


def test_dsa_items_are_language_agnostic():
    # DSA problems have solutions in every language, so they match any filter
    for lang in ("python", "rust", "c"):
        assert len(filter_content(track="dsa", language=lang)) == len(
            filter_content(track="dsa")
        )


def test_algorithm_tag_links_concept_to_problems():
    tagged = filter_content(algorithm="binary-search")
    tracks = {c.track for c in tagged}
    assert "dsa" in tracks          # practice problems exist
    assert len(tagged) >= 2


def test_difficulty_progression_available():
    easy = filter_content(track="dsa", difficulty="Easy")
    medium = filter_content(track="dsa", difficulty="Medium")
    assert easy and medium
    assert all(c.difficulty == "Easy" for c in easy)


def test_every_algorithm_tag_resolves():
    for tag in known_algorithms():
        assert filter_content(algorithm=tag), f"tag {tag} matches nothing"


async def test_language_preference_persists(client):
    r = await client.post(
        "/auth/register", json={"email": "lang@x.com", "password": "password123"}
    )
    token = r.json()["access_token"]
    assert r.json()["user"]["preferred_language"] == "python"
    h = {"Authorization": f"Bearer {token}"}

    upd = await client.patch("/auth/me/language", headers=h, json={"language": "rust"})
    assert upd.status_code == 200
    assert upd.json()["preferred_language"] == "rust"

    me = await client.get("/auth/me", headers=h)
    assert me.json()["preferred_language"] == "rust"


async def test_tracks_endpoint_lists_three_paths(client):
    r = await client.post(
        "/auth/register", json={"email": "tr@x.com", "password": "password123"}
    )
    h = {"Authorization": f"Bearer {r.json()['access_token']}"}
    res = await client.get("/tracks/", headers=h)
    assert res.status_code == 200
    body = res.json()
    # Learner-facing SECTIONS, not internal tracks: `algorithm` is folded into
    # `dsa` because a learner sees problems and the techniques behind them as
    # one subject rather than two separate destinations.
    assert [t["track"] for t in body["tracks"]] == [
        "language", "dsa", "design-patterns",
    ]
    assert body["modes"] == ["learn", "practice"]


async def test_tracks_require_auth(client):
    assert (await client.get("/tracks/")).status_code == 401
