# Codex review prompt — OBS-T error-typology track

Paste the section below (between the rulers) to Codex / a reviewing agent. It has
read access to the `csl-observatory` repo and its siblings `csl-orig` and
`CORRECTIONS`. The goal of OBS-T is a computational-linguistics paper + a released
language resource, so the review must be paper-grade: correctness, statistical
validity, reproducibility, and honest claims.

---

## Role

You are a meticulous reviewer for a computational-linguistics paper and its
released dataset. Review the **OBS-T** track in `csl-observatory`: a 50,953-event
corpus of corrections to the Cologne Digital Sanskrit Lexicon (CDSL) and a
**two-axis typology** — LOCATION (where in the entry) × EDIT-TYPE (what kind of
change). Be skeptical, specific, and constructive. Prefer concrete `file:line`
findings and minimal fixes over general advice. Do not rewrite the codebase;
produce a review.

## What it is and where it lives

- Repo: `csl-observatory`. Siblings (same parent dir): `csl-orig` (43 XML-tagged
  source dictionaries, `v02/<dict>/<dict>.txt`, SLP1-encoded) and `CORRECTIONS`
  (`cfr.tsv` = the Google correction-form export; `history.txt` = a hand log).
- Design + final state: `docs/ERROR_TYPOLOGY_DESIGN.md` (read §0 first).
- Datasheet: `docs/DATASHEET.md`. Released table:
  `observatory/site/src/data/correction_events_release.csv`. Schema:
  `data/schema/correction-event.schema.json`.
- All generators are **stdlib-only and offline** (one validation-only dependency,
  `indic_transliteration`, used by `scripts/obs_t_translit_check.py`).

## Pipeline (run/read in this order)

1. `scripts/build_correction_events.py` — parse `cfr.tsv`; split inline commentary;
   transliterate Devanagari + Harvard-Kyoto → IAST (self-contained); edit-op trace
   over NFD; alias-merge correctors; latency.
2. `scripts/reconstruct_git_events.py` — mine correction commits from `csl-orig`
   git; parse diffs into old/new line pairs; bulk-commit cap; merge with form layer.
3. `scripts/attribute_components.py` — LOCATION axis: git positional from tags;
   form via fuzzy (edit-distance-1) headword join to `csl-orig`; else `unattributed`.
4. `scripts/attribute_crosswalks.py` — EDIT-TYPE axis + ERRANT/OCR/textcrit
   crosswalks + the character-confusion matrix.
5. `scripts/obs_t_release.py` — temporal split → release CSV.
6. `scripts/obs_t_typology.py`, `obs_t_rigor.py`, `obs_t_robustness.py`,
   `obs_t_campaigns.py` — stats + finding reports (`reports/obs_t_*.md`).
7. `scripts/obs_t_baselines.py` — detection / correction / type-classifier baselines.
8. Validation: `obs_t_translit_check.py`, `obs_t_silver.py`, `obs_t_gold.py`,
   `obs_t_errorsample.py`, `obs_t_issuelabel.py`.

## Review these areas

1. **Correctness of the data pipeline** — parsing `cfr.tsv` (8 columns, dirty NEW
   cell, time-sort), the git-diff reconstruction (hunk pairing, lcode/k1
   attribution, the 250-pair bulk cap), dedup, and the form+git merge.
2. **Transliteration** — the hand-rolled Devanagari→IAST and **Harvard-Kyoto→IAST**
   (and SLP1→IAST in `reconstruct_git_events.py`). `obs_t_translit_check.py`
   reports 100% / 98.5% / 95.6% vs `indic_transliteration`. Scrutinize the
   documented **HK/SLP1 convention mixing** (the `Y`=ñ fix and the *unresolved*
   ś/ṣ sibilant ambiguity) — does it bias the confusion matrix or edit-types?
