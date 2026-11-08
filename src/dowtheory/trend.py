"""Dow trend state machine driven by confirmed secondary swings and closes.

The defense line is agent-defined (no literature source). The machine only sees swings whose
``confirmed_idx`` equals the current bar, so it cannot look ahead.
"""

from __future__ import annotations

import datetime as dt
from collections import defaultdict
from collections.abc import Sequence
from dataclasses import dataclass, replace
from decimal import Decimal
from typing import Literal

import pandas as pd

from dowtheory.config import DowConfig
from dowtheory.swings import Swing, to_price

UNDEFINED = "UNDEFINED"
BULL_PRIMARY = "BULL_PRIMARY"
BEAR_PRIMARY = "BEAR_PRIMARY"
BULL_SUSPECT = "BULL_SUSPECT"
BEAR_SUSPECT = "BEAR_SUSPECT"

SignalKind = Literal[
    "REVERSAL_UP",
    "REVERSAL_DOWN",
    "DEFENSE_BREAK",
    "HH",
    "HL",
    "LH",
    "LL",
    "LINE_BREAKOUT_UP",
    "LINE_BREAKOUT_DOWN",
]
DefenseKind = Literal["reaction_low", "reaction_high"]


@dataclass
class TrendState:
    """Current primary-trend assessment. ``since`` marks the start of the current direction."""

    state: str = UNDEFINED
    since: dt.date | None = None
    last_H: Swing | None = None
    prev_H: Swing | None = None
    last_L: Swing | None = None
    prev_L: Swing | None = None
    defense_line: Decimal | None = None
    defense_line_ts: dt.date | None = None
    defense_line_kind: DefenseKind | None = None
    secondary_direction: Literal["up", "down", "flat"] = "flat"


@dataclass(frozen=True)
class Signal:
    """A dated observation; ``agent_defined`` marks signals with no literature source."""

    idx: int
    ts: dt.date
    kind: SignalKind
    price: Decimal
    level: Decimal | None
    note: str
    agent_defined: bool = False


@dataclass(frozen=True)
class _Bar:
    idx: int
    ts: dt.date
    close: Decimal


def _label(sw: Swing, prev: Swing | None) -> str | None:
    """HH/LH for highs, HL/LL for lows, relative to the previous same-kind swing."""
    if prev is None or sw.price == prev.price:
        return None
    up = sw.price > prev.price
    if sw.kind == "H":
        return "HH" if up else "LH"
    return "HL" if up else "LL"


