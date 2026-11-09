"""Executes submitted solutions against test cases in a constrained subprocess.

SECURITY NOTE
-------------
EXEC_BACKEND=docker uses a digest-pinned operator-provided toolchain image,
network isolation, a read-only root, dropped capabilities and resource limits.
It fails closed if Docker/image startup fails. The opt-in subprocess backend
is for trusted local development: resource limits are NOT filesystem/network
isolation and static screening is not a security boundary.

Interpreted and supported compiled signatures execute real test cases. An
unsupported signature or missing toolchain is never reported as passing.
"""
from __future__ import annotations

import json
import os
import re
import resource
import shutil
import signal
import subprocess
import tempfile
from dataclasses import asdict, dataclass, field
from pathlib import Path
from functools import lru_cache

from app.core.config import settings
from app.services import exec_harness
from app.services.execution_adapters import (ADAPTERS, NO_ADDRESS_SPACE_LIMIT, SUPPORT_FILES,
                                             diagnostic_evidence, stdio_commands)

# Interpreted languages: run directly, test cases handed over as JSON on stdin.
TIER1 = ("python", "javascript")

# Compiled languages. These are EXECUTED too, not merely compiled: the test
# data has no JSON parser to rely on in C, so `exec_harness` code-generates a
# driver with the cases embedded as native literals and only the answers are
# printed. When a problem's shape cannot be expressed as a typed signature
# (linked lists, trees, node graphs) execution is refused and the language
# falls back to the compile-only check below — never to a silent pass.
COMPILED = ("c", "cpp", "java", "rust")

# Languages dispatched to the language-specific generated function harnesses.
# JSON-native runtimes take cases as data; typed runtimes get safe literals.
SCRIPTED = ("ruby", "typescript", "go", "csharp", "php", "dart", "kotlin",
            "swift", "scala", "haskell")

# The compile-only fallback, used when execution was refused.
TIER2 = COMPILED

# Which executable proves a toolchain is installed
_TOOLCHAIN = {name: adapter.toolchain for name, adapter in ADAPTERS.items()}


def available_languages() -> dict[str, bool]:
    """Runtime detection — Java/Rust are optional on a dev machine."""
    if settings.exec_backend == "docker":
        return _container_languages(settings.exec_container_image)
    tools = {lang: shutil.which(exe) is not None for lang, exe in _TOOLCHAIN.items()}
    tools["java"] = _working_javac(exec_harness.java_tool("javac"))
    tools["typescript"] = tools["typescript"] and tools["javascript"]
    tools["kotlin"] = tools["kotlin"] and tools["java"]
    tools["scala"] = tools["scala"] and tools["java"] and shutil.which("scala") is not None
    # macOS exposes command shims even when the developer toolchain is absent.
    for language in ("swift", "dart", "kotlin", "scala", "haskell", "php"):
        if tools[language]:
            from app.services.script_runners import PROBE_ARGS
            tools[language] = _working_tool(_TOOLCHAIN[language], tuple(PROBE_ARGS.get(language, ["--version"])))
    if tools["scala"]:
        tools["scala"] = _scala_runner_supports_classpath()
    return tools


@lru_cache(maxsize=1)
def _scala_runner_supports_classpath() -> bool:
    """The current adapter runs compiled classes with legacy `scala -cp`."""
    try:
        result = subprocess.run(["scala", "-version"], capture_output=True, timeout=5, text=True)
    except (OSError, subprocess.TimeoutExpired):
        return False
    banner = result.stdout + result.stderr
    return result.returncode == 0 and "Scala code runner version:" not in banner


@lru_cache(maxsize=8)
def _container_languages(image: str) -> dict[str, bool]:
    tools = {}
    with tempfile.TemporaryDirectory(prefix="dsa-probe-") as scratch:
        for language, executable in _TOOLCHAIN.items():
            from app.services.script_runners import PROBE_ARGS
            args = PROBE_ARGS.get(language, ["--version"])
            tools[language] = False
            for _ in range(2):
                try:
                    tools[language] = _run([executable, *args], Path(scratch))[0] == 0
                    break
                except RuntimeError:
                    # A transient daemon/image-start error should not turn a
                    # runnable language off for the lifetime of this cache.
                    continue
        if tools["scala"]:
            # scalac alone cannot run the program; the `scala` runner must exist too.
            try:
                status, stdout, stderr = _run(["scala", "-version"], Path(scratch))
                tools["scala"] = status == 0 and "Scala code runner version:" not in stdout + stderr
            except RuntimeError:
                tools["scala"] = False
    tools["typescript"] = tools["typescript"] and tools["javascript"]
    tools["kotlin"] = tools["kotlin"] and tools["java"]
    tools["scala"] = tools["scala"] and tools["java"]
    return tools


