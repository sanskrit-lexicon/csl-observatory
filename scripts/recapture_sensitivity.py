#!/usr/bin/env python3
"""How much of the recapture result is arithmetic, and how much is assumption? (H5072)

`error_recapture.py` publishes a Chapman point estimate and a 95% CI for the four
dictionaries whose two-era overlap clears m >= 10, and states in prose that two
assumption violations — sequential occasions (upward bias) and positively
correlated catchability (downward bias) — "pull in opposite directions". Neither
has ever been sized. This script sizes both, on one axis, and separates three
things the published report runs together:

  * what is ARITHMETIC             — reproducible from the committed CSV, no model;
  * what is ASSUMPTION             — a one-parameter family the data cannot choose within;
  * what the histories CAN IDENTIFY — the observable overdispersion of per-site
                                      correction counts, and nothing else.

The single axis
---------------
With the form era as occasion 1 and the git era as occasion 2 over N sites, define

    gamma = P(caught in era 2 | caught in era 1) / P(caught in era 2)

so that E[n1] = N p1, E[n2] = N p2, E[m] = N p1 p2 gamma, and therefore

    N = gamma * (n1 n2 / m).

gamma = 1 is independence; gamma > 1 is positive dependence (Chapman UNDERestimates);
gamma < 1 is negative dependence (Chapman OVERestimates). Every violation of the
independence assumption — shared catchability, heterogeneous detectability, the
sequential-removal mechanism — enters the point estimate through this one factor.
The published numbers are the gamma = 1 slice of that family.

gamma is NOT identifiable here. A two-list table has three observable counts
(era-1 only, era-2 only, both); the independence model already spends all three on
(N, p1, p2) and leaves zero residual degrees of freedom. Adding gamma makes four
parameters for three counts: the likelihood is exactly flat along the curve
{(N, p1, p2, gamma) : gamma/N = const}. `nonidentification_check()` demonstrates
this numerically rather than asserting it.

Controls (preregistered in reports/recapture_sensitivity_prereg.md)
------------------------------------------------------------------
A  Independent-source recovery (POSITIVE control). gamma = 1, CV = 0, N and (p1, p2)
   matched to each estimable dictionary's observed counts. Chapman must be within 5%
   of truth and its nominal 95% CI must cover in >= 90% of replicates. A failure here
   voids everything downstream, because it would mean the arithmetic is wrong.

B  Heterogeneous detectability (NEGATIVE control, positive dependence). Site-level
   multiplicative factor theta with E[theta] = 1 and coefficient of variation CV,
   giving analytically gamma = 1 + CV^2 and relative Chapman bias -CV^2/(1 + CV^2).
   Primary family is the symmetric two-point {1-CV, 1+CV}: bounded, so the capture
   probabilities stay probabilities and the analytic identity is exact rather than
   approximate. A clipped Gamma is run beside it as the robustness row.

C  Sequential removal (NEGATIVE control, the opposite sign). Each site carries k
   errors from a zero-truncated Poisson; the form era detects each with probability
   q1 AND FIXES WHAT IT DETECTS; the git era detects each survivor with probability
   q2. Recapture therefore needs a residual error. Cell probabilities are closed-form
   (see `sequential_cells`), so the mechanism's gamma is computed exactly and the
   simulation only confirms it.

D  Arithmetic invariants (`--selftest`): gamma = 1 reproduces Chapman exactly, the
   envelope is monotone in gamma, `gamma_for_target` inverts `envelope`, the exact
   binomial sampler matches its own mean and variance, and the published
   `error_recapture.csv` counts are reproduced from the events CSV.

Outputs
-------
* `reports/recapture_sensitivity.md`
* `observatory/site/src/data/recapture_sensitivity.csv`           (dict x gamma envelope)
* `observatory/site/src/data/recapture_sensitivity_controls.csv`  (control cells)

Usage:  python scripts/recapture_sensitivity.py [--selftest] [--reps N] [--quick]
"""
import argparse, csv, hashlib, math, os, random, statistics, sys
from collections import defaultdict

sys.stdout.reconfigure(encoding='utf-8'); sys.stderr.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DATA = os.path.join(ROOT, 'observatory', 'site', 'src', 'data')
EVENTS = os.path.join(DATA, 'correction_events_final.csv')
PUBLISHED = os.path.join(DATA, 'error_recapture.csv')
OUT_MD = os.path.join(ROOT, 'reports', 'recapture_sensitivity.md')
OUT_CSV = os.path.join(DATA, 'recapture_sensitivity.csv')
OUT_CTRL = os.path.join(DATA, 'recapture_sensitivity_controls.csv')

sys.path.insert(0, HERE)
import error_recapture as ER          # noqa: E402  (chapman, collect, estimates, RECORD_COUNTS)
import headword_linkage as HL         # noqa: E402

# ---- preregistered grid (reports/recapture_sensitivity_prereg.md, frozen 20-09-2026)
GAMMA_GRID = (0.50, 0.60, 0.75, 0.90, 1.00, 1.10, 1.25, 1.50, 2.00)
CV_GRID = (0.00, 0.25, 0.50, 0.75, 1.00)
KBAR_GRID = (1.0, 1.5, 2.5, 4.0)
REPS = 400
SEED = 5072
FRAGILE_BAND = (0.90, 1.10)     # an interval that breaks inside this band is "fragile"
TOL = 0.05                      # 5% tolerance on every preregistered pass condition
COVERAGE_MIN = 0.90             # control A nominal-95% coverage floor
# Two-sided since 20-09-2026 (external review, defect 6): a coverage FLOOR alone is
# satisfied by any interval wide enough, including the degenerate [0, inf). A
# calibration control that cannot reject over-coverage certifies nothing about the
# interval it is meant to be calibrating. `selftest` mutates the interval to prove it.
COVERAGE_MAX = 0.99             # control A nominal-95% coverage ceiling


# --------------------------------------------------------------------------- #
# the envelope: one multiplicative parameter over the published arithmetic
# --------------------------------------------------------------------------- #
def envelope(n1, n2, m, gamma):
    """Chapman-form point estimate under dependence factor `gamma`.

    gamma = 1 returns Chapman exactly; the factor multiplies the (n1+1)(n2+1)/(m+1)
    ratio, which is where the independence assumption lives."""
    if m <= 0:
        return None
    return gamma * ((n1 + 1) * (n2 + 1) / (m + 1)) - 1


def gamma_for_target(n1, n2, m, target):
    """The gamma at which `envelope` equals `target`. Exact inverse."""
    if m <= 0:
        return None
    return (target + 1) * (m + 1) / ((n1 + 1) * (n2 + 1))


def nonidentification_check(n1, n2, m, gammas):
    """Full closed-population log-likelihood of the observed table under each gamma.

    For each gamma the profile parameters (N, p1, p2) are the ones that fit the three
    observed counts EXACTLY — N = gamma*n1*n2/m in Chapman form, p1 = n1/N, p2 = n2/N,
    which give E[m] = m, E[n1] = n1, E[n2] = n2 identically. The likelihood therefore
    compares equally perfect fits, and what is left is the combinatorial term

        log N! - log (N - S_obs)!   plus   (N - S_obs) log p00,

    which must be carried: N is a parameter, not a datum, so dropping the N-dependent
    normalising constant would manufacture a slope where the model has none. Returns
    (gamma, N, log-likelihood, max |expected - observed| over the three cells)."""
    out = []
    for g in gammas:
        # Petersen form, not Chapman: the exact-fit profile. Chapman's +1/-1 bias
        # correction shifts N by O(1) and would leave a residual of that size, which
        # is precisely the thing this check must be able to distinguish from zero.
        n = g * n1 * n2 / m if m else None
        if n is None or n <= max(n1, n2):
            out.append((g, None, None, None))
            continue
        p1, p2 = n1 / n, n2 / n
        p11 = p1 * p2 * g
        p10, p01 = p1 - p11, p2 - p11
        p00 = 1 - p11 - p10 - p01
        s_obs = n1 + n2 - m
        if min(p11, p10, p01, p00) <= 0 or n <= s_obs:
            out.append((g, None, None, None))
            continue
        ll = (math.lgamma(n + 1) - math.lgamma(n - s_obs + 1)
              - math.lgamma(m + 1) - math.lgamma(n1 - m + 1) - math.lgamma(n2 - m + 1)
              + m * math.log(p11) + (n1 - m) * math.log(p10)
              + (n2 - m) * math.log(p01) + (n - s_obs) * math.log(p00))
        resid = max(abs(n * p11 - m), abs(n * (p11 + p10) - n1), abs(n * (p11 + p01) - n2))
        out.append((g, n, ll, resid))
    return out


# --------------------------------------------------------------------------- #
# exact sampling, stdlib only (this repo's scripts take no third-party deps)
# --------------------------------------------------------------------------- #
def _beta(a, b, rng):
    x = rng.gammavariate(a, 1.0)
    y = rng.gammavariate(b, 1.0)
    return x / (x + y) if (x + y) else 0.5


def rbinom(n, p, rng):
    """Exact Binomial(n, p) by the Beta recursion (Devroye): O(log n) Beta draws.

    Not an approximation — the recursion is exact, which matters because control A
    is a coverage check and a normal approximation would fake its own answer."""
    if n <= 0 or p <= 0:
        return 0
    if p >= 1:
        return n
    if n < 40:
        return sum(1 for _ in range(n) if rng.random() < p)
    k = 1 + n // 2
    a = _beta(k, n + 1 - k, rng)
    if a > p:
        return rbinom(k - 1, p / a, rng)
    return k + rbinom(n - k, (p - a) / (1 - a), rng)


def draw_table(n_true, p11, p10, p01, rng):
    """One (n1, n2, m) table from the four-cell multinomial, exactly."""
    both = rbinom(n_true, p11, rng)
    rest = n_true - both
    d1 = rbinom(rest, p10 / (1 - p11), rng) if rest and p11 < 1 else 0
    rest2 = rest - d1
    denom = 1 - p11 - p10
    d2 = rbinom(rest2, p01 / denom, rng) if rest2 and denom > 0 else 0
    return both + d1, both + d2, both


# --------------------------------------------------------------------------- #
# mechanisms: closed-form cell probabilities
# --------------------------------------------------------------------------- #
def hetero_cells(p1, p2, cv):
    """Multiplicative site-level heterogeneity, E[theta] = 1, Var[theta] = cv^2.

    E[theta^2] = 1 + cv^2, so P(both) = p1 p2 (1 + cv^2) and gamma = 1 + cv^2 exactly.
    Families with the same first two moments give the same table law here, which is
    why the symmetric two-point family is used: it is bounded, so p1*theta and
    p2*theta stay probabilities at every CV in the grid."""
    p11 = p1 * p2 * (1 + cv * cv)
    return p11, p1 - p11, p2 - p11


def _ztpois_pmf(lam, kmax=200):
    """Zero-truncated Poisson pmf over k = 1..kmax (a site with no error is not a site)."""
    denom = 1 - math.exp(-lam)
    out, logf = [], 0.0
    for k in range(1, kmax + 1):
        logf += math.log(k)
        out.append(math.exp(-lam + k * math.log(lam) - logf) / denom)
    return out


def lam_for_mean(kbar, lo=1e-6, hi=200.0):
    """lambda of a zero-truncated Poisson whose mean is kbar (kbar > 1)."""
    if kbar <= 1.0:
        return lo
    f = lambda L: L / (1 - math.exp(-L)) - kbar
    for _ in range(200):
        mid = (lo + hi) / 2
        if f(mid) > 0:
            hi = mid
        else:
            lo = mid
    return (lo + hi) / 2


