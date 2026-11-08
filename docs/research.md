# Research notes: distilling Dow Theory into an agent and skills

This document records the method decisions, measured results, review history and open issues of the Dow project. It is written for the next team that distils a public literature into skills with executable checks. Every number cites the file it came from. Paths are relative to the repository root.

Sister projects: `../HD/README.md` (private LINE group, eight skills) and `../HD/docs/research.md`.

## 1. Architecture decisions

| Question | HD (private corpus) | Dow (public literature) | Why |
|---|---|---|---|
| Source of trust | Private third party; claims checked against price windows | Published books, papers and educators | `docs/team_design.md`, section "Three differences from HD"; `../HD/README.md` |
| Evidence labels | Claim status from a claim registry and price windows | Two layers: literature (consensus, disputed, single-source, agent-defined) and data (data-confirmed, data-refuted, insufficient-evidence) | `CLAUDE.md`, "Status labels"; `../HD/README.md`, 驗證與統計 section |
| Executable content | Knowledge-only skills | Skills carry scripts; `src/dowtheory/` is the only algorithm home, scripts are thin wrappers | `CLAUDE.md`, "Algorithms live only in src/dowtheory/"; `docs/specs/skill_contract.md`, item 7 |
| Skill count | Eight | Six, merged from an earlier plan | `docs/team_design.md`, section 5 |
| Data store | JSONL files under `data/` | One ClickHouse database per product, `dow` | `db/README.md`, "Write scope"; `../HD/README.md`, 目錄結構 section |
| Review weights | 0.35 and 0.65 for all skills | 0.5 and 0.5 for script skills; 0.35 and 0.65 only for the knowledge-only skill | `CLAUDE.md`, "Skills are generated one at a time" |

The Dow project added three things HD did not need. It added rule-level backtests with a pre-registered protocol (`analysis/decision_table.md`). It added an independent methodology audit (`reports/backtest_audit.md`). It added a boundary ledger to keep skills from repeating each other (`analysis/skill_boundary_ledger.md`).

## 2. Literature pipeline

### 2.1 Source notes

`research/sources/` holds 42 files. The registry header still says 43 (`research/canonical_rules.md`, line 3). The count dropped when the academic search log moved out of the folder (git commit `a4f20cd`). One of the 42 files, `research/sources/zh-defense-line-search-log.md`, is a search log and not a source note.

| Access level | Count | Type | Count |
|---|---|---|---|
| full-text | 5 | educator | 28 |
| partial | 32 | primary | 4 |
| search-snippet | 5 | academic | 5 |
| | | textbook | 3 |
| | | encyclopedia | 2 |

Full-text notes: Hamilton 1922, Nelson 1903, Brown-Goetzmann-Kumar 1998, Cowles 1933 and Russell's history. Primary-source notes (Hamilton, Nelson, Dow's editorials and Rhea) are classified by type in each note's header. Rhea's note is classified primary but was read second-hand through a publisher excerpt and two articles (`research/sources/rhea-1932-the-dow-theory.md`, line 8).

### 2.2 Quote audit

| Verdict | Count |
|---|---|
| Verbatim | 504 |
| Minor difference | 16 |
| Misquote (fixed) | 1 |
| Not found at the cited URL | 5 |
| Page unreachable | 4 |
| Total | 530 |

Source: `reports/quote_audit_p1.md`, section 2. The audit's overall rate is 95.1 percent verbatim. The minor differences are truncations, a swapped word order, and inserted footnote markers. The audit lists the fixes it recommends. The git log records "minor quote corrections" (commit `a4f20cd`), but this pass did not re-check every listed fix.

### 2.3 Canonical registry

`research/canonical_rules.md` holds 65 rules, R-001 to R-065, in section 1. Labels: 27 literature-consensus, 16 literature-disputed, 3 agent-defined and 19 single-source. The git log recorded 62 rules in the first draft (`1b34640`) and 65 in the second (`8651634`).

### 2.4 Disputes, side by side

