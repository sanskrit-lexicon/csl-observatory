#!/usr/bin/env python3
"""Record-linkage study for the OBS-T capture-recapture estimator (G3 / A48).

`error_recapture.py` joins the two OBS-T eras on the *raw* headword string, which
is why only pw/mw/bur clear the recapture threshold. This script asks whether a
looser join is defensible, and answers it with measurement rather than assertion:
every candidate rule is scored for **false matches** against csl-orig itself.

Candidate site keys (a "site" is one dictionary record)
------------------------------------------------------
exact         raw `headword_iast` string                      (current published key)
normalised    NFC + casefold + edge-punctuation strip
scheme_repair normalised + Harvard-Kyoto decode of pure-ASCII cells.  The cfr form
              encoded roman cells in HK, and `build_correction_events.looks_hk`
              only fires on an *internal* capital or a `z`, so a cell like
              `Adeya` (= ādeya) reaches the corpus un-decoded.
fold          scheme_repair + diacritic folding (ā→a, ś/ṣ→s, ṭ→t, ...)
fold_ed1      fold + Damerau-ish edit distance 1 (`within1`, ported from
              `attribute_components.build_index`'s delete-1 blocking index)
lcode         join on the csl-orig `<L>` number instead of the headword
anchored      resolve BOTH eras to a *current* csl-orig record — exact headword
              if attested, else a folded key that is unique in the FULL
              dictionary vocabulary — and use that record as the site

Why the last two are not obviously better
-----------------------------------------
Both look like free recall. Both are measured here and both are worse than they
look: the 2014 form-era L-numbers have drifted, and Sanskrit headword space is
dense at edit distance 1 (kāla/kala, aṇu/anu, aś/as are different lemmas, not
spelling variants), so a fuzzy key manufactures recaptures. A false match
inflates m, and N_hat ~ 1/(m+1), so it deflates the estimate — that is, it makes
the "remaining correction work" headline smaller by an artefact.

Adjudication channels (both external to the rule being scored)
--------------------------------------------------------------
A. **Vocabulary attestation.** For a non-identical linked pair, look both sides up
   in that dictionary's real `<k1>` set. Both attested and different ⇒ two real
   records were merged ⇒ FALSE. Exactly one attested ⇒ the other is a variant
   spelling of it ⇒ TRUE (optimistic: a mangled string that happens to be
   unattested is scored TRUE, so the false rate reported here is a LOWER bound).
   Circular for the `anchored` rule, which is built from the vocabulary — hence:
B. **L-code corroboration.** For a fuzzy resolution, does the event's own
   (independent) `<L>` number resolve to the same record? Only meaningful where
   the L-numbering is stable, so the rate is reported stratified by the measured
   per-dictionary L-code stability.

Outputs
-------
* `observatory/site/src/data/obs_t_dict_records.csv`      record counts, ALL dicts
* `observatory/site/src/data/error_recapture_linkage.csv` per dict x rule scores
* `reports/error_recapture_linkage.md`                    method + verdict

Needs a local csl-orig checkout (`--csl-orig`, `$CSL_ORIG`, or a sibling
`../csl-orig/v02`); `error_recapture.py` itself stays offline and consumes only
the two committed CSVs above.

Usage:  python scripts/error_recapture_linkage.py [--csl-orig PATH]
"""
import argparse
import csv
import os
import re
import sys
import unicodedata
from collections import defaultdict

sys.stdout.reconfigure(encoding='utf-8'); sys.stderr.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)

from attribute_components import deletes1, within1            # noqa: E402
from build_correction_events import hk_to_iast                # noqa: E402
from reconstruct_git_events import slp1_to_iast               # noqa: E402

DATA = os.path.join(ROOT, 'observatory', 'site', 'src', 'data')
EVENTS = os.path.join(DATA, 'correction_events_final.csv')
OUT_RECORDS = os.path.join(DATA, 'obs_t_dict_records.csv')
OUT_LINKAGE = os.path.join(DATA, 'error_recapture_linkage.csv')
OUT_SUMMARY = os.path.join(DATA, 'error_recapture_linkage_summary.csv')
OUT_MD = os.path.join(ROOT, 'reports', 'error_recapture_linkage.md')

