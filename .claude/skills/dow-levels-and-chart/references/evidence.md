# Evidence for dow-levels-and-chart

Every verbatim quote and rule id used in `../SKILL.md`, grouped by Workflow step. Quotes are copied from `../../../../research/sources/<slug>.md` and carry their `(slug:Qn)` pointer; the URL is the note's recorded source. Chinese-language sources (stockcloud, OANDA, kcmtrade, ctyeh) are paraphrased in the skill with their Qn pointers and are not quoted, because skill text is English. Labels follow `../../../../research/canonical_rules.md` section 0 (definitions owned by `dow-theory-sources`). Project figures (tolerances, touch counts, the shading floor, the example levels) have no source note; their provenance is the file named in the row.

## Contents

1. Source URLs
2. Step 1: what the literature says about drawing
3. Step 3: support and resistance zones
4. Step 4: trendlines
5. Step 5: elements owned elsewhere
6. Step 8: data labels
7. Examples and Limitations
8. Rule ids cited

## 1. Source URLs

| Slug | Access | URL |
|---|---|---|
| nelson-1903-abc-of-stock-speculation | full-text | https://archive.org/stream/abcofstockspecul00nelsiala/abcofstockspecul00nelsiala_djvu.txt |
| sperandeo-123-stockjock | web page (blog summary of Sperandeo) | https://stockjock2.blogspot.com/2007/08/sperandeo-analysis.html |
| thedowtheory-rhea-three-weeks | web page (Blay) | https://thedowtheory.com/dow-theory-update-for-april-4th-did-rhea-really-tell-that-secondary-reactions-had-to-last-three-weeks/ |
| zh-stockcloud-dow-theory-trendline | web page, Chinese (paraphrased) | https://www.stockcloud.tw/2024/01/Dow-Theory-trendline.html |
| oanda-bvi-dow-theory-after-breakout | web page, Chinese (paraphrased) | https://www.oanda.com/bvi-ft/lab-education/technical_analysis/dow-theory-after_breakout/ |
| oanda-bvi-dow-theory-breakout-return-moves | web page, Chinese (paraphrased) | https://www.oanda.com/bvi-ft/lab-education/technical_analysis/dow-theory-breakout_return_moves/ |
| oanda-bvi-dow-theory-trend-continuation | web page, Chinese (paraphrased) | https://www.oanda.com/bvi-ft/lab-education/technical_analysis/trend_continuation_forward_idea/ |
| kcmtrade-dow-theory | web page, Chinese (paraphrased) | https://www.kcmtrade.com/tw/hc/content/dao-shi-li-lun-shi-shi-mo-cong-gao-di-dian-kan-dong-shang-sheng-xia-jiang-yu-pan-zheng-qu-shi |
| edwards-magee-technical-analysis-dow-chapters | Google Books snippets; the note records support and resistance drawing as not mentioned in the Dow chapters | https://books.google.com/books?id=MDgPEAAAQBAJ |

Project files cited (no source note): `../../../../src/dowtheory/levels.py`, `../../../../src/dowtheory/chart.py`, `../../../../src/dowtheory/report.py`, `../../../../src/dowtheory/analysis.py`, `../../../../src/dowtheory/cli.py`, `../../../../src/dowtheory/persist.py`, `../../../../docs/specs/algorithm_contract.md`, `../../../../configs/dow.yaml`, `../../../../configs/pairs.yaml`, `../../../../reports/spec_review_p3.md`, `../../../../analysis/decision_table.md`, `../../../../research/canonical_rules.md`.

## 2. Step 1: what the literature says about drawing

