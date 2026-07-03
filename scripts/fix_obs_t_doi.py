#!/usr/bin/env python3
"""Sweep the corrected OBS-T Zenodo DOI across the repos — verify-first.

Background: `10.5281/zenodo.15834721` was recorded 2026-07-01 as the OBS-T
dataset concept DOI but resolves to an unrelated preprint (H092 finding,
2026-07-03). Once the real record exists on Zenodo, this script replaces the
bad DOI in every file that cites it AS the OBS-T DOI ("authoritative" files),
while leaving the historical mismatch narratives intact (they must keep the
old number to stay true).

It refuses to write anything until the new record is fetched from the Zenodo
API and its title/creator match OBS-T — the wrong DOI got in exactly because
a number was written down unverified.

Usage:
    python scripts/fix_obs_t_doi.py --record 10.5281/zenodo.NNNNNNN            # dry run
    python scripts/fix_obs_t_doi.py --record NNNNNNN --apply                   # write

After --apply, finish by hand (the script prints this too):
  1. python scripts/external_reach.py --fetch     (unblocks the Zenodo tier)
  2. update the narrative files it lists (prose: "resolved, new DOI ...")
  3. rebuild the site, commit csl-observatory + Uprava, regen the dashboard.
"""
import argparse, json, os, re, sys, urllib.request
sys.stdout.reconfigure(encoding='utf-8'); sys.stderr.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
GH = os.path.dirname(ROOT)

OLD_DOI = '10.5281/zenodo.15834721'
OLD_ID = '15834721'

# Files where the old DOI is cited AS the OBS-T dataset DOI -> replace.
AUTHORITATIVE = [
    'CITATION.cff',
    'README.md',
    'STATUS.md',
    'CHANGELOG.md',
    'reports/obs_t_paper_draft.md',
    'docs/REVIEWER_REPRODUCIBILITY.md',
    'observatory/site/src/reproducibility.md',
    'observatory/site/src/data.md',
    'article/A48_error_recapture.md',
]

# Files that DESCRIBE the mismatch — keep the old number, update prose by hand.
NARRATIVE = [
    '.ai_state.md',
    'docs/OBSERVATORY_ROADMAP.md',
    'reports/external_reach.md',
    'observatory/site/src/reach.md',
    'observatory/site/src/data/external_reach.csv',
    '../Uprava/GTD_NEXT_ACTIONS.md',
    '../Uprava/ARTICLES.md',
    '../Uprava/handoffs/archive/H092_obs_external_impact.md',
    '../Uprava/dashboard/articles.js (regenerate: python ../Uprava/tools/build_dashboard_data.py)',
]

STALE_CACHE = 'reports/external_reach_cache/2026-07/zenodo_15834721.json'
REACH_SCRIPT = 'scripts/external_reach.py'


def fetch_record(rec_id):
    url = f'https://zenodo.org/api/records/{rec_id}'
    with urllib.request.urlopen(url, timeout=30) as r:
        return json.loads(r.read().decode('utf-8'))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--record', required=True,
                    help='new Zenodo record: bare id or 10.5281/zenodo.NNN')
    ap.add_argument('--concept', help='concept DOI override (default: from the record)')
    ap.add_argument('--apply', action='store_true', help='write changes (default: dry run)')
    a = ap.parse_args()

    rec_id = a.record.rsplit('.', 1)[-1] if '/' in a.record else a.record
    if not rec_id.isdigit():
        sys.exit(f'cannot parse record id from {a.record!r}')

    # ---- verify BEFORE touching anything ----
    rec = fetch_record(rec_id)
    md = rec.get('metadata', {})
    title = md.get('title', '')
    creators = '; '.join(c.get('name', '') for c in md.get('creators', []))
    print(f'record {rec_id}:')
    print(f'  title:    {title}')
    print(f'  creators: {creators}')
    ok_title = ('OBS-T' in title or 'Correction-Event' in title) and 'Sanskrit' in title
    ok_creator = 'Gas' in creators
    if not (ok_title and ok_creator):
        sys.exit('ABORT: fetched record does not look like the OBS-T dataset '
                 '(title must mention OBS-T/Correction-Event + Sanskrit; creator Gasūns). '
                 'Nothing written.')
    concept = a.concept or rec.get('conceptdoi') or ''
    record_doi = rec.get('doi', f'10.5281/zenodo.{rec_id}')
    new_doi = concept or record_doi   # cite the concept DOI when it exists
    print(f'  record DOI:  {record_doi}')
    print(f'  concept DOI: {concept or "(none — using record DOI)"}')
    print(f'  -> citing:   {new_doi}\n')

    changed = []
    for rel in AUTHORITATIVE:
        p = os.path.join(ROOT, *rel.split('/'))
        if not os.path.exists(p):
            print(f'  MISSING (skip): {rel}')
            continue
        s = open(p, encoding='utf-8').read()
        n = s.count(OLD_DOI)
        if not n:
            continue
        if a.apply:
            open(p, 'w', encoding='utf-8', newline='').write(s.replace(OLD_DOI, new_doi))
        changed.append((rel, n))
        print(f'  {"FIXED " if a.apply else "would fix"} {rel}: {n} occurrence(s)')

    # external_reach.py record id
    p = os.path.join(ROOT, *REACH_SCRIPT.split('/'))
    s = open(p, encoding='utf-8').read()
    if f'ZENODO_RECORD_ID = "{OLD_ID}"' in s:
        if a.apply:
            open(p, 'w', encoding='utf-8', newline='').write(
                s.replace(f'ZENODO_RECORD_ID = "{OLD_ID}"', f'ZENODO_RECORD_ID = "{rec_id}"'))
        changed.append((REACH_SCRIPT, 1))
        print(f'  {"FIXED " if a.apply else "would fix"} {REACH_SCRIPT}: ZENODO_RECORD_ID -> {rec_id}')

    cache = os.path.join(ROOT, *STALE_CACHE.split('/'))
    if os.path.exists(cache):
        if a.apply:
            os.remove(cache)
        print(f'  {"REMOVED" if a.apply else "would remove"} stale cache {STALE_CACHE}')

    print(f'\n{"applied" if a.apply else "dry run"}: {sum(n for _, n in changed)} replacement(s) '
          f'in {len(changed)} file(s).')
    print('\nNarrative files — update the PROSE by hand (they must keep the old '
          'number as part of the mismatch story, adding "resolved, new DOI ...")')
    for rel in NARRATIVE:
        print(f'  - {rel}')
    if a.apply:
        print('\nFinish with:\n'
              '  python scripts/external_reach.py --fetch\n'
              '  python scripts/data_index.py && python scripts/data_index.py --check\n'
              '  (cd observatory/site && npm run build)\n'
              '  commit csl-observatory + Uprava; regen the Uprava dashboard.')


if __name__ == '__main__':
    main()
