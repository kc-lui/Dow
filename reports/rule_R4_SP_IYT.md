# R4 Secondary retracement (`rule_key: secondary_retracement`)

Pair `SP_IYT` (SPY, IYT), 2004-01-02 to 2026-11-06, 5749 bars. Specification `pct0.03/0.08f15`. Run `a6d2d48e46014e7da3cc7c6be7ce8a02`.
Config hash `e6f5b9cd228e458809a42aa2a5c5e2811175de3d74fafca1a3496c6ac68ae24e`. Decision table sha256 `c8675eff2b281ac6f4fa8ed790063ecaf1e063d78f20fa9569ded1988be39836`. Bootstrap iterations 2000, seed 20261108.

## Event definition

Confirmed counter-trend secondary swings with a retrace ratio. Metric: share with 1/3 <= rr <= 2/3, null 1/3 (uniform rr). Exact binomial, Wilson CI; the label uses the worst point of the `secondary_pct` grid.

## Result

| field | value |
|---|---|
| events n | 29 |
| clusters | n/a |
| right-censored | 0 |
| metric | share_band na |
| estimate | 0.3103 |
| 95% CI | [0.1728, 0.4923] |
| null value | 0.3333 |
| p raw (one-sided, predicted direction) | 0.670266 |
| p used in the Holm family | n/a |
| p Holm (family of 8) | n/a |
| Bonferroni one-sided upper bound (level 0.99375) | 0.5415 |
| sub-sample split | 2015-12-31 (A up to and including, B after) |
| sub-sample A | 0.4375 (n = 16) |
| sub-sample B | 0.1538 (n = 13) |
| sub-sample signs vs null | A+ B- |

## Label

- No label: `SP_IYT` is a robustness pair (labels come from `DJ` only).

## Descriptive and robustness rows

| spec | variant | metric | horizon | n | value | CI low | CI high | p raw | notes |
|---|---|---|---|---|---|---|---|---|---|
| pct0.03/0.08f15 | share_sf | share_third_half | na | 29 | 0.1724 | 0.0760 | 0.3455 | 0.5436 |  |
| pct0.03/0.08f15 | share_gt1 | share_rr_gt_1 | na | 29 | 0.2414 | 0.1222 | 0.4211 | 0.0000 |  |
| pct0.03/0.08f15 | share_lt_third | share_rr_lt_third | na | 29 | 0.2414 | 0.1222 | 0.4211 | 0.0000 |  |
| pct0.03/0.08f15 | majority | share_band | na | 29 | 0.3103 | 0.1728 | 0.4923 | 0.9879 |  |
| pct0.03/0.08f15 | all_legs | share_band | na | 52 | 0.1731 | 0.0938 | 0.2973 | 0.9969 |  |
| pct0.03/0.08f15 | all_legs_sf | share_third_half | na | 52 | 0.0962 | 0.0418 | 0.2061 | 0.9485 |  |
| pct0.03/0.08f15 | median_rr | median_rr | na | 29 | 0.5388 | 0.4121 | 0.7371 | n/a |  |
| pct0.03/0.08f15 | sub_A | share_band | na | 16 | 0.4375 | n/a | n/a | n/a | sub-sample split 2015-12-31 |
| pct0.03/0.08f15 | sub_B | share_band | na | 13 | 0.1538 | n/a | n/a | n/a | sub-sample split 2015-12-31 |

## Specification sweep (descriptive)

Range of the primary metric over 15 grid points (not a selected optimum): min 0.1765, median 0.3103, max 0.4375.

| spec | variant | metric | horizon | n | value | CI low | CI high | p raw | notes |
|---|---|---|---|---|---|---|---|---|---|
| pct0.03/0.05f0 | primary | share_band | na | 80 | 0.4375 | 0.3341 | 0.5466 | 0.0335 | sweep |
| pct0.03/0.05f15 | primary | share_band | na | 67 | 0.3582 | 0.2540 | 0.4778 | 0.3763 | sweep |
| pct0.03/0.06f0 | primary | share_band | na | 62 | 0.4032 | 0.2902 | 0.5275 | 0.1510 | sweep |
| pct0.03/0.06f15 | primary | share_band | na | 56 | 0.3929 | 0.2758 | 0.5237 | 0.2094 | sweep |
| pct0.03/0.08f0 | primary | share_band | na | 34 | 0.3235 | 0.1913 | 0.4916 | 0.6117 | sweep |
| pct0.03/0.1f0 | primary | share_band | na | 17 | 0.1765 | 0.0619 | 0.4103 | 0.9558 | sweep |
| pct0.03/0.1f15 | primary | share_band | na | 17 | 0.1765 | 0.0619 | 0.4103 | 0.9558 | sweep |
| pct0.03/0.12f0 | primary | share_band | na | 14 | 0.2857 | 0.1172 | 0.5465 | 0.7388 | sweep |
| pct0.03/0.12f15 | primary | share_band | na | 13 | 0.3077 | 0.1268 | 0.5763 | 0.6776 | sweep |
| pct0.02/0.08f15 | primary | share_band | na | 29 | 0.3103 | 0.1728 | 0.4923 | 0.6703 | sweep |
| pct0.05/0.08f15 | primary | share_band | na | 29 | 0.3103 | 0.1728 | 0.4923 | 0.6703 | sweep |
| pct0.03/0.08f15 | tol0 | share_band | na | 29 | 0.3103 | 0.1728 | 0.4923 | 0.6703 | sweep |
| pct0.03/0.08f15 | djt0.12 | share_band | na | 29 | 0.3103 | 0.1728 | 0.4923 | 0.6703 | sweep |
| atr2.0/14f15 | primary | share_band | na | 27 | 0.3704 | 0.2153 | 0.5577 | 0.4108 | sweep |
| pivot5 | primary | share_band | na | 145 | 0.3517 | 0.2787 | 0.4324 | 0.3483 | sweep |

### Secondary-threshold grid (15-session filter), label inputs

| secondary_pct | n | estimate | p raw | Bonferroni bound |
|---|---|---|---|---|
| 0.05 | 67 | 0.3582 | 0.376325 | 0.5107 |
| 0.06 | 56 | 0.3929 | 0.209389 | 0.5586 |
| 0.08 | 29 | 0.3103 | 0.670266 | 0.5415 |
| 0.1 | 17 | 0.1765 | 0.955849 | 0.4791 |
| 0.12 | 13 | 0.3077 | 0.677576 | 0.6402 |

### Retrace-ratio histogram (counter-trend legs)

Deciles of rr in (0, 1], last entry rr > 1:

`[0, 0, 2, 7, 3, 3, 2, 3, 1, 1, 7]`

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
