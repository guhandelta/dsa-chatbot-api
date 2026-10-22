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
    (r"(?<![.\w$])fetch\s*\(|XMLHttpRequest", "block", "makes outbound HTTP requests"),
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

_STRING_AWARE_REASONS = {"writes to the filesystem", "attempts path traversal",
                         "references an absolute path", "writes to or deletes from the filesystem"}

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


# ---------------------------------------------------------------------------
# TypeScript
#
# Same intent as the JavaScript rules (a DSA solution needs no module loader
# and no host globals) but evaluated on a *stripped* view of the source so
# that comments and ordinary string text cannot cause a false strike, while
# code inside template-literal ${...} expressions is still scanned.
#
# Policy decisions (single-file exercises):
#   * ALL import / require / import() / `export ... from` / `export =` are
#     blocked, including `import type`. Nothing a solution needs lives in
#     another module.
#   * `declare module` / `declare global` are blocked (module augmentation).
#   * `constructor(...)` declarations, user functions/methods called
#     `process(...)`, object keys named `process:`, `type`, `interface`,
#     `// @ts-ignore` / `@ts-nocheck` / `/// <reference>` comments are allowed
#     (comments never execute; a reference directive only pulls in types).
#   * Property access (`x.process`, `x.require`) is allowed; only bare
#     identifiers reach host objects. `.constructor` / ['constructor'] /
#     __proto__ are blocked wherever they appear (classic Function escape).
#   * `window`/`document`/`global`/`self`-style names are only host access when
#     they are not declared locally (a sliding-window solution legitimately
#     has `const window: number[] = []`).
# ---------------------------------------------------------------------------
_TS_REGEX_PREV_KEYWORDS = {"return", "typeof", "case", "do", "else", "in", "of",
                           "instanceof", "new", "delete", "void", "throw",
                           "yield", "await"}
_TS_REGEX_PREV_CHARS = set("(,=:[!&|?{};+-*%<>~^")
_TS_IDENT = re.compile(r"[A-Za-z_$][\w$]*")


class _StripFailed(Exception):
    pass


def _ts_scan(src: str, i: int, in_expr: bool) -> tuple[str, str, int]:
    """Return (code_view, keyed_view, next_index).

    code_view: comments removed, string/template text blanked (``""``/``````),
               template ${} expressions and regex bodies kept as code.
    keyed_view: comments removed, strings kept verbatim.
    Raises _StripFailed on anything unterminated or ambiguous so the caller
    falls back to the raw text (fail closed).
    """
    n = len(src)
    code: list[str] = []
    keyed: list[str] = []
    depth = 0
    last_sig = ""
    last_word = ""
    while i < n:
        ch = src[i]
        nx = src[i + 1] if i + 1 < n else ""
        if ch == "/" and nx == "/":
            j = src.find("\n", i)
            i = n if j == -1 else j
            code.append(" "); keyed.append(" ")
            continue
        if ch == "/" and nx == "*":
            j = src.find("*/", i + 2)
            if j == -1:
                raise _StripFailed
            i = j + 2
            code.append(" "); keyed.append(" ")
            continue
        if ch in "\"'":
            j = i + 1
            while j < n and src[j] != ch:
                if src[j] == "\n":
                    raise _StripFailed
                j += 2 if src[j] == "\\" else 1
            if j >= n:
                raise _StripFailed
            code.append('""'); keyed.append(src[i:j + 1])
            i = j + 1
            last_sig = '"'
            continue
        if ch == "`":
            code.append("``"); keyed.append("`")
            j = i + 1
            while True:
                if j >= n:
                    raise _StripFailed
                c = src[j]
                if c == "\\":
                    keyed.append(src[j:j + 2]); j += 2
                elif c == "`":
                    keyed.append("`"); j += 1
                    break
                elif src.startswith("${", j):
                    c2, k2, j = _ts_scan(src, j + 2, True)
                    code.append(" ( " + c2 + " ) ")
                    keyed.append("${" + k2 + "}")
                else:
                    keyed.append(c); j += 1
            i = j
            last_sig = '"'
            continue
        if ch == "/":
            is_regex = (last_sig == "" or last_sig in _TS_REGEX_PREV_CHARS or last_sig == "}"
                        or (last_sig == "a" and last_word in _TS_REGEX_PREV_KEYWORDS))
            if last_sig == ")":
                # `if (x) /re/.test(y)` vs `(a+b)/2`: if a quote sits between this
                # slash and another one on the line we cannot tell; give up.
                rest = src[i + 1:src.find("\n", i) if src.find("\n", i) != -1 else n]
                k = rest.find("/")
                if k != -1 and re.search(r"[\"'`]", rest[:k]):
                    raise _StripFailed
            if is_regex:
                j, in_class, ok = i + 1, False, False
                while j < n and src[j] != "\n":
                    c = src[j]
                    if c == "\\":
                        j += 2
                        continue
                    if c == "[":
                        in_class = True
                    elif c == "]":
                        in_class = False
                    elif c == "/" and not in_class:
                        ok = True
                        break
                    j += 1
                if ok:
                    body = re.sub(r"[\"'`]", " ", src[i:j + 1])
                    code.append(body); keyed.append(body)
                    i = j + 1
                    last_sig = '"'
                    continue
            code.append("/"); keyed.append("/")
            i += 1
            last_sig = "/"
            continue
        if in_expr:
            if ch == "{":
                depth += 1
            elif ch == "}":
                if depth == 0:
                    return "".join(code), "".join(keyed), i + 1
                depth -= 1
        m = _TS_IDENT.match(src, i)
        if m:
            code.append(m.group()); keyed.append(m.group())
            last_sig, last_word = "a", m.group()
            i = m.end()
            continue
        code.append(ch); keyed.append(ch)
        if not ch.isspace():
            last_sig = "0" if ch.isdigit() else ch
        i += 1
    if in_expr:
        raise _StripFailed
    return "".join(code), "".join(keyed), i


