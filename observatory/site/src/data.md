---
title: Data downloads
toc: true
---

# Data downloads

Every chart on this site is backed by a stable, citable, downloadable dataset. Use these in your own work; cite the snapshot date.

## Files

| File | Rows | Description | Download |
|---|---|---|---|
| repos.csv | 77 | One row per repository in the org | [📥](data/repos.csv) |
| issues.csv | 5,280 | All issues + PRs (slimmed schema) | [📥](data/issues.csv) |
| commits.csv | 9,176 | All commits since 2014 | [📥](data/commits.csv) |
| contributors.csv | 207 | (login, repo) pairs with commit counts | [📥](data/contributors.csv) |
| timeseries_monthly.csv | 1,340 | (year-month, repo) aggregates | [📥](data/timeseries_monthly.csv) |
| timeseries_annual.csv | 383 | (year, repo) aggregates | [📥](data/timeseries_annual.csv) |
| issue_typology_annual.csv | 135 | (year, type-label, count) | [📥](data/issue_typology_annual.csv) |
| people_summary.csv | 17 | Curated contributors index | [📥](data/people_summary.csv) |

*Numbers are from snapshot **2026-05**. Refreshed manually + monthly fallback.*

## Schemas

### timeseries_monthly.csv
```
year_month, repo, issues_opened, issues_closed, prs_opened, prs_closed, commits, unique_authors
```

### issue_typology_annual.csv
```
year, type_label, count
```
Where `type_label` is one of the 9 dictionary type labels (`link-target`, `link-splitting`, `markup`, `text-correction`, `content-enhancement`, `encoding`, `scan-quality`, `bug`, `question`) or 9 tooling type labels (`bug`, `feature`, `enhancement`, `performance`, `tech-debt`, `security`, `documentation`, `infrastructure`, `question`).

### issues.csv
```
repo, number, title, state, created_at, closed_at, user, labels, milestone, comments, kind
```
`kind` is `issue` or `PR`. `labels` is `|`-separated.

## Citation

If you use these data in published work, please cite:

> Gasūns, M. et al. (2026). *CSL Observatory: 12 years of Cologne Digital Sanskrit Lexicon* [Data set]. Zenodo. DOI: pending mint.

Plus the snapshot date (e.g. "snapshot 2026-05") so your numbers are reproducible.

## Reproducibility

All raw snapshots and the transformer code are in [csl-observatory/observatory/](https://github.com/sanskrit-lexicon/csl-observatory/tree/main/observatory).

To regenerate locally:
```sh
cd observatory
python fetch.py             # 12-year backfill, ~13 minutes
python transform.py         # build CSVs from snapshots
python build_people.py      # refresh people.yaml
```

[← back to overview](/)
