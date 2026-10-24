"""obst-bench v1 — scorer arithmetic and frozen-split canary (H7124).

The metric fixtures live in ``scripts/obst_bench.py --selftest`` (so a third
party can run them without pytest); this module guards the two properties a
benchmark must not lose silently:

* the selftest exits 0, and
* the committed split digests and the committed baseline numbers reproduce
  from the pinned E32 CSV (``obst_bench.py check``).

``check`` rebuilds the split from the 62 MB release, so it is a slow test; it
is skipped when the release CSV is a Git-LFS pointer (CI without ``lfs:
true``) or absent.
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = REPO_ROOT / "scripts" / "obst_bench.py"
RELEASE = REPO_ROOT / "observatory" / "site" / "src" / "data" / "correction_events_release.csv"
LFS_MAGIC = b"version https://git-lfs.github.com/spec/v1"


def _run(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, str(SCRIPT), *args],
                          cwd=REPO_ROOT, capture_output=True, text=True)


def test_selftest_exits_zero():
    proc = _run("selftest")
    assert proc.returncode == 0, proc.stdout + proc.stderr
    assert "checks passed" in proc.stdout


def test_frozen_split_files_exist():
    bench = REPO_ROOT / "obst-bench" / "v1"
    for rel in ("SPLITS.json", "README.md",
                "detection/train.tsv", "detection/dev.tsv", "detection/test.tsv",
                "location/train.tsv", "location/test.tsv",
                "scoring_only/detection_test_gold.tsv",
                "scoring_only/location_test_gold.tsv",
                "baselines/b1_charlm_detection.predictions.tsv",
                "baselines/b1_charlm_detection.scores.json",
                "baselines/b2_majority_location.predictions.tsv",
                "baselines/b2_majority_location.scores.json"):
        assert (bench / rel).is_file(), f'missing obst-bench/v1/{rel}'


def test_test_inputs_carry_no_gold():
    """The submission inputs must not leak the label: detection test columns are
    pair_id/event_id/date/form_a/form_b and location test has no gold column."""
    bench = REPO_ROOT / "obst-bench" / "v1"
    det = (bench / "detection" / "test.tsv").read_text(encoding="utf-8").splitlines()[0]
    loc = (bench / "location" / "test.tsv").read_text(encoding="utf-8").splitlines()[0]
    assert det.split("\t") == ["pair_id", "event_id", "date", "form_a", "form_b"]
    assert loc.split("\t") == ["row_id", "event_id", "date", "features"]


@pytest.mark.skipif(not RELEASE.is_file(), reason="E32 release CSV not present")
def test_check_reproduces_digests_and_baselines():
    head = RELEASE.open("rb").read(64)
    if head.startswith(LFS_MAGIC):
        pytest.skip("E32 release CSV is a Git-LFS pointer (run `git lfs pull`)")
    proc = _run("check")
    assert proc.returncode == 0, proc.stdout + proc.stderr
    assert "ALL PASS" in proc.stdout
