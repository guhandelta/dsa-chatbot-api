"""Type-driven test harness generation for compiled languages.

WHY THIS EXISTS
---------------
`code_runner` could only *execute* Python and JavaScript, because its harness
reads the test cases as JSON from stdin and C, C++, Java and Rust have no JSON
parser in their standard libraries. Everything else was compile-checked only
and reported as "unverified" — which is honest, but it means four of six
languages were never actually run.

The fix avoids runtime parsing entirely. Python already holds the test data and
knows its shape, so it emits the cases as **native literals** directly into a
generated program. Nothing is parsed at run time; the program only has to
*print* its answers, and printing is easy in every language.

THE CONTRACT
------------
Types are inferred from the test data itself (unioned across every case), so
existing problems need no new front matter. The supported set covers the great
majority of array/string problems:

    int  double  bool  string
    int[]  double[]  bool[]  string[]
    int[][]  string[][]

Anything outside it — linked lists, trees, graph node objects — returns None
from `infer_types`, and the caller must keep reporting those languages as
"unverified". That is deliberate: the failure mode of this module is refusing
to verify, never claiming a pass it did not establish.

Integers are widened to 64-bit everywhere (`long long` / `long` / `i64`) so a
sum that overflows 32 bits is not mistaken for a wrong answer.

Each case prints one `__CASE__<json>` line, in order. A missing line means the
program died partway through, which the caller reports as a failure.
"""
from __future__ import annotations

import json
import re
from dataclasses import dataclass

def java_tool(name: str) -> str:
    from pathlib import Path
    from app.core.config import settings
    return str(Path(settings.java_home) / "bin" / name) if settings.java_home else name


RESULT_MARKER = "__CASE__"

SCALARS = ("int", "double", "bool", "string")
VECTORS = ("int[]", "double[]", "bool[]", "string[]")
MATRICES = ("int[][]", "string[][]")
SUPPORTED = SCALARS + VECTORS + MATRICES


@dataclass
class TypeSig:
    """The inferred shape of one problem's entry point."""
    args: list[str]
    ret: str

    def __str__(self) -> str:
        return f"({', '.join(self.args)}) -> {self.ret}"


# ----------------------------------------------------------------- inference

def _scalar_type(v) -> str | None:
    # bool before int: in Python, bool is a subclass of int.
    if isinstance(v, bool):
        return "bool"
    if isinstance(v, int):
        return "int"
    if isinstance(v, float):
        return "double"
    if isinstance(v, str):
        return "string"
    return None


def _unify(a: str | None, b: str | None) -> str | None:
    """Widen two observations of the same position into one type.

    `None` means "nothing observed yet" (an empty list contributes no element
    type) and propagates as unknown rather than guessing.
    """
    if a is None:
        return b
    if b is None:
        return a
    if a == b:
        return a
    # An int column that also holds a float is a float column.
    if {a, b} == {"int", "double"}:
        return "double"
    return "?"          # genuinely mixed — refuse


def _value_type(v) -> str | None:
    s = _scalar_type(v)
    if s:
        return s
    if isinstance(v, list):
        if not v:
            return None                     # empty: element type unobserved
        if all(isinstance(x, list) for x in v):
            inner: str | None = None
            for row in v:
                for x in row:
                    inner = _unify(inner, _scalar_type(x))
            if inner is None:
                return None
            if inner == "int":
                return "int[][]"
            if inner == "string":
                return "string[][]"
            return "?"
        elem: str | None = None
        for x in v:
            elem = _unify(elem, _scalar_type(x))
        if elem is None:
            return None
        return f"{elem}[]" if f"{elem}[]" in VECTORS else "?"
    return None


def infer_types(cases: list, expected: list) -> TypeSig | None:
    """Infer the entry point's shape, or None when it cannot be pinned down.

    Every case contributes, so a type left unobserved by one case (an empty
    array, say) can still be settled by another. Returning None is a normal
    outcome and means "do not claim this language was verified".
    """
    if not cases or not isinstance(cases[0], list):
        return None
    arity = len(cases[0])
    if arity == 0 or any(not isinstance(c, list) or len(c) != arity for c in cases):
        return None

    args: list[str | None] = [None] * arity
    for case in cases:
        for i, v in enumerate(case):
            args[i] = _unify(args[i], _value_type(v))

    ret: str | None = None
    for e in expected:
        ret = _unify(ret, _value_type(e))

    if any(a is None or a not in SUPPORTED for a in args):
        return None
    if ret is None or ret not in SUPPORTED:
        return None
    return TypeSig(args=[a for a in args], ret=ret)  # type: ignore[misc]


