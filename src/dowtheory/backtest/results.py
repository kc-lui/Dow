"""Result containers and the generic estimators shared by the rule functions."""

from __future__ import annotations

import datetime as dt
import math
from collections.abc import Sequence
from dataclasses import dataclass, field
from typing import Any

import numpy as np

from dowtheory.backtest import stats
from dowtheory.backtest.events import PairObjects, SideObjects, forward_returns, subsample_of
from dowtheory.backtest.labels import PrimaryResult, SubSample
from dowtheory.backtest.protocol import RULE_KEY, Protocol
from dowtheory.config import DowConfig

NAN = float("nan")


@dataclass
class RuleResult:
    """One row of the evidence ledger (``dow.str_rule_backtest_log``)."""

    rule_id: str
    rule_key: str
    pair: str
    spec: str
    variant: str
    metric_name: str
    metric_value: float
    n_obs: int
    ci_low: float
    ci_high: float
    null_value: float
    p_value: float
    direction: str
    subsample_signs: str
    horizon: str
    notes: str = ""
    label: str = "n/a"
    n_clusters: int | None = None
    n_censored: int = 0
    config_hash: str = ""
    period_start: dt.date | None = None
    period_end: dt.date | None = None
    extras: dict[str, Any] = field(default_factory=dict)

    @property
    def log_name(self) -> str:
        """``<spec>|<variant>|<metric>|<horizon>`` (protocol 1.7)."""
        return f"{self.spec}|{self.variant}|{self.metric_name}|{self.horizon}"


@dataclass
class RuleOutcome:
    """Primary row, the inputs of ``decide_label``, descriptive rows and printable details."""

    primary: RuleResult
    label_input: PrimaryResult
    rows: list[RuleResult] = field(default_factory=list)
    details: dict[str, Any] = field(default_factory=dict)


@dataclass
class Ctx:
    """Everything a rule needs besides its events."""

    rule_id: str
    pair: str
    objs: PairObjects
    cfg: DowConfig
    protocol: Protocol
    spec: str
    split: dt.date
    config_hash: str
    period_start: dt.date
    period_end: dt.date

    @property
    def level(self) -> float:
        return self.protocol.bonferroni_level

    @property
    def n_iter(self) -> int:
        return self.protocol.n_iter

    def rng(self) -> np.random.Generator:
        return stats.make_rng(self.protocol.seed)

    def row(
        self, variant: str, metric: str, value: float, n: int, lo: float, hi: float,
        null: float, p: float, *, horizon: str = "na", signs: str = "na", notes: str = "",
        clusters: int | None = None, censored: int = 0, direction: str = "greater",
        extras: dict[str, Any] | None = None,
    ) -> RuleResult:
        return RuleResult(
            self.rule_id, RULE_KEY[self.rule_id], self.pair, self.spec, variant, metric,
            value, n, lo, hi, null, p, direction, signs, horizon, notes, "n/a", clusters,
            censored, self.config_hash, self.period_start, self.period_end, extras or {},
        )

    # ------------------------------------------------------------------ sub-samples
    def side_of(self, date: dt.date) -> str:
        return subsample_of(date, self.split)


def sign_string(subs: Sequence[SubSample], null: float, min_group: int) -> str:
    """``A+ B-`` style summary of ``sign(estimate - null)`` per sub-sample (``na`` if n small)."""
    out = []
    for name, s in zip("AB", subs, strict=True):
        if s.n < min_group or math.isnan(s.estimate):
            out.append(f"{name}?")
        else:
            d = s.estimate - null
            out.append(f"{name}{'+' if d > 0 else '-' if d < 0 else '0'}")
    return " ".join(out)


# --------------------------------------------------------------------------- proportions
def proportion(
    ctx: Ctx, variant: str, metric: str, outcomes: Sequence[tuple[dt.date, bool]], null: float,
    *, horizon: str = "na", notes: str = "", censored: int = 0, clusters: int | None = None,
    alternative: stats.Alternative = "greater",
) -> tuple[RuleResult, PrimaryResult]:
    """Binomial / Wilson estimate of a proportion of independent events."""
    n = len(outcomes)
    k = sum(1 for _, ok in outcomes if ok)
    est = k / n if n else NAN
    p = stats.binomial_pvalue(k, n, null, alternative)
    lo, hi = stats.wilson_interval(k, n)
    bound = stats.wilson_bound(k, n, ctx.level, "upper") if n else NAN
    subs = []
    for side in ("A", "B"):
        sel = [ok for d, ok in outcomes if ctx.side_of(d) == side]
        subs.append(SubSample(len(sel), sum(sel) / len(sel) if sel else NAN))
    signs = sign_string(subs, null, ctx.protocol.min_group)
    row = ctx.row(variant, metric, est, n, lo, hi, null, p, horizon=horizon, signs=signs,
                  notes=notes, clusters=clusters, censored=censored)
    prim = PrimaryResult(ctx.rule_id, n, n, 0, 0, False, est, null, p, bound, subs[0], subs[1])
    return row, prim