def _ts_views(code: str) -> tuple[str, str]:
    try:
        c, k, _ = _ts_scan(code, 0, False)
        return c, k
    except (_StripFailed, RecursionError):
        return code, code


_TS_MEMBER = re.compile(r"(?<=[\w$)\]!])\s*\??\.\s*[A-Za-z_$][\w$]*")
_TS_PROCESS_KEY = re.compile(
    r"([{,;]\s*)(?:process|require|import|module|exports|global|window|document|Deno|Bun|eval|Worker|Reflect)"
    r"(\s*\??\s*:)(?!:)")
_TS_HARD_NAMES = re.compile(
    r"(?<![\w$])(?:require|import|module|exports|globalThis|eval|Reflect|"
    r"WebAssembly|importScripts|Worker)\b")
_TS_PROCESS = re.compile(r"(?<![\w$])process\b(?!\s*\()")
_TS_WEAK_NAMES = ("global", "window", "document", "Deno", "Bun", "self", "navigator",
                  "WebSocket", "EventSource", "SharedWorker", "WebTransport", "BroadcastChannel")
_TS_EXPORT_FROM = re.compile(r"\bexport\s*(?:\*|\{[^}]*\})\s*from\b|\bexport\s*=|\bdeclare\s+(?:module|global)\b")
_TS_FUNCTION_CTOR = re.compile(r"(?<![\w$.])Function\s*\(|\bnew\s+Function\b")
_TS_DYNAMIC = re.compile(
    r"\.\s*constructor\b|__proto__|\bconstructor\s*[:,}]"
    r"|\bgetOwnProperty(?:Descriptors?|Names|Symbols)\b|(?<![\w$.])atob\s*\("
    r"|\[\s*String\s*\.\s*fromCharCode|\[[^\[\]]*\"\"\s*\+\s*\"\"")
_TS_KEYED = re.compile(r"\[\s*['\"`]\s*(?:constructor|__proto__)\b")
_TS_ESCAPE = re.compile(r"\\(?:u\{([0-9a-fA-F]+)\}|u([0-9a-fA-F]{4})|x([0-9a-fA-F]{2}))")


def _ts_letter_escape(text: str) -> bool:
    """True if a string contains an escape that decodes to an ASCII identifier
    character (e.g. '\\x72equire'); harmless escapes like '\\u2713' are fine."""
    for m in _TS_ESCAPE.finditer(text):
        cp = int(m.group(1) or m.group(2) or m.group(3), 16)
        if cp < 128 and (chr(cp).isalnum() or chr(cp) in "_$"):
            return True
    return False


def _ts_weak_declared(code_view: str, name: str) -> bool:
    n = re.escape(name)
    return bool(re.search(rf"\b(?:const|let|var|function|class)\s+{n}\b|[(,]\s*{n}\s*[:,)=?]", code_view))


