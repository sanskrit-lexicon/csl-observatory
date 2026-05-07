---
title: "The Cologne Digital Sanskrit Dictionaries: a 30-year ecosystem"
subtitle: "An empirical study of distributed lexicographic labour"
author:
  - name: Mārcis Gasūns
    affiliation: Cologne Digital Sanskrit Dictionaries
    orcid: PLACEHOLDER-GASUNS
    email: gasyoun@gmail.com
  - name: Jim Funderburk
    affiliation: Cologne Digital Sanskrit Dictionaries
    orcid: PLACEHOLDER-FUNDERBURK
  - name: Dhaval Patel
    affiliation: Cologne Digital Sanskrit Dictionaries
    orcid: PLACEHOLDER-PATEL
  - name: Nagabhushana Rao
    affiliation: Andhrabharati
    orcid: PLACEHOLDER-RAO
date: 2026-05-07
abstract: |
  The Cologne Digital Sanskrit Dictionaries (CDSL) form one of the longest-running
  digital lexicographic projects in any classical language. Begun at the University
  of Cologne in 1994 and now hosted as the GitHub organisation `sanskrit-lexicon`,
  the project encompasses more than seventy repositories covering the major
  printed Sanskrit dictionaries of the eighteenth, nineteenth, and twentieth
  centuries. This article presents the first empirical, ecosystem-wide analysis
  of CDSL as a digital humanities artefact: its corpus, its workflow, its
  contributor network, and the recent introduction of a unified issue-taxonomy
  and triage runbook applied across the active dictionary repositories. Drawing
  on a complete data snapshot of <!-- DATA: total_issues --> issues,
  <!-- DATA: total_commits --> commits, and <!-- DATA: contributor_count -->
  contributors over <!-- DATA: span_years --> years, we document the
  methodological norms that have emerged organically in the project, evaluate
  them against current digital humanities standards (TEI Lex-0, OntoLex-Lemon,
  FAIR), and demonstrate one path toward linked-data lexicography through a
  proof-of-concept TEI export. We argue that the CDSL model — long-term
  community stewardship, plain-text source files, and per-issue correction
  workflows — represents a durable alternative to monolithic scholarly editions,
  and that the patterns we describe generalise to other classical-language
  lexicographic projects.
keywords:
  - Sanskrit lexicography
  - Cologne Digital Sanskrit Dictionaries
  - digital humanities
  - TEI Lex-0
  - OntoLex-Lemon
  - FAIR principles
  - distributed scholarship
bibliography: refs.bib
csl: indo-iranian-journal.csl
link-citations: true
papersize: a4
fontsize: 11pt
mainfont: "EB Garamond"
sansfont: "Inter"
mathfont: "TeX Gyre Termes Math"
geometry: margin=2.5cm
---

# 1. Introduction

The Cologne Digital Sanskrit Dictionaries (henceforth CDSL) have, since 1994,
served as the principal digital reference resource for Sanskritists working
outside India. What began as a single keyboarded transcript of Monier-Williams
in plain ASCII has grown into a continuously maintained corpus of more than
seventy repositories, hosted today at <https://github.com/sanskrit-lexicon>.
The corpus encompasses Petersburger Wörterbuch (Böhtlingk and Roth, 1855–1875),
Monier-Williams' Sanskrit-English Dictionary (1899), Apte's Sanskrit-English
Dictionary (1890; expanded 1957), Macdonell, Cappeller, Benfey, Wilson,
Grassmann's Wörterbuch zum Rig-Veda, Vacaspatyam, Shabda-Kalpadruma, and many
others, alongside the tooling, web display, and bibliographic infrastructure
that knit them together.

Despite three decades of continuous activity, no comprehensive empirical study
of CDSL exists. Existing publications [@malten1997; @kapp2009] describe
individual dictionaries or particular technical milestones but predate the
project's migration to a distributed Git-based workflow and do not address the
ecosystem as a coherent object of study. The present article aims to fill this
gap. It is the first to:

1. Survey the CDSL corpus comprehensively, with empirical counts of
   dictionaries, entries, and contributors over the project's full history.
2. Document the methodological norms — file formats, transliteration schemes,
   issue conventions, correction workflows — that have emerged organically and
   are now codified in a project-wide runbook.
3. Evaluate CDSL against contemporary digital humanities standards — TEI Lex-0
   [@romary2019teilex0], OntoLex-Lemon [@cimiano2016ontolex], FAIR data
   principles [@wilkinson2016fair], and ELEXIS infrastructure recommendations
   [@krek2018elexis] — identifying both areas of strong alignment and concrete
   gaps.
4. Demonstrate, through a one-off proof-of-concept, the path from CDSL's
   plain-text source format to TEI-conformant XML and linked-data RDF.

# 2. The Cologne Digital Sanskrit Dictionaries: a brief history

## 2.1 Origins (1994–2010)

<!-- TBD: Cologne origins, MWS first transcription, Malten's role -->

## 2.2 Migration to distributed workflows (2010–2018)

<!-- TBD: GitHub organisation founded, csl-orig as canonical store -->

## 2.3 The current ecosystem (2018–present)

<!-- TBD: 70+ repositories, contributor influx, COLOGNE issue tracker -->

# 3. The corpus

CDSL today comprises <!-- DATA: repos_count --> active repositories.
<!-- TBD: Table of dictionaries with bibliographic metadata, see refs.bib -->

## 3.1 The dictionaries

<!-- DATA: corpus table from data/repo_metrics.json -->

## 3.2 Source-text format

