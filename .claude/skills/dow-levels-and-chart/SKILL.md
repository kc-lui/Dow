---
name: dow-levels-and-chart
description: >-
  Dow project drawing layer: one command renders the PNG chart, its JSON twin and the markdown
  report of a Dow analysis, with support and resistance zones clustered from swing lows and highs
  (side-filtered so resistance sits above and support below the as-of close), the trendline through
  the last two secondary higher lows or lower highs, the Dow defense line drawn dashed red and
  labelled agent-defined, Dow line ranges shaded, swing and signal markers. Use when asked
  to draw or plot a Dow chart, produce a PNG, list support or resistance zones, levels, trendlines,
  whether a trendline is still valid, how to read the chart or the report,
  支撐線 / 壓力線 / 趨勢線 / 畫線 / 道氏防線 drawing, or to run dow analyze. Not covered: sources and labels → dow-theory-sources; swing detection →
  dow-swing-detection; trend state and the defense line definition → dow-trend-classification;
  pair confirmation and line detection → dow-confirmation-and-line; backtest results →
  dow-rule-backtest.
---

# dow-levels-and-chart: Support and resistance zones, trendlines and the chart

> This skill is the drawing layer of the Dow project. Its knowledge comes from the code in `../../../src/dowtheory/levels.py`, `../../../src/dowtheory/chart.py` and `../../../src/dowtheory/report.py`, the driver `../../../src/dowtheory/analysis.py` and CLI `../../../src/dowtheory/cli.py`, the frozen contract `../../../docs/specs/algorithm_contract.md` (levels.py, chart.py and CLI sections, Deviations 8 and 12, Amendment A8), the configuration `../../../configs/dow.yaml` (`levels:`), and the synthesis `../../../research/canonical_rules.md` (section 1.8 and section 6) built from the source notes under `../../../research/sources/` (see `dow-theory-sources`). Glossary, Chinese term mapping and label vocabulary are owned by `dow-theory-sources`; swing definitions by `dow-swing-detection`; the trend state machine and the Dow defense line by `dow-trend-classification`; Dow lines and pair confirmation by `dow-confirmation-and-line`; all are referenced, never restated. Every quantitative statement carries exactly one literature label from 【literature-consensus】【literature-disputed】【single-source】【agent-defined】 and, where a backtest exists, one data label from 【data-confirmed】【data-refuted】【insufficient-evidence】. Double quotes are reserved for verbatim source text with a `(slug:Qn)` pointer; everything else is paraphrase. The zone and trendline parameters are this project's choices and are labelled 【agent-defined】; the defense line has no literature source. The chart describes the trend state as of a date. It never predicts prices, draws no targets, and it is not investment advice.

## When to Use

- Draw the chart of one average with its confirmation pair as of a date and hand back the PNG, the JSON twin and the markdown report.
- List the support and resistance zones with their touch counts and explain why a side may be empty (`levels_note`).
- Report the current uptrend or downtrend line, its anchors, its value at the as-of date and whether it is still valid.
- Explain what each chart element is, which skill owns its definition and which label it carries.
- Run `dow analyze` with any flag combination, including `--as-of` historical runs and `--persist`.

Do not use it to detect swings, classify the trend, decide pair confirmation or lines, or quote backtest numbers. Those are sibling skills (see Boundaries).

## Prerequisites

1. **Project checkout and environment.** The script imports `dowtheory` from `../../../src/`. `scripts/_anchor.py` finds the repo through `DOW_PROJECT_ROOT`, or by walking up to a directory holding `pyproject.toml` and `src/dowtheory`, and re-executes the script under `<root>/.venv/bin/python`, so any `python3` works as the launcher. Matplotlib renders with the `Agg` backend, so no display is needed. Global-install setup, one line:

   ```bash
   export DOW_PROJECT_ROOT=<path-to-Dow-repo>
   ```

