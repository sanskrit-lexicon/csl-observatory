---
title: Metadata readiness
toc: true
---

# Metadata Readiness

Operational view of B3 metadata coverage: documentation, automation, releases,
and unresolved live-fetch blockers.

```js
const metadata = await FileAttachment("data/repo_metadata.csv").csv({typed: true});
```

```js
const GREEN = "#1a7f37";
const AMBER = "#bf8700";
const RED = "#cf222e";
const BLUE = "#0969da";
const splitPipe = value => String(value ?? "").split("|").map(d => d.trim()).filter(Boolean);
const active = metadata.filter(d => String(d.archived).toLowerCase() !== "true");
```

```js
const metadataScope = view(Inputs.select(["all active repos", "unknown blockers", "fetch warnings"], {value: "all active repos", label: "Metadata scope"}));
```

```js
const scopedActive = active.filter(d => {
  if (metadataScope === "unknown blockers") return splitPipe(d.metadata_flags).some(flag => flag.endsWith("-unknown"));
  if (metadataScope === "fetch warnings") return String(d.fetch_warning ?? "").trim();
  return true;
});
const unknownFields = [
  ["README", "has_readme"],
  ["Citation", "has_citation"],
  ["Issue template", "has_issue_template"],
  ["PR template", "has_pr_template"],
  ["Workflows", "has_workflows"],
  ["Dependabot", "has_dependabot"],
  ["CodeQL", "has_codeql"],
  ["Releases", "release_count"]
];
const statusColor = status => status === "yes" ? GREEN : status === "no" || status === "0" ? RED : AMBER;
```

## Metadata Score Histogram

```js
const scoreHist = Array.from(d3.rollup(scopedActive, v => v.length, d => +d.metadata_score || 0), ([score, count]) => ({score, count}))
  .sort((a, b) => a.score - b.score);

display(Plot.plot({
  width,
  height: 300,
  x: {label: "Metadata score"},
  y: {label: "Repositories", grid: true},
  marks: [
    Plot.barY(scoreHist, {x: "score", y: "count", fill: d => d.score >= 8 ? GREEN : d.score >= 5 ? AMBER : RED, tip: true}),
    Plot.ruleY([0])
  ]
}))
```

## Unknown Field Blocker Breakdown

```js
const unknownBreakdown = unknownFields.map(([label, field]) => ({
  label,
  count: scopedActive.filter(d => String(d[field] ?? "") === "unknown").length
})).sort((a, b) => b.count - a.count);

display(Plot.plot({
  width,
  height: 330,
  marginLeft: 120,
  x: {label: "Repositories still unknown", grid: true},
  y: {label: null, domain: unknownBreakdown.map(d => d.label)},
  marks: [
    Plot.barX(unknownBreakdown, {x: "count", y: "label", fill: AMBER, tip: true}),
    Plot.ruleX([0])
  ]
}))
```

## Fetch Warning Type Breakdown

```js
function warningKind(d) {
  const warning = String(d.fetch_warning ?? "");
  if (!warning) return "none";
  if (warning.includes("tree:")) return "tree lookup";
  if (warning.includes("releases:")) return "release lookup";
  if (warning.includes("offline mode")) return "offline";
  if (warning.includes("cache")) return "cache";
  return "other";
}
const warningRows = Array.from(d3.rollup(scopedActive, v => v.length, warningKind), ([kind, count]) => ({kind, count}))
  .sort((a, b) => b.count - a.count);

display(Plot.plot({
  width,
  height: 260,
  marginLeft: 120,
  x: {label: "Repositories", grid: true},
  y: {label: null, domain: warningRows.map(d => d.kind)},
  marks: [
    Plot.barX(warningRows, {x: "count", y: "kind", fill: d => d.kind === "none" ? GREEN : AMBER, tip: true}),
    Plot.ruleX([0])
  ]
}))
```

## Automation Maturity

```js
const automationFields = [
  ["Workflows", "has_workflows"],
  ["Dependabot", "has_dependabot"],
  ["CodeQL", "has_codeql"]
];
const automationRows = automationFields.flatMap(([label, field]) => ["yes", "no", "unknown"].map(status => ({
  label,
  status,
  count: scopedActive.filter(d => String(d[field] ?? "") === status).length
})));

display(Plot.plot({
  width,
  height: 280,
  marginLeft: 110,
  x: {label: "Repositories", grid: true},
  y: {label: null, domain: automationFields.map(d => d[0])},
  color: {legend: true, domain: ["yes", "no", "unknown"], range: [GREEN, RED, AMBER]},
  marks: [
    Plot.barX(automationRows, Plot.stackX({x: "count", y: "label", fill: "status", tip: true})),
    Plot.ruleX([0])
  ]
}))
```

## Release Readiness By License Class

```js
function releaseStatus(d) {
  if (String(d.release_count ?? "") === "unknown") return "unknown";
  return (+d.release_count || 0) > 0 ? "has release" : "no release";
}
const releaseRows = Array.from(d3.rollup(scopedActive, v => v.length, d => d.license_class, releaseStatus), ([license_class, inner]) =>
  Array.from(inner, ([status, count]) => ({license_class, status, count}))
).flat();

display(Plot.plot({
  width,
  height: 320,
  x: {label: "License class"},
  y: {label: "Repositories", grid: true},
  color: {legend: true, domain: ["has release", "no release", "unknown"], range: [GREEN, RED, AMBER]},
  marks: [
    Plot.barY(releaseRows, Plot.stackY({x: "license_class", y: "count", fill: "status", tip: true})),
    Plot.ruleY([0])
  ]
}))
```

[Back to overview](/)
