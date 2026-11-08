# Evidence for dow-trend-classification

Every verbatim quote and rule id used in `../SKILL.md`, grouped by Workflow step. Quotes are copied from `../../../../research/sources/<slug>.md` and carry their `(slug:Qn)` pointer; the URL is the note's recorded source. Labels follow `../../../../research/canonical_rules.md` section 0 (definitions owned by `dow-theory-sources`). Project figures (state machine mechanics, stall lengths, signal counts, backtest rows) have no source note; their provenance is the file named in the row.

## Contents

1. Source URLs
2. Step 1: three trends, HH/HL definition, persistence
3. Step 3: state machine and EQUAL swings
4. Step 4: the Dow defense line and its analogues
5. Step 5: strict versus non-strict reversal
6. Step 6: warm-up and no lookahead
7. Step 7: data labels
8. Examples and Limitations
9. Rule ids cited

## 1. Source URLs

| Slug | Access | URL |
|---|---|---|
| nelson-1903-abc-of-stock-speculation | full-text | https://archive.org/stream/abcofstockspecul00nelsiala/abcofstockspecul00nelsiala_djvu.txt |
| hamilton-1922-stock-market-barometer | full-text | https://distantreader.org/stacks/trust/uc2/uc2_ark+=13960=t42r3r118.txt |
| russell-history-of-the-dow-theory | full-text | https://www.sfu.ca/~poitras/DOW-THEORY-HISTORY.pdf |
| schannep-dow-theory-21st-century | partial | https://www.aaii.com/journal/article/charles-dows-theory-still-valid-for-the-21st-century |
| thedowtheory-rhea-three-weeks | partial | https://thedowtheory.com/dow-theory-update-for-april-4th-did-rhea-really-tell-that-secondary-reactions-had-to-last-three-weeks/ |
| zh-ctyeh-dow-theory | partial, Chinese | https://ctyeh.com/stock/knowledge/12890 |
| zh-defense-line-search-log | search-snippet | n/a (WebSearch results and follow-up fetches, logged in the note) |
| dow-editorials-wsj-1900-1902 | partial, via Nelson and Hamilton reprints | no original scans; text via the nelson and hamilton URLs above |
| rhea-1932-the-dow-theory | partial, via Wiley excerpt of Schannep 2008 | https://catalogimages.wiley.com/images/db/pdf/9780470240595.excerpt.pdf |

Project files cited (no source note): `../../../../src/dowtheory/trend.py`, `../../../../src/dowtheory/analysis.py`, `../../../../docs/specs/algorithm_contract.md`, `../../../../configs/dow.yaml`, `../../../../reports/spec_review_p3.md`, `../../../../analysis/rule_status_table.md`, `../../../../reports/rule_R1.md`.

## 2. Step 1: three trends, HH/HL definition, persistence

| Quote | Pointer | Supports |
|---|---|---|
| "It is a bull period as long as the average of one high point exceeds that of previous high points. It is a bear period when the low point becomes lower than the previous low points." (nelson-1903-abc-of-stock-speculation:Q8) | Dow, Jan 4, 1902, Nelson Ch. VIII p.40; the same sentence is dow-editorials-wsj-1900-1902:Q3 | `R-016` trend definition by highs and lows, 【literature-consensus】; the machine's HH+HL / LH+LL establishment and HH/HL/LH/LL signals |
| "The primary trend, once in place, is assumed to continue in place until definitely proven otherwise." (schannep-dow-theory-21st-century:Q7) | Schannep, AAII article | `R-017` trend persists until reversal, 【literature-consensus】; a state persists until a `REVERSAL_*` signal |

