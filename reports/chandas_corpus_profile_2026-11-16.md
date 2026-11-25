# Chandas corpus profile — meter detection over the DCS text layer (H6257)

_Created: 25-11-2026 · Last updated: 25-11-2026_

_Dr. Mārcis Gasūns · executor: OxAlpha (MiMo v2.6 Flash, ollama-cloud/mimo-v2.6-flash)_

First metrical work in the estate: a guru/laghu syllable scanner + meter
detector ([scripts/chandas_meter.py](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/scripts/chandas_meter.py)),
validated on 272 labelled stanzas, then run over the whole DCS CoNLL-U text
layer (270 texts) to produce the meter distribution by text and epoch.

## What the detector does

1. Normalise each DCS `# text` line (IAST), collapse IAST digraphs to phonemes
   so clusters count phonemically, merge `ai`/`au` diphthongs.
2. Mark every syllable **guru** (heavy) / **laghu** (light): long vowel or
   diphthong ⇒ guru; short vowel closed by a cluster or a word-final
   consonant (incl. `-ṃ`/`-ḥ`) ⇒ guru; single medial consonant (onset of the
   next syllable) ⇒ laghu. `e`/`o` are naturally guru (bha-guru).
3. Group lines into stanzas: DCS `sent_counter` groups where present, a bare
   line where a text has no counters (Vedic files).
4. Classify the stanza by its syllable-count signature against a pinned
   vṛtta table: 24 ⇒ gāyatrī (3×8), 30 ⇒ uṣṇih-class, 32 ⇒ anuṣṭubh/śloka
   (4×8), 44 ⇒ triṣṭubh (4×11), 52 ⇒ jagatī (4×13), 68 ⇒ 17×4
   mandākrānta/indravajrā. Anything else ⇒ `unclassified`.

## Validation (≥200 labelled stanzas) — `--validate`

Weak labels are text-level and independent of the detector:
Meghadūta is composed in mandākrānta (4×17); Vālmīki's Rāmāyaṇa is the
foundational anuṣṭubh kāvya (first 150 stanzas used).

| class | gold | TP | FN | precision | recall | F1 |
|---|---:|---:|---:|---:|---:|---:|
| 17×4 mandakranta/indravajra | 122 | 112 | 10 | 1.000 | 0.918 | 0.957 |
| anustubh/sloka (4×8) | 150 | 142 | 8 | 1.000 | 0.947 | 0.973 |
| **total** | **272** | **254** | **18** | — | — | — |

All 18 errors fall to `unclassified` (±1 syllable scanner residuals); there
are **zero cross-class confusions** (`as-other-class=0` per text). Labels:
[data/chandas_validation_labels_2026-11-16.tsv](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/data/chandas_validation_labels_2026-11-16.tsv).

## Canary — 20 hand-labelled stanzas, `--canary`

10 Meghadūta + 10 Rāmāyaṇa stanzas labelled by hand (syllable structure read
line by line, detector output hidden at labelling time), committed in
[data/chandas_canary_manual_2026-11-16.tsv](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/data/chandas_canary_manual_2026-11-16.tsv).

**Agreement 19/20 (gate ≥18).** The single disagreement is Rāmāyaṇa stanza
#160, where DCS grouped three 16-syllable lines (1.5 verses) into one
`sent_counter`; the hand label follows the lines themselves (anuṣṭubh).

## Corpus run — `--corpus`

Input: `VisualDCS/src/DCS-data-2026/conllu/files/` (corpus pinned at
`gasyoun/dcs-conllu @ 04e0778`, 270 texts, the DCS text layer). A text enters
the **poetic layer** if it has ≥50 grouped stanzas and ≥50% of them classify
into a table meter.

- **270 texts scanned, 94 poetic-layer texts, 199,470 classified stanzas**
  (16 s wall time), 297 distribution rows.
