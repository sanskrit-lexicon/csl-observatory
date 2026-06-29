# Error typology of digital Sanskrit dictionaries — design spec

Date: 2026-06-11 · **Updated 2026-06-12 (Phases 1–8 shipped; two-axis typology)**
Status: implemented. Authoritative spec for the error-typology / correction-event
track (working code **OBS-T**). Owner: Mārcis Gasūns.

This document specifies an observatory finding layer that complements the
existing correction-*sustainability* finding
([`reports/obs_q_correction_sustainability.md`](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/reports/obs_q_correction_sustainability.md),
[`scripts/obs_q_correction.py`](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/scripts/obs_q_correction.py)). OBS-Q answers **who corrects, when, and how
fast**; OBS-T answers **what was wrong, where in the entry, and how the error
profile changed over twelve years**.

---

## 0. Final state (Phases 1–8) — read this first

The track is **implemented and merged to `main`**. The original single-axis
"microstructure component" plan below (§1–§13) was **superseded in Phase 8** after a
validation finding (see [`reports/obs_t_silver.md`](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/reports/obs_t_silver.md)): the
component column conflated two different things. The shipped design is **two
orthogonal axes**:

- **LOCATION** (`error_component`) — *where* in the entry: `headword · grammar ·
  citation · sense · markup · crossref · meta`; reported on **derived** labels;
  join-failures = `unattributed`. (Phase 3 / 8 in
  [`scripts/attribute_components.py`](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/scripts/attribute_components.py).)
- **EDIT-TYPE** (`edit_type`) — *what kind* of change, from the edit-op trace:
  `spelling · diacritic · case · spacing · punctuation · digit · transposition · source-raw`.
  (Phase 8 in
  [`scripts/attribute_crosswalks.py`](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/scripts/attribute_crosswalks.py).)

Current headline results are generated, not hand-maintained; see
[`reports/obs_t_typology.md`](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/reports/obs_t_typology.md),
[`reports/obs_t_rigor.md`](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/reports/obs_t_rigor.md),
and the post-review delta tracker in
[`docs/archive/OBS_T_FIX_PLAN_2026-06-12.md`](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/docs/archive/OBS_T_FIX_PLAN_2026-06-12.md).
The paper claim is now narrower than the Phase-8 draft: micro-edit dominance is
strongest overall and in sense/headword locations; markup, citation, and grammar
are reported separately. H2 p-values are descriptive, with Cramer's V and
commit/campaign-block sensitivity checks carrying the interpretation. H3 trends
use multiple-comparison handling.

Pipeline (all stdlib, offline; reproduce in order):
[`build_correction_events`](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/scripts/build_correction_events.py) →
[`reconstruct_git_events`](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/scripts/reconstruct_git_events.py) →
[`attribute_components`](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/scripts/attribute_components.py) →
[`attribute_crosswalks`](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/scripts/attribute_crosswalks.py) →
[`obs_t_release`](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/scripts/obs_t_release.py) →
[`obs_t_typology`](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/scripts/obs_t_typology.py) →
[`obs_t_baselines`](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/scripts/obs_t_baselines.py) →
[`obs_t_rigor`](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/scripts/obs_t_rigor.py) →
[`obs_t_robustness`](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/scripts/obs_t_robustness.py) →
[`obs_t_campaigns`](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/scripts/obs_t_campaigns.py) ·
validation-only: [`obs_t_translit_check`](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/scripts/obs_t_translit_check.py),
[`obs_t_gold`](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/scripts/obs_t_gold.py),
[`obs_t_errorsample`](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/scripts/obs_t_errorsample.py),
[`obs_t_issuelabel`](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/scripts/obs_t_issuelabel.py),
[`obs_t_silver`](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/scripts/obs_t_silver.py).

Open: human gold/error annotation ([`validation/gold_sample.csv`](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/validation/gold_sample.csv),
[`validation/error_sample.csv`](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/validation/error_sample.csv)) + a second annotator for κ.

**Manuscript (2026-06-13).** The paper drafted from this spec lives at the repo root:
[`paper-obs-t-error-typology.md`](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/paper-obs-t-error-typology.md)
— *Surface, Not Substance* — carrying the two-axis typology, H1–H3 with their statistics,
the three crosswalks, the released-resource baselines, and the corrected-≠-error-rate
caveat. Targets an NLP/language-resource venue (LREC-COLING; IJL alternate). No κ is
asserted; the gold annotation above remains the open validation gate.

