# R1 Trend persistence (`rule_key: trend_persistence`)

Pair `SP_IYT` (SPY, IYT), 2004-01-02 to 2026-11-06, 5749 bars. Specification `pct0.03/0.08f15`. Run `a6d2d48e46014e7da3cc7c6be7ce8a02`.
Config hash `e6f5b9cd228e458809a42aa2a5c5e2811175de3d74fafca1a3496c6ac68ae24e`. Decision table sha256 `c8675eff2b281ac6f4fa8ed790063ecaf1e063d78f20fa9569ded1988be39836`. Bootstrap iterations 2000, seed 20261108.

## Event definition

Confirmed secondary swing counter to an established primary trend (`state(c)` BULL_PRIMARY with an L swing, BEAR_PRIMARY with an H swing). Success: the next secondary swing makes a new extreme (HH / LL) beyond `equal_extreme_tol`. Metric `p_extend`, null 0.5, exact binomial, Wilson CI.

## Result

| field | value |
|---|---|
| events n | 20 |
| clusters | n/a |
| right-censored | 1 |
| metric | p_extend na |
| estimate | 0.8000 |
| 95% CI | [0.5840, 0.9193] |
| null value | 0.5000 |
| p raw (one-sided, predicted direction) | 0.005909 |
| p used in the Holm family | n/a |
| p Holm (family of 8) | n/a |
| Bonferroni one-sided upper bound (level 0.99375) | 0.9363 |
| sub-sample split | 2015-12-31 (A up to and including, B after) |
| sub-sample A | 0.7500 (n = 12) |
| sub-sample B | 0.8750 (n = 8) |
| sub-sample signs vs null | A+ B? |

## Label

- No label: `SP_IYT` is a robustness pair (labels come from `DJ` only).

## Descriptive and robustness rows

| spec | variant | metric | horizon | n | value | CI low | CI high | p raw | notes |
|---|---|---|---|---|---|---|---|---|---|
| pct0.03/0.08f15 | bull | p_extend | na | 12 | 0.7500 | 0.4677 | 0.9111 | 0.0730 |  |
| pct0.03/0.08f15 | bear | p_extend | na | 8 | 0.8750 | 0.5291 | 0.9776 | 0.0352 |  |
| pct0.03/0.08f15 | p_sim | p_extend | na | 20 | 0.8000 | n/a | n/a | 0.1314 | drift-matched null mean=0.6866 |
| pct0.03/0.08f15 | sub_A | p_extend | na | 12 | 0.7500 | n/a | n/a | n/a | sub-sample split 2015-12-31 |
| pct0.03/0.08f15 | sub_B | p_extend | na | 8 | 0.8750 | n/a | n/a | n/a | sub-sample split 2015-12-31 |

## Specification sweep (descriptive)

Range of the primary metric over 15 grid points (not a selected optimum): min 0.6735, median 0.7895, max 0.8182.

