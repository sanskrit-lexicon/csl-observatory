#!/usr/bin/env python3
"""Within-era corrector-pair recapture — a second design to cross-check G3.

`error_recapture.py` estimates the error-site population from the two OBS-T
*eras* (form 2014-2019, git 2019-2026) as two capture occasions. That design has
a known, stated weakness: the occasions are **sequential**, so a site fixed
completely in era 1 cannot be recaptured in era 2. Recaptures m are depressed and
N-hat is biased upward, and nothing inside the two-era design can measure how big
that bias is.

This script builds the independent design that can. Within a single era, each
**corrector** is treated as a capture occasion over the same text state: Jim
Funderburk and Dhaval Patel working the same dictionary in the same period are
sampling one population, not two successive ones. Two things follow:

* a **corrector-pair Chapman** estimate per dictionary that does not inherit the
  sequential-occasion bias, and
* with K >= 3 correctors, a **Chao2 incidence estimator**, which is consistent
  under heterogeneous catchability — the second violation the two-era report
  flags but cannot quantify. Chao2's Q1/Q2 (sites seen by exactly one / exactly
  two correctors) is precisely a measurement of that heterogeneity.

Comparing the three N-hats per dictionary is the point: agreement supports the
published two-era figure, and a systematic gap sizes the bias it carries.

Occasions are PEOPLE, not raw strings
-------------------------------------
The `corrector` column is free text from two very different sources (git commit
authors; cfr web-form "who" cells) and needs identity resolution before it can
index an occasion:

* aliases are folded to the canonical person (`ejf` -> `funderburkjim`,
  `dhavel`/`dhaval` -> `drdhaval2785`, `sampada` -> `sanskritisampada`), using the
  same canonical map as the rest of the observatory (`scripts/contributors_map.json`);
* **joint cells** (`dhaval_ejf`, `sampada/ejf`, `Dhaval/gasyoun`) name two people
  for one correction, and are DROPPED by default. Crediting the site to both would
  keep the 6,206-event `dhaval_ejf` block — the largest form-era block — but it makes
  those two occasions co-capture by construction, and the damage is not theoretical:
  with joint cells kept, pw's form era reports MORE sites caught twice than once
  (Q2 5,517 > Q1 4,053), which drags Chao2 down to 1.13x the observed count, i.e. the
  false conclusion that the dictionary is nearly exhausted. `--keep-joint` runs it
  that way and the report carries both columns, so the size of the artifact is visible;
* unattributable cells (`unknown`, `(nouser)`, `? 2011`) are dropped — an occasion
  with no identity cannot be an occasion. Anonymous but STABLE form-corrector
  hashes (`form_corrector_b517a7c785`) are kept: they are distinct people.

Sites use the `form_key` linkage level of `headword_linkage.py`, so a site means
the same thing here as in the two-era analysis. The cross-era alias layer is not
applied: it exists to bridge the two eras' spelling conventions, and there is no
era boundary to bridge inside one era.

Outputs
-------
* `reports/corrector_recapture.md`
* `observatory/site/src/data/corrector_recapture.csv`

Usage:  python scripts/corrector_recapture.py [--keep-joint] [--selftest]
"""
import argparse, csv, math, os, re, sys
from collections import defaultdict
sys.stdout.reconfigure(encoding='utf-8'); sys.stderr.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DATA = os.path.join(ROOT, 'observatory', 'site', 'src', 'data')
EVENTS = os.path.join(DATA, 'correction_events_final.csv')
OUT_MD = os.path.join(ROOT, 'reports', 'corrector_recapture.md')
OUT_CSV = os.path.join(DATA, 'corrector_recapture.csv')

sys.path.insert(0, HERE)
import headword_linkage as HL              # noqa: E402
from error_recapture import chapman, MIN_M  # noqa: E402  (one estimator, one home)

MIN_OCCASION = 5      # a person with fewer sites is not a usable capture occasion
MIN_Q2 = 10           # Chao2 divides by Q2: below this the estimate is not reportable


