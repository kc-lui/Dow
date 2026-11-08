"""Run ``scripts/trend.py`` on the CSV fixture (strict and non-strict); check table, JSON, replay."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

SKILL = Path(__file__).resolve().parents[1]
ROOT = SKILL.parents[2]
SCRIPT = SKILL / "scripts" / "trend.py"
FIXTURE = ROOT / "tests" / "fixtures" / "dji_sample.csv"
BREAK_FIXTURE = SKILL / "tests" / "fixtures" / "defense_break_sample.csv"
STATES = {"UNDEFINED", "BULL_PRIMARY", "BEAR_PRIMARY", "BULL_SUSPECT", "BEAR_SUSPECT"}
SIGNAL_KINDS = {
    "TREND_ESTABLISHED",
    "HH",
    "HL",
    "LH",
    "LL",
    "DEFENSE_BREAK",
    "REVERSAL_UP",
    "REVERSAL_DOWN",
}
DOC_KEYS = {
    "symbol",
    "bars",
    "start",
    "end",
    "strict",
    "equal_extreme_tol",
    "warmup_note",
    "trend_state",
    "signals",
}
STATE_KEYS = {
    "primary",
    "since",
    "secondary_direction",
    "defense_line",
    "last_H",
    "prev_H",
    "last_L",
    "prev_L",
}
SIGNAL_KEYS = {"ts", "kind", "price", "level", "note", "agent_defined"}
DEFENSE_KEYS = {"price", "ts", "type", "agent_defined"}


def run(*extra: str, csv: Path | None = FIXTURE) -> subprocess.CompletedProcess:
    cmd = [sys.executable, str(SCRIPT), "--json", *extra]
    if csv is not None:
        cmd += ["--source", "csv", "--csv", str(csv)]
    return subprocess.run(cmd, capture_output=True, text=True, cwd=ROOT, timeout=300, check=False)


def clickhouse_available() -> bool:
    sys.path.insert(0, str(ROOT / "src"))
    try:
        from dowtheory.storage.clickhouse_client import ClickHouseClient

        return ClickHouseClient().ping()
    except Exception:  # noqa: BLE001 - any failure means skip, not fail
        return False


def doc_of(proc: subprocess.CompletedProcess) -> dict:
    assert proc.returncode == 0, proc.stderr
    return json.loads(proc.stdout.strip().splitlines()[-1])


@pytest.mark.parametrize("mode", ["--strict", "--no-strict"])
def test_state_defense_line_and_signals(mode: str) -> None:
    proc = run("--symbol", "^DJI", mode)
    doc = doc_of(proc)
    assert set(doc) == DOC_KEYS and doc["strict"] is (mode == "--strict")
    state = doc["trend_state"]
    assert set(state) == STATE_KEYS and state["primary"] in STATES
    assert state["secondary_direction"] in {"up", "down", "flat"}
    if state["primary"] != "UNDEFINED":
        assert state["since"] is not None
        defense = state["defense_line"]
        assert set(defense) == DEFENSE_KEYS and defense["agent_defined"] is True
        assert defense["type"] in {"reaction_low", "reaction_high"}
    for sig in doc["signals"]:
        assert set(sig) == SIGNAL_KEYS and sig["kind"] in SIGNAL_KINDS
        assert sig["agent_defined"] is (sig["kind"] == "DEFENSE_BREAK")
    table = [ln for ln in proc.stdout.splitlines() if ln.startswith("| 20")]
    assert len(table) == len(doc["signals"])
    assert "| BULL_" in proc.stdout or "| BEAR_" in proc.stdout or "| UNDEFINED" in proc.stdout
    assert "agent-defined" in proc.stdout or state["defense_line"] is None


def test_fixture_reaches_bear_primary_with_warmup_note() -> None:
    doc = doc_of(run())  # no --symbol: defaults to the CSV stem
    assert doc["symbol"] == "DJI_SAMPLE"
    kinds = [s["kind"] for s in doc["signals"]]
    assert "TREND_ESTABLISHED" in kinds
    assert doc["trend_state"]["primary"] == "BEAR_PRIMARY"
    assert doc["warmup_note"].startswith("Data starts 2020-01-02")
    established = next(s for s in doc["signals"] if s["kind"] == "TREND_ESTABLISHED")
    assert doc["trend_state"]["since"] == established["ts"] == "2020-12-07"


@pytest.mark.parametrize("end", ["2020-10-30", "2021-01-15"])
def test_truncated_replay_matches_full_run(end: str) -> None:
    """No lookahead: signals up to ``end`` equal the full run's signals up to that date."""
    full = doc_of(run("--symbol", "^DJI"))
    part = doc_of(run("--symbol", "^DJI", "--end", end))
    assert part["end"] <= end
    expected = [s for s in full["signals"] if s["ts"] <= part["end"]]
    assert part["signals"] == expected
    assert part["trend_state"]["primary"] in STATES