2. **Data access.** Same two sources as `dow-swing-detection` Prerequisites 2 to 4: `--source clickhouse` (the default) reads `dow.mkt_klines` with `FINAL` through `ClickHouseClient`, whose connection comes from `CLICKHOUSE_HOST`, `CLICKHOUSE_PORT`, `CLICKHOUSE_DATABASE`, `DOW_CLICKHOUSE_USER` and `DOW_CLICKHOUSE_PASSWORD` (template in `../../../.env.example`); `--source csv --csv PATH [--csv-pair PATH]` reads one file per leg, the pair file defaulting to the first, with symbols defaulting to the upper-cased file stems. Run the integrity gate `.venv/bin/python scripts/check_integrity.py` from the project root before any ClickHouse-based run; CSV fixtures need no gate.
3. **Pair default.** With the ClickHouse source and no `--pair`, the partner comes from `../../../configs/pairs.yaml` (`^DJI` with `^DJT`), exactly as `dow analyze` does (contract Deviation 13). Without a pair there are no Dow lines and pair confirmation reads `pending` with the detail `no pair supplied`.
4. **Configuration.** `levels.tol_mode` (`pct`), `levels.tol_pct` (`0.0075`), `levels.tol_atr_mult` (`0.5`), `levels.min_touches` (`2`), `levels.max_levels` (`4`) and `levels.trendline_tol_pct` (`0.01`) in `../../../configs/dow.yaml`. There are no CLI overrides; change the config to experiment, and note that the config hash in the report changes with it.
5. **Upstream layers.** Everything drawn is computed by `analysis.analyze`: swings by `dow-swing-detection`, the state and defense line by `dow-trend-classification`, lines and confirmation by `dow-confirmation-and-line`. Nothing about them is defined here.
6. **Siblings for definitions.** Term meanings and label semantics: `dow-theory-sources` Steps 1 and 2. Rule ids `R-0xx` refer to `../../../research/canonical_rules.md`.

## Workflow

**Step 1 - What the literature says about drawing (by pointer; none of it is a Dow Theory rule)**

The registry's section 6 records that Dow, Hamilton and Rhea give no support, resistance or trendline drawing rule, and that the Edwards and Magee Dow chapters do not mention support and resistance drawing (their separate chapter on the subject is outside the project's notes). Dow's own chart is the book method, recorded as history with no rule id (【literature-consensus】 that it is Dow's own text): "Prices are set down, giving each change of 1 point as it occurs, forming thereby lines having a general horizontal direction but running into diagonals as the market moves up and down." (nelson-1903-abc-of-stock-speculation:Q11), plus the double top observation (nelson Q14). What the educators say, with their labels:

| Convention | Source, by pointer | Rule | Label |
|---|---|---|---|
| an uptrend line joins rising lows, a downtrend line joins falling highs | stockcloud trendline note Q2, Q7, Q21 (Chinese textbook summary, paraphrased); Sperandeo: a trendline "connects all the lows for an uptrend or all the highs for a downtrend" (sperandeo-123-stockjock:Q1); OANDA trend-continuation Q8 and after-breakout Q2 (paraphrased: a resistance line joins highs, a support line joins lows) | `R-049` | 【literature-consensus】 among educators only |
| a valid uptrend line needs at least two rising lows | stockcloud Q8 (paraphrased); Sperandeo Q1 says all the lows | `R-050` | 【single-source】 |
| draw on a log chart; a slope near 45 degrees is the most meaningful | stockcloud Q5, Q6, Q10 (paraphrased) | `R-051`, `R-052` | 【single-source】, not implemented |
| a break is valid after two consecutive closes beyond the line, or a close penetration of at least 3 percent; these are alternatives | stockcloud Q14, Q17, Q19 (paraphrased); Q18 says the 3 percent rule is unsuited to margined futures | `R-053` | 【single-source】, only partly implemented |
| broken support becomes resistance and the reverse (role swap) | stockcloud Q13; OANDA breakout-return-moves Q4, Q5 (paraphrased) | `R-054` | 【literature-consensus】 among educators, not implemented |
| horizontal levels come from repeatedly tested prices; no zone width is given | kcmtrade Q9, Q19 (paraphrased) | `R-055` | 【single-source】 |
| the lows of secondary reactions serve as the exit point when broken | "The lows of secondary reactions serve as our exit point (stop-loss) when broken down" (thedowtheory-rhea-three-weeks:Q6), "(always with confirmation)" (thedowtheory-rhea-three-weeks:Q7) | `R-048` | 【single-source】; same geometry as the defense line, which stays 【agent-defined】 (`R-045`) |

