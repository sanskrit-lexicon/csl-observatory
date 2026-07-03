---
title: Contributor network
toc: true
---

# The org as a network

Every human contributor connected to every repository they have committed to, in one picture. Bus-factor numbers say concentration exists; this page shows *where* the thin threads are — a repository whose only line reaches one person is a single point of failure drawn literally. Source data: [`contributors.csv`](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/observatory/site/src/data/contributors.csv) (alias-merged upstream), bus-factor classes from [`bus_factor.csv`](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/observatory/site/src/data/bus_factor.csv) ([`reports/bus_factor.md`](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/reports/bus_factor.md)).

```js
const contrib = await FileAttachment("data/contributors.csv").csv({typed: true});
const busfac = await FileAttachment("data/bus_factor.csv").csv({typed: true});
```

```js
// Humans only; the Actions service account is operationally a bot.
const BOTLIKE = new Set(["actions-user"]);
const human = contrib.filter(d => String(d.type).toLowerCase() !== "bot" && !BOTLIKE.has(d.login));
const totals = d3.rollup(human, v => d3.sum(v, d => d.contributions), d => d.login);
// Fold single-contribution one-off accounts out of the graph (kept in the count).
const folded = [...totals].filter(([, n]) => n < 2).map(([l]) => l);
const shown = human.filter(d => !folded.includes(d.login));
const bfClass = new Map(busfac.map(d => [d.repo, d.bus_factor]));
const repoTotals = d3.rollup(shown, v => d3.sum(v, d => d.contributions), d => d.repo);
const soloRepos = [...d3.rollup(shown, v => new Set(v.map(d => d.login)).size, d => d.repo)]
  .filter(([, n]) => n === 1).length;
const grand = d3.sum(shown, d => d.contributions);
```

<div class="grid grid-cols-4">
  <div class="card"><h2>Repositories</h2><span class="big">${repoTotals.size}</span></div>
  <div class="card"><h2>Human contributors</h2><span class="big">${totals.size}</span><br>${folded.length} one-off accounts folded</div>
  <div class="card"><h2>Repos reachable from one person only</h2><span class="big">${soloRepos}</span></div>
  <div class="card"><h2>Edges (person→repo)</h2><span class="big">${shown.length}</span></div>
</div>

## Force map

> **How to read:** Squares are repositories, colored by bus factor (red = one person carries the majority of the work, amber = two, green = three or more); circles are people, sized by their share of all contributions. A line means that person has commits in that repository; line thickness scales with how many. **Example 1:** A red square dangling from a single line is the sharpest continuity risk in the org — one account lost, and that repository's working knowledge goes with it. **Example 2:** If any square were green (bus factor ≥ 3), it would mark a repository with genuinely shared ownership — as of this snapshot, not a single one of the 76 repositories qualifies.

```js
{
  const width_ = Math.min(width, 960), height_ = 640;
  const people = [...totals].filter(([l]) => !folded.includes(l))
    .map(([login, n]) => ({id: "p:" + login, kind: "person", label: login, total: n}));
  const repos = [...repoTotals].map(([repo, n]) =>
    ({id: "r:" + repo, kind: "repo", label: repo, total: n, bf: bfClass.get(repo) ?? 0}));
  const nodes = [...people, ...repos];
  const links = shown.map(d => ({source: "p:" + d.login, target: "r:" + d.repo, w: d.contributions}));

  const bfColor = bf => bf === 1 ? "#cf222e" : bf === 2 ? "#bf8700" : bf >= 3 ? "#1a7f37" : "#8c959f";
  const rPerson = d => 4 + 26 * Math.sqrt(d.total / grand);
  const rRepo = d => 3 + 2 * Math.log10(1 + d.total);

  const sim = d3.forceSimulation(nodes)
    .force("link", d3.forceLink(links).id(d => d.id)
      .distance(l => 40 + 60 / Math.sqrt(l.w)).strength(l => Math.min(1, 0.2 + Math.log10(1 + l.w) / 4)))
    .force("charge", d3.forceManyBody().strength(-60))
    .force("center", d3.forceCenter(width_ / 2, height_ / 2))
    .force("collide", d3.forceCollide(d => (d.kind === "person" ? rPerson(d) : rRepo(d)) + 3))
    .stop();
  for (let i = 0; i < 300; ++i) sim.tick();

  const svg = d3.create("svg").attr("width", width_).attr("height", height_)
    .attr("viewBox", [0, 0, width_, height_]).style("max-width", "100%").style("height", "auto");
  svg.append("g").selectAll("line").data(links).join("line")
    .attr("x1", d => d.source.x).attr("y1", d => d.source.y)
    .attr("x2", d => d.target.x).attr("y2", d => d.target.y)
    .attr("stroke", "currentColor").attr("stroke-opacity", 0.25)
    .attr("stroke-width", d => Math.max(0.5, Math.log10(1 + d.w)));
  const repoG = svg.append("g").selectAll("rect").data(repos).join("rect")
    .attr("x", d => d.x - rRepo(d)).attr("y", d => d.y - rRepo(d))
    .attr("width", d => 2 * rRepo(d)).attr("height", d => 2 * rRepo(d))
    .attr("fill", d => bfColor(d.bf)).attr("stroke", "white").attr("stroke-width", 1);
  repoG.append("title").text(d => `${d.label} — ${d.total.toLocaleString("en-US")} contributions, bus factor ${d.bf || "n/a"}`);
  const pplG = svg.append("g").selectAll("circle").data(people).join("circle")
    .attr("cx", d => d.x).attr("cy", d => d.y).attr("r", rPerson)
    .attr("fill", "#57606a").attr("stroke", "white").attr("stroke-width", 1.5);
  pplG.append("title").text(d => `${d.label} — ${d.total.toLocaleString("en-US")} contributions (${(100 * d.total / grand).toFixed(1)}% of all)`);
  svg.append("g").selectAll("text")
    .data(nodes.filter(d => d.kind === "person" && d.total / grand > 0.005))
    .join("text")
    .attr("x", d => d.x).attr("y", d => d.y - rPerson(d) - 4)
    .attr("text-anchor", "middle").attr("font-size", 11).attr("fill", "currentColor")
    .text(d => d.label);
  display(svg.node());
}
```

