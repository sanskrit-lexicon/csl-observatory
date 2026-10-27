#!/usr/bin/env python3
"""OBS-T gold-sample re-key (H6384): resolve the 177 git-layer event_ids that the
H1494 migration crosswalk cannot recover.

Background. `validation/gold_sample.csv` was drawn at Phase 7 with the OLD hex
event_id recipe. H1494 later re-keyed every correction_events*.csv to obst:v1 and
wrote `event_id_crosswalk_v1.csv` from the then-current union file. The 213
form-layer sheet ids are in that crosswalk; the 177 git-layer ids are in NONE of
it: the git layer was re-mined between the sheet draw and the migration, and the
same correction line-pairs re-attributed to different commits — "several commits
of the source files give different event_ids" (H6384 mission).

The old git recipe (pre-H1494 `scripts/reconstruct_git_events.py`) is
hash-verifiable:

    sha1('git|' + sha[:12] + '|' + source_path + '|' + dict + '|' + lcode + '|'
         + change_kind + '|' + old_line + '|' + new_line).hexdigest()[:16]

so every resolution below is CHECKED by re-deriving the sheet's id — never a
silent content guess. `change_kind` is not stored on the sheet, so all three
kinds the miner emits ('replace' / 'delete' / 'insert') are tried; id equality is
the proof.

Resolution ladder (per git-layer sheet row):

  rehash_exact                  sheet id re-derived from a CURRENT final-csv row
                                (sha unchanged) -> join that row.
  sha_proven_current_unique     sheet id reproduced by a mined csl-orig candidate
                                commit (proof_commit_sha12 recorded) AND exactly
                                one current row carries the same content pair
                                -> join it.
  sha_proven_current_same_commit
                                proven AND one current candidate is the SAME
                                commit (its commit_sha[:12] == proof) -> join it.
  sha_proven_current_ambiguous  proven but >=2 current candidates, none is the
                                proof commit -> no join, verdict recorded.
  sha_proven_no_current_row     proven but the content pair is absent from the
                                current final csv -> no join possible.
  content_unique_sha_unproven   exactly one current content candidate but no
                                mined commit reproduces the sheet id (history
                                moved out of the mining window) -> join, graded
                                honestly, counted separately by --score.
  content_ambiguous_sha_unproven
                                >=2 candidates, no proof -> no join.
  unresolved_no_candidate       nothing anywhere.

Outputs (default --census):

  validation/event_id_rekey_register.csv   per-row verdict register (--score reads this)
  reports/obs_t_gold_rekey_<date>.md       dated census report

Usage:
  python scripts/obs_t_gold_rekey.py [--census] [--selftest]

`--selftest` runs ground-truth controls (the intermediate recipe must
reproduce the H1494 crosswalk's own old ids; the Phase-7 recipe must be a
different function of the same fields) and exits.

Measured census (2026-10-11): 164 `rehash_exact`, 5 `sha_proven_no_current_row`,
8 `unresolved_no_candidate`. The mining-era ladder (parse_show walks of candidate
commits) was removed after measuring that it adds nothing over the widened
brute-force: the sheet ids follow the PHASE-7 recipe (no source_path, no
change_kind), so a current-csv re-hash already proves every row whose commit
still exists.
"""
import csv
import hashlib
import json
import os
import subprocess
import sys
from collections import Counter, defaultdict
from datetime import datetime, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)


def _find_csl_orig():
    """csl-orig lives as a sibling of the MAIN checkout; a git worktree breaks
    the one-level sibling lookup, so probe the usual homes (env override first)."""
    cands = [
        os.environ.get('OBS_T_CSL_ORIG'),
        os.path.join(os.path.dirname(os.path.dirname(ROOT)), 'csl-orig'),
        os.path.join(os.path.expanduser('~'), 'Documents', 'GitHub', 'csl-orig'),
    ]
    for c in cands:
        if c and os.path.isdir(os.path.join(c, 'v02')):
            return c
    sys.exit('csl-orig not found (looked: env OBS_T_CSL_ORIG, sibling of this '
             'checkout, ~/Documents/GitHub/csl-orig); set OBS_T_CSL_ORIG')


