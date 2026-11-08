# Dow database (`dow`)

ClickHouse database for the Dow Theory project. Schema: `db/init/01_schema.sql`.
Naming follows `~/.claude/db_naming_convention.md`.

## Tables

| Table | Purpose | Partition |
|---|---|---|
| `mkt_klines` | Daily OHLCV bars (indices, ETFs), with source | month of `ts_open` |
| `str_swing_log` | Confirmed swing highs/lows per method, threshold, scale | year of `ts` |
| `str_trend_state_snapshots` | Trend state per index and pair, JSON payload | year of `ts` |
| `str_level_log` | Support, resistance, trendline and defense levels | year of `ts` |
| `str_rule_backtest_log` | Rule evidence ledger: metrics, CI, p-value, labels, hashes | none |
| `ops_data_quality_log` | Integrity check findings | month of `ts` |

All tables use `ReplacingMergeTree(inserted_at)`. Prices are `Decimal(12, 4)`, no `Float*`.

## Read rule

Duplicates survive until a background merge. Every analytic read must use `FINAL`:

```sql
SELECT * FROM dow.mkt_klines FINAL WHERE symbol = 'DJI' AND interval = '1d';
```

Swings carry `confirmed_ts`. Downstream code may only use rows with `confirmed_ts` at or before the evaluation bar.

## Write scope

Write only to the `dow` database. `usstock`, `twstock`, `trading` and `twdaytrade` are off limits.
The init script refuses any statement containing `DROP` or `TRUNCATE`.

## Re-run init

Safe to repeat, all statements are `CREATE ... IF NOT EXISTS`.

```bash
.venv/bin/python scripts/init_clickhouse.py
```

Env overrides: `CLICKHOUSE_HOST` (localhost), `CLICKHOUSE_PORT` (8123), `CLICKHOUSE_USER` (trading_user), `CLICKHOUSE_PASSWORD`.
Schema changes go in a new numbered file (for example `02_*.sql`), not in edits to applied tables.
