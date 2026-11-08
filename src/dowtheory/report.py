"""Markdown rendering of an :class:`AnalysisResult`."""

from __future__ import annotations

from typing import Any

from dowtheory.schema import AnalysisResult

MAX_LINES_SHOWN = 10
MAX_SIGNALS_SHOWN = 15


def _fmt(value: Any, nd: int = 2) -> str:
    if value is None:
        return "-"
    if isinstance(value, bool):
        return "yes" if value else "no"
    if isinstance(value, (float, int)) or hasattr(value, "quantize"):
        return f"{float(value):,.{nd}f}"
    return str(value)


def _table(headers: list[str], rows: list[list[str]]) -> list[str]:
    if not rows:
        return ["_none_", ""]
    out = ["| " + " | ".join(headers) + " |", "|" + "|".join("---" for _ in headers) + "|"]
    out += ["| " + " | ".join(r) + " |" for r in rows]
    return [*out, ""]


def to_markdown(result: AnalysisResult) -> str:
    """Render the result as markdown tables; the defense line is flagged agent-defined."""
    m, ts, labels = result.meta, result.trend_state, result.status_labels
    conf = ts["confirmation"]
    title = f"{m['symbol']} vs {m['pair']}" if m.get("pair") else str(m["symbol"])
    lines = [f"# Dow analysis: {title} as of {m['as_of']}", ""]
    lines += [
        (f"Method `{m['swing_method']}` minor {m['thresholds']['minor_pct']} / "
        f"secondary {m['thresholds']['secondary_pct']}; run `{m['run_id']}`; "
        f"config `{m['config_hash'][:12]}`"),
        "",
        "## Trend state",
        "",
    ]
    dl = ts.get("defense_line")
    rows = [
        ["Primary trend", f"{ts['primary']} since {ts['since'] or '-'}"],
        ["Secondary direction", str(ts["secondary_direction"])],
        ["Pair confirmation", f"{conf['status']} (pair state {conf['pair_state'] or '-'})"],
        ["Confirmation detail", conf["detail"]],
        ["Volume confirms", _fmt(ts.get("volume_confirms"))],
        [
            "Defense line [agent-defined]",
            f"{_fmt(dl['price'])} ({dl['type']}, set {dl['ts']}) - agent-defined, no literature source"
            if dl else "-",
        ],
    ]
    lines += _table(["Item", "Value"], rows)

    sec = [s for s in result.swings if s["scale"] == "secondary"]
    counts = {sc: sum(1 for s in result.swings if s["scale"] == sc) for sc in ("minor", "secondary")}
    lines += [f"## Secondary swings ({counts['secondary']}; minor swings: {counts['minor']})", ""]
    lines += _table(
        ["Date", "Kind", "Price", "Confirmed", "Amplitude %", "Days", "Retrace"],
        [
            [str(s["ts"]), s["kind"], _fmt(s["price"]), str(s["confirmed_ts"]),
             _fmt(float(s["amplitude_pct"]) * 100, 1), str(s["duration_days"]),
             _fmt(s["retrace_ratio"])]
            for s in sec[-12:]
        ],
    )

    lines += ["## Levels", ""]
    lv_rows = [
        [name, _fmt(lv["price"]), f"{_fmt(lv['zone_low'])} - {_fmt(lv['zone_high'])}",
         str(lv["touches"])]
        for name in ("support", "resistance") for lv in result.levels[name]
    ]
    lines += _table(["Type", "Price", "Zone", "Touches"], lv_rows)
    tl_rows = [
        [f"{t['kind']}trend", f"{t['p0'][0]} @ {_fmt(t['p0'][1])}",
         f"{t['p1'][0]} @ {_fmt(t['p1'][1])}", _fmt(t["slope_per_day"], 3),
         _fmt(t["value_at_as_of"]), str(t["touches"]), "yes" if t["valid"] else "broken"]
        for t in result.levels["trendlines"]
    ]
    lines += _table(["Trendline", "P0", "P1", "Slope/day", "At as-of", "Touches", "Valid"], tl_rows)

    lines += [f"## Lines ({len(result.lines)}; last {MAX_LINES_SHOWN} shown)", ""]
    lines += _table(
        ["Start", "End", "Band A %", "Band B %", "Breakout", "Both confirm"],
        [
            [str(x["start"]), str(x["end"]), _fmt(x["band_pct_a"] * 100, 1),
             _fmt(x["band_pct_b"] * 100, 1),
             x["breakout"] + (f" {x['breakout_ts']}" if x["breakout_ts"] else ""),
             "yes" if x["confirmed_both"] else "no"]
            for x in result.lines[-MAX_LINES_SHOWN:]
        ],
    )

    trend_signals = [s for s in result.signals if not s["kind"].startswith("LINE_")]
    lines += [
        (f"## Signals ({len(trend_signals)} trend signals, "
        f"{len(result.signals) - len(trend_signals)} line breakouts; "
        f"last {MAX_SIGNALS_SHOWN} trend signals shown)"),
        "",
    ]
    lines += _table(
        ["Date", "Kind", "Price", "Level", "Agent-defined", "Confirmation", "Note"],
        [
            [str(s["ts"]), s["kind"], _fmt(s["price"]), _fmt(s["level"]),
             "yes" if s["agent_defined"] else "no", s["confirmation"], s["note"]]
            for s in trend_signals[-MAX_SIGNALS_SHOWN:]
        ],
    )

    lines += ["## Status labels", ""]
    lines += _table(["Item", "Label"], [[k, f"【{v}】"] for k, v in labels.items()])
    return "\n".join(lines)
