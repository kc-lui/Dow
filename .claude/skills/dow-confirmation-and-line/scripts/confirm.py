#!/usr/bin/env python3
"""Thin CLI over ``dowtheory.confirmation`` and ``dowtheory.line``: pair status, lines, volume."""

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _anchor import ensure_venv

ensure_venv()
import _table as t

from dowtheory.config import load_config
from dowtheory.confirmation import confirm_signal, pair_confirm, volume_confirms
from dowtheory.data.loader import load_klines
from dowtheory.line import detect_lines
from dowtheory.swings import detect_multiscale, swings_as_of
from dowtheory.trend import run_trend


def _leg(df, cfg, symbol):  # swings confirmed by the last bar, then the replayed trend
    scales = detect_multiscale(df["close"], cfg, df["high"], df["low"], symbol=symbol)
    secondary = swings_as_of(scales["secondary"], len(df) - 1)
    return *run_trend(df["close"], secondary, cfg)[:2], secondary


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    for flag in ("--symbol", "--pair", "--csv", "--csv-pair", "--start", "--end"):
        ap.add_argument(flag)
    ap.add_argument("--source", choices=["clickhouse", "csv"], default="clickhouse")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args(argv)
    if a.source == "csv" and a.csv:  # CSV legs: pair file defaults to --csv, symbols to file stems
        a.csv_pair = a.csv_pair or a.csv
        a.symbol = a.symbol or Path(a.csv).stem.upper()
        a.pair = a.pair or Path(a.csv_pair).stem.upper()
    (a.symbol and a.pair) or ap.error("--symbol and --pair are required (or --csv PATH)")
    cfg = load_config()
    df = load_klines(a.symbol, a.start, a.end, source=a.source, csv_path=a.csv, cfg=cfg)
    df_b = load_klines(a.pair, a.start, a.end, source=a.source, csv_path=a.csv_pair, cfg=cfg)
    df, df_b = df.loc[df.index.isin(df_b.index)], df_b.loc[df_b.index.isin(df.index)]  # inner join
    df.empty and ap.error(f"no common sessions for {a.symbol} and {a.pair}")
    state, signals, secondary = _leg(df, cfg, a.symbol)
    state_b, signals_b, _ = _leg(df_b, cfg, a.pair)
    c, max_days, closes = cfg.line, cfg.confirmation.max_days, (df["close"], df_b["close"])
    lines = detect_lines(*closes, c.band_pct, c.min_sessions, None, max_days, c.max_drift_frac)
    args = (signals, signals_b, max_days, df.index[-1].date())
    pair = pair_confirm(state, state_b, *args)
    rows = [t.signal_row(s, confirm_signal(s, *args)) for s in signals]
    vol = volume_confirms(df, secondary)
    report = t.Report(a, df, cfg, pair, state, state_b, rows, signals_b, lines, vol)
    print(report.text(), *([json.dumps(report.doc())] if a.json else []), sep="\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
