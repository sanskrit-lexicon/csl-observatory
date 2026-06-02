# R2 sense-splitter — first-slice findings (2026-05-31)

First real build of **R2** (the per-dict sense splitter, RESEARCH_LAYER_ROADMAP §5.1), run on the 5 anchor lemmas (`gam`, `dharma`, `rāma`, `iti`, `bodhisattva`) across the 8 Western-tagged dictionaries. Script: [`scripts/lexico/sense_split.py`](../scripts/lexico/sense_split.py). Data: `data/lexico/senses_<dict>.jsonl`, `r2_align_<lemma>.json`, `r2_summary.json`. Deterministic, stdlib-only, reads sibling `csl-orig`.

## What it does

1. **Heuristic per-dict sense split** — each dictionary's own markers: AP `∙²N`, AP90/BEN/BHS `{@N@}`, PWG `<div n="N"> N)/a)`, WIL `.²N`. The MW-family (MW, MW72, SCH) use **no per-sense markers** — a run-on `;`-list — flagged `lumped`.
2. **Sanskrit fingerprint per sense** — the SLP1 tokens it carries (`{#…#}`/`<s>`, headword excluded) **plus** `<ls>` citation sigla.
3. **Cross-dict alignment** — Jaccard overlap of fingerprints (A6 = *anchor on Sanskrit*, no gloss translation).

## Headline results

**① Sanskrit-anchoring aligns senses across the language barrier — with no translation.** For `dharma`:

| Aligned senses | J | Shared Sanskrit anchors | Meaning |
|---|---|---|---|
| `ap#4` ~ `ap90#4` | **1.0** | `ezaH`, `zazWAMSavftterapi` + Ms./Ś. | "Duty, prescribed course of conduct" (same sense, two Apte editions) |
| `ap#3` ~ `ap90#3` | 0.57 | `eka eva …` + Ku./H. | "Religious/moral merit, virtue" |
| **`pwg#b)` ~ `ap#3`** | 0.02 | `suhfdDarmo`, `eka`, `eva`, `yaH` + H. | **German** "Gesetz, Brauch, Vorschrift" ↔ **English** "moral merit, virtue" |

The last row is the proof of concept: a **German** PWG sense aligned to an **English** Apte sense purely through the Sanskrit material they share — exactly what A6 promised.

**② Sense granularity is a *tradition* trait, not (yet) a clean time-trend** — a refinement to H1. Explicit-sense counts for `dharma`, by year:

| Year | Dict | Senses |
|---|---|---|
| 1855 | PWG | 3 divisions (lumps within) |
| 1866 | BEN | 11 explicit |
| 1872 | MW72 | **lumped** (~136 `;`-clauses in one bundle) |
| 1890 | AP90 | 22 explicit |
| 1899 | MW | **lumped** |
| 1953 | BHS | 4 (proper-name senses) |
| 1957 | AP | 23 explicit |

The **Apte family** (AP/AP90) enumerates finely (~22); the **Petersburg/MW family** packs everything into one run-on gloss. So sense-granularity tracks lexicographic *school* more than publication year — H1 must control for family. (Within the Apte family, AP 1957 ≈ AP90 1890 — no inflation, as expected for a revision.)

## Limitations (next iteration → full R2)

- **MW splits a lemma across many `<L>` blocks** (homonyms + compounds; 33 for `dharma`); this slice reads only the first block, so MW's counts undercount. Need homonym-block aggregation (the `<hom>` grouping).
- **Verbs are messier than nominals** — `gam` (conjugation classes, preverb sub-entries) needs verb-specific markers (`€N`); nominal lemmas (`dharma`, `rāma`) are the clean demonstrators here.
- The **lumped clause-count** is a rough "implicit-sense" proxy, not a true sense count.
- Apte **compound** sub-senses may slightly inflate counts (Apte has no clean compound-section marker).

## Next

- Full corpus + homonym aggregation; verb-marker grammar; indigenous (VCP/SKD `iti`-quotation) + reverse (ApteES `Ⓐ/Ⓑ`) cluster grammars.
- The cross-language alignment feeds the **sense-alignment view** and the **divergence map** (maker worklist); the granularity-vs-family result is the empirical seed for **H1** (Paper L).
