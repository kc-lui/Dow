# R3 Two-index confirmation (`rule_key: two_average_confirmation`)

Pair `DJ` (^DJI, ^DJT), 1992-01-02 to 2026-11-06, 8775 bars. Specification `pct0.03/0.08f15`. Run `a6d2d48e46014e7da3cc7c6be7ce8a02`.
Config hash `e6f5b9cd228e458809a42aa2a5c5e2811175de3d74fafca1a3496c6ac68ae24e`. Decision table sha256 `c8675eff2b281ac6f4fa8ed790063ecaf1e063d78f20fa9569ded1988be39836`. Bootstrap iterations 2000, seed 20261108.

## Event definition

Reversals on `^DJI` matched cycle-aware with `^DJT` (event bar = `confirmed_ts`) versus reversals with no match by `c + h` (event bar `c`). Metric: difference of mean signed excess returns, h = 60. Label permutation test, within-group cluster-bootstrap CI.

## Result

| field | value |
|---|---|
| events n | 15 |
| clusters | 13 |
| right-censored | 0 |
| metric | diff_excess_logret h60 |
| estimate | -0.0544 |
| 95% CI | [-0.1385, 0.0308] |
| null value | 0.0000 |
| p raw (one-sided, predicted direction) | 0.790105 |
| p used in the Holm family | 1.000000 |
| p Holm (family of 8) | 1.000000 |
| Bonferroni one-sided upper bound (level 0.99375) | 0.0457 |
| sub-sample split | 2009-12-31 (A up to and including, B after) |
| sub-sample A | -0.0079 (n = 5) |
| sub-sample B | -0.0312 (n = 10) |
| sub-sample signs vs null | A? B- |

## Label

- Data label: **insufficient-evidence**. Reason: n below minimum.
- Literature label: **literature-consensus** (registry rows R-032,R-033,R-034).
- Refutation bound actually computed: one-sided 0.99375 upper bound 0.0457 against null 0.0000; it does not lie below the null, so refutation is excluded.

### Exploratory rows (R11 F4)

For every row of this report, the single group is classified with information up to `c + h`, the outcome window itself, and a reversal matched later than `c + h` is in both groups. Treat these rows as exploratory; the label is unchanged (recommended redefinition for v3 in `analysis/protocol_deviations.md`).

## Descriptive and robustness rows

| spec | variant | metric | horizon | n | value | CI low | CI high | p raw | notes |
|---|---|---|---|---|---|---|---|---|---|
| pct0.03/0.08f15 | horizon20 | diff_excess_logret | h20 | 16 | 0.0131 | -0.0318 | 0.0620 | 0.4428 | groups confirmed=12 single=4; exploratory: the single-group classification uses information up to c+h (R11 F4) |
| pct0.03/0.08f15 | horizon120 | diff_excess_logret | h120 | 14 | 0.0122 | -0.0623 | 0.1143 | 0.5372 | groups confirmed=12 single=2; exploratory: the single-group classification uses information up to c+h (R11 F4) |
| pct0.03/0.08f15 | max_days90 | diff_excess_logret | h60 | 12 | -0.0508 | -0.1170 | 0.0102 | 0.8841 | groups confirmed=6 single=6; exploratory: the single-group classification uses information up to c+h (R11 F4) |
| pct0.03/0.08f15 | hit_rate_diff | hit_rate_diff | h60 | 15 | -0.5833 | n/a | n/a | 1.0000 | exploratory: the single-group classification uses information up to c+h (R11 F4) |
| pct0.03/0.08f15 | sub_A | diff_excess_logret | h60 | 5 | -0.0079 | n/a | n/a | n/a | sub-sample split 2009-12-31; exploratory: the single-group classification uses information up to c+h (R11 F4) |
| pct0.03/0.08f15 | sub_B | diff_excess_logret | h60 | 10 | -0.0312 | n/a | n/a | n/a | sub-sample split 2009-12-31; exploratory: the single-group classification uses information up to c+h (R11 F4) |

## Specification sweep (descriptive)

Range of the primary metric over 15 grid points (not a selected optimum): min -0.0579, median -0.0132, max 0.0328.

