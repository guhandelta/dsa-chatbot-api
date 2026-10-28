"""Function-call graders for Dart, Kotlin, Swift, Scala, and Haskell.

The harness is generated from JSON fixture types and writes answers to a
randomly named file. Unsupported argument shapes are refused as unverified;
these adapters deliberately support scalar values and one-dimensional arrays
for arguments, plus two-dimensional arrays for returned values.
"""
from __future__ import annotations

import json
import re
import secrets
import tempfile
from pathlib import Path

from app.services import exec_harness


def _string_literal(value: str, language: str) -> str:
    if language != "swift":
        return json.dumps(value, ensure_ascii=False)
    escaped = []
    for char in value:
        code = ord(char)
        escaped.append({"\\": "\\\\", '"': '\\"', "\n": "\\n", "\r": "\\r",
                        "\t": "\\t", "\0": "\\0"}.get(char,
                        f"\\u{{{code:x}}}" if code < 0x20 else char))
    return '"' + "".join(escaped) + '"'


def _is_solution_class(language: str, source: str) -> str | None:
    if language == "scala" and re.search(r"\bobject\s+Solution\b", source):
        return "object"
    if re.search(r"\bclass\s+Solution\b", source):
        return "class"
    return None


def _call(language: str, source: str, fn: str, args: list[str]) -> str:
    if language == "haskell":
        return fn + " " + " ".join(f"({arg})" for arg in args)
    target = fn
    kind = _is_solution_class(language, source)
    if kind == "object":
        target = f"Solution.{fn}"
    elif kind == "class":
        target = {"dart": f"Solution().{fn}", "kotlin": f"Solution().{fn}", "swift": f"Solution().{fn}",
                  "scala": f"new Solution().{fn}"}[language]
    return f"{target}({', '.join(args)})"


def _dart_scalar(value, kind: str) -> str:
    if kind == "string":
        return _string_literal(value, "dart")
    if kind == "bool":
        return "true" if value else "false"
    if kind == "double":
        return repr(float(value))
    return str(int(value))


def _dart_value(value, kind: str) -> str:
    if kind.endswith("[]"):
        elem = kind[:-2]
        if kind.endswith("[][]"):
            elem = kind[:-4]
            return "<List<" + {"int": "int", "string": "String"}[elem] + ">>[" + ", ".join(
                _dart_value(row, elem + "[]") for row in value) + "]"
        name = {"int": "int", "double": "double", "bool": "bool", "string": "String"}[elem]
        return f"<{name}>[" + ", ".join(_dart_scalar(v, elem) for v in value) + "]"
    return _dart_scalar(value, kind)


def _run_dart(solution, fn, cases, expected, equal, result):
    from app.services.code_runner import _run
    from app.services.script_runners import _fail, _no_results, _read_results, _score, _unverified
    sig = exec_harness.infer_types(cases, expected)
    if sig is None or any(kind.endswith("[][]") for kind in sig.args):
        return _unverified("dart", len(cases), "Dart grader accepts scalar and one-dimensional array arguments")
    calls = [_call("dart", solution, fn, [_dart_value(v, t) for v, t in zip(case, sig.args)]) for case in cases]
    source = f'''import 'dart:convert';
import 'dart:io';
{solution}
void main() {{
  final results = <dynamic>[];
{chr(10).join('  results.add(' + call + ');' for call in calls)}
  File({json.dumps(result)}).writeAsStringSync(jsonEncode(results));
}}
'''
    with tempfile.TemporaryDirectory() as td:
        cwd = Path(td)
        (cwd / "main.dart").write_text(source, encoding="utf-8")
        code, out, err = _run(["dart", "main.dart"], cwd, apply_address_space=False)
        actual = _read_results(cwd, result, len(cases)) if code == 0 else None
    if code != 0:
        return _fail("dart", len(cases), err or out)
    return _score("dart", actual, expected, equal) if actual is not None else _no_results("dart", len(cases))