None of these sources ties resistance near prior highs or support near prior lows to Dow Theory itself; the registry files them as adjacent constructs (section 1.8). The project's zone width, touch count, level cap and trendline tolerance have no source and are registered as `R-047` (【agent-defined】).

**Step 2 - Run**

```bash
# from this skill directory; any python3 re-executes under the project .venv
python3 scripts/draw.py --symbol ^DJI --pair ^DJT --start 2015-01-01 --out-dir ../../../outputs/charts
python3 scripts/draw.py --symbol ^DJI --as-of 2022-09-30 --start 2015-01-01 --out-dir /tmp/dow/charts
python3 scripts/draw.py --source csv --csv ../../../tests/fixtures/dji_sample.csv --out-dir /tmp/dow/charts --json
python3 scripts/draw.py --symbol ^DJI --pair ^DJT --no-chart --out-dir /tmp/dow/charts
# the project CLI, same engine, plus --persist
cd ../../../ && uv run dow analyze --symbol ^DJI --pair ^DJT --start 2015-01-01 [--as-of YYYY-MM-DD] [--method pct|atr|pivot] [--no-chart] [--persist] [--out-dir outputs/charts]
```

Flags: `--symbol`, `--pair`, `--source clickhouse|csv`, `--csv`, `--csv-pair`, `--start`, `--as-of` (bars are cut there; `--end` is an alias), `--method pct|atr|pivot` (overrides `swings.method`), `--out-dir` (PNG directory; the JSON twin goes to its sibling `json/` directory), `--no-chart` (markdown and JSON only), `--json` (also print the JSON document). The wrapper calls `analysis.analyze`, `report.to_markdown` and `chart.render_chart` and contains no algorithm code. `--persist` exists only on `dow analyze`: it inserts the run into `dow.str_swing_log`, `dow.str_trend_state_snapshots` (payload = the full JSON) and `dow.str_level_log` (one row per support zone, resistance zone, trendline and defense line, with `level_type`, `price`, `zone_low`, `zone_high`, `touches`, `slope_per_day`, keyed by `run_id`, `symbol`, `ts`).

**Step 3 - Support and resistance zones as implemented (`R-047`, `R-055`; 【agent-defined】)**

`cluster_levels` (contract levels.py section, Deviation 8, Amendment A8):

| Element | Implementation | Label |
|---|---|---|
| input | confirmed minor swings of the analysed symbol as of the evaluation bar (secondary swings alone rarely repeat within the tolerance, Deviation 8); lows (`L`) for support, highs (`H`) for resistance | 【agent-defined】 |
| side filter (A8) | resistance clusters only swing highs at or above the as-of close, support only swing lows at or below it; resistance is never reported below the price | 【agent-defined】, introduced after the spec review found all four resistance zones below the close (D7) |
| tolerance | `tol_pct` 0.75 percent of the cluster mean, or `tol_atr_mult` 0.5 times the ATR when `tol_mode` is `atr` (`R-047`) | 【agent-defined】 |
| grouping | prices sorted ascending and joined greedily: a swing joins the open cluster while its price is within the tolerance of the running mean, so a cluster may spread beyond one tolerance (spec review row 13) | 【agent-defined】 |
| zone | min and max of the members, widened to at least plus or minus half a tolerance around the mean so it is visible; `price` is the member mean | 【agent-defined】 |
| touches | members per cluster; clusters with fewer than `min_touches` 2 members are dropped (`R-047`) | 【agent-defined】 |
| cap and order | the `max_levels` 4 clusters closest to the as-of close are kept, ties broken by more touches (`R-047`); the report lists them nearest first | 【agent-defined】 |
| `levels_note` | when a side has fewer than `min_touches` qualifying swings, `meta.levels_note` says so and that side is empty (A8); at an all-time high the resistance side is always empty | 【agent-defined】 |

Not implemented, so never claim them from this output: role swap after a break (`R-054`, 【literature-consensus】 among educators); a volume test on a level break (stockcloud Q22 to Q25, paraphrased, `R-029`-like, 【single-source】); any level outside the window loaded by `--start`, because the swings and therefore the zones depend on the start date (spec review row 13, 【agent-defined】 observation).

**Step 4 - Trendlines as implemented (`R-049` to `R-053`)**

`fit_trendlines` (contract levels.py section):

