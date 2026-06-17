#!/usr/bin/env python3
"""OBS-T release regression checks.

These are lightweight safety gates for the citable correction-event release.
They intentionally check invariants that are easy to break when the corpus is
re-mined: git provenance, unequal hunk accounting, identity redaction, schema
drift, and documentation of human-gated validation commands.

Usage:  python scripts/obs_t_regression.py
"""
import csv, json, os, re, sys

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DATA = os.path.join(ROOT, 'observatory', 'site', 'src', 'data')
SCHEMA = os.path.join(ROOT, 'data', 'schema', 'correction-event.schema.json')
RELEASE = os.path.join(DATA, 'correction_events_release.csv')
GIT_META = os.path.join(DATA, 'correction_events_git.meta.json')
REPORTS_README = os.path.join(ROOT, 'reports', 'README.md')

sys.path.insert(0, HERE)
# Reuse the exact redaction rule the builder applies, so this gate verifies the
# real pattern rather than a private copy that could drift from it.
from build_correction_events import _EMAIL_RE as EMAIL_RE  # noqa: E402

ENTRY_RE = re.compile(r'^v02/([^/]+)/\1\.txt$')


def fail(msgs, msg):
    msgs.append(msg)


def load_release():
    with open(RELEASE, encoding='utf-8', newline='') as f:
        reader = csv.DictReader(f)
        return reader.fieldnames or [], list(reader)


def check_git_paths(rows, failures):
    bad = [r['source_path'] for r in rows
           if r.get('source_layer') == 'git'
           and not ENTRY_RE.fullmatch(r.get('source_path', ''))]
    if bad:
        fail(failures, f'{len(bad)} git rows have non-entry source_path, e.g. {bad[:3]}')


def check_diff_pairing(failures):
    with open(GIT_META, encoding='utf-8') as f:
        meta = json.load(f)
    pairing = meta.get('stats', {}).get('diffPairing', {})
    required = {'unequal_runs', 'unmatched_deletions', 'unmatched_additions',
                'replacements', 'deletions', 'insertions'}
    missing = sorted(required - set(pairing))
    if missing:
        fail(failures, f'diffPairing is missing counters: {missing}')
    if pairing.get('unequal_runs', 0) and (
            pairing.get('unmatched_deletions', 0) + pairing.get('unmatched_additions', 0) == 0):
        fail(failures, 'unequal hunks were seen but unmatched line counters are zero')


def check_no_emails(rows, failures):
    # corrector/corrector_name are pseudonymised; comment_raw (git commit
    # subjects) and inline_comment are copied verbatim and are NOT, so an email
    # in a commit message would otherwise ship in the release uncaught.
    hits = []
    for r in rows:
        for field in ('corrector', 'corrector_name', 'comment_raw', 'inline_comment'):
            val = r.get(field, '')
            if EMAIL_RE.search(val):
                hits.append((r.get('event_id', ''), field, val[:80]))
                if len(hits) >= 5:
                    break
        if len(hits) >= 5:
            break
    if hits:
        fail(failures, f'email-shaped values leaked in release: {hits}')


def check_schema_columns(fields, failures):
    with open(SCHEMA, encoding='utf-8') as f:
        schema = json.load(f)
    props = set(schema.get('properties', {}))
    cols = set(fields)
    missing_in_schema = sorted(cols - props)
    missing_in_release = sorted(props - cols)
    if missing_in_schema:
        fail(failures, f'release columns missing from schema: {missing_in_schema}')
    if missing_in_release:
        fail(failures, f'schema columns missing from release: {missing_in_release}')


def check_human_gated_docs(failures):
    text = open(REPORTS_README, encoding='utf-8').read()
    needed = [
        'obs_t_gold.py --make',
        'obs_t_gold.py --score',
        'obs_t_errorsample.py --make',
        'obs_t_errorsample.py --score',
    ]
    missing = [s for s in needed if s not in text]
    if missing:
        fail(failures, f'human-gated validation commands missing from reports README: {missing}')


def main():
    failures = []
    fields, rows = load_release()
    check_git_paths(rows, failures)
    check_diff_pairing(failures)
    check_no_emails(rows, failures)
    check_schema_columns(fields, failures)
    check_human_gated_docs(failures)

    if failures:
        for msg in failures:
            print(f'FAIL: {msg}', file=sys.stderr)
        return 1

    n_git = sum(1 for r in rows if r.get('source_layer') == 'git')
    print(f'OK release rows: {len(rows):,}')
    print(f'OK git source paths: {n_git:,} entry-file rows')
    print('OK diff pairing counters present')
    print('OK no email-shaped released identities')
    print('OK schema columns match release CSV')
    print('OK human-gated validation commands documented')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
