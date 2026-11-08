---
name: dow-theory-sources
description: >-
  Literature layer of the Dow project: what the Dow Theory sources say, with the glossary and its
  Chinese term mapping, the labels and R-0xx rule ids, the canonical rules with disputed figures side
  by side with their sources, the provenance chain from Dow to educators, the performance evidence,
  and the negative result that the defense line has no literature source. Use when asked what Dow
  Theory says about X, who first said Y, whether Z is canonical or a modern variant, how long a
  secondary reaction lasts or retraces, whether Dow required two-average confirmation, whether Dow
  Theory beats buy-and-hold, what literature-disputed or agent-defined means, or what 道氏理論 / 道氏防線 /
  支撐線 / 壓力線 / 主要趨勢 / 次要趨勢 / 小型趨勢 mean. Not covered: swing detection → dow-swing-detection; trend state
  and defense-line definition → dow-trend-classification; line detection and pair confirmation →
  dow-confirmation-and-line; support, resistance, trendlines, charts → dow-levels-and-chart; backtest
  results and data labels → dow-rule-backtest.
---

# dow-theory-sources: Glossary, labels, canonical rules and evidence

> This skill is the literature layer of the Dow project. Its knowledge comes from the synthesis in `../../../research/canonical_rules.md`, built from the 42 source notes under `../../../research/sources/` (the registry header says 43; one note, the academic search log, has since moved to `../../../research/`). It covers the glossary (primary, secondary and minor trend; line; confirmation and non-confirmation; defense line; support, resistance and trendline; the three phases), the provenance chain Dow → Hamilton → Rhea → Schaefer and Russell → Schannep and Blay → educators, and the performance studies (Cowles, Brown Goetzmann Kumar, Sideris, StockCharts, Schannep). It reads no code and runs no script. Every quantitative statement carries exactly one literature label from 【literature-consensus】【literature-disputed】【single-source】【agent-defined】, and a data label from 【data-confirmed】【data-refuted】【insufficient-evidence】 only where a backtest exists. Double quotes are reserved for verbatim source text and carry a `(slug:Qn)` pointer into `../../../research/sources/<slug>.md`; everything else is paraphrase. The skill describes what sources say about trend state. It never predicts prices and it is not investment advice.

## When to Use

Use this skill for questions about the literature, not about the project's algorithms or data:

- What does Dow Theory say about X (secondary duration, retracement, lines, confirmation, volume, phases)?
- Who first said Y (Dow, Hamilton, Rhea, Schaefer, Russell, Schannep, an educator)?
- Is Z canonical, disputed, a single-source claim, or a modern variant?
- What does a label such as 【literature-disputed】 or an id such as `R-006` mean?
- Does Dow Theory beat buy-and-hold, and how reliable is each study?
- Is the Dow defense line (道氏防線) a Dow Theory term?
- What is the English term for 主要趨勢, 次要趨勢, 小型趨勢, 支撐線, 壓力線 or 盤整?

Do not use it to detect swings, classify a trend, draw a chart or run a backtest. Those are sibling skills (see Boundaries).

## Prerequisites

1. **Files that must be readable** (paths are relative to this skill directory; `../../../` is the project root):
   - `../../../research/canonical_rules.md` (rule registry `R-001` to `R-065`, matrices, provenance chain, performance evidence).
   - `../../../research/sources/<slug>.md` (one note per source, verbatim `Qn` quotes, `access:` flag).
   - `references/evidence.md` in this skill (every quote and rule id used below, grouped by Workflow step, with URL).
2. **Hard rule against filling gaps.** Answer only from those files. If a figure is not in the registry, say it is not sourced in this project. Never adjudicate a dispute; list the positions side by side with their sources.
3. **Label discipline.** One literature label per figure. Label definitions are in Workflow Step 2 and are owned by this skill; siblings reference them and never restate them.
4. **No code dependency.** This skill does not import `dowtheory`. Where a rule's implementation status matters, point to the `contract` column of the registry and to the sibling skill.

## Workflow

**Step 1 - Resolve the term (glossary)**

