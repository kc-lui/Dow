# Dow Theory rule backtests: pre-registered decision table

Status: **frozen before the first backtest run**. Written 2026-11-08 by R12 (statistical verdict).
The sha256 of this file is stored in `analysis/decision_table.sha256` and written into every row of
`dow.str_rule_backtest_log.decision_table_hash`. Nothing above the `PROTOCOL-HASH-SCOPE` line may change
after the first label-driving run; see section 6 for what counts as a deviation and how it is logged.

Audience: backtest engineers (R10), methodology auditor (R11), statistical verdict (R12).
Everything here is expressed in terms of `docs/specs/algorithm_contract.md` objects (`Swing`, `Signal`,
`TrendState`, `LineRange`, `ConfirmationResult`) and `configs/dow.yaml`.

---

## 0. Scope and data

| Item | Value |
|---|---|
| Primary pair (label-driving) | `DJ` = (`^DJI`, `^DJT`), `dow.mkt_klines` daily close, inner join on session date |
| Primary sample | 1992-01-02 to 2026-11-06 (8,775 bars; `period_end` is **fixed** at 2026-11-06 for every label-driving run; later backfills do not extend it) |
| Robustness pair (reported, never label-driving) | `SP_IYT` = (`SPY`, `IYT`), 2004 to 2026-11-06 |
| Price field | close only (Dow Theory uses closes; contract `detect_swings(close)`) |
| Return definition | daily log return `r_t = ln(P_t / P_{t-1})`; h-bar forward return from bar `s`: `F_h(s) = ln(P_{s+h} / P_s)` |
| Primary swing specification | `method="pct"`, `minor_pct=0.03`, `secondary_pct=0.10` (`configs/dow.yaml: swings`) |
| Robustness swing specifications | `method="atr"` (`atr_mult=2.0`, `atr_window=14`) and `method="pivot"` (`pivot_n=5`) with contract multiscale widening; **reported, not used for labels** |
| Trend state machine | `require_lower_high_for_reversal: true` (strict mode); `DEFENSE_BREAK` signals are agent-defined and excluded from the R1-R8 family |
| Pair confirmation | `confirmation.max_days: null` as configured; the robustness run uses `max_days=90` |
| Random seed | `numpy.random.default_rng(20261108)` for every bootstrap, permutation and placement test; one generator per (rule, pair, specification), re-seeded identically |

Analysis uses `FINAL` on ReplacingMergeTree reads and requires `scripts/check_integrity.py` exit 0 on the
run date (CLAUDE.md). The integrity report path is written into `notes` of every logged row.

---

## 1. Global rules

### 1.1 Significance and multiple testing

- Significance level `alpha = 0.05`.
- **Family** = the 8 primary p-values, one per rule R1-R8, all computed on pair `DJ` with the primary
  swing specification and the primary horizon/variant named in section 2. Holm step-down correction is
  applied to these 8 p-values exactly once. The Holm-adjusted p-value `p_holm` is what the label algorithm reads.
- Every other number (other horizons, `SP_IYT`, ATR/pivot, sweeps, sub-samples, the `^DJT`-side metrics,
  short variants, BGK-style call counts) is **descriptive**: reported with its CI and raw p-value, never
  corrected, never used by `decide_label`.
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

- Every event bar is a bar at which the event was knowable: `Swing.confirmed_idx` for swings,
  `Signal.idx` for signals (contract deviation 5: signals are stamped at the confirmation bar),
  `LineRange.breakout_ts` for line breakouts, and for pair-confirmed events the **later** of the two
  single-index event bars.
- Trend state used at bar `c` is the `TrendState` snapshot of `run_trend` for bar `c` (after processing
  bar `c`).
- **Forward returns start at the bar after the event bar**: for event bar `c` and horizon `h`,
  `F_h(c) = ln(P_{c+1+h} / P_{c+1})`. The close at `c+1` proxies the next open. Events with
  `c + 1 + h > last_bar` are excluded and their count is reported.
- The unconditional benchmark for horizon `h` is the mean of `F_h(t)` over every bar `t` of the sample with
  `t + 1 + h <= last_bar`.
- R11 replays each label-driving run on truncated data (`close[:t+1]` for at least 5 cut dates) and
  requires identical event sets up to the cut.

### 1.6 Parameter sweeps and robustness

- Sweeps are reported as **ranges** (min, median, max of the primary metric over the grid) and as a
  table, never as a selected optimum, never as a label input.
