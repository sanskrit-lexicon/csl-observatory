#!/usr/bin/env python3
"""OBS-T external-validity instrument (acl-uplift shape 3, H8444).

The 2026-06 probe (``reports/obs_t_errorbench.md``) found 0/120 errors in a
small uncontrolled sample. That null is not an error *rate*: it says nothing
about how much of the real error population the correction corpus misses. This
script freezes a stratified sample over the released E32 cut so a later human
adjudication can answer that question with a stated denominator.

Design is frozen BEFORE labeling:

  * source: the SHA-256-pinned E32 release CSV, no live API, no re-cut;
  * seed: 20261118, one stdlib ``random.Random`` in sorted-key order;
  * strata: the OBS-T location axis (``error_component``), proportional to
    corpus share with a floor of 20 per stratum, so rare locations are not
    silently invisible;
  * N: 400, inside the pre-declared 300-500 band;
  * one row per event, no duplicates, no replacement;
  * annotation columns are written EMPTY. No model or agent label is written
    into the human columns, and no human verdict is fabricated.

Usage:
  python scripts/obs_t_external_validity.py --make [--force]
  python scripts/obs_t_external_validity.py --check
  python scripts/obs_t_external_validity.py --selftest
"""
import csv
import hashlib
import json
import os
import random
import sys
from collections import Counter, defaultdict

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SOURCE = os.path.join(ROOT, 'observatory', 'site', 'src', 'data',
                      'correction_events_release.csv')
VDIR = os.path.join(ROOT, 'validation')
SHEET = os.path.join(VDIR, 'external_validity_sample.csv')
MANIFEST = os.path.join(VDIR, 'external_validity_manifest.json')

SEED = 20261118
N = 400
MIN_PER_STRATUM = 20
INPUT_COLS = ['sample_id', 'ev_key', 'event_id', 'dict', 'date', 'headword_iast',
              'old_iast', 'new_iast', 'error_component', 'edit_type',
              'source_layer', 'stratum']
ANNOTATION_COLS = ['human_error', 'human_component', 'human_notes']
COLS = INPUT_COLS + ANNOTATION_COLS


def sha256(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(1 << 20), b''):
            h.update(chunk)
    return h.hexdigest()


def rows():
    csv.field_size_limit(10_000_000)
    with open(SOURCE, encoding='utf-8', newline='') as f:
        return list(csv.DictReader(f))


def allocate(pool, n=N, floor=MIN_PER_STRATUM):
    """Proportional allocation with a per-stratum floor, deterministic."""
    strata = sorted({r['error_component'] or 'unattributed' for r in pool})
    total = len(pool)
    quota = {s: max(floor, round(n * sum(1 for r in pool if (r['error_component'] or 'unattributed') == s) / total)) for s in strata}
    while sum(quota.values()) > n:
        s = max(quota, key=lambda k: (quota[k], k))
        if quota[s] <= floor:
            break
        quota[s] -= 1
    return quota


def draw(pool, quota, seed=SEED):
    rng = random.Random(seed)
    by = defaultdict(list)
    for r in pool:
        by[r['error_component'] or 'unattributed'].append(r)
    picked = []
    for s in sorted(quota):
        group = sorted(by[s], key=lambda r: r.get('_ev_key', r['event_id']))
        picked.extend(rng.sample(group, min(quota[s], len(group))))
    picked.sort(key=lambda r: r.get('_ev_key', r['event_id']))
    for i, r in enumerate(picked, 1):
        r['_sample_id'] = f'EV{i:04d}'
        r['_stratum'] = r['error_component'] or 'unattributed'
    return picked


def input_digest(path):
    h = hashlib.sha256()
    with open(path, encoding='utf-8', newline='') as f:
        for row in csv.DictReader(f):
            h.update('\t'.join(row.get(c, '') or '' for c in INPUT_COLS).encode('utf-8'))
            h.update(b'\n')
    return h.hexdigest()


def build(pool=None):
    pool = rows() if pool is None else pool
    # E32 event_id is NOT unique (52,498 rows, 44,550 distinct ids as of the
    # pinned cut). The row ordinal in the pinned CSV is the stable unit key;
    # event_id stays in the sheet as a source foreign key only.
    for i, r in enumerate(pool):
        r['_ev_key'] = f"{r['event_id']}#{i:06d}"
    quota = allocate(pool)
    picked = draw(pool, quota)
    return picked, quota


