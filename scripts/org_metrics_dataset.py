#!/usr/bin/env python3
"""Emit a Croissant-style dataset description for the A15 org-metrics corpus.

The observatory already catalogues its public data files in
``observatory/site/src/data/data_index.csv``. That catalogue records size and
row count but not a stable dataset ID, a per-cut digest, or a machine-readable
distribution block. This script derives those from the committed catalogue and
bytes -- no live API call, no data re-cut -- so the A15 paper can cite a dataset
rather than a dashboard.

Usage:
    python scripts/org_metrics_dataset.py            # write data/org_metrics_dataset.json
    python scripts/org_metrics_dataset.py --check    # refuse on drift (CI gate)
    python scripts/org_metrics_dataset.py --selftest # metric/fixture checks

The OBS-T correction corpus is deliberately out of scope: it has its own
concept DOI and its own datasheet. Excluded files are listed in the output's
``exclusions`` block with a reason, never silently dropped.
"""
import csv
import hashlib
import json
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DATA_DIR = os.path.join(ROOT, 'observatory', 'site', 'src', 'data')
INDEX = os.path.join(DATA_DIR, 'data_index.csv')
MANIFEST = os.path.join(ROOT, 'data', 'manifest.json')
OUT = os.path.join(ROOT, 'data', 'org_metrics_dataset.json')

DATASET_ID = 'csl-obs/org-metrics@1.0.0'
SNAPSHOT_ID = 'csl-obs/org@1.0.0'
LICENSE = 'CC BY 4.0'
RAW = ('https://github.com/sanskrit-lexicon/csl-observatory/raw/main/'
       'observatory/site/src/data/')

# Categories that belong to the separate OBS-T data release, plus the LFS
# corpus and locally-derived helper files. Each carries a written reason.
EXCLUDE_CATEGORIES = {
    'obs-t': 'OBS-T release — separate concept DOI 10.5281/zenodo.21346705',
    'obs-t analysis': 'OBS-T analysis layer — separate data release',
    'obs-t recapture': 'OBS-T recapture layer — separate data release',
    'obs-t release': 'OBS-T release manifest — separate data release',
    'obs-t corpus': 'OBS-T corpus — 62 MB LFS object, digest pinned elsewhere',
}


def sha256(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(1 << 20), b''):
            h.update(chunk)
    return h.hexdigest()


def is_lfs_pointer(path):
    with open(path, 'rb') as f:
        return f.read(64).startswith(b'version https://git-lfs.github.com/spec/v1')


def build():
    with open(MANIFEST, encoding='utf-8') as f:
        manifest = json.load(f)
    as_of = manifest['transformed_at']
    exclusions, distributions = [], []
    with open(INDEX, encoding='utf-8', newline='') as f:
        rows = list(csv.DictReader(f))
    for row in rows:
        name, cat = row['file'], row['category']
        if cat in EXCLUDE_CATEGORIES:
            exclusions.append({'file': name, 'reason': EXCLUDE_CATEGORIES[cat]})
            continue
        path = os.path.join(DATA_DIR, name)
        if not os.path.exists(path):
            exclusions.append({'file': name, 'reason': 'catalogued but absent from this checkout'})
            continue
        if is_lfs_pointer(path):
            exclusions.append({'file': name, 'reason': 'LFS pointer, blob not present — digest not computable offline'})
            continue
        distributions.append({
            '@type': 'FileObject',
            'name': name,
            'contentUrl': RAW + name,
            'encodingFormat': 'text/csv' if name.endswith('.csv') else 'application/json',
            'contentSize': os.path.getsize(path),
            'sha256': sha256(path),
            'description': row['description'],
        })
    distributions.sort(key=lambda d: d['name'])
    exclusions.sort(key=lambda e: e['file'])
    return {
        '@context': 'https://schema.org/',
        '@type': 'Dataset',
        'name': 'CSL Observatory org-metrics snapshot',
        'identifier': DATASET_ID,
        'description': ('Org-level GitHub/CDSL maintenance metrics (repositories, issues, '
                        'PRs, commits, contributors, taxonomy and reach) for the '
                        'sanskrit-lexicon organisation. Offline, reproducible from the '
                        'committed CSVs.'),
        'snapshot': SNAPSHOT_ID,
        'asOf': as_of,
        'license': LICENSE,
        'url': 'https://sanskrit-lexicon.github.io/csl-observatory/',
        'sameAs': 'https://doi.org/10.5281/zenodo.22853817',
        'variableMeasured': sorted({r['category'] for r in rows} - set(EXCLUDE_CATEGORIES)),
        'distribution': distributions,
        'exclusions': exclusions,
    }


def selftest():
    checks = []
    checks.append(('dataset id is stable', DATASET_ID == 'csl-obs/org-metrics@1.0.0'))
    checks.append(('OBS-T corpus excluded', 'obs-t corpus' in EXCLUDE_CATEGORIES))
    checks.append(('exclusion reasons written', all(EXCLUDE_CATEGORIES.values())))
    obj = build()
    checks.append(('distributions present', len(obj['distribution']) > 20))
    checks.append(('every distribution has a digest',
                   all(len(d['sha256']) == 64 for d in obj['distribution'])))
    checks.append(('every distribution has a contentUrl',
                   all(d['contentUrl'].startswith('https://') for d in obj['distribution'])))
    checks.append(('no OBS-T row leaked into distributions',
                   not any(d['name'].startswith('obs_t') for d in obj['distribution'])))
    for name, ok in checks:
        print(('  PASS ' if ok else '  FAIL ') + name)
    return 0 if all(ok for _, ok in checks) else 1


def main():
    args = set(sys.argv[1:])
    if '--selftest' in args:
        return selftest()
    obj = build()
    if '--check' in args:
        if not os.path.exists(OUT):
            print(f'FAIL {OUT} missing — run the generator', file=sys.stderr)
            return 1
        with open(OUT, encoding='utf-8') as f:
            committed = json.load(f)
        if committed != obj:
            print('FAIL data/org_metrics_dataset.json is stale — regenerate with '
                  'python scripts/org_metrics_dataset.py', file=sys.stderr)
            return 1
        print(f'OK  {len(obj["distribution"])} distributions, '
              f'{len(obj["exclusions"])} documented exclusions — dataset JSON current')
        return 0
    with open(OUT, 'w', encoding='utf-8', newline='\n') as f:
        json.dump(obj, f, indent=2, ensure_ascii=False, sort_keys=False)
        f.write('\n')
    print(f'wrote {OUT}: {len(obj["distribution"])} distributions, '
          f'{len(obj["exclusions"])} exclusions, snapshot {obj["asOf"]}')
    return 0


if __name__ == '__main__':
    sys.exit(main())
