# P2 data-pipeline adversarial review (commit 897f51e)

Reviewer: code-reviewer (red team). Date: 2026-11-08. Scope: `config.py`, `storage/clickhouse_client.py`,
`data/*.py`, `cli.py`, `scripts/check_integrity.py`, `scripts/init_clickhouse.py`, `db/init/01_schema.sql`, `tests/`.

## Verification performed

| Item | Result |
|---|---|
| `pytest -q` | 27 passed |
| `ruff check src tests scripts` | 1 error, PYI041 in `src/dowtheory/levels.py:25` (untracked file, not in 897f51e, but the lint gate fails on the working tree) |
| `SHOW GRANTS FOR trading_user` | `ALL`-equivalent incl. DROP, TRUNCATE, ALTER, SYSTEM `ON *.* WITH GRANT OPTION` |
| `dow.mkt_klines` active partitions / parts | 1188 / 1530 for ~70.7k rows |
| ts_open wall-clock | 100% of rows at 09:30 NY, incl. 1927 rows (pre-1970 round trip is correct) |
| Flat bars O=H=L=C (FINAL) | ^GSPC 8547, ^IXIC 3459, IYT 8 |
| Same-date duplicates under FINAL | 0 today |
| TEST_RT residue in production table | 10 raw rows, last cleanup mutation `is_done=0` |
| `ops_data_quality_log` raw vs FINAL | 73 / 73 (already merged; see H1 for the lost row) |

All ClickHouse access was read-only. Probe script: Python calls of `_guard_sql`, `check_gaps`, `normalize_bars`, `load_klines(csv)`, `run_integrity_checks(symbols=[])`, `load_config` on scratch inputs.

---

## CRITICAL

### C1. Write scope "dow only" is enforced on `insert_df` only; `command()`/`query_df()` reach every database with any non-DROP destructive statement
- **Where:** `src/dowtheory/storage/clickhouse_client.py:16`, `:23-25`, `:60-63`, `:76-79`.
- **Flaw:** `_guard_sql` is a keyword blacklist for `DROP|TRUNCATE`. The `database` check (`:40`) only sets the *default* database; fully qualified names bypass it. `trading_user` holds `ALL ... ON *.* WITH GRANT OPTION`, so this regex is the *only* barrier protecting `usstock` / `twstock` / `trading`.
- **Adversarial scenario (verified, every statement below passes the guard):**
  ```
  ALTER TABLE usstock.mkt_daily_quotes DELETE WHERE 1          -- TRUNCATE-equivalent on a shared table
  INSERT INTO usstock.x SELECT 1                                 -- cross-DB write via query_df/command
  RENAME TABLE dow.mkt_klines TO dow.old
  EXCHANGE TABLES dow.mkt_klines AND usstock.x                   -- swaps a shared table out
  CREATE OR REPLACE TABLE dow.mkt_klines (a UInt8) ENGINE=Memory -- implicit drop
  ALTER TABLE dow.mkt_klines MODIFY TTL toDateTime(ts_open) + INTERVAL 1 DAY  -- deletes all history on merge
  ALTER TABLE dow.mkt_klines DETACH PARTITION ALL
  ```
  One P3/P4 agent writing "clean up old swings" as `client.command("ALTER TABLE str_swing_log DELETE ...")` with a typo'd database prefix wipes another project's data, and nothing stops it.
- **PoC test:**
  ```python
  @pytest.mark.parametrize("sql", [
      "ALTER TABLE usstock.t DELETE WHERE 1", "INSERT INTO usstock.t SELECT 1",
      "RENAME TABLE dow.a TO dow.b", "EXCHANGE TABLES dow.a AND usstock.b",
      "CREATE OR REPLACE TABLE dow.a (x UInt8) ENGINE=Memory",
      "ALTER TABLE dow.a MODIFY TTL ts + INTERVAL 1 DAY", "ALTER TABLE dow.a DETACH PARTITION ALL",
      "SELECT 1 FROM usstock.t SETTINGS readonly=0"])
  def test_guard_blocks(sql):
      with pytest.raises(UnsafeSQLError):
          ClickHouseClient().command(sql)
  ```