def _screen_typescript(code: str) -> ScreenResult | None:
    c, k = _ts_views(code)
    if (_TS_DYNAMIC.search(c) or _TS_FUNCTION_CTOR.search(c) or _TS_KEYED.search(k)
            or _ts_letter_escape(k) or _ts_letter_escape(c)):
        return ScreenResult("block", ["uses dynamic execution or obfuscated runtime access"],
                            ["typescript_runtime_access"])
    masked = _TS_MEMBER.sub(" .M", c)
    masked = _TS_PROCESS_KEY.sub(r"\1_key\2", masked)
    hit = (_TS_HARD_NAMES.search(masked) or _TS_PROCESS.search(masked)
           or _TS_EXPORT_FROM.search(masked))
    if not hit:
        for name in _TS_WEAK_NAMES:
            if re.search(rf"(?<![\w$]){name}\b", masked) and not _ts_weak_declared(masked, name):
                hit = True
                break
    if hit:
        return ScreenResult("block", ["accesses module loading or host runtime globals"],
                            ["typescript_runtime_access"])
    return None


# ---------------------------------------------------------------------------
# Go: allow-list on import paths. Known-dangerous or third-party packages are
# a block; any other package outside the list is a warn (no strike) because it
# is more likely a student reaching for an unusual-but-harmless stdlib package.
# ---------------------------------------------------------------------------
_GO_ALLOWED_IMPORTS = {
    "fmt", "strings", "sort", "strconv", "math", "math/bits", "math/rand", "math/big",
    "math/cmplx", "math/rand/v2", "errors", "sync", "sync/atomic", "container/heap", "container/list",
    "container/ring", "unicode", "unicode/utf8", "unicode/utf16", "bytes", "bufio",
    "slices", "maps", "cmp", "iter", "time", "context", "regexp", "io", "reflect",
    "runtime", "log", "path", "hash/fnv", "hash/maphash", "encoding/json",
    "text/tabwriter",
}
_GO_BLOCKED_IMPORTS = {
    "os", "os/exec", "os/signal", "os/user", "syscall", "unsafe", "plugin", "C",
    "embed", "io/ioutil", "io/fs", "path/filepath", "runtime/cgo", "runtime/debug",
    "debug/elf", "debug/macho", "debug/pe", "crypto/tls", "html/template",
    "text/template",
}
_GO_IMPORT = re.compile(r"(?m)(?:^|;)[ \t]*import\b\s*(?:\(([^)]*)\)|([^\n]*))")
_GO_PATH = re.compile(r"\"([^\"\n]*)\"|`([^`\n]*)`")


_GO_DIRECTIVE = re.compile(r"(?m)^[ \t]*//go:(?:linkname|embed|cgo_\w+)\b")


def _screen_go(code: str) -> ScreenResult | None:
    if _GO_DIRECTIVE.search(code):
        return ScreenResult("block", ["uses compiler directives that reach runtime internals"],
                            ["go_directive"])
    stripped = re.sub(r"/\*.*?\*/", " ", code, flags=re.S)
    stripped = re.sub(r"(?m)^[ \t]*//.*$", "", stripped)
    paths: list[str] = []
    for m in _GO_IMPORT.finditer(stripped):
        body = m.group(1) if m.group(1) is not None else m.group(2)
        body = re.sub(r"//[^\n\"`]*$", "", body, flags=re.M)
        paths += [a or b for a, b in _GO_PATH.findall(body)]
    for path in paths:
        root = path.split("/")[0]
        if ("\\" in path or path in _GO_BLOCKED_IMPORTS or root in ("net", "syscall", "unsafe", "plugin")
                or "." in root):
            return ScreenResult("block", ["imports packages that reach the network, filesystem, "
                                          "processes or native memory"], ["go_import"])
    for path in paths:
        if path not in _GO_ALLOWED_IMPORTS:
            return ScreenResult("warn", ["imports a package outside the supported set"],
                                ["go_import_unlisted"])
    return None


# ---------------------------------------------------------------------------
# Ruby: precise, call-shaped patterns on raw text (whole-line comments and
# =begin/=end blocks removed). Deliberately not exhaustive; the sandbox is
# the boundary.
# ---------------------------------------------------------------------------
_RUBY_SAFE_REQUIRES = {"set", "json", "prime", "bigdecimal", "bigdecimal/util", "date",
                       "time", "ostruct", "forwardable", "singleton", "comparable",
                       "stringio", "delegate", "pp", "benchmark", "securerandom",
                       "observer", "matrix", "rational", "complex"}
