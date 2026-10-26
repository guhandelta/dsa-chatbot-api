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


def test_unsupported_function_style_language_is_unverified():
    report = run_suite({"php": "<?php function f($x) { return $x; }"}, {"php": "f"}, [[1]], [1])
    assert report["can_publish"] is False
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
