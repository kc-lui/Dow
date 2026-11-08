# Dow Theory agent and skills

Dow Theory as a Claude Code subagent (`dow-theory`) and six `dow-*` skills. The project turns the public Dow Theory literature into a sourced rule registry, implements the trend rules in code, draws charts (PNG, JSON and markdown), and tests the rules on Dow Jones Industrial (`^DJI`) and Transportation (`^DJT`) history from 1992. The agent describes trend state and evidence. It never predicts prices, gives targets, or offers investment advice.

## Core deliverables

| Deliverable | Location | Auto | LLM | Final | Round | Status |
|---|---|---|---|---|---|---|
| `dow-theory-sources` | `.claude/skills/dow-theory-sources/` | 83 | 93 | 90 | 3b (see note 1) | passed |
| `dow-swing-detection` | `.claude/skills/dow-swing-detection/` | 98 | 93 | 96 | 2 | passed |
| `dow-trend-classification` | `.claude/skills/dow-trend-classification/` | 98 | 93 | 96 | 2 | passed |
| `dow-confirmation-and-line` | `.claude/skills/dow-confirmation-and-line/` | 98 | 96 | 97 | 2 | passed |
| `dow-levels-and-chart` | `.claude/skills/dow-levels-and-chart/` | 98 | 96 | 97 | 2 | passed |
| `dow-rule-backtest` | `.claude/skills/dow-rule-backtest/` | 98 | 95 | 96 | 2 | passed |
| `dow-theory` agent | `.claude/agents/dow-theory.md` | n/a | n/a | n/a | n/a | golden run: pending |

Each skill must pass a dual-axis review with a gate of 90. Scripts-backed skills weight the axes 0.5 and 0.5. The knowledge-only skill weights them 0.35 and 0.65 (see `docs/team_design.md`, section 3). Sources: the final scores are in `reports/skill_review_dow-*_2026-11-08_*.json` and the LLM scores in `reports/llm_review_dow-*.json`.

1. `dow-theory-sources` passed in round 3b. Round 3b is one extra round beyond the three-round cap, granted because round-3 blockers were project-state drift. The ledger records the exception in `analysis/skill_boundary_ledger.md`.

`dow-rule-backtest` passed in round 2 (`reports/llm_review_dow-rule-backtest.json`, LLM 95; merged 96 in the latest `reports/skill_review_dow-rule-backtest_*.json`).

## What the agent can do

- **Three trends.** Primary, secondary and minor trends from confirmed swings. The primary trend is a state machine: UNDEFINED, BULL_PRIMARY, BEAR_PRIMARY, BULL_SUSPECT and BEAR_SUSPECT.
- **Dow defense line (agent-defined).** The last confirmed secondary reaction low in a bull trend, or reaction high in a bear trend. No source defines or names this construct, so every output labels it agent-defined.
- **Support, resistance and trendlines.** Zones clustered from confirmed swings on the correct side of the last close. Two-point trendlines through the last two confirmed reaction lows or highs.
- **Two-average confirmation.** Industrials against Transports, reported as confirmed, non_confirmation or pending. Matching is cycle-aware and works in either order.
- **Dow lines.** Sideways bands in both averages (5 percent band, at least 15 sessions, net drift filter) and their breakouts.
- **Charts and reports.** One command writes a PNG chart, a JSON twin and a markdown table.
- **Rule evidence.** Pre-registered backtest results for eight rules, each with a literature label and a data label.

Example command:

```
uv run --python .venv/bin/python -m dowtheory.cli analyze --symbol '^DJI' --pair '^DJT' --start 2015-01-01
```

Headline state for `^DJI` with `^DJT` as of 2026-11-06, from `outputs/json/DJI_DJT_2026-11-06_pct0.03.json`:

- **Primary trend:** BULL_PRIMARY since 2023-06-15.
- **Dow defense line:** 45,166.64 (agent-defined), set on 2026-03-27.
- **Confirmation:** non_confirmation. `^DJT` is BEAR_PRIMARY, dated 2026-09-24 in `reports/spec_review_p3.md`. Non-confirmation is a warning, not a reversal.
- **Lines:** 41 line ranges in the saved JSON.

The chart for the same run is `outputs/charts/DJI_DJT_2026-11-06_pct0.03.png`. The file name rule is `{symbol}_{pair}_{as_of}_{method}{minor_pct}.png` with the caret removed (`docs/specs/algorithm_contract.md`, section Chart).

## Evidence labels

Every quantitative statement in the skills and the agent carries two labels, one per layer.

**Literature layer** (`research/canonical_rules.md`):

