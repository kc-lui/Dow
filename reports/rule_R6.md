# R6 Line breakout (`rule_key: line_breakout`)

Pair `DJ` (^DJI, ^DJT), 1992-01-02 to 2026-11-06, 8775 bars. Specification `pct0.03/0.08f15`. Run `a6d2d48e46014e7da3cc7c6be7ce8a02`.
Config hash `e6f5b9cd228e458809a42aa2a5c5e2811175de3d74fafca1a3496c6ac68ae24e`. Decision table sha256 `c8675eff2b281ac6f4fa8ed790063ecaf1e063d78f20fa9569ded1988be39836`. Bootstrap iterations 2000, seed 20261108.

## Event definition

Line breakouts confirmed by both averages (event bar `confirmed_ts`). Metric: share with `sgn * F_20(c) > 0`, null 0.5. Exact binomial, Wilson CI.

## Result

| field | value |
|---|---|
| events n | 87 |
| clusters | 77 |
| right-censored | 1 |
| metric | agree h20 |
| estimate | 0.4138 |
| 95% CI | [0.3161, 0.5188] |
| null value | 0.5000 |
| p raw (one-sided, predicted direction) | 0.957156 |
| p used in the Holm family | 0.957156 |
| p Holm (family of 8) | 1.000000 |
| Bonferroni one-sided upper bound (level 0.99375) | 0.5471 |
| sub-sample split | 2009-12-31 (A up to and including, B after) |
| sub-sample A | 0.4250 (n = 40) |
| sub-sample B | 0.4043 (n = 47) |
| sub-sample signs vs null | A- B- |

## Label

- Data label: **insufficient-evidence**. Reason: not significant after Holm, or sub-samples disagree.
- Literature label: **literature-consensus** (registry rows R-022,R-023,R-024,R-025,R-026,R-027).
- Refutation bound actually computed: one-sided 0.99375 upper bound 0.5471 against null 0.5000; it does not lie below the null, so refutation is excluded.

### Exploratory rows (R11 F4)

For the `single` and `conf_minus_single` rows, the single group is classified with information up to `c + h`, the outcome window itself, and a reversal matched later than `c + h` is in both groups. Treat these rows as exploratory; the label is unchanged (recommended redefinition for v3 in `analysis/protocol_deviations.md`).

## Descriptive and robustness rows

| spec | variant | metric | horizon | n | value | CI low | CI high | p raw | notes |
|---|---|---|---|---|---|---|---|---|---|
| pct0.03/0.08f15 | horizon60 | agree | h60 | 86 | 0.5233 | 0.4190 | 0.6255 | 0.3733 |  |
| pct0.03/0.08f15 | horizon120 | agree | h120 | 84 | 0.5000 | 0.3954 | 0.6046 | 0.5434 |  |
| pct0.03/0.08f15 | single | agree | h20 | 15 | 0.0667 | 0.0119 | 0.2982 | 1.0000 | exploratory: the single-group classification uses information up to c+h (R11 F4) |
| pct0.03/0.08f15 | conf_minus_single | agree_diff | h20 | 102 | 0.3471 | n/a | n/a | 0.0065 | groups confirmed=87 single=15; exploratory: the single-group classification uses information up to c+h (R11 F4) |
| pct0.03/0.08f15 | excess | mean_excess_logret | h20 | 87 | -0.0015 | -0.0088 | 0.0062 | 0.6382 |  |
| pct0.03/0.08f15 | sub_A | agree | h20 | 40 | 0.4250 | n/a | n/a | n/a | sub-sample split 2009-12-31 |
| pct0.03/0.08f15 | sub_B | agree | h20 | 47 | 0.4043 | n/a | n/a | n/a | sub-sample split 2009-12-31 |

## Specification sweep (descriptive)

Range of the primary metric over 31 grid points (not a selected optimum): min 0.3077, median 0.4138, max 0.5395.