The 16 disputed rows are listed here with their ids. The registry shows the positions and does not adjudicate them (`research/canonical_rules.md`, section 1).

| Id | Dispute |
|---|---|
| R-002 | Minimum length of a primary movement: 4 years, 1 year, under 1 year, or months |
| R-003 | Upper typical length of a primary movement: Dow's 4 to 6 years against Hamilton's rejection |
| R-006 | Minimum length of a secondary reaction: none, 8 trading days, about 10 days, 15 days, 20 days, or 3 weeks |
| R-007 | Upper length of a secondary reaction: about a month, 60 days, 3 months, 12 weeks, several months, or no limit |
| R-008 | Lower retracement bound: 3/8 (Dow, for stocks), 1/3 (Rhea and others), about 1/2, or none |
| R-009 | Upper retracement bound: 2/3, 1/2, or unbounded |
| R-010 | Retracement base: change since the last secondary ended, or the preceding primary swing |
| R-011 | Whether a retracement is required: required, guide only, replaced by 3 percent, or no limit |
| R-014 | Length of a minor movement: daily to a month or more |
| R-018 | Reversal rule: orthodox swing structure against Russell and Schaefer |
| R-038 | Volume during reactions: rises against dries up |
| R-043 | Bull phase names: Rhea's scheme against the modern scheme |
| R-044 | Bear phase names: Rhea's scheme against the modern scheme |
| R-056 | Sperandeo's 1-2-3 reversal steps 2 and 3 |
| R-061 | Value of double tops and bottoms |
| R-062 | Whether Dow Theory beats buy-and-hold: no edge, risk-adjusted edge, or 1 to 2 percent a year |

### 2.5 Defense line: negative result

No source defines or names the Dow defense line. The search used eight queries, five standard and three extended, and about 40 fetched pages. Nothing used the term as Dow Theory vocabulary (`research/canonical_rules.md`, section 6; `research/sources/zh-defense-line-search-log.md`). The search tool is US-only, so the result means "not found", not "does not exist". The first-hand notes for Hamilton, Nelson, Dow's editorials, Rhea, Edwards-Magee, Kirkpatrick-Dahlquist and Russell record the defense line as not mentioned (`research/canonical_rules.md`, section 6). The project therefore labels it agent-defined (R-045).

### 2.6 Primary-source verification outcomes

- **Misquote in the first Hamilton note.** The source reads "the weather", and the first note had "atmospheric pressure". The `-v2` note fixes it (`reports/quote_audit_p1.md`, section 2).
- **Misquote in the first Dow editorial note.** The first note gave the 1901 editorial as "3/8". The Bishop PDF reads "¼ to ½ of the primary move". The note was replaced (`reports/quote_audit_p1.md`, section 2).
- **Hamilton has no phase schema.** The phase schema is Rhea's. Hamilton's 1922 text has none (R-042 in `research/canonical_rules.md`).
- **"Not infallible" is Rhea's phrase.** Hamilton writes that the barometer is "not perfect" (`research/canonical_rules.md`, section 3, and R-060).
- **Two-average confirmation has a disputed origin.** Hamilton first defined it. One educator, thismatter, credits Dow (R-032 and `research/canonical_rules.md`, section 3).
- **The 3 percent filter is Rhea's, not Hamilton's.** The contract key `hamilton_3pct_filter` was renamed to `rhea_3pct_filter` (`docs/specs/algorithm_contract.md`, amendment A9; R-013).
- **Cowles is 1933, not 1934.** Brown-Goetzmann-Kumar cite 1934. The correct year is 1933 (`research/canonical_rules.md`, section 5).
- **Brown-Goetzmann-Kumar figure mismatch.** The text says 9.95 percent and the table says 10.73 percent (`research/canonical_rules.md`, section 5).
- **Editorial count mismatch.** Russell says Hamilton wrote 252 editorials. Cowles and Brown-Goetzmann-Kumar say 255 (`research/canonical_rules.md`, section 5).

### 2.7 Dow's own figures

