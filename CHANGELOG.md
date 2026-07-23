# Changelog

All notable changes to this repository are documented here, following [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- **Three analytical idle-stats dashboards (H1524).** POS-by-text, paradigm-cell coverage,
  and sense polysemy were already computed (H817 TSVs + reports) but only thin census
  magnitude bars. New Observable pages at `/pos-by-text`, `/paradigm-cell-coverage`, and
  `/sense-polysemy` (each ≥5 `Plot.plot` calls, Trust Block, table + CSV download), with
  read-only TSV→CSV loaders under `observatory/site/src/data/`, nav + `PAGE_DESCRIPTIONS`,
  smoke registration, and sitemap. Executed by Grok 4.5 (`grok-4.5`) on user override of the
  Sonnet 5 intended executor.

## [1.3.0] - 2026-07-21

### Added
- **Blind cross-model IAA for the OBS-T location axis (H1385): κ = 0.906 [95 % CI 0.872–0.938], n = 390.**
  Two fresh, mutually blind LLM annotation passes — Opus 4.8 (`claude-opus-4-8`) and Sonnet 5
  (`claude-sonnet-5`) — over all 390 gold-sample rows against `validation/COMPONENT_GUIDE.md`,
  under the org's pre-registered blind-LLM second-annotator reliability protocol (gate ladder,
  seeds and models committed before either pass ran). Raw agreement 92.8 %; pre-registered
  4-group granularity κ = 0.896 [0.855–0.935]; per-annotator label flip-rates over 3 repeated
  runs 4.4 % / 5.6 % (below the 10 % instability gate). New artifacts under `validation/`:
  `build_blind_sample.py`, `gold_sample_blind.json`, `blind_batches/`, `component_passA.json`,
  `component_passB.json`, `flip_runs/`, `compute_component_kappa.py`,
  `component_kappa_stats.json`, `component_kappa_disagreements.csv` (28 rows). The draft's three
  "pending a second annotator" passages replaced with the measured result and its cross-model
  caveat. Axis finding recorded: the June `gold_component` fill follows the paper's older 9-label
  hybrid Table 1 (65 % `encoding`/`orthography`), while the codebook and the current pipeline
  `error_component` axis are location-only — the fresh passes annotate the codebook axis and are
  kept as separate artifacts.

### Fixed
- **Stale false-DOI footer line in `reports/obs_t_paper_draft.md` (H1364 residue).** The draft's
  closing footer still asserted `10.5281/zenodo.15834721` as "minted 2026-07-01"; it now states
  no DOI is minted, matching §8 and the H1364 sweep.