| spec | variant | metric | horizon | n | value | CI low | CI high | p raw | notes |
|---|---|---|---|---|---|---|---|---|---|
| pct0.03/0.05f0 | primary | agree | h20 | 87 | 0.4138 | 0.3161 | 0.5188 | 0.9572 | sweep; lines=103; breakouts=103; mean_line_days=30.0; censored=1 |
| pct0.03/0.05f15 | primary | agree | h20 | 87 | 0.4138 | 0.3161 | 0.5188 | 0.9572 | sweep; lines=103; breakouts=103; mean_line_days=30.0; censored=1 |
| pct0.03/0.06f0 | primary | agree | h20 | 87 | 0.4138 | 0.3161 | 0.5188 | 0.9572 | sweep; lines=103; breakouts=103; mean_line_days=30.0; censored=1 |
| pct0.03/0.06f15 | primary | agree | h20 | 87 | 0.4138 | 0.3161 | 0.5188 | 0.9572 | sweep; lines=103; breakouts=103; mean_line_days=30.0; censored=1 |
| pct0.03/0.08f0 | primary | agree | h20 | 87 | 0.4138 | 0.3161 | 0.5188 | 0.9572 | sweep; lines=103; breakouts=103; mean_line_days=30.0; censored=1 |
| pct0.03/0.1f0 | primary | agree | h20 | 87 | 0.4138 | 0.3161 | 0.5188 | 0.9572 | sweep; lines=103; breakouts=103; mean_line_days=30.0; censored=1 |
| pct0.03/0.1f15 | primary | agree | h20 | 87 | 0.4138 | 0.3161 | 0.5188 | 0.9572 | sweep; lines=103; breakouts=103; mean_line_days=30.0; censored=1 |
| pct0.03/0.12f0 | primary | agree | h20 | 87 | 0.4138 | 0.3161 | 0.5188 | 0.9572 | sweep; lines=103; breakouts=103; mean_line_days=30.0; censored=1 |
| pct0.03/0.12f15 | primary | agree | h20 | 87 | 0.4138 | 0.3161 | 0.5188 | 0.9572 | sweep; lines=103; breakouts=103; mean_line_days=30.0; censored=1 |
| pct0.02/0.08f15 | primary | agree | h20 | 87 | 0.4138 | 0.3161 | 0.5188 | 0.9572 | sweep; lines=103; breakouts=103; mean_line_days=30.0; censored=1 |
| pct0.05/0.08f15 | primary | agree | h20 | 87 | 0.4138 | 0.3161 | 0.5188 | 0.9572 | sweep; lines=103; breakouts=103; mean_line_days=30.0; censored=1 |
| pct0.03/0.08f15 | tol0 | agree | h20 | 87 | 0.4138 | 0.3161 | 0.5188 | 0.9572 | sweep; lines=103; breakouts=103; mean_line_days=30.0; censored=1 |
| pct0.03/0.08f15 | djt0.12 | agree | h20 | 87 | 0.4138 | 0.3161 | 0.5188 | 0.9572 | sweep; lines=103; breakouts=103; mean_line_days=30.0; censored=1 |
| atr2.0/14f15 | primary | agree | h20 | 87 | 0.4138 | 0.3161 | 0.5188 | 0.9572 | sweep; lines=103; breakouts=103; mean_line_days=30.0; censored=1 |
| pivot5 | primary | agree | h20 | 87 | 0.4138 | 0.3161 | 0.5188 | 0.9572 | sweep; lines=103; breakouts=103; mean_line_days=30.0; censored=1 |
| pct0.03/0.08f15 | band0.03_min10_drift0.5 | agree | h20 | 81 | 0.4444 | 0.3412 | 0.5527 | 0.8668 | line sweep; lines=103; breakouts=103; mean_line_days=17.5; censored=0 |
| pct0.03/0.08f15 | band0.03_min10_driftnone | agree | h20 | 239 | 0.5021 | 0.4392 | 0.5649 | 0.5000 | line sweep; lines=301; breakouts=301; mean_line_days=17.7; censored=1 |
| pct0.03/0.08f15 | band0.03_min15_drift0.5 | agree | h20 | 26 | 0.3077 | 0.1650 | 0.4999 | 0.9855 | line sweep; lines=33; breakouts=33; mean_line_days=24.0; censored=0 |
| pct0.03/0.08f15 | band0.03_min15_driftnone | agree | h20 | 87 | 0.4253 | 0.3267 | 0.5302 | 0.9335 | line sweep; lines=106; breakouts=106; mean_line_days=24.3; censored=0 |
| pct0.03/0.08f15 | band0.03_min28_drift0.5 | agree | h20 | 0 | n/a | n/a | n/a | n/a | line sweep; lines=0; breakouts=0; mean_line_days=0.0; censored=0 |
| pct0.03/0.08f15 | band0.03_min28_driftnone | agree | h20 | 3 | 0.3333 | 0.0615 | 0.7923 | 0.8750 | line sweep; lines=4; breakouts=4; mean_line_days=41.8; censored=0 |
| pct0.03/0.08f15 | band0.05_min10_drift0.5 | agree | h20 | 142 | 0.4648 | 0.3848 | 0.5467 | 0.8220 | line sweep; lines=167; breakouts=167; mean_line_days=23.6; censored=1 |
| pct0.03/0.08f15 | band0.05_min10_driftnone | agree | h20 | 355 | 0.5014 | 0.4497 | 0.5531 | 0.5000 | line sweep; lines=425; breakouts=425; mean_line_days=23.7; censored=1 |
| pct0.03/0.08f15 | band0.05_min15_driftnone | agree | h20 | 218 | 0.4679 | 0.4028 | 0.5341 | 0.8452 | line sweep; lines=264; breakouts=264; mean_line_days=29.9; censored=1 |
| pct0.03/0.08f15 | band0.05_min28_drift0.5 | agree | h20 | 24 | 0.3333 | 0.1797 | 0.5329 | 0.9680 | line sweep; lines=26; breakouts=26; mean_line_days=45.0; censored=1 |
| pct0.03/0.08f15 | band0.05_min28_driftnone | agree | h20 | 56 | 0.4464 | 0.3239 | 0.5759 | 0.8252 | line sweep; lines=71; breakouts=71; mean_line_days=47.6; censored=1 |
| pct0.03/0.08f15 | band0.07_min10_drift0.5 | agree | h20 | 89 | 0.5281 | 0.4254 | 0.6285 | 0.3359 | line sweep; lines=99; breakouts=99; mean_line_days=35.9; censored=1 |
| pct0.03/0.08f15 | band0.07_min10_driftnone | agree | h20 | 296 | 0.5169 | 0.4601 | 0.5732 | 0.3005 | line sweep; lines=337; breakouts=337; mean_line_days=33.8; censored=1 |
| pct0.03/0.08f15 | band0.07_min15_drift0.5 | agree | h20 | 76 | 0.5395 | 0.4282 | 0.6469 | 0.2833 | line sweep; lines=87; breakouts=87; mean_line_days=36.9; censored=0 |
| pct0.03/0.08f15 | band0.07_min15_driftnone | agree | h20 | 231 | 0.5152 | 0.4510 | 0.5788 | 0.3466 | line sweep; lines=272; breakouts=272; mean_line_days=39.1; censored=1 |
| pct0.03/0.08f15 | band0.07_min28_drift0.5 | agree | h20 | 35 | 0.4857 | 0.3299 | 0.6443 | 0.6321 | line sweep; lines=42; breakouts=42; mean_line_days=49.9; censored=1 |
| pct0.03/0.08f15 | band0.07_min28_driftnone | agree | h20 | 111 | 0.5045 | 0.4129 | 0.5958 | 0.5000 | line sweep; lines=138; breakouts=138; mean_line_days=54.7; censored=1 |

