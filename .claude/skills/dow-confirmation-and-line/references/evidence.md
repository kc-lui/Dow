# Evidence for dow-confirmation-and-line

Every verbatim quote and rule id used in `../SKILL.md`, grouped by Workflow step. Quotes are copied from `../../../../research/sources/<slug>.md` and carry their `(slug:Qn)` pointer; the URL is the note's recorded source. Labels follow `../../../../research/canonical_rules.md` section 0 (definitions owned by `dow-theory-sources`). Project figures (line counts, matching mechanics, backtest rows) have no source note; their provenance is the file named in the row.

## Contents

1. Source URLs
2. Step 1: two-average confirmation and the time-window question
3. Step 4: Dow lines
4. Step 6: the volume flag
5. Step 7: data labels
6. Examples and Limitations
7. Rule ids cited

## 1. Source URLs

| Slug | Access | URL |
|---|---|---|
| hamilton-1922-stock-market-barometer | full-text | https://distantreader.org/stacks/trust/uc2/uc2_ark+=13960=t42r3r118.txt |
| rhea-1932-the-dow-theory | partial, via Wiley excerpt of Schannep 2008 | https://catalogimages.wiley.com/images/db/pdf/9780470240595.excerpt.pdf |
| nelson-1903-abc-of-stock-speculation | full-text | https://archive.org/stream/abcofstockspecul00nelsiala/abcofstockspecul00nelsiala_djvu.txt |
| russell-history-of-the-dow-theory | full-text | https://www.sfu.ca/~poitras/DOW-THEORY-HISTORY.pdf |
| brown-goetzmann-kumar-1998 | full-text | https://chesler.us/about/about%20files/dow_theory.pdf |
| cmt-open-exam-prep-dow-theory | web page | https://open-exam-prep.com/study-guides/cmt/theory-and-history/dow-theory |
| wikipedia-en-dow-theory | web page | https://en.wikipedia.org/wiki/Dow_theory |
| incrediblecharts-dow-theory-trends | web page | https://www.incrediblecharts.com/technical/dow_theory_trends.php |
| thedowtheory-lines-special-issue | web page (Blay) | https://thedowtheory.com/dow-theory-special-issue-lines-classical-dow-theory-and-schannep/ |
| edwards-magee-technical-analysis-dow-chapters | Google Books snippets | https://books.google.com/books?id=MDgPEAAAQBAJ |
| zh-ctyeh-dow-theory | partial, Chinese | https://ctyeh.com/stock/knowledge/12890 |

Project files cited (no source note): `../../../../src/dowtheory/confirmation.py`, `../../../../src/dowtheory/line.py`, `../../../../src/dowtheory/analysis.py`, `../../../../docs/specs/algorithm_contract.md`, `../../../../configs/dow.yaml`, `../../../../configs/pairs.yaml`, `../../../../reports/spec_review_p3.md`, `../../../../analysis/rule_status_table.md`, `../../../../reports/rule_R3.md`, `../../../../reports/rule_R6.md`, `../../../../reports/rule_R7.md`, `../../../../analysis/protocol_deviations.md`.

## 2. Step 1: two-average confirmation and the time-window question

