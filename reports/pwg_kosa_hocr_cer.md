# PWG kośa hOCR ingest — first CER measurement against a print e-text (amara_dlc)

_Created: 28-07-2026 · Last updated: 28-07-2026_

_Sonnet 5 (`claude-sonnet-5`), H1720. Reproducible with
[`scripts/pwg_kosa_hocr_ingest.py`](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/scripts/pwg_kosa_hocr_ingest.py);
per-page data in
[`data/pwg_kosa_hocr/amara_dlc/`](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/data/pwg_kosa_hocr/amara_dlc/)
(cached hOCR under `raw/`, stripped text under `text/`, alignment output in `manifest.tsv`
and `cer_sample.tsv`)._

[H1715](https://github.com/gasyoun/Uprava/blob/main/handoffs/archive/H1715-Opus_csl-observatory_pwg-kosa-etext-pilot-amara-abhidhana_27.07.26.md)
measured that BSB's already-published per-page hOCR beats local tesseract 5 `san` by 2.5×
on a token-validity metric, but could not report a character error rate — see
[`reports/pwg_kosa_etext_pilot.md`](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/reports/pwg_kosa_etext_pilot.md)
§1 for why (no reliable hand-transcribed ground truth). This handoff (H1720) closes that
gap for one of the two editions, `amara_dlc` (Amarakoṣa, Deslongchamps 1839, BSB
`bsb10250868`), by harvesting the BSB hOCR for every indexed page and aligning it against
the existing [`AMAR/amar.txt`](https://github.com/sanskrit-lexicon/AMAR) e-text — a
different edition of the same work, already digitized and committed, which stands in as
reference text where no hand transcription exists.

## 1 · What was harvested

Every page the `amara_dlc` campaign index (`app1/pywork/index.txt`) references — 374
distinct repo pages out of 417 index rows (several rows share a page: more than one
section/verse range starts on the same leaf) — was fetched from
`https://api.digitale-sammlungen.de/ocr/bsb10250868/<n>` and cached. **374/374, zero
fetch errors.** The BSB→repo page offset was derived empirically rather than assumed —
per the handoff's explicit warning not to copy `abch2`'s offset (`-1`) across editions —
by token-overlap matching at two independent anchor pages (repo page 32, the first
substantive content page, and repo page 229, deep into kāṇḍa 2); both agree on offset
**-3** for `amara_dlc`.

## 2 · Alignment method for CER

`index.txt`'s own section/verse-number columns do not line up with `AMAR/amar.txt`'s
citation scheme cleanly enough to trust a literal cross-reference match — the exact
FINDINGS §480 trap this handoff warns against (there: a 7–22× over-count from anchoring on
in-page digits), applied here to citation numbers instead of page numbers. Instead each
hOCR page is aligned to AMAR **by content**: the search is restricted to the correct kāṇḍa
(unambiguous — `index.txt`'s `book` column against AMAR's `;k{}` markers), then a window
the length of the page's token count is slid across that kāṇḍa's token stream and scored
by token-multiset overlap with the page; the highest-scoring window becomes the reference
for that page. This is the same token-overlap principle
[`pwg_kosa_ocr_probe.py`](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/scripts/pwg_kosa_ocr_probe.py)
used to derive the `abch2` offset, applied per page instead of once globally.

Manual spot-check (page 229, kāṇḍa 2, overlap score 29/116 tokens) confirms the aligned
window is the genuinely corresponding passage — the printed edition's
`निषूदनं निहिंसनं । निर्वासनं संज्ञपनं ...` list matches AMAR's `निषूदन क्ली निहिंसन क्ली
निर्वासन क्ली संज्ञपन क्ली ...` word-for-word in content and order.

## 3 · CER

Stratified sample, ~4 pages per page-depth decile → **39 pages** (≥30 required). Text
normalized to bare Devanagari token streams (numerals, Latin verse/section markers, and
punctuation stripped from both sides) before Levenshtein distance.

| decile | n | mean CER |
|--:|--:|--:|
| 1 | 4 | 0.709 |
| 2 | 4 | 0.728 |
| 3 | 4 | 0.636 |
| 4 | 4 | 0.716 |
| 5 | 3 | 0.747 |
| 6 | 5 | 0.703 |
| 7 | 4 | 0.746 |
| 8 | 4 | 0.694 |
| 9 | 4 | 0.743 |
| 10 | 3 | 0.805 |

**Overall mean CER (unweighted, 39 pages): 0.719.**

Unlike H1715's engine comparison (both engines scored against the same reference, so a
relative ranking is safe even with an imperfect reference), this is an **absolute** figure
and needs two caveats before it is read as "72% OCR error":

- **Edition variance is baked in**, as flagged going in: AMAR is a different edition
  (a different print run's word list) from the 1839 Deslongchamps page being OCR'd, so a
  mismatch is not automatically an OCR mistake.
- **A format mismatch inflates the number further, and is the dominant one at this sample
  size.** `AMAR/amar.txt` is a per-word gloss list — every noun carries an inline
  grammatical-gender tag (`क्ली`, `पुं`, `स्त्री`) that has no counterpart in the printed
  verse text at all (compare §2's spot-check: AMAR's `निषूदन क्ली निहिंसन क्ली...` against
  the page's plain `निषूदनं निहिंसनं...`). Every one of those tags shows up as pure edit
  distance against a hOCR page that is reading real, matching content correctly. **The
  0.719 figure is therefore a ceiling, not a floor** — true OCR CER against a
  same-format, same-edition ground truth would read measurably lower. No published CER for
  19th-century Devanagari appears to exist to compare against; this is offered as a first,
  honestly-caveated number, not a final one.
- The tail-degradation pattern H1715 found in the token-validity metric does **not**
  clearly reappear in CER by decile here (0.709 → 0.805 across deciles 1→10, but decile 3
  is the sample's best at 0.636) — plausibly because the gender-tag noise floor dominates
  over whatever OCR-quality signal exists at this sample size.

## 4 · What this does not cover yet

- **`abch2` (Hemacandra) is not harvested.** The DoD for this handoff is met by one
  edition; `abch2`'s hOCR harvest, its own empirically-derived offset, and a CER against
  `csl-orig/v02/abch` remain open follow-on work.
- **The `abch2` index drift** the handoff flagged (`app1/index.js` vs.
  `PWG/pwgissues/issue104/abch_index.txt` disagreeing at page 119 and page 200) touches only
  `abch2` and was not investigated in this pass — it does not block `amara_dlc`'s
  completion and is carried forward as-is.

## Attribution

Page images and their hOCR are from the Bayerische Staatsbibliothek
(`bsb10250868`), the way [`amara_dlc/app1/info.html`](https://github.com/sanskrit-lexicon-scans/amara_dlc)
already credits them.

_Dr. Mārcis Gasūns_