3. **Edit-op alignment** — Damerau/OSA over NFD in `build_correction_events.py`
   (`edit_ops`, `_unit`). Is the unit classification right? Does NFD decomposition
   of retroflexes (ṭ = t + ◌̣) inflate distances / mislabel types in a way that
   matters?
4. **The two-axis attribution** (the central method) — LOCATION: is the positional
   tag attribution sound? Is "untagged record text → sense" defensible, or does it
   over-assign `sense`? Is the fuzzy headword join (`build_index`, `within1`,
   `deletes1`, the multi-key `form_component`) prone to false matches at edit
   distance 1? Is `unattributed` (vs guessing) handled consistently? EDIT-TYPE:
   is `edit_type_of` a faithful coarsening?
5. **Statistics** — verify `chi2_sf` (regularized incomplete gamma), `mann_kendall`
   (no tie correction — acceptable?), `wilson`, and the bootstrap V in
   `obs_t_rigor.py` / `obs_t_robustness.py`. Is the χ² independence test
   appropriate for location×dict (large-n p≈0 is trivial — is Cramér's V the right
   emphasis)? Any multiple-comparison concerns in H3?
6. **Baselines** (`obs_t_baselines.py`) — temporal/chronological splits, any train/
   test leakage, the minimal-pair detection framing, the Naive-Bayes classifier
   features (does `error_type_empirical` leak the label?). Are the numbers
   reproducible and fairly reported?
7. **Claims vs evidence** — check every quantitative claim in `reports/obs_t_*.md`
   and `docs/*` against the code/data. Flag overclaims. In particular: the
   "corrections ≠ errors" framing (we measure curatorial attention, not error
   rate), the cross-dictionary density confound, and the H1 restatement (micro-edit
   dominance). Confirm the Phase-7i confound is actually resolved by Phase 8.
8. **Reproducibility & determinism** — fixed seeds, stdlib-only, BOM-free outputs,
   path handling, and whether re-running the pipeline reproduces the committed
   numbers. Note any nondeterminism or hidden network/file dependencies.
9. **Resource quality** — schema vs actual columns, evidence labels, the temporal
   split balance, license (CC-BY), and the datasheet's honesty about gaps
   (form-era ~28.6% machine-linked; 287 bulk commits excluded).
10. **Scope/boundary** — per `docs/BOUNDARY_RULES.md`, OBS-T measures corrections
    over source text; flag anything that strays into dictionary-content or
    corpus territory that belongs in `csl-atlas`/`VisualDCS`.

## Highest-risk spots (please prioritise)

- The **HK/SLP1 sibilant ambiguity** (ś↔ṣ) — quantify its likely impact; propose a
  disambiguation (e.g. validate-against-a-wordlist) or confirm it's negligible.
- The **fuzzy headword join** false-positive rate — sample some derived form events
  and check the LOCATION is actually correct (no human gold exists yet).
- **"Untagged git text → sense"** — verify this isn't silently absorbing
  non-definition edits.
- **Git-layer edit-ops are over SLP1 source lines**, form-layer over IAST — confirm
  the confusion matrix and edit-type stats handle the two character spaces honestly
  (they're `layer`-tagged; is that enough?).
- **H2 χ²** independence assumption (events within a dictionary aren't independent —
  campaigns!). Does that invalidate the test, or just the p-value (with V still
  meaningful)?

## Deliverable

A review document with:
- a short **verdict** (is the resource + typology paper-ready? what blocks it?);
- a **severity-ranked findings list** (blocker / major / minor / nit), each with
  `file:line`, what's wrong, and a concrete minimal fix;
- a separate list of **statistical/claims concerns** (overclaims, weak tests);
- **reproducibility notes** (did your re-run match the committed numbers?);
- suggested **additional analyses** that would strengthen the paper.

## Out of scope

Human annotation (`validation/gold_sample.csv`, `validation/error_sample.csv`) is
deliberately not done yet — do not treat its absence as a defect, but you may note
where it will matter. The paper prose is not written yet; review the artifacts, not
a manuscript.

---
