---
title: "Methodological infrastructure of the Cologne Digital Sanskrit Dictionaries"
subtitle: "A quantitative companion to Gasūns, *Report on Cologne Digital Sanskrit Lexicon Project* (forthcoming)"
author:
  - name: Jim Funderburk
    affiliation: Cologne Digital Sanskrit Dictionaries
    orcid: PLACEHOLDER-FUNDERBURK
  - name: Dhaval Patel
    affiliation: Cologne Digital Sanskrit Dictionaries
    orcid: PLACEHOLDER-PATEL
  - name: Nagabhushana Rao Kālepu
    affiliation: Andhrabharati
    orcid: PLACEHOLDER-RAO
  - name: Mārcis Gasūns
    affiliation: Sanskrit Zealots's Society / Russia, Obninsk
    orcid: 0000-0003-4513-884X
    email: gasyoun@gmail.com
date: 2026-07-11
abstract: |
  This article is a quantitative and methodological companion to Gasūns
  (*Report on Cologne Digital Sanskrit Lexicon Project*, forthcoming),
  hereafter "the report", which surveys the thirty-year history of the
  Cologne Digital Sanskrit Dictionaries (CDSL) in a reflective scholarly
  voice. Where the report tells the story of the project — its founders,
  its disputes, its lost archives, its hopes for the next half-century —
  this companion documents the present state of the project as a digital
  infrastructure, in numbers and standards. We describe the unified
  issue-taxonomy and triage runbook applied across eight active
  dictionary repositories in 2026; we present a complete data snapshot of
  the ecosystem (78 repositories, 5,172 issues and pull requests, 3,979
  captured commits, 49 distinct
  contributors after alias merge); we demonstrate the path from CDSL's
  plain-text source format to TEI Lex-0 and OntoLex-Lemon RDF; and we
  evaluate the project against the FAIR data principles and ELEXIS
  infrastructure recommendations. The data behind every figure and table
  is publicly archived in the `csl-observatory` repository under CC BY
  4.0 and is regenerable by running a single Python pipeline.
keywords:
  - Sanskrit lexicography
  - Cologne Digital Sanskrit Dictionaries
  - digital humanities
  - TEI Lex-0
  - OntoLex-Lemon
  - FAIR principles
  - lexicographic infrastructure
bibliography: refs.bib
csl: indo-iranian-journal.csl
link-citations: true
papersize: a4
fontsize: 11pt
geometry: margin=2.5cm
---

# 1. Introduction

The Cologne Digital Sanskrit Dictionaries are presented in two voices in the
present pair of articles. The narrative report by Gasūns (forthcoming) speaks
in the first person from a vantage of three decades of personal involvement;
it traces the project from its origin in Thomas Malten's Cologne Indology
seminar in 1994, through Peter Scharf's 2004 collaboration at Brown, the
GitHub migration in 2014, and the contributor influx of the 2020s. It argues,
with reference to specific entries, archives, and email exchanges, that the
project remains the global standard for printed-source Sanskrit lexicography
and that its future depends on volunteer crowdsourcing.

This companion paper undertakes a different task. Where the report cites
arguments, anecdotes, and unpublished correspondence, this paper provides
counts, distributions, and methodological codifications drawn from a complete
empirical snapshot of the `sanskrit-lexicon` GitHub organisation as of 2026.
The two papers are intended to be read together: the report supplies
historical, scholarly, and editorial context; the present companion documents
the contemporary digital infrastructure and the standards against which it
should be evaluated.

We focus on four contributions.

1. **The 2026 issue-taxonomy runbook** (§3): we describe the unified
   labelling, milestone, and project taxonomy applied across eight active
   dictionary repositories in 2026, together with the seventeen-phase
   autonomous runbook (numbered 0–16) whose triage core produces it.

2. **An ecosystem-wide data snapshot** (§4): we present the first complete
   quantitative survey of the CDSL ecosystem — 78 repositories, 5,172 issues
   and pull requests, 3,979 captured commits, 49 distinct contributors — and
   analyse the distribution of
   issue types, contributor labour, and activity over the project's
   thirteen-year GitHub history (2014–2026).

3. **A standards alignment** (§5): we evaluate the project against TEI Lex-0
   [@romary2019teilex0], OntoLex-Lemon [@cimiano2016ontolex], the FAIR
   principles [@wilkinson2016fair], and the European Lexicographic
   Infrastructure (ELEXIS) recommendations [@krek2018elexis]. We demonstrate,
   through a worked example, the conversion path from CDSL's `<L>...<LEND>`
   plain-text format to TEI-conformant XML.

4. **The `csl-observatory` infrastructure** (§6): we describe the reproducible
   data-aggregation pipeline that produces every figure in this paper and
   supports continuous monitoring of the ecosystem.

We close with limitations (§7) and with a programme of future work that
follows from both this paper and the report (§8).

# 2. Relationship to the narrative report

The report (in its "Evolution of Data Formats" and "Encoding Standard"
sections) recounts the evolution of the source format from Malten's
original `MONIER.ALL` numerical-marker encoding, through Hyman's XML
intervention, to the present `<L>...<LEND>` line-oriented format. It also
reproduces a side-by-side example of the entry *kuJjakuTIra* in 1997 and 2025
encodings. We accept these technical findings as given and use them as the
starting point for the data dictionary in §3.5 below.

