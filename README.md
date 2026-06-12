# csl-observatory

> **Live observatory for 12 years of Cologne Digital Sanskrit Lexicon (CDSL).**
> Tracking 76 repos, 5,413 issues+PRs, 9,877 commits, and 16 contributors since 2014.

## What this is

A meta-repository that **measures the entire sanskrit-lexicon GitHub organisation** and turns 12 years of distributed work into measurable, citable, reproducible knowledge. It is intentionally limited to repositories, issues, pull requests, commits, contributors, workflows, and organization-level maintenance evidence. The 2026-06-04 boundary cleanup is merged: dictionary-structure research belongs in [`csl-atlas`](https://github.com/sanskrit-lexicon/csl-atlas), standards/export work belongs in [`csl-standards`](https://github.com/sanskrit-lexicon/csl-standards), and DCS/corpus work belongs in [`VisualDCS`](https://github.com/gasyoun/VisualDCS).

## Quick links

- **[Observatory dashboard](https://sanskrit-lexicon.github.io/csl-observatory/)** — live charts, deployed to GitHub Pages via `.github/workflows/deploy.yml`
- **[Findings & reports](reports/README.md)** — the five reproducible analyses + the synthesis (start here)
- **[Synthesis](reports/synthesis.md)** — *State of the observatory*, the four findings tied into one picture
- **[Tooling Roadmap (project #9)](https://github.com/orgs/sanskrit-lexicon/projects/9)** — findings (#22–25) and action issues (#15–21), grouped by `Category`
- **[Boundary rules](docs/BOUNDARY_RULES.md)** — what belongs in the GitHub/org observatory, and what must move elsewhere
- **[Design document](docs/OBSERVATORY_DESIGN.md)** — boundary-safe architecture and KPI scope
- **[Docs archive index](docs/ARCHIVE.md)** — legacy and moved-to-`csl-atlas` documents in one place
- **[Data downloads](observatory/site/src/data/)** — every chart's source as CSV
- **[Runbooks](runbook/)** — the issue-taxonomy procedures applied to all active repos
- **[Contributor & work statistics](docs/CONTRIBUTOR_STATS.md)** — per-contributor & per-repo commits, churn, tenure, and issues (2014–2026)
- **[Decisions needed](docs/DECISIONS_NEEDED.md)** — open items blocked on a maintainer (decisions, credentials, confirmations)

## Findings

Five offline, reproducible analyses of the organization (script → report →
site page). Full index and reproduction steps: **[`reports/README.md`](reports/README.md)**.
The headline picture is in **[`reports/synthesis.md`](reports/synthesis.md)**.

| Finding | Report | Headline |
|---|---|---|
| Contributor concentration | [`bus_factor.md`](reports/bus_factor.md) | Core trio = 97.6%; 65/76 repos have bus factor 1; Gini 0.86 |
| Repository health | [`repo_health.md`](reports/repo_health.md) | 41/76 repos unlicensed; 46/76 default to `master`; 5 fully clean |
| Issue-taxonomy adoption | [`taxonomy_adoption.md`](reports/taxonomy_adoption.md) | 89% typed, 63% conformant; 92% peak in 2025; 54 stray labels |
| Velocity & health timeline | [`velocity_timeline.md`](reports/velocity_timeline.md) | 9,877 commits; peak 11 authors/yr; backlog 1,742 (2025) → 913 (2026) |
| Contributor identity | [`contributor_identity.md`](reports/contributor_identity.md) | 0/16 authors have a registered ORCID |
| **Error typology (OBS-T)** | [`obs_t_typology.md`](reports/obs_t_typology.md) | 50,953 corrections, two axes — location (sense 53% · headword 22%) × edit-type (mostly micro surface edits, 66% ≤2 chars); cross-dict V=0.42 |

Actionable follow-ups are filed on the [Tooling Roadmap](https://github.com/orgs/sanskrit-lexicon/projects/9)
as issues #15–#21 (Actions), with the findings themselves as #22–#25 (Findings).

### OBS-T — error typology of digital Sanskrit dictionaries

A standalone language-resource + finding track (Phases 1–8), distinct from the
org-process findings above. It unifies 12 years of corrections (correction-form
archive + `csl-orig` git history) into a 50,953-event corpus and a **two-axis
typology** — **location** (where in the entry) × **edit-type** (what kind of edit).
Design: [`docs/ERROR_TYPOLOGY_DESIGN.md`](docs/ERROR_TYPOLOGY_DESIGN.md) · datasheet:
[`docs/DATASHEET.md`](docs/DATASHEET.md) · live page:
[Error Typology](https://sanskrit-lexicon.github.io/csl-observatory/error-typology).
Reports: [typology](reports/obs_t_typology.md) · [rigor](reports/obs_t_rigor.md) ·
[robustness](reports/obs_t_robustness.md) · [baselines](reports/obs_t_baselines.md) ·
[campaigns](reports/obs_t_campaigns.md) · [transliterator validation](reports/obs_t_translit_validation.md) ·
[silver validation](reports/obs_t_silver.md) · [issue-label corroboration](reports/obs_t_issuelabel.md).

## What's in this repo

| Path | Purpose |
|---|---|
| `scripts/{bus_factor,repo_health,taxonomy_adoption,velocity_timeline,contributor_identity}.py` | The five finding analyses (offline, over the committed site CSVs) |
| `reports/` | Finding reports + [`synthesis.md`](reports/synthesis.md) + index |
| `observatory/fetch.py`, `transform.py`, `build_people.py` | GitHub data fetch → time-series CSVs → contributor identities |
| `observatory/site/` | Observable Framework dashboard source |
| `observatory/site/src/data/` | The CSV snapshots the dashboard and findings read |
| `docs/OBSERVATORY_DESIGN.md` | Boundary-safe design doc with GitHub/org KPI catalog |
| `docs/ARCHIVE.md` | Index of legacy and moved-to-`csl-atlas` docs |
| `runbook/cologne-issue-runbook.md` | Dictionary-repo issue-taxonomy runbook |
| `runbook/cologne-tooling-runbook.md` | Tooling-repo issue-taxonomy runbook |
| `.github/workflows/refresh-observatory.yml` | Monthly auto-refresh (template; needs `workflow` token scope to push) |

## Headline numbers (snapshot 2026-06)

| Metric | Value |
|---|---|
| Repos tracked | 76 |
| Issues + PRs (lifetime) | 5,413 |
| Commits since 2014 | 9,877 |
| Distinct human contributors | 16 |
| Contribution concentration | core trio = 97.6%; 65/76 repos bus factor 1 |
| Most active repo | `csl-orig` (the git-based correction workflow) |
| Peak commit year | 2026 (2,519 commits) |
| Peak issue year | 2025 (1,178 opened) |
| Dominant work type | `text-correction` (4,000+ across 12 years) |

## Refresh cadence

- **Manual**: `cd observatory && python fetch.py && python transform.py && python build_people.py`
- **Auto**: monthly via GitHub Actions (`.github/workflows/refresh-observatory.yml`)

## Report Roadmap

1. **GitHub/org observatory release** — reproducible repository, issue, PR, commit, contributor, and workflow metrics.
2. **Repository health report** — license, citation, README, template, and workflow coverage across the organization.
3. **Maintenance-process report** — taxonomy coverage, refresh bottlenecks, and cross-repo workflow evidence.

The former broad publication roadmap is preserved only as legacy reference in `docs/*LEGACY_BROAD_METRICS.md`.

## Boundary Status

The scope split was merged on 2026-06-04 in
[`csl-observatory` PR #14](https://github.com/sanskrit-lexicon/csl-observatory/pull/14).
New observatory work must start from GitHub repository, issue, PR, commit,
contributor, workflow, project, or organization-process evidence.

## Citation

If you use these data in published work:

> Gasūns, M. et al. (2026). *CSL Observatory: 12 years of Cologne Digital Sanskrit Lexicon* [Data set]. Zenodo. DOI: pending mint.

Plus the snapshot date for reproducibility.

## Tech Stack

- **Runtime**: Python 3.11+
- **Framework**: Observable Framework (dashboard), GitHub CLI (`gh`) for data fetch
- **Build**: `npm` (Observable Framework site) + plain `python` scripts
- **Deploy**: GitHub Pages via `.github/workflows/refresh-observatory.yml`
- **External services**: GitHub REST API (org-wide data fetch)

## Issue Status

This repo uses the **tooling-repo taxonomy** (see [runbook/cologne-tooling-runbook.md](runbook/cologne-tooling-runbook.md)).
The 2026-06-05 observatory work filed 11 issues (#15–#25), all on the
[Tooling Roadmap (project #9)](https://github.com/orgs/sanskrit-lexicon/projects/9)
and split by a `Category` field:

- **Findings** (#22–#25) — the four analysis reports, type `documentation`.
- **Actions** (#15–#21) — the hygiene follow-ups: licenses, default-branch,
  descriptions, archiving, ORCIDs, taxonomy cleanup (`documentation` /
  `infrastructure` / `tech-debt`).

| Milestone | Open issues |
|---|---:|
| Developer Experience | #15–#19, #21–#25 |
| Community | #20 |

Rationale and per-issue checklists: [`docs/hygiene_issues_draft.md`](docs/hygiene_issues_draft.md).
For a live board grouped into Finding/Action columns, open project #9 → a board
view → **Group by → Category**.

---

*Last refreshed 2026-06-05.*
