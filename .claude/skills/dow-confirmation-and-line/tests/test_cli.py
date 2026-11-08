"""Run ``scripts/confirm.py`` on the CSV fixture (both legs) and on the skill's two-leg fixture."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

SKILL = Path(__file__).resolve().parents[1]
ROOT = SKILL.parents[2]
SCRIPT = SKILL / "scripts" / "confirm.py"
FIXTURE = ROOT / "tests" / "fixtures" / "dji_sample.csv"
PAIR_A = SKILL / "tests" / "fixtures" / "pair_a_sample.csv"
PAIR_B = SKILL / "tests" / "fixtures" / "pair_b_sample.csv"
STATUSES = {"confirmed", "non_confirmation", "pending"}
STATES = {"UNDEFINED", "BULL_PRIMARY", "BEAR_PRIMARY", "BULL_SUSPECT", "BEAR_SUSPECT"}
DOC_KEYS = {
    "symbol",
    "pair",
    "bars",
    "start",
    "end",
    "band_pct",
    "min_sessions",
    "max_drift_frac",
    "max_days",
    "pair_confirm",
    "trend_a",
    "trend_b",
    "signals",
    "reversals_b",
    "lines",
    "volume_confirms",
}
PAIR_KEYS = {"status", "pair_state", "detail", "confirmed_ts"}
SIGNAL_KEYS = {"ts", "kind", "price", "level", "confirmation", "matched_ts", "confirmed_ts"}
LINE_KEYS = {
    "start",
    "end",
    "sessions",
    "band_pct_a",
    "band_pct_b",
    "breakout",
    "breakout_ts",
    "confirmed_both",
    "confirmed_ts",
}


def run(*extra: str, csv: Path | None = FIXTURE, csv_pair: Path | None = None):
    cmd = [sys.executable, str(SCRIPT), "--json", *extra]
    if csv is not None:
        cmd += ["--source", "csv", "--csv", str(csv)]
    if csv_pair is not None:
        cmd += ["--csv-pair", str(csv_pair)]
    return subprocess.run(cmd, capture_output=True, text=True, cwd=ROOT, timeout=300, check=False)


def doc_of(proc: subprocess.CompletedProcess) -> dict:
    assert proc.returncode == 0, proc.stderr
    return json.loads(proc.stdout.strip().splitlines()[-1])


def clickhouse_available() -> bool:
    sys.path.insert(0, str(ROOT / "src"))
    try:
        from dowtheory.storage.clickhouse_client import ClickHouseClient

        return ClickHouseClient().ping()
    except Exception:  # noqa: BLE001 - any failure means skip, not fail
        return False


def check_shape(doc: dict) -> None:
    assert set(doc) == DOC_KEYS
    assert set(doc["pair_confirm"]) == PAIR_KEYS and doc["pair_confirm"]["status"] in STATUSES
    assert doc["trend_a"]["primary"] in STATES and doc["trend_b"]["primary"] in STATES
    assert isinstance(doc["lines"], list)
    for ln in doc["lines"]:
        assert set(ln) == LINE_KEYS and ln["sessions"] >= doc["min_sessions"] == 15
        assert ln["breakout"] in {"up", "down", "none"}
        assert max(ln["band_pct_a"], ln["band_pct_b"]) <= doc["band_pct"] == 0.05
        assert ln["confirmed_both"] is (ln["confirmed_ts"] is not None)
        if ln["confirmed_ts"] is not None:
            assert ln["confirmed_ts"] >= ln["breakout_ts"]
    for sig in doc["signals"] + doc["reversals_b"]:
        assert set(sig) == SIGNAL_KEYS
        assert sig["confirmation"] in {"confirmed", "pending", "not_applicable"}
        if not sig["kind"].startswith("REVERSAL"):
            assert sig["confirmation"] == "not_applicable"
    assert doc["volume_confirms"] in {True, False, None}
    assert doc["max_days"] is None


def test_fixture_as_both_legs() -> None:
    proc = run()  # no --symbol/--pair/--csv-pair: the fixture is both legs
    doc = doc_of(proc)
    check_shape(doc)
    assert doc["symbol"] == doc["pair"] == "DJI_SAMPLE"
    assert doc["pair_confirm"]["status"] == "confirmed"  # identical legs give identical states
    assert doc["pair_confirm"]["pair_state"] == doc["trend_a"]["primary"] == "BEAR_PRIMARY"
    assert doc["lines"] and all(ln["band_pct_a"] == ln["band_pct_b"] for ln in doc["lines"])
    table_rows = [ln for ln in proc.stdout.splitlines() if ln.startswith("| 20")]
    assert len(table_rows) == len(doc["signals"]) + len(doc["lines"])
    assert "| confirmed | BEAR_PRIMARY |" in proc.stdout
    assert "volume_confirms:" in proc.stdout and "41 lines" not in proc.stdout


def test_pair_fixture_non_confirmation_and_confirmed_line_breakout() -> None:
    """Leg A stays bull, leg B reverses: state-level non_confirmation; one line, confirmed later."""
    doc = doc_of(run(csv=PAIR_A, csv_pair=PAIR_B))
    check_shape(doc)
    assert (doc["symbol"], doc["pair"]) == ("PAIR_A_SAMPLE", "PAIR_B_SAMPLE")
    assert doc["pair_confirm"]["status"] == "non_confirmation"
    assert doc["pair_confirm"]["pair_state"] is None
    assert "opposite directions" in doc["pair_confirm"]["detail"]
    assert doc["trend_a"] == {"primary": "BULL_PRIMARY", "since": "2021-05-14"}
    assert doc["trend_b"] == {"primary": "BEAR_PRIMARY", "since": "2021-07-21"}
    assert [(r["ts"], r["kind"]) for r in doc["reversals_b"]] == [("2021-07-21", "REVERSAL_DOWN")]
    assert not any(s["kind"].startswith("REVERSAL") for s in doc["signals"])
    assert len(doc["lines"]) == 1
    line = doc["lines"][0]
    assert (line["start"], line["end"], line["sessions"]) == ("2021-03-11", "2021-04-07", 20)
    assert line["band_pct_a"] < 0.01 and line["band_pct_b"] < 0.01
    assert (line["breakout"], line["breakout_ts"]) == ("up", "2021-04-08")
    assert line["confirmed_both"] is True and line["confirmed_ts"] == "2021-04-13"
    assert doc["volume_confirms"] is not None


@pytest.mark.parametrize(
    ("end", "confirmed", "confirmed_ts"),
    [("2021-04-09", False, None), ("2021-04-12", False, None), ("2021-04-13", True, "2021-04-13")],
)
def test_confirmed_both_flips_only_after_second_leg_breaks(end, confirmed, confirmed_ts) -> None:
    """No lookahead: the line's breakout is known on A's break; confirmation waits for B's."""
    doc = doc_of(run("--end", end, csv=PAIR_A, csv_pair=PAIR_B))
    assert doc["end"] <= end
    assert len(doc["lines"]) == 1
    line = doc["lines"][0]
    assert (line["start"], line["end"], line["breakout"], line["breakout_ts"]) == (
        "2021-03-11",
        "2021-04-07",
        "up",
        "2021-04-08",
    )
    assert line["confirmed_both"] is confirmed and line["confirmed_ts"] == confirmed_ts


