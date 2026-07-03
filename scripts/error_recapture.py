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

Design caveats (stated in full in the report)
---------------------------------------------
1. The occasions are SEQUENTIAL, not simultaneous: era-1 fixes remove
   errors, so era-2 recapture of a site requires a *different* residual
   error there. Where sites carry few errors this depresses m and inflates
   N_hat (upward bias).
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

Usage:  python scripts/error_recapture.py
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

MIN_M = 10   # minimum recaptures for a point estimate

# <L> record counts from the sibling csl-orig v02 sources (counted 2026-07-03,
# `grep -c "^<L>"`); embedded so the script stays offline-reproducible. The
# physical cap: N cannot exceed the number of records in the dictionary.
RECORD_COUNTS = {'pw': 170556, 'mw': 286525, 'bur': 19776}


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


def collect(rows, with_component=False, exclude=None):
    """dict -> {'form': set(sites), 'git': set(sites)}."""
    per = defaultdict(lambda: {'form': set(), 'git': set()})
    for r in rows:
        h = r['headword_iast'].strip()
        if not h:
            continue
        if exclude and (r['dict'], r['date'][:10]) in exclude:
            continue
        key = (h, r['error_component']) if with_component else h
        per[r['dict']][r['source_layer']].add(key)
    return per


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

    by = {r['dict']: r for r in main_est}
    camp_by = {r['dict']: r for r in camp_est}
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
    A('Estimates are capped at the dictionary\'s physical record count (from the '
      'sibling `csl-orig` v02 sources, 2026-07-03). A raw estimate that EXCEEDS '
      'the cap (bur) signals that headword-match noise between the two eras is '
      'inflating the estimate there — read a capped row as "the whole '
      'dictionary should be treated as unproofread", not as a precise count.')
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


if __name__ == '__main__':
    main()
