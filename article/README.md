# Article folder

This folder contains the source for two paired articles on the Cologne
Digital Sanskrit Dictionaries (CDSL). They are intended to be submitted
together as a "narrative + companion" pair; reviewers and readers may also
read either independently.

## Files

| File | Authors | Voice | Topic |
|---|---|---|---|
| [`00-report-narrative.md`](00-report-narrative.md) | Mārcis Gasūns | First-person scholarly narrative | The thirty-year history of CDSL: founders, disputes, archives, hopes |
| [`01-empirical-companion.md`](01-empirical-companion.md) | Funderburk, Patel, Rao, Gasūns | Formal third-person | Quantitative survey, runbook, standards alignment, infrastructure |
| [`refs.bib`](refs.bib) | — | — | BibTeX bibliography for the companion paper |

The narrative report (`00-report-narrative.md`) is also mirrored at the
root of the repository as [`gasuns-cologne-30-report.md`](../gasuns-cologne-30-report.md);
the version in this folder is the canonical source for the article submission.

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

If the *Brill* font is not installed, drop the `-V mainfont` line or
substitute another Unicode font with full IAST coverage (e.g.
`-V mainfont="Noto Serif"`).

## Submission target

Indo-Iranian Journal (Brill). The paired articles are formatted for the
journal's house style; the bibliography uses
[`indo-iranian-journal.csl`](indo-iranian-journal.csl), an author-date
style based on the Chicago Manual of Style 18th edition (adjust to Brill
house style as needed).

## Licence

Both articles are licensed CC BY 4.0. The data and figures referenced in
the companion paper are licensed CC BY-SA 4.0 and live in `../data/`.
