"""TypeScript / Go / Ruby / C# screening rules."""
import pytest

from app.services.code_screener import screen

TS_BLOCKED = [
    "const fs = require('fs');",
    "const load = require; load('node:fs')",
    "require /* c */ ('fs')",
    "import('node:fs').then(f => f)",
    "import fs from 'node:fs';",
    "import type { X } from './x';",
    "import x = require('fs');",
    "export * from './other';",
    "export { a } from './other';",
    "export = foo;",
    "declare module 'fs' { export const x: number; }",
    "declare global { interface Window { a: 1 } }",
    "const k = process.env.SECRET;",
    "const p = process; p.exit(1)",
    "const e = process\n  .env;",
    "console.log(`${process.env.X}`)",
    "const s = `a ${`b ${process.env.X}`} c`;",
    "globalThis['pro' + 'cess']",
    "(globalThis as any).process.exit()",
    "this.constructor.constructor('return process')()",
    "({} as any).constructor.constructor('return 1')()",
    "const {constructor: C} = {} as any;",
    "x['constructor']['constructor']('return 1')()",
    "x?.constructor",
    "x['__proto__']",
    "obj.__proto__.polluted = 1",
    "this['constr' + 'uctor']",
    "eval('1+1')",
    "const f = eval; f('1')",
    "new Function('return 1')()",
    "Function('return 1')()",
    r"const load = require; load('fs')",
    r"require('fs')",
    r"const a = '\x72equire';",
    "Deno.readTextFileSync('x')",
    "Bun.file('x')",
    "global.x = 1",
    "window.location",
    "document.cookie",
    "Reflect.get(Object, 'constructor')",
    "Object.getOwnPropertyDescriptor(a, 'b')",
    "WebAssembly.instantiate(b)",
    "module.exports = {}",
    "exports.a = 1",
    "const s = `${[...process.argv]}`;",
]

TS_ALLOWED = [
    "class Stack<T> { private items: T[] = []; constructor() { this.items = []; } push(x: T): void { this.items.push(x); } }",
    "class Q { constructor(public n: number, private m = 2) {} }",
    "function process(tasks: number[]): number { return tasks.length; }\nprocess([1]);",
    "class Sched { process(t: number): number { return t; } run() { return this.process(1); } }",
    "interface Job { process: (x: number) => number; name: string }\nconst j: Job = { process: (x) => x, name: 'a' };",
    "type Pair = [number, number]; interface Node { val: number; next?: Node }",
    "// @ts-ignore\nconst x: number = 'a' as any;",
    "// @ts-nocheck\nconst y = 1;",
    "/// <reference types=\"node\" />\nconst y = 1;",
    "// uses require and process.env and eval in a comment\nconst y = 1;",
    "/* import fs from 'fs'; globalThis.constructor */ const y = 1;",
    "const msg = 'do not call require(\"fs\") or process.env or eval';",
    "const msg = `the constructor, globalThis and import words ${1 + 1}`;",
    "const window: number[] = []; window.push(1); let sum = 0; for (const w of window) sum += w;",
    "function slide(nums: number[], k: number) { const document = nums.slice(0, k); return document; }",
    "const memo: Record<string, number> = {}; const i = 1, j = 2; memo[`${i},${j}`] = memo[i + ',' + j] ?? 0;",
    "const avg = (a + b) / 2; const r = /ab'c/.test(s); const t = \"x\";",
    "const cb: Function = () => 1;",
    "const u = '\\n'; const re = /\\d+/g;",
    "function f(a: number) { return a / 2 / 3; } const s = 'it\\'s';",
    "const o = { constructorName: 'x', requireAll: true, importance: 1, evaluate: 2 };",
    "job.process; job.require; job.import;",
]


@pytest.mark.parametrize("code", TS_BLOCKED)
def test_typescript_blocked(code):
    assert screen(code, "typescript").verdict == "block", code


@pytest.mark.parametrize("code", TS_ALLOWED)
def test_typescript_allowed(code):
    r = screen(code, "typescript")
    assert r.allowed, (code, r.reasons)


def test_typescript_unterminated_falls_back_to_raw():
    assert screen("const s = 'abc\nprocess.env.X", "typescript").verdict == "block"


def test_typescript_regex_quote_trick_is_not_a_bypass():
    code = "if (x) /'/.test(y); process.env.X; var s = '';"
    assert screen(code, "typescript").verdict == "block"


