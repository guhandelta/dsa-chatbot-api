"""Static screening of submitted code, run BEFORE execution.

This is defence in depth, not the primary control. The sandbox is the real
boundary; a static screener can always be evaded by sufficiently obfuscated
code. Its jobs are narrower and still worthwhile:

  1. Block the obvious attack attempts cheaply, before spending a process.
  2. Produce an auditable signal ("this submission tried to open a socket")
     that a runtime failure alone would not give us.
  3. Distinguish DELIBERATE abuse from a beginner mistake, so the strike
     system can respond proportionately.

Severity drives the response:
  block   — refuse to run, record a strike (clear exfiltration/destruction)
  warn    — refuse to run, no strike (suspicious but plausibly innocent)
  allow   — proceed to the sandbox

Never treat an `allow` as "this code is safe". It means "nothing obvious was
found"; the sandbox still assumes the code is hostile.
"""
import re
from dataclasses import dataclass

# (pattern, severity, human-readable reason)
# Patterns are intentionally broad — false positives here cost a student one
# retry, while a miss costs a sandbox escape attempt.
_RULES: list[tuple[str, str, str]] = [
    # --- network egress: the main exfiltration path -----------------------
    (r"\bimport\s+socket\b|\bfrom\s+socket\b", "block", "opens raw network sockets"),
    (r"\brequire\s*\(\s*['\"](net|http|https|dgram|tls)['\"]\s*\)", "block",
     "opens network connections"),
    (r"\bimport\s+(requests|urllib|httpx|aiohttp)\b|\bfrom\s+(urllib|requests|httpx)\b",
     "block", "makes outbound HTTP requests"),
    (r"\bfetch\s*\(|XMLHttpRequest", "block", "makes outbound HTTP requests"),
    (r"#include\s*<\s*(sys/socket|netinet/in|arpa/inet)\.h\s*>", "block",
     "opens raw network sockets"),
    (r"\bstd::net\b|\bTcpStream\b|\bUdpSocket\b", "block", "opens network connections"),
    (r"\bjava\.net\.|\bURLConnection\b|\bHttpClient\b", "block",
     "opens network connections"),

    # --- process execution -----------------------------------------------
    (r"\bimport\s+subprocess\b|\bfrom\s+subprocess\b", "block", "spawns subprocesses"),
    (r"\bos\.(system|popen|exec[lv]|spawn|fork)\b", "block", "spawns processes"),
    (r"\brequire\s*\(\s*['\"]child_process['\"]\s*\)", "block", "spawns subprocesses"),
    (r"\b(system|popen|execve|fork)\s*\(", "block", "spawns processes"),
    (r"\bRuntime\.getRuntime\(\)|\bProcessBuilder\b", "block", "spawns processes"),
    (r"\bstd::process::Command\b", "block", "spawns processes"),

    # --- credential / environment access ---------------------------------
    (r"\bos\.environ\b|\bos\.getenv\b", "block", "reads environment variables"),
    (r"\bprocess\.env\b", "block", "reads environment variables"),
    (r"\bSystem\.getenv\b", "block", "reads environment variables"),
    (r"\bstd::env::var|\benv!\s*\(", "block", "reads environment variables"),
    (r"\bgetenv\s*\(", "block", "reads environment variables"),

    # --- filesystem writes / traversal ------------------------------------
    (r"\bopen\s*\([^)]*['\"][wax]\+?['\"]", "block", "writes to the filesystem"),
    (r"\bshutil\.(rmtree|move|copy)\b|\bos\.(remove|unlink|rmdir|rename)\b",
     "block", "deletes or moves files"),
    (r"\brequire\s*\(\s*['\"]fs['\"]\s*\)\s*\.\s*(write|unlink|rm)", "block",
     "writes to or deletes from the filesystem"),
    (r"\.\./\.\./|/etc/passwd|/proc/self", "block", "attempts path traversal"),
    (r"\bPath\s*\(\s*['\"]\s*/", "warn", "references an absolute path"),

    # --- dynamic execution ------------------------------------------------
    (r"\b__import__\s*\(", "block", "dynamically imports modules"),
    (r"\beval\s*\(|\bexec\s*\(", "warn", "evaluates code at runtime"),
    (r"\bcompile\s*\(", "warn", "compiles code at runtime"),
    (r"\bFunction\s*\(\s*['\"]", "warn", "constructs functions from strings"),
    (r"\bpickle\b|\bmarshal\b", "block", "deserialises arbitrary objects"),

    # --- introspection used for sandbox escape ---------------------------
    (r"__subclasses__|__globals__|__builtins__|__bases__|__mro__", "block",
     "uses introspection associated with sandbox escapes"),
    (r"\bctypes\b|\bcffi\b", "block", "calls into native memory directly"),
    (r"\bgc\.get_objects\b", "block", "inspects the object graph"),

    # --- resource exhaustion ---------------------------------------------
    (r"while\s*\(?\s*(True|true|1)\s*\)?\s*:?\s*(\n|\{)?\s*(pass|;|\}|$)",
     "warn", "contains a loop with no exit condition"),
    (r"\bfork\s*\(\s*\)\s*;?\s*.*\bfork\s*\(", "block", "resembles a fork bomb"),
    (r"\[\s*0\s*\]\s*\*\s*\(?\s*10\s*\*\*\s*([9-9]|\d{2,})", "warn",
     "allocates an extreme amount of memory"),

    # --- threading / timers (can outlive the measured run) ----------------
    (r"\bimport\s+threading\b|\bimport\s+multiprocessing\b", "warn",
     "spawns threads or processes"),
    (r"\bsetInterval\s*\(|\bsetTimeout\s*\(", "warn", "schedules deferred work"),
]

