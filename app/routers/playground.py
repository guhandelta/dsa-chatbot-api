"""Web playground: HTML, CSS, JavaScript and TypeScript projects with a live
preview. The preview itself runs in the learner's browser, in a sandboxed
iframe with no network access and no access to the application (see the UI's
lib/preview.ts). The server stores the files and compiles TypeScript inside
the execution sandbox, so compiler output is the same as everywhere else.
"""
import json
import re
import tempfile
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.security import get_current_user
from app.db.database import get_session
from app.db.models import User, WorkspaceDraft, WorkspaceRun
from app.services.strikes import AccountSuspendedError, assert_active

router = APIRouter(prefix="/playground", tags=["playground"])

LANGUAGE = "web"
PREFIX = "playground:"
SLUG = re.compile(r"[a-z0-9][a-z0-9-]{0,39}")
NAME = re.compile(r"[A-Za-z0-9_][A-Za-z0-9_.-]{0,63}")
EXTENSIONS = (".html", ".css", ".js", ".ts", ".jsx", ".tsx", ".md", ".txt")
COMPILED = (".ts", ".tsx", ".jsx")
MAX_FILES = 12
MAX_TOTAL_CHARS = 60_000
MAX_PROJECTS = 30

_HTML = """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>{title}</title>
  <link rel="stylesheet" href="styles.css">
</head>
<body>
  <main>
    <h1>Hello, playground</h1>
    <button id="count" type="button">Clicked 0 times</button>
  </main>
  <script src="{script}"></script>
</body>
</html>
"""
_CSS = "body {\n  font-family: system-ui, sans-serif;\n  margin: 2rem;\n}\n\nbutton {\n  padding: 0.5rem 1rem;\n}\n"
_JS = ("const button = document.getElementById('count');\nlet clicks = 0;\n\n"
       "button.addEventListener('click', () => {\n  clicks += 1;\n  button.textContent = `Clicked ${clicks} times`;\n"
       "  console.log('clicks', clicks);\n});\n")
_TS = ("const button = document.getElementById('count') as HTMLButtonElement;\nlet clicks: number = 0;\n\n"
       "button.addEventListener('click', () => {\n  clicks += 1;\n  button.textContent = `Clicked ${clicks} times`;\n"
       "  console.log('clicks', clicks);\n});\n")

_REACT_HTML = """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>React playground</title>
  <link rel="stylesheet" href="styles.css">
</head>
<body>
  <div id="root"></div>
  <script src="app.tsx"></script>
</body>
</html>
"""
_REACT_APP = """function Counter({ start }: { start: number }) {
  const [count, setCount] = React.useState(start);
  return (
    <button type="button" onClick={() => setCount(count + 1)}>
      Clicked {count} times
    </button>
  );
}

function App() {
  return (
    <main>
      <h1>Hello, React</h1>
      <Counter start={0} />
    </main>
  );
}

ReactDOM.createRoot(document.getElementById('root')!).render(<App />);
"""
# React and ReactDOM are globals in the preview (the UI inlines them); these
# declarations let the compiler accept them without @types/react.
REACT_GLOBALS = """declare const React: any;
declare const ReactDOM: any;
declare namespace JSX {
  interface IntrinsicElements { [name: string]: any }
  interface Element {}
}
"""

TEMPLATES = {
    "html-css-js": {"title": "HTML, CSS and JavaScript", "entry": "index.html",
                    "files": [("index.html", _HTML.format(title="Playground", script="script.js")),
                              ("styles.css", _CSS), ("script.js", _JS)]},
    "html-css-ts": {"title": "HTML, CSS and TypeScript", "entry": "index.html",
                    "files": [("index.html", _HTML.format(title="Playground", script="script.ts")),
                              ("styles.css", _CSS), ("script.ts", _TS)]},
    "react-tsx": {"title": "React with TypeScript", "entry": "index.html",
                  "files": [("index.html", _REACT_HTML), ("styles.css", _CSS), ("app.tsx", _REACT_APP)]},
    "html-css": {"title": "HTML and CSS only", "entry": "index.html",
                 "files": [("index.html", _HTML.format(title="Playground", script="").replace(
                     '  <script src=""></script>\n', "")), ("styles.css", _CSS)]},
}


class PlaygroundFile(BaseModel):
    name: str = Field(min_length=1, max_length=64)
    content: str = Field(default="", max_length=MAX_TOTAL_CHARS)


class FilesBody(BaseModel):
    files: list[PlaygroundFile] = Field(min_length=1, max_length=MAX_FILES)


