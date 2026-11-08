---
name: dow-rule-backtest
description: >-
  Data layer of the Dow project and the single authority for the data labels: what the
  pre-registered rule-level backtest (hashed decision table v2, Holm family of eight rules R1 to R8
  on ^DJI/^DJT 1992 to 2026) tested, how each label was decided, the results (n, estimate, CI, p_raw,
  p_holm, sub-sample signs, refutation bound), the R1 caveat, the exploratory
  R3/R6 rows, the SP_IYT robustness pair, and how to re-run with `dow backtest`. Use when asked
  whether a Dow Theory rule holds in the data, does it work, is it data-confirmed or
  insufficient-evidence or refuted, what the evidence, p-value or Sharpe is, whether the Hamilton
  timing strategy beats buy-and-hold, how to re-run or read the ledger, or 回測 / 驗證 / 勝率 /
  道氏理論 backtest. Not covered: glossary, labels, literature → dow-theory-sources; swings →
  dow-swing-detection; trend state, defense line → dow-trend-classification; lines, confirmation,
  volume flag → dow-confirmation-and-line; levels, trendlines, charts → dow-levels-and-chart.
---

# dow-rule-backtest: Pre-registered rule backtests and the data labels

> This skill is the data layer of the Dow project and the only owner of the data labels 【data-confirmed】【data-refuted】【insufficient-evidence】. Its knowledge comes from the frozen protocol `../../../analysis/decision_table.md` (v2, hashed in `../../../analysis/decision_table.sha256`), the harness `../../../src/dowtheory/backtest/` (`events.py`, `stats.py`, `rules.py`, `labels.py`, `runner.py`, `protocol.py`), the run of record `../../../reports/backtest_run_20261108_063248.json` with its reports `../../../reports/rule_R1.md` to `rule_R8.md` and the `_SP_IYT` variants, the status table `../../../analysis/rule_status_table.md`, the deviation log `../../../analysis/protocol_deviations.md` and the methodology audit `../../../reports/backtest_audit.md`. The label vocabulary and the rule ids `R-0xx` are defined in `dow-theory-sources` and only referenced here; the literature synthesis is `../../../research/canonical_rules.md`. Every quantitative statement carries exactly one literature label from 【literature-consensus】【literature-disputed】【single-source】【agent-defined】 and, where a backtest exists, one data label. Double quotes are reserved for verbatim source text with a `(slug:Qn)` pointer. A data label never asserts economic significance; the effect size and interval are always cited with it. The skill describes what the data say about trend rules as of the run date. It never predicts prices and it is not investment advice.

## When to Use

- Answer whether a Dow Theory rule holds in the data: find the rule's row, read its data label with its caveat, cite n, effect and interval, and place the literature label beside it.
- Explain how a label was decided (pre-registration, Holm family, minimum n, sub-sample signs, worst-grid rule, refutation bound) and what would change it.
- Report the Hamilton-style timing strategy against buy-and-hold with every caveat the protocol requires.
- Re-run the harness into a scratch directory, or read the ledger `dow.str_rule_backtest_log`.
- Say what 【insufficient-evidence】 means and does not mean for a given rule.

Do not use it to define the swing, trend, line or confirmation algorithms, to quote what the sources say, to draw charts, or to adjudicate a literature dispute. Those are sibling skills (see Boundaries).

## Prerequisites

1. **Project checkout and environment.** `scripts/rules.py` reads only the committed status table and run JSON, so it needs no database. `scripts/_anchor.py` finds the repo through `DOW_PROJECT_ROOT`, or by walking up to a directory holding `pyproject.toml` and `src/dowtheory`, and re-executes the script under `<root>/.venv/bin/python`. Global-install setup, one line:

   ```bash
   export DOW_PROJECT_ROOT=<path-to-Dow-repo>
   ```

