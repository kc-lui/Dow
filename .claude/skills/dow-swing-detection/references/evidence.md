# Evidence for dow-swing-detection

Every verbatim quote and rule id used in `../SKILL.md`, grouped by Workflow step. Quotes that SKILL.md now only points to (Rhea Q7, Schannep Q1, Blay Q8, stockfeel Q6, already quoted in `dow-theory-sources` Step 3) are kept here in full as the skill's own evidence. Quotes are copied from `../../../../research/sources/<slug>.md` and carry their `(slug:Qn)` pointer; the URL is the note's recorded source. Labels follow `../../../../research/canonical_rules.md` section 0 (definitions owned by `dow-theory-sources`). Project figures (thresholds, counts, sensitivity table) have no source note; their provenance is the file named in the row.

## Contents

1. Source URLs
2. Step 1: load bars (closing prices)
3. Step 2: detector and the Rhea filter
4. Step 3: alternation and no lookahead
5. Step 4: multi-scale nesting and threshold choice
6. Step 5: metrics and flags
7. Limitations
8. Rule ids cited

## 1. Source URLs

| Slug | Access | URL |
|---|---|---|
| rhea-1932-the-dow-theory | partial, via Wiley excerpt of Schannep 2008 and thedowtheory.com | https://catalogimages.wiley.com/images/db/pdf/9780470240595.excerpt.pdf |
| nelson-1903-abc-of-stock-speculation | full-text | https://archive.org/stream/abcofstockspecul00nelsiala/abcofstockspecul00nelsiala_djvu.txt |
| brown-goetzmann-kumar-1998 | full-text, working paper | https://chesler.us/about/about%20files/dow_theory.pdf |
| schannep-dow-theory-21st-century | partial | https://www.aaii.com/journal/article/charles-dows-theory-still-valid-for-the-21st-century |
| thedowtheory-lines-special-issue | partial | https://thedowtheory.com/dow-theory-special-issue-lines-classical-dow-theory-and-schannep/ |
| stockfeel-dow-theory | partial, Chinese | https://www.stockfeel.com.tw/%e9%81%93%e6%b0%8f%e7%90%86%e8%ab%96-%e6%b3%a2%e6%b5%aa%e7%90%86%e8%ab%96-%e6%8a%80%e8%a1%93%e5%88%86%e6%9e%90/ |

Project files cited (no source note): `../../../../docs/specs/algorithm_contract.md`, `../../../../configs/dow.yaml`, `../../../../reports/spec_review_p3.md` section 3b, `../../../../analysis/rule_status_table.md`, `../../../../src/dowtheory/swings.py`.

## 2. Step 1: load bars (closing prices)

| Quote | Pointer | Supports |
|---|---|---|
| "The fluctuations of the daily closing prices of the Dow-Jones rail and industrial averages afford a composite index of all the hopes, disappointments, and knowledge of everyone who knows anything of financial matters, and for that reason the effects of coming events (excluding acts of God) are always properly anticipated in their movement." (brown-goetzmann-kumar-1998:Q12) | Rhea's first hypothesis as quoted by Brown, Goetzmann and Kumar | `R-036` closing prices only, 【literature-consensus】 |

## 3. Step 2: detector and the Rhea filter

| Quote | Pointer | Supports |
|---|---|---|
| "a rally or a decline is one or more daily movements resulting in a net reversal of direction exceeding 3 percent of the price of either average." (rhea-1932-the-dow-theory:Q7) | Rhea, Determining the Trend, via Wiley excerpt p.9 | `R-013` minor move filter, 【single-source】; the project reuses the value as the `pct` minor threshold |

Paraphrase rows (no quote): `R-046` swing detection thresholds (minor 0.03, secondary 0.10 in the registry row; 0.08 after contract amendment A1; ATR 2.0 × 14; pivot_n 5), 【agent-defined】, provenance `../../../../docs/specs/algorithm_contract.md` Swing section, Deviations 1 to 3, Amendment A1, and `../../../../configs/dow.yaml`. The status key rename `hamilton_3pct_filter` → `rhea_3pct_filter` is contract A9.

