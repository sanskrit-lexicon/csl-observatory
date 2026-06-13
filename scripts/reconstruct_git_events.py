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
from build_correction_events import edit_ops, detect_script, empirical_cluster, public_identity  # noqa: E402
from obs_q_correction import classify, load_resolver as load_git_resolver        # noqa: E402

FIELDS = ['event_id', 'date', 'source_layer', 'dict', 'lcode', 'headword_iast',
          'old_iast', 'new_iast', 'old_raw', 'new_raw', 'inline_comment',
          'edit_ops', 'edit_distance', 'script_old', 'script_new', 'comment_raw',
          'source_path', 'commit_sha', 'edit_space', 'error_type_empirical',
          'corrector', 'corrector_name', 'latency_days', 'evidence_level']

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
_BRACE_RE = re.compile(r'\{#(.*?)#\}')
_PAIR_TAG_RE = re.compile(r'<(s|s1|s2|s3|bot)>(.*?)</\1>')
_FIELD_TAG_RE = re.compile(r'<(k1|k2|k|h)>([^<]*)')


def entry_dict(path):
    """Return dict code only for v02/<dict>/<dict>.txt entry files."""
    seg = path.split('/')
    if len(seg) == 3 and seg[0] == 'v02' and seg[2] == f'{seg[1]}.txt':
        return seg[1]
    return None


def changed_pos(old, new):
    n = min(len(old), len(new))
    i = 0
    while i < n and old[i] == new[i]:
        i += 1
    return i


def _contains_pos(start, end, pos):
    return start <= pos < end or (pos == end and start < end)


def sanskrit_span_at(line, pos):
    """Return SLP1-ish Sanskrit content around pos, if the changed span is inside it."""
    if not line:
        return None
    for m in _BRACE_RE.finditer(line):
        start, end = m.start(1), m.end(1)
        if _contains_pos(start, end, pos):
            return m.group(1)
    for m in _PAIR_TAG_RE.finditer(line):
        start, end = m.start(2), m.end(2)
        if _contains_pos(start, end, pos):
            return m.group(2)
    for m in _FIELD_TAG_RE.finditer(line):
        start, end = m.start(2), m.end(2)
        if _contains_pos(start, end, pos):
            return m.group(2)
    return None


def git_edit_payload(old_line, new_line):
    """Choose the character space for git edit ops and display fields."""
    pos = changed_pos(old_line, new_line)
    old_span = sanskrit_span_at(old_line, pos) if old_line else None
    new_span = sanskrit_span_at(new_line, pos) if new_line else None
    if old_span is not None or new_span is not None:
        old_iast = slp1_to_iast(old_span or '')
        new_iast = slp1_to_iast(new_span or '')
        if len(old_iast) + len(new_iast) <= MAX_DP:
            ops, dist = edit_ops(old_iast, new_iast)
        else:
            ops, dist = [], abs(len(old_iast) - len(new_iast))
        return old_iast, new_iast, ops, dist, 'iast'

    ref = old_line or new_line
    edit_space = 'markup_raw' if any(ch in ref for ch in '<>{}#') else 'slp1_raw'
    if len(old_line) + len(new_line) <= MAX_DP:
        ops, dist = edit_ops(old_line, new_line)
    else:
        ops, dist = [], abs(len(old_line) - len(new_line))
    return old_line, new_line, ops, dist, edit_space


# --------------------------------------------------------------------- git log
def correction_commits():
    """Yield (sha, date_iso, login, subj, author_email) for correction commits.

    `author_email` is the raw, unresolved git email; callers need it to redact
    unmapped authors (resolve() returns only the email local part)."""
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
        yield sha, date, login, subj, ae


