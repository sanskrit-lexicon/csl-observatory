# Article 1 — Methods section (DRAFT)

**Full title** (working): *Quantifying digital lexicography: a measurement framework for the Cologne Digital Sanskrit Lexicon*
**Target venue**: World Sanskrit Conference 2028 (long paper) + *Digital Scholarship in the Humanities* (Oxford)
**Authors** (draft order): M. Gasūns, J. Funderburk, D. Patel, + Claude (with appropriate disclosure)
**Status**: METHODS SECTION DRAFT — Results to be added after Phases L0, M1 complete
**Date**: 2026-05-16

---

## 3. Methodology

This section describes our four-dimensional KPI framework, the data sources, the volunteer-hour estimation methodology, and the reproducibility guarantees of the open observatory.

### 3.1 The four-dimensional KPI catalog

We organise lexicographic-project measurements into four orthogonal dimensions, each populated with a set of computable KPIs. The four dimensions and their rationale are:

**Activity** — measures *what was done and when*: issues opened, issues closed, commits authored, pull requests reviewed, releases tagged. This is the temporal pulse of the project. Activity KPIs are derivable from any git-hosted project's API metadata; they require no domain knowledge.

**Coverage** — measures *what is included in the lexicographic record*: which lemmata appear in which dictionaries, with what density, with what citation backing. Coverage KPIs require parsing of source XML and a canonical headword index (in our case, the pre-computed `sanhw1.txt` from Cologne's `hwnorm1` repository, which normalises ~470,000 headword variants into a single SLP1 namespace per Patel's (2016) conventions).

**Community** — measures *who contributed, when, and how their work is distributed*: contributor counts, retention curves, geographic distribution, bus-factor concentration, specialisation patterns. Community KPIs require the same git metadata as Activity, augmented by curated identity information (in our case, `data/people.yaml`, generated from project-wide CITATION.cff files).

**Ecosystem** — measures *what depends on or cites the lexicographic record*: web-display traffic (where available), external citations in academic literature, Wikipedia and Wiktionary backlinks, downstream tool consumption (mobile apps, JSON exports, SQLite snapshots). Ecosystem KPIs require ingest from external sources (web analytics, Semantic Scholar API, MediaWiki `exturlusage` endpoints).

Each KPI in our framework is **defined by a tuple** `(name, dimension, data source, computation method, visualisation type, frequency of refresh)`. The full catalogue contains 30+ KPIs across the four dimensions; we provide it as a downloadable CSV at `https://sanskrit-lexicon.github.io/csl-observatory/data/kpi_catalog.csv`. Section 4 (below) applies this framework to CDSL and reports headline findings.

### 3.2 Data sources

Our measurements draw on five categories of source:

1. **GitHub REST and GraphQL APIs** for the `sanskrit-lexicon` organisation (77 repositories, 12 years of history). We fetch issues (state=all), pull requests, commits since 2014, repository metadata, contributors, releases, and language statistics. Full snapshots are archived monthly in our `observatory/snapshots/YYYY-MM/` directory; snapshots are append-only and dated, so any chart can be reproduced from any historical state.

2. **The canonical CDSL master headword index** (`sanhw1.txt`, 469,844 unique normalised SLP1 lemmas across 41 dictionaries). This file is produced and maintained by the Cologne team and applies Patel's (2016) headword normalisation conventions. Use of this pre-computed index spares us the substantial effort of rebuilding lemma overlap matrices from the raw dictionary XML.

3. **Source XML of individual dictionaries** in `csl-orig/v02/<dict>/<dict>.txt`, for entry-level microstructure analysis (subentries, citations, etymology markers, grammatical tags). We process these per-dictionary using regex-based extraction calibrated against a manual annotation of a 10-entry sample.

4. **CITATION.cff files** in each dictionary's GitHub repository, providing authorship + publication-year metadata. We enriched all 34 dictionary-repo CITATION.cff files in May 2026 to include publication years, author lists, and preferred-citation blocks; the enrichment script is `observatory/enrich_citations.py`.

5. **External usage signals**: the Cologne University web analytics (Matomo, when accessible), Wikipedia and Wiktionary `exturlusage` queries across all language editions, and the Semantic Scholar API for academic citation tracking. These are deferred to a later phase (Phase F/G/M0a of the project roadmap) and reported here as future work.

All snapshots, intermediate transformations, and final chart data are version-controlled in the public `csl-observatory` repository and exported as CSV/Parquet from a stable URL namespace under `https://sanskrit-lexicon.github.io/csl-observatory/data/`.

### 3.3 Volunteer-hour estimation

We report a sensitivity range, not a point estimate, for the equivalent monetary value of CDSL volunteer labour. Our method has three steps.

