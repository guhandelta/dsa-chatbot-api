"""Execution capabilities must describe what the runner can really verify."""
import pytest

from app.services.code_runner import available_languages, run_suite
from app.services.execution_adapters import (ADAPTERS, GO_BUILD, SUPPORT_FILES, catalog,
                                             diagnostic_evidence, stdio_commands, unsupported)
from app.db.models import User
from app.routers.tracks import execution_capabilities
from app.routers.training import training_status
from app.services.language_access import allowed_languages


def test_capabilities_are_explicit_and_claim_only_browser_previews_for_js_and_ts():
    profiles = catalog({"python": True, "kotlin": False})
    assert set(ADAPTERS) >= {"python", "javascript", "typescript", "java", "c", "cpp",
                             "rust", "ruby", "go", "csharp", "php", "dart", "kotlin",
                             "swift", "scala", "haskell"}
    assert profiles["python"]["function_execution"] is True
    assert all(ADAPTERS[name].function_tests for name in
               ("dart", "kotlin", "swift", "scala", "haskell"))
    assert profiles["kotlin"]["stdio_execution"] is False
    assert {n for n, p in profiles.items() if p["browser_preview"]} == {"javascript", "typescript"}
    assert not any(p["server_preview"] for p in profiles.values())
    assert profiles["csharp"]["stdio_tests"] is False


def test_stdin_stdout_build_plans_never_invoke_a_shell(tmp_path):
    for language, adapter in ADAPTERS.items():
        if not adapter.stdio_tests:
            continue
        build, run = stdio_commands(language, tmp_path, 256)
        assert build is None or isinstance(build, list)
        assert isinstance(run, list) and run
        # The only shell is Go's fixed build script; learner text is never interpolated.
        if build and build[:2] == ["sh", "-c"]:
            assert language == "go" and build[2] == GO_BUILD
            continue
        assert all(part not in {"sh", "bash", "-c"} for part in (build or []) + run)


def test_typescript_stdio_declares_node_globals_in_a_separate_file(tmp_path):
    build, _ = stdio_commands("typescript", tmp_path, 256)
    assert "main.ts" in build and set(SUPPORT_FILES["typescript"]) <= set(build)


@pytest.mark.parametrize("language,source", [
    ("go", "package main\nimport \"fmt\"\nfunc main() { var n int; fmt.Scan(&n); fmt.Println(n * 2) }"),
    ("typescript", "const n = Number(require('fs').readFileSync(0, 'utf8'));\nconsole.log(n * 2);"),
])
def test_scripted_stdin_stdout_executes_cases(language, source):
    if not available_languages().get(language):
        pytest.skip(f"{language} toolchain unavailable")
    report = run_suite({language: source}, {}, ["2", "3"], ["4", "6"], io_mode="stdio")
    assert report["can_publish"] is True, report["results"]


def test_diagnostic_line_prefers_the_learners_file_over_runtime_frames():
    trace = "panic: boom\n\truntime/panic.go:1073 +0x38\nmain.main()\n\t/work/main.go:5 +0x1c"
    assert diagnostic_evidence("go", "run", trace)["line"] == 5
    assert diagnostic_evidence("python", "run", 'File "/work/main.py", line 3, in <module>')["line"] == 3


def test_unsupported_language_profile_has_the_full_shape():
    assert set(unsupported("cobol")) == set(catalog({})["python"])


