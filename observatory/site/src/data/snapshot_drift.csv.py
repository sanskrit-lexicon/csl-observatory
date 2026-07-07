#!/usr/bin/env python3
"""Observable Framework data loader: tidy view of the weekly org snapshots.

Reads data/snapshots/<date>/summary.json (read-only — snapshots stay canonical
in data/) and emits snapshot_date,metric,value to stdout for the /org-shape
page (V9/V10). No files are written.
"""
import csv
import json
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

# this file: observatory/site/src/data/snapshot_drift.csv.py -> repo root is 4 up
ROOT = Path(__file__).resolve().parents[4]
SNAPSHOTS = ROOT / 'data' / 'snapshots'
METRICS = ['total_issues', 'total_pull_requests', 'total_commits', 'repos_count']

w = csv.writer(sys.stdout, lineterminator='\n')
w.writerow(['snapshot_date', 'metric', 'value'])
for summary_path in sorted(SNAPSHOTS.glob('*/summary.json')):
    with open(summary_path, encoding='utf-8') as f:
        summary = json.load(f)
    date = summary.get('snapshot_date', summary_path.parent.name)
    for metric in METRICS:
        if metric in summary:
            w.writerow([date, metric, summary[metric]])
