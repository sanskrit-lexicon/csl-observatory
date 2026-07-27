#!/usr/bin/env python3
"""Headword record-linkage keys for the two-era capture-recapture design (G3).

`error_recapture.py` joins the two OBS-T capture occasions (form era 2014-2019,
git era 2019-2026) on the *site* key `(dict, headword)`. That join was
**exact-string** only, which is the wrong instrument for this corpus: the
form-era cells are hand-typed web-form submissions carrying ASCII fallbacks
(`nyancana` for `nyañcana`), stray SLP1/HK residue, homonym digits and accent
marks, while the git-era headwords come from the machine-clean `<k1>` field of
`csl-orig`. Exact matching therefore *misses true recaptures*, which biases the
Chapman estimate UPWARD (fewer recaptures m => larger N-hat).

The cure is not "fuzzy matching" in the loose sense. A record-linkage key that
merges genuinely distinct lemmas biases the estimate the other way (spurious
recaptures => N-hat too small), and Sanskrit headword inventories are dense with
minimal pairs (`kara`/`kāra`, `nīla`/`nīca`, `kṛṣ`/`tṛṣ`) — a naive
edit-distance-1 join is almost all false matches. So this module offers a
**ladder of linkage keys of increasing aggressiveness** and, for each one, a
*measured* false-match rate, so the choice of operating key is an empirical
decision rather than a taste.

The ladder (each level subsumes the one above)
----------------------------------------------
| level          | key                                  | folds |
|----------------|--------------------------------------|-------|
| `exact`        | raw string                           | nothing |
| `clean`        | NFC, casefold, drop punctuation/digits/spaces | typographic noise |
| `repair`       | `clean` + SLP1->IAST decode of cells carrying `f/q/w/x/z` | a provable encoding fault, not a similarity guess |
| `form_key`     | `sanskrit_util.form_key` on `repair` | + anusvāra/homorganic nasals -> n, final visarga, pitch accents — **vowel length and retroflexion preserved** |
| `norm`         | `sanskrit_util.norm` on `repair`     | + every combining mark: ā->a, ś->s, ṭ->t, ṇ->n |
| `ed1`          | `clean` + edit-distance-1 join       | any single substitution/insertion/deletion |

`form_key` / `norm` are the canonical shared normalizers from the org's
`sanskrit-util` package (SHARED_CODE.md §1-2) — deliberately NOT re-rolled here.
The `ed1` level is the `deletes1`/`within1` SymSpell machinery already used by
`attribute_components.py` for the form-layer csl-orig join, ported to site keys.

How the false-match rate is measured (no human annotation needed)
-----------------------------------------------------------------
Two independent, fully offline measurements, both taken against the dictionary's
own headword inventory (`csl-orig/v02/<dict>/<dict>.txt`, `<k1>` fields):

1. **Key-collision rate.** How often does the key merge two *distinct records of
   the dictionary itself*? If `kara` and `kāra` are two separate `<L>` records
   and a key maps both to `kara`, then any cross-era match on that key is
   ambiguous by construction. Collision rate = share of records whose key is
   shared with at least one other record. This is a property of the key and the
   dictionary, independent of the correction corpus.

2. **Attestation test on the actual matched pairs.** For every non-exact pair
   (form-era string x linked to git-era string y, x != y) the module asks whether
   x and y are BOTH attested as distinct headwords of that dictionary. If they
   are, the link joins two real, different records — a **false match**, counted.
   If x is unattested (the typical case for a hand-typed misspelling) the link is
   the intended repair and counts as plausible. This yields a per-dictionary,
   per-level false-match rate over exactly the pairs the estimator consumes.

Outputs (committed, so the reported numbers stay reproducible without csl-orig)
------------------------------------------------------------------------------
* `observatory/site/src/data/dict_record_counts.csv`  — `<L>` record count and
  distinct-`<k1>` count for every csl-orig v02 dictionary (also closes the
  "record-count denominators for ALL dicts" backlog row of A48: the Chapman
  estimates are capped at the physical record count, which previously existed
  for three dictionaries only).
* `observatory/site/src/data/headword_key_collisions.csv` — per dict x level
  collision rate of the linkage key over the dictionary's own inventory.

Usage
-----
    python scripts/headword_linkage.py            # refresh both sidecars from csl-orig
    python scripts/headword_linkage.py --selftest # key-ladder unit checks, no csl-orig needed
"""
import argparse, csv, os, re, sys, unicodedata
from collections import defaultdict
sys.stdout.reconfigure(encoding='utf-8'); sys.stderr.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
GH_ROOT = os.path.dirname(ROOT)
CSL_ORIG = os.path.join(GH_ROOT, 'csl-orig')
DATA = os.path.join(ROOT, 'observatory', 'site', 'src', 'data')
OUT_COUNTS = os.path.join(DATA, 'dict_record_counts.csv')
OUT_COLL = os.path.join(DATA, 'headword_key_collisions.csv')


