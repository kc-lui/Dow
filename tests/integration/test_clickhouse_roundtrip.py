import pandas as pd
import pytest

from dowtheory.data.bars import normalize_bars, to_insert_frame
from dowtheory.data.loader import load_klines
from dowtheory.storage.clickhouse_client import ClickHouseClient

client = ClickHouseClient()
pytestmark = pytest.mark.skipif(not client.ping(), reason="ClickHouse not reachable")


def test_roundtrip_with_final_and_cleanup():
    raw = pd.DataFrame(
        {"Open": [1.5, 2, 3, 4, 5], "High": [2, 3, 4, 5, 6], "Low": [1, 1, 2, 3, 4],
         "Close": [1.75, 2.5, 3.5, 4.5, 5.5], "Volume": [10, 20, 30, 40, 50]},
        index=pd.bdate_range("2024-03-04", periods=5, name="Date"))
    bars = normalize_bars(raw.reset_index(), "TEST_RT", "csv", "INDEX")
    try:
        client.insert_df("dow.mkt_klines", to_insert_frame(bars))
        client.insert_df("dow.mkt_klines", to_insert_frame(bars))  # re-load: FINAL must dedupe
        df = load_klines("TEST_RT", client=client)
        assert len(df) == 5
        assert df["close"].tolist() == [1.75, 2.5, 3.5, 4.5, 5.5]
        assert df.index[0] == pd.Timestamp("2024-03-04")
    finally:
        client.command("ALTER TABLE dow.mkt_klines DELETE WHERE symbol = 'TEST_RT' "
                       "SETTINGS mutations_sync = 0")  # async: sync waits ~80s on the shared server
