# Changelog

All notable changes to this repository are documented here, following [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Initial repository scaffold: `scripts/`, `data/`, `reports/`, `article/`, `.github/workflows/`.
- `pull_data.py` — fetches issues, commits, contributors from every sanskrit-lexicon repo via REST + GraphQL.
- `compute_metrics.py` — derives per-contributor activity, role span, repo-touched counts.
- `render_reports.py` — renders Markdown dashboards from snapshots.
- `contributors_map.json` — maps GitHub login → real name → ORCID (placeholders) → role.
- `CITATION.cff` (FORCE11 software citation), `LICENSE` (GPL-3.0), `CHANGELOG.md`, `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`.
- Weekly GitHub Actions refresh workflow.
