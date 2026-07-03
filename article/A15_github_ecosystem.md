# Measuring the Cologne Digital Sanskrit Dictionaries as a GitHub Maintenance Ecosystem

_Created: 03-07-2026 · Last updated: 03-07-2026_

**Status (03-07-2026):** skeleton draft (readiness 3/5), paper A15. Sequencing: the
[FABLE index](https://github.com/gasyoun/Uprava/blob/main/FABLE_UNTOUCHED_INDEX.md)
schedules A15 after A13/A14, but this skeleton depends on neither of them *shipping* —
A13 is GO-conditional for IIJ and A14 is ORCID-gated; only A15's eventual **submission**
should wait on their venue outcomes. Venue: TBD (@DECIDE — likely the same
LREC/JOHD-family as A13/A14). Byline: pending MG ruling.

**Draft byline:** Mārcis Gasūns

## Abstract

Long-running digital lexicography projects are usually described through their
content — entries digitised, dictionaries released — while the *maintenance labour*
that keeps the content alive stays invisible. This article treats the Cologne
Digital Sanskrit Dictionaries (CDSL), a digitisation programme spanning more than
three decades, as a **GitHub maintenance ecosystem** and measures it with the
reproducible instruments of repository mining: contributor concentration, repository
hygiene, issue lifecycle, taxonomy conformance, activity velocity, and external
reach. Against a snapshot of 76 repositories, 5,324 issues, and 9,877 commits
(2014–2026), we find a paradoxical profile: throughput is high and rising (a record
2,519 commits in 2026), yet 65 of 76 repositories depend on a single maintainer,
three people account for 97.6% of all contributions, and 620 open issues are more
than four years old. A case study of the `csl-orig` correction campaign of
2025–2026 — 1,023 issues opened in one year, 923 closed the next — shows that the
ecosystem's characteristic rhythm is the *correction wave*, not steady-state
maintenance. We argue that GitHub-native metrics, properly bounded, give digital
lexicography a maintenance observability layer it currently lacks, and that the
CDSL profile (used as infrastructure, cloned ~6,900 times a fortnight, yet starred
only 103 times) is likely typical of scholarly data organisations.

**Keywords:** digital lexicography, Sanskrit, repository mining, software
maintenance, bus factor, sustainability of research infrastructure

## 1. Introduction

The Cologne Digital Sanskrit Dictionaries project has digitised and now maintains
several dozen Sanskrit dictionaries — works originally published between the early
nineteenth and the late twentieth century, from Wilson (1832) through the great
Petersburg lexica (Böhtlingk & Roth 1855–1875) and Monier-Williams (1899) to
twentieth-century specialist dictionaries. The digitisation story itself, its
founders, disputes, and archives, is told elsewhere (the narrative report, A13);
a descriptive survey of the ecosystem's 2026 state and its standards alignment is
given in the empirical companion (A14). This article asks a different question:
**what does it cost, in observable maintenance work, to keep a two-century-old
lexicographic corpus alive on a modern collaborative platform — and is that work
sustainable?**

Since 2014 the project's operational home has been the
[`sanskrit-lexicon`](https://github.com/sanskrit-lexicon) GitHub organisation.
Every correction to a dictionary entry, every markup normalisation, every display
upgrade passes through GitHub issues, commits, and (recently) pull requests. That
makes the platform's event stream a *maintenance ledger*: an involuntary,
timestamped record of who fixed what, when, how fast, and at what backlog cost.
Software engineering has mined such ledgers for two decades — for contributor
concentration ("truck factor"; Avelino et al. 2016), for the perils of GitHub's
data model (Kalliamvakou et al. 2014), and for the health of open-source commons
(Eghbal 2020) — but digital lexicography has rarely turned these instruments on
itself. Lexicographic infrastructure is typically evaluated by FAIR-style data
criteria (Wilkinson et al. 2016), which audit the *artifact*; maintenance metrics
audit the *process* that keeps the artifact correct.

The measurement instrument is
[`csl-observatory`](https://github.com/sanskrit-lexicon/csl-observatory), an
open-source observatory built for exactly this purpose: snapshot the organisation's
GitHub state, transform it into versioned CSV/JSON datasets, and derive findings
through offline, reproducible scripts whose outputs are committed alongside the
code. Its scope is deliberately bounded to GitHub/organisation observability —
repositories, issues, PRs, commits, contributors, workflows, labels, milestones,
metadata. It does not analyse dictionary entries, dictionary structure, TEI/OntoLex
exports, corpus data, or website telemetry; those live in sibling projects, and the
error *content* of corrections is the subject of a separate typology resource
(A12). What remains is precisely the maintenance layer.

Section 2 describes the data and its reproducibility envelope. Section 3 presents
the six maintenance findings. Section 4 gives the case study — the `csl-orig`
correction campaign of 2025–2026, the largest single maintenance event in the
ecosystem's recorded history. Section 5 discusses what the profile implies for the
sustainability of scholarly data organisations.

### Relationship to companion articles (boundary note)

A15 is the third member of a set and deliberately claims none of its siblings'
ground. **A13** (the narrative report) owns the thirty-year *history* of CDSL —
founders, copyright disputes, encoding decisions, team memory; A15 makes no
historical claims beyond dating the GitHub era. **A14** (the empirical companion)
owns the *descriptive* 2026 snapshot — the issue-taxonomy runbook definition, the
headline ecosystem numbers as a survey, the dictionary corpus by entry count, and
standards alignment (FAIR, TEI Lex-0, OntoLex-Lemon); A15 reuses the same snapshot
but contributes the *analytical* maintenance instruments — bus-factor and Gini
concentration measures, lifecycle survival tables, the hygiene audit, external
reach — and the campaign case study, none of which appear in A14. (A14 §4 does
narrate contributor concentration and the annual activity curve descriptively;
A15 quantifies them with dedicated instruments and interprets them as a
sustainability profile.) **A12** (the error-typology resource) owns the linguistic content of
corrections — what was wrong in the text; A15 treats corrections only as process
events. Overlap is limited to shared provenance (the same snapshot data) and is
cited, not restated.

## 2. Data and reproducibility

All figures in this article derive from committed artifacts in the
[`csl-observatory`](https://github.com/sanskrit-lexicon/csl-observatory) repository,
regenerable offline from the versioned snapshot. The canonical snapshot inventory is
[`data/manifest.json`](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/data/manifest.json)
(snapshot `2026-06`, transformed 2026-06-01):

| Dataset | Rows | Content |
|---|---:|---|
| `repos.csv` | 76 | non-fork repositories with metadata |
| `issues.csv` | 5,413 | issues and pull requests (5,324 issues + 89 PRs) |
| `commits.csv` | 9,877 | commits across all repositories |
| `contributors.csv` | 209 | per-repository contributor rows |
| `timeseries_monthly.csv` | 1,341 | monthly activity aggregates |
| `timeseries_annual.csv` | 382 | annual activity aggregates |
| `issue_typology_annual.csv` | 140 | taxonomy label counts by year |

Two caveats govern every downstream number. First, `contributors.csv` holds 209
*per-repository* rows, not 209 people; after alias-merging, the organisation has
**17 distinct human contributors** in the snapshot window. Second, per-repo author
counts must never be summed into an organisation total (double-counting); distinct
authors are recomputed from `commits.csv`. Both rules are enforced in the finding
scripts. Known limitations of the GitHub data model apply (Kalliamvakou et al.
2014): squashed history, renamed accounts, API pagination limits, and a rolling
14-day traffic window (relevant to Section 3.6).

Each finding below is generated by one offline script over the committed snapshot,
producing a Markdown report plus a CSV consumed by the observatory's public
dashboard (https://sanskrit-lexicon.github.io/csl-observatory/). The
script–report–page triples are listed per subsection, so every figure traces to a
committed artifact.

## 3. Findings

### 3.1 Contributor concentration: a bus factor of one, sixty-five times over

(Source: [`reports/bus_factor.md`](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/reports/bus_factor.md),
generated by [`scripts/bus_factor.py`](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/scripts/bus_factor.py).)

Of 76 repositories, **65 (85%) have a bus factor of 1** — a single person accounts
for the majority of contributions — and no repository in the organisation reaches a
bus factor of 3. One maintainer (funderburkjim) alone carries 51.8% of all
contributions across 58 repositories; the core trio (funderburkjim, drdhaval2785,
gasyoun) carries **97.6%**. The Gini coefficient of the contribution distribution
is 0.861. One person covers 50% of all recorded work; two cover 80%; three cover
90%. None of the 17 human contributors has a registered ORCID, which compounds the
concentration problem with an attribution problem: the labour is not only
concentrated, it is also invisible to scholarly credit systems.

### 3.2 Repository hygiene: recoverable, and largely recovered

(Source: [`reports/repo_health.md`](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/reports/repo_health.md),
audit of 2026-06-20.)

Hygiene tells a more hopeful story, because it is the one dimension where a
targeted campaign already ran. A 2026 license rollout took the organisation from 41
unlicensed repositories to **6** (all archival/temp candidates), with 70/76 now
carrying a recognised SPDX license. Remaining debt is structural rather than legal:
46/76 repositories still default to the legacy `master` branch, 5 lack a
description, and 2 disposable repositories await archiving. Notably, **zero
repositories are stale** (all pushed within 180 days) and 22 carry no hygiene flag
at all. Hygiene, unlike concentration, proved fixable by a bounded effort — a point
we return to in the discussion.

### 3.3 Issue taxonomy: retroactive order, fragile at the edge

(Source: [`reports/taxonomy_adoption.md`](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/reports/taxonomy_adoption.md).)

A 2025–2026 runbook (defined in A14) retroactively imposed a controlled taxonomy —
one type label, one severity label, one milestone — on the historical issue base.
Coverage is now high: 89% of the 5,324 issues carry a type label and **63% are
fully conformant**. The adoption curve is instructive: conformance among issues
opened in 2014–2018 sits at 6–25%, climbs through the runbook years to a 92% peak
for 2025, then **dips to 39% for 2026** — freshly opened issues outrun the
labelling process. Classification of a backlog is a campaign; keeping new intake
classified is a habit the ecosystem has not yet formed.

### 3.4 Issue lifecycle: fast median, heavy tail, old backlog

(Source: [`reports/issue_lifecycle.md`](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/reports/issue_lifecycle.md),
snapshot as-of 2026-06-01.)

The median closed issue closes in **6 days** — for a three-person volunteer
operation, remarkably fast. But the distribution is savagely long-tailed: the 90th
percentile is 349 days, 23% of issues are still open a year after opening, and of
the 913 issues open at the snapshot, **719 (79%) are older than two years** and 620
are older than four. A **silent backlog** of 178 open issues (19%) has never
received a single comment. The lifecycle profile is thus bimodal: issues either
enter the active attention of a maintainer and close within days, or fall out of it
and persist for years.

### 3.5 Velocity: rising throughput on non-rising shoulders

(Source: [`reports/velocity_timeline.md`](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/reports/velocity_timeline.md).)

Across 2014–2026 the organisation recorded 9,877 commits and 5,324 issues, with
throughput *rising*: 2026 is the peak commit year (2,519) and 2025 the peak
issue-opening year (1,178). Yet the busiest year in the entire series drew only
**11 distinct authors** (2021). Growth is volume-per-person, not community growth.
Pull requests barely register — 89 in thirteen years, first appearing in 2019, with
59% of the lifetime total landing in 2026 alone. The organisation runs on direct
commits and issues; review-based contribution is only now emerging, and its 2026
uptick coincides with the arrival of agent-assisted tooling that works PR-first.

### 3.6 External reach: infrastructure, not fame

(Source: [`reports/external_reach.md`](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/reports/external_reach.md),
API tiers fetched 2026-07-03.)

The organisation holds **103 GitHub stars in total**; 49 of 76 repositories have
zero. Yet in a single 14-day window its core repositories were cloned **6,923
times** by ~1,814 unique cloners, and 18 distinct external projects — 10 curated
downstream libraries/applications and a partly overlapping set of 17
code-search-visible repositories — ship or wrap CDSL data. The star-to-clone disproportion is the finding: CDSL is consumed
as *infrastructure* — cloned, mirrored, embedded — not favourited as a project.
Any evaluation of scholarly data organisations that reads popularity metrics will
systematically underrate them.

## 4. Case study: the `csl-orig` correction campaign, 2025–2026

*(One trajectory, chosen as the best-documented maintenance event in the snapshot;
per-repository figures computed from the committed
[`issues.csv`](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/observatory/site/src/data/issues.csv),
snapshot 2026-06; PRs excluded via the `kind` column.)*

[`csl-orig`](https://github.com/sanskrit-lexicon/csl-orig) is the ecosystem's
canonical source repository: the digitised text of every dictionary, to which all
corrections ultimately apply. It is also the ecosystem's centre of gravity — 2,801
of the organisation's 5,324 issues (53%) live there, and it is the most-cloned
repository (2,413 clones in the 14-day traffic window).

From 2020 through 2024, `csl-orig` ran in near-equilibrium: roughly 275–435 issues
opened per year and almost exactly as many closed (e.g. 433 opened / 440 closed in
2023). Then the equilibrium broke, in two asymmetric strokes:

| Year | Opened | Closed |
|---|---:|---:|
| 2023 | 433 | 440 |
| 2024 | 276 | 278 |
| **2025** | **1,023** | **130** |
| **2026 (Jan–May)** | **45** | **923** |

In 2025, a systematic correction campaign — batch-filing correction reports against
the dictionary source text — opened 1,023 issues while only 130 closed: an intake
wave that single-handedly drove the organisation-wide backlog to its all-time peak
of 1,742 open issues. In the first five months of 2026 the wave inverted: 923
closures against 45 openings, collapsing the repository's open count to just 68 at
the snapshot (11 of them silent). The organisation-wide cohort-survival table shows
the same signature from the other side: of all issues opened in 2025, 93% were
still open after 30 days — but only **5%** after a year, the *lowest* one-year
survival of any cohort in the ecosystem's history. Issues filed in bulk were also
resolved in bulk.

Three observations generalise from this trajectory. First, the ecosystem's natural
work unit is the **campaign**: a concentrated, months-long wave of filing followed
by a concentrated wave of resolution, visible as a sawtooth in the backlog curve —
not the steady drip that "maintenance" usually connotes. Second, campaigns are
*load-tested against the concentration finding*: the 2026 resolution wave was
executed by the same handful of people who carry 97.6% of all contributions, plus
newly-arrived agent tooling — the backlog fell because the trio's capacity
temporarily spiked, not because the contributor base grew. Third, the campaign
rhythm explains the taxonomy dip of Section 3.3: bulk intake outruns classification,
so process metrics sampled mid-campaign (the 2026 conformance of 39%) can look like
regressions when they are actually phase artifacts. Maintenance observability for
scholarly data must therefore be read *campaign-aware*, or it will misdiagnose its
healthiest events.

## 5. Discussion

**What the profile says.** Measured as a software organisation, CDSL is
simultaneously robust and fragile. Robust: no stale repositories, a 6-day median
issue close, rising throughput, a completed licensing campaign, and demonstrated
capacity to cut a 1,742-issue backlog nearly in half (to 913) within a year. Fragile: every one of those
capabilities is embodied in three people, 65 repositories would lose their majority
maintainer to a single departure, and the four-year-old tail of the backlog (620
issues) marks the work that never intersects a campaign. The ecosystem's health is
not an average of these two facts; it is their coexistence.

**Campaigns as the sustainability mechanism.** The case study suggests that for
volunteer-scale scholarly infrastructure, the campaign — not continuous integration
of small contributions — is the realistic sustainability mechanism. The license
rollout (Section 3.2) and the correction wave (Section 4) both show bounded,
tool-assisted campaigns succeeding where years of steady-state effort had not.
The policy implication for similar projects is to *design for campaigns*: keep
backlogs classified so a campaign can be scoped, keep sources under version
control so a campaign's effects are auditable, and keep an observatory running so
a campaign's completion is verifiable.

**What GitHub metrics cannot claim.** These are process metrics, not quality
metrics: 923 closed issues say nothing about whether the underlying corrections
were philologically right (that is A12's question), and contribution counts are a
poor proxy for scholarly effort — a one-line fix to a Vedic accent may cost more
expertise than a hundred mechanical commits. We also make no labour-valuation
claims. The metrics bound what can be said: they observe the *shape* of
maintenance, reliably and reproducibly, and that shape was previously invisible.

**Generalisation.** Nothing in the method is Sanskrit-specific. Any long-running
scholarly data organisation on a forge — critical editions, corpus projects,
linguistic databases — could stand up the same observatory (the code is GPL-3.0)
and obtain the same six-instrument profile. We conjecture the CDSL profile is
typical of the class: high-throughput, hyper-concentrated, campaign-driven,
infrastructure-consumed, and star-invisible. Testing that conjecture across
organisations is the natural next study.

## Data and code availability

All snapshot data, finding scripts, reports, and the dashboard source are public in
[`sanskrit-lexicon/csl-observatory`](https://github.com/sanskrit-lexicon/csl-observatory)
(code GPL-3.0, data CC-BY-4.0 per `DATA_LICENSE.md`). The dashboard is live at
https://sanskrit-lexicon.github.io/csl-observatory/. Every figure in this article
appears in a committed report generated by a committed script over the committed
`2026-06` snapshot ([`data/manifest.json`](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/data/manifest.json)).

## References

Avelino, G., Passos, L., Hora, A., & Valente, M. T. (2016). A novel approach for
estimating truck factors. *Proceedings of the 24th IEEE International Conference on
Program Comprehension (ICPC)*, 1–10.

Böhtlingk, O., & Roth, R. (1855–1875). *Sanskrit-Wörterbuch* (7 vols.). St.
Petersburg: Kaiserliche Akademie der Wissenschaften.

Eghbal, N. (2020). *Working in Public: The Making and Maintenance of Open Source
Software*. San Francisco: Stripe Press.

Kalliamvakou, E., Gousios, G., Blincoe, K., Singer, L., German, D. M., & Damian, D.
(2014). The promises and perils of mining GitHub. *Proceedings of the 11th Working
Conference on Mining Software Repositories (MSR)*, 92–101.

Monier-Williams, M. (1899). *A Sanskrit–English Dictionary*. Oxford: Clarendon
Press.

Wilkinson, M. D., Dumontier, M., Aalbersberg, I. J., et al. (2016). The FAIR
Guiding Principles for scientific data management and stewardship. *Scientific
Data*, 3, 160018.

Wilson, H. H. (1832). *A Dictionary in Sanscrit and English* (2nd ed.). Calcutta:
Education Press.

**Companion articles (this project):** the narrative report (A13,
[`article/00-report-narrative.md`](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/article/00-report-narrative.md))
and the empirical companion (A14,
[`article/01-empirical-companion.md`](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/article/01-empirical-companion.md)),
both in preparation; the error-typology resource paper (A12,
[`reports/obs_t_paper_draft.md`](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/reports/obs_t_paper_draft.md)).

_Dr. Mārcis Gasūns_
