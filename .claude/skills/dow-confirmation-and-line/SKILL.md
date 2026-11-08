---
name: dow-confirmation-and-line
description: >-
  Dow project confirmation layer: two-average confirmation between Industrials and Transports
  (^DJI/^DJT), pair_confirm status confirmed / non_confirmation / pending with cycle-aware matching
  of reversals in either order and no time window, Dow lines (both averages inside a 5 percent
  band for at least 15 sessions, drift-filtered) with as-of-safe dual-confirmed breakouts, and the
  volume flag. Use when asked whether transports confirm industrials, whether
  a reversal is confirmed or a non-confirmation (divergence) holds, when a signal was matched by
  the other average, whether the market is in a line (sideways range, accumulation,
  distribution), whether a line breakout was confirmed by both, whether volume confirms,
  or 相互確認 / 盤整 / 量能 / 道氏理論 confirmation. Not covered: sources and labels →
  dow-theory-sources; swings → dow-swing-detection; trend state, HH/HL, defense line →
  dow-trend-classification; levels, trendlines, charts → dow-levels-and-chart; backtest results →
  dow-rule-backtest.
---

# dow-confirmation-and-line: Two-average confirmation, Dow lines and the volume flag

> This skill is the confirmation layer of the Dow project. Its knowledge comes from the code in `../../../src/dowtheory/confirmation.py` and `../../../src/dowtheory/line.py`, the driver `../../../src/dowtheory/analysis.py`, the frozen contract `../../../docs/specs/algorithm_contract.md` (line.py and confirmation.py sections, Deviations 9 to 13, Amendments A6 and A7), the configuration `../../../configs/dow.yaml` (`line:`, `confirmation:`) and `../../../configs/pairs.yaml`, and the synthesis `../../../research/canonical_rules.md` built from the source notes under `../../../research/sources/` (see `dow-theory-sources`). Glossary, Chinese term mapping and label vocabulary are owned by `dow-theory-sources`; swing definitions by `dow-swing-detection`; the trend state machine, its `REVERSAL_*` signals and the defense line by `dow-trend-classification`; all are referenced, never restated. Every quantitative statement carries exactly one literature label from 【literature-consensus】【literature-disputed】【single-source】【agent-defined】 and, where a backtest exists, one data label from 【data-confirmed】【data-refuted】【insufficient-evidence】. Double quotes are reserved for verbatim source text with a `(slug:Qn)` pointer; everything else is paraphrase. The line parameters that make Rhea's description executable are this project's choices and are labelled 【agent-defined】. The skill describes the confirmation state as of a date. It never predicts prices and it is not investment advice.

## When to Use

- Say whether the second average confirms the first as of a date: `confirmed`, `non_confirmation` or `pending`, and why.
- Say whether a `REVERSAL_UP` or `REVERSAL_DOWN` on one average has been matched by the other, on which date, and when the pair confirmation became knowable.
- List the Dow lines (joint sideways windows) in a period with their band widths, breakout direction and date, and whether both averages broke the same way.
- Report the informational volume flag and what it does and does not say.
- Phrase a non-confirmation correctly: a warning that the averages disagree, never a reversal.
- Feed pair status and line breakouts to a sibling (chart, backtest) without lookahead.

Do not use it to detect swings, classify one average's trend, quote the full source positions, cluster levels or report backtest numbers beyond the three rows in Step 7. Those are sibling skills (see Boundaries).

## Prerequisites

1. **Project checkout and environment.** The scripts import `dowtheory` from `../../../src/`. `scripts/_anchor.py` finds the repo through `DOW_PROJECT_ROOT`, or by walking up to a directory holding `pyproject.toml` and `src/dowtheory`, and re-executes the script under `<root>/.venv/bin/python`, so any `python3` works as the launcher. Global-install setup, one line:

   ```bash
   export DOW_PROJECT_ROOT=<path-to-Dow-repo>
   ```

2. **Data access.** Same two sources as `dow-swing-detection` Prerequisites 2 to 4: `--source clickhouse` (the default) reads `dow.mkt_klines` with `FINAL` inside the Docker container `trading_clickhouse` and needs `--symbol` and `--pair`; `--source csv --csv PATH [--csv-pair PATH]` reads one file per leg, the pair file defaulting to the first so a single fixture can stand in for both legs, with symbols defaulting to the upper-cased file stems. The two legs are inner-joined on session date before anything runs, exactly as `analysis.analyze` does. Run the integrity gate `.venv/bin/python scripts/check_integrity.py` from the project root before any ClickHouse-based analysis; CSV fixtures need no gate.
3. **Pairs.** `../../../configs/pairs.yaml` names `DJ` = `^DJI` with `^DJT` (the literature pair, `R-034`, 【literature-consensus】) and `SP_IYT` = `SPY` with `IYT` (the backtest robustness pair, 【agent-defined】; ETF volume is used where index volume is missing). `dow analyze --pair` defaults from this file (contract Deviation 13); the wrapper takes `--pair` explicitly.
4. **Upstream layers.** Both legs are run through `detect_multiscale`, `swings_as_of` and `run_trend` as in `dow-swing-detection` and `dow-trend-classification`; nothing about swings or states is defined here. `warmup_note` and start-date dependence (`dow-trend-classification` Step 6) apply to each leg separately.
5. **Configuration.** `line.band_pct` (default `0.05`), `line.min_sessions` (`15`), `line.max_drift_frac` (`0.5`) and `confirmation.max_days` (`null`) in `../../../configs/dow.yaml`. There are no CLI overrides; change the config to experiment.
6. **Siblings for definitions.** Term meanings and label semantics: `dow-theory-sources` Steps 1 and 2. Rule ids `R-0xx` refer to `../../../research/canonical_rules.md`.

