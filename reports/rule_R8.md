# R8 Hamilton-style timing strategy (`rule_key: hamilton_timing`)

Pair `DJ` (^DJI, ^DJT), 1992-01-02 to 2026-11-06, 8775 bars. Specification `pct0.03/0.08f15`. Run `a6d2d48e46014e7da3cc7c6be7ce8a02`.
Config hash `e6f5b9cd228e458809a42aa2a5c5e2811175de3d74fafca1a3496c6ac68ae24e`. Decision table sha256 `c8675eff2b281ac6f4fa8ed790063ecaf1e063d78f20fa9569ded1988be39836`. Bootstrap iterations 2000, seed 20261108.

## Event definition

Long when `^DJI` is BULL_PRIMARY and the pair is confirmed, else cash; executed one bar after the signal, 10 bps per side. Metric: Sharpe(strategy) - Sharpe(buy-and-hold) of daily log returns; null 0. Joint stationary block bootstrap (block 20).

## Result

| field | value |
|---|---|
| events n | 28 |
| clusters | n/a |
| right-censored | 0 |
| metric | delta_sharpe na |
| estimate | 0.1099 |
| 95% CI | [-0.1827, 0.4336] |
| null value | 0.0000 |
| p raw (one-sided, predicted direction) | 0.246377 |
| p used in the Holm family | 1.000000 |
| p Holm (family of 8) | 1.000000 |
| Bonferroni one-sided upper bound (level 0.99375) | 0.5070 |
| sub-sample split | 2009-12-31 (A up to and including, B after) |
| sub-sample A | 0.1090 (n = 12) |
| sub-sample B | 0.0858 (n = 16) |
| sub-sample signs vs null | A+ B+ |

## Label

- Data label: **insufficient-evidence**. Reason: n below minimum.
- Literature label: **literature-disputed** (registry rows R-062).
- Refutation bound actually computed: one-sided 0.99375 upper bound 0.5070 against null 0.0000; it does not lie below the null, so refutation is excluded.

## Descriptive and robustness rows

| spec | variant | metric | horizon | n | value | CI low | CI high | p raw | notes |
|---|---|---|---|---|---|---|---|---|---|
| pct0.03/0.08f15 | cost0 | delta_sharpe | na | 28 | 0.1196 | -0.1736 | 0.4404 | 0.2269 | trades=28 |
| pct0.03/0.08f15 | short | delta_sharpe | na | 48 | -0.1677 | -0.5114 | 0.2103 | 0.8121 | trades=48 |
| pct0.03/0.08f15 | p_spell | delta_sharpe | na | 28 | 0.1099 | n/a | n/a | 0.0245 | random-spell null |
| pct0.03/0.08f15 | calls | share_right | na | 24 | 0.6667 | 0.4671 | 0.8203 | 0.1516 | right=16; wrong=8; descriptive |
| pct0.03/0.08f15 | sub_A | delta_sharpe | na | 12 | 0.1090 | n/a | n/a | n/a | sub-sample split 2009-12-31 |
| pct0.03/0.08f15 | sub_B | delta_sharpe | na | 16 | 0.0858 | n/a | n/a | n/a | sub-sample split 2009-12-31 |

## Specification sweep (descriptive)

Range of the primary metric over 15 grid points (not a selected optimum): min -0.4440, median 0.0228, max 0.1137.

| spec | variant | metric | horizon | n | value | CI low | CI high | p raw | notes |
|---|---|---|---|---|---|---|---|---|---|
| pct0.03/0.05f0 | primary | delta_sharpe | na | 62 | 0.0758 | -0.2346 | 0.4025 | 0.3173 | sweep; trades=62 |
| pct0.03/0.05f15 | primary | delta_sharpe | na | 54 | 0.0228 | -0.2941 | 0.3722 | 0.4523 | sweep; trades=54 |
| pct0.03/0.06f0 | primary | delta_sharpe | na | 42 | 0.1137 | -0.1831 | 0.4290 | 0.2274 | sweep; trades=42 |
| pct0.03/0.06f15 | primary | delta_sharpe | na | 38 | 0.0506 | -0.2676 | 0.3842 | 0.3863 | sweep; trades=38 |
| pct0.03/0.08f0 | primary | delta_sharpe | na | 28 | 0.1099 | -0.1827 | 0.4336 | 0.2464 | sweep; trades=28 |
| pct0.03/0.1f0 | primary | delta_sharpe | na | 14 | -0.2181 | -0.6132 | 0.1812 | 0.8556 | sweep; trades=14 |
| pct0.03/0.1f15 | primary | delta_sharpe | na | 14 | -0.2181 | -0.6132 | 0.1812 | 0.8556 | sweep; trades=14 |
| pct0.03/0.12f0 | primary | delta_sharpe | na | 18 | -0.2338 | -0.5402 | 0.0740 | 0.9300 | sweep; trades=18 |
| pct0.03/0.12f15 | primary | delta_sharpe | na | 18 | -0.2338 | -0.5402 | 0.0740 | 0.9300 | sweep; trades=18 |
| pct0.02/0.08f15 | primary | delta_sharpe | na | 28 | 0.1099 | -0.1827 | 0.4336 | 0.2464 | sweep; trades=28 |
| pct0.05/0.08f15 | primary | delta_sharpe | na | 28 | 0.1099 | -0.1827 | 0.4336 | 0.2464 | sweep; trades=28 |
| pct0.03/0.08f15 | tol0 | delta_sharpe | na | 28 | 0.0197 | -0.2918 | 0.3405 | 0.4553 | sweep; trades=28 |
| pct0.03/0.08f15 | djt0.12 | delta_sharpe | na | 20 | 0.0354 | -0.2657 | 0.3338 | 0.4083 | sweep; trades=20 |
| atr2.0/14f15 | primary | delta_sharpe | na | 26 | -0.0076 | -0.3234 | 0.3373 | 0.5187 | sweep; trades=26 |
| pivot5 | primary | delta_sharpe | na | 140 | -0.4440 | -0.7752 | -0.0892 | 0.9930 | sweep; trades=140 |

### Strategy against buy-and-hold (10 bps, long/cash)

| | strategy | buy-and-hold |
|---|---|---|
| Sharpe | 0.5693 | 0.4594 |
| annual return (log) | 0.0481 | 0.0797 |
| annual volatility | 0.0845 | 0.1735 |
| max drawdown | -0.1640 | -0.5378 |

Time in market 0.4226; trades 28; cumulative log-return difference -1.0993 (CI -2.4134 to 0.5121, p 0.924538). Price indices exclude dividends, which favours a strategy that is partly in cash.
Random-spell null p_spell = 0.0245.
Calls (descriptive, no label): {'right': 16, 'wrong': 8, 'n_calls': 24}.

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
