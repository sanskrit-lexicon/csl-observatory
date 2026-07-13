---
title: "Census — L5 Roots & etymology"
toc: true
---

# L5 · Roots & etymology

Statistics over verbal roots and derivational morphology: the MW root
inventory, etymology derivation tables, root-oracle agreement, and the
Whitney × DCS audit. Part of the [statistics census overview](./census-overview)
(H817 WS1.3).

```js
const all = await FileAttachment("data/stats_census_register.csv").csv({typed: true});
const rows = all.filter(d => d.layer === "L5");
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
rows where `layer = L5`, aggregated from csl-orig v02 and WhitneyRoots.
**n = ${n}**. As of 06–12-07-2026. This is the one layer in the register with
**zero** ○ not-started rows — the descriptive base here is fully closed.
:::

## Headline magnitudes

```js
const numeric = rows.filter(d => d.value_numeric != null && !Number.isNaN(d.value_numeric) && d.value_numeric > 0)
  .sort((a, b) => d3.descending(a.value_numeric, b.value_numeric));
```

> **How to read:** log-scale bar of root/etymology counts. **Example:** the
> Whitney × DCS audit (935 roots) sits between the 41-pair oracle-agreement
> matrix and the 2,113-root MW inventory — it audits a large minority of MW's
> roots, not all of them, and is explicitly **capped**: unaccented DCS text
> cannot split verb class I/VI, so corpus root-class verdicts do not appear
> here as a bare number (see the full table's caveat column-equivalent, the
> `value_display` field).

```js
Plot.plot({
  width,
  height: 180,
  marginLeft: 220,
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
  height: 110,
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

## Known ceiling

Per the roadmap's risk register: unaccented DCS cannot split verb class I/VI
or IV/passive (accent collapse). Do not over-claim on root-class statistics
beyond what the Whitney × DCS audit already flags as capped.

**Chart density note:** 2 `Plot.plot` calls (magnitude bar + status bar) —
justified per the same heterogeneous-units reasoning as the L1 page.

<style>
.census-table { font-size: 0.86rem; min-width: 50rem; }
.census-table th, .census-table td { vertical-align: top; }
.table-scroll { max-width: 100%; overflow-x: auto; }
</style>