- `literature-consensus`: at least two independent sources agree and none contradicts. Most consensus rows trace to one lineage, Dow to Hamilton to Rhea.
- `literature-disputed`: at least two sources give materially different figures or readings. Positions are shown side by side and never adjudicated.
- `single-source`: one source states the rule, or later sources only echo it.
- `agent-defined`: a construct of this project, with no literature source.

**Data layer** (`analysis/decision_table.md`, sections 1.3 and 1.4):

- `data-confirmed`: at least 30 events, Holm-adjusted p below 0.05 in the predicted direction, and both sub-samples agree.
- `data-refuted`: the one-sided Bonferroni bound excludes the null on the wrong side, and both sub-samples agree.
- `insufficient-evidence`: everything else.

R1 carries a mandatory caveat. Its 0.5 null is not a random-walk baseline. A drift-matched random walk run through the same machinery gives p_extend of about 0.65 to 0.69, and the random-walk p is 0.0055 in the harness and 0.0085 in the audit replay (`reports/backtest_audit.md`, section 7). Any citation of R1 must state that baseline, the random-walk p and n = 33. Citing the Holm-adjusted p alone is not allowed.

## Rule backtest results

Pair `DJ` (`^DJI` against `^DJT`), 1992-01-02 to 2026-11-06, primary specification `pct0.03/0.08f15`. Source: `analysis/rule_status_table.md`.

| Rule | Literature label | Data label | n | Estimate | 95% CI | p_holm |
|---|---|---|---|---|---|---|
| R1 trend persistence | consensus | data-confirmed (with caveat) | 33 | p_extend 0.8788 | [0.7267, 0.9518] | 0.000044 |
| R2 primary reversal signal | disputed | insufficient-evidence | 12 | excess log return, h60: -0.0151 | [-0.0456, 0.0206] | 1.000000 |
| R3 two-average confirmation | consensus | insufficient-evidence | 15 | difference, h60: -0.0544 | [-0.1385, 0.0308] | 1.000000 |
| R4 secondary retracement | disputed | insufficient-evidence | 44 | share in 1/3 to 2/3: 0.4091 | [0.2769, 0.5559] | 1.000000 |
| R5 secondary duration | disputed | insufficient-evidence | 44 | share in Rhea window: 0.7273 | [0.5815, 0.8365] | 0.310191 |
| R6 line breakout | consensus | insufficient-evidence | 87 | agreement, h20: 0.4138 | [0.3161, 0.5188] | 1.000000 |
| R7 volume confirmation | disputed | insufficient-evidence | 57 | share with-trend volume higher: 0.3509 | [0.2400, 0.4806] | 1.000000 |
| R8 Hamilton-style timing | disputed | insufficient-evidence | 28 | delta Sharpe: 0.1099 | [-0.1827, 0.4336] | 1.000000 |

R4 and R5 use the worst grid point over the secondary threshold, so their p-values are the most conservative across the grid. R8 has 28 position changes, below the 30 floor. Effects are in each metric's own units.

`insufficient-evidence` means the data did not meet the minimum sample, did not reach significance after the Holm correction, or the two sub-samples disagreed. It does not mean the rule is false. R6 and R7 have refutation bounds of 0.547 and 0.516, which sit above the null of 0.5, so the data do not refute them.

The Dow defense line and support and resistance zones are not in the backtest family. No rule tests them.

## Data pipeline

Market data lives in the ClickHouse database `dow` (`db/README.md`). The database holds six tables:

- `mkt_klines`: daily OHLCV bars, with source and exchange.
- `str_swing_log`, `str_trend_state_snapshots`, `str_level_log`: persisted analysis output, written only with `--persist`.
- `str_rule_backtest_log`: the rule evidence ledger, with metrics, labels and hashes.
- `ops_data_quality_log`: integrity findings, grouped by run and never deduplicated.

Prices are `Decimal(12, 4)`, with no float types. The package connects as a dedicated user, `dow_user`, with write rights only on `dow.*` and read rights on `usstock.*` and `twstock.*`. A client-side SQL guard adds a second check (`src/dowtheory/storage/sql_guard.py`). Analytic reads use `FINAL`.

Coverage from the 2026-11-08 integrity report (`reports/integrity_20261108_142118.txt`):

| Symbol | Exchange | First date | Last date | Rows | Notes |
|---|---|---|---|---|---|
| `^DJI` | INDEX | 1992-01-02 | 2026-11-06 | 8,775 | |
| `^DJT` | INDEX | 1992-01-02 | 2026-11-06 | 8,775 | |
| `^GSPC` | INDEX | 1927-12-30 | 2026-11-06 | 24,831 | analysis_start 1962-07-02 clips 8,635 close-only bars |
| `^IXIC` | INDEX | 1971-02-05 | 2026-11-06 | 14,057 | analysis_start 1984-10-11 clips 3,457 close-only bars |
| `SPY` | NYSEARCA | 1993-01-29 | 2026-11-06 | 8,502 | |
| `IYT` | NYSEARCA | 2004-01-02 | 2026-11-06 | 5,749 | |

