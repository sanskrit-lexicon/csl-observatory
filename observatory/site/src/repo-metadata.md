---
title: Repository metadata
toc: true
---

# Repository metadata

Completeness dashboard for repository-level metadata: descriptions, licenses,
branches, README/citation/template coverage, workflows, releases, Dependabot,
and CodeQL. Unknown live-only fields are explicit blockers when the snapshot
was generated offline or a live lookup failed. Source plan:
[`docs/METADATA_COMPLETENESS_DASHBOARD_PLAN.md`](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/docs/METADATA_COMPLETENESS_DASHBOARD_PLAN.md).

```js
const metadata = await FileAttachment("data/repo_metadata.csv").csv({typed: true});
```

```js
const repoUrl = repo => `https://github.com/sanskrit-lexicon/${repo}`;
const isArchived = d => d.archived === true || String(d.archived).toLowerCase() === "true";
const rowFlags = d => String(d.metadata_flags ?? "").split("|").filter(Boolean);
const unknownFlags = d => rowFlags(d).filter(flag => flag.endsWith("-unknown"));
const knownFlags = d => rowFlags(d).filter(flag => !flag.endsWith("-unknown"));
const active = metadata.filter(d => !isArchived(d));
const archived = metadata.filter(isArchived);
const activeWithUnknowns = active.filter(d => unknownFlags(d).length);
const activeKnownFlags = active.filter(d => knownFlags(d).length);
const fetchedAt = metadata[0]?.fetched_at ?? "unknown";
const warningRows = metadata.filter(d => String(d.fetch_warning ?? "").trim());
```

<div class="grid grid-cols-4">
  <div class="card"><h2>Active repos</h2><span class="big">${active.length}</span></div>
  <div class="card"><h2>Archived repos</h2><span class="big">${archived.length}</span></div>
  <div class="card"><h2>Known active flags</h2><span class="big">${d3.sum(active, d => knownFlags(d).length)}</span></div>
  <div class="card"><h2>Unknown blockers</h2><span class="big">${activeWithUnknowns.length}</span></div>
</div>

Generated snapshot: `${fetchedAt}`.

```js
display(html`Download: <a href=${await FileAttachment("data/repo_metadata.csv").url()}>repo_metadata.csv</a>.`);
```

```js
display(activeWithUnknowns.length
  ? html`<p><strong>Live metadata blocker:</strong> ${activeWithUnknowns.length} active rows still have <code>unknown</code> live fields; ${warningRows.length} total rows include fetch warnings.</p>`
  : html`<p><strong>Live metadata:</strong> no unknown live-field blockers are present in this snapshot.</p>`);
```

## Coverage Summary

Known yes/no/unknown coverage across active repositories. Unknown means the
field requires a live metadata fetch or an explicit inherited-template decision.

```js
const coverageFields = [
  ["Description", "has_description"],
  ["README", "has_readme"],
  ["Citation", "has_citation"],
  ["Issue template", "has_issue_template"],
  ["PR template", "has_pr_template"],
  ["Workflows", "has_workflows"],
  ["Dependabot", "has_dependabot"],
  ["CodeQL", "has_codeql"]
];

const coverageRows = coverageFields.map(([label, field]) => ({
  label,
  yes: active.filter(d => d[field] === "yes").length,
  no: active.filter(d => d[field] === "no").length,
  unknown: active.filter(d => d[field] === "unknown").length
}));

display(html`<table>
  <thead><tr><th>Field</th><th>Yes</th><th>No</th><th>Unknown</th></tr></thead>
  <tbody>
    ${coverageRows.map(row => html`<tr>
      <td>${row.label}</td>
      <td>${row.yes}</td>
      <td>${row.no}</td>
      <td>${row.unknown}</td>
    </tr>`)}
  </tbody>
</table>`);
```

```js
const coverageLong = coverageRows.flatMap(row => [
  {label: row.label, status: "yes", count: row.yes},
  {label: row.label, status: "no", count: row.no},
  {label: row.label, status: "unknown", count: row.unknown}
]);

Plot.plot({
  width,
  height: 300,
  marginLeft: 120,
  x: {label: "Active repositories", grid: true},
  y: {label: null, domain: coverageRows.map(d => d.label)},
  color: {legend: true, domain: ["yes", "no", "unknown"], range: ["#1a7f37", "#cf222e", "#bf8700"]},
  marks: [
    Plot.barX(coverageLong, Plot.stackX({x: "count", y: "label", fill: "status", tip: true})),
    Plot.ruleX([0])
  ]
})
```

## Active Repository Queue

Known repository-health flags are strict for active repositories. Unknown live
metadata fields are shown separately as blockers.

```js
const activeQueue = active
  .map(d => ({
    ...d,
    known_flag_count: knownFlags(d).length,
    unknown_flag_count: unknownFlags(d).length,
    known_flag_text: knownFlags(d).join("|"),
    unknown_flag_text: unknownFlags(d).join("|")
  }))
  .sort((a, b) =>
    b.known_flag_count - a.known_flag_count ||
    b.unknown_flag_count - a.unknown_flag_count ||
    d3.ascending(a.repo, b.repo)
  );

display(html`<table>
  <thead>
    <tr><th>Repository</th><th>Score</th><th>Known flags</th><th>Unknown blockers</th><th>Warning</th></tr>
  </thead>
  <tbody>
    ${activeQueue.map(d => html`<tr>
      <td><a href=${repoUrl(d.repo)}>${d.repo}</a></td>
      <td>${d.metadata_score}</td>
      <td>${d.known_flag_text || "none"}</td>
      <td>${d.unknown_flag_text || "none"}</td>
      <td>${d.fetch_warning || ""}</td>
    </tr>`)}
  </tbody>
</table>`);
```

## Unknown Live Metadata Blockers

These rows are not failed metadata checks. They identify where the placeholder
snapshot needs a live GitHub fetch or an explicit inherited-template policy.

```js
display(html`<table>
  <thead><tr><th>Repository</th><th>Unknown fields</th><th>Fetch warning</th></tr></thead>
  <tbody>
    ${activeWithUnknowns
      .slice()
      .sort((a, b) => d3.descending(unknownFlags(a).length, unknownFlags(b).length) || d3.ascending(a.repo, b.repo))
      .map(d => html`<tr>
        <td><a href=${repoUrl(d.repo)}>${d.repo}</a></td>
        <td>${unknownFlags(d).join("|")}</td>
        <td>${d.fetch_warning}</td>
      </tr>`)}
  </tbody>
</table>`);
```

## Archived Repositories

Archived repositories are displayed but excluded from strict active scoring.

```js
display(html`<table>
  <thead><tr><th>Repository</th><th>License</th><th>Branch</th><th>Known flags</th><th>Unknown blockers</th></tr></thead>
  <tbody>
    ${archived
      .slice()
      .sort((a, b) => d3.ascending(a.repo, b.repo))
      .map(d => html`<tr>
        <td><a href=${repoUrl(d.repo)}>${d.repo}</a></td>
        <td>${d.license || "none"}</td>
        <td><code>${d.default_branch}</code></td>
        <td>${knownFlags(d).join("|") || "none"}</td>
        <td>${unknownFlags(d).join("|") || "none"}</td>
      </tr>`)}
  </tbody>
</table>`);
```

[Back to overview](/)
