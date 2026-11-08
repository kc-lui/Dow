"""Trend state machine: scripted sequences, mirror cases, replay and no-lookahead."""

from __future__ import annotations

import datetime as dt
from dataclasses import replace
from decimal import Decimal
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from dowtheory.config import DowConfig
from dowtheory.data.loader import load_klines
from dowtheory.swings import Swing, detect_multiscale, detect_swings, swings_as_of
from dowtheory.trend import (
    BEAR_PRIMARY,
    BEAR_SUSPECT,
    BULL_PRIMARY,
    BULL_SUSPECT,
    UNDEFINED,
    Signal,
    TrendStateMachine,
    run_trend,
)

FIXTURE = Path(__file__).resolve().parents[1] / "fixtures" / "dji_sample.csv"
BASE = dt.date(2021, 1, 1)


def day(idx: int) -> dt.date:
    return BASE + dt.timedelta(days=idx)


def sw(idx: int, kind: str, price: float, conf: int) -> Swing:
    return Swing(idx, day(idx), Decimal(str(price)), kind, conf, day(conf), "secondary",  # type: ignore[arg-type]
                 Decimal(0), 0, None)


def machine(strict: bool = True) -> TrendStateMachine:
    base = DowConfig()
    return TrendStateMachine(DowConfig(trend=replace(base.trend, require_lower_high_for_reversal=strict)))


def feed(m: TrendStateMachine, events: list[tuple[int, float, list[Swing]]]) -> list[Signal]:
    out: list[Signal] = []
    for idx, close, swings in events:
        out.extend(m.step(idx, day(idx), close, swings))
    return out


def kinds(signals: list[Signal]) -> list[str]:
    return [s.kind for s in signals]


# Bull establishment: L100, H120, L110 (HL), H130 (HH) -> defense = 110 at bar 33.
BULL_START = [
    (3, 105.0, [sw(0, "L", 100, 3)]),
    (13, 108.0, [sw(10, "H", 120, 13)]),
    (23, 125.0, [sw(20, "L", 110, 23)]),
    (33, 118.0, [sw(30, "H", 130, 33)]),
]
# Bear establishment: H130, L110, H120 (LH), L100 (LL) -> defense = 120 at bar 33.
BEAR_START = [
    (3, 125.0, [sw(0, "H", 130, 3)]),
    (13, 115.0, [sw(10, "L", 110, 13)]),
    (23, 105.0, [sw(20, "H", 120, 23)]),
    (33, 108.0, [sw(30, "L", 100, 33)]),
]


def test_starts_undefined() -> None:
    m = machine()
    assert m.state.state == UNDEFINED and m.state.since is None and m.state.defense_line is None
    assert m.state.secondary_direction == "flat"


def test_bull_established_by_hl_then_hh() -> None:
    m = machine()
    sig = feed(m, BULL_START)
    st = m.state
    assert st.state == BULL_PRIMARY and st.since == day(33)
    assert kinds(sig) == ["HL", "HH"]
    assert (st.defense_line, st.defense_line_ts, st.defense_line_kind) == (
        Decimal(110), day(20), "reaction_low")
    assert st.secondary_direction == "down" and st.last_H.price == 130 and st.prev_H.price == 120


def test_bull_established_by_hh_then_hl() -> None:
    m = machine()
    feed(m, [(3, 105.0, [sw(0, "H", 120, 3)]), (13, 108.0, [sw(10, "L", 100, 13)]),
             (23, 125.0, [sw(20, "H", 130, 23)]), (33, 118.0, [sw(30, "L", 110, 33)])])
    assert m.state.state == BULL_PRIMARY and m.state.since == day(33)
    assert m.state.defense_line == 110 and m.state.secondary_direction == "up"


def test_hh_alone_does_not_establish() -> None:
    m = machine()
    feed(m, [(3, 105.0, [sw(0, "H", 120, 3)]), (13, 108.0, [sw(10, "L", 100, 13)]),
             (23, 125.0, [sw(20, "H", 130, 23)])])
    assert m.state.state == UNDEFINED


def test_bear_established_by_lh_and_ll() -> None:
    m = machine()
    sig = feed(m, BEAR_START)
    st = m.state
    assert st.state == BEAR_PRIMARY and st.since == day(33)
    assert kinds(sig) == ["LH", "LL"]
    assert (st.defense_line, st.defense_line_ts, st.defense_line_kind) == (
        Decimal(120), day(20), "reaction_high")
    assert st.secondary_direction == "up"


