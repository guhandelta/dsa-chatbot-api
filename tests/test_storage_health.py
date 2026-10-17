import sqlite3
import pytest
from tools.storage_health import audit, copy_database


def test_backup_restore_round_trip_and_overwrite_protection(tmp_path):
    source, backup, restored = [tmp_path / n for n in ('live.db','backup.db','restored.db')]
    with sqlite3.connect(source) as c:
        c.execute('create table knowledge_documents(status text)')
        c.execute("insert into knowledge_documents values ('published')")
        c.execute('create table users(id text,peppercorns integer)')
        c.execute('create table transactions(user_id text,amount integer)')
        c.execute("insert into users values ('one',45)")
        c.executemany('insert into transactions values (?,?)', [('one',50),('one',-5)])
    first = copy_database(source, backup)
    assert len(first['sha256']) == 64
    assert backup.stat().st_mode & 0o777 == 0o600
    with pytest.raises(FileExistsError):
        copy_database(source, backup)
    copy_database(backup, restored)
    assert audit(restored) == {'integrity':'ok','ledger_mismatches':[], 'knowledge_documents':{'published':1}}
    with sqlite3.connect(restored) as c:
        c.execute('update users set peppercorns=99')
    assert audit(restored)['ledger_mismatches'] == [{'user_id':'one','balance':99,'ledger_balance':45}]
    assert audit(source)['ledger_mismatches'] == []
