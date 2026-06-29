#!/usr/bin/env python3
"""OBS-T Phase 3 — microstructure component attribution (the canonical typology).

Assigns each correction event an `error_component`: which part of the dictionary
microstructure was wrong (headword / grammar / citation / sense / markup /
crossref / meta / unattributed). This is the LOCATION axis; edit type is handled
separately by `attribute_crosswalks.py`.

Two attribution paths, both deterministic:

* **git layer** — the changed source line already carries its XML tags, so the
  component is read off positionally: locate the changed span (common prefix /
  suffix between old and new) and report the tag enclosing it. Evidence: derived.
* **form layer** — the cfr old/new are bare IAST fragments, not full records, so
  we join to `../csl-orig`: render likely records to IAST and find which segment
  contains the corrected value. Evidence is derived when the location is supported;
  otherwise the LOCATION is `unattributed`, evidence=inferred.

Inputs : observatory/site/src/data/correction_events_all.csv
         ../csl-orig/v02/<dict>/<dict>.txt  (form-layer join only)
Outputs: observatory/site/src/data/correction_events_typed.csv  (+ error_component)
         observatory/site/src/data/obs_t_component.csv           (component x layer x dict)
         observatory/site/src/data/correction_events_typed.meta.json

Usage:  python scripts/attribute_components.py
"""
import csv, json, os, random, re, sys, unicodedata
from collections import Counter, defaultdict
from datetime import datetime, timezone
sys.stdout.reconfigure(encoding='utf-8'); sys.stderr.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
GH_ROOT = os.path.dirname(ROOT)
CSL_ORIG = os.path.join(GH_ROOT, 'csl-orig')
DATA = os.path.join(ROOT, 'observatory', 'site', 'src', 'data')
IN_CSV = os.path.join(DATA, 'correction_events_all.csv')
OUT_CSV = os.path.join(DATA, 'correction_events_typed.csv')
OUT_COMP = os.path.join(DATA, 'obs_t_component.csv')
OUT_META = os.path.join(DATA, 'correction_events_typed.meta.json')
VDIR = os.path.join(ROOT, 'validation')
OUT_AUDIT = os.path.join(VDIR, 'form_join_audit_sample.csv')

sys.path.insert(0, HERE)
from reconstruct_git_events import slp1_to_iast  # noqa: E402

# ---- tag -> component map (the microstructure frame) ----
TAG2COMP = {
    'l': 'meta', 'pc': 'meta', 'e': 'meta', 'mul': 'meta', 'tail': 'meta',
    'k1': 'headword', 'k2': 'headword', 'k': 'headword', 'h': 'headword',
    'hom': 'headword',
    'lex': 'grammar',
    'ls': 'citation',
    'lb': 'crossref', 'mat': 'crossref',
    's': 'sense', 's1': 'sense', 's2': 'sense', 's3': 'sense', 'bot': 'sense',
    'ab': 'sense', 'gk': 'sense', 'etym': 'sense', 'vlex': 'sense',
}
# empirical cluster -> component (form-layer fallback, evidence=inferred)
CLUSTER2COMP = {
    'capitalization': 'orthography', 'iast-diacritic': 'encoding',
    'markup': 'markup', 'reference': 'citation', 'as-number': 'encoding',
    'ocr-print': 'orthography', 'variant': 'sense', 'typo': 'orthography',
    'unspecified': 'unknown', 'other': 'unknown',
}
# LOCATION axis only (microstructure component / where in the entry). Edit-TYPE
# (orthography/encoding/diacritic) is a separate axis — see edit_type in crosswalks.
COMPONENTS = ['headword', 'grammar', 'citation', 'sense', 'crossref', 'meta',
              'markup', 'unattributed']

_TAG_RE = re.compile(r'<[^>]*>')


def component_of_line(line, pos):
    """Component of the tag enclosing character index `pos` in a tagged line."""
    if not line:
        return 'unknown'
    tags = list(_TAG_RE.finditer(line))
    if not tags:
        return 'sense'                # bare text in a record = definition prose
    for m in tags:
        if m.start() <= pos < m.end():
            return 'markup'           # the edit hit the tag delimiter itself
    active = None
    for m in tags:
        if m.end() > pos:
            break
        t = m.group()
        if t.startswith('</'):
            active = None
        elif t.endswith('/>'):
            continue                  # self-closing (e.g. <info .../>)
        else:
            mm = re.match(r'<\s*([^\s>/]+)', t)
            active = mm.group(1).lower() if mm else None
    if active is None:
        return 'sense'                # prose inside the definition
    return TAG2COMP.get(active, 'sense')


