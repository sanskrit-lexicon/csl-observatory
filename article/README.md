# Article folder

This folder contains articles on the Cologne Digital Sanskrit Dictionaries
(CDSL). A61 in the sibling `SanskritGrammar` repository is now the canonical
historical synthesis. A13 (`00-report-narrative.md`) is an independent,
complementary study of repository evidence and the transition from
founder-led work to distributed infrastructure; it is not a memoir companion
that duplicates A61.

## Files

| File | Authors | Voice | Topic |
|---|---|---|---|
| [`00-report-narrative.md`](00-report-narrative.md) | Mārcis Gasūns | Analytical history with situated first-person evidence | What repository records reveal and conceal; founder-to-community transition |
| [`01-empirical-companion.md`](01-empirical-companion.md) | Funderburk, Patel, Rao, Gasūns | Formal third-person | Quantitative survey, runbook, standards alignment, infrastructure |
| [`refs.bib`](refs.bib) | — | — | BibTeX bibliography for the companion paper |
| [`A15_github_ecosystem.md`](A15_github_ecosystem.md) | Gasūns | Formal third-person | A15 full draft: CDSL as a GitHub maintenance ecosystem (seven analytical findings incl. the data-layer bus factor, the correction-loop anatomy + 52,498-event ledger, the `csl-orig` campaign case study, claim→artifact inventory; boundary note vs the pair above) |
| [`A48_error_recapture.md`](A48_error_recapture.md) | Gasūns | Formal third-person | A48 skeleton: capture–recapture estimate of residual errors |

The report has a legacy root mirror at
[`gasuns-cologne-30-report.md`](../gasuns-cologne-30-report.md). It is not an
authoritative submission source; the version in this folder is canonical and
the only version that shares the A61 evidence contract.

## Build

To produce a typeset PDF of the companion paper:

```sh
pandoc article/01-empirical-companion.md \
  --citeproc \
  --bibliography article/refs.bib \
  --csl article/indo-iranian-journal.csl \
  -o article/01-empirical-companion.pdf
```

The narrative report (`00-report-narrative.md`) carries its own
hand-formatted, IIJ-style author-date reference list, so it builds
without `--citeproc`. To produce the submission Word file and a
fonts-embedded PDF:

```sh
# Word (.docx) for the IIJ email submission
pandoc article/00-report-narrative.md \
  -o article/00-report-narrative.docx

# fonts-embedded PDF (xelatex handles the Sanskrit diacritics)
pandoc article/00-report-narrative.md \
  --pdf-engine=xelatex \
  -V mainfont="Brill" \
  -o article/00-report-narrative.pdf
```

If the *Brill* font is not installed, substitute another Unicode font
with full IAST coverage — `-V mainfont="Times New Roman"` (used for the
committed `00-report-narrative.pdf`, 26 pp., all fonts embedded) or
`-V mainfont="Noto Serif"` both work; or drop the `-V mainfont` line to
fall back to Latin Modern.

## Submission target

Indo-Iranian Journal (Brill). A13 is designed to stand alone; A61 targets the
World Sanskrit Conference and may be cited as the wider synthesis. The
bibliography uses
[`indo-iranian-journal.csl`](indo-iranian-journal.csl), an author-date
style based on the Chicago Manual of Style 18th edition (adjust to Brill
house style as needed).

## Licence

Both articles are licensed CC BY 4.0. The data and figures referenced in
the companion paper are licensed CC BY 4.0 (see `../DATA_LICENSE.md`) and
live in `../data/`.
