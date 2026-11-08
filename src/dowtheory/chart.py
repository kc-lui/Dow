"""Matplotlib chart of an analysis (price panel + volume panel)."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import matplotlib

matplotlib.use("Agg")

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.lines import Line2D
from matplotlib.patches import Patch

DEFENSE_LABEL = "Dow defense line (agent-defined)"
_ANNOTATED_SIGNALS = ("REVERSAL_UP", "REVERSAL_DOWN", "DEFENSE_BREAK")
_LINE_SIGNALS = ("LINE_BREAKOUT_UP", "LINE_BREAKOUT_DOWN")
MIN_LINE_DAYS_SHOWN = 28  # shorter ranges are too frequent at band 5% to be readable


def _ts(value: Any) -> pd.Timestamp:
    return pd.Timestamp(value)


def chart_filename(result: Any) -> str:
    """``{sym}_{pair}_{as_of}_{method}{minor_pct}.png`` with ``^`` stripped."""
    meta = result.meta
    parts = [meta["symbol"], meta.get("pair"), str(meta["as_of"])]
    stem = "_".join(p for p in parts if p).replace("^", "")
    return f"{stem}_{meta['swing_method']}{meta['thresholds']['minor_pct']}.png"


def chart_title(result: Any) -> str:
    """Title per the contract."""
    m, ts = result.meta, result.trend_state
    names = f"{m['symbol']} vs {m['pair']}" if m.get("pair") else str(m["symbol"])
    th = m["thresholds"]
    return (
        f"{names} | {ts['primary']} since {ts['since']} | "
        f"confirmation: {ts['confirmation']['status']} | "
        f"method {m['swing_method']} {th['minor_pct']}/{th['secondary_pct']}"
    )


def render_chart(
    result: Any,
    df: pd.DataFrame,
    df_pair: pd.DataFrame | None = None,
    out_dir: str | Path = "outputs/charts",
) -> Path:
    """Render the chart as PNG into ``out_dir`` and return its path.

    Signal markers: reversals and defense breaks get a dotted vertical line with text; line
    breakouts are small triangles on the close; HH/HL/LH/LL are visible as swing markers.
    """
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    fig, (ax, axv) = plt.subplots(
        2, 1, figsize=(14, 8), sharex=True, gridspec_kw={"height_ratios": [4, 1]}
    )
    handles: list[Any] = []
    ax.plot(df.index, df["close"], color="#1f3a5f", lw=1.0, zorder=3)
    handles.append(Line2D([], [], color="#1f3a5f", lw=1.0, label=f"{result.meta['symbol']} close"))
    x_end = df.index[-1]

    if df_pair is not None:
        ax2 = ax.twinx()
        ax2.plot(df_pair.index, df_pair["close"], color="#e08a1e", lw=0.8, alpha=0.6, zorder=2)
        ax2.set_ylabel(f"{result.meta['pair']} close", color="#e08a1e")
        ax2.tick_params(axis="y", colors="#e08a1e")
        handles.append(
            Line2D([], [], color="#e08a1e", lw=0.8, alpha=0.6,
                   label=f"{result.meta['pair']} close (right axis)")
        )

    # Support / resistance zones
    for key, color in (("support", "green"), ("resistance", "red")):
        for lv in result.levels[key]:
            ax.axhspan(float(lv["zone_low"]), float(lv["zone_high"]), color=color, alpha=0.15, zorder=1)
            ax.text(
                df.index[0], float(lv["price"]), f" {key[:3].upper()} x{lv['touches']}",
                fontsize=7, color=color, va="center", zorder=5,
            )
        if result.levels[key]:
            handles.append(Patch(color=color, alpha=0.3, label=f"{key} zone (clustered swings)"))

    # Line ranges
    shown_lines = [
        ln for ln in result.lines
        if (_ts(ln["end"]) - _ts(ln["start"])).days >= MIN_LINE_DAYS_SHOWN
    ]
    for ln in shown_lines:
        ax.axvspan(_ts(ln["start"]), _ts(ln["end"]), color="grey", alpha=0.2, zorder=0)
    if shown_lines:
        handles.append(
            Patch(color="grey", alpha=0.3,
                  label=f"line >= {MIN_LINE_DAYS_SHOWN} days (both averages sideways)")
        )
    for direction, marker, color in (("UP", "^", "#1f77b4"), ("DOWN", "v", "#9467bd")):
        pts = [s for s in result.signals if s["kind"] == f"LINE_BREAKOUT_{direction}"]
        if pts:
            ax.scatter([_ts(s["ts"]) for s in pts], [float(s["price"]) for s in pts], s=14,
                       marker=marker, color=color, zorder=6)
            handles.append(Line2D([], [], marker=marker, ls="", color=color, ms=5,
                                  label=f"line breakout {direction.lower()}"))

    # Swings
    minor = [s for s in result.swings if s["scale"] == "minor"]
    sec = [s for s in result.swings if s["scale"] != "minor"]
    if minor:
        ax.scatter([_ts(s["ts"]) for s in minor], [float(s["price"]) for s in minor],
                   s=10, color="grey", alpha=0.7, zorder=4)
        handles.append(Line2D([], [], marker="o", ls="", color="grey", ms=4, label="minor swing"))
    for kind, marker, color, name in (
        ("H", "v", "red", "secondary high"), ("L", "^", "green", "secondary low")
    ):
        pts = [s for s in sec if s["kind"] == kind]
        if pts:
            ax.scatter([_ts(s["ts"]) for s in pts], [float(s["price"]) for s in pts],
                       s=60, marker=marker, color=color, edgecolor="black", lw=0.5, zorder=6)
            handles.append(Line2D([], [], marker=marker, ls="", color=color, mec="black", ms=7, label=name))

    # Defense line
    dl = result.trend_state.get("defense_line")
    if dl:
        ax.hlines(float(dl["price"]), _ts(dl["ts"]), x_end, colors="red", linestyles="--",
                  lw=1.4, zorder=5)
        ax.annotate(
            f"{DEFENSE_LABEL}: {float(dl['price']):,.0f}", (_ts(dl["ts"]), float(dl["price"])),
            xytext=(-8, -12), textcoords="offset points", ha="right", fontsize=7, color="red",
            zorder=7, bbox={"facecolor": "white", "alpha": 0.7, "pad": 0.5, "lw": 0},
        )
        handles.append(Line2D([], [], color="red", ls="--", lw=1.4, label=DEFENSE_LABEL))

    # Trendlines
    for tl in result.levels["trendlines"]:
        x0, x1 = _ts(tl["p0"][0]), x_end
        y0 = float(tl["p0"][1])
        y1 = y0 + float(tl["slope_per_day"]) * (x1 - x0).days
        color = "green" if tl["kind"] == "up" else "red"
        ax.plot([x0, x1], [y0, y1], color=color, lw=1.2, alpha=1.0 if tl["valid"] else 0.4, zorder=5)
        handles.append(Line2D([], [], color=color, lw=1.2,
                              label=f"{tl['kind']}trend line{'' if tl['valid'] else ' (broken)'}"))

    # Signals
    lo, hi = ax.get_ylim()
    shown = [s for s in result.signals if s["kind"] in _ANNOTATED_SIGNALS]
    for i, s in enumerate(shown):
        x = _ts(s["ts"])
        ax.axvline(x, color="black", ls=":", lw=0.8, alpha=0.7, zorder=2)
        ax.text(x, hi - (hi - lo) * (0.03 + 0.05 * (i % 4)), s["kind"], rotation=90, fontsize=6,
                ha="right", va="top", zorder=7,
                bbox={"facecolor": "white", "alpha": 0.7, "pad": 0.5, "lw": 0})
    if shown:
        handles.append(Line2D([], [], color="black", ls=":", lw=0.8, label="signal"))
    ax.set_ylim(lo, hi)

    # Volume panel
    axv.bar(df.index, df["volume"] / 1e6, width=1.0, color="#7a8ba3")
    axv.set_ylabel("Volume (M)")
    axv.xaxis.set_major_locator(mdates.AutoDateLocator())
    axv.xaxis.set_major_formatter(mdates.ConciseDateFormatter(axv.xaxis.get_major_locator()))

    ax.set_ylabel(f"{result.meta['symbol']} close")
    ax.set_title(chart_title(result), fontsize=10)
    ax.grid(alpha=0.25)
    ax.legend(handles=handles, loc="center left", bbox_to_anchor=(1.08 if df_pair is not None else 1.01, 0.5),
              fontsize=8, frameon=False)
    path = out / chart_filename(result)
    fig.savefig(path, dpi=110, bbox_inches="tight")
    plt.close(fig)
    return path


__all__ = ["DEFENSE_LABEL", "chart_filename", "chart_title", "render_chart"]
