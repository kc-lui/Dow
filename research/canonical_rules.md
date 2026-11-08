# Canonical Dow Theory rules (literature synthesis)

Built from the 42 notes in `research/sources/` as read on 2026-11-08. The `-v2` first-hand notes and a Poitras note did not exist when I last checked the directory. Edwards-Magee and Kirkpatrick-Dahlquist contain no retrievable text, so no rule rests on them.

## 0. Method and legend

**Labels.**
- `literature-consensus`: at least 2 independent sources agree and none contradicts.
- `literature-disputed`: at least 2 sources give materially different figures. They are shown side by side with no adjudication.
- `single-source`: one source states it, or later sources only echo that source.
- `agent-defined`: the project's own construct.

**Independence caveat.** Nearly every modern source repeats Rhea (1932), who compiled Hamilton (1922), who quoted Dow (1899 to 1902). A consensus label means the sources agree and do not conflict. It does not mean independent rediscovery. Echoes of one author, such as Blay repeating Schannep, are treated as one source.

**Provenance tags.**
- `P-Dow`: Dow's own words, seen via Hamilton, Nelson, or Bishop.
- `P-Ham`: Hamilton first-hand.
- `P-Rhea`: Rhea, only second-hand via Schannep or Bishop.
- `SEC`: secondary, textbook, academic, or encyclopedia.
- `EDU`: educator or broker.
- `MOD`: modern construct with no traceable primary source.

**Verified flag.**
- `yes`: the core figure appears in at least one `access: full-text` note (hamilton, brown-goetzmann-kumar-1998, cowles-1933).
- `partial`: some figures are verified that way and others are not.
- `no`: only `access: partial` or `search-snippet` notes support it. Many of these were tool-extracted and never re-checked against the live page.

**Algorithmizable.** `yes`, `partly`, or `no-narrative` (not measurable).

**Contract column.** This describes `docs/specs/algorithm_contract.md` as it stands. "Dev. n" refers to its Deviations list.

**Slugs.**
- Short names stand for these full slugs: hamilton = hamilton-1922-stock-market-barometer; rhea = rhea-1932-the-dow-theory; nelson = nelson-1903-abc-of-stock-speculation; dow-editorials = dow-editorials-wsj-1900-1902; brown = brown-goetzmann-kumar-1998; cowles33 = cowles-1933-can-forecasters-forecast.
- In the tables below I write every slug in full, except a few lines where `stockcharts`, `incredible`, `cmt`, and `kcm` are used as the obvious short forms of the stockcharts-chartschool, incrediblecharts, cmt-open-exam-prep, and kcmtrade slugs.

## 1. Rule registry

Columns: id | rule_key | canonical statement | figure(s) | sources agreeing | sources disagreeing | label | provenance | algorithmizable | verified | contract implementation.

For disputed rows, "agreeing" lists the grouped positions (P1, P2, and so on) with their sources. "Disagreeing" says the positions are mutually exclusive.

### 1.1 Three trends and durations

| id | rule_key | statement | figure(s) | agreeing | disagreeing | label | prov. | algo | verified | contract |
|---|---|---|---|---|---|---|---|---|---|---|
| R-001 | three_trends | Three movements run at the same time: daily/minor, secondary (reaction), primary (main). Names vary (short swing, medium swing, tertiary, minor). | 3 | hamilton:Q1,Q3,Q4,Q8; dow-editorials-wsj-1900-1902:Q1,Q2,Q4,Q5; nelson-1903-abc-of-stock-speculation:Q1-Q5; rhea-1932-the-dow-theory:Q4; brown-goetzmann-kumar-1998:Q9; stockcharts-chartschool-dow-theory:Q1-Q3; incrediblecharts-dow-theory-trends:Q1-Q3; thismatter-dow-theory:Q7; cmt-open-exam-prep-dow-theory:Q5-Q8; wikipedia-en-dow-theory:Q2,Q3,Q5; wikipedia-zh-dow-theory:Q4; rich01-what-is-dow-theory:Q5; stockfeel-dow-theory:Q3; aaii-dow-theory-21st-century:Q1-Q3; thedowtheory-basics:Q1-Q3 | none on the count; naming only | consensus | P-Dow, P-Ham, P-Rhea | partly | yes (hamilton:Q1) | Implemented as `Swing.scale` minor/secondary/primary and `detect_multiscale` (dev. 3). There is no separate primary-swing detector; primary comes from the state machine. |
| R-002 | primary_duration_min | Lower bound of a primary movement is disputed. | P1 at least 4 y; P2 at least 1 y; P3 under 1 y; P4 months | P1 at least 4 y (Dow 1900): dow-editorials-wsj-1900-1902:Q4; nelson-1903-abc-of-stock-speculation:Q4; reason-1974-dow-theory-revisited:Q2. P2 at least 1 y: hamilton-1922-stock-market-barometer:Q2; wikipedia-zh-dow-theory:Q5; wantgoo-dow-theory:Q1; stockfeel-dow-theory:Q4; zh-ctyeh-dow-theory:Q2. P3 under 1 y: rhea-1932-the-dow-theory:Q5; wikipedia-en-dow-theory:Q2. P4 months: stockcharts-chartschool-dow-theory:Q1; cmt-open-exam-prep-dow-theory:Q7; rich01-what-is-dow-theory:Q6; kcmtrade-dow-theory:Q11 | P1/P2/P3/P4 mutually exclusive | disputed | P-Dow, P-Ham, P-Rhea, EDU | no-narrative | partial (hamilton:Q2 yes; Dow only via Hamilton:Q8) | Not implemented as a duration test. Primary is a state, and `Swing.duration_days` is only recorded. |
| R-003 | primary_duration_max_typical | Dow's 1902 figure was 4 to 6 years. Hamilton rejected it as too long. | P1 4-6 y; P2 rarely 3 y, oftener under 2 y; P3 bull averaging over 2 y | P1: dow-editorials-wsj-1900-1902:Q6; nelson-1903-abc-of-stock-speculation:Q7; incrediblecharts-dow-theory-trends:Q3. P2: hamilton-1922-stock-market-barometer:Q7,Q9. P3: rhea-1932-the-dow-theory:Q10. Several years or unspecified: stockcharts-chartschool-dow-theory:Q1; wikipedia-en-dow-theory:Q2; wikipedia-zh-dow-theory:Q5; kcmtrade-dow-theory:Q11 | P1 vs P2 (hamilton:Q7 explicitly refutes P1) | disputed | P-Dow, P-Ham, P-Rhea | no-narrative | yes (hamilton:Q6,Q7) | Not implemented. |
| R-004 | primary_duration_empirical_avg | Hamilton's empirical averages for 1900 to 1923. | bull 25 months; bear 15 months | hamilton-1922-stock-market-barometer:Q13 | none | single-source | P-Ham | no-narrative | yes | Not implemented. |
| R-005 | primary_duration_unforecastable | The length and extent of a primary movement cannot be forecast in advance. | — | hamilton-1922-stock-market-barometer:Q12 (Dow, Jul 1901); rhea-1932-the-dow-theory:Q5; russell-dow-theory-letters:Q3 (primary runs until exhaustion, journalist-relayed) | none | consensus (one lineage) | P-Dow, P-Rhea | no-narrative | yes (hamilton:Q12) | Implicit only. No forecast of extent is made. |

### 1.2 Secondary reaction

