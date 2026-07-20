# OBS-T: A Longitudinal Error-Typology Corpus of Digital Sanskrit Lexicography

**Mārcis Gasūns**  
Independent Researcher  
ORCID: 0000-0003-4513-884X  
`sanskrit.research.institute@gmail.com`

---

## Abstract

We present OBS-T, a twelve-year, 50,953-event corpus of corrections to the
Cologne Digital Sanskrit Lexicon (CDSL) — 43 dictionaries spanning German,
English, and Sanskrit-medium sources from the nineteenth and early twentieth
centuries. Unifying a 2014–2019 correction-form archive with the full
2019–2026 source git history, we normalize every edit to IAST and attribute
it to the dictionary-entry *microstructure component* it repairs: one of nine
labels (headword, grammar, citation, sense, crossref, meta, encoding,
orthography, markup). Every event carries an evidence label (`derived` for
positionally attributed git events; `inferred` for form-layer events joined by
headword) and a temporal train/test split for reproducible benchmarking.

Three findings emerge. First, surface repair dominated the twelve-year record
as a whole (72.7% of all corrections), but the balance shifted sharply between
eras: the 2014–2019 form era was 97.2% surface-form, while the 2019–2026 git
era reached near parity (50.1% surface, 49.9% meaning) — a maturation signal
as the orthographic layer stabilized and content-level editorial work moved to
the foreground. Second, error profiles differ significantly across dictionaries
(χ²(112) = 58,934.6, p < 0.001, Cramér's V = 0.411), with per-dictionary
fingerprints reflecting source language, age, and editorial history. Third,
Mann-Kendall trend tests (Mann 1945; Kendall 1948) confirm statistically
significant diachronic shifts: markup and meta corrections are rising
(τ = 0.590, p = 0.006 and τ = 0.513, p = 0.017 respectively); encoding and
orthography corrections are falling (τ = −0.462, p = 0.033 and τ = −0.590,
p = 0.006).

We release the corpus under CC-BY-4.0 with a JSON schema, provenance
envelope, and three reference baselines (detection accuracy 0.516, correction
accuracy@1 0.059, type classification accuracy 0.388 vs. majority baseline
0.226) as a language resource for Sanskrit NLP, historical-dictionary
digitisation research, and computational error analysis.

---

## 1. Introduction

The Cologne Digital Sanskrit Lexicon (CDSL) is one of the largest freely
available digital humanities corpora for Sanskrit: 43 dictionaries, roughly
1.8 million XML-tagged entries, and an open correction pipeline that has been
operating since 2014. In those twelve years the project's volunteer correctors
have submitted, reviewed, and committed more than 50,000 individual corrections
to dictionary text — fixing spelling, transliteration, source citations,
part-of-speech labels, and markup structure. Every correction is, in effect,
a labelled pair (erroneous form, correct form) attached to a specific
dictionary entry and timestamped. Yet no systematic analysis of what was wrong
or where in the entry has ever been performed.

This paper fills that gap. We build OBS-T (the Observatory Error-Typology
corpus) from five data layers: the correction-form response archive (2014–
2019), the `csl-orig` git history (2019–2026), a hand-maintained correction
log, formal change-batch files, and an org-metrics backdrop from the CDSL
Observatory. We attribute every event to a microstructure *component* —
the part of the dictionary entry the error damaged — giving, for the first
time, an empirically grounded answer to the question: *what kinds of errors
does digitised Sanskrit lexicography produce?*

The contribution is threefold:

1. **A released language resource.** 50,953 correction events, schema-documented,
   evidence-labelled, split temporally, and released under CC-BY-4.0. Suitable
   as training/test data for Sanskrit error detection, correction, and typology
   tasks.

2. **A component-attributed error typology.** Nine microstructure labels derived
   directly from the XML tags of the corrected `csl-orig` lines, with ERRANT,
   OCR, and textual-criticism crosswalks.

3. **Longitudinal analysis.** Three statistically tested hypotheses about
   surface-form dominance, cross-dictionary variation, and diachronic maturation,
   with confidence intervals and effect sizes throughout.

The remainder is organised as follows. §2 surveys related work. §3 describes
data sources and corpus construction. §4 presents the annotation scheme. §5
reports corpus statistics. §6 presents the three-hypothesis analysis. §7
describes reference baselines. §8 is the data statement. §9 discusses
limitations. §10 concludes.

---

## 2. Related Work

**Grammatical error correction (GEC) corpora.** The most closely related NLP
resources are the English learner-error corpora — the Cambridge Learner Corpus
(Yannakoudakis et al. 2011), CoNLL-2013/2014 shared tasks (Ng et al. 2013,
2014), and BEA-2019 (Bryant et al. 2019). The ERRANT toolkit (Bryant et al.
2017) defines a linguistically motivated error taxonomy for English and
provides a pipeline for automatic error annotation of parallel edits. OBS-T
follows ERRANT's methodological pattern (parallel old/new pairs → operation
× linguistic-unit labels) but adapts it to the very different structure of
historical Sanskrit dictionaries, where errors arise from OCR artifacts,
transliteration inconsistencies, and the six-script transcription history of
the source texts rather than from non-native-speaker grammar.

