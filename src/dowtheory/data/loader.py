"""Load daily bars (ClickHouse or CSV) as a date-indexed OHLCV frame."""

from __future__ import annotations

from pathlib import Path
from typing import Literal

import pandas as pd

from dowtheory.storage.clickhouse_client import ClickHouseClient

OHLCV = ["open", "high", "low", "close", "volume"]
_DATE_COLUMNS = ("date", "ts_open")


def _load_clickhouse(
    symbol: str, start: str | None, end: str | None, client: ClickHouseClient | None
) -> pd.DataFrame:
    own = client is None
    client = client or ClickHouseClient()
    try:
        sql = (
            "SELECT toDate32(ts_open, 'America/New_York') AS date, open, high, low, close, volume "
            "FROM dow.mkt_klines FINAL WHERE symbol = {symbol:String} AND interval = '1d' "
        )
        params: dict[str, object] = {"symbol": symbol}
        if start:
            sql += "AND toDate32(ts_open, 'America/New_York') >= {start:Date32} "
            params["start"] = pd.Timestamp(start).date()
        if end:
            sql += "AND toDate32(ts_open, 'America/New_York') <= {end:Date32} "
            params["end"] = pd.Timestamp(end).date()
        df = client.query_df(sql + "ORDER BY date", params)
    finally:
        if own:
            client.close()
    return df


def _load_csv(symbol: str, csv_path: str | Path) -> pd.DataFrame:
    df = pd.read_csv(csv_path)
    df.columns = [str(c).strip().lower() for c in df.columns]
    if "symbol" in df.columns:
        df = df[df["symbol"] == symbol]
    date_col = next((c for c in _DATE_COLUMNS if c in df.columns), None)
    if date_col is None:
        raise ValueError(f"{csv_path}: need a 'Date' or 'ts_open' column")
    missing = [c for c in OHLCV if c not in df.columns]
    if missing:
        raise ValueError(f"{csv_path}: missing columns {missing}")
    dates = pd.to_datetime(df[date_col], utc=False, format="mixed")
    if getattr(dates.dt, "tz", None) is not None:
        dates = dates.dt.tz_localize(None)
    out = df[OHLCV].copy()
    out.insert(0, "date", dates.dt.normalize())
    return out


def load_klines(
    symbol: str,
    start: str | None = None,
    end: str | None = None,
    source: Literal["clickhouse", "csv"] = "clickhouse",
    csv_path: str | Path | None = None,
    client: ClickHouseClient | None = None,
) -> pd.DataFrame:
    """Return OHLCV indexed by session date (``date``), float prices, ascending, no duplicates."""
    if source == "clickhouse":
        df = _load_clickhouse(symbol, start, end, client)
    elif source == "csv":
        if csv_path is None:
            raise ValueError("csv_path is required when source='csv'")
        df = _load_csv(symbol, csv_path)
    else:
        raise ValueError(f"Unknown source '{source}'")
    if df.empty:
        raise ValueError(f"No bars for {symbol} from {source}")
    df["date"] = pd.to_datetime(df["date"])
    for col in ("open", "high", "low", "close"):
        df[col] = df[col].astype(float)
    df["volume"] = df["volume"].astype("int64")
    df = df.set_index("date").sort_index()
    df = df[~df.index.duplicated(keep="last")]
    if source == "csv":
        if start:
            df = df[df.index >= pd.Timestamp(start)]
        if end:
            df = df[df.index <= pd.Timestamp(end)]
    return df[OHLCV]


def load_pair(
    a: str, b: str, start: str | None = None, end: str | None = None, **kwargs: object
) -> pd.DataFrame:
    """Inner-join two symbols on date; columns are MultiIndex-free ``<col>_<symbol>``."""
    left = load_klines(a, start, end, **kwargs).add_suffix(f"_{a}")  # type: ignore[arg-type]
    right = load_klines(b, start, end, **kwargs).add_suffix(f"_{b}")  # type: ignore[arg-type]
    return left.join(right, how="inner")
