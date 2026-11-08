"""R8 spec review P3: truncation-replay look-ahead audit and economic sanity checks.

Read-only. Loads ^DJI / ^DJT from ClickHouse (dow.mkt_klines FINAL) and never writes.
Run:  uv run --python .venv/bin/python python reports/spec_review_p3_replay.py

Sections
  A  swings: detect_multiscale(close[:t+1]) vs swings_as_of(full, t)       (pct/atr/pivot)
  B  trend:  run_trend on truncated data vs per-bar snapshot of the full run
  C  lines:  detect_lines(as_of_idx=t) vs full run, incl. confirmed_both flag
  D  per-signal pair confirmation: status at the signal date vs at the final as_of
  E  trendlines / levels: truncated recompute vs full swings filtered as of t
  F  secondary swings: retracement 1/3-2/3 and 21-90 day duration shares; sensitivity
  G  lines: counts under alternative band / min-session / sideways definitions
  H  SUSPECT episodes after DEFENSE_BREAK, stale defense lines, Rhea 5%/15-day screen
  I  (--equal-tol) equal-extreme tolerance prototype for HH/HL labelling
"""

from __future__ import annotations

import dataclasses
import sys
from collections import Counter

import numpy as np
import pandas as pd

from dowtheory.confirmation import signal_confirmed
from dowtheory.config import load_config
from dowtheory.data.loader import load_klines
from dowtheory.levels import cluster_levels, fit_trendlines
from dowtheory.line import detect_lines
from dowtheory.swings import detect_multiscale, swings_as_of
from dowtheory.trend import BULL_PRIMARY, BEAR_PRIMARY, run_trend

CFG = load_config()
STEP = 25  # sample every STEP bars (plus every swing-confirmation bar for section A/B)


def with_swings(cfg, **kw):
    return dataclasses.replace(cfg, swings=dataclasses.replace(cfg.swings, **kw))


def load_pair():
    a = load_klines("^DJI")
    b = load_klines("^DJT")
    common = a.index.intersection(b.index)
    return a.loc[common], b.loc[common]


def sample_bars(n, extra=()):
    return sorted(set(range(300, n, STEP)) | {t for t in extra if 300 <= t < n} | {n - 1})


# --------------------------------------------------------------------------- A
def audit_swings(df, method):
    cfg = with_swings(CFG, method=method)
    full = detect_multiscale(df.close, cfg, df.high, df.low)
    conf_bars = {s.confirmed_idx for s in full["secondary"]} | {
        s.confirmed_idx - 1 for s in full["secondary"]
    }
    bad = Counter()
    first_bad = {}
    bars = sample_bars(len(df), conf_bars)
    for t in bars:
        d = df.iloc[: t + 1]
        tr = detect_multiscale(d.close, cfg, d.high, d.low)
        for scale in ("minor", "secondary"):
            if swings_as_of(tr[scale], t) != swings_as_of(full[scale], t):
                bad[scale] += 1
                first_bad.setdefault(scale, df.index[t].date())
    return len(bars), bad, first_bad


# --------------------------------------------------------------------------- B
def audit_trend(df):
    full = detect_multiscale(df.close, CFG, df.high, df.low)
    _, sig_full, snaps = run_trend(df.close, full["secondary"], CFG)
    bars = sample_bars(len(df), {s.confirmed_idx for s in full["secondary"]})
    bad = 0
    for t in bars:
        d = df.iloc[: t + 1]
        tr = detect_multiscale(d.close, CFG, d.high, d.low)
        st, sig, _ = run_trend(d.close, swings_as_of(tr["secondary"], t), CFG)
        same_state = (st.state, st.since, st.defense_line, st.secondary_direction) == (
            snaps[t].state, snaps[t].since, snaps[t].defense_line, snaps[t].secondary_direction
        )
        same_sig = sig == [s for s in sig_full if s.idx <= t]
        bad += not (same_state and same_sig)
    return len(bars), bad