- Dataset:
  [data/chandas_meter_distribution_2026-11-16.tsv](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/data/chandas_meter_distribution_2026-11-16.tsv)
  (`text, epoch, meter, stanzas, classified_total`).

### Distribution by meter

| meter | stanzas | share |
|---|---:|---:|
| anustubh/sloka (4×8) | 190,644 | 95.6% |
| tristubh (4×11) | 7,504 | 3.8% |
| 17×4 mandakranta/indravajra | 584 | 0.3% |
| jagati (4×13) | 340 | 0.2% |
| usnih-class | 285 | 0.1% |
| gayatri (3×8) | 113 | 0.1% |

The śloka's dominance is the epic/purāṇa/katha profile of the corpus itself:
the two biggest poetic texts alone (Mahābhārata 59,363; Rāmāyaṇa 17,448) are
anuṣṭubh works.

### Distribution by epoch

Epochs come from a hand-encoded conventional-dating map
([data/chandas_text_epochs_2026-11-16.tsv](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/data/chandas_text_epochs_2026-11-16.tsv);
vedic ≤−500, early-classical −499…299, classical 300…699, medieval ≥700).

| epoch | stanzas | share | texts | dominant meters |
|---|---:|---:|---:|---|
| vedic | 154 | 0.1% | 2 | anustubh 123, tristubh 26 |
| early-classical | 22,700 | 11.4% | 6 | anustubh 22,210, tristubh 472 |
| classical | 95,198 | 47.7% | 20 | anustubh 89,420, tristubh 5,112, 17×4 286, jagati 231 |
| medieval | 80,257 | 40.2% | 62 | anustubh 77,795, tristubh 1,887, 17×4 241 |
| unknown (4 texts) | 1,161 | 0.6% | 4 | — |

Triṣṭubh and the 17-syllable kāvya metres concentrate in the classical bucket
(Mahābhārata, Kumārasaṃbhava, Meghadūta, Buddhacarita-era works); the
medieval bucket is the nighaṇṭu/rasa/purāṇa verse mass, śloka-dominated.

## Limits of this pass (honest scope)

1. **Count-signature classification, not yet guru-pattern templates.** The
   guru/laghu marks are computed and unit-tested per syllable
   (`--selftest`, 7 checks incl. a prose negative control), but family
   disambiguation that needs the weight pattern is deferred: mandākrānta vs
   indravajrā both sit at 68, triṣṭubh has four pattern variants, and the
   **āryā/mātrā-chandas family** (Amaruśataka, Gītagovinda: constant morae,
   variable syllables) is not in the table at all — such texts surface only
   through whatever syllabic verses they contain.
2. **Vedic undercount.** Ṛgveda & saṃhitā files carry no `sent_counter`, so
   stanzas are single lines and most Vedic line-shapes (22, 15, 9…) fall
   outside the table; Ṛgveda does not reach the ≥50% poetic filter. The 2
   vedic-bucket texts that do pass are Atharvavedapariśiṣṭa and
   Kaṭhopaniṣad.
3. **18/272 validation stanzas** are still ±1 syllable scanner residuals
   (word-boundary/anusvāra edges); one DCS verse-grouping anomaly is visible
   in the canary.
4. **Weak labels are text-level** (Meghadūta = mandākrānta,
   Rāmāyaṇa = anuṣṭubh) — genuine internal metrical variety inside a text
   counts against recall, not against precision.

Residuals are filed as dated `@DO` rows in Uprava `GTD_NEXT_ACTIONS.md`.

## Reproduce

```bash
python3 scripts/chandas_meter.py --selftest   # scanner unit checks
python3 scripts/chandas_meter.py --validate   # 272-stanza validation table
python3 scripts/chandas_meter.py --canary     # 20 hand-labelled stanzas
python3 scripts/chandas_meter.py --corpus     # regenerates the distribution TSV
```

`DCS_CONLLU_ROOT` overrides the default CoNLL-U root.