def _kotlin_type(kind: str, width: str) -> str:
    scalar = {"int": "Long" if width == "long" else "Int", "double": "Double",
              "bool": "Boolean", "string": "String"}
    if kind.endswith("[][]"):
        return f"Array<{_kotlin_type(kind[:-2], width)}>"
    if kind.endswith("[]"):
        return {"int": "LongArray" if width == "long" else "IntArray",
                "double": "DoubleArray", "bool": "BooleanArray",
                "string": "Array<String>"}[kind[:-2]]
    return scalar[kind]


def _kotlin_value(value, kind: str, width: str) -> str:
    if kind.endswith("[][]"):
        row_type = _kotlin_type(kind[:-2], width)
        if not value:
            return f"emptyArray<{row_type}>()"
        return "arrayOf(" + ", ".join(_kotlin_value(row, kind[:-2], width) for row in value) + ")"
    if kind.endswith("[]"):
        elem = kind[:-2]
        method = {"int": "longArrayOf" if width == "long" else "intArrayOf",
                  "double": "doubleArrayOf", "bool": "booleanArrayOf", "string": "arrayOf"}[elem]
        if elem == "string":
            return "arrayOf<String>(" + ", ".join(_kotlin_value(v, elem, width) for v in value) + ")"
        return method + "(" + ", ".join(_kotlin_value(v, elem, width) for v in value) + ")"
    if kind == "string":
        return _string_literal(value, "kotlin")
    if kind == "bool":
        return "true" if value else "false"
    if kind == "double":
        return repr(float(value))
    return f"{int(value)}L" if width == "long" else str(int(value))


_KOTLIN_JSON = r'''private fun _dsaQuote(s: String): String = buildString {
    append('"')
    for (c in s) when (c) {
        '"' -> append("\\\""); '\\' -> append("\\\\"); '\n' -> append("\\n")
        '\r' -> append("\\r"); '\t' -> append("\\t")
        else -> if (c.code < 32) append("\\u%04x".format(c.code)) else append(c)
    }
    append('"')
}
private fun _dsaJson(v: Any?): String = when (v) {
    null -> "null"
    is String -> _dsaQuote(v)
    is Boolean -> v.toString()
    is Byte, is Short, is Int, is Long -> v.toString()
    is Float, is Double -> v.toString().also { require(v.toString() !in setOf("NaN", "Infinity", "-Infinity")) }
    is IntArray -> v.joinToString(",", "[", "]") { _dsaJson(it) }
    is LongArray -> v.joinToString(",", "[", "]") { _dsaJson(it) }
    is DoubleArray -> v.joinToString(",", "[", "]") { _dsaJson(it) }
    is BooleanArray -> v.joinToString(",", "[", "]") { _dsaJson(it) }
    is Array<*> -> v.joinToString(",", "[", "]") { _dsaJson(it) }
    is Iterable<*> -> v.joinToString(",", "[", "]") { _dsaJson(it) }
    else -> error("unsupported function result type: ${v::class}")
}
'''


def _run_kotlin(solution, fn, cases, expected, equal, result):
    from app.services.code_runner import _run
    from app.services.script_runners import _fail, _no_results, _read_results, _score, _unverified
    sig = exec_harness.infer_types(cases, expected)
    if sig is None or any(kind.endswith("[][]") for kind in sig.args):
        return _unverified("kotlin", len(cases), "Kotlin grader accepts scalar and one-dimensional array arguments")
    kind = _is_solution_class("kotlin", solution)
    entry = "Solution" if kind else ""
    for width in ("int", "long"):
        calls = [_call("kotlin", solution, fn, [_kotlin_value(v, t, width) for v, t in zip(case, sig.args)])
                 for case in cases]
        source = f'''{solution}
{_KOTLIN_JSON}
fun main() {{
    val results = mutableListOf<Any?>()
{chr(10).join('    results.add(' + call + ')' for call in calls)}
    java.io.File({json.dumps(result)}).writeText(results.joinToString(",", "[", "]") {{ _dsaJson(it) }})
}}
'''
        with tempfile.TemporaryDirectory() as td:
            cwd = Path(td)
            (cwd / "Main.kt").write_text(source, encoding="utf-8")
            code, out, err = _run(["kotlinc", "Main.kt", "-include-runtime", "-d", "program.jar"],
                                  cwd, apply_address_space=False)
            if code != 0:
                compile_error = err or out
                continue
            code, out, err = _run(["java", "-Xmx512m", "-jar", "program.jar"], cwd,
                                  apply_address_space=False)
            actual = _read_results(cwd, result, len(cases)) if code == 0 else None
        if code != 0:
            return _fail("kotlin", len(cases), err or out)
        return _score("kotlin", actual, expected, equal) if actual is not None else _no_results("kotlin", len(cases))
    return _fail("kotlin", len(cases), (compile_error or "did not compile")[:600])