def test_defense_break_fixture_strict_vs_non_strict() -> None:
    """Strict: break -> SUSPECT -> REVERSAL_DOWN; non-strict: the break itself flips the trend."""
    strict = doc_of(run("--strict", csv=BREAK_FIXTURE))
    loose = doc_of(run("--no-strict", csv=BREAK_FIXTURE))
    s_kinds = [s["kind"] for s in strict["signals"]]
    l_kinds = [s["kind"] for s in loose["signals"]]
    assert s_kinds[2:] == ["TREND_ESTABLISHED", "DEFENSE_BREAK", "LL", "LH", "REVERSAL_DOWN", "LL"]
    assert l_kinds[2:] == ["TREND_ESTABLISHED", "DEFENSE_BREAK", "LL", "LH", "LL"]
    s_break = next(s for s in strict["signals"] if s["kind"] == "DEFENSE_BREAK")
    l_break = next(s for s in loose["signals"] if s["kind"] == "DEFENSE_BREAK")
    assert s_break["ts"] == l_break["ts"] == "2021-04-29"
    assert s_break["agent_defined"] and l_break["agent_defined"]
    assert s_break["level"] == l_break["level"] == 108.0 and s_break["price"] < 108.0
    assert "now suspect" in s_break["note"] and "flips" in l_break["note"]
    reversal = next(s for s in strict["signals"] if s["kind"] == "REVERSAL_DOWN")
    assert reversal["ts"] == "2021-06-22" and not reversal["agent_defined"]
    assert strict["trend_state"]["primary"] == loose["trend_state"]["primary"] == "BEAR_PRIMARY"
    assert strict["trend_state"]["since"] == reversal["ts"]
    assert loose["trend_state"]["since"] == l_break["ts"]
    assert strict["signals"] != loose["signals"]
    for doc in (strict, loose):
        assert doc["trend_state"]["defense_line"]["type"] == "reaction_high"
        assert doc["trend_state"]["defense_line"]["agent_defined"] is True


def test_defense_break_fixture_suspect_before_counter_swing() -> None:
    """Cut right after the break: strict mode is BULL_SUSPECT and keeps the broken line."""
    doc = doc_of(run("--strict", "--end", "2021-05-05", csv=BREAK_FIXTURE))
    assert [s["kind"] for s in doc["signals"]][-1] == "DEFENSE_BREAK"
    assert doc["trend_state"]["primary"] == "BULL_SUSPECT"
    assert doc["trend_state"]["since"] == "2021-04-13"
    assert doc["trend_state"]["defense_line"]["price"] == 108.0


@pytest.mark.skipif(not clickhouse_available(), reason="ClickHouse not reachable")
def test_dji_since_2015_matches_skill_example() -> None:
    doc = doc_of(run("--symbol", "^DJI", "--start", "2015-01-01", "--end", "2026-11-06", csv=None))
    by_kind = {(s["ts"], s["kind"]) for s in doc["signals"]}
    assert ("2018-12-19", "DEFENSE_BREAK") in by_kind
    assert ("2020-04-08", "DEFENSE_BREAK") in by_kind
    assert ("2023-06-15", "REVERSAL_UP") in by_kind
    assert doc["trend_state"]["primary"] == "BULL_PRIMARY"
    assert doc["trend_state"]["since"] == "2023-06-15"
    assert round(doc["trend_state"]["defense_line"]["price"], 2) == 45166.64
