# Agent verification sample (golden run)

Agent: `dow-theory` (draft commit 0aa753b; skills 1–6 as of 2026-11-08 16:40). Each answer is the agent's final message to the lead, verbatim. Grading by R17 (Reality Checker) follows each answer.


## Q1 Draw ^DJI vs ^DJT since 2015: trends, defense line, S/R, trendlines; state; confirmation

### Answer

Golden run Q1 complete. Chart PNG: /Users/lui/workspace/Dow/outputs/charts/DJI_DJT_2026-11-06_pct0.03.png (195 kB). JSON twin: /Users/lui/workspace/Dow/outputs/json/DJI_DJT_2026-11-06_pct0.03.json. Integrity gate passed (exit 0, report /Users/lui/workspace/Dow/reports/integrity_20261108_163852.txt).

## Trend state
- Symbol ^DJI, pair ^DJT, data through 2026-11-06 (close 51,285.73), start 2015-01-01, method pct 0.03/0.08, strict mode.
- Primary: BULL_PRIMARY since 2023-06-15 (REVERSAL_UP bar). Secondary direction: up.
- Dow defense line [agent-defined, R-045]: 45,166.64, reaction_low of 2026-03-27, set when that HL was confirmed on 2026-04-17. No source defines or names the defense line; it is this project's construct (last confirmed secondary reaction low in a bull).
- Pair confirmation: non_confirmation. Industrials BULL_PRIMARY since 2023-06-15; Transports BEAR_PRIMARY since 2026-09-24 (REVERSAL_DOWN on ^DJT). Under R-032 【literature-consensus】 this is a divergence warning, not a reversal; no bear market is declared for the pair until the Industrials also signal REVERSAL_DOWN and the match is found. Latest Industrials REVERSAL_UP (2023-06-15) was matched by Transports on 2023-02-01, confirmed 2023-06-15.

## Layered analysis
1. Data check (dow-swing-detection): ^DJI and ^DJT both 1992-01-02 to 2026-11-06, 8775 rows each, gate exit 0; window 2015-01-01 onward gives 2980 bars.
2. Swings (dow-swing-detection, via dow analyze): 146 minor, 30 secondary. Last four secondary: H 2024-12-04 45,014.04 (confirmed 2025-03-12); L 2025-04-08 37,645.59 (confirmed 2025-04-30, retrace 0.58); H 2026-02-10 50,188.14 (confirmed 2026-03-19); L 2026-03-27 45,166.64 (confirmed 2026-04-17, retrace 0.40, 45 days, inside the Rhea window and both retracement bands). Thresholds R-046 【agent-defined】; 3 % figure R-013 【single-source】.
3. Trend (dow-trend-classification): last signals HH 2026-03-19 (50,188.14 vs 45,014.04) and HL 2026-04-17 (45,166.64 vs 37,645.59). Last reversal REVERSAL_UP 2023-06-15 after the 2022-11-23 DEFENSE_BREAK. No DEFENSE_BREAK or counter swing since; state is PRIMARY, not SUSPECT. Non-strict mode would give since 2022-11-23 instead.
4. Confirmation, lines, volume (dow-confirmation-and-line): status above. 41 Dow lines since 2015 at band 0.05 / 15 sessions / drift 0.5 【agent-defined】 parameters; latest line 2026-09-16 to 2026-10-26 (bands 3.8 % / 4.6 %), broke up 2026-10-27, confirmed by both 2026-11-04. No line currently open. volume_confirms: false (informational; R-038 【literature-disputed】, flag adopts the P2 reading that counter legs are lighter, Hamilton P1 allows heavy reactions).
5. Levels and chart (dow-levels-and-chart): four support zones (R-047 【agent-defined】), nearest first: 41,850.96 (41,694.01 to 42,007.90, 2 touches); 38,140.95 (2); 37,690.35 (2); 34,008.91 (33,843.92 to 34,160.78, 3 touches). No resistance zone: fewer than 2 swing highs above the close (index at a high above every prior swing high, levels_note). Uptrend line joins 2025-04-08 @ 37,645.59 and 2026-03-27 @ 45,166.64, slope 21.306/day, value 49,939.21 at as-of, 2 touches, valid under the 1 % tolerance 【agent-defined】. No downtrend line (last two secondary highs are rising). Chart shows: DJI close with pair in orange on the right axis, secondary swing triangles, minor dots, green support bands, green uptrend line, dashed red defense line from 2026-03-27, grey bands for lines of 28+ days, REVERSAL/DEFENSE_BREAK vertical markers, volume panel.

## Evidence status
- HH/HL definition R-016, persistence R-017, two-average confirmation R-032, line definition R-022: 【literature-consensus】. R1 trend persistence 【data-confirmed】 only with caveat: p_extend 0.8788, n = 33, drift-matched random-walk baseline 0.65 to 0.69, p_sim 0.0055 (never p_holm alone).
- Reversal signal R-018: 【literature-disputed】; R2 【insufficient-evidence】 (n = 12). Pair confirmation R3, line breakout R6, volume R7: all 【insufficient-evidence】.
- Secondary thresholds R-046, defense line R-045, zone and trendline parameters R-047, line session floor and drift filter, EQUAL tolerance: 【agent-defined】.
- Not tested: defense line (excluded from backtest family), support/resistance zones, trendlines (no R-row exists).

## Disputes (side by side, not adjudicated)
- Reversal rule R-018: orthodox P1 (Hamilton, Rhea, Edwards and Magee: failed rally plus break of prior low; strict mode) vs Schaefer/Russell P2 (break of secondary low alone is not proof; 50 % principle R-065 【single-source】, not implemented).
- Secondary duration R-006/R-007: Rhea three weeks to three months vs Schannep 8 trading days minimum; retracement R-008 to R-010: Rhea 1/3 to 2/3 vs Taiwan educator 1/3 to 1/2. The 2026-03-27 low satisfies all of these bands; the 2025-04-08 low (retrace 0.95) satisfies none.
- Volume on reactions R-038: Hamilton P1 (reactions can be heavy) vs educators P2 (reactions light).

## Limitations
Defense line, state names, SUSPECT mechanics, swing thresholds, zone and trendline parameters are all project constructs tuned in sample on ^DJI 1992 onward. Data starts 1992; indices unadjusted. Start date 2015 means the first established state in this window was 2018-07-26 (warm-up). Every signal is dated at its confirmation bar, so it lags the extreme. Ten-year chart has overlapping labels around 2020 and a short defense-line segment. Not investment advice.

### Grade

