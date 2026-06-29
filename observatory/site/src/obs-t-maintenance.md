---
title: OBS-T maintenance
toc: true
---

# OBS-T Maintenance Light

Small operational views for keeping OBS-T healthy after infrastructure changes.

```js
const component = await FileAttachment("data/obs_t_component.csv").csv({typed: true});
const confus = await FileAttachment("data/obs_t_confusion.csv").csv({typed: true});
const campaigns = await FileAttachment("data/obs_t_campaigns.csv").csv({typed: true});
const dicts = await FileAttachment("data/obs_t_dict.csv").csv({typed: true});
const monthly = await FileAttachment("data/obs_t_timeline_monthly.csv").csv({typed: true});
```

```js
const GREEN = "#1a7f37";
const AMBER = "#bf8700";
const RED = "#cf222e";
const BLUE = "#0969da";
```

## Component X Layer Balance

The OBS-T corpus attributes each correction event to an error component (the part of the dictionary entry that was wrong) and a data layer (whether the event came from the legacy form layer of cfr.tsv records, or the git layer of csl-orig commit diffs). This chart shows whether the same components appear proportionally in both layers or whether certain error types are specific to one era — which would affect the corpus's temporal generalisability claims.

> **How to read:** Each row is one error component; bars stack form-layer (blue) and git-layer (amber) event counts. **Example 1:** A component with a much larger git-layer bar than form bar means that error type became common only after systematic git-tracked corrections began in 2019 — it is not well-represented in the pre-2019 legacy record. **Example 2:** A component whose bars are roughly equal in both layers appeared consistently throughout the full 2014–2026 span — a temporally stable error category that supports generalisability claims.

```js
const componentLayer = Array.from(d3.rollup(component, v => d3.sum(v, d => d.count), d => d.component, d => d.layer), ([name, inner]) =>
  Array.from(inner, ([layer, count]) => ({component: name, layer, count}))
).flat().sort((a, b) => d3.descending(a.count, b.count));
const componentOrder = Array.from(d3.rollup(componentLayer, v => d3.sum(v, d => d.count), d => d.component), ([component, count]) => ({component, count}))
  .sort((a, b) => b.count - a.count).map(d => d.component);

display(Plot.plot({
  width,
  height: 340,
  marginLeft: 120,
  x: {label: "Events", grid: true},
  y: {label: null, domain: componentOrder},
  color: {legend: true, domain: ["form", "git"], range: [BLUE, AMBER]},
  marks: [
    Plot.barX(componentLayer, Plot.stackX({x: "count", y: "component", fill: "layer", tip: true})),
    Plot.ruleX([0])
  ]
}))
```

> **Conclusion:** Layer imbalances identify components that are over- or under-represented in one era of the corpus. A component dominated by the git layer is a 2019+ phenomenon; one dominated by form data is a legacy pattern. This matters for the OBS-T paper: any temporal-generalisability claim should be checked against this balance before submission.

## Edit-Space X Unit Mix

A heatmap of how often each edit unit type (letter, diacritic, digit, punctuation, etc.) appears in each edit space (the number of changed character positions). Edit space 1 means a single character was swapped; edit space 2 means two positions changed; and so on. This is the quantitative foundation of the OBS-T micro-edit finding: most corrections change very few characters.

> **How to read:** Row = edit unit type; column = edit space (number of changed positions); colour = count of substitution events. **Example 1:** A bright cell at (letter, 1) means the most common single-position change is one letter for another — the classic OCR error or typo pattern. **Example 2:** A bright cell at (punctuation, 2) indicates that many two-position changes involve punctuation — consistent with spacing and punctuation normalisation accounting for a large share of corrections.

```js
const unitSpace = Array.from(d3.rollup(confus, v => d3.sum(v, d => d.count), d => d.unit, d => d.edit_space), ([unit, inner]) =>
  Array.from(inner, ([edit_space, count]) => ({unit, edit_space, count}))
).flat();
const unitOrder = Array.from(d3.rollup(unitSpace, v => d3.sum(v, d => d.count), d => d.unit), ([unit, count]) => ({unit, count}))
  .sort((a, b) => b.count - a.count).map(d => d.unit);

display(Plot.plot({
  width,
  height: 380,
  marginLeft: 120,
  x: {label: "Edit space"},
  y: {label: null, domain: unitOrder},
  color: {scheme: "YlOrRd", legend: true, label: "Substitutions"},
  marks: [
    Plot.cell(unitSpace, {x: "edit_space", y: "unit", fill: "count", tip: true})
  ]
}))
```

> **Conclusion:** The edit-space matrix quantifies the micro-edit dominance claim from OBS-T H1. If the brightest cells cluster at edit-space 1 and 2, most corrections are minimal — one or two character substitutions — which is the core empirical finding supporting the paper's framing of dictionary correction as a high-frequency micro-task.

## Campaign Magnitude Timeline

Each correction campaign — a coordinated batch of cfr.tsv form-layer events submitted together — is plotted at its date with a circle sized by its magnitude (number of events contributed). Colour encodes the campaign category. The timeline reveals when the historic digitisation pushes happened, how large they were relative to each other, and whether recent campaigns are comparable in scale to the founding-era batches.