def _swift_type(kind: str, width: str) -> str:
    scalar = {"int": "Int64" if width == "wide" else "Int", "double": "Double",
              "bool": "Bool", "string": "String"}
    return f"[{_swift_type(kind[:-2], width)}]" if kind.endswith("[]") else scalar[kind]


def _swift_value(value, kind: str, width: str) -> str:
    if kind.endswith("[]"):
        return "[" + ", ".join(_swift_value(v, kind[:-2], width) for v in value) + "]"
    if kind == "string":
        return _string_literal(value, "swift")
    if kind == "bool":
        return "true" if value else "false"
    if kind == "double":
        return repr(float(value))
    return f"Int64({int(value)})" if width == "wide" else str(int(value))


def _run_swift(solution, fn, cases, expected, equal, result):
    from app.services.code_runner import _run
    from app.services.script_runners import _fail, _no_results, _read_results, _score, _unverified
    sig = exec_harness.infer_types(cases, expected)
    if sig is None or any(kind.endswith("[][]") for kind in sig.args):
        return _unverified("swift", len(cases), "Swift grader accepts scalar and one-dimensional array arguments")
    for width in ("wide", "native"):
        calls = [_call("swift", solution, fn, [_swift_value(v, t, width) for v, t in zip(case, sig.args)])
                 for case in cases]
        source = f'''import Foundation
{solution}
let results: [Any] = [
{chr(10).join('    ' + call + ',' for call in calls)}
]
let data = try JSONSerialization.data(withJSONObject: results, options: [.fragmentsAllowed, .sortedKeys])
try data.write(to: URL(fileURLWithPath: {json.dumps(result)}))
'''
        with tempfile.TemporaryDirectory() as td:
            cwd = Path(td)
            (cwd / "main.swift").write_text(source, encoding="utf-8")
            code, out, err = _run(["swiftc", "main.swift", "-o", "program"], cwd,
                                  apply_address_space=False)
            if code != 0:
                compile_error = err or out
                continue
            code, out, err = _run(["./program"], cwd, apply_address_space=False)
            actual = _read_results(cwd, result, len(cases)) if code == 0 else None
        if code != 0:
            return _fail("swift", len(cases), err or out)
        return _score("swift", actual, expected, equal) if actual is not None else _no_results("swift", len(cases))
    return _fail("swift", len(cases), (compile_error or "did not compile")[:600])


def _scala_type(kind: str, width: str) -> str:
    scalar = {"int": "Long" if width == "wide" else "Int", "double": "Double",
              "bool": "Boolean", "string": "String"}
    return f"Array[{_scala_type(kind[:-2], width)}]" if kind.endswith("[]") else scalar[kind]


def _scala_value(value, kind: str, width: str) -> str:
    if kind.endswith("[]"):
        elem = kind[:-2]
        t = _scala_type(elem, width)
        return f"Array[{t}]()" if not value else f"Array[{t}]({', '.join(_scala_value(v, elem, width) for v in value)})"
    if kind == "string":
        return _string_literal(value, "scala")
    if kind == "bool":
        return "true" if value else "false"
    if kind == "double":
        return repr(float(value))
    return f"{int(value)}L" if width == "long" else str(int(value))