| Figure | Date | Source |
|---|---|---|
| Three movements run at the same time | December 1900 | `research/canonical_rules.md`, section 3, row "Three movements" |
| Primary movement 4 to 6 years | 4 January 1902 | `research/canonical_rules.md`, section 3, row "Primary 4 to 6 years"; R-002, R-003 |
| Secondary: "ten days to sixty days, averaging thirty to forty" | 4 January 1902 | `research/canonical_rules.md`, section 3 |
| Secondary: "two weeks to a month or more" | December 1900 | `research/canonical_rules.md`, section 3 |
| At least three-eighths retracement, for stocks | 20 July 1901 | R-008 |
| Line range of 2 points for a stock | | R-023 |
| Trend: highs for a bull, lows for a bear | 4 January 1902 | R-016 |

Nelson's 1903 text and Hamilton's 1922 text carry the figures in full (`research/sources/nelson-1903-abc-of-stock-speculation.md`, `research/sources/hamilton-1922-stock-market-barometer.md`). The dates come from Hamilton and from Schannep, because Nelson prints none (`research/sources/dow-editorials-wsj-1900-1902.md`, line 8).

### 2.8 Performance evidence

| Study | Result | Source |
|---|---|---|
| Cowles (1933) | Hamilton earned 12 percent a year against 15.5 percent for buy-and-hold on industrials. 90 changes of position: 45 successful, 45 not. | `research/canonical_rules.md`, section 5 |
| Brown-Goetzmann-Kumar (1998) | 255 editorials, 110 right and 74 wrong. Event study p = 0.034. | `research/canonical_rules.md`, section 5 |
| Schannep and Blay | 1 to 2 percent a year over buy-and-hold, unsourced. Promotional. | `research/canonical_rules.md`, section 5 |
| Sideris | Figures conflict across auto-summaries. Do not cite. | `research/canonical_rules.md`, section 5 |
| Post-1998 search | No peer-reviewed or working-paper test of the confirmation rule was found. | `research/academic-search-log.md` |

## 3. Data layer

### 3.1 Schema

Six tables live in ClickHouse database `dow` (`db/README.md`, section "Tables"; DDL in `db/init/01_schema.sql`):

- `mkt_klines`: daily bars, partitioned by year of `ts_open`.
- `str_swing_log`, `str_trend_state_snapshots`, `str_level_log`: analysis output, written only with `--persist`.
- `str_rule_backtest_log`: the evidence ledger. Its sort key was corrected to include `metric_name` (`db/README.md`, "Migrations").
- `ops_data_quality_log`: MergeTree, grouped by run and never deduplicated.

Prices use `Decimal(12, 4)`. The write-scope rules are in `db/README.md`, "Write scope", and `src/dowtheory/storage/sql_guard.py`.

### 3.2 Review findings and fixes

The P2 code review (`reports/code_review_p2.md`) found one critical, four high, seven medium and eight low findings. The commit that answered them lists these fixes (commit `a9fc82d`): scoped `dow_user` and an SQL allowlist guard (C1), MergeTree quality log with `run_id` (H1), a flat-bar check and `analysis_start` clipping (H2), per-symbol fetch isolation (H3), duplicate and exchange conflict checks (H4), and yearly partitions (M4).

| Finding | Status |
|---|---|
| C1 write scope, H1 log deduplication, H2 close-only bars, H3 batch abort, H4 duplicate checks, M4 partitions | Listed as fixed in `a9fc82d` |
| M1 silent coercion, M2 structural checks, M3 vacuous gate, M5 test residue, M6 config types, M7 source conflicts, L1 to L7 | Not listed in that commit. Status not verified in this pass. |
| L8 lint error PYI041 in `src/dowtheory/levels.py` | Status not verified in this pass |

Test counts recorded in commit messages and reports: 27 (P2 review, `reports/code_review_p2.md`), 117 (P3 spec review, `reports/spec_review_p3.md`), 176 (`a9fc82d`), 204 (`ca7a284`), 233 (`da6427c`), 290 (`3770aa1`, `reports/backtest_audit.md`), and 297 (`77816e3`).