# --------------------------------------------------------------------------- C
def audit_lines(a, b, band=0.05, min_days=14):
    full = detect_lines(a.close, b.close, band, min_days, None, None)
    geo_bad = flag_bad = 0
    flips = []
    for ln in full:
        if ln.breakout_ts is None:
            continue
        k = a.index.get_loc(pd.Timestamp(ln.breakout_ts))
        trunc = detect_lines(a.close, b.close, band, min_days, k, None)
        match = [x for x in trunc if x.start == ln.start]
        if not match or (match[0].end, match[0].breakout, match[0].breakout_ts) != (
            ln.end, ln.breakout, ln.breakout_ts
        ):
            geo_bad += 1
            continue
        if match[0].confirmed_both != ln.confirmed_both:
            flag_bad += 1
            flips.append((ln.start, ln.breakout_ts))
    return len(full), geo_bad, flag_bad, flips


# --------------------------------------------------------------------------- D
def audit_signal_confirmation(a, b, start=None):
    if start:
        a, b = a[a.index >= start], b[b.index >= start]
    sa = detect_multiscale(a.close, CFG, a.high, a.low)["secondary"]
    sb = detect_multiscale(b.close, CFG, b.high, b.low)["secondary"]
    _, sig_a, _ = run_trend(a.close, sa, CFG)
    _, sig_b, _ = run_trend(b.close, sb, CFG)
    rows = []
    for s in sig_a:
        if not s.kind.startswith("REVERSAL"):
            continue
        at_signal = signal_confirmed(s, [o for o in sig_b if o.idx <= s.idx], None)
        at_end = signal_confirmed(s, sig_b, None)
        matched = [o for o in sig_b if o.kind == s.kind and o.ts >= s.ts]
        prior = [o for o in sig_b if o.kind == s.kind and o.ts < s.ts]
        rows.append((s.ts, s.kind, at_signal, at_end,
                     matched[0].ts if matched else None, prior[-1].ts if prior else None))
    return rows


# --------------------------------------------------------------------------- E
def audit_levels(df):
    full = detect_multiscale(df.close, CFG, df.high, df.low)
    bad = 0
    bars = sample_bars(len(df))[::4]
    for t in bars:
        d = df.iloc[: t + 1]
        tr = detect_multiscale(d.close, CFG, d.high, d.low)
        ref = d.close.iloc[-1]
        for kind in ("up", "down"):
            x = fit_trendlines(swings_as_of(tr["secondary"], t), kind, d.close, 0.01)
            y = fit_trendlines(swings_as_of(full["secondary"], t), kind, d.close, 0.01)
            bad += x != y
        for kind in ("L", "H"):
            x = cluster_levels(swings_as_of(tr["minor"], t), kind, ref_price=ref)
            y = cluster_levels(swings_as_of(full["minor"], t), kind, ref_price=ref)
            bad += x != y
    return len(bars), bad


# --------------------------------------------------------------------------- F
def secondary_stats(df, pct, label):
    cfg = with_swings(CFG, secondary_pct=pct)
    sec = detect_multiscale(df.close, cfg, df.high, df.low)["secondary"]
    st, sig, snaps = run_trend(df.close, sec, cfg)
    legs = sec[2:]
    rr = np.array([float(s.retrace_ratio) for s in legs if s.retrace_ratio is not None])
    dur = np.array([s.duration_days for s in legs])
    react = [s for s in legs if s.retrace_ratio is not None and s.retrace_ratio < 1]
    rr_r = np.array([float(s.retrace_ratio) for s in react])
    dur_r = np.array([s.duration_days for s in react])
    # counter-trend legs: leg ending in an L while the state at its confirmation is bull (or H/bear)
    ctr = []
    for s in legs:
        state = snaps[s.confirmed_idx - 1].state if s.confirmed_idx else "UNDEFINED"
        if (s.kind == "L" and state.startswith("BULL")) or (s.kind == "H" and state.startswith("BEAR")):
            ctr.append(s)
    rr_c = np.array([float(s.retrace_ratio) for s in ctr if s.retrace_ratio is not None])
    dur_c = np.array([s.duration_days for s in ctr])
    in_band = lambda r: float(np.mean((r >= 1 / 3) & (r <= 2 / 3))) if len(r) else float("nan")
    in_dur = lambda d: float(np.mean((d >= 21) & (d <= 90))) if len(d) else float("nan")
    ge21 = lambda d: float(np.mean(d >= 21)) if len(d) else float("nan")
    rev = [s for s in sig if s.kind.startswith("REVERSAL")]
    dbr = [s for s in sig if s.kind == "DEFENSE_BREAK"]
    # longest stay in a SUSPECT state (sessions)
    longest = cur = 0
    for sn in snaps:
        cur = cur + 1 if sn.state.endswith("SUSPECT") else 0
        longest = max(longest, cur)
    suspect_share = float(np.mean([sn.state.endswith("SUSPECT") for sn in snaps]))
    lag = [ (s.confirmed_idx - s.idx) for s in sec ]
    print(
        f"{label} pct={pct:.2f}: n_sec={len(sec)} legs={len(legs)} | all legs: retr1/3-2/3={in_band(rr):.0%} "
        f"dur21-90={in_dur(dur):.0%} dur>=21={ge21(dur):.0%} | reaction legs(r<1) n={len(react)}: "
        f"retr={in_band(rr_r):.0%} dur21-90={in_dur(dur_r):.0%} | counter-trend n={len(ctr)}: "
        f"retr={in_band(rr_c):.0%} dur21-90={in_dur(dur_c):.0%} | reversals={len(rev)} "
        f"defense_breaks={len(dbr)} suspect_share={suspect_share:.0%} longest_suspect={longest} "
        f"median_confirm_lag_bars={int(np.median(lag))} final={st.state} since {st.since}"
    )