# --------------------------------------------------------------- shared package
def _load_sanskrit_util():
    """The canonical transliteration/normalization package (SHARED_CODE.md §1-2).

    Installed copy first; sibling-repo checkout as the fallback, matching the shim
    pattern used by the other Python consumers (e.g. SanskritSpellCheck)."""
    try:
        import sanskrit_util
        return sanskrit_util
    except ImportError:
        pass
    import importlib.util
    init = os.path.join(GH_ROOT, 'sanskrit-util', 'py', 'sanskrit_util', '__init__.py')
    if not os.path.exists(init):
        raise ImportError(
            "shared 'sanskrit-util' package not found (neither importable nor at %s) — "
            "restore the sibling repo or `pip install -e <path>/sanskrit-util/py`" % init)
    spec = importlib.util.spec_from_file_location('sanskrit_util', init)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


SU = _load_sanskrit_util()


# ------------------------------------------------------------------ key ladder
# Homonym indices ("kara 2"), separators and editorial punctuation are
# typographic, not lexical: they never distinguish two lemmas on their own.
_DROP = re.compile(r'[\s\-\u2010-\u2015|/\\^~+.,;:()\[\]{}#%\u00b0\u00af\u00b2\u02d8\u221a0-9]')


# Pitch/metre marks, which the printed dictionaries carry inconsistently. Dropped
# only when they sit on a VOWEL: the same combining acute also builds ś (s + U+0301),
# where it is phonemic. Length (macron) and retroflexion (dot below) are never touched.
_PITCH = {'́', '̀', '॑', '॒', '̐', '̇', '˘'}
_VOWELS = set('aāiīuūṛṝḷḹeēoō')


def _strip_pitch(s):
    """Drop pitch accents from vowels, keeping ś and every length/retroflex mark."""
    out = []
    for ch in unicodedata.normalize('NFD', s):
        if ch in _PITCH:
            j = len(out) - 1
            while j >= 0 and unicodedata.combining(out[j]):
                j -= 1
            base = unicodedata.normalize('NFC', ''.join(out[j:])) if j >= 0 else ''
            if base in _VOWELS:
                continue
        out.append(ch)
    return unicodedata.normalize('NFC', ''.join(out))


def clean(s):
    """Level `clean`: NFC + casefold + strip typographic noise. Diacritics kept."""
    s = _strip_pitch(unicodedata.normalize('NFC', (s or '').strip()).lower())
    return _DROP.sub('', s)


# f/F, q/Q, w/W, x/X, z/Z are SLP1 (or Harvard-Kyoto) letters that **cannot occur
# in IAST at all**. A headword cell containing one is therefore not "close to" the
# right string — it is provably a cell the cfr export left in (or partly in) SLP1,
# and transcoding it is a decoding step with no similarity judgement anywhere in
# it. 3,905 form-era headwords are in this state; the residue is the same partial
# transcode that produced the documented `R`=ṇ trap (SHARED_CODE.md §12).
_IMPOSSIBLE_IN_IAST = set('fFqQwWxXzZ')


def repair(s):
    """Level `repair`: `clean`, plus SLP1->IAST decoding of provably SLP1 cells."""
    s = _DROP.sub('', unicodedata.normalize('NFC', (s or '').strip()))
    if any(c in _IMPOSSIBLE_IN_IAST for c in s):
        s = SU.from_slp1(s)
    return clean(s)


def key_exact(s):
    return (s or '').strip()


def key_clean(s):
    return clean(s)


def key_repair(s):
    return repair(s)


def key_form(s):
    """Length-preserving fold (ā != a, ṭ != t); anusvāra/homorganic nasals -> n."""
    return SU.form_key(repair(s))


