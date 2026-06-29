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

Shows for each year how many issues opened that year received a type label (green) vs were left untyped (amber). This is the most direct measure of the taxonomy rollout's effectiveness over time: before the labelling runbook was applied, most issues were untyped; after the rollout, typed issues should dominate. Recent years reveal whether new issues are being labelled promptly or accumulating as unlabelled backlog.

> **How to read:** Each bar is one year; segments stack typed (green) and untyped (amber) issue counts. **Example 1:** A bar with almost no green segment in 2014–2015 shows that issues in the pre-taxonomy era were opened without labels — the labelling convention did not exist yet. **Example 2:** A bar with a significant amber segment in a recent year means current issues are arriving faster than the labelling workflow can process them — a triage-velocity problem, not a policy problem.

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

> **Conclusion:** The trend should show a clear inflection point around the year the runbook was deployed, with green dominating afterwards. Any recent amber growth indicates that new issues are not being labelled promptly — the most actionable finding on this page for a maintainer to act on this week.

## Open Issues By Type Label

The distribution of currently-open (unresolved) issues by type label — the live triage backlog by category, not the all-time history. Whichever type label has the longest bar represents the largest queue of outstanding work. The "(no type)" entry shows how much of the backlog cannot be prioritised because it has never been labelled at all.

> **How to read:** Each bar is one label; length = currently open issues with that label. "(no type)" is highlighted red. **Example 1:** If "text-correction" dominates the open backlog, thousands of identified dictionary errors are waiting to be addressed — the main correction work queue. **Example 2:** A large "(no type)" bar means a significant fraction of the open backlog cannot be routed to a workstream because it has never been labelled — triage before action is the first step.

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

> **Conclusion:** The open-by-type chart is the maintainer's triage list by category. The dominant label type in the open backlog is the highest-volume pending workstream. The "(no type)" bar is the meta-problem: issues that need labelling before they can even be assigned to a workflow.

## Conformance Heatmap

A year-by-requirement matrix where each cell shows the percentage of that year's issues meeting one conformance requirement. Unlike the line chart on the Issue Taxonomy page, the heatmap makes it easy to spot specific year × requirement combinations that are below expectation — for example, a pale "milestone" column in a recent year shows that milestoning has been lagging even if type labelling is current.

> **How to read:** Colour encodes the percentage — greener (darker) = higher conformance. Row = one requirement; column = one year's issue cohort. **Example 1:** A pale cell at ("milestone", 2026) means most issues opened in 2026 have not yet been assigned a milestone — an expected gap for recently-opened issues, but worth tracking. **Example 2:** A pale "milestone" row across all years while "type" is bright throughout reveals that type labelling succeeded retroactively but milestone assignment lagged — the milestone step needs a targeted backfill.

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

> **Conclusion:** The heatmap exposes specific gaps in retroactive labelling. If the "milestone" row is consistently paler than the "type" row, milestone assignment is the weakest link in the conformance chain — the next triage priority. Any pale column in recent years signals current-issue processing velocity has fallen behind.

## Repo Conformance Scoreboard

Each repository's share of issues that are fully conformant (type + severity + milestone), surfaced as a ranked list. The scoreboard mode dropdown switches between lowest conformance (repos needing triage), highest conformance (exemplar repos), and most open issues (where the largest backlogs live). This is the most directly actionable view on this page: it names the exact repos a maintainer should focus on this sprint.

> **How to read:** Each bar is one repo; length = share of its issues that are fully conformant. Colour signals tier: green ≥ 80%, amber 50–80%, red < 50%. **Example 1:** A repo at 5% conformance has almost no correctly labelled issues — either pre-taxonomy history that the runbook missed, or new issues arriving unlabelled faster than they are triaged. **Example 2:** A repo at 95%+ is a labelling model — its process is working; other repos should adopt the same workflow.

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

> **Conclusion:** The scoreboard in "lowest conformance" mode is the maintainer's immediate triage queue: repos at the bottom need either a retroactive labelling pass or a workflow change to ensure new issues arrive with labels. Repos with both low conformance AND large open-issue counts are the highest combined priority.

## Label Co-Occurrence: Type X Severity

A matrix showing how often each issue type label appears together with each severity label. Expected pairings reflect the project's actual work pattern — if text-correction is almost always "minor," that is a convention, not a coincidence. Unexpected bright cells in positions that should be rare reveal either labelling inconsistencies or edge-case work that deserves explicit documentation in the taxonomy guide.

> **How to read:** Each cell is one type × severity combination; colour = count (darker = more issues). **Example 1:** "text-correction" × "minor" being the brightest cell is expected — most correction issues are targeted, self-contained fixes. **Example 2:** "bug" × "critical" appearing with very low count despite a large bug total suggests bugs are being filed conservatively; if maintainers believe more bugs are critical, the labelling convention needs updating.

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

> **Conclusion:** The co-occurrence matrix reveals the labelling conventions in practice across the org. Bright cells in expected positions confirm the taxonomy is being applied consistently. Unexpected bright cells identify either labelling inconsistencies to clean up or genuine edge cases that deserve an explicit convention note in the taxonomy documentation.

[Back to overview](/)
