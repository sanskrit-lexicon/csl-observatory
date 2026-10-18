"""Shared fixtures for the H5800 smoke suite.

Scaffolded by H5800 (csl-observatory smoke-test bootstrap): the repo had zero
tests; this suite smoke-tests the main script entry points (import + --help)
plus a handful of pure helpers.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]

# Directories holding script entry points / importable modules.
SCRIPT_DIRS = [
    REPO_ROOT / "scripts",
    REPO_ROOT / "observatory",
    REPO_ROOT / "tools",
    REPO_ROOT / "validation",
    REPO_ROOT / "observatory" / "site" / "scripts",
]

# Observable Framework data loaders (observatory/site/src/data/*.csv.py) EXECUTE
# at import — they read data/snapshots/ and write CSV rows to stdout as a module
# side effect. They are page-data loaders, not script entry points, and are
# deliberately excluded from import smoke.
EXCLUDED = [
    REPO_ROOT / "observatory" / "site" / "src" / "data",
]


def script_files() -> list[Path]:
    """Every repo .py script eligible for import smoke, sorted and deduped."""
    files: list[Path] = []
    for d in SCRIPT_DIRS:
        files.extend(p for p in d.glob("*.py") if p.is_file())
    return sorted({f for f in files if not any(f.is_relative_to(x) for x in EXCLUDED)})


@pytest.fixture(scope="session", autouse=True)
def _script_dirs_on_path():
    for d in SCRIPT_DIRS:
        if str(d) not in sys.path:
            sys.path.insert(0, str(d))
    yield