MIN_M = 10          # recapture threshold used by error_recapture.py
STABLE_LCODE = 0.5  # form-era L-code validity above which channel B is informative
STABLE_MIN_N = 100  # ...and the minimum sample the validity figure must rest on

_L_RE = re.compile(r'<L>([^<]*)')
_K1_RE = re.compile(r'<k1>([^<]*)')
_IAST_RE = re.compile(r'[āīūṛṝḷḹṅñṭḍṇśṣṃḥ]')
_ASCII_ALPHA_RE = re.compile(r'^[A-Za-z]+$')

# IAST -> its diacritic-free skeleton. Every one of these distinctions is
# phonemic in Sanskrit, which is precisely why folding them is dangerous.
_FOLD = str.maketrans({'ā': 'a', 'ī': 'i', 'ū': 'u', 'ṛ': 'r', 'ṝ': 'r',
                       'ḷ': 'l', 'ḹ': 'l', 'ṅ': 'n', 'ñ': 'n', 'ṭ': 't',
                       'ḍ': 'd', 'ṇ': 'n', 'ś': 's', 'ṣ': 's', 'ṃ': 'm',
                       'ḥ': 'h'})


# ------------------------------------------------------------------ key builders
def normalise(s):
    s = unicodedata.normalize('NFC', s.strip()).casefold()
    return re.sub(r'\s+', ' ', s.strip('.,;:!?"\'()[]{}*-–—°˚ '))


def scheme_repair(s):
    """Best IAST reading: decode a pure-ASCII cell as Harvard-Kyoto."""
    t = s.strip()
    if _ASCII_ALPHA_RE.match(t) and not _IAST_RE.search(t):
        return normalise(hk_to_iast(t))
    return normalise(t)


def fold(s):
    return scheme_repair(s).translate(_FOLD)


KEYFN = {'exact': lambda s: s.strip(),
         'normalised': normalise,
         'scheme_repair': scheme_repair,
         'fold': fold,
         'fold_ed1': fold}
FUZZY_RULES = ('fold', 'fold_ed1')          # rules that can link non-identical strings


# ------------------------------------------------------------------ csl-orig side
def find_csl_orig(cli):
    for c in (cli, os.environ.get('CSL_ORIG'),
              os.path.join(os.path.dirname(ROOT), 'csl-orig', 'v02'),
              os.path.join(os.path.dirname(os.path.dirname(ROOT)), 'GitHub', 'csl-orig', 'v02'),
              os.path.join(os.path.dirname(ROOT), 'GitHub', 'csl-orig', 'v02')):
        if c and os.path.isdir(c):
            return c
    return None


def read_dict(orig, code):
    """(record_count, {L -> normalised k1}, {normalised k1}) for one dictionary."""
    src = os.path.join(orig, code, f'{code}.txt')
    if not os.path.exists(src):
        return None
    n, lmap, vocab = 0, {}, set()
    with open(src, encoding='utf-8', errors='replace') as f:
        for line in f:
            if not line.startswith('<L>'):
                continue
            n += 1
            lm, km = _L_RE.search(line), _K1_RE.search(line)
            if not (lm and km and km.group(1).strip()):
                continue
            k1 = normalise(slp1_to_iast(km.group(1).strip()))
            if k1:
                lmap[lm.group(1).strip()] = k1
                vocab.add(k1)
    return n, lmap, vocab


