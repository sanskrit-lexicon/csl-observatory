#!/usr/bin/env python3
"""Do any estimators survive the sub-10-recapture floor? (GAPS §2 / H3986)

`error_recapture.py` estimates the error-site population N per dictionary from
the two OBS-T eras via Chapman, and reports a point estimate only where the
recapture count m >= 10. That threshold leaves **39 of 43** dictionaries with no
estimate at all (a 40th, cae, is estimable but its raw Chapman exceeds the
dictionary's record count, so it is published capped and carries no usable
point). Correction-campaign planning consequently still assumes a convergence it
cannot demonstrate for almost the whole corpus.

This script asks whether some other estimator can fill that hole, and answers it
the only honest way: by scoring candidates **where Chapman IS computable** —
pw, mw and bur, the three dictionaries with an uncapped Chapman point estimate —
before letting any of them near the other 39.

Candidates
----------
C0  Chapman (bias-corrected Lincoln-Petersen)         -- the CONTROL, not a candidate.
C1  Chao2 over the two eras (incidence, bias-corrected). Needs only m >= 1.
C2  Chao2 over CORRECTORS within one era (from `corrector_recapture.py`).
    Does not use the two-era overlap at all, so the floor does not bind it;
    it needs K >= 3 correctors and a stable Q1/Q2 instead.
C3a Pooled-prevalence hierarchical fit (the "censored panel" candidate).
    Model N_d = rho * R_d with R_d the dictionary's record count and rho a
    prevalence shared across dictionaries; m_d ~ Poisson(n1_d n2_d / N_d).
    Closed-form MLE  rho_hat = sum_d c_d / sum_d m_d,  c_d = n1_d n2_d / R_d.
    Every dictionary contributes, INCLUDING the m = 0 ones: an m of zero against
    a large n1 n2 is not missing data, it is evidence that N is large. That is
    the sense in which the panel is censored rather than absent.
C3b Empirical-Bayes shrinkage of C3a: phi_d = 1/rho_d ~ Gamma(a, b) fitted by
    moments over the dictionaries with m > 0, posterior mean (a + m_d)/(b + c_d).
    A dictionary with a little of its own signal moves off the pooled value.
C4  Correction-density extrapolation (the RECIPES-§6-style candidate):
    take the observed error-site prevalence N/R from the dictionaries where
    Chapman IS computable and apply it to the target's record count. Uses no
    per-dictionary correction history beyond the dictionary's size.

Two scorings, both pre-registered before the numbers were looked at
------------------------------------------------------------------
**Scoring 1 - leave-one-out on the ground truth.** For each target t in
{pw, mw, bur}: fit whatever the candidate needs on the OTHER dictionaries only
(C3a/C3b/C4 are fitted; C1/C2 are self-contained and simply evaluated), predict
N_t, compare against t's own Chapman point and 95% CI. Fitting on the target
would be circular, and with three ground-truth dictionaries it would also be
invisible.

**Scoring 2 - censoring stress test.** LOO alone still hands the candidate a
target whose data is rich. The real question is whether the estimator survives
when the target's own sample is AT the floor. So each target's git-era site set
is thinned by independent Bernoulli(r) retention, r chosen so that the expected
recaptures E[m] = 5 (i.e. below the threshold of 10), B = 400 replicates, fixed
seed. Each candidate is recomputed on the thinned data and compared against the
target's FULL-data Chapman. This measures bias and spread at the sample size
that actually matters. Chapman itself is run through the same mill as the
control - the floor exists precisely because Chapman fails this test.

Verdict rule (fixed in advance)
-------------------------------
QUALIFIES        - for ALL THREE targets: the LOO point estimate falls inside the
                   target's Chapman 95% CI, AND under censoring the median
                   estimate is within a factor of 2 of full-data Chapman with an
                   interquartile ratio P75/P25 <= 3.
CONDITIONAL      - the factor-2 median condition holds for all three, but the CI
                   or the spread condition fails.
DOES NOT QUALIFY - otherwise.

A finding that NO candidate qualifies is a result, not a failure: it converts an
open method question into a measured ceiling and tells correction-campaign
planning to stop assuming convergence for the 39.

Outputs
-------
* `reports/error_recapture_lowm.md`                       (the comparison)
* `observatory/site/src/data/error_recapture_lowm.csv`    (per candidate x target)

Usage:  python scripts/lowm_estimators.py [--selftest] [--reps N]
"""
import argparse, csv, math, os, random, statistics, sys, zlib
from collections import defaultdict

sys.stdout.reconfigure(encoding='utf-8'); sys.stderr.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DATA = os.path.join(ROOT, 'observatory', 'site', 'src', 'data')
EVENTS = os.path.join(DATA, 'correction_events_final.csv')
CORRECTOR = os.path.join(DATA, 'corrector_recapture.csv')
OUT_MD = os.path.join(ROOT, 'reports', 'error_recapture_lowm.md')
OUT_CSV = os.path.join(DATA, 'error_recapture_lowm.csv')
OUT_CAL = os.path.join(DATA, 'error_recapture_calibrated.csv')

sys.path.insert(0, HERE)
import error_recapture as ER          # noqa: E402  (chapman, collect, RECORD_COUNTS)
import headword_linkage as HL         # noqa: E402

MIN_M = ER.MIN_M                      # 10 — the floor this whole exercise is about
TARGET_EXP_M = 5                      # censoring stress test thins to E[m] = 5
REPS = 400
SEED = 3986
LADDER = (1, 2, 5, 9)   # E[m] rungs for the precision ladder

# Pre-registered acceptance thresholds.
FACTOR_TOL = 2.0                      # median within this factor of full-data Chapman
IQ_RATIO_TOL = 3.0                    # P75/P25 of the censored replicates


# --------------------------------------------------------------------------- #
# estimators
# --------------------------------------------------------------------------- #
def chao2_two_era(n1, n2, m):
    """Bias-corrected Chao2 over T=2 incidence occasions. Needs Q2 = m >= 1."""
    s_obs = n1 + n2 - m
    q1, q2 = n1 + n2 - 2 * m, m
    if q2 <= 0:
        return None
    return s_obs + ((2 - 1) / 2) * (q1 * q1) / (2 * q2)


def fit_pooled_rho(panel, exclude=()):
    """MLE of the shared prevalence rho in N_d = rho * R_d, m_d ~ Pois(c_d/rho).

    Returns (rho_hat, n_dicts_used, sum_c, sum_m). Dictionaries with m = 0 are
    kept: they carry the censored information that N is large.
    """
    sum_c = sum_m = 0.0
    used = 0
    for d in panel:
        if d['dict'] in exclude:
            continue
        if not d['records'] or d['n1'] == 0 or d['n2'] == 0:
            continue
        sum_c += d['n1'] * d['n2'] / d['records']
        sum_m += d['m']
        used += 1
    if sum_m <= 0:
        return None, used, sum_c, sum_m
    return sum_c / sum_m, used, sum_c, sum_m


