"""Regenerate pair_a_sample.csv / pair_b_sample.csv: two synthetic legs for the confirmation tests.

Both legs share three steep moves (100 -> 124 -> 106 -> 122, each >= 13 sessions at about 1.2
points per session, so every turn is a secondary swing and no 15-session window stays within 5
percent) and then jump to a flat shelf at 131 (+/- 0.3): leg A holds it for 20 sessions, leg B for
23. That shelf is the one Dow line (both legs within 5 percent over the same 20 sessions, net
drift about zero). Each leg then jumps to 142 and climbs to 160: A breaks out first
(LINE_BREAKOUT_UP), B three sessions later, so ``confirmed_ts`` is B's break date and
``confirmed_both`` flips only once B has broken out. Afterwards the legs diverge: A keeps making
higher highs and higher lows (BULL_PRIMARY); B falls through its reaction low 106, makes a lower
high at 118 and falls again (DEFENSE_BREAK, LH, REVERSAL_DOWN -> BEAR_PRIMARY), which gives a
state-level ``non_confirmation`` and one unmatched B reversal. Volume is 2e6 on rising bars and
1e6 on falling bars. Slopes stay at or above 1.2 points per session so that no V-shaped turn
forms a second line.
"""

import argparse
from pathlib import Path

import numpy as np
import pandas as pd

SHARED = [(100.0, 124.0, 20), (124.0, 106.0, 15), (106.0, 122.0, 13)]
LEGS_A = [
    *SHARED,
    ("flat", 131.0, 20),
    (142.0, 160.0, 15),
    (160.0, 142.0, 15),
    (142.0, 165.0, 19),
    (165.0, 146.0, 16),
    (146.0, 170.0, 20),
]
LEGS_B = [
    *SHARED,
    ("flat", 131.0, 23),
    (142.0, 160.0, 15),
    (160.0, 100.0, 30),
    (100.0, 118.0, 15),
    (118.0, 92.0, 22),
]


def _closes(legs: list[tuple]) -> np.ndarray:
    parts = []
    for a, b, n in legs:
        if a == "flat":
            parts.append(b + 0.3 * np.where(np.arange(n) % 2 == 0, 1.0, -1.0))
        else:
            parts.append(np.linspace(a, b, n, endpoint=False))
    return np.concatenate(parts + [[legs[-1][1]]])


def _frame(close: np.ndarray) -> pd.DataFrame:
    dates = pd.bdate_range("2021-01-04", periods=len(close))
    open_ = np.concatenate([[close[0]], close[:-1]])
    return pd.DataFrame(
        {
            "Date": dates.strftime("%Y-%m-%d"),
            "Open": open_.round(4),
            "High": (np.maximum(open_, close) * 1.002).round(4),
            "Low": (np.minimum(open_, close) * 0.998).round(4),
            "Close": close.round(4),
            "Volume": np.where(close >= open_, 2_000_000, 1_000_000),
        }
    )


def main(argv: list[str] | None = None) -> int:
    """Write both CSVs in place; with ``--check`` only compare them to the generated frames."""
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--check", action="store_true", help="exit 1 if the CSVs on disk differ")
    check = ap.parse_args(argv).check
    a, b = _closes(LEGS_A), _closes(LEGS_B)
    assert len(a) == len(b), (len(a), len(b))
    here = Path(__file__).parent
    stale = 0
    for name, close in (("pair_a_sample.csv", a), ("pair_b_sample.csv", b)):
        path, text = here / name, _frame(close).to_csv(index=False)
        if check:
            stale += int(not path.is_file() or path.read_text() != text)
        else:
            path.write_text(text)
    return 1 if stale else 0


if __name__ == "__main__":
    raise SystemExit(main())