# ------------------------------------------------------------ identity folding
# Canonical person per alias token. The git-side logins are already canonical (they
# come from `contributors_map.json`); what needs folding is the free-text cfr side.
ALIAS = {
    'ejf': 'funderburkjim', 'jim': 'funderburkjim', 'jfunderb': 'funderburkjim',
    'funderburkjim': 'funderburkjim',
    'dhaval': 'drdhaval2785', 'dhavel': 'drdhaval2785', 'drdhaval2785': 'drdhaval2785',
    'sampada': 'sanskritisampada', 'sanskritisampada': 'sanskritisampada',
    'gasyoun': 'gasyoun', 'aumsanskrit': 'aumsanskrit', 'adminlip': 'adminlip',
    'caujolle': 'caujolle',
}
# Cells that name nobody. `etal` is a real "and others" marker but identifies no
# person, so it contributes no occasion (the named part of the cell still does).
ANONYMOUS = {'unknown', 'nouser', '(nouser)', '?', 'etal', 'et al', 'na', 'n/a', ''}
_SPLIT = re.compile(r'\s*[/+,&]\s*|\s+and\s+|_')
_YEAR = re.compile(r'\b(19|20)\d\d\b')


def persons(cell):
    """Canonical person ids named by one `corrector` cell (possibly several)."""
    c = (cell or '').strip()
    if not c:
        return []
    if c.startswith('form_corrector_'):     # stable anonymous hash = one person
        return [c]
    c = _YEAR.sub('', c).strip(' ,')        # "Frank Ziesing 2011" == "Frank Ziesing, 2010"
    out = []
    for tok in _SPLIT.split(c):
        t = tok.strip().lower()
        if not t or t in ANONYMOUS:
            continue
        out.append(ALIAS.get(t, t))
    return sorted(set(out))


def is_joint(cell):
    return len(persons(cell)) > 1


# ------------------------------------------------------------------ estimators
def chao2(incidence, k):
    """Chao2 incidence richness estimate + log-normal 95% CI.

    `incidence` maps site -> number of occasions that captured it; `k` = number of
    occasions. Q1/Q2 are the sites seen exactly once / exactly twice: the more the
    captures pile onto the same few sites (heterogeneity), the larger Q1/Q2 and the
    larger the correction over S_obs."""
    s_obs = len(incidence)
    if s_obs == 0 or k < 2:
        return None
    q1 = sum(1 for v in incidence.values() if v == 1)
    q2 = sum(1 for v in incidence.values() if v == 2)
    r = (k - 1) / k
    if q2 > 0:
        extra = r * q1 * q1 / (2 * q2)
    else:                                    # bias-corrected form when nothing was seen twice
        extra = r * q1 * (q1 - 1) / 2
    s_est = s_obs + extra
    lo = hi = None
    if q2 > 0 and extra > 0:
        ratio = q1 / q2
        var = q2 * (r / 2 * ratio ** 2 + r * r * ratio ** 3 + r * r / 4 * ratio ** 4)
        if var > 0:
            c = math.exp(1.96 * math.sqrt(math.log(1 + var / (extra ** 2))))
            lo, hi = s_obs + extra / c, s_obs + extra * c
    return {'s_obs': s_obs, 'q1': q1, 'q2': q2, 'k': k, 'n_hat': s_est,
            'ci_low': lo, 'ci_high': hi}


def pair_estimates(by_person):
    """Chapman over every corrector pair with enough recaptures, largest m first."""
    people = sorted(by_person, key=lambda p: -len(by_person[p]))
    out = []
    for i, a in enumerate(people):
        for b in people[i + 1:]:
            sa, sb = by_person[a], by_person[b]
            if len(sa) < MIN_OCCASION or len(sb) < MIN_OCCASION:
                continue
            m = len(sa & sb)
            if m < MIN_M or m == len(sa) == len(sb):
                continue        # identical site sets = one occasion recorded twice
            n_hat, se, lo, hi = chapman(len(sa), len(sb), m)
            out.append({'a': a, 'b': b, 'n1': len(sa), 'n2': len(sb), 'm': m,
                        'n_hat': n_hat, 'ci_low': lo, 'ci_high': hi})
    out.sort(key=lambda r: -r['m'])
    return out


# ----------------------------------------------------------------------- model
def build(rows, keep_joint=True):
    """{(dict, era): {person: set(site)}} plus {(dict, era): {site: n_occasions}}."""
    keyfn = HL.KEY_BY_NAME['form_key']
    by_person = defaultdict(lambda: defaultdict(set))
    for r in rows:
        h = (r.get('headword_iast') or '').strip()
        if not h:
            continue
        site = keyfn(h)
        if not site:
            continue
        ppl = persons(r.get('corrector'))
        if not ppl or (len(ppl) > 1 and not keep_joint):
            continue
        for p in ppl:
            by_person[(r['dict'], r['source_layer'])][p].add(site)
    incidence = {}
    for key, per in by_person.items():
        inc = defaultdict(int)
        for sites in per.values():
            for s in sites:
                inc[s] += 1
        incidence[key] = dict(inc)
    return by_person, incidence