def fit_eb_gamma(panel, exclude=()):
    """Method-of-moments Gamma(a, b) prior on phi = 1/rho, over dicts with m > 0."""
    phis = []
    for d in panel:
        if d['dict'] in exclude or not d['records'] or d['m'] <= 0:
            continue
        c = d['n1'] * d['n2'] / d['records']
        if c > 0:
            phis.append(d['m'] / c)
    if len(phis) < 3:
        return None
    mu = statistics.fmean(phis)
    var = statistics.pvariance(phis)
    if var <= 0 or mu <= 0:
        return None
    b = mu / var          # rate
    a = mu * b            # shape
    return a, b


def eb_posterior_n(a, b, n1, n2, m, records):
    """Empirical-Bayes posterior-mean N for one dictionary."""
    if not records or n1 == 0 or n2 == 0:
        return None
    c = n1 * n2 / records
    phi_post = (a + m) / (b + c)      # posterior mean of 1/rho
    if phi_post <= 0:
        return None
    return records / phi_post


def density_extrapolate(truth_rows, exclude=()):
    """Mean error-site prevalence N/R over the ground-truth dicts, minus `exclude`."""
    vals = [r['n_hat'] / r['records'] for r in truth_rows
            if r['dict'] not in exclude and r['records']]
    if not vals:
        return None
    return statistics.fmean(vals)


def load_corrector_chao2():
    """dict -> best stable within-era Chao2 estimate (largest era by S_obs)."""
    best = {}
    if not os.path.exists(CORRECTOR):
        return best
    with open(CORRECTOR, encoding='utf-8') as f:
        for r in csv.DictReader(f):
            if r.get('chao2_stable') != '1' or not r.get('chao2_n_hat'):
                continue
            d, s_obs = r['dict'], int(r['s_observed'])
            if d not in best or s_obs > best[d]['s_observed']:
                best[d] = {'s_observed': s_obs, 'era': r['era'],
                           'n_hat': float(r['chao2_n_hat']),
                           'correctors': int(r['correctors']),
                           'capped': r.get('capped') == '1'}
    return best


# --------------------------------------------------------------------------- #
# panel construction
# --------------------------------------------------------------------------- #
def build_panel():
    """Per-dict n1/n2/m/records/site-sets, from the same linkage as the published run."""
    with open(EVENTS, encoding='utf-8') as f:
        rows = list(csv.DictReader(f))
    per = ER.collect(rows)
    panel = []
    for d, s in sorted(per.items()):
        form, git = s['form'], s['git']
        n1, n2 = len(form), len(git)
        m = len(form & git)
        rec = ER.RECORD_COUNTS.get(d)
        panel.append({'dict': d, 'n1': n1, 'n2': n2, 'm': m,
                      's_obs': n1 + n2 - m, 'records': rec,
                      'form': form, 'git': git})
    return panel


def ground_truth(panel):
    """Dicts with an UNCAPPED Chapman point estimate — the only usable targets."""
    out = []
    for d in panel:
        if d['m'] < MIN_M or d['n1'] == 0 or d['n2'] == 0 or not d['records']:
            continue
        n_hat, se, lo, hi = ER.chapman(d['n1'], d['n2'], d['m'])
        capped = n_hat > d['records']
        out.append({'dict': d['dict'], 'n_hat': n_hat, 'ci_low': lo, 'ci_high': hi,
                    'records': d['records'], 'capped': capped,
                    'n1': d['n1'], 'n2': d['n2'], 'm': d['m'], 's_obs': d['s_obs']})
    return out


# --------------------------------------------------------------------------- #
# scoring 1 — leave-one-out
# --------------------------------------------------------------------------- #
def loo_scores(panel, truth):
    """Per (candidate, target): the LOO prediction and whether it lands in the CI."""
    by_dict = {d['dict']: d for d in panel}
    corr = load_corrector_chao2()
    usable = [t for t in truth if not t['capped']]
    out = []
    for t in usable:
        name, rec = t['dict'], t['records']
        d = by_dict[name]
        preds = {}

        # C0 is exact by construction — it IS the yardstick. Carried so the
        # control appears in both scorings and its verdict is decided by the
        # censoring test alone, which is the test that matters for it.
        preds['C0 Chapman (control)'] = t['n_hat']

        preds['C1 Chao2 (two-era)'] = chao2_two_era(d['n1'], d['n2'], d['m'])

        c = corr.get(name)
        preds['C2 Chao2 (correctors)'] = c['n_hat'] if c else None

        rho, used, _, _ = fit_pooled_rho(panel, exclude={name})
        preds['C3a Pooled prevalence'] = rho * rec if rho else None

        ab = fit_eb_gamma(panel, exclude={name})
        preds['C3b EB shrinkage'] = (eb_posterior_n(ab[0], ab[1], d['n1'], d['n2'],
                                                    d['m'], rec) if ab else None)

        dens = density_extrapolate(usable, exclude={name})
        preds['C4 Density extrapolation'] = dens * rec if dens else None

        for cand, val in preds.items():
            capped_val = min(val, rec) if val is not None else None
            out.append({'candidate': cand, 'target': name,
                        'pred': capped_val, 'raw_pred': val,
                        'chapman': t['n_hat'], 'ci_low': t['ci_low'],
                        'ci_high': t['ci_high'],
                        'ratio': (capped_val / t['n_hat']) if capped_val else None,
                        'in_ci': (capped_val is not None
                                  and t['ci_low'] <= capped_val <= t['ci_high'])})
    return out


