"""Analysis result container and its JSON form (see docs/specs/algorithm_contract.md)."""

from __future__ import annotations

import datetime as dt
import json
from dataclasses import dataclass, field
from decimal import Decimal
from typing import Any

import pandas as pd

STATUS_LABELS: dict[str, str] = {
    "defense_line": "agent-defined",
    "secondary_duration_bounds": "literature-disputed",
    "secondary_retracement": "literature-disputed",
    "rhea_3pct_filter": "single-source",
    "secondary_pct_threshold": "agent-defined",
    "line_definition": "literature-consensus",
    "two_average_confirmation": "literature-consensus",
}


def jsonable(obj: Any) -> Any:
    """Recursively convert Decimal to float and dates to ISO strings."""
    if isinstance(obj, Decimal):
        return float(obj)
    if isinstance(obj, (dt.datetime, pd.Timestamp)):
        return obj.date().isoformat()
    if isinstance(obj, dt.date):
        return obj.isoformat()
    if isinstance(obj, dict):
        return {str(k): jsonable(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [jsonable(v) for v in obj]
    if hasattr(obj, "item") and callable(obj.item):  # numpy scalars
        return jsonable(obj.item())
    return obj


@dataclass
class AnalysisResult:
    """In-memory analysis output; sections hold native types (Decimal, date).

    Section layout follows the contract JSON: ``meta``, ``trend_state``, ``swings``,
    ``levels`` (``support``, ``resistance``, ``trendlines``), ``lines``, ``signals`` and
    ``status_labels``.
    """

    meta: dict[str, Any]
    trend_state: dict[str, Any]
    swings: list[dict[str, Any]] = field(default_factory=list)
    levels: dict[str, list[dict[str, Any]]] = field(
        default_factory=lambda: {"support": [], "resistance": [], "trendlines": []}
    )
    lines: list[dict[str, Any]] = field(default_factory=list)
    signals: list[dict[str, Any]] = field(default_factory=list)
    status_labels: dict[str, str] = field(default_factory=lambda: dict(STATUS_LABELS))

    def to_dict(self) -> dict[str, Any]:
        """JSON-ready dict: Decimal -> float, dates -> ISO strings."""
        return jsonable(
            {
                "meta": self.meta,
                "trend_state": self.trend_state,
                "swings": self.swings,
                "levels": self.levels,
                "lines": self.lines,
                "signals": self.signals,
                "status_labels": self.status_labels,
            }
        )

    def to_json(self, indent: int | None = 2) -> str:
        """Serialise ``to_dict()`` as JSON text."""
        return json.dumps(self.to_dict(), indent=indent)
