---
title: Taxonomy triage
toc: true
---

# Taxonomy Triage

Issue-label quality and triage gaps for maintainer review.

```js
const typology = await FileAttachment("data/issue_typology_annual.csv").csv({typed: true});
const issues = await FileAttachment("data/issues.csv").csv({typed: true});
const adoption = await FileAttachment("data/taxonomy_adoption.csv").csv({typed: true});
```

```js
const GREEN = "#1a7f37";
const AMBER = "#bf8700";
const RED = "#cf222e";
const BLUE = "#0969da";
const typeLabelSet = new Set(typology.map(d => d.type_label));
const severitySet = new Set(["trivial", "minor", "medium", "major", "hard"]);
const issueLabels = d => String(d.labels ?? "").split("|").map(label => label.trim()).filter(Boolean);
const issueTypes = d => issueLabels(d).filter(label => typeLabelSet.has(label));
const issueSeverities = d => issueLabels(d).filter(label => severitySet.has(label));
```

## Typed Vs Untyped Trend

```js
const typedTrend = adoption.flatMap(d => [
  {year: d.year, status: "typed", count: d.typed},
  {year: d.year, status: "untyped", count: d.issues - d.typed}
]);

display(Plot.plot({
  width,
  height: 330,
  x: {label: "Year", tickFormat: "d"},
  y: {label: "Issues opened", grid: true},
  color: {legend: true, domain: ["typed", "untyped"], range: [GREEN, AMBER]},
  marks: [
    Plot.barY(typedTrend, Plot.stackY({x: "year", y: "count", fill: "status", tip: true})),
    Plot.ruleY([0])
  ]
}))
```

## Open Issues By Type Label

```js
const openTypeRows = issues.filter(d => d.state === "open").flatMap(d => {
  const types = issueTypes(d);
  return types.length ? types.map(label => ({label})) : [{label: "(no type)"}];
});
const openTypes = Array.from(d3.rollup(openTypeRows, v => v.length, d => d.label), ([label, count]) => ({label, count}))
  .sort((a, b) => b.count - a.count)
  .slice(0, 20);

display(Plot.plot({
  width,
  height: 520,
  marginLeft: 150,
  x: {label: "Open issues", grid: true},
  y: {label: null, domain: openTypes.map(d => d.label)},
  marks: [
    Plot.barX(openTypes, {x: "count", y: "label", fill: d => d.label === "(no type)" ? RED : BLUE, tip: true}),
    Plot.ruleX([0])
  ]
}))
```

## Conformance Heatmap

```js
const conformanceRows = adoption.flatMap(d => [
  {year: d.year, requirement: "type", pct: d.pct_typed},
  {year: d.year, requirement: "severity", pct: d.pct_severity},
  {year: d.year, requirement: "milestone", pct: d.pct_milestone},
  {year: d.year, requirement: "full conformance", pct: d.pct_conformant}
]);

display(Plot.plot({
  width,
  height: 260,
  marginLeft: 130,
  x: {label: "Year", tickFormat: "d"},
  y: {label: null},
  color: {scheme: "YlGn", legend: true, label: "%"},
  marks: [
    Plot.cell(conformanceRows, {x: "year", y: "requirement", fill: "pct", tip: true}),
    Plot.text(conformanceRows, {x: "year", y: "requirement", text: d => `${Math.round(d.pct)}%`, fill: "black"})
  ]
}))
```

## Repo Conformance Scoreboard

```js
const scoreboardMode = view(Inputs.select(["lowest conformance", "highest conformance", "most open issues"], {value: "lowest conformance", label: "Scoreboard mode"}));
```

```js
const repoConformance = Array.from(d3.rollup(issues, v => {
  const conformant = v.filter(d => issueTypes(d).length === 1 && issueSeverities(d).length === 1 && String(d.milestone ?? "").trim()).length;
  const open = v.filter(d => d.state === "open").length;
  return {issues: v.length, conformant, open, pct: v.length ? conformant / v.length : 0};
}, d => d.repo), ([repo, stats]) => ({repo, ...stats}))
  .filter(d => d.issues >= 5);
const scoreboard = repoConformance.slice().sort((a, b) => {
  if (scoreboardMode === "highest conformance") return d3.descending(a.pct, b.pct) || d3.ascending(a.repo, b.repo);
  if (scoreboardMode === "most open issues") return d3.descending(a.open, b.open) || d3.ascending(a.repo, b.repo);
  return d3.ascending(a.pct, b.pct) || d3.descending(a.issues, b.issues);
}).slice(0, 20);

display(Plot.plot({
  width,
  height: 520,
  marginLeft: 140,
  x: {label: "Conformant share", percent: true, grid: true, domain: [0, 1]},
  y: {label: null, domain: scoreboard.map(d => d.repo)},
  marks: [
    Plot.barX(scoreboard, {x: "pct", y: "repo", fill: d => d.pct >= 0.8 ? GREEN : d.pct >= 0.5 ? AMBER : RED, tip: true, channels: {Issues: "issues", Open: "open"}}),
    Plot.ruleX([0])
  ]
}))
```

## Label Co-Occurrence: Type X Severity

```js
const coRows = issues.flatMap(d => {
  const types = issueTypes(d);
  const severities = issueSeverities(d);
  if (!types.length) return [];
  return types.flatMap(type => (severities.length ? severities : ["(no severity)"]).map(severity => ({type, severity})));
});
const coMatrix = Array.from(d3.rollup(coRows, v => v.length, d => d.type, d => d.severity), ([type, inner]) =>
  Array.from(inner, ([severity, count]) => ({type, severity, count}))
).flat();
const topTypes = Array.from(d3.rollup(coRows, v => v.length, d => d.type), ([type, count]) => ({type, count}))
  .sort((a, b) => b.count - a.count).slice(0, 18).map(d => d.type);

display(Plot.plot({
  width,
  height: 520,
  marginLeft: 150,
  marginBottom: 120,
  x: {label: null, domain: topTypes, tickRotate: -35},
  y: {label: null},
  color: {scheme: "YlOrRd", legend: true, label: "Issues"},
  marks: [
    Plot.cell(coMatrix.filter(d => topTypes.includes(d.type)), {x: "type", y: "severity", fill: "count", tip: true})
  ]
}))
```

[Back to overview](/)