The report (in "Team Members", subsection "Major Cologne Contributors
1994-2025") lists the major contributors with year spans:
Thomas Malten (1994–2013), Peter Scharf (2004–2013), Malcolm D. Hyman
(2004–2009), Jim Funderburk (2004–2025), Sampada Savardekar (2014–2023),
Mārcis Gasūns (2014–2025), Dhaval Patel (2014–2021), Nagabhushana Rao
Kālepu (2021–2025), and Scott Rhodes (2024–2025). Our data (§4.5)
extends this list with empirical commit and issue counts, exposes several
aliases — chiefly Cologne SSH dialog hostnames — that have to be merged for
accurate attribution, and corrects one span empirically: Patel's commit
record runs from November 2015 through 2026, past the report's 2014–2021
window.

The report's headline figures — "over 5,400 issues and pull requests across
76 repositories" by 2025 (abstract), "over 390,000" normalised entries
(abstract), and the lemma and citation counts quoted in §4.8 below (168633
MW lemmas, 106169 PWG lemmas, 67138 Mahābhārata references) — are
reproduced and
contextualised where relevant. Our own snapshot (2026-05-07) records 5,172
issue records across the organisation, of which 37 are pull requests, both
open and closed states included. The report's slightly larger figure rests
on a later census — the June 2026 transformation pass (`data/manifest.json`)
counts 5,413 issue-and-pull-request records across the 76 canonical
(non-fork) repositories — and the gap between the two is ordinary June-2026
growth plus the differing repository census (our 78 includes two forks).
Where exact reconciliation is needed for an individual claim, we indicate it.

# 3. The 2026 issue-taxonomy runbook

The report observes (in its "Encoding Standard" section) that issues
"quickly piled up between 2014
and 2024 not so quickly to be solved", that "csl-orig, CORRECTIONS,
cologne-stardict, csl-apidev, csl-corrections, csl-pywork, csl-websanlexicon,
MWS, PWK, hwnorm1 [are the] most active [repositories]", and that "some of
them will remain unsolved, but at least documented". In 2026 the project
undertook a systematic triage of issues across its dictionary repositories,
motivated by precisely this observation: an unresolved issue is more useful
than a deleted one, but only if it is classified, prioritised, and attached
to a long-lived programme of work.

The triage applies a consistent vocabulary to every issue in eight active
dictionary repositories — AP, AP90, FRI, GRA, MD, MWS, PWG, PWK — and
deposits the result in a four-quadrant kanban board mirrored as four GitHub
Projects (V2). The vocabulary, the assignment rules, and the runbook that
automates the application are described below.

## 3.1 Type labels (nine)

Every triaged issue carries exactly one type label, drawn from the following
set. The colour code (`#0075ca`, GitHub blue) is shared across all type
labels to signal their syntactic equivalence.

| Label | Definition |
|---|---|
| `link-target` | A hyperlink from a `<ls>` (literary source) abbreviation to scanned PDF pages of the cited print edition. The work involves researching the source, constructing an index of pages, and installing links across all dictionaries that cite the source. |
| `link-splitting` | The decomposition of combined `SOURCE N,N` references into individual per-page links. |
| `markup` | The normalisation of XML tag content or structure (`<ls>`, `<lex>`, `<ab>`, etc.). |
| `text-correction` | A correction to a German or English definition or to a Sanskrit headword. |
| `content-enhancement` | New material, display upgrades, or structural additions that go beyond correction. |
| `encoding` | SLP1/IAST/AS transcoding, character rendering (Greek, accents, diacritics), and hyphen/dash normalisation. |
| `scan-quality` | The replacement of blurry, skewed, or missing scan pages with clearer images. |
| `bug` | Broken links, XML structure errors, or broken download files. |
| `question` | A scholarly or editorial question requiring research before any code change. |

## 3.2 Severity labels (three)

Every triaged issue also carries exactly one severity label.

| Label | Definition |
|---|---|
| `minor` | A targeted, self-contained fix — a handful of lines or a single file. |
| `medium` | A standard unit of work — one link-target index, a batch of markup corrections. |
| `hard` | A large effort spanning many sources, files, or dictionaries. |

## 3.3 Milestones (four)

Each type label maps deterministically to one of four milestones, which in
turn mirror four organisation-level GitHub Projects (kanban boards).

| Milestone | Type labels |
|---|---|
| Dictionary to Book | `link-target`, `link-splitting` |
| Digitization Quality | `scan-quality`, `encoding`, `bug`, `text-correction` |
| Structured Data | `markup`, `question` |
| Major Enhancements | `content-enhancement` |

The four-milestone partition reflects a clean separation of editorial
concerns: linking the digital text to its printed source (DTB), correcting
errors introduced in digitisation (DQ), adding structural information beyond
what the print contains (SD), and substantive content extension (ME).

## 3.4 The runbook

Application of the taxonomy is codified as a seventeen-phase runbook
(numbered 0–16) executed
by a large language model agent (Claude Code) operating against the GitHub
REST and GraphQL APIs, the local file system, and `git`. The phases are:

| Phase | Action |
|---|---|
| 0 | Set repository variables; verify access. |
| 1 | Audit existing issues, labels, and milestones; auto-detect noise. |
| 2 | Create the nine type labels and three severity labels with canonical colours. |
| 3 | Assign exactly one type label per issue; remove conflicting GitHub-default labels. |
| 4 | Assign exactly one severity label per issue. |
| 5 | Create the four milestones; assign each issue to its milestone. |
| 6 | Add each issue to the corresponding GitHub Project. |
| 7 | Verify: every issue has exactly one type, exactly one severity, exactly one milestone, and is in exactly one project. |
| 8 | Generate `CLAUDE.md` (developer guidance) for the repository. |
| 9 | Generate `README.md` (public overview) with live counts and Mermaid charts. |
| 10 | Commit and push. |
| 11 | Add citation infrastructure: `CITATION.cff`, `LICENSE`, `CHANGELOG.md`, Zenodo–GitHub integration. |
| 12 | Add a printed-source bibliography block (publisher, year, volumes, scan provenance). |
| 13 | Add a data dictionary with annotated example entry. |
| 14 | Declare the encoding policy (UTF-8 NFC, SLP1 boundaries, round-trip status). |
| 15 | Generate a Mermaid pipeline diagram of the actual data flow from source to display. |
| 16 | Drop community files: `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`, `.github/ISSUE_TEMPLATE/`, pull-request template. |

Phases 0–10 — the triage core — were executed across the eight repositories
in 2026; Phases 11–16 are specified but not yet propagated (§8). Phase 7 is
enforced as a hard gate: all five integrity checks — missing type
label, missing severity, missing milestone, multi-type, and type/milestone
mismatch — must reach zero before the runbook proceeds to documentation. The
autonomy rules, encoding requirements, and pre-existing GitHub-default-label
collision protocol are documented separately in the runbook source, mirrored
publicly at `runbook/cologne-issue-runbook.md` in the `csl-observatory`
repository [@runbook2026].

## 3.5 Data dictionary

The CDSL plain-text record format described in the report's "Data
Structure" section is here
codified into the following data dictionary, which is reproduced in every
triaged repository's `CLAUDE.md` per Phase 13.

| Tag | Semantic role | Example |
|---|---|---|
| `<L>NNNN` | Entry begin; `<pc>` carries the print page,column reference | `<L>51478<pc>288,1` |
| `<LEND>` | Entry end | |
| `<k1>` | Primary headword in SLP1 | `<k1>kuYjakuwIra` |
| `<k2>` | Secondary spelling, with compound-seam separator | `<k2>kuYja—kuwIra` |
| `<e>N` | Etymology marker / homonym index | `<e>3` |
| `<lex>` | Lexical category (part of speech) | `<lex>m.</lex>` |
| `<ls>` | Literary source citation | `<ls>Mālatīm.</ls>` |
| `<ab>` | Italicised abbreviation | `<ab>m.</ab>` |
| `<s>` | Sanskrit text in display layer | `<s>kuYja—kuwIra</s>` |
| `<info>` | Structured metadata | `<info lex="m"/>` |
| `{#…#}` | Sanskrit text in SLP1 inline | `{#rAmaH#}` |
| `{%…%}` | Italicised display text | `{%abc%}` |
| `{{Lbody=NNN}}` | Cross-reference to parent entry | `{{Lbody=159.1}}` |

The full set of 67 unique tags observed across all repositories is recorded
in the `COLOGNE` repository's `xmltag/all_xmltags.txt` [@all_xmltags] and
reproduced in the report's "Unique Tags" section.

# 4. The CDSL ecosystem in numbers (2026 snapshot)

We took a complete data snapshot of the `sanskrit-lexicon` organisation on
2026-05-07. The aggregator script `pull_data.py` calls the GitHub REST
endpoint `/repos/$ORG/$REPO/issues` for every repository's issue list, and
the GraphQL `Repository.defaultBranchRef.target.history` connection for every
repository's commit history. The raw snapshot is archived under
`data/snapshots/2026-05-07/`; the headline totals below are taken from that
archive's `summary.json` after the retry-recovery pass recorded in the file.
They should not be replaced directly with later Observable CSV row counts:
the 2026-06 `manifest.json` counts transformed rows (`repos.csv`,
`issues.csv`, `commits.csv`, and repo-login rows in `contributors.csv`), not
the same archived REST/GraphQL snapshot or the same distinct-contributor
definition used here.

## 4.1 Headline numbers

| Metric | Value |
|---|---:|
| Repositories in `sanskrit-lexicon` (including 2 forks) | 78 |
| Repositories with issues enabled | 78 |
| Issue records across the ecosystem (open + closed) | 5,172 |
| Pull requests (subset of above) | 37 |
| Issues proper (excluding pull requests) | 5,135 |
| Commits captured in default branches | 3,979 |
| Distinct contributors (commit + issue authors, post-alias-merge) | 49 |
| Repositories triaged with the 2026 taxonomy | 8 |
| Issues carrying a type label across the eight triaged repositories | 578 |
| Type-label assignments (30 issues carried two labels) | 608 |

The 78 repositories include both active dictionary repos (PWG, MWS, AP, …),
tooling repos (`csl-app`, `csl-pywork`, `csl-corrections`, …), and deprecated
experiments (`temp_corrections_*`, `Wil-YAT`). Of these, 8 have completed the
2026 taxonomy runbook at the time of writing: AP, AP90, FRI, GRA, MD, MWS,
PWG, PWK. A further 22 dictionary repositories with open issue records
(ACC, AMAR, ApteES, BEN, BHS, BOP, BOR, BUR, CAE, CCS, INM, KOW, KRM,
LRV, MCI, PUI, SHS, SKD, STC, VCP, VEI, WIL) are queued for triage in
2026–2027.

The report's abstract counts "over 5,400 issues and pull requests across 76
repositories" by 2025. Our snapshot's 5,172 records (37 of them pull
requests) is the same population measured a few weeks earlier and over a
slightly wider census: the report's figure follows the June 2026
transformation pass (5,413 records, `data/manifest.json`), which excludes
the two forks our 78-repository count retains, and the intervening weeks of
the 2026 correction campaign account for the growth.

