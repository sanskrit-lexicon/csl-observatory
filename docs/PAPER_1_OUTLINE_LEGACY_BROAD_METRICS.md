# Legacy Broad Paper Outline

Status: legacy reference only. This file predates the 2026-06-04 boundary
cleanup and includes dictionary-content, usage-analytics, backlinks, citation,
and broad publication planning that no longer belongs in active
`csl-observatory` scope. Use `PAPER_1_OUTLINE.md` for the current
GitHub/org-only report outline.

---

# Paper 1 — *Quantifying digital lexicography: A 12-year measurement framework for the Cologne Digital Sanskrit Lexicon*

**Target venue**: World Sanskrit Conference 2028, long paper (~15-20 pages)
**Structure**: Methodology-first (per author decision 2026-05-15)
**Authorship**: Claude drafts full first pass; M. Gasūns rewrites for voice
**Companion**: [`OBSERVATORY_ROADMAP.md`](OBSERVATORY_ROADMAP.md)

This is the **paragraph-by-paragraph outline**. Every paragraph slot lists its KPI source, target word count, figure reference, and "draft trigger" (which roadmap phase produces enough data to draft it).

---

## §0 Front matter

| Slot | Words | Content | Trigger |
|---|---|---|---|
| Title | — | "Quantifying digital lexicography: A 12-year measurement framework for the CDSL" | now |
| Authors | — | M. Gasūns (lead), funderburkjim, drdhaval2785, others; ORCID per `people.yaml` | A |
| Abstract | 200 | Problem + method + headline number + reusability claim | F+G done |
| Keywords | — | digital lexicography, Sanskrit, software metrics, CHAOSS, open data, DH | now |

---

## §1 Introduction (1.5 pages, ~700 words)

| ¶ | Words | Topic | Trigger |
|---|---|---|---|
| 1.1 | 150 | Hook: 12 years, 9,176 commits, 5,280 issues, 17 contributors, **€X equivalent labour** — none of it funded | A |
| 1.2 | 150 | Problem: DH lexicography projects lack a common measurement framework; comparison is impossible; funders + reviewers can't assess sustainability | now |
| 1.3 | 150 | Existing measurement: ad-hoc reports, no shared schema, no time-series, often paywalled (TLG opacity) | now |
| 1.4 | 150 | Contribution: (a) reusable KPI catalog for DH lexicography projects (b) worked example on CDSL (c) public reproducible dashboard (d) open data API | now |
| 1.5 | 100 | Roadmap of the rest of the paper | end |

---

## §2 Related work (1 page, ~500 words)

| ¶ | Words | Topic | Trigger |
|---|---|---|---|
| 2.1 | 100 | Other DH lexicography projects: TLG, Perseus, CDLI, DDBDP, Pandanus, Sanskrit Heritage, DCS — brief positioning | now |
| 2.2 | 150 | Existing software-engineering metrics frameworks: CHAOSS, GHOST, Linux Foundation reports — what they cover, what's missing for lexicography | now |
| 2.3 | 150 | Citation studies in DH (Underwood, Eve, So) — how they measure impact; why citation alone is insufficient | now |
| 2.4 | 100 | Volunteer-labour quantification literature (Crowston, Howison, Wikipedia studies); methodology choices justified later | now |

---

## §3 The Cologne Digital Sanskrit Lexicon: brief context (1 page, ~500 words)

| ¶ | Words | Topic | Trigger |
|---|---|---|---|
| 3.1 | 150 | Origin: Cologne University, Indology dept., 1990s digitisation effort moving to git-based workflow ~2014 | now |
| 3.2 | 200 | Scope today: 35 dictionary repos covering 8 source languages, ~600,000 lemmas across all dicts; tooling stack (28 repos: API, web, transcoders, linkers) | A+B |
| 3.3 | 150 | Governance: a handful of long-term maintainers, no funding, voluntary contribution model | A |

---

## §4 Methodology (4 pages, ~2000 words)

This is the **core contribution** — the KPI taxonomy.

### §4.1 The four-dimension KPI taxonomy

