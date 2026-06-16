---
title: Data downloads
toc: true
---

# Data downloads

Every chart on this site is backed by a stable, citable, downloadable dataset. Use these in your own work; cite the snapshot date.

## Files

```js
// Row counts are read from the pipeline's own manifest so they never drift from the data.
const manifest = await FileAttachment("data/manifest.json").json();
const peopleRows = (await FileAttachment("data/people_summary.csv").csv()).length;
const rowCount = (name) => name === "people_summary.csv" ? peopleRows : manifest.files[name];
const downloads = [
  ["repos.csv", "One row per repository in the org"],
  ["issues.csv", "All issues + PRs (slimmed schema)"],
  ["commits.csv", "All commits since 2014"],
  ["contributors.csv", "(login, repo) pairs with commit counts"],
  ["timeseries_monthly.csv", "(year-month, repo) aggregates"],
  ["timeseries_annual.csv", "(year, repo) aggregates"],
  ["issue_typology_annual.csv", "(year, type-label, count)"],
  ["people_summary.csv", "Curated contributors index"]
];
```

```js
display(html`<table>
  <thead>
    <tr><th>File</th><th>Rows</th><th>Description</th><th>Download</th></tr>
  </thead>
  <tbody>
    ${await Promise.all(downloads.map(async ([name, description]) => html`<tr>
      <td><code>${name}</code></td>
      <td>${(rowCount(name) ?? 0).toLocaleString()}</td>
      <td>${description}</td>
      <td><a href=${await FileAttachment(`data/${name}`).url()}>download</a></td>
    </tr>`))}
  </tbody>
</table>`);
```

*Numbers are from snapshot **${manifest.snapshot_date}**. Refreshed monthly from the GitHub API.*

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

> Gasūns, M. et al. (2026). *CSL Observatory: 13 years of Cologne Digital Sanskrit Lexicon* [Data set]. Zenodo. DOI: pending mint.

Plus the snapshot date (e.g. "snapshot 2026-06") so your numbers are reproducible.

## Reproducibility

All raw snapshots and the transformer code are in [csl-observatory/observatory/](https://github.com/sanskrit-lexicon/csl-observatory/tree/main/observatory).

To regenerate locally:
```sh
cd observatory
python fetch.py             # 13-year backfill, ~13 minutes
python transform.py         # build CSVs from snapshots
python build_people.py      # refresh people.yaml
```

[← back to overview](/)