# ------------------------------------------------------------- literal emitters

def _lit_c(v, t: str) -> str:
    if t == "string":
        return json.dumps(str(v))
    if t == "bool":
        return "1" if v else "0"
    if t == "double":
        return repr(float(v))
    return str(int(v))


def _lit_rust(v, t: str) -> str:
    if t == "string":
        return f"{json.dumps(str(v))}.to_string()"
    if t == "bool":
        return "true" if v else "false"
    if t == "double":
        return f"{float(v)!r}f64"
    return f"{int(v)}i64"


def _lit_java(v, t: str) -> str:
    if t == "string":
        return json.dumps(str(v))
    if t == "bool":
        return "true" if v else "false"
    if t == "double":
        return repr(float(v))
    return f"{int(v)}L"


_C_SCALAR = {"int": "long long", "double": "double", "bool": "int", "string": "char*"}
_CPP_SCALAR = {"int": "long long", "double": "double", "bool": "bool", "string": "std::string"}
_JAVA_SCALAR = {"int": "long", "double": "double", "bool": "boolean", "string": "String"}
_RUST_SCALAR = {"int": "i64", "double": "f64", "bool": "bool", "string": "String"}


def _elem(t: str) -> str:
    return t.replace("[]", "")


# ------------------------------------------------------------------- C++

_CPP_PRELUDE = r'''
#include <cstdio>
#include <cstdlib>
#include <cmath>
#include <iostream>
#include <iomanip>
#include <limits>
#include <string>
#include <vector>

namespace _h {
static void esc(const std::string& s) {
  std::cout << '"';
  for (unsigned char c : s) {
    if (c == '"' || c == '\\') std::cout << '\\' << c;
    else if (c == '\n') std::cout << "\\n";
    else if (c == '\t') std::cout << "\\t";
    else if (c == '\r') std::cout << "\\r";
    else if (c < 0x20) { char b[8]; snprintf(b, sizeof b, "\\u%04x", c); std::cout << b; }
    else std::cout << c;
  }
  std::cout << '"';
}
inline void emit(bool v) { std::cout << (v ? "true" : "false"); }
inline void emit(char v) { std::cout << static_cast<int>(v); }
inline void emit(long long v) { std::cout << v; }
inline void emit(unsigned long long v) { std::cout << v; }
inline void emit(long v) { std::cout << v; }
inline void emit(int v) { std::cout << v; }
inline void emit(double v) {
  // Round-trippable, and integral values stay integral so 3.0 does not read
  // as a different answer than 3.
  if (v == static_cast<long long>(v) && std::abs(v) < 1e15)
    std::cout << static_cast<long long>(v);
  else std::cout << std::setprecision(17) << v;
}
inline void emit(const std::string& v) { esc(v); }
inline void emit(const char* v) { esc(std::string(v)); }
template <class T> void emit(const std::vector<T>& v) {
  std::cout << '[';
  for (size_t i = 0; i < v.size(); ++i) { if (i) std::cout << ','; emit(v[i]); }
  std::cout << ']';
}
}  // namespace _h
'''

_CPP_TYPE = {
    "wide":   {"int": "long long", "double": "double", "bool": "bool", "string": "std::string"},
    "narrow": {"int": "int",       "double": "double", "bool": "bool", "string": "std::string"},
}


def _cpp_decl(t: str, width: str) -> str:
    base = _CPP_TYPE[width][_elem(t)]
    if t in MATRICES:
        return f"std::vector<std::vector<{base}>>"
    if t in VECTORS:
        return f"std::vector<{base}>"
    return base


def _cpp_value(v, t: str, width: str) -> str:
    elem = _elem(t)
    if t in MATRICES:
        rows = ", ".join(
            "{" + ", ".join(_lit_c(x, elem) if elem != "string" else json.dumps(str(x))
                            for x in row) + "}"
            for row in v
        )
        return "{" + rows + "}"
    if t in VECTORS:
        return "{" + ", ".join(
            json.dumps(str(x)) if elem == "string" else _lit_c(x, elem) for x in v
        ) + "}"
    if t == "string":
        return json.dumps(str(v))
    if t == "bool":
        return "true" if v else "false"
    return _lit_c(v, t)


