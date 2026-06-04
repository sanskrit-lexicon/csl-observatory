# csl-observatory Roadmap

Date: 2026-06-04

Status: active roadmap after boundary cleanup. The older broad roadmap is
preserved as `OBSERVATORY_ROADMAP_LEGACY_BROAD_METRICS.md`.

## Rule

Every active roadmap item must start from a repository, issue, pull request,
commit, contributor, workflow, project board, repository metadata file, or
organization-level maintenance process.

## Phase 0: Boundary Stabilization

- Keep `docs/BOUNDARY_RULES.md` current.
- Preserve legacy broad plans under explicit legacy filenames.
- Keep dictionary-structure, standards/export, corpus, and broad publication
  planning out of active observatory docs.
- Add relocation pointers instead of duplicating work from sibling repos.

## Phase 1: Reliable GitHub Snapshot

- Refresh the repository list and document which repos are dictionary, tooling,
  infrastructure, archive, or external comparator repos.
- Fetch issues, PRs, commits, releases, labels, milestones, workflow metadata,
  and repository metadata through a reproducible script.
- Store dated snapshots and generated CSV/JSON outputs with schema notes.
- Make missing permissions and rate-limit caveats visible.

## Phase 2: Repository Health Dashboard

- Report README, license, `CITATION.cff`, issue-template, PR-template, and
  workflow presence.
- Surface stale repos, archived repos, inactive default branches, and repos
  missing basic metadata.
- Keep recommendations at the repository/process level.

## Phase 3: Issue And PR Taxonomy

- Track taxonomy coverage across dictionary and tooling repos.
- Measure time-to-triage, time-to-close, open backlog, and label completeness.
- Keep examples as issue/PR evidence, not as dictionary-content analysis.

## Phase 4: Contributor And Maintainer Metrics

- Consolidate contributor identities with maintainer-reviewed metadata.
- Show contributor activity by repo, year, and type of GitHub event.
- Report maintainer concentration and review bottlenecks with consent-aware
  naming rules.

## Phase 5: Workflow And Refresh Reliability

- Track CI, cron, release, and artifact-refresh workflows.
- Document blocked refresh paths and repository dependencies.
- File or link issues in the owning repositories instead of implementing
  dictionary or standards pipelines here.

## Phase 6: Public Observatory Release

- Build the Observable dashboard from generated observatory data.
- Expose chart data as downloadable CSV/JSON with snapshot dates.
- Add a release checklist for reproducibility, caveats, and GitHub Pages
  readiness.

## Optional Comparator Slice

External projects may be compared only through public project/repository
metadata: openness, license, repository activity, contributor count, release
cadence, and documentation signals. Do not ingest DCS corpus data, dictionary
entries, TEI/OntoLex exports, or lookup logs.

## Explicitly Out Of Scope

- Source mining of dictionary XML: `csl-atlas` or dictionary repos.
- Dictionary structure, genealogy, citations, senses, or headword conventions:
  `csl-atlas`.
- TEI/OntoLex/FrAC/SHACL/RDF export work: `csl-standards`.
- DCS/corpus and grammar: `VisualDCS` or a future grammar repo.
- Matomo/top-entry lookup analytics, Wikipedia/Wiktionary backlink studies,
  and broad publication planning: no active observatory home until a new human
  decision assigns one.
