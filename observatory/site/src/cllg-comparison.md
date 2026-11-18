---
title: CLLG vs the Sanskrit estate (18-11-2026)
toc: false
---

_Created: 18-11-2026 · Last updated: 18-11-2026_

# CLLG vs the Sanskrit estate — 18-11-2026

_Dr. Mārcis Gasūns_

A dated strategic comparison of CLLG (Corpus Liberatum Linguae Graecae) with the open-Sanskrit estate and the proprietary TLG. Snapshot frozen at **18-11-2026**; a re-run produces a new dated document, never a silent edit. The full internal evidence appendix — including the estate's internal ops tooling — lives in the source document linked below.

## How to read

1. **Closest-analogue mapping is interpretive.** Where CLLG has no counterpart (notably pedagogy/product), the comparison maps to the nearest enabling artefact. A mapped verdict is not a like-for-like measurement; the mapping is named in the axis note below.
2. **TLG's cells are mostly NO COMPARABLE DATA.** TLG is a proprietary subscription resource. That is the finding, not a shortfall of effort. Where a public proxy exists (the A68 canon-coverage measure), it is used and labelled as a proxy.
3. **"No counterpart" was a decision, not an omission.** The estate scope deliberately includes internal ops tooling; its CLLG analogue is the project's public repository governance. Cells marked `internal-only` in the evidence are visible here but omitted from the public page.

## Scorecard