Paraphrase rows (no quote): `R-001` three trends 【literature-consensus】 on the count (registry row lists Dow, Hamilton, Rhea and the educators); `R-002` to `R-004` primary duration 【literature-disputed】, positions tabulated in `dow-theory-sources` Step 3 and not restated; `R-006`, `R-007` secondary duration 【literature-disputed】, owned by `dow-swing-detection`; `R-015` daily movement low information 【literature-consensus】 (nelson-1903-abc-of-stock-speculation:Q3, quoted in `dow-swing-detection`); `R-046` swing thresholds 【agent-defined】. The nuance that Dow states highs for bulls and lows for bears while Rhea and the educators require both is the registry's own note on `R-016`.

## 3. Step 3: state machine and EQUAL swings

No source quotes. Provenance:

- States `UNDEFINED`, `BULL_PRIMARY`, `BEAR_PRIMARY`, `BULL_SUSPECT`, `BEAR_SUSPECT`; transition table; `TREND_ESTABLISHED` (A4); counter-swing bookkeeping; `secondary_direction` semantics: `../../../../docs/specs/algorithm_contract.md` TrendStateMachine section, Deviations 5, 6, 7, 14, 16, 17, Amendments A2 to A5, and `TrendStateMachine` in `../../../../src/dowtheory/trend.py`. 【agent-defined】 mechanics around `R-016` and `R-018`.
- `equal_extreme_tol` default and `require_lower_high_for_reversal` default: `../../../../configs/dow.yaml` `trend:`.
- The motivating case for the tolerance (2016-02-11 low a hair below 2015-08-25, read as LL, strict deadlock): `../../../../reports/spec_review_p3.md` rule-mapping row 2 and defect D3; contract Deviation 14.
- `LINE_BREAKOUT_UP/DOWN` produced by `analysis.py` from the line module, not by `run_trend`: contract Deviation 9.

## 4. Step 4: the Dow defense line and its analogues

| Quote | Pointer | Supports |
|---|---|---|
| "no page defines 道氏防線 or uses 防線 as a Dow Theory term in any page read" (zh-defense-line-search-log:Q1) | project search log, eight queries, US-only tool | `R-045` negative result, 【agent-defined】; the sentence that no source defines or names the line |
| "The lows of secondary reactions serve as our exit point (stop-loss) when broken down" (thedowtheory-rhea-three-weeks:Q6) | Blay, thedowtheory.com | `R-048` secondary low as stop, 【single-source】; nearest analogue of the bull-side line |
| "(always with confirmation)" (thedowtheory-rhea-three-weeks:Q7) | Blay, same page | `R-048`; Blay requires the second average, which the machine does not test |
| (Chinese, paraphrased in SKILL.md: the index broke below the pullback low of September 2021, used as a support reference) (zh-ctyeh-dow-theory:Q21) | Taiwan educator ctyeh | analogue row of `R-045`; the note marks the defense line not mentioned beyond this reference |

Paraphrase rows: the definition (last confirmed reaction low in a bull, reaction high in a bear), the refresh on HL/LH and on return to PRIMARY (A3, Deviation 16), `defense_line` always emitted with `agent_defined: true`: contract TrendStateMachine section and `_set_defense`, `_resume_primary`, `_enter` in `../../../../src/dowtheory/trend.py`; `defense_line_from_state` in `../../../../src/dowtheory/levels.py`. Stale-line defect before A3: `../../../../reports/spec_review_p3.md` row 12 and D4. First-hand notes marking the defense line not mentioned: the `defense_line` row of each of hamilton, nelson, rhea, dow-editorials, edwards-magee, kirkpatrick-dahlquist and russell-history notes, summarised in the registry row `R-045`. The Schaefer halfway level as a third analogue: `R-065`, 【single-source】 (section 5 below).

## 5. Step 5: strict versus non-strict reversal

