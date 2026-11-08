# Canonical Dow Theory rules (literature synthesis)

Built from the 43 notes in `research/sources/` as read on 2026-11-08. This version reflects the first-hand replacements of the hamilton, nelson, rhea, dow-editorials, edwards-magee and kirkpatrick-dahlquist notes, and the new russell-history-of-the-dow-theory note.

## 0. Method and legend

**Labels.**
- `literature-consensus`: at least 2 independent sources agree and none contradicts.
- `literature-disputed`: at least 2 sources give materially different figures or opposing readings. Positions are shown side by side with no adjudication.
- `single-source`: one source states it, or later sources only echo it.
- `agent-defined`: the project's own construct.

**Independence caveat.** Nearly every modern source repeats Rhea (1932), who built on Hamilton (1922), who quoted Dow (1900 to 1902). Consensus means agreement without conflict. It does not mean independent rediscovery. An echo of one author, such as Blay repeating Schannep, counts as one source.

**Provenance tags.**
- `P-Dow`: Dow's own words, seen in Nelson 1903 (full text) and quoted by Hamilton (full text).
- `P-Ham`: Hamilton first-hand.
- `P-Rhea`: Rhea, read only through the Wiley reprint inside Schannep's book and through Blay. Never seen in the original.
- `SEC`: secondary, textbook, academic or encyclopedia.
- `EDU`: educator or broker.
- `MOD`: modern construct with no traceable primary source.

**Verified flag.**
- `yes`: the core figure appears in at least one `access: full-text` note (hamilton, nelson, brown-goetzmann-kumar-1998, cowles-1933-can-forecasters-forecast, russell-history-of-the-dow-theory).
- `no`: only partial or snippet notes support it. Most partial notes were tool-extracted and never re-checked against the live page.
- `partial`: some figures in the row are verified and others are not.

**Paraphrase rule.** Where a note records a figure only as paraphrase, I write "(paraphrase, no Qn)" and set verified to no.

**Contract column.** This describes `docs/specs/algorithm_contract.md` as it stands. "Dev. n" refers to its Deviations list.

**Short slugs.** `stockcharts`, `incredible`, `cmt` and `kcm` stand for stockcharts-chartschool-dow-theory, incrediblecharts-dow-theory-trends, cmt-open-exam-prep-dow-theory and kcmtrade-dow-theory. Likewise `dow-editorials` = dow-editorials-wsj-1900-1902 and `rhea` = rhea-1932-the-dow-theory. All other slugs are written in full or follow the file name.

**Removed from the earlier draft.** The dow-editorials note no longer carries the Bishop-derived items. These were the 20 to 40 day swing, the 15 to 30 day sag, 3/8 to 5/8, one-half, 1/3 to 1/2, the tide analogy, the 1% range and the Dow volume quotes. They are not cited here.

## 1. Rule registry

Columns: id | rule_key | canonical statement | figure(s) | sources agreeing | sources disagreeing | label | provenance | algorithmizable | verified | contract.

For disputed rows, "agreeing" lists grouped positions (P1, P2, ...) and "disagreeing" says the positions are mutually exclusive.

### 1.1 Three trends and durations

| id | rule_key | statement | figure(s) | agreeing | disagreeing | label | prov. | algo | verified | contract |
|---|---|---|---|---|---|---|---|---|---|---|
| R-001 | three_trends | Three movements run at the same time: daily/minor, secondary (reaction, short or medium swing), primary (main). Names vary. | 3 | hamilton:Q1,Q3,Q4,Q8; dow-editorials:Q1,Q2; nelson:Q2,Q6; rhea:Q3; brown:Q9; kirkpatrick-dahlquist:Q2; edwards-magee:Q2,Q3; stockcharts:Q1-Q3; incredible:Q1-Q3; thismatter-dow-theory:Q7; cmt:Q5-Q8; wikipedia-en-dow-theory:Q2,Q3,Q5; wikipedia-zh-dow-theory:Q4; rich01-what-is-dow-theory:Q5; stockfeel-dow-theory:Q3; aaii-dow-theory-21st-century:Q1-Q3 | none on the count | consensus | P-Dow, P-Ham, P-Rhea | partly | yes | Implemented as `Swing.scale` minor/secondary/primary and `detect_multiscale` (dev. 3). No separate primary detector. |
| R-002 | primary_duration_min | Lower bound of a primary movement is disputed. | P1 at least 4 y; P2 at least 1 y; P3 under 1 y; P4 months | P1 (Dow 1900): dow-editorials:Q1; nelson:Q2; hamilton:Q8; reason-1974-dow-theory-revisited:Q2. P2: hamilton:Q2; wikipedia-zh-dow-theory:Q5; wantgoo-dow-theory:Q1; stockfeel-dow-theory:Q4; zh-ctyeh-dow-theory:Q2; edwards-magee (a year or more with over 20%, snippet paraphrase, no Qn). P3: rhea:Q4; wikipedia-en-dow-theory:Q2. P4: stockcharts:Q1; cmt:Q7; rich01-what-is-dow-theory:Q6; kcm:Q11 | P1-P4 mutually exclusive | disputed | P-Dow, P-Ham, P-Rhea, EDU | no-narrative | partial (P1, P2 verified) | Not a duration test. Primary is a state. `duration_days` is only recorded. |
| R-003 | primary_duration_max_typical | Dow's 1902 figure was 4 to 6 years. Hamilton rejected it as far too long. | P1 4-6 y; P2 rarely 3 y, oftener under 2 y; P3 bull markets average over 2 y | P1: dow-editorials:Q2; nelson:Q6; hamilton:Q6; incredible:Q3; nelson:Q1 and dow-editorials:Q6 (four and five years at a time). P2: hamilton:Q7,Q9. P3: rhea (paraphrase, no Qn). Unspecified: stockcharts:Q1; wikipedia-en-dow-theory:Q2; kcm:Q11 | P1 vs P2 (hamilton:Q7 refutes P1) | disputed | P-Dow, P-Ham, P-Rhea | no-narrative | yes | Not implemented. |
| R-004 | primary_duration_empirical_avg | Hamilton's averages for 1900 to 1923. | bull 25 months, bear 15 months | hamilton:Q13 | none | single-source | P-Ham | no-narrative | yes | Not implemented. |
| R-005 | primary_duration_unforecastable | The length of a primary movement cannot be told in advance. | — | hamilton:Q12 (Dow, Jul 1901); nelson:Q16; rhea (paraphrase, no Qn); russell-dow-theory-letters:Q3 (journalist-relayed) | none | consensus (one lineage) | P-Dow, P-Rhea | no-narrative | yes | Implicit only. |

### 1.2 Secondary reaction

