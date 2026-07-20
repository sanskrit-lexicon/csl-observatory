---
title: Reproducibility
toc: true
---

# Reproducibility

This page gives reviewers the command path for checking the observatory snapshot,
understanding live-data dependencies, and avoiding human-gated OBS-T annotation
steps during unattended reproduction.

## Local Layout

Full OBS-T checks expect this sibling layout:

```text
GitHub/
  csl-observatory/
  csl-orig/
  CORRECTIONS/
```

Check it first:

```powershell
python scripts/check_workspace.py
```

## Read-Only Check

Use this path to verify an existing snapshot without intentionally refreshing
generated data:

```powershell
python scripts/refresh_observatory.py --check-only
python scripts/obs_t_regression.py
python scripts/workflow_health.py --check
python scripts/data_index.py --check
python scripts/repo_health_regression.py
```

## Full Refresh

Use this path when refreshing generated reports and dashboard data:

```powershell
python scripts/refresh_observatory.py --dry-run
python scripts/refresh_observatory.py
```

The default refresh reads live GitHub metadata and workflow metadata through
`gh api`. If credentials are unavailable and placeholders are intentional:

```powershell
python scripts/refresh_observatory.py --offline-metadata --offline-workflows
```

Offline metadata/workflow placeholders are useful for schema checks, but should
not be cited as complete live coverage.

## Dashboard Build

```powershell
cd observatory\site
npm ci
npm run build
```

## OBS-T Pipeline

The citable OBS-T release is guarded by:

```powershell
python scripts/obs_t_regression.py
```

The full regeneration path is:

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

## Human-Gated

Do not run these in unattended automation:

```powershell
python scripts/obs_t_gold.py --make
python scripts/obs_t_gold.py --score
python scripts/obs_t_errorsample.py --make
python scripts/obs_t_errorsample.py --score
```

They create or score annotation sheets and require an intentional human review
workflow.

## Data And Citation

Use [Data Downloads](/data) or `observatory/site/src/data/data_index.csv` to
identify the exact public CSV/JSON file, generated date, source script, and
caveat. Cite the repository commit or frozen tag together with the file and
generated date. No Zenodo DOI minted yet — see [Data Downloads](/data).

The longer repository guide is
[`docs/REVIEWER_REPRODUCIBILITY.md`](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/docs/REVIEWER_REPRODUCIBILITY.md).