| Quote | Pointer | Supports |
|---|---|---|
| "The movement of one price average must be confirmed by the other before reliable inferences may be drawn." (rhea-1932-the-dow-theory:Q6) | Rhea, Both Averages Must Confirm, via Wiley/Schannep p.9 | `R-032` 【literature-consensus】 |
| "One of the shortest ways of going wrong is to accept an indication by one average which has not been clearly confirmed by the other." (hamilton-1922-stock-market-barometer:Q21) | Hamilton Ch. XII p.138 | `R-032` |
| "it was Hamilton who first defined the confirmation principle of the Averages." (russell-history-of-the-dow-theory:Q4) | Russell p.2 | `R-032` provenance: Hamilton, not Dow |
| "the averages must confirm each other, although they may not break out of their respective lines on the same day or in the same week. It is sufficient if they take the same direction." (hamilton-1922-stock-market-barometer:Q25) | Hamilton Ch. XIV p.159 | `R-033` 【literature-consensus】 no same-day requirement; `confirmation.max_days: null` |
| "the confirmation need not occur on the same day." (brown-goetzmann-kumar-1998:Q5) | Brown, Goetzmann, Kumar Sec. I p.5 | `R-033` |
| "Confirmation can lag days or longer." (cmt-open-exam-prep-dow-theory:Q3) | CMT study guide, Confirmation | `R-033` |
| "Waiting is part of the method." (cmt-open-exam-prep-dow-theory:Q4) | CMT study guide, Confirmation | `R-033` |
| "When the performance of the averages diverges, it is a warning that change is in the air." (wikipedia-en-dow-theory:Q11) | Wikipedia, Tenet 4 | non-confirmation is a warning, never a reversal |
| "A bear market commences when a bear trend on one average is confirmed by the start of a bear trend on the other average." (incrediblecharts-dow-theory-trends:Q11) | IncredibleCharts, Confirmation | both averages must start the new trend before the market is called |

Paraphrase rows (no quote): Rhea's statement that line breaks are simultaneous is available only as a paraphrase in the rhea note (Wiley p.10, no Qn) and is recorded in the `R-026` and `R-033` disagreeing columns of the registry as an internal tension with Hamilton Q25; the nelson note's finding that Dow's text contains no two-average rule is the `R-032` disagreeing column. `pair_confirm` status table and `confirm_signal` matching: `../../../../docs/specs/algorithm_contract.md` confirmation.py section, Deviation 10, Amendment A7; `pair_confirm` and `confirm_signal` in `../../../../src/dowtheory/confirmation.py`; defect D1 of `../../../../reports/spec_review_p3.md` is the reason for cycle-aware matching in either order. Pair definitions: `../../../../configs/pairs.yaml` (`R-034` 【literature-consensus】 for ^DJI with ^DJT; SP_IYT 【agent-defined】).

## 3. Step 4: Dow lines

| Quote | Pointer | Supports |
|---|---|---|
| "a succession of closing prices, over a sufficient number of days for a fair volume of trading within a narrow range" (hamilton-1922-stock-market-barometer:Q24) | Hamilton Ch. XIV p.159 (sub-span; the OCR drops the dashes around the parenthetical) | `R-022` 【literature-consensus】 line defined on closing prices of the averages; `R-036` closes only |
| "a movement of the average price out of that line, downward or upward, will confidently indicate a change in the general market direction of at least a secondary and even a primary character, which we can depend upon where either average is confirmed by the other." (hamilton-1922-stock-market-barometer:Q24) | same sentence, second sub-span | `R-026` breakout meaning, `R-027` at least secondary character, `R-032` confirmation of the break |
| "stay within a narrow range of prices, say 2 points, until there has formed quite a long horizontal line of these figures." (nelson-1903-abc-of-stock-speculation:Q12) | Dow, Jul 20, 1901, in Nelson Ch. IX p.42 (also dow-editorials-wsj-1900-1902:Q4 and hamilton:Q10 with "two points") | `R-023` point range for an individual stock; `R-022` Dow's usage is for a stock's chart |
| "the price variation of both averages move within a range of approximately five per cent." (thedowtheory-lines-special-issue:Q2) | Blay quoting Rhea (Fraser p.79); the same sentence is rhea-1932-the-dow-theory:Q8 with "5 percent" | `R-023` about 5 percent, `R-025` both averages |
| "Hamilton said that we could always depend upon the breaking of a line" (thedowtheory-lines-special-issue:Q5) | Blay quoting Rhea | `R-026` |
| "Generally speaking, the longer the Line (in duration) and the narrower or more compact its price range, the greater the significance of its ultimate breakout." (edwards-magee-technical-analysis-dow-chapters:Q7) | Edwards and Magee, 10th ed. snippet, Ch. 3 | `R-063` 【literature-consensus】, not implemented |
| "which has been discarded by Schannep." (thedowtheory-lines-special-issue:Q14) | Blay | `R-022` disagreeing column: Schannep discards lines |

