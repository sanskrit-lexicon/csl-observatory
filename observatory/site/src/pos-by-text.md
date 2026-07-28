---
title: POS distribution by text
toc: true
---

<link rel="stylesheet" href="./palette.css">

# POS distribution by text

UD part-of-speech share across the **270** texts of the Digital Corpus of Sanskrit
(DCS). Census magnitude bars only answered “how many tokens”; this page answers
**which texts skew noun-heavy vs verb-heavy** — the register/genre signal behind
the L3 POS feed.

```js
const pos = await FileAttachment("data/pos_distribution_per_text.csv").csv({typed: true});
```

```js
const paletteStyles = getComputedStyle(document.documentElement);
const token = (name) => paletteStyles.getPropertyValue(name).trim();
const OBS_ACCENT = token("--obs-accent");
const OBS_MUTED = token("--obs-muted");
const OBS_GOOD = token("--obs-good");
const OBS_WARN = token("--obs-warn");
const OBS_SEQ = [1, 2, 3, 4, 5, 6, 7].map((i) => token(`--obs-seq-${i}`));
const seqInterpolate = d3.piecewise(d3.interpolateRgb, OBS_SEQ);
```

```js
const nRows = pos.length;
const nTexts = new Set(pos.map((d) => d.text)).size;
const totalTokens = d3.sum(pos, (d) => d.count);
const uposOrder = Array.from(
  d3.rollup(pos, (v) => d3.sum(v, (d) => d.count), (d) => d.upos),
  ([upos, count]) => ({upos, count})
).sort((a, b) => b.count - a.count).map((d) => d.upos);
const textTotals = Array.from(
  d3.rollup(pos, (v) => d3.sum(v, (d) => d.count), (d) => d.text),
  ([text, tokens]) => ({text, tokens})
).sort((a, b) => b.tokens - a.tokens);
```

<div class="grid grid-cols-4">
  <div class="card"><h2>Texts</h2><span class="big">${nTexts.toLocaleString()}</span></div>
  <div class="card"><h2>UPOS rows</h2><span class="big">${nRows.toLocaleString()}</span></div>
  <div class="card"><h2>Tokens</h2><span class="big">${totalTokens.toLocaleString()}</span></div>
  <div class="card"><h2>UPOS tags</h2><span class="big">${uposOrder.length}</span></div>
</div>

:::note
**Trust block.** Source: [`data/pos_distribution_per_text.tsv`](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/data/pos_distribution_per_text.tsv)
(loader: `observatory/site/src/data/pos_distribution_per_text.csv.py`, read-only).
Generator: [`scripts/pos_distribution_per_text.py`](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/scripts/pos_distribution_per_text.py)
from VisualDCS `dcs_full.sqlite`. **n = ${nRows.toLocaleString()}** rows · **${nTexts}** texts ·
**${totalTokens.toLocaleString()}** tokens. Data date: 13-07-2026 (H817 WS1.2).
DCS tags unaccented text — coarse 11-way UD `upos` only; no class I/VI or aorist/perfect split.
:::

## Top texts — UPOS stack

Stacked shares for the largest texts by token count (default top 25). Epic narrative
tends toward higher VERB%; medical/śāstra denser in NOUN%.

> **How to read:** Each horizontal bar is one text; segments are UPOS shares of that
> text’s tokens. **Example 1:** A long NOUN segment with a short VERB segment is a
> catalogue-like or technical register. **Example 2:** VERB near ~20% with NOUN ~40%
> matches the epic average (Mahābhārata, Rāmāyaṇa).

```js
const topN = view(Inputs.range([10, 40], {value: 25, step: 1, label: "Top-N texts by tokens"}));
```

```js
const topTexts = new Set(textTotals.slice(0, topN).map((d) => d.text));
const stackRows = pos.filter((d) => topTexts.has(d.text));
const yDomain = textTotals.slice(0, topN).map((d) => d.text);

display(Plot.plot({
  width,
  height: Math.max(360, topN * 18),
  marginLeft: 160,
  x: {label: "Share of text tokens", domain: [0, 1], percent: true, grid: true},
  y: {label: null, domain: yDomain},
  color: {legend: true, domain: uposOrder, range: OBS_SEQ.concat(OBS_MUTED), label: "UPOS"},
  marks: [
    Plot.barX(stackRows, {
      x: (d) => d.pct_of_text / 100,
      y: "text",
      fill: "upos",
      tip: true,
      channels: {Tokens: "count", "pct_of_text": "pct_of_text"}
    })
  ]
}))
```

> **Conclusion:** The stack separates catalogue/śāstra (noun-dominant medical and purāṇa
> blocks) from narrative epic and kathā (higher VERB%). Register, not dictionary markup,
> is what moves the POS profile.

## Heatmap — text × UPOS (top 40)

Top 40 texts by total tokens; remaining texts are omitted so the grid stays readable.

> **How to read:** Row = text, column = UPOS, colour = `pct_of_text`. **Example 1:** A
> bright NOUN cell on a medical text is high nominal density. **Example 2:** A bright
> PART/PRON cell marks formulaic particle-rich prose or dialogue.

