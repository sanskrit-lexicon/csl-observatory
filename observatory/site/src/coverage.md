---
title: Coverage and quality
toc: true
---

# Coverage and quality

What got digitized, corrected, linked. The 9-label issue typology over time.

```js
const typology = await FileAttachment("data/issue_typology_annual.csv").csv({typed: true});
const issues = await FileAttachment("data/issues.csv").csv({typed: true});
```

## Issue typology evolution (Paper 1 lead figure)

```js
Plot.plot({
  width,
  height: 500,
  marginLeft: 60,
  x: {label: "Year"},
  y: {label: "Issues"},
  color: {legend: true, scheme: "tableau10"},
  marks: [
    Plot.areaY(typology, {x: "year", y: "count", fill: "type_label", curve: "monotone-x", tip: true}),
    Plot.ruleY([0])
  ]
})
```

## Issue type distribution (all-time, top labels)

```js
const labelTotals = d3.flatRollup(issues, v => v.length, d => d.labels.split("|").filter(l => l).join("|") || "(no labels)")
  .filter(([k]) => k && !k.includes("|"))
  .map(([label, count]) => ({label, count}))
  .sort((a, b) => b.count - a.count)
  .slice(0, 20);

Plot.plot({
  width,
  height: 500,
  marginLeft: 200,
  x: {label: "Issue count", grid: true},
  y: {label: null, domain: labelTotals.map(d => d.label)},
  marks: [
    Plot.barX(labelTotals, {x: "count", y: "label", fill: "#0075ca", tip: true}),
    Plot.ruleX([0])
  ]
})
```

## Open vs closed by repo (top 20 most active)

```js
const repoStats = d3.flatRollup(issues,
  v => ({
    open: v.filter(d => d.state === "open").length,
    closed: v.filter(d => d.state === "closed").length
  }),
  d => d.repo
).map(([repo, s]) => ({repo, ...s, total: s.open + s.closed}))
 .sort((a, b) => b.total - a.total)
 .slice(0, 20);

Plot.plot({
  width,
  height: 600,
  marginLeft: 140,
  x: {label: "Issues"},
  y: {label: null, domain: repoStats.map(d => d.repo)},
  color: {legend: true, domain: ["closed", "open"], range: ["#1a7f37", "#bf8700"]},
  marks: [
    Plot.barX(repoStats.flatMap(d => [
      {repo: d.repo, kind: "closed", count: d.closed},
      {repo: d.repo, kind: "open", count: d.open}
    ]), {x: "count", y: "repo", fill: "kind", tip: true}),
    Plot.ruleX([0])
  ]
})
```

[← back to overview](/)
