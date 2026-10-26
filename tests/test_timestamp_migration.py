"""Legacy rows survive timestamp alignment, including missing timestamps."""
from pathlib import Path
import sqlite3

from alembic import command
from alembic.config import Config
from app.core.config import settings


def test_timestamp_upgrade_backfills_and_matches_metadata(tmp_path, monkeypatch):
    path = tmp_path / 'timestamps.db'
    monkeypatch.setattr(settings, 'database_url', 'sqlite+aiosqlite:///' + str(path))
    root = Path(__file__).resolve().parents[1]
    config = Config(str(root / 'alembic.ini'))
    config.set_main_option('script_location', str(root / 'alembic'))
    command.upgrade(config, '0018_learning_strikes')
    with sqlite3.connect(path) as db:
        db.execute("INSERT INTO users (id,email,hashed_password,peppercorns,role,preferred_language,status,strikes,suspended_reason,profile_generation) VALUES ('legacy','legacy@example.com','unused',50,'student','python','active',0,'',0)")
    command.upgrade(config, 'head')
    command.check(config)
    with sqlite3.connect(path) as db:
        assert db.execute("SELECT created_at FROM users WHERE id='legacy'").fetchone()[0]
        assert next(c for c in db.execute('PRAGMA table_info(users)') if c[1] == 'created_at')[3] == 1
    command.downgrade(config, '0018_learning_strikes')
    with sqlite3.connect(path) as db:
        assert db.execute("SELECT email FROM users WHERE id='legacy'").fetchone()[0] == 'legacy@example.com'
    command.upgrade(config, 'head')
    command.check(config)
