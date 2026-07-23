---
title: Paradigm-cell coverage
toc: true
---

<link rel="stylesheet" href="./palette.css">

# Paradigm-cell coverage

How many **finite-verb paradigm cells** each DCS root lemma attests — the org-wide
version of what the VisualDCS paradigm browser shows on a handful of roots. A cell is a
DCS UD 5-tuple (tense · mood · voice · person · number) on finite tokens only.

```js
const roots = await FileAttachment("data/paradigm_cell_coverage_per_root.csv").csv({typed: true});
```

```js
const paletteStyles = getComputedStyle(document.documentElement);
const token = (name) => paletteStyles.getPropertyValue(name).trim();
const OBS_ACCENT = token("--obs-accent");
const OBS_MUTED = token("--obs-muted");
const OBS_GOOD = token("--obs-good");
const OBS_WARN = token("--obs-warn");
const OBS_SEQ = [1, 2, 3, 4, 5, 6, 7].map((i) => token(`--obs-seq-${i}`));
```

```js
const nRoots = roots.length;
const finiteTotal = d3.sum(roots, (d) => d.finite_tokens);
const with1 = roots.filter((d) => d.distinct_cells >= 1).length;
const with5 = roots.filter((d) => d.distinct_cells >= 5).length;
const with20 = roots.filter((d) => d.distinct_cells >= 20).length;
const maxCells = d3.max(roots, (d) => d.distinct_cells);
```

<div class="grid grid-cols-4">
  <div class="card"><h2>Roots (≥1 finite)</h2><span class="big">${nRoots.toLocaleString()}</span></div>
  <div class="card"><h2>Finite tokens</h2><span class="big">${finiteTotal.toLocaleString()}</span></div>
  <div class="card"><h2>≥5 cells</h2><span class="big">${with5.toLocaleString()}</span></div>
  <div class="card"><h2>Max cells / root</h2><span class="big">${maxCells}</span></div>
</div>

:::note
**Trust block.** Source: [`data/paradigm_cell_coverage_per_root.tsv`](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/data/paradigm_cell_coverage_per_root.tsv)
(loader: `observatory/site/src/data/paradigm_cell_coverage_per_root.csv.py`, read-only).
Generator: [`scripts/paradigm_cell_coverage.py`](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/scripts/paradigm_cell_coverage.py)
from VisualDCS `dcs_full.sqlite`. **n = ${nRoots.toLocaleString()}** roots · **${finiteTotal.toLocaleString()}** finite tokens.
Data date: 13-07-2026 (H817 WS1.2).
**Caveat (B11 / WhitneyRoots):** unaccented DCS cannot split class I/VI or IV/passive;
`Tense=Past` conflates aorist/perfect. Cells never overcount traditional lakāra; they can undercount.
Non-finite forms (participles, converbs, gerundives, infinitives) are out of scope.
:::

## Coverage summary

Share of roots clearing cell-count floors — the long tail of hapax finite forms vs
paradigm-rich lemmas.

```js
const floors = [
  {floor: "≥1 cell", n: with1, share: with1 / nRoots},
  {floor: "≥5 cells", n: with5, share: with5 / nRoots},
  {floor: "≥20 cells", n: with20, share: with20 / nRoots}
];
```

```js
display(Plot.plot({
  width,
  height: 200,
  marginLeft: 90,
  x: {label: "Share of roots", domain: [0, 1], percent: true, grid: true},
  y: {label: null, domain: floors.map((d) => d.floor)},
  marks: [
    Plot.barX(floors, {
      x: "share",
      y: "floor",
      fill: OBS_ACCENT,
      tip: true,
      channels: {Roots: "n"}
    }),
    Plot.ruleX([0])
  ]
}))
```

## Histogram of distinct cells

> **How to read:** x = number of distinct finite cells per root; y = root count.
> **Example 1:** A tall bar at 1 is hapax-cell lemmas (one form only). **Example 2:** The
> right tail is high-coverage roots used across many lakāra cells in running text.

```js
display(Plot.plot({
  width,
  height: 340,
  x: {label: "Distinct finite cells per root", grid: true},
  y: {label: "Roots", grid: true},
  marks: [
    Plot.rectY(roots, Plot.binX({y: "count"}, {x: "distinct_cells", thresholds: 40, fill: OBS_ACCENT})),
    Plot.ruleY([0])
  ]
}))
```

## Tokens vs cells (log × linear)