- Sweep grid (run for every rule where the parameter matters):
  `secondary_pct in {0.08, 0.10, 0.12, 0.15}`, `minor_pct in {0.02, 0.03, 0.05}`; R6 additionally
  `band_pct in {0.03, 0.05, 0.07}`, `min_days in {14, 28}`; R8 additionally cost `{0, 10} bps/side`.
- ATR and pivot methods run with the contract defaults only (no sweep) and are reported side by side with
  pct.
- `SP_IYT` is reported for every rule with the same specification grid. If the `SP_IYT` primary point
  estimate has the opposite sign to the `DJ` estimate, the status table carries the note
  `pair-inconsistent`; the label is unaffected.

### 1.7 Logging convention for `dow.str_rule_backtest_log`

- `rule_id`: `R1` .. `R8`.
- `pair`: `DJ` or `SP_IYT`.
- `metric_name`: `<spec>|<variant>|<metric>|<horizon>` with `spec` in
  `{pct0.03/0.10, pct<minor>/<secondary>, atr2.0/14, pivot5}`, `variant` in `{primary, sub_A, sub_B,
  djt_side, pooled, cost0, cost10, short, ...}`, `horizon` in `{h20, h60, h120, na}`.
  Example: `pct0.03/0.10|primary|mean_excess_logret|h60`.
- `label`: one of the three data labels for the single label-driving row per rule (the `DJ`,
  `pct0.03/0.10`, `primary` row); every other row carries `n/a`.
- `literature_label`: carried from `research/canonical_rules.md` by `rule_key` (section 3); `unresolved` if
  the key is not yet present.
- `p_value`: the **raw** one-sided p-value; the Holm-adjusted value is written in `notes` as
  `p_holm=<value>` on the label-driving row.
- `notes`: integrity report path, number of event clusters, number of right-censored events, deviation ids
  (section 6), and the simulated-null p-value where section 2 asks for one.

---

## 2. Per-rule specification

Notation. `S = [S_1, S_2, ...]` is the list of confirmed **secondary** swings of the analysed index (pct
3%/10%, nested on minor swings per contract `nest_scales`). `state(c)` is the `TrendState` at bar `c`.
A **leg** `L_k` is the move from `S_{k-1}` to `S_k`. Horizons are in trading bars from
`configs/dow.yaml: backtest.horizons_days = [20, 60, 120]`.

### R1  Trend persistence (`rule_key: trend_persistence`)

| Field | Specification |
|---|---|
| Claim | A primary trend is more likely to continue than to reverse: the next swing in the trend direction extends the trend's extreme. |
| Event | Confirmed secondary swing `S_k` that is counter to the primary trend while the trend is established at its confirmation bar `c = S_k.confirmed_idx`: `S_k.kind == "L"` and `state(c).state == BULL_PRIMARY`, or `S_k.kind == "H"` and `state(c).state == BEAR_PRIMARY`. `SUSPECT` and `UNDEFINED` states are excluded. |
| Outcome | Bull case: success if `S_{k+1}.kind == "H"` and `S_{k+1}.price > state(c).last_H.price` (an HH). Bear case: success if `S_{k+1}.price < state(c).last_L.price` (an LL). Events whose `S_{k+1}` is not confirmed by `period_end` are excluded (right-censored; count reported). |
| Metric | `p_extend = successes / n_events` |
| Null | `H0: p_extend = 0.5`; predicted direction `> 0.5` |
| Test | exact binomial one-sided; Wilson 95% CI |
| Mandatory robustness (reported, in `notes`) | **drift-matched random-walk null**: 2000 stationary-block-bootstrap (block 20) resamples of the `^DJI` daily log returns, drift preserved, rebuilt into price paths, run through the identical `detect_multiscale` + `run_trend`, giving the null distribution of `p_extend`; report `p_sim`. The label uses the 0.5 null; if `p_sim >= 0.05` the status table note reads `not-distinguishable-from-random-walk-with-drift`. |
| Horizons | n/a (swing-defined outcome) |
| Decision | section 1.4 with null 0.5 |

### R2  Reversal signal (`rule_key: primary_reversal_signal`)

