# R6 Line breakout (`rule_key: line_breakout`)

Pair `SP_IYT` (SPY, IYT), 2004-01-02 to 2026-11-06, 5749 bars. Specification `pct0.03/0.08f15`. Run `a6d2d48e46014e7da3cc7c6be7ce8a02`.
Config hash `e6f5b9cd228e458809a42aa2a5c5e2811175de3d74fafca1a3496c6ac68ae24e`. Decision table sha256 `c8675eff2b281ac6f4fa8ed790063ecaf1e063d78f20fa9569ded1988be39836`. Bootstrap iterations 2000, seed 20261108.

## Event definition

Line breakouts confirmed by both averages (event bar `confirmed_ts`). Metric: share with `sgn * F_20(c) > 0`, null 0.5. Exact binomial, Wilson CI.

## Result

| field | value |
|---|---|
| events n | 50 |
| clusters | 46 |
| right-censored | 0 |
| metric | agree h20 |
| estimate | 0.5400 |
| 95% CI | [0.4040, 0.6703] |
| null value | 0.5000 |
| p raw (one-sided, predicted direction) | 0.335906 |
| p used in the Holm family | n/a |
| p Holm (family of 8) | n/a |
| Bonferroni one-sided upper bound (level 0.99375) | 0.7016 |
| sub-sample split | 2015-12-31 (A up to and including, B after) |
| sub-sample A | 0.5714 (n = 28) |
| sub-sample B | 0.5000 (n = 22) |
| sub-sample signs vs null | A+ B0 |

## Label

- No label: `SP_IYT` is a robustness pair (labels come from `DJ` only).

## Descriptive and robustness rows

| spec | variant | metric | horizon | n | value | CI low | CI high | p raw | notes |
|---|---|---|---|---|---|---|---|---|---|
| pct0.03/0.08f15 | horizon60 | agree | h60 | 50 | 0.4400 | 0.3116 | 0.5769 | 0.8389 |  |
| pct0.03/0.08f15 | horizon120 | agree | h120 | 50 | 0.4800 | 0.3480 | 0.6149 | 0.6641 |  |
| pct0.03/0.08f15 | single | agree | h20 | 17 | 0.2353 | 0.0956 | 0.4726 | 0.9936 |  |
| pct0.03/0.08f15 | conf_minus_single | agree_diff | h20 | 67 | 0.3047 | n/a | n/a | 0.0365 | groups confirmed=50 single=17 |
| pct0.03/0.08f15 | excess | mean_excess_logret | h20 | 50 | 0.0035 | -0.0138 | 0.0240 | 0.2874 |  |
| pct0.03/0.08f15 | sub_A | agree | h20 | 28 | 0.5714 | n/a | n/a | n/a | sub-sample split 2015-12-31 |
| pct0.03/0.08f15 | sub_B | agree | h20 | 22 | 0.5000 | n/a | n/a | n/a | sub-sample split 2015-12-31 |

## Specification sweep (descriptive)

Range of the primary metric over 32 grid points (not a selected optimum): min 0.0000, median 0.5400, max 0.5595.

