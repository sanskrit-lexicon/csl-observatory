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

## Edit-Space X Unit Mix

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

## Campaign Magnitude Timeline

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

## Dictionary Event-Density Scatter

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

## Correction Component Monthly Trend

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

[Back to overview](/)
