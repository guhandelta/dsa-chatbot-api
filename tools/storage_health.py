#!/usr/bin/env python3
"""Read-only ledger/approval audit and non-destructive SQLite backup tooling.

Backups contain private learner data. Store the destination with the same care
as the source database. Restore writes only to a NEW destination, never in place.
"""
import argparse
import hashlib
import json
import os
import sqlite3
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))


def database_path():
    from sqlalchemy.engine import make_url
    from app.core.config import settings
    url = make_url(settings.resolved_database_url)
    if not url.drivername.startswith('sqlite'):
        raise ValueError('Use database-native backup tooling for PostgreSQL')
    return Path(url.database).resolve()


def audit(path):
    with sqlite3.connect(path.as_uri()+'?mode=ro', uri=True) as conn:
        conn.row_factory = sqlite3.Row
        mismatches = [dict(row) for row in conn.execute('''
            SELECT u.id AS user_id, u.peppercorns AS balance, COALESCE(SUM(t.amount),0) AS ledger_balance
            FROM users u LEFT JOIN transactions t ON t.user_id=u.id GROUP BY u.id,u.peppercorns
            HAVING u.peppercorns != COALESCE(SUM(t.amount),0)''')]
        counts = dict(conn.execute('SELECT status,COUNT(*) FROM knowledge_documents GROUP BY status'))
        return {'integrity': conn.execute('PRAGMA integrity_check').fetchone()[0],
                'ledger_mismatches': mismatches, 'knowledge_documents': counts}


def copy_database(source, destination):
    source, destination = Path(source).resolve(), Path(destination).resolve()
    destination.parent.mkdir(parents=True, exist_ok=True)
    # O_EXCL prevents accidental overwriting, including symlinks.
    fd = os.open(destination, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    os.close(fd)
    try:
        with sqlite3.connect(source.as_uri()+'?mode=ro', uri=True) as src, sqlite3.connect(destination) as dst:
            src.backup(dst)
            if dst.execute('PRAGMA integrity_check').fetchone()[0] != 'ok':
                raise ValueError('Copied database failed integrity check')
        return {'file': str(destination), 'sha256': hashlib.sha256(destination.read_bytes()).hexdigest(),
                'bytes': destination.stat().st_size}
    except BaseException:
        destination.unlink(missing_ok=True)
        raise


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=['audit', 'backup', 'restore'])
    parser.add_argument('--source', type=Path)
    parser.add_argument('--destination', type=Path)
    args = parser.parse_args()
    source = args.source or database_path()
    if args.action == 'audit':
        report = audit(source)
    else:
        if not args.destination:
            parser.error('--destination is required')
        report = copy_database(source, args.destination)
    print(json.dumps(report, indent=2))
    return 1 if report.get('integrity', 'ok') != 'ok' or report.get('ledger_mismatches') else 0


if __name__ == '__main__':
    raise SystemExit(main())
