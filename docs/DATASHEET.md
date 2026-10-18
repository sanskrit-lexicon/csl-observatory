_Created: 11-06-2026 · Last updated: 11-10-2026_

# Datasheet - CDSL Correction-Event Corpus (OBS-T)

Following Gebru et al., *Datasheets for Datasets* (2021), and — for the
data-statement sections below — Bender & Friedman, *Data Statements for NLP with
Emphasis on Training Set Development and Evaluation* (2018), as the statement
form the JOHD / LREC resource-publication family expects. Describes the released
resource `observatory/site/src/data/correction_events_release.csv` and its
derivation. Snapshot: 2026-06-12. Regenerate with the OBS-T pipeline below.
**Upgrade note (H6390, 11-10-2026):** the datasheet was extended from skeleton to
the full two-form statement — every B&F data-statement section is now present,
with honest N/A where a section does not apply to a corpus of written dictionary
corrections; no released fact changed.

## Data Statement (Bender & Friedman 2018 form; JOHD/LREC family)

- **Curation Rationale.** The corpus exists to make the maintenance history of a
  retro-digitised lexicographic collection measurable. It was curated because the
  two correction channels (community web form; git commits) had never been joined
  into one event stream, and error typology, correction-remaining estimation
  (A48), and maintenance studies all require exactly that join. Curation decisions
  — entry-files-only mining, bulk-reformat exclusion, deterministic-with-route
  location attribution — are those of the `csl-observatory` pipeline and are
  documented in the sections above and in `docs/OBSERVATORY_DESIGN.md`.
