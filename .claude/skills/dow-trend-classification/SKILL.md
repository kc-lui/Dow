---
name: dow-trend-classification
description: >-
  Dow project trend layer: classifies the primary trend as a replayed state machine (UNDEFINED,
  BULL_PRIMARY, BEAR_PRIMARY, BULL_SUSPECT, BEAR_SUSPECT) driven by confirmed secondary swings,
  emits HH/HL/LH/LL (with an EQUAL tolerance), TREND_ESTABLISHED, DEFENSE_BREAK and
  REVERSAL_UP/REVERSAL_DOWN signals, and owns the agent-defined Dow defense line (last confirmed
  reaction low or high). Use when asked what the primary trend is and
  how the secondary and minor scales feed it, whether the market makes higher highs or lower lows, whether a reversal has been
  signalled or only suspect, where the defense line sits, strict versus non-strict reversal,
  or 主要趨勢 / 次要趨勢 / 小型趨勢 / 道氏防線 / 反轉. Not covered: source statements and label definitions → dow-theory-sources;
  swing detection and thresholds → dow-swing-detection; lines and two-average confirmation →
  dow-confirmation-and-line; support, resistance, trendlines, charts → dow-levels-and-chart;
  backtest results and data labels → dow-rule-backtest.
---

# dow-trend-classification: Primary trend state, HH/HL signals and the Dow defense line

> This skill is the trend layer of the Dow project. Its knowledge comes from the code in `../../../src/dowtheory/trend.py` and the driver `../../../src/dowtheory/analysis.py`, the frozen contract `../../../docs/specs/algorithm_contract.md` (TrendStateMachine section, Deviations 5 to 7, 14 and 16 to 17, Amendments A2 to A5), the configuration `../../../configs/dow.yaml` (`trend:`), and the synthesis `../../../research/canonical_rules.md` built from the 42 source notes under `../../../research/sources/` (registry header: 43; see `dow-theory-sources`). Glossary, Chinese term mapping and label vocabulary are owned by `dow-theory-sources`; swing definitions, thresholds and `confirmed_idx` are owned by `dow-swing-detection`; both are referenced, never restated. Every quantitative statement carries exactly one literature label from 【literature-consensus】【literature-disputed】【single-source】【agent-defined】 and, where a backtest exists, one data label from 【data-confirmed】【data-refuted】【insufficient-evidence】. Double quotes are reserved for verbatim source text with a `(slug:Qn)` pointer; everything else is paraphrase. The Dow defense line is this project's construct, labelled 【agent-defined】 everywhere (`R-045`); no source defines or names it. The skill describes trend state as of a date. It never predicts prices and it is not investment advice.

## When to Use

- Say which primary trend an index or ETF is in as of a date, since when, and whether it is PRIMARY or SUSPECT.
- List the HH/HL/LH/LL, TREND_ESTABLISHED, DEFENSE_BREAK and REVERSAL signals over a window, with the bar on which each became knowable.
- Report the Dow defense line (price, date, kind) and explain what moves it.
- Explain why a reversal has or has not been declared, and what strict versus non-strict mode would say.
- Explain how the three trends are operationalised here (primary as a state, secondary and minor as swing scales).
- Feed a dated trend state to a sibling (pair confirmation, levels, backtest) without lookahead.

Do not use it to detect swings, quote what the sources say, detect lines, confirm with the second average, cluster levels, or report backtest numbers beyond the two rows cited in Step 7. Those are sibling skills (see Boundaries).

## Prerequisites

1. **Project checkout and environment.** The scripts import `dowtheory` from `../../../src/`. `scripts/_anchor.py` finds the repo through `DOW_PROJECT_ROOT`, or by walking up to a directory holding `pyproject.toml` and `src/dowtheory`, and re-executes the script under `<root>/.venv/bin/python`, so any `python3` works as the launcher. Global-install setup, one line:

   ```bash
   export DOW_PROJECT_ROOT=<path-to-Dow-repo>
   ```

