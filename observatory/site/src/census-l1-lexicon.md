---
title: "Census — L1 Lexicon text"
toc: true
---

# L1 · Lexicon text

Statistics over the **44 digitized dictionaries**: headwords, overlap, markup,
citations, corrections, and the sense/definition-level gaps still open. Part of
the [statistics census overview](./census-overview) (H817 WS1.3).

```js
const all = await FileAttachment("data/stats_census_register.csv").csv({typed: true});
const rows = all.filter(d => d.layer === "L1");
```

```js
const n = rows.length;
const done = rows.filter(d => d.status === "done").length;
const partial = rows.filter(d => d.status === "partial").length;
const notStarted = rows.filter(d => d.status === "not_started").length;
```

<div class="grid grid-cols-4">
  <div class="card"><h2>Statistics</h2><span class="big">${n}</span></div>
  <div class="card"><h2>Done</h2><span class="big">${done}</span></div>
  <div class="card"><h2>Partial</h2><span class="big">${partial}</span></div>
  <div class="card"><h2>Not started</h2><span class="big">${notStarted}</span></div>
</div>

:::note
**Trust block.** Source: [`stats_census_register.csv`](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/observatory/site/src/data/stats_census_register.csv),
rows where `layer = L1`, aggregated from SanskritLexicography, csl-atlas, csl-orig,
CORRECTIONS, and csl-observatory itself. **n = ${n}**. As of 06–12-07-2026.
:::

## Headline magnitudes

```js
const numeric = rows.filter(d => d.value_numeric != null && !Number.isNaN(d.value_numeric) && d.value_numeric > 0)
  .sort((a, b) => d3.descending(a.value_numeric, b.value_numeric));
```

> **How to read:** log-scale bar of every L1 statistic that has a plain numeric
> count (citations, headwords, tag hits, n-grams). Non-numeric rows (status-only
> or percentage rows) are omitted here and appear in the full table below.
> **Example:** the markup-tag census (17.5M tag hits) and the n-gram oracle
> (6.66M n-grams) dwarf the union-headword count (323k) by more than an order
> of magnitude — expected, since one headword carries many markup hits.

```js
Plot.plot({
  width,
  height: 260,
  marginLeft: 260,
  x: {label: "Count (log scale)", type: "log", grid: true},
  y: {label: null, domain: numeric.map(d => d.statistic)},
  marks: [
    Plot.barX(numeric, {x: "value_numeric", y: "statistic", fill: "#3a5f7d", tip: true}),
    Plot.ruleX([1])
  ]
})
```

## Status breakdown

```js
const statusOrder = [
  {key: "done", label: "Done", color: "#1a7f37"},
  {key: "partial", label: "Partial", color: "#bf8700"},
  {key: "not_started", label: "Not started", color: "#cf222e"}
];
const statusData = statusOrder.map(s => ({label: s.label, count: rows.filter(d => d.status === s.key).length, color: s.color}));
```

```js
Plot.plot({
  width,
  height: 130,
  marginLeft: 110,
  x: {label: "Statistics", grid: true},
  y: {label: null, domain: statusData.map(d => d.label)},
  marks: [
    Plot.barX(statusData, {x: "count", y: "label", fill: "color", tip: true}),
    Plot.ruleX([0])
  ]
})
```

## Full table

```js
display(html`<div class="table-scroll"><table class="census-table">
  <thead><tr><th>Statistic</th><th>Value</th><th>Status</th><th>Source</th><th>As of</th></tr></thead>
  <tbody>
    ${rows.map(d => html`<tr>
      <td>${d.statistic}</td>
      <td>${d.value_display}</td>
      <td>${d.status}</td>
      <td><a href=${d.source_url} target="_blank" rel="noopener">${d.source_repo}</a></td>
      <td>${d.as_of_date}</td>
    </tr>`)}
  </tbody>
</table></div>`);
```

Download: [`stats_census_register.csv`](https://raw.githubusercontent.com/sanskrit-lexicon/csl-observatory/main/observatory/site/src/data/stats_census_register.csv) (full register, all layers) · [Data downloads](./data).

## Open gaps

The two ○ not-started rows (definition typology, per-dict editorial fingerprint)
are Q2/analytical-layer work per the roadmap, not Q1 — see
[Part II Q2](https://github.com/gasyoun/SanskritLexicography/blob/master/ROADMAP_STATISTICS_ORG_CENSUS_2026_2027.md#q2-octdec-2026--the-analytical-layer).
Sense/polysemy per dict is genuinely capped at 11/44 dicts — the remaining 33
have no structural sense-marking to count against (dead end recorded in the
roadmap's H817 WS1.2 pass, not a to-do).

**Chart density note:** 2 `Plot.plot` calls — a magnitude bar (comparable
numeric rows only) + a status bar. The remaining rows are non-numeric
(percentages, qualitative status) and are covered by the full table, not
manufactured into additional bars.

<style>
.census-table { font-size: 0.86rem; min-width: 50rem; }
.census-table th, .census-table td { vertical-align: top; }
.table-scroll { max-width: 100%; overflow-x: auto; }
</style>