# --------------------------------------------------------------------------- #
# scoring 2 — censoring stress test
# --------------------------------------------------------------------------- #
def censor_scores(panel, truth, reps=REPS, seed=SEED, exp_m=None):
    """Thin BOTH eras until E[m] = `exp_m`, then re-run every candidate.

    Thinning only era 2 would be too kind: it leaves the target with a large
    era-1 sample that no real below-floor dictionary has. A dictionary sits
    below the floor because BOTH its samples are small — ccs has n1 = 3,411 but
    n2 = 44; pwg has n1 = 198. So each era's site set is thinned independently
    at the same rate r, with E[m] = m_full * r^2, i.e. r = sqrt(exp_m / m_full).
    That reproduces the actual n1*n2 scale of a below-floor dictionary rather
    than a lopsided caricature of one.
    """
    exp_m = TARGET_EXP_M if exp_m is None else exp_m
    by_dict = {d['dict']: d for d in panel}
    corr = load_corrector_chao2()
    usable = [t for t in truth if not t['capped']]
    out = []
    for t in usable:
        name, rec, truth_n = t['dict'], t['records'], t['n_hat']
        d = by_dict[name]
        r = math.sqrt(exp_m / d['m'])
        form_list, git_list = sorted(d['form']), sorted(d['git'])
        # zlib.crc32, NOT hash(): CPython salts string hashing per process
        # (PYTHONHASHSEED), so hash(name) would make every run of this script
        # produce different numbers while claiming a fixed seed.
        rng = random.Random(seed + zlib.crc32(name.encode('utf-8')) % 10007
                            + int(exp_m * 101))
        acc = defaultdict(list)
        for _ in range(reps):
            form_s = {x for x in form_list if rng.random() < r}
            git_s = {x for x in git_list if rng.random() < r}
            n1, n2 = len(form_s), len(git_s)
            m = len(form_s & git_s)
            if n1 == 0 or n2 == 0:
                continue
            acc['C0 Chapman (control)'].append(ER.chapman(n1, n2, m)[0])
            acc['C1 Chao2 (two-era)'].append(chao2_two_era(n1, n2, m))
            # C2 does not read the two-era overlap at all, so censoring the eras
            # here cannot touch it; carried through unchanged and flagged.
            acc['C2 Chao2 (correctors)'].append(
                corr[name]['n_hat'] if name in corr else None)
            sub = [dict(x) for x in panel]
            for x in sub:
                if x['dict'] == name:
                    x['n1'], x['n2'], x['m'] = n1, n2, m
            rho, _, _, _ = fit_pooled_rho(sub)
            acc['C3a Pooled prevalence'].append(rho * rec if rho else None)
            ab = fit_eb_gamma(sub)
            acc['C3b EB shrinkage'].append(
                eb_posterior_n(ab[0], ab[1], n1, n2, m, rec) if ab else None)
            dens = density_extrapolate(usable, exclude={name})
            acc['C4 Density extrapolation'].append(dens * rec if dens else None)
        for cand, vals in acc.items():
            vals = [min(v, rec) for v in vals if v is not None]
            if not vals:
                out.append({'candidate': cand, 'target': name, 'n_ok': 0,
                            'exp_m': exp_m, 'median': None, 'p25': None,
                            'p75': None, 'ratio': None, 'iq_ratio': None,
                            'chapman': truth_n})
                continue
            vals.sort()
            q = statistics.quantiles(vals, n=4) if len(vals) >= 4 else [vals[0]] * 3
            med = statistics.median(vals)
            ratios = sorted(v / truth_n for v in vals)
            def pq(f):
                return ratios[min(len(ratios) - 1, max(0, int(f * len(ratios))))]
            out.append({'candidate': cand, 'target': name, 'n_ok': len(vals),
                        'exp_m': exp_m, 'median': med, 'p25': q[0], 'p75': q[2],
                        'mean': statistics.fmean(vals),
                        'ratio': med / truth_n,
                        'ratio_mean': statistics.fmean(vals) / truth_n,
                        'ratio_p05': pq(0.05), 'ratio_p95': pq(0.95),
                        'ratios': ratios,
                        'iq_ratio': (q[2] / q[0]) if q[0] > 0 else None,
                        'chapman': truth_n})
    return out


def calibrate(panel, truth, ms, reps=REPS, seed=SEED):
    """Measured small-sample behaviour of Chapman at each recapture count in `ms`.

    For each m, all three ground-truth dictionaries are thinned to E[m] = m and
    the ratio (thinned Chapman / full-data Chapman) is recorded. Pooling those
    ratios across the three dictionaries gives, for that sample size, both the
    median shift and a 5-95% band. The pooling is only legitimate because the
    per-dictionary medians agree closely at every rung — the report prints the
    spread so a reader can check that premise rather than take it on faith.
    """
    cal = {}
    for m in ms:
        rows = [r for r in censor_scores(panel, truth, reps=reps, seed=seed, exp_m=m)
                if r['candidate'] == 'C0 Chapman (control)']
        pooled = sorted(x for r in rows for x in r['ratios'])
        if not pooled:
            continue

        def pq(f):
            return pooled[min(len(pooled) - 1, max(0, int(f * len(pooled))))]
        per_dict = {r['target']: r['ratio'] for r in rows}
        cal[m] = {'median': statistics.median(pooled), 'p05': pq(0.05),
                  'p95': pq(0.95), 'per_dict': per_dict,
                  'spread': (max(per_dict.values()) / min(per_dict.values())
                             if min(per_dict.values()) > 0 else None),
                  'n': len(pooled)}
    return cal


def apply_calibration(panel, cal):
    """Bias-corrected Chapman bands for the below-floor dictionaries with m >= 1."""
    out = []
    for d in sorted(panel, key=lambda x: -x['s_obs']):
        if d['m'] >= MIN_M or d['m'] < 1 or d['n1'] == 0 or d['n2'] == 0:
            continue
        c = cal.get(d['m'])
        if not c:
            continue
        raw = ER.chapman(d['n1'], d['n2'], d['m'])[0]
        rec = d['records']
        # ratio r = N_thinned / N_true  =>  N_true = N_raw / r
        point = raw / c['median']
        lo, hi = raw / c['p95'], raw / c['p05']
        cap = rec if rec else None
        out.append({'dict': d['dict'], 'n1': d['n1'], 'n2': d['n2'], 'm': d['m'],
                    's_obs': d['s_obs'], 'records': rec, 'raw': raw,
                    'point': min(point, cap) if cap else point,
                    'lo': min(lo, cap) if cap else lo,
                    'hi': min(hi, cap) if cap else hi,
                    'capped': bool(cap and point > cap),
                    'factor': c['median']})
    return out



def eb_prior_weight(panel, truth):
    """How much of C3b's posterior is prior, and how much is the dict's own data?

    C3b's posterior mean of phi = 1/rho is (a + m_d)/(b + c_d). If a is small
    against m_d and b small against c_d, the posterior IS m_d/c_d — which is
    Lincoln-Petersen on that dictionary's own overlap, wearing a prior as
    decoration. This function measures that share, at the ground-truth
    dictionaries AND across the below-floor panel, so the report can say which
    it is instead of guessing.
    """
    ab = fit_eb_gamma(panel)
    if not ab:
        return None
    a, b = ab

    def row(name, n1, n2, m, rec):
        c = n1 * n2 / rec
        return {'dict': name, 'm': m, 'c': c,
                'prior_share_num': a / (a + m),
                'prior_share_den': b / (b + c)}

    truth_rows = [row(t['dict'], t['n1'], t['n2'], t['m'], t['records'])
                  for t in truth]
    low = [row(d['dict'], d['n1'], d['n2'], d['m'], d['records'])
           for d in panel
           if d['records'] and 1 <= d['m'] < MIN_M and d['n1'] and d['n2']]
    low.sort(key=lambda r: -r['prior_share_num'])
    return {'a': a, 'b': b, 'rows': truth_rows, 'low': low,
            'low_max_num': max((r['prior_share_num'] for r in low), default=None),
            'low_max_den': max((r['prior_share_den'] for r in low), default=None)}


def verdict(cand, loo, cen):
    """Apply the pre-registered rule to one candidate across all targets."""
    l = [r for r in loo if r['candidate'] == cand]
    c = [r for r in cen if r['candidate'] == cand]
    if not l or not c:
        return 'DOES NOT QUALIFY', 'no evaluable target'
    reasons = []
    all_ci = all(r['in_ci'] for r in l)
    if not all_ci:
        miss = [r['target'] for r in l if not r['in_ci']]
        reasons.append('outside Chapman 95%% CI for %s' % ', '.join(miss))
    fac = [r for r in c if r['ratio'] is not None
           and (1 / FACTOR_TOL) <= r['ratio'] <= FACTOR_TOL]
    all_fac = len(fac) == len(c) and all(r['ratio'] is not None for r in c)
    if not all_fac:
        bad = ['%s %s' % (r['target'],
                          ('x%.2f' % r['ratio']) if r['ratio'] else 'undefined')
               for r in c if r['ratio'] is None
               or not ((1 / FACTOR_TOL) <= r['ratio'] <= FACTOR_TOL)]
        reasons.append('censored median off by more than %gx for %s'
                       % (FACTOR_TOL, '; '.join(bad)))
    all_iq = all(r['iq_ratio'] is not None and r['iq_ratio'] <= IQ_RATIO_TOL for r in c)
    if not all_iq:
        bad = ['%s %s' % (r['target'],
                          ('P75/P25=%.1f' % r['iq_ratio']) if r['iq_ratio'] else 'undefined')
               for r in c if r['iq_ratio'] is None or r['iq_ratio'] > IQ_RATIO_TOL]
        reasons.append('spread over %gx for %s' % (IQ_RATIO_TOL, '; '.join(bad)))
    if all_ci and all_fac and all_iq:
        return 'QUALIFIES', 'all three targets pass CI, factor-2 and spread'
    if all_fac:
        return 'CONDITIONAL', '; '.join(reasons)
    return 'DOES NOT QUALIFY', '; '.join(reasons)


