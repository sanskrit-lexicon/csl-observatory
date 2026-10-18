# A12 — LREC-COLING Reproducibility Checklist + venue Scopus-record verdict

_Created: 11-10-2026 · Last updated: 11-10-2026_

**Scope.** Companion artifact for the A12 manuscript
[`paper-obs-t-error-typology.md`](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/paper-obs-t-error-typology.md)
(canonical two-axis version, reconciliation ruling
[`docs/A12_OBS_T_MANUSCRIPT_RECONCILIATION_RULING.md`](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/docs/A12_OBS_T_MANUSCRIPT_RECONCILIATION_RULING.md)),
preparing the pre-submission items named in ARTICLES.md row A12: the
LREC-COLING-family reproducibility checklist, and the MG-ruled pre-submission
Scopus check (ruling 29-07-2026: «Перед подачей проверить Scopus-запись
конкретного выпуска LREC-COLING»). Checklist verdicts are honest per item —
NO/PARTIAL rows are commitments for the submission pass, not claimed green.

## Part 1 — Reproducibility checklist (LREC-COLING 2024 form, carried to the next LREC edition)

### A. Claims and evidence

| # | Item | Verdict | Evidence |
|---|---|---|---|
| A1 | All theoretical claims and results have verifiable sources | **YES** | Every headline number re-verified against the released 52,498-event snapshot (18-row verification table, H1759 reconciliation ruling doc); snapshot archived at DOI [10.5281/zenodo.21346705](https://doi.org/10.5281/zenodo.21346705) |
| A2 | Limitations / error analysis are discussed | **YES** | §Limitations states sites-vs-defects scope, `unattributed` label semantics, cross-model (not human) agreement status for κ 0.906; §4.3/§4.6 carry the H1272-accurate phrasing |
| A3 | Paper states the corpus release with a citable identifier | **YES** | Zenodo concept DOI minted 16-08-2026, resolved 24-08-2026 |

### B. Datasets

| # | Item | Verdict | Evidence |
|---|---|---|---|
| B1 | All datasets cited and referenced | **YES** | OBS-T corpus (this paper's release); form export `CORRECTIONS/cfr.tsv`; csl-orig v02 entry files — all named with generation scripts |
| B2 | Dataset licenses stated | **YES** | CC-BY-4.0 (`DATA_LICENSE.md`); upstream csl-orig GPL-3.0 code boundary stated |
| B3 | Personal data / anonymisation handled | **YES** | Raw form emails never released; public canonical aliases or stable pseudonyms only (`reports/contributor_identity.md`); no demographic attributes present (full B&F data statement: [`docs/DATASHEET.md`](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/docs/DATASHEET.md)) |

### C. Code and experiments

| # | Item | Verdict | Evidence |
|---|---|---|---|
| C1 | Code available for all experiments | **YES** | All generators committed: `scripts/build_correction_events.py`, `reconstruct_git_events.py`, `attribute_components.py`, `attribute_crosswalks.py`, `obs_t_release.py`, `obs_t_typology.py`, `obs_t_baselines.py`, `obs_t_rigor.py`, `obs_t_robustness.py`, `obs_t_gold.py` |
| C2 | Dependencies specified; environment reproducible | **YES** | Stdlib-only Python, documented in `docs/REVIEWER_REPRODUCIBILITY.md` (no package versions to pin) |
| C3 | Randomness controlled and reported | **PARTIAL → YES at submission** | Annotation sheets use pre-registered seed 20260721 (`scripts/obs_t_second_sheet.py`); paper text must name the seed and state all other steps are deterministic — one-line edit queued for the submission pass |
| C4 | Hardware/software requirements stated | **YES** (trivially) | CPU-only stdlib Python; stated in reviewer reproducibility guide |
| C5 | Statistical measures reported with uncertainty | **YES** | κ = 0.906 [0.872–0.938] with CI (n = 390, location axis, blind cross-model double annotation, H1385/PR #102); χ²/τ values explicit in abstract |
| C6 | Human-gated validation separated from the automated pipeline | **YES** | `obs_t_gold.py --make/--score` and `obs_t_errorsample.py --make/--score` documented as intentionally manual (`docs/DATASHEET.md`, `docs/REVIEWER_REPRODUCIBILITY.md`) |

### D. Open items before submission (not checklist-failable, tracked in the A12 row)

1. Genuine byline confirmation; expert review of the ~66 encoding↔orthography
   borderline rows in `validation/gold_sample.csv`; MG read-and-sign
   ([`SIGNOFF_A12_author_pass.md`](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/SIGNOFF_A12_author_pass.md)).
2. C3 one-liner (name seed 20260721 + determinism statement) folded into the
   manuscript at the submission pass.
3. Final submission wording of §4.6 (`@DECIDE` open since H1759).

## Part 2 — Venue Scopus-record verdict (MG-ruled pre-submission check, 29-07-2026)

**Question.** Does the specific LREC-COLING issue the A12 manuscript would appear
in have a Scopus record?

**Evidence (web-verified 11-10-2026, links below):**

1. The joint **LREC-COLING** branding last ran as **LREC-COLING 2024 (Turin,
   20–25 May 2024)** — the LREC 2026 welcome text states this explicitly
   ("except for 2024 when it joined forces with COLING to stage the LREC-COLING
   2024 in Turin", [proceedings front matter](https://aclanthology.org/2026.lrec-1.0.pdf)).
2. **LREC 2026** (the current edition; Palma de Mallorca, 11–16 May 2026, 945
   accepted papers) ran as plain LREC — proceedings published by ELRA in the ACL
   Anthology as [2026.lrec-1](https://aclanthology.org/volumes/2026.lrec-1/)
   (proceedings DOI 10.63317/4fxzgre27xzj, ISBN 978-2-493814-49-4, ISSN 2522-2686).
3. **Publisher attestation of Scopus coverage:** ELRA's own proceedings page
   states "LREC proceedings from 2000 on are published in the ACL Anthology. They
   are also indexed in Thomson Citation Index and SCOPUS"
   ([elra.info — LREC Proceedings](https://www.elra.info/elra-events/lrec/proceedings-2/)),
   with the LREC-COLING 2024 and LREC 2026 volumes listed on the same page.

**Verdict: GO (publisher-attested Scopus coverage), with a one-time direct-record confirmation residual.**
The LREC proceedings series — which includes the LREC-COLING 2024 issue and the
2026 edition — is Scopus-indexed by the publisher's own statement; the "LREC-COLING
venue family" therefore satisfies the Scopus requirement of the SUBMIT-15 set.
What this check cannot do from the public web is quote the exact **Scopus source
ID** for the specific future issue; that is a one-minute Scopus-session lookup for
MG (source list → "Language Resources and Evaluation Conference" source record,
check the 2024/2026 coverage rows) and is filed as a dated residual in GTD rather
than left open here. If MG's direct lookup contradicts the publisher attestation,
the venue verdict reverts to @DECIDE (IJL alternate, which is a Scopus-indexed
journal).

---

_Dr. Mārcis Gasūns_
