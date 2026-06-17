# Metadata Completeness Dashboard Plan

Date: 2026-06-13
Status: B3 dashboard, cached live fetcher, and complete live metadata snapshot
are implemented.

This plan defines the repository metadata dashboard promised by
`docs/OBSERVATORY_ROADMAP.md` B3. It is read-only and does not authorize
repository edits. It records the exact data needed before the dashboard can
truthfully show README, description, citation, template, workflow, release, and
branch coverage.

## Current Constraint

`repos.csv` already supports:

- description present or missing;
- default branch;
- archived state;
- license string and license class through `repo_health.csv`;
- open issues, stars, forks, primary language, size, and push dates.

It did not previously include README, citation, issue template, PR template,
workflow, release, Dependabot, or CodeQL coverage. On 2026-06-13, local
`gh auth status` and `gh api` succeeded as account `gasyoun`, and the live
snapshot filled all live-only fields.

## Target Snapshot

New generated file:

```text
observatory/site/src/data/repo_metadata.csv
```

The tracked CSV is currently a complete live snapshot. Existing
repository-health fields are populated, and live-only fields use real
yes/no/count values.

2026-06-13 live run summary:

- Rows: 76.
- Rows with fetch warnings: 0.
- Unknown live fields: 0.
- Confirmed live positives include 75 README, 62 citation, 24 issue-template,
  25 PR-template, 23 workflow, 18 Dependabot, 8 CodeQL rows, and 1 repository
  with at least one GitHub release.

Proposed columns:

| Column | Meaning |
|---|---|
| `repo` | Repository name from `repos.csv`. |
| `archived` | Existing archive state from `repos.csv`. |
| `default_branch` | Existing default branch from `repos.csv`. |
| `license_class` | `none`, `unrecognised`, or `recognised` from `repo_health.csv`. |
| `license` | Existing license string. |
| `has_description` | Existing description coverage from `repo_health.csv`. |
| `has_readme` | Any root README recognized by GitHub or by filename check. |
| `has_citation` | Root `CITATION.cff` or `citation.cff`. |
| `has_issue_template` | `.github/ISSUE_TEMPLATE/*`, `ISSUE_TEMPLATE.md`, or organization-inherited template if detectable. |
| `has_pr_template` | `.github/PULL_REQUEST_TEMPLATE.md`, `PULL_REQUEST_TEMPLATE.md`, or organization-inherited template if detectable. |
| `workflow_count` | Count of `.github/workflows/*.yml` and `.yaml`. |
| `has_workflows` | `yes` when `workflow_count > 0`. |
| `has_dependabot` | `.github/dependabot.yml` or `.yaml`. |
| `has_codeql` | Workflow or config signal for CodeQL. |
| `release_count` | GitHub release count, not tag count. |
| `latest_release` | Latest release tag/name if present. |
| `metadata_score` | Count of present core metadata checks. |
| `metadata_flags` | Pipe-separated missing or risky fields. |
| `fetched_at` | UTC timestamp for the snapshot. |
| `fetch_warning` | Empty unless API access, rate limit, or repo-specific lookup failed. |

## Fetch Strategy

Snapshot script:

```powershell
python scripts/repo_metadata_snapshot.py --out observatory/site/src/data/repo_metadata.csv
```

Offline schema check:

```powershell
python scripts/repo_metadata_snapshot.py --offline --out $env:TEMP\repo_metadata_offline.csv
```

Implementation notes:

- `scripts/repo_metadata_snapshot.py` already reads the repo list from
  `observatory/site/src/data/repos.csv`.
- Prefer `gh api` when authenticated, because it respects local GitHub auth and
  can see org-inherited metadata if permissions allow.
- Live responses are cached under
  `observatory/snapshots/<YYYY-MM>/repo_metadata/`, which is already gitignored.
- Provide `--repo <name>` for focused debug runs.
- Provide `--offline` to validate schema and merge existing `repos.csv` /
  `repo_health.csv` fields without calling GitHub.
- Cache raw API responses under a gitignored snapshot directory if live fetches
  become expensive.
- Treat API errors as row-level `fetch_warning` values; if they reappear, keep
  B3 regression visible instead of counting `unknown` values as missing fields.
- Never write to the target repositories.

## Dashboard Design

The dashboard lives at `observatory/site/src/repo-metadata.md` and is linked as
Repo Metadata in the Observable navigation.

Required sections:

| Section | Purpose |
|---|---|
| Metadata headline cards | Counts for missing descriptions, missing README, missing citation, missing issue template, missing PR template, no workflows, no releases. |
| Repository queue | Table sorted by `metadata_flags` count, with repo links and flags. |
| Documentation coverage | README, citation, license, description, issue template, and PR template coverage. |
| Automation coverage | Workflow, Dependabot, CodeQL, and release coverage. |
| Blockers | Rows where fetch failed or inherited org-level template status is uncertain. |
| Maintainer actions | Separate safe local/docs follow-ups from external repo changes requiring approval. |

## Acceptance For B3

B3 is complete when all are true:

- `repo_metadata.csv` exists and has the schema above or a documented successor
  schema.
- `scripts/repo_metadata_snapshot.py` regenerates the file from committed
  snapshots plus live GitHub metadata, with clear rate-limit/auth behavior.
- The dashboard shows README, description, citation, issue template, PR
  template, workflow, release, and branch state.
- Missing fields are visible as queues, not prose-only claims.
- Placeholder `unknown` live fields are not present in the current live
  snapshot; if they reappear, they should be shown as blockers rather than
  missing failures.
- External repo changes remain blocked until maintainer approval.
- Monthly review checklist includes the regeneration command and failure mode.

## Open Dependencies

| Dependency | Needed for | Status |
|---|---|---|
| Durable GitHub CLI auth or CI token | Keep future live repository metadata fetches reproducible outside an interactive local session. | local `gh auth status` and `gh api` worked on 2026-06-13; CI/secret setup remains future automation work |
| Decision on org-inherited templates | Distinguish repo-local gaps from org-level coverage when interpreting dashboard results. | needs maintainer confirmation |
| Scope for archived repos | Decide whether archived repos need README/citation/template coverage. | recommend report separately, do not force active-repo standards |

B3 no longer depends on unresolved `unknown` live fields, but future refresh
automation should still avoid relying on a single interactive local credential.
