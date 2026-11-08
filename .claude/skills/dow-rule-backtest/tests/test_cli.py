"""Run ``scripts/rules.py`` against the committed status table, the run JSON and a CSV rerun."""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path

SKILL = Path(__file__).resolve().parents[1]
ROOT = SKILL.parents[2]
SCRIPT = SKILL / "scripts" / "rules.py"
TABLE = ROOT / "analysis" / "rule_status_table.md"
SHA_FILE = ROOT / "analysis" / "decision_table.sha256"
FIXTURE = ROOT / "tests" / "fixtures" / "dji_sample.csv"
RULES = [f"R{i}" for i in range(1, 9)]
DATA_LABELS = {"data-confirmed", "data-refuted", "insufficient-evidence"}
LIT_LABELS = {"literature-consensus", "literature-disputed", "single-source", "agent-defined"}
DOC_KEYS = {"run_id", "table", "decision_table_hash", "run_table_hash", "config_hash", "rules"}
ROW_KEYS = {
    "rule_id",
    "rule_key",
    "pair",
    "spec",
    "period",
    "data_label",
    "literature_label",
    "literature_ids",
    "n",
    "metric_name",
    "horizon",
    "estimate",
    "ci",
    "null_value",
    "p_raw",
    "p_holm",
    "subsample_signs",
    "refute_bound",
    "reason",
    "caveat",
    "flags",
    "exploratory",
    "notes",
}
CAVEAT_PHRASE = "the 0.5 null is not a random-walk baseline"


def run(*extra: str):
    cmd = [sys.executable, str(SCRIPT), *extra]
    return subprocess.run(cmd, capture_output=True, text=True, cwd=ROOT, timeout=600, check=False)


def doc_of(proc: subprocess.CompletedProcess) -> dict:
    assert proc.returncode == 0, proc.stderr
    return json.loads(proc.stdout.strip().splitlines()[-1])


def blocks(text: str) -> dict[str, str]:
    """Split the text output into one block per rule id."""
    out: dict[str, str] = {}
    for part in text.split("\n\n"):
        head = part.split(" ", 1)[0]
        if head in RULES:
            out[head] = part
    return out


def test_all_eight_rules_from_committed_table() -> None:
    proc = run()
    assert proc.returncode == 0, proc.stderr
    got = blocks(proc.stdout)
    assert sorted(got) == RULES
    for rule, block in got.items():
        label = block.split("data label: ", 1)[1].split(" |", 1)[0]
        lit = block.split("literature label: ", 1)[1].split(" (", 1)[0]
        assert label in DATA_LABELS, (rule, label)
        assert lit in LIT_LABELS, (rule, lit)
        assert "R-0" in block  # literature ids are printed
    assert "data label: data-confirmed" in got["R1"]
    assert CAVEAT_PHRASE in got["R1"] and "p_sim = 0.0055" in got["R1"]
    assert "0.65 to 0.69" in got["R1"] and "n = 33" in got["R1"]
    assert "decision_table_hash c8675eff2b28" in proc.stdout


def test_r7_is_insufficient_not_refuted() -> None:
    proc = run("--rule", "R7")
    assert proc.returncode == 0, proc.stderr
    got = blocks(proc.stdout)
    assert list(got) == ["R7"]
    assert "data label: insufficient-evidence" in got["R7"]
    assert "refutation bound 0.5162 vs null 0.5000 -> not refuted" in got["R7"]
    assert "n=57" in got["R7"] and "p_vol" in got["R7"]
    assert "2000-01-03..2026-11-06" in got["R7"]


def test_r3_marked_exploratory_and_r6_refutation_bound() -> None:
    got = blocks(run("--rule", "R3").stdout)
    assert "EXPLORATORY (DEV-11)" in got["R3"] and "n=15" in got["R3"]
    got = blocks(run("--rule", "R6").stdout)
    assert "refutation bound 0.5471 vs null 0.5000 -> not refuted" in got["R6"]
    assert "pair-inconsistent" in got["R6"]


