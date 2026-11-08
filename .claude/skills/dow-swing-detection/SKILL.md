---
name: dow-swing-detection
description: >-
  Dow project swing layer: detects confirmed swing highs and lows (波段高低點, 轉折點) on
  closing prices at minor and secondary scale by percentage zig-zag (Rhea 3 percent default), ATR
  multiple or N-bar pivot, with strict H/L alternation, a confirmed_idx per swing (no lookahead), the
  causal 15-session secondary filter, and literature flags that annotate but never filter. Use when asked to list
  swings, zigzag or pivot points, ATR swings, the 3% filter, higher highs and lower lows, 次要趨勢 or
  小型趨勢 swings, when a swing was confirmed, why a correction is or is not a secondary swing, a leg's amplitude, duration or
  retrace, or how minor and secondary scales nest. Not covered: source statements and label
  definitions → dow-theory-sources; trend state, HH/HL signals, defense line →
  dow-trend-classification; lines and pair confirmation → dow-confirmation-and-line; support,
  resistance, trendlines, charts → dow-levels-and-chart; backtest results and data labels →
  dow-rule-backtest.
---

# dow-swing-detection: Confirmed swing highs and lows at two scales

> This skill is the swing-point layer of the Dow project. Its knowledge comes from the code in `../../../src/dowtheory/swings.py` and `../../../src/dowtheory/data/loader.py`, the frozen contract `../../../docs/specs/algorithm_contract.md` (Swing section, Deviations 1 to 4 and 15, Amendments A1, A5), the configuration `../../../configs/dow.yaml`, and, for the few sourced figures, the synthesis `../../../research/canonical_rules.md` built from the source notes under `../../../research/sources/`. Label vocabulary, glossary and Chinese term mapping are owned by `dow-theory-sources` and are referenced here, never restated. Every quantitative statement carries exactly one literature label from 【literature-consensus】【literature-disputed】【single-source】【agent-defined】 and, where a backtest exists, one data label from 【data-confirmed】【data-refuted】【insufficient-evidence】. Double quotes are reserved for verbatim source text with a `(slug:Qn)` pointer; everything else is paraphrase. The skill reports where swings occurred and when they became knowable. It never predicts prices and it is not investment advice.

## When to Use

- List the swing highs and lows of an index or ETF over a window, at minor or secondary scale.
- Say on which session a given swing became confirmed, and why a later leg does not yet count.
- Compare the three detectors (percentage zig-zag, ATR multiple, N-bar pivot) on the same data.
- Explain why a correction is or is not a secondary swing under the project's parameters.
- Read amplitude, duration, retrace ratio and literature flags of a secondary leg.
- Feed confirmed swings to a sibling (trend state, levels, lines, backtests) without lookahead.

Do not use it to classify the trend, draw the defense line, cluster levels, detect lines, or quote what the sources say. Those are sibling skills (see Boundaries).

## Prerequisites

1. **Project checkout and environment.** The scripts import `dowtheory` from `../../../src/`. `scripts/_anchor.py` finds the repo through `DOW_PROJECT_ROOT`, or by walking up to a directory holding `pyproject.toml` and `src/dowtheory`, and re-executes the script under `<root>/.venv/bin/python`, so any `python3` works as the launcher. Global-install setup, one line:

   ```bash
   export DOW_PROJECT_ROOT=<path-to-Dow-repo>
   ```

2. **Data access.** Two sources, chosen with `--source`:
   - `clickhouse` (default): table `dow.mkt_klines`, daily bars, read with `FINAL`, through the scoped `dow_user` login (`DOW_CLICKHOUSE_USER` / `DOW_CLICKHOUSE_PASSWORD`, host and port from `CLICKHOUSE_HOST` / `CLICKHOUSE_PORT`). ClickHouse runs only in Docker (container `trading_clickhouse`). The `usstock` and `twstock` databases are read-only and are not touched by this skill.
   - `csv`: any file with `Date` (or `ts_open`), `Open`, `High`, `Low`, `Close`, `Volume` columns, for example `../../../tests/fixtures/dji_sample.csv`. `--symbol` is required for ClickHouse; for CSV it defaults to the upper-cased file stem (`DJI_SAMPLE` for the fixture) and only labels the output, filters an optional `symbol` column and selects a per-symbol threshold. When the CSV has a `symbol` column, pass `--symbol` explicitly, otherwise the stem default filters to zero rows.
