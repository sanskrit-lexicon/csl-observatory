---
title: Error typology
toc: true
---

# Error typology of digital Sanskrit dictionaries

What kinds of errors are corrected in the Cologne Digital Sanskrit Lexicon, where
in the entry they occur, and how the profile changes over twelve years. Each of
the **50,953** correction events (2014–2026, 43 dictionaries) is normalized to IAST
and attributed to the dictionary *microstructure component* it repairs. See the
finding [`reports/obs_t_typology.md`](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/reports/obs_t_typology.md)
and the [design spec](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/docs/ERROR_TYPOLOGY_DESIGN.md).

```js
const summary  = await FileAttachment("data/obs_t_summary.json").json();
const timeline = await FileAttachment("data/obs_t_timeline.csv").csv({typed: true});
const monthly  = await FileAttachment("data/obs_t_timeline_monthly.csv").csv({typed: true});
const dicts    = await FileAttachment("data/obs_t_dict.csv").csv({typed: true});
const confus   = await FileAttachment("data/obs_t_confusion.csv").csv({typed: true});
const cross    = await FileAttachment("data/obs_t_crosswalk.csv").csv({typed: true});
const baselines = await FileAttachment("data/obs_t_baselines.json").json();
```

<div class="grid grid-cols-4">
  <div class="card"><h2>Correction events</h2><span class="big">${summary.events.toLocaleString("en-US")}</span></div>
  <div class="card"><h2>Dictionaries</h2><span class="big">${summary.dictionaries}</span></div>
  <div class="card"><h2>Correctors</h2><span class="big">${summary.correctors}</span></div>
  <div class="card"><h2>Derived (not heuristic)</h2><span class="big">${summary.derivedPct}%</span></div>
</div>

## Two axes: location × edit-type

Each correction is described on two orthogonal axes — **where** in the entry it
lands (the microstructure *location*) and **what kind** of change it is (the
*edit-type*). Mixing them was a pitfall; keeping them apart is the honest typology.

### Axis A — location (derived labels)

Where in the entry the correction repairs. Git layer is attributed positionally
from the source XML tags; the form layer is joined to `csl-orig` by headword.
Reported on derived labels (location is not guessed when the join fails).

```js
const locTotals = (summary.locationDerived ?? summary.components).map(([location, count]) => ({location, count}));
```

```js
Plot.plot({
  width, height: 300, marginLeft: 110,
  x: {label: "events (derived)", grid: true},
  y: {label: null, domain: locTotals.map(d => d.location)},
  marks: [
    Plot.barX(locTotals, {x: "count", y: "location", fill: "#5319e7", tip: true}),
    Plot.ruleX([0])
  ]
})
```

Corrections concentrate in the **sense (definition)** and **headword** — the
meaning-bearing fields.

### Axis B — edit-type (all events)

What kind of change. Every category is a surface micro-edit; there is no
"content rewrite" type — even corrections to definitions are small form fixes.

```js
const etTotals = (summary.editType ?? []).map(([type, count]) => ({type, count}));
```

```js
Plot.plot({
  width, height: 300, marginLeft: 110,
  x: {label: "events", grid: true},
  y: {label: null, domain: etTotals.map(d => d.type)},
  marks: [
    Plot.barX(etTotals, {x: "count", y: "type", fill: "#fb8c00", tip: true}),
    Plot.ruleX([0])
  ]
})
```

## Twelve-year timelapse — location over time

Monthly correction volume, coloured by the location repaired. The form era and the
git era meet at mid-2019 into one continuous record.

```js
const monthlyDated = monthly.map(d => ({...d, date: new Date(d.ym + "-01")}));
```

```js
Plot.plot({
  width, height: 380,
  x: {label: null},
  y: {label: "events / month", grid: true},
  color: {legend: true, scheme: "Tableau10", label: "location"},
  marks: [
    Plot.areaY(monthlyDated, {x: "date", y: "count", fill: "component", tip: true}),
    Plot.ruleY([0])
  ]
})
```

### Scrub a year

```js
const year = view(Inputs.range([2014, 2026], {step: 1, value: 2016, label: "Year"}));
```

