# CDSL Observatory: One-Year Maintainer Roadmap

_Created: 30-05-2026 · Last updated: 05-09-2026_

Last updated: 2026-08-27
Horizon: 2026-06 to 2027-06

> **Truth-pass 27-08-2026 (Opus 5 `claude-opus-5`, [H3002](https://github.com/gasyoun/Uprava/blob/main/handoffs/archive/H3002-Opus_multi_stale-roadmap-s4-cologne-ask-replan_17.08.26.md), stale-roadmap slice 4).**
> Statuses only — no new items, no re-scoping. Two Q3 rows (RH1, RH3) still read `blocked`
> although MG approved both on **2026-06-17** and the RH1 rollout completed 2026-06-19; the
> "Next Implementation Session" section at the foot still opens by asking for those same two
> approvals. Both are corrected below against
> [`docs/REPOSITORY_HEALTH_DECISION_PACKET.md`](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/docs/REPOSITORY_HEALTH_DECISION_PACKET.md)
> and the 2026-08-24 regeneration of
> [`reports/repo_health.md`](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/reports/repo_health.md).
> Everything else in the file measured accurate.
Audience: maintainer first. Contributor and reviewer-facing surfaces are planned
after the maintenance backbone is sturdier.

## Purpose

This is the active maintainer roadmap for `csl-observatory` and the
repository/process work it measures across the `sanskrit-lexicon` GitHub
organization. It is action-oriented: every item has an owner, a target date, and
an acceptance condition.

The priority order for the next year is:

1. Repository-health actions.
2. Sustainability and community continuity.
3. Automation and refresh reliability.
4. Public observatory release surfaces for future contributors and reviewers.
5. OBS-T paper readiness, last, after the infrastructure is safer.

For the implementation detail behind the observatory itself, see
[`OBSERVATORY_ROADMAP.md`](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/docs/OBSERVATORY_ROADMAP.md).

## Scope Rules

Active roadmap items must start from repository, issue, pull request, commit,
contributor, workflow, project-board, repository-metadata, release, or
organization-maintenance evidence.

Out of scope here: dictionary-content research, dictionary genealogy, TEI/OntoLex
exports, corpus/DCS work, lookup analytics, and broad publication planning. Those
belong in sibling projects or archived planning docs.

## Status And Owners

| Field | Meaning |
|---|---|
| Owner | `MG` = maintainer; `Codex` = implementation assistant; `Org` = requires sanskrit-lexicon maintainer decision |
| Status | `next`, `active`, `blocked`, `scheduled`, `done` |
| Cadence | **Monthly**, on the `docs/MAINTAINER_REVIEW_CHECKLIST.md` ritual (SC6); update statuses after each implementation session. *Re-stated 27-08-2026: this row read "every Friday", which neither matched the observed edit history (29-07-2026 → 27-08-2026 with no status change) nor SC6's own monthly ritual. A cadence nobody keeps is worse than an honest one.* |

## 2026-Q3: Repository Health First

| ID | Action | Owner | Status | Target | Acceptance |
|---|---|---|---|---|---|
| RH1 | Decide license policy for code/data/dictionary repos. | MG + Org | done | 2026-06-28 | **Approved by MG 2026-06-17**, five repo groups ruled, in `docs/REPOSITORY_HEALTH_DECISION_PACKET.md` §1. Rollout **complete 2026-06-19** — ~36 repos licensed across 7 batches, logged in `docs/RH1_LICENSE_ROLLOUT_LOG.md`. Met inside target. |
| RH2 | Resolve the license backlog from `reports/repo_health.md`: 41 no-license repos and 21 `NOASSERTION` repos. | MG + Codex | done | 2026-08-31 | Each repo has a recognized license or an explicit issue explaining why not. RH1 rollout (PR #54/#55, merged 2026-06-19/20) resolved this: `reports/repo_health.md` (2026-07-28) shows 0/77 `NOASSERTION` and 6/77 no-license, all six being the RH3 archive/temp candidates (intentionally excluded, tracked separately). |
| RH3 | Archive or justify the six cleanup candidates: `santamlegacy`, `temp_corrections_*`, `test_cologne_push`. | funderburkjim | active | 2026-07-15 | **Decision made 2026-06-17; 4 of 6 archived 2026-06-19** (`santamlegacy`, `temp_corrections_acc`, `temp_corrections_ae`, `test_cologne_push`, via `scripts/rh3_archive.py`). `temp_corrections_ap90` and `temp_corrections_mw` each still hold one open *active* scholarly-question issue authored by funderburkjim — **MG ruled 2026-06-19 that he migrates/closes them**, then `scripts/rh3_archive.py` (which blocks on open issues) is simply re-run. Not `blocked` on a decision: the decision exists. Owner moved off `MG + Org` accordingly. |
| RH4 | Add a standard `.gitattributes` / line-ending policy to active tooling repos. | Codex | done | 2026-07-31 | All 34 repos in `.github/workflows/tooling-audit.yml` REPOS carry `eol=lf` `.gitattributes` — verified and rolled out 2026-07-27 via [H1542](https://github.com/gasyoun/Uprava/blob/main/handoffs/archive/H1542-Sonnet_csl-observatory_rh4-gitattributes-lf-rollout_23.07.26.md). |
| RH5 | Add no-BOM, UTF-8, NFC, and XML parse guards for dictionary-source change paths. | Codex | done | 2026-08-15 | CI template exists and is piloted on `csl-orig` or the owning tooling repo. |
| RH6 | Finish issue-taxonomy rollout across remaining repos. | MG + Codex | done | 2026-08-31 | Rollout is verified complete; ongoing taxonomy/project drift is handled by the monthly maintainer review checklist. |
| RH7 | Normalize missing descriptions and basic metadata for the top flagged repos. | MG | active | 2026-09-30 | `reports/repo_health.md` missing-description list is empty or justified. **Target re-dated 27-08-2026** — the 2026-07-31 target passed unmet. Nearly there: the 2026-08-24 regeneration shows **3 / 77** repos still without a description (`csl-inflect`, `hwnorm2`, `sanskrit-lexicon.github.io`), so this is three one-line `gh repo edit --description` calls plus a report refresh, not a project. |

Evidence to keep current: `reports/repo_health.md`,
`docs/hygiene_issues_draft.md`, `docs/RUNBOOK_NOTES.md`,
`docs/REPOSITORY_HEALTH_DECISION_PACKET.md`,
`docs/METADATA_COMPLETENESS_DASHBOARD_PLAN.md`, and (RH5)
`docs/ENCODING_GUARD.md`. Maintainer dashboard entry points:
`/ops-command`, `/repository-risk`, and `/metadata-readiness`.

## 2026-Q3/Q4: Sustainability And Community Continuity

| ID | Action | Owner | Status | Target | Acceptance |
|---|---|---|---|---|---|
| SC1 | Complete the contributor identity worksheet. | MG | next | 2026-09-15 | `scripts/contributors_map.json` has confirmed names/ORCIDs where contributors consent; unknowns are triaged. |
| SC2 | Create a maintainer continuity packet for the core workflows. | MG + Codex | done | 2026-09-30 | A new maintainer can run observatory refresh, correction reports, and dashboard build from documented steps. |
| SC3 | Convert the bus-factor finding into an action plan. | MG + Codex | done | 2026-10-15 | Top five bus-factor risks have linked mitigation issues or explicit accepted risk notes. |
| SC4 | Roll out `AI_CONTRIBUTION_POLICY.md` into contributor guidance. | MG + Codex | done | 2026-08-15 | README/CONTRIBUTING text points to the policy; bot/AI contribution expectations are unambiguous. |
| SC5 | Prepare a contributor entry path. | MG + Codex | done | 2026-11-15 | A contributor page lists setup, good first issues, taxonomy labels, and where not to work. |
| SC6 | Add a lightweight monthly maintainer review ritual. | MG | done | 2026-07-01 | Calendar/checklist exists: health report, open blockers, bus-factor risks, next project-board moves. |

Evidence to keep current: `reports/bus_factor.md`,
`reports/contributor_identity.md`, `reports/synthesis.md`,
`docs/BUS_FACTOR_ACTION_PLAN.md`, `docs/MAINTAINER_CONTINUITY_PACKET.md`, and
`docs/MAINTAINER_REVIEW_CHECKLIST.md`. Maintainer dashboard entry points:
`/community-continuity` and `/ops-command`.

## 2026-Q4: Automation And Refresh Reliability

| ID | Action | Owner | Status | Target | Acceptance |
|---|---|---|---|---|---|
| AR1 | Modernize `redo_xampp_selective.sh` and related refresh scripts. | Codex | active | 2026-10-31 | Python 2 removed, hardcoded paths parameterized, prerequisites documented, dry-run mode available. Code-side refactor landed 14-07-2026 ([csl-pywork#68](https://github.com/sanskrit-lexicon/csl-pywork/pull/68), plan steps 1-6/10 of `REFRESH_SCRIPT_MODERNIZATION_PLAN.md`) — new `v02/redo_xampp_selective.py` driver (parameterized `--base`/`--indic-base`, `--dry-run`, `--no-push`, `--strict-clean`, JSON manifest), `.sh` now a thin wrapper, 13 tests against a synthetic layout. Confirmed `make_babylon.py`/`json_from_babylon.py` were already Python 3 compatible — only the interpreter binary was wrong. **Remaining:** live server rehearsal (plan steps 7-9) needs Cologne server access (C2, not yet granted); status stays `active` not `done` until that rehearsal runs. |
| AR2 | Add a local clone/bootstrap checker for sibling repos. | Codex | done | 2026-09-30 | Setup script verifies `csl-observatory`, `csl-orig`, and `CORRECTIONS` are real working trees with enough history. |
| AR3 | Automate monthly observatory refresh. | Codex | active | 2026-11-30 | Local refresh runner exists with dry-run, manifest, summary, checks, and site build; scheduled workflow/credential hardening remains. |
| AR4 | Build workflow reliability baseline. | Codex | done | 2026-06-13 | `reports/workflow_health.md`, `/workflow-health`, and `workflow_health.csv` list CI, cron/scheduled, release, artifact-refresh, Dependabot, and CodeQL status for active repos. |
| AR5 | Keep generated outputs reproducible and reviewable. | Codex | active | ongoing | Generated CSV/JSON/report churn is explained in release notes and gated by regression checks. |

Evidence to keep current: `reports/README.md`, generated site data under
`observatory/site/src/data/`, `docs/REFRESH_SCRIPT_MODERNIZATION_PLAN.md`, and
the Tooling Roadmap project.

## 2027-Q1: Public Observatory Release

| ID | Action | Owner | Status | Target | Acceptance |
|---|---|---|---|---|---|
| PR1 | Produce a 2026/2027 observatory snapshot release. | MG + Codex | scheduled | 2027-01-31 | Tagged release includes data snapshot date, report index, caveats, and reproducibility commands. |
| PR2 | Make maintainer dashboard pages match the active findings. | Codex | done | 2026-06-13 | Maintainer-first pages now cover operations, repository risk, metadata readiness, taxonomy triage, community continuity, and OBS-T maintenance light; contributor/reviewer polish remains in PR3/PR4. |
| PR3 | Add a reviewer-facing reproducibility note. | MG + Codex | done | 2026-06-13 | `docs/REVIEWER_REPRODUCIBILITY.md` and `/reproducibility` document report refresh, credentials, dashboard build, OBS-T checks, and human-gated commands. |
| PR4 | Add a contributor-facing "where to help" page. | MG + Codex | scheduled | 2027-03-31 | Future contributors can see safe entry points: metadata cleanup, issue taxonomy, docs, tests, and dashboards. |
| PR5 | Make the public site discoverable (SEO foundation). | Codex | done | 2026-06-30 | Per-page `<head>` (canonical, distinct descriptions, Open Graph, Twitter `summary_large_image`), 1200×630 social card, `sitemap.xml`, and `robots.txt` all ship via `observablehq.config.js` + `scripts/`. See `OBSERVATORY_ROADMAP.md` E6. |

## 2027-Q2: Paper And OBS-T Readiness Last

| ID | Action | Owner | Status | Target | Acceptance |
|---|---|---|---|---|---|
| OT1 | Keep OBS-T release green after infrastructure work. | Codex | scheduled | 2027-04-15 | `scripts/obs_t_regression.py` passes after any refresh; datasheet and reports match generated counts. |
| OT2 | Run human-gated OBS-T validation samples. | MG | scheduled | 2027-04-30 | `obs_t_gold.py --make/--score` and `obs_t_errorsample.py --make/--score` have annotated outputs or documented deferral. |
| OT3 | Draft the OBS-T paper package. | MG + Codex | scheduled | 2027-05-31 | Draft has dataset statement, limitations, baselines, statistics, and release checklist. |
| OT4 | Freeze a paper-reviewer artifact. | MG + Codex | scheduled | 2027-06-15 | DOI/tag or frozen archive exists with exact data, scripts, reports, and reviewer instructions. |

The completed post-review OBS-T fix tracker is archived at
[`archive/OBS_T_FIX_PLAN_2026-06-12.md`](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/docs/archive/OBS_T_FIX_PLAN_2026-06-12.md).

## Parking Lot

These are valuable but not first-year blockers:

- Org-wide branch-name normalization after license and cleanup decisions.
- CodeQL/Dependabot rollout for every maintained tooling repo.
- A reusable observatory report package.
- Broader comparative project metrics, if restricted to public repository metadata.
- Dictionary-content roadmaps in `csl-atlas` and standards/export work in
  `csl-standards`.

## Next Implementation Session

**Rewritten 27-08-2026.** Steps 1 and 2 previously asked for the license-matrix
and cleanup-candidate approvals — both of which MG granted on **2026-06-17**, so
the file's own opening instruction had been pointing the next session at a
decision that already existed for two months. What is actually left:

1. **RH7 — three descriptions.** `gh repo edit sanskrit-lexicon/<repo> --description "…"`
   for `csl-inflect`, `hwnorm2`, and `sanskrit-lexicon.github.io`, then re-run
   `scripts/repo_health.py`. The smallest open item on this roadmap.
2. **RH3 — nothing for us.** The two unarchived `temp_corrections_*` repos wait
   on funderburkjim closing his own open issues; re-run `scripts/rh3_archive.py`
   once they are clear. Do not force it.
3. **AR1/AR3 — the real engineering.** Both are `active` and both stop at the
   same wall: the live-server rehearsal (plan steps 7–9 of
   `docs/REFRESH_SCRIPT_MODERNIZATION_PLAN.md`) and the scheduled-refresh
   credential hardening need Cologne server access (C2), not more code.
4. **Control surface** for the monthly review, unchanged:
   `docs/WEEKLY_MAINTAINER_WORK_PLAN_2026-06-13.md`, `/ops-command`,
   `/repository-risk`, `/taxonomy-triage`, `/community-continuity`.

_Dr. Mārcis Gasūns_
