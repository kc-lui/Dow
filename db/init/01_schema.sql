-- ClickHouse schema for the Dow Theory analysis project
-- Database: dow (isolated from usstock, twstock, trading, twdaytrade)
-- Applied by scripts/init_clickhouse.py. Idempotent: CREATE ... IF NOT EXISTS only.
-- Convention: ~/.claude/db_naming_convention.md (DBA-1 prefix, DBA-3 suffix, DBA-6 times,
--   DBA-8 Decimal for prices, DBA-10 LowCardinality for enum-like columns).
--
-- READ RULE: every table is ReplacingMergeTree(inserted_at). Re-running a loader or a
--   strategy run inserts a newer row for the same sorting key, and the older row survives
--   until a background merge. Analytic reads MUST use FINAL (SELECT ... FROM dow.<t> FINAL)
--   or an argMax(..., inserted_at) aggregate to get exactly-once rows.
--   Never use a bare-table read for integrity checks, features or backtests.
--
-- DEVIATIONS from the brief (documented, none affects semantics):
--   1. PARTITION BY toYear(ts) replaces the non-existent toYYYY(ts). ClickHouse has toYear.
--   2. ops_data_quality_log.bar_ts DEFAULT toDateTime64(0, 3) is kept as specified. The value
--      means "no bar" (epoch). It is a non-Nullable sentinel per DBA-9.
--   3. mkt_klines is partitioned by year (monthly gave ~1200 tiny partitions for 70k rows).
--   4. Table dimension "exchange" in mkt_klines is not in ORDER BY (per brief). A symbol must
--      therefore map to one exchange, otherwise rows from two exchanges would collapse.

CREATE DATABASE IF NOT EXISTS dow;

-- =============================================================================
-- mkt_klines: daily OHLCV bars for indices and ETFs (raw market data)
-- Dedup key: (symbol, interval, ts_open). A reload from another source replaces older rows.
-- =============================================================================
CREATE TABLE IF NOT EXISTS dow.mkt_klines
(
    exchange     LowCardinality(String),        -- 'INDEX', 'NYSEARCA', 'NASDAQ', 'NYSE'
    symbol       LowCardinality(String),
    interval     LowCardinality(String),        -- '1d'
    ts_open      DateTime64(3, 'America/New_York'),
    ts_close     DateTime64(3, 'America/New_York'),
    open         Decimal(12, 4),
    high         Decimal(12, 4),
    low          Decimal(12, 4),
    close        Decimal(12, 4),
    volume       UInt64,
    source       LowCardinality(String),        -- 'yfinance', 'stooq', 'csv'
    inserted_at  DateTime64(3, 'UTC') DEFAULT now64(3)
)
ENGINE = ReplacingMergeTree(inserted_at)
PARTITION BY toYear(ts_open)
ORDER BY (symbol, interval, ts_open)
SETTINGS index_granularity = 8192;

-- =============================================================================
-- str_swing_log: confirmed swing highs and lows per method, threshold and scale
-- ts is the swing extreme time. confirmed_ts is when the swing became knowable
-- (no-lookahead rule: only use rows with confirmed_ts <= evaluation time).
-- =============================================================================
CREATE TABLE IF NOT EXISTS dow.str_swing_log
(
    run_id          String,
    symbol          LowCardinality(String),
    method          LowCardinality(String),
    threshold       Decimal(8, 4),
    scale           LowCardinality(String),     -- 'minor', 'secondary', 'primary'
    kind            LowCardinality(String),     -- 'H' high, 'L' low
    ts              DateTime64(3, 'America/New_York'),
    price           Decimal(12, 4),
    confirmed_ts    DateTime64(3, 'America/New_York'),
    amplitude_pct   Decimal(8, 4),
    retrace_ratio   Decimal(8, 4) DEFAULT 0,
    duration_days   UInt16 DEFAULT 0,
    inserted_at     DateTime64(3, 'UTC') DEFAULT now64(3)
)
ENGINE = ReplacingMergeTree(inserted_at)
PARTITION BY toYear(ts)
ORDER BY (symbol, method, scale, ts, run_id)
SETTINGS index_granularity = 8192;

