---
title: PWG scan-index campaign
toc: true
---

# PWG literary-source scan-index campaign

Between January 2025 and July 2026 a volunteer team page-indexed the printed
editions that the Böhtlingk-Roth *Sanskrit-Wörterbuch* (PWG) cites, so that an
`<ls>` citation in the dictionary can be resolved to the page image of the edition
it cites. This page measures that campaign **by citation mass** — a 159-page
*Kumārasaṃbhava* and a 2,420-page *Taittirīyabrāhmaṇa* are neither equal work nor
equal payoff.

Complement, not duplicate, of [Citation Coverage](/citation-coverage): that page
asks how many citations *link out*; this one asks how the link targets got built.

```js
const sum = await FileAttachment("data/pwg_scan_index_summary.json").json();
const works = await FileAttachment("data/pwg_scan_index.csv").csv({typed: true});
```

<div class="grid grid-cols-4">
  <div class="card">
    <h2>Works indexed</h2>
    <span class="big">${sum.done} / ${sum.tracked_works}</span>
  </div>
  <div class="card">
    <h2>Citation mass indexed</h2>
    <span class="big">${sum.indexed_mass_pct_of_tracked}%</span>
  </div>
  <div class="card">
    <h2>Pages indexed</h2>
    <span class="big">${sum.pages_indexed.toLocaleString("en-US")}</span>
  </div>
  <div class="card">
    <h2>Volunteers</h2>
    <span class="big">${sum.volunteers}</span>
  </div>
</div>

:::note
**Two denominators, and they are not interchangeable.** The headline percentage is
coverage of the **tracked set** — the works the campaign took on. Against the whole
dictionary it is
${(100 * sum.indexed_citation_mass / sum.citation_mass_denominator).toFixed(1)}%:
${sum.indexed_citation_mass.toLocaleString("en-US")} of
${sum.citation_mass_denominator.toLocaleString("en-US")} `<ls>` citations, the `ALL` of
the ${sum.citation_mass_denominator_snapshot} count snapshot these numbers come from.
That second figure was unavailable until H2874 recovered the column's provenance;
mixing it with a differently dated total is the mistake the
[contract](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/reports/pwg_citation_count_provenance.md)
exists to prevent. ${sum.tracked_works} sources tracked, snapshot ${sum.as_of}.
:::

## Where the work stands

Status is the sheet's own vocabulary. Two of its values are **rulings, not backlog**:
`page-wise` marks a work PWG cites by page rather than by verse, so a per-entry index
would answer a question nobody asks of it; `nr-*` marks an abbreviation that is an
indirect citation or an alternate name for a work already indexed.

> **How to read:** Each bar is one status; length is the citation mass of the works in
> it, so the chart shows *payoff at stake*, not headcount. **Example 1:** `done`
> dwarfing every other bar means the campaign has already captured most of the
> citation value it set out to capture. **Example 2:** `page-wise` being large is not
> a backlog warning — it is the mass the campaign deliberately declined to index.

```js
const statusOrder = ["done", "on-going", "to-do", "page-wise", "nr-indirect", "nr-alt-name"];
const byStatus = Array.from(
  d3.rollup(works, v => ({
    works: v.length,
    mass: d3.sum(v, d => d.citations || 0),
    pages: d3.sum(v, d => d.pages || 0)
  }), d => d.status),
  ([status, v]) => ({status, ...v})
).sort((a, b) => statusOrder.indexOf(a.status) - statusOrder.indexOf(b.status));

display(Plot.plot({
  width,
  height: 300,
  marginLeft: 110,
  x: {label: "Citation mass", grid: true},
  y: {label: null, domain: byStatus.map(d => d.status)},
  color: {legend: false},
  marks: [
    Plot.barX(byStatus, {
      x: "mass", y: "status",
      fill: d => d.status === "done" ? "#1a7f37"
             : d.status === "on-going" ? "#bf8700"
             : d.status === "to-do" ? "#cf222e" : "#8c959f",
      tip: true, channels: {works: "works", pages: "pages"}
    }),
    Plot.ruleX([0])
  ]
}))
```

> **Conclusion:** The campaign finished the works that carry the citation weight. What
> is left unclaimed is a small share of the tracked mass, concentrated in long Vedic
> texts.

## Velocity — two pipelines, not one

An index being *finished* by its volunteer and its scan directory going *public* are
separate steps with separate queues. Plotting them together shows the publishing lag
as a visible offset rather than hiding it inside one "progress" line.

> **How to read:** Two series over the campaign's months — indexes finished, and scan
> directories published. **Example 1:** A tall finished-bar with no published-bar
> beside it is a month whose output was still in the publishing queue. **Example 2:**
> Published exceeding finished in a later month is that queue draining.

