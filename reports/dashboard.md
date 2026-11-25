# CDSL ecosystem dashboard

**Snapshot date**: 2026-11-23 · **Fetched**: 2026-11-23T17:44:41.691158Z · **Snapshot**: `csl-obs/org-live@1.0.0` (as of 2026-11-23)

## Headline numbers

| Metric | Value |
|---|---|
| Repositories in `sanskrit-lexicon` | 89 |
| Repositories with issues enabled | 89 |
| Total issues (incl. closed) | 8,803 |
| Total pull requests | 3,032 |
| Total commits in default branches | 15,217 |
| Distinct contributors (commit authors + issue authors) | 73 |
| Triaged repositories (taxonomy applied) | 63 |

## Issue type distribution across all triaged repos

| Type | Count | % of typed issues |
|---|---:|---:|
| `link-target` | 106 | 2.4 % |
| `link-splitting` | 10 | 0.2 % |
| `markup` | 331 | 7.6 % |
| `text-correction` | 2881 | 65.9 % |
| `content-enhancement` | 323 | 7.4 % |
| `encoding` | 73 | 1.7 % |
| `scan-quality` | 46 | 1.1 % |
| `bug` | 320 | 7.3 % |
| `question` | 280 | 6.4 % |

```mermaid
pie title Issue type distribution
    "link-target" : 106
    "link-splitting" : 10
    "markup" : 331
    "text-correction" : 2881
    "content-enhancement" : 323
    "encoding" : 73
    "scan-quality" : 46
    "bug" : 320
    "question" : 280
```

## Type × repository heatmap

| Type | ACC | AMAR | AP | AP90 | ApteES | ArabicInSanskrit | BEN | BHS | BOP | BOR | BUR | CAE | CCS | COLOGNE | DCS | FRI | GRA | GreekInSanskrit | IEG | INM | KNA | KOW | KRM | LRV | MCI | MD | MW72 | MWS | MWinflect | PUI | PWG | PWK | SCH | SHS | SKD | STC | VCP | VEI | WIL | Wil-YAT | alternateheadwords | cologne-stardict | csl-apidev | csl-app | csl-corrections | csl-devanagari | csl-doc | csl-inflect | csl-kale | csl-ldev | csl-lnum | csl-lslink | csl-newsletter | csl-observatory | csl-orig | csl-pywork | csl-sqlite | csl-westergaard | hwnorm1 | hwnorm2 | literarysource | mw-dev | rvlinks | total |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `link-target` | 0 | 0 | 2 | 3 | 0 | 0 | 2 | 0 | 0 | 0 | 0 | 0 | 0 | 1 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 13 | 0 | 0 | 74 | 7 | 0 | 0 | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 2 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | **106** |
| `link-splitting` | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 | 0 | 0 | 8 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | **10** |
| `markup` | 12 | 1 | 20 | 10 | 6 | 0 | 12 | 4 | 1 | 1 | 1 | 1 | 1 | 9 | 1 | 3 | 8 | 0 | 0 | 4 | 0 | 0 | 1 | 11 | 1 | 3 | 1 | 54 | 0 | 0 | 38 | 57 | 5 | 1 | 2 | 2 | 4 | 1 | 6 | 3 | 0 | 0 | 0 | 0 | 11 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 35 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | **331** |
| `text-correction` | 0 | 0 | 2 | 4 | 3 | 0 | 0 | 1 | 4 | 1 | 3 | 1 | 0 | 0 | 0 | 0 | 6 | 0 | 0 | 1 | 0 | 0 | 0 | 3 | 0 | 4 | 1 | 46 | 0 | 1 | 7 | 9 | 0 | 0 | 4 | 0 | 7 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 128 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 2645 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | **2881** |
| `content-enhancement` | 2 | 0 | 3 | 6 | 2 | 0 | 3 | 2 | 1 | 0 | 2 | 2 | 1 | 125 | 1 | 5 | 15 | 0 | 1 | 3 | 1 | 1 | 3 | 3 | 0 | 6 | 0 | 30 | 0 | 0 | 22 | 23 | 4 | 1 | 5 | 1 | 7 | 0 | 10 | 1 | 0 | 0 | 0 | 0 | 6 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 25 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | **323** |
| `encoding` | 1 | 0 | 2 | 4 | 0 | 0 | 2 | 0 | 1 | 1 | 0 | 0 | 0 | 5 | 0 | 1 | 3 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 1 | 2 | 10 | 0 | 2 | 11 | 1 | 2 | 1 | 2 | 0 | 1 | 0 | 0 | 2 | 0 | 0 | 0 | 0 | 13 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 4 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | **73** |
| `scan-quality` | 0 | 0 | 0 | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 1 | 1 | 0 | 2 | 2 | 0 | 0 | 0 | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 3 | 0 | 0 | 5 | 3 | 0 | 0 | 1 | 0 | 1 | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 23 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | **46** |
| `bug` | 0 | 1 | 3 | 1 | 2 | 0 | 8 | 0 | 0 | 0 | 0 | 0 | 0 | 40 | 1 | 0 | 3 | 3 | 0 | 0 | 0 | 0 | 0 | 8 | 0 | 1 | 0 | 19 | 0 | 0 | 16 | 4 | 0 | 0 | 2 | 0 | 5 | 0 | 1 | 0 | 1 | 13 | 13 | 4 | 39 | 9 | 3 | 1 | 2 | 6 | 0 | 0 | 0 | 2 | 85 | 17 | 0 | 1 | 4 | 0 | 0 | 1 | 1 | **320** |
| `question` | 4 | 0 | 2 | 3 | 2 | 3 | 0 | 0 | 1 | 1 | 0 | 0 | 0 | 78 | 1 | 0 | 1 | 3 | 1 | 2 | 0 | 0 | 0 | 5 | 1 | 0 | 2 | 22 | 8 | 1 | 12 | 10 | 1 | 1 | 4 | 0 | 6 | 0 | 0 | 0 | 5 | 1 | 4 | 1 | 46 | 1 | 0 | 1 | 0 | 1 | 0 | 0 | 1 | 0 | 38 | 2 | 0 | 0 | 2 | 0 | 0 | 2 | 0 | **280** |

