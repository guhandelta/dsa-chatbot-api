"""Practice workspace: autosaved files, checkpoints, reset, and free test runs.

A test run executes the problem's curated cases and nothing else: no review,
no LLM, no peppercorns, and it never unlocks the reference solution. Only a
paid evaluation (POST /practice/sessions/{sid}/actions) does that.

Curated test inputs are hidden content (see content_access.public_text), so a
run reports which numbered cases passed and the compiler/runtime diagnostics,
never the inputs or expected outputs.
"""
import asyncio
import json
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.security import get_current_user
from app.db.database import get_session
from app.db.models import LearningEvent, User, WorkspaceCheckpoint, WorkspaceDraft, WorkspaceRun
from app.routers.analyze import screen_submission, validate_problem
from app.services import workspace
from app.services.content_access import can_reveal, reveal_policy, solution_document
from app.services.content_catalog import filter_content
from app.services.language_access import require_content
from app.services.strikes import AccountSuspendedError, assert_active

router = APIRouter(prefix="/workspace", tags=["workspace"])


class WorkspaceFile(BaseModel):
    name: str = Field(min_length=1, max_length=64)
    content: str = Field(default="", max_length=workspace.MAX_TOTAL_CHARS)


class FilesBody(BaseModel):
    language: str = Field(min_length=1, max_length=20)
    files: list[WorkspaceFile] = Field(min_length=1, max_length=workspace.MAX_FILES)
    entry: str = Field(min_length=1, max_length=64)


class SaveBody(FilesBody):
    template: str = Field(default="single", max_length=40)
    # The revision this edit was based on; None creates the first draft.
    revision: int | None = None
    # Overwrite a newer save from another tab after the learner chose to.
    force: bool = False


class CheckpointBody(FilesBody):
    label: str = Field(default="", max_length=120)


class ResetBody(BaseModel):
    language: str = Field(min_length=1, max_length=20)
    template: str = Field(default="single", max_length=40)


def _active(user: User):
    try:
        assert_active(user)
    except AccountSuspendedError as exc:
        raise HTTPException(403, str(exc))


async def _scope(session, user, problem_id, language):
    _active(user)
    validate_problem(problem_id, language)
    await require_content(session, user, problem_id, language)
    if language not in workspace.ENTRY:
        raise HTTPException(422, "This language has no practice workspace.")


def _starter(problem_id: str) -> str:
    item = next((c for c in filter_content() if c.id == problem_id), None)
    return item.starter_code if item else ""


def _files(body: FilesBody) -> list[dict]:
    return workspace.validate(body.language, [f.model_dump() for f in body.files], body.entry)


def _draft_view(draft: WorkspaceDraft | None, problem_id: str, language: str) -> dict:
    if draft is None:
        files = workspace.starter_files(language, "single", _starter(problem_id))
        return {"files": files, "entry": workspace.ENTRY[language], "template": "single",
                "revision": None, "updated_at": None}
    return {"files": json.loads(draft.files_json), "entry": draft.entry, "template": draft.template,
            "revision": draft.revision, "updated_at": draft.updated_at.isoformat() if draft.updated_at else None}


def _checkpoint_view(c: WorkspaceCheckpoint, with_files: bool = False) -> dict:
    view = {"id": c.id, "kind": c.kind, "label": c.label, "entry": c.entry,
            "created_at": c.created_at.isoformat(),
            "file_names": [f["name"] for f in json.loads(c.files_json)]}
    if with_files:
        view["files"] = json.loads(c.files_json)
    return view


async def _draft(session, user_id, problem_id, language) -> WorkspaceDraft | None:
    return await session.scalar(select(WorkspaceDraft).where(
        WorkspaceDraft.user_id == user_id, WorkspaceDraft.problem_id == problem_id,
        WorkspaceDraft.language == language))


async def add_checkpoint(session, user_id, problem_id, language, files, entry, kind, label=""):
    """Store a snapshot and keep at most `workspace_max_checkpoints`, pruning
    automatic snapshots before the learner's own."""
    session.add(WorkspaceCheckpoint(user_id=user_id, problem_id=problem_id, language=language,
                                    kind=kind, label=label[:120], entry=entry, files_json=json.dumps(files)))
    await session.flush()
    rows = list((await session.scalars(select(WorkspaceCheckpoint).where(
        WorkspaceCheckpoint.user_id == user_id, WorkspaceCheckpoint.problem_id == problem_id,
        WorkspaceCheckpoint.language == language).order_by(WorkspaceCheckpoint.created_at))).all())
    excess = len(rows) - settings.workspace_max_checkpoints
    if excess > 0:
        doomed = sorted(rows[:-1], key=lambda c: (c.kind == "manual", c.created_at))[:excess]
        await session.execute(delete(WorkspaceCheckpoint).where(
            WorkspaceCheckpoint.id.in_([c.id for c in doomed])))


