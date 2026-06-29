---
title: Ops command center
toc: true
---

# Ops Command Center

Maintainer-first operating view across repository health, metadata blockers,
issue pressure, and bus-factor risk.

```js
const health = await FileAttachment("data/repo_health.csv").csv({typed: true});
const metadata = await FileAttachment("data/repo_metadata.csv").csv({typed: true});
const issues = await FileAttachment("data/issues.csv").csv({typed: true});
const busFactor = await FileAttachment("data/bus_factor.csv").csv({typed: true});
```

```js
const GREEN = "#1a7f37";
const AMBER = "#bf8700";
const RED = "#cf222e";
const BLUE = "#0969da";
const repoUrl = repo => `https://github.com/sanskrit-lexicon/${repo}`;
const splitPipe = value => String(value ?? "").split("|").map(d => d.trim()).filter(Boolean);
const unknownFlags = d => splitPipe(d.metadata_flags).filter(flag => flag.endsWith("-unknown"));
const healthByRepo = new Map(health.map(d => [d.repo, d]));
const metadataByRepo = new Map(metadata.map(d => [d.repo, d]));
const busByRepo = new Map(busFactor.map(d => [d.repo, d]));
const issueCounts = d3.rollup(issues, v => ({
  open: v.filter(d => d.state === "open").length,
  closed: v.filter(d => d.state === "closed").length,
  unlabeled_open: v.filter(d => d.state === "open" && !String(d.labels ?? "").trim()).length
}), d => d.repo);
const opsRows = Array.from(new Set([...health.map(d => d.repo), ...metadata.map(d => d.repo), ...busFactor.map(d => d.repo)])).map(repo => {
  const h = healthByRepo.get(repo) ?? {};
  const m = metadataByRepo.get(repo) ?? {};
  const b = busByRepo.get(repo) ?? {};
  const i = issueCounts.get(repo) ?? {open: 0, closed: 0, unlabeled_open: 0};
  const hygiene_flags = +h.flag_count || 0;
  const unknown_metadata = unknownFlags(m).length;
  const top_share = +b.top_share || 0;
  const bus_factor = +b.bus_factor || 0;
  const action_score = hygiene_flags * 3 + unknown_metadata * 2 + i.open + (bus_factor === 1 ? 4 : 0);
  return {repo, h, m, b, ...i, hygiene_flags, unknown_metadata, top_share, bus_factor, action_score};
});
```

<div class="grid grid-cols-4">
  <div class="card"><h2>Repos needing action</h2><span class="big">${opsRows.filter(d => d.action_score > 0).length}</span></div>
  <div class="card"><h2>Open issues</h2><span class="big">${d3.sum(opsRows, d => d.open).toLocaleString("en-US")}</span></div>
  <div class="card"><h2>Unknown metadata</h2><span class="big">${opsRows.filter(d => d.unknown_metadata).length}</span></div>
  <div class="card"><h2>Bus factor 1</h2><span class="big">${opsRows.filter(d => d.bus_factor === 1).length}</span></div>
</div>

## Risk Quadrant By Repo

Each repository is plotted as a dot combining two risk dimensions: open-issue pressure on the x-axis and a selectable second metric on the y-axis (hygiene flags, unknown metadata fields, or top contributor share). Dot size encodes the composite action score — a weighted sum of hygiene flags, metadata gaps, bus-factor penalty, and open issues. Red dots are highest priority: bus factor 1 with additional outstanding problems; green dots have at least two maintainers; amber covers repos whose bus-factor status is unknown.

> **How to read:** Each dot is one repository; x = open issues, y = the metric selected in the dropdown above, dot size = action score. Switch the y-axis to explore different risk combinations. **Example 1:** A large red dot in the upper-right corner has high open-issue pressure AND high risk on the y-axis AND bus factor 1 — the worst combination, highest priority for action. **Example 2:** A small green dot near the origin is low-priority: few issues, low hygiene risk, and at least two maintainers who could continue the work.

```js
const riskY = view(Inputs.select(["hygiene_flags", "unknown_metadata", "top_share"], {value: "hygiene_flags", label: "Y-axis risk metric"}));
```

```js
display(Plot.plot({
  width,
  height: 460,
  marginLeft: 60,
  x: {label: "Open issues", grid: true},
  y: {label: riskY.replace("_", " "), grid: true},
  color: {legend: true, domain: ["bus factor 1", "bus factor >= 2", "unknown"], range: [RED, GREEN, AMBER]},
  marks: [
    Plot.dot(opsRows, {
      x: "open",
      y: d => d[riskY],
      r: d => Math.max(3, Math.sqrt(d.action_score + 1) * 2),
      fill: d => d.bus_factor === 1 ? "bus factor 1" : d.bus_factor > 1 ? "bus factor >= 2" : "unknown",
      stroke: "white",
      tip: true,
      channels: {Repository: "repo", "Hygiene flags": "hygiene_flags", "Unknown metadata": "unknown_metadata", "Top share": "top_share"}
    })
  ]
}))
```

> **Conclusion:** The quadrant reveals which repos need attention on multiple fronts simultaneously. Repos in the upper-right are the highest-leverage targets; resolving their hygiene or bus-factor issues would have disproportionate impact on the org's overall risk profile.

## Blocker Mix By Category

A summary inventory of the org's current hygiene blockers by category — the single most condensed "to-do list" view in the observatory. Each bar shows how many repositories carry that specific problem. Because the categories span licensing, metadata, contributor risk, and issue quality, the chart guides where to direct effort across very different workstreams.

> **How to read:** Each bar is one blocker type; length = the number of repositories currently affected. **Example 1:** If "bus factor 1" is the longest bar, contributor concentration is more widespread than any licensing or branch issue — the priority is community-building, not cleanup scripts. **Example 2:** If "open unlabeled issues" shows a large count, that's a taxonomy-triage problem rather than a repository-health problem — the fix belongs in the coverage-page workflow, not here.

```js
const blockerMix = [
  {category: "no license", count: health.filter(d => d.license_class === "none").length},
  {category: "NOASSERTION", count: health.filter(d => d.license_class === "unrecognised").length},
  {category: "legacy branch", count: health.filter(d => d.default_branch === "master").length},
  {category: "metadata unknown", count: opsRows.filter(d => d.unknown_metadata).length},
  {category: "cleanup candidate", count: health.filter(d => splitPipe(d.flags).includes("cleanup-candidate")).length},
  {category: "bus factor 1", count: opsRows.filter(d => d.bus_factor === 1).length},
  {category: "open unlabeled issues", count: d3.sum(opsRows, d => d.unlabeled_open)}
];

