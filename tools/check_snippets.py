#!/usr/bin/env python3
"""Extract every fenced solution from the problem .md files and syntax-check
each with the real toolchain. Python/JS/C/C++ are fully checked here;
Java/Rust get a lightweight structural check (no compiler in this env)."""
import re
import subprocess
import sys
import tempfile
from pathlib import Path

PROBLEMS = Path(__file__).resolve().parents[1] / "data" / "dsa_problems"

# Preludes wrap a bare function-style snippet into a compilable unit.
C_PRELUDE = """#include <stdlib.h>
#include <string.h>
#include <stdbool.h>
#include <limits.h>
#include <stdint.h>
struct ListNode { int val; struct ListNode *next; };
struct TreeNode { int val; struct TreeNode *left; struct TreeNode *right; };
"""
CPP_PRELUDE = """#include <bits/stdc++.h>
using namespace std;
struct ListNode { int val; ListNode *next; ListNode(int x):val(x),next(nullptr){} };
struct TreeNode { int val; TreeNode *left,*right; TreeNode(int x):val(x),left(nullptr),right(nullptr){} };
"""

block_re = re.compile(r"^### (Python|JavaScript|Java|C\+\+|C|Rust)\n```[a-z+]*\n(.*?)```",
                      re.DOTALL | re.MULTILINE)


def run(cmd, **kw):
    return subprocess.run(cmd, capture_output=True, text=True, **kw)


def check(lang: str, code: str, tmp: Path) -> tuple[bool, str]:
    if lang == "Python":
        f = tmp / "s.py"
        f.write_text(code)
        r = run([sys.executable, "-m", "py_compile", str(f)])
        return r.returncode == 0, r.stderr
    if lang == "JavaScript":
        f = tmp / "s.js"
        f.write_text(code)
        r = run(["node", "--check", str(f)])
        return r.returncode == 0, r.stderr
    if lang == "C":
        f = tmp / "s.c"
        f.write_text(C_PRELUDE + code)
        r = run(["gcc", "-fsyntax-only", "-w", str(f)])
        return r.returncode == 0, r.stderr
    if lang == "C++":
        f = tmp / "s.cpp"
        f.write_text(CPP_PRELUDE + code)
        r = run(["g++", "-std=c++17", "-fsyntax-only", "-w", str(f)])
        return r.returncode == 0, r.stderr
    if lang == "Java":
        # No javac here: structural sanity only.
        ok = code.count("{") == code.count("}") and "public" in code
        return ok, "brace/keyword mismatch" if not ok else ""
    if lang == "Rust":
        ok = code.count("{") == code.count("}") and "pub fn" in code
        return ok, "brace/fn mismatch" if not ok else ""
    return False, "unknown language"


def main():
    failures = []
    counts = {}
    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td)
        for md in sorted(PROBLEMS.glob("*.md")):
            text = md.read_text()
            blocks = block_re.findall(text)
            if not blocks:
                continue
            for lang, code in blocks:
                ok, err = check(lang, code, tmp)
                counts[lang] = counts.get(lang, [0, 0])
                counts[lang][0] += 1
                if ok:
                    counts[lang][1] += 1
                else:
                    failures.append((md.name, lang, err.strip().splitlines()[-3:]))
    print("=== Syntax-check results by language (passed/total) ===")
    for lang in ("Python", "JavaScript", "C", "C++", "Java", "Rust"):
        if lang in counts:
            total, ok = counts[lang]
            print(f"  {lang:12} {ok}/{total}")
    if failures:
        print(f"\n=== {len(failures)} FAILURES ===")
        for name, lang, err in failures:
            print(f"\n[{name}] {lang}:")
            for line in err:
                print(f"    {line}")
    else:
        print("\nAll snippets passed their checks.")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