- **Hardened fix (defence in depth, both layers):**
  1. Server side (root cause): create a dedicated `dow_user` with `GRANT SELECT ON usstock.*, twstock.*; GRANT SELECT, INSERT, ALTER DELETE, ALTER UPDATE, OPTIMIZE, CREATE TABLE ON dow.*` and no DROP/TRUNCATE. Use it as the default in `clickhouse_client.py:47-48` and `init_clickhouse.py:26-27`. This is the only fix that a regex cannot get wrong.
  2. Client side: split read and write paths and whitelist instead of blacklist.
  ```python
  _READ_OK = re.compile(r"^\s*(SELECT|WITH|SHOW|DESCRIBE|EXISTS)\b", re.I)
  _WRITE_OK = re.compile(
      r"^\s*(CREATE\s+TABLE\s+IF\s+NOT\s+EXISTS\s+dow\.|CREATE\s+DATABASE\s+IF\s+NOT\s+EXISTS\s+dow\b"
      r"|ALTER\s+TABLE\s+dow\.\w+\s+(DELETE|UPDATE)\b|OPTIMIZE\s+TABLE\s+dow\.)", re.I)
  _FORBIDDEN = re.compile(r"\b(DROP|TRUNCATE|RENAME|EXCHANGE|DETACH|ATTACH|TTL|REPLACE|MOVE|FREEZE|GRANT|SYSTEM|KILL)\b", re.I)
  _OTHER_DB = re.compile(r"\b(?!dow\b)(\w+)\s*\.\s*\w+", re.I)  # qualified name outside dow (reads only)

  def query_df(self, sql, params=None):
      if not _READ_OK.match(sql) or ";" in sql.rstrip().rstrip(";"):
          raise UnsafeSQLError(...)
      return self._conn().query_df(sql, parameters=params, settings={"readonly": 2})

  def command(self, sql, params=None):
      if not _WRITE_OK.match(sql) or _FORBIDDEN.search(sql) or ";" in sql.rstrip().rstrip(";"):
          raise UnsafeSQLError(...)
  ```
  Passing `settings={"readonly": 2}` on reads makes the server reject any write smuggled through `query_df` regardless of regex coverage. Also reuse this one guard from `scripts/init_clickhouse.py:10` instead of the duplicated regex.

---

## HIGH

### H1. `ops_data_quality_log` is ReplacingMergeTree keyed `(symbol, check_name, ts)`: findings of the same run collapse; a real gap warning is already lost
- **Where:** `db/init/01_schema.sql:161-163`; `src/dowtheory/data/quality.py:173-175` (all issues of a run share one `ts`).
- **Flaw:** `check_gaps` emits N `warn` rows plus one `info` row, all `(symbol, 'gap', now)`. On merge (or FINAL) only one survives. The header comment calls this table "append-only audit", the engine contradicts it.
- **Evidence (verified):** `check_gaps('^GSPC', ...)` today returns `warn: 7 missing sessions 1933-03-06 -> 1933-03-14` (the 1933 bank holiday) plus an `info`. The log contains `^GSPC gap info` x4 and **zero** `gap warn` rows. The warning was written and merged away.
- **PoC:** insert the three issues from `check_gaps("X", bdate_range("2024-01-02","2024-06-28").delete([*range(10,20), *range(40,50), 70]), 4)` via `log_issues`, then `SELECT count() FROM dow.ops_data_quality_log FINAL WHERE symbol='X'` returns 1, expected 3.
- **Fix:** an audit log must not deduplicate. New table (the current one cannot be altered in place; use the migration pattern with RENAME, not DROP):
  ```sql
  CREATE TABLE IF NOT EXISTS dow.ops_data_quality_log_v2 (... same columns ..., run_id String)
  ENGINE = MergeTree PARTITION BY toYYYYMM(ts)
  ORDER BY (symbol, check_name, ts, severity, bar_ts);
  ```
  Add a `run_id` (uuid4 per `run_integrity_checks`/`cmd_fetch`) so runs are groupable. Add a unit test asserting distinct rows survive `OPTIMIZE ... FINAL` in the integration suite.