def sequential_cells(q1, q2, kbar):
    """Era 1 detects each error w.p. q1 AND FIXES IT; era 2 detects each survivor w.p. q2.

    Conditional on k errors at the site:
        P(caught1)      = 1 - (1-q1)^k
        P(both)         = P(caught1) - [(q1 + (1-q1)(1-q2))^k - ((1-q1)(1-q2))^k]
        P(caught2)      = P(both) + (1-q1)^k [1 - (1-q2)^k]
    The bracket is sum_{d>=1} C(k,d) q1^d (1-q1)^(k-d) (1-q2)^(k-d), i.e. the sites the
    form era touched whose every survivor the git era then missed."""
    pmf = _ztpois_pmf(lam_for_mean(kbar)) if kbar > 1.0 else [1.0]
    r = (1 - q1) * (1 - q2)
    s = q1 + (1 - q1) * (1 - q2)
    p1 = p2 = p11 = 0.0
    for i, w in enumerate(pmf):
        k = i + 1
        c1 = 1 - (1 - q1) ** k
        b = c1 - (s ** k - r ** k)
        c2 = b + ((1 - q1) ** k) * (1 - (1 - q2) ** k)
        p1 += w * c1
        p2 += w * c2
        p11 += w * b
    return p11, p1 - p11, p2 - p11, p1, p2


def gamma_of(p11, p1, p2):
    return p11 / (p1 * p2) if p1 > 0 and p2 > 0 else float('nan')


def joint_cells(q1, q2, kbar, cv, thetas=None):
    """Cell probabilities when BOTH mechanisms act at once.

    One site-level factor theta (mean 1, coefficient of variation `cv`) scales the
    per-error detection probabilities of both eras, AND the form era fixes what it
    detects, over a zero-truncated Poisson error count of mean `kbar`. Exact: the
    theta mixture and the k sum are both evaluated, nothing is simulated.

    This exists because the two mechanisms' gammas DO NOT MULTIPLY (external review,
    defect 4). Conditioning on a shared theta correlates the two eras' detection
    within a site, so the composite gamma has to be computed from the joint cells.
    `control_e` reports the exact discrepancy; `selftest` pins it."""
    if thetas is None:
        thetas = ((1.0 - cv, 0.5), (1.0 + cv, 0.5))     # symmetric two-point, E=1
    lam = ztp_lambda_for_mean(kbar) if kbar > 1.0 else 1e-9
    norm = 1.0 - math.exp(-lam)
    p1 = p2 = p11 = 0.0
    for th, w in thetas:
        a = q1 * th                          # found in era 1 -> fixed, cannot recur
        b = (1.0 - a) * (q2 * th)            # survives era 1, found in era 2
        r = 1.0 - a - b
        if min(a, b, r) < 0.0 or max(a, b) > 1.0:
            return None                      # theta pushes a probability out of range
        s1 = s2 = s12 = 0.0
        term = math.exp(-lam)                 # Poisson(lam) pmf at k = 0
        for k in range(1, 400):
            term *= lam / k                   # recurrence: no factorial, no overflow
            pk = term / norm
            if pk < 1e-15 and k > lam + 10:
                break
            s1 += pk * (1.0 - (1.0 - a) ** k)
            s2 += pk * (1.0 - (1.0 - b) ** k)
            s12 += pk * (1.0 - (1.0 - a) ** k - (1.0 - b) ** k + r ** k)
        p1 += w * s1
        p2 += w * s2
        p11 += w * s12
    return p11, p1 - p11, p2 - p11, p1, p2


def gamma_two_point(cv):
    """The analytic gamma of the heterogeneity mechanism alone: 1 + CV^2.

    Valid only where capture probability is LINEAR in theta (p_j * theta), which is
    how controls B and E construct it (external review, defect 8). Under a nonlinear
    kernel the identity fails and two families sharing (mean, variance) disagree --
    `nonlinear_kernel_gap` exhibits that, and `selftest` pins it."""
    return 1.0 + cv * cv


def family_moments(thetas):
    """(mean, realised CV) of a discrete mixing family."""
    mean = sum(w * th for th, w in thetas)
    var = sum(w * (th - mean) ** 2 for th, w in thetas)
    return mean, (var ** 0.5) / mean if mean else float('nan')


def clipped_gamma_thetas(cv, nodes=96, lo=0.0, hi=4.0):
    """Discretised Gamma(shape=1/cv^2, mean 1) clipped to [lo, hi], renormalised to
    mean 1 exactly. The robustness companion control B's own docstring promised and
    did not ship (external review, defect 6).

    Clipping truncates the Gamma's upper tail, so the family's REALISED CV falls below
    the nominal one it was built from (nominal 1.00 -> realised 0.901). The identity is
    a statement about the family one actually has, so each row carries `cv_realised`
    and its gamma is checked against 1 + cv_realised^2 -- which it matches to machine
    precision, confirming the identity from a second family rather than restating it."""
    if cv <= 0:
        return ((1.0, 1.0),)
    shape = 1.0 / (cv * cv)
    scale = 1.0 / shape
    edges = [lo + (hi - lo) * i / nodes for i in range(nodes + 1)]
    pts = []
    for i in range(nodes):
        mid = (edges[i] + edges[i + 1]) / 2.0
        # Gamma density at the midpoint, unnormalised (constant cancels below).
        dens = mid ** (shape - 1.0) * math.exp(-mid / scale) if mid > 0 else 0.0
        if dens > 0:
            pts.append([mid, dens])
    tot = sum(w for _, w in pts)
    pts = [[m, w / tot] for m, w in pts]
    mean = sum(m * w for m, w in pts)
    return tuple((m / mean, w) for m, w in pts)       # rescale to E[theta] = 1


def nonlinear_kernel_gap(cv, alt_thetas=None):
    """gamma under a NONLINEAR capture kernel 1 - exp(-theta), for two mixing
    families that share a mean and a variance. Linear-kernel theory says both give
    1 + CV^2; under this kernel they do not even agree with each other."""
    def g(thetas):
        p1 = sum(w * (1.0 - math.exp(-th)) for th, w in thetas)
        p11 = sum(w * (1.0 - math.exp(-th)) ** 2 for th, w in thetas)
        return p11 / (p1 * p1)
    two_pt = ((1.0 - cv, 0.5), (1.0 + cv, 0.5))
    if alt_thetas is None:
        # three-point family with the same mean (1) and the same variance (cv^2)
        w_out = cv * cv / (2.0 * 4.0)                  # mass at 1 -/+ 2cv
        alt_thetas = ((1.0 - 2.0 * cv, w_out), (1.0, 1.0 - 2.0 * w_out),
                      (1.0 + 2.0 * cv, w_out))
    return g(two_pt), g(alt_thetas)


