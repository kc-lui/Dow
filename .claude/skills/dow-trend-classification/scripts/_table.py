"""Row and markdown-table formatting for trend output (presentation only, no state logic)."""

from __future__ import annotations

from dowtheory.swings import Swing
from dowtheory.trend import Signal, TrendState

STATE_COLS = ["state", "since", "secondary_direction", "defense_line", "last_H", "last_L"]
SIGNAL_COLS = ["ts", "kind", "price", "level", "note", "agent_defined"]


def _swing(sw: Swing | None) -> dict | None:
    return None if sw is None else {"ts": sw.ts.isoformat(), "price": float(sw.price)}


def state_row(st: TrendState) -> dict:
    """JSON-ready dict mirroring ``AnalysisResult.trend_state`` plus the bookkeeping swings."""
    defense = None
    if st.defense_line is not None:
        defense = {
            "price": float(st.defense_line),
            "ts": st.defense_line_ts.isoformat() if st.defense_line_ts else None,
            "type": st.defense_line_kind,
            "agent_defined": True,
        }
    return {
        "primary": st.state,
        "since": st.since.isoformat() if st.since else None,
        "secondary_direction": st.secondary_direction,
        "defense_line": defense,
        "last_H": _swing(st.last_H),
        "prev_H": _swing(st.prev_H),
        "last_L": _swing(st.last_L),
        "prev_L": _swing(st.prev_L),
    }


def signal_row(sig: Signal) -> dict:
    """JSON-ready dict for one signal."""
    return {
        "ts": sig.ts.isoformat(),
        "kind": sig.kind,
        "price": float(sig.price),
        "level": None if sig.level is None else float(sig.level),
        "note": sig.note,
        "agent_defined": sig.agent_defined,
    }


def _fmt_swing(d: dict | None) -> str:
    return "-" if d is None else f"{d['price']:.2f} ({d['ts']})"


def state_table(row: dict) -> str:
    """One-row markdown table of the current trend state."""
    d = row["defense_line"]
    defense = "-" if d is None else f"{d['price']:.2f} ({d['ts']}, {d['type']}, agent-defined)"
    cells = [
        row["primary"],
        row["since"] or "-",
        row["secondary_direction"],
        defense,
        _fmt_swing(row["last_H"]),
        _fmt_swing(row["last_L"]),
    ]
    header = "| " + " | ".join(STATE_COLS) + " |\n|" + "---|" * len(STATE_COLS)
    return header + "\n| " + " | ".join(cells) + " |"


def signals_table(rows: list[dict]) -> str:
    """Markdown table over ``SIGNAL_COLS``."""
    out = ["| " + " | ".join(SIGNAL_COLS) + " |", "|" + "---|" * len(SIGNAL_COLS)]
    for r in rows:
        level = "-" if r["level"] is None else f"{r['level']:.2f}"
        out.append(
            f"| {r['ts']} | {r['kind']} | {r['price']:.2f} | {level} | {r['note']} | "
            f"{str(r['agent_defined']).lower()} |"
        )
    return "\n".join(out)


def summary_line(rows: list[dict], symbol: str, df, strict: bool, tol: float) -> str:
    """One-line footer: signal count, symbol, bar range, mode and tolerance."""
    mode = "strict" if strict else "non-strict"
    return (
        f"\n{len(rows)} signals | {symbol} | bars {len(df)} {df.index[0].date()} -> "
        f"{df.index[-1].date()} | require_lower_high_for_reversal {mode} | "
        f"equal_extreme_tol {tol}"
    )


def json_doc(symbol: str, df, strict: bool, tol: float, warmup: str) -> dict:
    """Run metadata for the JSON document (window, mode, tolerance, warm-up note)."""
    return {
        "symbol": symbol,
        "bars": len(df),
        "start": df.index[0].date().isoformat(),
        "end": df.index[-1].date().isoformat(),
        "strict": strict,
        "equal_extreme_tol": tol,
        "warmup_note": warmup,
    }