@lru_cache(maxsize=8)
def _working_javac(executable: str) -> bool:
    # macOS ships a javac shim even when no JDK is installed.
    try:
        result = subprocess.run([executable, "-version"], capture_output=True, timeout=5)
        return result.returncode == 0
    except (OSError, subprocess.TimeoutExpired):
        return False


@lru_cache(maxsize=32)
def _working_tool(executable: str, args: tuple[str, ...] = ("--version",)) -> bool:
    try:
        result = subprocess.run([executable, *args], capture_output=True, timeout=5)
        return result.returncode == 0
    except (OSError, subprocess.TimeoutExpired):
        return False


@dataclass
class LangResult:
    language: str
    tier: int
    status: str                  # "passed" | "failed" | "unverified" | "error"
    detail: str = ""
    passed_cases: int = 0
    total_cases: int = 0
    outputs: list = field(default_factory=list)   # actual outputs, for cross-language agreement
    evidence: dict = field(default_factory=dict)  # observed diagnostics for mentor context


def _limits(apply_address_space: bool = True):
    """Applied inside the child process before exec.

    `apply_address_space` is False for Node and for Java: V8 and the JVM both
    *reserve* a large virtual address space at startup, so an RLIMIT_AS cap
    makes them abort immediately — and `javac` is itself a Java program, so
    the compile step is affected as well. Their heaps are bounded with a
    runtime flag instead (--max-old-space-size, -Xmx). The set of affected
    languages lives in exec_harness.NO_ADDRESS_SPACE_LIMIT.

    This is invisible on macOS, where lowering RLIMIT_AS is refused and the
    error swallowed below, and only shows up on Linux.
    """
    if apply_address_space:
        mem = settings.exec_memory_mb * 1024 * 1024
        try:
            resource.setrlimit(resource.RLIMIT_AS, (mem, mem))
        except (ValueError, OSError):
            # macOS refuses to lower RLIMIT_AS below the address space the
            # process already has reserved, so raising here would kill every
            # run on a dev laptop. The memory cap is enforced on Linux (the
            # production target); locally the wall-clock and CPU limits
            # still bound runaway code.
            pass
    resource.setrlimit(resource.RLIMIT_CPU, (settings.exec_timeout_seconds, settings.exec_timeout_seconds))
    resource.setrlimit(resource.RLIMIT_FSIZE, (16 * 1024 * 1024, 16 * 1024 * 1024))
    # NOTE: RLIMIT_NPROC is deliberately NOT set here. It caps processes
    # per *UID*, not per process tree, so any value below the API user's
    # existing process count makes every fork fail — including the
    # compiler's. Host mode cannot contain a deliberate fork bomb; use the
    # Docker backend for a per-container process limit.
    # No core dumps (they can be large and leak memory contents)
    resource.setrlimit(resource.RLIMIT_CORE, (0, 0))
    # Detach from the parent's process group so a kill takes the whole tree
    os.setsid()


def _run(cmd: list[str], cwd: Path, stdin: str = "",
         apply_address_space: bool = True) -> tuple[int, str, str]:
    settings.validate_execution_policy()
    if settings.exec_backend == "docker":
        from app.services.container_executor import run
        return run(cmd, cwd, stdin, _run_host)
    return _run_host(cmd, cwd, stdin, apply_address_space)