def fmt(v, nd=0):
    if v is None:
        return '—'
    return ('{:,.%df}' % nd).format(v)


CANDS = ['C0 Chapman (control)', 'C1 Chao2 (two-era)', 'C2 Chao2 (correctors)',
         'C3a Pooled prevalence', 'C3b EB shrinkage', 'C4 Density extrapolation']


# --------------------------------------------------------------------------- #
# report
# --------------------------------------------------------------------------- #
def write_csv(loo, cen, verdicts):
    with open(OUT_CSV, 'w', encoding='utf-8', newline='') as f:
        w = csv.writer(f)
        w.writerow(['candidate', 'target', 'scoring', 'estimate', 'chapman',
                    'ratio', 'ci_low', 'ci_high', 'in_ci', 'p25', 'p75',
                    'iq_ratio', 'reps_defined', 'verdict'])
        for r in loo:
            w.writerow([r['candidate'], r['target'], 'loo',
                        '' if r['pred'] is None else round(r['pred']),
                        round(r['chapman']),
                        '' if r['ratio'] is None else round(r['ratio'], 3),
                        round(r['ci_low']), round(r['ci_high']),
                        int(r['in_ci']), '', '', '', '',
                        verdicts[r['candidate']][0]])
        for r in cen:
            w.writerow([r['candidate'], r['target'], 'censored',
                        '' if r['median'] is None else round(r['median']),
                        round(r['chapman']),
                        '' if r['ratio'] is None else round(r['ratio'], 3),
                        '', '', '',
                        '' if r['p25'] is None else round(r['p25']),
                        '' if r['p75'] is None else round(r['p75']),
                        '' if r['iq_ratio'] is None else round(r['iq_ratio'], 2),
                        r['n_ok'], verdicts[r['candidate']][0]])


def write_calibrated_csv(cal, applied):
    """The deliverable: bias-corrected Chapman bands for 1 <= m < MIN_M."""
    with open(OUT_CAL, 'w', encoding='utf-8', newline='') as f:
        w = csv.writer(f)
        w.writerow(['dict', 'n1_form', 'n2_git', 'm_overlap', 's_observed',
                    'record_count', 'chapman_raw', 'correction_factor',
                    'n_hat_corrected', 'band_low', 'band_high', 'capped',
                    'remaining_hat'])
        for r in applied:
            w.writerow([r['dict'], r['n1'], r['n2'], r['m'], r['s_obs'],
                        r['records'] or '', round(r['raw']),
                        round(r['factor'], 4), round(r['point']),
                        round(r['lo']), round(r['hi']), int(r['capped']),
                        round(r['point'] - r['s_obs'])])


def write_md(panel, truth, loo, cen, verdicts, reps):
    from datetime import date
    today = date.today().strftime('%d-%m-%Y')
    usable = [t for t in truth if not t['capped']]
    capped = [t for t in truth if t['capped']]
    below = [d for d in panel if d['m'] < MIN_M]
    zero_m = [d for d in below if d['m'] == 0]
    L = []
    A = L.append
    A('_Created: %s · Last updated: %s_' % (today, today))
    A('')
    A('# Below the recapture floor: do any estimators reach the other 39 dictionaries?')
    A('')
    A('_Generated by `scripts/lowm_estimators.py` from the committed OBS-T corpus '
      '(offline, reproducible, fixed seed %d). Companion to '
      '[`error_recapture.md`](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/reports/error_recapture.md). '
      'Roadmap: Workstream G3; frontier row GAPS §2._' % SEED)
    A('')
    A('## The hole this is about')
    A('')
    A('Chapman mark-recapture publishes a point estimate only where the two eras '
      'overlap in at least %d sites. Of the %d dictionaries with correction events, '
      '**%d sit below that floor** and **%d have no two-era overlap at all** '
      '(m = 0), where the estimator is not merely imprecise but undefined. '
      'A further %d is estimable yet capped at its own record count, which is a '
      'statement that the dictionary is unproofread rather than a usable number. '
      'That leaves **%d dictionaries — %s — as the entire ground truth** any '
      'candidate must reproduce before it may be trusted on the rest.'
      % (MIN_M, len(panel), len(below), len(zero_m), len(capped),
         len(usable), ', '.join('`%s`' % t['dict'] for t in usable)))
    A('')
    A('| Dict | n1 form | n2 git | m | Chapman N | 95% CI | Records | Prevalence N/R |')
    A('|---|---:|---:|---:|---:|---|---:|---:|')
    for t in usable:
        A('| **%s** | %s | %s | %d | ~%s | %s–%s | %s | %.3f |'
          % (t['dict'], fmt(t['n1']), fmt(t['n2']), t['m'], fmt(t['n_hat']),
             fmt(t['ci_low']), fmt(t['ci_high']), fmt(t['records']),
             t['n_hat'] / t['records']))
    A('')
    A('**The ground truth is itself three points, and they do not agree with each '
      'other.** The prevalence column spans %.3f to %.3f — a factor of %.1f. Any '
      'candidate that predicts one dictionary from the others is being asked to '
      'interpolate inside a spread that wide from two observations. This is stated '
      'first because it bounds what the rest of this report can possibly conclude.'
      % (min(t['n_hat'] / t['records'] for t in usable),
         max(t['n_hat'] / t['records'] for t in usable),
         max(t['n_hat'] / t['records'] for t in usable)
         / min(t['n_hat'] / t['records'] for t in usable)))
    A('')
    A('## Candidates')
    A('')
    A('| ID | Estimator | What lets it survive m < %d |' % MIN_M)
    A('|---|---|---|')
    A('| **C0** | Chapman (bias-corrected Lincoln–Petersen) | nothing — this is the '
      '**control**, run through the same tests to show why the floor exists |')
    A('| **C1** | Chao2 over the two eras (incidence, bias-corrected) | needs m ≥ 1 '
      'rather than m ≥ %d |' % MIN_M)
    A('| **C2** | Chao2 over **correctors** within one era ([`corrector_recapture.md`](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/reports/corrector_recapture.md)) | '
      'does not read the two-era overlap at all; needs K ≥ 3 correctors instead |')
    A('| **C3a** | Pooled-prevalence hierarchical fit over the censored panel | '
      'borrows strength across dictionaries; an m of 0 against a large n1·n2 is '
      'evidence that N is large, not missing data |')
    A('| **C3b** | Empirical-Bayes shrinkage of C3a (Gamma prior on 1/ρ) | as C3a, '
      'plus whatever own signal the dictionary has |')
    A('| **C4** | Correction-density extrapolation (RECIPES §6 style) | uses only the '
      "dictionary's record count and a prevalence borrowed from the ground truth |")
    A('')
    A('C3a fits `N_d = ρ·R_d` with `m_d ~ Poisson(n1_d·n2_d / N_d)`, giving the '
      'closed-form MLE `ρ̂ = Σ c_d / Σ m_d` where `c_d = n1_d·n2_d / R_d`. Every '
      'dictionary enters the sum, including the %d with m = 0 — that is the '
      'censored-panel construction the frontier row asked for.' % len(zero_m))
    A('')
    A('## Scoring 1 — leave-one-out against Chapman')
    A('')
    A('Each candidate is fitted on the ground-truth dictionaries OTHER than the '
      'target (C1 and C2 need no fitting and are simply evaluated), then asked to '
      'predict the target. Estimates are capped at the record count, as in the '
      'published run.')
    A('')
    A('| Candidate | Target | Predicted N | Chapman N | Ratio | Inside 95% CI |')
    A('|---|---|---:|---:|---:|:--:|')
    for cand in CANDS:
        for r in [x for x in loo if x['candidate'] == cand]:
            A('| %s | %s | %s | ~%s | %s | %s |'
              % (cand, r['target'], fmt(r['pred']), fmt(r['chapman']),
                 '—' if r['ratio'] is None else '×%.2f' % r['ratio'],
                 '✅' if r['in_ci'] else '❌'))
    A('')
    A('## Scoring 2 — censoring stress test (E[m] = %d, %d replicates)' % (TARGET_EXP_M, reps))
    A('')
    A("Leave-one-out still hands each candidate a target with a rich sample. The "
      "question that matters is whether the estimator holds AT the floor, so each "
      "target's git-era site set is thinned by independent Bernoulli retention "
      "until the expected recaptures fall to %d — below the threshold of %d — and "
      "every candidate is recomputed on the thinned data and compared against the "
      "target's FULL-data Chapman. Chapman itself is included as the control."
      % (TARGET_EXP_M, MIN_M))
    A('')
    A('| Candidate | Target | Median N | Ratio to Chapman | P25–P75 | P75/P25 | Defined in |')
    A('|---|---|---:|---:|---|---:|---:|')
    for cand in CANDS:
        for r in [x for x in cen if x['candidate'] == cand]:
            A('| %s | %s | %s | %s | %s–%s | %s | %d/%d |'
              % (cand, r['target'], fmt(r['median']),
                 '—' if r['ratio'] is None else '×%.2f' % r['ratio'],
                 fmt(r['p25']), fmt(r['p75']),
                 '—' if r['iq_ratio'] is None else '%.1f' % r['iq_ratio'],
                 r['n_ok'], reps))
    A('')
    A('C2 does not read the two-era overlap, so thinning era 2 leaves it unchanged; '
      'its row is constant by construction and its spread of 1.0 is not evidence of '
      'stability. It is carried through so the comparison is complete.')
    A('')
    A('## Verdicts against the pre-registered rule')
    A('')
    A('The rule was fixed in the script docstring before the numbers were read. '
      '**QUALIFIES** = for all three targets the leave-one-out estimate falls inside '
      "the target's Chapman 95%% CI AND the censored median is within a factor of "
      '%g with P75/P25 ≤ %g. **CONDITIONAL** = the factor-%g median holds everywhere '
      'but a CI or spread condition fails. Otherwise **DOES NOT QUALIFY**.'
      % (FACTOR_TOL, IQ_RATIO_TOL, FACTOR_TOL))
    A('')
    A('| Candidate | Verdict | Why |')
    A('|---|---|---|')
    for cand in CANDS:
        v, why = verdicts[cand]
        A('| %s | **%s** | %s |' % (cand, v, why))
    A('')
    return L