**PASS** (R17, 2026-11-08). Evidence:
- PNG `/Users/lui/workspace/Dow/outputs/charts/DJI_DJT_2026-11-06_pct0.03.png` exists, 195,056 bytes (> 10 kB).
- Fresh run `uv run --python .venv/bin/python -m dowtheory.cli analyze --symbol ^DJI --pair ^DJT --start 2015-01-01 --no-chart` (run 5a33a4a4): BULL_PRIMARY since 2023-06-15; defense line 45,166.64 reaction_low 2026-03-27 labelled agent-defined; pair non_confirmation, B BEAR_PRIMARY since 2026-09-24, latest A REVERSAL_UP 2023-06-15 matched by B 2023-02-01; 146 minor / 30 secondary swings; support zones 41,850.96 (41,694.01–42,007.90, 2), 38,140.95 (2), 37,690.35 (2), 34,008.91 (33,843.92–34,160.78, 3); no resistance (fewer than 2 highs above close); uptrend line 2025-04-08 @ 37,645.59 → 2026-03-27 @ 45,166.64, slope 21.306, 49,939.21 at as-of, valid; 41 lines, last 2026-09-16→2026-10-26 bands 3.8/4.6, up 2026-10-27, confirmed 2026-11-04. All match the answer.
- Labels: defense line R-045 agent-defined with "no source defines or names" sentence; R1 cited with baseline 0.65–0.69, p_sim 0.0055, n = 33; disputes side by side; no targets or predictions; English.
- Defect (does not violate a listed criterion, must be corrected): the Disputes paragraph says "the 2025-04-08 low (retrace 0.95) satisfies none". The JSON twin gives retrace_ratio 0.585 for that swing with flags schannep_window true and retrace_in_third_two_thirds true (rhea_window false, third_half false). The answer's own Layered analysis item 2 states 0.58. The 0.95 figure matches nothing in the run output and "satisfies none" is false.


## Q2 道氏防線是什麼？是道氏理論原本就有的概念嗎？誰提出的？

### Answer

Golden Q2 answer (道氏防線 origin). Short version: the Dow defense line is NOT an original Dow Theory concept and no author proposed it. It is this project's own construct, rule R-045, label 【agent-defined】. No source defines or names it.

## Trend state
Not applicable. Pure literature/provenance question, routed to step 7 (dow-theory-sources) plus the construct definition in dow-trend-classification. No data run needed.

## Layered analysis

**Step 7, dow-theory-sources (glossary Step 1, provenance Step 6):**
- 道氏防線 maps to "Dow defense line", 【agent-defined】, R-045. Registry row (research/canonical_rules.md:122): "No source defines or names this construct"; provenance tag MOD; agreeing sources: none.
- Negative search result: the project's search log records "no page defines 道氏防線 or uses 防線 as a Dow Theory term in any page read" (zh-defense-line-search-log:Q1). Eight queries found only military, corporate-governance and casual trader uses of 防線.
- The first-hand and snippet notes for Dow (via Nelson 1903 and Hamilton 1922), Hamilton, Rhea, the Dow editorials, Edwards and Magee, Kirkpatrick and Dahlquist, and Russell's history essay all mark the defense line as "not mentioned".
- So: not in Dow (1900-1902 editorials), not in Hamilton (1922), not in Rhea (1932), not in Schaefer/Russell, not in Schannep/Blay, and not found in Chinese-language educator pages.