def two_era_reference():
    """{dict: N-hat} from the published two-era analysis, for the comparison column."""
    path = os.path.join(DATA, 'error_recapture.csv')
    out = {}
    if not os.path.exists(path):
        return out
    with open(path, encoding='utf-8') as f:
        for r in csv.DictReader(f):
            if r.get('estimable') == '1' and r.get('n_hat'):
                out[r['dict']] = (int(r['n_hat']), int(r['m_overlap']), r.get('capped') == '1')
    return out


def analyse(rows, keep_joint=True):
    by_person, incidence = build(rows, keep_joint)
    ref = two_era_reference()
    caps = HL.load_record_counts()
    results = []
    for (d, era), per in sorted(by_person.items()):
        usable = {p: s for p, s in per.items() if len(s) >= MIN_OCCASION}
        if len(usable) < 2:
            continue
        inc = defaultdict(int)
        for sites in usable.values():
            for s in sites:
                inc[s] += 1
        c2 = chao2(dict(inc), len(usable))
        pairs = pair_estimates(usable)
        best = pairs[0] if pairs else None
        two = ref.get(d)
        cap = caps.get(d)
        # Chao2's correction term is Q1^2/2Q2: with a handful of doubly-caught sites
        # it is arithmetic, not evidence. Capping at the dictionary's physical record
        # count is the same floor/ceiling discipline the two-era analysis uses.
        stable = bool(c2 and c2['q2'] >= MIN_Q2)
        capped = 0
        if c2:
            for k in ('n_hat', 'ci_low', 'ci_high'):
                if c2[k] is not None and cap and c2[k] > cap:
                    c2[k] = cap
                    capped = 1
        if best and cap:
            for k in ('n_hat', 'ci_low', 'ci_high'):
                best[k] = min(best[k], cap)
        results.append({
            'dict': d, 'era': era, 'correctors': len(usable),
            's_observed': len(inc), 'chao2_stable': int(stable),
            'record_count': cap or '', 'capped': capped,
            'pair_a': best['a'] if best else '', 'pair_b': best['b'] if best else '',
            'pair_n1': best['n1'] if best else '', 'pair_n2': best['n2'] if best else '',
            'pair_m': best['m'] if best else '',
            'pair_n_hat': round(best['n_hat']) if best else '',
            'pair_ci_low': round(best['ci_low']) if best else '',
            'pair_ci_high': round(best['ci_high']) if best else '',
            'pairs_estimable': len(pairs),
            'chao2_q1': c2['q1'] if c2 else '', 'chao2_q2': c2['q2'] if c2 else '',
            'chao2_n_hat': round(c2['n_hat']) if c2 else '',
            'chao2_ci_low': round(c2['ci_low']) if c2 and c2['ci_low'] else '',
            'chao2_ci_high': round(c2['ci_high']) if c2 and c2['ci_high'] else '',
            'two_era_n_hat': two[0] if two else '',
            'two_era_m': two[1] if two else '',
            'two_era_capped': int(two[2]) if two else '',
            'all_pairs': pairs,
        })
    results.sort(key=lambda r: (-r['s_observed'], r['dict']))
    return results


# ------------------------------------------------------------------- reporting
def fmt(v):
    return f'{v:,}' if isinstance(v, (int, float)) and v != '' else '—'


