#!/usr/bin/env python3
"""Observable Framework data loader for /research-measurements (H6071).

Aggregates EVERY data/publication/a61-* release directory into one CSV so the
page auto-surfaces new measurement releases on the weekly refresh cron: each
row carries (release, measurement, label, value_kind, value) built from the
release's own summary.json / matrix.csv — no numbers are hand-typed here.
Rows for measurement families without a public release yet (mānadaṇḍa census,
NWS coverage, WSD bench) come from the register tail below with status
pending_public_release and NO values (paper-priv: those artifacts live in
private storage until their submissions clear)."""
import csv
import io
import json
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')

ROOT = Path(__file__).resolve().parents[4]
PUB = ROOT / 'data' / 'publication'

rows = []


def num(x):
    try:
        return f"{float(x):g}"
    except (TypeError, ValueError):
        return ""


for rel_dir in sorted(PUB.glob('a61-*')):
    if not rel_dir.is_dir():
        continue
    release = rel_dir.name
    summary_p = rel_dir / 'summary.json'
    if not summary_p.is_file():
        continue
    try:
        summary = json.loads(summary_p.read_text(encoding='utf-8'))
    except (OSError, json.JSONDecodeError):
        continue

    if 'matrix.csv' in [p.name for p in rel_dir.iterdir()]:
        # sixdict sense-seq rho-matrix release: one row per dictionary pair
        with open(rel_dir / 'matrix.csv', encoding='utf-8', newline='') as fh:
            for rec in csv.DictReader(fh):
                rows.append({
                    'release': release,
                    'measurement': 'sense-seq rho-matrix',
                    'label': f"{rec['pair_a']}×{rec['pair_b']}",
                    'value_kind': 'rho_median (n_pairs)',
                    'value': num(rec.get('rho_median')),
                    'detail': (
                        f"n_common_k1={rec.get('n_common_k1', '')}; "
                        f"n_pairs_ge3={rec.get('n_pairs_ge3', '')}; "
                        f"null_median={num(rec.get('cross_null_median'))}"
                    ),
                    'status': 'released',
                })
    else:
        # single-measurement release (e.g. a61-mwpwg-sense-seq): summary counts
        mw = summary.get('mwpwg') or {}
        label = str(mw.get('label', release))
        for key, blob in mw.items():
            if key in ('label',):
                continue
            rows.append({
                'release': release,
                'measurement': 'sense-seq concordance',
                'label': label,
                'value_kind': key,
                'value': num(blob),
                'detail': f"n_pairs={mw.get('n_pairs', '')}",
                'status': 'released',
            })

# Register tail: measurement families of the A61 wave with no public release
# yet — presence only, never values (STANDING_POLICY_PAPER_WORK_PRIVATE).
for fam, note in [
    ('mānadaṇḍa census',
     'Kālidāsa dossier wave (H5920–H5922); artifact private until submission'),
    ('NWS coverage',
     '82.7%-outside-full-base analysis (H5932); artifact private until submission'),
    ('WSD bench',
     'LLM-vs-MFS disambiguation bench; artifact private until ISCLS-9 submission (01-02-2027)'),
]:
    rows.append({
        'release': '—',
        'measurement': fam,
        'label': note,
        'value_kind': '—',
        'value': '',
        'detail': 'auto-surfaces here as a data/publication/a61-* release',
        'status': 'pending_public_release',
    })

buf = io.StringIO()
w = csv.DictWriter(buf, fieldnames=[
    'release', 'measurement', 'label', 'value_kind', 'value', 'detail',
    'status'])
w.writeheader()
w.writerows(rows)
sys.stdout.write(buf.getvalue())
