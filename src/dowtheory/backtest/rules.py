"""Rules R1..R8 of the pre-registered decision table.

Each ``R<n>(pair_df, objs, cfg, protocol, *, pair, ...)`` returns a :class:`RuleOutcome`: the
label-driving row (variant ``primary``), the inputs of ``decide_label`` and the descriptive
rows the table asks for. Descriptive rows never carry a label.
"""

from __future__ import annotations

import datetime as dt
import math
from collections.abc import Callable
from typing import Any

import numpy as np
import pandas as pd

from dowtheory.backtest import stats
from dowtheory.backtest.events import (
    PairObjects,
    breakout_groups,
    calls_from_states,
    detect_pair_lines,
    leg_events,
    leg_pair_events,
    pair_reversal_groups,
    pair_states,
    position_series,
    r1_events,
    reversal_events,
    split_date,
    trailing_median_volume,
)
from dowtheory.backtest.labels import PrimaryResult, SubSample
from dowtheory.backtest.nulls import simulate_p_extend, spell_null_delta_sharpe
from dowtheory.backtest.protocol import (
    BAND_HI,
    BAND_LO,
    COST_PRIMARY,
    HALF,
    PRIMARY_HORIZON,
    TRADING_DAYS,
    Protocol,
)
from dowtheory.backtest.results import (
    NAN,
    Ctx,
    RuleOutcome,
    RuleResult,
    event_returns,
    excess_row,
    hit_row,
    proportion,
    sign_string,
)
from dowtheory.config import DowConfig
from dowtheory.confirmation import volume_confirms


def make_ctx(
    rule_id: str, pair: str, objs: PairObjects, cfg: DowConfig, protocol: Protocol,
    *, spec: str, start: dt.date | None = None,
) -> Ctx:
    """Context with the pair's sub-sample split (median of the sample period)."""
    first, last = objs.date_at(0), objs.date_at(objs.last)
    return Ctx(rule_id, pair, objs, cfg, protocol, spec, split_date(first, last),
               cfg.config_hash(), start or first, last)


def _horizon_label(h: int) -> str:
    return f"h{h}"


# =========================================================================== R1
def R1(
    pair_df: pd.DataFrame, objs: PairObjects, cfg: DowConfig, protocol: Protocol,
    *, pair: str = "DJ", spec: str = "", heavy: bool = False, workers: int = 1,
) -> RuleOutcome:
    """Trend persistence: share of counter-trend secondary swings followed by a new extreme."""
    ctx = make_ctx("R1", pair, objs, cfg, protocol, spec=spec)
    tol = cfg.trend.equal_extreme_tol
    events = r1_events(objs.a.secondary, objs.a.snapshots, objs.index, tol)
    done = [e for e in events if e.outcome is not None]
    cens = len(events) - len(done)
    obs = [(e.date, e.outcome == "extend") for e in done]
    n_equal = sum(e.outcome == "equal" for e in done)
    notes = f"censored={cens}; equal_not_extended={n_equal}"
    row, prim = proportion(ctx, "primary", "p_extend", obs, 0.5, notes=notes, censored=cens)
    details: dict[str, Any] = {"n_events": len(events), "censored": cens, "equal": n_equal}
    rows: list[RuleResult] = []
    for side in ("bull", "bear"):
        sub = [(e.date, e.outcome == "extend") for e in done if e.side == side]
        rows.append(proportion(ctx, side, "p_extend", sub, 0.5)[0])
    if heavy and obs:
        sims = simulate_p_extend(
            objs.a.close, objs.index, cfg, objs.a.symbol, seed=protocol.seed,
            n_sim=protocol.n_iter, block_len=protocol.block_len, workers=workers,
        )
        sims = sims[~np.isnan(sims)]
        p_sim = stats.one_sided_p(sims, row.metric_value) if sims.size else NAN
        details.update(p_sim=p_sim, sim_mean=float(sims.mean()) if sims.size else NAN,
                       n_sim=int(sims.size))
        flag = "" if p_sim < 0.05 else "; not-distinguishable-from-random-walk-with-drift"
        row.notes += f"; p_sim={p_sim:.4f}{flag}"
        rows.append(ctx.row("p_sim", "p_extend", row.metric_value, row.n_obs, NAN, NAN, 0.5,
                            p_sim, notes=f"drift-matched null mean={details['sim_mean']:.4f}"))
    return RuleOutcome(row, prim, rows, details)


