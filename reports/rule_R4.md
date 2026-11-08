# R4 Secondary retracement (`rule_key: secondary_retracement`)

Pair `DJ` (^DJI, ^DJT), 1992-01-02 to 2026-11-06, 8775 bars. Specification `pct0.03/0.08f15`. Run `a6d2d48e46014e7da3cc7c6be7ce8a02`.
Config hash `e6f5b9cd228e458809a42aa2a5c5e2811175de3d74fafca1a3496c6ac68ae24e`. Decision table sha256 `c8675eff2b281ac6f4fa8ed790063ecaf1e063d78f20fa9569ded1988be39836`. Bootstrap iterations 2000, seed 20261108.

## Event definition

Confirmed counter-trend secondary swings with a retrace ratio. Metric: share with 1/3 <= rr <= 2/3, null 1/3 (uniform rr). Exact binomial, Wilson CI; the label uses the worst point of the `secondary_pct` grid.

## Result

| field | value |
|---|---|
| events n | 44 |
| clusters | n/a |
| right-censored | 0 |
| metric | share_band na |
| estimate | 0.4091 |
| 95% CI | [0.2769, 0.5559] |
| null value | 0.3333 |
| p raw (one-sided, predicted direction) | 0.181585 |
| p used in the Holm family | 0.510467 |
| p Holm (family of 8) | 1.000000 |
| Bonferroni one-sided upper bound (level 0.99375) | 0.5940 |
| sub-sample split | 2009-12-31 (A up to and including, B after) |
| sub-sample A | 0.3810 (n = 21) |
| sub-sample B | 0.4348 (n = 23) |
| sub-sample signs vs null | A+ B+ |

## Label

- Data label: **insufficient-evidence**. Reason: not significant after Holm, or sub-samples disagree.
- Literature label: **literature-disputed** (registry rows R-008,R-009,R-010,R-011).
- Refutation bound actually computed: one-sided 0.99375 upper bound 0.5940 against null 0.3333; it does not lie below the null, so refutation is excluded.

## Descriptive and robustness rows

| spec | variant | metric | horizon | n | value | CI low | CI high | p raw | notes |
|---|---|---|---|---|---|---|---|---|---|
| pct0.03/0.08f15 | share_sf | share_third_half | na | 44 | 0.2045 | 0.1115 | 0.3450 | 0.3063 |  |
| pct0.03/0.08f15 | share_gt1 | share_rr_gt_1 | na | 44 | 0.2273 | 0.1284 | 0.3699 | 0.0000 |  |
| pct0.03/0.08f15 | share_lt_third | share_rr_lt_third | na | 44 | 0.1591 | 0.0793 | 0.2937 | 0.0000 |  |
| pct0.03/0.08f15 | majority | share_band | na | 44 | 0.4091 | 0.2769 | 0.5559 | 0.9129 |  |
| pct0.03/0.08f15 | all_legs | share_band | na | 82 | 0.2195 | 0.1436 | 0.3205 | 0.9913 |  |
| pct0.03/0.08f15 | all_legs_sf | share_third_half | na | 82 | 0.1098 | 0.0588 | 0.1956 | 0.9438 |  |
| pct0.03/0.08f15 | median_rr | median_rr | na | 44 | 0.6352 | 0.5081 | 0.7674 | n/a |  |
| pct0.03/0.08f15 | sub_A | share_band | na | 21 | 0.3810 | n/a | n/a | n/a | sub-sample split 2009-12-31 |
| pct0.03/0.08f15 | sub_B | share_band | na | 23 | 0.4348 | n/a | n/a | n/a | sub-sample split 2009-12-31 |

## Specification sweep (descriptive)

Range of the primary metric over 15 grid points (not a selected optimum): min 0.2549, median 0.3889, max 0.4091.

