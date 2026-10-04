"""Unit smoke over the shared pure helpers (H5800).

Real assertions on the two helper modules nearly every script imports — not
empty-fixture green: wrong behaviour must actually fail these.
"""
from __future__ import annotations

import sys

from conftest import REPO_ROOT

sys.path.insert(0, str(REPO_ROOT / "scripts"))

import _common  # noqa: E402
import pyfloor  # noqa: E402

# --- pyfloor: declared interpreter floor (H3541) -----------------------------

def test_pyfloor_floor_is_declared_and_sane():
    assert pyfloor.FLOOR >= (3, 9), "the declared floor moved below the H3541 floor"
    assert pyfloor.FLOOR_STR == ".".join(map(str, pyfloor.FLOOR))


def test_pyfloor_satisfied_verdicts():
    assert pyfloor.satisfied((3, 13)) is True
    assert pyfloor.satisfied(sys.version_info[:2]) is True
    assert pyfloor.satisfied((3, 8)) is False


def test_pyfloor_write_read_roundtrip_preserves_newlines(tmp_path):
    p = tmp_path / "roundtrip.txt"
    body = "a\r\nb\r\nc\r\n"
    pyfloor.write_text(p, body, newline="\n")
    assert pyfloor.read_text(p, newline="") == body, (
        "pyfloor.write_text/read_text must preserve line endings byte-for-byte "
        "(the F3541 CRLF-protection contract)"
    )


# --- _common: subprocess/git plumbing ----------------------------------------

def test_common_run_captures_utf8_output():
    proc = _common.run([sys.executable, "-c", "print('héllo ✓')"])
    assert proc.returncode == 0
    assert "héllo ✓" in proc.stdout


def test_common_git_helper_runs_real_git():
    proc = _common.git(REPO_ROOT, "rev-parse", "--abbrev-ref", "HEAD")
    assert proc.returncode == 0
    assert proc.stdout.strip(), "git rev-parse returned no branch name"


def test_common_repo_root_points_here():
    assert (_common.repo_root() / "AGENTS.md").exists(), (
        "_common.repo_root() must resolve to the csl-observatory checkout"
    )
