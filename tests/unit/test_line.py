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
    (ln,) = detect_lines(a, b, band_pct=0.05, min_sessions=15)
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
    assert detect_lines(a, a, min_sessions=15) == []
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


def test_confirmed_ts_is_later_break_and_status_matches_truncation():
    a = _series(_flat_then([110, 112, 114, 116, 118, 120]))
    b = _series(_flat_then([100.5, 100.5, 100.5, 111, 112, 113]))
    (ln,) = detect_lines(a, b)
    assert ln.confirmed_both and ln.confirmed_ts == b.index[23].date()
    assert ln.breakout_ts == a.index[20].date()
    # Truncation invariance: at every t the truncated run agrees with the full-run line.
    for t in range(20, len(a)):
        part = detect_lines(a.iloc[: t + 1], b.iloc[: t + 1])
        assert part, t
        got = part[0]
        if t >= 20:
            assert got.breakout_ts == ln.breakout_ts
        known = ln.confirmed_ts is not None and ln.confirmed_ts <= a.index[t].date()
        assert got.confirmed_both is known
        assert (got.confirmed_ts == ln.confirmed_ts) if known else got.confirmed_ts is None


def test_drift_filter_rejects_trending_window():
    trend = _series(list(np.linspace(100, 108, 30)))  # 15+ sessions in a 5% band, drift > 2.5%
    assert detect_lines(trend, trend) == []
    assert len(detect_lines(trend, trend, max_drift_frac=1.0)) == 1


def test_min_sessions_counts_trading_sessions():
    a = _series([100.0 + (i % 2) for i in range(14)] + [130.0])
    assert detect_lines(a, a, min_sessions=15) == []
    assert len(detect_lines(a, a, min_sessions=14)) == 1
