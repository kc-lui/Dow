# R2 Reversal signal (`rule_key: primary_reversal_signal`)

Pair `SP_IYT` (SPY, IYT), 2004-01-02 to 2026-11-06, 5749 bars. Specification `pct0.03/0.08f15`. Run `a6d2d48e46014e7da3cc7c6be7ce8a02`.
Config hash `e6f5b9cd228e458809a42aa2a5c5e2811175de3d74fafca1a3496c6ac68ae24e`. Decision table sha256 `c8675eff2b281ac6f4fa8ed790063ecaf1e063d78f20fa9569ded1988be39836`. Bootstrap iterations 2000, seed 20261108.

## Event definition

`REVERSAL_UP` / `REVERSAL_DOWN` on `^DJI` at `Signal.idx`. Metric: mean of `sgn * (F_h(c) - mean_t F_h(t))`, `F_h(c) = ln(P[c+1+h] / P[c+1])`, primary h = 60. Random-placement test, cluster-bootstrap CI.

## Result

| field | value |
|---|---|
| events n | 8 |
| clusters | 7 |
| right-censored | 0 |
| metric | mean_excess_logret h60 |
| estimate | 0.0198 |
| 95% CI | [-0.0260, 0.0719] |
| null value | 0.0000 |
| p raw (one-sided, predicted direction) | 0.229885 |
| p used in the Holm family | n/a |
| p Holm (family of 8) | n/a |
| Bonferroni one-sided upper bound (level 0.99375) | 0.0870 |
| sub-sample split | 2015-12-31 (A up to and including, B after) |
| sub-sample A | 0.0323 (n = 4) |
| sub-sample B | 0.0074 (n = 4) |
| sub-sample signs vs null | A? B? |

## Label

- No label: `SP_IYT` is a robustness pair (labels come from `DJ` only).

## Descriptive and robustness rows

| spec | variant | metric | horizon | n | value | CI low | CI high | p raw | notes |
|---|---|---|---|---|---|---|---|---|---|
| pct0.03/0.08f15 | horizon20 | mean_excess_logret | h20 | 8 | -0.0073 | -0.0400 | 0.0253 | 0.6722 |  |
| pct0.03/0.08f15 | horizon120 | mean_excess_logret | h120 | 8 | 0.0650 | -0.0407 | 0.2083 | 0.0615 |  |
| pct0.03/0.08f15 | primary | hit_rate | h60 | 8 | 0.6250 | 0.3057 | 0.8632 | 0.3633 |  |
| pct0.03/0.08f15 | up | mean_excess_logret | h60 | 4 | 0.0337 | -0.0032 | 0.0669 | 0.1709 |  |
| pct0.03/0.08f15 | down | mean_excess_logret | h60 | 4 | 0.0060 | -0.0947 | 0.1067 | 0.4353 |  |
| pct0.03/0.08f15 | djt_side | mean_excess_logret | h60 | 26 | -0.0187 | -0.0645 | 0.0326 | 0.8176 |  |
| pct0.03/0.08f15 | pooled | mean_excess_logret | h60 | 34 | -0.0097 | -0.0460 | 0.0324 | n/a | descriptive; no p-value |
| pct0.03/0.08f15 | sub_A | mean_excess_logret | h60 | 4 | 0.0323 | n/a | n/a | n/a | sub-sample split 2015-12-31 |
| pct0.03/0.08f15 | sub_B | mean_excess_logret | h60 | 4 | 0.0074 | n/a | n/a | n/a | sub-sample split 2015-12-31 |

## Specification sweep (descriptive)

Range of the primary metric over 15 grid points (not a selected optimum): min -0.0272, median 0.0095, max 0.0339.