def key_norm(s):
    """Diacritic-insensitive fold (ā -> a, ś -> s, ṭ -> t, ṇ -> n)."""
    return SU.norm(repair(s))


# Deterministic keys, in ascending aggressiveness. `ed1` is not a key (it is a
# pairwise predicate) and is handled separately by `ed1_links`.
KEY_LEVELS = [
    ('exact', key_exact, 'raw string, as recorded'),
    ('clean', key_clean, 'NFC + casefold + drop punctuation/digits/accent marks'),
    ('repair', key_repair, 'clean + SLP1->IAST decoding of cells carrying letters impossible in IAST'),
    ('form_key', key_form, 'repair + anusvāra/homorganic nasal fold, final visarga, pitch accent (vowel length kept)'),
    ('norm', key_norm, 'repair + drop every combining mark (ā->a, ś->s, ṭ->t)'),
]
KEY_BY_NAME = {n: f for n, f, _ in KEY_LEVELS}
LEVEL_DESC = {n: d for n, _, d in KEY_LEVELS}
LEVEL_ORDER = [n for n, _, _ in KEY_LEVELS] + ['ed1']


# ------------------------------------------------- edit-distance-1 (ported ED1)
def deletes1(s):
    """All edit-distance-1 deletions of s (SymSpell key set)."""
    return {s[:i] + s[i + 1:] for i in range(len(s))}


def within1(a, b):
    """True if a and b are within edit distance 1 (substitution/insertion/deletion)."""
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
            i += 1
            j += 1
        else:
            diff += 1
            j += 1
            if diff > 1:
                return False
    return True


def ed1_links(left, right):
    """Pairs (x, y), x in `left`, y in `right`, x != y, within edit distance 1.

    Both sides are `clean`-level strings. Bounded by a delete-1 index over the
    right-hand set, so cost is linear in the sets, not quadratic."""
    idx = defaultdict(set)
    for y in right:
        idx[y].add(y)
        for d in deletes1(y):
            idx[d].add(y)
    out = []
    for x in left:
        cands = set(idx.get(x, ()))
        for d in deletes1(x):
            cands |= idx.get(d, set())
        for y in cands:
            if y != x and within1(x, y):
                out.append((x, y))
    return out


# ------------------------------------------------------------ csl-orig reading
_K1_RE = re.compile(r'<k1>([^<]*)')


def entry_path(code):
    return os.path.join(CSL_ORIG, 'v02', code, f'{code}.txt')


def dict_headwords(code):
    """(record_count, [headword IAST, ...]) from csl-orig v02 `<L>` records.

    One entry per `<L>` line; the `<k1>` field is SLP1 and is transcoded with the
    shared package. Streaming — the big dictionaries are ~100 MB."""
    path = entry_path(code)
    if not os.path.exists(path):
        return 0, []
    n, hw = 0, []
    with open(path, encoding='utf-8') as f:
        for line in f:
            if line.startswith('<L>'):
                n += 1
                m = _K1_RE.search(line)
                if m and m.group(1).strip():
                    hw.append(SU.from_slp1(m.group(1).strip()))
    return n, hw


def available_dicts():
    v02 = os.path.join(CSL_ORIG, 'v02')
    if not os.path.isdir(v02):
        return []
    return sorted(d for d in os.listdir(v02) if os.path.exists(entry_path(d)))


# --------------------------------------------------------------- measurements
def collision_stats(headwords, keyfn):
    """(distinct_keys, colliding_records, mean_cluster) for a key over an inventory.

    `colliding_records` = records whose key is shared with >= 1 other DISTINCT
    headword: that is exactly the situation in which a cross-era match on this key
    cannot be attributed to one record."""
    buckets = defaultdict(set)
    for h in headwords:
        k = keyfn(h)
        if k:
            buckets[k].add(h)
    distinct = len(buckets)
    colliding = sum(len(v) for v in buckets.values() if len(v) > 1)
    total = sum(len(v) for v in buckets.values())
    return distinct, colliding, (total / distinct if distinct else 0.0)


def load_record_counts(path=OUT_COUNTS):
    """{dict: record_count} from the committed sidecar (offline path)."""
    out = {}
    if not os.path.exists(path):
        return out
    with open(path, encoding='utf-8') as f:
        for r in csv.DictReader(f):
            try:
                out[r['dict']] = int(r['records'])
            except (KeyError, ValueError):
                continue
    return out