def test_truncated_run_matches_full_run_prefix() -> None:
    """Signals and line windows known at ``--end`` equal the full run's up to that date."""
    full = doc_of(run(csv=PAIR_A, csv_pair=PAIR_B))
    part = doc_of(run("--end", "2021-06-30", csv=PAIR_A, csv_pair=PAIR_B))
    assert part["signals"] == [s for s in full["signals"] if s["ts"] <= part["end"]]
    windows = [(ln["start"], ln["end"]) for ln in full["lines"] if ln["end"] <= part["end"]]
    assert [(ln["start"], ln["end"]) for ln in part["lines"]] == windows
    assert part["pair_confirm"]["status"] in STATUSES
    assert part["trend_a"]["primary"] == "BULL_PRIMARY"
    assert part["trend_b"]["primary"] != "BEAR_PRIMARY"  # B's reversal is only known on 2021-07-21


def test_missing_symbol_errors_cleanly() -> None:
    proc = run(csv=None)
    assert proc.returncode == 2 and "--symbol and --pair are required" in proc.stderr


@pytest.mark.parametrize("end", ["2021-04-09", "2021-04-12"])
def test_pending_while_either_leg_is_undefined(end: str) -> None:
    doc = doc_of(run("--end", end, csv=PAIR_A, csv_pair=PAIR_B))
    assert doc["pair_confirm"]["status"] == "pending" and doc["pair_confirm"]["pair_state"] is None
    assert doc["trend_a"]["primary"] == doc["trend_b"]["primary"] == "UNDEFINED"
    assert "no defined trend yet" in doc["pair_confirm"]["detail"]