| id | rule_key | statement | figure(s) | agreeing | disagreeing | label | prov. | algo | verified | contract |
|---|---|---|---|---|---|---|---|---|---|---|
| R-006 | secondary_duration_min | Minimum length of a secondary reaction is disputed. | no minimum; 8 trading days; 10 d; 2 weeks; 15 d; 20 d; 3 weeks | P0 no limit (Schaefer): russell-history-of-the-dow-theory:Q6 and its paraphrase section. P1 8 trading days (Schannep): thedowtheory-lines-special-issue:Q8. P2 about 10 d: dow-editorials:Q2; hamilton:Q6; nelson:Q6; reason-1974-dow-theory-revisited:Q3; wikipedia-en-dow-theory:Q3; thedowtheory-schannep-vs-classical:Q3. P3 2 weeks (Dec 1900): dow-editorials:Q1; hamilton:Q8; nelson:Q2. P4 15 d (Rhea's own statistical screen, via Blay, unverified): rhea (paraphrase, no Qn). P5 20 d (Hamilton editorial Sep 1904, via Schannep's author's note): rhea note (paraphrase, no Qn). P6 3 weeks: rhea:Q5; edwards-magee:Q2 (glossary); russell-history-of-the-dow-theory:Q5; kirkpatrick-dahlquist:Q4; thedowtheory-basics:Q5; wikipedia-zh-dow-theory:Q6; wantgoo-dow-theory:Q2; stockfeel-dow-theory:Q5; zh-ctyeh-dow-theory:Q3; thedowtheory-lines-special-issue:Q9. Rhea may allow less: thedowtheory-rhea-three-weeks:Q1,Q2. Unquantified weeks: cmt:Q8; rich01-what-is-dow-theory:Q7; kcm:Q12 | all positions mutually exclusive. Schannep's 8 vs 10 days differ between two Blay pages. The rhea note says the three-week minimum is Rhea's, not Dow's or Hamilton's. | disputed | P-Dow, P-Ham, P-Rhea, EDU | partly | partial (P2, P3 verified) | Not a filter. `duration_days` is recorded. `status_labels.secondary_duration_bounds` = literature-disputed. |
| R-007 | secondary_duration_max | Upper bound and typical length are disputed. | about 1 month+; 60 d; 3 months; 12 weeks; several months; no limit. Typical: Dow 30-40 d, Hamilton under 40 d | P1 a month or more: dow-editorials:Q1; hamilton:Q8; nelson:Q2. P2 60 d: dow-editorials:Q2; hamilton:Q6; nelson:Q6; reason-1974-dow-theory-revisited:Q3. P2b Hamilton calls 40-60 d exceedingly rare: hamilton:Q22 (also zh-stockcloud-dow-theory-line:Q19, out of context). P3 3 months ("as many months"): rhea:Q5; edwards-magee:Q2; russell-history-of-the-dow-theory:Q5; thedowtheory-basics:Q5; wikipedia-en-dow-theory:Q3; wantgoo-dow-theory:Q2; stockfeel-dow-theory:Q5. P4 12 weeks (Rhea alternative, via Blay): rhea (paraphrase, no Qn). P5 several months: cmt:Q8; rich01-what-is-dow-theory:Q7; kcm:Q12; zh-ctyeh-dow-theory:Q3. P6 no limit: russell-history-of-the-dow-theory paraphrase on Schaefer. Typical 30-40 d: dow-editorials:Q2; hamilton:Q6; Hamilton under 40: hamilton:Q22 | all mutually exclusive; hamilton:Q22 contradicts the long tail of P2 | disputed | P-Dow, P-Ham, P-Rhea | partly | partial | Same as R-006. |
| R-008 | secondary_retracement_lower | Lower bound is disputed. | 3/8; 1/3; about 1/2; none | P1 at least 3/8 (Dow, for stocks): dow-editorials:Q5; hamilton:Q11; nelson:Q15,Q20; reason-1974-dow-theory-revisited:Q1. P2 1/3 or 33%: rhea:Q5; edwards-magee:Q2; russell-history-of-the-dow-theory:Q5; thedowtheory-basics:Q4; aaii-dow-theory-21st-century:Q4; schannep-dow-theory-21st-century:Q4; wikipedia-en-dow-theory:Q4; wikipedia-zh-dow-theory:Q7; thedowtheory-rhea-three-weeks:Q3; thedowtheory-schannep-vs-classical:Q5; thedowtheory-lines-special-issue:Q10; stockfeel-dow-theory:Q6. P3 about 1/2 for a 2-3 point rise: nelson:Q19 (Ch. XXX); Russell/Schaefer 50% Principle (paraphrase, no Qn). P4 none: Schaefer (russell-history-of-the-dow-theory paraphrase). Not Dow: zh-ctyeh-dow-theory:Q5 (10-20%) | P1-P4 | disputed | P-Dow (3/8); P-Rhea (33%) | yes as a measurement | partial (3/8 verified; 33% not) | Partly. `Swing.retrace_ratio` records leg over previous opposite leg. `status_labels.secondary_retracement` = literature-disputed. |
| R-009 | secondary_retracement_upper | Upper bound is disputed. Dow gives only a minimum. | 2/3; 1/2; unbounded | P1 66% or 2/3: rhea:Q5; edwards-magee:Q2; russell-history-of-the-dow-theory:Q5; thedowtheory-basics:Q4; aaii-dow-theory-21st-century:Q4; wikipedia-en-dow-theory:Q4; wikipedia-zh-dow-theory:Q7; thedowtheory-rhea-three-weeks:Q3. P2 1/2: stockfeel-dow-theory:Q6. P3 unbounded: Dow "at least" (hamilton:Q11; nelson:Q15); Schaefer (russell-history-of-the-dow-theory paraphrase) | P1/P2/P3 | disputed | P-Rhea, EDU | yes | partial (Dow side verified) | Not used. |
| R-010 | secondary_retracement_base | The measured base differs. | Rhea: change since the last secondary ended. Others: the whole preceding primary swing. | P1 since last secondary ended: rhea:Q5; russell-history-of-the-dow-theory:Q5 (preceding uncorrected primary advance). P2 preceding primary swing: thedowtheory-rhea-three-weeks:Q3; thedowtheory-lines-special-issue:Q10; wikipedia-zh-dow-theory:Q7; edwards-magee:Q2 (previous Primary Advance); Russell 50% Principle uses the full 1953-56 swing (paraphrase). P3 unspecified primary movement: hamilton:Q11; nelson:Q15 | P1 vs P2 | disputed | P-Rhea vs EDU | yes | no | `retrace_ratio` uses the previous opposite leg. It matches neither base exactly. |
| R-011 | secondary_retracement_binding | Is a minimum retracement required? | required 1/3; guide only; replaced by 3%; none | P1 required: thedowtheory-lines-special-issue:Q10; thedowtheory-schannep-vs-classical:Q5; a secondary reading of Edwards-Magee as "at least three weeks and at least a third" (edwards-magee note, paraphrase). P2 guide only: thedowtheory-rhea-three-weeks:Q4,Q5. P3 replaced by 3%: thedowtheory-lines-special-issue:Q11,Q12; thedowtheory-rhea-three-weeks:Q8; schannep-dow-theory-21st-century:Q3. P4 no limit: Schaefer (russell-history-of-the-dow-theory). Dow: "generally ... at least" (hamilton:Q11; nelson:Q15) | P1-P4 | disputed | EDU, SEC | partly | no | Not a filter. |
| R-012 | secondary_pullback_pct_schannep | Schannep counts a counter move as a secondary reaction when it exceeds 3% on either average. At least 4% on both is usual. | >3% either; at least 4% both | schannep-dow-theory-21st-century:Q1,Q2,Q3; echoed by thedowtheory-lines-special-issue:Q11,Q13; thedowtheory-rhea-three-weeks:Q8; thedowtheory-schannep-vs-classical:Q4 | classical 1/3 test (R-011) | single-source (Schannep, echoed) | MOD | yes | no | Not implemented as a confirmation test. |
| R-013 | minor_move_filter_pct | A rally or decline counts only if the net reversal exceeds 3% of either average. In Rhea's own statistics, reactions under 15 days or 5% were discarded. | 3%; 15 d / 5% | rhea:Q7 (3%); rhea note paraphrase (15 d / 5%, via Blay and an unverified Fraser page). Schannep reuses 3%: schannep-dow-theory-21st-century:Q1. | Not in Dow or Hamilton (rhea note; hamilton note lists it as not mentioned). Dow's book method records each 1 point change in a single stock: nelson:Q11. Schannep calls the percentage a generality (rhea note). thedowtheory-lines-special-issue:Q11 presents 3% as Schannep's. | single-source | P-Rhea (second-hand) | yes | no | `detect_swings(method="pct", threshold=0.03)` flips at 3% adverse close. The JSON key `hamilton_3pct_filter` is labelled consensus. That is wrong on name and label. |
| R-014 | minor_duration | Length of a minor movement is disputed. | daily; under 6 d, rarely over 3 weeks; hours to a month or more; days to weeks; days to 3 weeks | P1 daily: hamilton:Q4,Q6; nelson:Q2,Q3,Q6; kirkpatrick-dahlquist:Q5; stockcharts:Q3; wikipedia-zh-dow-theory:Q8; aaii-dow-theory-21st-century:Q3. P2 usually under six days, rarely over three weeks: edwards-magee:Q3 (Bassetti glossary). P3 hours to a month or more: wikipedia-en-dow-theory:Q5. P4 days to weeks: rich01-what-is-dow-theory:Q8; kcm:Q13. P5 days to 3 weeks: zh-ctyeh-dow-theory:Q4 | P1-P5 | disputed | P-Dow vs EDU | partly | partial | Minor scale is a threshold scale. No duration test. |
| R-015 | daily_fluctuation_low_information | Day-to-day moves should be disregarded by ordinary investors and are misleading except while a line forms. | — | nelson:Q3; kirkpatrick-dahlquist:Q5 (quoting Rhea); stockcharts:Q3; aaii-dow-theory-21st-century:Q3; thedowtheory-basics:Q3; wikipedia-zh-dow-theory:Q8; cmt:Q5; rhea (paraphrase, no Qn) | none | consensus | P-Dow, P-Rhea | partly | yes (nelson:Q3) | State machine takes secondary-scale swings only. Minor swings are not used for trend state. |

### 1.3 Trend and reversal definitions

| id | rule_key | statement | figure(s) | agreeing | disagreeing | label | prov. | algo | verified | contract |
|---|---|---|---|---|---|---|---|---|---|---|
| R-016 | trend_definition_hh_hl | Dow's bull period lasts while each high exceeds previous highs. His bear period begins when a low falls below previous lows. Rhea combines highs and lows. | — | dow-editorials:Q3; nelson:Q8; rhea (paraphrase, Wiley p.9, no Qn); stockcharts:Q7; incredible:Q4,Q5,Q13; zh-stockcloud-dow-theory-trendline:Q3,Q4; kcm:Q2-Q8; oanda-bvi-dow-theory-trend-changes:Q1,Q2; oanda-bvi-dow-theory-trend-continuation:Q2; oanda-bvi-dow-theory-breakout-return-moves:Q2; zh-ctyeh-dow-theory:Q7,Q8; edwards-magee (up primary trend marked by each reaction stopping above the previous reaction low, snippet paraphrase) | none. Nuance: Dow uses highs for bulls and lows for bears. Rhea and modern educators require both. | consensus | P-Dow, P-Rhea | yes | yes (nelson:Q8) | Implemented. UNDEFINED to BULL_PRIMARY on confirmed HH then HL, mirrored for bears. HH/HL/LH/LL signals. |
| R-017 | trend_persists_until_reversal | A trend is assumed to continue until its reversal is definitely signalled. | — | edwards-magee:Q6; schannep-dow-theory-21st-century:Q7; incredible:Q14; wantgoo-dow-theory:Q9,Q10; stockfeel-dow-theory:Q15,Q16,Q17; oanda-bvi-dow-theory-index:Q2; oanda-bvi-dow-theory-trend-changes:Q5; rich01-what-is-dow-theory:Q15; zh-ctyeh-dow-theory:Q19; wikipedia-en-dow-theory:Q15; kcm:Q18; russell-dow-theory-letters:Q3 | none | consensus | P-Rhea lineage | partly | no | Implicit. A state persists until a `REVERSAL_*` signal. |
| R-018 | reversal_definition_swing_structure | The orthodox reading: a bull-to-bear reversal needs a failed rally high and a decline through the prior low, confirmed by both averages. Russell and Schaefer reject that a break of the preceding secondary lows alone proves a bear market. | — | P1 orthodox: hamilton:Q23,Q24; rhea:Q6 (confirmation), rhea paraphrase (Wiley p.9); stockcharts:Q8; kirkpatrick-dahlquist:Q3 and Study Guide paraphrase; edwards-magee:Q6 and 11th-ed. paraphrase (both averages beyond previous limit); oanda-bvi-dow-theory-trend-changes:Q3,Q4; russell-dow-theory-letters:Q5; thedowtheory-basics:Q9; russell-history-of-the-dow-theory:Q7 (describes the orthodox view). P2 Schaefer/Russell: russell-history-of-the-dow-theory:Q6,Q7, and its paraphrase of the 50% Principle and the third-phase test | P1 vs P2 | disputed | P-Ham, P-Rhea; MOD | partly | partial (hamilton:Q23,Q24 yes) | Partly. `REVERSAL_DOWN` needs LH then a close below the agent-defined defense line. Non-strict mode flips on `DEFENSE_BREAK`. |
| R-019 | reversal_abrupt_resumption_slow | A change of direction is abrupt. Resumption of the major trend is slower and is often foretold by a line. | — | hamilton:Q23 | none | single-source | P-Ham | no-narrative | yes | Not implemented. |
| R-020 | reversal_hard_to_tell_from_secondary | It is often hard to judge whether an advance has ended, because a pronounced secondary looks like a trend change. | — | nelson:Q9 (Dow, Jan 1902); rhea (paraphrase: secondaries are frequently mistaken for a change of primary trend, Wiley pp.7-8, no Qn) | none | consensus | P-Dow, P-Rhea | yes | yes (nelson:Q9) | Implemented through `confirmed_idx`, `swings_as_of` and the SUSPECT states. |
| R-021 | schannep_bull_bear_status_pct | Bull status needs a rise over 19%, bear status a fall over 16%. | +19% / -16% | aaii-dow-theory-21st-century:Q7,Q8; schannep-dow-theory-21st-century:Q9,Q10; thedowtheory-schannep-vs-classical:Q1; thedowtheory-basics:Q13 (19% only) | The AAII note says the traditional figure is 20% (note remark, no quote). Edwards-Magee snippet paraphrase gives over 20% for a primary trend (no Qn). | single-source (Schannep, echoed) | MOD | yes | no | Not implemented. |

### 1.4 Lines

| id | rule_key | statement | figure(s) | agreeing | disagreeing | label | prov. | algo | verified | contract |
|---|---|---|---|---|---|---|---|---|---|---|
| R-022 | line_definition | A line is a narrow sideways range, read as accumulation or distribution. Dow's text applies the word to an individual stock's chart. Hamilton and Rhea apply it to the averages. | — | dow-editorials:Q4; nelson:Q11,Q12; hamilton:Q10,Q15,Q24; rhea:Q8; brown:Q6; edwards-magee:Q7; reason-1974-dow-theory-revisited:Q7; stockcharts:Q10; cmt:Q10; zh-stockcloud-dow-theory-line:Q1 | Schannep discards lines: thedowtheory-lines-special-issue:Q14. oanda-bvi-dow-theory-after-breakout:Q2 treats a rectangle as a different pattern. | consensus | P-Dow, P-Ham, P-Rhea | yes | yes | Implemented in `line.py` `detect_lines`. `status_labels.line_definition` = consensus. |
| R-023 | line_band_pct | The line range is about 5% for both averages. Dow and Hamilton gave point ranges for stocks and averages. | ~5% | rhea:Q8; thedowtheory-lines-special-issue:Q2; reason-1974-dow-theory-revisited:Q8; incredible:Q7 (5% or less); zh-stockcloud-dow-theory-line:Q2,Q6,Q7; edwards-magee (5% ordinary width, 11th-ed. snippet paraphrase, no Qn). Point ranges: dow-editorials:Q4 and nelson:Q12 (2 points); hamilton:Q10 | none contradict. The 5% is a generality: zh-stockcloud-dow-theory-line:Q5,Q7,Q8. | consensus (one lineage) | P-Rhea | yes | no | Implemented: `band_pct=0.05` on (max-min)/mean for both series. Total versus plus/minus is not settled by any source. |
| R-024 | line_min_duration | A line lasts two to three weeks or longer. | 2-3 weeks | rhea:Q8; thedowtheory-lines-special-issue:Q1; reason-1974-dow-theory-revisited:Q9; zh-stockcloud-dow-theory-line:Q4,Q7; edwards-magee (two to three weeks or more, snippet paraphrase, no Qn). Variant: zh-stockcloud-dow-theory-line:Q3 (at least 3 weeks). Hamilton gives no figure: hamilton:Q15 (the 66 and 71 trading-day 1914 line is a paraphrase in the hamilton note, no Qn) | none | consensus (one lineage) | P-Rhea | yes | no | Implemented: `min_days=14` consecutive sessions (dev. 9). |
| R-025 | line_both_averages | Both averages must be inside their range at the same time. | — | rhea:Q8; thedowtheory-lines-special-issue:Q2; reason-1974-dow-theory-revisited:Q7; hamilton:Q24 | none | consensus | P-Ham, P-Rhea | yes | no | Implemented: both series must qualify. |
| R-026 | line_breakout_meaning | A break upward implies accumulation and higher prices. A break downward implies distribution and lower prices. | — | hamilton:Q24; rhea (paraphrase, Wiley p.10, no Qn); edwards-magee (8th-ed. snippet paraphrase); zh-stockcloud-dow-theory-line:Q9,Q10 | rhea paraphrase says "simultaneous" breaks, while hamilton:Q25 says the same day is not needed (see R-033) | consensus | P-Ham, P-Rhea | yes | yes (hamilton:Q24) | Implemented: first later close outside the window min/max. Emits `LINE_BREAKOUT_UP/DOWN` (dev. 9). |
| R-027 | line_break_implies_secondary_or_more | A confirmed line break signals a change of at least secondary, possibly primary, character. | — | hamilton:Q24; thedowtheory-lines-special-issue:Q5,Q6 | none | consensus | P-Ham | no-narrative | yes | Not implemented as a magnitude claim. |
| R-028 | line_breakout_3pct_filter | A line break needs a 3% penetration. | 3% | zh-stockcloud-dow-theory-line:Q12,Q13 (truncated fragments) | none | single-source | EDU | yes | no | Not implemented. Any close outside the range is a breakout. |
| R-029 | line_breakout_volume | A real breakout comes with large volume, judged against overall activity. | — | zh-stockcloud-dow-theory-line:Q14,Q15,Q16 | none | single-source | EDU | partly | no | Not implemented. |
| R-030 | line_breakout_measured_move | After a 5% line, expect about another 5% move. | ~5% | thedowtheory-lines-special-issue:Q7 | none | single-source | EDU | yes | no | Not implemented. |
| R-031 | line_precedes_resumption | A line often forms before resumption of the major trend. The line usually comes after, not before, the secondary break. | — | hamilton:Q23; hamilton note paraphrase for the "usually after" part (no Qn) | none | single-source | P-Ham | no-narrative | yes | Not implemented. |
| R-063 | line_significance_grows | A line gains significance as it lasts longer and stays narrower. | — | hamilton:Q15; edwards-magee:Q7 | none | consensus | P-Ham | partly | yes (hamilton:Q15) | Not implemented. Detection uses fixed `band_pct` and `min_days`. |
| R-064 | line_substitutes_for_secondary | A line may take the place of a secondary reaction. | — | incredible:Q7; edwards-magee (tenet heading "Lines May Substitute for Secondaries", from the note's tenet list, no Qn) | none | consensus | EDU | partly | no | Not implemented. |

### 1.5 Confirmation, closes, volume

| id | rule_key | statement | figure(s) | agreeing | disagreeing | label | prov. | algo | verified | contract |
|---|---|---|---|---|---|---|---|---|---|---|
| R-032 | two_average_confirmation | A move in one average is unreliable until the other average confirms it. Hamilton first defined it. | 2 averages | hamilton:Q17,Q21,Q25; rhea:Q6; russell-history-of-the-dow-theory:Q4; brown:Q5; kirkpatrick-dahlquist:Q6; edwards-magee:Q4; reason-1974-dow-theory-revisited:Q4,Q5; incredible:Q11,Q15; cmt:Q2; wikipedia-en-dow-theory:Q10,Q11; aaii-dow-theory-21st-century:Q5,Q6,Q13; thedowtheory-basics:Q7,Q8; russell-dow-theory-letters:Q1,Q2 | Origin only: thismatter-dow-theory:Q10 credits Dow. nelson:Q5 shows Dow only says to watch the averages, and the nelson note finds no two-average rule. | consensus | P-Ham (not P-Dow) | yes | yes | Implemented: `pair_confirm`. `status_labels.two_average_confirmation` = consensus. |
| R-033 | confirmation_lag | Confirmation need not come on the same day or week. Taking the same direction is enough. No maximum lag is given. | no fixed window | hamilton:Q25; brown:Q5; cmt:Q3,Q4; thedowtheory-lines-special-issue:Q3; rhea (paraphrase, Wiley p.9, no Qn) | rhea paraphrase on lines says "simultaneous" (internal tension, paraphrase only) | consensus | P-Ham, P-Rhea | partly | yes | Implemented as `confirmation.max_days`, default None (dev. 9). |
| R-034 | confirmation_pair | The pair is Industrials and Rails/Transports. Taiwan educators adapt it to market index plus sector index. | DJI + DJT | rhea:Q1; kirkpatrick-dahlquist:Q6; brown:Q5; thedowtheory-basics:Q7; thismatter-dow-theory:Q10. Adaptation: wantgoo-dow-theory:Q11; stockfeel-dow-theory:Q12 | none for DJI/DJT | consensus | P-Ham, EDU | yes | yes (brown:Q5) | Implemented for ^DJI/^DJT. `--pair` defaults from `pairs.yaml` for other symbols (dev. 13). |
| R-035 | schannep_three_indices_two_confirm | Schannep uses three indices including the S&P 500 and needs two to confirm. | 3 indices, 2 confirm | thedowtheory-schannep-vs-classical:Q2 | Absent from schannep-dow-theory-21st-century and thedowtheory-lines-special-issue. | single-source (promotional) | MOD | yes | no | Not implemented. `pair_confirm` takes two series. |
| R-036 | closing_prices_only | Signals use closing prices. Intraday extremes are ignored. | — | hamilton:Q24; rhea:Q1; edwards-magee:Q5; brown:Q12; cmt:Q1; reason-1974-dow-theory-revisited:Q10; rich01-what-is-dow-theory:Q4; zh-stockcloud-dow-theory-line:Q1; russell-dow-theory-letters:Q5; sperandeo-123-stockjock:Q4 | zh-stockcloud-dow-theory-trendline:Q20 says most chartists prefer closes, implying others use extremes. | consensus | P-Ham, P-Rhea | yes | yes (hamilton:Q24; brown:Q12) | Implemented: closes only. High/low only for the ATR method. |
| R-037 | volume_with_primary_trend | Volume is larger and expands in a bull market and contracts as prices fall. Volume is collateral evidence. | — | hamilton:Q19; nelson:Q4 (keep a volume record, no rule); edwards-magee (volume goes with the trend, tenet heading, snippet paraphrase); stockcharts:Q9; cmt:Q9; wikipedia-en-dow-theory:Q12,Q13; rich01-what-is-dow-theory:Q13,Q14; wantgoo-dow-theory:Q8; stockfeel-dow-theory:Q13,Q14; zh-ctyeh-dow-theory:Q17 | none | consensus | P-Ham, EDU | partly | yes (hamilton:Q19) | `volume_confirms` compares mean volume on legs aligned with the net move against counter legs over the last four secondary swings (dev. 11). It returns None when volume is all zero, as for the index. |
| R-038 | volume_in_secondary_reaction | Volume behaviour during reactions is disputed. | rises vs dries up | P1 a sharp reaction often stimulates volume: hamilton:Q20. P2 volume dries up against the trend: cmt:Q9; zh-ctyeh-dow-theory:Q17,Q18; kcm:Q16 | P1 vs P2 | disputed | P-Ham vs EDU | partly | partial | `volume_confirms` adopts P2. |
| R-039 | volume_overbought_oversold | An overbought market is dull on rallies and active on declines. An oversold market is the reverse. | — | rhea (paraphrase, Wiley p.10, no Qn); incredible:Q10,Q16 (echo) | none | single-source | P-Rhea | partly | no | Not implemented. |
| R-040 | volume_leads_price | Volume peaks have led market peaks by 5.6 months on average over 14 cycles since 1900. | 5.6 months; 14 cycles | takasugi-volume-leads-price:Q2 | A different study (all but one of 27 bull tops) is noted in the takasugi note. | single-source (undocumented) | EDU | yes | no | Not implemented. |
| R-041 | volume_secondary_to_price | The averages already discount volume. Volume adds only collateral evidence and signals come from price. | — | hamilton:Q5; edwards-magee (volume affords only collateral evidence, snippet paraphrase, no Qn); kcm:Q15 | none | consensus | P-Ham | no-narrative | yes (hamilton:Q5) | Consistent with the optional status of `volume_confirms`. |

### 1.6 Phases

| id | rule_key | statement | figure(s) | agreeing | disagreeing | label | prov. | algo | verified | contract |
|---|---|---|---|---|---|---|---|---|---|---|
| R-042 | phases_count | Bull and bear markets each have three phases. Hamilton's 1922 book has no phase schema. The schema is Rhea's. | 3 | rhea (paraphrase, Wiley p.7, no Qn); brown:Q10,Q11; incredible:Q8,Q9; kirkpatrick-dahlquist (Rhea's bear list, snippet paraphrase); edwards-magee (section on characteristic phases, snippet paraphrase); russell-history-of-the-dow-theory (Schaefer/Russell use a third speculative phase as a precondition, rules table); wikipedia-en-dow-theory:Q6; wantgoo-dow-theory:Q4-Q6; stockfeel-dow-theory:Q8; rich01-what-is-dow-theory:Q9; zh-ctyeh-dow-theory (accumulation, euphoria, distribution, panic, despair) | wikipedia-zh-dow-theory has no phases. hamilton and nelson notes: not mentioned. | consensus on the count only | P-Rhea | no-narrative | yes (brown:Q10,Q11) | Not implemented. |
| R-043 | phases_bull_names | Bull phase names fall into two schemes. | Rhea: revival of confidence, response to earnings, rampant speculation. Modern: accumulation, public participation, excess or distribution. | P1 Rhea: brown:Q10; incredible:Q8; rhea (paraphrase, no Qn). P2 modern: wikipedia-en-dow-theory:Q7,Q8; wantgoo-dow-theory:Q4,Q5,Q6; stockfeel-dow-theory:Q8-Q11; rich01-what-is-dow-theory:Q10; zh-ctyeh-dow-theory:Q10-Q13; stockcharts:Q5; thismatter-dow-theory:Q8,Q9; edwards-magee (accumulation, public participation, distribution, per secondary citations) | P1 vs P2 | disputed | P-Rhea; MOD | no-narrative | yes for P1 (brown:Q10) | Not implemented. |
| R-044 | phases_bear_names | Bear phase names fall into two schemes. | Rhea: abandonment of hopes, decreased business and earnings, distress selling. Modern: distribution, participation or panic, despair. | P1 Rhea: brown:Q11; incredible:Q9; rhea (paraphrase, no Qn); kirkpatrick-dahlquist (snippet paraphrase). P2 modern: rich01-what-is-dow-theory:Q11; zh-ctyeh-dow-theory:Q14,Q15,Q16; stockcharts:Q4,Q6 | P1 vs P2 | disputed | P-Rhea; MOD | no-narrative | yes for P1 (brown:Q11) | Not implemented. |

### 1.7 Agent-defined constructs

| id | rule_key | statement | figure(s) | agreeing | disagreeing | label | prov. | algo | verified | contract |
|---|---|---|---|---|---|---|---|---|---|---|
| R-045 | defense_line | The Dow defense line is the most recent secondary-reaction low in a bull trend or reaction high in a bear trend, used as a break level. No source defines or names this construct; see zh-defense-line-search-log. | none | none. Nearest analogues: thedowtheory-rhea-three-weeks:Q6,Q7 (secondary lows as stop-loss); zh-ctyeh-dow-theory:Q21 (prior pullback low as support); the Study Guide idea of failing to make new highs after a secondary (kirkpatrick-dahlquist note paraphrase) | zh-defense-line-search-log:Q1 (not found). edwards-magee, kirkpatrick-dahlquist, nelson, rhea, hamilton: not mentioned. | agent-defined | MOD | yes | n/a | Implemented as `TrendState.defense_line`, `DEFENSE_BREAK` with `agent_defined=True`, chart label "Dow defense line (agent-defined)", and `status_labels.defense_line` = agent-defined. |
| R-046 | swing_detection_thresholds | Swing detection by percentage, ATR or pivot, with a minor threshold of 3% and a secondary threshold of 8% plus a 15-session causal filter (was 10% before contract amendment A1, 2026-11-08). Only Rhea's 3% (R-013) is sourced. | minor 0.03; secondary 0.08 + 15 sessions; ATR 2.0 x 14; pivot_n 5; equal_extreme_tol 0.005 | none | — | agent-defined | MOD | yes | n/a | Implemented in `detect_swings` and `detect_multiscale` (dev. 2, 3; amendments A1, A2). |
| R-047 | level_clustering_parameters | Support and resistance zones from clustered swings: tolerance 0.75% or 0.5 ATR, at least 2 touches, at most 4 levels. | 0.0075; 0.5 ATR; 2; 4 | none | — | agent-defined | MOD | yes | n/a | Implemented in `cluster_levels` (dev. 8). |

### 1.8 Support, resistance, trendlines, adjacent constructs

| id | rule_key | statement | figure(s) | agreeing | disagreeing | label | prov. | algo | verified | contract |
|---|---|---|---|---|---|---|---|---|---|---|
| R-048 | secondary_low_as_stop | The lows of secondary reactions serve as the exit point when broken, always with confirmation. | — | thedowtheory-rhea-three-weeks:Q6,Q7 | none | single-source | EDU | yes | no | Partly. The defense line has the same geometry but is labelled agent-defined. |
| R-049 | trendline_construction | An uptrend line joins rising lows and a downtrend line joins falling highs. | — | zh-stockcloud-dow-theory-trendline:Q2,Q7,Q21; sperandeo-123-stockjock:Q1; oanda-bvi-dow-theory-after-breakout:Q2; oanda-bvi-dow-theory-trend-continuation:Q8; oanda-bvi-dow-theory-trend-changes:Q8 | none. Hamilton, Rhea, Nelson and Dow give no trendline rule. | consensus (educators only) | EDU | yes | no | Implemented: `fit_trendlines` through the last two confirmed secondary HL or LH. |
| R-050 | trendline_min_points | A valid uptrend line needs at least two rising lows. | 2 | zh-stockcloud-dow-theory-trendline:Q8 | sperandeo-123-stockjock:Q1 says "all the lows" | single-source | EDU | yes | no | Implemented with two points. |
| R-051 | trendline_log_scale | Ordinary trendlines should be drawn on a log chart. | — | zh-stockcloud-dow-theory-trendline:Q5,Q6 | none | single-source | EDU | yes | no | Not implemented. `slope_per_day` is linear. |
| R-052 | trendline_angle_45 | A trendline near 45 degrees is the most meaningful. | 45 degrees | zh-stockcloud-dow-theory-trendline:Q10 | none | single-source | EDU | partly | no | Not implemented. |
| R-053 | trendline_break_filter | A break needs two consecutive closes beyond the line, or a close penetration of at least 3%. These are alternatives. | two closes; 3% | zh-stockcloud-dow-theory-trendline:Q14,Q17,Q19; Q18 says 3% is unsuited to margin futures | none | single-source | EDU | yes | no | Partly. A line is valid if no close violates it by more than `tol_pct=0.01`. |
| R-054 | sr_role_reversal | Broken support becomes resistance and the reverse. | — | zh-stockcloud-dow-theory-trendline:Q13; oanda-bvi-dow-theory-breakout-return-moves:Q4,Q5 | none | consensus (educators) | EDU | partly | no | Not implemented. |
| R-055 | horizontal_levels_from_tests | Horizontal levels come from repeatedly tested prices. No zone width is given. | — | kcm:Q9,Q19 | none | single-source | EDU | yes | no | Implemented by `cluster_levels` with agent-defined tolerances (R-047). |
| R-056 | sperandeo_123_reversal | Sperandeo's 1-2-3 reversal: trendline break, failed new extreme, then a further break. Sources disagree on steps 2 and 3. | 3 steps | P1: roboforex-sperandeo-123-2b:Q1,Q2,Q3. P2: sperandeo-123-stockjock:Q2,Q3,Q4 | P1 vs P2 on steps 2 and 3 | disputed | EDU (Trader Vic, not Dow) | yes | no | Not implemented. |
| R-057 | sperandeo_2b | The 2B pattern is a false-breakout reversal setup. | — | roboforex-sperandeo-123-2b:Q4; sperandeo-123-stockjock:Q5 (paraphrase) | none | consensus (educators, not Dow) | EDU | yes | no | Not implemented. |

### 1.9 Other tenets, dissent and evidence

| id | rule_key | statement | figure(s) | agreeing | disagreeing | label | prov. | algo | verified | contract |
|---|---|---|---|---|---|---|---|---|---|---|
| R-058 | primary_not_manipulable | The primary trend cannot be manipulated. Manipulation is possible in daily and, to a limited degree, secondary moves. | — | hamilton:Q18; rhea (Hypothesis 1, paraphrase, no Qn); kirkpatrick-dahlquist (Rhea claim, snippet paraphrase) | none. nelson:Q13,Q17 describe manipulation in individual stocks and leaders. | consensus | P-Ham, P-Rhea | no-narrative | yes (hamilton:Q18) | Not implemented. |
| R-059 | averages_discount_everything | The averages already reflect everything known. This is Rhea's second hypothesis. | — | hamilton:Q5,Q16; rhea:Q1; edwards-magee:Q1; thismatter-dow-theory:Q2; wikipedia-en-dow-theory:Q9; stockfeel-dow-theory:Q2 | none | consensus | P-Ham, P-Rhea | no-narrative | yes | Not implemented. |
| R-060 | theory_not_infallible | The theory is not an infallible system. The sentence is Rhea's. Hamilton says only that the barometer is not perfect. | — | rhea:Q2; hamilton:Q14; nelson:Q22; incredible:Q12; thismatter-dow-theory:Q3; thedowtheory-basics:Q10; edwards-magee:Q8 | none | consensus | P-Rhea (phrase); P-Ham, P-Dow (sense) | no-narrative | yes (hamilton:Q14; nelson:Q22) | Not implemented. |
| R-061 | double_tops_bottoms | The value of double tops and bottoms is disputed. | useful vs low value | P1 Dow describes the pattern as a method, with a decline likely after a second failure: nelson:Q14. Hamilton calls it not infallible but often useful (hamilton note paraphrase, no Qn). P2 Rhea says of little value and deceptive more often than not (rhea paraphrase, Wiley p.10, no Qn) | P1 vs P2 | disputed | P-Dow, P-Ham vs P-Rhea | partly | partial (nelson:Q14 yes) | Not implemented. |
| R-062 | beats_buy_and_hold | Whether Dow Theory beats buy-and-hold is disputed. See section 5. | see section 5 | P1 no raw edge: cowles-1933-can-forecasters-forecast:Q11,Q12,Q13; brown:Q29; rich01-what-is-dow-theory:Q22. P2 risk-adjusted edge: brown:Q30,Q31; kirkpatrick-dahlquist:Q7. P3 1-2% a year: aaii-dow-theory-21st-century:Q11; schannep-dow-theory-21st-century:Q11; stockcharts:Q11 | P1 vs P2 vs P3 | disputed | SEC, EDU | yes (backtest) | yes (cowles33, brown) | Not in `src`. Tested in the P4 backtests. |
| R-065 | schaefer_50pct_principle | A secondary reaction is distinguished from a new bear market by whether the decline stays above the halfway level of the primary swing, and by whether a third speculative phase has occurred. | 50% of the primary swing; example halfway level 388.27 for the 1953-56 swing | russell-history-of-the-dow-theory (paraphrase section, Q7 context; Russell and Schaefer) | orthodox reading (R-018): russell-history-of-the-dow-theory:Q7 | single-source | MOD (Schaefer, Russell) | yes | yes (note read in full text, paraphrase) | Not implemented. |

## 2. Agree/disagree matrix for numeric parameters

### 2.1 Secondary duration (R-006, R-007)

| source:quote | min | max | note |
|---|---|---|---|
| dow-editorials:Q1; nelson:Q2; hamilton:Q8 | 2 weeks | a month or more | Dec 19, 1900 |
| dow-editorials:Q2; nelson:Q6; hamilton:Q6 | 10 d | 60 d | Jan 4, 1902; average 30-40 d |
| reason-1974-dow-theory-revisited:Q3 | about 10 d | 60 d | restates Dow 1902 |
| hamilton:Q22 | — | 40-60 d "exceedingly rare" | duration may be appreciably under 40 d |
| Hamilton editorials via Schannep author's note (rhea note, paraphrase, no Qn) | 20 d / 1 month / a few days | 60 d / 3 months / many weeks | Sep 17, 1904; Feb 26, 1909; Feb 11, 1922; not in the 1922 book |
| zh-stockcloud-dow-theory-line:Q19 | — | 40-60 d | Dow estimate, out of context |
| rhea:Q5 | 3 weeks ("usually") | as many months (3) | via Wiley reprint |
| rhea note (paraphrase via Blay, Fraser p.76 and p.61, unverified) | 15 d discard in Rhea's statistics; alternative 3 weeks | alternative 12 weeks | |
| edwards-magee:Q2 | 3 weeks | 3 months | glossary text by Bassetti |
| russell-history-of-the-dow-theory:Q5 | 3 weeks | 3 months | Russell paraphrase of Rhea |
| kirkpatrick-dahlquist:Q4 | 3 weeks | truncated | quotes Rhea |
| thedowtheory-basics:Q5; wantgoo-dow-theory:Q2; stockfeel-dow-theory:Q5 | 3 weeks | 3 months | |
| wikipedia-en-dow-theory:Q3 | 10 d | 3 months | mixes Dow's 10 days with Rhea's 3 months |
| wikipedia-zh-dow-theory:Q6 | over 3 weeks | — | |
| cmt:Q8; rich01-what-is-dow-theory:Q7; kcm:Q12 | weeks | a few or several months | |
| zh-ctyeh-dow-theory:Q3 | 3 weeks | several months | |
| thedowtheory-lines-special-issue:Q9 | 3 calendar weeks | — | "classical" |
| thedowtheory-lines-special-issue:Q8 | 8 trading days | — | Schannep |
| thedowtheory-schannep-vs-classical:Q3 | 10 d or fewer | — | Schannep |
| thedowtheory-rhea-three-weeks:Q1,Q2 | 3 weeks called "market lore" | — | a reaction may be shorter |
| russell-history-of-the-dow-theory:Q6 | none | none | Schaefer ignores "temporary reactions" |

### 2.2 Secondary retracement (R-008 to R-011)

| source:quote | figure | note |
|---|---|---|
| dow-editorials:Q5; hamilton:Q11; nelson:Q15 | at least 3/8 | Dow, Jul 20, 1901; for a stock: 10 points up gives 4 or more back |
| nelson:Q20 | at least 3/8 of the first swing | Ch. XXX |
| nelson:Q19 | about half | for a 2-3 point rise; Ch. XXX |
| reason-1974-dow-theory-revisited:Q1 | at least 3/8 | credited to Dow |
| rhea:Q5 | 33% to 66% of the primary change since the last secondary ended | via Wiley reprint |
| edwards-magee:Q2 | 1/3 to 2/3 of the previous primary advance | glossary text |
| russell-history-of-the-dow-theory:Q5 | 1/3 to 2/3 of the preceding uncorrected primary advance | paraphrase of Rhea |
| thedowtheory-basics:Q4; aaii-dow-theory-21st-century:Q4; schannep-dow-theory-21st-century:Q4; wikipedia-en-dow-theory:Q4 | 33% to 66% | |
| wikipedia-zh-dow-theory:Q7; thedowtheory-rhea-three-weeks:Q3; thedowtheory-schannep-vs-classical:Q5 | 1/3 to 2/3 | |
| thedowtheory-lines-special-issue:Q10 | at least 1/3 | "classical requires" |
| stockfeel-dow-theory:Q6 | 1/3 to 1/2 | |
| zh-ctyeh-dow-theory:Q5 | 10-20% | Taiwan reference, not Dow |
| cmt:Q8 | "a portion" | no fraction |
| Schaefer (russell-history-of-the-dow-theory paraphrase) | no limit; 50% Principle as separate test | |
| schannep-dow-theory-21st-century:Q1,Q2 | over 3% on either; at least 4% on both | replaces retracement |

### 2.3 Line band percent (R-023)

| source:quote | figure | note |
|---|---|---|
| rhea:Q8 | about 5% | both averages |
| thedowtheory-lines-special-issue:Q2 | about 5% | Rhea as quoted |
| reason-1974-dow-theory-revisited:Q8 | about 5% | |
| incredible:Q7 | 5% or less | as a secondary reaction shape |
| zh-stockcloud-dow-theory-line:Q2,Q6 | 5%, centred on the mean | Q7 says empirical; Q5 and Q8 say not strict |
| edwards-magee (snippet paraphrase, no Qn) | 5% ordinary width | reported, not verified |
| dow-editorials:Q4; nelson:Q12; hamilton:Q10 | 2 points | Dow 1901, individual stock |
| hamilton note paraphrase (no Qn) | 3 and 4 points (1914); "three points or so" (Ch. XXI) | points, not percent |
| contract | (max-min)/mean at most 5% | |

### 2.4 Line minimum duration (R-024)

| source:quote | figure |
|---|---|
| rhea:Q8 | two to three weeks or longer |
| thedowtheory-lines-special-issue:Q1; reason-1974-dow-theory-revisited:Q9 | two to three weeks or longer |
| zh-stockcloud-dow-theory-line:Q4,Q7 | two to three weeks or longer; empirical |
| zh-stockcloud-dow-theory-line:Q3 | at least 3 weeks |
| edwards-magee (snippet paraphrase, no Qn) | two to three weeks or more |
| hamilton:Q15; edwards-magee:Q7 | no figure; longer and narrower is more significant |
| hamilton note paraphrase (no Qn) | 66 and 71 trading days in 1914 |
| contract | 14 sessions |

### 2.5 Minor-move filter (R-013)

| source:quote | figure | note |
|---|---|---|
| rhea:Q7 | 3% net reversal of either average | defines "rally or decline" |
| rhea note paraphrase (via Blay, unverified) | reactions under 15 days or 5% discarded | Rhea's statistical work |
| schannep-dow-theory-21st-century:Q1 | over 3% on either average | secondary return move |
| thedowtheory-lines-special-issue:Q11,Q13; thedowtheory-rhea-three-weeks:Q8; thedowtheory-schannep-vs-classical:Q4 | 3% | presented as Schannep's variant |
| nelson:Q11 | each 1 point change recorded | book method, a single stock, not a filter on averages |
| zh-stockcloud-dow-theory-trendline:Q17; zh-stockcloud-dow-theory-line:Q12,Q13 | 3% penetration | different object |
| hamilton note | not mentioned | |
| incredible:Q6 | "large corrections" | no figure |

### 2.6 Primary duration (R-002, R-003)

| source:quote | figure |
|---|---|
| dow-editorials:Q1; nelson:Q2; hamilton:Q8 | at least 4 years (Dec 1900) |
| dow-editorials:Q2; nelson:Q6; hamilton:Q6; incredible:Q3 | 4 to 6 years (Jan 1902) |
| nelson:Q1; dow-editorials:Q6 | bull and bear markets run four and five years at a time |
| reason-1974-dow-theory-revisited:Q2 | at least 4 years |
| hamilton:Q2 | at least a year, generally much longer |
| hamilton:Q7 | before Dow never 4 to 6 years, rarely 3, oftener under 2 |
| hamilton:Q13 | bull 25 months, bear 15 months (1900-1923) |
| rhea:Q4 | under a year to several years |
| rhea paraphrase (no Qn) | bull markets average longer than two years |
| edwards-magee (snippet paraphrase, no Qn) | a year or more, over 20% |
| wikipedia-en-dow-theory:Q2 | under a year to several years |
| wikipedia-zh-dow-theory:Q5; wantgoo-dow-theory:Q1; stockfeel-dow-theory:Q4 | one year or more |
| zh-ctyeh-dow-theory:Q2 | 1 year to several |
| stockcharts:Q1; cmt:Q7; rich01-what-is-dow-theory:Q6; kcm:Q11 | months to years |
| thedowtheory-flavors-iii:Q6 | Schannep trades average 2.5 years (holding period, not a primary duration) |

### 2.7 Schannep variants

| variant | source:quote | classical comparator |
|---|---|---|
| 3% counter move | schannep-dow-theory-21st-century:Q1; thedowtheory-lines-special-issue:Q11,Q13; thedowtheory-rhea-three-weeks:Q8; thedowtheory-schannep-vs-classical:Q4 | 1/3 to 2/3 (thedowtheory-schannep-vs-classical:Q5). Rhea's own text already contains a 3% rally/decline definition: rhea:Q7. |
| at least 4% on both averages | schannep-dow-theory-21st-century:Q2 | — |
| 8 trading days | thedowtheory-lines-special-issue:Q8 | 3 calendar weeks (thedowtheory-lines-special-issue:Q9) |
| 10 days or fewer | thedowtheory-schannep-vs-classical:Q3 | same |
| +19% bull, -16% bear | aaii-dow-theory-21st-century:Q7,Q8; schannep-dow-theory-21st-century:Q9,Q10; thedowtheory-schannep-vs-classical:Q1; thedowtheory-basics:Q13 (19% only) | AAII note says traditional is 20% (no quote, unverified) |
| three indices, two confirm | thedowtheory-schannep-vs-classical:Q2 only | two averages |
| lines discarded | thedowtheory-lines-special-issue:Q14 | lines in rhea:Q8 |

## 3. Provenance chain

| key sentence or claim | earliest traceable | chain | flag |
|---|---|---|---|
| Three movements | Dow, Dec 19, 1900 (dow-editorials:Q1) | Nelson 1903 (nelson:Q2, no dates printed), Hamilton (hamilton:Q8, dates given), Rhea (rhea:Q3), then educators | Dates come from Hamilton and from Schannep's Wiley excerpt (dow-editorials note). Hamilton says Dow never wrote one editorial on the theory alone (dow-editorials note). |
| Dow Theory as a name | Nelson's footnote "Dow's Theory" (nelson note) | russell-history-of-the-dow-theory:Q2 says Dow never used it | wikipedia-zh-dow-theory:Q2 credits Hamilton, Rhea and Schaefer with naming. That conflicts with Q2 of the Russell history, which treats Schaefer as a later theorist. |
| Primary 4 to 6 years | Dow, Jan 4, 1902 (dow-editorials:Q2) | Nelson:Q6, Hamilton:Q6, then rejected by hamilton:Q7 | incredible:Q3 still repeats Dow's number. reason-1974:Q2 says "at least four years" only. |
| Secondary "ten days to sixty days, averaging thirty to forty" | Dow, Jan 4, 1902 (dow-editorials:Q2) | Nelson:Q6, Hamilton:Q6, revised by hamilton:Q22 | Hamilton says the long end is rare. |
| Secondary "two weeks to a month or more" | Dow, Dec 1900 (dow-editorials:Q1) | Nelson:Q2, Hamilton:Q8 | |
| "Three weeks to three months" | Rhea 1932: "three weeks to as many months" (rhea:Q5) | Schannep reprint, Russell paraphrase (russell-history-of-the-dow-theory:Q5), Bassetti's glossary (edwards-magee:Q2), educators | The rhea note says the three-week minimum is Rhea's, not Dow's or Hamilton's. Rhea also wrote 3 to 12 weeks elsewhere (via Blay, unverified). wikipedia-en:Q3 "ten days to three months" mixes Dow and Rhea. The edwards-magee glossary was written by Bassetti, not in the 1948 text. |
| "33% to 66%" retracement | Rhea (rhea:Q5) | edwards-magee:Q2 (Bassetti glossary), wikipedia-en:Q4, thedowtheory-basics:Q4, aaii:Q4 | Not Dow. Dow gave only "at least three-eighths" (hamilton:Q11). |
| "1/3 to 2/3" | Russell, Bassetti and Blay rounding of Rhea | russell-history-of-the-dow-theory:Q5; wikipedia-zh:Q7 | Restatement, not Rhea's wording. |
| "50% typical" retracement | Dow's "about half" for a 2-3 point stock rise (nelson:Q19, Ch. XXX); Russell/Schaefer 50% Principle (paraphrase) | | No note gives 50% as a typical retracement of the averages. Nelson's attribution of Ch. XXX is unsettled. |
| "Three-eighths" | Dow, Jul 20, 1901 (dow-editorials:Q5) | Nelson:Q15, Hamilton:Q11, reason-1974:Q1 | Stated for stocks, not the averages. |
| Lines "5% and two to three weeks" | Rhea (rhea:Q8) | Blay, reason-1974, incredible:Q7, edwards-magee, stockcloud | Dow and Hamilton gave points for stocks and averages (dow-editorials:Q4; hamilton:Q10). Dow's line is a single-stock chart (nelson:Q11,Q12). |
| Rhea's 3% filter | Rhea (rhea:Q7) | Schannep (schannep:Q1) | rhea note: the 3% and 5% filters are not in Dow or Hamilton. The contract key `hamilton_3pct_filter` is misattributed. |
| Confirmation | Hamilton (hamilton:Q17,Q21,Q25) | Rhea:Q6, Edwards-Magee:Q4, Kirkpatrick-Dahlquist:Q6 | russell-history-of-the-dow-theory:Q4: Hamilton first defined it. nelson:Q5 shows Dow only watching the averages. thismatter:Q10 credits Dow. |
| HH/HL trend definition | Dow, Jan 4, 1902 (dow-editorials:Q3; nelson:Q8) | Rhea (paraphrase), Edwards-Magee, educators | Dow uses highs for a bull period and lows for a bear period. Letter shorthand HH/HL/LH/LL is modern (kcm:Q3-Q7). |
| Phases | Rhea (paraphrase, Wiley p.7; brown:Q10,Q11) | incredible:Q8,Q9; kirkpatrick-dahlquist; edwards-magee | Not in Dow, Nelson or Hamilton 1922 (their notes). Schaefer and Russell use a third speculative phase (russell-history-of-the-dow-theory). The accumulation, participation, distribution names are not traceable to a primary source. |
| "Not infallible" | Rhea (rhea:Q2) | incredible:Q12, thismatter:Q3, thedowtheory-basics:Q10 | Hamilton says "not perfect" (hamilton:Q14). Nelson says no infallible plan has been found (nelson:Q22). |
| Primary not manipulable | Rhea Hypothesis 1 (paraphrase) | Hamilton:Q18 is the source for the idea (hamilton note) | |
| Closing prices | Hamilton:Q24 | Rhea:Q1, Edwards-Magee:Q5, brown:Q12 | Nelson does not mention closing prices (nelson note). |
| Attributed to Dow, Jan 31, 1901 | no current note carries this editorial | | thedowtheory-basics:Q1-Q3 attribute "three movements ... most deceptive ... usually unimportant" to it. That wording equals Rhea via Schannep (rhea:Q3; aaii:Q1-Q3). Not traceable to Dow. |
| Wording drift | | | incredible:Q2 says "buying and selling" where nelson:Q6 and hamilton:Q6 say "buying or selling". |
| Dow's theory was incoherent | kirkpatrick-dahlquist (3rd ed., snippet paraphrase) | | Dow wrote for about five years and never assembled a coherent theory. |

## 4. Phases by source

| source | bull phases | bear phases | label |
|---|---|---|---|
| dow-editorials, nelson, hamilton | none (notes) | none | — |
| rhea (paraphrase, Wiley p.7) | reviving confidence; response to earnings; rampant speculation | abandonment of hopes; decreased business and earnings; distress selling | no-narrative |
| brown:Q10,Q11 | same text as Rhea | same | no-narrative |
| incredible:Q8,Q9 | reviving confidence first | abandonment of hopes first | no-narrative |
| kirkpatrick-dahlquist (snippet paraphrase) | not visible | hopes abandoned; selling on decreased earnings; distress selling | no-narrative |
| edwards-magee (snippet paraphrase) | accumulation, public participation, distribution | not shown | no-narrative |
| russell-history-of-the-dow-theory | Schaefer/Russell: third speculative phase needed before a top | — | no-narrative |
| stockcharts:Q4,Q5,Q6 | accumulation, big move, excess (summary) | distribution, big move, despair (summary) | no-narrative |
| wikipedia-en-dow-theory:Q6,Q7,Q8 | accumulation, public participation, distribution | no separate sequence | no-narrative |
| thismatter-dow-theory:Q8,Q9 | phase 1 cheap buying; phase 2 economy prospers | not shown | no-narrative |
| rich01-what-is-dow-theory:Q9,Q10,Q11 | accumulation, participation, excess | distribution, participation, panic | no-narrative |
| wantgoo-dow-theory:Q4,Q5,Q6; stockfeel-dow-theory:Q8-Q11 | accumulation, public participation, distribution | none | no-narrative |
| zh-ctyeh-dow-theory:Q10-Q16 | accumulation, euphoria | distribution, panic, despair (modern additions per note) | no-narrative |
| wikipedia-zh-dow-theory | none | none | — |

## 5. Performance evidence

**Brown, Goetzmann, Kumar (1998).** Full text, but a working-paper draft.
- 255 editorials, 11 dropped (Q20). Right 110 times, wrong 74 (Q23). Fisher test significant at 1% (Q24).
- Raw return 10.73% against 10.75% for the market (Q29). Sharpe 0.559 against 0.456, Jensen alpha 4.04%, beta 0.326 (Q30, Q31).
- Event study: bull calls +1.5%, bear calls -1.74% over 40 days (Q33), p = 0.034 (Q34).
- Out of sample is a neural-net imitation of Hamilton, not mechanical Dow rules. The next-day variant earned 9.87% geometric against 5.48% for the DJIA (note, Table IV). Q41 says frictions would remove most of the excess.
- Problems: the text says 9.95% where the table says 10.73%; a single scorer; trading at the prior close may be an artefact; the out-of-sample benchmark excludes dividends and cash earns zero; the paper cites Cowles as 1934.

**Cowles (1933).** Full text. The figures are reliable, but the test has no risk adjustment.
- Hamilton earned 12% a year against 15.5% for buy-and-hold on industrials, with a normal return near 5% (Q11, Q12, Q14). Rails: 5.7% against 7.7% (Q15).
- Long 55%, short 16%, out 29% of the time (Q16).
- 90 changes of position, 45 successful and 45 unsuccessful (Q21, Q26, Q27). Breakdown: 29 bullish with 16 profitable, 23 bearish with 10 profitable, 38 withdrawals with 19 profitable (Q17-Q20). Rails: 41 successful, 49 not (Q22). 1909 to 1914: minus 7.8% a year versus a 5% loan (Q23).
- **Citation issues.**
  - Brown, Goetzmann and Kumar cite 1934.
  - wikipedia-en:Q17 also says Cowles 1934 and the window "1902 to 1929".
  - kirkpatrick-dahlquist:Q8 (first edition) says 1937.
  - The correct year is 1933 (Econometrica 1(3)).
  - The cowles-1934-follow-up note finds no 1934 piece. The later paper is the 1944 Econometrica article, seen only as a snippet.
  - Cowles's own window is December 1903 to December 1929 (Q11) and 1904 to 1929 (Q25).
- **"Half" paraphrase.** Brown, Goetzmann and Kumar Q18 says half the changes were profitable. Cowles gives 45 and 45 out of 90 (Q21), so the paraphrase is faithful.
- The test trades rails and industrials together, so it does not test the confirmation rule.
- Count mismatch: Russell says Hamilton wrote 252 editorials (russell-history-of-the-dow-theory:Q3). Cowles and Brown, Goetzmann and Kumar say 255.

**Sideris (UNC Wilmington, about 2008).** Unverified and unreadable PDF. A search-tool paraphrase says no significant alpha (Q4). The figures 10.21% against 11.28%, Sharpe 0.37 against 0.31, and alpha minus 0.47% come from auto-summaries and conflict. Do not cite them.

**StockCharts 70-year claim.** stockcharts:Q11 says a Dow Theory system beat buy-and-hold by about 2% a year over 70 years. No author or study is named. Reliability: low.

**Schannep and Blay.**
- aaii:Q11 and schannep:Q11 claim the traditional theory beat buy-and-hold by 1% to 2% a year, unsourced.
- thedowtheory-schannep-vs-classical: 32 trades against 24 (Q7); average loss minus 6.48% against minus 7.85% (Q8); 100 dollars grew to 14,973 against 8,756 (Q9); "ca. 2%" outperformance (Q10); 28.7% more profit in secular bears (Q11). Window 1954 to 2013.
- **Reliability: promotional and unverified.** The author sells Schannep's newsletter.
- My arithmetic, assuming 59 years: the terminal values imply about 8.9% against 7.9% a year, a gap near 1 point. The note does not say what the "ca. 2%" refers to.

**Anecdotal calls.** russell-history-of-the-dow-theory reports Rhea's July 8, 1932 bottom call and 1937 top call, and Schaefer's 1949 buy and 1966 sell. It gives no statistics.

**Other.**
- Takasugi's 5.6 month volume lead has no stated method (takasugi:Q2).
- wikipedia-en:Q21 gives a 2% buy-and-hold gap. It matches neither Cowles's 3.5 points nor Brown, Goetzmann and Kumar's 0.02.
- rich01 Q21 and Q22 remark that risk and return is not clearly better than buy-and-hold, with no source.
- kirkpatrick-dahlquist:Q7 reports the risk-adjusted finding of Brown, Goetzmann and Kumar.
- academic-search-log finds no peer-reviewed test of Dow Theory after 1998.
- reason-1974:Q14 reports the Barbour objection that Cowles chose an unlucky period.
- hamilton:Q14 is Hamilton's own admission that the barometer is not perfect.

## 6. Defense line and support/resistance drawing

**Negative result on the defense line.** No source defines or names this construct; see zh-defense-line-search-log.
- Eight queries, five standard and three extended, found nothing. None of the roughly 40 fetched pages used the term as Dow Theory vocabulary.
- Hits were military, corporate three-lines-of-defense risk models, and casual labels on trader chart ideas for neckline or moving-average levels (zh-defense-line-search-log:Q1).
- The search tool is US-only, so the conclusion is "not found", not "does not exist".
- The first-hand and textbook notes for hamilton, nelson, dow-editorials, rhea, edwards-magee, kirkpatrick-dahlquist, and russell-history-of-the-dow-theory also record the defense line as not mentioned.
- Nearest concepts: the narrow-range line (R-022), the Blay stop-loss on secondary lows (R-048), and Schaefer's 50% Principle level (R-065), which is not a drawn line.

**What sources do say about drawing.**
- Dow himself (nelson:Q11, Q12, Q14) describes a "book method" chart of price changes with lines, and double tops. He gives no trendline or support rule.
- Hamilton, Rhea and Edwards-Magee's Dow chapters give no S/R or trendline drawing rule. Edwards-Magee cover support and resistance in a separate chapter.
- zh-stockcloud-dow-theory-trendline (a Chinese textbook summary, book not named):
  - Join two successive rising lows for an uptrend line and two highs for a downtrend line (Q7, Q8, Q21).
  - Use a log chart (Q5, Q6) and prefer about 45 degrees (Q10).
  - A valid break needs two consecutive closes, or a close beyond the line by 3% or more (Q14, Q17, Q19). These are alternatives.
  - Support and resistance swap roles (Q13). Volume should confirm (Q22, Q23, Q25).
- zh-stockcloud-dow-theory-line: the range limits are the breakout levels (Q9, Q10). No further drawing procedure.
- cmt:Q10 and incredible:Q7 describe lines but give no drawing rule.
- OANDA pages: resistance joins highs and support joins lows, with role reversal after a break (oanda-bvi-dow-theory-after-breakout:Q2; breakout-return-moves:Q4, Q5; trend-continuation:Q8). No drawing method.
- kcm:Q9, Q19: horizontal levels from repeated tests, no procedure.

## 7. Gaps the algorithm must fill

- **Swing threshold.** The only numeric swing filter is Rhea's 3% (R-013, second-hand). The 10% secondary threshold, ATR multiple and pivot width are agent-defined.
- **Primary versus secondary boundary.** No source gives an objective size or time cut. Schaefer would drop the limits altogether.
- **Retracement.** Base: last uncorrected move (Rhea) or full preceding swing. Whether it applies to averages or stocks, since Dow's 3/8 was stated for stocks. Whether it is binding.
- **Confirmation window.** No maximum lag between the two averages.
- **Reversal trigger.** Order of lower high before lower low, whether equal highs count, and one close versus two beyond the level. Orthodox theorists and Schaefer disagree on whether a break of secondary lows alone is a bear signal. The contract's strict flag has no source.
- **Closes versus extremes.** Lines and signals are on closes (R-036). Trendlines can use closes or extremes.
- **Line geometry.** Total range or plus/minus about the mean. Which base price. Sessions versus calendar weeks. Breakout filter size, if any (R-028).
- **Trendline details.** Fit method, tolerance, linear versus log, touches, break filter (R-050 to R-053).
- **S/R zones.** Zone width and touch count have no source (R-047).
- **Volume.** The ^DJI and ^DJT series carry no volume. No source defines the volume metric. Hamilton and educators disagree about reactions (R-038).
- **Secondary classification.** Rhea had trouble deciding what counted (thedowtheory-lines-special-issue:Q15).
- **Index composition.** Constituents have changed since the early 1900s (rich01 Q17; stockfeel Q19), which limits historical backtests.
- **Contract fixes needed.**
  - Rename or relabel `status_labels.hamilton_3pct_filter`. It is single-source and belongs to Rhea via Schannep.
  - Mark the `secondary_pct` of 0.10 as agent-defined.
  - State that `volume_confirms` follows the educator reading of reaction volume, not Hamilton's.
