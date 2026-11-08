"""Causal swing detection on closing prices (Dow: closes only).

Every swing carries ``confirmed_idx``, the first bar at which it became knowable.
All detectors are causal, so ``detect_swings(close[:t+1])`` restricted to swings confirmed
at or before ``t`` equals ``swings_as_of(detect_swings(close), t)`` (no lookahead).
"""

from __future__ import annotations

import datetime as dt
from collections.abc import Callable, Sequence
from dataclasses import dataclass, replace
from decimal import Decimal
from typing import Literal, NamedTuple

import numpy as np
import pandas as pd

from dowtheory.config import DowConfig

Kind = Literal["H", "L"]
Scale = Literal["minor", "secondary", "primary"]
Method = Literal["pct", "atr", "pivot"]

_PRICE_Q = Decimal("0.0001")
_RATIO_Q = Decimal("0.000001")
_EPS = 1e-12
_SNAP_BARS = 2


@dataclass(frozen=True)
class Swing:
    """A confirmed swing extreme (see ``docs/specs/algorithm_contract.md``)."""

    idx: int
    ts: dt.date
    price: Decimal
    kind: Kind
    confirmed_idx: int
    confirmed_ts: dt.date
    scale: Scale
    amplitude_pct: Decimal
    duration_days: int
    retrace_ratio: Decimal | None = None


class _Raw(NamedTuple):
    idx: int
    kind: Kind
    confirmed_idx: int


def to_price(value: float | Decimal | str) -> Decimal:
    """Convert a price to ``Decimal`` quantised to 4 dp (floats go through ``str``)."""
    if isinstance(value, Decimal):
        return value.quantize(_PRICE_Q)
    return Decimal(str(float(value))).quantize(_PRICE_Q)


def _opposite(kind: Kind) -> Kind:
    return "L" if kind == "H" else "H"


# --------------------------------------------------------------------------- detectors
def _atr(close: pd.Series, high: pd.Series | None, low: pd.Series | None, window: int) -> pd.Series:
    """Simple-mean average true range; close-to-close range when high/low are absent."""
    prev = close.shift(1)
    if high is None or low is None:
        true_range = (close - prev).abs()
    else:
        true_range = pd.concat(
            [high - low, (high - prev).abs(), (low - prev).abs()], axis=1
        ).max(axis=1)
    return true_range.rolling(window, min_periods=window).mean()


def _arg_extreme(values: np.ndarray, start: int, stop: int, kind: Kind) -> int:
    """Index of the first max (kind ``H``) or min (``L``) in ``values[start:stop]``."""
    seg = values[start:stop]
    return start + int(np.argmax(seg) if kind == "H" else np.argmin(seg))


def _moved(x: float, ref: float, thr: float, sign: int) -> bool:
    """True when ``x`` moved at least ``thr`` (fraction of ``ref``) in direction ``sign``."""
    return sign * (x / ref - 1.0) >= thr - _EPS


def _decide_start(v: np.ndarray, i: int, hi: int, lo: int, thr: Callable[[int, float], float]):
    """Resolve the very first swing: returns (kind confirmed, extreme idx) or ``None``."""
    rise = _moved(v[i], v[lo], thr(i, v[lo]), +1)
    fall = _moved(v[i], v[hi], thr(i, v[hi]), -1)
    if rise and (not fall or lo < hi):
        return "L", lo
    if fall:
        return "H", hi
    return None


def _zigzag(v: np.ndarray, thr: Callable[[int, float], float]) -> list[_Raw]:
    """Causal zig-zag: a candidate extreme flips once price retraces ``thr`` against it."""
    out: list[_Raw] = []
    hi = lo = 0
    cand: int | None = None
    cand_kind: Kind = "H"
    for i in range(1, len(v)):
        x = v[i]
        if cand is None:
            hi, lo = (i if x > v[hi] else hi), (i if x < v[lo] else lo)
            start = _decide_start(v, i, hi, lo, thr)
            if start is None:
                continue
            kind, ext = start
            out.append(_Raw(ext, kind, i))
            cand_kind = _opposite(kind)
            cand = _arg_extreme(v, ext + 1, i + 1, cand_kind)
        elif cand_kind == "H":
            if x > v[cand]:
                cand = i
            elif _moved(x, v[cand], thr(i, v[cand]), -1):
                out.append(_Raw(cand, "H", i))
                cand, cand_kind = _arg_extreme(v, cand + 1, i + 1, "L"), "L"
        else:
            if x < v[cand]:
                cand = i
            elif _moved(x, v[cand], thr(i, v[cand]), +1):
                out.append(_Raw(cand, "L", i))
                cand, cand_kind = _arg_extreme(v, cand + 1, i + 1, "H"), "H"
    return out


