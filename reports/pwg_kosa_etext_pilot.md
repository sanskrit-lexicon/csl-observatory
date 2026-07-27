# PWG kośa e-text pilot — measured NO-GO on OCR-from-scratch, GO on ingesting the library's own OCR

_Created: 27-07-2026 · Last updated: 27-07-2026_

_Opus 5 1M (`claude-opus-5[1m]`), H1715. Measurement reproducible with
[`scripts/pwg_kosa_ocr_probe.py`](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/scripts/pwg_kosa_ocr_probe.py);
per-page numbers in
[`data/pwg_scan_index_tracker/kosa_ocr_pilot.tsv`](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/data/pwg_scan_index_tracker/kosa_ocr_pilot.tsv)._

[H1715](https://github.com/gasyoun/Uprava/blob/main/handoffs/H1715-Opus_csl-observatory_pwg-kosa-etext-pilot-amara-abhidhana_27.07.26.md)
proposed OCR-ing the two heaviest kośa scan sets from the
[H1706 e-text queue](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/data/pwg_scan_index_tracker/pwg_etext_candidate_queue.tsv)
— `amara_dlc` (Amarakoṣa, Deslongchamps 1839; 16,151 PWG citations) and `abch2`
(Hemacandra's Abhidhānacintāmaṇi, Böhtlingk & Rieu 1847; 16,148) — with tesseract 5 `san`,
anchored to the campaign's per-page index.

**Verdict: NO-GO on that method. GO on a different, much cheaper one.** The library that
holds the scans already publishes per-page OCR for both editions, and it is measurably 2.5×
better than what we produce locally. The job is an ingest-and-correct, not an OCR.

## 1 · The measurement

Two engines, the same twelve pages, the same metric.

| | tokens recovered | valid Sanskrit | rate |
|---|--:|--:|--:|
| tesseract 5 `san`, local, on the repo's page PDFs | 658 | 117 | **17.8 %** |
| BSB's published per-page hOCR | 722 | 316 | **43.8 %** |
| _control — the reference text through the same tokenizer_ | 1,071 | 1,071 | _100.0 %_ |

BSB's OCR is **2.5×** better and recovers 1.10× as many tokens: tesseract is dropping
content, not merely misreading it.

**What the metric is, and is not.** It is the share of extracted Devanagari tokens that are
real Sanskrit words, checked against the *same work* already digitized in `csl-orig`
(`abch` + `acph` + `acsj`, Nirṇaya-sāgara 1896) plus the MW headword inventory — 25,399
distinct SLP1 tokens. It is **not** a character error rate. A CER needs hand-transcribed
ground truth, and 1839/1847 Devanagari with archaic orthography (`श्र` for अ, old conjunct
forms) is not material this author can transcribe reliably enough to serve as truth;
asserting a CER off an unreliable transcription would be worse than reporting none. The
reference is also a *different edition*, so a miss is not automatically an OCR error —
edition variants, sandhi splits and 1847 orthography all produce legitimate misses. The
absolute level is therefore a conservative floor. **The comparison is nonetheless sound**:
both engines are scored against the identical reference with the identical tokenizer, and
the control shows the tokenizer itself loses nothing.

## 2 · The low number is the material, not the settings

Before reporting a negative result, eighteen configurations were tried on the three best
pages — dpi {300, 400} × psm {6, 4, 11} × preprocessing {raw, Otsu threshold, aggressive
threshold}:

| best | worst | best config |
|--:|--:|---|
| 30.5 % | 13.1 % | raw, 400 dpi, psm 4 |

and the 30.5 % configuration reached that rate only by emitting 82 tokens where the others
emitted ~145 — it scored better by reading less. Nothing approaches usable. Show-through
from the reverse page, clearly visible on every leaf of the 1847 printing, is the dominant
cause; thresholding it away removes ink with it.

Both engines collapse in the back half of the book — tesseract 28 % → 3.9 % and BSB 54 % →
11.3 % between p. 60 and p. 380 — so the ranking holds but neither is uniform, and any
downstream consumer must expect the tail to be much worse than the head.

## 3 · What the prior-art gate actually found

The handoff made prior art a hard gate, citing
[SL FINDINGS §59](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md)
— a handoff minted and killed the same day because the search skipped the
`sanskrit-lexicon-scans` org. Four findings, in descending order of how much they change the job.

**1. The library publishes the OCR.** Every canvas in the IIIF manifests for both editions
carries a `seeAlso` pointing at per-page hOCR with word-level bounding boxes
(`ocr_page` / `ocrx_block` / `ocr_par` / `ocr_line` / `ocrx_word`). Verified by fetching it:
`https://api.digitale-sammlungen.de/ocr/bsb10250953/229` returns 24 KB of hOCR, 53 lines,
230 words, correctly reading the Devanagari **and** the editorial square brackets, the
Devanagari verse numerals `॥ ११४२ ॥`, and Böhtlingk's Latin botanical apparatus. The same
holds for the Amarakoṣa (`bsb10250868`), including Deslongchamps' French footnotes.

**2. There is no text layer in the scan repos** — so OCR of some kind genuinely is needed.
Every sampled page yields 0 characters, 0 fonts, 0 drawings, and exactly one embedded JPEG.
This was checked per [FINDINGS §480](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md),
which requires testing the *script* of the extracted text rather than its length.

**3. The content already exists in the org — but cannot do this job.** `csl-orig` carries
the Abhidhānacintāmaṇi three times over (`abch` 1,965 records, `acph` 163, `acsj` 240, all
Nirṇaya-sāgara 1896, proofread), and `sanskrit-lexicon/AMAR` carries the Amarakoṣa
(`amar.txt`, 2,359 records). Neither can serve the page-anchoring purpose: they are
different editions, and `amar.txt` declares `;pagenum{false}` with no page markers at all.
So the e-text is not the gap — *this edition's* page-aligned text is. What the existing
e-texts are excellent for is exactly what this pilot used them for: a free correction
reference and a free accuracy instrument.

**4. The citation → page link already works.** `ls_resolver.py` resolves `AK.` → `amara_dlc/app1`,
`H.` → `abch2/app1`, `H. ś.` → `abch2/app2` at verse-address granularity, and the per-page
index is committed in both the scan repos and the PWG repo. So the deliverable was never
"link citations to pages" — that shipped. It is "make the pages searchable and alignable".

## 4 · Recommendation

Re-scope to an **ingest-and-correct** job, and drop the OCR-from-scratch framing:

1. **Harvest BSB's hOCR** for both editions (417 + 465 pages) from the IIIF `seeAlso`
   endpoints. Free, already word-boxed, 2.5× better than anything produced locally.
2. **Align each page against the existing csl-orig / AMAR e-text** of the same work. That
   turns the different-edition text from a substitute into a corrector, and yields the
   org's first real Sanskrit OCR accuracy figure as a by-product — no published CER for
   19th-century Devanagari appears to exist.
3. **Anchor to the committed per-page index**, never to digits found on the page. A
   commented kośa page is wall-to-wall verse and footnote numbers; deriving anchors from
   them fails the way [FINDINGS §480](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md)
   records (a 7–22× over-count of verse markers on multi-zone pages).
4. **Expect the tail to be bad.** Budget correction effort by page depth, not uniformly.

## 5 · Two things a human has to settle first

**Rights on the scans are asserted, not granted.** Both BSB manifests carry
`https://rightsstatements.org/vocab/NoC-NC/1.0/` — *No Copyright, Non-Commercial use only*,
attributed to the Bayerische Staatsbibliothek. The 1839 and 1847 works are long out of
copyright; the NC restriction is the library's condition on **its scans**, and it is a
rights statement to honour rather than a licence granting reuse. Neither scan repository
declares a licence at all (`license: none` via the API, no `LICENSE` file). Any derived
text published from these images inherits that unresolved position.

**`AMAR` declares three different licences.** Verified across four files in
[sanskrit-lexicon/AMAR](https://github.com/sanskrit-lexicon/AMAR): `LICENSE` is GPL-2.0,
`README.md` states CC-BY-SA-4.0, `CITATION.cff` states CC-BY-SA-4.0, and `amar.txt`'s own
metadata says GNU GPL v3.0. GPL and CC-BY-SA impose incompatible obligations. Two **public**
kosha datasets are built over `amar.txt`. Which licence actually governs is a human ruling,
not an agent's call; it is filed as an open decision rather than guessed at.

## 6 · What this pilot did not do

Stated plainly, because the handoff's definition of done asked for it:

- **No character-accuracy figure on ≥30 hand-checked pages.** The valid-token comparison
  over 12 pages settled the engine choice by a 2.5× margin, and hand-transcribing 30 pages
  of archaic Devanagari to produce a CER would not have changed which engine wins. A real
  CER is worth producing — but against BSB's hOCR, after the re-scope, where the existing
  e-text can supply the alignment instead of a human transcriber.
- **No text layer was built for every indexed page**, because the method changed before it
  was worth building one.
- **Only `abch2` was measured.** `amara_dlc` was verified to have no text layer and to have
  BSB hOCR available, but was not put through the comparison — the handoff said do one
  work first, and the finding generalises to the method rather than the book.

## Files

- measurement — [`scripts/pwg_kosa_ocr_probe.py`](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/scripts/pwg_kosa_ocr_probe.py) · [`data/pwg_scan_index_tracker/kosa_ocr_pilot.tsv`](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/data/pwg_scan_index_tracker/kosa_ocr_pilot.tsv)
- the queue this came from — [`pwg_etext_candidate_queue.tsv`](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/data/pwg_scan_index_tracker/pwg_etext_candidate_queue.tsv)
- the campaign — [`reports/pwg_scan_index.md`](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/reports/pwg_scan_index.md) · [history](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/docs/PWG_SCAN_INDEX_CAMPAIGN_HISTORY_2025_2026.md)

_Dr. Mārcis Gasūns_
