---
title: Data Downloads
toc: true
---

# Data Downloads

Every public CSV/JSON artifact on this site is listed here with its source
script, generated date, and caveat. Use the release-facing files for citation
and the intermediate files for audit or dashboard reproduction.

```js
const files = await FileAttachment("data/data_index.csv").csv();
```

```js
const categories = ["all", ...Array.from(new Set(files.map((d) => d.category))).sort()];
const formats = ["all", ...Array.from(new Set(files.map((d) => d.format))).sort()];
const category = view(Inputs.select(categories, {label: "Category"}));
const format = view(Inputs.select(formats, {label: "Format"}));
const query = view(Inputs.search(files, {placeholder: "Search files, scripts, caveats"}));
```

```js
const filtered = query.filter((d) =>
  (category === "all" || d.category === category) &&
  (format === "all" || d.format === format)
);
const rawBase = "https://raw.githubusercontent.com/sanskrit-lexicon/csl-observatory/main/observatory/site/src/data/";
```

```js
const totalBytes = files.reduce((sum, d) => sum + Number(d.bytes || 0), 0);
const csvCount = files.filter((d) => d.format === "csv").length;
const jsonCount = files.filter((d) => d.format === "json").length;
```

<div class="metric-grid">
  <div class="metric">
    <div class="label">Files</div>
    <div class="value">${files.length.toLocaleString()}</div>
  </div>
  <div class="metric">
    <div class="label">CSV</div>
    <div class="value">${csvCount.toLocaleString()}</div>
  </div>
  <div class="metric">
    <div class="label">JSON</div>
    <div class="value">${jsonCount.toLocaleString()}</div>
  </div>
  <div class="metric">
    <div class="label">Total Size</div>
    <div class="value">${(totalBytes / 1024 / 1024).toFixed(1)} MB</div>
  </div>
</div>

## Catalog

```js
display(html`<div class="table-scroll"><table class="catalog">
  <thead>
    <tr>
      <th>File</th>
      <th>Category</th>
      <th>Rows</th>
      <th>Generated</th>
      <th>Source</th>
      <th>Description</th>
      <th>Caveat</th>
      <th>Download</th>
    </tr>
  </thead>
  <tbody>
    ${filtered.map((d) => html`<tr>
      <td><code>${d.file}</code></td>
      <td>${d.category}</td>
      <td class="num">${d.rows ? Number(d.rows).toLocaleString() : "n/a"}</td>
      <td>${d.generated_date}</td>
      <td><code>${d.source_script}</code></td>
      <td>${d.description}</td>
      <td>${d.caveat}</td>
      <td><a href=${rawBase + encodeURIComponent(d.file)}>download</a></td>
    </tr>`)}
  </tbody>
</table></div>`);
```

## Reproduce

Refresh the local reports, dashboard inputs, and catalog:

```sh
python scripts/refresh_observatory.py --dry-run
python scripts/refresh_observatory.py
```

Regenerate only the catalog:

```sh
python scripts/data_index.py
python scripts/data_index.py --check
```

## Citation

If you use these data in published work, cite the repository snapshot, the
specific downloaded file, and the generated date shown in the catalog. No
Zenodo DOI is minted yet — `10.5281/zenodo.15834721`, previously listed here,
was a false DOI resolving to an unrelated topology preprint (see the [Reach
page](/reach) and [SanskritLexicography CONTRADICTIONS §8](https://github.com/gasyoun/SanskritLexicography/blob/master/CONTRADICTIONS.md)).

<style>
.metric-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(9rem, 1fr));
  gap: 0.75rem;
  margin: 1rem 0 1.5rem;
}
.metric {
  border: 1px solid var(--theme-foreground-faint);
  border-radius: 8px;
  padding: 0.75rem;
  background: var(--theme-background-alt);
}
.label {
  color: var(--theme-foreground-muted);
  font-size: 0.82rem;
  margin-bottom: 0.2rem;
}
.value {
  font-size: 1.45rem;
  font-weight: 700;
}
.catalog {
  font-size: 0.86rem;
  min-width: 72rem;
}
.catalog th,
.catalog td {
  vertical-align: top;
}
.catalog .num {
  text-align: right;
  white-space: nowrap;
}
.table-scroll {
  max-width: 100%;
  overflow-x: auto;
}
</style>
