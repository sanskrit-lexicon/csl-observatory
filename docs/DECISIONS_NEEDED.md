# Decisions Needed From The Maintainer

Consolidated list of items that are blocked on a human decision,
credential, or action. This file is now scoped to `csl-observatory` as
the GitHub/org observatory only.

Last updated: 2026-06-17.

> Agent note: when M.G. asks "what's next?" or resumes observatory work,
> surface this list first.
>
> **Org-wide view:** for pending decisions across *all* Sanskrit Lexicon
> repos (not just the observatory), see the master index
> [`CROSS_REPO_DECISIONS.md`](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/docs/CROSS_REPO_DECISIONS.md).

---

## Open Observatory Items

### A. Repository Health / Roadmap Decisions

| # | Item | Source |
|---|---|---|
| A7 | Review the bus-factor accepted-risk notes for `DCS`, `KNA`, `KOW`, `MCI`, and `santamlegacy`; confirm whether public artifact tooling should be promoted next. | `BUS_FACTOR_ACTION_PLAN.md` SC3 |

> **A4/A5 approved 2026-06-17 — see Recently Resolved.** The license policy and
> archive list are now decided; remaining work is the gated *rollout* (filing
> tracking issues, adding LICENSE text per group, archiving repos on GitHub),
> which is an external-mutation batch and runs only on an explicit "go".

### B. Identifications / Facts Only You Can Confirm

| # | Item | Source |
|---|---|---|
| B2 | Verify bibliography filled for the 6 documented repos, especially BUR (Leupol / Maisonneuve) and BOP (1847 edition). | Handoff full-runbook gaps |

### C. Credentials / Access Needed

Local `gh auth status` and `gh api` worked on 2026-06-13 as account `gasyoun`.
Longer-lived CI or repo-secret credentials are still needed for scheduled
automation and project-board audits.

| # | Need | For |
|---|---|---|
| C1 | GitHub token/CLI auth with workflow + `read:project` scope as a repo secret or durable local credential. | Automate observatory refresh; tooling-roadmap audit; **dictionary drift-watch audit** (`dict-audit.yml`, see [DRIFT_WATCH.md](DRIFT_WATCH.md)); B3 live metadata fetch now works locally but should not depend on an interactive session. |
| C2 | Cologne server access for `redo_xampp_selective.sh`, if the observatory is asked to track the repository/process side of public artifact refreshes. | Public artifact refresh as repository/process evidence |
| C3 | DNS for `observatory.sanskrit-lexicon.org` plus Cologne `uni-koeln.de/observatory` handover. | Observatory mirrors |

### D. Confirmations

| # | Item | Status |
|---|---|---|
| D1 | A Cologne admin will run, or let the cron run, `redo_xampp_selective.sh` so the 2026-05 `csl-orig` fixes propagate to Stardict/JSON/homepage. | Awaiting Cologne admin; not M.G.'s action |
| D4 | **Taxonomy drift watch** ([DRIFT_WATCH.md](DRIFT_WATCH.md)): OK to (a) enable the weekly `dict-audit.yml` backstop now (reuses `TOOLING_AUDIT_TOKEN`), and (b) pilot the event-driven `needs-triage` guard on `GRA` before fanning out to all repos? | Awaiting M.G. decision |

---

## Recently Resolved Observatory Items

