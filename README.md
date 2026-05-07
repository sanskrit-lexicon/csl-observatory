# csl-observatory

Cross-repository analytics, dashboards, and data aggregator for the **Cologne Digital Sanskrit Dictionaries (CDSL)** ecosystem at [sanskrit-lexicon](https://github.com/sanskrit-lexicon).

This repository ingests metadata from every CDSL repo (issues, milestones, projects, commits, contributors, and source-file statistics), produces canonical JSON snapshots, and renders both Markdown dashboards and figures used in published reports.

## Purpose

CDSL has been under continuous collaborative development since 1997, spanning ~50 repositories and four generations of contributors. The work is highly distributed: corrections to the Petersburger Wörterbuch may propagate to Apte, Macdonell, and Monier-Williams; changes flow through `csl-orig`, build tooling in `csl-app`, and end users access them via the Cologne web portal. **Without a unified observatory, the scale and structure of the project are illegible to outside researchers and to the contributors themselves.**

This repository fills that gap. It produces:

1. **Canonical data snapshots** of the whole ecosystem (`data/snapshots/<date>/`).
2. **A live dashboard** of cross-repo metrics (`reports/dashboard.md`).
3. **Per-contributor profile pages** showing role evolution over time (`reports/contributors.md`).
4. **Figures and tables** that drive the article *The Cologne Digital Sanskrit Dictionaries: a 30-year ecosystem* (Indo-Iranian Journal, in preparation).

## Architecture

```
csl-observatory/
├── scripts/
│   ├── pull_data.py          # main aggregator — calls GitHub API + git log
│   ├── compute_metrics.py    # derives contributor / repo / cross-repo stats
│   ├── render_reports.py     # renders dashboard.md, contributors.md, etc.
│   └── contributors_map.json # login → real name + ORCID + role (manual)
├── data/
│   ├── repos.json            # all org repos, with metadata
│   ├── issues.json           # all issues across all repos, normalised
│   ├── commits.json          # commit history (sha, author, date, +/-)
│   ├── contributors.json     # per-person derived metrics
│   ├── headwords.json        # entry counts per dictionary
│   └── snapshots/<YYYY-MM-DD>/  # time-stamped immutable copies
├── reports/
│   ├── dashboard.md          # cross-repo headline metrics
│   ├── contributors.md       # one section per contributor
│   ├── timeline.md           # activity Gantt + milestone timeline
│   └── coverage.md           # entry counts, scan coverage, markup ratios
├── article/
│   ├── article.md            # Pandoc Markdown source
│   ├── refs.bib              # BibTeX references
│   └── figures/              # PNG/SVG generated from data
└── .github/workflows/
    └── refresh.yml           # weekly cron — refreshes data + commits if changed
```

## Refresh cycle

```sh
python scripts/pull_data.py        # rebuilds data/*.json
python scripts/compute_metrics.py  # derives contributors.json, summary tables
python scripts/render_reports.py   # rewrites reports/*.md
git add data reports article/figures
git commit -m "data: snapshot $(date +%Y-%m-%d)"
```

The same chain runs weekly via `.github/workflows/refresh.yml`.

## Data licensing

This repository is licensed **GPL-3.0** (tooling code).
The aggregated data in `data/` is derived from public CDSL repositories and is released under **CC BY-SA 4.0**, matching the source data.
The article in `article/` is licensed **CC BY 4.0**.

## Citation

See [`CITATION.cff`](CITATION.cff). Once the article is published, cite as:

> Gasūns, M., Funderburk, J., Patel, D., Rao, N. (forthcoming). The Cologne Digital Sanskrit Dictionaries: a 30-year ecosystem. *Indo-Iranian Journal*.

## Methodological note

All figures and counts are reproducible from the data snapshots in `data/snapshots/`. A reader who clones this repository and runs `python scripts/render_reports.py --snapshot <date>` will reproduce every figure in the dashboard and the article. This satisfies FAIR principles F1–F4 (findable), A1 (accessible), I1 (interoperable JSON), and R1.1 (license).
