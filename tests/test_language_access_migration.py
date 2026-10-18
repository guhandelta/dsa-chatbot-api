"""Upgrade an existing database without guessing the language of old chats."""
from pathlib import Path
import sqlite3
from alembic import command
from alembic.config import Config
from app.core.config import settings


def test_upgrade_preserves_existing_chats_and_supports_rollback(tmp_path,monkeypatch):
    path=tmp_path/'existing.db'
    monkeypatch.setattr(settings,'database_url','sqlite+aiosqlite:///'+str(path))
    root=Path(__file__).resolve().parents[1]
    config=Config(str(root/'alembic.ini'));config.set_main_option('script_location',str(root/'alembic'))
    command.upgrade(config,'0008_upload_language')
    with sqlite3.connect(path) as db:
        db.execute("INSERT INTO users (id,email,hashed_password,peppercorns,role,preferred_language,status,strikes,suspended_reason,created_at) VALUES ('owner','owner@example.com','unused',50,'student','java','active',0,'','2026-10-17')")
        db.execute("INSERT INTO chat_threads (id,user_id,title,created_at) VALUES ('old-thread','owner','Keep this history','2026-10-17')")
    command.upgrade(config,'head')
    with sqlite3.connect(path) as db:
        assert db.execute("SELECT title,language,subject,track FROM chat_threads WHERE id='old-thread'").fetchone()==('Keep this history','','','dsa')
        assert {c[1] for c in db.execute('PRAGMA table_info(instructor_languages)')}=={'user_id','language','assigned_by','created_at'}
    command.downgrade(config,'0008_upload_language')
    with sqlite3.connect(path) as db:
        assert db.execute("SELECT title FROM chat_threads WHERE id='old-thread'").fetchone()==('Keep this history',)
    command.upgrade(config,'head')