| Field | Specification |
|---|---|
| Claim | A confirmed primary reversal (failed secondary swing followed by a break of the prior reaction extreme) predicts the subsequent primary direction. |
| Event | `Signal.kind in {REVERSAL_DOWN, REVERSAL_UP}` on `^DJI`, event bar `c = Signal.idx`. `DEFENSE_BREAK` excluded (agent-defined). Sign `sgn = -1` for `REVERSAL_DOWN`, `+1` for `REVERSAL_UP`. |
| Metric | `excess_h = mean_events( sgn * F_h(c) ) - mean_all_bars( sgn_free benchmark )` where the benchmark for a `REVERSAL_DOWN` event is `-mean_t F_h(t)` and for a `REVERSAL_UP` event `+mean_t F_h(t)`; equivalently `excess_h = mean_events( sgn * (F_h(c) - mean_t F_h(t)) )`. **Primary horizon `h = 60`**; `h = 120` secondary, `h = 20` descriptive. |
| Also reported | hit rate `P( sgn * F_h(c) > 0 )` with Wilson CI; the two signal kinds separately; `^DJT`-side signals measured on `^DJT`; pooled `^DJI`+`^DJT` with same-bar clustering. |
| Null | `H0: excess_60 = 0`; predicted direction `> 0` |
| Test | random-placement test (1.2), eligible bars = all bars with `state(t).state != UNDEFINED`; CI = cluster bootstrap |
| Decision | section 1.4 with null 0; expect low n (primary reversals are rare at 10%): `insufficient-evidence` is the honest outcome when `n < 30` |

### R3  Two-index confirmation (`rule_key: two_average_confirmation`)

| Field | Specification |
|---|---|
| Claim | Reversals confirmed by both averages are more reliable than unconfirmed ones. |
| Groups | **Confirmed**: event bar `c` = first bar at which `pair_confirm(state_DJI(c), state_DJT(c)).status == "confirmed"` with `pair_state in {BEAR_PRIMARY, BULL_PRIMARY}` following a `REVERSAL_*` signal on either index (i.e. the later of the two reversal bars). **Single**: `REVERSAL_*` signals on `^DJI` at bar `c` for which `pair_confirm(...)` at `c` is `non_confirmation` or `pending`, and no confirmed event occurs within the next `h` bars (otherwise the event is re-classified as the confirmed event at its later bar). Signs as in R2. All forward returns measured on `^DJI`. |
| Metric | `diff_h = excess_h(confirmed) - excess_h(single)`; **primary `h = 60`**; `h = 120` secondary; hit-rate difference reported |
| Null | `H0: diff_60 = 0`; predicted direction `> 0` |
| Test | permutation of group labels (2000), one-sided; CI = within-group cluster bootstrap |
| Minimum n | `n_total >= 30` and each group `>= 10` (1.3) |
| Robustness | `max_days = 90` confirmation window; `SP_IYT` |
| Decision | section 1.4 with null 0 |

### R4  Secondary retracement (`rule_key: secondary_retracement`)

| Field | Specification |
|---|---|
| Claim (literature-disputed) | Secondary reactions typically retrace one third to two thirds of the preceding primary leg (variant: one third to one half). |
| Event | Every confirmed secondary swing with `retrace_ratio is not None` that terminates a **counter-trend** leg: the leg from `S_{k-1}` to `S_k` runs against `state(S_k.confirmed_idx).state` with the state in `{BULL_PRIMARY, BEAR_PRIMARY, BULL_SUSPECT, BEAR_SUSPECT}` (SUSPECT allowed because a deep retracement is exactly what produces SUSPECT). `UNDEFINED` excluded. `rr = S_k.retrace_ratio`. |
| Primary metric | `share_band = P( 1/3 <= rr <= 2/3 )` |
| Null | **uniform null**: if `rr` were uniform on `(0, 1]` the band share would be `1/3`. `H0: share_band = 1/3`; predicted direction `> 1/3` |
| Test | exact binomial one-sided; Wilson CI |
| Also reported | observed median `rr` with bootstrap CI; `share_sf = P( 1/3 <= rr <= 1/2 )` vs null `1/6` (stockfeel variant); `P( rr > 1 )` (full retracement or more); `P( rr < 1/3 )`; histogram deciles; a majority test `share_band` vs `0.5` (descriptive) |
| Mechanical caveat (must be printed) | With pct 10% swings a secondary leg is at least 10% of price, so `rr >= 0.10 / amplitude of the preceding leg`. Small preceding legs force high `rr`. The sweep over `secondary_pct` is therefore mandatory and the range is reported. |
| Decision | section 1.4 with null 1/3. `data-confirmed` requires `p_holm < 0.05` for `share_band > 1/3` plus sub-sample consistency; `data-refuted` requires the Bonferroni bound of `share_band` to lie below `1/3`. |

