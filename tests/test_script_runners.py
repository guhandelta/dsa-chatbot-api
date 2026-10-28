"""Scripted-language execution: harness rendering and, where the toolchain
exists, real runs (correct, wrong, uncompilable, endless)."""
import pytest

from app.services import exec_harness, script_runners
from app.services.code_runner import available_languages, run_suite

CASES = [[3, 4], [0, 5], [-2, 6]]
EXPECTED = [12, 0, -12]
SIG = exec_harness.infer_types(CASES, EXPECTED)

SOLUTIONS = {
    'ruby': ('def total_cost(price, quantity)\n  price * quantity\nend\n', 'total_cost'),
    'typescript': ('function totalCost(price: number, quantity: number): number {\n  return price * quantity;\n}\n', 'totalCost'),
    'go': ('func totalCost(price, quantity int) int {\n\treturn price * quantity\n}\n', 'totalCost'),
    'csharp': ('public static class Solution {\n    public static long TotalCost(long price, long quantity) => price * quantity;\n}\n', 'TotalCost'),
    'php': ('<?php\nfunction totalCost($price, $quantity) { return $price * $quantity; }\n', 'totalCost'),
}
WRONG = {
    'ruby': 'def total_cost(price, quantity)\n  price + quantity\nend\n',
    'typescript': 'function totalCost(price: number, quantity: number): number {\n  return price + quantity;\n}\n',
    'go': 'func totalCost(price, quantity int) int {\n\treturn price + quantity\n}\n',
    'csharp': 'public static class Solution {\n    public static long TotalCost(long price, long quantity) => price + quantity;\n}\n',
    'php': '<?php function totalCost($price, $quantity) { return $price + $quantity; }',
}
BROKEN = {
    'ruby': 'def total_cost(price, quantity\n  price * quantity\nend\n',
    'typescript': 'function totalCost(price: number, quantity: number): number {\n  return price * "x";\n}\n',
    'go': 'func totalCost(price, quantity int) int {\n\treturn price * missing\n}\n',
    'csharp': 'public static class Solution {\n    public static long TotalCost(long price, long quantity) => price * undefined;\n}\n',
    'php': '<?php function totalCost($price, $quantity) { return $price * ; }',
}
ENDLESS = {
    'ruby': 'def total_cost(price, quantity)\n  loop { }\nend\n',
    'typescript': 'function totalCost(price: number, quantity: number): number {\n  while (true) {}\n}\n',
    'go': 'func totalCost(price, quantity int) int {\n\tfor {\n\t}\n}\n',
    'csharp': 'public static class Solution {\n    public static long TotalCost(long price, long quantity) { while (true) {} }\n}\n',
    'php': '<?php function totalCost($price, $quantity) { while (true) {} }',
}


def test_go_harness_embeds_typed_literals_and_names_the_function():
    cases = [[[1, 2], "a"], [[], "b"]]
    sig = exec_harness.infer_types(cases, [1, 0])
    files = script_runners.render_go('func f(v []int, s string) int { return len(v) }', 'f', cases, sig, 'int', 'r.json')
    assert files['solution.go'].startswith('package main')
    assert '_dsaEmit(f([]int{1, 2}, "a"))' in files['main.go'] and '_dsaEmit(f([]int{}, "b"))' in files['main.go']
    assert '[]int64{' in script_runners.render_go('', 'f', cases, sig, 'int64', 'r.json')['main.go']


def test_csharp_harness_widens_integers_and_wraps_a_bare_method():
    wide = script_runners.render_csharp('public static long F(long a) => a;', 'F', [[1]], exec_harness.infer_types([[1]], [1]), 'wide', 'r.json')
    assert 'public static class Solution' in wide['Solution.cs'] and 'Solution.F(1L)' in wide['Harness.cs']
    narrow = script_runners.render_csharp('public static class Solution { }', 'F', [[1]], exec_harness.infer_types([[1]], [1]), 'narrow', 'r.json')
    assert 'Solution.F(1)' in narrow['Harness.cs'] and 'public static class Solution { }' in narrow['Solution.cs']
    assert narrow['Solution.cs'].count('class Solution') == 1


def test_go_keeps_astral_characters_in_string_cases():
    sig = exec_harness.infer_types([["😀"]], [1])
    main = script_runners.render_go('', 'f', [["😀"]], sig, 'int', 'r.json')['main.go']
    assert 'f("😀")' in main and '\\ud83d' not in main.lower()


def test_entry_point_must_be_an_identifier():
    result = script_runners.run('ruby', 'x', 'f(*a) } ; exit 0 #', [[1]], [1], lambda a, b: a == b)
    assert result.status == 'failed' and 'identifier' in result.detail