# =========================================================================== R2
def R2(
    pair_df: pd.DataFrame, objs: PairObjects, cfg: DowConfig, protocol: Protocol,
    *, pair: str = "DJ", spec: str = "", heavy: bool = False, workers: int = 1,
) -> RuleOutcome:
    """Reversal signal: signed excess forward return after ``REVERSAL_*`` on ``^DJI``."""
    ctx = make_ctx("R2", pair, objs, cfg, protocol, spec=spec)
    h0 = PRIMARY_HORIZON["R2"]
    ev_a = reversal_events(objs.a, objs.index)
    row, prim = excess_row(ctx, "primary", objs.a, ev_a, h0)
    rows: list[RuleResult] = []
    for h in protocol.horizons:
        if h != h0:
            rows.append(excess_row(ctx, f"horizon{h}", objs.a, ev_a, h)[0])
    rows.append(hit_row(ctx, "primary", event_returns(objs.a.close, ev_a, h0), h0))
    for name, sgn in (("up", 1), ("down", -1)):
        rows.append(excess_row(ctx, name, objs.a, [e for e in ev_a if e.sign == sgn], h0)[0])
    ev_b = reversal_events(objs.b, objs.index)
    rows.append(excess_row(ctx, "djt_side", objs.b, ev_b, h0)[0])
    rows.append(_pooled_excess(ctx, objs, ev_a, ev_b, h0))
    details = {"n_reversals_a": len(ev_a), "n_reversals_b": len(ev_b),
               "dates_a": [str(e.date) for e in ev_a]}
    return RuleOutcome(row, prim, rows, details)


def _pooled_excess(ctx: Ctx, objs: PairObjects, ev_a: list, ev_b: list, h: int) -> RuleResult:
    """Pooled ``^DJI`` + ``^DJT`` mean excess; same-bar events form one cluster (no p-value)."""
    ra, rb = event_returns(objs.a.close, ev_a, h), event_returns(objs.b.close, ev_b, h)
    vals = np.concatenate([ra.values, rb.values])
    bars = np.concatenate([ra.bars, rb.bars])
    if vals.size == 0:
        return ctx.row("pooled", "mean_excess_logret", NAN, 0, NAN, NAN, 0.0, NAN,
                       horizon=_horizon_label(h))
    ids = stats.cluster_ids(bars, h)
    boot = stats.cluster_bootstrap_mean(vals, ids, ctx.n_iter, ctx.rng())
    lo, hi = stats.percentile_interval(boot)
    return ctx.row("pooled", "mean_excess_logret", float(vals.mean()), vals.size, lo, hi, 0.0,
                   NAN, horizon=_horizon_label(h), clusters=int(ids.max()) + 1,
                   notes="descriptive; no p-value", censored=ra.censored + rb.censored)


