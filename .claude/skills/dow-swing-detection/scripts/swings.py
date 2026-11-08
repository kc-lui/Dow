#!/usr/bin/env python3
"""Thin CLI over ``dowtheory.swings``: print confirmed swings as a markdown table (+ JSON)."""

import argparse
import json
import sys
from dataclasses import replace
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _anchor import ensure_venv

ensure_venv()
from _table import markdown_table, summary_line, swing_row

from dowtheory.config import load_config
from dowtheory.data.loader import load_klines
from dowtheory.swings import detect_multiscale, secondary_pct_for


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--symbol", help="required for clickhouse; defaults to the CSV file stem")
    ap.add_argument("--source", choices=["clickhouse", "csv"], default="clickhouse")
    ap.add_argument("--csv")
    ap.add_argument("--start")
    ap.add_argument("--end")
    ap.add_argument("--method", choices=["pct", "atr", "pivot"])
    ap.add_argument("--scale", choices=["minor", "secondary", "both"], default="both")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args(argv)
    if a.source == "csv" and a.csv and not a.symbol:
        a.symbol = Path(a.csv).stem.upper()
    if not a.symbol:
        ap.error("--symbol is required (or --source csv --csv PATH)")
    cfg = load_config()
    cfg = replace(cfg, swings=replace(cfg.swings, method=a.method or cfg.swings.method))
    df = load_klines(a.symbol, a.start, a.end, source=a.source, csv_path=a.csv, cfg=cfg)
    sw, sec_pct = cfg.swings, secondary_pct_for(cfg, a.symbol)
    scales = detect_multiscale(df["close"], cfg, df["high"], df["low"], symbol=a.symbol)
    minor_keys = {(m.idx, m.kind) for m in scales["minor"]}
    rows = [swing_row(s, None) for s in scales["minor"] if a.scale != "secondary"]
    if a.scale != "minor":
        rows += [swing_row(s, (s.idx, s.kind) in minor_keys) for s in scales["secondary"]]
    rows.sort(key=lambda r: (r["ts"], r["scale"]))
    print(markdown_table(rows))
    print(summary_line(rows, a.symbol, df, sw, sec_pct))
    if a.json:
        thresholds = {
            "minor_pct": sw.minor_pct,
            "secondary_pct": sec_pct,
            "secondary_min_sessions": sw.secondary_min_sessions,
        }
        doc = {"symbol": a.symbol, "method": sw.method, "bars": len(df), "thresholds": thresholds}
        print(json.dumps(doc | {"swings": rows}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