def render_cpp(solution: str, fn: str, cases: list, sig: TypeSig, width: str) -> str:
    body = []
    for case in cases:
        lines = []
        names = []
        for i, (v, t) in enumerate(zip(case, sig.args)):
            decl = _cpp_decl(t, width)
            lines.append(f"    {decl} a{i} = {_cpp_value(v, t, width)};")
            names.append(f"a{i}")
        lines.append(f"    auto r = {fn}({', '.join(names)});")
        lines.append('    std::cout << "' + RESULT_MARKER + '"; _h::emit(r);'
                     ' std::cout << std::endl;')
        body.append("  {\n" + "\n".join(lines) + "\n  }")
    return (_CPP_PRELUDE + "\n" + solution
            + "\n\nint main() {\n" + "\n".join(body) + "\n  return 0;\n}\n")


# ------------------------------------------------------------------- Java

_JAVA_PRELUDE = r'''
import java.util.*;

public class Main {
  static StringBuilder _sb = new StringBuilder();

  static void _esc(String s) {
    _sb.append('"');
    for (int i = 0; i < s.length(); i++) {
      char c = s.charAt(i);
      if (c == '"' || c == '\\') _sb.append('\\').append(c);
      else if (c == '\n') _sb.append("\\n");
      else if (c == '\t') _sb.append("\\t");
      else if (c == '\r') _sb.append("\\r");
      else if (c < 0x20) _sb.append(String.format("\\u%04x", (int) c));
      else _sb.append(c);
    }
    _sb.append('"');
  }

  static void _emit(Object o) {
    if (o == null) { _sb.append("null"); return; }
    if (o instanceof String) { _esc((String) o); return; }
    if (o instanceof Character) { _esc(o.toString()); return; }
    if (o instanceof Boolean) { _sb.append(((Boolean) o) ? "true" : "false"); return; }
    if (o instanceof Double || o instanceof Float) {
      double d = ((Number) o).doubleValue();
      // Keep integral doubles integral so 3.0 and 3 compare equal downstream.
      if (d == Math.rint(d) && Math.abs(d) < 1e15) _sb.append((long) d);
      else _sb.append(d);
      return;
    }
    if (o instanceof Number) { _sb.append(o.toString()); return; }
    if (o instanceof long[]) { long[] a = (long[]) o; _sb.append('[');
      for (int i = 0; i < a.length; i++) { if (i > 0) _sb.append(','); _sb.append(a[i]); }
      _sb.append(']'); return; }
    if (o instanceof int[]) { int[] a = (int[]) o; _sb.append('[');
      for (int i = 0; i < a.length; i++) { if (i > 0) _sb.append(','); _sb.append(a[i]); }
      _sb.append(']'); return; }
    if (o instanceof double[]) { double[] a = (double[]) o; _sb.append('[');
      for (int i = 0; i < a.length; i++) { if (i > 0) _sb.append(','); _emit(a[i]); }
      _sb.append(']'); return; }
    if (o instanceof boolean[]) { boolean[] a = (boolean[]) o; _sb.append('[');
      for (int i = 0; i < a.length; i++) { if (i > 0) _sb.append(','); _sb.append(a[i]); }
      _sb.append(']'); return; }
    if (o instanceof char[]) { _esc(new String((char[]) o)); return; }
    if (o instanceof Object[]) { Object[] a = (Object[]) o; _sb.append('[');
      for (int i = 0; i < a.length; i++) { if (i > 0) _sb.append(','); _emit(a[i]); }
      _sb.append(']'); return; }
    if (o instanceof Iterable) { _sb.append('['); boolean f = true;
      for (Object x : (Iterable<?>) o) { if (!f) _sb.append(','); f = false; _emit(x); }
      _sb.append(']'); return; }
    _esc(o.toString());
  }

  static void _flush() { System.out.println("__MARKER__" + _sb); _sb.setLength(0); }
'''

_JAVA_TYPE = {
    "wide":   {"int": "long", "double": "double", "bool": "boolean", "string": "String"},
    "narrow": {"int": "int",  "double": "double", "bool": "boolean", "string": "String"},
}