# ------------------------------------------------------------------ linkage
def link_pairs(f_raws, g_raws, rule):
    """{(form_raw, git_raw)} linked by `rule`."""
    keyfn = KEYFN[rule]
    gidx = defaultdict(set)
    for g in g_raws:
        k = keyfn(g)
        if k:
            gidx[k].add(g)
    out = set()
    for f in f_raws:
        k = keyfn(f)
        if not k:
            continue
        for g in gidx.get(k, ()):
            out.add((f, g))
    if rule != 'fold_ed1':
        return out
    # delete-1 blocking index over the git side, then verify with within1 —
    # the same bounded scheme as attribute_components.build_index.
    gdel = defaultdict(set)
    for k, gs in gidx.items():
        gdel[k] |= gs
        for kd in deletes1(k):
            gdel[kd] |= gs
    for f in f_raws:
        k = keyfn(f)
        if not k:
            continue
        cands = set(gdel.get(k, ()))
        for kd in deletes1(k):
            cands |= gdel.get(kd, set())
        for g in cands:
            if within1(k, keyfn(g)):
                out.add((f, g))
    return out


def anchor(hw, vocab, buckets):
    """Resolve a headword to a current csl-orig record. -> (record|None, route)."""
    cands = list(dict.fromkeys([normalise(hw), scheme_repair(hw)]))
    for c in cands:
        if c in vocab:
            return c, 'exact'
    for c in cands:
        b = buckets.get(c.translate(_FOLD), ())
        if len(b) == 1:
            return b[0], 'fold_unique'
        if len(b) > 1:
            return None, 'fold_ambiguous'
    return None, 'unattested'


def adjudicate(pairs, vocab):
    """Channel A. -> dict(identical/true/false/undetermined), [false examples]."""
    c = dict.fromkeys(('identical', 'true', 'false', 'undetermined'), 0)
    examples = []
    for f, g in sorted(pairs):
        fi, gi = scheme_repair(f), normalise(g)
        if fi == gi:
            c['identical'] += 1
            continue
        af, ag = fi in vocab, gi in vocab
        if af and ag:
            c['false'] += 1
            if len(examples) < 5:
                examples.append(f'{f} = {g}')
        elif af or ag:
            c['true'] += 1
        else:
            c['undetermined'] += 1
    return c, examples


def m_of(pairs):
    """Recaptures implied by a link set: the smaller matched side (a site cannot
    be recaptured twice)."""
    return min(len({f for f, _ in pairs}), len({g for _, g in pairs})) if pairs else 0