# =========================================================================== R3
def _diff_outcome(
    ctx: Ctx, variant: str, conf: list, single: list, close: np.ndarray, h: int, notes: str = ""
) -> tuple[RuleResult, PrimaryResult]:
    cr, sr = event_returns(close, conf, h), event_returns(close, single, h)
    nc, ns = cr.values.size, sr.values.size
    subs = []
    for s in ("A", "B"):
        cv = [v for d, v in zip(cr.dates, cr.values, strict=True) if ctx.side_of(d) == s]
        sv = [v for d, v in zip(sr.dates, sr.values, strict=True) if ctx.side_of(d) == s]
        both = bool(cv) and bool(sv)
        subs.append(SubSample(len(cv) + len(sv) if both else 0,
                              float(np.mean(cv) - np.mean(sv)) if both else NAN))
    cens = cr.censored + sr.censored
    if nc == 0 or ns == 0:
        row = ctx.row(variant, "diff_excess_logret", NAN, nc + ns, NAN, NAN, 0.0, NAN,
                      horizon=_horizon_label(h), notes=f"groups confirmed={nc} single={ns}; {notes}",
                      censored=cens)
        return row, PrimaryResult(ctx.rule_id, nc + ns, nc + ns, nc, ns, True, NAN, 0.0, NAN, NAN,
                                  subs[0], subs[1])
    rng = ctx.rng()
    obs, p = stats.permutation_pvalue(cr.values, sr.values, ctx.n_iter, rng)
    boot = stats.cluster_bootstrap_diff(
        cr.values, stats.cluster_ids(cr.bars, h), sr.values, stats.cluster_ids(sr.bars, h),
        ctx.n_iter, rng,
    )
    lo, hi = stats.percentile_interval(boot)
    n_clusters = int(stats.cluster_ids(np.concatenate([cr.bars, sr.bars]), h).max()) + 1
    row = ctx.row(variant, "diff_excess_logret", obs, nc + ns, lo, hi, 0.0, p,
                  horizon=_horizon_label(h), signs=sign_string(subs, 0.0, ctx.protocol.min_group),
                  notes=f"groups confirmed={nc} single={ns}; {notes}".strip("; "),
                  clusters=n_clusters, censored=cens,
                  extras={"mean_confirmed": float(cr.values.mean()),
                          "mean_single": float(sr.values.mean())})
    prim = PrimaryResult(ctx.rule_id, nc + ns, nc + ns, nc, ns, True, obs, 0.0, p,
                         stats.upper_percentile(boot, ctx.level), subs[0], subs[1])
    return row, prim


def R3(
    pair_df: pd.DataFrame, objs: PairObjects, cfg: DowConfig, protocol: Protocol,
    *, pair: str = "DJ", spec: str = "", heavy: bool = False, workers: int = 1,
) -> RuleOutcome:
    """Two-index confirmation: confirmed minus single reversal excess return."""
    ctx = make_ctx("R3", pair, objs, cfg, protocol, spec=spec)
    h0 = PRIMARY_HORIZON["R3"]
    max_days = cfg.confirmation.max_days
    conf, single = pair_reversal_groups(objs, h0, max_days)
    row, prim = _diff_outcome(ctx, "primary", conf, single, objs.a.close, h0)
    rows: list[RuleResult] = []
    for h in protocol.horizons:
        if h != h0:
            c, s = pair_reversal_groups(objs, h, max_days)
            rows.append(_diff_outcome(ctx, f"horizon{h}", c, s, objs.a.close, h)[0])
    c90, s90 = pair_reversal_groups(objs, h0, 90)
    rows.append(_diff_outcome(ctx, "max_days90", c90, s90, objs.a.close, h0)[0])
    cr, sr = event_returns(objs.a.close, conf, h0), event_returns(objs.a.close, single, h0)
    hc, hs = (cr.signs * cr.raw > 0).astype(float), (sr.signs * sr.raw > 0).astype(float)
    if hc.size and hs.size:
        obs, p = stats.permutation_pvalue(hc, hs, ctx.n_iter, ctx.rng())
        rows.append(ctx.row("hit_rate_diff", "hit_rate_diff", obs, hc.size + hs.size, NAN, NAN,
                            0.0, p, horizon=_horizon_label(h0)))
    both_in_one = sum(
        1 for s in single if any(c.sign == s.sign and 0 < c.bar - s.bar for c in conf)
    )
    details = {"n_confirmed": len(conf), "n_single": len(single),
               "single_confirmed_later": both_in_one}
    return RuleOutcome(row, prim, rows, details)


# =========================================================================== R4 / R5
def _leg_sets(objs: PairObjects) -> tuple[list, list]:
    legs = leg_events(objs.a, objs.index)
    return [lg for lg in legs if lg.counter], legs