| Element | Implementation | Literature, by pointer | Label |
|---|---|---|---|
| anchors | the last two confirmed secondary lows for the uptrend line, the last two confirmed secondary highs for the downtrend line; the line exists only when the second anchor is a higher low (up) or a lower high (down) | rising lows / falling highs (`R-049`, 【literature-consensus】 among educators) | two-point rule 【agent-defined】; `R-050` gives two as a minimum, Sperandeo says all the lows |
| geometry | linear in calendar days, `slope_per_day` = price difference over days; extended from the first anchor to the as-of date (`value_at_as_of`) | log chart (`R-051`), 45 degrees (`R-052`) | not implemented, 【single-source】 each |
| validity | `valid` is true when no close from the first anchor to the as-of bar lies more than `trendline_tol_pct` 1 percent below an uptrend line or above a downtrend line; a broken line is still drawn, faded, and tagged `(broken)` in the legend | two closes or 3 percent penetration (`R-053`, 【single-source】) | 1 percent tolerance 【agent-defined】 |
| touches | swing points of the same kind from the first anchor onward within the tolerance of the line, anchors included | none | 【agent-defined】 |
| count | zero or one line per direction; both can exist in the same run | none | 【agent-defined】 |

Honest note: the tolerance is a continuous version of neither educator alternative; a one-session close 1.5 percent through the line invalidates it here, while the two-close rule would wait and the 3 percent rule would ignore it (`R-053`, 【single-source】). Closes are used, not intraday extremes (`R-036`, 【literature-consensus】 for signals; the registry notes trendlines may use either).

**Step 5 - What else is drawn, owned elsewhere**

- **Dow defense line.** Dashed red horizontal from its set date to the as-of bar, annotated `Dow defense line (agent-defined): <price>`, and listed in the report as `Defense line [agent-defined]` with its type (`reaction_low` or `reaction_high`) and set date. Its definition, refresh rule and the no-source finding (`R-045`, 【agent-defined】) belong to `dow-trend-classification` Step 4 and `dow-theory-sources` Step 6; this skill only draws it and never presents it as canonical.
- **Dow lines.** Grey vertical bands over each line range; ranges shorter than 28 calendar days are not shaded because at the project band they are too frequent to read (contract Deviation 12, 【agent-defined】 presentation rule), and the legend says `line >= 28 days`. Line breakouts are small triangles on the close (blue up, purple down). Detection, breakout and dual confirmation belong to `dow-confirmation-and-line` Steps 4 and 5.
- **Swings and signals.** Minor swings as small grey dots, secondary highs as red down-triangles and secondary lows as green up-triangles (`dow-swing-detection`). `REVERSAL_UP`, `REVERSAL_DOWN` and `DEFENSE_BREAK` get a dotted vertical line with the kind written vertically; HH/HL/LH/LL and `TREND_ESTABLISHED` are not repeated on the chart (Deviation 12). Signal meanings: `dow-trend-classification` Step 3.
- **Pair close.** The confirmation pair is drawn in orange on a right-hand axis with its own scale, so the two series share dates but not price levels.

**Step 6 - Chart anatomy and files**

Two panels sharing the date axis: price (four fifths) and volume in millions (one fifth). Title: `{symbol} vs {pair} | {primary} since {since} | confirmation: {status} | method {method} {minor_pct}/{secondary_pct}`. Legend outside right, one entry per element actually present (an empty side adds no zone entry). Support zones are green bands with a `SUP xN` label at the left edge, resistance zones red bands with `RES xN`, N being the touch count. Trendlines are solid green (up) or red (down). Filename: `{sym}_{pair}_{as_of}_{method}{minor_pct}.png` with `^` stripped, so a historical `--as-of` never overwrites the latest chart. The JSON twin has the same stem under the sibling `json/` directory and holds the full `AnalysisResult` (`meta`, `trend_state`, `swings`, `levels`, `lines`, `signals`, `status_labels`); the markdown report is printed to stdout.

**Step 7 - Read the markdown report**

