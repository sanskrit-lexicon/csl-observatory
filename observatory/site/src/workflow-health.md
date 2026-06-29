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

Each active repository receives a workflow health score based on which CI automation signals are present: a base score for having any workflows, with bonuses for scheduled jobs, artifact-refresh pipelines, CI/test/build workflows, deploy pipelines, and formal releases. The histogram shows whether repos cluster at the top (well-automated) or the bottom (no automation at all), and where the biggest improvement opportunities are.

> **How to read:** Each bar is one score level; colour codes the tier: green ≥ 6 (well-automated), amber 3–5 (partial), red < 3 (minimal or none). **Example 1:** A large red bar at score 0 means many repos have no GitHub Actions at all — no CI, no scheduled jobs, no releases — the org's baseline automation level. **Example 2:** A small peak at the maximum score identifies a well-configured cluster; those repos are the templates to copy when setting up automation for others.

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

> **Conclusion:** A distribution with most repos at score 0–2 is expected for a project where most content repos are simple dictionary text holders that need no CI. However, tooling repos (csl-websanlexicon, csl-apidev, csl-pywork) scoring below 3 would be a genuine concern — those are the repos where automation failures have direct impact on the live public site.

## Automation Signals

For each of six automation categories — GitHub Actions workflows, scheduled jobs, artifact/refresh pipelines, CI/test/build, deploy/pages, and formal releases — this chart shows how many repos have that signal present vs missing. The split across six categories reveals which automation types are widespread and which are rare, pointing to org-wide gaps that could be addressed with a shared template or runbook.

> **How to read:** Each row is one automation type; bars stack "present" (green) vs "missing" (red). **Example 1:** If "Workflows" shows most repos as "present" but "Scheduled" shows mostly "missing," repos have adopted basic CI but have not configured any recurring automated tasks — data refresh or periodic health checks are not running. **Example 2:** A "Releases" row that is mostly "missing" means repos are not making formal tagged releases — important for reproducibility and scholarly citation.

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

> **Conclusion:** Releases and scheduled jobs are typically the last automation layers to be adopted; their absence across most repos is expected but should be remedied for any repo whose data outputs are intended to be citable. A single shared release workflow template could bring many repos from 0 to 1 releases with minimal per-repo effort.

## Dependency And Security Coverage

Dependabot (automated dependency update PRs) and CodeQL (GitHub's static security analysis) are the two security-focused automation signals tracked per repository. Both require opting in via configuration files. For pure-data dictionary repos the risk is low, but for web-facing infrastructure repos (csl-apidev, csl-websanlexicon), the absence of these tools is a concrete security gap — dependency vulnerabilities go unpatched until a maintainer manually notices them.

> **How to read:** Each row is one security tool; bars stack "yes" (green), "no" (red), "unknown" (amber). **Example 1:** If Dependabot is "yes" for only a handful of repos, most dependency updates — including security patches — are happening manually or not at all. **Example 2:** A large "unknown" segment for CodeQL means the data snapshot could not confirm its status — re-check after a live refresh before concluding it is absent.

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

> **Conclusion:** Low Dependabot and CodeQL coverage is the org's primary security-automation gap. For pure-data repos this is low risk; for web-facing repos running production infrastructure, lack of automated dependency updates is an addressable vulnerability. Dependabot can be enabled with a single `.github/dependabot.yml` file — one file, one repo, immediate improvement.

## Flag Mix

A ranked breakdown of which specific workflow-health flags appear most frequently across the org's active repositories. Each flag represents one concrete automation gap (no-workflows, no-scheduled-job, no-releases, etc.). The rank order tells maintainers whether gaps are systemic — affecting many repos and addressable with a shared template — or isolated — affecting specific repos requiring individual attention.

> **How to read:** Each bar is one flag type; length = repos carrying that flag. Amber = "unknown" flags (data-snapshot gaps); red = confirmed automation gaps. **Example 1:** If "no-releases" is the longest bar, the most widespread single automation gap across the org is the absence of formal tagged releases — a systemic problem addressable with an org-level release-workflow template. **Example 2:** An amber "unknown" flag that appears frequently means the data snapshot has a consistent blind spot for that field — a live refresh should resolve most instances.

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

> **Conclusion:** The flag mix converts per-repo workflow data into an org-wide action list. Flags at the top are systemic — worth addressing with a shared template that many repos can adopt. Amber unknown flags are data-quality problems that resolve with a live snapshot refresh and should not be treated as confirmed gaps until verified.

## Action Queue

The 25 lowest-scoring repositories, sorted first by workflow health score (ascending) then by flag count (descending) — the repos that most need CI/automation attention this sprint. Unlike the ops-command action queue which scores across all risk dimensions, this queue focuses specifically on workflow and release automation gaps. The sortable table lets maintainers drill into the specific missing signals for each repo.

> **How to read:** Each row is one repo; columns show the score, specific workflow counts, Dependabot/CodeQL presence, release count, and the flags that lowered the score. **Example 1:** A repo with score 0, no workflows, no releases, and flags "no-workflows|no-releases" needs both a basic CI workflow file and a release process set up from scratch. **Example 2:** A repo with score 3, existing workflows, and flag "no-scheduled-job" is already partially automated — the specific gap is easy to add (a cron trigger on an existing workflow).

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

> **Conclusion:** The workflow action queue is the maintainer's CI sprint list for this snapshot. Repos at the top (score 0, multiple flags) are completely unautomated and need setup from scratch. Repos lower in the queue (score 2–3, single remaining flag) need one targeted addition. Any tooling or web-facing repo appearing in this queue is higher priority than a pure-content dictionary repo with the same score.

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