| Quote or paraphrase | Pointer | Supports |
|---|---|---|
| "Prices are set down, giving each change of 1 point as it occurs, forming thereby lines having a general horizontal direction but running into diagonals as the market moves up and down." (nelson-1903-abc-of-stock-speculation:Q11) | Nelson Ch. IX p.42, Dow's book method | registry section 6: Dow gives no trendline or support rule, 【literature-consensus】 as history |
| Double tops observation (nelson-1903-abc-of-stock-speculation:Q14, paraphrased) | Nelson Ch. IX pp.42-43 | registry section 6 |
| A trendline "connects all the lows for an uptrend or all the highs for a downtrend" (sperandeo-123-stockjock:Q1) | Sperandeo via stockjock, trendline definition | `R-049` 【literature-consensus】 among educators; `R-050` disagreeing column (all the lows, not two) |
| A trendline is the straight line between the highest points of wave tops or the lowest points of troughs; an uptrend line joins the lows of each swing, not the highs; uptrend line from two lowest prices, downtrend line from two highest (zh-stockcloud-dow-theory-trendline:Q2, Q7, Q21, paraphrased) | stockcloud, definition and drawing sections | `R-049` |
| A valid uptrend line needs at least two rising lows (zh-stockcloud-dow-theory-trendline:Q8, paraphrased) | stockcloud, drawing section | `R-050` 【single-source】 |
| Draw on a log chart; about 45 degrees is most meaningful (zh-stockcloud-dow-theory-trendline:Q5, Q6, Q10, paraphrased) | stockcloud | `R-051`, `R-052` 【single-source】, not implemented |
| A valid crossing needs two consecutive closes on the other side; a close penetration of 3 percent or more counts; the 3 percent rule suits margined futures poorly (zh-stockcloud-dow-theory-trendline:Q14, Q17, Q19, Q18, paraphrased) | stockcloud, breakout and 3 percent sections | `R-053` 【single-source】 |
| Support and resistance lines can turn into each other (zh-stockcloud-dow-theory-trendline:Q13, paraphrased); after a return to the level that is not a false break, the resistance and support lines have reversed (oanda-bvi-dow-theory-breakout-return-moves:Q4, Q5, paraphrased) | stockcloud; OANDA | `R-054` 【literature-consensus】 among educators, not implemented |
| A resistance line joins the highs and a support line joins the lows, forming a visible shape (oanda-bvi-dow-theory-trend-continuation:Q8, paraphrased); a rectangle's resistance line joins highs and support line joins lows (oanda-bvi-dow-theory-after-breakout:Q2, paraphrased) | OANDA flag and rectangle pages | `R-049` agreeing column |
| Repeated approaches to a level met resistance and the pullback found support; horizontal support and resistance lines help find prices the market tests repeatedly (kcmtrade-dow-theory:Q9, Q19, paraphrased) | kcmtrade | `R-055` 【single-source】; no zone width |
| "The lows of secondary reactions serve as our exit point (stop-loss) when broken down" (thedowtheory-rhea-three-weeks:Q6); "(always with confirmation)" (thedowtheory-rhea-three-weeks:Q7) | Blay | `R-048` 【single-source】; nearest analogue of the defense line (`R-045` 【agent-defined】) |
| Support and resistance drawing not mentioned in the Dow chapters (edwards-magee note, rule table row `support_resistance_drawing`) | Edwards and Magee note | registry section 6 |

## 3. Step 3: support and resistance zones

| Statement | Provenance | Label |
|---|---|---|
| Tolerance 0.75 percent or 0.5 ATR, at least 2 touches, at most 4 levels | `R-047` row of the registry; `../../../../configs/dow.yaml` `levels:`; `cluster_levels` in `levels.py` | 【agent-defined】 |
| Minor swings are the input | contract Deviation 8 | 【agent-defined】 |
| Side filter: resistance from swing highs at or above the close, support from swing lows at or below it; `levels_note` when a side has fewer than `min_touches` | contract Amendment A8; `analysis.py` (`side_filter=True`, `notes`); spec review D7 | 【agent-defined】 |
| Greedy running-mean grouping can spread a cluster beyond one tolerance; the level set depends on `--start` | spec review rule-mapping row 13 | 【agent-defined】 observation |
| Zone widened to at least half a tolerance around the mean; nearest `max_levels` kept | `cluster_levels` docstring; Deviation 8 | 【agent-defined】 |

## 4. Step 4: trendlines