| id | rule_key | statement | figure(s) | agreeing | disagreeing | label | prov. | algo | verified | contract |
|---|---|---|---|---|---|---|---|---|---|---|
| R-006 | secondary_duration_min | Minimum length of a secondary reaction is disputed. | 8 trading days; 10 days; 2 weeks; 15 days; 20 days; 3 weeks | P1 8 trading days (Schannep): thedowtheory-lines-special-issue:Q8. P2 about 10 days: dow-editorials-wsj-1900-1902:Q6 (Jan 1902); hamilton-1922-stock-market-barometer:Q6; nelson-1903-abc-of-stock-speculation:Q6; reason-1974-dow-theory-revisited:Q3; wikipedia-en-dow-theory:Q3; thedowtheory-schannep-vs-classical:Q3. P3 2 weeks (Dow Dec 1900): dow-editorials-wsj-1900-1902:Q4; hamilton-1922-stock-market-barometer:Q8; nelson-1903-abc-of-stock-speculation:Q3. P4 15 days (sagging reaction): dow-editorials-wsj-1900-1902:Q11. P5 20 days: dow-editorials-wsj-1900-1902:Q1,Q3. P6 3 weeks: rhea-1932-the-dow-theory:Q14; thedowtheory-basics:Q5; wikipedia-zh-dow-theory:Q6; wantgoo-dow-theory:Q2; stockfeel-dow-theory:Q5; zh-ctyeh-dow-theory:Q3; thedowtheory-lines-special-issue:Q9. Rhea may allow less: thedowtheory-rhea-three-weeks:Q1,Q2. Unquantified weeks: cmt-open-exam-prep-dow-theory:Q8; rich01-what-is-dow-theory:Q7; kcmtrade-dow-theory:Q12 | all positions mutually exclusive. Schannep's 8 vs 10 days differ even between two Blay pages. | disputed | P-Dow, P-Rhea, EDU | partly | partial (Dow figures via hamilton:Q6,Q8; Rhea not first-hand) | Not a filter. `duration_days` is recorded. `status_labels.secondary_duration_bounds` = literature-disputed. |
| R-007 | secondary_duration_max | Upper bound and typical length are disputed. | about 1 month; 40 d; 60 d; 3 months; several months. Typical: Dow 30-40 d, Hamilton under 40 d | P1 a month or more: dow-editorials-wsj-1900-1902:Q4; hamilton-1922-stock-market-barometer:Q8. P2 40 d (20-40 d): dow-editorials-wsj-1900-1902:Q1,Q3. P3 60 d: dow-editorials-wsj-1900-1902:Q6; hamilton-1922-stock-market-barometer:Q6; reason-1974-dow-theory-revisited:Q3. P3b: Dow's 40-60 d counter move is called exceedingly rare by Hamilton: hamilton-1922-stock-market-barometer:Q22; also zh-stockcloud-dow-theory-line:Q19 (out of context). P4 three months ("as many months"): rhea-1932-the-dow-theory:Q14; thedowtheory-basics:Q5; wikipedia-en-dow-theory:Q3; wantgoo-dow-theory:Q2; stockfeel-dow-theory:Q5. P5 several months: cmt-open-exam-prep-dow-theory:Q8; rich01-what-is-dow-theory:Q7; kcmtrade-dow-theory:Q12; zh-ctyeh-dow-theory:Q3. Typical 30-40 d: dow-editorials-wsj-1900-1902:Q6; hamilton-1922-stock-market-barometer:Q6. | P1-P5 mutually exclusive. Hamilton:Q22 contradicts the long tail of P3. | disputed | P-Dow, P-Ham, P-Rhea, EDU | partly | yes (hamilton:Q6,Q22) | Same as R-006. |
| R-008 | secondary_retracement_lower | Lower bound of retracement is disputed. | 3/8 (37.5%); 1/3 (33%); 1/2; (10% Taiwan reference, not Dow) | P1 at least 3/8 (Dow): hamilton-1922-stock-market-barometer:Q11; nelson-1903-abc-of-stock-speculation:Q8,Q9; reason-1974-dow-theory-revisited:Q1; dow-editorials-wsj-1900-1902:Q7,Q10,Q12. P2 1/3 or 33%: rhea-1932-the-dow-theory:Q14,Q15; thedowtheory-basics:Q4; aaii-dow-theory-21st-century:Q4; schannep-dow-theory-21st-century:Q4; wikipedia-en-dow-theory:Q4; wikipedia-zh-dow-theory:Q7; thedowtheory-rhea-three-weeks:Q3; thedowtheory-schannep-vs-classical:Q5; thedowtheory-lines-special-issue:Q10; stockfeel-dow-theory:Q6; dow-editorials-wsj-1900-1902:Q13. P3 at least 1/2: dow-editorials-wsj-1900-1902:Q9,Q14,Q8. Not Dow: zh-ctyeh-dow-theory:Q5 (10-20%) | P1/P2/P3 | disputed | P-Dow (3/8, 1/2); P-Rhea (33%) | yes as a measurement | partial (3/8 verified by hamilton:Q11; 33% not first-hand) | Partly. `Swing.retrace_ratio` = leg / previous opposite leg. `status_labels.secondary_retracement` = literature-disputed. |
| R-009 | secondary_retracement_upper | Upper bound of retracement is disputed. | 5/8 (62.5%); 2/3 (66%); 1/2 | P1 5/8 (Dow): dow-editorials-wsj-1900-1902:Q7,Q10. P2 66% or 2/3: rhea-1932-the-dow-theory:Q14,Q15; thedowtheory-basics:Q4; aaii-dow-theory-21st-century:Q4; wikipedia-en-dow-theory:Q4; wikipedia-zh-dow-theory:Q7; thedowtheory-rhea-three-weeks:Q3. P3 1/2: dow-editorials-wsj-1900-1902:Q12,Q13; stockfeel-dow-theory:Q6. Hamilton gives no upper bound: hamilton-1922-stock-market-barometer:Q11 | P1/P2/P3 | disputed | P-Dow, P-Rhea, EDU | yes | no | Not used. |
| R-010 | secondary_retracement_base | The measured base differs. | Rhea: the primary change since the last secondary ended. Others: the whole preceding primary swing. Dow: unspecified. | P1 since the last secondary ended: rhea-1932-the-dow-theory:Q14,Q15. P2 preceding primary swing: thedowtheory-rhea-three-weeks:Q3; thedowtheory-lines-special-issue:Q10; wikipedia-zh-dow-theory:Q7. P3 unspecified primary movement: hamilton-1922-stock-market-barometer:Q11; aaii-dow-theory-21st-century:Q4 | P1 vs P2 | disputed | P-Rhea vs EDU | yes | no | `retrace_ratio` uses the previous opposite leg. This matches neither base exactly. |
| R-011 | secondary_retracement_binding | Is a minimum retracement required? | classical 1/3 requirement vs guide only vs replaced by 3% | P1 required: thedowtheory-lines-special-issue:Q10; thedowtheory-schannep-vs-classical:Q5. P2 guide only; Rhea judged short reactions: thedowtheory-rhea-three-weeks:Q4,Q5. P3 replaced by a 3% test: thedowtheory-lines-special-issue:Q11,Q12; thedowtheory-rhea-three-weeks:Q8; schannep-dow-theory-21st-century:Q3. Dow: "at least" (hamilton-1922-stock-market-barometer:Q11) | P1/P2/P3 | disputed | EDU (Blay), SEC | partly | no | Not a filter. |
| R-012 | secondary_pullback_pct_schannep | Schannep treats a counter move as a secondary reaction when it exceeds 3% on either average. A move of at least 4% on both is usual. | >3% either; at least 4% both | schannep-dow-theory-21st-century:Q1,Q2,Q3; aaii-dow-theory-21st-century (no figure Q); echoed by thedowtheory-lines-special-issue:Q11,Q13; thedowtheory-rhea-three-weeks:Q8; thedowtheory-schannep-vs-classical:Q4 | classical 1/3 retracement test (R-011) | single-source (Schannep, echoed by Blay) | MOD (2008) | yes | no | Not implemented as a confirmation test. |
| R-013 | minor_move_filter_pct | A rally or decline counts only if the net reversal exceeds 3% of either average. | 3% | rhea-1932-the-dow-theory:Q20 (italic in Schannep; may be his emphasis; 1932 original unchecked). Schannep reuses it: schannep-dow-theory-21st-century:Q1. | The Hamilton note says it is not stated: hamilton-1922-stock-market-barometer (minor_move_filter row). Schannep says the figure is a generality, not a requirement: rhea note. Blay presents 3% as Schannep-only: thedowtheory-lines-special-issue:Q11. | single-source | P-Rhea (second-hand) | yes | no | `detect_swings(method="pct", threshold=0.03)` flips at 3% adverse close. The JSON key `hamilton_3pct_filter` is labelled consensus. That is wrong on both name and label. |
| R-014 | minor_duration | Length of a minor (day-to-day) movement is disputed. | daily; 0.5-1.5 pt daily range; hours to a month or more; days to weeks; days to 3 weeks | P1 daily: hamilton-1922-stock-market-barometer:Q4,Q6; nelson-1903-abc-of-stock-speculation:Q2; rhea-1932-the-dow-theory:Q16; stockcharts-chartschool-dow-theory:Q3; wikipedia-zh-dow-theory:Q8; aaii-dow-theory-21st-century:Q3; dow-editorials-wsj-1900-1902:Q1 (0.5 to 1.5 pt). P2 hours to a month or more: wikipedia-en-dow-theory:Q5. P3 days to weeks: rich01-what-is-dow-theory:Q8; kcmtrade-dow-theory:Q13. P4 days to 3 weeks: zh-ctyeh-dow-theory:Q4 | P1-P4 | disputed | P-Dow vs EDU | partly | yes (hamilton:Q4,Q6) | Minor scale is a threshold scale. No duration test. |
| R-015 | daily_fluctuation_low_information | Day-to-day moves are of little use except while a line forms. | — | dow-editorials-wsj-1900-1902:Q36; rhea-1932-the-dow-theory:Q16; stockcharts-chartschool-dow-theory:Q3; aaii-dow-theory-21st-century:Q3; thedowtheory-basics:Q3; wikipedia-zh-dow-theory:Q8; cmt-open-exam-prep-dow-theory:Q5 | none | consensus | P-Dow, P-Rhea | partly | no | The state machine takes secondary-scale swings only. Minor swings are not used for trend state. |

