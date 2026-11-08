import uuid

import pandas as pd
import pytest

from dowtheory.data.bars import normalize_bars, to_insert_frame
from dowtheory.data.loader import load_klines
from dowtheory.data.quality import QualityIssue, log_issues
from dowtheory.storage.clickhouse_client import ClickHouseClient


@pytest.fixture(scope="module")
def client():
    c = ClickHouseClient()
    if not c.ping():
        pytest.skip("ClickHouse not reachable")
    return c


@pytest.fixture
def symbol(client):
    """Unique temp symbol; its rows are deleted and the mutation awaited afterwards."""
    sym = f"TEST_RT_{uuid.uuid4().hex[:8]}"
    yield sym
    client.command(f"ALTER TABLE dow.mkt_klines DELETE WHERE symbol = '{sym}' "
                   "SETTINGS mutations_sync = 2")
    left = client.query_df("SELECT count() AS n FROM dow.mkt_klines WHERE symbol = {s:String}",
                           {"s": sym})["n"].iloc[0]
    assert left == 0


def _bars(sym, start, n=5):
    raw = pd.DataFrame(
        {"Open": [1.5] * n, "High": [2.0] * n, "Low": [1.0] * n,
         "Close": [1.75, 2.5, 3.5, 4.5, 5.5][:n], "Volume": [10] * n},
        index=pd.bdate_range(start, periods=n, name="Date"))
    return normalize_bars(raw.reset_index(), sym, "csv", "INDEX")


def test_roundtrip_final_dst_and_pre1970(client, symbol):
    # one week crossing the 2024-03-10 DST change, plus a 1950 bar (pre-epoch)
    bars = pd.concat([_bars(symbol, "1950-06-05", 1), _bars(symbol, "2024-03-07")], ignore_index=True)
    client.insert_df("dow.mkt_klines", to_insert_frame(bars))
    client.insert_df("dow.mkt_klines", to_insert_frame(bars))  # re-load: FINAL must dedupe
    df = load_klines(symbol, client=client, ignore_analysis_start=True)
    assert len(df) == 6
    assert df.index[0] == pd.Timestamp("1950-06-05") and df.index[1] == pd.Timestamp("2024-03-07")


def test_conflicting_duplicate_detected(client, symbol):
    """Needs two unmerged parts, so a background merge winning the race skips the test.

    (Rows inside ONE insert block are already collapsed by ReplacingMergeTree.)
    """
    from dowtheory.data.quality import check_duplicates
    good = to_insert_frame(_bars(symbol, "2024-03-04", 1))
    bad = to_insert_frame(_bars(symbol, "2024-03-04", 1).assign(close=9.0, exchange="NYSE"))
    client.insert_df("dow.mkt_klines", good)
    client.insert_df("dow.mkt_klines", good)
    ident = {i.check_name for i in check_duplicates(client, symbol)}
    if not ident:
        pytest.skip("parts merged before the check ran")
    assert ident == {"duplicate_identical"}
    client.insert_df("dow.mkt_klines", bad)
    sev = {i.check_name: i.severity for i in check_duplicates(client, symbol)}
    if "duplicate_conflict" not in sev:
        pytest.skip("parts merged before the check ran")
    assert sev["duplicate_conflict"] == "error"


def test_quality_log_keeps_all_rows(client):
    run = uuid.uuid4().hex
    issues = [QualityIssue("TEST_LOG", "gap", "warn", f"gap {i}") for i in range(3)]
    log_issues(client, issues, run)
    client.command("OPTIMIZE TABLE dow.ops_data_quality_log FINAL")
    n = client.query_df("SELECT count() AS n FROM dow.ops_data_quality_log WHERE run_id = {r:String}",
                        {"r": run})["n"].iloc[0]
    assert n == 3
    client.command(f"ALTER TABLE dow.ops_data_quality_log DELETE WHERE run_id = '{run}' "
                   "SETTINGS mutations_sync = 2")
