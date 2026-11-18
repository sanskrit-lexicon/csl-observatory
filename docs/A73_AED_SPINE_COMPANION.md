# A73 companion — placing the E32 release on the annotation-error-detection spine

_Created: 18-11-2026 · Last updated: 18-11-2026_

**Companion to:** A73, *Correction-event mining as annotation-error-detection corpus release* (ARTICLES.md, 3/5, owning repo `csl-observatory`).
**Executes:** one `/acl-uplift` shape-4 item — reframe / companion artifact.
**Corpus of record:** [`data/publication/e32-correction-events-release-2026-10-10/`](../data/publication/e32-correction-events-release-2026-10-10/README.md), frozen cut `a27fec9e…faaf`, 52,498 events.
**Benchmark of record:** [`obst-bench/v1/`](../obst-bench/v1/README.md) — the scorer, split digests and two reference baselines live there and are **not** duplicated here.

## Goal / stop condition

Place E32 on the task spine the field already owns, with every anchor claim carried by a live-checked citation, and leave every released number byte-identical to the E32 pins. Stop when the three anchors below resolve to primary records and the numeric canary re-runs `ALL PASS`.

## 1. Why a companion is the right shape here

A73's `Related work` already names annotation-error detection (AED), grammatical-error correction (GEC) error typing, post-OCR Sanskrit and datasheets. What it does not do is state the **comparability contract**: which published task each E32 task instantiates, in which reporting terms its numbers may be compared, and where a third party finds the frozen split and scorer. A reviewer cannot place a resource paper without that contract, and adding it to the manuscript would disturb a frozen submission pack. This companion carries it without touching the draft.

## 2. The canonical spine — three anchors, each with verified citations

### A1 · AED is detection plus error typing over gold labels

**Claim.** AED asks first *whether* a gold label is wrong and then *what kind* of error it is; a corpus that supplies both is placeable on this spine. E32's `detection` task (which of two forms is the pre-correction one) and `location` task (which dictionary component was damaged) are the two halves of that question over dictionary entries.

**Sources.**

- Jan-Christoph Klie, Bonnie Webber, Iryna Gurevych. 2023. *Annotation Error Detection: Analyzing the Past and Present for a More Coherent Future*. **Computational Linguistics** 49(1):157–198. <https://aclanthology.org/2023.cl-1.4/> — reimplements 18 AED methods over 9 datasets and defines a uniform evaluation setup. Already cited in A73's `iscls.bib` as `klie2023annotation`; re-verified here.
- Christopher Bryant, Mariano Felice, Ted Briscoe. 2017. *Automatic Annotation and Evaluation of Error Types for Grammatical Error Correction*. **ACL 2017** (Volume 1: Long Papers). <https://aclanthology.org/P17-1074/> — the ERRANT error-type framework. Already cited as `bryant2017automatic`; re-verified here.

### A2 · A diff-derived error trace is the field's standard evidence form

**Claim.** ERRANT turns an original/corrected pair into an operation trace from which error types are derived. E32's per-event edit-op trace (`op`, `unit`, `dist`, `script`, `edit_space`, `cl`) is the same evidence form applied to dictionary entries; the two-axis location × edit-type decomposition is the field's standard split of *where* from *what kind*.

**Sources.** Bryant et al. 2017 (above) for the dataset-agnostic rule-based typology; Klie et al. 2023 (above) for the uniform AED evaluation setup that makes method scores comparable. Both anchors are sufficient for the claim; no third citation is needed.

### A3 · A released resource is documented, not just described

**Claim.** A CL resource paper is expected to travel with a datasheet and a reproducible cut. E32 ships `docs/DATASHEET.md`, a schema, a SHA-256-pinned release directory and a one-command numeric canary; that satisfies the documentation expectation without adding a claim about correctness.

**Source.** Timnit Gebru, Jamie Morgenstern, Briana Vecchione, Jennifer Wortman Vaughan, Hanna Wallach, Hal Daumé III, Kate Crawford. 2021. *Datasheets for Datasets*. **Communications of the ACM** 64(12):86–92. DOI <https://doi.org/10.1145/3458723>. Already cited as `geenru2021datasheets`; re-verified here.

