from tools.check_migration_drift import migration_columns


def test_literal_loop_added_understanding_columns():
    columns = migration_columns()
    assert "understanding_json" in columns["quiz_answers"]
    assert "understanding_json" in columns["debug_challenge_attempts"]