1. **Header.** Symbol, pair, as-of date, method and thresholds, `run_id`, config hash prefix; `Warm-up note` when the first state depends on the data start (`dow-trend-classification` Step 6).
2. **Trend state.** Primary state and since date, secondary direction, pair confirmation status and detail, volume flag, the defense line with its `[agent-defined]` tag. Read it through `dow-trend-classification` and `dow-confirmation-and-line`.
3. **Secondary swings.** The last twelve, with confirmation date, amplitude, duration and retrace ratio (`dow-swing-detection`).
4. **Levels.** Support rows then resistance rows, nearest to the close first, with `Zone` as `low - high` and `Touches`; `Note:` repeats `levels_note` when a side is empty; then the trendline table with `P0`, `P1`, `Slope/day`, `At as-of`, `Touches`, `Valid` (`yes` or `broken`). Phrase a zone as a band where prior swing lows (or highs) clustered, labelled 【agent-defined】 (`R-047`), never as a floor or ceiling that will hold.
5. **Lines.** The last ten line ranges with both band widths, breakout and `Confirmed (both)` date or `pending` (`dow-confirmation-and-line` Step 5).
6. **Signals.** The last fifteen trend signals with `Agent-defined` yes/no and the pair confirmation per reversal; line breakouts are counted in the heading.
7. **Status labels.** The seven labels carried by every result (`defense_line` agent-defined, `line_definition` literature-consensus, and so on, owned by `dow-theory-sources`).

**Step 8 - What the data says, persist and hand off**

No backtest rule in `../../../analysis/decision_table.md` (rules R1 to R8) tests support zones, resistance zones or trendlines, so no R-row exists for them; every statement about zones and trendlines carries 【insufficient-evidence】 by absence, and no claim that a zone held or a trendline break mattered may be made from this skill. The drawn elements that do have backtest coverage are the primary state in the title (R1 trend persistence, 【data-confirmed】 with its mandatory caveat) and the `REVERSAL_*` markers (R2, 【insufficient-evidence】), both reported in `dow-trend-classification` Step 7, and the line-breakout triangles (R6, 【insufficient-evidence】), reported in `dow-confirmation-and-line` Step 7. The defense line and `DEFENSE_BREAK` are excluded from the backtest family as agent-defined, so no row tests them.

1. Give the PNG and JSON paths, then the levels table and the trendline row in prose with their labels.
2. Say which side is empty and why (`levels_note`), and whether the trendline is valid or broken under the 1 percent tolerance (【agent-defined】).
3. Point the defense line to `dow-trend-classification`, lines and confirmation to `dow-confirmation-and-line`, swings to `dow-swing-detection`, any evidence question to `dow-rule-backtest`.
4. With `--persist`, report the rows written per table; the level rows can be read back from `dow.str_level_log` by `run_id`.

## Output

The script prints the markdown report, then `JSON: <path>` and, unless `--no-chart`, `Chart: <path>`; with `--json` one JSON document follows.

Markdown sections, in order: `# Dow analysis: {symbol} vs {pair} as of {as_of}`, method line, `## Trend state`, `## Secondary swings (n; minor swings: m)`, `## Levels` (zone table, optional `Note:`, trendline table), `## Lines (n; last 10 shown)`, `## Signals (...)`, `## Status labels`.

JSON `levels`: `{"support": [{"price", "zone_low", "zone_high", "touches"}], "resistance": [same], "trendlines": [{"kind": "up"|"down", "p0": [date, price], "p1": [date, price], "slope_per_day", "touches", "valid", "value_at_as_of"}]}`; `meta.levels_note` present only when a side is empty; `trend_state.defense_line`: `{"price", "ts", "type", "agent_defined": true}` or `null`. The remaining sections are documented by the owning siblings.

When answering in prose, give the file paths, the zones nearest the close on each side with touch counts, the trendline anchors, slope and validity, the defense line with its agent-defined tag, and the Step 8 data statement; hand the rest to the siblings.

## Examples

### Example 1: CSV fixture, both legs, into a temporary directory

Command, run from this skill directory:

```bash
python3 scripts/draw.py --source csv --csv ../../../tests/fixtures/dji_sample.csv --out-dir /tmp/dow/charts
```

Real output, the Trend state defense row, the Levels section and the file lines:

