# Dow — Team Design (P0 deliverable)

Project: distill Dow Theory into a Claude Code subagent `dow-theory` plus six `dow-*` skills, modelled on the sister project `../HD` (skills generated one at a time → dual-axis review ≥ 90 → thin routing agent → golden run → global `cp -R` install).

Three differences from HD shape everything:
1. **Source is public literature, not a private corpus.** Evidence labels are two-layered: literature `【literature-consensus】【literature-disputed】【agent-defined】` and data `【data-confirmed】【data-refuted】【insufficient-evidence】`.
2. **Skills carry executable scripts.** The agent must draw: swing highs/lows, three trends (primary / secondary / minor), the Dow defense line (agent-defined construct), support / resistance / trendlines, Dow "lines" (sideways bands), two-average confirmation, volume confirmation. Output = PNG (matplotlib) + JSON + markdown.
3. **Rule-level quantitative validation** on DJIA/DJT history (Brown-Goetzmann-Kumar 1998 line) produces the data-layer labels.

User decisions: data source ClickHouse (shared container `trading_clickhouse`, new per-product DB `dow`); PNG + JSON output; rule backtests; English everywhere (Chinese trigger words only in the agent description/routing table).

## 1. Roles

| # | Role | Agent type | Phase | Outputs | Gate |
|---|---|---|---|---|---|
| R0 | Team designer | agent-organizer | P0 | this file | user approval |
| R1 | Scaffold / infra | main session | P0 | git, venv, CLAUDE.md, ClickHouse up | ping OK, imports OK |
| R2 | Source harvesters | search-specialist ×3, scientific-literature-researcher ×2 | P1 | `research/sources/*.md` (URL, date, verbatim quotes) | every quote has a URL |
| R3 | Rules synthesizer | research-analyst | P1 | `research/canonical_rules.md` (R-001…, agree/disagree matrix, defense line = AGENT-DEFINED) | each rule ≥ 2 sources or flagged single-source |
| R4 | Schema designer | database-administrator | P2 | `db/init/01_schema.sql` | DBA-1/6/8 audit, idempotent DDL |
| R5 | Pipeline engineer | python-pro (data-engineer reviews contract) | P2 | fetch / backfill / loader / quality, `scripts/check_integrity.py` | exit 0, pytest green |
| R6 | Integrity gate | main session | P2 | `reports/integrity_<ts>.txt` | checks below |
| R7 | Algorithm engineers | python-pro ×2 (A swings+trend, B levels+line+confirmation+chart) | P3 | `src/dowtheory/*`, CLI | synthetic tests, no-lookahead test |
| R8 | Spec reviewer | quant-analyst | P3 | rule-id → function table | every rule implemented or marked non-algorithmic |
| R9 | Code reviewer | code-reviewer | P2–P4 | review | tests green, ruff clean |
| R10 | Backtest engineers | backtest-expert skill + python-pro ×3 | P4 | `backtest/`, `str_rule_backtest_log`, `reports/rule_<id>.md` | pre-registered thresholds |
| R11 | Methodology auditor | Model QA Specialist | P4 | `reports/backtest_audit.md` | truncation replay identical; multiple-testing handled |
| R12 | Statistical verdict | quant-finance-master + data-scientist | P4 | `analysis/decision_table.md` (before), `analysis/rule_status_table.md` (after) | labels follow table |
| R13 | Skill author | general-purpose + skill-creator, strictly serial | P5 | `.claude/skills/dow-*/` | R14 ≥ 90 |
| R14 | Skill reviewer | fresh general-purpose per skill, dual-axis-skill-reviewer | P5 | `reports/skill_review_*` | ≥ 90, ≤ 3 rounds, author ≠ reviewer |
| R15 | TA consultant | technical-analyst skill | P5 | advisory on S/R, defense line, lines | — |
| R16 | Agent author | main / general-purpose | P6 | `.claude/agents/dow-theory.md` | YAML parses, all skills routed |
| R17 | Golden run | qa-expert + Reality Checker | P7 | `analysis/agent_verification_sample.md` | 6/6 PASS |
| R18 | Docs | documentation-engineer | P7 | `README.md`, `docs/research.md` | real numbers only |
| R19 | Read-only auditor | Explore | P1/P5/P7 | 15 % quote audit, cross-skill DRY | 0 violations |

