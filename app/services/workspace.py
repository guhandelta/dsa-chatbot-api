"""Practice workspace files: templates, validation and single-program bundling.

The runners execute one program per submission. A multi-file workspace is
therefore bundled into one source text before it runs: helper files first,
the entry file last, and imports of the learner's own files blanked out
(replaced by empty lines, so every line keeps its number). The returned
source map lets the UI point a compiler or runtime line back at the file the
learner wrote it in.

Bundling is only offered where plain concatenation is sound. Java, Go and C#
need package/class restructuring to combine files, so those workspaces stay
single-file (plus notes) and say so through `multi_file` in the capability
profile rather than failing at run time.
"""
from __future__ import annotations

import re
from dataclasses import dataclass

import json

from fastapi import HTTPException
from sqlalchemy import delete, select

MAX_FILES = 8
MAX_TOTAL_CHARS = 20_000  # same cap as a single practice submission
NAME = re.compile(r"[A-Za-z0-9_][A-Za-z0-9_.-]{0,63}")
NOTE_EXTENSIONS = (".md", ".txt")

ENTRY = {
    "python": "solution.py", "javascript": "solution.js", "typescript": "solution.ts",
    "java": "Solution.java", "c": "solution.c", "cpp": "solution.cpp", "rust": "solution.rs",
    "ruby": "solution.rb", "go": "solution.go", "csharp": "Solution.cs",
}
CODE_EXTENSIONS = {
    "python": (".py",), "javascript": (".js",), "typescript": (".ts",), "java": (".java",),
    "c": (".c", ".h"), "cpp": (".cpp", ".hpp", ".h"), "rust": (".rs",), "ruby": (".rb",),
    "go": (".go",), "csharp": (".cs",),
}
HELPER = {
    "python": "helpers.py", "javascript": "helpers.js", "typescript": "helpers.ts",
    "c": "helpers.h", "cpp": "helpers.hpp", "rust": "helpers.rs", "ruby": "helpers.rb",
}
MULTI_FILE = frozenset(HELPER)

NOTES = ("# Notes\n\nApproach:\n\nEdge cases to test:\n\nComplexity:\n")


@dataclass(frozen=True)
class Template:
    id: str
    title: str
    description: str
    multi_file: bool


TEMPLATES = (
    Template("single", "Single file", "One solution file.", False),
    Template("notes", "Solution and notes", "A solution file plus a notes file that is never executed.", False),
    Template("helpers", "Solution and helpers",
             "Split helper functions into their own file. They are combined with the "
             "solution before it runs.", True),
)


def templates(language: str) -> list[dict]:
    return [{"id": t.id, "title": t.title, "description": t.description}
            for t in TEMPLATES if not t.multi_file or language in MULTI_FILE]


def _comment(language: str, text: str) -> str:
    return f"# {text}\n" if language in ("python", "ruby") else f"// {text}\n"


def _helper_stub(language: str) -> str:
    return {
        "python": "# Helper functions. Import them in solution.py with:\n#   from helpers import name\n",
        "javascript": "// Helper functions. Import them in solution.js with:\n//   const { name } = require('./helpers')\n",
        "typescript": "// Helper functions. Import them in solution.ts with:\n//   import { name } from './helpers'\n",
        "c": "// Helper functions. Include them in solution.c with:\n//   #include \"helpers.h\"\n",
        "cpp": "// Helper functions. Include them in solution.cpp with:\n//   #include \"helpers.hpp\"\n",
        "rust": "// Helper functions. Use them in solution.rs with:\n//   mod helpers;\n//   use helpers::name;\n",
        "ruby": "# Helper methods. Load them in solution.rb with:\n#   require_relative 'helpers'\n",
    }[language]


def starter_files(language: str, template: str, starter_code: str) -> list[dict]:
    if template not in {t["id"] for t in templates(language)}:
        raise HTTPException(422, "That project template is not available for this language.")
    entry = starter_code or _comment(language, "Write your solution here.")
    files = [{"name": ENTRY[language], "content": entry}]
    if template == "helpers":
        files.insert(0, {"name": HELPER[language], "content": _helper_stub(language)})
    if template == "notes":
        files.append({"name": "NOTES.md", "content": NOTES})
    return files


