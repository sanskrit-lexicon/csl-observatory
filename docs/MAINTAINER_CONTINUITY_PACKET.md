# Maintainer Continuity Packet

Date: 2026-06-12
Status: SC2 continuity handoff for core `csl-observatory` workflows.

This packet is for a maintainer or trusted assistant who needs to refresh the
observatory, regenerate correction reports, or rebuild the dashboard without
depending on one person's local memory.

It does not authorize external repository mutations. Do not archive repositories,
apply licenses, rename branches, push to sibling repositories, or change
organization settings from this file alone.

## Core Workflows Covered

| Workflow | Purpose | Network needed | Writes |
|---|---|---|---|
| Observatory snapshot refresh | Fetch current GitHub repo/issue/commit/contributor metadata. | yes, `gh` auth | `observatory/snapshots/`, `data/`, `observatory/site/src/data/` |
| Offline finding reports | Recompute repository health, bus factor, taxonomy, velocity, and identity reports from committed CSVs. | no | `reports/*.md`, `observatory/site/src/data/*.csv` |
| OBS-Q / OBS-T correction reports | Rebuild correction sustainability and correction-event typology outputs. | mostly no; optional issue-latency refresh uses `gh` | `reports/obs_*.md`, `observatory/site/src/data/obs_*`, `correction_events_*` |
| Dashboard build | Build the Observable Framework site from committed data. | no after npm install | `observatory/site/dist/` |

## Required Workspace

The expected local layout has sibling repositories under the same parent
directory:

```text
GitHub/
  csl-observatory/
  csl-orig/
  CORRECTIONS/
```

Run these checks from `csl-observatory` before any corpus-affecting refresh:

```powershell
python scripts/check_workspace.py
```

For automation or issue comments, use `python scripts/check_workspace.py --json`.
Use `--strict-clean` only when a clean worktree is required; normal report
refreshes may run in a dirty local workspace after the diff is inspected.

Required tools:

```powershell
python --version
node --version
npm --version
gh auth status
```

Expected versions and packages:

- Python 3.11+ for local scripts; GitHub Actions uses 3.12 for the scheduled
  refresh workflow.
- Node 20+ for the Observable Framework dashboard.
- `gh` authenticated for live GitHub fetches, contributor people refresh, and
  optional OBS-Q latency refresh.
- `pyyaml` for `observatory/build_people.py`.
- Optional validation dependency: `python -m pip install -r scripts/requirements-validation.txt`.

## Manual Observatory Refresh

Use this when you want a fresh GitHub/org snapshot. It uses the live GitHub API
and writes gitignored raw JSONL under `observatory/snapshots/<YYYY-MM>/`.

```powershell
cd observatory
python fetch.py --since 2014-01-01 --skip-existing
python transform.py
python build_people.py
cd ..
Copy-Item data\*.csv observatory\site\src\data\ -Force
```

Then regenerate the offline finding reports:

```powershell
python scripts/bus_factor.py
python scripts/repo_health.py
python scripts/taxonomy_adoption.py
python scripts/velocity_timeline.py
python scripts/contributor_identity.py
```

Inspect:

```powershell
git diff --stat -- data observatory/site/src/data reports
git diff -- reports/README.md reports/bus_factor.md reports/repo_health.md
```

Do not publish a refresh if the headline counts move unexpectedly and there is
no note explaining why.

## Offline Finding Refresh Only

Use this when `observatory/site/src/data/*.csv` is already current and you only
need regenerated reports or dashboard inputs:

```powershell
python scripts/refresh_observatory.py --dry-run
python scripts/refresh_observatory.py
```

The refresh runner records `reports/refresh_observatory_manifest.json` and
`reports/refresh_observatory_summary.md`. By default it refreshes read-only
GitHub metadata and workflow-health snapshots through `gh api`. Use
`--offline-metadata` or `--offline-workflows` only when credentials are
unavailable or an explicit placeholder refresh is intended.

To run only the read-only verification phases:

```powershell
python scripts/refresh_observatory.py --check-only
```

The runner currently covers the local finding reports, metadata snapshot,
workflow-health snapshot, data catalog, regression checks, visualization smoke
check, and Observable build. The manual commands below remain useful for
targeted reruns:

```powershell
python scripts/bus_factor.py
python scripts/repo_health.py
python scripts/taxonomy_adoption.py
python scripts/velocity_timeline.py
python scripts/contributor_identity.py
```

The default runner path calls GitHub for metadata and workflow snapshots. Use
`--offline-metadata --offline-workflows` when a no-network placeholder run is
intentional.

## OBS-Q Correction Sustainability

OBS-Q reads the sibling `../csl-orig` git history and cached
`observatory/site/src/data/obs_q_latency.csv`.

```powershell
python scripts/obs_q_correction.py
```

To refresh the issue-latency cache, use the live GitHub path:

```powershell
python scripts/obs_q_correction.py --fetch-latency
```

The `--fetch-latency` form requires `gh` auth and network. If it fails, keep the
existing cache and record the failure in the monthly review notes.

## OBS-T Correction-Event Pipeline

OBS-T requires sibling `../CORRECTIONS` and `../csl-orig`. Run the full pipeline
after any corpus-affecting change:

