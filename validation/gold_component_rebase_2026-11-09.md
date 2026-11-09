_Created: 09-11-2026 · Last updated: 09-11-2026_

# Gold-component axis re-base — H7947 (2026-11-09)

Repair for the H5313 verifier FAIL of 08-11-2026. Verifier findings: (1) no
second-annotator decisions file in the repo (only a synthetic fixture); (2)
`gold_component_2` had 4/390 populated rows; (3) 254/390 `gold_component`
rows carried retired one-axis labels (`encoding`×149, `orthography`×105), so
any kappa was uninterpretable. Scope (H7947): re-base the first-annotator
column onto the current Phase-8 location axis with a committed documented
mapping and a re-run of `obs_t_gold.py --score`; do NOT invent
second-annotator data.

## What changed

- `validation/gold_sample.csv` — `gold_component`: 254 retired rows re-based
  onto the 8-value location axis (`headword`, `grammar`, `citation`, `sense`,
  `crossref`, `meta`, `markup`, `unattributed`); 136 already-on-axis rows
  preserved verbatim. Retired count is now 0/390.
- `validation/gold_sample.csv` — `gold_component_2`: the 4 pre-H5312 legacy
  stragglers cleared (archived below). The column is now 0/390 filled, so
  `--score` reports kappa=None with the "no 2nd annotator yet" reason.
- `validation/gold_component_rebase_mapping_2026-11-09.csv` (this file's
  machine companion): one row per sheet row with old/new labels and the rule
  applied. Retired rows carry rule `H1385-passA-adopted-retired`; preserved
  rows carry `preserved-already-on-axis`.
- `scripts/obs_t_gold_roundtrip_check.py` + `scripts/obs_t_gold.py`
  provenance updated for the new invariant (gold_component_2 = 0) and the
  H7947 scorer (see below).

## Mapping rule

For each of the 254 retired rows, the new label is the H1385 pass-A label
for the same `row_id` from `validation/component_passA.json` (ad862bd,
Opus 4.8 `claude-opus-4-8`, blind, κ=0.906 [0.872–0.938] vs pass-B, n=390,
`validation/component_kappa_stats.json`). This is the adoption path the
harness already names: `obs_t_gold.py --score` and the H5312 closeout both
state that the column must be re-based by adopting the H1385 pass-A labels
or a fresh human pass before quoting any kappa. Pass A is a blind,
pre-registered location-axis annotation of exactly this 390-row sheet, so no
row is relabelled without a documented rule and no second-annotator value is
invented.

The 136 already-on-axis rows are preserved, not overwritten. Of those, 31
disagree with pass A (e.g. row 17 `meta` vs pass-A `citation`, row 28
`headword` vs `meta`); those are listed in the mapping CSV audit and kept as
first-annotator judgment. The resulting column is therefore hybrid —
136 preserved prior gold + 254 pass-A-adopted — and that hybrid provenance is
stated here and in `gold_metrics.json`, not hidden. A future second-annotator
kappa will mix those provenances; a fresh full human pass would remove the
hybrid, and is a human decision outside H7947 (no phase of H7947 authorises
overwriting preserved gold with machine labels wholesale).

Re-based distribution (retired rows → pass A: headword 97, citation 77, sense
44, markup 18, grammar 8, crossref 5, unattributed 4, meta 1; preserved rows
unchanged):

| new label | n |
|---|---:|
| citation | 118 |
| headword | 107 |
| sense | 57 |
| grammar | 36 |
| markup | 32 |
| meta | 31 |
| crossref | 5 |
| unattributed | 4 |

Old distribution for audit: meta 30, citation 41, sense 13, grammar 28,
markup 14, headword 10, encoding 149, orthography 105.

## Cleared legacy second-column values (archived, not deleted history)

Pre-H5312 debris rows, cleared to empty (values preserved here; git history
is the full pre-image):

| row_id | gold_component (pre) | gold_component_2 cleared |
|---:|---|---|
| 28 | headword | meta |
| 339 | headword | meta |
| 344 | grammar | encoding (retired vocabulary) |
| 388 | grammar | citation |

Clearing (rather than keeping n=4 spurious pairs) is what makes `--score`
honestly report kappa=None until a real second-annotator decisions file
lands. No synthetic fixture values were ever ingested into the real sheet;
`validation/fixtures/second_annotator_fixture.json` (`fixture:true`) remains
sandbox-only.

## Second-annotator gate (human:MG)

There is still no real second-annotator decisions file in the repo — only
`validation/fixtures/second_annotator_fixture.json` (synthetic) and the blank
blind sheet `validation/second_annotator_sheet.html`. Supplying real decisions
is a human act (H7947 gate: human:MG) and is NOT part of this repair. Until
MG supplies the decisions file and it is ingested with
`obs_t_gold.py --ingest`, `cohen_kappa` and `krippendorff_alpha_nominal` stay
None with the "no 2nd annotator yet" reason; no kappa is quoted.

## Prove with

- `grep -c` retired: 0 rows with `gold_component` in (`encoding`,
  `orthography`) in `validation/gold_sample.csv` (see mapping CSV).
- `python scripts/obs_t_gold.py --score` → `validation/gold_metrics.json`
  `firstAnnotatorColumn.status = ok (location axis)`, `iaa.pairs = 0`,
  `cohen_kappa = null`, `krippendorff_alpha_nominal = null`; console prints
  "(no 2nd annotator yet)".
- `python scripts/obs_t_gold_roundtrip_check.py` → ROUND-TRIP PASS (sandbox
  ingest still round-trips to kappa; real sheet now carries 0 filled
  `gold_component_2` rows).

## Provenance

- Re-base: H7947 (OxAlpha); executed by Crouton Alpha Free
  (`opencode-go/crouton-alpha-free`) under H3688 (tier token is bookkeeping).
- Pass-A labels: H1385, Opus 4.8 (`claude-opus-4-8`), blind, 21-07-2026.
- Scorer: `scripts/obs_t_gold.py --score` (deterministic stdlib), provenance
  in `validation/gold_metrics.json` updated from H6388 to H7947.

_Dr. Mārcis Gasūns_
