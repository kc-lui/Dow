import numpy as np
import pandas as pd
import pytest

from dowtheory.data import yahoo_fetcher
from dowtheory.data.bars import KLINE_COLUMNS, normalize_bars, to_insert_frame


def _raw(tz="America/New_York"):
    idx = pd.DatetimeIndex(["2024-03-08", "2024-03-11"], tz=tz, name="Date")
    return pd.DataFrame(
        {"Open": [1.00004, 2.0], "High": [2.0, 3.0], "Low": [0.5, 1.5],
         "Close": [1.5, 2.5], "Volume": [np.nan, 100]}, index=idx)


def test_schema_and_times():
    out = normalize_bars(_raw().reset_index(), "^DJI", "yfinance", "INDEX")
    assert list(out.columns) == KLINE_COLUMNS
    assert str(out["ts_open"].iloc[0]) == "2024-03-08 09:30:00-05:00"
    assert str(out["ts_open"].iloc[1]) == "2024-03-11 09:30:00-04:00"  # DST starts 03-10
    assert str(out["ts_close"].iloc[1]) == "2024-03-11 16:00:00-04:00"
    assert out["open"].iloc[0] == 1.0
    assert out["volume"].tolist() == [0, 100]
    assert set(out["interval"]) == {"1d"}


def test_decimal_frame():
    dec = to_insert_frame(normalize_bars(_raw().reset_index(), "SPY", "yfinance"))
    assert str(dec["open"].iloc[0]) == "1.0000"
    assert dec["exchange"].iloc[0] == "NYSEARCA"


def test_empty_raises():
    with pytest.raises(ValueError):
        normalize_bars(pd.DataFrame(), "^DJI", "yfinance")


def test_fetch_daily_uses_unadjusted(monkeypatch):
    seen = {}

    class FakeTicker:
        def __init__(self, symbol):
            pass

        def history(self, **kwargs):
            seen.update(kwargs)
            return _raw()

    monkeypatch.setattr(yahoo_fetcher.yf, "Ticker", FakeTicker)
    out = yahoo_fetcher.fetch_daily("^DJI")
    assert seen["auto_adjust"] is False
    assert len(out) == 2 and out["source"].iloc[0] == "yfinance"
