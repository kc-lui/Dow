# R3 Two-index confirmation (`rule_key: two_average_confirmation`)

Pair `SP_IYT` (SPY, IYT), 2004-01-02 to 2026-11-06, 5749 bars. Specification `pct0.03/0.08f15`. Run `a6d2d48e46014e7da3cc7c6be7ce8a02`.
Config hash `e6f5b9cd228e458809a42aa2a5c5e2811175de3d74fafca1a3496c6ac68ae24e`. Decision table sha256 `c8675eff2b281ac6f4fa8ed790063ecaf1e063d78f20fa9569ded1988be39836`. Bootstrap iterations 2000, seed 20261108.

## Event definition

Reversals on `^DJI` matched cycle-aware with `^DJT` (event bar = `confirmed_ts`) versus reversals with no match by `c + h` (event bar `c`). Metric: difference of mean signed excess returns, h = 60. Label permutation test, within-group cluster-bootstrap CI.

## Result

| field | value |
|---|---|
| events n | 9 |
| clusters | 8 |
| right-censored | 0 |
| metric | diff_excess_logret h60 |
| estimate | -0.0922 |
| 95% CI | [-0.1639, 0.0082] |
| null value | 0.0000 |
| p raw (one-sided, predicted direction) | 0.857071 |
| p used in the Holm family | n/a |
| p Holm (family of 8) | n/a |
| Bonferroni one-sided upper bound (level 0.99375) | 0.0369 |
| sub-sample split | 2015-12-31 (A up to and including, B after) |
| sub-sample A | -0.0519 (n = 5) |
| sub-sample B | n/a (n = 0) |
| sub-sample signs vs null | A? B? |

## Label

- No label: `SP_IYT` is a robustness pair (labels come from `DJ` only).

### Exploratory rows (R11 F4)

For every row of this report, the single group is classified with information up to `c + h`, the outcome window itself, and a reversal matched later than `c + h` is in both groups. Treat these rows as exploratory; the label is unchanged (recommended redefinition for v3 in `analysis/protocol_deviations.md`).

## Descriptive and robustness rows

| spec | variant | metric | horizon | n | value | CI low | CI high | p raw | notes |
|---|---|---|---|---|---|---|---|---|---|
| pct0.03/0.08f15 | horizon20 | diff_excess_logret | h20 | 10 | 0.0303 | -0.0442 | 0.1142 | 0.4063 | groups confirmed=8 single=2; exploratory: the single-group classification uses information up to c+h (R11 F4) |
| pct0.03/0.08f15 | horizon120 | diff_excess_logret | h120 | 8 | n/a | n/a | n/a | n/a | groups confirmed=8 single=0;; exploratory: the single-group classification uses information up to c+h (R11 F4) |
| pct0.03/0.08f15 | max_days90 | diff_excess_logret | h60 | 8 | -0.0593 | -0.1502 | 0.0371 | 0.8106 | groups confirmed=5 single=3; exploratory: the single-group classification uses information up to c+h (R11 F4) |
| pct0.03/0.08f15 | hit_rate_diff | hit_rate_diff | h60 | 9 | -0.3750 | n/a | n/a | 1.0000 | exploratory: the single-group classification uses information up to c+h (R11 F4) |
| pct0.03/0.08f15 | sub_A | diff_excess_logret | h60 | 5 | -0.0519 | n/a | n/a | n/a | sub-sample split 2015-12-31; exploratory: the single-group classification uses information up to c+h (R11 F4) |
| pct0.03/0.08f15 | sub_B | diff_excess_logret | h60 | 0 | n/a | n/a | n/a | n/a | sub-sample split 2015-12-31; exploratory: the single-group classification uses information up to c+h (R11 F4) |

## Specification sweep (descriptive)

Range of the primary metric over 14 grid points (not a selected optimum): min -0.1485, median -0.0241, max 0.1191.

