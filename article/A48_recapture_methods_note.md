# Measuring residual correction work in a retro-digitised dictionary: capture–recapture with a measured record-linkage ladder

_Created: 11-10-2026 · Last updated: 11-10-2026_

**Status: venue-ready methods-note draft (companion artifact, H6390 shape 4). All numbers are restatements of committed artifacts — nothing here is newly derived. Sources: [`article/A48_error_recapture.md`](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/article/A48_error_recapture.md), [`reports/error_recapture.md`](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/reports/error_recapture.md), [`reports/error_recapture_lowm.md`](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/reports/error_recapture_lowm.md), [`reports/corrector_recapture.md`](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/reports/corrector_recapture.md).**

**Target form.** IJL / DSH methods note (~2,500–3,000 words at venue formatting; this draft carries the full content). Alternate track: LREC resource-paper if bundled with the A12 OBS-T corpus release (A48 venue line, ARTICLES.md). External validation remains the readiness gate (3/5) and is stated as such — the note is venue-ready in content, submission-gated on that validation.

## Abstract

"How much proofreading is left?" is unanswerable for every retro-digitised dictionary by direct inspection: the latent error population is unobservable, and correction logs record only what has already been found. We treat the Cologne Digital Sanskrit Lexicon's two historical correction channels — 2014–2019 web-form submissions and 2019–2026 git commits to the source files — as two capture occasions over error-prone dictionary records, and estimate the residual population with the Chapman mark–recapture estimator. The two occasions are near-disjoint (recaptures m ≤ 196 against capture counts in the thousands), so the estimate is large: the twelve-year correction effort has completed an estimated 5–16 % of the work in the four estimable dictionaries (PW ~16 %, MW ~11 %, BUR ~10 %, CAE ~5 %). Two methodological results make the estimate defensible and transfer it. First, the linkage instrument is part of the finding: the two eras spell headwords differently, exact joins silently lose recaptures, and the obvious cure — edit-distance matching — is worse, joining real, distinct lemmas in 70–98 % of links over morphologically dense Sanskrit headword lists. A measured ladder of linkage keys, each scored for false matches against the dictionaries' own inventories, is what makes the estimate trustworthy. Second, an independent design — correctors within one era as capture occasions — cross-checks the two-era figure at the same order of magnitude and yields the first population estimate for PWG (~26,515 error sites), a dictionary the two-era design cannot reach. A pre-registered comparison shows that no estimator borrowing strength across dictionaries reproduces known answers, converting "we need a better estimator" into a measured ceiling; thinning analysis replaces the conventional m ≥ 10 recapture floor with a calibrated correction curve, giving five more dictionaries bounded first estimates.

**Keywords:** digital lexicography; capture–recapture; record linkage; retro-digitisation; quality estimation; correction logs; Sanskrit dictionaries.

## 1. Introduction

Retro-digitised reference works accumulate corrections for decades, and the maintenance question that dominates planning — how much work remains — has never had a quantitative answer. Correction logs are by-catch data: they record discovered errors, never the latent population. Population-estimation methods built for exactly this situation — mark–recapture from ecology — apply whenever the same object can be "captured" by more than one independent detection process. The CDSL correction history provides two such processes with independent origins (a community web form, later git commits by a separate working group), which is the structural precondition for a two-occasion estimate.

The contribution is a methods note in three parts: (i) a per-dictionary estimate of residual correction work over the 52,498-event OBS-T correction corpus [Zenodo DOI 10.5281/zenodo.21346705]; (ii) a measured record-linkage procedure for joining heterogeneous-era correction records, with the false-match cost of every level reported — the piece generalises to any correction log whose eras spell identifiers differently; (iii) a within-era replication design that recovers estimates where the two-era design cannot, plus a pre-registered negative result bounding what further estimator search can deliver.

## 2. Data

