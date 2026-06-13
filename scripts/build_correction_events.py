#!/usr/bin/env python3
"""OBS-T Phase 1 — build the unified correction-event table from the correction form.

Reads the Cologne correction-form export (`../CORRECTIONS/cfr.tsv`, the L1 layer of
the error-typology track) and produces one normalized row per correction event:
parsed, time-sorted, inline-commentary stripped from the NEW cell, Devanagari
transliterated to IAST (self-contained, stdlib only), edit-operation trace over
NFD, corrector aliases merged, and submit->corrected latency where parseable.

This is the complement of `obs_q_correction.py` (which measures *who/when/how-fast*
from git): OBS-T measures *what was wrong and how*. See
`docs/ERROR_TYPOLOGY_DESIGN.md` for the full spec.

Sources
-------
* `../CORRECTIONS/cfr.tsv`               — correction-form responses (8 tab cols)
* `scripts/contributors_map.json`        — corrector alias -> canonical login

Outputs
-------
* `observatory/site/src/data/correction_events.csv`  — the event table
* `observatory/site/src/data/correction_events.meta.json` — envelope + assumptions
* `data/schema/correction-event.schema.json`         — JSON Schema (written once)

Usage:  python scripts/build_correction_events.py
"""
import csv, json, os, re, sys, unicodedata, hashlib
from collections import Counter
from datetime import datetime, timezone
sys.stdout.reconfigure(encoding='utf-8'); sys.stderr.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
GH_ROOT = os.path.dirname(ROOT)
CFR = os.path.join(GH_ROOT, 'CORRECTIONS', 'cfr.tsv')
MAP = os.path.join(HERE, 'contributors_map.json')
DATA = os.path.join(ROOT, 'observatory', 'site', 'src', 'data')
OUT_CSV = os.path.join(DATA, 'correction_events.csv')
OUT_META = os.path.join(DATA, 'correction_events.meta.json')
SCHEMA_DIR = os.path.join(ROOT, 'data', 'schema')
OUT_SCHEMA = os.path.join(SCHEMA_DIR, 'correction-event.schema.json')

SCHEMA_VERSION = '1.0.0'
csv.field_size_limit(10_000_000)

# --------------------------------------------------------------------------- IAST
# Self-contained Devanagari (U+0900-097F) -> IAST. Deterministic, no dependency.
_V_IND = {  # independent vowels
    'अ': 'a', 'आ': 'ā', 'इ': 'i', 'ई': 'ī', 'उ': 'u', 'ऊ': 'ū',
    'ऋ': 'ṛ', 'ॠ': 'ṝ', 'ऌ': 'ḷ', 'ॡ': 'ḹ', 'ऎ': 'e', 'ए': 'e',
    'ऐ': 'ai', 'ऒ': 'o', 'ओ': 'o', 'औ': 'au',
}
_V_SIGN = {  # dependent vowel signs (matras)
    'ा': 'ā', 'ि': 'i', 'ी': 'ī', 'ु': 'u', 'ू': 'ū', 'ृ': 'ṛ', 'ॄ': 'ṝ',
    'ॢ': 'ḷ', 'ॣ': 'ḹ', 'ॆ': 'e', 'े': 'e', 'ै': 'ai', 'ॊ': 'o', 'ो': 'o', 'ौ': 'au',
}
_CONS = {
    'क': 'k', 'ख': 'kh', 'ग': 'g', 'घ': 'gh', 'ङ': 'ṅ',
    'च': 'c', 'छ': 'ch', 'ज': 'j', 'झ': 'jh', 'ञ': 'ñ',
    'ट': 'ṭ', 'ठ': 'ṭh', 'ड': 'ḍ', 'ढ': 'ḍh', 'ण': 'ṇ',
    'त': 't', 'थ': 'th', 'द': 'd', 'ध': 'dh', 'न': 'n',
    'प': 'p', 'फ': 'ph', 'ब': 'b', 'भ': 'bh', 'म': 'm',
    'य': 'y', 'र': 'r', 'ल': 'l', 'व': 'v',
    'श': 'ś', 'ष': 'ṣ', 'स': 's', 'ह': 'h', 'ळ': 'ḷ',
    # nukta-composed (handled via base too):
    'क़': 'q', 'ख़': 'ḵh', 'ग़': 'ġ', 'ज़': 'z', 'ड़': 'ṛ', 'ढ़': 'ṛh', 'फ़': 'f', 'य़': 'y',
}
_MARK = {'ं': 'ṃ', 'ः': 'ḥ', 'ँ': 'm̐', 'ऽ': "'", 'ॐ': 'oṃ', '।': '|', '॥': '||'}
_DIGIT = {d: str(i) for i, d in enumerate('०१२३४५६७८९')}
_VIRAMA = '्'
_NUKTA = '़'


