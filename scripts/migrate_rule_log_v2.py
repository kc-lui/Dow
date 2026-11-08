"""Rebuild dow.str_rule_backtest_log with metric_name in the sorting key (idempotent).

The old key (rule_id, pair, run_id) made ReplacingMergeTree collapse all metrics of one rule,
pair and run into a single row. Uses the account in CLICKHOUSE_USER / CLICKHOUSE_PASSWORD
(default dow_user / dow_secret; set the admin pair if EXCHANGE TABLES is refused). Every
statement is validated with the project allowlist (no DROP). The old table stays as
``dow.str_rule_backtest_log_v2``.
"""
import os
import sys
from pathlib import Path

import clickhouse_connect

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from dowtheory.storage.sql_guard import check_write

DDL = """CREATE TABLE IF NOT EXISTS dow.str_rule_backtest_log_v2
(
    run_id String, rule_id LowCardinality(String), pair LowCardinality(String),
    period_start Date, period_end Date, n_obs UInt32, metric_name LowCardinality(String),
    metric_value Decimal(12, 6), ci_low Decimal(12, 6), ci_high Decimal(12, 6),
    null_value Decimal(12, 6), p_value Decimal(8, 6), label LowCardinality(String),
    literature_label LowCardinality(String), config_hash String, decision_table_hash String,
    notes String, inserted_at DateTime64(3, 'UTC') DEFAULT now64(3)
)
ENGINE = ReplacingMergeTree(inserted_at)
ORDER BY (rule_id, pair, run_id, metric_name)
SETTINGS index_granularity = 8192"""


def run(client, sql: str) -> None:
    check_write(sql)
    client.command(sql)


def main() -> int:
    client = clickhouse_connect.get_client(
        host=os.getenv("CLICKHOUSE_HOST", "localhost"),
        port=int(os.getenv("CLICKHOUSE_PORT", "8123")),
        username=os.getenv("CLICKHOUSE_USER", "dow_user"),
        password=os.getenv("CLICKHOUSE_PASSWORD", "dow_secret"),
        database="dow",
    )
    try:
        key = client.query(
            "SELECT sorting_key FROM system.tables WHERE database = 'dow' "
            "AND name = 'str_rule_backtest_log'").result_rows[0][0]
        if "metric_name" in key:
            print(f"str_rule_backtest_log already keyed by {key}")
            return 0
        run(client, DDL)
        if client.query("SELECT count() FROM dow.str_rule_backtest_log_v2").result_rows[0][0] == 0:
            run(client, "INSERT INTO dow.str_rule_backtest_log_v2 "
                        "SELECT * FROM dow.str_rule_backtest_log")
        old = client.query("SELECT count() FROM dow.str_rule_backtest_log").result_rows[0][0]
        new = client.query("SELECT count() FROM dow.str_rule_backtest_log_v2").result_rows[0][0]
        if old != new:
            raise RuntimeError(f"copy mismatch: {old} != {new}")
        run(client, "EXCHANGE TABLES dow.str_rule_backtest_log AND dow.str_rule_backtest_log_v2")
        print(f"migrated {new} rows; old table kept as dow.str_rule_backtest_log_v2")
    finally:
        client.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