### H2. Close-only history is stored as fake OHLC and passes every check (8547 ^GSPC bars to 1962, 3459 ^IXIC bars to 1984)
- **Where:** `src/dowtheory/data/quality.py:67-78` (`check_ohlc`), `:81-90` (`check_zero_volume` only warns for INDEX).
- **Flaw:** Yahoo's early ^GSPC (1927-1962) and ^IXIC (1971-1984) rows are `open=high=low=close`, volume 0. `check_ohlc` accepts equality, zero-volume is a warn for indices, so `check_integrity.py` exits 0. Dow-theory swings, ranges, ATR and "line" detection built on high/low will run on close-only data presented as intraday ranges; ATR is 0, line/range rules trivially fire. The `【data-confirmed】` label would then rest on synthetic bars.
- **Adversarial scenario:** P4 backtests ^GSPC/^DJT from 1928; the ATR swing method with `atr_mult=2.0` gets `ATR≈close-to-close` only, `line.band_pct` ranges are computed on closes, and results are labelled data-confirmed.
- **PoC:**
  ```python
  def test_flat_bars_flagged():
      df = _frame(["2024-01-02"] * 1, open=10.0, high=10.0, low=10.0, close=10.0)
      assert q.check_flat_bars("X", df)[0].severity in {"warn", "error"}
  ```
- **Fix:** add a `flat_bar` check that reports the share and the last flat date, and persist an `ohlc_since` per symbol.
  ```python
  def check_flat_bars(symbol, df, max_share=0.01):
      flat = (df["open"] == df["high"]) & (df["high"] == df["low"]) & (df["low"] == df["close"])
      if not flat.any():
          return []
      sev = "error" if flat.mean() > max_share else "warn"
      return [QualityIssue(symbol, "flat_bar", sev,
              f"{int(flat.sum())} O=H=L=C bars; last {flat[flat].index[-1].date()} "
              "(close-only history; restrict high/low methods to later dates)", flat[flat].index[0])]
  ```
  Then either set `data.analysis_start` per symbol in `configs/dow.yaml` (^GSPC 1962-07, ^IXIC 1985-01) and make `load_klines` enforce it, or give swing methods an explicit close-only mode. Document the decision in the research doc.

### H3. `cmd_fetch` aborts the whole batch on predictable failures and loses the issues it already collected
- **Where:** `src/dowtheory/cli.py:27`, `:51-57`, `:61`, `:62` (`_coverage_issue` at `:34-35`).
- **Flaw:**
  1. Stooq with `--start` after the last available bar filters to an empty frame; `insert_df` raises `ValueError("Refusing to insert an empty frame")` **outside** the `try`, killing the loop. In probe mode `_coverage_issue` raises `IndexError` on `.iloc[0]`.
  2. Only `ValueError`/`SourceUnavailable` are caught. yfinance raises `YFRateLimitError`, `requests` errors, `KeyError` on schema drift; any of them aborts the loop.
  3. On abort, `quality.log_issues` (`:68`) never runs. Symbols already inserted have no coverage/reconciliation row, and later symbols are silently not fetched.
- **PoC:**
  ```python
  def test_fetch_continues_after_empty_stooq(monkeypatch, fake_client):
      monkeypatch.setattr(stooq_fetcher, "fetch_daily", lambda s, exchange=None: _bars_ending("2020-01-01"))
      rc = cli.main(["fetch", "--source", "stooq", "--start", "2025-01-01", "--symbols", "A", "B"])
      assert rc == 1 and fake_client.logged_symbols == {"A", "B"}
  ```