```powershell
python scripts/build_correction_events.py
python scripts/reconstruct_git_events.py
python scripts/attribute_components.py
python scripts/attribute_crosswalks.py
python scripts/obs_t_release.py
python scripts/obs_t_typology.py
python scripts/obs_t_baselines.py
python scripts/obs_t_rigor.py
python scripts/obs_t_robustness.py
python scripts/obs_t_campaigns.py
python scripts/obs_t_translit_check.py
python scripts/obs_t_silver.py
python scripts/obs_t_issuelabel.py
python scripts/obs_t_regression.py
```

Regression must pass before treating the release table as usable. It checks git
source paths, unequal diff accounting, identity redaction, schema drift, and
human-gated validation documentation.

Human-gated commands stay out of unattended automation:

```powershell
python scripts/obs_t_gold.py --make
python scripts/obs_t_gold.py --score
python scripts/obs_t_errorsample.py --make
python scripts/obs_t_errorsample.py --score
```

Run those only when MG is intentionally preparing or scoring annotation sheets.

## Dashboard Build

The dashboard is an Observable Framework app in `observatory/site`.

```powershell
cd observatory\site
npm ci
npm run build
```

For local inspection:

```powershell
npm run dev
```

The build output is `observatory/site/dist/` and is gitignored. Deploy through
GitHub Pages workflows after reviewing generated data and reports.

## GitHub Actions Paths

| Workflow | Purpose | Caveat |
|---|---|---|
| `.github/workflows/refresh-observatory.yml` | Scheduled/monthly or manual fetch, transform, report regeneration, site build, Pages deploy. | Needs sufficient token permissions to fetch org data and push refresh commits. |
| `.github/workflows/deploy.yml` | Build and deploy committed dashboard data on push/manual dispatch. | Does not fetch fresh data. |
| `.github/workflows/refresh.yml` | Legacy manual-only `pull_data.py` / `compute_metrics.py` / `render_reports.py` path. | Kept for legacy report tables; do not schedule alongside the canonical refresh. |
| `.github/workflows/tooling-audit.yml` | Weekly Tooling Roadmap audit. | Needs `TOOLING_AUDIT_TOKEN` with `read:project` and repo access. |

If automation fails because credentials are missing, update
`docs/DECISIONS_NEEDED.md` rather than weakening the workflow.

## Public Artifact Refresh Modernization

The selective Cologne refresh script is not modernized in this repository. The
planning packet is [`REFRESH_SCRIPT_MODERNIZATION_PLAN.md`](REFRESH_SCRIPT_MODERNIZATION_PLAN.md).
Use it before starting `csl-pywork#53`; do not change the Cologne cron or
push-capable refresh scripts without maintainer/server approval.

## Review After Any Refresh

Run:

```powershell
python scripts/obs_t_regression.py
python scripts/repo_health_regression.py
python scripts/repo_metadata_snapshot.py --offline --out $env:TEMP\repo_metadata_offline.csv
git diff --stat
git status --short
```

When GitHub auth is healthy, refresh the public metadata snapshot with:

```powershell
python scripts/repo_metadata_snapshot.py --out observatory/site/src/data/repo_metadata.csv
```

Check these files first:

- `reports/README.md`
- `reports/synthesis.md`
- `reports/repo_health.md`
- `reports/bus_factor.md`
- `reports/contributor_identity.md`
- `reports/obs_t_*.md`
- `observatory/site/src/data/*.csv`
- `observatory/site/src/data/*.json`
- `data/schema/correction-event.schema.json`

Update these maintainer docs when the refresh changes decisions or priorities:

- `docs/ROADMAP.md`
- `docs/OBSERVATORY_ROADMAP.md`
- `docs/DECISIONS_NEEDED.md`
- `docs/MAINTAINER_REVIEW_CHECKLIST.md`
- `docs/BUS_FACTOR_ACTION_PLAN.md`

## Common Failure Modes

| Symptom | Likely cause | Response |
|---|---|---|
| `gh auth status` fails | No GitHub auth in local shell or CI. | Authenticate locally or add the documented secret; do not bypass permission checks. |
| `transform.py` cannot find snapshots | The current month has not been fetched. | Run `python fetch.py` first or confirm the snapshot month. |
| OBS-T scripts cannot find `../csl-orig` or `../CORRECTIONS` | Sibling repos are missing or in a different parent directory. | Clone/move siblings into the expected layout or update only after documenting the alternate path. |
| `obs_t_regression.py` fails on released identities | Email-shaped value leaked into `corrector` or `corrector_name`. | Fix the source aliasing/redaction before release. |
| `obs_t_regression.py` fails on schema columns | Generated release columns and JSON schema diverged. | Update schema and release together, with the reason in the diff. |
| `npm run build` fails | Node version or site dependencies are stale. | Use Node 20+, then rerun `npm ci` in `observatory/site`. |
| Large generated diff | Snapshot changed materially or a script changed behavior. | Compare headline counts and write a note before publishing. |

## Continuity Priorities

1. Keep the offline findings reproducible from committed data.
2. Keep OBS-T regression green after corpus-affecting changes.
3. Keep the dashboard buildable with Node 20 and committed data.
4. Keep blocked external actions in `docs/DECISIONS_NEEDED.md`.
5. Keep raw snapshots and generated build artifacts out of git unless they are
   intended release data.