3. **`analysis_start` clipping.** `load_klines` clips close-only history (bars with open = high = low = close) to `data.analysis_start[symbol]` from `../../../configs/dow.yaml`; only `^GSPC` and `^IXIC` have a floor. Set `DOW_IGNORE_ANALYSIS_START=1` to disable. ATR needs real high/low, so never disable it for the `atr` method.
4. **Integrity gate.** Before any ClickHouse-based analysis run `.venv/bin/python scripts/check_integrity.py` from the project root (`dow check` is the same gate) and require exit 0. The gate checks coverage, gaps, duplicates, exchange conflicts, OHLC sanity, flat bars, zero volume and staleness, and logs to `dow.ops_data_quality_log`. The CSV fixture needs no gate.
5. **Siblings for definitions.** Term meanings and label semantics: `dow-theory-sources` Step 1 and Step 2. Rule ids `R-0xx` refer to `../../../research/canonical_rules.md`.

## Workflow

**Step 1 - Load bars and pick the window**

`load_klines(symbol, start, end, source, csv_path)` returns an OHLCV frame indexed by session date, ascending, deduplicated, floats. The detectors use the `close` column only; `high` and `low` are passed through for the ATR method. Closing prices only is a sourced rule (`R-036`, 【literature-consensus】), restated in Brown, Goetzmann and Kumar as "The fluctuations of the daily closing prices of the Dow-Jones rail and industrial averages afford a composite index" (brown-goetzmann-kumar-1998:Q12). Choose `--start` so that at least one full secondary leg precedes the period of interest: the first emitted swing has `amplitude_pct` 0, `duration_days` 0 and no retrace, and its confirmation can lag by months when the window opens inside a long leg (Example 2).

**Step 2 - Choose the detector (`swings.method`)**

| Method | Flip rule (paraphrase of the contract) | `confirmed_idx` | Parameters | Label |
|---|---|---|---|---|
| `pct` (default) | A candidate extreme flips once the close has moved at least `threshold` against it | the bar that met the threshold | `minor_pct` 0.03, `secondary_pct` 0.08 | threshold value 3 percent: Rhea's filter, `R-013` 【single-source】; the 8 percent secondary and both as swing thresholds: `R-046` 【agent-defined】 |
| `atr` | Same zig-zag, threshold per bar = `atr_mult` × ATR(`atr_window`) / candidate price; no flip while ATR is NaN or zero; without high/low the true range falls back to close-to-close | the bar that met the threshold | `atr_mult` 2.0, `atr_window` 14; secondary scale multiplies `atr_mult` by `secondary_pct / minor_pct` | `R-046` 【agent-defined】 |
| `pivot` | Bar i is H when its close is the maximum of the window i-n to i+n (L symmetric); flat windows yield nothing | i + n | `pivot_n` 5; secondary scale uses `pivot_n` × `secondary_pct / minor_pct`, rounded | `R-046` 【agent-defined】 |

Rhea's definition of a rally or decline as a net reversal exceeding 3 percent of either average (`R-013`, rhea-1932-the-dow-theory:Q7, quoted in `dow-theory-sources` Step 3 and in `references/evidence.md`) is absent from Dow and Hamilton and reaches this project second-hand (Wiley excerpt), so `R-013` is 【single-source】; the JSON status key is `rhea_3pct_filter` (contract A9). Everything else in the table, including the choice of 3 percent as a swing threshold rather than as Rhea's rally definition, is the project's construct under `R-046` 【agent-defined】. Note that the registry row `R-046` still records the pre-review secondary value of 10 percent, while the contract amendment A1 and the config set 8 percent (Step 4).

**Step 3 - Alternation and the no-lookahead rule**

- H and L strictly alternate; the first swing may be either kind. For `pivot`, two same-kind pivots with no opposite pivot between them are both kept and the deepest close between them is inserted as the opposite swing, confirmed with the second pivot (Deviation 1); plateau repeats without a real dip keep the earlier pivot.
- Every swing carries `confirmed_idx` and `confirmed_ts`, the first bar at which it became knowable (`confirmed_idx >= idx`). Detection is append-only, so truncation invariance holds: detecting on `close[:t+1]` and keeping swings confirmed at or before t equals `swings_as_of(detect_swings(close), t)`. Downstream code may only consume `swings_as_of(swings, t_idx)`.
- This is the operational form of the sourced warning that a reversal is hard to tell from a secondary (`R-020`, 【literature-consensus】): Dow wrote "It is often difficult to judge whether the end of an advance has come because the movement of prices is that which would occur if the main tendency had changed. Yet, it may only be an unusually pronounced secondary movement." (nelson-1903-abc-of-stock-speculation:Q9). The project answers it by dating each swing twice: when it happened and when it was known.
- Minor swings are not used for trend state, in line with Dow's advice that daily movement is low information (`R-015`, 【literature-consensus】): "The day to day movement should be disregarded by everybody, except traders, who pay no commissions. The medium swing is the one for ordinary consideration." (nelson-1903-abc-of-stock-speculation:Q3).