# --------------------------------------------------------------------------- G
def sideways_filter(a, b, ln, frac):
    """Line is sideways if the net drift start->end is <= frac*band in both series."""
    s, e = pd.Timestamp(ln.start), pd.Timestamp(ln.end)
    da = abs(a.close.loc[e] / a.close.loc[s] - 1)
    db = abs(b.close.loc[e] / b.close.loc[s] - 1)
    return da, db


def line_stats(a, b, start):
    a, b = a[a.index >= start], b[b.index >= start]
    years = (a.index[-1] - a.index[0]).days / 365.25
    print(f"lines {start}->: {years:.1f} years, {len(a)} sessions")
    # how normal is a 5% joint 14/15-session range?
    for w in (10, 14, 15, 20):
        ra = a.close.rolling(w).apply(lambda x: (x.max() - x.min()) / x.mean(), raw=True)
        rb = b.close.rolling(w).apply(lambda x: (x.max() - x.min()) / x.mean(), raw=True)
        print(f"  share of {w}-session windows with both ranges<=5%: {float(((ra <= .05) & (rb <= .05)).mean()):.0%}; "
              f"<=3%: {float(((ra <= .03) & (rb <= .03)).mean()):.0%}")
    for band in (0.05, 0.04, 0.03):
        for md in (10, 14, 15, 20):
            lines = detect_lines(a.close, b.close, band, md)
            if not lines:
                continue
            chained = sum(1 for p, q in zip(lines, lines[1:]) if p.breakout_ts == q.start)
            side = 0
            for ln in lines:
                da, db = sideways_filter(a, b, ln, 0.5)
                side += (da <= band / 2) and (db <= band / 2)
            conf = sum(ln.confirmed_both for ln in lines)
            print(f"  band={band:.2f} min_sessions={md}: lines={len(lines)} ({len(lines)/years:.1f}/yr) "
                  f"chained={chained} confirmed_both={conf} sideways(net drift<=band/2 both)={side}")


