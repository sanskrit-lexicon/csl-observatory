# Changelog

All notable changes to this repository are documented here, following [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- **H817 WS1.2 — 3 new statistics census artifacts**: `scripts/pos_distribution_per_text.py`
  (UD-POS frequency per DCS text, all 270 texts) + `reports/pos_distribution_per_text.md`;
  `scripts/paradigm_cell_coverage.py` (attested finite verb cells per root, 8,054/11,096
  lemmas, 171 distinct cells) + `reports/paradigm_cell_coverage.md`; and
  `data/sense_polysemy_per_dict.tsv` + `reports/sense_polysemy_per_dict.md` (mirrors the
  csl-atlas A02 paper's per-dict senses/entry table for the 11/44 dicts where a
  sense-marking convention exists; the `<L>` decimal-suffix shortcut for the other 33 was
  tried and confirmed invalid — recorded so it isn't re-attempted). Closes 3 of 5
  descriptive rows in `ROADMAP_STATISTICS_ORG_CENSUS_2026_2027.md` Part 0; registered as
  FEATURES_INDEX E44/E45/E46.
- **Statistics census dashboard skeleton (H817 WS1.3)** — 6 new Observable
  pages (`census-overview`, `census-l1-lexicon` … `census-l5-roots`) seeding
  the org-wide [statistics census roadmap](https://github.com/gasyoun/SanskritLexicography/blob/master/ROADMAP_STATISTICS_ORG_CENSUS_2026_2027.md)'s
  Part-0 register (~60 headline statistics across 7 data layers, done/partial/
  not-started status) with a house trust block, log-scale magnitude charts,
  status breakdown, filterable full-register table, and CSV download. New
  feed: `observatory/site/src/data/stats_census_register.csv`.

## [1.1.1] - 2026-07-03

## [obs-t-data-v1.0.0] - 2026-06-30

### Added
- **OBS-T data deposit** — Zenodo dataset snapshot of the OBS-T (observatory
  bot-triage) validation study: `reports/obs_t_paper_draft.md` (first full
  draft, ~6000 words), `reports/obs_t_validation.md` and
  `reports/obs_t_errorbench.md`, plus the underlying `validation/gold_sample.csv`
  (390-row gold annotation), `validation/error_sample.csv` (120-row error-type
  sample), and `validation/gold_metrics.json`. Zenodo metadata + `CITATION.cff`
  completed for the deposit; separate tag from the software `v*` releases so
  the dataset citation stays pinned to this exact commit.

## [1.1.0] - 2026-06-27

### Added
- **Agent issue-automation roadmap** (`docs/AGENT_ROADMAP.md`) — living map of
  820+ open issues across 68 repos, classified Tier A–D by agent-readiness;
  moved here from Uprava and linked prominently in README.
- **Tier C P3 — `cologne-question-research` skill** — swept ~130 `question`
  issues org-wide; ~73 comments posted with concrete data; ~57 skipped.
  Findings digest: `docs/question-research-findings.md`.
- **Tier C P4 — `cologne-bug-triage` skill** — swept 84 `bug` issues across
  22 repos; ~24 comments posted; 10 new Tier A bugs surfaced; 8 confirmed
  already-fixed. Findings digest: `docs/bug-triage-findings.md`.
- **Bot-noise policy** — Phase 3.5 gate (no post without concrete data),
  `<details>` collapsible wrapper on all agent comments, per-skill digest `.md`
  files as non-GitHub finding stores. Documented in `docs/AI_CONTRIBUTION_POLICY.md`.
- **Tier A P5 — source-correction PRs** — 12 PRs opened (csl-orig ×8,
  csl-pywork ×1, csl-websanlexicon ×1, csl-apidev ×1); 2 merged same day.
  Fixes: MW ruci→Ruci, STC broken s.v. lines, INM truncated headword, LRV
  homonymy markers, SCH double spaces, MW stub entry merge, SHS k1/k2 bracket
  correction (10 metalines), CAE v. abbreviation, iOS enterkeyhint on search
  inputs, address-bar pushState for simple-search.

### Fixed
- Dependabot auto-merge now validates PRs before merge, leaves semver-major
  updates for human review, and no longer falls back to a blind direct merge.
- Observatory refresh now uses `npm ci`, commits refreshed data/report artifacts
  before Pages deployment, and fails loudly if `git push` fails.
- GitHub snapshot fetching now passes the requested `--since` date into commit
  collection and records attempted, skipped, and failed repos in the manifest.
- Refresh coverage now rejects snapshots where attempted repos would silently
  disappear from `repos.csv`.
- Contributor identity refresh now reads the current generated repo inventory
  from `data/repos.csv` instead of a stale hardcoded list.
- The public data catalog now includes `manifest.json`, restoring
  `scripts/data_index.py --check`.
- RH1 helper scripts now exit nonzero on partial batch failures and use the
  final `licenses/GPL-3.0.txt` dual-license wording.

## [1.0.0] - 2026-06-16

### Fixed
- Front-door number drift: the landing dashboard now filters bots from the
  contributor count, reports 76 repos / 13 years consistently, and reads its
  row-count table and snapshot date from `data/manifest.json` (no hand-typed
  numbers). The "last refreshed" stamp shows the data snapshot date, not the
  render date.
- OBS-T paper and datasheet: corrected the form-layer link rate (12.9% → 28.8%,
  the post-Phase-8 value computed from the released corpus).

## [0.1.0] - 2026-06-13

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
- Citation DOI minted: [10.5281/zenodo.15834721](https://doi.org/10.5281/zenodo.15834721) (in CITATION.cff). Contributor ORCIDs are not yet registered.

[Unreleased]: https://github.com/sanskrit-lexicon/csl-observatory/compare/v1.1.0...HEAD
[1.1.0]: https://github.com/sanskrit-lexicon/csl-observatory/compare/v1.0.0...v1.1.0
[1.0.0]: https://github.com/sanskrit-lexicon/csl-observatory/compare/v0.1.0...v1.0.0
[0.1.0]: https://github.com/sanskrit-lexicon/csl-observatory/releases/tag/v0.1.0
