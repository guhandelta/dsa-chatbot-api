"""The new record table upgrades and rolls back without touching old events."""

import sqlite3
from pathlib import Path

from alembic import command
from alembic.config import Config

from app.core.config import settings


def test_student_path_records_migration(tmp_path, monkeypatch):
    path = tmp_path / "student-path-records.db"
    monkeypatch.setattr(settings, "database_url", "sqlite+aiosqlite:///" + str(path))
    root = Path(__file__).resolve().parents[1]
    config = Config(str(root / "alembic.ini"))
    config.set_main_option("script_location", str(root / "alembic"))
    command.upgrade(config, "0021_understanding_checks")
    with sqlite3.connect(path) as db:
        db.execute("INSERT INTO users (id,email,hashed_password,peppercorns,role,preferred_language,status,strikes,suspended_reason,created_at,profile_generation) VALUES ('owner','owner@example.com','unused',0,'student','javascript','active',0,'','2026-11-09',0)")
        db.execute("INSERT INTO learning_events (id,user_id,problem_id,kind,language,algorithms,error_category,detail,hint_tier,reasoning,created_at) VALUES ('old','owner','two-sum','solved','javascript','','','',0,'my reasoning','2026-11-09')")
    command.upgrade(config, "head")
    with sqlite3.connect(path) as db:
        db.execute("INSERT INTO student_path_records (id,user_id,section,language,kind,concept_id,body,curriculum_version,created_at) VALUES ('new','owner','dsa','javascript','goal','','Learn invariants',1,'2026-11-09')")
        assert db.execute("SELECT body FROM student_path_records").fetchone() == ("Learn invariants",)
        assert db.execute("SELECT reasoning FROM learning_events WHERE id='old'").fetchone() == ("my reasoning",)
    command.downgrade(config, "0021_understanding_checks")
    with sqlite3.connect(path) as db:
        assert "student_path_records" not in {row[0] for row in db.execute("SELECT name FROM sqlite_master WHERE type='table'")}
        assert db.execute("SELECT reasoning FROM learning_events WHERE id='old'").fetchone() == ("my reasoning",)
