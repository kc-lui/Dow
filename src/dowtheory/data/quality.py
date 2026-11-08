"""Data-integrity checks for ``dow.mkt_klines`` with results logged to ``ops_data_quality_log``.

Calendar approximation: expected sessions are business days (Mon-Fri) minus the US federal
holidays from ``USFederalHolidayCalendar``. That differs from the NYSE calendar: it wrongly
treats Columbus Day and Veterans Day as closed (the extra bars are harmless) and misses Good
Friday and ad-hoc closures (those appear as short gaps). Gap runs of at most
``max_gap_business_days`` are therefore summarised as info; only longer runs warn.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import UTC, datetime

import pandas as pd
from pandas.tseries.holiday import USFederalHolidayCalendar

from dowtheory.config import DowConfig
from dowtheory.storage.clickhouse_client import ClickHouseClient

LOG_TABLE = "dow.ops_data_quality_log"
NY = "America/New_York"


@dataclass(frozen=True)
class QualityIssue:
    symbol: str
    check_name: str
    severity: str  # info | warn | error
    detail: str
    bar_ts: pd.Timestamp | None = None


def expected_sessions(first: pd.Timestamp, last: pd.Timestamp) -> pd.DatetimeIndex:
    """Approximate trading days between ``first`` and ``last`` inclusive."""
    holidays = USFederalHolidayCalendar().holidays(first, last)
    return pd.bdate_range(first, last, freq="C", holidays=holidays)


def check_gaps(symbol: str, dates: pd.DatetimeIndex, max_gap: int) -> list[QualityIssue]:
    """Warn for runs of missing expected sessions longer than ``max_gap``; summarise the rest."""
    if len(dates) < 2:
        return []
    expected = expected_sessions(dates.min(), dates.max())
    missing = expected.difference(dates)
    if missing.empty:
        return []
    pos = expected.get_indexer(missing)
    run_id = (pd.Series(pos).diff() != 1).cumsum().to_numpy()
    issues: list[QualityIssue] = []
    short = 0
    for rid in sorted(set(run_id)):
        run = missing[run_id == rid]
        if len(run) > max_gap:
            issues.append(QualityIssue(
                symbol, "gap", "warn",
                f"{len(run)} missing sessions {run[0].date()} -> {run[-1].date()}", run[0]))
        else:
            short += len(run)
    if short:
        issues.append(QualityIssue(
            symbol, "gap", "info",
            f"{short} missing sessions in runs <= {max_gap} (holiday-calendar approximation)"))
    return issues


def check_ohlc(symbol: str, df: pd.DataFrame) -> list[QualityIssue]:
    """Error rows violating high>=max(open,close), low<=min(open,close) or low>0."""
    bad = df[
        (df["high"] < df[["open", "close"]].max(axis=1))
        | (df["low"] > df[["open", "close"]].min(axis=1))
        | (df["low"] <= 0)
    ]
    if bad.empty:
        return []
    first = bad.index[0]
    return [QualityIssue(symbol, "ohlc_sanity", "error",
                         f"{len(bad)} bars violate OHLC sanity; first {first.date()}", first)]


def check_flat_bars(
    symbol: str, df: pd.DataFrame, analysis_start: str | None = None
) -> list[QualityIssue]:
    """Warn about O=H=L=C bars (close-only history presented as OHLC)."""
    flat = (df["open"] == df["high"]) & (df["high"] == df["low"]) & (df["low"] == df["close"])
    if not flat.any():
        return []
    dates = df.index[flat]
    after = f"; {int((dates >= pd.Timestamp(analysis_start)).sum())} on/after analysis_start " \
            f"{analysis_start}" if analysis_start else ""
    return [QualityIssue(
        symbol, "flat_bar", "warn",
        f"{len(dates)} O=H=L=C bars ({dates[0].date()} -> {dates[-1].date()}){after}; "
        "close-only history, do not use high/low methods before the analysis start", dates[0])]


def check_zero_volume(symbol: str, df: pd.DataFrame, exchange: str) -> list[QualityIssue]:
    """Zero-volume bars: warn for indices (volume often unreported), error otherwise."""
    zero = df[df["volume"] == 0]
    if zero.empty:
        return []
    sev = "warn" if exchange == "INDEX" else "error"
    return [QualityIssue(
        symbol, "zero_volume", sev,
        f"{len(zero)} zero-volume bars ({zero.index[0].date()} -> {zero.index[-1].date()})",
        zero.index[0])]


def check_stale(symbol: str, last: pd.Timestamp, today: pd.Timestamp, limit: int) -> list[QualityIssue]:
    """Warn when the newest bar is more than ``limit`` business days old."""
    age = len(pd.bdate_range(last.normalize(), today.normalize())) - 1
    if age > limit:
        return [QualityIssue(symbol, "stale", "warn",
                             f"last bar {last.date()} is {age} business days old", last)]
    return []


def row_reconciliation(client: ClickHouseClient, source_counts: dict[str, int]) -> list[QualityIssue]:
    """Compare ClickHouse FINAL row counts to the counts the source delivered."""
    issues = []
    for symbol, expected in source_counts.items():
        got = int(client.query_df(
            "SELECT count() AS n FROM dow.mkt_klines FINAL "
            "WHERE symbol = {s:String} AND interval = '1d'", {"s": symbol})["n"].iloc[0])
        if got != expected:
            issues.append(QualityIssue(symbol, "row_reconciliation", "error",
                                       f"ClickHouse has {got} rows, source delivered {expected}"))
    return issues


def check_duplicates(client: ClickHouseClient, symbol: str) -> list[QualityIssue]:
    """Raw-table duplicates per (symbol, interval, ts_open), split by whether values agree.

    Identical re-loads are info (they vanish on merge). Rows with different
    exchange/OHLC/volume for one key are errors: they must be resolved by a person.
    """
    inner = (
        "FROM (SELECT ts_open, count() AS c, "
        "uniqExact(tuple(exchange, open, high, low, close, volume)) AS v "
        "FROM dow.mkt_klines WHERE symbol = {s:String} AND interval = '1d' "
        "GROUP BY ts_open HAVING c > 1)"
    )
    row = client.query_df(
        f"SELECT countIf(v = 1) AS ident_keys, sumIf(c - 1, v = 1) AS ident_extra, "
        f"countIf(v > 1) AS conflict_keys {inner}", {"s": symbol}).iloc[0]
    issues: list[QualityIssue] = []
    if int(row["ident_keys"]):
        issues.append(QualityIssue(
            symbol, "duplicate_identical", "info",
            f"{int(row['ident_extra'] or 0)} extra identical rows over {int(row['ident_keys'])} keys"))
    if int(row["conflict_keys"]):
        sample = client.query_df(
            f"SELECT ts_open {inner} WHERE v > 1 ORDER BY ts_open LIMIT 5", {"s": symbol})
        first = [str(t.date()) for t in pd.to_datetime(sample["ts_open"])] if len(sample) else []  # empty if merged in between
        issues.append(QualityIssue(
            symbol, "duplicate_conflict", "error",
            f"{int(row['conflict_keys'])} keys with conflicting values for the same ts_open; "
            f"first: {first}", pd.Timestamp(first[0]) if first else None))
    return issues


def check_exchange(
    client: ClickHouseClient, symbol: str, final_exchange: str, expected: str | None
) -> list[QualityIssue]:
    """Error when one symbol carries several exchanges or differs from ``exchange_map``."""
    n = int(client.query_df(
        "SELECT uniqExact(exchange) AS n FROM dow.mkt_klines WHERE symbol = {s:String}",
        {"s": symbol})["n"].iloc[0])
    issues = []
    if n > 1:
        issues.append(QualityIssue(symbol, "exchange_conflict", "error",
                                   f"{n} distinct exchange values stored for this symbol"))
    if expected is not None and final_exchange != expected:
        issues.append(QualityIssue(symbol, "exchange_conflict", "error",
                                   f"stored exchange '{final_exchange}' != configured '{expected}'"))
    return issues


def run_integrity_checks(
    client: ClickHouseClient,
    symbols: list[str],
    cfg: DowConfig,
    source_counts: dict[str, int] | None = None,
    log: bool = True,
    today: pd.Timestamp | None = None,
    run_id: str | None = None,
) -> list[QualityIssue]:
    """Run all checks for ``symbols``, optionally log them, and return the issues.

    An empty symbol list is itself an error: a gate that checks nothing must not pass.
    """
    today = today or pd.Timestamp.now(tz=NY).tz_localize(None).normalize()
    issues: list[QualityIssue] = []
    if not symbols:
        issues.append(QualityIssue("*", "coverage", "error", "no symbols to check"))
    for symbol in symbols:
        df = client.query_df(
            "SELECT toDate32(ts_open, 'America/New_York') AS date, exchange, open, high, low, "
            "close, volume FROM dow.mkt_klines FINAL WHERE symbol = {s:String} "
            "AND interval = '1d' ORDER BY date", {"s": symbol})
        if df.empty:
            issues.append(QualityIssue(symbol, "coverage", "error", "no rows in dow.mkt_klines"))
            continue
        exchange = str(df["exchange"].iloc[0])
        df = df.drop(columns="exchange")
        df["date"] = pd.to_datetime(df["date"])
        df = df.set_index("date")
        for col in ("open", "high", "low", "close"):
            df[col] = df[col].astype(float)
        start = cfg.data.analysis_start.get(symbol)
        issues.append(QualityIssue(
            symbol, "coverage", "info",
            f"first={df.index[0].date()} last={df.index[-1].date()} rows={len(df)}"))
        if start:
            clipped = int((df.index < pd.Timestamp(start)).sum())
            issues.append(QualityIssue(
                symbol, "coverage", "info",
                f"analysis_start={start} clips {clipped} earlier close-only bars"))
        issues += check_gaps(symbol, df.index, cfg.data.max_gap_business_days)
        issues += check_duplicates(client, symbol)
        issues += check_exchange(client, symbol, exchange, cfg.data.exchange_map.get(symbol))
        issues += check_ohlc(symbol, df)
        issues += check_flat_bars(symbol, df, start)
        issues += check_zero_volume(symbol, df, exchange)
        issues += check_stale(symbol, df.index[-1], today, cfg.data.stale_business_days)
    if source_counts:
        issues += row_reconciliation(client, source_counts)
    if log:
        log_issues(client, issues, run_id)
    return issues


def _bar_ts(ts: pd.Timestamp | None) -> pd.Timestamp:
    """Bar key (session date at 09:30 NY) or the epoch sentinel when not bar-specific."""
    if ts is None:
        return pd.Timestamp(0, tz="UTC").tz_convert(NY)
    return (ts.tz_localize(None).normalize() + pd.Timedelta(hours=9, minutes=30)).tz_localize(NY)


def new_run_id() -> str:
    """Fresh identifier grouping the rows of one check or fetch run."""
    return uuid.uuid4().hex


def log_issues(client: ClickHouseClient, issues: list[QualityIssue], run_id: str | None = None) -> str:
    """Append issues to ``dow.ops_data_quality_log``; returns the run_id used."""
    run_id = run_id or new_run_id()
    if not issues:
        return run_id
    frame = pd.DataFrame({
        "ts": [datetime.now(UTC)] * len(issues),
        "symbol": [i.symbol for i in issues],
        "check_name": [i.check_name for i in issues],
        "severity": [i.severity for i in issues],
        "detail": [i.detail for i in issues],
        "bar_ts": pd.to_datetime([_bar_ts(i.bar_ts) for i in issues], utc=True).tz_convert(NY),
        "run_id": run_id,
    })
    client.insert_df(LOG_TABLE, frame)
    return run_id


def exit_status(issues: list[QualityIssue]) -> int:
    """1 when any issue has severity 'error', else 0."""
    return int(any(i.severity == "error" for i in issues))


def format_report(issues: list[QualityIssue]) -> str:
    """Human-readable report with a summary line per severity."""
    counts = {s: sum(i.severity == s for i in issues) for s in ("error", "warn", "info")}
    lines = [f"Integrity report {datetime.now(UTC):%Y-%m-%d %H:%M:%S} UTC",
             f"SUMMARY errors={counts['error']} warnings={counts['warn']} info={counts['info']}",
             f"STATUS {'FAIL' if counts['error'] else 'PASS'}", ""]
    for sev in ("error", "warn", "info"):
        for i in (x for x in issues if x.severity == sev):
            lines.append(f"[{sev.upper():5}] {i.symbol:6} {i.check_name:18} {i.detail}")
    return "\n".join(lines) + "\n"
