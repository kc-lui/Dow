# Dual-Axis Skill Review

- Generated at: 2026-11-08 15:08:41
- Selected skill: `dow-swing-detection`
- Skill file: `skills/dow-swing-detection/SKILL.md`
- Skill type: `execution_or_hybrid`
- Selection mode: `manual`
- Seed: `None`
- Auto score: **98 / 100**
- LLM score: **93 / 100**
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
1. [LLM|LOW] `skills/dow-swing-detection/SKILL.md:175` - The Example 2 reading says the 2025-04-08 low became knowable on 2025-04-30, '16 sessions later'. Counting sessions in dow.mkt_klines (Good Friday 2025-04-18 closed) gives idx(2025-04-30) - idx(2025-04-08) = 15, which is exactly secondary_min_sessions; the filter was binding on that bar. The number is wrong and the more informative reading (confirmation landed on the first bar the time filter allowed) is missed.
2. [LLM|LOW] `skills/dow-swing-detection/SKILL.md:213` - Limitation 8 states 'at most 46 percent of reactions fall in the 1/3 to 2/3 band at any threshold', copied from the spec_review_p3.md judgement list, but the skill's own Step 4 table (line 86) shows 49 percent for the adopted 0.08 + 15-session filter setting. The limitation contradicts the table two sections above it.
3. [LLM|LOW] `skills/dow-swing-detection/SKILL.md:3` - The description parses to exactly 1024 characters (YAML folded scalar, measured with PyYAML). It is inside the ≤1024 contract limit but any future edit, including adding one trigger word, will push it over and break skill loading.
4. [LLM|LOW] `skills/dow-swing-detection/scripts/swings.py:32` - With --source csv and no --symbol, the symbol defaults to the upper-cased file stem. loader._load_csv then filters on a 'symbol' column when one exists, so a multi-symbol CSV named export.csv is filtered to symbol 'EXPORT', yields zero rows and fails with 'No bars for EXPORT from csv', an error that does not mention the stem default. Prerequisites item 2 describes both behaviours but not their interaction.

## Test Verification (Auto Axis)
- Status: `passed`
- Command: `uv run --extra dev pytest /Users/lui/workspace/Dow/.claude/skills/dow-swing-detection/tests -q`
