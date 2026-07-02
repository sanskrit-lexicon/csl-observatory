# PWG citation link coverage

_Created: 02-07-2026 · Last updated: 02-07-2026_

A dictionary-content metric (complementing the observatory's org/process
metrics): how much of the PWG `<ls>` literary-source citation apparatus is
clickable — i.e. resolves to a Cologne **scan** (page image) or **HTML**
(digital text) target.

**Scope.** Measured over the ~51 PWG roots translated so far for the RU/EN
[article site](https://gasyoun.github.io/SanskritLexicography/) — a subset, **not**
the whole dictionary. Full-dictionary `<ls>` extraction lives in the PWG repo's
[`pwg_ls`](https://github.com/sanskrit-lexicon/PWG/tree/main/pwg_ls) work.

## Headline (snapshot 02-07-2026)

| metric | value |
|---|---:|
| citation occurrences | 50,065 |
| covered (link out) | 41,642 (83.2%) |
| &nbsp;&nbsp;• scan (page image) | 34,560 (69.0%) |
| &nbsp;&nbsp;• HTML (digital text) | 7,082 (14.1%) |
| uncovered (no Cologne target) | 6,505 |
| non-referential `<ls>` labels | 1,883 |
| distinct references | 37,951 |
| distinct coverage | 86.4% |
| un-digitised works cited | 446 |

Coverage is **target-limited**: the covered works are the heavily-cited backbone
(MBh., Ṛg-Veda, Rāmāyaṇa, Bhāgavata-Purāṇa …); the 446 uncovered works are mostly
un-digitised (Suśruta, the Upaniṣads, the Śrauta/Gṛhya sūtras) and cannot be
linked from anywhere.

## Source (live, always-current)

- data: [`observatory/site/src/data/pwg_citation_coverage.json`](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/observatory/site/src/data/pwg_citation_coverage.json)
- full reports (PWG repo): [`pwg_ls/pwg_ru_coverage/`](https://github.com/sanskrit-lexicon/PWG/tree/main/pwg_ls/pwg_ru_coverage) — [coverage index](https://github.com/sanskrit-lexicon/PWG/blob/main/pwg_ls/pwg_ru_coverage/CITATION_SOURCES.md) · [uncovered works](https://github.com/sanskrit-lexicon/PWG/blob/main/pwg_ls/pwg_ru_coverage/UNCOVERED_SOURCES.md) · [covered vs uncovered](https://github.com/sanskrit-lexicon/PWG/blob/main/pwg_ls/pwg_ru_coverage/COVERAGE_COMPARISON.md)
- generator: [`RussianTranslation/src/build_citation_index.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/build_citation_index.py)

_Dr. Mārcis Gasūns_
