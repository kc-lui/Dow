import json
from pathlib import Path

import pytest

from dowtheory.analysis import analyze
from dowtheory.cli import main
from dowtheory.config import load_config
from dowtheory.report import to_markdown

FIXTURE = Path(__file__).parent.parent / "fixtures" / "dji_sample.csv"


@pytest.fixture(scope="module")
def run():
    return analyze("^DJI", "^DJT", source="csv", csv_path=FIXTURE, csv_pair_path=FIXTURE,
                   cfg=load_config())


def test_json_keys_per_contract(run):
    result, df, df_pair = run
    data = json.loads(result.to_json())
    assert set(data) == {"meta", "trend_state", "swings", "levels", "lines", "signals",
                         "status_labels"}
    assert {"symbol", "pair", "as_of", "config_hash", "swing_method", "thresholds",
            "run_id"} <= set(data["meta"])
    assert {"primary", "since", "secondary_direction", "confirmation", "defense_line",
            "volume_confirms"} <= set(data["trend_state"])
    assert {"pair_state", "status", "detail"} == set(data["trend_state"]["confirmation"])
    assert set(data["levels"]) == {"support", "resistance", "trendlines"}
    assert data["status_labels"]["defense_line"] == "agent-defined"
    assert len(df) == len(df_pair)


def test_defense_line_is_agent_defined(run):
    result, _, _ = run
    dl = result.trend_state["defense_line"]
    if dl is not None:
        assert dl["agent_defined"] is True


def test_same_series_as_pair_is_confirmed_or_pending(run):
    result, _, _ = run
    assert result.trend_state["confirmation"]["status"] in {"confirmed", "pending"}


def test_markdown_mentions_agent_defined(run):
    assert "agent-defined" in to_markdown(run[0])


def test_cli_analyze_writes_outputs(tmp_path, capsys):
    out = tmp_path / "charts"
    rc = main(["analyze", "--symbol", "^DJI", "--pair", "^DJT", "--source", "csv",
               "--csv", str(FIXTURE), "--csv-pair", str(FIXTURE), "--out-dir", str(out)])
    assert rc == 0
    assert list(out.glob("*.png")) and list((tmp_path / "json").glob("*.json"))
    assert "Dow analysis" in capsys.readouterr().out
