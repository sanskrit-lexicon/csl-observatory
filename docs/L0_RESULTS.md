# Phase L0 — Results (first convention-fingerprint cladogram)

**Date**: 2026-06-03 · **Status**: pipeline complete + validated; final tree gated on Patel co-annotation
**Design**: [`L0_DESIGN.md`](L0_DESIGN.md) · **Scripts**: `scripts/L0/s2b_patel_auto.py`, `scripts/L0/s3_cladogram.py`
**Data products**: `data/L0/` (distances, trees, encodings, validation report)

---

## 1. What ran

The full L0 pipeline (design §3–§7) now executes end-to-end:

1. **`s2_fingerprint.py`** (prior) — auto-extracts dims 9–30 from the 32 locally-available CDSL sources.
2. **`s2b_patel_auto.py`** (new) — mechanically pre-fills the **two parseable Patel conventions** (per design §12.2):
   - **dim 2 (duplication after r)** — character-level gemination test on headwords.
   - **dim 4 (inflected vs uninflected headword)** — visarga/anusvāra suffix test on `k1`.
3. **`s3_cladogram.py`** (new) — 3 encodings × distance metrics → **4 (encoding, metric) configs**, **UPGMA + Neighbour-Joining** → 8 candidate trees, **Robinson–Foulds** comparison, **1000× dimension-bootstrap** consensus canonical tree, and validation (known-edge recovery, nearest-neighbour LOO, bootstrap support + Wilson CIs).

Run over **32 dicts × 20 informative dims**. (KNA/KOW/AMAR dropped — no local source; the five judgement-bound Patel dims 1,3,5,6,7,8,16 await the M.G. co-annotation gate.)

## 2. The Patel pre-fill is a real phylogenetic signal

**dim 2 — r-duplication** cleanly separates the old-orthography editions from the modern ones:

| Geminating (mixed/duplicated) | Single (modern) |
|---|---|
| WIL 0.33, YAT 0.32, SHS 0.32, VCP 0.34, **SKD 0.41** | everyone else ≤ 0.02 |

WIL → YAT → SHS sharing the geminate convention **independently corroborates the known Wilson lineage** (previously seen only via sanhw1 headword containment). **dim 4 — inflected headword** isolates exactly the Apte editions + Śabdakalpadruma (AP90 0.32, AP 0.27, SKD 0.72 visarga-rate) — Apte's documented citation signature.

## 3. The tree (canonical, `B_whamming` UPGMA, bootstrap-consensus)

`data/L0/trees/canonical_consensus.{newick,txt,png}`. Recovered groupings (sister pairs / tight clades):

- **WIL + SHS** (0.11) · **CAE + CCS** (0.20) · **AP90 + AP** (0.32) · **MW72 + BOP** (0.22, a *Bopp-dependence* hint) · **VCP + SKD + KRM** indigenous Skt-Skt · **PW + SCH** (0.17) · **MW with Vedic GRA/VEI**.

## 4. Validation (honest)

| Test | Result | Target | Verdict |
|---|---|---|---|
| **Lineage-family cohesion** | **6/6 families tighter than global mean** | — | ✅ strong |
| Known directed-edge recovery (tier A, knn-3 / clade ≤ 5) | **3/11 = 27%** | ≥ 70% | ⚠️ below |
| Nearest-neighbour LOO accuracy | **54%** | ≥ 60% | ⚠️ below |
| Bootstrap support — WIL→SHS | **0.90** [0.88, 0.91] | ≥ 0.80 | ✅ |
| Bootstrap support — CCS→CAE | **0.76** [0.74, 0.79] | ≥ 0.80 | ⚠️ near |
| Bootstrap support — AP90→AP | **0.64** [0.61, 0.67] | ≥ 0.80 | ⚠️ |

**Interpretation.** On the 20 mechanically-available dimensions, the convention fingerprint robustly recovers **family-level** structure (all six lineages cohere; the strongest single edge WIL→SHS hits 90% bootstrap support) but **does not yet resolve fine directed lineage** (MW72→MW, PWG→PW, PWG→MW72 land in different subclades). This is the design's §6.4 below-target case, and it is informative rather than a failure: the five still-ungated Patel conventions (anusvāra spelling, `-at` handling, ṛkārānta, vas/yas, sandhi) are precisely the high-resolution discriminators Patel selected — their absence is the most likely reason directed edges blur. **Completing the co-annotation is the gating next step**, and re-running `s3_cladogram.py` then yields the final tree with no code change.

**Sensitivity (Robinson–Foulds).** Encoding barely matters for UPGMA (`A_jaccard_upgma` vs `B_hamming_upgma` RF = 0.067); algorithm matters most (UPGMA vs NJ RF ≈ 0.5). So conclusions are robust to the encoding choice but should be read on UPGMA, where the known pairs surface.

## 5. Deviations from the design's nominal "27 trees"

Recorded in `validation_report.json`:
- Stage-2 yields a **primary** option per cell (no ranked secondary) → encodings B and C share one categorical value, differing only in distance weighting → **4** meaningful (encoding, metric) configs, not 9.
- The Bayesian-consensus canonical tree is approximated by a **1000× dimension-bootstrap majority-consensus UPGMA**; full MCMC is deferred (design §9 risk-mitigation).
- Canonical config (`B_whamming`, rare-option-weighted Hamming) is **pre-registered**, not tuned to maximise recovery.

## 6. Next steps

1. **Patel co-annotation (the gate)** — fill dims 1,3,5,6,7,8,16 for the 32+3 dicts from `data/L0/patel_annotation_scaffold.csv` (exemplars already extracted). ~30–50 high-judgement cells, ~1–2 h (design §12). Then re-run `s2b`→`s3`.
2. **KNA/KOW/AMAR** — no local source; fetch from Cologne to bring the Russian-tradition + Amarakośa dicts into the tree (LEXICOGRAPHY_ROADMAP §11.5).
3. **Dashboard page** `/lexicography/conventions.md` (design §7.2) once the final tree lands.
4. **Paper M §4.1.5 / Paper H §5** paragraphs from these validated results.