**OCR error corpora.** Several corpora document OCR errors in digitized
historical documents (Springmann et al. 2016; Clematide et al. 2016). These
works share OBS-T's concern with how scanning introduces character-level noise,
but they operate at the document level rather than the lexicographic-entry
level and lack the microstructure attribution that makes OBS-T useful for
dictionary-specific NLP. Piotrowski (2012) provides a thorough survey of
NLP methods for historical texts, identifying the multi-script polyglot entry
as the hardest class for automated processing — a challenge OBS-T's character
confusion analysis quantifies.

**Digital humanities correction datasets.** The Deutsches Textarchiv (DTAbf;
Haaf et al. 2015) and similar projects maintain correction logs for digitised
historical texts. Reul et al. (2019) demonstrate OCR post-correction workflows
over historical German printing. OBS-T is distinguished by (a) the Sanskrit
polyglot context — entries mix Sanskrit in SLP1 transliteration, German,
English, and Latin in a single record; (b) the XML microstructure that names
each field explicitly; and (c) the unusually complete provenance chain from
paper scan to correction event spanning twelve years under continuous editorial
oversight.

**Lexicographic language resources.** The Global Wordnet Association (Bond &
Paik 2012) and OntoLex-Lemon (McCrae et al. 2012) formalisms have motivated
structured release of lexicographic data; CDSL is one of the largest open
multilingual historical-dictionary corpora in this ecosystem. Measures of
lexicographic quality and correction effort have not previously been studied
systematically for Sanskrit-medium dictionaries.

**Sanskrit NLP resources.** The Digital Corpus of Sanskrit (DCS; Hellwig 2010+)
provides parsed Sanskrit text for morphological and syntactic research.
Hellwig (2016) applies DCS-trained morphological models to Sanskrit word-sense
disambiguation in the Monier-Williams dictionary. OBS-T is complementary: it
focuses not on the semantic content of the dictionaries but on the *error signal*
in their digitisation history, which is a prerequisite for automated correction
tooling and complements DCS as a structured resource for Sanskrit NLP.

---

## 3. Data Sources and Corpus Construction

### 3.1 Data layers

OBS-T is built from five data layers, each contributing a different time range
and level of per-event richness.

| Layer | Source | Era | Events | Notes |
|---|---|---|---:|---|
| L1 — correction forms | `CORRECTIONS/cfr.tsv` | 2014–2019 | 24,441 | Google Form export; highest per-event richness |
| L2 — git diffs | `csl-orig` git history | 2019–2026 | 26,512 | Unified diffs; positional attribution |
| L3 — hand log | `CORRECTIONS/history.txt` | 2014–2019 | campaign-level | Not event-individualised; used for metadata only |
| L4 — change batches | `csl-corrections/batch_*/` | 2024–2026 | integrated into L2 | `updateByLine.py` changefile format |
| L5 — org metrics | Observatory CSVs | 2014–2026 | aggregate | Backdrop; not correction events |

**Layer 1 (correction forms).** The project accepted corrections via a Google
Form from 2014 to 2019. Each submission recorded: dictionary, headword,
erroneous form, corrected form, a free-text type comment, and a datestamp.
The form export (`cfr.tsv`) has 24,441 rows after deduplication. A critical
complication is that the form-era data mixes three scripts: Devanagari, IAST,
and Harvard-Kyoto (HK). The PW dictionary (the largest single contributor,
~57% of form events) used HK conventions (`z` for ś, `S` for ṣ, `R` for ṛ,
`T` for ṭ), while other contributors used IAST or Devanagari. We normalise
all forms to IAST via a self-contained transliterator that detects the script
of each cell and applies the appropriate mapping.

**Layer 2 (git diffs).** The `csl-orig` repository contains the XML source
for all 43 dictionaries and has been maintained under git since 2014, with
active committing from 2019 onwards. We mine all commits classified as
corrections (using the same `classify()` logic as the OBS-Q sustainability
analysis), parse unified diffs into old/new line pairs, and attribute each
pair to its `<L>` record and `<k1>` headword from hunk context. Bulk
reformatting commits (top ≈12 commits with >400,000 changed lines, a clear
cliff above normal correction throughput) are capped at 250 pairs per commit
and excluded from the event table with a warning; they represent encoding
re-normalizations, not individual corrections. After filtering, L2 yields
26,512 events from 1,243 commits (2019-11-04 to 2026-05-30). A memory
optimization was required: large commits were streamed line-by-line via
`subprocess.Popen` rather than buffered with `subprocess.run`, keeping peak
memory below 32 MB.

