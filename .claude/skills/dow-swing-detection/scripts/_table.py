"""Row and markdown-table formatting for swing output (presentation only, no detection logic)."""

from __future__ import annotations

from dowtheory.swings import Swing

COLS = [
    "ts",
    "kind",
    "price",
    "confirmed_ts",
    "scale",
    "amplitude_pct",
    "duration_days",
    "retrace",
    "flags",
]


def swing_row(s: Swing, snapped: bool | None) -> dict:
    """JSON-ready dict for one swing; ``snapped`` is None on minor swings."""
    return {
        "ts": s.ts.isoformat(),
        "kind": s.kind,
        "price": float(s.price),
        "confirmed_ts": s.confirmed_ts.isoformat(),
        "scale": s.scale,
        "amplitude_pct": float(s.amplitude_pct),
        "duration_days": s.duration_days,
        "retrace_ratio": None if s.retrace_ratio is None else float(s.retrace_ratio),
        "flags": s.flags,
        "snapped": snapped,
    }


def markdown_table(rows: list[dict]) -> str:
    """Markdown table over ``COLS``; unsnapped secondary rows get a ``*`` after the scale."""
    out = ["| " + " | ".join(COLS) + " |", "|" + "---|" * len(COLS)]
    for r in rows:
        retrace = "-" if r["retrace_ratio"] is None else f"{r['retrace_ratio']:.3f}"
        flags = ",".join(k for k, v in r["flags"].items() if v) or "-"
        scale = r["scale"] + ("*" if r["snapped"] is False else "")
        out.append(
            f"| {r['ts']} | {r['kind']} | {r['price']:.2f} | {r['confirmed_ts']} | {scale} | "
            f"{100 * r['amplitude_pct']:.2f}% | {r['duration_days']} | {retrace} | {flags} |"
        )
    return "\n".join(out)


def summary_line(rows: list[dict], symbol: str, df, sw, sec_pct: float) -> str:
    """One-line footer: count, symbol, bar range, method and thresholds."""
    return (
        f"\n{len(rows)} swings | {symbol} | bars {len(df)} {df.index[0].date()} -> "
        f"{df.index[-1].date()} | method {sw.method} minor {sw.minor_pct} secondary {sec_pct} "
        f"min_sessions {sw.secondary_min_sessions}"
    )