def _pivot_candidates(v: np.ndarray, n: int) -> list[_Raw]:
    """Bars that are the max/min of ``close[i-n..i+n]`` (flat windows are skipped)."""
    s = pd.Series(v)
    window = 2 * n + 1
    top = s.rolling(window, center=True).max().to_numpy()
    bottom = s.rolling(window, center=True).min().to_numpy()
    out: list[_Raw] = []
    for i in range(n, len(v) - n):
        is_h, is_l = v[i] == top[i], v[i] == bottom[i]
        if is_h and not is_l:
            out.append(_Raw(i, "H", i + n))
        elif is_l and not is_h:
            out.append(_Raw(i, "L", i + n))
    return out


def _alternate(cands: Sequence[_Raw], v: np.ndarray) -> list[_Raw]:
    """Enforce H/L alternation without ever rewriting an already emitted swing.

    Two same-kind pivots with no opposite pivot between them keep both and get the deepest
    close between them inserted as the opposite swing (confirmed together with the second
    pivot). Plateau repeats with no real dip are dropped (the earlier one wins). Append-only
    emission is what makes the detector truncation invariant.
    """
    out: list[_Raw] = []
    for c in cands:
        if out and out[-1].kind == c.kind:
            prev = out[-1]
            if c.idx - prev.idx < 2:
                continue
            opp = _opposite(c.kind)
            k = _arg_extreme(v, prev.idx + 1, c.idx, opp)
            bound = min(v[prev.idx], v[c.idx]) if c.kind == "H" else max(v[prev.idx], v[c.idx])
            dips = v[k] < bound if c.kind == "H" else v[k] > bound
            if not dips:
                continue
            out.append(_Raw(k, opp, c.confirmed_idx))
        out.append(c)
    return out


# --------------------------------------------------------------------------- building
def _amplitude(price: Decimal, prev: Decimal | None) -> Decimal:
    if prev is None or prev == 0:
        return Decimal(0).quantize(_RATIO_Q)
    return abs(price / prev - 1).quantize(_RATIO_Q)


def _to_date(ts: object) -> dt.date:
    return pd.Timestamp(ts).date()  # type: ignore[arg-type]


def _build(raws: Sequence[_Raw], close: pd.Series, scale: Scale) -> list[Swing]:
    swings: list[Swing] = []
    for r in raws:
        ts, cts = _to_date(close.index[r.idx]), _to_date(close.index[r.confirmed_idx])
        price = to_price(close.iloc[r.idx])
        prev = swings[-1] if swings else None
        swings.append(
            Swing(
                idx=r.idx,
                ts=ts,
                price=price,
                kind=r.kind,
                confirmed_idx=r.confirmed_idx,
                confirmed_ts=cts,
                scale=scale,
                amplitude_pct=_amplitude(price, prev.price if prev else None),
                duration_days=(ts - prev.ts).days if prev else 0,
                retrace_ratio=None,
            )
        )
    return swings


def _aligned(series: pd.Series | None, close: pd.Series) -> pd.Series | None:
    if series is None:
        return None
    if len(series) != len(close):
        raise ValueError("high/low must have the same length as close")
    return pd.Series(series.to_numpy(dtype=float), index=close.index)


def detect_swings(
    close: pd.Series,
    *,
    method: Method = "pct",
    threshold: float = 0.03,
    atr_mult: float = 2.0,
    atr_window: int = 14,
    pivot_n: int = 5,
    high: pd.Series | None = None,
    low: pd.Series | None = None,
    scale: Scale = "minor",
) -> list[Swing]:
    """Detect strictly alternating confirmed swings on ``close`` (see module docstring)."""
    if close.isna().any():
        raise ValueError("close contains NaN")
    v = close.to_numpy(dtype=float)
    if method == "pct":
        if threshold <= 0:
            raise ValueError("threshold must be > 0")
        raws = _zigzag(v, lambda _i, _p: threshold)
    elif method == "atr":
        atr = _atr(close, _aligned(high, close), _aligned(low, close), atr_window).to_numpy()
        raws = _zigzag(v, lambda i, p: atr_mult * atr[i] / p if atr[i] > 0 else float("nan"))
    elif method == "pivot":
        if pivot_n < 1:
            raise ValueError("pivot_n must be >= 1")
        raws = _alternate(_pivot_candidates(v, pivot_n), v)
    else:
        raise ValueError(f"Unknown swing method '{method}'")
    return _build(raws, close, scale)


