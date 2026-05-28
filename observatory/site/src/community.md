---
title: Community growth
toc: true
---

# Community growth

Contributors over 12 years. Bus-factor, retention, geographic distribution.

```js
const contributors = await FileAttachment("data/contributors.csv").csv({typed: true});
const peopleSummary = await FileAttachment("data/people_summary.csv").csv({typed: true});
const annual = await FileAttachment("data/timeseries_annual.csv").csv({typed: true});
const commits = await FileAttachment("data/commits.csv").csv({typed: true});
```

## Top contributors by total commits (lifetime)

```js
const contribTotals = d3.flatRollup(contributors, v => d3.sum(v, x => x.contributions), d => d.login)
  .map(([login, total]) => ({login, total}))
  .sort((a, b) => b.total - a.total)
  .slice(0, 20);

Plot.plot({
  width,
  height: 500,
  marginLeft: 140,
  x: {label: "Total commits (lifetime)"},
  y: {label: null, domain: contribTotals.map(d => d.login)},
  marks: [
    Plot.barX(contribTotals, {x: "total", y: "login", fill: "#5319e7", tip: true}),
    Plot.ruleX([0])
  ]
})
```

## Repo coverage per contributor

How many distinct repos each person has touched.

```js
const repoCoverage = d3.flatRollup(contributors, v => v.length, d => d.login)
  .map(([login, n_repos]) => ({login, n_repos}))
  .sort((a, b) => b.n_repos - a.n_repos)
  .slice(0, 20);

Plot.plot({
  width,
  height: 500,
  marginLeft: 140,
  x: {label: "Distinct repos contributed to"},
  y: {label: null, domain: repoCoverage.map(d => d.login)},
  marks: [
    Plot.barX(repoCoverage, {x: "n_repos", y: "login", fill: "#0075ca", tip: true}),
    Plot.ruleX([0])
  ]
})
```

## New contributors per year (first commit)

```js
const firstCommit = new Map();
for (const c of commits) {
  if (!c.author_login || !c.date) continue;
  const date = new Date(c.date);
  const existing = firstCommit.get(c.author_login);
  if (!existing || date < existing) firstCommit.set(c.author_login, date);
}

const newPerYear = d3.flatRollup(
  Array.from(firstCommit, ([login, date]) => ({login, year: date.getFullYear()})),
  v => v.length, d => d.year
).map(([year, n]) => ({year, n})).sort((a, b) => a.year - b.year);

Plot.plot({
  width,
  height: 350,
  x: {label: "Year"},
  y: {label: "New contributors (first commit)"},
  marks: [
    Plot.barY(newPerYear, {x: "year", y: "n", fill: "#1a7f37", tip: true}),
    Plot.ruleY([0])
  ]
})
```

## Bus-factor: top-3 commit concentration

If the top-3 contributors disappear, what % of repos lose >50% of their commit history?

```js
const repoConcentration = d3.flatRollup(contributors,
  v => {
    const sorted = v.sort((a, b) => b.contributions - a.contributions);
    const top3 = d3.sum(sorted.slice(0, 3), d => d.contributions);
    const total = d3.sum(sorted, d => d.contributions);
    return total > 0 ? top3 / total : 0;
  },
  d => d.repo
).map(([repo, ratio]) => ({repo, top3_share: ratio}))
 .sort((a, b) => b.top3_share - a.top3_share);

Plot.plot({
  width,
  height: 700,
  marginLeft: 140,
  x: {label: "Top-3 contributors' share of all commits", domain: [0, 1], grid: true, percent: true},
  y: {label: null, domain: repoConcentration.map(d => d.repo)},
  marks: [
    Plot.barX(repoConcentration, {x: "top3_share", y: "repo", fill: d => d.top3_share > 0.95 ? "#cf222e" : d.top3_share > 0.8 ? "#bf8700" : "#1a7f37", tip: true}),
    Plot.ruleX([0.5], {stroke: "red", strokeDasharray: "4 4"})
  ]
})
```

Red bars (>95% top-3 share) = high bus-factor risk. Green bars (<80%) = healthy distribution.

[← back to overview](/)