| spec | variant | metric | horizon | n | value | CI low | CI high | p raw | notes |
|---|---|---|---|---|---|---|---|---|---|
| pct0.03/0.05f0 | primary | p_extend | na | 58 | 0.7241 | 0.5980 | 0.8225 | 0.0004 | sweep; censored=0; equal_not_extended=2 |
| pct0.03/0.05f15 | primary | p_extend | na | 47 | 0.7872 | 0.6510 | 0.8801 | 0.0000 | sweep; censored=0; equal_not_extended=0 |
| pct0.03/0.06f0 | primary | p_extend | na | 41 | 0.7317 | 0.5807 | 0.8431 | 0.0022 | sweep; censored=1; equal_not_extended=1 |
| pct0.03/0.06f15 | primary | p_extend | na | 38 | 0.7895 | 0.6365 | 0.8893 | 0.0002 | sweep; censored=1; equal_not_extended=0 |
| pct0.03/0.08f0 | primary | p_extend | na | 22 | 0.7273 | 0.5185 | 0.8685 | 0.0262 | sweep; censored=1; equal_not_extended=0 |
| pct0.03/0.1f0 | primary | p_extend | na | 11 | 0.8182 | 0.5230 | 0.9486 | 0.0327 | sweep; censored=1; equal_not_extended=0 |
| pct0.03/0.1f15 | primary | p_extend | na | 11 | 0.8182 | 0.5230 | 0.9486 | 0.0327 | sweep; censored=1; equal_not_extended=0 |
| pct0.03/0.12f0 | primary | p_extend | na | 9 | 0.7778 | 0.4526 | 0.9368 | 0.0898 | sweep; censored=1; equal_not_extended=0 |
| pct0.03/0.12f15 | primary | p_extend | na | 8 | 0.7500 | 0.4093 | 0.9285 | 0.1445 | sweep; censored=1; equal_not_extended=0 |
| pct0.02/0.08f15 | primary | p_extend | na | 20 | 0.8000 | 0.5840 | 0.9193 | 0.0059 | sweep; censored=1; equal_not_extended=0 |
| pct0.05/0.08f15 | primary | p_extend | na | 20 | 0.8000 | 0.5840 | 0.9193 | 0.0059 | sweep; censored=1; equal_not_extended=0 |
| pct0.03/0.08f15 | tol0 | p_extend | na | 20 | 0.8000 | 0.5840 | 0.9193 | 0.0059 | sweep; censored=1; equal_not_extended=0 |
| pct0.03/0.08f15 | djt0.12 | p_extend | na | 20 | 0.8000 | 0.5840 | 0.9193 | 0.0059 | sweep; censored=1; equal_not_extended=0 |
| atr2.0/14f15 | primary | p_extend | na | 19 | 0.7895 | 0.5667 | 0.9149 | 0.0096 | sweep; censored=1; equal_not_extended=0 |
| pivot5 | primary | p_extend | na | 98 | 0.6735 | 0.5756 | 0.7582 | 0.0004 | sweep; censored=0; equal_not_extended=20 |

Drift-matched random-walk null: p_sim = 0.1314 over 2000 paths (null mean p_extend 0.6866).

## Caveats


### Data coverage (verbatim from the decision table, section 5)

- `^DJT` history in `dow.mkt_klines` begins **1992-01-02**. Nothing in this protocol tests Dow Theory on 1897-1991 data; claims about that period default to `insufficient-evidence` per `docs/team_design.md` section 5 unless a long-history source is loaded under a new, hashed protocol.
- `^DJI` 1992-01-02 to 2026-11-06 = 8,775 bars. At the committed spec (8%, 15-session filter) the spec review counted about 82 secondary swings, about 37 reaction legs and **10 primary reversals** on `^DJI` (12 without the filter, 8 at 10%). Hence the pre-run expectation: R2, R3 and probably R8 fall below the evidence floor and receive `insufficient-evidence`; R1, R4, R5 have `n` in the 30-40 range and are decidable but with wide intervals; R6 and R7 counts are unknown before the run. These are expectations, not thresholds; the labels follow section 3 whatever the counts turn out to be.
- Index volume is sparse or zero before 2000 and is a vendor-constructed aggregate afterward; R7 therefore starts 2000-01-03 and its `SP_IYT` robustness uses ETF volume (2004+).
- `^GSPC` and `^IXIC` have `analysis_start` clipping (first real OHLC 1962-07-02 and 1984-10-11); they are not used in any label-driving row. `IYT` begins 2004, so the `SP_IYT` pair covers 2004-2026 only.
- Price indices exclude dividends (R8 caveat). The `^DJI` series is yfinance-sourced; vendor revisions after 2026-11-06 do not change the frozen `period_end` of label-driving runs.
- Forward windows overlap at `h = 60` and `h = 120`; effective sample sizes are smaller than `n`; the number of event clusters is reported next to `n` for every return-based row.
- The primary threshold was selected on this sample (1.8); R4 and R5 labels are therefore computed under the worst-grid-point rule and every R4/R5 report prints the full threshold range.
