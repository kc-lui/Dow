"""One-off migration for DBs created before the P2 review: new partitioning and audit log.

Runs with the ADMIN account (CLICKHOUSE_USER / CLICKHOUSE_PASSWORD, default trading_user)
because EXCHANGE TABLES needs more than dow_user's grants. Every statement is validated with
the project allowlist (dow only, no DROP/TRUNCATE/RENAME). Idempotent: skips finished steps.

After the run, the OLD tables remain as ``dow.mkt_klines_v2`` and
``dow.ops_data_quality_log_v2`` (no DROP is ever issued; delete them by hand if wanted).
"""
import os
import sys
from pathlib import Path

import clickhouse_connect

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from dowtheory.storage.sql_guard import check_write

KLINES_V2_DDL = """CREATE TABLE IF NOT EXISTS dow.mkt_klines_v2
(
    exchange LowCardinality(String), symbol LowCardinality(String), interval LowCardinality(String),
    ts_open DateTime64(3, 'America/New_York'), ts_close DateTime64(3, 'America/New_York'),
    open Decimal(12, 4), high Decimal(12, 4), low Decimal(12, 4), close Decimal(12, 4),
    volume UInt64, source LowCardinality(String),
    inserted_at DateTime64(3, 'UTC') DEFAULT now64(3)
)
ENGINE = ReplacingMergeTree(inserted_at)
PARTITION BY toYear(ts_open)
ORDER BY (symbol, interval, ts_open)
SETTINGS index_granularity = 8192"""

OPS_V2_DDL = """CREATE TABLE IF NOT EXISTS dow.ops_data_quality_log_v2
(
    ts DateTime64(3, 'UTC'), symbol LowCardinality(String), check_name LowCardinality(String),
    severity LowCardinality(String), detail String,
    bar_ts DateTime64(3, 'America/New_York') DEFAULT toDateTime64(0, 3),
    inserted_at DateTime64(3, 'UTC') DEFAULT now64(3), run_id String
)
ENGINE = MergeTree
PARTITION BY toYYYYMM(ts)
ORDER BY (symbol, check_name, ts, run_id)
SETTINGS index_granularity = 8192"""


def run(client, sql: str) -> None:
    check_write(sql)
    client.command(sql)


def engine_info(client, table: str) -> tuple[str, str]:
    rows = client.query(
        "SELECT engine, partition_key FROM system.tables WHERE database = 'dow' AND name = %(t)s",
        parameters={"t": table}).result_rows
    return rows[0] if rows else ("", "")


def migrate_klines(client) -> None:
    _engine, key = engine_info(client, "mkt_klines")
    if key == "toYear(ts_open)":
        print("mkt_klines already partitioned by year")
        return
    run(client, KLINES_V2_DDL)
    for lo in range(1890, 2030, 10):  # <= 10 yearly partitions per insert block
        run(client, "INSERT INTO dow.mkt_klines_v2 SELECT * FROM dow.mkt_klines FINAL "
                    f"WHERE toYear(ts_open) BETWEEN {lo} AND {lo + 9}")
    old = client.query("SELECT count() FROM dow.mkt_klines FINAL").result_rows[0][0]
    new = client.query("SELECT count() FROM dow.mkt_klines_v2 FINAL").result_rows[0][0]
    if old != new:
        raise RuntimeError(f"mkt_klines copy mismatch: {old} != {new}")
    run(client, "EXCHANGE TABLES dow.mkt_klines AND dow.mkt_klines_v2")
    print(f"mkt_klines migrated ({new} rows); old table kept as dow.mkt_klines_v2")


def migrate_ops_log(client) -> None:
    cols = client.query("SELECT name FROM system.columns WHERE database = 'dow' "
                        "AND table = 'ops_data_quality_log'").result_rows
    if ("run_id",) in cols or any(c[0] == "run_id" for c in cols):
        print("ops_data_quality_log already has run_id")
        return
    run(client, OPS_V2_DDL)
    run(client, "INSERT INTO dow.ops_data_quality_log_v2 (ts, symbol, check_name, severity, detail, "
                "bar_ts, inserted_at, run_id) SELECT ts, symbol, check_name, severity, detail, "
                "bar_ts, inserted_at, 'legacy' FROM dow.ops_data_quality_log")
    old = client.query("SELECT count() FROM dow.ops_data_quality_log").result_rows[0][0]
    new = client.query("SELECT count() FROM dow.ops_data_quality_log_v2").result_rows[0][0]
    if old != new:
        raise RuntimeError(f"ops log copy mismatch: {old} != {new}")
    run(client, "EXCHANGE TABLES dow.ops_data_quality_log AND dow.ops_data_quality_log_v2")
    print(f"ops_data_quality_log migrated ({new} rows, run_id='legacy')")


def main() -> int:
    client = clickhouse_connect.get_client(
        host=os.getenv("CLICKHOUSE_HOST", "localhost"),
        port=int(os.getenv("CLICKHOUSE_PORT", "8123")),
        username=os.getenv("CLICKHOUSE_USER", "trading_user"),
        password=os.getenv("CLICKHOUSE_PASSWORD", "trading_secret"),
        database="dow",
    )
    try:
        migrate_klines(client)
        migrate_ops_log(client)
    finally:
        client.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