**Step 4 - Multi-scale nesting (`detect_multiscale`)**

| Item | Value | Mechanism | Label |
|---|---|---|---|
| Minor scale | `minor_pct` 0.03 | plain zig-zag, flags empty | `R-046` 【agent-defined】 |
| Secondary scale | `secondary_pct` 0.08 (per-symbol override via `per_symbol_secondary_pct`, currently empty) | zig-zag with the causal time filter | `R-046` 【agent-defined】, contract A1 |
| Causal time filter | `secondary_min_sessions` 15 | at confirmation bar i, the flip is accepted only when i minus the previous secondary swing's `idx` is at least 15 sessions; evaluated with bars up to i only; pct and atr only, not pivot (Deviation 15) | `R-046` 【agent-defined】; the 15-day screen Rhea used in his own statistics is a paraphrase-only figure under `R-013` 【single-source】 and is not the source of this filter |
| Nesting | snap within ±2 bars | each secondary swing snaps to the nearest same-kind minor swing within two bars, takes its bar and price, and keeps the later of the two confirmations; unsnapped swings are kept unchanged (Deviation 4); the library drops the snapped flags, so `scripts/swings.py` recomputes `snapped` exactly as whether a minor swing with the same bar and kind exists, prints `secondary*` for an unsnapped swing and emits `snapped` in JSON | `R-046` 【agent-defined】 |

Justification for 0.08 and the filter, project analysis from `../../../reports/spec_review_p3.md` section 3b, ^DJI 1992 onward, 【agent-defined】 (in-sample inspection, not a literature figure and not a backtest result):

| `secondary_pct` | swings | reaction legs | reactions with retrace in the Rhea band | reactions inside the Rhea duration window | reversals | median confirmation lag (bars) |
|---|---|---|---|---|---|---|
| 0.10 | 53 | 23 | 39 % | 57 % | 8 | 23 |
| 0.08 | 88 | 39 | 46 % | 67 % | 12 | 16 |
| 0.08 + 15-session filter | 82 | 37 | 49 % | 73 % | 10 | 19 |

The review judged 0.10 too coarse (the 2023 correction of about 9 percent is invisible) and 0.08 with the filter the most Rhea-like, 【agent-defined】. The current run on the full ^DJI history gives 450 minor and 84 secondary swings over 8775 bars (Example 2), 【agent-defined】 count from this project's data.

**Step 5 - Read the secondary metrics and flags (`compute_secondary_metrics`, contract A5)**

| Field | Definition | Literature anchor | Label |
|---|---|---|---|
| `amplitude_pct` | abs(price / previous same-scale swing price - 1) | none | measurement, no rule |
| `duration_days` | calendar days since the previous same-scale swing | `R-006`, `R-007` | recorded only; duration bounds 【literature-disputed】 |
| `retrace_ratio` | abs(this leg) / abs(previous opposite leg), secondary only, None for the first two swings | `R-010`: the base matches neither Rhea's move since the last secondary nor the educators' whole primary swing | 【literature-disputed】 |
| `flags.rhea_window` | `secondary_min_days` 21 ≤ duration ≤ `secondary_max_days` 90 | Rhea: "usually lasting from three weeks to as many months" (rhea-1932-the-dow-theory:Q5); `R-006`, `R-007` | 【literature-disputed】; side-by-side positions in `dow-theory-sources` Step 3 |
| `flags.schannep_window` | duration ≥ `schannep_min_days` 8 and amplitude ≥ `schannep_min_pct` 0.03 | Schannep's 8 trading days (thedowtheory-lines-special-issue:Q8, `R-006` position P1) and his 3 percent counter move (schannep-dow-theory-21st-century:Q1, `R-012`); both quoted in `dow-theory-sources` Step 3 | `R-012` 【single-source】. Unit mismatch: the config threshold is compared with calendar `duration_days`, while Schannep's figure counts trading days (about 10 to 12 calendar days), so the flag is a loose approximation, 【agent-defined】 under `R-046` |
| `flags.retrace_in_third_two_thirds` | 1/3 ≤ `retrace_ratio` ≤ 2/3 | the 33 to 66 percent clause of the same Rhea sentence (rhea-1932-the-dow-theory:Q5); `R-008`, `R-009` | 【literature-disputed】 |
| `flags.retrace_in_third_half` | 1/3 ≤ `retrace_ratio` ≤ 1/2 | Taiwan educator position P2 under `R-009` (stockfeel-dow-theory:Q6; see `dow-theory-sources` Step 3) | 【literature-disputed】 |