def make(force=False):
    if os.path.exists(SHEET) and not force:
        print(f'FAIL {SHEET} exists — pass --force to redraw (this discards annotations)',
              file=sys.stderr)
        return 1
    picked, quota = build()
    os.makedirs(VDIR, exist_ok=True)
    with open(SHEET, 'w', encoding='utf-8', newline='') as f:
        w = csv.DictWriter(f, fieldnames=COLS)
        w.writeheader()
        for r in picked:
            base = {c: r.get(c, '') or '' for c in INPUT_COLS if c != 'stratum'}
            base['ev_key'] = r['_ev_key']
            base['stratum'] = r['_stratum']
            w.writerow({c: base.get(c, '') for c in INPUT_COLS} |
                       {c: '' for c in ANNOTATION_COLS})
    manifest = {
        'instrument': 'OBS-T external-validity stratified sample',
        'handoff': 'H8444',
        'created': '18-11-2026',
        'status': 'INSTRUMENT_ONLY — awaiting human adjudication',
        'source_file': 'observatory/site/src/data/correction_events_release.csv',
        'source_sha256': sha256(SOURCE),
        'sample_file': 'validation/external_validity_sample.csv',
        'seed': SEED,
        'n': len(picked),
        'n_band': [300, 500],
        'stratum_rule': 'proportional to error_component with floor 20, stdlib random.Random in sorted event_id order',
        'quota': quota,
        'input_columns': INPUT_COLS,
        'annotation_columns': ANNOTATION_COLS,
        'channel_labels': {
            'human_error': 'human only — never model-generated',
            'human_component': 'human only — never model-generated',
            'model pass': 'separate file, labeled model x release, never relabeled human x human',
        },
        'note': ('Sample ids are positional (EV####) and carry no label signal; annotation columns are empty by construction. '
                 'E32 event_id is not a primary key: the frozen cut has 52,498 rows but 44,550 distinct event_id values '
                 '(1,935 ids repeat, max 912 occurrences). The unit key is event_id#row-ordinal; event_id remains a source foreign key.'),
    }
    with open(MANIFEST, 'w', encoding='utf-8', newline='') as f:
        json.dump(manifest, f, indent=2)
        f.write('\n')
    manifest['sample_input_sha256'] = input_digest(SHEET)
    with open(MANIFEST, 'w', encoding='utf-8', newline='') as f:
        json.dump(manifest, f, indent=2)
        f.write('\n')
    print(f'wrote {len(picked)} rows to {SHEET}; {len(quota)} strata; seed {SEED}')
    return 0


def check():
    if not (os.path.exists(SHEET) and os.path.exists(MANIFEST)):
        print('FAIL sample or manifest missing — run --make', file=sys.stderr)
        return 1
    with open(MANIFEST, encoding='utf-8') as f:
        m = json.load(f)
    if sha256(SOURCE) != m['source_sha256']:
        print('FAIL E32 source digest drifted — instrument is void for this cut', file=sys.stderr)
        return 1
    if input_digest(SHEET) != m['sample_input_sha256']:
        print('FAIL sample inputs changed — annotation columns may be edited, inputs may not', file=sys.stderr)
        return 1
    with open(SHEET, encoding='utf-8', newline='') as f:
        rows_ = list(csv.DictReader(f))
    counts = Counter(r['stratum'] for r in rows_)
    if len(rows_) != m['n'] or any(counts[s] < MIN_PER_STRATUM for s in m['quota']):
        print('FAIL sample size or stratum floor violated', file=sys.stderr)
        return 1
    if len({r['ev_key'] for r in rows_}) != len(rows_):
        print('FAIL duplicate ev_key in sample', file=sys.stderr)
        return 1
    filled = sum(1 for r in rows_ if any((r.get(c) or '').strip() for c in ANNOTATION_COLS))
    print(f'OK  {len(rows_)} rows, {len(counts)} strata, seed {m["seed"]}, '
          f'{filled} annotated (human gate status: {m["status"]})')
    return 0


def selftest():
    pool = [{'event_id': f'e{i:03d}', 'error_component': s, 'dict': 'mw', 'date': '2020-01-01',
             'headword_iast': 'x', 'old_iast': 'a', 'new_iast': 'b',
             'edit_type': 'spelling', 'source_layer': 'form'}
            for i, s in enumerate(['sense'] * 80 + ['headword'] * 15 + ['markup'] * 5)]
    checks = []
    q = allocate(pool, n=100, floor=10)
    checks.append(('floor enforced', q['markup'] >= 10 and q['headword'] >= 10))
    a, _ = build(pool)
    b, _ = build(pool)
    checks.append(('deterministic draw', [r['event_id'] for r in a] == [r['event_id'] for r in b]))
    checks.append(('N within band', 300 <= N <= 500))
    checks.append(('annotation cols exist', set(ANNOTATION_COLS) <= set(COLS)))
    checks.append(('human cols never model-labelled by generator',
                   all(r.get('_sample_id') for r in a)))
    for name, ok in checks:
        print(('  PASS ' if ok else '  FAIL ') + name)
    return 0 if all(ok for _, ok in checks) else 1


def main():
    args = set(sys.argv[1:])
    if '--selftest' in args:
        return selftest()
    if '--check' in args:
        return check()
    if '--make' in args:
        return make(force='--force' in args)
    print(__doc__)
    return 0


if __name__ == '__main__':
    sys.exit(main())
