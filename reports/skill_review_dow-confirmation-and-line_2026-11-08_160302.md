# Dual-Axis Skill Review

- Generated at: 2026-11-08 16:03:02
- Selected skill: `dow-confirmation-and-line`
- Skill file: `skills/dow-confirmation-and-line/SKILL.md`
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
1. [LLM|LOW] `skills/dow-confirmation-and-line/references/evidence.md:61` - The Hamilton 1914 paraphrase (66 and 71 trading days with 3 and 4 point ranges) is filed under `R-024` only; the point ranges belong to the band-percent row `R-023`, where SKILL.md Step 4 cites them (registry section 2.3), while the day counts belong to `R-024` (section 2.4).

## Test Verification (Auto Axis)
- Status: `passed`
- Command: `uv run --extra dev pytest /Users/lui/workspace/Dow/.claude/skills/dow-confirmation-and-line/tests -q`
