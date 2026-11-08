"""Orchestration: load a pair, run R1..R8 over the specification grid, label, and persist."""

from __future__ import annotations

import copy
import datetime as dt
import logging
import time
import uuid
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import pandas as pd

from dowtheory.backtest import protocol as proto
from dowtheory.backtest.events import (
    build_objects,
    make_pair_frame,
    spec_name,
    split_date,
    with_line,
    with_swings,
    with_trend,
)
from dowtheory.backtest.labels import (
    PrimaryResult,
    label_all,
    load_canonical_rules,
    resolve_literature,
)
from dowtheory.backtest.ledger import insert_ledger, ledger_frame
from dowtheory.backtest.protocol import FAMILY, Protocol
from dowtheory.backtest.results import RuleOutcome, RuleResult
from dowtheory.backtest.rules import RULES
from dowtheory.config import DowConfig, load_config, load_pairs, project_root
from dowtheory.data.loader import load_klines
from dowtheory.storage.clickhouse_client import ClickHouseClient

logger = logging.getLogger(__name__)
LABEL_PAIR = "DJ"
SWEEP_RULES_WITHOUT_GRID = ("R4", "R5")


@dataclass
class PairRun:
    """All results for one pair."""

    pair: str
    symbols: tuple[str, str]
    n_bars: int
    first: dt.date
    last: dt.date
    split: dt.date
    primary_spec: str
    config_hash: str
    outcomes: dict[str, RuleOutcome]
    sweep_rows: dict[str, list[RuleResult]] = field(default_factory=dict)
    grids: dict[str, dict[float, PrimaryResult]] = field(default_factory=dict)
    labels: dict[str, dict[str, Any]] = field(default_factory=dict)
    flags: dict[str, list[str]] = field(default_factory=dict)

    def all_rows(self) -> list[RuleResult]:
        """Every ledger row of this pair, primary rows first within each rule."""
        out: list[RuleResult] = []
        for r in FAMILY:
            o = self.outcomes[r]
            out.append(o.primary)
            out.extend(o.rows)
            out.extend(self.sweep_rows.get(r, []))
        return out


@dataclass
class BacktestRun:
    run_id: str
    started: dt.datetime
    runtime_s: float
    config_hash: str
    table_hash: str
    table_hash_scoped: str
    integrity_path: str
    deviations: list[str]
    n_iter: int
    pairs: dict[str, PairRun]
    literature: dict[str, str]
    literature_ids: dict[str, str]
    sweeps: bool
    notes: list[str] = field(default_factory=list)


# --------------------------------------------------------------------------- specification grid
def sweep_configs(cfg: DowConfig, second_symbol: str) -> list[tuple[str, DowConfig]]:
    """``(variant, config)`` points of the protocol's robustness grid (primary excluded)."""
    points: list[tuple[str, DowConfig]] = []
    for pct in proto.GRID_SECONDARY_PCT:
        for sessions in proto.SWEEP_SESSIONS:
            points.append(("primary", with_swings(cfg, secondary_pct=pct,
                                                  secondary_min_sessions=sessions)))
    for minor in proto.SWEEP_MINOR_PCT:
        points.append(("primary", with_swings(cfg, minor_pct=minor)))
    for tol in proto.SWEEP_EQUAL_TOL:
        points.append(("tol0" if tol == 0 else "primary", with_trend(cfg, equal_extreme_tol=tol)))
    points.append(("djt0.12", with_swings(cfg, per_symbol_secondary_pct={second_symbol: 0.12})))
    points.append(("primary", with_swings(cfg, method="atr")))
    points.append(("primary", with_swings(cfg, method="pivot")))
    seen = {cfg.config_hash()}
    out = []
    for variant, c in points:
        h = c.config_hash()
        if h not in seen:
            seen.add(h)
            out.append((variant, c))
    return out


def line_configs(cfg: DowConfig) -> list[tuple[str, DowConfig]]:
    """R6 line grid: band x min_sessions x max_drift_frac (primary excluded)."""
    seen = {cfg.config_hash()}
    out = []
    for band in proto.LINE_BANDS:
        for sessions in proto.LINE_MIN_SESSIONS:
            for drift in proto.LINE_DRIFT:
                c = with_line(cfg, band_pct=band, min_sessions=sessions,
                              max_drift_frac=float("inf") if drift is None else drift)
                if c.config_hash() in seen:
                    continue
                seen.add(c.config_hash())
                tag = "none" if drift is None else f"{drift:g}"
                out.append((f"band{band:g}_min{sessions}_drift{tag}", c))
    return out