- **Fix:**
  ```python
  for symbol in symbols:
      try:
          bars = _fetch_one(args.source, symbol, args.start, cfg)
          if bars.empty:
              raise ValueError(f"no bars on/after {args.start}")
          if not args.probe:
              client.insert_df("dow.mkt_klines", to_insert_frame(bars))
      except Exception as exc:  # noqa: BLE001 - recorded as an error issue and exit 1, never hidden
          logger.exception("fetch %s failed", symbol)
          issues.append(QualityIssue(symbol, "coverage", "error", f"fetch failed: {type(exc).__name__}: {exc}"))
          status = 1
          continue
      ...
  # wrap the post-loop in try/finally so log_issues always runs
  ```

### H4. Duplicate check cannot tell a benign reload from a conflicting row; its own remediation destroys the evidence; exchange conflicts are invisible
- **Where:** `src/dowtheory/data/quality.py:115-126`, `:148`; `db/init/01_schema.sql:17-18`, `:43`.
- **Flaw:**
  1. Every routine re-fetch (same values) creates raw duplicates until a background merge, so `check_integrity.py` flaps between FAIL and PASS depending on merge timing. The CLAUDE.md gate "exit 0 required" becomes timing-dependent.
  2. The message tells the operator to run `OPTIMIZE TABLE dow.mkt_klines FINAL`. If the duplicates were *conflicting* (yfinance vs stooq values, or exchange `INDEX` vs `NYSE`), OPTIMIZE silently keeps the newest and the conflict is gone forever.
  3. `exchange` is not in the sort key; `run_integrity_checks` reads `df["exchange"].iloc[0]` only. A symbol re-loaded with a different exchange (missing `exchange_map` entry, default `NYSEARCA` for a NYSE stock) silently overwrites, and the zero-volume severity is decided on whichever row is first.
- **PoC (integration):** insert one bar for `TEST_DUP` with `close=1.0, exchange='INDEX'`, re-insert with `close=2.0, exchange='NYSE'`; current code reports one generic "duplicate" error and recommends OPTIMIZE, after which `check` passes with close=2.0 and no trace.
- **Fix:**
  ```sql
  SELECT count() AS keys, sum(c - 1) AS extra, countIf(v > 1) AS conflicting
  FROM (SELECT count() c, uniqExact(tuple(open, high, low, close, volume, exchange)) v
        FROM dow.mkt_klines WHERE symbol = {s:String} AND interval = '1d'
        GROUP BY ts_open HAVING c > 1)
  ```
  Report `conflicting > 0` as **error** (and list first 5 ts_open with both values), identical re-loads as **info**. Add `SELECT uniqExact(exchange) FROM dow.mkt_klines WHERE symbol=...` (raw, not FINAL) as an `exchange_conflict` error, and compare to `cfg.data.exchange_map[symbol]` (error when the symbol is missing from the map). Remove the OPTIMIZE hint from the conflicting branch.

---

## MEDIUM

### M1. `normalize_bars` silently rewrites bad vendor data
- **Where:** `src/dowtheory/data/bars.py:44`, `:45`, `:56`, `:57`; `:66`.
- **Flaw (verified):** NaN volume becomes 0, negative volume `-5` becomes 0, `1.9` truncates to 1, `inf` high passes (`dropna` ignores inf, `check_ohlc` accepts `inf >= max`) and `to_insert_frame` builds `Decimal('inf')`. Duplicate vendor dates are dropped with `keep="last"` without a count. Each of these hides a source defect the integrity gate is supposed to surface. The global CLAUDE.md says never silently swallow.
- **Fix:** validate before coercion and raise or return counts.
  ```python
  prices = df[PRICE_COLUMNS].astype(float)
  if not np.isfinite(prices.to_numpy()).all(): raise ValueError(f"{source}: non-finite price for {symbol}")
  vol = df["volume"]
  if (vol < 0).any() or (vol.dropna() % 1 != 0).any(): raise ValueError(f"{source}: invalid volume for {symbol}")
  n_dup = int(df.index.duplicated().sum()); if n_dup: logger.warning("%s %s: %d duplicate dates", source, symbol, n_dup)
  ```
  Keep NaN volume as 0 only for `exchange == "INDEX"` and log the count.