| spec | variant | metric | horizon | n | value | CI low | CI high | p raw | notes |
|---|---|---|---|---|---|---|---|---|---|
| pct0.03/0.05f0 | primary | agree | h20 | 50 | 0.5400 | 0.4040 | 0.6703 | 0.3359 | sweep; lines=67; breakouts=67; mean_line_days=30.6; censored=0 |
| pct0.03/0.05f15 | primary | agree | h20 | 50 | 0.5400 | 0.4040 | 0.6703 | 0.3359 | sweep; lines=67; breakouts=67; mean_line_days=30.6; censored=0 |
| pct0.03/0.06f0 | primary | agree | h20 | 50 | 0.5400 | 0.4040 | 0.6703 | 0.3359 | sweep; lines=67; breakouts=67; mean_line_days=30.6; censored=0 |
| pct0.03/0.06f15 | primary | agree | h20 | 50 | 0.5400 | 0.4040 | 0.6703 | 0.3359 | sweep; lines=67; breakouts=67; mean_line_days=30.6; censored=0 |
| pct0.03/0.08f0 | primary | agree | h20 | 50 | 0.5400 | 0.4040 | 0.6703 | 0.3359 | sweep; lines=67; breakouts=67; mean_line_days=30.6; censored=0 |
| pct0.03/0.1f0 | primary | agree | h20 | 50 | 0.5400 | 0.4040 | 0.6703 | 0.3359 | sweep; lines=67; breakouts=67; mean_line_days=30.6; censored=0 |
| pct0.03/0.1f15 | primary | agree | h20 | 50 | 0.5400 | 0.4040 | 0.6703 | 0.3359 | sweep; lines=67; breakouts=67; mean_line_days=30.6; censored=0 |
| pct0.03/0.12f0 | primary | agree | h20 | 50 | 0.5400 | 0.4040 | 0.6703 | 0.3359 | sweep; lines=67; breakouts=67; mean_line_days=30.6; censored=0 |
| pct0.03/0.12f15 | primary | agree | h20 | 50 | 0.5400 | 0.4040 | 0.6703 | 0.3359 | sweep; lines=67; breakouts=67; mean_line_days=30.6; censored=0 |
| pct0.02/0.08f15 | primary | agree | h20 | 50 | 0.5400 | 0.4040 | 0.6703 | 0.3359 | sweep; lines=67; breakouts=67; mean_line_days=30.6; censored=0 |
| pct0.05/0.08f15 | primary | agree | h20 | 50 | 0.5400 | 0.4040 | 0.6703 | 0.3359 | sweep; lines=67; breakouts=67; mean_line_days=30.6; censored=0 |
| pct0.03/0.08f15 | tol0 | agree | h20 | 50 | 0.5400 | 0.4040 | 0.6703 | 0.3359 | sweep; lines=67; breakouts=67; mean_line_days=30.6; censored=0 |
| pct0.03/0.08f15 | djt0.12 | agree | h20 | 50 | 0.5400 | 0.4040 | 0.6703 | 0.3359 | sweep; lines=67; breakouts=67; mean_line_days=30.6; censored=0 |
| atr2.0/14f15 | primary | agree | h20 | 50 | 0.5400 | 0.4040 | 0.6703 | 0.3359 | sweep; lines=67; breakouts=67; mean_line_days=30.6; censored=0 |
| pivot5 | primary | agree | h20 | 50 | 0.5400 | 0.4040 | 0.6703 | 0.3359 | sweep; lines=67; breakouts=67; mean_line_days=30.6; censored=0 |
| pct0.03/0.08f15 | band0.03_min10_drift0.5 | agree | h20 | 63 | 0.3968 | 0.2853 | 0.5202 | 0.9615 | line sweep; lines=81; breakouts=81; mean_line_days=17.2; censored=0 |
| pct0.03/0.08f15 | band0.03_min10_driftnone | agree | h20 | 153 | 0.5163 | 0.4377 | 0.5941 | 0.3733 | line sweep; lines=205; breakouts=205; mean_line_days=17.5; censored=1 |
| pct0.03/0.08f15 | band0.03_min15_drift0.5 | agree | h20 | 19 | 0.4211 | 0.2314 | 0.6372 | 0.8204 | line sweep; lines=24; breakouts=24; mean_line_days=24.4; censored=0 |
| pct0.03/0.08f15 | band0.03_min15_driftnone | agree | h20 | 53 | 0.4528 | 0.3266 | 0.5855 | 0.7949 | line sweep; lines=74; breakouts=74; mean_line_days=24.4; censored=0 |
| pct0.03/0.08f15 | band0.03_min28_drift0.5 | agree | h20 | 1 | 0.0000 | 0.0000 | 0.7935 | 1.0000 | line sweep; lines=1; breakouts=1; mean_line_days=45.0; censored=0 |
| pct0.03/0.08f15 | band0.03_min28_driftnone | agree | h20 | 2 | 0.0000 | 0.0000 | 0.6576 | 1.0000 | line sweep; lines=3; breakouts=3; mean_line_days=41.3; censored=0 |
| pct0.03/0.08f15 | band0.05_min10_drift0.5 | agree | h20 | 84 | 0.5595 | 0.4531 | 0.6608 | 0.1631 | line sweep; lines=101; breakouts=101; mean_line_days=24.9; censored=0 |
| pct0.03/0.08f15 | band0.05_min10_driftnone | agree | h20 | 224 | 0.5446 | 0.4792 | 0.6086 | 0.1021 | line sweep; lines=267; breakouts=267; mean_line_days=24.6; censored=0 |
| pct0.03/0.08f15 | band0.05_min15_driftnone | agree | h20 | 132 | 0.5455 | 0.4604 | 0.6279 | 0.1692 | line sweep; lines=171; breakouts=171; mean_line_days=30.8; censored=0 |
| pct0.03/0.08f15 | band0.05_min28_drift0.5 | agree | h20 | 14 | 0.1429 | 0.0401 | 0.3994 | 0.9991 | line sweep; lines=19; breakouts=19; mean_line_days=45.8; censored=0 |
| pct0.03/0.08f15 | band0.05_min28_driftnone | agree | h20 | 40 | 0.3750 | 0.2422 | 0.5297 | 0.9597 | line sweep; lines=55; breakouts=55; mean_line_days=46.0; censored=0 |
| pct0.03/0.08f15 | band0.07_min10_drift0.5 | agree | h20 | 60 | 0.4500 | 0.3309 | 0.5751 | 0.8169 | line sweep; lines=67; breakouts=67; mean_line_days=37.8; censored=0 |
| pct0.03/0.08f15 | band0.07_min10_driftnone | agree | h20 | 185 | 0.5459 | 0.4740 | 0.6160 | 0.1197 | line sweep; lines=214; breakouts=213; mean_line_days=34.9; censored=0 |
| pct0.03/0.08f15 | band0.07_min15_drift0.5 | agree | h20 | 51 | 0.3529 | 0.2363 | 0.4901 | 0.9880 | line sweep; lines=57; breakouts=57; mean_line_days=42.7; censored=0 |
| pct0.03/0.08f15 | band0.07_min15_driftnone | agree | h20 | 145 | 0.5103 | 0.4298 | 0.5904 | 0.4341 | line sweep; lines=169; breakouts=168; mean_line_days=40.7; censored=0 |
| pct0.03/0.08f15 | band0.07_min28_drift0.5 | agree | h20 | 26 | 0.3077 | 0.1650 | 0.4999 | 0.9855 | line sweep; lines=28; breakouts=28; mean_line_days=54.6; censored=0 |
| pct0.03/0.08f15 | band0.07_min28_driftnone | agree | h20 | 73 | 0.4247 | 0.3178 | 0.5390 | 0.9201 | line sweep; lines=90; breakouts=90; mean_line_days=54.4; censored=0 |