def _java_decl(t: str, width: str) -> str:
    base = _JAVA_TYPE[width][_elem(t)]
    if t in MATRICES:
        return f"{base}[][]"
    if t in VECTORS:
        return f"{base}[]"
    return base


def _java_value(v, t: str, width: str) -> str:
    elem = _elem(t)
    wide = width == "wide"

    def one(x):
        if elem == "string":
            return json.dumps(str(x))
        if elem == "bool":
            return "true" if x else "false"
        if elem == "double":
            return repr(float(x))
        return f"{int(x)}L" if wide else str(int(x))

    if t in MATRICES:
        return "{" + ", ".join("{" + ", ".join(one(x) for x in row) + "}" for row in v) + "}"
    if t in VECTORS:
        return "{" + ", ".join(one(x) for x in v) + "}"
    return one(v)


def render_java(solution: str, fn: str, cases: list, sig: TypeSig,
                width: str, call: str) -> tuple[str, str]:
    """Returns (Main.java source, helper class file content).

    `call` is "static" for `Solution.fn(...)` or "instance" for
    `new Solution().fn(...)`; both conventions are common in published
    solutions, so the caller tries each.
    """
    cls = _java_class_name(solution) or "Solution"
    invoke = f"{cls}.{fn}" if call == "static" else f"new {cls}().{fn}"
    signature = re.search(r"\b" + re.escape(fn) + r"\s*\(([^)]*)\)", solution)
    parameters = signature.group(1).split(',') if signature else []
    body = []
    for case in cases:
        lines, names = [], []
        for i, (v, t) in enumerate(zip(case, sig.args)):
            lines.append(f"      {_java_decl(t, width)} a{i} = {_java_value(v, t, width)};")
            parameter = parameters[i] if i < len(parameters) else ""
            names.append(f"java.util.Arrays.asList(a{i})"
                         if t == "string[]" and re.search(r"\bList\s*<\s*String\s*>", parameter)
                         else f"a{i}")
        lines.append(f"      _emit({invoke}({', '.join(names)}));")
        lines.append("      _flush();")
        body.append("    {\n" + "\n".join(lines) + "\n    }")
    main = (_JAVA_PRELUDE.replace("__MARKER__", RESULT_MARKER)
            + "\n  public static void main(String[] _args) {\n"
            + "\n".join(body) + "\n  }\n}\n")
    return main, _java_wrap(solution, cls)


_JAVA_CLASS_RE = re.compile(
    r"^\s*(?:public\s+|final\s+|abstract\s+)*class\s+(\w+)", re.M)


def _java_class_name(solution: str) -> str | None:
    m = _JAVA_CLASS_RE.search(solution)
    return m.group(1) if m else None


def _java_wrap(solution: str, cls: str) -> str:
    """Bare methods get wrapped in a class; `public` is stripped so the file
    name need not match (we always write it as <cls>.java anyway)."""
    if _java_class_name(solution):
        return solution.replace("public class", "class", 1)
    return f"import java.util.*;\nclass {cls} {{\n{solution}\n}}\n"


# ------------------------------------------------------------------- Rust

_RUST_PRELUDE = r'''
#![allow(dead_code, unused_imports, unused_mut, unused_variables, non_snake_case)]
use std::collections::*;
use std::fmt::Write as _;

trait Emit { fn emit(&self) -> String; }
fn _esc(s: &str) -> String {
    let mut o = String::from("\"");
    for c in s.chars() {
        match c {
            '"'  => o.push_str("\\\""),
            '\\' => o.push_str("\\\\"),
            '\n' => o.push_str("\\n"),
            '\t' => o.push_str("\\t"),
            '\r' => o.push_str("\\r"),
            c if (c as u32) < 0x20 => { let _ = write!(o, "\\u{:04x}", c as u32); }
            c => o.push(c),
        }
    }
    o.push('"');
    o
}
macro_rules! emit_int { ($($t:ty),*) => { $(impl Emit for $t {
    fn emit(&self) -> String { self.to_string() } })* } }
emit_int!(i8, i16, i32, i64, i128, isize, u8, u16, u32, u64, usize);
impl Emit for bool { fn emit(&self) -> String { self.to_string() } }
impl Emit for f64 {
    fn emit(&self) -> String {
        // Integral floats stay integral so 3.0 matches 3 downstream.
        if self.fract() == 0.0 && self.abs() < 1e15 { format!("{}", *self as i64) }
        else { format!("{}", self) }
    }
}
impl Emit for String { fn emit(&self) -> String { _esc(self) } }
impl Emit for &str  { fn emit(&self) -> String { _esc(self) } }
impl Emit for char  { fn emit(&self) -> String { _esc(&self.to_string()) } }
impl<T: Emit> Emit for Vec<T> {
    fn emit(&self) -> String {
        let parts: Vec<String> = self.iter().map(|x| x.emit()).collect();
        format!("[{}]", parts.join(","))
    }
}
impl<T: Emit> Emit for &[T] {
    fn emit(&self) -> String {
        let parts: Vec<String> = self.iter().map(|x| x.emit()).collect();
        format!("[{}]", parts.join(","))
    }
}
impl<T: Emit> Emit for Option<T> {
    fn emit(&self) -> String {
        match self { Some(v) => v.emit(), None => "null".to_string() }
    }
}
'''

