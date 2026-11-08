"""Shared helpers for the markdown lint scripts (check_quotes, check_labels)."""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent

_FENCE = re.compile(r"^\s*(```|~~~)")
_INLINE_CODE = re.compile(r"`[^`\n]*`")


@dataclass(frozen=True)
class Violation:
    """One lint finding."""

    path: Path
    line: int
    kind: str
    detail: str


def expand_paths(root: Path, args: list[str], defaults: list[str]) -> list[Path]:
    """Resolve CLI paths (files, directories, globs) or the default globs under root."""
    if not args:
        found = {p for pattern in defaults for p in root.glob(pattern) if p.is_file()}
        return sorted(found)
    out: set[Path] = set()
    for arg in args:
        p = Path(arg)
        if not p.is_absolute():
            p = Path.cwd() / p
        if p.is_dir():
            out.update(q for q in p.rglob("*.md") if q.is_file())
        elif p.is_file():
            out.add(p)
        else:
            raise FileNotFoundError(f"path not found: {arg}")
    return sorted(out)


def prose_lines(text: str, *, skip_frontmatter: bool) -> list[tuple[int, str]]:
    """Return (1-based line number, text) for lines outside code fences.

    Fenced blocks are dropped entirely. YAML frontmatter is dropped when asked.
    """
    lines = text.splitlines()
    out: list[tuple[int, str]] = []
    start = 0
    if skip_frontmatter and lines and lines[0].strip() == "---":
        for i in range(1, len(lines)):
            if lines[i].strip() == "---":
                start = i + 1
                break
    in_fence = False
    for i in range(start, len(lines)):
        if _FENCE.match(lines[i]):
            in_fence = not in_fence
            continue
        if not in_fence:
            out.append((i + 1, lines[i]))
    return out


def blank_inline_code(line: str) -> str:
    """Replace inline code spans by spaces, preserving column positions."""
    return _INLINE_CODE.sub(lambda m: " " * len(m.group(0)), line)


def render(violations: list[Violation], root: Path) -> str:
    """Format violations as an aligned table with file:line locations."""
    rows = []
    for v in violations:
        try:
            shown = v.path.relative_to(root)
        except ValueError:
            shown = v.path
        rows.append((f"{shown}:{v.line}", v.kind, v.detail))
    head = ("location", "kind", "detail")
    widths = [max(len(r[i]) for r in [head, *rows]) for i in range(2)]
    fmt = f"{{:<{widths[0]}}}  {{:<{widths[1]}}}  {{}}"
    lines = [fmt.format(*head), fmt.format("-" * widths[0], "-" * widths[1], "-" * 6)]
    lines += [fmt.format(*r) for r in rows]
    return "\n".join(lines)
