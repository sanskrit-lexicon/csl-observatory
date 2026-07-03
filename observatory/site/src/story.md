---
title: Thirteen years, one scroll — the story of the Cologne corrections
toc: false
---

# Thirteen years, one scroll

_The Cologne Digital Sanskrit Lexicon (CDSL) was not built in a grant cycle. It was built in the open, one correction at a time, by a handful of volunteers over thirteen years. This page tells that story from the record the work itself left behind — every dictionary edit, every issue, every commit — with the numbers embedded rather than filed away in a dashboard. Read it start to finish; it takes about five minutes._

```js
const velocity = await FileAttachment("data/velocity_timeline.csv").csv({typed: true});
// Per-year/layer/component correction counts (78 rows) — sums to the same
// 52,498 total as the event-level dataset, but keeps this page light enough to send.
const correctionTimeline = await FileAttachment("data/obs_t_timeline.csv").csv({typed: true});
const survival = await FileAttachment("data/issue_lifecycle_survival.csv").csv({typed: true});
const backlog = await FileAttachment("data/issue_lifecycle_backlog.csv").csv({typed: true});
const identity = await FileAttachment("data/contributor_identity.csv").csv({typed: true});
const repoHealth = await FileAttachment("data/repo_health.csv").csv({typed: true});
const taxonomy = await FileAttachment("data/taxonomy_adoption.csv").csv({typed: true});
const obsT = await FileAttachment("data/obs_t_summary.json").json();
const manifest = await FileAttachment("data/manifest.json").json();
```

```js
// All narrative figures are computed live from the committed datasets, so every
// number below is traceable to a downloadable CSV/JSON on the Data page.
const totalCorrections = obsT.events;
const nDicts = obsT.dictionaries;
const nCorrectors = obsT.correctors;
const spanStart = obsT.dateRange[0];
const spanEnd = obsT.dateRange[1];

// Corrections per calendar year, summed from the per-layer timeline.
const corrPerYear = d3.rollups(correctionTimeline, v => d3.sum(v, d => d.count), d => d.year)
  .map(([year, count]) => ({year, count}))
  .sort((a, b) => a.year - b.year);

// Backlog (open issues carried into each year) and breadth (distinct authors).
const backlogByYear = velocity.map(d => ({year: d.year, open: d.cumulative_open, authors: d.active_authors}));
const peakAuthorsRow = velocity.reduce((a, b) => b.active_authors > a.active_authors ? b : a);
const backlogPeakRow = velocity.reduce((a, b) => b.cumulative_open > a.cumulative_open ? b : a);
const row2019 = velocity.find(d => d.year === 2019);
const row2025 = velocity.find(d => d.year === 2025);
const row2026 = velocity.find(d => d.year === 2026);

// Concentration: the single largest contributor's share of all recorded work.
const contribTotal = d3.sum(identity, d => d.contributions);
const topPerson = identity.reduce((a, b) => b.contributions > a.contributions ? b : a);
const topShare = topPerson.contributions / contribTotal;

// Silence: open issues that never received a single reply, across all age buckets.
const silentTotal = d3.sum(backlog, d => d.silent);

// Survival: the 2014 cohort's share still open four years (1460 days) on.
const cohort2014_4yr = survival.find(d => d.cohort === 2014 && d.horizon_days === 1460);

// Licensing: repos still carrying no license, after the RH1 rollout.
const noLicense = repoHealth.filter(d => d.license_class === "none").length;

// Taxonomy conformance, org-wide, all years pooled.
const conformShare = d3.sum(taxonomy, d => d.conformant) / d3.sum(taxonomy, d => d.issues);
```

Between **${spanStart}** and **${spanEnd}**, the project logged **${totalCorrections.toLocaleString()}** individual, reconstructable corrections to **${nDicts}** dictionaries — a public ledger of philological repair with no real parallel in Sanskrit lexicography. This is what those thirteen years look like.

<div class="grid grid-cols-3">
  <div class="card">
    <h2>Corrections recorded</h2>
    <span class="big">${totalCorrections.toLocaleString()}</span>
    <span class="muted">${spanStart.slice(0,4)}–${spanEnd.slice(0,4)}</span>
  </div>
  <div class="card">
    <h2>Dictionaries touched</h2>
    <span class="big">${nDicts}</span>
    <span class="muted">from Apte to Böhtlingk-Roth</span>
  </div>
  <div class="card">
    <h2>Hands on the work</h2>
    <span class="big">${nCorrectors}</span>
    <span class="muted">correctors over 13 years</span>
  </div>
</div>

## The spine: a backlog that tells the whole story

