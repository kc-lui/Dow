# Dual-Axis Skill Review

- Generated at: 2026-11-08 15:27:09
- Selected skill: `dow-trend-classification`
- Skill file: `skills/dow-trend-classification/SKILL.md`
- Skill type: `execution_or_hybrid`
- Selection mode: `manual`
- Seed: `None`
- Auto score: **78 / 100**
- LLM score: `not provided`
- Final score: **78 / 100**

## Auto Score Breakdown
- metadata_use_case: 20
- workflow_coverage: 25
- execution_safety_reproducibility: 23
- supporting_artifacts: 10
- test_health: 0

## Score Weights
- auto_weight: 1.00
- llm_weight: 0.00

## Findings (Combined)
1. [AUTO|HIGH] `skills/dow-trend-classification/SKILL.md` - Skill tests failed.

## Test Verification (Auto Axis)
- Status: `failed`
- Command: `uv run --extra dev pytest /Users/lui/workspace/Dow/.claude/skills/dow-trend-classification/tests -q`

## Improvement Items (Final Score < 90)
1. Skill tests failed. -> Fix failing tests before relying on this skill in automation.
