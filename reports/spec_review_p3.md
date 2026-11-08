# Spec review P3 (R8): algorithms vs `docs/specs/algorithm_contract.md`

Reviewer: R8 spec reviewer (quant-analyst). Commit reviewed: 1272b99. Date: 2026-11-08.
Scope: `src/dowtheory/{swings,trend,line,confirmation,levels,analysis,schema,chart,report}.py`, `tests/`, `configs/dow.yaml`, `outputs/json/DJI_DJT_2026-11-06_pct0.03.json`, `outputs/charts/DJI_DJT_2026-11-06_pct0.03.png`.
No file under `src/` or `tests/` was modified.

Evidence:
- `uv run --python .venv/bin/python pytest -q` gives **117 passed**.
- `dowtheory.cli analyze --symbol ^DJI --pair ^DJT --start 2015-01-01 --no-chart` gives BULL_PRIMARY since 2025-05-12, non_confirmation (DJT is BEAR_PRIMARY since 2026-09-24), defense line 45,166.64, 108 lines.
- Replay and statistics script: `reports/spec_review_p3_replay.py`. It is read-only against `dow.mkt_klines FINAL`, uses ^DJI/^DJT from 1992-01-02 to 2026-11-06 (8,775 common sessions) and runs in about 70 s. Section I (equal-extreme tolerance) runs with `--equal-tol`.

---

## 1. Rule to code mapping

