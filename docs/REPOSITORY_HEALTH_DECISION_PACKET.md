# Repository Health Decision Packet

Date: 2026-06-13 (RH1 + RH3 approved 2026-06-17)
Status: **RH1 license policy and RH3 archive list APPROVED by MG on 2026-06-17.**
**RH1 rollout COMPLETE (2026-06-19)** except the RH3-excluded repos — see
`docs/RH1_LICENSE_ROLLOUT_LOG.md` (~36 repos licensed across 7 batches).
**RH3 archiving STARTED 2026-06-19**: `santamlegacy`, `temp_corrections_acc`,
`temp_corrections_ae`, `test_cologne_push` are **archived** (verified, via
`scripts/rh3_archive.py`). `temp_corrections_ap90` and `temp_corrections_mw`
remain **NOT archived** — each has one open, *active* scholarly-question issue
(ap90 #2 is a 25-comment thread authored by funderburkjim). **MG decision
(2026-06-19): left for funderburkjim** — as the thread author and lead
maintainer he migrates/closes the issues, after which these two can be archived
(`scripts/rh3_archive.py` blocks on open issues, so just re-run it once clear).

This packet prepares the first maintainer decisions from the one-year roadmap:

- RH1: decide license policy for code/data/dictionary repositories.
- RH3: decide whether six cleanup candidates should be archived or retained.

Use this as the review sheet before applying licenses, archiving repositories, or
opening follow-up pull requests. Anything marked "blocked" needs maintainer or
organization approval first.

The active week-level decision queue and rollout batches are in
`docs/WEEKLY_MAINTAINER_WORK_PLAN_2026-06-13.md`.

## 1. License Decision Matrix

### Recommended Policy To Approve

| Repo group | Proposed default | Status | Notes |
|---|---|---|---|
| Code and tooling | GPL-3.0 unless an existing recognized SPDX license is intentionally different. | approved 2026-06-17 | Matches several existing tooling repos; do not overwrite MIT/LGPL/GPL-2.0 without a separate decision. |
| Dictionary data repositories | CC-BY-SA-4.0 or the organization-approved dictionary-data license. | approved 2026-06-17 | Confirm this with the maintainers before adding any license text. |
| Mixed code + dictionary data | Dual statement: code under GPL-3.0, data under the approved dictionary-data license. | approved 2026-06-17 | Requires a short README/LICENSE note so GitHub and humans do not conflate code and data rights. |
| Infrastructure and websites | GPL-3.0 for code; content/data assets under the approved data/content license when separable. | approved 2026-06-17 | Handle `COLOGNE`, `csl-homepage`, and `sanskrit-lexicon.github.io` carefully. |
| Archive/legacy/temporary repos | Decide archive/retain first; if retained, apply the policy for its actual repo group. | approved 2026-06-17 | Do not add licenses to disposable repos before the archive decision. |
| OBS-T released data | CC-BY-4.0. | decided for `csl-observatory` only | Implemented in `DATA_LICENSE.md`; does not decide dictionary data licensing. |

Default safety rule: do not make a repository license change unless the repo group
and license text have been explicitly approved.

### No-License Repositories By Proposed Group

These 41 repositories currently have no license in `reports/repo_health.md`.

| Proposed group | Repositories | Proposed action |
|---|---|---|
| Dictionary data | `ACC`, `ArabicInSanskrit`, `BEN`, `BHS`, `CAE`, `CCS`, `GreekInSanskrit`, `KNA`, `KOW`, `LRV`, `MCI`, `SHS`, `SKD`, `STC`, `VEI`, `WIL` | Apply approved dictionary-data license after RH1 approval. |
| Correction/source data | `CORRECTIONS`, `alternateheadwords`, `literarysource` | Decide whether these inherit dictionary-data policy or need a correction-data note. |
| Mixed data/tooling | `MWinflect`, `mw-dev`, `csl-devanagari`, `csl-json`, `csl-ldev`, `csl-lnum`, `csl-lslink` | Use dual code/data statement unless maintainer classifies as pure code or pure data. |
| Code/tooling | `csl-apidev`, `csl-doc`, `csl-newsletter`, `hwnorm1`, `hwnorm2`, `avlinks` | Apply code/tooling default after approval. |
| Infrastructure/web/content | `csl-homepage`, `sanskrit-fonts`, `sanskrit-lexicon.github.io` | Confirm whether code/content/data assets need split licensing. |
| Archive/temporary candidates | `santamlegacy`, `temp_corrections_acc`, `temp_corrections_ae`, `temp_corrections_ap90`, `temp_corrections_mw`, `test_cologne_push` | Decide archive/retain first; do not license before that. |

### NOASSERTION Repositories By Proposed Group

These 21 repositories have a `LICENSE` file that GitHub cannot map to an SPDX id.

| Proposed group | Repositories | Proposed action |
|---|---|---|
| Dictionary data | `AP`, `ApteES`, `BOP`, `BOR`, `BUR`, `DCS`, `FRI`, `GRA`, `INM`, `MD`, `MW72`, `MWS`, `PWG`, `PWK`, `SCH`, `VCP`, `Wil-YAT` | Replace with canonical approved dictionary-data license only after confirming the existing text's intent. |
| Source aggregate | `csl-orig` | Likely needs dictionary-data or mixed-source policy; decide explicitly. |
| Code/tooling | `csl-pywork`, `csl-websanlexicon` | Replace with canonical code/tooling license only after confirming intent. |
| Infrastructure/web | `COLOGNE` | Confirm whether it is code, content, data, or mixed before changing license text. |

### Decision Questions For Maintainer

| ID | Decision needed | Recommended default |
|---|---|---|
| RH1-L1 | Should code/tooling default to GPL-3.0? | Yes, unless a repo already has an intentional recognized SPDX license. |
| RH1-L2 | Should dictionary data default to CC-BY-SA-4.0? | Yes, if the organization confirms this is the intended CDSL data license. |
| RH1-L3 | Should mixed repos get an explicit code/data split? | Yes. |
| RH1-L4 | Should temporary/archive candidates be excluded from the license rollout until archived/retained? | Yes. |
| RH1-L5 | Should OBS-T data remain CC-BY-4.0 separately from dictionary data? | Yes; this is already implemented for `csl-observatory`. |

## 2. Cleanup-Candidate Decisions

Source evidence: `reports/repo_health.md` and `observatory/site/src/data/repos.csv`.

Default safety rule: archive only after the maintainer confirms the work was
merged, superseded, or intentionally preserved elsewhere. Archiving is reversible
but makes the repository read-only.

| Repository | Evidence | Likely purpose | Recommendation | Status |
|---|---|---|---|---|
| `santamlegacy` | 0 open issues; pushed 20 days before the 2026-06-05 audit; description says "php version of Cologne-"; size 0 KB. | Legacy PHP snapshot. | Archive after confirming no current deployment depends on it. | approved 2026-06-17 |
| `temp_corrections_acc` | 0 open issues; pushed 21 days before audit; description says temporary English-word corrections for ACC. | Temporary correction batch. | Archive after confirming corrections were merged or superseded. | approved 2026-06-17 |
| `temp_corrections_ae` | 0 open issues; pushed 21 days before audit; description says temporary Apte English-Sanskrit corrections. | Temporary correction batch. | Archive after confirming corrections were merged or superseded. | approved 2026-06-17 |
| `temp_corrections_ap90` | 1 open issue; pushed 21 days before audit; description says working repository for analyzing AP90 correction batch; Python present. | Temporary analysis repo with one unresolved item. | Review/close or migrate the open issue, then archive if superseded. | approved 2026-06-17 |
| `temp_corrections_mw` | 1 open issue; pushed 21 days before audit; description says MW dictionary digitization corrections. | Temporary correction batch with one unresolved item. | Review/close or migrate the open issue, then archive if superseded. | approved 2026-06-17 |
| `test_cologne_push` | 0 open issues; pushed 20 days before audit; description says temporary push-from-Cologne-server problem; size 2 KB. | Push/deployment test repo. | Archive after confirming the server push problem is no longer being tested here. | approved 2026-06-17 |

### Decision Questions For Maintainer

| ID | Decision needed | Recommended default |
|---|---|---|
| RH3-A1 | Can `santamlegacy` be archived? | Yes, after dependency check. |
| RH3-A2 | Can `temp_corrections_acc` and `temp_corrections_ae` be archived? | Yes, after merge/superseded confirmation. |
| RH3-A3 | Should the two open issues in `temp_corrections_ap90` and `temp_corrections_mw` be migrated or closed before archiving? | Yes. |
| RH3-A4 | Can `test_cologne_push` be archived? | Yes, after confirming no active server test uses it. |

## 3. What To Do After Approval

After RH1 and RH3 are approved:

1. Update `docs/DECISIONS_NEEDED.md` with the chosen license and archive decisions.
2. File or update tracking issues for the approved license rollout and cleanup work.
3. Apply archive changes only through GitHub after maintainer approval.
4. Apply license changes only to approved repo groups, with separate commits/PRs per sensible batch.
5. Re-run `python scripts/repo_health.py` and update roadmap statuses.

No external repository mutation is authorized by this packet alone.