```text
| Defense line [agent-defined] | 28,713.48 (reaction_high, set 2020-11-16) - agent-defined, no literature source |

## Levels

| Type | Price | Zone | Touches |
|---|---|---|---|
| support | 26,214.68 | 26,094.87 - 26,312.99 | 3 |
| resistance | 28,028.83 | 27,923.73 - 28,133.94 | 2 |
| resistance | 28,276.58 | 28,170.55 - 28,382.62 | 2 |
| resistance | 28,712.51 | 28,604.83 - 28,820.18 | 2 |

| Trendline | P0 | P1 | Slope/day | At as-of | Touches | Valid |
|---|---|---|---|---|---|---|
| downtrend | 2020-03-13 @ 30,042.53 | 2020-11-16 @ 28,713.48 | -5.359 | 28,177.57 | 2 | yes |

JSON: /tmp/dow/json/DJI_SAMPLE_DJI_SAMPLE_2021-02-24_pct0.03.json
Chart: /tmp/dow/charts/DJI_SAMPLE_DJI_SAMPLE_2021-02-24_pct0.03.png
```

Reading: the fixture (synthetic, 300 bars from `../../../tests/fixtures/make_dji_sample.py`) closes at 27,084.67 on its last bar in a BEAR_PRIMARY state, so the one support zone lies below the close and the three resistance zones above it, nearest first (A8, 【agent-defined】). With no `--csv-pair` the same file serves as both legs, so the `confirmed` pair status is trivial (identical states) and the orange pair line overlays the primary close on the chart; pass a distinct `--csv-pair` for a real two-leg run. The downtrend line runs through the last two secondary highs and is valid: no close since 2020-03-13 exceeded it by more than the 1 percent tolerance (【agent-defined】). The PNG is about 150 kB; the test asserts it exceeds 10 kB and that `--no-chart` writes none.

### Example 2: ^DJI with ^DJT from ClickHouse since 2015, at an all-time high

```bash
python3 scripts/draw.py --symbol ^DJI --pair ^DJT --start 2015-01-01 --out-dir ../../../outputs/charts
```

Real output on 2026-11-08 (data through 2026-11-06, close 51,285.73), Levels section; the two file lines are printed as absolute paths and are shown here relative to this skill directory:

```text
| Type | Price | Zone | Touches |
|---|---|---|---|
| support | 41,850.96 | 41,694.01 - 42,007.90 | 2 |
| support | 38,140.95 | 37,997.92 - 38,283.97 | 2 |
| support | 37,690.35 | 37,549.01 - 37,831.69 | 2 |
| support | 34,008.91 | 33,843.92 - 34,160.78 | 3 |

Note: fewer than 2 swing highs on the upper side of the close; no zone reported

| Trendline | P0 | P1 | Slope/day | At as-of | Touches | Valid |
|---|---|---|---|---|---|---|
| uptrend | 2025-04-08 @ 37,645.59 | 2026-03-27 @ 45,166.64 | 21.306 | 49,939.21 | 2 | yes |

JSON: ../../../outputs/json/DJI_DJT_2026-11-06_pct0.03.json
Chart: ../../../outputs/charts/DJI_DJT_2026-11-06_pct0.03.png
```

Reading: the Industrials are BULL_PRIMARY since 2023-06-15 with a non-confirmation from the Transports (`dow-confirmation-and-line` Example 2). Four support zones sit below the close, the nearest two touches at about 41,851, the deepest three touches at about 34,009 (`R-047`, 【agent-defined】). No resistance zone exists because the index closed at a high above every prior swing high, which the `levels_note` states rather than reporting a zone below the price as the pre-A8 code did (spec review D7). The uptrend line joins the secondary lows of 2025-04-08 and 2026-03-27 (the second is also the defense line, 45,166.64, `dow-trend-classification`) and is valid at 49,939.21 on the as-of date, below the close. On the chart the line is the green diagonal from the 2025 low to the right edge, the defense line the short dashed red segment from 2026-03-27, the four green bands the zones, and the grey bands the 28-day-or-longer lines (【agent-defined】 presentation rule).

### Example 3: a historical `--as-of` run with resistance above the price

```bash
python3 scripts/draw.py --symbol ^DJI --pair ^DJT --start 2015-01-01 --as-of 2022-09-30 --out-dir /tmp/dow/charts
```

Real output (close 28,725.51 on 2022-09-30), abbreviated:

