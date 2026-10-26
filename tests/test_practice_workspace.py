"""Practice workspace: drafts, checkpoints, reset, free test runs, bundling,
the configurable reveal policy and session summaries. Test runs execute for
real in the configured local executor."""
from datetime import datetime, timedelta, timezone

import pytest
from fastapi import HTTPException
from sqlalchemy import func, select

from app.core.config import settings
from app.db.models import (LearningEvent, PracticeSession, Subscription, WorkspaceCheckpoint,
                           WorkspaceDraft, WorkspaceRun)
from app.services import workspace
from app.services.code_runner import available_languages
from app.services.content_access import can_reveal

PID = "python-path-01-values"
RIGHT = "def total_cost(price, quantity):\n    return price * quantity\n"
WRONG = "def total_cost(price, quantity):\n    return price + quantity\n"


async def _learner(client, db, email="workspace@example.com", language="python"):
    registered = (await client.post("/auth/register", json={"email": email, "password": "password123"})).json()
    uid = registered["user"]["id"]
    db.add(Subscription(user_id=uid, language=language, expires_at=datetime.now(timezone.utc) + timedelta(days=42)))
    await db.commit()
    return uid, {"Authorization": "Bearer " + registered["access_token"]}


def _body(files, entry="solution.py", **extra):
    return {"language": "python", "entry": entry,
            "files": [{"name": n, "content": c} for n, c in files], **extra}


# ------------------------------------------------------------- bundling

def test_python_helpers_bundle_keeps_line_numbers_and_maps_back():
    files = [{"name": "helpers.py", "content": "def double(x):\n    return x * 2"},
             {"name": "solution.py", "content": "from helpers import double\n\ndef f(x):\n    return double(x)"},
             {"name": "NOTES.md", "content": "never executed"}]
    code, source_map = workspace.bundle("python", files, "solution.py")
    assert "from helpers" not in code and "never executed" not in code
    assert source_map == [{"file": "helpers.py", "start": 1, "end": 2},
                          {"file": "solution.py", "start": 3, "end": 6}]
    assert workspace.locate(source_map, 6) == {"file": "solution.py", "line": 4}
    namespace = {}
    exec(code, namespace)
    assert namespace["f"](4) == 8


def test_bare_python_import_of_a_helper_is_rejected_with_guidance():
    files = [{"name": "helpers.py", "content": "def d(x): return x"},
             {"name": "solution.py", "content": "import helpers\ndef f(x): return helpers.d(x)"}]
    with pytest.raises(HTTPException) as err:
        workspace.bundle("python", files, "solution.py")
    assert "from helpers import" in err.value.detail


def test_javascript_helpers_drop_exports_and_requires():
    files = [{"name": "helpers.js", "content": "export function twice(x) { return 2 * x }\nmodule.exports = { twice }"},
             {"name": "solution.js", "content": "const { twice } = require('./helpers')\nfunction f(x) { return twice(x) }"}]
    code, _ = workspace.bundle("javascript", files, "solution.js")
    assert "export" not in code and "require" not in code and "module.exports" not in code
    assert code.count("\n") == 3  # blanked, not removed


def test_multiline_local_imports_are_blanked_in_place():
    py = [{"name": "helpers.py", "content": "def a(): return 1\ndef b(): return 2"},
          {"name": "solution.py", "content": "from helpers import (\n    a,\n    b,\n)\ndef f(): return a() + b()"}]
    code, _ = workspace.bundle("python", py, "solution.py")
    namespace = {}
    exec(code, namespace)
    assert namespace["f"]() == 3 and code.count("\n") == 6
    js = [{"name": "helpers.js", "content": "export const a = 1"},
          {"name": "solution.js", "content": "import {\n  a,\n} from './helpers'\nfunction f() { return a }"}]
    code, _ = workspace.bundle("javascript", js, "solution.js")
    assert "import" not in code and "from" not in code and code.count("\n") == 4


