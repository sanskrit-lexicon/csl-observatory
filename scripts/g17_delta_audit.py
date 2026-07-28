#!/usr/bin/env python3
"""G17 delta audit: explain data_index.csv bytes/rows drift file by file.

For every row of the committed data_index.csv, compare the recorded bytes
against the on-disk size, the git blob size, and the file's newline profile,
so the drift H864 flagged (all files ~0.7-3% smaller than recorded) is
attributed arithmetically instead of guessed at.
"""

from __future__ import annotations

import csv
import subprocess
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "observatory" / "site" / "src" / "data"
INDEX = DATA_DIR / "data_index.csv"
REL = "observatory/site/src/data"


def blob_size(name: str) -> int | None:
    proc = subprocess.run(
        ["git", "-C", str(ROOT), "cat-file", "-s", f"HEAD:{REL}/{name}"],
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    if proc.returncode != 0:
        return None
    return int(proc.stdout.strip())


def main() -> int:
    with INDEX.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))

    print(f"{'file':44} {'recorded':>9} {'disk':>9} {'blob':>9} {'rec-disk':>8} {'lines':>7} {'crlf':>6} verdict")
    counts = {"match": 0, "newline-arith": 0, "content-drift": 0, "absent": 0, "self": 0}
    for row in rows:
        name = row["file"]
        recorded = int(row["bytes"])
        path = DATA_DIR / name
        if name == "data_index.csv":
            counts["self"] += 1
            continue
        if not path.exists():
            print(f"{name:44} {recorded:>9} {'ABSENT':>9}")
            counts["absent"] += 1
            continue
        raw = path.read_bytes()
        disk = len(raw)
        blob = blob_size(name)
        lines = raw.count(b"\n")
        crlf = raw.count(b"\r\n")
        delta = recorded - disk
        if delta == 0:
            verdict = "match"
        elif delta == lines - crlf:
            # recorded was measured on a CRLF checkout of this same content:
            # every LF-only line ending gains exactly one byte there.
            verdict = "newline-arith"
        else:
            verdict = "content-drift"
        counts[verdict] += 1
        print(f"{name:44} {recorded:>9} {disk:>9} {str(blob):>9} {delta:>8} {lines:>7} {crlf:>6} {verdict}")

    print()
    print("summary:", counts)
    autocrlf = subprocess.run(
        ["git", "-C", str(ROOT), "config", "core.autocrlf"],
        capture_output=True,
        text=True,
        encoding="utf-8",
    ).stdout.strip()
    print(f"core.autocrlf here: {autocrlf or '(unset)'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
