# P4 backtest methodology audit (R11)

Auditor: R11 (methodology auditor, Model QA). Date: 2026-11-08. Scope: the label-driving run
`a6d2d48e46014e7da3cc7c6be7ce8a02` (pair `DJ`, spec `pct0.03/0.08f15`, 1992-01-02 to
2026-11-06) and the robustness pair `SP_IYT`, as recorded in `reports/backtest_run_20261108_063248.json`,
`reports/rule_R1.md` .. `rule_R8.md` (+ `_SP_IYT`), `analysis/rule_status_table.md`, the ledger
`dow.str_rule_backtest_log`, and the code under `src/dowtheory/backtest/` plus
`src/dowtheory/{swings,trend,line,confirmation}.py`. Nothing under `src/`, `analysis/` or
`reports/rule_*.md` was modified. Replay script: `reports/backtest_audit_replay.py` (read-only).

Evidence runs (all reproducible):

- `uv run --python .venv/bin/python pytest -q`: 290 passed.
- `shasum -a 256 analysis/decision_table.md` = `c8675eff...9836` = line 1 of `decision_table.sha256`.
- `reports/backtest_audit_replay.py`: 8 cut dates, 16 event sets per cut, 1 non-issue diff (see 2).
- Independent statistics check (scipy 1.x in an ephemeral `uv run --with scipy` overlay) and an
  independent 3 x 2000-path random-walk simulation of the R1 null (scripts kept in the session
  scratchpad; numbers reproduced below).

Overall opinion: **Sound with findings.** All eight data labels follow the pre-registered algorithm
and the arithmetic is correct. Two findings are governance/tooling (ledger history, scoped hash),
one is interpretive and must accompany every citation of R1 (the 0.5 null is not what a random
walk produces), and two are protocol-design flaws that only touch descriptive rows now but must be
fixed before a v3 table.

---

## 1. Protocol adherence: PASS (with CONCERN on verifiability)

