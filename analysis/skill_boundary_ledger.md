# Skill boundary ledger

Order of generation (DRY anchors first). One entry appended per skill that passes dual-axis review ≥ 90.

| # | skill | covers | does not cover → sibling | DRY anchor | review (auto / LLM / final, round) |
|---|---|---|---|---|---|
| 1 | `dow-theory-sources` | glossary + Chinese term mapping; label vocabulary and R-id reading; canonical rules digest with disputed figures side by side; provenance chain; performance evidence (Cowles, BGK, Sideris, StockCharts, Schannep); defense-line negative result; answer procedure | swing parameters → `dow-swing-detection`; state machine / defense line definition → `dow-trend-classification`; line & confirmation algorithms → `dow-confirmation-and-line`; S/R, trendlines, chart → `dow-levels-and-chart`; data labels authority → `dow-rule-backtest` | DRY anchor for glossary, labels, registry digest (knowledge-only, weights 0.35/0.65) | 83 / 93 / **90**, round 3b — one extra round beyond the 3-round cap granted because round-3 blockers were project-state drift (15-session filter and backtest results landed in parallel), documented here as an exception |
