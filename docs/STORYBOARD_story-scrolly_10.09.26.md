# Storyboard — `/story` full scrollytelling upgrade «Thirteen years, one scroll»

_Created: 10-09-2026 · Last updated: 10-09-2026_

**Surface:** [csl-observatory `/story`](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/observatory/site/src/story.md)
(Observable Framework) · G5 in [OBSERVATORY_ROADMAP.md](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/docs/OBSERVATORY_ROADMAP.md) ·
**Template:** [SCROLLYTELLING_STORYBOARD_TEMPLATE.md](https://github.com/gasyoun/Uprava/blob/main/docs/SCROLLYTELLING_STORYBOARD_TEMPLATE.md)
**Status:** awaiting MG read. MG ruling 10-09-2026: **full scrolly** (sticky chart + steps).

## Goal

The page already tells the 13-year CDSL story as long-form with inline charts. Upgrade it to true
scrollytelling: one **sticky figure panel** that changes as the reader scrolls the narrative steps, so each
finding lands against its own chart. No new data derivation — every figure stays computed live from the
committed CSVs, and every number stays traceable (the A14 lesson).

## Constraints

1. **No new derivation** — feeds are the existing `observatory/site/src/data/*.csv` (13 files:
   `velocity_timeline`, `obs_t_timeline`, `issue_lifecycle_survival`, `issue_lifecycle_backlog`,
   `contributor_identity`, `repo_health`, `taxonomy_adoption`, `obs_t_summary.json`, `manifest.json`, …).
2. Observable Framework stack: keep pages as `src/*.md` with Plot; scrolly via a sticky container
   (Framework-native layout + IntersectionObserver) — no scrollama dependency unless justified in the PR.
3. Trust block per figure: source CSV link + n + snapshot date.
4. No-JS / reduced-motion: the existing long-form layout is the fallback — text complete, charts above/below.
5. Site has no analytics today; measurement is explicitly **“unmeasured — accepted”** (scholar site), not silent.
6. MG text-read gate for the rewritten narrative stays (GTD @DO — the original G5 gate is still open).

## Beats

| # | Beat / claim | Scroll trigger | Visual | Feed (committed) | Text | Fallback | Reduced motion | Analytics goal | QA check | Rights / PII | Owner |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 52,498 documented corrections over 13 years | hero enter | big number + timeline axis, 2014→2026 | `obs_t_summary.json`, `obs_t_timeline.csv` | 2 sentences | static hero + inline chart | static | unmeasured — accepted | number == `obs_t_summary.events` | GPL-3.0 data | build agent |
| 2 | 2014–16: the cfr form-correction era | step 1 | year bars grow (form era segment) | `obs_t_timeline.csv` | 2 sentences | inline chart | static | unmeasured | sums to same total as event dataset | GPL-3.0 | build agent |
| 3 | 2019: the git era begins | step 2 | velocity line, PR-era inflection | `velocity_timeline.csv` | 2 sentences | inline | static | unmeasured | first-PR date matches repo history | GPL-3.0 | build agent |
| 4 | 2021: volume peak, 11 authors | step 3 | per-year bars peak + author breadth dots | `obs_t_timeline.csv`, `contributor_identity.csv` | 2 sentences | inline | static | unmeasured | peak year == CSV max | GPL-3.0 | build agent |
| 5 | 2025: the correction wave (backlog 1,742) | step 4 | backlog area rises then falls to 913 | `issue_lifecycle_backlog.csv` | 2 sentences | inline | static | unmeasured | both numbers == CSV | GPL-3.0 | build agent |
| 6 | 2026: taxonomy + observatory era (63 %) | step 5 | conformance line + taxonomy adoption | `taxonomy_adoption.csv` | 2 sentences | inline | static | unmeasured | % == CSV | GPL-3.0 | build agent |
| 7 | Standing findings as turns: bus factor 51.8 % · 178 silent · survival ~45 % · licensing 41→6 | step 6, sticky swaps figure | four small charts, one per finding | `contributor_identity.csv`, `issue_lifecycle_survival.csv`, `repo_health.csv` | one sentence each | four inline charts | static | unmeasured | each number == cited CSV | GPL-3.0 | build agent |
| 8 | Where a new contributor starts | closing step | onboarding links block | static links | 2 sentences | links | static | unmeasured | links 200 | none | build agent |

## Mechanics

1. Sticky figure panel: one container with all figures stacked; step observer toggles the active figure.
2. Chapter rail (progress) as a progressive enhancement; hidden under reduced motion.
3. Build: `npm run build` clean; site smoke script PAGES list unchanged (page path stays `/story`).
4. PR to `sanskrit-lexicon/csl-observatory`; merge when green per repo practice.

## QA

1. Build clean + smoke green; plot count unchanged or higher.
2. Every trust block resolves to a committed CSV; numbers re-derived from CSVs (spot-check 3).
3. Screenshots desktop + 390 px mobile; no-JS pass (figures still visible).
4. MG narrative read (G5 text gate) recorded before merge.

## Gates

1. **MG storyboard read** — this file.
2. **MG narrative text read** — original G5 gate, still open in GTD.
3. No new data derivation; PR only, no direct push to `main`.

## Out of scope

New metrics, API-gated analyses, site analytics installation (explicitly accepted as unmeasured).

_Dr. Mārcis Gasūns_
