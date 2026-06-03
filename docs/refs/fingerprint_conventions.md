# Convention-fingerprint reference — all 30 L0 dimensions (canonical taxonomy)

**Purpose**: the single source of truth for every fingerprint dimension used in
Phase L0 (and reused by L0.5/L0.6 and the typology papers). It enumerates each
dimension's option set, how it is currently obtained, and — for Patel's canonical
7 — the contrastive states we can measure versus the exact codes that live in
Patel 2016 and must be slotted in by M.G. / V. Patel.

**Companion**: [`../L0_DESIGN.md`](../L0_DESIGN.md) §2 (rationale), [`../L0_RESULTS.md`](../L0_RESULTS.md)
(first tree), [`../L0_PATEL_ANNOTATION.md`](../L0_PATEL_ANNOTATION.md) (the fill-in sheet),
[`concordance.md`](concordance.md) (numbering ↔ Patel 2016 ↔ CSV columns; the stability contract).
**Source of truth for code**: `scripts/L0/s2_fingerprint.py` (DIMS), `s2b_patel_auto.py`, `s2c_patel_evidence.py`.

### Status legend

| Tag | Meaning |
|---|---|
| `auto` | mechanically extracted from source XML by `s2_fingerprint.py` |
| `auto-patel` | mechanically extracted by `s2b_patel_auto.py` (a parseable Patel conv.) |
| `gate` | judgement-bound — awaits M.G. co-annotation (`patel_fillin.csv`) |
| `gate+pdf` | needs Patel 2016's exact option enumeration before annotation is final |

> **Convention on option labels.** The pipeline treats every cell value as a free
> categorical string, so canonical Patel codes (e.g. `1.5`) and descriptive labels
> (e.g. `homorganic`) are interchangeable. Where Patel 2016 enumerates N options we
> have left numbered slots `(c.1)…(c.N)` to be filled with his definitions.

---

## A. Patel's canonical 7 (dims 1–7)

These are V. Patel's 2016 transliteration/citation conventions. Dims 2 & 4 are
mechanically recoverable (now `auto-patel`); the other five are `gate`/`gate+pdf`.

### dim 1 — Anusvāra before consonants  ·  **6 options** · `gate+pdf`
*Phenomenon*: representation of a word-internal nasal before a following consonant.
Measured signal: `anusvāra-share` = (`M`+stop) ÷ (`M`+stop + homorganic-nasal+stop).

