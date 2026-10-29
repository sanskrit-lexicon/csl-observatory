"""Unit smoke over the shared pure helpers (H5800).

Real assertions on the two helper modules nearly every script imports — not
empty-fixture green: wrong behaviour must actually fail these.
"""
from __future__ import annotations

import io
import sys
from unittest import mock

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
    # A bare \n next to a literal \r\n: on a platform whose os.linesep is \r\n
    # a translating write turns the bare \n into \r\n, so the byte assertion
    # fails unless write_text passes newline="\n" (H7108, bughunt §15 — the
    # old all-CRLF body round-tripped identically with and without the kwarg).
    body = "a\r\nb\nc\r\n"
    pyfloor.write_text(p, body, newline="\n")
    assert p.read_bytes() == b"a\r\nb\nc\r\n", (
        "pyfloor.write_text must not translate line endings"
    )
    assert pyfloor.read_text(p, newline="") == body, (
        "pyfloor.write_text/read_text must preserve line endings byte-for-byte "
        "(the F3541 CRLF-protection contract)"
    )


def test_pyfloor_write_text_passes_newline_kwarg(tmp_path):
    """Platform-independent pin for the same contract: the kwarg must reach io.open."""
    p = tmp_path / "kwarg.txt"
    seen: dict = {}
    real_open = io.open

    def spy(*args, **kwargs):
        seen.update(kwargs)
        return real_open(*args, **kwargs)

    with mock.patch("io.open", side_effect=spy):
        pyfloor.write_text(p, "a\r\nb\n", newline="")
    assert seen.get("newline") == "", (
        "pyfloor.write_text dropped the newline= kwarg (F3541 CRLF contract)"
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
