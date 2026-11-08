"""Statistics for the rule backtests (pure functions of arrays and a seed).

Decimal values are converted to float here and nowhere else. Every resampling routine takes a
``numpy.random.Generator``; build it with :func:`make_rng` so that each (rule, pair,
specification) starts from the protocol seed.
"""

from __future__ import annotations

import math
from collections.abc import Iterable, Sequence
from decimal import Decimal
from fractions import Fraction
from statistics import NormalDist
from typing import Literal

import numpy as np

SEED = 20261108
Alternative = Literal["greater", "less", "two-sided"]
_CHUNK_CELLS = 4_000_000  # max cells of a (draws x length) work matrix


def make_rng(seed: int = SEED) -> np.random.Generator:
    """Fresh generator from the protocol seed."""
    return np.random.default_rng(seed)


def to_float_array(values: Iterable[float | Decimal | int]) -> np.ndarray:
    """The single Decimal -> float conversion point."""
    return np.asarray([float(v) for v in values], dtype=float)


# --------------------------------------------------------------------------- binomial
def _pmf(n: int, p: Fraction) -> list[Fraction]:
    q = 1 - p
    return [math.comb(n, i) * p**i * q ** (n - i) for i in range(n + 1)]


def binomial_pvalue(
    k: int, n: int, p0: float = 0.5, alternative: Alternative = "greater"
) -> float:
    """Exact binomial test (rational arithmetic, no scipy).

    ``greater``: ``P(X >= k)``; ``less``: ``P(X <= k)``; ``two-sided``: total probability of
    outcomes no more likely than ``k``. ``n == 0`` gives ``nan``.
    """
    if n == 0:
        return float("nan")
    if not 0 <= k <= n:
        raise ValueError("k must lie in [0, n]")
    p = Fraction(p0).limit_denominator(10**6)
    pmf = _pmf(n, p)
    if alternative == "greater":
        val = sum(pmf[k:], Fraction(0))
    elif alternative == "less":
        val = sum(pmf[: k + 1], Fraction(0))
    elif alternative == "two-sided":
        val = sum((x for x in pmf if x <= pmf[k]), Fraction(0))
    else:
        raise ValueError(f"unknown alternative {alternative!r}")
    return float(min(val, Fraction(1)))


def _z(level: float) -> float:
    return NormalDist().inv_cdf(level)


def wilson_interval(k: int, n: int, conf: float = 0.95) -> tuple[float, float]:
    """Two-sided Wilson score interval."""
    return _wilson(k, n, _z(0.5 + conf / 2))


def wilson_bound(k: int, n: int, level: float, side: Literal["upper", "lower"] = "upper") -> float:
    """One-sided Wilson bound at confidence ``level`` (e.g. ``1 - 0.05/8``)."""
    lo, hi = _wilson(k, n, _z(level))
    return hi if side == "upper" else lo


def _wilson(k: int, n: int, z: float) -> tuple[float, float]:
    if n == 0:
        return float("nan"), float("nan")
    phat = k / n
    denom = 1 + z * z / n
    centre = (phat + z * z / (2 * n)) / denom
    half = z * math.sqrt(phat * (1 - phat) / n + z * z / (4 * n * n)) / denom
    return max(0.0, centre - half), min(1.0, centre + half)


# --------------------------------------------------------------------------- summaries
def percentile_interval(dist: np.ndarray, conf: float = 0.95) -> tuple[float, float]:
    """Two-sided percentile interval of a bootstrap distribution."""
    if dist.size == 0:
        return float("nan"), float("nan")
    a = (1 - conf) / 2
    lo, hi = np.quantile(dist, [a, 1 - a])
    return float(lo), float(hi)


def upper_percentile(dist: np.ndarray, level: float) -> float:
    """One-sided upper bound: the ``level`` quantile of a bootstrap distribution."""
    return float(np.quantile(dist, level)) if dist.size else float("nan")


def one_sided_p(null: np.ndarray, observed: float, alternative: Alternative = "greater") -> float:
    """``(1 + #{null as extreme or more}) / (B + 1)`` (Davison-Hinkley)."""
    if null.size == 0 or math.isnan(observed):
        return float("nan")
    if alternative == "greater":
        hits = int(np.sum(null >= observed))
    elif alternative == "less":
        hits = int(np.sum(null <= observed))
    else:
        raise ValueError("one_sided_p handles greater/less only")
    return (1 + hits) / (null.size + 1)


def median_interval(
    values: Sequence[float | Decimal], rng: np.random.Generator, n_iter: int, conf: float = 0.95
) -> tuple[float, float, float]:
    """Median with an ordinary percentile bootstrap CI (descriptive use)."""
    x = to_float_array(values)
    if x.size == 0:
        return (float("nan"),) * 3
    draws = rng.integers(0, x.size, size=(n_iter, x.size))
    meds = np.median(x[draws], axis=1)
    lo, hi = percentile_interval(meds, conf)
    return float(np.median(x)), lo, hi


