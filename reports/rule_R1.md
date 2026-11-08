# R1 Trend persistence (`rule_key: trend_persistence`)

Pair `DJ` (^DJI, ^DJT), 1992-01-02 to 2026-11-06, 8775 bars. Specification `pct0.03/0.08f15`. Run `a6d2d48e46014e7da3cc7c6be7ce8a02`.
Config hash `e6f5b9cd228e458809a42aa2a5c5e2811175de3d74fafca1a3496c6ac68ae24e`. Decision table sha256 `c8675eff2b281ac6f4fa8ed790063ecaf1e063d78f20fa9569ded1988be39836`. Bootstrap iterations 2000, seed 20261108.

## Event definition

Confirmed secondary swing counter to an established primary trend (`state(c)` BULL_PRIMARY with an L swing, BEAR_PRIMARY with an H swing). Success: the next secondary swing makes a new extreme (HH / LL) beyond `equal_extreme_tol`. Metric `p_extend`, null 0.5, exact binomial, Wilson CI.

## Result

| field | value |
|---|---|
| events n | 33 |
| clusters | n/a |
| right-censored | 1 |
| metric | p_extend na |
| estimate | 0.8788 |
| 95% CI | [0.7267, 0.9518] |
| null value | 0.5000 |
| p raw (one-sided, predicted direction) | 0.000005 |
| p used in the Holm family | 0.000005 |
| p Holm (family of 8) | 0.000044 |
| Bonferroni one-sided upper bound (level 0.99375) | 0.9620 |
| sub-sample split | 2009-12-31 (A up to and including, B after) |
| sub-sample A | 0.9412 (n = 17) |
| sub-sample B | 0.8125 (n = 16) |
| sub-sample signs vs null | A+ B+ |

## Label

- Data label: **data-confirmed**. Reason: p_holm<alpha, sub-samples agree.
- Literature label: **literature-consensus** (registry rows R-016,R-017).
- Refutation bound actually computed: one-sided 0.99375 upper bound 0.9620 against null 0.5000; it does not lie below the null, so refutation is excluded.

## Descriptive and robustness rows

| spec | variant | metric | horizon | n | value | CI low | CI high | p raw | notes |
|---|---|---|---|---|---|---|---|---|---|
| pct0.03/0.08f15 | bull | p_extend | na | 21 | 0.8571 | 0.6536 | 0.9502 | 0.0007 |  |
| pct0.03/0.08f15 | bear | p_extend | na | 12 | 0.9167 | 0.6461 | 0.9851 | 0.0032 |  |
| pct0.03/0.08f15 | p_sim | p_extend | na | 33 | 0.8788 | n/a | n/a | 0.0055 | drift-matched null mean=0.6906 |
| pct0.03/0.08f15 | sub_A | p_extend | na | 17 | 0.9412 | n/a | n/a | n/a | sub-sample split 2009-12-31 |
| pct0.03/0.08f15 | sub_B | p_extend | na | 16 | 0.8125 | n/a | n/a | n/a | sub-sample split 2009-12-31 |

## Specification sweep (descriptive)

Range of the primary metric over 15 grid points (not a selected optimum): min 0.5935, median 0.7606, max 0.8788.

