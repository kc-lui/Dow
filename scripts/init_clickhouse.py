"""Apply db/init/*.sql to ClickHouse. Idempotent, create-only (no DROP/TRUNCATE)."""
import os
import re
import sys
from pathlib import Path

import clickhouse_connect

SQL_DIR = Path(__file__).resolve().parent.parent / "db" / "init"
FORBIDDEN = re.compile(r"\b(DROP|TRUNCATE)\b", re.IGNORECASE)
DATABASE = "dow"


def strip_comments(sql: str) -> str:
    return "\n".join(line.split("--", 1)[0] for line in sql.splitlines())


def split_statements(sql: str) -> list[str]:
    return [s.strip() for s in strip_comments(sql).split(";") if s.strip()]


def main() -> int:
    client = clickhouse_connect.get_client(
        host=os.getenv("CLICKHOUSE_HOST", "localhost"),
        port=int(os.getenv("CLICKHOUSE_PORT", "8123")),
        username=os.getenv("CLICKHOUSE_USER", "trading_user"),
        password=os.getenv("CLICKHOUSE_PASSWORD", "trading_secret"),
    )
    password = os.getenv("DOW_CLICKHOUSE_PASSWORD", "dow_secret")
    statements = [
        s.replace("${DOW_CLICKHOUSE_PASSWORD}", password.replace("'", "\\'"))
        for f in sorted(SQL_DIR.glob("*.sql"))
        for s in split_statements(f.read_text())
    ]
    for stmt in statements:  # validate all before executing any
        if FORBIDDEN.search(stmt):
            print(f"REFUSED (DROP/TRUNCATE found): {stmt[:80]}...", file=sys.stderr)
            return 1
    for stmt in statements:
        client.command(stmt)
    print(f"Applied {len(statements)} statements")
    print(f"SHOW TABLES FROM {DATABASE}")
    for (name,) in client.query(f"SHOW TABLES FROM {DATABASE}").result_rows:
        print(f"  {name}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