Map the user's word to the project term, then to the rule id that defines it. Chinese mapping, one line: 道氏理論 = Dow Theory; 主要趨勢 = primary trend; 次要趨勢 = secondary reaction; 小型趨勢 = minor (daily) movement; 道氏防線 = Dow defense line (agent-defined); 支撐線 = support; 壓力線 = resistance; 盤整/線 = line (narrow range).

| Term | Working definition (paraphrase) | Rule ids | Label |
|---|---|---|---|
| Primary trend (main movement) | The broad bull or bear movement that the other two ride on; direction is a state, not a duration test | R-001, R-002, R-003, R-005 | 【literature-consensus】on three movements; durations disputed (Step 3) |
| Secondary reaction (medium swing) | An important counter-move against the primary; duration and retracement figures disputed | R-006 to R-011 | 【literature-disputed】on figures |
| Minor movement (daily fluctuation) | Day-to-day moves, low information except while a line forms | R-014, R-015 | 【literature-consensus】on low information |
| Trend by highs and lows | Dow: bull period while each high exceeds prior highs; bear period once a low undercuts prior lows. Rhea and educators require both highs and lows | R-016 | 【literature-consensus】 |
| Line | Narrow sideways range in both averages, read as accumulation or distribution | R-022 to R-027 | 【literature-consensus】on definition; band and duration figures one lineage (Step 3) |
| Confirmation | A move in one average is unreliable until the other average moves the same way; no fixed lag | R-032, R-033, R-034 | 【literature-consensus】 |
| Non-confirmation | The two averages diverge; a warning, not a signal in itself | R-032 (wikipedia-en Q11) | 【literature-consensus】 |
| Dow defense line | The last secondary low in a bull trend or secondary high in a bear trend, used as a break level. Project construct; definition lives in `dow-trend-classification` | R-045 | 【agent-defined】 |
| Support, resistance, trendline | Educator constructs adjacent to Dow Theory; no drawing rule in Dow, Hamilton or Rhea | R-049 to R-055 | 【single-source】or educator-only consensus per row |
| Three phases | Rhea's schema; two naming schemes; no measurable rule | R-042 to R-044 | 【literature-consensus】on the count, 【literature-disputed】on names |

**Step 2 - Read the label and the id**

| Label | Meaning (from `canonical_rules.md` section 0) |
|---|---|
| 【literature-consensus】 | At least two independent sources agree and none contradicts. Agreement without conflict; it does not mean independent rediscovery |
| 【literature-disputed】 | At least two sources give materially different figures or opposing readings; positions shown side by side, no adjudication |
| 【single-source】 | One source states it, or later sources only echo it |
| 【agent-defined】 | The project's own construct, no literature source |
| 【data-confirmed】【data-refuted】【insufficient-evidence】 | Data layer; set only by `dow-rule-backtest` after the hashed decision table |

Rule ids read `R-0xx`; each row of the registry carries the statement, the figures, agreeing and disagreeing sources as `slug:Qn`, label, provenance tag (`P-Dow`, `P-Ham`, `P-Rhea`, `SEC`, `EDU`, `MOD`), a verified flag (yes, no, partial) and the contract column. Verified yes means the figure sits in a full-text note: hamilton, nelson, brown-goetzmann-kumar-1998, cowles-1933-can-forecasters-forecast, russell-history-of-the-dow-theory. An echo (Blay repeating Schannep) counts as one source. The registry is grouped 1.1 trends, 1.2 secondary, 1.3 reversal, 1.4 lines, 1.5 confirmation and volume, 1.6 phases, 1.7 agent-defined, 1.8 adjacent constructs, 1.9 evidence.

**Step 3 - Digest of the core rules (disputed figures side by side)**

Secondary duration, `R-006` and `R-007`, 【literature-disputed】:

