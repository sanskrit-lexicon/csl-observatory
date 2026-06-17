# Datasheet - CDSL Correction-Event Corpus (OBS-T)

Following Gebru et al., *Datasheets for Datasets* (2021). Describes the released
resource `observatory/site/src/data/correction_events_release.csv` and its
derivation. Snapshot: 2026-06-12. Regenerate with the OBS-T pipeline below.

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

## Distribution

- **Where.** In `csl-observatory`, with intended archival deposit for paper use.
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
