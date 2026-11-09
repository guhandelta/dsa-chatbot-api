#!/usr/bin/env python3
"""Detect drift between the Alembic migrations and the ORM models.

Compares real COLUMNS only — `relationship()` attributes are Python-side
associations, not database columns, and counting them produces false drift.

Run this in CI: a migration that silently diverges from the models is worse
than no migration at all, because it breaks on first deploy rather than in dev.
"""

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def migration_columns() -> dict[str, set[str]]:
    tables: dict[str, set[str]] = {}
    for path in sorted((ROOT / "alembic" / "versions").glob("*.py")):
        text = path.read_text()
        for m in re.finditer(
            r'op\.create_table\(\s*"(\w+)",(.*?)\n    \)', text, re.DOTALL
        ):
            table, body = m.group(1), m.group(2)
            tables.setdefault(table, set()).update(
                re.findall(r'sa\.Column\(\s*"(\w+)"', body)
            )
        # later revisions may add columns
        for m in re.finditer(
            r'op\.add_column\(\s*"(\w+)",\s*sa\.Column\(\s*"(\w+)"', text
        ):
            tables.setdefault(m.group(1), set()).add(m.group(2))
        # A few migrations add the same column to a fixed tuple of tables.
        # Keep this deliberately narrow; do not try to execute migration code.
        for m in re.finditer(
            r"for (\w+) in \(([^()]+)\):\s*\n\s+op\.add_column\(\1,\s*sa\.Column\(\s*['\"](\w+)['\"]",
            text,
        ):
            table_names = re.findall(r"['\"](\w+)['\"]", m.group(2))
            if not table_names or re.sub(r"['\"]\w+['\"]|[\s,]", "", m.group(2)):
                continue
            for table in table_names:
                tables.setdefault(table, set()).add(m.group(3))
    return tables


def model_columns() -> dict[str, set[str]]:
    text = (ROOT / "app" / "db" / "models.py").read_text()
    tables: dict[str, set[str]] = {}
    for block in re.split(r"\nclass ", text)[1:]:
        tm = re.search(r'__tablename__\s*=\s*"(\w+)"', block)
        if not tm:
            continue
        cols = set()
        for line in block.splitlines():
            m = re.match(r"\s{4}(\w+):\s*Mapped\[", line)
            if not m:
                continue
            # relationship() is a Python association, not a column
            if "relationship(" in line:
                continue
            cols.add(m.group(1))
        tables[tm.group(1)] = cols
    return tables


def main() -> int:
    mig, mod = migration_columns(), model_columns()
    drift = False
    for table in sorted(set(mig) | set(mod)):
        m_cols, o_cols = mig.get(table, set()), mod.get(table, set())
        missing, extra = o_cols - m_cols, m_cols - o_cols
        if missing or extra:
            drift = True
            print(f"  DRIFT  {table}")
            if missing:
                print(f"         in models but not migrated: {sorted(missing)}")
            if extra:
                print(f"         migrated but not in models: {sorted(extra)}")
        else:
            print(f"  OK     {table} ({len(o_cols)} columns)")
    print(
        "\n"
        + (
            "DRIFT DETECTED — add a migration."
            if drift
            else "Migrations match the models."
        )
    )
    return 1 if drift else 0


if __name__ == "__main__":
    sys.exit(main())