Contrastive states we can measure (map to Patel's 6):
- **homorganic** — class nasal per varga: `aṅka, pañca, daṇḍa, anta, ambu` (SLP1 `aNka…`).
- **anusvāra** — `ṃ` before any consonant: `aṃka, paṃca…` (SLP1 `aMka`).
- **anusvāra-before-sibilant-only** — `saṃskāra` but `aṅka` (the common scholarly compromise).
- **mixed / inconsistent**.

Patel's exact 6:
- (1.1) ⟶ _to fill from Patel 2016_
- (1.2) ⟶ …
- (1.3) ⟶ …
- (1.4) ⟶ …
- (1.5) ⟶ …
- (1.6) ⟶ …

Measured (anusvāra-share, 32 sourced dicts): AP90 0.999, LRV 0.565, FRI 0.235; all
others < 0.13 (homorganic). → suggested: AP90/LRV `anusvara`, FRI `mixed`, rest `homorganic`.

### dim 2 — Duplication after r  ·  **2 options** · `auto-patel` ✅
*Phenomenon*: a consonant following a consonant-`r` is geminated (older orthography)
or single (modern). Test: char-level `rCC` vs `rCV`.
- (2.1) **single** — `akarkaSa, akarRa` (modern).
- (2.2) **duplicated** — `akarkkaSa, akarRRa` (older). Intermediate → **mixed**.

Measured: WIL/YAT/SHS/VCP ≈ 0.32–0.34 (`mixed`), SKD 0.41 (`duplicated`); all others ≤ 0.02 (`single`).

### dim 3 — Words ending with -at (śatṛ / vatup-matup)  ·  **5 options (3+2)** · `gate+pdf`
*Phenomenon*: how present participles in `-at` (śatṛ) and possessives in `-vat`/`-mat`
(vatup/matup) are cited. Patel: 3 sub-options for `-at`, 2 for `-vat/-mat`.

Patel's exact options:
- `-at` sub-conventions: (3.1) … (3.2) … (3.3) … ⟶ _to fill_
- `-vat/-mat` sub-conventions: (3.4) … (3.5) … ⟶ _to fill_

Measured counts (per dict): in `patel_fillin.csv` (`-at`/`-vat`/`-mat` + examples).
Notable: GRA `-vat` 274 (Vedic), BOR/AE `-vat` ≈ 1 (English-headword dicts).

### dim 4 — Inflected vs uninflected headword form  ·  **2 options** · `auto-patel` ✅
*Phenomenon*: citation form carries nominative inflection or is the bare stem.
Test: trailing visarga `-H` / neuter anusvāra `-M` rate on `k1`.
- (4.1) **uninflected** — bare stem `aMSa`.
- (4.2) **inflected** — `aMSaH`, neuter `aMSakaM`.

Measured: AP90 0.32, AP 0.27, SKD 0.72 visarga-rate → `inflected`; all others `uninflected`.

### dim 5 — Anusvāra of verbs  ·  **N options** · `gate+pdf`
*Phenomenon*: nasal verbal **roots** cited with anusvāra (`aMS`, `aMh`) vs nasal letter
(`aMs`); some dicts list both as separate root entries.
- (5.1) **anusvara** · (5.2) **nasal-letter** · (5.3) **both/mixed** · (5.4) **n.a.** (no verb roots).
- Patel's exact set ⟶ _to fill_.

Measured: short nasal-root inventory + examples per dict in `patel_fillin.csv`. Index/
reverse dicts (INM, ACC, BOR, AE) → n.a.

### dim 6 — ṛkārānta words (ṛ-final agent nouns)  ·  **3 options** · `gate`
*Phenomenon*: citation of an ṛ-stem agent noun (`kartṛ`).
- (6.1) **stem-f** — bare stem, SLP1 `kartf` (Anglo-Indian / Apte / MW school).
- (6.2) **ar** — `kartar`, SLP1 `…ar` (Böhtlingk–Roth / Petersburg school).
- (6.3) **nominative-A** — `kartā`, SLP1 `…A`.
- Patel's exact 3 ⟶ confirm mapping above.

Measured (f-stem / -ar counts): **PWG 0/134, PW 1, CCS 6, SCH 16** → `ar`; WIL 80, MW72 228,
AP90 222, MD 227, STC 259 etc. → `stem-f`. Clean Petersburg-vs-rest split.

### dim 7 — vas/yas suffixes  ·  **4 options** · `gate+pdf`
*Phenomenon*: spelling/listing of `-vas` (perfect participle, `vidvas`) and `-yas`
(comparative, `garīyas`) stems.
- (7.1) … (7.2) … (7.3) … (7.4) … ⟶ _to fill from Patel 2016_.

Measured: `-vas`/`-yas` counts + examples per dict. GRA 83/81 (Vedic outlier); BOR/AE/SKD/ACC/BHS ≈ 0 → n.a.

---

## B. Added dimensions (8–30) — fully defined, mostly `auto`

Grouped as in L0_DESIGN §2.2–2.9. Option sets here are canonical (no PDF needed).

### Sandhi & compound handling
- **8 Sandhi at compound boundary** · `preserved` | `split` | `both` · `gate` (judgement).
- **9 Compound-headword separation** · `hyphen` | `space` | `merged` · `auto`.
- **10 Variant-headword inclusion (`<k2>`)** · `none` | `few` (<5%) | `many` (>5%) · `auto`.

### Polysemy & sense numbering
- **11 Sense numbering style** · `arabic` | `roman` | `alpha` | `sanskrit` | `unnumbered` · `auto`.
- **12 Sense-internal separator** · `semicolon` | `comma` | `period` | `colon` · `auto`.
- **13 Sub-sense indentation** · `present` | `flat` · `auto`.

### Citation conventions
- **14 Citation depth** · `full` (`Rv. 1.22.16`) | `partial` (`Rv. 1.22`) | `minimal` (`RV.`) | `mixed` · `auto`.
- **15 Citation format style** · `abbreviated` | `full` | `sanskrit` · `auto`.
- **16 Mahābhārata edition reference** · `pune` | `critical` · `gate` (judgement; partial auto-signal `MBh. crit.`).

### Grammar / gender markers
- **17 Grammar marker style** · `abbreviated` (`m./f./n.`) | `full` (`masc./fem./neut.`) | `sanskrit` (`puṃ./strī./napuṃ.`) · `auto`.
- **18 Verb-class marker style** · `roman` (`P.IX`) | `arabic` (`9.P`) | `sanskrit` · `auto`.

### Etymology & cross-reference
- **19 Etymology presence** · `none` | `partial` | `full` · `auto`.
- **20 Cross-reference syntax** · `explicit` (`see X`) | `k1` (`<k1>`) | `italic` | `absent` · `auto`.
- **21 Loanword marker** · `tagged` | `untagged` · `auto`.

### Vedic & accent
- **22 Vedic accent preservation** · `present` (`āgnís`) | `absent` · `auto`.
- **23 Vedic-only marker** · `flagged` | `unflagged` · `auto`.

### Loose ends
- **24 Frequency / rarity marker** · `present` (`(rare)`) | `absent` · `auto`.
- **25 Indeclinable marker style** · `ind` | `inv` | `nipata` | `unmarked` · `auto`.
- **26 Pāṇinian sūtra reference** · `cited` | `uncited` · `auto`.
- **27 Source-language identification** · `present` | `absent` · `auto`.

### Etymology / derivation richness (added 2026-05-16)
- **28 Etymology presence rate** · `>5%` | `<=5%` · `auto`.
- **29 Etymology mean-length** · `low` (<30 ch) | `med` (30–80) | `high` (>80) · `auto`.
- **30 Distinct etym-marker patterns** · `0` | `1` | `>1` · `auto`.

---

## C. Methodological taxonomy (encodings · metrics · algorithms · validation)

Locked in L0_DESIGN §3–§6; current implementation in `s3_cladogram.py`.

**Encodings** — A set-membership (one-hot, → Jaccard); B primary categorical (→ Hamming);
C inconsistency-flagged (categorical + confidence weight). *Note*: stage-2 yields a
primary-only cell, so B/C share one value → 4 live (encoding,metric) configs, not 9.

**Distance metrics** — plain Hamming; weighted Hamming (IDF, weight = −log₂ p(option),
rare-option mismatches cost more); confidence-weighted Hamming; Jaccard (encoding A).
All missing-aware (skip dims unknown in either dict).

**Algorithms** — UPGMA (scipy average linkage); Neighbour-Joining (Saitou–Nei);
Bayesian-consensus *approximated* by 1000× dimension-bootstrap majority-consensus UPGMA
(full MCMC deferred, design §9). Canonical config = `B_whamming`, pre-registered.

**Validation** — (a) known-edge recovery (knn-3 cophenetic / clade ≤ 5; target ≥ 70%);
(b) nearest-neighbour LOO (target ≥ 60%); (c) 1000× bootstrap support + Wilson 95% CI
(strong edge ≥ 0.80); (d) Robinson–Foulds across trees; (e) lineage-family cohesion.

---

## D. Known-edge ground truth (validation targets)

Directed parent → child. Tier A = high-confidence (inventory + sanhw1 containment);
Tier B = scholarly hypothesis under test (not assumed true).

| Edge | Tier | Basis |
|---|---|---|
| WIL → YAT | A | sanhw1 containment 0.926 |
| WIL → SHS | A | 0.953; r-duplication shared |
| YAT → SHS | A | Wilson line |
| PWG → PW | A | 0.938 (abridgement) |
| PW → CCS | A | 0.945 |
| CCS → CAE | A | same author Cappeller |
| MW72 → MW | A | self-expansion 0.896 |
| AP90 → AP | A | revised edition, ~2.6× |
| PWG → MW72 | A | MW72 preface cites PWG vols 1–4 |
| PWG → MW | A | 0.893 |
| PWG → SCH | A | Schmidt = continuation of PWG/PWK |
| BOP → MW | B | Bopp-dependence (0 direct citations; cognate-set test) |
| BEN → MW | B | candidate absorption |

*Multi-volume temporal nuance* (L0_DESIGN §13): PWG 1855–1875 (7 vols) → a PWG→MW72 (1872)
edge applies only to lemmas in vols 1–4 (≈ letters a–p). Range columns live in
`data/dictionary_inventory.csv` (`start_year, end_year, n_volumes, letter_coverage`).

---

## E. Future-phase dimension catalogs (pointers, not duplicated here)

- **L0.5 Nirukta** (WIL `.E.`): dhātu / suffix / upasarga token tables + Pāṇinian
  kṛt/taddhita/uṇādi/samāsa classification — L0_DESIGN §17.
- **L0.6 Subentry**: `Caus./Pass./Desid./Inten./Den./Periphr.` density + nesting depth +
  per-verb derivation matrix — L0_DESIGN §20.
- **Microstructure typology**: 24 verb-entry + 10 nominal dimensions — `../MICROSTRUCTURE-MACROSTRUCTURE.md`.
- **Macrostructure typology**: 20 dimensions — same doc.
- **M3-Bopp cognate-set test** (dim-19/BOP↔MW) — L0_DESIGN §18.

> When any future phase needs a fixed option set, add it to this file so there is one
> canonical taxonomy across the programme.
