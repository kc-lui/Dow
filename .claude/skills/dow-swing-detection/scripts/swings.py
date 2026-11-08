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
from dowtheory.config import load_config
from dowtheory.data.loader import load_klines
from dowtheory.swings import detect_multiscale, secondary_pct_for

COLS = ["ts", "kind", "price", "confirmed_ts", "scale", "amplitude_pct", "duration_days", "retrace", "flags"]


def row(s) -> dict:
    return {"ts": s.ts.isoformat(), "kind": s.kind, "price": float(s.price), "scale": s.scale,
            "confirmed_ts": s.confirmed_ts.isoformat(), "amplitude_pct": float(s.amplitude_pct),
            "duration_days": s.duration_days, "flags": s.flags,
            "retrace_ratio": None if s.retrace_ratio is None else float(s.retrace_ratio)}


def fmt(r: dict) -> str:
    retrace = "-" if r["retrace_ratio"] is None else f"{r['retrace_ratio']:.3f}"
    flags = ",".join(k for k, v in r["flags"].items() if v) or "-"
    return (f"| {r['ts']} | {r['kind']} | {r['price']:.2f} | {r['confirmed_ts']} | {r['scale']} | "
            f"{100 * r['amplitude_pct']:.2f}% | {r['duration_days']} | {retrace} | {flags} |")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--symbol", required=True)
    ap.add_argument("--source", choices=["clickhouse", "csv"], default="clickhouse")
    ap.add_argument("--csv"), ap.add_argument("--start"), ap.add_argument("--end")
    ap.add_argument("--scale", choices=["minor", "secondary", "both"], default="both")
    ap.add_argument("--method", choices=["pct", "atr", "pivot"]), ap.add_argument("--json", action="store_true")
    a = ap.parse_args(argv)
    cfg = load_config()
    cfg = replace(cfg, swings=replace(cfg.swings, method=a.method or cfg.swings.method))
    df = load_klines(a.symbol, a.start, a.end, source=a.source, csv_path=a.csv, cfg=cfg)
    sw, sec_pct = cfg.swings, secondary_pct_for(cfg, a.symbol)
    scales = detect_multiscale(df["close"], cfg, df["high"], df["low"], symbol=a.symbol)
    rows = sorted((row(s) for k, v in scales.items() if a.scale in ("both", k) for s in v),
                  key=lambda r: (r["ts"], r["scale"]))
    print("| " + " | ".join(COLS) + " |\n|" + "---|" * len(COLS) + "\n" + "\n".join(map(fmt, rows)))
    print(f"\n{len(rows)} swings | {a.symbol} | bars {len(df)} {df.index[0].date()} -> {df.index[-1].date()}"
          f" | method {sw.method} minor {sw.minor_pct} secondary {sec_pct} min_sessions {sw.secondary_min_sessions}")
    if a.json:
        print(json.dumps({"symbol": a.symbol, "method": sw.method, "bars": len(df), "swings": rows, "thresholds": {
            "minor_pct": sw.minor_pct, "secondary_pct": sec_pct, "secondary_min_sessions": sw.secondary_min_sessions}}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