## 4. Step 3: alternation and no lookahead

| Quote | Pointer | Supports |
|---|---|---|
| "It is often difficult to judge whether the end of an advance has come because the movement of prices is that which would occur if the main tendency had changed. Yet, it may only be an unusually pronounced secondary movement." (nelson-1903-abc-of-stock-speculation:Q9) | Dow, Jan 4, 1902, Nelson Ch. VIII p.40 | `R-020` reversal hard to tell from a secondary, 【literature-consensus】; implemented through `confirmed_idx` and `swings_as_of` |
| "The day to day movement should be disregarded by everybody, except traders, who pay no commissions. The medium swing is the one for ordinary consideration." (nelson-1903-abc-of-stock-speculation:Q3) | Dow, Dec 19, 1900, Nelson Ch. VII p.36 | `R-015` daily fluctuation low information, 【literature-consensus】; minor swings are not used for trend state |

Paraphrase rows: strict alternation, append-only pivot alternation (Deviation 1), truncation invariance and `swings_as_of` come from `../../../../docs/specs/algorithm_contract.md` and the module docstring of `../../../../src/dowtheory/swings.py`.

## 5. Step 4: multi-scale nesting and threshold choice

No source quotes. Provenance:

- `secondary_pct` 0.08, `secondary_min_sessions` 15, `per_symbol_secondary_pct`: `../../../../docs/specs/algorithm_contract.md` Amendment A1 and Deviation 15; `../../../../configs/dow.yaml`. Label `R-046` 【agent-defined】.
- Snap within two bars, later confirmation kept: Deviation 4 and `nest_scales` in `../../../../src/dowtheory/swings.py`.
- Sensitivity table (0.10, 0.08, 0.08 + 15-session filter; swings, reaction legs, retrace share, duration share, reversals, median confirmation lag): `../../../../reports/spec_review_p3.md` section 3b, ^DJI 1992 onward. Project analysis, 【agent-defined】; not a backtest result.
- Rhea's own 15-day and 5 percent statistical screen is a paraphrase-only figure in the rhea note (via Blay, unverified Fraser page), filed under `R-013`; it is cited in SKILL.md only to say that the project's 15-session filter is not sourced from it.
- Counts 450 minor and 84 secondary swings over 8775 bars, `R-046` 【agent-defined】 parameters: run of `../scripts/swings.py --symbol ^DJI --json` on 2026-11-08 against `dow.mkt_klines`.

## 6. Step 5: metrics and flags

| Quote | Pointer | Supports |
|---|---|---|
| "a secondary reaction is considered to be an important decline in a bull market or advance in a bear market, usually lasting from three weeks to as many months, during which intervals the price movement generally retraces from 33 percent to 66 percent of the primary price change since the termination of the last preceding secondary reaction." (rhea-1932-the-dow-theory:Q5) | Rhea, Secondary reaction, via Wiley excerpt p.7 | `flags.rhea_window` (`R-006`, `R-007`, 【literature-disputed】) and `flags.retrace_in_third_two_thirds` (`R-008`, `R-009`, 【literature-disputed】); the base of the retrace, `R-010`, 【literature-disputed】 |
| "It can be as short as 8 trading days (or even less following capitulation)." (thedowtheory-lines-special-issue:Q8) | Blay on Schannep secondary reactions | `flags.schannep_window` duration leg, `schannep_min_days` 8; `R-006` position P1, 【literature-disputed】 overall; Schannep's figure itself 【single-source】 |
| "that it shall exceed 3% on either of the averages." (schannep-dow-theory-21st-century:Q1) | Schannep, AAII article, secondary return move | `flags.schannep_window` amplitude leg, `schannep_min_pct` 0.03; `R-012` 【single-source】 |
| "a secondary trend will usually extend at least 4% on both the industrials and transportation averages." (schannep-dow-theory-21st-century:Q2) | Schannep, AAII article | context for `R-012`; the project uses the 3 percent figure, not the 4 percent one |
| (Chinese text, paraphrased in SKILL.md: the pullback of a secondary correction is usually about one third to one half of the prior swing) (stockfeel-dow-theory:Q6) | Taiwan educator, 論點二 | `flags.retrace_in_third_half`; `R-009` position P2, 【literature-disputed】 |