## Activity by year

| Year | Commits | Issues opened | Issues closed |
|---|---:|---:|---:|
| 2014 | 125 | 190 | 65 |
| 2015 | 420 | 271 | 170 |
| 2016 | 396 | 175 | 140 |
| 2017 | 276 | 268 | 130 |
| 2018 | 152 | 98 | 30 |
| 2019 | 417 | 246 | 144 |
| 2020 | 631 | 470 | 485 |
| 2021 | 1705 | 639 | 485 |
| 2022 | 707 | 451 | 382 |
| 2023 | 580 | 534 | 542 |
| 2024 | 620 | 372 | 381 |
| 2025 | 873 | 1169 | 213 |
| 2026 | 8315 | 888 | 1753 |

## Top contributors (by commits)

| Real name | GitHub | Role | Commits | Repos | Span | Lines + / − |
|---|---|---|---:|---:|---|---:|
| Mārcis Gasūns | [@gasyoun](https://github.com/gasyoun) | lead | 4,851 | 78 | 2014-01 → 2026-11 | +43,542,707 / −2,827,501 |
| Jim Funderburk | [@funderburkjim](https://github.com/funderburkjim) | maintainer | 2,617 | 56 | 2014-01 → 2026-09 | +54,147,232 / −4,989,564 |
| drdhaval2785@gmail.com | [@drdhaval2785@gmail.com](https://github.com/drdhaval2785@gmail.com) | contributor | 2,055 | 9 | 2015-11 → 2026-11 | +0 / −0 |
| funderburkjim@gmail.com | [@funderburkjim@gmail.com](https://github.com/funderburkjim@gmail.com) | contributor | 2,006 | 5 | 2014-01 → 2026-07 | +0 / −0 |
| Dhaval Patel | [@drdhaval2785](https://github.com/drdhaval2785) | core | 1,782 | 32 | 2015-11 → 2026-11 | +26,294,662 / −5,851,693 |
| gasyoun@users.noreply.github.com | [@gasyoun@users.noreply.github.com](https://github.com/gasyoun@users.noreply.github.com) | contributor | 504 | 9 | 2015-02 → 2026-11 | +0 / −0 |
| drdhaval2785gmail.com | [@drdhaval2785gmail.com](https://github.com/drdhaval2785gmail.com) | contributor | 344 | 1 | 2026-03 → 2026-11 | +0 / −0 |
| dependabot[bot] | [@dependabot[bot]](https://github.com/dependabot[bot]) | contributor | 327 | 73 | 2026-05 → 2026-11 | +1,564 / −980 |
| GitHub Actions (bot) | [@github-actions[bot]](https://github.com/github-actions[bot]) | bot | 210 | 3 | 2026-04 → 2026-11 | +2,215,765 / −312,552 |
| gasyoun@ya.ru | [@gasyoun@ya.ru](https://github.com/gasyoun@ya.ru) | contributor | 178 | 9 | 2014-01 → 2026-11 | +0 / −0 |
| Anna Rybakova | [@AnnaRybakovaT](https://github.com/AnnaRybakovaT) | occasional | 82 | 11 | 2020-12 → 2023-06 | +67,265 / −4,309 |
| GitHub Actions (bot) | [@actions-user](https://github.com/actions-user) | bot | 46 | 4 | 2026-04 → 2026-09 | +67,888 / −39,702 |
| 49699333+dependabot[bot]@users.noreply.github.com | [@49699333+dependabot[bot]@users.noreply.github.com](https://github.com/49699333+dependabot[bot]@users.noreply.github.com) | contributor | 38 | 9 | 2026-06 → 2026-11 | +0 / −0 |
| 75209130+Andhrabharati@users.noreply.github.com | [@75209130+Andhrabharati@users.noreply.github.com](https://github.com/75209130+Andhrabharati@users.noreply.github.com) | contributor | 38 | 1 | 2021-01 → 2021-03 | +0 / −0 |
| (misconfigured git client) | [@you@example.com](https://github.com/you@example.com) | occasional | 30 | 5 | 2021-01 → 2021-09 | +11,395 / −8,887 |
| actions@github.com | [@actions@github.com](https://github.com/actions@github.com) | contributor | 25 | 1 | 2026-04 → 2026-08 | +0 / −0 |
| Nagabhushana Rao | [@Andhrabharati](https://github.com/Andhrabharati) | core | 24 | 2 | 2021-05 → 2023-04 | +1,374,787 / −226,487 |
| Scott Rhodes | [@aumsanskrit](https://github.com/aumsanskrit) | contributor | 17 | 1 | 2024-01 → 2024-01 | +0 / −0 |
| shenyileirob | [@shenyileirob](https://github.com/shenyileirob) | occasional | 8 | 1 | 2024-01 → 2025-11 | +0 / −0 |
| root@localhost.localdomain | [@root@localhost.localdomain](https://github.com/root@localhost.localdomain) | occasional | 5 | 3 | 2019-10 → 2019-10 | +3 / −3 |

## Per-repository summary

| Repo | Commits | Issues | Open | Closed | Triaged | First | Last |
|---|---:|---:|---:|---:|:---:|---|---|
| [csl-orig](https://github.com/sanskrit-lexicon/csl-orig) | 2,328 | 2816 | 31 | 2785 | ✓ | 2019-07-20 | 2026-11-15 |
| [csl-corrections](https://github.com/sanskrit-lexicon/csl-corrections) | 1,201 | 383 | 70 | 313 | ✓ | 2019-12-16 | 2026-11-18 |
| [csl-atlas](https://github.com/sanskrit-lexicon/csl-atlas) | 932 | 66 | 6 | 60 |  | 2026-05-23 | 2026-11-21 |
| [cologne-stardict](https://github.com/sanskrit-lexicon/cologne-stardict) | 896 | 48 | 3 | 45 | ✓ | 2017-04-04 | 2026-11-15 |
| [csl-apidev](https://github.com/sanskrit-lexicon/csl-apidev) | 764 | 68 | 19 | 49 | ✓ | 2018-04-17 | 2026-11-18 |
| [csl-observatory](https://github.com/sanskrit-lexicon/csl-observatory) | 724 | 60 | 19 | 41 | ✓ | 2026-05-07 | 2026-11-22 |
| [CORRECTIONS](https://github.com/sanskrit-lexicon/CORRECTIONS) | 720 | 443 | 83 | 360 |  | 2014-09-29 | 2026-11-07 |
| [MWS](https://github.com/sanskrit-lexicon/MWS) | 639 | 221 | 39 | 182 | ✓ | 2014-01-16 | 2026-11-23 |
| [csl-pywork](https://github.com/sanskrit-lexicon/csl-pywork) | 604 | 60 | 7 | 53 | ✓ | 2019-07-20 | 2026-11-18 |
| [PWG](https://github.com/sanskrit-lexicon/PWG) | 503 | 199 | 32 | 167 | ✓ | 2014-09-25 | 2026-11-08 |
| [PWK](https://github.com/sanskrit-lexicon/PWK) | 328 | 117 | 38 | 79 | ✓ | 2014-11-08 | 2026-11-07 |
| [csl-guides](https://github.com/sanskrit-lexicon/csl-guides) | 302 | 37 | 2 | 35 |  | 2026-06-13 | 2026-11-23 |
| [csl-standards](https://github.com/sanskrit-lexicon/csl-standards) | 286 | 14 | 3 | 11 |  | 2026-06-04 | 2026-11-05 |
| [COLOGNE](https://github.com/sanskrit-lexicon/COLOGNE) | 253 | 472 | 188 | 284 | ✓ | 2014-01-14 | 2026-11-07 |
| [csl-app](https://github.com/sanskrit-lexicon/csl-app) | 227 | 43 | 1 | 42 | ✓ | 2026-03-18 | 2026-11-12 |
| [hwnorm1](https://github.com/sanskrit-lexicon/hwnorm1) | 215 | 21 | 17 | 4 | ✓ | 2015-11-19 | 2026-11-07 |
| [csl-devanagari](https://github.com/sanskrit-lexicon/csl-devanagari) | 210 | 43 | 13 | 30 | ✓ | 2021-09-02 | 2026-11-15 |
| [AP](https://github.com/sanskrit-lexicon/AP) | 179 | 35 | 11 | 24 | ✓ | 2025-07-06 | 2026-10-26 |
| [BEN](https://github.com/sanskrit-lexicon/BEN) | 173 | 28 | 5 | 23 | ✓ | 2020-04-30 | 2026-10-26 |
| [LRV](https://github.com/sanskrit-lexicon/LRV) | 167 | 32 | 3 | 29 | ✓ | 2022-09-20 | 2026-10-26 |
| [VCP](https://github.com/sanskrit-lexicon/VCP) | 162 | 32 | 19 | 13 | ✓ | 2014-01-22 | 2026-10-27 |
| [sanskrit-util](https://github.com/sanskrit-lexicon/sanskrit-util) | 139 | 14 | 1 | 13 |  | 2026-06-15 | 2026-11-22 |
| [alternateheadwords](https://github.com/sanskrit-lexicon/alternateheadwords) | 130 | 25 | 18 | 7 | ✓ | 2016-10-01 | 2026-10-26 |
| [GRA](https://github.com/sanskrit-lexicon/GRA) | 126 | 40 | 10 | 30 | ✓ | 2015-01-04 | 2026-11-07 |
| [MWinflect](https://github.com/sanskrit-lexicon/MWinflect) | 124 | 50 | 48 | 2 | ✓ | 2018-10-16 | 2026-11-07 |
| [MD](https://github.com/sanskrit-lexicon/MD) | 117 | 16 | 6 | 10 | ✓ | 2020-04-17 | 2026-10-26 |
| [csl-json](https://github.com/sanskrit-lexicon/csl-json) | 114 | 9 | 0 | 9 |  | 2021-08-16 | 2026-10-27 |
| [WIL](https://github.com/sanskrit-lexicon/WIL) | 107 | 19 | 13 | 6 | ✓ | 2014-12-28 | 2026-10-26 |
| [PUI](https://github.com/sanskrit-lexicon/PUI) | 99 | 4 | 2 | 2 | ✓ | 2026-04-05 | 2026-10-27 |
| [csl-inflect](https://github.com/sanskrit-lexicon/csl-inflect) | 95 | 21 | 13 | 8 | ✓ | 2019-11-27 | 2026-11-11 |
| [SKD](https://github.com/sanskrit-lexicon/SKD) | 87 | 20 | 11 | 9 | ✓ | 2014-07-19 | 2026-10-27 |
| [AP90](https://github.com/sanskrit-lexicon/AP90) | 86 | 32 | 14 | 18 | ✓ | 2020-03-14 | 2026-11-07 |
| [csl-ldev](https://github.com/sanskrit-lexicon/csl-ldev) | 84 | 9 | 7 | 2 | ✓ | 2021-10-05 | 2026-10-27 |
| [ApteES](https://github.com/sanskrit-lexicon/ApteES) | 76 | 17 | 2 | 15 | ✓ | 2014-07-15 | 2026-10-26 |
| [sanskrit-lexicon.github.io](https://github.com/sanskrit-lexicon/sanskrit-lexicon.github.io) | 74 | 0 | 0 | 0 |  | 2015-11-24 | 2026-11-21 |
| [BHS](https://github.com/sanskrit-lexicon/BHS) | 74 | 8 | 4 | 4 | ✓ | 2016-01-02 | 2026-10-26 |
| [BOP](https://github.com/sanskrit-lexicon/BOP) | 73 | 9 | 1 | 8 | ✓ | 2022-05-02 | 2026-11-07 |
| [csl-newsletter](https://github.com/sanskrit-lexicon/csl-newsletter) | 72 | 4 | 2 | 2 | ✓ | 2021-09-13 | 2026-10-26 |
| [csl-lnum](https://github.com/sanskrit-lexicon/csl-lnum) | 72 | 4 | 1 | 3 | ✓ | 2021-10-02 | 2026-10-27 |
| [mw-dev](https://github.com/sanskrit-lexicon/mw-dev) | 70 | 23 | 17 | 6 | ✓ | 2023-01-19 | 2026-11-07 |
| [SCH](https://github.com/sanskrit-lexicon/SCH) | 69 | 12 | 4 | 8 | ✓ | 2014-01-15 | 2026-11-07 |
| [CAE](https://github.com/sanskrit-lexicon/CAE) | 64 | 4 | 3 | 1 | ✓ | 2020-04-12 | 2026-10-26 |
| [csl-doc](https://github.com/sanskrit-lexicon/csl-doc) | 62 | 6 | 2 | 4 | ✓ | 2018-10-23 | 2026-10-26 |
| [hwnorm2](https://github.com/sanskrit-lexicon/hwnorm2) | 61 | 5 | 4 | 1 | ✓ | 2020-02-01 | 2026-10-27 |
| [BUR](https://github.com/sanskrit-lexicon/BUR) | 61 | 6 | 1 | 5 | ✓ | 2020-04-09 | 2026-10-26 |
| [csl-pyutil](https://github.com/sanskrit-lexicon/csl-pyutil) | 56 | 6 | 1 | 5 |  | 2026-07-14 | 2026-11-21 |
| [csl-santam](https://github.com/sanskrit-lexicon/csl-santam) | 54 | 4 | 0 | 4 |  | 2015-06-02 | 2026-10-26 |
| [SHS](https://github.com/sanskrit-lexicon/SHS) | 54 | 4 | 3 | 1 | ✓ | 2025-12-22 | 2026-10-27 |
| [BOR](https://github.com/sanskrit-lexicon/BOR) | 48 | 4 | 3 | 1 | ✓ | 2021-09-14 | 2026-10-26 |
| [VEI](https://github.com/sanskrit-lexicon/VEI) | 47 | 2 | 1 | 1 | ✓ | 2016-01-02 | 2026-10-27 |
| [KRM](https://github.com/sanskrit-lexicon/KRM) | 47 | 4 | 3 | 1 | ✓ | 2020-03-31 | 2026-10-26 |
| [INM](https://github.com/sanskrit-lexicon/INM) | 47 | 11 | 3 | 8 | ✓ | 2021-12-03 | 2026-10-26 |
| [PD](https://github.com/sanskrit-lexicon/PD) | 46 | 1 | 1 | 0 |  | 2026-07-21 | 2026-11-11 |
| [FRI](https://github.com/sanskrit-lexicon/FRI) | 43 | 11 | 3 | 8 | ✓ | 2024-01-26 | 2026-10-26 |
| [CCS](https://github.com/sanskrit-lexicon/CCS) | 42 | 3 | 2 | 1 | ✓ | 2020-04-15 | 2026-10-26 |
| [STC](https://github.com/sanskrit-lexicon/STC) | 42 | 3 | 2 | 1 | ✓ | 2020-04-19 | 2026-10-27 |
| [literarysource](https://github.com/sanskrit-lexicon/literarysource) | 42 | 3 | 3 | 0 | ✓ | 2022-02-12 | 2026-10-26 |
| [MCI](https://github.com/sanskrit-lexicon/MCI) | 40 | 2 | 1 | 1 | ✓ | 2026-05-15 | 2026-10-26 |
| [temp_corrections_ap90](https://github.com/sanskrit-lexicon/temp_corrections_ap90) | 40 | 2 | 1 | 1 |  | 2021-01-13 | 2026-10-27 |
| [DCS](https://github.com/sanskrit-lexicon/DCS) | 38 | 4 | 4 | 0 | ✓ | 2014-01-17 | 2026-11-04 |
| [ACC](https://github.com/sanskrit-lexicon/ACC) | 38 | 19 | 9 | 10 | ✓ | 2017-05-28 | 2026-11-04 |
| [MW72](https://github.com/sanskrit-lexicon/MW72) | 36 | 6 | 1 | 5 | ✓ | 2014-08-24 | 2026-10-26 |
| [AMAR](https://github.com/sanskrit-lexicon/AMAR) | 36 | 3 | 2 | 1 | ✓ | 2024-01-30 | 2026-10-26 |
| [csl-lslink](https://github.com/sanskrit-lexicon/csl-lslink) | 34 | 2 | 2 | 0 | ✓ | 2026-03-31 | 2026-10-26 |
| [rvlinks](https://github.com/sanskrit-lexicon/rvlinks) | 30 | 2 | 1 | 1 | ✓ | 2018-08-29 | 2026-10-27 |
| [avlinks](https://github.com/sanskrit-lexicon/avlinks) | 29 | 1 | 1 | 0 |  | 2021-04-08 | 2026-10-26 |
| [csl-kale](https://github.com/sanskrit-lexicon/csl-kale) | 26 | 3 | 2 | 1 | ✓ | 2019-11-09 | 2026-11-11 |
| [KNA](https://github.com/sanskrit-lexicon/KNA) | 26 | 1 | 1 | 0 | ✓ | 2026-02-21 | 2026-11-08 |
| [Wil-YAT](https://github.com/sanskrit-lexicon/Wil-YAT) | 24 | 6 | 0 | 6 | ✓ | 2015-03-10 | 2026-10-26 |
| [csl-westergaard](https://github.com/sanskrit-lexicon/csl-westergaard) | 24 | 2 | 2 | 0 | ✓ | 2019-11-08 | 2026-11-11 |
| [KOW](https://github.com/sanskrit-lexicon/KOW) | 24 | 1 | 1 | 0 | ✓ | 2026-02-21 | 2026-10-26 |
| [GreekInSanskrit](https://github.com/sanskrit-lexicon/GreekInSanskrit) | 22 | 44 | 1 | 43 | ✓ | 2015-04-15 | 2026-10-27 |
| [csl-whitroot](https://github.com/sanskrit-lexicon/csl-whitroot) | 21 | 1 | 1 | 0 |  | 2019-11-08 | 2026-11-11 |
| [cologne-skills](https://github.com/sanskrit-lexicon/cologne-skills) | 19 | 0 | 0 | 0 |  | 2026-06-16 | 2026-10-26 |
| [csl-usage](https://github.com/sanskrit-lexicon/csl-usage) | 19 | 0 | 0 | 0 |  | 2026-11-09 | 2026-11-11 |
| [ArabicInSanskrit](https://github.com/sanskrit-lexicon/ArabicInSanskrit) | 18 | 16 | 0 | 16 | ✓ | 2015-01-18 | 2026-10-26 |
| [temp_corrections_mw](https://github.com/sanskrit-lexicon/temp_corrections_mw) | 18 | 2 | 1 | 1 |  | 2021-04-11 | 2026-10-27 |
| [csl-sqlite](https://github.com/sanskrit-lexicon/csl-sqlite) | 17 | 1 | 1 | 0 | ✓ | 2026-04-08 | 2026-11-12 |
| [IEG](https://github.com/sanskrit-lexicon/IEG) | 17 | 2 | 1 | 1 | ✓ | 2026-06-24 | 2026-10-26 |
| [sanskrit-fonts](https://github.com/sanskrit-lexicon/sanskrit-fonts) | 15 | 0 | 0 | 0 |  | 2018-09-05 | 2026-10-27 |
| [cologne-hugo](https://github.com/sanskrit-lexicon/cologne-hugo) | 13 | 0 | 0 | 0 |  | 2021-01-20 | 2026-10-26 |
| [.github](https://github.com/sanskrit-lexicon/.github) | 5 | 0 | 0 | 0 |  | 2026-10-18 | 2026-11-05 |
| [pwg-ru-lod](https://github.com/sanskrit-lexicon/pwg-ru-lod) | 4 | 0 | 0 | 0 |  | 2026-10-11 | 2026-10-27 |
| [csl-homepage](https://github.com/sanskrit-lexicon/csl-homepage) | 0 | 0 | 0 | 0 |  | - | - |
| [csl-websanlexicon](https://github.com/sanskrit-lexicon/csl-websanlexicon) | 0 | 0 | 0 | 0 |  | - | - |

---
*Generated by `scripts/render_reports.py`. Data: `data/snapshots/2026-11-23/`. License: data CC BY-SA 4.0.*