async def _write_draft(session, user_id, problem_id, language, files, entry, template, draft=None):
    if draft is None:
        draft = WorkspaceDraft(user_id=user_id, problem_id=problem_id, language=language, revision=0)
        session.add(draft)
    draft.files_json, draft.entry, draft.template = json.dumps(files), entry, template
    draft.revision = (draft.revision or 0) + 1
    draft.updated_at = datetime.now(timezone.utc)
    await session.flush()
    return draft


async def progress(session, user_id, problem_id, language) -> dict:
    """All-time progress on one problem in one language, from observed events."""
    scope = (LearningEvent.user_id == user_id, LearningEvent.problem_id == problem_id,
             LearningEvent.language == language)
    counts = dict((await session.execute(select(LearningEvent.kind, func.count()).where(*scope)
                                         .group_by(LearningEvent.kind))).all())
    max_hint = await session.scalar(select(func.max(LearningEvent.hint_tier)).where(
        *scope, LearningEvent.kind == "hint")) or 0
    run_scope = (WorkspaceRun.user_id == user_id, WorkspaceRun.problem_id == problem_id,
                 WorkspaceRun.language == language)
    runs = await session.scalar(select(func.count()).select_from(WorkspaceRun).where(
        *run_scope, WorkspaceRun.kind == "run")) or 0
    best = (await session.execute(select(WorkspaceRun.passed_cases, WorkspaceRun.total_cases).where(
        *run_scope, WorkspaceRun.total_cases > 0).order_by(
        (WorkspaceRun.passed_cases * 1.0 / WorkspaceRun.total_cases).desc(),
        WorkspaceRun.created_at.desc()).limit(1))).first()
    last = await session.scalar(select(func.max(LearningEvent.created_at)).where(*scope))
    return {
        "test_runs": runs,
        "evaluations": counts.get("evaluated", 0),
        "attempts": counts.get("attempt", 0) + counts.get("solved", 0),
        "solved": counts.get("solved", 0) > 0,
        "hints": counts.get("hint", 0),
        "highest_hint_tier": max_hint,
        "reflections": counts.get("reflection", 0),
        "best_result": {"passed": best[0], "total": best[1]} if best else None,
        "last_activity": last.isoformat() if last else None,
    }


@router.get("/templates")
async def list_templates(language: str, user: User = Depends(get_current_user)):
    if language not in workspace.ENTRY:
        raise HTTPException(422, "This language has no practice workspace.")
    return {"language": language, "multi_file": language in workspace.MULTI_FILE,
            "templates": workspace.templates(language)}


@router.get("/{problem_id}")
async def open_workspace(problem_id: str, language: str, user: User = Depends(get_current_user),
                         session: AsyncSession = Depends(get_session)):
    await _scope(session, user, problem_id, language)
    draft = await _draft(session, user.id, problem_id, language)
    checkpoints = (await session.scalars(select(WorkspaceCheckpoint).where(
        WorkspaceCheckpoint.user_id == user.id, WorkspaceCheckpoint.problem_id == problem_id,
        WorkspaceCheckpoint.language == language).order_by(WorkspaceCheckpoint.created_at.desc()))).all()
    has_solution = bool(solution_document(problem_id, language))
    return {
        "problem_id": problem_id, "language": language,
        "draft": _draft_view(draft, problem_id, language),
        "templates": workspace.templates(language),
        "multi_file": language in workspace.MULTI_FILE,
        "checkpoints": [_checkpoint_view(c) for c in checkpoints],
        "progress": await progress(session, user.id, problem_id, language),
        "reveal": {**reveal_policy(), "has_solution": has_solution,
                   "available": has_solution and await can_reveal(session, user.id, problem_id, language)},
        "limits": {"max_files": workspace.MAX_FILES, "max_total_chars": workspace.MAX_TOTAL_CHARS,
                   "runs_per_hour": settings.workspace_runs_per_hour},
    }


@router.put("/{problem_id}")
async def save_workspace(problem_id: str, body: SaveBody, user: User = Depends(get_current_user),
                         session: AsyncSession = Depends(get_session)):
    await _scope(session, user, problem_id, body.language)
    files = _files(body)
    if body.template not in {t["id"] for t in workspace.templates(body.language)}:
        raise HTTPException(422, "That project template is not available for this language.")
    draft = await _draft(session, user.id, problem_id, body.language)
    current = draft.revision if draft else None
    if not body.force and body.revision != current:
        raise HTTPException(409, {"message": "This workspace was saved from another tab or device.",
                                  "revision": current})
    draft = await _write_draft(session, user.id, problem_id, body.language, files, body.entry, body.template, draft)
    await session.commit()
    return {"revision": draft.revision, "updated_at": draft.updated_at.isoformat()}


