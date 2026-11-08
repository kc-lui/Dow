# Dow Theory rule backtests: pre-registered decision table

Status: **frozen before the first backtest run**. Written 2026-11-08 by R12 (statistical verdict).
The sha256 of this file is stored in `analysis/decision_table.sha256` and written into every row of
`dow.str_rule_backtest_log.decision_table_hash`. Nothing above the `PROTOCOL-HASH-SCOPE` line may change
after the first label-driving run; see section 6 for what counts as a deviation and how it is logged.

Protocol history (pre-run edits only; none of these is a deviation because no backtest had run):
- v1 2026-11-08: initial version, primary spec pct 3%/10%; sha256 `d94a32e14531350d981f8dab6a6d248f1023fe8380a98af92dd54139a0bcbbc2`.
- v2 2026-11-08: aligned to the committed configuration of commit `5a3b907` (secondary 8%, 15-session
  causal filter, equal-extreme tolerance, line drift filter, cycle-aware confirmation, contract amendments
  A1-A9); 10% demoted to a robustness point; selection disclosure (1.8) and worst-grid-point rule for R4/R5
  added; R8 random-spell null added. No run had occurred.

Audience: backtest engineers (R10), methodology auditor (R11), statistical verdict (R12).
Everything here is expressed in terms of `docs/specs/algorithm_contract.md` objects (`Swing`, `Signal`,
`TrendState`, `LineRange`, `ConfirmationResult`, amendments A1-A9) and `configs/dow.yaml` at commit `5a3b907`.

---

## 0. Scope and data

| Item | Value |
|---|---|
| Primary pair (label-driving) | `DJ` = (`^DJI`, `^DJT`), `dow.mkt_klines` daily close, inner join on session date |
| Primary sample | 1992-01-02 to 2026-11-06 (8,775 bars; `period_end` is **fixed** at 2026-11-06 for every label-driving run; later backfills do not extend it) |
| Robustness pair (reported, never label-driving) | `SP_IYT` = (`SPY`, `IYT`), 2004 to 2026-11-06 |
| Price field | close only (Dow Theory uses closes; contract `detect_swings(close)`) |
| Return definition | daily log return `r_t = ln(P_t / P_{t-1})`; h-bar forward return from bar `s`: `F_h(s) = ln(P_{s+h} / P_s)` |
| **Primary specification** = committed `configs/dow.yaml` (commit `5a3b907`) | `swings.method="pct"`, `minor_pct=0.03`, `secondary_pct=0.08`, `secondary_min_sessions=15` (causal filter, A1), `per_symbol_secondary_pct={}` (both averages at 0.08); `trend.require_lower_high_for_reversal=true`, `trend.equal_extreme_tol=0.005` (A2); `line.band_pct=0.05`, `line.min_sessions=15`, `line.max_drift_frac=0.5` (A6); `confirmation.max_days=null` with cycle-aware matching (A7) |
| Config hash mechanism | every logged row carries `config_hash = dowtheory.config.config_hash()` of the configuration actually used. Label-driving rows must carry the hash of the committed file, which at the time of writing is `e6f5b9cd228e458809a42aa2a5c5e2811175de3d74fafca1a3496c6ac68ae24e`. A label-driving row whose `config_hash` differs from the committed value is invalid. Robustness rows carry the hash of their own (modified) configuration. |
| Robustness swing specifications | pct `secondary_pct in {0.05, 0.06, 0.10, 0.12}` with and without the 15-session filter; `^DJT` override `per_symbol_secondary_pct={'^DJT': 0.12}` (spec review 3b suggestion, unverified); `method="atr"` (`atr_mult=2.0`, `atr_window=14`, filter applies) and `method="pivot"` (`pivot_n=5`, filter does not apply) with contract multiscale widening. **Reported, not used for labels.** |
| Signals excluded from the family | `DEFENSE_BREAK` (agent-defined), `TREND_ESTABLISHED` (A4, warm-up artefact), `HH/HL/LH/LL` (building blocks, not rules); EQUAL swings per A2 emit no signal |
| Random seed | `numpy.random.default_rng(20261108)` for every bootstrap, permutation and placement test; one generator per (rule, pair, specification), re-seeded identically |

Analysis uses `FINAL` on ReplacingMergeTree reads and requires `scripts/check_integrity.py` exit 0 on the
run date (CLAUDE.md). The integrity report path is written into `notes` of every logged row.

---

## 1. Global rules

### 1.1 Significance and multiple testing

- Significance level `alpha = 0.05`.
- **Family** = the 8 primary p-values, one per rule R1-R8, all computed on pair `DJ` with the primary
  specification and the primary horizon/variant named in section 2. Holm step-down correction is applied to
  these 8 p-values exactly once. The Holm-adjusted p-value `p_holm` is what the label algorithm reads.
- Every other number (other horizons, `SP_IYT`, ATR/pivot, sweeps, sub-samples, the `^DJT`-side metrics,
  short variants, BGK-style call counts, simulated nulls) is **descriptive**: reported with its CI and raw
  p-value, never corrected, never used by `decide_label`.
- Directional rules (R1, R2, R3, R6, R7, R8) use **one-sided** tests in the direction the rule predicts.
  R4 and R5 use one-sided tests against the "no over-representation" null stated in their rows. The
  predicted direction is fixed here and may not be flipped after seeing data.