| ¶ | Words | Topic | Trigger |
|---|---|---|---|
| 4.1.0 | 150 | Why four dimensions: activity, coverage, community, ecosystem. Mutual exclusivity argument | now |
| 4.1.1 | 200 | Activity dimension: 13 KPIs covering throughput, latency, distribution. **Table 1** lists them all | A |
| 4.1.2 | 200 | Coverage dimension: 8 KPIs measuring what's been digitised, with what density and quality. **Table 2** | B |
| 4.1.3 | 200 | Community dimension: 9 KPIs on contributor structure, retention, geography, network. **Table 3** | C+D |
| 4.1.4 | 200 | Ecosystem dimension: 8 KPIs on real-world usage, citations, downstream consumption. **Table 4** | E+F+G |

### §4.2 Data sources

| ¶ | Words | Topic | Trigger |
|---|---|---|---|
| 4.2.1 | 100 | Primary: GitHub REST + GraphQL API (issues, PRs, commits, metadata) | now |
| 4.2.2 | 100 | Source mining: parse XML in `csl-orig` and per-dict repos for content metrics | B |
| 4.2.3 | 100 | Usage telemetry: Matomo at Cologne site, supplemented by GitHub stars/forks | E |
| 4.2.4 | 150 | External signals: Wikipedia/Wiktionary backlinks (MediaWiki `exturlusage` API), Semantic Scholar citation graph, Google Scholar quarterly | F+G |
| 4.2.5 | 100 | Reproducibility: append-only snapshot strategy, public CSV/Parquet API, Zenodo DOI per annual release | now |

### §4.3 Volunteer-hour estimation

| ¶ | Words | Topic | Trigger |
|---|---|---|---|
| 4.3.1 | 150 | Why estimate: epistemic + political — DH funders need a number to compare; volunteer projects vanish without visible proof | A |
| 4.3.2 | 200 | Method: classify each commit and each issue/PR into effort classes; multiply by published time-per-class medians (Beller et al. 2017, Mockus & Herbsleb 2002) | A |
| 4.3.3 | 150 | Three cost scenarios: PhD researcher rate (€45/hr, fully-loaded), senior engineer market rate (€80/hr), Sanskrit-specialist consulting rate (€150/hr) | A |
| 4.3.4 | 100 | Sensitivity disclosure: report a range, not a point estimate; cite all assumptions; numbers will only strengthen with finer-grained activity data | A |

### §4.4 Reproducibility

| ¶ | Words | Topic | Trigger |
|---|---|---|---|
| 4.4.1 | 150 | Snapshot strategy: monthly cron + manual; every snapshot is dated and immutable; every chart caption cites a snapshot date | now |
| 4.4.2 | 100 | Public data API at `sanskrit-lexicon.github.io/csl-observatory/data/` — every chart's source CSV/JSON/Parquet is downloadable + citable | now |
| 4.4.3 | 100 | Code is open (GPL-3.0), data is open (CC-BY-SA-4.0), all in `csl-observatory` repo | now |

---

## §5 Results: applying the framework to CDSL (5-6 pages, ~3000 words)

This section is the **empirical heart**. One sub-section per dimension; one paragraph per KPI; each ¶ ends by pointing to its figure.

### §5.1 Activity (5 KPIs detailed, 5 figures)

| ¶ | Words | KPI | Figure | Trigger |
|---|---|---|---|---|
| 5.1.1 | 150 | Annual issues+PR throughput timeline | Fig. 1: stacked area | now |
| 5.1.2 | 150 | Commit volume per repo per year | Fig. 2: heatmap | now |
| 5.1.3 | 100 | Top-10 most active repos by lifetime activity | Fig. 3: bar chart | now |
| 5.1.4 | 200 | Code churn: lines added/removed per repo (full timeline) | Fig. 4: stream graph | A |
| 5.1.5 | 150 | File-level churn: most-edited files (treemap) | Fig. 5: treemap | A |
| 5.1.6 | 100 | Day-of-week × hour activity heatmap | Fig. 6: 7×24 grid | A |
| 5.1.7 | 150 | Time-to-first-comment (median per year, with quartiles) | Fig. 7: box-plot trend | A |
| 5.1.8 | 150 | Time-to-merge (PR cycle time over years) | Fig. 8: box-plot trend | A |