def R4(
    pair_df: pd.DataFrame, objs: PairObjects, cfg: DowConfig, protocol: Protocol,
    *, pair: str = "DJ", spec: str = "", heavy: bool = False, workers: int = 1,
) -> RuleOutcome:
    """Secondary retracement: share of counter-trend reactions retracing 1/3 to 2/3."""
    ctx = make_ctx("R4", pair, objs, cfg, protocol, spec=spec)
    counter, legs = _leg_sets(objs)
    row, prim = proportion(ctx, "primary", "share_band", [(x.date, x.in_band) for x in counter],
                           1 / 3)
    rows = [
        proportion(ctx, "share_sf", "share_third_half", [(x.date, x.in_half) for x in counter],
                   1 / 6)[0],
        proportion(ctx, "share_gt1", "share_rr_gt_1", [(x.date, x.rr > 1) for x in counter],
                   0.0)[0],
        proportion(ctx, "share_lt_third", "share_rr_lt_third",
                   [(x.date, float(x.rr) < BAND_LO) for x in counter], 0.0)[0],
        proportion(ctx, "majority", "share_band", [(x.date, x.in_band) for x in counter], 0.5)[0],
        proportion(ctx, "all_legs", "share_band", [(x.date, x.in_band) for x in legs], 1 / 3)[0],
        proportion(ctx, "all_legs_sf", "share_third_half", [(x.date, x.in_half) for x in legs],
                   1 / 6)[0],
    ]
    rr = [x.rr for x in counter]
    med, lo, hi = stats.median_interval(rr, ctx.rng(), protocol.n_iter)
    rows.append(ctx.row("median_rr", "median_rr", med, len(rr), lo, hi, NAN, NAN))
    details = {"deciles": stats.decile_counts(rr), "n_counter": len(counter), "n_legs": len(legs),
               "band": (BAND_LO, BAND_HI), "half": HALF}
    return RuleOutcome(row, prim, rows, details)


def R5(
    pair_df: pd.DataFrame, objs: PairObjects, cfg: DowConfig, protocol: Protocol,
    *, pair: str = "DJ", spec: str = "", heavy: bool = False, workers: int = 1,
) -> RuleOutcome:
    """Secondary duration: share of counter-trend reactions lasting 21 to 90 calendar days."""
    ctx = make_ctx("R5", pair, objs, cfg, protocol, spec=spec)
    counter, _legs = _leg_sets(objs)
    sw = cfg.swings
    row, prim = proportion(ctx, "primary", "share_rhea", [(x.date, x.rhea) for x in counter], 0.5)
    rows = [
        proportion(ctx, "schannep", "share_schannep", [(x.date, x.schannep) for x in counter],
                   0.5)[0],
        proportion(ctx, "gt_max", "share_gt_max_days",
                   [(x.date, x.d_cal > sw.secondary_max_days) for x in counter], 0.0)[0],
        proportion(ctx, "lt_min", "share_lt_min_days",
                   [(x.date, x.d_cal < sw.secondary_min_days) for x in counter], 0.0)[0],
    ]
    d = stats.describe([x.d_cal for x in counter])
    d_bar = stats.describe([x.d_bar for x in counter])
    rows.append(ctx.row("median_d_cal", "median_days", d["median"], d["n"], d["q1"], d["q3"],
                        NAN, NAN, notes="ci columns hold the inter-quartile range"))
    return RuleOutcome(row, prim, rows, {"d_cal": d, "d_bar": d_bar, "n_counter": len(counter)})