| spec | variant | metric | horizon | n | value | CI low | CI high | p raw | notes |
|---|---|---|---|---|---|---|---|---|---|
| pct0.03/0.05f0 | primary | share_band | na | 113 | 0.3451 | 0.2639 | 0.4366 | 0.4298 | sweep |
| pct0.03/0.05f15 | primary | share_band | na | 100 | 0.3400 | 0.2546 | 0.4372 | 0.4812 | sweep |
| pct0.03/0.06f0 | primary | share_band | na | 87 | 0.4023 | 0.3055 | 0.5074 | 0.1066 | sweep |
| pct0.03/0.06f15 | primary | share_band | na | 80 | 0.3375 | 0.2435 | 0.4464 | 0.5105 | sweep |
| pct0.03/0.08f0 | primary | share_band | na | 46 | 0.3913 | 0.2639 | 0.5354 | 0.2462 | sweep |
| pct0.03/0.1f0 | primary | share_band | na | 24 | 0.3333 | 0.1797 | 0.5329 | 0.5762 | sweep |
| pct0.03/0.1f15 | primary | share_band | na | 23 | 0.3478 | 0.1881 | 0.5511 | 0.5193 | sweep |
| pct0.03/0.12f0 | primary | share_band | na | 18 | 0.3889 | 0.2031 | 0.6138 | 0.3915 | sweep |
| pct0.03/0.12f15 | primary | share_band | na | 18 | 0.3889 | 0.2031 | 0.6138 | 0.3915 | sweep |
| pct0.02/0.08f15 | primary | share_band | na | 44 | 0.4091 | 0.2769 | 0.5559 | 0.1816 | sweep |
| pct0.05/0.08f15 | primary | share_band | na | 44 | 0.4091 | 0.2769 | 0.5559 | 0.1816 | sweep |
| pct0.03/0.08f15 | tol0 | share_band | na | 45 | 0.4000 | 0.2702 | 0.5455 | 0.2128 | sweep |
| pct0.03/0.08f15 | djt0.12 | share_band | na | 44 | 0.4091 | 0.2769 | 0.5559 | 0.1816 | sweep |
| atr2.0/14f15 | primary | share_band | na | 51 | 0.2549 | 0.1555 | 0.3887 | 0.9120 | sweep |
| pivot5 | primary | share_band | na | 230 | 0.3435 | 0.2851 | 0.4070 | 0.3960 | sweep |

### Secondary-threshold grid (15-session filter), label inputs

| secondary_pct | n | estimate | p raw | Bonferroni bound |
|---|---|---|---|---|
| 0.05 | 100 | 0.3400 | 0.481197 | 0.4646 |
| 0.06 | 80 | 0.3375 | 0.510467 | 0.4770 |
| 0.08 | 44 | 0.4091 | 0.181585 | 0.5940 |
| 0.1 | 23 | 0.3478 | 0.519308 | 0.6027 |
| 0.12 | 18 | 0.3889 | 0.391490 | 0.6665 |

### Retrace-ratio histogram (counter-trend legs)

Deciles of rr in (0, 1], last entry rr > 1:

`[0, 1, 4, 4, 7, 5, 5, 5, 2, 1, 10]`

## Caveats

- With pct 8% swings a secondary leg is at least 8% of price, so `rr >= 0.08 / amplitude of the preceding leg`. Small preceding legs force high `rr`. The sweep over `secondary_pct` is therefore mandatory and the range is reported.

### Data coverage (verbatim from the decision table, section 5)

- `^DJT` history in `dow.mkt_klines` begins **1992-01-02**. Nothing in this protocol tests Dow Theory on 1897-1991 data; claims about that period default to `insufficient-evidence` per `docs/team_design.md` section 5 unless a long-history source is loaded under a new, hashed protocol.
- `^DJI` 1992-01-02 to 2026-11-06 = 8,775 bars. At the committed spec (8%, 15-session filter) the spec review counted about 82 secondary swings, about 37 reaction legs and **10 primary reversals** on `^DJI` (12 without the filter, 8 at 10%). Hence the pre-run expectation: R2, R3 and probably R8 fall below the evidence floor and receive `insufficient-evidence`; R1, R4, R5 have `n` in the 30-40 range and are decidable but with wide intervals; R6 and R7 counts are unknown before the run. These are expectations, not thresholds; the labels follow section 3 whatever the counts turn out to be.
- Index volume is sparse or zero before 2000 and is a vendor-constructed aggregate afterward; R7 therefore starts 2000-01-03 and its `SP_IYT` robustness uses ETF volume (2004+).
- `^GSPC` and `^IXIC` have `analysis_start` clipping (first real OHLC 1962-07-02 and 1984-10-11); they are not used in any label-driving row. `IYT` begins 2004, so the `SP_IYT` pair covers 2004-2026 only.
- Price indices exclude dividends (R8 caveat). The `^DJI` series is yfinance-sourced; vendor revisions after 2026-11-06 do not change the frozen `period_end` of label-driving runs.
- Forward windows overlap at `h = 60` and `h = 120`; effective sample sizes are smaller than `n`; the number of event clusters is reported next to `n` for every return-based row.
- The primary threshold was selected on this sample (1.8); R4 and R5 labels are therefore computed under the worst-grid-point rule and every R4/R5 report prints the full threshold range.

Correction (R11 audit): `^DJI` volume is positive on every bar since 1992. What exists is a level break (annual mean 21 to 99 million shares in 1992-1999 against about 205 million in 2000) and a second break in 2016/2017 (about 117 against 311 million), which lies inside R7's sample. The 2000 start stays as pre-registered; only the normalised variant partly handles the 2016/2017 break.