The sections below are retained for provenance and the parts still accurate (data
layers, normalization, NLP resource). Where they say "component = canonical
typology", read "location = one of two axes".

---

## 1. Goal and publication target

One comprehensive English paper for a **computational-linguistics / NLP venue**
(LREC-style: a documented, released language resource + a typology + reproducible
baselines). The paper carries four argument axes in one narrative:

1. **Error typology** — what kinds of errors digitized Sanskrit dictionaries
   contain, classified by the dictionary component they damage.
2. **Diachronic change** — how the error profile and correction practice changed
   across the full 2014–2026 span.
3. **Correction workflow** — how errors are found and fixed (form → changefile →
   commit), throughput, latency, and the human network (reuses OBS-Q).
4. **Cross-dictionary comparison** — error density and error fingerprints per
   dictionary, normalized by entry count.

The headline contribution is a **component-attributed error typology**: the
canonical taxonomy classifies each correction by *which part of the dictionary
microstructure* was wrong, made possible because we hold both the corrections and
the XML-tagged `csl-orig` sources locally.

## 2. Locked decisions

| Dimension | Decision |
|---|---|
| Output | One paper, NLP/CL venue; released language resource + baselines |
| Time span | Full 2014–2026 (all five data layers unified) |
| Canonical typology | **Two axes** (Phase 8): LOCATION (microstructure component, derived) × EDIT-TYPE (from edit-ops). Was single-axis "microstructure component"; see §0. |
| Crosswalk taxonomies | NLP/ERRANT edit-ops · OCR/digitization · textual-criticism (Katre) |
| Normalization | **IAST** canonical (NFC for display, NFD for diacritic-level edit ops) |
| Resource split | **Temporal** (train past → test recent) |
| Contributors | Release-safe public aliases or stable pseudonyms; raw form-submit emails removed |
| License | Code GPL-3.0; OBS-T released data CC-BY-4.0 (`DATA_LICENSE.md`) |
| Home | `csl-observatory` (process/time framing); cross-links to `csl-atlas` |

## 3. Data sources (five layers)