class TrendStateMachine:
    """Replay-friendly Dow trend state machine (see the algorithm contract)."""

    def __init__(self, cfg: DowConfig) -> None:
        self._strict = cfg.trend.require_lower_high_for_reversal
        self.state = TrendState()
        self._counter_swing = False  # LH seen in a bull (HL in a bear) since the last HH (LL)

    # ------------------------------------------------------------------ public
    def step(
        self,
        idx: int,
        ts: dt.date,
        close: float | Decimal,
        newly_confirmed_swings: Sequence[Swing],
    ) -> list[Signal]:
        """Advance one bar: process swings confirmed on it, then test the close."""
        bar = _Bar(idx, ts, to_price(close))
        signals: list[Signal] = []
        for sw in sorted(newly_confirmed_swings, key=lambda s: s.idx):
            signals.extend(self._on_swing(sw, bar))
        signals.extend(self._on_close(bar))
        return signals

    # ------------------------------------------------------------------ swings
    def _record(self, sw: Swing) -> tuple[str | None, Swing | None]:
        st = self.state
        if sw.kind == "H":
            prev = st.last_H
            st.prev_H, st.last_H = prev, sw
        else:
            prev = st.last_L
            st.prev_L, st.last_L = prev, sw
        st.secondary_direction = "down" if sw.kind == "H" else "up"
        return _label(sw, prev), prev

    def _on_swing(self, sw: Swing, bar: _Bar) -> list[Signal]:
        label, prev = self._record(sw)
        signals: list[Signal] = []
        if label is not None and prev is not None:
            note = f"{label}: swing {sw.ts} vs {prev.ts}, confirmed {bar.ts}"
            signals.append(
                Signal(bar.idx, bar.ts, label, sw.price, prev.price, note, False)  # type: ignore[arg-type]
            )
        self._react(sw, label, bar)
        return signals

    def _react(self, sw: Swing, label: str | None, bar: _Bar) -> None:
        state = self.state.state
        if state == UNDEFINED:
            self._try_establish(bar)
        elif state in (BULL_PRIMARY, BULL_SUSPECT):
            if label == "HH":
                self._set(BULL_PRIMARY, counter=False)
            elif label == "LH":
                self._set(BULL_SUSPECT, counter=True)
            elif label == "HL":
                self._set_defense(sw, "reaction_low")
        else:
            if label == "LL":
                self._set(BEAR_PRIMARY, counter=False)
            elif label == "HL":
                self._set(BEAR_SUSPECT, counter=True)
            elif label == "LH":
                self._set_defense(sw, "reaction_high")

    def _try_establish(self, bar: _Bar) -> None:
        st = self.state
        if None in (st.last_H, st.prev_H, st.last_L, st.prev_L):
            return
        assert st.last_H and st.prev_H and st.last_L and st.prev_L  # narrow for type checkers
        if st.last_H.price > st.prev_H.price and st.last_L.price > st.prev_L.price:
            self._enter(BULL_PRIMARY, bar, st.last_L, "reaction_low")
        elif st.last_H.price < st.prev_H.price and st.last_L.price < st.prev_L.price:
            self._enter(BEAR_PRIMARY, bar, st.last_H, "reaction_high")

    # ------------------------------------------------------------------ closes
    def _on_close(self, bar: _Bar) -> list[Signal]:
        st = self.state
        level = st.defense_line
        if level is None:
            return []
        if st.state == BULL_PRIMARY and bar.close < level:
            return [self._defense_break(bar, level, flip=not self._strict)]
        if st.state == BULL_SUSPECT and self._counter_swing and bar.close < level:
            return [self._reverse(bar, level, to_bear=True)]
        if st.state == BEAR_PRIMARY and bar.close > level:
            return [self._defense_break(bar, level, flip=not self._strict)]
        if st.state == BEAR_SUSPECT and self._counter_swing and bar.close > level:
            return [self._reverse(bar, level, to_bear=False)]
        return []

    def _defense_break(self, bar: _Bar, level: Decimal, *, flip: bool) -> Signal:
        bull_side = self.state.state == BULL_PRIMARY
        action = "flips to the opposite primary trend" if flip else "now suspect"
        note = (
            f"close {bar.close} {'<' if bull_side else '>'} defense line {level} "
            f"(agent-defined) without a counter swing; {action}"
        )
        signal = Signal(bar.idx, bar.ts, "DEFENSE_BREAK", bar.close, level, note, True)
        if flip:
            self._flip(bar, bull_side)
        else:
            self._set(BULL_SUSPECT if bull_side else BEAR_SUSPECT, counter=False)
        return signal

    def _reverse(self, bar: _Bar, level: Decimal, *, to_bear: bool) -> Signal:
        kind: SignalKind = "REVERSAL_DOWN" if to_bear else "REVERSAL_UP"
        note = f"close {bar.close} crossed defense line {level} after a counter swing"
        signal = Signal(bar.idx, bar.ts, kind, bar.close, level, note, False)
        self._flip(bar, to_bear)
        return signal

    def _flip(self, bar: _Bar, to_bear: bool) -> None:
        st = self.state
        if to_bear:
            assert st.last_H is not None
            self._enter(BEAR_PRIMARY, bar, st.last_H, "reaction_high")
        else:
            assert st.last_L is not None
            self._enter(BULL_PRIMARY, bar, st.last_L, "reaction_low")

    # ------------------------------------------------------------------ mutation helpers
    def _enter(self, state: str, bar: _Bar, anchor: Swing, kind: DefenseKind) -> None:
        self.state.since = bar.ts
        self._set(state, counter=False)
        self._set_defense(anchor, kind)

    def _set(self, state: str, *, counter: bool) -> None:
        self.state.state = state
        self._counter_swing = counter

    def _set_defense(self, anchor: Swing, kind: DefenseKind) -> None:
        st = self.state
        st.defense_line, st.defense_line_ts, st.defense_line_kind = anchor.price, anchor.ts, kind


def run_trend(
    close: pd.Series, secondary_swings: Sequence[Swing], cfg: DowConfig
) -> tuple[TrendState, list[Signal], list[TrendState]]:
    """Replay ``close`` bar by bar, feeding each swing only on its ``confirmed_idx`` bar.

    Returns the final state, all signals, and one state snapshot per bar (aligned to ``close``).
    """
    machine = TrendStateMachine(cfg)
    by_bar: dict[int, list[Swing]] = defaultdict(list)
    for sw in secondary_swings:
        by_bar[sw.confirmed_idx].append(sw)
    signals: list[Signal] = []
    snapshots: list[TrendState] = []
    for i, (ts, px) in enumerate(close.items()):
        signals.extend(machine.step(i, pd.Timestamp(ts).date(), float(px), by_bar.get(i, [])))
        snapshots.append(replace(machine.state))
    return replace(machine.state), signals, snapshots
