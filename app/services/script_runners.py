"""Execution of Ruby, TypeScript, Go and C# solutions against test cases.

Ruby and TypeScript are handed the cases as data (Ruby reads cases.json,
TypeScript has them embedded as a literal because the sandbox image carries no
Node type declarations). Go and C# are statically typed, so, like the other
compiled languages, the cases are emitted as native literals from the types
inferred from the test data (`exec_harness.infer_types`) and only the answers
are recorded. Anything the type inference cannot express is reported as
"unverified", never as a pass.

Results never travel on stdout, where a solution could print a forged line or
flood the 64 KB output cap ahead of the real answers. The harness writes them,
once, after the solution has run, to a file whose name carries a per-run random
token. A submission would have to read the harness source to forge it.

Every command goes through `code_runner._run`, so the container sandbox
(no network, read-only root, 8 s wall clock) applies exactly as it does for
the other languages. The sandbox image must contain the toolchains; see
sandbox/Dockerfile. Go depends on a pre-built standard-library cache
(GOCACHE) baked into the image, and C# is compiled with Roslyn directly, so a
cold build fits inside the wall clock.
"""
from __future__ import annotations

import json
import re
import secrets
import tempfile
from pathlib import Path

from app.services import exec_harness
from app.services.exec_harness import TypeSig

SCRIPTED = ("ruby", "typescript", "go", "csharp")

# How to ask each toolchain whether it exists; `go --version` is not a command
# and `dotnet --version` initialises the SDK, which needs a writable home.
PROBE_ARGS = {"go": ["version"], "csharp": ["--list-runtimes"]}

_RUBY_HARNESS = '''{solution}

require "json"
_cases = JSON.parse(File.read("cases.json"))
_out = _cases.map {{ |_args| {fn}(*_args) }}
File.write("{result}", JSON.generate(_out))
'''

_TS_HARNESS = '''{solution}

declare const require: (id: string) => {{ writeFileSync(path: string, data: string): void }};
const __cases: unknown[][] = {cases};
require("fs").writeFileSync("{result}", JSON.stringify(__cases.map((a) => ({fn} as (...x: any[]) => unknown)(...a))));
'''

_GO_MAIN = '''package main

import (
\t"encoding/json"
\t"os"
\t"strings"
)

var _dsaResults []string

func _dsaEmit(v any) {{
\tout, _ := json.Marshal(v)
\tif string(out) == "null" {{
\t\tout = []byte("[]")
\t}}
\t_dsaResults = append(_dsaResults, string(out))
}}

func main() {{
{body}
\tos.WriteFile("{result}", []byte("["+strings.Join(_dsaResults, ",")+"]"), 0o644)
}}
'''

_CS_USINGS = "using System;\nusing System.Collections.Generic;\nusing System.Linq;\nusing System.Text;\n"

_CS_MAIN = '''public static class Harness {{
    public static void Main() {{
        var results = new List<string>();
{body}
        System.IO.File.WriteAllText("{result}", "[" + string.Join(",", results) + "]");
    }}
}}
'''

# DOTNET_EnableWriteXorExecute=0: the runtime otherwise maps a large shared-memory
# file for W^X, which the sandbox's 16 MB file-size limit kills (SIGXFSZ).
# Roslyn straight from the SDK: `dotnet build` needs a writable NuGet home and
# takes ~10 s. This compiles in about a second and needs nothing but the SDK
# and the targeting pack that ship with it.
_CS_BUILD = (
    'for root in /usr/share/dotnet /usr/local/share/dotnet /opt/homebrew/opt/dotnet/libexec; do '
    '[ -d "$root/sdk" ] && break; done; '
    'csc=$(ls "$root"/sdk/*/Roslyn/bincore/csc.dll | head -n 1); '
    'refs=""; for f in "$root"/packs/Microsoft.NETCore.App.Ref/*/ref/net*/*.dll; do refs="$refs -r:$f"; done; '
    'exec env DOTNET_EnableWriteXorExecute=0 dotnet "$csc" -nologo -target:exe -out:m.dll -nullable:enable $refs Solution.cs Harness.cs'
)
_CS_RUNTIMECONFIG = json.dumps({"runtimeOptions": {"tfm": "net8.0", "framework": {
    "name": "Microsoft.NETCore.App", "version": "8.0.0"}}})

_GO_CANDIDATES = ("int", "int64")  # the int64 candidate is only ever tried for scalar signatures; see _run_typed
_CS_CANDIDATES = ("wide", "narrow")