| # | Dow rule | Implementing code | Matches contract? | Semantic concern |
|---|---|---|---|---|
| 1 | Three trends (primary / secondary / minor) | `swings.py:306-338` `detect_multiscale` (minor 3 %, secondary 10 %); primary = state of `trend.py:224-240` `run_trend` | Yes | The `primary` swing scale is never produced; the primary trend exists only as a state. The 10 % "secondary" zig-zag mostly returns **primary legs**: on ^DJI 1992-2026, 92 % of its legs last >= 21 days and amplitudes reach 97.9 % (2020-03 to 2022-01). Only 23 of 51 legs are reactions (retrace < 1). The 3 % minor scale never feeds the trend logic. |
| 2 | HH / HL definition | `trend.py:77-84` `_label`, `trend.py:112-121` `_record` | Yes | There is no equal-extreme tolerance. 2016-02-11 (15,660.18) is 0.04 % below 2015-08-25 (15,666.44), so it is labelled LL. Classical reading is a double bottom (failure to make a lower low). This single label causes the 2016-2018 stall (finding D3). |
| 3 | Reversal = LH then close below prior reaction low (mirror) | `trend.py:141-142, 148-149` (LH/HL sets SUSPECT + counter), `trend.py:171-176` `_on_close`, `trend.py:193-207` `_reverse`/`_flip` | Yes, including Deviation 6 | Strict mode deadlocks after a `DEFENSE_BREAK` without a counter swing: HH in a bear SUSPECT and LL in a bull SUSPECT are ignored (`trend.py:138-151`). Stalls reach 616 sessions (finding D3). |
| 4 | Closing prices only | `swings.py:229` (close array), `trend.py:237-238`, `line.py:81-82`, `levels.py:87` | Yes | The `atr` method uses high/low in the threshold only (Deviation 2). `analysis._atr` (`analysis.py:41-47`) uses high/low for the ATR level tolerance. Both are acceptable as volatility scales, not price signals. |
| 5 | 3 % rally/decline filter | `swings.py:83-85` `_moved`, `swings.py:233`, `configs/dow.yaml` `minor_pct: 0.03` | Yes (uses >= 3 % - eps; Rhea says "exceeding") | The status label `hamilton_3pct_filter` (`schema.py:17`) misattributes the rule. `research/sources/rhea-1932-the-dow-theory.md` states that the 3 % and 5 % filters are Rhea's and "neither is in Dow or Hamilton". The minor scale is used only for levels and the chart. |
| 6 | Secondary 1/3-2/3 retracement (flag only) | `swings.py:285-303` `compute_secondary_metrics` computes the raw `retrace_ratio` | Partly | No flag is emitted. The denominator is the previous opposite secondary leg. Rhea uses "the primary price change since the termination of the last preceding secondary reaction"; the two coincide only when the previous leg is a primary leg. |
| 7 | Secondary duration bounds (flag only) | `swings.py:299` raw `duration_days` only | Partly / flag not implemented | `secondary_min_days: 21`, `secondary_max_days: 90`, `schannep_min_days`, `schannep_min_pct` in `configs/dow.yaml` are **read by nothing** (no reference outside `config.py`). |
| 8 | Line: both averages within 5 % for >= 2-3 weeks, simultaneous breakout | `line.py:55-96` `detect_lines`, `line.py:28-40` `_window_end`, `line.py:43-52` `_first_breakout`, `line.py:108-129` `_build`; signals `analysis.py:92-106` | Yes vs contract and Deviation 9 | Windows need not be sideways: a steady 4.9 % trend qualifies. The "breakout" is always bar `end+1`, the bar that widened the joint range beyond 5 %. 57 of 108 lines (2015 onward) start on the previous line's breakout bar. `confirmed_both` has look-ahead (section 2). See section 3. |
| 9 | Two-average confirmation, no time window | `confirmation.py:52-94` `pair_confirm` (state level), `confirmation.py:37-49` `signal_confirmed` (signal level), `analysis.py:81-89` | State level: yes. Signal level: **no** | `signal_confirmed` with `max_days=None` ignores a DJT signal that **preceded** the DJI signal, so the leading average never counts. It also accepts any later same-kind DJT signal, even across cycles. The DJI REVERSAL_DOWN of 2022-09-23 is "confirmed" by a DJT REVERSAL_DOWN on 2026-09-24. The correct confirming signal (DJT 2022-04-08) is ignored. |
| 10 | Non-confirmation = warning | `confirmation.py:76-81`, rendered by `report.py:49-50` and the chart title | Yes | It is a status, not a dated warning signal. `pair_state` becomes `None` on non-confirmation, so the last **jointly confirmed** primary trend (the classical answer) is not reported. |
| 11 | Volume subordinate | `confirmation.py:97-121` `volume_confirms`; `analysis.py:222`; not an input to `run_trend` | Yes | ^DJI volume from Yahoo has a regime break in Dec 2016 (monthly mean volume rose from about 1.0e8 to 2.8e8). `persist.py:53` stores `None` (unknown) as 0 (false). |
| 12 | Defense line (agent-defined last reaction low/high) | `trend.py:143-144, 150-151` (HL/LH update), `trend.py:210-221` `_enter`/`_set_defense`, `levels.py:185-194`, chart label `chart.py:18` | Yes, labelled agent-defined everywhere | The line goes **stale** when SUSPECT returns to PRIMARY via HH/LL: it keeps an older HL instead of the latest reaction low. This happened 4 times on ^DJI at 10 % since 1992. Example: on 2020-02-27 the line stayed at 23,533 (2018-03-23) instead of 21,792 (2018-12-24). |
| 13 | S/R clustering | `levels.py:57-127` `cluster_levels`; inputs `analysis.py:178-187` (minor swings, Deviation 8) | Yes | No side filter. All four "resistance" zones (34,708 to 44,969) lie **below** the 51,286 close, and the highest is 12 % below. The levels set depends on `--start`. Greedy mean-joining (`levels.py:96-103`) lets a cluster spread beyond the tolerance. |
| 14 | Trendlines through last two reaction lows/highs | `levels.py:130-182` `fit_trendlines`; `analysis.py:188-192` | Yes | There is no `as_of` argument. Validity is correct only because `analysis` loads data cut at `as_of`, and a backtest caller passing full closes would leak. `touches` is almost always 2 because the line uses two secondary swings that are often a year apart. |

---

## 2. Look-ahead audit

