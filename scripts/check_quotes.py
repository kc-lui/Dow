#!/usr/bin/env python3
"""Verify that every quoted span of 4+ words is a cited, verbatim source quote.

A double-quoted span ("..." straight or curly) with at least 4 words must be followed
on the same line by ``(slug:Qn)`` or ``(slug:Qn, slug:Qm)``. Each slug must exist as
``research/sources/<slug>.md`` and the span must be a substring of the cited ``Qn`` line
(curly quotes, dashes and whitespace normalised; case-sensitive).

Exempt: code fences, inline code, phrases listed in ``research/quote_whitelist.txt``,
and spans under 4 words.

``research/canonical_rules.md`` is deliberately not in the default scan. It is a
synthesis table whose cells quote short paraphrased phrases and cite source ids in a
different notation (``slug:Q1,Q3``). It is still checkable by passing it explicitly.

Usage: check_quotes.py [--root DIR] [paths...]
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

DEFAULT_GLOBS = [
    ".claude/skills/**/SKILL.md",
    ".claude/skills/**/references/*.md",
    ".claude/agents/*.md",
    # analysis/agent_verification_sample.md holds verbatim agent transcripts graded by R17; excluded from the default scan
]
MIN_WORDS = 4

_SPAN = re.compile(r'"([^"\n]+)"|“([^”\n]+)”')
_CITE = re.compile(r"^\s*\(\s*([a-z0-9][a-z0-9\-]*:Q\d+(?:\s*,\s*[a-z0-9][a-z0-9\-]*:Q\d+)*)\s*\)")
_QLINE = re.compile(r"^\s*-\s*Q(\d+):\s*(.*)$")
_DASHES = dict.fromkeys(map(ord, "‐‑‒–—―−"), "-")
_QUOTES = {ord(c): '"' for c in "“”„‟«»"} | {ord(c): "'" for c in "‘’‚‛"}


def normalise(text: str) -> str:
    """Unify quotes, dashes and whitespace so verbatim comparison is robust."""
    text = text.translate(_DASHES).translate(_QUOTES)
    return re.sub(r"\s+", " ", text).strip()


def load_whitelist(root: Path) -> set[str]:
    """Read allowed non-quote phrases (one per line, # comments)."""
    path = root / "research" / "quote_whitelist.txt"
    if not path.is_file():
        return set()
    return {
        normalise(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.lstrip().startswith("#")
    }


class SourceIndex:
    """Lazy loader of ``Qn`` lines from source notes."""

    def __init__(self, root: Path) -> None:
        self._dir = root / "research" / "sources"
        self._cache: dict[str, dict[int, str] | None] = {}

    def quotes(self, slug: str) -> dict[int, str] | None:
        """Return {n: normalised quote line text} or None when the note is missing."""
        if slug not in self._cache:
            path = self._dir / f"{slug}.md"
            if not path.is_file():
                self._cache[slug] = None
            else:
                found: dict[int, str] = {}
                for line in path.read_text(encoding="utf-8").splitlines():
                    m = _QLINE.match(line)
                    if m:
                        found[int(m.group(1))] = normalise(m.group(2))
                self._cache[slug] = found
        return self._cache[slug]


def _check_span(span: str, cite: str, sources: SourceIndex) -> str | None:
    """Return an error message, or None when the span is verbatim in a cited Qn."""
    needle = normalise(span).rstrip(".,;:!?").strip()
    refs = [c.strip() for c in cite.split(",")]
    missing: list[str] = []
    for ref in refs:
        slug, qid = ref.split(":Q")
        qs = sources.quotes(slug)
        if qs is None:
            return f"unknown source slug '{slug}' (no research/sources/{slug}.md)"
        text = qs.get(int(qid))
        if text is None:
            missing.append(ref)
        elif needle in text:
            return None
    if missing and len(missing) == len(refs):
        return f"cited quote id not found: {', '.join(missing)}"
    return f"text is not a verbatim substring of {', '.join(refs)}"


def check_file(path: Path, sources: SourceIndex, whitelist: set[str]) -> list[Violation]:
    """Lint one markdown file."""
    out: list[Violation] = []
    text = path.read_text(encoding="utf-8")
    for no, raw in prose_lines(text, skip_frontmatter=False):
        line = blank_inline_code(raw)
        for m in _SPAN.finditer(line):
            span = m.group(1) or m.group(2)
            if len(span.split()) < MIN_WORDS or normalise(span) in whitelist:
                continue
            cite = _CITE.match(line[m.end() :])
            shown = span if len(span) <= 60 else span[:57] + "..."
            if not cite:
                out.append(Violation(path, no, "no-citation", f'"{shown}"'))
                continue
            err = _check_span(span, cite.group(1), sources)
            if err:
                out.append(Violation(path, no, "bad-quote", f'"{shown}" {err}'))
    return out


def main(argv: list[str] | None = None) -> int:
    """CLI entry point."""
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("paths", nargs="*")
    ap.add_argument("--root", type=Path, default=PROJECT_ROOT, help="project root")
    args = ap.parse_args(argv)
    root = args.root.resolve()
    sources, whitelist = SourceIndex(root), load_whitelist(root)
    violations: list[Violation] = []
    for path in expand_paths(root, args.paths, DEFAULT_GLOBS):
        violations += check_file(path, sources, whitelist)
    if violations:
        print(render(violations, root))
        print(f"\n{len(violations)} violation(s)")
        return 1
    print("ALL CLEAN")
    return 0


if __name__ == "__main__":
    sys.exit(main())