2. **Data access.** Same two sources as `dow-swing-detection` Prerequisites 2 to 4 (`--source clickhouse`, the default, reading `dow.mkt_klines` with `FINAL` inside the Docker container `trading_clickhouse`; or `--source csv --csv PATH`, for example `../../../tests/fixtures/dji_sample.csv`). For CSV the symbol defaults to the upper-cased file stem. Run the integrity gate `.venv/bin/python scripts/check_integrity.py` from the project root before any ClickHouse-based analysis; the CSV fixture needs no gate.
3. **Swing layer.** The machine consumes only confirmed secondary swings (`detect_multiscale`, `swings_as_of`) as defined in `dow-swing-detection` Steps 2 to 4; the 3 percent minor scale never feeds it (`R-015`, 【literature-consensus】 that daily movement is low information). Parameters `minor_pct`, `secondary_pct`, `secondary_min_sessions` are explained there and only named here.
4. **Configuration.** `trend.require_lower_high_for_reversal` (default `true`, strict) and `trend.equal_extreme_tol` (default `0.005`) in `../../../configs/dow.yaml`; `--strict` / `--no-strict` overrides the first for one run.
5. **Siblings for definitions.** Term meanings and label semantics: `dow-theory-sources` Step 1 and Step 2. Rule ids `R-0xx` refer to `../../../research/canonical_rules.md`.

## Workflow

**Step 1 - The three trends as applied here (`R-001`, 【literature-consensus】 on the count)**

| Trend | Operational meaning in this project | Produced by | Duration figures |
|---|---|---|---|
| Primary | A state, not a swing: the output of the TrendStateMachine (BULL_PRIMARY, BEAR_PRIMARY, or the two SUSPECT states), with `since` the bar on which the direction was established or flipped | this skill, `run_trend` | disputed between Dow, Hamilton, Rhea and educators (`R-002` to `R-004`, 【literature-disputed】); positions side by side in `dow-theory-sources` Step 3; the project applies no duration test |
| Secondary | The `secondary` swing scale as defined in `dow-swing-detection` Step 4, thresholds `R-046` 【agent-defined】 | `dow-swing-detection` Step 4 | disputed (`R-006`, `R-007`, 【literature-disputed】); recorded as `duration_days` and flags only, see the sibling |
| Minor | The `minor` swing scale; used for levels and the chart, never for trend state | `dow-swing-detection` | none applied |

Dow's own trend-by-extremes rule (`R-016`, 【literature-consensus】): "It is a bull period as long as the average of one high point exceeds that of previous high points. It is a bear period when the low point becomes lower than the previous low points." (nelson-1903-abc-of-stock-speculation:Q8). Dow states highs for bulls and lows for bears; Rhea and the educators require both, and the machine follows the Rhea reading (HH and HL to establish a bull, LH and LL for a bear). A trend persists until a reversal is signalled (`R-017`, 【literature-consensus】): "The primary trend, once in place, is assumed to continue in place until definitely proven otherwise." (schannep-dow-theory-21st-century:Q7).

**Step 2 - Run**

```bash
# from this skill directory; any python3 re-executes under the project .venv
python3 scripts/trend.py --symbol ^DJI --start 2015-01-01
python3 scripts/trend.py --symbol ^DJI --start 2015-01-01 --no-strict --json
python3 scripts/trend.py --source csv --csv ../../../tests/fixtures/dji_sample.csv --end 2020-12-31
```

The wrapper loads bars, runs `detect_multiscale`, keeps the secondary swings confirmed at or before the last bar (`swings_as_of`) and replays `run_trend` bar by bar, exactly as `analysis.analyze` does. It contains no algorithm code.

**Step 3 - Read the state machine**

States, 【agent-defined】 naming under `R-016` and `R-018` (the SUSPECT states operationalise `R-020`):

| State | Meaning | Defense line kind |
|---|---|---|
| `UNDEFINED` | fewer than two confirmed highs and two confirmed lows, or the pattern is neither HH+HL nor LH+LL | none |
| `BULL_PRIMARY` | established or resumed bull: the latest trend-side swing was a new high | `reaction_low` |
| `BEAR_PRIMARY` | mirror | `reaction_high` |
| `BULL_SUSPECT` | bull with a counter swing (LH, or an EQUAL high) or with a defense break but no counter swing yet; waits for a new HH (back to PRIMARY) or a close below the defense line after a counter swing (REVERSAL_DOWN) | `reaction_low` (kept) |
| `BEAR_SUSPECT` | mirror | `reaction_high` (kept) |

Transitions, evaluated when a secondary swing becomes confirmed (on its `confirmed_idx` bar), then on every close (contract, Deviations 6 and 16, Amendments A2 and A3; all 【agent-defined】 mechanics around the sourced `R-016` / `R-018` rules):

