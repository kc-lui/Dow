from pathlib import Path

import pandas as pd
import pytest

from dowtheory.data.loader import load_klines, load_pair

FIXTURE = Path(__file__).parent.parent / "fixtures" / "dji_sample.csv"


def test_yfinance_style_csv():
    df = load_klines("^DJI", source="csv", csv_path=FIXTURE)
    assert len(df) == 300
    assert list(df.columns) == ["open", "high", "low", "close", "volume"]
    assert df.index.is_monotonic_increasing and df.index.name == "date"
    assert (df["high"] >= df[["open", "close"]].max(axis=1)).all()


def test_date_range():
    df = load_klines("^DJI", "2020-02-01", "2020-02-29", source="csv", csv_path=FIXTURE)
    assert df.index.min() >= pd.Timestamp("2020-02-01") and df.index.max() <= pd.Timestamp("2020-02-29")


def test_klines_layout_csv(tmp_path):
    p = tmp_path / "k.csv"
    p.write_text(
        "exchange,symbol,interval,ts_open,ts_close,open,high,low,close,volume,source\n"
        "INDEX,^DJI,1d,2024-03-08 09:30:00-05:00,2024-03-08 16:00:00-05:00,1,2,0.5,1.5,10,csv\n"
        "INDEX,^DJT,1d,2024-03-08 09:30:00-05:00,2024-03-08 16:00:00-05:00,9,9,9,9,10,csv\n")
    df = load_klines("^DJI", source="csv", csv_path=p)
    assert len(df) == 1 and df["open"].iloc[0] == 1.0
    assert df.index[0] == pd.Timestamp("2024-03-08")


def test_pair_inner_join():
    pair = load_pair("^DJI", "^DJT", source="csv", csv_path=FIXTURE)  # no symbol column: same data
    assert "close_^DJI" in pair.columns and "close_^DJT" in pair.columns and len(pair) == 300


def test_errors(tmp_path):
    with pytest.raises(ValueError):
        load_klines("^DJI", source="csv")
    bad = tmp_path / "b.csv"
    bad.write_text("Date,Open\n2024-01-01,1\n")
    with pytest.raises(ValueError):
        load_klines("^DJI", source="csv", csv_path=bad)
