from app.services import learning_path as lp


def test_path_exposes_safe_assessment_profile():
    stage = next(n for n in lp.nodes("typescript") if n["id"] == "typescript:stage-03")
    profile = stage["assessment_profile"]
    assert "mcq" in profile["formats"]
    assert "recognize" in profile["roles"]
    assert profile["runtime_checks"] >= 0
    assert "answer" not in profile and "tests" not in profile