```text
| Primary trend | BEAR_PRIMARY since 2022-05-09 |
| Pair confirmation | non_confirmation (pair state -) |
| Defense line [agent-defined] | 34,152.01 (reaction_high, set 2022-08-16) - agent-defined, no literature source |

| Type | Price | Zone | Touches |
|---|---|---|---|
| support | 25,444.39 | 25,348.97 - 25,539.81 | 2 |
| support | 25,071.86 | 24,977.84 - 25,165.88 | 2 |
| support | 24,490.49 | 24,398.65 - 24,582.33 | 2 |
| support | 24,201.77 | 24,111.01 - 24,292.53 | 2 |
| resistance | 29,449.76 | 29,339.32 - 29,560.20 | 2 |
| resistance | 34,106.54 | 33,978.64 - 34,234.43 | 2 |
| resistance | 34,767.08 | 34,636.70 - 34,897.45 | 2 |
| resistance | 35,696.73 | 35,562.87 - 35,830.59 | 2 |

| Trendline | P0 | P1 | Slope/day | At as-of | Touches | Valid |
|---|---|---|---|---|---|---|
| downtrend | 2022-03-29 @ 35,294.19 | 2022-08-16 @ 34,152.01 | -8.158 | 33,784.88 | 2 | yes |

Chart: /tmp/dow/charts/DJI_DJT_2022-09-30_pct0.03.png
```

