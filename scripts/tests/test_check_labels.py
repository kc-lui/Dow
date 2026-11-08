"""Tests for scripts/check_labels.py using fixture markdown under fixtures/."""

from pathlib import Path

import check_labels
import pytest

FIX = Path(__file__).parent / "fixtures"
ROOT = FIX / "root"


def run(name: str, capsys: pytest.CaptureFixture[str]) -> tuple[int, str]:
    code = check_labels.main(["--root", str(ROOT), str(FIX / "labels" / name)])
    return code, capsys.readouterr().out


def test_pass(capsys):
    code, out = run("pass.md", capsys)
    assert code == 0, out
    assert out.strip() == "ALL CLEAN"


def test_unlabelled_quantities(capsys):
    code, out = run("unlabelled.md", capsys)
    assert code == 1
    assert out.count("unlabelled-quantity") == 4  # line 3 splits on ";"
    for line in (1, 2, 3):
        assert f"unlabelled.md:{line}" in out


def test_unknown_rule_id(capsys):
    code, out = run("unknown_id.md", capsys)
    assert code == 1
    assert "unknown-rule-id" in out
    assert "R-099" in out


def test_label_mismatch(capsys):
    code, out = run("mismatch.md", capsys)
    assert code == 1
    assert out.count("label-mismatch") == 2
    assert "mismatch.md:1" in out
    assert "mismatch.md:3" in out
    assert "mismatch.md:2" not in out  # single-source (one) normalises to single-source


def test_table_row_unlabelled(capsys):
    code, out = run("table_unlabelled.md", capsys)
    assert code == 1
    assert "table_unlabelled.md:3" in out


def test_registry_normalisation():
    reg = check_labels.load_registry(ROOT)
    assert reg == {
        "R-001": "literature-consensus",
        "R-002": "literature-disputed",
        "R-004": "single-source",
        "R-020": "agent-defined",
    }


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("lasts 30 days", True),
        ("a 2.5% band", True),
        ("3/8 of the move", True),
        ("Sharpe of 0.8", True),
        ("on 2026-11-08", False),
        ("in 1922", False),
        ("43 notes and 204 tests", False),
        ("see docs/3days/x.md", False),
        ("min_sessions 15 sessions", False),
        ("--window 20 days", False),
        ("alpha channel", False),
    ],
)
def test_has_rule_quantity(text, expected):
    assert check_labels.has_rule_quantity(text) is expected


def test_default_globs_empty_repo_is_clean(tmp_path, capsys):
    (tmp_path / "research").mkdir()
    (tmp_path / "research" / "canonical_rules.md").write_text("# none\n")
    assert check_labels.main(["--root", str(tmp_path)]) == 0
    assert capsys.readouterr().out.strip() == "ALL CLEAN"
