import datetime as dt

import numpy as np
import pandas as pd
import pytest

from dowtheory.backtest import events as ev
from dowtheory.backtest.protocol import BAND_HI, BAND_LO
from dowtheory.config import load_config

N = 1800


def synthetic_frame(n: int = N, shift: int = 4) -> pd.DataFrame:
    """Two noisy cyclical series with trending phases (deterministic)."""
    t = np.arange(n)

    def make(phase: int, seed: int) -> np.ndarray:
        noise = np.random.default_rng(seed).normal(0, 0.004, n)
        x = 0.35 * np.sin(2 * np.pi * (t - phase) / 520) + 0.12 * np.sin(2 * np.pi * (t - phase) / 85)
        return 100 * np.exp(x + 0.0002 * t + np.cumsum(noise) * 0.3)

    idx = pd.bdate_range("2000-01-03", periods=n)
    a, b = make(0, 1), make(shift, 2)
    return pd.DataFrame({
        "open": a, "high": a, "low": a, "close": a, "volume": 1_000_000.0 + 50.0 * t,
        "open_b": b, "high_b": b, "low_b": b, "close_b": b, "volume_b": 900_000.0 + 40.0 * t,
    }, index=idx).rename(columns=lambda c: c if c.endswith("_b") else f"{c}_a")


@pytest.fixture(scope="module")
def frame() -> pd.DataFrame:
    return synthetic_frame()


@pytest.fixture(scope="module")
def objs(frame):
    return ev.build_objects(frame, load_config(), ("^DJI", "^DJT"))


# --------------------------------------------------------------------------- returns
def test_forward_return_indexing_off_by_one():
    close = np.array([100.0, 110.0, 121.0, 133.1, 146.41, 161.051])  # +10% per bar
    f = ev.forward_returns(close, 2)
    # F_2(c) = ln(P[c+3] / P[c+1]) = 2 * ln(1.1), defined while c + 1 + 2 <= 5, i.e. c <= 2
    assert f[0] == pytest.approx(2 * np.log(1.1))
    assert f[2] == pytest.approx(2 * np.log(1.1))
    assert np.isnan(f[3]) and np.isnan(f[5])
    assert int(np.sum(~np.isnan(f))) == 3


def test_forward_return_starts_after_event_bar():
    close = np.array([100.0, 50.0, 60.0, 90.0])  # the c -> c+1 move must not count
    assert ev.forward_returns(close, 1)[0] == pytest.approx(np.log(60 / 50))
    assert ev.forward_returns(close, 1)[1] == pytest.approx(np.log(90 / 60))


def test_forward_return_ignores_prices_before_event_bar():
    base = np.array([100.0, 101.0, 102.0, 103.0, 104.0, 105.0])
    changed = base.copy()
    changed[:2] = [1.0, 500.0]
    assert ev.forward_returns(base, 2)[2] == ev.forward_returns(changed, 2)[2]


def test_benchmark_mean_uses_only_defined_windows():
    close = np.exp(np.arange(10) * 0.01)
    assert ev.benchmark_mean(close, 3) == pytest.approx(0.03)
    assert np.isnan(ev.benchmark_mean(close[:3], 5))


def test_split_date_matches_protocol_examples():
    assert ev.split_date(dt.date(1992, 1, 2), dt.date(2026, 11, 6)) == dt.date(2009, 12, 31)
    assert ev.split_date(dt.date(2004, 10, 1), dt.date(2026, 11, 6)) == dt.date(2015, 12, 31)
    assert ev.subsample_of(dt.date(2009, 12, 31), dt.date(2009, 12, 31)) == "A"
    assert ev.subsample_of(dt.date(2010, 1, 4), dt.date(2009, 12, 31)) == "B"


def test_spec_names():
    cfg = load_config()
    assert ev.spec_name(cfg) == "pct0.03/0.08f15"
    assert ev.spec_name(ev.with_swings(cfg, method="atr")) == "atr2.0/14f15"
    assert ev.spec_name(ev.with_swings(cfg, method="pivot")) == "pivot5"
    assert ev.spec_name(ev.with_swings(cfg, secondary_pct=0.1, secondary_min_sessions=0)) == (
        "pct0.03/0.1f0"
    )


# --------------------------------------------------------------------------- event sets
def test_synthetic_series_produces_events(objs):
    assert len(objs.a.secondary) >= 6
    assert ev.reversal_events(objs.a, objs.index), "synthetic cycles must reverse the trend"
    assert ev.r1_events(objs.a.secondary, objs.a.snapshots, objs.index, 0.005)


