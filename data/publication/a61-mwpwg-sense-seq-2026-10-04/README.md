# a61-mwpwg-sense-seq-2026-10-04 — MW↔PWG sense-sequence concordance

_Created: 04-10-2026 · Last updated: 04-10-2026_

Evidence release for the A61 report §7.2: the test of Kapp and Malten's (1997, p. 6)
surmise that "MW has largely followed the order of meanings in PW1".

**Method.** Cross-language sense matching is impractical at full scale, so meaning order is
proxied by the sequence of cited source works (`<ls>` sigla) inside each entry. For every
headword common to MW and PWG (exact `k1` key), the first-occurrence positions of works cited
by BOTH entries were rank-correlated (Spearman ρ, Kendall τ); pairs with fewer than three
shared works are excluded. Controls: within-entry permutation null; cross-lemma null
(MW entry of lemma X vs PWG entry of a different lemma Y — detects global siglum-order
conventions such as "Vedic sources first"); a condensation control (PW vs PWG, the same
author abridging his own dictionary); and the semicolon sense-count Pearson r.

**Headline (summary.json).** 4,943 qualifying pairs of 94,779 exact-key common lemmas
(the locked a61-history-v1.1 release counts 94,753 on normalized keys):

| Measure | Value |
|---|---|
| MW×PWG median ρ | **0.90** (mean 0.66; 67.9% of pairs > 0.5) |
| Cross-lemma null median ρ | 0.50 (mean 0.28) — convention floor |
| Permutation null mean ρ | 0.03 |
| PW×PWG condensation control median ρ | 0.30 (n=487; truncation flattens the measure) |
| Sense-count Pearson r (all common lemmas) | 0.70 |

**Reading.** Entry-specific order agreement is real and large above the convention floor,
but the floor itself is high: both dictionaries order citations by a shared canonical habit.
Consistent with — not proof of — meaning-order following.

**Reproduce.**

```bash
python3 mwpwg_sense_seq.py <path-to-csl-orig/v02> <outdir>
```

Deterministic (seed 20261004). Data: csl-orig @ f4c08c5 (mw.txt 194,083 keys /
286,525 entries; pwg.txt 106,082 keys / 123,366 entries; pw.txt 151,349 keys).
Files: [mwpwg_sense_seq.py](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/data/publication/a61-mwpwg-sense-seq-2026-10-04/mwpwg_sense_seq.py) ·
[metrics.csv](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/data/publication/a61-mwpwg-sense-seq-2026-10-04/metrics.csv) (per-lemma rows) ·
[summary.json](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/data/publication/a61-mwpwg-sense-seq-2026-10-04/summary.json).

Provenance: H5916 (Uprava), executed by GLM-5.3 (`z.ai-individual-coding-plan/GLM-5.3`) via
ZCode, 04-10-2026; DeepSeek-verified against the paper text.

_Гасунс_
