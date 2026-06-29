# Workflow Health

Read-only workflow/release reliability baseline for the `sanskrit-lexicon` organization.

## Summary

- Active repositories: 76
- Active repos with workflows: 28/76 (36.8%)
- Active repos with scheduled workflows: 11/76 (14.5%)
- Active repos with artifact/deploy/refresh workflows: 13/76 (17.1%)
- Active repos with Dependabot config: 18/76 (23.7%)
- Active repos with CodeQL signal: 8/76 (10.5%)
- Active repos with releases: 1/76 (1.3%)
- Rows with fetch warnings: 0

## Lowest-Score Active Queue

| Repo | Score | Workflows | Scheduled | Artifact/refresh | Dependabot | CodeQL | Releases | Flags |
|---|---:|---:|---:|---:|---|---|---:|---|
| ACC | 0 | 0 | 0 | 0 | no | no | 0 | no-workflows|no-scheduled-workflows|no-artifact-refresh-workflow|missing-dependabot|missing-codeql|no-releases |
| AMAR | 0 | 0 | 0 | 0 | no | no | 0 | no-workflows|no-scheduled-workflows|no-artifact-refresh-workflow|missing-dependabot|missing-codeql|no-releases |
| ArabicInSanskrit | 0 | 0 | 0 | 0 | no | no | 0 | no-workflows|no-scheduled-workflows|no-artifact-refresh-workflow|missing-dependabot|missing-codeql|no-releases |
| BEN | 0 | 0 | 0 | 0 | no | no | 0 | no-workflows|no-scheduled-workflows|no-artifact-refresh-workflow|missing-dependabot|missing-codeql|no-releases |
| BHS | 0 | 0 | 0 | 0 | no | no | 0 | no-workflows|no-scheduled-workflows|no-artifact-refresh-workflow|missing-dependabot|missing-codeql|no-releases |
| BOP | 0 | 0 | 0 | 0 | no | no | 0 | no-workflows|no-scheduled-workflows|no-artifact-refresh-workflow|missing-dependabot|missing-codeql|no-releases |
| BOR | 0 | 0 | 0 | 0 | no | no | 0 | no-workflows|no-scheduled-workflows|no-artifact-refresh-workflow|missing-dependabot|missing-codeql|no-releases |
| BUR | 0 | 0 | 0 | 0 | no | no | 0 | no-workflows|no-scheduled-workflows|no-artifact-refresh-workflow|missing-dependabot|missing-codeql|no-releases |
| CAE | 0 | 0 | 0 | 0 | no | no | 0 | no-workflows|no-scheduled-workflows|no-artifact-refresh-workflow|missing-dependabot|missing-codeql|no-releases |
| CCS | 0 | 0 | 0 | 0 | no | no | 0 | no-workflows|no-scheduled-workflows|no-artifact-refresh-workflow|missing-dependabot|missing-codeql|no-releases |
| CORRECTIONS | 0 | 0 | 0 | 0 | no | no | 0 | no-workflows|no-scheduled-workflows|no-artifact-refresh-workflow|missing-dependabot|missing-codeql|no-releases |
| GreekInSanskrit | 0 | 0 | 0 | 0 | no | no | 0 | no-workflows|no-scheduled-workflows|no-artifact-refresh-workflow|missing-dependabot|missing-codeql|no-releases |
| INM | 0 | 0 | 0 | 0 | no | no | 0 | no-workflows|no-scheduled-workflows|no-artifact-refresh-workflow|missing-dependabot|missing-codeql|no-releases |
| KNA | 0 | 0 | 0 | 0 | no | no | 0 | no-workflows|no-scheduled-workflows|no-artifact-refresh-workflow|missing-dependabot|missing-codeql|no-releases |
| KOW | 0 | 0 | 0 | 0 | no | no | 0 | no-workflows|no-scheduled-workflows|no-artifact-refresh-workflow|missing-dependabot|missing-codeql|no-releases |

## Caveats

- This report does not mutate any repository.
- `artifact_refresh_workflow_count` is keyword-based and should be treated as a queueing signal.
- Scheduled workflow detection scans workflow YAML content for cron entries.
- Dependabot, CodeQL, and release fields come from `repo_metadata.csv`.
- Rows with fetch warnings are retained with explicit warning text rather than failing the whole run.

Generated data: `observatory/site/src/data/workflow_health.csv`.