## 3. Placeability contract

| E32 task | Field analogue | Reporting terms | Committed source of the number | Caveat |
|---|---|---|---|---|
| `detection` — pick the pre-correction form of a pair | AED binary error flagging | per-class precision / recall / **F0.5**, false-positive rate, chance-corrected α | [`reports/obs_t_baselines_field_metrics.md`](../reports/obs_t_baselines_field_metrics.md), reproduced on the frozen split by `scripts/obst_bench.py baselines` | detection is unsolved (F0.5 0.519, FPR 0.474); report it as a baseline, not a solved task |
| `location` — assign the damaged dictionary component | GEC / AED error-type classification | accuracy, macro-F1, per-class P/R/F0.5, α | same field-metrics report; `obst-bench/v1/` `location` split | no dev split in the E32 release; the test digest is the tuning fence |
| corpus release | GEC / post-OCR resource release | row count, dictionary count, digest pins, canary | [`e32_canary.py`](../data/publication/e32-correction-events-release-2026-10-10/e32_canary.py) — `ALL PASS`, 25 corpus + 65 pinned numbers | the working CSV grows; only the pinned cut is comparable |

The benchmark is **enterable but not sealed**: the corpus is CC BY 4.0 and public, so a test row's gold can be recovered by joining the release. A score means something only under the stated no-lookup rule; see [`obst-bench/v1/README.md`](../obst-bench/v1/README.md) § *Honour code*. This caveat is part of the placeability contract and must travel with any number quoted from it.

## 4. Direct-ancestor hunt — outcome

A candidate direct ancestor of the AED line — Klie, Webber & Gurevych, *Annotation Error Detection: The Curious Case of Reversing Annotations* (commonly cited as NAACL-HLT 2018, anthology `N18-1031`) — could **not** be live-verified in this session: direct HTTP fetches of `aclanthology.org` timed out, and the search index did not return a primary record confirming the title, venue and identifier together. Per the `/acl-uplift` anti-fabrication rule it is **not cited**; it is recorded here as an open candidate for a later session with working network access. No keystone citation was invented to fill the gap.

## 5. Verification dossier

| Citation | Anchor claim | Primary record | Check performed (18-11-2026) | Status |
|---|---|---|---|---|
| Klie, Webber & Gurevych 2023, *CL* 49(1):157–198 | A1, A2 | `https://aclanthology.org/2023.cl-1.4/` | official anthology metadata + `.bib` record returned by search index: authors, title, journal, volume, pages, year | verified |
| Bryant, Felice & Briscoe 2017, *ACL 2017* | A1, A2 | `https://aclanthology.org/P17-1074/` | official anthology record + `.bib`: authors, title, proceedings, publisher, year | verified |
| Gebru et al. 2021, *CACM* 64(12):86–92 | A3 | `https://doi.org/10.1145/3458723` | DOI landing page + ACM record: title, venue, volume/issue, pages, publication date | verified |
| Klie et al. 2018, *Reversing Annotations* | A1 candidate | `https://aclanthology.org/N18-1031/` | fetch timed out; search index did not confirm the record | **not cited** — open candidate |

**Method note, stated rather than hidden.** Direct page fetches to `aclanthology.org` timed out from this host on 18-11-2026. The three cited records were confirmed against search-indexed official anthology metadata and the DOI landing page, not by opening the article pages themselves. All three are already in A73's `iscls.bib`; this pass re-checked their bibliographic identity and added the comparability claims they support. The fourth candidate was dropped rather than cited unverified.

## 6. What this companion does not change

- No E32 row, digest, schema or release file is re-cut.
- No number is restated from memory; every quoted figure points at a committed artifact.
- No venue, DOI or submission-pack decision is made here.
- The A73 manuscript in `Uprava/papers/A73_iscls9/` is untouched — the paper-priv boundary stays intact.

## 7. Reproduction

```bash
python3 data/publication/e32-correction-events-release-2026-10-10/e32_canary.py
python3 scripts/obst_bench.py check
```

Expected: `ALL PASS — 25 corpus + 65 pinned numbers verified against the frozen cut`, and the benchmark digest check green.

---

_Dr. Mārcis Gasūns_
