---
title: Sense polysemy by dictionary
toc: true
---

<link rel="stylesheet" href="./palette.css">

# Sense polysemy by dictionary

Mean **sense units per entry** for the **11** CDSL dictionaries that carry structural
sense marking. The remaining 33 dictionaries have no machine-readable sense boundary —
this page does **not** invent a proxy (H817 dead end).

```js
const poly = await FileAttachment("data/sense_polysemy_per_dict.csv").csv({typed: true});
```

```js
const paletteStyles = getComputedStyle(document.documentElement);
const token = (name) => paletteStyles.getPropertyValue(name).trim();
const OBS_ACCENT = token("--obs-accent");
const OBS_MUTED = token("--obs-muted");
const OBS_GOOD = token("--obs-good");
const OBS_SEQ = [1, 2, 3, 4, 5, 6, 7].map((i) => token(`--obs-seq-${i}`));
```

```js
const n = poly.length;
const byYear = poly.slice().sort((a, b) => a.year - b.year);
const families = Array.from(new Set(poly.map((d) => d.family))).sort();
const meanSense = d3.mean(poly, (d) => d.sense_units_per_entry);
const totalEntries = d3.sum(poly, (d) => d.entries);
```

<div class="grid grid-cols-4">
  <div class="card"><h2>Dictionaries</h2><span class="big">${n}</span><div class="muted">of 44 CDSL</div></div>
  <div class="card"><h2>Mean sense/entry</h2><span class="big">${meanSense.toFixed(2)}</span></div>
  <div class="card"><h2>Entries (sum)</h2><span class="big">${totalEntries.toLocaleString()}</span></div>
  <div class="card"><h2>Families</h2><span class="big">${families.length}</span></div>
</div>

:::note
**Trust block.** Source: [`data/sense_polysemy_per_dict.tsv`](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/data/sense_polysemy_per_dict.tsv)
(loader: `observatory/site/src/data/sense_polysemy_per_dict.csv.py`, read-only).
Upstream: csl-atlas `data/lexico/r2_h1.json` (per-row `source` column).
**n = ${n}** dictionaries · **${totalEntries.toLocaleString()}** entries summed.
Data date: 13-07-2026 (H817). **Coverage ceiling:** 11/44 — the other 33 lack structural
sense-marking in digitised text; expanding n requires markup work, not a denser chart.
:::

## Sense units per entry (chronological)

Sorted by publication year — the editorial history of how densely senses were split.

> **How to read:** Bar height = mean sense units per entry. **Example 1:** `mw72` (1872)
> sits high: denser sense subdivision than many later titles. **Example 2:** Indigenous
> monolingual works near 1.0 mean nearly one sense unit per entry under this metric.

```js
display(Plot.plot({
  width,
  height: 320,
  marginBottom: 50,
  x: {label: "Dictionary (by year)", domain: byYear.map((d) => d.dict)},
  y: {label: "Sense units per entry", grid: true},
  color: {legend: true, domain: families, range: OBS_SEQ, label: "Family"},
  marks: [
    Plot.barY(byYear, {
      x: "dict",
      y: "sense_units_per_entry",
      fill: "family",
      tip: true,
      channels: {Year: "year", Entries: "entries"}
    }),
    Plot.ruleY([0]),
    Plot.ruleY([1], {stroke: OBS_MUTED, strokeDasharray: "4,3"})
  ]
}))
```

## Year × density (family colour)

> **How to read:** x = year, y = sense units per entry, colour = family.
> **Example 1:** Points climbing over the 19th century would be rising sense density.
> **Example 2:** Same-family pairs (mw72/mw, ap90/ap) show within-lineage drift.

