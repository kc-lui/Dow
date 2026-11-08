"""Swing detection: exact sets, alternation, truncation invariance, nesting, fixture smoke."""

from __future__ import annotations

import itertools
from decimal import Decimal
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from dowtheory.config import DowConfig
from dowtheory.data.loader import load_klines
from dowtheory.swings import (
    Swing,
    compute_secondary_metrics,
    detect_multiscale,
    detect_swings,
    nest_scales,
    swings_as_of,
    to_price,
)

FIXTURE = Path(__file__).resolve().parents[1] / "fixtures" / "dji_sample.csv"
METHODS = ("pct", "atr", "pivot")


def _sawtooth(waypoints: list[float], leg: int = 4) -> pd.Series:
    """Linear legs of ``leg`` bars between waypoints, on business days."""
    values = [float(waypoints[0])]
    for a, b in itertools.pairwise(waypoints):
        values += list(np.linspace(a, b, leg + 1)[1:])
    idx = pd.bdate_range("2021-01-04", periods=len(values))
    return pd.Series(values, index=idx)


def _walk(seed: int, n: int = 500, vol: float = 0.012) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    close = 100 * np.exp(np.cumsum(rng.normal(0, vol, n)))
    spread = np.abs(rng.normal(0, 0.004, n)) * close
    idx = pd.bdate_range("2019-01-02", periods=n)
    return pd.DataFrame({"close": close, "high": close + spread, "low": close - spread}, index=idx)


def _detect(df: pd.DataFrame, method: str, **kw: object) -> list[Swing]:
    return detect_swings(
        df["close"], method=method, high=df["high"], low=df["low"],  # type: ignore[arg-type]
        threshold=0.03, atr_mult=2.0, atr_window=14, pivot_n=4, **kw,  # type: ignore[arg-type]
    )


def test_to_price_quantises_floats() -> None:
    assert to_price(28093.88) == Decimal("28093.8800")
    assert to_price(0.1 + 0.2) == Decimal("0.3000")


def test_pct_sawtooth_exact_swings() -> None:
    close = _sawtooth([100, 120, 104, 128, 108, 140])
    got = [(s.idx, s.kind, s.price, s.confirmed_idx) for s in detect_swings(close, threshold=0.03)]
    assert got == [
        (0, "L", Decimal("100.0000"), 1),
        (4, "H", Decimal("120.0000"), 5),
        (8, "L", Decimal("104.0000"), 9),
        (12, "H", Decimal("128.0000"), 13),
        (16, "L", Decimal("108.0000"), 17),
    ]


def test_pct_swing_fields() -> None:
    close = _sawtooth([100, 120, 104, 128, 108, 140])
    sw = detect_swings(close, threshold=0.03)
    assert sw[0].amplitude_pct == 0 and sw[0].duration_days == 0
    assert sw[1].amplitude_pct == Decimal("0.200000")
    assert sw[1].duration_days == (sw[1].ts - sw[0].ts).days > 0
    assert all(s.confirmed_idx >= s.idx and s.confirmed_ts >= s.ts for s in sw)
    assert all(s.scale == "minor" and s.retrace_ratio is None for s in sw)


def test_pivot_sawtooth_exact_swings() -> None:
    close = _sawtooth([100, 120, 104, 128, 108, 140])
    sw = detect_swings(close, method="pivot", pivot_n=2)
    assert [(s.idx, s.kind, s.confirmed_idx) for s in sw] == [
        (4, "H", 6),
        (8, "L", 10),
        (12, "H", 14),
        (16, "L", 18),
    ]


def test_pivot_same_kind_run_gets_dip_inserted_and_stays_alternating() -> None:
    # Two highs separated by a dip whose left window is lower than the dip: no L pivot.
    values = [100, 99, 98, 97, 110, 104, 105, 106, 107, 108, 109, 112, 111, 110, 109]
    close = pd.Series(values, index=pd.bdate_range("2021-01-04", periods=len(values)), dtype=float)
    sw = detect_swings(close, method="pivot", pivot_n=3)
    kinds = [s.kind for s in sw]
    assert all(a != b for a, b in itertools.pairwise(kinds))
    assert [(s.idx, s.kind) for s in sw if s.kind == "H"] == [(4, "H"), (11, "H")]


def test_flat_series_has_no_swings() -> None:
    close = pd.Series(100.0, index=pd.bdate_range("2021-01-04", periods=40))
    for method in METHODS:
        assert detect_swings(close, method=method, pivot_n=3) == []


def test_invalid_inputs_raise() -> None:
    close = _sawtooth([100, 120])
    with pytest.raises(ValueError, match="Unknown swing method"):
        detect_swings(close, method="nope")  # type: ignore[arg-type]
    with pytest.raises(ValueError, match="threshold"):
        detect_swings(close, threshold=0)
    with pytest.raises(ValueError, match="NaN"):
        detect_swings(close.where(close.index != close.index[2]))
    with pytest.raises(ValueError, match="same length"):
        detect_swings(close, method="atr", high=close.iloc[:-1], low=close.iloc[:-1])


