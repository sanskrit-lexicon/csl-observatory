# Patel annotation guide — Phase L0 Stage 2 human gate

**Companion file**: [`data/L0/patel_annotation_scaffold.csv`](../../data/L0/patel_annotation_scaffold.csv) (315 rows = 35 dicts × 9 Patel-schema convention dimensions).
**Unblocks**: Stage 3 of phase L0 ([`STAGE_3_DISTANCE.md`](STAGE_3_DISTANCE.md)) and the gated full 30-dim cladogram.

---

## Background

Phase L0 builds a 30-dimensional convention fingerprint per dictionary, defined in [`docs/L0_DESIGN.md`](../L0_DESIGN.md). The deterministic extractor [`scripts/L0/s2_fingerprint.py`](../../scripts/L0/s2_fingerprint.py) auto-fills 21 of the 30 dimensions at ~56% overall cell coverage. The remaining **9 dimensions — dims 1–8 (Patel's 2016 transcription schema) and dim 16 (Mahābhārata edition reference) — require manual judgement** and stay `unknown` until annotated.

This scaffold extracts up to three real exemplar entries per (dict × dim) cell so the annotator can answer without re-reading the source files. The cells that an annotator does not feel confident about can be left blank; cells where the feature simply does not occur in the dictionary (e.g. dim 16 in a dict that never cites the Mahābhārata) should be filled with `n/a` and a one-line note.

---

## Workflow

1. Open `data/L0/patel_annotation_scaffold.csv` in a spreadsheet (utf-8 CSV).
2. Sort or filter as preferred — by `dict` to work one dictionary at a time, by `dim_id` to compare the same convention across the whole corpus.
3. For each row, inspect the three `exemplar_*` columns. They are real entries sampled from the dictionary that exhibit the feature in question; the third may be empty if the dictionary has fewer than three matches.
4. Fill `annotator_value` with the option label that best matches what you see.
5. The placeholder labels in `options_available` (e.g. `opt1|opt2|opt3`) stand in for Patel's 2016 canonical labels, which are not yet in hand. If you have a more descriptive label (e.g. `assimilated`, `preserved`, `mixed`), put it in `annotator_label_if_new` and we will normalise the schema once all annotators agree on it. Leave `annotator_value` blank in that case or set it to your new label.
6. Optionally fill `annotator_confidence` (0.0–1.0) and free-text `annotator_notes` for any caveat or interesting observation.
7. Save the CSV (utf-8). Run the merge step described in §"After completion" below.

---

## The nine dimensions

Read the original Patel (2016) for the full schema once it arrives. Until then, the brief glosses below cover what to look for in the exemplars.

| Dim | Name | What to look for in the exemplars |
|---|---|---|
| 1 | Anusvāra before consonants | Headwords with SLP1 `M` (anusvāra) immediately before a consonant, e.g. `aMSa`, `aMSaka`. Note whether the dictionary retains the anusvāra spelling, replaces it with the homorganic nasal (`aJca`, `anta`, `ampu`), or varies by consonant class. |
| 2 | Duplication after r | Headwords with `r` followed by a consonant. Compare e.g. WIL `akarkkaSa` (doubled `kk`) vs. an alternative `akarkaSa` (single `k`). Some dicts double the post-r consonant consistently; some never; some are mixed. |
| 3 | Words ending with -at | Headwords ending in `-at` (present participles and similar stems), e.g. `aMSumat`, `akzavat`. Note the citation form chosen: bare stem `-at`, full nom.sg. `-an`, both forms, etc. |
| 4 | Inflected vs uninflected headword form | Inspect any three headwords. Is the citation form the lemma stem (e.g. `gam`) or an inflected form (e.g. `gacchati`, `gamati`)? Most CDSL dicts are uninflected, but Patel distinguishes nuances. |
| 5 | Anusvāra of verbs | Verb entries (those whose body contains a class marker `r.` or `cl.`) that contain `M`. The exemplar field shows the verb with a short body snippet. Note whether the anusvāra survives in the present-stem citation. (Only 9 of 35 dicts had enough matches in our sample to populate this row.) |
| 6 | ṛkārānta words | Stems ending in SLP1 `f` (= ṛ), e.g. `aMSayitf`, `aMSuBartf`. Note how the genitive or vocative form is given (compare WIL `aMSuBartf` vs. YAT `aMSuBarttf` with doubled `tt`). |
| 7 | vas/yas suffixes | Stems ending in `-vas` or `-yas` (comparative/superlative adjective stems), e.g. `aRIyas`, `anASvas`. Note the citation form convention. |
| 8 | Sandhi handling at compound boundary | Compound headwords from `k2`, joined with `-` or `—` (e.g. `aMSa-BAj`, `aMSu-jAla`). Note whether the boundary preserves both phonemes intact (`-`) or sandhi has been applied (e.g. `aMSv-`). Many dicts merge compounds into a single token (`aMSuBAj`) — those rows will be empty here. |
| 16 | Mahābhārata edition reference | Citations of the Mahābhārata in `<ls>` tags (e.g. `Mbh. 1, 1, 5`, `MahābhārataAyam.`). Note whether the citation format matches the post-1933 Pune critical edition's chapter/verse numbering or a pre-critical edition's (e.g. Calcutta, Bombay). |

---

## Honest gaps

| Concern | What to do |
|---|---|
| The Patel 2016 PDF is not yet available locally, so `options_available` shows placeholders `opt1|opt2|…`. | Use `annotator_label_if_new` with a descriptive label. We will reconcile labels across annotators after the first pass. |
| 91 of 315 rows have no exemplar in the first column. | The feature does not occur (or occurs rarely) in the first 4,000 entries of that dictionary. Either skip and write `annotator_value=n/a`, or open the source `csl-orig/v02/<code>/<code>.txt` to look further. |
| KNA, KOW, AMAR have `source_available=no`. | The dictionary's source is not under `../csl-orig/v02` — either fetch from the per-dict org repo (`github.com/sanskrit-lexicon/<CODE>`) or skip until we source them. The 27 rows for these three dicts will then stay `unknown`. |
| Dim 5 (anusvāra of verbs) has only 9/35 rows with exemplars. | The combined constraint of "has a verb class marker in the body AND has anusvāra in the headword" is narrow. For the other 26 dicts, look manually at any verb entry — most CDSL dicts mark verbs identifiably. |

---

## After completion

Once the CSV has annotator values, run:

```sh
python scripts/L0/merge_patel_annotations.py   # to be added; will produce a diff and update data/L0/convention_fingerprint.csv
```

The merge step is not yet implemented — it will become trivial once we see what format the annotated rows take (canonical labels vs. free-text labels in `annotator_label_if_new`). After merging, re-run:

```sh
python scripts/L0/s2_fingerprint.py       # rebuild summary with the new annotator cells
python scripts/L0/preview_tree.py         # new 30-dim preview tree
python scripts/L0/tanglegram.py           # updated homoplasy metrics
python scripts/L0/joint_inheritance_table.py   # updated joint-test pair list
```

The gated [`STAGE_3_DISTANCE.md`](STAGE_3_DISTANCE.md) preflight requires `cells_unknown == 0` — i.e. the annotator has reached every cell, even if the answer is `n/a`. The variance check in Stage 3 will then drop any annotated dimension that turns out constant.
