# Decisions Needed From The Maintainer

Consolidated list of items that are blocked on a human decision,
credential, or action. This file is now scoped to `csl-observatory` as
the GitHub/org observatory only.

Last updated: 2026-06-03.

> Agent note: when M.G. asks "what's next?" or resumes observatory work,
> surface this list first.

---

## Open Observatory Items

### B. Identifications / Facts Only You Can Confirm

| # | Item | Source |
|---|---|---|
| B2 | Verify bibliography filled for the 6 documented repos, especially BUR (Leupol / Maisonneuve) and BOP (1847 edition). | Handoff full-runbook gaps |

### C. Credentials / Access Needed

Deferred: none available now, per M.G. 2026-05-31.

| # | Need | For |
|---|---|---|
| C1 | GitHub token with workflow + `read:project` scope as a repo secret. | Automate observatory refresh; tooling-roadmap audit |
| C2 | Cologne server access for `redo_xampp_selective.sh`, if the observatory is asked to track the repository/process side of public artifact refreshes. | Public artifact refresh as repository/process evidence |
| C3 | DNS for `observatory.sanskrit-lexicon.org` plus Cologne `uni-koeln.de/observatory` handover. | Observatory mirrors |

### D. Confirmations

| # | Item | Status |
|---|---|---|
| D1 | A Cologne admin will run, or let the cron run, `redo_xampp_selective.sh` so the 2026-05 `csl-orig` fixes propagate to Stardict/JSON/homepage. | Awaiting Cologne admin; not M.G.'s action |

---

## Recently Resolved Observatory Items

| # | Resolution | Documented in |
|---|---|---|
| A2 | Taxonomy rollout done: 24 dictionary repos (786 issues) plus 4 tooling repos (153 issues), all verified clean. | `SESSION_HANDOFF.md`; `csl-corrections/.ai_state.md` |
| A1 | KRM license set to CC-BY-SA-4.0; full legalcode replaced the GPL text. | KRM `LICENSE` |
| A3 | Full CC-BY-SA-4.0 legalcode applied to 21 repos; GitHub now auto-detects the license. | `*/LICENSE` |
| B3 | `.github/ISSUE_TEMPLATE/*.yml` plus `PULL_REQUEST_TEMPLATE.md` pushed to BOR/BUR/INM/KRM/BOP/MW72. | `csl-corrections/.ai_state.md`; previous handoff |
| B4 | SHS author confirmed as Kulapati Jibananda Vidyasagara. | SHS README/CLAUDE; M3 docs |
| B5 | ApteES reverse-direction English-to-Sanskrit docs built. | ApteES README/CLAUDE; M3 docs |
| D2 | Approved M1 refresh-script modernization as a backward-compatible refactor. | `docs/ROADMAP.md`; `csl-pywork#53` |
| D3 | Approved wiring the full `make_xml` XML-parse check into CI. | `csl-pywork#51` |

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
