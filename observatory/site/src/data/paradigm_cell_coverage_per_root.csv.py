#!/usr/bin/env python3
"""Observable Framework data loader: read-only TSV→CSV of
data/paradigm_cell_coverage_per_root.tsv for the /paradigm-cell-coverage page.

Does not mutate repo-root data/ (H1524 /viz-page contract).
"""
import csv
import io
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parents[4]
src = ROOT / "data" / "paradigm_cell_coverage_per_root.tsv"
buf = io.StringIO()
with src.open(encoding="utf-8", newline="") as fh:
    reader = csv.reader(fh, delimiter="\t")
    writer = csv.writer(buf, lineterminator="\n")
    for row in reader:
        writer.writerow(row)
sys.stdout.write(buf.getvalue())
