---
title: CSL Observatory — overview
toc: false
---

# CSL Observatory

12 years of Cologne Digital Sanskrit Lexicon, in numbers and pictures.

```js
const annual = await FileAttachment("data/timeseries_annual.csv").csv({typed: true});
const repos = await FileAttachment("data/repos.csv").csv({typed: true});
const typology = await FileAttachment("data/issue_typology_annual.csv").csv({typed: true});
const contributors = await FileAttachment("data/contributors.csv").csv({typed: true});
```

<div class="grid grid-cols-4">
  <div class="card">
    <h2>Repos tracked</h2>
    <span class="big">${repos.length}</span>
  </div>
  <div class="card">
    <h2>Total issues+PRs</h2>
    <span class="big">${d3.sum(annual, d => d.issues_opened + d.prs_opened).toLocaleString()}</span>
  </div>
  <div class="card">
    <h2>Total commits</h2>
    <span class="big">${d3.sum(annual, d => d.commits).toLocaleString()}</span>
  </div>
  <div class="card">
    <h2>Distinct contributors</h2>
    <span class="big">${new Set(contributors.map(d => d.login)).size}</span>
  </div>
</div>

## Lead figure: How the work changed over 12 years

Stacked-area chart of issue typology by year. Watch `text-correction` dominate; see the rise of `link-target`, `markup`, and (recently) `bug` / `enhancement` as the project matured.

```js
Plot.plot({
  title: "Issues created per year, by type label",
  width,
  height: 400,
  marginLeft: 60,
  x: {label: "Year", tickFormat: ""},
  y: {label: "Issues created"},
  color: {legend: true, scheme: "tableau10"},
  marks: [
    Plot.areaY(typology, {x: "year", y: "count", fill: "type_label", curve: "monotone-x", tip: true}),
    Plot.ruleY([0])
  ]
})
```

## Annual throughput

```js
Plot.plot({
  title: "Issues opened vs. closed per year",
  width,
  height: 350,
  x: {label: "Year"},
  y: {label: "Count"},
  color: {legend: true, domain: ["issues_opened", "issues_closed"], range: ["#0075ca", "#1a7f37"]},
  marks: [
    Plot.barY(d3.flatRollup(annual, v => d3.sum(v, x => x.issues_opened), d => d.year).map(([year, c]) => ({year, kind: "issues_opened", count: c})), {x: "year", y: "count", fill: "kind", dx: -8, insetLeft: 1, insetRight: 1}),
    Plot.barY(d3.flatRollup(annual, v => d3.sum(v, x => x.issues_closed), d => d.year).map(([year, c]) => ({year, kind: "issues_closed", count: c})), {x: "year", y: "count", fill: "kind", dx: 8, insetLeft: 1, insetRight: 1}),
    Plot.ruleY([0])
  ]
})
```

## Top 10 most active repositories (all-time)

```js
const repoActivity = d3.flatRollup(annual, v => d3.sum(v, x => x.issues_opened + x.prs_opened + x.commits), d => d.repo)
  .map(([repo, total]) => ({repo, total}))
  .sort((a, b) => b.total - a.total)
  .slice(0, 10);

Plot.plot({
  title: "Top 10 repos by lifetime activity",
  width,
  height: 350,
  marginLeft: 140,
  x: {label: "Issues + PRs + commits (all-time)"},
  y: {label: null, domain: repoActivity.map(d => d.repo)},
  marks: [
    Plot.barX(repoActivity, {x: "total", y: "repo", fill: "#0075ca", tip: true}),
    Plot.ruleX([0])
  ]
})
```

## Navigation

- [**Activity**](/activity) — issue/commit/PR throughput timelines, heatmaps, GitHub-style year grids
- [**Coverage**](/coverage) — what got digitized, corrected, linked. Issue typology by repo
- [**Community**](/community) — contributor growth, retention, bus-factor analysis
- [**Tech Stack**](/tech-stack) — language evolution, dependency graphs, runbook adoption
- [**Benchmarks**](/benchmarks) — comparison with TLG, Perseus, CDLI, DDBDP, sister projects
- [**Data**](/data) — raw downloads (CSV, JSON, Parquet) for reproducibility

---

*Last refreshed from GitHub on ${new Date().toISOString().slice(0, 10)}.
Refresh cadence: manual + monthly fallback (see [design doc](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/docs/OBSERVATORY_DESIGN.md)).*

<style>
.card .big { font-size: 2rem; font-weight: 600; display: block; }
</style>
