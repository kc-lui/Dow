from decimal import Decimal

import matplotlib
import numpy as np
import pandas as pd

from dowtheory.chart import DEFENSE_LABEL, chart_filename, render_chart
from dowtheory.schema import AnalysisResult


def _frames():
    idx = pd.bdate_range("2024-01-02", periods=200)
    close = 100 + np.cumsum(np.random.default_rng(1).normal(0.2, 1.0, 200))
    df = pd.DataFrame({"close": close, "volume": np.full(200, 1_000_000)}, index=idx)
    return df, df.assign(close=df["close"] * 0.5)


def _result(df):
    d = lambda i: df.index[i].date()
    p = lambda i: Decimal(str(round(df["close"].iloc[i], 2)))
    sw = lambda i, k, sc: {
        "ts": d(i), "price": p(i), "kind": k, "scale": sc, "confirmed_ts": d(i + 3),
        "amplitude_pct": Decimal("0.1"), "duration_days": 10, "retrace_ratio": None}
    return AnalysisResult(
        meta={"symbol": "^DJI", "pair": "^DJT", "as_of": d(-1), "swing_method": "pct",
              "thresholds": {"minor_pct": 0.03, "secondary_pct": 0.10}},
        trend_state={"primary": "BULL_PRIMARY", "since": d(20), "secondary_direction": "up",
                     "confirmation": {"status": "confirmed", "pair_state": "BULL_PRIMARY",
                                      "detail": ""},
                     "defense_line": {"price": p(100), "ts": d(100), "type": "reaction_low",
                                      "agent_defined": True}},
        swings=[sw(10, "H", "minor"), sw(30, "L", "secondary"), sw(60, "H", "secondary")],
        levels={"support": [{"price": p(30), "zone_low": p(30) - 1, "zone_high": p(30) + 1,
                             "touches": 2}],
                "resistance": [],
                "trendlines": [{"kind": "up", "p0": [d(30), p(30)], "p1": [d(100), p(100)],
                                "slope_per_day": Decimal("0.1"), "touches": 2, "valid": True,
                                "value_at_as_of": p(-1)}]},
        lines=[{"start": d(40), "end": d(80), "band_pct_a": 0.03, "band_pct_b": 0.04,
                "breakout": "up", "breakout_ts": d(81), "confirmed_both": True}],
        signals=[{"ts": d(120), "kind": "REVERSAL_DOWN", "price": p(120), "level": None,
                  "note": "", "agent_defined": False, "confirmation": "pending"},
                 {"ts": d(81), "kind": "LINE_BREAKOUT_UP", "price": p(81), "level": None,
                  "note": "", "agent_defined": False, "confirmation": "confirmed"}],
    )


def test_render_chart_creates_png(tmp_path):
    df, df_pair = _frames()
    result = _result(df)
    path = render_chart(result, df, df_pair, tmp_path)
    assert path.parent == tmp_path and path.name == chart_filename(result)
    assert path.name == f"DJI_DJT_{df.index[-1].date()}_pct0.03.png"
    assert path.stat().st_size > 10_000
    assert matplotlib.get_backend().lower() == "agg"
    assert "agent-defined" in DEFENSE_LABEL


def test_render_chart_without_pair(tmp_path):
    df, _ = _frames()
    result = _result(df)
    result.meta["pair"] = None
    path = render_chart(result, df, None, tmp_path)
    assert path.name.startswith("DJI_2024") and path.stat().st_size > 10_000