def validate(language: str, files: list[dict], entry: str) -> list[dict]:
    """Reject anything the runner cannot honour; return normalised files."""
    if language not in ENTRY:
        raise HTTPException(422, "This language has no practice workspace.")
    if not files or len(files) > MAX_FILES:
        raise HTTPException(422, f"A workspace holds between 1 and {MAX_FILES} files.")
    names = [f.get("name", "") for f in files]
    if len(set(names)) != len(names):
        raise HTTPException(422, "File names must be unique.")
    if entry not in names:
        raise HTTPException(422, "The entry file must be one of the workspace files.")
    total = 0
    code_files = 0
    for f in files:
        name, content = f.get("name", ""), f.get("content", "")
        if not isinstance(content, str) or not NAME.fullmatch(name or "") or ".." in name:
            raise HTTPException(422, f"Invalid file name: {name!r}.")
        if not name.endswith(CODE_EXTENSIONS[language] + NOTE_EXTENSIONS):
            raise HTTPException(422, f"{name} is not a {language} source or notes file.")
        total += len(content)
        code_files += not name.endswith(NOTE_EXTENSIONS)
    if entry.endswith(NOTE_EXTENSIONS):
        raise HTTPException(422, "The entry file must be a source file.")
    if total > MAX_TOTAL_CHARS:
        raise HTTPException(422, f"The workspace exceeds {MAX_TOTAL_CHARS:,} characters.")
    if code_files > 1 and language not in MULTI_FILE:
        raise HTTPException(422, f"{language} workspaces run a single source file. "
                                 "Keep extra material in a .md or .txt notes file.")
    return [{"name": f["name"], "content": f["content"]} for f in files]


def _stems(names: list[str]) -> set[str]:
    return {n.rsplit(".", 1)[0] for n in names}


def _local_import_patterns(language: str, stems: set[str]) -> list[re.Pattern]:
    if not stems:
        return []
    alt = "|".join(re.escape(s) for s in sorted(stems))
    q = r"""['"]"""
    return {
        "python": [re.compile(rf"^\s*from\s+\.?({alt})\s+import\s+[^\n]+$")],
        "javascript": [re.compile(rf"^\s*(?:const|let|var)\s+[^=]+=\s*require\(\s*{q}\./({alt})(?:\.js)?{q}\s*\)\s*;?\s*$"),
                       re.compile(rf"^\s*import\s+[^\n]*from\s+{q}\./({alt})(?:\.js)?{q}\s*;?\s*$")],
        "typescript": [re.compile(rf"^\s*import\s+[^\n]*from\s+{q}\./({alt})(?:\.ts|\.js)?{q}\s*;?\s*$"),
                       re.compile(rf"^\s*(?:const|let|var)\s+[^=]+=\s*require\(\s*{q}\./({alt})(?:\.ts|\.js)?{q}\s*\)\s*;?\s*$")],
        "c": [re.compile(rf"^\s*#\s*include\s+\"({alt})\.h\"\s*$")],
        "cpp": [re.compile(rf"^\s*#\s*include\s+\"({alt})\.(?:h|hpp)\"\s*$")],
        "rust": [re.compile(rf"^\s*(?:pub\s+)?mod\s+({alt})\s*;\s*$"),
                 re.compile(rf"^\s*use\s+(?:crate::|self::)?({alt})::[^\n]+;\s*$")],
        "ruby": [re.compile(rf"^\s*require_relative\s+{q}(?:\./)?({alt})(?:\.rb)?{q}\s*$")],
    }.get(language, [])


_EXPORT = re.compile(r"^(\s*)export\s+(?=(?:async\s+)?(?:function|const|let|var|class|interface|type|enum)\b)")
_MODULE_EXPORTS = re.compile(r"^\s*module\.exports(?:\.\w+)?\s*=")
_PY_BARE_IMPORT = re.compile(r"^\s*import\s+([\w, ]+)")


def _multiline_import(language: str, lines: list[str], index: int, stems: set[str]) -> int | None:
    """Index of the last line of an import of a local file that spans lines,
    e.g. `from helpers import (\n a,\n b)` or `import {\n a\n} from './helpers'`."""
    if not stems:
        return None
    alt = "|".join(re.escape(s) for s in sorted(stems))
    line = lines[index]
    if language == "python":
        if re.match(rf"^\s*from\s+\.?({alt})\s+import\s*\(", line) and ")" not in line:
            return next((j for j in range(index + 1, min(len(lines), index + 50)) if ")" in lines[j]), None)
        return None
    if language in ("javascript", "typescript") and re.match(r"^\s*(?:import|const|let|var)\s*\{[^}]*$", line):
        end = re.compile(rf"""(?:from\s+|require\(\s*)['"]\./({alt})(?:\.[jt]s)?['"]""")
        for j in range(index + 1, min(len(lines), index + 50)):
            if "}" in lines[j]:
                return j if end.search(lines[j]) else None
    return None