display(Plot.plot({
  width,
  height: 320,
  marginLeft: 150,
  x: {label: "Count", grid: true},
  y: {label: null, domain: blockerMix.map(d => d.category)},
  marks: [
    Plot.barX(blockerMix, {x: "count", y: "category", fill: d => d.category.includes("unknown") ? AMBER : RED, tip: true}),
    Plot.ruleX([0])
  ]
}))
```

> **Conclusion:** The blocker mix is the dashboard's prioritisation compass. After the RH1 license rollout, the licensing bars should be short; the dominant remaining blockers are expected to be bus factor, legacy branch naming, and metadata unknowns — each requiring a different kind of intervention.

## Open Issue Pressure By License Class

Groups all open issues by the license class of the repository they live in. The goal is to see whether the active correction backlog sits in licensed or unlicensed repos. If unlicensed repos carry a disproportionate share of open issues, active scholarly correction work is happening in a legally ambiguous context — a combined hygiene-and-backlog risk that the RH1 rollout aimed to eliminate.

> **How to read:** Each bar is one license class; height = total open issues across all repos in that class. **Example 1:** A tall "recognised" bar is normal and expected — most active repos are now licensed and their backlog sits in a clear legal frame. **Example 2:** Any non-trivial height in the "none" bar means active correction campaigns are running in repos with no usage license — the highest-priority combination for the cleanup decision queue.

```js
const issuePressure = Array.from(
  d3.rollup(opsRows, v => d3.sum(v, d => d.open), d => d.h.license_class || "unknown"),
  ([license_class, open_issues]) => ({license_class, open_issues})
).sort((a, b) => b.open_issues - a.open_issues);