def changed_pos(old, new):
    """Start index of the differing span (common-prefix length)."""
    n = min(len(old), len(new))
    i = 0
    while i < n and old[i] == new[i]:
        i += 1
    return i


# ---- form-layer csl-orig join ----
def parse_segments(record):
    """Split a record's text into (field, content) pairs by its tags."""
    segs = []
    active, buf = None, []
    pos = 0
    for m in _TAG_RE.finditer(record):
        if m.start() > pos:
            buf.append(record[pos:m.start()])
        if buf:
            segs.append((active or 'prose', ''.join(buf)))
            buf = []
        t = m.group()
        if t.startswith('</'):
            active = None
        elif t.endswith('/>'):
            pass
        else:
            mm = re.match(r'<\s*([^\s>/]+)', t)
            active = mm.group(1).lower() if mm else None
        pos = m.end()
    if record[pos:]:
        segs.append((active or 'prose', record[pos:]))
    return segs


def lcode_id(raw):
    """Extract the bare record id from a cfr L-code cell.
    e.g. '[L=5590] [p= 1-299]' -> '5590'; '12241.114' -> '12241.114';
    'LHK', '0(NA)', '' -> None."""
    if not raw:
        return None
    m = re.search(r'L\s*=\s*([0-9][0-9.]*)', raw)
    if m:
        return m.group(1)
    m = re.match(r'\s*([0-9][0-9.]*)\s*$', raw)
    return m.group(1) if m else None


def norm(s):
    return unicodedata.normalize('NFC', s.strip().lower())


def first_tok(s):
    """First word of a cell, dropping trailing commentary/variants ('a / b', 'a (x)')."""
    return re.split(r'[\s/(]', s.strip(), maxsplit=1)[0]


_K1_LINE = re.compile(r'<k1>([^<]*)')


def deletes1(s):
    """All edit-distance-1 deletions of s (SymSpell key set)."""
    return {s[:i] + s[i + 1:] for i in range(len(s))}


def within1(a, b):
    """True if a and b are within Damerau-ish edit distance 1 (sub/ins/del)."""
    if a == b:
        return True
    la, lb = len(a), len(b)
    if abs(la - lb) > 1:
        return False
    if la == lb:
        return sum(1 for x, y in zip(a, b) if x != y) == 1
    if la > lb:
        a, b, la, lb = b, a, lb, la
    i = j = diff = 0
    while i < la and j < lb:
        if a[i] == b[j]:
            i += 1; j += 1
        else:
            diff += 1; j += 1
            if diff > 1:
                return False
    return True


def build_index(dict_path, needed_hw):
    """norm(headword IAST query) -> list of segment-lists for csl-orig records whose
    <k1> is exact or **edit-distance-1** to the query. Keyed by headword (not <L>
    id): the 2014-era cfr L-codes have drifted, and the cfr headword is usually the
    *old (mistyped)* form, so a fuzzy match recovers the corrected record. Bounded:
    a delete-1 index over the (small) query set, one streaming pass over the dict."""
    qdel = defaultdict(list)            # delete-1 variant -> queries
    for q in needed_hw:
        qdel[q].append(q)
        for d in deletes1(q):
            qdel[d].append(q)
    idx = defaultdict(list)
    cur_lines, cur_k1 = [], None

    def flush():
        if not cur_k1:
            return
        cands = set()
        for kd in (cur_k1, *deletes1(cur_k1)):
            for q in qdel.get(kd, ()):
                cands.add(q)
        cands = {q for q in cands if within1(cur_k1, q)}
        if cands:
            segs = [(fld, slp1_to_iast(c)) for fld, c in
                    parse_segments(' '.join(cur_lines)) if c.strip()]
            for q in cands:
                idx[q].append({
                    'segments': segs,
                    'match': 'exact' if cur_k1 == q else 'fuzzy',
                    'k1': cur_k1,
                })

    with open(dict_path, encoding='utf-8') as f:
        for line in f:
            line = line.rstrip('\n')
            if line.startswith('<L>'):
                flush()
                m = _K1_LINE.search(line)
                cur_k1 = norm(slp1_to_iast(m.group(1))) if m else None
                cur_lines = [line]
            elif line.startswith('<LEND>'):
                flush()
                cur_lines, cur_k1 = [], None
            elif cur_lines:
                cur_lines.append(line)
    flush()
    return idx


