# Concordance — dimension numbering across schemes

**Purpose**: decouple our **operational** fingerprint numbering (the `dim_1…dim_30`
keys baked into every CSV, script, and tree) from **Dhaval Patel's 2016** convention
numbering (the citable source for conventions 1–7). The pipeline is stable on the
L0 IDs; this file is the only place the mapping to external schemes lives, so Patel's
paper order can be confirmed or revised here **without touching code or data**.

**Companion**: [`fingerprint_conventions.md`](fingerprint_conventions.md) (definitions),
[`../L0_DESIGN.md`](../L0_DESIGN.md) §2 (rationale).

---

## Stability contract

1. **`L0-dim-N` is canonical.** Every `data/L0/*.csv` column (`dim_N_value`,
   `dim_N_source`, `dim_N_confidence`), `dim_schema.json` entry, and script keys on
   the integer N. These IDs are **frozen** — never reused or reordered in place.
2. **Human-facing names/order may change freely** — they live in `dim_schema.json`
   (the `name` field) and in this concordance, not in the column keys.
3. **External numbering (Patel 2016, TEI, OntoLex) is recorded here only.** If Patel's
   paper turns out to order his 7 conventions differently from our `dim_1…dim_7`, we
   update the `Patel2016 §` column below — the fingerprint matrix is unaffected.
4. **Retiring a dimension**: mark it `deprecated` in this table and in `dim_schema.json`;
   do not delete the column or renumber survivors (keeps old trees reproducible).

---

## Master concordance (all 30 L0 dimensions)

| L0 dim | CSV column key | slug | category | Patel2016 § | #opts | status |
|---:|---|---|---|:---:|:---:|---|
| 1 | `dim_1_*` | anusvara-before-cons | Patel-orthography | conv. 1 ⟲ | 6 | gate+pdf |
| 2 | `dim_2_*` | r-duplication | Patel-orthography | conv. 2 ⟲ | 2 | auto-patel ✅ |
| 3 | `dim_3_*` | at-ending (śatṛ/vatup) | Patel-orthography | conv. 3 ⟲ | 5 | gate+pdf |
| 4 | `dim_4_*` | inflected-headword | Patel-orthography | conv. 4 ⟲ | 2 | auto-patel ✅ |
| 5 | `dim_5_*` | verb-anusvara | Patel-orthography | conv. 5 ⟲ | N | gate+pdf |
| 6 | `dim_6_*` | rkaranta | Patel-orthography | conv. 6 ⟲ | 3 | gate |
| 7 | `dim_7_*` | vas-yas-suffix | Patel-orthography | conv. 7 ⟲ | 4 | gate+pdf |
| 8 | `dim_8_*` | sandhi-compound-boundary | sandhi/compound | — | 3 | gate |
| 9 | `dim_9_*` | compound-hw-separation | sandhi/compound | — | 3 | auto |
| 10 | `dim_10_*` | variant-hw-k2 | sandhi/compound | — | 3 | auto |
| 11 | `dim_11_*` | sense-numbering | polysemy | — | 5 | auto |
| 12 | `dim_12_*` | sense-separator | polysemy | — | 4 | auto |
| 13 | `dim_13_*` | subsense-indentation | polysemy | — | 2 | auto |
| 14 | `dim_14_*` | citation-depth | citation | — | 4 | auto |
| 15 | `dim_15_*` | citation-format | citation | — | 3 | auto |
| 16 | `dim_16_*` | mahabharata-edition | citation | — | 2 | gate |
| 17 | `dim_17_*` | grammar-marker | grammar | — | 3 | auto |
| 18 | `dim_18_*` | verbclass-marker | grammar | — | 3 | auto |
| 19 | `dim_19_*` | etymology-presence | etymology/xref | — | 3 | auto |
| 20 | `dim_20_*` | xref-syntax | etymology/xref | — | 4 | auto |
| 21 | `dim_21_*` | loanword-marker | etymology/xref | — | 2 | auto |
| 22 | `dim_22_*` | vedic-accent | vedic/accent | — | 2 | auto |
| 23 | `dim_23_*` | vedic-only-marker | vedic/accent | — | 2 | auto |
| 24 | `dim_24_*` | frequency-marker | loose-ends | — | 2 | auto |
| 25 | `dim_25_*` | indeclinable-marker | loose-ends | — | 4 | auto |
| 26 | `dim_26_*` | panini-sutra-ref | loose-ends | — | 2 | auto |
| 27 | `dim_27_*` | source-lang-id | loose-ends | — | 2 | auto |
| 28 | `dim_28_*` | etym-presence-rate | etym-richness | — | 2 | auto |
| 29 | `dim_29_*` | etym-mean-length | etym-richness | — | 3 | auto |
| 30 | `dim_30_*` | etym-marker-patterns | etym-richness | — | 3 | auto |

**Legend.** `Patel2016 §` — the convention's number in Dhaval Patel's 2016 paper;
`⟲` = our assumed mapping, **to be confirmed against the PDF** (see below). `—` = a
project addition, not in Patel 2016. `#opts` — option count (see `fingerprint_conventions.md`).
Status tags as in `fingerprint_conventions.md` (`auto` / `auto-patel` / `gate` / `gate+pdf`).

---

## Patel 2016 ⟶ L0 (the 7 to confirm)

We currently assume Patel's conventions appear in his paper in the same order as our
`dim_1…dim_7`. If his numbering differs, fill the **Patel # / Patel title** columns
from the paper and the `⟲` flags above resolve to `=`.

| our L0 dim | our short name | Patel 2016 conv. # | Patel's own title | confirmed? |
|---:|---|:---:|---|:---:|
| 1 | anusvara-before-cons | _to fill_ | _to fill_ | ☐ |
| 2 | r-duplication | _to fill_ | _to fill_ | ☐ |
| 3 | at-ending | _to fill_ | _to fill_ | ☐ |
| 4 | inflected-headword | _to fill_ | _to fill_ | ☐ |
| 5 | verb-anusvara | _to fill_ | _to fill_ | ☐ |
| 6 | rkaranta | _to fill_ | _to fill_ | ☐ |
| 7 | vas-yas-suffix | _to fill_ | _to fill_ | ☐ |

> Reference: D. Patel & ___, "____" (2016). _Add full citation + stable URL/DOI here._
> The PDF is expected at `data/sources/patel_2016.pdf` (checked by `s1_bootstrap.py`,
> currently `pending`).

---

## Reserved for future external schemes

When the TEI Lex-0 and OntoLex-Lemon exports land (locked decision, SESSION_HANDOFF
§3), add columns mapping each L0 dim to its TEI element / OntoLex property here, so a
single lookup serves all three serialisations.

---

## Change log

| Date | Change |
|---|---|
| 2026-06-03 | Concordance created. Adopted `L0-dim-N` as the frozen operational numbering, decoupled from Patel 2016 (recorded here for citation). No code/data renumbered. |
