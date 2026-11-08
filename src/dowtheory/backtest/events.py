"""Event sets of the pre-registered protocol, built from the P3 objects.

Every event carries the bar at which it became knowable (``Swing.confirmed_idx``,
``Signal.idx``, ``LineRange.confirmed_ts``); forward returns start one bar later:
``F_h(c) = ln(P[c+1+h] / P[c+1])``. Nothing here looks past the event bar except the
classification windows the protocol itself defines (R3 and R6 "single" groups), and those
never change an event bar.
"""

from __future__ import annotations

import dataclasses
import datetime as dt
from dataclasses import dataclass
from decimal import Decimal

import numpy as np
import pandas as pd

from dowtheory.config import DowConfig
from dowtheory.confirmation import confirm_signal, pair_confirm
from dowtheory.line import LineRange, detect_lines
from dowtheory.swings import Swing, detect_multiscale
from dowtheory.trend import (
    BEAR_PRIMARY,
    BEAR_SUSPECT,
    BULL_PRIMARY,
    BULL_SUSPECT,
    Signal,
    TrendState,
    _label,  # the machine's own HH/LL/EQUAL classification (single source of truth)
    run_trend,
)

PRIMARY_STATES = (BULL_PRIMARY, BEAR_PRIMARY)
TREND_STATES = (BULL_PRIMARY, BEAR_PRIMARY, BULL_SUSPECT, BEAR_SUSPECT)
REVERSALS = ("REVERSAL_UP", "REVERSAL_DOWN")


# --------------------------------------------------------------------------- frames, specs
def make_pair_frame(df_a: pd.DataFrame, df_b: pd.DataFrame) -> pd.DataFrame:
    """Inner-join two OHLCV frames on date; columns get the suffixes ``_a`` and ``_b``."""
    out = df_a.add_suffix("_a").join(df_b.add_suffix("_b"), how="inner")
    if out.empty:
        raise ValueError("no common sessions between the two legs")
    return out


def spec_name(cfg: DowConfig) -> str:
    """Specification label used in ``metric_name`` (``pct0.03/0.08f15``, ``atr2.0/14f15``, ``pivot5``)."""
    sw = cfg.swings
    if sw.method == "pct":
        return f"pct{sw.minor_pct:g}/{sw.secondary_pct:g}f{sw.secondary_min_sessions}"
    if sw.method == "atr":
        return f"atr{sw.atr_mult:.1f}/{sw.atr_window}f{sw.secondary_min_sessions}"
    return f"pivot{sw.pivot_n}"


def with_swings(cfg: DowConfig, **changes: object) -> DowConfig:
    return dataclasses.replace(cfg, swings=dataclasses.replace(cfg.swings, **changes))


def with_trend(cfg: DowConfig, **changes: object) -> DowConfig:
    return dataclasses.replace(cfg, trend=dataclasses.replace(cfg.trend, **changes))


# --------------------------------------------------------------------------- objects
@dataclass(frozen=True)
class SideObjects:
    """Everything the rules need about one average."""

    symbol: str
    close: np.ndarray
    volume: np.ndarray
    secondary: list[Swing]
    signals: list[Signal]
    snapshots: list[TrendState]


@dataclass(frozen=True)
class PairObjects:
    index: pd.DatetimeIndex
    a: SideObjects
    b: SideObjects
    cfg: DowConfig

    @property
    def last(self) -> int:
        return len(self.index) - 1

    def date_at(self, bar: int) -> dt.date:
        return self.index[bar].date()

    def bar_of(self, date: dt.date) -> int:
        return int(self.index.get_loc(pd.Timestamp(date)))


def build_side(frame: pd.DataFrame, which: str, symbol: str, cfg: DowConfig) -> SideObjects:
    close = frame[f"close_{which}"]
    scales = detect_multiscale(
        close, cfg, frame.get(f"high_{which}"), frame.get(f"low_{which}"), symbol=symbol
    )
    secondary = scales["secondary"]
    _final, signals, snaps = run_trend(close, secondary, cfg)
    vol = frame[f"volume_{which}"].to_numpy(dtype=float) if f"volume_{which}" in frame else (
        np.zeros(len(frame))
    )
    return SideObjects(symbol, close.to_numpy(dtype=float), vol, secondary, signals, snaps)


