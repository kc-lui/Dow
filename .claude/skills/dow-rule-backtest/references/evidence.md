# Evidence for dow-rule-backtest

Every verbatim quote, rule id and figure used in `../SKILL.md`, grouped by Workflow step. Quotes are copied from `../../../../research/sources/<slug>.md` and carry their `(slug:Qn)` pointer; the URL is the note's recorded source. Label definitions are owned by `dow-theory-sources` (`../../../../research/canonical_rules.md` section 0). Project figures have no source note; their provenance is the file named in the row. The run of record is `a6d2d48e46014e7da3cc7c6be7ce8a02` (2026-11-08, pair DJ, specification `pct0.03/0.08f15`, 1992-01-02 to 2026-11-06, decision table sha256 `c8675eff2b281ac6f4fa8ed790063ecaf1e063d78f20fa9569ded1988be39836`, config hash `e6f5b9cd228e458809a42aa2a5c5e2811175de3d74fafca1a3496c6ac68ae24e`).

## Contents

1. Source URLs
2. Step 1: the protocol
3. Step 2: rules, metrics and registry mapping
4. Step 3: results table
5. Step 4: reading a label (caveats, exploratory rows, flags, coverage)
6. Steps 6 and 7: re-run, ledger, incidents
7. Examples
8. Rule ids cited

## 1. Source URLs

| Slug | Access | URL |
|---|---|---|
| brown-goetzmann-kumar-1998 | full-text, working-paper draft | https://chesler.us/about/about%20files/dow_theory.pdf |

Project files cited (no source note): `../../../../analysis/decision_table.md`, `../../../../analysis/decision_table.sha256`, `../../../../analysis/rule_status_table.md`, `../../../../analysis/protocol_deviations.md`, `../../../../reports/backtest_audit.md`, `../../../../reports/backtest_audit_replay.py`, `../../../../reports/rule_R1.md` to `rule_R8.md` and the `_SP_IYT` variants, `../../../../reports/backtest_run_20261108_063248.json`, `../../../../reports/backtest_run_20261108_062655.json`, `../../../../src/dowtheory/backtest/` (`protocol.py`, `labels.py`, `runner.py`, `rules.py`, `events.py`, `stats.py`, `README.md`), `../../../../src/dowtheory/cli.py`, `../../../../src/dowtheory/config.py` (`config_hash`), `../../../../db/init/01_schema.sql`, `../../../../scripts/migrate_rule_log_v2.py`, `../../../../configs/dow.yaml`, `../../../../configs/pairs.yaml`, `../../../../reports/spec_review_p3.md` (section 3b, the selection disclosed in protocol 1.8).

## 2. Step 1: the protocol

No source quotes. Every row of the Step 1 table paraphrases `../../../../analysis/decision_table.md`:

| Element | Section of the decision table | Related log entries |
|---|---|---|
| hash, scope marker, config hash pin | header, section 0 (config hash mechanism), section 6 | DEV-07 (whole-file hash is the column value), FIX-01 (scoped marker) |
| sample and frozen `period_end` | section 0 | `protocol.PERIOD_END` |
| family of 8, Holm once, missing p = 1 | 1.1, 3 (`holm_adjust`, `label_all`) | R11 section 1 reproduces p_holm by hand and with statsmodels |
| min n 30, two-sample 30 and 10, R8 trades | 1.3, R8 row (Minimum n) | DEV-03 (two-sample sub-sample n), DEV-08 (R8 sub-sample n) |
| sub-sample split 2009-12-31 / 2015-12-31, sign rule | 1.3 | DEV-01 (wording versus example; example followed; R1 signs unchanged under either) |
| label definitions | 1.4, 3 (`decide_label`) | DEV-06 (bound for non-proportion metrics: 0.99375 bootstrap quantile) |
| worst-grid-point rule | 1.8, 3 (`label_inputs`) | R11 section 5 |
| R1 drift-matched null, flag text | R1 row (Mandatory robustness) | DEV-10, R11 F1 and section 7 |
| R8 floor and random-spell null, flag text | R8 row | DEV-08 |
| no lookahead | 1.5 | R11 section 2 (8 cut dates, 127 of 128 comparisons identical, the one diff an open line window) |
| git timestamps (Limitation 6) | `protocol_deviations.md` header | `da6427c` 06:09 UTC holds decision_table.md with sha256 `c8675eff...` and a `.sha256` file still at v1 `d94a32e1...`; `3770aa1` 06:33 UTC updates the hash file; first label run 06:26 UTC (`backtest_run_20261108_062655.json`) |
| deviations, cap rule | 6 | `analysis/protocol_deviations.md` header |