| spec | variant | metric | horizon | n | value | CI low | CI high | p raw | notes |
|---|---|---|---|---|---|---|---|---|---|
| pct0.03/0.05f0 | primary | mean_excess_logret | h60 | 19 | -0.0016 | -0.0295 | 0.0299 | 0.5462 | sweep |
| pct0.03/0.05f15 | primary | mean_excess_logret | h60 | 15 | 0.0072 | -0.0297 | 0.0405 | 0.3548 | sweep |
| pct0.03/0.06f0 | primary | mean_excess_logret | h60 | 18 | -0.0216 | -0.0721 | 0.0236 | 0.8926 | sweep |
| pct0.03/0.06f15 | primary | mean_excess_logret | h60 | 14 | 0.0095 | -0.0326 | 0.0449 | 0.3088 | sweep |
| pct0.03/0.08f0 | primary | mean_excess_logret | h60 | 12 | -0.0272 | -0.1033 | 0.0437 | 0.8806 | sweep |
| pct0.03/0.1f0 | primary | mean_excess_logret | h60 | 5 | 0.0012 | -0.0573 | 0.0515 | 0.5342 | sweep |
| pct0.03/0.1f15 | primary | mean_excess_logret | h60 | 5 | 0.0012 | -0.0573 | 0.0515 | 0.5342 | sweep |
| pct0.03/0.12f0 | primary | mean_excess_logret | h60 | 5 | 0.0192 | -0.0515 | 0.0792 | 0.2704 | sweep |
| pct0.03/0.12f15 | primary | mean_excess_logret | h60 | 5 | 0.0192 | -0.0515 | 0.0792 | 0.2734 | sweep |
| pct0.02/0.08f15 | primary | mean_excess_logret | h60 | 8 | 0.0198 | -0.0260 | 0.0719 | 0.2299 | sweep |
| pct0.05/0.08f15 | primary | mean_excess_logret | h60 | 8 | 0.0198 | -0.0260 | 0.0719 | 0.2299 | sweep |
| pct0.03/0.08f15 | tol0 | mean_excess_logret | h60 | 8 | 0.0198 | -0.0260 | 0.0719 | 0.2299 | sweep |
| pct0.03/0.08f15 | djt0.12 | mean_excess_logret | h60 | 8 | 0.0198 | -0.0260 | 0.0719 | 0.2299 | sweep |
| atr2.0/14f15 | primary | mean_excess_logret | h60 | 8 | 0.0339 | -0.0131 | 0.0740 | 0.0935 | sweep |
| pivot5 | primary | mean_excess_logret | h60 | 33 | 0.0046 | -0.0114 | 0.0239 | 0.3603 | sweep |

## Caveats


### Data coverage (verbatim from the decision table, section 5)

- `^DJT` history in `dow.mkt_klines` begins **1992-01-02**. Nothing in this protocol tests Dow Theory on 1897-1991 data; claims about that period default to `insufficient-evidence` per `docs/team_design.md` section 5 unless a long-history source is loaded under a new, hashed protocol.
- `^DJI` 1992-01-02 to 2026-11-06 = 8,775 bars. At the committed spec (8%, 15-session filter) the spec review counted about 82 secondary swings, about 37 reaction legs and **10 primary reversals** on `^DJI` (12 without the filter, 8 at 10%). Hence the pre-run expectation: R2, R3 and probably R8 fall below the evidence floor and receive `insufficient-evidence`; R1, R4, R5 have `n` in the 30-40 range and are decidable but with wide intervals; R6 and R7 counts are unknown before the run. These are expectations, not thresholds; the labels follow section 3 whatever the counts turn out to be.
- Index volume is sparse or zero before 2000 and is a vendor-constructed aggregate afterward; R7 therefore starts 2000-01-03 and its `SP_IYT` robustness uses ETF volume (2004+).
- `^GSPC` and `^IXIC` have `analysis_start` clipping (first real OHLC 1962-07-02 and 1984-10-11); they are not used in any label-driving row. `IYT` begins 2004, so the `SP_IYT` pair covers 2004-2026 only.
- Price indices exclude dividends (R8 caveat). The `^DJI` series is yfinance-sourced; vendor revisions after 2026-11-06 do not change the frozen `period_end` of label-driving runs.
- Forward windows overlap at `h = 60` and `h = 120`; effective sample sizes are smaller than `n`; the number of event clusters is reported next to `n` for every return-based row.
- The primary threshold was selected on this sample (1.8); R4 and R5 labels are therefore computed under the worst-grid-point rule and every R4/R5 report prints the full threshold range.