### §5.2 Coverage (8 KPIs, 6 figures)

| ¶ | Words | KPI | Figure | Trigger |
|---|---|---|---|---|
| 5.2.1 | 200 | Headword count per dictionary (top 8) | Fig. 9: bar chart | B |
| 5.2.2 | 150 | Definition density (chars per entry) | Fig. 10: per-dict histograms | B |
| 5.2.3 | 150 | Citation density (`<ls>` tags per entry) | Fig. 11: bar + scatter | B |
| 5.2.4 | 200 | Cross-reference network within dicts | Fig. 12: mini force-graphs | B |
| 5.2.5 | 150 | Print-page coverage % (digitised vs total) | Fig. 13: stacked bar | B |
| 5.2.6 | 150 | Markup richness + XML validation pass rate | Fig. 14: radar | B |
| 5.2.7 | 100 | Roundtrip encoding success rate | inline numbers | B |
| 5.2.8 | 200 | Issue typology evolution — the lead figure | **Fig. 15 (lead)**: stacked area | now |

### §5.3 Community (9 KPIs, 7 figures)

| ¶ | Words | KPI | Figure | Trigger |
|---|---|---|---|---|
| 5.3.1 | 150 | Top contributors by commits + repo-coverage | Fig. 16: side-by-side bars | now |
| 5.3.2 | 150 | New contributors per year + cumulative | Fig. 17: stacked area | now |
| 5.3.3 | 200 | Bus-factor: top-3 commit concentration per repo | Fig. 18: per-repo bar with risk colors | now |
| 5.3.4 | 200 | Co-authorship network (commit-level overlap) | Fig. 19: force-directed | C |
| 5.3.5 | 150 | @-mention graph (issue/PR threads) | Fig. 20: force-directed | C |
| 5.3.6 | 200 | Cross-org overlap (Pandanus, DCS, Heritage, Wikipedia editors) | Fig. 21: Sankey | C |
| 5.3.7 | 150 | Timezone-inferred geography | Fig. 22: world map | C |
| 5.3.8 | 200 | Year-of-joining cohort retention curves | Fig. 23: cohort grid | D |
| 5.3.9 | 150 | Specialisation matrix (login × repo focus) | Fig. 24: heatmap | D |

### §5.4 Ecosystem (8 KPIs, 6 figures)

| ¶ | Words | KPI | Figure | Trigger |
|---|---|---|---|---|
| 5.4.1 | 200 | Cologne site traffic over time (Matomo) | Fig. 25: time-series | E |
| 5.4.2 | 150 | Geographic user distribution (Matomo) | Fig. 26: choropleth | E |
| 5.4.3 | 200 | Most-looked-up entries (top 100, with word cloud) | Fig. 27: bar + cloud | E |
| 5.4.4 | 200 | Wikipedia backlinks per language edition | Fig. 28: bar | F |
| 5.4.5 | 150 | Wiktionary lexical citations per language | Fig. 29: bar | F |
| 5.4.6 | 200 | Google Scholar mentions per year | Fig. 30: time-series | G |
| 5.4.7 | 150 | Semantic Scholar citation graph | Fig. 31: network | G |
| 5.4.8 | 100 | Stargazers/forks growth | inline | A |

### §5.5 The headline: 12 years of unfunded labor in € equivalent

| ¶ | Words | KPI | Figure | Trigger |
|---|---|---|---|---|
| 5.5.1 | 250 | Volunteer-hour total with sensitivity range — present **the number** | Fig. 32: range chart | A+B |
| 5.5.2 | 250 | Equivalent commercial cost across 3 rate scenarios — **the headline table** | Table 5: 3-scenario sensitivity | A+B |
| 5.5.3 | 250 | Print-page commercial-OCR equivalent — second framing | Fig. 33: comparative bars | B |
| 5.5.4 | 250 | What this proves: not a project; an institution sustaining itself for 12 years on volunteer labor | discursive | all |

---

## §6 Discussion (2 pages, ~1000 words)

