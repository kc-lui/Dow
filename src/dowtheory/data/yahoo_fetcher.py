"""Fetch daily OHLCV for indices and ETFs from Yahoo Finance (unadjusted)."""

from __future__ import annotations

import logging

import pandas as pd
import yfinance as yf

from dowtheory.data.bars import normalize_bars

logger = logging.getLogger(__name__)
SOURCE = "yfinance"


def fetch_daily(
    symbol: str,
    start: str | None = None,
    end: str | None = None,
    exchange: str | None = None,
) -> pd.DataFrame:
    """Return daily bars in the ``mkt_klines`` layout. Raises ValueError on empty results.

    ``ts_open`` is the session date at 09:30 and ``ts_close`` 16:00, America/New_York.
    Prices are unadjusted (``auto_adjust=False``) and rounded to 4 decimals.
    """
    kwargs: dict[str, str] = {}
    if start:
        kwargs["start"] = start
    if end:
        kwargs["end"] = end
    if not kwargs:
        kwargs["period"] = "max"
    raw = yf.Ticker(symbol).history(interval="1d", auto_adjust=False, actions=False, **kwargs)
    bars = normalize_bars(raw.reset_index(), symbol, SOURCE, exchange)
    logger.info("yfinance %s: %d bars", symbol, len(bars))
    return bars