@router.post("/{problem_id}/reset")
async def reset_workspace(problem_id: str, body: ResetBody, user: User = Depends(get_current_user),
                          session: AsyncSession = Depends(get_session)):
    """Start over from the starter code in a chosen template. The current
    files are kept as a checkpoint first, so a reset can be undone."""
    await _scope(session, user, problem_id, body.language)
    files = workspace.starter_files(body.language, body.template, _starter(problem_id))
    entry = workspace.ENTRY[body.language]
    draft = await _draft(session, user.id, problem_id, body.language)
    if draft is not None:
        await add_checkpoint(session, user.id, problem_id, body.language, json.loads(draft.files_json),
                             draft.entry, "before_reset", "Before reset")
    draft = await _write_draft(session, user.id, problem_id, body.language, files, entry, body.template, draft)
    await session.commit()
    return {"draft": _draft_view(draft, problem_id, body.language)}


@router.post("/{problem_id}/checkpoints")
async def create_checkpoint(problem_id: str, body: CheckpointBody, user: User = Depends(get_current_user),
                            session: AsyncSession = Depends(get_session)):
    await _scope(session, user, problem_id, body.language)
    files = _files(body)
    label = body.label.strip() or "Checkpoint"
    await add_checkpoint(session, user.id, problem_id, body.language, files, body.entry, "manual", label)
    await session.commit()
    latest = await session.scalar(select(WorkspaceCheckpoint).where(
        WorkspaceCheckpoint.user_id == user.id, WorkspaceCheckpoint.problem_id == problem_id,
        WorkspaceCheckpoint.language == body.language).order_by(WorkspaceCheckpoint.created_at.desc()).limit(1))
    return _checkpoint_view(latest)


async def _owned_checkpoint(session, user, problem_id, cid) -> WorkspaceCheckpoint:
    item = await session.get(WorkspaceCheckpoint, cid)
    if item is None or item.user_id != user.id or item.problem_id != problem_id:
        raise HTTPException(404, "Checkpoint not found")
    await _scope(session, user, problem_id, item.language)
    return item


@router.get("/{problem_id}/checkpoints/{cid}")
async def read_checkpoint(problem_id: str, cid: str, user: User = Depends(get_current_user),
                          session: AsyncSession = Depends(get_session)):
    return _checkpoint_view(await _owned_checkpoint(session, user, problem_id, cid), with_files=True)


@router.post("/{problem_id}/checkpoints/{cid}/restore")
async def restore_checkpoint(problem_id: str, cid: str, user: User = Depends(get_current_user),
                             session: AsyncSession = Depends(get_session)):
    item = await _owned_checkpoint(session, user, problem_id, cid)
    files, entry = json.loads(item.files_json), item.entry
    draft = await _draft(session, user.id, problem_id, item.language)
    if draft is not None:
        await add_checkpoint(session, user.id, problem_id, item.language, json.loads(draft.files_json),
                             draft.entry, "before_restore", f"Before restoring {item.label or 'a checkpoint'}")
    template = draft.template if draft else "single"
    draft = await _write_draft(session, user.id, problem_id, item.language, files, entry, template, draft)
    await session.commit()
    return {"draft": _draft_view(draft, problem_id, item.language)}


@router.delete("/{problem_id}/checkpoints/{cid}")
async def delete_checkpoint(problem_id: str, cid: str, user: User = Depends(get_current_user),
                            session: AsyncSession = Depends(get_session)):
    item = await _owned_checkpoint(session, user, problem_id, cid)
    await session.delete(item)
    await session.commit()
    return {"deleted": cid}


COMPILED_LANGUAGES = frozenset({"c", "cpp", "java", "rust", "csharp", "go", "kotlin", "swift", "scala", "haskell", "dart"})