### 3.3 Integrity

The latest saved integrity report (`reports/integrity_20261108_142118.txt`) shows `errors=0 warnings=7 info=14` and `STATUS PASS`. The warnings are close-only flat bars in `^GSPC`, `^IXIC` and `IYT`, zero-volume bars, and a 7-session gap in `^GSPC` in March 1933. The integrity report counts 8,547 flat `^GSPC` bars in total, 38 of them on or after the 1962 analysis start. It counts 3,459 flat `^IXIC` bars in total, 2 of them on or after the 1984 analysis start (`reports/integrity_20261108_142118.txt`).

### 3.4 Volume caveat

Two documents say index volume is absent or sparse. `research/canonical_rules.md`, section 7, says the `^DJI` and `^DJT` series "carry no volume". The protocol says index volume is "sparse or zero before 2000" (`analysis/decision_table.md`, section 5). The audit found that `^DJI` volume is positive on every bar since 1992. It found level breaks in 2000 and in 2016 to 2017 instead: annual mean 21 to 99 million shares in 1992 to 1999, against about 205 million in 2000, and about 117 million before and 311 million after the 2016 to 2017 break (`reports/backtest_audit.md`, section 6; `analysis/protocol_deviations.md`, "Volume caveat correction"). The chart's volume panel shows the same break (`outputs/charts/DJI_DJT_2026-11-06_pct0.03.png`). Section 7 of the registry is stale and should be corrected.

## 4. Algorithms

### 4.1 Contract

The algorithm contract was frozen in commit `c0b9613` ("P3 prep: freeze algorithm contract") and covers `Swing`, the state machine, the JSON schema, the chart and the CLI (`docs/specs/algorithm_contract.md`). Deviations 1 to 17 record implementation choices made while coding. Amendments A1 to A9 changed the contract after the spec review (`docs/specs/algorithm_contract.md`, "Amendments after R8 spec review").

### 4.2 Spec review and look-ahead replay

The spec review (`reports/spec_review_p3.md`, commit reviewed `1272b99`) mapped 14 Dow rules to code. It ranked 16 defects: three high (D1 signal confirmation, D2 line confirmation, D3 strict-mode deadlock), six medium, and seven low.

The look-ahead replay re-ran the pipeline on truncated data and compared results (`reports/spec_review_p3.md`, section 2):

| Item | Bars or objects tested | Result |
|---|---|---|
| Percent swing confirmation | 438 bars (`^DJI`), 565 bars (`^DJT`) | PASS, 0 mismatches |
| ATR swing confirmation | 462 bars | PASS |
| Pivot confirmation | 887 bars | PASS |
| Trend state, defense line and signals | 390 bars (`^DJI`), 451 bars (`^DJT`) | PASS |
| Line geometry and breakout bar | 299 lines | PASS |
| Line `confirmed_both` | 299 lines | FAIL: 104 lines change at their breakout bar |
| Per-signal pair confirmation | All three `^DJI` reversals since 2015 | FAIL: unconfirmed at their own date |

### 4.3 Amendments A1 to A9 and why

| Amendment | Change | Defect it answers |
|---|---|---|
| A1 | Secondary threshold 8 percent, plus a 15-session causal filter | Secondary swings were mostly primary legs at 10 percent (D8, `reports/spec_review_p3.md`, section 3b) |
| A2 | Equal-extreme tolerance 0.5 percent | The 2016-04-14 reversal was missed (D3) |
| A3 | No deadlock in strict mode | SUSPECT states stalled for 597 and 616 sessions (D3) |
| A4 | Establishing a trend emits `TREND_ESTABLISHED` | Results depended on the start date (D5) |
| A5 | Secondary flags for retracement and duration | Config keys were unused (D8) |
| A6 | Line confirmation date and drift filter | Line breakouts had look-ahead; lines were trend segments (D2, D6) |
| A7 | Cycle-aware pair matching in either order | Leading averages were ignored (D1) |
| A8 | Resistance above the close, support below | Resistance zones sat below price (D7) |
| A9 | Rename `hamilton_3pct_filter` to `rhea_3pct_filter`; mark 8 percent agent-defined | Misattribution (D11, R-013) |