### M2. Integrity checks miss structural defects that FINAL does not collapse
- **Where:** `src/dowtheory/data/quality.py:139-161`; `src/dowtheory/data/loader.py:83`.
- **Flaw:** None of these is checked: (a) two rows with the same NY date but different `ts_open` (a source or code change that stamps 00:00 or 09:31 creates a second key that FINAL keeps; the loader then drops one with `keep="last"`); (b) extra bars on weekends or holidays (gap check only looks for *missing* sessions); (c) future-dated bars (`check_stale` returns `age=-1` and passes); (d) `ts_close <= ts_open` or different calendar date; (e) price jumps that indicate unit or split errors on unadjusted ETFs. Non-monotonic order is not an issue here because the SQL sorts, but it also means non-monotonic source data is never detected.
- **Fix:** select `ts_open, ts_close` as well and add:
  ```python
  if df.index.duplicated().any(): error "same_date_duplicate"
  if (toTime(ts_open) != '09:30') rows: error "ts_open_not_canonical"
  extra = df.index.difference(expected_sessions(first, last)); weekend = extra[extra.dayofweek >= 5]: warn/error "extra_session"
  if df.index[-1] > today: error "future_bar"
  ret = df["close"].pct_change().abs(); if (ret > 0.25).any(): warn "price_jump"
  ```
  In `loader.py:83` raise on duplicated dates instead of dropping.

### M3. Integrity gate passes vacuously
- **Where:** `src/dowtheory/data/quality.py:129-166`; `src/dowtheory/cli.py:72-77`.
- **Flaw (verified):** `run_integrity_checks(client, [], cfg)` returns `exit 0`, PASS. A config with an empty or typo'd `symbols` list (see M6) yields a green gate with zero data checked. Symbols present in `dow.mkt_klines` but not in config (e.g. `TEST_RT`) are never checked. Row reconciliation with the source (team_design §3) is never executed by `check`, only during `fetch` without `--start`.
- **Fix:** `if not symbols: return [QualityIssue("*", "coverage", "error", "no symbols to check")]`. Add an `unexpected_symbol` warn from `SELECT DISTINCT symbol FROM dow.mkt_klines` minus config. Persist fetch counts (e.g. `ops_fetch_log` with `run_id, symbol, source, rows, first_ts, last_ts`) and reconcile against the latest one in `check`.

### M4. Monthly partitioning of 70k rows: 1188 partitions, 1530 parts; FINAL cost and fragile chunk math
- **Where:** `db/init/01_schema.sql:42`; `src/dowtheory/storage/clickhouse_client.py:15`, `:71-73`.
- **Flaw:** ~60 rows per partition. Every FINAL query (loader, all checks) merges across 1188 partitions; a full re-fetch of ^GSPC creates ~1190 new parts. `INSERT_CHUNK_ROWS=1000` only stays under `max_partitions_per_insert_block=100` because bars are daily; weekly/monthly bars (a planned higher-scale view) or a sparse pre-1930 source exceed 100 months per chunk and the insert fails mid-way, leaving a partial load.
- **Fix:** `PARTITION BY toYear(ts_open)` (~100 partitions) or `toDecade`-like `intDiv(toYear(ts_open), 10)`. Migrate via new table + `INSERT SELECT` + `RENAME` (no DROP). Compute chunks by partition instead of a row count:
  ```python
  key = df["ts_open"].dt.year
  for _, part in df.groupby(key // 50):  # <= 50 partitions per block
      self._conn().insert_df(table, part)
  ```

### M5. Integration test writes into the production table and leaves residue
- **Where:** `tests/integration/test_clickhouse_roundtrip.py:8-9`, `:19-27`.
- **Flaw (verified):** 10 raw `TEST_RT` rows sit in `dow.mkt_klines` now; the last `ALTER ... DELETE` mutation is `is_done=0`. Each run issues a mutation on the shared server. A failed or interrupted run leaves rows that `DISTINCT symbol` queries and P3 tooling will see. `client.ping()` runs at import, so test collection hits the network.
- **Fix:** create `dow.mkt_klines_test` (same DDL via `CREATE TABLE IF NOT EXISTS dow.mkt_klines_test AS dow.mkt_klines`) and point the loader at a table parameter, or use a unique `TEST_RT_<uuid>` symbol and assert absence after `mutations_sync=2` in a session-scoped fixture with a 120 s timeout. Move `ping()` into a fixture.

