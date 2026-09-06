# How much correction work is left? A capture–recapture estimate of residual error populations in the Cologne Digital Sanskrit Lexicon

_Created: 03-07-2026 · Last updated: 06-09-2026_

**Status: readiness 3/5 (method complete, two designs, external validation outstanding). ID: A48.**

## Claim

Treating the CDSL's two historical correction channels (2014–2019 web-form submissions; 2019–2026 git commits) as two capture occasions over error-prone dictionary records, Chapman mark–recapture estimation shows that the twelve-year correction effort has completed only ~5–16% of the estimated work in the four estimable dictionaries (PW ~16%, MW ~11%, BUR ~10%, CAE ~5%) — the first quantitative answer to "how much proofreading remains" for any retro-digitised dictionary, with the method transferable to any correction-logged digital edition.

Two methodological results carry the paper beyond the headline number. First, **the linkage instrument is part of the finding**: the two eras spell headwords differently (ASCII fallbacks, SLP1 residue, homonym digits), and joining them by exact string silently loses recaptures and inflates the estimate — while the obvious cure, edit-distance matching, is worse, since 70–98% of its links join real, distinct lemmas in a language whose headword lists are dense with minimal pairs. A measured ladder of linkage keys, each scored for false matches against the dictionaries' own inventories, is what makes the estimate defensible. Second, **a second, independent design** — correctors within one era as capture occasions — cross-checks the two-era figure at the same order of magnitude and gives population estimates for dictionaries the two-era design cannot reach at all.

## Data inventory

