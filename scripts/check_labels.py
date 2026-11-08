#!/usr/bin/env python3
"""Verify that quantitative rule statements in skills and agents carry a status label.

A sentence (split on '.', ';', newline; a table row counts as one sentence) with a
number in a rule context (number + %, percent, days, sessions, weeks, months, years,
bars, points, /3, /8; or a number together with Sharpe, alpha, beta) must contain one of
the literature labels or a rule id ``R-0nn``. A sentence mentioning ``backtest`` or a
``data-`` label needs nothing more.

Also checked: every ``R-0nn`` exists in ``research/canonical_rules.md``, and a
``literature-*`` label in the same sentence as an ``R-0nn`` matches the registry label
for that id (consensus, disputed, single-source, agent-defined).

Exempt: YAML frontmatter, code fences, inline code, tables headed Example/Command,
ISO dates, paths and URLs, bare years, and numbers directly after a config key
(snake_case name, ``--flag``, or the words config/default/parameter).

Usage: check_labels.py [--root DIR] [paths...]
Exit 0 and ``ALL CLEAN`` when clean, exit 1 with a violation table otherwise.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _mdlint import (
    PROJECT_ROOT,
    Violation,
    blank_inline_code,
    expand_paths,
    prose_lines,
    render,
)

DEFAULT_GLOBS = [".claude/skills/**/SKILL.md", ".claude/agents/*.md"]
LABELS = ("literature-consensus", "literature-disputed", "single-source", "agent-defined")
LABEL_RE = re.compile(r"【(literature-consensus|literature-disputed|single-source|agent-defined)】")
RULE_ID_RE = re.compile(r"\bR-0\d\d\b")
_UNITS = r"(?:%|\s*percent\b|\s*(?:days?|sessions?|weeks?|months?|years?|bars?|points?)\b)"
_QUANT = re.compile(rf"(?<![\w.])\d+(?:\.\d+)?{_UNITS}|(?<![\w.])\d+\s*/\s*[38]\b", re.IGNORECASE)
_METRIC = re.compile(r"\b(?:Sharpe|alpha|beta)\b", re.IGNORECASE)
_DIGIT = re.compile(r"(?<![\w.])\d+(?:\.\d+)?")
_ISO_DATE = re.compile(r"\b\d{4}-\d{2}-\d{2}\b")
_URL = re.compile(r"https?://\S+")
_PATH = re.compile(r"[\w.\-]*[A-Za-z_][\w.\-]*/[\w./\-]+")
_CONFIG_BEFORE = re.compile(
    r"(?:\b[a-z]+_[a-z_0-9]+|--[\w-]+|\b(?:config|default|parameter|setting)s?)"
    r"(?:\W{0,6}|\s+(?:to|of|is|at|=)\s+)$",
    re.IGNORECASE,
)
_EXEMPT_HEADER = re.compile(r"^\s*(?:example|command)", re.IGNORECASE)
_SPLIT = re.compile(r"\.(?=\s|$)|;")
_CTX_OK = re.compile(r"backtest|data-", re.IGNORECASE)

_REGISTRY_ROW = re.compile(r"^\|\s*(R-0\d\d)\s*\|")


def load_registry(root: Path) -> dict[str, str]:
    """Map rule id -> normalised label from the canonical_rules.md registry."""
    path = root / "research" / "canonical_rules.md"
    if not path.is_file():
        raise FileNotFoundError(f"registry not found: {path}")
    reg: dict[str, str] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        m = _REGISTRY_ROW.match(line)
        if not m:
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) < 7:
            continue
        cell = cells[6].lower()
        for key in ("consensus", "disputed", "single-source", "agent-defined"):
            if cell.startswith(key):
                reg[m.group(1)] = key if key in LABELS else f"literature-{key}"
                break
        else:
            reg[m.group(1)] = cell
    return reg


_KEY_CODE = re.compile(r"`((?:--[\w-]+)|(?:[a-z]+_[a-z_0-9]+))`")


def blank_code_keep_keys(line: str) -> str:
    """Blank inline code, but keep config keys (snake_case, --flag) visible."""
    line = _KEY_CODE.sub(lambda m: m.group(1), line)
    return blank_inline_code(line)


def _scrub(text: str) -> str:
    """Remove dates, URLs and paths so they cannot look like rule quantities."""
    for pat in (_URL, _ISO_DATE, _PATH):
        text = pat.sub(" ", text)
    return text


def has_rule_quantity(text: str) -> bool:
    """True when text holds a number in a rule context that is not a config value."""
    text = _scrub(text)
    for m in _QUANT.finditer(text):
        if not _CONFIG_BEFORE.search(text[: m.start()]):
            return True
    if _METRIC.search(text):
        return any(not _CONFIG_BEFORE.search(text[: m.start()]) for m in _DIGIT.finditer(text))
    return False


def sentences(path: Path) -> list[tuple[int, str, str]]:
    """Yield (line, sentence-with-inline-code, sentence-without-inline-code)."""
    out: list[tuple[int, str, str]] = []
    skip_table = False
    prev_table = False
    for no, raw in prose_lines(path.read_text(encoding="utf-8"), skip_frontmatter=True):
        is_row = raw.lstrip().startswith("|")
        if is_row and not prev_table:
            skip_table = any(_EXEMPT_HEADER.match(c) for c in raw.strip().strip("|").split("|"))
        prev_table = is_row
        if is_row:
            if not skip_table:
                out.append((no, raw, blank_code_keep_keys(raw)))
            continue
        for part in _SPLIT.split(raw):
            if part.strip():
                out.append((no, part, blank_code_keep_keys(part)))
    return out


def check_file(path: Path, registry: dict[str, str]) -> list[Violation]:
    """Lint one markdown file."""
    out: list[Violation] = []
    for no, full, bare in sentences(path):
        ids = sorted(set(RULE_ID_RE.findall(full)))
        labels = LABEL_RE.findall(full)
        for rid in ids:
            if rid not in registry:
                out.append(
                    Violation(path, no, "unknown-rule-id", f"{rid} not in canonical_rules.md")
                )
        known = {registry[r] for r in ids if r in registry}
        for lab in labels:
            if lab.startswith("literature-") and known and lab not in known:
                out.append(
                    Violation(
                        path,
                        no,
                        "label-mismatch",
                        f"{lab} vs registry {', '.join(sorted(known))} for {', '.join(ids)}",
                    )
                )
        if has_rule_quantity(bare) and not (labels or ids or _CTX_OK.search(full)):
            snippet = " ".join(bare.split())
            snippet = snippet if len(snippet) <= 90 else snippet[:87] + "..."
            out.append(Violation(path, no, "unlabelled-quantity", snippet))
    return out


def main(argv: list[str] | None = None) -> int:
    """CLI entry point."""
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("paths", nargs="*")
    ap.add_argument("--root", type=Path, default=PROJECT_ROOT, help="project root")
    args = ap.parse_args(argv)
    root = args.root.resolve()
    registry = load_registry(root)
    violations: list[Violation] = []
    for path in expand_paths(root, args.paths, DEFAULT_GLOBS):
        violations += check_file(path, registry)
    if violations:
        print(render(violations, root))
        print(f"\n{len(violations)} violation(s)")
        return 1
    print("ALL CLEAN")
    return 0


if __name__ == "__main__":
    sys.exit(main())