### M6. Config has no type validation
- **Where:** `src/dowtheory/config.py:109-116`.
- **Flaw (verified):** `symbols: '^DJI'` loads as a string; `cmd_fetch` then iterates `'^', 'D', 'J', 'I'`. `stale_business_days: 'five'` loads and fails later deep in `check_stale`. `config_hash` hashes these invalid values happily.
- **Fix:** validate against field annotations in `_build` (`typing.get_type_hints(cls)`, check `list`/`dict`/`int`/`float`/`bool`), or switch these dataclasses to `pydantic` models with `extra="forbid"`. Add a test for each wrong type.

### M7. Mixed sources overwrite each other silently; reconciliation is wrong across sources
- **Where:** `src/dowtheory/cli.py:23-28`, `:63-67`; `db/init/01_schema.sql:24`.
- **Flaw:** A Stooq fallback has no server-side range and re-inserts the whole history, replacing every yfinance row with newer `inserted_at` (the schema comment states this as intended). No cross-source diff is computed before overwrite. Stooq's US ETF series are, to my knowledge, adjusted for splits and dividends while yfinance here is `auto_adjust=False`; verify this before relying on it. If true, SPY/IYT history becomes a silent mix of adjusted and unadjusted prices. `row_reconciliation` compares one source's count to the FINAL union of all sources, so any symbol touched by two sources reports a false error, and `--start` skips reconciliation entirely.
- **Fix:** before insert, read the overlapping FINAL rows, compute max abs relative diff on close; above 0.1% raise `source_conflict` error and refuse unless `--force-source`. Reconcile only the delivered window: `count() FINAL WHERE ts_open BETWEEN first AND last AND source = {src}`.

---

## LOW

### L1. CSV loader crashes on ClickHouse-style exports spanning DST
- **Where:** `src/dowtheory/data/loader.py:51-53`.
- **Flaw (verified):** a `ts_open` column with `-05:00` and `-04:00` offsets raises `ValueError: Mixed timezones detected`. Every real export of `mkt_klines` spans DST. The only test (`test_loader_csv.py:24-32`) uses a single offset.
- **Fix:** `dates = pd.to_datetime(df[date_col], utc=True, format="mixed").dt.tz_convert("America/New_York").dt.tz_localize(None)` when any value carries an offset; keep the naive path for plain dates. Add a two-offset test.

### L2. Staleness uses the machine's local zone (Asia/Taipei), not New York
- **Where:** `src/dowtheory/data/quality.py:138`.
- **Flaw (verified):** local now is 13:45 on 11-08 while NY is 00:45; between midnight Taipei and midnight NY the age is one business day too high. Gap/stale boundaries become run-time dependent.
- **Fix:** `today = today or pd.Timestamp.now(tz="America/New_York").tz_localize(None).normalize()`.

### L3. `bar_ts` does not match the bar key and mixes time zones
- **Where:** `src/dowtheory/data/quality.py:180-181`.
- **Flaw (verified):** naive dates are localised to 00:00 NY (the bar key is 09:30), and the non-bar sentinel is UTC epoch, giving an `object` column with mixed tz. `JOIN ON bar_ts = ts_open` never matches.
- **Fix:** store `date + 09:30` NY for bar issues and `pd.Timestamp(0, tz="America/New_York")` for the sentinel; build the column with `pd.to_datetime(..., utc=True)`.

### L4. `init_clickhouse.py` has its own weaker guard and naive parsing
- **Where:** `scripts/init_clickhouse.py:10`, `:14-19`, `:23-28`, `:34-35`.
- **Flaw:** duplicated regex (DRY), no database-scope check (a SQL file can `CREATE TABLE usstock.x` or `ALTER TABLE usstock... DELETE`), `--` and `;` are split inside string literals, `/* */` comments are not stripped, the client is never closed.
- **Fix:** route through `ClickHouseClient.command` with the whitelist from C1, require every statement to reference `dow.` or `DATABASE ... dow`, and `close()` in `finally`.

