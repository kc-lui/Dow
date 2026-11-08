# R2 Reversal signal (`rule_key: primary_reversal_signal`)

Pair `DJ` (^DJI, ^DJT), 1992-01-02 to 2026-11-06, 8775 bars. Specification `pct0.03/0.08f15`. Run `a6d2d48e46014e7da3cc7c6be7ce8a02`.
Config hash `e6f5b9cd228e458809a42aa2a5c5e2811175de3d74fafca1a3496c6ac68ae24e`. Decision table sha256 `c8675eff2b281ac6f4fa8ed790063ecaf1e063d78f20fa9569ded1988be39836`. Bootstrap iterations 2000, seed 20261108.

## Event definition

`REVERSAL_UP` / `REVERSAL_DOWN` on `^DJI` at `Signal.idx`. Metric: mean of `sgn * (F_h(c) - mean_t F_h(t))`, `F_h(c) = ln(P[c+1+h] / P[c+1])`, primary h = 60. Random-placement test, cluster-bootstrap CI.

## Result

| field | value |
|---|---|
| events n | 12 |
| clusters | 10 |
| right-censored | 0 |
| metric | mean_excess_logret h60 |
| estimate | -0.0151 |
| 95% CI | [-0.0456, 0.0206] |
| null value | 0.0000 |
| p raw (one-sided, predicted direction) | 0.773613 |
| p used in the Holm family | 1.000000 |
| p Holm (family of 8) | 1.000000 |
| Bonferroni one-sided upper bound (level 0.99375) | 0.0343 |
| sub-sample split | 2009-12-31 (A up to and including, B after) |
| sub-sample A | 0.0433 (n = 3) |
| sub-sample B | -0.0346 (n = 9) |
| sub-sample signs vs null | A? B? |

## Label

- Data label: **insufficient-evidence**. Reason: n below minimum.
- Literature label: **literature-disputed** (registry rows R-018,R-020).
- Refutation bound actually computed: one-sided 0.99375 upper bound 0.0343 against null 0.0000; it does not lie below the null, so refutation is excluded.

## Descriptive and robustness rows

| spec | variant | metric | horizon | n | value | CI low | CI high | p raw | notes |
|---|---|---|---|---|---|---|---|---|---|
| pct0.03/0.08f15 | horizon20 | mean_excess_logret | h20 | 12 | -0.0205 | -0.0399 | -0.0015 | 0.9545 |  |
| pct0.03/0.08f15 | horizon120 | mean_excess_logret | h120 | 12 | 0.0179 | -0.0415 | 0.1150 | 0.2479 |  |
| pct0.03/0.08f15 | primary | hit_rate | h60 | 12 | 0.5000 | 0.2538 | 0.7462 | 0.6128 |  |
| pct0.03/0.08f15 | up | mean_excess_logret | h60 | 6 | 0.0039 | -0.0219 | 0.0244 | 0.4698 |  |
| pct0.03/0.08f15 | down | mean_excess_logret | h60 | 6 | -0.0341 | -0.0916 | 0.0395 | 0.8786 |  |
| pct0.03/0.08f15 | djt_side | mean_excess_logret | h60 | 29 | 0.0015 | -0.0457 | 0.0524 | 0.4763 |  |
| pct0.03/0.08f15 | pooled | mean_excess_logret | h60 | 41 | -0.0033 | -0.0365 | 0.0336 | n/a | descriptive; no p-value |
| pct0.03/0.08f15 | sub_A | mean_excess_logret | h60 | 3 | 0.0433 | n/a | n/a | n/a | sub-sample split 2009-12-31 |
| pct0.03/0.08f15 | sub_B | mean_excess_logret | h60 | 9 | -0.0346 | n/a | n/a | n/a | sub-sample split 2009-12-31 |

## Specification sweep (descriptive)

Range of the primary metric over 15 grid points (not a selected optimum): min -0.0214, median -0.0151, max 0.0002.

