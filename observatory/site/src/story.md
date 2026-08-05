---
title: Thirteen years, one scroll — the story of the Cologne corrections
toc: false
---

# Thirteen years, one scroll

_The Cologne Digital Sanskrit Lexicon (CDSL) began in 1994, two decades before its public GitHub record. This page tells the narrower story that the committed 2014–2026 correction and repository snapshots can support: documented dictionary edits, issues, and commits. Earlier institutional and email history requires different evidence. Read it start to finish; it takes about seven minutes, in two chapters: the thirteen-year arc, then the first fully-measured month under the observatory._

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

:::note
**Trust block.** Source: [`data/velocity_timeline.csv`](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/observatory/site/src/data/velocity_timeline.csv), a committed feed loaded at build time. **n = ${backlogByYear.length}** yearly rows, 2014–2026. Data date: snapshot ${manifest.snapshot_date}. Download: [`velocity_timeline.csv`](https://raw.githubusercontent.com/sanskrit-lexicon/csl-observatory/main/observatory/site/src/data/velocity_timeline.csv).
:::

**Data table (figure fallback).** ${Inputs.table(backlogByYear, {columns: ["year", "open", "authors"], header: {year: "Year", open: "Open issues carried in", authors: "Active authors"}, rows: 6})}

> **What this proves:** the project has always generated far more work than any small team could close, and the backlog is the accumulated evidence. What changed in 2026 is not that the work got smaller — it is that the org finally began measuring and draining it.

## 2014–2016 · The public correction ledger expands

The GitHub-era record opens with text repair, but this is not the project's founding: CDSL had already existed for twenty years. The inherited `cfr.tsv` form-correction file records fixes to transcription errors in the dictionary text: a `ṭ` read as `द`, a dropped conjunct, a mis-segmented compound. These are the **form-layer** corrections, and they dominate the early public ledger: the series peaks in **2015–2016**, before the later git-derived layer begins.

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

:::note
**Trust block.** Source: [`data/obs_t_timeline.csv`](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/observatory/site/src/data/obs_t_timeline.csv), a committed feed loaded at build time. **n = ${correctionTimeline.length}** year × layer × component rows, summing to ${totalCorrections.toLocaleString()} corrections. Data date: snapshot ${manifest.snapshot_date}. Download: [`obs_t_timeline.csv`](https://raw.githubusercontent.com/sanskrit-lexicon/csl-observatory/main/observatory/site/src/data/obs_t_timeline.csv).
:::

**Data table (figure fallback).** ${Inputs.table(corrPerYear, {columns: ["year", "count"], header: {year: "Year", count: "Corrections recorded"}, rows: 6})}

> **What this proves:** the earliest period represented by this dataset is dominated by form corrections. It does not prove what dominated the unmeasured 1994–2013 project history.

## 2019 · Pull requests arrive

The organisation and its public issue history date from 2014. **2019 is the narrower milestone when pull requests first appear in the committed snapshot.** The number of distinct Git author identities active that year is **${row2019.active_authors}**. This marks adoption of an additional review mechanism, not the arrival of Git itself and not the beginning of public correction work.

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

:::note
**Trust block.** Source: [`data/issue_lifecycle_survival.csv`](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/observatory/site/src/data/issue_lifecycle_survival.csv), a committed feed loaded at build time. **n = ${survival.filter(d => d.cohort === 2014).length}** horizon rows for the 2014 cohort (of ${survival.length} cohort × horizon rows). Data date: snapshot ${manifest.snapshot_date}. Download: [`issue_lifecycle_survival.csv`](https://raw.githubusercontent.com/sanskrit-lexicon/csl-observatory/main/observatory/site/src/data/issue_lifecycle_survival.csv).
:::

**Data table (figure fallback).** ${Inputs.table(survival.filter(d => d.cohort === 2014), {columns: ["horizon_days", "pct_open"], header: {horizon_days: "Days after opening", pct_open: "Still open (%)"}, rows: 6})}

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

## Chapter 2 · The first measured month — July 2026

_Chapter 1 ended with the observatory built and a loop promised: surface a fact, act on it, re-measure. This chapter is that loop's first full month of output. In July 2026 two scheduled data refreshes landed ([July 20](https://github.com/sanskrit-lexicon/csl-observatory/commit/e0f237f), [July 28](https://github.com/sanskrit-lexicon/csl-observatory/commit/1e98dba)), and every result below was committed, with its dataset, inside the month it describes._

```js
const monthlyRaw = await FileAttachment("data/timeseries_monthly.csv").csv();
const monthlyAll = monthlyRaw.map(d => ({ym: d.year_month, repo: d.repo, opened: +d.issues_opened, closed: +d.issues_closed, commits: +d.commits}));
const monthWindow = d3.rollups(
  monthlyAll.filter(d => d.ym >= "2025-08" && d.ym <= "2026-07"),
  v => ({
    commits: d3.sum(v, d => d.commits),
    opened: d3.sum(v, d => d.opened),
    closed: d3.sum(v, d => d.closed),
    repos: new Set(v.filter(x => x.commits || x.opened || x.closed).map(x => x.repo)).size
  }),
  d => d.ym
).map(([ym, v]) => ({ym, ...v})).sort((a, b) => a.ym.localeCompare(b.ym));
const july = monthWindow.find(d => d.ym === "2026-07");
const commitRank = d3.rollups(monthlyAll, v => d3.sum(v, d => d.commits), d => d.ym)
  .map(([ym, commits]) => ({ym, commits}))
  .sort((a, b) => b.commits - a.commits);
const julyCommitRank = commitRank.findIndex(d => d.ym === "2026-07") + 1;
```

<div class="grid grid-cols-3">
  <div class="card">
    <h2>Commits in July</h2>
    <span class="big">${july.commits.toLocaleString()}</span>
    <span class="muted">month #${julyCommitRank} of ${commitRank.length} in the whole record</span>
  </div>
  <div class="card">
    <h2>Issues closed vs opened</h2>
    <span class="big">${july.closed} / ${july.opened}</span>
    <span class="muted">the backlog kept draining</span>
  </div>
  <div class="card">
    <h2>Repositories active</h2>
    <span class="big">${july.repos}</span>
    <span class="muted">of ~85 in the organisation</span>
  </div>
</div>

### The month in the thirteen-year curve

Chapter 1's closing claim — that 2026 is the year the ledger came under active management — holds at month granularity. July's **${july.commits.toLocaleString()}** commits make it the **second-busiest month in the entire 2014–2026 record** (only May 2026's ${commitRank[0].commits.toLocaleString()} was higher), and closings again outran openings, **${july.closed} to ${july.opened}**.

> **How to read:** Each bar is one month of org-wide commits, the twelve months to July 2026. **Example 1:** the three-bar plateau on the right — May, June, July 2026 each above 1,350 — is the observatory era running at a sustained pace no earlier period reached. **Example 2:** the low bars of late 2025 are the pre-taxonomy baseline the era is measured against.

```js
Plot.plot({
  width,
  height: 280,
  marginBottom: 55,
  x: {label: null, tickRotate: -40},
  y: {label: "Commits, org-wide", grid: true},
  marks: [
    Plot.barY(monthWindow, {x: "ym", y: "commits", fill: d => d.ym === "2026-07" ? "#1a7f37" : "#c9c2b6", tip: true, channels: {opened: "opened", closed: "closed", repos: "repos"}}),
    Plot.text(monthWindow.filter(d => d.ym === "2026-07"), {x: "ym", y: "commits", text: d => d.commits.toLocaleString(), dy: -8, fontWeight: 600, fill: "#1a7f37"}),
    Plot.ruleY([0])
  ]
})
```

:::note
**Trust block.** Source: [`data/timeseries_monthly.csv`](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/observatory/site/src/data/timeseries_monthly.csv), a committed feed loaded at build time. **n = ${monthlyAll.length.toLocaleString()}** repo × month rows (${monthWindow.length} months shown). Data date: snapshot ${manifest.snapshot_date}. Download: [`timeseries_monthly.csv`](https://raw.githubusercontent.com/sanskrit-lexicon/csl-observatory/main/observatory/site/src/data/timeseries_monthly.csv).
:::

**Data table (figure fallback).** ${Inputs.table(monthWindow, {columns: ["ym", "commits", "opened", "closed", "repos"], header: {ym: "Month", commits: "Commits", opened: "Issues opened", closed: "Issues closed", repos: "Active repos"}, rows: 6})}

> **What this proves:** the 2026 turn described in chapter 1 is not a single burst — it is a sustained operating pace, and July is the first month whose whole shape the observatory captured as it happened.

### A volunteer campaign becomes a dataset

The single largest July commit was historiographical: the 2025–26 **PWG scan-index campaign** — eighteen months of volunteers page-indexing the printed editions that the Böhtlingk-Roth dictionary cites — was committed as data ([PR #107](https://github.com/sanskrit-lexicon/csl-observatory/pull/107)): a registry of **${scanSum.tracked_works} tracked works**, of which **${scanSum.done} are done**, covering **${scanSum.indexed_mass_pct_of_tracked}%** of the tracked citation mass — **${scanSum.pages_indexed.toLocaleString()}** pages indexed by **${scanSum.volunteers}** volunteers. The full analysis is in the [campaign report](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/reports/pwg_scan_index.md) and on its [dedicated page](/scan-index).

```js
const scanSum = await FileAttachment("data/pwg_scan_index_summary.json").json();
const scanWorks = await FileAttachment("data/pwg_scan_index.csv").csv({typed: true});
const scanStatusOrder = ["done", "on-going", "to-do", "page-wise", "nr-indirect", "nr-alt-name"];
const scanByStatus = Array.from(
  d3.rollup(scanWorks, v => ({works: v.length, mass: d3.sum(v, d => d.citations || 0), pages: d3.sum(v, d => d.pages || 0)}), d => d.status),
  ([status, v]) => ({status, ...v})
).sort((a, b) => scanStatusOrder.indexOf(a.status) - scanStatusOrder.indexOf(b.status));
```

> **How to read:** Each bar is one campaign status; length is the citation mass of the works in it, so the chart shows payoff at stake, not headcount. `page-wise` and `nr-*` are rulings, not backlog — works the campaign deliberately declined to index per-entry.

```js
Plot.plot({
  width,
  height: 240,
  marginLeft: 110,
  x: {label: "Citation mass", grid: true},
  y: {label: null, domain: scanByStatus.map(d => d.status)},
  marks: [
    Plot.barX(scanByStatus, {
      x: "mass", y: "status",
      fill: d => d.status === "done" ? "#1a7f37"
             : d.status === "on-going" ? "#bf8700"
             : d.status === "to-do" ? "#cf222e" : "#8c959f",
      tip: true, channels: {works: "works", pages: "pages"}
    }),
    Plot.ruleX([0])
  ]
})
```

:::note
**Trust block.** Source: [`data/pwg_scan_index.csv`](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/observatory/site/src/data/pwg_scan_index.csv) + [`data/pwg_scan_index_summary.json`](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/observatory/site/src/data/pwg_scan_index_summary.json), committed feeds loaded at build time. **n = ${scanWorks.length}** tracked works. Data date: sheet snapshot ${scanSum.as_of}. Report: [`reports/pwg_scan_index.md`](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/reports/pwg_scan_index.md). Download: [`pwg_scan_index.csv`](https://raw.githubusercontent.com/sanskrit-lexicon/csl-observatory/main/observatory/site/src/data/pwg_scan_index.csv).
:::

**Data table (figure fallback).** ${Inputs.table(scanByStatus, {columns: ["status", "works", "mass", "pages"], header: {status: "Status", works: "Works", mass: "Citation mass", pages: "Pages"}, rows: 6})}

The campaign's follow-on question — can the indexed scans become e-text? — got a measured answer the same month, and the answer was **no, not the obvious way**. The [kośa e-text pilot](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/reports/pwg_kosa_etext_pilot.md) ([PR #110](https://github.com/sanskrit-lexicon/csl-observatory/pull/110)) OCR'd the two heaviest kośa scan sets locally and recovered only **17.8%** valid Sanskrit tokens — while the hOCR the Bayerische Staatsbibliothek already publishes for the same pages scored **43.8%**, 2.5× better, for free. The job was re-scoped from OCR-from-scratch to ingest-and-correct, and the first BSB hOCR harvest landed on July 28 ([PR #123](https://github.com/sanskrit-lexicon/csl-observatory/pull/123)). A NO-GO that costs one pilot and saves a campaign is the observatory loop working as designed.

> **What this proves:** volunteer work that lived in a Google Sheet is now a versioned, downloadable dataset with its own regression checks — and the next step after it was chosen by measurement, not enthusiasm.

### How many errors are left — the first population estimates

Thirteen years of corrections beg the question chapter 1 could not answer: **how much is left?** July produced the org's first defensible estimates ([PR #120](https://github.com/sanskrit-lexicon/csl-observatory/pull/120)), using two-era Chapman capture–recapture over a measured record-linkage ladder: the form-era (2014–2019) and git-era (2019–2026) correction sets act as two capture occasions, and their overlap sizes the unseen population.

```js
const recapture = await FileAttachment("data/error_recapture.csv").csv({typed: true});
const recaptureEst = recapture.filter(d => d.estimable === 1).sort((a, b) => b.n_hat - a.n_hat);
```

> **How to read:** One row per dictionary with an estimable overlap; the dot is the Chapman point estimate of total error sites, the line its 95% confidence interval. **Example 1:** pw's estimate near 68,000 against ~11,000 sites already corrected implies most of the error population is still untouched. **Example 2:** a wide interval (bur) is honesty, not weakness — the overlap is small, and the method says so.

```js
Plot.plot({
  width,
  height: 200,
  marginLeft: 60,
  x: {label: "Estimated total error sites (Chapman, 95% CI)", grid: true},
  y: {label: null, domain: recaptureEst.map(d => d.dict)},
  marks: [
    Plot.ruleY(recaptureEst, {y: "dict", x1: "ci_low", x2: "ci_high", stroke: "#57606a", strokeWidth: 2}),
    Plot.dot(recaptureEst, {x: "n_hat", y: "dict", fill: "#0075ca", r: 5, tip: true, channels: {observed: "s_observed", remaining: "remaining_hat"}}),
    Plot.ruleX([0])
  ]
})
```

:::note
**Trust block.** Source: [`data/error_recapture.csv`](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/observatory/site/src/data/error_recapture.csv), a committed feed loaded at build time. **n = ${recaptureEst.length}** dictionaries with an estimable two-era overlap (of ${recapture.length} tested). Data date: 2026-07 (H1477 measurement; snapshot ${manifest.snapshot_date}). Estimator: two-era Chapman, capped at each dictionary's physical record count; assumptions and caveats in [`reports/error_recapture.md`](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/reports/error_recapture.md). Download: [`error_recapture.csv`](https://raw.githubusercontent.com/sanskrit-lexicon/csl-observatory/main/observatory/site/src/data/error_recapture.csv).
:::

**Data table (figure fallback).** ${Inputs.table(recaptureEst, {columns: ["dict", "s_observed", "n_hat", "ci_low", "ci_high", "remaining_hat"], header: {dict: "Dictionary", s_observed: "Sites corrected", n_hat: "Estimated total", ci_low: "CI low", ci_high: "CI high", remaining_hat: "Est. remaining"}, rows: 6})}

The headline: **pw** has an estimated **~67,866** error sites (CI 59,208–76,525), of which **~56,935** are still uncorrected; **mw** ~60,997, with ~54,110 remaining. A [within-era cross-check](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/reports/corrector_recapture.md) ([PR #122](https://github.com/sanskrit-lexicon/csl-observatory/pull/122)) — correctors as capture occasions instead of eras — lands in the same order of magnitude and gives `pwg` its first estimate (~26,515). Just as important is what the linkage work *rejected*: the [documented dead ends](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/reports/record_linkage_rejected_alternatives.md) include the tempting `<L>`-number join, unsafe because **64% of form-era L-codes have drifted**.

> **What this proves:** the correction project's remaining work is now a number with a confidence interval, not a shrug. At the observed pace, the backlog of dictionary errors is measured in decades — which is exactly the kind of fact a funder or successor institution needs stated plainly.

### Who actually cites the digital resource

Chapter 1 counted the work; July counted the audience. A systematic [OpenAlex citation sweep](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/reports/citation_sweep.md) ([PR #128](https://github.com/sanskrit-lexicon/csl-observatory/pull/128)) replaced the five hand-picked citations the project used to show with a documented **lower bound: ${sweepByTier.find(d => d.code === "C1").works + sweepByTier.find(d => d.code === "C2").works} scholarly works** demonstrably naming or citing the Cologne *digital* lexicon — ${sweepByTier.find(d => d.code === "C1").works} confirmed by name-unique phrase match, ${sweepByTier.find(d => d.code === "C2").works} probable via the citation graph. The **${sweepByTier.find(d => d.code === "C3").works}-work print envelope** (works citing Monier-Williams or Böhtlingk in print) is deliberately fenced off, *not* claimed as digital reach, and the ${sweepByTier.find(d => d.code === "C0").works} rejected phrase collisions stay in the CSV so the exclusions are evidenced, not asserted.

```js
const sweep = await FileAttachment("data/citation_sweep.csv").csv();
const sweepExternal = sweep.filter(d => d.bucket === "external");
const sweepTierLabels = {C1: "C1 · confirmed digital", C2: "C2 · probable (graph)", C3: "C3 · print envelope", C0: "C0 · rejected collisions"};
const sweepByTier = ["C1", "C2", "C3", "C0"].map(t => ({code: t, tier: sweepTierLabels[t], works: sweepExternal.filter(d => d.confidence_tier === t).length}));
```

> **How to read:** One bar per confidence tier of the sweep, external works only (project self-records excluded). Only the two green-to-amber bars are claimed as citations of the digital resource; the two grey bars are the honesty apparatus — the envelope not claimed, and the collisions rejected.

```js
Plot.plot({
  width,
  height: 200,
  marginLeft: 175,
  x: {label: "Works", grid: true},
  y: {label: null, domain: sweepByTier.map(d => d.tier)},
  marks: [
    Plot.barX(sweepByTier, {
      x: "works", y: "tier",
      fill: d => d.code === "C1" ? "#1a7f37" : d.code === "C2" ? "#bf8700" : "#8c959f",
      tip: true
    }),
    Plot.text(sweepByTier, {x: "works", y: "tier", text: d => d.works.toLocaleString(), dx: 12, fontWeight: 600}),
    Plot.ruleX([0])
  ]
})
```

:::note
**Trust block.** Source: [`data/citation_sweep.csv`](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/observatory/site/src/data/citation_sweep.csv), a committed feed loaded at build time. **n = ${sweep.length}** candidate works from the OpenAlex sweep (${sweepExternal.length} external after removing project self-records). Data date: API fetch 2026-07-28, cache committed. Method + recall bounds: [`reports/citation_sweep.md`](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/reports/citation_sweep.md). Download: [`citation_sweep.csv`](https://raw.githubusercontent.com/sanskrit-lexicon/csl-observatory/main/observatory/site/src/data/citation_sweep.csv).
:::

**Data table (figure fallback).** ${Inputs.table(sweepByTier, {columns: ["tier", "works"], header: {tier: "Confidence tier", works: "Works"}, rows: 4})}

> **What this proves:** the project can now put a sourced, reproducible number on its scholarly reach — smaller than a hand-wave, but real, and with its recall limits stated in the report rather than hidden.

### The paper track, quietly

The same month moved the research pipeline without a single new figure needing to be drawn here. Blind cross-model double annotation put the error-typology corpus's inter-annotator agreement at **κ = 0.906** [0.872–0.938] on the location axis ([PR #102](https://github.com/sanskrit-lexicon/csl-observatory/pull/102)), clearing the gate the [OBS-T paper](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/paper-obs-t-error-typology.md) had been waiting on. Its two rival manuscript drafts were reconciled into one canonical text ([PR #125](https://github.com/sanskrit-lexicon/csl-observatory/pull/125)). A false Zenodo DOI was hunted down and corrected everywhere it had been asserted ([PR #99](https://github.com/sanskrit-lexicon/csl-observatory/pull/99)); correction events got a persistent ID scheme so future releases stay comparable ([PR #109](https://github.com/sanskrit-lexicon/csl-observatory/pull/109)); and the rights question was closed in the open — everything here publishes ([PR #111](https://github.com/sanskrit-lexicon/csl-observatory/pull/111)).

> **What this proves:** the loop chapter 1 promised — surface, act, re-measure — ran at monthly cadence for the first time in July 2026. Chapter 3 is whichever month next earns one.

---

*Every figure on this page is computed from the committed datasets — snapshot **${manifest.snapshot_date}**. The scheduled refresh is intended to be monthly but may lag; the snapshot date, not the page-view date, is authoritative. Download the underlying CSV/JSON from the [Data](/data) page to check any number here.*

<style>
.card .big { font-size: 2.1rem; font-weight: 600; display: block; line-height: 1.1; }
.card .muted { font-size: 0.8rem; opacity: 0.65; display: block; margin-top: 0.15rem; }
</style>
