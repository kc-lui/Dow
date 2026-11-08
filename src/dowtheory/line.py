"""Dow "line": a sideways range in both averages, and the breakout that ends it."""

from __future__ import annotations

import datetime as dt
from dataclasses import dataclass
from typing import Literal

import numpy as np
import pandas as pd

Direction = Literal["up", "down", "none"]


@dataclass(frozen=True)
class LineRange:
    """A qualifying consolidation window and how (and whether) it was resolved.

    ``confirmed_ts`` is the later of the two averages' breakout dates (same direction); it
    is ``None`` while the other average has not broken out yet. ``confirmed_both`` is
    evaluated with data up to ``as_of`` only, i.e. it equals ``confirmed_ts is not None``.
    """

    start: dt.date
    end: dt.date
    band_pct_a: float
    band_pct_b: float
    breakout: Direction
    breakout_ts: dt.date | None
    confirmed_both: bool
    confirmed_ts: dt.date | None = None


def _window_end(values: np.ndarray, band_pct: float, start: int, stop: int) -> int:
    """Largest ``j`` in ``[start, stop]`` such that ``values[start..j]`` stays within the band."""
    lo = hi = values[start]
    total = 0.0
    end = start
    for j in range(start, stop + 1):
        v = values[j]
        new_lo, new_hi = min(lo, v), max(hi, v)
        mean = (total + v) / (j - start + 1)
        if mean <= 0 or (new_hi - new_lo) / mean > band_pct:
            break
        lo, hi, total, end = new_lo, new_hi, total + v, j
    return end


def _first_breakout(
    values: np.ndarray, lo: float, hi: float, after: int, stop: int
) -> tuple[int, Direction] | None:
    """First index in ``(after, stop]`` where the close leaves ``[lo, hi]``."""
    for k in range(after + 1, stop + 1):
        if values[k] > hi:
            return k, "up"
        if values[k] < lo:
            return k, "down"
    return None


def _drift_ok(values: np.ndarray, i: int, end: int, limit: float) -> bool:
    """Net drift |close_end / close_start - 1| stays within ``limit``."""
    return abs(values[end] / values[i] - 1.0) <= limit


def detect_lines(
    close_a: pd.Series,
    close_b: pd.Series,
    band_pct: float = 0.05,
    min_sessions: int = 15,
    as_of_idx: int | None = None,
    max_days: int | None = None,
    max_drift_frac: float = 0.5,
) -> list[LineRange]:
    """Find sideways windows in both averages and the breakout that ends them.

    A window qualifies when, for both series, ``(max - min) / mean <= band_pct`` over at
    least ``min_sessions`` consecutive trading sessions and the net drift
    ``|close_end / close_start - 1|`` is at most ``band_pct * max_drift_frac``. The window
    is the longest in-band window from its start (greedy); windows do not overlap. A maximal
    window that fails the drift rule is consumed without being reported.

    The breakout is the first later close outside the window's min/max range in either
    series (earliest wins). ``confirmed_ts`` is the date the other series has broken out the
    same way (``None`` until then, or if it lies more than ``max_days`` calendar days after
    the first break); ``confirmed_both`` is ``confirmed_ts is not None``. Only bars up to
    ``as_of_idx`` (default: last bar) are used, so results are invariant under truncation of
    later data.

    Raises:
        ValueError: if the series are not index-aligned.
    """
    if len(close_a) != len(close_b) or not close_a.index.equals(close_b.index):
        raise ValueError("close_a and close_b must share the same index")
    n = len(close_a)
    if n == 0:
        return []
    stop = n - 1 if as_of_idx is None else min(as_of_idx, n - 1)
    a = close_a.to_numpy(dtype=float)
    b = close_b.to_numpy(dtype=float)
    index = close_a.index
    limit = band_pct * max_drift_frac

    out: list[LineRange] = []
    i = 0
    while i <= stop:
        end = _joint_end(a, b, band_pct, i, min(_window_end(a, band_pct, i, stop),
                                                _window_end(b, band_pct, i, stop)))
        if end - i + 1 < min_sessions:
            i += 1
            continue
        # A long in-band window that drifts is a slow trend, not a line: it is consumed
        # (so the next candidate cannot chain onto it) but not reported.
        if _drift_ok(a, i, end, limit) and _drift_ok(b, i, end, limit):
            out.append(_build(index, a, b, i, end, stop, max_days))
        i = end + 1
    return out


def _joint_end(a: np.ndarray, b: np.ndarray, band_pct: float, start: int, end: int) -> int:
    """Shrink ``end`` until both series satisfy the band over ``[start, end]``."""
    while end > start:
        if (
            _window_end(a, band_pct, start, end) == end
            and _window_end(b, band_pct, start, end) == end
        ):
            return end
        end -= 1
    return start


def _build(
    index: pd.Index, a: np.ndarray, b: np.ndarray, i: int, end: int, stop: int,
    max_days: int | None,
) -> LineRange:
    sa, sb = a[i : end + 1], b[i : end + 1]
    band_a = float((sa.max() - sa.min()) / sa.mean())
    band_b = float((sb.max() - sb.min()) / sb.mean())
    brk_a = _first_breakout(a, float(sa.min()), float(sa.max()), end, stop)
    brk_b = _first_breakout(b, float(sb.min()), float(sb.max()), end, stop)
    first = [x for x in (brk_a, brk_b) if x is not None]
    if not first:
        return LineRange(index[i].date(), index[end].date(), band_a, band_b, "none", None, False)
    k, direction = min(first, key=lambda x: x[0])
    confirmed_ts = None
    if brk_a is not None and brk_b is not None and brk_a[1] == brk_b[1]:
        k2 = max(brk_a[0], brk_b[0])
        if max_days is None or (index[k2] - index[k]).days <= max_days:
            confirmed_ts = index[k2].date()
    return LineRange(
        index[i].date(), index[end].date(), band_a, band_b, direction, index[k].date(),
        confirmed_ts is not None, confirmed_ts,
    )