- **Refutation** uses a Bonferroni-level bound (level `1 - alpha/8`), see 1.4. Bonferroni is at least as
  strict as Holm, so a refutation can never be weaker than a confirmation.

### 1.2 Uncertainty quantification

| Statistic type | Interval | p-value | Iterations |
|---|---|---|---|
| Proportion of independent events (R1, R4, R5, R6, R7) | Wilson score interval | exact binomial, one-sided | n/a |
| Mean forward return conditional on event dates (R2, R3, R6 robustness) | percentile bootstrap over **event clusters** (events whose forward windows `[s, s+h]` overlap form one cluster; clusters resampled with replacement) | **random-placement test**: draw the same number of event bars uniformly at random from eligible bars (respecting the sample's minimum spacing between actual events), recompute the statistic, `p = (1 + #{stat* >= stat_obs}) / (B + 1)` one-sided | `B = 2000` |
| Two-group difference of event means (R3, R6 confirmed-vs-single) | percentile bootstrap, clusters resampled within group | permutation of group labels across events, one-sided | `B = 2000` |
| Series-level return metrics (R8 Sharpe difference, R8 cumulative return difference) | **stationary block bootstrap** (Politis-Romano, mean block length `20` bars) applied **jointly** to the aligned daily return vectors of strategy and benchmark (identical block indices) | one-sided: `p = (1 + #{Delta* <= 0}) / (B + 1)` | `B = 2000` |

- `bootstrap_iter = 2000`, `block_len = 20` come from `configs/dow.yaml: backtest`.
- Day clustering: whenever an event set has two events on the same bar (possible only when `^DJI` and
  `^DJT` events are pooled in a descriptive row) they form one cluster.
- Overlapping forward windows reduce effective n; the cluster bootstrap above is the only adjustment, and
  the report must state the number of clusters next to the number of events.

### 1.3 Minimum evidence

- **One-sample rules**: `n_events >= 30` (`backtest.min_n`), otherwise `insufficient-evidence` regardless of
  p-value.
- **Two-sample rules** (R3, R6 difference): `n_total >= 30` and each group `>= 10`.
- **Sub-sample consistency** (required for `data-confirmed` and for `data-refuted`):
  the sample is split at the **median calendar date of the pair's sample period, rounded to the preceding
  31 December**. For `DJ` (1992-01-02 to 2026-11-06) the split is **2009-12-31**: sub-sample A =
  1992-2009, sub-sample B = 2010-2026. For `SP_IYT` (2004-2026) the split is 2015-12-31. An event belongs
  to the sub-sample containing its event bar. Both sub-samples need `n >= 10`; if either has fewer, the
  consistency check is **not assessable** and the rule cannot be `data-confirmed` or `data-refuted`.
  Consistency means the **sign of (point estimate - null value)** agrees in both sub-samples; no
  significance is required within sub-samples.

### 1.4 Label definitions (applied by `decide_label`, section 3)

| Label | Condition |
|---|---|
| `data-confirmed` | `n` meets 1.3; `p_holm < 0.05` in the predicted direction; both sub-samples on the predicted side of the null |
| `data-refuted` | `n` meets 1.3; the one-sided `(1 - alpha/8)` confidence bound of the effect in the predicted direction lies **strictly on the wrong side** of the null value (i.e. the data exclude even a zero effect); both sub-samples on the wrong side of the null |
| `insufficient-evidence` | everything else, including "significant in one sub-sample only", "n too small", "wrong-side point estimate without exclusion of the null" |

A `data-confirmed` label does **not** assert economic significance; the effect size and its CI are
always reported next to the label.

### 1.5 No lookahead

- Every event bar is a bar at which the event was knowable: `Swing.confirmed_idx` for swings (the
  15-session filter is evaluated at the confirmation bar, A1), `Signal.idx` for signals (contract deviation
  5: signals are stamped at the confirmation bar), `LineRange.confirmed_ts` (A6) for pair-confirmed line
  breakouts, and for pair-confirmed reversals the `confirmed_ts` of the cycle-aware match (A7), which is
  the later of the two single-index dates.
- Trend state used at bar `c` is the `TrendState` snapshot of `run_trend` for bar `c` (after processing
  bar `c`). Pair-confirmation status at bar `c` uses only signals with `ts <= c` (A7).
- **Forward returns start at the bar after the event bar**: for event bar `c` and horizon `h`,
  `F_h(c) = ln(P_{c+1+h} / P_{c+1})`. The close at `c+1` proxies the next open. Events with
  `c + 1 + h > last_bar` are excluded and their count is reported.
- The unconditional benchmark for horizon `h` is the mean of `F_h(t)` over every bar `t` of the sample with
  `t + 1 + h <= last_bar`.
- R11 replays each label-driving run on truncated data (`close[:t+1]` for at least 5 cut dates) and
  requires identical event sets up to the cut.

### 1.6 Parameter sweeps and robustness

- Sweeps are reported as **ranges** (min, median, max of the primary metric over the grid) and as a
  table, never as a selected optimum, never as a label input (exception: the worst-grid-point rule of 1.8,
  which can only make a label harder to obtain).
- Sweep grid (run for every rule where the parameter matters):
  `secondary_pct in {0.05, 0.06, 0.08, 0.10, 0.12}` x `secondary_min_sessions in {0, 15}`,
  `minor_pct in {0.02, 0.03, 0.05}`, `equal_extreme_tol in {0, 0.005}`; `^DJT` override 0.12;
  R6 additionally `band_pct in {0.03, 0.05, 0.07}`, `min_sessions in {10, 15, 28}`,
  `max_drift_frac in {0.5, none}`; R8 additionally cost `{0, 10} bps/side`.
- ATR and pivot methods run with the contract defaults only (no sweep) and are reported side by side with
  pct.
- `SP_IYT` is reported for every rule with the same specification grid. If the `SP_IYT` primary point
  estimate has the opposite sign to the `DJ` estimate, the status table carries the note
  `pair-inconsistent`; the label is unaffected.

### 1.7 Logging convention for `dow.str_rule_backtest_log`

- `rule_id`: `R1` .. `R8`.
- `pair`: `DJ` or `SP_IYT`.
- `metric_name`: `<spec>|<variant>|<metric>|<horizon>` with `spec` in
  `{pct0.03/0.08f15` (primary), `pct<minor>/<secondary>f<sessions>`, `atr2.0/14f15`, `pivot5}`,
  `variant` in `{primary, sub_A, sub_B, djt_side, djt0.12, pooled, cost0, cost10, short, worst_grid,
  exploratory, ...}`, `horizon` in `{h20, h60, h120, na}`.
  Example: `pct0.03/0.08f15|primary|mean_excess_logret|h60`.
- `config_hash`: `dowtheory.config.config_hash()` of the configuration used for the row (section 0).
- `label`: one of the three data labels for the single label-driving row per rule (the `DJ`,
  `pct0.03/0.08f15`, `primary` row); every other row carries `n/a`.
- `literature_label`: carried from `research/canonical_rules.md` by `rule_key` (section 3); `unresolved` if
  the key is not yet present.
- `p_value`: the **raw** one-sided p-value; the Holm-adjusted value is written in `notes` as
  `p_holm=<value>` on the label-driving row.
- `notes`: integrity report path, number of event clusters, number of right-censored events, deviation ids
  (section 6), and the simulated-null p-values where section 2 asks for them.

### 1.8 Selection disclosure and the worst-grid-point rule

The primary specification was chosen in `reports/spec_review_p3.md` section 3b after inspecting, on the
**same** `^DJI` 1992-2026 sample, the following quantities at several `secondary_pct` values: swing counts,
share of reaction legs with retracement in [1/3, 2/3], share of reactions lasting 21-90 calendar days,
reversal counts, median confirmation lag and longest SUSPECT stall. The 8% + 15-session choice was
motivated in part by its Rhea-window duration share (67-73%). Consequences:

- The **R5** primary metric (`share_rhea`) and the **R4** primary metric (`share_band`) were seen before
  pre-registration. For these two rules the label-driving statistic is the **worst grid point**: the raw
  p-value entered into the Holm family is the **maximum** one-sided p-value over the grid
  `secondary_pct in {0.05, 0.06, 0.08, 0.10, 0.12}` with the 15-session filter on, and the Bonferroni bound
  used for refutation is the **least favourable** (for the predicted direction) bound over the same grid.
  Sub-sample consistency must hold at the primary point (0.08, f15). The primary-point estimate is still
  reported in full. This rule can only make `data-confirmed` harder, so it cannot inflate labels.
- No forward return, hit rate, volume ratio, Sharpe ratio or line-breakout outcome was inspected during
  the spec review (its tables contain none), so R1, R2, R3, R6, R7, R8 use the primary point directly.
- Reversal **counts** at 0.08 were seen (12 without, 10 with the filter on `^DJI`); this informs the
  expectations in section 5 but is not a metric of any rule.

---

## 2. Per-rule specification

Notation. `S = [S_1, S_2, ...]` is the list of confirmed **secondary** swings of the analysed index (pct
3%/8%, 15-session filter, nested on minor swings per contract `nest_scales`). `state(c)` is the
`TrendState` at bar `c`. A **leg** `L_k` is the move from `S_{k-1}` to `S_k`. An **EQUAL** swing (A2) is a
swing within `equal_extreme_tol` of the compared extreme. Horizons are in trading bars from
`configs/dow.yaml: backtest.horizons_days = [20, 60, 120]`.

### R1  Trend persistence (`rule_key: trend_persistence`)

| Field | Specification |
|---|---|
| Claim | A primary trend is more likely to continue than to reverse: the next swing in the trend direction extends the trend's extreme. |
| Event | Confirmed secondary swing `S_k` that is counter to the primary trend while the trend is established at its confirmation bar `c = S_k.confirmed_idx`: `S_k.kind == "L"` and `state(c).state == BULL_PRIMARY`, or `S_k.kind == "H"` and `state(c).state == BEAR_PRIMARY`. `SUSPECT` and `UNDEFINED` states are excluded. |
| Outcome | Bull case: success if `S_{k+1}` emits an `HH` signal (price above `state(c).last_H.price` by more than `equal_extreme_tol`). Bear case: success if `S_{k+1}` emits `LL`. An EQUAL `S_{k+1}` counts as **not extended** (the extreme was not exceeded); the EQUAL share is reported separately. Events whose `S_{k+1}` is not confirmed by `period_end` are excluded (right-censored; count reported). |
| Metric | `p_extend = successes / n_events` |
| Null | `H0: p_extend = 0.5`; predicted direction `> 0.5` |
| Test | exact binomial one-sided; Wilson 95% CI |
| Mandatory robustness (reported, in `notes`) | **drift-matched random-walk null**: 2000 stationary-block-bootstrap (block 20) resamples of the `^DJI` daily log returns, drift preserved, rebuilt into price paths, run through the identical `detect_multiscale` + `run_trend`, giving the null distribution of `p_extend`; report `p_sim`. The label uses the 0.5 null; if `p_sim >= 0.05` the status table note reads `not-distinguishable-from-random-walk-with-drift`. Also `equal_extreme_tol = 0` variant. |
| Horizons | n/a (swing-defined outcome) |
| Decision | section 1.4 with null 0.5 |

### R2  Reversal signal (`rule_key: primary_reversal_signal`)

| Field | Specification |
|---|---|
| Claim | A confirmed primary reversal (failed secondary swing followed by a break of the prior reaction extreme) predicts the subsequent primary direction. |
| Event | `Signal.kind in {REVERSAL_DOWN, REVERSAL_UP}` on `^DJI`, event bar `c = Signal.idx`. `DEFENSE_BREAK` (agent-defined) and `TREND_ESTABLISHED` (warm-up) excluded. Sign `sgn = -1` for `REVERSAL_DOWN`, `+1` for `REVERSAL_UP`. |
| Metric | `excess_h = mean_events( sgn * (F_h(c) - mean_t F_h(t)) )`. **Primary horizon `h = 60`**; `h = 120` secondary, `h = 20` descriptive. |
| Also reported | hit rate `P( sgn * F_h(c) > 0 )` with Wilson CI; the two signal kinds separately; `^DJT`-side signals measured on `^DJT`; pooled `^DJI`+`^DJT` with same-bar clustering (descriptive, roughly doubles n). |
| Null | `H0: excess_60 = 0`; predicted direction `> 0` |
| Test | random-placement test (1.2), eligible bars = all bars with `state(t).state != UNDEFINED`; CI = cluster bootstrap |
| Decision | section 1.4 with null 0. At the committed spec about 10 reversals exist on `^DJI` (spec review 3b), so `insufficient-evidence` is the expected and honest outcome; descriptive rows are still produced. |

### R3  Two-index confirmation (`rule_key: two_average_confirmation`)

| Field | Specification |
|---|---|
| Claim | Reversals confirmed by both averages are more reliable than unconfirmed ones. |
| Groups | **Confirmed**: a `^DJI` `REVERSAL_*` signal matched cycle-aware (A7) with the nearest same-kind `^DJT` signal in either order within the same primary cycle; event bar `c` = `confirmed_ts` (the later of the two dates). **Single**: a `^DJI` `REVERSAL_*` signal at bar `c` that has no cycle-aware match with `ts <= c + h` (evaluated with information up to `c + h` only for classification; forward return still starts at `c + 1`). A signal matched later than `c + h` is a confirmed event at its own `confirmed_ts`. Signs as in R2. All forward returns measured on `^DJI`. |
| Metric | `diff_h = excess_h(confirmed) - excess_h(single)`; **primary `h = 60`**; `h = 120` secondary; hit-rate difference reported |
| Null | `H0: diff_60 = 0`; predicted direction `> 0` |
| Test | permutation of group labels (2000), one-sided; CI = within-group cluster bootstrap |
| Minimum n | `n_total >= 30` and each group `>= 10` (1.3) |
| Robustness | `max_days = 90` confirmation window; `^DJT` at 0.12 override; `SP_IYT` |
| Decision | section 1.4 with null 0. With about 10 `^DJI` reversals the two-sample floor will not be met; `insufficient-evidence` expected. |

### R4  Secondary retracement (`rule_key: secondary_retracement`)

| Field | Specification |
|---|---|
| Claim (literature-disputed) | Secondary reactions typically retrace one third to two thirds of the preceding primary leg (variant: one third to one half). |
| Event | Every confirmed secondary swing with `retrace_ratio is not None` that terminates a **counter-trend** leg: the leg from `S_{k-1}` to `S_k` runs against `state(S_k.confirmed_idx).state` with the state in `{BULL_PRIMARY, BEAR_PRIMARY, BULL_SUSPECT, BEAR_SUSPECT}` (SUSPECT allowed because a deep retracement is exactly what produces SUSPECT). `UNDEFINED` excluded. `rr = S_k.retrace_ratio`; the indicator is `S_k.flags["retrace_in_third_two_thirds"]` (A5), which must equal `1/3 <= rr <= 2/3`. |
| Primary metric | `share_band = P( 1/3 <= rr <= 2/3 )` |
| Null | **uniform null**: if `rr` were uniform on `(0, 1]` the band share would be `1/3`. `H0: share_band = 1/3`; predicted direction `> 1/3` |
| Test | exact binomial one-sided; Wilson CI. **Label-driving p-value = worst grid point over `secondary_pct` (1.8).** |
| Also reported | observed median `rr` with bootstrap CI; `share_sf = P( 1/3 <= rr <= 1/2 )` = `flags["retrace_in_third_half"]` vs null `1/6`; `P( rr > 1 )` (full retracement or more); `P( rr < 1/3 )`; histogram deciles; a majority test `share_band` vs `0.5` (descriptive); the same shares over **all** legs (not only counter-trend) as in the spec review table |
| Mechanical caveat (must be printed) | With pct 8% swings a secondary leg is at least 8% of price, so `rr >= 0.08 / amplitude of the preceding leg`. Small preceding legs force high `rr`. The sweep over `secondary_pct` is therefore mandatory and the range is reported. |
| Decision | section 1.4 with null 1/3 using the worst-grid-point p-value and bound; sub-sample consistency at the primary point. |

### R5  Secondary duration (`rule_key: secondary_duration`)

| Field | Specification |
|---|---|
| Claim (literature-disputed) | Secondary reactions last about three weeks to three months (Rhea); variant: at least 8 trading days (Schannep). |
| Event | Same event set as R4 (confirmed counter-trend secondary swings). `d_cal = S_k.duration_days` (calendar days); `d_bar = S_k.idx - S_{k-1}.idx` (trading bars). |
| Primary metric | `share_rhea = P( 21 <= d_cal <= 90 )` = share of `flags["rhea_window"]` (A5; `swings.secondary_min_days` / `secondary_max_days`) |
| Null | `H0: share_rhea = 0.5`; predicted direction `> 0.5` ("typically" read as a majority) |
| Test | exact binomial one-sided; Wilson CI. **Label-driving p-value = worst grid point over `secondary_pct` (1.8)**, because the Rhea share was the selection criterion for 0.08. |
| Also reported | `share_schannep` = share of `flags["schannep_window"]` (`schannep_min_days`, `schannep_min_pct`), median and interquartile range of `d_cal`, `P( d_cal > 90 )`, `P( d_cal < 21 )`; the no-filter (`secondary_min_sessions = 0`) variant, since the 15-session filter mechanically removes short reactions and raises `share_rhea` |
| Mechanical caveat (must be printed) | The 15-session causal filter excludes secondaries shorter than 15 sessions (about 21 calendar days), so the lower Rhea bound is partly enforced by construction. The no-filter variant is the relevant comparison and must be printed next to the primary. |
| Decision | section 1.4 with null 0.5 using the worst-grid-point p-value and bound. The rule keeps `literature-disputed` whatever the data label. It can still be `data-refuted`: if the least favourable Bonferroni upper bound of `share_rhea` over the grid is below `0.5` and both sub-samples at the primary point are below `0.5`. |

### R6  Line breakout (`rule_key: line_breakout`)

| Field | Specification |
|---|---|
| Claim | A breakout from a Dow "line" (narrow sideways band in both averages) predicts continuation in the breakout direction, more reliably when both averages break the same way. |
| Event | `LineRange` from `detect_lines(close_DJI, close_DJT, band_pct=0.05, min_sessions=15, max_drift_frac=0.5)` with `breakout != "none"`. **Confirmed-both**: `confirmed_both == True` with event bar `c = confirmed_ts` (A6, the later of the two breakout dates; knowable then). **Single**: `confirmed_both` still `False` when evaluated with information up to `c + h`; event bar = the first breakout bar. Direction `sgn = +1` for `up`, `-1` for `down`. Forward returns measured on `^DJI`. |
| Primary metric | `agree_h = P( sgn * F_h(c) > 0 )` for confirmed-both breakouts, **primary `h = 20`**; `h = 60` secondary |
| Null | `H0: agree_20 = 0.5`; predicted direction `> 0.5` |
| Test | exact binomial one-sided; Wilson CI |
| Also reported | `agree_h` for single breakouts and the difference confirmed minus single (permutation test, two-sample minimum n per 1.3); `excess_h = mean( sgn * F_h(c) ) - mean_t F_h(t)` with random-placement `p` (drift-aware robustness, because a 0.5 sign null ignores index drift and upward breakouts inherit positive drift); number of lines, number of breakouts, mean line length |
| Sweep | `band_pct {0.03, 0.05, 0.07}` x `min_sessions {10, 15, 28}` x `max_drift_frac {0.5, none}`; ranges only |
| Decision | section 1.4 with null 0.5 on the confirmed-both `agree_20` |

### R7  Volume confirmation (`rule_key: volume_confirmation`)

| Field | Specification |
|---|---|
| Claim | Volume expands in the direction of the primary trend and contracts on reactions. |
| Sample | `^DJI` bars from **2000-01-03** onward only (index volume is sparse or zero earlier); the row's `period_start` is 2000-01-03. `SP_IYT` uses ETF volume from 2004. |
| Event | Consecutive leg pair `(L_k, L_{k+1})` of confirmed secondary swings where one leg is **with** the primary state and the other **against** it, state taken at the confirmation bar of the later swing, state in `{BULL_PRIMARY, BEAR_PRIMARY}`. Both legs must have strictly positive mean volume. Event bar = `S_{k+1}.confirmed_idx`. |
| Metric | `p_vol = P( mean_volume(with-trend leg) > mean_volume(counter-trend leg) )` where mean volume is over the bars `(S_{j-1}.idx, S_j.idx]` of the leg |
| Null | `H0: p_vol = 0.5`; predicted direction `> 0.5` |
| Test | exact binomial one-sided; Wilson CI |
| Robustness | volume normalised by its trailing 250-bar median before averaging (removes secular volume growth); the contract's `volume_confirms(df, swings)` boolean over rolling four-swing windows reported as a share of `True` |
| Decision | section 1.4 with null 0.5; if fewer than 30 leg pairs exist after 2000 the label is `insufficient-evidence` |

### R8  Hamilton-style timing strategy (`rule_key: hamilton_timing`)

| Field | Specification |
|---|---|
| Claim | Acting on Dow Theory signals (Hamilton's editorials, Brown-Goetzmann-Kumar 1998) beats buy-and-hold on a risk-adjusted basis. |
| Position rule (primary, long/cash) | at the close of bar `t`: `pos_t = 1` if `state_DJI(t).state == BULL_PRIMARY` and `pair_confirm(state_DJI(t), state_DJT(t)).status == "confirmed"` (state-level, A7 cycle-aware, information `<= t`); else `pos_t = 0`. **Variant (long/short)**: `pos_t = -1` if `state_DJI(t).state == BEAR_PRIMARY` and pair-confirmed. |
| Execution | daily rebalancing at the next open, proxied by the next close: the position decided at close `t` is held from close `t+1`, so the strategy's return on bar `t` is `r_s(t) = pos_{t-2} * r(t)` with `r(t) = ln(P_t / P_{t-1})` on `^DJI`. Cash earns 0 (stated assumption; conservative for the strategy). |
| Costs | `cost_t = kappa * abs(pos_{t-2} - pos_{t-3})` deducted from `r_s(t)` on the trade bar, `kappa in {0, 0.0010}` (0 and 10 bps per side). **Primary: 10 bps.** |
| Benchmark | buy-and-hold `^DJI` price index, same bars. Both legs exclude dividends; because the strategy is in cash part of the time, a price-index comparison **favours the strategy** (caveat printed). |
| Primary metric | `delta_sharpe = Sharpe(r_s, 10 bps) - Sharpe(r_bh)`, Sharpe = `mean / std * sqrt(252)` of daily log returns, risk-free 0 |
| Null | `H0: delta_sharpe = 0`; predicted direction `> 0` |
| Test | stationary block bootstrap (block 20, 2000, joint indices) on the aligned `(r_s, r_bh)` series; one-sided `p = (1 + #{delta* <= 0}) / 2001`; percentile 95% CI |
| Mandatory robustness (reported, in `notes`) | **random-spell null**: keep the realised long and cash spell lengths, shuffle their order 2000 times over the same return series, recompute `delta_sharpe`; report `p_spell`. The block bootstrap treats positions as given and so understates the uncertainty of a handful of regime calls; `p_spell` addresses that. If `p_spell >= 0.05` the status table note reads `not-distinguishable-from-random-timing`. |
| Also reported | annualised return and volatility of both legs, maximum drawdown, time in market, number of trades, cumulative log-return difference with bootstrap CI, the long/short variant, cost 0, `SP_IYT`, `^DJT` 0.12 override; sub-samples 1992-2009 / 2010-2026 |
| Right/wrong calls (descriptive, BGK analogue) | a **call** occurs at bar `c` when the pair-confirmed state first becomes `BULL_PRIMARY` (bull call) or `BEAR_PRIMARY` (bear call), including the initial `TREND_ESTABLISHED` entry (reported with the `meta.warmup_note`). A call is **right** if `ln(P_{c'+1} / P_{c+1})` has the called sign, where `c'` is the bar of the next call (or `period_end`). Report `right / wrong`, the share with Wilson CI and a two-sided binomial p vs 0.5. |
| Explicit caveat (must be printed verbatim) | "The 1992-2026 DJI/DJT sample cannot replicate Brown, Goetzmann and Kumar's 1902-1929 reconstruction of Hamilton's 255 editorials (110 right, 74 wrong, 71 neutral). Our calls are produced by a mechanical state machine, not by Hamilton's judgement, on a different century of data. Any comparison with 110/74 is descriptive and carries no label." |
| Minimum n | the primary metric is series-level; the `n >= 30` rule applies to the number of **position changes** (trades) of the primary long/cash strategy. Fewer than 30 trades gives `insufficient-evidence`. With about 10 `^DJI` reversals at the committed spec, roughly 20-25 position changes are expected, so this floor is likely binding; the descriptive rows are produced regardless. |
| Decision | section 1.4 with null 0 on `delta_sharpe` (10 bps, long/cash, `DJ`) |

### Summary of label-driving rows

| Rule | Event count `n` | Primary metric | Null | Direction | Test | Horizon | Label p-value |
|---|---|---|---|---|---|---|---|
| R1 | counter-trend secondary swings in `*_PRIMARY` | `p_extend` | 0.5 | > | binomial | swing | primary point |
| R2 | `REVERSAL_*` on `^DJI` | `excess_60` | 0 | > | random placement | 60 | primary point |
| R3 | confirmed vs single reversals | `diff_60` | 0 | > | permutation | 60 | primary point |
| R4 | counter-trend secondary swings | `share_band` | 1/3 | > | binomial | n/a | worst grid point (1.8) |
| R5 | counter-trend secondary swings | `share_rhea` | 0.5 | > | binomial | n/a | worst grid point (1.8) |
| R6 | confirmed-both line breakouts | `agree_20` | 0.5 | > | binomial | 20 | primary point |
| R7 | with/counter leg pairs, 2000+ | `p_vol` | 0.5 | > | binomial | n/a | primary point |
| R8 | trades (for n), series for metric | `delta_sharpe` (10 bps) | 0 | > | block bootstrap | series | primary point |

---

## 3. Label algorithm

```python
ALPHA = 0.05
FAMILY = ["R1", "R2", "R3", "R4", "R5", "R6", "R7", "R8"]
WORST_GRID_RULES = {"R4", "R5"}          # section 1.8
GRID_SECONDARY_PCT = [0.05, 0.06, 0.08, 0.10, 0.12]   # with secondary_min_sessions = 15
MIN_N = 30            # backtest.min_n
MIN_N_GROUP = 10      # per group in two-sample rules, per sub-sample for consistency
RULE_KEY = {"R1": "trend_persistence", "R2": "primary_reversal_signal",
            "R3": "two_average_confirmation", "R4": "secondary_retracement",
            "R5": "secondary_duration", "R6": "line_breakout",
            "R7": "volume_confirmation", "R8": "hamilton_timing"}

def holm_adjust(p_raw: dict[str, float]) -> dict[str, float]:
    """Holm step-down over the 8 primary raw one-sided p-values. Missing rules
    (insufficient n, metric undefined) enter with p = 1.0 so the family size stays 8."""
    items = sorted(p_raw.items(), key=lambda kv: kv[1])
    m, adj, running = len(items), {}, 0.0
    for rank, (rule, p) in enumerate(items):
        running = max(running, (m - rank) * p)
        adj[rule] = min(1.0, running)
    return adj

def sign_consistent(result, side: str) -> bool | None:
    """side = 'predicted' or 'wrong'. None when not assessable (a sub-sample has n < MIN_N_GROUP).
    Always evaluated at the primary point (0.08, f15)."""
    subs = [result.sub_A, result.sub_B]
    if any(s.n < MIN_N_GROUP for s in subs):
        return None
    d = [s.estimate - result.null_value for s in subs]
    if side == "predicted":
        return all(x > 0 for x in d)
    return all(x < 0 for x in d)

def n_ok(result) -> bool:
    if result.two_sample:
        return result.n_total >= MIN_N and min(result.n_group_a, result.n_group_b) >= MIN_N_GROUP
    return result.n >= MIN_N

def label_inputs(rule: str, primary, grid: dict[float, object]) -> tuple[float, float]:
    """Return (p_raw_for_family, bound_for_refutation).
    grid maps secondary_pct -> result at that point (f15), only used for WORST_GRID_RULES.
    bound_bonf is the one-sided (1 - ALPHA/8) confidence bound of the effect in the predicted
    direction; 'least favourable' = the one closest to / furthest beyond the null on the predicted side."""
    if rule not in WORST_GRID_RULES:
        return primary.p_raw, primary.bound_bonf
    pts = [grid[g] for g in GRID_SECONDARY_PCT if g in grid and n_ok(grid[g])]
    if not pts:
        return 1.0, primary.null_value          # cannot confirm, cannot refute
    p_worst = max(r.p_raw for r in pts)
    bound_worst = max(r.bound_bonf for r in pts)   # highest upper bound = hardest to refute
    return p_worst, bound_worst

def decide_label(rule: str, result, p_holm: dict[str, float], bound: float, canonical_rules) -> dict:
    """result: the DJ / pct0.03-0.08f15 / primary row of `rule`, with fields
       n, n_total, n_group_a, n_group_b, two_sample, estimate, null_value, p_raw, bound_bonf, sub_A, sub_B.
       bound: refutation bound from label_inputs."""
    lit = canonical_rules.get(RULE_KEY[rule], {}).get("literature_label", "unresolved")

    if not n_ok(result):
        return {"label": "insufficient-evidence", "literature_label": lit, "reason": "n below minimum"}

    if p_holm[rule] < ALPHA and sign_consistent(result, "predicted") is True:
        return {"label": "data-confirmed", "literature_label": lit, "reason": "p_holm<alpha, sub-samples agree"}

    wrong_side = (bound - result.null_value) < 0   # effect bound on the wrong side of the null
    if wrong_side and sign_consistent(result, "wrong") is True:
        return {"label": "data-refuted", "literature_label": lit, "reason": "Bonferroni bound excludes null, sub-samples agree"}

    reason = ("sub-sample consistency not assessable" if sign_consistent(result, "predicted") is None
              else "not significant after Holm, or sub-samples disagree")
    return {"label": "insufficient-evidence", "literature_label": lit, "reason": reason}

def label_all(primary_results: dict[str, object], grids: dict[str, dict[float, object]], canonical_rules) -> dict[str, dict]:
    inputs = {r: label_inputs(r, primary_results[r], grids.get(r, {})) for r in FAMILY}
    p_raw = {r: (inputs[r][0] if n_ok(primary_results[r]) else 1.0) for r in FAMILY}
    p_holm = holm_adjust(p_raw)
    return {r: decide_label(r, primary_results[r], p_holm, inputs[r][1], canonical_rules) for r in FAMILY}
```

Rules for the two label fields:

- `label` (data layer) is produced **only** by `decide_label` on the `DJ` primary row (with the worst-grid
  inputs for R4/R5). Humans do not override it. R12 writes the result into `analysis/rule_status_table.md`
  together with the effect size, CI, `n`, number of clusters, both sub-sample estimates, the `SP_IYT`
  estimate, the `config_hash`, and every note flag.
- `literature_label` is carried from `research/canonical_rules.md` by `rule_key` and is **independent** of
  the data label. A rule may be `literature-disputed` and `data-confirmed`, or `literature-consensus` and
  `data-refuted`; both fields are shown side by side. If the key is absent, the row is logged with
  `literature_label = unresolved` and must be resolved before any skill (P5) cites the row.
- The Dow defense line is `agent-defined` and is **not** in the family; `DEFENSE_BREAK` events may be
  reported descriptively (rule_id `R2x`, label `n/a`) but never receive a data label. The 8% secondary
  threshold itself is `agent-defined` (A9) and is reported as such wherever a label depends on it.

---

## 4. Multiple-testing and sweep policy

1. One Holm family of 8 tests, fixed above. Adding a rule, a horizon or a variant to the family after the
   first run is a protocol deviation (section 6).
2. Primary horizon, primary variant, primary null and direction are fixed per rule in section 2. They
   may not be changed after inspection of results.
3. Sweeps (1.6) are reported as ranges and tables. The text accompanying a sweep must not single out the
   best parameter. If a rule is `insufficient-evidence` at the primary specification but significant at
   another grid point, the label stays `insufficient-evidence` and the grid point is reported as
   `exploratory`. For R4/R5 the grid enters the label only through the worst point (1.8).
4. Robustness methods (ATR, pivot), robustness pair (`SP_IYT`), the 10% and other threshold points, the
   `^DJT` 0.12 override, confirmation-window variant, cost variants, long/short variant, pooled
   `^DJI`+`^DJT` rows, the drift-matched simulated null (R1) and the random-spell null (R8) carry raw
   p-values only and never enter the family.
5. Sub-sample results are reported but never tested for significance on their own; they serve only the
   sign-consistency check.
6. Any statistic not listed in section 2 that engineers find useful is logged with `variant = exploratory`
   and `label = n/a` and may not be cited in skills or the agent as evidence for a label.

---

## 5. Data-coverage caveats and expectations (to be printed with every report)

- `^DJT` history in `dow.mkt_klines` begins **1992-01-02**. Nothing in this protocol tests Dow Theory on
  1897-1991 data; claims about that period default to `insufficient-evidence` per `docs/team_design.md`
  section 5 unless a long-history source is loaded under a new, hashed protocol.
- `^DJI` 1992-01-02 to 2026-11-06 = 8,775 bars. At the committed spec (8%, 15-session filter) the spec
  review counted about 82 secondary swings, about 37 reaction legs and **10 primary reversals** on `^DJI`
  (12 without the filter, 8 at 10%). Hence the pre-run expectation: R2, R3 and probably R8 fall below the
  evidence floor and receive `insufficient-evidence`; R1, R4, R5 have `n` in the 30-40 range and are
  decidable but with wide intervals; R6 and R7 counts are unknown before the run. These are
  expectations, not thresholds; the labels follow section 3 whatever the counts turn out to be.
- Index volume is sparse or zero before 2000 and is a vendor-constructed aggregate afterward; R7 therefore
  starts 2000-01-03 and its `SP_IYT` robustness uses ETF volume (2004+).
- `^GSPC` and `^IXIC` have `analysis_start` clipping (first real OHLC 1962-07-02 and 1984-10-11); they are
  not used in any label-driving row. `IYT` begins 2004, so the `SP_IYT` pair covers 2004-2026 only.
- Price indices exclude dividends (R8 caveat). The `^DJI` series is yfinance-sourced; vendor revisions after
  2026-11-06 do not change the frozen `period_end` of label-driving runs.
- Forward windows overlap at `h = 60` and `h = 120`; effective sample sizes are smaller than `n`; the
  number of event clusters is reported next to `n` for every return-based row.
- The primary threshold was selected on this sample (1.8); R4 and R5 labels are therefore computed under
  the worst-grid-point rule and every R4/R5 report prints the full threshold range.

---

## 6. Protocol deviations

A **deviation** is any change, after the first label-driving run, to: an event definition, a null value, a
predicted direction, a primary horizon or variant, a test or bootstrap scheme, `alpha`, `MIN_N`, the
sub-sample split rule, the Holm family, the swing specification or configuration used for labels (any
change of the committed `config_hash`), the sample period, or the `decide_label` algorithm. Fixing an
implementation bug that makes the code match this document is **not** a deviation but must be recorded in
the run notes with the rows it invalidated. Edits made **before** the first label-driving run are not
deviations; they are recorded in the "Protocol history" at the top of this file with the superseded hash.

Every deviation must:

1. be appended to `analysis/protocol_deviations.md` as `DEV-<nn>` with date, author (role id), the exact
   text before and after, the reason, and whether results had already been seen for the affected rule;
2. result in a new `decision_table.sha256` (the amended table is re-hashed; the previous hash is kept in the
   deviations file);
3. be referenced by id in `notes` of every `str_rule_backtest_log` row produced afterwards;
4. keep every row produced before it (ReplacingMergeTree rows are versioned by `run_id`; never delete);
5. be listed in `analysis/rule_status_table.md` next to the affected rule with the sentence
   "label computed under DEV-<nn>".

A rule whose primary specification was changed after its results were seen is reported with the note
`post-hoc-modified` and its label is capped at `insufficient-evidence` for this project, whatever the
re-run shows. R11 verifies that the `decision_table_hash` on every label-driving row equals the hash in
`analysis/decision_table.sha256` that was current at the row's `inserted_at`, and that `config_hash`
equals the committed value in section 0.

PROTOCOL-HASH-SCOPE: everything above this line