2. **Files that must be readable.** `../../../analysis/rule_status_table.md` (the labels), the newest `../../../reports/backtest_run_*.json` (every row of both pairs), `../../../analysis/decision_table.md` and `.sha256` (the protocol and its hash), `../../../analysis/protocol_deviations.md` (DEV-01 to DEV-11, INC-01, FIX-01, FIX-02), `../../../reports/backtest_audit.md` (R11 verdicts F1 to F4).
3. **Re-running** needs ClickHouse (`trading_clickhouse` in Docker, `dow.mkt_klines` read with `FINAL`) and `.venv/bin/python scripts/check_integrity.py` exit 0 from the project root; the integrity report path is written into every row. A CSV pair (`--source csv --csv A --csv-pair B`) needs neither.
4. **Label discipline.** Labels come only from the `DJ` primary row of each rule through `decide_label`; humans do not override them. Siblings cite rows from this skill and never recompute them. Label definitions: `dow-theory-sources` Step 2.

## Workflow

**Step 1 - The protocol (what was fixed before the first run; 【agent-defined】 design choices)**

| Element | Pre-registered rule (`../../../analysis/decision_table.md`) |
|---|---|
| Pre-registration and hash | v2 written 2026-11-08, sha256 `c8675eff...9836` stored in `decision_table.sha256` and in every ledger row; the harness refuses to run when the stored hash matches neither the whole file nor the text above `PROTOCOL-HASH-SCOPE`; label-driving rows must also carry the committed `config_hash` `e6f5b9cd...ae24e` |
| Sample | pair `DJ` = ^DJI with ^DJT, closes, inner join on session, 1992-01-02 to a frozen `period_end` 2026-11-06, 8775 bars; `SP_IYT` (SPY, IYT, 2004 onward) is reported and never label-driving |
| Family and correction | exactly eight primary one-sided p-values, one per rule, Holm step-down once; rules below the n floor enter with p = 1 so the family stays eight; everything else (horizons, sweeps, SP_IYT, sub-samples, simulated nulls) is descriptive and never corrected |
| Minimum evidence | `backtest.min_n` 30 events for one-sample rules; 30 total and 10 per group for two-sample rules (R3); for R8 the n is the number of position changes |
| Sub-sample sign rule | split at 2009-12-31 for `DJ` (DEV-01 clarified the wording), 2015-12-31 for `SP_IYT`; both halves need 10 events and the sign of estimate minus null must agree in both for 【data-confirmed】 or 【data-refuted】 |
| Labels | 【data-confirmed】 = n ok, p_holm below 0.05 in the predicted direction, both sub-samples on the predicted side; 【data-refuted】 = n ok, the one-sided Bonferroni bound at level 1 minus 0.05/8 lies strictly on the wrong side of the null, both sub-samples on the wrong side; 【insufficient-evidence】 = everything else |
| Worst-grid-point rule (R4, R5) | the 8 percent secondary threshold (【agent-defined】) was chosen on this sample before the backtest after seeing the retracement band share and the Rhea duration share, so the family p-value and the refutation bound for R4 and R5 are the least favourable over `secondary_pct` 0.05, 0.06, 0.08, 0.10, 0.12 with the 15-session filter; it can only make a label harder |
| R1 simulated null | 2000 drift-matched stationary-block-bootstrap paths of ^DJI returns run through the same swing and trend code; `p_sim` is reported, and the flag `not-distinguishable-from-random-walk-with-drift` is set when it reaches 0.05 |
| R8 floor and spell null | fewer than 30 trades gives 【insufficient-evidence】; the random-spell null keeps the realised long and cash spell lengths and shuffles their order 2000 times; `p_spell` at or above 0.05 sets `not-distinguishable-from-random-timing` |
| No lookahead | event bars are `confirmed_idx`, `Signal.idx`, line `confirmed_ts` or the pair `confirmed_ts`; forward returns start at the bar after the event; R11 replayed eight cut dates with identical event sets |
| Deviations | any post-run change to an event, null, direction, horizon, test, alpha, min n, split, family, configuration or label algorithm is a `DEV-nn` with a new hash; a rule changed after its results were seen is `post-hoc-modified` and capped at 【insufficient-evidence】 |

**Step 2 - The eight rules as events, metrics and nulls (one row each; registry ids by DEV-02 mapping)**

