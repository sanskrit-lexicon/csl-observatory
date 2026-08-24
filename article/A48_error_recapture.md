# How much correction work is left? A capture–recapture estimate of residual error populations in the Cologne Digital Sanskrit Lexicon

_Created: 03-07-2026 · Last updated: 27-07-2026_

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

## Comparanda / literature

- Eick, Loader et al. on capture–recapture for software-inspection defect estimation (the closest methodological analog: reviewers = correctors).
- Chao (1987), Chapman (1951) — estimator sources.
- Piotrowski (2012), Reul et al. (2019) on OCR/digitisation error rates — the field the number lands in.

## Venue candidates

Digital Scholarship in the Humanities, or International Journal of Lexicography (methods note); LREC-COLING resource-paper track if bundled with A12's corpus release. Serious shortlist = `/venue-scout A48` later.

## Open questions

- **The "more estimable dictionaries" bet did not pay off the way it was framed.** The linkage was expected to lift several dictionaries over the m ≥ 10 recapture floor; under a key with a measured false-match rate it lifts exactly one (CAE, m 1 → 13). Raising the others would need a key that merges distinct lemmas, and the measurement says what that costs. The finding stands on its own — the two eras really are near-disjoint — but it means the two-era design will not scale to the whole CDSL, and the within-era design is the more promising route for the remaining dictionaries.
- **Structured division of labour** is not repaired by any incidence estimator: if two correctors split a dictionary alphabetically they are not sampling one population. Measuring the overlap structure of corrector territories is the natural next step.
- **External validation** (a small annotated random sample against the model's predicted error rate) remains the one thing no amount of re-analysis of the correction log can substitute for.

## Provenance

Scaffolded 03-07-2026 by Fable 5 (`claude-fable-5`) executing [H089](https://github.com/gasyoun/Uprava/blob/main/handoffs/archive/H089-Fable_csl-observatory_obs_capture_recapture_03.07.26.md); analysis shipped same session (commit `acd8687`).

Extended 27-07-2026 by Opus 5 1M (`claude-opus-5[1m]`) executing [H1477](https://github.com/gasyoun/Uprava/blob/main/handoffs/archive/H1477-Opus_csl-observatory_capture-recapture-fuzzy-linkage-corrector-pair_22.07.26.md): the measured record-linkage ladder, the record-count sweep over all 44 csl-orig v02 dictionaries, and the within-era corrector-pair design. Readiness 2/5 → 3/5 (all three of the criteria stated for that step are now met; external validation is the remaining gate).

_Dr. Mārcis Gasūns_
