# The authenticated, language-scoped problem catalog.
import pytest

@pytest.fixture
async def problem_headers(client, subscribe_user):
    body=(await client.post("/auth/register",json={"email":"catalog@scope.example","password":"password123"})).json()
    await subscribe_user(body["user"]["id"], "javascript")
    return {"Authorization":"Bearer "+body["access_token"]}

async def test_list_problems_returns_catalog(client, problem_headers):
    r = await client.get("/problems/", headers=problem_headers)
    assert r.status_code == 200
    problems = r.json()
    assert len(problems) >= 20
    ids = {p["id"] for p in problems}
    assert "two-sum" in ids
    two_sum = next(p for p in problems if p["id"] == "two-sum")
    assert two_sum["difficulty"] == "Easy"


async def test_get_single_problem_markdown(client, problem_headers):
    r = await client.get("/problems/two-sum", headers=problem_headers)
    assert r.status_code == 200
    assert "Find a Pair That Sums to a Target" in r.json()["markdown"]


async def test_unknown_problem_404(client, problem_headers):
    r = await client.get("/problems/does-not-exist", headers=problem_headers)
    assert r.status_code == 404