### R5  Secondary duration (`rule_key: secondary_duration`)

| Field | Specification |
|---|---|
| Claim (literature-disputed) | Secondary reactions last about three weeks to three months (Rhea); variant: at least 8 trading days (Schannep). |
| Event | Same event set as R4 (confirmed counter-trend secondary swings). `d_cal = S_k.duration_days` (calendar days, contract field); `d_bar = S_k.idx - S_{k-1}.idx` (trading bars). |
| Primary metric | `share_rhea = P( 21 <= d_cal <= 90 )` (`swings.secondary_min_days` / `secondary_max_days`) |
| Null | `H0: share_rhea = 0.5`; predicted direction `> 0.5` ("typically" read as a majority) |
| Test | exact binomial one-sided; Wilson CI |
| Also reported | `share_schannep = P( d_bar >= 8 )` (`schannep_min_days`), median and interquartile range of `d_cal`, `P( d_cal > 90 )`, `P( d_cal < 21 )` |
| Decision | section 1.4 with null 0.5. The rule is descriptive and keeps `literature-disputed` whatever the data label. It can still be `data-refuted`: if the Bonferroni upper bound of `share_rhea` is below `0.5` (fewer than half of secondaries fall in the Rhea window with the CI excluding one half) and both sub-samples are below `0.5`. |

### R6  Line breakout (`rule_key: line_breakout`)

| Field | Specification |
|---|---|
| Claim | A breakout from a Dow "line" (narrow sideways band in both averages) predicts continuation in the breakout direction, more reliably when both averages break the same way. |
| Event | `LineRange` from `detect_lines(close_DJI, close_DJT, band_pct=0.05, min_days=14)` with `breakout != "none"`. **Confirmed-both**: `confirmed_both == True`; event bar `c` = the later of the two breakout bars (knowable then). **Single**: `confirmed_both == False` at bar `c + h` (the other average has not broken the same way within the horizon); event bar = the first breakout bar. Direction `sgn = +1` for `up`, `-1` for `down`. Forward returns measured on `^DJI`. |
| Primary metric | `agree_h = P( sgn * F_h(c) > 0 )` for confirmed-both breakouts, **primary `h = 20`**; `h = 60` secondary |
| Null | `H0: agree_20 = 0.5`; predicted direction `> 0.5` |
| Test | exact binomial one-sided; Wilson CI |
| Also reported | `agree_h` for single breakouts and the difference confirmed minus single (permutation test, two-sample minimum n per 1.3); `excess_h = mean( sgn * F_h(c) ) - mean_t F_h(t)` with random-placement `p` (drift-aware robustness, because a 0.5 sign null ignores index drift and upward breakouts inherit positive drift); number of lines, number of breakouts, mean line length |
| Sweep | `band_pct {0.03, 0.05, 0.07}` x `min_days {14, 28}`; ranges only |
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
| Position rule (primary, long/cash) | at the close of bar `t`: `pos_t = 1` if `state_DJI(t).state == BULL_PRIMARY` and `pair_confirm(state_DJI(t), state_DJT(t)).status == "confirmed"`; else `pos_t = 0`. **Variant (long/short)**: `pos_t = -1` if `state_DJI(t).state == BEAR_PRIMARY` and pair-confirmed. |
| Execution | daily rebalancing at the next open, proxied by the next close: the position decided at close `t` is held from close `t+1`, so the strategy's return on bar `t` is `r_s(t) = pos_{t-2} * r(t)` with `r(t) = ln(P_t / P_{t-1})` on `^DJI`. Cash earns 0 (stated assumption; conservative for the strategy). |
| Costs | `cost_t = kappa * abs(pos_{t-2} - pos_{t-3})` deducted from `r_s(t)` on the trade bar, `kappa in {0, 0.0010}` (0 and 10 bps per side). **Primary: 10 bps.** |
| Benchmark | buy-and-hold `^DJI` price index, same bars. Both legs exclude dividends; because the strategy is in cash part of the time, a price-index comparison **favours the strategy** (caveat printed). |
| Primary metric | `delta_sharpe = Sharpe(r_s, 10 bps) - Sharpe(r_bh)`, Sharpe = `mean / std * sqrt(252)` of daily log returns, risk-free 0 |
| Null | `H0: delta_sharpe = 0`; predicted direction `> 0` |
| Test | stationary block bootstrap (block 20, 2000, joint indices) on the aligned `(r_s, r_bh)` series; one-sided `p = (1 + #{delta* <= 0}) / 2001`; percentile 95% CI |
| Also reported | annualised return and volatility of both legs, maximum drawdown, time in market, number of trades, cumulative log-return difference with bootstrap CI, the long/short variant, cost 0, `SP_IYT`; sub-samples 1992-2009 / 2010-2026 |
| Right/wrong calls (descriptive, BGK analogue) | a **call** occurs at bar `c` when the pair-confirmed state first becomes `BULL_PRIMARY` (bull call) or `BEAR_PRIMARY` (bear call). A call is **right** if `ln(P_{c'+1} / P_{c+1})` has the called sign, where `c'` is the bar of the next call (or `period_end`). Report `right / wrong`, the share with Wilson CI and a two-sided binomial p vs 0.5. |
| Explicit caveat (must be printed verbatim) | "The 1992-2026 DJI/DJT sample cannot replicate Brown, Goetzmann and Kumar's 1902-1929 reconstruction of Hamilton's 255 editorials (110 right, 74 wrong, 71 neutral). Our calls are produced by a mechanical state machine, not by Hamilton's judgement, on a different century of data. Any comparison with 110/74 is descriptive and carries no label." |
| Minimum n | the primary metric is series-level; the `n >= 30` rule applies to the number of **position changes** (trades). Fewer than 30 trades gives `insufficient-evidence`. |
| Decision | section 1.4 with null 0 on `delta_sharpe` (10 bps, long/cash, `DJ`) |

