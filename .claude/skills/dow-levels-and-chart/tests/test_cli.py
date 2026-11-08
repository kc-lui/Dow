"""Run ``scripts/draw.py`` on the project CSV fixture and (when reachable) on ClickHouse ^DJI/^DJT."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

SKILL = Path(__file__).resolve().parents[1]
ROOT = SKILL.parents[2]
SCRIPT = SKILL / "scripts" / "draw.py"
FIXTURE = ROOT / "tests" / "fixtures" / "dji_sample.csv"
LEVEL_KEYS = {"price", "zone_low", "zone_high", "touches"}
TRENDLINE_KEYS = {"kind", "p0", "p1", "slope_per_day", "touches", "valid", "value_at_as_of"}
MIN_PNG_BYTES = 10_000


def run(out_dir: Path, *extra: str, csv: Path | None = FIXTURE) -> subprocess.CompletedProcess:
    cmd = [sys.executable, str(SCRIPT), "--json", "--out-dir", str(out_dir / "charts"), *extra]
    if csv is not None:
        cmd += ["--source", "csv", "--csv", str(csv)]
    return subprocess.run(cmd, capture_output=True, text=True, cwd=ROOT, timeout=600, check=False)


def doc_of(proc: subprocess.CompletedProcess) -> dict:
    assert proc.returncode == 0, proc.stderr
    return json.loads(proc.stdout.strip().splitlines()[-1])


def last_close(csv: Path, as_of: str | None = None) -> float:
    sys.path.insert(0, str(ROOT / "src"))
    from dowtheory.data.loader import load_klines

    return float(load_klines(csv.stem, None, as_of, source="csv", csv_path=csv)["close"].iloc[-1])


def clickhouse_available() -> bool:
    sys.path.insert(0, str(ROOT / "src"))
    try:
        from dowtheory.storage.clickhouse_client import ClickHouseClient

        return ClickHouseClient().ping()
    except Exception:  # noqa: BLE001 - any failure means skip, not fail
        return False


def check_levels(doc: dict, close: float) -> None:
    """Shape of ``levels`` and the A8 side filter: resistance >= close >= support."""
    levels = doc["levels"]
    assert set(levels) == {"support", "resistance", "trendlines"}
    for kind in ("support", "resistance"):
        for lv in levels[kind]:
            assert set(lv) == LEVEL_KEYS and lv["touches"] >= 2
            assert lv["zone_low"] <= lv["price"] <= lv["zone_high"]
        assert len(levels[kind]) <= 4
    assert all(lv["price"] >= close for lv in levels["resistance"])
    assert all(lv["price"] <= close for lv in levels["support"])
    for tl in levels["trendlines"]:
        assert set(tl) == TRENDLINE_KEYS and tl["kind"] in {"up", "down"}
        assert tl["p0"][0] < tl["p1"][0] and tl["touches"] >= 2
    dl = doc["trend_state"].get("defense_line")
    if dl is not None:
        assert dl["agent_defined"] is True and set(dl) == {"price", "ts", "type", "agent_defined"}


def test_fixture_writes_png_json_and_markdown(tmp_path: Path) -> None:
    proc = run(tmp_path)
    doc = doc_of(proc)
    check_levels(doc, last_close(FIXTURE))
    pngs = list((tmp_path / "charts").glob("*.png"))
    assert len(pngs) == 1 and pngs[0].stat().st_size > MIN_PNG_BYTES
    assert pngs[0].name == "DJI_SAMPLE_DJI_SAMPLE_2021-02-24_pct0.03.png"
    jsons = list((tmp_path / "json").glob("*.json"))
    assert len(jsons) == 1 and jsons[0].stem == pngs[0].stem
    assert json.loads(jsons[0].read_text())["levels"] == doc["levels"]
    assert "## Levels" in proc.stdout and "Defense line [agent-defined]" in proc.stdout
    assert f"Chart: {pngs[0]}" in proc.stdout and f"JSON: {jsons[0]}" in proc.stdout
    assert doc["trend_state"]["defense_line"]["price"] == 28713.48
    assert [t["kind"] for t in doc["levels"]["trendlines"]] == ["down"]
    assert len(doc["levels"]["support"]) == 1 and len(doc["levels"]["resistance"]) == 3


def test_no_chart_writes_no_png(tmp_path: Path) -> None:
    proc = run(tmp_path, "--no-chart")
    doc = doc_of(proc)
    assert not (tmp_path / "charts").exists() or not list((tmp_path / "charts").glob("*.png"))
    assert len(list((tmp_path / "json").glob("*.json"))) == 1
    assert "Chart:" not in proc.stdout and doc["meta"]["symbol"] == "DJI_SAMPLE"


def test_as_of_side_filter_on_truncated_fixture(tmp_path: Path) -> None:
    """Cut at a different bar: zones re-sort around that bar's close, never across it."""
    as_of = "2020-12-31"
    doc = doc_of(run(tmp_path, "--as-of", as_of))
    assert doc["meta"]["as_of"] == as_of
    check_levels(doc, last_close(FIXTURE, as_of))
    assert len(list((tmp_path / "charts").glob(f"*_{as_of}_*.png"))) == 1


