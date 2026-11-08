"""Markdown and JSON outputs of a backtest run."""

from __future__ import annotations

import dataclasses
import datetime as dt
import json
import math
from pathlib import Path
from typing import Any

import numpy as np

from dowtheory.backtest import protocol as proto
from dowtheory.backtest.protocol import BGK_CAVEAT, FAMILY
from dowtheory.backtest.results import RuleResult
from dowtheory.backtest.runner import LABEL_PAIR, BacktestRun, PairRun
from dowtheory.config import project_root

TITLES = {
    "R1": "Trend persistence",
    "R2": "Reversal signal",
    "R3": "Two-index confirmation",
    "R4": "Secondary retracement",
    "R5": "Secondary duration",
    "R6": "Line breakout",
    "R7": "Volume confirmation",
    "R8": "Hamilton-style timing strategy",
}
EVENTS = {
    "R1": "Confirmed secondary swing counter to an established primary trend "
          "(`state(c)` BULL_PRIMARY with an L swing, BEAR_PRIMARY with an H swing). Success: the "
          "next secondary swing makes a new extreme (HH / LL) beyond `equal_extreme_tol`. "
          "Metric `p_extend`, null 0.5, exact binomial, Wilson CI.",
    "R2": "`REVERSAL_UP` / `REVERSAL_DOWN` on `^DJI` at `Signal.idx`. Metric: mean of "
          "`sgn * (F_h(c) - mean_t F_h(t))`, `F_h(c) = ln(P[c+1+h] / P[c+1])`, primary h = 60. "
          "Random-placement test, cluster-bootstrap CI.",
    "R3": "Reversals on `^DJI` matched cycle-aware with `^DJT` (event bar = `confirmed_ts`) versus "
          "reversals with no match by `c + h` (event bar `c`). Metric: difference of mean signed "
          "excess returns, h = 60. Label permutation test, within-group cluster-bootstrap CI.",
    "R4": "Confirmed counter-trend secondary swings with a retrace ratio. Metric: share with "
          "1/3 <= rr <= 2/3, null 1/3 (uniform rr). Exact binomial, Wilson CI; the label uses "
          "the worst point of the `secondary_pct` grid.",
    "R5": "Same events as R4. Metric: share lasting 21 to 90 calendar days, null 0.5. Exact "
          "binomial, Wilson CI; the label uses the worst point of the `secondary_pct` grid.",
    "R6": "Line breakouts confirmed by both averages (event bar `confirmed_ts`). Metric: share "
          "with `sgn * F_20(c) > 0`, null 0.5. Exact binomial, Wilson CI.",
    "R7": "Consecutive secondary legs in a PRIMARY state, 2000-01-03 onward. Metric: share of "
          "pairs where the with-trend leg has higher mean volume, null 0.5. Exact binomial.",
    "R8": "Long when `^DJI` is BULL_PRIMARY and the pair is confirmed, else cash; executed one "
          "bar after the signal, 10 bps per side. Metric: Sharpe(strategy) - Sharpe(buy-and-hold) "
          "of daily log returns; null 0. Joint stationary block bootstrap (block 20).",
}
NO_P = float("nan")


def f(x: Any, nd: int = 4) -> str:
    """Format a number; ``nan`` and ``None`` become ``n/a``."""
    if x is None or (isinstance(x, float) and math.isnan(x)):
        return "n/a"
    return f"{x:.{nd}f}" if isinstance(x, float) else str(x)


def row_table(rows: list[RuleResult]) -> list[str]:
    out = ["| spec | variant | metric | horizon | n | value | CI low | CI high | p raw | notes |",
           "|---|---|---|---|---|---|---|---|---|---|"]
    for r in rows:
        out.append(
            f"| {r.spec} | {r.variant} | {r.metric_name} | {r.horizon} | {r.n_obs} | "
            f"{f(r.metric_value)} | {f(r.ci_low)} | {f(r.ci_high)} | {f(r.p_value)} | "
            f"{r.notes.replace('|', '/')} |"
        )
    return out


def sweep_summary(rows: list[RuleResult]) -> list[str]:
    vals = np.array([r.metric_value for r in rows if not math.isnan(r.metric_value)])
    if vals.size == 0:
        return ["No sweep point had a defined metric."]
    return [
        (f"Range of the primary metric over {vals.size} grid points (not a selected optimum): "
        f"min {vals.min():.4f}, median {float(np.median(vals)):.4f}, max {vals.max():.4f}.")
    ]


