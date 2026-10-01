# Andhrabharati `<ls>` update vs CDSL pwgbib — full-auto diff + MG rulings

_Created: 24-09-2026 · Last updated: 24-09-2026_

## Provenance

- `PWG-ls.txt` is **Andhrabharati's update to CDSL** — MG ruling 24-09-2026:
  «The .txt file give is what Andhrabharati made, it's an update to CDSL».
- Received file pinned as sha256
  `f44ae1bbccca1ceb508e9da0c1c389dcb93910fb570d0a4d962819cf756b5fd0`
  (as received; this repo's copy is LF-normalized by `.gitattributes`, so the
  committed bytes differ from the received file by line endings only).
- CDSL side: `csl-pywork/v02/distinctfiles/pwg/pywork/pwgauth/pwgbib_input.txt`
  (4-tab: id, code, iast, tooltip) — 2844 records, 2838 distinct codes,
  6 codes on 2+ records (`LIA.`, `KANDYUR`, `WILSON, Hindu Th.`, …).

## Method

Generator: [scripts/andhrabharati_ls_diff.py](../../../scripts/andhrabharati_ls_diff.py).
Normalization NFC + whitespace collapse; **case preserved** — case is meaningful
in this bibliography (`S.` vs `s.`, `Un.` vs `UN.` are different works; see the
H2874 caveat on ls_counts). After the exact pass, a case-fold pass and a
CDSL-style longest-prefix pass decompose each residue class.

## Numbers

| set | count |
|---|---|
| PWG-ls distinct values (Andhrabharati update) | 2680 |
| CDSL pwgbib distinct codes | 2838 |
| exact match, both sides | 2006 |
| added (in update, not in CDSL) | 674 |
| — of which case-only variant | 10 |
| — of which extends a known code (`AIT. BR. Comm.`, `MBH. ed. Calc.`) | 449 |
| — **true unknowns, no bib record at all** | **215** |
| removed (in CDSL, dropped by update) | 832 |
| — of which case-only variant | 19 |
| — of which cited in extended form (prefix of longer ls value) | 86 |
| — **totally uncited by the update** | **727** |

Artifacts in this directory: `PWG-ls.txt` (input), `pwg_ls_vs_cdsl_added.tsv`
(674, with prefix-resolution + class columns), `pwg_ls_vs_cdsl_deleted.tsv`
(832, with pwgbib ids), `pwg_ls_vs_cdsl_unknown.tsv` (215), and the first-pass
taxonomy draft `pwg_ls_taxonomy_draft.tsv` (book-work 2433 · person-western 151 ·
journal-periodical 55 · person-author 28 · commentary 13).

## MG rulings (grill, 10 cards, 24-09-2026, chat)

1. No deletion queues — full auto comparison only; the txt is Andhrabharati's
   update, not a repair proposal.
2. The 215 unknowns become new pwgbib entries tagged `[Cologne Addition]`
   (existing in-file convention, cf. 1.004a).
3. Bare ALL-CAPS name pool (750 tokens, morphology resolves 38): rules +
   MW name-lexicon cross-check + human-residue review sheet.
4. Full extra-class set: person (+subtype), book, journal, **kośa/dictionary,
   manuscript-Hdschr, German-academy-series**, commentary, edition-qualifier.
5. Regenerate + pin sha256 (input pinned above).
6. Text defects (AGAYAPĀLA→AJAYAPĀLA, AMṚTABINDŪP. vs bib AMṚTAV. UP., `AINSL`,
   case + candrabindu/Ṣ-Ś variants) are **documented as a pwgissues issue** —
   «We do not change pwg.txt, but can propose changes».
7. Local overlay + upstream PR offer for the pwgbib additions.
8. Repair first, then classify.
9. Classifier lands in csl-observatory `scripts/` beside `pwg_ls_counts.py`;
   kosha `datasets.json` registration when published.
10. Flat `person` class + nullable subtype column (sanskrit-author /
    western / royal-mythic).

## Follow-on

- **H5465 (OxAlpha)** — 215 `[Cologne Addition]` entries + pwgissues defect
  issue + upstream PR + kosha registration.
- **H5466 (Fable 5)** — full-set taxonomy classifier with `--check` gate +
  human-residue review sheet (runs after H5465, per ruling 8).

_Гасунс_
