// Observable Framework config
// https://observablehq.com/framework/config

// Production origin for canonical / Open Graph URLs (GitHub Pages).
const ORIGIN = "https://sanskrit-lexicon.github.io/csl-observatory";

// One-line default used for <meta name="description"> and og:description on any
// page that does not set its own `description:` in front matter.
const DEFAULT_DESCRIPTION =
  "A living, fully-open measurement of the Cologne Digital Sanskrit Lexicon (CDSL): " +
  "13 years of volunteer dictionary digitisation turned into citable, reproducible data — " +
  "repository health, contributor sustainability, issue taxonomy, and correction metrics.";

// Escape a string for safe interpolation into an HTML attribute value.
const attr = (s) =>
  String(s).replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;");

// Per-page <head> injection: canonical URL, description, Open Graph, and Twitter
// card. Receives {title, data, path} from Observable Framework, where `data` is
// the page front matter and `path` is the route (e.g. "/ops-command", "/index").
const head = ({title, data, path}) => {
  const canonicalPath = path === "/index" || path === "/" ? "/" : path;
  const url = ORIGIN + canonicalPath;
  const pageTitle = (data && data.title) || title || "CSL Observatory";
  const description = (data && data.description) || DEFAULT_DESCRIPTION;
  return `<meta name="description" content="${attr(description)}">
<link rel="canonical" href="${attr(url)}">
<meta name="robots" content="index,follow">
<meta name="theme-color" content="#3a5f7d">
<meta name="author" content="Cologne Digital Sanskrit Lexicon project (sanskrit-lexicon)">
<meta property="og:type" content="website">
<meta property="og:site_name" content="CSL Observatory">
<meta property="og:locale" content="en">
<meta property="og:title" content="${attr(pageTitle)}">
<meta property="og:description" content="${attr(description)}">
<meta property="og:url" content="${attr(url)}">
<meta name="twitter:card" content="summary">
<meta name="twitter:title" content="${attr(pageTitle)}">
<meta name="twitter:description" content="${attr(description)}">`;
  // TODO(SEO): add og:image / twitter:image once a 1200×630 social card PNG exists.
};

export default {
  head,
  title: "CSL Observatory",
  pages: [
    {name: "Ops Command", path: "/ops-command"},
    {name: "Activity", path: "/activity"},
    {name: "Error Typology", path: "/error-typology"},
    {name: "OBS-T Maintenance", path: "/obs-t-maintenance"},
    {name: "Issue Taxonomy", path: "/coverage"},
    {name: "Taxonomy Triage", path: "/taxonomy-triage"},
    {name: "Community", path: "/community"},
    {name: "Community Continuity", path: "/community-continuity"},
    {name: "Tech Stack", path: "/tech-stack"},
    {name: "Repo Benchmarks", path: "/benchmarks"},
    {name: "Repo Health", path: "/repo-health"},
    {name: "Repository Risk", path: "/repository-risk"},
    {name: "Repo Metadata", path: "/repo-metadata"},
    {name: "Metadata Readiness", path: "/metadata-readiness"},
    {name: "Workflow Health", path: "/workflow-health"},
    {name: "Reproducibility", path: "/reproducibility"},
    {name: "Data", path: "/data"},
    {name: "Conclusions", path: "/conclusions"}
  ],
  theme: ["air", "alt", "wide"],
  header: `<a href="/" style="display: flex; align-items: center; gap: 0.5rem; color: inherit; text-decoration: none;">
    <strong>CSL Observatory</strong>
    <span style="opacity: 0.6;">13 years of Cologne Digital Sanskrit Lexicon</span>
  </a>`,
  footer: `Generated from <a href="https://github.com/sanskrit-lexicon">sanskrit-lexicon</a> data.
    Source: <a href="https://github.com/sanskrit-lexicon/csl-observatory">csl-observatory</a>.
    See <a href="/data">data downloads</a> · DOI: pending Zenodo mint`,
  root: "src",
  output: "dist"
};
