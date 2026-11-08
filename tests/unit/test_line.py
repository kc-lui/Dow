import numpy as np
import pandas as pd
import pytest

from dowtheory.line import detect_lines


def _series(values):
    idx = pd.bdate_range("2024-01-02", periods=len(values))
    return pd.Series(values, index=idx, dtype=float)


def _flat_then(after, n=20):
    return [100.0 + (i % 2) for i in range(n)] + after


def test_flat_window_detected_with_confirmed_upward_breakout():
    a = _series(_flat_then([110, 112, 114]))
    b = _series(_flat_then([111, 113, 115]))
    (ln,) = detect_lines(a, b, band_pct=0.05, min_days=14)
    assert ln.breakout == "up" and ln.confirmed_both
    assert ln.breakout_ts == a.index[20].date()
    assert ln.band_pct_a <= 0.05 and ln.band_pct_b <= 0.05


def test_non_confirmed_when_other_series_breaks_opposite():
    a = _series(_flat_then([110, 112]))
    b = _series(_flat_then([90, 88]))
    (ln,) = detect_lines(a, b)
    assert ln.breakout == "up" and not ln.confirmed_both


def test_max_days_limits_confirmation():
    a = _series(_flat_then([110, 111, 112, 113, 114, 115]))
    b = _series(_flat_then([100.5, 100.5, 100.5, 100.5, 100.5, 120]))
    assert detect_lines(a, b, max_days=None)[0].confirmed_both
    assert not detect_lines(a, b, max_days=3)[0].confirmed_both


def test_too_short_or_too_wide_is_not_a_line():
    a = _series([100, 101, 100, 101, 130, 131])
    assert detect_lines(a, a, min_days=14) == []
    wide = _series(list(np.linspace(100, 150, 40)))
    assert detect_lines(wide, wide) == []


def test_as_of_idx_hides_future_breakout():
    a = _series(_flat_then([110, 112, 114]))
    (ln,) = detect_lines(a, a, as_of_idx=19)
    assert ln.breakout == "none" and ln.breakout_ts is None and not ln.confirmed_both


def test_misaligned_series_rejected():
    a = _series([1.0, 2.0, 3.0])
    with pytest.raises(ValueError):
        detect_lines(a, a.iloc[:2])