## 4.2 Activity timeline

CDSL activity on GitHub spans the period 2014–present. The following table
aggregates commits and issue activity per calendar year.

| Year | Commits | Issues opened | Issues closed |
|---|---:|---:|---:|
| 2014 | 75 | 190 | 65 |
| 2015 | 123 | 270 | 170 |
| 2016 | 160 | 175 | 140 |
| 2017 | 85 | 268 | 130 |
| 2018 | 63 | 98 | 30 |
| 2019 | 234 | 246 | 144 |
| 2020 | 255 | 470 | 485 |
| 2021 | 610 | 637 | 484 |
| 2022 | 337 | 451 | 382 |
| 2023 | 357 | 534 | 542 |
| 2024 | 309 | 372 | 381 |
| 2025 | 612 | 1,169 | 213 |
| 2026 | 759 | 255 | 1,122 |

The commits column sums to the 3,979 captured commits of §4.1; the issue
columns count issues proper (pull requests excluded).

Two phenomena are visible. First, a sharp acceleration in 2021 (610 commits,
2.4 times the 2020 count) coincides with the report's account (in "Major
Cologne Contributors 1994-2025") of
Nagabhushana Rao's accession to the team and with the batch headword-cleaning
campaigns. Second, the 2026 row records the mass closure of 1,122 issues
against only 255 newly opened — the runbook's verification gates accept
previously stale issues into a managed state rather than leaving them open,
which mechanically advances closure rates.

