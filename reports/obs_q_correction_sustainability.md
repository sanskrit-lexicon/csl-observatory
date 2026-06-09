# Correction sustainability & the data-layer bus factor (OBS-Q)

_Read-only probes over `../csl-orig` git history (1,981 commits, 2019–2026) and
the `csl-corrections` GitHub issue API, 2026-06-10. Author identities alias-merged
via `scripts/contributors_map.json`. Reproduction commands at the foot of this
file._

> **Claim (reframed after measurement).** Correction throughput in the CDSL data
> layer is *single-person-burst-driven, not crew-size-driven* — so the dictionary
> **data** (not just the code) is bus-factor-fragile. The pipeline is *responsive*
> when staffed (median fix 6 days) but its **capacity** rests on one or two people,
> and a long tail of low-severity work is never reached.

This finding sits beside the org-wide [`bus_factor.md`](bus_factor.md) (code
contributions) and extends it to **content corrections** — the actual edits to
dictionary source text in `csl-orig`.

## Headline

| Metric | Value |
|---|---:|
| Correction commits analysed (`csl-orig`, v02) | 1,981 (2019–2026) |
| Distinct content correctors in any single year | **≤ 4** |
| Lead corrector's annual share | **51 – 100 %** |
| Single-corrector year (2020) | 1 person / 269 commits |
| 2026 lead handoff | funderburkjim → drdhaval2785 |
| Dictionaries that are single-maintainer-dominated | **43 / 43** |
| `csl-corrections` issues (closed / open) | 244 (229 / 15) |
| Resolution latency — median | **6 days** |
| Resolution latency — mean / p90 / max | 155.7 d / 317 d / 2,337 d (6.4 yr) |
| Long-tail issues (open or > 90 d) | 47 / 244 |

## 1. Annual correction concentration

Distinct correctors per year never exceeds four, and a single person carries the
majority of corrections every year — *more* concentrated than the org-wide code
bus factor (core trio = 97.6 %).

| Year | Correction commits | Correctors | Lead | Lead share |
|---|---:|---:|---|---:|
| 2019 | 61 | 4 | funderburkjim | 51 % |
| 2020 | 269 | **1** | funderburkjim | **100 %** |
| 2021 | 392 | 4 | funderburkjim | 73 % |
| 2022 | 153 | 3 | funderburkjim | 85 % |
| 2023 | 162 | 3 | funderburkjim | 81 % |
| 2024 | 224 | 4 | funderburkjim | 75 % |
| 2025 | 259 | 3 | funderburkjim | 64 % |
| 2026 | 461 | 4 | **drdhaval2785** | 83 % |

**2020 disproves the naïve hypothesis** that contributor diversity drives
throughput: one corrector produced 269 commits, a high-output year. Throughput
tracks the *lead corrector's burst activity*, not crew size. **2026 records a
leadership handoff** — drdhaval2785 overtakes funderburkjim, who had led every
year 2019–2025.

## 2. Per-dictionary single points of failure

Every one of the 43 dictionaries is dominated by a single corrector (top-corrector
share 44–93 %; ≤ 6 correctors each). The two leads divide the corpus between them.

| Dict | Commits | Correctors | Lead | Lead share | SPOF |
|---|---:|---:|---|---:|:--:|
| mw | 516 | 6 | funderburkjim | 69 % | |
| pwg | 211 | 3 | funderburkjim | 76 % | |
| ap | 157 | 3 | drdhaval2785 | 75 % | |
| pw | 143 | 3 | funderburkjim | 83 % | ⚠ |
| ap90 | 142 | 4 | funderburkjim | 72 % | |
| shs | 102 | 2 | drdhaval2785 | 79 % | |
| sch | 55 | 2 | funderburkjim | 93 % | ⚠ |
| lrv | 48 | 2 | drdhaval2785 | 81 % | ⚠ |
| md | 39 | 2 | funderburkjim | 90 % | ⚠ |