The single most honest summary of the project's history is the shape of its open-issue backlog — the count of unresolved issues carried into each year. It rises through the campaign years, holds, and then, in 2026, drops sharply as the taxonomy-and-observatory era brings the ledger under active management. Every turning point in the prose below is a bend in this one line.

```js
Plot.plot({
  width,
  height: 300,
  marginLeft: 50,
  x: {label: "Year", tickFormat: "d"},
  y: {label: "Open issues carried into year", grid: true},
  marks: [
    Plot.areaY(backlogByYear, {x: "year", y: "open", fill: "#3a5f7d", fillOpacity: 0.12, curve: "monotone-x"}),
    Plot.lineY(backlogByYear, {x: "year", y: "open", stroke: "#3a5f7d", strokeWidth: 2, curve: "monotone-x"}),
    Plot.dot(backlogByYear, {x: "year", y: "open", fill: "#3a5f7d", r: 2.5}),
    Plot.text([backlogPeakRow], {x: "year", y: "cumulative_open", text: d => `2025 peak: ${d.cumulative_open.toLocaleString()}`, dy: -12, fontWeight: 600, fill: "#b03a2e"}),
    Plot.text([row2026], {x: "year", y: "cumulative_open", text: d => `2026: ${d.cumulative_open.toLocaleString()}`, dy: -12, dx: 4, fontWeight: 600, fill: "#1a7f37"}),
    Plot.ruleY([0])
  ]
})
```

> **What this proves:** the project has always generated far more work than any small team could close, and the backlog is the accumulated evidence. What changed in 2026 is not that the work got smaller — it is that the org finally began measuring and draining it.

## 2014–2016 · Founding, and the correction ledger

The project's first act was pure text repair. Before there was a git workflow, there was `cfr.tsv` — a flat form-correction file into which volunteers poured fixes to OCR and transcription errors in the scanned dictionary text: a `ṭ` read as `द`, a dropped conjunct, a mis-segmented compound. These are the **form-layer** corrections, and they dominate the early years: the correction ledger peaks in **2015–2016**, before the project had any of the machinery it later built.

```js
Plot.plot({
  width,
  height: 220,
  marginLeft: 50,
  x: {label: "Year", tickFormat: "d"},
  y: {label: "Corrections recorded", grid: true},
  marks: [
    Plot.barY(corrPerYear, {x: "year", y: "count", fill: d => d.year <= 2016 ? "#8a6d3b" : "#c9c2b6", tip: true}),
    Plot.ruleY([0])
  ]
})
```

> **What this proves:** the founding era was not about infrastructure or display — it was about getting the text right. The gold-brown bars (2014–2016) are the `cfr.tsv` form-correction era; everything after is the project working through the same dictionaries again with better tools.

## 2019 · Git arrives

For its first five years the project's corrections lived in flat files and hand-edited text. **2019 is the year the pull request appears** — the first PRs in the org's history are recorded here, and the number of distinct people active in a year jumps to **${row2019.active_authors}**. This is the quiet inflection: the moment a personal correction practice became a reviewable, git-native workflow that a newcomer could join.

## 2021 · The volume peak

If any single year was the project at full stretch, it was **${peakAuthorsRow.year}**: **${peakAuthorsRow.active_authors}** distinct authors active — the widest the contributor base has ever been — and **${peakAuthorsRow.commits.toLocaleString()}** commits, more than any year before it. The correction ledger surges again as the git-era workflow lets several dictionaries be reworked in parallel.

<div class="grid grid-cols-3">
  <div class="card">
    <h2>Peak breadth (${peakAuthorsRow.year})</h2>
    <span class="big">${peakAuthorsRow.active_authors}</span>
    <span class="muted">distinct active authors</span>
  </div>
  <div class="card">
    <h2>Commits that year</h2>
    <span class="big">${peakAuthorsRow.commits.toLocaleString()}</span>
    <span class="muted">an all-time high</span>
  </div>
  <div class="card">
    <h2>Issues opened</h2>
    <span class="big">${peakAuthorsRow.issues_opened.toLocaleString()}</span>
    <span class="muted">campaign in full flow</span>
  </div>
</div>

> **What this proves:** the project's ceiling is a dozen people, not a hundred. Even at its most active it was a small circle working intensively — an important fact when reading everything that follows about concentration and continuity.

## 2025 · The correction wave, and the reckoning

**2025** is the year the backlog crested. Issues were opened in bulk — **${row2025.issues_opened.toLocaleString()}** of them, far more than any prior year — largely as a tracking mechanism for a fresh correction campaign, while closings lagged. The open-issue count carried into the next year reached its all-time high of **${backlogPeakRow.cumulative_open.toLocaleString()}**. The project had, in effect, catalogued how much unfinished work it was actually carrying.

