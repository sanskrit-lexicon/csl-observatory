---
title: Community continuity
toc: true
---

# Community Continuity

Maintainer continuity and contributor concentration views for monthly review.

```js
const commits = await FileAttachment("data/commits.csv").csv({typed: true});
const contributors = await FileAttachment("data/contributors.csv").csv({typed: true});
const busFactor = await FileAttachment("data/bus_factor.csv").csv({typed: true});
const peopleSummary = await FileAttachment("data/people_summary.csv").csv({typed: true});
const repos = await FileAttachment("data/repos.csv").csv({typed: true});
```

```js
const GREEN = "#1a7f37";
const AMBER = "#bf8700";
const RED = "#cf222e";
const BLUE = "#0969da";
const repoInfo = new Map(repos.map(d => [d.repo, d]));
const humanContribs = contributors.filter(d => d.type !== "Bot");
```

## Contributor Retention: First X Last Commit Year

Positions each contributor at their first and last commit year to distinguish long-term participants from one-time visitors. Contributors on the diagonal (first ≈ last year) contributed briefly and left; contributors with a large vertical span between first and last year are the project's long-term backbone. Green dots are people still active in 2026; amber dots are contributors who last committed before 2026.

> **How to read:** Each dot is one contributor; x = year of first commit, y = year of most recent commit, dot size = total commits. **Example 1:** A large green dot at (first=2014, last=2026) is a founding contributor still active 12 years later — the project's highest-value continuity asset. **Example 2:** A small amber dot where first and last year are the same is a one-time contributor who made a single-session contribution and never returned — common in open-source digital humanities projects where scholars contribute one correction batch.

```js
const byPerson = d3.rollup(commits.filter(d => d.author_login), v => {
  const years = v.map(d => new Date(d.date).getFullYear()).filter(Boolean);
  return {first: d3.min(years), last: d3.max(years), commits: v.length};
}, d => d.author_login);
const retention = Array.from(byPerson, ([login, stats]) => ({login, ...stats}))
  .filter(d => d.first && d.last);
```

```js
const contributorScope = view(Inputs.select(["all contributors", "active in 2026", "inactive before 2026"], {value: "all contributors", label: "Contributor scope"}));
const scopedRetention = retention.filter(d => {
  if (contributorScope === "active in 2026") return d.last >= 2026;
  if (contributorScope === "inactive before 2026") return d.last < 2026;
  return true;
});
```

```js
display(Plot.plot({
  width,
  height: 430,
  x: {label: "First commit year", tickFormat: "d", grid: true},
  y: {label: "Last commit year", tickFormat: "d", grid: true},
  color: {legend: true, domain: ["active in 2026", "inactive"], range: [GREEN, AMBER]},
  marks: [
    Plot.dot(scopedRetention, {x: "first", y: "last", r: d => Math.max(3, Math.sqrt(d.commits)), fill: d => d.last >= 2026 ? "active in 2026" : "inactive", tip: true, channels: {Login: "login", Commits: "commits"}})
  ]
}))
```

> **Conclusion:** The retention chart shows that long-term continuity rests on a very small group of contributors with large vertical spans, while the majority of ever-contributors appeared briefly and left. The project's operational continuity depends almost entirely on the few green dots with the longest vertical spans remaining active.

## Repo Contributor-Count Distribution

The distribution of how many distinct contributors each repository has accumulated in its entire history — 1, 2, 3, and so on. This is the direct readout of the bus-factor risk landscape across the org: repos with only 1 contributor have zero redundancy, while repos with 5+ contributors can survive the departure of any single person. The shape of the distribution — whether it peaks sharply at 1 or has a meaningful tail — determines the org's collective resilience.

> **How to read:** Each bar is one contributor-count value; height = number of repos with exactly that many contributors. Red = 1–2 (high single-point-of-failure risk). **Example 1:** A very tall bar at "1" means most repos have only ever been touched by a single person — the entire commit history has no second author who could continue the work. **Example 2:** A small but non-zero bar at "5+" means a handful of repos have achieved real contributor diversity — these are the models to emulate for new repo creation.

```js
const contributorCounts = Array.from(d3.rollup(busFactor, v => v.length, d => +d.contributors || 0), ([contributors, count]) => ({contributors, count}))
  .sort((a, b) => a.contributors - b.contributors);

display(Plot.plot({
  width,
  height: 300,
  x: {label: "Contributors in repo history"},
  y: {label: "Repositories", grid: true},
  marks: [
    Plot.barY(contributorCounts, {x: "contributors", y: "count", fill: d => d.contributors <= 2 ? RED : AMBER, tip: true}),
    Plot.ruleY([0])
  ]
}))
```

> **Conclusion:** A peak at 1 with a rapidly decaying tail confirms that most repositories are single-maintainer projects. The handful of repos with broader contributor bases are the ones most likely to survive a maintainer departure intact — studying what made them attract more contributors is worth the analysis.

## Largest Contributor Share Histogram

Shows how often the single most active contributor accounts for 0–10%, 10–20%, …, 90–100% of a repository's history. This goes beyond the bus-factor-1 binary: a repo where the top contributor holds 55% is bus factor 1, but so is a repo where they hold 99% — yet those two situations are very different in terms of replacement difficulty. A distribution skewed towards the 80–100% bucket means concentration is extreme, not merely majority-level.

> **How to read:** Each bar is a 10-percentage-point bucket of the top contributor's share; height = repos in that bucket. Red = buckets above 50% (bus factor 1). **Example 1:** A tallest bar in the 90–100% bucket means most bus-factor-1 repos are effectively total single-author projects — the top contributor wrote almost everything, making knowledge transfer far harder than a 51% majority. **Example 2:** Any bars in the 0–50% range (green) show repos with genuine work distribution — where no one person dominates more than half the commits.

