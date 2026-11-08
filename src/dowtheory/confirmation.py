"""Two-average confirmation (DJI vs DJT) and the volume check."""

from __future__ import annotations

import datetime as dt
import itertools
from collections.abc import Sequence
from dataclasses import dataclass
from typing import TYPE_CHECKING, Literal

import pandas as pd

if TYPE_CHECKING:
    from dowtheory.swings import Swing
    from dowtheory.trend import Signal, TrendState

Status = Literal["confirmed", "non_confirmation", "pending"]
REVERSAL_KINDS = ("REVERSAL_UP", "REVERSAL_DOWN")


@dataclass(frozen=True)
class ConfirmationResult:
    """Outcome of comparing the two averages' trend states."""

    status: Status
    pair_state: str | None
    detail: str
    confirmed_ts: dt.date | None = None


@dataclass(frozen=True)
class SignalConfirmation:
    """Confirmation of one reversal: ``confirmed_ts`` is the later of the two dates."""

    status: Literal["confirmed", "pending"]
    confirmed_ts: dt.date | None
    matched_ts: dt.date | None


def _side(state: str) -> str | None:
    if state.startswith("BULL"):
        return "bull"
    if state.startswith("BEAR"):
        return "bear"
    return None


def _in_window(sig_ts: dt.date, lo: dt.date | None, hi: dt.date | None) -> bool:
    return (lo is None or sig_ts > lo) and (hi is None or sig_ts <= hi)


def confirm_signal(
    signal: Signal,
    signals_a: Sequence[Signal],
    signals_b: Sequence[Signal],
    max_days: int | None = None,
    as_of: dt.date | None = None,
) -> SignalConfirmation:
    """Match a reversal on average A with the other average's same-kind reversal.

    Matching is cycle-aware and works in either order. The cycle of ``signal`` lies between
    the previous and the next reversal on A (both from ``signals_a``). A candidate is a B
    signal of the same kind inside that cycle with no opposite-kind B reversal between the
    candidate and ``signal``. A candidate that leads (or coincides) wins, the latest one
    first; otherwise the earliest following candidate is used. ``max_days`` (calendar days)
    limits the distance; ``None`` means no limit. Only signals on or before ``as_of`` are
    used, and ``confirmed_ts`` is the later of the two dates, so the status at any date
    ``t`` equals ``confirmed_ts is not None and confirmed_ts <= t`` (truncation invariant).
    """
    if signal.kind not in REVERSAL_KINDS:
        return SignalConfirmation("pending", None, None)

    def known(sig: Signal) -> bool:
        return as_of is None or sig.ts <= as_of

    rev_a = sorted(
        (s for s in signals_a if s.kind in REVERSAL_KINDS and known(s)), key=lambda s: s.ts
    )
    prev_ts = max((s.ts for s in rev_a if s.ts < signal.ts), default=None)
    next_ts = min((s.ts for s in rev_a if s.ts > signal.ts), default=None)
    rev_b = [s for s in signals_b if s.kind in REVERSAL_KINDS and known(s)]
    same = [s for s in rev_b if s.kind == signal.kind and _in_window(s.ts, prev_ts, next_ts)]
    opposite = [s.ts for s in rev_b if s.kind != signal.kind]

    def within(b: Signal) -> bool:
        return max_days is None or abs((b.ts - signal.ts).days) <= max_days

    leading = sorted((s for s in same if s.ts <= signal.ts and within(s)), key=lambda s: s.ts)
    for cand in reversed(leading):
        if not any(cand.ts < o <= signal.ts for o in opposite):
            return SignalConfirmation("confirmed", signal.ts, cand.ts)
    following = sorted((s for s in same if s.ts > signal.ts and within(s)), key=lambda s: s.ts)
    for cand in following:
        if not any(signal.ts < o < cand.ts for o in opposite):
            return SignalConfirmation("confirmed", cand.ts, cand.ts)
    return SignalConfirmation("pending", None, None)


def pair_confirm(
    state_a: TrendState,
    state_b: TrendState,
    signals_a: Sequence[Signal],
    signals_b: Sequence[Signal],
    max_days: int | None = None,
    as_of: dt.date | None = None,
) -> ConfirmationResult:
    """Classify the pair as confirmed, non-confirming or pending as of ``as_of``.

    - Either side ``UNDEFINED`` -> ``pending``.
    - Opposite sides (bull vs bear) -> ``non_confirmation``.
    - Same side but one PRIMARY and one SUSPECT -> ``non_confirmation`` (one average has
      already failed to make a new extreme).
    - Identical states -> ``confirmed`` with that state as ``pair_state``.

    The states must already be computed as of ``as_of``; signals after ``as_of`` are
    ignored. The latest A reversal is reported in ``detail`` with its cycle-aware match
    (see :func:`confirm_signal`) and ``confirmed_ts``.
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

    known_a = [s for s in signals_a if as_of is None or s.ts <= as_of]
    reversals = [s for s in known_a if s.kind in REVERSAL_KINDS]
    confirmed_ts = None
    if reversals:
        last = reversals[-1]
        res = confirm_signal(last, signals_a, signals_b, max_days, as_of)
        confirmed_ts = res.confirmed_ts
        if res.matched_ts is not None:
            detail += (
                f"; latest A {last.kind} on {last.ts} matched by B on {res.matched_ts} "
                f"(confirmed {res.confirmed_ts})"
            )
        else:
            detail += f"; latest A {last.kind} on {last.ts} not yet confirmed by B"
    return ConfirmationResult(status, pair_state, detail, confirmed_ts)


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