# --------------------------------------------------------------------------- clusters
def cluster_ids(bars: Sequence[int], horizon: int) -> np.ndarray:
    """Cluster label per event; events with overlapping forward windows share a cluster.

    The forward window of event bar ``c`` is ``[c+1, c+1+h]``, so two events overlap when
    their bars differ by at most ``h``. Overlap is chained (single linkage). Events on the
    same bar always share a cluster.
    """
    arr = np.asarray(bars, dtype=int)
    order = np.argsort(arr, kind="stable")
    ids = np.zeros(arr.size, dtype=int)
    cur = -1
    prev = None
    for pos in order:
        if prev is None or arr[pos] - prev > horizon:
            cur += 1
        ids[pos] = cur
        prev = arr[pos]
    return ids


def _cluster_sums(values: np.ndarray, ids: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    g = int(ids.max()) + 1 if ids.size else 0
    return np.bincount(ids, weights=values, minlength=g), np.bincount(ids, minlength=g).astype(float)


def cluster_bootstrap_mean(
    values: np.ndarray, ids: np.ndarray, n_iter: int, rng: np.random.Generator
) -> np.ndarray:
    """Event mean over clusters resampled with replacement (``n_iter`` draws)."""
    if values.size == 0:
        return np.empty(0)
    sums, counts = _cluster_sums(values, ids)
    g = sums.size
    out = np.empty(n_iter)
    step = max(1, _CHUNK_CELLS // g)
    for lo in range(0, n_iter, step):
        b = min(step, n_iter - lo)
        draws = rng.integers(0, g, size=(b, g))
        out[lo : lo + b] = sums[draws].sum(axis=1) / counts[draws].sum(axis=1)
    return out


def cluster_bootstrap_diff(
    x: np.ndarray, ids_x: np.ndarray, y: np.ndarray, ids_y: np.ndarray, n_iter: int,
    rng: np.random.Generator,
) -> np.ndarray:
    """``mean(x*) - mean(y*)`` with clusters resampled within each group."""
    if x.size == 0 or y.size == 0:
        return np.empty(0)
    return cluster_bootstrap_mean(x, ids_x, n_iter, rng) - cluster_bootstrap_mean(
        y, ids_y, n_iter, rng
    )


# --------------------------------------------------------------------------- placement
def min_spacing(bars: Sequence[int]) -> int:
    """Smallest gap between distinct sorted event bars (at least 1)."""
    s = np.unique(np.asarray(bars, dtype=int))
    return int(max(1, np.diff(s).min())) if s.size > 1 else 1


def random_placement_null(
    g: np.ndarray, first: int, last: int, n: int, signs: Sequence[int], spacing: int,
    n_iter: int, rng: np.random.Generator,
) -> np.ndarray:
    """Null distribution of ``mean(sign * g[bar])`` for ``n`` events placed at random.

    Bars are drawn uniformly (without replacement) from the contiguous range
    ``[first, last]`` subject to pairwise gaps of at least ``spacing`` (exact, via the
    stars-and-bars shift). The observed signs are randomly re-assigned in every draw.

    Raises:
        ValueError: if the events cannot fit in the range with that spacing.
    """
    if n == 0:
        return np.empty(0)
    length = last - first + 1
    m = length - (n - 1) * (spacing - 1)
    if m < n:
        raise ValueError(f"cannot place {n} events with spacing {spacing} in {length} bars")
    sg = np.asarray(signs, dtype=float)
    out = np.empty(n_iter)
    step = max(1, _CHUNK_CELLS // m)
    shift = (spacing - 1) * np.arange(n)
    for lo in range(0, n_iter, step):
        b = min(step, n_iter - lo)
        pick = np.argpartition(rng.random((b, m)), n - 1, axis=1)[:, :n] if n < m else (
            np.tile(np.arange(m), (b, 1))
        )
        pick.sort(axis=1)
        bars = first + pick + shift
        s = rng.permuted(np.tile(sg, (b, 1)), axis=1)
        out[lo : lo + b] = (s * g[bars]).mean(axis=1)
    return out


# --------------------------------------------------------------------------- permutation
def permutation_diff_null(
    x: np.ndarray, y: np.ndarray, n_iter: int, rng: np.random.Generator
) -> np.ndarray:
    """Null of ``mean(x) - mean(y)`` under random reassignment of the group labels."""
    pooled = np.concatenate([x, y])
    nx = x.size
    out = np.empty(n_iter)
    step = max(1, _CHUNK_CELLS // pooled.size)
    for lo in range(0, n_iter, step):
        b = min(step, n_iter - lo)
        perm = np.argsort(rng.random((b, pooled.size)), axis=1)
        vals = pooled[perm]
        out[lo : lo + b] = vals[:, :nx].mean(axis=1) - vals[:, nx:].mean(axis=1)
    return out


def permutation_pvalue(
    x: Sequence[float], y: Sequence[float], n_iter: int, rng: np.random.Generator,
    alternative: Alternative = "greater",
) -> tuple[float, float]:
    """Label-permutation test of ``mean(x) - mean(y)``; returns (observed diff, p)."""
    xa, ya = np.asarray(x, dtype=float), np.asarray(y, dtype=float)
    if xa.size == 0 or ya.size == 0:
        return float("nan"), float("nan")
    obs = float(xa.mean() - ya.mean())
    null = permutation_diff_null(xa, ya, n_iter, rng)
    if alternative == "two-sided":
        return obs, (1 + int(np.sum(np.abs(null) >= abs(obs)))) / (n_iter + 1)
    return obs, one_sided_p(null, obs, alternative)


# --------------------------------------------------------------------------- block bootstrap
def stationary_indices(length: int, block_len: int, n_draws: int, rng: np.random.Generator) -> np.ndarray:
    """Politis-Romano stationary bootstrap index matrix of shape ``(n_draws, length)``.

    Each position starts a new block with probability ``1/block_len`` (mean block length
    ``block_len``); otherwise it continues the previous index (circularly).
    """
    new = rng.random((n_draws, length)) < 1.0 / block_len
    new[:, 0] = True
    starts = rng.integers(0, length, size=(n_draws, length))
    pos = np.arange(length)
    last_new = np.maximum.accumulate(np.where(new, pos, 0), axis=1)
    base = np.take_along_axis(starts, last_new, axis=1)
    return (base + (pos - last_new)) % length


def sharpe(r: np.ndarray, periods: int = 252) -> np.ndarray | float:
    """``mean / std(ddof=1) * sqrt(periods)`` along the last axis (nan if std is 0)."""
    r = np.asarray(r, dtype=float)
    sd = r.std(axis=-1, ddof=1)
    with np.errstate(divide="ignore", invalid="ignore"):
        out = np.where(sd > 0, r.mean(axis=-1) / sd * math.sqrt(periods), np.nan)
    return float(out) if out.ndim == 0 else out


def block_bootstrap_paired(
    a: np.ndarray, b: np.ndarray, block_len: int, n_iter: int, rng: np.random.Generator,
    periods: int = 252,
) -> tuple[np.ndarray, np.ndarray]:
    """Joint stationary bootstrap of aligned series ``a`` (strategy) and ``b`` (benchmark).

    Returns the bootstrap distributions of ``Sharpe(a) - Sharpe(b)`` and of
    ``sum(a) - sum(b)`` (cumulative log-return difference).
    """
    t = a.size
    d_sharpe = np.empty(n_iter)
    d_cum = np.empty(n_iter)
    step = max(1, _CHUNK_CELLS // t)
    for lo in range(0, n_iter, step):
        k = min(step, n_iter - lo)
        idx = stationary_indices(t, block_len, k, rng)
        ra, rb = a[idx], b[idx]
        d_sharpe[lo : lo + k] = sharpe(ra, periods) - sharpe(rb, periods)
        d_cum[lo : lo + k] = ra.sum(axis=1) - rb.sum(axis=1)
    return d_sharpe, d_cum


# --------------------------------------------------------------------------- Holm
def holm_adjust(p_raw: dict[str, float]) -> dict[str, float]:
    """Holm step-down adjusted p-values (monotone, capped at 1).

    Ties keep input order. Missing or NaN p-values must be supplied as 1.0 by the caller
    so that the family size stays fixed.
    """
    items = sorted(p_raw.items(), key=lambda kv: kv[1])
    m = len(items)
    adj: dict[str, float] = {}
    running = 0.0
    for rank, (rule, p) in enumerate(items):
        running = max(running, (m - rank) * p)
        adj[rule] = min(1.0, running)
    return adj


# --------------------------------------------------------------------------- descriptives
def describe(values: Sequence[float | Decimal]) -> dict[str, float]:
    """Count, median and inter-quartile range of ``values`` (``nan`` when empty)."""
    x = to_float_array(values)
    if x.size == 0:
        return {"n": 0, "median": float("nan"), "q1": float("nan"), "q3": float("nan")}
    q1, med, q3 = np.quantile(x, [0.25, 0.5, 0.75])
    return {"n": int(x.size), "median": float(med), "q1": float(q1), "q3": float(q3)}


def decile_counts(values: Sequence[float | Decimal]) -> list[int]:
    """Counts in the ten equal bins of ``[0, 1]`` plus a last entry for values above 1."""
    x = to_float_array(values)
    inside = x[x <= 1.0]
    counts, _ = np.histogram(inside, bins=np.linspace(0.0, 1.0, 11))
    return [*(int(c) for c in counts), int(np.sum(x > 1.0))]
