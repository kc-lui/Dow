# R8 Hamilton-style timing strategy (`rule_key: hamilton_timing`)

Pair `SP_IYT` (SPY, IYT), 2004-01-02 to 2026-11-06, 5749 bars. Specification `pct0.03/0.08f15`. Run `a6d2d48e46014e7da3cc7c6be7ce8a02`.
Config hash `e6f5b9cd228e458809a42aa2a5c5e2811175de3d74fafca1a3496c6ac68ae24e`. Decision table sha256 `c8675eff2b281ac6f4fa8ed790063ecaf1e063d78f20fa9569ded1988be39836`. Bootstrap iterations 2000, seed 20261108.

## Event definition

Long when `^DJI` is BULL_PRIMARY and the pair is confirmed, else cash; executed one bar after the signal, 10 bps per side. Metric: Sharpe(strategy) - Sharpe(buy-and-hold) of daily log returns; null 0. Joint stationary block bootstrap (block 20).

## Result

| field | value |
|---|---|
| events n | 15 |
| clusters | n/a |
| right-censored | 0 |
| metric | delta_sharpe na |
| estimate | 0.0168 |
| 95% CI | [-0.4333, 0.4592] |
| null value | 0.0000 |
| p raw (one-sided, predicted direction) | 0.488256 |
| p used in the Holm family | n/a |
| p Holm (family of 8) | n/a |
| Bonferroni one-sided upper bound (level 0.99375) | 0.6196 |
| sub-sample split | 2015-12-31 (A up to and including, B after) |
| sub-sample A | 0.1694 (n = 6) |
| sub-sample B | -0.1658 (n = 9) |
| sub-sample signs vs null | A? B? |

## Label

- No label: `SP_IYT` is a robustness pair (labels come from `DJ` only).

## Descriptive and robustness rows

| spec | variant | metric | horizon | n | value | CI low | CI high | p raw | notes |
|---|---|---|---|---|---|---|---|---|---|
| pct0.03/0.08f15 | cost0 | delta_sharpe | na | 15 | 0.0264 | -0.4225 | 0.4693 | 0.4758 | trades=15 |
| pct0.03/0.08f15 | short | delta_sharpe | na | 25 | -0.1975 | -0.7076 | 0.2949 | 0.7821 | trades=25 |
| pct0.03/0.08f15 | p_spell | delta_sharpe | na | 15 | 0.0168 | n/a | n/a | 0.1154 | random-spell null |
| pct0.03/0.08f15 | calls | share_right | na | 13 | 0.6154 | 0.3552 | 0.8229 | 0.5811 | right=8; wrong=5; descriptive |
| pct0.03/0.08f15 | sub_A | delta_sharpe | na | 6 | 0.1694 | n/a | n/a | n/a | sub-sample split 2015-12-31 |
| pct0.03/0.08f15 | sub_B | delta_sharpe | na | 9 | -0.1658 | n/a | n/a | n/a | sub-sample split 2015-12-31 |

## Specification sweep (descriptive)

Range of the primary metric over 15 grid points (not a selected optimum): min -0.2678, median -0.1064, max 0.0168.

| spec | variant | metric | horizon | n | value | CI low | CI high | p raw | notes |
|---|---|---|---|---|---|---|---|---|---|
| pct0.03/0.05f0 | primary | delta_sharpe | na | 46 | -0.1343 | -0.5262 | 0.2482 | 0.7491 | sweep; trades=46 |
| pct0.03/0.05f15 | primary | delta_sharpe | na | 34 | -0.1208 | -0.5272 | 0.2843 | 0.7256 | sweep; trades=34 |
| pct0.03/0.06f0 | primary | delta_sharpe | na | 33 | -0.1442 | -0.5304 | 0.2256 | 0.7796 | sweep; trades=33 |
| pct0.03/0.06f15 | primary | delta_sharpe | na | 31 | -0.0427 | -0.4247 | 0.3279 | 0.5967 | sweep; trades=31 |
| pct0.03/0.08f0 | primary | delta_sharpe | na | 17 | -0.0694 | -0.5171 | 0.3726 | 0.6297 | sweep; trades=17 |
| pct0.03/0.1f0 | primary | delta_sharpe | na | 9 | -0.2273 | -0.6911 | 0.2411 | 0.8341 | sweep; trades=9 |
| pct0.03/0.1f15 | primary | delta_sharpe | na | 9 | -0.2273 | -0.6911 | 0.2411 | 0.8341 | sweep; trades=9 |
| pct0.03/0.12f0 | primary | delta_sharpe | na | 9 | -0.0200 | -0.4199 | 0.4374 | 0.5497 | sweep; trades=9 |
| pct0.03/0.12f15 | primary | delta_sharpe | na | 9 | -0.0200 | -0.4199 | 0.4374 | 0.5497 | sweep; trades=9 |
| pct0.02/0.08f15 | primary | delta_sharpe | na | 15 | 0.0168 | -0.4333 | 0.4592 | 0.4883 | sweep; trades=15 |
| pct0.05/0.08f15 | primary | delta_sharpe | na | 15 | 0.0168 | -0.4333 | 0.4592 | 0.4883 | sweep; trades=15 |
| pct0.03/0.08f15 | tol0 | delta_sharpe | na | 15 | -0.0284 | -0.4802 | 0.4284 | 0.5577 | sweep; trades=15 |
| pct0.03/0.08f15 | djt0.12 | delta_sharpe | na | 13 | -0.1064 | -0.4906 | 0.3122 | 0.7051 | sweep; trades=13 |
| atr2.0/14f15 | primary | delta_sharpe | na | 19 | -0.1306 | -0.5493 | 0.2754 | 0.7516 | sweep; trades=19 |
| pivot5 | primary | delta_sharpe | na | 78 | -0.2678 | -0.6975 | 0.1552 | 0.8941 | sweep; trades=78 |

