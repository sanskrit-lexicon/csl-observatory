# csl-observatory

_Created: 07-05-2026 · Last updated: 11-07-2026_

> **Live observatory for 13 years of Cologne Digital Sanskrit Lexicon (CDSL).**
> Tracking 76 repos, 5,413 issues+PRs, 9,877 commits, and 16 contributors since 2014.

## What this is

A meta-repository that **measures the entire sanskrit-lexicon GitHub organisation** and turns 13 years of distributed work into measurable, citable, reproducible knowledge. It serves five distinct use cases:

1. **Org observability** — repositories, issues, PRs, commits, contributors, workflows, and maintenance evidence, published as reproducible findings and a live dashboard.
2. **AI-assisted issue triage** — a living [Agent Automation Roadmap](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/docs/AGENT_ROADMAP.md) maps 820+ open issues across 68 repos by agent-readiness (Tier A: fix+PR; Tier B: verify+comment; Tier C: needs skill; Tier D: blocked on human decision), tracking which corrections agents can supply and in what order.
3. **Maintainer coordination hub** — runbooks, decision logs, skills inventory, and bot-noise policies so Jim/Dhaval can see exactly what automation has touched and what still needs them.
4. **Bot-noise management** — [AI contribution policy](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/docs/AI_CONTRIBUTION_POLICY.md), `no-bot` label protocol, and weekly human-activity feeds so automated agent volume does not drown maintainer discussion threads.
5. **Agent findings digest** — research output from agent sweeps collected in structured `.md` files (see [`docs/question-research-findings.md`](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/docs/question-research-findings.md)) instead of being scattered as GitHub comments; only concrete, actionable findings are posted to issues.

