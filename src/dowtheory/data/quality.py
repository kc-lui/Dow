"""Data-integrity checks for ``dow.mkt_klines`` with results logged to ``ops_data_quality_log``.

Calendar approximation: expected sessions are business days (Mon-Fri) minus the US federal
holidays from ``USFederalHolidayCalendar``. That differs from the NYSE calendar: it wrongly
treats Columbus Day and Veterans Day as closed (the extra bars are harmless) and misses Good
Friday and ad-hoc closures (those appear as short gaps). Gap runs of at most
``max_gap_business_days`` are therefore summarised as info; only longer runs warn.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime

import pandas as pd
from pandas.tseries.holiday import USFederalHolidayCalendar

from dowtheory.config import DowConfig
from dowtheory.storage.clickhouse_client import ClickHouseClient

LOG_TABLE = "dow.ops_data_quality_log"
EPOCH = pd.Timestamp(0, tz="UTC")


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


def _check_duplicates(client: ClickHouseClient, symbol: str) -> list[QualityIssue]:
    """Count duplicate (symbol, ts_open) keys WITHOUT FINAL, as the raw table sees them."""
    dup = client.query_df(
        "SELECT count() AS keys, sum(c - 1) AS extra FROM ("
        "SELECT count() AS c FROM dow.mkt_klines WHERE symbol = {s:String} "
        "GROUP BY symbol, interval, ts_open HAVING c > 1)", {"s": symbol})
    extra = int(dup["extra"].iloc[0] or 0)
    if extra:
        return [QualityIssue(symbol, "duplicate", "error",
                             f"{extra} extra rows over {int(dup['keys'].iloc[0])} duplicated "
                             "keys (run OPTIMIZE TABLE dow.mkt_klines FINAL if they are re-loads)")]
    return []


def run_integrity_checks(
    client: ClickHouseClient,
    symbols: list[str],
    cfg: DowConfig,
    source_counts: dict[str, int] | None = None,
    log: bool = True,
    today: pd.Timestamp | None = None,
) -> list[QualityIssue]:
    """Run all checks for ``symbols``, optionally log them, and return the issues."""
    today = today or pd.Timestamp.now().normalize()
    issues: list[QualityIssue] = []
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
        issues.append(QualityIssue(
            symbol, "coverage", "info",
            f"first={df.index[0].date()} last={df.index[-1].date()} rows={len(df)}"))
        issues += check_gaps(symbol, df.index, cfg.data.max_gap_business_days)
        issues += _check_duplicates(client, symbol)
        issues += check_ohlc(symbol, df)
        issues += check_zero_volume(symbol, df, exchange)
        issues += check_stale(symbol, df.index[-1], today, cfg.data.stale_business_days)
    if source_counts:
        issues += row_reconciliation(client, source_counts)
    if log:
        log_issues(client, issues)
    return issues


def log_issues(client: ClickHouseClient, issues: list[QualityIssue]) -> None:
    """Append issues to ``dow.ops_data_quality_log`` (no-op for an empty list)."""
    if not issues:
        return
    now = datetime.now(UTC)
    frame = pd.DataFrame({
        "ts": [now] * len(issues),
        "symbol": [i.symbol for i in issues],
        "check_name": [i.check_name for i in issues],
        "severity": [i.severity for i in issues],
        "detail": [i.detail for i in issues],
        "bar_ts": [(i.bar_ts.tz_localize("America/New_York") if i.bar_ts is not None
                    and i.bar_ts.tzinfo is None else i.bar_ts or EPOCH) for i in issues],
    })
    client.insert_df(LOG_TABLE, frame)


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
