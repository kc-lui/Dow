"""Label algorithm of the pre-registered decision table (section 3), plus literature lookup.

``decide_label`` and ``label_all`` follow the protocol pseudocode; the only additions are
type annotations and a defensive ``nan -> 1.0`` for p-values of undefined metrics.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from dowtheory.backtest.protocol import (
    FAMILY,
    GRID_SECONDARY_PCT,
    MIN_N_GROUP,
    RULE_KEY,
    WORST_GRID_RULES,
)
from dowtheory.backtest.stats import holm_adjust

ALPHA = 0.05
MIN_N = 30
CONFIRMED, REFUTED, INSUFFICIENT = "data-confirmed", "data-refuted", "insufficient-evidence"

__all__ = [
    "ALPHA",
    "MIN_N",
    "RULE_ENTRIES",
    "PrimaryResult",
    "SubSample",
    "decide_label",
    "holm_adjust",
    "label_all",
    "label_inputs",
    "load_canonical_rules",
    "n_ok",
    "resolve_literature",
    "sign_consistent",
]


@dataclass(frozen=True)
class SubSample:
    """Sample size and point estimate inside one sub-sample."""

    n: int
    estimate: float


@dataclass(frozen=True)
class PrimaryResult:
    """The fields ``decide_label`` reads from the DJ / primary-spec / primary row of a rule."""

    rule: str
    n: int
    n_total: int
    n_group_a: int
    n_group_b: int
    two_sample: bool
    estimate: float
    null_value: float
    p_raw: float
    bound_bonf: float
    sub_A: SubSample
    sub_B: SubSample


# --------------------------------------------------------------------------- literature
_LIT = (
    ("consensus", "literature-consensus"),
    ("disputed", "literature-disputed"),
    ("agent-defined", "agent-defined"),
    ("single-source", "single-source"),
)


def _normalise_label(raw: str) -> str:
    low = raw.strip().strip("*`").lower()
    return next((full for key, full in _LIT if low.startswith((key, full))), "unresolved")


def load_canonical_rules(path: str | Path) -> dict[str, dict[str, str]]:
    """Parse the registry tables of ``research/canonical_rules.md``: ``rule_key -> {...}``.

    Each table's header row names its columns; only tables with ``rule_key`` and ``label``
    columns are read. The label is normalised to ``literature-consensus`` /
    ``literature-disputed`` / ``agent-defined`` / ``single-source``.
    """
    text = Path(path).read_text(encoding="utf-8")
    out: dict[str, dict[str, str]] = {}
    header: list[str] | None = None
    for line in text.splitlines():
        if not line.startswith("|"):
            header = None
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if "rule_key" in cells and "label" in cells:
            header = cells
            continue
        if header is None or set(line.replace("|", "").strip()) <= {"-", " ", ":"}:
            continue
        if len(cells) < len(header):
            continue
        row = dict(zip(header, cells, strict=False))
        key = row["rule_key"].strip("`")
        out[key] = {"literature_label": _normalise_label(row["label"]), "id": row.get("id", "")}
    return out


# Protocol rule_key -> registry ids (the registry keys are finer than the protocol's).
RULE_ENTRIES: dict[str, tuple[str, ...]] = {
    "trend_persistence": ("R-016", "R-017"),
    "primary_reversal_signal": ("R-018", "R-020"),
    "two_average_confirmation": ("R-032", "R-033", "R-034"),
    "secondary_retracement": ("R-008", "R-009", "R-010", "R-011"),
    "secondary_duration": ("R-006", "R-007"),
    "line_breakout": ("R-022", "R-023", "R-024", "R-025", "R-026", "R-027"),
    "volume_confirmation": ("R-037", "R-038", "R-041"),
    "hamilton_timing": ("R-062",),
}


def resolve_literature(canonical: dict[str, dict[str, str]]) -> dict[str, dict[str, str]]:
    """Protocol ``rule_key`` -> ``{literature_label, ids}`` from the mapped registry rows.

    ``literature-disputed`` if any mapped row is disputed, else ``literature-consensus`` if all
    are consensus, else ``single-source``. A key whose mapped ids are missing from the
    registry is ``unresolved``.
    """
    by_id = {v["id"]: v["literature_label"] for v in canonical.values() if v.get("id")}
    out: dict[str, dict[str, str]] = {}
    for key, ids in RULE_ENTRIES.items():
        labels = [by_id[i] for i in ids if i in by_id]
        if len(labels) != len(ids):
            lit = "unresolved"
        elif "literature-disputed" in labels:
            lit = "literature-disputed"
        elif all(x == "literature-consensus" for x in labels):
            lit = "literature-consensus"
        else:
            lit = "single-source"
        out[key] = {"literature_label": lit, "ids": ",".join(ids)}
    return out


# --------------------------------------------------------------------------- protocol section 3
def sign_consistent(result: PrimaryResult, side: str) -> bool | None:
    """``side`` is ``"predicted"`` or ``"wrong"``; ``None`` when a sub-sample has ``n < 10``."""
    subs = [result.sub_A, result.sub_B]
    if any(s.n < MIN_N_GROUP for s in subs):
        return None
    d = [s.estimate - result.null_value for s in subs]
    if side == "predicted":
        return all(x > 0 for x in d)
    return all(x < 0 for x in d)


def n_ok(result: PrimaryResult) -> bool:
    if result.two_sample:
        return result.n_total >= MIN_N and min(result.n_group_a, result.n_group_b) >= MIN_N_GROUP
    return result.n >= MIN_N


def label_inputs(
    rule: str, primary: PrimaryResult, grid: dict[float, PrimaryResult]
) -> tuple[float, float]:
    """``(p_raw for the family, bound for refutation)``; worst grid point for R4 and R5."""
    if rule not in WORST_GRID_RULES:
        return primary.p_raw, primary.bound_bonf
    pts = [grid[g] for g in GRID_SECONDARY_PCT if g in grid and n_ok(grid[g])]
    if not pts:
        return 1.0, primary.null_value  # cannot confirm, cannot refute
    return max(r.p_raw for r in pts), max(r.bound_bonf for r in pts)


def decide_label(
    rule: str,
    result: PrimaryResult,
    p_holm: dict[str, float],
    bound: float,
    canonical_rules: dict[str, dict[str, str]],
) -> dict[str, Any]:
    lit = canonical_rules.get(RULE_KEY[rule], {}).get("literature_label", "unresolved")

    if not n_ok(result):
        return {"label": INSUFFICIENT, "literature_label": lit, "reason": "n below minimum"}

    if p_holm[rule] < ALPHA and sign_consistent(result, "predicted") is True:
        return {
            "label": CONFIRMED,
            "literature_label": lit,
            "reason": "p_holm<alpha, sub-samples agree",
        }

    wrong_side = (bound - result.null_value) < 0  # effect bound on the wrong side of the null
    if wrong_side and sign_consistent(result, "wrong") is True:
        return {
            "label": REFUTED,
            "literature_label": lit,
            "reason": "Bonferroni bound excludes null, sub-samples agree",
        }

    reason = (
        "sub-sample consistency not assessable"
        if sign_consistent(result, "predicted") is None
        else "not significant after Holm, or sub-samples disagree"
    )
    return {"label": INSUFFICIENT, "literature_label": lit, "reason": reason}


def _clean_p(p: float | None) -> float:
    return 1.0 if p is None or math.isnan(p) else p


def label_all(
    primary_results: dict[str, PrimaryResult],
    grids: dict[str, dict[float, PrimaryResult]],
    canonical_rules: dict[str, dict[str, str]],
) -> dict[str, dict[str, Any]]:
    """Labels for the whole family; adds ``p_holm``, ``p_label`` and ``bound`` to each entry."""
    inputs = {r: label_inputs(r, primary_results[r], grids.get(r, {})) for r in FAMILY}
    p_raw = {r: (_clean_p(inputs[r][0]) if n_ok(primary_results[r]) else 1.0) for r in FAMILY}
    p_holm = holm_adjust(p_raw)
    out = {}
    for r in FAMILY:
        d = decide_label(r, primary_results[r], p_holm, inputs[r][1], canonical_rules)
        d.update(p_holm=p_holm[r], p_label=p_raw[r], bound=inputs[r][1])
        out[r] = d
    return out