The object of analysis is a **correction event** over source text (per `docs/BOUNDARY_RULES.md`): one old→new repair of one microstructure location, drawn from two layers — 24,441 form rows from the 2014–2019 web-form export and 28,057 git rows mined from 2019–2026 correction commits to csl-orig entry files, released as the OBS-T corpus (52,498 events; 43 dictionaries). The **site** is a dictionary-headword record, identified by a `form_key`-normalised headword key. Record-count denominators cover all 44 csl-orig v02 dictionaries (`dict_record_counts.csv`), so estimates can be capped at physical inventory.

## 3. Method

### 3.1 The record-linkage ladder (the load-bearing instrument)

The two eras do not spell headwords alike: form-era cells are hand-typed submissions carrying ASCII fallbacks (`nyancana` for `nyañcana`), homonym digits, pitch accents, and in 3,905 cells raw SLP1 residue (`prakfti`, `āQaka`); git-era cells come from the machine-clean `<k1>` field. Exact-string joins miss true recaptures (each miss inflates N̂); keys that merge distinct lemmas depress it. Sanskrit headword lists are dense with minimal pairs (`kara`/`kāra`, `kṛṣ`/`tṛṣ`, `nāman`/`yāman` — all one edit apart), so fuzzy linkage is not free. The operating level is chosen on two offline measurements taken against the dictionaries' own `<k1>` inventories:

- **collision rate** — the share of a dictionary's own records whose key is shared with another record (an upper bound on key ambiguity); and
- **measured false matches** — matched pairs in which both strings are real, distinct headwords of that dictionary.

The ladder runs `exact` → `clean` → `repair` → `form_key` → `form_key+alias` (operating) → `norm` (rejected) → edit-distance-1 (rejected). `repair` is not fuzzy matching at all: `f/q/w/x/z` cannot occur in IAST, so a cell containing one is provably still in SLP1 and is decoded (`prakfti` → `prakṛti`), not guessed. `form_key` folds anusvāra and homorganic nasals while keeping vowel length and retroflexion; at `form_key` the collision rate is 0.31 % (PW) / 0.25 % (MW) and measured false matches are 0 / 1 / 0 across pw/mw/bur — against 606 / 474 false links for the edit-distance-1 join, a 70–98 % false-link rate. `norm` (all combining marks dropped) is rejected one step earlier: it makes roughly one record in nine ambiguous. The `+alias` layer adds the corrected value of form-era headword-corrections (4,929 events, all `evidence_level = derived`), lifting recaptures to 196 / 131 / 44 without touching the collision rate. **The transferable lesson for record linkage over any morphologically dense headword list: score every level against the inventory you have, publish the false-match cost, and let the measurement pick the operating point.**

### 3.2 Two-occasion estimation

Chapman's bias-corrected Lincoln–Petersen estimator over the two eras, joined at the operating level, with record-count capping and Chao heterogeneity as a range end. Assumption violations (sequential occasions, heterogeneous catchability, imperfect closure) are stated as first-class results with bias directions rather than assumed away.

**Table 1 — Chapman estimates, dictionaries at or above the m ≥ 10 recapture floor** (source: `error_recapture.csv`).

| Dict | n₁ (form) | n₂ (git) | m | Sites seen | N̂ | 95 % CI | Corrected | Remaining |
|---|---:|---:|---:|---:|---:|---|---:|---:|
| PW | 9,756 | 1,369 | 196 | 10,929 | 67,852 | 59,196–76,509 | 16.1 % | 56,923 |
| MW | 1,443 | 5,575 | 131 | 6,887 | 60,997 | 51,233–70,761 | 11.3 % | 54,110 |
| BUR | 877 | 883 | 44 | 1,716 | 17,247 | 12,517–21,977 | 10.0 % | 15,531 |
| CAE | 1,824 | 339 | 13 | 2,150 | 40,069 | 22,442–40,069 | 5.4 % | 37,919 |

The central empirical fact is the near-disjointness of the two eras. A measured key lifted exactly one dictionary over the floor (CAE, m 1 → 13); lifting the rest would require keys that merge distinct lemmas, and §3.1 prices that.