Concurrency ≤ 8 agents per wave (M1 16 GB). One commit per phase and per passed skill.

## 2. Phases

- **P0 Scaffold** — git, `uv venv --python 3.11`, pyproject, CLAUDE.md, `docker compose up -d clickhouse`, ping. Probe results (2026-11-08): yfinance `^DJI`/`^DJT` 1992-01-02 → today (8,775 bars), `^GSPC` 1927-12-30 →, `IYT` 2004 →, `SPY` 1993 →; Stooq CSV endpoint returned 404; `usstock.mkt_daily_quotes` 2,853 symbols 2015 →, `twstock.mkt_quotes` 2,542 symbols 2017 →.
- **P1 Literature** — 5 harvesters in parallel, then R3 synthesises `canonical_rules.md`; R19 audits 15 % of quotes.
- **P2 Data layer** — R4 DDL → `scripts/init_clickhouse.py` (CREATE only) → R5 fetch/backfill (`dow fetch --probe` records coverage in `ops_data_quality_log`) → R9 review → R6 integrity exit 0.
- **P3 Algorithms & drawing** — `Swing` dataclass and JSON schema frozen first; R7-A / R7-B in parallel; R8 rule→code table; R9 review; `dow analyze --symbol ^DJI --pair ^DJT` produces PNG + JSON + md.
- **P4 Rule backtests** — R12 writes and hashes `decision_table.md` before any run; R10 three rule families in parallel; R11 audit; R12 labels.
- **P5 Skills** (serial, DRY anchors first): `dow-theory-sources` (knowledge-only) → `dow-swing-detection` → `dow-trend-classification` → `dow-confirmation-and-line` → `dow-levels-and-chart` → `dow-rule-backtest`. Reviewer weights 0.5/0.5 for skills with scripts; 0.35/0.65 only for the knowledge-only skill, fixed before authoring.
- **P6 Agent** — `dow-theory.md`, tools `Read, Glob, Grep, Skill, Bash`, decision framework + trigger-word routing.
- **P7 Golden run / install / docs** — six prompts (chart; "what is the defense line" → agent-defined; a disputed rule; a refuted or insufficient rule; real DJI/DJT confirmation; a `usstock` stock), `cp -R` install, byte-identical diff, `/Users/` grep = 0, README + research doc.

## 3. Quality gates

- Integrity: NYSE-calendar gaps, duplicate `(symbol, ts_open)` without FINAL, OHLC sanity, zero volume (warn for indices), staleness, row reconciliation with source, write-scope = `dow` only.
- No lookahead: `confirmed_idx` on every swing; truncation-invariance test; audit replay.
- Labels: `scripts/check_labels.py` — every number in a skill carries one label; `scripts/check_quotes.py` — quotes verbatim against `research/sources/`.
- Skills: ≥ 90 dual-axis, ≤ 3 rounds, author ≠ reviewer, boundary ledger appended per pass.

## 4. Risks (ranked)

1. Lookahead from swing confirmation lag (R11). 2. Label inflation / p-hacking (R12: pre-registered table, correction, sub-samples, ranges not optima). 3. Agent-defined constructs leaking into literature (R3/R13). 4. Short DJT history, no pre-1992 data (R5: label insufficient, do not fudge). 5. Quote drift (R2/R19). 6. Skill overlap / duplicate code (R13: ledger, `src/dowtheory` single home). 7. Shared-container side effects (write `dow` only, no DROP). 8. Memory (≤ 8 agents). 9. Agent Bash scope (CLI + skill scripts, write `outputs/` only).

## 5. Decisions taken by the main session

Six skills (merged foundations+sources, reversal into trend, render into levels). P4 backtests index pairs only (DJ primary, SP/IYT robustness); individual stocks are analyse-only. Three phases (accumulation etc.) are labelled non-measurable. Pre-1992 claims default to insufficient-evidence unless a long-history source is found.