**Deduplication.** L1 and L2 overlap in the 2019 transition period. Events
are deduplicated by a stable hash of (layer, dict, lcode, old_iast, new_iast,
date). An event appearing in both layers is kept with the git-derived record
(higher positional evidence); the form record is flagged `source_layer=form`
and retained as a secondary row.

### 3.2 Event schema

Each row in the released CSV corresponds to one correction event with the
following key fields: `event_id` (stable hash), `date`, `source_layer`,
`dict`, `lcode` (the `<L>` record identifier), `headword_iast`, `old_iast`,
`new_iast`, `edit_ops` (Damerau-Levenshtein alignment over NFD characters),
`edit_distance`, `error_component` (the canonical label), `errant_type`,
`ocr_class`, `textcrit_class`, `corrector`, `corrector_name`, `latency_days`
(form era only), and `evidence_level` (`derived` | `inferred`).

Edit operations are computed over NFD-decomposed IAST so that diacritic
repairs (e.g. ā → a) register as single-character substitutions. NFD
decomposition inflates the formal edit distance for retroflex consonants
(e.g. ṭ = t + ◌̣, so d → ṭ has distance 2 rather than 1) but gives
fine-grained alignment for the character-confusion analysis.

### 3.3 Alias merging

The correction-form archive records correctors by email or username; the git
history records them by git committer. A manually curated `contributors_map.json`
maps 28 aliases (e.g. `dhaval_ejf`, `dhavel_ejf`) to 16 canonical identities.
After merging, 210 distinct correctors are represented, though the distribution
is highly skewed (see §5.4).

---

## 4. Annotation Scheme

### 4.1 Microstructure components

The canonical typology attributes each correction to the dictionary-entry
*microstructure component* it repairs — the structural slot in the XML record
whose content was wrong. The nine labels and their typical XML loci are:

| Component | What it covers | Typical XML tag |
|---|---|---|
| `headword` | Lemma, headword form, homonym index | `<k1>`, `<k2>`, `<h>` |
| `grammar` | Gender, part-of-speech, inflection class | `<lex>` |
| `citation` | Source reference, siglum, page number | `<ls>`, `<pc>` |
| `sense` | Gloss, definition, meaning content | Definition prose, `<s>` |
| `crossref` | Cross-reference, link target | `<lb>` |
| `meta` | Record identifier, structural metadata | `<L>`, `<e>` |
| `encoding` | Sanskrit transliteration / diacritic repair | Any Sanskrit text field |
| `markup` | XML delimiter or tag-structure repair | `<…>`, `{#…#}`, `{%…%}` |
| `orthography` | Latin/German/English spelling typo, case, whitespace | Body text prose |

The boundary between `encoding` and `orthography` requires care: `encoding`
covers a diacritic or transliteration fix to a Sanskrit form (e.g. correcting
`vedrana` to `vedanā`), while `orthography` covers a plain spelling error in
the non-Sanskrit text of the definition (e.g. `ignorrant` → `ignorant`). This
boundary is the most contested in annotation (see §4.3).

### 4.2 Attribution method

**Git layer (L2).** Component attribution is *positional*: we find the XML
tag enclosing the changed characters on the modified source line and assign the
corresponding component. For example, a change on a line where the modified
text falls inside `<ls>…</ls>` is labelled `citation`; a change to the `<k1>`
field is labelled `headword`. Because `csl-orig` lines are consistently tagged,
this works for over 99% of git-layer events (evidence label: `derived`).

**Form layer (L1).** The form submissions record only the headword and the
old/new string pair without line context. We join to the live `csl-orig` source
by headword to find the enclosing tag; if the headword join succeeds and the
old string is found in a specific tag's content, the event is attributed
positionally (evidence: `derived`, ≈12.9% of form events). For the remainder
we apply an empirical-cluster fallback: the old/new strings are compared using
edit-op features (operation type, Unicode script, presence of diacritics, match
to known transliteration error patterns) and assigned the highest-probability
component under a small lookup table (evidence: `inferred`). Overall, 65.9%
(33,561 / 50,953) of events carry `derived` evidence; 34.1% (17,392) are
`inferred`.

### 4.3 Validation: gold annotation

To measure component attribution accuracy we drew a stratified random sample
of 390 events (stratified by `source_layer` and `evidence_level`) and annotated
each with a `gold_component` label following the scheme in Table 1, using the
annotation guide in `validation/COMPONENT_GUIDE.md`. This gold annotation was
performed as an AI-assisted first pass (see §9, Limitations). The scorer
(`scripts/obs_t_gold.py --score`) reports the following:

