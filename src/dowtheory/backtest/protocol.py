"""Constants of the pre-registered decision table (``analysis/decision_table.md``).

Everything fixed by the protocol lives here so that the rule code never hard-codes it.
Values that the protocol takes from ``configs/dow.yaml`` (``min_n``, iterations, block
length, horizons) are read from the config at construction time.
"""

from __future__ import annotations

import datetime as dt
import hashlib
import re
from dataclasses import dataclass, field
from pathlib import Path

from dowtheory.config import DowConfig, project_root

FAMILY: tuple[str, ...] = ("R1", "R2", "R3", "R4", "R5", "R6", "R7", "R8")
RULE_KEY: dict[str, str] = {
    "R1": "trend_persistence",
    "R2": "primary_reversal_signal",
    "R3": "two_average_confirmation",
    "R4": "secondary_retracement",
    "R5": "secondary_duration",
    "R6": "line_breakout",
    "R7": "volume_confirmation",
    "R8": "hamilton_timing",
}
SEED = 20261108
MIN_N_GROUP = 10
PERIOD_END = dt.date(2026, 11, 6)
R7_START = dt.date(2000, 1, 3)
PRIMARY_HORIZON: dict[str, int] = {"R2": 60, "R3": 60, "R6": 20}
COST_PRIMARY = 0.0010
TRADING_DAYS = 252
SHARPE_BLOCK_NOTE = "stationary block bootstrap, joint indices"
# Retracement band as quantised by the swing module (ratio is stored to 6 dp).
BAND_LO, BAND_HI, HALF = 0.333333, 0.666667, 0.5
WORST_GRID_RULES: frozenset[str] = frozenset({"R4", "R5"})  # section 1.8
GRID_SECONDARY_PCT: tuple[float, ...] = (0.05, 0.06, 0.08, 0.10, 0.12)  # with the 15-session filter
SWEEP_SESSIONS: tuple[int, ...] = (0, 15)
SWEEP_MINOR_PCT: tuple[float, ...] = (0.02, 0.03, 0.05)
SWEEP_EQUAL_TOL: tuple[float, ...] = (0.0, 0.005)
DJT_OVERRIDE = {"^DJT": 0.12}
LINE_BANDS: tuple[float, ...] = (0.03, 0.05, 0.07)
LINE_MIN_SESSIONS: tuple[int, ...] = (10, 15, 28)
LINE_DRIFT: tuple[float | None, ...] = (0.5, None)

BGK_CAVEAT = (
    "The 1992-2026 DJI/DJT sample cannot replicate Brown, Goetzmann and Kumar's 1902-1929 "
    "reconstruction of Hamilton's 255 editorials (110 right, 74 wrong, 71 neutral). Our calls "
    "are produced by a mechanical state machine, not by Hamilton's judgement, on a different "
    "century of data. Any comparison with 110/74 is descriptive and carries no label."
)
SCOPE_MARKER = "PROTOCOL-HASH-SCOPE"


@dataclass(frozen=True)
class Protocol:
    """Protocol constants plus the config-derived numbers the statistics need."""

    min_n: int
    n_iter: int
    block_len: int
    horizons: tuple[int, ...]
    alpha: float
    seed: int = SEED
    min_group: int = MIN_N_GROUP
    family: tuple[str, ...] = FAMILY
    period_end: dt.date = PERIOD_END
    r7_start: dt.date = R7_START
    table_hash: str = ""
    table_hash_scoped: str = ""
    history: str = field(default="", compare=False)

    @property
    def bonferroni_level(self) -> float:
        """One-sided confidence level of the refutation bound: ``1 - alpha / |family|``."""
        return 1.0 - self.alpha / len(self.family)


def committed_config_hash(table_text: str) -> str | None:
    """The config hash pinned in section 0 of the table (``None`` if the table has none)."""
    m = re.search(r"committed file, which at the time of writing is `([0-9a-f]{64})`", table_text)
    return m.group(1) if m else None


def coverage_caveats(table_text: str) -> list[str]:
    """Bullets of section 5 (data-coverage caveats), verbatim from the table."""
    m = re.search(r"^## 5\..*?$(.*?)^---\s*$", table_text, flags=re.DOTALL | re.MULTILINE)
    if not m:
        return []
    items: list[str] = []
    for line in m.group(1).splitlines():
        if line.startswith("- "):
            items.append(line[2:].strip())
        elif line.startswith("  ") and items and line.strip():
            items[-1] += " " + line.strip()
    return items


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def scoped_sha256(path: Path) -> str:
    """Hash of the text above the ``PROTOCOL-HASH-SCOPE`` line (as the table defines it)."""
    text = path.read_text(encoding="utf-8")
    cut = text.find(SCOPE_MARKER)
    if cut < 0:
        raise ValueError(f"{path}: no {SCOPE_MARKER} line")
    cut = text.rfind("\n", 0, cut) + 1
    return hashlib.sha256(text[:cut].encode("utf-8")).hexdigest()


def protocol_paths(root: Path | None = None) -> tuple[Path, Path]:
    base = root or project_root()
    return base / "analysis" / "decision_table.md", base / "analysis" / "decision_table.sha256"


def read_stored_hashes(hash_file: Path) -> list[str]:
    """First hex token of every non-empty line in ``decision_table.sha256``."""
    out = []
    for line in hash_file.read_text(encoding="utf-8").splitlines():
        m = re.match(r"\s*([0-9a-f]{64})\b", line)
        if m:
            out.append(m.group(1))
    return out


def load_protocol(cfg: DowConfig, root: Path | None = None, *, verify: bool = True) -> Protocol:
    """Build the protocol, checking the stored hash against the table on disk.

    Raises:
        ValueError: when ``verify`` and the stored hash matches neither the whole file nor
            the scoped text, i.e. the table changed after it was hashed.
    """
    table, hash_file = protocol_paths(root)
    whole = scoped = ""
    history = ""
    if table.exists():
        whole, scoped = sha256_file(table), scoped_sha256(table)
        history = table.read_text(encoding="utf-8")
    if verify and hash_file.exists():
        stored = read_stored_hashes(hash_file)
        if stored and not ({whole, scoped} & set(stored)):
            raise ValueError(
                f"{hash_file} does not match {table}: stored {stored[:2]}, "
                f"computed {whole} / {scoped}. The protocol changed after it was hashed."
            )
    bt = cfg.backtest
    return Protocol(
        min_n=bt.min_n, n_iter=bt.bootstrap_iter, block_len=bt.block_len,
        horizons=tuple(bt.horizons_days), alpha=bt.alpha, table_hash=whole,
        table_hash_scoped=scoped, history=history,
    )


def printed_caveats(table_text: str) -> dict[str, list[str]]:
    """Rule-level caveats the table says must be printed (``Mechanical caveat`` rows)."""
    out: dict[str, list[str]] = {}
    rule = ""
    for line in table_text.splitlines():
        m = re.match(r"^### (R\d)\b", line)
        if m:
            rule = m.group(1)
        elif rule and re.match(r"^\| (Mechanical|Explicit) caveat", line):
            cells = [c.strip() for c in line.strip().strip("|").split("|", 1)]
            out.setdefault(rule, []).append(cells[1].strip().strip('"'))
    return out