def form_component(event, idx):
    """Join to a csl-orig record by headword (stable key), then locate the corrected
    value within its segments — this gives the LOCATION (microstructure component).
    The cfr 'headword' cell is often the *old* (mistyped) word, so we also try the
    new/old values as entry keys: if the corrected value is itself a k1, the
    correction was to the headword. When the location cannot be derived we return
    `unattributed` rather than guessing from the edit type (which is a different
    axis — see edit_type). Returns (location, evidence, route)."""
    hw, ni, oi = norm(event['headword_iast']), norm(event['new_iast']), norm(event['old_iast'])
    ni1, oi1 = norm(first_tok(event['new_iast'])), norm(first_tok(event['old_iast']))
    needles = [n for n in (ni, oi, ni1, oi1) if n]
    # 1) headword key -> a record exists; locate the value to pin the component
    if hw and hw in idx:
        for rec in idx[hw]:
            for needle in needles:
                for fld, content in rec['segments']:
                    if needle in norm(content):
                        return TAG2COMP.get(fld, 'sense'), 'derived', \
                            f'segment_{rec["match"]}'
    # 2) corrected value (or first token) is itself a headword. This is weaker than
    # locating the value in the event's own record, so only unique, non-short keys
    # count as derived; the rest are preserved for audit as unattributed.
    for key in (ni, ni1, oi, oi1):
        matches = idx.get(key, [])
        if key and matches:
            if len(key) >= 4 and len(matches) == 1:
                return 'headword', 'derived', 'value_headword_unique'
            return 'unattributed', 'inferred', 'value_headword_weak'
    # 3) location not derivable -> unattributed (do NOT guess from edit type)
    return 'unattributed', 'inferred', 'unattributed'


def write_audit_sample(rows):
    """Write a deterministic, stratified sample of risky form joins."""
    buckets = defaultdict(list)
    for r in rows:
        route = r.get('attribution_route', '')
        if r.get('source_layer') != 'form':
            continue
        if route not in {'segment_fuzzy', 'value_headword_unique', 'value_headword_weak'}:
            continue
        buckets[route].append(r)
    rng = random.Random(7)
    picked = []
    for route, items in sorted(buckets.items()):
        rng.shuffle(items)
        picked.extend(items[:25])
    os.makedirs(VDIR, exist_ok=True)
    fields = ['event_id', 'dict', 'date', 'attribution_route', 'evidence_level',
              'error_component', 'headword_iast', 'old_iast', 'new_iast',
              'old_raw', 'new_raw', 'comment_raw']
    with open(OUT_AUDIT, 'w', encoding='utf-8', newline='') as f:
        w = csv.DictWriter(f, fieldnames=fields); w.writeheader()
        for r in picked:
            w.writerow({k: r.get(k, '') for k in fields})
    return len(picked), {k: len(v) for k, v in sorted(buckets.items())}