Flags never filter swings; they annotate. Data labels from `../../../analysis/rule_status_table.md` (backtest run on pair DJ, specification `pct0.03/0.08f15`): row R5 secondary_duration, mapped to `R-006` and `R-007`, is 【insufficient-evidence】 (share of secondaries in the Rhea window 0.7273, n 44, p_holm 0.31 above alpha 0.05); row R4 secondary_retracement, mapped to `R-008` to `R-011`, is 【insufficient-evidence】 (share in the 1/3 to 2/3 band 0.4091, n 44, p_holm 1.0). The labelling rule itself is explained by `dow-rule-backtest`, the authority for those labels.

**Step 6 - Run and read the output**

```bash
# from this skill directory; any python3 re-executes under the project .venv
python3 scripts/swings.py --symbol ^DJI --start 2024-01-01 --scale secondary
python3 scripts/swings.py --symbol ^DJI --source csv --csv ../../../tests/fixtures/dji_sample.csv --method pivot --json
```

Reading order: sort by `ts`; a secondary row printed as `secondary*` (JSON `snapped: false`) was not snapped onto a minor swing; compare `confirmed_ts` with the as-of date before using a swing; read `flags` as annotations and `retrace_ratio` above 1 as a leg that exceeded the previous opposite leg (a trend-side leg, not a reaction).

## Output

The script prints a markdown table, a summary line and, with `--json`, one JSON document.

Table columns: `ts`, `kind` (H or L), `price` (close), `confirmed_ts`, `scale`, `amplitude_pct`, `duration_days`, `retrace` (3 decimals or `-`), `flags` (comma-joined names of the true flags, or `-`). An unsnapped secondary swing shows `secondary*` in the scale column.

Summary line: swing count, symbol, bar count and date range, method, minor and secondary thresholds, `secondary_min_sessions`.

JSON: `{"symbol", "method", "bars", "thresholds": {"minor_pct", "secondary_pct", "secondary_min_sessions"}, "swings": [{"ts", "kind", "price", "confirmed_ts", "scale", "amplitude_pct", "duration_days", "retrace_ratio", "flags": {"rhea_window", "schannep_window", "retrace_in_third_two_thirds", "retrace_in_third_half"}, "snapped"}]}`. Minor swings carry an empty `flags` object and `snapped: null`; secondary swings carry the four flag keys and a boolean `snapped`. Prices are floats in JSON and `Decimal` inside the library.

When answering in prose, give for each swing its two dates (extreme and confirmation), the scale, and the label of any threshold mentioned; hand off trend state, levels and backtest numbers to the siblings.

## Examples

### Example 1: CSV fixture, percentage method, both scales

Command, run from this skill directory:

```bash
python3 scripts/swings.py --symbol ^DJI --source csv --csv ../../../tests/fixtures/dji_sample.csv
```

Abbreviated real output (first rows and the summary line):

```text
| ts | kind | price | confirmed_ts | scale | amplitude_pct | duration_days | retrace | flags |
|---|---|---|---|---|---|---|---|---|
| 2020-01-07 | H | 28302.84 | 2020-01-09 | minor | 0.00% | 0 | - | - |
| 2020-01-15 | L | 27157.34 | 2020-01-21 | minor | 4.05% | 8 | - | - |
| 2020-01-15 | L | 27157.34 | 2020-03-06 | secondary | 0.00% | 0 | - | - |
| 2020-03-13 | H | 30042.53 | 2020-03-27 | minor | 10.62% | 58 | - | - |
| 2020-03-13 | H | 30042.53 | 2020-05-18 | secondary | 10.62% | 58 | - | rhea_window,schannep_window |
| 2020-06-11 | L | 26532.03 | 2020-06-24 | minor | 11.69% | 90 | - | - |
...
20 swings | ^DJI | bars 300 2020-01-02 -> 2021-02-24 | method pct minor 0.03 secondary 0.08 min_sessions 15
```

