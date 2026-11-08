# R7 Volume confirmation (`rule_key: volume_confirmation`)

Pair `SP_IYT` (SPY, IYT), 2004-01-02 to 2026-11-06, 5749 bars. Specification `pct0.03/0.08f15`. Run `a6d2d48e46014e7da3cc7c6be7ce8a02`.
Config hash `e6f5b9cd228e458809a42aa2a5c5e2811175de3d74fafca1a3496c6ac68ae24e`. Decision table sha256 `c8675eff2b281ac6f4fa8ed790063ecaf1e063d78f20fa9569ded1988be39836`. Bootstrap iterations 2000, seed 20261108.

## Event definition

Consecutive secondary legs in a PRIMARY state, 2000-01-03 onward. Metric: share of pairs where the with-trend leg has higher mean volume, null 0.5. Exact binomial.

## Result

| field | value |
|---|---|
| events n | 41 |
| clusters | n/a |
| right-censored | 0 |
| metric | p_vol na |
| estimate | 0.4390 |
| 95% CI | [0.2989, 0.5896] |
| null value | 0.5000 |
| p raw (one-sided, predicted direction) | 0.825556 |
| p used in the Holm family | n/a |
| p Holm (family of 8) | n/a |
| Bonferroni one-sided upper bound (level 0.99375) | 0.6276 |
| sub-sample split | 2015-12-31 (A up to and including, B after) |
| sub-sample A | 0.4545 (n = 22) |
| sub-sample B | 0.4211 (n = 19) |
| sub-sample signs vs null | A- B- |

## Label

- No label: `SP_IYT` is a robustness pair (labels come from `DJ` only).

## Descriptive and robustness rows

| spec | variant | metric | horizon | n | value | CI low | CI high | p raw | notes |
|---|---|---|---|---|---|---|---|---|---|
| pct0.03/0.08f15 | normalised | p_vol | na | 40 | 0.4500 | 0.3071 | 0.6017 | 0.7852 |  |
| pct0.03/0.08f15 | volume_confirms | share_true | na | 51 | 0.3333 | 0.2197 | 0.4703 | 0.9945 |  |
| pct0.03/0.08f15 | sub_A | p_vol | na | 22 | 0.4545 | n/a | n/a | n/a | sub-sample split 2015-12-31 |
| pct0.03/0.08f15 | sub_B | p_vol | na | 19 | 0.4211 | n/a | n/a | n/a | sub-sample split 2015-12-31 |

## Specification sweep (descriptive)

Range of the primary metric over 15 grid points (not a selected optimum): min 0.2759, median 0.4091, max 0.5200.

| spec | variant | metric | horizon | n | value | CI low | CI high | p raw | notes |
|---|---|---|---|---|---|---|---|---|---|
| pct0.03/0.05f0 | primary | p_vol | na | 120 | 0.3000 | 0.2253 | 0.3872 | 1.0000 | sweep |
| pct0.03/0.05f15 | primary | p_vol | na | 101 | 0.2772 | 0.1993 | 0.3715 | 1.0000 | sweep |
| pct0.03/0.06f0 | primary | p_vol | na | 87 | 0.2759 | 0.1929 | 0.3777 | 1.0000 | sweep |
| pct0.03/0.06f15 | primary | p_vol | na | 81 | 0.2840 | 0.1973 | 0.3902 | 1.0000 | sweep |
| pct0.03/0.08f0 | primary | p_vol | na | 44 | 0.4091 | 0.2769 | 0.5559 | 0.9129 | sweep |
| pct0.03/0.1f0 | primary | p_vol | na | 25 | 0.5200 | 0.3350 | 0.6997 | 0.5000 | sweep |
| pct0.03/0.1f15 | primary | p_vol | na | 25 | 0.5200 | 0.3350 | 0.6997 | 0.5000 | sweep |
| pct0.03/0.12f0 | primary | p_vol | na | 19 | 0.4211 | 0.2314 | 0.6372 | 0.8204 | sweep |
| pct0.03/0.12f15 | primary | p_vol | na | 17 | 0.3529 | 0.1731 | 0.5870 | 0.9283 | sweep |
| pct0.02/0.08f15 | primary | p_vol | na | 41 | 0.4390 | 0.2989 | 0.5896 | 0.8256 | sweep |
| pct0.05/0.08f15 | primary | p_vol | na | 41 | 0.4390 | 0.2989 | 0.5896 | 0.8256 | sweep |
| pct0.03/0.08f15 | tol0 | p_vol | na | 41 | 0.4390 | 0.2989 | 0.5896 | 0.8256 | sweep |
| pct0.03/0.08f15 | djt0.12 | p_vol | na | 41 | 0.4390 | 0.2989 | 0.5896 | 0.8256 | sweep |
| atr2.0/14f15 | primary | p_vol | na | 39 | 0.3846 | 0.2489 | 0.5410 | 0.9459 | sweep |
| pivot5 | primary | p_vol | na | 197 | 0.3655 | 0.3014 | 0.4347 | 0.9999 | sweep |

## Caveats


### Data coverage (verbatim from the decision table, section 5)

- `^DJT` history in `dow.mkt_klines` begins **1992-01-02**. Nothing in this protocol tests Dow Theory on 1897-1991 data; claims about that period default to `insufficient-evidence` per `docs/team_design.md` section 5 unless a long-history source is loaded under a new, hashed protocol.
- `^DJI` 1992-01-02 to 2026-11-06 = 8,775 bars. At the committed spec (8%, 15-session filter) the spec review counted about 82 secondary swings, about 37 reaction legs and **10 primary reversals** on `^DJI` (12 without the filter, 8 at 10%). Hence the pre-run expectation: R2, R3 and probably R8 fall below the evidence floor and receive `insufficient-evidence`; R1, R4, R5 have `n` in the 30-40 range and are decidable but with wide intervals; R6 and R7 counts are unknown before the run. These are expectations, not thresholds; the labels follow section 3 whatever the counts turn out to be.
- Index volume is sparse or zero before 2000 and is a vendor-constructed aggregate afterward; R7 therefore starts 2000-01-03 and its `SP_IYT` robustness uses ETF volume (2004+).
- `^GSPC` and `^IXIC` have `analysis_start` clipping (first real OHLC 1962-07-02 and 1984-10-11); they are not used in any label-driving row. `IYT` begins 2004, so the `SP_IYT` pair covers 2004-2026 only.
- Price indices exclude dividends (R8 caveat). The `^DJI` series is yfinance-sourced; vendor revisions after 2026-11-06 do not change the frozen `period_end` of label-driving runs.
- Forward windows overlap at `h = 60` and `h = 120`; effective sample sizes are smaller than `n`; the number of event clusters is reported next to `n` for every return-based row.
- The primary threshold was selected on this sample (1.8); R4 and R5 labels are therefore computed under the worst-grid-point rule and every R4/R5 report prints the full threshold range.