def _p_family(pr: PairRun, rule: str) -> tuple[str, str]:
    lab = pr.labels.get(rule)
    if not lab:
        return "n/a", "n/a"
    return f(lab["p_label"], 6), f(lab["p_holm"], 6)


def rule_report(run: BacktestRun, pr: PairRun, rule: str, protocol_text: str) -> str:
    o = pr.outcomes[rule]
    p = o.primary
    lab = pr.labels.get(rule)
    p_label, p_holm = _p_family(pr, rule)
    li = o.label_input
    lines = [
        f"# {rule} {TITLES[rule]} (`rule_key: {p.rule_key}`)",
        "",
        (f"Pair `{pr.pair}` ({pr.symbols[0]}, {pr.symbols[1]}), {pr.first} to {pr.last}, "
        f"{pr.n_bars} bars. Specification `{pr.primary_spec}`. Run `{run.run_id}`."),
        (f"Config hash `{pr.config_hash}`. Decision table sha256 `{run.table_hash}`. "
        f"Bootstrap iterations {run.n_iter}, seed {proto.SEED}."),
        "",
        "## Event definition",
        "",
        EVENTS[rule],
        "",
        "## Result",
        "",
        "| field | value |",
        "|---|---|",
        f"| events n | {p.n_obs} |",
        f"| clusters | {f(p.n_clusters)} |",
        f"| right-censored | {p.n_censored} |",
        f"| metric | {p.metric_name} {p.horizon} |",
        f"| estimate | {f(p.metric_value)} |",
        f"| 95% CI | [{f(p.ci_low)}, {f(p.ci_high)}] |",
        f"| null value | {f(p.null_value)} |",
        f"| p raw (one-sided, predicted direction) | {f(p.p_value, 6)} |",
        f"| p used in the Holm family | {p_label} |",
        f"| p Holm (family of 8) | {p_holm} |",
        (f"| Bonferroni one-sided upper bound (level {1 - 0.05 / 8:.5f}) | "
        f"{f(li.bound_bonf)} |"),
        f"| sub-sample split | {pr.split} (A up to and including, B after) |",
        f"| sub-sample A | {f(li.sub_A.estimate)} (n = {li.sub_A.n}) |",
        f"| sub-sample B | {f(li.sub_B.estimate)} (n = {li.sub_B.n}) |",
        f"| sub-sample signs vs null | {p.subsample_signs} |",
        "",
        "## Label",
        "",
    ]
    if lab:
        lines += [
            f"- Data label: **{lab['label']}**. Reason: {lab['reason']}.",
            (f"- Literature label: **{lab['literature_label']}** "
            f"(registry rows {run.literature_ids.get(rule) or 'none'})."),
            f"- Refutation bound actually computed: one-sided {1 - 0.05 / 8:.5f} upper bound "
            f"{f(lab['bound'], 4)} against null {f(p.null_value, 4)}; "
            + ("it lies below the null" if lab['bound'] < p.null_value
               else "it is undefined" if math.isnan(lab['bound'])
               else "it does not lie below the null, so refutation is excluded")
            + ".",
            *(f"- Flag: `{x}`." for x in pr.flags.get(rule, [])),
        ]
    else:
        lines.append(f"- No label: `{pr.pair}` is a robustness pair (labels come from `DJ` only).")
    if rule == "R1":
        sim = o.details.get("p_sim")
        lines += ["", "### Mandatory caveat (R11 F1)", "",
                  proto.R1_CAVEAT.format(p_sim="n/a" if sim is None else f"{sim:.4f}")]
    if rule in proto.EXPLORATORY_VARIANTS:
        which = ("every row of this report" if rule == "R3" else
                 "the `single` and `conf_minus_single` rows")
        lines += ["", "### Exploratory rows (R11 F4)", "",
                  (f"For {which}, the single group is classified with information up to `c + h`, "
                  "the outcome window itself, and a reversal matched later than `c + h` is in both "
                  "groups. Treat these rows as exploratory; the label is unchanged "
                  "(recommended redefinition for v3 in `analysis/protocol_deviations.md`).")]
    lines += ["", "## Descriptive and robustness rows", "", *row_table(o.rows)]
    sweep = pr.sweep_rows.get(rule, [])
    if sweep:
        lines += ["", "## Specification sweep (descriptive)", "", *sweep_summary(sweep), "",
                  *row_table(sweep)]
    if rule in proto.WORST_GRID_RULES and pr.grids.get(rule):
        lines += ["", "### Secondary-threshold grid (15-session filter), label inputs", "",
                  "| secondary_pct | n | estimate | p raw | Bonferroni bound |", "|---|---|---|---|---|"]
        for g, res in sorted(pr.grids[rule].items()):
            lines.append(f"| {g:g} | {res.n} | {f(res.estimate)} | {f(res.p_raw, 6)} | "
                         f"{f(res.bound_bonf)} |")
    lines += _extras(rule, o.details)
    lines += ["", "## Caveats", ""]
    caveats = proto.printed_caveats(protocol_text).get(rule, [])
    if rule == "R8" and not any(BGK_CAVEAT in c for c in caveats):
        caveats.append(BGK_CAVEAT)
    lines += [f"- {cav}" for cav in caveats]
    lines += ["", "### Data coverage (verbatim from the decision table, section 5)", ""]
    lines += [f"- {c}" for c in proto.coverage_caveats(protocol_text)]
    lines += ["", proto.VOLUME_CORRECTION]
    return "\n".join(lines) + "\n"


