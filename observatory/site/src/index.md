---
title: CSL Observatory — overview
toc: false
---

# CSL Observatory

**A living, fully-open measurement of the [Cologne Digital Sanskrit Lexicon](https://www.sanskrit-lexicon.uni-koeln.de/)** — 13 years of volunteer work digitising and correcting the foundational Sanskrit dictionaries, turned into citable, reproducible data. Every figure below is computed live from datasets you can [download and reuse](/data); nothing here is hand-typed.

```js
const annual = await FileAttachment("data/timeseries_annual.csv").csv({typed: true});
const repos = await FileAttachment("data/repos.csv").csv({typed: true});
const typology = await FileAttachment("data/issue_typology_annual.csv").csv({typed: true});
const contributors = await FileAttachment("data/contributors.csv").csv({typed: true});
const busFactor = await FileAttachment("data/bus_factor.csv").csv({typed: true});
const repoHealth = await FileAttachment("data/repo_health.csv").csv({typed: true});
const taxonomy = await FileAttachment("data/taxonomy_adoption.csv").csv({typed: true});
const velocity = await FileAttachment("data/velocity_timeline.csv").csv({typed: true});
const manifest = await FileAttachment("data/manifest.json").json();
const obsT = await FileAttachment("data/obs_t_summary.json").json();

// One canonical "human contributor" definition, matching reports/contributor_identity.md
// (16): exclude type=Bot, [bot]-suffixed logins, and service accounts like actions-user.
const isHuman = (d) => d.type !== "Bot" && !/\[bot\]$/.test(d.login) && !["actions-user", "github-actions"].includes(d.login);
const humanLogins = new Set(contributors.filter(isHuman).map(d => d.login));
```

<div class="grid grid-cols-4">
  <div class="card">
    <h2>Repos tracked</h2>
    <span class="big">${repos.length}</span>
  </div>
  <div class="card">
    <h2>Total issues+PRs</h2>
    <span class="big">${d3.sum(annual, d => d.issues_opened + d.prs_opened).toLocaleString()}</span>
  </div>
  <div class="card">
    <h2>Total commits</h2>
    <span class="big">${d3.sum(annual, d => d.commits).toLocaleString()}</span>
  </div>
  <div class="card">
    <h2>Human contributors</h2>
    <span class="big">${humanLogins.size}</span>
  </div>
</div>

## Key findings

```js
const humans = contributors.filter(isHuman);
const personTotal = d3.rollup(humans, v => d3.sum(v, x => x.contributions), d => d.login);
const grand = d3.sum(personTotal.values());
const coreShare = d3.sum(["funderburkjim", "drdhaval2785", "gasyoun"], l => personTotal.get(l) || 0) / grand;
const bf1 = busFactor.filter(d => d.bus_factor === 1).length;
const noLicense = repoHealth.filter(d => d.license_class === "none").length;
const conformant = d3.sum(taxonomy, d => d.conformant) / d3.sum(taxonomy, d => d.issues);
const peakAuthors = d3.max(velocity, d => d.active_authors);
```

Across 13 years and ${repos.length} repositories, a small, dedicated team has logged tens of thousands of dictionary corrections entirely in the open — and the [error-typology study](/error-typology) turns ${obsT.events.toLocaleString()} of them, across ${obsT.dictionaries} dictionaries, into a published, reusable language resource. Four offline, reproducible analyses describe the organisation behind that work: productive, well-governed, and actively maintained — though carried by a tiny core and still thin on reuse metadata. Full write-up: [synthesis report](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/reports/synthesis.md).

- **Concentration** — the core trio carries **${(coreShare * 100).toFixed(0)}%** of all contributions, and **${bf1} of ${busFactor.length}** repos have a bus factor of 1. [Community →](/community)
- **Activity** — thousands of commits, yet the busiest year drew only **${peakAuthors}** distinct authors: volume-per-person, not a growing base. [Activity →](/activity)
- **Process** — **${(conformant * 100).toFixed(0)}%** of issues are fully taxonomy-conformant, after adoption climbed to a 92% peak in 2025. [Issue taxonomy →](/coverage)
- **Hygiene** — **${noLicense} of ${repoHealth.length}** repos carry no license, and no contributor has a registered ORCID. [Repo health →](/repo-health)

## Lead figure: How the work changed over 13 years

Stacked-area chart of issue typology by year. Watch `text-correction` dominate; see the rise of `link-target`, `markup`, and (recently) `bug` / `enhancement` as the project matured.

```js
Plot.plot({
  title: "Issues created per year, by type label",
  width,
  height: 400,
  marginLeft: 60,
  x: {label: "Year", tickFormat: ""},
  y: {label: "Issues created"},
  color: {legend: true, scheme: "tableau10"},
  marks: [
    Plot.areaY(typology, {x: "year", y: "count", fill: "type_label", curve: "monotone-x", tip: true}),
    Plot.ruleY([0])
  ]
})
```

## Annual throughput

```js
Plot.plot({
  title: "Issues opened vs. closed per year",
  width,
  height: 350,
  x: {label: "Year"},
  y: {label: "Count"},
  color: {legend: true, domain: ["issues_opened", "issues_closed"], range: ["#0075ca", "#1a7f37"]},
  marks: [
    Plot.barY(d3.flatRollup(annual, v => d3.sum(v, x => x.issues_opened), d => d.year).map(([year, c]) => ({year, kind: "issues_opened", count: c})), {x: "year", y: "count", fill: "kind", dx: -8, insetLeft: 1, insetRight: 1}),
    Plot.barY(d3.flatRollup(annual, v => d3.sum(v, x => x.issues_closed), d => d.year).map(([year, c]) => ({year, kind: "issues_closed", count: c})), {x: "year", y: "count", fill: "kind", dx: 8, insetLeft: 1, insetRight: 1}),
    Plot.ruleY([0])
  ]
})
```

## Top 10 most active repositories (all-time)

```js
const repoActivity = d3.flatRollup(annual, v => d3.sum(v, x => x.issues_opened + x.prs_opened + x.commits), d => d.repo)
  .map(([repo, total]) => ({repo, total}))
  .sort((a, b) => b.total - a.total)
  .slice(0, 10);
```

```js
Plot.plot({
  title: "Top 10 repos by lifetime activity",
  width,
  height: 350,
  marginLeft: 140,
  x: {label: "Issues + PRs + commits (all-time)"},
  y: {label: null, domain: repoActivity.map(d => d.repo)},
  marks: [
    Plot.barX(repoActivity, {x: "total", y: "repo", fill: "#0075ca", tip: true}),
    Plot.ruleX([0])
  ]
})
```

## Navigation

- [**Ops Command**](/ops-command) - maintainer operating dashboard across blockers, issue pressure, metadata, and bus factor
- [**Activity**](/activity) — issue/commit/PR throughput timelines, heatmaps, GitHub-style year grids
- [**OBS-T Maintenance**](/obs-t-maintenance) - light operational checks for the correction typology release
- [**Issue taxonomy**](/coverage) — GitHub issue and PR label patterns by repo
- [**Taxonomy Triage**](/taxonomy-triage) - label quality, conformance, and open issue triage views
- [**Community**](/community) — contributor growth, retention, bus-factor analysis
- [**Community Continuity**](/community-continuity) - maintainer concentration, retention, and identity readiness
- [**Repository Health**](/repo-health) — licensing, default-branch, and hygiene audit
- [**Repository Risk**](/repository-risk) - deeper license, branch, flag, size, and cleanup-risk charts
- [**Metadata Readiness**](/metadata-readiness) - B3 documentation, automation, release, and unknown-field blockers
- [**Tech Stack**](/tech-stack) — language evolution, dependency graphs, runbook adoption
- [**Repository Benchmarks**](/benchmarks) — project-level openness and repository evidence
- [**Data**](/data) — raw downloads (CSV, JSON, Parquet) for reproducibility

## About & how to cite

The observatory is an open-source project of the [sanskrit-lexicon](https://github.com/sanskrit-lexicon) organisation, part of the [Cologne Digital Sanskrit Dictionaries](https://www.sanskrit-lexicon.uni-koeln.de/) effort. It measures only the org's own GitHub activity — repositories, issues, commits, contributors — and the public correction record; the dictionary *content* itself lives in the upstream dictionary repos. Code and data are released under open licences (GPL-3.0 for code, CC-BY-4.0 for the datasets).

To cite the data, see [Data downloads → Citation](/data). The error-typology corpus has its own [datasheet](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/docs/DATASHEET.md).

---

*Data snapshot: **${manifest.snapshot_date}**, refreshed monthly from the GitHub API — see [how it's built](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/docs/OBSERVATORY_DESIGN.md) and [Data downloads](/data) for the exact figures.*

<style>
.card .big { font-size: 2rem; font-weight: 600; display: block; }
</style>
