# Anthology alignment — what the 2026 ACL Anthology rewards, and the observatory's next seven moves

_Created: 20-10-2026 · Last updated: 20-10-2026_

**Status:** proposal, not a shipped change. Three units are minted as
[H7122](https://github.com/gasyoun/Uprava/blob/main/handoffs/H7122-DeepSeek_csl-observatory_headline-claims-gate_20.10.26.md)
(headline claims gate),
[H7123](https://github.com/gasyoun/Uprava/blob/main/handoffs/H7123-DeepSeek_csl-observatory_agent-lane-census_20.10.26.md)
(agent-lane census) and
[H7124](https://github.com/gasyoun/Uprava/blob/main/handoffs/H7124-DeepSeek_csl-observatory_obst-bench-split_20.10.26.md)
(OBS-T benchmark split). Moves 4–7 below are not minted: three need data that
does not exist yet, one needs a human gate.

This document answers one question: **given what the ACL Anthology is
currently rewarding, where should the observatory spend its next units?** It is
not a publication plan for the whole org — the org-wide programme lives in
[ROADMAP_ACL_ANTHOLOGY_FOOTPRINT_2026_2027.md](https://github.com/gasyoun/Uprava/blob/main/ROADMAP_ACL_ANTHOLOGY_FOOTPRINT_2026_2027.md)
and the method-family census in
[ACL_METHOD_OPPORTUNITIES_SANSKRIT_2026.md](https://github.com/gasyoun/Uprava/blob/main/ACL_METHOD_OPPORTUNITIES_SANSKRIT_2026.md).

## 1. Method, and what it cannot say

The measurement is a title census over the official machine-readable dump,
`https://aclanthology.org/anthology.bib.gz`, fetched **2026-10-19**: 12.7 MB
compressed, **131,709 entries** with a parseable `year` field. Braces are
stripped from titles before matching (`{S}anskrit` → `Sanskrit`), families are
regular-expression bands, and every share is computed against the entry count
of the same year.

Limits, stated rather than hedged:

- **Title-only.** The dump carries no abstracts, so every count is a **floor**,
  not a census. A paper that documents a dataset without saying so in its title
  is invisible.
- **Precision is not adjudicated.** Some bands over-trigger ("judge" catches
  legal-judgement papers; "historical" catches historical linguistics).
  Direction of travel is the signal; individual percentages are not.
- **2026 is partial** (10,822 entries through October), which is why its shares
  are compared with 2025 rather than read as a trend of their own.

To re-derive the table below, take the dump and apply the same recipe:

```sh
curl -sO https://aclanthology.org/anthology.bib.gz
gzip -dc anthology.bib.gz | python3 -c '...'   # parse year+title, strip braces, count per family per year
```

The org's tracked, reusable version of this mining is
[`tools/mine_anthology.py`](https://github.com/gasyoun/Uprava/blob/main/tools/mine_anthology.py)
(method families, not the bands used here); this page's bands are stated in §2
so the numbers stay checkable without the script.

## 2. What the field is rewarding

| Title band (share of that year's entries) | 2015 | 2018 | 2020 | 2022 | 2024 | 2025 | 2026 |
|---|---:|---:|---:|---:|---:|---:|---:|
| dataset / corpus / resource / benchmark | 5.6% | 11.1% | 12.6% | 12.7% | 12.1% | 11.2% | **14.8%** |
| LLM / GPT / prompt | 0.0% | 0.0% | 0.3% | 2.9% | 25.9% | 33.9% | **29.3%** |
| judge / judging | 0.2% | 0.0% | 0.1% | 0.1% | 0.2% | 0.6% | **0.8%** (89) |
| contamination / leakage / memorisation | 0.0% | 0.0% | 0.0% | 0.1% | 0.4% | **0.5%** | 0.5% (49) |
| low-resource / historical / DH | 1.0% | 1.8% | 2.4% | 2.7% | 2.9% | 2.7% | **3.2%** (344) |
| Sanskrit / Vedic / Pāṇini | 0.0% | 0.1% | 0.2% | 0.1% | 0.1% | 0.3% | 0.2% (20) |
| _entries in the year_ | _2,965_ | _4,877_ | _7,330_ | _8,656_ | _12,135_ | _14,931_ | _10,822_ |

Three readings that matter for an observatory:

1. **A released, enterable object beats a described one.** Resource-flavoured
   titles are the largest stable band and still growing. The question a reviewer
   asks is no longer "is the corpus interesting?" but "can I run my system on
   it?".
2. **Evaluation validity is the live methodological argument.** 89 titles in
   2026 carry "judge"; 49 carry contamination/leakage/memorisation, a band that
   was empty in 2015. What is being rewarded is not another number but the
   demonstration that a number means what it claims.
3. **The Sanskrit niche cannot carry a paper by itself** — 159 titles in twelve
   years, 20 in 2026 so far. The observatory's work travels when the *method*
   generalises: correction-event typology as annotation-error detection,
   maintenance metrics as community health, a benchmark anyone can enter.

The venue structure moved the same way. NLP4DH volumes went from 22 entries
(2021) to 54 (2024) and 54 (2025); LaTeCH-CLfL from 21 (2020) to 33 (2026).
The Anthology now carries both ISCLS volumes and the WSC CSDH section (29
entries each) — the two venues this repo's papers already target.

## 3. Where the observatory stands, measured

| Axis | Evidence today | Gap |
|---|---|---|
| **Agent contributions** | [AI contribution policy](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/docs/AI_CONTRIBUTION_POLICY.md) and an [820-issue agent roadmap](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/docs/AGENT_ROADMAP.md); `contributors.csv` types bots | No script and no report measures agent work. `issues.csv` holds 1,339 PRs, **1,303 created in 2026** (1,092 `gasyoun`, 206 `dependabot[bot]`) against ~36 in the preceding twelve years, and `merged_at` is not in the schema, so merged and closed-unmerged are indistinguishable |
| **Quoted numbers** | [README.md:6](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/README.md#L6) — 86 repos, 10,039 issues+PRs, 13,810 commits, 72 contributors — is generated by `scripts/update_headline_numbers.py` (H5424) from `data/summary.json` (snapshot 2026-09-28: 86 repos, 7,877 issues + 2,162 PRs, 13,810 commits) | The offline snapshot every report re-derives from says **77 repos, 5,667 issues + 1,339 PRs = 7,006, 13,299 commits**. [reports/README.md](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/reports/README.md) promises "no live API calls", so a reviewer cannot reproduce the front page. The generator is write-only (no `--check`) and covers only README/STATUS |
| **External validity** | [obs_t_errorbench.md:7](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/reports/obs_t_errorbench.md#L7): 0/120 entries contained an error | The independent error-incidence probe is null, and A48's recapture is self-referential (both occasions are correction events). A12 and A48 are both 4/5-or-below on exactly this |
| **Benchmark object** | E32 is a digest-pinned release (52,498 rows, 43 dictionaries, 208 aliases) with a 25+65-number canary; `obs_t_baselines.py` splits chronologically inside the script (train ≤2016, dev 2017, test ≥2018) | No frozen split is exported, no submission format, no scoring script, no baseline prediction files: a third party cannot enter, only cite. Detection is unsolved — P 0.521 / R 0.515 / F0.5 0.519 / **FPR 0.474** ([obs_t_baselines_field_metrics.md:19](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/reports/obs_t_baselines_field_metrics.md#L19)) |
| **Org-metrics dataset** | A15 draft; Zenodo analysis-inputs concept DOI; per-page schema.org `Dataset` node | No dataset ID per snapshot, no datasheet row for the org-metrics corpus, no distribution-level metadata (contentUrl + SHA-256) |
| **Reference graph** | `/network` = contributors × repos; the OpenAlex citation sweep **exists** (H1478: 35 works, a stated lower bound, snapshot 2026-07-28) | The cross-repo reference graph specified as Part 4.5 of the [standards spec](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/docs/HYPOTHESIS_VIZ_STANDARDS_SPEC_2026-07.md#L293) is unbuilt, although the `org/repo#N` edges are already in `data/issues.json` |
| **Identity** | 286 contributor rows, 9 unidentifiable logins, `consent` field landed but empty | [issue #20](https://github.com/sanskrit-lexicon/csl-observatory/issues/20) blocks A14/A15 at 5/5, and identity quality silently drives bus factor and recapture |

## 4. The seven moves

| # | Move | Artifact | Effort | Lane |
|---|---|---|---|---|
| 1 | **Headline claims gate** — one authority table, one check | `docs/SNAPSHOT_AUTHORITY.md` + `update_headline_numbers.py --check` + CI | S–M | [H7122](https://github.com/gasyoun/Uprava/blob/main/handoffs/H7122-DeepSeek_csl-observatory_headline-claims-gate_20.10.26.md) |
| 2 | **Agent-lane census** — measure the contribution channel that grew 36× | `merged_at` in the snapshot, `scripts/agent_lane.py`, `reports/agent_lane.md` | M | [H7123](https://github.com/gasyoun/Uprava/blob/main/handoffs/H7123-DeepSeek_csl-observatory_agent-lane-census_20.10.26.md) |
| 3 | **OBS-T as a benchmark** — export and freeze what the script does privately | `obst-bench/v1/` splits + digests, `scripts/obst_bench.py`, two baselines | M | [H7124](https://github.com/gasyoun/Uprava/blob/main/handoffs/H7124-DeepSeek_csl-observatory_obst-bench-split_20.10.26.md) |
| 4 | **External-validity sample** — settle the error-incidence question | stratified 300–500-entry sample, LLM annotators + human adjudication | M (human gate) | unminted |
| 5 | **Org-metrics dataset release** — a citable snapshot, not a dashboard | dataset ID per cut, datasheet row, Croissant-style distributions, A15 venue | M | unminted |
| 6 | **Cross-repo reference graph** — the AAN move, org surface only | node/edge CSVs from `org/repo#N` mentions + `/network` section | S–M | unminted |
| 7 | **LLM record linkage** — identity with a measured error rate | linkage ladder + LLM matcher, per-level false-match rates | M | depends on #20 |

**1. Headline claims gate.** The trend to mirror is contamination and
versioning: a number is only worth what its provenance allows. The fix is not a
new generator — H5424 already regenerates the front page — but (a) a written
authority table saying which snapshot each surface quotes, (b) a `--check` mode
that fails on a mismatch instead of silently writing, and (c) coverage of
`reports/*.md`, the roadmap and the article drafts, where hand-typed numbers
still live. The divergence between the live pipeline and the offline transform
is itself a finding and belongs in `reports/`, not in a commit message.

**2. Agent-lane census.** The field's dominant subject is now the model as
producer and as judge; this repo has two years of the producer side and
measures none of it. Once `merged_at` is in the snapshot and an attribution rule
has a measured error rate on a hand-checked sample, the report can state merge
rate, time-to-merge, review latency, CI first-run failure, revert and
follow-up-defect rates per lane — and can answer a policy question no one else
can: did `no-bot` and the weekly human-activity feed actually keep maintainer
threads clean?

**3. OBS-T as a benchmark.** A73's ISCLS-9 cut releases the corpus; a benchmark
is what makes people build on it. The split logic already exists inside
`obs_t_baselines.py`; exporting it frozen (test as digests plus a scoring-only
copy), with a prediction format and two reproducible baselines, turns a
described resource into an enterable one — and the honest FPR of 0.474 gives the
leaderboard room to be entered. Do not re-cut E32: the benchmark is a pinned
view over it.

**4. External-validity sample.** The only probe of independent error incidence
returned 0/120, which supports no claim in either direction. A stratified
sample with LLM annotators and human adjudication on disagreements is the one
gate no re-analysis of the correction log can substitute for, and the blind
cross-model protocol (κ = 0.906) already exists. Needs a human adjudication
budget, hence unminted.

**5. Org-metrics dataset release.** Resource-flavoured titles are 14.8% of 2026
and A15 has a completed draft with no venue. The missing pieces are mechanical:
a dataset ID per snapshot (`csl-obs/org@x.y.z`), a filled datasheet row, and
distribution-level metadata next to the existing `Dataset` node. Note the Zenodo
DOI and datasheet template are already done — this is packaging, not new
research.

**6. Cross-repo reference graph.** Specified, unbuilt, cheap: nodes = repos +
issues/PRs, edges = `org/repo#N` mentions already present in `data/issues.json`.
The citation side is no longer a gap (H1478 shipped a systematic OpenAlex sweep
with stated recall bounds); what is missing is the community's internal
referential structure, which is the observatory's own territory.

**7. LLM record linkage.** Nine unidentified logins and empty consent values
hold A14/A15 at 4/5. The repo already has the right methodology — a linkage
ladder with a measured false-match rate per level, and a documented rejection of
edit-distance-1 at 70–98% false links. Adding an embedding/LLM matcher with the
same measurement discipline fixes a real data gap and yields a small methods
result; it is blocked on the human consent/ORCID fill, not on technique.

## 5. What not to redo

- **Part 4 of the standards spec is largely shipped** — event-ID scheme (4.1),
  datasheet template (4.2), MWSA evaluation lineage (4.3), OntoLex/TEI routing
  (4.4). Do not re-mint them.
- **Data statements and ERRANT edit typing are already in the instruments**;
  the org-wide census records them as tried, not as opportunities.
- **The OpenAlex citation sweep is done** (H1478). Only the internal reference
  graph remains.
- **No more static chart pages.** The dashboard is maintenance infrastructure;
  the research product is the dataset, the benchmark and the report.
- **Do not chase a "Sanskrit NLP" framing.** Twenty titles a year cannot carry
  an argument; the correction-event corpus travels as annotation-error
  detection, not as Indology.

## 6. Sequencing

1. **H7122** (claims gate) — cheapest, and every later report inherits its
   credibility.
2. **H7123** (agent lane) — the new axis; needs one snapshot field before any
   analysis is honest.
3. **H7124** (benchmark split) — the durable citation object; feeds A73's
   camera-ready pointing at a real benchmark rather than a promise.
4. Then #4 (external validity, human-gated), #5 (dataset release, venue
   `@DECIDE`), #6 (reference graph), #7 (linkage, after #20).

**Venue notes.** A73's ISCLS-9 submission is due **20-10-2026 AoE** — the
benchmark unit (#3) is timed to be citable by the camera-ready, not by the
submission. #5 fits JOHD or an LREC data paper, or MSR/IST through the CHAOSS
framing already added to A15. #2 fits LREC or NLP4DH; #6 fits LaTeCH-CLfL.

_Dr. Mārcis Gasūns_
