#!/usr/bin/env python3
"""One-off migration (H1494 / roadmap Part 4.1): rewrite event_id to the obst:v1 scheme.

Recipe lives in `event_id_v1()` (scripts/build_correction_events.py), reused here so the
freshly-generated rows a future Phase-1/Phase-2 run produces and the rows this script
re-migrates can never disagree: obst:v1:<source_layer>:<dict>:<h12>, where <h12> = first
12 hex chars of SHA-256 over (source_layer, dict, source_path, commit_sha, date, old_iast,
new_iast) joined with U+001F.

Idempotent: any row whose event_id already matches ^obst:v1: is left untouched, so running
this twice is a no-op. Rewrites the event_id column in place across every
correction_events*.csv under observatory/site/src/data/, and writes an
old_event_id,new_event_id crosswalk (deduplicated, built once from the union file
correction_events_all.csv) so any event_id already cited in a report stays resolvable.

Known property, not a bug: the recipe's tuple deliberately excludes headword_iast, so two
rows that share every tuple field collapse to the same new id (see the schema $comment).

Usage:  python scripts/migrate_event_ids_v1.py [--dry-run]
"""
import csv
import os
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DATA = os.path.join(ROOT, 'observatory', 'site', 'src', 'data')

sys.path.insert(0, HERE)
from build_correction_events import event_id_v1  # noqa: E402

UNION_CSV = os.path.join(DATA, 'correction_events_all.csv')
CROSSWALK_CSV = os.path.join(DATA, 'event_id_crosswalk_v1.csv')
TARGET_FILES = [
    'correction_events.csv',
    'correction_events_all.csv',
    'correction_events_git.csv',
    'correction_events_typed.csv',
    'correction_events_final.csv',
    'correction_events_release.csv',
]
TUPLE_FIELDS = ('source_layer', 'dict', 'source_path', 'commit_sha', 'date',
                'old_iast', 'new_iast')
_NEW_RE = re.compile(r'^obst:v1:')


def compute(row):
    return event_id_v1(*(row[f] for f in TUPLE_FIELDS))


def build_crosswalk(dry_run):
    """Read the union file once; return (total, unique_new, collisions)."""
    pairs = []
    new_ids = set()
    with open(UNION_CSV, encoding='utf-8', newline='') as f:
        for row in csv.DictReader(f):
            old_id = row['event_id']
            new_id = old_id if _NEW_RE.match(old_id) else compute(row)
            pairs.append((old_id, new_id))
            new_ids.add(new_id)
    collisions = len(pairs) - len(new_ids)
    if not dry_run:
        with open(CROSSWALK_CSV, 'w', encoding='utf-8', newline='') as f:
            w = csv.writer(f)
            w.writerow(['old_event_id', 'new_event_id'])
            for old, new in sorted(set(pairs)):
                w.writerow([old, new])
    return len(pairs), len(new_ids), collisions


def rewrite_file(path, dry_run):
    if not os.path.exists(path):
        return None
    with open(path, encoding='utf-8', newline='') as f:
        reader = csv.DictReader(f)
        fields = reader.fieldnames
        rows = list(reader)
    changed = already = 0
    for r in rows:
        if _NEW_RE.match(r['event_id']):
            already += 1
            continue
        r['event_id'] = compute(r)
        changed += 1
    if not dry_run:
        with open(path, 'w', encoding='utf-8', newline='') as f:
            w = csv.DictWriter(f, fieldnames=fields)
            w.writeheader()
            w.writerows(rows)
    return len(rows), changed, already


def main():
    dry_run = '--dry-run' in sys.argv
    total, unique, collisions = build_crosswalk(dry_run)
    tail = ' [dry-run, not written]' if dry_run else f' -> wrote {CROSSWALK_CSV}'
    print(f'crosswalk: {total} rows -> {unique} unique new ids ({collisions} collisions; '
          f'expected under the content-addressed recipe, see schema $comment){tail}')
    for name in TARGET_FILES:
        path = os.path.join(DATA, name)
        result = rewrite_file(path, dry_run)
        if result is None:
            print(f'{name}: not found, skipped')
            continue
        n, changed, already = result
        suffix = ' [dry-run]' if dry_run else ''
        print(f'{name}: {n} rows, {changed} migrated, {already} already v1{suffix}')


if __name__ == '__main__':
    main()