| ¶ | Words | Topic | Trigger |
|---|---|---|---|
| 6.1 | 200 | What worked: which KPIs revealed the most. The bus-factor finding. The 2025 throughput surge. The 2026 cleanup signature. | all |
| 6.2 | 200 | What didn't: limitations of automated taxonomy classification, the missing offline correspondence, the volunteer-hour estimate's irreducible uncertainty | all |
| 6.3 | 200 | Methodological lessons for other DH lexicography projects: minimum viable observatory, what to measure first, what to skip | all |
| 6.4 | 200 | Comparison with TLG / Perseus / CDLI — positioning chart from §2 revisited with our new numbers | benchmark done |
| 6.5 | 200 | Open challenges: longitudinal data quality (early years sparser), cross-org overlap measurement (depends on partner cooperation), funding sustainability paradox (the better we measure unfunded labor, the more visible the problem becomes) | all |

---

## §7 Conclusion (0.5 page, ~250 words)

| ¶ | Words | Topic | Trigger |
|---|---|---|---|
| 7.1 | 150 | Restate contribution + headline number; framework is reusable; data is open | end |
| 7.2 | 100 | Future work: Papers 2 (community), 3 (history), 4 (ecosystem) — same framework, different framings | end |

---

## §8 Data and software availability

| ¶ | Words | Topic | Trigger |
|---|---|---|---|
| 8.1 | 100 | Code: GPL-3.0 at github.com/sanskrit-lexicon/csl-observatory | now |
| 8.2 | 100 | Data: CC-BY-SA-4.0 at sanskrit-lexicon.github.io/csl-observatory/data/ | now |
| 8.3 | 100 | Reproducibility: snapshot 2026-XX-XX archived to Zenodo, DOI: ... | end |

---

## §9 Acknowledgements

| ¶ | Words | Topic | Trigger |
|---|---|---|---|
| 9.1 | 100 | Cologne University Indology dept; named contributors; communities (Sanskrit Heritage, DCS, Pandanus); Anthropic + Claude Code as research-assistant tooling (with appropriate disclosure) | end |

---

## §10 References

Bibliography in `article/refs.bib`. Categories:
- **DH lexicography projects** (TLG, Perseus, CDLI, DDBDP, Pandanus, Heritage, DCS): ~15 refs
- **Software metrics frameworks** (CHAOSS, GHOST, Linux Foundation reports): ~8 refs
- **Volunteer-labor methodology** (Beller et al. 2017, Mockus & Herbsleb 2002, Crowston, Howison): ~10 refs
- **Sanskrit digital humanities** (Hellwig, Huet, Kulkarni, others): ~12 refs
- **Citation/impact methodology** (Underwood, Eve): ~5 refs

Target: ~50 references total.

---

## Word budget

| Section | Words | Pages (350 wpg) |
|---|---|---|
| §0 | 200 | 0.5 |
| §1 | 700 | 2 |
| §2 | 500 | 1.5 |
| §3 | 500 | 1.5 |
| §4 | 2000 | 5.5 |
| §5 | 3000 | 8.5 |
| §6 | 1000 | 3 |
| §7 | 250 | 0.7 |
| §8 + §9 | 400 | 1 |
| §10 | refs | 1.5 |
| **Total** | ~8,550 | ~25 |

WSC long-paper limit is typically 15-20 pages → trim §5 sub-paragraphs as needed during revision.

---

## Drafting order (matches Roadmap phases A → G)

1. After Phase A completes: draft §1.1, §3.2-3.3, §4.3, §5.1.4–5.1.8, §5.5
2. After Phase B: draft §3.2 (final numbers), §4.1.2, §5.2 (all 8 ¶s)
3. After Phase C: draft §4.1.3 (partial), §5.3.4–5.3.6
4. After Phase D: complete §4.1.3, §5.3.7–5.3.9
5. After Phase E: §4.2.3 final, §5.4.1–5.4.3
6. After Phase F: §5.4.4–5.4.5
7. After Phase G: §4.2.4, §5.4.6–5.4.7
8. Always-on: §1, §2, §6, §7 — drafted last with full data context