### Summary of label-driving rows

| Rule | Event count `n` | Primary metric | Null | Direction | Test | Horizon |
|---|---|---|---|---|---|---|
| R1 | counter-trend secondary swings in `*_PRIMARY` | `p_extend` | 0.5 | > | binomial | swing |
| R2 | `REVERSAL_*` on `^DJI` | `excess_60` | 0 | > | random placement | 60 |
| R3 | confirmed vs single reversals | `diff_60` | 0 | > | permutation | 60 |
| R4 | counter-trend secondary swings | `share_band` | 1/3 | > | binomial | n/a |
| R5 | counter-trend secondary swings | `share_rhea` | 0.5 | > | binomial | n/a |
| R6 | confirmed-both line breakouts | `agree_20` | 0.5 | > | binomial | 20 |
| R7 | with/counter leg pairs, 2000+ | `p_vol` | 0.5 | > | binomial | n/a |
| R8 | trades (for n), series for metric | `delta_sharpe` (10 bps) | 0 | > | block bootstrap | series |

---

## 3. Label algorithm

```python
ALPHA = 0.05
FAMILY = ["R1", "R2", "R3", "R4", "R5", "R6", "R7", "R8"]
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
    """side = 'predicted' or 'wrong'. None when not assessable (a sub-sample has n < MIN_N_GROUP)."""
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

def decide_label(rule: str, result, p_holm: dict[str, float], canonical_rules) -> dict:
    """result: the DJ / pct0.03-0.10 / primary row of `rule`, with fields
       n, n_total, n_group_a, n_group_b, two_sample, estimate, null_value,
       p_raw (one-sided, predicted direction), bound_bonf (one-sided (1-ALPHA/8)
       confidence bound of the effect in the predicted direction), sub_A, sub_B."""
    lit = canonical_rules.get(RULE_KEY[rule], {}).get("literature_label", "unresolved")

    if not n_ok(result):
        return {"label": "insufficient-evidence", "literature_label": lit, "reason": "n below minimum"}

    if p_holm[rule] < ALPHA and sign_consistent(result, "predicted") is True:
        return {"label": "data-confirmed", "literature_label": lit, "reason": "p_holm<alpha, sub-samples agree"}

    wrong_side = (result.bound_bonf - result.null_value) < 0   # effect bound on the wrong side of the null
    if wrong_side and sign_consistent(result, "wrong") is True:
        return {"label": "data-refuted", "literature_label": lit, "reason": "Bonferroni bound excludes null, sub-samples agree"}

    reason = ("sub-sample consistency not assessable" if sign_consistent(result, "predicted") is None
              else "not significant after Holm, or sub-samples disagree")
    return {"label": "insufficient-evidence", "literature_label": lit, "reason": reason}

def label_all(primary_results: dict[str, object], canonical_rules) -> dict[str, dict]:
    p_raw = {r: (primary_results[r].p_raw if r in primary_results and n_ok(primary_results[r]) else 1.0)
             for r in FAMILY}
    p_holm = holm_adjust(p_raw)
    return {r: decide_label(r, primary_results[r], p_holm, canonical_rules) for r in FAMILY}
```

