# Contributor Entry Path

Date: 2026-06-12
Status: contributor-facing entry page for roadmap SC5.

This page helps new contributors find useful, low-risk work in
`csl-observatory`. It is scoped to GitHub/org observatory work: repositories,
issues, pull requests, commits, contributors, workflows, metadata, reports,
runbooks, and dashboard surfaces.

## Start Here

1. Read [`BOUNDARY_RULES.md`](BOUNDARY_RULES.md) so observatory work stays out
   of dictionary-content research and standards/export work.
2. Read [`AI_CONTRIBUTION_POLICY.md`](AI_CONTRIBUTION_POLICY.md) if you use AI
   assistance or automation.
3. Check [`DECISIONS_NEEDED.md`](DECISIONS_NEEDED.md) before touching anything
   related to licenses, archives, credentials, or external services.
4. Use [`MAINTAINER_CONTINUITY_PACKET.md`](MAINTAINER_CONTINUITY_PACKET.md) for
   local setup, report regeneration, and dashboard build commands.

## Local Setup

Minimal docs/report setup:

```powershell
git clone https://github.com/sanskrit-lexicon/csl-observatory.git
cd csl-observatory
python --version
```

Dashboard setup:

```powershell
cd observatory\site
npm ci
npm run build
```

Report reproduction smoke check:

```powershell
python scripts/check_workspace.py
python scripts/bus_factor.py
python scripts/repo_health.py
python scripts/taxonomy_adoption.py
python scripts/velocity_timeline.py
python scripts/contributor_identity.py
```

OBS-T and OBS-Q work additionally need sibling `../csl-orig` and
`../CORRECTIONS`. Use the continuity packet before attempting those pipelines.

## Good First Work

| Work type | Examples | Labels to use | Review expectation |
|---|---|---|---|
| Documentation cleanup | Broken internal links, unclear reproduction commands, stale roadmap references. | `documentation`, `trivial` or `minor` | Small PR with before/after note. |
| Report reproduction check | Rerun one offline report script and compare headline counts. | `documentation` or `data-pipeline`, `minor` | Include command output summary and changed files. |
| Dashboard smoke check | Build the site, check chart pages against `reports/README.md`, flag missing data. | `bug` or `documentation`, `minor` | Link the page and source CSV involved. |
| Repository metadata audit | Verify README/license/citation/template status from generated reports. | `documentation`, `minor` | Do not apply licenses; report evidence only. |
| Contributor identity support | Help identify public names/ORCID gaps with consent-aware evidence. | `enhancement`, `minor` | Do not add private contact details. |
| Issue taxonomy review | Check whether open issues have one type, one severity, and an appropriate milestone. | `tech-debt`, `minor` | Use the runbook vocabulary and cite ambiguous cases. |

## Taxonomy Cheat Sheet

For tooling and observatory issues, use exactly one type label and one severity
label unless the issue is explicitly exempted by the runbook.

Common type labels:

- `bug`
- `regression`
- `tech-debt`
- `dependency`
- `security`
- `feature`
- `enhancement`
- `performance`
- `documentation`
- `docs-api`
- `infrastructure`
- `data-pipeline`
- `cross-repo`
- `build-tooling`
- `question`
- `proposal`
- `discussion`

Severity labels:

- `trivial`: cosmetic or single small docs fix.
- `minor`: well-scoped single component or report.
- `major`: multiple modules, visible behavior, or design decision.
- `critical`: data loss, security, blocked users, or production outage.

Use [`runbook/cologne-tooling-runbook.md`](../runbook/cologne-tooling-runbook.md)
for full tooling taxonomy rules and
[`runbook/cologne-issue-runbook.md`](../runbook/cologne-issue-runbook.md) for
dictionary-repo issue taxonomy rules.

## Where Not To Start

These need maintainer or organization approval first:

- Applying licenses to other repositories.
- Archiving or unarchiving repositories.
- Renaming default branches.
- Pushing to `csl-orig`, `CORRECTIONS`, or other sibling repos.
- Changing GitHub org project fields or credentials.
- Running Cologne server refresh/deploy steps.
- Publishing DOI, Zenodo, or paper-reviewer artifacts.
- Running `obs_t_gold.py --make/--score` or
  `obs_t_errorsample.py --make/--score` without an explicit annotation plan.

These belong outside `csl-observatory` unless the maintainer creates a new
observatory-scoped decision:

- Dictionary microstructure, genealogy, and source-content research:
  `csl-atlas`.
- TEI/OntoLex/RDF/export standards work: `csl-standards`.
- DCS/corpus/grammar work: `VisualDCS` or a future corpus repository.

## Pull Request Checklist

- The change starts from repository, issue, pull request, commit, contributor,
  workflow, metadata, report, runbook, or dashboard evidence.
- Generated files are included only when they are expected outputs of the
  command you ran.
- The PR says which command was run and what headline count changed, if any.
- AI-assisted work follows `AI_CONTRIBUTION_POLICY.md`.
- The change does not decide a blocked maintainer item silently.

## Useful Pointers

- Active maintainer roadmap: [`ROADMAP.md`](ROADMAP.md)
- Implementation roadmap: [`OBSERVATORY_ROADMAP.md`](OBSERVATORY_ROADMAP.md)
- Monthly review checklist: [`MAINTAINER_REVIEW_CHECKLIST.md`](MAINTAINER_REVIEW_CHECKLIST.md)
- Repository health decisions: [`REPOSITORY_HEALTH_DECISION_PACKET.md`](REPOSITORY_HEALTH_DECISION_PACKET.md)
- Bus-factor action plan: [`BUS_FACTOR_ACTION_PLAN.md`](BUS_FACTOR_ACTION_PLAN.md)