def test_same_side_suspect_is_non_confirmation() -> None:
    """Leg B has broken its defense line but not reversed: PRIMARY vs SUSPECT on the same side."""
    doc = doc_of(run("--end", "2021-06-21", csv=PAIR_A, csv_pair=PAIR_B))
    assert doc["trend_a"]["primary"] == "BULL_PRIMARY"
    assert doc["trend_b"]["primary"] == "BULL_SUSPECT"
    assert doc["pair_confirm"]["status"] == "non_confirmation"
    assert "only one average has stalled" in doc["pair_confirm"]["detail"]
    confirmed = doc_of(run("--end", "2021-06-10", csv=PAIR_A, csv_pair=PAIR_B))
    assert confirmed["pair_confirm"] == {
        "status": "confirmed",
        "pair_state": "BULL_PRIMARY",
        "detail": "Both averages are BULL_PRIMARY",
        "confirmed_ts": None,
    }


def test_volume_flag_is_none_with_fewer_than_three_swings() -> None:
    doc = doc_of(run("--end", "2021-02-12", csv=PAIR_A, csv_pair=PAIR_B))
    assert doc["bars"] == 30 and doc["volume_confirms"] is None
    assert "volume_confirms: null" in run("--end", "2021-02-12", csv=PAIR_A, csv_pair=PAIR_B).stdout


def test_empty_inner_join_errors_cleanly() -> None:
    proc = run("--start", "2021-03-01", csv=PAIR_A, csv_pair=FIXTURE)  # fixture ends 2021-02-24
    assert (
        proc.returncode == 2
        and "no common sessions for PAIR_A_SAMPLE and DJI_SAMPLE" in proc.stderr
    )


def test_pair_fixture_matches_its_generator() -> None:
    gen = SKILL / "tests" / "fixtures" / "make_pair_sample.py"
    proc = subprocess.run(
        [sys.executable, str(gen), "--check"], capture_output=True, text=True, check=False
    )
    assert proc.returncode == 0, proc.stdout + proc.stderr


@pytest.mark.skipif(not clickhouse_available(), reason="ClickHouse not reachable")
def test_dji_djt_since_2015_matches_skill_example() -> None:
    doc = doc_of(
        run(
            "--symbol",
            "^DJI",
            "--pair",
            "^DJT",
            "--start",
            "2015-01-01",
            "--end",
            "2026-11-06",
            csv=None,
        )
    )
    check_shape(doc)
    assert doc["pair_confirm"]["status"] == "non_confirmation"
    assert doc["trend_a"] == {"primary": "BULL_PRIMARY", "since": "2023-06-15"}
    assert doc["trend_b"] == {"primary": "BEAR_PRIMARY", "since": "2026-09-24"}
    reversals = {
        (s["ts"], s["kind"]): s for s in doc["signals"] if s["kind"].startswith("REVERSAL")
    }
    down = reversals[("2022-05-09", "REVERSAL_DOWN")]
    assert (down["confirmation"], down["matched_ts"], down["confirmed_ts"]) == (
        "confirmed",
        "2022-04-08",
        "2022-05-09",
    )
    up = reversals[("2020-08-05", "REVERSAL_UP")]
    assert (up["matched_ts"], up["confirmed_ts"]) == ("2020-04-17", "2020-08-05")
    assert ("2026-09-24", "REVERSAL_DOWN") in {(s["ts"], s["kind"]) for s in doc["reversals_b"]}
    assert len(doc["lines"]) == 41
    last = doc["lines"][-1]
    assert (last["start"], last["end"], last["breakout"]) == ("2026-09-16", "2026-10-26", "up")
    assert (last["breakout_ts"], last["confirmed_ts"]) == ("2026-10-27", "2026-11-04")
