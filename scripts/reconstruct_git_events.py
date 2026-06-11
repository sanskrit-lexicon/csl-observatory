#!/usr/bin/env python3
"""OBS-T Phase 2 — reconstruct correction events from the csl-orig git history.

The correction-form layer (`build_correction_events.py`) covers 2014–2019. The
ongoing correction stream from 2019–2026 lives only in the `../csl-orig` git
history. This script mines that history: for every *correction-classified* commit
touching `v02/<dict>/<dict>.txt`, it parses the unified diff into old/new line
pairs, attributes each pair to its dictionary record (`<L>` code + `<k1>`
headword) by scanning hunk context, and emits rows in the same schema as Phase 1.

Source lines are SLP1-encoded markup, not Devanagari, so the changed lines are
kept verbatim (`old_raw`/`new_raw`) and the edit-op trace runs over them directly
(alignment only reports the characters that actually differ). Only the clean
`<k1>` headword token is transliterated SLP1->IAST.

Sources
-------
* `../csl-orig` git history (sibling repo; fully reproducible offline)
* `scripts/contributors_map.json`            — author alias -> canonical login

Outputs
-------
* `observatory/site/src/data/correction_events_git.csv`   — git-layer events
* `observatory/site/src/data/correction_events_all.csv`   — form + git, deduped
* `observatory/site/src/data/correction_events_git.meta.json`

Usage:  python scripts/reconstruct_git_events.py
"""
import csv, json, os, re, subprocess, sys, hashlib, unicodedata
from collections import Counter
from datetime import datetime, timezone
sys.stdout.reconfigure(encoding='utf-8'); sys.stderr.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
GH_ROOT = os.path.dirname(ROOT)
CSL_ORIG = os.path.join(GH_ROOT, 'csl-orig')
MAP = os.path.join(HERE, 'contributors_map.json')
DATA = os.path.join(ROOT, 'observatory', 'site', 'src', 'data')
OUT_GIT = os.path.join(DATA, 'correction_events_git.csv')
OUT_ALL = os.path.join(DATA, 'correction_events_all.csv')
OUT_META = os.path.join(DATA, 'correction_events_git.meta.json')
FORM_CSV = os.path.join(DATA, 'correction_events.csv')

SCHEMA_VERSION = '1.0.0'
MAX_DP = 1500           # skip detailed edit-op DP above this combined line length
MAX_PAIRS_PER_COMMIT = 250  # above this a commit is a bulk reformat, not a targeted fix
csv.field_size_limit(10_000_000)

# reuse Phase-1 helpers and OBS-Q git classifier/resolver
sys.path.insert(0, HERE)
from build_correction_events import edit_ops, detect_script, empirical_cluster  # noqa: E402
from obs_q_correction import classify, load_resolver as load_git_resolver        # noqa: E402

FIELDS = ['event_id', 'date', 'source_layer', 'dict', 'lcode', 'headword_iast',
          'old_iast', 'new_iast', 'old_raw', 'new_raw', 'inline_comment',
          'edit_ops', 'edit_distance', 'script_old', 'script_new', 'comment_raw',
          'error_type_empirical', 'corrector', 'corrector_name', 'latency_days',
          'evidence_level']

# --------------------------------------------------------------------- SLP1
_SLP1 = {
    'a': 'a', 'A': 'ā', 'i': 'i', 'I': 'ī', 'u': 'u', 'U': 'ū', 'f': 'ṛ', 'F': 'ṝ',
    'x': 'ḷ', 'X': 'ḹ', 'e': 'e', 'E': 'ai', 'o': 'o', 'O': 'au', 'M': 'ṃ', 'H': 'ḥ',
    '~': 'm̐', 'k': 'k', 'K': 'kh', 'g': 'g', 'G': 'gh', 'N': 'ṅ', 'c': 'c', 'C': 'ch',
    'j': 'j', 'J': 'jh', 'Y': 'ñ', 'w': 'ṭ', 'W': 'ṭh', 'q': 'ḍ', 'Q': 'ḍh', 'R': 'ṇ',
    't': 't', 'T': 'th', 'd': 'd', 'D': 'dh', 'n': 'n', 'p': 'p', 'P': 'ph', 'b': 'b',
    'B': 'bh', 'm': 'm', 'y': 'y', 'r': 'r', 'l': 'l', 'v': 'v', 'S': 'ś', 'z': 'ṣ',
    's': 's', 'h': 'h', 'L': 'ḻ', "'": '’', '˚': '°', '—': '-',
    '/': '', '\\': '', '^': '', '+': '', '|': '', '&': '',
}


