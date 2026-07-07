---
title: Org Shape
toc: true
---

<link rel="stylesheet" href="./palette.css">

# Org Shape

The organization's labor map and weekly trajectory: who works where across the 78 sanskrit-lexicon repositories, how specialised each contributor is, and how the org-level backlog moves between weekly snapshots. Contributor tables were computed 2026-06 from the full commit history; snapshots accrue weekly via the refresh workflow. The inferential companions are hypotheses H4 and H7 in the Phase-3 spec.

```js
const heatmap = await FileAttachment("data/contributor_repo_heatmap.csv").csv({typed: true});
const specialisation = await FileAttachment("data/contributor_specialisation.csv").csv({typed: true});
const drift = await FileAttachment("data/snapshot_drift.csv").csv({typed: true});
```

```js
// Chart colors come from palette.css tokens (light + dark), never hard-coded here.
const paletteStyles = getComputedStyle(document.documentElement);
const token = (name) => paletteStyles.getPropertyValue(name).trim();
const OBS_ACCENT = token("--obs-accent");
const OBS_MUTED = token("--obs-muted");
const OBS_GOOD = token("--obs-good");
const OBS_WARN = token("--obs-warn");
const OBS_BAD = token("--obs-bad");
const OBS_SEQ = [1, 2, 3, 4, 5, 6, 7].map((i) => token(`--obs-seq-${i}`));
const seqInterpolate = d3.piecewise(d3.interpolateRgb, OBS_SEQ);
```

## Contributor × Repository Heatmap

The org's labor map: every contributor (rows) against every repository they have committed to (columns), grouped into repo families. Computed in June 2026 from the full commit history and never rendered until now.

> **How to read:** Row = contributor login; column = repository, grouped by family panel; colour = commit count on a log scale. **Example 1:** A row lighting up across an entire family panel is a family owner — one person maintaining a whole class of repos. **Example 2:** A column with several coloured rows is a shared repo — the closest thing the org has to a commons; a column with exactly one row is a single-maintainer repo, the bus-factor surface.

```js
const loginOrder = Array.from(
  d3.rollup(heatmap, (v) => d3.sum(v, (d) => d.commits), (d) => d.login),
  ([login, commits]) => ({login, commits})
).sort((a, b) => b.commits - a.commits).map((d) => d.login);
// repos grouped by family (alphabetical), then by total commits within each family
const repoFamily = new Map(heatmap.map((d) => [d.repo, d.family]));
const repoOrder = Array.from(
  d3.rollup(heatmap, (v) => d3.sum(v, (d) => d.commits), (d) => d.repo),
  ([repo, commits]) => ({repo, commits, family: repoFamily.get(repo)})
).sort((a, b) => d3.ascending(a.family, b.family) || b.commits - a.commits).map((d) => d.repo);

display(Plot.plot({
  width,
  height: 480,
  marginLeft: 110,
  marginBottom: 90,
  x: {label: "Repository (grouped by family)", domain: repoOrder, tickRotate: -60, tickFormat: (d) => (d.length > 14 ? d.slice(0, 13) + "…" : d)},
  y: {label: null, domain: loginOrder},
  color: {type: "log", interpolate: seqInterpolate, legend: true, label: "Commits (log)"},
  marks: [
    Plot.cell(heatmap, {x: "repo", y: "login", fill: "commits", tip: true, channels: {Family: "family"}})
  ]
}))
```

> **Conclusion:** The map shows where the org's 13 years of commits actually landed: a dense two-row core (`funderburkjim`, `drdhaval2785`) spanning nearly every family, a handful of family-scoped contributors, and a long tail of single-repo participants. Columns with a single coloured cell are the repos that stop moving if one person does.

## Specialisation Index

Companion to hypothesis H4: is the org run by generalists or specialists? Normalized entropy of each contributor's commit distribution across repos — 0 means all commits in one repo (pure specialist), 1 means commits spread evenly over every repo they touch (pure generalist).

