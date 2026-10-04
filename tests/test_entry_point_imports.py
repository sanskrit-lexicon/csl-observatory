"""Import smoke over every repo script entry point (H5800).

Each module must import cleanly under its own interpreter environment: no
SyntaxError, no missing dependency, no module-level blow-up. This is the
load-bearing smoke layer — the repo's scripts are run one-off from CI/CLI, so
an import regression surfaces only when someone invokes them in anger.
"""
from __future__ import annotations

import importlib.util
import sys
import uuid
from pathlib import Path

import pytest
from conftest import REPO_ROOT, script_files

# Named import-smoke skips with reasons (H5800). Everything NOT listed here is
# expected to import cleanly on Linux CI. Skips here are census facts, not
# empty-fixture green: the module genuinely cannot import off its author box.
IMPORT_SKIP = {
    # Loads C:/Windows/Fonts georgiab.ttf/arial.ttf at module level (a
    # Windows-authoring-box helper for the site's social card). Unimportable
    # on Linux CI without refactoring product code — out of H5800 scope.
    "observatory/site/scripts/make_social_card.py": "hardcodes C:/Windows/Fonts module-level (Windows-only helper)",
    # WRITES observatory/site/src/sitemap.xml as a module-level side effect —
    # importing it dirties the checkout (H5800 found this live). Import-smoke
    # must stay side-effect-free, so this stays skipped until the writer is
    # moved under main().
    "observatory/site/scripts/make_sitemap.py": "writes sitemap.xml at import (module-level side effect, H5800 finding)",
}


def _import_module(path: Path, idx: int):
    name = f"smoke_import_{idx}_{uuid.uuid4().hex[:8]}"
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None, f"no import spec for {path}"
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module  # sibling imports (`import pyfloor` etc.) resolve
    spec.loader.exec_module(module)
    return module


# Discovery happens ONCE at module level — the same list feeds args, ids and
# the census floor, so pytest can never mis-parametrize against a divergent
# re-discovery (verifier finding F4, H5800 round 1).
SCRIPTS = script_files()


@pytest.mark.parametrize(
    "path", SCRIPTS, ids=[str(p.relative_to(REPO_ROOT)) for p in SCRIPTS]
)
def test_script_imports_cleanly(path):
    rel = str(path.relative_to(REPO_ROOT))
    if rel in IMPORT_SKIP:
        pytest.skip(f"named skip: {IMPORT_SKIP[rel]}")
    module = _import_module(path, SCRIPTS.index(path))
    assert module is not None


def test_smoke_census_is_not_empty():
    """The suite must stay honest: if discovery breaks and finds nothing, fail."""
    assert len(SCRIPTS) >= 90, (
        f"import-smoke discovery found only {len(SCRIPTS)} scripts — "
        "the census at H5800 was ~99; discovery is broken"
    )


def test_named_skips_still_exist():
    """A named skip must point at a real file — dead skip entries rot silently."""
    all_rel = {str(p.relative_to(REPO_ROOT)) for p in SCRIPTS}
    for rel in IMPORT_SKIP:
        assert rel in all_rel, f"IMPORT_SKIP entry {rel} no longer exists — drop it"
