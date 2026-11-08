"""Regenerate defense_break_sample.csv: deterministic piecewise-linear bars for the trend tests.

Legs (close): 100 -> 120 -> 108 -> 130 -> 100 -> 118 -> 95 -> 105. Each leg is at least 15
sessions and moves more than 8 percent, so every turn is a secondary swing under the default
configuration. The fall from 130 crosses the reaction low 108 before any lower high is confirmed
(DEFENSE_BREAK); the later lower high 118 and the fall under 108 give REVERSAL_DOWN in strict mode.
"""

from pathlib import Path

import numpy as np
import pandas as pd

LEGS = [
    (100.0, 120.0, 20),
    (120.0, 108.0, 18),
    (108.0, 130.0, 22),
    (130.0, 100.0, 30),
    (100.0, 118.0, 20),
    (118.0, 95.0, 25),
    (95.0, 105.0, 15),
]


def main() -> None:
    close = np.concatenate(
        [np.linspace(a, b, n, endpoint=False) for a, b, n in LEGS] + [[LEGS[-1][1]]]
    )
    dates = pd.bdate_range("2021-01-04", periods=len(close))
    open_ = np.concatenate([[close[0]], close[:-1]])
    df = pd.DataFrame(
        {
            "Date": dates.strftime("%Y-%m-%d"),
            "Open": open_.round(4),
            "High": (np.maximum(open_, close) * 1.002).round(4),
            "Low": (np.minimum(open_, close) * 0.998).round(4),
            "Close": close.round(4),
            "Volume": 1_000_000,
        }
    )
    df.to_csv(Path(__file__).with_name("defense_break_sample.csv"), index=False)


if __name__ == "__main__":
    main()
