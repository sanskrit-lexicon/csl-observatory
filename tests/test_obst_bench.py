"""obst-bench v1 — scorer arithmetic and frozen-split canary (H7124).

The metric fixtures live in ``scripts/obst_bench.py selftest`` (so a third
party can run them without pytest); this module guards the three properties a
benchmark must not lose silently:

* the selftest exits 0 (both spellings: ``selftest`` and ``--selftest``),
* the test inputs publish no label and no release foreign key, and
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
TAB = "\t"


def _run(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, str(SCRIPT), *args],
                          cwd=REPO_ROOT, capture_output=True, text=True)


def test_selftest_exits_zero_both_spellings():
    for args in (("selftest",), ("--selftest",)):
        proc = _run(*args)
        assert proc.returncode == 0, (args, proc.stdout + proc.stderr)
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


def test_test_inputs_carry_no_gold_and_no_event_id():
    """The submission inputs publish no label column and no ``event_id``: the id
    is a foreign key into the public E32 CSV, so shipping it would hand a reader
    the gold by a single lookup (H7124 verifier finding). Every data row must be
    exactly as wide as its header — a gold field appended to the rows would
    otherwise slip past a header-only check."""
    bench = REPO_ROOT / "obst-bench" / "v1"
    det_lines = (bench / "detection" / "test.tsv").read_text(encoding="utf-8").splitlines()
    loc_lines = (bench / "location" / "test.tsv").read_text(encoding="utf-8").splitlines()

    assert det_lines[0].split(TAB) == ["pair_id", "date", "form_a", "form_b"]
    assert loc_lines[0].split(TAB) == ["row_id", "date", "features"]
    for header in (det_lines[0], loc_lines[0]):
        assert "event_id" not in header
        assert "gold" not in header

    for name, lines in (("detection", det_lines), ("location", loc_lines)):
        width = len(lines[0].split(TAB))
        wrong = [i for i, line in enumerate(lines[1:], 2) if len(line.split(TAB)) != width]
        assert not wrong, f"obst-bench/v1/{name}/test.tsv rows of wrong width: {wrong[:5]}"


def test_split_ids_are_prefixed_per_split():
    """A bare D00001 / L00001 repeats in every split file and would let an entrant
    silently cross-join train onto test."""
    bench = REPO_ROOT / "obst-bench" / "v1"
    for rel, prefix in (("detection/train.tsv", "DTR"), ("detection/dev.tsv", "DDV"),
                        ("detection/test.tsv", "DTE"), ("location/train.tsv", "LTR"),
                        ("location/test.tsv", "LTE")):
        first = (bench / rel).read_text(encoding="utf-8").splitlines()[1].split(TAB)[0]
        assert first.startswith(prefix), f"{rel}: first id {first!r} lacks prefix {prefix}"


@pytest.mark.skipif(not RELEASE.is_file(), reason="E32 release CSV not present")
def test_check_reproduces_digests_and_baselines():
    head = RELEASE.open("rb").read(64)
    if head.startswith(LFS_MAGIC):
        pytest.skip("E32 release CSV is a Git-LFS pointer (run `git lfs pull`)")
    proc = _run("check")
    assert proc.returncode == 0, proc.stdout + proc.stderr
    assert "ALL PASS" in proc.stdout
