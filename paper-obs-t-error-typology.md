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
are the released 52,498-event snapshot and reproducible from committed data and stdlib-only
scripts. Since 28-07-2026 (H1759) this is the single canonical A12 manuscript; the earlier
one-axis draft at*
[`reports/obs_t_paper_draft.md`](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/reports/obs_t_paper_draft.md)
*is retired.*

**Mārcis Gasūns**  
Independent Researcher  
ORCID: 0000-0003-4513-884X  
`sanskrit.research.institute@gmail.com`

---

## Abstract

We present a twelve-year, **52,498-event** corpus of corrections to the Cologne Digital
Sanskrit Lexicon (CDSL — 43 dictionaries, 208 named correctors, 2014–2026) and a
**two-axis typology** of the errors those corrections repair. Unifying a 2014–2019
correction-form archive with the 2019–2026 source git history, we normalise every edit
to IAST — which requires resolving the form archive's mixed Devanagari/Harvard-Kyoto
encoding, a finding in itself — and describe each correction on two orthogonal axes: its
**location** in the dictionary microstructure (headword, sense, citation, markup, …),
recovered by joining the edit to the XML-tagged source, and its **edit-type** (spelling,
punctuation, spacing, diacritic, …), read from a character-level edit-operation trace.
The two axes are genuinely orthogonal: a location-join and an edit-type heuristic that a
naïve single-axis design conflated agree only 0.1 % of the time, a near-zero we show to
be structural, not noise. Three results follow. **(H1)** Corrections concentrate first in
**sense** (52.7 % of located edits), with markup, headword, and citation as the next tier;
the median edit distance is 2, but minor-edit rates vary sharply by location (headword
85.6 %, sense 38.2 %, markup 5.2 %). **(H2)** The location profile differs sharply by
dictionary (χ² = 26,192.5, Cramér's V = 0.432). **(H3)** The yearly profile shows
directional shifts — headword corrections fall (0.88 → 0.10), markup rises (0.00 → 0.17) —
while the corrected trend table reports BH-adjusted q-values. A stable character-confusion
signal led by *b*/*v* emerges. The location codebook is validated by a blind
cross-model double annotation of a frozen 390-event sample: Cohen κ = 0.906
(95 % CI 0.872–0.938) between two LLM annotators from different model families —
agreement that licenses the codebook as executable and its labels as stable, not as
human-validated ground truth. We release the
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

Our contributions are: (i) a unified, IAST-normalised, evidence-labelled corpus of 52,498
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

**Adjacent correction corpora.** The nearest NLP resources are the English
grammatical-error corpora — the Cambridge Learner Corpus (Yannakoudakis et al. 2011),
the CoNLL-2014 shared task (Ng et al. 2014), and BEA-2019 (Bryant et al. 2019) — whose
parallel old/new pairs OBS-T's event schema mirrors, though our errors arise from OCR
artifacts, transliteration inconsistency and a multi-script transcription history rather
than from learner grammar. OCR gold standards for historical documents (Springmann et
al. 2016; Clematide et al. 2016) share the concern with character-level noise but
operate at document level, without the entry-microstructure attribution that makes a
correction record readable as lexicography; Piotrowski (2012) identifies the
multi-script polyglot entry as the hardest class for automated processing — exactly the
CDSL record type. Digital-humanities correction logs (the DTA base format, Haaf et al.
2015; OCR4all, Reul et al. 2019) maintain comparable provenance chains for historical
German printing. On the lexicographic side, the structured-release formalisms of the
wordnet and OntoLex-Lemon communities (Bond and Paik 2012; McCrae et al. 2012) frame
CDSL as one of the largest open historical-dictionary corpora in that ecosystem; for
Sanskrit NLP the Digital Corpus of Sanskrit (Hellwig 2010–; Hellwig 2016) provides the
parsed-text complement — OBS-T contributes not the dictionaries' semantic content but
the *error signal* in their digitisation history.

**Post-correction lineage for the edit-type axis.** Because Axis B classifies *kind of
change* rather than *location*, it inherits directly from the OCR/digitisation
post-correction literature rather than from lexicography — and that literature has
converged on exactly the error granularity Axis B reports (spelling, diacritic, case,
spacing, punctuation, digit, transposition). Richter et al. (2018) correct a
low-resource historical corpus (Faroese) with a character-level HMM decoded by a
modified Viterbi search, escalating only the harder residual cases to a small set of
targeted heuristics — a two-tier design (cheap channel model first, human/heuristic
effort where it counts) that reduced word error rate from 7.6% to 1.3% at roughly 65
human-hours, directly comparable in spirit to our own edit-op trace plus crosswalk
fallback. Lyu et al. (2021) instead learn the character-substitution channel end-to-end
with a recurrent+convolutional network and a correction-aware loss. Both pre-date large
language models; more recently, Thomas et al. (2024) show an instruction-tuned Llama 2
correcting historical newspaper OCR at a 54.5% character-error-rate reduction against
23.3% for a fine-tuned BART baseline on BLN600, and Boros et al. (2024) benchmark
fourteen foundation LLMs across post-correction tasks spanning languages, periods, and
document types. We read this lineage specifically as *prior art for what a corrector
looks like once an error is typed* — the CDSL is not OCR-sourced, but a large share of
its correction events (the spelling/diacritic/case/spacing/punctuation clusters that
dominate Axis B, §5.3) are the same class of small, local, channel-model-tractable
errors these systems target. The released baselines in §6 are deliberately the cheap
end of this spectrum (trigram LM, Norvig edit-1); the natural next step this typology
enables is applying a Viterbi- or neural-channel corrector of this kind per edit-type
cluster, using the location axis to decide where correction effort is worth spending.

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

Two constructions deserve note. **Deduplication:** L1 and L2 overlap in the 2019
transition period; events are deduplicated on a stable hash of (layer, dictionary,
record, old, new, date), keeping the git-derived record — higher positional evidence —
where both layers carry the same edit. Bulk reformatting commits (a clear cliff of
>400,000 changed lines above normal correction throughput) are excluded with a warning:
they are encoding re-normalisations, not individual corrections. **Identity
resolution:** the form archive records correctors by email or username, the git history
by committer; a manually curated alias map merges attested alias variants onto
canonical identities, leaving 208 release-safe corrector labels; historical aliases
whose identity is not attested remain separate labels rather than being guessed.

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
the mistake: on the 5,634 form events where both signals are available, they agree only
**0.1 %** of the time (5 of 5,634 = 0.089 %; [`obs_t_silver.json`](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/reports/obs_t_silver.md)).
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

### 4.5 Evaluation lineage

OBS-T label validation, its confusion/alignment analysis (§4.3), and any future
cross-dictionary sense/headword mapping are instances of the ELEXIS/GlobaLex
**Monolingual Word Sense Alignment (MWSA)** shared-task family (Ahmadi et al. 2020). Rather
than invent a bespoke validation method, we adopt the MWSA evaluation contract — a **frozen
gold sample, two annotators, Cohen's κ, and per-class precision/recall/F1** — for the
gold-annotation gate described in §8. The harness
([`scripts/obs_t_gold.py`](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/scripts/obs_t_gold.py))
implements the stratified sampling, blind annotation sheets, κ, and per-class P/R/F1 this
lineage prescribes. Naming the lineage here does not itself change what OBS-T releases: if a
cross-dictionary sense-alignment dataset is ever emitted from this corpus, the alignment
content routes to *csl-atlas*, with OBS-T keeping only the process metrics.

### 4.6 Validation: the gold sample and cross-model agreement

The validation instrument is a frozen, stratified 390-event sample
([`validation/gold_sample.csv`](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/validation/gold_sample.csv)),
drawn by `source_layer` × `evidence_level` under the MWSA-style contract of §4.5. Its
provenance is stated plainly: the sample's original `gold_component` column was filled
in a single machine first pass (a rule-based classifier, LLM-assisted) — no human
annotated it at any point. Its 0.29 agreement with the automatic attribution is
therefore a *consistency* figure between two heuristic processes on the historical
hybrid (one-axis) scheme, not an accuracy against human ground truth; within it, the
structurally distinctive components agree well (grammar and meta F1 = 0.90) while the
encoding ↔ orthography boundary of the old scheme was the dominant confusion —
roughly 66 boundary rows still await human expert review.

**Cross-model inter-annotator agreement (measured 21-07-2026).** Two fresh, mutually
blind annotation passes over all 390 rows were run by two LLM annotators from
different model families — Opus 4.8 (`claude-opus-4-8`) and Sonnet 5
(`claude-sonnet-5`) — against the location-axis codebook in
[`validation/COMPONENT_GUIDE.md`](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/validation/COMPONENT_GUIDE.md),
with all label columns and notes stripped from the input and row order shuffled.
Cross-model agreement on the 8-value location axis is **Cohen κ = 0.906 (95 %
bootstrap CI 0.872–0.938, 2,000 resamples; raw agreement 92.8 %, 362/390)**; at the
pre-registered coarser 4-group granularity κ = 0.896 [0.855–0.935]. Label stability
was measured, not assumed: over three repeated runs on a fixed 30-row subsample the
flip-rate was 4.4 % and 5.6 % per annotator, below the pre-registered 10 % threshold.
The κ gate, granularity ladder, seeds and annotator models were pre-registered and
committed before either pass ran; the 28 disagreement rows and full statistics are
published
([`component_kappa_disagreements.csv`](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/validation/component_kappa_disagreements.csv),
[`component_kappa_stats.json`](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/validation/component_kappa_stats.json)).
Two caveats. First, this is *cross-model* agreement between two LLM annotators: it
demonstrates that the codebook is executable and its labels stable across model
families, not that the labels match a human expert's judgment. Second, the fresh
passes use the location-only axis, whereas the original `gold_component` column
follows the hybrid scheme; the two artifacts are on different axes and are kept
separate.

**Independent error-sample benchmark.** A complementary check asks whether OBS-T
corrections track real errors: 120 random entries (20 per dictionary across six
dictionaries) were independently scanned for detectable digitisation errors, finding
**0/120** — a 0.0 % entry-level error rate
([`reports/obs_t_errorbench.md`](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/reports/obs_t_errorbench.md)).
Either the correction campaigns have already removed the obvious errors from random
entries, or the residue is subtle enough to need human expert reading; both readings
are consistent with the corpus recording real historical errors rather than
systematic over-correction.

## 5. Results

### 5.1 Headline

52,498 correction events over **2014-03-18 to 2026-05-30**, across 43 dictionaries and 208
named correctors; **64.3 % carry a derived (non-heuristic) label** (33,755 derived /
18,743 inferred). Where the form layer records a resolution date, the median
correction latency is **12 days** (p90 73, max 447).

### 5.2 Axis A — where corrections land

On derived labels (n = 33,755), corrections concentrate most strongly in **sense**
fields, with markup, headword, and citation forming the next tier (Table 2).

**Table 2.** Location of corrections (derived labels).

| Location | Events | Share |
|---|---:|---:|
| sense (definition) | 17,778 | 52.7 % |
| markup | 5,902 | 17.5 % |
| headword | 5,823 | 17.3 % |
| citation | 3,335 | 9.9 % |
| meta | 624 | 1.8 % |
| grammar | 293 | 0.9 % |

### 5.3 Axis B — what kind of change

Every edit-type is a surface change; the corpus contains **no "content rewrite" category**
(Table 3, all 52,498 events).

**Table 3.** Edit-type of corrections.

| Edit type | Events | Share |
|---|---:|---:|
| spelling | 11,683 | 22.3 % |
| spacing | 10,233 | 19.5 % |
| punctuation | 9,506 | 18.1 % |
| source-raw | 7,852 | 15.0 % |
| diacritic | 4,785 | 9.1 % |
| case | 3,813 | 7.3 % |
| digit | 2,907 | 5.5 % |
| (none) | 1,228 | 2.3 % |
| transposition | 491 | 0.9 % |

### 5.4 H1 — surface edits, uneven by location

Corrections are usually small. The median edit distance is **2**, and **63 %** are ≤ 2
characters (p90 20, max 508). The finding that matters is how unevenly this surface-edit
signal is distributed by location (Table 4). Headword corrections are overwhelmingly small
form fixes; sense is the largest location, but its edit-type mix is more varied, and markup,
citation, and grammar often involve longer structural/source edits.

**Table 4.** Minor-edit rate (small surface edit) by location, with 95 % Wilson CIs.

| Location | n | minor-edit rate (95 % CI) |
|---|---:|---|
| sense | 17,778 | 38.2 % [37.5, 39.0] |
| markup | 5,902 | 5.2 % [4.6, 5.7] |
| headword | 5,823 | 85.6 % [84.7, 86.5] |
| citation | 3,335 | 25.0 % [23.6, 26.5] |
| meta | 624 | 66.2 % [62.4, 69.8] |
| grammar | 293 | 13.3 % [9.9, 17.7] |

The split is itself interpretable: the high-minor-rate fields (especially headword and
meta) are where humans fix compact forms; the low-rate fields (markup, citation, grammar)
are where edits are structural — re-tagging or re-sourcing — and so span more characters.

### 5.5 H2 — the location profile differs by dictionary

Location is not independent of dictionary. A chi-square test of location × dictionary
(top 15 by volume, derived labels) gives χ² = 26,192.5, dof = 70. Row-level p-values
are descriptive because events cluster by commit/campaign; the effect size is
**Cramér's V = 0.432** (commit-block bootstrap CI [0.407, 0.482]). Dictionaries differ in *where* their errors sit, not
merely how many they have — a fingerprint, not just a count.

### 5.6 H3 — the profile shifts over twelve years

Mann–Kendall trend diagnostics on the yearly shares (Table 5) show directional movement:
headword corrections fall (τ = −0.462; 0.88 → 0.10 of the yearly share), while markup
rises (τ = 0.564; 0.00 → 0.17). After Benjamini-Hochberg correction, however, the current
yearly series remains best reported as directional rather than as a set of significant
trend claims. On the edit-type axis, spacing, punctuation, and source-raw edits rise
directionally while spelling, case, and transposition fall.

**Table 5.** Diachronic trend diagnostics (Mann–Kendall on yearly share).

| Axis | Category | τ | *p* | q (BH) | first → last |
|---|---|---:|---:|---:|---|
| location | headword | −0.462 | 0.0327 | 0.0981 | 0.88 → 0.10 |
| location | markup | 0.564 | 0.0087 | 0.0522 | 0.00 → 0.17 |
| location | sense | 0.333 | 0.1272 | 0.1908 | 0.11 → 0.67 |
| edit-type | spacing | 0.513 | 0.0173 | 0.0779 | 0.05 → 0.17 |
| edit-type | spelling | −0.436 | 0.0441 | 0.0879 | 0.73 → 0.18 |
| edit-type | source-raw | 0.410 | 0.0586 | 0.0879 | 0.00 → 0.26 |

### 5.7 Cross-dictionary error density

Normalising by entry count (`<L>` markers), correction *density* ranges widely among
dictionaries with ≥ 30 events — and read over the full 43-dictionary table the spread is
≈**4.5–160.8 per 1,000 entries**: 160.8 (PGN) and 91.4 (BUR) at the top, down to 4.48
(mwe, 145 events) at the floor, with PUI (~56) nowhere near the bottom of the range.
PW, the largest dictionary, carries the most raw events (13,662) at 80.1 per
1,000. We stress in §7 that high density reflects curatorial attention as much as latent
error.

### 5.8 Crosswalks and the character-confusion signal

Read through the external schemes, the same edits distribute as: **OCR** — substitution
14,815, insertion 14,713, deletion 11,018, segmentation 10,253; **Katre textual criticism**
— addition 20,546, substitution 15,246, omission 14,260, with the classical
metathesis/haplography/dittography tail (491 / 496 / 231). The clean form-layer phoneme
signal is led by **b → v** (341), the classic Sanskrit orthographic merger, followed by
*k*/*t*, *s*/*m* and a retroflex-and-diacritic repair cluster — exactly the confusions a
Sanskrit OCR or spell-checker should target first.

### 5.9 Who repairs what

Correction labour is concentrated: **Jim Funderburk** (35,057 events, mostly sense) and
**Dhaval Patel** (8,248, sense) account for the large majority, with a long tail of named
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
3. **Location classification** — Naïve Bayes over edit-op features predicts the location
   component at accuracy **0.638** (macro-F1 0.453; majority baseline 0.402), evidence the
   location axis is *learnable* from surface features alone.

These low numbers are the point of a baseline: they establish headroom for the neural
sequence models the resource is meant to enable.

**DOI.** ✅ Minted: concept DOI [`10.5281/zenodo.21346705`](https://doi.org/10.5281/zenodo.21346705)
(version DOI `10.5281/zenodo.21965649`, published 2026-08-16, CC-BY-4.0). The DOI
previously recorded for this dataset (`10.5281/zenodo.15834721`) was **false** — it
resolved to an unrelated preprint (confirmed by a live Zenodo check, 20-07-2026); the
repo-wide sweep to the genuine DOI landed 24-08-2026 (`scripts/fix_obs_t_doi.py`).

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
character-confusion profile of §5.8. The error mass is where a transducer can reach it —
which is precisely the class of corrector the OCR/digitisation post-correction lineage
(§2) was built for, from channel-model HMMs (Richter et al. 2018) through LLM-based
correctors (Thomas et al. 2024; Boros et al. 2024).

**The two-axis lesson generalises.** The 0.1 % silver agreement (§4.3) is a cautionary
result for any digitisation-correction study: *where* an edit lands and *what kind* of edit
it is are orthogonal, and a single typology column that mixes them will be dominated by
whichever axis its fallback heuristic happens to encode. Separate the axes first.

## 8. Limitations and future work

**Form-layer linkage.** Only 28.8 % of form-era events join to a current source record, so
the location axis leans on the git layer; raising the form link rate (fuzzy headword
matching, per-dictionary encoding profiles, id-drift reconciliation) is the main avenue to
extend location coverage backward in time.

**Validation is cross-model, not human-adjudicated.** The typology is
machine-derived; its checks are the human-free silver standard (§4.3) and the blind
cross-model double annotation of §4.6 (κ = 0.906 [0.872–0.938] on the location
axis). No label in this corpus has yet been adjudicated by a human domain expert:
the κ licenses the codebook as executable and its labels as stable across model
families, nothing more. The outstanding human steps are expert review of the ~66
encoding ↔ orthography boundary rows of the historical hybrid sample and, ideally, a
human expert pass over the location-axis sample
([`validation/gold_sample.csv`](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/validation/gold_sample.csv),
[`validation/error_sample.csv`](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/validation/error_sample.csv)).

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
We release the corpus, its two-axis typology (location codebook validated at
cross-model κ = 0.906), three crosswalk readings and reference
baselines as a language resource for Sanskrit error detection and correction — with the
standing caveat that it measures the repairs a community chose to make, which is a
different and more human thing than a list of a dictionary's mistakes.

---

## References

Ahmadi, S., McCrae, J. P., Nimb, S., Khan, F., Monachini, M., Pedersen, B. S. et al. (2020).
A Multilingual Evaluation Dataset for Monolingual Word Sense Alignment. *LREC 2020*,
3232–3242. https://aclanthology.org/2020.lrec-1.395/ — [MWSA shared task; data/format:
https://github.com/elexis-eu/MWSA]

Bond, F. and Paik, K. (2012). A survey of wordnets and their licenses. In *Proceedings
of the 6th Global WordNet Conference*, 64–71.

Boros, E., Ehrmann, M., Romanello, M., Najem-Meyer, S. and Kaplan, F. (2024).
Post-Correction of Historical Text Transcripts with Large Language Models: An
Exploratory Study. *LaTeCH-CLfL 2024.* https://aclanthology.org/2024.latechclfl-1.14/

Bryant, C., Felice, M. and Briscoe, T. (2017). Automatic annotation and evaluation of
error types for grammatical error correction. *ACL 2017.* — [ERRANT]

Bryant, C., Felice, M., Andersen, Ø. E. and Briscoe, T. (2019). The BEA-2019 shared
task on grammatical error correction. In *Proceedings of the 14th Workshop on
Innovative Use of NLP for Building Educational Applications*, 52–75.

Clematide, S., Furrer, L. and Volk, M. (2016). Crowdsourcing an OCR gold standard for
a German and French heritage corpus. In *Proceedings of LREC 2016*, 975–980.

Gebru, T. et al. (2021). Datasheets for Datasets. *Communications of the ACM* 64(12).

Haaf, S., Geyken, A. and Wiegand, F. (2015). The DTA 'base format': A TEI subset for
the compilation of a large reference corpus of printed historical German. *Journal
of the Text Encoding Initiative*, 8.

Hellwig, O. (2010–). Digital Corpus of Sanskrit. Department of Indology, Heinrich
Heine University Düsseldorf.

Hellwig, O. (2016). Morphological disambiguation of classical Sanskrit. In
*Proceedings of COLING 2016*, 1082–1093.

Hartmann, R. R. K. and James, G. (1998). *Dictionary of Lexicography.* Routledge.

Kapp, D. and Malten, T. *Cologne Digital Sanskrit Dictionaries*, University of Cologne
(sanskrit-lexicon.uni-koeln.de).

Katre, S. M. (1941). *Introduction to Indian Textual Criticism.* Karnatak Publishing House.

Kendall, M. G. (1948). *Rank Correlation Methods.* Griffin.

Levenshtein, V. I. (1966). Binary codes capable of correcting deletions, insertions,
and reversals. *Soviet Physics Doklady*, 10(8), 707–710.

Lyu, L., Koutraki, M., Krickl, M. and Fetahu, B. (2021). Neural OCR Post-Hoc Correction
of Historical Corpora. *Transactions of the Association for Computational Linguistics*
9. https://aclanthology.org/2021.tacl-1.29/

Mann, H. B. (1945). Nonparametric tests against trend. *Econometrica*, 13(3), 245–259.

McCrae, J., Aguado-de-Cea, G., Buitelaar, P., Cimiano, P., Declerck, T., Gómez-Pérez,
A., … Unger, C. (2012). Interchanging lexical resources on the Semantic Web.
*Language Resources and Evaluation*, 46(4), 701–719.

Ng, H. T., Wu, S. M., Briscoe, T., Hadiwinoto, C., Susanto, R. H. and Bryant, C.
(2014). The CoNLL-2014 shared task on grammatical error correction. In *Proceedings
of the CoNLL-2014 Shared Task*, 1–14.

Norvig, P. (2007). How to write a spelling corrector.
https://norvig.com/spell-correct.html

Piotrowski, M. (2012). *Natural Language Processing for Historical Texts.* Morgan &
Claypool.

Reul, C., Christ, D., Hartelt, A., Balbach, N., Wehner, M., Springmann, U., … Puppe, F.
(2019). OCR4all — an open-source tool providing a (semi-)automatic OCR workflow for
historical printings. *Applied Sciences*, 9(22), 4853.

Richter, C., Wickes, M., Beser, D. and Marcus, M. (2018). Low-resource Post Processing
of Noisy OCR Output for Historical Corpus Digitisation. *LREC 2018.*
https://aclanthology.org/L18-1369/

Springmann, U., Lüdeling, A. and Bollmann, M. (2016). OCR of historical printings of
Latin texts: Problems, prospects, progress. In *Proceedings of Digital Humanities
2016*, 578–580.

Svensén, B. (2009). *A Handbook of Lexicography.* Cambridge University Press.

Thomas, A., Gaizauskas, R. and Lu, H. (2024). Leveraging LLMs for Post-OCR Correction
of Historical Newspapers. *LT4HALA Workshop @ LREC-COLING 2024.*
https://aclanthology.org/2024.lt4hala-1.14/

Wiegand, H. E. (1998–). *Wörterbuchforschung.* De Gruyter.

Yannakoudakis, H., Briscoe, T. and Medlock, B. (2011). A new dataset and method for
automatically grading ESOL texts. In *Proceedings of ACL 2011*, 180–189.

*Plus the OBS-Q correction-sustainability companion and the* csl-atlas *microstructure
papers (citation registers; sense inheritance; indigenous microstructure), cross-linked
above.*

---

*Canonical A12 pre-submission draft, reconciled 28-07-2026 (H1759): the two-axis
manuscript absorbed the validation, IAA, related-work and data-statement material of
the retired one-axis draft
([`reports/obs_t_paper_draft.md`](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/reports/obs_t_paper_draft.md)),
with every count restated to the released 52,498-event snapshot. Target venue:
LREC-COLING (IJL alternate). Pending human steps: byline confirmation, genuine Zenodo
DOI mint (§6), expert review of the encoding ↔ orthography boundary rows (§8),
read-and-sign.*