| Axis | CLLG | Open-Sanskrit estate | TLG | vs CLLG | vs TLG | Evidence |
|---|---|---|---|---|---|---|
| Corpus scale & coverage | Freed (TLG CD-ROM E re-encoded), Sources Chrétiennes (Irenaeus excluded), Nova in development; ~185,000 synthetic pages from 4,582 works; CLLG-ACDC 838k line images; printed dataset 60 files / 2,113 lines / 69,351 chars | DCS 5.69M running-text tokens over 270 texts; 44 digitised dictionaries / 1.49M `<L>` records; ~323k union headwords; 155 registered datasets; 1.09M word-aligned Sa→Ru rows; 828,505 resolved citations over 912 texts | Proprietary corpus + curated Canon; no public token counts on comparable axes | LEADS | NO COMPARABLE DATA | [CLLG landing](https://cllg-project.github.io/); [A68](https://github.com/gasyoun/Uprava/blob/main/papers/A68/iscls.tex) 5.69M / 25.2% / 77.9%; [FEATURES_INDEX](https://github.com/gasyoun/SanskritLexicography/blob/master/FEATURES_INDEX.md) A1/E44/C13/E49/E38; [kosha manifest](https://github.com/gasyoun/kosha/blob/main/data/manifest/datasets.json) 155 datasets |
| OCR/HTR tech + accuracy | Kraken/eScriptorium polytonic model; segmentation model awaiting a Kraken fix; Qwen3VL-8B 1.0% CER on real scans; distant supervision 5.8–6.9% mean CER; dedicated visual-grounding failure study | VLM OCR recipe (PyMuPDF 300 dpi + qwen3-vl-plus) measured on Stch.pdf: 232 IAST diacritics vs gemini 166; tesseract ships zero; two-pass verify measured and REJECTED; Gorresio image-only volumes via tesseract-5 `san` | No public OCR pipeline | TRAILS | NO COMPARABLE DATA | [CLLG landing](https://cllg-project.github.io/) publications; [REUSE_INDEX](https://github.com/gasyoun/Uprava/blob/main/REUSE_INDEX.md) §1 `tools/ocr_vlm/`; FEATURES_INDEX E50 |
| Encoding & interoperability | TEI XML native with `pb`/`lb`, canonical `citeStructure`; Biblissima Textes DTS API planned; schema-constrained TEI encoding lifts validity 9.0%/23.7% → 97.3%/99.3% with adapted 0.6B models | Custom `<L>` markup plus `make_xml.py` TEI exports; MDF/LIFT with semdom `\sd` layer; DCS CoNLL-U; KoshaSHRI vocable adapter; no DTS endpoint | Proprietary encoding with its own citation scheme; no public interoperability spec | TRAILS | NO COMPARABLE DATA | [CLLG landing](https://cllg-project.github.io/); [REUSE_INDEX](https://github.com/gasyoun/Uprava/blob/main/REUSE_INDEX.md) §1 `csl-pywork`, C19 semdom; FEATURES_INDEX C21 |
| Openness & licensing | All data/tools free; Apache-2.0 scanner; CC-BY 4.0 printed dataset; Nakala, GitLab, GitHub, Zenodo, HuggingFace; Garnier v Droz legal basis | CC-BY-SA 4.0 data (kosha), CC-BY 4.0 OBS-T, GPL-3.0 code; Zenodo code DOI `10.5281/zenodo.24055368`; public GitHub issue governance | Commercial subscription; closed | PARITY | LEADS | [CLLG landing](https://cllg-project.github.io/); [DATA_LICENSE.md](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/DATA_LICENSE.md); [CHANGELOG](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/CHANGELOG.md) v1.15.2 |
| Tooling & UX | CLLG-Scanner: offline PDF/DjVu/image/ALTO → TEI desktop app, Apache-2.0; Kraken-JS for Node/Electron inference; HTRMoPo model hosting; live demo | 23 interfaces (17 live), 17 tools; csl-websanlexicon endpoints; VisualDCS; `sanskrit-util` package; public sandhi-bench with deterministic grader; internal claim/sweeper/harness tooling | Closed subscription client | LEADS | LEADS | [CLLG landing](https://cllg-project.github.io/) + [scanner repo](https://github.com/cllg-project/cllg-scanner); [FEATURES_INDEX](https://github.com/gasyoun/SanskritLexicography/blob/master/FEATURES_INDEX.md) at a glance; F52 sandhi-bench (additional internal-only evidence withheld) |
| Team / funding / governance | ANR-24-RRII-0002 (France 2030), Inria Quadrant / PIQ, ALMAnaCH Inria Paris; named five-person team; public GitLab + GitHub | Independent scholar + volunteer correctors (52,498 events, 210 correctors across 43 dictionaries); 76 per-dictionary repos with public issue tracking; no equivalent institutional grant | UC Irvine since 1972, subscription-funded, permanent institutional host | TRAILS | TRAILS | [CLLG landing](https://cllg-project.github.io/); [benchmarks.md](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/observatory/site/src/benchmarks.md) 76 repos / 2014; FEATURES_INDEX E41 (additional internal-only evidence withheld) |
| Publications & impact | Four named 2026 outputs (arXiv 2603.02803, arXiv 2605.27750, HAL 05732106, HAL 05732094) with headline CER and TEI-validity numbers | 74 A-series papers registered in ARTICLES.md; A61/A68 measurement line; LREC-COLING OBS-T paper; Zenodo data + code DOIs; dedicated benchmarks page | Foundational scholarship and the Canon; not comparable on modern article counts | LEADS | NO COMPARABLE DATA | [CLLG landing](https://cllg-project.github.io/) publications; [ARTICLES.md](https://github.com/gasyoun/Uprava/blob/main/ARTICLES.md) A01–A74; [PUBLICATIONS.md](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/docs/PUBLICATIONS.md) |
| Pedagogy / product | **Closest-analogue mapping:** no pedagogical arm; mapped to community-enablement artefacts (HTRMoPo models, HuggingFace datasets, scanner live demo) | Learner-facing products: Systema-Sanscriticum courses, native SRS, 12 drill/practice sets (P1–P12), LILA exercises; 17 live interfaces | **Closest-analogue mapping:** the curated Canon functions as a curricular list; no learner products | LEADS | LEADS | [CLLG landing](https://cllg-project.github.io/) resources; [FEATURES_INDEX](https://github.com/gasyoun/SanskritLexicography/blob/master/FEATURES_INDEX.md) P1–P12; [REUSE_INDEX](https://github.com/gasyoun/Uprava/blob/main/REUSE_INDEX.md) §5 Systema |

## Adoption moves

1. **Publish a char-error benchmark for the estate's OCR recipe.** Freeze a printed-Sanskrit sample, measure CER against human transcriptions, and publish alongside the existing diacritic counts. Closes the only clear technical deficit (OCR axis).
2. **Ship a TEI/DTS export profile for one dictionary corpus.** Reuse `make_xml.py` and the existing citation maps; publish a `pb`/`lb`-anchored TEI sample and a DTS endpoint probe. Closes the encoding/interoperability deficit.
3. **Adopt the offline-first scanner pattern for Sanskrit.** Port the CLLG-Scanner *pattern* (not its code) to a PDF/DjVu → structured Sanskrit e-text path, with a local-only default. Extends the tooling lead into CLLG's strongest UX.
4. **Consolidate the estate's CLLG/TLG positioning into a reusable page.** The generator and public page in this handoff are the first instance; refresh by new dated snapshot, never by silent edit.

Source of record: [internal comparison doc](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/docs/CLLG_VS_SANSKRIT_ESTATE_18-11-2026.md). Internal-only evidence is withheld from this page by `scripts/gen_cllg_comparison_page.py`; run `--check` to verify parity.

_Dr. Mārcis Gasūns_
