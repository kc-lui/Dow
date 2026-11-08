"""Write an analysis into the ``dow.str_*`` log tables."""

from __future__ import annotations

import datetime as dt
from decimal import Decimal

import pandas as pd

from dowtheory.schema import AnalysisResult
from dowtheory.storage.clickhouse_client import ClickHouseClient

NY_TZ = "America/New_York"
_ZERO = Decimal(0)


def _dec(value: object, places: int = 4) -> Decimal:
    return Decimal(str(value if value is not None else 0)).quantize(Decimal(1).scaleb(-places))


def _ts(date: dt.date | pd.Timestamp) -> pd.Timestamp:
    """Session close time (16:00 New York) for a session date."""
    return (pd.Timestamp(date).normalize() + pd.Timedelta(hours=16)).tz_localize(NY_TZ)


def swing_frame(result: AnalysisResult) -> pd.DataFrame:
    """Rows for ``dow.str_swing_log``."""
    m = result.meta
    th = m["thresholds"]
    rows = [
        {
            "run_id": m["run_id"], "symbol": m["symbol"], "method": m["swing_method"],
            "threshold": _dec(th["minor_pct"] if s["scale"] == "minor" else th["secondary_pct"]),
            "scale": s["scale"], "kind": s["kind"], "ts": _ts(s["ts"]), "price": _dec(s["price"]),
            "confirmed_ts": _ts(s["confirmed_ts"]), "amplitude_pct": _dec(s["amplitude_pct"]),
            "retrace_ratio": _dec(s["retrace_ratio"]), "duration_days": int(s["duration_days"]),
        }
        for s in result.swings
    ]
    return pd.DataFrame(rows)


def state_frame(result: AnalysisResult) -> pd.DataFrame:
    """One row for ``dow.str_trend_state_snapshots`` (payload = full JSON)."""
    m, ts = result.meta, result.trend_state
    dl = ts.get("defense_line")
    return pd.DataFrame([{
        "run_id": m["run_id"], "symbol": m["symbol"], "pair_symbol": m.get("pair") or "",
        "ts": _ts(m["as_of"]), "primary_state": ts["primary"],
        "secondary_direction": ts["secondary_direction"],
        "confirmation_status": ts["confirmation"]["status"],
        "defense_line": _dec(dl["price"]) if dl else _ZERO,
        "volume_confirms": 1 if ts.get("volume_confirms") else 0,
        "payload": result.to_json(indent=None),
    }])


def level_frame(result: AnalysisResult) -> pd.DataFrame:
    """Rows for ``dow.str_level_log`` (support, resistance, trendlines, defense)."""
    m = result.meta
    ts = _ts(m["as_of"])
    base = {"run_id": m["run_id"], "symbol": m["symbol"], "ts": ts}
    rows = []
    for kind in ("support", "resistance"):
        for lv in result.levels[kind]:
            rows.append({**base, "level_type": kind, "price": _dec(lv["price"]),
                         "zone_low": _dec(lv["zone_low"]), "zone_high": _dec(lv["zone_high"]),
                         "touches": int(lv["touches"]), "slope_per_day": _ZERO})
    for tl in result.levels["trendlines"]:
        price = _dec(tl["value_at_as_of"])
        rows.append({**base, "level_type": f"trendline_{tl['kind']}", "price": price,
                     "zone_low": price, "zone_high": price, "touches": int(tl["touches"]),
                     "slope_per_day": _dec(tl["slope_per_day"], 6)})
    dl = result.trend_state.get("defense_line")
    if dl:
        price = _dec(dl["price"])
        rows.append({**base, "level_type": "defense", "price": price, "zone_low": price,
                     "zone_high": price, "touches": 1, "slope_per_day": _ZERO})
    return pd.DataFrame(rows)


def persist(result: AnalysisResult, client: ClickHouseClient) -> dict[str, int]:
    """Insert the result into the three log tables; returns rows written per table.

    Empty frames (e.g. no levels) are skipped rather than inserted.
    """
    written: dict[str, int] = {}
    for table, frame in (
        ("dow.str_swing_log", swing_frame(result)),
        ("dow.str_trend_state_snapshots", state_frame(result)),
        ("dow.str_level_log", level_frame(result)),
    ):
        written[table] = client.insert_df(table, frame) if not frame.empty else 0
    return written


__all__ = ["level_frame", "persist", "state_frame", "swing_frame"]
