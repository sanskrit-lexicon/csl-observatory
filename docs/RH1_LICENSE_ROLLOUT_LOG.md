# RH1 License Rollout Log

Execution record for the RH1 license policy approved by MG on 2026-06-17
(see `REPOSITORY_HEALTH_DECISION_PACKET.md`). Tool: `scripts/rh1_apply_license.py`
(commits the canonical license text via the GitHub contents API; **never**
overwrites an existing LICENSE).

## Started 2026-06-17

### Batch 1 — code/tooling, no license → GPL-3.0 ✅ done

| Repo | Branch | Result |
|---|---|---|
| `csl-doc` | master | LICENSE @ `0ec8fb0e` — GitHub detects GPL-3.0 (pilot) |
| `avlinks` | master | LICENSE @ `a0b5260a` |
| `csl-apidev` | master | LICENSE @ `a57dad48` |
| `csl-newsletter` | main | LICENSE @ `2be6fc16` |
| `hwnorm1` | master | LICENSE @ `1687fdc4` |
| `hwnorm2` | master | LICENSE @ `0735a291` |

All six verified showing **GPL-3.0** on GitHub.

### Batch 2 — dictionary data, no license → CC-BY-SA-4.0 ✅ done

The repo-health audit was stale: 12 of the 16 listed repos already carried
CC-BY-SA-4.0 (from the earlier A3 work) and were skipped by the safety guard.
Only 4 were genuinely unlicensed:

| Repo | Branch | Result |
|---|---|---|
| `ArabicInSanskrit` | master | LICENSE @ `fd7726af` |
| `GreekInSanskrit` | master | LICENSE @ `bee87809` |
| `KNA` | main | LICENSE @ `134d98ae` |
| `KOW` | main | LICENSE @ `42bd29aa` |

All four verified showing **CC-BY-SA-4.0**. Already-licensed (skipped): `ACC`,
`BEN`, `BHS`, `CAE`, `CCS`, `LRV`, `MCI`, `SHS`, `SKD`, `STC`, `VEI`, `WIL`.

## Remaining batches — NOT yet executed (need a decision or careful handling)

| Batch | Repos | Why it's held |
|---|---|---|
| Code/tooling NOASSERTION | `csl-pywork`, `csl-websanlexicon` | Existing LICENSE text that GitHub can't map. Per policy, replace only after **confirming the current text's intent** — needs a per-repo look + go. |
| Dictionary-data NOASSERTION | `AP`, `ApteES`, `BOP`, `BOR`, `BUR`, `DCS`, `FRI`, `GRA`, `INM`, `MD`, `MW72`, `MWS`, `PWG`, `PWK`, `SCH`, `VCP`, `Wil-YAT` (+ source `csl-orig`) | Same — existing LICENSE text; confirm intent before replacing with canonical CC-BY-SA-4.0. |
| Correction/source data | `CORRECTIONS`, `alternateheadwords`, `literarysource` | MG must decide whether these inherit dictionary-data policy or need correction-data wording. |
| Mixed data/tooling | `MWinflect`, `mw-dev`, `csl-devanagari`, `csl-json`, `csl-ldev`, `csl-lnum`, `csl-lslink` | Need the dual-statement mechanism (code GPL-3.0 / data CC-BY-SA-4.0) decided + a README/LICENSE note design. |
| Infrastructure/web/content | `COLOGNE`, `csl-homepage`, `sanskrit-fonts`, `sanskrit-lexicon.github.io` | Special review before any license text change. |
| Excluded until RH3 | `santamlegacy`, `temp_corrections_*`, `test_cologne_push` | Excluded from licensing until the archive/retain decision is executed. |

## Note

The committed `repo_health.csv` snapshot predates this rollout, so the dashboard
still shows the pre-rollout license counts. A data refresh (`scripts/pull_data.py`
→ `repo_health.py`) will reconcile the numbers.
