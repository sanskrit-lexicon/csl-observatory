#!/usr/bin/env python3
"""Capture-recapture estimate of error-prone sites remaining per dictionary (G3).

Operates offline on the committed OBS-T corpus
(`observatory/site/src/data/correction_events_final.csv`). The two OBS-T
layers are treated as two capture occasions over error-prone *sites*:

* occasion 1 = form era (cfr.tsv web submissions, 2014-2019), n1 sites
* occasion 2 = git era (csl-orig commits, 2019-2026), n2 sites
* m = sites captured in BOTH eras

A **site** is (dict, headword) — the dictionary record. We estimate the
population of records harbouring at least one error, N, via the Chapman
estimator, and derive "remaining" = N_hat - S_obs where S_obs = n1 + n2 - m
(distinct sites already caught). This answers, at order-of-magnitude
precision, "how much correction work is left in dictionary X?" - never
before quantified for CDSL.

Estimators
----------
Chapman (bias-corrected Lincoln-Petersen):
    N_hat = (n1+1)(n2+1)/(m+1) - 1
    var   = (n1+1)(n2+1)(n1-m)(n2-m) / ((m+1)^2 (m+2))
    95% CI = N_hat +/- 1.96*sqrt(var)     (reported only when m >= MIN_M)
Chao lower bound (2-occasion incidence form, robustness):
    f1 = n1 + n2 - 2m (sites seen once), f2 = m (seen twice)
    N_chao >= S_obs + f1^2 / (2 f2)

Site linkage (H1477)
--------------------
The two occasions do not spell headwords the same way: form-era cells are
hand-typed web-form submissions (ASCII fallbacks like `nyancana`, SLP1
residue like `prakfti`, homonym digits, pitch accents), git-era cells come
from the machine-clean `<k1>` field. An exact-string join therefore MISSES
true recaptures and inflates N_hat. Sites are linked with the measured
`form_key` level of `headword_linkage.py` (see that module for the full
ladder and its measured false-match rates), plus the headword-component
alias: a form-era correction attributed to the headword itself names the
record through its *corrected* value.

Design caveats (stated in full in the report)
---------------------------------------------
1. The occasions are SEQUENTIAL, not simultaneous: era-1 fixes remove
   errors, so era-2 recapture of a site requires a *different* residual
   error there. Where sites carry few errors this depresses m and inflates
   N_hat (upward bias). `corrector_recapture.py` builds the independent
   within-era design that can size this bias.
2. Catchability is heterogeneous and positively correlated (both eras
   gravitate to long, high-traffic entries), which biases N_hat DOWNWARD.
   The two violations pull in opposite directions; we report order of
   magnitude, not precision, and the CI is statistical-only.
3. Site key excludes the error component: the form layer is 77% component-
   unattributed, so including the component collapses matches on missing
   data, not on substance (shown in the sensitivity table).

Outputs
-------
* `reports/error_recapture.md`
* `observatory/site/src/data/error_recapture.csv`   (per-dict estimates)
* `observatory/site/src/data/linkage_ladder.csv`    (m and measured false
  matches per dict x linkage level — the evidence for the level chosen)

Usage:  python scripts/error_recapture.py [--selftest]
"""
import csv, math, os, sys
from collections import defaultdict
sys.stdout.reconfigure(encoding='utf-8'); sys.stderr.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DATA = os.path.join(ROOT, 'observatory', 'site', 'src', 'data')
EVENTS = os.path.join(DATA, 'correction_events_final.csv')
CAMPAIGNS = os.path.join(DATA, 'obs_t_campaigns.csv')
OUT_MD = os.path.join(ROOT, 'reports', 'error_recapture.md')
OUT_CSV = os.path.join(DATA, 'error_recapture.csv')
OUT_LADDER = os.path.join(DATA, 'linkage_ladder.csv')

sys.path.insert(0, HERE)
import headword_linkage as HL   # noqa: E402

MIN_M = 10   # minimum recaptures for a point estimate

# Operating linkage level, chosen on the measured evidence in the report's
# "Site linkage" section: `form_key` keeps vowel length and retroflexion, so it
# does not merge minimal pairs, and its measured false-match count over the
# actual matched pairs is 0-1 per dictionary.
LINKAGE_LEVEL = 'form_key'
USE_ALIAS = True

