#!/usr/bin/env python3
"""Ruff baseline gate (H5800).

Runs ``ruff check .`` and fails ONLY when the live violation count EXCEEDS the
documented baseline stored in ``.ruff-baseline``. The point is a documented,
moving-only-down floor at bootstrap (H5800 acceptance: "ruff starts from a
documented baseline count, not silently zero") — it is NOT a silent pass.

Usage:
    python scripts/ruff_baseline_gate.py            # gate (CI mode)
    python scripts/ruff_baseline_gate.py --refresh  # re-record the baseline

Ruff resolution order: $RUFF_BIN, ``ruff`` on PATH, ``.venv/bin/ruff``.
"""
from __future__ import annotations

import argparse
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
BASELINE_FILE = REPO_ROOT / ".ruff-baseline"
VIOLATION_RE = re.compile(r"^[^ :].+:\d+:\d+: [A-Z]+[0-9]+")


def find_ruff() -> str:
    for candidate in (os.environ.get("RUFF_BIN"), shutil.which("ruff"),
                      str(REPO_ROOT / ".venv" / "bin" / "ruff")):
        if candidate and Path(candidate).exists():
            return candidate
    return "ruff"


def count_violations(ruff_bin: str) -> tuple[int, str]:
    proc = subprocess.run(
        [ruff_bin, "check", ".", "--output-format", "concise", "--exit-zero"],
        cwd=REPO_ROOT, capture_output=True, text=True, timeout=300,
    )
    lines = [
        line for line in (proc.stdout or "").splitlines() if VIOLATION_RE.match(line)
    ]
    return len(lines), (proc.stdout or "") + (proc.stderr or "")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--refresh", action="store_true",
                    help="overwrite .ruff-baseline with the live count")
    args = ap.parse_args()

    ruff_bin = find_ruff()
    count, raw = count_violations(ruff_bin)
    # Fail closed on a broken probe: zero violations is only believable when
    # ruff itself says so — "Found 0 errors" (with violations-mode wording) or
    # "All checks passed!" (the wording ruff actually prints on a clean repo,
    # confirmed live against ruff 0.16.10). A dead/missing ruff must never
    # read as a clean repo.
    if count == 0 and not re.search(r"Found 0 errors|All checks passed", raw or ""):
        print(f"ruff_baseline_gate: ruff produced no parsable output — FAIL\n{(raw or '')[-2000:]}")
        return 2

    if args.refresh:
        BASELINE_FILE.write_text(f"{count}\n", encoding="utf-8")
        print(f"ruff_baseline_gate: baseline refreshed to {count}")
        return 0

    if not BASELINE_FILE.exists():
        print(f"ruff_baseline_gate: FAIL — {BASELINE_FILE} missing")
        return 2
    baseline = int(BASELINE_FILE.read_text(encoding="utf-8").strip())

    print(f"ruff_baseline_gate: live={count} baseline={baseline}")
    if count > baseline:
        print(
            "ruff_baseline_gate: FAIL — violations exceed the documented baseline.\n"
            "Fix the new violations, or (after review) refresh with:\n"
            "  python scripts/ruff_baseline_gate.py --refresh"
        )
        return 1
    print("ruff_baseline_gate: PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