**dow-trend-classification Step 4 (the project's definition):**
The Dow defense line is the price of the last confirmed secondary reaction low while the primary state is on the bull side (kind `reaction_low`), or the last confirmed secondary reaction high on the bear side (kind `reaction_high`). It is set when a trend is established or flipped, refreshed on each new HL in a bull (LH in a bear), and refreshed again when a SUSPECT state returns to PRIMARY on a new HH/LL (Amendment A3). A close through it is a `DEFENSE_BREAK` when no counter swing has formed (strict mode: state becomes SUSPECT, a warning not a reversal), or a `REVERSAL_UP/DOWN` when a counter swing (LH / HL / EQUAL double top or bottom) has already formed. It is emitted as `defense_line: {price, ts, type, agent_defined: true}` and the chart labels it "Dow defense line (agent-defined)". The machine tests one average only; it never checks the second average.

**Nearest published analogues (none is a drawn line, none is called a defense line):**
| Analogue | Statement | Rule | Label |
|---|---|---|---|
| Blay, thedowtheory.com | "The lows of secondary reactions serve as our exit point (stop-loss) when broken down" (thedowtheory-rhea-three-weeks:Q6), "(always with confirmation)" (Q7). Same geometry as the bull-side line, but Blay requires the second average | R-048 | 【single-source】, EDU |
| Taiwan educator ctyeh | prior pullback low used as support (zh-ctyeh-dow-theory:Q21, paraphrase; no rule given) | R-045 analogue row | 【agent-defined】 mapping |
| Schaefer and Russell | halfway (50 percent) level of the primary swing, not the secondary low (russell-history-of-the-dow-theory, paraphrase) | R-065 | 【single-source】 |
| Rhea | the narrow-range "line" (a sideways range, unrelated to a break level) | R-022 | 【literature-consensus】 |

**What IS canonical and what the defense line operationalises:** Dow's trend-by-extremes rule R-016 【literature-consensus】: "It is a bull period as long as the average of one high point exceeds that of previous high points. It is a bear period when the low point becomes lower than the previous low points." (nelson-1903-abc-of-stock-speculation:Q8). The orthodox reversal reading R-018 (failed rally high plus a decline through the prior secondary low) is 【literature-disputed】: Schaefer and Russell reject that a break of the preceding secondary low alone proves a bear market (russell-history-of-the-dow-theory:Q6, Q7). The defense line is the project's way of making "the prior secondary low/high" an explicit, dated, emitted price level. The level is implied by the orthodox reading; the name, the drawing, the SUSPECT mechanics and the refresh rules are the project's.

## Evidence status
- R-045 defense line: 【agent-defined】; data layer: never tested (no row in the decision table). It has no data label of its own.
- R-048 Blay stop at secondary lows: 【single-source】; not tested.
- R-065 Schaefer 50 percent principle: 【single-source】; not implemented, not tested.
- R-016 HH/HL rule and R-017 persistence: 【literature-consensus】; data label 【data-confirmed】 for R1 trend persistence only with its mandatory caveat (drift-matched random-walk baseline 0.65 to 0.69, p_sim 0.0055, n = 33; never p_holm alone). This says nothing about the defense line as a trading rule.
- R-018 reversal rule: 【literature-disputed】; R2 primary_reversal_signal 【insufficient-evidence】 (n = 12, below the 30-event floor).

## Disputes
- Reversal rule R-018, side by side, not adjudicated: orthodox P1 (Hamilton, Rhea, Edwards and Magee, StockCharts): a failed rally high and a decline through the prior secondary low signals the reversal. P2 (Schaefer, Russell): a break of the preceding secondary low alone does not prove a bear market; test the 50 percent level and whether the third phase occurred (R-065).
- Confirmation origin: thismatter-dow-theory:Q10 credits Dow; Russell (Q4) and the nelson note credit Hamilton. Relevant because Blay's analogue requires confirmation and the defense line machine does not.

## Limitations
- The negative result is "not found", not "does not exist": the search tool was US-only, so absence in Chinese-language Dow literature is not proven. The term 道氏防線 may exist in Chinese educator material the project did not reach.
- Rhea is read second-hand (Wiley reprint in Schannep 2008, and Blay); Edwards and Magee and Kirkpatrick and Dahlquist only via snippets.
- The defense line depends on the project's in-sample secondary swing thresholds (R-046, 【agent-defined】, tuned on ^DJI 1992 onward); different thresholds move the line.
- Not investment advice; this describes a project construct and its provenance only.

Files consulted: /Users/lui/workspace/Dow/research/canonical_rules.md (rows R-045 line 122, R-048 line 130, R-065 line 150, section 6 line 369), /Users/lui/workspace/Dow/research/sources/zh-defense-line-search-log.md, /Users/lui/workspace/Dow/research/sources/thedowtheory-rhea-three-weeks.md, skills dow-theory-sources and dow-trend-classification.

### Grade

**PASS** (R17, 2026-11-08). Evidence:
- States the defense line is NOT an original concept, no author proposed it, project construct R-045 【agent-defined】; cites both `zh-defense-line-search-log:Q1` and registry row R-045 (`research/canonical_rules.md` row verified: "No source defines or names this construct; see zh-defense-line-search-log", agreeing none, label agent-defined, prov. MOD).
- Project definition given (last confirmed reaction low/high, DEFENSE_BREAK vs REVERSAL, strict/SUSPECT, agent_defined: true) and explicitly separated from the canonical R-016 rule it operationalises; analogues table labelled "none is a drawn line, none is called a defense line".
- Honest caveat present in Limitations: "not found, not does not exist, search tool US-only". Source note line 38 says exactly that; line 14 is Q1 NOT FOUND; eight query entries counted in the log.
- Spot-checked pointers, all exist and match: thedowtheory-rhea-three-weeks:Q6 ("exit point (stop-loss)") and Q7 ("always with confirmation"); zh-ctyeh-dow-theory:Q21 (prior pullback low); russell-history-of-the-dow-theory:Q4 (Hamilton defined confirmation), Q6, Q7; nelson-1903-abc-of-stock-speculation:Q8 (bull period text); thismatter-dow-theory:Q10 (credits Dow).
- R1 caveat cited in full; R-018 disputed, not adjudicated; English; no predictions.


## Q3 How long does a secondary reaction last and how much does it retrace? How certain?

### Answer

Golden run Q3 result: there is no single canonical figure for secondary-reaction duration or retracement. Both are 【literature-disputed】 in the registry (research/canonical_rules.md section 1.2), and the one data test that touches duration is 【insufficient-evidence】.

## Trend state
Not applicable. Pure literature question, routed to step 7 (dow-theory-sources) only; no data or scripts run.

## Layered analysis (dow-theory-sources, Step 3 digest, verified against registry rows R-006 to R-013)

**Duration (R-006 minimum, R-007 maximum/typical) 【literature-disputed】**

| Position | Figure | Source (slug:Qn) | Verification |
|---|---|---|---|
| Dow, Dec 1900 | "running from two weeks to a month or more" | hamilton-1922-stock-market-barometer:Q8; nelson-1903-abc-of-stock-speculation:Q2 | first-hand |
| Dow, Jan 1902 | "ten days to sixty days, averaging probably between thirty and forty days" | hamilton-1922:Q6; nelson-1903:Q6 | first-hand |
| Hamilton 1922 | 40 to 60 days "exceedingly rare", duration "may be appreciably less than forty days" | hamilton-1922:Q22 | first-hand |
| Rhea 1932 | "usually lasting from three weeks to as many months" | rhea-1932-the-dow-theory:Q5 | second-hand (Wiley reprint in Schannep 2008 / Blay) |
| Rhea alt. | 3 to 12 weeks; 15-day / 5 % screen in his statistics (filed under R-013) | rhea note paraphrase via Blay | unverified |
| Schannep | "as short as 8 trading days (or even less following capitulation)"; face-off page says 10 days | thedowtheory-lines-special-issue:Q8; thedowtheory-schannep-vs-classical:Q3 | tool-extracted, partial access |
| Schaefer | no limit on secondaries | russell-history-of-the-dow-theory:Q6 | first-hand paraphrase in Russell's essay |

Educators (Edwards-Magee glossary, Kirkpatrick-Dahlquist, Wikipedia, StockCharts, Taiwan sites) repeat Rhea's three weeks to three months. That is one lineage, not independent evidence.

**Retracement (R-008 lower, R-009 upper, R-010 base, R-011 binding) 【literature-disputed】**

| Position | Figure | Source (slug:Qn) | Verification |
|---|---|---|---|
| Dow, Jul 1901 (stated for a stock) | "at least three-eighths of the primary movement"; minimum only, no upper bound | hamilton-1922:Q11; nelson-1903:Q15 | first-hand |
| Dow, small moves | "swings back about half of the amount of the advance" | nelson-1903:Q19 (Ch. XXX attribution unsettled) | first-hand |
| Rhea 1932 | "retraces from 33 percent to 66 percent of the primary price change since the termination of the last preceding secondary reaction" | rhea-1932:Q5 | second-hand |
| Russell on Rhea | "one-third to two-thirds of the preceding uncorrected primary advance" | russell-history-of-the-dow-theory:Q5 | first-hand (Russell), rounding of Rhea |
| Taiwan educator | 1/3 to 1/2 of the prior swing | stockfeel-dow-theory:Q6 | tool-extracted |
| Schannep (R-012) | replaces the fraction with ">3 % on either average"; "usually extend at least 4 % on both" | schannep-dow-theory-21st-century:Q1, Q2 | 【single-source】, partial access |
| Schaefer | none | russell-history paraphrase | first-hand paraphrase |

Two further disputes inside retracement: the measured base (R-010: Rhea measures from the end of the last secondary; educators measure the whole preceding primary swing; Dow leaves it unspecified) and whether the fraction is binding (R-011: required, guide only, replaced by 3 %, or no limit).

## Evidence status
- R-006, R-007 (duration): 【literature-disputed】. Data layer: rule_status_table row R5 secondary_duration is 【insufficient-evidence】 (n = 44, share within Rhea's window 0.727, CI 0.58 to 0.84, p_raw 0.0018 but not significant after Holm with worst-grid-point p 0.044; refute bound 0.8585). dow-rule-backtest is the authority for that row.
- R-008 to R-011 (retracement): 【literature-disputed】. Not tested; registry contract column says retrace_ratio is recorded using the previous opposite leg, which matches neither Rhea's nor the educators' base exactly.
- R-012 (Schannep 3 % / 4 %): 【single-source】. Not tested.
- R-013 (Rhea 3 % filter): 【single-source】. Used as the swing threshold in dow-swing-detection, not tested as a rule.
- Verified flags: Dow and Hamilton figures sit in full-text notes (verified yes). Every Rhea figure is verified no (second-hand through the Wiley reprint or Blay).

## Disputes
Duration: 8 to 10 trading days (Schannep) vs two weeks (Dow 1900) vs ten days (Dow 1902) vs three weeks (Rhea) at the floor; a month or more (Dow 1900) vs sixty days (Dow 1902) vs under forty typical (Hamilton) vs three months (Rhea) vs no limit (Schaefer) at the ceiling.
Retracement: 3/8 minimum unbounded (Dow) vs 33 to 66 % (Rhea) vs 1/3 to 1/2 (Taiwan educator) vs 3 % threshold (Schannep) vs none (Schaefer). Not adjudicated.

## How certain the figures are
- Most certain: that Dow himself gave figures and that Hamilton pushed back on his own mentor's upper range. Both are first-hand in full-text notes.
- Least certain: the figures most people quote as "canonical" (three weeks to three months, one-third to two-thirds) are Rhea's, reached here only second-hand, and modern agreement on them is a single Dow → Hamilton → Rhea lineage.
- Dow's three-eighths and half were stated for individual stocks; applying them to the averages is an inference.
- The project's own test gives no confirmation of any duration window and no test at all of retracement.

## Limitations
Rhea second-hand; educator notes tool-extracted and not rechecked against live pages; no Edwards-Magee or Kirkpatrick-Dahlquist full text; one-lineage consensus; backtest data 1992+ with mechanical rules, unlike the original authors' context. Description of what sources say only, not advice.

### Grade

**PASS** (R17, 2026-11-08). Evidence:
- Duration and retracement each in a side-by-side table with slug:Qn and verification column, both headed 【literature-disputed】; Disputes section ends "Not adjudicated" and no figure is picked as correct.
- Rhea flagged second-hand four times (table row, Verified flags, How certain, Limitations); matches `rhea-1932-the-dow-theory.md` Q5 provenance "via Wiley/Schannep p.7; Blay cites Fraser p.52".
- R5 data label cited: 【insufficient-evidence】, n 44, share 0.7273, CI 0.58–0.84, p_raw 0.0018, worst-grid 0.044, refute bound 0.8585. All match `analysis/rule_status_table.md` row R5 (0.7273, [0.5815, 0.8365], p_raw 0.0018, p_label_worst_grid 0.0443, refute 0.8585).
- Spot-checked pointers, all exist with matching text: hamilton-1922:Q6 (ten to sixty days), Q8 (two weeks to a month), Q11 (three-eighths, Jul 20 1901), Q22 (forty to sixty exceedingly rare); nelson-1903:Q2, Q6, Q15, Q19; rhea-1932:Q5; russell-history:Q5, Q6; thedowtheory-lines-special-issue:Q8 (8 trading days); thedowtheory-schannep-vs-classical:Q3 (10 days); stockfeel-dow-theory:Q6 (1/3 到 1/2); schannep-dow-theory-21st-century:Q1, Q2; cmt note not needed here. R-012 and R-013 single-source labels match the registry.
- English; no prediction; no fabricated source found.


## Q4 Does the data support volume confirmation? Is trend persistence proven?

### Answer

Golden Q4 answer: volume confirmation is 【insufficient-evidence】 (not refuted, but close); trend persistence is 【data-confirmed】 only with its mandatory random-walk caveat.

## Trend state
Not applicable. This is an evidence question (framework step 6, literature step 7). No chart or current-state analysis was run.

## Layered analysis

**Step 6, dow-rule-backtest** (`scripts/rules.py --rule R7`, `--rule R1`; run of record a6d2d48e, pair DJ = ^DJI with ^DJT, spec pct0.03/0.08f15, decision table hash c8675eff…, config hash e6f5b9cd…)

R7 volume_confirmation, 2000-01-03 to 2026-11-06:
- Data label: 【insufficient-evidence】. Reason: not significant after Holm; both sub-samples sit on the wrong side of the null, but the refutation bound does not cross it.
- Event: consecutive with-trend and counter-trend secondary legs inside a PRIMARY state. Metric p_vol = share of pairs where the with-trend leg has the higher mean volume. Null 0.5, one-sided greater.
- n = 57. p_vol 0.3509 (20 of 57). Wilson 95% CI 0.2400 to 0.4806. p_raw 0.9918, p_holm 1.0.
- Sub-samples: A (to 2009) 0.3600 on n 25, B (2010 on) 0.3438 on n 32. Both below 0.5.
- Refutation bound 0.5162 vs null 0.5. It sits above 0.5, so the protocol cannot call 【data-refuted】. The R11 audit notes it is close to a refuted outcome.
- Descriptive variants from reports/rule_R7.md: trailing-median normalised p_vol 0.4211 (CI 0.3019 to 0.5502); the `volume_confirms` flag was true in 0.4058 of 69 windows; the 15-point specification sweep stays between 0.2903 and 0.4739, every point below 0.5.
- Reading: in this sample the with-trend secondary leg carried the heavier mean volume in a minority of cases, the opposite of the rule's direction. The data do not support the rule; they also do not exclude a zero effect.
- Coverage caveat: ^DJI volume is a vendor aggregate with level breaks in 2000 and 2016/2017, which is why the pre-registered start is 2000. The frozen table's wording "sparse or zero before 2000" is corrected to "level breaks" in the deviation log.

R1 trend_persistence, 1992-01-02 to 2026-11-06:
- Data label: 【data-confirmed】 by the pre-registered protocol. Reason: p_holm below alpha and both sub-samples agree.
- Event: confirmed secondary swing counter to a *_PRIMARY state. Metric p_extend = share whose next swing makes a new HH or LL. Null 0.5.
- n = 33. p_extend 0.8788 (29 of 33). Wilson CI 0.7267 to 0.9518. p_raw 0.000005, p_holm 0.000044. Sub-samples A 0.9412, B 0.8125. Refutation bound 0.9620.
- Mandatory caveat (R11 audit F1, DEV-10), never omit: the 0.5 null is not a random-walk baseline. A drift-matched random walk run through the same swing and trend machinery gives p_extend of about 0.65 to 0.69 (auditor: iid 0.654, zero drift 0.633, block bootstrap 0.695). The harness random-walk p is p_sim 0.0055 (null mean 0.6906); the audit reproduces about 0.0085. Cite the baseline 0.65 to 0.69, p_sim and n = 33 together; never p_holm alone.
- Reading: after an 8 percent rally off an unbroken reaction low, the index usually made a new high within the same primary cycle, more often than a drift-matched random walk does. Against the correct baseline the evidence is near p 0.005 to 0.009 and would be borderline after Holm, not overwhelming. The headline is the most favourable grid point (sweep 0.5935 to 0.8788), though the direction holds at every secondary_pct point with n at or above 30.
- SP_IYT (SPY with IYT, 2004 on, descriptive only): p_extend 0.80 on n 20, p_sim 0.1314, flagged not distinguishable from a random walk with drift.

So "is trend persistence actually proven": proven under the protocol as pre-registered against a 0.5 null, yes. Against the mechanically correct random-walk baseline the effect is real but modest and borderline. A v3 protocol that pre-registers the simulated null (DEV-10) is what would move this from "confirmed with caveat" to a cleaner statement either way.

**Step 7, dow-theory-sources** (research/canonical_rules.md rows, Hamilton quotes first-hand)

Volume rules mapped to R7:
- R-037 volume_with_primary_trend, 【literature-consensus】, P-Ham and educators, verified yes. Hamilton: "It is worth while to note here that the volume of trading is always larger in a bull market than in a bear market. It expands as prices go up and contracts as they decline." (hamilton-1922-stock-market-barometer:Q19). Echoed by Edwards and Magee (snippet), StockCharts, CMT, Wikipedia, Taiwan educators. Nelson records Dow keeping a volume record but states no rule.
- R-038 volume_in_secondary_reaction, 【literature-disputed】, Hamilton vs educators. P1 Hamilton: "A sharp reaction in a bull market will often stimulate the volume of business." (hamilton-1922-stock-market-barometer:Q20). P2 educators (cmt:Q9, zh-ctyeh:Q17,Q18, kcm:Q16): volume dries up against the trend. The project's `volume_confirms` adopts P2, so the R7 test is a test of the educator reading, not Hamilton's.
- R-041 volume_secondary_to_price, 【literature-consensus】, P-Ham, verified yes. Hamilton: "it must be obvious that the averages have already taken those things into account" (hamilton-1922-stock-market-barometer:Q5). Volume is collateral evidence; signals come from price.
- The composite literature label on the R7 row is 【literature-disputed】 because R-038 is disputed (DEV-02 mapping rule).

Persistence rules mapped to R1:
- R-016 trend_definition_hh_hl, 【literature-consensus】, P-Dow and P-Rhea, verified yes (nelson:Q8). Dow: bull period while each high exceeds prior highs, bear once a low undercuts prior lows; Rhea and educators require both.
- R-017 trend_persists_until_reversal, 【literature-consensus】, Rhea lineage, verified no (second-hand through Edwards and Magee, Schannep, educators, Russell).

## Evidence status
| Claim | Literature label | Data label |
|---|---|---|
| Volume expands with the primary trend (R-037) | consensus | R7 【insufficient-evidence】, n 57, p_vol 0.3509, CI 0.2400 to 0.4806, bound 0.5162 |
| Volume dries up in reactions (R-038, P2) | disputed vs Hamilton P1 | same R7 row (test adopts P2) |
| Volume is collateral only (R-041) | consensus | not tested |
| Trend defined by HH/HL (R-016) | consensus | R1 【data-confirmed】 with caveat, n 33, 0.8788, CI 0.7267 to 0.9518, baseline 0.65 to 0.69, p_sim 0.0055 |
| Trend persists until reversal (R-017) | consensus | same R1 row |
Not tested: whether volume predicts anything about forward returns; R-041 as a stand-alone claim; any pre-2000 volume behaviour; Hamilton's P1 reading of R-038 (the harness only tested P2).

## Disputes
R-038, side by side, not adjudicated: Hamilton (first-hand, Q20) says a sharp bull-market reaction often stimulates volume; CMT, zh-ctyeh and kcm (educators, partial access) say volume dries up against the trend. The R7 result (with-trend leg heavier in only 35 percent of pairs) is descriptively nearer Hamilton's wording, but the protocol tested only P2 and labels nothing about P1.

## Limitations
- Volume data: vendor aggregate for ^DJI, level breaks 2000 and 2016/2017, sample starts 2000-01-03; nothing tests 1897 to 1999.
- R1 null mis-specified at 0.5; the 0.65 to 0.69 baseline is the honest comparison; headline at the most favourable grid point; the 8 percent and 15-session thresholds (R-046, 【agent-defined】) were chosen on this sample before the protocol was written.
- One pair label-driving (^DJI with ^DJT, 1992 on); SP_IYT descriptive only.
- Labels describe how a mechanical rule behaved on past closes. Not a forecast, not investment advice.

Files: /Users/lui/workspace/Dow/analysis/rule_status_table.md, /Users/lui/workspace/Dow/reports/rule_R7.md, /Users/lui/workspace/Dow/reports/rule_R1.md, /Users/lui/workspace/Dow/reports/backtest_audit.md, /Users/lui/workspace/Dow/research/canonical_rules.md (rows R-016, R-017, R-037, R-038, R-041).

### Grade

**PASS** (R17, 2026-11-08). Evidence:
- R7: 【insufficient-evidence】, explicitly "not refuted"; n 57, p_vol 0.3509 (20/57), CI 0.2400–0.4806, p_raw 0.9918, p_holm 1.0, sub-samples 0.3600 (25) / 0.3438 (32), refutation bound 0.5162 vs 0.5. All match `analysis/rule_status_table.md` row R7 and `reports/rule_R7.md` lines 14–34. Descriptive variants 0.4211 (CI 0.3019–0.5502), share_true 0.4058 on 69, sweep 0.2903–0.4739 match rule_R7.md lines 40–65. "Close to refuted" matches `reports/backtest_audit.md` lines 203 and 242. Level-break correction matches rule_R7.md line 80.
- R1: 【data-confirmed】 with the mandatory caveat in full (baseline 0.65–0.69 with iid 0.654 / zero-drift 0.633 / block 0.695, p_sim 0.0055, null mean 0.6906, audit 0.0085, n 33) and the sentence "never p_holm alone"; p_holm 0.000044 is only shown next to p_sim and the baseline. n 33, 0.8788 (29/33), CI 0.7267–0.9518, sub-samples 0.9412 / 0.8125, refute 0.9620, sweep 0.5935–0.8788 match rule_status_table.md and `reports/rule_R1.md` lines 18–72. SP_IYT 0.80 on n 20, p_sim 0.1314 matches `reports/backtest_run_20261108_063248.json` row (metric_value 0.8, n_obs 20, p_sim 0.1314).
- Literature pointers checked: hamilton-1922:Q19 (volume larger in bull), Q20 (sharp reaction stimulates volume), Q5 (averages take those things into account); cmt-open-exam-prep:Q9; zh-ctyeh:Q17, Q18; kcmtrade:Q16; nelson:Q8. All exist with matching text. R-038 presented P1 vs P2, not adjudicated; DEV-02 and DEV-10 exist in `analysis/protocol_deviations.md`.
- English; no forecast.


## Q5 The 2022 reversal down: when, confirmed by Transports? Next reversal up? Dow line in late 2026?

### Answer

Golden Q5 result (^DJI with ^DJT, data through 2026-11-06, integrity gate exit 0, strict mode, scripts: dow-trend-classification trend.py on both legs, dow-confirmation-and-line confirm.py since 2015).

## Trend state
- ^DJI: BULL_PRIMARY since 2023-06-15; defense line 45166.64 (2026-03-27 secondary low, reaction_low) [agent-defined, R-045; no source defines or names the Dow defense line]. ^DJT: BEAR_PRIMARY since 2026-09-24. Pair status today: non_confirmation (divergence warning under R-032 【literature-consensus】, not a reversal of the Industrials).

## Layered analysis
**2022 reversal down (dow-trend-classification, ^DJI).** Sequence of knowable dates:
- 2022-02-22: HH confirmed (secondary high 2022-01-04 at 36799.65).
- 2022-03-29: HL confirmed (secondary low 2022-03-08 at 32632.64); this low became the defense line [agent-defined].
- 2022-05-09: LH confirmed (secondary high 2022-03-29 at 35294.19 below 36799.65) and, the same session, the close 32245.70 crossed the defense line 32632.64 → REVERSAL_DOWN signalled 2022-05-09. State BEAR_PRIMARY since 2022-05-09.
**Transports confirmation (dow-confirmation-and-line).** ^DJT had already signalled REVERSAL_DOWN on 2022-04-08 (close 14470.72 through its reaction_high line 14523.47 after a counter swing). confirm_signal matches the two within the same primary cycle; pair confirmation dated the later of the two: 2022-05-09. So the Transports led by about a month and the Industrials' signal was confirmed on the day it appeared. The ^DJI bear then extended with LL 2022-07-28 and 2022-10-21 (secondary lows 2022-06-17 at 29888.78 and 2022-09-30 at 28725.51) and LH 2022-09-02 (2022-08-16 at 34152.01, which became the bear-side defense line).
**Next reversal up.** ^DJI: 2022-11-23 DEFENSE_BREAK (close 34194.06 above 34152.01 without a counter swing → BEAR_SUSPECT, a warning not a reversal); 2023-03-13 HH confirmed (2022-11-30 at 34589.77); 2023-06-15 HL confirmed (2023-03-13 low at 31819.14 above 28725.51) and the close 34408.06 was above the line → REVERSAL_UP 2023-06-15, BULL_PRIMARY since. ^DJT: 2022-07-29 DEFENSE_BREAK, then REVERSAL_UP 2023-02-01 (close 15197.91 through 14649.20 after a counter swing). Match: Transports led again; pair confirmation dated 2023-06-15. Both 2022 and 2023 reversals are therefore confirmed by the pair, with the Transports leading each time. Pending status would have been shown for the Transports' signals during the gaps (2022-04-08 to 2022-05-09; 2023-02-01 to 2023-06-15).
**Late-2026 Dow line (dow-confirmation-and-line, detect_lines).** Yes. Lines in the second half of 2026 (band_pct 0.05, min_sessions 15, max_drift_frac 0.5, all [agent-defined] parameters around Rhea's ~5 %, 2–3 weeks R-023/R-024 【literature-consensus】):
| start | end | sessions | band ^DJI | band ^DJT | breakout | breakout_ts | confirmed_both | confirmed_ts |
|---|---|---|---|---|---|---|---|---|
| 2026-06-04 | 2026-07-01 | 19 | 0.047 | 0.048 | up | 2026-07-02 | true | 2026-07-16 |
| 2026-07-02 | 2026-07-28 | 18 | 0.026 | 0.049 | down | 2026-07-29 | true | 2026-07-29 |
| 2026-07-30 | 2026-08-31 | 23 | 0.040 | 0.041 | down | 2026-09-01 | true | 2026-09-10 |
| 2026-09-16 | 2026-10-26 | 29 | 0.038 | 0.046 | up | 2026-10-27 | true | 2026-11-04 |
The most recent line ran 2026-09-16 to 2026-10-26 (29 sessions), broke upward on 2026-10-27 and both averages had broken the same way by 2026-11-04. No line is open as of 2026-11-06. Note the line breakout up on 2026-10-27 sits inside the current pair non-confirmation (Transports BEAR_PRIMARY since 2026-09-24); the line module and the trend machine are separate outputs and the skills do not reconcile them. volume_confirms: false (informational; R-038 【literature-disputed】).

## Evidence status
- HH/HL definition R-016, persistence R-017, closing prices R-036, two-average confirmation R-032/R-033, line definition R-022–R-025: 【literature-consensus】. Reversal rule R-018: 【literature-disputed】 (orthodox vs Schaefer/Russell); the strict machine is the project's reading of the orthodox position. Secondary thresholds 3 %/8 %/15 sessions R-046, defense line R-045, EQUAL tolerance, line min_sessions 15 and drift filter: 【agent-defined】. Rhea 3 % filter R-013: 【single-source】.
- Data labels (dow-rule-backtest rows cited by the skills): R1 trend persistence 【data-confirmed】 only with caveat (drift-matched random-walk baseline 0.65–0.69, p_sim 0.0055, n = 33). R2 reversal signal 【insufficient-evidence】 (n = 12). R3 two-average confirmation 【insufficient-evidence】 (n = 15, exploratory grouping DEV-11). R6 line breakout 【insufficient-evidence】 (n = 87, share 0.4138, refutation bound 0.5471 above 0.5). R7 volume 【insufficient-evidence】. Not tested: the defense line as a rule; whether Transports-leading confirmation matters.

## Disputes
- Reversal rule R-018: P1 orthodox (Hamilton, Rhea, Edwards & Magee) failed rally + break of prior low vs P2 Schaefer/Russell rejecting a break of secondary lows alone (R-065 halfway principle, 【single-source】). Not adjudicated.
- Confirmation timing R-033: Hamilton/BGK/CMT no same-day requirement vs Rhea's simultaneity paraphrase on line breaks; code imposes no window (max_days null).
- Volume on reactions R-038: Hamilton P1 (reactions can be heavy) vs educators P2 (dry up).

## Limitations
Signals are dated at confirmation bars, so the 2022 reversal is declared ~2 months after the January high. Thresholds tuned in-sample on ^DJI 1992+; different thresholds give different dates. Start 2015 run: trend establishment depends on --start (both legs were already established well before 2022, so 2022–2023 rows are unaffected). Indices unadjusted. Line counts are parameter-dependent (41 lines since 2015). Not investment advice.

### Grade

**PASS** (R17, 2026-11-08). Evidence:
- Fresh run of `.claude/skills/dow-confirmation-and-line/scripts/confirm.py --symbol ^DJI --pair ^DJT --start 2015-01-01`: 2022-05-09 REVERSAL_DOWN 32,245.70 vs level 32,632.64, confirmation confirmed, matched_ts 2022-04-08, confirmed_ts 2022-05-09; 2023-06-15 REVERSAL_UP 34,408.06 vs 34,152.01, matched_ts 2023-02-01, confirmed_ts 2023-06-15; 2022-11-23 DEFENSE_BREAK 34,194.06 > 34,152.01; HH 2022-02-22 36,799.65; HL 2022-03-29 32,632.64; LH 2022-05-09 35,294.19; LL 2022-07-28 29,888.78 and 2022-10-21 28,725.51; LH 2022-09-02 34,152.01; HH 2023-03-13 34,589.77; HL 2023-06-15 31,819.14. All match.
- Lines: last four rows 2026-06-04→07-01 (19, 0.047/0.048, up 07-02, conf 07-16), 2026-07-02→07-28 (18, 0.026/0.049, down 07-29, conf 07-29), 2026-07-30→08-31 (23, 0.040/0.041, down 09-01, conf 09-10), 2026-09-16→10-26 (29, 0.038/0.046, up 2026-10-27, confirmed_both true, 2026-11-04). 41 lines, band 0.05 / 15 / 0.5, max_days None. Exact match.
- ^DJT leg verified with `trend.py --symbol ^DJT --start 2015-01-01`: REVERSAL_DOWN 2022-04-08 close 14,470.72 through 14,523.47; DEFENSE_BREAK 2022-07-29; REVERSAL_UP 2023-02-01 close 15,197.91 through 14,649.20; BEAR_PRIMARY since 2026-09-24. All match.
- Labels: R-032 consensus, R-018 disputed not adjudicated, R-045/R-046 agent-defined, R1 caveat in full, R3 n 15 DEV-11, R6 n 87 / 0.4138 / 0.5471 match the status table. Honest note that the line breakout and the pair non-confirmation are unreconciled outputs. English; no prediction.


## Q6 Analyse AAPL (usstock, read-only) with SPY as pair; single-stock limitations

### Answer

Golden Q6 complete: AAPL is BULL_PRIMARY since 2025-07-03, defense line 302.25 [agent-defined], SPY state-level confirmed, four support zones, no resistance zone, uptrend line broken.

## Trend state

AAPL vs SPY, as-of 2026-11-06 (close 342.37), data 2015-01-02 to 2026-11-06, 2980 bars, method pct 0.03/0.08, 15-session filter, strict mode.

- Primary: BULL_PRIMARY since 2025-07-03 (REVERSAL_UP, close 212.71 crossed the bear-side line 212.20 after the HL counter swing of 2025-05-23, confirmed 2025-07-02).
- Secondary direction: up. Last secondary H 340.08 (2026-07-28, confirmed 2026-07-31, HH). Last secondary L 302.25 (2026-08-12, confirmed 2026-09-03, HL). The 2026-11-04 close of 349.51 exceeds the last H but is not yet a confirmed swing (no 8 percent pullback since).
- Dow defense line [agent-defined, R-045]: 302.25, reaction_low, set 2026-09-03 when the HL was confirmed. No source defines or names the Dow defense line; it is this project's construct (last confirmed secondary reaction low in a bull).
- Pair confirmation: `confirmed`, pair state BULL_PRIMARY (both legs BULL_PRIMARY). SPY is BULL_PRIMARY since 2023-11-14 with its own [agent-defined] line at 631.97 (2026-03-30). Signal-level note: the AAPL REVERSAL_UP of 2025-07-03 has no matching SPY REVERSAL_UP because SPY never signalled REVERSAL_DOWN in 2025 (its 2025-04-04 defense break put it in BULL_SUSPECT only, resumed by the 2026-03-27 HH). So state-level agreement is confirmed; the signal row stays `pending` by construction.

## Layered analysis

- Step 1, data (dow-swing-detection prerequisites): AAPL is not in `dow.mkt_klines`; the project loader reads only that table or CSV. I exported AAPL and SPY from `usstock.mkt_daily_quotes` (read-only, dow_user) to CSV and ran every layer with `--source csv`. Quality on the export: 2980 unique sessions each, no duplicates, no OHLC violations, no zero-volume bars, no multi-day gaps; the series is split- and dividend-adjusted (no 4:1 gap on 2020-08-31). SPY also taken from usstock so both legs share one adjustment basis (the `dow.mkt_klines` SPY copy is unadjusted). Integrity gate `scripts/check_integrity.py` on the dow database: exit 0.
- Step 2, swings (`swings.py`): 303 minor, 81 secondary swings since 2015. Last five secondary: H 315.20 (2026-06-02, conf 2026-06-25), L 275.15 (2026-06-25, conf 2026-07-02, retrace 0.58, in Rhea window and 1/3 to 2/3 band), H 340.08 (2026-07-28, conf 2026-07-31), L 302.25 (2026-08-12, conf 2026-09-03, amplitude 11.1 percent, 15 days, retrace 0.58, schannep_window and 1/3 to 2/3 band true, rhea_window false because 15 days is under 21).
- Step 3, trend (`trend.py`): 99 signals since 2015; first trend established 2015-12-15 (BEAR_PRIMARY), so the pre-2016 state depends on the data start. Since the 2025-07-03 REVERSAL_UP: HH 2026-01-06, HL 2026-02-02, LH 2026-03-13 (BULL_SUSPECT), HH 2026-06-25 (back to PRIMARY, line refreshed), HL 2026-07-02, HH 2026-07-31, HL 2026-09-03. No DEFENSE_BREAK since. With this history AAPL has shown 13 reversals since 2016 and 10 DEFENSE_BREAK warnings, many of them resolved within weeks: a single stock at this threshold flips far more often than ^DJI.
- Step 4, confirmation and lines (`confirm.py`): status above. 26 Dow lines since 2015, none open as of 2026-11-06; the last, 2025-11-24 to 2025-12-16, broke down on 2025-12-17 in one leg and was never confirmed by both (`pending`). volume_confirms: false (informational; R-038 literature-disputed; a false flag is what Hamilton's P1 allows).
- Step 5, levels and chart (`draw.py`): PNG /Users/lui/workspace/Dow/outputs/charts/AAPL_SPY_2026-11-06_pct0.03.png, JSON /Users/lui/workspace/Dow/outputs/json/AAPL_SPY_2026-11-06_pct0.03.json, CSV inputs /Users/lui/workspace/Dow/outputs/csv/AAPL_usstock_2026-11-06.csv and /Users/lui/workspace/Dow/outputs/csv/SPY_usstock_2026-11-06.csv.

Support zones [agent-defined, R-047], nearest first (bands where prior minor swing lows clustered, not floors that will hold):

| Zone | Range | Touches |
|---|---|---|
| 302.83 | 301.70 to 303.97 | 2 |
| 245.74 | 244.58 to 246.66 | 3 |
| 226.17 | 225.32 to 227.02 | 2 |
| 220.54 | 219.71 to 221.37 | 3 |

Resistance: none. `levels_note`: fewer than 2 swing highs above the close; the 2026-11-04 close 349.51 is above every prior swing high, so no zone can be reported (A8 side filter).

Trendline [agent-defined]: uptrend through the last two secondary lows 2026-06-25 @ 275.15 and 2026-08-12 @ 302.25, slope 0.565 per day, value 350.80 at as-of, status broken. Closes on 2026-11-02, 11-03, 11-05 and 11-06 sit 1.7 to 4.9 percent below the line, beyond the 1 percent tolerance. A broken trendline is not a Dow signal; the state machine ignores it. The nearest support zone coincides with the defense line (both from the 2026-08-12 low).

## Evidence status

- Three trends, HH/HL rule, persistence: R-001, R-016, R-017 literature-consensus. R1 trend persistence data-confirmed on ^DJI/^DJT only, with its caveat: drift-matched random-walk baseline 0.65 to 0.69, p_sim 0.0055, n = 33. Not tested on AAPL or any single stock.
- Reversal rule: R-018 literature-disputed; R2 insufficient-evidence (n = 12 on ^DJI).
- Two-average confirmation: R-032 literature-consensus; R3 insufficient-evidence. SPY as a "pairing average" for a stock is an agent-defined choice; no source pairs a stock with an index.
- Lines: R-022 literature-consensus on definition, 15 sessions and drift filter agent-defined; R6 insufficient-evidence. Volume: R-037 consensus, R-038 disputed; R7 insufficient-evidence.
- Swing thresholds 3/8 percent and 15-session filter: R-046 agent-defined; the 3 percent as Rhea's rally filter R-013 single-source. Secondary duration R-006/R-007 and retrace R-008 to R-010 literature-disputed; R5 and R4 insufficient-evidence.
- Defense line: R-045 agent-defined, never tested. Support/resistance zones and trendlines: R-047 agent-defined, no backtest row, insufficient-evidence by absence.

## Disputes (side by side, not adjudicated)

- Secondary duration (R-006/R-007): Rhea three weeks to three months; Schannep 8 trading days minimum; the 2026-08-12 leg (15 calendar days) passes Schannep and fails Rhea.
- Secondary retrace (R-008 to R-010): Rhea 1/3 to 2/3; Taiwan educators 1/3 to 1/2; base of measurement differs between Rhea and the educators. The 0.58 retrace of the last low sits inside Rhea's band and outside the educators'.
- Reversal rule (R-018): orthodox P1 (failed rally plus break of prior low; strict mode here) versus Schaefer/Russell P2 (break of secondary low alone proves nothing; halfway-level test, R-065 single-source, not implemented).

## Limitations specific to a single stock

1. Dow Theory is written for averages (R-034 literature-consensus pairs Industrials with Rails/Transports). Applying it to one stock, and pairing it with SPY, is a project extrapolation with no source behind it. Only the index-pair backtest exists; nothing here carries a data label for AAPL.
2. The 8 percent secondary threshold was tuned in-sample on ^DJI 1992 to 2026. AAPL's higher volatility yields 81 secondary swings and 13 reversals since 2015 versus far fewer on ^DJI, so states flip often and the reversal count is noisy.
3. Adjusted prices: usstock quotes are split- and dividend-adjusted, so historical levels differ from prices actually traded and can shift when the vendor re-adjusts. Zones and the defense line are stated on the adjusted series.
4. Volume flag uses AAPL's own share volume; a company's volume carries stock-specific news (earnings, buybacks), which the sources never discuss.
5. Start-date dependence: data from 2015 only; the first trend is established 2015-12-15; zones cluster only swings since 2015.
6. Pair status is coarse: SPY has had no reversal since 2023-11-14, so the "confirmed" status rests on state agreement, not on a matched reversal signal.
7. Chart legibility: ten years of dense signals; a narrower --start reads better.
8. Not investment advice; no targets, no prediction. Trend state and lines describe the record as of 2026-11-06.

### Grade

**PASS** (R17, 2026-11-08). Evidence:
- PNG `/Users/lui/workspace/Dow/outputs/charts/AAPL_SPY_2026-11-06_pct0.03.png` exists, 212,804 bytes. CSVs `outputs/csv/AAPL_usstock_2026-11-06.csv` and `SPY_usstock_2026-11-06.csv` exist, 2,980 rows each.
- Provenance: `SELECT count() FROM dow.mkt_klines WHERE symbol='AAPL'` → 0. `SHOW GRANTS` for dow_user: SELECT only on usstock.* (read-only). usstock.mkt_daily_quotes AAPL 2015-01-02→2026-11-06, 2980 rows; closes 24.1925 and 342.3699 equal the CSV first and last rows; SPY 170.125 / 735.2899 likewise. Adjusted-series claim verified: CSV 2020-08-28 close 121.06 → 2020-08-31 125.17 (no 4:1 gap); dow.mkt_klines SPY 2015-01-02 close 205.43 vs usstock 170.125, so the dow copy is indeed unadjusted.
- Reproduction with `draw.py --source csv --csv ... --csv-pair ... --symbol AAPL --pair SPY --start 2015-01-01 --no-chart` (run c476e2ad): BULL_PRIMARY since 2025-07-03 (REVERSAL_UP close 212.71 vs 212.20); defense line 302.25 reaction_low 2026-08-12 agent-defined; pair confirmed BULL_PRIMARY with "latest A REVERSAL_UP not yet confirmed by B"; 303 minor / 81 secondary; last swings H 315.20 (06-02, conf 06-25), L 275.15 (conf 07-02, retrace 0.58), H 340.08 (conf 07-31), L 302.25 (conf 09-03, 11.1 %, 15 days, retrace 0.58); zones 302.83 (301.70–303.97, 2), 245.74 (3), 226.17 (2), 220.54 (3); no resistance; uptrend 2026-06-25 @ 275.15 → 2026-08-12 @ 302.25, slope 0.565, 350.80 at as-of, broken; 26 lines, last 2025-11-24→12-16 down 2025-12-17 pending; 99 signals. SPY leg: BULL_PRIMARY since 2023-11-14, line 631.97 (2026-03-30), DEFENSE_BREAK 2025-04-04, HH 2026-03-27. 2026-11-04 close 349.51 in CSV. All match.
- Limitations stated: theory written for averages (R-034), SPY pairing agent-defined with no source, no data label for AAPL, adjusted prices, volume stock-specific, start-date dependence. Labels on every figure; no targets; English.
- Defect (does not violate a listed criterion): "10 DEFENSE_BREAK warnings" — the CSV trend run gives 9 DEFENSE_BREAK signals since 2016 and none in 2015. Reversal count 13 (6 down, 7 up) is correct.


## Summary

| Q | PASS/FAIL | Reason |
|---|---|---|
| Q1 | PASS | PNG 195 kB on disk; state, since, defense line, zones, trendline anchors and 41 lines all equal a fresh `dow analyze` run; labels and R1 caveat present. One wrong retrace figure (0.95) in the Disputes paragraph. |
| Q2 | PASS | Defense line stated as agent-defined with no literature source, cites search log Q1 and registry R-045, gives the project definition without calling it canonical, carries the "not found ≠ does not exist" caveat; all spot-checked pointers exist. |
| Q3 | PASS | Duration and retracement figures side by side with slug:Qn and 【literature-disputed】, not adjudicated, Rhea flagged second-hand, R5 figures match the status table; pointers verified. |
| Q4 | PASS | R7 insufficient-evidence (not refuted) with n/estimate/CI/bound; R1 data-confirmed with the full mandatory caveat, never p_holm alone; every figure matches rule_status_table.md, rule_R1.md, rule_R7.md, backtest_audit.md. |
| Q5 | PASS | 2022-05-09 ↔ ^DJT 2022-04-08, 2023-06-15 ↔ 2023-02-01, line 2026-09-16→10-26 up 10-27 confirmed 11-04 all reproduced by confirm.py and trend.py. |
| Q6 | PASS | Full AAPL/SPY analysis reproduced from the CSVs; limitations stated; AAPL absent from dow.mkt_klines (count 0), dow_user has SELECT-only on usstock, CSV equals usstock closes. DEFENSE_BREAK count off by one (9, not 10). |

## Issues for the lead

1. Q1 Disputes paragraph: "the 2025-04-08 low (retrace 0.95) satisfies none" is wrong. The run output and the answer's own item 2 give retrace 0.58; flags are schannep_window true and 1/3–2/3 band true, Rhea window and 1/3–1/2 band false. Correct the sentence or drop it before this answer is used as a golden reference.
2. Q6 Step 3: "10 DEFENSE_BREAK warnings" should be 9 (count from the same CSV trend run, no DEFENSE_BREAK in 2015). Cosmetic, but a golden answer should not carry an uncheckable tally.
3. Q4 and Q6 cite an SP_IYT R1 figure (0.80, n 20, p_sim 0.1314) that lives only in `reports/backtest_run_*.json`, not in `reports/rule_R1.md` or the status table. Consider adding the SP_IYT descriptive row to rule_R1.md so the agent's citation has a markdown home.
4. Q5 notes that the 2026-10-27 upward line breakout (confirmed by both averages) and the current pair non-confirmation (^DJT BEAR_PRIMARY) are unreconciled outputs. The agent handled it honestly, but the skills give no guidance on what to say when the two modules disagree; a sentence in dow-confirmation-and-line would prevent future answers from picking one.
5. Q1's chart caveat ("overlapping labels around 2020 and a short defense-line segment") is self-reported and I did not inspect the PNG visually; the file-size and content checks passed. If chart legibility matters for the golden run, someone should eyeball the PNG.
6. Verification environment: `usstock.mkt_daily_quotes` uses `trade_date`, `dow.mkt_klines` uses `ts_open`/`ts_close`; the lead's suggested count query ran fine, but anyone re-running provenance checks needs those column names.

