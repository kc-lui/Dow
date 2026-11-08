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
    """A qualifying consolidation window and how (and whether) it was resolved."""

    start: dt.date
    end: dt.date
    band_pct_a: float
    band_pct_b: float
    breakout: Direction
    breakout_ts: dt.date | None
    confirmed_both: bool


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


def detect_lines(
    close_a: pd.Series,
    close_b: pd.Series,
    band_pct: float = 0.05,
    min_days: int = 14,
    as_of_idx: int | None = None,
    max_days: int | None = None,
) -> list[LineRange]:
    """Find windows where both series stay within ``band_pct`` for ``min_days`` sessions.

    A window qualifies when ``(max - min) / mean <= band_pct`` holds for both series over
    at least ``min_days`` consecutive sessions; it is extended greedily and windows do not
    overlap. The breakout is the first later close outside the window's min/max range in
    either series (earliest wins). ``confirmed_both`` is true when the other series breaks
    the same way within ``max_days`` calendar days (``None`` = any date up to ``as_of``).
    Only bars up to ``as_of_idx`` (default: last bar) are used.

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

    out: list[LineRange] = []
    i = 0
    while i <= stop:
        end = min(_window_end(a, band_pct, i, stop), _window_end(b, band_pct, i, stop))
        # The two series may stop at different bars; re-check the shorter window for both.
        end = _joint_end(a, b, band_pct, i, end)
        if end - i + 1 < min_days:
            i += 1
            continue
        out.append(_build(index, a, b, i, end, stop, max_days))
        i = end + 1
    return out


def _joint_end(a: np.ndarray, b: np.ndarray, band_pct: float, start: int, end: int) -> int:
    """Shrink ``end`` until both series satisfy the band over ``[start, end]``."""
    while end > start:
        if _window_end(a, band_pct, start, end) == end and _window_end(b, band_pct, start, end) == end:
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
        return LineRange(
            index[i].date(), index[end].date(), band_a, band_b, "none", None, False
        )
    k, direction = min(first, key=lambda x: x[0])
    confirmed = False
    if brk_a is not None and brk_b is not None:
        lag = (index[max(brk_a[0], brk_b[0])] - index[k]).days
        confirmed = brk_a[1] == brk_b[1] and (max_days is None or lag <= max_days)
    return LineRange(
        index[i].date(), index[end].date(), band_a, band_b, direction, index[k].date(), confirmed
    )
