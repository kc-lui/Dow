import dataclasses
import json
from pathlib import Path

import pytest

from dowtheory.backtest.ledger import ledger_frame
from dowtheory.backtest.protocol import BGK_CAVEAT, FAMILY
from dowtheory.backtest.reporting import write_outputs
from dowtheory.backtest.runner import base_notes, run_backtest
from dowtheory.cli import main
from dowtheory.config import load_config, project_root

FIXTURE = Path(__file__).parent.parent / "fixtures" / "dji_sample.csv"
LABELS = {"data-confirmed", "data-refuted", "insufficient-evidence"}


@pytest.fixture(scope="module")
def run():
    cfg = load_config()
    cfg = dataclasses.replace(cfg, backtest=dataclasses.replace(cfg.backtest, bootstrap_iter=100))
    return run_backtest(["DJ"], cfg=cfg, source="csv", csv=str(FIXTURE), csv_pair=str(FIXTURE),
                        sweeps=True, verify_config=False)


def test_every_rule_has_label_or_na(run):
    pr = run.pairs["DJ"]
    for r in FAMILY:
        assert pr.outcomes[r].primary.label in LABELS
        assert pr.labels[r]["label"] == pr.outcomes[r].primary.label
        assert all(row.label == "n/a" for row in pr.outcomes[r].rows)
        assert all(row.label == "n/a" for row in pr.sweep_rows[r])
    labelled = [x for x in pr.all_rows() if x.label != "n/a"]
    assert len(labelled) == len(FAMILY)


def test_outputs_exist_and_are_portable(run, tmp_path):
    status = tmp_path / "status.md"
    written = write_outputs(run, tmp_path / "reports", status)
    for r in FAMILY:
        text = (tmp_path / "reports" / f"rule_{r}.md").read_text(encoding="utf-8")
        assert "/Users/" not in text
        assert "## Caveats" in text and "Data coverage" in text
        assert "unresolved" in text or "literature-" in text
    r8 = (tmp_path / "reports" / "rule_R8.md").read_text(encoding="utf-8")
    assert BGK_CAVEAT in r8
    r4 = (tmp_path / "reports" / "rule_R4.md").read_text(encoding="utf-8")
    assert "Mechanical caveat" not in r4 and "rr >=" in r4
    assert any(p.name.startswith("backtest_run_") for p in written)
    table = status.read_text(encoding="utf-8")
    assert table.count("\n| R") == 8 and "/Users/" not in table
    data = json.loads(next(p for p in written if p.suffix == ".json").read_text(encoding="utf-8"))
    assert data["run_id"] == run.run_id and "DJ" in data["pairs"]


def test_ledger_rows_follow_convention(run):
    pr = run.pairs["DJ"]
    rows = [(r, run.literature[r.rule_id], "") for r in pr.all_rows()]
    frame = ledger_frame(rows, run.run_id, run.table_hash, base_notes(run))
    assert len(frame) == len(rows)
    assert set(frame["label"]) <= LABELS | {"n/a"}
    assert (frame["decision_table_hash"] == run.table_hash).all()
    names = frame["metric_name"]
    assert names.str.count(r"\|").eq(3).all()
    assert names.str.startswith("pct0.03/0.08f15|primary|").any()
    assert frame["notes"].str.contains("integrity=").all()
    assert (frame["config_hash"].str.len() == 64).all()
    primary = frame[frame["label"] != "n/a"]
    assert sorted(primary["rule_id"]) == sorted(FAMILY)
    assert primary["notes"].str.contains("p_holm=").all()


def test_cli_backtest_writes_files(tmp_path, capsys):
    status = tmp_path / "status.md"
    code = main([
        "backtest", "--pair", "DJ", "--source", "csv", "--csv", str(FIXTURE),
        "--csv-pair", str(FIXTURE), "--out", str(tmp_path / "out"), "--status-table", str(status),
        "--no-sweeps",
    ])
    assert code == 0
    assert status.exists()
    assert len(list((tmp_path / "out").glob("rule_R*.md"))) == 8
    assert "runtime" in capsys.readouterr().out


def test_config_hash_guard(run):
    cfg = load_config()
    changed = dataclasses.replace(cfg, backtest=dataclasses.replace(cfg.backtest, min_n=31))
    with pytest.raises(ValueError, match="committed value"):
        run_backtest(["DJ"], cfg=changed, source="csv", csv=str(FIXTURE), csv_pair=str(FIXTURE),
                     sweeps=False, root=project_root())
