import datetime as dt
import json
from decimal import Decimal

from dowtheory.schema import STATUS_LABELS, AnalysisResult


def _result():
    return AnalysisResult(
        meta={"symbol": "^DJI", "as_of": dt.date(2024, 1, 2)},
        trend_state={"primary": "BULL_PRIMARY", "since": dt.date(2023, 5, 1)},
        swings=[{"ts": dt.date(2024, 1, 1), "price": Decimal("100.25"), "retrace_ratio": None}],
    )


def test_status_labels_default_exact():
    assert _result().status_labels == {
        "defense_line": "agent-defined",
        "secondary_duration_bounds": "literature-disputed",
        "secondary_retracement": "literature-disputed",
        "rhea_3pct_filter": "single-source",
        "secondary_pct_threshold": "agent-defined",
        "line_definition": "literature-consensus",
        "two_average_confirmation": "literature-consensus",
    }


def test_status_labels_not_shared_between_instances():
    a, b = _result(), _result()
    a.status_labels["defense_line"] = "x"
    assert b.status_labels == STATUS_LABELS


def test_to_json_converts_decimal_and_dates():
    data = json.loads(_result().to_json())
    assert data["swings"][0] == {"ts": "2024-01-01", "price": 100.25, "retrace_ratio": None}
    assert data["meta"]["as_of"] == "2024-01-02"
    assert set(data) == {
        "meta", "trend_state", "swings", "levels", "lines", "signals", "status_labels"
    }
    assert set(data["levels"]) == {"support", "resistance", "trendlines"}