class SaveBody(FilesBody):
    template: str = Field(default="html-css-js", max_length=40)
    revision: int | None = None
    force: bool = False


def _active(user: User):
    try:
        assert_active(user)
    except AccountSuspendedError as exc:
        raise HTTPException(403, str(exc))


def _slug(slug: str) -> str:
    if not SLUG.fullmatch(slug):
        raise HTTPException(422, "Project names use lowercase letters, digits and dashes.")
    return PREFIX + slug


def validate(files: list[dict]) -> list[dict]:
    names = [f["name"] for f in files]
    if len(set(names)) != len(names):
        raise HTTPException(422, "File names must be unique.")
    if "index.html" not in names:
        raise HTTPException(422, "A web project needs an index.html.")
    for name in names:
        if not NAME.fullmatch(name) or ".." in name or not name.endswith(EXTENSIONS):
            raise HTTPException(422, f"{name}: use .html, .css, .js, .ts, .jsx, .tsx, .md or .txt files.")
    if sum(len(f["content"]) for f in files) > MAX_TOTAL_CHARS:
        raise HTTPException(422, f"A web project holds at most {MAX_TOTAL_CHARS:,} characters.")
    return [{"name": f["name"], "content": f["content"]} for f in files]


def _view(slug: str, draft: WorkspaceDraft | None, template: str = "html-css-js") -> dict:
    if draft is None:
        chosen = TEMPLATES[template]
        return {"slug": slug, "template": template, "entry": "index.html", "revision": None, "updated_at": None,
                "files": [{"name": n, "content": c} for n, c in chosen["files"]]}
    return {"slug": slug, "template": draft.template, "entry": draft.entry, "revision": draft.revision,
            "updated_at": draft.updated_at.isoformat() if draft.updated_at else None,
            "files": json.loads(draft.files_json)}


async def _draft(session, user_id, slug):
    return await session.scalar(select(WorkspaceDraft).where(
        WorkspaceDraft.user_id == user_id, WorkspaceDraft.problem_id == _slug(slug),
        WorkspaceDraft.language == LANGUAGE))


@router.get("")
async def list_projects(user: User = Depends(get_current_user), session: AsyncSession = Depends(get_session)):
    _active(user)
    drafts = (await session.scalars(select(WorkspaceDraft).where(
        WorkspaceDraft.user_id == user.id, WorkspaceDraft.language == LANGUAGE).order_by(
        WorkspaceDraft.updated_at.desc()))).all()
    return {"projects": [{"slug": d.problem_id[len(PREFIX):], "template": d.template,
                          "updated_at": d.updated_at.isoformat() if d.updated_at else None} for d in drafts],
            "templates": [{"id": k, "title": v["title"]} for k, v in TEMPLATES.items()],
            "limits": {"max_files": MAX_FILES, "max_total_chars": MAX_TOTAL_CHARS, "max_projects": MAX_PROJECTS}}


@router.get("/{slug}")
async def open_project(slug: str, template: str = "html-css-js", user: User = Depends(get_current_user),
                       session: AsyncSession = Depends(get_session)):
    _active(user)
    _slug(slug)
    if template not in TEMPLATES:
        raise HTTPException(422, "Unknown template.")
    return _view(slug, await _draft(session, user.id, slug), template)


@router.put("/{slug}")
async def save_project(slug: str, body: SaveBody, user: User = Depends(get_current_user),
                       session: AsyncSession = Depends(get_session)):
    _active(user)
    key = _slug(slug)
    if body.template not in TEMPLATES:
        raise HTTPException(422, "Unknown template.")
    files = validate([f.model_dump() for f in body.files])
    from app.services.user_lock import lock_user
    await lock_user(session, user.id)
    draft = await _draft(session, user.id, slug)
    current = draft.revision if draft else None
    if not body.force and body.revision != current:
        raise HTTPException(409, {"message": "This project was saved from another tab or device.", "revision": current})
    if draft is None:
        count = await session.scalar(select(func.count()).select_from(WorkspaceDraft).where(
            WorkspaceDraft.user_id == user.id, WorkspaceDraft.language == LANGUAGE))
        if count >= MAX_PROJECTS:
            raise HTTPException(409, f"You can keep up to {MAX_PROJECTS} playground projects.")
        draft = WorkspaceDraft(user_id=user.id, problem_id=key, language=LANGUAGE, revision=0)
        session.add(draft)
    from datetime import datetime, timezone
    draft.files_json, draft.entry, draft.template = json.dumps(files), "index.html", body.template
    draft.revision = (draft.revision or 0) + 1
    draft.updated_at = datetime.now(timezone.utc)
    await session.commit()
    return {"revision": draft.revision, "updated_at": draft.updated_at.isoformat()}