| Metric | Value |
|---|---:|
| Annotated events | 390 |
| Overall accuracy (auto vs. gold) | 0.29 |
| Derived subset (n = 210) | 0.49 |
| Inferred subset (n = 180) | 0.06 |
| Grammar F1 | 0.90 |
| Meta F1 | 0.90 |
| Encoding F1 | 0.022 |
| Orthography F1 | 0.206 |

The figures above compare the automatic attribution system against an
AI-assisted annotator first pass; they should be read as a *consistency*
score between two heuristic processes rather than a gold-standard accuracy
figure. The derived-subset consistency (0.49) substantially exceeds the
inferred-subset (0.06), confirming that positional attribution is far more
reliable than the fallback heuristic regardless of annotator type.

The main confusion zone is encoding ↔ orthography: 38 events labelled
`orthography` by the automatic system were re-labelled `encoding` by the
annotator, and 28 events labelled `encoding` were re-labelled `orthography`.
This boundary — a diacritic repair to a Sanskrit form vs a spelling error in
non-Sanskrit prose — requires human expert judgment and cannot be resolved by
surface features alone. Human expert review of the ~66 boundary cases is the
most important quality step before the corpus is finalized.

Grammar (F1 = 0.90) and meta (F1 = 0.90) are the most reliably attributed
components; their structural distinctiveness in the XML makes both heuristics
converge.

A second annotator (for Cohen κ) has not yet completed the gold sheet; IAA
results are pending.

### 4.4 Independent error-sample benchmark

A complementary validation asks whether OBS-T corrections track real errors or
whether they over-represent certain types. We drew 120 random entries from the
current `csl-orig` corpus (20 per dictionary across six dictionaries: MW, PW,
AP90, SKD, BUR, BEN) and independently annotated each for `found_error`
(yes/no) and `error_component`. The AI-assisted scan found **0/120 entries**
with detectable digitisation errors, yielding a 0.0% entry-level error rate
(`reports/obs_t_errorbench.md`). This result is interpretable in two ways:
(a) the correction campaigns have already cleaned up the most obvious errors,
so random entries now look clean; or (b) remaining errors are subtle —
semantic or orthographic in extended prose — and require human expert reading
to detect. Either way, the finding is consistent with OBS-T corrections having
targeted real historical errors rather than systematic over-correction.

---

## 5. Corpus Statistics

### 5.1 Scale and span

| Statistic | Value |
|---|---:|
| Total correction events | 50,953 |
| Dictionaries | 43 |
| Distinct correctors (alias-merged) | 210 |
| First event | 2014-03-18 |
| Last event | 2026-05-30 |
| Span | 12.2 years |
| Evidence: derived | 33,561 (65.9%) |
| Evidence: inferred | 17,392 (34.1%) |
| Form layer (L1) | 24,441 (48.0%) |
| Git layer (L2) | 26,512 (52.0%) |

### 5.2 Component distribution

| Component | Events | Share |
|---|---:|---:|
| orthography | 19,529 | 38.3% |
| sense | 13,626 | 26.7% |
| headword | 7,282 | 14.3% |
| markup | 4,400 | 8.6% |
| citation | 3,580 | 7.0% |
| encoding | 1,325 | 2.6% |
| meta | 822 | 1.6% |
| grammar | 294 | 0.6% |
| unknown | 95 | 0.2% |

Orthography is the single largest component (38.3%), followed by sense
(26.7%) and headword (14.3%). The two surface-form components — orthography
and encoding — together account for 40.9% of all corrections; the two
meaning components — sense and grammar — account for 27.3%.

### 5.3 Cross-dictionary error density

Events per 1,000 entries, normalised by the `<L>` entry count of each
dictionary, for dictionaries with ≥ 30 events:

| Dictionary | Events | Entries | Per 1k | Top component |
|---|---:|---:|---:|---|
| pgn (Pāṇinian terms) | 78 | 485 | 160.8 | sense |
| bur (Burnouf, French) | 1,803 | 19,776 | 91.2 | sense |
| pw (Böhtlingk small, German) | 13,651 | 170,556 | 80.0 | orthography |
| ccs | 2,290 | 30,010 | 76.3 | headword |
| ap90 (Apte 1890) | 2,474 | 34,882 | 70.9 | sense |
| ben (Benfey) | 1,221 | 17,310 | 70.5 | sense |
| gra (Grassmann) | 710 | 12,785 | 55.5 | sense |

Error density varies by more than a factor of two between the highest and
lowest active dictionaries. PW's top component is orthography, reflecting
its large body of German-language definitions and a long OCR correction
campaign; BUR, AP90, BEN, and GRA all show `sense` as the top component,
suggesting that content-level editorial work dominates their correction
history.