> **How to read:** Each dot is one campaign; x = date, y = magnitude, dot size = magnitude (linear, so large dots are visually much larger). **Example 1:** A very large dot in 2015–2018 marks one of the founding correction waves — bulk submissions when the cfr.tsv correction log was being populated from scanned materials. **Example 2:** Small dots in recent years indicate ongoing maintenance corrections rather than large campaigns — consistent with the project having shifted from bulk upload to incremental refinement.

```js
const campaignRows = campaigns.map(d => ({...d, day: new Date(d.date)})).filter(d => !Number.isNaN(+d.day));

display(Plot.plot({
  width,
  height: 360,
  x: {label: "Campaign date", type: "utc"},
  y: {label: "Magnitude", grid: true},
  color: {legend: true, scheme: "Tableau10"},
  marks: [
    Plot.dot(campaignRows, {x: "day", y: "magnitude", r: d => Math.max(3, Math.sqrt(d.magnitude)), fill: "category", fillOpacity: 0.75, tip: true}),
    Plot.ruleY([0])
  ]
}))
```

> **Conclusion:** The campaign timeline makes the project's correction history legible at a glance: large early dots are the founding digitisation push; smaller later dots are maintenance refinements. If the most recent dot is small, the project is in a steady-state maintenance phase — which affects the OBS-T paper's framing of the corpus as a completed historical resource vs an active and growing one.

## Dictionary Event-Density Scatter

Each dictionary is plotted by its total entry count (x-axis, square-root scale) against its correction event density — events per 1,000 entries (y-axis). Dot size encodes raw event count; colour shows the most common error component for that dictionary. This reveals which dictionaries have been corrected most intensively relative to their size, and which are large but lightly corrected — either because they are high-quality or because correction attention has not yet reached them.

> **How to read:** Each dot is one dictionary; x = entry count (sqrt scale), y = events per 1,000 entries, colour = dominant error component. **Example 1:** A dot in the upper-left (small dictionary, high density) is a small resource that has been very intensively corrected — every thousand entries generated many correction events. **Example 2:** A dot in the lower-right (large dictionary, low density) is a large resource with sparse correction coverage — either quality is high and few errors were found, or it has not yet been fully reviewed.

```js
const minEvents = view(Inputs.range([0, 500], {step: 10, value: 30, label: "Minimum events"}));
```

```js
const dictDensity = dicts.filter(d => (+d.events || 0) >= minEvents && (+d.entries || 0) > 0);

display(Plot.plot({
  width,
  height: 430,
  x: {label: "Entries", grid: true, type: "sqrt"},
  y: {label: "Events per 1,000 entries", grid: true},
  color: {legend: true, scheme: "Tableau10"},
  marks: [
    Plot.dot(dictDensity, {x: "entries", y: "per_1k_entries", r: d => Math.max(3, Math.sqrt(d.events) / 2), fill: "top_component", tip: true, channels: {Dictionary: "dict", Events: "events"}})
  ]
}))
```

> **Conclusion:** High-density dictionaries have received the most careful correction attention relative to their size; low-density large dictionaries represent the largest uncovered correction surface. This scatter is a prioritisation tool: large low-density dictionaries are where future correction campaigns would have the greatest per-entry impact.

## Correction Component Monthly Trend

Monthly event counts for selected error components, plotted as lines from 2014 to the present. This shows whether the balance of correction types has shifted over time — for example, whether headword errors peaked early and sense errors grew later, or whether the component mix has remained stable throughout the corpus's history. Use the checkbox selector to compare any subset of components.

> **How to read:** Each line is one selected component; x = month, y = event count. **Example 1:** A headword line that is high in 2014–2018 and then falls after 2019 means headword errors were caught in the early campaigns and the remaining corpus is cleaner on that dimension. **Example 2:** A sense line that grows after 2020 means meaning-level errors — harder to catch and requiring deeper lexicographic knowledge — are being addressed in the later, more expert-driven correction phase.

```js
const components = Array.from(new Set(monthly.map(d => d.component))).sort();
```

```js
const selectedComponents = view(Inputs.checkbox(components, {value: ["sense", "headword", "markup"].filter(d => components.includes(d)), label: "Components"}));
```

```js
const selectedComponentSet = new Set(Array.from(selectedComponents ?? []));
const monthRows = monthly
  .filter(d => selectedComponentSet.has(d.component))
  .map(d => ({...d, date: new Date(d.ym + "-01")}));

display(Plot.plot({
  width,
  height: 390,
  x: {label: "Month", type: "utc"},
  y: {label: "Events", grid: true},
  color: {legend: true, scheme: "Tableau10"},
  marks: [
    Plot.line(monthRows, {x: "date", y: "count", stroke: "component", tip: true}),
    Plot.ruleY([0])
  ]
}))
```

> **Conclusion:** Monthly component trends are the OBS-T operational health signal: if all components are flat near zero in recent months, correction activity has slowed; if they are active, the corpus is still being refined. A crossing of two component lines — e.g. sense overtaking headword — marks a phase transition in the project's correction focus and should be noted in the OBS-T paper's temporal-analysis section.

[Back to overview](/)