```js
const yearData = d3.flatRollup(
    timeline.filter(d => +d.year === year),
    v => d3.sum(v, x => x.count), d => d.component)
  .map(([component, count]) => ({component, count}))
  .sort((a, b) => b.count - a.count);
```

```js
Plot.plot({
  width, height: 300, marginLeft: 110,
  title: `Components corrected in ${year}`,
  x: {label: "events", grid: true},
  y: {label: null, domain: yearData.map(d => d.component)},
  marks: [
    Plot.barX(yearData, {x: "count", y: "component", fill: "#fb8c00", tip: true}),
    Plot.ruleX([0])
  ]
})
```

## Cross-dictionary error density

Corrections per 1,000 entries (`<L>` count), dictionaries with ≥30 events — a
size-normalized quality signal, so a small heavily-edited dictionary is not hidden
by a large one.

```js
const dens = dicts.filter(d => d.entries && d.events >= 30)
  .sort((a, b) => b.per_1k_entries - a.per_1k_entries).slice(0, 20);
```

```js
Plot.plot({
  width, height: 460, marginLeft: 70,
  x: {label: "corrections per 1,000 entries", grid: true},
  y: {label: null, domain: dens.map(d => d.dict)},
  marks: [
    Plot.barX(dens, {x: "per_1k_entries", y: "dict", fill: "top_component", tip: true}),
    Plot.ruleX([0])
  ],
  color: {legend: true}
})
```

## Character confusion — the clean Sanskrit signal

Single-character substitutions in the form layer (IAST), restricted to consonants:
the genuine phoneme-confusion signal, led by the classic **b ↔ v** merger.

```js
const cons = confus.filter(d => d.layer === "form" && d.unit === "consonant")
  .sort((a, b) => b.count - a.count).slice(0, 25);
```

```js
Plot.plot({
  width, height: 420, marginLeft: 70,
  x: {label: null, domain: [...new Set(cons.map(d => d.from))]},
  y: {label: null, domain: [...new Set(cons.map(d => d.to))]},
  color: {scheme: "YlOrRd", legend: true, label: "count"},
  marks: [
    Plot.cell(cons, {x: "from", y: "to", fill: "count", tip: true})
  ]
})
```

## Crosswalk typologies

The same events under the OCR/digitization and textual-criticism (Katre) frames,
derived from the edit-op trace.

```js
const ocr = d3.flatRollup(cross.filter(d => d.scheme === "ocr"),
    v => d3.sum(v, x => x.count), d => d.label)
  .map(([label, count]) => ({frame: "OCR", label, count}));
const tc = d3.flatRollup(cross.filter(d => d.scheme === "textcrit"),
    v => d3.sum(v, x => x.count), d => d.label)
  .map(([label, count]) => ({frame: "Textual criticism", label, count}));
```

```js
Plot.plot({
  width, height: 320, marginLeft: 110, marginRight: 80,
  x: {label: "events", grid: true},
  fy: {label: null},
  y: {label: null},
  color: {legend: true, scheme: "Set2"},
  marks: [
    Plot.barX(ocr.concat(tc), {x: "count", y: "label", fy: "frame", fill: "frame", tip: true, sort: {y: "x", reverse: true}}),
    Plot.ruleX([0])
  ]
})
```

## Reference baselines

Stdlib-only, deterministic baselines that define the NLP tasks the released corpus
supports, on a temporal split. See [`reports/obs_t_baselines.md`](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/reports/obs_t_baselines.md)
and the [datasheet](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/docs/DATASHEET.md).

<div class="grid grid-cols-3">
  <div class="card"><h2>Detection (char-LM, minimal pair)</h2><span class="big">${baselines.detection.pairwise_accuracy}</span><br>pairwise accuracy (chance 0.5)</div>
  <div class="card"><h2>Correction (noisy-channel)</h2><span class="big">${baselines.correction.accuracy_at_1}</span><br>accuracy@1 — ${baselines.correction.dist1_share} reachable at dist-1</div>
  <div class="card"><h2>Type classifier (Naive Bayes)</h2><span class="big">${baselines.classification.accuracy}</span><br>accuracy vs ${baselines.classification.majority_baseline_accuracy} majority</div>