Data labels: `../../../../analysis/rule_status_table.md` rows R4 secondary_retracement (share_band 0.4091, n 44, p_holm 1.0, 【insufficient-evidence】) and R5 secondary_duration (share_rhea 0.7273, n 44, p_holm 0.31 while p_label_worst_grid 0.0443, 【insufficient-evidence】), run `a6d2d48e46014e7da3cc7c6be7ce8a02`, specification `pct0.03/0.08f15`. Authority: `dow-rule-backtest`.

## 7. Limitations

- In-sample tuning and the 46 percent ceiling of reactions inside the 1/3 to 2/3 band: `../../../../reports/spec_review_p3.md` section 3b judgement list, 【agent-defined】.
- One-day secondary leg example (^DJI 2020-03-12 L, 2020-03-13 H confirmed 2020-04-03): run of `../scripts/swings.py --symbol ^DJI --start 2020-01-01 --end 2021-12-31 --scale secondary` on 2026-11-08.
- `^DJI` and `^DJT` history begins 1992-01-02: `../../../../analysis/rule_status_table.md` header and the ClickHouse coverage row of the integrity report.
- All series unadjusted (`auto_adjust=False`): `../../../../src/dowtheory/data/yahoo_fetcher.py`; INDEX versus NYSEARCA split: `../../../../configs/dow.yaml` `exchange_map`. ETF closes embed ex-dividend drops; indices carry no dividend cash.
- Schannep flag unit mismatch (calendar `duration_days` against a trading-day figure): `secondary_flags` in `../../../../src/dowtheory/swings.py` and `compute_secondary_metrics` (calendar days), 【agent-defined】 approximation under `R-046`.
- `snapped` recomputed in `../scripts/swings.py` as the existence of a minor swing with the same bar and kind; exact because an unsnapped secondary swing has no same-kind minor swing within two bars (Deviation 4).

## 8. Rule ids cited

| Id | Key | Registry label | Used for |
|---|---|---|---|
| R-006 | secondary_duration_min | disputed | `flags.rhea_window`, `flags.schannep_window`, `duration_days`; data label R5 |
| R-007 | secondary_duration_max | disputed | same |
| R-008 | secondary_retracement_lower | disputed | `flags.retrace_in_third_two_thirds`; data label R4 |
| R-009 | secondary_retracement_upper | disputed | `flags.retrace_in_third_two_thirds`, `flags.retrace_in_third_half` |
| R-010 | secondary_retracement_base | disputed | `retrace_ratio` base |
| R-011 | secondary_retracement_binding | disputed | data label R4 mapping |
| R-012 | secondary_pullback_pct_schannep | single-source | `flags.schannep_window` amplitude leg |
| R-013 | minor_move_filter_pct | single-source | 3 percent `pct` threshold; Rhea's 15-day and 5 percent screen |
| R-015 | daily_fluctuation_low_information | consensus | minor swings not used for trend state |
| R-016 to R-018, R-045 | trend definition, reversal, defense line | consensus / disputed / agent-defined | Boundaries table only, handed to `dow-trend-classification` |
| R-020 | reversal_hard_to_tell_from_secondary | consensus | `confirmed_idx`, `swings_as_of` |
| R-022 to R-035 | lines and confirmation | various | Boundaries table only, handed to `dow-confirmation-and-line` |
| R-036 | closing_prices_only | consensus | close-only detection |
| R-046 | swing_detection_thresholds | agent-defined | every threshold, the time filter, nesting, counts |
| R-047, R-049 to R-055 | levels and drawing | agent-defined / various | Boundaries table only, handed to `dow-levels-and-chart` |
