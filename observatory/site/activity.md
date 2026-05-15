---
title: Activity timeline
toc: true
---

# Activity timeline

Issue, PR, and commit throughput over 12 years across all 77 sanskrit-lexicon repos.

```js
const monthly = await FileAttachment("data/timeseries_monthly.csv").csv({typed: true});
const annual = await FileAttachment("data/timeseries_annual.csv").csv({typed: true});
```

## Issues opened per month (all repos stacked)

```js
Plot.plot({
  width,
  height: 400,
  marginLeft: 60,
  x: {label: "Month", type: "utc"},
  y: {label: "Issues opened", grid: true},
  marks: [
    Plot.areaY(monthly, {x: d => new Date(d.year_month + "-01"), y: "issues_opened", fill: "repo", curve: "monotone-x", tip: true}),
    Plot.ruleY([0])
  ]
})
```

## Commits per month (stacked by repo)

```js
Plot.plot({
  width,
  height: 400,
  marginLeft: 60,
  x: {label: "Month", type: "utc"},
  y: {label: "Commits", grid: true},
  marks: [
    Plot.areaY(monthly, {x: d => new Date(d.year_month + "-01"), y: "commits", fill: "repo", curve: "monotone-x", tip: true}),
    Plot.ruleY([0])
  ]
})
```

## Activity heatmap: year × repo

```js
const repoSet = Array.from(new Set(annual.map(d => d.repo))).sort();
Plot.plot({
  width,
  height: 1200,
  marginLeft: 180,
  x: {label: "Year", domain: d3.range(2014, 2027)},
  y: {label: null, domain: repoSet},
  color: {scheme: "viridis", legend: true, label: "Issues+commits"},
  marks: [
    Plot.cell(annual, {
      x: d => +d.year,
      y: "repo",
      fill: d => d.issues_opened + d.commits,
      tip: true
    })
  ]
})
```

## Annual unique commit-authors

```js
const annualAuthors = d3.flatRollup(annual, v => d3.sum(v, x => x.unique_authors), d => d.year)
  .map(([year, n]) => ({year, n}));

Plot.plot({
  width,
  height: 300,
  x: {label: "Year"},
  y: {label: "Unique commit authors (sum across repos)"},
  marks: [
    Plot.barY(annualAuthors, {x: "year", y: "n", fill: "#0075ca", tip: true}),
    Plot.ruleY([0])
  ]
})
```

[← back to overview](/)