**Step 1: classify each commit by effort class.** We use a heuristic combining commit-message regex, diff size, and file count to assign each commit to one of five effort classes: `trivial` (5-min, e.g. typo fixes), `small` (15-min, single-file edits under 50 lines), `medium` (60-min, multi-file edits with design decisions), `large` (180-min, substantial code or schema changes), `huge` (480-min, major refactors or new pipelines). Classification accuracy was validated against a 100-commit hand-labeled sample (Cohen's κ = TBD).

**Step 2: add issue/PR effort.** Each issue receives 5 minutes of triage time plus 45 minutes of resolution time (if closed). Each PR receives 30 minutes of review time. Comments add 5 minutes each. These per-activity time estimates derive from Beller et al. (2017) and Mockus & Herbsleb (2002).

**Step 3: apply three cost scenarios.** We multiply total estimated hours by three hourly rates:
- **Low**: €45/hour (PhD researcher in Germany, fully-loaded employer cost)
- **Mid**: €80/hour (senior software engineer market rate in Germany)
- **High**: €150/hour (Sanskrit-specialist consulting rate reflecting skill rarity)

The result is a range, e.g. "between €X million and €Y million across 12 years," rather than a single number. We argue this range *understates* the true cost because:
- It excludes unpaid time spent reading issues but not acting (typically 2-3× the acting time in OSS projects).
- It excludes offline correspondence and meetings (substantial in academic projects).
- The Sanskrit-specialist rate is conservative for the rarest skills (no Russian / Tamil / Czech-Sanskrit specialist rate is included).

We disclose all assumptions in a single table (§4.5) so reviewers can adjust the numbers.

### 3.4 Reproducibility

Every published chart is reproducible from public artifacts:

- **Source data** is in our `snapshots/YYYY-MM/` directories, append-only and dated.
- **Transformer code** is in `observatory/transform.py` and related scripts, all GPL-3.0.
- **Chart code** is in our Observable Framework site (`observatory/site/src/*.md`); the source markdown plus the CSV input produces the rendered SVG.
- **Annual data snapshots** are deposited to Zenodo with DOI minting via GitHub-Zenodo integration on release tags.
- **Code is preserved** at Software Heritage via SWH's GitHub crawler.

To reproduce any chart in this paper, the reader retrieves the named snapshot (`snapshot 2026-NN`), runs `python observatory/transform.py`, and rebuilds the site via `observable build` from the `observatory/site/` directory. We provide a Dockerfile that pins all dependencies.

A reader who wishes to extend the framework to a different lexicographic project would (1) configure the GitHub-fetch script for the target organisation, (2) adapt the headword-normalisation step to the project's conventions (or apply Patel's framework if Sanskrit), and (3) re-run the pipeline. The estimated effort to apply our framework to a comparable project (e.g. CDLI for Cuneiform, Perseus for Greek-Latin) is 2-3 weeks.

### 3.5 What this framework does NOT measure (limitations)

We are explicit about the boundaries of our methodology:

1. **Editorial quality** is not measured. We count corrections issued and resolved, but we do not assess whether the corrections improved the dictionary; that requires expert review beyond automated metrics.
2. **Linguistic accuracy** is not validated. Our lemma counts assume the published headwords are linguistically correct; errors in the source dictionary propagate to our counts.
3. **Citation appropriateness** is not assessed. We count literary-source citations but do not judge whether they support the gloss provided.
4. **Inter-dictionary derivation** is *suggested* by the framework (via lemma containment, citation truncation, convention fingerprint), but full proof requires the additional analyses described in Papers L and H of our series.
5. **Volunteer-hour estimates** are inherently uncertain (we report a range to acknowledge this) and do not capture the intellectual leadership of long-term maintainers, which exceeds what time-on-task can quantify.

These limitations are mitigated by our open-data approach: any researcher who wishes to substitute different assumptions can do so using our raw snapshots.

---

## NEXT STEPS (TO DO BEFORE THIS PAPER IS COMPLETE)

- [ ] **Phase L0 (convention-fingerprint cladogram)**: produces validation of the framework's inheritance-detection capability — required for §4.2 Results
- [ ] **Phase M1 (data-richness typology)**: produces the L0-L10 placement of each dict — required for §4.3 Results
- [ ] **Phase A (volunteer-hour computation with finer commit classification)**: produces the headline numbers for §4.4 Results
- [ ] **References section**: pull Beller, Mockus, Patel, Huet, CHAOSS, plus 30-40 DH-lexicography references
- [ ] **Abstract** (200 words, written last)
- [ ] **Introduction** (700 words)
- [ ] **Related work** (500 words)
- [ ] **Results** (3000 words)
- [ ] **Discussion** (1000 words)
- [ ] **Conclusion** (250 words)

This Methods section is ~1700 words; the target overall length is ~8500 words (15-20 pages).
