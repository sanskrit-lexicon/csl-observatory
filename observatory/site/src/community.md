---
title: Community growth
toc: true
---

# Community growth

Contributors over 13 years. Bus-factor, retention, geographic distribution.

```js
const contributors = await FileAttachment("data/contributors.csv").csv({typed: true});
const peopleSummary = await FileAttachment("data/people_summary.csv").csv({typed: true});
const annual = await FileAttachment("data/timeseries_annual.csv").csv({typed: true});
const commits = await FileAttachment("data/commits.csv").csv({typed: true});
const busFactor = await FileAttachment("data/bus_factor.csv").csv({typed: true});
const contributorIdentity = await FileAttachment("data/contributor_identity.csv").csv({typed: true});
const botLogins = new Set(contributorIdentity.filter(d => d.status === "bot").map(d => d.login));
const humanContributors = contributors.filter(d => d.type !== "Bot" && !botLogins.has(d.login));
```

## Top contributors by total commits (lifetime)

The lifetime contribution leaderboard reveals the extreme inequality in this project's contributor base. One person — funderburkjim — alone accounts for well over half of all recorded commits across the entire org; the next two contributors form a compact core trio that together cover roughly 98% of the work. Everyone else trails far behind. This is not unusual for volunteer open-source lexicography, but it means the health of the entire project is tightly coupled to the continued availability of a single individual.

> **How to read:** Each horizontal bar is one person; its length equals their total number of contributions across all repositories they have ever touched. The chart shows the top 20 contributors only. **Example 1:** If funderburkjim's bar is roughly twice as long as the second-place contributor, it means one person has done twice as much recorded work as the runner-up. **Example 2:** A contributor near the bottom of the top-20 with a bar barely visible compared to the top suggests they rank in the leaderboard only because the long tail beyond position 20 is thinner still — most people have contributed very few commits.

```js
const contribTotals = d3.flatRollup(humanContributors, v => d3.sum(v, x => x.contributions), d => d.login)
  .map(([login, total]) => ({login, total}))
  .sort((a, b) => b.total - a.total)
  .slice(0, 20);
```

```js
Plot.plot({
  width,
  height: 500,
  marginLeft: 140,
  x: {label: "Total commits (lifetime)"},
  y: {label: null, domain: contribTotals.map(d => d.login)},
  marks: [
    Plot.barX(contribTotals, {x: "total", y: "login", fill: "#5319e7", tip: true}),
    Plot.ruleX([0])
  ]
})
```

> **Conclusion:** The contribution distribution is sharply unequal: a single contributor accounts for more than half of all recorded commits, with the next two forming a tight core trio — everyone else trails far behind. This is the primary sustainability risk for the org: not low activity, but extreme concentration in individuals who cannot easily be replaced.

## Repo coverage per contributor

Commit count measures depth; repo coverage measures breadth — how many different parts of the org each person has worked in. The core contributors are broad as well as deep: they touch not just their primary repos but the full stack from dictionary source files through correction pipelines to web infrastructure. Specialists who appear only in one or two repos typically worked on a single dictionary correction campaign.

> **How to read:** Each bar shows the number of distinct repositories a person has committed to at least once. **Example 1:** A contributor with 30+ repos touched is a project-wide generalist who has worked across dictionaries, tooling, and infrastructure. **Example 2:** A contributor with 2–3 repos touched is a specialist — likely someone who contributed corrections to one specific dictionary before moving on.

```js
const repoCoverage = d3.flatRollup(humanContributors, v => v.length, d => d.login)
  .map(([login, n_repos]) => ({login, n_repos}))
  .sort((a, b) => b.n_repos - a.n_repos)
  .slice(0, 20);
```

```js
Plot.plot({
  width,
  height: 500,
  marginLeft: 140,
  x: {label: "Distinct repos contributed to"},
  y: {label: null, domain: repoCoverage.map(d => d.login)},
  marks: [
    Plot.barX(repoCoverage, {x: "n_repos", y: "login", fill: "#0075ca", tip: true}),
    Plot.ruleX([0])
  ]
})
```

> **Conclusion:** The same core trio that dominates commit totals also has the widest repo coverage — they are not just prolific but spread across the entire org. Their absence would create gaps not in one dictionary but across every layer of the stack, from source data to web display to CI infrastructure.

## New contributors per year (first commit)

New-contributor acquisition is the forward-looking complement to the concentration metrics: even if the current core is stable, the long-term health of the project depends on whether new people join. The picture here is sparse: many years add only one or two new contributors, some add none, and there is no visible upward trend. The org has not built a reliable onboarding pipeline.

> **How to read:** Each bar is the count of contributors whose very first commit to any org repository falls in that year. **Example 1:** A bar of height 5 in a given year means five people made their first-ever commit to the org that year — some may have stayed active, others may have made only that one commit. **Example 2:** A year with a bar of height 0 means not a single new person joined the contributor base that year.