# ------------------------------------------------------------------- typed literals

def _go_type(t: str, width: str) -> str:
    base = {"int": width, "bool": "bool", "string": "string", "double": "float64"}
    elem = t.replace("[]", "")
    if t.endswith("[][]") or elem not in base:
        raise ValueError(t)
    return ("[]" if t.endswith("[]") else "") + base[elem]


def _go_literal(value, t: str, width: str) -> str:
    if t.endswith("[]"):
        elem = t[:-2]
        items = ", ".join(_go_literal(v, elem, width) for v in value)
        return f"{_go_type(t, width)}{{{items}}}"
    if t == "string":
        return json.dumps(str(value), ensure_ascii=False)
    if t == "bool":
        return "true" if value else "false"
    if t == "double":
        return repr(float(value))
    return str(int(value))


def render_go(solution: str, fn: str, cases: list, sig: TypeSig, width: str, result: str) -> dict[str, str]:
    body = []
    for case in cases:
        args = ", ".join(_go_literal(v, t, width) for v, t in zip(case, sig.args))
        body.append(f"\t_dsaEmit({fn}({args}))")
    return {
        "go.mod": "module m\n\ngo 1.21\n",
        "solution.go": "package main\n\n" + solution + "\n",
        "main.go": _GO_MAIN.format(result=result, body="\n".join(body)),
    }


def _cs_type(t: str, width: str) -> str:
    base = {"int": "long" if width == "wide" else "int", "bool": "bool", "string": "string", "double": "double"}
    elem = t.replace("[]", "")
    if t.endswith("[][]") or elem not in base:
        raise ValueError(t)
    return base[elem] + ("[]" if t.endswith("[]") else "")


def _cs_literal(value, t: str, width: str) -> str:
    if t.endswith("[]"):
        elem = t[:-2]
        items = ", ".join(_cs_literal(v, elem, width) for v in value)
        return f"new {_cs_type(t, width)} {{ {items} }}"
    if t == "string":
        return json.dumps(str(value), ensure_ascii=False)
    if t == "bool":
        return "true" if value else "false"
    if t == "double":
        return repr(float(value))
    return f"{int(value)}L" if width == "wide" else str(int(value))


def render_csharp(solution: str, fn: str, cases: list, sig: TypeSig, width: str, result: str) -> dict[str, str]:
    body = []
    for case in cases:
        args = ", ".join(_cs_literal(v, t, width) for v, t in zip(case, sig.args))
        body.append(f"        results.Add(System.Text.Json.JsonSerializer.Serialize(Solution.{fn}({args})));")
    code = solution if re.search(r"\bclass\s+Solution\b", solution) else (
        "public static class Solution {\n" + solution + "\n}\n")
    return {
        "Solution.cs": _CS_USINGS + code + "\n",
        "Harness.cs": _CS_USINGS + _CS_MAIN.format(body="\n".join(body), result=result),
        "m.runtimeconfig.json": _CS_RUNTIMECONFIG,
    }


# ----------------------------------------------------------------------- execution

_IDENTIFIER = re.compile(r"[A-Za-z_][A-Za-z0-9_]*")


