---
title: Repository risk
toc: true
---

# Repository Risk

Deeper repository-hygiene views for license, branch, size, stale cleanup, and
flag interactions.

```js
const repos = await FileAttachment("data/repos.csv").csv({typed: true});
const health = await FileAttachment("data/repo_health.csv").csv({typed: true});
```

```js
const GREEN = "#1a7f37";
const AMBER = "#bf8700";
const RED = "#cf222e";
const BLUE = "#0969da";
const splitPipe = value => String(value ?? "").split("|").map(d => d.trim()).filter(Boolean);
const repoMeta = new Map(repos.map(d => [d.repo, d]));
const rows = health.map(d => ({...d, repo_info: repoMeta.get(d.repo) ?? {}}));
const repoUrl = repo => `https://github.com/sanskrit-lexicon/${repo}`;
```

```js
const repoScope = view(Inputs.select(["all repos", "flagged repos", "cleanup candidates"], {value: "all repos", label: "Repository scope"}));
```

```js
const scopedRows = rows.filter(d => {
  if (repoScope === "flagged repos") return (+d.flag_count || 0) > 0;
  if (repoScope === "cleanup candidates") return splitPipe(d.flags).includes("cleanup-candidate");
  return true;
});
```

## License X Branch Heatmap

A two-way matrix crossing license class (rows) against default branch name (columns). The question it answers: are licensing and branch hygiene problems the same repos or different repos? If the "none"/"master" cell is the darkest, repos with both problems cluster together and can be addressed in a single pass. If "recognised"/"master" is large, branch renaming is an isolated, separate-population problem.

> **How to read:** Each cell is the count of repos in that license × branch combination; darker colour = more repos. **Example 1:** A dark "none"/"master" cell means the same repos that lack a license are also on the legacy branch — the problems cluster, so a combined cleanup sweep is efficient. **Example 2:** A bright "recognised"/"main" cell shows the fully-modernised population — licensed and on the preferred branch — which is the target state for every repo.

```js
const licenseBranch = Array.from(
  d3.rollup(scopedRows, v => v.length, d => d.license_class, d => d.default_branch),
  ([license_class, inner]) => Array.from(inner, ([branch, count]) => ({license_class, branch, count}))
).flat();

display(Plot.plot({
  width,
  height: 260,
  marginLeft: 130,
  x: {label: "Default branch"},
  y: {label: null},
  color: {scheme: "YlOrRd", legend: true, label: "Repositories"},
  marks: [
    Plot.cell(licenseBranch, {x: "branch", y: "license_class", fill: "count", tip: true}),
    Plot.text(licenseBranch, {x: "branch", y: "license_class", text: "count", fill: "black"})
  ]
}))
```

> **Conclusion:** The heatmap's darkest cell identifies the dominant hygiene cluster. If "none"/"master" dominates, hygiene problems compound each other and should be fixed together. If "recognised"/"master" is also large, branch naming is a separate isolated issue that a simple default-branch rename can resolve without touching licensing.

## Flag Co-Occurrence Matrix

A symmetric matrix showing how often pairs of hygiene flags appear together on the same repository. High off-diagonal counts mean fixing one flag often implies fixing both — or that a shared root cause drives multiple symptoms simultaneously. Low off-diagonal counts mean flags are independent, requiring separate targeted actions for each repo.

> **How to read:** Row A, column B shows how many repos carry both flag A and flag B. The diagonal shows repos carrying that single flag. **Example 1:** High co-occurrence between "no-license" and "legacy-branch" means most unlicensed repos are also on "master" — a combined cleanup script can address both in one pass per repo. **Example 2:** A flag with strong off-diagonal entries across many other flags is a marker for overall neglect — those repos likely need a full hygiene sweep rather than targeted single-fix actions.

```js
const flagNames = Array.from(new Set(scopedRows.flatMap(d => splitPipe(d.flags)))).sort();
const flagPairs = [];
for (const d of scopedRows) {
  const flags = splitPipe(d.flags);
  for (const a of flags) for (const b of flags) flagPairs.push({a, b, repo: d.repo});
}
const flagMatrix = Array.from(d3.rollup(flagPairs, v => v.length, d => d.a, d => d.b), ([a, inner]) =>
  Array.from(inner, ([b, count]) => ({a, b, count}))
).flat();

display(Plot.plot({
  width,
  height: 520,
  marginLeft: 150,
  marginBottom: 120,
  x: {label: null, domain: flagNames, tickRotate: -35},
  y: {label: null, domain: flagNames},
  color: {scheme: "YlOrRd", legend: true, label: "Repos"},
  marks: [
    Plot.cell(flagMatrix, {x: "b", y: "a", fill: "count", tip: true})
  ]
}))
```

> **Conclusion:** Co-occurrence clusters guide prioritisation: pairs of flags that appear together frequently should be fixed together in a single automated pass. Isolated flags — those with sparse off-diagonal entries — can be addressed individually without needing to touch other hygiene dimensions.

## Repo Age X Size

Each repository plotted by its age in years (x-axis) against its size in kilobytes on a square-root scale (y-axis). Dot size encodes hygiene-flag count; colour shows license class. The scatter reveals whether older repos are larger (expected — they have accumulated more corrections), whether the unlicensed repos are the historic ones or recent additions, and whether hygiene problems cluster in the oldest or newest part of the collection.

> **How to read:** Each dot is one repo; x = years since creation, y = size in KB (sqrt scale to compress the large outliers), dot size = hygiene flag count, colour = license class. **Example 1:** Large red dots in the upper-right corner are old, large, and unlicensed — the highest-priority cleanup combination, since these hold the most historical content with the weakest legal frame. **Example 2:** Small green dots near the left edge are recently created repos already carrying a recognised license — evidence that newer repos are being set up with better hygiene practices from the start.

```js
const nowYear = 2026;
const ageSize = scopedRows.map(d => {
  const info = d.repo_info ?? {};
  const created = info.created_at ? new Date(info.created_at).getFullYear() : null;
  return {
    repo: d.repo,
    age: created ? nowYear - created : null,
    size_kb: +info.size_kb || 0,
    license_class: d.license_class,
    flag_count: +d.flag_count || 0,
    open_issues: +d.open_issues || 0
  };
}).filter(d => d.age !== null);

