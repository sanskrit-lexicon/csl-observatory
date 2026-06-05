# State of the observatory — synthesis

**csl-observatory · 2026-06-05 · Cologne Digital Sanskrit Dictionaries**

> **Abstract.** Four offline, reproducible analyses of the `sanskrit-lexicon`
> GitHub organization — contributor concentration, repository health, issue-
> taxonomy conformance, and activity over time — converge on one structural
> portrait: a 13-year, 76-repository digitisation effort that is highly
> productive and well-governed at the issue level, yet carried by three people
> and thin on the reuse metadata (licenses, ORCIDs) that would make it FAIR and
> citable. The organization's risk is continuity and metadata, not abandonment.

_Each headline number below is computed offline and reproducibly from the data
in `observatory/site/src/data/`; this document only ties them together. Sources:
[`bus_factor.md`](bus_factor.md), [`repo_health.md`](repo_health.md),
[`taxonomy_adoption.md`](taxonomy_adoption.md),
[`velocity_timeline.md`](velocity_timeline.md),
[`contributor_identity.md`](contributor_identity.md). Index of all reports:
[`README.md`](README.md)._

## The ecosystem in one paragraph

The `sanskrit-lexicon` organization is a **13-year, 76-repository,
~9,900-commit** digitisation effort that has produced and corrected dozens of
Sanskrit dictionaries through an unusually disciplined public issue workflow —
and that rests on **three people**. It is highly productive, well-governed at
the issue level, actively maintained, and structurally fragile. The risk it
faces is not abandonment; it is **continuity** (too few hands) and **reuse
metadata** (licenses and scholarly identifiers largely absent).

## Four findings, one picture

| Lens | Headline | What it says |
|---|---|---|
| **Concentration** (`bus_factor`) | 3 people = 97.6% of contributions; **65/76 repos have bus factor 1**; Gini 0.86 | The work is carried by a tiny core; most repos have no second author for the majority of their history. |
| **Activity** (`velocity_timeline`) | 9,877 commits / 5,324 issues; peak year drew only **11 distinct authors**; PRs negligible until 2026; backlog peaked 1,742 (2025) → 913 (2026) | Throughput is volume-per-person, not a growing base. Work comes in **correction campaigns**, not steady-state maintenance. |
| **Process** (`taxonomy_adoption`) | **89% of issues typed, 63% fully conformant**; adoption climbed to a 92% peak in 2025 | Governance was retrofitted across the whole corpus and is now strong — with a tail of cleanup debt (324 over-typed issues, 54 stray labels). |
| **Hygiene** (`repo_health` + `contributor_identity`) | **53% of repos have no license**; 46/76 default to `master`; **0 of 16 authors have a registered ORCID** | The metadata layer that makes the work FAIR and citable is thin. |

## The cross-cutting tension: productive but fragile

The four lenses agree on one structural fact from different angles. The
**concentration** finding says three people do nearly everything; the
**velocity** finding independently confirms it (never more than 11 distinct
authors active in a single year, even as commits and issues ran into the
thousands). So the ecosystem's remarkable output is a function of a few
people's sustained intensity, not of scale. That is the central risk and it
is invisible in raw throughput charts — which is exactly why the multi-lens
read matters.

Against that fragility sits genuine strength: the **issue taxonomy** is applied
to ~9 in 10 issues across a 13-year backlog, and conformance reached 92% in
2025. This is a project that takes process seriously. The 2026 dip (39%
conformant) is not regression — it is the normal lag of recently-opened,
not-yet-triaged issues, consistent with the velocity finding's picture of an
active 2026 correction wave.

Where the project is genuinely thin is **metadata for reuse and credit**: over
half the repositories carry no license at all, and not one contributor has a
registered ORCID. For a scholarly digitisation project whose value depends on
being citable and reusable, this is the cheapest high-leverage gap to close —
and unlike concentration, it is fixable with mechanical effort rather than new
people.

## What this implies

- **Continuity is the strategic risk.** Mitigations are documentation,
  onboarding, and lowering the barrier to a second author per repo — the
  emergence of pull-request workflow in 2026 is a healthy early signal.
- **Hygiene is the quick win.** Licensing, default-branch standardisation, and
  ORCID registration are mechanical and high-leverage. Drafted (not filed) as
  reviewable issues in [`docs/hygiene_issues_draft.md`](../docs/hygiene_issues_draft.md);
  the ORCID worksheet is [`contributor_identity.md`](contributor_identity.md).
- **The taxonomy is worth finishing, not rebuilding.** Close the small
  conformance tail (over-typed issues, stray labels) rather than re-litigating
  the scheme.

## Method note

Every figure here is produced by an offline, reproducible script over committed
CSV snapshots — no live API calls — so the synthesis can be re-derived at any
time by re-running `scripts/{bus_factor,repo_health,taxonomy_adoption,velocity_timeline,contributor_identity}.py`.
Each finding is also surfaced on the Observable site (Community, Repo Health,
Issue Taxonomy, Activity pages), where the page JavaScript recomputes the same
numbers as a cross-check.

## Citation

> Gasūns, M. et al. (2026). *State of the Observatory: a multi-signal analysis
> of the Cologne Digital Sanskrit Lexicon GitHub organization.* csl-observatory,
> Cologne Digital Sanskrit Dictionaries. Snapshot 2026-06-05. DOI: pending
> Zenodo mint.

Cite with the snapshot date for reproducibility; see [`../CITATION.cff`](../CITATION.cff).

*Object of analysis: the GitHub organization as a whole — in scope per
`docs/BOUNDARY_RULES.md`.*
