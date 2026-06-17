---
title: Workflow Health
toc: true
---

# Workflow Health

Read-only baseline for CI, scheduled jobs, artifact refresh, Dependabot, CodeQL,
and release signals across the organization.

```js
const workflows = await FileAttachment("data/workflow_health.csv").csv({typed: true});
```

```js
const GREEN = "#1a7f37";
const AMBER = "#bf8700";
const RED = "#cf222e";
const BLUE = "#0969da";
const splitPipe = value => String(value ?? "").split("|").map(d => d.trim()).filter(Boolean);
const active = workflows.filter(d => String(d.archived).toLowerCase() !== "true");
```

```js
const scope = view(Inputs.select(["all active repos", "lowest-score queue", "fetch warnings"], {label: "Workflow scope"}));
```

```js
const scoped = active.filter(d => {
  if (scope === "lowest-score queue") return (+d.workflow_health_score || 0) <= 2;
  if (scope === "fetch warnings") return String(d.fetch_warning ?? "").trim();
  return true;
});
```

```js
const metricRows = [
  ["Repos", active.length],
  ["With workflows", active.filter(d => (+d.workflow_count || 0) > 0).length],
  ["Scheduled", active.filter(d => (+d.scheduled_workflow_count || 0) > 0).length],
  ["Artifact/refresh", active.filter(d => (+d.artifact_refresh_workflow_count || 0) > 0).length],
  ["Dependabot", active.filter(d => String(d.has_dependabot) === "yes").length],
  ["CodeQL", active.filter(d => String(d.has_codeql) === "yes").length],
  ["Releases", active.filter(d => (+d.release_count || 0) > 0).length]
];
```

<div class="metric-grid">
  ${metricRows.map(([label, value]) => html`<div class="metric">
    <div class="label">${label}</div>
    <div class="value">${value.toLocaleString()}</div>
  </div>`)}
</div>

## Workflow Score Distribution

```js
const scoreRows = Array.from(d3.rollup(scoped, v => v.length, d => +d.workflow_health_score || 0), ([score, count]) => ({score, count}))
  .sort((a, b) => a.score - b.score);

display(Plot.plot({
  width,
  height: 300,
  x: {label: "Workflow health score"},
  y: {label: "Repositories", grid: true},
  marks: [
    Plot.barY(scoreRows, {x: "score", y: "count", fill: d => d.score >= 6 ? GREEN : d.score >= 3 ? AMBER : RED, tip: true}),
    Plot.ruleY([0])
  ]
}))
```

## Automation Signals

```js
const signalRows = [
  ["Workflows", "workflow_count"],
  ["Scheduled", "scheduled_workflow_count"],
  ["Artifact/refresh", "artifact_refresh_workflow_count"],
  ["CI/test/build", "ci_workflow_count"],
  ["Deploy/pages", "deploy_workflow_count"],
  ["Releases", "release_count"]
].map(([label, field]) => ({
  label,
  yes: scoped.filter(d => (+d[field] || 0) > 0).length,
  no: scoped.filter(d => (+d[field] || 0) === 0).length
})).flatMap(d => [
  {label: d.label, status: "present", count: d.yes},
  {label: d.label, status: "missing", count: d.no}
]);

display(Plot.plot({
  width,
  height: 330,
  marginLeft: 120,
  x: {label: "Repositories", grid: true},
  y: {label: null},
  color: {legend: true, domain: ["present", "missing"], range: [GREEN, RED]},
  marks: [
    Plot.barX(signalRows, Plot.stackX({x: "count", y: "label", fill: "status", tip: true})),
    Plot.ruleX([0])
  ]
}))
```

## Dependency And Security Coverage

```js
const binaryRows = [
  ["Dependabot", "has_dependabot"],
  ["CodeQL", "has_codeql"]
].flatMap(([label, field]) => ["yes", "no", "unknown"].map(status => ({
  label,
  status,
  count: scoped.filter(d => String(d[field] ?? "unknown") === status).length
})));

display(Plot.plot({
  width,
  height: 220,
  marginLeft: 95,
  x: {label: "Repositories", grid: true},
  y: {label: null},
  color: {legend: true, domain: ["yes", "no", "unknown"], range: [GREEN, RED, AMBER]},
  marks: [
    Plot.barX(binaryRows, Plot.stackX({x: "count", y: "label", fill: "status", tip: true})),
    Plot.ruleX([0])
  ]
}))
```

## Flag Mix

```js
const flagRows = Array.from(d3.rollup(scoped.flatMap(d => splitPipe(d.workflow_flags).map(flag => ({repo: d.repo, flag}))), v => v.length, d => d.flag), ([flag, count]) => ({flag, count}))
  .sort((a, b) => d3.descending(a.count, b.count));

display(Plot.plot({
  width,
  height: Math.max(300, flagRows.length * 24),
  marginLeft: 210,
  x: {label: "Repositories", grid: true},
  y: {label: null, domain: flagRows.map(d => d.flag)},
  marks: [
    Plot.barX(flagRows, {x: "count", y: "flag", fill: d => d.flag.includes("unknown") ? AMBER : RED, tip: true}),
    Plot.ruleX([0])
  ]
}))
```

## Action Queue

```js
const queue = scoped
  .slice()
  .sort((a, b) =>
    d3.ascending(+a.workflow_health_score || 0, +b.workflow_health_score || 0) ||
    d3.descending(splitPipe(a.workflow_flags).length, splitPipe(b.workflow_flags).length) ||
    d3.ascending(a.repo, b.repo)
  )
  .slice(0, 25);

display(Inputs.table(queue, {
  columns: [
    "repo",
    "workflow_health_score",
    "workflow_count",
    "scheduled_workflow_count",
    "artifact_refresh_workflow_count",
    "has_dependabot",
    "has_codeql",
    "release_count",
    "workflow_flags",
    "fetch_warning"
  ],
  header: {
    repo: "Repo",
    workflow_health_score: "Score",
    workflow_count: "Workflows",
    scheduled_workflow_count: "Scheduled",
    artifact_refresh_workflow_count: "Artifact/refresh",
    has_dependabot: "Dependabot",
    has_codeql: "CodeQL",
    release_count: "Releases",
    workflow_flags: "Flags",
    fetch_warning: "Fetch warning"
  },
  rows: 25
}))
```

<style>
.metric-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(8rem, 1fr));
  gap: 0.75rem;
  margin: 1rem 0 1.5rem;
}
.metric {
  border: 1px solid var(--theme-foreground-faint);
  border-radius: 8px;
  padding: 0.75rem;
  background: var(--theme-background-alt);
}
.label {
  color: var(--theme-foreground-muted);
  font-size: 0.82rem;
  margin-bottom: 0.2rem;
}
.value {
  font-size: 1.45rem;
  font-weight: 700;
}
</style>
