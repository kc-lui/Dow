"""Allowlist guard for SQL sent to ClickHouse (defence in depth; the server grants are primary).

Statements are normalised first: comments removed, string literals blanked, whitespace
collapsed. Reads must start with a read keyword. Writes must match one of a few exact shapes.
Qualified ``db.table`` references are limited to ``dow`` (writes) or ``dow/usstock/twstock``
(reads). Table aliases containing a dot are only recognised when declared with ``AS``.
"""

from __future__ import annotations

import re

WRITE_DB = "dow"
READ_DBS = frozenset({"dow", "usstock", "twstock"})

_READ_START = re.compile(r"^(SELECT|WITH|SHOW|DESCRIBE|DESC|EXISTS)\b", re.IGNORECASE)
_WRITE_SHAPES = tuple(re.compile(p, re.IGNORECASE) for p in (
    r"^INSERT INTO dow\.\w+\b",
    r"^ALTER TABLE dow\.\w+ (DELETE|UPDATE)\b",
    r"^OPTIMIZE TABLE dow\.\w+\b",
    r"^CREATE TABLE IF NOT EXISTS dow\.\w+\b",
    r"^CREATE DATABASE IF NOT EXISTS dow$",
    r"^EXCHANGE TABLES dow\.\w+ AND dow\.\w+$",
))
_FORBIDDEN = re.compile(
    r"\b(DROP|TRUNCATE|RENAME|DETACH|ATTACH|TTL|GRANT|REVOKE|SYSTEM|KILL|FREEZE|MOVE)\b"
    r"|\bOR\s+REPLACE\b", re.IGNORECASE)
_QUALIFIED = re.compile(r"(?<![\w.])([A-Za-z_]\w*)\s*\.\s*([A-Za-z_]\w*)")
_ALIAS = re.compile(r"\bAS\s+([A-Za-z_]\w*)", re.IGNORECASE)


class UnsafeSQLError(RuntimeError):
    """Raised when a statement or target violates the project's write-scope rules."""


def normalize(sql: str) -> str:
    """Strip comments, blank string literals, collapse whitespace, drop one trailing ';'."""
    out: list[str] = []
    i, n = 0, len(sql)
    while i < n:
        ch = sql[i]
        if ch in "'`\"":
            j = i + 1
            while j < n:
                if sql[j] == "\\":
                    j += 2
                    continue
                if sql[j] == ch:
                    if j + 1 < n and sql[j + 1] == ch:  # doubled quote
                        j += 2
                        continue
                    break
                j += 1
            else:
                raise UnsafeSQLError("Unterminated quote in SQL")
            out.append("''" if ch == "'" else sql[i : j + 1])  # keep identifiers, blank strings
            i = j + 1
        elif sql.startswith("--", i) or ch == "#":
            j = sql.find("\n", i)
            i = n if j < 0 else j
        elif sql.startswith("/*", i):
            j = sql.find("*/", i + 2)
            if j < 0:
                raise UnsafeSQLError("Unterminated comment in SQL")
            out.append(" ")
            i = j + 2
        else:
            out.append(ch)
            i += 1
    text = re.sub(r"\s+", " ", "".join(out)).strip()
    return text[:-1].strip() if text.endswith(";") else text


def _check_common(code: str, allowed_dbs: frozenset[str], original: str) -> None:
    if ";" in code:
        raise UnsafeSQLError(f"Multiple statements are not allowed: {original[:80]!r}")
    if _FORBIDDEN.search(code):
        raise UnsafeSQLError(f"Forbidden keyword in statement: {original[:80]!r}")
    aliases = {a.lower() for a in _ALIAS.findall(code)}
    for db, _ in _QUALIFIED.findall(code):
        if db.lower() not in allowed_dbs and db.lower() not in aliases:
            raise UnsafeSQLError(f"Database '{db}' is not allowed here: {original[:80]!r}")


def check_read(sql: str) -> None:
    """Raise UnsafeSQLError unless ``sql`` is a plain read over dow/usstock/twstock."""
    code = normalize(sql)
    if not _READ_START.match(code):
        raise UnsafeSQLError(f"Only SELECT/WITH/SHOW/DESCRIBE/EXISTS reads allowed: {sql[:80]!r}")
    if re.search(r"\breadonly\b|\bINTO\s+OUTFILE\b", code, re.IGNORECASE):
        raise UnsafeSQLError(f"Read may not touch readonly/OUTFILE: {sql[:80]!r}")
    _check_common(code, READ_DBS, sql)


def check_write(sql: str) -> None:
    """Raise UnsafeSQLError unless ``sql`` is an allowlisted write confined to ``dow``."""
    code = normalize(sql)
    if not any(p.match(code) for p in _WRITE_SHAPES):
        raise UnsafeSQLError(f"Statement is not on the write allowlist: {sql[:80]!r}")
    _check_common(code, frozenset({WRITE_DB}), sql)