# =========================================================================== R6
def R6(
    pair_df: pd.DataFrame, objs: PairObjects, cfg: DowConfig, protocol: Protocol,
    *, pair: str = "DJ", spec: str = "", heavy: bool = False, workers: int = 1,
) -> RuleOutcome:
    """Line breakout: share of confirmed-both breakouts followed by a move in their direction.

    Line parameters come from ``cfg.line`` (an infinite ``max_drift_frac`` disables the drift
    rule, which is how the sweep expresses "none").
    """
    ctx = make_ctx("R6", pair, objs, cfg, protocol, spec=spec)
    lines = detect_pair_lines(objs, cfg.line.band_pct, cfg.line.min_sessions,
                              cfg.line.max_drift_frac)
    h0 = PRIMARY_HORIZON["R6"]
    groups = breakout_groups(lines, objs, h0)
    er = event_returns(objs.a.close, groups.confirmed, h0)
    obs = [(d, bool(s * r > 0)) for d, s, r in zip(er.dates, er.signs, er.raw, strict=True)]
    clusters = int(stats.cluster_ids(er.bars, h0).max()) + 1 if er.bars.size else 0
    notes = (f"lines={groups.n_lines}; breakouts={groups.n_breakouts}; "
             f"mean_line_days={groups.mean_line_len:.1f}; censored={er.censored}")
    row, prim = proportion(ctx, "primary", "agree", obs, 0.5, horizon=_horizon_label(h0),
                           notes=notes, censored=er.censored, clusters=clusters)
    rows: list[RuleResult] = []
    for h in protocol.horizons:
        if h == h0:
            continue
        g = breakout_groups(lines, objs, h)
        e = event_returns(objs.a.close, g.confirmed, h)
        rows.append(proportion(ctx, f"horizon{h}", "agree",
                               [(d, bool(s * r > 0)) for d, s, r in
                                zip(e.dates, e.signs, e.raw, strict=True)],
                               0.5, horizon=_horizon_label(h), censored=e.censored)[0])
    sr = event_returns(objs.a.close, groups.single, h0)
    s_obs = [(d, bool(s * r > 0)) for d, s, r in zip(sr.dates, sr.signs, sr.raw, strict=True)]
    rows.append(proportion(ctx, "single", "agree", s_obs, 0.5, horizon=_horizon_label(h0),
                           censored=sr.censored)[0])
    hc = np.array([ok for _, ok in obs], dtype=float)
    hs = np.array([ok for _, ok in s_obs], dtype=float)
    if hc.size and hs.size:
        diff, p = stats.permutation_pvalue(hc, hs, ctx.n_iter, ctx.rng())
        rows.append(ctx.row("conf_minus_single", "agree_diff", diff, hc.size + hs.size, NAN, NAN,
                            0.0, p, horizon=_horizon_label(h0),
                            notes=f"groups confirmed={hc.size} single={hs.size}"))
    rows.append(excess_row(ctx, "excess", objs.a, groups.confirmed, h0,
                           rule_metric="mean_excess_logret",
                           eligible=(0, len(objs.a.close) - 2 - h0))[0])
    return RuleOutcome(row, prim, rows, {"lines": groups.n_lines, "breakouts": groups.n_breakouts,
                                         "confirmed": len(groups.confirmed),
                                         "single": len(groups.single)})


# =========================================================================== R7
def R7(
    pair_df: pd.DataFrame, objs: PairObjects, cfg: DowConfig, protocol: Protocol,
    *, pair: str = "DJ", spec: str = "", heavy: bool = False, workers: int = 1,
) -> RuleOutcome:
    """Volume confirmation: with-trend legs carry more average volume than counter legs."""
    first = max(objs.date_at(0), protocol.r7_start)
    ctx = make_ctx("R7", pair, objs, cfg, protocol, spec=spec, start=first)
    start_bar = int(objs.index.searchsorted(pd.Timestamp(protocol.r7_start)))
    pairs = leg_pair_events(objs.a, objs.index, start_bar)
    row, prim = proportion(ctx, "primary", "p_vol",
                           [(x.date, x.with_vol > x.counter_vol) for x in pairs], 0.5)
    norm = trailing_median_volume(objs.a.volume)
    pairs_n = leg_pair_events(objs.a, objs.index, start_bar, norm)
    rows = [proportion(ctx, "normalised", "p_vol",
                       [(x.date, x.with_vol > x.counter_vol) for x in pairs_n], 0.5)[0]]
    df = pd.DataFrame({"volume": objs.a.volume})
    sec = objs.a.secondary
    windows = [(sec[k + 3].confirmed_idx, volume_confirms(df, sec[k : k + 4]))
               for k in range(len(sec) - 3) if sec[k].idx >= start_bar]
    flags = [(objs.date_at(c), f) for c, f in windows if f is not None]
    rows.append(proportion(ctx, "volume_confirms", "share_true", flags, 0.5)[0])
    return RuleOutcome(row, prim, rows, {"n_pairs": len(pairs), "n_pairs_normalised": len(pairs_n),
                                         "volume_confirms_windows": len(flags)})