def deva_to_iast(s):
    """Transliterate Devanagari runs to IAST; leave other scripts untouched."""
    out = []
    i, n = 0, len(s)
    while i < n:
        ch = s[i]
        # normalise an explicit nukta onto its base if a composed form exists
        if i + 1 < n and s[i + 1] == _NUKTA and (ch + _NUKTA) in _CONS:
            ch = ch + _NUKTA
            i += 1
        if ch in _CONS:
            out.append(_CONS[ch])
            j = i + 1
            if j < n and s[j] == _NUKTA:  # stray nukta with no composed form
                j += 1
            if j < n and s[j] == _VIRAMA:
                i = j + 1                 # bare consonant, no inherent vowel
                continue
            if j < n and s[j] in _V_SIGN:
                out.append(_V_SIGN[s[j]])
                i = j + 1
                continue
            out.append('a')               # inherent vowel
            i = j
            continue
        if ch in _V_IND:
            out.append(_V_IND[ch]); i += 1; continue
        if ch in _MARK:
            out.append(_MARK[ch]); i += 1; continue
        if ch in _DIGIT:
            out.append(_DIGIT[ch]); i += 1; continue
        if ch in _V_SIGN:                 # orphan matra (malformed) — emit vowel
            out.append(_V_SIGN[ch]); i += 1; continue
        if ch in (_VIRAMA, _NUKTA):
            i += 1; continue
        out.append(ch); i += 1            # pass through Latin/space/punct/IAST
    return unicodedata.normalize('NFC', ''.join(out))


_DEVA_RE = re.compile(r'[ऀ-ॿ]')
_LATIN_RE = re.compile(r'[A-Za-z]')

# --- Harvard-Kyoto -> IAST (the cfr form encodes roman cells in HK, e.g. PW:
#     'bharahezaravRtti' = bharaheśaravṛtti — HK z=ś, S=ṣ, R=ṛ, T=ṭ) ---
_HK = {  # longest-match keys first (3,2,1 chars)
    'lRR': 'ḹ',
    'RR': 'ṝ', 'lR': 'ḷ', 'kh': 'kh', 'gh': 'gh', 'ch': 'ch', 'jh': 'jh',
    'Th': 'ṭh', 'Dh': 'ḍh', 'th': 'th', 'dh': 'dh', 'ph': 'ph', 'bh': 'bh',
    'a': 'a', 'A': 'ā', 'i': 'i', 'I': 'ī', 'u': 'u', 'U': 'ū', 'R': 'ṛ',
    'e': 'e', 'o': 'o', 'M': 'ṃ', 'H': 'ḥ', 'k': 'k', 'g': 'g', 'G': 'ṅ',
    'c': 'c', 'j': 'j', 'J': 'ñ', 'Y': 'ñ', 'T': 'ṭ', 'D': 'ḍ', 'N': 'ṇ', 't': 't',
    'd': 'd', 'n': 'n', 'p': 'p', 'b': 'b', 'm': 'm', 'y': 'y', 'r': 'r',
    'l': 'l', 'v': 'v', 'z': 'ś', 'S': 'ṣ', 's': 's', 'h': 'h', 'L': 'ḷ',
    '˚': '°',
}
_HK_KEYS = sorted(_HK, key=len, reverse=True)