@pytest.mark.parametrize("language,source", [
    ("c", "#include <stdio.h>\nint main(void) { int n; scanf(\"%d\", &n); printf(\"%d\\n\", n * 2); }"),
    ("cpp", "#include <iostream>\nint main() { int n; std::cin >> n; std::cout << n * 2; }"),
    ("java", "import java.util.*; public class Main { public static void main(String[] args) { Scanner s=new Scanner(System.in); System.out.println(s.nextInt()*2); } }"),
    ("rust", "use std::io::{self, Read}; fn main() { let mut s=String::new(); io::stdin().read_to_string(&mut s).unwrap(); println!(\"{}\", s.trim().parse::<i32>().unwrap()*2); }"),
])
def test_compiled_stdin_stdout_executes_cases(language, source):
    if not available_languages().get(language):
        pytest.skip(f"{language} compiler unavailable")
    report = run_suite({language: source}, {}, ["2", "3"], ["4", "6"], io_mode="stdio")
    assert report["can_publish"] is True, report["results"]
    assert report["results"][0]["outputs"] == ["4", "6"]


@pytest.mark.parametrize("language,source", [
    ("dart", "import 'dart:io'; void main() { final n = int.parse(stdin.readLineSync()!); print(n * 2); }"),
    ("kotlin", "fun main() { val n = readLine()!!.toInt(); println(n * 2) }"),
    ("swift", "if let line = readLine(), let n = Int(line) { print(n * 2) }"),
    ("scala", "object Main { def main(args: Array[String]): Unit = { println(scala.io.StdIn.readInt() * 2) } }"),
    ("haskell", "main = interact (show . (* 2) . read)"),
])
def test_newly_added_language_runtimes_compile_and_execute_stdin_cases(language, source):
    if not available_languages().get(language):
        pytest.skip(f"{language} toolchain unavailable")
    report = run_suite({language: source}, {}, ["2", "3"], ["4", "6"], io_mode="stdio")
    assert report["can_publish"] is True, report["results"]
    assert report["results"][0]["outputs"] == ["4", "6"]


def test_php_function_style_language_runs_when_runtime_is_installed():
    report = run_suite({"php": "<?php function f($x) { return $x; }"}, {"php": "f"}, [[1]], [1])
    assert report["results"][0]["status"] in {"unverified", "passed"}
    assert report["can_publish"] is available_languages().get("php", False)
    if report["can_publish"]:
        assert report["results"][0]["status"] == "passed"


def test_java_function_workspace_compiles_helper_alongside_generated_harness(monkeypatch):
    from app.services import code_runner
    from app.services.deep_review import run_curated

    entry = "public int totalCost(int price, int quantity) { return Helper.multiply(price, quantity); }"
    helper = "class Helper { static int multiply(int a, int b) { return a * b; } }"
    saw_build = False

    def fake_run(command, cwd, stdin="", apply_address_space=True):
        nonlocal saw_build
        if any("javac" in part for part in command):
            saw_build = True
            assert "Helper.java" in command
            assert (cwd / "Helper.java").read_text() == helper
            source = (cwd / "Solution.java").read_text()
            assert entry in source and "class Solution" in source
            return 0, "", ""
        assert saw_build and command[-1] == "Main"
        return 0, "\n".join(f"__CASE__{value}" for value in (12, 0, 0, 1, 1000000, 42)), ""

    monkeypatch.setattr(code_runner, "available_languages", lambda: {"java": True})
    monkeypatch.setattr(code_runner, "_run", fake_run)
    report = run_curated("java-path-01-values", "// rendered workspace source", "java",
                         {"Main.java": entry, "Helper.java": helper})
    assert saw_build and report["results"][0]["status"] == "passed"
    assert report["results"][0]["passed_cases"] == 6


def test_java_function_workspace_runs_in_pinned_sandbox():
    from app.services.deep_review import run_curated

    if not available_languages().get("java"):
        pytest.skip("Java compiler unavailable")
    entry = "public int totalCost(int price, int quantity) { return Helper.multiply(price, quantity); }"
    helper = "class Helper { static int multiply(int a, int b) { return a * b; } }"
    report = run_curated("java-path-01-values", entry, "java",
                         {"Main.java": entry, "Helper.java": helper})
    result = report["results"][0]
    assert result["status"] == "passed", result
    assert result["passed_cases"] == 6