```js
const heatTexts = textTotals.slice(0, 40).map((d) => d.text);
const heatSet = new Set(heatTexts);
const heatRows = pos.filter((d) => heatSet.has(d.text));

display(Plot.plot({
  width,
  height: 720,
  marginLeft: 160,
  marginBottom: 40,
  x: {label: "UPOS", domain: uposOrder},
  y: {label: null, domain: heatTexts},
  color: {type: "linear", interpolate: seqInterpolate, legend: true, label: "% of text"},
  marks: [
    Plot.cell(heatRows, {
      x: "upos",
      y: "text",
      fill: "pct_of_text",
      tip: true,
      channels: {Tokens: "count"}
    })
  ]
}))
```

## UPOS share distribution across texts

Each point is one text’s `pct_of_text` for that UPOS — the spread of genre, not the
corpus mean alone.

> **How to read:** Box (or jittered dots) of percentage by UPOS. **Example 1:** A tight
> NOUN box around 40% means most texts sit near the epic mean. **Example 2:** A long
> upper whisker on NOUN is a technical text pulling far above the median.

```js
display(Plot.plot({
  width,
  height: 380,
  marginLeft: 50,
  x: {label: "UPOS", domain: uposOrder},
  y: {label: "% of text", grid: true},
  color: {domain: uposOrder, range: OBS_SEQ.concat(OBS_MUTED)},
  marks: [
    Plot.boxY(pos, {x: "upos", y: "pct_of_text", fill: OBS_MUTED, fillOpacity: 0.35}),
    Plot.dot(pos, {
      x: "upos",
      y: "pct_of_text",
      fill: "upos",
      fillOpacity: 0.25,
      r: 2,
      tip: true,
      channels: {Text: "text", Tokens: "count"}
    })
  ]
}))
```

## Outlier ranks — NOUN% and VERB%

Texts ranked by noun share and verb share (among texts with ≥500 tokens so tiny
fragments do not dominate).

> **How to read:** Horizontal bars of share for the top/bottom tails. **Example 1:** Highest
> NOUN% texts are typically medical or list-like. **Example 2:** Highest VERB% texts lean
> narrative or ritual instruction.

```js
const byText = Array.from(
  d3.group(pos, (d) => d.text),
  ([text, rows]) => {
    const tokens = d3.sum(rows, (d) => d.count);
    const pct = (upos) => {
      const r = rows.find((d) => d.upos === upos);
      return r ? r.pct_of_text : 0;
    };
    return {text, tokens, noun_pct: pct("NOUN"), verb_pct: pct("VERB")};
  }
).filter((d) => d.tokens >= 500);
const nounTop = byText.slice().sort((a, b) => b.noun_pct - a.noun_pct).slice(0, 12);
const verbTop = byText.slice().sort((a, b) => b.verb_pct - a.verb_pct).slice(0, 12);
```

```js
display(Plot.plot({
  width,
  height: 320,
  marginLeft: 160,
  x: {label: "NOUN % of text", grid: true},
  y: {label: null, domain: nounTop.map((d) => d.text)},
  marks: [
    Plot.barX(nounTop, {
      x: "noun_pct",
      y: "text",
      fill: OBS_ACCENT,
      tip: true,
      channels: {Tokens: "tokens", "VERB %": "verb_pct"}
    }),
    Plot.ruleX([0])
  ]
}))
```

```js
display(Plot.plot({
  width,
  height: 320,
  marginLeft: 160,
  x: {label: "VERB % of text", grid: true},
  y: {label: null, domain: verbTop.map((d) => d.text)},
  marks: [
    Plot.barX(verbTop, {
      x: "verb_pct",
      y: "text",
      fill: OBS_GOOD,
      tip: true,
      channels: {Tokens: "tokens", "NOUN %": "noun_pct"}
    }),
    Plot.ruleX([0])
  ]
}))
```

> **Conclusion:** The same feed that looked flat at census level (NOUN ~42%, VERB ~18%
> corpus-wide) is **text-heterogeneous**: medical and technical works pull NOUN% into the
> 50s; narrative and some ritual texts push VERB% above the epic band. Genre skew is the
> analytical payload of this page.

## Data table

```js
const tableFilter = view(Inputs.search(pos, {placeholder: "Filter text or UPOS…", label: "Search"}));
```

```js
display(Inputs.table(tableFilter, {
  columns: ["text", "upos", "count", "pct_of_text"],
  sort: "count",
  reverse: true,
  rows: 20
}))
```

Download source TSV:
[`pos_distribution_per_text.tsv`](https://raw.githubusercontent.com/sanskrit-lexicon/csl-observatory/main/data/pos_distribution_per_text.tsv)
· report:
[`reports/pos_distribution_per_text.md`](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/reports/pos_distribution_per_text.md)
· [Data downloads](./data) · sibling census: [L3 Corpus](./census-l3-corpus).