```js
const shareBins = d3.range(0.1, 1.1, 0.1).map(upper => {
  const lower = +(upper - 0.1).toFixed(1);
  return {
    bucket: `${Math.round(lower * 100)}-${Math.round(upper * 100)}%`,
    upper,
    count: busFactor.filter(d => (+d.top_share || 0) > lower && (+d.top_share || 0) <= upper).length
  };
});

display(Plot.plot({
  width,
  height: 320,
  marginBottom: 60,
  x: {label: "Largest contributor share", domain: shareBins.map(d => d.bucket), tickRotate: -35},
  y: {label: "Repositories", grid: true},
  marks: [
    Plot.barY(shareBins, {x: "bucket", y: "count", fill: d => d.upper > 0.5 ? RED : GREEN, tip: true}),
    Plot.ruleY([0])
  ]
}))
```

> **Conclusion:** A strong right-skew confirms that bus-factor-1 concentration is extreme, not marginal. In most affected repos, the top contributor did not just edge past 50% — they authored 80–100% of the history. This makes knowledge transfer and succession planning far harder than the headline bus-factor number suggests.

## Bus-Factor Risk By Primary Language

Bus-factor risk broken down by a repository's primary programming language. This tests whether the concentration problem is uniform across the org's tech stack or whether certain language ecosystems — and their associated repos — are more exposed. If both Python (processing scripts) and HTML (display pages) show predominantly bus-factor-1, the entire technical stack is at risk simultaneously.

> **How to read:** Each row is one language; bars stack bus-factor-1 (red) vs bus-factor-≥-2 (green) repo counts. **Example 1:** A Python row with a large red segment means the correction and pipeline scripts — the core of the project's back-end tooling — are heavily concentrated in single maintainers. **Example 2:** A language row that is entirely green means all repositories of that type have at least two contributors — an unusual positive signal worth noting and protecting.

```js
const languageRows = busFactor.map(d => ({
  repo: d.repo,
  language: repoInfo.get(d.repo)?.primary_language || "unknown",
  risk: +d.bus_factor === 1 ? "bus factor 1" : "bus factor >= 2"
}));
const topLanguages = Array.from(d3.rollup(languageRows, v => v.length, d => d.language), ([language, count]) => ({language, count}))
  .sort((a, b) => b.count - a.count)
  .slice(0, 8)
  .map(d => d.language);
const languageRisk = Array.from(d3.rollup(languageRows.filter(d => topLanguages.includes(d.language)), v => v.length, d => d.language, d => d.risk), ([language, inner]) =>
  Array.from(inner, ([risk, count]) => ({language, risk, count}))
).flat();

display(Plot.plot({
  width,
  height: 360,
  marginLeft: 100,
  x: {label: "Repositories", grid: true},
  y: {label: null, domain: topLanguages},
  color: {legend: true, domain: ["bus factor 1", "bus factor >= 2"], range: [RED, GREEN]},
  marks: [
    Plot.barX(languageRisk, Plot.stackX({x: "count", y: "language", fill: "risk", tip: true})),
    Plot.ruleX([0])
  ]
}))
```

> **Conclusion:** If both Python and HTML show predominantly red bars, the entire technical stack — back-end scripts and front-end display pages — is single-maintainer territory simultaneously. That means any maintainer departure would affect both the correction pipeline and the live dictionary website, not just one layer.

## Identity And ORCID Status

The identity and ORCID audit tracks two independent attributes for every contributor: whether they have been identified by their real name (vs remaining as a pseudonymous GitHub login), and whether they have an ORCID persistent researcher identifier. ORCID is required for scholarly citation chains — any paper or dataset release that credits contributors by login rather than ORCID cannot be properly attributed in academic databases. The current state of both fields determines the project's readiness to publish its outputs as citable scholarly resources.

> **How to read:** Two stacked rows — identity status (named / pseudonymous / unknown) and ORCID coverage (has ORCID / missing ORCID). **Example 1:** A "missing ORCID" segment that fills most of the ORCID row means no contributor is currently citable via a persistent identifier — a concrete blocker for any paper submission that requires contributor ORCID fields. **Example 2:** A large "named" segment in the identity row that does not translate to a matching "has ORCID" segment shows contributors who are known by name but still lack the persistent identifier — identity and ORCID are separate attributes that both need to be resolved.

```js
const identityRows = peopleSummary.flatMap(d => [
  {kind: "identity status", status: String(d.status || "unknown"), n: 1},
  {kind: "ORCID", status: String(d.orcid || "").trim() ? "has ORCID" : "missing ORCID", n: 1}
]);
const identityCounts = Array.from(d3.rollup(identityRows, v => v.length, d => d.kind, d => d.status), ([kind, inner]) =>
  Array.from(inner, ([status, count]) => ({kind, status, count}))
).flat();

display(Plot.plot({
  width,
  height: 340,
  marginLeft: 120,
  x: {label: "People", grid: true},
  y: {label: null},
  color: {legend: true, range: [GREEN, AMBER, RED, BLUE, "#8250df"]},
  marks: [
    Plot.barX(identityCounts, Plot.stackX({x: "count", y: "kind", fill: "status", tip: true})),
    Plot.ruleX([0])
  ]
}))
```

> **Conclusion:** Zero or near-zero ORCID coverage is the primary attribution blocker for the OBS-T paper and any future dataset publication. The fix is registration — each named contributor needs to create or link an ORCID account — which requires direct contact and cannot be automated. This is tracked in hygiene issue #20.

[Back to overview](/)