def slp1_to_iast(tok):
    return unicodedata.normalize('NFC', ''.join(_SLP1.get(c, c) for c in tok))


_L_RE = re.compile(r'<L>(\S+?)<')
_K1_RE = re.compile(r'<k1>([^<]*)')


# --------------------------------------------------------------------- git log
def correction_commits():
    """Yield (sha, date_iso, login) for correction-classified v02 commits."""
    resolve, bots = load_git_resolver()
    US, RS = '\x1f', '\x1e'
    fmt = f'{RS}%H{US}%ae{US}%an{US}%ad{US}%s'
    out = subprocess.run(
        ['git', '-C', CSL_ORIG, 'log', f'--pretty=format:{fmt}',
         '--date=format:%Y-%m-%d', '--', 'v02'],
        capture_output=True, encoding='utf-8', errors='replace').stdout
    for rec in out.split(RS):
        if not rec.strip():
            continue
        parts = rec.strip().split(US)
        if len(parts) < 5:
            continue
        sha, ae, an, date, subj = parts[0], parts[1], parts[2], parts[3], US.join(parts[4:])
        if classify(subj) != 'correction':
            continue
        login = resolve(ae, an)
        if login in bots:
            continue
        yield sha, date, login, subj


# --------------------------------------------------------------------- diff parse
def parse_show(sha):
    """Return (pairs, bulk_skipped). pairs = (dict, lcode, k1, old, new) tuples.
    A commit changing more than MAX_PAIRS_PER_COMMIT lines is treated as a bulk
    reformat (not a targeted correction) and skipped wholesale."""
    # Stream the diff (Popen) instead of buffering it: a bulk commit's diff can
    # be gigabytes, so we read line-by-line and abort early — memory stays bounded
    # no matter how large the commit.
    proc = subprocess.Popen(
        ['git', '-C', CSL_ORIG, 'show', sha, '-U10', '--no-color', '--no-renames',
         '--', 'v02'],
        stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
        encoding='utf-8', errors='replace')
    cur_dict = None
    lcode = k1 = ''
    dels, adds = [], []

    def flush(acc):
        for old_line, new_line in zip(dels, adds):
            acc.append((cur_dict, lcode, k1, old_line, new_line))
        dels.clear(); adds.clear()

    acc = []
    for raw in proc.stdout:
        line = raw.rstrip('\n')
        if len(acc) + len(dels) > MAX_PAIRS_PER_COMMIT:
            proc.kill(); proc.stdout.close(); proc.wait()
            return [], True   # bulk reformat — discard, flag (bounded memory)
        if line.startswith('+++ b/'):
            flush(acc)
            seg = line[6:].strip().split('/')
            cur_dict = seg[1] if len(seg) >= 2 and seg[0] == 'v02' else None
            lcode = k1 = ''
            continue
        if line.startswith('@@'):
            flush(acc)
            continue
        if cur_dict is None:
            continue
        if line.startswith('-') and not line.startswith('---'):
            body = line[1:]
            m = _L_RE.search(body); k = _K1_RE.search(body)
            if m: lcode = m.group(1)
            if k: k1 = k.group(1)
            dels.append(body)
        elif line.startswith('+') and not line.startswith('+++'):
            body = line[1:]
            m = _L_RE.search(body); k = _K1_RE.search(body)
            if m: lcode = m.group(1)
            if k: k1 = k.group(1)
            adds.append(body)
        else:  # context line (' ') or other — update record markers, break the run
            m = _L_RE.search(line[1:] if line[:1] == ' ' else line)
            k = _K1_RE.search(line[1:] if line[:1] == ' ' else line)
            if m: lcode = m.group(1)
            if k: k1 = k.group(1)
            flush(acc)
    flush(acc)
    proc.stdout.close(); proc.wait()
    return acc, False