_RUBY_RULES = (
    (r"(?<![.\w:$])(?:exec|spawn|fork|syscall)\b(?=\s*[(\"'%:])|(?<![.\w:$])fork\s*(?:\{|do\b)|(?<![.\w:$])system\s+[\"'%:]",
     "spawns processes"),
    (r"\bKernel\s*(?:\.|::)\s*(?:system|exec|spawn|fork|open|syscall|`|eval|load|require\w*)\b"
     r"|\bIO\s*(?:\.|::)\s*(?:popen|read|readlines|foreach|write|sysopen|binread|new|for_fd|open|select)\b"
     r"|\bProcess\s*(?:\.|::)\s*(?:spawn|exec|fork|daemon|kill)\b"
     r"|\bOpen3\b|\bPTY\b", "spawns processes or opens files"),
    (r"%x[\[({<|!/]|^[^#'\"\n]*`|#\{[^}\n#`]*`", "runs shell commands"),
    (r"\bENV\b(?!\s+(?!(?:if|unless|and|or|do|then|rescue|while|until)\b)[A-Za-z])",
     "reads environment variables"),
    (r"\b(?:File|Dir|FileUtils|Pathname|Tempfile)\s*(?:\.|::)\s*\w+", "accesses the filesystem"),
    (r"(?<![.\w:$])open\s*\(?\s*[\"'|]|\bURI\s*\.\s*open\b|\bNet::|\b(?:TCPSocket|TCPServer|UDPSocket|"
     r"UNIXSocket|Socket|WEBrick|Resolv)\b", "opens files or network connections"),
    (r"\b(?:instance_eval|class_eval|module_eval|instance_exec|class_exec|module_exec|binding|"
     r"TOPLEVEL_BINDING|ObjectSpace|RubyVM|Fiddle|FFI|const_get|const_missing|TracePoint)\b|(?<![.\w:$])eval\b",
     "evaluates code or inspects the runtime"),
    (r"\b(?:__send__|public_send|send|method)\s*\(?\s*[:\"'](?:system|exec|spawn|fork|eval|open|"
     r"instance_eval|require\w*|load|syscall|popen|`)\b", "invokes dangerous methods indirectly"),
    (r"\b(?:__send__|public_send|send)\s*\(?\s*[\"'][\w]*[\"']\s*\+|\b(?:__send__|public_send|send)\s*\(?\s*\"[^\"\n]*#\{",
     "invokes methods by constructed name"),
    (r"(?<![.\w:$])(?:require_relative|load|autoload)\b(?=\s*[(\"'])", "loads other files"),
)
_RUBY_COMPILED = [(re.compile(p, re.M), why) for p, why in _RUBY_RULES]
_RUBY_REQUIRE = re.compile(
    r"(?:^|[;({=,|&!]|\b(?:then|do|begin|if|unless|and|or|not|else)\b)[ \t]*"
    r"require\b\s*\(?\s*([^\s)\n]*)", re.M)


def _ruby_text(code: str) -> str:
    text = re.sub(r"(?ms)^=begin\b.*?^=end\b", "", code)
    text = re.sub(r"(?m)^[ \t]*#(?!\{).*$", "", text)
    # Trailing comments, only where nothing before the `#` could be an open
    # string/regex/%-literal/heredoc that makes the `#` part of a literal.
    return re.sub(r"(?m)^([^%/?'\"`<#\n]*?[ \t])#(?!\{)[^\n]*$", r"\1", text)


def _screen_ruby(code: str) -> ScreenResult | None:
    text = _ruby_text(code)
    for pattern, why in _RUBY_COMPILED:
        if pattern.search(text):
            return ScreenResult("block", [why], ["ruby_runtime_access"])
    for m in _RUBY_REQUIRE.finditer(text):
        arg = m.group(1)
        lit = re.fullmatch(r"[\"']([\w/]+)[\"']", arg)
        if not lit or lit.group(1) not in _RUBY_SAFE_REQUIRES:
            return ScreenResult("block", ["loads modules outside the supported set"],
                                ["ruby_require"])
    return None