Reading: the 2020-01-15 low is both a minor and a secondary swing (snapped); as a minor swing it was knowable on 2020-01-21, as a secondary swing only on 2020-03-06, because the secondary flip needs the larger threshold and the time filter. The fixture is a 300-bar synthetic sample built by `../../../tests/fixtures/make_dji_sample.py`, so its dates and prices do not match the real index.

### Example 2: ^DJI from ClickHouse, secondary scale since 2024

Command:

```bash
python3 scripts/swings.py --symbol ^DJI --start 2024-01-01 --scale secondary
```

Real output on 2026-11-08 (data through 2026-11-06):

```text
| ts | kind | price | confirmed_ts | scale | amplitude_pct | duration_days | retrace | flags |
|---|---|---|---|---|---|---|---|---|
| 2024-01-17 | L | 37266.67 | 2024-07-16 | secondary | 0.00% | 0 | - | - |
| 2024-12-04 | H | 45014.04 | 2025-03-12 | secondary | 20.79% | 322 | - | schannep_window |
| 2025-04-08 | L | 37645.59 | 2025-04-30 | secondary | 16.37% | 125 | 0.951 | schannep_window |
| 2026-02-10 | H | 50188.14 | 2026-03-19 | secondary | 33.32% | 308 | 1.702 | schannep_window |
| 2026-03-27 | L | 45166.64 | 2026-04-17 | secondary | 10.01% | 45 | 0.400 | rhea_window,schannep_window,retrace_in_third_two_thirds,retrace_in_third_half |

5 swings | ^DJI | bars 716 2024-01-02 -> 2026-11-06 | method pct minor 0.03 secondary 0.08 min_sessions 15
```

Reading: the 2025-04-08 low became knowable on 2025-04-30, 15 sessions later (`R-046` 【agent-defined】 threshold and filter), when the rebound exceeded the secondary threshold and the time filter had elapsed; its retrace ratio 0.951 says it gave back almost the whole prior up-leg, so it sits outside every retracement band and only the Schannep flag is true. The 2026-03-27 low is the one secondary swing in this window inside the Rhea window and both retracement bands. The first row is an artefact of the window start: a long up-leg began before 2024-01-01, so the first swing has no previous swing and was confirmed only in July. The full history (no `--start`) yields 450 minor and 84 secondary swings over 8775 bars from 1992-01-02, 【agent-defined】 count from this project's data. All thresholds behind these rows are `R-046` 【agent-defined】.

### Example 3: same fixture, pivot method, secondary only

```bash
python3 scripts/swings.py --source csv --csv ../../../tests/fixtures/dji_sample.csv --method pivot --scale secondary
```

```text
| 2021-01-05 | L | 26561.75 | 2021-01-22 | secondary | 2.47% | 11 | 0.458 | retrace_in_third_two_thirds,retrace_in_third_half |
| 2021-01-28 | H | 28250.33 | 2021-02-16 | secondary | 6.36% | 23 | 2.509 | rhea_window,schannep_window |

15 swings | DJI_SAMPLE | bars 300 2020-01-02 -> 2021-02-24 | method pivot minor 0.03 secondary 0.08 min_sessions 15
```

Reading: pivot confirmation is fixed at n bars after the extreme (here the secondary scale uses n = round(5 × 0.08 / 0.03) = 13), so small legs pass that the percentage method would merge; the time filter does not apply to pivots. The pivot method therefore yields more and smaller secondary swings than the percentage method on the same data.

## Boundaries

| Not covered here | Sibling skill |
|---|---|
| Glossary, Chinese term mapping, label definitions, what each source says, provenance, performance studies | `dow-theory-sources` |
| Trend state machine, HH/HL/LH/LL and EQUAL swings, SUSPECT states, defense line definition and `DEFENSE_BREAK` (`R-016` to `R-018`, `R-045`) | `dow-trend-classification` |
| Line detection, line breakout, two-average pair confirmation (`R-022` to `R-035` as code) | `dow-confirmation-and-line` |
| Support and resistance clustering from swings, trendline fitting, chart rendering (`R-047`, `R-049` to `R-055`) | `dow-levels-and-chart` |
| Decision table, backtest runs, the data labels 【data-confirmed】【data-refuted】【insufficient-evidence】 | `dow-rule-backtest` |

Swing definitions, detector parameters, `confirmed_idx` semantics, nesting and flags are defined only here; siblings reference them. When a sibling is not installed, read `../../../docs/specs/algorithm_contract.md` and `../../../research/canonical_rules.md` section 7.

