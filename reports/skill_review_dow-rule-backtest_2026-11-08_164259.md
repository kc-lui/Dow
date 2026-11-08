# Dual-Axis Skill Review

- Generated at: 2026-11-08 16:42:59
- Selected skill: `dow-rule-backtest`
- Skill file: `skills/dow-rule-backtest/SKILL.md`
- Skill type: `execution_or_hybrid`
- Selection mode: `manual`
- Seed: `None`
- Auto score: **98 / 100**
- LLM score: **95 / 100**
- Final score: **96 / 100**

## Auto Score Breakdown
- metadata_use_case: 20
- workflow_coverage: 25
- execution_safety_reproducibility: 23
- supporting_artifacts: 10
- test_health: 20

## Score Weights
- auto_weight: 0.50
- llm_weight: 0.50

## Findings (Combined)
1. [LLM|LOW] `skills/dow-rule-backtest/SKILL.md:182` - Example 4's abbreviated output keeps the stamp from the original run (backtest_run_20261108_082330.json, runtime 3.1s) while the appended caveat line comes from a later fixture run. Both are genuine outputs and the numbers are deterministic, so nothing is wrong; the block is merely stitched from two invocations, and a reader comparing stamps with their own run may wonder why the stamp differs.

## Test Verification (Auto Axis)
- Status: `passed`
- Command: `uv run --extra dev pytest /Users/lui/workspace/Dow/.claude/skills/dow-rule-backtest/tests -q`