### 5.4 Corrector distribution

| Corrector | Events | Top component | Active span |
|---|---:|---|---|
| Jim Funderburk | 34,489 | sense | 2014–2026 |
| Dhaval Patel | 7,271 | orthography | 2014–2026 |
| dhaval_ejf (alias) | 6,206 | orthography | 2015–2016 |
| Mārcis Gasūns | 445 | headword | 2014–2026 |

The corrector distribution is highly skewed. Jim Funderburk alone accounts
for 67.7% of all events; the top two correctors together account for 81.9%.
This extreme concentration is consistent with the OBS-Q finding (Gini = 0.86
across repository contributions) and represents the primary sustainability
risk for the project.

### 5.5 Crosswalk typologies

The same events annotated under three secondary frames:

**OCR / digitization frame:** substitution 15,847 (31.1%), insertion 13,195
(25.9%), deletion 10,564 (20.7%), segmentation 9,750 (19.1%), transposition
707 (1.4%), unknown 890 (1.7%).

**Textual criticism frame (Katre 1954):** addition 18,877 (37.1%),
substitution 16,432 (32.2%), omission 13,340 (26.2%), metathesis 732 (1.4%),
haplography 489 (1.0%), dittography 193 (0.4%), unknown 890 (1.7%).

**Top character confusions (form layer, IAST):**

| From → To | Count |
|---|---:|
| b → v | 341 |
| k → t | 255 |
| s → m | 198 |
| s → a | 187 |
| t → a | 180 |
| r → c | 173 |
| v → b | 123 |
| n → m | 120 |
| n → d | 115 |

The `b ↔ v` confusion leads (341 cases in one direction, 123 in the other),
a well-known merger in Sanskrit orthographic tradition. Retroflex-versus-
dental confusions appear across multiple rows (n/m, n/d, t/a, k/t), reflecting
the difficulty of consistently rendering the retroflex series in early
digitisation workflows.

---

## 6. Analysis

### 6.1 H1: surface-form dominance shifts across eras

We define *surface edits* as corrections to orthography, encoding, markup,
citation, meta, crossref, or headword — anything other than the semantic
content of the definition. *Meaning edits* are corrections to `sense` or
`grammar`. The hypothesis is that surface repair dominates the record overall,
driven by the early digitisation era's emphasis on OCR and transliteration
correction.

| Subset | N | Meaning share (95% CI) | Surface share |
|---|---:|---|---:|
| All events | 50,953 | 0.273 [0.269, 0.277] | 0.727 |
| Form era (L1, 2014–2019) | 24,441 | 0.028 [0.026, 0.030] | 0.972 |
| Git era (L2, 2019–2026) | 26,512 | 0.499 [0.493, 0.505] | 0.501 |
| Derived evidence only | 33,561 | 0.413 [0.408, 0.419] | 0.587 |

The overall 72.7% surface-form share confirms the headline hypothesis, but
the layer split reveals the mechanism. The form era (2014–2019) is almost
exclusively surface repair (97.2%). The git era (2019–2026) is near parity:
50.1% surface, 49.9% meaning. The correct framing is therefore not uniform
dominance but a *maturation shift*: as OCR and transliteration errors were
corrected in the first half of the project, the residual work moved toward
content-level editorial improvement — sense corrections, cross-reference
additions, markup restructuring.

This shift is corroborated by H3 and by the corrector data: Jim Funderburk,
whose top component is `sense` (67.7% of all events), is responsible for the
bulk of the git-era content corrections, while the form-era activity was more
evenly distributed across orthographic and encoding fixes.

### 6.2 H2: error profiles differ across dictionaries

To test whether the component distribution is homogeneous across dictionaries
we run a chi-square test of independence on the component × dictionary
contingency table (top 15 dictionaries by event count):

> χ²(112) = 58,934.6, p < 0.001, **Cramér's V = 0.411**

The effect size is large by standard benchmarks (Cohen 1988: V > 0.35 is
large for this table shape). Dictionaries do not share a common error profile;
they have distinct *fingerprints* shaped by the source text's age, language,
transcription history, and the editorial focus of their correctors. PW's
fingerprint is dominated by German-prose orthography fixes; BUR's and AP90's
are dominated by sense corrections; MWS has a mixed profile reflecting its
size and multi-decadal editorial history.

### 6.3 H3: diachronic trends

Mann-Kendall trend tests (Mann 1945; Kendall 1948) on the yearly share of
each component (12 annual observations, 2014–2026):