Rules for the two label fields:

- `label` (data layer) is produced **only** by `decide_label` on the `DJ` primary row. Humans do not override it. R12 writes the result into `analysis/rule_status_table.md` together with the effect size, CI, `n`, number of clusters, both sub-sample estimates, the `SP_IYT` estimate and every note flag.
- `literature_label` is carried from `research/canonical_rules.md` by `rule_key` and is **independent** of the data label. A rule may be `literature-disputed` and `data-confirmed`, or `literature-consensus` and `data-refuted`; both fields are shown side by side. If the canonical file is not yet available or the key is absent, the row is logged with `literature_label = unresolved` and must be resolved before any skill (P5) cites the row.
- The Dow defense line is `agent-defined` and is **not** in the family; `DEFENSE_BREAK` events may be reported descriptively (rule_id `R2x`, label `n/a`) but never receive a data label.

---

## 4. Multiple-testing and sweep policy

1. One Holm family of 8 tests, fixed above. Adding a rule, a horizon or a variant to the family after the
   first run is a protocol deviation (section 6).
2. Primary horizon, primary variant, primary null and direction are fixed per rule in section 2. They
   may not be changed after inspection of results.
3. Sweeps (1.6) are reported as ranges and tables. The text accompanying a sweep must not single out the
   best parameter. If a rule is `insufficient-evidence` at the primary specification but significant at
   another grid point, the label stays `insufficient-evidence` and the grid point is reported as
   `exploratory`.
4. Robustness methods (ATR, pivot), robustness pair (`SP_IYT`), confirmation-window variant, cost variants,
   long/short variant, pooled `^DJI`+`^DJT` rows and the drift-matched simulated null carry raw p-values
   only and never enter the family.
5. Sub-sample results are reported but never tested for significance on their own; they serve only the
   sign-consistency check.
6. Any statistic not listed in section 2 that engineers find useful is logged with `variant = exploratory`
   and `label = n/a` and may not be cited in skills or the agent as evidence for a label.

---

## 5. Data-coverage caveats (to be printed with every report)

- `^DJT` history in `dow.mkt_klines` begins **1992-01-02**. Nothing in this protocol tests Dow Theory on
  1897-1991 data; claims about that period default to `insufficient-evidence` per `docs/team_design.md`
  section 5 unless a long-history source is loaded under a new, hashed protocol.
- `^DJI` 1992-01-02 to 2026-11-06 = 8,775 bars. Primary reversals at a 10% secondary threshold are rare;
  R2 and R3 are expected to have small `n`, and `insufficient-evidence` is then the correct label, not a
  failure.
- Index volume is sparse or zero before 2000 and is a vendor-constructed aggregate afterward; R7 therefore
  starts 2000-01-03 and its `SP_IYT` robustness uses ETF volume (2004+).
- `^GSPC` and `^IXIC` have `analysis_start` clipping (first real OHLC 1962-07-02 and 1984-10-11); they are
  not used in any label-driving row. `IYT` begins 2004, so the `SP_IYT` pair covers 2004-2026 only.
- Price indices exclude dividends (R8 caveat). The `^DJI` series is yfinance-sourced; vendor revisions after
  2026-11-06 do not change the frozen `period_end` of label-driving runs.
- Forward windows overlap at `h = 60` and `h = 120`; effective sample sizes are smaller than `n`; the
  number of event clusters is reported next to `n` for every return-based row.

---

## 6. Protocol deviations

A **deviation** is any change, after the first label-driving run, to: an event definition, a null value, a
predicted direction, a primary horizon or variant, a test or bootstrap scheme, `alpha`, `MIN_N`, the
sub-sample split rule, the Holm family, the swing specification used for labels, the sample period, or
the `decide_label` algorithm. Fixing an implementation bug that makes the code match this document is
**not** a deviation but must be recorded in the run notes with the rows it invalidated.

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
`analysis/decision_table.sha256` that was current at the row's `inserted_at`.

PROTOCOL-HASH-SCOPE: everything above this line