_TSC_LINE = re.compile(r"^(?P<file>[\w.-]+\.(?:ts|tsx|jsx))\((?P<line>\d+),(?P<col>\d+)\): (?P<kind>error|warning) (?P<code>TS\d+): (?P<message>.*)$")


def parse_tsc(output: str) -> list[dict]:
    diagnostics = []
    for raw in output.splitlines():
        m = _TSC_LINE.match(raw.strip())
        if m:
            diagnostics.append({"file": m["file"], "line": int(m["line"]), "column": int(m["col"]),
                                "code": m["code"], "message": m["message"]})
        elif raw.strip() and diagnostics:
            diagnostics[-1]["message"] += " " + raw.strip()
    return diagnostics


def transpile(files: list[dict]) -> dict:
    """Compile .ts, .tsx and .jsx files to browser JavaScript in the sandbox.
    JSX becomes React.createElement calls. Type errors are reported but do not
    stop the output, so the preview still runs."""
    from app.services.code_runner import _run
    sources = [f for f in files if f["name"].endswith(COMPILED)]
    if not sources:
        return {"outputs": {}, "diagnostics": []}
    react = any(f["name"].endswith((".tsx", ".jsx")) for f in sources)
    with tempfile.TemporaryDirectory(prefix="dsa-ts-") as scratch:
        cwd = Path(scratch)
        for f in sources:
            (cwd / f["name"]).write_text(f["content"], encoding="utf-8")
        names = [f["name"] for f in sources]
        flags = ["--target", "es2020", "--lib", "es2020,dom", "--module", "es2020", "--strict",
                 "--skipLibCheck", "--pretty", "false", "--outDir", "out"]
        if react:
            (cwd / "react-globals.d.ts").write_text(REACT_GLOBALS, encoding="utf-8")
            flags += ["--jsx", "react", "--allowJs"]
            names.append("react-globals.d.ts")
        code, out, err = _run(["tsc", *flags, *names], cwd, apply_address_space=False)
        outputs = {}
        for f in sources:
            emitted = cwd / "out" / (f["name"].rsplit(".", 1)[0] + ".js")
            if emitted.exists():
                outputs[f["name"]] = emitted.read_text(encoding="utf-8")
    diagnostics = parse_tsc(out or err)
    if code != 0 and not diagnostics and not outputs:
        diagnostics = [{"file": None, "line": None, "column": None, "code": "", "message": (err or out).strip()[:600]}]
    return {"outputs": outputs, "diagnostics": diagnostics}


@router.post("/transpile")
async def transpile_project(body: FilesBody, user: User = Depends(get_current_user),
                            session: AsyncSession = Depends(get_session)):
    import asyncio
    from datetime import datetime, timedelta, timezone
    _active(user)
    files = [f.model_dump() for f in body.files]
    for f in files:
        if not NAME.fullmatch(f["name"]) or ".." in f["name"]:
            raise HTTPException(422, f"Invalid file name: {f['name']!r}.")
    if sum(len(f["content"]) for f in files) > MAX_TOTAL_CHARS:
        raise HTTPException(422, f"A web project holds at most {MAX_TOTAL_CHARS:,} characters.")
    # TypeScript compiles count against the same hourly budget as test runs.
    from app.services.user_lock import lock_user
    await lock_user(session, user.id)
    if settings.workspace_runs_per_hour > 0:
        since = datetime.now(timezone.utc) - timedelta(hours=1)
        used = await session.scalar(select(func.count()).select_from(WorkspaceRun).where(
            WorkspaceRun.user_id == user.id, WorkspaceRun.kind.in_(("run", "transpile")),
            WorkspaceRun.created_at >= since))
        if used >= settings.workspace_runs_per_hour:
            raise HTTPException(429, "You've reached the hourly limit for runs and compiles. Try again shortly.")
    run = WorkspaceRun(user_id=user.id, problem_id="playground", language=LANGUAGE, kind="transpile")
    session.add(run)
    await session.commit()
    try:
        result = await asyncio.to_thread(transpile, files)
    except RuntimeError:
        run.status = "error"
        await session.commit()
        raise HTTPException(503, "The TypeScript compiler is unavailable right now.")
    run.status = "failed" if result["diagnostics"] else "passed"
    await session.commit()
    return result