## 4.3 Issue type distribution (triaged repositories)

The 578 typed issues across the eight triaged repositories carry 608
type-label assignments (30 issues held two type labels at the snapshot date;
the Phase 7 single-type gate had not yet been enforced everywhere), which
distribute as follows. Percentages are of type-label assignments; non-type
GitHub-default labels
(`invalid`, `duplicate`, `wontfix`, `help wanted`) are excluded.

| Type | Count | % |
|---|---:|---:|
| `markup` | 174 | 28.6 |
| `content-enhancement` | 113 | 18.6 |
| `link-target` | 94 | 15.5 |
| `text-correction` | 84 | 13.8 |
| `question` | 46 | 7.6 |
| `bug` | 40 | 6.6 |
| `encoding` | 33 | 5.4 |
| `scan-quality` | 15 | 2.5 |
| `link-splitting` | 9 | 1.5 |
| **total** | **608** | 100.0 |

Three observations are warranted. First, `markup` and `content-enhancement`
together account for 47.2 percent of typed work, confirming the report's
claim (in "Future Plans") that "the corpus revolution in lexicography has
not yet reached
the field of Sanskrit" — most active work in the project is structural
enrichment of historical print, not new lexicographic compilation. Second,
`link-target` work represents a substantial fraction (15.5 percent) and is
concentrated in two repositories (PWG with 72 issues, MWS with 11),
consistent with the report's account (in "Linking Dictionary and Corpus")
of the link-target era that opened once batch headword correction ended in
2022. Third, `scan-quality` and `link-splitting` are the smallest
categories, indicating that most of the imaging and citation-decomposition
work either is complete or is performed outside the issue tracker.

## 4.4 Type by repository

The following heatmap shows the distribution of types across the eight
triaged repositories (cells count type-label assignments, as in §4.3). The
PWG column totals 197 assignments, the largest of any
repository; this is consistent with the report's identification of PWG as
the canonical Sanskrit-German dictionary on which most recent Cologne work
has been concentrated.

| Type | AP | AP90 | FRI | GRA | MD | MWS | PWG | PWK | total |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `link-target` | 2 | 1 | 0 | 1 | 0 | 11 | 72 | 7 | 94 |
| `link-splitting` | 0 | 0 | 0 | 0 | 0 | 1 | 8 | 0 | 9 |
| `markup` | 15 | 9 | 2 | 7 | 2 | 51 | 32 | 56 | 174 |
| `text-correction` | 2 | 5 | 0 | 6 | 4 | 48 | 10 | 9 | 84 |
| `content-enhancement` | 2 | 5 | 5 | 13 | 5 | 26 | 35 | 22 | 113 |
| `encoding` | 2 | 4 | 1 | 3 | 1 | 10 | 11 | 1 | 33 |
| `scan-quality` | 0 | 0 | 2 | 2 | 0 | 3 | 5 | 3 | 15 |
| `bug` | 2 | 1 | 0 | 3 | 1 | 19 | 10 | 4 | 40 |
| `question` | 0 | 2 | 0 | 1 | 0 | 20 | 14 | 9 | 46 |
| **total** | 25 | 27 | 10 | 36 | 13 | 189 | 197 | 111 | 608 |

