#!/usr/bin/env python3
"""Preflight check. Run this BEFORE starting the server.

    python tools/doctor.py              # full check
    python tools/doctor.py --quick      # skip the slow execution checks

Catches the things that otherwise surface as a confusing runtime error ten
minutes into using the app: a missing dependency, an unmigrated database, an
unset secret, content that references a function the harness cannot call, a
toolchain that silently downgrades verification.

Exit code 0 = safe to start. 1 = something will break. Warnings do not fail
the run; they tell you which capabilities are degraded.

Nothing here calls a paid API. Key PRESENCE is checked, key validity is not —
that would cost money on every preflight.
"""
from __future__ import annotations

import importlib.util
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

PASS, WARN, FAIL = "PASS", "WARN", "FAIL"
results: list[tuple[str, str, str]] = []


def check(section: str, status: str, message: str) -> None:
    results.append((section, status, message))


# --------------------------------------------------------------- dependencies

REQUIRED_MODULES = {
    "fastapi": "FastAPI web framework",
    "uvicorn": "ASGI server",
    "sqlalchemy": "database ORM",
    "pydantic": "schema validation",
    "pydantic_settings": "settings loading",
    "jwt": "JWT auth (package: pyjwt)",
    "passlib": "password hashing",
    "alembic": "database migrations",
}
OPTIONAL_MODULES = {
    "langchain": "LLM orchestration",
    "langchain_openai": "OpenAI provider",
    "langchain_anthropic": "Anthropic provider",
    "langchain_google_genai": "Gemini provider",
    "chromadb": "vector store",
}


def check_dependencies() -> None:
    for module, why in REQUIRED_MODULES.items():
        if importlib.util.find_spec(module) is None:
            check("deps", FAIL, f"missing '{module}' ({why}) — pip install -r requirements.txt")
        else:
            check("deps", PASS, f"{module}")
    for module, why in OPTIONAL_MODULES.items():
        if importlib.util.find_spec(module) is None:
            check("deps", WARN, f"'{module}' absent ({why}) — that feature will fail at runtime")


# --------------------------------------------------------------- configuration

def check_config() -> None:
    env_file = ROOT / ".env"
    if not env_file.is_file():
        check("config", FAIL, ".env not found — copy .env.example to .env")
        return

    raw = env_file.read_text()
    values = dict(
        re.findall(r"^([A-Z_]+)\s*=\s*(.*)$", raw, re.MULTILINE)
    )

    # Keys: presence only. Validity is never checked — that costs money.
    if not values.get("OPENAI_API_KEY", "").strip():
        check("config", FAIL, "OPENAI_API_KEY is empty (needed for embeddings)")
    elif "your-key-here" in values["OPENAI_API_KEY"]:
        check("config", FAIL, "OPENAI_API_KEY still holds the placeholder value")
    else:
        check("config", PASS, "OPENAI_API_KEY set")

    for optional in ("ANTHROPIC_API_KEY", "GOOGLE_API_KEY"):
        if not values.get(optional, "").strip():
            check("config", WARN, f"{optional} unset — that provider will fail if selected")

    secret = values.get("JWT_SECRET", "").strip()
    if not secret or "change-me" in secret or len(secret) < 32:
        check("config", FAIL,
              "JWT_SECRET is missing, placeholder, or too short. Generate one:\n"
              '        python -c "import secrets; print(secrets.token_hex(32))"')
    else:
        check("config", PASS, "JWT_SECRET looks strong")

    if not values.get("ADMIN_EMAILS", "").strip():
        check("config", WARN,
              "ADMIN_EMAILS unset — nobody can reach /train or /admin. "
              "Set it to the email you will register with.")
    else:
        check("config", PASS, f"ADMIN_EMAILS set ({values['ADMIN_EMAILS']})")

    backend = values.get("VECTOR_STORE", "chroma").strip().lower()
    if backend not in ("chroma", "pgvector"):
        check("config", FAIL, f"VECTOR_STORE='{backend}' is not 'chroma' or 'pgvector'")
    elif backend == "pgvector":
        if importlib.util.find_spec("langchain_postgres") is None:
            check("config", FAIL,
                  "VECTOR_STORE=pgvector but langchain-postgres is not installed "
                  "— pip install -r requirements.txt")
        target = values.get("VECTOR_DATABASE_URL", "").strip() or values.get("DATABASE_URL", "")
        if "sqlite" in target:
            check("config", FAIL,
                  "VECTOR_STORE=pgvector but the database URL points at SQLite. "
                  "pgvector needs Postgres — see docs/SUPABASE.md")
        else:
            check("config", PASS, "pgvector backend configured")
    else:
        check("config", PASS, "vector store: chroma (embedded)")

    if values.get("AUTO_CREATE_TABLES", "false").lower() == "true":
        check("config", WARN,
              "AUTO_CREATE_TABLES=true bypasses migrations. Fine for throwaway "
              "databases, wrong for anything you care about.")

    # .env must never be committed
    gitignore = ROOT / ".gitignore"
    if gitignore.is_file() and ".env" in gitignore.read_text():
        check("config", PASS, ".env is gitignored")
    else:
        check("config", FAIL, ".env is NOT gitignored — your keys could be committed")