| spec | variant | metric | horizon | n | value | CI low | CI high | p raw | notes |
|---|---|---|---|---|---|---|---|---|---|
| pct0.03/0.05f0 | primary | diff_excess_logret | h60 | 41 | -0.0132 | -0.0561 | 0.0339 | 0.6707 | sweep; groups confirmed=28 single=13; exploratory: the single-group classification uses information up to c+h (R11 F4) |
| pct0.03/0.05f15 | primary | diff_excess_logret | h60 | 36 | -0.0154 | -0.0709 | 0.0409 | 0.6877 | sweep; groups confirmed=28 single=8; exploratory: the single-group classification uses information up to c+h (R11 F4) |
| pct0.03/0.06f0 | primary | diff_excess_logret | h60 | 38 | -0.0109 | -0.0550 | 0.0341 | 0.6477 | sweep; groups confirmed=26 single=12; exploratory: the single-group classification uses information up to c+h (R11 F4) |
| pct0.03/0.06f15 | primary | diff_excess_logret | h60 | 32 | 0.0208 | -0.0266 | 0.0667 | 0.2149 | sweep; groups confirmed=22 single=10; exploratory: the single-group classification uses information up to c+h (R11 F4) |
| pct0.03/0.08f0 | primary | diff_excess_logret | h60 | 15 | -0.0579 | -0.1414 | 0.0276 | 0.7986 | sweep; groups confirmed=12 single=3; exploratory: the single-group classification uses information up to c+h (R11 F4) |
| pct0.03/0.1f0 | primary | diff_excess_logret | h60 | 11 | -0.0358 | -0.0752 | 0.0068 | 0.7876 | sweep; groups confirmed=8 single=3; exploratory: the single-group classification uses information up to c+h (R11 F4) |
| pct0.03/0.1f15 | primary | diff_excess_logret | h60 | 11 | -0.0358 | -0.0752 | 0.0068 | 0.7876 | sweep; groups confirmed=8 single=3; exploratory: the single-group classification uses information up to c+h (R11 F4) |
| pct0.03/0.12f0 | primary | diff_excess_logret | h60 | 10 | 0.0204 | -0.0478 | 0.0804 | 0.2639 | sweep; groups confirmed=6 single=4; exploratory: the single-group classification uses information up to c+h (R11 F4) |
| pct0.03/0.12f15 | primary | diff_excess_logret | h60 | 10 | 0.0204 | -0.0478 | 0.0804 | 0.2639 | sweep; groups confirmed=6 single=4; exploratory: the single-group classification uses information up to c+h (R11 F4) |
| pct0.02/0.08f15 | primary | diff_excess_logret | h60 | 15 | -0.0544 | -0.1385 | 0.0308 | 0.7901 | sweep; groups confirmed=12 single=3; exploratory: the single-group classification uses information up to c+h (R11 F4) |
| pct0.05/0.08f15 | primary | diff_excess_logret | h60 | 15 | -0.0544 | -0.1385 | 0.0308 | 0.7901 | sweep; groups confirmed=12 single=3; exploratory: the single-group classification uses information up to c+h (R11 F4) |
| pct0.03/0.08f15 | tol0 | diff_excess_logret | h60 | 15 | -0.0198 | -0.1267 | 0.0923 | 0.6192 | sweep; groups confirmed=12 single=3; exploratory: the single-group classification uses information up to c+h (R11 F4) |
| pct0.03/0.08f15 | djt0.12 | diff_excess_logret | h60 | 14 | 0.0178 | -0.0315 | 0.0748 | 0.3158 | sweep; groups confirmed=8 single=6; exploratory: the single-group classification uses information up to c+h (R11 F4) |
| atr2.0/14f15 | primary | diff_excess_logret | h60 | 20 | -0.0078 | -0.0458 | 0.0245 | 0.6537 | sweep; groups confirmed=11 single=9; exploratory: the single-group classification uses information up to c+h (R11 F4) |
| pivot5 | primary | diff_excess_logret | h60 | 65 | 0.0328 | 0.0026 | 0.0698 | 0.0375 | sweep; groups confirmed=47 single=18; exploratory: the single-group classification uses information up to c+h (R11 F4) |

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