Method: for each sampled bar t, the pipeline was re-run on `close[:t+1]` and compared with the full-history output restricted to what was knowable at t. Bars were sampled every 25 sessions, plus every secondary confirmation bar and the bar before it. See `reports/spec_review_p3_replay.py`, sections A to E.

| Item | Code | Verdict | Evidence |
|---|---|---|---|
| Swing confirmation, pct | `swings.py:99-128` | **PASS** | 438 bars on ^DJI and 565 on ^DJT: 0 mismatches for both minor and secondary swings. A flip is stamped on the bar that crosses the threshold, and `_arg_extreme` scans only `cand+1..i`. |
| Swing confirmation, atr | `swings.py:65-74, 236` | **PASS** | 462 bars, 0 mismatches. The rolling ATR is trailing, and a NaN threshold never flips. |
| Pivot `i+n` | `swings.py:131-169` | **PASS** | 887 bars, 0 mismatches. The centred window is fully observed at `i+n = confirmed_idx`. The inserted opposite swing is stamped with the second pivot's confirmation, and emission is append-only (Deviation 1). |
| `nest_scales` snapping | `swings.py:252-282` | **PASS** | `confirmed_idx = max(secondary, minor)`; it is covered by the secondary-scale comparison above. |
| `retrace_ratio` / amplitude / duration | `swings.py:285-303` | **PASS** | They use swings k-1 and k-2 only, and they are part of the full `Swing` equality check above. |
| Trend state, defense line, signals | `trend.py:224-240` | **PASS** | 390 (^DJI) and 451 (^DJT) bars: state, `since`, `defense_line`, `secondary_direction` and the signal prefix are all identical. |
| `secondary_direction` | `trend.py:120` | **PASS** | It is set only from a swing on its confirmation bar. It lags economically (see D10). |
| Trendline validity "between p0 and as_of" | `levels.py:164-173` | **PASS (conditional)** | 85 bars, 0 mismatches against full swings filtered at t. It is safe only because the caller truncates `closes`. Add an `as_of` parameter (D14). |
| Level clustering on future swings | `analysis.py:178-187`, `levels.py:57-127` | **PASS** | Only `swings_as_of(minor, last)` is used; same 85-bar replay, 0 mismatches. |
| Line geometry and breakout bar | `line.py:55-129` | **PASS** | All 299 lines (1992 onward) re-run with `as_of_idx = breakout bar`: start, end, direction and breakout_ts are identical. |
| Line `confirmed_both` | `line.py:123-126`, `analysis.py:104` | **FAIL** | 104 of 299 lines show `confirmed_both = False` at their breakout bar but True in the full run. `LineRange` has no confirmation date, so a backtest that reads `LINE_BREAKOUT_*.confirmation` at `breakout_ts` uses the future. This also breaks the contract preamble ("every derived object carries the bar index at which it became knowable"). |
| Per-signal pair confirmation | `confirmation.py:37-49`, `analysis.py:81-89`, `pair_confirm` detail `confirmation.py:86-93` | **FAIL** | All three DJI reversals since 2015 are unconfirmed at their own date. Two become "confirmed" only through DJT signals 17 months and 4 years later: 2018-08-27 via 2020-01-14, and 2022-09-23 via 2026-09-24. No confirmation timestamp is stored. |

---

## 3. Economic sanity

### 3a. Lines

- **Days are trading sessions.** `line.py:91` tests `end - i + 1 < min_days` on bar positions, so `min_days: 14` means 14 sessions, about 2.8 calendar weeks. Rhea's "two to three weeks or longer" equals 10-15 sessions, so 14 is inside the range. The literal reading of "or longer" suggests **15 sessions** (3 trading weeks) as the floor.
- **Duration is not the driver of the count.** A joint 5 % band is the normal state of the market, not a consolidation:

| Window (sessions) | Share of windows, both averages <= 5 % | Both <= 3 % |
|---|---|---|
| 10 | 64 % | 23 % |
| 14 | 45 % | 9 % |
| 15 | 41 % | 7 % |
| 20 | 25 % | 2 % |