def _extras(rule: str, d: dict[str, Any]) -> list[str]:
    out: list[str] = []
    if rule == "R4" and "deciles" in d:
        out += ["", "### Retrace-ratio histogram (counter-trend legs)", "",
                "Deciles of rr in (0, 1], last entry rr > 1:", "", f"`{d['deciles']}`"]
    if rule == "R5" and "d_cal" in d:
        c, b = d["d_cal"], d["d_bar"]
        out += ["", "### Duration summary", "",
                (f"Calendar days: median {f(c['median'], 1)}, IQR [{f(c['q1'], 1)}, "
                f"{f(c['q3'], 1)}]. Trading bars: median {f(b['median'], 1)}, "
                f"IQR [{f(b['q1'], 1)}, {f(b['q3'], 1)}]. Compare the sweep rows with "
                "`f0` (no 15-session filter) next to the primary.")]
    if rule == "R8" and d.get("primary"):
        m = d["primary"]
        out += ["", "### Strategy against buy-and-hold (10 bps, long/cash)", "",
                "| | strategy | buy-and-hold |", "|---|---|---|",
                f"| Sharpe | {f(m['sharpe_strategy'])} | {f(m['sharpe_bh'])} |",
                f"| annual return (log) | {f(m['ann_ret_strategy'])} | {f(m['ann_ret_bh'])} |",
                f"| annual volatility | {f(m['ann_vol_strategy'])} | {f(m['ann_vol_bh'])} |",
                f"| max drawdown | {f(m['mdd_strategy'])} | {f(m['mdd_bh'])} |",
                "", (f"Time in market {f(m['time_in_market'])}; trades {m['trades']}; cumulative "
                f"log-return difference {f(m['cum_diff'])} (CI {f(m['cum_diff_ci'][0])} to "
                f"{f(m['cum_diff_ci'][1])}, p {f(m['p_cum'], 6)}). Price indices exclude "
                "dividends, which favours a strategy that is partly in cash."),
                f"Random-spell null p_spell = {f(d.get('p_spell'), 4)}.",
                f"Calls (descriptive, no label): {d.get('calls')}."]
    if rule == "R1" and "p_sim" in d:
        out += ["", (f"Drift-matched random-walk null: p_sim = {f(d['p_sim'], 4)} over "
                f"{d['n_sim']} paths (null mean p_extend {f(d['sim_mean'])}).")]
    return out


# --------------------------------------------------------------------------- status table
def _consistency_note(run: BacktestRun, rule: str) -> str:
    dj, other = run.pairs.get(LABEL_PAIR), [p for k, p in run.pairs.items() if k != LABEL_PAIR]
    if not dj or not other:
        return ""
    a = dj.outcomes[rule].label_input
    b = other[0].outcomes[rule].label_input
    if math.isnan(a.estimate) or math.isnan(b.estimate):
        return ""
    return "pair-inconsistent" if (a.estimate - a.null_value) * (b.estimate - b.null_value) < 0 else ""


