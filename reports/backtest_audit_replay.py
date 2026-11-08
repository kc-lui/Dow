"""R11 audit: truncation replay of the P4 event construction (read-only, no src/ changes).

For several cut dates the DJ pair frame is truncated at ``close[:t+1]``, the P4 objects are
rebuilt with the committed configuration, and every event set of R1..R8 restricted to bars
``<= t`` is compared with the full-sample event set restricted the same way. Outcomes that
need post-cut information (R1 ``S_{k+1}``, R3/R6 "single" classification windows) are
compared only where the full sample's information was available before the cut.

Run:  uv run --python .venv/bin/python reports/backtest_audit_replay.py
"""

from __future__ import annotations

import sys
import time

import numpy as np
import pandas as pd

from dowtheory.backtest.events import (
    breakout_groups,
    build_objects,
    detect_pair_lines,
    leg_events,
    leg_pair_events,
    make_pair_frame,
    pair_reversal_groups,
    pair_states,
    position_series,
    r1_events,
    reversal_events,
    split_date,
)
from dowtheory.config import load_config
from dowtheory.data.loader import load_klines
from dowtheory.storage.clickhouse_client import ClickHouseClient

CUTS = ["1996-06-28", "2001-09-28", "2008-10-31", "2012-12-31", "2016-03-31", "2020-03-23",
        "2023-06-30", "2025-12-31"]
PERIOD_END = "2026-11-06"
H = {"R2": 60, "R3": 60, "R6": 20}


def load_frame() -> pd.DataFrame:
    with ClickHouseClient() as client:
        a = load_klines("^DJI", None, PERIOD_END, client=client)
        b = load_klines("^DJT", None, PERIOD_END, client=client)
    return make_pair_frame(a, b)


def events_at(frame: pd.DataFrame, cfg, cut_bar: int | None) -> dict[str, list]:
    """Every event set, as hashable tuples, computed on ``frame`` (full or truncated)."""
    objs = build_objects(frame, cfg, ("^DJI", "^DJT"))
    last = objs.last if cut_bar is None else cut_bar
    tol = cfg.trend.equal_extreme_tol
    out: dict[str, list] = {}
    # R1: event bars; outcomes only when S_{k+1} is confirmed by the cut
    sec = objs.a.secondary
    r1 = r1_events(sec, objs.a.snapshots, objs.index, tol)
    out["R1_bars"] = [(e.bar, e.side) for e in r1 if e.bar <= last]
    by_bar = {s.confirmed_idx: k for k, s in enumerate(sec)}
    r1_out = []
    for e in r1:
        k = by_bar[e.bar]
        if k + 1 < len(sec) and sec[k + 1].confirmed_idx <= last:
            r1_out.append((e.bar, e.outcome))
    out["R1_outcomes"] = r1_out
    # swings and states themselves
    out["swings"] = [(s.idx, s.kind, s.confirmed_idx, str(s.price)) for s in sec if s.confirmed_idx <= last]
    out["states"] = [objs.a.snapshots[t].state for t in range(last + 1)]
    out["signals_a"] = [(s.idx, s.kind) for s in objs.a.signals if s.idx <= last]
    out["signals_b"] = [(s.idx, s.kind) for s in objs.b.signals if s.idx <= last]
    # R2
    out["R2"] = [(e.bar, e.sign) for e in reversal_events(objs.a, objs.index) if e.bar <= last]
    # R3: confirmed events by confirmed bar; single only when c + h <= cut
    conf, single = pair_reversal_groups(objs, H["R3"], cfg.confirmation.max_days)
    out["R3_confirmed"] = [(e.bar, e.sign) for e in conf if e.bar <= last]
    out["R3_single"] = [(e.bar, e.sign) for e in single if e.bar + H["R3"] <= last]
    # R4/R5
    legs = leg_events(objs.a, objs.index)
    out["R45"] = [(lg.bar, lg.counter, str(lg.rr), lg.in_band, lg.d_cal, lg.rhea) for lg in legs
                  if lg.bar <= last]
    # R6
    lines = detect_pair_lines(objs, cfg.line.band_pct, cfg.line.min_sessions, cfg.line.max_drift_frac)
    g = breakout_groups(lines, objs, H["R6"])
    out["R6_lines"] = [(ln.start, ln.end) for ln in lines if objs.bar_of(ln.end) <= last]
    out["R6_confirmed"] = [(e.bar, e.sign) for e in g.confirmed if e.bar <= last]
    out["R6_single"] = [(e.bar, e.sign) for e in g.single if e.bar + H["R6"] <= last]
    # R7
    start_bar = int(objs.index.searchsorted(pd.Timestamp("2000-01-03")))
    out["R7"] = [(p.bar, round(p.with_vol, 3), round(p.counter_vol, 3))
                 for p in leg_pair_events(objs.a, objs.index, start_bar) if p.bar <= last]
    # R8
    states = pair_states(objs)
    pos = position_series(states, objs, allow_short=False)
    out["R8_pos"] = list(pos[: last + 1])
    out["R8_states"] = states[: last + 1]
    return out


def main() -> int:
    cfg = load_config()
    frame = load_frame()
    print(f"frame {frame.index[0].date()}..{frame.index[-1].date()} n={len(frame)} "
          f"config_hash={cfg.config_hash()}")
    print(f"split_date = {split_date(frame.index[0].date(), frame.index[-1].date())}")
    t0 = time.time()
    full = events_at(frame, cfg, None)
    print(f"full objects in {time.time() - t0:.1f}s; R1 events {len(full['R1_bars'])}, "
          f"R2 {len(full['R2'])}, R3 conf/single {len(full['R3_confirmed'])}/{len(full['R3_single'])}, "
          f"R45 {len(full['R45'])}, R6 conf/single {len(full['R6_confirmed'])}/{len(full['R6_single'])}, "
          f"R7 {len(full['R7'])}")
    failures = 0
    for cut in CUTS:
        cut_bar = int(frame.index.searchsorted(pd.Timestamp(cut), side="right")) - 1
        trunc = frame.iloc[: cut_bar + 1]
        full_cut = events_at(frame, cfg, cut_bar)
        part = events_at(trunc, cfg, None)
        print(f"\n== cut {cut} (bar {cut_bar}, {len(trunc)} bars)")
        for key in full_cut:
            a, b = full_cut[key], part[key]
            if key == "R8_pos":
                same = np.array_equal(np.asarray(a), np.asarray(b))
            else:
                same = a == b
            status = "PASS" if same else "FAIL"
            if not same:
                failures += 1
                sa, sb = set(map(tuple, a)) if key != "states" else set(enumerate(a)), (
                    set(map(tuple, b)) if key != "states" else set(enumerate(b)))
                extra = f" full-only={sorted(sa - sb)[:5]} trunc-only={sorted(sb - sa)[:5]}"
            else:
                extra = ""
            print(f"  {status} {key:13s} n_full={len(a):5d} n_trunc={len(b):5d}{extra}")
    print(f"\nTOTAL FAILURES: {failures}")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