Reading: bars are cut at 2022-09-30, so only swings confirmed by then are used (no lookahead) and the file name carries that date. Both sides are populated (A8 side filter, 【agent-defined】; members recovered by matching the as-of minor swings against each zone's bounds, since the JSON twin does not serialise `Level.members`): the nearest resistance zone joins the swing highs of 2020-01-17 and 2020-02-12 near 29,450, the next the lower highs of 2022-05-04 and 2022-08-16 (the trendline anchor), then the 2021-05-07 with 2021-06-04 highs and the 2021-08-16 with 2022-02-09 highs; the two nearest support zones join the lows of 2019-08-14 with 2020-02-28 and of 2020-06-11 with 2020-06-26, the two deepest the 2018 lows (2018-03-02 with 2018-10-29, and 2018-06-27 with 2018-11-23). The downtrend line joins the lower highs of 2022-03-29 and 2022-08-16 (the second is also the defense line) and is valid; the Transports read BEAR_SUSPECT, hence the same-side non-confirmation (`dow-confirmation-and-line` Step 3).

## Boundaries

| Not covered here | Sibling skill |
|---|---|
| Glossary, Chinese term mapping, label definitions, what each source says, provenance, the defense-line negative result (`R-045`) | `dow-theory-sources` |
| Swing detectors, `minor_pct` / `secondary_pct` / `secondary_min_sessions`, `confirmed_idx`, which swings are minor or secondary | `dow-swing-detection` |
| State machine, HH/HL/LH/LL, `REVERSAL_*`, `DEFENSE_BREAK`, the defense line definition and refresh, warm-up, R1 and R2 results | `dow-trend-classification` |
| Pair confirmation status, cycle-aware matching, Dow line detection and breakouts, `LINE_BREAKOUT_*`, volume flag, R3, R6 and R7 results | `dow-confirmation-and-line` |
| Decision table, backtest runs, data-label authority, the SP_IYT robustness results | `dow-rule-backtest` |

Zone clustering, trendline fitting, chart rendering, the report layout, the file naming rule and `dow.str_level_log` are defined only here; siblings reference them. When a sibling is not installed, read `../../../docs/specs/algorithm_contract.md` (levels.py, chart.py, CLI, Deviations 8 and 12, A8) and `../../../research/canonical_rules.md` sections 1.8 and 6.

## Limitations

1. **Every zone and trendline parameter is agent-defined.** Tolerance, touch count, level cap, two-point fit, 1 percent validity and the 28-day shading floor are the project's choices (`R-047`, 【agent-defined】); the educators' conventions (`R-049` to `R-055`) give no width, count or tolerance, and no first-hand Dow source gives any drawing rule.
2. **No backtest of levels or trendlines.** Nothing here is 【data-confirmed】 or 【data-refuted】; it is 【insufficient-evidence】 by absence of a registered rule.
3. **Start-date dependence.** Zones are clustered from the swings inside the loaded window, so `--start` changes the zones; the trendline uses only the last two secondary swings and is less sensitive. Compare runs only at equal `--start`.
4. **Greedy clustering.** Joining by running mean can let a cluster spread beyond one tolerance, and two zones can sit a few hundred points apart (Example 2 at 38,141 and 37,690), 【agent-defined】 behaviour recorded in spec review row 13.
5. **Legibility over long ranges.** On a ten-year chart the `SUP xN` labels of adjacent zones overlap, the vertical signal labels cluster where reversals are dense (2020), the defense-line annotation can sit on the price line, and the dashed defense segment is short when the line was set recently. Fifteen-plus shaded line ranges add grey texture. Narrow `--start` or `--as-of` windows read better; nothing is fixed in the renderer here.
6. **Pair axis.** The pair close uses a separate right-hand scale; relative levels between the two series cannot be read off the chart. Zones and trendlines are drawn for the first symbol only.
7. **Linear, closes only.** `slope_per_day` is linear in calendar days, not log (`R-051`, 【single-source】, not implemented), and closes are used throughout; intraday extremes never touch a zone or a line.
8. **Indices unadjusted.** `^DJI` and `^DJT` are price indices without dividends or splits to adjust; ETF legs (`SPY`, `IYT`) are vendor-adjusted closes, so a zone on an ETF can shift when the vendor re-adjusts history.
9. **Lag by construction.** Zones use only swings confirmed by the as-of bar and the trendline's second anchor is confirmed later than it occurred, so a line or zone appears on the chart only after its confirmation bar (`dow-swing-detection` on `confirmed_idx`).
10. **Not advice.** The chart records where swings clustered and which line joins the last two secondary extremes. It draws no targets, makes no price prediction and gives no investment advice.

## Resources

- `scripts/draw.py`: the CLI wrapper (imports `analyze`, `to_markdown`, `render_chart`, `chart_filename`, `load_config`, `load_pairs`; no algorithm code). `scripts/_anchor.py`: project root and `.venv` resolution shared by skill scripts.
- `tests/test_cli.py`: runs the wrapper on the project CSV fixture (PNG exists and exceeds 10 kB in a temporary directory with the contract file name, JSON twin equals the printed document, `--no-chart` writes no PNG, the A8 side filter at the last bar and at `--as-of 2020-12-31`, defense line `agent_defined` true, one downtrend line, one support and three resistance zones, `--end` equal to `--as-of`, `--method atr` changing the swings and the file name, a distinct scaled `--csv-pair` as a real second leg, the plain stdout layout without `--json`, clean errors without `--symbol` and when `--csv` and `--source csv` are not given together) and a ClickHouse-gated ^DJI/^DJT run since 2015 (skipped when the container does not answer) asserting the four support zones of Example 2 with touches 2, 2, 2, 3, no resistance, the `levels_note`, the valid uptrend line through 2025-04-08 and 2026-03-27 and the defense line at 45,166.64. Run from the project root: `uv run --python .venv/bin/python pytest .claude/skills/dow-levels-and-chart -q`.
- `references/evidence.md`: every verbatim quote and rule id used here, grouped by Workflow step, with `slug:Qn` and URL.
- `../../../src/dowtheory/levels.py`: `cluster_levels`, `fit_trendlines`, `defense_line_from_state`. `../../../src/dowtheory/chart.py`: `render_chart`, `chart_filename`, `chart_title`, `MIN_LINE_DAYS_SHOWN`. `../../../src/dowtheory/report.py`: `to_markdown`. `../../../src/dowtheory/persist.py`: `level_frame`, `persist`. `../../../src/dowtheory/analysis.py`: how `analyze` feeds minor swings, the side filter and `levels_note`. `../../../src/dowtheory/cli.py`: `dow analyze` flags.
- `../../../docs/specs/algorithm_contract.md` (levels.py, chart.py, CLI, Deviations 8, 12, 13, Amendment A8) and `../../../docs/specs/skill_contract.md`.
- `../../../configs/dow.yaml` `levels:` section; `../../../configs/pairs.yaml`.
- `../../../reports/spec_review_p3.md`: rule-mapping row 13 (clustering) and defect D7 (resistance below price, fixed by A8). `../../../research/canonical_rules.md` section 1.8 (`R-047` to `R-056`) and section 6.
- `../../../tests/unit/test_levels.py`: library tests of clustering, the side filter and trendline validity.