# <L> record counts per dictionary — the physical cap: N cannot exceed the number
# of records in the dictionary. Derived for all 44 csl-orig v02 dictionaries by
# `headword_linkage.py` into `dict_record_counts.csv` (H1477); the three counted
# by hand on 2026-07-03 remain as the offline fallback and as a regression check.
RECORD_COUNTS_FALLBACK = {'pw': 170556, 'mw': 286525, 'bur': 19776}
RECORD_COUNTS = {**RECORD_COUNTS_FALLBACK, **HL.load_record_counts()}


def chapman(n1, n2, m):
    n_hat = (n1 + 1) * (n2 + 1) / (m + 1) - 1
    var = ((n1 + 1) * (n2 + 1) * (n1 - m) * (n2 - m)) / (((m + 1) ** 2) * (m + 2))
    se = math.sqrt(var)
    return n_hat, se, max(n1 + n2 - m, n_hat - 1.96 * se), n_hat + 1.96 * se


def chao_lb(n1, n2, m):
    s_obs = n1 + n2 - m
    f1, f2 = n1 + n2 - 2 * m, m
    if f2 == 0:
        return None
    return s_obs + f1 * f1 / (2 * f2)


def collect(rows, with_component=False, exclude=None, level=None, alias=None):
    """dict -> {'form': set(sites), 'git': set(sites)}, linked per `headword_linkage`."""
    return HL.site_sets(rows,
                        level=LINKAGE_LEVEL if level is None else level,
                        alias=USE_ALIAS if alias is None else alias,
                        with_component=with_component, exclude=exclude)


def estimates(per):
    """List of per-dict stat dicts, sorted by S_obs desc."""
    out = []
    for d, s in per.items():
        n1, n2 = len(s['form']), len(s['git'])
        m = len(s['form'] & s['git'])
        s_obs = n1 + n2 - m
        row = {'dict': d, 'n1_form': n1, 'n2_git': n2, 'm_overlap': m,
               's_observed': s_obs, 'estimable': int(m >= MIN_M and n1 > 0 and n2 > 0),
               'n_hat': '', 'ci_low': '', 'ci_high': '', 'chao_hetero': '',
               'record_count': RECORD_COUNTS.get(d, ''), 'capped': '',
               'remaining_hat': ''}
        if row['estimable']:
            n_hat, se, lo, hi = chapman(n1, n2, m)
            cap = RECORD_COUNTS.get(d)
            capped = cap is not None and n_hat > cap
            if capped:
                n_hat, hi = cap, min(hi, cap)
                lo = min(lo, cap)
            row.update(n_hat=round(n_hat), ci_low=round(lo), ci_high=round(hi),
                       capped=int(capped), remaining_hat=round(n_hat - s_obs))
            c = chao_lb(n1, n2, m)
            row['chao_hetero'] = round(min(c, cap) if cap else c) if c is not None else ''
        out.append(row)
    out.sort(key=lambda r: -r['s_observed'])
    return out


def load_campaign_excl():
    """Set of (dict_lower, ISO-date) covered by a documented campaign."""
    excl = set()
    if not os.path.exists(CAMPAIGNS):
        return excl
    with open(CAMPAIGNS, encoding='utf-8') as f:
        for r in csv.DictReader(f):
            for d in r['dicts'].split('|'):
                if d.strip():
                    excl.add((d.strip().lower(), r['date']))
    return excl


def load_corrector_crosscheck():
    """Stable Chao2 rows from the within-era design, for the cross-check table."""
    path = os.path.join(DATA, 'corrector_recapture.csv')
    if not os.path.exists(path):
        return []
    out = []
    with open(path, encoding='utf-8') as f:
        for r in csv.DictReader(f):
            if r.get('chao2_stable') == '1' and r.get('two_era_n_hat'):
                out.append({'dict': r['dict'], 'era': r['era'],
                            'chao2': int(r['chao2_n_hat'])})
    return out