def main():
    with open(IN_CSV, encoding='utf-8') as f:
        rows = list(csv.DictReader(f))
    fields = list(rows[0].keys())
    if 'error_component' not in fields:
        fields = fields[:fields.index('evidence_level')] + ['error_component'] + \
                 fields[fields.index('evidence_level'):]
    if 'attribution_route' not in fields:
        fields = fields[:fields.index('evidence_level')] + ['attribution_route'] + \
                 fields[fields.index('evidence_level'):]

    # git layer — positional
    n_git = n_form_join = n_form_fallback = 0
    route_counts = Counter()
    form_by_dict = defaultdict(list)
    for r in rows:
        if r['source_layer'] == 'git':
            old, new = r['old_raw'], r['new_raw']
            ref = old if old else new
            r['error_component'] = component_of_line(ref, changed_pos(old, new))
            r['attribution_route'] = 'git_positional'
            r['evidence_level'] = 'derived'
            route_counts[r['attribution_route']] += 1
            n_git += 1
        else:
            form_by_dict[r['dict']].append(r)

    # form layer — csl-orig join per dict (bounded memory)
    for dct, evs in form_by_dict.items():
        path = os.path.join(CSL_ORIG, 'v02', dct, dct + '.txt')
        idx = {}
        if os.path.exists(path):
            needed_hw = set()
            for e in evs:
                needed_hw.update((norm(e['headword_iast']), norm(e['new_iast']),
                                  norm(e['old_iast']), norm(first_tok(e['new_iast'])),
                                  norm(first_tok(e['old_iast']))))
            needed_hw.discard('')
            if needed_hw:
                idx = build_index(path, needed_hw)
        for e in evs:
            comp, ev, route = form_component(e, idx)
            e['error_component'] = comp
            e['attribution_route'] = route
            e['evidence_level'] = ev
            route_counts[route] += 1
            lc = lcode_id(e['lcode'])
            if lc:
                e['lcode'] = lc          # store the clean record id (note: may be drifted)
            if ev == 'derived':
                n_form_join += 1
            else:
                n_form_fallback += 1

    rows.sort(key=lambda r: (r.get('date', ''), r['event_id']))
    with open(OUT_CSV, 'w', encoding='utf-8', newline='') as f:
        w = csv.DictWriter(f, fieldnames=fields); w.writeheader(); w.writerows(rows)

    # component x layer x dict summary
    summ = Counter((r['error_component'], r['source_layer'], r['dict']) for r in rows)
    with open(OUT_COMP, 'w', encoding='utf-8', newline='') as f:
        w = csv.writer(f); w.writerow(['component', 'layer', 'dict', 'count'])
        for (comp, layer, dct), n in sorted(summ.items(), key=lambda kv: -kv[1]):
            w.writerow([comp, layer, dct, n])
    audit_n, audit_pool = write_audit_sample(rows)

    comp_counts = Counter(r['error_component'] for r in rows)
    comp_by_layer = defaultdict(Counter)
    for r in rows:
        comp_by_layer[r['source_layer']][r['error_component']] += 1
    meta = {
        'schemaVersion': '1.0.0',
        'generatedAt': datetime.now(timezone.utc).isoformat(),
        'sourcePath': 'correction_events_all.csv + ../csl-orig (form join)',
        'recordCount': len(rows),
        'assumptions': [
            'error_component is the LOCATION axis (which part of the entry); edit '
            'TYPE (orthography/encoding/diacritic) is a separate axis -> edit_type.',
            'git layer: location read positionally from the changed source line tags; '
            'untagged record text = sense (definition prose).',
            'form layer: location from the csl-orig <L> record segment whose IAST '
            'content contains the corrected value; if not derivable -> unattributed '
            '(we do NOT guess a location from the edit type).',
            'form value-is-headword shortcuts are derived only when the matching key '
            'is unique and length >= 4; weaker shortcuts are unattributed/inferred.',
        ],
        'warnings': [],
        'stats': {
            'gitAttributed': n_git,
            'formJoinHits': n_form_join, 'formFallback': n_form_fallback,
            'formJoinRate': round(n_form_join / (n_form_join + n_form_fallback), 3)
            if (n_form_join + n_form_fallback) else 0,
            'componentTotals': comp_counts.most_common(),
            'byLayer': {k: v.most_common() for k, v in comp_by_layer.items()},
            'attributionRoutes': route_counts.most_common(),
            'auditSampleRows': audit_n,
            'auditSamplePool': audit_pool,
        },
    }
    with open(OUT_META, 'w', encoding='utf-8') as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)

    print(f'wrote {OUT_CSV}  ({len(rows)} events)')
    print(f'wrote {OUT_COMP}')
    print(f'wrote {OUT_META}')
    print(f'wrote {OUT_AUDIT}  ({audit_n} audit rows)')
    print(f'  git attributed: {n_git}  form join hits: {n_form_join}  '
          f'fallback: {n_form_fallback}  join rate: {meta["stats"]["formJoinRate"]}')
    print(f'  component totals: {comp_counts.most_common()}')


if __name__ == '__main__':
    main()