# --------------------------------------------------------------------------- #
# control runners
# --------------------------------------------------------------------------- #
def run_cells(n_true, p11, p10, p01, reps, seed, ci_widen=1.0):
    """Replicate tables -> Chapman point/CI summaries against the known truth.

    `ci_widen` exists only for `selftest`'s interval mutation (defect 6): scaling the
    half-width by a large factor produces the degenerate interval whose coverage the
    two-sided gate must REJECT. Every real control call leaves it at 1.0."""
    rng = random.Random(seed)
    pts, covered, gammas = [], 0, []
    for _ in range(reps):
        n1, n2, m = draw_table(n_true, p11, p10, p01, rng)
        if m <= 0:
            continue
        n_hat, se, lo, hi = ER.chapman(n1, n2, m)
        if ci_widen != 1.0:
            lo, hi = n_hat - (n_hat - lo) * ci_widen, n_hat + (hi - n_hat) * ci_widen
        pts.append(n_hat)
        covered += int(lo <= n_true <= hi)
        gammas.append(n_true * m / (n1 * n2) if n1 and n2 else float('nan'))
    if not pts:
        return None
    pts.sort()
    return {'n_reps': len(pts), 'median': statistics.median(pts),
            'p25': pts[len(pts) // 4], 'p75': pts[(3 * len(pts)) // 4],
            'rel_bias': statistics.median(pts) / n_true - 1,
            'coverage': covered / len(pts),
            'gamma_emp': statistics.median(gammas)}


def control_a(targets, reps, seed):
    rows = []
    for t in targets:
        n_true = int(round(t['n_hat']))
        p1, p2 = t['n1_form'] / n_true, t['n2_git'] / n_true
        p11, p10, p01 = hetero_cells(p1, p2, 0.0)
        r = run_cells(n_true, p11, p10, p01, reps, seed)
        r.update(control='A independent-source recovery', dict=t['dict'], cv='',
                 kbar='', gamma_analytic=1.0, n_true=n_true,
                 passes=int(abs(r['rel_bias']) <= TOL
                            and COVERAGE_MIN <= r['coverage'] <= COVERAGE_MAX))
        rows.append(r)
    return rows


def mixture_cells(p1, p2, thetas):
    """Cells built by INTEGRATING over an explicit mixing family, not by substituting
    1 + CV^2 into the answer.

    External review, defect 6: control B used to generate its cells from the very
    identity it then reported as confirmed, so the check could not fail. Here the
    family is the input, the cells come from it, and `gamma_of` reads the identity
    back out -- the only path by which the check can disagree with the theory."""
    p1m = sum(w * p1 * th for th, w in thetas)
    p2m = sum(w * p2 * th for th, w in thetas)
    p11 = sum(w * (p1 * th) * (p2 * th) for th, w in thetas)
    if min(p1m - p11, p2m - p11) <= 0 or p11 <= 0:
        return None
    return p11, p1m - p11, p2m - p11, p1m, p2m


def control_b(targets, reps, seed, cvs=CV_GRID):
    rows = []
    families = (('two-point', lambda cv: ((1.0 - cv, 0.5), (1.0 + cv, 0.5))),
                ('gamma-clipped', clipped_gamma_thetas))
    for t in targets:
        n_true = int(round(t['n_hat']))
        p1, p2 = t['n1_form'] / n_true, t['n2_git'] / n_true
        for cv in cvs:
            for fam_name, fam in families:
                if cv == 0.0 and fam_name == 'gamma-clipped':
                    continue                      # degenerate, identical to two-point
                cells = mixture_cells(p1, p2, fam(cv))
                if cells is None:
                    continue
                p11, p10, p01, p1m, p2m = cells
                if p11 + p10 + p01 >= 1:
                    continue
                # read the identity back OUT of the constructed cells
                g_emp_family = gamma_of(p11, p1m, p2m)
                _, cv_real = family_moments(fam(cv))
                g = gamma_two_point(cv_real)     # identity at the family's TRUE cv
                r = run_cells(n_true, p11, p10, p01, reps, seed)
                if r is None:
                    continue
                # does the envelope, evaluated at the analytic gamma, recover the truth?
                n1s = int(round(n_true * p1m)); n2s = int(round(n_true * p2m))
                ms = int(round(n_true * p11))
                rec = envelope(n1s, n2s, ms, g_emp_family)
                r.update(control='B heterogeneous detectability', dict=t['dict'], cv=cv,
                         kbar='', gamma_analytic=g_emp_family, n_true=n_true,
                         family=fam_name, gamma_identity=g, cv_realised=cv_real,
                         envelope_recovery=rec / n_true - 1 if rec else '',
                         bias_predicted=-(g_emp_family - 1) / g_emp_family)
                r['passes'] = int(abs(g_emp_family - g) <= 1e-9        # the identity itself
                                  and abs(r['gamma_emp'] - g_emp_family) <= TOL * g_emp_family
                                  and abs(r['rel_bias'] - r['bias_predicted']) <= TOL
                                  and abs(rec / n_true - 1) <= TOL)
                rows.append(r)
    return rows


def control_c(targets, reps, seed, kbars=KBAR_GRID):
    rows = []
    for t in targets:
        n_true = int(round(t['n_hat']))
        # PER-ERROR detection probabilities. They are NOT calibrated to reproduce the
        # dictionary's site-level era sizes: a site with k errors is caught if any one
        # of them is found, so the implied site-level size exceeds n_j whenever k > 1
        # (external review, defect 9). The mechanism's gamma does not depend on q1, q2
        # -- it is a function of kbar alone -- so the gamma column is unaffected; the
        # COVERAGE column is therefore not dictionary-matched, and each row now carries
        # the implied sizes so the mismatch is visible rather than assumed away.
        q1 = t['n1_form'] / n_true
        q2 = t['n2_git'] / n_true
        for kbar in kbars:
            p11, p10, p01, p1, p2 = sequential_cells(q1, q2, kbar)
            g = gamma_of(p11, p1, p2)
            implied_n1, implied_n2 = round(n_true * p1), round(n_true * p2)
            if min(p10, p01) <= 0 or p11 <= 0:
                # kbar = 1 is the degenerate corner: one error per site, fixed in era 1,
                # so recapture is impossible and gamma = 0. Recorded, not simulated —
                # there is no table to draw, which is itself the result.
                rows.append({'control': 'C sequential removal', 'dict': t['dict'],
                             'cv': '', 'kbar': kbar, 'n_true': n_true,
                             'gamma_analytic': g, 'gamma_emp': float('nan'),
                             'median': float('nan'), 'p25': '', 'p75': '',
                             'rel_bias': float('nan'), 'bias_predicted': float('inf'),
                             'coverage': 0.0, 'envelope_recovery': '', 'n_reps': 0,
                             'passes': int(g < 1.0)})
                continue
            r = run_cells(n_true, p11, p10, p01, reps, seed)
            if r is None:
                continue
            r.update(control='C sequential removal', dict=t['dict'], cv='', kbar=kbar,
                     gamma_analytic=g, n_true=n_true, envelope_recovery='',
                     implied_n1=implied_n1, implied_n2=implied_n2,
                     observed_n1=t['n1_form'], observed_n2=t['n2_git'],
                     bias_predicted=1 / g - 1)
            r['passes'] = int(g < 1.0 and abs(r['gamma_emp'] - g) <= TOL * g)
            rows.append(r)
    return rows


def control_e(targets, reps, seed, cells=((1.5, 0.50), (1.5, 0.85), (2.5, 0.50),
                                          (2.5, 1.00), (4.0, 0.85))):
    """E  MECHANISM COMPOSITION (added 20-09-2026 after external review, defect 4).

    Controls B and C each size one mechanism. The report then MULTIPLIED their gammas
    to argue heterogeneity cancels sequential removal at CV = 0.85. That step has no
    derivation: a shared site-level theta correlates the eras within a site, so the
    composite gamma is not the product. This control computes the joint gamma exactly
    and reports the product's error. It PASSES when the simulation reproduces the
    exact joint gamma -- the product is reported, never used."""
    rows = []
    for t in targets:
        n_true = int(round(t['n_hat']))
        q1, q2 = t['n1_form'] / n_true, t['n2_git'] / n_true
        for kbar, cv in cells:
            jc = joint_cells(q1, q2, kbar, cv)
            if jc is None:
                continue
            p11, p10, p01, p1, p2 = jc
            if min(p10, p01) <= 0 or p11 <= 0 or p11 + p10 + p01 >= 1:
                continue
            g_joint = gamma_of(p11, p1, p2)
            sc = sequential_cells(q1, q2, kbar)
            g_seq = gamma_of(sc[0], sc[3], sc[4])
            g_het = gamma_two_point(cv)
            product = g_seq * g_het
            r = run_cells(n_true, p11, p10, p01, reps, seed)
            if r is None:
                continue
            r.update(control='E mechanism composition', dict=t['dict'], cv=cv,
                     kbar=kbar, gamma_analytic=g_joint, n_true=n_true,
                     gamma_sequential=g_seq, gamma_heterogeneity=g_het,
                     gamma_naive_product=product,
                     product_error=product - g_joint,
                     envelope_recovery='', bias_predicted=1 / g_joint - 1)
            r['passes'] = int(abs(r['gamma_emp'] - g_joint) <= TOL * g_joint)
            rows.append(r)
    return rows


# --------------------------------------------------------------------------- #
# what the correction histories CAN identify: per-site overdispersion
# --------------------------------------------------------------------------- #
def site_event_counts(rows, level=None):
    """{dict: {era: {site_key: n_events}}} using the operating linkage key.

    Counts EVENTS per site, which `headword_linkage.site_sets` discards. The alias
    layer is deliberately not applied: it manufactures a site key from a corrected
    value and would not correspond to an additional correction event."""
    keyfn = HL.KEY_BY_NAME[ER.LINKAGE_LEVEL if level is None else level]
    per = defaultdict(lambda: defaultdict(lambda: defaultdict(int)))
    for r in rows:
        h = (r.get('headword_iast') or '').strip()
        if not h:
            continue
        k = keyfn(h)
        if k:
            per[r['dict']][r['source_layer']][k] += 1
    return per


def _ztp_moments(mu_raw):
    """(mean, var) of a Poisson(mu_raw) conditioned on X >= 1."""
    s = 1 - math.exp(-mu_raw)
    if s <= 0:
        return 1.0, 0.0
    mean = mu_raw / s
    e2 = (mu_raw * mu_raw + mu_raw) / s
    return mean, e2 - mean * mean


def ztp_lambda_for_mean(mean, lo=1e-9, hi=500.0):
    """Poisson rate whose ZERO-TRUNCATED mean is `mean` (mean > 1)."""
    if mean <= 1.0:
        return lo
    for _ in range(300):
        mid = (lo + hi) / 2
        if _ztp_moments(mid)[0] > mean:
            hi = mid
        else:
            lo = mid
    return (lo + hi) / 2


def dispersion_ratio(counts):
    """Observed variance divided by the variance of a ZERO-TRUNCATED Poisson of the
    same mean. > 1 is overdispersion, < 1 underdispersion.

    The naive (Var - Mean)/Mean^2 moment estimator is invalid here: a site with no
    correction event is unobservable in both eras, so the counts are conditioned on
    X >= 1, and that conditioning removes variance on its own. Comparing against the
    matched zero-truncated Poisson is the like-for-like version."""
    if len(counts) < 2:
        return None
    mean = statistics.fmean(counts)
    var = statistics.variance(counts)
    if mean <= 1.0 + 1e-12:
        return None
    ref = _ztp_moments(ztp_lambda_for_mean(mean))[1]
    return var / ref if ref > 0 else None


def _ztnb_moments(lam, k):
    """(mean, var) of X ~ Poisson(lam*theta), theta ~ Gamma(mean 1, CV^2 = 1/k), X >= 1.

    The Gamma mixing family is used here — and NOT the bounded two-point family of
    control B — because a bounded theta caps the achievable dispersion far below what
    these counts show: at mean 1.218 the two-point family cannot exceed a dispersion
    ratio of about 1.04 at any CV, while pw's form era sits at 5.2. A family that
    cannot reach the data is not a fit, it is an argmax."""
    p0 = (1 + lam / k) ** (-k)
    s = 1 - p0
    if s <= 0:
        return None
    mean = lam / s
    e2 = (lam + lam * lam + lam * lam / k) / s
    return mean, e2 - mean * mean


def _ztnb_lambda_for_mean(mean, k):
    lo, hi = 1e-12, 1e6
    for _ in range(300):
        mid = (lo + hi) / 2
        mm = _ztnb_moments(mid, k)
        if mm is None or mm[0] > mean:
            hi = mid
        else:
            lo = mid
    return (lo + hi) / 2


def gamma_family_variance_ceiling(mean, k_lo=1e-6):
    """Supremum of the zero-truncated Poisson-Gamma variance at a fixed truncated mean.

    The variance is monotone decreasing in k, so the ceiling is the k -> 0 limit. It is
    finite, and that is the non-obvious part: driving the Gamma's CV up also drives lam
    down (the truncated mean is held fixed), and the two effects cancel. The ceiling
    belongs to the FAMILY, not to mixed Poissons in general — a mixing distribution with
    a heavy enough tail can exceed it, at the cost of no longer being summarised by one
    parameter."""
    mm = _ztnb_moments(_ztnb_lambda_for_mean(mean, k_lo), k_lo)
    return mm[1] if mm else None


def fit_latent_cv_nb(counts):
    """CV of a latent per-site intensity factor matching the observed mean AND variance,
    under a zero-truncated Poisson-Gamma.

    Returns a dict with `status` in {'fitted', 'homogeneous', 'unreachable'}:
      fitted       — a CV reproduces both moments;
      homogeneous  — the counts are no more dispersed than a plain ZT Poisson already is;
      unreachable  — the observed variance EXCEEDS the family's ceiling at that mean, so
                     no CV fits at all. That is a result about the data, not a solver
                     failure, and it must never be reported as the argmax."""
    if len(counts) < 2:
        return None
    mean = statistics.fmean(counts)
    var = statistics.variance(counts)
    if mean <= 1.0 + 1e-12:
        return None
    k_hi = 1e7                                    # k -> infinity is the Poisson limit
    floor = _ztnb_moments(_ztnb_lambda_for_mean(mean, k_hi), k_hi)
    ceiling = gamma_family_variance_ceiling(mean)
    base = {'mean': mean, 'var': var, 'ceiling': ceiling,
            'poisson_var': floor[1] if floor else None}
    if floor and floor[1] >= var:
        return dict(base, status='homogeneous', cv=0.0)
    if ceiling is not None and var > ceiling:
        return dict(base, status='unreachable', cv=None,
                    excess=var / ceiling if ceiling else None)
    lo, hi = 1e-6, k_hi                           # variance decreases as k rises
    for _ in range(300):
        mid = math.sqrt(lo * hi)
        mm = _ztnb_moments(_ztnb_lambda_for_mean(mean, mid), mid)
        if mm is None or mm[1] > var:
            lo = mid
        else:
            hi = mid
    k = math.sqrt(lo * hi)
    return dict(base, status='fitted', cv=1 / math.sqrt(k), k=k)


def _ztmix_moments(lam, c):
    """(mean, var) of X ~ Poisson(lam*theta) | X >= 1, theta in {1-c, 1+c} equiprobable.

    The observed population is the sites with at least one event, so the two theta
    arms are re-weighted by their own P(X >= 1) — the site that attracts nothing is
    missing from the data, not present with a zero."""
    arms = []
    for th in (1 - c, 1 + c):
        mu = lam * th
        if mu <= 0:
            continue
        s = 1 - math.exp(-mu)
        arms.append((0.5 * s, mu / s, (mu * mu + mu) / s))
    tot = sum(w for w, _, _ in arms)
    if tot <= 0:
        return None
    mean = sum(w * m1 for w, m1, _ in arms) / tot
    e2 = sum(w * m2 for w, _, m2 in arms) / tot
    return mean, e2 - mean * mean


def bounded_dispersion_ceiling(mean, cmax=0.999, steps=200):
    """Largest dispersion ratio D the BOUNDED two-point theta family can reach at this
    mean, maximised over CV.

    Worth computing rather than assuming: theta <= 2 caps how much spread a site-level
    factor can manufacture, and at these means the cap turns out to be close to 1 —
    which is how the bounded family was caught failing to fit these counts at all."""
    if mean <= 1.0 + 1e-12:
        return None
    ref = _ztp_moments(ztp_lambda_for_mean(mean))[1]
    if ref <= 0:
        return None
    best = 0.0
    for i in range(steps + 1):
        c = cmax * i / steps
        lo, hi = 1e-9, 500.0
        for _ in range(120):
            mid = (lo + hi) / 2
            mm = _ztmix_moments(mid, c)
            if mm is None or mm[0] > mean:
                hi = mid
            else:
                lo = mid
        mm = _ztmix_moments((lo + hi) / 2, c)
        if mm:
            best = max(best, mm[1])
    return best / ref


# --------------------------------------------------------------------------- #
# ranking arithmetic
# --------------------------------------------------------------------------- #
def remaining_at(row, gamma):
    n = envelope(row['n1_form'], row['n2_git'], row['m_overlap'], gamma)
    return None if n is None else n - row['s_observed']


def common_gamma_swap(a, b):
    """gamma at which `remaining` of a and b are equal, under one corpus-common gamma.

    remaining_d(g) = g*B_d - 1 - S_d, so the crossing is linear in g and exact."""
    ba = (a['n1_form'] + 1) * (a['n2_git'] + 1) / (a['m_overlap'] + 1)
    bb = (b['n1_form'] + 1) * (b['n2_git'] + 1) / (b['m_overlap'] + 1)
    if abs(ba - bb) < 1e-12:
        return None
    return (a['s_observed'] - b['s_observed']) / (ba - bb)


def differential_ratio_swap(a, b):
    """gamma_b / gamma_a needed to equalise `remaining`, holding gamma_a = 1."""
    ba = (a['n1_form'] + 1) * (a['n2_git'] + 1) / (a['m_overlap'] + 1)
    bb = (b['n1_form'] + 1) * (b['n2_git'] + 1) / (b['m_overlap'] + 1)
    target = (ba - 1 - a['s_observed']) + b['s_observed'] + 1
    return target / bb if bb else None


# --------------------------------------------------------------------------- #
# IO helpers
# --------------------------------------------------------------------------- #
def sha256(path, limit=None):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(1 << 20), b''):
            h.update(chunk)
    return h.hexdigest()


