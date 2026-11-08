"""Row, markdown-table and JSON formatting for confirmation output (presentation only, no logic)."""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass

import pandas as pd

from dowtheory.confirmation import REVERSAL_KINDS, ConfirmationResult, SignalConfirmation
from dowtheory.line import LineRange
from dowtheory.trend import Signal, TrendState

PAIR_COLS = ["status", "pair_state", "confirmed_ts", "A_state", "A_since", "B_state", "B_since"]
SIGNAL_COLS = ["ts", "kind", "price", "level", "confirmation", "matched_ts", "confirmed_ts"]
LINE_COLS = [
    "start",
    "end",
    "sessions",
    "band_a",
    "band_b",
    "breakout",
    "breakout_ts",
    "confirmed_both",
    "confirmed_ts",
]
VOLUME_TEXT = {
    True: "true (trend-leg mean volume > counter-leg mean)",
    False: "false",
    None: "null",
}


def _d(value) -> str | None:
    return None if value is None else value.isoformat()


def _s(value, fmt: str | None = None) -> str:
    if value is None:
        return "-"
    if isinstance(value, bool):
        return str(value).lower()
    return format(value, fmt) if fmt else str(value)


def _table(cols: list[str], rows: list[list[str]]) -> str:
    out = ["| " + " | ".join(cols) + " |", "|" + "---|" * len(cols)]
    return "\n".join(out + ["| " + " | ".join(r) + " |" for r in rows])


def trend_row(st: TrendState) -> dict:
    return {"primary": st.state, "since": _d(st.since)}


def pair_row(res: ConfirmationResult) -> dict:
    """JSON-ready dict mirroring ``trend_state.confirmation`` of ``dow analyze``."""
    return {
        "status": res.status,
        "pair_state": res.pair_state,
        "detail": res.detail,
        "confirmed_ts": _d(res.confirmed_ts),
    }


def signal_row(sig: Signal, res: SignalConfirmation | None) -> dict:
    """One signal with its pair confirmation; ``not_applicable`` unless it is a reversal."""
    applicable = res is not None and sig.kind in REVERSAL_KINDS
    return {
        "ts": _d(sig.ts),
        "kind": sig.kind,
        "price": float(sig.price),
        "level": None if sig.level is None else float(sig.level),
        "confirmation": res.status if applicable else "not_applicable",
        "matched_ts": _d(res.matched_ts) if applicable else None,
        "confirmed_ts": _d(res.confirmed_ts) if applicable else None,
    }


def line_row(ln: LineRange, index: pd.DatetimeIndex) -> dict:
    """One line range; ``sessions`` counts trading sessions from ``start`` to ``end``."""
    sessions = index.get_loc(pd.Timestamp(ln.end)) - index.get_loc(pd.Timestamp(ln.start)) + 1
    return {
        "start": _d(ln.start),
        "end": _d(ln.end),
        "sessions": int(sessions),
        "band_pct_a": ln.band_pct_a,
        "band_pct_b": ln.band_pct_b,
        "breakout": ln.breakout,
        "breakout_ts": _d(ln.breakout_ts),
        "confirmed_both": ln.confirmed_both,
        "confirmed_ts": _d(ln.confirmed_ts),
    }


def signals_table(rows: list[dict]) -> str:
    return _table(
        SIGNAL_COLS,
        [
            [
                r["ts"],
                r["kind"],
                _s(r["price"], ".2f"),
                _s(r["level"], ".2f"),
                r["confirmation"],
                _s(r["matched_ts"]),
                _s(r["confirmed_ts"]),
            ]
            for r in rows
        ],
    )


def lines_table(rows: list[dict]) -> str:
    return _table(
        LINE_COLS,
        [
            [
                r["start"],
                r["end"],
                str(r["sessions"]),
                _s(r["band_pct_a"], ".3f"),
                _s(r["band_pct_b"], ".3f"),
                r["breakout"],
                _s(r["breakout_ts"]),
                _s(r["confirmed_both"]),
                _s(r["confirmed_ts"]),
            ]
            for r in rows
        ],
    )


@dataclass(frozen=True)
class Report:
    """Everything the CLI prints, assembled from library results (no decisions are made here)."""

    args: object  # argparse namespace: symbol, pair
    df: pd.DataFrame
    cfg: object
    pair: ConfirmationResult
    state_a: TrendState
    state_b: TrendState
    signal_rows: list[dict]
    signals_b: Sequence[Signal]
    lines: Sequence[LineRange]
    volume: bool | None

    def line_rows(self) -> list[dict]:
        return [line_row(ln, self.df.index) for ln in self.lines]

    def pair_table(self) -> str:
        p, a, b = pair_row(self.pair), trend_row(self.state_a), trend_row(self.state_b)
        row = [
            p["status"],
            _s(p["pair_state"]),
            _s(p["confirmed_ts"]),
            a["primary"],
            _s(a["since"]),
            b["primary"],
            _s(b["since"]),
        ]
        return _table(PAIR_COLS, [row]) + f"\n{p['detail']}"

    def summary(self) -> str:
        c, df, n = self.cfg.line, self.df, len(self.lines)
        return (
            f"volume_confirms: {VOLUME_TEXT[self.volume]} (informational; literature-disputed R-038)\n"
            f"{self.args.symbol} vs {self.args.pair} | bars {len(df)} {df.index[0].date()} -> "
            f"{df.index[-1].date()} | {n} lines | band_pct {c.band_pct} min_sessions "
            f"{c.min_sessions} max_drift_frac {c.max_drift_frac} | "
            f"confirmation.max_days {self.cfg.confirmation.max_days}"
        )

    def text(self) -> str:
        return "\n\n".join(
            [
                self.pair_table(),
                signals_table(self.signal_rows),
                lines_table(self.line_rows()),
                self.summary(),
            ]
        )

    def doc(self) -> dict:
        c, df = self.cfg.line, self.df
        return {
            "symbol": self.args.symbol,
            "pair": self.args.pair,
            "bars": len(df),
            "start": df.index[0].date().isoformat(),
            "end": df.index[-1].date().isoformat(),
            "band_pct": c.band_pct,
            "min_sessions": c.min_sessions,
            "max_drift_frac": c.max_drift_frac,
            "max_days": self.cfg.confirmation.max_days,
            "pair_confirm": pair_row(self.pair),
            "trend_a": trend_row(self.state_a),
            "trend_b": trend_row(self.state_b),
            "signals": self.signal_rows,
            "reversals_b": [
                signal_row(s, None) for s in self.signals_b if s.kind in REVERSAL_KINDS
            ],
            "lines": self.line_rows(),
            "volume_confirms": self.volume,
        }