# --------------------------------------------------------------------------- H
def suspect_episodes(df, pct):
    """Every DEFENSE_BREAK / LH-HL entry into SUSPECT: how long it lasted and how it ended."""
    cfg = with_swings(CFG, secondary_pct=pct)
    sec = detect_multiscale(df.close, cfg, df.high, df.low)["secondary"]
    _, sig, snaps = run_trend(df.close, sec, cfg)
    rows, i, n = [], 1, len(snaps)
    while i < n:
        if snaps[i].state.endswith("SUSPECT") and not snaps[i - 1].state.endswith("SUSPECT"):
            j = i
            while j < n and snaps[j].state.endswith("SUSPECT"):
                j += 1
            how = "open" if j == n else snaps[j].state
            px0 = df.close.iloc[i]
            px1 = df.close.iloc[min(j, n - 1)]
            rows.append((df.index[i].date(), snaps[i].state, j - i, how, px1 / px0 - 1))
            i = j
        i += 1
    stale = 0
    for k in range(1, n):
        a, b = snaps[k - 1], snaps[k]
        if a.state == "BULL_SUSPECT" and b.state == BULL_PRIMARY and b.last_L is not None \
                and b.defense_line != b.last_L.price:
            stale += 1
        if a.state == "BEAR_SUSPECT" and b.state == BEAR_PRIMARY and b.last_H is not None \
                and b.defense_line != b.last_H.price:
            stale += 1
    print(f"  pct={pct:.2f}: SUSPECT episodes={len(rows)}; returns to PRIMARY with defense line "
          f"!= latest reaction extreme: {stale}")
    for r in sorted(rows, key=lambda r: -r[2])[:5]:
        print(f"    {r[0]} {r[1]} lasted {r[2]} sessions -> {r[3]}, close change {r[4]:+.1%}")


def time_qualified_zigzag(close, thr, min_days):
    """Causal zig-zag that flips only after >= thr move AND >= min_days calendar days since the
    candidate extreme (Rhea's 15-day / 5% screen made causal). Script-only prototype."""
    from dowtheory.swings import _Raw
    v = close.to_numpy(dtype=float)
    d = close.index
    out, cand, kind = [], None, None
    hi = lo = 0
    for i in range(1, len(v)):
        if cand is None:
            hi = i if v[i] > v[hi] else hi
            lo = i if v[i] < v[lo] else lo
            if v[i] / v[lo] - 1 >= thr and (d[i] - d[lo]).days >= min_days:
                out.append(_Raw(lo, "L", i)); cand, kind = i, "H"
            elif 1 - v[i] / v[hi] >= thr and (d[i] - d[hi]).days >= min_days:
                out.append(_Raw(hi, "H", i)); cand, kind = i, "L"
            continue
        if kind == "H":
            if v[i] > v[cand]:
                cand = i
            elif 1 - v[i] / v[cand] >= thr and (d[i] - d[cand]).days >= min_days:
                out.append(_Raw(cand, "H", i))
                cand, kind = cand + 1 + int(np.argmin(v[cand + 1:i + 1])), "L"
        else:
            if v[i] < v[cand]:
                cand = i
            elif v[i] / v[cand] - 1 >= thr and (d[i] - d[cand]).days >= min_days:
                out.append(_Raw(cand, "L", i))
                cand, kind = cand + 1 + int(np.argmax(v[cand + 1:i + 1])), "H"
    return out


def rhea_screen_stats(df, thr, min_days):
    from dowtheory.swings import _build, compute_secondary_metrics
    raws = time_qualified_zigzag(df.close, thr, min_days)
    sec = compute_secondary_metrics(_build(raws, df.close, "secondary"))
    st, sig, snaps = run_trend(df.close, sec, CFG)
    legs = sec[2:]
    react = [s for s in legs if s.retrace_ratio is not None and s.retrace_ratio < 1]
    rr = np.array([float(s.retrace_ratio) for s in react])
    du = np.array([s.duration_days for s in react])
    lag = np.median([s.confirmed_idx - s.idx for s in sec])
    rev = sum(s.kind.startswith("REVERSAL") for s in sig)
    longest = cur = 0
    for sn in snaps:
        cur = cur + 1 if sn.state.endswith("SUSPECT") else 0
        longest = max(longest, cur)
    print(f"  thr={thr:.2f} min_days={min_days}: n_sec={len(sec)} reaction legs={len(react)} "
          f"retr1/3-2/3={float(np.mean((rr>=1/3)&(rr<=2/3))):.0%} dur21-90={float(np.mean((du>=21)&(du<=90))):.0%} "
          f"reversals={rev} longest_suspect={longest} median_confirm_lag_bars={int(lag)} final={st.state} since {st.since}")


