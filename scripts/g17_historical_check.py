#!/usr/bin/env python3
"""One-off: verify the CRLF arithmetic against the poisoned 6f573f1 baseline.

For every row of data_index.csv AS COMMITTED AT 6f573f1 (17-06-2026), compare
the recorded bytes against that same commit's blob size and blob line count.
If the G17 drift was CRLF inflation, recorded - blob == lines exactly.
"""

from __future__ import annotations

import csv
import io
import subprocess
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parents[1]
REL = "observatory/site/src/data"
COMMIT = "6f573f1"


def git(args: list[str]) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["git", "-C", str(ROOT), *args], capture_output=True, encoding="utf-8", errors="replace"
    )


def main() -> int:
    index = git(["show", f"{COMMIT}:{REL}/data_index.csv"]).stdout
    rows = list(csv.DictReader(io.StringIO(index)))
    print(f"{'file':44} {'recorded':>9} {'blob':>9} {'delta':>7} {'lines':>7} verdict")
    exact = other = 0
    for row in rows:
        name = row["file"]
        if name == "data_index.csv":
            continue
        recorded = int(row["bytes"])
        blob_proc = git(["cat-file", "-s", f"{COMMIT}:{REL}/{name}"])
        if blob_proc.returncode != 0:
            print(f"{name:44} {recorded:>9} {'ABSENT':>9}")
            continue
        blob = int(blob_proc.stdout.strip())
        content = subprocess.run(
            ["git", "-C", str(ROOT), "cat-file", "-p", f"{COMMIT}:{REL}/{name}"],
            capture_output=True,
        ).stdout
        lines = content.count(b"\n") - content.count(b"\r\n")
        delta = recorded - blob
        verdict = "crlf-exact" if delta == lines else ("match" if delta == 0 else "OTHER")
        exact += verdict == "crlf-exact"
        other += verdict == "OTHER"
        print(f"{name:44} {recorded:>9} {blob:>9} {delta:>7} {lines:>7} {verdict}")
    print(f"\ncrlf-exact: {exact} · other: {other}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
