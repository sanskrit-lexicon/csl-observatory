# OBS-T two-axis typology ↔ ERRANT/GEC + historical-text-normalization crosswalk

_Created: 11-10-2026 · Last updated: 11-10-2026_

Executed under handoff
[H6389](https://github.com/gasyoun/Uprava/blob/main/handoffs/H6389-OxAlpha_csl-observatory_obs-t-errant-gec-crosswalk-a15-chaoss_10.10.26.md)
by OxAlpha (`zai-coding-plan/glm-5.3-flash` via ZCode), 2026-10-11.

Reporting transform only — **no system re-run, no labels recomputed**. This doc
re-expresses the two-axis OBS-T typology (location × edit-type,
[`docs/DATASHEET.md`](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/docs/DATASHEET.md))
in published shared-task terms, so a reviewer from the GEC or
historical-text-normalization tradition can read the corpus without re-deriving
its vocabulary. Mismatches are flagged, never forced: where no published
category exists the cell is marked **UNPLACEABLE** and stays in the table.

## 1. Relation to existing frames

- The paper's §4.4 already types the **edit-op trace** under three external
  schemes (ERRANT op×unit, OCR/digitisation, textual criticism). This doc is the
  **two-axis cell view**: the same published schemes, joined per
  (location × edit-type) cell of the released corpus, with the location axis
  reported honestly as having **no published analogue** (§4).
- This extends — it does not re-derive — the **MWSA evaluation-lineage framing**
  (paper §4.5; DATASHEET *Evaluation lineage*): OBS-T's *validation* contract
  (frozen gold sample, two annotators, Cohen's κ, per-class P/R/F1) remains the
  MWSA shared-task contract (Ahmadi/McCrae, ELEXIS/GlobaLex — both sources
  re-verified live 11-10-2026, see the citation log). The crosswalk here is a
  *labeling/reporting* transform on the released labels; it adds no evaluation
  protocol and changes nothing the corpus releases.

## 2. Anchor claims and citations

Every anchor claim carries ≥2 live-verified sources (fetched and matched against
authors/title/venue on 2026-10-11; full log with per-claim URLs:
[`docs/OBST_CROSSWALK_CITATION_LOG.md`](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/docs/OBST_CROSSWALK_CITATION_LOG.md)).

1. **ERRANT is a rule-based operation × category framework for GEC.**
   Bryant, Felice & Briscoe 2017, *Automatic Annotation and Evaluation of Error
   Types for Grammatical Error Correction* (ACL 2017,
   [P17-1074](https://aclanthology.org/P17-1074/)) + the
   [ERRANT v3 repository](https://github.com/chrisjbryant/errant) (M2 format
   worked examples `R:SPELL`, `M:DET`, `R:VERB:SVA`; category definitions in
   Bryant's PhD technical report
   [UCAM-CL-TR-938](https://www.cl.cam.ac.uk/techreports/UCAM-CL-TR-938.html),
   Ch. 5, DOI 10.48456/tr-938).
2. **GEC shared-task evaluation is ERRANT-based over the W&I+LOCNESS corpus.**
   Bryant, Felice, Andersen & Briscoe 2019, *The BEA-2019 Shared Task on
   Grammatical Error Correction* ([W19-4406](https://aclanthology.org/W19-4406/))
   + the [BEA-2019 shared-task page](https://www.cl.cam.ac.uk/research/nl/bea2019st/)
   (evaluation migrated to ERRANT v3; W&I+LOCNESS introduced as the shared-task
   dataset).
3. **Historical text normalization is reported word-level, character-level,
   with segmentation as a first-class problem.**
   Bollmann 2019, *A Large-Scale Comparison of Historical Text Normalization
   Systems* (NAACL-HLT 2019, [N19-1389](https://aclanthology.org/N19-1389/),
   DOI 10.18653/v1/N19-1389; eight languages, word-level normalization accuracy)
   + Baron & Rayson 2008, *VARD2: a tool for dealing with spelling variation in
   historical corpora* ([Lancaster eprints 41666](https://eprints.lancs.ac.uk/id/eprint/41666/)),
   whose character-edit-rule framing (including character confusion sets) is the
   reporting vocabulary for letter-level variants.
4. **The MWSA framing is the existing validation lineage.**
   [ELEXIS MWSA shared task](https://elex.is/mwsa2020/) (GlobaLex 2020 workshop
   at LREC 2020, organised by McCrae & Ahmadi) +
   [elexis-eu/MWSA](https://github.com/elexis-eu/MWSA) datasets (17 datasets, 15
   languages). Already cited in the DATASHEET; re-verified here, not re-derived.

**Verification discipline note.** One guessed anthology ID was caught by the
verification pass itself: N19-1090 (fetched) is *not* Bollmann 2019 — the
correct ID is N19-1389. Every URL in the log was fetched, not recalled; this is
the defect class this handoff removes.

## 3. The two axes and what maps

- **Axis B (edit-type)** maps, cell-by-cell, to the table below: nine values,
  four PLACEABLE, four PARTIAL (nearest category carries a named caveat), two
  UNPLACEABLE (`source-raw`, `none`).
- **Axis A (location)** has **no published analogue** in ERRANT, the GEC shared
  tasks, or historical text normalization — all three annotate sentence-internal
  edits and carry no entry-microstructure semantics (headword vs sense vs
  citation). A GEC- or normalization-native reading of any OBS-T event can
  recover the edit-*type* class; it cannot recover the location class. This is
  the same *where vs what-kind* orthogonality the paper argues for internally
  (§4.3, the 0.1 % silver-agreement result), seen from the outside: the
  published schemes measure only *what kind*.

## 4. Per-cell crosswalk

<!-- BEGIN GENERATED per-cell table (scripts/obs_t_errant_gec_crosswalk.py) -- DO NOT HAND-EDIT -->

Per-cell crosswalk over the released corpus — 52,498 events, 57 occupied (location × edit-type) cells (the full label vocabulary admits 8 locations × 9 edit-types = 72 cells; `crossref` occurs 0 times in the release and is reported absent rather than invented, leaving 63 addressable cells, of which 57 are occupied). Ordered by event volume.

| location | edit-type | events | share | nearest ERRANT/GEC category | nearest historical-normalization term | placement | caveat |
|---|---|---:|---:|---|---|---|---|
| unattributed | spelling | 5,780 | 11.0% | R:SPELL | word-form variant (normalization target) | **PLACEABLE** | ERRANT R:SPELL covers letter-changing misspellings (README worked example); OBS-T spelling edits over romanised Sanskrit are the same class of surface letter repair. |
| sense | source-raw | 5,604 | 10.7% | — | — | **UNPLACEABLE** | Edits typed in the raw SLP1/markup character space are transliteration- or markup-space operations, not natural-language surface errors; neither ERRANT/GEC nor historical normalization has a category for them. |
| sense | punctuation | 5,430 | 10.3% | M:/R:/U:PUNCT | not a normalization category (punctuation modernisation is reported separately) | **PLACEABLE** | Direct map to ERRANT's punctuation class. |
| headword | spelling | 3,836 | 7.3% | R:SPELL | word-form variant (normalization target) | **PLACEABLE** | ERRANT R:SPELL covers letter-changing misspellings (README worked example); OBS-T spelling edits over romanised Sanskrit are the same class of surface letter repair. |
| unattributed | case | 3,752 | 7.1% | R:ORTH | not a normalization category (orthography fixed in the target language) | **PLACEABLE** | R:ORTH is ERRANT's orthographic (case-preserving-letters) class; OBS-T case edits on romanised forms map to it directly. |
| sense | spacing | 3,488 | 6.6% | M:/R:/U:PUNCT (token-boundary operation) | segmentation (word merge/split) | **PARTIAL** | ERRANT expresses merges/splits as punctuation-adjacent M/R/U operations on the token boundary; the exact v3 subcategory for pure whitespace was not verified against the full category table in this pass, so the assignment is stated at operation level. |
| unattributed | diacritic | 2,906 | 5.5% | R:SPELL | character-level variant (diacritic recovery) | **PARTIAL** | ERRANT has no dedicated diacritic class (English-centric); a combining-mark fix is a letter-level substitution nearest R:SPELL. Historical-normalization evaluation counts these as character-level variants. |
| unattributed | punctuation | 2,607 | 5.0% | M:/R:/U:PUNCT | not a normalization category (punctuation modernisation is reported separately) | **PLACEABLE** | Direct map to ERRANT's punctuation class. |
| markup | spacing | 2,359 | 4.5% | M:/R:/U:PUNCT (token-boundary operation) | segmentation (word merge/split) | **PARTIAL** | ERRANT expresses merges/splits as punctuation-adjacent M/R/U operations on the token boundary; the exact v3 subcategory for pure whitespace was not verified against the full category table in this pass, so the assignment is stated at operation level. |
| citation | spacing | 2,238 | 4.3% | M:/R:/U:PUNCT (token-boundary operation) | segmentation (word merge/split) | **PARTIAL** | ERRANT expresses merges/splits as punctuation-adjacent M/R/U operations on the token boundary; the exact v3 subcategory for pure whitespace was not verified against the full category table in this pass, so the assignment is stated at operation level. |
| markup | source-raw | 1,774 | 3.4% | — | — | **UNPLACEABLE** | Edits typed in the raw SLP1/markup character space are transliteration- or markup-space operations, not natural-language surface errors; neither ERRANT/GEC nor historical normalization has a category for them. |
| unattributed | spacing | 1,696 | 3.2% | M:/R:/U:PUNCT (token-boundary operation) | segmentation (word merge/split) | **PARTIAL** | ERRANT expresses merges/splits as punctuation-adjacent M/R/U operations on the token boundary; the exact v3 subcategory for pure whitespace was not verified against the full category table in this pass, so the assignment is stated at operation level. |
| sense | spelling | 1,637 | 3.1% | R:SPELL | word-form variant (normalization target) | **PLACEABLE** | ERRANT R:SPELL covers letter-changing misspellings (README worked example); OBS-T spelling edits over romanised Sanskrit are the same class of surface letter repair. |
| unattributed | digit | 1,359 | 2.6% | R:/M:OTHER | not a normalization category | **PARTIAL** | ERRANT has no dedicated numeric class; nearest is OTHER. Kept visible rather than folded into spelling. |
| headword | diacritic | 1,221 | 2.3% | R:SPELL | character-level variant (diacritic recovery) | **PARTIAL** | ERRANT has no dedicated diacritic class (English-centric); a combining-mark fix is a letter-level substitution nearest R:SPELL. Historical-normalization evaluation counts these as character-level variants. |
| markup | punctuation | 1,006 | 1.9% | M:/R:/U:PUNCT | not a normalization category (punctuation modernisation is reported separately) | **PLACEABLE** | Direct map to ERRANT's punctuation class. |
| sense | diacritic | 637 | 1.2% | R:SPELL | character-level variant (diacritic recovery) | **PARTIAL** | ERRANT has no dedicated diacritic class (English-centric); a combining-mark fix is a letter-level substitution nearest R:SPELL. Historical-normalization evaluation counts these as character-level variants. |
| unattributed | none | 481 | 0.9% | — | — | **UNPLACEABLE** | No typed edit operation in the trace (identity/metadata events); no external scheme places an empty edit. |
| sense | none | 435 | 0.8% | — | — | **UNPLACEABLE** | No typed edit operation in the trace (identity/metadata events); no external scheme places an empty edit. |
| meta | digit | 415 | 0.8% | R:/M:OTHER | not a normalization category | **PARTIAL** | ERRANT has no dedicated numeric class; nearest is OTHER. Kept visible rather than folded into spelling. |
| citation | digit | 413 | 0.8% | R:/M:OTHER | not a normalization category | **PARTIAL** | ERRANT has no dedicated numeric class; nearest is OTHER. Kept visible rather than folded into spelling. |
| markup | spelling | 342 | 0.7% | R:SPELL | word-form variant (normalization target) | **PLACEABLE** | ERRANT R:SPELL covers letter-changing misspellings (README worked example); OBS-T spelling edits over romanised Sanskrit are the same class of surface letter repair. |
| markup | digit | 316 | 0.6% | R:/M:OTHER | not a normalization category | **PARTIAL** | ERRANT has no dedicated numeric class; nearest is OTHER. Kept visible rather than folded into spelling. |
| citation | punctuation | 310 | 0.6% | M:/R:/U:PUNCT | not a normalization category (punctuation modernisation is reported separately) | **PLACEABLE** | Direct map to ERRANT's punctuation class. |
| sense | digit | 288 | 0.5% | R:/M:OTHER | not a normalization category | **PARTIAL** | ERRANT has no dedicated numeric class; nearest is OTHER. Kept visible rather than folded into spelling. |
| sense | transposition | 254 | 0.5% | R:SPELL / R:OTHER | metathesis (classical scribal category) | **PARTIAL** | ERRANT has no transposition operation; a token-internal letter swap lands in SPELL/OTHER. Textual criticism (Katre) and OBS-T's own OCR class name it metathesis/transposition — the honest home. |
| citation | source-raw | 249 | 0.5% | — | — | **UNPLACEABLE** | Edits typed in the raw SLP1/markup character space are transliteration- or markup-space operations, not natural-language surface errors; neither ERRANT/GEC nor historical normalization has a category for them. |
| headword | spacing | 230 | 0.4% | M:/R:/U:PUNCT (token-boundary operation) | segmentation (word merge/split) | **PARTIAL** | ERRANT expresses merges/splits as punctuation-adjacent M/R/U operations on the token boundary; the exact v3 subcategory for pure whitespace was not verified against the full category table in this pass, so the assignment is stated at operation level. |
| grammar | spacing | 204 | 0.4% | M:/R:/U:PUNCT (token-boundary operation) | segmentation (word merge/split) | **PARTIAL** | ERRANT expresses merges/splits as punctuation-adjacent M/R/U operations on the token boundary; the exact v3 subcategory for pure whitespace was not verified against the full category table in this pass, so the assignment is stated at operation level. |
| headword | none | 169 | 0.3% | — | — | **UNPLACEABLE** | No typed edit operation in the trace (identity/metadata events); no external scheme places an empty edit. |
| meta | source-raw | 167 | 0.3% | — | — | **UNPLACEABLE** | Edits typed in the raw SLP1/markup character space are transliteration- or markup-space operations, not natural-language surface errors; neither ERRANT/GEC nor historical normalization has a category for them. |
| unattributed | transposition | 162 | 0.3% | R:SPELL / R:OTHER | metathesis (classical scribal category) | **PARTIAL** | ERRANT has no transposition operation; a token-internal letter swap lands in SPELL/OTHER. Textual criticism (Katre) and OBS-T's own OCR class name it metathesis/transposition — the honest home. |
| headword | punctuation | 129 | 0.2% | M:/R:/U:PUNCT | not a normalization category (punctuation modernisation is reported separately) | **PLACEABLE** | Direct map to ERRANT's punctuation class. |
| headword | digit | 116 | 0.2% | R:/M:OTHER | not a normalization category | **PARTIAL** | ERRANT has no dedicated numeric class; nearest is OTHER. Kept visible rather than folded into spelling. |
| markup | none | 90 | 0.2% | — | — | **UNPLACEABLE** | No typed edit operation in the trace (identity/metadata events); no external scheme places an empty edit. |
| citation | spelling | 71 | 0.1% | R:SPELL | word-form variant (normalization target) | **PLACEABLE** | ERRANT R:SPELL covers letter-changing misspellings (README worked example); OBS-T spelling edits over romanised Sanskrit are the same class of surface letter repair. |
| headword | transposition | 66 | 0.1% | R:SPELL / R:OTHER | metathesis (classical scribal category) | **PARTIAL** | ERRANT has no transposition operation; a token-internal letter swap lands in SPELL/OTHER. Textual criticism (Katre) and OBS-T's own OCR class name it metathesis/transposition — the honest home. |
| grammar | source-raw | 57 | 0.1% | — | — | **UNPLACEABLE** | Edits typed in the raw SLP1/markup character space are transliteration- or markup-space operations, not natural-language surface errors; neither ERRANT/GEC nor historical normalization has a category for them. |
| headword | case | 55 | 0.1% | R:ORTH | not a normalization category (orthography fixed in the target language) | **PLACEABLE** | R:ORTH is ERRANT's orthographic (case-preserving-letters) class; OBS-T case edits on romanised forms map to it directly. |
| citation | none | 43 | 0.1% | — | — | **UNPLACEABLE** | No typed edit operation in the trace (identity/metadata events); no external scheme places an empty edit. |
| meta | spacing | 18 | 0.0% | M:/R:/U:PUNCT (token-boundary operation) | segmentation (word merge/split) | **PARTIAL** | ERRANT expresses merges/splits as punctuation-adjacent M/R/U operations on the token boundary; the exact v3 subcategory for pure whitespace was not verified against the full category table in this pass, so the assignment is stated at operation level. |
| grammar | punctuation | 14 | 0.0% | M:/R:/U:PUNCT | not a normalization category (punctuation modernisation is reported separately) | **PLACEABLE** | Direct map to ERRANT's punctuation class. |
| markup | diacritic | 13 | 0.0% | R:SPELL | character-level variant (diacritic recovery) | **PARTIAL** | ERRANT has no dedicated diacritic class (English-centric); a combining-mark fix is a letter-level substitution nearest R:SPELL. Historical-normalization evaluation counts these as character-level variants. |
| grammar | spelling | 11 | 0.0% | R:SPELL | word-form variant (normalization target) | **PLACEABLE** | ERRANT R:SPELL covers letter-changing misspellings (README worked example); OBS-T spelling edits over romanised Sanskrit are the same class of surface letter repair. |
| meta | punctuation | 10 | 0.0% | M:/R:/U:PUNCT | not a normalization category (punctuation modernisation is reported separately) | **PLACEABLE** | Direct map to ERRANT's punctuation class. |
| meta | spelling | 6 | 0.0% | R:SPELL | word-form variant (normalization target) | **PLACEABLE** | ERRANT R:SPELL covers letter-changing misspellings (README worked example); OBS-T spelling edits over romanised Sanskrit are the same class of surface letter repair. |
| grammar | none | 6 | 0.0% | — | — | **UNPLACEABLE** | No typed edit operation in the trace (identity/metadata events); no external scheme places an empty edit. |
| sense | case | 5 | 0.0% | R:ORTH | not a normalization category (orthography fixed in the target language) | **PLACEABLE** | R:ORTH is ERRANT's orthographic (case-preserving-letters) class; OBS-T case edits on romanised forms map to it directly. |
| citation | diacritic | 5 | 0.0% | R:SPELL | character-level variant (diacritic recovery) | **PARTIAL** | ERRANT has no dedicated diacritic class (English-centric); a combining-mark fix is a letter-level substitution nearest R:SPELL. Historical-normalization evaluation counts these as character-level variants. |
| citation | transposition | 5 | 0.0% | R:SPELL / R:OTHER | metathesis (classical scribal category) | **PARTIAL** | ERRANT has no transposition operation; a token-internal letter swap lands in SPELL/OTHER. Textual criticism (Katre) and OBS-T's own OCR class name it metathesis/transposition — the honest home. |
| meta | none | 4 | 0.0% | — | — | **UNPLACEABLE** | No typed edit operation in the trace (identity/metadata events); no external scheme places an empty edit. |
| meta | diacritic | 2 | 0.0% | R:SPELL | character-level variant (diacritic recovery) | **PARTIAL** | ERRANT has no dedicated diacritic class (English-centric); a combining-mark fix is a letter-level substitution nearest R:SPELL. Historical-normalization evaluation counts these as character-level variants. |
| markup | transposition | 2 | 0.0% | R:SPELL / R:OTHER | metathesis (classical scribal category) | **PARTIAL** | ERRANT has no transposition operation; a token-internal letter swap lands in SPELL/OTHER. Textual criticism (Katre) and OBS-T's own OCR class name it metathesis/transposition — the honest home. |
| meta | transposition | 2 | 0.0% | R:SPELL / R:OTHER | metathesis (classical scribal category) | **PARTIAL** | ERRANT has no transposition operation; a token-internal letter swap lands in SPELL/OTHER. Textual criticism (Katre) and OBS-T's own OCR class name it metathesis/transposition — the honest home. |
| grammar | diacritic | 1 | 0.0% | R:SPELL | character-level variant (diacritic recovery) | **PARTIAL** | ERRANT has no dedicated diacritic class (English-centric); a combining-mark fix is a letter-level substitution nearest R:SPELL. Historical-normalization evaluation counts these as character-level variants. |
| citation | case | 1 | 0.0% | R:ORTH | not a normalization category (orthography fixed in the target language) | **PLACEABLE** | R:ORTH is ERRANT's orthographic (case-preserving-letters) class; OBS-T case edits on romanised forms map to it directly. |
| headword | source-raw | 1 | 0.0% | — | — | **UNPLACEABLE** | Edits typed in the raw SLP1/markup character space are transliteration- or markup-space operations, not natural-language surface errors; neither ERRANT/GEC nor historical normalization has a category for them. |

**Structural mismatch, stated once for all cells.** ERRANT/GEC/normalization annotate sentence-internal edits and carry no entry-microstructure semantics: the location dimension of every cell rides on OBS-T alone. `unattributed`-location cells (18,743 events) additionally have no location at all — they are reported here for the edit-type half of the cell only.

Status rollup: **PLACEABLE 18 · PARTIAL 26 · UNPLACEABLE 13** cells; by events: PLACEABLE 25,002 / PARTIAL 18,416 / UNPLACEABLE 9,080.

<!-- END GENERATED per-cell table -->




## 5. Honest-mismatch summary

- **UNPLACEABLE by construction:** all `source-raw` cells (raw SLP1/markup-space
  edits — 15.0 % of the corpus) and all `none` cells; these are reported, not
  papered over.
- **PARTIAL by category gap:** `diacritic`, `spacing`, `digit`, `transposition`
  — nearest categories exist but no ERRANT class names them exactly
  (English-centric GEC has no diacritic class and no transposition operation).
- **Location-blind by design (all 57 cells):** the location half of every cell
  rides on OBS-T alone; `crossref` has zero events in the release and is
  reported absent rather than invented.
- **No mapping was invented to fill a gap.** Where the published vocabulary has
  no cell, the table says so.

## 6. Verification

```bash
python scripts/obs_t_errant_gec_crosswalk.py --check
# CHECK PASS: docs/OBST_ERRANT_GEC_CROSSWALK.md generated table is byte-identical
```
