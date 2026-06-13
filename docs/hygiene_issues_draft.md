# Org-hygiene issues

Date: 2026-06-05

**Status: FILED on 2026-06-05** as issues
[#15](https://github.com/sanskrit-lexicon/csl-observatory/issues/15)–[#21](https://github.com/sanskrit-lexicon/csl-observatory/issues/21)
in `csl-observatory` (see the mapping in the summary table below). This file
is retained as the rationale/source-of-truth for those issues.

These turn the findings in [`reports/repo_health.md`](../reports/repo_health.md),
[`reports/taxonomy_adoption.md`](../reports/taxonomy_adoption.md), and
[`reports/contributor_identity.md`](../reports/contributor_identity.md) into
GitHub issues. Each carries a `⚠ Care` note where an action is visible or
partly irreversible — those notes are reproduced in the filed issues and still
require maintainer judgement before execution.

Suggested labels follow the `csl-observatory` tooling taxonomy (one type +
one severity + one milestone). These are written as **org-level tracking
issues to be filed in `csl-observatory`**, each referencing the affected
repos, rather than spamming dozens of individual repos — adjust if you'd
rather file per-repo.

Counts are current as of the 2026-06-05 data snapshot; re-run the scripts
before filing in case they have moved.

---

## Draft 1 — Add a license to the 41 unlicensed repositories

- **Type:** `documentation` · **Severity:** `major` · **Milestone:** Developer Experience

**Body:**

> 53% of org repositories carry no license at all, leaving reuse rights
> legally undefined for over half the ecosystem. Add a `LICENSE` file
> (proposed org default: **GPL-3.0** for code, consistent with the repos that
> already declare one; confirm the intended license for data vs code).
>
> Affected (41): `ACC`, `ArabicInSanskrit`, `BEN`, `BHS`, `CAE`, `CCS`,
> `CORRECTIONS`, `GreekInSanskrit`, `KNA`, `KOW`, `LRV`, `MCI`, `MWinflect`,
> `SHS`, `SKD`, `STC`, `VEI`, `WIL`, `alternateheadwords`, `avlinks`,
> `csl-apidev`, `csl-devanagari`, `csl-doc`, `csl-homepage`, `csl-json`,
> `csl-ldev`, `csl-lnum`, `csl-lslink`, `csl-newsletter`, `hwnorm1`,
> `hwnorm2`, `literarysource`, `mw-dev`, `sanskrit-fonts`,
> `sanskrit-lexicon.github.io`, `santamlegacy`, `temp_corrections_acc`,
> `temp_corrections_ae`, `temp_corrections_ap90`, `temp_corrections_mw`,
> `test_cologne_push`.
>
> **Acceptance:** each repo above has a `LICENSE` file GitHub recognises as an
> SPDX license. ⚠ **Care:** dictionary *data* may need a different license
> (e.g. CC-BY-SA) than *code* (GPL); decide the data/code split first.

---

## Draft 2 — Normalise the 21 `NOASSERTION` licenses

- **Type:** `documentation` · **Severity:** `minor` · **Milestone:** Developer Experience

**Body:**

> These repos have a `LICENSE` file that GitHub cannot map to an SPDX id
> (`NOASSERTION`) — usually a non-standard or lightly-edited license text.
> Replace with the canonical SPDX text so the license is machine-detectable.
>
> Affected (21): `AP`, `ApteES`, `BOP`, `BOR`, `BUR`, `COLOGNE`, `DCS`,
> `FRI`, `GRA`, `INM`, `MD`, `MW72`, `MWS`, `PWG`, `PWK`, `SCH`, `VCP`,
> `Wil-YAT`, `csl-orig`, `csl-pywork`, `csl-websanlexicon`.
>
> **Acceptance:** GitHub's repo sidebar shows a recognised SPDX license for
> each. ⚠ **Care:** confirm the intended license matches the existing text's
> intent before overwriting.

---

## Draft 3 — Standardise the default branch to `main` (46 repos on `master`)

- **Type:** `infrastructure` · **Severity:** `major` · **Milestone:** Developer Experience

**Body:**

> 46 of 76 repos still default to `master`, 28 to `main`, 2 to `gh-pages`. The
> inconsistency complicates tooling, CI defaults, runbooks, and contributor
> instructions. Rename `master` → `main` org-wide (GitHub redirects the old
> name and offers to retarget open PRs).
>
> **Acceptance:** every non-Pages repo defaults to `main`.
> ⚠ **Care:** this is the highest-touch item — it can break hard-coded branch
> references in CI configs, raw-content URLs, submodules, local clones, and
> external links. Audit those per repo first; the 2 `gh-pages` defaults
> (`rvlinks`, `sanskrit-fonts`) are intentional and should be left.

---

## Draft 4 — Add a description to 5 repositories

- **Type:** `documentation` · **Severity:** `trivial` · **Milestone:** Developer Experience

**Body:**

> These repos have an empty GitHub description, hurting discoverability:
> `csl-apidev`, `csl-inflect`, `csl-websanlexicon`, `hwnorm2`,
> `sanskrit-lexicon.github.io`. Add a one-line description to each.
>
> **Acceptance:** all five have a non-empty description.

---

## Draft 5 — Archive 6 disposable repositories

- **Type:** `tech-debt` · **Severity:** `minor` · **Milestone:** Developer Experience

**Body:**

> These look disposable (temporary correction batches, a push test, a legacy
> PHP snapshot), are not archived, and carry ~0 open issues — yet they still
> appear in contributor/issue metrics and search: `temp_corrections_acc`,
> `temp_corrections_ae`, `temp_corrections_ap90`, `temp_corrections_mw`,
> `test_cologne_push`, `santamlegacy`.
>
> **Acceptance:** each is either archived or has a stated reason to remain
> active. ⚠ **Care:** confirm with the maintainer that the work in each was
> merged/superseded before archiving. Archiving is reversible but read-only.

---

## Draft 6 — Register ORCIDs for named contributors; identify the rest

- **Type:** `documentation` · **Severity:** `minor` · **Milestone:** Community

**Body:**

> 0 of 16 human commit authors have a registered ORCID. Seven are already
> identified and only need an ORCID (Jim Funderburk, Dhaval Patel, Mārcis
> Gasūns, Anna Rybakova, Nagabhushana Rao, Scott Rhodes, Thomas Malten); nine
> occasional authors still need identification. Worksheet:
> [`reports/contributor_identity.md`](../reports/contributor_identity.md).
>
> **Acceptance:** registered ORCIDs filled into `scripts/contributors_map.json`
> for the seven named contributors; the nine unknown logins triaged. Extends
> existing tracking issue #1 (self-identification).

---

## Draft 7 — Close the issue-taxonomy conformance tail

- **Type:** `tech-debt` · **Severity:** `minor` · **Milestone:** Developer Experience

**Body:**

> The taxonomy is broadly applied (89% typed, 63% fully conformant) but has a
> cleanup tail: **324 issues carry more than one type label** (one-type-rule
> violation) and **999 issues carry one of 54 stray labels** (GitHub defaults
> like `duplicate`/`help wanted`, capitalised dupes like `Documentation`/`Bug`,
> and a `domain:*` scheme). Detail:
> [`reports/taxonomy_adoption.md`](../reports/taxonomy_adoption.md).
>
> **Acceptance:** over-typed issues reduced to one type label each; stray
> labels deleted or folded into the taxonomy (decide the fate of the `domain:*`
> scheme explicitly — keep as an orthogonal axis or drop).

---

## Summary

| Issue | Action | Type | Severity | Scope | Care |
|---|---|---|---|---:|:---:|
| [#15](https://github.com/sanskrit-lexicon/csl-observatory/issues/15) | Add licenses | documentation | major | 41 repos | ⚠ data vs code |
| [#16](https://github.com/sanskrit-lexicon/csl-observatory/issues/16) | Normalise NOASSERTION | documentation | minor | 21 repos | — |
| [#17](https://github.com/sanskrit-lexicon/csl-observatory/issues/17) | Default branch → `main` | infrastructure | major | 46 repos | ⚠ high-touch |
| [#18](https://github.com/sanskrit-lexicon/csl-observatory/issues/18) | Add descriptions | documentation | trivial | 5 repos | — |
| [#19](https://github.com/sanskrit-lexicon/csl-observatory/issues/19) | Archive disposable repos | tech-debt | minor | 6 repos | ⚠ confirm merged |
| [#20](https://github.com/sanskrit-lexicon/csl-observatory/issues/20) | ORCIDs / identity | documentation | minor | 16 people | — |
| [#21](https://github.com/sanskrit-lexicon/csl-observatory/issues/21) | Taxonomy cleanup tail | tech-debt | minor | ~1,300 issues | — |

*Object of analysis: GitHub repositories, issues, and contributors — in scope
per `docs/BOUNDARY_RULES.md`. These drafts act on the observatory's own
findings; filing them is a separate, human-authorised step.*
