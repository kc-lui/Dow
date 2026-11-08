"""Orchestration: load bars, detect swings, classify the trend, assemble the result."""

from __future__ import annotations

import dataclasses
import datetime as dt
import uuid
from collections.abc import Sequence
from decimal import Decimal
from pathlib import Path
from typing import Any

import pandas as pd

from dowtheory.config import DowConfig, load_config
from dowtheory.confirmation import (
    ConfirmationResult,
    pair_confirm,
    signal_confirmed,
    volume_confirms,
)
from dowtheory.data.loader import load_klines
from dowtheory.levels import (
    Level,
    TrendLine,
    cluster_levels,
    defense_line_from_state,
    fit_trendlines,
)
from dowtheory.line import LineRange, detect_lines
from dowtheory.schema import AnalysisResult
from dowtheory.storage.clickhouse_client import ClickHouseClient

_CONFIRMABLE = {"REVERSAL_UP", "REVERSAL_DOWN", "LINE_BREAKOUT_UP", "LINE_BREAKOUT_DOWN"}


def _dec(value: float | str | Decimal) -> Decimal:
    return value if isinstance(value, Decimal) else Decimal(str(value))


def _atr(df: pd.DataFrame, window: int) -> float:
    """Simple average true range over the last ``window`` bars."""
    prev = df["close"].shift(1)
    tr = pd.concat(
        [df["high"] - df["low"], (df["high"] - prev).abs(), (df["low"] - prev).abs()], axis=1
    ).max(axis=1)
    return float(tr.tail(window).mean())


def _swing_dict(s: Any) -> dict[str, Any]:
    return {
        "ts": s.ts, "price": s.price, "kind": s.kind, "scale": s.scale,
        "confirmed_ts": s.confirmed_ts, "amplitude_pct": s.amplitude_pct,
        "duration_days": s.duration_days, "retrace_ratio": s.retrace_ratio,
    }


def _level_dict(lv: Level) -> dict[str, Any]:
    return {
        "price": lv.price, "zone_low": lv.zone_low, "zone_high": lv.zone_high,
        "touches": lv.touches,
    }


def _trendline_dict(tl: TrendLine, as_of: dt.date) -> dict[str, Any]:
    return {
        "kind": tl.kind, "p0": [tl.p0[0], tl.p0[1]], "p1": [tl.p1[0], tl.p1[1]],
        "slope_per_day": tl.slope_per_day, "touches": tl.touches, "valid": tl.valid,
        "value_at_as_of": tl.value_at(as_of),
    }


def _line_dict(ln: LineRange) -> dict[str, Any]:
    return {
        "start": ln.start, "end": ln.end, "band_pct_a": ln.band_pct_a,
        "band_pct_b": ln.band_pct_b, "breakout": ln.breakout,
        "breakout_ts": ln.breakout_ts, "confirmed_both": ln.confirmed_both,
    }


def _signal_dict(sig: Any, others: Sequence[Any], max_days: int | None, has_pair: bool) -> dict:
    if sig.kind in _CONFIRMABLE and has_pair:
        confirmation = "confirmed" if signal_confirmed(sig, others, max_days) else "pending"
    else:
        confirmation = "not_applicable"
    return {
        "ts": sig.ts, "kind": sig.kind, "price": sig.price, "level": sig.level,
        "note": sig.note, "agent_defined": sig.agent_defined, "confirmation": confirmation,
    }


def _line_signals(lines: Sequence[LineRange], close: pd.Series) -> list[dict[str, Any]]:
    out = []
    for ln in lines:
        if ln.breakout == "none" or ln.breakout_ts is None:
            continue
        out.append({
            "ts": ln.breakout_ts,
            "kind": "LINE_BREAKOUT_UP" if ln.breakout == "up" else "LINE_BREAKOUT_DOWN",
            "price": _dec(close.loc[pd.Timestamp(ln.breakout_ts)]),
            "level": None,
            "note": f"line {ln.start}..{ln.end} broken {ln.breakout}",
            "agent_defined": False,
            "confirmation": "confirmed" if ln.confirmed_both else "pending",
        })
    return out


def _with_method(cfg: DowConfig, method: str | None) -> DowConfig:
    if method is None or method == cfg.swings.method:
        return cfg
    return dataclasses.replace(cfg, swings=dataclasses.replace(cfg.swings, method=method))


def _load(
    symbol: str, end: str | None, start: str | None, source: str,
    csv_path: str | Path | None, client: ClickHouseClient | None,
) -> pd.DataFrame:
    return load_klines(symbol, start, end, source=source, csv_path=csv_path, client=client)  # type: ignore[arg-type]


