"""Declared execution capabilities and stdin/stdout build plans.

An adapter is a promise about the *kind* of evidence the runner can produce.
The runtime probe is separate: a language can have an adapter without its
toolchain being present in the configured sandbox image.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
import re


@dataclass(frozen=True)
class Adapter:
    language: str
    toolchain: str
    source: str
    function_tests: bool
    stdio_tests: bool
    compiled: bool
    browser_preview: bool = False
    server_preview: bool = False
    complexity_analysis: bool = False

    def view(self, installed: bool) -> dict:
        return {**asdict(self), "installed": installed,
                "function_execution": installed and self.function_tests,
                "stdio_execution": installed and self.stdio_tests,
                "debug_diagnostics": installed and (self.function_tests or self.stdio_tests)}


ADAPTERS: dict[str, Adapter] = {a.language: a for a in (
    Adapter("python", "python3", "main.py", True, True, False, complexity_analysis=True),
    # Browser preview runs client-side in a sandboxed iframe (/playground);
    # TypeScript is compiled in the execution sandbox first.
    Adapter("javascript", "node", "main.js", True, True, False, browser_preview=True, complexity_analysis=True),
    Adapter("typescript", "tsc", "main.ts", True, True, True, browser_preview=True),
    Adapter("java", "javac", "Main.java", True, True, True, complexity_analysis=True),
    Adapter("c", "gcc", "main.c", True, True, True),
    Adapter("cpp", "g++", "main.cpp", True, True, True),
    Adapter("rust", "rustc", "main.rs", True, True, True),
    Adapter("ruby", "ruby", "main.rb", True, True, False),
    Adapter("go", "go", "main.go", True, True, True),
    Adapter("csharp", "dotnet", "Main.cs", True, False, True),
    Adapter("php", "php", "main.php", True, True, False),
    Adapter("dart", "dart", "main.dart", False, True, False),
    Adapter("kotlin", "kotlinc", "Main.kt", False, True, True),
    Adapter("swift", "swiftc", "main.swift", False, True, True),
    Adapter("scala", "scalac", "Main.scala", False, True, True),
    Adapter("haskell", "ghc", "Main.hs", False, True, True),
)}


GO_BUILD = ("gc=${TMPDIR:-/tmp}/gc; cp -r /opt/gocache \"$gc\" 2>/dev/null; GOCACHE=\"$gc\" "
            "GOMAXPROCS=2 go build -p 1 -o program main.go")

# Ambient declarations so a TypeScript program can read stdin without
# @types/node; kept in a separate file so learner line numbers are unchanged.
SUPPORT_FILES = {"typescript": {"stdio.d.ts": "declare var require: any;\ndeclare var process: any;\n"}}

# Executables whose runtime reserves a large virtual address space up front,
# so RLIMIT_AS on the host backend aborts them; their memory is bounded by a
# runtime flag or by the container instead.
NO_ADDRESS_SPACE_LIMIT = frozenset({"javascript", "typescript", "java", "kotlin", "scala",
                                    "go", "haskell", "dart", "ruby", "swift"})


def stdio_commands(language: str, cwd: Path, memory_mb: int, helpers: list[str] | None = None) -> tuple[list[str] | None, list[str]]:
    """Return a build command and run command, with no shell interpolation."""
    from app.services.exec_harness import java_tool
    if language not in ADAPTERS or not ADAPTERS[language].stdio_tests:
        raise ValueError(f"No stdin/stdout execution adapter for {language}")
    plans = {
        "python": (None, ["python3", "main.py"]),
        "javascript": (None, ["node", f"--max-old-space-size={memory_mb}", "main.js"]),
        "typescript": (["tsc", "--strict", "--noEmitOnError", "--target", "es2022", "--module", "commonjs", "--skipLibCheck", "main.ts", "stdio.d.ts"], ["node", f"--max-old-space-size={memory_mb}", "main.js"]),
        "java": ([java_tool("javac"), "Main.java"], [java_tool("java"), f"-Xmx{memory_mb}m", "Main"]),
        "c": (["gcc", "-std=c11", "-O0", "-Werror=implicit-function-declaration", "main.c", "-o", "program"], ["./program"]),
        "cpp": (["g++", "-std=c++17", "-O0", "main.cpp", "-o", "program"], ["./program"]),
        "rust": (["rustc", "--edition=2021", "main.rs", "-o", "program"], ["./program"]),
        "ruby": (None, ["ruby", "main.rb"]),
        # Fixed script, no learner input: the image's prebuilt standard-library
        # cache is read-only, so it is copied to tmpfs, and Go's scheduler must
        # stay inside the container's process limit (see script_runners).
        "go": (["sh", "-c", GO_BUILD], ["./program"]),
        "php": (None, ["php", "main.php"]),
        "dart": (None, ["dart", "main.dart"]),
        "kotlin": (["kotlinc", "Main.kt", "-include-runtime", "-d", "program.jar"], [java_tool("java"), f"-Xmx{memory_mb}m", "-jar", "program.jar"]),
        "swift": (["swiftc", "main.swift", "-o", "program"], ["./program"]),
        "scala": (["scalac", "Main.scala"], ["scala", "-cp", ".", "Main"]),
        "haskell": (["ghc", "-v0", "-o", "program", "Main.hs"], ["./program"]),
    }
    build, run = plans[language]
    extra = helper_sources(language, helpers or [])
    if build and extra:
        if language in ("c", "cpp"):
            at = build.index("-o")
            build = build[:at] + extra + build[at:]
        else:
            build = build + extra
    return build, run


def catalog(installed: dict[str, bool]) -> dict[str, dict]:
    return {name: adapter.view(installed.get(name, False)) for name, adapter in ADAPTERS.items()}


def unsupported(language: str) -> dict:
    """The same profile shape for a permitted language with no adapter."""
    return {**Adapter(language, "", "", False, False, False).view(False), "toolchain": None, "source": None}


SOURCE_FILE = re.compile(r"([\w.-]+\.(?:py|js|ts|java|c|cpp|h|hpp|rs|rb|go|cs|php|dart|kt|swift|scala|hs))[:(](\d+)")
PY_FRAME = re.compile(r'File "([^"]+)", line (\d+)')


def diagnostic_evidence(language: str, phase: str, message: str) -> dict:
    """Keep observed compiler/runtime evidence concise for mentor prompts.

    `file` is the source file the location names, so a multi-file run can point
    at the helper that failed; `line` is that file's line."""
    if phase not in {"compile", "run"}:
        raise ValueError("Unknown execution phase")
    clean = re.sub(r"\x1b\[[0-9;]*m", "", message).strip()[:600]
    # Prefer a location in the learner's own file over one inside a runtime
    # or standard-library frame (a Go panic names runtime/panic.go first).
    source = ADAPTERS[language].source if language in ADAPTERS else None
    frame = PY_FRAME.findall(clean)
    if source and frame and language == "python":
        file, line = frame[-1]
        return {"language": language, "phase": phase, "message": clean or "non-zero exit",
                "file": file.rsplit("/", 1)[-1], "line": int(line)}
    # The entry file first: a Go panic names runtime/panic.go before main.go.
    own = source and (re.search(rf"\b{re.escape(source)}[:(](\d+)", clean)
                      or re.search(rf"\b{re.escape(source)}\", line (\d+)", clean))
    if own:
        return {"language": language, "phase": phase, "message": clean or "non-zero exit",
                "file": source, "line": int(own.group(1))}
    located = SOURCE_FILE.search(clean)
    if located:
        return {"language": language, "phase": phase, "message": clean or "non-zero exit",
                "file": located.group(1).rsplit("/", 1)[-1], "line": int(located.group(2))}
    line = re.search(r"(?:\bline\s+|\.(?:py|js|ts|java|c|cpp|rs|rb|go|cs|php|dart|kt|swift|scala|hs):)(\d+)\b", clean, re.I)
    return {"language": language, "phase": phase, "message": clean or "non-zero exit",
            "file": source if line else None, "line": int(line.group(1)) if line else None}


# Languages whose stdin/stdout runs can build several files natively: the build
# or the runtime finds helper files by their real names.
NATIVE_MULTIFILE = frozenset({"python", "javascript", "typescript", "c", "cpp", "rust", "ruby", "java"})
_HELPER_SOURCE = {"c": ".c", "cpp": ".cpp", "java": ".java", "typescript": ".ts"}


def helper_sources(language: str, helpers: list[str]) -> list[str]:
    """Helper source files that the language's build must compile explicitly.
    Languages that import or include helpers at run time need none."""
    ext = _HELPER_SOURCE.get(language)
    return [h for h in helpers if ext and h.endswith(ext)]