| From | Event | To | Signal(s) |
|---|---|---|---|
| UNDEFINED | last two highs are HH and last two lows are HL (either order) | BULL_PRIMARY, `since` = this bar, defense = last L | `TREND_ESTABLISHED` (A4) |
| UNDEFINED | LH and LL | BEAR_PRIMARY, defense = last H | `TREND_ESTABLISHED` |
| BULL_PRIMARY | new H above last H | BULL_PRIMARY, defense refreshed to last L | `HH` |
| BULL_PRIMARY | new L above last L | BULL_PRIMARY, defense = this L | `HL` |
| BULL_PRIMARY | new H below last H, or EQUAL high (double top) | BULL_SUSPECT, counter swing set | `LH` (none for EQUAL) |
| BULL_PRIMARY | close below the defense line, no counter swing | strict: BULL_SUSPECT; non-strict: BEAR_PRIMARY, `since` = this bar, defense = last H | `DEFENSE_BREAK` (agent_defined true) |
| BULL_SUSPECT | new H above last H | BULL_PRIMARY, defense refreshed to the latest L (A3, Deviation 16) | `HH` |
| BULL_SUSPECT | LH or EQUAL high | BULL_SUSPECT, counter swing set | `LH` or none |
| BULL_SUSPECT | new L above last L | BULL_SUSPECT, defense = this L | `HL` |
| BULL_SUSPECT | new L below last L | BULL_SUSPECT, bookkeeping only | `LL` |
| BULL_SUSPECT with counter swing | close below the defense line | BEAR_PRIMARY, `since` = this bar, defense = last H (`reaction_high`) | `REVERSAL_DOWN` |
| bear side | mirror of every row (LL resumes, HL is the counter swing, EQUAL low is a double bottom, close above the line breaks it) | mirror | `LL`, `HL`, `LH`, `HH`, `DEFENSE_BREAK`, `REVERSAL_UP` |

