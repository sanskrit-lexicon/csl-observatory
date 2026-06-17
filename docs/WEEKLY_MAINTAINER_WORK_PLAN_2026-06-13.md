# Weekly Maintainer Work Plan: Repository Decisions First

Date: 2026-06-13
Period: 2026-06-13 through 2026-06-19
Status: active weekly decision packet; no external repository mutations are
authorized by this file.

Main outcome: unblock repository-health decisions, especially RH1 license policy
and RH3 cleanup candidates. B3 metadata completeness was retried on 2026-06-13
and now has a complete live snapshot with no remaining `unknown` live fields.

## Week Decision Queue

| Priority | Item | Owner | Target day | Current status | Done when |
|---|---|---|---|---|---|
| 1 | Approve or revise RH1 license policy. | MG + Org | 2026-06-14 | blocked | Each repo group has an approved default or an explicit unresolved question. |
| 2 | Convert RH1 into rollout batches. | Codex | 2026-06-15 | ready for prep | Batch list separates safe code/tooling, dictionary data, mixed repos, infrastructure, and excluded archive candidates. |
| 3 | Decide RH3 cleanup candidates. | MG + Org | 2026-06-16 | blocked | Each candidate is `archive approved`, `retain`, `migrate issue first`, or `blocked with reason`. |
| 4 | Close out B3 metadata completeness. | Codex | 2026-06-17 | live snapshot complete | `repo_metadata.csv` has 76 rows, no fetch warnings, and no `unknown` live metadata fields. |
| 5 | Prepare next-week implementation packets. | Codex | 2026-06-18 | pending decisions | Approved license/archive work has a first implementation target and safety gates. |
| 6 | Friday review closeout. | MG + Codex | 2026-06-19 | pending | Roadmaps and decision queue reflect the week; checks pass. |

## Daily Operating Plan

### Sat Jun 13: Stabilize And Review Current State

- Treat the visualization and roadmap cleanup as the current checkpoint.
- Use `/ops-command`, `/repository-risk`, `/metadata-readiness`,
  `/taxonomy-triage`, and `/community-continuity` as the maintainer control
  surface.
- Update the week packet from `docs/REPOSITORY_HEALTH_DECISION_PACKET.md`,
  `docs/DECISIONS_NEEDED.md`, and
  `docs/METADATA_COMPLETENESS_DASHBOARD_PLAN.md`.

### Sun Jun 14: Decide RH1 License Policy

Decision defaults prepared for approval:

| Decision | Recommended default | Status |
|---|---|---|
| Code/tooling default | GPL-3.0 unless an existing recognized SPDX license is intentional. | MG/Org decision needed |
| Dictionary-data default | CC-BY-SA-4.0 or the organization-approved dictionary-data license. | MG/Org decision needed |
| Mixed code/data repos | Explicit split: code under GPL-3.0, data under approved data license. | MG/Org decision needed |
| Temporary/archive candidates | Exclude from license rollout until retain/archive is decided. | MG/Org decision needed |
| OBS-T released data | Keep CC-BY-4.0 separately from dictionary data. | already decided for `csl-observatory` |

### Mon Jun 15: RH1 Rollout Batches

Prepared non-mutating batches:

| Batch | Repositories | Next action |
|---|---|---|
| Safe code/tooling no-license | `avlinks`, `csl-apidev`, `csl-doc`, `csl-newsletter`, `hwnorm1`, `hwnorm2` | Apply code/tooling default only after RH1 approval. |
| Code/tooling NOASSERTION | `csl-pywork`, `csl-websanlexicon` | Replace ambiguous license text only after confirming current intent. |
| Dictionary data no-license | `ACC`, `ArabicInSanskrit`, `BEN`, `BHS`, `CAE`, `CCS`, `GreekInSanskrit`, `KNA`, `KOW`, `LRV`, `MCI`, `SHS`, `SKD`, `STC`, `VEI`, `WIL` | Apply approved dictionary-data license after RH1 approval. |
| Dictionary data NOASSERTION | `AP`, `ApteES`, `BOP`, `BOR`, `BUR`, `DCS`, `FRI`, `GRA`, `INM`, `MD`, `MW72`, `MWS`, `PWG`, `PWK`, `SCH`, `VCP`, `Wil-YAT` | Replace with canonical approved dictionary-data license after confirming existing intent. |
| Correction/source data | `CORRECTIONS`, `alternateheadwords`, `literarysource` | MG decides whether these inherit dictionary-data policy or need correction-data wording. |
| Mixed data/tooling | `MWinflect`, `mw-dev`, `csl-devanagari`, `csl-json`, `csl-ldev`, `csl-lnum`, `csl-lslink` | Use code/data split unless MG reclassifies a repo as pure code or pure data. |
| Infrastructure/web/content | `COLOGNE`, `csl-homepage`, `sanskrit-fonts`, `sanskrit-lexicon.github.io` | Special review before any license text changes. |
| Excluded until RH3 | `santamlegacy`, `temp_corrections_acc`, `temp_corrections_ae`, `temp_corrections_ap90`, `temp_corrections_mw`, `test_cologne_push` | Decide archive/retain first. |

### Tue Jun 16: RH3 Cleanup Candidates

Default safety rule: archive only after MG confirms the work was merged,
superseded, or intentionally preserved elsewhere.

| Repository | Prepared recommendation | Required MG decision |
|---|---|---|
| `santamlegacy` | Archive after confirming no current deployment depends on it. | archive approved / retain / blocked |
| `temp_corrections_acc` | Archive after confirming corrections were merged or superseded. | archive approved / retain / blocked |
| `temp_corrections_ae` | Archive after confirming corrections were merged or superseded. | archive approved / retain / blocked |
| `temp_corrections_ap90` | Migrate or close the open issue before archiving. | migrate issue first / retain / blocked |
| `temp_corrections_mw` | Migrate or close the open issue before archiving. | migrate issue first / retain / blocked |
| `test_cologne_push` | Archive after confirming server push testing no longer uses it. | archive approved / retain / blocked |

### Wed Jun 17: B3 Metadata Closeout

Live metadata was refreshed successfully on 2026-06-13:

| Metric | Before live retry | After live retry |
|---|---:|---:|
| Rows | 76 | 76 |
| Rows with fetch warnings | 53 | 0 |
| Unknown live fields | 347 | 0 |
| Rows with unknown tree metadata | 42 | 0 |
| Unknown release counts | 53 | 0 |
| README present | 34 | 75 |
| Citation present | 28 | 62 |
| Workflows present | 11 | 23 |
| Dependabot present | 8 | 18 |
| CodeQL present | 3 | 8 |

B3 moved from `active` to `done` after the site build, metadata row-set check,
and `/metadata-readiness` browser check passed.

### Thu Jun 18: Next Implementation Packets

Prepare but do not execute:

- License rollout packet for whichever RH1 batches MG/Org approves.
- Cleanup/archive execution checklist for whichever RH3 candidates MG approves.
- Metadata follow-up note for dashboard interpretation now that unknown blockers
  are gone.

### Fri Jun 19: Weekly Review Closeout

Use `docs/MAINTAINER_REVIEW_CHECKLIST.md` and record:

```text
Review date: 2026-06-19
Reports refreshed:
Decisions made:
Blocked decisions:
External repo changes approved:
Roadmap statuses changed:
Next implementation session:
```

## Checks For This Week

- `python scripts/repo_health_regression.py`
- `python scripts/site_visualization_smoke.py`
- Metadata row-set check: `repo_metadata.csv` must have the same 76 repos as
  `repos.csv`.
- `npm run build` in `observatory/site` after metadata or dashboard changes.
- `git diff --check -- docs observatory/site/src/data/repo_metadata.csv`

## Guardrails

- Do not archive repositories, commit licenses to external repos, rename
  branches, or open org-wide rollout PRs without explicit MG/Org approval.
- Keep archive candidates out of license rollout until RH3 is decided.
- Keep OBS-T paper work out of this week unless a regression fails.
