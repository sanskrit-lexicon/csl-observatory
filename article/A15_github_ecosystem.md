# Measuring the Cologne Digital Sanskrit Dictionaries as a GitHub Maintenance Ecosystem

_Created: 03-07-2026 · Last updated: 11-07-2026_

**Status (11-07-2026):** full draft (H672 pass, Fable 5 `claude-fable-5`), paper A15;
advanced from the 03-07 skeleton by folding in the correction-event ledger
(52,498 events), the data-layer bus-factor instrument, the correction-loop anatomy,
and the claim→artifact inventory. Sequencing: the
[FABLE index](https://github.com/gasyoun/Uprava/blob/main/FABLE_UNTOUCHED_INDEX.md)
schedules A15 after A13/A14, but this draft depends on neither of them *shipping* —
A13 is GO-conditional for IIJ and A14 is ORCID-gated; only A15's eventual **submission**
should wait on their venue outcomes. Venue: TBD (@DECIDE — likely the same
LREC/JOHD-family as A13/A14; a human decides). Byline: pending MG ruling.

**Draft byline:** Mārcis Gasūns

## Abstract

Long-running digital lexicography projects are usually described through their
content — entries digitised, dictionaries released — while the *maintenance labour*
that keeps the content alive stays invisible. This article treats the Cologne
Digital Sanskrit Dictionaries (CDSL), a digitisation programme spanning more than
three decades, as a **GitHub maintenance ecosystem** and measures it with the
reproducible instruments of repository mining: contributor concentration, repository
hygiene, issue lifecycle, taxonomy conformance, activity velocity, external
reach, and — new to this class of study — the *correction throughput of the data
layer itself*. Against a snapshot of 76 repositories, 5,324 issues, and 9,877
commits (2014–2026), we find a paradoxical profile: throughput is high and rising
(a record 2,519 commits in 2026), yet 65 of 76 repositories depend on a single
maintainer, three people account for 97.6% of all contributions, and 620 open
issues are more than four years old. The fragility extends below the code: a
ledger of 52,498 individual text-correction events (2014–2026) shows that in no
year did more than four people correct dictionary text, with the lead corrector
carrying 64–100% of each year's corrections — and that while 206 people have
*reported* corrections, the capacity to *apply* them has rested with five. A case study of the `csl-orig`
correction campaign of 2025–2026 — 1,023 issues opened in one year, 923 closed
the next — shows that the ecosystem's characteristic rhythm is the *correction
wave*, not steady-state maintenance, a rhythm the correction ledger traces back
to 2015. We argue that GitHub-native metrics, properly bounded, give digital
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
the seven maintenance findings — six platform-level instruments plus a
data-layer instrument that measures correction throughput over the dictionary
text itself. Section 4 anatomises the correction loop: the workflow that turns an
error report into a source change, the twelve-year ledger of 52,498 individual
correction events it has produced, and the `csl-orig` correction campaign of
2025–2026, the largest single maintenance event in the ecosystem's recorded
history. Section 5 discusses what the profile implies for the sustainability of
scholarly data organisations. An appendix inventories every headline claim
against the committed artifact it recomputes from.

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
events. The division is sharpest over the correction-event ledger of Section 4.2:
A12 owns its *typed* columns (edit operations, error components, OCR/text-critical
classes), A15 uses only its *process* columns (date, provenance layer, volume).
Overlap is limited to shared provenance (the same snapshot data) and is cited,
not restated.

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

Three further committed datasets serve the data-layer instruments of Sections 3.7
and 4.2 (paths under
[`observatory/site/src/data/`](https://github.com/sanskrit-lexicon/csl-observatory/tree/main/observatory/site/src/data);
the two layer files each carry a sidecar `.meta.json` recording generation time,
source path, and assumptions, and the merged file's provenance — including its
52,498-row total — is recorded in the git-layer sidecar):

| Dataset | Rows | Content |
|---|---:|---|
| [`correction_events_all.csv`](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/observatory/site/src/data/correction_events_all.csv) | 52,498 | merged correction-event ledger, both provenance layers, 2014–2026 |
| [`correction_events.csv`](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/observatory/site/src/data/correction_events.csv) | 24,441 | form layer: correction-form exports (`cfr.tsv`, [CORRECTIONS](https://github.com/sanskrit-lexicon/CORRECTIONS)), 2014–2019 |
| [`correction_events_git.csv`](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/observatory/site/src/data/correction_events_git.csv) | 28,057 | git layer: line-level diffs of `csl-orig/v02` dictionary sources, 2019–2026 |

(The `_typed` and `_final` variants of the merged ledger add classification
columns — those belong to A12 and are not used here.) The data-layer bus-factor
finding (Section 3.7) additionally draws on the sibling
[`csl-orig`](https://github.com/sanskrit-lexicon/csl-orig) git history (1,849
dictionary-correction commits, 2019–2026) and the cached issue latencies of the
[`csl-corrections`](https://github.com/sanskrit-lexicon/csl-corrections) tracker,
as computed in
[`reports/obs_q_correction_sustainability.md`](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/reports/obs_q_correction_sustainability.md).

Two caveats govern every downstream number. First, `contributors.csv` holds 209
*per-repository* rows, not 209 people; after alias-merging, the organisation has
**16 distinct human contributors** in the snapshot window (three bot logins are
excluded; the generated bus-factor report's headline of 17 still counts the
`actions-user` CI bot — a known generator defect, flagged for repair). Second, per-repo author
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
90%. None of the 16 human contributors has a registered ORCID (per the
alias-merged identity worksheet,
[`reports/contributor_identity.md`](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/reports/contributor_identity.md)),
which compounds the
concentration problem with an attribution problem: the labour is not only
concentrated, it is also invisible to scholarly credit systems.

### 3.2 Repository hygiene: recoverable, and largely recovered

(Source: [`reports/repo_health.md`](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/reports/repo_health.md),
audit of 2026-06-20.)

Hygiene tells a more hopeful story, because it is the one dimension where a
targeted campaign already ran. A 2026 license rollout took the organisation from 41
unlicensed repositories (the pre-rollout count, recorded in
[`reports/coverage.md`](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/reports/coverage.md))
to **6** (all archival/temp candidates), with 70/76 now
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
fully conformant**. The adoption curve is instructive: conformance among the
pre-runbook cohorts (2014–2018) sits at 6–25% — the 6% floor being 2018, the
last pre-runbook year — jumps to a 92% peak for the 2025 cohort under the
runbook, then **dips to 39% for 2026** — freshly opened issues outrun the
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
times** by ~1,814 unique cloners, and 18 distinct external projects — the union
of 10 curated downstream libraries/applications and a partly overlapping set of
17 code-search-visible repositories (9 of the 10 curated appear in both tiers) —
ship or wrap CDSL data. The star-to-clone disproportion is the finding: CDSL is consumed
as *infrastructure* — cloned, mirrored, embedded — not favourited as a project.
Any evaluation of scholarly data organisations that reads popularity metrics will
systematically underrate them.

### 3.7 The data layer: correction throughput is single-person-burst-driven

(Source: [`reports/obs_q_correction_sustainability.md`](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/reports/obs_q_correction_sustainability.md),
generated by [`scripts/obs_q_correction.py`](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/scripts/obs_q_correction.py)
from the `csl-orig` git history and cached `csl-corrections` issue latencies.)

The six instruments above measure the platform. The seventh measures the thing
the platform exists for: correction of the dictionary text itself. Across 1,849
commits touching `csl-orig`'s dictionary sources (2019–2026), **no year had more
than four distinct content correctors**, and the lead corrector's annual share
ranged from 64% to 100% — 2020 was literally a single-corrector year (269
commits, one person). Of the 37 dictionaries with at least ten correction
commits, every one is dominated by a single corrector, and four exceed an 80%
lead share. Resolution latency over the 244 tracked correction issues is
bimodal in exactly the pattern of Section 3.4: a **6-day median** against a
155.7-day mean, a 457-day 90th percentile, and a 6.4-year maximum — and the
55-issue tail is dominated by low-severity questions and enhancements, the
signature of a single maintainer triaging by severity, not of a blocked
pipeline. Throughput, moreover, tracks the lead corrector's bursts rather than
crew size: counted by correction-classified commits (the report's preferred
throughput unit, which excludes imports and infrastructure noise), the busiest
year — 2021, with 248 corrections — had three correctors, both four-corrector
years rank below it, and the single-corrector year 2020 still landed 105. The
bus-factor problem of Section 3.1 is therefore not merely a *code* risk; the
**data itself has a bus factor**, and it is one.

## 4. The correction loop

The findings above describe stocks and distributions. This section describes the
ecosystem's central *process* — the loop that turns an error report into a
changed dictionary source — first structurally, then through the twelve-year
event ledger it has produced, and finally through its largest recorded
oscillation, the 2025–2026 `csl-orig` campaign.

### 4.1 Anatomy of the loop

A correction to a CDSL dictionary never edits the published display directly.
The canonical path, documented in the workflow guide of the
[`csl-corrections`](https://github.com/sanskrit-lexicon/csl-corrections/blob/main/docs/correction-workflow.md)
repository, is: (1) an error is reported — as a GitHub issue against the
dictionary's repository, or historically through a web **correction form**
whose submissions were archived as tab-separated exports in the
[CORRECTIONS](https://github.com/sanskrit-lexicon/CORRECTIONS) repository;
(2) the fix is expressed as a machine-readable **change file** recording the
exact line, the old text, and the new text; (3) the change is applied by script
to the canonical source text in
[`csl-orig`](https://github.com/sanskrit-lexicon/csl-orig), never by hand to a
derived artifact — and a second, diff-generated change file is committed
afterwards to the corrections archive as the audit trail that outlives the
edit (the workflow guide is explicit that the archived change files are records
*of* edits, not inputs *to* them); (4) display artifacts across the public interfaces are
regenerated from the changed source by scheduled server-side jobs; (5) the
originating issue is closed with cross-links to the applying commit. Since the
arrival of agent-assisted tooling (2026), delivery has additionally been
*batched*: corrections accumulate locally and ship as consolidated
multi-correction pull requests rather than per-fix streams
(the archive's
[batch runbook](https://github.com/sanskrit-lexicon/csl-corrections/blob/main/docs/BATCH_RUNBOOK.md)
mandates one consolidated PR per batch), deliberately shaped
to maintainer attention. Two properties matter for measurement: every step
leaves a timestamped trace, and the traces are independent of the people —
which is what makes a longitudinal ledger possible at all.

### 4.2 Twelve years of correction events: the ledger

*(Source: the merged
[`correction_events_all.csv`](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/observatory/site/src/data/correction_events_all.csv);
provenance and assumptions in the sidecar
[`.meta.json`](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/observatory/site/src/data/correction_events_git.meta.json)
files. Only the process columns — date, provenance layer, volume — are used
here; the typed content of the same events is A12's subject.)*

Reconstructed from both trace layers, the loop has processed **52,498
individual text-correction events** between 2014-03-18 and 2026-05-30: 24,441
from the correction-form era (2014–2019, archived form exports) and 28,057 from
the git era (2019–2026, line-level diffs of the dictionary sources). The annual
series is anything but steady:

| Years | Events | Share | Phase |
|---|---:|---:|---|
| 2014 | 2,088 | 4% | form era opens |
| 2015–2016 | 21,518 | 41% | the first great wave |
| 2017–2019 | 892 | 2% | trough |
| 2020–2021 | 7,540 | 14% | second wave (git era) |
| 2022–2023 | 5,487 | 10% | steady state |
| 2024–2026 (May) | 14,973 | 29% | third wave, ongoing |

Two years — 2015 and 2016 — carry 41% of twelve years of corrections; the
2017–2019 trough processed under 450 events a year; and the current wave
(5,244 in 2024, 5,392 in 2025, already 4,337 by May 2026) is the strongest
since the first. The maintainers' own hand-kept campaign log (analysed in
[`reports/obs_t_campaigns.md`](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/reports/obs_t_campaigns.md):
361 dated entries, 34,971 corrections with stated magnitudes) confirms that the
first wave was explicitly campaign-structured — discrete, named passes such as
the literary-source-abbreviation sweeps over the Petersburg lexicon (a single
pass of 3,015 corrections in December 2015) — and that even the trough was
punctuated by bulk passes, such as a ~4,500-correction IAST-encoding conversion
in September 2018 (the hand log records work at stages the event ledger does
not capture, which is why a trough-era campaign need not surface as ledger
events). Campaigns are not a recent invention of the
issue-tracker era; they are how this ecosystem has always metabolised
correction work. What changed across the ledger is *observability*: the form
era recorded submissions, the git era records applications, and the current
wave is the first to be fully issue-tracked end to end.

The ledger also quantifies the funnel between *reporting* an error and
*applying* its fix. The `corrector` column names **206 distinct submitters**
across the form-era events but only **5 distinct appliers** across the git-era
events — the crowd could always report, and did, in the hundreds; the capacity
to change the canonical text has never rested with more than a handful of
people (Section 3.7 puts it at ≤4 in any single year). Correction *reporting*
is crowd-shaped; correction *application* is the bottleneck the bus-factor
instruments measure.

### 4.3 The largest oscillation: the `csl-orig` campaign of 2025–2026

*(Per-repository figures computed from the committed
[`issues.csv`](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/observatory/site/src/data/issues.csv),
snapshot 2026-06; PRs excluded via the `kind` column.)*

As the canonical source repository — the terminus of every loop iteration of
Section 4.1 — [`csl-orig`](https://github.com/sanskrit-lexicon/csl-orig) is
also the ecosystem's centre of gravity: 2,801
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
survival of any cohort with an observable one-year horizon (the 2026 cohort is
right-censored: no issue opened in 2026 had existed a year at the snapshot).
Issues filed in bulk were also resolved in bulk.

Three observations generalise from this trajectory. First, the ecosystem's natural
work unit is the **campaign**: a concentrated, months-long wave of filing followed
by a concentrated wave of resolution, visible as a sawtooth in the backlog curve —
not the steady drip that "maintenance" usually connotes. The event ledger of
Section 4.2 shows this is constitutive, not episodic: the same sawtooth appears
in 2015–2016 and 2020–2021, long before the present tooling. Second, campaigns
are *load-tested against the concentration findings*: the 2026 resolution wave
was executed by the same handful of people who carry 97.6% of all contributions
(and, per Section 3.7, by at most four content correctors in any year), plus
newly-arrived agent tooling — the backlog fell because the core group's capacity
temporarily spiked, not because the contributor base grew. Third, the campaign
rhythm explains the taxonomy dip of Section 3.3: bulk intake outruns classification,
so process metrics sampled mid-campaign (the 2026 conformance of 39%) can look like
regressions when they are actually phase artifacts. Maintenance observability for
scholarly data must therefore be read *campaign-aware*, or it will misdiagnose its
healthiest events.

### 4.4 Postscript: the agent-assisted maintenance layer (beyond the snapshot)

*(This subsection reports events after the `2026-06` snapshot closes; its
figures come from the project's maintenance ledger and are verifiable against
the public pull-request record of the organisation's repositories, but they are
not regenerable from the committed snapshot and are therefore kept out of the
findings of Section 3.)*

The 2026 uptick in pull requests (Section 3.5) marks a structural change in who
executes campaigns. Beginning in mid-2026, LLM-based coding agents became a
routine maintenance instrument: they prepare corrections as change files,
deliver them as consolidated batched pull requests (Section 4.1), and run
org-wide hygiene campaigns that were previously too labour-expensive to
contemplate. The scale is of a different order: in a single two-day
documentation campaign (10–11 July 2026), agent sessions audited every
repository in the maintenance perimeter and landed **117 merged
README-refresh pull requests** — 48 across dictionary repositories, 33 across
tooling repositories, 36 across research and product repositories — each
individually reviewed and merged. The retroactive issue-taxonomy conformance of
Section 3.3 was likewise applied by agent-assisted runbooks. For the
sustainability question this cuts both ways. Agent capacity multiplies the
output of the existing three maintainers — campaigns that took years now take
days — but it multiplies *their* output: the agents are operated by the same
concentrated group, so the bus factor of Sections 3.1 and 3.7 is unchanged, and
arguably better hidden, since throughput metrics now look healthier than the
underlying human redundancy is. An observatory that counts only commits and
closures will read an agent-amplified ecosystem as flourishing; the
concentration instruments are what keep the reading honest.

## 5. Discussion

**What the profile says.** Measured as a software organisation, CDSL is
simultaneously robust and fragile. Robust: no stale repositories, a 6-day median
issue close, rising throughput, a completed licensing campaign, and demonstrated
capacity to cut a 1,742-issue backlog nearly in half (to 913) within a year. Fragile: every one of those
capabilities is embodied in three people, 65 repositories would lose their majority
maintainer to a single departure, and the four-year-old tail of the backlog (620
issues) marks the work that never intersects a campaign. The data-layer
instrument sharpens the fragility: it is not only the *code* that depends on
individuals but the ongoing correction of the dictionary text itself — at most
four content correctors in any year of a twelve-year, 52,498-event ledger. The
ecosystem's health is not an average of these two facts; it is their
coexistence.

**Campaigns as the sustainability mechanism.** The case study suggests that for
volunteer-scale scholarly infrastructure, the campaign — not continuous integration
of small contributions — is the realistic sustainability mechanism. The license
rollout (Section 3.2), the historical correction waves of the event ledger
(Section 4.2), and the 2025–2026 issue wave (Section 4.3) all show bounded,
tool-assisted campaigns succeeding where years of steady-state effort had not —
and the agent postscript (Section 4.4) shows the campaign form absorbing new
tooling without changing shape. The policy implication for similar projects is
to *design for campaigns*: keep backlogs classified so a campaign can be
scoped, keep sources under version control so a campaign's effects are
auditable, and keep an observatory running so a campaign's completion is
verifiable.

**What agents change, and what they do not.** If the mid-2026 pattern holds,
the marginal cost of a maintenance campaign is collapsing: work that was
bounded by volunteer hours is increasingly bounded by review attention. That
relieves the throughput half of the profile and leaves the concentration half
untouched — the reviewing humans are the same three people, and the correction
ledger's data-layer bus factor (Section 3.7) does not improve when the drafting
is delegated. The honest framing is that agents convert a labour shortage into
a *governance* concentration: more of the ecosystem's output now flows through
fewer human decision points per unit of change. Observatories for scholarly
infrastructure should therefore begin distinguishing authored from reviewed
contribution — a distinction GitHub's data model does not natively surface.

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
and obtain the same seven-instrument profile. We conjecture the CDSL profile is
typical of the class: high-throughput, hyper-concentrated, campaign-driven,
infrastructure-consumed, and star-invisible. Testing that conjecture across
organisations is the natural next study.

## Appendix: claim → artifact inventory

Every headline figure in this article, the committed artifact it recomputes
from, and its status (✅ committed and regenerable offline · ⚠️ committed but
refreshed from a live API tier · ⬜ post-snapshot, not in the reproducibility
envelope). Artifact paths are in
[`sanskrit-lexicon/csl-observatory`](https://github.com/sanskrit-lexicon/csl-observatory)
unless stated.

| # | Claim | Artifact | Status |
|---|---|---|:--:|
| 1 | 76 repos · 5,413 issues+PRs (5,324 issues, 89 PRs) · 9,877 commits · snapshot `2026-06` | [`data/manifest.json`](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/data/manifest.json) | ✅ |
| 2 | 16 distinct human contributors after alias-merging (3 bot logins excluded; the bus-factor report's headline "17" counts the `actions-user` bot — generator defect, flagged) | [`reports/contributor_identity.md`](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/reports/contributor_identity.md) + [`data/people_summary.csv`](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/data/people_summary.csv) | ✅ |
| 3 | Bus factor 1 in 65/76 repos; top contributor 51.8%; trio 97.6%; Gini 0.861; zero ORCIDs | [`reports/bus_factor.md`](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/reports/bus_factor.md) | ✅ |
| 4 | Licenses 41→6 unlicensed; 70/76 SPDX; 46 on `master`; zero stale repos | [`reports/repo_health.md`](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/reports/repo_health.md) (post-rollout state) + [`reports/coverage.md`](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/reports/coverage.md) (pre-rollout 41) | ✅ |
| 5 | 89% type-labelled; 63% fully conformant; 92% peak (2025) vs 39% (2026) | [`reports/taxonomy_adoption.md`](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/reports/taxonomy_adoption.md) | ✅ |
| 6 | 6-day median close; p90 349 d; 719/913 open issues >2 y; 620 >4 y; 178 silent | [`reports/issue_lifecycle.md`](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/reports/issue_lifecycle.md) | ✅ |
| 7 | Peak years 2,519 commits (2026) / 1,178 issues (2025); ≤11 authors in any year; 89 PRs lifetime, 59% in 2026 | [`reports/velocity_timeline.md`](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/reports/velocity_timeline.md) | ✅ |
| 8 | 103 stars; 49 zero-star repos; 6,923 clones / ~1,814 cloners per 14-day window; 18 downstream projects (union derived from the report's 10 curated + 17 code-search tiers) | [`reports/external_reach.md`](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/reports/external_reach.md) (API tiers fetched 2026-07-03) | ⚠️ |
| 9 | 1,849 correction commits (2019–2026); ≤4 correctors/year; lead share 64–100%; 4/37 dicts ≥80% lead | [`reports/obs_q_correction_sustainability.md`](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/reports/obs_q_correction_sustainability.md) | ✅ |
| 10 | 244 correction issues; median 6 d / mean 155.7 d / p90 457 d / max 2,337 d; 55-issue tail | same as #9 | ✅ |
| 11 | 52,498 correction events; form 24,441 (2014-03-18 – 2019-07-21) + git 28,057 (2019-11-04 – 2026-05-30) | [`correction_events_all.csv`](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/observatory/site/src/data/correction_events_all.csv) + the two layer sidecar metas ([form](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/observatory/site/src/data/correction_events.meta.json), [git](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/observatory/site/src/data/correction_events_git.meta.json)) | ✅ |
| 12 | Annual wave table of Section 4.2 (2015–16 = 41%; 2017–19 trough; 2024–26 = 29%); 206 form-era submitters vs 5 git-era appliers | recomputed from #11 (`date`, `source_layer`, `corrector` columns) | ✅ |
| 13 | Hand-log campaigns: 361 dated entries, 34,971 stated corrections; 3,015-correction PW pass (Dec 2015); ~4,500 IAST pass (2018) | [`reports/obs_t_campaigns.md`](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/reports/obs_t_campaigns.md) | ✅ |
| 14 | `csl-orig` opened/closed table (1,023 opened 2025; 923 closed Jan–May 2026; 68 open at snapshot); 2025 cohort 5% one-year survival | [`observatory/site/src/data/issues.csv`](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/observatory/site/src/data/issues.csv) + [`reports/issue_lifecycle.md`](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/reports/issue_lifecycle.md) | ✅ |
| 15 | 117 merged agent-authored README PRs (48 dict + 33 tooling + 36 research/product), 10–11 July 2026 | maintenance ledger; verifiable against the public PR record of the audited repositories | ⬜ |

## Data and code availability

All snapshot data, finding scripts, reports, and the dashboard source are public in
[`sanskrit-lexicon/csl-observatory`](https://github.com/sanskrit-lexicon/csl-observatory)
(code GPL-3.0, data CC-BY-4.0 per `DATA_LICENSE.md`). The dashboard is live at
https://sanskrit-lexicon.github.io/csl-observatory/. Every figure in this article
— apart from the explicitly post-snapshot postscript of Section 4.4 (inventory
row 15) — appears in a committed report generated by a committed script over the
committed `2026-06` snapshot
([`data/manifest.json`](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/data/manifest.json)).

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
