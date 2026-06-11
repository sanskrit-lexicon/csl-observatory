#!/usr/bin/env python3
"""OBS-T Phase 3 — microstructure component attribution (the canonical typology).

Assigns each correction event an `error_component`: which part of the dictionary
microstructure was wrong (headword / grammar / citation / sense / markup /
crossref / meta / orthography). This is the canonical lexicographic typology;
the empirical cluster and the edit-op crosswalk are secondary views.

Two attribution paths, both deterministic:

* **git layer** — the changed source line already carries its XML tags, so the
  component is read off positionally: locate the changed span (common prefix /
  suffix between old and new) and report the tag enclosing it. Evidence: derived.
* **form layer** — the cfr old/new are bare IAST fragments, not full records, so
  we join to `../csl-orig`: for the event's `<L>` record, render each tagged
  segment to IAST and find which segment contains the corrected value. Evidence:
  derived when the join hits; otherwise an empirical-cluster -> component
  fallback, evidence: inferred.

Inputs : observatory/site/src/data/correction_events_all.csv
         ../csl-orig/v02/<dict>/<dict>.txt  (form-layer join only)
Outputs: observatory/site/src/data/correction_events_typed.csv  (+ error_component)
         observatory/site/src/data/obs_t_component.csv           (component x layer x dict)
         observatory/site/src/data/correction_events_typed.meta.json

Usage:  python scripts/attribute_components.py
"""
import csv, json, os, re, sys, unicodedata
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
COMPONENTS = ['headword', 'grammar', 'citation', 'sense', 'crossref', 'meta',
              'encoding', 'markup', 'orthography', 'unknown']

_TAG_RE = re.compile(r'<[^>]*>')


def component_of_line(line, pos):
    """Component of the tag enclosing character index `pos` in a tagged line."""
    if not line:
        return 'unknown'
    tags = list(_TAG_RE.finditer(line))
    if not tags:
        return 'orthography'          # bare text, no markup
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
    return re.split(r'[\s/(]', s.strip(), 1)[0]


_K1_LINE = re.compile(r'<k1>([^<]*)')


def build_index(dict_path, needed_hw):
    """norm(headword IAST) -> list of segment-lists, for the needed headwords only.
    Keyed by headword (not <L> id): the 2014-era cfr L-codes have drifted against
    today's sequential csl-orig ids, but the headword is stable."""
    idx = defaultdict(list)
    cur_lines, cur_k1 = [], None
    with open(dict_path, encoding='utf-8') as f:
        for line in f:
            line = line.rstrip('\n')
            if line.startswith('<L>'):
                m = _K1_LINE.search(line)
                cur_k1 = norm(slp1_to_iast(m.group(1))) if m else None
                cur_lines = [line]
            elif line.startswith('<LEND>'):
                if cur_k1 and cur_k1 in needed_hw:
                    segs = [(fld, slp1_to_iast(c)) for fld, c in
                            parse_segments(' '.join(cur_lines)) if c.strip()]
                    idx[cur_k1].append(segs)
                cur_lines, cur_k1 = [], None
            elif cur_lines:
                cur_lines.append(line)
    return idx


def form_component(event, idx):
    """Join to a csl-orig record by headword (stable key), then locate the corrected
    value within its segments. The cfr 'headword' cell is often the *old* (mistyped)
    word, so we also try the new/old values as entry keys: if the corrected value is
    itself a k1, the correction was to the headword. Returns (component, evidence)."""
    hw, ni, oi = norm(event['headword_iast']), norm(event['new_iast']), norm(event['old_iast'])
    ni1, oi1 = norm(first_tok(event['new_iast'])), norm(first_tok(event['old_iast']))
    needles = [n for n in (ni, oi, ni1, oi1) if n]
    # 1) headword key -> a record exists; locate the value to pin the component
    if hw and hw in idx:
        for segs in idx[hw]:
            for needle in needles:
                for fld, content in segs:
                    if needle in norm(content):
                        return TAG2COMP.get(fld, 'sense'), 'derived'
    # 2) corrected value (or its first token) is itself a headword -> headword fix
    for key in (ni, ni1, oi, oi1):
        if key and key in idx:
            return 'headword', 'derived'
    # 3) fallback: empirical cluster -> component (inferred)
    return CLUSTER2COMP.get(event['error_type_empirical'], 'unknown'), 'inferred'


def main():
    with open(IN_CSV, encoding='utf-8') as f:
        rows = list(csv.DictReader(f))
    fields = list(rows[0].keys())
    if 'error_component' not in fields:
        fields = fields[:fields.index('evidence_level')] + ['error_component'] + \
                 fields[fields.index('evidence_level'):]

    # git layer — positional
    n_git = n_form_join = n_form_fallback = 0
    form_by_dict = defaultdict(list)
    for r in rows:
        if r['source_layer'] == 'git':
            old, new = r['old_raw'], r['new_raw']
            ref = old if old else new
            r['error_component'] = component_of_line(ref, changed_pos(old, new))
            r['evidence_level'] = 'derived'
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
            comp, ev = form_component(e, idx)
            e['error_component'] = comp
            e['evidence_level'] = ev
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
            'Canonical typology = microstructure component (which part of the entry).',
            'git layer: component read positionally from the changed source line tags.',
            'form layer: component from the csl-orig <L> record segment whose IAST '
            'content contains the corrected value; else empirical-cluster fallback.',
            'encoding/orthography components arise mainly from the form fallback; '
            'in the git layer such edits are attributed by location (headword/sense).',
        ],
        'warnings': [],
        'stats': {
            'gitAttributed': n_git,
            'formJoinHits': n_form_join, 'formFallback': n_form_fallback,
            'formJoinRate': round(n_form_join / (n_form_join + n_form_fallback), 3)
            if (n_form_join + n_form_fallback) else 0,
            'componentTotals': comp_counts.most_common(),
            'byLayer': {k: v.most_common() for k, v in comp_by_layer.items()},
        },
    }
    with open(OUT_META, 'w', encoding='utf-8') as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)

    print(f'wrote {OUT_CSV}  ({len(rows)} events)')
    print(f'wrote {OUT_COMP}')
    print(f'wrote {OUT_META}')
    print(f'  git attributed: {n_git}  form join hits: {n_form_join}  '
          f'fallback: {n_form_fallback}  join rate: {meta["stats"]["formJoinRate"]}')
    print(f'  component totals: {comp_counts.most_common()}')


if __name__ == '__main__':
    main()