def test_validation_rejects_unsafe_or_unsupported_workspaces():
    ok = [{"name": "solution.py", "content": "x"}]
    assert workspace.validate("python", ok, "solution.py") == ok
    for files, entry in [
        ([{"name": "../evil.py", "content": ""}], "../evil.py"),
        ([{"name": "solution.rb", "content": ""}], "solution.rb"),
        ([{"name": f"f{i}.py", "content": ""} for i in range(9)], "f0.py"),
        ([{"name": "solution.py", "content": "x" * 20_001}], "solution.py"),
        ([{"name": "NOTES.md", "content": ""}], "NOTES.md"),
        ([{"name": "solution.py", "content": ""}], "missing.py"),
    ]:
        with pytest.raises(HTTPException):
            workspace.validate("python", files, entry)
    with pytest.raises(HTTPException) as err:
        workspace.validate("java", [{"name": "Solution.java", "content": ""},
                                    {"name": "Helper.java", "content": ""}], "Solution.java")
    assert "single source file" in err.value.detail
    assert workspace.validate("java", [{"name": "Solution.java", "content": ""},
                                       {"name": "NOTES.md", "content": ""}], "Solution.java")


def test_templates_only_offer_helpers_where_bundling_is_sound():
    assert {t["id"] for t in workspace.templates("python")} == {"single", "notes", "helpers"}
    assert {t["id"] for t in workspace.templates("java")} == {"single", "notes"}
    files = workspace.starter_files("python", "helpers", "def f(): pass")
    assert [f["name"] for f in files] == ["helpers.py", "solution.py"]


# ------------------------------------------------------------- HTTP flow

async def test_drafts_autosave_with_revisions_and_conflicts(client, db):
    uid, headers = await _learner(client, db)
    opened = (await client.get(f"/workspace/{PID}", params={"language": "python"}, headers=headers)).json()
    assert opened["draft"]["revision"] is None
    assert opened["draft"]["files"][0]["content"].startswith("def total_cost")
    assert opened["reveal"]["policy"] == settings.solution_reveal_policy
    assert opened["reveal"]["available"] is False

    first = await client.put(f"/workspace/{PID}", headers=headers, json=_body([("solution.py", WRONG)]))
    assert first.status_code == 200 and first.json()["revision"] == 1
    second = await client.put(f"/workspace/{PID}", headers=headers,
                              json=_body([("solution.py", RIGHT)], revision=1))
    assert second.json()["revision"] == 2
    stale = await client.put(f"/workspace/{PID}", headers=headers,
                             json=_body([("solution.py", WRONG)], revision=1))
    assert stale.status_code == 409 and stale.json()["detail"]["revision"] == 2
    forced = await client.put(f"/workspace/{PID}", headers=headers,
                              json=_body([("solution.py", WRONG)], revision=1, force=True))
    assert forced.json()["revision"] == 3

    reopened = (await client.get(f"/workspace/{PID}", params={"language": "python"}, headers=headers)).json()
    assert reopened["draft"]["files"] == [{"name": "solution.py", "content": WRONG}]


async def test_checkpoints_restore_and_reset_are_undoable(client, db):
    uid, headers = await _learner(client, db)
    await client.put(f"/workspace/{PID}", headers=headers, json=_body([("solution.py", RIGHT)]))
    made = await client.post(f"/workspace/{PID}/checkpoints", headers=headers,
                             json=_body([("solution.py", RIGHT)], label="Working version"))
    assert made.status_code == 200 and made.json()["label"] == "Working version"
    cid = made.json()["id"]

    await client.put(f"/workspace/{PID}", headers=headers, json=_body([("solution.py", WRONG)], revision=1))
    reset = await client.post(f"/workspace/{PID}/reset", headers=headers,
                              json={"language": "python", "template": "notes"})
    assert [f["name"] for f in reset.json()["draft"]["files"]] == ["solution.py", "NOTES.md"]
    restored = await client.post(f"/workspace/{PID}/checkpoints/{cid}/restore", headers=headers)
    assert restored.json()["draft"]["files"] == [{"name": "solution.py", "content": RIGHT}]

    listed = (await client.get(f"/workspace/{PID}", params={"language": "python"}, headers=headers)).json()
    kinds = [c["kind"] for c in listed["checkpoints"]]
    assert kinds == ["before_restore", "before_reset", "manual"]
    before_reset = next(c for c in listed["checkpoints"] if c["kind"] == "before_reset")
    detail = (await client.get(f"/workspace/{PID}/checkpoints/{before_reset['id']}", headers=headers)).json()
    assert detail["files"] == [{"name": "solution.py", "content": WRONG}]

    _, other = await _learner(client, db, email="someone-else@example.com")
    assert (await client.get(f"/workspace/{PID}/checkpoints/{cid}", headers=other)).status_code == 404
    assert (await client.post(f"/workspace/{PID}/checkpoints/{cid}/restore", headers=other)).status_code == 404
    assert (await client.delete(f"/workspace/{PID}/checkpoints/{cid}", headers=headers)).status_code == 200