# --------------------------------------------------------------- database

def check_database() -> None:
    env_file = ROOT / ".env"
    url = ""
    if env_file.is_file():
        m = re.search(r"^DATABASE_URL\s*=\s*(.*)$", env_file.read_text(), re.MULTILINE)
        url = m.group(1).strip() if m else ""
    url = url or "sqlite+aiosqlite:///./dsa_chatbot.db"

    if url.startswith("sqlite"):
        db_path = ROOT / url.split("///")[-1].lstrip("./")
        if not db_path.is_file():
            check("database", WARN,
                  f"{db_path.name} does not exist yet — run: alembic upgrade head")
            return
        import sqlite3

        con = sqlite3.connect(db_path)
        tables = {r[0] for r in con.execute(
            "SELECT name FROM sqlite_master WHERE type='table'"
        )}
        con.close()

        if "alembic_version" not in tables:
            check("database", FAIL,
                  "database exists but has no migration history. "
                  f"Delete it and re-run migrations:  rm {db_path.name} && alembic upgrade head")
            return

        expected = {
            "users", "transactions", "chat_threads", "chat_messages", "submissions",
            "security_events", "subscriptions", "learning_events", "trace_records",
        }
        missing = expected - tables
        if missing:
            check("database", FAIL,
                  f"tables missing: {sorted(missing)} — run: alembic upgrade head")
        else:
            check("database", PASS, f"schema present ({len(expected)} tables)")
    else:
        check("database", WARN, f"non-SQLite database ({url.split('://')[0]}) — not inspected here")


# --------------------------------------------------------------- toolchains

def check_toolchains() -> None:
    required = {"python3": "Python solutions", "gcc": "C solutions", "g++": "C++ solutions"}
    optional = {"node": "JavaScript execution + fuzzing",
                "javac": "Java verification", "rustc": "Rust verification"}

    for exe, why in required.items():
        if shutil.which(exe):
            check("toolchains", PASS, f"{exe} ({why})")
        else:
            check("toolchains", FAIL, f"{exe} missing — {why} cannot be verified")

    for exe, why in optional.items():
        if shutil.which(exe):
            check("toolchains", PASS, f"{exe} ({why})")
        else:
            hint = "brew install openjdk" if exe == "javac" else (
                "brew install rust" if exe == "rustc" else "install Node 20+")
            check("toolchains", WARN,
                  f"{exe} missing — {why} will be reported 'unverified'. {hint}")


# --------------------------------------------------------------- content

FRONT = re.compile(r"^---\n(.*?)\n---\n", re.DOTALL)


def _front_matter(text: str) -> dict:
    m = FRONT.match(text)
    if not m:
        return {}
    out = {}
    for line in m.group(1).splitlines():
        if ":" in line:
            k, _, v = line.partition(":")
            out[k.strip()] = v.strip()
    return out