<div style="display:flex; gap:1.5rem; flex-wrap:wrap; font-size:0.85em;">
  <span><span style="display:inline-block;width:10px;height:10px;background:#cf222e;"></span> bus factor 1</span>
  <span><span style="display:inline-block;width:10px;height:10px;background:#bf8700;"></span> bus factor 2</span>
  <span><span style="display:inline-block;width:10px;height:10px;background:#1a7f37;"></span> bus factor ≥ 3</span>
  <span><span style="display:inline-block;width:10px;height:10px;border-radius:50%;background:#57606a;"></span> person (size = org share)</span>
</div>

> **Conclusion:** The picture is a hub-and-spoke system, not a mesh: three large circles hold nearly every repository, 65 of 76 squares are red (single-majority ownership), the remaining 11 amber, and **not one repository reaches bus factor 3**. There is no path between most repositories except through funderburkjim, drdhaval2785, or gasyoun; recruiting even one contributor into the rim would visibly re-wire this graph — precisely the bus-factor mitigation the [Community page](community) quantifies.

## Adjacency matrix (accessible view)

> **How to read:** The same data as the force map, as a matrix: one row per contributor (top 10 by volume), one column per repository, a cell where that person has commits, darker for more. This view is exact where the force layout is impressionistic — use it to look up *who* has touched *what*. **Example 1:** A row that spans most columns is a generalist maintainer; a row with one dark cell is a specialist. **Example 2:** Columns with exactly one filled cell are the single-point-of-failure repositories from the map, now individually identifiable.

```js
const top10 = [...totals].sort((a, b) => b[1] - a[1]).slice(0, 10).map(([l]) => l);
const matrix = shown.filter(d => top10.includes(d.login));
const repoOrder = [...repoTotals].sort((a, b) => b[1] - a[1]).map(([r]) => r);
```

```js
Plot.plot({
  width,
  height: 320,
  marginLeft: 110,
  marginBottom: 70,
  x: {label: null, domain: repoOrder, tickRotate: -60, tickFontSize: 8},
  y: {label: null, domain: top10},
  color: {type: "log", scheme: "blues", label: "contributions", legend: true},
  marks: [
    Plot.cell(matrix, {x: "repo", y: "login", fill: "contributions", inset: 0.5, tip: true,
      title: d => `${d.login} → ${d.repo}: ${d.contributions.toLocaleString("en-US")} contributions`})
  ]
})
```

> **Conclusion:** Only the top three rows have meaningful width; rows four to ten are narrow specialists. Reading down almost any column lands on the same one or two names — the matrix confirms that the network's apparent breadth is three people's reach, not a distributed community.

The cross-repo *issue-reference* graph (which issues cite which across repositories) needs issue bodies the committed snapshot does not carry; it is tracked as an API-gated extension under Workstream G4 in the [roadmap](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/docs/OBSERVATORY_ROADMAP.md).