```js
const firstCommit = new Map();
for (const c of commits) {
  if (botLogins.has(c.author_login)) continue;
  if (!c.author_login || !c.date) continue;
  const date = new Date(c.date);
  const existing = firstCommit.get(c.author_login);
  if (!existing || date < existing) firstCommit.set(c.author_login, date);
}

const newPerYear = d3.flatRollup(
  Array.from(firstCommit, ([login, date]) => ({login, year: date.getFullYear()})),
  v => v.length, d => d.year
).map(([year, n]) => ({year, n})).sort((a, b) => a.year - b.year);
```

```js
Plot.plot({
  width,
  height: 350,
  x: {label: "Year"},
  y: {label: "New contributors (first commit)"},
  marks: [
    Plot.barY(newPerYear, {x: "year", y: "n", fill: "#1a7f37", tip: true}),
    Plot.ruleY([0])
  ]
})
```

> **Conclusion:** Contributor acquisition is sparse and sporadic — some years add zero new people, and the trend shows no growth in the onboarding pipeline. This amplifies the long-term sustainability risk: the project depends on its existing core indefinitely, with no observed mechanism for refreshing the contributor base as founding members age or step back.

## Bus factor & contributor concentration

A repository's **bus factor** is the smallest number of contributors whose combined work exceeds 50% of its history. A bus factor of **1** means a single person could be lost and the majority of that repo's history has no second author. Source and full per-repo table: [`reports/bus_factor.md`](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/reports/bus_factor.md) (generated by [`scripts/bus_factor.py`](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/scripts/bus_factor.py)).

```js
const humans = humanContributors;
const personTotal = d3.rollup(humans, v => d3.sum(v, x => x.contributions), d => d.login);
const totals = Array.from(personTotal.values()).sort((a, b) => b - a);
const grand = d3.sum(totals);
const bf1 = busFactor.filter(d => d.bus_factor === 1);

function gini(vals) {
  const v = vals.filter(x => x > 0).slice().sort((a, b) => a - b);
  const n = v.length;
  if (!n) return 0;
  let cum = 0;
  v.forEach((x, i) => cum += (i + 1) * x);
  return (2 * cum) / (n * d3.sum(v)) - (n + 1) / n;
}
function peopleFor(frac) {
  let c = 0;
  for (let i = 0; i < totals.length; i++) { c += totals[i]; if (c >= frac * grand) return i + 1; }
  return totals.length;
}
const coreTrio = ["funderburkjim", "drdhaval2785", "gasyoun"];
const coreShare = d3.sum(coreTrio, l => personTotal.get(l) || 0) / grand;
```

<div class="grid grid-cols-4">
  <div class="card"><h2>Repos with bus factor 1</h2><span class="big">${bf1.length} / ${busFactor.length}</span></div>
  <div class="card"><h2>People for half of all work</h2><span class="big">${peopleFor(0.5)}</span></div>
  <div class="card"><h2>Core-trio share</h2><span class="big">${(coreShare * 100).toFixed(0)}%</span></div>
  <div class="card"><h2>Gini (inequality)</h2><span class="big">${gini(totals).toFixed(2)}</span></div>
</div>

> **How to read:** Each horizontal bar is one repository; its length equals the largest single contributor's share of that repo's total commit history. Bars are coloured red for bus factor 1 (one person holds the majority) and green for bus factor ≥ 2 (the work is more distributed). The dashed line at 50% marks the majority threshold. **Example 1:** A bar reaching 100% means one person authored every commit in that repository — the entire history depends on a single individual. **Example 2:** A green bar stopping just past the 50% mark means the top contributor crossed the threshold but only barely — a second person covers the remaining ~49%, giving some resilience.

Each bar is the largest single contributor's share of that repository. Red bars are single-points-of-failure (bus factor 1); the dashed line marks the 50% majority threshold.

```js
const ranked = busFactor.slice().sort((a, b) => b.top_share - a.top_share);
```

```js
Plot.plot({
  width,
  height: 760,
  marginLeft: 150,
  x: {label: "Largest single contributor's share of the repo", domain: [0, 1], grid: true, percent: true},
  y: {label: null, domain: ranked.map(d => d.repo)},
  color: {legend: true, domain: ["bus factor 1", "bus factor ≥ 2"], range: ["#cf222e", "#1a7f37"]},
  marks: [
    Plot.barX(ranked, {
      x: "top_share",
      y: "repo",
      fill: d => d.bus_factor === 1 ? "bus factor 1" : "bus factor ≥ 2",
      tip: true,
      channels: {"Top contributor": "top_login", "Contributors": "contributors"}
    }),
    Plot.ruleX([0.5], {stroke: "currentColor", strokeDasharray: "4 4"})
  ]
})
```

Of **${busFactor.length}** repositories with human contributors, **${bf1.length}** depend on a single maintainer for the majority of their history. Just **${peopleFor(0.5)}** person accounts for half of all recorded contributions, and the core trio carries **${(coreShare * 100).toFixed(0)}%** — a Gini of **${gini(totals).toFixed(2)}** confirms a long tail of one-off contributors behind a tiny active core.

[← back to overview](/)