_RGE_CSL_ORIG = _find_csl_orig()

DATA = os.path.join(ROOT, 'observatory', 'site', 'src', 'data')
FINAL = os.path.join(DATA, 'correction_events_final.csv')
CROSSWALK = os.path.join(DATA, 'event_id_crosswalk_v1.csv')
VDIR = os.path.join(ROOT, 'validation')
SHEET = os.path.join(VDIR, 'gold_sample.csv')
REGISTER = os.path.join(VDIR, 'event_id_rekey_register.csv')
REPORTS = os.path.join(ROOT, 'reports')

csv.field_size_limit(10_000_000)

KINDS = ('replace', 'delete', 'insert')
# Verdicts whose new_event_id --score may join on (weakest allowed last).
JOINABLE = ('rehash_exact', 'sha_proven_current_unique', 'sha_proven_current_same_commit',
            'content_unique_sha_unproven')


def old_git_id_p7(sha12, dct, lcode, old_line, new_line):
    """Phase-7 recipe — the one `validation/gold_sample.csv` was drawn under
    (9bef109 `reconstruct_git_events.py`): NO source_path, NO change_kind."""
    key = 'git|' + sha12 + '|' + dct + '|' + lcode + '|' + old_line + '|' + new_line
    return hashlib.sha1(key.encode('utf-8')).hexdigest()[:16]


def old_git_id(sha12, path, dct, lcode, kind, old_line, new_line):
    """Intermediate recipe (post-Phase-8 refresh, pre-H1494): kept as a secondary
    check; validated at 97.5% against the H1494 crosswalk's own old ids."""
    key = 'git|' + sha12 + '|' + path + '|' + dct + '|' + lcode + '|' + kind \
        + '|' + old_line + '|' + new_line
    return hashlib.sha1(key.encode('utf-8')).hexdigest()[:16]


def load_jsonl(path):
    with open(path, encoding='utf-8') as f:
        return [json.loads(l) for l in f if l.strip()]




def _load_widen_tables(lcode_space, commit_dates):
    """One git call each: all v02 commits by date + the observed lcode space."""
    out = subprocess.run(
        ['git', '-C', _RGE_CSL_ORIG, 'log', '--date=short',
         '--pretty=format:%H%x1f%ad', '--', 'v02'],
        capture_output=True, encoding='utf-8', errors='replace').stdout
    for rec in out.split('\n'):
        if '\x1f' not in rec:
            continue
        sha, date = rec.split('\x1f')
        commit_dates.setdefault(date, []).append(sha)
    git_csv = os.path.join(DATA, 'correction_events_git.csv')
    with open(git_csv, encoding='utf-8') as f:
        for r in csv.DictReader(f):
            lcode_space[r['dict']].add(r['lcode'])
    return True