(⚠ = single corrector or lead share ≥ 80 %. Full 43-dict table reproducible from
the command below.) Labor split: **funderburkjim** leads most dictionaries,
**drdhaval2785** owns a cluster (ap, shs, lrv, mw72, yat, bor, gst, pe).

## 3. Resolution latency is bimodal

Across 244 `csl-corrections` issues (229 closed), the **median resolution is
6 days** — but the mean is 155.7, p90 is 317 days, and the maximum is 2,337 days
(6.4 years). Half of all corrections close within a week; a long tail languishes
for months to years.

The fast median means the pipeline is **responsive when active**; the long tail is
where **single-maintainer capacity runs out**.

## 4. What sits in the tail

47 of 244 issues are tail (open or > 90 days; 7 still open). The tail is **not**
dictionary-specific (37/47 issue titles carry no dictionary name — issue *bodies*
would be needed). The signal is the **label**:

| Tail label | n | | Tail severity | n |
|---|---:|---|---|---:|
| question | 16 | | minor | 33 |
| text-correction | 13 | | medium | 15 |
| enhancement | 8 | | | |
| encoding | 8 | | | |
| bug | **4** | | | |

The tail is **deprioritized low-severity questions and enhancements, not blocked
critical fixes** — the signature of a single maintainer triaging by severity and
letting the "nice-to-have" backlog fall off.

## 5. Methodological note — count corrections, not lines

Line volume is a misleading throughput measure: 2019 shows 7.85 M insertions (bulk
*import* of whole dictionary files, not corrections) and 2021 shows 2.9 M
insertions ≈ 2.85 M deletions (a mass *reformat*). The reliable unit is the
**correction-classified commit** — subject signature `DC <date>` +
`csl-corrections#N`, excluding `ci:`/`docs:`/import/reformat. Under that classifier
2026's raw 461 commits reduce to 213 real corrections (≈ 2025's 212); the rest is
CI/infra noise. Net-line change ≈ 0 with high churn is the genuine-correction
fingerprint; large positive net = import.

## Draft abstract

> Digital lexicography projects are routinely assessed for code sustainability,
> but the sustainability of the **data** — the ongoing correction of dictionary
> text — is rarely measured. Using twelve years of version history from the
> Cologne Digital Sanskrit Lexicon (43 dictionaries, 1.49 M entries), we show that
> content correction is even more concentrated than code contribution: in no year
> do more than four people correct dictionary text, and a single editor accounts
> for 51–100 % of corrections annually. Throughput is driven by individual bursts
> rather than crew size — a sole corrector produced the second-highest annual
> output on record. Correction *responsiveness* is nonetheless high (median issue
> resolution six days), but bimodally so: a long tail of low-severity questions and
> enhancements remains unresolved for months to years (max 6.4 years), exactly
> where single-maintainer capacity is exhausted. We argue that the curatorial
> layer of a mature digital dictionary carries a measurable, and currently
> unmanaged, bus-factor risk, and we propose correction-classified commit counts
> as the appropriate throughput unit for such audits.

## Reproduction

```sh
# Annual concentration (alias-merged):
git -C ../csl-orig log --pretty=format:"%ad|%ae" --date=format:"%Y" -- v02 | awk -F'|' '…'

# Per-dictionary correctors:
git -C ../csl-orig log --pretty=format:"C|%ae" --name-only -- v02 | awk '…'

# Resolution latency (retry-with-min-rows guard; API is TLS-flaky):
gh api --paginate repos/sanskrit-lexicon/csl-corrections/issues?state=all\&per_page=100 \
  --jq '.[] | select(.pull_request==null) | [(.created_at),(.closed_at//"open"),
        ([.labels[].name]|join(";")),(.title)] | @tsv'
```

_(Full awk bodies are in the plan/probe log; this report is a consolidation of the
2026-06-10 read-only probes. A `scripts/obs_q_correction.py` offline generator —
following the `bus_factor.py` pattern — is the next engineering step.)_