| Quote | Pointer | Supports |
|---|---|---|
| "the change in the broad general direction of the market is abrupt, while the resumption of the major movement is appreciably slower" (hamilton-1922-stock-market-barometer:Q23) | Hamilton, Ch. XIII p.143 | `R-019` 【single-source】; colour for the orthodox position P1 of `R-018` |
| "When the Averages broke through their preceding secondary lows, many orthodox Dow Theorists, who relied almost totally (as most do today) on the pattern of the Averages, proclaimed that a bear market had started." (russell-history-of-the-dow-theory:Q7) | Russell, history essay p.5 | `R-018` 【literature-disputed】: Russell's description of the orthodox break-of-secondary-low reading, which the non-strict mode resembles |
| "to remain invested in harmony with the primary trend of the market" (russell-history-of-the-dow-theory:Q6) | Russell on Schaefer, p.4 (the full sentence also says Schaefer told subscribers to ignore temporary reactions) | `R-018` position P2, the Schaefer and Russell dissent, 【literature-disputed】 |

Paraphrase rows: the 50 percent principle and the third-phase test, `R-065`, 【single-source】 (russell-history-of-the-dow-theory paraphrase section, Q7 context); the orthodox P1 sources (hamilton:Q23,Q24; rhea:Q6; stockcharts:Q8; kirkpatrick-dahlquist:Q3; edwards-magee:Q6; oanda-bvi trend-changes Q3,Q4; russell-dow-theory-letters:Q5; thedowtheory-basics:Q9) are listed in the registry row `R-018` and quoted, where quoted, in `dow-theory-sources`. Mode behaviour (`DEFENSE_BREAK` then SUSPECT, or immediate flip without `REVERSAL_*`): contract Deviation 6 and `_defense_break` in `../../../../src/dowtheory/trend.py`. Hamilton Q24 is not quoted in SKILL.md because it contains an inner quoted word that the quote linter cannot span.

## 6. Step 6: warm-up and no lookahead

| Quote | Pointer | Supports |
|---|---|---|
| "It is often difficult to judge whether the end of an advance has come because the movement of prices is that which would occur if the main tendency had changed. Yet, it may only be an unusually pronounced secondary movement." (nelson-1903-abc-of-stock-speculation:Q9) | Dow, Jan 4, 1902, Nelson Ch. VIII p.40 | `R-020` reversal hard to tell from a secondary, 【literature-consensus】; implemented through `confirmed_idx` replay and the SUSPECT states |

Paraphrase rows: `warmup_note` and `meta.warmup_note`: contract A4 and Deviation 17, `warmup_note` in `../../../../src/dowtheory/trend.py`; start-date dependence (2016 bear silent with a 2015 start, REVERSAL_DOWN on 2016-02-11 with a 1992 start): `../../../../reports/spec_review_p3.md` D5; look-ahead audit of trend state, defense line and signals with zero mismatches on 390 ^DJI and 451 ^DJT sampled bars: `../../../../reports/spec_review_p3.md` section 2; truncation test: `../tests/test_cli.py`.

## 7. Step 7: data labels

No source quotes. Provenance: `../../../../analysis/rule_status_table.md` (run `a6d2d48e46014e7da3cc7c6be7ce8a02`, pair DJ, specification `pct0.03/0.08f15`, 1992-01-02 to 2026-11-06) and `../../../../reports/rule_R1.md`.

- R1 trend_persistence, mapped to `R-016`, `R-017`: 【data-confirmed】, p_extend 0.8788, n 33, Wilson CI 0.7267 to 0.9518, p_holm 0.000044. Mandatory caveat (R11 audit F1), copied from the status table and the R1 report: the 0.5 null is not a random-walk baseline; a drift-matched random walk through the same machinery gives p_extend of about 0.65 to 0.69 (auditor: iid 0.654, zero drift 0.633, block bootstrap 0.695); the harness random-walk p is p_sim = 0.0055 (null mean 0.6906 over 2000 paths). Cite the baseline, p_sim and n = 33; never p_holm alone.
- R2 primary_reversal_signal, mapped to `R-018`, `R-020`: 【insufficient-evidence】, n 12, mean_excess_logret_h60 -0.0151, CI -0.0456 to 0.0206, p_holm 1.0, n below the minimum of 30, pair-inconsistent.
- Authority for the labelling rule: `dow-rule-backtest`.

## 8. Examples and Limitations

