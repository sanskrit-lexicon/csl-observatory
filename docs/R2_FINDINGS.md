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

## Update — full clusters (2026-05-31, v2)

`sense_split.py` now covers **all four parser families** with **homonym aggregation** (all `<L>` blocks of a lemma, not just the first):

- **Western** (mw, mw72, pwg, ap, ap90, ben, sch, bhs, **wil, cae**) — explicit markers / lumped.
- **Indigenous** (**vcp, skd**) — raw-SLP1 scholastic prose; senses ≈ `iti.`-closed units; fingerprint = `…0` authority sigla (`jE0`=Jaimini) + `"…"`-quoted forms.
- **Reverse** (**ae** / ApteES) — English-keyed, reverse-indexed by its `<s>` Sanskrit equivalents, so a Sanskrit lemma finds the English senses that gloss it (e.g. *dharma* → ae "Duty" = `DarmaH, kartavyaM`).
- **Index** (acc/vei/mci/inm/…) — references, not senses; out of scope.

**Cross-cluster alignment now works** (strong-anchor filter: citation / siglum / content word ≥4 chars):
- `bodhisattva`: **`pwg#1 ~ skd#1`** — PWG (German, Western) ↔ SKD (Sanskrit, indigenous) via shared story-Sanskrit (`jImUtavAhanAt`, `kalpadrumaM`, `kftI`).
- `dharma`: `mw#bundle ~ ben/sch` via shared `<ls>` citations (MBh., Dharmaś.).

**Full-corpus scale proven** (runs in seconds): CAE **40,069** entries → 40,069 senses (1.00/entry — lumps); **BEN 17,310 → 36,177 senses (2.09/entry — enumerates)** — the family contrast holds across the whole dictionary, not just the anchor lemmas.

**Remaining (honest):** the AE reverse index over-matches very common roots (gam → 144 English senses — fine for distinctive words, noisy for `go`-class verbs); SKD headword coverage is partial (works for `Darmma`/`rAma`); indigenous sense-splitting is coarse (`iti`-units); verbs remain coarser than nominals.

## H1 — does sense granularity inflate over time? (family-controlled, full corpus)

[`scripts/lexico/h1_analysis.py`](../scripts/lexico/h1_analysis.py) → [`data/lexico/r2_h1.json`](../data/lexico/r2_h1.json) + `r2_h1.html` (SVG scatter, a Paper-L figure). Metric: **sense-units per entry** over each dictionary's *whole* corpus (explicit markers for enumerating dicts; `;`-meaning-clauses, citations stripped, for lumpers).

**Result: H1 (pure temporal inflation) is NOT supported.** Across 11 general dictionaries 1822–1957, the year-trend is essentially flat — **Pearson r = 0.06** (slope ≈ 0.001 units/year). The variance is captured by **lexicographic family**:

| Family | mean units/entry |
|---|---|
| Benfey | 2.53 |
| Apte | 2.35 |
| Monier-Williams | 2.06 |
| Wilson | 1.80 |
| Cappeller | 1.35 |
| Petersburg | 1.15 |
| indigenous | 1.09 |

**Caveat (recorded):** the per-entry metric is confounded by **headword-splitting policy** — MW splits compounds into ~286k separate short entries, diluting its units/entry (1.22) below MW72 (2.90) despite the same family. That's structural, not temporal, and doesn't change the no-trend conclusion. A fixed simple-lemma panel removes it; corroboration from the anchor lemmas — the enumerating dicts show **no** inflation 1866→1957 (BEN dharma=11, AP90=22, AP=23).

**For Paper L:** sense granularity is a **tradition / marking-style trait, to be controlled for** (a covariate), not a function of date — a clean, defensible result, and a useful corrective to the naïve "later = finer" intuition.

## Next

- Tighten the AE reverse index (rank by equivalent-position); verb-marker grammar; finer indigenous splitting.
- H1 rigour: a fixed simple-lemma panel (≥20 nouns) to remove the headword-splitting confound entirely.
- The cross-language + cross-cluster alignment feeds the **sense-alignment view** (R1 dashboard page) and the **divergence map** (maker worklist); the granularity-by-family result is the empirical seed for **H1** (Paper L), measured family-controlled next.