_SCALA_JSON = r'''object DsaHarness {
def _dsaQuote(s: String): String = "\"" + s.flatMap {
  case '"' => "\\\""; case '\\' => "\\\\"; case '\n' => "\\n"
  case '\r' => "\\r"; case '\t' => "\\t"
  case c if c < ' ' => "\\u%04x".format(c.toInt)
  case c => c.toString
} + "\""
def _dsaJson(v: Any): String = v match {
  case null => "null"
  case s: String => _dsaQuote(s)
  case b: Boolean => b.toString
  case n: Byte => n.toString; case n: Short => n.toString; case n: Int => n.toString
  case n: Long => n.toString; case n: Double => require(!n.isNaN && !n.isInfinity); n.toString
  case a: Array[_] => a.map(_dsaJson).mkString("[", ",", "]")
  case xs: Iterable[_] => xs.map(_dsaJson).mkString("[", ",", "]")
  case other => throw new IllegalArgumentException("unsupported function result type: " + other.getClass)
}
}
'''


def _run_scala(solution, fn, cases, expected, equal, result):
    from app.services.code_runner import _run
    from app.services.script_runners import _fail, _no_results, _read_results, _score, _unverified
    sig = exec_harness.infer_types(cases, expected)
    if sig is None or any(kind.endswith("[][]") for kind in sig.args):
        return _unverified("scala", len(cases), "Scala grader accepts scalar and one-dimensional array arguments")
    for width in ("int", "long"):
        calls = [_call("scala", solution, fn, [_scala_value(v, t, width) for v, t in zip(case, sig.args)])
                 for case in cases]
        source = f'''{solution}
{_SCALA_JSON}
object Main {{
  def main(args: Array[String]): Unit = {{
    val results = Seq[Any](
{chr(10).join('      ' + call + (',' if i < len(calls)-1 else '') for i, call in enumerate(calls))}
    )
    java.nio.file.Files.write(java.nio.file.Paths.get({json.dumps(result)}), results.map(DsaHarness._dsaJson).mkString("[", ",", "]").getBytes("UTF-8"))
  }}
}}
'''
        with tempfile.TemporaryDirectory() as td:
            cwd = Path(td)
            (cwd / "Main.scala").write_text(source, encoding="utf-8")
            code, out, err = _run(["scalac", "Main.scala"], cwd, apply_address_space=False)
            if code != 0:
                compile_error = err or out
                continue
            code, out, err = _run(["scala", "-cp", ".", "Main"], cwd, apply_address_space=False)
            actual = _read_results(cwd, result, len(cases)) if code == 0 else None
        if code != 0:
            return _fail("scala", len(cases), err or out)
        return _score("scala", actual, expected, equal) if actual is not None else _no_results("scala", len(cases))
    return _fail("scala", len(cases), (compile_error or "did not compile")[:600])


def _haskell_type(kind: str, width: str) -> str:
    scalar = {"int": "Integer" if width == "wide" else "Int", "double": "Double",
              "bool": "Bool", "string": "String"}
    return "[" + _haskell_type(kind[:-2], width) + "]" if kind.endswith("[]") else scalar[kind]


def _haskell_string(value: str) -> str:
    escaped = []
    for char in value:
        code = ord(char)
        escaped.append({"\\": "\\\\", '"': '\\"', "\n": "\\n", "\r": "\\r",
                        "\t": "\\t", "\0": "\\0"}.get(char,
                        f"\\x{code:x}\\&" if code < 0x20 else char))
    return '"' + "".join(escaped) + '"'


def _haskell_value(value, kind: str, width: str) -> str:
    if kind.endswith("[]"):
        return "[" + ", ".join(_haskell_value(v, kind[:-2], width) for v in value) + "]"
    if kind == "string":
        return _haskell_string(value)
    if kind == "bool":
        return "True" if value else "False"
    if kind == "double":
        return repr(float(value))
    return f"({int(value)})"


