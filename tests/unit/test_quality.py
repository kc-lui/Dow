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
    """Serves canned frames to run_integrity_checks / row_reconciliation."""

    def __init__(self, bars, dup_extra=0, count=3):
        self.bars, self.dup_extra, self.count, self.logged = bars, dup_extra, count, None

    def query_df(self, sql, params=None):
        if "GROUP BY" in sql:
            return pd.DataFrame({"keys": [1], "extra": [self.dup_extra]})
        if "count()" in sql:
            return pd.DataFrame({"n": [self.count]})
        return self.bars

    def insert_df(self, table, df):
        self.logged = (table, df)


def _bars():
    return pd.DataFrame({"date": pd.to_datetime(["2024-01-02", "2024-01-03", "2024-01-04"]),
                         "exchange": "INDEX", "open": 10.0, "high": 11.0, "low": 9.0,
                         "close": 10.5, "volume": 0})


def test_run_checks_duplicates_and_reconciliation_and_log():
    from dowtheory.config import load_config
    client = FakeClient(_bars(), dup_extra=2, count=3)
    issues = q.run_integrity_checks(client, ["X"], load_config(), {"X": 5},
                                    today=pd.Timestamp("2024-01-05"))
    names = {(i.check_name, i.severity) for i in issues}
    assert {("coverage", "info"), ("duplicate", "error"), ("zero_volume", "warn"),
            ("row_reconciliation", "error")} <= names
    assert q.exit_status(issues) == 1
    table, frame = client.logged
    assert table == "dow.ops_data_quality_log" and len(frame) == len(issues)
    assert "STATUS FAIL" in q.format_report(issues)


def test_clean_run_exit_zero():
    from dowtheory.config import load_config
    client = FakeClient(_bars().assign(volume=5))
    issues = q.run_integrity_checks(client, ["X"], load_config(), {"X": 3},
                                    today=pd.Timestamp("2024-01-05"))
    assert q.exit_status(issues) == 0
