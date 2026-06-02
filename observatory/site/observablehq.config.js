// Observable Framework config
// https://observablehq.com/framework/config

export default {
  title: "CSL Observatory",
  pages: [
    {name: "Activity", path: "/activity"},
    {name: "Coverage", path: "/coverage"},
    {name: "Community", path: "/community"},
    {name: "Tech Stack", path: "/tech-stack"},
    {name: "Lexicography", path: "/lexicography"},
    {name: "Benchmarks", path: "/benchmarks"},
    {name: "Data", path: "/data"}
  ],
  theme: ["air", "alt", "wide"],
  header: `<a href="/" style="display: flex; align-items: center; gap: 0.5rem; color: inherit; text-decoration: none;">
    <strong>CSL Observatory</strong>
    <span style="opacity: 0.6;">12 years of Cologne Digital Sanskrit Lexicon</span>
  </a>`,
  footer: `Generated from <a href="https://github.com/sanskrit-lexicon">sanskrit-lexicon</a> data.
    Source: <a href="https://github.com/sanskrit-lexicon/csl-observatory">csl-observatory</a>.
    See <a href="/data">data downloads</a> · DOI: pending Zenodo mint`,
  head: `<meta name="description" content="CSL Observatory: 12 years of Cologne Digital Sanskrit Lexicon (CDSL). Live metrics, charts, and data downloads tracking 77 repos, 5,280+ issues, and commits.">
  <meta name="keywords" content="Sanskrit, Lexicon, CDSL, GitHub metrics, data dashboard, open source">
  <meta name="author" content="Cologne Digital Sanskrit Lexicon project contributors">
  <meta property="og:title" content="CSL Observatory">
  <meta property="og:description" content="12 years of Cologne Digital Sanskrit Lexicon in numbers and pictures.">
  <meta property="og:type" content="website">`,
  root: "src",
  output: "dist"
};
