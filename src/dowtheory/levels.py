"""Support/resistance clusters, trendlines and the (agent-defined) defense line.

Prices are ``Decimal`` internally. All inputs are expected to be confirmed swings only
(no lookahead); this module never looks at bars after the last supplied close.
"""

from __future__ import annotations

import datetime as dt
from collections.abc import Sequence
from dataclasses import dataclass, field
from decimal import Decimal
from typing import TYPE_CHECKING, Any, Literal

import pandas as pd

if TYPE_CHECKING:
    from dowtheory.swings import Swing
    from dowtheory.trend import TrendState

_SUPPORT_KINDS = {"L", "support"}
_RESISTANCE_KINDS = {"H", "resistance"}


def _dec(value: float | str | Decimal) -> Decimal:
    """Convert to Decimal without binary-float noise."""
    return value if isinstance(value, Decimal) else Decimal(str(value))


@dataclass(frozen=True)
class Level:
    """A horizontal support/resistance zone built from clustered swing prices."""

    price: Decimal
    zone_low: Decimal
    zone_high: Decimal
    touches: int
    members: list[dt.date] = field(default_factory=list)


@dataclass(frozen=True)
class TrendLine:
    """A straight line through two swing points, extended to the evaluation date."""

    kind: Literal["up", "down"]
    p0: tuple[dt.date, Decimal]
    p1: tuple[dt.date, Decimal]
    slope_per_day: Decimal
    touches: int
    valid: bool

    def value_at(self, date: dt.date) -> Decimal:
        """Line price at ``date`` (linear in calendar days)."""
        return self.p0[1] + self.slope_per_day * (date - self.p0[0]).days


def cluster_levels(
    swings: Sequence[Swing],
    kind: str,
    tol_mode: Literal["pct", "atr"] = "pct",
    tol_pct: float = 0.0075,
    tol_atr_mult: float = 0.5,
    atr: float | None = None,
    min_touches: int = 2,
    max_levels: int = 4,
    ref_price: Decimal | float | None = None,
    side_filter: bool = False,
) -> list[Level]:
    """Cluster swing prices of one kind into support (``L``) or resistance (``H``) zones.

    Prices are sorted and grouped greedily: a swing joins the open cluster while it lies
    within the tolerance of the cluster mean. Tolerance is ``tol_pct`` of the price, or
    ``tol_atr_mult * atr`` when ``tol_mode == "atr"`` and ``atr`` is given. The zone spans
    the members' min/max, widened to at least +/- tolerance/2 around the mean so that it is
    visible. Clusters with fewer than ``min_touches`` members are dropped. The ``max_levels``
    clusters closest to ``ref_price`` are kept (most touches first when no reference).
    With ``side_filter`` (needs ``ref_price``) only swing highs at or above the reference
    (resistance) or swing lows at or below it (support) are clustered, so resistance is
    never reported below the current price.

    Raises:
        ValueError: if ``kind`` is not one of ``H``/``L``/``resistance``/``support``.
    """
    if kind in _SUPPORT_KINDS:
        wanted = "L"
    elif kind in _RESISTANCE_KINDS:
        wanted = "H"
    else:
        raise ValueError(f"kind must be H/L/support/resistance, got {kind!r}")

    if side_filter and ref_price is None:
        raise ValueError("side_filter requires ref_price")
    ref = _dec(ref_price) if ref_price is not None else None

    def on_side(price: Decimal) -> bool:
        if not side_filter or ref is None:
            return True
        return price >= ref if wanted == "H" else price <= ref

    pts = sorted(
        ((s.price, s.ts) for s in swings if s.kind == wanted and on_side(s.price)),
        key=lambda p: p[0],
    )
    if not pts:
        return []

    def tolerance(price: Decimal) -> Decimal:
        if tol_mode == "atr" and atr is not None:
            return _dec(tol_atr_mult) * _dec(atr)
        return price * _dec(tol_pct)

    groups: list[list[tuple[Decimal, dt.date]]] = [[pts[0]]]
    for pt in pts[1:]:
        group = groups[-1]
        mean = sum((p for p, _ in group), Decimal(0)) / len(group)
        if pt[0] - mean <= tolerance(mean):
            group.append(pt)
        else:
            groups.append([pt])

    levels: list[Level] = []
    for group in groups:
        if len(group) < min_touches:
            continue
        prices = [p for p, _ in group]
        mean = sum(prices, Decimal(0)) / len(prices)
        half = tolerance(mean) / 2
        levels.append(
            Level(
                price=mean,
                zone_low=min(min(prices), mean - half),
                zone_high=max(max(prices), mean + half),
                touches=len(group),
                members=sorted(d for _, d in group),
            )
        )

    if ref is not None:
        levels.sort(key=lambda lv: (abs(lv.price - ref), -lv.touches))
    else:
        levels.sort(key=lambda lv: (-lv.touches, lv.price))
    return levels[:max_levels]


def fit_trendlines(
    swings: Sequence[Swing],
    kind: Literal["up", "down"],
    closes: pd.Series,
    tol_pct: float = 0.01,
) -> list[TrendLine]:
    """Fit the trendline through the last two confirmed secondary HL (up) or LH (down).

    ``closes`` is a date-indexed series ending at the evaluation date. The line exists only
    when the two points really form a higher low (up) or lower high (down). It is ``valid``
    when no close between the first point and the last close violates it by more than
    ``tol_pct`` (below the line for ``up``, above it for ``down``). ``touches`` counts swing
    points of the same kind within ``tol_pct`` of the line (including the two anchors).

    Returns a list with zero or one line.
    """
    if kind not in ("up", "down"):
        raise ValueError(f"kind must be 'up' or 'down', got {kind!r}")
    wanted = "L" if kind == "up" else "H"
    pts = sorted((s for s in swings if s.kind == wanted), key=lambda s: s.idx)
    if len(pts) < 2:
        return []
    a, b = pts[-2], pts[-1]
    if (kind == "up" and b.price <= a.price) or (kind == "down" and b.price >= a.price):
        return []
    days = (b.ts - a.ts).days
    if days <= 0:
        return []
    slope = (b.price - a.price) / days
    tol = _dec(tol_pct)

    def line_at(date: dt.date) -> Decimal:
        return a.price + slope * (date - a.ts).days

    window = closes[closes.index >= pd.Timestamp(a.ts)]
    valid = True
    for ts, close in window.items():
        level = line_at(ts.date())
        diff = _dec(float(close)) - level
        if (kind == "up" and diff < -abs(level) * tol) or (
            kind == "down" and diff > abs(level) * tol
        ):
            valid = False
            break
    touches = sum(
        1 for s in pts if s.ts >= a.ts and abs(s.price - line_at(s.ts)) <= abs(line_at(s.ts)) * tol
    )
    return [
        TrendLine(
            kind=kind, p0=(a.ts, a.price), p1=(b.ts, b.price), slope_per_day=slope,
            touches=touches, valid=valid,
        )
    ]


def defense_line_from_state(state: TrendState) -> dict[str, Any] | None:
    """Return the state's defense line as a JSON-ready dict, always ``agent_defined``."""
    if state.defense_line is None:
        return None
    return {
        "price": state.defense_line,
        "ts": state.defense_line_ts,
        "type": state.defense_line_kind,
        "agent_defined": True,
    }
