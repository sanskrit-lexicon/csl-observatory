# Surface, Not Substance: A Two-Axis Error Typology of Twelve Years of Correction to the Cologne Digital Sanskrit Lexicon

*Draft manuscript for a computational-linguistics / language-resource venue (target:
LREC-COLING; the* International Journal of Lexicography *as a metalexicographic
alternate). Empirical basis: the OBS-T correction-event track — the released corpus
[`correction_events_release.csv`](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/observatory/site/src/data/correction_events_release.csv)
with its datasheet
([`docs/DATASHEET.md`](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/docs/DATASHEET.md)),
the design spec
([`docs/ERROR_TYPOLOGY_DESIGN.md`](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/docs/ERROR_TYPOLOGY_DESIGN.md)),
and the generated findings
([`reports/obs_t_typology.md`](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/reports/obs_t_typology.md),
[`reports/obs_t_rigor.md`](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/reports/obs_t_rigor.md),
[`reports/obs_t_baselines.md`](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/reports/obs_t_baselines.md),
[`reports/obs_t_silver.md`](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/reports/obs_t_silver.md)).
Process companion to the correction-sustainability finding OBS-Q
([`reports/obs_q_correction_sustainability.md`](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/reports/obs_q_correction_sustainability.md));
lexicographic-structure companion to the* csl-atlas *microstructure papers. All counts
are the 2026-06-12 snapshot and reproducible from committed data and stdlib-only
scripts. Author: M. Gasūns and the CDSL community (byline to finalise).*

---

## Abstract