def test_defense_line_updates_on_each_hl() -> None:
    m = machine()
    feed(m, BULL_START)
    assert m.state.defense_line == 110
    feed(m, [(43, 130.0, [sw(40, "L", 115, 43)])])
    assert m.state.defense_line == 115 and m.state.defense_line_ts == day(40)
    feed(m, [(53, 140.0, [sw(50, "H", 140, 53)]), (63, 140.0, [sw(60, "L", 120, 63)])])
    assert m.state.defense_line == 120 and m.state.state == BULL_PRIMARY
    assert m.state.since == day(33)


def test_lh_then_close_below_defense_is_reversal_down() -> None:
    m = machine()
    feed(m, BULL_START + [(43, 130.0, [sw(40, "L", 115, 43)])])
    sig = feed(m, [(53, 119.0, [sw(50, "H", 125, 53)])])
    assert kinds(sig) == ["LH"] and m.state.state == BULL_SUSPECT
    assert m.state.since == day(33)
    sig = feed(m, [(54, 114.0, [])])
    assert kinds(sig) == ["REVERSAL_DOWN"]
    assert sig[0].level == 115 and sig[0].price == 114 and not sig[0].agent_defined
    st = m.state
    assert st.state == BEAR_PRIMARY and st.since == day(54)
    assert (st.defense_line, st.defense_line_ts, st.defense_line_kind) == (
        Decimal(125), day(50), "reaction_high")


def test_lh_confirmed_below_defense_reverses_on_same_bar() -> None:
    m = machine()
    feed(m, BULL_START + [(43, 130.0, [sw(40, "L", 115, 43)])])
    sig = feed(m, [(53, 112.0, [sw(50, "H", 125, 53)])])
    assert kinds(sig) == ["LH", "REVERSAL_DOWN"] and m.state.state == BEAR_PRIMARY


def test_suspect_returns_to_primary_on_new_high() -> None:
    m = machine()
    feed(m, BULL_START + [(43, 130.0, [sw(40, "L", 115, 43)]), (53, 119.0, [sw(50, "H", 125, 53)])])
    assert m.state.state == BULL_SUSPECT
    sig = feed(m, [(63, 140.0, [sw(60, "H", 135, 63)])])
    assert kinds(sig) == ["HH"] and m.state.state == BULL_PRIMARY and m.state.since == day(33)
    # the counter-swing flag was reset: a plain close below defense is a DEFENSE_BREAK again
    assert kinds(feed(m, [(64, 100.0, [])])) == ["DEFENSE_BREAK"]


def test_defense_break_without_lh_strict_stays_suspect() -> None:
    m = machine(strict=True)
    feed(m, BULL_START)
    sig = feed(m, [(40, 109.0, [])])
    assert kinds(sig) == ["DEFENSE_BREAK"] and sig[0].agent_defined and sig[0].level == 110
    assert m.state.state == BULL_SUSPECT and m.state.since == day(33)
    assert feed(m, [(41, 90.0, [])]) == []  # no LH yet: no reversal
    sig = feed(m, [(53, 95.0, [sw(50, "H", 125, 53)])])  # LH confirmed while still below
    assert kinds(sig) == ["LH", "REVERSAL_DOWN"] and m.state.state == BEAR_PRIMARY


def test_defense_break_without_lh_non_strict_flips() -> None:
    m = machine(strict=False)
    feed(m, BULL_START)
    sig = feed(m, [(40, 109.0, [])])
    assert kinds(sig) == ["DEFENSE_BREAK"] and sig[0].agent_defined
    st = m.state
    assert st.state == BEAR_PRIMARY and st.since == day(40)
    assert (st.defense_line, st.defense_line_kind) == (Decimal(130), "reaction_high")


def test_hl_then_close_above_defense_is_reversal_up() -> None:
    m = machine()
    feed(m, BEAR_START + [(43, 100.0, [sw(40, "H", 115, 43)])])
    assert m.state.defense_line == 115
    sig = feed(m, [(53, 108.0, [sw(50, "L", 105, 53)])])
    assert kinds(sig) == ["HL"] and m.state.state == BEAR_SUSPECT
    sig = feed(m, [(54, 116.0, [])])
    assert kinds(sig) == ["REVERSAL_UP"] and sig[0].level == 115
    st = m.state
    assert st.state == BULL_PRIMARY and st.since == day(54)
    assert (st.defense_line, st.defense_line_kind, st.defense_line_ts) == (
        Decimal(105), "reaction_low", day(50))


def test_bear_defense_break_strict_and_non_strict() -> None:
    strict = machine(True)
    feed(strict, BEAR_START)
    sig = feed(strict, [(40, 121.0, [])])
    assert kinds(sig) == ["DEFENSE_BREAK"] and sig[0].agent_defined
    assert strict.state.state == BEAR_SUSPECT and strict.state.since == day(33)
    loose = machine(False)
    feed(loose, BEAR_START)
    feed(loose, [(40, 121.0, [])])
    st = loose.state
    assert st.state == BULL_PRIMARY and st.since == day(40)
    assert (st.defense_line, st.defense_line_kind) == (Decimal(100), "reaction_low")