async def test_checkpoint_cap_prunes_automatic_snapshots_first(client, db, monkeypatch):
    monkeypatch.setattr(settings, "workspace_max_checkpoints", 3)
    uid, headers = await _learner(client, db)
    for label in ("a", "b"):
        await client.post(f"/workspace/{PID}/checkpoints", headers=headers,
                          json=_body([("solution.py", RIGHT)], label=label))
    await client.put(f"/workspace/{PID}", headers=headers, json=_body([("solution.py", RIGHT)]))
    for _ in range(3):
        await client.post(f"/workspace/{PID}/reset", headers=headers, json={"language": "python"})
    rows = (await db.scalars(select(WorkspaceCheckpoint).where(WorkspaceCheckpoint.user_id == uid))).all()
    assert len(rows) == 3
    assert sorted(c.label for c in rows if c.kind == "manual") == ["a", "b"]


async def test_free_test_runs_report_cases_and_diagnostics_without_leaking_tests(client, db):
    uid, headers = await _learner(client, db)
    failed = await client.post(f"/workspace/{PID}/run", headers=headers, json=_body([("solution.py", WRONG)]))
    assert failed.status_code == 200, failed.text
    view = failed.json()
    assert view["status"] == "failed" and view["total"] == 6 and view["passed"] < 6
    assert len(view["cases"]) == 6 and view["diagnostic"] is None
    assert set(view["cases"][0]) == {"index", "passed"}  # no inputs or expected outputs
    assert "expected" not in failed.text and "[3, 4]" not in failed.text

    passed = await client.post(f"/workspace/{PID}/run", headers=headers, json=_body([
        ("helpers.py", "def multiply(a, b):\n    return a * b\n"),
        ("solution.py", "from helpers import multiply\n\ndef total_cost(price, quantity):\n    return multiply(price, quantity)\n")]))
    assert passed.json()["status"] == "passed" and passed.json()["passed"] == 6

    crashed = await client.post(f"/workspace/{PID}/run", headers=headers,
                                json=_body([("solution.py", "def total_cost(price, quantity):\n    return price * missing\n")]))
    diagnostic = crashed.json()["diagnostic"]
    assert crashed.json()["status"] == "failed" and "missing" in diagnostic["message"]

    # Runs are free and never unlock the reference solution.
    assert not await can_reveal(db, uid, PID, "python")
    balance = (await client.get("/auth/me", headers=headers)).json()["peppercorns"]
    assert balance == settings.signup_bonus
    assert await db.scalar(select(func.count()).select_from(WorkspaceRun).where(WorkspaceRun.user_id == uid)) == 3


async def test_test_runs_are_rate_limited(client, db, monkeypatch):
    monkeypatch.setattr(settings, "workspace_runs_per_hour", 1)
    uid, headers = await _learner(client, db)
    assert (await client.post(f"/workspace/{PID}/run", headers=headers, json=_body([("solution.py", RIGHT)]))).status_code == 200
    limited = await client.post(f"/workspace/{PID}/run", headers=headers, json=_body([("solution.py", RIGHT)]))
    assert limited.status_code == 429


async def test_workspace_requires_language_access(client, db):
    _, headers = await _learner(client, db, language="java")
    assert (await client.get(f"/workspace/{PID}", params={"language": "python"}, headers=headers)).status_code in (403, 404)
    assert (await client.post(f"/workspace/{PID}/run", headers=headers, json=_body([("solution.py", RIGHT)]))).status_code in (403, 404)


