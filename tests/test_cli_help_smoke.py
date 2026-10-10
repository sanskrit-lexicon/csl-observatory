"""CLI smoke: argparse entry points must answer --help with exit 0.

Argparse exits before main() runs, so this exercises argument wiring without
touching the network, the git org, or data refreshes.
"""
from __future__ import annotations

import subprocess
import sys

import pytest
from conftest import REPO_ROOT

# Argparse-confirmed, offline-at---help entry points (H5800 live census 03-10).
HELP_SMOKE_TARGETS = [
    "scripts/data_index.py",
    "scripts/eol_census.py",
    "scripts/envelope_check.py",
    "scripts/encoding_xml_guard.py",
    "scripts/code_duplication_census.py",
    "scripts/dict_runbook.py",
    "scripts/pre_push_stale_base_check.py",
    "scripts/workflow_health.py",
    "scripts/citation_sweep.py",
    "scripts/repo_metadata_snapshot.py",
    "scripts/tooling_runbook.py",
    "scripts/lowm_estimators.py",
]


@pytest.mark.parametrize(
    "rel", HELP_SMOKE_TARGETS, ids=[t.rsplit("/", 1)[-1] for t in HELP_SMOKE_TARGETS]
)
def test_cli_help_exits_zero(rel):
    proc = subprocess.run(
        [sys.executable, str(REPO_ROOT / rel), "--help"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        timeout=90,
    )
    assert proc.returncode == 0, (
        f"{rel} --help exited {proc.returncode}\nstdout:\n{proc.stdout[-1000:]}\n"
        f"stderr:\n{proc.stderr[-1000:]}"
    )
    assert "usage" in (proc.stdout or "").lower(), (
        f"{rel} --help produced no usage text:\n{proc.stdout[-500:]}"
    )
