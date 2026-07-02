# Pending maintainer actions

_Created: 02-07-2026 · Last updated: 02-07-2026_

A short, shared worklist of open items across the Sanskrit Lexicon repos that
need a maintainer's review, merge, deploy, or decision. It is the merge/deploy
counterpart to [`CROSS_REPO_DECISIONS.md`](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/docs/CROSS_REPO_DECISIONS.md)
(scholarly/credential decisions) and the [`MAINTAINER_REVIEW_CHECKLIST.md`](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/docs/MAINTAINER_REVIEW_CHECKLIST.md).

States were verified live on 2026-07-02; merged/closed items are dropped as they
land. Nothing here is urgent-by-default — it is a convenience view so nothing
slips, not a queue anyone is blocked on.

## Open PRs awaiting review / merge

| PR | Fixes |
|---|---|
| [csl-orig #2867](https://github.com/sanskrit-lexicon/csl-orig/pull/2867) | LRV: add homonymy markers to duplicate `fjvI` entries |
| [csl-orig #2872](https://github.com/sanskrit-lexicon/csl-orig/pull/2872) | MW: restore parentheses in deletion markup for `akzara` L>592 (csl-websanlexicon #60) |
| [csl-orig #2874](https://github.com/sanskrit-lexicon/csl-orig/pull/2874) | BOR: move ellipsis outside Devanagari delimiters at L=11063 (fixes #606) |
| [csl-devanagari #45](https://github.com/sanskrit-lexicon/csl-devanagari/pull/45) | Preserve XML tags during Devanagari conversion (+ `/`→accent corruption in BOR/SKD/VCP); then regenerate `v02/` outputs server-side |
| [csl-app #47](https://github.com/sanskrit-lexicon/csl-app/pull/47) | Strip SLP1 accent markers when Vedic Accents is off |
| [csl-websanlexicon #74](https://github.com/sanskrit-lexicon/csl-websanlexicon/pull/74) | Templates: add `enterkeyhint=search` for the iOS virtual keyboard |

## Deploys / server-side

| Action | Where | Effect |
|---|---|---|
| Deploy images to `web/images/` on the server — the code path is already correct in `basicdisplay.php` | [csl-apidev #10](https://github.com/sanskrit-lexicon/csl-apidev/issues/10) | `<pic>` element display |
| Trigger [`csl-pywork/v02/redo_xampp_selective.sh`](https://github.com/sanskrit-lexicon/csl-pywork/blob/main/v02/redo_xampp_selective.sh) (server cron; can be run manually) — merged csl-orig fixes then propagate to Stardict / JSON / homepage | [csl-pywork](https://github.com/sanskrit-lexicon/csl-pywork) | public-artefact + tracking refresh |

## Decisions / proposals

| Item | Where | Ask |
|---|---|---|
| **Jachertz 1983 bibliography backfill** — resolve 37 of the 287 unresolved `pwbib_new` literary-source stubs from the newly-parsed Jachertz thesis | [PWK #128](https://github.com/sanskrit-lexicon/PWK/issues/128) · open PR [#127](https://github.com/sanskrit-lexicon/PWK/pull/127) | approve the 37 resolutions; confirm how a resolved title should be recorded in `pwbib_new.txt` (since `mergebibnew.txt` is generated); optionally schedule the AS-scheme normalizer + the never-deployed bibliography hyperlinks |

## Contributor identity

| Item | Where |
|---|---|
| Register ORCIDs for the named contributors (Funderburk, Patel, Gasūns, Rao, …) and identify the remaining unknown logins — needed for citable `CITATION.cff` metadata across repos | [csl-observatory #20](https://github.com/sanskrit-lexicon/csl-observatory/issues/20) |

## Longer-running (csl-apidev)

- Point [`init_word_frequency()`](https://github.com/sanskrit-lexicon/csl-apidev/blob/main/v1.1/getword_list_1.0_main.php) (v1.1) at [`wf1/wf.txt`](https://github.com/sanskrit-lexicon/csl-apidev/tree/main/wf1) — a one-line switch; the surrounding code is frozen, so it is the maintainer's to flip (Fix I, roadmap §12).
- Implement csl-apidev **v1.2 M1→M5** from [`simple-search/roadmap_v1.2.md`](https://github.com/sanskrit-lexicon/csl-apidev/blob/main/simple-search/roadmap_v1.2.md).
- Adopt cleanurl's dict-code in the [`Salt` rewrite](https://github.com/sanskrit-lexicon/Salt/blob/main/salt_entries.md) §1.7.

## Small cleanups

- Close [PWK #76](https://github.com/sanskrit-lexicon/PWK/issues/76) (typing of `pwk3_vn_page256-265`).
- Archive the disposable [`temp_corrections_ap90`](https://github.com/sanskrit-lexicon/temp_corrections_ap90) and [`temp_corrections_mw`](https://github.com/sanskrit-lexicon/temp_corrections_mw) repos (each still has one open scholarly-question issue).

_Dr. Mārcis Gasūns_