# ------------------------------------------------------------- reveal policy

async def _events(db, uid, *kinds):
    for kind in kinds:
        db.add(LearningEvent(user_id=uid, problem_id=PID, kind=kind, language="python"))
    await db.commit()


async def test_reveal_policy_is_configurable(client, db, monkeypatch):
    uid, _ = await _learner(client, db)
    await _events(db, uid, "evaluated", "attempt")
    assert await can_reveal(db, uid, PID, "python")
    monkeypatch.setattr(settings, "solution_reveal_min_evaluations", 2)
    assert not await can_reveal(db, uid, PID, "python")
    monkeypatch.setattr(settings, "solution_reveal_policy", "after_pass")
    assert not await can_reveal(db, uid, PID, "python")
    await _events(db, uid, "evaluated", "solved")
    assert await can_reveal(db, uid, PID, "python")
    monkeypatch.setattr(settings, "solution_reveal_policy", "disabled")
    assert not await can_reveal(db, uid, PID, "python")


# ------------------------------------------------------------- summaries and privacy

async def test_session_summary_counts_this_session_only(client, db):
    uid, headers = await _learner(client, db)
    old = datetime.now(timezone.utc) - timedelta(days=2)
    db.add(LearningEvent(user_id=uid, problem_id=PID, kind="hint", language="python", hint_tier=4, created_at=old))
    item = PracticeSession(user_id=uid, problem_id=PID, language="python", provider="gemini",
                           created_at=datetime.now(timezone.utc) - timedelta(minutes=5))
    db.add(item)
    await db.commit()
    await _events(db, uid, "hint", "evaluated", "solved", "reflection")
    db.add(WorkspaceRun(user_id=uid, problem_id=PID, language="python", kind="evaluation",
                        status="passed", passed_cases=6, total_cases=6))
    db.add(WorkspaceRun(user_id=uid, problem_id=PID, language="python", kind="run", status="failed"))
    await db.commit()
    summary = (await client.get(f"/practice/sessions/{item.id}/summary", headers=headers)).json()
    assert summary["solved"] is True and summary["test_runs"] == 1
    assert summary["hint_tiers"] == [0]
    assert summary["evaluations"][0]["passed"] == 6
    other_uid, other = await _learner(client, db, email="summary-other@example.com")
    assert (await client.get(f"/practice/sessions/{item.id}/summary", headers=other)).status_code == 404


async def test_profile_export_includes_workspaces_and_erase_keeps_saved_work(client, db):
    uid, headers = await _learner(client, db)
    await client.put(f"/workspace/{PID}", headers=headers, json=_body([("solution.py", RIGHT)]))
    await client.post(f"/workspace/{PID}/checkpoints", headers=headers, json=_body([("solution.py", RIGHT)]))
    exported = (await client.get("/mentor/profile/export", headers=headers)).json()
    assert exported["workspace"]["drafts"][0]["files"][0]["content"] == RIGHT
    assert len(exported["workspace"]["checkpoints"]) == 1
    # Erasing the behavioural profile keeps saved work, as the profile page says;
    # retention of learner work is an open product decision.
    assert (await client.delete("/mentor/profile", headers=headers)).status_code == 200
    assert await db.scalar(select(func.count()).select_from(WorkspaceDraft).where(WorkspaceDraft.user_id == uid)) == 1
    from app.services.workspace import delete_for_user
    await delete_for_user(db, uid)
    await db.commit()
    for model in (WorkspaceDraft, WorkspaceCheckpoint, WorkspaceRun):
        assert await db.scalar(select(func.count()).select_from(model).where(model.user_id == uid)) == 0


# ------------------------------------------------------------- evaluation coverage

def test_evaluations_now_run_tests_for_scripted_languages():
    from app.services.deep_review import run_curated
    if not available_languages().get("typescript"):
        pytest.skip("TypeScript toolchain unavailable")
    source = ("function safeAt(values: readonly number[], index: number, fallback: number): number {\n"
              "    return index >= 0 && index < values.length ? values[index] : fallback;\n}")
    report = run_curated("typescript-path-10-validation", source, "typescript")
    result = report["results"][0]
    assert result["tier"] == 1 and result["status"] == "passed", result