display(Plot.plot({
  width,
  height: 420,
  x: {label: "Repository age (years)", grid: true},
  y: {label: "Size (KB)", grid: true, type: "sqrt"},
  color: {legend: true, domain: ["recognised", "unrecognised", "none"], range: [GREEN, AMBER, RED]},
  marks: [
    Plot.dot(ageSize, {x: "age", y: "size_kb", r: d => Math.max(3, Math.sqrt(d.flag_count + 1) * 3), fill: "license_class", tip: true, channels: {Repository: "repo", "Open issues": "open_issues", "Flags": "flag_count"}})
  ]
}))
```

> **Conclusion:** The age-size scatter typically shows that the largest repos are the oldest (years of accumulated corrections) and that unlicensed repos span both old and new — not all unlicensed repos are legacy holdovers. Old, large, unlicensed repos are the most urgent targets; new unlicensed repos should be caught before they accumulate history.

## Cleanup Candidates: Idle Time X Open Issues

A focused view on the small number of repositories flagged as cleanup candidates — temp_*, test_*, or legacy repos that are no longer actively maintained. Each is plotted by how long it has been idle (days since last push) against how many open issues it still carries. Idle repos with open issues are the hardest archiving case: clearly not being maintained, but with unresolved threads that require a decision before the repo can be safely archived.

> **How to read:** Each dot is one cleanup-candidate repo; x = days idle, y = open issues. Labels name each repo directly. **Example 1:** A repo far right with 0 open issues is the easiest archiving case — idle for a long time with no outstanding threads, safe to archive immediately with maintainer sign-off. **Example 2:** A repo with non-zero open issues, even if very idle, is blocked until those issues are either migrated to the primary dictionary repo or explicitly closed — each is a separate decision that requires maintainer attention.

```js
const cleanup = scopedRows.filter(d => splitPipe(d.flags).includes("cleanup-candidate"))
  .sort((a, b) => d3.descending(+a.days_since_push || 0, +b.days_since_push || 0));

display(Plot.plot({
  width,
  height: 360,
  marginRight: 120,
  x: {label: "Days since last push", grid: true},
  y: {label: "Open issues", grid: true},
  marks: [
    Plot.dot(cleanup, {x: "days_since_push", y: "open_issues", r: 7, fill: RED, tip: true}),
    Plot.text(cleanup, {x: "days_since_push", y: "open_issues", text: "repo", dx: 10, fill: "currentColor"})
  ]
}))
```

> **Conclusion:** Cleanup candidates with open issues are the RH3 blockers. The specific blocker for each is typically a scholarly question thread that may need to be migrated to the primary dictionary repo before the temp repo can be safely archived. Jim Funderburk was notified in June 2026; archiving depends on his responses to those threads.

## Hygiene Flag Distribution

The frequency distribution of how many hygiene flags each repository carries — 0, 1, 2, 3, and up. This is the headline summary of the org's overall hygiene state: a tall green bar at 0 means most repos are clean; a long right tail at 3–4 means some repos have accumulated multiple overlapping problems that need a coordinated sweep. After the RH1 rollout the distribution should have shifted left, with the green zero-flag bar significantly taller than before.

> **How to read:** Each bar is one flag-count value; height = repos at that count. Green = 0 flags (clean). **Example 1:** A tall green bar means the majority of repos now pass every hygiene check — the RH1 rollout worked. **Example 2:** A persistent hump at 2–3 flags identifies repos where problems have clustered; these need multi-issue coordinated fixes rather than single targeted actions.

```js
const flagHistogram = Array.from(d3.rollup(scopedRows, v => v.length, d => +d.flag_count || 0), ([flag_count, count]) => ({flag_count, count}))
  .sort((a, b) => a.flag_count - b.flag_count);

display(Plot.plot({
  width,
  height: 300,
  x: {label: "Hygiene flag count"},
  y: {label: "Repositories", grid: true},
  marks: [
    Plot.barY(flagHistogram, {x: "flag_count", y: "count", fill: d => d.flag_count === 0 ? GREEN : AMBER, tip: true}),
    Plot.ruleY([0])
  ]
}))
```

> **Conclusion:** The flag distribution is the headline hygiene metric for the org at a snapshot in time. A shift left (more repos at 0) after a cleanup campaign confirms the campaign worked. Any tail at 3+ flags after RH1 identifies the remaining hard cases that need direct maintainer attention, not automation.

[Back to overview](/)