| Component | τ | p | Trend | Share: first → last year |
|---|---:|---:|---|---|
| markup | 0.590 | 0.006 | **rising** | 0.02 → 0.06 |
| meta | 0.513 | 0.017 | **rising** | 0.00 → 0.03 |
| sense | 0.359 | 0.100 | flat | 0.05 → 0.34 |
| citation | 0.372 | 0.088 | flat | 0.00 → 0.03 |
| grammar | 0.090 | 0.714 | flat | 0.00 → 0.02 |
| headword | −0.359 | 0.100 | flat | 0.48 → 0.12 |
| unknown | −0.423 | 0.051 | flat | 0.01 → 0.00 |
| encoding | −0.462 | 0.033 | **falling** | 0.01 → 0.00 |
| orthography | −0.590 | 0.006 | **falling** | 0.42 → 0.41 |

Statistically significant results (p < 0.05): markup and meta are rising;
encoding and orthography are falling. The rising markup trend reflects a
sustained effort to normalise XML tag conventions (e.g. delimiter
standardisation, tag-splitting) that was not present in the early form-era
work. The falling encoding trend reflects the near-completion of the
transliteration correction campaigns. Headword share exhibits a dramatic
absolute drop (0.48 → 0.12) even without reaching the τ significance
threshold; the trend is consistent with the form-era headword-correction
campaigns that were largely completed before 2019.

---

## 7. Baseline Systems

We define three reference tasks on OBS-T and report stdlib-only, deterministic
baselines. These establish what a competent but simple system can achieve and
provide a target for neural follow-up work.

**Temporal split.** Training data: events before 2024 (form era + early git).
Test data: events from 2024 onwards (recent git era, n = 3,127 for form-based
tasks; 8,359 for the typed corpus).

### 7.1 Error detection

*Task:* Given a (erroneous, corrected) character string pair, does a character
language model rank the corrected form higher? This is a binary pairwise
ranking task; chance = 0.50.

*System:* Character trigram LM (add-one smoothing) trained on correct forms from
the training split. For each test pair, compute perplexity of both forms and
predict the one with lower perplexity as correct.

| Metric | Value |
|---|---:|
| Training tokens | 14,670 |
| Test pairs | 3,127 |
| Pairwise accuracy | **0.516** |
| Tie rate | 0.012 |

Pairwise accuracy of 0.516 is only marginally above chance (0.50), indicating
that a surface character LM without structural context is insufficient for
reliable error detection in this domain.

### 7.2 Error correction

*Task:* Given an erroneous form, produce the corrected form.

*System:* Noisy-channel model (Norvig 2007): enumerate all edit-1 candidates;
score with the character LM; return the highest-scoring candidate in the
training lexicon (open-vocabulary: if no candidate is in the lexicon, return
the highest-scoring edit-1 form regardless).