```js
display(Plot.plot({
  width,
  height: 320,
  marginBottom: 60,
  x: {label: null, tickRotate: -40},
  y: {label: "Works", grid: true},
  color: {legend: true, domain: ["indexes finished", "scans published"], range: ["#0075ca", "#1a7f37"]},
  marks: [
    Plot.barY(sum.months.flatMap(m => [
      {month: m.month, kind: "indexes finished", n: m.indexes_finished},
      {month: m.month, kind: "scans published", n: m.scans_published}
    ]), {x: "month", y: "n", fill: "kind", fx: null, tip: true, dx: 0}),
    Plot.ruleY([0])
  ]
}))
```

The median lag from an index being posted to its scan directory going public is
**${sum.median_index_to_public_days} days**.

> **Conclusion:** Throughput peaked in February–March 2025 and decayed through the
> year — a volunteer campaign's normal shape, not a stall. The publishing pipeline
> tracked the indexing pipeline with a lag of under two weeks at the median.

## Who did it

Attribution is exactly the sheet's `Reserved/Indexed by` column. Rows count assigned
work, so a volunteer's row count includes work in progress, not only finished indexes.

> **How to read:** Each bar is one volunteer; length is the citation mass of the works
> they took. **Example 1:** Two volunteers carrying a third of the mass between them
> is the bus-factor pattern this observatory measures elsewhere, reproduced inside a
> single campaign. **Example 2:** A volunteer with many pages but little citation mass
> took long, thinly-cited books — real work the mass metric under-credits.

```js
const vols = sum.per_volunteer.slice().sort((a, b) => b.citation_mass - a.citation_mass);

display(Plot.plot({
  width,
  height: 320,
  marginLeft: 140,
  x: {label: "Citation mass of works taken", grid: true},
  y: {label: null, domain: vols.map(d => d.handle)},
  marks: [
    Plot.barX(vols, {x: "citation_mass", y: "handle", fill: "#0075ca", tip: true,
                     channels: {works: "works", pages: "pages"}}),
    Plot.ruleX([0])
  ]
}))
```

> **Conclusion:** Eight volunteers carried the campaign, with the top three taking
> roughly half the citation mass between them. One volunteer's work sits entirely in
> multi-volume books whose citation count the sheet records only once, on volume 1 —
> their mass reads as zero here and their page count tells the truer story.

## What remains

The unclaimed backlog, ranked by citation payoff. The ★ marking in the source sheet
picks out exactly the Vedic saṃhitā / brāhmaṇa / upaniṣad / śrauta- and gṛhya-sūtra /
prātiśākhya group.

> **How to read:** One bar per unclaimed work, longest citation count first.
> **Example 1:** A short bar over a large page count is a low-yield, high-effort
> target. **Example 2:** The colour split shows how much of what is left is Vedic —
> the material with the awkward reference schemes.

```js
const backlog = sum.backlog.slice().sort((a, b) => b.citations - a.citations);

display(Plot.plot({
  width,
  height: 260,
  marginLeft: 130,
  x: {label: "Citations in PWG (sheet count)", grid: true},
  y: {label: null, domain: backlog.map(d => d.ls_code)},
  color: {legend: true, domain: ["Vedic (★)", "other"], range: ["#8250df", "#57606a"]},
  marks: [
    Plot.barX(backlog, {x: "citations", y: "ls_code",
                        fill: d => d.vedic ? "Vedic (★)" : "other",
                        tip: true, channels: {work: "title", pages: "pages"}}),
    Plot.ruleX([0])
  ]
}))
```

> **Conclusion:** The remaining work is Vedic and long. The kāvya and kośa material,
> which indexes quickly and is cited densely, is finished — so the backlog's citation
> payoff per page is the lowest the campaign has faced.

## Source

- report — [`reports/pwg_scan_index.md`](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/reports/pwg_scan_index.md)
- registry — [`data/pwg_scan_index_tracker/pwg_scan_index.tsv`](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/data/pwg_scan_index_tracker/pwg_scan_index.tsv)
- e-text candidate queue — [`pwg_etext_candidate_queue.tsv`](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/data/pwg_scan_index_tracker/pwg_etext_candidate_queue.tsv)
- campaign history — [`docs/PWG_SCAN_INDEX_CAMPAIGN_HISTORY_2025_2026.md`](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/docs/PWG_SCAN_INDEX_CAMPAIGN_HISTORY_2025_2026.md)
- generator — [`scripts/pwg_scan_index.py`](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/scripts/pwg_scan_index.py)
- upstream tracker — [Google Sheet](https://docs.google.com/spreadsheets/d/1rcYfQE0D26RNdWSmRQzhFnV3Gf248wSuldTj-wt8_O0/edit?gid=0), snapshotted verbatim under [`snapshot/`](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/data/pwg_scan_index_tracker/snapshot)

[← back to overview](/)