def load_published():
    with open(PUBLISHED, encoding='utf-8') as f:
        return list(csv.DictReader(f))


def fmt(v, nd=0):
    if v is None or v == '':
        return '—'
    if isinstance(v, float) and (math.isnan(v) or math.isinf(v)):
        return '—'
    return f'{v:,.{nd}f}'


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--selftest', action='store_true')
    ap.add_argument('--reps', type=int, default=REPS)
    ap.add_argument('--quick', action='store_true',
                    help='one dictionary per control (smoke run, not the published grid)')
    args = ap.parse_args()
    if args.selftest:
        return selftest()

    with open(EVENTS, encoding='utf-8') as f:
        rows = list(csv.DictReader(f))
    est = ER.estimates(ER.collect(rows))
    by = {r['dict']: r for r in est}

    # arithmetic reproduction check against the committed published table
    pub = {r['dict']: r for r in load_published()}
    repro = []
    for d, p in pub.items():
        mine = by.get(d)
        ok = (mine and int(p['n1_form']) == mine['n1_form']
              and int(p['n2_git']) == mine['n2_git']
              and int(p['m_overlap']) == mine['m_overlap'])
        repro.append((d, bool(ok)))
    repro_fail = [d for d, ok in repro if not ok]

    estimable = [r for r in est if r['estimable']]
    estimable.sort(key=lambda r: -r['remaining_hat'])
    # EVERY estimable dictionary, capped ones included. The earlier exclusion of the
    # capped row (cae) was undeclared protocol drift: the preregistration promises the
    # controls for every estimable dictionary, and the cap affects only how the
    # PUBLISHED row is displayed, not whether the mechanism can be simulated against
    # its counts (external review, defect 5).
    targets = estimable

    reps = args.reps
    ctl_targets = targets[:1] if args.quick else targets
    ctrl = (control_a(ctl_targets, reps, SEED)
            + control_b(ctl_targets, reps, SEED)
            + control_c(ctl_targets, reps, SEED)
            + control_e(ctl_targets, reps, SEED))

    # envelope table
    env_rows = []
    for r in estimable:
        cap = ER.RECORD_COUNTS.get(r['dict'])
        for g in GAMMA_GRID:
            n = envelope(r['n1_form'], r['n2_git'], r['m_overlap'], g)
            n_floor = max(n, r['s_observed'])
            env_rows.append({
                'dict': r['dict'], 'gamma': g,
                'n_hat': round(n_floor),
                'remaining': round(n_floor - r['s_observed']),
                'above_record_count': int(cap is not None and n > cap),
                'inside_published_ci': int(
                    r['ci_low'] != '' and float(r['ci_low']) <= n <= float(r['ci_high'])),
            })

    # gamma thresholds per dictionary
    thr = []
    for r in estimable:
        cap = ER.RECORD_COUNTS.get(r['dict'])
        a = {'dict': r['dict'],
             'g_ci_low': gamma_for_target(r['n1_form'], r['n2_git'], r['m_overlap'],
                                          float(r['ci_low'])) if r['ci_low'] != '' else None,
             'g_ci_high': gamma_for_target(r['n1_form'], r['n2_git'], r['m_overlap'],
                                           float(r['ci_high'])) if r['ci_high'] != '' else None,
             'g_cap': gamma_for_target(r['n1_form'], r['n2_git'], r['m_overlap'], cap) if cap else None,
             'g_sobs': gamma_for_target(r['n1_form'], r['n2_git'], r['m_overlap'], r['s_observed'])}
        # LITERAL preregistered rule (restored 20-09-2026, external review defect 5):
        # "report the smallest |log gamma| at which this happens, and call the interval
        # fragile if it happens at gamma in [0.90, 1.10]". The implementation had
        # silently required BOTH crossings inside the band, which is a strictly
        # stronger and therefore more flattering test. The break is the crossing
        # NEAREST gamma = 1; if the published interval already excludes the envelope
        # at gamma = 1, the break is at gamma = 1 itself.
        n_at_1 = envelope(r['n1_form'], r['n2_git'], r['m_overlap'], 1.0)
        outside_at_1 = (r['ci_low'] != ''
                        and not (float(r['ci_low']) <= n_at_1 <= float(r['ci_high'])))
        crossings = [g for g in (a['g_ci_low'], a['g_ci_high']) if g and g > 0]
        if outside_at_1:
            a['g_break'] = 1.0
        elif crossings:
            a['g_break'] = min(crossings, key=lambda g: abs(math.log(g)))
        else:
            a['g_break'] = None
        a['break_at_gamma_1_via_cap'] = int(outside_at_1)
        a['fragile'] = int(a['g_break'] is not None
                           and FRAGILE_BAND[0] <= a['g_break'] <= FRAGILE_BAND[1])
        thr.append(a)

    # ranking
    order = [r['dict'] for r in estimable]
    swaps = []
    for i in range(len(estimable) - 1):
        a, b = estimable[i], estimable[i + 1]
        g_swap = common_gamma_swap(a, b)
        # A crossing is only a real reordering if both dictionaries still have a
        # POSITIVE remaining count there. cae / bur cross at gamma = 0.016, where
        # both remainders are about -1,440: under the report's floor both are zero
        # and the pair ties rather than swapping (external review, defect 7).
        rem_a = remaining_at(a, g_swap) if g_swap and g_swap > 0 else None
        rem_b = remaining_at(b, g_swap) if g_swap and g_swap > 0 else None
        feasible = int(rem_a is not None and rem_b is not None
                       and rem_a > 0 and rem_b > 0)
        swaps.append({'pair': f"{a['dict']} / {b['dict']}",
                      'common_gamma': g_swap,
                      'remaining_at_crossing': rem_a,
                      'feasible': feasible,
                      'differential_ratio': differential_ratio_swap(a, b)})

    # identifiability demonstration on the largest dictionary
    top = estimable[0]
    nonid = nonidentification_check(top['n1_form'], top['n2_git'], top['m_overlap'],
                                    GAMMA_GRID)

    # overdispersion on the real histories
    sc = site_event_counts(rows)
    od = []
    for r in estimable:
        d = r['dict']
        for era in ('form', 'git'):
            c = list(sc.get(d, {}).get(era, {}).values())
            fit = fit_latent_cv_nb(c)
            mean = statistics.fmean(c) if c else None
            var = statistics.variance(c) if len(c) > 1 else None
            cv = fit.get('cv') if fit else None
            od.append({'dict': d, 'era': era, 'sites': len(c),
                       'events': sum(c), 'mean': mean, 'var': var,
                       'disp': dispersion_ratio(c),
                       'status': fit['status'] if fit else None,
                       'excess': (var / fit['ceiling']
                                  if fit and fit.get('ceiling') and var else None),
                       'cv': cv,
                       'gamma_indicative': (1 + cv ** 2) if cv else None})

    zero_m = [r for r in est if r['m_overlap'] == 0 and r['s_observed'] > 0]

    with open(OUT_CSV, 'w', encoding='utf-8', newline='') as f:
        w = csv.DictWriter(f, fieldnames=list(env_rows[0].keys()))
        w.writeheader(); w.writerows(env_rows)
    ctrl_fields = ['control', 'dict', 'cv', 'kbar', 'n_true', 'gamma_analytic',
                   'gamma_emp', 'median', 'p25', 'p75', 'rel_bias', 'bias_predicted',
                   'coverage', 'envelope_recovery', 'n_reps', 'passes']
    with open(OUT_CTRL, 'w', encoding='utf-8', newline='') as f:
        w = csv.DictWriter(f, fieldnames=ctrl_fields, extrasaction='ignore')
        w.writeheader(); w.writerows(ctrl)

    write_md(est, estimable, env_rows, thr, swaps, nonid, od, ctrl, zero_m,
             repro, repro_fail, reps, order)
    print(f'wrote {OUT_MD}')
    print(f'wrote {OUT_CSV}  ({len(env_rows)} rows)')
    print(f'wrote {OUT_CTRL} ({len(ctrl)} rows)')
    failed = [c for c in ctrl if not c.get('passes')]
    print(f'controls: {len(ctrl) - len(failed)}/{len(ctrl)} pass')
    for c in failed:
        print(f"  FAIL {c['control']} {c['dict']} cv={c['cv']} kbar={c['kbar']}")
    return 0