All sibling repos under `C:\Users\user\Documents\GitHub\` and reproducible offline
except where a `--fetch-*` flag is noted.

| # | Layer | Path | Era | Per-event richness | Notes |
|---|---|---|---|---|---|
| L1 | Correction-form responses | `../CORRECTIONS/cfr.tsv` | 2014–2019 | **highest** (old/new/type/who/when) | Google-form export; 24,441 rows; dirty NEW cell |
| L2 | `csl-orig` git diffs | `../csl-orig` (git) | 2014–2026 | high (old/new from diff) | Extends past the form era; reconstruct pairs from hunks |
| L3 | Hand log + printchange | `../CORRECTIONS/history.txt`, `../CORRECTIONS/dictionaries/*/*printchange.txt` | 2014–2019 | medium (campaign-level) | `printchange` = deviations from the *scanned print*, not markup |
| L4 | Formal change batches | `../csl-corrections/batch_YYYYMMDD/` | 2024–2026 | high (paired old/new lines) | `updateByLine.py` changefile format |
| L5 | Org metrics backdrop | observatory CSVs (`obs_q_*`, `timeseries_*`) | 2014–2026 | aggregate | Reused, not regenerated |

Provenance is recorded per event in a `source_layer` field so any figure can be
sliced or audited by layer. L1 is the spine; L2 is the largest extension; L1∩L2
overlap is deduplicated (§5.6).

## 4. The unified correction-event schema

Phase-1 output `observatory/site/src/data/correction_events.csv` (+ a JSON
sibling for the schema/envelope). One row = one correction event.

| Field | Type | Source | Description |
|---|---|---|---|
| `event_id` | str | derived | stable hash of (layer, dict, lcode, old, new, date) |
| `date` | ISO date | L1/L2/L4 | event date (form submit, commit, or batch date) |
| `source_layer` | enum | — | `form` \| `git` \| `printchange` \| `batch` |
| `source_path` | str | L1/L2 | source file/path for the mined event |
| `commit_sha` | str | L2 | commit SHA for git-layer events |
| `dict` | str | all | dictionary code, lowercased to csl-orig convention |
| `lcode` | str | L1/L2 | `<L>` record id when known (`0(NA)` → empty) |
| `headword_iast` | str | L1 | headword, normalized to IAST |
| `old_iast` | str | all | erroneous string, IAST/NFC for Sanskrit spans; raw source span otherwise |
| `new_iast` | str | all | corrected string, IAST/NFC for Sanskrit spans; raw source span otherwise |
| `old_raw` / `new_raw` | str | all | verbatim source cells (audit trail) |
| `inline_comment` | str | L1 | commentary lifted out of the NEW cell |
| `edit_ops` | json | derived | alignment trace over NFD chars (§5.4) |
| `edit_distance` | int | derived | Damerau–Levenshtein over NFD |
| `edit_space` | enum | derived | `iast` \| `slp1_raw` \| `markup_raw` |
| `script_old` / `script_new` | enum | derived | `deva` \| `iast` \| `latin` \| `mixed` |
| `comment_raw` | str | L1 | the form's free-text type comment |
| `error_type_empirical` | str | derived | normalized empirical cluster label (§6.2), diagnostic only |
| `error_component` | enum | derived | microstructure component (§6.1) — the canon |
| `errant_type` | str | derived | crosswalk: operation × unit (§6.4) |
| `ocr_class` / `textcrit_class` | str | derived | crosswalk columns (§6.4) |
| `corrector` | str | L1/L2/L4 | canonical login (alias-merged) |
| `corrector_name` | str | derived | public name or stable pseudonym; no raw form emails |
| `latency_days` | int | L1 | submit → "Corrected" (when parseable) |
| `evidence_level` | enum | — | `observed` \| `derived` \| `inferred` |
| `attribution_route` | str | derived | route used for location attribution (exact segment, shortcut, fuzzy, unattributed) |
| `warnings` | str | — | per-row caveats (unparsed cell, no lcode join, …) |

Every generated file uses the observatory/atlas **envelope**: `schemaVersion`,
`generatedAt`, `sourcePath`, `recordCount`, `assumptions[]`, `warnings[]`, then
`rows`. JSON Schema committed at `data/schema/correction-event.schema.json`.

## 5. Normalization pipeline (Phase 1)

### 5.1 Parse `cfr.tsv`
8 tab columns: `timestamp, dict, lcode, headword, old, new, comment, corrector`.
Reuse the time-sort logic from `../CORRECTIONS/cfr_adj.py` (Google does not append
in order). Rows that are not 8 columns are logged to `warnings`, not dropped.

### 5.2 Split the dirty NEW cell
The NEW cell frequently embeds commentary: `वेदना - no "र" conjunct consonant`,
`घट् (ट् not द्)`. Rule: split on the first ` - `, ` (`, or `  ` (double space)
that is followed by Latin/explanatory text; the leading run is the correction, the
remainder is `inline_comment`. Conservative — when ambiguous, keep the whole cell
as `new_raw` and flag a warning. This heuristic is `inferred` and review-sampled.

### 5.3 Script detection + transliteration to IAST
The cfr cells are **mixed-encoding across dictionaries** (a finding in itself): some
dicts (e.g. APES) use Devanagari, others (e.g. PW, the largest) use **Harvard-Kyoto**
(`bharahezaravRtti` = bharaheśaravṛtti; HK `z`=ś, `S`=ṣ, `R`=ṛ, `T`=ṭ). Two
self-contained transliterators (stdlib only): Devanagari→IAST (inherent-`a`, virāma,
vowel-sign handling) and HK→IAST (greedy longest-match). `normalize_to_iast` routes
Devanagari runs to the first and HK-looking roman tokens (internal capital, or HK `z`)
to the second; plain Latin/English is left alone. `csl-orig` source files, by
contrast, are **SLP1** — so the form-layer join transliterates both sides to a common
IAST. Output normalized to Unicode **NFC**.

### 5.4 Edit-operation trace
Compute over **NFD** (so a diacritic is its own combining char and therefore its
own edit). Damerau–Levenshtein alignment → list of typed ops:
`{op: sub|ins|del|transpose, from, to, unit}` where `unit ∈ {diacritic, vowel,
consonant, conjunct-virama, anusvara-candrabindu, case, whitespace, punctuation,
digit, latin}`. This drives both the ERRANT crosswalk and the edit-op statistics.

### 5.5 Identity resolution
Reuse `load_resolver()` semantics from `obs_q_correction.py` against
`scripts/contributors_map.json`; extend the map with form-only aliases
(`ejf→funderburkjim`, `dhaval/dhavel/Dhaval→drdhaval2785`, `gas/Gasyoun→gasyoun`,
`ss/sampada`, named volunteers). Latency parsed from the `… : Corrected M/D/YYYY`
tail of the corrector cell.

### 5.6 L2 git reconstruction (Phase 2, specified here)
`git log --name-only --follow -- v02/<dict>/<dict>.txt`, then per correction
commit parse the unified diff hunks into `-old/+new` line pairs; attribute date,
author (resolved), and dict. Deduplicate against L1 by (dict, lcode, old, new)
fuzzy key. Bulk imports/reformats excluded by the OBS-Q `classify()` subject
filter.

## 6. The typology

### 6.1 Canonical frame — microstructure component (the contribution)
Each event is attributed to the dictionary component it damaged, by joining to the
`csl-orig` record (`dict` + `lcode`) and locating `old_raw` inside the XML-tagged
text:

| `error_component` | Tag locus | Example |
|---|---|---|
| `headword` | `<k1>`,`<k2>`,`<h>` | wrong lemma / homonym |
| `grammar` | `<lex>` | wrong gender/POS |
| `citation` | `<ls>` | wrong source siglum / reference |
| `sense` | definition prose, `<s>` | wrong gloss / meaning |
| `encoding` | `<bot>`,IAST runs,diacritics | transliteration / diacritic |
| `markup` | tag delimiters, `{}` | structural / tag error |
| `crossref` | `<lb>`,link refs | broken cross-reference |
| `orthography` | body word, no tag | plain spelling typo in body |

When the join fails the released component is `unattributed` and flagged
`inferred`; the empirical cluster is retained only as a diagnostic feature.

**Phase 3 outcome (2026-06-11).** Implemented in `scripts/attribute_components.py`.
- **git layer: 26,512 events, 100% positionally derived** — the changed source line
  carries its tags, so the component is read off directly. Distribution: sense 12,988,
  orthography 4,301, markup 3,945, citation 3,234 (PWG's dense `<ls>`), headword 1,002.
- **Historical Phase-3 form layer: 12.9% derived (3,158), the rest inferred.**
  The post-review implementation records attribution routes and leaves weak joins
  `unattributed`. Two legacy-data findings
  forced the join onto the **headword** rather than the L-code: (a) the cfr "L code"
  cell is free-text (`[L=5590] [p= 1-299]`), and (b) more fundamentally, the 2014-era
  sequential `<L>` ids have **drifted** against today's csl-orig (cfr L=4477 → utkaṇṭhā,
  but current record 4477 = utkalaṃ). The headword is the only stable key; even so, the
  cfr "headword" cell is usually the *old* (mistyped) form, so the join also tries the
  corrected value and first tokens as entry keys.
- **Historical Phase-3 overall: 58% derived / 42% inferred** across 50,953 events.
  Current numbers are regenerated by the pipeline and recorded in
  `docs/archive/OBS_T_FIX_PLAN_2026-06-12.md`. The low form-layer
  link rate is reported, not hidden: historical correction-form data is only partly
  machine-linkable to current sources because of encoding heterogeneity and id drift —
  a result the paper can state directly. Future work (Phase 3.1): fuzzy/edit-distance
  headword matching and per-dictionary encoding profiles to raise the form link rate.

### 6.2 Empirical clusters (bottom-up, hybrid)
Normalize `comment_raw` (lowercase, strip, collapse the 40+ `typo` variants);
cluster on `comment + edit_op signature`. Produce a frequency table of emergent
clusters (`typo`, `capitalization`, `AS-number`, `IAST/diacritic`, `markup`,
`OCR/print`, `reference`, `variant`, `article-splitting`, …). These clusters are
diagnostic features and baseline covariates, not a fallback source for the
canonical location label.

### 6.3 Evidence labels
`observed` = present in source cell; `derived` = deterministic rule (edit ops,
component join that succeeded); `inferred` = heuristic or failed location join
kept as `unattributed`. No figure hides the label.

### 6.4 Crosswalk columns
Same event also typed under three secondary frames so reviewers from any tradition
can read it: **ERRANT** (`errant_type` = operation × unit, automatic),
**OCR/digitization** (`ocr_class`: substitution/segmentation/reading-order/
real-vs-non-word), **textual-criticism** (`textcrit_class`: substitution/omission/
addition/transposition + haplography/dittography/metathesis; anchor S.M. Katre,
*Introduction to Indian Textual Criticism*, 1941). Anchors for the canon: Wiegand
*Wörterbuchforschung*; Hartmann & James 1998; Svensén 2009.

## 7. Statistics catalogue → outputs

| Axis | Statistic | Output CSV |
|---|---|---|
| Typology | component × frequency; empirical-cluster freq; edit-op distribution; char-confusion matrix; edit-distance histogram; error position | `obs_t_typology.csv`, `obs_t_confusion.csv` |
| Diachronic | events/year × component (stacked); error-type drift; per-dict settling curves; campaign annotations | `obs_t_annual.csv`, `obs_t_campaigns.csv` |
| Workflow | corrector × component; latency by type/era; pipeline-era shares | reuse `obs_q_*` + `obs_t_corrector.csv` |
| Cross-dict | corrections per 1k entries (normalize by `<L>` counts); error fingerprint vectors; print-vs-digital split | `obs_t_per_dict.csv` |

`<L>` entry counts come from the existing `data/headwords.json` (1,495,422
entries, 43 dicts) for density normalization.

## 8. Timelapse / visualization deliverables

Observable Framework pages under the observatory site:

- animated **stacked-area** of error components 2014→2026;
- **racing bar** of dictionaries by cumulative corrections;
- animated **confusion-matrix heatmap** per year (which char-confusions dominate);
- **corrector-network** growth animation;
- a **scrubber timeline** with `history.txt` campaign annotations.

## 9. NLP resource and baselines

- **Release**: `correction_events.csv` + schema + datasheet (Gebru et al.
  "Datasheets for Datasets"), CC-BY-4.0, with a temporal split
  (`split ∈ {train,dev,test}` by date thresholds, test = most recent).
- **Baselines**: (1) error **detection** (old vs new token flag, P/R/F1);
  (2) error **correction** (char-level edit transducer / seq2seq old→new);
  (3) **location classifier** (predict `error_component` from edit-ops, with an
  ablation that removes `error_type_empirical`).

## 10. Phased plan

| Phase | Deliverable | Status |
|---|---|---|
| **1** | Unified event table from L1 (cfr.tsv): parse, NEW-split, Deva→IAST, edit-ops, alias-merge, latency → `correction_events.csv` + schema | **in progress** |
| 2 | L2 git-diff reconstruction; dedup; extend to 2014–2026 | next |
| 3 | Component attribution via `csl-orig` join (canon typology) | |
| 4 | Empirical clustering + crosswalk tables + evidence labels | |
| 5 | Statistics CSVs + `reports/obs_t_typology.md` finding | |
| 6 | Temporal split + datasheet + 3 NLP baselines | |
| 7 | Observable timelapse pages + paper figures | |

## 11. Reproducibility & validation gates

- stdlib-only Python; paths relative via `HERE/ROOT/GH_ROOT`; UTF-8 reconfigure;
  no BOM (`open(...,'w',encoding='utf-8')`).
- Network only behind `--fetch-*`, cached to CSV (mirror OBS-Q).
- Validation: row count vs `cfr.tsv` non-blank lines; `<L>/<LEND>` join hit-rate
  reported; NFC round-trip check; sampled-review of `inferred` rows.
- Boundary check (per `docs/BOUNDARY_RULES.md`): the object of analysis is
  corrections/commits/issues over dictionary source text — in scope for the
  observatory; the *dictionary-structure* interpretation cross-links to
  `csl-atlas` rather than living here.

## 12. Risks

- Dirty NEW cell → some old/new pairs unrecoverable (mitigate: keep `*_raw`,
  flag, review-sample).
- L1∩L2 dedup false-merges (mitigate: conservative fuzzy key + warning).
- Component join miss-rate on dicts without clean `<L>` codes in the form era
  (mitigate: edit-op fallback, labeled `inferred`).
- Privacy: strip raw form-submit emails from public output; keep public canonical
  aliases/names where already present and stable pseudonyms otherwise.

## 13. Related

- `scripts/obs_q_correction.py` · `reports/obs_q_correction_sustainability.md`
- `docs/BOUNDARY_RULES.md` · `docs/OBSERVATORY_DESIGN.md`
- `data/headwords.json` (entry counts) · `scripts/contributors_map.json`
- csl-atlas microstructure work (cross-link for the lexicographic frame)
