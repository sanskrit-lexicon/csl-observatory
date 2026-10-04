# a61-sixdict-sense-seq-matrix-2026-10-04 — full ρ-matrix of sense-sequence concordance, six dictionaries

_Created: 04-10-2026 · Last updated: 04-10-2026_

Evidence release extending [`a61-mwpwg-sense-seq-2026-10-04`](https://github.com/sanskrit-lexicon/csl-observatory/tree/main/data/publication/a61-mwpwg-sense-seq-2026-10-04)
(H5916) from the single MW↔PWG comparison to **all 15 unordered pairs of the six base
dictionaries of the A61 verification base**, under the identical protocol. Anchor line for
A61's evidence programme toward WSC-2027.

**Method (unchanged from H5916).** Meaning order is proxied by the sequence of cited source
works (`<ls>` sigla) inside each entry: for every headword common to both dictionaries
(exact `k1` match), first-occurrence ranks of works cited by BOTH entries are correlated
(Spearman ρ; Kendall τ also recorded); pairs with fewer than three shared works are excluded.
Controls per pair: a within-entry **permutation null** (first-named side's token order
shuffled) and a **cross-lemma null** (entry of lemma X vs entry of a different lemma Y — the
global siglum-order convention floor, e.g. "Vedic sources first"). H5916 shuffled the MW
side; this run shuffles the first-named side of each pair, so on the anchor pair the
permutation null reads 0.068 instead of 0.033 — an order of magnitude below the observed
0.90 either way. All iteration is sorted and each pair's RNG is freshly seeded: reruns are
byte-identical (verified).

**The matrix (median ρ, qualifying pairs n in parentheses).**

| | PWG | PW | MW | SCH | ACC | PWKVN |
|---|---|---|---|---|---|---|
| **PWG** (Böhtlingk–Roth 1855–75) | — | 0.30 (487) | **0.90** (4,943) | −0.50 (20) | — | −0.30 (14) |
| **PW** (kürzerer Fassung 1879–89) | | — | 0.80 (268) | 1.00 (182) | — | 1.00 (381) |
| **MW** (1899) | | | — | 1.00 (7) | — | 1.00 (7) |
| **SCH** (Nachträge 1928) | | | | — | — | 1.00 (204) |
| **ACC** (Aufrecht, Catalogus Catalogorum) | | | | | — | — |
| **PWKVN** (Nachträge zur kürzeren Fassung) | | | | | | — |

**Reading.** The matrix is genealogical to a degree the single pair could not show:

- **PWG×MW 0.90** (n=4,943) — the H5916 result, reproduced digit-for-digit (median, mean
  0.6622, quartiles 0.5/1.0, cross-lemma floor 0.50) against the same data commit.
- **PW×PWG 0.30** (n=487) — the condensation control, reproduced exactly: abridging one's
  own large dictionary flattens citation-rank concordance; the mission's 0.30 anchor holds.
- **PW×MW 0.80** (n=268) — MW tracks the *shorter* Petersburg's order almost as closely as
  the large one's, while the shorter dictionary does not track its own parent's (0.30):
  MW is aligned with the terminal state of the Petersburg line, not merely its 1855–75 state.
- **Supplement saturation at 1.00** — PW×PWKVN (n=381), PW×SCH (n=182), SCH×PWKVN (n=204):
  the Nachträge cite in their parent's order, so the measure saturates. These rows act as
  the method's upper-bound control and are NOT independent attestation.
- **Small-n pairs are fragile** (PWG×SCH n=20, PWG×PWKVN n=14, MW×SCH n=7, MW×PWKVN n=7;
  cross-lemma nulls correspondingly coarse) — read as "too few qualifying pairs to say",
  not as evidence of disorder.
- **ACC is a structural null**: Aufrecht's *Catalogus Catalogorum* carries no `<ls>` markup
  (its citations are plain text in a bio-bibliographic catalog, not a sense dictionary), so
  all five ACC pairs have 0 measurable rows under this protocol. Reported as such; no
  non-comparable tokenizer was invented for it. ACC's semicolon counts are list separators,
  not sense counts, so its `semis_pearson` cells are likewise not interpretable.

**Counts (summary.json).** k1 keys: PWG 106,082 · PW 151,349 · MW 194,083 · SCH 28,455 ·
ACC 32,585 · PWKVN 14,995.

**Reproduce.**

```bash
python3 sixdict_sense_seq_matrix.py <path-to-csl-orig/v02> <outdir>
```

Deterministic (seed 20261004, per-pair RNGs, sorted iteration). Data: csl-orig @ f4c08c5 —
the same commit as the H5916 release. Files:
[sixdict_sense_seq_matrix.py](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/data/publication/a61-sixdict-sense-seq-matrix-2026-10-04/sixdict_sense_seq_matrix.py) ·
[matrix.csv](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/data/publication/a61-sixdict-sense-seq-matrix-2026-10-04/matrix.csv) (per-pair summary rows) ·
[summary.json](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/data/publication/a61-sixdict-sense-seq-matrix-2026-10-04/summary.json) ·
[metrics/](https://github.com/sanskrit-lexicon/csl-observatory/tree/main/data/publication/a61-sixdict-sense-seq-matrix-2026-10-04/metrics) (15 per-lemma CSVs, one per pair; ACC files are header-only).

Provenance: H6051 (Uprava, epic E024), executed by GLM-5.3 (`account:zai-individual-coding-plan/GLM-5.3`)
via ZCode, 04-10-2026; MW×PWG and PW×PWG reproduce H5916 exactly as the run's internal anchors.

_Гасунс_