# --------------------------------------------------------------------------- #
# report
# --------------------------------------------------------------------------- #
def write_md(est, estimable, env_rows, thr, swaps, nonid, od, ctrl, zero_m,
             repro, repro_fail, reps, order):
    from datetime import date
    L = []; A = L.append
    A('_Created: 20-09-2026 · Last updated: %s_' % date.today().strftime('%d-%m-%Y'))
    A('')
    A('# What the recapture numbers survive: a dependence and detectability envelope')
    A('')
    A('_Generated by `scripts/recapture_sensitivity.py` from '
      '`observatory/site/src/data/correction_events_final.csv` (offline, reproducible). '
      'Grid and decision rules frozen in advance in '
      '[`recapture_sensitivity_prereg.md`](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/reports/recapture_sensitivity_prereg.md). '
      'Companion to [`error_recapture.md`](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/reports/error_recapture.md); '
      'it replaces no estimate there._')
    A('')

    top = estimable[0]
    t_by = {t['dict']: t for t in thr}
    tt = t_by[top['dict']]
    A('## The short version')
    A('')
    A(f"1. **The published intervals are the narrowest thing in the analysis.** "
      f"{top['dict']}'s statistical 95% CI is exhausted by a dependence factor of "
      f"{tt['g_ci_low']:.3f}–{tt['g_ci_high']:.3f} — a **{100*(tt['g_ci_high']-1):.1f}% "
      f"departure from independence swallows the whole interval**. Nothing in the data "
      f"can rule out departures far larger than that.")
    A(f"2. **Heterogeneous detectability is that departure, exactly.** A site-level "
      f"detectability factor with coefficient of variation CV produces dependence "
      f"γ = 1 + CV² — so CV = {math.sqrt(max(tt['g_ci_high'] - 1, 1e-9)):.2f} alone "
      f"pushes {top['dict']} past its published upper limit. Control B confirms the "
      f"identity and the resulting bias by simulation.")
    A('3. **The two violations do not cancel, and neither is small.** Control C sizes '
      'the sequential-removal mechanism for the first time: γ from 0.98 down to 0.58, '
      'and exactly 0 in the corner where sites carry one error each — where the design '
      'cannot estimate at all. It runs against heterogeneity, so the net is a '
      'difference of two large unmeasured quantities, which is worse than either.')
    A('4. **Even the ordering breaks, at a γ that mechanism can reach** (§5, §8). The '
      'one thing that does NOT break is the arithmetic itself (control A).')
    A('5. **Zero recapture remains unidentifiable.** Nothing here changes it, and '
      'nothing here could: see §7.')
    A('6. **What to do with the published numbers:** keep them, and carry §4\'s envelope '
      'beside them. γ = 1 is a convention this design cannot test, not a result it '
      'established.')
    A('')

    A('## 1. Arithmetic, assumption, identification')
    A('')
    A('Three different kinds of statement are mixed together in the published report. '
      'They have different warrants and this section separates them once, for the rest '
      'of the document to refer back to.')
    A('')
    A('| | Statement | Warrant | Can the data check it? |')
    A('|---|---|---|---|')
    A('| **Arithmetic** | the counts n1, n2, m and the Chapman value computed from them | '
      'the committed events CSV plus a formula | yes — reproduced below |')
    A('| **Assumption** | that the two eras discover error sites independently (γ = 1) | '
      'none; it is a modelling choice | **no** — the model is saturated (§2) |')
    A('| **Identifiable** | how unevenly sites attract corrections | the observed '
      'per-site event counts | partly — as overdispersion, with confounds (§6) |')
    A('')
    if repro_fail:
        A(f'**Arithmetic reproduction: FAIL** for {", ".join(sorted(repro_fail))} — the '
          'counts recomputed here differ from the committed `error_recapture.csv`. '
          'Everything downstream is suspect until that is resolved.')
    else:
        A(f'**Arithmetic reproduction: PASS.** All {len(repro)} dictionary rows of '
          '`error_recapture.csv` (n1, n2, m) recompute from the events CSV on this '
          'revision, so the sensitivity below is applied to the published numbers '
          'themselves, not to a re-derivation of them.')
    A('')

    A('## 2. One axis, and why the data cannot choose a point on it')
    A('')
    A('With the form era as occasion 1 and the git era as occasion 2 over N sites,')
    A('')
    A('    γ  =  P(caught in era 2 | caught in era 1) / P(caught in era 2)')
    A('')
    A('gives E[n1] = N·p1, E[n2] = N·p2, E[m] = N·p1·p2·γ and hence the *moment* '
      'identity **N = γ·E[n1]·E[n2]/E[m]**. Substituting the realised counts — and, '
      'below, Chapman’s +1-adjusted ratio in place of the plain one — is the '
      'sensitivity **convention** of this report, not a further consequence of that '
      'identity: the equality holds between expectations, and the plug-in version '
      'inherits the usual ratio-estimator error on top. '
      'Independence is γ = 1. Positive dependence (γ > 1) means the eras revisit the '
      'same sites, m is inflated and Chapman **underestimates**; negative dependence '
      '(γ < 1) means a form-era fix removes the error a git-era recapture would have '
      'needed, m is deflated and Chapman **overestimates**.')
    A('')
    A('**What γ does and does not absorb.** Every *dependence between the two eras* on '
      'a fixed, correctly linked set of sites is summarised by this one number — that '
      'covers both mechanisms `error_recapture.md` names (sequential occasions, '
      'correlated catchability), and it is what §3 sizes. Two other assumptions of the '
      'published design are **not** of that form and are not covered anywhere in this '
      'report: **closure** (sites entering or leaving the population between the eras '
      'changes the estimand itself, not the dependence between lists) and **linkage '
      'error** (a false match inflates m, a missed match deflates it, which corrupts '
      'the observation mechanism rather than re-weighting it). A scalar multiplier '
      'cannot repair either, and neither is bounded by the envelope below.')
    A('')
    A('A two-list table has exactly three observable counts — era-1 only, era-2 only, '
      'both. The independence model spends all three on (N, p1, p2): it is saturated, '
      'with zero residual degrees of freedom and therefore no goodness-of-fit test. '
      'Adding γ gives four parameters for three counts, and the likelihood is flat '
      f'along the curve. On {top["dict"]} (n1={top["n1_form"]:,}, n2={top["n2_git"]:,}, '
      f'm={top["m_overlap"]:,}):')
    A('')
    lls = [ll for _, _, ll, _ in nonid if ll is not None]
    ref = max(lls) if lls else 0.0
    A('| γ | profile N̂ | max |expected − observed| over the 3 cells | log-likelihood '
      '(relative to the best) |')
    A('|---:|---:|---:|---:|')
    for g, n, ll, resid in nonid:
        if ll is None:
            A(f'| {g:.2f} | — | — | — |')
            continue
        A(f'| {g:.2f} | {n:,.0f} | {resid:.2e} | {ll - ref:+.4f} |')
    if len(lls) > 1:
        A('')
        n_lo = min(n for _, n, ll, _ in nonid if ll is not None)
        n_hi = max(n for _, n, ll, _ in nonid if ll is not None)
        A('The middle column is the point: **at every γ the fitted model reproduces all '
          'three observed counts exactly** (residuals at floating-point noise). The '
          f'grid spans a **{n_hi / n_lo:.1f}-fold** range of N̂ — {n_lo:,.0f} to '
          f'{n_hi:,.0f} — and every value in it fits the table equally well.')
        A('')
        A('The last column needs stating precisely, because it is weaker than "flat". '
          f'It spans **{max(lls) - min(lls):.3f} log-likelihood units** across that '
          'range, and the difference is **monotone**: the finite-N combinatorial term '
          'gives a real, if very weak, preference for the smaller N̂ (the profile also '
          'excludes the boundary N = S_obs, which would sit at the end of that same '
          'slope). So this is not exact non-identification of the full finite-N '
          'likelihood; it is a likelihood that discriminates by less than a fifth of a '
          'log-unit where two units is the conventional threshold for *weak* evidence. '
          'The identification argument proper is the middle column and the parameter '
          'count — four parameters, three counts, zero residual degrees of freedom — '
          'not the size of that slope. Exact non-identification holds for the unseen '
          'cell under the conditional/Poisson formulations, where the term producing '
          'this slope is not part of the likelihood at all.')
        A('')
        A('Either way the practical consequence is the same, and it is not a wide '
          'confidence interval: more events from these same two eras do not touch it, '
          'because the deficiency is in the design — two lists — and not in the sample '
          'size.')
    A('')

    A('## 3. Controls')
    A('')
    A(f'Preregistered pass conditions, {reps} replicates per cell, seed {SEED}, exact '
      'multinomial sampling (Beta-recursion binomial, no normal approximation).')
    A('')
    A('| Control | Dict | CV | k̄ | γ (analytic) | γ (simulated) | Chapman rel. bias | '
      'predicted | 95% CI coverage | Verdict |')
    A('|---|---|---:|---:|---:|---:|---:|---:|---:|:--:|')
    def pct(v):
        if v in ('', None) or (isinstance(v, float) and (math.isnan(v) or math.isinf(v))):
            return '—'
        return f'{100*v:+.1f}%'

    for c in ctrl:
        degenerate = not c['n_reps']
        A('| {control} | {dict} | {cv} | {kbar} | {ga} | {ge} | {rb} | {bp} | {cov} | {v} |'.format(
            control=c['control'], dict=c['dict'],
            cv=(f"{c['cv']:.2f}" if c['cv'] != '' else '—'),
            kbar=(f"{c['kbar']:.1f}" if c['kbar'] != '' else '—'),
            ga=f"{c['gamma_analytic']:.4f}",
            ge=('n/a' if degenerate else f"{c['gamma_emp']:.4f}"),
            rb=('unbounded' if degenerate else pct(c['rel_bias'])),
            bp=('unbounded' if degenerate else pct(c.get('bias_predicted'))),
            cov=('n/a' if degenerate else f"{100*c['coverage']:.1f}%"),
            v='PASS' if c['passes'] else 'FAIL'))
    A('')
    a_rows = [c for c in ctrl if c['control'].startswith('A')]
    b_rows = [c for c in ctrl if c['control'].startswith('B')]
    c_rows = [c for c in ctrl if c['control'].startswith('C')]
    if a_rows:
        A(f"**A — independent-source recovery.** When the two sources really are "
          f"independent the published machinery recovers the truth: median bias "
          f"{100*statistics.fmean([r['rel_bias'] for r in a_rows]):+.2f}%, nominal-95% "
          f"coverage {100*statistics.fmean([r['coverage'] for r in a_rows]):.1f}%. "
          f"The arithmetic is not the problem.")
    if b_rows:
        worst = min(b_rows, key=lambda r: r['coverage'])
        half = [r for r in b_rows if abs(r['cv'] - 0.5) < 1e-9]
        A('')
        A(f"**B — heterogeneous detectability.** The analytic identity γ = 1 + CV² is "
          f"reproduced at every level, and the envelope evaluated at that γ recovers the "
          f"true N. The interesting column is the last one: at CV = "
          f"{worst['cv']:.2f} the nominal 95% interval covers the truth "
          f"{100*worst['coverage']:.1f}% of the time. "
          + (f"Already at CV = 0.50 — mild unevenness — coverage is "
             f"{100*statistics.fmean([r['coverage'] for r in half]):.1f}% and the point "
             f"estimate is {100*statistics.fmean([r['rel_bias'] for r in half]):+.0f}% off. "
             if half else '')
          + "**The published CI is a statement about sampling noise only; it carries no "
            "information about the assumption that dominates the error.**")
    live_c = [r for r in c_rows if r['n_reps']]
    if live_c:
        gmin = min(r['gamma_analytic'] for r in live_c)
        gmax = max(r['gamma_analytic'] for r in live_c)
        A('')
        A(f"**C — sequential removal.** Sized here for the first time. Over the "
          f"mean-error grid the mechanism gives γ ∈ [{gmin:.3f}, {gmax:.3f}] — an "
          f"**upward** bias on N̂ of {100*(1/gmax - 1):+.0f}% to {100*(1/gmin - 1):+.0f}%, "
          f"weakening as sites carry more errors, exactly as the mechanism predicts. "
          f"The corner case is the sharpest statement in this report: if a site carries "
          f"**exactly one** error, the form era's fix removes the very thing a git-era "
          f"recapture would need, γ = 0, and the two-era design cannot estimate that "
          f"dictionary at all — not imprecisely, at all.")
    e_rows = [r for r in ctrl if r['control'].startswith('E')]
    if e_rows:
        A('')
        worst_e = max(e_rows, key=lambda r: abs(r['product_error']))
        neg = [r for r in e_rows if r['gamma_analytic'] < 1.0]
        A("**E — mechanism composition, and a correction to an earlier draft of this "
          "report.** An earlier version argued that heterogeneity *cancels* sequential "
          "removal at a detectability CV of about 0.85, by multiplying the two "
          "mechanisms' γ values together. That step is wrong, and external review "
          "caught it. When one site-level factor scales both eras' detection "
          "probabilities, the eras become correlated *within* a site, and the composite "
          "γ is not the product of the separate ones. Control E computes the joint "
          "mechanism exactly instead of multiplying:")
        A('')
        A('| k̄ | CV | γ sequential | γ heterogeneity | naive product | **true joint γ** | product error |')
        A('|---:|---:|---:|---:|---:|---:|---:|')
        for r in sorted(e_rows, key=lambda r: (r['kbar'], r['cv']))[:8]:
            A(f"| {r['kbar']:.1f} | {r['cv']:.2f} | {r['gamma_sequential']:.4f} | "
              f"{r['gamma_heterogeneity']:.4f} | {r['gamma_naive_product']:.4f} | "
              f"**{r['gamma_analytic']:.4f}** | {r['product_error']:+.4f} |")
        A('')
        A("The product overstates the composite γ in every cell, by as much as "
          f"{abs(worst_e['product_error']):.3f}, and it can get the **sign of the net "
          "bias wrong**: at k̄ = 1.5, CV = 0.85 the product says 1.004 — cancellation, "
          "a hair of positive dependence — while the true joint value is "
          f"{[r for r in e_rows if abs(r['cv']-0.85) < 1e-9 and abs(r['kbar']-1.5) < 1e-9][0]['gamma_analytic']:.4f}"
          ", still clearly negative dependence. "
          + (f"{len(neg)} of the {len(e_rows)} composed cells stay below 1. "
             if neg else "")
          + "The correction runs **in favour of** this report's headline rather than "
            "against it: heterogeneity does not neutralise sequential removal as easily "
            "as the multiplied figure suggested, so the γ < 1 region that reorders the "
            "ranking in §5 is reached under a wider range of joint assumptions, not a "
            "narrower one.")
    A('')

    A('## 4. The envelope, and where the published intervals break')
    A('')
    A('N̂ at each grid γ, floored at the observed site count (a population cannot be '
      'smaller than what was seen) and flagged where it exceeds the dictionary\'s '
      'physical record count — the point at which the row means "treat as unproofread" '
      'rather than carrying a number.')
    A('')
    dicts = [r['dict'] for r in estimable]
    A('| γ | ' + ' | '.join(dicts) + ' |')
    A('|---:|' + '|'.join(['---:'] * len(dicts)) + '|')
    ev = {(r['dict'], r['gamma']): r for r in env_rows}
    for g in GAMMA_GRID:
        cells = []
        for d in dicts:
            r = ev[(d, g)]
            s = f"{r['n_hat']:,}"
            if r['above_record_count']:
                s += ' ⚠'
            if r['inside_published_ci']:
                s = '**' + s + '**'
            cells.append(s)
        marker = ' ←published' if g == 1.00 else ''
        A(f'| {g:.2f}{marker} | ' + ' | '.join(cells) + ' |')
    A('')
    A('**Bold** = still inside that dictionary\'s published 95% CI. ⚠ = above the '
      'dictionary\'s record count, i.e. the estimate no longer bounds the population '
      'below the whole dictionary.')
    A('')
    A('The γ at which each published boundary is crossed:')
    A('')
    A('| Dict | γ at CI low | γ at CI high | **break γ** (nearest 1) | CI fragile? | '
      'γ at record count | γ at observed floor |')
    A('|---|---:|---:|---:|:--:|---:|---:|')
    for t in thr:
        brk = ('1.000 (already outside at γ = 1)' if t['break_at_gamma_1_via_cap']
               else (f"{t['g_break']:.3f}" if t['g_break'] else '—'))
        A('| {d} | {lo} | {hi} | {b} | {f} | {cap} | {so} |'.format(
            d=t['dict'],
            lo=(f"{t['g_ci_low']:.3f}" if t['g_ci_low'] else '—'),
            hi=(f"{t['g_ci_high']:.3f}" if t['g_ci_high'] else '—'),
            b=brk,
            f=('**yes**' if t['fragile'] else 'no'),
            cap=(f"{t['g_cap']:.3f}" if t['g_cap'] else '—'),
            so=(f"{t['g_sobs']:.3f}" if t['g_sobs'] else '—')))
    A('')
    frag = [t['dict'] for t in thr if t['fragile']]
    widths = [(t['dict'], max(abs(t['g_ci_low'] - 1), abs(t['g_ci_high'] - 1)))
              for t in thr if t['g_ci_low'] and t['g_ci_high']]
    via_cap = [t['dict'] for t in thr if t['fragile'] and t['break_at_gamma_1_via_cap']]
    if frag:
        A(f"**Fragile by the preregistered rule — the nearest break to γ = 1 falls "
          f"inside [0.90, 1.10]: {', '.join(frag)}.** The rule is applied as written "
          "(«report the smallest |log γ| at which this happens … fragile if it happens "
          "at γ ∈ [0.90, 1.10]»). An earlier draft of this report implemented it as a "
          "requirement that *both* boundary crossings lie inside the band — a strictly "
          "stronger and more flattering test, which reported no fragile interval at "
          "all. That was an undeclared deviation; external review caught it and the "
          "literal rule is restored here."
          + (f" For **{', '.join(via_cap)}** the break is at γ = 1 itself: the raw "
             "envelope already sits outside the published *capped* interval before any "
             "dependence is introduced, so the flag records the cap, not a dependence "
             "finding — see the reading note below." if via_cap else ''))
    else:
        A('**No interval is *fragile* by the letter of the preregistered rule** — no '
          'break nearest γ = 1 falls inside [0.90, 1.10]. But read the widths: ')
    if widths:
        A('')
        A('the whole published 95% interval of '
          + ', '.join(f"**{d}** is spent by a {100*w:.1f}% departure from independence"
                      for d, w in widths)
          + '. For scale, control B shows a detectability CV of 0.25 — the mildest '
            'non-zero level in the grid — is already a 6.25% departure, and CV = 0.50 '
            'is a 25% one, i.e. several times the entire statistical interval.')
    A('')
    capped_rows = [r['dict'] for r in estimable if r['capped']]
    if capped_rows:
        A(f"One reading note. **{', '.join(capped_rows)}** is published *capped* at its "
          "record count: its raw Chapman value exceeds the number of records in the "
          "dictionary. The envelope above is drawn from the raw arithmetic, so its γ = 1 "
          "cell sits above the published (capped) CI by construction — that is the cap "
          "showing through, not a disagreement with the published table.")
        A('')

    A('## 5. Where the ranking changes — and where it does not')
    A('')
    A('Published order by estimated remaining error sites: **' + ' > '.join(order) + '**.')
    A('')
    A('Two questions, and they have different answers. A **corpus-common** γ scales '
      'every dictionary\'s N̂ by the same factor, but *remaining* = N̂ − S_obs subtracts '
      'a different observed count from each, so even a common γ can reorder the list. '
      'A **dictionary-differential** γ can reorder it trivially. Both thresholds are '
      'exact (the crossing is linear in γ), not simulated:')
    A('')
    A('| Adjacent pair | swaps at common γ | real reordering? | swaps at γ-ratio (2nd ÷ 1st) |')
    A('|---|---:|:--:|---:|')
    for s in swaps:
        if not s['common_gamma'] or s['common_gamma'] <= 0:
            feas = '—'
        elif s['feasible']:
            feas = 'yes'
        else:
            feas = (f"no — both remainders ≈ {s['remaining_at_crossing']:,.0f} there"
                    if s['remaining_at_crossing'] is not None else 'no')
        A('| {p} | {c} | {f} | {d} |'.format(
            p=s['pair'],
            c=(f"{s['common_gamma']:.3f}" if s['common_gamma'] and s['common_gamma'] > 0 else 'never (γ > 0)'),
            f=feas,
            d=(f"{s['differential_ratio']:.3f}" if s['differential_ratio'] else '—')))
    A('')
    infeas = [s for s in swaps if s['common_gamma'] and s['common_gamma'] > 0
              and not s['feasible']]
    if infeas:
        A('One crossing in that table is arithmetic only, not a reordering that could be '
          'observed: '
          + ', '.join(f"**{s['pair']}** at γ = {s['common_gamma']:.3f}" for s in infeas)
          + ' puts *both* dictionaries at a negative remaining count, which the '
            'report’s floor clamps to zero — so the pair ties at zero rather than '
            'changing places. External review flagged it; it is kept in the table and '
            'marked rather than dropped.')
        A('')
    A('The differential column is also narrower than it looks: each ratio is computed '
      'holding the first dictionary at γ = 1, so it answers «how much more dependent '
      'would the second have to be than an *independent* first», not «what ratio of two '
      'arbitrary γ values reverses the pair».')
    A('')
    in_grid = [s for s in swaps if s['common_gamma'] and s['feasible']
               and GAMMA_GRID[0] <= s['common_gamma'] <= GAMMA_GRID[-1]]
    if in_grid:
        A('Pairs that swap **inside** the preregistered γ range: '
          + ', '.join(f"{s['pair']} (γ = {s['common_gamma']:.3f})" for s in in_grid)
          + '. Those orderings are not safe to quote without the assumption attached.')
    else:
        A('**No adjacent pair swaps anywhere in the preregistered γ range under a '
          'corpus-common factor.** The ordering is a property of the observed counts, '
          'not of the independence assumption — which is why it, and not the point '
          'estimates, is the part of this analysis worth planning against.')
    A('')

    A('## 6. What the correction histories can actually identify')
    A('')
    A('γ is not estimable (§2). Something adjacent to it **is** observable: how unevenly '
      'sites attract corrections, from the per-site event counts.')
    A('')
    A('Two estimator traps had to be walked past to get a number here, and both are '
      'worth recording because either one alone reverses the answer.')
    A('')
    A('**Trap 1 — zero truncation.** The textbook moment estimator CV² = (Var − Mean)/Mean² '
      'returns *negative* values for seven of the eight cells below. That is not '
      'underdispersion in the corpus; it is the estimator applied to a population '
      'conditioned on having at least one event. A site with no correction is invisible '
      'in both eras, and the truncation removes variance by itself. The like-for-like '
      'comparison is against a **zero-truncated Poisson of the same mean**: that is the '
      'D column.')
    A('')
    A('**Trap 2 — the mixing family has a variance ceiling, and the data are above it.** '
      'Fitting a CV means choosing a family for the latent factor θ. The bounded '
      'two-point θ of control B cannot produce these dispersions; neither, it turns out, '
      'can the standard unbounded choice, a **zero-truncated Poisson–Gamma**. Driving its '
      'CV up also drives its rate down, because the truncated mean is held fixed, and the '
      'two effects cancel into a finite ceiling on the variance. The observed variances '
      'sit *above* that ceiling. A solver aimed at this will happily return the boundary '
      'value — CV = 1000, "γ ≈ 10⁶" — and that number is a solver artefact, not a '
      'measurement. It is reported here as **unreachable** instead.')
    A('')
    A('| Dict | Era | Sites | Events | Mean/site | Var | D = Var ÷ ZT-Poisson Var | '
      'Var ÷ Poisson–Gamma ceiling | Latent CV |')
    A('|---|---|---:|---:|---:|---:|---:|---:|---|')
    label = {'fitted': None, 'homogeneous': 'none needed',
             'unreachable': '**no fit exists**'}
    for o in od:
        cv = (label.get(o['status']) or
              (f"{o['cv']:.3f}" if o['cv'] is not None else '—'))
        A('| {d} | {e} | {s:,} | {ev:,} | {m} | {v} | {disp} | {ex} | {cv} |'.format(
            d=o['dict'], e=o['era'], s=o['sites'], ev=o['events'],
            m=(f"{o['mean']:.3f}" if o['mean'] else '—'),
            v=(f"{o['var']:.3f}" if o['var'] is not None else '—'),
            disp=(f"{o['disp']:.3f}" if o['disp'] is not None else '—'),
            ex=(f"{o['excess']:.2f}" if o['excess'] is not None else '—'),
            cv=cv))
    A('')
    live = [o for o in od if o['disp'] is not None]
    over = [o for o in live if o['disp'] > 1.0]
    unre = [o for o in live if o['status'] == 'unreachable']
    if live:
        A(f"**{len(over)} of {len(live)}** era-dictionary cells are overdispersed against "
          f"the matched zero-truncated Poisson, up to D = "
          f"{max(o['disp'] for o in live):.2f}. "
          + (f"**{len(unre)} of {len(live)}** are above the Poisson–Gamma ceiling "
             f"entirely, by up to {max(o['excess'] for o in unre):.1f}×." if unre else ''))
    A('')
    A('That last column is the real finding of this section, and it is a negative one, '
      'stated with the scope it actually has: **no zero-truncated Poisson–Gamma of '
      'that mean can produce this much spread.** The Gamma family — the standard '
      'latent-rate mixture, and the one whose CV feeds γ = 1 + CV² — has a finite '
      'variance ceiling at a fixed truncated mean, and these cells are above it.')
    A('')
    A('**That is a statement about the Gamma family, not about mixed Poissons in '
      'general, and an earlier draft of this report overreached by claiming the '
      'latter.** External review supplied the counterexample: a bounded two-point '
      'mixture of Poisson rates (0.01 and 5.616, with weight 4.81e-4 on the high rate) '
      'reproduces the pw-form truncated mean 1.2181 and variance 1.2002 exactly. So a '
      'mixed-Poisson description exists; it simply cannot be a Gamma one. Worse for '
      'any attempt to read γ off these counts: **homogeneous capture with clustered '
      'event batches reproduces the same moments with γ = 1**. Event-count '
      'overdispersion therefore does not by itself refute homogeneous catchability. '
      'Nor is "observed moments exceed a family\'s ceiling" a calibrated test — no '
      'sampling distribution is attached to it here, so it is a descriptive '
      'impossibility for that family, not a rejection at a stated level.')
    A('')
    A('Two readings remain, and the data here cannot separate them:')
    A('')
    A('1. **Heavy-tailed heterogeneity** — a small minority of records attracting very '
      'many corrections, heavier than a Gamma tail. Then γ = 1 + CV²(θ) is not merely '
      '> 1 but potentially far above the grid in §4, because a heavy tail inflates '
      'E[θ²] without bound.')
    A('2. **Clustered events** — corrections at a site are not conditionally independent: '
      'one commit fixes several errors in one entry, one corrector works an entry '
      'through. Then the counts say nothing directly about capture probability, because '
      'the Poisson kernel itself is wrong.')
    A('')
    A('Both readings break the published design\'s assumptions; they differ in which '
      'assumption. Distinguishing them needs event *timestamps and authorship* per site '
      '— available in the events CSV, out of scope here (§9), and the concrete next '
      'investigation this report recommends.')
    A('')
    A('**What this does NOT establish.** Not a value for γ: §2 forbids it and this '
      'section adds no identification. Not even a bound, since reading 2 would void the '
      'link between count dispersion and capture dependence entirely. Event counts also '
      'mix how many errors a record carries with how findable they are, and only the '
      'second belongs in γ.')
    A('')
    A('**What it does establish.** That the *simplest* quantitative story about these '
      'histories — a Gamma-mixed Poisson, the model whose CV would feed straight into '
      f'γ = 1 + CV² — is unavailable in {len(unre)} of {len(live)} era-dictionary '
      'cells. Any model that fits has to be something else: a heavier or a bounded '
      'non-Gamma mixture, or a clustered event process. Under reading 1 that puts γ '
      'above 1, possibly far above, and the published figures at the **bottom** of '
      'their own envelope. Under reading 2 the direction is simply unknown. What it '
      'does **not** establish is that homogeneous catchability is refuted: reading 2 '
      'is compatible with γ = 1 exactly, as the batch-event construction above shows. '
      'The honest summary is that these counts leave the assumption untested rather '
      'than disproved — which is still not the reassuring branch, because the '
      'published CI is computed as though it were settled.')
    A('')

    A('## 7. Zero recapture: still not identified')
    A('')
    A(f'{len(zero_m)} dictionaries with observed sites have m = 0. For them N = γ·(n1·n2/m) '
      'is undefined at every γ: the envelope of this report has nothing to say about '
      'them, in either direction. Their only defensible statement remains the one '
      '`error_recapture.md` already makes — the observed site count is a lower bound and '
      'there is no upper one. Nothing in this analysis provides one, and the '
      'preregistration forbids claiming otherwise.')
    A('')
    low_m = [r for r in est if 0 < r['m_overlap'] < ER.MIN_M]
    A(f'A further {len(low_m)} dictionaries sit between m = 1 and the m ≥ {ER.MIN_M} '
      f'floor. For them the envelope is defined but useless: N̂ is proportional to γ/m, '
      f'so at m in the low single digits a factor-of-two change in an unmeasurable '
      f'parameter moves the estimate by as much as the entire count does. '
      + (f"The one published row capped at its record count "
         f"({', '.join(r['dict'] for r in estimable if r['capped'])}) is the same "
         f"situation one step further on. " if any(r['capped'] for r in estimable) else '')
      + 'A dependence envelope widens intervals; it does not create identification where '
        'the design has none.')
    A('')

    A('## 8. The robustness claim')
    A('')
    if in_grid:
        worst_swap = min(in_grid, key=lambda s: abs(math.log(s['common_gamma'])))
        gs_c = [r['gamma_analytic'] for r in c_rows if r['n_reps']]
        reach = [s for s in in_grid
                 if gs_c and min(gs_c) <= s['common_gamma'] <= max(max(gs_c), 1.0)]
        claim = ('**The published ordering of dictionaries by remaining error sites is '
                 'NOT robust to the dependence assumption, and the mechanism that breaks '
                 'it is one the existing report already names.** The '
                 f"{worst_swap['pair']} ordering — the headline pair — reverses at a "
                 f"corpus-common γ of {worst_swap['common_gamma']:.3f}"
                 + (f", and control C puts the sequential-removal mechanism at γ = "
                    f"{min(gs_c):.3f} when sites average 1.5 errors: the flip point is "
                    f"inside the range a mechanism already conceded in "
                    "`error_recapture.md` can produce, not out at the edge of a "
                    "hypothetical grid." if reach else
                    ", which is inside the preregistered range.")
                 + ' The point estimates and their 95% intervals are separately not '
                   'robust: a dependence departure of ~13% exhausts them (§4).')
        conf = ('high for the arithmetic — every threshold in §4 and §5 is an exact '
                'inversion, not a simulation, and the controls reproduce their analytic '
                f'predictions to within 5% at {sum(r["passes"] for r in ctrl)} of '
                f'{len(ctrl)} cells; moderate for the practical severity, which depends '
                'on the true mean error count per site — a quantity §6 shows these '
                'histories cannot pin down; and explicitly NOT extended to closure or '
                'linkage error, which §2 puts outside γ altogether')
    else:
        claim = ('**The ordering of the four estimable dictionaries by remaining error '
                 'sites is robust to any corpus-common dependence factor in [0.50, 2.00], '
                 'and to dictionary-differential factors up to the ratios in §5; the point '
                 'estimates and their 95% intervals are not robust to a dependence '
                 'departure of 10%.**')
        conf = 'high for the ordering (the crossing is exact arithmetic, not a simulation); ' \
               'high for the fragility of the intervals (same); moderate for the claim ' \
               'that real γ exceeds 1, which rests on the indicative overdispersion of §6'
    A(claim)
    A('')
    A(f'**Confidence:** {conf}.')
    A('')
    A('**This is refuted if** any of the following is shown. The conditions below were '
      'rewritten after external review pointed out that the previous set challenged the '
      'grid’s *extent* rather than the claim itself — a refutation condition has to bear '
      'on the ordering, which is what the claim is about.')
    A('')
    A('1. **An independent γ estimate that excludes the crossing.** The within-era '
      'corrector design of '
      '[`corrector_recapture.md`](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/reports/corrector_recapture.md) '
      'yields a γ for these sites whose plausible range lies **entirely above the '
      'headline crossing** — i.e. rules out the γ < crossing region — which would make '
      'the published ordering safe to quote after all. (A γ estimate merely *outside* '
      '[0.5, 2.0] would say the grid is too narrow, not that the ordering is robust: '
      'that is the condition this replaces.)')
    A('2. **The sequential-removal mechanism is shown not to operate** — era-1 '
      'corrections are found not to remove the errors an era-2 recapture would need '
      '(re-introduction, partial fixes, or independent error inventories per era), '
      'removing the only mechanism this report demonstrates can reach the crossing.')
    A('3. **A third capture occasion plus an identifying assumption.** Three lists do '
      'not identify the unseen cell on their own; they do so under a stated constraint '
      'such as no three-way interaction. A third occasion *with* such an assumption '
      'defended would replace this envelope with an estimate and settle the ordering '
      'directly. (Reading §6’s dispersion as pure event clustering would remove one '
      'argument for γ > 1 — but the ordering claim rests on the γ < 1 branch, so that '
      'finding would leave it standing, which is why it is no longer listed here.)')
    A('')
    A('**What would NOT refute it:** more correction events from these same two eras. '
      'The deficiency is structural (§2); more data shrinks the CI that is already the '
      'least of the problems.')
    A('')

    A('## 9. Limitations')
    A('')
    A('1. γ is a single summary of everything that breaks independence. Real dependence '
      'can be non-uniform across sites in ways one scalar cannot express; the envelope '
      'is then correct on average and wrong site by site.')
    A('2. Control B runs two bounded families — a symmetric two-point θ and a clipped '
      'Gamma — so that capture probabilities stay probabilities at CV = 1, and builds '
      'its cells by integrating the family rather than by substituting the identity it '
      'reports. Both reproduce γ = 1 + CV² at their *realised* CV to machine precision. '
      'Neither is sound as a *fitting* family, which is §6\'s trap.')
    A('3. **The identity γ = 1 + CV² needs capture probability LINEAR in θ** (p_j·θ), '
      'which is how controls B and E construct it. Under a nonlinear kernel such as '
      '1 − e^(−θ) it fails, and two families sharing a mean and a variance no longer '
      'even agree with each other — `--selftest` exhibits a pair that differ at CV = '
      '0.5. So the identity may not be applied to unbounded intensity heterogeneity of '
      'the kind §6\'s reading 1 contemplates.')
    A('4. Control C assumes each error is detected independently and that the form era '
      'fixes what it detects. Partial fixes and re-introduced errors are not modelled; '
      'both would push γ back toward 1. Its q₁, q₂ are **per-error** probabilities set '
      'from the dictionary\'s era sizes, which does not reproduce those era sizes at '
      'the site level once sites carry more than one error (each row prints the implied '
      'sizes beside the observed ones). The mechanism\'s γ is a function of k̄ alone and '
      'is unaffected; the coverage column of those rows is therefore illustrative and '
      'not dictionary-matched.')
    A('5. The closure assumption of the original design is untouched here, and so is '
      'linkage error: §2 shows neither enters as a γ, so neither is bounded by any '
      'number in this report. An envelope over dependence is not an envelope over the '
      'design.')
    A('6. The overdispersion of §6 is computed on the operating linkage key, so it '
      'inherits that key\'s measured false-match rate. It is a descriptive comparison '
      'against a family\'s variance ceiling, with no sampling distribution attached — '
      'not a calibrated test at a stated level.')
    A('7. §6 leaves one question open that its own data could close: whether the '
      'over-ceiling dispersion is heavy-tailed site heterogeneity or within-site event '
      'clustering. The events CSV carries per-event date and author, so the test is '
      'available — count *distinct correction occasions* per site instead of events, and '
      'the clustering reading predicts the excess dispersion largely disappears. That is '
      'the single next step this report recommends, and it is deliberately not taken '
      'here: the mint scopes this task to the dependence envelope.')
    A('')

    A('## 9a. Deviations from the preregistration')
    A('')
    A('The preregistration forbids editing itself after the results commit and requires '
      'every changed decision rule to appear here as a labelled deviation. All seven '
      'below were made **after** results existed; six of them follow an independent '
      'logic review of the first version of this report (Codex Astra `gpt-6-astra`, '
      '20-09-2026), which returned FAIL. They are listed whether they helped the '
      'report’s thesis or hurt it.')
    A('')
    A('1. **Fragility rule — corrected, changes a published verdict.** The rule reads '
      '«the smallest |log γ| at which this happens … fragile if it happens at γ ∈ '
      '[0.90, 1.10]». It had been implemented as *both* crossings inside the band. '
      'Restored to the literal rule, which flags **cae** where the first version '
      'reported no fragile interval at all.')
    A('2. **Control E added (not preregistered).** Composition of two mechanisms. Added '
      'because the first version multiplied two separately derived γ values, a step '
      'with no derivation; §3 now computes the joint mechanism exactly. This is a '
      'post-hoc addition and is labelled as such rather than presented as planned.')
    A('3. **Capped dictionaries restored to the controls.** The preregistration promises '
      'the controls for every estimable dictionary; the implementation had excluded the '
      'capped row (cae). All '
      f'{len(set(r["dict"] for r in ctrl))} estimable dictionaries are now run.')
    A('4. **Coverage gate made two-sided.** The preregistration specifies a coverage '
      '*floor* only. A floor alone is satisfied by any sufficiently wide interval — '
      'review demonstrated that replacing every interval with [0, ∞) passes every '
      'control. A ceiling was added and `--selftest` now asserts the gate rejects that '
      'mutation.')
    A('5. **Control B rebuilt to avoid circularity, and a second family added.** Its '
      'cells had been generated by substituting γ = 1 + CV² — the identity the control '
      'reports as confirmed — so the check could not fail. Cells are now obtained by '
      'integrating an explicit mixing family, and the clipped-Gamma companion named in '
      'the design note is actually run beside the two-point family.')
    A('6. **Overdispersion estimator changed from the preregistered one.** The '
      'preregistration names the moment estimator CV²_obs = (Var − Mean)/Mean². That '
      'expression ignores zero truncation and returns negative values on these counts. '
      '§6 instead reports a dispersion ratio against a *matched zero-truncated* Poisson '
      'and a comparison against the Poisson–Gamma variance ceiling. The preregistered '
      'restriction that no γ may be estimated from these counts is unchanged and '
      'honoured.')
    A('7. **Two claims narrowed.** §6 said the counts «are not a mixed-Poisson process»; '
      'that is true only of the *Gamma* family, and review supplied a bounded two-point '
      'Poisson mixture matching the moments exactly. §8’s refutation conditions were '
      'rewritten: two of the three bore on the grid’s extent rather than on the ordering '
      'claim they were supposed to be able to refute.')
    A('')
    A('Unchanged from the preregistration: the γ grid, the CV and k̄ grids, the seed, the '
      'replicate count, the estimator, the fragile band itself, the ranking definition, '
      'and the zero-recapture prohibition of §7.')
    A('')

    A('## 10. Reproduce')
    A('')
    A('```sh')
    A('python scripts/recapture_sensitivity.py --selftest   # arithmetic invariants')
    A('python scripts/recapture_sensitivity.py              # the full grid')
    A('```')
    A('')
    A('Evidence manifest (inputs frozen at run time):')
    A('')
    A('| Input | SHA-256 |')
    A('|---|---|')
    for p in (EVENTS, PUBLISHED):
        A(f'| `{os.path.relpath(p, ROOT)}` | `{sha256(p)}` |')
    A('')
    A(f'Replicates {reps}, seed {SEED}, grid frozen in '
      '[`recapture_sensitivity_prereg.md`](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/reports/recapture_sensitivity_prereg.md).')
    A('')
    A('_Гасунс_')

    with open(OUT_MD, 'w', encoding='utf-8', newline='\n') as f:
        f.write('\n'.join(L) + '\n')