## Workflow

**Step 1 - Two-average confirmation as implemented (`R-032`, 【literature-consensus】)**

The rule: a movement in one average is unreliable until the other average confirms it. Rhea: "The movement of one price average must be confirmed by the other before reliable inferences may be drawn." (rhea-1932-the-dow-theory:Q6). Hamilton: "One of the shortest ways of going wrong is to accept an indication by one average which has not been clearly confirmed by the other." (hamilton-1922-stock-market-barometer:Q21). Russell credits Hamilton, not Dow, with defining it: "it was Hamilton who first defined the confirmation principle of the Averages." (russell-history-of-the-dow-theory:Q4); the nelson note finds no two-average rule in Dow's own text (`R-032` provenance column).

How `pair_confirm` reads the two trend states (contract Deviation 10, 【agent-defined】 mechanics around `R-032`):

| A state vs B state | `status` | `pair_state` | Meaning |
|---|---|---|---|
| either `UNDEFINED` | `pending` | none | at least one average has no established trend yet (warm-up) |
| opposite sides (bull vs bear) | `non_confirmation` | none | the averages disagree on direction |
| same side, one PRIMARY and one SUSPECT | `non_confirmation` | none | one average has already failed to make a new extreme (lower high or higher low) |
| identical states | `confirmed` | that state | both averages agree |

