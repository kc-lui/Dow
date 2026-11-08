import pandas as pd
import pytest

from dowtheory.storage.clickhouse_client import ClickHouseClient, UnsafeSQLError


@pytest.mark.parametrize("sql", ["DROP TABLE dow.mkt_klines", "truncate table dow.x",
                                 "SELECT 1; drop database dow"])
def test_refuses_drop_truncate(sql):
    c = ClickHouseClient()
    with pytest.raises(UnsafeSQLError):
        c.command(sql)
    with pytest.raises(UnsafeSQLError):
        c.query_df(sql)


def test_refuses_non_dow_table():
    with pytest.raises(UnsafeSQLError):
        ClickHouseClient().insert_df("usstock.mkt_daily_quotes", pd.DataFrame({"a": [1]}))
    with pytest.raises(UnsafeSQLError):
        ClickHouseClient().insert_df("mkt_klines", pd.DataFrame({"a": [1]}))


def test_refuses_other_database(monkeypatch):
    with pytest.raises(UnsafeSQLError):
        ClickHouseClient(database="usstock")
    monkeypatch.setenv("CLICKHOUSE_DATABASE", "twstock")
    with pytest.raises(UnsafeSQLError):
        ClickHouseClient()


def test_refuses_empty_insert():
    with pytest.raises(ValueError):
        ClickHouseClient().insert_df("dow.mkt_klines", pd.DataFrame())
