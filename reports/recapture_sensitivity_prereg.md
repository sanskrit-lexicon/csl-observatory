_Created: 20-09-2026 · Last updated: 20-09-2026_

# Preregistration — dependence and detectability sensitivity of the recapture conclusions (H5072)

**Frozen before any sensitivity number was computed.** This file is committed in its own
commit, ahead of the commit that adds results, so the ordering is checkable in git history
rather than asserted. Nothing below may be edited after the results commit; a changed
decision rule goes in the results report as a labelled deviation.

- **Source revision under test:** `csl-observatory` @ `3b0a870ed5e7f51f4f11a25d0bf3a59b1b62e029`
  (the revision named in the H5072 mint), re-based for execution on `42b6922` — the two differ
  only outside `scripts/error_recapture.py`, `scripts/lowm_estimators.py` and
  `observatory/site/src/data/correction_events_final.csv`; the exact hashes of the three
  inputs are frozen in the results report's evidence manifest.
- **Estimand:** N_d, the number of records in dictionary *d* harbouring at least one error,
  as published in [`reports/error_recapture.md`](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/reports/error_recapture.md).
- **What is NOT in scope:** a replacement estimator, a new pooled estimate, any claim that a
  zero-recapture dictionary becomes identifiable, and any restatement of the completed
  below-floor study in [`reports/error_recapture_lowm.md`](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/reports/error_recapture_lowm.md).

## 1. The one sensitivity axis, and why it is one

Write the two capture occasions as the form era (1) and the git era (2) over N sites, and
define the **dependence factor**

    γ  =  P(site caught in era 2 | caught in era 1) / P(site caught in era 2)

γ = 1 is independence; γ > 1 is positive dependence (a site the form era found is
*more* likely to be found again); γ < 1 is negative dependence. In expectation
E[n1] = N·p1, E[n2] = N·p2, E[m] = N·p1·p2·γ, so

    N  =  γ · (n1 · n2 / m)          (Petersen form)

i.e. **every** violation of the independence assumption enters the point estimate as a single
multiplicative factor. The published figures are the γ = 1 slice of a one-parameter family.

γ is **not identifiable** from a two-list table: the table has three observable counts
(era-1 only, era-2 only, both) and the model has four parameters (N, p1, p2, γ). The
independence model is already saturated at zero residual degrees of freedom, so the data
cannot prefer any γ over any other. The grid below is therefore an *envelope*, not a fit,
and this is a claim to be proven in the results, not assumed.

## 2. Preregistered grid

| Axis | Levels | Why these |
|---|---|---|
| γ (envelope) | 0.50, 0.60, 0.75, 0.90, **1.00**, 1.10, 1.25, 1.50, 2.00 | Symmetric in log around independence; ±2× brackets the range reported for two-list human-population estimates. |
| Heterogeneity CV (control B) | 0.00, 0.25, 0.50, 0.75, 1.00 | CV of a multiplicative site-level detectability factor θ (E[θ] = 1). |
| Mean errors per site (control C) | 1.0, 1.5, 2.5, 4.0 | Drives the sequential-removal mechanism (era-1 fixes remove the error that would have been recaptured). |
| Replicates | B = 400 per cell | Matches the existing censoring test in `lowm_estimators.py`. |
| Seed | 5072, fixed | Deterministic; the same seed is used for every cell. |
| Dictionaries carried to the envelope | every dictionary in `error_recapture.csv` with `estimable = 1` (pw, mw, cae, bur), plus the below-floor rows for the no-identification statement | The estimable four are the only rows carrying a published point and CI. |

## 3. Controls, each with its pass condition fixed now

**Control A — independent-source recovery (positive control).** Simulate γ = 1, CV = 0,
N and (p1, p2) chosen so that E[n1], E[n2], E[m] match each estimable dictionary's observed
counts. *Passes* if the median Chapman estimate is within 5 % of the true N **and** the
nominal 95 % CI covers the truth in ≥ 90 % of replicates. A failure here means the published
arithmetic — not its assumptions — is wrong, and the rest of the report is void.

**Control B — positively dependent discovery via heterogeneity (negative control).**
Multiplicative heterogeneity θ_i with coefficient of variation CV induces, analytically,
γ = 1 + CV². *Passes* if (i) the simulated γ_eff reproduces 1 + CV² within 5 % at every CV
level, (ii) Chapman's relative bias is negative and matches −CV²/(1 + CV²) within 5 %
absolute, and (iii) the envelope evaluated at γ = 1 + CV² recovers the true N within 5 %.
The coverage of the nominal 95 % CI is recorded at each level; the *prediction* is that it
degrades to below 50 % by CV = 0.5.

**Control C — sequential removal (negative control, opposite sign).** Sites carry k errors;
the form era detects each with probability q1 and **fixes what it detects**; the git era
detects each survivor with probability q2. *Passes* if the simulated γ_eff is < 1 at every
mean-error level and rises monotonically toward 1 as the mean error count rises. This sizes,
for the first time, the upward bias the current report asserts but never quantifies.

**Control D — arithmetic invariants (selftest).** γ = 1 must return the published Chapman
number exactly; the envelope must be monotone in γ; `gamma_for_target` must invert
`envelope` to 1e-9; N(γ) must never be reported below the observed site count S_obs.

## 4. Decision rules, fixed now

1. **"An interval changes"** means: the envelope at a grid γ falls outside the published
   statistical 95 % CI for that dictionary. Report the smallest |log γ| at which this happens
   per dictionary, and call the interval **fragile** if it happens at γ ∈ [0.90, 1.10].
2. **"A ranking changes"** means: the order of dictionaries by `remaining_hat = N − S_obs`
   differs from the published order. Report the γ at which each adjacent pair swaps, both for
   a corpus-common γ and for a dictionary-differential γ ratio.
3. **No-identification for zero recapture is preserved** unless a control produces a finite
   upper bound on N for m = 0 *from the data*, which none of A–D is capable of doing. Any
   such claim in the results is a preregistration violation.
4. **The robustness claim** must be stated as a single falsifiable sentence with a named
   refutation condition and an explicit confidence word (high / moderate / low), and must
   distinguish what is arithmetic, what is assumption, and what the correction histories can
   actually identify.
5. **Overdispersion**: the per-site correction-event counts give a moment estimate
   CV²_obs = (Var − Mean)/Mean². It is reported as an *observable* quantity with its
   confounds named; it is **not** to be presented as a measurement of capture-probability
   heterogeneity, and any γ derived from it is labelled indicative, not estimated.

## 5. Stop budget

Three unsuccessful repair/test cycles without verified progress, or four hours of active
investigation, whichever comes first — then record the remaining uncertainty and one
physical next action, per the H5072 mint.

_Гасунс_