Signal kinds and fields: `ts` is the bar on which the signal became knowable (for HH/HL/LH/LL that is the swing's confirmation bar, not the extreme, Deviation 5); `price` is the swing price (or the close for close-driven signals); `level` is the previous same-kind swing price (or the defense line); `agent_defined` is true only for `DEFENSE_BREAK`. `TREND_ESTABLISHED` carries the state name and the HH+HL or LH+LL pair in its note. `LINE_BREAKOUT_UP/DOWN` exist in the contract but are produced by the line module, not by this machine (sibling `dow-confirmation-and-line`).

EQUAL swings (`equal_extreme_tol`, A2, Deviation 14, 【agent-defined】): a new swing within the tolerance fraction of the previous same-kind swing is EQUAL, emits no HH/HL/LH/LL and changes nothing, except when it is the trend-side extreme (a double top in a bull, a double bottom in a bear), where it counts as the counter swing. The tolerance exists because, without it, the 2016-02-11 ^DJI low sat a hair below the 2015-08-25 low and read as LL, which deadlocked the strict machine; Example 3 shows the restored case.

**Step 4 - Read the Dow defense line (`R-045`, 【agent-defined】)**

Definition: the Dow defense line is the price of the last confirmed secondary reaction low while the state is on the bull side (kind `reaction_low`), or the last confirmed secondary reaction high on the bear side (kind `reaction_high`). It is set when a trend is established or flipped (to the latest opposite-side swing), refreshed on each new HL in a bull (LH in a bear), and refreshed again to the latest confirmed reaction extreme whenever a SUSPECT state returns to PRIMARY on a new HH or LL (A3), so it cannot go stale across a SUSPECT episode. A close through it is a `DEFENSE_BREAK` when no counter swing has formed, or a `REVERSAL_*` when one has. It is always emitted as `defense_line: {price, ts, type, agent_defined: true}`.

Provenance sentence to repeat whenever the line is mentioned: no source defines or names the Dow defense line; the project's search found "no page defines 道氏防線 or uses 防線 as a Dow Theory term in any page read" (zh-defense-line-search-log:Q1), and the first-hand notes (hamilton, nelson, rhea, dow-editorials, edwards-magee, kirkpatrick-dahlquist, russell-history) mark it not mentioned; the negative result is detailed in `dow-theory-sources` Step 6. Nearest analogues, none a drawn line:

| Analogue | Statement | Rule | Label |
|---|---|---|---|
| Blay (thedowtheory.com) | "The lows of secondary reactions serve as our exit point (stop-loss) when broken down" (thedowtheory-rhea-three-weeks:Q6), "(always with confirmation)" (thedowtheory-rhea-three-weeks:Q7) | `R-048` | 【single-source】; same geometry as the bull-side line, but Blay requires the second average, which this machine does not test |
| Taiwan educator ctyeh | a prior pullback low used as support (zh-ctyeh-dow-theory:Q21, Chinese, paraphrased) | `R-045` analogue row | 【agent-defined】 mapping; the source gives no rule |
| Schaefer and Russell | the halfway level of the primary swing, not the secondary low (Step 5) | `R-065` | 【single-source】 |

**Step 5 - Strict versus non-strict reversal and the literature (`R-018`, 【literature-disputed】)**

| Mode | `require_lower_high_for_reversal` | A close through the defense line without a counter swing | Mapping to the literature |
|---|---|---|---|
| strict (default) | `true` | `DEFENSE_BREAK`, state SUSPECT; the reversal is declared only after a counter swing (LH in a bull, HL in a bear, or an EQUAL trend-side extreme) and a close through the line | orthodox position P1 of `R-018`, 【literature-disputed】: a failed rally high and a decline through the prior low, Hamilton, Rhea, Edwards and Magee, StockCharts; Hamilton: "the change in the broad general direction of the market is abrupt, while the resumption of the major movement is appreciably slower" (hamilton-1922-stock-market-barometer:Q23), `R-019` 【single-source】 |
| non-strict | `false` | `DEFENSE_BREAK` and an immediate flip to the opposite PRIMARY; no `REVERSAL_*` is emitted for that flip | the break-of-secondary-low reading that Russell attributes to orthodox theorists: "When the Averages broke through their preceding secondary lows, many orthodox Dow Theorists, who relied almost totally (as most do today) on the pattern of the Averages, proclaimed that a bear market had started." (russell-history-of-the-dow-theory:Q7) |

The dissent, presented and not adjudicated: Schaefer and Russell reject that a break of the preceding secondary lows alone proves a bear market (`R-018` position P2, 【literature-disputed】); Schaefer told subscribers "to remain invested in harmony with the primary trend of the market" (russell-history-of-the-dow-theory:Q6) and tested instead whether the decline held above the halfway level of the primary swing and whether a third speculative phase had occurred (`R-065`, 【single-source】). Neither mode implements the 50 percent principle (`R-065`, 【single-source】); both modes ignore the second average, which every orthodox source requires and which `dow-confirmation-and-line` adds. Neither mode is canonical: the strict machine is this project's reading of P1 with an agent-defined line as the break level.

**Step 6 - Warm-up, start-date dependence and the replay guarantee**

- `warmup_note` (A4, Deviation 17) states the data start and the first `TREND_ESTABLISHED` date; the state before that date is UNDEFINED and the first established trend depends on where the data starts. Example 2 (start 2015) establishes BULL_PRIMARY only on 2018-07-26, while the full history (start 1992) is already in a trend there; choose `--start` at least two secondary legs before the period of interest, or run the full history and read the snapshot at the date you need.
- No lookahead (`R-020`, 【literature-consensus】 that a reversal is hard to tell from a secondary): Dow wrote "It is often difficult to judge whether the end of an advance has come because the movement of prices is that which would occur if the main tendency had changed. Yet, it may only be an unusually pronounced secondary movement." (nelson-1903-abc-of-stock-speculation:Q9). The machine answers it by seeing each swing only on its `confirmed_idx` bar and testing closes bar by bar, so a run cut at `--end` reproduces the full run's signals and state up to that date (`tests/test_cli.py` checks this on the fixture; the spec review replay found zero mismatches on ^DJI and ^DJT). A signal's `ts` is therefore later than the swing it reports, by the confirmation lag of `dow-swing-detection`.

**Step 7 - What the data says (labels owned by `dow-rule-backtest`)**

| Row | Rule tested | Data label | Figures from `../../../analysis/rule_status_table.md` and `../../../reports/rule_R1.md` |
|---|---|---|---|
| R1 trend_persistence | `R-016`, `R-017` (【literature-consensus】): a confirmed counter swing in an established primary is followed by a new extreme (HH or LL) | 【data-confirmed】 | p_extend 0.8788, n = 33, Wilson CI 0.7267 to 0.9518. Mandatory caveat (R11 audit F1): the 0.5 null is not a random-walk baseline; a drift-matched random walk through the same machinery gives p_extend of about 0.65 to 0.69, and the harness random-walk p is p_sim = 0.0055. Cite the baseline 0.65 to 0.69, p_sim and n = 33; never p_holm alone |
| R2 primary_reversal_signal | `R-018`, `R-020` (【literature-disputed】 overall) | 【insufficient-evidence】 | n = 12 reversal signals, below the floor of 30 events; mean excess log return at 60 sessions -0.0151, CI -0.0456 to 0.0206; pair-inconsistent |

Read R1 as: with the project's own secondary scale, trends extend more often than a drift-matched random walk would produce, on a sample of 33 events since 1992, 【data-confirmed】. Read R2 as: the reversal signal has not been tested to any conclusion, 【insufficient-evidence】. Neither row says anything about the defense line as a trading rule.

**Step 8 - Interpret and hand off**

1. Read `state` and `since`; a PRIMARY state means the last trend-side swing extended the trend; a SUSPECT state means a counter swing or a defense break happened and no new extreme has followed.
2. Read `defense_line` with its `ts` and `type`, and say agent-defined, `R-045`, 【agent-defined】 every time.
3. A reversal is declared only by a `REVERSAL_UP` or `REVERSAL_DOWN` signal (strict) or by the flip noted in a `DEFENSE_BREAK` (non-strict); a `DEFENSE_BREAK` in strict mode is a warning, not a reversal.
4. Read `secondary_direction` as the direction of the current secondary-scale leg (opposite to the last confirmed swing kind, Deviation 6); it lags until the leg is confirmed and does not say whether a reaction is in progress (spec review D10).
5. Pair confirmation is pending until `dow-confirmation-and-line` has matched the same signal kind on the second average; this skill reports one average only and never calls a reversal confirmed.

## Output

The script prints a one-row state table, a signals table, a summary line, the warm-up note and, with `--json`, one JSON document.

State table columns: `state`, `since`, `secondary_direction`, `defense_line` (price, date, kind and the word agent-defined), `last_H`, `last_L` (price and extreme date).

Signals table columns: `ts` (knowable bar), `kind`, `price`, `level`, `note`, `agent_defined`.

Summary line: signal count, symbol, bar count and date range, strict or non-strict, `equal_extreme_tol`.

JSON: `{"symbol", "bars", "start", "end", "strict", "equal_extreme_tol", "warmup_note", "trend_state": {"primary", "since", "secondary_direction", "defense_line": {"price", "ts", "type", "agent_defined": true} | null, "last_H", "prev_H", "last_L", "prev_L"}, "signals": [{"ts", "kind", "price", "level", "note", "agent_defined"}]}`. `trend_state` mirrors `AnalysisResult.trend_state` of `dow analyze` minus the pair confirmation and volume fields, which belong to the siblings. Prices are floats in JSON and `Decimal` inside the library.

When answering in prose, give the state, its `since` date, the defense line with its label, the last two highs and lows, the most recent signals with their knowable dates, and the mode; hand off pair confirmation, levels and backtest numbers to the siblings.

## Examples

### Example 1: CSV fixture, strict mode

Command, run from this skill directory:

```bash
python3 scripts/trend.py --source csv --csv ../../../tests/fixtures/dji_sample.csv
```

Real output:

```text
| state | since | secondary_direction | defense_line | last_H | last_L |
|---|---|---|---|---|---|
| BEAR_PRIMARY | 2020-12-07 | up | 28713.48 (2020-11-16, reaction_high, agent-defined) | 28713.48 (2020-11-16) | 25763.90 (2020-12-11) |

| ts | kind | price | level | note | agent_defined |
|---|---|---|---|---|---|
| 2020-09-24 | LL | 26094.87 | 27157.34 | LL: swing 2020-09-02 vs 2020-01-15, confirmed 2020-09-24 | false |
| 2020-12-07 | LH | 28713.48 | 30042.53 | LH: swing 2020-11-16 vs 2020-03-13, confirmed 2020-12-07 | false |
| 2020-12-07 | TREND_ESTABLISHED | 26179.97 | 28713.48 | BEAR_PRIMARY established (LH+LL); state before the first established trend depends on where the data starts | false |
| 2021-01-20 | LL | 25763.90 | 26094.87 | LL: swing 2020-12-11 vs 2020-09-02, confirmed 2021-01-20 | false |

4 signals | DJI_SAMPLE | bars 300 2020-01-02 -> 2021-02-24 | require_lower_high_for_reversal strict | equal_extreme_tol 0.005
Data starts 2020-01-02; the first trend was established on 2020-12-07 (BEAR_PRIMARY). ...
```

Reading: the bear is established on the bar that confirmed the LH (2020-12-07), because the LL had already been confirmed in September; the defense line is that LH at 28713.48 (`reaction_high`), agent-defined. The later LL only extends the bear. The fixture is a 300-bar synthetic sample built by `../../../tests/fixtures/make_dji_sample.py`, so dates and prices do not match the real index. `--no-strict` gives the same four signals here because no close crossed the line.

### Example 2: ^DJI from ClickHouse since 2015, strict mode

```bash
python3 scripts/trend.py --symbol ^DJI --start 2015-01-01
```

Real output on 2026-11-08 (data through 2026-11-06), abbreviated to the state, every close-driven signal, and the HH and HL rows that bound the 2018 stall and set the current line:

```text
| state | since | secondary_direction | defense_line | last_H | last_L |
|---|---|---|---|---|---|
| BULL_PRIMARY | 2023-06-15 | up | 45166.64 (2026-03-27, reaction_low, agent-defined) | 50188.14 (2026-02-10) | 45166.64 (2026-03-27) |

| 2018-07-26 | TREND_ESTABLISHED | 25527.07 | 23533.20 | BULL_PRIMARY established (HH+HL); ... | false |
| 2018-12-19 | DEFENSE_BREAK | 23323.66 | 23533.20 | close 23323.6602 < defense line 23533.1992 (agent-defined) without a counter swing; now suspect | true |
| 2020-02-25 | HH | 29551.42 | 26828.39 | HH: swing 2020-02-12 vs 2018-10-03, confirmed 2020-02-25 | false |
| 2020-03-12 | DEFENSE_BREAK | 21200.62 | 21792.20 | close 21200.6191 < defense line 21792.1992 (agent-defined) without a counter swing; now suspect | true |
| 2020-04-03 | REVERSAL_DOWN | 21052.53 | 21792.20 | close 21052.5293 crossed defense line 21792.1992 after a counter swing | false |
| 2020-04-08 | DEFENSE_BREAK | 23433.57 | 23185.62 | close 23433.5703 > defense line 23185.6191 (agent-defined) without a counter swing; now suspect | true |
| 2020-08-05 | REVERSAL_UP | 27201.52 | 23185.62 | close 27201.5195 crossed defense line 23185.6191 after a counter swing | false |
| 2022-05-09 | REVERSAL_DOWN | 32245.70 | 32632.64 | close 32245.6992 crossed defense line 32632.6406 after a counter swing | false |
| 2022-11-23 | DEFENSE_BREAK | 34194.06 | 34152.01 | close 34194.0586 > defense line 34152.0117 (agent-defined) without a counter swing; now suspect | true |
| 2023-06-15 | REVERSAL_UP | 34408.06 | 34152.01 | close 34408.0586 crossed defense line 34152.0117 after a counter swing | false |
| 2026-04-17 | HL | 45166.64 | 37645.59 | HL: swing 2026-03-27 vs 2025-04-08, confirmed 2026-04-17 | false |

36 signals | ^DJI | bars 2980 2015-01-02 -> 2026-11-06 | require_lower_high_for_reversal strict | equal_extreme_tol 0.005
```

Reading: ^DJI is BULL_PRIMARY since 2023-06-15, the bar on which the close crossed the bear-side line after the HL counter swing. The defense line is the 2026-03-27 secondary low 45166.64, `reaction_low`, set on 2026-04-17 when that HL was confirmed, 【agent-defined】 (`R-045`). The 2018-12-19 break put the bull in SUSPECT until the 2020-02-25 HH resumed it, a stall of 296 sessions, 【agent-defined】 behaviour recorded as Deviation 16; the LL confirmed on 2019-01-08 in between was bookkeeping only. The 2020 bear declared on 2020-04-03 was itself SUSPECT three sessions later, when the 2020-04-08 close rose above the 2020-03-13 reaction high 23185.62, and REVERSAL_UP followed on 2020-08-05 once the HL counter swing of 2020-06-26 had been confirmed. With `--no-strict` the same window gives 34 signals, five `DEFENSE_BREAK` flips and one `REVERSAL_DOWN`, and `since` becomes 2022-11-23. Pair confirmation against ^DJT is not part of this output (sibling).

### Example 3: the 2016-04-14 REVERSAL_UP restored by the EQUAL tolerance (full history)

```bash
python3 scripts/trend.py --symbol ^DJI --json
```

Rows for 2015 to 2016 from the real run (data from 1992-01-02):

```text
| 2015-08-21 | HH | 18312.39 | 13279.32 | HH: swing 2015-05-19 vs 2012-05-01, confirmed 2015-08-21 | false |
| 2015-10-08 | HL | 15666.44 | 12101.46 | HL: swing 2015-08-25 vs 2012-06-04, confirmed 2015-10-08 | false |
| 2016-01-08 | LH | 17918.15 | 18312.39 | LH: swing 2015-11-03 vs 2015-05-19, confirmed 2016-01-08 | false |
| 2016-02-11 | REVERSAL_DOWN | 15660.18 | 15666.44 | close 15660.1797 crossed defense line 15666.4404 after a counter swing | false |
| 2016-04-14 | REVERSAL_UP | 17926.43 | 17918.15 | close 17926.4297 crossed defense line 17918.1504 after a counter swing | false |

102 signals | ^DJI | bars 8775 1992-01-02 -> 2026-11-06 | require_lower_high_for_reversal strict | equal_extreme_tol 0.005
```

Reading: the LH of 2015-11-03 made the bull SUSPECT on 2016-01-08; the close of 2016-02-11 crossed the 2015-08-25 reaction low and flipped to BEAR_PRIMARY with the LH 17918.15 as the new line (`reaction_high`). The 2016-02-11 low itself, confirmed 2016-03-03, lies within the tolerance of the 2015-08-25 low, so it is EQUAL, emits no LL and counts as the double-bottom counter swing; the close of 2016-04-14 above 17918.15 therefore declares REVERSAL_UP. Without the tolerance that low read as LL and the strict machine stalled here for 597 sessions, measured by the spec review at `secondary_pct` 0.10 before amendment A1 (the same deadlock appears at 0.08), 【agent-defined】 diagnosis from `../../../reports/spec_review_p3.md` D3. The same case is invisible with `--start 2015-01-01` (Example 2), because the trend is not yet established there: start-date dependence in practice.

## Boundaries

| Not covered here | Sibling skill |
|---|---|
| Glossary, Chinese term mapping, label definitions, what each source says, provenance, performance studies, the full negative result on the defense line | `dow-theory-sources` |
| Swing detectors, `minor_pct` / `secondary_pct` / `secondary_min_sessions`, `confirmed_idx`, multi-scale nesting, secondary flags (`R-013`, `R-046`) | `dow-swing-detection` |
| Line detection, `LINE_BREAKOUT_UP/DOWN`, two-average pair confirmation and the `confirmation` field of `dow analyze` (`R-022` to `R-035` as code) | `dow-confirmation-and-line` |
| Support and resistance clustering, trendline fitting, chart rendering of the defense line (`R-047`, `R-049` to `R-055`) | `dow-levels-and-chart` |
| Decision table, backtest runs, the data labels 【data-confirmed】【data-refuted】【insufficient-evidence】 beyond the two rows quoted in Step 7 | `dow-rule-backtest` |

The state machine, its signals, the EQUAL tolerance and the Dow defense line are defined only here; siblings reference them. When a sibling is not installed, read `../../../docs/specs/algorithm_contract.md` (TrendStateMachine section) and `../../../research/canonical_rules.md` sections 1.3 and 1.7.

## Limitations

1. **Agent-defined constructs.** The state names, the SUSPECT mechanics, the EQUAL tolerance and the Dow defense line are the project's own (`R-045`, 【agent-defined】). The sourced content is the HH/HL definition (`R-016`), persistence (`R-017`) and the disputed reversal reading (`R-018`); everything that makes them executable is the project's choice.
2. **Strict mode can stall.** A SUSPECT state reached by a `DEFENSE_BREAK` resolves only on a counter swing or a new extreme at secondary scale; on ^DJI the longest stall since 1992 is 296 sessions from 2018-12-19, 【agent-defined】 behaviour recorded as Deviation 16, and the pre-tolerance machine stalled for 597 sessions from 2016 at the review's `secondary_pct` 0.10 configuration (the deadlock also appeared at 0.08; the current 0.08 plus 15-session configuration shows the 296-session stall above), 【agent-defined】 diagnosis in the spec review.
3. **Start-date dependence.** The first established trend and every `since` before the first reversal depend on `--start` (Step 6, Examples 2 and 3). Always read `warmup_note`.
4. **One average only.** The machine never tests the second average; orthodox sources make confirmation mandatory (`R-032`, 【literature-consensus】) and Blay's analogue of the line says so too (`R-048`, 【single-source】). Use `dow-confirmation-and-line`.
5. **Thresholds tuned in sample.** The secondary scale that drives every transition (`secondary_pct`, `secondary_min_sessions`) was chosen on ^DJI data from 1992 onward (`R-046`, 【agent-defined】; `dow-swing-detection` Step 4); different thresholds give different reversal dates and counts.
6. **Data start 1992.** ClickHouse history for ^DJI and ^DJT begins 1992-01-02; no state is known for earlier regimes.
7. **Lag by construction.** Every signal is dated at the confirmation bar, so a reversal is declared weeks after the extreme it reacts to (median secondary confirmation lag in `dow-swing-detection` Step 4); a `REVERSAL_*` price can be far from the defense line (Example 2, 2020-08-05).
8. **Evidence is thin.** R1 is 【data-confirmed】 only with its caveat (baseline 0.65 to 0.69, p_sim 0.0055, n = 33), and the reversal signal itself is 【insufficient-evidence】 (Step 7). The defense line has no data label of its own.
9. **Not advice.** The skill reports the trend state and its signals as of a date. It makes no price prediction and gives no investment advice.

## Resources

- `scripts/trend.py`: the CLI wrapper (imports `detect_multiscale`, `swings_as_of`, `run_trend`, `warmup_note`; no algorithm code). `scripts/_table.py`: row, table and JSON formatting only. `scripts/_anchor.py`: project root and `.venv` resolution shared by skill scripts.
- `tests/test_cli.py`: runs the wrapper on the project CSV fixture and on the skill's own `tests/fixtures/defense_break_sample.csv` (piecewise-linear legs generated by `tests/fixtures/make_defense_break_sample.py`: bull established, break of the reaction low without a counter swing, lower high, second break) in strict and non-strict mode; asserts the strict run gives `DEFENSE_BREAK` then `REVERSAL_DOWN` with `since` at the reversal, the non-strict run flips on the `DEFENSE_BREAK` with no `REVERSAL_*` and `since` at the break, and that the two modes differ; a ClickHouse-gated test (skipped when the container does not answer) checks the ^DJI 2015 run for the 2018-12-19 `DEFENSE_BREAK` and the 2023-06-15 `REVERSAL_UP`; also checks exit code, a valid state name, `defense_line` with `agent_defined: true` when the state is not UNDEFINED, signal kinds within the allowed set, JSON keys, the fixture's BEAR_PRIMARY outcome and `warmup_note`, and the truncation check (signals of a run cut at `--end` equal the full run's signals up to that date). Run from the project root: `uv run --python .venv/bin/python pytest .claude/skills/dow-trend-classification -q`.
- `references/evidence.md`: every verbatim quote and rule id used here, grouped by Workflow step, with `slug:Qn` and URL.
- `../../../src/dowtheory/trend.py`: `TrendState`, `Signal`, `TrendStateMachine`, `warmup_note`, `run_trend`. `../../../src/dowtheory/analysis.py`: how `analyze` drives the machine. `../../../src/dowtheory/levels.py`: `defense_line_from_state`.
- `../../../docs/specs/algorithm_contract.md` (TrendStateMachine, Deviations 5 to 7, 14, 16, 17, Amendments A2 to A5) and `../../../docs/specs/skill_contract.md`.
- `../../../configs/dow.yaml` `trend:` section.
- `../../../reports/spec_review_p3.md`: rows 2, 3 and 12 of the rule mapping, defects D3 to D5, and the look-ahead audit of the trend state. `../../../analysis/rule_status_table.md` and `../../../reports/rule_R1.md`: rows R1 and R2 with the mandatory caveat.
- `../../../tests/unit/test_trend.py`: library tests of the transitions, including the same-bar LH plus break case.