def _read_results(cwd: Path, result: str, count: int):
    try:
        data = json.loads((cwd / result).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None
    return data if isinstance(data, list) and len(data) == count else None


def _score(language: str, actual: list, expected: list, equal):
    from app.services.code_runner import LangResult
    res = LangResult(language=language, tier=1, status="failed", total_cases=len(expected), outputs=actual)
    res.passed_cases = sum(1 for a, e in zip(actual, expected) if equal(a, e))
    if res.passed_cases == len(expected):
        res.status = "passed"
    else:
        res.detail = "; ".join(f"case {i + 1}: got {a!r}, expected {e!r}"
                               for i, (a, e) in enumerate(zip(actual, expected))
                               if not equal(a, e))[:600]
    return res


def _fail(language: str, total: int, detail: str):
    from app.services.code_runner import LangResult
    return LangResult(language=language, tier=1, status="failed", total_cases=total,
                      detail=(detail or "non-zero exit").strip()[:600])


def _unverified(language: str, total: int, detail: str):
    from app.services.code_runner import LangResult
    return LangResult(language=language, tier=2, status="unverified", total_cases=total, detail=detail)


def _no_results(language: str, total: int):
    return _fail(language, total, "no results were produced — the program ended before every case ran")


def _run_ruby(solution, fn, cases, expected, equal, result):
    from app.services.code_runner import _run
    with tempfile.TemporaryDirectory() as td:
        cwd = Path(td)
        (cwd / "cases.json").write_text(json.dumps(cases))
        (cwd / "s.rb").write_text(_RUBY_HARNESS.format(solution=solution, fn=fn, result=result))
        code, out, err = _run(["ruby", "s.rb"], cwd, apply_address_space=False)
        actual = _read_results(cwd, result, len(cases)) if code == 0 else None
    if code != 0:
        return _fail("ruby", len(cases), err or out)
    return _score("ruby", actual, expected, equal) if actual is not None else _no_results("ruby", len(cases))


def _run_typescript(solution, fn, cases, expected, equal, result):
    from app.services.code_runner import _run
    with tempfile.TemporaryDirectory() as td:
        cwd = Path(td)
        (cwd / "s.ts").write_text(_TS_HARNESS.format(solution=solution, fn=fn, result=result,
                                                     cases=json.dumps(cases)))
        code, out, err = _run(["tsc", "--strict", "--noEmitOnError", "--target", "es2022", "--module", "commonjs",
                               "--lib", "es2022", "--skipLibCheck", "s.ts"], cwd, apply_address_space=False)
        if code != 0:
            return _fail("typescript", len(cases), out or err)
        code, out, err = _run(["node", "s.js"], cwd, apply_address_space=False)
        actual = _read_results(cwd, result, len(cases)) if code == 0 else None
    if code != 0:
        return _fail("typescript", len(cases), err or out)
    return _score("typescript", actual, expected, equal) if actual is not None else _no_results("typescript", len(cases))


def _run_typed(language, solution, fn, cases, expected, equal, result):
    from app.services.code_runner import _run
    sig = exec_harness.infer_types(cases, expected)
    # Nested results (int[][]) are supported; nested arguments are not.
    if sig is None or any(t.endswith("[][]") for t in sig.args):
        return _unverified(language, len(cases), "test-case shapes are not expressible as a typed "
                           "signature — execution skipped, nothing claimed")
    render, candidates = (render_go, _GO_CANDIDATES) if language == "go" else (render_csharp, _CS_CANDIDATES)
    # Both integer widths are tried for every signature; the first that compiles wins.
    errors: list[str] = []
    for width in candidates:
        with tempfile.TemporaryDirectory() as td:
            cwd = Path(td)
            for name, text in render(solution, fn, cases, sig, width, result).items():
                (cwd / name).write_text(text, encoding="utf-8")
            if language == "go":
                # The baked standard-library cache is read-only, and Go's cache trimming writes
                # to it and fails. Copy it into the run's tmpfs and build from that copy.
                build = ["sh", "-c", "cp -r /opt/gocache /tmp/gc 2>/dev/null; GOCACHE=/tmp/gc "
                                     "GOMAXPROCS=2 go build -p 1 -o m ."]
                run_cmd = ["./m"]
            else:
                build = ["sh", "-c", _CS_BUILD]
                run_cmd = ["env", "DOTNET_EnableWriteXorExecute=0", "dotnet", "m.dll"]
            code, out, err = _run(build, cwd, apply_address_space=False)
            if code != 0:
                errors.append(f"[{width}] {(err or out).strip()[:300]}")
                continue
            code, out, err = _run(run_cmd, cwd, apply_address_space=False)
            actual = _read_results(cwd, result, len(cases)) if code == 0 else None
        if code != 0:
            return _fail(language, len(cases), f"crashed during execution: {(err or out).strip()[:400]}")
        return _score(language, actual, expected, equal) if actual is not None else _no_results(language, len(cases))
    return _fail(language, len(cases), "did not compile: " + " | ".join(errors))


def run(language: str, solution: str, fn: str, cases: list, expected: list, equal):
    """One LangResult for a scripted language: tier 1 when it ran, tier 2 when refused."""
    if not _IDENTIFIER.fullmatch(fn or ""):
        return _fail(language, len(cases), "the entry point is not a valid identifier")
    result = f"r{secrets.token_hex(8)}.json"
    if language == "ruby":
        return _run_ruby(solution, fn, cases, expected, equal, result)
    if language == "typescript":
        return _run_typescript(solution, fn, cases, expected, equal, result)
    return _run_typed(language, solution, fn, cases, expected, equal, result)