@pytest.mark.parametrize("method", METHODS)
@pytest.mark.parametrize("seed", [1, 2, 3, 4])
def test_alternation_and_ordering_on_random_walk(method: str, seed: int) -> None:
    sw = _detect(_walk(seed), method)
    assert len(sw) > 3
    assert all(a.kind != b.kind for a, b in itertools.pairwise(sw))
    assert all(a.idx < b.idx for a, b in itertools.pairwise(sw))
    assert all(a.confirmed_idx <= b.confirmed_idx for a, b in itertools.pairwise(sw))
    assert all(s.confirmed_idx >= s.idx for s in sw)


@pytest.mark.parametrize("method", METHODS)
@pytest.mark.parametrize("seed", [11, 12, 13])
def test_truncation_invariance_no_lookahead(method: str, seed: int) -> None:
    df = _walk(seed, n=360)
    full = _detect(df, method)
    for t in list(range(5, 360, 7)) + [359]:
        part = _detect(df.iloc[: t + 1], method)
        assert swings_as_of(part, t) == swings_as_of(full, t), f"{method} t={t}"


def test_swings_as_of_filters_on_confirmation() -> None:
    sw = detect_swings(_sawtooth([100, 120, 104, 128, 108, 140]), threshold=0.03)
    assert swings_as_of(sw, 0) == []
    assert [s.idx for s in swings_as_of(sw, 9)] == [0, 4, 8]


def _mk(idx: int, kind: str, price: str, conf: int) -> Swing:
    day = pd.Timestamp("2021-01-01") + pd.Timedelta(days=idx)
    cday = pd.Timestamp("2021-01-01") + pd.Timedelta(days=conf)
    return Swing(idx, day.date(), Decimal(price), kind, conf, cday.date(), "minor",  # type: ignore[arg-type]
                 Decimal(0), 0, None)


def test_nest_scales_snaps_within_two_bars_and_flags_orphans() -> None:
    minor = [_mk(10, "H", "120", 14), _mk(20, "L", "100", 24)]
    secondary = [_mk(12, "H", "121", 13), _mk(40, "L", "90", 45), _mk(21, "H", "119", 30)]
    nested, flags = nest_scales(minor, secondary)
    assert nested[0].idx == 10 and nested[0].price == Decimal(120)
    assert nested[0].confirmed_idx == 14  # later of the two confirmations
    assert flags[10] is True
    assert nested[1].idx == 40 and flags[40] is False  # no minor swing nearby
    assert nested[2].idx == 21 and flags[21] is False  # wrong kind: not snapped


def test_compute_secondary_metrics_retrace_and_duration() -> None:
    chain = [_mk(0, "L", "100", 1), _mk(30, "H", "150", 31), _mk(50, "L", "125", 51),
             _mk(80, "H", "160", 81)]
    out = compute_secondary_metrics(chain)
    assert [s.retrace_ratio for s in out] == [None, None, Decimal("0.500000"), Decimal("1.400000")]
    assert [s.duration_days for s in out] == [0, 30, 20, 30]
    assert out[1].amplitude_pct == Decimal("0.500000")


@pytest.mark.parametrize("method", METHODS)
def test_multiscale_nesting_on_random_walk(method: str) -> None:
    from dataclasses import replace

    cfg = DowConfig(swings=replace(DowConfig().swings, method=method, pivot_n=3))
    df = _walk(7, n=900, vol=0.015)
    res = detect_multiscale(df["close"], cfg, high=df["high"], low=df["low"])
    minor, secondary = res["minor"], res["secondary"]
    assert set(res) == {"minor", "secondary"} and secondary
    assert all(s.scale == "secondary" for s in secondary)
    assert all(s.scale == "minor" for s in minor)
    assert all(s.confirmed_idx >= s.idx for s in secondary)
    assert all(a.kind != b.kind for a, b in itertools.pairwise(secondary))
    assert secondary[0].retrace_ratio is None


def test_multiscale_snapped_secondary_shares_a_minor_bar() -> None:
    df = _walk(5, n=900, vol=0.015)
    res = detect_multiscale(df["close"], DowConfig())
    minor_bars = {(m.idx, m.kind) for m in res["minor"]}
    shared = [(s.idx, s.kind) in minor_bars for s in res["secondary"]]
    assert shared and sum(shared) >= 0.8 * len(shared)


def test_dji_fixture_smoke(capsys: pytest.CaptureFixture[str]) -> None:
    df = load_klines("^DJI", source="csv", csv_path=FIXTURE)
    for method in METHODS:
        from dataclasses import replace

        cfg = DowConfig(swings=replace(DowConfig().swings, method=method, pivot_n=3))
        res = detect_multiscale(df["close"], cfg, high=df["high"], low=df["low"])
        print(f"{method}: minor={len(res['minor'])} secondary={len(res['secondary'])}")
        assert len(res["minor"]) > 0
        assert len(res["secondary"]) > 0
    assert "pct: minor=" in capsys.readouterr().out