| Rule | Event (knowable bar) | Metric and primary horizon | Null, direction, test | Registry ids |
|---|---|---|---|---|
| R1 trend_persistence | confirmed secondary swing counter to a `*_PRIMARY` state at its confirmation bar | `p_extend` = share whose next swing makes a new HH or LL (EQUAL counts as not extended) | 0.5, greater, exact binomial, Wilson CI; drift-matched null reported | `R-016`, `R-017` |
| R2 primary_reversal_signal | `REVERSAL_UP` / `REVERSAL_DOWN` on ^DJI at `Signal.idx` | signed mean excess log return over 60 sessions after the event; 20 and 120 descriptive | 0, greater, random-placement test, cluster bootstrap CI | `R-018`, `R-020` |
| R3 two_average_confirmation | ^DJI reversal matched cycle-aware by ^DJT (bar `confirmed_ts`) versus reversal unmatched by `c + h` | difference of the R2 metric, confirmed minus single, 60 sessions | 0, greater, permutation of group labels | `R-032`, `R-033`, `R-034` |
| R4 secondary_retracement | confirmed counter-trend secondary swing with a retrace ratio | `share_band` = share with one third to two thirds retracement | 1/3 (uniform ratio), greater, binomial; worst grid point | `R-008` to `R-011` |
| R5 secondary_duration | same events as R4 | `share_rhea` = share lasting 21 to 90 calendar days | 0.5, greater, binomial; worst grid point; no-filter variant printed | `R-006`, `R-007` |
| R6 line_breakout | line breakout confirmed by both averages at `confirmed_ts` | `agree_20` = share followed by a same-direction move over 20 sessions | 0.5, greater, binomial | `R-022` to `R-027` |
| R7 volume_confirmation | consecutive with-trend and counter-trend secondary legs in a PRIMARY state, legs from 2000-01-03 | `p_vol` = share where the with-trend leg has the higher mean volume | 0.5, greater, binomial | `R-037`, `R-038`, `R-041` |
| R8 hamilton_timing | long ^DJI when BULL_PRIMARY and pair-confirmed, else cash; next-close execution, 10 bps per side | `delta_sharpe` = annualised Sharpe of strategy minus buy-and-hold, daily log returns | 0, greater, joint stationary block bootstrap; spell null | `R-062` |

The literature label of a row is `literature-disputed` if any mapped registry id is disputed, else `literature-consensus` (DEV-02). It is independent of the data label and both are shown side by side.

**Step 3 - Results of the run of record (copied from `../../../analysis/rule_status_table.md`, run `a6d2d48e...`, pair `DJ`, spec `pct0.03/0.08f15`)**

| Rule | n | Estimate | Wilson or bootstrap interval | p_raw | p_holm | Sub-samples | Refutation bound vs null | Data label | Literature label (ids) |
|---|---|---|---|---|---|---|---|---|---|
| R1 trend_persistence | 33 | p_extend 0.8788 | 0.7267 to 0.9518 | 0.000005 | 0.000044 | A+ B+ (0.9412, 0.8125) | 0.9620 vs 0.5 | 【data-confirmed】 with the Step 4 caveat | literature-consensus (`R-016`, `R-017`) |
| R2 primary_reversal_signal | 12 | excess log return h60 -0.0151 | -0.0456 to 0.0206 | 0.7736 | 1.0 | A? B? (n 3 and 9) | 0.0343 vs 0 | 【insufficient-evidence】, n below minimum; pair-inconsistent | literature-disputed (`R-018`, `R-020`) |
| R3 two_average_confirmation | 15 (groups 12 and 3) | diff h60 -0.0544 | -0.1385 to 0.0308 | 0.7901 | 1.0 | A? B- | 0.0457 vs 0 | 【insufficient-evidence】, n below minimum; every row EXPLORATORY | literature-consensus (`R-032` to `R-034`) |
| R4 secondary_retracement | 44 | share_band 0.4091 | 0.2769 to 0.5559 | 0.1816 (worst grid 0.5105) | 1.0 | A+ B+ (0.3810, 0.4348) | 0.5940 vs 0.3333 | 【insufficient-evidence】; pair-inconsistent | literature-disputed (`R-008` to `R-011`) |
| R5 secondary_duration | 44 | share_rhea 0.7273 | 0.5815 to 0.8365 | 0.0018 (worst grid 0.0443) | 0.3102 | A+ B+ (0.7619, 0.6957) | 0.8585 vs 0.5 | 【insufficient-evidence】 | literature-disputed (`R-006`, `R-007`) |
| R6 line_breakout | 87 (77 clusters) | agree_20 0.4138 | 0.3161 to 0.5188 | 0.9572 | 1.0 | A- B- (0.4250, 0.4043) | 0.5471 vs 0.5 | 【insufficient-evidence】; pair-inconsistent | literature-consensus (`R-022` to `R-027`) |
| R7 volume_confirmation | 57 | p_vol 0.3509 | 0.2400 to 0.4806 | 0.9918 | 1.0 | A- B- (0.3600, 0.3438) | 0.5162 vs 0.5 | 【insufficient-evidence】 | literature-disputed (`R-037`, `R-038`, `R-041`) |
| R8 hamilton_timing | 28 trades | delta_sharpe 0.1099 | -0.1827 to 0.4336 | 0.2464 | 1.0 | A+ B+ (0.1090, 0.0858) | 0.5070 vs 0 | 【insufficient-evidence】, n below minimum | literature-disputed (`R-062`) |