# --------------------------------------------------------------------- diff parse
def parse_show(sha):
    """Return (pairs, bulk_skipped, stats).

    pairs = (source_path, dict, lcode, k1, old, new, change_kind) tuples.
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
    cur_path = ''
    cur_dict = None
    lcode = k1 = ''
    dels, adds = [], []
    stats = Counter()

    def flush(acc):
        common = min(len(dels), len(adds))
        if len(dels) != len(adds):
            stats['unequal_runs'] += 1
            stats['unmatched_deletions'] += max(0, len(dels) - len(adds))
            stats['unmatched_additions'] += max(0, len(adds) - len(dels))
        for i in range(common):
            stats['replacements'] += 1
            acc.append((cur_path, cur_dict, lcode, k1, dels[i], adds[i], 'replace'))
        for old_line in dels[common:]:
            stats['deletions'] += 1
            acc.append((cur_path, cur_dict, lcode, k1, old_line, '', 'delete'))
        for new_line in adds[common:]:
            stats['insertions'] += 1
            acc.append((cur_path, cur_dict, lcode, k1, '', new_line, 'insert'))
        dels.clear(); adds.clear()

    acc = []
    for raw in proc.stdout:
        line = raw.rstrip('\n')
        if len(acc) + len(dels) + len(adds) > MAX_PAIRS_PER_COMMIT:
            proc.kill(); proc.stdout.close(); proc.wait()
            return [], True, stats   # bulk reformat — discard, flag (bounded memory)
        if line.startswith('+++ b/'):
            flush(acc)
            cur_path = line[6:].strip()
            cur_dict = entry_dict(cur_path)
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
    return acc, False, stats


def merge_only():
    """Rebuild correction_events_all.csv from the existing form + git CSVs,
    without re-mining git (use after re-running Phase 1)."""
    git_rows = list(csv.DictReader(open(OUT_GIT, encoding='utf-8'))) \
        if os.path.exists(OUT_GIT) else []
    form_rows = list(csv.DictReader(open(FORM_CSV, encoding='utf-8'))) \
        if os.path.exists(FORM_CSV) else []
    for row in form_rows + git_rows:
        for field in FIELDS:
            row.setdefault(field, '')
    all_rows = form_rows + git_rows
    all_rows.sort(key=lambda r: (r.get('date', ''), r['event_id']))
    with open(OUT_ALL, 'w', encoding='utf-8', newline='') as f:
        w = csv.DictWriter(f, fieldnames=FIELDS); w.writeheader(); w.writerows(all_rows)
    print(f'merge-only: wrote {OUT_ALL}  '
          f'({len(form_rows)} form + {len(git_rows)} git = {len(all_rows)})')


def main():
    if '--merge-only' in sys.argv:
        merge_only()
        return
    if not os.path.isdir(os.path.join(CSL_ORIG, 'v02')):
        sys.exit(f'csl-orig not found at {CSL_ORIG} (expected sibling)')
    with open(MAP, encoding='utf-8') as f:
        realname = {k: v.get('real_name', k) for k, v in json.load(f).items()
                    if isinstance(v, dict)}
    # canonical logins: any author resolve() did NOT map falls back to the email
    # local part (or bare name), which must be pseudonymised, not published.
    canonical = set(realname)

    rows = []
    n_commits = n_bulk = n_entry_commits = 0
    parse_stats = Counter()
    events_by_kind = Counter()
    for sha, date, login, subj, ae in correction_commits():
        n_commits += 1
        pairs, bulk, stats = parse_show(sha)
        parse_stats.update(stats)
        if bulk:
            n_bulk += 1
            continue
        before = len(rows)
        raw_author = '' if login in canonical else ae
        safe_login, safe_name = public_identity(
            login, realname.get(login, login), raw=raw_author, layer='git')
        for source_path, cur_dict, lcode, k1, old_line, new_line, change_kind in pairs:
            if old_line == new_line or not cur_dict:
                continue
            if old_line.strip() == '' or new_line.strip() == '':
                pass  # keep pure ins/del-of-blank? skip whitespace-only noise
            old_iast, new_iast, ops, dist, edit_space = git_edit_payload(old_line, new_line)
            ops_json = json.dumps(ops, ensure_ascii=False)
            eid = hashlib.sha1(
                ('git|' + sha[:12] + '|' + source_path + '|' + cur_dict + '|'
                 + lcode + '|' + change_kind + '|' + old_line + '|'
                 + new_line).encode('utf-8')).hexdigest()[:16]
            events_by_kind[change_kind] += 1
            rows.append({
                'event_id': eid, 'date': date, 'source_layer': 'git',
                'source_path': source_path, 'commit_sha': sha,
                'dict': cur_dict, 'lcode': lcode,
                'headword_iast': slp1_to_iast(k1) if k1 else '',
                'old_iast': old_iast, 'new_iast': new_iast,
                'old_raw': old_line, 'new_raw': new_line, 'inline_comment': '',
                'edit_ops': ops_json, 'edit_distance': dist,
                'edit_space': edit_space,
                'script_old': detect_script(old_iast), 'script_new': detect_script(new_iast),
                'comment_raw': subj, 'error_type_empirical': empirical_cluster(subj),
                'corrector': safe_login, 'corrector_name': safe_name,
                'latency_days': '', 'evidence_level': 'observed',
            })
        if len(rows) > before:   # count only commits that emitted >=1 entry event
            n_entry_commits += 1

    # de-dup exact repeats within the git layer
    seen, git_rows = set(), []
    for r in rows:
        key = (r['source_path'], r['dict'], r['lcode'], r['old_raw'], r['new_raw'])
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
    for row in form_rows + git_rows:
        for field in FIELDS:
            row.setdefault(field, '')
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
            'Only v02/<dict>/<dict>.txt dictionary entry files are emitted; helper, '
            'metadata, header, and update files under v02 are ignored.',
            'Old/new raw source lines are kept verbatim; edit ops run over IAST only '
            'when the changed span is inside Sanskrit-bearing markup, otherwise over '
            'the raw source space marked by edit_space.',
            'lcode/<k1> attributed from the nearest record markers within the hunk '
            '(-U10 context); only <k1> is transliterated SLP1->IAST.',
            'Unequal delete/add runs emit paired replacements plus explicit insertion '
            'or deletion events for unmatched lines.',
        ],
        'warnings': [f'{n_bulk} commits skipped as bulk reformats '
                     f'(>{MAX_PAIRS_PER_COMMIT} changed lines).'] if n_bulk else [],
        'stats': {
            'commitsMined': n_commits, 'commitsSkippedBulk': n_bulk,
            'commitsWithEntryEvents': n_entry_commits,
            'eventsRaw': len(rows), 'eventsDeduped': len(git_rows),
            'eventsByChangeKind': events_by_kind.most_common(),
            'diffPairing': dict(parse_stats),
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
