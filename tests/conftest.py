"""Shared fixtures for swing-shaped test data."""

from __future__ import annotations

import datetime as dt
from collections.abc import Callable
from decimal import Decimal

import pytest

from dowtheory.swings import Swing

BASE = dt.date(2024, 1, 1)


@pytest.fixture
def make_swing() -> Callable[..., Swing]:
    """Factory: ``make_swing(idx, price, kind, scale="secondary")`` (1 bar = 1 calendar day)."""

    def _make(idx: int, price: float, kind: str, scale: str = "secondary") -> Swing:
        ts = BASE + dt.timedelta(days=idx)
        return Swing(
            idx=idx, ts=ts, price=Decimal(str(price)), kind=kind,  # type: ignore[arg-type]
            confirmed_idx=idx + 3, confirmed_ts=ts + dt.timedelta(days=3),
            scale=scale,  # type: ignore[arg-type]
            amplitude_pct=Decimal("0.1"), duration_days=10, retrace_ratio=None,
        )

    return _make
