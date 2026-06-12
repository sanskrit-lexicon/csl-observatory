# Observatory reports

Offline, reproducible analyses of the `sanskrit-lexicon` GitHub organization.
Each finding is produced by a script in [`../scripts/`](../scripts/) over the
committed CSV snapshots in
[`../observatory/site/src/data/`](../observatory/site/src/data/) — no live API
calls — and is mirrored on the [Observable dashboard](https://sanskrit-lexicon.github.io/csl-observatory/).

**Start here:** [`synthesis.md`](synthesis.md) ties the four findings into one
picture.

## Findings

| Report | Script | Site page | Headline |
|---|---|---|---|
| [`bus_factor.md`](bus_factor.md) | `bus_factor.py` | [Community](https://sanskrit-lexicon.github.io/csl-observatory/community) | Core trio = 97.6% of contributions; 65/76 repos have bus factor 1; Gini 0.86 |
| [`repo_health.md`](repo_health.md) | `repo_health.py` | [Repo Health](https://sanskrit-lexicon.github.io/csl-observatory/repo-health) | 41/76 repos unlicensed; 46/76 default to `master`; only 5 fully clean |
| [`taxonomy_adoption.md`](taxonomy_adoption.md) | `taxonomy_adoption.py` | [Issue Taxonomy](https://sanskrit-lexicon.github.io/csl-observatory/coverage) | 89% of issues typed, 63% fully conformant; 92% peak in 2025; 54 stray labels |
| [`velocity_timeline.md`](velocity_timeline.md) | `velocity_timeline.py` | [Activity](https://sanskrit-lexicon.github.io/csl-observatory/activity) | 9,877 commits over 13 yrs; peak 11 distinct authors/yr; backlog 1,742 (2025) → 913 (2026) |
| [`contributor_identity.md`](contributor_identity.md) | `contributor_identity.py` | — | 0/16 authors have a registered ORCID; 7 named await registration, 9 to identify |
| [`obs_q_correction_sustainability.md`](obs_q_correction_sustainability.md) | _(probe; `obs_q_correction.py` is next)_ | — | Content corrections are single-person-burst-driven: ≤4 correctors/yr, lead 51–100%; resolution median 6 d but a tail to 6.4 yr |

## OBS-T — error typology (language-resource track, Phases 1–8)

A 50,953-event correction corpus + two-axis typology (location × edit-type), with a
released resource, NLP baselines, and a validation suite. Design:
[`../docs/ERROR_TYPOLOGY_DESIGN.md`](../docs/ERROR_TYPOLOGY_DESIGN.md) · datasheet:
[`../docs/DATASHEET.md`](../docs/DATASHEET.md) · live:
[Error Typology](https://sanskrit-lexicon.github.io/csl-observatory/error-typology).

| Report | Script | Headline |
|---|---|---|
| [`obs_t_typology.md`](obs_t_typology.md) | `obs_t_typology.py` | Location: sense 53% · headword 22% · markup 12% · citation 10%. Edit-type: spelling 33% · punctuation 20% · spacing 19% · diacritic 11% |
| [`obs_t_rigor.md`](obs_t_rigor.md) | `obs_t_rigor.py` | H1 micro-edit (median dist 2, 66% ≤2 chars) at all locations; H2 location×dict Cramér's V=0.415; H3 headword falling, markup/meta rising |
| [`obs_t_robustness.md`](obs_t_robustness.md) | `obs_t_robustness.py` | V bootstrap [0.41,0.42], minus-PW 0.437, git-only 0.374; micro-edit rate robust across layers |
| [`obs_t_campaigns.md`](obs_t_campaigns.md) | `obs_t_campaigns.py` | 361 campaigns, 34,971 documented; citation-source standardization largest (11,966); campaign vs organic separated |
| [`obs_t_baselines.md`](obs_t_baselines.md) | `obs_t_baselines.py` | Detection 0.516 (chance .5); correction acc@1 0.059; location classifier 0.594 vs 0.44 majority |
| [`obs_t_translit_validation.md`](obs_t_translit_validation.md) | `obs_t_translit_check.py` | SLP1→IAST 100%, Devanagari 98.5%, HK 95.6% vs `indic_transliteration`; found HK/SLP1 convention mixing |
| [`obs_t_silver.md`](obs_t_silver.md) | `obs_t_silver.py` | Silver validation that surfaced the location/edit-type axis confound (resolved in Phase 8) |
| [`obs_t_issuelabel.md`](obs_t_issuelabel.md) | `obs_t_issuelabel.py` | Independent issue-typing corroborates: surface/text 65.6% vs content 17.1% |

Human-gated (awaiting annotation): `obs_t_gold.py` and `obs_t_errorsample.py` —
blank sheets in [`../validation/`](../validation/).

## Research-paper hypotheses (OBS-*)

A separate line of work frames probes as falsifiable hypotheses for lexicography
/ Indology journals. **OBS-Q** (above) is org-process evidence and lives here.
**OBS-R** (redundancy/derivation) and **OBS-C** (citations) are *dictionary-content*
findings and belong in [`csl-atlas`](https://github.com/sanskrit-lexicon/csl-atlas)
per the boundary rules — [`obs_rc_atlas_bridge.md`](obs_rc_atlas_bridge.md) records
their corpus-wide numbers and routes each to the existing `csl-atlas` hypothesis it
extends (`M1-M2-MACRO`, `XREF-CORE`, `INDIG-CITE`).

## Synthesis

[`synthesis.md`](synthesis.md) — *State of the observatory.* A productive,
well-governed, actively-maintained but structurally fragile ecosystem whose
risks are **continuity** (3 people carry it) and **reuse metadata** (licenses,
ORCIDs), not abandonment.

## From findings to action

Each finding's actionable follow-ups are filed on the
[Tooling Roadmap (project #9)](https://github.com/orgs/sanskrit-lexicon/projects/9),
split by a `Category` field into **Findings** (issues #22–#25) and **Actions**
(#15–#21). The action drafts and their rationale live in
[`../docs/hygiene_issues_draft.md`](../docs/hygiene_issues_draft.md).

## Reproducing

```sh
python scripts/bus_factor.py
python scripts/repo_health.py
python scripts/taxonomy_adoption.py
python scripts/velocity_timeline.py
python scripts/contributor_identity.py
```

Each writes its `reports/<name>.md` and refreshes the matching
`observatory/site/src/data/<name>.csv`. The numbers are deterministic from the
committed snapshot, so a re-run reproduces the reports exactly.

---

_Other files in this directory (`contributors.md`, `coverage.md`,
`dashboard.md`, `timeline.md`) are generated summary tables from the
`render_reports.py` pipeline, distinct from the analytical findings above._
