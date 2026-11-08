# LLM Skill Review Request

Please perform a deep review of the following skill, including:
- SKILL.md instruction quality and consistency
- helper scripts for correctness/risk
- tests and coverage gaps
- practical usability for operators

## Skill
- Name: `dow-theory-sources`
- SKILL.md: `skills/dow-theory-sources/SKILL.md`

## Files to inspect
- Scripts:
  - (none)
- Tests:
  - (none)
- References:
  - `skills/dow-theory-sources/references/evidence.md`

## Auto-axis baseline (for reference only; verify independently)
- Auto score: 63/100
- Auto findings:
  - [high] Frontmatter is missing or malformed.
  - [high] Frontmatter `name` is missing.

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