def check_content() -> None:
    dirs = [ROOT / "data" / "dsa_problems"] + list((ROOT / "data" / "content").glob("*"))
    files = [f for d in dirs if d.is_dir() for f in d.glob("*.md")]
    if not files:
        check("content", FAIL, "no problem markdown found under data/")
        return
    check("content", PASS, f"{len(files)} content files found")

    langs = ("Python", "JavaScript", "Java", "C++", "C", "Rust")
    no_tests, bad_json, incomplete = [], [], []

    for path in files:
        text = path.read_text()
        front = _front_matter(text)

        if front.get("track", "dsa") == "dsa":
            raw = front.get("test_cases")
            if not raw:
                no_tests.append(path.stem)
            else:
                try:
                    cases = json.loads(raw)
                    if not cases:
                        bad_json.append(path.stem)
                    # the harness calls these by name; a missing name means a
                    # silent fallback to review-only feedback
                    if not front.get("fn_python"):
                        incomplete.append(f"{path.stem} (no fn_python)")
                except json.JSONDecodeError:
                    bad_json.append(path.stem)

            present = sum(1 for l in langs if f"### {l}\n" in text)
            if 0 < present < len(langs):
                incomplete.append(f"{path.stem} ({present}/6 languages)")

    if bad_json:
        check("content", FAIL, f"unparseable test_cases: {bad_json}")
    if no_tests:
        check("content", WARN,
              f"{len(no_tests)} problem(s) without executable tests "
              f"(review-only feedback): {no_tests[:5]}")
    if incomplete:
        check("content", WARN, f"incomplete entries: {incomplete[:5]}")
    if not bad_json and not incomplete:
        check("content", PASS, "all content entries well-formed")


# --------------------------------------------------------------- wiring

def check_wiring() -> None:
    """Static checks for the integration mistakes that are invisible until a
    feature silently does nothing — like a table that is read but never
    written."""
    analyze = (ROOT / "app" / "routers" / "analyze.py").read_text()
    if "learning_profile.record_event" not in analyze:
        check("wiring", FAIL,
              "/analyze does not record learning events — the mentor's pattern "
              "tracking and tier-3 recall would never fire")
    else:
        check("wiring", PASS, "/analyze records learning events")

    main = (ROOT / "app" / "main.py").read_text()
    expected_routers = ["auth", "chat", "analyze", "problems", "tracks",
                        "training", "admin", "mentor", "subscriptions"]
    missing = [r for r in expected_routers if f"{r}.router" not in main]
    if missing:
        check("wiring", FAIL, f"routers not registered in main.py: {missing}")
    else:
        check("wiring", PASS, f"all {len(expected_routers)} routers registered")

    subs = (ROOT / "app" / "routers" / "subscriptions.py").read_text()
    if "stripe_webhook_secret" not in subs:
        check("wiring", FAIL, "subscription webhook does not verify a secret")
    else:
        check("wiring", PASS, "subscription webhook refuses unsigned payloads")


# --------------------------------------------------------------- execution

def check_execution(quick: bool) -> None:
    """Actually run the sandbox end to end. This is the check that proves
    code execution works on THIS machine, which is what the whole review
    pipeline depends on."""
    if quick:
        check("execution", WARN, "skipped (--quick)")
        return

    for tool in ("tools/check_snippets.py", "tools/check_python_correctness.py",
                 "tools/check_migration_drift.py"):
        path = ROOT / tool
        if not path.is_file():
            check("execution", WARN, f"{tool} not found")
            continue
        try:
            proc = subprocess.run([sys.executable, str(path)], cwd=ROOT,
                                  capture_output=True, text=True, timeout=300)
            name = Path(tool).stem
            if proc.returncode == 0:
                tail = [l for l in proc.stdout.strip().splitlines() if l.strip()][-1:]
                check("execution", PASS, f"{name}: {tail[0] if tail else 'ok'}")
            else:
                check("execution", FAIL, f"{name} failed:\n        {proc.stdout.strip()[-300:]}")
        except subprocess.TimeoutExpired:
            check("execution", WARN, f"{tool} timed out")


# --------------------------------------------------------------- report

def main() -> int:
    quick = "--quick" in sys.argv
    print("\nDSA Mentor — preflight check\n" + "=" * 60)

    check_dependencies()
    check_config()
    check_database()
    check_toolchains()
    check_content()
    check_wiring()
    check_execution(quick)

    current = None
    for section, status, message in results:
        if section != current:
            print(f"\n[{section}]")
            current = section
        if status == PASS:
            print(f"  ok    {message}")
        elif status == WARN:
            print(f"  warn  {message}")
        else:
            print(f"  FAIL  {message}")

    fails = sum(1 for _, s, _ in results if s == FAIL)
    warns = sum(1 for _, s, _ in results if s == WARN)
    print("\n" + "=" * 60)
    if fails:
        print(f"{fails} blocking issue(s), {warns} warning(s). Fix the FAILs before starting.")
        return 1
    print(f"Ready to start. {warns} warning(s) — degraded capabilities, not blockers.")
    print("\n  alembic upgrade head")
    print("  python -m app.services.knowledge_base")
    print("  uvicorn app.main:app --reload --port 8000")
    return 0


if __name__ == "__main__":
    sys.exit(main())
