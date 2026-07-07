---
title: Correction Anatomy
toc: true
---

<link rel="stylesheet" href="./palette.css">

# Correction Anatomy

Who fixes what in the OBS-T correction corpus, and how letters break: the character-confusion structure, its directionality, and the concentration and tenure of correction labor. All data is read from the committed OBS-T aggregates; the inferential companions are hypotheses H5, H6 and H8 in the Phase-3 spec.

```js
const confus = await FileAttachment("data/obs_t_confusion.csv").csv({typed: true});
const correctors = await FileAttachment("data/obs_t_corrector.csv").csv({typed: true});
const corrComp = await FileAttachment("data/obs_t_corrector_component.csv").csv({typed: true});
```

```js
// Chart colors come from palette.css tokens (light + dark), never hard-coded here.
const paletteStyles = getComputedStyle(document.documentElement);
const token = (name) => paletteStyles.getPropertyValue(name).trim();
const OBS_ACCENT = token("--obs-accent");
const OBS_MUTED = token("--obs-muted");
const OBS_GOOD = token("--obs-good");
const OBS_WARN = token("--obs-warn");
const OBS_BAD = token("--obs-bad");
const OBS_SEQ = [1, 2, 3, 4, 5, 6, 7].map((i) => token(`--obs-seq-${i}`));
const seqInterpolate = d3.piecewise(d3.interpolateRgb, OBS_SEQ);
```

## Character Confusion Matrix

Every substitution edit in the corpus is a `from → to` character pair. This matrix shows the full character-level error space for one encoding regime at a time (IAST Sanskrit spans by default; raw markup/SLP1 edits are separate regimes and are not mixed in). The top 40 characters by total involvement get their own row/column; everything rarer is binned into "·other".

> **How to read:** Row = the character that was wrong (`from`); column = what it was corrected to (`to`); colour = event count on a log scale, so both the dominant pairs and the long tail stay visible. **Example 1:** A bright cell at row `P`, column `p` means upper-case→lower-case folding of that letter is a dominant correction. **Example 2:** A bright diacritic cell such as `m → ṃ` marks anusvāra repair — a diacritic restoration, not a lexical change.

```js
const editSpace = view(Inputs.select(
  Array.from(new Set(confus.map((d) => d.edit_space))).sort(),
  {value: "iast", label: "Edit space"}
));
```

```js
const spaceRows = confus.filter((d) => d.edit_space === editSpace);
const marginal = d3.rollup(
  spaceRows.flatMap((d) => [{ch: String(d.from), count: d.count}, {ch: String(d.to), count: d.count}]),
  (v) => d3.sum(v, (d) => d.count),
  (d) => d.ch
);
const topChars = new Set(Array.from(marginal, ([ch, count]) => ({ch, count}))
  .sort((a, b) => b.count - a.count).slice(0, 40).map((d) => d.ch));
const bin = (ch) => (topChars.has(String(ch)) ? String(ch) : "·other");
const cells = Array.from(
  d3.rollup(spaceRows, (v) => d3.sum(v, (d) => d.count), (d) => bin(d.from), (d) => bin(d.to)),
  ([from, inner]) => Array.from(inner, ([to, count]) => ({from, to, count}))
).flat();
const charOrder = Array.from(marginal, ([ch, count]) => ({ch, count}))
  .filter((d) => topChars.has(d.ch)).sort((a, b) => b.count - a.count).map((d) => d.ch)
  .concat(["·other"]);

display(Plot.plot({
  width,
  height: 720,
  marginLeft: 60,
  marginBottom: 40,
  x: {label: "corrected to →", domain: charOrder},
  y: {label: "↓ was", domain: charOrder},
  color: {type: "log", interpolate: seqInterpolate, legend: true, label: "Events (log)"},
  marks: [
    Plot.cell(cells, {x: "to", y: "from", fill: "count", tip: true})
  ]
}))
```

> **Conclusion:** In the IAST space, case folding (`P → p`, 2,945 events) and punctuation swaps dominate the character-level error surface — corrections are typographic, not lexical. This is the OBS-T micro-edit finding (H1) made visible: the corpus's modal correction changes one character's case or diacritic, not a word.

## Confusion Asymmetry

Companion to hypothesis H8: are confusions directional? For every unordered character pair with at least 30 total events in the selected edit space, this plots the share of events flowing in the pair's dominant direction against the pair's total volume. Under the null (symmetric noise) shares sit near 0.5; a systematic error source (OCR, case-folding, encoding conversion) pushes shares toward 1. Whiskers are Wilson 95% CIs; emphasized dots are significant after a Benjamini-Hochberg correction (exact two-sided binomial, q < 0.05) across all tested pairs.

> **How to read:** Each dot is one character pair; x = total events (log), y = share in the dominant direction (0.5 = perfectly symmetric, 1.0 = one-way). **Example 1:** A large-volume pair at share ≈ 1.0 with a tight CI is a one-way error channel — e.g. upper case always folding down, never up. **Example 2:** A pair whose CI whisker crosses 0.5 (muted colour) is directionally undecided — its two directions occur at statistically indistinguishable rates.