## 3. Step 2: rules, metrics and registry mapping

Event, metric, null and test per rule: decision table section 2 (`### R1` to `### R8`) and the summary table of label-driving rows; implemented in `rules.py` and `events.py` as verified in R11 section 1. The registry-id mapping is `labels.RULE_ENTRIES`, recorded as DEV-02:

| protocol key | registry ids | registry labels | resolved literature label |
|---|---|---|---|
| trend_persistence | R-016, R-017 | consensus, consensus | literature-consensus |
| primary_reversal_signal | R-018, R-020 | disputed, consensus | literature-disputed |
| two_average_confirmation | R-032, R-033, R-034 | consensus x3 | literature-consensus |
| secondary_retracement | R-008, R-009, R-010, R-011 | disputed x4 | literature-disputed |
| secondary_duration | R-006, R-007 | disputed x2 | literature-disputed |
| line_breakout | R-022 to R-027 | consensus x6 (R-023, R-024 one lineage) | literature-consensus |
| volume_confirmation | R-037, R-038, R-041 | consensus, disputed, consensus | literature-disputed |
| hamilton_timing | R-062 | disputed | literature-disputed |

## 4. Step 3: results table

Copied from `../../../../analysis/rule_status_table.md` (label, n, effect, CI, p_holm, notes) with the sub-sample estimates, p_raw, worst-grid p-values and refutation bounds from the `## Result` block of each `../../../../reports/rule_R<n>.md`:

- R1: 33 events (29 successes), 0.8788, [0.7267, 0.9518], p_raw 0.000005, p_holm 0.000044, A 0.9412 (n 17), B 0.8125 (n 16), bound 0.9620; bull 0.8571 (n 21), bear 0.9167 (n 12); sweep 0.5935 to 0.8788; p_sim 0.0055, null mean 0.6906.
- R2: 12 events, 10 clusters, -0.0151, [-0.0456, 0.0206], p_raw 0.7736, A 0.0433 (n 3), B -0.0346 (n 9), bound 0.0343; hit rate 0.5; SP_IYT 0.0198 (n 8) gives pair-inconsistent.
- R3: 15 events (confirmed 12, single 3), 13 clusters, -0.0544, [-0.1385, 0.0308], p_raw 0.7901, A -0.0079 (n 5), B -0.0312 (n 10), bound 0.0457; all rows exploratory.
- R4 (backtest row): 44 events, 0.4091, [0.2769, 0.5559], p_raw 0.1816, worst-grid p 0.5105 at 0.06, A 0.3810 (n 21), B 0.4348 (n 23), bound 0.5940 vs 1/3; median ratio 0.6352; SP_IYT 0.3103 gives pair-inconsistent.
- R5: 44 events, 0.7273, [0.5815, 0.8365], p_raw 0.0018, worst-grid p 0.0443 at 0.05, p_holm 0.310191, A 0.7619 (n 21), B 0.6957 (n 23), bound 0.8585; no-filter variant 0.6739 (n 46); median 54.5 calendar days.
- R6: 87 events, 77 clusters, 0.4138, [0.3161, 0.5188], p_raw 0.9572, A 0.4250 (n 40), B 0.4043 (n 47), bound 0.5471; h60 0.5233, h120 0.5000; SP_IYT 0.5400 (n 50) gives pair-inconsistent.
- R7: 57 events (20 successes) from 2000-01-03, 0.3509, [0.2400, 0.4806], p_raw 0.9918, A 0.3600 (n 25), B 0.3438 (n 32), bound 0.5162; normalised 0.4211; `volume_confirms` share true 0.4058 over 69; sweep 0.2903 to 0.4739.
- R8 (backtest row): 28 trades, 0.1099, [-0.1827, 0.4336], p_raw 0.2464, A 0.1090 (n 12), B 0.0858 (n 16), bound 0.5070; backtest Sharpe 0.5693 vs 0.4594; annual log return 0.0481 vs 0.0797; volatility 0.0845 vs 0.1735; max drawdown -0.1640 vs -0.5378; time in market 0.4226; cumulative log-return difference -1.0993 [-2.4134, 0.5121], p 0.9245; p_spell 0.0245; calls 16 right, 8 wrong of 24; cost0 0.1196; long/short -0.1677 (48 trades).
- SP_IYT backtest rows (`rule_R<n>_SP_IYT.md`): 2004-01-02 to 2026-11-06, 5749 bars, split 2015-12-31, no labels; R1 0.8000 (n 20, p_sim 0.1314, flagged); R8 0.0168 (15 trades, p_spell 0.1154, flagged).

