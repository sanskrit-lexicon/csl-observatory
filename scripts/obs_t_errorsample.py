#!/usr/bin/env python3
"""OBS-T Phase 7d — independent error sample (corrections vs real errors).

A reviewer will object that the corpus measures *what was fixed*, not *what is
wrong*. To answer it, draw a blind random sample of **raw dictionary entries**,
have a human read each and flag any errors + their component, then compare that
independently-measured error distribution to the *correction* distribution. If the
two profiles agree, corrections track real errors; if not, that gap is itself a
finding.

  --make   sample N raw entries (across dictionaries) into validation/error_sample.csv
  --score  read the annotated sheet and compare the error profile to the corpus
           correction profile (chi-square + side-by-side shares)

Inputs : ../csl-orig/v02/<dict>/<dict>.txt
         observatory/site/src/data/obs_t_summary.json   (correction profile)
Outputs: validation/error_sample.csv
         reports/obs_t_errorbench.md  (--score)

--make refuses to overwrite a sheet that already carries hand annotations (it
would discard them); pass --force to draw a fresh sample anyway.

Usage:  python scripts/obs_t_errorsample.py --make [N] [--force]
        python scripts/obs_t_errorsample.py --score
"""
import csv, json, os, random, re, sys
from collections import Counter
from datetime import datetime, timezone
sys.stdout.reconfigure(encoding='utf-8'); sys.stderr.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
GH_ROOT = os.path.dirname(ROOT)
CSL_ORIG = os.path.join(GH_ROOT, 'csl-orig')
DATA = os.path.join(ROOT, 'observatory', 'site', 'src', 'data')
SUMMARY = os.path.join(DATA, 'obs_t_summary.json')
VDIR = os.path.join(ROOT, 'validation')
SHEET = os.path.join(VDIR, 'error_sample.csv')
OUT_MD = os.path.join(ROOT, 'reports', 'obs_t_errorbench.md')
csv.field_size_limit(10_000_000)

SEED = 7
DICTS = ['mw', 'pw', 'ap90', 'skd', 'bur', 'ben']   # spread of size/era/language
N_DEFAULT = 120
MAXLEN = 900
COLS = ['row_id', 'dict', 'headword_slp1', 'entry_raw',
        'found_error', 'error_component', 'notes']

sys.path.insert(0, HERE)
from reconstruct_git_events import slp1_to_iast  # noqa
_K1 = re.compile(r'<k1>([^<]*)')


def read_records(dct):
    p = os.path.join(CSL_ORIG, 'v02', dct, dct + '.txt')
    if not os.path.exists(p):
        return []
    recs, cur, k1 = [], [], ''
    with open(p, encoding='utf-8', errors='replace') as f:
        for line in f:
            line = line.rstrip('\n')
            if line.startswith('<L>'):
                m = _K1.search(line); k1 = m.group(1) if m else ''
                cur = [line]
            elif line.startswith('<LEND>'):
                if cur:
                    recs.append((k1, ' '.join(cur)))
                cur = []
            elif cur:
                cur.append(line)
    return recs


# Columns a human fills in by hand; never clobber these without --force.
ANNOTATION_COLS = ('found_error', 'error_component', 'notes')


def count_annotations(path, cols):
    """How many rows in an existing sheet carry hand-entered annotations."""
    if not os.path.exists(path):
        return 0
    try:
        with open(path, encoding='utf-8') as f:
            rows = list(csv.DictReader(f))
    except Exception:
        return 0
    return sum(1 for r in rows if any((r.get(c) or '').strip() for c in cols))


def make(n, force=False):
    # The sheet is git-tracked and gets hand-annotated (found_error/error_component).
    # Drawing a fresh blind sample would discard that work, so refuse unless --force.
    existing = count_annotations(SHEET, ANNOTATION_COLS)
    if existing and not force:
        sys.exit(
            f'refusing to overwrite {os.path.relpath(SHEET, ROOT)}: it carries '
            f'{existing} hand-annotated row(s). Re-drawing the blind sample would '
            f'discard them. Use --score to read the current sheet, or back it up '
            f'and pass --force to draw a new sample.'
        )
    rng = random.Random(SEED)
    per = max(1, n // len(DICTS))
    picked = []
    for d in DICTS:
        recs = read_records(d)
        if recs:
            picked.extend((d, k1, body) for k1, body in rng.sample(recs, min(per, len(recs))))
    rng.shuffle(picked)
    os.makedirs(VDIR, exist_ok=True)
    with open(SHEET, 'w', encoding='utf-8', newline='') as f:
        w = csv.DictWriter(f, fieldnames=COLS); w.writeheader()
        for i, (d, k1, body) in enumerate(picked[:n], 1):
            w.writerow({'row_id': i, 'dict': d, 'headword_slp1': slp1_to_iast(k1),
                        'entry_raw': body[:MAXLEN], 'found_error': '',
                        'error_component': '', 'notes': ''})
    print(f'wrote {SHEET}  ({min(n, len(picked))} raw entries from {DICTS})')
    print('  For each entry: found_error = y/n; if y, error_component (same labels '
          'as validation/COMPONENT_GUIDE.md). Then run --score.')


def main():
    if '--make' in sys.argv:
        i = sys.argv.index('--make')
        n = int(sys.argv[i + 1]) if len(sys.argv) > i + 1 and sys.argv[i + 1].isdigit() else N_DEFAULT
        make(n, force='--force' in sys.argv)
    elif '--score' in sys.argv:
        score()
    else:
        sys.exit('usage: obs_t_errorsample.py --make [N] | --score')


def score():
    with open(SHEET, encoding='utf-8') as f:
        rows = [r for r in csv.DictReader(f) if r['found_error'].strip()]
    if not rows:
        sys.exit(f'no annotations yet — fill found_error in {os.path.relpath(SHEET, ROOT)}')
    n = len(rows)
    err = [r for r in rows if r['found_error'].strip().lower().startswith('y')]
    err_profile = Counter(r['error_component'].strip() for r in err if r['error_component'].strip())
    with open(SUMMARY, encoding='utf-8') as f:
        corr = dict(json.load(f)['components'])
    comps = sorted(set(err_profile) | set(corr))
    e_tot = sum(err_profile.values()) or 1
    c_tot = sum(corr.values()) or 1

    L = []; A = L.append
    A('# Corrections vs independently-found errors (OBS-T)')
    A('')
    A(f'_Generated by `scripts/obs_t_errorsample.py --score`. {n} raw entries read; '
      f'{len(err)} contained an error ({len(err)/n:.1%} entry-level error rate). '
      'Compares the independently-annotated error profile to the corpus correction '
      'profile — does correction effort track real errors?_')
    A('')
    A(f'**Entry-level error rate:** {len(err)}/{n} = **{len(err)/n:.1%}**.')
    A('')
    A('| component | found-error share | correction share |')
    A('|---|---:|---:|')
    for c in comps:
        A(f'| {c} | {err_profile.get(c,0)/e_tot:.1%} | {corr.get(c,0)/c_tot:.1%} |')
    A('')
    A('Where the found-error share exceeds the correction share, errors are '
      '*under-corrected* (a backlog signal); where it is lower, corrections '
      'over-represent that component relative to its true incidence.')
    A('')
    A('*Validation artifact; small sample — read as indicative, not definitive.*')
    with open(OUT_MD, 'w', encoding='utf-8', newline='\n') as f:
        f.write('\n'.join(L) + '\n')
    print(f'wrote {OUT_MD}')
    print(f'  entries {n}  with-error {len(err)} ({len(err)/n:.1%})  '
          f'profile {err_profile.most_common()}')


if __name__ == '__main__':
    main()
