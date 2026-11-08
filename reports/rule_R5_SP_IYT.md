# R5 Secondary duration (`rule_key: secondary_duration`)

Pair `SP_IYT` (SPY, IYT), 2004-01-02 to 2026-11-06, 5749 bars. Specification `pct0.03/0.08f15`. Run `a6d2d48e46014e7da3cc7c6be7ce8a02`.
Config hash `e6f5b9cd228e458809a42aa2a5c5e2811175de3d74fafca1a3496c6ac68ae24e`. Decision table sha256 `c8675eff2b281ac6f4fa8ed790063ecaf1e063d78f20fa9569ded1988be39836`. Bootstrap iterations 2000, seed 20261108.

## Event definition

Same events as R4. Metric: share lasting 21 to 90 calendar days, null 0.5. Exact binomial, Wilson CI; the label uses the worst point of the `secondary_pct` grid.

## Result

| field | value |
|---|---|
| events n | 29 |
| clusters | n/a |
| right-censored | 0 |
| metric | share_rhea na |
| estimate | 0.5862 |
| 95% CI | [0.4074, 0.7449] |
| null value | 0.5000 |
| p raw (one-sided, predicted direction) | 0.229129 |
| p used in the Holm family | n/a |
| p Holm (family of 8) | n/a |
| Bonferroni one-sided upper bound (level 0.99375) | 0.7787 |
| sub-sample split | 2015-12-31 (A up to and including, B after) |
| sub-sample A | 0.5625 (n = 16) |
| sub-sample B | 0.6154 (n = 13) |
| sub-sample signs vs null | A+ B+ |

## Label

- No label: `SP_IYT` is a robustness pair (labels come from `DJ` only).

## Descriptive and robustness rows

| spec | variant | metric | horizon | n | value | CI low | CI high | p raw | notes |
|---|---|---|---|---|---|---|---|---|---|
| pct0.03/0.08f15 | schannep | share_schannep | na | 29 | 0.9655 | 0.8282 | 0.9939 | 0.0000 |  |
| pct0.03/0.08f15 | gt_max | share_gt_max_days | na | 29 | 0.2414 | 0.1222 | 0.4211 | 0.0000 |  |
| pct0.03/0.08f15 | lt_min | share_lt_min_days | na | 29 | 0.1724 | 0.0760 | 0.3455 | 0.0000 |  |
| pct0.03/0.08f15 | median_d_cal | median_days | na | 29 | 48.0000 | 22.0000 | 88.0000 | n/a | ci columns hold the inter-quartile range |
| pct0.03/0.08f15 | sub_A | share_rhea | na | 16 | 0.5625 | n/a | n/a | n/a | sub-sample split 2015-12-31 |
| pct0.03/0.08f15 | sub_B | share_rhea | na | 13 | 0.6154 | n/a | n/a | n/a | sub-sample split 2015-12-31 |

## Specification sweep (descriptive)

Range of the primary metric over 15 grid points (not a selected optimum): min 0.3517, median 0.5294, max 0.7037.