## Caveats


### Data coverage (verbatim from the decision table, section 5)

- `^DJT` history in `dow.mkt_klines` begins **1992-01-02**. Nothing in this protocol tests Dow Theory on 1897-1991 data; claims about that period default to `insufficient-evidence` per `docs/team_design.md` section 5 unless a long-history source is loaded under a new, hashed protocol.
- `^DJI` 1992-01-02 to 2026-11-06 = 8,775 bars. At the committed spec (8%, 15-session filter) the spec review counted about 82 secondary swings, about 37 reaction legs and **10 primary reversals** on `^DJI` (12 without the filter, 8 at 10%). Hence the pre-run expectation: R2, R3 and probably R8 fall below the evidence floor and receive `insufficient-evidence`; R1, R4, R5 have `n` in the 30-40 range and are decidable but with wide intervals; R6 and R7 counts are unknown before the run. These are expectations, not thresholds; the labels follow section 3 whatever the counts turn out to be.
- Index volume is sparse or zero before 2000 and is a vendor-constructed aggregate afterward; R7 therefore starts 2000-01-03 and its `SP_IYT` robustness uses ETF volume (2004+).
- `^GSPC` and `^IXIC` have `analysis_start` clipping (first real OHLC 1962-07-02 and 1984-10-11); they are not used in any label-driving row. `IYT` begins 2004, so the `SP_IYT` pair covers 2004-2026 only.
- Price indices exclude dividends (R8 caveat). The `^DJI` series is yfinance-sourced; vendor revisions after 2026-11-06 do not change the frozen `period_end` of label-driving runs.
- Forward windows overlap at `h = 60` and `h = 120`; effective sample sizes are smaller than `n`; the number of event clusters is reported next to `n` for every return-based row.
- The primary threshold was selected on this sample (1.8); R4 and R5 labels are therefore computed under the worst-grid-point rule and every R4/R5 report prints the full threshold range.

Correction (R11 audit): `^DJI` volume is positive on every bar since 1992. What exists is a level break (annual mean 21 to 99 million shares in 1992-1999 against about 205 million in 2000) and a second break in 2016/2017 (about 117 against 311 million), which lies inside R7's sample. The 2000 start stays as pre-registered; only the normalised variant partly handles the 2016/2017 break.