Signal-level matching (`confirm_signal`, Amendment A7, 【agent-defined】 mechanics around `R-033`): a `REVERSAL_*` on A is matched with a same-kind `REVERSAL_*` on B inside the same primary cycle of A (between A's previous and next reversal), in either order, with no opposite-kind B reversal between the two; a leading or same-day B signal wins (the latest one), otherwise the earliest following one. `confirmed_ts` is the later of the two dates, so the status at any date equals `confirmed_ts <= date` and a run cut at `--end` reproduces the full run (no lookahead). `confirmation.max_days: null` means no time limit (`R-033`, 【literature-consensus】 that no maximum lag is given).

The time-window question, side by side and not adjudicated:

| Position | Statement | Rule | Label |
|---|---|---|---|
| Hamilton, no same-day requirement | "the averages must confirm each other, although they may not break out of their respective lines on the same day or in the same week. It is sufficient if they take the same direction." (hamilton-1922-stock-market-barometer:Q25) | `R-033` | 【literature-consensus】 |
| Brown, Goetzmann and Kumar, same reading | "the confirmation need not occur on the same day." (brown-goetzmann-kumar-1998:Q5) | `R-033` | 【literature-consensus】 |
| CMT study guide, same reading | "Confirmation can lag days or longer." (cmt-open-exam-prep-dow-theory:Q3) and "Waiting is part of the method." (cmt-open-exam-prep-dow-theory:Q4) | `R-033` | 【literature-consensus】 |
| Rhea on line breaks, simultaneity | Rhea's line passage, available only as a paraphrase in the rhea note (Wiley p.10, no Qn), speaks of simultaneous breaks out of a line; the registry records this as an internal tension with Hamilton Q25 | `R-026`, `R-033` disagreeing column | 【literature-consensus】 overall; the simultaneity wording is a paraphrase, not a verified quote |

The code imposes no window (`confirmation.max_days: null`); the Rhea simultaneity wording exists only as a paraphrase in this project's notes and could not be coded from them, and both readings stay listed above without ranking. The registry marks `R-033` as only partly algorithmizable because no source gives a maximum lag; its contract column records it as implemented with `max_days` None. Example 2 shows a match ten months apart (2003-06-04 matched by 2004-04-06) that a window would have rejected.

A non-confirmation is a warning, never a reversal (`R-032`, 【literature-consensus】): "When the performance of the averages diverges, it is a warning that change is in the air." (wikipedia-en-dow-theory:Q11). The averages must both start the new trend before a market is called (`R-032`): "A bear market commences when a bear trend on one average is confirmed by the start of a bear trend on the other average." (incrediblecharts-dow-theory-trends:Q11). Only `dow-trend-classification` declares a reversal on one average; this skill says whether the other average has joined it.

**Step 2 - Run**

```bash
# from this skill directory; any python3 re-executes under the project .venv
python3 scripts/confirm.py --symbol ^DJI --pair ^DJT --start 2015-01-01
python3 scripts/confirm.py --symbol ^DJI --pair ^DJT --json
python3 scripts/confirm.py --source csv --csv ../../../tests/fixtures/dji_sample.csv
python3 scripts/confirm.py --source csv --csv tests/fixtures/pair_a_sample.csv --csv-pair tests/fixtures/pair_b_sample.csv --end 2021-04-12
```

The wrapper loads both legs, inner-joins them on session, runs swings and trend for each leg exactly as `analysis.analyze` does, then calls `detect_lines`, `pair_confirm`, `confirm_signal` for every A reversal, and `volume_confirms`. It contains no algorithm code.

**Step 3 - Read the pair status and phrase it**

1. Read the pair table: `status`, `pair_state`, `confirmed_ts`, then both states with their `since` dates; the detail line names the latest A reversal and its B match or says it is not yet confirmed.
2. `confirmed` with a `pair_state`: say both averages are in that state and give the later of the two reversal dates as the date the pair confirmed.
3. `non_confirmation`: say which average is in which state, since when, and that this is a divergence warning under `R-032` (【literature-consensus】), not a reversal of either average; the A trend stays what `dow-trend-classification` says it is. Example wording: Industrials BULL_PRIMARY since 2023-06-15, Transports BEAR_PRIMARY since 2026-09-24, non-confirmation in force; no bear market is declared for the pair until the Industrials also signal REVERSAL_DOWN and the match is found.
4. `pending`: one leg is still UNDEFINED; read each leg's `warmup_note` through `dow-trend-classification` and widen `--start`.
5. In the signals table, `confirmation` is `confirmed` or `pending` only on `REVERSAL_*` rows; `matched_ts` is the B date and `confirmed_ts` the later of the two. Everything else is `not_applicable`.

**Step 4 - Dow lines as implemented (`R-022`, 【literature-consensus】 on the definition)**

What a line is (`R-022`): a narrow sideways range in both averages, read as accumulation or distribution. Hamilton on the averages: a line is "a succession of closing prices, over a sufficient number of days for a fair volume of trading within a narrow range" (hamilton-1922-stock-market-barometer:Q24), and "a movement of the average price out of that line, downward or upward, will confidently indicate a change in the general market direction of at least a secondary and even a primary character, which we can depend upon where either average is confirmed by the other." (hamilton-1922-stock-market-barometer:Q24). Dow's own text applies the word to an individual stock's chart (the book method), the registry notes; Hamilton and Rhea apply it to the averages.

`detect_lines` (contract line.py section, Deviation 9, Amendment A6):

| Element | Implementation | Literature figure, by pointer | Label |
|---|---|---|---|
| band | `(max - min) / mean <= band_pct` on closes, both series, over the same window | Rhea about 5 percent for both averages (`R-023`; section 2.3 of the registry lists the echoes) | 【literature-consensus】 one lineage |
| band, older figures | not implemented as points | Dow 1901 for a stock: "stay within a narrow range of prices, say 2 points, until there has formed quite a long horizontal line of these figures." (nelson-1903-abc-of-stock-speculation:Q12); Hamilton's 1914 line ran 3 and 4 points in the two averages (hamilton note paraphrase, `R-023`) | 【literature-consensus】 as history; points are not percent |
| duration | at least `min_sessions` consecutive trading sessions | Rhea two to three weeks or longer (`R-024`) | 【literature-consensus】 one lineage |
| duration, project setting | `min_sessions` = 15 sessions, the literal reading of three trading weeks; the contract originally said 14 | none; the spec review (section 3a) chose 15 | 【agent-defined】 |
| both averages | both series must qualify over the same window (full temporal overlap, `_joint_end`) | "the price variation of both averages move within a range of approximately five per cent." (thedowtheory-lines-special-issue:Q2); `R-025` | 【literature-consensus】 |
| sideways filter | net drift `abs(close_end / close_start - 1) <= band_pct * max_drift_frac` in both series; a long in-band window that drifts is consumed and not reported | none; introduced after the spec review found that a steady 4.9 percent trend qualified as a line (D6) | 【agent-defined】 |
| breakout | first later close outside the window's own min and max in either series, earliest wins; emitted by `analysis.py` as `LINE_BREAKOUT_UP` or `LINE_BREAKOUT_DOWN` (not agent-defined) in `dow analyze` only; the wrapper's signals table has no such rows, read the lines table | a break upward implies accumulation and higher prices, a break downward distribution (registry paraphrase of `R-026`); Rhea via Blay: "Hamilton said that we could always depend upon the breaking of a line" (thedowtheory-lines-special-issue:Q5) | 【literature-consensus】 |
| dual confirmation | `confirmed_ts` = the later of the two series' same-direction breakout dates, or none; `confirmed_both` = `confirmed_ts` is known as of the evaluation bar; evaluated only with bars up to `as_of` | Hamilton Q25 above (`R-033`) | 【literature-consensus】 on the need, 【agent-defined】 on the mechanics |
| significance by length | not implemented; fixed `band_pct` and `min_sessions` | "Generally speaking, the longer the Line (in duration) and the narrower or more compact its price range, the greater the significance of its ultimate breakout." (edwards-magee-technical-analysis-dow-chapters:Q7); `R-063` | 【literature-consensus】 |

Honest note on the count: the spec review (`../../../reports/spec_review_p3.md` section 3a and D6) measured that a joint 5 percent band is the normal state of the market rather than a consolidation (41 percent of all 15-session windows since 2015 qualify, 【agent-defined】 measurement), that the pre-amendment detector reported 108 lines between 2015-01-01 and 2026-11-06 of which 57 started on the previous line's breakout bar, and judged those windows to be trend segments rather than lines. With the drift filter and 15 sessions the same period gives 41 lines (about 3.5 per year, 【agent-defined】 figure) and the full history from 1992 gives 103. The filter and the session count are the project's parameters, not Rhea's; different values give different lines, and the spec review's table of alternatives is the place to look before changing them.

Not implemented, so never claim them from this output: a 3 percent penetration filter on the break (`R-028`, 【single-source】, Taiwan educator); a volume requirement on the break (`R-029`, 【single-source】); a measured move of about another 5 percent after a 5 percent line (`R-030`, 【single-source】, Blay); a line as a substitute for a secondary reaction (`R-064`, 【literature-consensus】 but not coded); Hamilton's observation that lines usually form after, not before, the secondary break (`R-031`, 【single-source】). Dissent: Blay reports that lines are an element of classical Dow Theory "which has been discarded by Schannep." (thedowtheory-lines-special-issue:Q14), the `R-022` disagreeing column.

**Step 5 - Read the lines table**

Columns: `start`, `end` (first and last session of the window), `sessions`, `band_a`, `band_b` (realised `(max - min) / mean` of each series), `breakout` (`up`, `down`, `none`), `breakout_ts` (first close outside the window in either series), `confirmed_both`, `confirmed_ts`.

- `breakout: none` means the window runs to the last bar: the market is in a line as of `--end`; say so and give both band widths.
- `confirmed_both: false` with a `breakout_ts` means one average has left the range and the other has not yet broken the same way (or broke the other way, which can never confirm): report the breakout as pending under `R-033` (【literature-consensus】 that confirmation may lag) and do not call it a signal for the pair.
- `confirmed_both: true`: give both dates; the pair-level breakout is dated `confirmed_ts`, which is the event date used by the R6 backtest.
- Windows never overlap and the next window may start on the bar after a breakout; a long run of back-to-back windows is the chaining the spec review warned about, and the drift filter removes most but not all of it.
- Line ranges are also shaded on the chart by `dow-levels-and-chart` (ranges shorter than 28 calendar days are not shaded there, contract Deviation 12, 【agent-defined】 presentation rule).

**Step 6 - The volume flag (`R-037`, 【literature-consensus】; `R-038`, 【literature-disputed】)**

What the sources say: "the volume of trading is always larger in a bull market than in a bear market. It expands as prices go up and contracts as they decline." (hamilton-1922-stock-market-barometer:Q19), and volume is subordinate to price: "the averages have already taken those things into account" (hamilton-1922-stock-market-barometer:Q5), `R-041` (【literature-consensus】 that volume adds only collateral evidence and signals come from price). Dow asked the trader only to keep a volume record alongside prices (`R-037` agreeing column, nelson Q4, no rule).

`volume_confirms(df, swings)` (contract Deviation 11, 【agent-defined】 mechanics around `R-037`): take the last four confirmed secondary swings of the first average (at most three legs); legs moving with the net move between the first and last of those swings are trend legs, the rest counter legs; return whether the mean daily volume on trend legs exceeds the mean on counter legs; `None` when volume is all zero, when fewer than three confirmed secondary swings exist (fewer than two legs, as on a short CSV or an early `--end`), or when either group is empty. It is informational: nothing in the state machine, the pair status or the lines depends on it.

The disputed point, side by side and not adjudicated (`R-038`, 【literature-disputed】):

| Position | Statement | Source |
|---|---|---|
| P1 reactions can be heavy | "A sharp reaction in a bull market will often stimulate the volume of business." (hamilton-1922-stock-market-barometer:Q20) | Hamilton, primary |
| P2 reactions are light | "Volume typically expands with the primary direction and dries up against it." (cmt-open-exam-prep-dow-theory:Q9); the Taiwan educator ctyeh describes a pullback as one on shrinking volume (zh-ctyeh-dow-theory:Q17, Q18, paraphrased) | educators |

`volume_confirms` adopts P2 by construction (a counter leg is expected to be lighter), so a `false` flag during a sharp reaction is exactly what Hamilton's P1 predicts; do not read it as a failed trend. Index volume is a vendor-constructed aggregate with level breaks (`../../../analysis/protocol_deviations.md`, volume caveat correction), which is why the R7 backtest starts in 2000 and uses ETF volume for the robustness pair.

**Step 7 - What the data says (labels owned by `dow-rule-backtest`)**

| Row | Rule tested | Data label | Figures from `../../../analysis/rule_status_table.md` and `../../../reports/rule_R3.md`, `rule_R6.md`, `rule_R7.md` |
|---|---|---|---|
| R3 two_average_confirmation | `R-032` to `R-034` | 【insufficient-evidence】 | n = 15 events from 12 ^DJI reversals since 1992 (3 reversals confirmed later than the outcome window sit in both groups, DEV-11), below the floor of 30 events; difference of mean excess log return at 60 sessions between confirmed and single reversals -0.0544, CI -0.1385 to 0.0308; refutation bound 0.0457 against null 0; every row is EXPLORATORY because the single group is classified with information up to the end of the outcome window (R11 F4, `../../../analysis/protocol_deviations.md` DEV-11 recommends redefining it for v3) |
| R6 line_breakout | `R-022` to `R-027` | 【insufficient-evidence】 | n = 87 confirmed breakouts since 1992; share of breakouts followed by a same-direction move over 20 sessions 0.4138, Wilson CI 0.3161 to 0.5188, against null 0.5; refutation upper bound 0.5471 does not lie below 0.5, so the data do not refute the rule either; sub-samples agree in sign (0.4250 before 2010, 0.4043 after); pair-inconsistent |
| R7 volume_confirmation | `R-037`, `R-038`, `R-041` | 【insufficient-evidence】 | n = 57 consecutive secondary leg pairs in a PRIMARY state, 2000-01-03 onward; share where the trend leg has the higher mean volume 0.3509, CI 0.2400 to 0.4806, against null 0.5; refutation bound 0.5162; the `volume_confirms` flag itself is true in 0.4058 of 69 evaluations |

Read R3 as: too few reversals to say whether confirmed reversals behave differently from unconfirmed ones, and the grouping itself is exploratory. Read R6 as: at the project's line parameters, confirmed breakouts were followed by a same-direction move less than half the time over 20 sessions in the R6 backtest, 【insufficient-evidence】, but the interval reaches 0.52 and the refutation bound sits above 0.5, so neither confirmation nor refutation; the 60-session and 120-session rows are near 0.5. Read R7 as: the flag's premise was true in about a third of leg pairs, 【insufficient-evidence】 by the pre-registered rule; the sweep over 15 specifications stays between 0.29 and 0.47. None of the three rows is 【data-refuted】; all are 【insufficient-evidence】.

**Step 8 - Interpret and hand off**

1. Give the pair status with both states and `since` dates, then the latest A reversal and its B match (or that it is pending).
2. State the current line, if any (`breakout: none`), or the last breakout with its `confirmed_both` and both dates.
3. Report `volume_confirms` with the word informational and the `R-038` dispute.
4. Attach the data labels of Step 7 whenever the output is used to support a rule.
5. Hand off: one-average trend and the defense line to `dow-trend-classification`; swing dates to `dow-swing-detection`; levels and the chart to `dow-levels-and-chart`; anything beyond the three rows above to `dow-rule-backtest`.

## Output

The script prints a one-row pair table followed by the detail line, a signals table for the first average, a lines table, the volume line, a summary line and, with `--json`, one JSON document.

Pair table columns: `status`, `pair_state`, `confirmed_ts`, `A_state`, `A_since`, `B_state`, `B_since`.

Signals table columns: `ts` (knowable bar), `kind`, `price`, `level`, `confirmation` (`confirmed`, `pending`, `not_applicable`), `matched_ts`, `confirmed_ts`. The table holds only the first average's `run_trend` signals; no `LINE_BREAKOUT_*` rows appear here (only `dow analyze` emits them), so breakouts are read from the lines table.

Lines table columns: `start`, `end`, `sessions`, `band_a`, `band_b`, `breakout`, `breakout_ts`, `confirmed_both`, `confirmed_ts`.

Summary line: symbols, bar count and date range, line count, `band_pct`, `min_sessions`, `max_drift_frac`, `confirmation.max_days`.

JSON: `{"symbol", "pair", "bars", "start", "end", "band_pct", "min_sessions", "max_drift_frac", "max_days", "pair_confirm": {"status", "pair_state", "detail", "confirmed_ts"}, "trend_a": {"primary", "since"}, "trend_b": {"primary", "since"}, "signals": [{"ts", "kind", "price", "level", "confirmation", "matched_ts", "confirmed_ts"}], "reversals_b": [same keys], "lines": [{"start", "end", "sessions", "band_pct_a", "band_pct_b", "breakout", "breakout_ts", "confirmed_both", "confirmed_ts"}], "volume_confirms": true | false | null}`. `pair_confirm` mirrors `trend_state.confirmation` of `dow analyze` plus `confirmed_ts`; `lines` mirrors its `lines` section plus `sessions`; `signals[].confirmation` mirrors the per-signal field of `dow analyze`.

When answering in prose, give the status and both states with dates, the latest reversal match, the current or last line with its confirmation, the volume flag with its label, and the Step 7 data labels; hand the rest to the siblings.

## Examples

### Example 1: CSV fixture used as both legs

Command, run from this skill directory:

```bash
python3 scripts/confirm.py --source csv --csv ../../../tests/fixtures/dji_sample.csv
```

Real output (signals table omitted):

```text
| status | pair_state | confirmed_ts | A_state | A_since | B_state | B_since |
|---|---|---|---|---|---|---|
| confirmed | BEAR_PRIMARY | - | BEAR_PRIMARY | 2020-12-07 | BEAR_PRIMARY | 2020-12-07 |
Both averages are BEAR_PRIMARY

| start | end | sessions | band_a | band_b | breakout | breakout_ts | confirmed_both | confirmed_ts |
|---|---|---|---|---|---|---|---|---|
| 2020-01-02 | 2020-02-12 | 30 | 0.044 | 0.044 | up | 2020-02-13 | true | 2020-02-13 |
| 2020-06-16 | 2020-07-07 | 16 | 0.046 | 0.046 | down | 2020-07-08 | true | 2020-07-08 |
| 2020-07-20 | 2020-09-15 | 42 | 0.046 | 0.046 | up | 2020-09-16 | true | 2020-09-16 |
| 2020-10-14 | 2020-11-13 | 23 | 0.043 | 0.043 | up | 2020-11-16 | true | 2020-11-16 |
| 2021-01-19 | 2021-02-24 | 27 | 0.045 | 0.045 | none | - | false | - |
volume_confirms: true (trend-leg mean volume > counter-leg mean) (informational; literature-disputed R-038)
DJI_SAMPLE vs DJI_SAMPLE | bars 300 2020-01-02 -> 2021-02-24 | 5 lines | band_pct 0.05 min_sessions 15 max_drift_frac 0.5 | confirmation.max_days None
```

Reading: with one file as both legs the states are identical, so the status is `confirmed` and every breakout confirms itself on the same day; `confirmed_ts` in the pair row is empty because this leg has no `REVERSAL_*` signal (the bear was established, not reversed into). The last window has no breakout: the sample ends inside a line. The fixture is a synthetic 300-bar sample from `../../../tests/fixtures/make_dji_sample.py`, so its dates and prices are not the real index.

### Example 2: ^DJI with ^DJT from ClickHouse since 2015

```bash
python3 scripts/confirm.py --symbol ^DJI --pair ^DJT --start 2015-01-01
```

Real output on 2026-11-08 (data through 2026-11-06), abbreviated to the pair table, the four reversal rows and the summary:

```text
| status | pair_state | confirmed_ts | A_state | A_since | B_state | B_since |
|---|---|---|---|---|---|---|
| non_confirmation | - | 2023-06-15 | BULL_PRIMARY | 2023-06-15 | BEAR_PRIMARY | 2026-09-24 |
A=BULL_PRIMARY and B=BEAR_PRIMARY point in opposite directions; latest A REVERSAL_UP on 2023-06-15 matched by B on 2023-02-01 (confirmed 2023-06-15)

| 2020-04-03 | REVERSAL_DOWN | 21052.53 | 21792.20 | confirmed | 2020-04-03 | 2020-04-03 |
| 2020-08-05 | REVERSAL_UP | 27201.52 | 23185.62 | confirmed | 2020-04-17 | 2020-08-05 |
| 2022-05-09 | REVERSAL_DOWN | 32245.70 | 32632.64 | confirmed | 2022-04-08 | 2022-05-09 |
| 2023-06-15 | REVERSAL_UP | 34408.06 | 34152.01 | confirmed | 2023-02-01 | 2023-06-15 |

volume_confirms: false (informational; literature-disputed R-038)
^DJI vs ^DJT | bars 2980 2015-01-02 -> 2026-11-06 | 41 lines | band_pct 0.05 min_sessions 15 max_drift_frac 0.5 | confirmation.max_days None
```

Reading: a non-confirmation is in force. The Industrials are BULL_PRIMARY since 2023-06-15 while the Transports signalled REVERSAL_DOWN on 2026-09-24 and are BEAR_PRIMARY; under `R-032` (【literature-consensus】) that is a divergence warning, and no bear market is declared for the pair until the Industrials also reverse and the match is found. Every Industrials reversal since 2015 was confirmed: the 2022-05-09 REVERSAL_DOWN had been led by the Transports on 2022-04-08, so the pair confirmation is dated 2022-05-09 (the later date); the 2020-08-05 REVERSAL_UP was led by the Transports on 2020-04-17; the 2020-04-03 REVERSAL_DOWN was matched the same day. The full history (`--json` without `--start`, 8775 bars from 1992-01-02) shows how far the no-window rule reaches: the 2003-06-04 REVERSAL_UP is matched by the Transports only on 2004-04-06 and the 2016-04-14 REVERSAL_UP on 2016-10-05, and all twelve Industrials reversals since 1992 are eventually confirmed; 103 lines, 88 of them confirmed by both. The 41 lines in this window are the count the spec review predicted for the drift-filtered detector. `volume_confirms` is `false`: with the last four confirmed secondary swings of ^DJI the counter legs carried the heavier volume, which Hamilton's P1 allows and the educators' P2 does not (`R-038`, 【literature-disputed】).

### Example 3: line breakouts with dates (same run as Example 2)

```text
| start | end | sessions | band_a | band_b | breakout | breakout_ts | confirmed_both | confirmed_ts |
|---|---|---|---|---|---|---|---|---|
| 2015-10-28 | 2015-12-02 | 25 | 0.038 | 0.036 | down | 2015-12-03 | true | 2015-12-18 |
| 2017-03-14 | 2017-05-16 | 45 | 0.029 | 0.045 | down | 2017-05-17 | false | - |
| 2026-09-16 | 2026-10-26 | 29 | 0.038 | 0.046 | up | 2026-10-27 | true | 2026-11-04 |
```

Reading: the 2015 line held both averages inside their bands for twenty-five sessions; the Industrials closed below their range on 2015-12-03 and the Transports followed on 2015-12-18, so the pair breakout is dated 2015-12-18 and would have read `pending` on any run cut between those dates. The 45-session 2017 line broke down in one average on 2017-05-17 and was never confirmed: the other average left its range upward instead, so the row stays `false` forever. The latest line, 2026-09-16 to 2026-10-26, broke upward on 2026-10-27 and was confirmed on 2026-11-04, two sessions before the data end. Of the 41 lines, 6 are unconfirmed and none is still open. Whether such breakouts were followed by same-direction moves is the R6 question, 【insufficient-evidence】 (Step 7).

### Example 4: the skill's two-leg fixture, non-confirmation and truncation

```bash
python3 scripts/confirm.py --source csv --csv tests/fixtures/pair_a_sample.csv --csv-pair tests/fixtures/pair_b_sample.csv
```

Real output, pair row and lines table:

```text
| non_confirmation | - | - | BULL_PRIMARY | 2021-05-14 | BEAR_PRIMARY | 2021-07-21 |
A=BULL_PRIMARY and B=BEAR_PRIMARY point in opposite directions

| 2021-03-11 | 2021-04-07 | 20 | 0.005 | 0.005 | up | 2021-04-08 | true | 2021-04-13 |
```

Reading: the two synthetic legs (generator `tests/fixtures/make_pair_sample.py`, documented in its docstring) share a flat shelf, then leg A jumps out of it on 2021-04-08 and leg B three sessions later; run with `--end 2021-04-12` the same line shows `breakout up 2021-04-08` with `confirmed_both false`, and from `--end 2021-04-13` it shows `true` with `confirmed_ts 2021-04-13`. Leg B later falls through its reaction low, makes a lower high and reverses (REVERSAL_DOWN on 2021-07-21) while leg A keeps making higher highs, so the final status is `non_confirmation` with no `pair_state`; A has no reversal, so the pair row's `confirmed_ts` is empty and `reversals_b` carries the unmatched B signal.

## Boundaries

| Not covered here | Sibling skill |
|---|---|
| Glossary, Chinese term mapping, label definitions, what each source says, provenance, performance studies | `dow-theory-sources` |
| Swing detectors, `minor_pct` / `secondary_pct` / `secondary_min_sessions`, `confirmed_idx`, multi-scale nesting, secondary flags (`R-013`, `R-046`) | `dow-swing-detection` |
| State machine, HH/HL/LH/LL, `DEFENSE_BREAK`, `REVERSAL_UP/DOWN` on one average, strict versus non-strict, the Dow defense line (`R-016` to `R-020`, `R-045`) | `dow-trend-classification` |
| Support and resistance clustering, trendline fitting, chart rendering of lines and pair closes (`R-047`, `R-049` to `R-055`) | `dow-levels-and-chart` |
| Decision table, backtest runs, the data labels beyond the three rows quoted in Step 7, the SP_IYT robustness results | `dow-rule-backtest` |

Pair confirmation, `confirm_signal` matching, line detection, `LINE_BREAKOUT_*` and the volume flag are defined only here; siblings reference them. When a sibling is not installed, read `../../../docs/specs/algorithm_contract.md` (line.py, confirmation.py, Deviations 9 to 13, A6, A7) and `../../../research/canonical_rules.md` sections 1.4 and 1.5.

## Limitations

1. **Transports history starts in 1992.** ClickHouse holds `^DJT` from 1992-01-02, so no pair status, match or line exists for earlier regimes, and every count here (twelve Industrials reversals, 103 lines) is a 1992-onward figure, 【agent-defined】.
2. **Lines are agent-parameterised.** Rhea gives about 5 percent and two to three weeks or longer (`R-023`, `R-024`, 【literature-consensus】 one lineage) and nothing else; the session floor, the drift filter and the min-max breakout rule are the project's (【agent-defined】), and the spec review showed the undiluted literature reading produces trend segments. Treat every line count as parameter-dependent.
3. **Breakout is any close outside the range.** No penetration filter (`R-028`, 【single-source】) and no volume test (`R-029`, 【single-source】) are applied; a one-session poke counts.
4. **No time window on confirmation.** With `max_days: null` a match can arrive many months later (Example 2); the status is correct as of each date, but a very late confirmation says little about the original signal. The literature gives no maximum lag (`R-033`, 【literature-consensus】), so none is imposed.
5. **State-level non-confirmation is coarse.** `non_confirmation` is also raised when the two averages are on the same side but one is SUSPECT; read both states before saying the averages diverge in direction.
6. **Volume on indices.** Index volume is a vendor aggregate with level breaks; the flag uses only the first average's volume and the last four secondary swings, and returns `None` with fewer than three confirmed secondary swings; it is informational, adopts the disputed P2 reading (`R-038`, 【literature-disputed】), and the R7 backtest is 【insufficient-evidence】.
7. **Evidence is thin.** R3, R6 and R7 are all 【insufficient-evidence】; R3's grouping is exploratory (DEV-11). Nothing here is 【data-confirmed】.
8. **Lag by construction.** Each leg's reversals are dated at their confirmation bars (`dow-trend-classification` Limitation 7), and the pair date is the later of two such dates.
9. **Not advice.** The skill reports whether two averages agree and whether a range has been left. It makes no price prediction and gives no investment advice.

## Resources

- `scripts/confirm.py`: the CLI wrapper (imports `load_klines`, `detect_multiscale`, `swings_as_of`, `run_trend`, `detect_lines`, `pair_confirm`, `confirm_signal`, `volume_confirms`; no algorithm code). `scripts/_table.py`: row, table and JSON formatting only. `scripts/_anchor.py`: project root and `.venv` resolution shared by skill scripts.
- `tests/test_cli.py`: runs the wrapper on the project CSV fixture as both legs (exit code, status within the allowed set, lines present with `sessions` at or above `min_sessions`, JSON keys) and on the skill's own `tests/fixtures/pair_a_sample.csv` and `pair_b_sample.csv` (generated by `tests/fixtures/make_pair_sample.py`: shared shelf, staggered breakouts, leg B reverses): asserts the non-confirmation, the single line with `breakout_ts` 2021-04-08 and `confirmed_ts` 2021-04-13, the truncation check (`confirmed_both` is false at `--end` 2021-04-09 and 2021-04-12 and true from 2021-04-13), the prefix equality of a truncated run, the `pending` status while both legs are UNDEFINED, the same-side PRIMARY-versus-SUSPECT `non_confirmation` at `--end` 2021-06-21, `volume_confirms` null on a short window, the clean error on an empty inner join, and that the CSVs match their generator (`make_pair_sample.py --check`; without the flag the generator rewrites both files in place); a ClickHouse-gated test (skipped when the container does not answer) checks the ^DJI/^DJT run since 2015 for the 2022-05-09 REVERSAL_DOWN matched by 2022-04-08, the current non-confirmation and the 41 lines. Run from the project root: `uv run --python .venv/bin/python pytest .claude/skills/dow-confirmation-and-line -q`.
- `references/evidence.md`: every verbatim quote and rule id used here, grouped by Workflow step, with `slug:Qn` and URL.
- `../../../src/dowtheory/confirmation.py`: `pair_confirm`, `confirm_signal`, `volume_confirms`. `../../../src/dowtheory/line.py`: `detect_lines`, `LineRange`. `../../../src/dowtheory/analysis.py`: how `analyze` assembles lines, per-signal confirmation and the volume flag.
- `../../../docs/specs/algorithm_contract.md` (line.py, confirmation.py, Deviations 9 to 13, Amendments A6, A7) and `../../../docs/specs/skill_contract.md`.
- `../../../configs/dow.yaml` `line:` and `confirmation:` sections; `../../../configs/pairs.yaml`.
- `../../../reports/spec_review_p3.md`: rule-mapping row 8, section 3a (line counts and the drift recommendation), defects D1, D2 and D6. `../../../analysis/rule_status_table.md` and `../../../reports/rule_R3.md`, `rule_R6.md`, `rule_R7.md`; `../../../analysis/protocol_deviations.md` DEV-11 and the volume caveat correction.
- `../../../tests/unit/test_line.py` and `../../../tests/unit/test_confirmation.py`: library tests of the drift filter, session counting, as-of truncation, cycle-aware matching and the volume flag.