| spec | variant | metric | horizon | n | value | CI low | CI high | p raw | notes |
|---|---|---|---|---|---|---|---|---|---|
| pct0.03/0.05f0 | primary | share_rhea | na | 80 | 0.4125 | 0.3111 | 0.5220 | 0.9535 | sweep |
| pct0.03/0.05f15 | primary | share_rhea | na | 67 | 0.5672 | 0.4481 | 0.6790 | 0.1642 | sweep |
| pct0.03/0.06f0 | primary | share_rhea | na | 62 | 0.4839 | 0.3641 | 0.6055 | 0.6482 | sweep |
| pct0.03/0.06f15 | primary | share_rhea | na | 56 | 0.5714 | 0.4414 | 0.6923 | 0.1748 | sweep |
| pct0.03/0.08f0 | primary | share_rhea | na | 34 | 0.4706 | 0.3145 | 0.6326 | 0.6962 | sweep |
| pct0.03/0.1f0 | primary | share_rhea | na | 17 | 0.5294 | 0.3096 | 0.7383 | 0.5000 | sweep |
| pct0.03/0.1f15 | primary | share_rhea | na | 17 | 0.5294 | 0.3096 | 0.7383 | 0.5000 | sweep |
| pct0.03/0.12f0 | primary | share_rhea | na | 14 | 0.3571 | 0.1634 | 0.6124 | 0.9102 | sweep |
| pct0.03/0.12f15 | primary | share_rhea | na | 13 | 0.3846 | 0.1771 | 0.6448 | 0.8666 | sweep |
| pct0.02/0.08f15 | primary | share_rhea | na | 29 | 0.5862 | 0.4074 | 0.7449 | 0.2291 | sweep |
| pct0.05/0.08f15 | primary | share_rhea | na | 29 | 0.5862 | 0.4074 | 0.7449 | 0.2291 | sweep |
| pct0.03/0.08f15 | tol0 | share_rhea | na | 29 | 0.5862 | 0.4074 | 0.7449 | 0.2291 | sweep |
| pct0.03/0.08f15 | djt0.12 | share_rhea | na | 29 | 0.5862 | 0.4074 | 0.7449 | 0.2291 | sweep |
| atr2.0/14f15 | primary | share_rhea | na | 27 | 0.7037 | 0.5152 | 0.8415 | 0.0261 | sweep |
| pivot5 | primary | share_rhea | na | 145 | 0.3517 | 0.2787 | 0.4324 | 0.9999 | sweep |

### Secondary-threshold grid (15-session filter), label inputs

| secondary_pct | n | estimate | p raw | Bonferroni bound |
|---|---|---|---|---|
| 0.05 | 67 | 0.5672 | 0.164216 | 0.7062 |
| 0.06 | 56 | 0.5714 | 0.174841 | 0.7211 |
| 0.08 | 29 | 0.5862 | 0.229129 | 0.7787 |
| 0.1 | 17 | 0.5294 | 0.500000 | 0.7803 |
| 0.12 | 13 | 0.3846 | 0.866577 | 0.7016 |

### Duration summary

Calendar days: median 48.0, IQR [22.0, 88.0]. Trading bars: median 34.0, IQR [16.0, 63.0]. Compare the sweep rows with `f0` (no 15-session filter) next to the primary.

## Caveats

- The 15-session causal filter excludes secondaries shorter than 15 sessions (about 21 calendar days), so the lower Rhea bound is partly enforced by construction. The no-filter variant is the relevant comparison and must be printed next to the primary.

### Data coverage (verbatim from the decision table, section 5)

- `^DJT` history in `dow.mkt_klines` begins **1992-01-02**. Nothing in this protocol tests Dow Theory on 1897-1991 data; claims about that period default to `insufficient-evidence` per `docs/team_design.md` section 5 unless a long-history source is loaded under a new, hashed protocol.
- `^DJI` 1992-01-02 to 2026-11-06 = 8,775 bars. At the committed spec (8%, 15-session filter) the spec review counted about 82 secondary swings, about 37 reaction legs and **10 primary reversals** on `^DJI` (12 without the filter, 8 at 10%). Hence the pre-run expectation: R2, R3 and probably R8 fall below the evidence floor and receive `insufficient-evidence`; R1, R4, R5 have `n` in the 30-40 range and are decidable but with wide intervals; R6 and R7 counts are unknown before the run. These are expectations, not thresholds; the labels follow section 3 whatever the counts turn out to be.
- Index volume is sparse or zero before 2000 and is a vendor-constructed aggregate afterward; R7 therefore starts 2000-01-03 and its `SP_IYT` robustness uses ETF volume (2004+).
- `^GSPC` and `^IXIC` have `analysis_start` clipping (first real OHLC 1962-07-02 and 1984-10-11); they are not used in any label-driving row. `IYT` begins 2004, so the `SP_IYT` pair covers 2004-2026 only.
- Price indices exclude dividends (R8 caveat). The `^DJI` series is yfinance-sourced; vendor revisions after 2026-11-06 do not change the frozen `period_end` of label-driving runs.
- Forward windows overlap at `h = 60` and `h = 120`; effective sample sizes are smaller than `n`; the number of event clusters is reported next to `n` for every return-based row.
- The primary threshold was selected on this sample (1.8); R4 and R5 labels are therefore computed under the worst-grid-point rule and every R4/R5 report prints the full threshold range.