def build_objects(frame: pd.DataFrame, cfg: DowConfig, symbols: tuple[str, str]) -> PairObjects:
    """Swings, trend replay and signals for both averages under ``cfg``."""
    a = build_side(frame, "a", symbols[0], cfg)
    b = build_side(frame, "b", symbols[1], cfg)
    return PairObjects(pd.DatetimeIndex(frame.index), a, b, cfg)


# --------------------------------------------------------------------------- returns
def forward_returns(close: np.ndarray, h: int) -> np.ndarray:
    """``F_h(t) = ln(P[t+1+h] / P[t+1])``; ``nan`` where ``t + 1 + h > last`` (censored)."""
    n = len(close)
    out = np.full(n, np.nan)
    m = n - 1 - h
    if m > 0:
        out[:m] = np.log(close[1 + h : 1 + h + m] / close[1 : 1 + m])
    return out


def benchmark_mean(close: np.ndarray, h: int) -> float:
    """Mean of ``F_h(t)`` over every bar with ``t + 1 + h <= last``."""
    f = forward_returns(close, h)
    f = f[~np.isnan(f)]
    return float(f.mean()) if f.size else float("nan")


# --------------------------------------------------------------------------- sub-samples
def split_date(first: dt.date, last: dt.date) -> dt.date:
    """Sub-sample boundary: 31 December of the year holding the median calendar date.

    The protocol says "rounded to the preceding 31 December" but gives 2009-12-31 for
    1992-01-02..2026-11-06 and 2015-12-31 for 2004..2026. Only "31 December of the median
    date's year" reproduces both stated dates, so that is what is implemented (DEV proposal
    in ``analysis/protocol_deviations.md``).
    """
    median = first + (last - first) / 2
    return dt.date(median.year, 12, 31)


def subsample_of(date: dt.date, split: dt.date) -> str:
    """``"A"`` when ``date <= split`` else ``"B"``."""
    return "A" if date <= split else "B"


# --------------------------------------------------------------------------- R1
@dataclass(frozen=True)
class SwingEvent:
    bar: int
    date: dt.date
    side: str
    outcome: str | None  # "extend" | "equal" | "fail" | None (right-censored)


def r1_events(
    secondary: list[Swing], snapshots: list[TrendState], index: pd.DatetimeIndex, tol: float
) -> list[SwingEvent]:
    """Counter-trend confirmed secondary swings in an established trend and their outcome.

    The outcome compares ``S_{k+1}`` with the trend extreme held in ``state(c)`` using the
    state machine's own EQUAL tolerance; EQUAL counts as not extended.
    """
    out: list[SwingEvent] = []
    for k, s in enumerate(secondary):
        c = s.confirmed_idx
        st = snapshots[c]
        if s.kind == "L" and st.state == BULL_PRIMARY:
            side, ref, want = "bull", st.last_H, "HH"
        elif s.kind == "H" and st.state == BEAR_PRIMARY:
            side, ref, want = "bear", st.last_L, "LL"
        else:
            continue
        outcome: str | None = None
        if k + 1 < len(secondary):
            nxt = secondary[k + 1]
            expected = "H" if side == "bull" else "L"
            if nxt.kind != expected or ref is None:
                raise ValueError(f"secondary swings do not alternate around bar {c}")
            lab = _label(nxt, ref, tol)
            outcome = "extend" if lab == want else "equal" if lab == "EQ" else "fail"
        out.append(SwingEvent(c, index[c].date(), side, outcome))
    return out


# --------------------------------------------------------------------------- R2 / R3
@dataclass(frozen=True)
class SignalEvent:
    bar: int
    date: dt.date
    sign: int
    group: str = ""


def _sign(kind: str) -> int:
    return -1 if kind == "REVERSAL_DOWN" else 1


def reversal_events(side: SideObjects, index: pd.DatetimeIndex) -> list[SignalEvent]:
    """``REVERSAL_*`` signals of one average at ``Signal.idx`` (DEFENSE_BREAK excluded)."""
    return [
        SignalEvent(s.idx, index[s.idx].date(), _sign(s.kind))
        for s in side.signals
        if s.kind in REVERSALS
    ]