(2015 onward; the 1992 onward figures are within 2 points.)

- Line counts, 2015-01-01 to 2026-11-06 (11.8 years):

| band | min sessions | lines | per year | chained to previous breakout | sideways (net drift <= band/2 in both) |
|---|---|---|---|---|---|
| 0.05 | 14 (current) | 108 | 9.1 | 57 | 42 |
| 0.05 | 15 | 95 | 8.0 | 44 | 41 |
| 0.05 | 20 | 59 | 5.0 | 22 | 23 |
| 0.04 | 15 | 72 | 6.1 | 18 | 26 |
| 0.03 | 15 | 38 | 3.2 | 5 | 10 |

- **Recommendation.** Keep `band_pct: 0.05` because it is the literature figure. Set `min_days: 15` and document it as sessions. Add a sideways condition: net drift from start to end <= `band_pct/2` in both averages. This gives about 41 lines in 11.8 years (3.5 per year), or 103 over 1992 onward (3.0 per year). It also removes most chained "lines" that are really trend segments. The breakout should require a close beyond the band edge in both averages, with its own confirmation date.
- **Temporal overlap.** The implementation already requires both averages to stay in band over the **same** window (`line.py:88-90`, `_joint_end`). Keep full overlap. Rhea's "both averages move within a range" describes one joint period, and partial overlap would make "simultaneous breakout" ill-defined.

### 3b. `secondary_pct: 0.10`

Rhea's own screen (via Blay/Fraser p.61) discarded reactions "shorter than 15 days or smaller than 5 per cent". The duration flag is 21-90 calendar days, matching `secondary_min/max_days`. All figures are ^DJI 1992 onward.

| secondary_pct | swings | reaction legs (retrace < 1) | reactions with retrace 1/3-2/3 | reactions lasting 21-90 d | all legs with retrace 1/3-2/3 | counter-trend legs with retrace 1/3-2/3 | reversals | median confirm lag (bars) | longest SUSPECT (sessions) |
|---|---|---|---|---|---|---|---|---|---|
| 0.05 | 222 | 106 | 42 % | 41 % | 20 % | 32 % | 36 | 7 | 414 |
| 0.06 | 170 | 82 | 46 % | 49 % | 23 % | 38 % | 32 | 10 | 469 |
| 0.08 | 88 | 39 | 46 % | **67 %** | 21 % | 33 % | 12 | 16 | 575 |
| **0.10** | 53 | 23 | 39 % | 57 % | 18 % | 29 % | 8 | 23 | 616 |
| 0.05 + 15-day causal time filter | 166 | 77 | 43 % | 61 % | n/a | n/a | 28 | 13 | 414 |
| 0.08 + 15-day causal time filter | 82 | 37 | 49 % | **73 %** | n/a | n/a | 10 | 19 | 575 |

Judgement:
- **0.10 is too coarse.** Only about 23 reactions occur in 35 years, the median confirmation lag is 23 sessions, and the 2023 correction of about 9 % is invisible. Since 2015 it yields only 4 reversals, two of which arrive 2+ years late.
- The retracement band is a weak discriminator at every threshold. At most 46 % of reactions fall in 1/3-2/3, and 18-23 % of all legs do. This supports keeping it as a flag only, labelled `literature-disputed`.
- **0.08 gives the most Rhea-like secondaries.** It has the highest share of reactions inside the duration band, with retracement share tied for best, and adding a 15-day time qualification improves both shares.
- **Recommendation.** Set `secondary_pct: 0.08` for ^DJI. Implement the 15-day minimum inside the zig-zag flip condition, which stays causal and append-only (prototype in `time_qualified_zigzag`). Emit retracement and duration flags.
- **Per-symbol thresholds.** ^DJT at 10 % produces 119 swings versus 53 on ^DJI, so the two averages are judged on different scales. That biases confirmation. Add a per-symbol override (about 0.12 for ^DJT gives a swing count comparable to ^DJI at 0.08; verify before adopting) or use volatility-scaled thresholds.