display(Plot.plot({
  width,
  height: 260,
  x: {label: "License class"},
  y: {label: "Open issues", grid: true},
  color: {domain: ["recognised", "unrecognised", "none", "unknown"], range: [GREEN, AMBER, RED, BLUE]},
  marks: [
    Plot.barY(issuePressure, {x: "license_class", y: "open_issues", fill: "license_class", tip: true}),
    Plot.ruleY([0])
  ]
}))
```

> **Conclusion:** After RH1, most open issues should sit in the "recognised" class. Any concentration in "none" or "unrecognised" identifies repos where active work is still happening without clear reuse rights — the most urgent overlap between hygiene and content priorities.

## Top Action Queues

The 20 repositories with the highest composite action score, sorted by urgency. The action score is a weighted index: hygiene flags contribute 3 points each, unknown metadata blockers 2 each, open issues 1 each, and bus factor 1 adds a flat penalty of 4. This single number captures a repo's urgency across all dimensions so maintainers can work a prioritised queue rather than scanning dozens of charts.

> **How to read:** Each bar is one repo; length = its composite action score. Amber bars are driven primarily by live-metadata unknowns; red bars by confirmed hygiene flags. **Example 1:** A long red bar means the repo has multiple confirmed hard flags AND a large open-issue backlog AND bus factor 1 — all problems at once, needing coordinated action. **Example 2:** A long amber bar may shrink after a live metadata refresh if the unknowns resolve to "yes" — always re-check amber-heavy repos against a current snapshot before acting.

```js
const topActions = opsRows.slice().sort((a, b) => b.action_score - a.action_score || d3.ascending(a.repo, b.repo)).slice(0, 20);

display(Plot.plot({
  width,
  height: 540,
  marginLeft: 150,
  x: {label: "Action score", grid: true},
  y: {label: null, domain: topActions.map(d => d.repo)},
  marks: [
    Plot.barX(topActions, {x: "action_score", y: "repo", fill: d => d.unknown_metadata ? AMBER : RED, tip: true, channels: {"Open issues": "open", "Hygiene flags": "hygiene_flags", "Unknown metadata": "unknown_metadata"}}),
    Plot.ruleX([0])
  ]
}))
```

> **Conclusion:** The top action queue is the maintainer's immediate triage list. Work from the top down: resolve amber bars first with a live refresh, then address confirmed red bars in order. Hovering on each bar shows the breakdown of issues, flags, and metadata gaps, making it actionable without leaving this page.

## Active Vs Clean Repo Matrix

A two-way matrix crossing each repo's default branch name against its hygiene status — clean (zero flags) or flagged. This tests whether legacy-branch repos and flagged repos are the same population or independent problems. If they are correlated, modernising the branch name and fixing hygiene tend to happen together; if they are independent, the branch rename can be targeted at a separate cohort.

> **How to read:** Each cell shows the count of repos in that branch × hygiene-status combination; darker colour = more repos. **Example 1:** A dark cell at ("master", "flagged") means most repos with the legacy branch name also have other outstanding flags — the two problems cluster and should be addressed together. **Example 2:** A bright cell at ("main", "clean") shows the modernised-and-clean population — the target state every repo should eventually reach.

```js
const cleanMatrix = Array.from(
  d3.rollup(opsRows, v => v.length, d => d.h.default_branch || "unknown", d => d.hygiene_flags === 0 ? "clean" : "flagged"),
  ([branch, inner]) => Array.from(inner, ([status, count]) => ({branch, status, count}))
).flat();

display(Plot.plot({
  width,
  height: 220,
  marginLeft: 90,
  x: {label: "Default branch"},
  y: {label: null},
  color: {scheme: "YlOrRd", legend: true, label: "Repos"},
  marks: [
    Plot.cell(cleanMatrix, {x: "branch", y: "status", fill: "count", tip: true}),
    Plot.text(cleanMatrix, {x: "branch", y: "status", text: "count", fill: "black"})
  ]
}))
```

> **Conclusion:** If "master"/"flagged" is the darkest cell, branch renaming and hygiene improvement are correlated — fixing one creates momentum for the other. If "master"/"clean" is also densely populated, branch naming is an isolated issue that a simple rename resolves without triggering any other hygiene work.

[Back to overview](/)