def hk_to_iast(tok):
    out, i, n = [], 0, len(tok)
    while i < n:
        for k in _HK_KEYS:
            if tok.startswith(k, i):
                out.append(_HK[k]); i += len(k); break
        else:
            out.append(tok[i]); i += 1
    return unicodedata.normalize('NFC', ''.join(out))


def looks_hk(tok):
    """A no-space roman token is Harvard-Kyoto if it carries HK-only signals —
    an internal capital (rare in English) or the HK letter z (=ś)."""
    if not any(c.isalpha() for c in tok):
        return False
    if any(c.isupper() for c in tok[1:]):
        return True
    return 'z' in tok


def normalize_to_iast(s):
    """Normalize a cfr cell to IAST: Devanagari runs first, else token-wise HK."""
    if _DEVA_RE.search(s):
        return deva_to_iast(s)
    return ' '.join(hk_to_iast(t) if looks_hk(t) else t for t in s.split(' '))


def detect_script(s):
    has_d = bool(_DEVA_RE.search(s))
    has_l = bool(_LATIN_RE.search(s))
    if has_d and has_l:
        return 'mixed'
    if has_d:
        return 'deva'
    if has_l:
        # IAST = Latin carrying combining diacritics or IAST letters
        if re.search(r'[āīūṛṝḷḹṅñṭḍṇśṣṃḥ]', s):
            return 'iast'
        if any(looks_hk(t) for t in s.split(' ')):
            return 'hk'
        return 'latin'
    return 'other'


# --------------------------------------------------------------------- NEW cell
# Lift trailing/inline commentary out of the NEW cell, conservatively.
_SPLIT_RE = re.compile(r'\s+-\s+|\s{2,}|\s*\(')


def split_new(cell):
    """Return (correction, inline_comment). Conservative: only split when the
    tail looks explanatory (Latin/quotes/parentheses)."""
    cell = cell.strip()
    m = _SPLIT_RE.search(cell)
    if not m:
        return cell, ''
    head, tail = cell[:m.start()].strip(), cell[m.start():].strip(' (')
    # only treat the tail as a comment when it contains Latin explanation
    if tail and _LATIN_RE.search(tail) and head:
        return head, tail
    return cell, ''


# --------------------------------------------------------------------- edit ops
def _unit(a, b):
    """Classify a single-char substitution/indel into a linguistic unit."""
    c = a or b
    if c is None:
        return 'other'
    if (a and unicodedata.combining(a)) or (b and unicodedata.combining(b)):
        return 'diacritic'          # a diacritic on either side = a diacritic edit
    if c.isspace():
        return 'whitespace'
    if c.isdigit():
        return 'digit'
    if a and b and a.lower() == b.lower():
        return 'case'
    cat = unicodedata.category(c)
    if cat.startswith('P') or cat.startswith('S'):
        return 'punctuation'
    base = unicodedata.normalize('NFD', c)[0].lower()
    if base in 'aeiou':
        return 'vowel'
    if base.isalpha():
        return 'consonant' if ord(base) < 128 else 'latin'
    return 'other'


def edit_ops(old, new):
    """Optimal-string-alignment edit trace over NFD chars (with transposition)."""
    a = list(unicodedata.normalize('NFD', old))
    b = list(unicodedata.normalize('NFD', new))
    la, lb = len(a), len(b)
    INF = la + lb + 1
    d = [[0] * (lb + 1) for _ in range(la + 1)]
    for i in range(la + 1):
        d[i][0] = i
    for j in range(lb + 1):
        d[0][j] = j
    for i in range(1, la + 1):
        for j in range(1, lb + 1):
            cost = 0 if a[i - 1] == b[j - 1] else 1
            d[i][j] = min(d[i - 1][j] + 1, d[i][j - 1] + 1, d[i - 1][j - 1] + cost)
            if (i > 1 and j > 1 and a[i - 1] == b[j - 2] and a[i - 2] == b[j - 1]):
                d[i][j] = min(d[i][j], d[i - 2][j - 2] + 1)
    # backtrace
    ops = []
    i, j = la, lb
    while i > 0 or j > 0:
        if (i > 1 and j > 1 and a[i - 1] == b[j - 2] and a[i - 2] == b[j - 1]
                and d[i][j] == d[i - 2][j - 2] + 1):
            ops.append({'op': 'transpose', 'from': a[i - 2] + a[i - 1],
                        'to': b[j - 2] + b[j - 1], 'unit': _unit(a[i - 1], b[j - 1])})
            i -= 2; j -= 2; continue
        if i > 0 and j > 0 and a[i - 1] == b[j - 1]:
            i -= 1; j -= 1; continue
        if i > 0 and j > 0 and d[i][j] == d[i - 1][j - 1] + 1:
            ops.append({'op': 'sub', 'from': a[i - 1], 'to': b[j - 1],
                        'unit': _unit(a[i - 1], b[j - 1])})
            i -= 1; j -= 1; continue
        if i > 0 and d[i][j] == d[i - 1][j] + 1:
            ops.append({'op': 'del', 'from': a[i - 1], 'to': '',
                        'unit': _unit(a[i - 1], None)})
            i -= 1; continue
        ops.append({'op': 'ins', 'from': '', 'to': b[j - 1],
                    'unit': _unit(None, b[j - 1])})
        j -= 1
    ops.reverse()
    return ops, d[la][lb]


