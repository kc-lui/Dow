---
name: demo
description: Frontmatter with 20% and 30 days is ignored.
---
# Demo

A primary move lasts at least a year 【literature-disputed】, see R-002.
The 3/8 retracement is cited by Dow 【literature-consensus】 (R-001).
The line band is 2% wide 【agent-defined】; this holds for 5 days R-020.
Rules held in 12 months of backtest results.
Data label 【data-confirmed】 shows 55% hit rate.
Released 2026-11-08 with 43 notes and 204 tests; Hamilton wrote in 1922.
See research/sources/x-3days.md and https://example.com/a/3 for details.
Set `min_sessions` to 15 sessions. Use --window 20 days for config.
Plain prose with no figures.

```bash
dow classify --days 30 --pct 5%
```

| Example | Output |
|---|---|
| run | 20% over 30 days |

| rule | figure |
|---|---|
| R-004 | 25 months |
