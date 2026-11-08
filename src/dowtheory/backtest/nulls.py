"""Simulated nulls: drift-matched random walk (R1) and random spells (R8)."""

from __future__ import annotations

from collections.abc import Sequence
from concurrent.futures import ProcessPoolExecutor

import numpy as np
import pandas as pd

from dowtheory.backtest.events import r1_events
from dowtheory.backtest.stats import sharpe, stationary_indices
from dowtheory.config import DowConfig
from dowtheory.swings import detect_multiscale
from dowtheory.trend import run_trend

_SimArgs = tuple[Sequence[int], np.ndarray, np.ndarray, DowConfig, str, int, int]


def _sim_chunk(args: _SimArgs) -> list[float]:
    ids, close, index_ns, cfg, symbol, seed, block = args
    index = pd.DatetimeIndex(index_ns)
    log_ret = np.diff(np.log(close))
    out: list[float] = []
    for i in ids:
        rng = np.random.default_rng(np.random.SeedSequence(seed, spawn_key=(int(i),)))
        pick = stationary_indices(log_ret.size, block, 1, rng)[0]
        path = close[0] * np.exp(np.concatenate([[0.0], np.cumsum(log_ret[pick])]))
        series = pd.Series(path, index=index)
        secondary = detect_multiscale(series, cfg, symbol=symbol)["secondary"]
        _final, _signals, snaps = run_trend(series, secondary, cfg)
        ev = [e for e in r1_events(secondary, snaps, index, cfg.trend.equal_extreme_tol)
              if e.outcome is not None]
        out.append(sum(e.outcome == "extend" for e in ev) / len(ev) if ev else float("nan"))
    return out


def simulate_p_extend(
    close: np.ndarray, index: pd.DatetimeIndex, cfg: DowConfig, symbol: str, *, seed: int,
    n_sim: int, block_len: int, workers: int = 1,
) -> np.ndarray:
    """``p_extend`` on ``n_sim`` drift-matched block-bootstrap price paths (R1 robustness).

    Each path resamples the daily log returns in stationary blocks (drift is preserved in
    expectation), is rebuilt into prices and passed through the identical
    ``detect_multiscale`` + ``run_trend`` + event definition. Simulation ``i`` uses the
    generator ``SeedSequence(seed, spawn_key=(i,))``, so the result does not depend on
    ``workers``. Paths without any event give ``nan`` (dropped by the caller).
    """
    ns = index.to_numpy()
    chunks = [list(range(lo, min(lo + 25, n_sim))) for lo in range(0, n_sim, 25)]
    jobs: list[_SimArgs] = [(c, close, ns, cfg, symbol, seed, block_len) for c in chunks]
    if workers > 1:
        with ProcessPoolExecutor(max_workers=workers) as pool:
            parts = list(pool.map(_sim_chunk, jobs))
    else:
        parts = [_sim_chunk(j) for j in jobs]
    return np.array([x for part in parts for x in part], dtype=float)


def spell_null_delta_sharpe(
    r: np.ndarray, executed: np.ndarray, kappa: float, n_iter: int, rng: np.random.Generator
) -> np.ndarray:
    """``Sharpe(strategy) - Sharpe(buy-and-hold)`` with the executed position spells shuffled.

    ``executed`` is the position series applied to ``r`` (already lagged). Spell lengths and
    values are kept; only their order is permuted. Costs are recomputed on every draw.
    """
    change = np.flatnonzero(np.diff(executed) != 0) + 1
    starts = np.concatenate([[0], change])
    lens = np.diff(np.concatenate([starts, [executed.size]]))
    vals = executed[starts]
    base = sharpe(r)
    out = np.empty(n_iter)
    for i in range(n_iter):
        perm = rng.permutation(vals.size)
        e = np.repeat(vals[perm], lens[perm])
        prev = np.concatenate([[0.0], e[:-1]])
        out[i] = sharpe(e * r - kappa * np.abs(e - prev)) - base
    return out
