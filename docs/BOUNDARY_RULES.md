# Boundary Rules

Date: 2026-06-03

Status: human decision. These rules define the direction of `csl-observatory`
and supersede broader "research around dictionaries" language wherever it
conflicts.

## Mission

`csl-observatory` is the GitHub and organization observatory for the
Sanskrit-Lexicon / CDSL ecosystem.

It measures work on digitisation: repositories, issues, pull requests,
commits, contributors, project health, tooling runbooks, metadata, and
maintenance workflows.

## Admission Test

A page, script, dataset, runbook, or plan belongs in `csl-observatory` only if
its primary object is one of:

- a GitHub repository;
- an issue, pull request, commit, branch, release, workflow, or project board;
- a contributor or maintainer identity;
- a repository-level metadata file such as `README`, `CITATION.cff`,
  `LICENSE`, issue templates, or contribution policy;
- an organization-wide tooling, quality, or maintenance process;
- a measurable history of digitisation work.

If it does not start from repo/workflow evidence, it does not belong here.

## Belongs Here

- Organization-level issue, PR, commit, contributor, and repository metrics.
- Runbooks for dictionary repos and tooling repos.
- Community templates and repository health checks.
- Refresh, extraction, retry, and reporting scripts for GitHub/org data.
- Papers or reports about the work of digitising and maintaining CDSL as a
  GitHub ecosystem.
- Tooling-roadmap items that concern the organization or its repositories.

## Does Not Belong Here

- Dictionary microstructure, macrostructure, headword systems, source
  citations, article structure, sense structure, and dictionary lineage as
  primary research objects. Those belong in `csl-atlas`.
- Lexicographic genealogy, Patel headword-convention, convention cladograms,
  and dictionary-structure research. These compare dictionaries themselves and
  should move to `csl-atlas`.
- DCS/corpus data and corpus grammar. DCS data belongs at
  `https://github.com/gasyoun/VisualDCS`; grammar needs a separate future repo.
- General standards/export work such as TEI, OntoLex, FrAC, SHACL, or RDF
  pipeline maintenance, unless the work is only being measured as repository
  activity. Standards implementation belongs in `csl-standards`.
- Publication plans that are not specifically about GitHub/org observability
  and the digitisation-work ecosystem.
- Website usage analytics, dictionary lookup telemetry, Wikipedia/Wiktionary
  backlink studies, and dictionary-content mining, unless a new human decision
  assigns them a separate home.

## External Links Are Allowed

`csl-observatory` may link to dictionary-atlas, corpus, standards, and
publication repositories, but it must not absorb their scope. A link is
acceptable when it explains repository work or organization history.

## Boundary Cleanup Completed

Completed on 2026-06-03:

- Dictionary-structure research moved to `csl-atlas`: `docs/L0_*`,
  lexicography roadmaps, microstructure/macrostructure notes, R2 sense work,
  scripts and data for L0/lexico/forensic pipelines, and the observatory site's
  lexicography/conventions/R2 pages.
- Technical standards/export implementation moved to `csl-standards`.
- Pointer: `docs/DICTIONARY_STRUCTURE_MOVED.md`.
- Broad pre-boundary observatory plans archived as
  `docs/*LEGACY_BROAD_METRICS.md`; the active design, roadmap, and report
  outline now stay inside GitHub/org observability.

## Current Relocation Candidates

These are present or planned items that need review before future cleanup:

- Older session handoffs, publication notes, or research-layer plans may still
  mention dictionary work historically. Keep only as archive/pointer material;
  do not add new dictionary research here.
- Matomo/top-entry analytics, backlinks, citation-impact studies, and broad
  publication schedules are not active observatory work under the current
  boundary decision.

## Future Work Rule

Before adding a new file, page, generated dataset, or script, ask:

> Does this start from a repository, issue, PR, commit, contributor, workflow,
> or organization-level process?

If the answer is no, open or use a different repository.
