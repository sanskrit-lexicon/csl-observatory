# CDSL ecosystem dashboard

**Snapshot date**: 2026-05-25 · **Fetched**: 2026-05-25T10:21:22.546451Z

## Headline numbers

| Metric | Value |
|---|---|
| Repositories in `sanskrit-lexicon` | 78 |
| Repositories with issues enabled | 78 |
| Total issues (incl. closed) | 5,256 |
| Total pull requests | 42 |
| Total commits in default branches | 5,077 |
| Distinct contributors (commit authors + issue authors) | 50 |
| Triaged repositories (taxonomy applied) | 52 |

## Issue type distribution across all triaged repos

| Type | Count | % of typed issues |
|---|---:|---:|
| `link-target` | 96 | 2.5 % |
| `link-splitting` | 9 | 0.2 % |
| `markup` | 251 | 6.4 % |
| `text-correction` | 2864 | 73.2 % |
| `content-enhancement` | 145 | 3.7 % |
| `encoding` | 50 | 1.3 % |
| `scan-quality` | 39 | 1.0 % |
| `bug` | 254 | 6.5 % |
| `question` | 206 | 5.3 % |

```mermaid
pie title Issue type distribution
    "link-target" : 96
    "link-splitting" : 9
    "markup" : 251
    "text-correction" : 2864
    "content-enhancement" : 145
    "encoding" : 50
    "scan-quality" : 39
    "bug" : 254
    "question" : 206
```

## Type × repository heatmap

| Type | ACC | AP | AP90 | ApteES | BEN | BHS | BOP | BOR | BUR | CAE | CCS | COLOGNE | FRI | GRA | GreekInSanskrit | INM | KRM | LRV | MCI | MD | MW72 | MWS | MWinflect | PWG | PWK | SCH | SHS | SKD | STC | VCP | VEI | WIL | Wil-YAT | alternateheadwords | cologne-stardict | csl-apidev | csl-app | csl-corrections | csl-devanagari | csl-doc | csl-inflect | csl-ldev | csl-lnum | csl-observatory | csl-orig | csl-pywork | csl-westergaard | hwnorm1 | hwnorm2 | literarysource | mw-dev | rvlinks | total |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `link-target` | 0 | 2 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 11 | 0 | 72 | 7 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 2 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | **96** |
| `link-splitting` | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 | 0 | 8 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | **9** |
| `markup` | 1 | 18 | 10 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 0 | 3 | 8 | 0 | 1 | 1 | 1 | 1 | 3 | 1 | 52 | 0 | 33 | 57 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 0 | 0 | 0 | 0 | 12 | 0 | 0 | 0 | 0 | 0 | 0 | 33 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | **251** |
| `text-correction` | 0 | 2 | 5 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 6 | 0 | 0 | 0 | 0 | 0 | 4 | 0 | 48 | 0 | 10 | 9 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 124 | 0 | 0 | 0 | 0 | 0 | 0 | 2656 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | **2864** |
| `content-enhancement` | 0 | 2 | 5 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 5 | 13 | 0 | 0 | 0 | 0 | 0 | 5 | 0 | 26 | 0 | 35 | 22 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 7 | 0 | 0 | 0 | 0 | 0 | 0 | 25 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | **145** |
| `encoding` | 0 | 2 | 4 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 | 3 | 0 | 0 | 0 | 0 | 0 | 1 | 0 | 10 | 0 | 11 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 13 | 0 | 0 | 0 | 0 | 0 | 0 | 4 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | **50** |
| `scan-quality` | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 2 | 2 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 3 | 0 | 5 | 3 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 23 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | **39** |
| `bug` | 0 | 2 | 1 | 0 | 1 | 0 | 2 | 0 | 1 | 0 | 0 | 40 | 0 | 3 | 3 | 0 | 0 | 6 | 0 | 1 | 1 | 19 | 0 | 10 | 4 | 0 | 0 | 2 | 0 | 4 | 0 | 0 | 0 | 1 | 13 | 11 | 3 | 38 | 9 | 3 | 0 | 4 | 0 | 0 | 54 | 12 | 0 | 4 | 0 | 0 | 1 | 1 | **254** |
| `question` | 0 | 0 | 2 | 2 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 46 | 0 | 1 | 3 | 0 | 0 | 3 | 1 | 0 | 1 | 20 | 8 | 14 | 9 | 0 | 0 | 2 | 0 | 3 | 0 | 0 | 0 | 5 | 1 | 4 | 1 | 43 | 1 | 0 | 0 | 1 | 0 | 0 | 29 | 1 | 0 | 2 | 0 | 0 | 2 | 0 | **206** |