# ---------------------------------------------------------------------------
# C#: namespace/type-shaped patterns on raw text. System.Threading,
# System.Text, System.Numerics, System.Collections*, System.Linq, System.Math
# and plain `Environment.NewLine` / `Console` remain allowed.
# ---------------------------------------------------------------------------
_CS_RULES = (
    (r"\bSystem\s*\.\s*(?:IO|Net|Reflection|Security|Data|Management|Web|CodeDom|Configuration|"
     r"Runtime\s*\.\s*(?:InteropServices|Loader|CompilerServices\s*\.\s*Unsafe)|"
     r"Diagnostics\s*\.\s*Process)\b|\bMicrosoft\s*\.\s*(?:CodeAnalysis|Win32)\b",
     "accesses the filesystem, network, processes or reflection"),
    (r"\b(?:Process\s*\.\s*(?:Start|GetProcess\w*|GetCurrentProcess|Kill)|ProcessStartInfo)\b"
     r"|\bnew\s+Process\s*\(", "spawns processes"),
    (r"\bEnvironment\s*\.\s*(?:GetEnvironmentVariables?|SetEnvironmentVariable|Exit|FailFast|"
     r"CommandLine|GetCommandLineArgs|CurrentDirectory|GetFolderPath|UserName|MachineName|"
     r"UserDomainName|ExpandEnvironmentVariables|SpecialFolder)\b", "reads environment or host state"),
    (r"\b(?:File|Directory|Path)\s*\.\s*(?:Read|Write|Open|Delete|Copy|Move|Append|Create|Exists|"
     r"Replace|Enumerate|Get|Set)\w*|\b(?:FileStream|StreamReader|StreamWriter|FileInfo|"
     r"DirectoryInfo|BinaryReader|BinaryWriter)\b", "accesses the filesystem"),
    (r"\bnew\s+(?:Socket|TcpClient|TcpListener|UdpClient|WebClient|HttpClient|HttpWebRequest)\b",
     "opens network connections"),
    (r"\[\s*(?:DllImport|LibraryImport)\b|\bMarshal\s*\.|\bGCHandle\b|\bNativeLibrary\b"
     r"|\bUnsafe\s*\.\s*(?:As|Read|Write|AsPointer|Add)\w*",
     "calls into native memory directly"),
    (r"\\[uU][0-9a-fA-F]{4}", "uses escaped identifiers"),
    (r"\b(?:Web|HttpWeb|FtpWeb)Request\s*\.\s*Create\w*|\bDns\s*\.|\bType\s*\.\s*GetType\w*",
     "opens network connections or loads types by name"),
    (r"\bAssembly\s*\.\s*\w+|\bActivator\s*\.\s*CreateInstance\w*|\bAppDomain\b|"
     r"\.\s*(?:GetMethod|GetField|GetProperty|InvokeMember|GetConstructor)s?\s*\(",
     "uses reflection or dynamic loading"),
    (r"\bunsafe\s*\{|\b(?:public|private|internal|protected|static)\s+unsafe\b|\bunsafe\s+"
     r"(?:static|class|struct|void|fixed)\b", "uses unsafe code"),
)
_CS_COMPILED = [(re.compile(p), why) for p, why in _CS_RULES]