def write_report(main, sens, n_rows, n_joint_events, n_anon_events, keep_joint):
    joint_word = 'credited to both named people' if keep_joint else 'dropped as non-independent'
    L = []
    A = L.append
    A('# Within-era corrector-pair recapture: cross-checking the two-era estimate')
    A('')
    A('_Generated by `scripts/corrector_recapture.py` from `observatory/site/src/data/'
      'correction_events_final.csv` (offline, reproducible). Roadmap: Workstream G3. '
      'Companion to [`error_recapture.md`](error_recapture.md), which estimates the same '
      'quantity from the two eras instead._')
    A('')
    A('## Why a second design')
    A('')
    A('The two-era design treats the form era (2014-2019) and the git era (2019-2026) as '
      'two capture occasions. They are **sequential**: a record fixed completely in era 1 '
      'cannot be recaptured in era 2, so recaptures are lost and N-hat is pushed upward. '
      'The size of that bias is not measurable from inside that design.')
    A('')
    A('Correctors working the SAME dictionary in the SAME era sample one text state, so '
      'they are much closer to genuine replicate occasions. Two estimators follow: '
      '**Chapman** over a corrector pair (no sequential bias), and **Chao2** over all K '
      'correctors of that dictionary-era, which is consistent under the heterogeneous '
      'catchability the two-era report flags as its other violation. Q1 and Q2 — sites '
      'caught by exactly one and exactly two correctors — are a direct read-out of that '
      'heterogeneity.')
    A('')
    A(f'Occasions are resolved PEOPLE, not raw strings: aliases folded to the canonical '
      f'identity, {n_joint_events:,} events in joint cells (`dhaval_ejf`, `sampada/ejf`) '
      f'{joint_word}, {n_anon_events:,} unattributable events (`unknown`, `(nouser)`) '
      f'dropped. A person needs >= {MIN_OCCASION} sites to count as an occasion and a pair '
      f'needs m >= {MIN_M} recaptures for a point estimate.')
    A('')
    reportable = [r for r in main if r['chao2_stable'] or r['pair_n_hat'] != '']
    dropped = len(main) - len(reportable)
    A('## Estimates')
    A('')
    A(f'{len(main)} dictionary-eras have two or more usable correctors. Chao2 divides by '
      f'Q2, so a row is only reportable when Q2 >= {MIN_Q2} (or a corrector pair clears '
      f'm >= {MIN_M}); **{dropped} rows fail that and are omitted** rather than shown with '
      f'an estimate that is arithmetic rather than evidence — they are in the CSV with '
      '`chao2_stable = 0`.')
    A('')
    A('| Dict | Era | Correctors | Sites | Best pair | n1 | n2 | m | N (pair Chapman) | 95% CI | Q1 | Q2 | N (Chao2) | 95% CI | N (two-era) |')
    A('|---|---|---:|---:|---|---:|---:|---:|---:|---|---:|---:|---:|---|---:|')
    for r in reportable:
        pair = f"{r['pair_a']} + {r['pair_b']}" if r['pair_a'] else '—'
        pci = (f"{fmt(r['pair_ci_low'])}-{fmt(r['pair_ci_high'])}" if r['pair_n_hat'] != '' else '—')
        cci = (f"{fmt(r['chao2_ci_low'])}-{fmt(r['chao2_ci_high'])}"
               if r['chao2_ci_low'] != '' else '—')
        two = (f"~{fmt(r['two_era_n_hat'])}" + (' (capped)' if r['two_era_capped'] == 1 else '')
               if r['two_era_n_hat'] != '' else '—')
        c2 = (('~' + fmt(r['chao2_n_hat']) + (' (capped)' if r['capped'] else ''))
              if r['chao2_stable'] else 'unstable')
        A(f"| **{r['dict']}** | {r['era']} | {r['correctors']} | {fmt(r['s_observed'])} | {pair} "
          f"| {fmt(r['pair_n1'])} | {fmt(r['pair_n2'])} | {fmt(r['pair_m'])} "
          f"| {('~' + fmt(r['pair_n_hat'])) if r['pair_n_hat'] != '' else '—'} | {pci} "
          f"| {fmt(r['chao2_q1'])} | {fmt(r['chao2_q2'])} | {c2} | {cci} | {two} |")
    A('')
    A('N (two-era) is the published Chapman estimate for the whole dictionary across both '
      'eras — the quantity being cross-checked. The corrector estimates are per '
      'dictionary-ERA, so they estimate the error-site population *visible to that era\'s '
      'correctors*, which is a subset: expect them to be smaller, and read the comparison '
      'as a consistency check on order of magnitude, not as two estimates of one number. '
      'Estimates are capped at the dictionary\'s physical record count '
      '(`dict_record_counts.csv`), as in the two-era analysis.')
    A('')
    A('## What the comparison says')
    A('')
    joint_cmp = [r for r in reportable if r['two_era_n_hat'] != '' and r['chao2_stable']]
    for r in joint_cmp:
        ratio = r['chao2_n_hat'] / r['two_era_n_hat'] if r['two_era_n_hat'] else 0
        pair_txt = (f"the {r['pair_a']}/{r['pair_b']} pair puts it at ~{fmt(r['pair_n_hat'])}"
                    if r['pair_n_hat'] != '' else 'no corrector pair clears the recapture threshold')
        A(f"- **{r['dict']} / {r['era']} era** — Chao2 over {r['correctors']} correctors: "
          f"~{fmt(r['chao2_n_hat'])} error sites ({ratio:.0%} of the two-era "
          f"~{fmt(r['two_era_n_hat'])}); {pair_txt}. "
          f"Q1/Q2 = {fmt(r['chao2_q1'])}/{fmt(r['chao2_q2'])}: "
          f"{'most sites were touched by a single corrector, the signature of strong catchability heterogeneity' if r['chao2_q2'] and r['chao2_q1'] > 5 * r['chao2_q2'] else 'recapture across correctors is substantial'}.")
    A('')
    fresh = [r for r in reportable if r['two_era_n_hat'] == '' and r['chao2_stable']]
    if fresh:
        A('')
        A('**Dictionaries this design can estimate and the two-era design cannot.** '
          'A dictionary is unestimable in `error_recapture.md` when its two eras barely '
          'overlap — which says nothing about whether its correctors overlap. '
          + '; '.join(f"**{r['dict']}** ({r['era']} era, {r['correctors']} correctors, "
                      f"Chao2 ~{fmt(r['chao2_n_hat'])} against {fmt(r['record_count'])} records)"
                      for r in fresh)
          + '. These are first population estimates for those dictionaries, from '
            'correction history alone.')
    A('')
    A('## Sensitivity: joint cells')
    A('')
    A('A cell naming two people (`dhaval_ejf`) is dropped above: one correction by two '
      'people is one capture, not two. Crediting it to both instead makes those occasions '
      'co-capture by construction — positive dependence that inflates m and deflates '
      'N-hat, badly enough in pw\'s form era to invert Q1/Q2. The alternative run gives:')
    A('')
    A('| Dict | Era | N (Chao2, joint dropped) | N (Chao2, joint credited to both) | Correctors |')
    A('|---|---|---:|---:|---:|')
    sens_by = {(r['dict'], r['era']): r for r in sens}
    for r in reportable:
        s = sens_by.get((r['dict'], r['era']))
        s_txt = ('below threshold' if not s else
                 ('~' + fmt(s['chao2_n_hat']) if s['chao2_stable'] else 'unstable'))
        A(f"| {r['dict']} | {r['era']} | {('~' + fmt(r['chao2_n_hat'])) if r['chao2_stable'] else 'unstable'} "
          f"| {s_txt} | {r['correctors']} -> {s['correctors'] if s else 0} |")
    A('')
    A('## Limits of this design')
    A('')
    A('1. **Correctors specialise.** The whole reason Chao2 is here is that catchability is '
       'uneven, but Chao2 corrects for heterogeneity, not for *structured division of '
       'labour* — if one corrector works A-K and another L-Z, they are not sampling the '
       'same population at all, and no incidence estimator repairs that.')
    A('2. **The git era is nearly a one-person operation.** Where a dictionary-era has one '
       'dominant corrector and a small second, the pair estimate rests on that small '
       'sample; the CI shows it.')
    A('3. **Joint cells** are excluded, which costs the form era its largest block; the '
       'sensitivity table above shows what including them would do instead.')
    A('4. Sites are `form_key`-linked headwords, so everything the linkage section of '
       '`error_recapture.md` says about the site key applies here too.')
    A('')
    A('*Object of analysis: correction events over source text (per `docs/BOUNDARY_RULES.md`). '
      'Method: Chapman 1951; Chao 1987 (Chao2 incidence form, log-normal CI). '
      'Candidate paper track — see `Uprava/ARTICLES.md` A48.*')
    with open(OUT_MD, 'w', encoding='utf-8', newline='\n') as f:
        f.write('\n'.join(L) + '\n')


