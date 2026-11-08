"""Typed configuration loaded from ``configs/dow.yaml`` (and ``configs/pairs.yaml``)."""

from __future__ import annotations

import hashlib
import json
import os
from dataclasses import asdict, dataclass, field, fields
from pathlib import Path
from typing import Any

import yaml

CONFIG_ENV = "DOW_CONFIG"


def project_root() -> Path:
    """Return the repository root (parent of ``src``) when run from a checkout."""
    return Path(__file__).resolve().parents[2]


def default_config_path() -> Path:
    """Locate ``configs/dow.yaml``: ``$DOW_CONFIG``, then the checkout, then the cwd."""
    env = os.environ.get(CONFIG_ENV)
    if env:
        return Path(env)
    checkout = project_root() / "configs" / "dow.yaml"
    return checkout if checkout.exists() else Path.cwd() / "configs" / "dow.yaml"


@dataclass(frozen=True)
class DataConfig:
    symbols: list[str] = field(default_factory=list)
    exchange_map: dict[str, str] = field(default_factory=dict)
    interval: str = "1d"
    stale_business_days: int = 5
    max_gap_business_days: int = 4
    analysis_start: dict[str, str | None] = field(default_factory=dict)


@dataclass(frozen=True)
class SwingConfig:
    method: str = "pct"
    minor_pct: float = 0.03
    secondary_pct: float = 0.10
    atr_window: int = 14
    atr_mult: float = 2.0
    pivot_n: int = 5
    secondary_min_days: int = 21
    secondary_max_days: int = 90
    schannep_min_days: int = 8
    schannep_min_pct: float = 0.03


@dataclass(frozen=True)
class TrendConfig:
    require_lower_high_for_reversal: bool = True


@dataclass(frozen=True)
class LineConfig:
    band_pct: float = 0.05
    min_days: int = 14


@dataclass(frozen=True)
class ConfirmationConfig:
    max_days: int | None = None


@dataclass(frozen=True)
class LevelsConfig:
    tol_mode: str = "pct"
    tol_pct: float = 0.0075
    tol_atr_mult: float = 0.5
    min_touches: int = 2
    max_levels: int = 4
    trendline_tol_pct: float = 0.01


@dataclass(frozen=True)
class BacktestConfig:
    min_n: int = 30
    bootstrap_iter: int = 2000
    block_len: int = 20
    horizons_days: list[int] = field(default_factory=lambda: [20, 60, 120])
    alpha: float = 0.05


@dataclass(frozen=True)
class DowConfig:
    data: DataConfig = field(default_factory=DataConfig)
    swings: SwingConfig = field(default_factory=SwingConfig)
    trend: TrendConfig = field(default_factory=TrendConfig)
    line: LineConfig = field(default_factory=LineConfig)
    confirmation: ConfirmationConfig = field(default_factory=ConfirmationConfig)
    levels: LevelsConfig = field(default_factory=LevelsConfig)
    backtest: BacktestConfig = field(default_factory=BacktestConfig)

    def to_dict(self) -> dict[str, Any]:
        """Return a plain nested dict (the YAML structure)."""
        return asdict(self)

    def config_hash(self) -> str:
        """SHA-256 of the canonical (sorted-key JSON) dump of the configuration."""
        canonical = json.dumps(self.to_dict(), sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def _build(cls: type, raw: dict[str, Any] | None, section: str) -> Any:
    """Instantiate a section dataclass, rejecting unknown keys (typos must not pass)."""
    raw = raw or {}
    known = {f.name for f in fields(cls)}
    unknown = set(raw) - known
    if unknown:
        raise ValueError(f"Unknown keys in config section '{section}': {sorted(unknown)}")
    return cls(**raw)


def load_config(path: str | Path | None = None) -> DowConfig:
    """Load the configuration from ``path`` (default: ``$DOW_CONFIG`` or ``configs/dow.yaml``)."""
    cfg_path = Path(path) if path else default_config_path()
    with cfg_path.open(encoding="utf-8") as fh:
        raw = yaml.safe_load(fh) or {}
    unknown = set(raw) - {f.name for f in fields(DowConfig)}
    if unknown:
        raise ValueError(f"Unknown top-level config sections: {sorted(unknown)}")
    return DowConfig(
        **{f.name: _build(f.default_factory, raw.get(f.name), f.name) for f in fields(DowConfig)}
    )


def config_hash(path: str | Path | None = None) -> str:
    """Hash of the configuration loaded from ``path``."""
    return load_config(path).config_hash()


def load_pairs(path: str | Path | None = None) -> dict[str, list[str]]:
    """Load index pairs (name -> [symbol_a, symbol_b]) from ``configs/pairs.yaml``."""
    pairs_path = Path(path) if path else default_config_path().with_name("pairs.yaml")
    with pairs_path.open(encoding="utf-8") as fh:
        return yaml.safe_load(fh) or {}
