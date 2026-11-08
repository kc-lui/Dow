import pandas as pd

from dowtheory.data import quality as q


def _frame(dates, **over):
    df = pd.DataFrame({"open": 10.0, "high": 11.0, "low": 9.0, "close": 10.5, "volume": 100},
                      index=pd.DatetimeIndex(dates))
    for k, v in over.items():
        df[k] = v
    return df


def test_gap_warn_and_info():
    dates = pd.bdate_range("2024-01-02", "2024-03-29").delete(
        list(range(10, 20)) + [30])  # one 10-day run, one single-day
    issues = q.check_gaps("X", dates, max_gap=4)
    sev = {i.severity for i in issues}
    assert sev == {"warn", "info"}
    assert any("10 missing" in i.detail for i in issues if i.severity == "warn")


def test_no_gap_over_holiday():
    dates = pd.DatetimeIndex(["2024-12-24", "2024-12-26"])  # Christmas excluded from expected
    assert q.check_gaps("X", dates, 4) == []


def test_ohlc_errors():
    df = _frame(["2024-01-02", "2024-01-03", "2024-01-04"])
    df.loc[df.index[0], "high"] = 10.0      # below close
    df.loc[df.index[1], "low"] = 10.9       # above close
    df.loc[df.index[2], "low"] = 0.0        # non-positive
    (issue,) = q.check_ohlc("X", df)
    assert issue.severity == "error" and "3 bars" in issue.detail
    assert q.check_ohlc("X", _frame(["2024-01-02"])) == []


def test_zero_volume_severity():
    df = _frame(["2024-01-02", "2024-01-03"], volume=0)
    assert q.check_zero_volume("X", df, "INDEX")[0].severity == "warn"
    assert q.check_zero_volume("X", df, "NYSEARCA")[0].severity == "error"
    assert q.check_zero_volume("X", _frame(["2024-01-02"]), "INDEX") == []


def test_stale():
    today = pd.Timestamp("2024-02-01")
    assert q.check_stale("X", pd.Timestamp("2024-01-10"), today, 5)[0].severity == "warn"
    assert q.check_stale("X", pd.Timestamp("2024-01-31"), today, 5) == []


class FakeClient:
    """Serves canned frames, dispatching on explicit query markers."""

    def __init__(self, bars, ident=0, conflict=0, n_exchange=1, count=3):
        self.bars, self.ident, self.conflict = bars, ident, conflict
        self.n_exchange, self.count, self.logged = n_exchange, count, None

    def query_df(self, sql, params=None):
        if "countIf(v = 1)" in sql:
            return pd.DataFrame({"ident_keys": [int(self.ident > 0)], "ident_extra": [self.ident],
                                 "conflict_keys": [self.conflict]})
        if "WHERE v > 1" in sql:
            return pd.DataFrame({"ts_open": pd.to_datetime(["2024-01-03 09:30"])})
        if "uniqExact(exchange)" in sql:
            return pd.DataFrame({"n": [self.n_exchange]})
        if "count() AS n" in sql:
            return pd.DataFrame({"n": [self.count]})
        return self.bars

    def insert_df(self, table, df):
        self.logged = (table, df)


def _bars():
    return pd.DataFrame({"date": pd.to_datetime(["2024-01-02", "2024-01-03", "2024-01-04"]),
                         "exchange": "INDEX", "open": 10.0, "high": 11.0, "low": 9.0,
                         "close": 10.5, "volume": 0})


def _run(client, symbols=("X",), counts=None):
    from dowtheory.config import load_config
    return q.run_integrity_checks(client, list(symbols), load_config(), counts,
                                  today=pd.Timestamp("2024-01-05"), run_id="r1")


def test_conflicting_duplicates_are_errors_identical_are_info():
    issues = _run(FakeClient(_bars(), ident=2, conflict=1), counts={"X": 5})
    names = {(i.check_name, i.severity) for i in issues}
    assert {("coverage", "info"), ("duplicate_identical", "info"), ("duplicate_conflict", "error"),
            ("zero_volume", "warn"), ("row_reconciliation", "error")} <= names
    assert "OPTIMIZE" not in " ".join(i.detail for i in issues)
    assert q.exit_status(issues) == 1


def test_identical_duplicates_alone_pass():
    issues = _run(FakeClient(_bars().assign(volume=5), ident=3), counts={"X": 3})
    assert q.exit_status(issues) == 0
    assert ("duplicate_identical", "info") in {(i.check_name, i.severity) for i in issues}


def test_exchange_conflict_both_forms():
    many = _run(FakeClient(_bars().assign(volume=5), n_exchange=2))
    assert ("exchange_conflict", "error") in {(i.check_name, i.severity) for i in many}
    mism = _run(FakeClient(_bars().assign(volume=5, exchange="NYSE"), n_exchange=1), symbols=["^DJI"])
    assert any(i.check_name == "exchange_conflict" and "NYSE" in i.detail for i in mism)


def test_log_rows_carry_run_id_and_bar_key():
    client = FakeClient(_bars(), conflict=1)
    issues = _run(client)
    table, frame = client.logged
    assert table == "dow.ops_data_quality_log" and len(frame) == len(issues)
    assert set(frame["run_id"]) == {"r1"}
    conflict = frame[frame["check_name"] == "duplicate_conflict"]["bar_ts"].iloc[0]
    assert str(conflict) == "2024-01-03 09:30:00-05:00"
    assert str(frame[frame["check_name"] == "coverage"]["bar_ts"].iloc[0]).startswith("1969-12-31 19:00")
    assert "STATUS FAIL" in q.format_report(issues)


def test_empty_symbol_list_fails_the_gate():
    issues = _run(FakeClient(_bars()), symbols=())
    assert q.exit_status(issues) == 1 and issues[0].detail == "no symbols to check"


def test_flat_bar_warns_and_reports_analysis_start():
    df = _frame(["2024-01-02", "2024-01-03"], open=10.0, high=10.0, low=10.0, close=10.0)
    (issue,) = q.check_flat_bars("X", df, "2024-01-03")
    assert issue.severity == "warn" and "1 on/after analysis_start" in issue.detail
    assert q.check_flat_bars("X", _frame(["2024-01-02"])) == []


def test_analysis_start_clip_logged_as_info():
    from dowtheory.config import load_config
    bars = _bars().assign(volume=5, date=pd.to_datetime(["1962-06-27", "1962-06-28", "1962-07-02"]))
    issues = q.run_integrity_checks(FakeClient(bars), ["^GSPC"], load_config(), today=pd.Timestamp("2024-01-05"), log=False)
    assert any("analysis_start=1962-07-02 clips 2" in i.detail for i in issues)
