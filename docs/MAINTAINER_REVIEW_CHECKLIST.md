# Monthly Maintainer Review Checklist

Date created: 2026-06-12
Status: active operating checklist for roadmap item SC6.

Use this checklist once per month, preferably on the last Friday of the month.
Expected output: updated roadmap statuses, updated `docs/DECISIONS_NEEDED.md`,
and a short list of next actions.

This checklist is for review and decision-making. It does not authorize external
repo changes, archiving, branch renames, or license commits.

## Cadence

| When | Action |
|---|---|
| Last Friday of each month | Run the review, update statuses, capture decisions. |
| First working session after review | Implement only the approved next actions. |
| Quarterly | Reassess roadmap targets and archive completed implementation plans. |

## Before The Review

Use the refresh runner as the first local entry point. It writes a manifest and
summary so the review has a durable record of what ran.

```powershell
python scripts/refresh_observatory.py --dry-run
python scripts/refresh_observatory.py --check-only
# When GitHub auth is unavailable and placeholders are intentional:
# python scripts/refresh_observatory.py --offline-metadata --offline-workflows
```

Run or inspect the individual commands below only when you need a targeted
rerun or are ready to review generated diffs. Several commands rewrite
generated reports and CSV/JSON files.

```powershell
python scripts/repo_health.py
python scripts/bus_factor.py
python scripts/contributor_identity.py
python scripts/taxonomy_adoption.py
python scripts/velocity_timeline.py
python scripts/obs_t_regression.py
python scripts/workflow_health.py --check
python scripts/data_index.py --check
python scripts/repo_health_regression.py
python scripts/repo_metadata_snapshot.py --offline --out $env:TEMP\repo_metadata_offline.csv
# When GitHub auth is healthy:
# python scripts/repo_metadata_snapshot.py --out observatory/site/src/data/repo_metadata.csv
```

For the Tooling Roadmap project audit, use the same repo list as
`.github/workflows/tooling-audit.yml`:

```bash
python scripts/tooling_runbook.py audit "csl-observatory,MWinflect,alternateheadwords,hwnorm1,csl-devanagari,mw-dev,csl-inflect,csl-ldev,csl-pywork,csl-homepage,hwnorm2,csl-app,literarysource,csl-doc,csl-newsletter,csl-westergaard,csl-kale,csl-lnum,csl-lslink,csl-sqlite,avlinks,rvlinks,csl-whitroot,csl-json,csl-atlas,csl-santam,sanskrit-fonts,cologne-hugo,sanskrit-lexicon.github.io,csl-orig,csl-apidev,csl-websanlexicon,csl-corrections,cologne-stardict"
```

If the audit needs live GitHub project access, confirm `TOOLING_AUDIT_TOKEN` is
available with `read:project` and `repo` scopes.

## Review Sections

### 1. Repository Health

Inspect:

- `reports/repo_health.md`
- `observatory/site/src/data/repo_health.csv`
- `docs/REPOSITORY_HEALTH_DECISION_PACKET.md`
- `docs/METADATA_COMPLETENESS_DASHBOARD_PLAN.md`

Questions:

- Did the no-license count change from 41?
- Did the `NOASSERTION` count change from 21?
- Did the six cleanup candidates change?
- Are any new repos missing descriptions, licenses, or expected metadata?
- Is GitHub CLI/token access healthy enough to generate `repo_metadata.csv`?

Expected update:

- Update RH1/RH2/RH3/RH7 statuses in `docs/ROADMAP.md`.
- Add new maintainer decisions to `docs/DECISIONS_NEEDED.md`.

### 2. License Backlog

Inspect:

- `docs/REPOSITORY_HEALTH_DECISION_PACKET.md`
- `docs/hygiene_issues_draft.md`
- `reports/repo_health.md`

Questions:

- Has the code/tooling default license been approved?
- Has the dictionary-data license been approved?
- Which repo groups are safe to batch first?
- Which repos need human review because they are mixed code/data or infrastructure?

Expected update:

- Keep unapproved license changes marked blocked.
- If approved, create a batch plan before touching any external repo.

### 3. Cleanup Candidates

Inspect:

- `reports/repo_health.md`
- `docs/REPOSITORY_HEALTH_DECISION_PACKET.md`

Questions:

- Has `santamlegacy` been confirmed unused?
- Have the temporary correction repos been confirmed merged or superseded?
- Were the open issues in `temp_corrections_ap90` and `temp_corrections_mw`
  migrated, closed, or intentionally retained?
- Is `test_cologne_push` still needed for server push testing?

Expected update:

- Keep each candidate as blocked until maintainer confirmation.
- After approval, archive only through GitHub and then rerun `repo_health.py`.

### 4. Contributor And ORCID Status

Inspect:

- `reports/contributor_identity.md`
- `reports/bus_factor.md`
- `scripts/contributors_map.json`

Questions:

- Did any confirmed contributor provide an ORCID?
- Did any unknown identity become identifiable?
- Did the bus-factor concentration change?
- Is any personal identity data sensitive or not consented for public reporting?

Expected update:

- Update SC1/SC3 in `docs/ROADMAP.md`.
- Keep identity changes conservative and consent-aware.

### 5. Project Board And Taxonomy Drift

Inspect:

- `reports/taxonomy_adoption.md`
- `docs/RUNBOOK_NOTES.md`
- Tooling Roadmap audit output

Questions:

- Did project-board item counts match open issue counts?
- Did over-typed issues drop below 324?
- Did stray labels drop below 999?
- Are new repos missing setup/classify/verify/project/refresh runbook phases?

Expected update:

- Update RH6 in `docs/ROADMAP.md`.
- Add blockers to `docs/DECISIONS_NEEDED.md` if token or project access is missing.

### 6. Generated Reports And Regression Checks

Inspect:

- `reports/README.md`
- `reports/synthesis.md`
- `reports/velocity_timeline.md`
- `reports/obs_t_*.md`
- `docs/REFRESH_SCRIPT_MODERNIZATION_PLAN.md`
- `docs/REVIEWER_REPRODUCIBILITY.md`

Questions:

- Did generated reports change only because inputs changed?
- Did `scripts/repo_health_regression.py` pass?
- Did `scripts/obs_t_regression.py` pass?
- Are generated CSV/JSON changes explainable in the next commit or release notes?
- Does `scripts/data_index.py --check` still cover every public CSV/JSON file?
- Are any human-gated commands still documented as human-gated?
- Does the reviewer reproducibility page still name the current refresh,
  dashboard-build, OBS-T regression, and human-gated commands?
- Has any `redo_xampp_selective.sh` modernization work stayed within the
  approved plan and avoided unauthorized server/external repo changes?

Expected update:

- Update AR5 and OT1 statuses in `docs/ROADMAP.md`.
- Do not run `obs_t_gold.py --make/--score` or `obs_t_errorsample.py --make/--score`
  unless the maintainer intentionally starts that annotation workflow.

## Closeout Template

At the end of each monthly review, record:

```text
Review date:
Reports refreshed:
Decisions made:
Blocked decisions:
External repo changes approved:
Roadmap statuses changed:
Next implementation session:
```

Default next action when no new decision is made: continue with the highest
priority unblocked repository-health item in `docs/ROADMAP.md`.