### L5. Hard-coded credential default
- **Where:** `src/dowtheory/storage/clickhouse_client.py:47-48`; `scripts/init_clickhouse.py:26-27`.
- **Fix:** read from env or a `.env` (git-ignored) and fail with a clear message when unset.

### L6. Guard false positives on literals
- **Where:** `src/dowtheory/storage/clickhouse_client.py:16`.
- **Flaw (verified):** `SELECT ... WHERE detail LIKE '%drop%'` is refused. Harmless but pushes callers to work around the guard. The whitelist in C1 removes this for reads.

### L7. Gap calendar is wrong before 1971 and before 1952
- **Where:** `src/dowtheory/data/quality.py:34-37`.
- **Flaw:** pre-1952 NYSE had Saturday sessions (yfinance omits them, so ^GSPC 1928 has 250 rows instead of ~300) and pre-1971 federal holiday rules differ. Swing `duration_days` and `secondary_min_days` counted in bars are not comparable across eras.
- **Fix:** use `pandas_market_calendars` (`XNYS`) or document a hard analysis start date per symbol in the research doc and in config.

### L8. Lint gate fails on the working tree
- `src/dowtheory/levels.py:25` PYI041. Not part of 897f51e, but the next commit will fail "follow project linting".

---

## Test gaps

| Gap | Where it should go |
|---|---|
| `test_hash_is_stable_and_sensitive` is vacuous: it builds `other` with `minor_pct=0.04` and never hashes it | `tests/unit/test_config.py:16-20` |
| No test for `cmd_fetch` at all (empty-after-filter, non-ValueError exceptions, reconciliation, logging on abort) | new `tests/unit/test_cli_fetch.py` |
| No test for `stooq_fetcher` (HTML body, HTTP 5xx, both hosts down) | new `tests/unit/test_stooq_fetcher.py` |
| Guard tests cover only DROP/TRUNCATE; none for cross-DB writes or other destructive DDL | `tests/unit/test_clickhouse_client.py` (C1 PoC) |
| No test that distinct issues survive in `ops_data_quality_log` | integration (H1 PoC) |
| No flat-bar, inf price, negative/NaN volume, same-date-duplicate, weekend-bar, future-bar tests | `tests/unit/test_quality.py`, `test_yahoo_fetcher.py` |
| Integration round trip covers only 2024-03-04..08 (all EST); no DST-crossing week, no pre-1970 row | `tests/integration/test_clickhouse_roundtrip.py` |
| No conflicting-duplicate or exchange-conflict integration test | integration (H4 PoC) |
| `init_clickhouse.split_statements` untested (`--` in literal, `/* */`) | new `tests/unit/test_init_sql.py` |
| `FakeClient` routes on substrings `"GROUP BY"`/`"count()"`; a new query containing either silently gets the wrong frame | `tests/unit/test_quality.py:57-62`, dispatch on an explicit marker |

## Checked and found correct
- `ts_open`/`ts_close` construction: 09:30/16:00 NY never fall in a DST transition hour; the DB shows 09:30 for 100% of rows across 1927-2026.
- Pre-1970 `toDate32(ts_open, 'America/New_York')` returns correct dates (^GSPC starts 1927-12-30 as at the source). Values before 1900 would saturate in DateTime64; no current source delivers them, but a Stooq ^DJI back to 1896 would. Add a `ts_open >= 1900-01-01` assertion in `normalize_bars` before enabling Stooq history.
- Decimal path: `round(4)` then `Decimal(f"{v:.4f}")` is exact for `Decimal(12,4)`; DJI-scale values are far from the 99,999,999.9999 limit.
- Analytic reads (loader, integrity, reconciliation) use FINAL; the duplicate check deliberately does not.
- The DROP/TRUNCATE regex itself is case-insensitive and scans comments, so case, whitespace and comment tricks do not hide those two keywords. The problem is everything else (C1).