def pair_reversal_groups(
    objs: PairObjects, horizon: int, max_days: int | None
) -> tuple[list[SignalEvent], list[SignalEvent]]:
    """R3 groups ``(confirmed, single)`` for horizon ``h``.

    Each ``^DJI`` reversal is matched cycle-aware with the other average (A7). *Confirmed*:
    matched at all, event bar = ``confirmed_ts`` (the later date). *Single*: no match with
    ``ts <= c + h`` (classification uses information up to ``c + h`` only; the event bar is
    still ``c``). A reversal matched later than ``c + h`` therefore appears in both groups,
    once at ``c`` and once at its own ``confirmed_ts`` (as the protocol words it).
    """
    a, b = objs.a, objs.b
    confirmed: list[SignalEvent] = []
    single: list[SignalEvent] = []
    for s in a.signals:
        if s.kind not in REVERSALS:
            continue
        sgn = _sign(s.kind)
        full = confirm_signal(s, a.signals, b.signals, max_days, None)
        if full.confirmed_ts is not None:
            bar = objs.bar_of(full.confirmed_ts)
            confirmed.append(SignalEvent(bar, full.confirmed_ts, sgn, "confirmed"))
        cut = objs.date_at(min(s.idx + horizon, objs.last))
        at_h = confirm_signal(s, a.signals, b.signals, max_days, cut)
        if at_h.status != "confirmed":
            single.append(SignalEvent(s.idx, objs.date_at(s.idx), sgn, "single"))
    return confirmed, single


# --------------------------------------------------------------------------- R4 / R5
@dataclass(frozen=True)
class LegEvent:
    bar: int
    date: dt.date
    counter: bool
    rr: Decimal
    in_band: bool
    in_half: bool
    d_cal: int
    d_bar: int
    rhea: bool
    schannep: bool


def leg_events(side: SideObjects, index: pd.DatetimeIndex) -> list[LegEvent]:
    """All secondary legs with a retrace ratio; ``counter`` marks the protocol's event set.

    Counter-trend: the leg ending at ``S_k`` runs against ``state(S_k.confirmed_idx)`` with
    the state in the four trend states (``UNDEFINED`` excluded).
    """
    out: list[LegEvent] = []
    sec = side.secondary
    for k, s in enumerate(sec):
        if k < 1 or s.retrace_ratio is None:
            continue
        st = side.snapshots[s.confirmed_idx].state
        counter = (st in (BULL_PRIMARY, BULL_SUSPECT) and s.kind == "L") or (
            st in (BEAR_PRIMARY, BEAR_SUSPECT) and s.kind == "H"
        )
        f = s.flags
        out.append(
            LegEvent(
                s.confirmed_idx, index[s.confirmed_idx].date(), counter, s.retrace_ratio,
                bool(f.get("retrace_in_third_two_thirds")), bool(f.get("retrace_in_third_half")),
                s.duration_days, s.idx - sec[k - 1].idx, bool(f.get("rhea_window")),
                bool(f.get("schannep_window")),
            )
        )
    return out


# --------------------------------------------------------------------------- R6
@dataclass(frozen=True)
class BreakoutSet:
    confirmed: list[SignalEvent]
    single: list[SignalEvent]
    n_lines: int
    n_breakouts: int
    mean_line_len: float


def detect_pair_lines(
    objs: PairObjects, band_pct: float, min_sessions: int, max_drift_frac: float
) -> list[LineRange]:
    """Lines under the given parameters (``inf`` as ``max_drift_frac`` disables the drift rule)."""
    return detect_lines(
        pd.Series(objs.a.close, index=objs.index), pd.Series(objs.b.close, index=objs.index),
        band_pct, min_sessions, None, objs.cfg.confirmation.max_days, max_drift_frac,
    )


def with_line(cfg: DowConfig, **changes: object) -> DowConfig:
    return dataclasses.replace(cfg, line=dataclasses.replace(cfg.line, **changes))


def breakout_groups(lines: list[LineRange], objs: PairObjects, horizon: int) -> BreakoutSet:
    """R6 groups. Confirmed-both: event bar = ``confirmed_ts``. Single: the other average has
    not broken the same way by ``c + h``; event bar = first breakout bar ``c``."""
    confirmed: list[SignalEvent] = []
    single: list[SignalEvent] = []
    broken = [ln for ln in lines if ln.breakout != "none" and ln.breakout_ts is not None]
    for ln in broken:
        sgn = 1 if ln.breakout == "up" else -1
        c = objs.bar_of(ln.breakout_ts)  # type: ignore[arg-type]
        if ln.confirmed_ts is not None:
            confirmed.append(SignalEvent(objs.bar_of(ln.confirmed_ts), ln.confirmed_ts, sgn, "confirmed"))
        late = ln.confirmed_ts is None or objs.bar_of(ln.confirmed_ts) > c + horizon
        if late:
            single.append(SignalEvent(c, ln.breakout_ts, sgn, "single"))  # type: ignore[arg-type]
    lengths = [(ln.end - ln.start).days for ln in lines]
    return BreakoutSet(
        confirmed, single, len(lines), len(broken), float(np.mean(lengths)) if lengths else 0.0
    )