> **How to read:** Each dot is a root; x = finite tokens (log), y = distinct cells.
> **Example 1:** Points high and left are morphologically diverse for their frequency.
> **Example 2:** Points low and right are frequent but paradigm-narrow (few cells).

```js
display(Plot.plot({
  width,
  height: 420,
  x: {label: "Finite tokens (log)", type: "log", grid: true},
  y: {label: "Distinct cells", grid: true},
  color: {type: "linear", scheme: "YlGnBu", legend: true, label: "Distinct cells"},
  marks: [
    Plot.dot(roots, {
      x: "finite_tokens",
      y: "distinct_cells",
      fill: "distinct_cells",
      fillOpacity: 0.45,
      r: 2.5,
      tip: true,
      channels: {Root: "root"}
    })
  ]
}))
```

## Top roots by cell coverage

```js
const topK = view(Inputs.range([15, 50], {value: 25, step: 1, label: "Top-K roots"}));
```

```js
const topByCells = roots.slice().sort((a, b) => b.distinct_cells - a.distinct_cells || b.finite_tokens - a.finite_tokens).slice(0, topK);

display(Plot.plot({
  width,
  height: Math.max(360, topK * 14),
  marginLeft: 100,
  x: {label: "Distinct cells", grid: true},
  y: {label: null, domain: topByCells.map((d) => d.root)},
  marks: [
    Plot.barX(topByCells, {
      x: "distinct_cells",
      y: "root",
      fill: OBS_ACCENT,
      tip: true,
      channels: {Tokens: "finite_tokens"}
    }),
    Plot.ruleX([0])
  ]
}))
```

## Most frequent cell labels (corpus-wide)

Parse the per-root `cells` field (`Label:count|…`) and sum token counts across roots for
the top 30 labels.

> **How to read:** Bar length = total finite tokens carrying that cell label.
> **Example 1:** `Pres.Ind.Act.3.Sing` dominates running Sanskrit finite usage.
> **Example 2:** Rare duals and passives sit at the long tail.

```js
const cellCounts = new Map();
for (const row of roots) {
  const field = String(row.cells || "");
  if (!field) continue;
  for (const part of field.split("|")) {
    const idx = part.lastIndexOf(":");
    if (idx < 0) continue;
    const label = part.slice(0, idx);
    const n = +part.slice(idx + 1);
    if (!label || !Number.isFinite(n)) continue;
    cellCounts.set(label, (cellCounts.get(label) || 0) + n);
  }
}
const cellRank = Array.from(cellCounts, ([cell, tokens]) => ({cell, tokens}))
  .sort((a, b) => b.tokens - a.tokens)
  .slice(0, 30);
```

```js
display(Plot.plot({
  width,
  height: 560,
  marginLeft: 180,
  x: {label: "Finite tokens (summed over roots)", grid: true},
  y: {label: null, domain: cellRank.map((d) => d.cell)},
  marks: [
    Plot.barX(cellRank, {x: "tokens", y: "cell", fill: OBS_GOOD, tip: true}),
    Plot.ruleX([0])
  ]
}))
```

> **Conclusion:** Finite coverage is heavily skewed: most roots show one or a few cells,
> while a small head of high-frequency roots open dozens of cells. The cell inventory itself
> is also skewed toward present indicative active 3sg and a handful of narrative past/optative
> cells — not a flat traditional paradigm chart.

## Data table

```js
const tableFilter = view(Inputs.search(roots, {placeholder: "Filter root…", label: "Search"}));
```

```js
display(Inputs.table(tableFilter, {
  columns: ["root", "finite_tokens", "distinct_cells", "cells"],
  sort: "distinct_cells",
  reverse: true,
  rows: 20
}))
```

Coverage floors (machine-readable summary of the first chart):

| Floor | Roots | Share |
|---|--:|--:|
| ≥1 cell | ${with1.toLocaleString()} | ${((100 * with1) / nRoots).toFixed(1)}% |
| ≥5 cells | ${with5.toLocaleString()} | ${((100 * with5) / nRoots).toFixed(1)}% |
| ≥20 cells | ${with20.toLocaleString()} | ${((100 * with20) / nRoots).toFixed(1)}% |

Download source TSV:
[`paradigm_cell_coverage_per_root.tsv`](https://raw.githubusercontent.com/sanskrit-lexicon/csl-observatory/main/data/paradigm_cell_coverage_per_root.tsv)
· report:
[`reports/paradigm_cell_coverage.md`](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/reports/paradigm_cell_coverage.md)
· sibling census: [L2 Morphology](./census-l2-morphology) · [L5 Roots](./census-l5-roots).