| Check | Result | Evidence |
|---|---|---|
| Event definitions R1-R8 implemented as written | PASS | `events.py`: R1 `r1_events` (counter-trend secondary in `*_PRIMARY`, outcome = machine's own `_label` vs `state(c).last_H/last_L`, EQUAL = not extended, right-censored excluded and counted); R2 `reversal_events` (`REVERSAL_*` at `Signal.idx`, `DEFENSE_BREAK`/`TREND_ESTABLISHED` excluded); R3 `pair_reversal_groups` (A7 cycle-aware, event bar `confirmed_ts`); R4/R5 `leg_events` (counter-trend, SUSPECT allowed, UNDEFINED excluded, flags A5); R6 `breakout_groups` (confirmed-both at `confirmed_ts`); R7 `leg_pair_events` (with/counter pair, state at later swing, positive volume); R8 `pair_states` + `position_series` + `strategy_series`. |
| Metrics, nulls, directions, horizons | PASS | `rules.py`: R1 `p_extend` vs 0.5 >; R2 `excess_60` vs 0 >; R3 `diff_60` vs 0 >; R4 `share_band` vs 1/3 >; R5 `share_rhea` vs 0.5 >; R6 `agree_20` vs 0.5 >; R7 `p_vol` vs 0.5 >; R8 `delta_sharpe` (10 bps) vs 0 >. `PRIMARY_HORIZON = {R2: 60, R3: 60, R6: 20}`, `COST_PRIMARY = 0.0010`. |
| Tests | PASS | binomial exact (rational arithmetic), Wilson, random placement (R2), permutation (R3), block bootstrap joint indices (R8); all one-sided in the predicted direction (`direction="greater"`; R8 counts `delta* <= 0`). |
| `min_n = 30`, two-sample floor 30/10, sub-sample floor 10 | PASS | `labels.py: n_ok`, `sign_consistent`; R2 (12), R3 (15, groups 12/3), R8 (28 trades) correctly fall to `n below minimum`. |
| Sub-sample rule | PASS with DEV-01 | split 2009-12-31 as the table states; the table's wording ("preceding 31 December") would give 2008-12-31. R1 signs unchanged under either split (A 16/17, B 13/16 vs A 15/16, B 14/17). |
| Holm family of exactly 8 | PASS | `label_all` iterates `FAMILY` (8), missing p -> 1.0. Hand/statsmodels Holm reproduces p_holm R1 0.000044, R5 0.310191, rest 1.0. |
| Worst-grid-point rule R4/R5 | PASS | `label_inputs` takes `max(p_raw)` and `max(bound_bonf)` over the five f15 grid points with `n >= 30`; R4 p_label 0.5105 (at 0.06), R5 p_label 0.0443 (at 0.05); sub-sample consistency evaluated at the primary point. |
| R8 floor and random-spell null | PASS | n = 28 position changes < 30 -> insufficient; `p_spell = 0.0245` (< 0.05, no flag); independent re-implementation gives 0.0305 (different seed, 29 spells). |
| `config_hash` on label rows | PASS | all 8 label rows carry `e6f5b9cd...ae24e`; recomputed from `configs/dow.yaml` at HEAD and at the pinned commit `5a3b907`: identical. |
| `decision_table_hash` on label rows | PASS | all 410 ledger rows (both runs) carry `c8675eff...9836`, equal to the file on disk and to `decision_table.sha256` line 1. |
| No post-run protocol edit | CONCERN | `git log` shows `analysis/decision_table.md`, `decision_table.sha256`, the harness, both run JSONs and the reports all entered the repository in **one commit** (`3770aa1`, 2026-11-08 06:33:34 UTC), one minute after the second run finished. There is therefore no commit timestamp proving the table predates the runs; the evidence is internal only (both run JSONs record the same whole-file hash at 06:26:55 and 06:32:48 UTC, and the file's history block records the superseded v1 hash `d94a32e1...`). The content is consistent with pre-registration, but it is not independently verifiable. |

## 2. Look-ahead: PASS

- Forward returns: `forward_returns` gives `F_h(t) = ln(P[t+1+h]/P[t+1])`, NaN when `t+1+h > last`;
  censored counts reported (R1 1, R6 1). Benchmark = mean over all bars with `F_h` defined.
- Event bars: swings at `confirmed_idx`, signals at `Signal.idx` (stamped at the confirmation bar by
  `run_trend`), lines at `confirmed_ts`/`breakout_ts`, pair reversals at `confirmed_ts` (later date).
- R8 lag: `strategy_series` uses `e = pos[1:-2]` against `r = diff(log close)[2:]`, i.e.
  `r_s(t) = pos[t-2] * r(t) - kappa * |pos[t-2] - pos[t-3]|`; an independent index construction
  reproduces the series exactly (`allclose` True, 28 trades).
- Truncation replay (`reports/backtest_audit_replay.py`, cuts 1996-06-28, 2001-09-28, 2008-10-31,
  2012-12-31, 2016-03-31, 2020-03-23, 2023-06-30, 2025-12-31): secondary swings, per-bar states,
  signals on both averages, R1 event bars and outcomes (where `S_{k+1}` was confirmed before the cut),
  R2 events, R3 confirmed and single groups (single only where `c+60 <= cut`), R4/R5 legs and flags,
  R6 confirmed and single breakouts, R7 leg pairs, R8 positions and pair states are **identical**
  between the truncated and the full sample at every cut (127 of 128 comparisons PASS). The single
  diff is a `LineRange` whose window was still open at the 2025-12-31 cut (its `end` differs by
  construction); no breakout event is affected.

## 3. Statistics: PASS

| Rule | Harness | Independent check |
|---|---|---|
| R1 29/33 | p 5.464e-06, Wilson [0.7267, 0.9518], upper bound (0.99375) 0.9620 | scipy `binomtest` 5.464e-06; Wilson identical to 1e-12; one-sided 0.99375 bound identical |
| R5 32/44 | p 0.001829, CI [0.5815, 0.8365] | scipy identical; flags `rhea_window` re-derived from `duration_days` with 0 mismatches |
| R4 18/44 | p 0.181585 vs 1/3 | scipy identical; `retrace_in_third_two_thirds` re-derived with 0 mismatches |
| R7 20/57 | p 0.991826, CI [0.2400, 0.4806] | scipy identical; first leg-pair mean volumes recomputed from raw volume: identical |
| R8 | delta_sharpe 0.1099, p 0.2464, CI [-0.1827, 0.4336], p_spell 0.0245 | independent Politis-Romano bootstrap (p = 1/20, joint indices, seed 1): p 0.2375, CI [-0.1966, 0.4316]; independent spell shuffle p 0.0305; harness functions re-run with the protocol seed reproduce 0.246377 exactly |
| R2 | p 0.7736 (random placement, spacing 43, pool [671, 8713]) | rejection-sampling placement with sign re-assignment: p 0.7701 |
| R3 | p 0.7901 (permutation) | independent permutation: p 0.8021 |
| Holm | R1 0.000044, R5 0.310191, others 1.0 | hand step-down and statsmodels `holm`: identical |

Implementation notes verified: `cluster_ids` single-linkage on `|c_i - c_j| <= h` (overlapping windows
share a cluster, same bar always); `cluster_bootstrap_mean` resamples clusters and divides summed
values by summed counts; `stationary_indices` restarts with probability `1/block_len` and continues
circularly; `random_placement_null` uses an exact stars-and-bars shift for the spacing constraint and
re-permutes the observed signs; `one_sided_p` is `(1 + hits)/(B + 1)`.

## 4. Deviations log: PASS for data labels, CONCERN for completeness

| id | Assessment | Label impact |
|---|---|---|
| DEV-01 split date | genuine clarification; table text and example disagree, the example was followed | none (R1 signs robust to both splits; other rules not label-affected) |
| DEV-02 literature mapping | clarification; affects `literature_label` only, by design independent of the data label. **Applied between the two full runs**, i.e. after data results had been seen; this is acceptable only because the field is independent of `decide_label` | none |
| DEV-03 two-sample sub-sample n | reasonable clarification | none (R3 insufficient) |
| DEV-04 placement details | faithful to 1.2; contiguous pool equals "all non-UNDEFINED bars" because the state never returns to UNDEFINED | none |
| DEV-05 R7 start | correct reading (full-history states, legs from 2000-01-03) | none |
| DEV-06 bound for non-proportions | reasonable; bootstrap 0.99375 quantile | none (refutation never triggered) |
| DEV-07 which hash | see finding F3: the scoped hash the harness computes is wrong, so only the whole-file hash protects the run | none |
| DEV-08 R8 details | reasonable; call definition re-triggers after non-confirmation gaps (24 calls) | none |
| DEV-09 R3 double counting | **material**, see F4: all 3 "single" events are reversals confirmed later than 60 bars, so the single group contains no unconfirmed reversal and `n_total` double counts 3 of 12 reversals | none now (insufficient-evidence either way) |

Cap check (section 6 "post-hoc-modified"): none of DEV-01..09 changes an event definition, null,
direction, horizon, test, alpha, MIN_N, split rule, family, configuration or `decide_label` after
results were seen for that rule; they are readings of silent or contradictory text. No label is
capped. The log's account of what was run before the persisted run is incomplete, however:

- It records a "development smoke run (300 bootstrap draws, no persist)". The ledger and the
  repository additionally contain a **full label-driving run** `b94022285206435e83b1c068eb123dc9`
  (06:26:55 UTC, 2000 iterations, both pairs, sweeps on, `reports/backtest_run_20261108_062655.json`)
  that **was persisted**. Its data labels and every primary statistic are identical to the final run
  (R1 0.8788, p_holm 0.000044; others insufficient). Only 16 of its ~394 rows survive in the ledger
  because the table's sorting key `(rule_id, pair, run_id)` made `ReplacingMergeTree` collapse all
  metrics of a rule/pair/run into one row; the key was then changed (`scripts/migrate_rule_log_v2.py`,
  `db/init/01_schema.sql`) and the run repeated. Protocol 6 requires a bug fix that invalidates rows to be
  recorded in the run notes with the rows it invalidated, and run `a6d2...` carries `deviations=[]`
  and no reference to `b940...`. Governance gap, not a label issue.

## 5. Multiple testing and selection: PASS with CONCERN

- The 8% + 15-session choice was made in `reports/spec_review_p3.md` 3b on the same sample after
  seeing swing counts, the Rhea duration share (67-73%), the retracement band share, reversal counts
  and lag statistics. The table discloses this (1.8) and applies the worst-grid-point rule to R4 and
  R5, whose primary metrics were literally the selection criteria. Adequate for R4/R5: the rule can
  only lower evidence, and it did (R5 primary p 0.0018 -> family p 0.0443 -> p_holm 0.31).
- R1 is **not** protected by the rule and is affected indirectly: `p_extend` was not inspected in the
  spec review, but its event count and the swing geometry depend on `secondary_pct`, and the sweep
  shows `p_extend` is highest at exactly the chosen point (0.8788 at 0.08 f15; 0.73-0.79 at 0.05/0.06;
  0.73 at 0.10; 0.62 at 0.12; ATR 0.77; pivot 0.59). Raw binomial p vs 0.5 is < 0.05 at every pct
  grid point with n >= 30 and for ATR, so the direction of the finding is robust, but the headline
  size is at the most favourable grid point. The worst-grid-point raw p over the f15 grid with
  n >= 30 is 0.0000 (0.05, 0.06, 0.08), so R1 would still pass Holm under a worst-grid rule against
  the 0.5 null; it would **not** necessarily pass against the mechanical null of section 7.
- No horizon, variant, null or direction was changed after the run (table hash unchanged in both run
  JSONs). Sweeps are reported as ranges without naming an optimum. The "exploratory" tag is unused;
  nothing beyond section 2 was logged.
- Descriptive two-group differences in R3 and R6 (confirmed minus single) have a design flaw: the
  "single" classification uses information up to `c + h`, the same window as the outcome `F_h(c)`,
  so group membership is partly a function of the outcome (R6 single breakouts agree 1/15 because a
  breakout the other average never follows is one that reversed). These rows must not be cited as
  evidence of the confirmation principle (they are descriptive and carry no label today).

## 6. Data coverage: PASS (one caveat text is inaccurate)

- `^DJT` and `^DJI` in `dow.mkt_klines FINAL`: 1992-01-02 to 2026-11-06, 8,775 bars each; the
  run's inner join has 8,775 bars. `period_end` fixed at 2026-11-06 (`protocol.PERIOD_END`).
- `^GSPC`/`^IXIC` `analysis_start` clipping is not used by any label row (DJ only); `load_klines`
  clips by default. `SP_IYT`: SPY from 1993, IYT from 2004-01-02 -> pair 2004-2026, 5,749 bars.
- Integrity: `reports/integrity_20261108_142118.txt`, STATUS PASS, errors 0, run 06:21:18 UTC on the
  run date; path written in every ledger row.
- Dividends: prices are unadjusted (`yahoo_fetcher.py`, `auto_adjust=False`), so the R8 caveat is
  correct; it is printed in every report (section 5 bullet) and in the R8 strategy table, including
  `rule_R8_SP_IYT.md`.
- Volume: the table says `^DJI` volume is "sparse or zero before 2000". In the database every `^DJI`
  bar since 1992 has positive volume; what exists is a level break (annual mean 21-99 million shares
  1992-1999 vs 205 million in 2000, and another break in 2016/2017: 117 vs 311 million). The 2000
  start is pre-registered and stays; the stated reason should be corrected to "vendor-constructed
  aggregate with level breaks" in v3. The 2016/2017 break lies inside R7's sample; only the normalised
  variant (trailing-250 median) partly handles it. Low.
- `pair-inconsistent` notes present for R2, R4, R6 in the status table; the caveat block is printed
  verbatim in all 16 reports.

## 7. Interpretation of R1: CONCERN (label algorithm satisfied, null mis-specified)

The event is a counter-trend secondary swing confirmed while the primary state is still
`*_PRIMARY`. In a bull that means: price fell from the last high to a low, did **not** close below the
defence line (the prior reaction low, otherwise the state would be SUSPECT and the event excluded),
and then rallied at least 8% over at least 15 sessions before the low was confirmed. Success means
the rally continues past the old high before any 8% setback. Conditioning on an 8% rally without a
defence break is conditioning on being already most of the way back to the old high, so a random walk
is far more likely than 50% to print a higher high. The pre-registered null 0.5 is therefore not the
"no information" baseline; the protocol anticipated this and made the drift-matched simulated null
mandatory robustness, and the harness reports `p_sim = 0.0055` (null mean 0.6906).

Independent simulation (2000 paths each, 8,775 bars, identical `detect_multiscale` + `run_trend` +
`r1_events`, different seeds):

| Null | mean `p_extend` | 5% / 50% / 95% | P(`p_extend` >= 0.8788) | mean n |
|---|---|---|---|---|
| iid Gaussian, drift 0.080/yr, sd 0.1735/yr (matched) | 0.654 | 0.528 / 0.657 / 0.771 | 0.0005 | 38 |
| iid Gaussian, zero drift, matched sd | 0.633 | 0.514 / 0.634 / 0.744 | 0.0005 | 38 |
| stationary block bootstrap of actual returns (harness null) | 0.695 | 0.560 / 0.692 / 0.826 | 0.0085 | 30 |

Conclusions:

- A random walk **does not** produce `p_extend` of 0.88: even the fattest null (block bootstrap,
  which keeps volatility clustering) puts 0.88 above its 95th percentile, and the harness value
  `p_sim = 0.0055` is reproduced (0.0085 here; the gap is Monte-Carlo and seed noise at B = 2000).
- About 0.13-0.19 of the 0.38 excess over 0.5 is mechanical (zig-zag plus state-machine
  conditioning); drift adds only ~0.02; volatility clustering adds ~0.04 more. The genuine signal is
  the remaining ~0.18-0.22 above the 0.65-0.69 baseline, with n = 33.
- Against the correct baseline the raw evidence is p about 0.005-0.009, not 5e-06. Had this p entered
  the Holm family as the smallest of eight, p_holm would be about 0.04-0.07: borderline rather than
  overwhelming. The label `data-confirmed` is produced by the algorithm as pre-registered and I do not
  override it, but every citation must carry the mechanical baseline and `p_sim`.
- The spec review shows the pct zig-zag at 8% mostly returns primary legs, not reactions; "trend
  persistence of secondary swings" here is closer to "after an 8% rally off an un-broken reaction
  low, the index usually makes a new high within the same primary cycle". That is still a Dow-Theory
  statement (primary trends persist), but weaker than the headline reads.

## 8. Verdict

| Rule | Data label | Endorse? | Grounds |
|---|---|---|---|
| R1 trend_persistence | data-confirmed | **Yes, with mandatory caveat** | algorithm correctly applied; direction robust across the grid and under a drift-matched/zero-drift/block null (p_sim 0.005-0.009); but the 0.5 null overstates the strength, so citations must state the mechanical baseline (~0.65-0.69) and p_sim, and must not quote p_holm 4.4e-05 alone |
| R2 primary_reversal_signal | insufficient-evidence | Yes | n = 12 < 30; point estimate negative; pair-inconsistent |
| R3 two_average_confirmation | insufficient-evidence | Yes | groups 12/3 below floor; single group is ill-defined (F4) |
| R4 secondary_retracement | insufficient-evidence | Yes | worst-grid p 0.51; share 0.34-0.41 across grid, barely above the 1/3 uniform null; mechanical caveat printed |
| R5 secondary_duration | insufficient-evidence | Yes | worst-grid p 0.044 -> p_holm 0.31; lower Rhea bound partly enforced by the 15-session filter (f0 variant 0.47-0.67) |
| R6 line_breakout | insufficient-evidence | Yes | agree_20 0.41 < 0.5 (n 87, both sub-samples below); refutation bound 0.547 does not exclude 0.5 |
| R7 volume_confirmation | insufficient-evidence | Yes | p_vol 0.35 (n 57), both sub-samples below 0.5; refutation bound 0.516 does not exclude 0.5 (close) |
| R8 hamilton_timing | insufficient-evidence | Yes | 28 trades < 30; delta_sharpe 0.11 with CI spanning 0; cumulative log-return difference -1.10; p_spell 0.02-0.03 |

### Blocking (required before P5 cites any row)

- **F1 (High, interpretation).** Every citation of R1 `data-confirmed` must state: the 0.5 null is
  not a random-walk baseline; a drift-matched random walk gives `p_extend` about 0.65-0.69 through
  the same machinery; the random-walk p is 0.0055 (harness) / 0.0085 (audit), uncorrected; n = 33.
  Add the sentence to `analysis/rule_status_table.md` notes for R1 and to the skill boundary ledger.
  For v3: pre-register the simulated null (or the gambler's-ruin analytic baseline) as the label null
  for R1.
- **F2 (Medium, governance).** Record run `b94022285206435e83b1c068eb123dc9` in
  `analysis/protocol_deviations.md` (first full label-driving run, persisted, rows collapsed by the
  old sorting key, data labels identical; surviving record `reports/backtest_run_20261108_062655.json`),
  and state that the sorting-key fix is the bug fix of protocol 6 with the invalidated rows. The
  statement "applied before the persisted run" under DEV-02 must be corrected to "between the two
  persisted runs".
- **F3 (Medium, tooling).** `protocol.scoped_sha256` finds the first occurrence of
  `PROTOCOL-HASH-SCOPE`, which is the prose mention on line 5, so it hashes only the first four lines
  (`3f6d676b...`). The stored scoped hash `35de767a...` is the correct hash of everything above the
  marker line (byte 40,540). Fix the search to a line-anchored marker, re-run the test, and note that
  `table_scoped=3f6d676bcd4c` in existing ledger notes is not a protocol hash. Protection of this run
  rested on the whole-file hash alone, which did match.
- **F4 (Medium, protocol design, v3).** R3 "single" and R6 "single" classify on information up to
  `c + h`, the outcome window itself; and the R3 wording puts late-confirmed reversals in both groups
  (3 of 3 single events are later-confirmed). Redefine single as "not confirmed by `period_end`" (or
  by a window ending before `c + 1`) and drop double counting before any confirmed-vs-single row is
  cited. No label changes today.

### Recommendations (non-blocking)

- Commit the decision table and its hash **before** the first run in future phases; the current
  pre-registration is internally consistent but has no external timestamp (one commit, `3770aa1`).
- DEV-01: adopt the proposed text ("31 December of the year containing the median date") in v3.
- Correct the section-5 volume caveat (level breaks, not sparse/zero) and mention the 2016/2017 break.
- `BacktestRun.started` is set after the run completes (it is the end time); rename or move.
- R7 `volume_confirms` rows are dated at the last bar (sub-sample columns meaningless; descriptive).
- R6 pct-grid sweep rows are identical by construction (lines do not depend on swings); harmless.
- Consider reporting R1 by side with the mechanical baseline per side (bull 18/21, bear 11/12).
- R7's refutation bound (0.516 vs 0.5) and R6's (0.547) are close to a `data-refuted` outcome; a
  longer sample or the `SP_IYT` pooling (never label-driving) will not change that under this table,
  but a v3 may want a pooled-pair family.

---

Files produced by this audit: `reports/backtest_audit.md` (this file),
`reports/backtest_audit_replay.py` (truncation replay, read-only, exit code 1 on any event diff).
