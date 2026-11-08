# LLM Skill Review Request

Please perform a deep review of the following skill, including:
- SKILL.md instruction quality and consistency
- helper scripts for correctness/risk
- tests and coverage gaps
- practical usability for operators

## Skill
- Name: `dow-levels-and-chart`
- SKILL.md: `skills/dow-levels-and-chart/SKILL.md`

## Files to inspect
- Scripts:
  - `skills/dow-levels-and-chart/scripts/_anchor.py`
  - `skills/dow-levels-and-chart/scripts/draw.py`
- Tests:
  - `skills/dow-levels-and-chart/tests/test_cli.py`
- References:
  - `skills/dow-levels-and-chart/references/evidence.md`

## Auto-axis baseline (for reference only; verify independently)
- Auto score: 98/100
- Auto findings:
  - none

## Output format (strict JSON only)
```json
{
  "score": 0,
  "summary": "one-paragraph overall assessment",
  "findings": [
    {
      "severity": "high|medium|low",
      "path": "skills/.../file.ext",
      "line": 0,
      "message": "problem statement",
      "improvement": "concrete fix"
    }
  ]
}
```

Scoring rule: 0-100. If score < 90, include concrete improvements.
