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

The narrative report is already in publication-ready Pandoc Markdown.

## Submission target

Indo-Iranian Journal (Brill). The paired articles are formatted for the
journal's house style; the bibliography uses the Brill Indo-Iranian Journal
CSL stylesheet (to be added).

## Licence

Both articles are licensed CC BY 4.0. The data and figures referenced in
the companion paper are licensed CC BY-SA 4.0 and live in `../data/`.
