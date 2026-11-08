#!/usr/bin/env python3
"""Thin CLI over ``dowtheory.analysis``: markdown report, PNG chart and JSON twin of one run."""

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _anchor import ensure_venv

ensure_venv()
from dowtheory.analysis import analyze
from dowtheory.chart import chart_filename, render_chart
from dowtheory.config import load_config, load_pairs
from dowtheory.report import to_markdown


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    for flag in ("--symbol", "--pair", "--csv", "--csv-pair", "--start", "--end", "--as-of"):
        ap.add_argument(flag)
    ap.add_argument("--source", choices=["clickhouse", "csv"], default="clickhouse")
    ap.add_argument("--method", choices=["pct", "atr", "pivot"])
    ap.add_argument("--out-dir", default="outputs/charts", help="PNG dir; JSON goes to ../json")
    ap.add_argument("--no-chart", action="store_true")
    ap.add_argument("--json", action="store_true", help="also print the JSON document")
    a = ap.parse_args(argv)
    if (a.source == "csv") != bool(a.csv):
        ap.error("--source csv and --csv PATH must be given together")
    if a.csv:  # CSV legs: pair file defaults to --csv, symbols to file stems
        a.csv_pair = a.csv_pair or a.csv
        a.symbol = a.symbol or Path(a.csv).stem.upper()
        a.pair = a.pair or Path(a.csv_pair).stem.upper()
    elif a.symbol and a.pair is None:  # same default as ``dow analyze``: partner from pairs.yaml
        a.pair = next((p[1] for p in load_pairs().values() if p[0] == a.symbol), None)
    a.symbol or ap.error("--symbol is required (or --csv PATH with --source csv)")
    as_of = a.as_of or a.end  # ``--end`` is an alias of ``--as-of`` (bars are cut there)
    result, df, df_pair = analyze(
        a.symbol, a.pair, as_of, a.start, a.source, a.csv, a.csv_pair, a.method, load_config()
    )
    out_dir = Path(a.out_dir)
    json_dir = out_dir.parent / "json"
    json_dir.mkdir(parents=True, exist_ok=True)
    json_path = json_dir / chart_filename(result).replace(".png", ".json")
    json_path.write_text(result.to_json(), encoding="utf-8")
    print(to_markdown(result))
    print(f"JSON: {json_path}")
    if not a.no_chart:
        print(f"Chart: {render_chart(result, df, df_pair, out_dir)}")
    if a.json:
        print(json.dumps(json.loads(result.to_json())))
    return 0


if __name__ == "__main__":
    sys.exit(main())