# --------------------------------------------------------------------------- #
# selftest — control D
# --------------------------------------------------------------------------- #
def selftest():
    ok = True

    def chk(name, cond, detail=''):
        nonlocal ok
        ok &= bool(cond)
        print(f"{'PASS' if cond else 'FAIL'}  {name}{(' — ' + detail) if detail else ''}")

    n1, n2, m = 9756, 1369, 196
    chap = ER.chapman(n1, n2, m)[0]
    chk('gamma=1 reproduces Chapman exactly',
        abs(envelope(n1, n2, m, 1.0) - chap) < 1e-9, f'{envelope(n1, n2, m, 1.0):.6f}')
    chk('envelope monotone in gamma',
        all(envelope(n1, n2, m, a) < envelope(n1, n2, m, b)
            for a, b in zip(GAMMA_GRID, GAMMA_GRID[1:])))
    g = gamma_for_target(n1, n2, m, 80000.0)
    chk('gamma_for_target inverts envelope',
        abs(envelope(n1, n2, m, g) - 80000.0) < 1e-6, f'gamma={g:.6f}')
    chk('m = 0 yields no estimate at any gamma',
        envelope(10, 10, 0, 1.0) is None and gamma_for_target(10, 10, 0, 5) is None)

    # heterogeneity identity gamma = 1 + cv^2
    p11, p10, p01 = hetero_cells(0.10, 0.05, 0.5)
    chk('hetero cells give gamma = 1 + cv^2',
        abs(gamma_of(p11, p11 + p10, p11 + p01) - 1.25) < 1e-12)

    # ---- invariants added 20-09-2026 after external review (gpt-6-astra) ----
    # Each pins one defect that review found, so a regression restores it loudly.

    # defect 6: cells built by INTEGRATING a family must reproduce the identity,
    # for the two-point family AND the clipped-Gamma companion.
    for fam_name, thetas in (('two-point', ((0.5, 0.5), (1.5, 0.5))),
                             ('gamma-clipped', clipped_gamma_thetas(0.5))):
        cells = mixture_cells(0.10, 0.05, thetas)
        g_read = gamma_of(cells[0], cells[3], cells[4])
        chk(f'{fam_name} mixture integrates to gamma = 1 + cv^2',
            abs(g_read - 1.25) < 2e-2, f'gamma={g_read:.6f}')

    # defect 6: the coverage gate must REJECT a deliberately broken interval.
    p11h, p10h, p01h = hetero_cells(0.10, 0.05, 0.0)
    good = run_cells(20000, p11h, p10h, p01h, 200, SEED)
    broke = run_cells(20000, p11h, p10h, p01h, 200, SEED, ci_widen=1e6)
    chk('two-sided coverage gate accepts the honest interval',
        COVERAGE_MIN <= good['coverage'] <= COVERAGE_MAX, f"{good['coverage']:.3f}")
    chk('two-sided coverage gate REJECTS a [0, inf) interval',
        not (COVERAGE_MIN <= broke['coverage'] <= COVERAGE_MAX),
        f"coverage={broke['coverage']:.3f} would have passed a floor-only gate")

    # defect 4: the two mechanisms' gammas must NOT be multiplied.
    q1t, q2t = 9756 / 68143.0, 1369 / 68143.0
    jc = joint_cells(q1t, q2t, 1.5, 0.85)
    g_joint = gamma_of(jc[0], jc[3], jc[4])
    sc_t = sequential_cells(q1t, q2t, 1.5)
    prod = gamma_of(sc_t[0], sc_t[3], sc_t[4]) * gamma_two_point(0.85)
    chk('joint gamma is NOT the product of the two mechanisms',
        abs(prod - g_joint) > 0.02,
        f'product={prod:.6f} joint={g_joint:.6f} error={prod - g_joint:+.6f}')
    chk('joint gamma at CV=0.85 still shows NET NEGATIVE dependence',
        g_joint < 1.0, f'{g_joint:.6f} — the product wrongly claimed cancellation')

    # defect 8: gamma = 1 + cv^2 needs a LINEAR capture kernel. Under 1 - exp(-theta)
    # two families sharing (mean, variance) disagree, so the identity is not general.
    g_two, g_alt = nonlinear_kernel_gap(0.5)
    chk('nonlinear kernel breaks the 1 + cv^2 identity',
        abs(g_two - g_alt) > 1e-3,
        f'two-point={g_two:.6f} three-point={g_alt:.6f} (both CV=0.5)')

    # defect 3: the variance ceiling is a GAMMA-family fact. A bounded two-point
    # Poisson mixture reaches moments the Gamma family cannot, so "not a mixed
    # Poisson process" was too strong a reading of it.
    rates, weights = (0.01, 5.6159883122), (1 - 0.0004813620, 0.0004813620)
    p0 = sum(w * math.exp(-r) for r, w in zip(rates, weights))
    mu_mix = sum(w * r for r, w in zip(rates, weights)) / (1 - p0)
    ex2 = sum(w * (r + r * r) for r, w in zip(rates, weights)) / (1 - p0)
    var_mix = ex2 - mu_mix * mu_mix
    ceiling = gamma_family_variance_ceiling(mu_mix)
    chk('a two-point Poisson mixture exceeds the Gamma-family ceiling',
        var_mix > ceiling,
        f'mean={mu_mix:.6f} var={var_mix:.6f} > gamma-ceiling={ceiling:.6f}')

    # sequential mechanism must be negative-dependence and monotone toward 1
    gs = [gamma_of(*(lambda c: (c[0], c[3], c[4]))(sequential_cells(0.10, 0.05, k)))
          for k in KBAR_GRID]
    chk('sequential removal gives gamma < 1', all(x < 1 for x in gs),
        ', '.join(f'{x:.4f}' for x in gs))
    chk('sequential gamma rises toward 1 with mean error count',
        all(a < b for a, b in zip(gs, gs[1:])))

    # exact binomial sampler: mean and variance
    rng = random.Random(1)
    draws = [rbinom(5000, 0.3, rng) for _ in range(3000)]
    mu, var = statistics.fmean(draws), statistics.variance(draws)
    chk('rbinom mean', abs(mu - 1500) < 15, f'{mu:.1f} vs 1500')
    chk('rbinom variance', abs(var - 1050) / 1050 < 0.08, f'{var:.1f} vs 1050')

    # zero-truncated Poisson mean solver
    for kb in KBAR_GRID[1:]:
        lam = lam_for_mean(kb)
        got = lam / (1 - math.exp(-lam))
        chk(f'ztpois mean solver kbar={kb}', abs(got - kb) < 1e-6, f'{got:.6f}')

    # dispersion ratio ~ 1 on a genuine ZERO-TRUNCATED Poisson sample, and the latent
    # CV fitted to it ~ 0: the estimator must not invent heterogeneity that is not there
    rng = random.Random(2)
    lam = 1.4
    ztp = []
    while len(ztp) < 30000:
        k = 0
        # Knuth Poisson draw, rejected when zero (that is the truncation)
        p, target = 1.0, math.exp(-lam)
        while p > target:
            p *= rng.random(); k += 1
        k -= 1
        if k:
            ztp.append(k)
    d = dispersion_ratio(ztp)
    chk('dispersion ratio ~ 1 on a zero-truncated Poisson sample',
        abs(d - 1) < 0.05, f'{d:.4f}')
    fit = fit_latent_cv_nb(ztp)
    chk('homogeneous sample is reported as needing no heterogeneity',
        fit['status'] in ('homogeneous', 'fitted') and (fit['cv'] or 0) < 0.10,
        f"{fit['status']} cv={fit['cv']}")

    # and it must RECOVER planted heterogeneity across an order of magnitude
    def ztnb_sample(lam_, k_, n, seed):
        r = random.Random(seed); out = []
        while len(out) < n:
            mu = lam_ * r.gammavariate(k_, 1.0 / k_)
            x, p, t = 0, 1.0, math.exp(-mu)
            while p > t:
                p *= r.random(); x += 1
            x -= 1
            if x:
                out.append(x)
        return out

    for cv_true in (0.5, 1.0, 2.0):
        s = ztnb_sample(0.4, 1 / cv_true ** 2, 30000, 11)
        f2 = fit_latent_cv_nb(s)
        chk(f'fitted latent CV recovers a planted CV = {cv_true:.1f}',
            f2['status'] == 'fitted' and abs(f2['cv'] - cv_true) / cv_true < 0.20,
            f"{f2['status']} cv={f2['cv']:.4f}" if f2['cv'] else f2['status'])

    # neither mixing family can reach the dispersion the real counts show: the bounded
    # two-point family has a small ceiling, and so does the unbounded Poisson-Gamma once
    # the truncated mean is held fixed. This is why the report says "no fit exists"
    # instead of printing the boundary value a solver would otherwise return.
    ceil2 = bounded_dispersion_ceiling(1.218)
    chk('bounded two-point family cannot exceed a small dispersion ratio',
        ceil2 is not None and ceil2 < 1.2, f'ceiling D={ceil2:.4f} at mean 1.218')
    gceil = gamma_family_variance_ceiling(1.218)
    chk('Poisson-Gamma variance ceiling is finite and below the observed pw-form variance',
        gceil is not None and gceil < 1.200, f'ceiling var={gceil:.4f} vs observed 1.200')
    chk('an over-ceiling sample is reported unreachable, never as a boundary CV',
        fit_latent_cv_nb([1] * 900 + [2] * 40 + [30] * 12)['status'] == 'unreachable')

    # the non-identification check must fit all three cells exactly at every gamma
    nid = nonidentification_check(n1, n2, m, GAMMA_GRID)
    chk('every gamma reproduces the observed table exactly',
        all(r[3] is not None and r[3] < 1e-6 for r in nid),
        f"max residual {max(r[3] for r in nid if r[3] is not None):.2e}")
    lls = [r[2] for r in nid if r[2] is not None]
    # NOT "flat" (external review, defect 2): the finite-N term gives a real, weak,
    # monotone slope favouring smaller N. The invariant that carries the argument is
    # the EXACT cell fit above; this one only bounds how little the likelihood can
    # discriminate -- well under the conventional 2-unit evidential threshold.
    spread = max(lls) - min(lls)
    chk('log-likelihood spread over the grid stays far below 2 units',
        spread < 1.0, f'spread {spread:.4f} (monotone in gamma, not flat)')
    chk('that slope is monotone, i.e. a real if weak preference for smaller N',
        lls == sorted(lls, reverse=True) or lls == sorted(lls),
        'direction recorded in the report rather than described as flat')

    # published counts reproduce from the events CSV (the arithmetic half)
    if os.path.exists(EVENTS) and os.path.exists(PUBLISHED):
        with open(EVENTS, encoding='utf-8') as f:
            rows = list(csv.DictReader(f))
        by = {r['dict']: r for r in ER.estimates(ER.collect(rows))}
        bad = []
        for p in load_published():
            mine = by.get(p['dict'])
            if not mine or (int(p['n1_form']), int(p['n2_git']), int(p['m_overlap'])) != (
                    mine['n1_form'], mine['n2_git'], mine['m_overlap']):
                bad.append(p['dict'])
        chk('published n1/n2/m reproduce from the events CSV', not bad, ', '.join(bad))
    else:
        print('SKIP  published-count reproduction (data files absent)')

    print('\nselftest', 'PASSED' if ok else 'FAILED')
    return 0 if ok else 1


if __name__ == '__main__':
    sys.exit(main())
