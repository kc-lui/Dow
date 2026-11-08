import datetime as dt
from decimal import Decimal
from types import SimpleNamespace

import pandas as pd
import pytest

from dowtheory.levels import cluster_levels, defense_line_from_state, fit_trendlines


def test_cluster_groups_close_prices_and_drops_singletons(make_swing):
    swings = [make_swing(1, 100, "H"), make_swing(10, 100.5, "H"), make_swing(20, 120, "H"),
              make_swing(30, 80, "L")]
    levels = cluster_levels(swings, "H")
    assert len(levels) == 1
    lv = levels[0]
    assert lv.touches == 2 and Decimal(100) <= lv.price <= Decimal("100.5")
    assert lv.zone_low <= lv.price <= lv.zone_high
    assert len(lv.members) == 2


def test_cluster_kind_filter_and_alias(make_swing):
    swings = [make_swing(1, 50, "L"), make_swing(5, 50.1, "L"), make_swing(9, 50, "H")]
    assert len(cluster_levels(swings, "support")) == 1
    assert cluster_levels(swings, "resistance") == []
    with pytest.raises(ValueError):
        cluster_levels(swings, "X")


def test_cluster_max_levels_prefers_ref_price(make_swing):
    swings = [make_swing(i, p, "L") for i, p in enumerate([10, 10, 50, 50, 90, 90])]
    levels = cluster_levels(swings, "L", max_levels=1, ref_price=88)
    assert len(levels) == 1 and levels[0].price == Decimal(90)


def test_cluster_atr_mode(make_swing):
    swings = [make_swing(1, 100, "H"), make_swing(5, 103, "H")]
    assert cluster_levels(swings, "H", tol_mode="pct") == []
    assert len(cluster_levels(swings, "H", tol_mode="atr", tol_atr_mult=0.5, atr=8)) == 1


def _closes(values):
    idx = pd.date_range("2024-01-01", periods=len(values), freq="D")
    return pd.Series(values, index=idx, dtype=float)


def test_uptrend_line_valid_and_value_at(make_swing):
    swings = [make_swing(0, 100, "L"), make_swing(10, 110, "L")]
    closes = _closes([100 + i for i in range(20)])
    (tl,) = fit_trendlines(swings, "up", closes)
    assert tl.valid and tl.slope_per_day == Decimal(1)
    assert tl.value_at(dt.date(2024, 1, 21)) == Decimal(120)
    assert tl.touches == 2


def test_uptrend_line_broken_when_close_violates(make_swing):
    swings = [make_swing(0, 100, "L"), make_swing(10, 110, "L")]
    closes = _closes([100 + i for i in range(15)] + [90.0])
    (tl,) = fit_trendlines(swings, "up", closes)
    assert not tl.valid


def test_trendline_requires_higher_low_or_lower_high(make_swing):
    lows = [make_swing(0, 110, "L"), make_swing(10, 100, "L")]
    assert fit_trendlines(lows, "up", _closes([105.0] * 20)) == []
    highs = [make_swing(0, 120, "H"), make_swing(10, 110, "H")]
    (tl,) = fit_trendlines(highs, "down", _closes([100.0] * 20))
    assert tl.kind == "down" and tl.slope_per_day < 0 and tl.valid


def test_defense_line_from_state():
    state = SimpleNamespace(
        defense_line=Decimal(100), defense_line_ts=dt.date(2024, 1, 1),
        defense_line_kind="reaction_low",
    )
    assert defense_line_from_state(state) == {
        "price": Decimal(100), "ts": dt.date(2024, 1, 1), "type": "reaction_low",
        "agent_defined": True,
    }
    assert defense_line_from_state(SimpleNamespace(defense_line=None)) is None