def test_event_bars_are_confirmation_bars(objs):
    for e in ev.r1_events(objs.a.secondary, objs.a.snapshots, objs.index, 0.005):
        assert any(s.confirmed_idx == e.bar for s in objs.a.secondary)
    for e in ev.reversal_events(objs.a, objs.index):
        assert any(s.idx == e.bar and s.kind.startswith("REVERSAL") for s in objs.a.signals)
    for g in ev.leg_events(objs.a, objs.index):
        assert any(s.confirmed_idx == g.bar for s in objs.a.secondary)


@pytest.mark.parametrize("cut", [700, 900, 1200, 1500])
def test_no_lookahead_event_sets_invariant_under_truncation(frame, objs, cut):
    cfg = load_config()
    part = frame.iloc[: cut + 1]
    po = ev.build_objects(part, cfg, ("^DJI", "^DJT"))
    tol = cfg.trend.equal_extreme_tol

    def keyset(o, upto):
        r1 = {(e.bar, e.side) for e in ev.r1_events(o.a.secondary, o.a.snapshots, o.index, tol)
              if e.bar <= upto}
        rev = {(e.bar, e.sign) for e in ev.reversal_events(o.a, o.index) if e.bar <= upto}
        legs = {(g.bar, g.counter, g.in_band, g.rhea) for g in ev.leg_events(o.a, o.index)
                if g.bar <= upto}
        pairs = {(p.bar) for p in ev.leg_pair_events(o.a, o.index, 0) if p.bar <= upto}
        states = ev.pair_states(o)[: upto + 1]
        return r1, rev, legs, pairs, states

    assert keyset(po, cut) == keyset(objs, cut)


def test_leg_flags_match_band_definition(objs):
    legs = ev.leg_events(objs.a, objs.index)
    assert legs
    for g in legs:
        assert g.in_band == (BAND_LO <= float(g.rr) <= BAND_HI)
        assert g.in_half == (BAND_LO <= float(g.rr) <= 0.5)


def test_counter_legs_run_against_trend(objs):
    sec = {s.confirmed_idx: s for s in objs.a.secondary}
    for g in ev.leg_events(objs.a, objs.index):
        if g.counter:
            st = objs.a.snapshots[g.bar].state
            kind = sec[g.bar].kind
            assert (st.startswith("BULL") and kind == "L") or (st.startswith("BEAR") and kind == "H")


def test_r1_outcome_uses_next_swing_only(objs):
    tol = 0.005
    sec = objs.a.secondary
    for e in ev.r1_events(sec, objs.a.snapshots, objs.index, tol):
        k = next(i for i, s in enumerate(sec) if s.confirmed_idx == e.bar and (
            (s.kind == "L") == (e.side == "bull")))
        if k + 1 == len(sec):
            assert e.outcome is None
        else:
            assert e.outcome in {"extend", "equal", "fail"}


def test_pair_groups_event_bars(objs):
    conf, single = ev.pair_reversal_groups(objs, 60, None)
    rev_bars = {e.bar for e in ev.reversal_events(objs.a, objs.index)}
    assert all(s.bar in rev_bars for s in single)
    for c in conf:
        assert c.bar >= min(rev_bars) and c.bar <= objs.last
    # a reversal matched within the horizon cannot be single
    conf0, single0 = ev.pair_reversal_groups(objs, 10_000, None)
    assert not single0 and len(conf0) >= len(conf) - len(single)


def test_pair_confirmed_state_requires_identical_primary_states(objs):
    states = ev.pair_states(objs)
    for t, s in enumerate(states):
        if s is not None:
            assert objs.a.snapshots[t].state == s == objs.b.snapshots[t].state


def test_positions_and_calls(objs):
    states = ev.pair_states(objs)
    long_only = ev.position_series(states, objs, allow_short=False)
    both = ev.position_series(states, objs, allow_short=True)
    assert set(np.unique(long_only)) <= {0.0, 1.0}
    assert set(np.unique(both)) <= {-1.0, 0.0, 1.0}
    assert np.array_equal(np.maximum(both, 0), long_only)
    calls = ev.calls_from_states(states, objs.index)
    assert calls and all(c.sign in (-1, 1) for c in calls)
    assert [c.bar for c in calls] == sorted(c.bar for c in calls)


def test_leg_pairs_need_positive_volume(objs):
    pairs = ev.leg_pair_events(objs.a, objs.index, 0)
    assert pairs and all(p.with_vol > 0 and p.counter_vol > 0 for p in pairs)
    zero = np.zeros_like(objs.a.volume)
    assert ev.leg_pair_events(objs.a, objs.index, 0, zero) == []
    assert len(ev.leg_pair_events(objs.a, objs.index, objs.last)) == 0


def test_trailing_median_volume_removes_growth():
    vol = np.linspace(100.0, 1000.0, 600)
    norm = ev.trailing_median_volume(vol, 250)
    assert np.isnan(norm[:249]).all()
    assert norm[-1] < 1.5
