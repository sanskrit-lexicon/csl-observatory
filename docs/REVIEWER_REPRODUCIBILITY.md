# Reviewer Reproducibility

Date: 2026-06-13
Status: public reviewer guide for roadmap PR3 / E3.

This guide explains how to reproduce the csl-observatory reports and dashboard
from the checked-out repository, which commands require live GitHub access, and
which OBS-T validation steps are intentionally human-gated.

## Scope

This repository measures GitHub/org maintenance evidence: repositories, issues,
pull requests, commits, contributors, workflows, releases, repository metadata,
and the OBS-T correction-event release.

Out of scope for this reproducibility guide: dictionary microstructure research,
TEI/OntoLex export work, DCS/corpus work, lookup analytics, and broad
publication planning.

## Required Local Layout

For the full OBS-T checks, the local workspace should have sibling repositories:

```text
GitHub/
  csl-observatory/
  csl-orig/
  CORRECTIONS/
```

Check the workspace:

```powershell
python scripts/check_workspace.py
```

The observatory-only dashboard and many repository reports can still be checked
without rebuilding OBS-T, but OBS-T regeneration and regression checks expect
`../csl-orig` and `../CORRECTIONS`.

## Install And Build

Python scripts use the repository checkout and standard library unless a script
documents otherwise. The dashboard is an Observable Framework app:

```powershell
cd observatory\site
npm ci
npm run build
```

Return to the repository root before running the Python commands below.

## Read-Only Verification

Use this when reviewing an existing snapshot without rewriting generated data:

```powershell
python scripts/refresh_observatory.py --check-only
python scripts/obs_t_regression.py
python scripts/workflow_health.py --check
python scripts/data_index.py --check
python scripts/repo_health_regression.py
```

Expected result: each command exits 0. The refresh runner writes a JSON manifest
and Markdown summary unless custom temp output paths are provided.

## Full Local Refresh

Use this when intentionally refreshing generated reports and dashboard data:

```powershell
python scripts/refresh_observatory.py --dry-run
python scripts/refresh_observatory.py
```

The default refresh reads live GitHub repository metadata and workflow metadata
through `gh api`. If GitHub auth is unavailable and a placeholder refresh is
intentional, use:

```powershell
python scripts/refresh_observatory.py --offline-metadata --offline-workflows
```

Do not cite an offline placeholder metadata/workflow refresh as complete live
coverage. Review `repo_metadata.csv`, `workflow_health.csv`, and the generated
manifest before publishing.

## OBS-T Release Checks

OBS-T regeneration requires `../CORRECTIONS` and `../csl-orig`:

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

`obs_t_regression.py` is the release safety gate. It checks git source paths,
unequal hunk accounting, identity redaction, schema drift, and documentation of
human-gated validation commands.

## Human-Gated Commands

These commands create or score annotation sheets and must not run in unattended
automation:

```powershell
python scripts/obs_t_gold.py --make
python scripts/obs_t_gold.py --score
python scripts/obs_t_errorsample.py --make
python scripts/obs_t_errorsample.py --score
```

Run them only when MG intentionally starts or scores a human annotation pass.

## Public Data And Citation

Use the dashboard Data page or `observatory/site/src/data/data_index.csv` to
identify the exact public CSV/JSON file, generated date, source script, and
caveat.

For citation, include:

- repository: `sanskrit-lexicon/csl-observatory`
- file name and generated date from `data_index.csv`
- git commit or tagged release (frozen: `obs-t-data-v1.0.0`)
- DOI: [10.5281/zenodo.15834721](https://doi.org/10.5281/zenodo.15834721)

The Zenodo DOI is [10.5281/zenodo.15834721](https://doi.org/10.5281/zenodo.15834721) (concept DOI, CC-BY-4.0).

## Review Checklist

Before treating a snapshot as reviewer-ready:

```powershell
python scripts/check_workspace.py
python scripts/refresh_observatory.py --check-only
python scripts/obs_t_regression.py
cd observatory\site
npm run build
```

Then inspect:

- `reports/README.md`
- `reports/workflow_health.md`
- `reports/repo_health.md`
- `reports/bus_factor.md`
- `reports/contributor_identity.md`
- `reports/obs_t_*.md`
- `observatory/site/src/data/data_index.csv`
- `docs/DATASHEET.md`
- `docs/DECISIONS_NEEDED.md`

Known human/org blockers, such as license rollout or repository archiving, stay
in `docs/DECISIONS_NEEDED.md` until MG or the organization resolves them.