```js
// Exact two-sided binomial test (p = 0.5) + Wilson CI, computed per pair in-page.
// The inferential artifact lives in the Part-1 rigor script; this is its picture.
function binomTwoSided(k, n) {
  const logPmf = new Float64Array(n + 1);
  let lp = -n * Math.LN2; // log pmf(0) = log(0.5^n)
  logPmf[0] = lp;
  for (let i = 1; i <= n; i++) {
    lp += Math.log((n - i + 1) / i);
    logPmf[i] = lp;
  }
  const threshold = logPmf[k] + 1e-9;
  let p = 0;
  for (let i = 0; i <= n; i++) if (logPmf[i] <= threshold) p += Math.exp(logPmf[i]);
  return Math.min(1, p);
}
function wilson(k, n, z = 1.96) {
  const phat = k / n, z2 = z * z;
  const centre = (phat + z2 / (2 * n)) / (1 + z2 / n);
  const half = (z * Math.sqrt((phat * (1 - phat) + z2 / (4 * n)) / n)) / (1 + z2 / n);
  return [Math.max(0, centre - half), Math.min(1, centre + half)];
}
const directed = d3.rollup(spaceRows, (v) => d3.sum(v, (d) => d.count), (d) => `${d.from}\u0000${d.to}`);
const seen = new Set();
const pairs = [];
for (const [key, ab] of directed) {
  const [a, b] = key.split("\u0000");
  if (a === b) continue;
  const revKey = `${b}\u0000${a}`;
  if (seen.has(revKey)) continue;
  seen.add(key);
  const ba = directed.get(revKey) ?? 0;
  const total = ab + ba;
  if (total < 30) continue;
  const [hi, lo, dir] = ab >= ba ? [ab, ba, `${a} → ${b}`] : [ba, ab, `${b} → ${a}`];
  const [ciLo, ciHi] = wilson(hi, total);
  pairs.push({pair: dir, total, share: hi / total, ciLo, ciHi, p: binomTwoSided(hi, total)});
}
// Benjamini-Hochberg across all tested pairs
const byP = pairs.slice().sort((a, b) => a.p - b.p);
let qMin = 1;
for (let i = byP.length - 1; i >= 0; i--) {
  qMin = Math.min(qMin, (byP[i].p * byP.length) / (i + 1));
  byP[i].q = qMin;
}
for (const d of pairs) d.significant = d.q < 0.05;

display(Plot.plot({
  width,
  height: 420,
  x: {label: "Total events (log)", type: "log", grid: true},
  y: {label: "Dominant-direction share", domain: [0.4, 1.02], grid: true},
  color: {
    legend: true,
    domain: ["BH-significant (q < 0.05)", "not significant"],
    range: [OBS_ACCENT, OBS_MUTED]
  },
  marks: [
    Plot.ruleY([0.5], {stroke: OBS_MUTED, strokeDasharray: "4,3"}),
    Plot.ruleX(pairs, {x: "total", y1: "ciLo", y2: "ciHi", stroke: OBS_MUTED, strokeOpacity: 0.6}),
    Plot.dot(pairs, {
      x: "total", y: "share",
      fill: (d) => d.significant ? "BH-significant (q < 0.05)" : "not significant",
      r: 4, tip: true, channels: {Pair: "pair", q: "q"}
    })
  ]
}))
```

> **Conclusion:** The high-volume confusions sit far above 0.5 with tight CIs: they have a dominant direction, so the error source is systematic — OCR misreads, case-folding, and encoding conversion each push characters one way — rather than symmetric typing noise. That directionality is exploitable: a correction assistant can rank candidate fixes by the known flow direction (H8's practical payoff).

## Corrector Pareto Curve

The correction corpus records 52k events by 60 attributed correctors. Ranking correctors by event count and accumulating their share shows how concentrated the labor is — the event-level restatement of the org's bus-factor finding.

> **How to read:** x = correctors ranked by events (1 = most prolific), y = cumulative share of all events; the dashed line marks 80%. **Example 1:** The curve crossing 0.8 at rank 2 means two people carry four fifths of thirteen years of corrections. **Example 2:** A long flat tail past rank 10 means the remaining correctors are drive-by contributors whose combined weight is marginal.

```js
const ranked = correctors.slice().sort((a, b) => b.events - a.events);
const totalEvents = d3.sum(ranked, (d) => d.events);
let cum = 0;
const pareto = ranked.map((d, i) => {
  cum += d.events;
  return {rank: i + 1, corrector: d.name || d.corrector, events: d.events, cumShare: cum / totalEvents};
});

display(Plot.plot({
  width,
  height: 360,
  x: {label: "Corrector rank", grid: true},
  y: {label: "Cumulative share of events", domain: [0, 1], percent: false, grid: true},
  marks: [
    Plot.ruleY([0.8], {stroke: OBS_WARN, strokeDasharray: "4,3"}),
    Plot.line(pareto, {x: "rank", y: "cumShare", stroke: OBS_ACCENT}),
    Plot.dot(pareto.slice(0, 10), {x: "rank", y: "cumShare", fill: OBS_ACCENT, r: 3, tip: true, channels: {Corrector: "corrector", Events: "events"}})
  ]
}))
```

The same head of the distribution, in absolute events:

```js
display(Plot.plot({
  width,
  height: 320,
  marginLeft: 130,
  x: {label: "Events", grid: true},
  y: {label: null},
  marks: [
    Plot.barX(ranked.slice(0, 10), {
      x: "events",
      y: (d) => d.name || d.corrector,
      sort: {y: "-x"},
      fill: OBS_ACCENT,
      tip: true
    }),
    Plot.ruleX([0])
  ]
}))
```

> **Conclusion:** Two of 60 correctors — `funderburkjim` (35,057 events) and `drdhaval2785` (8,248) — carry ~83% of the corpus. The bus-factor risk measured elsewhere at repo level holds at the level of individual correction events: the corpus is, empirically, the work of two hands plus a long tail.

## Corrector × Component Matrix

Companion to hypotheses H5/H6: do specialists exist *within* the corpus? Each row is one of the top-8 correctors; each cell is the share of that corrector's events landing in one error component (row-normalized, so prolific and occasional correctors are comparable).

> **How to read:** Row = corrector, column = error component (the part of the dictionary entry repaired), colour = the share of that corrector's own events in that component. **Example 1:** A row with one very bright cell is a specialist — nearly all their corrections repair one component. **Example 2:** Rows with similar colour profiles mean the typology reflects the material, not the person — everyone fixes roughly the same mix (H5's invariance claim).

