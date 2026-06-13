#!/usr/bin/env python3
"""OBS-T Phase 6a — build the citable release table with a temporal split.

Adds a `split` column (train / dev / test) to the final per-event table, assigned
by calendar date so models train on the past and are evaluated on recent data
(the honest split for an error-correction resource). Writes the release CSV the
NLP baselines and any external user consume.

Split policy (temporal): test = year >= 2025, dev = 2023-2024, train = <= 2022.

Input : observatory/site/src/data/correction_events_final.csv
Output: observatory/site/src/data/correction_events_release.csv  (+ split column)
        observatory/site/src/data/correction_events_release.meta.json

Usage:  python scripts/obs_t_release.py
"""
import csv, json, os, sys
from collections import Counter
from datetime import datetime, timezone
sys.stdout.reconfigure(encoding='utf-8'); sys.stderr.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DATA = os.path.join(ROOT, 'observatory', 'site', 'src', 'data')
IN_CSV = os.path.join(DATA, 'correction_events_final.csv')
OUT_CSV = os.path.join(DATA, 'correction_events_release.csv')
OUT_META = os.path.join(DATA, 'correction_events_release.meta.json')
csv.field_size_limit(10_000_000)

TEST_FROM = 2025
DEV_FROM = 2023


def split_of(date):
    if not date:
        return 'train'
    y = int(date[:4])
    if y >= TEST_FROM:
        return 'test'
    if y >= DEV_FROM:
        return 'dev'
    return 'train'


def main():
    with open(IN_CSV, encoding='utf-8') as f:
        rows = list(csv.DictReader(f))
    fields = list(rows[0].keys())
    if 'split' not in fields:
        fields.append('split')
    counts = Counter()
    by_layer = Counter()
    for r in rows:
        r['split'] = split_of(r['date'])
        counts[r['split']] += 1
        by_layer[(r['split'], r['source_layer'])] += 1
    with open(OUT_CSV, 'w', encoding='utf-8', newline='') as f:
        w = csv.DictWriter(f, fieldnames=fields); w.writeheader(); w.writerows(rows)

    meta = {
        'schemaVersion': '1.0.0',
        'generatedAt': datetime.now(timezone.utc).isoformat(),
        'sourcePath': 'correction_events_final.csv',
        'recordCount': len(rows),
        'assumptions': [
            f'Temporal split: test = year >= {TEST_FROM}, dev = {DEV_FROM}-{TEST_FROM-1}, '
            'train = earlier (incl. the 2014-2019 form era).',
            'Train/test are time-disjoint so evaluation does not leak future edits.',
        ],
        'warnings': [
            'The form era (2014-2019) falls entirely in train; test is git-era only. '
            'Layer-specific baselines (form-only detection/correction) therefore use '
            'their own within-form temporal split (see obs_t_baselines.py).'],
        'stats': {'split': counts.most_common(),
                  'splitByLayer': sorted(by_layer.items())},
    }
    with open(OUT_META, 'w', encoding='utf-8') as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)
    print(f'wrote {OUT_CSV}  ({len(rows)} events)')
    print(f'  split: {counts.most_common()}')


if __name__ == '__main__':
    main()