PWK and PWG together account for 308 (50.7 percent) of type-label
assignments across
the triaged set; MWS adds another 189. The Sanskrit-German dictionaries thus
dominate the active correction effort, which mirrors the report's claim
(in "Core Sanskrit-German Dictionaries") that PWG, PWK, CCS, and SCH form
the genealogical core of the
project.

## 4.5 Contributor labour

After alias merging — by which Cologne SSH dialog hostnames
(`jfunderb@dialog6.rrz.uni-koeln.de`, `dialog7`, `dialog8`), iMac hostnames
(`funderburk1@Jim-Funderburks-iMac.local`, `root@Jims-Mac-mini.local`), and
email-typo variants (`drdhaval2785#gmail.com`) are folded into their
canonical GitHub identities — the project shows 49 distinct contributors
over thirteen years. The top human contributors by captured commit count
are listed below (three bot identities — `github-actions[bot]` with 37
commits, `actions-user` with 21, and an automated updater with 3 — are
excluded from the table).

| Real name | GitHub | Role | Commits | Repos | Span |
|---|---|---|---:|---:|---|
| Jim Funderburk | `funderburkjim` | maintainer | 2,415 | 53 | 2014–2026 |
| Dhaval Patel | `drdhaval2785` | core | 1,232 | 29 | 2015–2026 |
| Mārcis Gasūns | `gasyoun` | lead | 129 | 21 | 2014–2026 |
| Anna Rybakova | `AnnaRybakovaT` | occasional | 70 | 10 | 2020–2023 |
| Nagabhushana Rao | `Andhrabharati` | core | 30 | 3 | 2021–2023 |
| (misconfigured client) | `you@example.com` | occasional | 30 | 5 | 2021 |
| DmitriSKT | `DmitriSKT` | occasional | 3 | 1 | 2017 |
| Haqob | `Haqob` | occasional | 2 | 1 | 2020 |
| Thomas Malten | `maltenth` | core | 1 | 1 | 2021 |

The picture is striking: a single contributor (Funderburk) has authored
60.7 percent of the project's captured commits over its entire GitHub
history; a second
contributor (Patel) has authored a further 31.0 percent. The remaining 47
identities share the residual 8.3 percent. This concentration of labour
is consistent with the report's observation (in "Key Contributors" and
"Future Plans") that "Almost none
of the initial team members are active now. The ship has lost its captain",
and with the report's stated need to plan for the "transition to the orphan
no-Jim mode".