| Metric | Value |
|---|---:|
| Training lexicon | 11,173 forms |
| Test pairs | 3,127 |
| Accuracy@1 | **0.059** |
| Test errors at edit-distance 1 | 78.7% (model's reach) |

Despite 78.7% of test errors being reachable at edit-distance 1, accuracy@1
is only 0.059. The low precision reflects the open vocabulary of Sanskrit
(many plausible edit-1 candidates per form) and the importance of structural
context that the LM cannot access.

### 7.3 Component type classification

*Task:* Predict the `error_component` from edit-op features alone.

*System:* Categorical Naive Bayes over features: dominant operation type (sub/
ins/del/transpose), character-unit granularity (letter/diacritic/segment),
edit-distance bucket, script label (deva/iast/latin/mixed), and empirical
cluster label. Trained on the derived-evidence subset (labels are most
reliable).

| Metric | Value |
|---|---:|
| Training / test events | 17,082 / 8,359 |
| Classes | 7 (unknown excluded) |
| Accuracy | **0.388** |
| Macro-F1 | 0.302 |
| Majority-class baseline (sense) | 0.226 |

The NB classifier improves substantially over the majority baseline (0.388
vs. 0.226), showing that edit-op features carry real signal for component
prediction. Accuracy is limited because encoding and orthography are
surface-identical (both manifest as character substitutions) and because the
`inferred` labels in the training set add noise.

---

## 8. Data Statement

Following Bender & Friedman (2018), we document the corpus along the key
dimensions they identify.

**Curation rationale.** OBS-T was created to enable systematic study of
digitisation errors in historical Sanskrit lexicography. The decision to
release the full correction history (not a sample) was made to support
longitudinal analysis. Inferred labels are flagged so users can filter to
high-confidence subsets.

**Language variety.** The corpus covers corrections to texts in four
languages: Sanskrit (SLP1 and IAST transliteration), German, English, and
French (one dictionary). The dominant language of the definition prose varies
by dictionary.

**Speaker demographics.** Correctors are volunteer scholars and project
maintainers affiliated with the Cologne Digital Sanskrit Lexicon project.
Of 210 correctors (alias-merged), 67.7% of events are attributable to a
single individual (J. Funderburk), reflecting the project's small core team.

**Annotator demographics.** Component labels for the git layer are derived
automatically from XML structure. The gold-standard annotation used for
validation (390 events) was performed with AI assistance (first pass) — see
§9.

**Speech situation.** The source texts are 19th–20th century scholarly
dictionaries; corrections reflect editorial standards of an ongoing digital
humanities project.

**Text characteristics.** Source dictionary entries are XML-tagged records
averaging 60–400 characters. The old/new pair for each event is typically a
short span (median edit distance = 3 characters).

**Provenance.** Layer 1 originates from a Google Form operated by the CDSL
project; Layer 2 from public git commits to the `csl-orig` repository
(github.com/sanskrit-lexicon/csl-orig). All data is publicly available
under the CDSL's CC-BY-SA 4.0 licence; OBS-T is released under CC-BY-4.0.

**License.** Creative Commons Attribution 4.0 International (CC-BY-4.0).

**DOI.** ⚠️ **Not yet minted.** `10.5281/zenodo.15834721` was previously recorded here as the concept DOI but is a **false DOI** — it resolves to an unrelated topology preprint, confirmed by a live Zenodo check (H1364, 20-07-2026; see [SanskritLexicography CONTRADICTIONS §8](https://github.com/gasyoun/SanskritLexicography/blob/master/CONTRADICTIONS.md)). A genuine Zenodo deposit for OBS-T must be minted before this section can cite a DOI — **do not submit with this placeholder.**

---

## 9. Limitations

**AI-assisted gold annotation.** The 390-row gold sample (§4.3) was annotated
in a single AI-assisted pass, not by an independent domain expert. The overall
consistency score (0.29) measures agreement between two heuristic processes
(automatic attribution and the AI annotator), not accuracy against a human
expert gold standard. The figure therefore cannot be read as a simple upper
bound on system quality; the true accuracy — particularly on the
encoding/orthography boundary — is better measured by the component-specific
metrics (grammar F1 = 0.90, encoding F1 = 0.022). Human expert review of the
~66 encoding/orthography boundary cases is the highest-priority quality step
before the corpus is used for downstream training. Inter-annotator agreement
(Cohen κ) is pending a second annotator and should be treated as an open gap
in the current version.

**Form-era HK/SLP1 mixing.** The cfr.tsv new-form cells mix Harvard-Kyoto
and SLP1 conventions within the PW dictionary's submissions. Our
normalisation uses a heuristic script-detector; the HK transliterator was
validated on known examples (e.g. `vedranA` → `vedanā`, `GaT` → `ghaṭa`)
but may misfire on edge cases where the two conventions are ambiguous (e.g.
`ś` renders as `z` in HK and is absent from SLP1).

**Inferred labels are heuristic.** 34.1% of events carry `inferred` evidence:
these are form-layer events where the headword join to `csl-orig` failed and
an empirical cluster was used. The inferred subset shows near-zero accuracy
(0.06) against the gold annotation. Any quantitative claim based on component
distribution should be run on the `derived` subset and checked for
sensitivity.

**Temporal gap in L2.** The git history of `csl-orig` before November 2019 is
sparse; the correction-form era (L1) provides better coverage for 2014–2019.
The mid-2019 transition creates a potential discontinuity in the apparent
component distribution — in particular, the dramatic rise of `sense`
corrections in the git era may partly reflect a methodological difference
(positional attribution vs. heuristic fallback) rather than a genuine
editorial shift, though the corrector-level analysis (§5.4 and §6.1) supports
a genuine interpretive shift.

**No neural baselines.** The three baselines in §7 are stdlib-only by design
(reproducible without GPU access). Neural sequence models (character-level
seq2seq, BERT-style masked LM fine-tuning) would likely improve substantially
on all three tasks; they are left for follow-up work.

---

## 10. Conclusion

OBS-T provides the first longitudinal, component-attributed corpus of
digitisation corrections for Sanskrit historical dictionaries. From 50,953
events spanning 43 dictionaries and twelve years, three empirically tested
findings emerge: (1) the project's early work was overwhelmingly surface-form
repair that gave way, post-2019, to a near-equal balance of surface and
meaning corrections; (2) dictionaries carry distinct error fingerprints
(Cramér V = 0.411); and (3) markup and meta corrections are significantly
rising while encoding and orthography are falling, tracing the maturation arc
of the digitisation project. The corpus, released under CC-BY-4.0 with a
temporal split and reference baselines, is available at:

> `https://github.com/sanskrit-lexicon/csl-observatory`  
> Branch `main` · `validation/` · `observatory/site/src/data/` · DOI: not yet minted (see §8 note)

The most pressing next step for the resource is human expert review of the
encoding/orthography boundary in the gold sample and completion of the
second-annotator IAA pass. Neural baselines (character-level seq2seq,
BERT-style masked LM) are left for follow-up work but the evaluation
protocol and temporal split established here make them straightforward to
add without changing the resource itself.

---

## Acknowledgements

Jim Funderburk and Dhaval Patel contributed the bulk of the corrections
catalogued in this corpus and reviewed the annotation guide. The CDSL project
has been hosted by the University of Cologne since 1994. We thank Oliver
Hellwig for discussions on Sanskrit NLP resources and the DCS interface.

---

## References

Bender, E. M., & Friedman, B. (2018). Data statements for natural language
processing: Toward mitigating system bias and enabling better science.
*Transactions of the Association for Computational Linguistics*, 6, 587–604.

Bryant, C., Felice, M., & Briscoe, T. (2017). Automatic annotation and
evaluation of error types for grammatical error correction. In *Proceedings
of ACL 2017*, 793–805.

Bryant, C., Felice, M., Andersen, Ø. E., & Briscoe, T. (2019). The BEA-2019
shared task on grammatical error correction. In *Proceedings of the 14th
Workshop on Innovative Use of NLP for Building Educational Applications*,
52–75.

Clematide, S., Furrer, L., & Volk, M. (2016). Crowdsourcing an OCR gold
standard for a German and French heritage corpus. In *Proceedings of LREC
2016*, 975–980.

Cohen, J. (1988). *Statistical power analysis for the behavioral sciences*
(2nd ed.). Erlbaum.

Hellwig, O. (2010–). Digital Corpus of Sanskrit. Department of Indology,
Heinrich Heine University Düsseldorf.

Katre, S. M. (1954). *Introduction to Indian textual criticism*. Deccan
College Post-Graduate and Research Institute.

Bond, F., & Paik, K. (2012). A survey of wordnets and their licenses. In
*Proceedings of the 6th Global WordNet Conference*, 64–71.

Haaf, S., Geyken, A., & Wiegand, F. (2015). The DTA 'base format': A TEI
subset for the compilation of a large reference corpus of printed
historical German. *Journal of the Text Encoding Initiative*, 8.

Hellwig, O. (2016). Morphological disambiguation of classical Sanskrit.
In *Proceedings of COLING 2016*, 1082–1093.

Kendall, M. G. (1948). *Rank Correlation Methods*. Griffin.

Levenshtein, V. I. (1966). Binary codes capable of correcting deletions,
insertions, and reversals. *Soviet Physics Doklady*, 10(8), 707–710.

Mann, H. B. (1945). Nonparametric tests against trend. *Econometrica*, 13(3),
245–259.

McCrae, J., Aguado-de-Cea, G., Buitelaar, P., Cimiano, P., Declerck, T.,
Gómez-Pérez, A., … Unger, C. (2012). Interchanging lexical resources on the
Semantic Web. *Language Resources and Evaluation*, 46(4), 701–719.

Ng, H. T., Wu, S. M., Wu, Y., Hadiwinoto, C., & Tetreault, J. (2013). The
CoNLL-2013 shared task on grammatical error correction. In *Proceedings of
CoNLL-2013 Shared Task*, 1–12.

Ng, H. T., Wu, S. M., Briscoe, T., Hadiwinoto, C., Susanto, R. H., &
Bryant, C. (2014). The CoNLL-2014 shared task on grammatical error
correction. In *Proceedings of CoNLL-2014 Shared Task*, 1–14.

Norvig, P. (2007). How to write a spelling corrector.
`https://norvig.com/spell-correct.html`

Piotrowski, M. (2012). *Natural Language Processing for Historical Texts*.
Morgan & Claypool.

Reul, C., Christ, D., Hartelt, A., Balbach, N., Wehner, M., Springmann, U.,
… Puppe, F. (2019). OCR4all — an open-source tool providing a (semi-)
automatic OCR workflow for historical printings. *Applied Sciences*, 9(22),
4853.

Springmann, U., Lüdeling, A., & Bollmann, M. (2016). OCR of historical
printings of Latin texts: Problems, prospects, progress. In *Proceedings of
the Digital Humanities 2016*, 578–580.

`indic-transliteration` Python library. Dhaval Patel et al.
`https://github.com/indic-transliteration/indic_transliteration`

`csl-orig` repository. Sanskrit Lexicon Project, 2014–2026.
`https://github.com/sanskrit-lexicon/csl-orig`

`csl-observatory` repository. M. Gasūns, Sanskrit Lexicon Project, 2026.
`https://github.com/sanskrit-lexicon/csl-observatory`

---

*Pre-submission draft, 2026-06-30. Target venue: LREC-COLING. Zenodo DOI [10.5281/zenodo.15834721](https://doi.org/10.5281/zenodo.15834721) minted 2026-07-01. Pending: human IAA (Cohen κ), neural baselines, submission.*
