---
title: Community continuity
toc: true
---

# Community Continuity

Maintainer continuity and contributor concentration views for monthly review.

```js
const commits = await FileAttachment("data/commits.csv").csv({typed: true});
const contributors = await FileAttachment("data/contributors.csv").csv({typed: true});
const busFactor = await FileAttachment("data/bus_factor.csv").csv({typed: true});
const peopleSummary = await FileAttachment("data/people_summary.csv").csv({typed: true});
const repos = await FileAttachment("data/repos.csv").csv({typed: true});
```

```js
const GREEN = "#1a7f37";
const AMBER = "#bf8700";
const RED = "#cf222e";
const BLUE = "#0969da";
const repoInfo = new Map(repos.map(d => [d.repo, d]));
const humanContribs = contributors.filter(d => d.type !== "Bot");
```

## Contributor Retention: First X Last Commit Year

```js
const byPerson = d3.rollup(commits.filter(d => d.author_login), v => {
  const years = v.map(d => new Date(d.date).getFullYear()).filter(Boolean);
  return {first: d3.min(years), last: d3.max(years), commits: v.length};
}, d => d.author_login);
const retention = Array.from(byPerson, ([login, stats]) => ({login, ...stats}))
  .filter(d => d.first && d.last);
```

```js
const contributorScope = view(Inputs.select(["all contributors", "active in 2026", "inactive before 2026"], {value: "all contributors", label: "Contributor scope"}));
const scopedRetention = retention.filter(d => {
  if (contributorScope === "active in 2026") return d.last >= 2026;
  if (contributorScope === "inactive before 2026") return d.last < 2026;
  return true;
});
```

```js
display(Plot.plot({
  width,
  height: 430,
  x: {label: "First commit year", tickFormat: "d", grid: true},
  y: {label: "Last commit year", tickFormat: "d", grid: true},
  color: {legend: true, domain: ["active in 2026", "inactive"], range: [GREEN, AMBER]},
  marks: [
    Plot.dot(scopedRetention, {x: "first", y: "last", r: d => Math.max(3, Math.sqrt(d.commits)), fill: d => d.last >= 2026 ? "active in 2026" : "inactive", tip: true, channels: {Login: "login", Commits: "commits"}})
  ]
}))
```

## Repo Contributor-Count Distribution

```js
const contributorCounts = Array.from(d3.rollup(busFactor, v => v.length, d => +d.contributors || 0), ([contributors, count]) => ({contributors, count}))
  .sort((a, b) => a.contributors - b.contributors);

display(Plot.plot({
  width,
  height: 300,
  x: {label: "Contributors in repo history"},
  y: {label: "Repositories", grid: true},
  marks: [
    Plot.barY(contributorCounts, {x: "contributors", y: "count", fill: d => d.contributors <= 2 ? RED : AMBER, tip: true}),
    Plot.ruleY([0])
  ]
}))
```

## Largest Contributor Share Histogram

```js
const shareBins = d3.range(0.1, 1.1, 0.1).map(upper => {
  const lower = +(upper - 0.1).toFixed(1);
  return {
    bucket: `${Math.round(lower * 100)}-${Math.round(upper * 100)}%`,
    upper,
    count: busFactor.filter(d => (+d.top_share || 0) > lower && (+d.top_share || 0) <= upper).length
  };
});

display(Plot.plot({
  width,
  height: 320,
  marginBottom: 60,
  x: {label: "Largest contributor share", domain: shareBins.map(d => d.bucket), tickRotate: -35},
  y: {label: "Repositories", grid: true},
  marks: [
    Plot.barY(shareBins, {x: "bucket", y: "count", fill: d => d.upper > 0.5 ? RED : GREEN, tip: true}),
    Plot.ruleY([0])
  ]
}))
```

## Bus-Factor Risk By Primary Language

```js
const languageRows = busFactor.map(d => ({
  repo: d.repo,
  language: repoInfo.get(d.repo)?.primary_language || "unknown",
  risk: +d.bus_factor === 1 ? "bus factor 1" : "bus factor >= 2"
}));
const topLanguages = Array.from(d3.rollup(languageRows, v => v.length, d => d.language), ([language, count]) => ({language, count}))
  .sort((a, b) => b.count - a.count)
  .slice(0, 8)
  .map(d => d.language);
const languageRisk = Array.from(d3.rollup(languageRows.filter(d => topLanguages.includes(d.language)), v => v.length, d => d.language, d => d.risk), ([language, inner]) =>
  Array.from(inner, ([risk, count]) => ({language, risk, count}))
).flat();

display(Plot.plot({
  width,
  height: 360,
  marginLeft: 100,
  x: {label: "Repositories", grid: true},
  y: {label: null, domain: topLanguages},
  color: {legend: true, domain: ["bus factor 1", "bus factor >= 2"], range: [RED, GREEN]},
  marks: [
    Plot.barX(languageRisk, Plot.stackX({x: "count", y: "language", fill: "risk", tip: true})),
    Plot.ruleX([0])
  ]
}))
```

## Identity And ORCID Status

```js
const identityRows = peopleSummary.flatMap(d => [
  {kind: "identity status", status: String(d.status || "unknown"), n: 1},
  {kind: "ORCID", status: String(d.orcid || "").trim() ? "has ORCID" : "missing ORCID", n: 1}
]);
const identityCounts = Array.from(d3.rollup(identityRows, v => v.length, d => d.kind, d => d.status), ([kind, inner]) =>
  Array.from(inner, ([status, count]) => ({kind, status, count}))
).flat();

display(Plot.plot({
  width,
  height: 340,
  marginLeft: 120,
  x: {label: "People", grid: true},
  y: {label: null},
  color: {legend: true, range: [GREEN, AMBER, RED, BLUE, "#8250df"]},
  marks: [
    Plot.barX(identityCounts, Plot.stackX({x: "count", y: "kind", fill: "status", tip: true})),
    Plot.ruleX([0])
  ]
}))
```

[Back to overview](/)
