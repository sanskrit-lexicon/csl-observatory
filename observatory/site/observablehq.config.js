// Observable Framework config
// https://observablehq.com/framework/config

// Production origin for canonical / Open Graph URLs (GitHub Pages).
const ORIGIN = "https://sanskrit-lexicon.github.io/csl-observatory";

// One-line default used for <meta name="description"> and og:description on any
// page without a PAGE_DESCRIPTIONS entry below.
const DEFAULT_DESCRIPTION =
  "A living, fully-open measurement of the Cologne Digital Sanskrit Lexicon (CDSL): " +
  "13 years of volunteer dictionary digitisation turned into citable, reproducible data — " +
  "repository health, contributor sustainability, issue taxonomy, and correction metrics.";

// Per-page meta descriptions, keyed by route. Observable Framework drops any
// non-whitelisted front-matter key (no `description:`), so the description lives
// here in the config rather than in each page's front matter. Key "/" is the
// home page; keys for sub-pages match their `path` in the `pages` array below.
const PAGE_DESCRIPTIONS = {
  "/": "A living, fully-open measurement of the Cologne Digital Sanskrit Lexicon: 13 years of volunteer dictionary digitisation turned into citable, reproducible data.",
  "/ops-command": "Maintainer-first operating view across repository health, metadata blockers, issue pressure, and bus-factor risk for sanskrit-lexicon.",
  "/activity": "Issue, pull request, and commit throughput across all 76 sanskrit-lexicon repositories over 13 years of the Cologne Digital Sanskrit Lexicon.",
  "/error-typology": "What kinds of errors are corrected in the Cologne Digital Sanskrit Lexicon, where in the entry they occur, and how the profile shifts over time.",
  "/obs-t-maintenance": "Operational views for keeping the OBS-T correction-typology dataset healthy after infrastructure changes.",
  "/coverage": "How Sanskrit dictionary digitisation work is represented in GitHub issue and pull-request labels across the sanskrit-lexicon org.",
  "/citation-coverage": "How much of the Böhtlingk-Roth (PWG) dictionary's literary-source citations link out to a Cologne source — page scans vs digital text — over the translated article subset.",
  "/taxonomy-triage": "Issue-label quality and triage gaps across the sanskrit-lexicon organization, for maintainer review.",
  "/community": "Contributors over 13 years: bus-factor risk, retention, and concentration across the Cologne Digital Sanskrit Lexicon repositories.",
  "/community-continuity": "Maintainer continuity and contributor-concentration views for monthly review of the sanskrit-lexicon organization.",
  "/tech-stack": "The technologies, languages, and tooling ecosystem behind the Cologne Digital Sanskrit Lexicon repositories.",
  "/benchmarks": "How the Cologne Digital Sanskrit Lexicon compares to peer open-source projects at the repository and project-governance level.",
  "/repo-health": "Repository hygiene across the sanskrit-lexicon org: licensing, default-branch naming, descriptions, and staleness.",
  "/repository-risk": "Deeper repository-hygiene views for license, branch, size, stale-cleanup, and flag interactions across the org.",
  "/repo-metadata": "Completeness dashboard for repository metadata: descriptions, licenses, branches, README and citation coverage, workflows, and releases.",
  "/metadata-readiness": "Operational view of repository metadata coverage: documentation, automation, releases, and unresolved live-fetch blockers.",
  "/workflow-health": "A read-only baseline for CI, scheduled jobs, artifact refresh, Dependabot, CodeQL, and release signals across the organization.",
  "/reproducibility": "The command path for reviewers to reproduce the CSL Observatory snapshot, with live-data dependencies and human-gated steps documented.",
  "/data": "Download every public CSV and JSON dataset behind the CSL Observatory, each with its source script, generation date, and caveats.",
  "/conclusions": "Plain-language summaries of what every chart in the CSL Observatory shows, grouped by page with links to the underlying data."
};

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
  const description = PAGE_DESCRIPTIONS[canonicalPath] || DEFAULT_DESCRIPTION;
  const image = ORIGIN + "/observatory-card.png"; // 1200×630, scripts/make_social_card.py
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
<meta property="og:image" content="${attr(image)}">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:image:alt" content="CSL Observatory — 13 years of the Cologne Digital Sanskrit Lexicon, measured">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="${attr(pageTitle)}">
<meta name="twitter:description" content="${attr(description)}">
<meta name="twitter:image" content="${attr(image)}">`;
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
    {name: "Citation Coverage", path: "/citation-coverage"},
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