# =========================================================================== R8
def strategy_series(
    close: np.ndarray, pos: np.ndarray, kappa: float
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """``(strategy r_s, buy-and-hold r, executed position e, previous position)`` for ``t >= 3``.

    ``r_s(t) = pos[t-2] * r(t) - kappa * |pos[t-2] - pos[t-3]|`` (protocol execution rule).
    """
    r = np.diff(np.log(close))[2:]
    e, prev = pos[1:-2], pos[:-3]
    return e * r - kappa * np.abs(e - prev), r, e, prev


def _max_drawdown(r: np.ndarray) -> float:
    equity = np.exp(np.cumsum(r))
    return float(np.min(equity / np.maximum.accumulate(equity) - 1.0)) if r.size else NAN


def _sharpe_row(
    ctx: Ctx, variant: str, close: np.ndarray, pos: np.ndarray, kappa: float, dates: pd.DatetimeIndex,
    *, notes: str = "", p_extra: bool = True,
) -> tuple[RuleResult, PrimaryResult, dict[str, Any]]:
    rs, rb, e, prev = strategy_series(close, pos, kappa)
    trades = int(np.sum(e != prev))
    obs = stats.sharpe(rs) - stats.sharpe(rb)
    subs = []
    mask_a = np.array([ctx.side_of(d.date()) == "A" for d in dates])
    for m in (mask_a, ~mask_a):
        n_tr = int(np.sum((e != prev)[m]))
        subs.append(SubSample(n_tr, float(stats.sharpe(rs[m]) - stats.sharpe(rb[m]))
                              if m.sum() > 2 else NAN))
    if rs.size < 3 or math.isnan(obs):
        row = ctx.row(variant, "delta_sharpe", NAN, trades, NAN, NAN, 0.0, NAN, notes=notes)
        return row, PrimaryResult(ctx.rule_id, trades, trades, 0, 0, False, NAN, 0.0, NAN, NAN,
                                  subs[0], subs[1]), {}
    rng = ctx.rng()
    d_sharpe, d_cum = stats.block_bootstrap_paired(
        rs, rb, ctx.protocol.block_len, ctx.n_iter, rng, TRADING_DAYS
    )
    p = stats.one_sided_p(d_sharpe, 0.0, "less")
    lo, hi = stats.percentile_interval(d_sharpe)
    cum = float(rs.sum() - rb.sum())
    cl, ch = stats.percentile_interval(d_cum)
    ann = lambda x: float(x.mean() * TRADING_DAYS)
    vol = lambda x: float(x.std(ddof=1) * math.sqrt(TRADING_DAYS))
    detail = {
        "trades": trades, "time_in_market": float(np.mean(e != 0)), "bars": int(rs.size),
        "sharpe_strategy": float(stats.sharpe(rs)), "sharpe_bh": float(stats.sharpe(rb)),
        "ann_ret_strategy": ann(rs), "ann_ret_bh": ann(rb),
        "ann_vol_strategy": vol(rs), "ann_vol_bh": vol(rb),
        "mdd_strategy": _max_drawdown(rs), "mdd_bh": _max_drawdown(rb),
        "cum_diff": cum, "cum_diff_ci": (cl, ch), "p_cum": stats.one_sided_p(d_cum, 0.0, "less"),
    }
    row = ctx.row(variant, "delta_sharpe", obs, trades, lo, hi, 0.0, p,
                  signs=sign_string(subs, 0.0, ctx.protocol.min_group),
                  notes=f"trades={trades}; {notes}".strip("; "), extras=detail)
    prim = PrimaryResult(ctx.rule_id, trades, trades, 0, 0, False, obs, 0.0, p,
                         stats.upper_percentile(d_sharpe, ctx.level), subs[0], subs[1])
    return row, prim, detail


def R8(
    pair_df: pd.DataFrame, objs: PairObjects, cfg: DowConfig, protocol: Protocol,
    *, pair: str = "DJ", spec: str = "", heavy: bool = False, workers: int = 1,
) -> RuleOutcome:
    """Hamilton-style timing: pair-confirmed long/cash strategy against buy-and-hold."""
    ctx = make_ctx("R8", pair, objs, cfg, protocol, spec=spec)
    close = objs.a.close
    if len(close) < 5:
        empty = SubSample(0, NAN)
        row = ctx.row("primary", "delta_sharpe", NAN, 0, NAN, NAN, 0.0, NAN, notes="too few bars")
        return RuleOutcome(row, PrimaryResult("R8", 0, 0, 0, 0, False, NAN, 0.0, NAN, NAN,
                                              empty, empty), [], {})
    states = pair_states(objs)
    pos = position_series(states, objs, allow_short=False)
    dates = objs.index[3:]
    row, prim, detail = _sharpe_row(ctx, "primary", close, pos, COST_PRIMARY, dates)
    rows = [_sharpe_row(ctx, "cost0", close, pos, 0.0, dates)[0]]
    short = position_series(states, objs, allow_short=True)
    rows.append(_sharpe_row(ctx, "short", close, short, COST_PRIMARY, dates)[0])
    details: dict[str, Any] = {"primary": detail, "caveat_price_index": True}
    _rs, rb, e, _prev = strategy_series(close, pos, COST_PRIMARY)
    if heavy and detail:
        spell = spell_null_delta_sharpe(rb, e, COST_PRIMARY, protocol.n_iter, ctx.rng())
        p_spell = stats.one_sided_p(spell, row.metric_value, "greater")
        flag = "" if p_spell < 0.05 else "; not-distinguishable-from-random-timing"
        row.notes += f"; p_spell={p_spell:.4f}{flag}"
        details["p_spell"] = p_spell
        rows.append(ctx.row("p_spell", "delta_sharpe", row.metric_value, row.n_obs, NAN, NAN, 0.0,
                            p_spell, notes="random-spell null"))
    calls = _call_rows(ctx, objs, states, close)
    rows.extend(calls[0])
    details["calls"] = calls[1]
    return RuleOutcome(row, prim, rows, details)


def _call_rows(
    ctx: Ctx, objs: PairObjects, states: list[str | None], close: np.ndarray
) -> tuple[list[RuleResult], dict[str, Any]]:
    """Right/wrong calls (BGK analogue): descriptive, two-sided binomial p against 0.5."""
    calls = calls_from_states(states, objs.index)
    last = len(close) - 1
    right = wrong = 0
    for i, c in enumerate(calls):
        if c.bar + 1 > last:
            continue
        end = min(calls[i + 1].bar + 1, last) if i + 1 < len(calls) else last
        ret = math.log(close[end] / close[c.bar + 1])
        if c.sign * ret > 0:
            right += 1
        else:
            wrong += 1
    n = right + wrong
    lo, hi = stats.wilson_interval(right, n)
    p = stats.binomial_pvalue(right, n, 0.5, "two-sided")
    row = ctx.row("calls", "share_right", right / n if n else NAN, n, lo, hi, 0.5, p,
                  direction="two-sided", notes=f"right={right}; wrong={wrong}; descriptive")
    return [row], {"right": right, "wrong": wrong, "n_calls": len(calls)}


RULES: dict[str, Callable[..., RuleOutcome]] = {
    "R1": R1, "R2": R2, "R3": R3, "R4": R4, "R5": R5, "R6": R6, "R7": R7, "R8": R8,
}