def _haskell_json_encoder(kind: str, width: str) -> str:
    if kind.endswith("[]"):
        return f"_dsaArray ({_haskell_json_encoder(kind[:-2], width)})"
    return {"int": "show", "double": "show", "bool": "_dsaBool", "string": "_dsaString"}[kind]


_HASKELL_JSON = r'''
_dsaJoin :: String -> [String] -> String
_dsaJoin _ [] = ""
_dsaJoin _ [x] = x
_dsaJoin separator (x:xs) = x ++ separator ++ _dsaJoin separator xs
_dsaArray :: (a -> String) -> [a] -> String
_dsaArray encode xs = "[" ++ _dsaJoin "," (map encode xs) ++ "]"
_dsaBool :: Bool -> String
_dsaBool True = "true"
_dsaBool False = "false"
_dsaString :: String -> String
_dsaString s = "\"" ++ concatMap escape s ++ "\""
  where
    escape '"' = "\\\""
    escape '\\' = "\\\\"
    escape '\n' = "\\n"
    escape '\r' = "\\r"
    escape '\t' = "\\t"
    escape c | fromEnum c < 32 = "\\u" ++ pad (showHex (fromEnum c))
             | otherwise = [c]
    showHex n = let digits = "0123456789abcdef" in
      if n < 16 then [digits !! n] else showHex (n `div` 16) ++ [digits !! (n `mod` 16)]
    pad x = replicate (4 - length x) '0' ++ x
'''


def _run_haskell(solution, fn, cases, expected, equal, result):
    from app.services.code_runner import _run
    from app.services.script_runners import _fail, _no_results, _read_results, _score, _unverified
    sig = exec_harness.infer_types(cases, expected)
    if sig is None or any(kind.endswith("[][]") for kind in sig.args):
        return _unverified("haskell", len(cases), "Haskell grader accepts scalar and one-dimensional list arguments")
    for width in ("Int", "Integer"):
        width_key = "wide" if width == "Integer" else "native"
        calls = [_call("haskell", solution, fn, [_haskell_value(v, t, width_key) for v, t in zip(case, sig.args)])
                 for case in cases]
        encoder = _haskell_json_encoder(sig.ret, width_key)
        result_expr = f"_dsaArray id [{', '.join(f'{encoder} ({call})' for call in calls)}]"
        source = f'''{solution}
{_HASKELL_JSON}
main :: IO ()
main = writeFile {json.dumps(result)} ({result_expr})
'''
        with tempfile.TemporaryDirectory() as td:
            cwd = Path(td)
            (cwd / "Main.hs").write_text(source, encoding="utf-8")
            code, out, err = _run(["ghc", "-v0", "-o", "program", "Main.hs"], cwd,
                                  apply_address_space=False)
            if code != 0:
                compile_error = err or out
                continue
            code, out, err = _run(["./program"], cwd, apply_address_space=False)
            actual = _read_results(cwd, result, len(cases)) if code == 0 else None
        if code != 0:
            return _fail("haskell", len(cases), err or out)
        return _score("haskell", actual, expected, equal) if actual is not None else _no_results("haskell", len(cases))
    return _fail("haskell", len(cases), (compile_error or "did not compile")[:600])


def run(language: str, solution: str, fn: str, cases: list, expected: list, equal):
    """Grade one supported polyglot function or explicitly refuse its shape."""
    from app.services.script_runners import _unverified
    if not cases or len(cases) > 64 or len(cases) != len(expected):
        return _unverified(language, len(cases), "function grading requires 1–64 aligned fixtures")
    if len(solution.encode("utf-8")) > 100_000:
        return _unverified(language, len(cases), "source exceeds the 100 KB execution limit")
    if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", fn or ""):
        from app.services.code_runner import _fail
        return _fail(language, len(cases), "the entry point is not a valid identifier")
    result = f"r{secrets.token_hex(8)}.json"
    runners = {"dart": _run_dart, "kotlin": _run_kotlin, "swift": _run_swift,
               "scala": _run_scala, "haskell": _run_haskell}
    return runners[language](solution, fn, cases, expected, equal, result)