def write_csv(main):
    cols = ['dict', 'era', 'correctors', 's_observed', 'record_count', 'pair_a', 'pair_b',
            'pair_n1', 'pair_n2', 'pair_m', 'pair_n_hat', 'pair_ci_low', 'pair_ci_high',
            'pairs_estimable', 'chao2_q1', 'chao2_q2', 'chao2_n_hat', 'chao2_ci_low',
            'chao2_ci_high', 'chao2_stable', 'capped', 'two_era_n_hat', 'two_era_m',
            'two_era_capped']
    with open(OUT_CSV, 'w', encoding='utf-8', newline='') as f:
        w = csv.DictWriter(f, fieldnames=cols, extrasaction='ignore')
        w.writeheader()
        for r in main:
            w.writerow(r)


# -------------------------------------------------------------------- selftest
def selftest():
    checks = []

    def eq(label, got, want):
        checks.append((label, got == want, got, want))

    eq('alias ejf', persons('ejf'), ['funderburkjim'])
    eq('alias dhavel', persons('dhavel_ejf'), ['drdhaval2785', 'funderburkjim'])
    eq('joint slash', persons('Dhaval/gasyoun'), ['drdhaval2785', 'gasyoun'])
    eq('etal keeps named', persons('ejf_etal'), ['funderburkjim'])
    eq('anonymous dropped', persons('(nouser)'), [])
    eq('form hash kept whole', persons('form_corrector_b517a7c785'), ['form_corrector_b517a7c785'])
    eq('year stripped', persons('Frank Ziesing 2011'), persons('Frank Ziesing, 2010'))
    eq('is_joint', (is_joint('dhaval_ejf'), is_joint('gasyoun')), (True, False))

    # Chao2 against a hand-computed case: S_obs=10, Q1=6, Q2=2, K=3
    #   extra = (2/3) * 36 / 4 = 6  ->  S_est = 16
    c = chao2({f's{i}': (1 if i < 6 else 2 if i < 8 else 3) for i in range(10)}, 3)
    eq('chao2 q1/q2', (c['q1'], c['q2']), (6, 2))
    eq('chao2 point', round(c['n_hat'], 6), 16.0)
    eq('chao2 ci brackets point', c['ci_low'] < c['n_hat'] < c['ci_high'], True)
    # Q2 = 0 falls back to the bias-corrected form: (1/2)*3*2/2 = 1.5 -> 4.5
    c0 = chao2({f's{i}': 1 for i in range(3)}, 2)
    eq('chao2 q2=0 fallback', round(c0['n_hat'], 6), 4.5)

    # a pair below the recapture floor yields no estimate
    eq('pair floor', pair_estimates({'a': set(range(20)), 'b': set(range(8, 40))}) != [], True)
    eq('pair floor low m', pair_estimates({'a': set(range(20)), 'b': set(range(19, 40))}), [])

    bad = [c for c in checks if not c[1]]
    for label, ok, got, want in checks:
        print(f'  {"ok  " if ok else "FAIL"} {label}' + ('' if ok else f'   got={got!r} want={want!r}'))
    print(f'{len(checks) - len(bad)}/{len(checks)} passed')
    return 1 if bad else 0