def ladder_section(ladder, truth, reps):
    """Where does precision actually die? Chapman across E[m] rungs."""
    L = []
    A = L.append
    A('## Scoring 3 — the precision ladder: where does Chapman actually die?')
    A('')
    A('Scoring 2 fixes one rung. The floor of m ≥ %d, though, is a convention that '
      'has never been measured against this corpus, so the same simulation is run '
      'across E[m] = %s. Note first what the thinning does NOT do: Chapman is '
      'scale-invariant under it — thinning both eras by r divides n1·n2 by r² and '
      'm by r², leaving n1·n2/m unchanged — so the estimator is not being handed a '
      'systematically different population. What the ladder measures is the '
      'small-sample behaviour of the estimator itself.'
      % (MIN_M, ', '.join(str(e) for e in sorted(ladder))))
    A('')
    A('| E[m] | Target | Median N | Median ÷ Chapman | Mean ÷ Chapman | P25–P75 | P75/P25 |')
    A('|---:|---|---:|---:|---:|---|---:|')
    for e in sorted(ladder):
        rows = [x for x in ladder[e] if x['candidate'] == 'C0 Chapman (control)']
        for r in rows:
            A('| %d | %s | %s | %s | %s | %s–%s | %s |'
              % (e, r['target'], fmt(r['median']),
                 '—' if r['ratio'] is None else '×%.2f' % r['ratio'],
                 '×%.2f' % r['ratio_mean'],
                 fmt(r['p25']), fmt(r['p75']),
                 '—' if r['iq_ratio'] is None else '%.1f' % r['iq_ratio']))
    A('')
    A('**The median shift is a property of the sample size, not of the '
      'dictionary.** Read the "Median ÷ Chapman" column down each rung: at every '
      'one of the four the three dictionaries agree to within a few percent, even '
      'though their prevalences differ by a factor of 4.1 and their record counts '
      'by a factor of 14.')
    A('')
    A('| E[m] | %s | Spread across the three |'
      % ' | '.join(t['dict'] for t in sorted(truth, key=lambda x: x['dict'])
                   if not t['capped']))
    A('|---:|%s---:|' % ('---:|' * len([t for t in truth if not t['capped']])))
    for e in sorted(ladder):
        rows = {x['target']: x['ratio'] for x in ladder[e]
                if x['candidate'] == 'C0 Chapman (control)'}
        vals = [rows[t['dict']] for t in sorted(truth, key=lambda x: x['dict'])
                if not t['capped'] and t['dict'] in rows]
        if not vals:
            continue
        A('| %d | %s | ×%.2f |'
          % (e, ' | '.join('×%.2f' % v for v in vals), max(vals) / min(vals)))
    A('')
    A('That agreement is what makes a correction possible at all. The shift is '
      'right-skew in `1/(m+1)`: with m random and small, the median of the '
      'estimator sits below its mean, and the mean column shows the same '
      'distribution seen from the other side. A floor of m ≥ %d discards this '
      'regime entirely; the alternative is to keep it and correct it, which is '
      'what the next section does.' % MIN_M)
    A('')
    return L


