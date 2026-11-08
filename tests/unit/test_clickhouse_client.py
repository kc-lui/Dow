import pandas as pd
import pytest

from dowtheory.storage import sql_guard
from dowtheory.storage.clickhouse_client import ClickHouseClient, UnsafeSQLError

BAD_WRITES = [
    "DROP TABLE dow.mkt_klines", "truncate table dow.x", "SELECT 1; drop database dow",
    "ALTER TABLE usstock.mkt_daily_quotes DELETE WHERE 1",
    "INSERT INTO usstock.x SELECT 1",
    "INSERT INTO dow.x SELECT * FROM trading.y",
    "RENAME TABLE dow.mkt_klines TO dow.old",
    "EXCHANGE TABLES dow.mkt_klines AND usstock.x",
    "CREATE OR REPLACE TABLE dow.mkt_klines (a UInt8) ENGINE=Memory",
    "CREATE TABLE dow.x (a UInt8) ENGINE=Memory",
    "ALTER TABLE dow.mkt_klines MODIFY TTL toDateTime(ts_open) + INTERVAL 1 DAY",
    "ALTER TABLE dow.mkt_klines DETACH PARTITION ALL",
    "ALTER TABLE dow.mkt_klines DROP PARTITION 1",
    "aLtEr   TaBlE usstock.t\n DeLeTe WHERE 1",
    "ALTER /* dow. */ TABLE usstock.t DELETE WHERE 1",
    "-- dow.\nALTER TABLE usstock.t DELETE WHERE 1",
    "ALTER TABLE dow.t DELETE WHERE 1; ALTER TABLE usstock.t DELETE WHERE 1",
    "ALTER TABLE dow.t DELETE WHERE id IN (SELECT id FROM usstock.t)",
    "OPTIMIZE TABLE usstock.t FINAL",
    "GRANT ALL ON *.* TO dow_user",
    "SYSTEM DROP DNS CACHE",
    "CREATE USER x",
    "SELECT 1",  # reads do not go through command()
]
GOOD_WRITES = [
    "INSERT INTO dow.mkt_klines SELECT * FROM dow.mkt_klines_v2",
    "ALTER TABLE dow.mkt_klines DELETE WHERE symbol = 'TEST_RT' SETTINGS mutations_sync = 2",
    "alter table dow.t update a = 1 where 1",
    "OPTIMIZE TABLE dow.mkt_klines FINAL",
    "CREATE TABLE IF NOT EXISTS dow.a (x UInt8) ENGINE = MergeTree ORDER BY x",
    "CREATE DATABASE IF NOT EXISTS dow",
    "EXCHANGE TABLES dow.a AND dow.b",
    "ALTER TABLE dow.t DELETE WHERE detail = 'drop; usstock.x'",  # blanked literal
    "ALTER TABLE dow.t DELETE WHERE 1;",
]
BAD_READS = [
    "SELECT 1 FROM trading.t", "SELECT * FROM system.users", "SELECT 1 FROM usstock.t SETTINGS readonly=0",
    "DROP TABLE dow.x", "INSERT INTO dow.x SELECT 1", "ALTER TABLE dow.x DELETE WHERE 1",
    "SELECT 1; SELECT 2", "SELECT 1 FROM default.t", "SELECT * FROM information_schema.tables",
]
GOOD_READS = [
    "SELECT * FROM dow.mkt_klines FINAL WHERE symbol = {s:String}",
    "select 1 from usstock.mkt_daily_quotes",
    "SELECT count() FROM twstock.mkt_quotes",
    "SELECT symbol FROM dow.t WHERE symbol LIKE '%drop%'",
    "SELECT 1.5 AS x -- trailing comment about trading.t",
    "EXISTS TABLE dow.mkt_klines",
    "SELECT a.x FROM dow.t AS a",
]


@pytest.mark.parametrize("sql", BAD_WRITES)
def test_command_blocks(sql):
    with pytest.raises(UnsafeSQLError):
        ClickHouseClient().command(sql)


@pytest.mark.parametrize("sql", GOOD_WRITES)
def test_command_allows(sql):
    sql_guard.check_write(sql)


@pytest.mark.parametrize("sql", BAD_READS)
def test_query_blocks(sql):
    with pytest.raises(UnsafeSQLError):
        ClickHouseClient().query_df(sql)


@pytest.mark.parametrize("sql", GOOD_READS)
def test_query_allows(sql):
    sql_guard.check_read(sql)


def test_refuses_non_dow_table():
    for table in ("usstock.mkt_daily_quotes", "mkt_klines", "dow.a.b", "dow.x; DROP"):
        with pytest.raises(UnsafeSQLError):
            ClickHouseClient().insert_df(table, pd.DataFrame({"a": [1]}))


def test_refuses_other_database(monkeypatch):
    with pytest.raises(UnsafeSQLError):
        ClickHouseClient(database="usstock")
    monkeypatch.setenv("CLICKHOUSE_DATABASE", "twstock")
    with pytest.raises(UnsafeSQLError):
        ClickHouseClient()


def test_refuses_empty_insert():
    with pytest.raises(ValueError):
        ClickHouseClient().insert_df("dow.mkt_klines", pd.DataFrame())


def test_defaults_to_scoped_user(monkeypatch):
    monkeypatch.delenv("DOW_CLICKHOUSE_USER", raising=False)
    monkeypatch.setenv("CLICKHOUSE_USER", "trading_user")  # admin env must not leak in
    assert ClickHouseClient()._params["username"] == "dow_user"