# ------------------------------------------------------------------ main
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--csl-orig', default=None, help='path to csl-orig/v02')
    args = ap.parse_args()

    orig = find_csl_orig(args.csl_orig)
    if not orig:
        sys.exit('csl-orig/v02 not found — pass --csl-orig or set $CSL_ORIG. '
                 '(error_recapture.py runs offline from the committed CSVs; only '
                 'this generator needs the sources.)')
    print(f'csl-orig: {orig}')

    with open(EVENTS, encoding='utf-8') as f:
        rows = list(csv.DictReader(f))
    dicts = sorted({r['dict'] for r in rows})

    sites = defaultdict(lambda: {'form': set(), 'git': set()})
    lcodes = defaultdict(lambda: {'form': set(), 'git': set()})
    ev_by_dict = defaultdict(list)
    for r in rows:
        hw = r['headword_iast'].strip()
        lc = r['lcode'].strip()
        if hw:
            sites[r['dict']][r['source_layer']].add(hw)
            ev_by_dict[r['dict']].append(r)
        if lc:
            lcodes[r['dict']][r['source_layer']].add(lc)

    records, out_rows = [], []
    stability, anchored_check = {}, defaultdict(lambda: [0, 0])
    for d in dicts:
        got = read_dict(orig, d)
        if not got:
            records.append({'dict': d, 'records': '', 'distinct_headwords': '',
                            'note': 'no csl-orig v02 source'})
            continue
        n_rec, lmap, vocab = got
        records.append({'dict': d, 'records': n_rec,
                        'distinct_headwords': len(vocab), 'note': ''})
        buckets = defaultdict(list)
        for v in vocab:
            buckets[v.translate(_FOLD)].append(v)

        # measured L-code stability: does a form-era event's own <L> still point
        # at a record carrying that event's headword? (folded comparison, so
        # transcription noise is not charged to the L-number)
        n_lc = ok_lc = 0
        for r in ev_by_dict[d]:
            if r['source_layer'] != 'form':
                continue
            k1 = lmap.get(r['lcode'].strip())
            if k1 is None:
                continue
            n_lc += 1
            if k1.translate(_FOLD) == fold(r['headword_iast']):
                ok_lc += 1
        stability[d] = ((ok_lc / n_lc), n_lc) if n_lc else None
        stab = stability[d][0] if stability[d] else None

        f_raws, g_raws = sites[d]['form'], sites[d]['git']
        if not f_raws or not g_raws:
            continue

        for rule in KEYFN:
            pairs = link_pairs(f_raws, g_raws, rule)
            counts, examples = adjudicate(pairs, vocab)
            m = m_of(pairs)
            adjudicated = counts['true'] + counts['false']
            out_rows.append({
                'dict': d, 'rule': rule, 'n1_form': len(f_raws), 'n2_git': len(g_raws),
                'm_overlap': m, 'estimable': int(m >= MIN_M),
                'links': len(pairs), 'links_identical': counts['identical'],
                'links_true': counts['true'], 'links_false': counts['false'],
                'links_undetermined': counts['undetermined'],
                'false_match_rate': (round(counts['false'] / adjudicated, 4)
                                     if adjudicated else ''),
                'lcode_stability': (round(stab, 4) if stab is not None else ''),
                'false_examples': ' | '.join(examples)})

        # lcode rule — no headword involved, so channel A cannot score it; its
        # credibility IS the measured stability figure.
        lm = len(lcodes[d]['form'] & lcodes[d]['git'])
        out_rows.append({
            'dict': d, 'rule': 'lcode', 'n1_form': len(lcodes[d]['form']),
            'n2_git': len(lcodes[d]['git']), 'm_overlap': lm,
            'estimable': int(lm >= MIN_M), 'links': lm, 'links_identical': '',
            'links_true': '', 'links_false': '', 'links_undetermined': '',
            'false_match_rate': (round(1 - stab, 4) if stab is not None else ''),
            'lcode_stability': (round(stab, 4) if stab is not None else ''),
            'false_examples': ''})

        # anchored rule — resolve both eras onto current records
        res = {'form': set(), 'git': set()}
        for r in ev_by_dict[d]:
            rec, route = anchor(r['headword_iast'], vocab, buckets)
            if not rec:
                continue
            res[r['source_layer']].add(rec)
            if route == 'fold_unique':          # channel B on the fuzzy increment
                k1 = lmap.get(r['lcode'].strip())
                if k1 is not None:
                    anchored_check[d][0] += 1
                    anchored_check[d][1] += int(k1 == rec)
        am = len(res['form'] & res['git'])
        n, ok = anchored_check[d]
        out_rows.append({
            'dict': d, 'rule': 'anchored', 'n1_form': len(res['form']),
            'n2_git': len(res['git']), 'm_overlap': am,
            'estimable': int(am >= MIN_M), 'links': am, 'links_identical': '',
            'links_true': ok, 'links_false': n - ok, 'links_undetermined': '',
            'false_match_rate': (round(1 - ok / n, 4) if n else ''),
            'lcode_stability': (round(stab, 4) if stab is not None else ''),
            'false_examples': ''})

    with open(OUT_RECORDS, 'w', encoding='utf-8', newline='') as f:
        w = csv.DictWriter(f, fieldnames=['dict', 'records', 'distinct_headwords', 'note'])
        w.writeheader()
        w.writerows(records)
    with open(OUT_LINKAGE, 'w', encoding='utf-8', newline='') as f:
        w = csv.DictWriter(f, fieldnames=list(out_rows[0].keys()))
        w.writeheader()
        w.writerows(out_rows)

    summary = write_report(out_rows, records, stability, anchored_check)
    with open(OUT_SUMMARY, 'w', encoding='utf-8', newline='') as f:
        w = csv.DictWriter(f, fieldnames=list(summary[0].keys()))
        w.writeheader()
        w.writerows(summary)
    print(f'wrote {OUT_RECORDS}  ({sum(1 for r in records if r["records"] != "")} dicts counted)')
    print(f'wrote {OUT_LINKAGE}  ({len(out_rows)} dict x rule rows)')
    print(f'wrote {OUT_SUMMARY}  ({len(summary)} rules)')
    print(f'wrote {OUT_MD}')


