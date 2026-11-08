"""Rows for ``dow.str_rule_backtest_log`` and the insert."""

from __future__ import annotations

import math
from decimal import ROUND_HALF_EVEN, Decimal

import pandas as pd

from dowtheory.backtest.results import RuleResult
from dowtheory.storage.clickhouse_client import ClickHouseClient

TABLE = "dow.str_rule_backtest_log"
_Q = Decimal("0.000001")
_MAX_12_6 = Decimal("999999.999999")
_MAX_8_6 = Decimal("99.999999")


def to_decimal(value: float, limit: Decimal = _MAX_12_6) -> tuple[Decimal, bool]:
    """Quantise to 6 dp; returns ``(value, was_missing)``. NaN and inf become 0 and are flagged."""
    if value is None or math.isnan(value) or math.isinf(value):
        return Decimal(0).quantize(_Q), True
    d = Decimal(repr(float(value))).quantize(_Q, rounding=ROUND_HALF_EVEN)
    if abs(d) > limit:
        raise ValueError(f"value {value} does not fit the column (|x| <= {limit})")
    return d, False


def ledger_frame(
    rows: list[tuple[RuleResult, str, str]], run_id: str, table_hash: str, base_notes: str,
) -> pd.DataFrame:
    """Frame for the insert. ``rows`` holds ``(result, literature_label, extra_notes)``.

    Missing numbers (NaN) are written as 0 and listed in ``notes`` as ``na=<fields>`` so a
    zero is never mistaken for a measurement.
    """
    out = []
    for r, lit, extra in rows:
        fields = {
            "metric_value": r.metric_value, "ci_low": r.ci_low, "ci_high": r.ci_high,
            "null_value": r.null_value,
        }
        dec: dict[str, Decimal] = {}
        missing: list[str] = []
        for name, val in fields.items():
            dec[name], miss = to_decimal(val)
            if miss:
                missing.append(name)
        p, p_miss = to_decimal(r.p_value, _MAX_8_6)
        if p_miss:
            missing.append("p_value")
        notes = "; ".join(
            x for x in (
                base_notes, f"clusters={r.n_clusters}" if r.n_clusters is not None else "",
                f"censored={r.n_censored}", r.notes, extra,
                f"na={','.join(missing)}" if missing else "",
            ) if x
        )
        out.append({
            "run_id": run_id, "rule_id": r.rule_id, "pair": r.pair,
            "period_start": r.period_start, "period_end": r.period_end,
            "n_obs": int(r.n_obs), "metric_name": r.log_name, **dec, "p_value": p,
            "label": r.label, "literature_label": lit, "config_hash": r.config_hash,
            "decision_table_hash": table_hash, "notes": notes,
        })
    return pd.DataFrame(out)


def insert_ledger(client: ClickHouseClient, frame: pd.DataFrame) -> int:
    """Insert into ``dow.str_rule_backtest_log`` (never deletes earlier rows)."""
    return client.insert_df(TABLE, frame)