# --------------------------------------------------------------------------- excess returns
@dataclass(frozen=True)
class EventReturns:
    """Signed excess forward returns of the uncensored events of one average."""

    bars: np.ndarray
    signs: np.ndarray
    raw: np.ndarray        # F_h(c)
    values: np.ndarray     # sign * (F_h(c) - benchmark)
    dates: list[dt.date]
    censored: int
    bench: float


def event_returns(
    close: np.ndarray, events: Sequence[Any], h: int
) -> EventReturns:
    """Forward returns of ``events`` (objects with ``bar``, ``date``, ``sign``)."""
    f = forward_returns(close, h)
    f_ok = f[~np.isnan(f)]
    bench = float(f_ok.mean()) if f_ok.size else NAN
    keep = [e for e in events if not np.isnan(f[e.bar])]
    bars = np.array([e.bar for e in keep], dtype=int)
    signs = np.array([e.sign for e in keep], dtype=float)
    raw = f[bars] if keep else np.empty(0)
    return EventReturns(
        bars, signs, raw, signs * (raw - bench), [e.date for e in keep],
        len(events) - len(keep), bench,
    )


def eligible_range(side: SideObjects, h: int) -> tuple[int, int] | None:
    """Contiguous bars with a defined trend state and a defined ``F_h`` (random-placement pool)."""
    first = next((i for i, s in enumerate(side.snapshots) if s.state != "UNDEFINED"), None)
    last = len(side.close) - 2 - h
    return None if first is None or first > last else (first, last)


def excess_row(
    ctx: Ctx, variant: str, side: SideObjects, events: Sequence[Any], h: int, *,
    rule_metric: str = "mean_excess_logret", placement: bool = True, notes: str = "",
    eligible: tuple[int, int] | None = None,
) -> tuple[RuleResult, PrimaryResult]:
    """Mean signed excess return with cluster-bootstrap CI and random-placement p."""
    er = event_returns(side.close, events, h)
    n = er.values.size
    rng = ctx.rng()
    if n == 0:
        row = ctx.row(variant, rule_metric, NAN, 0, NAN, NAN, 0.0, NAN, horizon=f"h{h}",
                      notes=notes, censored=er.censored)
        empty = SubSample(0, NAN)
        return row, PrimaryResult(ctx.rule_id, 0, 0, 0, 0, False, NAN, 0.0, NAN, NAN, empty, empty)
    obs = float(er.values.mean())
    ids = stats.cluster_ids(er.bars, h)
    boot = stats.cluster_bootstrap_mean(er.values, ids, ctx.n_iter, rng)
    lo, hi = stats.percentile_interval(boot)
    bound = stats.upper_percentile(boot, ctx.level)
    p = NAN
    rng_p = range_ = None
    if placement:
        range_ = eligible or eligible_range(side, h)
        if range_ is not None:
            g = forward_returns(side.close, h) - er.bench
            rng_p = stats.random_placement_null(
                g, range_[0], range_[1], n, er.signs, stats.min_spacing(er.bars), ctx.n_iter, rng
            )
            p = stats.one_sided_p(rng_p, obs)
    subs = []
    for s in ("A", "B"):
        sel = [v for d, v in zip(er.dates, er.values, strict=True) if ctx.side_of(d) == s]
        subs.append(SubSample(len(sel), float(np.mean(sel)) if sel else NAN))
    signs = sign_string(subs, 0.0, ctx.protocol.min_group)
    n_clusters = int(ids.max()) + 1
    row = ctx.row(variant, rule_metric, obs, n, lo, hi, 0.0, p, horizon=f"h{h}", signs=signs,
                  notes=notes, clusters=n_clusters, censored=er.censored,
                  extras={"bench": er.bench, "hit_rate": float(np.mean(er.signs * er.raw > 0))})
    prim = PrimaryResult(ctx.rule_id, n, n, 0, 0, False, obs, 0.0, p, bound, subs[0], subs[1])
    return row, prim


def hit_row(
    ctx: Ctx, variant: str, er: EventReturns, h: int, metric: str = "hit_rate"
) -> RuleResult:
    """Share of events whose signed forward return is positive (Wilson CI, binomial p vs 0.5)."""
    n = er.raw.size
    k = int(np.sum(er.signs * er.raw > 0))
    lo, hi = stats.wilson_interval(k, n)
    return ctx.row(variant, metric, k / n if n else NAN, n, lo, hi, 0.5,
                   stats.binomial_pvalue(k, n, 0.5, "greater"), horizon=f"h{h}",
                   censored=er.censored)