Amendment commits are `5a3b907` (configuration and amendments) and `ca7a284` (amendments A1 to A9, 204 tests).

### 4.4 From 108 lines to 41

At the first setting (5 percent band, 14 sessions, no drift filter), the 2015-onward window held 108 lines. At 15 sessions with the drift filter, 41 sideways lines remain (`reports/spec_review_p3.md`, section 3a). The saved analysis JSON holds 41 line ranges (`outputs/json/DJI_DJT_2026-11-06_pct0.03.json`).

### 4.5 The 2016-04-14 case

Under the strict rules, `^DJI` at 10 percent stalled from 2016-04-14 for 597 sessions, a 45.3 percent move in closes. A separate stall began on 2022-11-23 and lasted 616 sessions (D3, `reports/spec_review_p3.md`). The 2016-04-14 reversal returns under the equal-extreme tolerance. The contract records this in deviation 14 (`docs/specs/algorithm_contract.md`). The same review found 2016-02-11 labelled LL, 0.04 percent below 2015-08-25 (`reports/spec_review_p3.md`, section 1, row 2).

## 5. Rule backtest

### 5.1 Protocol

- Protocol versions: v1 with sha256 `d94a32e14531350d981f8dab6a6d248f1023fe8380a98af92dd54139a0bcbbc2`, then v2 with whole-file sha256 `c8675eff2b281ac6f4fa8ed790063ecaf1e063d78f20fa9569ded1988be39836` (`analysis/decision_table.md`, "Protocol history"; `analysis/decision_table.sha256`).
- Scoped hash `35de767a77dc3aca47d4727c5e78411160694fd4104cb8e609c4a0421e900caa` covers the text above the marker line (`analysis/decision_table.sha256`, line 2).
- Family: eight rules, Holm correction, alpha 0.05, minimum n 30, bootstrap 2,000 draws, block length 20, seed `20261108` (`analysis/decision_table.md`, sections 0 and 1).
- Sample: `^DJI` and `^DJT`, 1992-01-02 to 2026-11-06, 8,775 bars (`analysis/decision_table.md`, section 0; `analysis/rule_status_table.md`, header).
- Primary specification: percent swings, 3 percent minor, 8 percent secondary, 15-session filter (`configs/dow.yaml`, `swings` block).

Pre-registration is git-verifiable for the table text, not for the hash file. `git show da6427c --stat` (2026-11-08 14:09 local, 06:09 UTC) contains `analysis/decision_table.md` with sha256 `c8675eff…`; the first label-driving run started at 06:26 UTC (`analysis/protocol_deviations.md`, header). The `.sha256` companion still carried the v1 hash in that commit and was updated in `3770aa1` (06:33 UTC) together with the harness and run files. The audit's one-commit statement (`reports/backtest_audit.md`, section 1) was written before this check and is superseded; the whole-file hash was the effective protection.

### 5.2 Results

`analysis/rule_status_table.md` holds the full table, and the README repeats it. The labels are R1 data-confirmed with the caveat, and R2 to R8 insufficient-evidence. No rule was refuted.

Two figures from the audit carry extra weight: R1's simulated random-walk p is 0.0055 in the harness and 0.0085 in the audit replay (`reports/backtest_audit.md`, section 7). R8's random-spell p is 0.0245 in the harness and 0.0305 in the audit's independent re-implementation (`reports/backtest_audit.md`, sections 1 and 3).

### 5.3 Audit verdicts F1 to F4

The audit verdict is "sound with findings" (`reports/backtest_audit.md`, section 8). Each finding is blocking for any citation until it is handled.