def _run_host(cmd: list[str], cwd: Path, stdin: str = "",
         apply_address_space: bool = True) -> tuple[int, str, str]:
    """Run a command with a stripped env, scratch cwd, and hard timeout."""
    env = {"PATH": os.environ.get("PATH", "/usr/bin:/bin"), "HOME": str(cwd),
           "TMPDIR": str(cwd), "TMP": str(cwd), "TEMP": str(cwd), "LANG": "C.UTF-8"}
    # A few variables only tell a toolchain where it lives. Without them the
    # toolchain cannot start at all: `rustc` from a rustup install is a shim
    # that resolves the real compiler through RUSTUP_HOME, and with HOME
    # pointed at the scratch directory it exits with "could not choose a
    # version of rustc". These are toolchain-location settings, not secrets.
    # Host execution still has no filesystem or network isolation.
    for _k in exec_harness.TOOLCHAIN_ENV_PASSTHROUGH:
        if _k in os.environ:
            env[_k] = os.environ[_k]
    if settings.java_home:
        env["JAVA_HOME"] = settings.java_home
    proc = None
    try:
        # File-backed capture is bounded by RLIMIT_FSIZE; slicing a PIPE only
        # after communicate() would still allow unbounded parent memory use.
        with tempfile.TemporaryFile(dir=cwd) as output, tempfile.TemporaryFile(dir=cwd) as errors:
            proc = subprocess.Popen(cmd,cwd=cwd,stdin=subprocess.PIPE,stdout=output,stderr=errors,
                text=True,env=env,preexec_fn=lambda: _limits(apply_address_space))
            try:
                proc.communicate(input=stdin,timeout=settings.exec_timeout_seconds)
            except subprocess.TimeoutExpired:
                try: os.killpg(proc.pid,signal.SIGKILL)
                except ProcessLookupError: pass
                proc.wait(timeout=2)
                return -1,"",f"Timed out after {settings.exec_timeout_seconds}s (possible infinite loop)"
            cap=settings.exec_max_output_bytes
            output.seek(0);errors.seek(0)
            return proc.returncode,output.read(cap).decode('utf-8',errors='replace'),errors.read(cap).decode('utf-8',errors='replace')
    except (OSError,subprocess.SubprocessError) as exc:
        raise RuntimeError("Execution infrastructure could not start or complete the process") from exc
    finally:
        if proc is not None:
                try: os.killpg(proc.pid, signal.SIGKILL)
                except (ProcessLookupError, PermissionError):
                    # Timeout handling may already have reaped the process, or
                    # a restricted host may deny signalling its process group.
                    pass



# ---------------------------------------------------------------- Tier 1

_PY_HARNESS = '''
import json, sys
sys.setrecursionlimit(20000)
{solution}

_cases = json.loads(sys.stdin.read())
_out = []
for _args in _cases:
    _out.append({fn}(*_args))
print("__RESULT__" + json.dumps(_out, default=str))
'''

_JS_HARNESS = '''
{solution}
const _chunks = [];
process.stdin.on("data", d => _chunks.push(d));
process.stdin.on("end", () => {{
  const cases = JSON.parse(_chunks.join(""));
  const out = cases.map(args => {fn}(...args));
  console.log("__RESULT__" + JSON.stringify(out));
}});
'''


def _extract_result(stdout: str):
    for line in stdout.splitlines():
        if line.startswith("__RESULT__"):
            return json.loads(line[len("__RESULT__"):])
    raise ValueError("no result marker in output")