def _tagged(row: RuleResult, variant: str, note: str) -> RuleResult:
    r = copy.copy(row)
    r.variant, r.label = variant, "n/a"
    r.notes = f"{note}; {r.notes}".strip("; ")
    return r


# --------------------------------------------------------------------------- one pair
def run_pair(
    pair: str, symbols: tuple[str, str], frame: pd.DataFrame, cfg: DowConfig, protocol: Protocol,
    *, sweeps: bool = True, heavy: bool = True, workers: int = 1,
    canonical: dict[str, dict[str, str]] | None = None,
) -> PairRun:
    """Run every rule on the primary specification, then the grid, and label the DJ pair."""
    objs = build_objects(frame, cfg, symbols)
    spec = spec_name(cfg)
    outcomes = {
        r: RULES[r](frame, objs, cfg, protocol, pair=pair, spec=spec, heavy=heavy, workers=workers)
        for r in FAMILY
    }
    first, last = objs.date_at(0), objs.date_at(objs.last)
    run = PairRun(pair, symbols, len(frame), first, last, split_date(first, last), spec,
                  cfg.config_hash(), outcomes)
    run.grids = {r: {} for r in proto.WORST_GRID_RULES}
    if cfg.swings.method == "pct" and cfg.swings.secondary_min_sessions == 15:
        for r in proto.WORST_GRID_RULES:
            run.grids[r][cfg.swings.secondary_pct] = outcomes[r].label_input
    run.sweep_rows = {r: [] for r in FAMILY}
    for variant, c in sweep_configs(cfg, symbols[1]):
        in_grid = (c.swings.method == "pct" and c.swings.secondary_min_sessions == 15
                   and c.swings.minor_pct == cfg.swings.minor_pct and variant == "primary"
                   and c.trend == cfg.trend and c.swings.per_symbol_secondary_pct
                   == cfg.swings.per_symbol_secondary_pct)
        if not sweeps and not in_grid:
            continue
        o2 = build_objects(frame, c, symbols)
        for r in FAMILY if sweeps else SWEEP_RULES_WITHOUT_GRID:
            out = RULES[r](frame, o2, c, protocol, pair=pair, spec=spec_name(c))
            run.sweep_rows[r].append(_tagged(out.primary, variant, "sweep"))
            if in_grid and r in proto.WORST_GRID_RULES:
                run.grids[r][c.swings.secondary_pct] = out.label_input
    if sweeps:
        for variant, c in line_configs(cfg):
            out = RULES["R6"](frame, objs, c, protocol, pair=pair, spec=spec)
            run.sweep_rows["R6"].append(_tagged(out.primary, variant, "line sweep"))
    for r in FAMILY:
        for sub, est in (("sub_A", outcomes[r].label_input.sub_A),
                         ("sub_B", outcomes[r].label_input.sub_B)):
            base = outcomes[r].primary
            row = copy.copy(base)
            row.variant, row.label = sub, "n/a"
            row.metric_value, row.n_obs = est.estimate, est.n
            row.ci_low = row.ci_high = row.p_value = float("nan")
            row.notes = f"sub-sample split {run.split}"
            row.extras = {}
            outcomes[r].rows.append(row)
    run.flags = _flags(outcomes)
    if pair == LABEL_PAIR:
        _apply_labels(run, canonical or {})
    return run


def _apply_labels(run: PairRun, canonical: dict[str, dict[str, str]]) -> None:
    prim = {r: run.outcomes[r].label_input for r in FAMILY}
    run.labels = label_all(prim, run.grids, canonical)
    for r in FAMILY:
        lab = run.labels[r]
        row = run.outcomes[r].primary
        row.label = lab["label"]
        row.notes += (f"; p_holm={lab['p_holm']:.6f}; refute_bound={lab['bound']:.6f} "
                      f"vs null {row.null_value:.6f}")
        if r in proto.WORST_GRID_RULES:
            row.notes += f"; p_label_worst_grid={lab['p_label']:.6f}; bound_worst={lab['bound']:.6f}"


def _flags(outcomes: dict[str, RuleOutcome]) -> dict[str, list[str]]:
    """Status-table flags from the simulated nulls (protocol R1 and R8)."""
    flags: dict[str, list[str]] = {r: [] for r in FAMILY}
    for r, key, text in (("R1", "p_sim", "not-distinguishable-from-random-walk-with-drift"),
                         ("R8", "p_spell", "not-distinguishable-from-random-timing")):
        val = outcomes[r].details.get(key)
        if val is not None and val >= 0.05:
            flags[r].append(text)
    return flags


