# OBS-R / OBS-C — bridge memo to `csl-atlas`

**Status:** bridge / routing memo, not a final paper. **Boundary:** OBS-R
(redundancy/genealogy) and OBS-C (citations) are *dictionary-content* findings,
which per [`docs/BOUNDARY_RULES.md`] belong in **`csl-atlas`**, not here. This memo
records the corpus-wide numbers extracted during the 2026-06-09/10 read-only
probes and **routes each to the existing `csl-atlas` hypothesis it extends**, so a
session working *in* `csl-atlas` can integrate them with
[`docs/HYPOTHESIS_INDEX.md`] rather than creating parallel/contradictory docs.

These are corpus-wide (all 43 dicts) quantifications; the atlas findings they
extend were established on smaller panels. **Do not write these as new standalone
atlas hypotheses — they are quantitative extensions of Type-1 findings.**

---

## OBS-R — redundancy & derivation (extends `M1-M2-MACRO`, `XREF-CORE`, `WIL-SHS-SENSE`, L0)

Corpus-wide numbers (43 dicts, `<k1>` SLP1 keys; provenance below):

| Finding | Value |
|---|---|
| Entry → lemma collapse | 1,495,459 `<L>` entries → **409,011 distinct lemmas = 3.66:1** |
| Lemma redundancy (in ≥2 dicts) | **57.9 %** (independent 42.1 %) |
| Independence band (18-dict core+kosha) | 36.5 %–42.4 % (light norm ≈ surface; lower bound needs anusvāra/visarga folding) |
| Entry split-inflation (raw vs homonym-normalized) | 1,495,459 vs 1,291,215 = **1.158** |
| Structured novelty (unique%) | core mutually derivative (pwg 1.9, pw 4.4, mw 13.0); specialized novel (bhs 57.6, ieg 57.6, skd 37.2, ap 34.7) |
| Stemma (asymmetric containment) | **MW = great absorber** (BOP/BEN/MD/ARMH/ABCH/GRA 88–94 % ⊂ MW); PW second hub; PWKVN⊂SCH sibling |

**Routing to atlas hypotheses:**
- `M1-M2-MACRO` ("MW promotes derivatives to headwords; Petersburg nests them")
  is *exactly* what the 1.158 split-inflation + MW's 194K-key headword count
  quantify corpus-wide. → add the corpus split-inflation figure as evidence.
- `XREF-CORE` ("shared core, not wholesale descent; MW/PWG = lexical-shared-core")
  aligns with the containment stemma. → the asymmetric-containment table is the
  all-dictionary version of the xref-lineage panel.
- `WIL-SHS-SENSE` / inventory note "YAT derived from WIL (~91% mutual containment)"
  — the stemma reproduces this; direction by pub-year + size asymmetry
  (`dictionary_inventory.csv` already carries `year`, `family`, derivation notes).
- L0 `sanhw1_cladogram.newick` / `sanhw1_jaccard.csv` are the existing artifacts;
  OBS-R is the redundancy/independence read of the same data, not a new build.

**Caveat:** `abch` dropped from the `<k1>` pass (its `<L>` lines don't expose
`<k1>` the same way) — parser tweak needed before final numbers.

---

## OBS-C — citations, CORRECTED for two registers (extends `INDIG-CITE`)

The original OBS-C probe counted only `<ls>`-tagged citations and therefore
**undercounted the indigenous citation layer** — exactly the standing atlas
finding `INDIG-CITE` ("SKD/VCP are citation-dense despite low `<ls>` tagging").
The re-probe (2026-06-10) separates the two registers:

**Register A — `<ls>`-tagged (European tradition):**
- **1,234,530 citations**; **59.1 %–59.8 % resolvable** (locator + established
  siglum) → ~41 % (~496K) are the dictionary-to-book gap.
- 13,021 raw sigla → 9,180 normalized (1.4×; MBH.+MBh.=75K, ṚV.+RV.=32K); only
  **2,166 sources cited ≥10×**. Real contribution = abbreviation-family merging.
- Densest: pwg 4.63/entry (570,830), ben 2.81, bhs 2.71, mw 1.09 (311,933), ap 0.69.

**Register B — indigenous `iti`/`ity` quotative (Sanskrit-Sanskrit koshas):**
| Dict | `<ls>` | `iti` citations | iti/entry |
|---|---:|---:|---:|
| skd | 0 | **69,215** | 1.63 |
| vcp | 0 | **22,070** | 0.44 |
| krm | 0 | **6,449** | 3.13 (densest in corpus) |
| gst | 0 | 236 | 0.03 |
| mci | 0 | 245 | 0.09 |
| armh | 0 | 181 | 0.02 |

(`iti` count is a word-boundary proxy — includes some grammatical `iti`; the
register split is unambiguous nonetheless. SKD/VCP/KRM cite Amara, Trikāṇḍaśeṣa,
Śabdaratnāvalī, Viśva, Medinī etc. via `iti <source>`, never `<ls>`.)

**Corrected claim:** CDSL has **two disjoint citation systems**. The 59 %
resolvability result holds for Register A only. For the koshas the
dictionary-to-book problem is *different* — linking `iti <work>` to indigenous
source lexica, not page/verse locators. **Per-dictionary citation density must be
measured per-register**; a single `<ls>`-only metric mis-ranks every kosha as
citation-poor.

**Routing to atlas:** integrate Register B with `INDIG-CITE` /
`MICROSTRUCTURE_ZERO_MEANING` (which already calls for per-dictionary
citation-format normalizers); Register A's resolvability classifier extends
`build-citation-apparatus.mjs` + the `review-source-siglum` queue.

---

## Reproduction

```sh
# OBS-R entry→lemma collapse + per-dict novelty (43 dicts, <k1> keys):
#   awk over v02/*/<code>.txt, dedupe <k1> per dict, multiplicity map
# OBS-R stemma: asymmetric containment from ../csl-atlas/data/sanhw1_jaccard.csv (a_in_b vs b_in_a)
# OBS-C two registers (per dict):
git -C ../csl-orig … ; awk '/^<L>/{ent++} {while(match($0,/<ls>[^<]*<\/ls>/)) ls++;
  c=gsub(/[ ”"(]it[iy]/,"&",$0); iti+=c}'
```

_Full awk bodies in the 2026-06-09/10 probe log / plan file
`tender-wondering-reddy.md`. OBS-Q (org-process, in-scope here) is written up
separately in [`obs_q_correction_sustainability.md`](obs_q_correction_sustainability.md)._
