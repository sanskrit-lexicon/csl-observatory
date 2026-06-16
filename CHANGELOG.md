# Changelog

All notable changes to this repository are documented here, following [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Fixed
- Front-door number drift: the landing dashboard now filters bots from the
  contributor count, reports 76 repos / 13 years consistently, and reads its
  row-count table and snapshot date from `data/manifest.json` (no hand-typed
  numbers). The "last refreshed" stamp shows the data snapshot date, not the
  render date.
- OBS-T paper and datasheet: corrected the form-layer link rate (12.9% → 28.8%,
  the post-Phase-8 value computed from the released corpus).

## [0.1.0] - 2026-06-16

First tagged snapshot of the observatory: a reproducible measurement of the
sanskrit-lexicon organisation plus the OBS-T error-typology language resource.

### Added
- **Data pipeline** — `observatory/fetch.py` → `transform.py` → `build_people.py`
  fetch GitHub repo/issue/PR/commit/contributor data into versioned snapshots
  and time-series CSVs; legacy `scripts/pull_data.py` (+ `retry_via_clone.py`
  bare-clone fallback) and `compute_metrics.py` retained.
- **Five org-process findings** (offline, script → report → site page):
  contributor concentration / bus factor, repository health, issue-taxonomy
  adoption, velocity & health timeline, and a contributor-identity worksheet —
  plus [`reports/synthesis.md`](reports/synthesis.md).
- **OBS-T error-typology track** — a 50,953-event correction corpus (form
  archive + `csl-orig` git history) with a two-axis typology (location ×
  edit-type), reference baselines, a Gebru-style [`docs/DATASHEET.md`](docs/DATASHEET.md),
  a JSON schema, and a draft paper ([`paper-obs-t-error-typology.md`](paper-obs-t-error-typology.md)).
- **Observable Framework dashboard** (`observatory/site/`) deployed to GitHub
  Pages, with monthly auto-refresh (`.github/workflows/refresh-observatory.yml`).
- **Org tooling** — issue-taxonomy runbooks, community-file templates, and
  cross-repo decision tracking (`docs/DECISIONS_NEEDED.md`).
- **Repository metadata** — `CITATION.cff`, `LICENSE` (GPL-3.0), `CONTRIBUTING.md`,
  `CODE_OF_CONDUCT.md`, issue/PR templates, Dependabot, and CodeQL.

### Notes
- The 2026-06-04 boundary cleanup narrowed this repo to GitHub/org observability;
  dictionary-content research moved to `csl-atlas` (see `docs/BOUNDARY_RULES.md`).
- Citation DOI is pending a Zenodo mint; contributor ORCIDs are not yet registered.

[Unreleased]: https://github.com/sanskrit-lexicon/csl-observatory/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/sanskrit-lexicon/csl-observatory/releases/tag/v0.1.0
