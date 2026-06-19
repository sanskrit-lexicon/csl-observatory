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

### Batch 4 — MWS / Wil-YAT relicensed CC-BY-NC-SA-3.0+MIT → CC-BY-SA-4.0 ✅ done

These carried a deliberate dual license in `LICENSE.md`
(**data → CC-BY-NC-SA-3.0**, **code → MIT**). On **MG's explicit, informed
decision (2026-06-18)** to standardize and **drop the NonCommercial
restriction**, they were migrated to CC-BY-SA-4.0:

| Repo | Add canonical LICENSE | Delete old LICENSE.md | Verified |
|---|---|---|---|
| `MWS` | `bca2d700` | `99bc18e7` | CC-BY-SA-4.0, LICENSE.md gone |
| `Wil-YAT` | `d65414b8` | `2d1cd9a3` | CC-BY-SA-4.0, LICENSE.md gone |

### Batch 5 — mixed code+data ✅ done

The audit's "mixed" list (7 repos) wasn't uniform; `scripts/rh1_mixed_probe.py`
(language/byte composition) split it:

- **Pure data (no code detected) → single CC-BY-SA-4.0:** `csl-ldev` @ `06e561d4`,
  `csl-lnum` @ `3cd2a974`.
- **Genuinely mixed → dual layout** (MG-approved 2026-06-18): root `LICENSE` =
  CC-BY-SA-4.0 (GitHub-detected), `licenses/GPL-3.0.txt` = GPL-3.0 for source
  code, and a README "## License" section explaining the split. Applied to
  `MWinflect`, `mw-dev`, `csl-devanagari`, `csl-json`, `csl-lslink`
  (`scripts/rh1_apply_dual.py`). All five verified detecting **CC-BY-SA-4.0**.

**Layout gotcha (fixed):** the first attempt put the code license at root as
`LICENSE-CODE`, which collides with GitHub's `LICENSE*` detection glob and made
detection ambiguous (`mw-dev` mis-detected as GPL-3.0). Moving the code license
into `licenses/` (GitHub only scans the repo root) makes root `LICENSE` =
CC-BY-SA-4.0 detect cleanly. The stray root `LICENSE-CODE` files were deleted.

### Batch 6 — correction/source data → CC-BY-SA-4.0 ✅ done

On MG's decision (2026-06-19) to inherit the dictionary-data policy, all three
got a single canonical CC-BY-SA-4.0 LICENSE (clean adds — none had a license):

| Repo | Branch | Composition | Result |
|---|---|---|---|
| `CORRECTIONS` | master | HTML 99% (correction reports) | LICENSE @ `dae60975` — verified |
| `alternateheadwords` | master | **Python 99%** (code-heavy) | LICENSE @ `239094cd` — verified |
| `literarysource` | main | data | LICENSE @ `03027a24` — verified |

Note: `alternateheadwords` is 99% Python by language bytes — if MG would rather
treat its scripts under GPL-3.0, it can be switched to the dual layout (root
LICENSE=CC-BY-SA-4.0 + `licenses/GPL-3.0.txt`) like the mixed batch. Left as
single CC-BY-SA-4.0 per the explicit instruction.

## Remaining batches — NOT yet executed (need a decision or careful handling)

| Batch | Repos | Why it's held |
|---|---|---|
| Infrastructure/web/content | `COLOGNE`, `csl-homepage`, `sanskrit-fonts`, `sanskrit-lexicon.github.io` | Special review before any license text change (likely bundle third-party fonts/web assets with their own licenses). |
| Excluded until RH3 | `santamlegacy`, `temp_corrections_*`, `test_cologne_push` | Excluded from licensing until the archive/retain decision is executed. |

## Note

The committed `repo_health.csv` snapshot predates this rollout, so the dashboard
still shows the pre-rollout license counts. A data refresh (`scripts/pull_data.py`
→ `repo_health.py`) will reconcile the numbers.
