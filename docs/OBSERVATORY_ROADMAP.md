# csl-observatory Implementation Roadmap

_Created: 16-05-2026 · Last updated: 03-07-2026_

Horizon: 2026-06 to 2027-06
Primary audience: maintainer. Secondary audiences, added later in the year:
future contributors and paper/release reviewers.
Phase-2 audience decision (MG, 2026-07-03): scholars first, some of whom may
become future contributors — no funder-facing work. See Workstream G.

This document is the implementation plan for the observatory itself. The
maintainer-facing priority order lives in [`ROADMAP.md`](ROADMAP.md).

## Boundary Rule

Every active observatory item must start from repository, issue, pull request,
commit, contributor, workflow, project-board, repository metadata, release, or
organization-maintenance evidence.

Do not move dictionary structure, TEI/OntoLex, DCS/corpus, lookup analytics, or
broad publication planning back into this roadmap. Link to sibling projects or
archived docs instead.

## Current Evidence Base

| Finding | Current signal | Source |
|---|---|---|
| Repository health | 41/76 repos have no license; 21 have unrecognized license files; 46 default to `master`; 6 cleanup candidates remain live. | `reports/repo_health.md` |
| Sustainability | 67/76 repos have bus factor 1; core trio accounts for 98.0% of contributions; SC3 has an action plan. | `reports/bus_factor.md`, `docs/BUS_FACTOR_ACTION_PLAN.md` |
| Contributor identity | 0 registered ORCIDs in the contributor map; 7 confirmed names need ORCIDs; 9 identities need triage. | `reports/contributor_identity.md` |
| Issue taxonomy | Taxonomy is useful but still needs rollout/maintenance across repos and Org Project #9. | `reports/taxonomy_adoption.md`, `docs/RUNBOOK_NOTES.md` |
| Workflow reliability | 28/76 active repos have workflows; 11 have scheduled workflows; 13 have artifact/deploy/refresh workflows; 18 have Dependabot; 8 have CodeQL; 1 has releases. | `reports/workflow_health.md`, `/workflow-health` |
| Maintainer dashboards | Seven operational pages now provide the control surface for repo risk, B3 metadata, workflow health, taxonomy triage, continuity, and OBS-T maintenance. | `/ops-command`, `/repository-risk`, `/metadata-readiness`, `/workflow-health`, `/taxonomy-triage`, `/community-continuity`, `/obs-t-maintenance` |
| OBS-T | Post-review corpus is rebuilt and regression-gated; it should not drive the next roadmap phase. | `reports/obs_t_*.md`, `scripts/obs_t_regression.py` |

## Workstream A: Snapshot And Data Backbone

Goal: make every observatory report refresh from reproducible, dated snapshots.

| ID | Deliverable | Owner | Status | Target | Acceptance |
|---|---|---|---|---|---|
| A1 | Repository inventory with type, archival state, default branch, license, metadata, and cleanup flags. | Codex | active | 2026-07-15 | `repos.csv` and `repo_health.md` regenerate without manual edits; cleanup candidates are explicit. |
| A2 | Issue/PR/project snapshot refresh command. | Codex | scheduled | 2026-08-15 | One command refreshes issues, PRs, labels, milestones, and project-board fields with rate-limit notes. |
| A3 | Contributor and identity snapshot refresh. | Codex | scheduled | 2026-09-15 | Contributor reports regenerate from `contributors_map.json` and flag missing consent/ORCID fields. |
| A4 | Workflow/release metadata snapshot. | Codex | done | 2026-06-13 | `repo_metadata.csv` and `workflow_health.csv` expose workflow/release/dependabot/codeql status for active repos. |
| A5 | Snapshot manifest. | Codex | active | 2026-12-15 | `scripts/refresh_observatory.py` writes JSON and Markdown refresh summaries; extend coverage as live snapshot automation expands. |

## Workstream B: Repository Health Dashboard

Goal: turn repo health into a maintainable cleanup queue, not just a report.

| ID | Deliverable | Owner | Status | Target | Acceptance |
|---|---|---|---|---|---|
| B1 | License backlog dashboard. | Codex | done | 2026-07-31 | Repo Health page separates no-license, unrecognized-license, and recognized-SPDX repos with linked issues/decisions. |
| B2 | Cleanup-candidate dashboard. | Codex | done | 2026-07-31 | Repo Health page lists `temp_*`, `test_*`, and legacy repos with archive/retain blockers. |
| B3 | Metadata completeness dashboard. | Codex | done | 2026-06-13 | Repo Metadata page, cached live fetcher, and complete live `repo_metadata.csv` exist with 76 rows, 0 fetch warnings, and 0 unknown live fields. |
| B4 | Repository health regression check. | Codex | done | 2026-09-15 | `scripts/repo_health_regression.py` fails when generated health schema/report columns drift unexpectedly. |

## Workstream C: Sustainability And Contributor Metrics

Goal: measure continuity risk and make it actionable for the maintainer.

