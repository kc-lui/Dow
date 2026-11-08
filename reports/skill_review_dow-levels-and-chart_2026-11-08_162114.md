# Dual-Axis Skill Review

- Generated at: 2026-11-08 16:21:14
- Selected skill: `dow-levels-and-chart`
- Skill file: `skills/dow-levels-and-chart/SKILL.md`
- Skill type: `execution_or_hybrid`
- Selection mode: `manual`
- Seed: `None`
- Auto score: **98 / 100**
- LLM score: **96 / 100**
- Final score: **97 / 100**

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
1. [LLM|LOW] `skills/dow-levels-and-chart/SKILL.md:241` - The Example 3 reading says the member dates are 'read from Level.members'. That field exists on the Level dataclass but is not serialised into the JSON twin (levels rows carry only price, zone_low, zone_high, touches, as the test's LEVEL_KEYS asserts), so an operator who follows the pointer to the JSON cannot find them; they must be recovered by matching minor swings against each zone's bounds, which is how this review verified them.

## Test Verification (Auto Axis)
- Status: `passed`
- Command: `uv run --extra dev pytest /Users/lui/workspace/Dow/.claude/skills/dow-levels-and-chart/tests -q`