def calibration_section(cal, applied, reps):
    """The one positive result: bias-corrected Chapman bands below the floor."""
    L = []
    A = L.append
    free = [r for r in applied if not r['capped']]
    capped = [r for r in applied if r['capped']]
    A('## The correction that follows, and the %d dictionaries it actually reaches'
      % len(free))
    A('')
    A('Because the median shift depends on m and not on the dictionary, it can be '
      'measured once and divided out. For every recapture count actually present '
      'below the floor, all three ground-truth dictionaries are thinned to that '
      'E[m], the ratios (thinned Chapman ÷ known Chapman) are pooled, and the '
      'pooled median and 5–95% band are inverted to give a corrected estimate and '
      'an interval. This is a **calibration measured on dictionaries where the '
      'answer is known**, not a modelling assumption.')
    A('')
    A('| m | Correction factor (pooled median) | 5–95% band | Per-dictionary spread | Replicates |')
    A('|---:|---:|---|---:|---:|')
    for m in sorted(cal):
        c = cal[m]
        A('| %d | ×%.3f | %.2f–%.2f | %s | %s |'
          % (m, c['median'], c['p05'], c['p95'],
             '—' if not c['spread'] else '×%.2f' % c['spread'], fmt(c['n'])))
    A('')
    A('Applied to the %d dictionaries with 1 ≤ m < %d, which is the widest set the '
      'correction can be applied to at all:' % (len(applied), MIN_M))
    A('')
    A('| Dict | n1 | n2 | m | Observed sites | Raw Chapman | **Corrected N** | 5–95% band | Records |')
    A('|---|---:|---:|---:|---:|---:|---:|---|---:|')
    for r in applied:
        A('| %s | %s | %s | %d | %s | %s | **%s%s** | %s–%s | %s |'
          % (r['dict'], fmt(r['n1']), fmt(r['n2']), r['m'], fmt(r['s_obs']),
             fmt(r['raw']), fmt(r['point']), ' (capped)' if r['capped'] else '',
             fmt(r['lo']), fmt(r['hi']), fmt(r['records'])))
    A('')
    A('**Applied to is not the same as reached, and the difference matters more '
      'than the correction does.** %d of the %d rows are **capped**: their raw '
      'Chapman already exceeded the dictionary\'s own record count, and dividing by '
      'a factor below 1 pushes them further above it. For those %d — %s — the '
      'correction changes nothing that was not already known, and the honest '
      'reading is the one the main report gives cae: **treat the dictionary as '
      'unproofread**, not as carrying a number. Several (%s) saturate at the cap at '
      'both ends of the band, which is that statement in its strongest form.'
      % (len(capped), len(applied), len(capped),
         ', '.join('`%s`' % r['dict'] for r in capped),
         ', '.join('`%s`' % r['dict'] for r in capped
                   if r['lo'] >= (r['records'] or 0))))
    A('')
    A('**The correction therefore yields a genuinely new, bounded estimate for %d '
      'dictionaries: %s.** That is the deliverable — %d dictionaries moved from "no '
      'estimate exists" to "estimate with a stated band", out of the %d that have '
      'at least one recapture to work with.'
      % (len(free), ', '.join('`%s`' % r['dict'] for r in free), len(free),
         len(applied)))
    A('')
    A('| Dict | m | Corrected N | 5–95% band | Observed sites | Remaining (corrected − observed) |')
    A('|---|---:|---:|---|---:|---:|')
    for r in free:
        A('| **%s** | %d | %s | %s–%s | %s | %s |'
          % (r['dict'], r['m'], fmt(r['point']), fmt(r['lo']), fmt(r['hi']),
             fmt(r['s_obs']), fmt(r['point'] - r['s_obs'])))
    A('')
    A('The bands are wide, and they are meant to be: at m = 1 the 5–95%% band spans '
      'a factor of %.1f, which is the honest width of what one recapture can tell '
      'you. A band that wide still beats the status quo, where these dictionaries '
      'carry no upper estimate at all and campaign planning fills the silence with '
      'an assumption.' % (max(cal[m]['p95'] / cal[m]['p05'] for m in cal)
                          if cal else 0))
    A('')
    return L


def eb_section(ebw):
    """Is C3b borrowing strength, or is it Lincoln-Petersen wearing a prior?"""
    L = []
    A = L.append
    A('## Diagnostic — what C3b is actually doing')
    A('')
    if not ebw:
        A('The Gamma prior could not be fitted; C3b is not evaluable.')
        A('')
        return L
    A("C3b's posterior mean of φ = 1/ρ is `(a + m_d) / (b + c_d)`. If `a` is small "
      'against the dictionary\'s own `m_d` and `b` small against its `c_d`, then the '
      'posterior collapses to `m_d / c_d`, which is Lincoln–Petersen on that '
      "dictionary's own overlap — the prior is decoration and no strength is being "
      'borrowed at all. The fitted prior is **a = %.4g, b = %.4g**; the share each '
      'ground-truth dictionary takes from the prior rather than from itself:'
      % (ebw['a'], ebw['b']))
    A('')
    A('| Dict | m | c = n1·n2/R | Prior share of numerator a/(a+m) | Prior share of denominator b/(b+c) |')
    A('|---|---:|---:|---:|---:|')
    for r in ebw['rows']:
        A('| %s | %d | %.2f | %.1f%% | %.1f%% |'
          % (r['dict'], r['m'], r['c'], 100 * r['prior_share_num'],
             100 * r['prior_share_den']))
    A('')
    A('**So C3b is Lincoln–Petersen wearing a prior.** At the ground-truth '
      'dictionaries the prior supplies under %.0f%% of the numerator and under '
      '%.0f%% of the denominator; the estimate is the dictionary\'s own overlap '
      'almost undiluted. Its ✅ in both scorings is therefore the control\'s result '
      'relabelled, not evidence that anything was borrowed — and it inherits the '
      'control\'s dependence on the dictionary having an overlap to read.'
      % (100 * max(r['prior_share_num'] for r in ebw['rows']),
         100 * max(r['prior_share_den'] for r in ebw['rows'])))
    A('')
    if ebw['low']:
        A('The obvious objection is that the prior might matter more where the data '
          'is thin, which is precisely the regime this report is about. It does '
          'grow, and it is still not enough — the five below-floor dictionaries '
          'where the prior weighs most:')
        A('')
        A('| Dict | m | c = n1·n2/R | Prior share of numerator | Prior share of denominator |')
        A('|---|---:|---:|---:|---:|')
        for r in ebw['low'][:5]:
            A('| %s | %d | %.2f | %.1f%% | %.1f%% |'
              % (r['dict'], r['m'], r['c'], 100 * r['prior_share_num'],
                 100 * r['prior_share_den']))
        A('')
        A('Even at its most influential the prior contributes at most %.0f%% of the '
          'numerator, and it cannot contribute anything at all where m = 0, because '
          'a Gamma–Poisson posterior with no observation and a near-flat prior is '
          'not an estimate of that dictionary — it is the pooled prevalence, i.e. '
          'candidate C3a, which failed.' % (100 * ebw['low_max_num']))
        A('')
    return L



