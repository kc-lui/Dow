#!/usr/bin/env python3
"""Thin CLI over ``dowtheory.trend``: print the trend state and its signals (+ JSON)."""

import argparse
import json
import sys
from dataclasses import replace
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _anchor import ensure_venv

ensure_venv()
from _table import json_doc, signal_row, signals_table, state_row, state_table, summary_line

from dowtheory.config import load_config
from dowtheory.data.loader import load_klines
from dowtheory.swings import detect_multiscale, swings_as_of
from dowtheory.trend import run_trend, warmup_note


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--symbol", help="required for clickhouse; defaults to the CSV file stem")
    ap.add_argument("--source", choices=["clickhouse", "csv"], default="clickhouse")
    ap.add_argument("--csv")
    ap.add_argument("--start")
    ap.add_argument("--end")
    ap.add_argument("--strict", action=argparse.BooleanOptionalAction, default=None)
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args(argv)
    if a.source == "csv" and a.csv and not a.symbol:
        a.symbol = Path(a.csv).stem.upper()
    if not a.symbol:
        ap.error("--symbol is required (or --source csv --csv PATH)")
    cfg = load_config()
    if a.strict is not None:
        cfg = replace(cfg, trend=replace(cfg.trend, require_lower_high_for_reversal=a.strict))
    df = load_klines(a.symbol, a.start, a.end, source=a.source, csv_path=a.csv, cfg=cfg)
    last = len(df) - 1  # same driving as dowtheory.analysis.analyze
    scales = detect_multiscale(df["close"], cfg, df["high"], df["low"], symbol=a.symbol)
    state, signals, _ = run_trend(df["close"], swings_as_of(scales["secondary"], last), cfg)
    strict, tol = cfg.trend.require_lower_high_for_reversal, cfg.trend.equal_extreme_tol
    st, rows = state_row(state), [signal_row(s) for s in signals]
    print(state_table(st))
    print()
    print(signals_table(rows))
    print(summary_line(rows, a.symbol, df, strict, tol))
    note = warmup_note(signals, df.index[0].date())
    print(note)
    if a.json:
        doc = json_doc(a.symbol, df, strict, tol, note)
        print(json.dumps(doc | {"trend_state": st, "signals": rows}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