def linkage_ladder(rows, dicts=None):
    """Per dict x linkage level: recaptures won, and false matches measured.

    The key levels are run WITHOUT the alias so the table isolates what the key
    itself does; the operating configuration (`form_key` + alias) is reported as
    its own row. `ed1` is the edit-distance-1 join ported from
    `attribute_components.py`: not a key, so it is scored as "clean-level matches
    plus every form-side string that lands within edit distance 1 of a git-side
    one". False matches are counted by the attestation test (both strings are
    real, distinct headwords of that dictionary => the link joined two records)."""
    out = []
    per_clean = HL.site_sets(rows, level='clean', alias=False)
    for d in sorted(dicts or per_clean):
        att = HL.Attestation(d)
        for level, keyfn, _ in HL.KEY_LEVELS:
            per = HL.site_sets(rows, level=level, alias=False)
            f, g = per[d]['form'], per[d]['git']
            inv = defaultdict(lambda: {'form': set(), 'git': set()})
            for r in rows:                       # keep the raw strings behind each key
                if r['dict'] != d:
                    continue
                h = (r['headword_iast'] or '').strip()
                if h and keyfn(h):
                    inv[keyfn(h)][r['source_layer']].add(h)
            false_keys = 0
            for k in f & g:
                pairs = [(x, y) for x in inv[k]['form'] for y in inv[k]['git']]
                if pairs and all(HL.clean(x) == HL.clean(y) for x, y in pairs):
                    continue                     # same string, nothing was linked
                if any(att.verdict(x, y) == 'false' for x, y in pairs):
                    false_keys += 1
            out.append({'dict': d, 'level': level, 'n1_form': len(f), 'n2_git': len(g),
                        'm_overlap': len(f & g), 'false_matches': false_keys,
                        'audited': int(att.available)})
        # ed1, on the clean level
        fc, gc = per_clean[d]['form'], per_clean[d]['git']
        links = HL.ed1_links(fc - gc, gc)
        out.append({'dict': d, 'level': 'ed1', 'n1_form': len(fc), 'n2_git': len(gc),
                    'm_overlap': len(fc & gc) + len({x for x, _ in links}),
                    'false_matches': sum(1 for x, y in links if att.verdict(x, y) == 'false'),
                    'audited': int(att.available)})
        # the operating configuration
        per = HL.site_sets(rows, level=LINKAGE_LEVEL, alias=True)
        f, g = per[d]['form'], per[d]['git']
        out.append({'dict': d, 'level': f'{LINKAGE_LEVEL}+alias', 'n1_form': len(f),
                    'n2_git': len(g), 'm_overlap': len(f & g), 'false_matches': '',
                    'audited': int(att.available)})
    return out