| spec | variant | metric | horizon | n | value | CI low | CI high | p raw | notes |
|---|---|---|---|---|---|---|---|---|---|
| pct0.03/0.05f0 | primary | diff_excess_logret | h60 | 20 | 0.0225 | -0.0316 | 0.0821 | 0.3478 | sweep; groups confirmed=18 single=2; exploratory: the single-group classification uses information up to c+h (R11 F4) |
| pct0.03/0.05f15 | primary | diff_excess_logret | h60 | 15 | 0.0045 | -0.0354 | 0.0375 | 0.4473 | sweep; groups confirmed=14 single=1; exploratory: the single-group classification uses information up to c+h (R11 F4) |
| pct0.03/0.06f0 | primary | diff_excess_logret | h60 | 21 | -0.0906 | -0.1851 | 0.0183 | 0.9355 | sweep; groups confirmed=18 single=3; exploratory: the single-group classification uses information up to c+h (R11 F4) |
| pct0.03/0.06f15 | primary | diff_excess_logret | h60 | 14 | n/a | n/a | n/a | n/a | sweep; groups confirmed=14 single=0; exploratory: the single-group classification uses information up to c+h (R11 F4) |
| pct0.03/0.08f0 | primary | diff_excess_logret | h60 | 13 | -0.1485 | -0.1897 | -0.1070 | 0.9140 | sweep; groups confirmed=12 single=1; exploratory: the single-group classification uses information up to c+h (R11 F4) |
| pct0.03/0.1f0 | primary | diff_excess_logret | h60 | 6 | -0.0527 | -0.1077 | 0.0024 | 0.6762 | sweep; groups confirmed=5 single=1; exploratory: the single-group classification uses information up to c+h (R11 F4) |
| pct0.03/0.1f15 | primary | diff_excess_logret | h60 | 6 | -0.0527 | -0.1077 | 0.0024 | 0.6762 | sweep; groups confirmed=5 single=1; exploratory: the single-group classification uses information up to c+h (R11 F4) |
| pct0.03/0.12f0 | primary | diff_excess_logret | h60 | 5 | 0.0559 | -0.0681 | 0.1800 | 0.2089 | sweep; groups confirmed=3 single=2; exploratory: the single-group classification uses information up to c+h (R11 F4) |
| pct0.03/0.12f15 | primary | diff_excess_logret | h60 | 5 | 0.0559 | -0.0681 | 0.1800 | 0.2089 | sweep; groups confirmed=3 single=2; exploratory: the single-group classification uses information up to c+h (R11 F4) |
| pct0.02/0.08f15 | primary | diff_excess_logret | h60 | 9 | -0.0922 | -0.1639 | 0.0082 | 0.8571 | sweep; groups confirmed=8 single=1; exploratory: the single-group classification uses information up to c+h (R11 F4) |
| pct0.05/0.08f15 | primary | diff_excess_logret | h60 | 9 | -0.0922 | -0.1639 | 0.0082 | 0.8571 | sweep; groups confirmed=8 single=1; exploratory: the single-group classification uses information up to c+h (R11 F4) |
| pct0.03/0.08f15 | tol0 | diff_excess_logret | h60 | 9 | -0.0922 | -0.1639 | 0.0082 | 0.8571 | sweep; groups confirmed=8 single=1; exploratory: the single-group classification uses information up to c+h (R11 F4) |
| pct0.03/0.08f15 | djt0.12 | diff_excess_logret | h60 | 8 | 0.1191 | 0.0753 | 0.1843 | 0.0290 | sweep; groups confirmed=4 single=4; exploratory: the single-group classification uses information up to c+h (R11 F4) |
| atr2.0/14f15 | primary | diff_excess_logret | h60 | 10 | 0.0280 | -0.0337 | 0.0892 | 0.3328 | sweep; groups confirmed=8 single=2; exploratory: the single-group classification uses information up to c+h (R11 F4) |
| pivot5 | primary | diff_excess_logret | h60 | 34 | 0.0222 | -0.0077 | 0.0581 | 0.2049 | sweep; groups confirmed=27 single=7; exploratory: the single-group classification uses information up to c+h (R11 F4) |

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
