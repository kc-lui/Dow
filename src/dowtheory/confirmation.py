"""Two-average confirmation (DJI vs DJT) and the volume check."""

from __future__ import annotations

import itertools
from collections.abc import Sequence
from dataclasses import dataclass
from typing import TYPE_CHECKING, Literal

import pandas as pd

if TYPE_CHECKING:
    from dowtheory.swings import Swing
    from dowtheory.trend import Signal, TrendState

Status = Literal["confirmed", "non_confirmation", "pending"]
_CONFIRMABLE = {"REVERSAL_UP", "REVERSAL_DOWN", "LINE_BREAKOUT_UP", "LINE_BREAKOUT_DOWN"}


@dataclass(frozen=True)
class ConfirmationResult:
    """Outcome of comparing the two averages' trend states."""

    status: Status
    pair_state: str | None
    detail: str


def _side(state: str) -> str | None:
    if state.startswith("BULL"):
        return "bull"
    if state.startswith("BEAR"):
        return "bear"
    return None


def signal_confirmed(signal: Signal, others: Sequence[Signal], max_days: int | None) -> bool:
    """True if the other average shows a signal of the same kind within ``max_days`` days.

    With ``max_days`` the other signal may precede or follow within that many days; with
    ``None`` it must occur on or after the signal date (any later date). Only already-known signals are passed in, so nothing here looks ahead.
    """
    for o in others:
        if o.kind != signal.kind:
            continue
        delta = (o.ts - signal.ts).days
        if (max_days is None and delta >= 0) or (max_days is not None and abs(delta) <= max_days):
            return True
    return False


def pair_confirm(
    state_a: TrendState,
    state_b: TrendState,
    signals_a: Sequence[Signal],
    signals_b: Sequence[Signal],
    max_days: int | None = None,
) -> ConfirmationResult:
    """Classify the pair as confirmed, non-confirming or pending.

    - Either side ``UNDEFINED`` -> ``pending``.
    - Opposite sides (bull vs bear) -> ``non_confirmation``.
    - Same side but one PRIMARY and one SUSPECT -> ``non_confirmation`` (one average has
      already failed to make a new extreme).
    - Identical states -> ``confirmed`` with that state as ``pair_state``.

    The latest reversal signal of average A is also reported in ``detail`` with whether B
    confirmed it within ``max_days``.
    """
    sa, sb = state_a.state, state_b.state
    side_a, side_b = _side(sa), _side(sb)
    if side_a is None or side_b is None:
        status: Status = "pending"
        pair_state = None
        detail = f"A={sa}, B={sb}: at least one average has no defined trend yet"
    elif side_a != side_b:
        status, pair_state = "non_confirmation", None
        detail = f"A={sa} and B={sb} point in opposite directions"
    elif sa != sb:
        status, pair_state = "non_confirmation", None
        detail = f"A={sa} and B={sb}: only one average has stalled (lower high / higher low)"
    else:
        status, pair_state = "confirmed", sa
        detail = f"Both averages are {sa}"

    reversals = [s for s in signals_a if s.kind in ("REVERSAL_UP", "REVERSAL_DOWN")]
    if reversals:
        last = reversals[-1]
        ok = signal_confirmed(last, signals_b, max_days)
        detail += (
            f"; latest A {last.kind} on {last.ts} "
            f"{'confirmed' if ok else 'not yet confirmed'} by B"
        )
    return ConfirmationResult(status, pair_state, detail)


def volume_confirms(df: pd.DataFrame, swings: Sequence[Swing]) -> bool | None:
    """Does volume expand in the direction of the net move (Dow: volume confirms the trend)?

    Uses legs between the last four swings (at most three). Legs moving with the net move
    between the first and last of those swings are "aligned"; the rest are "counter". Returns
    whether mean daily volume on aligned legs exceeds that on counter legs. ``None`` when
    volume is all zero or fewer than one aligned and one counter leg exist.
    """
    if "volume" not in df.columns or float(df["volume"].sum()) == 0.0:
        return None
    pts = sorted(swings, key=lambda s: s.idx)[-4:]
    if len(pts) < 3:
        return None
    net_up = pts[-1].price > pts[0].price
    volume = df["volume"].to_numpy(dtype=float)
    aligned: list[float] = []
    counter: list[float] = []
    for p, q in itertools.pairwise(pts):
        seg = volume[p.idx + 1 : q.idx + 1]
        if seg.size == 0:
            continue
        (aligned if (q.price > p.price) == net_up else counter).append(float(seg.mean()))
    if not aligned or not counter:
        return None
    return sum(aligned) / len(aligned) > sum(counter) / len(counter)
