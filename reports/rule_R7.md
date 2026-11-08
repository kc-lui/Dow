# R7 Volume confirmation (`rule_key: volume_confirmation`)

Pair `DJ` (^DJI, ^DJT), 1992-01-02 to 2026-11-06, 8775 bars. Specification `pct0.03/0.08f15`. Run `a6d2d48e46014e7da3cc7c6be7ce8a02`.
Config hash `e6f5b9cd228e458809a42aa2a5c5e2811175de3d74fafca1a3496c6ac68ae24e`. Decision table sha256 `c8675eff2b281ac6f4fa8ed790063ecaf1e063d78f20fa9569ded1988be39836`. Bootstrap iterations 2000, seed 20261108.

## Event definition

Consecutive secondary legs in a PRIMARY state, 2000-01-03 onward. Metric: share of pairs where the with-trend leg has higher mean volume, null 0.5. Exact binomial.

## Result

| field | value |
|---|---|
| events n | 57 |
| clusters | n/a |
| right-censored | 0 |
| metric | p_vol na |
| estimate | 0.3509 |
| 95% CI | [0.2400, 0.4806] |
| null value | 0.5000 |
| p raw (one-sided, predicted direction) | 0.991826 |
| p used in the Holm family | 0.991826 |
| p Holm (family of 8) | 1.000000 |
| Bonferroni one-sided upper bound (level 0.99375) | 0.5162 |
| sub-sample split | 2009-12-31 (A up to and including, B after) |
| sub-sample A | 0.3600 (n = 25) |
| sub-sample B | 0.3438 (n = 32) |
| sub-sample signs vs null | A- B- |

## Label

- Data label: **insufficient-evidence**. Reason: not significant after Holm, or sub-samples disagree.
- Literature label: **literature-disputed** (registry rows R-037,R-038,R-041).
- Refutation bound actually computed: one-sided 0.99375 upper bound 0.5162 against null 0.5000; it does not lie below the null, so refutation is excluded.

## Descriptive and robustness rows

| spec | variant | metric | horizon | n | value | CI low | CI high | p raw | notes |
|---|---|---|---|---|---|---|---|---|---|
| pct0.03/0.08f15 | normalised | p_vol | na | 57 | 0.4211 | 0.3019 | 0.5502 | 0.9076 |  |
| pct0.03/0.08f15 | volume_confirms | share_true | na | 69 | 0.4058 | 0.2979 | 0.5236 | 0.9544 |  |
| pct0.03/0.08f15 | sub_A | p_vol | na | 25 | 0.3600 | n/a | n/a | n/a | sub-sample split 2009-12-31 |
| pct0.03/0.08f15 | sub_B | p_vol | na | 32 | 0.3438 | n/a | n/a | n/a | sub-sample split 2009-12-31 |

## Specification sweep (descriptive)

Range of the primary metric over 15 grid points (not a selected optimum): min 0.2903, median 0.3509, max 0.4739.

| spec | variant | metric | horizon | n | value | CI low | CI high | p raw | notes |
|---|---|---|---|---|---|---|---|---|---|
| pct0.03/0.05f0 | primary | p_vol | na | 137 | 0.3796 | 0.3026 | 0.4631 | 0.9982 | sweep |
| pct0.03/0.05f15 | primary | p_vol | na | 119 | 0.3950 | 0.3117 | 0.4848 | 0.9916 | sweep |
| pct0.03/0.06f0 | primary | p_vol | na | 102 | 0.3137 | 0.2318 | 0.4091 | 1.0000 | sweep |
| pct0.03/0.06f15 | primary | p_vol | na | 92 | 0.3478 | 0.2584 | 0.4495 | 0.9988 | sweep |
| pct0.03/0.08f0 | primary | p_vol | na | 58 | 0.3448 | 0.2356 | 0.4733 | 0.9940 | sweep |
| pct0.03/0.1f0 | primary | p_vol | na | 31 | 0.2903 | 0.1610 | 0.4659 | 0.9947 | sweep |
| pct0.03/0.1f15 | primary | p_vol | na | 30 | 0.3000 | 0.1666 | 0.4788 | 0.9919 | sweep |
| pct0.03/0.12f0 | primary | p_vol | na | 25 | 0.4000 | 0.2340 | 0.5926 | 0.8852 | sweep |
| pct0.03/0.12f15 | primary | p_vol | na | 25 | 0.4000 | 0.2340 | 0.5926 | 0.8852 | sweep |
| pct0.02/0.08f15 | primary | p_vol | na | 57 | 0.3509 | 0.2400 | 0.4806 | 0.9918 | sweep |
| pct0.05/0.08f15 | primary | p_vol | na | 57 | 0.3509 | 0.2400 | 0.4806 | 0.9918 | sweep |
| pct0.03/0.08f15 | tol0 | p_vol | na | 55 | 0.3273 | 0.2181 | 0.4590 | 0.9968 | sweep |
| pct0.03/0.08f15 | djt0.12 | p_vol | na | 57 | 0.3509 | 0.2400 | 0.4806 | 0.9918 | sweep |
| atr2.0/14f15 | primary | p_vol | na | 60 | 0.4167 | 0.3006 | 0.5427 | 0.9225 | sweep |
| pivot5 | primary | p_vol | na | 230 | 0.4739 | 0.4103 | 0.5383 | 0.8043 | sweep |

## Caveats


### Data coverage (verbatim from the decision table, section 5)

- `^DJT` history in `dow.mkt_klines` begins **1992-01-02**. Nothing in this protocol tests Dow Theory on 1897-1991 data; claims about that period default to `insufficient-evidence` per `docs/team_design.md` section 5 unless a long-history source is loaded under a new, hashed protocol.
- `^DJI` 1992-01-02 to 2026-11-06 = 8,775 bars. At the committed spec (8%, 15-session filter) the spec review counted about 82 secondary swings, about 37 reaction legs and **10 primary reversals** on `^DJI` (12 without the filter, 8 at 10%). Hence the pre-run expectation: R2, R3 and probably R8 fall below the evidence floor and receive `insufficient-evidence`; R1, R4, R5 have `n` in the 30-40 range and are decidable but with wide intervals; R6 and R7 counts are unknown before the run. These are expectations, not thresholds; the labels follow section 3 whatever the counts turn out to be.
- Index volume is sparse or zero before 2000 and is a vendor-constructed aggregate afterward; R7 therefore starts 2000-01-03 and its `SP_IYT` robustness uses ETF volume (2004+).
- `^GSPC` and `^IXIC` have `analysis_start` clipping (first real OHLC 1962-07-02 and 1984-10-11); they are not used in any label-driving row. `IYT` begins 2004, so the `SP_IYT` pair covers 2004-2026 only.
- Price indices exclude dividends (R8 caveat). The `^DJI` series is yfinance-sourced; vendor revisions after 2026-11-06 do not change the frozen `period_end` of label-driving runs.
- Forward windows overlap at `h = 60` and `h = 120`; effective sample sizes are smaller than `n`; the number of event clusters is reported next to `n` for every return-based row.
- The primary threshold was selected on this sample (1.8); R4 and R5 labels are therefore computed under the worst-grid-point rule and every R4/R5 report prints the full threshold range.