| spec | variant | metric | horizon | n | value | CI low | CI high | p raw | notes |
|---|---|---|---|---|---|---|---|---|---|
| pct0.03/0.05f0 | primary | mean_excess_logret | h60 | 36 | -0.0141 | -0.0348 | 0.0079 | 0.8816 | sweep |
| pct0.03/0.05f15 | primary | mean_excess_logret | h60 | 34 | -0.0090 | -0.0267 | 0.0125 | 0.7731 | sweep |
| pct0.03/0.06f0 | primary | mean_excess_logret | h60 | 34 | -0.0198 | -0.0451 | 0.0023 | 0.9440 | sweep |
| pct0.03/0.06f15 | primary | mean_excess_logret | h60 | 30 | -0.0164 | -0.0372 | 0.0051 | 0.9020 | sweep |
| pct0.03/0.08f0 | primary | mean_excess_logret | h60 | 12 | -0.0186 | -0.0542 | 0.0194 | 0.8211 | sweep |
| pct0.03/0.1f0 | primary | mean_excess_logret | h60 | 8 | -0.0090 | -0.0451 | 0.0300 | 0.6362 | sweep |
| pct0.03/0.1f15 | primary | mean_excess_logret | h60 | 8 | -0.0090 | -0.0451 | 0.0300 | 0.6362 | sweep |
| pct0.03/0.12f0 | primary | mean_excess_logret | h60 | 8 | -0.0195 | -0.0594 | 0.0184 | 0.7861 | sweep |
| pct0.03/0.12f15 | primary | mean_excess_logret | h60 | 8 | -0.0195 | -0.0594 | 0.0184 | 0.7861 | sweep |
| pct0.02/0.08f15 | primary | mean_excess_logret | h60 | 12 | -0.0151 | -0.0456 | 0.0206 | 0.7736 | sweep |
| pct0.05/0.08f15 | primary | mean_excess_logret | h60 | 12 | -0.0151 | -0.0456 | 0.0206 | 0.7736 | sweep |
| pct0.03/0.08f15 | tol0 | mean_excess_logret | h60 | 12 | -0.0214 | -0.0545 | 0.0163 | 0.8516 | sweep |
| pct0.03/0.08f15 | djt0.12 | mean_excess_logret | h60 | 12 | -0.0151 | -0.0456 | 0.0206 | 0.7736 | sweep |
| atr2.0/14f15 | primary | mean_excess_logret | h60 | 15 | 0.0002 | -0.0171 | 0.0186 | 0.4963 | sweep |
| pivot5 | primary | mean_excess_logret | h60 | 64 | -0.0150 | -0.0272 | -0.0026 | 0.9600 | sweep |

## Caveats


### Data coverage (verbatim from the decision table, section 5)

- `^DJT` history in `dow.mkt_klines` begins **1992-01-02**. Nothing in this protocol tests Dow Theory on 1897-1991 data; claims about that period default to `insufficient-evidence` per `docs/team_design.md` section 5 unless a long-history source is loaded under a new, hashed protocol.
- `^DJI` 1992-01-02 to 2026-11-06 = 8,775 bars. At the committed spec (8%, 15-session filter) the spec review counted about 82 secondary swings, about 37 reaction legs and **10 primary reversals** on `^DJI` (12 without the filter, 8 at 10%). Hence the pre-run expectation: R2, R3 and probably R8 fall below the evidence floor and receive `insufficient-evidence`; R1, R4, R5 have `n` in the 30-40 range and are decidable but with wide intervals; R6 and R7 counts are unknown before the run. These are expectations, not thresholds; the labels follow section 3 whatever the counts turn out to be.
- Index volume is sparse or zero before 2000 and is a vendor-constructed aggregate afterward; R7 therefore starts 2000-01-03 and its `SP_IYT` robustness uses ETF volume (2004+).
- `^GSPC` and `^IXIC` have `analysis_start` clipping (first real OHLC 1962-07-02 and 1984-10-11); they are not used in any label-driving row. `IYT` begins 2004, so the `SP_IYT` pair covers 2004-2026 only.
- Price indices exclude dividends (R8 caveat). The `^DJI` series is yfinance-sourced; vendor revisions after 2026-11-06 do not change the frozen `period_end` of label-driving runs.
- Forward windows overlap at `h = 60` and `h = 120`; effective sample sizes are smaller than `n`; the number of event clusters is reported next to `n` for every return-based row.
- The primary threshold was selected on this sample (1.8); R4 and R5 labels are therefore computed under the worst-grid-point rule and every R4/R5 report prints the full threshold range.