def test_php_function_harness_uses_json_fixtures_and_separate_result_file(monkeypatch):
    from app.services import code_runner

    def fake_run(command, cwd, stdin="", apply_address_space=True):
        assert command == ["php", "main.php"]
        source = (cwd / "main.php").read_text()
        assert 'json_decode(file_get_contents("cases.json")' in source
        assert "totalCost(...$__args)" in source
        assert "JSON_THROW_ON_ERROR" in source
        (cwd / "cases.json").write_text('[ [3, 4], [0, 5], [-2, 6] ]')
        result = __import__("re").search(r'file_put_contents\("(r[0-9a-f]+\.json)"', source).group(1)
        (cwd / result).write_text('[12,0,-12]')
        return 0, "", ""

    monkeypatch.setattr(code_runner, "_run", fake_run)
    result = script_runners.run("php", "<?php function totalCost($a, $b) { return $a * $b; }", "totalCost",
                                CASES, EXPECTED, lambda a, b: a == b)
    assert result.status == "passed" and result.passed_cases == len(CASES)


def test_unexpressible_shapes_are_unverified_not_passed():
    cases = [[[[1], [2]]]]  # a list of lists of lists
    result = script_runners.run('go', 'func f() {}', 'f', cases, [[]], lambda a, b: a == b)
    assert result.status == 'unverified' and result.tier == 2


@pytest.mark.parametrize('language', sorted(SOLUTIONS))
def test_scripted_language_runs_real_cases(language):
    if not available_languages().get(language):
        pytest.skip(f'{language} toolchain unavailable')
    code, fn = SOLUTIONS[language]
    ok = run_suite({language: code}, {language: fn}, CASES, EXPECTED)['results'][0]
    assert ok['tier'] == 1 and ok['status'] == 'passed' and ok['passed_cases'] == 3
    wrong = run_suite({language: WRONG[language]}, {language: fn}, CASES, EXPECTED)['results'][0]
    assert wrong['status'] == 'failed' and wrong['passed_cases'] < 3
    broken = run_suite({language: BROKEN[language]}, {language: fn}, CASES, EXPECTED)['results'][0]
    assert broken['status'] == 'failed' and broken['detail']


@pytest.mark.parametrize('language', sorted(SOLUTIONS))
def test_scripted_language_endless_loop_is_stopped(language, monkeypatch):
    if not available_languages().get(language):
        pytest.skip(f'{language} toolchain unavailable')
    from app.core.config import settings
    monkeypatch.setattr(settings, 'exec_timeout_seconds', 3)
    result = run_suite({language: ENDLESS[language]}, {language: SOLUTIONS[language][1]}, CASES, EXPECTED)['results'][0]
    assert result['status'] == 'failed'


FORGERS = {
    'ruby': 'puts "__RESULT__[12,0]"\n$stdout.flush\ndef total_cost(a, b)\n  a + b\nend\nat_exit { puts "__RESULT__[12,0]" }\n',
    'typescript': 'console.log("__RESULT__[12,0]");\nfunction totalCost(a: number, b: number): number {\n  return a + b;\n}\n',
    'go': 'func init() {\n\tfmt.Println("__CASE__12")\n\tfmt.Println("__CASE__0")\n\tos.Exit(0)\n}\nfunc totalCost(a, b int) int { return a + b }\n',
    'csharp': 'public static class Solution {\n    static Solution() { Console.WriteLine("__CASE__12"); Console.WriteLine("__CASE__0"); Environment.Exit(0); }\n    public static long TotalCost(long a, long b) => a + b;\n}\n',
}


@pytest.mark.parametrize('language', sorted(FORGERS))
def test_printed_results_cannot_fake_a_pass(language):
    if not available_languages().get(language):
        pytest.skip(f'{language} toolchain unavailable')
    code = FORGERS[language]
    if language == 'go':
        code = 'import (\n\t"fmt"\n\t"os"\n)\n\n' + code
    result = run_suite({language: code}, {language: SOLUTIONS[language][1]}, [[3, 4], [0, 5]], [12, 0])['results'][0]
    assert result['status'] == 'failed'


