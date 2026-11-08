"""Command line entry point: ``dow init-db | fetch | check | analyze | backtest``."""

from __future__ import annotations

import argparse
import logging
import runpy
import sys
from collections.abc import Sequence

import pandas as pd

from dowtheory.config import DowConfig, load_config, project_root
from dowtheory.data import quality, stooq_fetcher, yahoo_fetcher
from dowtheory.data.bars import to_insert_frame
from dowtheory.data.quality import QualityIssue
from dowtheory.storage.clickhouse_client import ClickHouseClient

logger = logging.getLogger("dow")
NOT_IMPLEMENTED = 2


def _fetch_one(source: str, symbol: str, start: str | None, cfg: DowConfig) -> pd.DataFrame:
    exchange = cfg.data.exchange_map.get(symbol)
    if source == "stooq":
        bars = stooq_fetcher.fetch_daily(symbol, exchange=exchange)
        return bars[bars["ts_open"] >= pd.Timestamp(start, tz="America/New_York")] if start else bars
    return yahoo_fetcher.fetch_daily(symbol, start=start, exchange=exchange)


def _coverage_issue(symbol: str, bars: pd.DataFrame, source: str, note: str) -> QualityIssue:
    return QualityIssue(
        symbol, "coverage", "info",
        f"{note} source={source} first={bars['ts_open'].iloc[0].date()} "
        f"last={bars['ts_open'].iloc[-1].date()} rows={len(bars)}")


def cmd_init_db(args: argparse.Namespace) -> int:
    script = project_root() / "scripts" / "init_clickhouse.py"
    return int(runpy.run_path(str(script), run_name="init_clickhouse")["main"]())


def cmd_fetch(args: argparse.Namespace) -> int:
    cfg = load_config(args.config)
    symbols = args.symbols or cfg.data.symbols
    status = 0
    issues: list[QualityIssue] = []
    counts: dict[str, int] = {}
    with ClickHouseClient() as client:
        for symbol in symbols:
            try:
                bars = _fetch_one(args.source, symbol, args.start, cfg)
            except (ValueError, stooq_fetcher.SourceUnavailable) as exc:
                print(f"FAIL {symbol}: {exc}", file=sys.stderr)
                issues.append(QualityIssue(symbol, "coverage", "error", f"fetch failed: {exc}"))
                status = 1
                continue
            if args.probe:
                issues.append(_coverage_issue(symbol, bars, args.source, "probe"))
            else:
                client.insert_df("dow.mkt_klines", to_insert_frame(bars))
                issues.append(_coverage_issue(symbol, bars, args.source, "backfill"))
                if not args.start:
                    counts[symbol] = len(bars)
            print(issues[-1].symbol, issues[-1].detail)
        if not args.probe and counts:
            issues += quality.row_reconciliation(client, counts)
        quality.log_issues(client, issues)
    return 1 if status or quality.exit_status(issues) else 0


def run_check(symbols: list[str] | None = None, config: str | None = None) -> tuple[int, str]:
    """Run integrity checks; return (exit status, human report)."""
    cfg = load_config(config)
    with ClickHouseClient() as client:
        issues = quality.run_integrity_checks(client, symbols or cfg.data.symbols, cfg)
    return quality.exit_status(issues), quality.format_report(issues)


def cmd_check(args: argparse.Namespace) -> int:
    status, report = run_check(args.symbols, args.config)
    print(report)
    return status


def _stub(name: str):
    def run(args: argparse.Namespace) -> int:
        print(f"{name}: not implemented in P2")
        return NOT_IMPLEMENTED
    return run


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="dow", description="Dow Theory toolkit")
    parser.add_argument("--config", default=None, help="path to dow.yaml (default $DOW_CONFIG)")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("init-db", help="create dow tables").set_defaults(func=cmd_init_db)
    p = sub.add_parser("fetch", help="fetch bars and insert into dow.mkt_klines")
    p.add_argument("--symbols", nargs="+")
    p.add_argument("--probe", action="store_true", help="fetch and log coverage only")
    p.add_argument("--source", choices=["yfinance", "stooq"], default="yfinance")
    p.add_argument("--start", default=None)
    p.set_defaults(func=cmd_fetch)
    p = sub.add_parser("check", help="run integrity checks (exit 1 on any error)")
    p.add_argument("--symbols", nargs="+")
    p.set_defaults(func=cmd_check)
    sub.add_parser("analyze", help="(P3)").set_defaults(func=_stub("analyze"))
    sub.add_parser("backtest", help="(P4)").set_defaults(func=_stub("backtest"))
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
    args = build_parser().parse_args(argv)
    return int(args.func(args))


if __name__ == "__main__":
    sys.exit(main())