## Activity by year

| Year | Commits | Issues opened | Issues closed |
|---|---:|---:|---:|
| 2014 | 75 | 190 | 65 |
| 2015 | 123 | 270 | 170 |
| 2016 | 241 | 175 | 140 |
| 2017 | 169 | 268 | 130 |
| 2018 | 146 | 98 | 30 |
| 2019 | 309 | 246 | 144 |
| 2020 | 327 | 470 | 485 |
| 2021 | 666 | 637 | 484 |
| 2022 | 378 | 451 | 382 |
| 2023 | 336 | 534 | 542 |
| 2024 | 383 | 372 | 381 |
| 2025 | 612 | 1169 | 213 |
| 2026 | 1312 | 334 | 1156 |

## Top contributors (by commits)

| Real name | GitHub | Role | Commits | Repos | Span | Lines + / − |
|---|---|---|---:|---:|---|---:|
| Jim Funderburk | [@funderburkjim](https://github.com/funderburkjim) | maintainer | 2,912 | 53 | 2014-01 → 2026-05 | +53,946,039 / −5,165,609 |
| Dhaval Patel | [@drdhaval2785](https://github.com/drdhaval2785) | core | 1,354 | 29 | 2015-11 → 2026-05 | +18,753,392 / −4,286,281 |
| Mārcis Gasūns | [@gasyoun](https://github.com/gasyoun) | lead | 602 | 67 | 2014-01 → 2026-05 | +3,537,694 / −43,389 |
| Anna Rybakova | [@AnnaRybakovaT](https://github.com/AnnaRybakovaT) | occasional | 70 | 10 | 2020-12 → 2023-06 | +71,367 / −6,300 |
| GitHub Actions (bot) | [@github-actions[bot]](https://github.com/github-actions[bot]) | bot | 57 | 2 | 2026-04 → 2026-05 | +365,052 / −69,273 |
| (misconfigured git client) | [@you@example.com](https://github.com/you@example.com) | occasional | 30 | 5 | 2021-01 → 2021-09 | +11,395 / −8,887 |
| GitHub Actions (bot) | [@actions-user](https://github.com/actions-user) | bot | 26 | 3 | 2026-04 → 2026-05 | +21,913 / −11,756 |
| Nagabhushana Rao | [@Andhrabharati](https://github.com/Andhrabharati) | core | 9 | 2 | 2021-03 → 2022-12 | +293,403 / −25,014 |
| DmitriSKT | [@DmitriSKT](https://github.com/DmitriSKT) | occasional | 3 | 1 | 2017-05 → 2017-11 | +33 / −2 |
| root@localhost.localdomain | [@root@localhost.localdomain](https://github.com/root@localhost.localdomain) | occasional | 3 | 2 | 2019-10 → 2019-10 | +3 / −3 |
| Automated updater (bot) | [@cfr-auto-updater@example.com](https://github.com/cfr-auto-updater@example.com) | bot | 3 | 1 | 2025-04 → 2025-04 | +1,457 / −0 |
| Haqob | [@Haqob](https://github.com/Haqob) | occasional | 2 | 1 | 2020-08 → 2020-09 | +2,019 / −1,593 |
| dpatel3@dialog7.rrz.uni-koeln.de | [@dpatel3@dialog7.rrz.uni-koeln.de](https://github.com/dpatel3@dialog7.rrz.uni-koeln.de) | contributor | 2 | 1 | 2023-12 → 2024-01 | +121 / −0 |
| Thomas Malten | [@maltenth](https://github.com/maltenth) | core | 1 | 1 | 2021-09 → 2021-09 | +860 / −0 |
| usha.sanka@gmial.com | [@usha.sanka@gmial.com](https://github.com/usha.sanka@gmial.com) | contributor | 1 | 1 | 2021-01 → 2021-01 | +1 / −1 |
| YevgenJohn | [@YevgenJohn](https://github.com/YevgenJohn) | occasional | 1 | 1 | 2019-10 → 2019-10 | +1 / −1 |
| sanskritisampada | [@sanskritisampada](https://github.com/sanskritisampada) | occasional | 1 | 1 | 2021-01 → 2021-01 | +1 / −0 |
| IrinaKonstant | [@IrinaKonstant](https://github.com/IrinaKonstant) | contributor | 0 | 0 | - → - | +0 / −0 |
| grigoriyt1 | [@grigoriyt1](https://github.com/grigoriyt1) | contributor | 0 | 0 | - → - | +0 / −0 |
| angalinde | [@angalinde](https://github.com/angalinde) | contributor | 0 | 0 | - → - | +0 / −0 |

## Per-repository summary

| Repo | Commits | Issues | Open | Closed | Triaged | First | Last |
|---|---:|---:|---:|---:|:---:|---|---|
| [csl-corrections](https://github.com/sanskrit-lexicon/csl-corrections) | 810 | 235 | 25 | 210 | ✓ | 2019-12-16 | 2026-05-25 |
| [csl-apidev](https://github.com/sanskrit-lexicon/csl-apidev) | 520 | 45 | 22 | 23 | ✓ | 2018-04-17 | 2026-05-16 |
| [csl-pywork](https://github.com/sanskrit-lexicon/csl-pywork) | 476 | 46 | 7 | 39 | ✓ | 2019-07-20 | 2026-05-21 |
| [PWG](https://github.com/sanskrit-lexicon/PWG) | 385 | 173 | 65 | 108 | ✓ | 2014-09-25 | 2026-05-24 |
| [CORRECTIONS](https://github.com/sanskrit-lexicon/CORRECTIONS) | 300 | 441 | 89 | 352 |  | 2016-04-24 | 2026-05-16 |
| [PWK](https://github.com/sanskrit-lexicon/PWK) | 267 | 112 | 41 | 71 | ✓ | 2014-11-08 | 2026-05-25 |
| [COLOGNE](https://github.com/sanskrit-lexicon/COLOGNE) | 211 | 455 | 209 | 246 | ✓ | 2014-01-14 | 2026-05-15 |
| [MWS](https://github.com/sanskrit-lexicon/MWS) | 200 | 191 | 34 | 157 | ✓ | 2021-03-04 | 2026-05-16 |
| [csl-app](https://github.com/sanskrit-lexicon/csl-app) | 178 | 39 | 3 | 36 | ✓ | 2026-03-18 | 2026-05-15 |
| [AP](https://github.com/sanskrit-lexicon/AP) | 133 | 29 | 13 | 16 | ✓ | 2025-07-06 | 2026-05-16 |
| [csl-observatory](https://github.com/sanskrit-lexicon/csl-observatory) | 125 | 2 | 2 | 0 | ✓ | 2026-05-07 | 2026-05-18 |
| [alternateheadwords](https://github.com/sanskrit-lexicon/alternateheadwords) | 117 | 25 | 19 | 6 | ✓ | 2016-10-01 | 2026-05-15 |
| [VCP](https://github.com/sanskrit-lexicon/VCP) | 116 | 29 | 20 | 9 | ✓ | 2014-01-22 | 2026-05-16 |
| [MWinflect](https://github.com/sanskrit-lexicon/MWinflect) | 88 | 48 | 48 | 0 | ✓ | 2018-10-16 | 2026-05-15 |
| [WIL](https://github.com/sanskrit-lexicon/WIL) | 76 | 17 | 14 | 3 | ✓ | 2014-12-28 | 2026-05-18 |
| [MD](https://github.com/sanskrit-lexicon/MD) | 76 | 14 | 6 | 8 | ✓ | 2020-04-17 | 2026-05-16 |
| [csl-inflect](https://github.com/sanskrit-lexicon/csl-inflect) | 67 | 15 | 12 | 3 | ✓ | 2019-11-27 | 2026-05-15 |
| [SKD](https://github.com/sanskrit-lexicon/SKD) | 58 | 19 | 13 | 6 | ✓ | 2014-07-19 | 2026-05-16 |
| [GRA](https://github.com/sanskrit-lexicon/GRA) | 58 | 37 | 10 | 27 | ✓ | 2015-01-04 | 2026-05-16 |
| [AP90](https://github.com/sanskrit-lexicon/AP90) | 53 | 29 | 16 | 13 | ✓ | 2020-03-14 | 2026-05-17 |
| [hwnorm2](https://github.com/sanskrit-lexicon/hwnorm2) | 43 | 5 | 4 | 1 | ✓ | 2020-02-01 | 2026-05-24 |
| [csl-newsletter](https://github.com/sanskrit-lexicon/csl-newsletter) | 43 | 2 | 2 | 0 |  | 2021-09-13 | 2026-05-15 |
| [csl-doc](https://github.com/sanskrit-lexicon/csl-doc) | 40 | 6 | 2 | 4 | ✓ | 2018-10-23 | 2026-05-15 |
| [sanskrit-lexicon.github.io](https://github.com/sanskrit-lexicon/sanskrit-lexicon.github.io) | 39 | 0 | 0 | 0 |  | 2015-11-24 | 2026-05-15 |
| [BEN](https://github.com/sanskrit-lexicon/BEN) | 36 | 10 | 4 | 6 | ✓ | 2020-04-30 | 2026-05-16 |
| [BHS](https://github.com/sanskrit-lexicon/BHS) | 33 | 6 | 4 | 2 | ✓ | 2016-01-02 | 2026-05-16 |
| [literarysource](https://github.com/sanskrit-lexicon/literarysource) | 31 | 3 | 3 | 0 | ✓ | 2022-02-12 | 2026-05-15 |
| [SCH](https://github.com/sanskrit-lexicon/SCH) | 30 | 11 | 4 | 7 | ✓ | 2014-01-15 | 2026-05-16 |
| [BUR](https://github.com/sanskrit-lexicon/BUR) | 30 | 6 | 2 | 4 | ✓ | 2020-04-09 | 2026-05-16 |
| [temp_corrections_ap90](https://github.com/sanskrit-lexicon/temp_corrections_ap90) | 30 | 2 | 1 | 1 |  | 2021-01-13 | 2026-05-15 |
| [ApteES](https://github.com/sanskrit-lexicon/ApteES) | 29 | 15 | 3 | 12 | ✓ | 2014-07-15 | 2026-05-16 |
| [temp_corrections_acc](https://github.com/sanskrit-lexicon/temp_corrections_acc) | 29 | 0 | 0 | 0 |  | 2021-01-23 | 2026-05-15 |
| [CAE](https://github.com/sanskrit-lexicon/CAE) | 28 | 3 | 3 | 0 | ✓ | 2020-04-12 | 2026-05-16 |
| [BOP](https://github.com/sanskrit-lexicon/BOP) | 26 | 8 | 2 | 6 | ✓ | 2022-05-02 | 2026-05-16 |
| [temp_corrections_ae](https://github.com/sanskrit-lexicon/temp_corrections_ae) | 20 | 0 | 0 | 0 |  | 2021-01-10 | 2026-05-15 |
| [rvlinks](https://github.com/sanskrit-lexicon/rvlinks) | 19 | 2 | 1 | 1 | ✓ | 2018-08-29 | 2026-05-15 |
| [csl-lslink](https://github.com/sanskrit-lexicon/csl-lslink) | 18 | 1 | 1 | 0 |  | 2026-03-31 | 2026-05-17 |
| [csl-santam](https://github.com/sanskrit-lexicon/csl-santam) | 17 | 2 | 0 | 2 |  | 2015-06-02 | 2026-05-15 |
| [VEI](https://github.com/sanskrit-lexicon/VEI) | 14 | 2 | 2 | 0 | ✓ | 2016-01-02 | 2026-05-16 |
| [BOR](https://github.com/sanskrit-lexicon/BOR) | 14 | 4 | 4 | 0 | ✓ | 2021-09-14 | 2026-05-16 |
| [avlinks](https://github.com/sanskrit-lexicon/avlinks) | 13 | 1 | 1 | 0 |  | 2021-04-08 | 2026-05-15 |
| [DCS](https://github.com/sanskrit-lexicon/DCS) | 12 | 4 | 4 | 0 |  | 2014-01-17 | 2026-05-16 |
| [KRM](https://github.com/sanskrit-lexicon/KRM) | 12 | 4 | 4 | 0 | ✓ | 2020-03-31 | 2026-05-16 |
| [csl-kale](https://github.com/sanskrit-lexicon/csl-kale) | 11 | 2 | 1 | 1 |  | 2019-11-09 | 2026-05-15 |
| [CCS](https://github.com/sanskrit-lexicon/CCS) | 11 | 3 | 3 | 0 | ✓ | 2020-04-15 | 2026-05-16 |
| [FRI](https://github.com/sanskrit-lexicon/FRI) | 11 | 11 | 4 | 7 | ✓ | 2024-01-26 | 2026-05-16 |
| [STC](https://github.com/sanskrit-lexicon/STC) | 10 | 3 | 3 | 0 | ✓ | 2020-04-19 | 2026-05-16 |
| [ACC](https://github.com/sanskrit-lexicon/ACC) | 9 | 19 | 11 | 8 | ✓ | 2017-05-28 | 2026-05-16 |
| [csl-westergaard](https://github.com/sanskrit-lexicon/csl-westergaard) | 9 | 1 | 1 | 0 | ✓ | 2019-11-08 | 2026-05-15 |
| [INM](https://github.com/sanskrit-lexicon/INM) | 9 | 10 | 3 | 7 | ✓ | 2021-12-03 | 2026-05-16 |
| [MCI](https://github.com/sanskrit-lexicon/MCI) | 8 | 2 | 2 | 0 | ✓ | 2026-05-15 | 2026-05-16 |
| [GreekInSanskrit](https://github.com/sanskrit-lexicon/GreekInSanskrit) | 8 | 44 | 2 | 42 | ✓ | 2015-04-15 | 2026-05-15 |
| [temp_corrections_mw](https://github.com/sanskrit-lexicon/temp_corrections_mw) | 8 | 2 | 1 | 1 |  | 2021-04-11 | 2026-05-15 |
| [csl-atlas](https://github.com/sanskrit-lexicon/csl-atlas) | 8 | 0 | 0 | 0 |  | 2026-05-23 | 2026-05-24 |
| [Wil-YAT](https://github.com/sanskrit-lexicon/Wil-YAT) | 7 | 6 | 1 | 5 | ✓ | 2015-03-10 | 2026-05-15 |
| [AMAR](https://github.com/sanskrit-lexicon/AMAR) | 7 | 1 | 1 | 0 |  | 2024-01-30 | 2026-05-16 |
| [MW72](https://github.com/sanskrit-lexicon/MW72) | 6 | 5 | 1 | 4 | ✓ | 2014-08-24 | 2026-05-15 |
| [csl-whitroot](https://github.com/sanskrit-lexicon/csl-whitroot) | 6 | 0 | 0 | 0 |  | 2019-11-08 | 2026-05-15 |
| [test_cologne_push](https://github.com/sanskrit-lexicon/test_cologne_push) | 5 | 0 | 0 | 0 |  | 2023-11-09 | 2026-05-15 |
| [SHS](https://github.com/sanskrit-lexicon/SHS) | 5 | 2 | 2 | 0 | ✓ | 2025-12-22 | 2026-05-23 |
| [ArabicInSanskrit](https://github.com/sanskrit-lexicon/ArabicInSanskrit) | 4 | 16 | 0 | 16 |  | 2015-01-18 | 2026-05-15 |
| [sanskrit-fonts](https://github.com/sanskrit-lexicon/sanskrit-fonts) | 3 | 0 | 0 | 0 |  | 2018-09-05 | 2026-05-15 |
| [KNA](https://github.com/sanskrit-lexicon/KNA) | 3 | 1 | 1 | 0 |  | 2026-02-21 | 2026-05-16 |
| [KOW](https://github.com/sanskrit-lexicon/KOW) | 3 | 1 | 1 | 0 |  | 2026-02-21 | 2026-05-16 |
| [csl-sqlite](https://github.com/sanskrit-lexicon/csl-sqlite) | 3 | 1 | 1 | 0 |  | 2026-04-08 | 2026-05-15 |
| [cologne-hugo](https://github.com/sanskrit-lexicon/cologne-hugo) | 2 | 0 | 0 | 0 |  | 2021-01-20 | 2026-05-15 |
| [santamlegacy](https://github.com/sanskrit-lexicon/santamlegacy) | 1 | 0 | 0 | 0 |  | 2026-05-15 | 2026-05-15 |
| [hwnorm1](https://github.com/sanskrit-lexicon/hwnorm1) | 0 | 20 | 17 | 3 | ✓ | - | - |
| [cologne-stardict](https://github.com/sanskrit-lexicon/cologne-stardict) | 0 | 48 | 3 | 45 | ✓ | - | - |
| [csl-homepage](https://github.com/sanskrit-lexicon/csl-homepage) | 0 | 0 | 0 | 0 |  | - | - |
| [csl-websanlexicon](https://github.com/sanskrit-lexicon/csl-websanlexicon) | 0 | 0 | 0 | 0 |  | - | - |
| [csl-orig](https://github.com/sanskrit-lexicon/csl-orig) | 0 | 2801 | 68 | 2733 | ✓ | - | - |
| [csl-json](https://github.com/sanskrit-lexicon/csl-json) | 0 | 9 | 0 | 9 |  | - | - |
| [csl-devanagari](https://github.com/sanskrit-lexicon/csl-devanagari) | 0 | 43 | 17 | 26 | ✓ | - | - |
| [csl-lnum](https://github.com/sanskrit-lexicon/csl-lnum) | 0 | 3 | 1 | 2 | ✓ | - | - |
| [csl-ldev](https://github.com/sanskrit-lexicon/csl-ldev) | 0 | 9 | 8 | 1 | ✓ | - | - |
| [LRV](https://github.com/sanskrit-lexicon/LRV) | 0 | 30 | 3 | 27 | ✓ | - | - |
| [mw-dev](https://github.com/sanskrit-lexicon/mw-dev) | 0 | 23 | 17 | 6 | ✓ | - | - |

---
*Generated by `scripts/render_reports.py`. Data: `data/snapshots/2026-05-25/`. License: data CC BY-SA 4.0.*