R11 verdicts: `../../../../reports/backtest_audit.md` section 8 (all eight endorsed; R1 with mandatory caveat).

## 5. Step 4: reading a label

| Point | Provenance |
|---|---|
| R1 mandatory caveat text (baseline 0.65 to 0.69; iid 0.654, zero drift 0.633, block 0.695; p_sim 0.0055 harness, about 0.0085 audit; n 33; never p_holm alone) | `rule_status_table.md` R1 notes; `rule_R1.md` section Mandatory caveat (R11 F1); `protocol.r1_caveat` via `runner.r1_caveat_for` (run-aware: the auditor baseline is quoted only when the run is the DJ reference run); `protocol_deviations.md` DEV-10; `backtest_audit.md` section 7 and F1 |
| borderline after Holm against the correct baseline; headline at the most favourable grid point; direction robust across the grid | `backtest_audit.md` sections 5 and 7 |
| meaning of insufficient-evidence; R6 0.547 and R7 0.516 bounds close to refuted | decision table 1.4; `backtest_audit.md` section 8 and recommendations |
| exploratory single groups; 3 of 12 reversals in both groups | `backtest_audit.md` F4 and section 5; `protocol_deviations.md` DEV-09, DEV-11; `protocol.EXPLORATORY_NOTE` |
| pair-inconsistent definition | decision table 1.6; status-table notes for R2, R4, R6 |
| coverage caveats and the volume correction | decision table section 5 (printed in every report); `protocol_deviations.md` Volume caveat correction; `backtest_audit.md` section 6 |
| BGK caveat wording (255 editorials, 110 right, 74 wrong, 71 neutral; mechanical state machine; descriptive, no label) | decision table R8 row (Explicit caveat); `protocol.BGK_CAVEAT`; printed in `rule_R8.md` |

Quote used in Step 4.6:

| Quote | Pointer | Supports |
|---|---|---|
| "In total, Hamilton was right 110 times and wrong 74 times, by our count." (brown-goetzmann-kumar-1998:Q23) | Sec. III.B, p.9 | `R-062` 【literature-disputed】; the 110/74 figure the BGK caveat refers to |

## 6. Steps 6 and 7: re-run, ledger, incidents

