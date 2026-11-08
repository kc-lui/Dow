import datetime as dt
from decimal import Decimal

from dowtheory.persist import persist
from dowtheory.schema import AnalysisResult


class FakeClient:
    def __init__(self):
        self.calls = {}

    def insert_df(self, table, df):
        self.calls[table] = df
        return len(df)


def test_persist_targets_dow_tables_and_skips_empty():
    d = dt.date(2024, 1, 2)
    result = AnalysisResult(
        meta={"symbol": "^DJI", "pair": "^DJT", "as_of": d, "swing_method": "pct",
              "run_id": "r1", "thresholds": {"minor_pct": 0.03, "secondary_pct": 0.1}},
        trend_state={"primary": "BULL_PRIMARY", "secondary_direction": "up",
                     "confirmation": {"status": "confirmed"}, "volume_confirms": None,
                     "defense_line": {"price": Decimal("100.5"), "ts": d, "type": "reaction_low",
                                      "agent_defined": True}},
        swings=[{"ts": d, "price": Decimal(100), "kind": "H", "scale": "minor",
                 "confirmed_ts": d, "amplitude_pct": Decimal("0.05"), "duration_days": 3,
                 "retrace_ratio": None}],
    )
    client = FakeClient()
    written = persist(result, client)
    assert set(written) == {"dow.str_swing_log", "dow.str_trend_state_snapshots",
                            "dow.str_level_log"}
    assert all(t.startswith("dow.") for t in client.calls)
    assert client.calls["dow.str_level_log"]["level_type"].tolist() == ["defense"]
    assert "BULL_PRIMARY" in client.calls["dow.str_trend_state_snapshots"]["payload"].iloc[0]
