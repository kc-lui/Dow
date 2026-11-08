"""Regenerate dji_sample.csv: 300 deterministic synthetic yfinance-style daily bars."""
from pathlib import Path

import numpy as np
import pandas as pd


def main() -> None:
    rng = np.random.default_rng(42)
    dates = pd.bdate_range("2020-01-02", periods=300)
    close = 28000 * np.exp(np.cumsum(rng.normal(0.0003, 0.01, len(dates))))
    open_ = np.concatenate([[28000.0], close[:-1]]) * (1 + rng.normal(0, 0.002, len(dates)))
    high = np.maximum(open_, close) * (1 + rng.uniform(0, 0.005, len(dates)))
    low = np.minimum(open_, close) * (1 - rng.uniform(0, 0.005, len(dates)))
    df = pd.DataFrame({
        "Date": dates.strftime("%Y-%m-%d"),
        "Open": open_.round(2), "High": high.round(2), "Low": low.round(2),
        "Close": close.round(2), "Volume": rng.integers(2e8, 5e8, len(dates)),
    })
    df.to_csv(Path(__file__).with_name("dji_sample.csv"), index=False)


if __name__ == "__main__":
    main()