| spec | variant | metric | horizon | n | value | CI low | CI high | p raw | notes |
|---|---|---|---|---|---|---|---|---|---|
| pct0.03/0.05f0 | primary | p_extend | na | 80 | 0.7250 | 0.6186 | 0.8108 | 0.0000 | sweep; censored=0; equal_not_extended=2 |
| pct0.03/0.05f15 | primary | p_extend | na | 71 | 0.7606 | 0.6496 | 0.8448 | 0.0000 | sweep; censored=0; equal_not_extended=2 |
| pct0.03/0.06f0 | primary | p_extend | na | 61 | 0.7377 | 0.6156 | 0.8316 | 0.0001 | sweep; censored=0; equal_not_extended=1 |
| pct0.03/0.06f15 | primary | p_extend | na | 56 | 0.7857 | 0.6618 | 0.8729 | 0.0000 | sweep; censored=0; equal_not_extended=1 |
| pct0.03/0.08f0 | primary | p_extend | na | 33 | 0.8485 | 0.6908 | 0.9335 | 0.0000 | sweep; censored=1; equal_not_extended=0 |
| pct0.03/0.1f0 | primary | p_extend | na | 15 | 0.7333 | 0.4805 | 0.8910 | 0.0592 | sweep; censored=1; equal_not_extended=0 |
| pct0.03/0.1f15 | primary | p_extend | na | 15 | 0.7333 | 0.4805 | 0.8910 | 0.0592 | sweep; censored=1; equal_not_extended=0 |
| pct0.03/0.12f0 | primary | p_extend | na | 13 | 0.6154 | 0.3552 | 0.8229 | 0.2905 | sweep; censored=1; equal_not_extended=0 |
| pct0.03/0.12f15 | primary | p_extend | na | 13 | 0.6154 | 0.3552 | 0.8229 | 0.2905 | sweep; censored=1; equal_not_extended=0 |
| pct0.02/0.08f15 | primary | p_extend | na | 33 | 0.8788 | 0.7267 | 0.9518 | 0.0000 | sweep; censored=1; equal_not_extended=0 |
| pct0.05/0.08f15 | primary | p_extend | na | 33 | 0.8788 | 0.7267 | 0.9518 | 0.0000 | sweep; censored=1; equal_not_extended=0 |
| pct0.03/0.08f15 | tol0 | p_extend | na | 32 | 0.8750 | 0.7193 | 0.9503 | 0.0000 | sweep; censored=1; equal_not_extended=0 |
| pct0.03/0.08f15 | djt0.12 | p_extend | na | 33 | 0.8788 | 0.7267 | 0.9518 | 0.0000 | sweep; censored=1; equal_not_extended=0 |
| atr2.0/14f15 | primary | p_extend | na | 35 | 0.7714 | 0.6098 | 0.8793 | 0.0009 | sweep; censored=0; equal_not_extended=2 |
| pivot5 | primary | p_extend | na | 155 | 0.5935 | 0.5149 | 0.6677 | 0.0121 | sweep; censored=0; equal_not_extended=31 |

Drift-matched random-walk null: p_sim = 0.0055 over 2000 paths (null mean p_extend 0.6906).

## Caveats


### Data coverage (verbatim from the decision table, section 5)

- `^DJT` history in `dow.mkt_klines` begins **1992-01-02**. Nothing in this protocol tests Dow Theory on 1897-1991 data; claims about that period default to `insufficient-evidence` per `docs/team_design.md` section 5 unless a long-history source is loaded under a new, hashed protocol.
- `^DJI` 1992-01-02 to 2026-11-06 = 8,775 bars. At the committed spec (8%, 15-session filter) the spec review counted about 82 secondary swings, about 37 reaction legs and **10 primary reversals** on `^DJI` (12 without the filter, 8 at 10%). Hence the pre-run expectation: R2, R3 and probably R8 fall below the evidence floor and receive `insufficient-evidence`; R1, R4, R5 have `n` in the 30-40 range and are decidable but with wide intervals; R6 and R7 counts are unknown before the run. These are expectations, not thresholds; the labels follow section 3 whatever the counts turn out to be.
- Index volume is sparse or zero before 2000 and is a vendor-constructed aggregate afterward; R7 therefore starts 2000-01-03 and its `SP_IYT` robustness uses ETF volume (2004+).
- `^GSPC` and `^IXIC` have `analysis_start` clipping (first real OHLC 1962-07-02 and 1984-10-11); they are not used in any label-driving row. `IYT` begins 2004, so the `SP_IYT` pair covers 2004-2026 only.
- Price indices exclude dividends (R8 caveat). The `^DJI` series is yfinance-sourced; vendor revisions after 2026-11-06 do not change the frozen `period_end` of label-driving runs.
- Forward windows overlap at `h = 60` and `h = 120`; effective sample sizes are smaller than `n`; the number of event clusters is reported next to `n` for every return-based row.
- The primary threshold was selected on this sample (1.8); R4 and R5 labels are therefore computed under the worst-grid-point rule and every R4/R5 report prints the full threshold range.