- **False OBS-T Zenodo DOI citation removed everywhere it was still asserted as genuine (H1364).** `10.5281/zenodo.15834721` resolves to an unrelated topology preprint (confirmed by the 03-07-2026 G6 finding, re-confirmed by a live check 20-07-2026). Corrected in `CITATION.cff`, `README.md`, `reports/obs_t_paper_draft.md`, `docs/REVIEWER_REPRODUCIBILITY.md`, `observatory/site/src/data.md`, `observatory/site/src/reproducibility.md` — all now state no DOI is minted yet instead of citing the false one. Re-minting remains an MG action; see [SanskritLexicography CONTRADICTIONS §8](https://github.com/gasyoun/SanskritLexicography/blob/master/CONTRADICTIONS.md).

## [1.2.1] - 2026-07-18

### Fixed
- **`data_index.py` measures committed content, not environment state (G17/H1223)** — recorded
  bytes are now the LF-normalized content size (what git stores under the repo-wide `eol=lf`
  policy) instead of `st_size`, killing the recurring `data-index-check` drift where a
  regeneration recorded CRLF-inflated sizes (`csv.writer`'s default `\r\n` lineterminator) that
  every fresh checkout then measured under by exactly one byte per line — confirmed 43/43
  `crlf-exact` at the poisoned `6f573f1` baseline, see
  `reports/data_index_crlf_drift_audit.md`. The 4 hand-curated `data/` files registered by #92
  are now resolved from their canonical committed home whether or not the workflow's
  "Copy data into site" step has run, so `--check` passes on a fresh clone; `data_index.csv`
  itself is written `newline="\n"`. Baseline regenerated (59 files catalogued); diagnostic
  scripts `g17_delta_audit.py` + `g17_historical_check.py` added.

## [1.2.0] - 2026-07-14

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
- **H787 — per-family verdict table for the 5 census-flagged pipeline template
  families** (follow-up to H688): diffs each `csl-pywork` canonical against
  the census's modal deployed representative and rules direction. For
  `transcoder.py`/`updateByLine.py`/`parseheadline.py`/php, the `csl-pywork`
  template actually LEADS deployment — the census's "template lags
  deployment" flag was inverted for them (hash mismatch, not staleness
  direction). Only genuine defect was the headless `digentry.py`, fixed by a
  one-file `csl-pywork` PR. The "bimodal 75/57" `updateByLine` split resolves
  to a single stdout-reconfigure line, not a real fork.
- **H688 — code-duplication census re-run: the sanskrit-util dedup payoff,
  measured.** Committed, reproducible successor of the throwaway 2026-06-14
  SHARED_CODE census (basename + MD5 grouping, 129 canonical repos).
  Headline: `transcoder.py` 83 copies (was 62), `digentry.py` 193/5 (was
  170/5, zero new drift) — vendored counts grew by design; the payoff is in
  the app-code lane (4/19 donor sites now delegate + 5 vendored
  package copies/shims). Two defects found: `digentry.py` is headless (no
  canonical copy in `csl-pywork`); 5 families' template copy is not the modal
  deployed version.
- **A15 — skeleton to full draft**: data-layer bus factor (§3.7),
  correction-loop anatomy + the 52,498-event ledger (§4), claim→artifact
  inventory. Every number recomputed from committed artifacts; 9 fact-check
  findings fixed pre-commit. Venue stays `@DECIDE`.
- **A14 — referee pass**: every claim re-verified against committed data,
  Figure 1 generated (`scripts/article_figures.py` →
  `article/figures/contributor-gantt.png`). Corrected several headline
  numbers against their source snapshots/reports (contributor timeline,
  issue-label counts, top-10 coverage share), fixed an MW/PWG worked-example
  misattribution, repaired dangling `report (SSX.Y)` cross-refs after A13's
  IIJ pass de-numbered the report's headings, rewrote §7 limitations, and
  relicensed the data CC BY-SA → CC BY 4.0.
- **HYPOTHESIS_VIZ_STANDARDS_SPEC Phase 3** (H269 design spec → H303/H293
  builds): H4–H9 falsifiable hypotheses in the existing rigor idiom (Wilson
  CI, χ²+Cramér's V with commit-block bootstrap, Mann-Kendall+BH,
  contributor-level permutation tests, exact binomial per confusion pair);
  two new dashboard pages — `correction-anatomy.md` (confusion heatmap, H8
  asymmetry, corrector Pareto/component matrix, tenure spans) and
  `org-shape.md` (contributor×repo heatmap, specialisation entropy, family
  capture, snapshot drift); `palette.css` light/dark tokens; H9 routed to
  csl-atlas per the spec's Part 3. Build green (26 pages, 81 links).
- **A12** — OCR-post-correction literature (Faroese HMM+Viterbi, neural
  RNN+ConvNet, LLM-based post-correction benchmarks) wired into the paper's
  error-typology framing.
- **A15 skeleton** — "CDSL as a GitHub maintenance ecosystem" (~2,900-word
  draft, readiness 2/5 → 3/5): six manifest-anchored maintenance findings +
  the csl-orig 2025–2026 correction-campaign case study, with an explicit
  anti-salami boundary note vs A12–A14. Fact-checked by two independent
  agents (5 mismatches found and fixed).

### Fixed
- `obs_phase3_rigor.json` + `obs_t_corrector_component.csv` registered in the
  `data_index` CATALOG — they'd landed via the H303/H293 PRs above but were
  never cataloged, so `refresh_observatory.py --check-only` failed at the
  data-index-check phase (caught by GOALS_MANUAL.md G17).

## [1.1.1] - 2026-07-03

### Added
- **OBS-T paper** — target venue set to LREC-COLING, Zenodo DOI
  `10.5281/zenodo.15834721` minted and wired in across status/reviewer/site
  docs (draft itself shipped in the `obs-t-data-v1.0.0` slice below).
- **G1 — issue lifecycle and responsiveness track**: survival cohorts,
  backlog age pyramid, latency metrics, new `/lifecycle` page.
- **G2 — active delta monitor**: snapshot-vs-HEAD digest wired into the
  weekly refresh.
- **G3 — capture-recapture estimate of correction work remaining** (H089);
  scaffolds **A48** (capture-recapture paper skeleton).
- **G4 — contributor-repo network page** (H090): force map + adjacency
  matrix.
- **G5 — narrative story page**: "13 years in one scroll" (`/story`).
- **G6 — external reach (scholar-framed) page + OBS-T Zenodo DOI mismatch
  flag** (H092); Workstream G (G1–G6) now fully shipped.
- **Citation Coverage dashboard** (`/citation-coverage`) — PWG `<ls>` citation
  link-coverage metric (data + report), with SEO JSON-LD (Organization/
  Person/WebSite/Dataset), per-page meta descriptions, sitemap + robots.txt.
- **A13 — IIJ narrative-report fix pass** (sections A–E) + a verified
  Jachertz 1983 reference and fonts-embedded PDF; `CROSS_REPO_DECISIONS`
  re-adjudicated (12 closed, tiers re-ranked) alongside an A13 go/no-go
  review.
- **`MAINTAINER_ACTIONS.md`** — public pending-maintainer worklist; a
  Cologne page-speed audit (2026-07) with maintainer-action rows; a
  2026-06-27 maintainers-call talking-points card.
- Full org dictionary-page SEO coverage (31 pages: social cards, sitemap,
  per-page meta descriptions, canonical/OG/Twitter head tags, CDN warming
  notes).
- `verify-first OBS-T DOI sweep script` (H104 prep); Zenodo/DOI thread
  formally deferred to 17-07-2026 per MG ruling.

### Fixed
- Mixed `const`+`Plot.plot` cells split so all charts render (error-typology
  + repo-size log-scale barX `x1=1` fix).

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
- Maintainer-dashboard pages gain description paragraphs, "how-to-read"
  callouts, and per-chart conclusions across the board.

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