</div>

Detection and correction are deliberately hard for context-free baselines — a
one-character-different Sanskrit string is usually also plausible — which is the
headroom a neural model is meant to fill. Error-type classification clearly beats
the majority class.

## How much correction work is left? (capture–recapture)

The two OBS-T layers — the form era (2014–2019 web submissions) and the git era (2019–2026 commits) — act as two capture occasions over error-prone records. The Chapman mark–recapture estimator turns their overlap into an estimate of the total error-site population, i.e. the work *remaining*. Full method, sensitivity checks, and honest assumption-violation discussion: [`reports/error_recapture.md`](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/reports/error_recapture.md), generated by [`scripts/error_recapture.py`](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/scripts/error_recapture.py).

```js
const recap = await FileAttachment("data/error_recapture.csv").csv({typed: true});
const recapEst = recap.filter(d => d.estimable === 1);
const recapTotal = d3.sum(recapEst, d => d.n_hat);
const recapDone = d3.sum(recapEst, d => d.s_observed);
const recapRemaining = d3.sum(recapEst, d => d.remaining_hat);
```

<div class="grid grid-cols-4">
  <div class="card"><h2>Dicts with estimable overlap</h2><span class="big">${recapEst.length} / ${recap.length}</span></div>
  <div class="card"><h2>Estimated error-prone records</h2><span class="big">~${recapTotal.toLocaleString("en-US")}</span></div>
  <div class="card"><h2>Corrected so far</h2><span class="big">${recapDone.toLocaleString("en-US")}</span></div>
  <div class="card"><h2>Estimated still awaiting</h2><span class="big">~${recapRemaining.toLocaleString("en-US")}</span></div>
</div>

> **How to read:** For each dictionary with enough two-era overlap (≥10 recaptures), the bar is the estimated population of error-prone records: the dark segment is what has already been corrected, the light segment the estimated remainder, and the black whisker the 95% confidence interval (statistical-only — the design biases discussed in the report are not inside it). **Example 1:** If the dark segment is a small fraction of the bar, most of the correction work in that dictionary still lies ahead. **Example 2:** A bar that reaches its dictionary's full record count (bur, capped) means the analysis cannot distinguish the error population from the whole dictionary — treat it as "effectively unproofread", not as a precise count.

```js
const recapLong = recapEst.flatMap(d => [
  {dict: d.dict, part: "Corrected", value: d.s_observed},
  {dict: d.dict, part: "Estimated remaining", value: d.remaining_hat}
]);
```

```js
Plot.plot({
  width,
  height: 220,
  marginLeft: 60,
  x: {label: "Records (estimated error-prone population)", grid: true},
  y: {label: null, domain: recapEst.map(d => d.dict)},
  color: {domain: ["Corrected", "Estimated remaining"], range: ["#0969da", "#9cc7f5"], legend: true},
  marks: [
    Plot.barX(recapLong, {x: "value", y: "dict", fill: "part", inset: 1, tip: true}),
    Plot.ruleY(recapEst, {y: "dict", x1: "ci_low", x2: "ci_high", stroke: "black", strokeWidth: 1.5}),
    Plot.text(recapEst, {x: "n_hat", y: "dict", text: d => `~${(100 * d.s_observed / d.n_hat).toFixed(0)}% done`, dx: 40})
  ]
})
```

> **Conclusion:** The two correction eras overlap so little that, under mark–recapture logic, the corrected record set must be a minority of the error population: roughly **10–14% of the estimated correction work is done** in the three estimable dictionaries (pw, mw, bur), with the heterogeneity scenario implying even less. For the other 40 dictionaries the overlap is too thin to estimate at all — itself evidence of how era-partitioned and concentrated correction effort has been.

---

*Object of analysis: corrections over dictionary source text — in scope per
[`docs/BOUNDARY_RULES.md`](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/docs/BOUNDARY_RULES.md).
The lexicographic-structure interpretation cross-links to
[`csl-atlas`](https://github.com/sanskrit-lexicon/csl-atlas).*
