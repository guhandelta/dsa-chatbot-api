"""Existing hints retain billing facts through migration and rollback."""
from pathlib import Path
import sqlite3

from alembic import command
from alembic.config import Config

from app.core.config import settings


def test_hint_backfill_and_thread_pins_upgrade_and_rollback(tmp_path, monkeypatch):
    path = tmp_path / "existing-hints.db"
    monkeypatch.setattr(settings, "database_url", "sqlite+aiosqlite:///" + str(path))
    root = Path(__file__).resolve().parents[1]
    config = Config(str(root / "alembic.ini"))
    config.set_main_option("script_location", str(root / "alembic"))
    command.upgrade(config, "0013_study_notes")
    with sqlite3.connect(path) as db:
        db.execute("INSERT INTO users (id,email,hashed_password,peppercorns,role,preferred_language,status,strikes,suspended_reason,created_at) VALUES ('owner','owner@example.com','unused',50,'student','python','active',0,'','2026-10-19')")
        db.execute("INSERT INTO learning_events (id,user_id,problem_id,kind,language,algorithms,error_category,detail,hint_tier,reasoning,created_at) VALUES ('old-hint','owner','two-sum','hint','python','','','',3,'personal reasoning','2026-10-19')")
        db.execute("INSERT INTO chat_threads (id,user_id,title,language,subject,track,created_at) VALUES ('old-thread','owner','Keep history','python','','study-explain','2026-10-19')")
    command.upgrade(config, "head")
    command.upgrade(config, "head")
    with sqlite3.connect(path) as db:
        assert db.execute("SELECT event_id,tier,operation_id FROM hint_usage").fetchall() == [("old-hint", 3, None)]
        assert "reasoning" not in {column[1] for column in db.execute("PRAGMA table_info(hint_usage)")}
        assert db.execute("SELECT profile_generation FROM users").fetchone() == (0,)
        assert db.execute("SELECT study_focus_id,compare_language,title FROM chat_threads").fetchone() == ("", "", "Keep history")
    command.downgrade(config, "0013_study_notes")
    with sqlite3.connect(path) as db:
        assert db.execute("SELECT reasoning FROM learning_events").fetchone() == ("personal reasoning",)
        assert "profile_generation" not in {column[1] for column in db.execute("PRAGMA table_info(users)")}
    command.upgrade(config, "head")
    with sqlite3.connect(path) as db:
        assert db.execute("SELECT count(*) FROM hint_usage").fetchone() == (1,)
