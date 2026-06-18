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

### Batch 3 — NOASSERTION resolution (existing LICENSE text confirmed, then replaced) ✅ done

The repo-health audit lumped 20 repos under "NOASSERTION", but a retried live
check (`scripts/rh1_state.py`) + content inspection
(`scripts/rh1_inspect_noassertion.py`) showed five distinct situations. Each
was content-confirmed before any overwrite (the "confirm intent" rule).

- **Already canonical, GitHub already detects them (skipped, 8):** `MW72`,
  `ApteES`, `BOR`, `BUR`, `INM`, `SCH`, `VCP`, `BOP` — all CC-BY-SA-4.0. (Their
  full-legalcode text is detected fine; they were never broken.)
- **CC-BY-SA-4.0 deed only (1 KB summary) → replaced with canonical legalcode:**
  `AP` @ `8c21eba1`, `DCS` @ `35bf993f`, `FRI` @ `ae62f0d4`, `GRA` @ `b8353d15`,
  `PWG` @ `beece2f0`, `PWK` @ `b510a055`, `MD` @ `7882ab42`. All verified CC-BY-SA-4.0.
- **GPL-3.0 stub (739 B notice) → replaced with canonical GPL-3.0:**
  `csl-pywork` @ `2f445127`, `csl-websanlexicon` @ `5471e0d8`. Verified GPL-3.0.
- **`csl-orig`** (source-data aggregate, was a GPL-3.0 stub) → **CC-BY-SA-4.0**
  per MG's data-policy choice, @ `79b29bc5`. Verified.

### ⚠️ Held — MWS and Wil-YAT carry a DIFFERENT, intentional license

Their `LICENSE.md` is a deliberate dual statement:
**data → CC-BY-NC-SA-3.0** (NonCommercial) and **code → MIT**. Migrating them to
CC-BY-SA-4.0 would *drop the NonCommercial restriction* — a real relicensing
decision, not a detection fix. **Not touched; awaiting an explicit MG decision.**

## Remaining batches — NOT yet executed (need a decision or careful handling)

| Batch | Repos | Why it's held |
|---|---|---|
| **MWS, Wil-YAT** | `MWS`, `Wil-YAT` | Intentional **CC-BY-NC-SA-3.0 (data) + MIT (code)**. Decide whether to keep, or migrate to CC-BY-SA-4.0 (drops NonCommercial). |
| Correction/source data | `CORRECTIONS`, `alternateheadwords`, `literarysource` | MG must decide whether these inherit dictionary-data policy or need correction-data wording. |
| Mixed data/tooling | `MWinflect`, `mw-dev`, `csl-devanagari`, `csl-json`, `csl-ldev`, `csl-lnum`, `csl-lslink` | Need the dual-statement mechanism (code GPL-3.0 / data CC-BY-SA-4.0) decided + a README/LICENSE note design. |
| Infrastructure/web/content | `COLOGNE`, `csl-homepage`, `sanskrit-fonts`, `sanskrit-lexicon.github.io` | Special review before any license text change. |
| Excluded until RH3 | `santamlegacy`, `temp_corrections_*`, `test_cologne_push` | Excluded from licensing until the archive/retain decision is executed. |

## Note

The committed `repo_health.csv` snapshot predates this rollout, so the dashboard
still shows the pre-rollout license counts. A data refresh (`scripts/pull_data.py`
→ `repo_health.py`) will reconcile the numbers.