### 1.3 Trend and reversal definitions

| id | rule_key | statement | figure(s) | agreeing | disagreeing | label | prov. | algo | verified | contract |
|---|---|---|---|---|---|---|---|---|---|---|
| R-016 | trend_definition_hh_hl | A bull trend is successive rallies above prior highs with declines ending above prior lows. A bear trend is the mirror. | — | rhea-1932-the-dow-theory:Q18; dow-editorials-wsj-1900-1902:Q17 (lower highs mark a bear market, 9 May 1900), Q15,Q16 (tide stick); stockcharts-chartschool-dow-theory:Q7; incrediblecharts-dow-theory-trends:Q4,Q5,Q13; zh-stockcloud-dow-theory-trendline:Q3,Q4; kcmtrade-dow-theory:Q2-Q8; oanda-bvi-dow-theory-trend-changes:Q1,Q2; oanda-bvi-dow-theory-trend-continuation:Q2; oanda-bvi-dow-theory-breakout-return-moves:Q2; zh-ctyeh-dow-theory:Q7,Q8 | none. Hamilton does not state it in his own words. | consensus | P-Dow (single-editorial), P-Rhea | yes | no | Implemented. UNDEFINED to BULL_PRIMARY on confirmed HH then HL; HH/HL/LH/LL signals. |
| R-017 | trend_persists_until_reversal | A trend is assumed to continue until a clear reversal signal appears. | — | schannep-dow-theory-21st-century:Q7; incrediblecharts-dow-theory-trends:Q14; wantgoo-dow-theory:Q9,Q10; stockfeel-dow-theory:Q15,Q16,Q17; oanda-bvi-dow-theory-index:Q2; oanda-bvi-dow-theory-trend-changes:Q5; rich01-what-is-dow-theory:Q15; zh-ctyeh-dow-theory:Q19; wikipedia-en-dow-theory:Q15; kcmtrade-dow-theory:Q18; russell-dow-theory-letters:Q3 | none | consensus | P-Rhea lineage, no first-hand quote | partly | no | Implicit. A state persists until a `REVERSAL_*` signal. |
| R-018 | reversal_definition_swing_structure | A bull-to-bear reversal needs a failed rally high plus a decline through the prior low, confirmed by both averages. A bear-to-bull reversal is the mirror. The exact trigger is not fixed. | — | rhea-1932-the-dow-theory:Q18,Q19,Q21; stockcharts-chartschool-dow-theory:Q8; oanda-bvi-dow-theory-trend-changes:Q3,Q4; russell-dow-theory-letters:Q5 (not Russell); hamilton-1922-stock-market-barometer:Q23,Q24 (line break); thedowtheory-basics:Q9 (hold above prior lows on both) | Sperandeo's 1-2-3 is a different construct (R-056). | consensus | P-Ham, P-Rhea, EDU | partly | partial (hamilton:Q23,Q24) | Partly. `REVERSAL_DOWN` needs LH then a close below the agent-defined defense line. Non-strict mode flips on `DEFENSE_BREAK`. |
| R-019 | reversal_abrupt_resumption_slow | A change of general direction is abrupt. Resumption of the major trend is slower and is often foretold by a line. | — | hamilton-1922-stock-market-barometer:Q23 | none | single-source | P-Ham | no-narrative | yes | Not implemented. |
| R-020 | turning_points_known_in_hindsight | A top or bottom can be identified only some time after it forms. | — | dow-editorials-wsj-1900-1902:Q33,Q34 (also Q15 tide) | none | single-source | P-Dow (via Bishop) | yes | no | Implemented through `confirmed_idx` and `swings_as_of` (no lookahead). |
| R-021 | schannep_bull_bear_status_pct | Bull status needs a rise over 19%, bear status a fall over 16%. | +19% / -16% | aaii-dow-theory-21st-century:Q7,Q8; schannep-dow-theory-21st-century:Q9,Q10; thedowtheory-schannep-vs-classical:Q1; thedowtheory-basics:Q13 (19% only) | The AAII note says the traditional figure is 20%. That is a note remark with no quote and is unverified. | single-source (Schannep, echoed) | MOD | yes | no | Not implemented. |

### 1.4 Lines (sideways ranges)

