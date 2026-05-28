---
title: Tech stack and ecosystem
toc: true
---

# Tech stack and ecosystem

How the technical infrastructure evolved over 12 years.

```js
const repos = await FileAttachment("data/repos.csv").csv({typed: true});
```

## Repos by primary language

```js
const langCounts = d3.flatRollup(repos, v => v.length, d => d.primary_language || "(none)")
  .map(([lang, count]) => ({lang, count}))
  .sort((a, b) => b.count - a.count);

Plot.plot({
  width,
  height: 400,
  marginLeft: 120,
  x: {label: "Number of repos"},
  y: {label: null, domain: langCounts.map(d => d.lang)},
  marks: [
    Plot.barX(langCounts, {x: "count", y: "lang", fill: "#5319e7", tip: true}),
    Plot.ruleX([0])
  ]
})
```

## Repos by size (KB)

```js
const sized = repos.filter(d => d.size_kb > 0).sort((a, b) => b.size_kb - a.size_kb).slice(0, 20);

Plot.plot({
  width,
  height: 500,
  marginLeft: 140,
  x: {label: "Size (KB)", type: "log"},
  y: {label: null, domain: sized.map(d => d.repo)},
  marks: [
    Plot.barX(sized, {x: "size_kb", y: "repo", fill: "#0075ca", tip: true}),
    Plot.ruleX([1])
  ]
})
```

## Repo creation timeline

When each repo was created.

```js
const repoTimeline = repos
  .filter(d => d.created_at)
  .map(d => ({...d, created: new Date(d.created_at)}))
  .sort((a, b) => a.created - b.created);

Plot.plot({
  width,
  height: 1100,
  marginLeft: 180,
  x: {label: "Date created", type: "utc"},
  y: {label: null, domain: repoTimeline.map(d => d.repo)},
  marks: [
    Plot.dot(repoTimeline, {x: "created", y: "repo", fill: "#0075ca", r: 5, tip: true}),
    Plot.ruleY(repoTimeline.map(d => d.repo), {stroke: "#eee"})
  ]
})
```

[← back to overview](/)
