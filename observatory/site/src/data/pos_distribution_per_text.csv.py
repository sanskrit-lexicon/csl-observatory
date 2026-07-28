#!/usr/bin/env python3
"""Observable Framework data loader: read-only TSV→CSV of
data/pos_distribution_per_text.tsv for the /pos-by-text page.

Does not mutate repo-root data/ (H1524 /viz-page contract).
"""
import csv
import io
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parents[4]
src = ROOT / "data" / "pos_distribution_per_text.tsv"
buf = io.StringIO()
with src.open(encoding="utf-8", newline="") as fh:
    reader = csv.reader(fh, delimiter="\t")
    writer = csv.writer(buf, lineterminator="\n")
    for row in reader:
        writer.writerow(row)
sys.stdout.write(buf.getvalue())