Yahoo serves open, high, low and close as one value before the analysis start for `^GSPC` and `^IXIC`. The loader clips those bars by default (`configs/dow.yaml`, `data.analysis_start`). Prices are unadjusted (`auto_adjust=False`). Stooq was probed as a fallback source and its CSV endpoint returned 404. The stored data comes from yfinance (`docs/team_design.md`, section 2, P0).

Integrity gate, latest saved run (`reports/integrity_20261108_142118.txt`, 06:21:18 UTC):

```
SUMMARY errors=0 warnings=7 info=14
STATUS PASS
```

The gate reports seven warnings, including the close-only flat bars before the analysis start and one zero-volume `^DJT` bar in 1998. The live `check_integrity.py` run was not repeated for this README.

## Methodology

The work followed five phases, each with a team role and a gate (`docs/team_design.md`, sections 1 and 2):

- **P0 scaffold:** repository, environment, ClickHouse, and a coverage probe.
- **P1 literature:** 42 source notes in `research/sources/`, each with verbatim quotes and URLs, then a synthesised rule registry in `research/canonical_rules.md`.
- **P2 data layer:** schema, pipeline and integrity gate. A code review (`reports/code_review_p2.md`) found write-scope and quality-log defects, which a later commit (`a9fc82d`) addressed.
- **P3 algorithms:** swings, state machine, lines, confirmation, levels and chart, implemented in `src/dowtheory/`. The frozen contract (`docs/specs/algorithm_contract.md`) was reviewed against the code (`reports/spec_review_p3.md`), and amendments A1 to A9 followed.
- **P4 rule backtests:** a pre-registered protocol, the run, and an independent methodology audit (`reports/backtest_audit.md`).
- **P5 skills:** six skills, generated one at a time, each reviewed to a score of at least 90.
- **P6 agent and P7 golden run and install:** the routing agent (`.claude/agents/dow-theory.md`), a six-question golden run graded by an independent Reality Checker (`analysis/agent_verification_sample.md`), then the global install (`cp -R`, byte-identical check, zero `/Users/` paths).

Source quotes: 530 quotes were checked against their source pages. 504 match word for word, 16 differ in minor typography, one misquote was fixed, five were not found at the cited URL, and four pages were unreachable (`reports/quote_audit_p1.md`).

Canonical rules: 65 rules (R-001 to R-065). Labels: 27 consensus, 16 disputed, 3 agent-defined and 19 single-source (`research/canonical_rules.md`, section 1).

Protocol: the backtest protocol is `analysis/decision_table.md`. Its whole-file sha256 is `c8675eff2b281ac6f4fa8ed790063ecaf1e063d78f20fa9569ded1988be39836` (`analysis/decision_table.sha256`). The protocol deviations log is `analysis/protocol_deviations.md`. The configuration hash of the committed `configs/dow.yaml` is `e6f5b9cd228e458809a42aa2a5c5e2811175de3d74fafca1a3496c6ac68ae24e`. The provenance of the pre-registration is disputed (see Limitations).

Skill gate: a skill passes at a dual-axis score of at least 90, within three rounds. The author and the reviewer must be different agent instances. Each skill's `check_labels.py` and `check_quotes.py` results are recorded in its review.

Gate outputs at the final commit (run by the lead on 2026-11-08):

```
341 passed in 36.19s
SUMMARY errors=0 warnings=7 info=14
STATUS PASS
ALL CLEAN   (scripts/check_quotes.py)
ALL CLEAN   (scripts/check_labels.py)
```

## Usage

Claude Code subagent (routes by decision framework):

```
@dow-theory what is the primary trend of ^DJI as of 2026-11-06, and does ^DJT confirm it?
```

Single skill, loaded by name:

```
/dow-levels-and-chart
/dow-swing-detection
```

Command-line tool (`dow`, entry point in `pyproject.toml`):

| Subcommand | Purpose |
|---|---|
| `dow init-db` | create the `dow` tables |
| `dow fetch --symbols ... [--source yfinance\|stooq] [--start ...] [--probe]` | fetch bars into `dow.mkt_klines` |
| `dow check [--symbols ...]` | run integrity checks, exit 1 on any error |
| `dow analyze --symbol ... [--pair ...] [--as-of ...] [--start ...] [--source clickhouse\|csv] [--method pct\|atr\|pivot] [--no-chart] [--persist]` | trend state, defense line, levels, lines, chart |
| `dow backtest [--pair ...] [--no-sweeps] [--persist] [--out reports]` | rerun the pre-registered backtests |

Install the skills and agent globally, then point them at this repository:

```
mkdir -p ~/.claude/skills ~/.claude/agents
cp -R .claude/skills/dow-* ~/.claude/skills/
cp .claude/agents/dow-theory.md ~/.claude/agents/
export DOW_PROJECT_ROOT=/path/to/Dow
```

Reproduction: create the environment with `uv venv --python 3.11 .venv`, start ClickHouse from the shared compose file (`../trading_system`), copy `.env.example` to `.env`, run `.venv/bin/python scripts/init_clickhouse.py`, then `dow fetch`, `dow check` and `dow analyze`.

## Directory structure

```
.claude/
  agents/dow-theory.md              routing and integration agent (decision framework, routing table)
  skills/dow-*/                     six skills: SKILL.md, references/evidence.md, scripts/, tests/
CLAUDE.md                           project rules
pyproject.toml                      package dowtheory; dow CLI
.env.example                        ClickHouse connection variables
configs/
  dow.yaml                          swing, trend, line, confirmation and backtest parameters (hashed)
  pairs.yaml                        confirmation pairs
db/
  README.md                         schema, read and write rules, migrations
  init/01_schema.sql                six dow tables
  init/02_users.sql                 scoped dow_user
docs/
  team_design.md                    roles, phases, quality gates
  specs/algorithm_contract.md       frozen contract, deviations, amendments A1 to A9
  specs/skill_contract.md           content contract for every dow-* skill
analysis/
  decision_table.md (+ .sha256)     pre-registered backtest protocol
  rule_status_table.md              R1 to R8 results and labels
  protocol_deviations.md            DEV, INC and FIX log
  skill_boundary_ledger.md          skill coverage ledger
research/
  canonical_rules.md                rule registry R-001 to R-065
  sources/*.md                      42 source notes with verbatim quotes and URLs
  academic-search-log.md            post-1998 search for tests of Dow Theory
src/dowtheory/                      all algorithms and storage (single home)
  swings.py trend.py line.py confirmation.py levels.py analysis.py chart.py report.py
  config.py schema.py persist.py cli.py
  data/                             fetchers, loader, bar normalisation, quality checks
  storage/                          ClickHouse client and SQL guard
  backtest/                         events, statistics, rules, labels, nulls, protocol, runner, ledger
scripts/
  check_integrity.py                integrity gate (exit 0 required)
  check_quotes.py check_labels.py   quote and label linters for skills
  init_clickhouse.py                create tables (idempotent)
  migrate_*.py                      one-off migrations, no DROP
  tests/                            linter tests
tests/                              unit, integration and smoke tests
reports/                            integrity logs, reviews, quote audit, backtest audit and rule reports, skill reviews
outputs/
  charts/                           PNG charts from dow analyze
  json/                             JSON twins of each analysis
```

## Limitations

- **Agent-defined constructs.** The defense line, the 8 percent secondary threshold, the 15-session filter, the 5 percent line band and the level tolerances are this project's choices. Only Rhea's 3 percent filter has a source, and it is single-source (`research/canonical_rules.md`, R-013 and R-046).
- **In-sample threshold choice.** The 8 percent and 15-session settings were chosen on the same sample they are tested on. R4 and R5 are protected by the worst-grid-point rule. R1 is affected indirectly (`reports/backtest_audit.md`, section 5).
- **R1 baseline.** The 0.5 null overstates the strength of R1. Cite the caveat above every time.
- **Short history for `^DJT`.** The analysis starts in 1992. Nothing tests Dow Theory on 1897 to 1991 data.
- **One pair.** The backtests cover the `DJ` pair only. The `SP_IYT` robustness pair is reported but never labelled. Individual stocks are analysis only.
- **Unadjusted indices.** Index and ETF prices exclude dividends, so the buy-and-hold comparison favours the strategy.
- **Second-hand Rhea.** Rhea's text was read through the Wiley reprint excerpt and through secondary pages, not in the original.
- **Tool-extracted quotes.** Quotes were extracted with tools and checked by exact string match. The Edwards-Magee and Kirkpatrick-Dahlquist quotes were checked through Google Books snippets, not full text.
- **Pre-registration provenance.** Verified by git: the v2 decision table text (sha256 `c8675eff…`) is in commit `da6427c` (2026-11-08 06:09 UTC), before the first label-driving run at 06:26 UTC; only the `.sha256` companion file lagged until `3770aa1` (06:33 UTC). The audit's one-commit sentence (`reports/backtest_audit.md`, section 1) predates this check and is superseded by the header of `analysis/protocol_deviations.md`. Future runs: commit the table and its hash file together before the first run.
- **Chart legibility.** In the saved chart, signal labels overlap, and the defense-line label is hard to read against the price line.
- **Not advice.** The output describes trend state and evidence. It is not investment advice.