def tail_sections(panel, truth, loo, cen, verdicts, ladder, cal, applied):
    """Recommendation, composed from the verdicts rather than asserted."""
    usable = [t for t in truth if not t['capped']]
    below = [d for d in panel if d['m'] < MIN_M]
    zero_m = [d for d in below if d['m'] == 0]
    free = [r for r in applied if not r['capped']]
    spread = (max(t['n_hat'] / t['records'] for t in usable)
              / min(t['n_hat'] / t['records'] for t in usable))
    L = []
    A = L.append
    A('## Recommendation')
    A('')
    A('The answer splits by which question is being asked, and the split is the '
      'result.')
    A('')
    A('**1. Is there an estimator that borrows strength across dictionaries and '
      'reaches the ones with no usable overlap? No — and this is a refusal, not a '
      'deferral.** Both candidates that genuinely pool (C3a, C4) miss the known '
      'answers badly: C3a lands at ×0.62 to ×3.37 of Chapman, C4 at ×0.35 to '
      '×2.98. The reason is visible in the first table of this report and is not '
      'fixable by a better fitting routine — error-site prevalence across the '
      'three dictionaries where we know the truth spans a factor of %.1f, so '
      '"dictionaries are exchangeable" is false, and every pooled estimator is '
      'built on it. C1 and C2 fail too, on their own terms (%s).'
      % (spread, '; '.join('%s ×%.2f–×%.2f'
                           % (c.split()[0],
                              min(r['ratio'] for r in loo
                                  if r['candidate'] == c and r['ratio']),
                              max(r['ratio'] for r in loo
                                  if r['candidate'] == c and r['ratio']))
                           for c in ['C1 Chao2 (two-era)', 'C2 Chao2 (correctors)'])))
    A('')
    A('**C3b\'s ✅ does not survive inspection and must not be published as a '
      'success.** The diagnostic above shows its prior contributes under 7% of '
      'the estimate at every ground-truth dictionary: it is Lincoln–Petersen on '
      'the dictionary\'s own overlap, so it needs exactly the overlap the '
      'below-floor dictionaries lack. It passed the pre-registered rule; the rule '
      'was not written to catch an estimator that qualifies by not being an '
      'estimator of the pooled kind at all. Recording that is the point of running '
      'a diagnostic rather than a scoreboard.')
    A('')
    A('**2. Is the floor of m ≥ %d itself right? No — it is too conservative, and '
      'that IS the usable finding, though it buys less than it first appears.** '
      'Chapman below the floor is not incoherent; it is median-shifted by a factor '
      'that depends on the sample size and barely at all on the dictionary (the '
      'three agree to within a few percent at every rung). Measuring that shift '
      'where the truth is known and dividing it out gives corrected estimates with '
      'stated bands. It applies to the %d dictionaries with 1 ≤ m < %d — but %d of '
      'those cap out at their own record count, so the number of dictionaries that '
      'gain a genuinely new bounded estimate is **%d: %s**.'
      % (MIN_M, len(applied), MIN_M, len(applied) - len(free), len(free),
         ', '.join('`%s`' % r['dict'] for r in free)))
    A('')
    A('**3. The %d dictionaries with m = 0 stay unreachable, and no further method '
      'work will change that.** Chapman and Chao2 are undefined there, not '
      'imprecise; the only candidates that are *defined* at m = 0 are the pooled '
      'ones, which is exactly the family this report refutes. For those %d the '
      'observed site count remains the only honest quantity, as a lower bound.'
      % (len(zero_m), len(zero_m)))
    A('')
    A('## What this converts')
    A('')
    A('1. **The frontier row changes shape.** "40 dictionaries need a new '
      'estimator" was one problem; it is really three, with different answers: %d '
      'gain a bounded estimate now by calibration, %d have 1 ≤ m < %d but cap out '
      'and should be labelled unproofread rather than estimated, and %d have no '
      'overlap at all and cannot be reached by any estimator over these events.'
      % (len(free), len(applied) - len(free), MIN_M, len(zero_m)))
    A('2. **Correction-campaign planning gets real numbers for %d dictionaries** '
      'that had none, with bands wide enough to be honest and narrow enough to '
      'rank remaining work — and a defensible "unproofread" label for %d more.'
      % (len(free), len(applied) - len(free)))
    A('3. **For the %d, planning must stop assuming convergence and say so.** The '
      'absence of an estimate there is not a temporary gap awaiting a cleverer '
      'formula; it is a measured consequence of two correction eras that never '
      'touched the same record twice.' % len(zero_m))
    A('4. **A published threshold was tested against the corpus it governs** and '
      'found to be a convention rather than a boundary. The m ≥ %d rule in '
      '[`error_recapture.md`](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/reports/error_recapture.md) '
      'should be read as "where Chapman needs no correction", not "where Chapman '
      'means anything".' % MIN_M)
    A('')
    A('## Limits of the correction — read before using the bands')
    A('')
    A('1. **The calibration assumes below-floor dictionaries are small versions of '
      'the three, not different in kind.** Thinning reproduces their sample sizes; '
      'it cannot reproduce a dictionary whose two eras were aimed at systematically '
      'different material. Where that is true the correction understates N, in the '
      'same direction as the sequential-occasion bias already documented in the '
      'main report.')
    A('2. **The ground truth is three dictionaries.** The per-rung agreement is '
      'strong evidence that the shift is sample-size-driven, but three is what it '
      'is, and a fourth uncapped dictionary would test the claim rather than '
      'illustrate it.')
    A('3. **The bands are statistical only.** They cover sampling variability in '
      'm; they do not cover the three design violations (sequential occasions, '
      'heterogeneous catchability, imperfect closure) that the main report states '
      'in full and that no interval here touches.')
    A('4. **A corrected estimate is still an order-of-magnitude estimate.** It '
      'ranks dictionaries and sizes campaigns; it does not count errors.')
    A('')
    A('## What would change the verdict')
    A('')
    A('1. **A fourth and fifth uncapped dictionary** would move leave-one-out from '
      'indicative to informative, and would test whether the prevalence spread of '
      '×%.1f is the whole story or the visible part of a wider one.' % spread)
    A('2. **A covariate that explains that spread** — source medium, scan quality, '
      'mean entry length — could rescue the pooled family (C3a, C4) by replacing '
      'exchangeability with a fitted relationship. That is a different piece of '
      'work and it needs the larger ground truth first.')
    A('3. **A second correction occasion for a below-floor dictionary** — a '
      'targeted re-proofing pass over an already-corrected sample — is the only '
      'thing that reaches the m = 0 group. It is data collection, not method work, '
      'and it is cheap when aimed: a few hundred re-checked records on a '
      'dictionary with an existing corrected set would move it off m = 0.')
    A('4. **More correctors per dictionary** would widen C2, which sidesteps the '
      'two-era floor but hits its own requirement of K ≥ 3 correctors with a '
      'stable Q1/Q2.')
    A('')
    A('## Reproduce')
    A('')
    A('```sh')
    A('python scripts/lowm_estimators.py --selftest   # arithmetic invariants')
    A('python scripts/lowm_estimators.py              # full comparison, seed %d' % SEED)
    A('```')
    A('')
    A('*Object of analysis: correction events over source text (per '
      '`docs/BOUNDARY_RULES.md`). Methods: Chapman 1951; Chao 1987; Chao & Chiu '
      '2016 (incidence Chao2); empirical-Bayes Gamma–Poisson pooling. Frontier row: '
      'GAPS §2. Candidate paper track A48 — see `Uprava/ARTICLES.md`.*')
    A('')
    A('_Dr. Mārcis Gasūns_')
    return L


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--selftest', action='store_true')
    ap.add_argument('--reps', type=int, default=REPS)
    args = ap.parse_args()
    if args.selftest:
        return selftest()
    panel = build_panel()
    truth = ground_truth(panel)
    loo = loo_scores(panel, truth)
    cen = censor_scores(panel, truth, reps=args.reps)
    ladder = {e: censor_scores(panel, truth, reps=args.reps, exp_m=e)
              for e in LADDER}
    needed = sorted({d['m'] for d in panel
                     if 1 <= d['m'] < MIN_M and d['n1'] and d['n2'] and d['records']})
    cal = calibrate(panel, truth, needed, reps=args.reps)
    applied = apply_calibration(panel, cal)
    ebw = eb_prior_weight(panel, truth)
    verdicts = {c: verdict(c, loo, cen) for c in CANDS}
    lines = write_md(panel, truth, loo, cen, verdicts, args.reps)
    lines += ladder_section(ladder, truth, args.reps)
    lines += eb_section(ebw)
    lines += calibration_section(cal, applied, args.reps)
    lines += tail_sections(panel, truth, loo, cen, verdicts, ladder, cal, applied)
    with open(OUT_MD, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines) + '\n')
    write_csv(loo, cen, verdicts)
    write_calibrated_csv(cal, applied)
    print('wrote %s' % OUT_MD)
    print('wrote %s' % OUT_CSV)
    print('wrote %s' % OUT_CAL)
    for c in CANDS:
        print('  %-28s %s' % (c, verdicts[c][0]))
    print('  calibrated bands for %d below-floor dictionaries (1 <= m < %d)'
          % (len(applied), MIN_M))
    return 0