def test_java_helper_compile_error_reports_native_file_in_pinned_sandbox():
    from app.services.deep_review import run_curated

    if not available_languages().get("java"):
        pytest.skip("Java compiler unavailable")
    entry = "public int totalCost(int price, int quantity) { return Helper.multiply(price, quantity); }"
    helper = "class Helper {\n  static int multiply(int a, int b) { return a * b }\n}"
    report = run_curated("java-path-01-values", entry, "java",
                         {"Main.java": entry, "Helper.java": helper})
    result = report["results"][0]
    assert result["status"] == "failed", result
    assert result["evidence"]["file"] == "Helper.java"
    assert result["evidence"]["line"] == 2


def test_java_helper_compile_error_names_helper_file(monkeypatch):
    from app.services import code_runner
    from app.services.deep_review import run_curated

    entry = "public int totalCost(int price, int quantity) { return Helper.multiply(price, quantity); }"

    def fake_run(command, cwd, stdin="", apply_address_space=True):
        assert "Helper.java" in command
        return 1, "", "Helper.java:2: error: ';' expected"

    monkeypatch.setattr(code_runner, "available_languages", lambda: {"java": True})
    monkeypatch.setattr(code_runner, "_run", fake_run)
    report = run_curated("java-path-01-values", entry, "java",
                         {"Main.java": entry, "Helper.java": "class Helper { broken }"})
    result = report["results"][0]
    assert result["status"] == "failed" and result["tier"] == 2
    assert result["evidence"]["file"] == "Helper.java"
    assert result["evidence"]["line"] == 2
    from app.routers.workspace import case_report
    view = case_report(report, "java", "java-path-01-values",
                       [{"file": "Helper.java", "start": 1, "end": 2}])
    assert view["diagnostic"]["file"] == "Helper.java"
    assert view["diagnostic"]["line"] == 2


def test_java_project_with_unsupported_case_shape_stays_unverified(monkeypatch):
    from app.services import code_runner

    monkeypatch.setattr(code_runner, "available_languages", lambda: {"java": True})
    monkeypatch.setattr(code_runner, "_run_tier2", lambda *args: pytest.fail("standalone compile omits helpers"))
    entry = "public int f(Object input) { return Helper.value(input); }"
    report = run_suite({"java": entry}, {"java": "f"}, [[{"node": 1}]], [{"node": 1}],
                       files={"Main.java": entry, "Helper.java": "class Helper {}"})
    assert report["results"][0]["status"] == "unverified"


def test_stdin_stdout_work_limit_fails_closed():
    report = run_suite({"python": "print(input())"}, {}, ["x"] * 65, ["x"] * 65, io_mode="stdio")
    assert report["can_publish"] is False
    assert report["results"][0]["status"] == "unverified"


def test_diagnostic_evidence_preserves_observed_line_without_terminal_codes():
    evidence = diagnostic_evidence("java", "compile", "\x1b[31mMain.java:7: error: missing token\x1b[0m")
    assert evidence == {"language": "java", "phase": "compile", "file": "Main.java",
                        "message": "Main.java:7: error: missing token", "line": 7}


async def test_capabilities_endpoint_scopes_admin_languages(db):
    user = User(email="capabilities-admin@example.net", hashed_password="x", role="admin")
    db.add(user)
    await db.flush()
    payload = await execution_capabilities(user, db)
    assert set(payload["languages"]) == set(await allowed_languages(db, user))
    assert "java" in payload["languages"]
    assert all("installed" in profile for profile in payload["languages"].values())


async def test_training_status_lists_executable_modes(db):
    user = User(email="capabilities-teacher@example.net", hashed_password="x", role="instructor")
    result = await training_status(user)
    assert set(result["executed_languages"]) == {
        name for name, profile in result["execution_capabilities"].items()
        if profile["function_execution"]}
    assert set(result["stdio_languages"]) == {
        name for name, profile in result["execution_capabilities"].items()
        if profile["stdio_execution"]}