def case_report(report: dict | None, language: str, problem_id: str, source_map: list[dict],
                entry_alias: dict | None = None) -> dict:
    """Learner-safe run output: per-case pass/fail and diagnostics only."""
    if not report:
        return {"status": "unverified", "passed": 0, "total": 0, "cases": [],
                "detail": "This problem has no executable tests in this language.", "diagnostic": None}
    from app.services.content_catalog import comparison_mode, load_test_cases
    from app.services.output_comparison import compare
    result = next((r for r in report.get("results", []) if r.get("language") == language), None) or {}
    _, expected, _, _ = load_test_cases(problem_id)
    outputs = result.get("outputs") or []
    mode = comparison_mode(problem_id)
    ran = result.get("tier") == 1 and result.get("status") in ("passed", "failed")
    cases = []
    flags = result.get("case_results")
    if ran and flags:
        cases = [{"index": i + 1, "passed": bool(ok)} for i, ok in enumerate(flags)]
    elif ran and outputs:
        for i, want in enumerate(expected):
            cases.append({"index": i + 1, "passed": i < len(outputs) and compare(outputs[i], want, mode)})
    evidence = result.get("evidence") or {}
    diagnostic = None
    if result.get("status") in ("failed", "error") and not result.get("passed_cases") and not outputs and not flags:
        if evidence and evidence.get("file") and evidence.get("line"):
            # A native multi-file run names its real files (helpers included).
            name = (entry_alias or {}).get(evidence["file"], evidence["file"])
            message, located = evidence.get("message") or "", {"file": name, "line": evidence["line"]}
        elif evidence:
            message, located = evidence.get("message") or "", workspace.locate(source_map, evidence.get("line"))
        else:
            message, located = workspace.clean_diagnostic(language, result.get("detail") or "", source_map)
        timed_out = "timed out" in (result.get("detail") or "").lower()
        # Compile-only checks (tier 2) report compiler output and nothing else.
        compile_only = result.get("tier") == 2 and language in COMPILED_LANGUAGES
        phase = evidence.get("phase") or ("timeout" if timed_out else "compile" if compile_only else "run")
        diagnostic = {"phase": phase,
                      "message": message,
                      "file": located["file"] if located else None,
                      "line": located["line"] if located else None}
    return {"status": result.get("status", "unverified"),
            "passed": result.get("passed_cases", 0), "total": result.get("total_cases", len(expected)),
            # A failing run's detail quotes hidden inputs and expected values;
            # only infrastructure explanations (unverified) are passed through.
            "cases": cases, "detail": (result.get("detail") or "") if result.get("status") == "unverified" else "",
            "diagnostic": diagnostic}


@router.post("/{problem_id}/run")
async def run_tests(problem_id: str, body: FilesBody, user: User = Depends(get_current_user),
                    session: AsyncSession = Depends(get_session)):
    await _scope(session, user, problem_id, body.language)
    files = _files(body)
    code, source_map = workspace.bundle(body.language, files, body.entry)
    if not code.strip():
        raise HTTPException(422, "Write some code before running the tests.")
    await screen_submission(session, user, code, body.language, context="workspace_run")
    if settings.workspace_runs_per_hour > 0:
        since = datetime.now(timezone.utc) - timedelta(hours=1)
        used = await session.scalar(select(func.count()).select_from(WorkspaceRun).where(
            WorkspaceRun.user_id == user.id, WorkspaceRun.kind == "run", WorkspaceRun.created_at >= since))
        if used >= settings.workspace_runs_per_hour:
            raise HTTPException(429, f"You've run the tests {used} times in the past hour, which is the "
                                     f"limit ({settings.workspace_runs_per_hour}). Try again shortly.")
    # Commit the run row before executing so parallel requests count it.
    run = WorkspaceRun(user_id=user.id, problem_id=problem_id, language=body.language, kind="run")
    session.add(run)
    await session.commit()
    from app.services.deep_review import run_curated
    from app.services.execution_adapters import ADAPTERS, NATIVE_MULTIFILE
    # Stdin/stdout problems build the learner's files natively (helpers by their
    # real names); function-style problems keep the bundle.
    native, alias = None, None
    code_files = [f for f in files if not f["name"].endswith(workspace.NOTE_EXTENSIONS)]
    if body.language in NATIVE_MULTIFILE and len(code_files) > 1:
        entry_name = ADAPTERS[body.language].source
        native = {entry_name: next(f["content"] for f in code_files if f["name"] == body.entry)}
        native.update({f["name"]: f["content"] for f in code_files if f["name"] != body.entry})
        alias = {entry_name: body.entry}
    try:
        report = await asyncio.to_thread(run_curated, problem_id, code, body.language, native)
    except RuntimeError:
        run.status = "error"
        await session.commit()
        raise HTTPException(503, "The code runner is unavailable right now. Test runs never cost peppercorns.")
    view = case_report(report, body.language, problem_id, source_map, alias)
    run.status, run.passed_cases, run.total_cases = view["status"], view["passed"], view["total"]
    await session.commit()
    return {**view, "source_map": source_map}