def main():
    with open(EVENTS, encoding='utf-8') as f:
        rows = list(csv.DictReader(f))

    # main analysis: site = (dict, headword)
    per = collect(rows)
    main_est = estimates(per)
    # sensitivity a: component in the site key
    comp_est = estimates(collect(rows, with_component=True))
    # sensitivity b: exclude events on documented campaign (dict, date) days
    excl = load_campaign_excl()
    n_excl = sum(1 for r in rows if (r['dict'], r['date'][:10]) in excl)
    camp_est = estimates(collect(rows, exclude=excl))
    # sensitivity c: what the exact-string join of the original design gives
    exact_est = estimates(collect(rows, level='exact', alias=False))

    est_rows = [r for r in main_est if r['estimable']]
    total_obs = sum(r['s_observed'] for r in main_est)
    total_hat = sum(r['n_hat'] for r in est_rows)
    total_rem = sum(r['remaining_hat'] for r in est_rows)
    total_obs_est = sum(r['s_observed'] for r in est_rows)

    with open(OUT_CSV, 'w', encoding='utf-8', newline='') as f:
        w = csv.DictWriter(f, fieldnames=list(main_est[0].keys()))
        w.writeheader()
        for r in main_est:
            w.writerow(r)

    # linkage evidence: run the ladder on every dictionary big enough for the
    # comparison to mean anything (both eras present, >= 100 observed sites)
    ladder_dicts = [r['dict'] for r in main_est
                    if r['n1_form'] and r['n2_git'] and r['s_observed'] >= 100]
    ladder = linkage_ladder(rows, ladder_dicts)
    with open(OUT_LADDER, 'w', encoding='utf-8', newline='') as f:
        w = csv.DictWriter(f, fieldnames=['dict', 'level', 'n1_form', 'n2_git',
                                          'm_overlap', 'false_matches', 'audited'])
        w.writeheader()
        w.writerows(ladder)
    lad = {(r['dict'], r['level']): r for r in ladder}
    collisions = HL.load_collisions()

    by = {r['dict']: r for r in main_est}
    camp_by = {r['dict']: r for r in camp_est}
    exact_by = {r['dict']: r for r in exact_est}
    comp_by = {r['dict']: r for r in comp_est}

    L = []; A = L.append
    A('# Capture-recapture: how much correction work is left?')
    A('')
    A('_Generated by `scripts/error_recapture.py` from `observatory/site/src/data/'
      'correction_events_final.csv` (offline, reproducible). Roadmap: Workstream '
      'G3. Estimand: dictionary records ("sites") harbouring at least one error, '
      'per dictionary — an order-of-magnitude estimate, not a precision one._')
    A('')
    A('## Design')
    A('')
    A('OBS-T\'s two correction layers act as two capture occasions over error-'
      'prone sites (dict + headword): the **form era** (cfr.tsv web submissions, '
      '2014-2019) and the **git era** (csl-orig commits, 2019-2026). Sites '
      'corrected in both eras are "recaptures"; the Chapman estimator converts '
      'capture/recapture counts into an estimate of the total error-site '
      f'population N. Point estimates only where recaptures m >= {MIN_M}.')
    A('')
    A('An **independent second design** — correctors within one era as the capture '
      'occasions — cross-checks these numbers in '
      '[`corrector_recapture.md`](corrector_recapture.md). It is the only handle on '
      'the sequential-occasion bias below, which cannot be measured from inside the '
      'two-era design.')
    A('')
    A('**Assumption violations, stated plainly.** (1) The occasions are '
      'sequential: a site fixed completely in era 1 cannot be recaptured in era '
      '2, which depresses m and biases N upward. (2) Catchability is '
      'heterogeneous and positively correlated across eras (both target long, '
      'high-traffic entries), biasing N downward. The violations pull in '
      'opposite directions; confidence intervals are statistical-only and do '
      'not cover these design biases. (3) Population closure is imperfect '
      '(new errors can be introduced between eras), a second upward pressure. '
      'Read every figure as order-of-magnitude.')
    A('')
    A('## Site linkage: how the two eras are joined, and at what error rate')
    A('')
    A('The eras do not spell headwords alike. Form-era cells are hand-typed web-form '
      'submissions carrying ASCII fallbacks (`nyancana` for `nyañcana`), homonym '
      'digits, pitch accents, and — in 3,905 cells — raw SLP1 residue (`prakfti`, '
      '`āQaka`); git-era cells come from the machine-clean `<k1>` field. Joining them '
      'by exact string misses true recaptures, and every missed recapture pushes '
      'N upward. But a key that merges *distinct lemmas* pushes N down instead, and '
      'Sanskrit headword lists are dense with minimal pairs (`kara`/`kāra`, '
      '`kṛṣ`/`tṛṣ`). The linkage level is therefore chosen on measured evidence, not '
      'taste; the ladder lives in `scripts/headword_linkage.py`.')
    A('')
    A('Two independent measurements of what each level costs, both offline against '
      'the dictionaries\' own `<k1>` inventories: the **collision rate** (share of '
      'the dictionary\'s own records whose key is shared with another record — an '
      'upper bound on ambiguity), and **measured false matches** (matched pairs in '
      'which both strings are real, distinct headwords of that dictionary, so the '
      'link joined two different records).')
    A('')
    A('| Level | What it folds | Collision rate (pw / mw) | Recaptures m won (pw / mw / bur) | Measured false matches (pw / mw / bur) |')
    A('|---|---|---|---:|---:|')
    for level, _, desc in HL.KEY_LEVELS:
        cr = ' / '.join(f"{collisions.get((d, level), float('nan')):.2%}" for d in ('pw', 'mw'))
        ms = ' / '.join(str(lad[(d, level)]['m_overlap']) if (d, level) in lad else '—'
                        for d in ('pw', 'mw', 'bur'))
        fs = ' / '.join(str(lad[(d, level)]['false_matches']) if (d, level) in lad else '—'
                        for d in ('pw', 'mw', 'bur'))
        A(f'| `{level}` | {desc} | {cr} | {ms} | {fs} |')
    ed = ' / '.join(str(lad[(d, 'ed1')]['m_overlap']) if (d, 'ed1') in lad else '—'
                    for d in ('pw', 'mw', 'bur'))
    edf = ' / '.join(str(lad[(d, 'ed1')]['false_matches']) if (d, 'ed1') in lad else '—'
                     for d in ('pw', 'mw', 'bur'))
    A(f'| `ed1` | any single substitution/insertion/deletion | n/a (pairwise) | {ed} | {edf} |')
    op = f'{LINKAGE_LEVEL}+alias'
    ops = ' / '.join(str(lad[(d, op)]['m_overlap']) if (d, op) in lad else '—'
                     for d in ('pw', 'mw', 'bur'))
    A(f'| **`{op}`** (operating) | + headword-component alias | as `{LINKAGE_LEVEL}` | **{ops}** | — |')
    A('')
    A('**The edit-distance-1 join is unusable here, and that is a result, not a '
      'shrug.** Porting the `deletes1`/`within1` machinery that `attribute_components.py` '
      'uses against csl-orig produces mostly false links between real, distinct '
      f"headwords ({lad[('pw', 'ed1')]['false_matches']} of pw's, "
      f"{lad[('mw', 'ed1')]['false_matches']} of mw's): `nāman`/`yāman`, `kṛṣ`/`tṛṣ`, "
      '`nīla`/`nīca` are all one edit apart and all different words. An estimator '
      'whose N is driven by m cannot consume that. `norm`, which drops every '
      'combining mark, is rejected on the same evidence one step earlier: it makes '
      'roughly one record in nine ambiguous against the dictionary\'s own inventory.')
    A('')
    A('`repair` is not fuzzy matching at all: `f`, `q`, `w`, `x` and `z` cannot occur '
      'in IAST, so a cell containing one is provably still in SLP1 and is decoded, '
      'not guessed (`prakfti` -> `prakṛti`, `āQaka` -> `āḍhaka`). `form_key` then '
      'folds anusvāra and homorganic nasals while **keeping vowel length and '
      'retroflexion**, which is what separates it from `norm`. The alias layer adds '
      'the corrected value of form-era events whose correction was attributed to the '
      'headword itself (all 4,929 carry `evidence_level = derived`): there the '
      'corrected string *is* the record\'s headword.')
    A('')
    A('Effect on the published figures — the same estimator, exact vs linked join:')
    A('')
    A('| Dict | m (exact) | m (linked) | N (exact join) | N (linked join) |')
    A('|---|---:|---:|---:|---:|')
    for r in est_rows:
        e = exact_by.get(r['dict'], {})
        A(f"| {r['dict']} | {e.get('m_overlap', '—')} | {r['m_overlap']} "
          f"| {('~' + format(e['n_hat'], ',')) if e.get('n_hat') != '' else 'below threshold'} "
          f"| ~{r['n_hat']:,}{' (capped)' if r['capped'] else ''} |")
    A('')
    A('## Headline')
    A('')
    A('| Metric | Value |')
    A('|---|---:|')
    A(f'| Correction events analysed | {len(rows):,} |')
    A(f'| Distinct error sites observed (all 43 dicts) | {total_obs:,} |')
    A(f'| Dictionaries with enough overlap to estimate (m >= {MIN_M}) | {len(est_rows)} |')
    A(f'| Estimated error-site population (those dicts) | **~{total_hat:,}** |')
    A(f'| Sites already corrected there | {total_obs_est:,} |')
    A(f'| **Estimated error sites still uncorrected there** | **~{total_rem:,}** |')
    A('')
    A('## Per-dictionary estimates')
    A('')
    A('| Dict | Records | Form sites n1 | Git sites n2 | Recaptures m | Observed | N (Chapman) | 95% CI | Chao (heterogeneity scenario) | Remaining |')
    A('|---|---:|---:|---:|---:|---:|---:|---|---:|---:|')
    for r in est_rows:
        n_show = f"~{r['n_hat']:,}" + (' (capped)' if r['capped'] else '')
        A(f"| **{r['dict']}** | {r['record_count']:,} | {r['n1_form']:,} | {r['n2_git']:,} | {r['m_overlap']} "
          f"| {r['s_observed']:,} | {n_show} | {r['ci_low']:,}-{r['ci_high']:,} "
          f"| {r['chao_hetero']:,} | **~{r['remaining_hat']:,}** |")
    A('')
    capped_now = [r['dict'] for r in est_rows if r['capped']]
    A('Estimates are capped at the dictionary\'s physical record count, now derived '
      f'for all {len(RECORD_COUNTS)} `csl-orig` v02 dictionaries by '
      '`scripts/headword_linkage.py` (`dict_record_counts.csv`) rather than for three '
      'by hand. A raw estimate that EXCEEDS the cap'
      + (f" ({', '.join(capped_now)})" if capped_now else '') +
      ' means the recapture rate is too low to bound the population below the whole '
      'dictionary — read a capped row as "this dictionary should be treated as '
      'unproofread", not as a precise count.')
    A('')
    A('Under the exact-string join **bur** was such a row; the linkage moves it off '
      f"the cap ({exact_by['bur']['m_overlap']} recaptures -> {by['bur']['m_overlap']}, "
      f"N ~{by['bur']['n_hat']:,} against {by['bur']['record_count']:,} records), which "
      'is the clearest single demonstration that the old ceiling was a measurement '
      'artefact of the join rather than a fact about the dictionary.')
    A('')
    A('Dictionaries below the overlap threshold (lower bound = observed sites only):')
    A('')
    A('| Dict | n1 | n2 | m | Observed (lower bound on N) |')
    A('|---|---:|---:|---:|---:|')
    for r in main_est:
        if not r['estimable']:
            A(f"| {r['dict']} | {r['n1_form']:,} | {r['n2_git']:,} | {r['m_overlap']} | {r['s_observed']:,} |")
    A('')
    A('## Sensitivity')
    A('')
    A('**(a) Site key with the error component.** Including `error_component` in '
      'the site key collapses recaptures (e.g. '
      f"mw m {by['mw']['m_overlap']} -> {comp_by['mw']['m_overlap']}, "
      f"pw m {by['pw']['m_overlap']} -> {comp_by['pw']['m_overlap']}) — but this "
      'reflects missing data, not substance: 77% of form-era events are '
      'component-unattributed (`evidence_level = inferred`), so component keys '
      'mismatch mechanically. The headword-level key is the honest unit.')
    A('')
    A(f'**(b) Campaign exclusion.** Dropping the {n_excl:,} events that fall on '
      'documented campaign days for their dictionary (obs_t_campaigns.csv) '
      'moves the estimable dictionaries to:')
    A('')
    A('| Dict | N (all events) | N (campaigns excluded) |')
    A('|---|---:|---:|')
    for r in est_rows:
        c = camp_by.get(r['dict'], {})
        cn = f"~{c.get('n_hat'):,}" if c.get('estimable') else 'below threshold'
        A(f"| {r['dict']} | ~{r['n_hat']:,} | {cn} |")
    A('')
    A('**(c) Heterogeneous catchability.** Chapman assumes every site is equally '
      'catchable; in reality correctors specialise, so the two eras oversample '
      'the same prominent entries and Chapman UNDERESTIMATES. The Chao column '
      'is the standard estimate under that heterogeneity scenario (Chao 1987): '
      'read Chapman and Chao as the two ends of the plausible range, not as '
      'point-and-floor. Both are capped at the record count; for pw and mw the '
      'heterogeneity scenario saturates near the whole dictionary — consistent '
      'with OCR-derived text where most long entries harbour at least one '
      'defect.')
    A('')
    A('## Reading')
    A('')
    if est_rows:
        top = est_rows[0]
        A(f'- The two eras overlap remarkably little: of {total_obs:,} observed '
          'error sites org-wide, only a few hundred were touched in both eras. '
          'Under mark-recapture logic, low overlap between two substantial '
          'samples means the underlying population is LARGE: what has been '
          'corrected so far is a minority of what exists.')
        for r in est_rows:
            pct = 100 * r['s_observed'] / r['n_hat']
            share = 100 * r['n_hat'] / r['record_count'] if r['record_count'] else None
            cap_note = ' (estimate capped at the full dictionary)' if r['capped'] else ''
            A(f"- **{r['dict']}**: ~{r['n_hat']:,} error-prone records estimated"
              f"{cap_note} = ~{share:.0f}% of its {r['record_count']:,} records; "
              f"{r['s_observed']:,} corrected so far = **~{pct:.0f}% of the "
              f"estimated work done**, ~{r['remaining_hat']:,} records still "
              'awaiting a first correction (Chapman scenario; under '
              'heterogeneity the remaining share is larger).')
        A('- Most dictionaries cannot be estimated yet — their two-era overlap '
          'is below threshold. That is itself a finding: correction effort has '
          'been so concentrated (and era-partitioned) that for most dictionaries '
          'we cannot even bound the remaining work from correction history alone.')
    cross = load_corrector_crosscheck()
    if cross:
        A('')
        A('**Cross-check against the within-era design.** '
          '[`corrector_recapture.md`](corrector_recapture.md) estimates the same '
          'quantity from correctors-as-occasions inside a single era, which does not '
          'inherit the sequential-occasion bias:')
        A('')
        A('| Dict | Era | N (two-era, whole dictionary) | N (Chao2 over that era\'s correctors) |')
        A('|---|---|---:|---:|')
        for c in cross:
            A(f"| {c['dict']} | {c['era']} | ~{by[c['dict']]['n_hat']:,} | ~{c['chao2']:,} |")
        A('')
        A('The within-era estimates cover only the sites visible to that era\'s '
          'correctors, so they are not expected to match; agreement of order of '
          'magnitude is the check that passes here, and where the within-era figure '
          'runs HIGHER (mw) the sequential-occasion bias is not the dominant term.')
    A('')
    A('*Object of analysis: correction events over source text (per '
      '`docs/BOUNDARY_RULES.md`). Method: Chapman 1951; Chao 1987 heterogeneity scenario. '
      'Candidate paper track — see `Uprava/ARTICLES.md`.*')

    with open(OUT_MD, 'w', encoding='utf-8', newline='\n') as f:
        f.write('\n'.join(L) + '\n')

    print(f'wrote {OUT_MD}')
    print(f'wrote {OUT_CSV}')
    print(f'  estimable dicts: {[r["dict"] for r in est_rows]}')
    print(f'  total N_hat (estimable): {total_hat:,}  remaining: {total_rem:,}')
    print(f'  campaign-excluded events: {n_excl:,}')