def bundle(language: str, files: list[dict], entry: str) -> tuple[str, list[dict]]:
    """Return (program source, source map). Notes files are never executed."""
    code = [f for f in files if not f["name"].endswith(NOTE_EXTENSIONS)]
    if len(code) == 1:
        only = code[0]
        lines = only["content"].count("\n") + 1
        return only["content"], [{"file": only["name"], "start": 1, "end": lines}]
    helpers = [f for f in code if f["name"] != entry]
    # Headers first so declarations precede their uses, then other helpers.
    helpers.sort(key=lambda f: not f["name"].endswith((".h", ".hpp")))
    ordered = helpers + [next(f for f in code if f["name"] == entry)]
    stems = _stems([f["name"] for f in helpers])
    patterns = _local_import_patterns(language, stems)
    out: list[str] = []
    source_map: list[dict] = []
    for f in ordered:
        lines = f["content"].split("\n")
        if language == "python":
            for line in lines:
                m = _PY_BARE_IMPORT.match(line)
                if m and stems & {part.strip().split(" ")[0] for part in m.group(1).split(",")}:
                    raise HTTPException(422, "In a multi-file Python workspace, import helpers with "
                                             "`from helpers import name` rather than `import helpers`.")
        kept = []
        blank_until = -1
        for index, line in enumerate(lines):
            if index <= blank_until:
                kept.append("")
                continue
            span = _multiline_import(language, lines, index, stems)
            if span is not None:
                blank_until = span
                kept.append("")
                continue
            if any(p.match(line) for p in patterns):
                kept.append("")
                continue
            if f is not ordered[-1] and language in ("javascript", "typescript"):
                if _MODULE_EXPORTS.match(line):
                    kept.append("")
                    continue
                line = _EXPORT.sub(r"\1", line)
            kept.append(line)
        start = len(out) + 1
        out.extend(kept)
        source_map.append({"file": f["name"], "start": start, "end": len(out)})
    return "\n".join(out), source_map


def locate(source_map: list[dict], line: int | None) -> dict | None:
    """Map a bundled-program line back to (file, line)."""
    if not line:
        return None
    for part in source_map:
        if part["start"] <= line <= part["end"]:
            return {"file": part["file"], "line": line - part["start"] + 1}
    return None


async def delete_for_user(session, user_id: str) -> None:
    """Erase the learner's workspace files, snapshots and run history."""
    from app.db.models import WorkspaceCheckpoint, WorkspaceDraft, WorkspaceRun
    for model in (WorkspaceDraft, WorkspaceCheckpoint, WorkspaceRun):
        await session.execute(delete(model).where(model.user_id == user_id))


async def export_for_user(session, user_id: str) -> dict:
    from app.db.models import WorkspaceCheckpoint, WorkspaceDraft, WorkspaceRun
    drafts = (await session.scalars(select(WorkspaceDraft).where(WorkspaceDraft.user_id == user_id))).all()
    checkpoints = (await session.scalars(select(WorkspaceCheckpoint).where(
        WorkspaceCheckpoint.user_id == user_id).order_by(WorkspaceCheckpoint.created_at))).all()
    runs = (await session.scalars(select(WorkspaceRun).where(
        WorkspaceRun.user_id == user_id).order_by(WorkspaceRun.created_at))).all()
    return {
        "drafts": [{"problem_id": d.problem_id, "language": d.language, "entry": d.entry,
                    "files": json.loads(d.files_json), "updated_at": d.updated_at.isoformat()} for d in drafts],
        "checkpoints": [{"problem_id": c.problem_id, "language": c.language, "kind": c.kind,
                         "label": c.label, "files": json.loads(c.files_json),
                         "created_at": c.created_at.isoformat()} for c in checkpoints],
        "runs": [{"problem_id": r.problem_id, "language": r.language, "kind": r.kind, "status": r.status,
                  "passed": r.passed_cases, "total": r.total_cases,
                  "created_at": r.created_at.isoformat()} for r in runs],
    }


# Lines the function-style harness puts before the learner's code (see
# code_runner._PY_HARNESS and _JS_HARNESS). Compiled harnesses wrap the code
# in generated drivers, so their line numbers are not mapped back.
HARNESS_OFFSET = {"python": ("s.py", 3), "javascript": ("s.js", 1)}
_ABSOLUTE = re.compile(r"(?<![\w:.])(?:/[\w.@+-]+)+/(?=[\w.-]+\b)")


def clean_diagnostic(language: str, message: str, source_map: list[dict]) -> tuple[str, dict | None]:
    """Strip sandbox paths from a runner message and locate the learner's line."""
    text = _ABSOLUTE.sub("", message or "")
    harness, offset = HARNESS_OFFSET.get(language, (None, 0))
    if not harness:
        return text, None
    if language == "python":
        found = re.findall(rf'File "{re.escape(harness)}", line (\d+)', text)
        line = int(found[-1]) if found else None
    else:
        found = re.search(rf"{re.escape(harness)}:(\d+)", text)
        line = int(found.group(1)) if found else None
    located = locate(source_map, line - offset) if line and line > offset else None
    return text, located
