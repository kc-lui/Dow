# Dual-Axis Skill Review

- Generated at: 2026-11-08 14:45:10
- Selected skill: `dow-theory-sources`
- Skill file: `skills/dow-theory-sources/SKILL.md`
- Skill type: `knowledge_only`
- Selection mode: `manual`
- Seed: `None`
- Auto score: **83 / 100**
- LLM score: **93 / 100**
- Final score: **90 / 100**

## Auto Score Breakdown
- metadata_use_case: 20
- workflow_coverage: 25
- execution_safety_reproducibility: 17
- supporting_artifacts: 9
- test_health: 12

## Score Weights
- auto_weight: 0.35
- llm_weight: 0.65

## Findings (Combined)
1. [LLM|LOW] `skills/dow-theory-sources/references/evidence.md:196` - Section 8 'Rule ids cited' lists R-011 then R-013 and omits R-012, but SKILL.md Step 3 cites R-012 in the Schannep retracement row ('Schannep (`R-012`) ... 【single-source】') and evidence.md itself tags two rows with R-012. Contract item 8 requires evidence.md to list every rule id used in SKILL.md.
2. [LLM|LOW] `skills/dow-theory-sources/SKILL.md:147` - Step 3 (Dow on averages row) now records the origin of two-average confirmation as 【literature-disputed】on origin only (thismatter-dow-theory:Q10 against russell Q4 and the nelson note). Step 4 row 'Confirmation | Hamilton 1922 | first-hand; not Dow | 【literature-consensus】' and the Example 2 verdict 'but its author is Hamilton' state the origin flatly, so the three passages read differently on the same question. The registry R-032 statement says Hamilton first defined it and lists thismatter as origin-only dissent, so the skill is not wrong, but the contract's side-by-side rule means the dissent should travel with the claim wherever it is stated.
3. [LLM|LOW] `skills/dow-theory-sources/SKILL.md` - Out of scope for the skill score (project lead task, carried from round 3): analysis/skill_boundary_ledger.md still has no entry for dow-theory-sources (grep for 'theory-sources' and 'glossary' returns nothing), so the DRY ownership of glossary, labels, provenance and performance evidence claimed in Boundaries is not recorded where siblings look for it.

## Test Verification (Auto Axis)
- Status: `not_applicable`
- Command: `None`