| ID | Deliverable | Owner | Status | Target | Acceptance |
|---|---|---|---|---|---|
| C1 | Maintainer identity update loop. | MG | scheduled | 2026-09-15 | `contributors_map.json` has reviewed names/ORCIDs where possible; unknowns are explicitly marked. |
| C2 | Bus-factor action table. | Codex | done | 2026-10-15 | `docs/BUS_FACTOR_ACTION_PLAN.md` links each high-risk class to mitigation: runbook, owner backup, automation, or accepted risk. |
| C3 | Onboarding surface. | MG + Codex | done | 2026-11-15 | A contributor-facing page lists safe tasks, setup, labels, review expectations, and AI contribution policy. |
| C4 | Maintainer review packet. | Codex | done | 2026-06-13 | Monthly checklist exists and the live maintainer dashboards summarize repo health, B3 metadata, bus factor, open taxonomy work, and next actions. |

## Workstream D: Workflow And Refresh Reliability

Goal: reduce single-machine and single-maintainer operational risk.

| ID | Deliverable | Owner | Status | Target | Acceptance |
|---|---|---|---|---|---|
| D1 | Local workspace checker. | Codex | done | 2026-09-30 | Script verifies sibling repos, history depth, clean/dirty state, and required paths. |
| D2 | Refresh script modernization plan. | Codex | done | 2026-10-15 | `docs/REFRESH_SCRIPT_MODERNIZATION_PLAN.md` covers Python 3, parameters, dry-run, manifests, and dependencies. |
| D3 | Refresh script implementation. | Codex | scheduled | 2026-10-31 | Modernized script runs outside the Cologne server assumptions or documents remaining blockers. |
| D4 | Monthly refresh automation. | Codex | active | 2026-11-30 | Reports and site data can be refreshed locally with one command and a generated summary; scheduled workflow/credential hardening remains. |
| D5 | Workflow health report. | Codex | done | 2026-06-13 | `reports/workflow_health.md` and `/workflow-health` show CI, scheduled, release, artifact-refresh/deploy, Dependabot, CodeQL, and row-level fetch-warning state. |

## Workstream E: Public Site And Release Surfaces

Goal: make the observatory useful to the maintainer first, then understandable to
contributors and reviewers.

| ID | Deliverable | Owner | Status | Target | Acceptance |
|---|---|---|---|---|---|
| E1 | Dashboard information architecture refresh. | Codex | done | 2026-06-13 | Pages mirror the active maintainer findings: operations, repository risk, metadata readiness, workflow health, taxonomy triage, community continuity, and OBS-T maintenance light. |
| E2 | Downloadable data index. | Codex | done | 2026-06-13 | `scripts/data_index.py` and `/data` list every public CSV/JSON with description, source script, generated date, caveat, and download link. |
| E3 | Reviewer reproducibility page. | MG + Codex | done | 2026-06-13 | `docs/REVIEWER_REPRODUCIBILITY.md` and `/reproducibility` document report refresh, credentials, dashboard build, OBS-T checks, human-gated steps, and citation inputs. |
| E4 | Contributor guide page. | MG + Codex | scheduled | 2027-03-31 | Future contributors see setup, safe issues, taxonomy, AI policy, and boundaries. |
| E5 | Annual snapshot release. | MG + Codex | scheduled | 2027-04-15 | Tag/release includes generated reports, data snapshot, manifest, and known caveats. |
| E6 | Site SEO + discoverability foundation. | Codex | done | 2026-06-30 | `observablehq.config.js` injects a per-page `<head>` (canonical, meta description, Open Graph, Twitter `summary_large_image`) for origin `https://sanskrit-lexicon.github.io/csl-observatory/`. Distinct per-page descriptions via a `PAGE_DESCRIPTIONS` route map (Framework drops non-whitelisted front-matter keys). 1200×630 social card (`scripts/make_social_card.py`), `sitemap.xml` (`scripts/make_sitemap.py`), and `robots.txt` emitted into `dist/` by `scripts/postbuild.mjs` (npm `postbuild`). Build clean (19 pages, 58 links); tags + statics verified in `dist/`. |

## Workstream F: OBS-T Maintenance And Paper Package

Goal: keep OBS-T healthy, but do not let it displace repository-health and
sustainability work.

| ID | Deliverable | Owner | Status | Target | Acceptance |
|---|---|---|---|---|---|
| F1 | Keep OBS-T regression green. | Codex | active | ongoing | `scripts/obs_t_regression.py` passes after refreshes. |
| F2 | Human validation samples. | MG | scheduled | 2027-04-30 | Gold/error samples are made, annotated, scored, or explicitly deferred. |
| F3 | Paper reviewer artifact. | MG + Codex | scheduled | 2027-06-15 | Frozen corpus, reports, datasheet, license, and reproduction instructions are ready. |

The completed OBS-T post-review implementation tracker is archived at
[`archive/OBS_T_FIX_PLAN_2026-06-12.md`](archive/OBS_T_FIX_PLAN_2026-06-12.md).

## Workstream G: Phase-2 Research Tracks (2026-07-03 Rethink)

Goal: open genuinely new measurement axes beyond retrospective-descriptive
audit. MG decisions (2026-07-03): audience = scholars (→ future contributors);
measurement priority = lifecycle ≈ predictive/risk > external impact > network;
visual forms = all four (networks, calendar/small-multiples, survival/Sankey,
narrative story page); mode = **active monitor**, not passive dashboard.