> **How to read:** Each dot is one contributor; x = normalized entropy, dot size = total commits, colour = the repo family holding the largest share of their work. **Example 1:** A large dot at high entropy is a high-volume generalist — the org's infrastructure depends on their breadth. **Example 2:** A small dot near 0 is a focused contributor whose entire output lives in one repository.

```js
const specSorted = specialisation.slice().sort((a, b) => b.normalized_entropy - a.normalized_entropy);

display(Plot.plot({
  width,
  height: 420,
  marginLeft: 130,
  x: {label: "Normalized entropy (0 = specialist, 1 = generalist)", domain: [0, 1], grid: true},
  y: {label: null, domain: specSorted.map((d) => d.login)},
  color: {legend: true, scheme: "Tableau10", label: "Dominant family"},
  r: {range: [3, 16]},
  marks: [
    Plot.dot(specSorted, {
      x: "normalized_entropy", y: "login", r: "total_commits",
      fill: "dominant_family", fillOpacity: 0.85, tip: true,
      channels: {Commits: "total_commits", Repos: "n_repos", "Top repo": "top_repo"}
    })
  ]
}))
```

> **Conclusion:** The org runs on generalists: the highest-volume contributors sit at high entropy (Jim Funderburk at 0.69 across 58 repos, Dhaval Patel at 0.78 across 39), while true specialists are low-volume. That is H4's picture — labor is concentrated in people, not confined to repos — and it means the org's knowledge is portable across repos but not across people.

## Dominant-Family Capture

How captured each contributor is by a single repo family: the share of their commits in their dominant family. The 0.5 rule marks the majority line — right of it, more than half of a contributor's work lives in one family.

> **How to read:** Bar length = share of the contributor's commits in their dominant family; colour = which family that is; the dashed rule marks 50%. **Example 1:** A bar near 1.0 is a contributor wholly captured by one family — their departure affects exactly one class of repos. **Example 2:** A bar just past 0.5 with high total commits is a broad contributor with a lean — invested in one family but active elsewhere.

```js
const captureSorted = specialisation.slice().sort((a, b) => b.dominant_family_share - a.dominant_family_share);

display(Plot.plot({
  width,
  height: 420,
  marginLeft: 130,
  x: {label: "Dominant-family share of commits", domain: [0, 1], grid: true},
  y: {label: null, domain: captureSorted.map((d) => d.login)},
  color: {legend: true, scheme: "Tableau10", label: "Dominant family"},
  marks: [
    Plot.ruleX([0.5], {stroke: OBS_MUTED, strokeDasharray: "4,3"}),
    Plot.barX(captureSorted, {
      x: "dominant_family_share", y: "login", fill: "dominant_family",
      tip: true, channels: {Commits: "total_commits", "Family commits": "dominant_family_commits"}
    }),
    Plot.ruleX([0])
  ]
}))
```

> **Conclusion:** Most contributors sit right of the majority line — one family holds most of their work — but the core maintainers do not: their dominant-family share stays near 0.5–0.65 despite huge volume. Family capture is a property of the periphery; the center is diversified.

## Snapshot Drift

Companion to hypothesis H7: is the org backlog in steady state? Weekly snapshots of org-level totals, shown as percent change from the first snapshot so all four metrics share one scale. H7 is registered but deliberately underpowered at the current snapshot count — with only five weekly snapshots, Mann-Kendall trend tests cannot reach significance except for perfect monotone runs — so this view is descriptive until ≥ 10 snapshots accumulate.

> **How to read:** One panel per metric; x = snapshot date, y = percent change since the first snapshot. **Example 1:** A flat line at 0% is a metric in steady state — the H7 null holds descriptively. **Example 2:** A panel climbing week over week (e.g. total issues) means the backlog is growing faster than it is being drained.