_COMPILED = [(re.compile(p, re.IGNORECASE | re.MULTILINE), sev, why)
             for p, sev, why in _RULES]

# Submissions above this size are refused outright — nothing legitimate in a
# DSA exercise needs it, and huge inputs are a cheap DoS on the LLM stage.
MAX_CODE_BYTES = 20_000


@dataclass
class ScreenResult:
    verdict: str                 # "allow" | "warn" | "block"
    reasons: list[str]
    matched_rules: list[str]     # for the audit log

    @property
    def allowed(self) -> bool:
        return self.verdict == "allow"

    @property
    def is_violation(self) -> bool:
        """Only a hard block counts toward a strike."""
        return self.verdict == "block"


def screen(code: str, language: str = "python") -> ScreenResult:
    if len(code.encode("utf-8")) > MAX_CODE_BYTES:
        return ScreenResult("block", ["Submission exceeds the size limit."],
                            ["size_limit"])

    if language == "python":
        import ast
        import io
        import tokenize
        # Comments are not executed and must not cause strikes.
        try:
            code = tokenize.untokenize(t for t in tokenize.generate_tokens(io.StringIO(code).readline) if t.type != tokenize.COMMENT)
        except (tokenize.TokenError, IndentationError):
            pass
        try:
            tree = ast.parse(code)
            aliases = {}
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for name in node.names: aliases[name.asname or name.name.split('.')[0]] = name.name
                elif isinstance(node, ast.ImportFrom):
                    for name in node.names: aliases[name.asname or name.name] = (node.module or '') + '.' + name.name
            def call_name(node):
                if isinstance(node, ast.Name): return aliases.get(node.id, node.id)
                if isinstance(node, ast.Attribute): return call_name(node.value) + '.' + node.attr
                if isinstance(node, ast.Call): return call_name(node.func)
                return ''
            prohibited = ('os.system','os.popen','os.fork','os.exec','os.spawn','os.environ','os.getenv',
                          'subprocess.','socket.','requests.','urllib.','httpx.','aiohttp.','ctypes.','cffi.',
                          'pathlib.Path.read_','pathlib.Path.write_')
            for node in ast.walk(tree):
                name = call_name(node.func) if isinstance(node, ast.Call) else call_name(node) if isinstance(node, ast.Attribute) else ''
                if name == 'open' or any(name.startswith(p) for p in prohibited):
                    return ScreenResult('block', ['uses prohibited filesystem, process, environment, or network operations'], ['python_ast'])
        except SyntaxError:
            pass  # Syntax errors belong to evaluation, not the strike policy.

    reasons: list[str] = []
    matched: list[str] = []
    worst = "allow"

    for pattern, severity, why in _COMPILED:
        if pattern.search(code):
            if why not in reasons:
                reasons.append(why)
                matched.append(pattern.pattern[:60])
            if severity == "block":
                worst = "block"
            elif severity == "warn" and worst != "block":
                worst = "warn"

    return ScreenResult(worst, reasons, matched)


def explain(result: ScreenResult) -> str:
    """Student-facing message. Deliberately does NOT reveal which regex fired
    or how to evade it — just what category of thing was detected."""
    if result.allowed:
        return ""
    joined = "; ".join(result.reasons)
    if result.verdict == "block":
        return (
            f"This submission was not run because it {joined}. "
            "Solutions should only compute and return an answer — no network, "
            "filesystem, process, or environment access. If this was "
            "unintentional, remove that code and resubmit."
        )
    return (
        f"This submission was not run because it {joined}. "
        "That is usually a mistake in a DSA solution — please simplify and "
        "resubmit."
    )