---

## 4. Defects and edge cases, ranked

| Rank | Severity | Defect | Location | Fix |
|---|---|---|---|---|
| D1 | High | Signal-level confirmation ignores a leading DJT signal and accepts any later same-kind DJT signal across cycles. Status is computed at as_of without a date (look-ahead FAIL). | `confirmation.py:37-49`, `analysis.py:81-89` | Confirm A's signal by B's most recent same-kind signal with no opposite-kind B signal in between, in **either order**. Set `confirmed_ts = max(ts_a, ts_b)` and store `confirmed_idx`. Evaluate as of each bar. |
| D2 | High | `LineRange.confirmed_both` and `LINE_BREAKOUT_*.confirmation` use the other average's later break with no date (104 of 299 lines change). | `line.py:123-126`, `analysis.py:104` | Add `confirmed_ts`/`confirmed_idx` to `LineRange`; report `pending` until then. |
| D3 | High (economic) | Strict-mode deadlock: after `DEFENSE_BREAK` without a counter swing, SUSPECT waits for a counter swing at secondary scale while HH (bear side) or LL (bull side) swings are ignored. ^DJI at 10 % stalled from 2016-04-14 for 597 sessions (+45.3 % close change) and from 2022-11-23 for 616 sessions (+24.0 %). The 2016 case also appears at 6 % and 8 %. | `trend.py:138-151, 171, 175` | (a) Add an equal-extreme tolerance in `_label`: within 0.5 % counts as the counter swing (double top/bottom). The prototype restores the 2016-04-14 REVERSAL_UP at both 6 % and 10 %. (b) In SUSPECT-via-break, accept a minor-scale counter swing that passes Rhea's 5 %/15-day screen. Mark it agent-defined in the contract. |
| D4 | Medium | Defense line goes stale when SUSPECT returns to PRIMARY via a new extreme; LL in a bull and HH in a bear never update it. 4 cases at 10 % since 1992. | `trend.py:139-140, 146-147` | On HH in BULL_SUSPECT, set defense to `last_L` (latest reaction low); mirror for bears. |
| D5 | Medium | `UNDEFINED -> BULL/BEAR_PRIMARY` emits no signal. With `--start 2015-01-01` the 2016 bear starts silently on 2016-03-14. With a 1992 start the same period gives REVERSAL_DOWN on 2016-02-11, so results depend on the start date. | `trend.py:153-161`, `analysis.py:145` | Emit `ESTABLISHED_BULL/BEAR`. Warm up from the earliest bar and slice the output to `--start`. |
| D6 | Medium | Lines are not required to be sideways, are chained, and the breakout is merely range expansion. | `line.py:28-52, 87-95` | Use a 15-session minimum and a drift filter. Require the breakout beyond the band edge with dual-average timing (section 3a). |
| D7 | Medium | Resistance and support levels are not side-filtered: all four resistance zones are below the current close. | `levels.py:122-127`, `analysis.py:186-187` | Keep resistance > ref and support < ref, or relabel by polarity (former resistance becomes support). |
| D8 | Medium | Retracement and duration flags are absent; their config keys are dead. | `swings.py:285-303`, `configs/dow.yaml` | Add `retrace_in_band` and `duration_in_bounds` to Swing and JSON, labelled `literature-disputed`. Wire `secondary_min/max_days`, or delete the keys. |
| D9 | Medium | The same pct threshold is applied to ^DJI and the more volatile ^DJT. | `analysis.py:157-166` | Use a per-symbol threshold override or volatility scaling. |
| D10 | Low | `secondary_direction` is the direction of the current secondary-scale leg, not a secondary reaction. It shows "up" through a 9 % pullback and flips only after the full threshold. | `trend.py:120` | Rename it or add `reaction_in_progress` derived from minor swings since the last secondary extreme. |
| D11 | Low | The status label `hamilton_3pct_filter` misattributes Rhea's 3 % rule. | `schema.py:17` | Rename to `rhea_3pct_filter`, or state the provenance. |
| D12 | Low | `volume_confirms = None` is persisted as 0. ^DJI volume has a Dec 2016 regime break. | `persist.py:53` | Use a Nullable column. Note the break, or use SPY/DIA volume. |
| D13 | Low | `fit_trendlines` has no `as_of` and relies on caller truncation. | `levels.py:130-173` | Add an `as_of` argument and clip `closes`. |
| D14 | Low | `nest_scales` flags are discarded, although the contract says they are returned alongside. | `swings.py:337` | Return them or attach them to the swing metadata. |
| D15 | Low | Greedy clustering against a running mean lets a cluster's spread exceed `tol_pct`. | `levels.py:96-103` | Compare against the cluster's first member, or cap max-min at the tolerance. |
| D16 | Low | `pair_state` is `None` under non-confirmation, so the last jointly confirmed trend is lost. | `confirmation.py:76-81` | Add `joint_primary` (last direction confirmed by both) and its date. |

