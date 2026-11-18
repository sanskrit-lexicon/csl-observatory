"""Generator-noise exemptions for the dict-audit taxonomy gate (MG ruling 18-11-2026).

The audit must ignore auto-generated detector/backlog issues (MWS #313, #327)
while still auditing genuine triaged work that merely carries a process label
(MWS #242). Real assertions — a regression here silently reddens or greens the gate.
"""
from __future__ import annotations

import sys

from conftest import REPO_ROOT

sys.path.insert(0, str(REPO_ROOT / "scripts"))

import dict_runbook  # noqa: E402


def test_generator_noise_is_exempt():
    # MWS #313 — paper-privacy detector quarantine finding (single label).
    assert dict_runbook.is_exempt(["paper-priv-violation"]) is True
    # MWS #327 — backfill mirror of the Uprava handoff backlog.
    assert dict_runbook.is_exempt(["handoff", "backfill", "ready-for-agent"]) is True
    # Pre-existing detector log class still exempt.
    assert dict_runbook.is_exempt(["daily-corrections"]) is True
    # Bare handoff execution tracker still exempt.
    assert dict_runbook.is_exempt(["handoff"]) is True


def test_genuine_triaged_work_stays_audited():
    # MWS #242 — real taxonomy labels plus a process label: must NOT be exempt.
    assert dict_runbook.is_exempt(["content-enhancement", "medium", "handoff"]) is False
    # Fully triaged issue unaffected.
    assert dict_runbook.is_exempt(["bug", "minor"]) is False
    # Unlabeled issue is not silently exempt.
    assert dict_runbook.is_exempt([]) is False