def test_missing_symbol_errors_cleanly(tmp_path: Path) -> None:
    proc = run(tmp_path, csv=None)
    assert proc.returncode == 2 and "--symbol is required" in proc.stderr


@pytest.mark.skipif(not clickhouse_available(), reason="ClickHouse not reachable")
def test_dji_djt_since_2015_matches_skill_example(tmp_path: Path) -> None:
    args = ("--symbol", "^DJI", "--pair", "^DJT", "--start", "2015-01-01", "--as-of", "2026-11-06")
    doc = doc_of(run(tmp_path, *args, csv=None))
    check_levels(doc, 51285.7305)
    levels = doc["levels"]
    assert [lv["touches"] for lv in levels["support"]] == [2, 2, 2, 3]
    assert [round(lv["price"]) for lv in levels["support"]] == [41851, 38141, 37690, 34009]
    assert levels["resistance"] == []
    assert doc["meta"]["levels_note"].startswith("fewer than 2 swing highs on the upper side")
    (tl,) = levels["trendlines"]
    assert (tl["kind"], tl["valid"], tl["p0"][0], tl["p1"][0]) == (
        "up",
        True,
        "2025-04-08",
        "2026-03-27",
    )
    assert doc["trend_state"]["defense_line"] == {
        "price": 45166.6406,
        "ts": "2026-03-27",
        "type": "reaction_low",
        "agent_defined": True,
    }
    png = tmp_path / "charts" / "DJI_DJT_2026-11-06_pct0.03.png"
    assert png.is_file() and png.stat().st_size > MIN_PNG_BYTES


def scaled_pair(tmp_path: Path, factor: float = 0.5) -> Path:
    """A second leg: the fixture with every price scaled, so the legs differ but share dates."""
    rows = FIXTURE.read_text().splitlines()
    out = [rows[0]]
    for row in rows[1:]:
        date, *prices, volume = row.split(",")
        out.append(",".join([date, *[f"{float(p) * factor:.2f}" for p in prices], volume]))
    path = tmp_path / "pair_half.csv"
    path.write_text("\n".join(out) + "\n")
    return path


def test_end_is_an_alias_of_as_of(tmp_path: Path) -> None:
    by_end = doc_of(run(tmp_path / "a", "--end", "2020-12-31"))
    by_as_of = doc_of(run(tmp_path / "b", "--as-of", "2020-12-31"))
    assert by_end["meta"]["as_of"] == by_as_of["meta"]["as_of"] == "2020-12-31"
    assert by_end["levels"] == by_as_of["levels"]
    assert by_end["trend_state"]["primary"] == by_as_of["trend_state"]["primary"]


def test_method_flag_changes_swings_and_filename(tmp_path: Path) -> None:
    doc = doc_of(run(tmp_path, "--method", "atr"))
    assert doc["meta"]["swing_method"] == "atr"
    check_levels(doc, last_close(FIXTURE))
    assert len(list((tmp_path / "charts").glob("*_atr0.03.png"))) == 1
    assert doc["levels"] != doc_of(run(tmp_path / "pct")).get("levels")


def test_distinct_csv_pair_is_a_real_second_leg(tmp_path: Path) -> None:
    pair = scaled_pair(tmp_path)
    doc = doc_of(run(tmp_path, "--csv-pair", str(pair)))
    assert (doc["meta"]["symbol"], doc["meta"]["pair"]) == ("DJI_SAMPLE", "PAIR_HALF")
    check_levels(doc, last_close(FIXTURE))
    assert doc["trend_state"]["confirmation"]["status"] == "confirmed"  # same shape, half scale
    png = tmp_path / "charts" / "DJI_SAMPLE_PAIR_HALF_2021-02-24_pct0.03.png"
    assert png.is_file() and png.stat().st_size > MIN_PNG_BYTES


def test_plain_stdout_is_markdown_then_paths(tmp_path: Path) -> None:
    cmd = [
        sys.executable,
        str(SCRIPT),
        "--source",
        "csv",
        "--csv",
        str(FIXTURE),
        "--out-dir",
        str(tmp_path / "charts"),
    ]
    proc = subprocess.run(cmd, capture_output=True, text=True, cwd=ROOT, timeout=600, check=False)
    assert proc.returncode == 0, proc.stderr
    lines = proc.stdout.strip().splitlines()
    assert lines[0] == "# Dow analysis: DJI_SAMPLE vs DJI_SAMPLE as of 2021-02-24"
    assert lines[-2].startswith("JSON: ") and lines[-1].startswith("Chart: ")
    assert not lines[-1].startswith("{") and "## Levels" in proc.stdout


@pytest.mark.parametrize(
    "extra",
    [("--csv", str(FIXTURE)), ("--source", "csv", "--symbol", "^DJI")],
)
def test_csv_and_source_must_be_given_together(tmp_path: Path, extra: tuple[str, ...]) -> None:
    proc = run(tmp_path, *extra, csv=None)
    assert proc.returncode == 2 and "must be given together" in proc.stderr
