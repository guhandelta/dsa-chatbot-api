# The public problem catalog endpoint and parsing.
async def test_list_problems_returns_catalog(client):
    r = await client.get("/problems/")
    assert r.status_code == 200
    problems = r.json()
    assert len(problems) >= 20
    ids = {p["id"] for p in problems}
    assert "two-sum" in ids
    two_sum = next(p for p in problems if p["id"] == "two-sum")
    assert two_sum["difficulty"] == "Easy"


async def test_get_single_problem_markdown(client):
    r = await client.get("/problems/two-sum")
    assert r.status_code == 200
    assert "Two Sum" in r.json()["markdown"]


async def test_unknown_problem_404(client):
    r = await client.get("/problems/does-not-exist")
    assert r.status_code == 404