# --------------------------------------------------------- empirical clustering
_CLUSTER_RULES = [
    ('capitalization', r'capital|uppercase|lowercase|\bcase\b'),
    ('as-number', r'\bas\b.*number|letter-number|as number'),
    ('iast-diacritic', r'iast|diacritic|hiatus|accent'),
    ('markup', r'markup|tag|<[a-z]+>|split'),
    ('reference', r'referen|biblio|\bls\b|source'),
    ('ocr-print', r'ocr|print|smudge|scan'),
    ('variant', r'variant|inferred|new resource'),
    ('typo', r'typo|error'),
]


def empirical_cluster(comment):
    c = (comment or '').strip().lower()
    if not c:
        return 'unspecified'
    for label, pat in _CLUSTER_RULES:
        if re.search(pat, c):
            return label
    return 'other'


# ------------------------------------------------------------------- identity
def load_resolver():
    email2login, name2login = {}, {}
    with open(MAP, encoding='utf-8') as f:
        m = json.load(f)
    realname = {}
    for login, info in m.items():
        if login.startswith('_') or not isinstance(info, dict):
            continue
        realname[login] = info.get('real_name', login)
        name2login[login.lower()] = login
        for a in info.get('aliases', []):
            a = a.strip().lower()
            (email2login if '@' in a else name2login)[a] = login
    # form-only aliases (the Google-form corrector handles)
    FORM = {'ejf': 'funderburkjim', 'dhaval': 'drdhaval2785', 'dhavel': 'drdhaval2785',
            'gas': 'gasyoun', 'gasyoun': 'gasyoun'}
    for k, v in FORM.items():
        name2login.setdefault(k, v)

    def resolve(raw):
        token = (raw or '').strip()
        # corrector cell looks like "Name : Corrected M/D/YYYY"
        handle = re.split(r'\s*:', token, maxsplit=1)[0].strip()
        key = handle.lower()
        if '@' in key and key in email2login:
            return email2login[key], handle
        if key in name2login:
            return name2login[key], handle
        return (handle or 'unknown'), handle
    return resolve, realname


_DATE_TAIL = re.compile(r'(\d{1,2})/(\d{1,2})/(\d{2,4})')


def parse_corrector(raw, submit_dt, resolve, realname):
    login, _handle = resolve(raw)
    name = realname.get(login, login)
    latency = ''
    m = _DATE_TAIL.search(raw or '')
    if m and submit_dt:
        mm, dd, yy = (int(m.group(1)), int(m.group(2)), int(m.group(3)))
        if yy < 100:
            yy += 2000
        try:
            done = datetime(yy, mm, dd)
            latency = (done - submit_dt).days
            if latency < 0:
                latency = ''
        except ValueError:
            latency = ''
    return login, name, latency