```js
const parseSnap = (d) => ({...d, date: new Date(d.snapshot_date)});
const driftRows = drift.map(parseSnap);
const firstValue = new Map(
  Array.from(d3.group(driftRows, (d) => d.metric),
    ([metric, rows]) => [metric, rows.slice().sort((a, b) => a.date - b.date)[0].value])
);
const driftPct = driftRows.map((d) => ({
  ...d,
  pct: 100 * (d.value / firstValue.get(d.metric) - 1)
}));

display(Plot.plot({
  width,
  height: 420,
  x: {label: null, type: "utc"},
  y: {label: "% change since first snapshot", grid: true},
  fy: {label: null},
  marks: [
    Plot.ruleY([0], {stroke: OBS_MUTED, strokeDasharray: "4,3"}),
    Plot.line(driftPct, {x: "date", y: "pct", fy: "metric", stroke: OBS_ACCENT}),
    Plot.dot(driftPct, {x: "date", y: "pct", fy: "metric", fill: OBS_ACCENT, r: 3, tip: true, channels: {Value: "value"}})
  ]
}))
```

The same series in absolute counts (log scale, one line per metric):

```js
display(Plot.plot({
  width,
  height: 340,
  x: {label: null, type: "utc"},
  y: {label: "Count (log)", type: "log", grid: true},
  color: {legend: true, scheme: "Tableau10"},
  marks: [
    Plot.line(driftRows, {x: "date", y: "value", stroke: "metric"}),
    Plot.dot(driftRows, {x: "date", y: "value", fill: "metric", r: 3, tip: true})
  ]
}))
```

> **Conclusion:** Until now the weekly snapshots existed only as a text digest; this is their first rendering. Movements so far are small — consistent with the steady-state null of H7 — but the verdict is explicitly deferred until enough snapshots accumulate for the registered Mann-Kendall test to have power.

## Backlog Composition

Whether the backlog is aging in place or churning: the open-issue vs open-PR composition of the backlog per snapshot. A stable split with rising totals means items accumulate without being recycled; a shifting split means one queue is being drained into the other.

> **How to read:** Each line is one backlog component's share of the combined issue+PR backlog; x = snapshot date, y = share. **Example 1:** A flat issue-share line near 98% means the backlog's composition is frozen — issues dominate and nothing structural is changing week to week. **Example 2:** A dropping PR-share line means pull requests are being merged or closed faster than new ones arrive, while the issue mountain stays.

```js
const bySnap = d3.group(driftRows.filter((d) => d.metric === "total_issues" || d.metric === "total_pull_requests"), (d) => d.snapshot_date);
const composition = Array.from(bySnap, ([snapshot_date, rows]) => {
  const issues = rows.find((d) => d.metric === "total_issues")?.value ?? 0;
  const prs = rows.find((d) => d.metric === "total_pull_requests")?.value ?? 0;
  const total = issues + prs;
  return [
    {date: new Date(snapshot_date), component: "issues", share: issues / total, count: issues},
    {date: new Date(snapshot_date), component: "pull requests", share: prs / total, count: prs}
  ];
}).flat();

display(Plot.plot({
  width,
  height: 340,
  x: {label: null, type: "utc"},
  y: {label: "Share of open backlog", type: "log", grid: true, tickFormat: ".1%"},
  color: {legend: true, domain: ["issues", "pull requests"], range: [OBS_ACCENT, OBS_WARN]},
  marks: [
    Plot.line(composition, {x: "date", y: "share", stroke: "component"}),
    Plot.dot(composition, {x: "date", y: "share", fill: "component", r: 3, tip: true, channels: {Count: "count"}})
  ]
}))
```

> **Conclusion:** The backlog is overwhelmingly issues (~98% of open items), and that split barely moves between snapshots: the org's backlog ages in place rather than churning. Combined with the drift panels above, the picture is a stable, slowly growing issue mountain tended by a small, diversified core — the org-shape context in which the correction labor of the [Correction Anatomy](/correction-anatomy) page happens.

[Back to overview](/)