| # | Resolution | Documented in |
|---|---|---|
| A2 | Taxonomy rollout done: 24 dictionary repos (786 issues) plus 4 tooling repos (153 issues), all verified clean. | `SESSION_HANDOFF.md`; `csl-corrections/.ai_state.md` |
| A1 | KRM license set to CC-BY-SA-4.0; full legalcode replaced the GPL text. | KRM `LICENSE` |
| A3 | Full CC-BY-SA-4.0 legalcode applied to 21 repos; GitHub now auto-detects the license. | `*/LICENSE` |
| B3 | `.github/ISSUE_TEMPLATE/*.yml` plus `PULL_REQUEST_TEMPLATE.md` pushed to BOR/BUR/INM/KRM/BOP/MW72, then extended 03-07-2026 to BEN/BHS/CAE/CCS/LRV/MCI/SHS/SKD/STC/VEI/WIL (17 dict repos total). | `csl-corrections/.ai_state.md`; previous handoff; [H126](https://github.com/gasyoun/Uprava/blob/main/handoffs/archive/H126-Sonnet_Uprava_dict_issue_templates_rollout_03.07.26.md) |
| B4 | SHS author confirmed as Kulapati Jibananda Vidyasagara. | SHS README/CLAUDE; M3 docs |
| B5 | ApteES reverse-direction English-to-Sanskrit docs built. | ApteES README/CLAUDE; M3 docs |
| D2 | Approved M1 refresh-script modernization as a backward-compatible refactor. | `docs/ROADMAP.md`; `csl-pywork#53` |
| D3 | Approved wiring the full `make_xml` XML-parse check into CI. | `csl-pywork#51` |
| A6 | Monthly maintainer review cadence created: last Friday/month-end review with roadmap status updates and decision-queue output. | `MAINTAINER_REVIEW_CHECKLIST.md` |
| SC2 | Maintainer continuity packet created for observatory refresh, correction reports, OBS-T regeneration, dashboard build, and failure handoff. | `MAINTAINER_CONTINUITY_PACKET.md` |
| SC4 | AI contribution policy linked from README and CONTRIBUTING; contributor guidance now states the low-noise bot/AI expectations. | `AI_CONTRIBUTION_POLICY.md` |
| SC5 | Contributor entry path created with setup, safe first tasks, taxonomy labels, review expectations, and out-of-scope warnings. | `CONTRIBUTOR_ENTRY_PATH.md` |
| AR2 | Local workspace checker added for `csl-observatory`, `csl-orig`, and `CORRECTIONS`; current workspace passes with dirty/shallow warnings. | `scripts/check_workspace.py` |
| B4 | Repository-health regression check added for generated CSV schemas, static flags, cleanup candidates, sort order, and report headline consistency. | `scripts/repo_health_regression.py` |
| B1/B2 | Repo Health dashboard now exposes license backlog queues and cleanup-candidate blockers with links to the tracking issues and decision packet. | `observatory/site/src/repo-health.md` |
| D2 | Refresh-script modernization plan written for `redo_xampp_selective.sh`: Python 3 driver, dry-run, parameterized paths, manifests, preflight, and deployment gates. | `REFRESH_SCRIPT_MODERNIZATION_PLAN.md` |
| B3-plan | Metadata-completeness dashboard plan, cached fetcher, partial live CSV, and Repo Metadata page created. | `METADATA_COMPLETENESS_DASHBOARD_PLAN.md`; `observatory/site/src/repo-metadata.md` |
| B3-live | Live repository metadata snapshot completed locally: 76 rows, 0 fetch warnings, 0 unknown live fields. | `METADATA_COMPLETENESS_DASHBOARD_PLAN.md`; `observatory/site/src/data/repo_metadata.csv`; `WEEKLY_MAINTAINER_WORK_PLAN_2026-06-13.md` |
| RH4-pilot | `csl-observatory` line-ending policy tightened to explicit LF for source, docs, and generated data files; org-wide rollout remains active. | `.gitattributes` |
| A4 (RH1) | License policy **approved 2026-06-17**: code/tooling → **GPL-3.0** (don't overwrite an intentional recognized SPDX license); dictionary data → **CC-BY-SA-4.0**; mixed repos → **dual split** (code GPL-3.0 / data CC-BY-SA-4.0); temp/archive candidates **excluded** until RH3 executed; OBS-T data stays CC-BY-4.0. | `REPOSITORY_HEALTH_DECISION_PACKET.md` RH1 |
| A5 (RH3) | Archive **approved 2026-06-17**: `santamlegacy`, `temp_corrections_acc`, `temp_corrections_ae`, `test_cologne_push` → archive after the standard dependency/merge confirmation; `temp_corrections_ap90`, `temp_corrections_mw` → archive **only after** their one open issue is migrated or closed. | `REPOSITORY_HEALTH_DECISION_PACKET.md` RH3 |

---

## Moved Out Of Observatory

Dictionary-structure and dictionary-evidence decisions now live in
`csl-atlas`. The preserved legacy copy is:

- `csl-atlas/docs/DECISIONS_NEEDED_LEGACY_OBSERVATORY.md`

This includes the former A6/A7/A8 research decisions, L0/Post-L0
decisions, R2 sense-splitter decisions, Patel convention work,
dictionary genealogy, and microstructure/macrostructure work.

Standards/export decisions belong in `csl-standards`. DCS/corpus decisions
belong in `VisualDCS` or a future grammar/corpus repository, not here.
Matomo/top-entry analytics, backlinks, and broad publication schedules are
also outside the active observatory boundary until a new human decision gives
them a home.