Edge cases verified as correct: flat series give no swings; NaN closes raise; same-bar LH confirmation plus a close below defense reverses on that bar (`tests/unit/test_trend.py:142`); misaligned pairs raise; `as_of_idx` hides future breakouts (`tests/unit/test_line.py:47`).

Missing tests:
- Signal confirmation when B leads A.
- Confirmation across cycles.
- `confirmed_both` evaluated at the breakout bar.
- Defense-line refresh on return to PRIMARY.
- Resistance above price.

---

## 5. Verdict per rule

| Rule | Verdict |
|---|---|
| Three trends | Partly: primary exists as state only, and the "secondary" scale mixes primary legs and reactions. |
| HH/HL definition | Implemented, with no equal-extreme tolerance. |
| Reversal (LH + break of reaction low, mirror) | Implemented; the economic deadlock is D3. |
| Closing prices only | Implemented. |
| 3 % filter | Implemented; it is misattributed to Hamilton and not used by the trend logic. |
| Secondary 1/3-2/3 retracement flag | Partly: the raw ratio exists but no flag. |
| Secondary duration bounds flag | Partly: raw duration exists, but no flag and the config is unused. |
| Line (5 %, 2-3 weeks, simultaneous breakout) | Partly: the windows are trend segments and `confirmed_both` has look-ahead. |
| Two-average confirmation, no time window | Partly: state level correct, signal level wrong (D1). |
| Non-confirmation = warning | Implemented as a status; no joint state is kept. |
| Volume subordinate | Implemented. |
| Defense line (agent-defined) | Implemented and labelled; stale-line defect D4. |
| S/R clustering | Partly: no side filter (D7). |
| Trendlines through last two reaction lows/highs | Implemented, with the conditional as_of safety noted in D13. |

None of the rules is unalgorithmizable. The discretionary parts are "importance" of a secondary and Hamilton's reading of lines, and those stay flags with literature-disputed labels.

## Recommended config changes

```yaml
swings:
  secondary_pct: 0.08          # was 0.10; best Rhea duration fit (67 % of reactions in 21-90 d), lag 16 vs 23 bars
  secondary_min_days: 15       # was 21 and unused; Rhea's 15-day screen, to be wired into the zig-zag flip (code change)
  secondary_max_days: 90       # keep; flag only once wired
  # per-symbol override needed for ^DJT (~0.12, verify) - requires contract/config support
line:
  band_pct: 0.05               # keep (literature)
  min_days: 15                 # was 14; sessions = 3 trading weeks; add max_drift_frac: 0.5 (code change)
confirmation:
  max_days: null               # keep per contract, but fix cycle-aware matching (D1)
trend:
  require_lower_high_for_reversal: true   # keep; add equal_extreme_tol: 0.005 (code change, D3)
```
