# R5 Secondary duration (`rule_key: secondary_duration`)

Pair `DJ` (^DJI, ^DJT), 1992-01-02 to 2026-11-06, 8775 bars. Specification `pct0.03/0.08f15`. Run `a6d2d48e46014e7da3cc7c6be7ce8a02`.
Config hash `e6f5b9cd228e458809a42aa2a5c5e2811175de3d74fafca1a3496c6ac68ae24e`. Decision table sha256 `c8675eff2b281ac6f4fa8ed790063ecaf1e063d78f20fa9569ded1988be39836`. Bootstrap iterations 2000, seed 20261108.

## Event definition

Same events as R4. Metric: share lasting 21 to 90 calendar days, null 0.5. Exact binomial, Wilson CI; the label uses the worst point of the `secondary_pct` grid.

## Result

| field | value |
|---|---|
| events n | 44 |
| clusters | n/a |
| right-censored | 0 |
| metric | share_rhea na |
| estimate | 0.7273 |
| 95% CI | [0.5815, 0.8365] |
| null value | 0.5000 |
| p raw (one-sided, predicted direction) | 0.001829 |
| p used in the Holm family | 0.044313 |
| p Holm (family of 8) | 0.310191 |
| Bonferroni one-sided upper bound (level 0.99375) | 0.8585 |
| sub-sample split | 2009-12-31 (A up to and including, B after) |
| sub-sample A | 0.7619 (n = 21) |
| sub-sample B | 0.6957 (n = 23) |
| sub-sample signs vs null | A+ B+ |

## Label

- Data label: **insufficient-evidence**. Reason: not significant after Holm, or sub-samples disagree.
- Literature label: **literature-disputed** (registry rows R-006,R-007).
- Refutation bound actually computed: one-sided 0.99375 upper bound 0.8585 against null 0.5000; it does not lie below the null, so refutation is excluded.

## Descriptive and robustness rows

| spec | variant | metric | horizon | n | value | CI low | CI high | p raw | notes |
|---|---|---|---|---|---|---|---|---|---|
| pct0.03/0.08f15 | schannep | share_schannep | na | 44 | 0.9773 | 0.8819 | 0.9960 | 0.0000 |  |
| pct0.03/0.08f15 | gt_max | share_gt_max_days | na | 44 | 0.2273 | 0.1284 | 0.3699 | 0.0000 |  |
| pct0.03/0.08f15 | lt_min | share_lt_min_days | na | 44 | 0.0455 | 0.0126 | 0.1513 | 0.0000 |  |
| pct0.03/0.08f15 | median_d_cal | median_days | na | 44 | 54.5000 | 33.2500 | 83.2500 | n/a | ci columns hold the inter-quartile range |
| pct0.03/0.08f15 | sub_A | share_rhea | na | 21 | 0.7619 | n/a | n/a | n/a | sub-sample split 2009-12-31 |
| pct0.03/0.08f15 | sub_B | share_rhea | na | 23 | 0.6957 | n/a | n/a | n/a | sub-sample split 2009-12-31 |

## Specification sweep (descriptive)

Range of the primary metric over 15 grid points (not a selected optimum): min 0.4261, median 0.6087, max 0.7451.

| spec | variant | metric | horizon | n | value | CI low | CI high | p raw | notes |
|---|---|---|---|---|---|---|---|---|---|
| pct0.03/0.05f0 | primary | share_rhea | na | 113 | 0.4690 | 0.3796 | 0.5605 | 0.7741 | sweep |
| pct0.03/0.05f15 | primary | share_rhea | na | 100 | 0.5900 | 0.4920 | 0.6813 | 0.0443 | sweep |
| pct0.03/0.06f0 | primary | share_rhea | na | 87 | 0.5632 | 0.4585 | 0.6626 | 0.1418 | sweep |
| pct0.03/0.06f15 | primary | share_rhea | na | 80 | 0.6500 | 0.5408 | 0.7455 | 0.0048 | sweep |
| pct0.03/0.08f0 | primary | share_rhea | na | 46 | 0.6739 | 0.5297 | 0.7913 | 0.0129 | sweep |
| pct0.03/0.1f0 | primary | share_rhea | na | 24 | 0.5417 | 0.3507 | 0.7211 | 0.4194 | sweep |
| pct0.03/0.1f15 | primary | share_rhea | na | 23 | 0.6087 | 0.4079 | 0.7784 | 0.2024 | sweep |
| pct0.03/0.12f0 | primary | share_rhea | na | 18 | 0.5556 | 0.3372 | 0.7544 | 0.4073 | sweep |
| pct0.03/0.12f15 | primary | share_rhea | na | 18 | 0.5556 | 0.3372 | 0.7544 | 0.4073 | sweep |
| pct0.02/0.08f15 | primary | share_rhea | na | 44 | 0.7273 | 0.5815 | 0.8365 | 0.0018 | sweep |
| pct0.05/0.08f15 | primary | share_rhea | na | 44 | 0.7273 | 0.5815 | 0.8365 | 0.0018 | sweep |
| pct0.03/0.08f15 | tol0 | share_rhea | na | 45 | 0.7333 | 0.5896 | 0.8404 | 0.0012 | sweep |
| pct0.03/0.08f15 | djt0.12 | share_rhea | na | 44 | 0.7273 | 0.5815 | 0.8365 | 0.0018 | sweep |
| atr2.0/14f15 | primary | share_rhea | na | 51 | 0.7451 | 0.6113 | 0.8445 | 0.0003 | sweep |
| pivot5 | primary | share_rhea | na | 230 | 0.4261 | 0.3639 | 0.4907 | 0.9896 | sweep |

### Secondary-threshold grid (15-session filter), label inputs

| secondary_pct | n | estimate | p raw | Bonferroni bound |
|---|---|---|---|---|
| 0.05 | 100 | 0.5900 | 0.044313 | 0.7040 |
| 0.06 | 80 | 0.6500 | 0.004841 | 0.7679 |
| 0.08 | 44 | 0.7273 | 0.001829 | 0.8585 |
| 0.1 | 23 | 0.6087 | 0.202436 | 0.8121 |
| 0.12 | 18 | 0.5556 | 0.407265 | 0.7938 |

### Duration summary

Calendar days: median 54.5, IQR [33.2, 83.2]. Trading bars: median 38.5, IQR [22.8, 58.2]. Compare the sweep rows with `f0` (no 15-session filter) next to the primary.

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

Correction (R11 audit): `^DJI` volume is positive on every bar since 1992. What exists is a level break (annual mean 21 to 99 million shares in 1992-1999 against about 205 million in 2000) and a second break in 2016/2017 (about 117 against 311 million), which lies inside R7's sample. The 2000 start stays as pre-registered; only the normalised variant partly handles the 2016/2017 break.