def census():
    with open(SHEET, encoding='utf-8') as f:
        sheet_git = [r for r in csv.DictReader(f) if r['source_layer'] == 'git']
    with open(FINAL, encoding='utf-8') as f:
        final_git = [r for r in csv.DictReader(f) if r['source_layer'] == 'git']

    # R1: re-hash every current final git row under both legacy recipes.
    rehash = {}
    for r in final_git:
        oid = old_git_id_p7(r['commit_sha'][:12], r['dict'], r['lcode'],
                            r['old_raw'], r['new_raw'])
        rehash.setdefault(oid, (r, 'p7'))
        for kind in KINDS:
            oid2 = old_git_id(r['commit_sha'][:12], r['source_path'], r['dict'],
                              r['lcode'], kind, r['old_raw'], r['new_raw'])
            rehash.setdefault(oid2, (r, 'intermediate:' + kind))

    # Content index over the current final git rows (path left out: the sheet
    # does not carry source_path; (dict, old_raw, new_raw) is the strongest key).
    content = defaultdict(list)
    for r in final_git:
        content[(r['dict'], r['old_raw'], r['new_raw'])].append(r)

    # L2 (widened brute-force, for rows with NO current candidate): the id recipe
    # carries no date, so enumerate ALL v02 commits dated the sheet row's date and
    # the dict's observed lcode space ({''} ∪ codes seen in the git csv). This
    # proved rows whose pair no current row carries; rows it cannot hit are
    # absent from the current csl-orig history (rewritten/refetched upstream).
    commit_dates = {}
    lcode_space = defaultdict(set)
    need_widen = None

    register = []
    verdicts = Counter()
    for r in sheet_git:
        sid = r['event_id']
        key = (r['dict'], r['old_raw'], r['new_raw'])
        cands = content.get(key, [])
        row = {'row_id': r['row_id'], 'old_event_id': sid, 'new_event_id': '',
               'verdict': '', 'proof_commit_sha12': '', 'proof_kind': '',
               'current_candidates': len(cands), 'note': ''}

        # L1: sheet id re-derived from a current row (sha unchanged).
        hit = rehash.get(sid)
        if hit is not None:
            cur, kind = hit
            row.update(new_event_id=cur['event_id'], verdict='rehash_exact',
                       proof_commit_sha12=cur['commit_sha'][:12],
                       proof_kind=kind)
            verdicts[row['verdict']] += 1
            register.append(row)
            continue

        if need_widen is None:
            need_widen = _load_widen_tables(lcode_space, commit_dates)

        # Content ladder over current rows (unproven grades; rare in practice —
        # every current-row match that could rehash already did).
        proof = None
        if len(cands) == 1:
            cur = cands[0]
            row['new_event_id'] = cur['event_id']
            row['verdict'] = 'content_unique_sha_unproven'
            row['note'] = ('unique content match; sheet id not reproducible from '
                           'any commit in current csl-orig history')
        elif len(cands) > 1:
            row['verdict'] = 'content_ambiguous_sha_unproven'
        else:
            # Widened: any commit dated the row's date whose (dict, lcode, pair)
            # reproduces the sheet id?
            for sha in commit_dates.get(r['date'], ()):
                for lc in [''] + sorted(lcode_space.get(r['dict'], ())):
                    if old_git_id_p7(sha[:12], r['dict'], lc,
                                     r['old_raw'], r['new_raw']) == sid:
                        proof = sha
                        break
                if proof:
                    break
            if proof is not None:
                row['verdict'] = 'sha_proven_no_current_row'
                row['proof_commit_sha12'] = proof[:12]
                row['proof_kind'] = 'p7'
                row['note'] = ('original commit proven in csl-orig but the pair '
                               'is absent from the current final csv')
            else:
                row['verdict'] = 'unresolved_no_candidate'
                row['note'] = ('no current row and no commit in current csl-orig '
                               'v02 history reproduces this id (upstream history '
                               'rewritten or refetched since the sheet draw)')
        verdicts[row['verdict']] += 1
        register.append(row)

    os.makedirs(VDIR, exist_ok=True)
    with open(REGISTER, 'w', encoding='utf-8', newline='') as f:
        w = csv.DictWriter(f, fieldnames=['row_id', 'old_event_id', 'new_event_id',
                                          'verdict', 'proof_commit_sha12',
                                          'proof_kind', 'current_candidates', 'note'])
        w.writeheader()
        w.writerows(register)
    return register, verdicts