- **F1 (high, interpretation).** The 0.5 null overstates R1. Every citation must give the 0.65 to 0.69 baseline, the simulated p and n = 33.
- **F2 (medium, governance).** The first full label-driving run `b94022285206435e83b1c068eb123dc9` was persisted but not recorded in the deviations log. Its rows collapsed under the old sort key.
- **F3 (medium, tooling).** The scoped hash matched the prose mention of the marker, not the marker line. Protection rested on the whole-file hash alone.
- **F4 (medium, design).** R3 and R6 "single" groups classify with information up to the outcome window. Three of the 12 reversals double-count.

### 5.4 Incidents and corrections

| Id | What happened | Recorded in |
|---|---|---|
| INC-01 | Run `b94022285206435e83b1c068eb123dc9` lost rows: 394 rows collapsed to 16 under the old sort key `(rule_id, pair, run_id)`. The key was changed to include `metric_name`, and the run was repeated as `a6d2d48e46014e7da3cc7c6be7ce8a02`, the run of record. | `analysis/protocol_deviations.md`, INC-01; `db/README.md`, "Migrations" |
| FIX-01 | Scoped hash used the prose mention of the marker | `analysis/protocol_deviations.md`, FIX-01 |
| FIX-02 | Run start time recorded at finish; R7 volume rows dated at the last bar | `analysis/protocol_deviations.md`, FIX-02 |
| DEV-01 to DEV-09 | Clarifications where the table was silent or contradictory. None changed a label. | `analysis/protocol_deviations.md` |

The audit's section 1 notes that 410 ledger rows across both runs carry the same decision-table hash (`reports/backtest_audit.md`, section 1).

### 5.5 What would change the labels

- **R1.** A pre-registered simulated null in a v3 table would replace the 0.5 null (DEV-10). The auditor estimates that a random-walk p entered into the Holm family would give p_holm of about 0.04 to 0.07, which is borderline (`reports/backtest_audit.md`, section 7).
- **R6 and R7.** Their refutation bounds of 0.547 and 0.516 sit close to the null (`analysis/rule_status_table.md`). A longer sample or a pooled-pair family could move them.
- **R2 and R3.** They have 12 and 15 events, below the floor of 30. More reversals would be needed.
- **R8.** It has 28 position changes, below the floor of 30.
- **R4 and R5.** The worst grid point governs both labels (`analysis/decision_table.md`, section 1.8). The threshold was chosen on the same sample.

## 6. Review gate calibration

### 6.1 Weights

The knowledge-only skill has no execution or test axis to score. Its auto score is 83 in the review JSON, where test status is not applicable and the test-health score is 12 of 20 (`reports/skill_review_dow-theory-sources_2026-11-08_144510.json`, `auto_review`). The script skills score 98 on the same axis (`reports/skill_review_dow-swing-detection_2026-11-08_150841.json`). At weights 0.5 and 0.5 the knowledge-only skill would score 88 with the same LLM score of 93, below the gate. At 0.35 and 0.65 it scores 89.5, which the reviewer reports as 90 (`reports/skill_review_dow-theory-sources_2026-11-08_144510.json`, `final_review`).

### 6.2 Final scores

| Skill | Final round | Auto | LLM | Final | Weights | Commit |
|---|---|---|---|---|---|---|
| `dow-theory-sources` | 3b | 83 | 93 | 90 | 0.35 / 0.65 | `92179e4` |
| `dow-swing-detection` | 2 | 98 | 93 | 96 | 0.5 / 0.5 | `31d8f86` |
| `dow-trend-classification` | 2 | 98 | 93 | 96 | 0.5 / 0.5 | `dea6e8a` |
| `dow-confirmation-and-line` | 2 | 98 | 96 | 97 | 0.5 / 0.5 | `3ec2aa8` |
| `dow-levels-and-chart` | 2 | 98 | 96 | 97 | 0.5 / 0.5 | `3c780c6` |
| `dow-rule-backtest` | scripts + tests (0.5/0.5) | 98 | 88 | 95 | 2 | 96 |