def load_collisions(path=OUT_COLL):
    """{(dict, level): collision_rate} from the committed sidecar."""
    out = {}
    if not os.path.exists(path):
        return out
    with open(path, encoding='utf-8') as f:
        for r in csv.DictReader(f):
            try:
                out[(r['dict'], r['level'])] = float(r['collision_rate'])
            except (KeyError, ValueError):
                continue
    return out


class Attestation:
    """Per-dictionary headword inventory, for the matched-pair attestation test.

    Falls back to an empty inventory (every verdict `unknown`) when csl-orig is
    absent, so downstream scripts stay runnable offline."""

    def __init__(self, code):
        _, hw = dict_headwords(code)
        self.clean = {clean(h) for h in hw}
        self.clean.discard('')
        self.available = bool(self.clean)

    def attested(self, s):
        return clean(s) in self.clean

    def verdict(self, x, y):
        """`false` (both are distinct real records), `plausible` (x unattested:
        the link repairs a misspelling), or `unknown` (no inventory)."""
        if not self.available:
            return 'unknown'
        if clean(x) == clean(y):
            return 'plausible'
        return 'false' if (self.attested(x) and self.attested(y)) else 'plausible'


# ------------------------------------------------------------------- site sets
# A form-era event whose correction landed ON THE HEADWORD tells us the site
# directly: the corrected value IS the record's headword, so the form-era cell
# (which carries the *old, wrong* spelling) and the git-era cell (which carries
# the current, right one) name the same record. `error_component` is already
# derived and evidence-graded in the corpus, and all 4,929 form-era `headword`
# events carry `evidence_level = derived`, so this alias uses a documented column
# rather than a similarity judgement. Values from events attributed to any other
# component are NOT usable this way: a corrected word inside a gloss is very
# often *also* a headword somewhere in a 40k-300k-record dictionary, so gating on
# attestation alone would manufacture sites.
HEADWORD_COMPONENT = 'headword'


def site_sets(rows, level='form_key', alias=True, with_component=False, exclude=None):
    """{dict: {'form': set(key), 'git': set(key)}} for the two capture occasions.

    `alias=True` adds the headword-component alias described above to the form-era
    side (it can only ever ADD recaptures, and only for events whose correction was
    attributed to the headword itself). `with_component` and `exclude` carry the two
    sensitivity switches of the two-era analysis: put the error component in the site
    key, and drop events falling on documented campaign (dict, date) days."""
    keyfn = KEY_BY_NAME[level]
    per = defaultdict(lambda: {'form': set(), 'git': set()})
    for r in rows:
        h = (r.get('headword_iast') or '').strip()
        if not h:
            continue
        if exclude and (r['dict'], (r.get('date') or '')[:10]) in exclude:
            continue
        comp = r.get('error_component')
        k = keyfn(h)
        if k:
            per[r['dict']][r['source_layer']].add((k, comp) if with_component else k)
        if alias and r.get('source_layer') == 'form' and comp == HEADWORD_COMPONENT:
            v = (r.get('new_iast') or '').strip().split(' ')[0]
            ak = keyfn(v) if v else ''
            if ak:
                per[r['dict']]['form'].add((ak, comp) if with_component else ak)
    return per


# --------------------------------------------------------------------- refresh
def refresh(dicts=None):
    codes = dicts or available_dicts()
    if not codes:
        print(f'csl-orig not found at {CSL_ORIG} — nothing to refresh', file=sys.stderr)
        return 1
    counts, coll = [], []
    for code in codes:
        n, hw = dict_headwords(code)
        if not n:
            continue
        counts.append({'dict': code, 'records': n, 'k1_present': len(hw),
                       'k1_distinct': len({clean(h) for h in hw} - {''})})
        for level, fn, _ in KEY_LEVELS:
            distinct, colliding, mean_cluster = collision_stats(hw, fn)
            coll.append({'dict': code, 'level': level, 'records': len(hw),
                         'distinct_keys': distinct, 'colliding_records': colliding,
                         'collision_rate': round(colliding / len(hw), 6) if hw else '',
                         'mean_cluster': round(mean_cluster, 4)})
        print(f'  {code:6s} records={n:7,d} k1={len(hw):7,d}')
    with open(OUT_COUNTS, 'w', encoding='utf-8', newline='') as f:
        w = csv.DictWriter(f, fieldnames=['dict', 'records', 'k1_present', 'k1_distinct'])
        w.writeheader()
        w.writerows(counts)
    with open(OUT_COLL, 'w', encoding='utf-8', newline='') as f:
        w = csv.DictWriter(f, fieldnames=['dict', 'level', 'records', 'distinct_keys',
                                          'colliding_records', 'collision_rate', 'mean_cluster'])
        w.writeheader()
        w.writerows(coll)
    print(f'wrote {OUT_COUNTS}  ({len(counts)} dictionaries)')
    print(f'wrote {OUT_COLL}    ({len(coll)} rows)')
    return 0