# ----------------------------------------------------------------------- main
def parse_time(s):
    """cfr timestamp is 'M/D/YYYY H:MM:SS'."""
    s = re.sub(r'[\r\n]+', ' ', s).strip()
    for fmt in ('%m/%d/%Y %H:%M:%S', '%m/%d/%Y %H:%M', '%m/%d/%Y'):
        try:
            return datetime.strptime(s, fmt)
        except ValueError:
            continue
    return None


def main():
    if not os.path.exists(CFR):
        sys.exit(f'cfr.tsv not found at {CFR}')
    os.makedirs(DATA, exist_ok=True)
    os.makedirs(SCHEMA_DIR, exist_ok=True)
    resolve, realname = load_resolver()

    rows, warnings = [], []
    n_in = n_bad = 0
    with open(CFR, encoding='utf-8', newline='') as f:
        reader = csv.reader(f, delimiter='\t')
        header = next(reader, None)
        for ln, parts in enumerate(reader, start=2):
            n_in += 1
            if len(parts) != 8:
                n_bad += 1
                if len(warnings) < 50:
                    warnings.append(f'line {ln}: {len(parts)} columns (expected 8)')
                # pad/truncate so we still capture what we can
                parts = (parts + [''] * 8)[:8]
            ts, dct, lcode, hw, old_raw, new_raw, comment, corr = parts
            dt = parse_time(ts)
            old_corr, old_inline = split_new(old_raw)   # strip commentary from both cells
            new_corr, new_inline = split_new(new_raw)
            inline = ' '.join(x for x in (old_inline, new_inline) if x)
            old_iast = normalize_to_iast(old_corr.strip())
            new_iast = normalize_to_iast(new_corr.strip())
            ops, dist = edit_ops(old_iast, new_iast)
            login, cname, latency = parse_corrector(corr, dt, resolve, realname)
            lc = '' if (not lcode or lcode.strip().startswith('0(')) else lcode.strip()
            eid = hashlib.sha1(
                ('form|' + dct + '|' + lc + '|' + old_raw + '|' + new_raw + '|'
                 + (dt.isoformat() if dt else ts)).encode('utf-8')).hexdigest()[:16]
            rows.append({
                'event_id': eid,
                'date': dt.date().isoformat() if dt else '',
                'source_layer': 'form',
                'dict': dct.strip().lower(),
                'lcode': lc,
                'headword_iast': normalize_to_iast(hw.strip()),
                'old_iast': old_iast,
                'new_iast': new_iast,
                'old_raw': old_raw.strip(),
                'new_raw': new_raw.strip(),
                'inline_comment': inline,
                'edit_ops': json.dumps(ops, ensure_ascii=False),
                'edit_distance': dist,
                'script_old': detect_script(old_corr),
                'script_new': detect_script(new_corr),
                'comment_raw': comment.strip(),
                'error_type_empirical': empirical_cluster(comment + ' ' + inline),
                'corrector': login,
                'corrector_name': cname,
                'latency_days': latency,
                'evidence_level': 'derived',
            })

    rows.sort(key=lambda r: (r['date'], r['event_id']))

    fields = ['event_id', 'date', 'source_layer', 'dict', 'lcode', 'headword_iast',
              'old_iast', 'new_iast', 'old_raw', 'new_raw', 'inline_comment',
              'edit_ops', 'edit_distance', 'script_old', 'script_new', 'comment_raw',
              'error_type_empirical', 'corrector', 'corrector_name', 'latency_days',
              'evidence_level']
    with open(OUT_CSV, 'w', encoding='utf-8', newline='') as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader(); w.writerows(rows)

    # ---- envelope / meta ----
    cluster_counts = Counter(r['error_type_empirical'] for r in rows)
    dict_counts = Counter(r['dict'] for r in rows)
    op_counts = Counter()
    for r in rows:
        for o in json.loads(r['edit_ops']):
            op_counts[o['op'] + ':' + o['unit']] += 1
    n_lat = sum(1 for r in rows if r['latency_days'] != '')
    meta = {
        'schemaVersion': SCHEMA_VERSION,
        'generatedAt': datetime.now(timezone.utc).isoformat(),
        'sourcePath': os.path.relpath(CFR, ROOT).replace('\\', '/'),
        'recordCount': len(rows),
        'assumptions': [
            'cfr.tsv is the L1 correction-form export; 8 tab-separated columns.',
            'Devanagari runs transliterated to IAST by a self-contained map (NFC).',
            'NEW-cell inline commentary split heuristically (inferred) when a Latin '
            'tail follows " - ", "(", or a double space.',
            'Edit ops computed over NFD via optimal-string-alignment incl. transposition.',
            'Correctors alias-merged via contributors_map.json + form aliases.',
        ],
        'warnings': warnings,
        'stats': {
            'rowsIn': n_in, 'rowsOut': len(rows), 'malformedRows': n_bad,
            'rowsWithLatency': n_lat,
            'dateRange': [rows[0]['date'], rows[-1]['date']] if rows else [],
            'topDicts': dict_counts.most_common(12),
            'empiricalClusters': cluster_counts.most_common(),
            'topEditUnits': op_counts.most_common(15),
        },
    }
    with open(OUT_META, 'w', encoding='utf-8') as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)

    # ---- JSON Schema (written once / overwritten) ----
    schema = {
        '$schema': 'https://json-schema.org/draft/2020-12/schema',
        '$id': 'correction-event.schema.json',
        'title': 'CDSL correction event (OBS-T)',
        'type': 'object',
        'required': ['event_id', 'date', 'source_layer', 'dict', 'old_iast', 'new_iast'],
        'properties': {
            'event_id': {'type': 'string'},
            'date': {'type': 'string'},
            'source_layer': {'enum': ['form', 'git', 'printchange', 'batch']},
            'dict': {'type': 'string'},
            'lcode': {'type': 'string'},
            'headword_iast': {'type': 'string'},
            'old_iast': {'type': 'string'}, 'new_iast': {'type': 'string'},
            'old_raw': {'type': 'string'}, 'new_raw': {'type': 'string'},
            'inline_comment': {'type': 'string'},
            'edit_ops': {'type': 'string', 'description': 'JSON array of typed ops'},
            'edit_distance': {'type': 'integer'},
            'script_old': {'enum': ['deva', 'iast', 'hk', 'latin', 'mixed', 'other']},
            'script_new': {'enum': ['deva', 'iast', 'hk', 'latin', 'mixed', 'other']},
            'comment_raw': {'type': 'string'},
            'error_type_empirical': {'type': 'string'},
            'corrector': {'type': 'string'}, 'corrector_name': {'type': 'string'},
            'latency_days': {'type': ['integer', 'string']},
            'evidence_level': {'enum': ['observed', 'derived', 'inferred']},
            # --- axes + crosswalks + split, added downstream (Phases 3/4/6/8) ---
            'error_component': {'enum': ['headword', 'grammar', 'citation', 'sense',
                                         'markup', 'crossref', 'meta', 'unattributed'],
                                'description': 'LOCATION axis (where in the entry); '
                                'derived labels only, else unattributed'},
            'edit_type': {'enum': ['spelling', 'diacritic', 'case', 'spacing',
                                   'punctuation', 'digit', 'transposition', 'none'],
                          'description': 'EDIT-TYPE axis (what kind of change)'},
            'errant_type': {'type': 'string', 'description': 'ERRANT op x unit crosswalk'},
            'ocr_class': {'type': 'string', 'description': 'OCR/digitization crosswalk'},
            'textcrit_class': {'type': 'string', 'description': 'textual-criticism crosswalk'},
            'split': {'enum': ['train', 'dev', 'test'],
                      'description': 'temporal split of the released resource'},
        },
    }
    with open(OUT_SCHEMA, 'w', encoding='utf-8') as f:
        json.dump(schema, f, ensure_ascii=False, indent=2)

    print(f'wrote {OUT_CSV}  ({len(rows)} events)')
    print(f'wrote {OUT_META}')
    print(f'wrote {OUT_SCHEMA}')
    print(f'  rows in/out/malformed: {n_in}/{len(rows)}/{n_bad}')
    print(f'  date range: {meta["stats"]["dateRange"]}  with-latency: {n_lat}')
    print(f'  clusters: {cluster_counts.most_common(8)}')


if __name__ == '__main__':
    main()