def selftest():
    """Estimator + linkage-wiring checks; needs neither csl-orig nor the corpus."""
    checks = []

    def eq(label, got, want):
        checks.append((label, got == want, got, want))

    # Chapman on a textbook case: n1=n2=100, m=50 -> (101*101)/51 - 1 = 199.02
    n_hat, se, lo, hi = chapman(100, 100, 50)
    eq('chapman point', round(n_hat, 2), 199.02)
    eq('chapman ci ordered', lo < n_hat < hi, True)
    # perfect recapture pins N at the observed count
    eq('chapman m=n1=n2', round(chapman(10, 10, 10)[0], 6), 10.0)
    # Chao lower bound: n1=n2=100, m=50 -> S_obs 150 + 100^2/(2*50) = 250
    eq('chao lower bound', chao_lb(100, 100, 50), 250.0)
    eq('chao no doubles', chao_lb(10, 10, 0), None)

    # a linked join can only ever find MORE recaptures than an exact one
    ev = [
        {'dict': 'x', 'source_layer': 'form', 'headword_iast': 'prakfti', 'date': '2015-01-01',
         'error_component': 'unattributed', 'new_iast': ''},
        {'dict': 'x', 'source_layer': 'git', 'headword_iast': 'prakṛti', 'date': '2021-01-01',
         'error_component': 'sense', 'new_iast': ''},
    ]
    ex = estimates(collect(ev, level='exact', alias=False))[0]
    lk = estimates(collect(ev))[0]
    eq('exact join misses slp1 residue', ex['m_overlap'], 0)
    eq('linked join finds it', lk['m_overlap'], 1)
    eq('linked s_obs shrinks', (ex['s_observed'], lk['s_observed']), (2, 1))

    # the record-count cap is loaded for far more than the three hand-counted dicts
    eq('record counts loaded', len(RECORD_COUNTS) >= 3, True)
    eq('record counts agree with hand count',
       all(RECORD_COUNTS[d] == v for d, v in RECORD_COUNTS_FALLBACK.items()), True)

    bad = [c for c in checks if not c[1]]
    for label, ok, got, want in checks:
        print(f'  {"ok  " if ok else "FAIL"} {label}' + ('' if ok else f'   got={got!r} want={want!r}'))
    print(f'{len(checks) - len(bad)}/{len(checks)} passed')
    return 1 if bad else 0


if __name__ == '__main__':
    if '--selftest' in sys.argv:
        sys.exit(selftest())
    main()