def test_bear_suspect_returns_to_primary_on_new_low() -> None:
    m = machine()
    feed(m, BEAR_START + [(43, 100.0, [sw(40, "H", 115, 43)]), (53, 108.0, [sw(50, "L", 105, 53)])])
    assert m.state.state == BEAR_SUSPECT
    sig = feed(m, [(63, 90.0, [sw(60, "L", 95, 63)])])
    assert kinds(sig) == ["LL"] and m.state.state == BEAR_PRIMARY


def test_signals_use_confirmation_bar_and_carry_level() -> None:
    m = machine()
    sig = feed(m, BULL_START)
    hh = sig[-1]
    assert (hh.idx, hh.ts, hh.price, hh.level) == (33, day(33), Decimal(130), Decimal(120))
    assert not hh.agent_defined


# --------------------------------------------------------------------------- replay
def _walk_close(seed: int, n: int = 700) -> pd.Series:
    rng = np.random.default_rng(seed)
    idx = pd.bdate_range("2018-01-02", periods=n)
    return pd.Series(100 * np.exp(np.cumsum(rng.normal(0.0003, 0.012, n))), index=idx)


def _cfg(strict: bool = True) -> DowConfig:
    base = DowConfig()
    return DowConfig(
        swings=replace(base.swings, secondary_pct=0.06),
        trend=replace(base.trend, require_lower_high_for_reversal=strict),
    )


@pytest.mark.parametrize("strict", [True, False])
def test_run_trend_snapshots_align_and_final_matches(strict: bool) -> None:
    close = _walk_close(21)
    cfg = _cfg(strict)
    sec = detect_multiscale(close, cfg)["secondary"]
    final, signals, snaps = run_trend(close, sec, cfg)
    assert len(snaps) == len(close)
    assert snaps[-1] == final
    assert all(s.idx >= 0 for s in signals) and signals == sorted(signals, key=lambda s: s.idx)
    assert final.state != UNDEFINED
    assert {s.kind for s in signals} & {"HH", "HL", "LH", "LL"}


@pytest.mark.parametrize("strict", [True, False])
def test_run_trend_has_no_lookahead(strict: bool) -> None:
    close = _walk_close(22)
    cfg = _cfg(strict)
    sec = detect_multiscale(close, cfg)["secondary"]
    _final, signals, snaps = run_trend(close, sec, cfg)
    for t in range(40, len(close), 37):
        part_sec = detect_multiscale(close.iloc[: t + 1], cfg)["secondary"]
        assert swings_as_of(part_sec, t) == swings_as_of(sec, t)
        part_final, part_signals, _ = run_trend(close.iloc[: t + 1], part_sec, cfg)
        assert part_final == snaps[t]
        assert part_signals == [s for s in signals if s.idx <= t]


def test_run_trend_ignores_swings_not_yet_confirmed() -> None:
    close = _walk_close(23, n=300)
    swings = detect_swings(close, threshold=0.06, scale="secondary")
    _, _, snaps = run_trend(close, swings, _cfg())
    first = swings[0].confirmed_idx
    assert all(s.last_H is None and s.last_L is None for s in snaps[:first])


def test_since_only_changes_on_primary_direction_change() -> None:
    close = _walk_close(24)
    cfg = _cfg()
    _, signals, snaps = run_trend(close, detect_multiscale(close, cfg)["secondary"], cfg)
    flips = {s.idx for s in signals if s.kind in ("REVERSAL_UP", "REVERSAL_DOWN")}
    for i in range(1, len(snaps)):
        a, b = snaps[i - 1], snaps[i]
        if a.since != b.since and a.state != UNDEFINED:
            assert i in flips or b.state in (BULL_PRIMARY, BEAR_PRIMARY)
            assert b.since == close.index[i].date()


def test_dji_fixture_trend_smoke(capsys: pytest.CaptureFixture[str]) -> None:
    df = load_klines("^DJI", source="csv", csv_path=FIXTURE)
    cfg = DowConfig()
    res = detect_multiscale(df["close"], cfg, high=df["high"], low=df["low"])
    final, signals, snaps = run_trend(df["close"], res["secondary"], cfg)
    counts = {k: sum(s.kind == k for s in signals) for k in sorted({s.kind for s in signals})}
    print(f"minor={len(res['minor'])} secondary={len(res['secondary'])} state={final.state} "
          f"since={final.since} defense={final.defense_line} signals={counts}")
    assert len(snaps) == len(df) and final.state in {
        UNDEFINED, BULL_PRIMARY, BEAR_PRIMARY, BULL_SUSPECT, BEAR_SUSPECT}