| Position | Figure | Source |
|---|---|---|
| Dow, Dec 1900 | "running from two weeks to a month or more" (hamilton-1922-stock-market-barometer:Q8) | also nelson-1903-abc-of-stock-speculation:Q2 |
| Dow, Jan 1902 | "The secondary movement covers a period ranging from ten days to sixty days, averaging probably between thirty and forty days." (hamilton-1922-stock-market-barometer:Q6) | also nelson-1903-abc-of-stock-speculation:Q6 |
| Hamilton | "this longer range is exceedingly rare and that the duration may be appreciably less than forty days" (hamilton-1922-stock-market-barometer:Q22) | first-hand |
| Rhea | "usually lasting from three weeks to as many months" (rhea-1932-the-dow-theory:Q5) | via Wiley reprint; Blay reads the usually as allowing shorter (thedowtheory-rhea-three-weeks:Q2) |
| Rhea alt. (`R-006`; the 15-day and 5 percent screen is filed under `R-013`) | 3 to 12 weeks; 15-day and 5 percent screen in his statistics | rhea note paraphrase via Blay, unverified |
| Schannep (`R-006`) | "It can be as short as 8 trading days (or even less following capitulation)." (thedowtheory-lines-special-issue:Q8) | the face-off page says "10 days, or even less, is enough to qualify a movement as a secondary reaction." (thedowtheory-schannep-vs-classical:Q3) |
| Schaefer | no limit on secondaries | russell-history-of-the-dow-theory:Q6 |

Secondary retracement, `R-008` to `R-011`, 【literature-disputed】:

| Position | Figure | Source |
|---|---|---|
| Dow, Jul 1901 (for a stock) | "at least three-eighths of the primary movement" (hamilton-1922-stock-market-barometer:Q11) | also nelson-1903-abc-of-stock-speculation:Q15; minimum only, no upper bound |
| Dow, small moves | "it very generally swings back about half of the amount of the advance" (nelson-1903-abc-of-stock-speculation:Q19) | Ch. XXX attribution unsettled |
| Rhea (`R-008`, `R-009`) | "retraces from 33 percent to 66 percent of the primary price change since the termination of the last preceding secondary reaction" (rhea-1932-the-dow-theory:Q5) | base = move since last secondary |
| Russell on Rhea | "retrace one-third to two-thirds of the preceding uncorrected primary advance" (russell-history-of-the-dow-theory:Q5) | rounding, not Rhea's wording |
| Taiwan educator (`R-009`) | 1/3 to 1/2 of the prior swing | stockfeel-dow-theory:Q6 |
| Schannep (`R-012`) | "that it shall exceed 3% on either of the averages." (schannep-dow-theory-21st-century:Q1) | replaces the fraction; "a secondary trend will usually extend at least 4% on both the industrials and transportation averages." (schannep-dow-theory-21st-century:Q2) |
| Schaefer | none | russell-history-of-the-dow-theory paraphrase |

Primary duration, `R-002` to `R-004`, 【literature-disputed】:

| Position | Figure | Source |
|---|---|---|
| Dow, Dec 1900 | main movement covering at least four years | hamilton-1922-stock-market-barometer:Q8; nelson-1903-abc-of-stock-speculation:Q2 |
| Dow, Jan 1902 | great swing of four to six years | hamilton-1922-stock-market-barometer:Q6; nelson-1903-abc-of-stock-speculation:Q6; "Bull markets and bear markets run four and five years at a time." (nelson-1903-abc-of-stock-speculation:Q1) |
| Hamilton | before Dow never four to six years, "rarely three years and oftener less than two" (hamilton-1922-stock-market-barometer:Q7); at least a year (Q2) | first-hand rejection of Dow's figure |
| Hamilton averages | "The average duration of seven major bull swings is twenty-five months; while the average duration of seven major bear swings is fifteen months." (hamilton-1922-stock-market-barometer:Q13) | 1900 to 1923; 【single-source】 R-004 |
| Rhea | "extending over periods that have varied from less than a year to several years" (rhea-1932-the-dow-theory:Q4) | via Wiley |
| Educators | months to years; one year or more | stockcharts-chartschool-dow-theory:Q1; stockfeel-dow-theory:Q4; wikipedia-en-dow-theory:Q2 |

Lines, `R-022` to `R-025`:

| Item | Figure | Source | Label |
|---|---|---|---|
| Definition | narrow range in both averages, accumulation or distribution; Hamilton: "a succession of closing prices, over a sufficient number of days for a fair volume of trading within a narrow range" (hamilton-1922-stock-market-barometer:Q24) | Dow, Hamilton, Rhea, textbooks | 【literature-consensus】 |
| Dow's line | a single stock "will stay within a narrow range of prices, say two points" (hamilton-1922-stock-market-barometer:Q10) | book method, Jul 1901 | 【literature-consensus】on wording, points not percent |
| Rhea's band and time | "is a price movement extending two to three weeks or longer, during which period the price variation of both averages move within a range of approximately 5 percent." (rhea-1932-the-dow-theory:Q8) | Rhea via Wiley; echoed by Blay, Bishop, Incredible Charts, stockcloud | 【literature-consensus】one lineage, verified no |
| Schannep | lines "is an element of the classical Dow Theory which has been discarded by Schannep" (thedowtheory-lines-special-issue:Q14) | Blay | 【single-source】 |

Filters and confirmation:

| Item | Statement | Source | Label |
|---|---|---|---|
| 3 percent filter, `R-013` | "a rally or a decline is one or more daily movements resulting in a net reversal of direction exceeding 3 percent of the price of either average." (rhea-1932-the-dow-theory:Q7) | Rhea only, reused by Schannep; absent from Dow and Hamilton | 【single-source】 |
| Confirmation, `R-032` | "One of the shortest ways of going wrong is to accept an indication by one average which has not been clearly confirmed by the other." (hamilton-1922-stock-market-barometer:Q21) | Hamilton first; "it was Hamilton who first defined the confirmation principle of the Averages" (russell-history-of-the-dow-theory:Q4) | 【literature-consensus】 |
| Dow on averages | "He should observe the movement of the general market as indicated by the averages published daily" (nelson-1903-abc-of-stock-speculation:Q5) | Dow watches the averages; no two-average rule in Nelson | 【literature-consensus】that Dow did not state it |
| Lag, `R-033` | "It is sufficient if they take the same direction." (hamilton-1922-stock-market-barometer:Q25) | no maximum lag anywhere | 【literature-consensus】 |
| Schannep pair, `R-035` | "It uses three indices (it includes the S&P), instead of just two, whereas it requires just two indices to confirm." (thedowtheory-schannep-vs-classical:Q2) | one promotional page | 【single-source】 |
| Bull and bear status, `R-021` | "The levels at which I consider that a market attains bull- or bear-market status are +19% and –16% as mentioned previously." (aaii-dow-theory-21st-century:Q8) | Schannep, echoed by Blay | 【single-source】 |

**Step 4 - Place the claim on the provenance chain**