| ID | Deliverable | Owner | Status | Target | Acceptance |
|---|---|---|---|---|---|
| G1 | Issue lifecycle & responsiveness track. | Codex | **shipped 2026-07-03** | 2026-07-31 | Commit `869c313`: [`scripts/issue_lifecycle.py`](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/scripts/issue_lifecycle.py) → [`reports/issue_lifecycle.md`](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/reports/issue_lifecycle.md) + 4 CSVs + `/lifecycle` page (survival heatmap, backlog age pyramid, latency band, per-repo dots). Headlines: median close 6 d / p90 349 d; 23% still open at 1 year; 620/913 open issues 4+ years old; 178 silent. Time-to-first-response remains an API-gated extension (no comment timestamps offline). |
| G2 | Active delta monitor. | Codex | **shipped 2026-07-03** | 2026-07-31 | Commit `1fcc41d`: [`scripts/monitor_deltas.py`](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/scripts/monitor_deltas.py) compares the fresh snapshot vs HEAD (backlog/silent/stale/repos/contributors/bus-factor/conformance) → [`reports/monitor_digest.md`](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/reports/monitor_digest.md) + Actions run summary; wired into `refresh-observatory.yml` before the refresh commit; alert path tested with a mutated snapshot. |
| G3 | Capture–recapture estimate of errors remaining per dictionary. | Codex + MG | **shipped 2026-07-03** | 2026-09-30 | Commit `acd8687`: [`scripts/error_recapture.py`](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/scripts/error_recapture.py) → [`reports/error_recapture.md`](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/reports/error_recapture.md) + `/error-typology` section. Chapman two-occasion (form era vs git era): pw ~78k error-prone records (~14% done) / mw ~65k (~10%) / bur capped at its full 19,776; Chao heterogeneity scenario + sensitivities. Paper scaffolded as **A48** ([`article/A48_error_recapture.md`](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/article/A48_error_recapture.md)). |
| G4 | Contributor–repo network page. | Codex | **shipped 2026-07-03** | 2026-08-31 | Commit `e9de36d`: `/network` — deterministic D3 force map (11 humans × 76 repos, 196 edges; bus-factor coloring; **zero repos at bus factor ≥ 3**) + Plot.cell adjacency-matrix accessible view. Cross-repo issue-reference graph stays API-gated (snapshot carries no issue bodies). |
| G5 | Narrative story page. | Codex + MG | **shipped 2026-07-03** | 2026-09-30 | `observatory/site/src/story.md` (`/story`) — one scroll-through 13-year org history with annotated turning points (2014–16 cfr era → 2019 git era → 2021 volume peak → 2025 correction wave → 2026 taxonomy) + the four standing findings woven as narrative turns; every figure computed live from committed CSV/JSON (light-weight `obs_t_timeline.csv`, 42 kB payload). Registered first in nav + `PAGE_DESCRIPTIONS`, linked from home; build clean, sitemap refreshed. **MG text-read gate open** (GTD @DO). |
| G6 | External impact & reach (scholar-framed). | Codex | **shipped 2026-07-03** | 2026-10-31 | [`scripts/external_reach.py`](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/scripts/external_reach.py) (API tiers behind `--fetch`, committed JSON cache under `observatory/snapshots/2026-07/external_reach/`, regenerates offline) → [`reports/external_reach.md`](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/reports/external_reach.md) + `external_reach.csv` + new `/reach` page. **Four measured/estimated tiers**, provenance per line: stars/forks (103 stars total, 49/76 zero-star — a finding) · 14-day traffic (**6,923 clones** across the core sample vs 103 stars = the headline) · downstream dependents (10 curated consumers — PyCDSL, Ambuda, DPD, StarDict-Sanskrit, Ashtadhyayi.com … + 17 code-search repos, each URL-cited) · representative citations (5, no completeness claim). Traffic API needed no token — the agent's `gh` session (gasyoun, push) served it directly. **Zenodo tier BLOCKED**: the recorded OBS-T DOI `10.5281/zenodo.15834721` resolves to an unrelated topology preprint (not OBS-T) — MG decision to re-mint/correct, tracked in GTD; the script flags it rather than reporting a stranger's downloads. Build 76 links / smoke 30 plots / catalog 52 files green. **Extension:** systematic Scholar/OpenAlex citation sweep. |

## Review Cadence

- Weekly: update status in `ROADMAP.md` and this file.
- Monthly: use `docs/MAINTAINER_REVIEW_CHECKLIST.md`, rerun core reports, and
  refresh the evidence base.
- Quarterly: decide whether to move scheduled items forward, archive completed
  implementation plans, and update the contributor/reviewer surfaces.

## Out Of Scope But Linked

- Dictionary microstructure and genealogy: `csl-atlas`.
- Standards/export work: `csl-standards`.
- DCS/corpus/grammar: `VisualDCS` or future grammar repo.
- Broad publication planning: archived docs unless a new maintainer decision
  assigns a live home.

_Dr. Mārcis Gasūns_