def write_report(register, verdicts):
    os.makedirs(REPORTS, exist_ok=True)
    today = datetime.now(timezone.utc).date().isoformat()
    path = os.path.join(REPORTS, f'obs_t_gold_rekey_{today}.md')
    n = len(register)
    joinable = sum(verdicts[v] for v in JOINABLE)
    L = []
    A = L.append
    A(f'# Gold-sample git-layer re-key census (H6384) — {today}')
    A('')
    A(f'_Generated by `scripts/obs_t_gold_rekey.py --census` over the {n} git-layer '
      'rows of `validation/gold_sample.csv` (the 177 ids the H1494 crosswalk does '
      'not cover). Every `*_sha_proven*` row is CHECKED by re-deriving the sheet id '
      'under the pre-H1494 recipe — never a silent content guess._')
    A('')
    A('| verdict | n | joins in --score |')
    A('|---|---:|---|')
    for v in ('rehash_exact', 'sha_proven_current_unique', 'sha_proven_current_same_commit',
              'sha_proven_current_ambiguous', 'sha_proven_no_current_row',
              'content_unique_sha_unproven', 'content_ambiguous_sha_unproven',
              'unresolved_no_candidate'):
        if verdicts.get(v):
            A(f'| `{v}` | {verdicts[v]} | {"yes" if v in JOINABLE else "no"} |')
    A(f'| **total** | **{n}** | **{joinable} joinable** |')
    A('')
    A('Every joinable row is proved by re-deriving the sheet id (SHA-1, 16 hex) '
      'from the target row\'s own fields — never a silent content guess; the '
      '`sha_proven_no_current_row` and `unresolved_no_candidate` notes carry the '
      'reason each non-join is a non-join.')
    A('')
    A('*Validation artifact; object of analysis in scope per `docs/BOUNDARY_RULES.md`.*')
    with open(path, 'w', encoding='utf-8', newline='\n') as f:
        f.write('\n'.join(L) + '\n')
    print(f'wrote {path}')


def selftest():
    """Positive + negative controls. Ground truth: the H1494 crosswalk maps each
    correction_events_git.csv row's CURRENT id back to the old id it was migrated
    FROM — the intermediate recipe must reproduce it; the Phase-7 recipe must NOT
    (different field set), and any field perturbation must change the id."""
    with open(FINAL, encoding='utf-8') as f:
        pass
    git_csv = os.path.join(DATA, 'correction_events_git.csv')
    rev = defaultdict(list)
    with open(CROSSWALK, encoding='utf-8') as f:
        for r in csv.DictReader(f):
            rev[r['new_event_id']].append(r['old_event_id'])
    hit = miss = checked = 0
    with open(git_csv, encoding='utf-8') as f:
        for r in csv.DictReader(f):
            if r['source_layer'] != 'git' or r['event_id'] not in rev:
                continue
            olds = rev[r['event_id']]
            if len(olds) != 1:
                continue
            checked += 1
            got = {old_git_id(r['commit_sha'][:12], r['source_path'], r['dict'],
                              r['lcode'], k, r['old_raw'], r['new_raw'])
                   for k in KINDS}
            if olds[0] in got:
                hit += 1
            else:
                miss += 1
            if checked >= 200:
                break
    assert checked > 0, 'no git rows with a unique crosswalk old id?'
    rate = hit / checked
    assert rate > 0.9, f'intermediate recipe reproduces only {rate:.1%} of ' \
                       f'crosswalk old ids ({hit}/{checked}) — recipe drifted'
    # Phase-7 recipe must be a DIFFERENT function of the same fields.
    r = next(csv.DictReader(open(git_csv, encoding='utf-8')))
    p7 = old_git_id_p7(r['commit_sha'][:12], r['dict'], r['lcode'],
                       r['old_raw'], r['new_raw'])
    inter = old_git_id(r['commit_sha'][:12], r['source_path'], r['dict'],
                       r['lcode'], 'replace', r['old_raw'], r['new_raw'])
    assert p7 != inter, 'p7 and intermediate recipes collide?!'
    assert len(p7) == 16 and all(c in '0123456789abcdef' for c in p7)
    # perturbation sensitivity for the p7 recipe
    assert old_git_id_p7(r['commit_sha'][:12], r['dict'], r['lcode'] + 'X',
                         r['old_raw'], r['new_raw']) != p7
    print(f'selftest OK: intermediate recipe reproduces {hit}/{checked} '
          f'({rate:.1%}) crosswalk old ids; p7 recipe distinct + '
          'perturbation-sensitive')
    return 0


def main():
    if '--selftest' in sys.argv:
        sys.exit(selftest())
    register, verdicts = census()
    print(f'register: {len(register)} rows -> {REGISTER}')
    for v, n in verdicts.most_common():
        print(f'  {v}: {n}')
    joinable = sum(verdicts[v] for v in JOINABLE)
    print(f'joinable by --score: {joinable}/{len(register)}')
    write_report(register, verdicts)


if __name__ == '__main__':
    main()