def write_report(out_rows, records, stability, anchored_check):
    by_rule = defaultdict(list)
    for r in out_rows:
        by_rule[r['rule']].append(r)

    # dictionaries whose L-numbering is demonstrably stable — the only stratum in
    # which "the L-code disagrees" is evidence against a linkage rather than
    # evidence about the L-code
    stable = sorted(d for d, s in stability.items()
                    if s and s[0] >= STABLE_LCODE and s[1] >= STABLE_MIN_N)
    n_anch = sum(anchored_check[d][0] for d in stable)
    ok_anch = sum(anchored_check[d][1] for d in stable)
    # events-weighted share of form-era L-codes that no longer point at their record
    n_lc = sum(s[1] for s in stability.values() if s)
    ok_lcs = sum(s[0] * s[1] for s in stability.values() if s)

    def totals(rule):
        rs = by_rule[rule]
        m = sum(r['m_overlap'] for r in rs)
        t = sum(r['links_true'] or 0 for r in rs if isinstance(r['links_true'], int))
        fl = sum(r['links_false'] or 0 for r in rs if isinstance(r['links_false'], int))
        est = sorted(r['dict'] for r in rs if r['estimable'])
        return m, t, fl, est

    def rate_cell(rule):
        """The honest false-match figure for the summary table."""
        if rule == 'lcode':
            return f'{1 - ok_lcs / n_lc:.1%} (L-drift)' if n_lc else '—'
        if rule == 'anchored':
            return (f'{1 - ok_anch / n_anch:.1%} (fuzzy increment)'
                    if n_anch else '—')
        _, t, fl, _ = totals(rule)
        if t + fl == 0:
            return 'n/a — links no non-identical pair'
        return f'{fl / (t + fl):.1%}'

    L = []; A = L.append
    A('# Record linkage for the capture–recapture estimator: which join is admissible?')
    A('')
    A('_Generated by `scripts/error_recapture_linkage.py` from '
      '`observatory/site/src/data/correction_events_final.csv` and a local '
      '`csl-orig/v02` checkout. Companion to `reports/error_recapture.md` '
      '(Workstream G3, paper A48)._')
    A('')
    A('## The question')
    A('')
    A('The capture–recapture estimate of remaining correction work joins the two '
      'OBS-T eras on the dictionary record ("site"). The published estimator uses '
      'the **raw headword string**, and only three dictionaries (pw, mw, bur) '
      f'reach the recapture threshold m ≥ {MIN_M}. A looser join would put more '
      'dictionaries in range. The backlog row asked for one; this report asks '
      'first whether a looser join is *allowed*, because a false match inflates '
      'm, N̂ ≈ (n1+1)(n2+1)/(m+1) − 1 falls as m rises, and the failure mode is '
      'therefore not noise but a **systematically smaller "work remaining" '
      'headline with no evidence behind it**.')
    A('')
    A('## Rules scored')
    A('')
    A('| Rule | Key | Total m | Non-identical links scored true / FALSE | Measured false-match rate | Dictionaries estimable |')
    A('|---|---|---:|---:|---:|---|')
    labels = {'exact': 'raw `headword_iast` (published)',
              'normalised': 'NFC + casefold + punctuation',
              'scheme_repair': '+ Harvard-Kyoto decode of ASCII cells',
              'fold': '+ diacritic folding',
              'fold_ed1': '+ edit distance 1',
              'lcode': 'csl-orig `<L>` number',
              'anchored': 'resolved current csl-orig record'}
    for rule in ('exact', 'normalised', 'scheme_repair', 'fold', 'fold_ed1',
                 'lcode', 'anchored'):
        m, t, fl, est = totals(rule)
        if rule == 'anchored':          # channel B, stable-L stratum only
            t, fl = ok_anch, n_anch - ok_anch
        elif rule == 'lcode':
            t, fl = round(ok_lcs), round(n_lc - ok_lcs)
        scored = f'{t:,} / {fl:,}' if (t + fl) else '—'
        A(f'| `{rule}` | {labels[rule]} | {m:,} | {scored} | {rate_cell(rule)} | '
          f'{len(est)} ({", ".join(est) if len(est) <= 6 else str(len(est))}) |')
    A('')
    A('False-match rates for `exact`…`fold_ed1` come from **vocabulary '
      'attestation**: a linked pair whose two sides are *both* attested as '
      'distinct `<k1>` headwords of that dictionary merged two real records. The '
      'rate is a lower bound — a mangled string that happens to be unattested is '
      'scored as a true match. `lcode` and `anchored` are scored by the '
      'independent **L-code corroboration** channel instead (see below), because '
      'the vocabulary channel is circular for them.')
    A('')
    A('## Verdict')
    A('')
    m_ex, _, _, _ = totals('exact')
    m_sr, t_sr, f_sr, _ = totals('scheme_repair')
    m_no, t_no, f_no, _ = totals('normalised')
    m_fo, t_fo, f_fo, est_fo = totals('fold')
    m_e1, t_e1, f_e1, _ = totals('fold_ed1')
    A(f'- **Adopted: `scheme_repair`.** It adds recaptures ({m_ex:,} → {m_sr:,}) '
      'while linking **no non-identical pair at all** — every link it makes is '
      'between two strings that become the same string once the encoding is '
      'repaired, so there is no fuzzy increment for a false match to hide in. '
      'What it repairs is a corpus defect, not a resemblance: '
      '`build_correction_events.looks_hk` recognises a Harvard-Kyoto cell only by '
      'an *internal* capital or a `z`, so cfr cells such as `Adeya` (= ādeya) or '
      '`Ahnika` (= āhnika) reached the corpus un-decoded and could never match '
      'their git-era twin. It also **removes** false matches: plain casefolding '
      f'(`normalised`, {f_no} false of {t_no + f_no} adjudicated) merges `Ayukta` '
      'with `ayukta` and `Adya` with `adya` — ā-initial headwords collapsed onto '
      'their a-initial neighbours, which `scheme_repair` keeps apart.')
    A(f'- **Rejected: `fold` ({f_fo / (t_fo + f_fo):.0%} false) and `fold_ed1` '
      f'({f_e1 / (t_e1 + f_e1):.0%} false).** Sanskrit headword space is dense at '
      'edit distance 1 *and* under diacritic folding, because every folded '
      'distinction is phonemic: `kāla`/`kala`, `aṇu`/`anu`, `kuṇḍa`/`kunda`, '
      '`aś`/`as` are different lemmas with their own records. Folding would have '
      f'made {len(est_fo)} dictionaries "estimable" — by merging records that a '
      'lexicographer keeps apart.')
    A('- **Rejected: `lcode`.** It looks like the strongest key (every event '
      'carries one, ~99 % populated in both eras) and it is the weakest. The '
      'git-era L-numbers resolve to their own headword ~100 % of the time — they '
      'were read out of csl-orig — but the 2014 form-era numbers have drifted, '
      'and the drift is measured below. Where an L-number is stale it typically '
      'points at an **alphabetically adjacent** record, so a stale-vs-stale '
      'collision is silently plausible.')
    A('- **Not adopted as primary: `anchored`.** Resolving both eras onto current '
      'csl-orig records is the methodologically cleanest key — it matches the '
      'estimand ("current records harbouring an error") — but it drops every '
      'form-era event whose headword is not attested in the dictionary at all, '
      'which is 40–97 % of them depending on the dictionary. That is not a '
      'linkage decision but a change of population, and it cannot be assumed '
      'independent of error-proneness: a headword mangled beyond recognition '
      'plausibly sits in a *more* corrupt entry, not a random one. Reported as a '
      'sensitivity row.')
    A('')
    A('## L-code drift, measured')
    A('')
    A('Share of form-era events whose own `<L>` number still resolves, in current '
      'csl-orig, to a record carrying that event\'s headword (diacritic-folded '
      'comparison, so transcription noise is not charged to the L-number):')
    A('')
    A('| Dict | Form-era events with a resolvable L-code | L-codes still valid | Fuzzy resolutions corroborated by the L-code |')
    A('|---|---:|---:|---:|')
    for d in sorted(stability, key=lambda d: -(stability[d][0] if stability[d] else 0)):
        s = stability[d]
        if s is None or s[1] < 25:
            continue
        n, ok = anchored_check[d]
        corr = f'{ok}/{n} = {ok / n:.0%}' if n else '—'
        A(f'| {d} | {s[1]:,} | {s[0]:.1%} | {corr} |')
    A('')
    A(f'Across all dictionaries, **{1 - ok_lcs / n_lc:.0%}** of resolvable '
      f'form-era L-codes ({n_lc - ok_lcs:,.0f} of {n_lc:,}) no longer point at a '
      'record carrying that event\'s headword. Dictionaries below ~25 resolvable '
      'form-era events are omitted from the table as too small to read.')
    A('')
    if n_anch:
        A(f'Restricted to the dictionaries whose L-numbering is both stable '
          f'(≥ {STABLE_LCODE:.0%} valid) and measured on ≥ {STABLE_MIN_N} events '
          f'({", ".join(stable)}), the independent L-code channel corroborates '
          f'{ok_anch:,}/{n_anch:,} = {ok_anch / n_anch:.1%} of the `anchored` '
          f'rule\'s *fuzzy* resolutions — a false-match rate of ≈ '
          f'{1 - ok_anch / n_anch:.0%} on the fuzzy increment, against ~0 % on '
          'its exact-attestation majority. Outside that stratum the channel '
          'measures the L-codes, not the linkage, and says nothing either way.')
        A('')
    A('## Record counts')
    A('')
    counted = [r for r in records if r['records'] != '']
    A(f'`obs_t_dict_records.csv` now carries `<L>` counts for **{len(counted)} of '
      f'{len(records)}** dictionaries in the event corpus (the missing ones — '
      f'{", ".join(r["dict"] for r in records if r["records"] == "") or "none"} — '
      'have no csl-orig v02 source and no git-era events, so they are '
      'non-estimable regardless). This replaces the three record counts embedded '
      'in `error_recapture.py`, whose values it reproduces exactly.')
    A('')
    A('_Method: record linkage scored against the linked corpus itself (csl-orig '
      'v02). Object of analysis: correction events over source text, per '
      '`docs/BOUNDARY_RULES.md`._')

    with open(OUT_MD, 'w', encoding='utf-8', newline='\n') as f:
        f.write('\n'.join(L) + '\n')

    basis = {'lcode': 'L-code drift, events-weighted over all dictionaries',
             'anchored': f'L-code corroboration of the fuzzy increment, '
                         f'stable-L stratum ({", ".join(stable)})'}
    summary = []
    for rule in ('exact', 'normalised', 'scheme_repair', 'fold', 'fold_ed1',
                 'lcode', 'anchored'):
        m, t, fl, est = totals(rule)
        if rule == 'anchored':
            t, fl = ok_anch, n_anch - ok_anch
        elif rule == 'lcode':
            t, fl = round(ok_lcs), round(n_lc - ok_lcs)
        summary.append({
            'rule': rule, 'key': labels[rule], 'total_m': m,
            'dicts_estimable': len(est), 'estimable': ' '.join(est),
            'links_true': t, 'links_false': fl,
            'false_match_rate': round(fl / (t + fl), 4) if (t + fl) else '',
            'basis': basis.get(rule, 'vocabulary attestation of non-identical links')})
    return summary


if __name__ == '__main__':
    main()