def main() -> int:
    a, b = load_pair()
    print(f"data ^DJI/^DJT {a.index[0].date()}..{a.index[-1].date()} n={len(a)}")

    print("\n[A] swings truncation replay")
    for method in ("pct", "atr", "pivot"):
        n, bad, first = audit_swings(a, method)
        print(f"  ^DJI {method}: bars tested={n} mismatches={dict(bad)} first={first}")
    n, bad, first = audit_swings(b, "pct")
    print(f"  ^DJT pct: bars tested={n} mismatches={dict(bad)} first={first}")

    print("\n[B] trend truncation replay")
    for name, df in (("^DJI", a), ("^DJT", b)):
        n, bad = audit_trend(df)
        print(f"  {name}: bars tested={n} mismatches={bad}")

    print("\n[C] lines truncation replay (full history 1992->)")
    n, geo, flag, flips = audit_lines(a, b)
    print(f"  lines={n} geometry mismatches at breakout bar={geo} confirmed_both differs at breakout bar={flag}")
    print(f"  examples (start, breakout_ts): {flips[:5]}")

    print("\n[D] per-signal confirmation, max_days=None (start 2015-01-01 as in CLI run)")
    for row in audit_signal_confirmation(a, b, "2015-01-01"):
        print(f"  {row[0]} {row[1]}: confirmed_at_signal={row[2]} confirmed_at_as_of={row[3]} "
              f"first_later_DJT_same_kind={row[4]} last_prior_DJT_same_kind={row[5]}")

    print("\n[E] trendlines / levels truncation replay")
    n, bad = audit_levels(a)
    print(f"  ^DJI bars tested={n} mismatches={bad}")

    print("\n[F] secondary swing operationalisation, ^DJI 1992->")
    for pct in (0.05, 0.06, 0.08, 0.10):
        secondary_stats(a, pct, "^DJI")
    secondary_stats(b, 0.10, "^DJT")
    secondary_stats(b, 0.15, "^DJT")

    print("\n[G] line counts")
    line_stats(a, b, "2015-01-01")
    line_stats(a, b, "1992-01-01")

    print("\n[H] SUSPECT episodes and stale defense lines, ^DJI 1992->")
    for pct in (0.06, 0.08, 0.10):
        suspect_episodes(a, pct)
    print("  Rhea screen as a causal time-qualified zig-zag, ^DJI 1992->")
    for thr, md in ((0.05, 15), (0.06, 15), (0.08, 15), (0.10, 0)):
        rhea_screen_stats(a, thr, md)
    return 0


# --------------------------------------------------------------------------- I
def equal_tolerance_test(df, pct, tol):
    """Prototype (temporarily patches ``trend._label``, restored in ``finally``): relabel a swing within ``tol`` of the previous same-kind
    swing as the counter swing (double top = LH, double bottom = HL), then replay."""
    import dowtheory.trend as T

    orig = T._label

    def label(sw, prev):
        if prev is not None and abs(sw.price / prev.price - 1) <= tol:
            return "LH" if sw.kind == "H" else "HL"
        return orig(sw, prev)

    cfg = with_swings(CFG, secondary_pct=pct)
    sec = detect_multiscale(df.close, cfg, df.high, df.low)["secondary"]
    T._label = label
    try:
        st, sig, snaps = run_trend(df.close, sec, cfg)
    finally:
        T._label = orig
    longest = cur = 0
    for sn in snaps:
        cur = cur + 1 if sn.state.endswith("SUSPECT") else 0
        longest = max(longest, cur)
    revs = [(s.ts, s.kind) for s in sig if s.kind.startswith("REVERSAL") and s.ts.year >= 2015]
    print(f"  pct={pct:.2f} equal_tol={tol:.3f}: reversals={sum(s.kind.startswith('REVERSAL') for s in sig)} "
          f"longest_suspect={longest} final={st.state} since {st.since}; 2015+ reversals={revs}")


def run_equal_tol() -> None:
    a, _ = load_pair()
    print("\n[I] equal-extreme tolerance prototype, ^DJI 1992->")
    for pct in (0.06, 0.10):
        for tol in (0.0, 0.005, 0.01):
            equal_tolerance_test(a, pct, tol)


if __name__ == "__main__":
    if "--equal-tol" in sys.argv:
        run_equal_tol()
        sys.exit(0)
    sys.exit(main())