| id | rule_key | statement | figure(s) | agreeing | disagreeing | label | prov. | algo | verified | contract |
|---|---|---|---|---|---|---|---|---|---|---|
| R-022 | line_definition | A line is a narrow sideways range in closing prices over enough days, read as accumulation or distribution. Dow only noted narrow ranges and never defined the term. | — | hamilton-1922-stock-market-barometer:Q10,Q15,Q24; rhea-1932-the-dow-theory:Q22,Q23; brown-goetzmann-kumar-1998:Q6; reason-1974-dow-theory-revisited:Q7; stockcharts-chartschool-dow-theory:Q10; cmt-open-exam-prep-dow-theory:Q10; nelson-1903-abc-of-stock-speculation:Q10; zh-stockcloud-dow-theory-line:Q1 | Dow never defined a line: dow-editorials-wsj-1900-1902:Q21. Schannep discards lines: thedowtheory-lines-special-issue:Q14. Not a Dow line (rectangle pattern): oanda-bvi-dow-theory-after-breakout:Q2. | consensus | P-Ham, P-Rhea | yes | yes (hamilton:Q10,Q15,Q24) | Implemented in `line.py` `detect_lines`. `status_labels.line_definition` = consensus. |
| R-023 | line_band_pct | The line range is about 5% for both averages. | ~5% | rhea-1932-the-dow-theory:Q22; thedowtheory-lines-special-issue:Q2; reason-1974-dow-theory-revisited:Q8; incrediblecharts-dow-theory-trends:Q7 (5% or less); zh-stockcloud-dow-theory-line:Q2,Q6 (centred on the mean),Q7 (empirical). Dow and Hamilton gave only point ranges: nelson-1903-abc-of-stock-speculation:Q11 (2 points); hamilton-1922-stock-market-barometer:Q10; dow-editorials-wsj-1900-1902:Q22 (within 1%, an observation), Q23. | none contradict. The 5% is explicitly a generality: zh-stockcloud-dow-theory-line:Q5,Q7,Q8. | consensus (one lineage, Rhea) | P-Rhea | yes | no (Hamilton gives points only) | Implemented: `band_pct=0.05` on (max-min)/mean for both series. Whether the 5% is a total range or plus/minus is not settled by any source. |
| R-024 | line_min_duration | A line lasts two to three weeks or longer. | 2-3 weeks | rhea-1932-the-dow-theory:Q22; thedowtheory-lines-special-issue:Q1; reason-1974-dow-theory-revisited:Q9; zh-stockcloud-dow-theory-line:Q4,Q7. Variant: zh-stockcloud-dow-theory-line:Q3 (at least 3 weeks). Hamilton: significance grows with days, no figure: hamilton-1922-stock-market-barometer:Q15 (the 66 and 71 trading-day 1914 line is a paraphrase in that note, no Qn). | none | consensus (one lineage, Rhea) | P-Rhea | yes | no | Implemented: `min_days=14` consecutive sessions (dev. 9). Sources say weeks, not sessions. |
| R-025 | line_both_averages | Both averages must be inside their range at the same time. | — | rhea-1932-the-dow-theory:Q22; thedowtheory-lines-special-issue:Q2; reason-1974-dow-theory-revisited:Q7; hamilton-1922-stock-market-barometer:Q24 (confirmation of the break) | none | consensus | P-Ham, P-Rhea | yes | no | Implemented: both series must qualify. |
| R-026 | line_breakout_meaning | A break above the range implies accumulation and higher prices. A break below implies distribution and lower prices. | — | hamilton-1922-stock-market-barometer:Q24; rhea-1932-the-dow-theory:Q23; zh-stockcloud-dow-theory-line:Q9,Q10 | Rhea Q23 says "simultaneous" breaks, but Q21 and hamilton:Q25 say same-day is not needed (see R-033). | consensus | P-Ham, P-Rhea | yes | yes (hamilton:Q24) | Implemented: first later close outside the window min/max. Emits `LINE_BREAKOUT_UP/DOWN` (dev. 9). |
| R-027 | line_break_implies_secondary_or_more | A confirmed line break signals a change of at least secondary, possibly primary, character. | — | hamilton-1922-stock-market-barometer:Q24; thedowtheory-lines-special-issue:Q5,Q6 (Blay quoting Rhea quoting Hamilton) | none | consensus | P-Ham | no-narrative | yes | Not implemented as a magnitude claim. |
| R-028 | line_breakout_3pct_filter | A line break needs a 3% penetration of the limit. | 3% | zh-stockcloud-dow-theory-line:Q12,Q13 (truncated fragments) | none | single-source | EDU | yes | no | Not implemented. Any close outside the range is a breakout. |
| R-029 | line_breakout_volume | A real breakout comes with large volume, judged relative to overall activity. | — | zh-stockcloud-dow-theory-line:Q14,Q15,Q16 | none | single-source | EDU | partly | no | Not implemented. |
| R-030 | line_breakout_measured_move | After a 5% line, expect about another 5% move. | ~5% | thedowtheory-lines-special-issue:Q7 (Blay's inference) | none | single-source | EDU | yes | no | Not implemented. |
| R-031 | line_precedes_resumption | A line often forms before the resumption of the major trend, usually after the secondary break and not before it. | — | hamilton-1922-stock-market-barometer:Q23 (the "usually after" part is a paraphrase in the hamilton note, no Qn) | none | single-source | P-Ham | no-narrative | yes (Q23) | Not implemented. |

### 1.5 Confirmation, closes, volume

| id | rule_key | statement | figure(s) | agreeing | disagreeing | label | prov. | algo | verified | contract |
|---|---|---|---|---|---|---|---|---|---|---|
| R-032 | two_average_confirmation | A move in one average is unreliable until the other average confirms it. | 2 averages | hamilton-1922-stock-market-barometer:Q17,Q21,Q24,Q25; rhea-1932-the-dow-theory:Q17,Q21; brown-goetzmann-kumar-1998:Q5; reason-1974-dow-theory-revisited:Q4,Q5; incrediblecharts-dow-theory-trends:Q11,Q15; cmt-open-exam-prep-dow-theory:Q2; wikipedia-en-dow-theory:Q10,Q11; aaii-dow-theory-21st-century:Q5,Q6,Q13; thedowtheory-basics:Q7,Q8; thismatter-dow-theory:Q10; russell-dow-theory-letters:Q1,Q2 | Origin dispute only. Bishop finds no confirmation rule in Dow's editorials: dow-editorials-wsj-1900-1902:Q19,Q20. thismatter:Q10 credits Dow. | consensus | P-Ham (not P-Dow) | yes | yes | Implemented: `pair_confirm`. `status_labels.two_average_confirmation` = consensus. |
| R-033 | confirmation_lag | Confirmation need not come on the same day or week. Taking the same direction is enough. No maximum lag is given. | no fixed window | hamilton-1922-stock-market-barometer:Q25; rhea-1932-the-dow-theory:Q21; brown-goetzmann-kumar-1998:Q5; cmt-open-exam-prep-dow-theory:Q3,Q4; thedowtheory-lines-special-issue:Q3 | rhea:Q23 says "simultaneous" (internal tension within Rhea) | consensus | P-Ham, P-Rhea | partly | yes | Implemented as `confirmation.max_days`, default None (dev. 9). |
| R-034 | confirmation_pair | The pair is Industrials and Rails/Transports. Taiwan educators adapt it to market index plus sector index. | DJI + DJT | rhea-1932-the-dow-theory:Q2; brown-goetzmann-kumar-1998:Q5; thedowtheory-basics:Q7; thismatter-dow-theory:Q10. Adaptation: wantgoo-dow-theory:Q11; stockfeel-dow-theory:Q12 | none for DJI/DJT | consensus | P-Ham, EDU | yes | yes (brown:Q5) | Implemented for ^DJI/^DJT. `--pair` defaults from `pairs.yaml` for other symbols (dev. 13). |
| R-035 | schannep_three_indices_two_confirm | Schannep uses three indices including the S&P 500 and needs two to confirm. | 3 indices, 2 confirm | thedowtheory-schannep-vs-classical:Q2 | Not found in schannep-dow-theory-21st-century. Not mentioned in thedowtheory-lines-special-issue. | single-source (promotional) | MOD | yes | no | Not implemented. `pair_confirm` takes two series. |
| R-036 | closing_prices_only | Signals use closing prices. Intraday highs and lows are ignored. | — | hamilton-1922-stock-market-barometer:Q24; rhea-1932-the-dow-theory:Q2; brown-goetzmann-kumar-1998:Q12; cmt-open-exam-prep-dow-theory:Q1; reason-1974-dow-theory-revisited:Q10; rich01-what-is-dow-theory:Q4; zh-stockcloud-dow-theory-line:Q1; russell-dow-theory-letters:Q5; sperandeo-123-stockjock:Q4 | zh-stockcloud-dow-theory-trendline:Q20 says most chartists prefer closes, which implies others use extremes. | consensus | P-Ham, P-Rhea | yes | yes (hamilton:Q24; brown:Q12) | Implemented: closes only. High/low are used only by the ATR method. |
| R-037 | volume_with_primary_trend | Volume is larger and expands in a bull market and contracts as prices fall. | — | hamilton-1922-stock-market-barometer:Q19; stockcharts-chartschool-dow-theory:Q9; cmt-open-exam-prep-dow-theory:Q9; wikipedia-en-dow-theory:Q12,Q13; rich01-what-is-dow-theory:Q13,Q14; wantgoo-dow-theory:Q8; stockfeel-dow-theory:Q13,Q14; zh-ctyeh-dow-theory:Q17; dow-editorials-wsj-1900-1902:Q27,Q28 | A rebutted claim that Dow never mentioned volume: dow-editorials-wsj-1900-1902:Q37 | consensus | P-Ham, P-Dow, EDU | partly | yes (hamilton:Q19) | `volume_confirms` compares mean volume on legs aligned with the net move against counter legs over the last four secondary swings (dev. 11). It returns None when volume is all zero, as for the index. |
| R-038 | volume_in_secondary_reaction | Volume behaviour during reactions is disputed. | rises vs dries up | P1 a sharp reaction often stimulates volume: hamilton-1922-stock-market-barometer:Q20. P2 volume dries up against the trend: cmt-open-exam-prep-dow-theory:Q9; zh-ctyeh-dow-theory:Q17,Q18; kcmtrade-dow-theory:Q16 (fading volume at highs) | P1 vs P2 | disputed | P-Ham vs EDU | partly | partial (hamilton side yes) | `volume_confirms` adopts P2. |
| R-039 | volume_overbought_oversold | An overbought market is dull on rallies and active on declines. An oversold market is the reverse. | — | rhea-1932-the-dow-theory:Q24; incrediblecharts-dow-theory-trends:Q10,Q16 (echo); dow-editorials-wsj-1900-1902:Q25 (dullness precedes advance in a bull, decline in a bear) | none | single-source (Rhea, echoed) | P-Rhea | partly | no | Not implemented. |
| R-040 | volume_leads_price | Volume peaks have led market peaks by 5.6 months on average over 14 cycles since 1900. | 5.6 months, 14 cycles | takasugi-volume-leads-price:Q2 | A different study says all but one of 27 bull tops: Notes of takasugi-volume-leads-price | single-source (undocumented) | EDU | yes | no | Not implemented. |
| R-041 | volume_not_combined_with_averages | The averages already discount volume, so volume should not be added to them as a forecasting input. | — | hamilton-1922-stock-market-barometer:Q5 | R-037 and Hamilton:Q19 treat volume as informative. | single-source | P-Ham | no-narrative | yes | Not applicable. Volume is an optional extra check. |

### 1.6 Phases

| id | rule_key | statement | figure(s) | agreeing | disagreeing | label | prov. | algo | verified | contract |
|---|---|---|---|---|---|---|---|---|---|---|
| R-042 | phases_count | Bull and bear markets each have three phases. Dow and Hamilton's book have no phase schema. | 3 | rhea-1932-the-dow-theory:Q6,Q11; brown-goetzmann-kumar-1998:Q10,Q11; stockcharts-chartschool-dow-theory (summary, Q4-Q6); wikipedia-en-dow-theory:Q6; wantgoo-dow-theory:Q4-Q6; stockfeel-dow-theory:Q8; rich01-what-is-dow-theory:Q9; zh-ctyeh-dow-theory (accumulation, euphoria, distribution, panic, despair) | wikipedia-zh-dow-theory has no phases (note) | consensus on the count only | P-Rhea; EDU | no-narrative | yes (brown:Q10,Q11) | Not implemented. |
| R-043 | phases_bull_names | Bull phase names fall into two schemes. | Rhea: revival of confidence, response to earnings, rampant speculation. Modern: accumulation, public participation, excess/distribution. | P1 Rhea: rhea-1932-the-dow-theory:Q11,Q12,Q13; brown-goetzmann-kumar-1998:Q10; incrediblecharts-dow-theory-trends:Q8. P2 modern: wikipedia-en-dow-theory:Q7,Q8; wantgoo-dow-theory:Q4,Q5,Q6; stockfeel-dow-theory:Q8-Q11; rich01-what-is-dow-theory:Q10; zh-ctyeh-dow-theory:Q10-Q13; stockcharts-chartschool-dow-theory:Q5; thismatter-dow-theory:Q8,Q9 | P1 vs P2 | disputed | P-Rhea; MOD | no-narrative | yes for P1 (brown:Q10) | Not implemented. |
| R-044 | phases_bear_names | Bear phase names fall into two schemes. | Rhea: abandonment of hopes, decreased business and earnings, distress selling. Modern: distribution, participation or panic, despair. | P1 Rhea: rhea-1932-the-dow-theory:Q7,Q8,Q9; brown-goetzmann-kumar-1998:Q11; incrediblecharts-dow-theory-trends:Q9. P2 modern: rich01-what-is-dow-theory:Q11; zh-ctyeh-dow-theory:Q14,Q15,Q16; stockcharts-chartschool-dow-theory:Q4,Q6 | P1 vs P2 | disputed | P-Rhea; MOD | no-narrative | yes for P1 (brown:Q11) | Not implemented. |

### 1.7 Agent-defined constructs

| id | rule_key | statement | figure(s) | agreeing | disagreeing | label | prov. | algo | verified | contract |
|---|---|---|---|---|---|---|---|---|---|---|
| R-045 | defense_line | The Dow defense line is the most recent secondary-reaction low in a bull trend or reaction high in a bear trend, used as a break level. No source defines or names this construct; see zh-defense-line-search-log. | none | none. Nearest analogues: secondary-reaction lows used as stop-loss (thedowtheory-rhea-three-weeks:Q6,Q7); a prior pullback low as support (zh-ctyeh-dow-theory:Q21) | zh-defense-line-search-log:Q1 (not found) | agent-defined | MOD | yes | n/a | Implemented as `TrendState.defense_line`, `DEFENSE_BREAK` with `agent_defined=True`, chart label "Dow defense line (agent-defined)", `status_labels.defense_line` = agent-defined. |
| R-046 | swing_detection_thresholds | Swing detection by percentage, ATR, or pivot, with a minor threshold of 3% and a secondary threshold of 10%. The 10% and the ATR and pivot settings have no literature source. | minor 0.03; secondary 0.10; ATR 2.0 x 14; pivot_n 5 | none. Only Rhea's 3% (R-013) is sourced. | — | agent-defined | MOD | yes | n/a | Implemented in `detect_swings` and `detect_multiscale` (dev. 2, 3). |
| R-047 | level_clustering_parameters | Support and resistance zones from clustered swings: tolerance 0.75% or 0.5 ATR, at least 2 touches, at most 4 levels. | 0.0075; 0.5 ATR; 2; 4 | none | — | agent-defined | MOD | yes | n/a | Implemented in `cluster_levels` (dev. 8). |

### 1.8 Support, resistance, trendlines, adjacent constructs

| id | rule_key | statement | figure(s) | agreeing | disagreeing | label | prov. | algo | verified | contract |
|---|---|---|---|---|---|---|---|---|---|---|
| R-048 | secondary_low_as_stop | The lows of secondary reactions serve as the exit point when broken, always with confirmation. | — | thedowtheory-rhea-three-weeks:Q6,Q7 | none | single-source | EDU | yes | no | Partly. The defense line has the same geometry but is labelled agent-defined. |
| R-049 | trendline_construction | An uptrend line joins rising lows and a downtrend line joins falling highs. | — | zh-stockcloud-dow-theory-trendline:Q2,Q7,Q21; sperandeo-123-stockjock:Q1; oanda-bvi-dow-theory-after-breakout:Q2; oanda-bvi-dow-theory-trend-continuation:Q8; oanda-bvi-dow-theory-trend-changes:Q8 (neckline) | none. Hamilton and Rhea do not mention it. | consensus (educators only) | EDU | yes | no | Implemented: `fit_trendlines` through the last two confirmed secondary HL (up) or LH (down). |
| R-050 | trendline_min_points | A valid uptrend line needs at least two rising lows. | 2 | zh-stockcloud-dow-theory-trendline:Q8 | sperandeo-123-stockjock:Q1 says "all the lows" | single-source | EDU | yes | no | Implemented with two points. |
| R-051 | trendline_log_scale | Ordinary trendlines should be drawn on a log chart. | — | zh-stockcloud-dow-theory-trendline:Q5,Q6 | none | single-source | EDU | yes | no | Not implemented. `slope_per_day` is linear. |
| R-052 | trendline_angle_45 | A trendline near 45 degrees is the most meaningful. | 45 degrees | zh-stockcloud-dow-theory-trendline:Q10 | none | single-source | EDU | partly | no | Not implemented. |
| R-053 | trendline_break_filter | A break needs two consecutive closes beyond the line, or a close penetration of at least 3%. These are alternatives. | two closes; 3% | zh-stockcloud-dow-theory-trendline:Q14,Q17,Q19; Q18 notes 3% is unsuited to margin futures | none | single-source | EDU | yes | no | Partly. A line is valid if no close violates it by more than `tol_pct=0.01` before as_of. |
| R-054 | sr_role_reversal | Broken support becomes resistance and the reverse. | — | zh-stockcloud-dow-theory-trendline:Q13; oanda-bvi-dow-theory-breakout-return-moves:Q4,Q5 | none | consensus (educators) | EDU | partly | no | Not implemented. |
| R-055 | horizontal_levels_from_tests | Horizontal levels come from repeatedly tested prices. No zone width is given. | — | kcmtrade-dow-theory:Q9,Q19 | none | single-source | EDU | yes | no | Implemented by `cluster_levels` with agent-defined tolerances (R-047). |
| R-056 | sperandeo_123_reversal | Sperandeo's 1-2-3 reversal: trendline break, failed new extreme, then a further break. Sources disagree on steps 2 and 3. | 3 steps | P1: roboforex-sperandeo-123-2b:Q1,Q2,Q3 (step 3 = break of the post-break swing). P2: sperandeo-123-stockjock:Q2,Q3,Q4 (step 2 optional, step 3 = close below the lowest low after the break) | P1 vs P2 on steps 2 and 3 | disputed | EDU (Trader Vic, not Dow) | yes | no | Not implemented. |
| R-057 | sperandeo_2b | The 2B pattern is a false-breakout reversal setup. | — | roboforex-sperandeo-123-2b:Q4; sperandeo-123-stockjock:Q5 (paraphrase) | none | consensus (educators, not Dow) | EDU | yes | no | Not implemented. |

### 1.9 Other tenets and evidence

| id | rule_key | statement | figure(s) | agreeing | disagreeing | label | prov. | algo | verified | contract |
|---|---|---|---|---|---|---|---|---|---|---|
| R-058 | primary_not_manipulable | The primary trend cannot be manipulated. Manipulation is possible in daily and, to a limited degree, secondary moves. | — | hamilton-1922-stock-market-barometer:Q18; rhea-1932-the-dow-theory:Q1; dow-editorials-wsj-1900-1902:Q35 | none | consensus | P-Ham, P-Rhea | no-narrative | yes | Not implemented. |
| R-059 | averages_discount_everything | The averages already reflect everything known. | — | hamilton-1922-stock-market-barometer:Q5,Q16; rhea-1932-the-dow-theory:Q2; dow-editorials-wsj-1900-1902:Q30,Q31,Q32; thismatter-dow-theory:Q2; wikipedia-en-dow-theory:Q9; stockfeel-dow-theory:Q2 | none | consensus | P-Dow, P-Ham, P-Rhea | no-narrative | yes | Not implemented. |
| R-060 | theory_not_infallible | The theory is not an infallible system. | — | hamilton-1922-stock-market-barometer:Q14; rhea-1932-the-dow-theory:Q3; incrediblecharts-dow-theory-trends:Q12; thismatter-dow-theory:Q3; thedowtheory-basics:Q10 | none | consensus | P-Ham, P-Rhea | no-narrative | yes | Not implemented. |
| R-061 | double_tops_bottoms | Double tops and bottoms are of little forecasting value. | — | rhea-1932-the-dow-theory:Q25. Hamilton is softer, calling them not infallible but often useful (a paraphrase in the hamilton note, no Qn). | none | single-source | P-Rhea | partly | no | Not implemented. |
| R-062 | beats_buy_and_hold | Whether Dow Theory beats buy-and-hold is disputed. See section 5. | see section 5 | P1 no raw edge: cowles-1933-can-forecasters-forecast:Q11,Q12,Q13; brown-goetzmann-kumar-1998:Q29; rich01-what-is-dow-theory:Q22. P2 risk-adjusted edge: brown-goetzmann-kumar-1998:Q30,Q31. P3 1-2% a year: aaii-dow-theory-21st-century:Q11; schannep-dow-theory-21st-century:Q11; stockcharts-chartschool-dow-theory:Q11 | P1 vs P2 vs P3 | disputed | SEC, EDU | yes (backtest) | yes (cowles33, brown) | Not in `src`. Tested in the P4 backtests. |

## 2. Agree/disagree matrix for numeric parameters

### 2.1 Secondary duration (R-006, R-007)

| source:quote | min | max | note |
|---|---|---|---|
| dow-editorials-wsj-1900-1902:Q1 | 20 d | 40 d | 12 May 1899, "longer swing" |
| dow-editorials-wsj-1900-1902:Q3 | 20 d | 40 d | 15 Jan 1900 |
| dow-editorials-wsj-1900-1902:Q4 (also hamilton:Q8, nelson:Q3) | 2 weeks | a month or more | Dec 1900 |
| dow-editorials-wsj-1900-1902:Q11 | 15 d | 30 d | 24 Nov 1900, sagging reaction |
| dow-editorials-wsj-1900-1902:Q6 (also hamilton:Q6, nelson:Q6 fragment) | 10 d | 60 d | 4 Jan 1902, average 30-40 d (avg in dow Q6 and hamilton Q6) |
| reason-1974-dow-theory-revisited:Q3 | about 10 d | 60 d | restates Dow 1902 |
| hamilton-1922-stock-market-barometer:Q22 | — | 40-60 d "exceedingly rare" | usually under 40 d |
| zh-stockcloud-dow-theory-line:Q19 | — | 40-60 d | Dow estimate, out of context |
| rhea-1932-the-dow-theory:Q14 | 3 weeks | "as many months" (3) | via Schannep; Q15 is the Bishop version of the retracement text only |
| thedowtheory-basics:Q5 | 3 weeks | "as many months" | quotes Rhea |
| wikipedia-zh-dow-theory:Q6 | over 3 weeks | — | |
| wantgoo-dow-theory:Q2; stockfeel-dow-theory:Q5 | 3 weeks | 3 months | |
| wikipedia-en-dow-theory:Q3 | 10 d | 3 months | hybrid of Dow's 10 days and Rhea's 3 months |
| cmt-open-exam-prep-dow-theory:Q8; rich01-what-is-dow-theory:Q7; kcmtrade-dow-theory:Q12 | weeks | a few / several months | |
| zh-ctyeh-dow-theory:Q3 | 3 weeks | several months | |
| thedowtheory-lines-special-issue:Q9 | 3 calendar weeks | — | "classical" |
| thedowtheory-lines-special-issue:Q8 | 8 trading days | — | Schannep |
| thedowtheory-schannep-vs-classical:Q3 | 10 d or fewer | — | Schannep |
| thedowtheory-rhea-three-weeks:Q1,Q2 | 3 weeks called "market lore" | — | a reaction may be shorter |

### 2.2 Secondary retracement (R-008 to R-011)

| source:quote | figure | note |
|---|---|---|
| hamilton-1922-stock-market-barometer:Q11 | at least 3/8 | Dow, Jul 1901; example 10 points advance gives 4 points relapse |
| nelson-1903-abc-of-stock-speculation:Q9 | at least 3/8 | fragment |
| reason-1974-dow-theory-revisited:Q1 | at least 3/8 | credited to Dow |
| dow-editorials-wsj-1900-1902:Q7 | 3/8 to 5/8 | 16 May 1899 |
| dow-editorials-wsj-1900-1902:Q10 | 3/8 to 5/8 | 24 Nov 1900 |
| dow-editorials-wsj-1900-1902:Q8 | about 1/2 | 7 Jul 1900 |
| dow-editorials-wsj-1900-1902:Q9 | at least 1/2 | 19 Oct 1900 |
| dow-editorials-wsj-1900-1902:Q12 | 3/8 to 1/2 | 22 Jan 1901 |
| dow-editorials-wsj-1900-1902:Q13 | 1/3 to 1/2 | 30 Jan 1901 |
| dow-editorials-wsj-1900-1902:Q14 | about 1/2 | 27 Mar 1901 |
| rhea-1932-the-dow-theory:Q14; Q15 | 33% to 66% of the primary change since the last secondary ended | via Schannep and Bishop |
| thedowtheory-basics:Q4; aaii-dow-theory-21st-century:Q4; schannep-dow-theory-21st-century:Q4; wikipedia-en-dow-theory:Q4 | 33% to 66% | |
| wikipedia-zh-dow-theory:Q7; thedowtheory-rhea-three-weeks:Q3; thedowtheory-schannep-vs-classical:Q5 | 1/3 to 2/3 | |
| thedowtheory-lines-special-issue:Q10 | at least 1/3 | "classical requires" |
| stockfeel-dow-theory:Q6 | 1/3 to 1/2 | |
| zh-ctyeh-dow-theory:Q5 | 10-20% | Taiwan reference, not Dow |
| cmt-open-exam-prep-dow-theory:Q8 | "a portion" | no fraction |
| schannep-dow-theory-21st-century:Q1,Q2 | over 3% on either; at least 4% on both | replaces retracement |

### 2.3 Line band percent (R-023)

| source:quote | figure | note |
|---|---|---|
| rhea-1932-the-dow-theory:Q22 | about 5% | both averages |
| thedowtheory-lines-special-issue:Q2 | about 5% | Rhea as quoted |
| reason-1974-dow-theory-revisited:Q8 | about 5% | |
| incrediblecharts-dow-theory-trends:Q7 | 5% or less | as a secondary reaction shape |
| zh-stockcloud-dow-theory-line:Q2,Q6 | 5%, centred on the mean | Q7 says empirical, Q5 and Q8 say not strict |
| nelson-1903-abc-of-stock-speculation:Q11 | 2 points | individual stock |
| hamilton-1922-stock-market-barometer:Q10 | two points | Dow 1901, individual stock |
| dow-editorials-wsj-1900-1902:Q22 | within 1% | observation of the 20-stock average, 19 Feb 1900 |
| dow-editorials-wsj-1900-1902:Q23 | 81.50 to 82.40 | 5 Apr 1900; about 1.1% by my arithmetic |
| hamilton note | 3 to 4 points (1914 line), "three points or so" (Ch. XXI) | paraphrases, no Qn, points not percent |
| contract | (max-min)/mean at most 5% | |

### 2.4 Line minimum duration (R-024)

| source:quote | figure |
|---|---|
| rhea-1932-the-dow-theory:Q22 | two to three weeks or longer |
| thedowtheory-lines-special-issue:Q1; reason-1974-dow-theory-revisited:Q9 | two to three weeks or longer |
| zh-stockcloud-dow-theory-line:Q4,Q7 | two to three weeks or longer; empirical |
| zh-stockcloud-dow-theory-line:Q3 | at least 3 weeks |
| hamilton-1922-stock-market-barometer:Q15 | no figure; significance grows with trading days |
| hamilton note (paraphrase, no Qn) | 66 and 71 trading days in 1914 |
| dow-editorials-wsj-1900-1902:Q26 | no figure; the longer a market is dull, the more important the move |
| contract | 14 sessions |

### 2.5 Minor-move filter (R-013)

| source:quote | figure | note |
|---|---|---|
| rhea-1932-the-dow-theory:Q20 | 3% net reversal of either average | defines "rally or decline" |
| schannep-dow-theory-21st-century:Q1 | over 3% on either average | secondary return move |
| thedowtheory-lines-special-issue:Q11,Q13 | over 3% | presented as Schannep's variant |
| thedowtheory-rhea-three-weeks:Q8 | 3% confirmed | Schannep rule |
| thedowtheory-schannep-vs-classical:Q4 | 3% | |
| zh-stockcloud-dow-theory-trendline:Q17 | 3% close penetration | a trendline test, different object |
| zh-stockcloud-dow-theory-line:Q12,Q13 | 3% line penetration | different object |
| hamilton-1922-stock-market-barometer | not mentioned | |
| dow-editorials-wsj-1900-1902:Q1,Q36 | daily range 0.5 to 1.5 points; day-to-day reactions not significant | no filter |
| incrediblecharts-dow-theory-trends:Q6 | "large corrections" | no figure |

### 2.6 Primary duration (R-002, R-003)

| source:quote | figure |
|---|---|
| dow-editorials-wsj-1900-1902:Q1 | "a period of years" (1899) |
| dow-editorials-wsj-1900-1902:Q4; nelson:Q4; reason-1974:Q2 | at least 4 years |
| dow-editorials-wsj-1900-1902:Q6; nelson:Q7; incrediblecharts:Q3 | 4 to 6 years |
| nelson-1903-abc-of-stock-speculation:Q16 | bull and bear runs of four and five years (fragment) |
| hamilton-1922-stock-market-barometer:Q2 | at least a year, generally much longer |
| hamilton-1922-stock-market-barometer:Q7 | before Dow never 4 to 6 years, rarely 3, oftener under 2 |
| hamilton-1922-stock-market-barometer:Q13 | bull 25 months, bear 15 months (1900-1923) |
| rhea-1932-the-dow-theory:Q5 | under a year to several years |
| rhea-1932-the-dow-theory:Q10 | bull averaging longer than two years |
| wikipedia-en-dow-theory:Q2 | under a year to several years |
| wikipedia-zh-dow-theory:Q5; wantgoo:Q1; stockfeel:Q4 | one year or more |
| zh-ctyeh-dow-theory:Q2 | 1 year to several |
| stockcharts:Q1; cmt:Q7; rich01:Q6; kcmtrade:Q11 | months to years |
| thedowtheory-flavors-iii:Q6 | Schannep trades average 2.5 years (holding period, not primary duration) |

### 2.7 Schannep variants

| variant | source:quote | classical comparator |
|---|---|---|
| 3% counter move | schannep-dow-theory-21st-century:Q1; thedowtheory-lines-special-issue:Q11,Q13; thedowtheory-rhea-three-weeks:Q8; thedowtheory-schannep-vs-classical:Q4 | 1/3 to 2/3 (thedowtheory-schannep-vs-classical:Q5); but rhea:Q20 holds a 3% filter in the same Rhea text |
| at least 4% on both averages | schannep-dow-theory-21st-century:Q2 | — |
| 8 trading days | thedowtheory-lines-special-issue:Q8 | 3 calendar weeks (thedowtheory-lines-special-issue:Q9) |
| 10 days or fewer | thedowtheory-schannep-vs-classical:Q3 | same |
| +19% bull, -16% bear | aaii-dow-theory-21st-century:Q7,Q8; schannep-dow-theory-21st-century:Q9,Q10; thedowtheory-schannep-vs-classical:Q1; thedowtheory-basics:Q13 (19% only) | AAII note says traditional is 20% (no quote, unverified) |
| three indices, two confirm | thedowtheory-schannep-vs-classical:Q2 only | two averages |
| lines discarded | thedowtheory-lines-special-issue:Q14 | lines in Rhea (rhea:Q22) |

## 3. Provenance chain

| key sentence or claim | earliest traceable | chain | flag |
|---|---|---|---|
| Three movements | Dow 12 May 1899 (dow-editorials:Q1); 15 Jan 1900 (Q2); Dec 1900 (Q4) | Dow, then Nelson (nelson:Q1-Q5), then Hamilton (hamilton:Q1,Q8), then Rhea (rhea:Q4), then educators | Bishop dates the editorial 20 Dec 1900; Hamilton and Nelson give 19 Dec. incrediblecharts:Q2 says "buying and selling" where Hamilton quoting Dow (hamilton:Q6) says "buying or selling". |
| Attributed to Dow, 31 Jan 1901 | tide analogy (dow-editorials:Q15,Q16) | | thedowtheory-basics:Q1-Q3 attributes "three movements ... most deceptive ... usually unimportant" to Dow 31 Jan 1901. That wording equals Rhea via Schannep (rhea:Q4; aaii-dow-theory-21st-century:Q1-Q3). Not traceable to Dow in the Bishop quotes. |
| Primary 4 to 6 years | Dow 4 Jan 1902 (dow-editorials:Q6) | Nelson, then rejected by Hamilton (Q7) | incrediblecharts:Q3 still repeats Dow's number. reason-1974:Q2 says "at least four years" only. |
| Secondary "ten days to sixty days, averaging thirty to forty" | Dow 4 Jan 1902 (dow-editorials:Q6) | Nelson, then Hamilton:Q6, then Hamilton:Q22 (revised) | Hamilton says the long end is rare. |
| Secondary "two weeks to a month or more" | Dow Dec 1900 (dow-editorials:Q4) | Hamilton:Q8, Nelson:Q3 | Schannep cites this as Dow's first time frame (rhea note, Q28). |
| "Three weeks to three months" | Rhea 1932: "three weeks to as many months" (rhea:Q14), read as three months | Schannep p.7 reprint, Bishop paraphrase, Russell paraphrase (rhea:Q29) | Traceable to Rhea, second-hand only. Not in Dow or Hamilton. wikipedia-en:Q3 "ten days to three months" mixes Dow and Rhea. Many Dow theorists treat the figure as cast in stone (rhea:Q27, Schannep's comment). |
| "33% to 66%" retracement | Rhea 1932 (rhea:Q14,Q15) | wikipedia-en:Q4, thedowtheory-basics:Q4, aaii:Q4 | Not Dow. Dow used 3/8 to 5/8 or about 1/2. |
| "1/3 to 2/3" | Blay and wikipedia-zh rounding of Rhea | thedowtheory-rhea-three-weeks:Q3; wikipedia-zh:Q7 | Rounded restatement. |
| "50% typical" retracement | Dow's half-rule (dow-editorials:Q8,Q9,Q14) | | No note gives "50% typical" as a modern rule. Rhea's range midpoint is not stated. Only Dow's half-rule is traceable. |
| "Three-eighths" | Dow 20 Jul 1901 (hamilton:Q11) | Nelson (Q9, possibly a gloss), Bishop 1974 (reason:Q1) | Hamilton notes it was stated for stocks, not the averages. |
| Line "5% and two to three weeks" | Rhea 1932 (rhea:Q22) | Blay, Reason footnote, incrediblecharts:Q7, stockcloud | Hamilton gives points. Dow gave no definition (dow-editorials:Q21). Schannep says percentages are a generality (rhea note). |
| Hamilton "3% filter" | Rhea (rhea:Q20, italic via Schannep) | Schannep (schannep:Q1) | Contract key `hamilton_3pct_filter` is misattributed. Hamilton:Q-none. |
| Confirmation | Hamilton (hamilton:Q17,Q21,Q24,Q25) | Rhea:Q17 | Bishop finds none in Dow (dow-editorials:Q19,Q20). thismatter:Q10 credits Dow. |
| HH/HL definition | Dow 9 May 1900 (dow-editorials:Q17) | Rhea:Q18 | Letter shorthand HH/HL/LH/LL is modern (kcmtrade:Q3-Q7). |
| Phases | Rhea (rhea:Q6-Q13) | brown:Q10,Q11, incrediblecharts:Q8,Q9 | Hamilton's 1922 book has no phase schema (hamilton note). BGK text matches Rhea but its attribution is not clear. Accumulation, participation, distribution names are not traceable to any primary source. |
| Name "Dow Theory" | Nelson footnote label (nelson note) | wikipedia-en:Q1, wikipedia-zh:Q3 say Dow never used it | wikipedia-zh:Q2 credits Hamilton, Rhea, and Schaefer with naming. This conflicts with the Nelson note. |
| Primary not manipulable | Hamilton:Q18 | Rhea:Q1 | |
| Closing prices | Hamilton:Q24 | Rhea:Q2, brown:Q12 | |

## 4. Phases by source

| source | bull phases | bear phases | label |
|---|---|---|---|
| dow-editorials-wsj-1900-1902 | none | none | — |
| hamilton-1922-stock-market-barometer | none (note) | none | — |
| rhea-1932-the-dow-theory:Q6-Q13 | revival of confidence; response to earnings; rampant speculation | abandonment of hopes; decreased business and earnings; distress selling | no-narrative |
| brown-goetzmann-kumar-1998:Q10,Q11 | same text as Rhea | same | no-narrative |
| incrediblecharts-dow-theory-trends:Q8,Q9 | reviving confidence first | abandonment of hopes first | no-narrative |
| stockcharts-chartschool-dow-theory:Q4,Q5,Q6 | accumulation, big move, excess (summary) | distribution, big move, despair (summary) | no-narrative |
| wikipedia-en-dow-theory:Q6,Q7,Q8 | accumulation, public participation, distribution | no separate sequence | no-narrative |
| thismatter-dow-theory:Q8,Q9 | phase 1 cheap buying; phase 2 economy prospers | not shown | no-narrative |
| rich01-what-is-dow-theory:Q9,Q10,Q11 | accumulation, participation, excess | distribution, participation, panic | no-narrative |
| wantgoo-dow-theory:Q4,Q5,Q6; stockfeel-dow-theory:Q8-Q11 | accumulation, public participation, distribution | none | no-narrative |
| zh-ctyeh-dow-theory:Q10-Q16 | accumulation, euphoria | distribution, panic, despair (modern additions per note) | no-narrative |
| wikipedia-zh-dow-theory | none | none | — |
| edwards-magee, kirkpatrick-dahlquist | table of contents mentions phases; names not retrieved | — | — |

## 5. Performance evidence

**Brown, Goetzmann, Kumar (1998).** Reliability: moderate. The note flags a working-paper draft.
- 255 editorials, 11 dropped (Q20); right 110, wrong 74 (Q23); Fisher test significant at 1% (Q24).
- Raw return 10.73% against 10.75% for the market (Q29). Sharpe 0.559 against 0.456, Jensen alpha 4.04%, beta 0.326 (Q30, Q31).
- Event study: bull calls +1.5%, bear calls -1.74% over 40 days (Q33); p = 0.034 (Q34).
- Out of sample is a neural-net imitation of Hamilton, not mechanical Dow rules. The next-day variant earned 9.87% geometric against 5.48% for the DJIA (note, Table IV). The note says frictions would remove most of the excess (Q41).
- Problems: the text says 9.95% where the table says 10.73%; a single scorer; the trade at the prior close may be an artefact; the benchmark excludes dividends and cash earns zero; the paper cites Cowles as 1934 (correct: 1933).

**Cowles (1933).** Reliability: high for the figures, low for the method. No risk adjustment.
- Hamilton earned 12% a year against 15.5% for buy-and-hold on industrials, with a normal return near 5% (Q11, Q12, Q14). Rails: 5.7% against 7.7% (Q15).
- Time in market: long 55%, short 16%, out 29% (Q16).
- 90 changes of position, 45 successful and 45 unsuccessful (Q21, Q26, Q27). Industrial breakdown: 29 bullish with 16 profitable, 23 bearish with 10 profitable, 38 withdrawals with 19 profitable (Q17-Q20). Rails: 41 successful, 49 not (Q22). 1909 to 1914: minus 7.8% a year versus a 5% loan (Q23).
- **Citation issues.** BGK cite 1934, and wikipedia-en:Q17 repeats "Cowles 1934" with the window "1902 to 1929". Cowles himself says December 1903 to December 1929 (Q11) and 1904 to 1929 (Q25). The cowles-1934-follow-up note finds no 1934 piece. The later paper is the 1944 Econometrica article, seen only as a snippet.
- **"Half" paraphrase.** BGK Q18 says half the changes were profitable. Cowles gives 45 and 45 out of 90 (Q21), so the paraphrase is faithful.
- The Cowles test trades rails and industrials together, so it does not test the confirmation rule.

**Sideris (UNC Wilmington, about 2008).** Unverified, unreadable PDF. No significant alpha is claimed by a search-tool paraphrase (Q4). Figures 10.21% against 11.28%, Sharpe 0.37 against 0.31, alpha minus 0.47% come from auto-summaries and conflict. Do not cite them.

**StockCharts 70-year claim.** stockcharts-chartschool-dow-theory:Q11 says a Dow Theory system beat buy-and-hold by about 2% a year over 70 years. No author or study is named. Reliability: low.

**Schannep and Blay.**
- aaii:Q11 and schannep:Q11 claim the traditional theory beat buy-and-hold by 1% to 2% a year, unsourced.
- thedowtheory-schannep-vs-classical: 32 trades against 24 (Q7); average loss minus 6.48% against minus 7.85% (Q8); 100 dollars grew to 14,973 against 8,756 (Q9); "ca. 2%" outperformance (Q10); 28.7% more profit in secular bears (Q11). Window 1954 to 2013.
- **Reliability: promotional and unverified.** The author sells Schannep's newsletter.
- My arithmetic, assuming 59 years: the terminal values imply about 8.9% against 7.9% a year, a gap near 1 point, not 2. The note does not say what the "ca. 2%" refers to.

**Other.**
- Takasugi volume lead of 5.6 months has no method (takasugi:Q2).
- wikipedia-en:Q21 states a 2% buy-and-hold gap. It matches neither Cowles's 3.5 points nor BGK's 0.02.
- rich01 Q21 and Q22 remark that risk and return is not clearly better than buy-and-hold, without a source.
- The academic-search-log finds no peer-reviewed test of Dow Theory after 1998.
- Reason 1974 reports the Barbour objection that Cowles chose an unlucky period (Q14).

## 6. Defense line and support/resistance drawing

**Negative result on the defense line.** No source defines or names this construct; see zh-defense-line-search-log.
- Eight queries were run, five standard and three extended, and none of the roughly 40 fetched pages used the term as Dow Theory vocabulary.
- Hits were military, corporate three-lines-of-defense risk models, and casual labels on trader chart ideas for neckline or moving-average levels (zh-defense-line-search-log:Q1).
- The search tool is US-only, so the conclusion is "not found", not "does not exist".
- Nearest concepts: Dow/Rhea's narrow-range line (R-022) and the Blay stop-loss on secondary lows (R-048).

**What sources do say about drawing.**
- zh-stockcloud-dow-theory-trendline (a Chinese textbook summary, book not named):
  - Join two successive rising lows for an uptrend line and two highs for a downtrend line (Q7, Q8, Q21).
  - Use a log chart (Q5, Q6) and prefer about 45 degrees (Q10).
  - A valid break needs two consecutive closes or a close beyond the line by 3% or more (Q14, Q17, Q19).
  - Support and resistance swap roles (Q13). Volume should confirm a break (Q22, Q23, Q25).
  - Q14 and Q17 are alternatives, not a combined rule.
- zh-stockcloud-dow-theory-line: the line range and its limits are breakout levels (Q9, Q10). There is no drawing procedure beyond the range definition.
- cmt-open-exam-prep-dow-theory:Q10 describes a line as a sideways pause that still needs confirmation to break. It gives no drawing rule.
- incrediblecharts-dow-theory-trends:Q7 treats a line as a shape a secondary reaction may take. It gives no S/R drawing rule.
- OANDA pages: resistance joins highs and support joins lows, with role reversal after a break (oanda-bvi-dow-theory-after-breakout:Q2; breakout-return-moves:Q4, Q5; trend-continuation:Q8). They give no drawing method.
- kcmtrade-dow-theory:Q9, Q19: horizontal levels from repeated tests, no procedure.
- Hamilton, Rhea, Nelson, and Dow's editorials contain no trendline or S/R drawing rules. Dow's tide analogy (dow-editorials:Q15, Q16) marks the high-water point only.

## 7. Gaps the algorithm must fill (no source pins these down)

- **Swing threshold.** The only numeric swing filter is Rhea's 3% (R-013, single-source, unverified against the 1932 original). The 10% secondary threshold, ATR multiple, and pivot width are agent-defined.
- **Primary versus secondary boundary.** No source gives an objective size or time cut.
- **Retracement.** Whether the base is the last uncorrected move (Rhea) or the full preceding swing. Whether the figure applies to averages or individual stocks (Dow's 3/8 was stated for stocks). Whether it is binding.
- **Confirmation window.** No maximum lag between the two averages. Rhea:Q23 says simultaneous, Q21 says not required.
- **Reversal trigger.** Order of lower high before lower low, whether equal highs count, and whether one close or two closes beyond the level is needed. The contract's strict flag has no source.
- **Closes versus extremes.** Lines and signals are on closes (R-036). Trendlines can use closes or extremes (zh-stockcloud-dow-theory-trendline:Q20 implies both exist).
- **Line geometry.** Whether 5% is a total range or plus/minus about the mean. Which base price. Sessions versus calendar weeks. Whether the range must hold at the same time in both averages. Breakout filter size, if any (R-028).
- **Trendline details.** Fit method, tolerance, linear versus log, touches needed, break filter (R-050 to R-053).
- **Support and resistance zones.** Zone width and touch count have no source (R-047).
- **Volume.** Index volume is absent for ^DJI and ^DJT. No source defines the volume metric. Hamilton and educators disagree about reactions (R-038).
- **Secondary classification.** Rhea himself had trouble deciding what counted as a secondary reaction (thedowtheory-lines-special-issue:Q15).
- **Index composition.** Constituents have changed since the early 1900s (rich01-what-is-dow-theory:Q17; stockfeel-dow-theory:Q19), which limits historical backtests.
- **Contract fixes needed.** Rename or relabel `status_labels.hamilton_3pct_filter` (single-source, Rhea via Schannep). Mark `secondary_pct` 0.10 as agent-defined. State that `volume_confirms` follows the educator reading of reaction volume, not Hamilton's.
Re-reading the seven updated notes.
Re-reading the seven updated notes.
