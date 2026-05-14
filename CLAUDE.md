# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Purpose

`csl-observatory` is a cross-repository analytics dashboard for the Cologne Digital Sanskrit Dictionaries (CDSL) — a 50+ repo ecosystem on GitHub. It produces canonical JSON snapshots, Markdown dashboards, contributor profiles, and figures for a scholarly article.

## Pipeline

Three Python scripts form the full refresh cycle, run in order:

```sh
python scripts/pull_data.py          # fetch from GitHub API + git log → data/*.json
python scripts/compute_metrics.py    # derive metrics → data/contributors.json, repo_metrics.json, etc.
python scripts/render_reports.py     # render Markdown → reports/dashboard.md, contributors.md, etc.
```

Run a single utility independently:

```sh
python scripts/count_headwords.py    # count <L> entries in csl-orig → data/headwords.json
python scripts/propagate_templates.py [--dry-run] [REPO ...]  # push community files to dictionary repos
```

The full pipeline also runs weekly via GitHub Actions (`.github/workflows/refresh.yml`, Mondays 06:00 UTC).

## Dependencies

No third-party Python packages — standard library only (json, pathlib, subprocess, argparse, datetime). Requires:
- Python 3.11+
- `gh` CLI (authenticated, with read access to the `sanskrit-lexicon` org)
- `pandoc` (only if generating PDF from article source)

All scripts need `sys.stdout.reconfigure(encoding='utf-8')` (already present) — critical on Windows.

## Data Architecture

```
data/
  repos.json          ← raw repo metadata (stars, forks, topics, language)
  issues.json         ← all issues with labels, milestone, state
  commits.json        ← commit log with author + date (via git log over clones)
  summary.json        ← aggregate headline stats
  contributors.json   ← merged contributor profiles (alias-resolved)
  repo_metrics.json   ← per-repo issue counts, commit activity, coverage
  timeline.json       ← monthly activity time series
  cross_repo.json     ← cross-cutting aggregates
  headwords.json      ← entry counts per dictionary
  snapshots/          ← immutable YYYY-MM-DD copies of all JSON files
```

`scripts/contributors_map.json` is the hand-maintained login → real name / ORCID / alias mapping. Edit this when GitHub logins need merging into a single canonical identity.

## Article

`article/` contains two companion documents targeting Indo-Iranian Journal (Brill):
- `00-report-narrative.md` — first-person 30-year scholarly history
- `01-empirical-companion.md` — formal third-person quantitative survey with runbook and standards alignment
- `refs.bib` — shared BibTeX bibliography

## Runbook

`runbook/cologne-issue-runbook.md` documents the 16-phase procedure for applying the issue taxonomy to a dictionary repo. It is also installed as a Claude Code custom command:

```
/cologne-issue-runbook <REPONAME>
```

See the org-level CLAUDE.md (parent directory) for the full taxonomy reference.

## Session State

Check `.ai_state.md` and `STATUS.md` at the start of any session to orient on current work. Update `.ai_state.md` at micro-milestones per the org-level session state protocol.