_RUST_TYPE = {
    "wide":   {"int": "i64", "double": "f64", "bool": "bool", "string": "String"},
    "narrow": {"int": "i32", "double": "f64", "bool": "bool", "string": "String"},
}


def _rust_decl(t: str, width: str) -> str:
    base = _RUST_TYPE[width][_elem(t)]
    if t in MATRICES:
        return f"Vec<Vec<{base}>>"
    if t in VECTORS:
        return f"Vec<{base}>"
    return base


def _rust_value(v, t: str, width: str) -> str:
    elem = _elem(t)
    suffix = _RUST_TYPE[width]["int"]

    def one(x):
        if elem == "string":
            return f"{json.dumps(str(x))}.to_string()"
        if elem == "bool":
            return "true" if x else "false"
        if elem == "double":
            return f"{float(x)!r}f64"
        return f"{int(x)}{suffix}"

    if t in MATRICES:
        return "vec![" + ", ".join(
            "vec![" + ", ".join(one(x) for x in row) + "]" for row in v) + "]"
    if t in VECTORS:
        return "vec![" + ", ".join(one(x) for x in v) + "]"
    return one(v)


def render_rust(solution: str, fn: str, cases: list, sig: TypeSig,
                width: str, call: str) -> str:
    """`call` is "bare" for `fn(...)` or "assoc" for `Solution::fn(...)` —
    the common Rust convention puts solutions in `impl Solution`."""
    invoke = fn if call == "bare" else f"Solution::{fn}"
    signature = re.search(r"\b" + re.escape(fn) + r"\s*\(([^)]*)\)", solution)
    parameters = signature.group(1).split(',') if signature else []
    body = []
    for case in cases:
        lines, names = [], []
        for i, (v, t) in enumerate(zip(case, sig.args)):
            lines.append(f"        let a{i}: {_rust_decl(t, width)} "
                         f"= {_rust_value(v, t, width)};")
            names.append(f"a{i}")
        lines.append(f"        let r = {invoke}({', '.join(names)});")
        lines.append(f'        println!("{RESULT_MARKER}{{}}", r.emit());')
        body.append("    {\n" + "\n".join(lines) + "\n    }")
    shim = ""
    if "impl Solution" in solution and not re.search(r"\bstruct\s+Solution\b", solution):
        # The common Rust form writes `impl Solution` and assumes the struct
        # is declared for you.
        shim = "struct Solution;\n"
    return (_RUST_PRELUDE + "\n" + shim + solution
            + "\n\nfn main() {\n" + "\n".join(body) + "\n}\n")


# -------------------------------------------------------------------- C

# C cannot return a sized array, so the usual convention threads sizes
# through parameters:
#
#   int*  twoSum(int* nums, int numsSize, int target, int* returnSize)
#   bool  anyNeg(int** g, int gSize, int* gColSize)
#
# Array arguments expand to (ptr, size); matrices to (ptr, rows, colSizes);
# an array return adds a trailing `int* returnSize`. Return shapes outside
# scalars / strings / 1-D numeric arrays are refused rather than guessed at.
_C_RETURNABLE = ("int", "double", "bool", "string", "int[]", "double[]", "int[][]")