Nothing is 【data-refuted】. R11 endorsed all eight labels (`../../../reports/backtest_audit.md` section 8).

**Step 4 - Read a label correctly**

1. **R1 mandatory caveat (R11 F1, DEV-10).** Every citation of R1 【data-confirmed】 must say: the pre-registered 0.5 null is not a random-walk baseline; a drift-matched random walk run through the same swing and trend machinery gives p_extend of about 0.65 to 0.69 (auditor: iid 0.654, zero drift 0.633, block bootstrap 0.695); the harness random-walk p is p_sim 0.0055 (null mean 0.6906) and the audit reproduces about 0.0085; n is 33. Cite the baseline, p_sim and n together; never p_holm alone. Against that baseline the raw evidence is near p 0.005 to 0.009 and would be borderline after Holm, so read R1 as: after an 8 percent rally off an unbroken reaction low, the index usually makes a new high within the same primary cycle, more often than a drift-matched random walk does, 【data-confirmed】 by the protocol as pre-registered. The headline sits at the most favourable grid point (sweep range 0.5935 to 0.8788); the direction holds at every `secondary_pct` point with n at or above 30.
2. **What 【insufficient-evidence】 means.** The algorithm could neither confirm nor refute: n below the floor (R2, R3, R8), or not significant after Holm, or sub-samples disagreeing. It does not mean the rule failed. The refutation bound shows how far from refuted: R6's upper bound 0.547 and R7's 0.516 lie above 0.5, so even with both sub-samples below the null the data do not exclude a zero effect; R11 notes both are close to a refuted outcome. R2's and R8's bounds are above 0 for the same reason.
3. **EXPLORATORY rows (R11 F4, DEV-11).** The R3 single group and the R6 `single` and `conf_minus_single` rows classify a reversal or breakout as unconfirmed using information up to `c + h`, the outcome window itself, and a reversal matched later than `c + h` sits in both R3 groups (3 of 12 ^DJI reversals, hence n 15). Every R3 row carries the note; cite none of them as evidence for or against the confirmation principle. Labels are unchanged; v3 should define single as not confirmed by `period_end`.
4. **pair-inconsistent.** Set when the `SP_IYT` primary estimate is on the other side of the null (R2 0.0198 against -0.0151; R4 0.3103 against 0.4091; R6 0.5400 against 0.4138). Descriptive only; the label does not move. `SP_IYT` rows carry no label, no p_holm and no refutation bound; its R1 (0.80, n 20, p_sim 0.1314) and R8 (0.0168, 15 trades, p_spell 0.1154) are both flagged not distinguishable from their random nulls.
5. **Coverage caveats printed with every report.** ^DJT history starts 1992-01-02, so nothing here tests 1897 to 1991; ^DJI volume is a vendor aggregate with level breaks in 2000 and 2016/2017 (the table's wording sparse or zero before 2000 is corrected in the deviation log), which is why R7 starts 2000-01-03; prices exclude dividends, which favours a strategy partly in cash (R8); forward windows overlap, so clusters are reported next to n.
6. **BGK comparison (R8).** The protocol's verbatim caveat says the 1992 to 2026 sample cannot replicate Brown, Goetzmann and Kumar's 1902 to 1929 reconstruction of Hamilton's 255 editorials, that the project's calls come from a mechanical state machine, and that any comparison with their 110 right and 74 wrong is descriptive and carries no label (`R-062`, 【literature-disputed】): "In total, Hamilton was right 110 times and wrong 74 times, by our count." (brown-goetzmann-kumar-1998:Q23). The project's descriptive analogue is 16 right and 8 wrong of 24 calls.

**Step 5 - Answer the question: does rule X hold in the data?**

1. Run `python3 scripts/rules.py --rule Rn` (or `--json`) and read the row; map a user's rule name to R1 to R8 through the Step 2 keys and registry ids.
2. State the data label first, with its reason, then n, the estimate, the interval and the null; for R1 add the caveat verbatim in substance; for R3 add EXPLORATORY; for R4 and R5 add the worst-grid rule and the mechanical caveat of the backtest reports (an 8 percent swing forces a high retrace ratio after a small leg; the 15-session filter, 【agent-defined】, enforces part of the Rhea floor, so the no-filter variant 0.6739 is printed next to the primary 0.7273).
3. Place the literature label beside it with its ids, and send the literature content to `dow-theory-sources`. A rule can be literature-disputed and data-confirmed, or consensus and insufficient; never merge the two layers.
4. Say what would change the label: more events (R2, R3, R8 need 30), a v3 protocol with a new hash (R1 simulated null, R3/R6 single definition), or a longer sample; never a re-run under the same protocol, which is deterministic.
5. Close with the limits: 1992 onward, one pair label-driving, frictions only in R8, not advice.

**Step 6 - Re-run (deterministic; never from a sibling)**

```bash
# from this skill directory; writes reports, run JSON and status table into DIR only
python3 scripts/rules.py --rerun --out <DIR>                       # ClickHouse, pair DJ, with sweeps
python3 scripts/rules.py --rerun --out <DIR> --pair DJ --pair SP_IYT
python3 scripts/rules.py --rerun --out <DIR> --source csv --csv <A.csv> --csv-pair <B.csv> --no-sweeps
# the underlying command (reports/ and analysis/rule_status_table.md are overwritten in place):
.venv/bin/dow backtest --pair DJ [--pair SP_IYT] [--persist] [--workers 8] [--out reports]
```

Runtime about 2 minutes for both pairs with sweeps (run of record 108.9 s); about 3 s on the 300-bar fixture with `--no-sweeps`. Every bootstrap, permutation and placement test is seeded with 20261108 per rule, pair and specification, so a re-run reproduces every number; only `run_id`, `started` and the file stamp change. The wrapper never passes `--persist`; persisting is a `dow backtest --persist` decision taken from the project root after `check_integrity.py` exits 0. `config_hash` is the sha256 of the whole `configs/dow.yaml` (swings, trend, line, confirmation, backtest sections); any edit changes it and the harness refuses a `DJ` run whose hash differs from the pinned value. Changing the decision table changes `decision_table_hash` and must follow Step 1's deviation procedure: append `DEV-nn` with before and after text, re-hash, reference the id in `--deviation DEV-nn`, keep every earlier row, and mark the status table row label computed under DEV-nn; a rule modified after its results were seen is capped at 【insufficient-evidence】.

**Step 7 - Read the ledger `dow.str_rule_backtest_log` (schema `../../../db/init/01_schema.sql`)**

- One row per rule, pair, run and metric; ReplacingMergeTree ordered by `(rule_id, pair, run_id, metric_name)`; read with `FINAL`. `metric_name` is `<spec>|<variant>|<metric>|<horizon>`, for example `pct0.03/0.08f15|primary|p_extend|na`; the label-driving row is `DJ`, spec `pct0.03/0.08f15`, variant `primary`; every other row has `label` `n/a`.
- `p_value` is the raw one-sided value; `p_holm`, `refute_bound`, `p_sim`, `p_spell`, cluster counts, deviation ids, `integrity=` and `table_scoped=` live in `notes`. `decision_table_hash` must equal line 1 of `decision_table.sha256` current at `inserted_at`; `config_hash` must equal the pinned value.
- **INC-01.** The first persisted run `b9402228...` (06:27 UTC) lost 378 of 394 rows because the sorting key was `(rule_id, pair, run_id)` and merges collapsed every metric of a rule into one row; the 16 survivors are in `str_rule_backtest_log_v2` after `scripts/migrate_rule_log_v2.py`. The rerun `a6d2d48e...` on the same code and data gave identical labels and estimates and is the run of record (394 rows). A bug fix, not a protocol deviation.
- **FIX-01.** `table_scoped=3f6d676bcd4c` in both runs' notes is not a protocol hash: the scoped-hash helper matched the prose mention of the marker and hashed four lines. The whole-file hash protected both runs and matched. The helper now anchors on the marker line and reproduces `35de767a...`.

## Output

`scripts/rules.py` prints a header line (run id, table file, decision table hash prefix, config hash prefix) and one block per requested rule and pair: rule id and key, pair, specification and period; data label and literature label with ids; n, metric, estimate, interval, null, p_raw, p_holm; sub-sample signs and the refutation bound with its reading; the label reason; EXPLORATORY where DEV-11 applies; flags (`pair-inconsistent`, random-null flags, `post-hoc-modified`); the R1 caveat text when present. With `--json` one document: `{"run_id", "table", "decision_table_hash", "run_table_hash", "config_hash", "rules": [{"rule_id", "rule_key", "pair", "spec", "period", "data_label", "literature_label", "literature_ids", "n", "metric_name", "horizon", "estimate", "ci", "null_value", "p_raw", "p_holm", "subsample_signs", "refute_bound", "reason", "caveat", "flags", "exploratory", "notes"}]}`. `--rerun` prints the exact `dow backtest` command, the harness log and the written paths. In prose, give label, reason, n, effect, interval, caveat, literature label and what would change the label.

## Examples

### Example 1: does trend persistence hold? (R1)

```bash
python3 scripts/rules.py --rule R1
```

Real output (header omitted):

```text
R1 trend_persistence | pair DJ | spec pct0.03/0.08f15 | 1992-01-02..2026-11-06
  data label: data-confirmed | literature label: literature-consensus (R-016,R-017)
  n=33  p_extend na = 0.8788  95% CI [0.7267, 0.9518]  null 0.5000  p_raw=0.0000  p_holm=0.000044
  sub-samples A+ B+ | refutation bound 0.9620 vs null 0.5000 -> not refuted
  reason: p_holm<alpha, sub-samples agree
  caveat: Mandatory caveat for any citation of R1 `data-confirmed` (R11 audit F1): the 0.5 null is not a random-walk baseline. [...] The harness random-walk p is p_sim = 0.0055. Cite the baseline 0.65 to 0.69, p_sim and n = 33; never p_holm alone.
```

Answer: 【data-confirmed】 by the pre-registered protocol: in 29 of 33 counter-trend secondary swings since 1992 the next swing made a new extreme (p_extend 0.8788, CI 0.7267 to 0.9518, both halves above 0.5). Mandatory caveat: the 0.5 null is not a random-walk baseline; a drift-matched random walk through the same machinery gives about 0.65 to 0.69, the random-walk p is p_sim 0.0055 on n 33, and the headline sits at the most favourable grid point. Literature: `R-016`, `R-017`, 【literature-consensus】 that a trend persists until a reversal is signalled. What would change it: a v3 protocol that pre-registers the simulated null (DEV-10), under which the evidence would be borderline, not overwhelming.

### Example 2: does volume confirm the trend? (R7)

```text
R7 volume_confirmation | pair DJ | spec pct0.03/0.08f15 | 2000-01-03..2026-11-06
  data label: insufficient-evidence | literature label: literature-disputed (R-037,R-038,R-041)
  n=57  p_vol na = 0.3509  95% CI [0.2400, 0.4806]  null 0.5000  p_raw=0.9918  p_holm=1.000000
  sub-samples A- B- | refutation bound 0.5162 vs null 0.5000 -> not refuted
  reason: not significant after Holm, or sub-samples disagree
```

Answer: 【insufficient-evidence】, not refuted. In 20 of 57 with-trend versus counter-trend leg pairs since 2000 the with-trend leg carried the heavier mean volume (p_vol 0.3509, CI 0.2400 to 0.4806); both sub-samples sit below 0.5, but the refutation bound 0.5162 does not fall below the null, so the protocol cannot call it refuted. The trailing-median normalised variant gives 0.4211 and the `volume_confirms` flag was true in 0.4058 of 69 windows; the 15-point sweep stays between 0.2903 and 0.4739. Literature: `R-037` consensus that volume goes with the trend, `R-038` 【literature-disputed】 on reaction volume (Hamilton against the educators, side by side in `dow-confirmation-and-line` Step 6), `R-041` that volume is collateral. R11 notes the bound is close to a refuted outcome; a longer sample under this table would not change the label mechanism.

### Example 3: is the Hamilton timing strategy profitable? (R8)

Answer: 【insufficient-evidence】, because the long/cash strategy made 28 position changes and the floor is 30 (`R-062`, 【literature-disputed】). Descriptive figures from `../../../reports/rule_R8.md` for this backtest: annualised Sharpe 0.5693 against 0.4594 for buy-and-hold (delta 0.1099, CI -0.1827 to 0.4336, p_raw 0.2464); annual log return 0.0481 against 0.0797, so the cumulative log-return difference of the backtest is -1.0993 (CI -2.4134 to 0.5121) with 42 percent time in market, annual volatility 0.0845 against 0.1735 and maximum drawdown -0.164 against -0.538; p_spell 0.0245; 16 right and 8 wrong of 24 calls; the long/short variant has delta -0.1677 over 48 trades; costs at 0 bps give 0.1196. Read: lower return, much lower risk, a Sharpe gap the bootstrap cannot distinguish from zero, and a price-index benchmark that favours the strategy because dividends are excluded. The BGK result for `R-062` (Sharpe 0.559 against 0.456, "normal trading frictions would preclude using the Theory to generate large excess returns" (brown-goetzmann-kumar-1998:Q41)) is a different century, different method and carries no label here.

### Example 4: re-run into a scratch directory on the CSV fixture

```bash
python3 scripts/rules.py --rerun --out <DIR> --source csv --csv ../../../tests/fixtures/dji_sample.csv --no-sweeps
python3 scripts/rules.py --rule R1 --table <DIR>/rule_status_table.md --run <DIR>/backtest_run_<stamp>.json
```

Real output, abbreviated (the fixture is a synthetic 300-bar sample, so every rule is below the floor):

```text
running: <root>/.venv/bin/dow backtest --out <DIR> --status-table <DIR>/rule_status_table.md --source csv --pair DJ --csv <root>/tests/fixtures/dji_sample.csv --no-sweeps
INFO dowtheory.backtest.runner: pair DJ: 300 bars 2020-01-02..2021-02-24
wrote <DIR>/rule_R1.md ... wrote <DIR>/rule_R8.md
wrote <DIR>/backtest_run_20261108_082330.json
wrote <DIR>/rule_status_table.md
runtime 3.1s

R1 trend_persistence | pair DJ | spec pct0.03/0.08f15 | 2020-01-02..2021-02-24
  data label: insufficient-evidence | literature label: literature-consensus (R-016,R-017)
  n=1  p_extend na = 1.0000  95% CI [0.2065, 1.0000]  null 0.5000  p_raw=0.5000  p_holm=1.000000
  reason: n below minimum
  flags: not-distinguishable-from-random-walk-with-drift
```

Reading: the committed `analysis/rule_status_table.md` and `reports/` are untouched (the wrapper always passes `--status-table` inside `--out`); the decision table hash in the scratch table equals the committed one, so the protocol was unchanged; the fixture run is a smoke test of the pipeline, not evidence. The caveat text printed by the harness is a fixed sentence apart from `p_sim`, so on a fixture it still says n = 33; read n from the row.

## Boundaries

| Not covered here | Sibling skill |
|---|---|
| Label vocabulary and definitions, `R-0xx` reading, what the sources say, Cowles and BGK and Schannep evidence, glossary and Chinese terms | `dow-theory-sources` |
| Swing methods, `confirmed_idx`, the 3 percent, 8 percent and 15-session parameters (【agent-defined】, `R-046`) | `dow-swing-detection` |
| State machine, `REVERSAL_*`, SUSPECT, the Dow defense line (`R-045`, not in the family, never labelled) | `dow-trend-classification` |
| `pair_confirm`, cycle-aware matching, `detect_lines`, `volume_confirms` mechanics and the R-038 dispute | `dow-confirmation-and-line` |
| Support and resistance, trendlines, charts (no backtest rule tests them) | `dow-levels-and-chart` |

Labels, protocol, results, re-run and ledger reading are defined only here; siblings quote rows from Step 3 and point back.

## Limitations

1. **Post-hoc threshold choice.** The 8 percent and 15-session specification (【agent-defined】) was selected on this sample before the backtest protocol was written, so the worst-grid rule protects R4 and R5 only, and R1's headline is at the most favourable point (Step 4.1).
2. **1992 onward, one pair.** No label covers 1897 to 1991 or any index other than ^DJI with ^DJT; `SP_IYT` starts 2004 and is descriptive. Reversal counts are tiny (12 on ^DJI), so R2, R3 and R8 are structurally 【insufficient-evidence】 under this table.
3. **Frictions and benchmark.** Only R8 charges costs (10 bps per side, cash earns zero, next-close execution); its benchmark is a price index without dividends, which favours the strategy. No slippage, taxes or borrowing (long/short variant) are modelled.
4. **R1 null mis-specified** (Step 4.1): the label follows the pre-registered 0.5 null; the mechanical baseline is 0.65 to 0.69.
5. **Exploratory group definitions** (DEV-11) make every confirmed-versus-single comparison unusable as evidence until v3.
6. **Governance gaps recorded by R11.** The table and the first runs entered git in one commit, so pre-registration is internally consistent but has no external timestamp; INC-01 collapsed the first ledger run; the scoped marker bug FIX-01 left a wrong `table_scoped` in both runs' notes. Protection rested on the whole-file hash, which matched.
7. **Volume caveat wording.** The frozen table says sparse or zero before 2000; the data show level breaks instead; the 2000 start stands as pre-registered.
8. **Overlapping windows** at the 60-session and 120-session backtest horizons shrink effective n; only the cluster bootstrap adjusts for it.
9. **Not advice.** A label describes how a mechanical rule behaved on past closes. It is not a forecast and not investment advice.

## Resources

- `scripts/rules.py`: the CLI wrapper (reads the status table and run JSON; `--rerun` shells to `dow backtest` without `--persist`; no statistics). `scripts/_rows.py`: parsing and formatting only. `scripts/_anchor.py`: project root and `.venv` resolution shared by skill scripts.
- `tests/test_cli.py`: all eight rules print with labels and ids and the R1 caveat with `p_sim`; R7 insufficient with bound 0.5162; R3 exploratory and R6 bound; JSON keys and label agreement between table and run JSON; `SP_IYT` rows unlabelled; status-table hash equals line 1 of `decision_table.sha256` and the sha256 of the table on disk; `--rerun` without `--out` errors; a CSV-fixture rerun into `tmp_path` leaves the committed table and reports untouched and yields eight below-floor rows. Run from the project root: `uv run --python .venv/bin/python pytest .claude/skills/dow-rule-backtest -q`.
- `references/evidence.md`: the quotes, rule ids and every figure's file of origin, grouped by Workflow step.
- `../../../analysis/decision_table.md`, `decision_table.sha256`, `rule_status_table.md`, `protocol_deviations.md`; `../../../reports/backtest_audit.md`, `backtest_audit_replay.py`, `rule_R1.md` to `rule_R8.md` and `_SP_IYT`, `backtest_run_20261108_063248.json` (run of record) and `backtest_run_20261108_062655.json` (INC-01 survivor).
- `../../../src/dowtheory/backtest/README.md` and modules; `../../../src/dowtheory/cli.py` (`backtest` flags: `--pair`, `--persist`, `--out`, `--status-table`, `--source`, `--csv`, `--csv-pair`, `--no-sweeps`, `--workers`, `--deviation`); `../../../db/init/01_schema.sql`; `../../../scripts/migrate_rule_log_v2.py`; `../../../configs/dow.yaml` `backtest:` section.
- `../../../research/canonical_rules.md` section 5 (performance evidence) and the registry rows mapped in `labels.py` `RULE_ENTRIES`; `../../../docs/specs/skill_contract.md`.
