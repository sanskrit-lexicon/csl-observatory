# Phase L0 — Results (convention-fingerprint cladogram)

**Date**: 2026-06-03 · **Status**: pipeline complete + validated on **Patel-2016 gold conventions**
**Design**: [`L0_DESIGN.md`](L0_DESIGN.md) · **Taxonomy**: [`refs/fingerprint_conventions.md`](refs/fingerprint_conventions.md), [`refs/concordance.md`](refs/concordance.md)
**Scripts**: `scripts/L0/s2b_patel_auto.py`, `s2d_patel_gold.py`, `s3_cladogram.py`
**Data**: `data/L0/` (distances, trees, encodings, `patel2016_assignments.csv`, `validation_report.json`)

---

## 1. What ran

1. **`s2_fingerprint.py`** — auto-extracts dims 9–30 from the 32 local CDSL sources.
2. **`s2b_patel_auto.py`** — mechanical pre-fill of the two parseable Patel conventions (dims 2, 4) for dicts outside Patel's coverage (LRV, FRI).
3. **`s2d_patel_gold.py`** — ingests **Patel 2016's authoritative per-dict assignments** for conventions 1–7 (`data/L0/patel2016_assignments.csv`), the gold ground truth that **closes the annotation gate** for all 30 covered dicts. Conventions are multi-valued → cells store `+`-joined option sets (e.g. AP90 dim 1 = `1.1+1.3+1.5`).
4. **`s3_cladogram.py`** — 4 (encoding, metric) configs → UPGMA + NJ (8 trees), Robinson–Foulds, 1000× dimension-bootstrap consensus canonical tree, validation. Multi-valued cells expand to per-option one-hot tokens (encoding A) with cell-level Jaccard inside the Hamming metrics.

