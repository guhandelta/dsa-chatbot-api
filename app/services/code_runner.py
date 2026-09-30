"""Executes submitted solutions against test cases in a constrained subprocess.

SECURITY NOTE
-------------
This runs code written by teachers/admins. Locally it is confined with an
OS-level CPU/memory/file-size limit, a wall-clock timeout, a scratch working
directory, and a stripped environment (so it cannot read your .env or API
keys). That is adequate for a trusted local dev setup. It is NOT a true
sandbox: a determined author could still open sockets or exhaust the disk.
Before exposing this to untrusted users, swap `_run` for a container-per-run
executor (Docker) or an external judge (Judge0 / Piston). The rest of the
pipeline talks to this module through `run_suite`, so only this file changes.

TIERS
-----
Tier 1 (Python, JavaScript): executed against real test cases. Arguments and
expected values arrive as JSON, so dispatch is dynamic and generic.
Tier 2 (C, C++, Java, Rust): compiled / type-checked. A compile catches type
errors, bad signatures and undeclared names. Languages whose toolchain is
absent are reported as "unverified" — never as passing.
"""
from __future__ import annotations

import json
import os
import resource
import shutil
import subprocess
import tempfile
from dataclasses import asdict, dataclass, field
from pathlib import Path

from app.core.config import settings

TIER1 = ("python", "javascript")
TIER2 = ("c", "cpp", "java", "rust")

# Which executable proves a toolchain is installed
_TOOLCHAIN = {
    "python": "python3",
    "javascript": "node",
    "c": "gcc",
    "cpp": "g++",
    "java": "javac",
    "rust": "rustc",
}


def available_languages() -> dict[str, bool]:
    """Runtime detection — Java/Rust are optional on a dev machine."""
    return {lang: shutil.which(exe) is not None for lang, exe in _TOOLCHAIN.items()}


@dataclass
class LangResult:
    language: str
    tier: int
    status: str                  # "passed" | "failed" | "unverified" | "error"
    detail: str = ""
    passed_cases: int = 0
    total_cases: int = 0
    outputs: list = field(default_factory=list)   # actual outputs, for cross-language agreement