def main():
    if not os.path.isdir(os.path.join(CSL_ORIG, 'v02')):
        sys.exit(f'csl-orig not found at {CSL_ORIG} (expected sibling)')
    with open(MAP, encoding='utf-8') as f:
        realname = {k: v.get('real_name', k) for k, v in json.load(f).items()
                    if isinstance(v, dict)}

    rows = []
    n_commits = n_bulk = 0
    for sha, date, login, subj in correction_commits():
        n_commits += 1
        pairs, bulk = parse_show(sha)
        if bulk:
            n_bulk += 1
            continue
        for cur_dict, lcode, k1, old_line, new_line in pairs:
            if old_line == new_line or not cur_dict:
                continue
            if old_line.strip() == '' or new_line.strip() == '':
                pass  # keep pure ins/del-of-blank? skip whitespace-only noise
            if len(old_line) + len(new_line) <= MAX_DP:
                ops, dist = edit_ops(old_line, new_line)
                ops_json = json.dumps(ops, ensure_ascii=False)
            else:
                ops_json, dist = '[]', abs(len(old_line) - len(new_line))
            eid = hashlib.sha1(
                ('git|' + sha[:12] + '|' + cur_dict + '|' + lcode + '|'
                 + old_line + '|' + new_line).encode('utf-8')).hexdigest()[:16]
            rows.append({
                'event_id': eid, 'date': date, 'source_layer': 'git',
                'dict': cur_dict, 'lcode': lcode,
                'headword_iast': slp1_to_iast(k1) if k1 else '',
                'old_iast': old_line, 'new_iast': new_line,
                'old_raw': old_line, 'new_raw': new_line, 'inline_comment': '',
                'edit_ops': ops_json, 'edit_distance': dist,
                'script_old': detect_script(old_line), 'script_new': detect_script(new_line),
                'comment_raw': subj, 'error_type_empirical': empirical_cluster(subj),
                'corrector': login, 'corrector_name': realname.get(login, login),
                'latency_days': '', 'evidence_level': 'observed',
            })

    # de-dup exact repeats within the git layer
    seen, git_rows = set(), []
    for r in rows:
        key = (r['dict'], r['lcode'], r['old_raw'], r['new_raw'])
        if key in seen:
            continue
        seen.add(key); git_rows.append(r)
    git_rows.sort(key=lambda r: (r['date'], r['event_id']))

    with open(OUT_GIT, 'w', encoding='utf-8', newline='') as f:
        w = csv.DictWriter(f, fieldnames=FIELDS); w.writeheader(); w.writerows(git_rows)

    # ---- merged all-layers table (form + git) ----
    form_rows = []
    if os.path.exists(FORM_CSV):
        with open(FORM_CSV, encoding='utf-8') as f:
            form_rows = list(csv.DictReader(f))
    all_rows = form_rows + git_rows
    all_rows.sort(key=lambda r: (r.get('date', ''), r['event_id']))
    with open(OUT_ALL, 'w', encoding='utf-8', newline='') as f:
        w = csv.DictWriter(f, fieldnames=FIELDS); w.writeheader(); w.writerows(all_rows)

    # ---- meta ----
    by_year = Counter(r['date'][:4] for r in git_rows if r['date'])
    by_dict = Counter(r['dict'] for r in git_rows)
    clusters = Counter(r['error_type_empirical'] for r in git_rows)
    meta = {
        'schemaVersion': SCHEMA_VERSION,
        'generatedAt': datetime.now(timezone.utc).isoformat(),
        'sourcePath': '../csl-orig (git history, v02)',
        'recordCount': len(git_rows),
        'assumptions': [
            'Only correction-classified commits (obs_q classify()) are mined.',
            'Old/new are SLP1-encoded source lines kept verbatim; edit ops run over '
            'them directly (alignment reports only differing characters).',
            'lcode/<k1> attributed from the nearest record markers within the hunk '
            '(-U10 context); only <k1> is transliterated SLP1->IAST.',
            'Change runs paired positionally (i-th deletion with i-th addition).',
        ],
        'warnings': [f'{n_bulk} commits skipped as bulk reformats '
                     f'(>{MAX_PAIRS_PER_COMMIT} changed lines).'] if n_bulk else [],
        'stats': {
            'commitsMined': n_commits, 'commitsSkippedBulk': n_bulk,
            'eventsRaw': len(rows), 'eventsDeduped': len(git_rows),
            'dateRange': [git_rows[0]['date'], git_rows[-1]['date']] if git_rows else [],
            'byYear': sorted(by_year.items()),
            'topDicts': by_dict.most_common(15),
            'clusters': clusters.most_common(),
            'allLayersTotal': len(all_rows),
        },
    }
    with open(OUT_META, 'w', encoding='utf-8') as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)

    print(f'wrote {OUT_GIT}  ({len(git_rows)} git events from {n_commits} commits, '
          f'{n_bulk} bulk-skipped)')
    print(f'wrote {OUT_ALL}  ({len(all_rows)} all-layer events)')
    print(f'wrote {OUT_META}')
    print(f'  git date range: {meta["stats"]["dateRange"]}  by year: {sorted(by_year.items())}')
    print(f'  top dicts: {by_dict.most_common(8)}')


if __name__ == '__main__':
    main()