Sources: the final JSON for each skill in `reports/skill_review_dow-*_2026-11-08_*.json`, and the commit messages in `.git/logs/HEAD`.

The `dow-swing-detection` commit message records 95.5, while the ledger and reviewer record 96 (`analysis/skill_boundary_ledger.md`, row 2). The reviewer rounds the average up.

The saved directory includes several runs per skill. Some are auto-only runs at weights 1.0 and 0.0, for example `reports/skill_review_dow-trend-classification_2026-11-08_152709.json` with a final of 78. Those runs are not gate results. The round-by-round LLM scores before the final round are not preserved in the saved JSON, so this table does not show them.

### 6.3 The skill-1 exception

`dow-theory-sources` passed in round 3b, one round beyond the three-round cap. The ledger records the exception and its cause: round-3 findings were project-state drift that landed during review (`analysis/skill_boundary_ledger.md`, row 1). The reviewer's remaining findings were low severity (`reports/skill_review_dow-theory-sources_2026-11-08_144510.json`, `llm_review`).

### 6.4 Dow-specific risks at the gate

The reviewer for `dow-swing-detection` noted that the description sat at exactly 1,024 characters, the limit (`reports/skill_review_dow-swing-detection_2026-11-08_150841.json`, `llm_review`). Any new trigger word would break skill loading.

## 7. Team execution against the design

`docs/team_design.md` (section 1) defines 19 roles. The repository records the following.

| Role | Record in the repository |
|---|---|
| R2 source harvesters | `research/sources/*.md`, 42 files |
| R3 rules synthesiser | `research/canonical_rules.md` |
| R4 schema designer (DBA) | `db/init/01_schema.sql`, commit `db4764e` |
| R5 pipeline engineer | commit `897f51e` |
| R6 integrity gate | `reports/integrity_*.txt`, five saved runs |
| R8 spec reviewer (quant-analyst) | `reports/spec_review_p3.md` |
| R9 code reviewer | `reports/code_review_p2.md` ("red team") |
| R11 methodology auditor (Model QA) | `reports/backtest_audit.md` |
| R12 statistical verdict | `analysis/decision_table.md`, `analysis/rule_status_table.md` |
| R13 and R14 skill author and reviewer | `reports/skill_review_*` |
| R16 agent author | `.claude/agents/dow-theory.md` (commit `0aa753b`, "P6 draft") |
| R17 golden run | Six prompts run against the `dow-theory` agent in parallel (one agent instance per prompt), answers assembled from transcripts, graded by a fresh Reality Checker instance (`analysis/agent_verification_sample.md`) |
| R18 docs | `README.md` and this file |
| R19 quote audit (all 530 quotes, not the 15 percent sample) | `reports/quote_audit_p1.md` |
| R15 technical-analysis consultant | No record in the repository |

The repository does not record wave timing. Commit order is in `.git/logs/HEAD`.

Two execution facts are recorded here by the lead because no repo file holds them. First, the `search-specialist` and `scientific-literature-researcher` agent types used for P1 have no file-writing tool, so their notes existed only in transcripts; the lead spawned a write-capable scribe agent that received each note by message and wrote it verbatim (30 notes), and recovered the remaining notes directly from the agents' transcripts (12 notes). Second, the agent harvesting the primary texts (Hamilton 1922, Nelson 1903, Rhea 1932) hit an output content filter after reading long passages of in-copyright scans; the job was re-run by a write-capable agent under an explicit quoting policy (public-domain texts quoted freely, at most eight short sentences from copyrighted previews, no pirated PDFs), which produced the first-hand verified notes now in `research/sources/`.

## 8. Open issues