```js
const topCorrectors = Array.from(
  d3.rollup(corrComp, (v) => d3.sum(v, (d) => d.count), (d) => d.corrector),
  ([corrector, count]) => ({corrector, count})
).sort((a, b) => b.count - a.count).slice(0, 8);
const topSet = new Set(topCorrectors.map((d) => d.corrector));
const rowTotals = new Map(topCorrectors.map((d) => [d.corrector, d.count]));
const nameOf = new Map(corrComp.map((d) => [d.corrector, d.name || d.corrector]));
const compOrder = Array.from(
  d3.rollup(corrComp.filter((d) => topSet.has(d.corrector)), (v) => d3.sum(v, (d) => d.count), (d) => d.component),
  ([component, count]) => ({component, count})
).sort((a, b) => b.count - a.count).map((d) => d.component);
const shares = corrComp
  .filter((d) => topSet.has(d.corrector))
  .map((d) => ({
    corrector: nameOf.get(d.corrector),
    component: d.component,
    share: d.count / rowTotals.get(d.corrector),
    count: d.count
  }));

display(Plot.plot({
  width,
  height: 340,
  marginLeft: 130,
  marginBottom: 45,
  x: {label: "Error component", domain: compOrder, tickRotate: -20},
  y: {label: null, domain: topCorrectors.map((d) => nameOf.get(d.corrector))},
  color: {type: "linear", interpolate: seqInterpolate, legend: true, label: "Share of corrector's events"},
  marks: [
    Plot.cell(shares, {x: "component", y: "corrector", fill: "share", tip: true, channels: {Events: "count"}})
  ]
}))
```

> **Conclusion:** The matrix answers whether the corpus has internal division of labor. Broadly similar row profiles (sense-heavy for both core correctors) support H5's corrector-invariance claim — the error typology is a property of the dictionaries, not of who happened to fix them; sharply divergent rows would instead reveal in-corpus specialisation. Note the `unattributed` column reflects join failures, not a correction type.

## Corrector Tenure Spans

Each corrector's active span, from their first to their last recorded correction event. Line thickness scales with the log of their event count.

> **How to read:** Each horizontal line is one corrector (top 20 by events); it starts at their first event and ends at their last; thicker = more events. **Example 1:** A thick line spanning 2014–2026 is a founder-maintainer whose correction work never stopped. **Example 2:** A thin line a few weeks long is a drive-by corrector — one campaign, then gone.

```js
const tenured = correctors.slice().sort((a, b) => b.events - a.events).slice(0, 20)
  .map((d) => ({
    corrector: d.name || d.corrector,
    events: d.events,
    first: new Date(d.first),
    last: new Date(d.last)
  }))
  .filter((d) => !Number.isNaN(+d.first) && !Number.isNaN(+d.last));

display(Plot.plot({
  width,
  height: 440,
  marginLeft: 130,
  x: {label: "Active span", type: "utc", grid: true},
  y: {label: null, domain: tenured.map((d) => d.corrector)},
  marks: [
    Plot.link(tenured, {
      x1: "first", x2: "last", y1: "corrector", y2: "corrector",
      stroke: OBS_ACCENT,
      strokeWidth: (d) => 1 + Math.log10(d.events) * 2,
      strokeLinecap: "round"
    }),
    Plot.dot(tenured, {x: "first", y: "corrector", fill: OBS_ACCENT, r: 2.5, tip: true, channels: {Events: "events"}})
  ]
}))
```

> **Conclusion:** Correction labor is long-tenure, few-hands: the core pair's spans run 2014–2026 while most of the top 20 are short, bounded engagements. Sustainability of the correction corpus therefore depends on the same two-person continuity the community pages flag at repo level.

[Back to overview](/)
