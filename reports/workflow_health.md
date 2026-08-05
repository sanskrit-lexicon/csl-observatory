# Workflow Health

Read-only workflow/release reliability baseline for the `sanskrit-lexicon` organization.

## Summary

- Active repositories: 73
- Active repos with workflows: 71/73 (97.3%)
- Active repos with scheduled workflows: 10/73 (13.7%)
- Active repos with artifact/deploy/refresh workflows: 51/73 (69.9%)
- Active repos with Dependabot config: 69/73 (94.5%)
- Active repos with CodeQL signal: 6/73 (8.2%)
- Active repos with releases: 5/73 (6.8%)
- Rows with fetch warnings: 44

## Lowest-Score Active Queue

| Repo | Score | Workflows | Scheduled | Artifact/refresh | Dependabot | CodeQL | Releases | Flags |
|---|---:|---:|---:|---:|---|---|---:|---|
| COLOGNE | 0 | unknown | unknown | unknown | unknown | unknown | unknown | workflows-unknown|active-workflows-unknown|scheduled-workflows-unknown|artifact-refresh-workflow-unknown|dependabot-unknown|codeql-unknown|releases-unknown |
| literarysource | 0 | unknown | unknown | unknown | unknown | unknown | unknown | workflows-unknown|active-workflows-unknown|scheduled-workflows-unknown|artifact-refresh-workflow-unknown|dependabot-unknown|codeql-unknown|releases-unknown |
| AMAR | 3 | 2 | unknown | unknown | yes | no | 0 | active-workflows-unknown|scheduled-workflows-unknown|artifact-refresh-workflow-unknown|missing-codeql|no-releases |
| BHS | 3 | 1 | unknown | unknown | yes | no | 0 | active-workflows-unknown|scheduled-workflows-unknown|artifact-refresh-workflow-unknown|missing-codeql|no-releases |
| FRI | 3 | 2 | unknown | unknown | yes | no | unknown | active-workflows-unknown|scheduled-workflows-unknown|artifact-refresh-workflow-unknown|missing-codeql|releases-unknown |
| KNA | 3 | 2 | unknown | unknown | yes | no | 0 | active-workflows-unknown|scheduled-workflows-unknown|artifact-refresh-workflow-unknown|missing-codeql|no-releases |
| KOW | 3 | 1 | unknown | unknown | yes | no | unknown | active-workflows-unknown|scheduled-workflows-unknown|artifact-refresh-workflow-unknown|missing-codeql|releases-unknown |
| LRV | 3 | 1 | unknown | unknown | yes | no | unknown | active-workflows-unknown|scheduled-workflows-unknown|artifact-refresh-workflow-unknown|missing-codeql|releases-unknown |
| MW72 | 3 | 1 | unknown | unknown | yes | no | unknown | active-workflows-unknown|scheduled-workflows-unknown|artifact-refresh-workflow-unknown|missing-codeql|releases-unknown |
| avlinks | 3 | 1 | unknown | unknown | yes | no | 0 | active-workflows-unknown|scheduled-workflows-unknown|artifact-refresh-workflow-unknown|missing-codeql|no-releases |
| csl-app | 3 | 4 | unknown | unknown | yes | no | 0 | active-workflows-unknown|scheduled-workflows-unknown|artifact-refresh-workflow-unknown|missing-codeql|no-releases |
| hwnorm2 | 3 | 1 | unknown | unknown | yes | no | 0 | active-workflows-unknown|scheduled-workflows-unknown|artifact-refresh-workflow-unknown|missing-codeql|no-releases |
| ArabicInSanskrit | 4 | 2 | 0 | 0 | yes | no | 0 | no-scheduled-workflows|no-artifact-refresh-workflow|missing-codeql|no-releases |
| CORRECTIONS | 4 | 2 | 0 | 0 | yes | no | unknown | no-scheduled-workflows|no-artifact-refresh-workflow|missing-codeql|releases-unknown |
| alternateheadwords | 4 | 2 | 0 | 0 | yes | no | 0 | no-scheduled-workflows|no-artifact-refresh-workflow|missing-codeql|no-releases |

## Caveats

- This report does not mutate any repository.
- `artifact_refresh_workflow_count` is keyword-based and should be treated as a queueing signal.
- Scheduled workflow detection scans workflow YAML content for cron entries.
- Dependabot, CodeQL, and release fields come from `repo_metadata.csv`.
- Rows with fetch warnings are retained with explicit warning text rather than failing the whole run.

Generated data: `observatory/site/src/data/workflow_health.csv`.