def _run_stdio(language: str, solution: str, cases: list, expected: list, files: dict | None = None) -> LangResult:
    """HackerRank-style: the program reads a test case from stdin and prints the
    answer. Each case is run as a separate process; output is compared as
    whitespace-normalised text."""
    res = LangResult(language=language, tier=1, status="error", total_cases=len(cases))
    if len(cases) > 64:
        res.status = "unverified"
        res.detail = "stdin/stdout execution accepts at most 64 cases per submission"
        return res
    if len(solution.encode("utf-8")) > 100_000:
        res.status = "unverified"
        res.detail = "source exceeds the 100 KB execution limit"
        return res
    if not available_languages().get(language, False):
        res.status = "unverified"
        res.detail = f"{_TOOLCHAIN[language]} is unavailable in the execution environment"
        return res
    from app.services.execution_adapters import NATIVE_MULTIFILE
    helpers = {n: t for n, t in (files or {}).items() if n != ADAPTERS[language].source}
    if helpers and language not in NATIVE_MULTIFILE:
        res.status = "unverified"
        res.detail = f"{language} runs a single source file; put helpers in the solution or use notes"
        return res
    actual: list = []
    with tempfile.TemporaryDirectory() as td:
        cwd = Path(td)
        adapter = ADAPTERS[language]
        # Helper files sit beside the entry file under their own names, so the
        # native build or runtime finds them; the entry file is `adapter.source`.
        (cwd / adapter.source).write_text(solution if not files else files.get(adapter.source, solution), encoding="utf-8")
        for name, text in helpers.items():
            (cwd / name).write_text(text, encoding="utf-8")
        for name, text in SUPPORT_FILES.get(language, {}).items():
            (cwd / name).write_text(text, encoding="utf-8")
        build, cmd = stdio_commands(language, cwd, max(64, settings.exec_memory_mb // 2), list(helpers))
        if build:
            code, out, err = _run(build, cwd, apply_address_space=False)
            if code != 0:
                res.status = "failed"
                res.evidence = diagnostic_evidence(language, "compile", err or out or "compilation failed")
                res.detail = res.evidence["message"]
                return res

        for case in cases:
            stdin_text = case if isinstance(case, str) else "\n".join(str(a) for a in case)
            if len(stdin_text.encode("utf-8")) > 65_536:
                res.status = "unverified"
                res.detail = "a test input exceeds the 64 KB stdin limit"
                return res
            code, out, err = _run(
                cmd, cwd, stdin=stdin_text,
                apply_address_space=language not in NO_ADDRESS_SPACE_LIMIT,
            )
            if code != 0:
                res.status = "failed"
                res.evidence = diagnostic_evidence(language, "run", err or out or "non-zero exit")
                res.detail = res.evidence["message"]
                return res
            actual.append(out.strip())

    res.outputs = actual
    norm = lambda t: " ".join(str(t).split())
    passed = sum(1 for a, e in zip(actual, expected) if norm(a) == norm(e))
    res.passed_cases = passed
    if passed == len(cases):
        res.status = "passed"
    else:
        res.status = "failed"
        res.detail = "; ".join(
            f"case {i + 1}: got {a!r}, expected {e!r}"
            for i, (a, e) in enumerate(zip(actual, expected))
            if norm(a) != norm(e)
        )[:600]
    return res


def _run_tier1(language: str, solution: str, fn: str, cases: list, expected: list, equal=None) -> LangResult:
    equal = equal or _equal
    res = LangResult(language=language, tier=1, status="error", total_cases=len(cases))
    with tempfile.TemporaryDirectory() as td:
        cwd = Path(td)
        if language == "python":
            (cwd / "s.py").write_text(_PY_HARNESS.format(solution=solution, fn=fn))
            cmd = ["python3", "s.py"]
        else:
            (cwd / "s.js").write_text(_JS_HARNESS.format(solution=solution, fn=fn))
            cmd = ["node", f"--max-old-space-size={settings.exec_memory_mb}", "s.js"]

        code, out, err = _run(
            cmd, cwd, stdin=json.dumps(cases),
            apply_address_space=(language != "javascript"),
        )
        if code != 0:
            res.status = "failed"
            res.detail = (err or out or "non-zero exit").strip()[:600]
            return res
        try:
            actual = _extract_result(out)
        except Exception as exc:  # noqa: BLE001
            res.status = "failed"
            res.detail = f"Could not parse output: {exc}"
            return res

    res.outputs = actual
    passed = sum(1 for a, e in zip(actual, expected) if equal(a, e))
    res.passed_cases = passed
    if passed == len(cases):
        res.status = "passed"
    else:
        res.status = "failed"
        mismatches = [
            f"case {i + 1}: got {a!r}, expected {e!r}"
            for i, (a, e) in enumerate(zip(actual, expected))
            if not equal(a, e)
        ]
        res.detail = "; ".join(mismatches[:5])
    return res


def _equal(a, b) -> bool:
    from app.services.output_comparison import exact
    return exact(a, b)


# ---------------------------------------------------------------- Tier 2

_C_PRELUDE = """#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdbool.h>
#include <limits.h>
#include <stdint.h>
struct ListNode { int val; struct ListNode *next; };
struct TreeNode { int val; struct TreeNode *left; struct TreeNode *right; };
"""
_CPP_PRELUDE = """#include <bits/stdc++.h>
using namespace std;
struct ListNode { int val; ListNode *next; ListNode(int x):val(x),next(nullptr){} };
struct TreeNode { int val; TreeNode *left,*right; TreeNode(int x):val(x),left(nullptr),right(nullptr){} };
"""


def _run_tier2(language: str, solution: str) -> LangResult:
    res = LangResult(language=language, tier=2, status="unverified")
    if not available_languages().get(language):
        res.detail = f"{_TOOLCHAIN[language]} not installed — cannot verify this language"
        return res

    with tempfile.TemporaryDirectory() as td:
        cwd = Path(td)
        written, name = "", ""
        if language == "c":
            written, name = _C_PRELUDE + solution, "s.c"
            (cwd / name).write_text(written)
            cmd = ["gcc", "-fsyntax-only",
                   "-Werror=implicit-function-declaration",
                   "-Werror=implicit-int",
                   "-Werror=return-type", "s.c"]
        elif language == "cpp":
            written, name = _CPP_PRELUDE + solution, "s.cpp"
            (cwd / name).write_text(written)
            cmd = ["g++", "-std=c++17", "-fsyntax-only", "-Werror=return-type", "s.cpp"]
        elif language == "java":
            body = solution if "class " in solution else f"class Solution {{\n{solution}\n}}"
            written, name = "import java.util.*;\n" + body, "Solution.java"
            (cwd / name).write_text(written)
            cmd = [exec_harness.java_tool("javac"), "-nowarn", "-d", ".", "Solution.java"]
        else:  # rust
            body = solution if "struct Solution" in solution else f"struct Solution;\nimpl Solution {{\n{solution}\n}}\nfn main() {{}}"
            written, name = body, "s.rs"
            (cwd / name).write_text(written)
            cmd = ["rustc", "--edition", "2021", "--crate-type", "bin", "-A", "warnings", "-o", "out", "s.rs"]

        code, out, err = _run(cmd, cwd)

    if code == 0:
        res.status = "passed"
        res.detail = "compiles cleanly"
    else:
        res.status = "failed"
        res.detail = exec_harness.solution_relative((err or out).strip(), name, written, solution)[:600]
    return res


# ------------------------------------------------- Tier 1, compiled languages


def _run_compiled(language: str, solution: str, fn: str,
                  cases: list, expected: list, equal=None,
                  files: dict | None = None) -> LangResult:
    """Execute a compiled language against the test cases.

    Falls back to the compile-only check when `exec_harness` declines to
    execute — a refusal is reported at tier 2 and blocks publication. What never
    happens is a pass being claimed for code that was not run.
    """
    import contextlib

    @contextlib.contextmanager
    def _workdir():
        with tempfile.TemporaryDirectory() as td:
            yield Path(td)

    outcome = exec_harness.compile_and_run(
        language, solution, fn, cases, expected,
        workdir=_workdir, run=_run,
        memory_mb=settings.exec_memory_mb, equal=equal or _equal,
        project_files=files,
    )

    if outcome.status == "unverified":
        if language == "java" and files:
            # A standalone compile omits the helper classes and can turn an
            # unsupported test shape into a misleading missing-symbol error.
            return LangResult(language=language, tier=2, status="unverified",
                              detail=outcome.detail, total_cases=len(cases))
        # Execution was refused, so keep the signal we can still get.
        res = _run_tier2(language, solution)
        if res.status == "failed":
            # The learner's own code failed to compile. Its standalone compile
            # output is the useful diagnostic, with lines counted from their code.
            return res
        res.detail = f"not executed: {outcome.detail}"
        if res.status == "passed":
            # Compiling is not verifying. Say so plainly rather than letting
            # it read as a pass.
            res.status = "unverified"
            res.detail += " (compiles cleanly, but correctness was not checked)"
        return res

    compile_failure = outcome.candidate == "compile"
    evidence = (diagnostic_evidence(language, "compile", outcome.detail)
                if compile_failure else {})
    return LangResult(
        language=language, tier=2 if compile_failure else 1, status=outcome.status,
        detail=outcome.detail,
        passed_cases=len(cases) if outcome.status == "passed" else 0,
        total_cases=len(cases),
        outputs=outcome.outputs or [],
        evidence=evidence,
    )


# ---------------------------------------------------------------- public API


def run_suite(solutions: dict[str, str], fn_names: dict[str, str],
              cases: list, expected: list, io_mode: str = "function",
              comparison: str = "exact", files: dict | None = None) -> dict:
    """Validate every provided solution.

    solutions: {"python": "<code>", "c": "<code>", ...}
    fn_names:  {"python": "two_sum", "javascript": "twoSum", ...}
    cases:     [[arg1, arg2], ...]   expected: [value, ...]
    io_mode:   "function" (function style: call fn, compare return value) or
               "stdio" (HackerRank style: feed stdin, compare printed output)

    Returns a report dict with per-language results, cross-language
    agreement, and whether the publish gate is satisfied.
    """
    from app.services.output_comparison import compare
    equal = lambda a, b: compare(a, b, comparison)
    results: list[LangResult] = []
    if io_mode == "linked_list":
        from app.services.list_adapter import adapt, SUPPORTED
        adapted, names = {}, dict(fn_names)
        for lang, code in solutions.items():
            if lang not in SUPPORTED:
                results.append(LangResult(language=lang, tier=2, status="unverified",
                                          detail="Linked-list adapter unavailable for this language"))
                continue
            adapted[lang], names[lang] = adapt(lang, code, fn_names.get(lang, ""))
        solutions, fn_names = adapted, names

    for lang in TIER1:
        if lang in solutions:
            if io_mode == "stdio":
                results.append(_run_stdio(lang, solutions[lang], cases, expected, files))
            else:
                results.append(
                    _run_tier1(lang, solutions[lang], fn_names.get(lang, ""), cases, expected, equal)
                )

    for lang in COMPILED:
        if lang not in solutions:
            continue
        if not available_languages().get(lang):
            results.append(LangResult(
                language=lang, tier=2, status="unverified",
                detail=f"{_TOOLCHAIN[lang]} not installed — cannot verify this language",
            ))
        elif io_mode == "stdio":
            results.append(_run_stdio(lang, solutions[lang], cases, expected, files))
        else:
            results.append(_run_compiled(
                lang, solutions[lang], fn_names.get(lang, ""), cases, expected, equal, files))

    for lang in SCRIPTED:
        if lang not in solutions:
            continue
        if not available_languages().get(lang):
            results.append(LangResult(
                language=lang, tier=2, status="unverified",
                detail=f"{_TOOLCHAIN[lang]} not installed — cannot verify this language",
            ))
        elif io_mode == "stdio":
            if ADAPTERS[lang].stdio_tests:
                results.append(_run_stdio(lang, solutions[lang], cases, expected, files))
            else:
                results.append(LangResult(language=lang, tier=2, status="unverified",
                                          detail="stdin/stdout problems are not supported for this language"))
        else:
            from app.services import script_runners
            results.append(script_runners.run(lang, solutions[lang], fn_names.get(lang, ""), cases, expected, equal))

    for lang in (name for name in ADAPTERS if name not in TIER1 + COMPILED + SCRIPTED):
        if lang not in solutions:
            continue
        if io_mode == "stdio":
            results.append(_run_stdio(lang, solutions[lang], cases, expected, files))
        else:
            results.append(LangResult(language=lang, tier=2, status="unverified",
                                      detail="function-style test adapter is unavailable for this language"))

    # Cross-language agreement across Tier-1 languages that actually ran
    ran = [r for r in results if r.tier == 1 and r.status in ("passed", "failed") and r.outputs]
    agreement = True
    agreement_detail = "n/a (fewer than two executable implementations)"
    if len(ran) >= 2:
        base = ran[0]
        disagreeing = [r.language for r in ran[1:] if len(r.outputs) != len(base.outputs) or not all(equal(a,b) for a,b in zip(r.outputs,base.outputs))]
        agreement = not disagreeing
        agreement_detail = (
            "all executable implementations agree"
            if agreement
            else f"{base.language} disagrees with: {', '.join(disagreeing)}"
        )

    tier1_ran = [r for r in results if r.tier == 1]
    tier2_ran = [r for r in results if r.tier == 2]
    tier1_ok = bool(tier1_ran) and all(r.status == "passed" for r in tier1_ran)
    tier2_ok = all(r.status == "passed" and r.tier == 1 for r in tier2_ran)

    can_publish = (tier1_ok and tier2_ok and agreement and bool(cases)
                   and len(cases) == len(expected)
                   and len(results) == len(solutions)
                   and all(r.tier == 1 and r.status == "passed"
                           and r.passed_cases == r.total_cases == len(cases)
                           and len(r.outputs) == len(cases) for r in results))
    return {
        "results": [asdict(r) for r in results],
        "agreement": agreement,
        "agreement_detail": agreement_detail,
        "tier1_ok": tier1_ok,
        "tier2_ok": tier2_ok,
        "can_publish": can_publish,
        "unverified": [r.language for r in results if r.status == "unverified"],
        "toolchains": available_languages(),
    }
