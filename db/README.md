# Dow database (`dow`)

ClickHouse database for the Dow Theory project. Schema: `db/init/01_schema.sql`.
Naming follows `~/.claude/db_naming_convention.md`.

## Tables

| Table | Purpose | Partition |
|---|---|---|
| `mkt_klines` | Daily OHLCV bars (indices, ETFs), with source | year of `ts_open` |
| `str_swing_log` | Confirmed swing highs/lows per method, threshold, scale | year of `ts` |
| `str_trend_state_snapshots` | Trend state per index and pair, JSON payload | year of `ts` |
| `str_level_log` | Support, resistance, trendline and defense levels | year of `ts` |
| `str_rule_backtest_log` | Rule evidence ledger: metrics, CI, p-value, labels, hashes | none |
| `ops_data_quality_log` | Integrity check findings, grouped by `run_id` (plain MergeTree, never deduplicated) | month of `ts` |

All tables except `ops_data_quality_log` use `ReplacingMergeTree(inserted_at)`. Prices are `Decimal(12, 4)`, no `Float*`.

## Read rule

Duplicates survive until a background merge. Every analytic read must use `FINAL`:

```sql
SELECT * FROM dow.mkt_klines FINAL WHERE symbol = 'DJI' AND interval = '1d';
```

Swings carry `confirmed_ts`. Downstream code may only use rows with `confirmed_ts` at or before the evaluation bar.

## Write scope

Write only to the `dow` database. `usstock`, `twstock`, `trading` and `twdaytrade` are off limits.
Two layers enforce it:

1. **Server**: user `dow_user` (`db/init/02_users.sql`) has `SELECT, INSERT, ALTER DELETE, ALTER UPDATE,
   CREATE TABLE, OPTIMIZE` on `dow.*` and `SELECT` on `usstock.*` and `twstock.*`. Nothing else: no DROP,
   TRUNCATE, RENAME or GRANT. The package never uses the admin account.
2. **Client** (`src/dowtheory/storage/sql_guard.py`): `command()` accepts only `INSERT INTO dow.`,
   `ALTER TABLE dow.<t> DELETE|UPDATE`, `OPTIMIZE TABLE dow.`, `CREATE TABLE|DATABASE IF NOT EXISTS dow`,
   `EXCHANGE TABLES dow.a AND dow.b`. `query_df()` accepts reads only and sends `readonly=1`. Comments are
   stripped and string literals blanked before checking. Qualified names outside `dow` (writes) or
   `dow/usstock/twstock` (reads) raise, as do `;`, DROP, TRUNCATE, RENAME, DETACH, ATTACH, TTL, GRANT, SYSTEM.
   Table aliases that are referenced as `alias.column` must be declared with `AS`.

`ALTER TABLE ... DELETE` is asynchronous; add `SETTINGS mutations_sync = 2` to wait for it.

## Close-only history

Yahoo serves `open = high = low = close` bars before 1962-07-02 (`^GSPC`) and 1984-10-11 (`^IXIC`).
They are stored but flagged (`flat_bar`), and `data.analysis_start` in `configs/dow.yaml` makes
`load_klines` clip to the first real-OHLC date. Override with `dow --ignore-analysis-start ...`.

## Migrations and legacy tables

`scripts/migrate_p2_review.py` (admin account, idempotent) moved existing databases to yearly
partitions and the MergeTree audit log by `CREATE ... _v2`, `INSERT SELECT`, `EXCHANGE TABLES`.
The superseded tables remain as `dow.mkt_klines_v2` and `dow.ops_data_quality_log_v2` (no DROP is ever
issued; remove them manually when no longer needed). Fresh installs do not have them.

## Re-run init

Safe to repeat, all statements are `CREATE ... IF NOT EXISTS`.

```bash
.venv/bin/python scripts/init_clickhouse.py
```

Init runs with the admin account (`CLICKHOUSE_USER`, `CLICKHOUSE_PASSWORD`; defaults `trading_user`) and substitutes `DOW_CLICKHOUSE_PASSWORD` (default `dow_secret`) into `02_users.sql`. Package access uses `DOW_CLICKHOUSE_USER` / `DOW_CLICKHOUSE_PASSWORD`. See `.env.example`.
Schema changes go in a new numbered file (for example `03_*.sql`), not in edits to applied tables.