### 3.3 From floor to calibrated curve

Thinning PW, MW and BUR to sub-floor sample sizes shows Chapman below m = 10 is not incoherent but median-shifted by a factor depending almost only on sample size (×0.54 at m = 1, ×0.69 at m = 2, ×0.88 at m = 5; the three dictionaries agree within 9 % at every rung). Dividing the measured shift out gives five below-floor dictionaries (SKD, STC, AE, MWE, INM) their first bounded estimates, published as bands — explicitly *not* mark–recapture estimates, in a table of their own (MG ruling 06-09-2026, «в таблицу»). Seven further dictionaries cap out at their record count and are reported as unproofread; the 26 with m = 0 are not estimated at all. **The generalisable claim: a recapture floor should be published as a calibrated correction curve, not as a discard threshold.** The calibration rests on three dictionaries and would be reversed by a fourth whose median shift falls outside the ×1.09 agreement band.

### 3.4 Within-era replication design

Correctors working the *same* dictionary in the *same* era sample one text state and are closer to genuine replicate occasions. Pairwise Chapman and Chao2 incidence over the 56 dictionary-eras with ≥ 2 usable correctors (51 reportable rows omitted where Q2 < 10 and no pair clears m ≥ 10 — arithmetic without evidence is not shown) cross-checks the two-era numbers at the same order of magnitude (pw/form Chao2 ~64,987 vs two-era 67,866, i.e. 96 %; bur/git ~19,776 vs 17,247, 115 %; mw/git 217 %, exposing strong catchability heterogeneity — Q1/Q2 = 5,484/89) and reaches dictionaries the two-era design cannot: **PWG's first estimate, ~26,515 error sites (Chao2, git era, CI 19,484–36,360) against 123,366 records**. The design cannot repair structured division of labour: correctors splitting a dictionary alphabetically are not sampling one population, and no incidence estimator fixes that.

### 3.5 Negative result with a control

Under a rule fixed before the numbers were read (H3986), every estimator that borrows strength across dictionaries misses the known answers: pooled prevalence and correction-density extrapolation by ×0.35–×3.4 (error-site prevalence spans ×4.1 across the three test dictionaries, so their exchangeability assumption is structurally false); Chao2 over the two eras and over correctors by ×1.02–×2.33 and ×0.96–×2.17. An empirical-Bayes shrinkage estimator passed the rule and was rejected on inspection — its prior contributes < 7 % of the estimate, making it Lincoln–Petersen in disguise. For m = 0 dictionaries the observed count is not a placeholder awaiting a better formula: it is the answer, as a lower bound.

## 4. Limitations and validation plan

Estimates are of error *sites discovered at least once by the log's own processes*, not of typographic defects per se; shares are over corrected events, not latent error rates. External validation — the observed error rate on a small annotated random record sample against the model's prediction — is the one check no re-analysis of the correction log substitutes for, and is the paper's standing readiness gate (tied to the A12 second-annotator recruit).

## 5. Reproducibility

All generators are offline stdlib Python, pinned in-repo: `error_recapture.py`, `headword_linkage.py` (+ `linkage_ladder.csv`, `headword_key_collisions.csv`), `corrector_recapture.py`, `lowm_estimators.py`, `recapture_sensitivity.py`, `recapture_mutation_check.py`; outputs `error_recapture.csv`, `error_recapture_calibrated.csv`; full narratives `reports/error_recapture.md`, `reports/error_recapture_lowm.md`, `reports/corrector_recapture.md`. The underlying 52,498-event corpus is released (Zenodo concept DOI 10.5281/zenodo.21346705).

## References (to be styled at venue)

Chapman 1951; Chao 1987; Eick, Loader et al. (capture–recapture for software-inspection defect estimation); Piotrowski 2012; Reul et al. 2019 (OCR/digitisation error rates). Full styled list follows `article/refs.bib` at submission.

---

_Dr. Mārcis Gasūns_