| Intended result | Committed artifact | Status |
|---|---|---|
| Per-dictionary Chapman N̂ + CI + Chao heterogeneity scenario (pw/mw/bur/cae) | [`observatory/site/src/data/error_recapture.csv`](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/observatory/site/src/data/error_recapture.csv) | exists |
| Method + sensitivity analyses (component key, campaign exclusion, exact-vs-linked join) | [`reports/error_recapture.md`](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/reports/error_recapture.md) | exists |
| Generator (offline, stdlib, reproducible) | [`scripts/error_recapture.py`](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/scripts/error_recapture.py) | exists |
| Underlying event corpus (52,498 events, DOI-backed) | [`correction_events_final.csv`](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/observatory/site/src/data/correction_events_final.csv) + [10.5281/zenodo.21346705](https://doi.org/10.5281/zenodo.21346705) | exists (released with A12) |
| Record-count denominators for ALL dicts (not just 3) | [`dict_record_counts.csv`](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/observatory/site/src/data/dict_record_counts.csv) — 44 csl-orig v02 dictionaries | exists (H1477) |
| Record-linkage of the two eras' headwords, with a measured false-match rate | [`scripts/headword_linkage.py`](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/scripts/headword_linkage.py) + [`linkage_ladder.csv`](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/observatory/site/src/data/linkage_ladder.csv) + [`headword_key_collisions.csv`](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/observatory/site/src/data/headword_key_collisions.csv) | exists (H1477) |
| Within-era corrector-pair recapture (validates against the two-era design) | [`scripts/corrector_recapture.py`](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/scripts/corrector_recapture.py) + [`reports/corrector_recapture.md`](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/reports/corrector_recapture.md) | exists (H1477) |
| Below-floor estimator comparison + calibrated bands (four candidate families scored against pw/mw/bur under a pre-registered rule) | [`scripts/lowm_estimators.py`](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/scripts/lowm_estimators.py) + [`reports/error_recapture_lowm.md`](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/reports/error_recapture_lowm.md) + [`error_recapture_calibrated.csv`](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/observatory/site/src/data/error_recapture_calibrated.csv) | exists (H3986) |
| External validation: error rate on a random record sample vs model prediction | — | needs deriving + HUMAN annotation (small gold sample; ties into the A12 second-annotator recruit) — the one gate between 3/5 and 4/5 |

## Outline

- **Introduction** — proofreading endpoints are unknown for every retro-digitised dictionary; correction logs are by-catch data that can answer it.
- **Related work** — mark–recapture beyond ecology: software defect estimation (capture–recapture code review), record-linkage census estimation, OCR error-rate estimation; digital-lexicography quality literature (link to A12's related-work base).
- **Data** — the OBS-T corpus, two-era structure, site definition (dict + headword record).
- **Method I: linkage** — the two eras' orthographies; the key ladder (`exact` → `clean` → `repair` → `form_key` → `norm` → `ed1`); the two offline false-match measurements (key-collision rate against the dictionary's own inventory; attestation test on the matched pairs); why the length-preserving fold is the operating level and why edit distance is not. The section doubles as a transferable warning for record linkage over any morphologically dense headword list.
- **Method II: estimation** — Chapman estimator, CI; assumption violations stated as first-class results (sequential occasions, heterogeneous catchability, imperfect closure) with bias directions; record-count capping; Chao scenario as range end.
- **Method III: the second design** — correctors within one era as occasions; identity resolution (aliases, joint cells); pairwise Chapman and Chao2 incidence; what the comparison can and cannot settle.
- **Results** — per-dictionary estimates; the near-disjointness of the two eras as the central empirical fact; the non-estimable dictionaries as a finding about effort concentration; the two designs side by side.
- **Sensitivity** — component-in-key, campaign exclusion, exact-vs-linked join, joint-cell treatment.
- **Implications** — planning correction campaigns; what "done" could mean for CDSL; transferability to other correction-logged editions.

## Results tables

Two tables, deliberately kept apart. The first carries mark–recapture estimates; the
second carries numbers that are *not* mark–recapture estimates and must never be read as
if they were. Keeping them in one table with a flag column would invite exactly that
misreading, which is why they are separated here and why the second carries its warrant in
its own caption (MG ruling, 06-09-2026: «в таблицу» — the calibrated bands are published,
in a table of their own).

**Table 1. Chapman mark–recapture estimates, dictionaries at or above the m ≥ 10 recapture
floor.** N̂ is the Chapman bias-corrected Lincoln–Petersen estimate over the two correction
eras (2014–2019 web-form submissions; 2019–2026 git commits), joined at the `form_key`
linkage level; the interval is the Chapman CI. CAE is capped at its own record count.
Source: [`error_recapture.csv`](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/observatory/site/src/data/error_recapture.csv).

| Dict | n₁ (form era) | n₂ (git era) | m | Sites seen | N̂ | 95% CI | Corrected | Remaining |
|---|---:|---:|---:|---:|---:|---|---:|---:|
| PW | 9,756 | 1,369 | 196 | 10,929 | 67,852 | 59,196–76,509 | 16.1 % | 56,923 |
| MW | 1,443 | 5,575 | 131 | 6,887 | 60,997 | 51,233–70,761 | 11.3 % | 54,110 |
| BUR | 877 | 883 | 44 | 1,716 | 17,247 | 12,517–21,977 | 10.0 % | 15,531 |
| CAE | 1,824 | 339 | 13 | 2,150 | 40,069 | 22,442–40,069 | 5.4 % | 37,919 |

**Table 2. Calibrated below-floor estimates — NOT mark–recapture estimates.** Each N̂ here is
a raw Chapman value divided by a measured small-sample correction factor, not an estimate
any recapture estimator produced. The factor is the median downward shift Chapman shows
when PW, MW and BUR — the only three dictionaries where the true answer is known — are
thinned to the same recapture count: ×0.52 at m = 1, ×0.69 at m = 2, ×0.84 at m = 5. The
calibration rests on those **three dictionaries only**; it generalises because the three
agree to within ×1.09 at every rung, and it has never been tested against a fourth. The
band is the interquartile range of the thinning distribution, capped at the dictionary's
record count where that binds (SKD's upper end is its record count, 42,531). These five are
the dictionaries that gain a genuinely new bounded estimate; seven further dictionaries with
1 ≤ m < 10 cap out at their own record count and are reported as *unproofread* rather than
estimated, and the 26 dictionaries with m = 0 are not estimated at all. Source:
[`error_recapture_calibrated.csv`](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/observatory/site/src/data/error_recapture_calibrated.csv),
method in [`reports/error_recapture_lowm.md`](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/reports/error_recapture_lowm.md).

| Dict | m | Sites seen | Chapman raw | Factor | N̂ calibrated | Band | Corrected | Remaining |
|---|---:|---:|---:|---:|---:|---|---:|---:|
| SKD | 2 | 624 | 20,957 | ×0.686 | 30,536 | 10,773–42,531 | 2.0 % | 29,912 |
| STC | 5 | 245 | 2,441 | ×0.842 | 2,898 | 1,478–4,630 | 8.5 % | 2,653 |
| AE | 2 | 211 | 1,181 | ×0.686 | 1,721 | 607–3,210 | 12.3 % | 1,510 |
| MWE | 1 | 153 | 3,039 | ×0.521 | 5,828 | 2,698–11,678 | 2.6 % | 5,675 |
| INM | 2 | 121 | 1,187 | ×0.686 | 1,730 | 610–3,227 | 7.0 % | 1,609 |

The bands are wide by construction and should be quoted as bands, never as point
estimates: on the "corrected" column they run 1.5–5.8 % for SKD and 6.6–34.8 % for AE. What
Table 2 supports is a planning statement — every one of these five dictionaries is early in
its correction life — not a per-dictionary figure of record.

## Comparanda / literature

- Eick, Loader et al. on capture–recapture for software-inspection defect estimation (the closest methodological analog: reviewers = correctors).
- Chao (1987), Chapman (1951) — estimator sources.
- Piotrowski (2012), Reul et al. (2019) on OCR/digitisation error rates — the field the number lands in.

## Venue candidates

Digital Scholarship in the Humanities, or International Journal of Lexicography (methods note); LREC-COLING resource-paper track if bundled with A12's corpus release. Serious shortlist = `/venue-scout A48` later.

## Open questions

- **The "more estimable dictionaries" bet did not pay off the way it was framed.** The linkage was expected to lift several dictionaries over the m ≥ 10 recapture floor; under a key with a measured false-match rate it lifts exactly one (CAE, m 1 → 13). Raising the others would need a key that merges distinct lemmas, and the measurement says what that costs. The finding stands on its own — the two eras really are near-disjoint — but it means the two-era design will not scale to the whole CDSL, and the within-era design is the more promising route for the remaining dictionaries.
- **"Use a different estimator for the rest" is now answered, and the answer is mostly no** (H3986, 06-09-2026 — [`reports/error_recapture_lowm.md`](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/reports/error_recapture_lowm.md)). Four candidate families were scored against pw, mw and bur under a rule fixed before the numbers were read. Every estimator that *borrows strength across dictionaries* — pooled prevalence, correction-density extrapolation — misses the known answers by ×0.35 to ×3.4, and the reason is structural rather than technical: error-site prevalence across the three dictionaries where the truth is known spans a factor of 4.1, so the exchangeability those estimators require is false. Chao2 over the two eras and Chao2 over correctors fail too (×1.02–×2.33, ×0.96–×2.17). An empirical-Bayes shrinkage estimator passed the rule and was rejected on inspection: its prior contributes under 7% of the estimate, so it is Lincoln–Petersen in disguise and needs exactly the overlap the below-floor dictionaries lack. **This is a publishable negative result with a control** — it converts "we need a better estimator" into a measured ceiling.
- **The m ≥ 10 floor itself turned out to be the softer target, and this is the paper's second methodological result.** Thinning pw, mw and bur to sub-floor sample sizes shows Chapman is not incoherent below the threshold but median-shifted by a factor that depends on the sample size and almost not at all on the dictionary (×0.54 at m = 1, ×0.69 at m = 2, ×0.88 at m = 5; the three agree within 9% at every rung). Dividing the measured shift out gives five dictionaries (`skd`, `stc`, `ae`, `mwe`, `inm`) their first bounded estimate, and labels seven more unproofread on the cap argument. The 26 dictionaries with m = 0 remain unreachable by any estimator over these events — that is a data limit, not a method gap, and the paper should say so rather than leave it open. Generalisable claim for the methods literature: **a recapture floor should be published as a calibrated correction curve, not as a discard threshold.** Whether the five calibrated bands belong in the paper's tables at all was a genuine editorial fork — a calibrated band is not a recapture estimate, and a reviewer may read it as one despite a label. **Ruled 06-09-2026 (MG, «в таблицу»): they are published**, as Table 2 above — a table of their own, with the calibration and its three-dictionary basis stated in the caption rather than in a footnote, so the claim and its warrant sit in one eyeline. What would reverse it: a fourth Chapman-computable dictionary whose median shift falls outside the ×1.09 agreement band the calibration rests on.
- **Structured division of labour** is not repaired by any incidence estimator: if two correctors split a dictionary alphabetically they are not sampling one population. Measuring the overlap structure of corrector territories is the natural next step.
- **External validation** (a small annotated random sample against the model's predicted error rate) remains the one thing no amount of re-analysis of the correction log can substitute for.

## Provenance

Scaffolded 03-07-2026 by Fable 5 (`claude-fable-5`) executing [H089](https://github.com/gasyoun/Uprava/blob/main/handoffs/archive/H089-Fable_csl-observatory_obs_capture_recapture_03.07.26.md); analysis shipped same session (commit `acd8687`).

Tabled 06-09-2026 by Opus 5 (`claude-opus-5`): the **Results tables** section above, on MG's ruling «в таблицу» that day. Table 1 restates the Chapman estimates; Table 2 publishes the five calibrated below-floor bands separately, with the calibration's three-dictionary basis and its ×1.09 agreement band in the caption rather than a footnote. The separation is the substance of the ruling's execution — a calibrated band is arithmetic on a Chapman value, not an estimator's output, and one table with a flag column would have blurred that.

Extended 06-09-2026 by Opus 5 (`claude-opus-5`) executing [H3986](https://github.com/gasyoun/Uprava/blob/main/handoffs/archive/H3986-Opus_csl-observatory_error-population-low-recapture-estimator_03.09.26.md): the below-floor estimator comparison against a pre-registered rule, the censoring stress test with Chapman as its control, and the calibrated bands. Readiness held at 3/5 — this closes a stated open question and adds a second methodological result, but external validation remains the gate to 4/5.

Extended 27-07-2026 by Opus 5 1M (`claude-opus-5[1m]`) executing [H1477](https://github.com/gasyoun/Uprava/blob/main/handoffs/archive/H1477-Opus_csl-observatory_capture-recapture-fuzzy-linkage-corrector-pair_22.07.26.md): the measured record-linkage ladder, the record-count sweep over all 44 csl-orig v02 dictionaries, and the within-era corrector-pair design. Readiness 2/5 → 3/5 (all three of the criteria stated for that step are now met; external validation is the remaining gate).

_Dr. Mārcis Gasūns_