def status_table(run: BacktestRun) -> str:
    pr = run.pairs[LABEL_PAIR]
    lines = [
        "# Rule status table",
        "",
        (f"Generated by `dow backtest` run `{run.run_id}` on {run.started:%Y-%m-%d %H:%M} UTC. "
        f"Pair `{LABEL_PAIR}`, specification `{pr.primary_spec}`, {pr.first} to {pr.last}. "
        f"Config hash `{pr.config_hash}`; decision table sha256 `{run.table_hash}`; "
        f"integrity report `{run.integrity_path or 'none'}`."),
        "",
        "| rule | rule_key | literature label | data label | n | effect | 95% CI | p_holm | notes |",
        "|---|---|---|---|---|---|---|---|---|",
    ]
    for r in FAMILY:
        o = pr.outcomes[r]
        p = o.primary
        lab = pr.labels[r]
        notes = [lab["reason"], f"p_raw={f(p.p_value, 4)}", f"signs {p.subsample_signs}"]
        if r in proto.WORST_GRID_RULES:
            notes.append(f"p_label_worst_grid={f(lab['p_label'], 4)}")
        if p.n_clusters is not None:
            notes.append(f"clusters={p.n_clusters}")
        notes.append(f"refute_bound={f(lab['bound'], 4)} vs null {f(p.null_value, 4)}")
        notes.append(f"lit ids {run.literature_ids.get(r) or 'none'}")
        if r == "R1":
            sim = o.details.get("p_sim")
            notes.append(proto.R1_CAVEAT.format(p_sim="n/a" if sim is None else f"{sim:.4f}"))
        notes += pr.flags.get(r, [])
        cons = _consistency_note(run, r)
        if cons:
            notes.append(cons)
        notes += [f"label computed under {d}" for d in run.deviations]
        lines.append(
            f"| {r} | {p.rule_key} | {lab['literature_label']} | {lab['label']} | {p.n_obs} | "
            f"{p.metric_name}{('_' + p.horizon) if p.horizon != 'na' else ''} = "
            f"{f(p.metric_value)} | [{f(p.ci_low)}, {f(p.ci_high)}] | {f(lab['p_holm'], 6)} | "
            f"{'; '.join(notes)} |"
        )
    lines += ["", ("Effects are in the metric's own units (a proportion for R1, R4 to R7; log "
              "return for R2 and R3; annualised Sharpe difference for R8). A data label does "
              "not assert economic significance.")]
    return "\n".join(lines) + "\n"


# --------------------------------------------------------------------------- json + files
def _clean(obj: Any) -> Any:
    if dataclasses.is_dataclass(obj) and not isinstance(obj, type):
        return _clean(dataclasses.asdict(obj))
    if isinstance(obj, dict):
        return {str(k): _clean(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [_clean(v) for v in obj]
    if isinstance(obj, (np.floating, np.integer)):
        return _clean(obj.item())
    if isinstance(obj, float):
        return None if math.isnan(obj) or math.isinf(obj) else obj
    if isinstance(obj, (dt.date, dt.datetime)):
        return obj.isoformat()
    return obj


def run_json(run: BacktestRun) -> str:
    return json.dumps(_clean(run), indent=2, allow_nan=False)


def write_outputs(
    run: BacktestRun, out_dir: Path, status_path: Path | None, root: Path | None = None
) -> list[Path]:
    """Write per-rule reports, the run JSON and (when ``DJ`` ran) the status table."""
    root = root or project_root()
    text = (root / "analysis" / "decision_table.md").read_text(encoding="utf-8")
    out_dir.mkdir(parents=True, exist_ok=True)
    written: list[Path] = []
    for pair, pr in run.pairs.items():
        for r in FAMILY:
            suffix = "" if pair == LABEL_PAIR else f"_{pair}"
            path = out_dir / f"rule_{r}{suffix}.md"
            path.write_text(rule_report(run, pr, r, text), encoding="utf-8")
            written.append(path)
    stamp = run.started.strftime("%Y%m%d_%H%M%S")
    jpath = out_dir / f"backtest_run_{stamp}.json"
    jpath.write_text(run_json(run), encoding="utf-8")
    written.append(jpath)
    if LABEL_PAIR in run.pairs and status_path is not None:
        status_path.parent.mkdir(parents=True, exist_ok=True)
        status_path.write_text(status_table(run), encoding="utf-8")
        written.append(status_path)
    return written