def test_function_mode_diagnostics_point_at_the_learners_file_without_sandbox_paths():
    files = [{"name": "helpers.py", "content": "def m(a, b):\n    return a * nope"},
             {"name": "solution.py", "content": "from helpers import m\ndef total_cost(p, q):\n    return m(p, q)"}]
    code, source_map = workspace.bundle("python", files, "solution.py")
    trace = ('Traceback (most recent call last):\n  File "/tmp/x/s.py", line 13, in <module>\n'
             '  File "/tmp/x/s.py", line 5, in m\nNameError: name \'nope\' is not defined')
    message, located = workspace.clean_diagnostic("python", trace, source_map)
    assert "/tmp/x" not in message and located == {"file": "helpers.py", "line": 2}
    message, _ = workspace.clean_diagnostic("javascript", "at endReadableNT (node:internal/streams/readable:1698:12)", [])
    assert "node:internal/streams/readable" in message


async def test_multi_file_evaluation_runs_the_bundle_and_records_a_checkpoint(client, db, monkeypatch):
    from types import SimpleNamespace
    from app.models.schemas import AnalysisResult
    feedback = AnalysisResult(mistakes=[], enhancements=[], watchouts=[], interview_tips=[],
                              overall_feedback="Checked against the execution evidence.")

    async def draft(**kwargs):
        return feedback

    class Model:
        def with_structured_output(self, *args):
            return self

        async def ainvoke(self, prompt):
            return feedback
    monkeypatch.setattr("app.services.deep_review.analyze_solution", draft)
    monkeypatch.setattr("app.services.deep_review.get_llm", lambda _: Model())
    monkeypatch.setattr("app.services.knowledge_base.get_vectorstore",
                        lambda: SimpleNamespace(similarity_search=lambda *a, **kw: []))
    monkeypatch.setattr(settings, "solution_reveal_policy", "after_pass")
    uid, headers = await _learner(client, db)
    started = await client.post("/practice/sessions", headers={**headers, "Idempotency-Key": "ws-start"},
                                json={"problem_id": PID, "language": "python"})
    assert started.status_code == 200, started.text
    path = f"/practice/sessions/{started.json()['session_id']}/actions"
    files = [{"name": "helpers.py", "content": "def mul(a, b):\n    return a + b\n"},
             {"name": "solution.py", "content": "from helpers import mul\n\ndef total_cost(price, quantity):\n    return mul(price, quantity)\n"},
             {"name": "NOTES.md", "content": "try multiplication"}]
    failed = await client.post(path, headers={**headers, "Idempotency-Key": "ws-fail"},
                               json={"action": "submit", "files": files, "entry": "solution.py"})
    assert failed.status_code == 200, failed.text
    body = failed.json()
    assert body["outcome"] == "failed" and body["tests"]["status"] == "failed"
    assert body["source_map"][0]["file"] == "helpers.py"
    # Evaluated, but this course reveals solutions only after a pass.
    assert body["solution_available"] is False

    files[0]["content"] = "def mul(a, b):\n    return a * b\n"
    passed = await client.post(path, headers={**headers, "Idempotency-Key": "ws-pass"},
                               json={"action": "submit", "files": files, "entry": "solution.py"})
    assert passed.json()["outcome"] == "passed" and passed.json()["solution_available"] is True
    checkpoints = (await db.scalars(select(WorkspaceCheckpoint).where(
        WorkspaceCheckpoint.user_id == uid, WorkspaceCheckpoint.kind == "evaluation"))).all()
    assert sorted(c.label for c in checkpoints) == ["Evaluation: 0/6 tests", "Evaluation: 6/6 tests"]
    runs = (await db.scalars(select(WorkspaceRun).where(WorkspaceRun.user_id == uid))).all()
    assert sorted(r.status for r in runs) == ["failed", "passed"] and all(r.kind == "evaluation" for r in runs)

    bad = await client.post(path, headers={**headers, "Idempotency-Key": "ws-bad"},
                            json={"action": "submit", "files": [{"name": "../x.py", "content": "x"}], "entry": "../x.py"})
    assert bad.status_code == 422