def swings_as_of(swings: Sequence[Swing], t_idx: int) -> list[Swing]:
    """Swings knowable at bar ``t_idx`` (``confirmed_idx <= t_idx``)."""
    return [s for s in swings if s.confirmed_idx <= t_idx]


# --------------------------------------------------------------------------- scales
def nest_scales(
    minor: Sequence[Swing], secondary: Sequence[Swing]
) -> tuple[list[Swing], dict[int, bool]]:
    """Snap each secondary swing to the nearest same-kind minor swing within +-2 bars.

    A snapped swing takes the minor swing's bar and price; its ``confirmed_idx`` becomes the
    later of the two confirmations (no lookahead). Returns the new list and a ``snapped``
    flag per final swing ``idx``; unsnapped swings are kept unchanged with flag ``False``.
    """
    out: list[Swing] = []
    flags: dict[int, bool] = {}
    for sec in secondary:
        near = [m for m in minor if m.kind == sec.kind and abs(m.idx - sec.idx) <= _SNAP_BARS]
        if not near:
            out.append(sec)
            flags[sec.idx] = False
            continue
        m = min(near, key=lambda x: (abs(x.idx - sec.idx), x.idx))
        later = m if m.confirmed_idx > sec.confirmed_idx else sec
        out.append(
            replace(
                sec,
                idx=m.idx,
                ts=m.ts,
                price=m.price,
                confirmed_idx=later.confirmed_idx,
                confirmed_ts=later.confirmed_ts,
            )
        )
        flags[m.idx] = True
    return out, flags


def compute_secondary_metrics(swings: Sequence[Swing]) -> list[Swing]:
    """Fill ``amplitude_pct``, ``duration_days`` and ``retrace_ratio`` from the swing chain."""
    out: list[Swing] = []
    for k, s in enumerate(swings):
        prev = swings[k - 1] if k else None
        retrace: Decimal | None = None
        if k >= 2:
            prev_leg = abs(swings[k - 1].price - swings[k - 2].price)
            if prev_leg:
                retrace = (abs(s.price - swings[k - 1].price) / prev_leg).quantize(_RATIO_Q)
        out.append(
            replace(
                s,
                amplitude_pct=_amplitude(s.price, prev.price if prev else None),
                duration_days=(s.ts - prev.ts).days if prev else 0,
                retrace_ratio=retrace,
            )
        )
    return out


def detect_multiscale(
    close: pd.Series,
    cfg: DowConfig,
    high: pd.Series | None = None,
    low: pd.Series | None = None,
) -> dict[str, list[Swing]]:
    """Detect minor and secondary swings with the configured method.

    The secondary scale widens the minor parameters by ``secondary_pct / minor_pct``
    (``atr_mult`` scaled, ``pivot_n`` scaled and rounded). The secondary list is snapped
    onto the minor swings and has its metrics filled.
    """
    sw = cfg.swings
    ratio = sw.secondary_pct / sw.minor_pct
    common = {"method": sw.method, "atr_window": sw.atr_window, "high": high, "low": low}
    minor = detect_swings(
        close,
        threshold=sw.minor_pct,
        atr_mult=sw.atr_mult,
        pivot_n=sw.pivot_n,
        scale="minor",
        **common,  # type: ignore[arg-type]
    )
    secondary = detect_swings(
        close,
        threshold=sw.secondary_pct,
        atr_mult=sw.atr_mult * ratio,
        pivot_n=max(1, round(sw.pivot_n * ratio)),
        scale="secondary",
        **common,  # type: ignore[arg-type]
    )
    nested, _flags = nest_scales(minor, secondary)
    return {"minor": minor, "secondary": compute_secondary_metrics(nested)}
