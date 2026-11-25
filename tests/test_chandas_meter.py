"""H6257: chandas scanner selftest (offline — no DCS CoNLL-U needed).

The heavy evidence (--validate, --canary, --corpus) needs the local DCS
CoNLL-U tree and runs in reports/chandas_corpus_profile_2026-11-16.md; the
scanner's hand-counted syllable/guru checks and the prose negative control
run here on every test pass.
"""

from __future__ import annotations

import subprocess
import sys

from conftest import REPO_ROOT


def test_chandas_selftest_passes() -> None:
    proc = subprocess.run(
        [sys.executable, str(REPO_ROOT / "scripts/chandas_meter.py"), "--selftest"],
        capture_output=True,
        text=True,
        check=False,
    )
    assert proc.returncode == 0, proc.stdout + proc.stderr
    assert "selftest: PASS" in proc.stdout


def test_meter_table_is_pinned_vrtta_family() -> None:
    import sys as _sys

    _sys.path.insert(0, str(REPO_ROOT / "scripts"))
    import chandas_meter as cm

    assert cm.METER_TABLE[32] == "anustubh/sloka (4x8)"
    assert cm.METER_TABLE[44] == "tristubh (4x11)"
    assert cm.classify(["yadā yadā hi dharmasya glānir bhavati bhārata"]) == (
        cm.UNCLASSIFIED
    )