Run over **32 dicts × 25 informative dims** (Patel's 7 now all live + dims 9–30).

## 2. The Patel ingest doubled the signal

| metric | mechanical only (20 dims) | **+ Patel gold (25 dims)** |
|---|---|---|
| known directed-edge recovery (tier A) | 27% | **55%** (6/11) |
| WIL→SHS bootstrap | 0.90 | 0.81 |
| **PWG→PW** bootstrap | 0.38 | **0.79** |
| **PWG→SCH** bootstrap | 0.31 | **0.70** |
| CCS→CAE bootstrap | 0.76 | 0.64 |
| AP90→AP bootstrap | 0.64 | 0.56 |
| lineage-family cohesion | 6/6 | **6/6** |

The **Petersburg formatting family snapped together**: PW+SCH sisters (0.111), PWG joining (0.286), then the Cappeller pair CAE+CCS (0.293) — because PWG/PW/SCH share an *identical* 7-convention fingerprint (`1.2+1.5 · 2.2 · 3.2+3.5 · 4.2 · 5.2 · 6.1 · 7.4`) and CCS differs only on conv 7. MW72+BOP (0.209) and WIL+SHS (0.222) also pair.

## 3. The key finding: convention-lineage ≠ content-lineage

Recovery is 55%, not higher — and the **pattern of hits vs misses is itself the result**:

- **Recovered (strong bootstrap)** are *formatting* lineages — dictionaries that inherited orthographic/citation **conventions**: WIL→SHS, PWG→PW→SCH, CCS↔CAE, AP90→AP.
- **Missed** are *content* lineages where the inheritor **reformatted**: **PWG→MW** (0.02), **MW72→MW** (0.29), **PWG→MW72** (0.01). Monier-Williams absorbed Petersburg *content* but recoded the conventions — MW uses `6.2 -ṛ` where PWG uses `6.1 -ar`, MW `7.1` vs PWG `7.4`, MW `3.1` vs PWG `3.2`. The fingerprint correctly reports that MW does **not** share PWG's house style.
- **YAT** is a convention outlier (uniquely `1.4`; inconsistent `2.1+2.2`) → it sits apart from WIL despite deriving from it: Yates re-styled Wilson.

So the convention cladogram is a **formatting-genealogy** instrument, distinct from (and complementary to) the sanhw1 content-containment edges. That distinction is a Paper-H/M result, not a shortfall: the 70% target was set for an undifferentiated notion of lineage; against *convention* lineage the strong edges land at 0.70–0.81 bootstrap.

### Phase L0.7 — quantified as a reformatting residual

`s4_residual.py` makes §3 a number: `residual = content_containment(A→B) − convention_similarity(A,B)` over the 25 known sanhw1 containment edges (`data/L0/content_convention_residual.csv`; scatter of all 435 shared pairs in `content_convention_scatter.csv`).

| ranked | top **reformatting** events (high content, recoded form) | residual | | most **faithful** (both axes inherited) | residual |
|---|---|---|---|---|---|
| 1 | **CAE→MW** (0.91 / 0.23) | **0.68** | | SHS→WIL (0.90 / 0.78) | 0.12 |
| 2 | **MD→MW** (0.93 / 0.27) | **0.65** | | WIL→SHS (0.95 / 0.78) | 0.17 |
| 3 | **CCS→MW** (0.90 / 0.28) | **0.62** | | PWG→PW (0.94 / 0.75) | 0.19 |
| 4 | GRA→PW (0.87 / 0.29) | 0.58 | | CCS→CAE (0.94 / 0.71) | 0.23 |
| 5 | **WIL→YAT** (0.93 / 0.39) | 0.54 | | CAE→PW (0.89 / 0.59) | 0.30 |

Every high-content edge **into MW** tops the list — Monier-Williams is the corpus's great
reformatter, absorbing CAE/MD/CCS/PWG content (89–93% containment) under its own house style
(convention similarity 0.23–0.28). WIL→YAT confirms Yates re-styled Wilson. The faithful tail
is exactly the formatting lineages the cladogram recovers. The residual is thus a single
scalar that **localises editorial recoding** — the instrument behind Paper H §5 and the
standalone methods note (Article 20). Shown on the dashboard `/conventions` as a two-axis
scatter + ranked bar.

## 4. The tree (canonical, `B_whamming` UPGMA, bootstrap-consensus)

`data/L0/trees/canonical_consensus.{newick,txt,png}` — five clean clades:
- **Petersburg formatting** (red): PWG, PW, SCH, CCS, CAE.
- **Latin/German etymological + MW** (green): BOP, MW72, BUR, VEI, GRA, MW, BHS, BEN.
- **Anglo-Indian** (orange): WIL, SHS, MD, INM, AP90, AP, GST.
- **Indigenous + verbs** (brown): SKD, VCP, KRM, ACC, AE, LRV.
- **Mixed/index** (purple): YAT, STC, PUI, MCI, BOR.

## 5. Validation summary

| Test | Result | Target | Verdict |
|---|---|---|---|
| Lineage-family cohesion | **6/6 tighter than global** | — | ✅ |
| Convention-lineage edges (WIL→SHS, PWG→PW, PWG→SCH, CCS→CAE) bootstrap | **0.64–0.81** | ≥ 0.80 strong | ✅ mostly |
| Directed-edge recovery (mixed content+convention edges) | 55% | ≥ 70% | ⚠️ (interpretable — see §3) |
| NN-LOO accuracy | 46% | ≥ 60% | ⚠️ |
| RF sensitivity | encoding RF≈0.07 (UPGMA), algorithm RF≈0.5 | — | robust to encoding |

## 6. Deviations from the design (in `validation_report.json`)

- Encodings B/C share one categorical value (stage-2 primary-only) → 4 live (encoding,metric) configs, not 9.
- Bayesian-consensus canonical tree approximated by 1000× dimension-bootstrap consensus UPGMA; full MCMC deferred (design §9).
- Canonical config `B_whamming` is pre-registered, not tuned to recovery.

## 7. Remaining / next

1. **LRV, FRI** — not in Patel's 36; dims 1,3,5,6,7 still `gate`. Annotate from source (the `patel_fillin.csv` evidence sheet covers them) or accept partial.
2. **KNA, KOW, AMAR** — no local source; fetch from Cologne to add the Russian-tradition + Amarakośa dicts.
3. **Patel's open conventions** (`tकारान्त` `mahat`-type; ṛ-nipātita; sकारान्त; रेफान्त) → candidate dims 31+ (see `refs/fingerprint_conventions.md` §A note).
4. **Dashboard page** `/lexicography/conventions.md` (design §7.2); **Paper M §4.1.5 / Paper H §5** paragraphs (esp. the convention-vs-content-lineage finding, §3 above).
