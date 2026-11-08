import dataclasses
import datetime as dt
import uuid

import pytest

from dowtheory.backtest.ledger import insert_ledger, ledger_frame
from dowtheory.backtest.results import RuleResult
from dowtheory.storage.clickhouse_client import ClickHouseClient


@pytest.fixture(scope="module")
def client():
    c = ClickHouseClient()
    if not c.ping():
        pytest.skip("ClickHouse not reachable")
    return c


def _row(metric: str) -> RuleResult:
    return RuleResult("R1", "trend_persistence", "DJ", "pct0.03/0.08f15", "primary", metric,
                      0.5, 10, 0.1, 0.9, 0.5, 0.2, "greater", "A+ B+", "na",
                      config_hash="c" * 64, period_start=dt.date(2000, 1, 3),
                      period_end=dt.date(2026, 11, 6))


def test_rows_differing_only_in_metric_name_survive_final_and_merge(client):
    run_id = f"test_rt_{uuid.uuid4().hex[:8]}"
    rows = [(_row("m1"), "literature-consensus", ""), (_row("m2"), "literature-consensus", "")]
    rows[1] = (dataclasses.replace(rows[1][0], label="data-confirmed"), rows[1][1], "")
    frame = ledger_frame(rows, run_id, "d" * 64, "integrity=none")
    try:
        insert_ledger(client, frame)
        client.command("OPTIMIZE TABLE dow.str_rule_backtest_log FINAL")  # force the merge
        got = client.query_df(
            "SELECT metric_name, label FROM dow.str_rule_backtest_log FINAL "
            "WHERE run_id = {r:String} ORDER BY metric_name", {"r": run_id})
        assert list(got["metric_name"]) == [
            "pct0.03/0.08f15|primary|m1|na", "pct0.03/0.08f15|primary|m2|na"]
        assert list(got["label"]) == ["n/a", "data-confirmed"]
        insert_ledger(client, frame)  # same run_id again stays idempotent
        n = client.query_df(
            "SELECT count() AS n FROM dow.str_rule_backtest_log FINAL WHERE run_id = {r:String}",
            {"r": run_id})["n"].iloc[0]
        assert n == 2
    finally:
        client.command("ALTER TABLE dow.str_rule_backtest_log DELETE WHERE run_id = "
                       f"'{run_id}' SETTINGS mutations_sync = 2")