Paraphrase rows: Rhea's two to three weeks or longer (`R-024`; verbatim in rhea-1932-the-dow-theory:Q8 and thedowtheory-lines-special-issue:Q1, not quoted in SKILL.md because the lines carry inner quotation marks); Hamilton's 1914 line of 66 and 71 trading days with 3 and 4 point ranges (hamilton note paraphrase, registry section 2.3 and 2.4, no Qn, under `R-023` (points) and `R-024` (days) 【literature-consensus】 one lineage, points not percent); `R-028` 3 percent penetration, `R-029` breakout volume (zh-stockcloud-dow-theory-line, Chinese, 【single-source】); `R-030` measured move (thedowtheory-lines-special-issue:Q7, 【single-source】); `R-031` lines after the secondary break (hamilton:Q23, 【single-source】); `R-064` line substitutes for a secondary (incredible:Q7, edwards-magee tenet heading). Implementation: `detect_lines`, `_window_end`, `_joint_end`, `_drift_ok`, `_first_breakout`, `_build` in `../../../../src/dowtheory/line.py`; contract line.py section, Deviation 9, Amendment A6; `LINE_BREAKOUT_*` emission in `_line_signals` of `../../../../src/dowtheory/analysis.py`; parameters in `../../../../configs/dow.yaml` `line:`. Line counts (108 before the amendment, 57 chained, 41 after the drift filter over 2015 to 2026, 103 over 1992 onward, 41 percent of 15-session windows within a joint 5 percent band, all 【agent-defined】 measurements) and the trend-segment judgement: `../../../../reports/spec_review_p3.md` rule-mapping row 8, section 3a, defects D2 and D6. The 28-calendar-day shading floor: contract Deviation 12.

## 4. Step 6: the volume flag

| Quote | Pointer | Supports |
|---|---|---|
| "the volume of trading is always larger in a bull market than in a bear market. It expands as prices go up and contracts as they decline." (hamilton-1922-stock-market-barometer:Q19) | Hamilton Ch. XII p.136 | `R-037` 【literature-consensus】 volume with the primary trend |
| "the averages have already taken those things into account" (hamilton-1922-stock-market-barometer:Q5) | Hamilton Ch. I pp.7-8 | `R-041` 【literature-consensus】 volume subordinate to price |
| "A sharp reaction in a bull market will often stimulate the volume of business." (hamilton-1922-stock-market-barometer:Q20) | Hamilton Ch. XII pp.136-137 | `R-038` 【literature-disputed】 position P1 |
| "Volume typically expands with the primary direction and dries up against it." (cmt-open-exam-prep-dow-theory:Q9) | CMT study guide, Volume | `R-038` position P2 |
| (Chinese, paraphrased in SKILL.md: volume should grow with the trend and shrink against it; a pullback is one on shrinking volume) (zh-ctyeh-dow-theory:Q17, Q18) | Taiwan educator ctyeh | `R-038` position P2 |

Paraphrase rows: Dow's advice to keep a volume record (nelson-1903-abc-of-stock-speculation:Q4, `R-037` agreeing column, no rule); `volume_confirms` mechanics: contract Deviation 11 and `volume_confirms` in `../../../../src/dowtheory/confirmation.py`; `analysis.analyze` passes the first average's frame and its confirmed secondary swings. Index volume level breaks and the 2000 start of R7: `../../../../analysis/protocol_deviations.md`, volume caveat correction, and the data coverage section quoted in `../../../../reports/rule_R7.md`.

## 5. Step 7: data labels

No source quotes. Figures are copied from `../../../../analysis/rule_status_table.md` (run `a6d2d48e46014e7da3cc7c6be7ce8a02`, 2026-11-08, pair DJ, specification `pct0.03/0.08f15`, 1992-01-02 to 2026-11-06) and the per-rule reports:

- R3 two_average_confirmation, `../../../../reports/rule_R3.md`: n 15, diff_excess_logret h60 -0.0544, CI [-0.1385, 0.0308], refutation bound 0.0457 against null 0, 【insufficient-evidence】 (n below minimum); every row marked exploratory under R11 F4; `../../../../analysis/protocol_deviations.md` DEV-11 recommends redefining the single group for v3.
- R6 line_breakout, `../../../../reports/rule_R6.md`: n 87 (clusters 77, one right-censored), agree h20 0.4138, Wilson CI [0.3161, 0.5188], refutation bound 0.5471 against null 0.5, sub-samples 0.4250 (n 40) and 0.4043 (n 47), horizon 60 row 0.5233, horizon 120 row 0.5000, 【insufficient-evidence】 (not significant after Holm); pair-inconsistent.
- R7 volume_confirmation, `../../../../reports/rule_R7.md`: n 57 from 2000-01-03, p_vol 0.3509, CI [0.2400, 0.4806], refutation bound 0.5162 against null 0.5, `volume_confirms` share_true 0.4058 over 69 evaluations, sweep range 0.2903 to 0.4739 over 15 grid points, 【insufficient-evidence】.

## 6. Examples and Limitations

Project data only. Example 1 output: `scripts/confirm.py --source csv --csv ../../../tests/fixtures/dji_sample.csv` on the fixture built by `../../../../tests/fixtures/make_dji_sample.py`. Examples 2 and 3: `scripts/confirm.py --symbol ^DJI --pair ^DJT --start 2015-01-01` and the same without `--start`, ClickHouse `dow.mkt_klines` on 2026-11-08 with data through 2026-11-06 (2980 common sessions since 2015, 8775 since 1992). Example 4: `tests/fixtures/pair_a_sample.csv` and `pair_b_sample.csv` from `tests/fixtures/make_pair_sample.py`. The 1992 data start of ^DJT: data coverage section of the decision table, quoted in `../../../../reports/rule_R3.md`.

## 7. Rule ids cited

| Rule | Key | Registry label | Where used |
|---|---|---|---|
| `R-013` | minor_move_filter | consensus (owned by `dow-swing-detection`) | Boundaries |
| `R-016` to `R-020` | trend definitions and reversal (owned by `dow-trend-classification`) | consensus / disputed | Boundaries |
| `R-022` | line_definition | consensus | Step 4, Step 7 |
| `R-023` | line_band_pct | consensus (one lineage) | Step 4, Limitations |
| `R-024` | line_min_duration | consensus (one lineage) | Step 4, Limitations |
| `R-025` | line_both_averages | consensus | Step 4 |
| `R-026` | line_breakout_meaning | consensus | Step 1, Step 4 |
| `R-027` | line_break_implies_secondary_or_more | consensus | Step 7 |
| `R-028` | line_breakout_3pct_filter | single-source | Step 4, Limitations |
| `R-029` | line_breakout_volume | single-source | Step 4, Limitations |
| `R-030` | line_breakout_measured_move | single-source | Step 4 |
| `R-031` | line_precedes_resumption | single-source | Step 4 |
| `R-032` | two_average_confirmation | consensus | Step 1, Step 3, Step 7, Example 2 |
| `R-033` | confirmation_lag | consensus | Step 1, Step 4, Step 5, Limitations |
| `R-034` | confirmation_pair | consensus | Prerequisites, Step 7 |
| `R-036` | closing_prices_only | consensus | evidence section 3 |
| `R-037` | volume_with_primary_trend | consensus | Step 6, Step 7 |
| `R-038` | volume_in_secondary_reaction | disputed | Step 6, Step 7, Examples, Limitations |
| `R-041` | volume_secondary_to_price | consensus | Step 6, Step 7 |
| `R-045` | defense_line | agent-defined (owned by `dow-trend-classification`) | Boundaries |
| `R-046` | swing_detection_thresholds | agent-defined (owned by `dow-swing-detection`) | Boundaries |
| `R-047`, `R-049` to `R-055` | levels and chart (owned by `dow-levels-and-chart`) | various | Boundaries |
| `R-063` | line_significance_grows | consensus | Step 4 |
| `R-064` | line_substitutes_for_secondary | consensus | Step 4 |