def test_json_mode_keys_and_labels_match_table() -> None:
    doc = doc_of(run("--json"))
    assert set(doc) == DOC_KEYS
    assert doc["decision_table_hash"] == doc["run_table_hash"]
    assert [r["rule_id"] for r in doc["rules"]] == RULES
    for row in doc["rules"]:
        assert set(row) == ROW_KEYS
        assert row["pair"] == "DJ" and row["data_label"] in DATA_LABELS
        assert row["literature_label"] in LIT_LABELS and row["literature_ids"].startswith("R-0")
        assert len(row["ci"]) == 2 and isinstance(row["n"], int)
    by_id = {r["rule_id"]: r for r in doc["rules"]}
    assert by_id["R1"]["data_label"] == "data-confirmed"
    assert by_id["R1"]["caveat"] and CAVEAT_PHRASE in by_id["R1"]["caveat"]
    assert by_id["R1"]["n"] == 33 and by_id["R1"]["p_holm"] < 0.05
    assert by_id["R3"]["exploratory"] is True
    assert by_id["R8"]["n"] == 28 and by_id["R8"]["data_label"] == "insufficient-evidence"
    assert {r["data_label"] for r in doc["rules"] if r["rule_id"] != "R1"} == {
        "insufficient-evidence"
    }
    assert {"pair-inconsistent"} <= set(by_id["R2"]["flags"]) & set(by_id["R4"]["flags"])


def test_sp_iyt_rows_are_descriptive_only() -> None:
    doc = doc_of(run("--json", "--pair", "SP_IYT", "--rule", "R6"))
    (row,) = doc["rules"]
    assert row["pair"] == "SP_IYT"
    assert row["data_label"].startswith("n/a")
    assert row["p_holm"] is None and row["refute_bound"] is None
    assert row["period"] == "2004-01-02..2026-11-06" and row["n"] == 50


def test_table_hash_equals_sha256_line_one() -> None:
    stored = SHA_FILE.read_text(encoding="utf-8").splitlines()[0].split()[0]
    doc = doc_of(run("--json", "--rule", "R1"))
    assert doc["decision_table_hash"] == stored == doc["run_table_hash"]
    table = ROOT / "analysis" / "decision_table.md"
    assert hashlib.sha256(table.read_bytes()).hexdigest() == stored


def test_rerun_requires_out_dir() -> None:
    proc = run("--rerun")
    assert proc.returncode == 2 and "--rerun needs --out DIR" in proc.stderr


def test_rerun_on_csv_fixture_writes_only_into_out_dir(tmp_path: Path) -> None:
    """The wrapper reruns the harness on the fixture without touching the committed outputs."""
    before = hashlib.sha256(TABLE.read_bytes()).hexdigest()
    runs_before = sorted((ROOT / "reports").glob("backtest_run_*.json"))
    proc = run(
        "--rerun", "--out", str(tmp_path), "--source", "csv", "--csv", str(FIXTURE), "--no-sweeps"
    )
    assert proc.returncode == 0, proc.stderr
    assert "--persist" not in proc.stdout and "--status-table" in proc.stdout
    assert hashlib.sha256(TABLE.read_bytes()).hexdigest() == before
    assert sorted((ROOT / "reports").glob("backtest_run_*.json")) == runs_before
    for rule in RULES:
        assert (tmp_path / f"rule_{rule}.md").is_file()
    (run_json,) = tmp_path.glob("backtest_run_*.json")
    status = tmp_path / "rule_status_table.md"
    assert status.is_file()
    doc = doc_of(run("--json", "--table", str(status), "--run", str(run_json)))
    assert doc["decision_table_hash"] == doc["run_table_hash"]
    assert [r["rule_id"] for r in doc["rules"]] == RULES
    assert {r["data_label"] for r in doc["rules"]} == {"insufficient-evidence"}  # 300 bars
    assert all(r["reason"] == "n below minimum" for r in doc["rules"])