def _cs_scan(src: str, i: int, in_expr: bool) -> tuple[str, str, int]:
    """Return (code_view, keyed_view, next_index) for C#: comments removed and
    string/char text blanked in code_view (interpolation holes stay code);
    keyed_view keeps strings. Raises _StripFailed on anything unterminated."""
    n = len(src)
    code: list[str] = []
    keyed: list[str] = []
    depth = 0
    while i < n:
        ch = src[i]
        two = src[i:i + 2]
        if two == "//":
            j = src.find("\n", i)
            i = n if j == -1 else j
            code.append(" "); keyed.append(" ")
            continue
        if two == "/*":
            j = src.find("*/", i + 2)
            if j == -1:
                raise _StripFailed
            i = j + 2
            code.append(" "); keyed.append(" ")
            continue
        m = re.compile(r"(?:\$@|@\$|\$|@)?\"").match(src, i) if ch in "$@\"" else None
        if m and not (i > 0 and (src[i - 1].isalnum() or src[i - 1] in "_$@") and ch != '"'):
            prefix = m.group()
            interp, verbatim = "$" in prefix, "@" in prefix
            j = m.end()
            if src.startswith('""', j) and not verbatim:  # raw string literal
                q = j
                while q < n and src[q] == '"':
                    q += 1
                quotes = q - (m.end() - 1)
                end = src.find('"' * quotes, q)
                if end == -1:
                    raise _StripFailed
                body = src[q:end]
                if interp:
                    code.append(" ( " + re.sub(r"[\"]", " ", body) + " ) ")
                else:
                    code.append('""')
                keyed.append(src[i:end + quotes])
                i = end + quotes
                continue
            code.append('""'); keyed.append(prefix)
            while True:
                if j >= n or (not verbatim and src[j] == "\n"):
                    raise _StripFailed
                c = src[j]
                if c == "\\" and not verbatim:
                    keyed.append(src[j:j + 2]); j += 2
                elif c == '"':
                    if verbatim and src.startswith('""', j):
                        keyed.append('""'); j += 2
                        continue
                    keyed.append('"'); j += 1
                    break
                elif interp and c == "{":
                    if src.startswith("{{", j):
                        keyed.append("{{"); j += 2
                        continue
                    c2, k2, j = _cs_scan(src, j + 1, True)
                    code.append(" ( " + c2 + " ) ")
                    keyed.append("{" + k2 + "}")
                else:
                    keyed.append(c); j += 1
            i = j
            continue
        if ch == "'":
            j = i + 1
            while j < n and src[j] != "'":
                if src[j] == "\n":
                    raise _StripFailed
                j += 2 if src[j] == "\\" else 1
            if j >= n:
                raise _StripFailed
            code.append("''"); keyed.append(src[i:j + 1])
            i = j + 1
            continue
        if in_expr:
            if ch == "{":
                depth += 1
            elif ch == "}":
                if depth == 0:
                    return "".join(code), "".join(keyed), i + 1
                depth -= 1
        code.append(ch); keyed.append(ch)
        i += 1
    if in_expr:
        raise _StripFailed
    return "".join(code), "".join(keyed), i


def _cs_views(code: str) -> tuple[str, str]:
    try:
        c, k, _ = _cs_scan(code, 0, False)
        return c, k
    except (_StripFailed, RecursionError):
        return code, code


def _screen_csharp(code: str) -> ScreenResult | None:
    view, _ = _cs_views(code)
    for pattern, why in _CS_COMPILED:
        if pattern.search(view):
            return ScreenResult("block", [why], ["csharp_runtime_access"])
    return None


_LANG_ALIASES = {"js": "javascript", "ts": "typescript", "py": "python", "c#": "csharp",
                 "cs": "csharp", "rb": "ruby", "golang": "go", "c++": "cpp"}


def screen(code: str, language: str = "python") -> ScreenResult:
    language = str(language or "python").strip().lower()
    language = _LANG_ALIASES.get(language, language)
    if len(code.encode("utf-8")) > MAX_CODE_BYTES:
        return ScreenResult("block", ["Submission exceeds the size limit."],
                            ["size_limit"])

    if language == "javascript":
        # DSA solutions need no module loader or host globals. Block identifiers,
        # not literal module names: require('f'+'s') and loader aliases count too.
        js_rules = (
            (r"\b(?:require|import|module|global|globalThis|exports)\b|\bprocess\b(?!\s*\()",
             "accesses module loading or host runtime globals"),
            (r"\b(?:eval|Function|__proto__)\b|[.\[]\s*['\"]?constructor\b|\\(?:u|x)[0-9a-fA-F]",
             "uses dynamic execution or obfuscated runtime access"),
        )
        for pattern, reason in js_rules:
            if re.search(pattern, code):
                return ScreenResult("block", [reason], ["javascript_runtime_access"])

    lang_screen = {"typescript": _screen_typescript, "go": _screen_go,
                   "ruby": _screen_ruby, "csharp": _screen_csharp}.get(language)
    if lang_screen is not None:
        try:
            early = lang_screen(code)
        except Exception:  # fail closed: never raise to the caller
            early = ScreenResult("block", ["Submission could not be screened safely."],
                                 ["screen_error"])
        if early is not None:
            return early

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

    # Generic rules: for TypeScript/Ruby, ignore comments (and TS string text)
    # so prose cannot cause a strike; rules that inspect string contents still
    # see them.
    scan = code
    if language == "typescript":
        scan, code = _ts_views(code)
    elif language == "ruby":
        scan = code = _ruby_text(code)
    elif language == "csharp":
        scan, code = _cs_views(code)

    for pattern, severity, why in _COMPILED:
        target = code if why in _STRING_AWARE_REASONS else scan
        if pattern.search(target):
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