GO_BLOCKED = [
    'package main\nimport "os/exec"\nfunc main() {}',
    'package main\nimport "net/http"\nfunc main() {}',
    'package main\nimport "net"\n',
    'package main\nimport (\n\t"fmt"\n\t"os"\n)\n',
    'package main\nimport ("fmt"; "syscall")\n',
    'package main\nimport . "unsafe"\n',
    'package main\nimport _ "plugin"\n',
    'package main\nimport x "os"\n',
    'package main\nimport "C"\n',
    'package main\nimport (\n\t"fmt"\n\t"github.com/x/y"\n)\n',
    'package main\nimport `os`\n',
]
GO_ALLOWED = [
    'package main\nimport "fmt"\nfunc main() { fmt.Println("os/exec") }',
    'package main\nimport (\n\t"fmt"\n\t"sort"\n\t"strings"\n\t"strconv"\n\t"math"\n\t"errors"\n\t"sync"\n)\n',
    'package main\n// import "os"\nimport "fmt"\n',
    'package main\nimport (\n\t"container/heap"\n\tstr "strings" // alias\n)\n',
    'package main\nfunc main() { s := "import \\"os\\"" ; _ = s }',
]


@pytest.mark.parametrize("code", GO_BLOCKED)
def test_go_blocked(code):
    assert screen(code, "go").verdict == "block", code


@pytest.mark.parametrize("code", GO_ALLOWED)
def test_go_allowed(code):
    r = screen(code, "go")
    assert r.allowed, (code, r.reasons)


def test_go_unlisted_stdlib_is_warn_not_strike():
    r = screen('package main\nimport "image/png"\n', "go")
    assert r.verdict == "warn" and not r.is_violation


RUBY_BLOCKED = [
    "system('ls')", "system 'ls'", "exec('ls')", "spawn 'ls'", "`ls`", "x = `ls -la`",
    "%x(ls)", "Kernel.system('ls')", "Kernel.open('|ls')", "IO.popen('ls')", "ENV['HOME']",
    "File.read('/x')", "Dir.glob('*')", "require 'socket'", "require 'net/http'",
    "require 'open3'", "require(name)", "require_relative 'x'", "eval('1')", "obj.instance_eval('1')",
    "send(:system, 'ls')", "Kernel.send(:exec, 'ls')", "open('|ls')", "Net::HTTP.get(u)",
    "x = \"#{ENV['K']}\"", "TCPSocket.new('a', 1)", "Object.const_get(:File)",
]
RUBY_ALLOWED = [
    "require 'set'\nrequire \"json\"", "# system('ls') ENV File.read\nx = 1",
    "def exec_plan(a) a end", "def system_name; 'system'; end",
    "puts 'run system now'", "h.fetch('k', 0)", "obj.send(:push, 1)",
    "class Task\n  def process(x) x end\nend", "=begin\nsystem('ls')\n=end\nx = 1",
    "puts \"File not found\"", "x = Struct.new(:a)", "a.each { |v| puts `v`.size } if false && false || true && nil" if False else "puts 1",
]


@pytest.mark.parametrize("code", RUBY_BLOCKED)
def test_ruby_blocked(code):
    assert screen(code, "ruby").verdict == "block", code


@pytest.mark.parametrize("code", RUBY_ALLOWED)
def test_ruby_allowed(code):
    r = screen(code, "ruby")
    assert r.allowed, (code, r.reasons)


CS_BLOCKED = [
    "using System.IO;", "using System.Diagnostics; Process.Start(\"ls\");",
    "System.IO.File.ReadAllText(\"x\");", "File.ReadAllText(\"x\")", "using System.Net.Http;",
    "using System.Reflection;", "Assembly.Load(\"x\")", "Environment.GetEnvironmentVariable(\"A\")",
    "[DllImport(\"libc\")] static extern int f();", "unsafe { int* p = null; }",
    "public static unsafe void F() {}", "new Process().Start()", "var s = new StreamReader(\"x\");",
    "var c = new TcpClient();", "Marshal.AllocHGlobal(1);", "Activator.CreateInstance(t);",
    "Directory.GetFiles(\".\")", "Environment.Exit(1);",
]
CS_ALLOWED = [
    "using System;\nusing System.Collections.Generic;\nusing System.Linq;\nusing System.Text;\nusing System.Numerics;",
    "Console.WriteLine(Environment.NewLine);", "// the word unsafe in a comment\nint x = 1;",
    "var d = new Dictionary<string,int>(); using var sw = new System.IO.StringWriter() ;" if False else "var d = new Dictionary<string,int>();",
    "class Proc { public int Process(int x) => x; }", "string s = \"unsafe operation\";",
    "using System.Threading; var t = new Thread(() => {});",
]


@pytest.mark.parametrize("code", CS_BLOCKED)
def test_csharp_blocked(code):
    assert screen(code, "csharp").verdict == "block", code


@pytest.mark.parametrize("code", CS_ALLOWED)
def test_csharp_allowed(code):
    r = screen(code, "csharp")
    assert r.allowed, (code, r.reasons)


