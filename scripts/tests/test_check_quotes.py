"""Tests for scripts/check_quotes.py using fixture markdown under fixtures/."""

from pathlib import Path

import check_quotes
import pytest

FIX = Path(__file__).parent / "fixtures"
ROOT = FIX / "root"


def run(name: str, capsys: pytest.CaptureFixture[str]) -> tuple[int, str]:
    code = check_quotes.main(["--root", str(ROOT), str(FIX / "quotes" / name)])
    return code, capsys.readouterr().out


def test_pass(capsys):
    code, out = run("pass.md", capsys)
    assert code == 0
    assert out.strip() == "ALL CLEAN"


@pytest.mark.parametrize(
    ("name", "kind", "fragment"),
    [
        ("no_citation.md", "no-citation", "The market is always"),
        ("unknown_slug.md", "bad-quote", "unknown source slug 'ghost-src'"),
        ("not_substring.md", "bad-quote", "not a verbatim substring"),
        ("missing_qid.md", "bad-quote", "cited quote id not found: demo-src:Q9"),
        ("wrong_case.md", "bad-quote", "not a verbatim substring"),
        ("cite_on_other_line.md", "no-citation", "The market is always"),
    ],
)
def test_failures(name, kind, fragment, capsys):
    code, out = run(name, capsys)
    assert code == 1
    assert kind in out
    assert fragment in out
    assert f"{name}:1" in out


def test_default_globs_in_root(tmp_path, capsys):
    (tmp_path / "research" / "sources").mkdir(parents=True)
    (tmp_path / "analysis").mkdir()
    (tmp_path / "analysis" / "a.md").write_text('He said "one two three four five" here.\n')
    assert check_quotes.main(["--root", str(tmp_path)]) == 1
    assert "analysis/a.md:1" in capsys.readouterr().out


def test_canonical_rules_not_in_default_scan():
    assert not any("canonical_rules" in g for g in check_quotes.DEFAULT_GLOBS)


def test_missing_path_raises():
    with pytest.raises(FileNotFoundError):
        check_quotes.main(["--root", str(ROOT), str(FIX / "nope.md")])


def test_normalise_dashes_quotes_whitespace():
    assert check_quotes.normalise("a—b  “c”\n d") == 'a-b "c" d'