_C_PRELUDE = r'''
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdbool.h>
#include <math.h>

static void _esc(const char* s) {
  putchar('"');
  if (s) for (const unsigned char* p = (const unsigned char*)s; *p; ++p) {
    if (*p == '"' || *p == '\\') { putchar('\\'); putchar(*p); }
    else if (*p == '\n') fputs("\\n", stdout);
    else if (*p == '\t') fputs("\\t", stdout);
    else if (*p == '\r') fputs("\\r", stdout);
    else if (*p < 0x20) printf("\\u%04x", *p);
    else putchar(*p);
  }
  putchar('"');
}
static void _emit_d(double v) {
  if (v == (double)(long long)v && fabs(v) < 1e15) printf("%lld", (long long)v);
  else printf("%.17g", v);
}
'''


def c_supported(sig: TypeSig) -> bool:
    """C is refused for return shapes its calling convention cannot express
    unambiguously. Refusing keeps the result honest: the caller reports the
    language as unverified rather than claiming a pass."""
    return sig.ret in _C_RETURNABLE


def _c_elem_type(t: str, width: str) -> str:
    base = _elem(t)
    if base == "int":
        return "long long" if width == "wide" else "int"
    return _C_SCALAR[base]


def _c_fmt(t: str) -> str:
    return "%lld" if t == "int" else "%d"


def render_c(solution: str, fn: str, cases: list, sig: TypeSig, width: str) -> str | None:
    if not c_supported(sig):
        return None
    body = []
    for case in cases:
        lines: list[str] = []
        names: list[str] = []
        for i, (v, t) in enumerate(zip(case, sig.args)):
            et = _c_elem_type(t, width)
            if t in MATRICES:
                if _elem(t) != "int":
                    return None                 # string matrices: not expressible here
                rows = v or []
                for j, row in enumerate(rows):
                    vals = ", ".join(_lit_c(x, "int") for x in row) or "0"
                    n = max(len(row), 1)
                    lines.append(f"    {et} a{i}_r{j}[{n}] = {{{vals}}};")
                ptrs = ", ".join(f"a{i}_r{j}" for j in range(len(rows))) or "NULL"
                cols = ", ".join(str(len(r)) for r in rows) or "0"
                lines.append(f"    {et}* a{i}_p[{max(len(rows), 1)}] = {{{ptrs}}};")
                lines.append(f"    int a{i}_c[{max(len(rows), 1)}] = {{{cols}}};")
                names += [f"a{i}_p", str(len(rows)), f"a{i}_c"]
            elif t in VECTORS:
                elem = _elem(t)
                if elem == "string":
                    vals = ", ".join(json.dumps(str(x)) for x in v) or "NULL"
                else:
                    vals = ", ".join(_lit_c(x, elem) for x in v) or "0"
                lines.append(f"    {et} a{i}[{max(len(v), 1)}] = {{{vals}}};")
                names += [f"a{i}", str(len(v))]
            else:
                lines.append(f"    {et} a{i} = {_lit_c(v, t)};")
                names.append(f"a{i}")

        ret = sig.ret
        if ret == "int[][]":
            # Nested result: the function returns int** rows, fills returnSize with the
            # row count and returnColumnSizes with each row's length (the usual LeetCode
            # convention). The harness prints [[...], [...]] from those three outputs.
            et = _c_elem_type("int", width)
            lines.append("    int _rn = 0;")
            lines.append("    int* _rc = NULL;")
            lines.append(f"    {et}** _r = {fn}({', '.join(names + ['&_rn', '&_rc'])});")
            lines.append(f'    fputs("{RESULT_MARKER}", stdout); putchar(\'[\');')
            lines.append("    for (int _k = 0; _k < _rn; ++_k) {")
            lines.append("      if (_k) putchar(',');")
            lines.append("      putchar('[');")
            lines.append("      for (int _j = 0; _j < _rc[_k]; ++_j) {")
            lines.append("        if (_j) putchar(',');")
            lines.append('        printf("%lld", (long long)_r[_k][_j]);')
            lines.append("      }")
            lines.append("      putchar(']');")
            lines.append("    }")
            lines.append("    putchar(']'); putchar('\\n');")
        elif ret in VECTORS:
            rt = _c_elem_type(ret, width)
            lines.append("    int _rn = 0;")
            lines.append(f"    {rt}* _r = {fn}({', '.join(names + ['&_rn'])});")
            lines.append(f'    fputs("{RESULT_MARKER}", stdout); putchar(\'[\');')
            lines.append("    for (int _k = 0; _k < _rn; ++_k) {")
            lines.append("      if (_k) putchar(',');")
            if _elem(ret) == "double":
                lines.append("      _emit_d(_r[_k]);")
            else:
                lines.append(f'      printf("{_c_fmt(_elem(ret))}", _r[_k]);')
            lines.append("    }")
            lines.append("    putchar(']'); putchar('\\n');")
        else:
            rt = _c_elem_type(ret, width)
            lines.append(f"    {rt} _r = {fn}({', '.join(names)});")
            lines.append(f'    fputs("{RESULT_MARKER}", stdout);')
            if ret == "string":
                lines.append("    _esc(_r);")
            elif ret == "double":
                lines.append("    _emit_d(_r);")
            elif ret == "bool":
                lines.append('    fputs(_r ? "true" : "false", stdout);')
            else:
                lines.append(f'    printf("{_c_fmt(ret)}", _r);')
            lines.append("    putchar('\\n');")
        body.append("  {\n" + "\n".join(lines) + "\n  }")
    return (_C_PRELUDE + "\n" + solution
            + "\n\nint main(void) {\n" + "\n".join(body) + "\n  return 0;\n}\n")