# -------------------------------------------------------------------- selftest
def selftest():
    checks = []

    def eq(label, got, want):
        checks.append((label, got == want, got, want))

    # `clean` strips homonym digits, hyphens and accent marks but keeps diacritics
    eq('clean digits', key_clean('kara 2'), 'kara')
    eq('clean hyphen', key_clean('a--kāra'), 'akāra')
    eq('clean acute', key_clean('ágni'), 'agni')
    eq('clean keeps diacritics', key_clean('nyañcana'), 'nyañcana')

    # `form_key` preserves vowel length and retroflexion (minimal pairs stay apart)
    eq('form_key kara != kāra', key_form('kara') == key_form('kāra'), False)
    eq('form_key nasal fold', key_form('ekāṅga'), key_form('ekāṃga'))
    eq('form_key visarga', key_form('anurodhaḥ'), key_form('anurodha'))

    # `norm` collapses length and retroflexion (deliberately more aggressive)
    eq('norm kara == kāra', key_norm('kara'), key_norm('kāra'))
    eq('norm ascii fallback', key_norm('nyancana'), key_norm('nyañcana'))

    # edit-distance-1 machinery
    eq('within1 sub', within1('kara', 'kala'), True)
    eq('within1 del', within1('kara', 'kra'), True)
    eq('within1 two', within1('kara', 'kila'), False)
    eq('ed1 links', sorted(ed1_links({'kara'}, {'kala', 'kara', 'mitra'})), [('kara', 'kala')])

    # SLP1-residue repair: an IAST-impossible letter proves the cell is SLP1
    eq('repair slp1 f', key_repair('prakfti'), 'prakṛti')
    eq('repair slp1 w', key_repair('kūwapālaka'), 'kūṭapālaka')
    eq('repair slp1 Q', key_repair('āQaka'), 'āḍhaka')
    eq('repair leaves iast alone', key_repair('prakṛti'), 'prakṛti')
    eq('repair no trigger', key_repair('deva'), 'deva')

    # collision counting
    distinct, colliding, _ = collision_stats(['kara', 'kāra', 'mitra'], key_norm)
    eq('collision distinct', distinct, 2)
    eq('collision records', colliding, 2)

    # site_sets: the headword-component alias adds the corrected value, nothing else
    ev = [
        {'dict': 'x', 'source_layer': 'form', 'headword_iast': 'prakfti',
         'error_component': 'headword', 'new_iast': 'prakṛti'},
        {'dict': 'x', 'source_layer': 'form', 'headword_iast': 'deva',
         'error_component': 'sense', 'new_iast': 'mitra'},
        {'dict': 'x', 'source_layer': 'git', 'headword_iast': 'prakṛti',
         'error_component': 'sense', 'new_iast': ''},
    ]
    noalias = site_sets(ev, alias=False)['x']
    eq('site_sets repair join', noalias['form'] & noalias['git'], {'prakṛti'})
    eq('site_sets alias adds hw only', site_sets(ev)['x']['form'], {'prakṛti', 'deva'})

    bad = [c for c in checks if not c[1]]
    for label, ok, got, want in checks:
        print(f'  {"ok  " if ok else "FAIL"} {label}' + ('' if ok else f'   got={got!r} want={want!r}'))
    print(f'{len(checks) - len(bad)}/{len(checks)} passed')
    return 1 if bad else 0


def main():
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('--selftest', action='store_true', help='run key-ladder checks and exit')
    ap.add_argument('--dict', action='append', help='limit refresh to these dict codes')
    a = ap.parse_args()
    return selftest() if a.selftest else refresh(a.dict)


if __name__ == '__main__':
    sys.exit(main())