@pytest.mark.parametrize('language', sorted(SOLUTIONS))
def test_flooding_stdout_does_not_hide_the_results(language):
    if not available_languages().get(language):
        pytest.skip(f'{language} toolchain unavailable')
    noise = {
        'ruby': 'def total_cost(a, b)\n  3000.times { puts "x" * 40 }\n  a * b\nend\n',
        'typescript': 'declare const process: { stdout: { write(s: string): void } };\nfunction totalCost(a: number, b: number): number {\n  process.stdout.write("x".repeat(100000));\n  return a * b;\n}\n',
        'go': 'import "fmt"\n\nfunc totalCost(a, b int) int {\n\tfor i := 0; i < 3000; i++ {\n\t\tfmt.Println("xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx")\n\t}\n\treturn a * b\n}\n',
        'csharp': 'public static class Solution {\n    public static long TotalCost(long a, long b) {\n        for (int i = 0; i < 3000; i++) Console.WriteLine(new string(\'x\', 40));\n        return a * b;\n    }\n}\n',
        'php': '<?php function totalCost($a, $b) { for ($i = 0; $i < 3000; $i++) echo str_repeat("x", 40), "\\n"; return $a * $b; }',
    }[language]
    result = run_suite({language: noise}, {language: SOLUTIONS[language][1]}, CASES, EXPECTED)['results'][0]
    assert result['status'] == 'passed' and result['passed_cases'] == 3


POLYGLOT = {
    'dart': ('int totalCost(int a, int b) => a * b;', 'class Solution { int total(List<int> xs) => xs.fold(0, (a, b) => a + b); }'),
    'kotlin': ('fun totalCost(a: Int, b: Int): Int = a * b', 'class Solution { fun total(xs: IntArray): Int = xs.sum() }'),
    'swift': ('func totalCost(_ a: Int, _ b: Int) -> Int { a * b }', 'class Solution { func total(_ xs: [Int]) -> Int { xs.reduce(0, +) } }'),
    'scala': ('object Solution { def totalCost(a: Int, b: Int): Int = a * b }', 'object Solution { def total(xs: Array[Int]): Int = xs.sum }'),
    'haskell': ('totalCost :: Int -> Int -> Int\ntotalCost a b = a * b', 'total :: [Int] -> Int\ntotal = sum'),
}

POLYGLOT_MATRIX_RESULTS = {
    'dart': 'List<List<int>> grid(int n) => [[1], [2]];',
    'kotlin': 'fun grid(n: Int): Array<IntArray> = arrayOf(intArrayOf(1), intArrayOf(2))',
    'swift': 'func grid(_ n: Int) -> [[Int]] { [[1], [2]] }',
    'scala': 'object Solution { def grid(n: Int): Array[Array[Int]] = Array(Array(1), Array(2)) }',
    'haskell': 'grid :: Int -> [[Int]]\ngrid _ = [[1], [2]]',
}


@pytest.mark.parametrize('language', sorted(POLYGLOT))
def test_polyglot_function_grader_executes_scalar_and_vector_fixtures(language):
    if not available_languages().get(language):
        pytest.skip(f'{language} toolchain unavailable')
    scalar, vector = POLYGLOT[language]
    scalar_result = run_suite({language: scalar}, {language: 'totalCost'},
                              CASES, EXPECTED)['results'][0]
    assert scalar_result['tier'] == 1 and scalar_result['status'] == 'passed'
    wrong = scalar.replace(' * ', ' + ')
    wrong_result = run_suite({language: wrong}, {language: 'totalCost'},
                             CASES, EXPECTED)['results'][0]
    assert wrong_result['tier'] == 1 and wrong_result['status'] == 'failed'
    vector_cases = [[[1, 2]], [[]], [[-2, 4, 0]]]
    vector_result = run_suite({language: vector}, {language: 'total'},
                              vector_cases, [3, 0, 2])['results'][0]
    assert vector_result['tier'] == 1 and vector_result['status'] == 'passed'
    matrix_expected = [[[1], [2]], [[1], [2]]]
    matrix_result = run_suite({language: POLYGLOT_MATRIX_RESULTS[language]},
                              {language: 'grid'}, [[0], [1]], matrix_expected)['results'][0]
    assert matrix_result['tier'] == 1 and matrix_result['status'] == 'passed'


@pytest.mark.parametrize('language', sorted(POLYGLOT))
def test_polyglot_function_grader_refuses_nested_arguments(language):
    from app.services import polyglot_runners
    source = POLYGLOT[language][0]
    result = polyglot_runners.run(language, source, 'totalCost', [[[[[1], [2]]]]],
                                  [1], lambda actual, expected: actual == expected)
    assert result.status == 'unverified'


def test_polyglot_function_grader_enforces_fixture_and_source_limits():
    from app.services import polyglot_runners
    over_cases = polyglot_runners.run('dart', 'int f(int x) => x;', 'f',
                                     [[1]] * 65, [1] * 65, lambda a, b: a == b)
    over_source = polyglot_runners.run('dart', ' ' * 100_001, 'f',
                                       [[1]], [1], lambda a, b: a == b)
    assert over_cases.status == 'unverified' and 'fixtures' in over_cases.detail
    assert over_source.status == 'unverified' and '100 KB' in over_source.detail