| Statement | Provenance | Label |
|---|---|---|
| Line through the last two confirmed secondary HL (up) or LH (down); valid if no close violates it by more than `tol_pct` between p0 and as-of | contract levels.py section; `fit_trendlines` | 【agent-defined】 mechanics around `R-049` |
| `trendline_tol_pct` 0.01 | `../../../../configs/dow.yaml` | 【agent-defined】 |
| Linear `slope_per_day`, log scale not implemented | `R-051` contract column | 【single-source】 rule, not implemented |
| Two closes or 3 percent penetration are the educator alternatives | `R-053`, stockcloud Q14, Q17, Q19 | 【single-source】 |
| Closes only for signals; trendlines may use closes or extremes | `R-036`; registry section 7 | 【literature-consensus】 |

## 5. Step 5: elements owned elsewhere

| Statement | Provenance | Owner |
|---|---|---|
| Defense line label `Dow defense line (agent-defined)`; `R-045` has no source | `chart.py` `DEFENSE_LABEL`; `R-045` row; `levels.py` `defense_line_from_state` | `dow-trend-classification`, `dow-theory-sources` |
| Line ranges shorter than 28 calendar days are not shaded | contract Deviation 12; `chart.py` `MIN_LINE_DAYS_SHOWN` | this skill (presentation), detection by `dow-confirmation-and-line` |
| Only `REVERSAL_*` and `DEFENSE_BREAK` get dotted vertical lines; line breakouts are triangles | contract Deviation 12; `chart.py` | `dow-trend-classification` for meaning |
| Pair close on a right axis; frames inner-joined on date | contract Deviation 12; `analysis.py` | this skill (presentation) |

## 6. Step 8: data labels

| Statement | Provenance | Label |
|---|---|---|
| No decision-table rule tests support, resistance or trendlines | `../../../../analysis/decision_table.md` (rules R1 to R8: trend persistence, reversal signal, confirmed vs single reversals, retracement band, Rhea window, line breakouts, volume, trading rule); `DEFENSE_BREAK` and the defense line are excluded from the family as agent-defined (section 0 and section 3) | 【insufficient-evidence】 by absence |
| R1 trend persistence (state in the chart title) and R2 reversal signal (`REVERSAL_*` markers) | `dow-trend-classification` Step 7 | 【data-confirmed】 with caveat; 【insufficient-evidence】 |
| R6 line breakout result (breakout triangles) | `dow-confirmation-and-line` Step 7 | 【insufficient-evidence】 |

## 7. Examples and Limitations

| Statement | Provenance |
|---|---|
| Example 1 levels, defense line and trendline | `python3 scripts/draw.py --source csv --csv ../../../tests/fixtures/dji_sample.csv`, run 2026-11-08 |
| Example 2 levels, `levels_note`, uptrend line 2025-04-08 to 2026-03-27, close 51,285.73 | `python3 scripts/draw.py --symbol ^DJI --pair ^DJT --start 2015-01-01`, data through 2026-11-06; asserted by `tests/test_cli.py` |
| Example 3 levels and downtrend line, close 28,725.51 | same with `--as-of 2022-09-30` |
| Legibility observations (overlapping zone labels, dense signal labels, defense annotation) | inspection of `../../../../outputs/charts/DJI_DJT_2026-11-06_pct0.03.png` and the Example 3 PNG |
| Indices unadjusted, ETF closes vendor-adjusted | `dow-swing-detection` Prerequisites; `../../../../configs/dow.yaml` `data:` |

## 8. Rule ids cited

| Id | Registry label | Used for |
|---|---|---|
| `R-036` | literature-consensus | closes only |
| `R-045` | agent-defined | defense line, by pointer |
| `R-047` | agent-defined | zone tolerance, touches, cap |
| `R-048` | single-source | secondary lows as exit point (Blay) |
| `R-049` | literature-consensus (educators) | trendline joins rising lows / falling highs |
| `R-050` | single-source | two-point minimum |
| `R-051` | single-source | log scale, not implemented |
| `R-052` | single-source | 45 degrees, not implemented |
| `R-053` | single-source | break filter alternatives |
| `R-054` | literature-consensus (educators) | role swap, not implemented |
| `R-055` | single-source | horizontal levels from repeated tests |