# ------------------------------------------------------- candidate driver

# Compiled languages vary in how published solutions are written, so each gets
# an ordered list of candidate shapes and the first that COMPILES wins.
#
# Wide (64-bit) is always tried first. If the solution genuinely uses 64-bit
# types, only the wide candidate compiles; if it uses 32-bit types, the wide
# candidate fails to compile and we fall through. That ordering is only safe
# because every mismatch is a hard compile error — see C_WERROR for why C
# needs help to make it one.
CANDIDATES: dict[str, list[tuple[str, str | None]]] = {
    "cpp":  [("wide", None), ("narrow", None)],
    "c":    [("wide", None), ("narrow", None)],
    "java": [("wide", "instance"), ("wide", "static"),
             ("narrow", "instance"), ("narrow", "static")],
    "rust": [("wide", "assoc"), ("wide", "bare"),
             ("narrow", "assoc"), ("narrow", "bare")],
}

# C will build a program that passes `long long*` to an `int*` parameter with
# only a warning, and the program then reads two 32-bit halves as one 64-bit
# value — a wrong answer that looks like a real one. These make it an error, so
# the wide candidate is rejected and the narrow one is tried instead. C++, Java
# and Rust reject the equivalent mismatch on their own.
C_WERROR = [
    "-Werror=implicit-function-declaration",
    "-Werror=incompatible-pointer-types",
    "-Werror=int-conversion",
    "-Werror=implicit-int",
    "-Werror=return-type",
]

# Languages whose runtime RESERVES a large virtual address space at startup, so
# an RLIMIT_AS cap makes them abort before running a line. Node was already
# known; the JVM behaves the same way, and javac is itself a Java program.
# Their heaps are bounded with a runtime flag instead.
NO_ADDRESS_SPACE_LIMIT = frozenset({"javascript", "java"})

# The sandbox strips the environment so executed code cannot read .env or API
# keys. But a few variables only tell a toolchain where it lives, and without
# them the toolchain cannot start:
#
#   RUSTUP_HOME / CARGO_HOME / RUSTUP_TOOLCHAIN — `rustc` from a rustup install
#     (the normal way to install Rust) is a shim that resolves the real
#     compiler through these. With HOME pointed at a scratch directory and
#     these absent, rustup exits with "could not choose a version of rustc".
#   JAVA_HOME — some JDK layouts need it to locate the runtime.
#   SDKROOT — clang on macOS needs it to find system headers.
#
# None of them carry secrets, so passing them through keeps the isolation
# property while letting the compilers actually run.
TOOLCHAIN_ENV_PASSTHROUGH = (
    "RUSTUP_HOME", "CARGO_HOME", "RUSTUP_TOOLCHAIN", "JAVA_HOME", "SDKROOT",
)


@dataclass
class RunOutcome:
    status: str                  # "passed" | "failed" | "unverified"
    detail: str = ""
    outputs: list | None = None
    candidate: str = ""


def _parse_cases(stdout: str, n: int) -> list | None:
    out = []
    for line in stdout.splitlines():
        if line.startswith(RESULT_MARKER):
            try:
                out.append(json.loads(line[len(RESULT_MARKER):]))
            except json.JSONDecodeError:
                return None
    return out if len(out) == n else None


