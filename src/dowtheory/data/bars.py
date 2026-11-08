"""Shared normalisation of vendor OHLCV frames to the ``dow.mkt_klines`` layout."""

from __future__ import annotations

from decimal import Decimal

import pandas as pd

NY_TZ = "America/New_York"
KLINE_COLUMNS = [
    "exchange", "symbol", "interval", "ts_open", "ts_close",
    "open", "high", "low", "close", "volume", "source",
]
PRICE_COLUMNS = ["open", "high", "low", "close"]


def default_exchange(symbol: str) -> str:
    """Fallback exchange label: caret symbols are indices, everything else NYSEARCA."""
    return "INDEX" if symbol.startswith("^") else "NYSEARCA"


def normalize_bars(
    raw: pd.DataFrame, symbol: str, source: str, exchange: str | None = None
) -> pd.DataFrame:
    """Convert a vendor frame (Date index or column; Open/High/Low/Close/Volume) to klines.

    Raises ValueError when ``raw`` is empty or lacks required columns, or when no valid
    row remains after dropping rows with missing prices.
    """
    if raw is None or raw.empty:
        raise ValueError(f"{source}: empty result for {symbol}")
    df = raw.copy()
    if "Date" in df.columns:
        df = df.set_index("Date")
    df.columns = [str(c).strip().lower() for c in df.columns]
    missing = [c for c in [*PRICE_COLUMNS, "volume"] if c not in df.columns]
    if missing:
        raise ValueError(f"{source}: {symbol} missing columns {missing}")

    idx = pd.DatetimeIndex(pd.to_datetime(df.index))
    if idx.tz is not None:
        idx = idx.tz_localize(None)  # keep the exchange-local wall-clock date
    df.index = idx.normalize()
    df = df[~df.index.duplicated(keep="last")].sort_index()
    df = df.dropna(subset=PRICE_COLUMNS)
    if df.empty:
        raise ValueError(f"{source}: no valid rows for {symbol} after dropping NaN prices")

    out = pd.DataFrame(index=df.index)
    out["exchange"] = exchange or default_exchange(symbol)
    out["symbol"] = symbol
    out["interval"] = "1d"
    out["ts_open"] = (df.index + pd.Timedelta(hours=9, minutes=30)).tz_localize(NY_TZ)
    out["ts_close"] = (df.index + pd.Timedelta(hours=16)).tz_localize(NY_TZ)
    for col in PRICE_COLUMNS:
        out[col] = df[col].astype(float).round(4)
    out["volume"] = df["volume"].fillna(0).astype("int64").clip(lower=0).astype("uint64")
    out["source"] = source
    return out.reset_index(drop=True)[KLINE_COLUMNS]


def to_insert_frame(df: pd.DataFrame) -> pd.DataFrame:
    """Return a copy with price columns as ``Decimal`` (exact for Decimal(12,4) columns)."""
    out = df.copy()
    for col in PRICE_COLUMNS:
        out[col] = [Decimal(f"{v:.4f}") for v in out[col]]
    return out