- **Language Variety(s).** Sanskrit (a written classical language, spanning Epic
  and classical registers in the dictionary headword/lemma stock) and, as meta-
  language, English and German (source dictionaries' apparatus) plus Russian-era
  form fields. The corpus contains no speech data; language variety is
  register-neutral at the correction-event level — what is recorded is a repaired
  string, not running prose. Romanisation spaces are explicit: released Sanskrit
  strings are IAST/NFC; source-side SLP1 and markup remain in `old_raw`/`new_raw`.
- **Speaker / Demographic Characteristics.** N/A — the corpus is corrections to
  written dictionary entries; no speakers, no speech, and no demographic data of
  any kind exist at the event level.
- **Annotator / Corrector Demographics.** Not collected and not released. The
  "annotators" are the CDSL correction community (208 released corrector aliases).
  Identities are public canonical aliases from project metadata or stable
  pseudonyms for form-only email identities; raw form-submitted email addresses
  are never released. No demographic attributes (age, gender, nationality,
  expertise level) are recorded, inferred, or derivable from the release; the
  release deliberately contains no personal data. Corrector-identity handling is
  documented in `reports/contributor_identity.md`.
- **Speech Situation.** N/A — written, asynchronous, non-interactive text repair
  events over 2014–2026.
- **Text Characteristics.** Instances are dictionary entry fragments: headword
  lines, grammar codes, sense lines, citations, cross-references, and markup in
  the Cologne `<k1>`-keyed plain-text entry format (SLP1 raw / IAST normalised).
  Vocabulary is Sanskrit lexicographic apparatus; genre is reference-work
  microstructure. Text is machine-clean on the git layer and hand-typed on the
  form layer (the source of the era-specific orthographic noise the A48 linkage
  ladder measures). Known text characteristics that affect use: correction events
  are not independent per dictionary-year (campaigns cluster); `unattributed`
  locations are a real label, not missing data.
- **Ethics and consent.** All released identities are either public project
  aliases (git authorship is public by construction of the MIT/GPL-published
  upstream repositories) or stable pseudonyms for form-only identities; no
  consent-sensitive content is present. The corpus records scholarly corrections
  to public dictionaries, not communications; no downstream use is expected to
  identify individuals, and per-person performance analysis is an explicitly
  discouraged use (see Uses).
- **Version and citation.** Citable snapshot: 2026-06-12 release, archived as
  Zenodo concept DOI [10.5281/zenodo.21346705](https://doi.org/10.5281/zenodo.21346705)
  (minted 16-08-2026). New releases bump the version and require a regenerated
  release CSV with count-delta inspection before publication (see Maintenance).

## Motivation

- **Purpose.** A multi-year, multi-dictionary record of corrections to digitized
  Sanskrit dictionaries, typed by the microstructure location repaired and by edit
  operation. Intended uses include error typology, Sanskrit error
  detection/correction, and studies of digital-lexicography maintenance.
- **Created by.** M. Gasuns and the CDSL/sanskrit-lexicon community; assembled in
  `csl-observatory` from CDSL correction-form records and `csl-orig` git history.

## Composition

- **Instances.** 52,498 correction events; one row is one old->new correction
  event. The release is 64.3% derived by evidence label.
- **Layers.** 24,441 form rows come from `../CORRECTIONS/cfr.tsv`; 28,057 git rows
  are mined only from dictionary entry files matching
  `../csl-orig/v02/<dict>/<dict>.txt`.
- **Coverage.** The release spans 43 dictionaries, 208 released corrector aliases,
  and the 2014-2026 correction record represented by the available form and git
  sources.
- **Fields.** Each row contains date, dictionary, source layer, `source_path`,
  `commit_sha` for git rows, headword, old/new values, raw old/new audit strings,
  edit operations, `edit_space`, the two typology axes, crosswalk labels,
  corrector alias/name, evidence level, attribution route, and temporal split.
- **Labels.**
  - **LOCATION** (`error_component`) records where the correction lands in the
    entry: `headword`, `grammar`, `citation`, `sense`, `markup`, `crossref`,
    `meta`, or `unattributed`.
  - **EDIT-TYPE** (`edit_type`) records what changed: `spelling`, `diacritic`,
    `case`, `spacing`, `punctuation`, `digit`, `transposition`, `source-raw`, or
    `none`.
  - `edit_space` says which character space the edit trace uses: `iast`,
    `slp1_raw`, or `markup_raw`.
- **Sampling.** Not a sample: it is the full available correction record under the
  reconstruction rules. Bulk reformat commits are excluded and counted in git
  metadata.
- **Sensitive data.** Raw form-submit email addresses are not released. Released
  identities use public canonical aliases from project metadata or stable
  pseudonyms for form-only email identities.

## Collection Process

- **Form layer.** Exported from the Google "Sanskrit-Lexicon Correction form
  (Responses)" spreadsheet at `../CORRECTIONS/cfr.tsv`.
- **Git layer.** Mined from `../csl-orig` correction-classified commits touching
  entry files only. Non-entry files under `v02` are ignored by construction.
- **Timeframe.** 2014-03-18 through the current `csl-orig` snapshot used for the
  pipeline run.

## Preprocessing, Cleaning, and Labeling

- Form-layer Sanskrit strings are normalized to IAST/NFC from Devanagari or
  Harvard-Kyoto-like romanization. Raw source cells remain in `old_raw` and
  `new_raw`.
- Git-layer rows keep raw SLP1 source lines in `old_raw`/`new_raw`. Edit operations
  are computed in IAST only when the changed span is inside Sanskrit-bearing
  content; raw source or markup changes are marked with `edit_space`.
- Unequal git diff hunks are not truncated: matched delete/add lines become
  replacements, while unmatched lines become insertion/deletion events. Counts are
  recorded in `correction_events_git.meta.json`.
- Location attribution is deterministic when possible. Form joins record their
  route (`segment_exact`, `segment_fuzzy`, `value_headword_unique`,
  `value_headword_weak`, `unattributed`); weak value-headword shortcuts are not
  promoted to derived labels.
- A stratified audit sample for high-risk form joins is written to
  `validation/form_join_audit_sample.csv`.

## Uses

- **Intended.** Error typology of digital dictionaries; Sanskrit error detection
  and correction; lexicographic maintenance and diachrony studies; reproducible
  NLP baselines.
- **Caveats.** Shares are over corrected events, not the latent error rate in the
  source dictionaries. Location labels should be filtered by `evidence_level` and
  `attribution_route` for high-stakes claims. Raw SLP1/markup edits should not be
  interpreted as Sanskrit spelling/case edits.
- **Discouraged.** Per-person performance judgments; treating `unattributed`
  locations as ground truth; joining form-era L-codes directly to current
  `csl-orig` records without accounting for drift.

## Evaluation lineage

- **Statement.** OBS-T label validation, its confusion/alignment analysis, and any future
  cross-dictionary sense/headword mapping are instances of the ELEXIS/GlobaLex
  **Monolingual Word Sense Alignment (MWSA)** shared-task family. Observatory adopts the
  MWSA evaluation contract — **frozen gold sample, two annotators, Cohen's κ, per-class
  P/R/F1** — rather than a bespoke method. The harness (`scripts/obs_t_gold.py`) implements
  stratified sampling, blind sheets, κ, and per-class P/R/F1 accordingly.
- **Scope.** Naming this lineage does not change what is released here: if a cross-dict
  sense-alignment dataset is ever emitted, the alignment content itself routes to
  `csl-atlas`, with `csl-observatory` keeping only the process metrics (κ, P/R/F1).
- **Sources.** ELEXIS MWSA shared task: <https://elex.is/mwsa2020/> · data/format:
  <https://github.com/elexis-eu/MWSA>.
- **Benchmark-fit extension (H6389, 11-10-2026).** The same lineage now extends to a
  *reporting* transform: every occupied (location × edit-type) cell of the two-axis
  typology is re-expressed in nearest ERRANT/GEC and historical-text-normalization
  terms in
  [`docs/OBST_ERRANT_GEC_CROSSWALK.md`](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/docs/OBST_ERRANT_GEC_CROSSWALK.md)
  (generator `scripts/obs_t_errant_gec_crosswalk.py --check`, byte-identical
  regen; unplaceable cells flagged, never forced; citation log with ≥2
  live-verified sources per anchor claim:
  [`docs/OBST_CROSSWALK_CITATION_LOG.md`](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/docs/OBST_CROSSWALK_CITATION_LOG.md)).

## Distribution

- **Where.** In `csl-observatory` (working tree), with the citable snapshot
  archived at Zenodo concept DOI
  [10.5281/zenodo.21346705](https://doi.org/10.5281/zenodo.21346705).
- **Data license.** OBS-T released data is CC-BY-4.0; see `DATA_LICENSE.md`.
- **Code license.** Repository code remains GPL-3.0; see `LICENSE` and
  `CITATION.cff`.
- **Splits.** Temporal `split`: test = year >= 2025, dev = 2023-2024, train =
  earlier. Form-only baselines use a separate within-form chronological split
  because the form era predates the global test period.

## Maintenance and Reproduction

- **Maintainer.** `csl-observatory` maintainers.
- **Updates.** Regenerate against fresher `csl-orig` and `CORRECTIONS` snapshots;
  inspect count deltas before publishing a new citable release.
- **Automated pipeline.**

```bash
python scripts/build_correction_events.py
python scripts/reconstruct_git_events.py
python scripts/attribute_components.py
python scripts/attribute_crosswalks.py
python scripts/obs_t_release.py
python scripts/obs_t_typology.py
python scripts/obs_t_baselines.py
python scripts/obs_t_rigor.py
python scripts/obs_t_robustness.py
python scripts/obs_t_campaigns.py
python scripts/obs_t_translit_check.py
python scripts/obs_t_silver.py
python scripts/obs_t_issuelabel.py
python scripts/obs_t_regression.py
```

- **Human-gated validation.** Do not run these as unattended pipeline steps:
  `python scripts/obs_t_gold.py --make`, `python scripts/obs_t_gold.py --score`,
  `python scripts/obs_t_errorsample.py --make`, and
  `python scripts/obs_t_errorsample.py --score`.

_Dr. Mārcis Gasūns_
