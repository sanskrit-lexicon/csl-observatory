---
title: Statistics census — overview
toc: true
---

# Statistics census — overview

The Part-0 counting register of the org-wide
[statistics roadmap](https://github.com/gasyoun/SanskritLexicography/blob/master/ROADMAP_STATISTICS_ORG_CENSUS_2026_2027.md):
every headline statistic the org can compute over the Sanskrit Lexicon ecosystem
(~85 repos), across seven data layers, each carrying its computed value and a
**done / partial / not-started** status. This page is the dashboard skeleton
seeded from that register (H817 WS1.3) — the per-layer pages below drill into
each layer.

```js
const register = await FileAttachment("data/stats_census_register.csv").csv({typed: true});
```

```js
const n = register.length;
const done = register.filter(d => d.status === "done").length;
const partial = register.filter(d => d.status === "partial").length;
const notStarted = register.filter(d => d.status === "not_started").length;
const layers = Array.from(new Set(register.map(d => d.layer))).sort();
```

<div class="grid grid-cols-4">
  <div class="card"><h2>Statistics tracked</h2><span class="big">${n}</span></div>
  <div class="card"><h2>Done</h2><span class="big">${done}</span></div>
  <div class="card"><h2>Partial</h2><span class="big">${partial}</span></div>
  <div class="card"><h2>Not started</h2><span class="big">${notStarted}</span></div>
</div>

:::note
**Trust block.** Source artifact:
[`stats_census_register.csv`](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/observatory/site/src/data/stats_census_register.csv)
(hand-curated from the roadmap's Part-0 table, itself aggregated from ~15 sibling
repos — this page computes nothing new). **n = ${n}** rows. **As of:** 06–13-07-2026
census re-measure; each row cites its own source link, re-verify before citing a
specific count in published work.
:::

## By layer

```js
const statusOrder = [
  {key: "done", label: "Done", color: "#1a7f37"},
  {key: "partial", label: "Partial", color: "#bf8700"},
  {key: "not_started", label: "Not started", color: "#cf222e"}
];
const byLayer = layers.map(layer => {
  const rows = register.filter(d => d.layer === layer);
  const layerName = rows[0]?.layer_name ?? layer;
  const counts = {layer: `${layer} — ${layerName}`};
  for (const s of statusOrder) counts[s.label] = rows.filter(d => d.status === s.key).length;
  return counts;
});
const byLayerLong = byLayer.flatMap(row =>
  statusOrder.map(s => ({layer: row.layer, status: s.label, color: s.color, count: row[s.label]}))
);
```

> **How to read:** each bar is one of the seven data layers (L1 lexicon text
> through L7 product/funnel); segment color is census status. **Example:** a bar
> that is entirely green is a fully-closed layer; a bar with a long red segment
> (L7 product/funnel) names an area still gated on host access, not on effort.

```js
Plot.plot({
  width,
  height: 320,
  marginLeft: 220,
  x: {label: "Statistics", grid: true},
  y: {label: null},
  color: {domain: statusOrder.map(s => s.label), range: statusOrder.map(s => s.color), legend: true},
  marks: [
    Plot.barX(byLayerLong, {x: "count", y: "layer", fill: "status", tip: true, order: layers}),
    Plot.ruleX([0])
  ]
})
```

## Overall status

```js
const overallData = statusOrder.map(s => ({label: s.label, count: register.filter(d => d.status === s.key).length, color: s.color}));
```

```js
Plot.plot({
  width,
  height: 140,
  marginLeft: 110,
  x: {label: "Statistics", grid: true},
  y: {label: null, domain: overallData.map(d => d.label)},
  marks: [
    Plot.barX(overallData, {x: "count", y: "label", fill: "color", tip: true}),
    Plot.ruleX([0])
  ]
})
```

## Layer pages

| Layer | Focus | Page |
|---|---|---|
| L1 | Lexicon text (44 dictionaries) | [Lexicon text](./census-l1-lexicon) |
| L2 | Morphology & forms (kosha, DCS, Heritage, vidyut) | [Morphology & forms](./census-l2-morphology) |
| L3 | Corpus & usage (DCS, SamudraManthanam) | [Corpus & usage](./census-l3-corpus) |
| L4 | Translation (RU/EN kits, alignment, glossaries) | [Translation](./census-l4-translation) |
| L5 | Roots & etymology | [Roots & etymology](./census-l5-roots) |
| L6 | Repo-meta & process | see [Repo health](./repo-health), [Org shape](./org-shape), [Community](./community) — already extensively covered |
| L7 | Product & funnel | mostly ○ not started, gated on host credentials — tracked in the register below, no dedicated page yet |

## Full register

```js
const statusFilter = view(Inputs.select(["all", ...statusOrder.map(s => s.label)], {label: "Status"}));
const layerFilter = view(Inputs.select(["all", ...layers], {label: "Layer"}));
```

```js
const statusKeyFor = (label) => statusOrder.find(s => s.label === label)?.key ?? label;
const filtered = register.filter(d =>
  (layerFilter === "all" || d.layer === layerFilter) &&
  (statusFilter === "all" || d.status === statusKeyFor(statusFilter))
);
```

```js
display(html`<div class="table-scroll"><table class="census-table">
  <thead><tr><th>Layer</th><th>Statistic</th><th>Value</th><th>Status</th><th>Source</th><th>As of</th></tr></thead>
  <tbody>
    ${filtered.map(d => html`<tr>
      <td>${d.layer}</td>
      <td>${d.statistic}</td>
      <td>${d.value_display}</td>
      <td>${d.status}</td>
      <td><a href=${d.source_url} target="_blank" rel="noopener">${d.source_repo}</a></td>
      <td>${d.as_of_date}</td>
    </tr>`)}
  </tbody>
</table></div>`);
```

Download the full register: [`stats_census_register.csv`](https://raw.githubusercontent.com/sanskrit-lexicon/csl-observatory/main/observatory/site/src/data/stats_census_register.csv) · see also [Data downloads](./data).

## Source

- [`ROADMAP_STATISTICS_ORG_CENSUS_2026_2027.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/ROADMAP_STATISTICS_ORG_CENSUS_2026_2027.md) — Part 0, the counting register this page renders
- [`FEATURES_INDEX.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/FEATURES_INDEX.md) — what assets exist
- [`DATA_LAYERS_CENSUS.md`](https://github.com/gasyoun/Uprava/blob/main/DATA_LAYERS_CENSUS.md) — what data sits uncounted on disk
- data: [`stats_census_register.csv`](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/observatory/site/src/data/stats_census_register.csv)

**Chart density note:** this overview page carries 2 `Plot.plot` calls (layer × status
stacked bar, overall status bar) — a status scoreboard over heterogeneous units
does not honestly support more distinct chart types without manufacturing
spurious visuals; the per-layer pages add a third (magnitude) chart each.

<style>
.census-table { font-size: 0.86rem; min-width: 56rem; }
.census-table th, .census-table td { vertical-align: top; }
.table-scroll { max-width: 100%; overflow-x: auto; }
</style>