Chain: Dow (editorials 1900 to 1902, read in Nelson 1903 and in Hamilton 1922) → Hamilton (1922 book, first-hand) → Rhea (1932, read only through the Wiley reprint inside Schannep 2008 and through Blay) → Schaefer and Russell (Russell's history essay, first-hand) → Schannep and Blay (AAII article and thedowtheory.com, partial) → educators and encyclopedias (partial, tool-extracted).

| Claim | Earliest traceable | Verification status | Label |
|---|---|---|---|
| Three movements | Dow, Dec 1900 | first-hand in nelson and hamilton | 【literature-consensus】 |
| Dow Theory as a name | Nelson's footnote; "But Dow himself never once used the term." (russell-history-of-the-dow-theory:Q2) and "Dow himself never used the term Dow theory nor presented it as a trading system." (wikipedia-en-dow-theory:Q1) | first-hand (russell) and partial (wikipedia) | 【literature-consensus】 |
| Ten to sixty days, four to six years | Dow, Jan 1902 | first-hand; Hamilton's own rejection first-hand | 【literature-disputed】 |
| Three weeks to three months, 33 to 66 percent | Rhea 1932 | second-hand only (Wiley excerpt, Blay, Russell paraphrase) | 【literature-disputed】with Dow |
| Three-eighths | Dow, Jul 1901, stated for stocks | first-hand | 【literature-disputed】with Rhea |
| 5 percent line, two to three weeks | Rhea 1932 | second-hand | 【literature-consensus】one lineage |
| 3 percent filter | Rhea 1932 | second-hand; the contract key `hamilton_3pct_filter` misattributes it | 【single-source】 |
| Confirmation | Hamilton 1922 | first-hand; not Dow | 【literature-consensus】 |
| Closing prices only | Hamilton 1922; Rhea hypothesis via brown-goetzmann-kumar-1998:Q12 | first-hand | 【literature-consensus】 |
| Three phases | Rhea 1932 (Hamilton 1922 has no schema) | second-hand; names in brown-goetzmann-kumar-1998:Q10,Q11 | 【literature-disputed】on names |
| Schaefer 50 percent principle and no-limit secondaries | Russell essay | first-hand paraphrase in a newsletter | 【single-source】 |

**Step 5 - Weigh the performance evidence (`R-062`, 【literature-disputed】)**

| Study | Result | Reliability | Label |
|---|---|---|---|
| Cowles 1933, Econometrica | Hamilton "would have earned a return, including dividend and interest income, of 12 per cent per annum" (cowles-1933-can-forecasters-forecast:Q11) while the industrials "showed a return of 15.5 per cent per annum" (cowles-1933-can-forecasters-forecast:Q12); "In all, 45 of his changes of position were unsuccessful, 45 successful." (cowles-1933-can-forecasters-forecast:Q21) | full text; no risk adjustment; rails and industrials traded together so confirmation is untested | 【single-source】full text, verified yes |
| Cowles citation year | Brown, Goetzmann and Kumar and wikipedia-en cite 1934; kirkpatrick-dahlquist first edition writes "Cowles III ( 1937 ) performed the first formal test of the profitability" (kirkpatrick-dahlquist-technical-analysis-dow-theory:Q8); the project's bibliographic check against the Econometrica PDF gives 1933 | project check, not a literature position | 【agent-defined】bibliographic check |
| Brown, Goetzmann, Kumar 1998 | "In total, Hamilton was right 110 times and wrong 74 times, by our count." (brown-goetzmann-kumar-1998:Q23); raw return 10.73 percent against 10.75 percent (Q29); "the Hamilton portfolio has a higher Sharpe ratio (0.559 compared with 0.456) and a positive Jensen measure of 4.04 percent" (brown-goetzmann-kumar-1998:Q30); beta 0.326 (Q31); bull calls "are followed by a 1.5 percent price increase over the next 40 days on average" (brown-goetzmann-kumar-1998:Q33) | full text, working-paper draft; one scorer; text says 9.95 where the table says 10.73; out-of-sample is a neural-net imitation, not Dow rules; "normal trading frictions would preclude using the Theory to generate large excess returns" (brown-goetzmann-kumar-1998:Q41) | 【single-source】full text, verified yes |
| Sideris, UNC Wilmington, about 2008 | "unsuccessful in producing a significant alpha measurement" (sideris-russell-dow-theory-thesis:Q4) | search-tool paraphrase of an unreadable PDF; its numbers conflict and must not be cited | 【single-source】unverified |
| StockCharts 70-year claim | "Over the 70-year period, the Dow Theory system outperformed a buy-and-hold strategy by about 2% per year." (stockcharts-chartschool-dow-theory:Q11) | no author or study named; partial access | 【single-source】unidentified |
| Schannep and Blay face-off, 1954 to 2013 | 32 trades against 24, growth of 100 dollars to 14,973 against 8,756, "outperformance of ca. 2%" (thedowtheory-schannep-vs-classical:Q10); AAII: "Historically, the traditional Dow Theory has outperformed a buy-and-hold approach by 1% to 2% a year." (schannep-dow-theory-21st-century:Q11) | promotional, newsletter vendor, unsourced; project arithmetic 【agent-defined】: the terminal values over 59 years imply about 8.9 percent against 7.9 percent a year, a gap near 1 point | 【single-source】promotional |

Summary sentence to reuse for `R-062`: raw returns do not beat buy-and-hold in either full-text study, a risk-adjusted edge appears only in Brown, Goetzmann and Kumar, and every claim of a 1 to 2 percent raw edge is unsourced or promotional. The academic search log finds no peer-reviewed test after 1998. Data labels for the project's own backtests come only from `dow-rule-backtest`.

**Step 6 - State the negative result on the defense line (`R-045`, 【agent-defined】)**

The search log records "no page defines 道氏防線 or uses 防線 as a Dow Theory term in any page read" (zh-defense-line-search-log:Q1). Eight queries found military, corporate-governance and casual trader uses only; the search tool is US-only, so the result is not found rather than does not exist. The hamilton, nelson, rhea, dow-editorials, edwards-magee, kirkpatrick-dahlquist and russell-history notes all mark the defense line as not mentioned. Nearest analogues, none a drawn line: Blay's secondary lows as stop-loss (`R-048`, 【single-source】), Rhea's narrow-range line (`R-022`), Schaefer's halfway level (`R-065`, 【single-source】). Always say: the Dow defense line is this project's construct; its definition and break rule live in `dow-trend-classification`; never present it as canonical.

**Step 7 - Answer procedure for any literature question**

1. Locate the rule id in `../../../research/canonical_rules.md` section 1 (or say none exists).
2. Report the label from the row, and the verified flag.
3. List every position side by side with `slug:Qn`, quoting verbatim only where the note has the text; mark paraphrase-only figures as such.
4. State the verification status: first-hand (full-text note), second-hand (Rhea via Wiley or Blay), tool-extracted (`access: partial`), or unverified (snippet).
5. Hand off: algorithm parameters → `dow-swing-detection`; trend state or defense line → `dow-trend-classification`; line detection or pair confirmation code → `dow-confirmation-and-line`; drawing → `dow-levels-and-chart`; numbers from runs → `dow-rule-backtest`.

## Output

A conversational answer, no files. Four parts:

1. **Verdict line**: rule id, label, one-sentence consensus statement or the word disputed.
2. **Positions table**: one row per source position (author, figure, `slug:Qn`, verification status). Never collapse a dispute into a single number.
3. **Provenance note**: who said it first and how this project saw the text (first-hand, Wiley reprint, Blay, tool-extracted).
4. **Hand-off**: which sibling answers the algorithm, chart or backtest part, or `../../../research/canonical_rules.md` section if the sibling is not installed.

## Examples

### Example 1: How long is a secondary reaction?

Verdict: `R-006` and `R-007`, 【literature-disputed】, no consensus figure. Positions: Dow 1900 two weeks to a month or more; Dow 1902 ten to sixty days averaging thirty to forty; Hamilton says over forty is exceedingly rare; Rhea usually three weeks to three months, with Blay noting the usually; Schannep eight or ten trading days; Schaefer no limit (table in Step 3). Provenance: the three-week floor is Rhea's, not Dow's or Hamilton's, and Rhea is second-hand here. Hand-off: the project records `duration_days` and applies no duration filter (`dow-swing-detection`).

### Example 2: Did Dow require two-average confirmation?

Verdict: `R-032`, 【literature-consensus】that confirmation is a Dow Theory rule, but its author is Hamilton. Positions: Hamilton states it first-hand (hamilton-1922-stock-market-barometer:Q17, Q21, Q25); Rhea restates it: "The movement of one price average must be confirmed by the other before reliable inferences may be drawn." (rhea-1932-the-dow-theory:Q6); Russell credits Hamilton (russell-history-of-the-dow-theory:Q4); Nelson's Dow chapters only say to watch the averages (nelson-1903-abc-of-stock-speculation:Q5) and the nelson note finds no two-average rule; thismatter credits Dow (thismatter-dow-theory:Q10, partial access). Provenance: Hamilton 1922, first-hand. Lag: no fixed window, `R-033`. Hand-off: `pair_confirm` behaviour → `dow-confirmation-and-line`.

### Example 3: Does Dow Theory beat buy-and-hold?

Verdict: `R-062`, 【literature-disputed】. Positions for `R-062` (table in Step 5): Cowles 12 against 15.5 percent raw with 45 of 90 calls right, Brown, Goetzmann and Kumar raw 10.73 against 10.75 percent with Sharpe 0.559 against 0.456 and alpha 4.04 percent, Sideris no significant alpha and unverified, StockCharts about 2 percent a year from an unidentified study, Schannep 1 to 2 percent and promotional. Provenance: only Cowles and Brown, Goetzmann and Kumar are full text. Hand-off: this project's own result on 1992 onward data, with its data label, comes from `dow-rule-backtest`; until it exists, no data label applies.

### Example 4: Is 道氏防線 a Dow Theory term?

Verdict: `R-045`, 【agent-defined】. No source defines or names it (Step 6); the nearest published idea is Blay's stop at secondary lows, 【single-source】. The project's definition and the break rule are in `dow-trend-classification`; charts label it as agent-defined.

## Boundaries

| Not covered here | Sibling skill |
|---|---|
| Swing-point detection, percentage, ATR and pivot thresholds, `confirmed_idx`, no-lookahead rule (`R-046`) | `dow-swing-detection` |
| Trend state machine, HH/HL/LH/LL signals, SUSPECT states, defense-line definition and `DEFENSE_BREAK` (`R-016` to `R-018`, `R-045`) | `dow-trend-classification` |
| Line detection parameters, breakout rule, pair confirmation and `max_days` (`R-022` to `R-035` as code) | `dow-confirmation-and-line` |
| Support and resistance clustering, trendline fitting, chart rendering and labels (`R-047`, `R-049` to `R-055`) | `dow-levels-and-chart` |
| Decision table, backtest runs, data labels 【data-confirmed】【data-refuted】【insufficient-evidence】 (`R-062` tested) | `dow-rule-backtest` |

Glossary, label definitions, provenance and performance evidence are defined only here; siblings reference them. The siblings above may not be installed. When one is missing, read the matching section of `../../../research/canonical_rules.md` (section 1 for rules, section 7 for the gaps the algorithms fill) and `../../../docs/specs/algorithm_contract.md`.

## Limitations

1. **Rhea is second-hand.** Every Rhea figure (three weeks to three months, 33 to 66 percent, 3 percent, 5 percent, two to three weeks: `R-006`, `R-008`, `R-013`, `R-023`, `R-024`) comes through the Wiley reprint in Schannep 2008 or through Blay; Fraser page numbers are unverified. Verified flag no.
2. **Tool-extracted quotes.** Notes marked `access: partial` (StockCharts, Wikipedia, AAII, thedowtheory.com, Taiwan educators) were pulled by a fetch tool asking for exact sentences and were not re-checked against the live page.
3. **No Edwards and Magee or Kirkpatrick and Dahlquist full text.** Only Google Books snippets; their glossary figures are Bassetti's later text, not the 1948 edition.
4. **Dow's figures are for stocks.** The three-eighths and the two-point line were stated for individual stocks, not the averages; carrying them to an index is an inference.
5. **Consensus is one lineage.** Nearly all modern sources repeat Rhea, who built on Hamilton, who quoted Dow; agreement is not independent evidence.
6. **Performance studies are old and unlike the project's test.** Cowles and Brown, Goetzmann and Kumar score Hamilton's editorials over Cowles' own window, December 1903 to December 1929; this project's backtests use data from 1992 onward and mechanical rules, so neither study confirms or refutes the project's results.
7. **Negative search is bounded.** The defense-line search used a US-only tool; absence in Chinese-language sources is not proven.
8. **Not advice.** The skill reports what sources say about trend state. It makes no price prediction and gives no investment advice.

## Resources

- `references/evidence.md`: every verbatim quote and rule id used in this skill, grouped by Workflow step, each with `slug:Qn` and URL. Self-contained evidence file for this skill.
- `../../../research/canonical_rules.md`: rule registry (section 1), numeric matrices (2), provenance chain (3), phases (4), performance evidence (5), defense line and drawing (6), gaps (7).
- `../../../research/sources/<slug>.md`: 42 source notes with verbatim `Qn` quotes, access flag and reliability notes; `../../../research/SOURCE_NOTE_TEMPLATE.md` describes the format.
- `../../../research/academic-search-log.md`: log of the search for peer-reviewed tests after 1998.
- `../../../docs/specs/skill_contract.md` and `../../../docs/specs/algorithm_contract.md`: the contracts this skill and its siblings follow.
- `../../../scripts/check_quotes.py` and `../../../scripts/check_labels.py`: the linters that verify quotes and labels in this file.
