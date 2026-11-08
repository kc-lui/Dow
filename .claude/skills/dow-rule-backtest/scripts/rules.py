#!/usr/bin/env python3
"""Print rule-backtest rows (label, caveat, literature ids) from the committed table and run JSON.

``--rerun --out DIR`` shells to ``dow backtest`` writing into DIR only; it never passes ``--persist``.
No statistics are computed here: every number is read from the harness outputs.
"""

import json
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _anchor import ensure_venv

ROOT = ensure_venv()
import _rows as r


def main(argv=None) -> int:
    ap = r.build_parser()
    a = ap.parse_args(argv)
    a.pair = a.pair or ["DJ"]
    if a.rerun:
        a.out or ap.error("--rerun needs --out DIR")
        cmd = r.rerun_command(a, ROOT)
        print("running:", " ".join(cmd))
        return subprocess.run(cmd, cwd=ROOT, check=False).returncode
    table = Path(a.table) if a.table else ROOT / "analysis" / "rule_status_table.md"
    run_path = Path(a.run) if a.run else r.latest_run(ROOT / "reports")
    run_path or ap.error("no reports/backtest_run_*.json found; pass --run PATH")
    table_hash, table_rows = r.read_table(table)
    run = json.loads(Path(run_path).read_text(encoding="utf-8"))
    rules = list(r.RULES) if a.rule == "ALL" else [a.rule]
    rows = [
        r.rule_row(run, p, rule, table_rows.get(rule) if p == "DJ" else None)
        for p in a.pair
        if p in run["pairs"]
        for rule in rules
    ]
    head = {
        "run_id": run["run_id"],
        "table": str(table),
        "decision_table_hash": table_hash,
        "run_table_hash": run["table_hash"],
        "config_hash": run["config_hash"],
    }
    if a.json:
        print(json.dumps({**head, "rules": rows}))
    else:
        print(r.header(head), *map(r.render, rows), sep="\n\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
