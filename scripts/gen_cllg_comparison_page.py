#!/usr/bin/env python3
"""Derive the public CLLG-comparison page from the canonical internal doc.

Single source of truth: docs/CLLG_VS_SANSKRIT_ESTATE_18-11-2026.md.
The internal doc carries three marked blocks (caveats, score table, moves).
This script drops the `Internal evidence` column entirely and replaces it with
a generic label; internal-only source paths never reach the public page.

Usage:
    python scripts/gen_cllg_comparison_page.py --emit
    python scripts/gen_cllg_comparison_page.py --check
    python scripts/gen_cllg_comparison_page.py --selftest
"""

import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SOURCE = ROOT / "docs" / "CLLG_VS_SANSKRIT_ESTATE_18-11-2026.md"
TARGET = ROOT / "observatory" / "site" / "src" / "cllg-comparison.md"

B_CAVEATS = "<!-- PUBLIC-CAVEATS:BEGIN -->"
E_CAVEATS = "<!-- PUBLIC-CAVEATS:END -->"
B_SCORE = "<!-- PUBLIC-SCORE:BEGIN -->"
E_SCORE = "<!-- PUBLIC-SCORE:END -->"
B_MOVES = "<!-- PUBLIC-MOVES:BEGIN -->"
E_MOVES = "<!-- PUBLIC-MOVES:END -->"

SOURCE_URL = (
    "https://github.com/sanskrit-lexicon/csl-observatory/blob/main/"
    "docs/CLLG_VS_SANSKRIT_ESTATE_18-11-2026.md"
)
INTERNAL_LABEL = "internal-only — not published"
INTERNAL_ADDITIONAL = " (additional internal-only evidence withheld)"

INTRO = (
    "A dated strategic comparison of CLLG (Corpus Liberatum Linguae Graecae) with the "
    "open-Sanskrit estate and the proprietary TLG. Snapshot frozen at **18-11-2026**; "
    "a re-run produces a new dated document, never a silent edit. "
    "The full internal evidence appendix — including the estate's internal ops tooling — "
    "lives in the source document linked below."
)


def extract_block(text: str, begin: str, end: str) -> str:
    i = text.find(begin)
    j = text.find(end)
    if i < 0 or j < 0 or j <= i:
        raise ValueError(f"missing or misordered markers {begin!r} / {end!r}")
    return text[i + len(begin):j].strip()


def split_table(block: str) -> list[list[str]]:
    rows = []
    for line in block.splitlines():
        if not line.strip().startswith("|"):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if all(re.fullmatch(r":?-{3,}:?", c) for c in cells):
            continue
        rows.append(cells)
    if len(rows) < 2:
        raise ValueError("score block must contain a header and at least one data row")
    width = len(rows[0])
    for n, row in enumerate(rows):
        if len(row) != width:
            raise ValueError(f"score table row {n} has {len(row)} cells, expected {width}")
    return rows


PUBLIC_HEADER = [
    "Axis", "CLLG", "Open-Sanskrit estate", "TLG",
    "vs CLLG", "vs TLG", "Evidence",
]


def redact(row: list[str]) -> list[str]:
    """Drop the internal-evidence column; never emit its content."""
    if len(row) != 8:
        raise ValueError(f"expected 8 columns in score row, got {len(row)}")
    public_evidence = row[6]
    internal_evidence = row[7]
    has_internal = internal_evidence not in {"—", "-", ""}
    if public_evidence in {"—", "-", ""}:
        evidence = INTERNAL_LABEL if has_internal else "—"
    else:
        evidence = public_evidence + (INTERNAL_ADDITIONAL if has_internal else "")
    return row[:6] + [evidence]


def render(source_text: str) -> str:
    caveats = extract_block(source_text, B_CAVEATS, E_CAVEATS)
    rows = split_table(extract_block(source_text, B_SCORE, E_SCORE))
    if rows[0] != [
        "Axis", "CLLG", "Open-Sanskrit estate", "TLG",
        "vs CLLG", "vs TLG", "Public evidence", "Internal evidence",
    ]:
        raise ValueError("score header drifted — generator and doc must be updated together")
    moves = extract_block(source_text, B_MOVES, E_MOVES)

    lines = [
        "---",
        "title: CLLG vs the Sanskrit estate (18-11-2026)",
        "toc: false",
        "---",
        "",
        "_Created: 18-11-2026 · Last updated: 18-11-2026_",
        "",
        "# CLLG vs the Sanskrit estate — 18-11-2026",
        "",
        "_Dr. Mārcis Gasūns_",
        "",
        INTRO,
        "",
        "## How to read",
        "",
        caveats,
        "",
        "## Scorecard",
        "",
        "| " + " | ".join(PUBLIC_HEADER) + " |",
        "|" + "|".join(["---"] * len(PUBLIC_HEADER)) + "|",
    ]
    for row in rows[1:]:
        lines.append("| " + " | ".join(redact(row)) + " |")
    lines += [
        "",
        "## Adoption moves",
        "",
        moves,
        "",
        "Source of record: [internal comparison doc](" + SOURCE_URL + "). "
        "Internal-only evidence is withheld from this page by "
        "`scripts/gen_cllg_comparison_page.py`; run `--check` to verify parity.",
        "",
        "_Dr. Mārcis Gasūns_",
        "",
    ]
    return "\n".join(lines)


def _control(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(f"selftest control failed: {message}")


def selftest() -> int:
    # Positive control: internal evidence must be replaced, never printed.
    synthetic_row = ["A", "b", "c", "d", "LEADS", "PARITY", "—", "/private/Uprava/tools/secret.py"]
    out = redact(synthetic_row)
    _control(out == ["A", "b", "c", "d", "LEADS", "PARITY", INTERNAL_LABEL], "redaction shape")
    _control("secret.py" not in " ".join(out), "internal path leaked")
    # Positive control 2: mixed evidence keeps public, withholds internal.
    out2 = redact(["A", "b", "c", "d", "TRAILS", "TRAILS", "[public](https://x)", "internal-path"])
    _control("[public](https://x)" in out2[6] and "internal-path" not in out2[6], "mixed evidence")
    # Negative control: a broken doc must refuse, not emit a partial page.
    try:
        extract_block("no markers here", B_SCORE, E_SCORE)
    except ValueError:
        pass
    else:
        raise RuntimeError("missing markers must fail closed")
    try:
        split_table("| a | b |\n| c |\n")
    except ValueError:
        pass
    else:
        raise RuntimeError("ragged table must fail closed")
    print("selftest: 4/4 controls PASS")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--emit", action="store_true", help="write the public page")
    g.add_argument("--check", action="store_true", help="verify the page matches the source")
    g.add_argument("--selftest", action="store_true", help="offline redaction controls")
    args = ap.parse_args()
    if args.selftest:
        return selftest()
    rendered = render(SOURCE.read_text(encoding="utf-8"))
    if args.emit:
        TARGET.write_text(rendered, encoding="utf-8")
        print(f"emitted {TARGET.relative_to(ROOT)} ({len(rendered)} bytes)")
        return 0
    if not TARGET.exists():
        print(f"FAIL: {TARGET.relative_to(ROOT)} missing — run with --emit", file=sys.stderr)
        return 1
    current = TARGET.read_text(encoding="utf-8")
    if current != rendered:
        print(f"FAIL: {TARGET.relative_to(ROOT)} is stale — run with --emit", file=sys.stderr)
        return 1
    print(f"OK: {TARGET.relative_to(ROOT)} matches canonical doc ({len(rendered)} bytes)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