def main():
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('--keep-joint', action='store_true',
                    help='credit joint corrector cells to both people (sensitivity run)')
    ap.add_argument('--selftest', action='store_true')
    a = ap.parse_args()
    if a.selftest:
        return selftest()

    with open(EVENTS, encoding='utf-8') as f:
        rows = list(csv.DictReader(f))
    n_joint = sum(1 for r in rows if is_joint(r.get('corrector')))
    n_anon = sum(1 for r in rows if not persons(r.get('corrector')))

    keep = a.keep_joint
    main_res = analyse(rows, keep_joint=keep)
    sens_res = analyse(rows, keep_joint=not keep)
    write_csv(main_res)
    write_report(main_res, sens_res, len(rows), n_joint, n_anon, keep)
    print(f'wrote {OUT_MD}')
    print(f'wrote {OUT_CSV}')
    print(f'  dictionary-eras modelled: {len(main_res)}')
    for r in main_res:
        print(f"  {r['dict']:6s} {r['era']:5s} K={r['correctors']:3d} S_obs={r['s_observed']:6,d} "
              f"Chao2={r['chao2_n_hat'] or '-':>8} pair={r['pair_n_hat'] or '-':>8} "
              f"two-era={r['two_era_n_hat'] or '-':>8}")
    print(f'  joint-cell events: {n_joint:,}   unattributable events: {n_anon:,}')
    return 0


if __name__ == '__main__':
    sys.exit(main())
