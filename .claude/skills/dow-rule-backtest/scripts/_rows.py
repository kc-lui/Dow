"""Read the committed status table and run JSON; format rule rows. Presentation only, no statistics."""

from __future__ import annotations

import argparse
import math
import re
from pathlib import Path

RULES = ("R1", "R2", "R3", "R4", "R5", "R6", "R7", "R8")
FLAG_WORDS = (
    "pair-inconsistent",
    "not-distinguishable-from-random-walk-with-drift",
    "not-distinguishable-from-random-timing",
    "post-hoc-modified",
)
NO_LABEL = "n/a (robustness pair: labels come from DJ only)"
_CAVEAT = re.compile(r"(Mandatory caveat .*?never p_holm alone\.)")
_HASH = re.compile(r"decision table sha256 `([0-9a-f]{64})`")
_BOUND = re.compile(r"refute_bound=([-\d.]+|n/a) vs null ([-\d.]+)")


def build_parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(description="Print rule-backtest rows; --rerun runs dow backtest.")
    ap.add_argument("--rule", default="all", help="R1..R8 or all")
    ap.add_argument("--pair", action="append", choices=["DJ", "SP_IYT"], default=None)
    for flag, text in (
        ("--table", "rule_status_table.md (default analysis/rule_status_table.md)"),
        ("--run", "backtest_run_*.json (default: latest under reports/)"),
        ("--out", "output directory for --rerun (reports, run JSON and status table)"),
        ("--csv", "first leg CSV (--source csv)"),
        ("--csv-pair", "second leg CSV (defaults to --csv)"),
    ):
        ap.add_argument(flag, help=text)
    for flag in ("--json", "--rerun", "--no-sweeps"):
        ap.add_argument(flag, action="store_true")
    ap.add_argument("--source", choices=["clickhouse", "csv"], default="clickhouse")
    return ap


def rerun_command(a: argparse.Namespace, root: Path) -> list[str]:
    """``dow backtest`` argv writing everything into ``a.out``; ``--persist`` is never added."""
    out = Path(a.out).resolve()
    out.mkdir(parents=True, exist_ok=True)
    cmd = [str(root / ".venv" / "bin" / "dow"), "backtest", "--out", str(out)]
    cmd += ["--status-table", str(out / "rule_status_table.md"), "--source", a.source]
    cmd += [x for p in a.pair for x in ("--pair", p)]
    csvs = (("--csv", a.csv), ("--csv-pair", a.csv_pair))
    cmd += [x for f, v in csvs if v for x in (f, str(Path(v).resolve()))]  # cwd is the repo root
    cmd += ["--no-sweeps"] if a.no_sweeps else []
    assert "--persist" not in cmd
    return cmd


def read_table(path: Path) -> tuple[str, dict[str, dict]]:
    """``(decision_table_hash, {rule_id: {label, literature_label, notes, caveat, flags}})``."""
    text = path.read_text(encoding="utf-8")
    hash_match = _HASH.search(text)
    rows: dict[str, dict] = {}
    for line in text.splitlines():
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) == 9 and cells[0] in RULES:
            cav = _CAVEAT.search(cells[8])
            rows[cells[0]] = {
                "label": cells[3],
                "literature_label": cells[2],
                "notes": cells[8],
                "caveat": cav.group(1) if cav else None,
                "flags": [f for f in FLAG_WORDS if f in cells[8]],
            }
    return (hash_match.group(1) if hash_match else ""), rows


def latest_run(reports_dir: Path) -> Path | None:
    found = sorted(reports_dir.glob("backtest_run_*.json"))
    return found[-1] if found else None


def _f(x, fmt: str = ".4f") -> str:
    return "n/a" if x is None or math.isnan(x) else format(x, fmt)


def rule_row(run: dict, pair: str, rule: str, table_row: dict | None) -> dict:
    """One JSON-ready record for ``rule`` on ``pair``; the table row (if given) sets the label."""
    pr = run["pairs"][pair]["outcomes"][rule]["primary"]
    lab = run["pairs"][pair].get("labels", {}).get(rule, {})
    notes, table_row = pr.get("notes", ""), table_row or {}
    bound = _BOUND.search(notes)
    return {
        "rule_id": rule,
        "rule_key": pr["rule_key"],
        "pair": pair,
        "spec": pr["spec"],
        "period": f"{pr['period_start']}..{pr['period_end']}",
        "data_label": table_row.get("label") or lab.get("label") or NO_LABEL,
        "literature_label": run["literature"].get(rule, "unresolved"),
        "literature_ids": run["literature_ids"].get(rule, ""),
        "n": pr["n_obs"],
        "metric_name": pr["metric_name"],
        "horizon": pr["horizon"],
        "estimate": pr["metric_value"],
        "ci": [pr["ci_low"], pr["ci_high"]],
        "null_value": pr["null_value"],
        "p_raw": pr["p_value"],
        "p_holm": lab.get("p_holm"),
        "subsample_signs": pr["subsample_signs"],
        "refute_bound": None if not bound or bound.group(1) == "n/a" else float(bound.group(1)),
        "reason": lab.get("reason"),
        "caveat": table_row.get("caveat"),
        "flags": sorted({*table_row.get("flags", []), *(f for f in FLAG_WORDS if f in notes)}),
        "exploratory": "exploratory" in notes,
        "notes": notes,
    }


def header(head: dict) -> str:
    return (
        f"run {head['run_id']} | table {Path(head['table']).name} | decision_table_hash "
        f"{head['decision_table_hash'][:12]} | config_hash {head['config_hash'][:12]}"
    )


def render(row: dict) -> str:
    """Human-readable block for one rule row."""
    ci = f"[{_f(row['ci'][0])}, {_f(row['ci'][1])}]"
    bound, null = row["refute_bound"], row["null_value"]
    if bound is None:
        refute = "refutation bound n/a"
    else:
        side = "not refuted" if bound >= null else "bound on the wrong side of the null"
        refute = f"refutation bound {_f(bound)} vs null {_f(null)} -> {side}"
    first = f"{row['rule_id']} {row['rule_key']} | pair {row['pair']} | spec {row['spec']}"
    labels = f"  data label: {row['data_label']} | literature label: {row['literature_label']}"
    stats = f"  n={row['n']}  {row['metric_name']} {row['horizon']} = {_f(row['estimate'])}"
    stats += f"  95% CI {ci}  null {_f(null)}  p_raw={_f(row['p_raw'])}"
    lines = [
        f"{first} | {row['period']}",
        f"{labels} ({row['literature_ids']})",
        f"{stats}  p_holm={_f(row['p_holm'], '.6f')}",
        f"  sub-samples {row['subsample_signs']} | {refute}",
    ]
    if row["reason"]:
        lines.append(f"  reason: {row['reason']}")
    if row["exploratory"]:
        lines.append("  EXPLORATORY (DEV-11): single-group rows use information up to c+h")
    if row["flags"]:
        lines.append("  flags: " + ", ".join(row["flags"]))
    if row["caveat"]:
        lines.append(f"  caveat: {row['caveat']}")
    return "\n".join(lines)
