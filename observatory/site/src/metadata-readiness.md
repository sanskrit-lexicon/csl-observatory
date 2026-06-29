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

Each active repository receives a metadata score based on how many of eight standard fields are confirmed present: README, citation file, issue template, PR template, GitHub Actions workflows, Dependabot, CodeQL, and formal releases. The histogram shows how scores are distributed — whether repos cluster at the high end (most fields present) or whether the distribution spreads thin across many partial states.

> **How to read:** Each bar is one score value; colour codes the tier: green ≥ 8 (near-complete metadata), amber ≥ 5 (partial), red < 5 (sparse). **Example 1:** A peak at score 2–3 means most repos have only a README and description — the minimum bare-bones metadata, with no automation, templates, or citation file. **Example 2:** A peak at 7–8 means most repos are well-documented — unusual for a volunteer-driven digital-humanities project and worth noting as a baseline to defend.

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

> **Conclusion:** A left-skewed distribution (low scores dominant) is expected for a project whose primary focus has been dictionary correction rather than software-engineering best practices. The score histogram sets the baseline: any score improvement after a metadata campaign is measurable here. Citation and automation fields are typically the last to be addressed and contribute most to low scores.

## Unknown Field Blocker Breakdown

"Unknown" values appear when a metadata field cannot be determined from the current data snapshot — either because it requires a live GitHub API call that failed during collection, or because the value is inherited from an org-level template and cannot be confirmed without a direct tree fetch. This chart ranks those blockers by frequency, showing which fields have the most unresolved unknowns and therefore the most uncertain coverage data.

> **How to read:** Each bar is one field name; length = the number of repos where that field's value is still "unknown" in the current snapshot. **Example 1:** A long bar for "Workflows" means many repos' CI status could not be confirmed — typically because the GitHub Actions API was unavailable during data collection, not because workflows are absent. **Example 2:** A near-zero bar for "README" means almost all repos have confirmed README status — a sign that this particular field is reliably captured in every snapshot.

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

> **Conclusion:** Unknown blockers are a data-quality problem, not necessarily a repo-quality problem. Before acting on "unknown" values, run a live snapshot refresh. If unknowns persist after a refresh, they indicate repos where the field genuinely cannot be determined — an explicit policy decision is then needed.

## Fetch Warning Type Breakdown

When the metadata snapshot could not retrieve a live value for a repository, it stores a warning categorising why: a tree-lookup failure (file structure not returned), a release-API failure, offline mode (no GitHub credentials), or cache-only results. A large "none" bar means the snapshot is complete; large warning bars mean data coverage is partial and the other charts on this page have inflated "unknown" counts.

> **How to read:** Each bar is one warning type; length = repos with that warning. "none" (green) means the fetch completed cleanly. **Example 1:** A large "tree lookup" bar means many repos' file-tree data (README, citation, templates) could not be confirmed — the unknown-blocker chart above will show correspondingly large bars for those fields. **Example 2:** An "offline" bar means those repos were processed with no live GitHub connectivity — their entire metadata is from a prior cached snapshot and should not be treated as current.

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

> **Conclusion:** Fetch warnings set the confidence bound for every other metric on this page. A low-warning snapshot is high-confidence; a high-warning snapshot means the "unknown" values in other charts reflect data-collection failures rather than confirmed absences. Resolve by re-running the snapshot with live GitHub credentials.

## Automation Maturity

Three CI automation signals — GitHub Actions workflows, Dependabot dependency updates, and CodeQL security scanning — are each either present, absent, or undetermined for every active repository. Most repos in this org predate widespread CI adoption in digital humanities; Dependabot and CodeQL are more recent practices. The chart shows how far the org has progressed on each dimension and where the automation gaps remain.

> **How to read:** Each row is one automation category; bars stack green (yes), red (no), amber (unknown). **Example 1:** If "Workflows" shows most repos as "no," the org has very little CI automation — corrections are applied and pushed without any automated testing gate. **Example 2:** A large "unknown" segment for "CodeQL" means the security scanning status cannot be confirmed from the current snapshot — rerun with live credentials before assuming it is absent.

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

> **Conclusion:** Low automation maturity is expected given the project's age and humanities focus. However, the absence of Dependabot across most repos means security patches arrive only when a maintainer notices them manually. For web-facing repos (csl-websanlexicon, csl-apidev), this is a concrete, addressable security gap that Dependabot configuration would close in one step per repo.

## Release Readiness By License Class

Formal GitHub releases (versioned tags with release notes) matter for citation: a stable versioned snapshot with a Zenodo DOI is the preferred citation target for a scholarly resource. This chart cross-tabulates release presence against license class to show whether the most legally clear repos are also the ones that have taken the extra step of making a citable versioned release.

> **How to read:** Each column is a license class; bars stack by release status — green (has release), red (no release), amber (unknown). **Example 1:** A tall red segment under "recognised" means repos have valid licenses but no formal releases — they are legally reusable but not yet citable via a stable version. **Example 2:** A "has release" segment under "none" is a licensing inconsistency: the repo has been versioned for release but carries no license — reusers have no legal clarity on whether they may build on it.

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

> **Conclusion:** If most licensed repos also lack releases, the org has completed the first prerequisite for scholarly citability (licensing) but not the second (stable versioned snapshots). The next step is creating tagged releases for the primary data repos and minting Zenodo DOIs — the action tracked in the Data page's citation section.

[Back to overview](/)
