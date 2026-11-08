"""Run ``scripts/swings.py`` on the CSV fixture for every method; check table and JSON."""

from __future__ import annotations

import csv
import json
import subprocess
import sys
from itertools import pairwise
from pathlib import Path

import pytest

SKILL = Path(__file__).resolve().parents[1]
ROOT = SKILL.parents[2]
SCRIPT = SKILL / "scripts" / "swings.py"
FIXTURE = ROOT / "tests" / "fixtures" / "dji_sample.csv"
JSON_KEYS = {
    "ts",
    "kind",
    "price",
    "confirmed_ts",
    "scale",
    "amplitude_pct",
    "duration_days",
    "retrace_ratio",
    "flags",
    "snapped",
}
FLAG_KEYS = {
    "rhea_window",
    "schannep_window",
    "retrace_in_third_two_thirds",
    "retrace_in_third_half",
}
MIN_SESSIONS = 15  # configs/dow.yaml swings.secondary_min_sessions
EXAMPLE_1_COUNT = 20  # SKILL.md Example 1 summary line (pct, both scales)


def run(*extra: str) -> subprocess.CompletedProcess:
    cmd = [sys.executable, str(SCRIPT), "--source", "csv", "--csv", str(FIXTURE), "--json", *extra]
    return subprocess.run(cmd, capture_output=True, text=True, cwd=ROOT, timeout=120, check=False)


def split(stdout: str) -> tuple[list[str], dict]:
    lines = stdout.strip().splitlines()
    table = [ln for ln in lines if ln.startswith("| 20")]
    return table, json.loads(lines[-1])


def session_index() -> dict[str, int]:
    with FIXTURE.open() as fh:
        return {r["Date"]: i for i, r in enumerate(csv.DictReader(fh))}


@pytest.mark.parametrize("method", ["pct", "atr", "pivot"])
def test_methods_alternate_and_emit_json(method: str) -> None:
    proc = run("--symbol", "^DJI", "--method", method)
    assert proc.returncode == 0, proc.stderr
    table, doc = split(proc.stdout)
    assert len(table) >= 1 and doc["method"] == method and doc["swings"]
    for scale in ("minor", "secondary"):
        kinds = [ln.split("|")[2].strip() for ln in table if f"| {scale} |" in ln]
        assert all(a != b for a, b in pairwise(kinds)), f"{scale} does not alternate"
    for swing in doc["swings"]:
        assert set(swing) == JSON_KEYS
        assert swing["confirmed_ts"] >= swing["ts"]
    assert set(doc["thresholds"]) == {"minor_pct", "secondary_pct", "secondary_min_sessions"}


def test_secondary_metrics_flags_and_time_filter() -> None:
    proc = run("--method", "pct")  # no --symbol: defaults to the CSV stem
    assert proc.returncode == 0, proc.stderr
    table, doc = split(proc.stdout)
    assert doc["symbol"] == "DJI_SAMPLE" and len(table) == len(doc["swings"]) == EXAMPLE_1_COUNT
    minor = [s for s in doc["swings"] if s["scale"] == "minor"]
    secondary = [s for s in doc["swings"] if s["scale"] == "secondary"]
    assert minor and secondary
    assert all(s["flags"] == {} and s["snapped"] is None for s in minor)
    assert all(set(s["flags"]) == FLAG_KEYS and isinstance(s["snapped"], bool) for s in secondary)
    assert [s["retrace_ratio"] for s in secondary[:2]] == [None, None]
    assert all(s["retrace_ratio"] is not None for s in secondary[2:])
    idx = session_index()
    for prev, cur in pairwise(secondary):
        assert idx[cur["confirmed_ts"]] - idx[prev["ts"]] >= MIN_SESSIONS, (prev["ts"], cur["ts"])


def test_scale_filter_and_window() -> None:
    proc = run(
        "--symbol", "^DJI", "--scale", "minor", "--start", "2020-06-01", "--end", "2020-12-31"
    )
    assert proc.returncode == 0, proc.stderr
    table, doc = split(proc.stdout)
    assert table and all("| minor |" in ln for ln in table)
    assert all("2020-06-01" <= s["ts"] <= "2020-12-31" for s in doc["swings"])