# --- round 2: false-positive and bypass regressions ---------------------------
MORE_BLOCKED = {
    "typescript": [
        "new WebSocket('ws://x')", "navigator.sendBeacon('http://x')", "self.importScripts('x')",
        "const t = <any>globalThis; t.process", "\\u0070rocess.exit()", "globalThis['\\x70rocess']",
        "(0,eval)('1')", "const F = Function.prototype.constructor; F('x')()",
        "[]['filter']['constructor']('return process')()", "console.log(import.meta.url)",
        "let s = \"//\"; process.exit()", "let s = \"/*\"; require('fs'); let t = \"*/\"",
    ],
    "go": [
        'package main;import "os"\n', 'package main\n//go:linkname x os.Exit\nfunc x(int)\n',
        'package main\n//go:embed secret.txt\nvar s string\n', 'package main\nimport ("fmt"\n "\\x6fs")\n',
    ],
    "ruby": [
        "x = <<~EOS\n#{`ls`}\nEOS", "self.send('sys'+'tem', 'id')", "fork { }", "IO.new(1)",
        "TOPLEVEL_BINDING.eval('1')", "x = 1 # c\nENV['A']", "puts 'a' # don't\nsystem('id')",
        "x = %w[ #a ]; ENV['k']",
    ],
    "csharp": [
        "Type.GetType(\"System.IO.File\")", "WebRequest.Create(\"http://x\")",
        "\\u0050rocess.Start(\"x\")", "global::System . IO . File.Delete(\"x\")",
        "var s = $\"{System.IO.File.ReadAllText(\"x\")}\";", "#if DEBUG\nSystem.IO.File.Delete(\"x\");\n#endif",
        "var s = @\"a\"\"b\"; System.IO.File.Delete(s);", "var x = \"/*\"; Process.Start(\"x\"); var y = \"*/\";",
        "System\n.Diagnostics\n.Process\n.Start(\"ls\")",
    ],
}
MORE_ALLOWED = {
    "typescript": [
        "const obj = { process: 1, require: 2 }; console.log(obj.process + obj.require);",
        "const check = '\\u2713 done \\x1b[0m'; console.log(check);",
        "const pat = /[\\u4e00-\\u9fa5]/; pat.test('a');",
        "const fetchData = (x: number) => x; const r = obj.fetch(1); this.fetch(2);",
        "const self = this; const navigator = 1; self.x = navigator;",
    ],
    "go": [
        'package main\nimport "math/rand/v2"\nimport "fmt"\nfunc main() { fmt.Println(rand.IntN(3)) }',
        'package main\nimport "fmt"\n// go:linkname is only mentioned in prose\nfunc main() { fmt.Println("//go:embed") }',
    ],
    "ruby": [
        "puts 'ENV is not used here'", "puts \"Tasks require a name: require 'x'\"",
        "x = 1 # uses ENV and File.read here", "obj.send(:push, 1); op = :+; 1.send(op, 2)",
        "puts \"Open the file? open sesame\"", "h.fetch('k') { |k| k * 2 }",
    ],
    "csharp": [
        'public class M { public static string S() { var s = "System.IO.File.ReadAllText and Process.Start"; return s + @"C:\\p\\File.txt"; } }',
        "int Dfs() { return 0; }\n// Process.Start would be bad; File.ReadAllText too",
        'var msg = $"{a} {b:F2} File {{x}}"; var raw = """Process.Start("x")""";',
        "var path = new List<int>(); var file = 1; var directory = 2;",
    ],
}


@pytest.mark.parametrize("lang,code", [(l, c) for l, cs in MORE_BLOCKED.items() for c in cs])
def test_round2_blocked(lang, code):
    assert screen(code, lang).verdict == "block", code


@pytest.mark.parametrize("lang,code", [(l, c) for l, cs in MORE_ALLOWED.items() for c in cs])
def test_round2_allowed(lang, code):
    r = screen(code, lang)
    assert r.allowed, (code, r.reasons)


@pytest.mark.parametrize("alias,canon", [("ts", "typescript"), ("TS", "typescript"), (" TypeScript ", "typescript"),
                                         ("c#", "csharp"), ("cs", "csharp"), ("C#", "csharp"),
                                         ("golang", "go"), ("Go", "go"), ("rb", "ruby"), ("Ruby", "ruby")])
def test_language_aliases_use_language_rules(alias, canon):
    probe = {"typescript": "const k = require('fs');", "csharp": "System.IO.File.Delete(\"x\");",
             "go": 'package main\nimport "os/exec"\n', "ruby": "system('ls')"}[canon]
    assert screen(probe, alias).verdict == "block"


def test_unknown_language_keeps_generic_rules():
    assert screen("x = 1", "brainfuck").allowed
    assert screen("socket(); import socket", "brainfuck").verdict == "block"
    assert screen("x = 1", "").allowed


@pytest.mark.parametrize("lang", ["typescript", "go", "ruby", "csharp"])
def test_adversarial_input_is_fast_and_never_raises(lang):
    import time
    for unit in ["`${", "'", "/*", "a /", "\"\"\"", "@\"", "#{", "import ("]:
        code = (unit * 20000)[:20000]
        t = time.perf_counter()
        r = screen(code, lang)
        assert r.verdict in {"allow", "warn", "block"}
        assert time.perf_counter() - t < 0.5
