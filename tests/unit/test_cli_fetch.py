import pandas as pd

from dowtheory import cli
from dowtheory.data import quality


class FakeClient:
    def __init__(self):
        self.inserted, self.logged = [], []

    def __enter__(self):
        return self

    def __exit__(self, *a):
        pass

    def insert_df(self, table, df):
        self.inserted.append((table, df["symbol"].iloc[0]))

    def query_df(self, sql, params=None):
        return pd.DataFrame({"n": [3]})


def _bars(symbol, last="2024-01-04"):
    ts = pd.to_datetime(pd.bdate_range(end=last, periods=3)).tz_localize("America/New_York")
    return pd.DataFrame({"exchange": "INDEX", "symbol": symbol, "interval": "1d", "ts_open": ts,
                         "ts_close": ts, "open": 1.0, "high": 2.0, "low": 0.5, "close": 1.5,
                         "volume": 1, "source": "t"})


def _setup(monkeypatch, fetch):
    client = FakeClient()
    monkeypatch.setattr(cli, "ClickHouseClient", lambda: client)
    monkeypatch.setattr(cli, "_fetch_one", fetch)
    monkeypatch.setattr(quality, "log_issues", lambda c, issues, run_id=None: client.logged.extend(issues))
    return client


def test_failure_does_not_stop_other_symbols_and_is_logged(monkeypatch):
    def fetch(source, symbol, start, cfg):
        if symbol == "A":
            raise RuntimeError("rate limited")
        return _bars(symbol)

    client = _setup(monkeypatch, fetch)
    rc = cli.main(["fetch", "--symbols", "A", "B"])
    assert rc == 1
    assert client.inserted == [("dow.mkt_klines", "B")]
    errors = [i for i in client.logged if i.severity == "error"]
    assert errors[0].symbol == "A" and "RuntimeError: rate limited" in errors[0].detail


def test_insert_failure_is_caught_per_symbol(monkeypatch):
    client = _setup(monkeypatch, lambda s, sym, st, c: _bars(sym))
    original = client.insert_df

    def flaky(table, df):
        if df["symbol"].iloc[0] == "A":
            raise OSError("disk")
        original(table, df)

    client.insert_df = flaky
    assert cli.main(["fetch", "--symbols", "A", "B"]) == 1
    assert client.inserted == [("dow.mkt_klines", "B")]
    assert any(i.symbol == "A" and "OSError" in i.detail for i in client.logged)


def test_empty_after_filter_is_error_not_crash(monkeypatch):
    client = _setup(monkeypatch, lambda *a: _bars("A").iloc[0:0])
    assert cli.main(["fetch", "--probe", "--symbols", "A", "--start", "2030-01-01"]) == 1
    assert client.logged and client.logged[0].severity == "error"


def test_success_exit_zero_and_logs_once(monkeypatch):
    client = _setup(monkeypatch, lambda s, sym, st, c: _bars(sym))
    assert cli.main(["fetch", "--symbols", "A"]) == 0
    assert [i.check_name for i in client.logged] == ["coverage"]