- Test fixture `../tests/fixtures/defense_break_sample.csv`: synthetic piecewise-linear legs 100, 120, 108, 130, 100, 118, 95, 105, generated by `../tests/fixtures/make_defense_break_sample.py`; strict run gives DEFENSE_BREAK 2021-04-29 and REVERSAL_DOWN 2021-06-22, non-strict flips on 2021-04-29, 【agent-defined】 construction for wrapper tests only.
- Example 1 output: run of `../scripts/trend.py --source csv --csv tests/fixtures/dji_sample.csv` on 2026-11-08; the fixture is synthetic (`../../../../tests/fixtures/make_dji_sample.py`).
- Example 2 output (BULL_PRIMARY since 2023-06-15, defense line 45166.64 set 2026-04-17 from the 2026-03-27 low, 36 signals strict, 34 signals non-strict with `since` 2022-11-23): runs of `../scripts/trend.py --symbol ^DJI --start 2015-01-01` with and without `--no-strict` on 2026-11-08 against `dow.mkt_klines` (data through 2026-11-06).
- Example 3 output (REVERSAL_DOWN 2016-02-11, REVERSAL_UP 2016-04-14, 102 signals over 8775 bars, 【agent-defined】 counts from the project's machine): run of `../scripts/trend.py --symbol ^DJI --json` on 2026-11-08; the swing context (2015-08-25 L 15666.44, 2015-11-03 H 17918.15, 2016-02-11 L 15660.18 confirmed 2016-03-03) from `dow-swing-detection` `scripts/swings.py --symbol ^DJI --start 2014-01-01 --end 2016-12-31 --scale secondary`.
- Stall of 296 sessions from 2018-12-19 (【agent-defined】, contract Deviation 16) and stall of 597 sessions from 2016-04-14 before the tolerance, measured by the spec review at `secondary_pct` 0.10 before amendment A1, with the same deadlock reported at 0.08 (【agent-defined】, `../../../../reports/spec_review_p3.md` D3), both behaviour of the project's machine.
- `secondary_direction` lag: `../../../../reports/spec_review_p3.md` D10.
- ^DJI and ^DJT history begins 1992-01-02: `../../../../analysis/rule_status_table.md` header.
- Confirmation lag of signals: median secondary confirmation lag tabulated in `dow-swing-detection` Step 4 (from spec review section 3b).

## 9. Rule ids cited

| Id | Key | Registry label | Used for |
|---|---|---|---|
| R-001 | three_trends | consensus | Step 1 table |
| R-002 to R-004 | primary duration | disputed / disputed / single-source | Step 1 pointer to `dow-theory-sources` |
| R-006, R-007 | secondary duration | disputed | Step 1 pointer to `dow-swing-detection` |
| R-013, R-046 | minor filter, swing thresholds | single-source / agent-defined | Boundaries and Limitations, owned by `dow-swing-detection` |
| R-015 | daily_fluctuation_low_information | consensus | Prerequisites 3 |
| R-016 | trend_definition_hh_hl | consensus | Step 1 quote, state machine, R1 mapping |
| R-017 | trend_persists_until_reversal | consensus | Step 1 quote, R1 mapping |
| R-018 | reversal_definition_swing_structure | disputed | Step 5 both positions, R2 mapping |
| R-019 | reversal_abrupt_resumption_slow | single-source | Step 5 Hamilton quote |
| R-020 | reversal_hard_to_tell_from_secondary | consensus | Step 6 quote, SUSPECT states, R2 mapping |
| R-022 to R-035 | lines and confirmation | various | Boundaries only; `R-032` in Limitations 4 |
| R-045 | defense_line | agent-defined | Step 4 definition, every mention of the line |
| R-047, R-049 to R-055 | levels and drawing | agent-defined / various | Boundaries only |
| R-048 | secondary_low_as_stop | single-source | Step 4 analogue, Limitations 4 |
| R-065 | schaefer_50pct_principle | single-source | Step 4 analogue, Step 5 dissent |
