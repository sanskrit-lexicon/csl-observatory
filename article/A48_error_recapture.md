# How much correction work is left? A capture–recapture estimate of residual error populations in the Cologne Digital Sanskrit Lexicon

_Created: 03-07-2026 · Last updated: 03-07-2026_

**Status: readiness 2/5 (skeleton with committed data). ID: A48.**

## Claim

Treating the CDSL's two historical correction channels (2014–2019 web-form submissions; 2019–2026 git commits) as two capture occasions over error-prone dictionary records, Chapman mark–recapture estimation shows that the twelve-year correction effort has completed only ~10–14% of the estimated work in the three estimable dictionaries (PW, MW, BUR) — the first quantitative answer to "how much proofreading remains" for any retro-digitised dictionary, with the method transferable to any correction-logged digital edition.

## Data inventory

| Intended result | Committed artifact | Status |
|---|---|---|
| Per-dictionary Chapman N̂ + CI + Chao heterogeneity scenario (pw/mw/bur) | [`observatory/site/src/data/error_recapture.csv`](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/observatory/site/src/data/error_recapture.csv) | exists |
| Method + sensitivity analyses (component key, campaign exclusion) | [`reports/error_recapture.md`](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/reports/error_recapture.md) | exists |
| Generator (offline, stdlib, reproducible) | [`scripts/error_recapture.py`](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/scripts/error_recapture.py) | exists |
| Underlying event corpus (52,498 events, DOI-backed) | [`correction_events_final.csv`](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/observatory/site/src/data/correction_events_final.csv) + [10.5281/zenodo.15834721](https://doi.org/10.5281/zenodo.15834721) | exists (released with A12) |
| Record-count denominators for ALL 43 dicts (not just 3) | — | needs deriving (`grep -c "^<L>"` sweep over `csl-orig/v02/*`; extend `RECORD_COUNTS`) |
| Fuzzy headword matching to raise two-era overlap (more estimable dicts) | — | needs deriving (Phase 3.1 fuzzy-join machinery exists in `scripts/attribute_components.py`; port to site keys) |
| Within-era corrector-pair recapture (validates against the two-era design) | — | needs deriving (corrector column supports multi-occasion Mth models) |
| External validation: error rate on a random record sample vs model prediction | — | needs deriving + HUMAN annotation (small gold sample; ties into the A12 second-annotator recruit) |

## Outline

- **Introduction** — proofreading endpoints are unknown for every retro-digitised dictionary; correction logs are by-catch data that can answer it.
- **Related work** — mark–recapture beyond ecology: software defect estimation (capture–recapture code review), record-linkage census estimation, OCR error-rate estimation; digital-lexicography quality literature (link to A12's related-work base).
- **Data** — the OBS-T corpus, two-era structure, site definition (dict + headword record).
- **Method** — Chapman estimator, CI; assumption violations stated as first-class results (sequential occasions, heterogeneous catchability, imperfect closure) with bias directions; record-count capping; Chao scenario as range end.
- **Results** — per-dictionary estimates; the near-disjointness of the two eras as the central empirical fact; the 40 non-estimable dictionaries as a finding about effort concentration.
- **Sensitivity** — component-in-key, campaign exclusion, fuzzy matching (once derived).
- **Implications** — planning correction campaigns; what "done" could mean for CDSL; transferability to other correction-logged editions.

## Comparanda / literature

- Eick, Loader et al. on capture–recapture for software-inspection defect estimation (the closest methodological analog: reviewers = correctors).
- Chao (1987), Chapman (1951) — estimator sources.
- Piotrowski (2012), Reul et al. (2019) on OCR/digitisation error rates — the field the number lands in.

## Venue candidates

Digital Scholarship in the Humanities, or International Journal of Lexicography (methods note); LREC-COLING resource-paper track if bundled with A12's corpus release. Serious shortlist = `/venue-scout A48` later.

## Provenance

Scaffolded 03-07-2026 by Fable 5 (`claude-fable-5`) executing [H089](https://github.com/gasyoun/Uprava/blob/main/handoffs/H089_obs_capture_recapture.md); analysis shipped same session (commit `acd8687`).

_Dr. Mārcis Gasūns_
