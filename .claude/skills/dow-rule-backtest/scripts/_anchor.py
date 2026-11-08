"""Locate the Dow repository and run the calling script under its ``.venv`` interpreter.

Shared by every ``dow-*`` skill script. Resolution order: ``DOW_PROJECT_ROOT`` env, then
walk up from this file to a directory holding ``pyproject.toml`` and ``src/dowtheory``.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

ROOT_ENV = "DOW_PROJECT_ROOT"


def project_root() -> Path:
    """Return the Dow repo root or exit with a one-line setup hint."""
    env = os.environ.get(ROOT_ENV)
    if env:
        return Path(env).expanduser().resolve()
    here = Path(__file__).resolve()
    for candidate in (here, *here.parents):
        if (candidate / "pyproject.toml").is_file() and (candidate / "src" / "dowtheory").is_dir():
            return candidate
    raise SystemExit(f"Dow repo not found: export {ROOT_ENV}=<path-to-Dow-repo>")


def ensure_venv() -> Path:
    """Re-exec under ``<root>/.venv/bin/python`` when needed; make ``dowtheory`` importable."""
    root = project_root()
    venv = root / ".venv"
    python = venv / "bin" / "python"
    if python.is_file() and Path(sys.prefix).resolve() != venv.resolve():
        os.environ[ROOT_ENV] = str(root)
        os.execv(str(python), [str(python), *sys.argv])
    sys.path.insert(0, str(root / "src"))
    os.environ.setdefault("DOW_CONFIG", str(root / "configs" / "dow.yaml"))
    return root
