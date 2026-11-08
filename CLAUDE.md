# Dow project rules

- Environment: always use `.venv` (`uv venv --python 3.11 .venv`; run with `.venv/bin/python` or `uv run`). Never pollute the native environment. ClickHouse runs only in Docker (shared container `trading_clickhouse`, compose file in `../trading_system`).
- Language: all code, skills, agent, docs and chart text are **English**. Chinese trigger words (道氏防線, 支撐線, 壓力線, 主要趨勢, 次要趨勢, 小型趨勢) appear only in the agent description and routing table.
- Database: write only to the `dow` database. `usstock` and `twstock` are read-only. Follow `~/.claude/db_naming_convention.md` (mkt_/str_/ops_ prefixes, Decimal on prices, `ts_open`/`ts_close` + `inserted_at`, no `_daily`). No `DROP` on shared tables.
- Data integrity: after init or backfill run `.venv/bin/python scripts/check_integrity.py`; exit 0 is required before any analysis or backtest. Analytic reads of ReplacingMergeTree tables use `FINAL`.
- Algorithms live only in `src/dowtheory/`. Skill `scripts/` are thin CLI wrappers (plus the shared `_anchor.py`). No duplicated swing/trend logic anywhere.
- Status labels (every quantitative statement in skills and agent output carries one): literature layer `【literature-consensus】` `【literature-disputed】` `【agent-defined】`; data layer `【data-confirmed】` `【data-refuted】` `【insufficient-evidence】`. The Dow defense line is `agent-defined` and has no literature source; never present it as canonical.
- Quotes from sources must be verbatim with a URL and are checked by `scripts/check_quotes.py` against `research/sources/`. Disputed figures are presented side by side without adjudication.
- No lookahead: swings carry `confirmed_idx`; downstream code may only use swings confirmed at or before the evaluation bar. Backtest decision table (`analysis/decision_table.md`) is written and hashed before any backtest runs.
- Skills are generated one at a time, each reviewed with the dual-axis reviewer (`--project-root .claude`, weights 0.5/0.5 for skills with scripts, 0.35/0.65 only for knowledge-only skills) to a score ≥ 90, at most 3 rounds, author and reviewer being different agent instances.
- One commit per phase and per passed skill. Never run `rm -rf`.
