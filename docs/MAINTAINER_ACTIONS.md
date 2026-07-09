# Pending maintainer actions

_Created: 02-07-2026 · Last updated: 09-07-2026_

A short, shared worklist of open items across the Sanskrit Lexicon repos that
need a maintainer's review, merge, deploy, or decision. It is the merge/deploy
counterpart to [`CROSS_REPO_DECISIONS.md`](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/docs/CROSS_REPO_DECISIONS.md)
(scholarly/credential decisions) and the [`MAINTAINER_REVIEW_CHECKLIST.md`](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/docs/MAINTAINER_REVIEW_CHECKLIST.md).

States were re-verified live on 2026-07-09; merged/closed items are dropped as
they land. Nothing here is urgent-by-default — it is a convenience view so
nothing slips, not a queue anyone is blocked on.

## Open PRs awaiting review / merge

| PR | Fixes |
|---|---|
| [csl-orig #2863](https://github.com/sanskrit-lexicon/csl-orig/pull/2863) | csl-orig batch fix (see PR for detail) |
| [csl-orig #2865](https://github.com/sanskrit-lexicon/csl-orig/pull/2865) | csl-orig batch fix (see PR for detail) |
| [csl-orig #2867](https://github.com/sanskrit-lexicon/csl-orig/pull/2867) | LRV: add homonymy markers to duplicate `fjvI` entries |
| [csl-orig #2872](https://github.com/sanskrit-lexicon/csl-orig/pull/2872) | MW: restore parentheses in deletion markup for `akzara` L>592 (csl-websanlexicon #60) |
| [csl-orig #2874](https://github.com/sanskrit-lexicon/csl-orig/pull/2874) | BOR: move ellipsis outside Devanagari delimiters at L=11063 (fixes #606) |

_Dropped since 03-07: [csl-devanagari #45](https://github.com/sanskrit-lexicon/csl-devanagari/pull/45) — MERGED 03-07-2026.
[csl-app #47](https://github.com/sanskrit-lexicon/csl-app/pull/47) and [csl-websanlexicon #74](https://github.com/sanskrit-lexicon/csl-websanlexicon/pull/74) — both CLOSED (not merged); flagged internally as conflicting with in-flight work, ours to re-apply, not a maintainer merge._

## Deploys / server-side

| Action | Where | Effect |
|---|---|---|
| Deploy images to `web/images/` on the server — the code path is already correct in `basicdisplay.php` | [csl-apidev #10](https://github.com/sanskrit-lexicon/csl-apidev/issues/10) | `<pic>` element display |
| Trigger [`csl-pywork/v02/redo_xampp_selective.sh`](https://github.com/sanskrit-lexicon/csl-pywork/blob/main/v02/redo_xampp_selective.sh) (server cron; can be run manually) — merged csl-orig fixes then propagate to Stardict / JSON / homepage | [csl-pywork](https://github.com/sanskrit-lexicon/csl-pywork) | public-artefact + tracking refresh |
| If `AllowOverride` is off under `/scans`: add the static-asset `Cache-Control`/`mod_expires` block to httpd.conf instead of the queued template `.htaccess` — the biggest measured page-speed win (audit D1) | [PERFORMANCE_AUDIT_2026-07.md](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/docs/PERFORMANCE_AUDIT_2026-07.md) | repeat visits stop revalidating every asset at a full RTT |

## Decisions / proposals

| Item | Where | Ask |
|---|---|---|
| **CDN in front of sanskrit-lexicon.uni-koeln.de** — would cut the ~0.6 s cold-connection RTT for the India/US audience (audit D5); **costs money**, so parked: needs funding plus a University of Cologne infrastructure decision, not a code change | [PERFORMANCE_AUDIT_2026-07.md](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/docs/PERFORMANCE_AUDIT_2026-07.md) | none unless funding appears — listed so the option isn't re-derived |
| **Jachertz 1983 bibliography backfill** — the proposal PR [#127](https://github.com/sanskrit-lexicon/PWK/pull/127) is CLOSED, superseded by [PWK #129](https://github.com/sanskrit-lexicon/PWK/pull/129) (MERGED). Still open per [PWK #128](https://github.com/sanskrit-lexicon/PWK/issues/128): confirm how a resolved title is recorded in `pwbib_new.txt` going forward, and schedule the AS-scheme normalizer + the never-deployed bibliography hyperlinks | [PWK #128](https://github.com/sanskrit-lexicon/PWK/issues/128) | decide the recording convention; schedule the two follow-on deploys |

## Contributor identity

| Item | Where |
|---|---|
| Register ORCIDs for the named contributors (Funderburk, Patel, Gasūns, Rao, …) and identify the remaining unknown logins — needed for citable `CITATION.cff` metadata across repos | [csl-observatory #20](https://github.com/sanskrit-lexicon/csl-observatory/issues/20) |

## Andhrabharati

- [csl-orig #1788](https://github.com/sanskrit-lexicon/csl-orig/issues/1788) — MW `sup`→`rev`, awaiting confirmation.
- SKD #13, lines 42288 / 54089 / 92343 — editorial judgment call.
- [MWS #217](https://github.com/sanskrit-lexicon/MWS/issues/217) — adjudication, jointly with @funderburkjim (unblocks SPEC-5 §1).
- csl-ldev #11 (SKD scanned-print variant) and PWK #12 (bracket form) — maintainer sign-off.

## Longer-running (csl-apidev)

- Point [`init_word_frequency()`](https://github.com/sanskrit-lexicon/csl-apidev/blob/main/v1.1/getword_list_1.0_main.php) (v1.1) at [`wf1/wf.txt`](https://github.com/sanskrit-lexicon/csl-apidev/tree/main/wf1) — a one-line switch; the surrounding code is frozen, so it is the maintainer's to flip (Fix I, roadmap §12).
- Implement csl-apidev **v1.2 M1→M5** from [`simple-search/roadmap_v1.2.md`](https://github.com/sanskrit-lexicon/csl-apidev/blob/main/simple-search/roadmap_v1.2.md).
- Adopt cleanurl's dict-code in the [`Salt` rewrite](https://github.com/sanskrit-lexicon/Salt/blob/main/salt_entries.md) §1.7.

## Small cleanups

- Close [PWK #76](https://github.com/sanskrit-lexicon/PWK/issues/76) (typing of `pwk3_vn_page256-265`).
- Archive the disposable [`temp_corrections_ap90`](https://github.com/sanskrit-lexicon/temp_corrections_ap90) and [`temp_corrections_mw`](https://github.com/sanskrit-lexicon/temp_corrections_mw) repos (each still has one open scholarly-question issue).

_Dr. Mārcis Gasūns_