We note one caveat: the very low commit count attributed to Thomas Malten
(a single 2021 commit) reflects only commits made under the GitHub login
`maltenth` on the
project's *current* GitHub branches; the foundational digitisation work
attributed to Malten in the report (in "Major Cologne Contributors
1994-2025") was deposited in pre-GitHub
formats (`MONIER.ALL`, raw `.txt`) and was imported into the repository
ecosystem by Funderburk and others. Empirical commit counts are therefore
not a measure of foundational contribution.

A further caveat applies to issue counts (omitted from the table above for
space): Funderburk authors 2,566 issues and Patel 2,019, both concentrated in
the central tracker `csl-orig` and in `COLOGNE`. These numbers reflect a
project culture in which the maintainer files the issues he then fixes, a
pattern visible in many long-lived infrastructure projects.

## 4.6 Activity span

Figure 1 (`figures/contributor-gantt.png`, generated from the archived
snapshot by `scripts/article_figures.py`; source
`data/snapshots/2026-05-07`, n = 16 commit-author identities after alias
merge, regenerated 2026-07-11) shows each
identity's first-to-last commit interval. The horizontal axis spans
2014–2026; bars are coloured by role and labelled with captured commit
counts. Three regimes are visible:

- A founding cohort active continuously since 2014 (Funderburk, Gasūns,
  Patel — though Patel's GitHub account dates from 2015).
- A 2020–2023 acceleration with multiple new contributors (Rybakova, Rao,
  others) entering and several leaving within three years.
- A late-2025/2026 acceleration with bot-driven automated commits
  (`github-actions[bot]`, `actions-user`) reflecting CI/CD adoption.

## 4.7 Dictionary corpus by entry count

We counted `<L>` markers in the canonical text file of every dictionary in
`csl-orig/v02/` (committed as `reports/coverage.md` in the observatory
repository; counts as of its 2026-06-01 refresh). The headword integrity is
excellent: in all 43 counted
dictionaries the number of `<L>` markers equals the number of `<LEND>`
markers exactly, confirming that no entry was left unclosed by the
correction pipeline. The total count is **1,495,422 entries** across 43
dictionaries.

The ten largest dictionaries account for 972,411 entries (65.0 percent
of the corpus). Their distribution is shown in Table 4.7.

| Dictionary | `<L>` count | Source bytes |
|---|---:|---:|
| MW (Monier-Williams 1899) | 286,558 | 50.1 MB |
| PW (Böhtlingk shorter, 1879–1889) | 170,556 | 31.3 MB |
| PWG (Böhtlingk–Roth 1855–1875) | 123,366 | 51.7 MB |
| AP (Apte 1957) | 90,613 | 18.4 MB |
| MW72 (Monier-Williams 1872) | 55,388 | 17.2 MB |
| LRV (Vaidya 1889) | 53,441 | 7.1 MB |
| VCP (Vacaspatyam 1873) | 50,135 | 25.1 MB |
| ACC (Aufrecht's *Catalogus Catalogorum* 1962) | 49,822 | 8.2 MB |
| SHS (Shabda-Sagara 1900) | 47,326 | 9.2 MB |
| YAT (Yates 1846) | 45,206 | 5.2 MB |

The report (abstract) counts "over 390,000" normalised entries
across the project. Our `<L>`-marker count is approximately 3.8× larger.
The discrepancy is explained by three factors. First, the alternate-headword
expansion (report, "Data Structure" section) splits a single printed entry
with multiple headword spellings (e.g. *akabara / akabbara / akavara*) into
N separate `<L>` records, each carrying a `{{Lbody=…}}` pointer to the
parent entry; these N − 1 alternate headwords are *expansions*, not new
*lemmas*. Second, the headword-normalisation work [@patel2016hwnorm]
collapses spelling variants to a single canonical form for cross-dictionary
search; the count behind the "over 390,000" figure is presumably this
normalised, deduplicated set. Third, our count includes *every* dictionary
in `csl-orig/v02/`, including English-Sanskrit and Sanskrit-French
volumes which were not in the original CDSL plan.

The relationship `<L>-markers ≈ 3.8 × normalised-lemmas` should be
empirically tested against the `hwnorm1` deduplication output as a
follow-up; see `csl-observatory` issue queue.

## 4.8 Reconciliation with the report's headline figures

The report cites several specific numerical claims that can now be
checked against the empirical snapshot.

The report's section names below abbreviate: "Analysis Tool" = "Offline
Sanskrit Analysis Tool" (under "Computer Programs"); "Digitization" =
"Digitization for Dictionaries" (under "Linking Dictionary and Corpus").

| Claim (report) | Empirical observation | Reconciliation |
|---|---|---|
| "168633 MW lemmas" (Analysis Tool) | 286,558 `<L>` markers in MW | The 168,633 figure is the lemma count *after* alternate-headword separation and deduplication; MW's `<L>` count is inflated by the alternate-headword expansion. |
| "106169 PWG lemmas" (Analysis Tool) | 123,366 `<L>` markers in PWG | Same explanation; ratio 1.16× is consistent with PWG having fewer alternate-headword expansions than MW. |
| "87091 lemmas in common" (Analysis Tool) | not yet recomputed | An empirical re-derivation is straightforward from the two `.txt` files plus `hwnorm1`; we defer it to a separate publication. |
| "67138 MBH." references in PWG (Digitization) | not yet recomputed in observatory | The report quotes the PWG source list itself; a deduplicating scan over `<ls>` in PWG would confirm. We anticipate doing so when the link-target programme stabilises. |
| "MW: 110 vs. PWG: 245" chars per entry (Analysis Tool) | derivable from source bytes ÷ entry count: MW = 175, PWG = 419 | Our character-per-entry values are larger than the report's by similar factors (1.6× and 1.7×); the report measures a different unit (likely character count of definition text, excluding tags). |
| "not more than 2800 literary sources" in PWG (Digitization) | not yet recomputed | A deduplicating scan over `<ls>` values in PWG would yield this count. |

The general pattern is that the report's figures and our empirical
counts are mutually consistent once the relevant unit is identified
(lemma vs `<L>`-record vs definition character). The discrepancies are
not errors; they are different valid measures of the same underlying
corpus. A **figure of merit for cross-dictionary work**, in our view,
should standardise on the lemma rather than the `<L>` record, because
the `<L>` count is sensitive to internal markup choices (such as the
alternate-headword expansion) that are not visible to the end
user. The observatory will report both counts going forward.

# 5. Standards alignment

## 5.1 FAIR

The CDSL ecosystem satisfies most of the FAIR data principles
[@wilkinson2016fair] by virtue of its public Git repositories and
machine-readable plain-text formats. Specifically:

- **F1** (globally unique persistent identifiers): partially satisfied by
  GitHub URLs; not satisfied by DOIs, which are absent at the time of
  writing. Phase 11 of the runbook addresses this through Zenodo–GitHub
  integration.
- **F2** (rich metadata): partially satisfied; the metadata block required
  by Phase 12 is absent in many repositories' READMEs.
- **F3** (metadata explicitly identifies data they describe): satisfied.
- **F4** (registered or indexed in a searchable resource): satisfied through
  GitHub search; not satisfied by registration in domain-specific catalogues
  such as ELEXIS.
- **A1** (retrievable by their identifier using a standardised protocol):
  satisfied (HTTPS / git).
- **I1** (machine-readable formats): partially satisfied; plain-text with
  documented tag conventions is machine-readable but not community-standard
  like TEI Lex-0 (see §5.2).
- **I2** (uses vocabularies that follow FAIR principles): not satisfied; the
  CDSL tag vocabulary is project-specific.
- **I3** (qualified references): partially satisfied; cross-dictionary links
  exist as `<ls>` and `{{Lbody=…}}` references but lack resolvable URIs.
- **R1.1** (clear and accessible data usage license): largely unsatisfied at
  the time of the snapshot: 62 of 78 repositories exposed no machine-readable
  licence at all, and only 13 carried a recognised SPDX identifier (a further
  3 were unclassifiable `NOASSERTION` bundles). A June 2026 remediation
  campaign, documented in the observatory's
  `docs/RH1_LICENSE_ROLLOUT_LOG.md` and measured in `reports/repo_health.md`,
  subsequently brought recognised SPDX licences to 70 of the 76 canonical
  repositories (code and tooling under GPL-3.0, dictionary data under
  CC BY-SA 4.0), with only six disposable `temp_*`/`test_*`/legacy
  repositories left
  unlicensed pending archival.

The principal gaps at the snapshot were F1 (no DOIs), I1/I2 (no
community-standard schema),
and R1.1 (no licence in most repositories — since remediated, see above).

## 5.2 TEI Lex-0 conversion

We demonstrate the path from CDSL's plain-text format to TEI Lex-0
[@romary2019teilex0] using a single representative entry — the same
*kuJjakuTIra* entry whose 1997 and 2025 encodings the report reproduces in
its "SLP1 Encoding" section. The entry is record `<L>51478` of the
Monier-Williams dictionary (MW; `csl-orig/v02/mw/mw.txt`, retrieved
2026-07-04 — the report's 2025-state quotation writes the compound seam as
`---`, which the source has since normalised to an em dash):

```
<L>51478<pc>288,1<k1>kuYjakuwIra<k2>kuYja—kuwIra<e>3
<s>kuYja—kuwIra</s> ¦ <lex>m.</lex> a bower, arbour, <ls>Mālatīm.</ls>; <ls>Gīt.</ls><info lex="m"/>
<LEND>
```

The corresponding TEI Lex-0 encoding is:

```xml
<entry xml:id="mw-51478">
  <form type="lemma">
    <orth xml:lang="sa-Latn-x-iast">kuñjakuṭīra</orth>
    <orth xml:lang="sa-Latn-x-slp1">kuYjakuwIra</orth>
    <gramGrp>
      <gram type="pos">m.</gram>
    </gramGrp>
  </form>
  <sense xml:id="mw-51478-1">
    <def xml:lang="en">a bower, arbour</def>
    <cit type="example">
      <bibl><title type="abbrev">Mālatīm.</title></bibl>
    </cit>
    <cit type="example">
      <bibl><title type="abbrev">Gīt.</title></bibl>
    </cit>
  </sense>
  <note type="provenance">
    <ref target="mw.txt#L51478">MW print page 288, column 1</ref>
  </note>
</entry>
```

The mapping is mechanical for entries with this regular structure: `<L>`
becomes `xml:id`; `<k1>` becomes the SLP1 `<orth>`; `<k2>` informs the IAST
`<orth>`; `<lex>` becomes `<gram type="pos">`; the gloss preceding the first
`<ls>` becomes `<def>`; each `<ls>` becomes a `<cit type="example">` with a
`<bibl>`. Compound entries, secondary headwords introduced via
`{{Lbody=…}}`, and entries with multiple senses separated by semicolons
require additional rules; a full conversion programme is sketched in §8.

## 5.3 OntoLex-Lemon RDF

The same entry rendered as OntoLex-Lemon [@cimiano2016ontolex] RDF, in
Turtle:

```turtle
@prefix ontolex: <http://www.w3.org/ns/lemon/ontolex#> .
@prefix lexinfo: <http://www.lexinfo.net/ontology/3.0/lexinfo#> .
@prefix dct:     <http://purl.org/dc/terms/> .
@prefix skos:    <http://www.w3.org/2004/02/skos/core#> .
@prefix mw:      <https://sanskrit-lexicon.uni-koeln.de/scans/MWScan/iast/> .

mw:kunjakutira-51478 a ontolex:LexicalEntry ;
    lexinfo:partOfSpeech lexinfo:noun ;
    lexinfo:gender lexinfo:masculine ;
    ontolex:canonicalForm [
        a ontolex:Form ;
        ontolex:writtenRep "kuñjakuṭīra"@sa-Latn-x-iast ,
                            "kuYjakuwIra"@sa-Latn-x-slp1
    ] ;
    ontolex:sense [
        a ontolex:LexicalSense ;
        skos:definition "a bower, arbour"@en ;
        dct:source mw:source-malatim , mw:source-git
    ] .
```

This representation supports cross-dictionary linking via SKOS, alignment to
BabelNet and Wiktionary, and SPARQL querying. It is heavier than TEI Lex-0
and is more naturally a *generated* artefact than a *source* artefact; we
recommend OntoLex-Lemon as a publication target for an RDF dump of CDSL, not
as a working format.

## 5.4 Software citation

The repositories have no `CITATION.cff` files at the time of the snapshot,
contrary to FORCE11 software citation principles [@forcecitation]. Phase 11
of the runbook (§3.4) installs `CITATION.cff` files in every triaged
repository, populated from the contributor data described in §4.5 and the
repository metadata. ORCIDs are placeholders pending registration.

# 6. The `csl-observatory` infrastructure

The data underlying every figure and table in this paper is produced by the
`csl-observatory` repository, hosted at
`github.com/sanskrit-lexicon/csl-observatory`. The repository is licensed
GPL-3.0 (code) and CC BY 4.0 (data; see the repository's
`DATA_LICENSE.md`); the article itself is licensed CC BY 4.0.

The aggregator pipeline consists of three Python scripts:

- **`pull_data.py`** fetches from the GitHub REST and GraphQL APIs and writes
  immutable snapshots to `data/snapshots/<date>/`; the archive underlying
  this paper holds weekly snapshots from 2026-05-07 through 2026-06-01.
- **`compute_metrics.py`** loads a snapshot, applies the contributor
  alias-merge rules, and derives `contributors.json`, `repo_metrics.json`,
  `timeline.json`, and `cross_repo.json`.
- **`render_reports.py`** writes Markdown dashboards (`dashboard.md`,
  `contributors.md`, `timeline.md`, `coverage.md`) with embedded Mermaid
  charts.

Figure 1 is generated by `scripts/article_figures.py` directly from the
archived 2026-05-07 snapshot.

A weekly scheduled workflow
(`.github/workflows/refresh-observatory.yml`) re-runs the pipeline on
Monday mornings (03:00 UTC) and commits any changes; the original
`refresh.yml` workflow is retained for manually dispatched runs of the
legacy report tables.

The complete data dictionary, contributor map, and reproduction instructions
are in the repository's `README.md` and `CONTRIBUTING.md`.

# 7. Limitations

Three limitations of the present analysis are explicit.

**Commit-history pagination failures.** The GraphQL endpoint returned HTTP
502 errors during commit-history pagination for several large repositories.
The archived 2026-05-07 snapshot records a retry-recovery pass for twelve
repositories, raising the captured default-branch commit count to 3,979, but
`csl-orig` remains reported with zero commits despite having a much larger
history. The commit totals in §4 are therefore conservative captured counts,
not a complete all-time commit census. A subsequent clone-based recount
(June 2026, committed as `data/commits.csv`) captured 9,877 commits,
including 1,985 for `csl-orig` alone — quantifying how conservative the
GraphQL capture is. We retain the 3,979 basis in §4 because the archived
snapshot, unlike the moving clone recount, is the frozen artifact this
paper's tables are derived from.

**Measurement dates are mixed.** The issue and commit statistics (§4.1–§4.6)
are frozen at the 2026-05-07 snapshot; the dictionary entry counts (§4.7)
follow the committed `reports/coverage.md` as of its 2026-06-01 refresh; the
worked source example (§5.2) quotes `csl-orig` as of 2026-07-04; and the
source corpus itself receives corrections continuously. Every figure in this
paper therefore names its measurement date, and small drifts between bases
(for example, the report's later June-2026 issue census, §2) are expected
rather than anomalous. The `<L>`-marker unit itself is sensitive to internal
markup choices (§4.8) and should not be read as a lemma count.

**Contributor identification incomplete.** Nine GitHub identities with
commit activity (shenyileirob, DmitriSKT, vvasuki, YevgenJohn, Haqob,
sanskritisampada, sumanthegde, adminlip, vlastavesely) have no confirmed
real name, and no human contributor has an ORCID registered in the
contributor map yet (`reports/contributor_identity.md`). A
tracking issue on `csl-observatory` (issue #20) invites them to
self-identify.

# 8. Future work

The runbook's Phases 11–16 (citation, source bibliography, data dictionary,
encoding declaration, pipeline diagram, community files) are specified but
have not yet been propagated to the eight triaged repositories. We intend to
apply them in 2026 Q3.

The 22 dictionary repositories with open issue records listed in §4.1 are
queued for triage in 2026–2027.

A TEI Lex-0 conversion programme covering the eight triaged dictionaries is
feasible on the basis of the conversion demonstrated in §5.2 and would
constitute a substantive contribution to the ELEXIS infrastructure. A
first-pass automatic conversion of MWS, the best-structured of the
dictionaries, is the natural starting point.

The report (in "Future Plans") outlines a much broader programme of future
work — five
Sanskrit-Russian dictionaries to be added, a reverse Sanskrit dictionary,
normalised cross-dictionary headwords, abbreviation markup, and the
long-deferred unification of meaning tagging. The infrastructure described
in the present companion paper is the substrate on which that programme can
be executed.

# Data and code availability

All data, scripts, and intermediate artefacts are available in the
`csl-observatory` repository:

- **Source dictionaries** (CC BY-SA 4.0): `github.com/sanskrit-lexicon/csl-orig`
- **Web display** (GPL-3.0): `github.com/sanskrit-lexicon/csl-app`
- **Observatory and analytics** (GPL-3.0; data CC BY 4.0): `github.com/sanskrit-lexicon/csl-observatory`
- **Per-dictionary correction workflows**: see the report's "Correction of Dictionaries" section

This article and its figures are licensed CC BY 4.0.

# Acknowledgements

This companion paper is built on the contributor record gathered by
Funderburk over twenty years, on the editorial decisions made by Malten,
Scharf, and Hyman in the project's first decade, and on the recent triage
work led by Patel, Rao, and Rhodes. The authors thank all 49 distinct
contributors recorded in
[reports/contributors.md](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/reports/contributors.md),
including the bots and the misconfigured git clients, for the part they have
played.

# References

::: {#refs}
:::
