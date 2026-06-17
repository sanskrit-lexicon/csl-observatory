---
title: Repository risk
toc: true
---

# Repository Risk

Deeper repository-hygiene views for license, branch, size, stale cleanup, and
flag interactions.

```js
const repos = await FileAttachment("data/repos.csv").csv({typed: true});
const health = await FileAttachment("data/repo_health.csv").csv({typed: true});
```

```js
const GREEN = "#1a7f37";
const AMBER = "#bf8700";
const RED = "#cf222e";
const BLUE = "#0969da";
const splitPipe = value => String(value ?? "").split("|").map(d => d.trim()).filter(Boolean);
const repoMeta = new Map(repos.map(d => [d.repo, d]));
const rows = health.map(d => ({...d, repo_info: repoMeta.get(d.repo) ?? {}}));
const repoUrl = repo => `https://github.com/sanskrit-lexicon/${repo}`;
```

```js
const repoScope = view(Inputs.select(["all repos", "flagged repos", "cleanup candidates"], {value: "all repos", label: "Repository scope"}));
```

```js
const scopedRows = rows.filter(d => {
  if (repoScope === "flagged repos") return (+d.flag_count || 0) > 0;
  if (repoScope === "cleanup candidates") return splitPipe(d.flags).includes("cleanup-candidate");
  return true;
});
```

## License X Branch Heatmap

```js
const licenseBranch = Array.from(
  d3.rollup(scopedRows, v => v.length, d => d.license_class, d => d.default_branch),
  ([license_class, inner]) => Array.from(inner, ([branch, count]) => ({license_class, branch, count}))
).flat();

display(Plot.plot({
  width,
  height: 260,
  marginLeft: 130,
  x: {label: "Default branch"},
  y: {label: null},
  color: {scheme: "YlOrRd", legend: true, label: "Repositories"},
  marks: [
    Plot.cell(licenseBranch, {x: "branch", y: "license_class", fill: "count", tip: true}),
    Plot.text(licenseBranch, {x: "branch", y: "license_class", text: "count", fill: "black"})
  ]
}))
```

## Flag Co-Occurrence Matrix

```js
const flagNames = Array.from(new Set(scopedRows.flatMap(d => splitPipe(d.flags)))).sort();
const flagPairs = [];
for (const d of scopedRows) {
  const flags = splitPipe(d.flags);
  for (const a of flags) for (const b of flags) flagPairs.push({a, b, repo: d.repo});
}
const flagMatrix = Array.from(d3.rollup(flagPairs, v => v.length, d => d.a, d => d.b), ([a, inner]) =>
  Array.from(inner, ([b, count]) => ({a, b, count}))
).flat();

display(Plot.plot({
  width,
  height: 520,
  marginLeft: 150,
  marginBottom: 120,
  x: {label: null, domain: flagNames, tickRotate: -35},
  y: {label: null, domain: flagNames},
  color: {scheme: "YlOrRd", legend: true, label: "Repos"},
  marks: [
    Plot.cell(flagMatrix, {x: "b", y: "a", fill: "count", tip: true})
  ]
}))
```

## Repo Age X Size

```js
const nowYear = 2026;
const ageSize = scopedRows.map(d => {
  const info = d.repo_info ?? {};
  const created = info.created_at ? new Date(info.created_at).getFullYear() : null;
  return {
    repo: d.repo,
    age: created ? nowYear - created : null,
    size_kb: +info.size_kb || 0,
    license_class: d.license_class,
    flag_count: +d.flag_count || 0,
    open_issues: +d.open_issues || 0
  };
}).filter(d => d.age !== null);

display(Plot.plot({
  width,
  height: 420,
  x: {label: "Repository age (years)", grid: true},
  y: {label: "Size (KB)", grid: true, type: "sqrt"},
  color: {legend: true, domain: ["recognised", "unrecognised", "none"], range: [GREEN, AMBER, RED]},
  marks: [
    Plot.dot(ageSize, {x: "age", y: "size_kb", r: d => Math.max(3, Math.sqrt(d.flag_count + 1) * 3), fill: "license_class", tip: true, channels: {Repository: "repo", "Open issues": "open_issues", "Flags": "flag_count"}})
  ]
}))
```

## Cleanup Candidates: Idle Time X Open Issues

```js
const cleanup = scopedRows.filter(d => splitPipe(d.flags).includes("cleanup-candidate"))
  .sort((a, b) => d3.descending(+a.days_since_push || 0, +b.days_since_push || 0));

display(Plot.plot({
  width,
  height: 360,
  marginRight: 120,
  x: {label: "Days since last push", grid: true},
  y: {label: "Open issues", grid: true},
  marks: [
    Plot.dot(cleanup, {x: "days_since_push", y: "open_issues", r: 7, fill: RED, tip: true}),
    Plot.text(cleanup, {x: "days_since_push", y: "open_issues", text: "repo", dx: 10, fill: "currentColor"})
  ]
}))
```

## Hygiene Flag Distribution

```js
const flagHistogram = Array.from(d3.rollup(scopedRows, v => v.length, d => +d.flag_count || 0), ([flag_count, count]) => ({flag_count, count}))
  .sort((a, b) => a.flag_count - b.flag_count);

display(Plot.plot({
  width,
  height: 300,
  x: {label: "Hygiene flag count"},
  y: {label: "Repositories", grid: true},
  marks: [
    Plot.barY(flagHistogram, {x: "flag_count", y: "count", fill: d => d.flag_count === 0 ? GREEN : AMBER, tip: true}),
    Plot.ruleY([0])
  ]
}))
```

[Back to overview](/)