- Commands and flags: `../../../../src/dowtheory/cli.py` (`backtest` sub-parser), `../../../../src/dowtheory/backtest/README.md` (about 2 minutes with `--workers 8`), run JSON `runtime_s` 108.9 for the run of record; fixture timing from the Example 4 run (3.1 s).
- Determinism: decision table section 0 (seed 20261108 per rule, pair and specification); `protocol.SEED`.
- `config_hash`: `DowConfig.config_hash` in `../../../../src/dowtheory/config.py` (sha256 of the canonical JSON of the whole configuration); `run_backtest` in `runner.py` refuses a `DJ` run whose hash differs from the pinned value.
- Deviation procedure and cap: decision table section 6; `--deviation` flag in `cli.py`.
- Ledger: `../../../../db/init/01_schema.sql` (`str_rule_backtest_log`, ReplacingMergeTree, ORDER BY `(rule_id, pair, run_id, metric_name)`); `metric_name` convention and `notes` content: decision table 1.7, `runner.base_notes`, `_apply_labels`.
- INC-01 (run `b94022285206435e83b1c068eb123dc9`, 16 of 394 rows survived, `str_rule_backtest_log_v2`, `scripts/migrate_rule_log_v2.py`, identical rerun): `protocol_deviations.md` INC-01; `backtest_audit.md` F2 and section 4.
- FIX-01 (`table_scoped=3f6d676bcd4c` not a protocol hash; correct scoped hash `35de767a...`): `protocol_deviations.md` FIX-01; `backtest_audit.md` F3; `protocol.scoped_sha256`.
- FIX-02 (run start time; R7 `volume_confirms` row dates): `protocol_deviations.md` FIX-02.

## 7. Examples

- Example 1: `scripts/rules.py --rule R1` on the committed table and run JSON; the answer text restates `rule_R1.md` and `backtest_audit.md` section 7.
- Example 2: `scripts/rules.py --rule R7`; descriptive rows from `rule_R7.md`; the R-038 dispute lives in `dow-confirmation-and-line` Step 6.
- Example 3: figures from `rule_R8.md` (Strategy against buy-and-hold table, descriptive rows, calls). Quotes:

| Quote | Pointer | Supports |
|---|---|---|
| "normal trading frictions would preclude using the Theory to generate large excess returns" (brown-goetzmann-kumar-1998:Q41) | Sec. IV.E, pp.19-20 (sub-span) | `R-062` 【literature-disputed】; BGK's own friction caveat |

  Paraphrased, not quoted: BGK Sharpe 0.559 against 0.456 for `R-062` (brown-goetzmann-kumar-1998:Q30; quoted in full in `dow-theory-sources` Step 5).
- Example 4: `scripts/rules.py --rerun --out <DIR> --source csv --csv ../../../tests/fixtures/dji_sample.csv --no-sweeps` on 2026-11-08; the fixture is built by `../../../../tests/fixtures/make_dji_sample.py` (a synthetic sample of 300 backtest bars). The fixture caveat line (Baseline not simulated for this run, harness null mean 0.549, p_sim 0.5434, n = 1) is produced by `protocol.r1_caveat` with `reference=False`; the reference-run wording (n = 33, p_sim 0.0055) stays in `rule_status_table.md` and `rule_R1.md`.

## 8. Rule ids cited

| Rule | Key | Registry label | Where used |
|---|---|---|---|
| `R-006`, `R-007` | secondary duration min / max | disputed | Steps 2, 3; Example answers |
| `R-008` to `R-011` | secondary retracement lower / upper / base / binding | disputed | Steps 2, 3 |
| `R-016` | trend_definition_hh_hl | consensus | Steps 2, 3; Example 1 |
| `R-017` | trend_persists_until_reversal | consensus | Steps 2, 3; Example 1 |
| `R-018` | reversal_definition_swing_structure | disputed | Steps 2, 3 |
| `R-020` | reversal_hard_to_tell_from_secondary | consensus | Steps 2, 3 |
| `R-022` to `R-027` | line definition, band, duration, both averages, breakout meaning, break implies secondary | consensus (R-023, R-024 one lineage) | Steps 2, 3 |
| `R-032`, `R-033`, `R-034` | two-average confirmation, lag, pair | consensus | Steps 2, 3 |
| `R-037` | volume_with_primary_trend | consensus | Steps 2, 3; Example 2 |
| `R-038` | volume_in_secondary_reaction | disputed | Steps 2, 3; Example 2 |
| `R-041` | volume_secondary_to_price | consensus | Steps 2, 3; Example 2 |
| `R-045` | defense_line (owned by `dow-trend-classification`; not in the family) | agent-defined | Boundaries |
| `R-046` | swing_detection_thresholds (owned by `dow-swing-detection`) | agent-defined | Boundaries |
| `R-062` | beats_buy_and_hold | disputed | Steps 2, 3, 4; Example 3 |