def analyze(
    symbol: str,
    pair: str | None = None,
    as_of: str | dt.date | None = None,
    start: str | None = None,
    source: str = "clickhouse",
    csv_path: str | Path | None = None,
    csv_pair_path: str | Path | None = None,
    method: str | None = None,
    cfg: DowConfig | None = None,
    client: ClickHouseClient | None = None,
) -> tuple[AnalysisResult, pd.DataFrame, pd.DataFrame | None]:
    """Run the full Dow analysis for ``symbol`` (and ``pair`` for confirmation).

    Bars are cut at ``as_of`` (default: last common session) and the two frames are
    inner-joined on date so every bar index refers to the same session in both. Returns the
    result plus the (aligned) frames used, for charting.
    """
    from dowtheory.swings import detect_multiscale, swings_as_of
    from dowtheory.trend import run_trend

    cfg = _with_method(cfg or load_config(), method)
    end = pd.Timestamp(as_of).date().isoformat() if as_of is not None else None
    df = _load(symbol, end, start, source, csv_path, client)
    df_pair: pd.DataFrame | None = None
    if pair:
        df_pair = _load(pair, end, start, source, csv_pair_path or csv_path, client)
        common = df.index.intersection(df_pair.index)
        if common.empty:
            raise ValueError(f"No common sessions for {symbol} and {pair}")
        df, df_pair = df.loc[common], df_pair.loc[common]
    last = len(df) - 1
    as_of_date = df.index[last].date()
    close = df["close"]

    scales = detect_multiscale(close, cfg, df["high"], df["low"])
    secondary = swings_as_of(scales.get("secondary", []), last)
    state, signals, _ = run_trend(close, secondary, cfg)

    signals_b: list[Any] = []
    state_b = None
    if df_pair is not None:
        scales_b = detect_multiscale(df_pair["close"], cfg, df_pair["high"], df_pair["low"])
        sec_b = swings_as_of(scales_b.get("secondary", []), last)
        state_b, signals_b, _ = run_trend(df_pair["close"], sec_b, cfg)

    max_days = cfg.confirmation.max_days
    lines: list[LineRange] = []
    if df_pair is not None:
        lines = detect_lines(
            close, df_pair["close"], cfg.line.band_pct, cfg.line.min_days, last, max_days
        )
        confirmation = pair_confirm(state, state_b, signals, signals_b, max_days)
    else:
        confirmation = ConfirmationResult("pending", None, "no pair supplied")

    minor = swings_as_of(scales.get("minor", []), last)
    atr = _atr(df, cfg.swings.atr_window) if cfg.levels.tol_mode == "atr" else None
    ref = _dec(close.iloc[last])
    level_kwargs = {
        "tol_mode": cfg.levels.tol_mode, "tol_pct": cfg.levels.tol_pct,
        "tol_atr_mult": cfg.levels.tol_atr_mult, "atr": atr, "min_touches": cfg.levels.min_touches,
        "max_levels": cfg.levels.max_levels, "ref_price": ref,
    }
    support = cluster_levels(minor, "L", **level_kwargs)  # type: ignore[arg-type]
    resistance = cluster_levels(minor, "H", **level_kwargs)  # type: ignore[arg-type]
    trendlines = [
        tl
        for kind in ("up", "down")
        for tl in fit_trendlines(secondary, kind, close, cfg.levels.trendline_tol_pct)  # type: ignore[arg-type]
    ]

    all_signals = [_signal_dict(s, signals_b, max_days, df_pair is not None) for s in signals]
    all_signals += _line_signals(lines, close)
    all_signals.sort(key=lambda s: s["ts"])

    all_swings = sorted(
        (s for scale in ("minor", "secondary", "primary") for s in
         swings_as_of(scales.get(scale, []), last)),
        key=lambda s: (s.ts, s.scale),
    )
    result = AnalysisResult(
        meta={
            "symbol": symbol, "pair": pair, "as_of": as_of_date,
            "config_hash": cfg.config_hash(), "swing_method": cfg.swings.method,
            "thresholds": {
                "minor_pct": cfg.swings.minor_pct, "secondary_pct": cfg.swings.secondary_pct,
            },
            "run_id": uuid.uuid4().hex,
        },
        trend_state={
            "primary": state.state,
            "since": state.since,
            "secondary_direction": state.secondary_direction,
            "confirmation": {
                "pair_state": confirmation.pair_state,
                "status": confirmation.status,
                "detail": confirmation.detail,
            },
            "defense_line": defense_line_from_state(state),
            "volume_confirms": volume_confirms(df, secondary),
        },
        swings=[_swing_dict(s) for s in all_swings],
        levels={
            "support": [_level_dict(x) for x in support],
            "resistance": [_level_dict(x) for x in resistance],
            "trendlines": [_trendline_dict(t, as_of_date) for t in trendlines],
        },
        lines=[_line_dict(x) for x in lines],
        signals=all_signals,
    )
    return result, df, df_pair
