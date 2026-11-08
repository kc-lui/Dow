"""Run ``scripts/swings.py`` on the CSV fixture for every method; check table and JSON."""

from __future__ import annotations

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
JSON_KEYS = {"ts", "kind", "price", "confirmed_ts", "scale", "amplitude_pct",
             "duration_days", "retrace_ratio", "flags"}


def run(*extra: str) -> subprocess.CompletedProcess:
    cmd = [sys.executable, str(SCRIPT), "--symbol", "^DJI", "--source", "csv",
           "--csv", str(FIXTURE), "--json", *extra]
    return subprocess.run(cmd, capture_output=True, text=True, cwd=ROOT, timeout=120, check=False)


def split(stdout: str) -> tuple[list[str], dict]:
    lines = stdout.strip().splitlines()
    table = [ln for ln in lines if ln.startswith("| 20")]
    return table, json.loads(lines[-1])


@pytest.mark.parametrize("method", ["pct", "atr", "pivot"])
def test_methods_alternate_and_emit_json(method: str) -> None:
    proc = run("--method", method)
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


def test_scale_filter_and_window() -> None:
    proc = run("--scale", "minor", "--start", "2020-06-01", "--end", "2020-12-31")
    assert proc.returncode == 0, proc.stderr
    table, doc = split(proc.stdout)
    assert table and all("| minor |" in ln for ln in table)
    assert all("2020-06-01" <= s["ts"] <= "2020-12-31" for s in doc["swings"])