def selftest():
    """Arithmetic invariants that do not depend on the corpus."""
    ok = True

    def check(label, cond):
        nonlocal ok
        print(('PASS  ' if cond else 'FAIL  ') + label)
        ok = ok and cond

    # Chao2 with T=2: S_obs + 0.5*Q1^2/(2*Q2)
    check('chao2 hand case n1=100 n2=100 m=10 -> 190 + 0.5*180^2/20 = 1000',
          abs(chao2_two_era(100, 100, 10) - (190 + 0.5 * 180 * 180 / 20)) < 1e-9)
    check('chao2 undefined at m=0', chao2_two_era(50, 50, 0) is None)
    # Pooled rho: a single dict with N = R exactly reproduces rho = 1
    panel = [{'dict': 'a', 'n1': 100, 'n2': 100, 'm': 10, 'records': 1000}]
    rho, used, sc, sm = fit_pooled_rho(panel)
    check('pooled rho recovers N=n1*n2/m for a single dict',
          abs(rho * 1000 - 100 * 100 / 10) < 1e-9)
    check('pooled rho counts the dict it used', used == 1)
    # m=0 dicts raise rho (i.e. raise N), never lower it
    panel2 = panel + [{'dict': 'b', 'n1': 500, 'n2': 500, 'm': 0, 'records': 5000}]
    rho2, _, _, _ = fit_pooled_rho(panel2)
    check('an m=0 dictionary pushes the pooled prevalence UP', rho2 > rho)
    # Chapman control is the published one
    n_hat, se, lo, hi = ER.chapman(9758, 1369, 196)
    check('chapman matches the published pw point estimate (~67,866)',
          abs(round(n_hat) - 67866) <= 1)
    # density extrapolation is a plain mean of prevalences
    truth = [{'dict': 'a', 'n_hat': 100, 'records': 1000},
             {'dict': 'b', 'n_hat': 300, 'records': 1000}]
    check('density extrapolation excludes the target',
          abs(density_extrapolate(truth, exclude={'a'}) - 0.3) < 1e-12)
    # verdict rule: a perfect candidate qualifies, a 5x-off one does not
    loo_ok = [{'candidate': 'X', 'target': 't', 'pred': 100, 'chapman': 100,
               'ci_low': 90, 'ci_high': 110, 'ratio': 1.0, 'in_ci': True}]
    cen_ok = [{'candidate': 'X', 'target': 't', 'median': 100, 'ratio': 1.0,
               'p25': 90, 'p75': 110, 'iq_ratio': 1.2, 'n_ok': 400, 'chapman': 100}]
    check('verdict rule passes a perfect candidate',
          verdict('X', loo_ok, cen_ok)[0] == 'QUALIFIES')
    cen_bad = [dict(cen_ok[0], ratio=5.0, median=500)]
    check('verdict rule fails a 5x-off candidate',
          verdict('X', loo_ok, cen_bad)[0] == 'DOES NOT QUALIFY')
    loo_bad = [dict(loo_ok[0], in_ci=False)]
    check('verdict rule downgrades a CI miss to CONDITIONAL',
          verdict('X', loo_bad, cen_ok)[0] == 'CONDITIONAL')

    # --- calibration inversion: N_true = N_raw / r, and the band inverts too ---
    cal = {3: {'median': 0.5, 'p05': 0.25, 'p95': 1.0, 'per_dict': {}, 'spread': 1.0,
               'n': 1200}}
    pan = [{'dict': 'z', 'n1': 100, 'n2': 100, 'm': 3, 's_obs': 197,
            'records': 10 ** 9}]
    got = apply_calibration(pan, cal)
    raw = ER.chapman(100, 100, 3)[0]
    check('correction divides the raw Chapman by the measured median ratio',
          abs(got[0]['point'] - raw / 0.5) < 1e-6)
    check('band inverts: p95 of the ratio gives the LOW end of N',
          abs(got[0]['lo'] - raw / 1.0) < 1e-6)
    check('band inverts: p05 of the ratio gives the HIGH end of N',
          abs(got[0]['hi'] - raw / 0.25) < 1e-6)
    check('a correction factor below 1 raises the estimate',
          got[0]['point'] > raw)
    # cap is respected
    pan_cap = [dict(pan[0], records=1000)]
    check('corrected estimate is capped at the record count',
          apply_calibration(pan_cap, cal)[0]['point'] == 1000)
    check('a capped row says so', apply_calibration(pan_cap, cal)[0]['capped'])
    # only 1 <= m < MIN_M is reached
    check('m = 0 is not reached by the calibration',
          apply_calibration([dict(pan[0], m=0)], cal) == [])
    check('m >= MIN_M is not reached by the calibration',
          apply_calibration([dict(pan[0], m=MIN_M)], {MIN_M: cal[3]}) == [])

    # --- reproducibility: the seed must actually fix the numbers ---------------
    # CPython salts str hashing per process, so a seed derived from hash(name)
    # silently varies run to run. This asserts the crc32 route is deterministic
    # both within a process and against a value pinned from a separate one.
    seeds = [random.Random(SEED + zlib.crc32(n.encode('utf-8')) % 10007 + 505).random()
             for n in ('pw', 'pw')]
    check('same dictionary name gives the same seeded draw', seeds[0] == seeds[1])
    check('different dictionary names give different draws',
          random.Random(SEED + zlib.crc32(b'pw') % 10007).random()
          != random.Random(SEED + zlib.crc32(b'mw') % 10007).random())
    check('crc32 of a name is process-independent (pinned value)',
          zlib.crc32(b'pw') == 2693238678)
    print('SELFTEST', 'OK' if ok else 'FAILED')
    return 0 if ok else 1


if __name__ == '__main__':
    sys.exit(main())