## Limitations

1. **Thresholds are agent-defined and were tuned in sample.** The 3 percent minor, 8 percent secondary and 15-session filter were chosen after inspecting ^DJI 1992 to 2026 (Step 4 table), `R-046` 【agent-defined】. They are not literature figures and the sensitivity table is not an out-of-sample test. Rhea's 3 percent (`R-013`, 【single-source】) defined a rally or decline, not a swing-detection threshold.
2. **The time filter delays confirmation; it does not lengthen legs.** The flip is deferred until 15 sessions have passed since the previous swing's bar, so a secondary leg can still be one day long when the reversal is sharp (for example a ^DJI secondary high on 2020-03-13 one day after the 2020-03-12 low, confirmed 2020-04-03), 【agent-defined】 behaviour under `R-046`.
3. **Close-only.** All three methods pick extremes from closes (`R-036`, 【literature-consensus】); intraday highs and lows enter only through the ATR scale. Close-only history before `analysis_start` makes ATR degenerate, hence the clipping.
4. **All series are stored unadjusted.** The fetcher uses `auto_adjust=False`, so `SPY` and `IYT` closes drop by the dividend on each ex-date, while `^DJI`, `^DJT`, `^GSPC`, `^IXIC` are price indices that carry no dividend cash at all. ETF swing amplitudes therefore embed small dividend gaps and are not directly comparable with index swings.
5. **Schannep flag unit mismatch.** `schannep_min_days` is compared with calendar `duration_days`, while Schannep's 8-day figure counts trading days; the flag is looser than the source, 【agent-defined】 approximation under `R-046`, and a candidate contract amendment (count sessions).
6. **Data start.** The project's ClickHouse history for `^DJI` and `^DJT` begins 1992-01-02; nothing before that is analysed, so the earlier regimes studied by Cowles or Brown, Goetzmann and Kumar are out of reach.
7. **First swing and window edges.** The first swing has no amplitude, duration or retrace, and its confirmation can arrive long after `--start` (Example 2). The last candidate extreme is never emitted until the market confirms it.
8. **Flags are weak discriminators.** In the Step 4 table at most 49 percent of reactions fall in the 1/3 to 2/3 band at any threshold, 【agent-defined】 project analysis, and the backtest data label for both duration and retracement is 【insufficient-evidence】 (Step 5); treat flags as descriptive.
9. **Pivot lookahead is explicit, not absent.** A pivot is knowable only n bars later; `confirmed_idx = i + n` encodes that. Comparing pivot and percentage swings by `ts` alone hides the different confirmation lags.
10. **Not advice.** The skill reports where swings occurred and when they were knowable. It makes no price prediction and gives no investment advice.

## Resources

- `scripts/swings.py`: the CLI wrapper (imports `detect_multiscale` and `load_klines`; no algorithm code). `scripts/_table.py`: row and table formatting only. `scripts/_anchor.py`: project root and `.venv` resolution shared by skill scripts.
- `tests/test_cli.py`: runs the wrapper on the CSV fixture for `pct`, `atr`, `pivot`; checks exit code, alternation per scale, JSON keys, the secondary flag keys, `retrace_ratio` None on the first two secondary swings, the 15-session gap between consecutive secondary swings, the Example 1 count of 20 and the date window. Run from the project root: `uv run --python .venv/bin/python pytest .claude/skills/dow-swing-detection -q`.
- `references/evidence.md`: every verbatim quote and rule id used here, grouped by Workflow step, with `slug:Qn` and URL.
- `../../../src/dowtheory/swings.py`: `Swing`, `detect_swings`, `swings_as_of`, `nest_scales`, `secondary_flags`, `compute_secondary_metrics`, `detect_multiscale`. `../../../src/dowtheory/data/loader.py`: `load_klines`, `load_pair`. `../../../src/dowtheory/data/quality.py` and `../../../scripts/check_integrity.py`: the integrity gate.
- `../../../docs/specs/algorithm_contract.md` (Swing section, Deviations, Amendments A1 and A5) and `../../../docs/specs/skill_contract.md`.
- `../../../configs/dow.yaml` `swings:` and `data:` sections.
- `../../../reports/spec_review_p3.md` section 3b: threshold sensitivity table. `../../../analysis/rule_status_table.md`: data labels R4 and R5.
- `../../../tests/unit/test_swings.py`: truncation-invariance and alternation tests of the library.
