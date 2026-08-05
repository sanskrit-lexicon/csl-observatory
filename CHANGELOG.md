# Changelog

All notable changes to this repository are documented here, following [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Fixed
- **G17 `refresh_observatory.py --check-only` red fixed (H2037, Sonnet 5 `claude-sonnet-5`).**
  `repo-metadata-check` and `workflow-health-check` were failing because `repos.csv` gained
  `PUI` (Purana Index 1951) on 2026-07-31 and neither `repo_metadata.csv` nor
  `workflow_health.csv` had been re-derived since — a stale-artifact drift, not a code
  regression, exactly as the phase's own note predicted. Reran the writer phases
  (`repo_metadata_snapshot.py`, `workflow_health.py`, `data_index.py`) to add the missing
  row. Also fixed a real bug surfaced along the way: `refresh_observatory.py`'s
  `run_text()` decoded subprocess output without an explicit `encoding="utf-8"`, so any
  non-UTF-8 byte from `npm run build` on Windows (observed: a stray `0xad`) crashed the
  whole pipeline with an unhandled `UnicodeDecodeError` instead of reporting the phase as
  failed. Added `encoding="utf-8", errors="replace"`. All six data/regression `--check-only`
  phases now pass locally; `site-build` remains locally red only because `observable build`
  fetches `npm:d3@latest` from a CDN this network can't reach (`ConnectTimeoutError`) — out
  of scope per the handoff's own "CDN-only failures without local fix path" exclusion. CI's
  equivalent `npm run build` step (real network) went green on the 2026-08-03 scheduled
  [Refresh observatory run](https://github.com/sanskrit-lexicon/csl-observatory/actions/runs/30789576509).

## [1.8.0] - 2026-08-04

### Changed
- **July cross-repo decisions re-adjudicated (H1875, Fable 5 `claude-fable-5`).**
  Every item of the 2026-07-02 edition of
  [`docs/CROSS_REPO_DECISIONS.md`](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/docs/CROSS_REPO_DECISIONS.md)
  re-checked against live repo state via seven read-only evidence sweeps:
  14 still-correct, 10 overtaken (struck in place with superseding pointers),
  9 contradicted (evidence + ruling in place). Headline corrections: the
  Tier-1 second-annotator recruit was PARKED by M.G. on 03-07 and must not
  resurface in 2026; "A12 DOI minted" was false (H1364 scrub); MWS G5 gold
  executed in full 02–03-07; csl-atlas H4 agent-adjudicated and the Xref
  "independent witnesses" premise retracted; the SanskritKaraoke audio-TODO
  and IndologyScholars sheet counts corrected against the actual files.

## [1.7.3] - 2026-07-29

### Changed
- **Fixed stale roadmap status drift (H1877 sweep).** `docs/ROADMAP.md` RH2 (license backlog)
  flipped scheduled → done: RH1 rollout (PR #54/#55, merged 2026-06-19/20) already resolved it
  to 0/77 `NOASSERTION` and 6/77 no-license (all six are the RH3 archive candidates). In
  `docs/OBSERVATORY_ROADMAP.md`, A1 (repository inventory) flipped active → done, past its
  2026-07-15 target, since `repo_health.md` already regenerates cleanly with explicit cleanup
  flags; A3 (contributor/identity snapshot) reworded scheduled → mostly done — the script
  already flags missing name/ORCID, only the `consent` field and human ORCID-filling remain.

## [1.7.2] - 2026-07-29

### Changed
- **All seven workflows now check out with `lfs: true`, not just the one that needed it
  (follow-on to [#127](https://github.com/sanskrit-lexicon/csl-observatory/issues/127)).**
  v1.7.1 fixed the workflow that demonstrably read LFS-backed data; the other six were
  correct only *by coincidence of what those jobs run today*, not by construction — a step
  added later that touched `correction_events*.csv` would have hit the same silent-stub class,
  and outside `data_index.py` there is no guard to catch it. **The honest trade-off, stated so
  nobody has to re-derive it:** a smudged checkout pulls **301 MB** (6 files, 12–62 MB each),
  and none of these six jobs reads them today — verified, not assumed: the 18 scripts that
  read `correction_events*` all run in `refresh-observatory.yml`, no site page
  `FileAttachment`s them, and `npm run build` therefore never copies them into `dist/`. So
  this buys future-proofing at real bandwidth cost, worst on
  `dependabot-auto-merge.yml`, which fires on every Dependabot PR. If LFS bandwidth quota
  becomes a problem, **revert these six rather than `refresh-observatory.yml`** — that one is
  load-bearing, and exhausting the quota would break it, which would be the worse outcome by
  far.

## [1.7.1] - 2026-07-29

### Fixed
- **The public data catalog published Git LFS *pointer* sizes as dataset sizes — the citable
  OBS-T release table was listed as "2 rows / 133 bytes" when it is 52,498 rows / ~62 MB
  ([#127](https://github.com/sanskrit-lexicon/csl-observatory/issues/127), H1845).** Two
  mutually-concealing halves: `refresh-observatory.yml` checked out **without** `lfs: true`,
  so the weekly refresh saw ~133-byte stubs; and `data_index.py` sized whatever bytes were on
  disk — correct behaviour given a wrong input, since a pointer is a *valid, readable, 2-line
  CSV* and nothing errored. The result **oscillated**: any contributor with LFS smudged
  regenerated true values and the next CI refresh silently reverted them, with neither side
  flagged — a wrong number that keeps changing back reads as ordinary churn. `data_index.py
  --check` could not catch it either, because it validates catalog *coverage* (is every
  public file described?), not whether a described size corresponds to real data. Fixed at
  both ends: CI now checks out with `lfs: true`, and `data_index.py` **refuses to run at all**
  against un-smudged pointers (new `lfs_pointer_size()` + `guard_lfs_smudged()`), naming the
  offending files and both remedies, so removing that CI line again fails the job loudly
  instead of silently republishing stub metadata. If the guard is ever bypassed, a pointer now
  reports the size recorded *in* the pointer and an **empty** row count — the honest answer
  from a stub is *unknown*, never *2*. Verified with a two-sided control (pointer blocked
  with an actionable message; real data, and a file merely *mentioning* the LFS spec URL, both
  pass; silent on a clean checkout — 5/5). Blast radius bounded and checked: this workflow is
  the only one running `data_index.py`, no site page loads the LFS-backed CSVs, and no
  findings script reads them — catalog metadata was wrong, no published analysis was computed
  over stubs.

## [1.7.0] - 2026-07-29

### Added
- **`reports/citation_sweep.md` + `scripts/citation_sweep.py` — the systematic OpenAlex
  citation sweep that replaces Tier 4's five hand-picked citations (H1478, roadmap G6
  extension).** `reports/external_reach.md` had named its own gap for a month ("Citations are
  under-counted here by design; a systematic Scholar / OpenAlex sweep is the natural G6
  extension"); this closes it. The sweep pulls **3 citation-graph anchors** (`cites:<id>`,
  identifier-exact) plus **14 phrase probes**, deduplicates by OpenAlex work id, applies a
  46-token Indological/lexicographic domain gate, and removes the org's own Zenodo release
  records, yielding a **documented lower bound of 35 works** that demonstrably name or cite
  the Cologne *digital* lexicon (C1 confirmed 31 + C2 probable 4, snapshot 2026-07-28).
  The methodological core is what is *refused*: bare sigla are never enumerated, and their
  collision counts are published as the evidence — `"MW"` matches **2,336,225** works,
  `"PW"` 873,310, `"Monier-Williams"` 2,453 — because swapping five accurate citations for
  hundreds of thousands of noisy ones would be strictly worse for the paper than the hedge
  it replaces. A separate **228-work print-dictionary envelope (C3)** is reported beside the
  headline and never added to it: citing Monier-Williams 1899 says nothing about whether the
  Cologne digital edition was used. Recall bounds are stated, not hedged — full-text
  coverage is 15.1% of OpenAlex's corpus, siglum-only citations are invisible by design, and
  the seed-recall proxy against the five previously hand-curated citations is published as
  measured. Follows the established tier pattern: network only under `--fetch`, month-stamped
  JSON cache committed under `reports/citation_sweep_cache/`, and every count regenerates
  byte-identically offline from a fresh clone.
  > **Adversarially audited before merge, and the audit moved the number.** The published
  > figure is 35, not the 36 the first pass produced: a `"Digital Pali Dictionary"` probe had
  > been filed as name-unique-for-CDSL, but DPD is an independent Pali project, so a work
  > saying "lemmatized using the Digital Pali Dictionary" names DPD, not Cologne — reach
  > *through* a downstream consumer is a different claim from citation and cannot be summed
  > into it. Retiring that probe exposed a second defect: `classify()` read the cached probe
  > blocks rather than the probe registry, so retiring a probe changed nothing until the
  > registry became authoritative — an unsound probe could have gone on contributing from a
  > stale cache. Also fixed: `"Cologne Digital Sanskrit Dictionary"` and `"…Dictionaries"`
  > are one probe, not two (OpenAlex stems; verified byte-identical 39-work result sets), so
  > 20 C1 rows had been showing phantom double confirmation; recall bound #1 claimed
  > full-text coverage caps recall outright, which the sweep's own results refute (Zenodo and
  > CRAN records have no full text yet matched); a temporally impossible citation edge (a
  > 2012 work "citing" the 2014 record) is now dropped by a `citing_year < anchor_year`
  > guard; and the report states where C1 actually concentrates (4 of 8 name-unique probes
  > contribute nothing).
- **OpenAlex now meters keyless access by a daily dollar budget — `--fetch` is no longer a
  reproducibility path.** Measured 2026-07-29: `{"error":"Rate limit exceeded","message":
  "Insufficient budget … Resets at midnight UTC","retryAfter":80414}` after roughly fifteen
  count-only requests from one address, identical with or without a `mailto` (the script's
  "polite pool … no key" comment was written against the old behaviour). Because the old code
  treated this as a transient 429, retried three times with ≤5 s backoff against a documented
  80,414 s `retryAfter`, and then wrote whatever had landed, a throttled refresh could have
  **silently overwritten a complete cache with a truncated one and lowered the published
  citation count**. `fetch_all` is now atomic — every payload is buffered and the snapshot is
  committed in one go — and budget exhaustion raises rather than warns, leaving the previous
  cache untouched. The offline rebuild is unaffected and remains the reproducibility guarantee.

### Changed
- **`reports/external_reach.md` Tier 4 rewritten from "estimated, representative" to
  "systematic sweep, bounded" (H1478).** `scripts/external_reach.py` no longer publishes a
  hand-maintained `CITATIONS` list; it consumes the sweep's committed output and prints the
  method, the tier counts, an explicit coverage/completeness statement, and all 36 claimed
  works. The old hand-picked list survives only as `SEED_CITATIONS`, the seed set whose
  recovery the sweep measures as its recall proxy — adding a citation now means adding a
  probe or an anchor, so the addition is systematic and its recall consequence is measured.
  The site's [External Reach](https://sanskrit-lexicon.github.io/csl-observatory/reach) page
  gains the swept-works table and a C1/C2/C3-by-year distribution; `citation_sweep.csv` is
  registered in the public data catalog; `reports/README.md` now indexes both this report and
  `external_reach.md`, which had never been indexed.
- **docs/AGENT_ROADMAP.md live re-compile 2026-07-28 (H1787)** — Tier A/B rows re-verified against open issues + local csl-orig tip; open agent PRs #2865/#2867/#2872/#2874 babysit-only (csl-orig never agent-merged); close-ready / re-tier comments posted on #1537, devanagari#42, #1788, #2824, websanlexicon#60, #606. Label tallies still 2026-06-26 snapshot.

## [1.6.0] - 2026-07-28

### Added
- **`reports/pwg_kosa_hocr_cer.md` — first CER measurement for BSB's published per-page hOCR against a print e-text (H1720).** All 374 indexed pages of the `amara_dlc` (Amarakoṣa, Deslongchamps 1839, `bsb10250868`) campaign harvested via [`scripts/pwg_kosa_hocr_ingest.py`](scripts/pwg_kosa_hocr_ingest.py), page offset (`-3`) derived empirically rather than assumed, and aligned to [`AMAR/amar.txt`](https://github.com/sanskrit-lexicon/AMAR) by content (token-overlap window search per kāṇḍa, never by in-page digits — the FINDINGS §480 trap). Mean CER over a 39-page depth-stratified sample: **0.719**, reported as a ceiling, not a floor — a gender-tag format mismatch between AMAR's per-word gloss list and the printed verse text inflates the figure independently of true OCR error, on top of the expected edition-variance caveat. `abch2` (Hemacandra) harvest/CER remains open follow-on work; the handoff's DoD is met by one edition.
- **`reports/record_linkage_rejected_alternatives.md` — the negative results behind the G3/A48
  linkage key, including a measurement that only existed on an unmerged branch (H1477).**
  Handoff H1477 was implemented twice concurrently; the second implementation was left
  uncommitted when its session ended and is now preserved unmerged on branch
  [`h1477-recapture-fuzzy-linkage`](https://github.com/sanskrit-lexicon/csl-observatory/tree/h1477-recapture-fuzzy-linkage).
  Its linkage proposal lost on measurement (328 recaptures against `form_key`'s 396; the union
  of both encoding repairs is worth **+1**), but three of its results are independent of that
  and are now on `main`: **64% of resolvable form-era `<L>` codes (14,403 of 22,466) no longer
  resolve to a record carrying that event's headword** — with a per-dictionary table, pw 53.9%
  valid down to cae 0.2% — so *any* join of 2014 form-era OBS-T data onto csl-orig by `<L>`
  number is unsafe outside pw and mw; the `anchored` key is documented as a change of
  population (drops 40–97% of form-era events), not a linkage choice; and edit-distance-1 is
  recorded as rejected by **two independent implementations** (63.4% false matches / 606-of-863
  pw links joining distinct lemmas), which settles the handoff's headline request. Also records,
  so it is not later mistaken for a data-integrity bug, that the SLP1 `repair` rewrites the
  occasional English cell in `headword_iast` (`work` → `ṭork`): 14 of 4,176 firings (0.3%),
  zero counted recaptures affected. `reports/README.md` now indexes all three recapture reports
  (the two from [#120](https://github.com/sanskrit-lexicon/csl-observatory/pull/120) were never
  registered).
- **`docs/DATASHEET_TEMPLATE.md` + `/data-release` wiring (H1541, roadmap Part 4.2 template
  half).** Generalized the filled OBS-T `docs/DATASHEET.md` into a blank, reusable Gebru-style
  template covering every mandatory section named in the spec (motivation, composition,
  source edition/page range where applicable, encoding + transliteration regime, collection
  process, known gaps & label-quality state, license, intended use, maintenance). The global
  `/data-release` command now points at this template in its Phase 2 FAIR pack and states the
  release gate explicitly. Zenodo DOI half of §4.2 excluded (credential-gated, deferred).
- **RH4 `.gitattributes` (`eol=lf`) line-ending policy rolled out org-wide (H1542, roadmap RH4).**
  All 34 repos in `.github/workflows/tooling-audit.yml` REPOS now carry the LF-normalization
  policy piloted in this repo (RH4-pilot): 12 already had it, 22 rolled out and merged via a new
  `gitattributes` deploy entry in [`Uprava/tools/cologne_batch_deploy.py`](https://github.com/gasyoun/Uprava/blob/main/tools/cologne_batch_deploy.py)
  (which also gained a `--repos` comma-list scope flag and transport-error retry-with-backoff on
  `gh()`, both reusable for future org-wide rollouts). `docs/DECISIONS_NEEDED.md` RH4 flipped to
  resolved; `docs/ROADMAP.md` RH4 flipped to done.
- **`scripts/pull_data.py` project-board fields + explicit rate-limit handling (H1540, roadmap A2).**
  `issues.json` entries now carry a `project_fields` object (Tooling Roadmap project #9 board
  values — `Title`/`Status`/`Category`/etc., keyed by repo+issue/PR number) fetched via the
  batched/aliased `ProjectV2` GraphQL pattern already documented in `.ai_state.md`; `summary.json`
  gained `total_project_board_items`. `gh()` now detects GitHub's primary and secondary rate-limit
  responses explicitly (separate retry budget from the existing 5xx/backoff path), reads the reset
  time off `gh api rate_limit`, sleeps (capped at 120s), and logs the wait — closing A2's full
  acceptance sentence ("One command refreshes issues, PRs, labels, milestones, and project-board
  fields with rate-limit notes"); A2 flipped to done in `docs/OBSERVATORY_ROADMAP.md`.
- **MWSA evaluation-lineage subsection (H1539, roadmap Part 4.3).** `docs/DATASHEET.md`
  gained an "Evaluation lineage" section and `paper-obs-t-error-typology.md` gained
  §4.5, both naming OBS-T label validation as an instance of the ELEXIS/GlobaLex
  Monolingual Word Sense Alignment (MWSA) shared-task family (Ahmadi et al. 2020) —
  adopting its evaluation contract (frozen gold sample, two annotators, Cohen's κ,
  per-class P/R/F1) rather than a bespoke method, and noting that any future
  cross-dictionary sense-alignment dataset routes its content to `csl-atlas`, with
  `csl-observatory` keeping only the process metrics. Reference added to the paper's
  bibliography; Part 4 acceptance checklist item 3 flipped to done in
  `docs/HYPOTHESIS_VIZ_STANDARDS_SPEC_2026-07.md`.
- **Measured record linkage + a second recapture design for G3/A48 (H1477).** The two-era
  capture-recapture estimate was joining the eras by exact headword string, which loses real
  recaptures (the form era carries ASCII fallbacks, homonym digits and 3,905 cells of raw SLP1
  residue; the git era carries clean `<k1>`) and so inflates N̂. New
  [`scripts/headword_linkage.py`](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/scripts/headword_linkage.py)
  supplies a **ladder of linkage keys with a measured false-match rate for each** — two offline
  measurements against the dictionaries' own `<k1>` inventories: key-collision rate
  (`headword_key_collisions.csv`) and an attestation test on the pairs actually matched
  (`linkage_ladder.csv`). Result: the operating key (`form_key`, length- and
  retroflexion-preserving, over an SLP1-residue repair, plus a headword-component alias) lifts
  recaptures pw 169 → 196, mw 105 → 131, bur 23 → 44, cae 1 → 13 — **cae becomes estimable
  (4 dictionaries, was 3)** and **bur comes off the record-count cap** (~17,247 against 19,776
  records), showing the old ceiling was an artefact of the join. The naive edit-distance-1 port
  is **measured and rejected**: 606 of 863 pw links and 474 of 616 mw links join real, distinct
  lemmas. Normalization comes from the shared `sanskrit-util` package, not a re-roll. Also new:
  [`scripts/corrector_recapture.py`](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/scripts/corrector_recapture.py)
  — the **within-era corrector-pair design** (correctors as occasions; pairwise Chapman + Chao2
  incidence with log-normal CI; identity resolution, joint cells excluded as non-independent) →
  [`reports/corrector_recapture.md`](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/reports/corrector_recapture.md),
  which cross-checks the two-era numbers at the same order of magnitude and gives **pwg its
  first population estimate** (~26,515), a dictionary the two-era design cannot reach.
  `dict_record_counts.csv` extends the record-count cap from 3 hand-counted dictionaries to all
  44 csl-orig v02 ones. A48 readiness 2/5 → 3/5.
- **Encoding/XML guard for dictionary-source change paths (H1496, roadmap RH5).**
  `scripts/encoding_xml_guard.py` checks no-BOM, UTF-8 validity, NFC normalization, and
  (for `.xml`) `ElementTree` parseability, CI-friendly (`violations: N` line, nonzero exit
  on any). Piloted live in this repo (`.github/workflows/encoding-guard.yml`) against
  bundled good/bad fixtures (`runbook/fixtures/encoding_guard/`) — satisfies RH5's
  "piloted on `csl-orig` or the owning tooling repo" acceptance via the owning-tooling-repo
  branch, since agents never commit to `csl-orig` directly. Fan-out template for other
  dictionary/tooling repos' actual change paths:
  `runbook/templates/encoding-xml-guard.yml` (draft, mirrors `taxonomy-drift.yml`'s
  sparse-checkout shape). Design: `docs/ENCODING_GUARD.md`. RH5 flipped `scheduled` →
  `done` in `docs/ROADMAP.md`.
- **Persistent OBS-T event-ID scheme (H1494, roadmap Part 4.1).** `event_id` in
  `data/schema/correction-event.schema.json` now carries a `pattern`
  (`^obst:v1:(form|git|printchange|batch):[a-z0-9]+:[0-9a-f]{12}$`) plus a `$comment`
  documenting the SHA-256 recipe (`event_id_v1()` in `scripts/build_correction_events.py`,
  reused by `scripts/reconstruct_git_events.py` so freshly generated rows already comply).
  One-off `scripts/migrate_event_ids_v1.py` rewrote all 52,498 rows across every
  `correction_events*.csv` to the new scheme (idempotent, schema-validated 0 errors) and
  wrote `observatory/site/src/data/event_id_crosswalk_v1.csv` so any `event_id` already
  cited in a report stays resolvable. **Known property, not a bug:** the tuple deliberately
  excludes `headword_iast`, so 7,948 of the 52,498 rows share an id with at least one other
  row (identical evidence). `data/manifest.json` gained a `dataset_ids.correction-events`
  row (`csl-obs/correction-events@1.0.0`); `observatory/transform.py` now preserves that
  key across its own regenerations instead of silently overwriting it.
- **PWG kośa e-text pilot — a measured NO-GO, and a cheaper route (H1715).** The H1706
  e-text queue ranked `amara_dlc` (Amarakoṣa, Deslongchamps 1839) and `abch2`
  (Abhidhānacintāmaṇi, Böhtlingk & Rieu 1847) at the top; H1715 proposed OCR-ing them with
  tesseract 5 `san`. Measured instead: **local tesseract scores 17.8 % valid Sanskrit tokens
  where the Bayerische Staatsbibliothek's already-published per-page hOCR scores 43.8 %** on
  the identical 12 pages — 2.5× better, word-boxed, free, and reachable from the IIIF
  manifest's `seeAlso`. An 18-configuration sweep (dpi × psm × preprocessing) tops out at
  30.5 %, and only by reading half as many tokens, so the low rate is the material and not
  the settings. The job is therefore an **ingest-and-correct**, not an OCR.
  New: `scripts/pwg_kosa_ocr_probe.py`, `reports/pwg_kosa_etext_pilot.md`,
  `data/pwg_scan_index_tracker/kosa_ocr_pilot.tsv`; the e-text queue's two top rows now carry
  the verdict so it is not re-derived.
  Page images are from the Bayerische Staatsbibliothek (`bsb10250868`, `bsb10250953`) and
  derived artifacts carry the library credit the scan repos already give. Publication of
  everything derived here was ruled open on 27-07-2026.
  Executed by Opus 5 1M (`claude-opus-5[1m]`).

### Changed
- **The two rival A12 (OBS-T) manuscripts are reconciled into one canonical draft (H1759).**
  [`paper-obs-t-error-typology.md`](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/paper-obs-t-error-typology.md)
  (two-axis framing, released 52,498-event snapshot) is the single surviving A12
  manuscript; the one-axis 50,953-event `reports/obs_t_paper_draft.md` is retired to a
  tombstone stub. Carried across in the merge: the byline block, the cross-model IAA
  section (κ = 0.906 [0.872–0.938], stated as cross-model — not human-validated), accurate
  gold-sample provenance wording (machine first pass, no human annotation; the final
  submission wording stays an open human decision, H1272), the 0/120 error-sample
  benchmark, the related-work survey, the false-DOI warning, and 16 references. Every
  headline number was re-verified against the released snapshot and generated reports
  (verification table + full editorial ruling in
  [`docs/A12_OBS_T_MANUSCRIPT_RECONCILIATION_RULING.md`](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/docs/A12_OBS_T_MANUSCRIPT_RECONCILIATION_RULING.md)).
  `STATUS.md`, `docs/ERROR_TYPOLOGY_DESIGN.md` and `article/A15_github_ecosystem.md`
  repointed at the survivor.

### Fixed
- **Repaired all four red default-branch workflows found by the org CI-health sweep (H1736).**
  `pages build and deployment` was red 72.6 days on a Liquid syntax error in
  `article/01-empirical-companion.md` (`{%…%}`/`{{…}}` used repo-wide as literal CDSL tag
  notation, not templating) — added a repo-root `_config.yml` disabling Liquid rendering
  site-wide. `Refresh observatory` was already fixed on `main` by an unrelated commit
  (#120) that added `event_id_crosswalk_v1.csv`'s catalog entry after that morning's failed
  scheduled run; verified `python scripts/data_index.py --check` now passes. The two audits
  (`Dictionary taxonomy audit`, `Tooling Roadmap audit`) were working as designed — they had
  found real drift, not a code bug: added AMAR#8, BEN#34 (a newly-opened untriaged issue),
  PWG#210, MWS#242, and 8 tooling-repo issues to their missing org-project columns; and
  taught `scripts/dict_runbook.py` that a bare `handoff` label (with no taxonomy labels) marks
  an auto-created execution-tracking stub, not triageable dictionary work — MWS
  #243/#250/#254/#256 were false-flagged as drift for exactly that reason. `TOOLING_AUDIT_TOKEN`
  is set and working; the handoff's note about it being unset did not reproduce.
- **`event_id_crosswalk_v1.csv` was never registered in `scripts/data_index.py`** (it arrived
  with the persistent-event-ID migration in [#109](https://github.com/sanskrit-lexicon/csl-observatory/pull/109)),
  so `python scripts/data_index.py --check` — which `refresh-observatory.yml` runs on every
  refresh — failed on `main` with `missing catalog entries`. Found while registering the H1477
  data files; catalog now 66 files, check green.
- **`scan_target_audit.tsv` / §7 of `reports/pwg_scan_index.md` re-verified after the `rvps` mislink + TS./TBR. arity-gap fix (H1714).** `rvps` flips from `not wired at all` to `yes` (was silently mislinking Rgveda-Pratisakhya citations to an unrelated Rgveda hymn anchor); `taittiriyas`/`taittiriyabr` flip from `partial` to `yes` (3-parameter citations now resolve). `pancar` stays `partial` (2-param has no natural viewer target, confirmed not a gap) and `amara_col` stays `mis-keyed` but is now recorded as by-design (16,151 citations under bare `AK.` for the paired Deslongchamps edition, zero measured for Colebrooke under that key). Fixed in [gasyoun/SanskritLexicography#840](https://github.com/gasyoun/SanskritLexicography/pull/840); tracker counts now 35 wired / 1 partial / 1 mis-keyed / 0 unwired (was 32/3/1/1).
## [1.5.0] - 2026-07-27

### Added

- **The PWG literary-source scan-index campaign, committed as data (H1706).** The
  2025–2026 volunteer effort that page-indexed the printed editions PWG cites existed
  only as a live Google Sheet; nothing survived it being edited or unshared. Now snapshotted
  and derived under `data/pwg_scan_index_tracker/`: all four sheet tabs verbatim, an 82-row
  cross-validated registry (TSV + JSON), a ranked e-text candidate queue, and a dated audit
  of all 37 scan directories. Generator `scripts/pwg_scan_index.py` (stdlib-only offline;
  `--fetch` re-snapshots). Analysis in `reports/pwg_scan_index.md`, dashboard page at
  `/scan-index`, campaign history in `docs/PWG_SCAN_INDEX_CAMPAIGN_HISTORY_2025_2026.md`
  reconstructed from 40 PWG/PWK coordinating issues.
  **Headline:** 55 of 82 works indexed, carrying 73.7 % of the tracked citation mass across
  28,963 pages by 8 volunteers; 7 works unclaimed, 5 of them Vedic; median 12 days from
  index posted to scan public.
  **Three findings the data forced.** (1) The sheet's `Citation count` column has
  unresolved provenance — it reproduces neither the bare-string counts nor a rollup of the
  full-dictionary `<ls>` extraction, so it is used for ranking only and never as a share of
  a dictionary-wide denominator. (2) `rvps` (Ṛgveda-Prātiśākhya) is indexed but unwired, and
  worse than unwired: a Prātiśākhya citation currently resolves to an Ṛgveda *hymn* anchor.
  (3) The tracker spells one scan directory `rAjatar` where the canonical name is `rajatar`;
  GitHub Pages paths are case-sensitive, so links built from the tracker spelling 404.
  Executed by Opus 5 (`claude-opus-5`).

### Changed

- **E-text queue: `ramayanabom` re-annotated from "claimed" to "assessed and
  REJECTED".** H1705 closed the same day with a measured negative result — the
  Bombay uttarakāṇḍa has 111 sargas + 13 interpolated against the corpus's 100, and
  the corpus file carries 2,690 sa / 0 ru critical-edition text, so a Bombay
  concordance would have no consumer. The queue now says so, to stop a future
  session re-deriving a refuted conclusion.

## [1.4.0] - 2026-07-23

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

[Unreleased]: https://github.com/sanskrit-lexicon/csl-observatory/compare/v1.6.0...HEAD
[1.7.2]: https://github.com/sanskrit-lexicon/csl-observatory/compare/v1.7.1...v1.7.2
[1.7.1]: https://github.com/sanskrit-lexicon/csl-observatory/compare/v1.7.0...v1.7.1
[1.7.0]: https://github.com/sanskrit-lexicon/csl-observatory/compare/v1.6.0...v1.7.0
[1.6.0]: https://github.com/sanskrit-lexicon/csl-observatory/compare/v1.5.0...v1.6.0
[1.4.0]: https://github.com/sanskrit-lexicon/csl-observatory/compare/v1.3.0...v1.4.0
[1.1.0]: https://github.com/sanskrit-lexicon/csl-observatory/compare/v1.0.0...v1.1.0
[1.0.0]: https://github.com/sanskrit-lexicon/csl-observatory/compare/v0.1.0...v1.0.0
[0.1.0]: https://github.com/sanskrit-lexicon/csl-observatory/releases/tag/v0.1.0