## Caveats


### Data coverage (verbatim from the decision table, section 5)

- `^DJT` history in `dow.mkt_klines` begins **1992-01-02**. Nothing in this protocol tests Dow Theory on 1897-1991 data; claims about that period default to `insufficient-evidence` per `docs/team_design.md` section 5 unless a long-history source is loaded under a new, hashed protocol.
- `^DJI` 1992-01-02 to 2026-11-06 = 8,775 bars. At the committed spec (8%, 15-session filter) the spec review counted about 82 secondary swings, about 37 reaction legs and **10 primary reversals** on `^DJI` (12 without the filter, 8 at 10%). Hence the pre-run expectation: R2, R3 and probably R8 fall below the evidence floor and receive `insufficient-evidence`; R1, R4, R5 have `n` in the 30-40 range and are decidable but with wide intervals; R6 and R7 counts are unknown before the run. These are expectations, not thresholds; the labels follow section 3 whatever the counts turn out to be.
- Index volume is sparse or zero before 2000 and is a vendor-constructed aggregate afterward; R7 therefore starts 2000-01-03 and its `SP_IYT` robustness uses ETF volume (2004+).
- `^GSPC` and `^IXIC` have `analysis_start` clipping (first real OHLC 1962-07-02 and 1984-10-11); they are not used in any label-driving row. `IYT` begins 2004, so the `SP_IYT` pair covers 2004-2026 only.
- Price indices exclude dividends (R8 caveat). The `^DJI` series is yfinance-sourced; vendor revisions after 2026-11-06 do not change the frozen `period_end` of label-driving runs.
- Forward windows overlap at `h = 60` and `h = 120`; effective sample sizes are smaller than `n`; the number of event clusters is reported next to `n` for every return-based row.
- The primary threshold was selected on this sample (1.8); R4 and R5 labels are therefore computed under the worst-grid-point rule and every R4/R5 report prints the full threshold range.