-- =============================================================================
-- str_trend_state_snapshots: periodic trend classification per index (and its pair)
-- payload holds the full JSON state for audit and replay.
-- =============================================================================
CREATE TABLE IF NOT EXISTS dow.str_trend_state_snapshots
(
    run_id               String,
    symbol               LowCardinality(String),
    pair_symbol          LowCardinality(String),
    ts                   DateTime64(3, 'America/New_York'),
    primary_state        LowCardinality(String),
    secondary_direction  LowCardinality(String),
    confirmation_status  LowCardinality(String),
    defense_line         Decimal(12, 4),
    volume_confirms      UInt8,
    payload              String,                -- JSON
    inserted_at          DateTime64(3, 'UTC') DEFAULT now64(3)
)
ENGINE = ReplacingMergeTree(inserted_at)
PARTITION BY toYear(ts)
ORDER BY (symbol, pair_symbol, ts, run_id)
SETTINGS index_granularity = 8192;

-- =============================================================================
-- str_level_log: support, resistance, trendline and defense levels
-- zone_low and zone_high bound the level zone. slope_per_day applies to trendlines.
-- =============================================================================
CREATE TABLE IF NOT EXISTS dow.str_level_log
(
    run_id         String,
    symbol         LowCardinality(String),
    ts             DateTime64(3, 'America/New_York'),
    level_type     LowCardinality(String),      -- 'support', 'resistance', 'trendline_up', 'trendline_down', 'defense'
    price          Decimal(12, 4),
    zone_low       Decimal(12, 4),
    zone_high      Decimal(12, 4),
    touches        UInt8,
    slope_per_day  Decimal(12, 6) DEFAULT 0,
    inserted_at    DateTime64(3, 'UTC') DEFAULT now64(3)
)
ENGINE = ReplacingMergeTree(inserted_at)
PARTITION BY toYear(ts)
ORDER BY (symbol, ts, level_type, price)
SETTINGS index_granularity = 8192;

-- =============================================================================
-- str_rule_backtest_log: one row per rule, pair, run and metric (evidence ledger)
-- Not partitioned: low volume. config_hash and decision_table_hash prove the decision
-- table was fixed before the backtest ran.
-- =============================================================================
CREATE TABLE IF NOT EXISTS dow.str_rule_backtest_log
(
    run_id               String,
    rule_id              LowCardinality(String),
    pair                 LowCardinality(String),
    period_start         Date,
    period_end           Date,
    n_obs                UInt32,
    metric_name          LowCardinality(String),
    metric_value         Decimal(12, 6),
    ci_low               Decimal(12, 6),
    ci_high              Decimal(12, 6),
    null_value           Decimal(12, 6),
    p_value              Decimal(8, 6),
    label                LowCardinality(String),    -- 'data-confirmed', 'data-refuted', 'insufficient-evidence'
    literature_label     LowCardinality(String),    -- 'literature-consensus', 'literature-disputed', 'agent-defined'
    config_hash          String,
    decision_table_hash  String,
    notes                String,
    inserted_at          DateTime64(3, 'UTC') DEFAULT now64(3)
)
ENGINE = ReplacingMergeTree(inserted_at)
ORDER BY (rule_id, pair, run_id)
SETTINGS index_granularity = 8192;

-- =============================================================================
-- ops_data_quality_log: findings of integrity checks (append-only audit)
-- Plain MergeTree on purpose: an audit log must never deduplicate. run_id groups one run.
-- ts is the check time (UTC). bar_ts is the affected bar (09:30 NY), or epoch when not bar-specific.
-- =============================================================================
CREATE TABLE IF NOT EXISTS dow.ops_data_quality_log
(
    ts           DateTime64(3, 'UTC'),
    symbol       LowCardinality(String),
    check_name   LowCardinality(String),        -- 'gap', 'duplicate_identical', 'duplicate_conflict', 'exchange_conflict', 'ohlc_sanity', 'flat_bar', 'zero_volume', 'stale', 'coverage', 'row_reconciliation'
    severity     LowCardinality(String),        -- 'info', 'warn', 'error'
    detail       String,
    bar_ts       DateTime64(3, 'America/New_York') DEFAULT toDateTime64(0, 3),
    inserted_at  DateTime64(3, 'UTC') DEFAULT now64(3),
    run_id       String
)
ENGINE = MergeTree
PARTITION BY toYYYYMM(ts)
ORDER BY (symbol, check_name, ts, run_id)
SETTINGS index_granularity = 8192;
