// Observable Framework config
// https://observablehq.com/framework/config

export default {
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
    <span style="opacity: 0.6;">12 years of Cologne Digital Sanskrit Lexicon</span>
  </a>`,
  footer: `Generated from <a href="https://github.com/sanskrit-lexicon">sanskrit-lexicon</a> data.
    Source: <a href="https://github.com/sanskrit-lexicon/csl-observatory">csl-observatory</a>.
    See <a href="/data">data downloads</a> · DOI: pending Zenodo mint`,
  root: "src",
  output: "dist"
};