- **Protocol v3, DEV-10.** Pre-register a simulated random-walk or gambler's-ruin null as the R1 label null (`analysis/protocol_deviations.md`, DEV-10).
- **Protocol v3, DEV-11.** Define the R3 and R6 "single" group as not confirmed by `period_end`, and count each reversal once (`analysis/protocol_deviations.md`, DEV-11).
- **Pre-registration hygiene.** The table text was committed before the run (`da6427c`) but its hash file lagged one commit; commit both together before any future run (`reports/backtest_audit.md`, section 8).
- **Individual-stock data path.** `load_klines` reads only `dow.mkt_klines` or CSV; the planned read-only `usstock`/`twstock` loader source was not implemented. The golden-run agent worked around it by exporting AAPL and SPY from `usstock.mkt_daily_quotes` to CSV (`outputs/csv/`). Add a `--source usstock|twstock` adapter (adjusted-price caveat) in a follow-up.
- **Chart legibility.** In `outputs/charts/DJI_DJT_2026-11-06_pct0.03.png`, signal labels overlap, and the defense-line label is hard to read against the price line.
- **Edwards-Magee and Kirkpatrick-Dahlquist.** Quotes were checked through Google Books snippets only. The full text is not in the sources (`research/sources/edwards-magee-technical-analysis-dow-chapters.md`, line 8; `research/sources/kirkpatrick-dahlquist-technical-analysis-dow-theory.md`, line 8).
- **Schannep book.** The book and its preview were not retrieved. The Schannep figures come from the AAII article and secondary pages (`research/sources/schannep-dow-theory-21st-century.md`, line 49).
- **Per-symbol threshold for `^DJT`.** `configs/dow.yaml` has `per_symbol_secondary_pct: {}`. The spec review suggests 12 percent for `^DJT`, which gives a swing count near that of `^DJI` at 8 percent. The suggestion is unverified and not applied. At 10 percent `^DJT` has 119 swings against 53 for `^DJI` (`reports/spec_review_p3.md`, section 3b).
- **R-046 wording.** The swing-threshold row still mentions the superseded 10 percent value next to the adopted 8 percent (`research/canonical_rules.md`, R-046).
- **Stale registry text.** Section 7 says the `^DJI` and `^DJT` series have no volume (`research/canonical_rules.md`, section 7). The header says 43 notes; the folder holds 42.
- **Agent description.** `.claude/agents/dow-theory.md` says each of the six skills has passed review. `dow-rule-backtest` has not.
- **Unverified code-review items.** Items M1 to M7, L1 to L7 and L8 in `reports/code_review_p2.md` are not confirmed closed.
- **Chart legibility.** Overlapping zone labels when zones are adjacent, stacked signal labels around 2020, and a short defense-line segment when recently set (`.claude/skills/dow-levels-and-chart/SKILL.md`, Limitation 5).

## 9. Install and reproduction steps

```
uv venv --python 3.11 .venv
uv run --python .venv/bin/python pytest -q
```

ClickHouse runs in the shared Docker container from the compose file in `../trading_system` (`CLAUDE.md`, "Environment"). Copy `.env.example` to `.env` and set the connection variables. Do not commit `.env`.

```
.venv/bin/python scripts/init_clickhouse.py
uv run --python .venv/bin/python -m dowtheory.cli fetch --symbols '^DJI' '^DJT' '^GSPC' '^IXIC' SPY IYT
.venv/bin/python scripts/check_integrity.py
uv run --python .venv/bin/python -m dowtheory.cli analyze --symbol '^DJI' --pair '^DJT' --start 2015-01-01
uv run --python .venv/bin/python -m dowtheory.cli backtest --out reports
```

`check_integrity.py` must exit 0 before any analysis or backtest (`CLAUDE.md`, "Data Integrity"). `backtest` without `--persist` writes reports and does not write the ledger (`src/dowtheory/cli.py`, `backtest` subcommand).

Global install and use from any directory (`docs/team_design.md`, section 2, P7; `docs/specs/skill_contract.md`, item 11):

```
mkdir -p ~/.claude/skills ~/.claude/agents
cp -R .claude/skills/dow-* ~/.claude/skills/
cp .claude/agents/dow-theory.md ~/.claude/agents/
export DOW_PROJECT_ROOT=<path-to-the-Dow-repository>
```