## 2026 · Taxonomy, and the observatory

The response was to start measuring. **2026** is the taxonomy-and-observatory era: a shared issue taxonomy pushed org-wide (pooled conformance now **${(conformShare * 100).toFixed(0)}%**), and closings finally outpacing openings — **${row2026.issues_closed.toLocaleString()}** issues closed against **${row2026.issues_opened.toLocaleString()}** opened — dropping the backlog from its 1,742 peak to **${row2026.cumulative_open.toLocaleString()}**. This observatory is itself a product of that era: the project turning its own thirteen-year record into citable, reproducible data.

---

The arc above is the encouraging reading. But the same record carries four harder facts, and an honest story has to state them.

## The work rests on one person

Across all thirteen years, a single contributor — **${topPerson.real_name}** — accounts for **${(topShare * 100).toFixed(0)}%** of every recorded contribution in the organisation. That is not a criticism of anyone; it is a structural risk. A project this concentrated is one departure away from stalling, and no amount of tooling changes that. It is the first thing a would-be funder, host institution, or successor needs to know. [Community analysis →](/community)

## Most of the backlog was never answered

Of the open issues still on the books, **${silentTotal}** have never received a single reply — not a triage label, not a comment, nothing. Silence, not disagreement, is the dominant failure mode: work is filed and then quietly outlives everyone's attention. The backlog is not a queue being worked down in order; it is a sediment, and most of it has never been touched since the day it was opened. [Issue lifecycle →](/lifecycle)

## Issues that survive early tend to survive forever

The **2014** cohort makes the point starkly: **${cohort2014_4yr.pct_open}%** of the issues opened that year were *still open four years later*. Once an issue clears its first weeks unresolved, its odds of ever being closed collapse. This is why the ${silentTotal}-issue silence matters — the backlog does not decay on its own; unattended issues become permanent.

```js
Plot.plot({
  width,
  height: 220,
  marginLeft: 50,
  x: {label: "Days after opening", type: "log", domain: [30, 1460], ticks: [30, 90, 180, 365, 730, 1460], tickFormat: d => d >= 365 ? `${Math.round(d/365)}y` : `${d}d`},
  y: {label: "Still open (%)", domain: [0, 100], grid: true},
  marks: [
    Plot.lineY(survival.filter(d => d.cohort === 2014), {x: "horizon_days", y: "pct_open", stroke: "#b03a2e", strokeWidth: 2, marker: "circle"}),
    Plot.ruleY([0])
  ]
})
```

> **What this proves:** the 2014 cohort's survival curve flattens well above zero — it never approaches full resolution. An issue's fate is largely sealed in its first months.

## One thing did get fixed: licensing

The record is not only decline. When the observatory surfaced that **41** of the org's repositories carried no license at all — a FAIR-reuse violation that made the data legally unsafe to build on — the project acted. After the RH1 license rollout, only **${noLicense}** repositories remain unlicensed, and those are the archive candidates intentionally held back for a separate cleanup. A measured problem became a closed one. [Repository health →](/repo-health)

> **What this proves:** the observatory is not a mirror the project looks into and sighs at — the licensing repair (41 → ${noLicense}) is the template. Surface a fact, act on it, re-measure. That is the loop this whole site exists to enable.

## Where a new contributor starts

If this story leaves you wanting to help rather than only to cite, the most valuable thing you can do is the least glamorous: **answer a silent issue.** The ${silentTotal} never-answered open issues are where a single reply — a triage label, a clarifying question, a "this is fixed" — has the highest marginal value in the entire organisation.

- **Triage the silence** — the [Issue Lifecycle](/lifecycle) and [Taxonomy Triage](/taxonomy-triage) pages surface the unanswered and unlabelled backlog, repo by repo.
- **See where the work is** — the [Ops Command](/ops-command) view ranks repositories by open pressure and metadata blockers, so a first contribution lands where it counts.
- **Reuse the data** — every figure on this page is downloadable from the [Data](/data) page under CC-BY-4.0; the [error-typology corpus](/error-typology) is a published language resource in its own right.

Thirteen years of one small circle's careful work are now legible, citable, and open. The next chapter is whether that circle widens.

---

*Every figure on this page is computed live from the committed datasets — snapshot **${manifest.snapshot_date}**, refreshed monthly from the GitHub API and the public correction record. Nothing is hand-typed; download the underlying CSV/JSON from the [Data](/data) page to check any number here.*

<style>
.card .big { font-size: 2.1rem; font-weight: 600; display: block; line-height: 1.1; }
.card .muted { font-size: 0.8rem; opacity: 0.65; display: block; margin-top: 0.15rem; }
</style>