### Strategy against buy-and-hold (10 bps, long/cash)

| | strategy | buy-and-hold |
|---|---|---|
| Sharpe | 0.4579 | 0.4411 |
| annual return (log) | 0.0315 | 0.0823 |
| annual volatility | 0.0689 | 0.1866 |
| max drawdown | -0.2010 | -0.5647 |

Time in market 0.2736; trades 15; cumulative log-return difference -1.1579 (CI -2.4085 to 0.1943, p 0.954023). Price indices exclude dividends, which favours a strategy that is partly in cash.
Random-spell null p_spell = 0.1154.
Calls (descriptive, no label): {'right': 8, 'wrong': 5, 'n_calls': 13}.

## Caveats

- The 1992-2026 DJI/DJT sample cannot replicate Brown, Goetzmann and Kumar's 1902-1929 reconstruction of Hamilton's 255 editorials (110 right, 74 wrong, 71 neutral). Our calls are produced by a mechanical state machine, not by Hamilton's judgement, on a different century of data. Any comparison with 110/74 is descriptive and carries no label.

### Data coverage (verbatim from the decision table, section 5)

- `^DJT` history in `dow.mkt_klines` begins **1992-01-02**. Nothing in this protocol tests Dow Theory on 1897-1991 data; claims about that period default to `insufficient-evidence` per `docs/team_design.md` section 5 unless a long-history source is loaded under a new, hashed protocol.
- `^DJI` 1992-01-02 to 2026-11-06 = 8,775 bars. At the committed spec (8%, 15-session filter) the spec review counted about 82 secondary swings, about 37 reaction legs and **10 primary reversals** on `^DJI` (12 without the filter, 8 at 10%). Hence the pre-run expectation: R2, R3 and probably R8 fall below the evidence floor and receive `insufficient-evidence`; R1, R4, R5 have `n` in the 30-40 range and are decidable but with wide intervals; R6 and R7 counts are unknown before the run. These are expectations, not thresholds; the labels follow section 3 whatever the counts turn out to be.
- Index volume is sparse or zero before 2000 and is a vendor-constructed aggregate afterward; R7 therefore starts 2000-01-03 and its `SP_IYT` robustness uses ETF volume (2004+).
- `^GSPC` and `^IXIC` have `analysis_start` clipping (first real OHLC 1962-07-02 and 1984-10-11); they are not used in any label-driving row. `IYT` begins 2004, so the `SP_IYT` pair covers 2004-2026 only.
- Price indices exclude dividends (R8 caveat). The `^DJI` series is yfinance-sourced; vendor revisions after 2026-11-06 do not change the frozen `period_end` of label-driving runs.
- Forward windows overlap at `h = 60` and `h = 120`; effective sample sizes are smaller than `n`; the number of event clusters is reported next to `n` for every return-based row.
- The primary threshold was selected on this sample (1.8); R4 and R5 labels are therefore computed under the worst-grid-point rule and every R4/R5 report prints the full threshold range.

Correction (R11 audit): `^DJI` volume is positive on every bar since 1992. What exists is a level break (annual mean 21 to 99 million shares in 1992-1999 against about 205 million in 2000) and a second break in 2016/2017 (about 117 against 311 million), which lies inside R7's sample. The 2000 start stays as pre-registered; only the normalised variant partly handles the 2016/2017 break.