# --------------------------------------------------------------------------- R7
@dataclass(frozen=True)
class LegPair:
    bar: int
    date: dt.date
    with_vol: float
    counter_vol: float


def leg_pair_events(
    side: SideObjects, index: pd.DatetimeIndex, start_bar: int, volume: np.ndarray | None = None
) -> list[LegPair]:
    """Consecutive legs ``(L_k, L_{k+1})`` in a PRIMARY state; volume is the mean over each leg.

    Swings and states come from the full history; only legs that begin on or after
    ``start_bar`` count. ``volume`` defaults to the side's raw volume. Pairs with a
    non-positive (or NaN) mean volume in either leg are dropped.
    """
    vol = side.volume if volume is None else volume
    csum = np.concatenate([[0.0], np.cumsum(np.nan_to_num(vol))])
    sec = side.secondary
    out: list[LegPair] = []
    for k in range(1, len(sec) - 1):
        p, q, r = sec[k - 1], sec[k], sec[k + 1]
        if p.idx < start_bar:
            continue
        c = r.confirmed_idx
        st = side.snapshots[c].state
        if st not in PRIMARY_STATES:
            continue
        v1 = _leg_mean(csum, vol, p.idx, q.idx)
        v2 = _leg_mean(csum, vol, q.idx, r.idx)
        if not (v1 > 0 and v2 > 0):
            continue
        last_with = (st == BULL_PRIMARY and r.kind == "H") or (st == BEAR_PRIMARY and r.kind == "L")
        out.append(LegPair(c, index[c].date(), v2 if last_with else v1, v1 if last_with else v2))
    return out


def _leg_mean(csum: np.ndarray, vol: np.ndarray, lo: int, hi: int) -> float:
    """Mean volume over bars ``(lo, hi]`` (``nan`` when the window is empty or has NaN)."""
    if hi <= lo or np.isnan(vol[lo + 1 : hi + 1]).any():
        return float("nan")
    return float((csum[hi + 1] - csum[lo + 1]) / (hi - lo))


def trailing_median_volume(volume: np.ndarray, window: int = 250) -> np.ndarray:
    """Volume divided by its trailing ``window``-bar median (``nan`` while the median is 0)."""
    med = pd.Series(volume).rolling(window, min_periods=window).median().to_numpy()
    with np.errstate(divide="ignore", invalid="ignore"):
        return np.where(med > 0, volume / med, np.nan)


# --------------------------------------------------------------------------- R8
def pair_states(objs: PairObjects) -> list[str | None]:
    """Per bar: the pair state when ``pair_confirm`` says ``confirmed`` and the state is PRIMARY."""
    out: list[str | None] = []
    for sa, sb in zip(objs.a.snapshots, objs.b.snapshots, strict=True):
        res = pair_confirm(sa, sb, [], [], None, None)
        out.append(res.pair_state if res.status == "confirmed" and res.pair_state in PRIMARY_STATES else None)
    return out


def position_series(states: list[str | None], objs: PairObjects, *, allow_short: bool) -> np.ndarray:
    """``pos_t`` decided at the close of bar ``t`` (1 long, 0 cash, -1 short)."""
    dji = [s.state for s in objs.a.snapshots]
    pos = np.zeros(len(states))
    for t, (ps, own) in enumerate(zip(states, dji, strict=True)):
        if ps == BULL_PRIMARY and own == BULL_PRIMARY:
            pos[t] = 1.0
        elif allow_short and ps == BEAR_PRIMARY and own == BEAR_PRIMARY:
            pos[t] = -1.0
    return pos


@dataclass(frozen=True)
class Call:
    bar: int
    date: dt.date
    sign: int


def calls_from_states(states: list[str | None], index: pd.DatetimeIndex) -> list[Call]:
    """A call at every bar where the pair-confirmed state first becomes BULL or BEAR."""
    out: list[Call] = []
    prev: str | None = None
    for t, s in enumerate(states):
        if s is not None and s != prev:
            out.append(Call(t, index[t].date(), 1 if s == BULL_PRIMARY else -1))
        prev = s
    return out