def compile_and_run(language: str, solution: str, fn: str, cases: list,
                    expected: list, *, workdir, run, memory_mb: int,
                    equal) -> RunOutcome:
    """Execute a compiled-language solution against the test cases.

    `run(cmd, cwd, stdin, apply_address_space) -> (code, stdout, stderr)` is
    injected so the sandbox (rlimits, stripped env, timeout) stays owned by the
    caller and this module stays testable on its own. `workdir` is a factory
    returning a fresh scratch directory context manager.

    An "unverified" result means this module declined to make a claim — the
    types could not be pinned down, the shape is not expressible, or nothing
    compiled. It never means "probably fine".
    """
    sig = infer_types(cases, expected)
    if sig is None:
        return RunOutcome("unverified",
                          "test-case shapes are not expressible as a typed "
                          "signature (linked lists, trees and node graphs land "
                          "here) — execution skipped, nothing claimed")
    if language == "c" and not c_supported(sig):
        return RunOutcome("unverified",
                          f"C's calling convention cannot express a {sig.ret} "
                          f"return unambiguously — execution skipped")

    no_as = language not in NO_ADDRESS_SPACE_LIMIT
    errors: list[str] = []

    for width, call in CANDIDATES[language]:
        tag = f"{width}" + (f"/{call}" if call else "")
        with workdir() as cwd:
            try:
                files, build, exec_cmd = _plan(language, solution, fn, cases,
                                               sig, width, call, memory_mb)
            except _Unexpressible as exc:
                return RunOutcome("unverified", str(exc))
            for name, text in files.items():
                (cwd / name).write_text(text)

            code, out, err = run(build, cwd, "", no_as)
            if code != 0:
                errors.append(f"[{tag}] {(err or out).strip()[:160]}")
                continue

            code, out, err = run(exec_cmd, cwd, "", no_as)
            if code != 0:
                return RunOutcome("failed",
                                  f"crashed during execution: "
                                  f"{(err or out).strip()[:400] or 'non-zero exit'}",
                                  candidate=tag)
            got = _parse_cases(out, len(cases))
            if got is None:
                return RunOutcome("failed",
                                  "incomplete or unparseable output — the "
                                  "program stopped partway through the cases",
                                  candidate=tag)
            mismatches = [
                f"case {i + 1}: got {a!r}, expected {e!r}"
                for i, (a, e) in enumerate(zip(got, expected)) if not equal(a, e)
            ]
            if mismatches:
                return RunOutcome("failed", "; ".join(mismatches[:5]), got, tag)
            return RunOutcome("passed", f"executed {len(cases)} cases ({tag})",
                              got, tag)

    return RunOutcome("unverified",
                      "no candidate signature compiled; the solution's "
                      "signature does not match a known convention: "
                      + " | ".join(errors[:2]))


class _Unexpressible(Exception):
    """The renderer cannot express this shape in this language."""


def _plan(language, solution, fn, cases, sig, width, call, memory_mb):
    """Returns (files to write, build command, execute command)."""
    if language == "cpp":
        return ({"m.cpp": render_cpp(solution, fn, cases, sig, width)},
                ["g++", "-std=c++17", "-O1", "-o", "m", "m.cpp"], ["./m"])
    if language == "c":
        src = render_c(solution, fn, cases, sig, width)
        if src is None:
            raise _Unexpressible("C renderer declined this argument shape")
        return ({"m.c": src},
                ["gcc", "m.c", "-o", "m", "-std=c11", "-O1", *C_WERROR, "-lm"],
                ["./m"])
    if language == "rust":
        return ({"m.rs": render_rust(solution, fn, cases, sig, width, call)},
                ["rustc", "--edition", "2021", "-O", "-A", "warnings",
                 "-o", "m", "m.rs"], ["./m"])
    if language == "java":
        main, helper = render_java(solution, fn, cases, sig, width, call)
        cls = _java_class_name(solution) or "Solution"
        return ({"Main.java": main, f"{cls}.java": helper},
                [java_tool("javac"), "-nowarn", "Main.java", f"{cls}.java"],
                [java_tool("java"), f"-Xmx{memory_mb}m", "-Xss64m", "Main"])
    raise _Unexpressible(f"no compiled renderer for {language}")