CDSL adopts a plain-text record format originally designed by Thomas Malten and
extended over the project's history. Each entry is delimited by `<L>...<LEND>`
markers; orthographic and structural information is encoded inline using
angle-bracket tags (`<k1>`, `<k2>`, `<e>`, `<lex>`, `<ls>`, `<ab>`) and
brace-pair markup (`{#…#}` for Sanskrit text in SLP1, `{%…%}` for italics).
The format is deliberately non-XML — it is line-oriented to enable
git-friendly diffs and per-line corrections via `updateByLine.py`-style tools.

<!-- TBD: Annotated example entry from MWS or Apte -->

## 3.3 Transliteration

The project uses three principal romanisation schemes interchangeably,
depending on context: SLP1 [@scharf2011slp1] for compact Sanskrit text within
entries; IAST [@iso15919] for headwords in display layers; and AS (Anglicised
Sanskrit) for legacy compatibility. Conversion is handled by the `transcoder`
library used across repositories.

# 4. Methodology

## 4.1 The issue taxonomy

In 2026 a unified issue taxonomy was introduced across the active dictionary
repositories. Every issue carries exactly one **type label** and one
**severity label**, and is assigned to one of four **milestones**:

| Milestone | Type labels |
|---|---|
| Dictionary to Book | `link-target`, `link-splitting` |
| Digitization Quality | `scan-quality`, `encoding`, `bug`, `text-correction` |
| Structured Data | `markup`, `question` |
| Major Enhancements | `content-enhancement` |

The taxonomy reflects a clean separation of editorial concerns: linking the
digital text to the printed source (DTB), correcting digitisation errors (DQ),
adding structural information (SD), and substantive content extension (ME).

## 4.2 The runbook

Application of the taxonomy is codified as a ten-phase runbook executed
autonomously by an LLM agent (Claude Code). Phases cover label and milestone
creation, type/severity assignment, GitHub Projects (V2) wiring, automated
verification, documentation generation (`CLAUDE.md`, `README.md`), and final
commit. The runbook ensures consistency across repositories without requiring
manual repetition of low-level GitHub API operations. Source: <!-- TBD: Zenodo
DOI for runbook v2 release -->.

## 4.3 Quality assurance

Phase 7 of the runbook performs five automated checks per repository: every
issue must have exactly one type label, exactly one severity label, exactly
one milestone, no orphan or stale labels, and milestone-type alignment. All
five must reach zero before the runbook proceeds to documentation generation.

## 4.4 Provenance and reproducibility

Every figure and table in this article is derived from a versioned data
snapshot (`csl-observatory/data/snapshots/<date>/`). Re-running
`scripts/render_reports.py --snapshot <date>` reproduces every visualisation.
This satisfies FAIR principles F1–F4, A1, I1, and R1.1 in full.

# 5. Results

## 5.1 Triage outcomes

<!-- DATA: per-repo triage table from data/repo_metrics.json -->

## 5.2 Cross-dictionary issue distribution

<!-- DATA: type×repo heatmap from data/cross_repo.json -->

## 5.3 Contributor network and labour

<!-- DATA: contributor table + Gantt of activity spans, top 20 -->

## 5.4 Temporal patterns

<!-- DATA: commits and issues by year -->

# 6. Discussion

## 6.1 FAIR alignment

CDSL satisfies most FAIR criteria already by virtue of its public Git
repositories and machine-readable formats. The principal gaps identified in
this study are:

- **F1 (globally unique persistent identifiers)**: no DOIs minted per release.
- **F3 (rich metadata)**: source bibliographic citation incomplete in many
  repositories.
- **R1.1 (clear licence)**: licence undeclared in approximately
  <!-- DATA: unlicensed_count --> active repositories.

These gaps are addressed in the runbook v2 (Section 4.2).

## 6.2 Toward TEI Lex-0

We demonstrate one TEI Lex-0 export of a representative MWS entry to show the
viable migration path:

```xml
<entry xml:id="mws-rama">
  <form type="lemma"><orth>rāma</orth></form>
  <gramGrp><pos>m.</pos></gramGrp>
  <sense>
    <def>delighting, pleasing</def>
    <cit type="example"><quote>...</quote></cit>
  </sense>
</entry>
```

The mapping from CDSL's `<L>...<LEND>` records to TEI Lex-0 `<entry>` is
mechanical for entries with regular structure. Compound entries, secondary
headwords, and embedded literary-source citations require additional tooling
which we discuss in Section 7.

## 6.3 Lessons for digital lexicography

<!-- TBD: synthesis -->

# 7. Limitations and future work

<!-- TBD -->

# 8. Conclusion

<!-- TBD -->

# Data and code availability

All data, code, and intermediate artefacts are available in the
`sanskrit-lexicon` GitHub organisation under permissive licences:

- **Source dictionaries** (CC BY-SA 4.0): <https://github.com/sanskrit-lexicon/csl-orig>
- **Web display** (GPL-3.0): <https://github.com/sanskrit-lexicon/csl-app>
- **Observatory and analytics** (GPL-3.0; data CC BY-SA 4.0): <https://github.com/sanskrit-lexicon/csl-observatory>
- **Per-dictionary correction workflows**: see Table <!-- TBD -->

This article and its figures are licensed CC BY 4.0.

# Acknowledgements

We thank the many contributors whose names appear in the contributor record
([reports/contributors.md](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/reports/contributors.md))
but who do not appear as authors of this article. Thomas Malten's foundational
digitisation effort at the University of Cologne (1994–2010) made everything
that follows possible.

# References

::: {#refs}
:::
