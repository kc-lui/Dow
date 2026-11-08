import pytest
import yaml

from dowtheory.config import load_config, load_pairs


def test_load_defaults_match_yaml():
    cfg = load_config()
    assert cfg.data.symbols == ["^DJI", "^DJT", "^GSPC", "^IXIC", "SPY", "IYT"]
    assert cfg.data.exchange_map["SPY"] == "NYSEARCA"
    assert cfg.swings.minor_pct == 0.03
    assert cfg.confirmation.max_days is None
    assert cfg.backtest.horizons_days == [20, 60, 120]


def test_hash_is_stable_and_sensitive():
    assert load_config().config_hash() == load_config().config_hash()
    assert len(load_config().config_hash()) == 64
    changed = load_config()
    object.__setattr__(changed.swings, "minor_pct", 0.04)
    assert changed.config_hash() != load_config().config_hash()


def test_env_override_and_unknown_key(tmp_path, monkeypatch):
    path = tmp_path / "c.yaml"
    path.write_text(yaml.safe_dump({"swings": {"minor_pct": 0.05}}))
    monkeypatch.setenv("DOW_CONFIG", str(path))
    cfg = load_config()
    assert cfg.swings.minor_pct == 0.05
    assert cfg.config_hash() != load_config("configs/dow.yaml").config_hash()
    path.write_text(yaml.safe_dump({"swings": {"bogus": 1}}))
    with pytest.raises(ValueError):
        load_config()


def test_pairs():
    assert load_pairs()["DJ"] == ["^DJI", "^DJT"]


def test_analysis_start_map():
    start = load_config().data.analysis_start
    assert start["^GSPC"] == "1962-07-02" and start["^IXIC"] == "1984-10-11" and start["^DJI"] is None