```js
display(Plot.plot({
  width,
  height: 340,
  x: {label: "Year", grid: true},
  y: {label: "Sense units per entry", grid: true},
  color: {legend: true, domain: families, range: OBS_SEQ, label: "Family"},
  marks: [
    Plot.dot(poly, {
      x: "year",
      y: "sense_units_per_entry",
      fill: "family",
      r: 7,
      tip: true,
      channels: {Dict: "dict", Entries: "entries"}
    }),
    Plot.text(poly, {
      x: "year",
      y: "sense_units_per_entry",
      text: "dict",
      dy: -10,
      fontSize: 10,
      fill: OBS_MUTED
    })
  ]
}))
```

## Entry counts

Absolute entry volume behind the density ratio — a small dense dictionary is not the
same editorial object as a large sparse one.

```js
const byEntries = poly.slice().sort((a, b) => b.entries - a.entries);

display(Plot.plot({
  width,
  height: 300,
  marginLeft: 60,
  x: {label: "Entries", grid: true},
  y: {label: null, domain: byEntries.map((d) => d.dict)},
  color: {domain: families, range: OBS_SEQ},
  marks: [
    Plot.barX(byEntries, {
      x: "entries",
      y: "dict",
      fill: "family",
      tip: true,
      channels: {Year: "year", "Sense/entry": "sense_units_per_entry"}
    }),
    Plot.ruleX([0])
  ]
}))
```

## Family aggregate means

Unweighted mean of `sense_units_per_entry` across dictionaries in each family (each
title counts once — not entry-weighted).

```js
const familyAgg = Array.from(
  d3.group(poly, (d) => d.family),
  ([family, rows]) => ({
    family,
    n_dicts: rows.length,
    mean_sense: d3.mean(rows, (d) => d.sense_units_per_entry),
    entries: d3.sum(rows, (d) => d.entries)
  })
).sort((a, b) => b.mean_sense - a.mean_sense);
```

```js
display(Plot.plot({
  width,
  height: 260,
  marginLeft: 130,
  x: {label: "Mean sense units / entry (unweighted)", grid: true},
  y: {label: null, domain: familyAgg.map((d) => d.family)},
  marks: [
    Plot.barX(familyAgg, {
      x: "mean_sense",
      y: "family",
      fill: OBS_ACCENT,
      tip: true,
      channels: {Dictionaries: "n_dicts", Entries: "entries"}
    }),
    Plot.ruleX([0]),
    Plot.ruleX([1], {stroke: OBS_MUTED, strokeDasharray: "4,3"})
  ]
}))
```

## Dict × year scatter of entry volume

Fifth mark: log-scale entry count against year, size optional via radius from sense density.

```js
display(Plot.plot({
  width,
  height: 340,
  x: {label: "Year", grid: true},
  y: {label: "Entries (log)", type: "log", grid: true},
  color: {legend: true, domain: families, range: OBS_SEQ, label: "Family"},
  r: {range: [4, 14]},
  marks: [
    Plot.dot(poly, {
      x: "year",
      y: "entries",
      r: "sense_units_per_entry",
      fill: "family",
      fillOpacity: 0.85,
      tip: true,
      channels: {Dict: "dict", "Sense/entry": "sense_units_per_entry"}
    })
  ]
}))
```

> **Conclusion:** Among the 11 sense-marked dictionaries, density is not a simple year
> trend: Benfey/Apte/mw72 sit high; several large Petersburg and indigenous titles sit near
> 1.0–1.2. Any org-wide “polysemy” claim must stay inside this n=11 set — the other 33 are
> not missing data, they are **out of scope** until sense markup exists.

## Full table

```js
display(Inputs.table(byYear, {
  columns: ["dict", "year", "family", "sense_units_per_entry", "entries", "source"],
  sort: "year",
  rows: 20
}))
```

Download source TSV:
[`sense_polysemy_per_dict.tsv`](https://raw.githubusercontent.com/sanskrit-lexicon/csl-observatory/main/data/sense_polysemy_per_dict.tsv)
· report:
[`reports/sense_polysemy_per_dict.md`](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/reports/sense_polysemy_per_dict.md)
· sibling census: [L1 Lexicon](./census-l1-lexicon).