The 2026-06-04 boundary cleanup is merged: dictionary-structure research belongs in [`csl-atlas`](https://github.com/sanskrit-lexicon/csl-atlas), standards/export work belongs in [`csl-standards`](https://github.com/sanskrit-lexicon/csl-standards), and DCS/corpus work belongs in [`VisualDCS`](https://github.com/gasyoun/VisualDCS).

## Quick links

- **[Agent Automation Roadmap](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/docs/AGENT_ROADMAP.md)** — living map of 820+ open issues: which agents can fix/supply data for, which need new skills, and in what order (Tier A–D classification)
- **[Observatory dashboard](https://sanskrit-lexicon.github.io/csl-observatory/)** — live charts, deployed to GitHub Pages via [`.github/workflows/deploy.yml`](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/.github/workflows/deploy.yml)
- **[Findings & reports](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/reports/README.md)** — the five reproducible analyses + the synthesis (start here)
- **[Synthesis](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/reports/synthesis.md)** — *State of the observatory*, the four findings tied into one picture
- **[Tooling Roadmap (project #9)](https://github.com/orgs/sanskrit-lexicon/projects/9)** — findings (#22–25) and action issues (#15–21), grouped by `Category`
- **[Boundary rules](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/docs/BOUNDARY_RULES.md)** — what belongs in the GitHub/org observatory, and what must move elsewhere
- **[Design document](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/docs/OBSERVATORY_DESIGN.md)** — boundary-safe architecture and KPI scope
- **[Docs archive index](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/docs/ARCHIVE.md)** — legacy and moved-to-`csl-atlas` documents in one place
- **[Data downloads](https://github.com/sanskrit-lexicon/csl-observatory/tree/main/observatory/site/src/data)** — every chart's source as CSV
- **[Runbooks](https://github.com/sanskrit-lexicon/csl-observatory/tree/main/runbook)** — the issue-taxonomy procedures applied to all active repos
- **[Maintenance skills](https://github.com/sanskrit-lexicon/cologne-skills)** — portable Claude Code skills for org-wide security & maintenance (PHP XSS sweep · security audit · alert triage)
- **[Contributor & work statistics](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/docs/CONTRIBUTOR_STATS.md)** — per-contributor & per-repo commits, churn, tenure, and issues (2014–2026)
- **[Decisions needed](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/docs/DECISIONS_NEEDED.md)** — open items blocked on a maintainer (decisions, credentials, confirmations)
- **[AI / bot contribution policy](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/docs/AI_CONTRIBUTION_POLICY.md)** — norms for AI-assisted commits, comments, and shared tooling changes
- **[Contributor entry path](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/docs/CONTRIBUTOR_ENTRY_PATH.md)** — safe setup, first tasks, taxonomy labels, and review expectations

## Findings

Five offline, reproducible analyses of the organization (script → report →
site page). Full index and reproduction steps: **[`reports/README.md`](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/reports/README.md)**.
The headline picture is in **[`reports/synthesis.md`](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/reports/synthesis.md)**.

| Finding | Report | Headline |
|---|---|---|
| Contributor concentration | [`bus_factor.md`](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/reports/bus_factor.md) | Core trio = 97.6%; 65/76 repos have bus factor 1; Gini 0.86 |
| Repository health | [`repo_health.md`](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/reports/repo_health.md) | 41/76 repos unlicensed; 46/76 default to `master`; 5 fully clean |
| Issue-taxonomy adoption | [`taxonomy_adoption.md`](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/reports/taxonomy_adoption.md) | 89% typed, 63% conformant; 92% peak in 2025; 54 stray labels |
| Velocity & health timeline | [`velocity_timeline.md`](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/reports/velocity_timeline.md) | 9,877 commits; peak 11 authors/yr; backlog 1,742 (2025) → 913 (2026) |
| Contributor identity | [`contributor_identity.md`](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/reports/contributor_identity.md) | 0/16 authors have a registered ORCID |
| **Error typology (OBS-T)** | [`obs_t_typology.md`](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/reports/obs_t_typology.md) | 52,498 corrections, two axes — location (sense 52.7% · markup 17.5% · headword 17.3%) × edit-type (median edit distance 2; 63% ≤2 chars); cross-dict V=0.432 |

Actionable follow-ups are filed on the [Tooling Roadmap](https://github.com/orgs/sanskrit-lexicon/projects/9)
as issues #15–#21 (Actions), with the findings themselves as #22–#25 (Findings).

### OBS-T — error typology of digital Sanskrit dictionaries

A standalone language-resource + finding track (Phases 1–8), distinct from the
org-process findings above. It unifies 13 years of corrections (correction-form
archive + `csl-orig` git history) into a 52,498-event corpus and a **two-axis
typology** — **location** (where in the entry) × **edit-type** (what kind of edit).
Design: [`docs/ERROR_TYPOLOGY_DESIGN.md`](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/docs/ERROR_TYPOLOGY_DESIGN.md) · datasheet:
[`docs/DATASHEET.md`](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/docs/DATASHEET.md) · live page:
[Error Typology](https://sanskrit-lexicon.github.io/csl-observatory/error-typology).
Reports: [typology](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/reports/obs_t_typology.md) · [rigor](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/reports/obs_t_rigor.md) ·
[robustness](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/reports/obs_t_robustness.md) · [baselines](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/reports/obs_t_baselines.md) ·
[campaigns](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/reports/obs_t_campaigns.md) · [transliterator validation](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/reports/obs_t_translit_validation.md) ·
[silver validation](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/reports/obs_t_silver.md) · [issue-label corroboration](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/reports/obs_t_issuelabel.md).

## What's in this repo

| Path | Purpose |
|---|---|
| **[`docs/AGENT_ROADMAP.md`](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/docs/AGENT_ROADMAP.md)** | **Living map of 820+ open issues: Tier A (agent-fixable), B (verify+comment), C (needs skill), D (blocked). Start here for any automation session.** |
| [`docs/question-research-findings.md`](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/docs/question-research-findings.md) | Digest of question-research sweep (2026-06-27): ~73 posted, ~57 skipped; ready-to-close list |
| [`docs/bug-triage-findings.md`](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/docs/bug-triage-findings.md) | Digest of bug-triage sweep + P5 network retry (2026-06-27): 12 Tier A PRs opened (2 merged), ~8 already-fixed, ~18 skipped; new Tier A: csl-websanlexicon#25, csl-apidev#21 |
| [`scripts/`](https://github.com/sanskrit-lexicon/csl-observatory/tree/main/scripts) | `bus_factor.py`, `repo_health.py`, `taxonomy_adoption.py`, `velocity_timeline.py`, `contributor_identity.py` — the five finding analyses (offline, over the committed site CSVs) |
| [`scripts/check_workspace.py`](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/scripts/check_workspace.py) | Local workspace and sibling-repo prerequisite check |
| [`reports/`](https://github.com/sanskrit-lexicon/csl-observatory/tree/main/reports) | Finding reports + [`synthesis.md`](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/reports/synthesis.md) + index |
| [`observatory/fetch.py`](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/observatory/fetch.py), [`transform.py`](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/observatory/transform.py), [`build_people.py`](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/observatory/build_people.py) | GitHub data fetch → time-series CSVs → contributor identities |
| [`observatory/site/`](https://github.com/sanskrit-lexicon/csl-observatory/tree/main/observatory/site) | Observable Framework dashboard source |
| [`observatory/site/src/data/`](https://github.com/sanskrit-lexicon/csl-observatory/tree/main/observatory/site/src/data) | The CSV snapshots the dashboard and findings read |
| [`docs/OBSERVATORY_DESIGN.md`](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/docs/OBSERVATORY_DESIGN.md) | Boundary-safe design doc with GitHub/org KPI catalog |
| [`docs/AI_CONTRIBUTION_POLICY.md`](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/docs/AI_CONTRIBUTION_POLICY.md) | AI-assisted and automated contribution norms |
| [`docs/CONTRIBUTOR_ENTRY_PATH.md`](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/docs/CONTRIBUTOR_ENTRY_PATH.md) | Safe contributor setup and first-task guide |
| [`docs/ARCHIVE.md`](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/docs/ARCHIVE.md) | Index of legacy and moved-to-`csl-atlas` docs |
| [`runbook/cologne-issue-runbook.md`](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/runbook/cologne-issue-runbook.md) | Dictionary-repo issue-taxonomy runbook |
| [`runbook/cologne-tooling-runbook.md`](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/runbook/cologne-tooling-runbook.md) | Tooling-repo issue-taxonomy runbook |
| [`.github/workflows/refresh-observatory.yml`](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/.github/workflows/refresh-observatory.yml) | Monthly auto-refresh (template; needs `workflow` token scope to push) |

## Org maintenance skills

Reusable [Claude Code](https://claude.com/claude-code) skills for security and maintenance across the organisation live in **[`sanskrit-lexicon/cologne-skills`](https://github.com/sanskrit-lexicon/cologne-skills)** — the shareable cut of the `/cologne-*` command family, encoding battle-tested playbooks (escaping decision tables, false-positive heuristics, the gotchas).

| Command | What it does |
|---|---|
| `/cologne-php-xss-sweep <repo\|all>` | Find + fix reflected-XSS / SQL-injection / injection in a repo's PHP web-frontend (context-correct escaping), PR-only |
| `/cologne-security-audit-all` | Org-wide audit — GitHub Actions (pwn-request / script-injection / token scope), committed secrets, SAST coverage |
| `/cologne-alert-triage <repo>` | Triage CodeQL + Semgrep alerts: fix the genuine ones (PR), dismiss false-positives/won't-fixes with written justifications |

Install: `git clone` that repo, then `cp .claude/commands/*.md ~/.claude/commands/` (or symlink). These complement the issue-taxonomy [runbooks](https://github.com/sanskrit-lexicon/csl-observatory/tree/main/runbook) above.

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
| Dominant work type | `text-correction` (4,000+ across 13 years) |

## Refresh cadence

- **Manual**: `cd observatory && python fetch.py && python transform.py && python build_people.py`
- **Auto**: monthly via GitHub Actions ([`.github/workflows/refresh-observatory.yml`](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/.github/workflows/refresh-observatory.yml))

## Report Roadmap

1. **GitHub/org observatory release** — reproducible repository, issue, PR, commit, contributor, and workflow metrics.
2. **Repository health report** — license, citation, README, template, and workflow coverage across the organization.
3. **Maintenance-process report** — taxonomy coverage, refresh bottlenecks, and cross-repo workflow evidence.

The former broad publication roadmap is preserved only as legacy reference in [`docs/OBSERVATORY_DESIGN_LEGACY_BROAD_METRICS.md`](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/docs/OBSERVATORY_DESIGN_LEGACY_BROAD_METRICS.md) and its siblings.

## Boundary Status

The scope split was merged on 2026-06-04 in
[`csl-observatory` PR #14](https://github.com/sanskrit-lexicon/csl-observatory/pull/14).
New observatory work must start from GitHub repository, issue, PR, commit,
contributor, workflow, project, or organization-process evidence.

## Citation

If you use these data in published work:

> Gasūns, M. et al. (2026). *CSL Observatory: 13 years of Cologne Digital Sanskrit Lexicon* [Data set]. `sanskrit-lexicon/csl-observatory` (no Zenodo DOI minted yet).

Plus the snapshot date for reproducibility. `10.5281/zenodo.15834721`, previously cited here, was a false DOI — it resolves to an unrelated topology preprint, confirmed by a live check 20-07-2026 (H1364; see [SanskritLexicography CONTRADICTIONS §8](https://github.com/gasyoun/SanskritLexicography/blob/master/CONTRADICTIONS.md)).

## Tech Stack

- **Runtime**: Python 3.11+
- **Framework**: Observable Framework (dashboard), GitHub CLI (`gh`) for data fetch
- **Build**: `npm` (Observable Framework site) + plain `python` scripts
- **Deploy**: GitHub Pages via [`.github/workflows/deploy.yml`](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/.github/workflows/deploy.yml)
- **External services**: GitHub REST API (org-wide data fetch)

## Issue Status

This repo uses the **tooling-repo taxonomy** (see [`runbook/cologne-tooling-runbook.md`](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/runbook/cologne-tooling-runbook.md)).
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

Rationale and per-issue checklists: [`docs/hygiene_issues_draft.md`](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/docs/hygiene_issues_draft.md).
For a live board grouped into Finding/Action columns, open project #9 → a board
view → **Group by → Category**.

---

_Last refreshed 11-07-2026._

_Dr. Mārcis Gasūns_