# --------------------------------------------------------------------------- pair-level glue
def load_pair_frame(
    pair: str, cfg: DowConfig, protocol: Protocol, *, source: str = "clickhouse",
    csv: str | None = None, csv_pair: str | None = None, client: ClickHouseClient | None = None,
) -> tuple[tuple[str, str], pd.DataFrame]:
    """Load both legs up to the protocol's fixed ``period_end`` and inner-join them."""
    syms = load_pairs().get(pair)
    if syms is None:
        raise ValueError(f"unknown pair {pair!r}; known: {sorted(load_pairs())}")
    end = protocol.period_end.isoformat()
    a = load_klines(syms[0], None, end, source=source, csv_path=csv, client=client)  # type: ignore[arg-type]
    b = load_klines(syms[1], None, end, source=source, csv_path=csv_pair or csv, client=client)  # type: ignore[arg-type]
    return (syms[0], syms[1]), make_pair_frame(a, b)


def latest_integrity_report(root: Path) -> str:
    """Repo-relative path of the newest ``reports/integrity_*.txt`` (empty string if none)."""
    found = sorted((root / "reports").glob("integrity_*.txt"))
    return found[-1].relative_to(root).as_posix() if found else ""


def run_backtest(
    pairs: list[str], *, cfg: DowConfig | None = None, source: str = "clickhouse",
    csv: str | None = None, csv_pair: str | None = None, sweeps: bool = True, workers: int = 1,
    deviations: list[str] | None = None, root: Path | None = None,
    client: ClickHouseClient | None = None, verify_config: bool = True,
) -> BacktestRun:
    """Run the harness for the requested pairs; labels exist for ``DJ`` only."""
    t0 = time.time()
    root = root or project_root()
    cfg = cfg or load_config()
    protocol = proto.load_protocol(cfg, root)
    pinned = proto.committed_config_hash(protocol.history)
    if verify_config and LABEL_PAIR in pairs and pinned and cfg.config_hash() != pinned:
        raise ValueError(
            f"config hash {cfg.config_hash()} differs from the committed value {pinned} pinned "
            "in the decision table; a label-driving row would be invalid"
        )
    canon_path = root / "research" / "canonical_rules.md"
    canonical = (
        resolve_literature(load_canonical_rules(canon_path)) if canon_path.exists() else {}
    )
    runs: dict[str, PairRun] = {}
    for pair in pairs:
        symbols, frame = load_pair_frame(pair, cfg, protocol, source=source, csv=csv,
                                         csv_pair=csv_pair, client=client)
        logger.info("pair %s: %d bars %s..%s", pair, len(frame), frame.index[0].date(),
                    frame.index[-1].date())
        runs[pair] = run_pair(pair, symbols, frame, cfg, protocol, sweeps=sweeps,
                              heavy=True, workers=workers, canonical=canonical)
    literature = {
        r: canonical.get(proto.RULE_KEY[r], {}).get("literature_label", "unresolved")
        for r in FAMILY
    }
    lit_ids = {r: canonical.get(proto.RULE_KEY[r], {}).get("ids", "") for r in FAMILY}
    return BacktestRun(
        uuid.uuid4().hex, dt.datetime.now(dt.UTC), time.time() - t0, cfg.config_hash(),
        protocol.table_hash, protocol.table_hash_scoped, latest_integrity_report(root),
        deviations or [], protocol.n_iter, runs, literature, lit_ids, sweeps,
    )


def base_notes(run: BacktestRun) -> str:
    parts = [f"integrity={run.integrity_path or 'none'}"]
    if run.deviations:
        parts.append("deviations=" + ",".join(run.deviations))
    parts.append(f"table_scoped={run.table_hash_scoped[:12]}")
    return "; ".join(parts)


def persist_run(run: BacktestRun, client: ClickHouseClient) -> int:
    """Insert every row of every pair into ``dow.str_rule_backtest_log``."""
    frames = [
        ledger_frame([(r, run.literature[r.rule_id], "") for r in pr.all_rows()],
                     run.run_id, run.table_hash, base_notes(run))
        for pr in run.pairs.values()
    ]  # all conversions happen before the first insert
    return insert_ledger(client, pd.concat(frames, ignore_index=True))


__all__ = ["BacktestRun", "PairRun", "persist_run", "run_backtest", "run_pair", "sweep_configs"]
