import sqlite3
from pathlib import Path

from alembic import command
from alembic.config import Config

from app.core.config import settings


def test_section_entitlement_migration_preserves_language_subscriptions(tmp_path, monkeypatch):
    path = tmp_path / 'section-entitlements.db'
    monkeypatch.setattr(settings, 'database_url', 'sqlite+aiosqlite:///' + str(path))
    root = Path(__file__).resolve().parents[1]
    config = Config(str(root / 'alembic.ini'))
    config.set_main_option('script_location', str(root / 'alembic'))
    command.upgrade(config, '0022_student_path_records')
    with sqlite3.connect(path) as db:
        db.execute("INSERT INTO users (id,email,hashed_password,peppercorns,role,preferred_language,status,strikes,suspended_reason,created_at,profile_generation) VALUES ('owner','owner@example.com','unused',0,'student','javascript','active',0,'','2026-11-09',0)")
        db.execute("INSERT INTO subscriptions (id,user_id,language,status,started_at,expires_at,provider_ref,provider_event_timestamp) VALUES ('old','owner','javascript','active','2026-11-01','2026-12-01','',0)")
    command.upgrade(config, 'head')
    with sqlite3.connect(path) as db:
        assert 'section_entitlements' in {row[0] for row in db.execute("SELECT name FROM sqlite_master WHERE type='table'")}
        assert db.execute('SELECT language FROM subscriptions').fetchone() == ('javascript',)
    command.downgrade(config, '0022_student_path_records')
    with sqlite3.connect(path) as db:
        assert 'section_entitlements' not in {row[0] for row in db.execute("SELECT name FROM sqlite_master WHERE type='table'")}
        assert db.execute('SELECT language FROM subscriptions').fetchone() == ('javascript',)