We present a twelve-year, **50,953-event** corpus of corrections to the Cologne Digital
Sanskrit Lexicon (CDSL — 43 dictionaries, 210 named correctors, 2014–2026) and a
**two-axis typology** of the errors those corrections repair. Unifying a 2014–2019
correction-form archive with the 2019–2026 source git history, we normalise every edit
to IAST — which requires resolving the form archive's mixed Devanagari/Harvard-Kyoto
encoding, a finding in itself — and describe each correction on two orthogonal axes: its
**location** in the dictionary microstructure (headword, sense, citation, markup, …),
recovered by joining the edit to the XML-tagged source, and its **edit-type** (spelling,
punctuation, spacing, diacritic, …), read from a character-level edit-operation trace.
The two axes are genuinely orthogonal: a location-join and an edit-type heuristic that a
naïve single-axis design conflated agree only 0.1 % of the time, a near-zero we show to
be structural, not noise. Three results follow. **(H1)** Corrections concentrate in the
**meaning-bearing fields** — sense 53 %, headword 22 % of located edits — yet are
**overwhelmingly small surface fixes**, not content rewrites: median edit distance 2,
two-thirds ≤ 2 characters, and the minor-edit rate stays high *even in* the sense
(69.8 %) and headword (81.5 %) fields. **(H2)** The location profile differs sharply by
dictionary (χ² = 23 674, Cramér's V = 0.415). **(H3)** The profile shifts over twelve
years: headword corrections fall (0.90 → 0.12 of the yearly share), markup and metadata
rise, and a stable character-confusion signal led by *b*/*v* emerges. We release the
corpus with per-event evidence labels, three crosswalk typologies (ERRANT, OCR, Katre
textual-criticism), a temporal train/test split, and reference baselines for error
detection, correction and type classification. The central interpretive caveat is stated
plainly: these are *corrected* events — a measure of curatorial attention — not a raw
error rate.

**Keywords:** error typology; digital lexicography; Sanskrit; correction corpus;
language resource; edit operations; diachronic analysis; ERRANT; Cologne Digital
Sanskrit Lexicon.

---

## 1. Introduction

Digitised historical dictionaries are corrected continuously after publication, and the
record of those corrections is itself a dataset — one that answers a question rarely
asked of a dictionary: not *what does it say* but *what was wrong with it, where, and how
did that change over time*. For the Cologne Digital Sanskrit Lexicon (CDSL), the largest
digital Sanskrit lexicographic resource, that record spans twelve years, two distinct
collection regimes (a public correction form, then a source git repository), forty-three
dictionaries and several hundred contributors. This paper assembles it into a single
typed corpus and reads an error typology off it.

The analysis is enabled by a data advantage particular to this project: we hold both the
corrections **and** the XML-tagged source files (`csl-orig`) locally, so each edit can be
located inside the dictionary microstructure it repairs — a headword versus a definition
versus a source citation — rather than treated as an undifferentiated string change. That
single capability is what turns a changelog into a typology.

Our contributions are: (i) a unified, IAST-normalised, evidence-labelled corpus of 50,953
correction events with full provenance across five data layers (§3); (ii) a **two-axis
typology** — *location* × *edit-type* — whose orthogonality we establish empirically
(§4); (iii) three tested findings on the shape, dictionary-dependence and diachrony of the
error profile (§5); and (iv) a released language resource with a temporal split and
reference baselines for Sanskrit error detection, correction and type classification (§6).
Throughout, we keep one caveat in view and return to it in §7: the corpus measures
*corrected* errors — where curators chose to act — not the latent error rate of any
dictionary.

## 2. Background and framing

**Two questions, two tracks.** A companion finding (OBS-Q) measures the correction
*process* — who corrects, when, and how fast. This paper (OBS-T) measures the corrected
*content* — what was wrong and where. The two share an identity-resolution layer (named,
alias-merged contributors) but answer different questions.

**Why two axes.** Error typologies in the adjacent literatures are single-axis by
construction: ERRANT (Bryant et al. 2017) types grammatical-error edits by an
operation × part-of-speech scheme; the OCR/digitisation literature types by
substitution/segmentation/reading-order; classical textual criticism (Katre 1941) types
by omission/addition/substitution/transposition. Each is a *kind-of-change* taxonomy. The
dictionary adds a second, orthogonal question those schemes do not ask — *which part of
the entry* was repaired — and we show (§4.3) that collapsing the two into one column,
as our own first design did, is a measurable error. We therefore report the typology as
two axes and crosswalk the edit-type axis to all three external schemes so reviewers from
any tradition can read it.

**Relation to the lexicographic-structure work.** The *interpretation* of the location
axis — what it means that a dictionary's errors sit in its citations versus its
definitions — connects to the microstructure analyses in the sibling `csl-atlas` project
(citation registers, sense inheritance, indigenous microstructure). Here the object of
analysis is strictly the corrections and commits over the source text, in keeping with the
observatory's boundary rule; the structural reading is cross-linked, not duplicated.

## 3. Data

### 3.1 Five layers, one schema

The corpus unifies five provenance layers (Table 1), each event stamped with its
`source_layer` so any figure can be sliced or audited by origin. The 2014–2019
correction-form export (L1) is the richest per event (it carries the corrector's own
free-text description); the `csl-orig` git history (L2) is the largest and extends the
record to the present; formal change-batches (L4) cover the recent curated campaigns.

**Table 1.** Provenance layers.

| Layer | Source | Era | Per-event richness |
|---|---|---|---|
| L1 correction-form responses | `cfr.tsv` (24,441 rows) | 2014–2019 | highest (old/new/type/who/when) |
| L2 `csl-orig` git diffs | source repository | 2014–2026 | high (old/new from diff hunks) |
| L3 hand log + printchange | history / printchange files | 2014–2019 | medium (campaign-level) |
| L4 formal change-batches | `csl-corrections` | 2024–2026 | high (paired old/new lines) |
| L5 org-metrics backdrop | observatory CSVs | 2014–2026 | aggregate (reused) |

One row is one correction event: a dated old→new edit to a dictionary source, with
dictionary, headword, normalised old/new strings, a verbatim audit copy, an edit-op
trace, both typology axes, three crosswalk columns, the resolved corrector, and an
**evidence label** — `observed` (present in the source cell), `derived` (a deterministic
rule succeeded), or `inferred` (a heuristic). No figure in this paper hides that label.

### 3.2 The encoding problem

Normalising the form archive to IAST is not a formality. The form cells are
**mixed-encoding across dictionaries** — some correctors typed Devanagari, others
Harvard-Kyoto romanisation (`bharahezaravRtti` = *bharaheśaravṛtti*), while the
`csl-orig` sources are SLP1. We route Devanagari runs and HK-looking roman tokens through
two self-contained transliterators to a common IAST (NFC for display, NFD for
diacritic-level edit operations). The heterogeneity is itself a result: a single
historical correction archive can carry three transliteration systems, and any
cross-dictionary statistic that does not unify them first will mis-segment the edits.

## 4. Method

### 4.1 The edit-operation trace

For every event we compute a Damerau–Levenshtein alignment over **NFD** characters — so a
diacritic is its own combining character and therefore its own edit — yielding a typed op
list (`sub`/`ins`/`del`/`transpose` × `diacritic`/`vowel`/`consonant`/`whitespace`/
`punctuation`/`digit`/…). This trace drives both the edit-type axis and the three external
crosswalks, and gives the edit-distance statistics of §5.4.

### 4.2 Axis A — location

Each event is attributed to the microstructure component it repairs by joining to the
`csl-orig` record and locating the changed text among its XML tags (`<k1>`/`<h>` →
headword, `<lex>` → grammar, `<ls>` → citation, definition prose → sense, tag delimiters
→ markup, …). On the **git layer the join is 100 % positional** — the changed source line
carries its own tags — so location is read off directly. On the **form layer only 28.8 %
join**, for two legacy-data reasons we report rather than hide: the form's "L-code" cell
is free text, and the 2014-era sequential record ids have **drifted** against today's
sources (a form pointer to record 4477 once meant *utkaṇṭhā*; that slot now holds
*utkalaṃ*). Location is reported on **derived labels only** — join failures are labelled
`unattributed`, never guessed.

### 4.3 Why two axes, established empirically

Our first design used a single "component" column, filling it from the location-join where
possible and from an edit-type heuristic otherwise. A human-free reliability check exposed
the mistake: on the 6,969 form events where both signals are available, they agree only
**0.1 %** of the time
([`obs_t_silver.md`](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/reports/obs_t_silver.md)).
That near-zero is structural — the join answers *where* (a headword typo → `headword`)
while the heuristic answers *what kind* (a typo → `orthography`); they disagree because
they measure different things. The fix is the two-axis design: derive **location** from
the source join, keep **edit-type** in its own axis and in the ERRANT/OCR crosswalks, and
never file a type value into the location column. The 0.1 % is thus not a data-quality
failure but the measurement that justifies the paper's central methodological move.

### 4.4 Crosswalks

The edit-type axis is additionally typed under three external schemes from the same op
trace: **ERRANT** (operation × unit), **OCR/digitisation** (substitution / segmentation /
insertion / deletion / transposition), and **textual criticism** (Katre 1941:
substitution / omission / addition / transposition, plus haplography / dittography /
metathesis). One corpus, four readings.

## 5. Results

### 5.1 Headline

50,953 correction events over **2014-03-18 to 2026-05-30**, across 43 dictionaries and 210
named correctors; **65.9 % carry a derived (non-heuristic) label** (33,561 derived /
17,392 inferred). Where the form layer records a resolution date, the median
correction latency is **12 days** (p90 73, max 447).

### 5.2 Axis A — where corrections land

On derived labels (n = 33,561), corrections concentrate in the **meaning-bearing
fields**, not in markup or metadata (Table 2).

**Table 2.** Location of corrections (derived labels).

| Location | Events | Share |
|---|---:|---:|
| sense (definition) | 17,880 | 53.3 % |
| headword | 7,282 | 21.7 % |
| markup | 3,945 | 11.8 % |
| citation | 3,338 | 9.9 % |
| meta | 822 | 2.4 % |
| grammar | 294 | 0.9 % |

### 5.3 Axis B — what kind of change

Every edit-type is a surface change; the corpus contains **no "content rewrite" category**
(Table 3, all 50,953 events).

**Table 3.** Edit-type of corrections.

| Edit type | Events | Share |
|---|---:|---:|
| spelling | 16,953 | 33.3 % |
| punctuation | 10,193 | 20.0 % |
| spacing | 9,725 | 19.1 % |
| diacritic | 5,396 | 10.6 % |
| case | 4,432 | 8.7 % |
| digit | 2,632 | 5.2 % |
| (none) | 890 | 1.7 % |
| transposition | 732 | 1.4 % |

### 5.4 H1 — surface, not substance, at *every* location

Corrections are small. The median edit distance is **2**, two-thirds (**66 %**) are ≤ 2
characters (p90 18, max 404). The finding that matters is that this holds **across
locations** — even where meaning lives, the corrections are small form fixes rather than
redefinitions (Table 4). A sense correction is, in two cases out of three, a typo or
spacing repair in a definition, not a reglossing.

**Table 4.** Minor-edit rate (small surface edit) by location, with 95 % Wilson CIs.

| Location | n | minor-edit rate (95 % CI) |
|---|---:|---|
| sense | 17,880 | 69.8 % [69.1, 70.5] |
| headword | 7,282 | 81.5 % [80.6, 82.4] |
| meta | 822 | 88.6 % [86.2, 90.6] |
| grammar | 294 | 31.6 % [26.6, 37.2] |
| citation | 3,338 | 30.7 % [29.2, 32.3] |
| markup | 3,945 | 18.2 % [17.1, 19.5] |

The split is itself interpretable: the high-minor-rate fields (sense, headword, meta) are
where humans fix what they read; the low-rate fields (markup, citation) are where
edits are structural — re-tagging or re-sourcing — and so span more characters.

### 5.5 H2 — the location profile differs by dictionary

Location is not independent of dictionary. A chi-square test of location × dictionary
(top 15 by volume, derived labels) gives χ² = 23 674.5, dof = 70, *p* < 0.001,
**Cramér's V = 0.415** (a moderate-to-strong association; bootstrap CI [0.41, 0.42], and
0.437 with the outlier PW removed). Dictionaries differ in *where* their errors sit, not
merely how many they have — a fingerprint, not just a count.

### 5.6 H3 — the profile shifts over twelve years

Mann–Kendall trend tests on the yearly shares (Table 5) show a clear movement: **headword**
corrections fall steeply (τ = −0.44, *p* = 0.044; 0.90 → 0.12 of the yearly share) as the
early headword-normalisation campaigns complete, while **markup** (τ = 0.64, *p* = 0.003)
and **metadata** (τ = 0.44, *p* = 0.044) rise as curation moves to structural polish. On
the edit-type axis, **diacritic** edits fall (τ = −0.44) while **punctuation** (τ = 0.44)
and **spacing** (τ = 0.49, *p* = 0.024) rise.

**Table 5.** Significant diachronic trends (Mann–Kendall on yearly share).

| Axis | Category | τ | *p* | direction | first → last |
|---|---|---:|---:|---|---|
| location | headword | −0.44 | 0.044 | falling | 0.90 → 0.12 |
| location | markup | 0.64 | 0.003 | rising | 0.00 → 0.06 |
| location | meta | 0.44 | 0.044 | rising | 0.00 → 0.03 |
| edit-type | diacritic | −0.44 | 0.044 | falling | 0.12 → 0.09 |
| edit-type | punctuation | 0.44 | 0.044 | rising | 0.03 → 0.32 |
| edit-type | spacing | 0.49 | 0.024 | rising | 0.05 → 0.15 |

### 5.7 Cross-dictionary error density

Normalising by entry count (`<L>` markers), correction *density* ranges widely among
dictionaries with ≥ 30 events — from **160.8 per 1,000 entries** (PGN) and 91.2 (BUR) down
to ~53 (PUI). PW, the largest dictionary, carries the most raw events (13,651) at 80.0 per
1,000. We stress in §7 that high density reflects curatorial attention as much as latent
error.

### 5.8 Crosswalks and the character-confusion signal

Read through the external schemes, the same edits distribute as: **OCR** — substitution
15,847, insertion 13,195, deletion 10,564, segmentation 9,750; **Katre textual criticism**
— addition 18,877, substitution 16,432, omission 13,340, with the classical
metathesis/haplography/dittography tail (732 / 489 / 193). The clean form-layer phoneme
signal is led by **b → v** (341), the classic Sanskrit orthographic merger, followed by
*k*/*t*, *s*/*m* and a retroflex-and-diacritic repair cluster — exactly the confusions a
Sanskrit OCR or spell-checker should target first.

### 5.9 Who repairs what

Correction labour is concentrated: **Jim Funderburk** (34,489 events, mostly sense) and
**Dhaval Patel** (7,271, sense) account for the large majority, with a long tail of named
volunteers (the present author among them at 445, mostly headword). The process detail —
latency, throughput, the contributor network's growth — is the subject of the OBS-Q
companion.

## 6. The released resource and baselines

The corpus is released as
[`correction_events_release.csv`](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/observatory/site/src/data/correction_events_release.csv)
with a Gebru-style datasheet
([`docs/DATASHEET.md`](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/docs/DATASHEET.md)),
per-event evidence labels, the three crosswalk columns, and a **temporal split** (train on
the past, test on recent edits) under **CC-BY-4.0**. It supports three tasks, for which we
give stdlib-only **reference baselines** that define the task rather than tune a system
([`obs_t_baselines.md`](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/reports/obs_t_baselines.md)):

1. **Error detection** — does a character-trigram LM prefer the corrected form? Pairwise
   accuracy **0.516** (chance 0.5): the task is hard precisely because old and new differ
   by a single character.
2. **Error correction** — a Norvig-style noisy-channel edit-1 model reaches acc@1 **0.059**,
   with 78.7 % of test errors within its edit-distance-1 reach.
3. **Error-type classification** — Naïve Bayes over edit-op features predicts the location
   component at accuracy **0.594** (macro-F1 0.403; majority baseline 0.44), evidence the
   location axis is *learnable* from surface features alone.

These low numbers are the point of a baseline: they establish headroom for the neural
sequence models the resource is meant to enable.

## 7. Discussion

**Corrected ≠ wrong.** The single most important reading rule for this corpus is that it
records *corrected* events — where curators looked and acted — not a dictionary's latent
error rate. A dictionary with high correction density (§5.7) may be **better** maintained,
not worse; the falling-headword trend (§5.6) reflects a finished campaign, not improving
typists. Every share in this paper is a share of curatorial attention. We state this
because the alternative reading — "PGN is the buggiest dictionary" — is both tempting and
wrong.

**Surface dominance has a lesson for QA.** That corrections are overwhelmingly small
surface edits, even in the definition and headword fields (§5.4), means the highest-yield
automated quality tooling for digital Sanskrit lexicography is **not** semantic — it is
spelling, spacing, punctuation and diacritic normalisation, targeted by the
character-confusion profile of §5.8. The error mass is where a transducer can reach it.

**The two-axis lesson generalises.** The 0.1 % silver agreement (§4.3) is a cautionary
result for any digitisation-correction study: *where* an edit lands and *what kind* of edit
it is are orthogonal, and a single typology column that mixes them will be dominated by
whichever axis its fallback heuristic happens to encode. Separate the axes first.

## 8. Limitations and future work

**Form-layer linkage.** Only 28.8 % of form-era events join to a current source record, so
the location axis leans on the git layer; raising the form link rate (fuzzy headword
matching, per-dictionary encoding profiles, id-drift reconciliation) is the main avenue to
extend location coverage backward in time.

**Validation is silver, not yet gold.** The typology is machine-derived and checked
against a human-free silver standard; a human **gold sample** is staged
([`validation/gold_sample.csv`](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/validation/gold_sample.csv),
[`validation/error_sample.csv`](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/validation/error_sample.csv))
but **awaits a second annotator** for an inter-annotator agreement (κ) figure. We report no
κ here and treat the location/edit-type labels as derived, not adjudicated.

**Surface ops cannot see intent.** Edit-type is computed from character operations, so a
meaning-changing correction that happens to be one character (a wrong vowel that flips the
lemma) is counted as a small edit; the "surface, not substance" claim is about edit *size*
and *location*, not a claim that no correction ever changes meaning.

**Coverage gaps.** PW's top location is `unattributed` (form-era, unjoined), so its dense
density figure is real but its location mix is partly unknown; dictionaries below the
≥ 30-event floor are omitted from the density and dictionary-difference tests.

## 9. Conclusion

Twelve years of correcting the Cologne Digital Sanskrit Lexicon resolve into a clear and
slightly surprising picture: the corrections cluster exactly where meaning lives — in
definitions and headwords — yet are almost entirely small surface repairs, they form a
per-dictionary fingerprint rather than a uniform noise floor, and that fingerprint has
visibly shifted as the project's curatorial priorities moved from headwords to structure.
We release the corpus, its two-axis typology, three crosswalk readings and reference
baselines as a language resource for Sanskrit error detection and correction — with the
standing caveat that it measures the repairs a community chose to make, which is a
different and more human thing than a list of a dictionary's mistakes.

---

## References (draft — author to finalise)

Bryant, C., Felice, M. and Briscoe, T. (2017). Automatic annotation and evaluation of
error types for grammatical error correction. *ACL 2017.* — [ERRANT]

Gebru, T. et al. (2021). Datasheets for Datasets. *Communications of the ACM* 64(12).

Hartmann, R. R. K. and James, G. (1998). *Dictionary of Lexicography.* Routledge.

Kapp, D. and Malten, T. *Cologne Digital Sanskrit Dictionaries*, University of Cologne
(sanskrit-lexicon.uni-koeln.de).

Katre, S. M. (1941). *Introduction to Indian Textual Criticism.* Karnatak Publishing House.

Svensén, B. (2009). *A Handbook of Lexicography.* Cambridge University Press.

Wiegand, H. E. (1998–). *Wörterbuchforschung.* De Gruyter.

*Plus the OBS-Q correction-sustainability companion and the* csl-atlas *microstructure
papers (citation registers; sense inheritance; indigenous microstructure), cross-linked
above. [TODO: author to insert remaining specific citations.]*
