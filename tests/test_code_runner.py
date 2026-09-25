# The execution harness is the safety net behind auto-publish, so it gets
# real tests: correct code passes, wrong logic fails, broken code fails to
# compile, infinite loops time out, missing toolchains are never "passed".
from app.services.code_runner import available_languages, run_suite

GOOD_PY = (
    "def two_sum(nums, target):\n"
    "    seen = {}\n"
    "    for i, x in enumerate(nums):\n"
    "        if target - x in seen:\n"
    "            return [seen[target - x], i]\n"
    "        seen[x] = i\n"
    "    return []"
)
GOOD_JS = (
    "function twoSum(nums, target) {\n"
    "  const m = new Map();\n"
    "  for (let i = 0; i < nums.length; i++) {\n"
    "    if (m.has(target - nums[i])) return [m.get(target - nums[i]), i];\n"
    "    m.set(nums[i], i);\n"
    "  }\n"
    "  return [];\n"
    "}"
)
WRONG_PY = "def two_sum(nums, target):\n    return [0, 1]"
BROKEN_C = "int* twoSum(int* nums, int n, int t, int* rs) { no_such_fn(); return 0; }"
LOOP_PY = "def two_sum(nums, target):\n    while True:\n        pass"

CASES = [[[2, 7, 11, 15], 9], [[3, 2, 4], 6]]
EXPECTED = [[0, 1], [1, 2]]
FN = {"python": "two_sum", "javascript": "twoSum"}


def test_correct_solutions_pass_and_agree():
    r = run_suite({"python": GOOD_PY, "javascript": GOOD_JS}, FN, CASES, EXPECTED)
    assert r["can_publish"] is True
    assert r["agreement"] is True
    assert all(x["status"] == "passed" for x in r["results"])


def test_wrong_logic_blocks_publish():
    r = run_suite({"python": WRONG_PY, "javascript": GOOD_JS}, FN, CASES, EXPECTED)
    assert r["can_publish"] is False
    py = next(x for x in r["results"] if x["language"] == "python")
    assert py["status"] == "failed"
    assert py["passed_cases"] < py["total_cases"]


def test_cross_language_disagreement_detected():
    r = run_suite({"python": WRONG_PY, "javascript": GOOD_JS}, FN, CASES, EXPECTED)
    assert r["agreement"] is False


def test_uncompilable_c_blocks_publish():
    r = run_suite(
        {"python": GOOD_PY, "javascript": GOOD_JS, "c": BROKEN_C}, FN, CASES, EXPECTED
    )
    assert r["can_publish"] is False
    c = next(x for x in r["results"] if x["language"] == "c")
    assert c["status"] == "failed"


def test_infinite_loop_times_out():
    r = run_suite({"python": LOOP_PY}, FN, CASES, EXPECTED)
    assert r["can_publish"] is False
    assert "imed out" in r["results"][0]["detail"]


def test_missing_toolchain_is_unverified_not_passed():
    tools = available_languages()
    missing = next((l for l in ("java", "rust") if not tools.get(l)), None)
    if missing is None:
        return  # both toolchains installed here; nothing to assert
    r = run_suite(
        {"python": GOOD_PY, "javascript": GOOD_JS, missing: "whatever"}, FN, CASES, EXPECTED
    )
    entry = next(x for x in r["results"] if x["language"] == missing)
    assert entry["status"] == "unverified"
    assert missing in r["unverified"]