def _limits(apply_address_space: bool = True):
    """Applied inside the child process before exec.

    `apply_address_space` is False for Node: V8 *reserves* a large virtual
    address space at startup, so an RLIMIT_AS cap makes it abort immediately.
    Node's heap is bounded with --max-old-space-size instead.
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
    # compiler's. Fork bombs are contained by the wall-clock timeout and the
    # static screener instead; true per-tree process limits require cgroups
    # or a container, which is the production path documented in the module
    # docstring.
    # No core dumps (they can be large and leak memory contents)
    resource.setrlimit(resource.RLIMIT_CORE, (0, 0))
    # Detach from the parent's process group so a kill takes the whole tree
    os.setsid()


def _run(cmd: list[str], cwd: Path, stdin: str = "",
         apply_address_space: bool = True) -> tuple[int, str, str]:
    """Run a command with a stripped env, scratch cwd, and hard timeout."""
    env = {"PATH": os.environ.get("PATH", "/usr/bin:/bin"), "HOME": str(cwd), "LANG": "C.UTF-8"}
    try:
        proc = subprocess.run(
            cmd,
            cwd=cwd,
            input=stdin,
            capture_output=True,
            text=True,
            timeout=settings.exec_timeout_seconds,
            env=env,
            preexec_fn=lambda: _limits(apply_address_space),
        )
        # Cap captured output — a program printing in a loop shouldn't be
        # able to exhaust the API process's memory.
        cap = settings.exec_max_output_bytes
        return proc.returncode, proc.stdout[:cap], proc.stderr[:cap]
    except subprocess.TimeoutExpired:
        # setsid above means the child leads its own process group, so any
        # grandchildren die with it rather than being orphaned.
        return -1, "", f"Timed out after {settings.exec_timeout_seconds}s (possible infinite loop)"
    except Exception as exc:  # noqa: BLE001
        return -1, "", f"Execution error: {exc}"


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


def _run_stdio(language: str, solution: str, cases: list, expected: list) -> LangResult:
    """HackerRank-style: the program reads a test case from stdin and prints the
    answer. Each case is run as a separate process; output is compared as
    whitespace-normalised text."""
    res = LangResult(language=language, tier=1, status="error", total_cases=len(cases))
    actual: list = []
    with tempfile.TemporaryDirectory() as td:
        cwd = Path(td)
        if language == "python":
            (cwd / "s.py").write_text(solution)
            cmd = ["python3", "s.py"]
        else:
            (cwd / "s.js").write_text(solution)
            cmd = ["node", f"--max-old-space-size={settings.exec_memory_mb}", "s.js"]

        for case in cases:
            stdin_text = case if isinstance(case, str) else "\n".join(str(a) for a in case)
            code, out, err = _run(
                cmd, cwd, stdin=stdin_text,
                apply_address_space=(language != "javascript"),
            )
            if code != 0:
                res.status = "failed"
                res.detail = (err or out or "non-zero exit").strip()[:600]
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


def _run_tier1(language: str, solution: str, fn: str, cases: list, expected: list) -> LangResult:
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
    passed = sum(1 for a, e in zip(actual, expected) if _equal(a, e))
    res.passed_cases = passed
    if passed == len(cases):
        res.status = "passed"
    else:
        res.status = "failed"
        mismatches = [
            f"case {i + 1}: got {a!r}, expected {e!r}"
            for i, (a, e) in enumerate(zip(actual, expected))
            if not _equal(a, e)
        ]
        res.detail = "; ".join(mismatches[:5])
    return res


def _equal(a, b) -> bool:
    """Order-insensitive for lists of lists (e.g. 3Sum triplets)."""
    if isinstance(a, list) and isinstance(b, list):
        if a and b and all(isinstance(x, list) for x in a + b):
            return sorted(sorted(x) for x in a) == sorted(sorted(x) for x in b)
    return a == b


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
        if language == "c":
            (cwd / "s.c").write_text(_C_PRELUDE + solution)
            cmd = ["gcc", "-fsyntax-only",
                   "-Werror=implicit-function-declaration",
                   "-Werror=implicit-int",
                   "-Werror=return-type", "s.c"]
        elif language == "cpp":
            (cwd / "s.cpp").write_text(_CPP_PRELUDE + solution)
            cmd = ["g++", "-std=c++17", "-fsyntax-only", "-Werror=return-type", "s.cpp"]
        elif language == "java":
            body = solution if "class " in solution else f"class Solution {{\n{solution}\n}}"
            (cwd / "Solution.java").write_text("import java.util.*;\n" + body)
            cmd = ["javac", "-nowarn", "-d", ".", "Solution.java"]
        else:  # rust
            body = solution if "struct Solution" in solution else f"struct Solution;\nimpl Solution {{\n{solution}\n}}\nfn main() {{}}"
            (cwd / "s.rs").write_text(body)
            cmd = ["rustc", "--edition", "2021", "--crate-type", "bin", "-A", "warnings", "-o", "out", "s.rs"]

        code, out, err = _run(cmd, cwd)

    if code == 0:
        res.status = "passed"
        res.detail = "compiles cleanly"
    else:
        res.status = "failed"
        res.detail = (err or out).strip()[:600]
    return res


# ---------------------------------------------------------------- public API


def run_suite(solutions: dict[str, str], fn_names: dict[str, str],
              cases: list, expected: list, io_mode: str = "function") -> dict:
    """Validate every provided solution.

    solutions: {"python": "<code>", "c": "<code>", ...}
    fn_names:  {"python": "two_sum", "javascript": "twoSum", ...}
    cases:     [[arg1, arg2], ...]   expected: [value, ...]
    io_mode:   "function" (LeetCode style: call fn, compare return value) or
               "stdio" (HackerRank style: feed stdin, compare printed output)

    Returns a report dict with per-language results, cross-language
    agreement, and whether the publish gate is satisfied.
    """
    results: list[LangResult] = []

    for lang in TIER1:
        if lang in solutions:
            if io_mode == "stdio":
                results.append(_run_stdio(lang, solutions[lang], cases, expected))
            else:
                results.append(
                    _run_tier1(lang, solutions[lang], fn_names.get(lang, ""), cases, expected)
                )
    for lang in TIER2:
        if lang in solutions:
            results.append(_run_tier2(lang, solutions[lang]))

    # Cross-language agreement across Tier-1 languages that actually ran
    ran = [r for r in results if r.tier == 1 and r.status in ("passed", "failed") and r.outputs]
    agreement = True
    agreement_detail = "n/a (fewer than two executable implementations)"
    if len(ran) >= 2:
        base = ran[0]
        disagreeing = [r.language for r in ran[1:] if not _equal(r.outputs, base.outputs)]
        agreement = not disagreeing
        agreement_detail = (
            "all executable implementations agree"
            if agreement
            else f"{base.language} disagrees with: {', '.join(disagreeing)}"
        )

    tier1_ran = [r for r in results if r.tier == 1]
    tier2_ran = [r for r in results if r.tier == 2]
    tier1_ok = bool(tier1_ran) and all(r.status == "passed" for r in tier1_ran)
    tier2_ok = all(r.status in ("passed", "unverified") for r in tier2_ran)

    can_publish = tier1_ok and tier2_ok and agreement
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
