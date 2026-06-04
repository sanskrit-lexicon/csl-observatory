# Legacy Broad Metrics Roadmap

Status: legacy reference only. This file predates the 2026-06-04 boundary
cleanup and includes source mining, Matomo usage analytics, backlinks, citation
tracking, and broad paper planning that no longer belongs in active
`csl-observatory` scope. Use `OBSERVATORY_ROADMAP.md` for the current
GitHub/org-only roadmap.

---

# csl-observatory — expansion roadmap

**Version**: 1.0 · **Date**: 2026-05-15 · **Owner**: M. Gasūns + Claude Code
**Companion to**: [`OBSERVATORY_DESIGN.md`](OBSERVATORY_DESIGN.md), [`PAPER_1_OUTLINE.md`](PAPER_1_OUTLINE.md)

This doc enumerates **everything additional** that can be measured, every new visualisation, the phasing to build it, and the matching paragraph mapping for Paper 1.

Decisions baked in (per planning round 2026-05-15):
- Volunteer-hours sensitivity analysis: 3 rates (€45 / €80 / €150 per hour)
- Source mining: start with the **top 8 processed dictionaries** (PWG, PWK, MWS, MD, AP, AP90, GRA, FRI)
- Backlinks: **all Wikipedia + all Wiktionary** (no language filter)
- Paper authorship: I draft a full first pass; you rewrite for voice

---

## 1. Expanded KPI catalog (additions to §4 of design doc)

### 1.1 Activity — finer grain (5 new KPIs)

| KPI | Source | Viz | Phase | Paper §  |
|---|---|---|---|---|
| Lines added/removed per commit | `GET /repos/.../commits/{sha}` (with diff) | Histogram + per-repo total | A | 5.1.4 |
| File-level churn (top 50 most-edited files) | parsed from commit diffs | Treemap | A | 5.1.5 |
| Day-of-week × hour-of-day activity heatmap | issue/commit timestamps | GitHub-style 7×24 grid | A | 5.1.6 |
| Time-to-first-comment (median per year) | issue events | Box-plot trend | A | 5.1.7 |
| Time-to-merge (PR creation → merge) | PR events | Box-plot trend | A | 5.1.8 |

### 1.2 Coverage — content metrics (8 new KPIs, requires source mining)

| KPI | Source | Viz | Phase | Paper § |
|---|---|---|---|---|
| Headword count per dictionary | parsed `<L>` tags in source XML | Bar chart, sorted | B | 5.2.1 |
| Definition density (chars / entry) | parsed text length | Histogram per dict | B | 5.2.2 |
| Citation density (`<ls>` tags / entry) | XML scan | Bar + scatter | B | 5.2.3 |
| Cross-reference network (entry → entry) | parsed refs | Force-directed mini-graph per dict | B | 5.2.4 |
| Print-page coverage % (digitized vs total) | per-repo metadata | Stacked bar | B | 5.2.5 |
| Markup richness (XML tag depth, validation pass rate) | xmllint + tag count | Radar | B | 5.2.6 |
| Roundtrip encoding success rate (SLP1↔IAST↔Devanāgarī) | transcoder + sample | Per-dict gauge | B | 5.2.7 |
| Content growth over time (entries digitized per year) | git blame + XML parse | Cumulative line chart | B+ | 5.2.8 |

### 1.3 Community — structure (6 new KPIs)

| KPI | Source | Viz | Phase | Paper § |
|---|---|---|---|---|
| Co-authorship graph (commit-level overlap) | commits.csv pairwise | Force-directed | C | 5.3.4 |
| @-mention graph (issue/PR comment scrape) | issue comments | Force-directed | C | 5.3.5 |
| Cross-org overlap (Pandanus/DCS/Heritage/Wikipedia) | external repo fetches | Sankey | C | 5.3.6 |
| Timezone-inferred geography | commit times → continent | Choropleth | C | 5.3.7 |
| Year-of-joining cohort retention | commits | Stacked area / cohort grid | D | 5.3.8 |
| Specialization map (which dicts each contributor focuses on) | commits per (login, repo) | Heatmap matrix | D | 5.3.9 |

### 1.4 Ecosystem — usage and impact (8 new KPIs)

| KPI | Source | Viz | Phase | Paper § |
|---|---|---|---|---|
| Cologne web traffic (page views, lookups) | Matomo API | Time-series line | E | 5.4.1 |
| Geographic user distribution (Matomo) | Matomo | Choropleth | E | 5.4.2 |
| Most-looked-up dictionary entries (top 100) | Matomo | Bar chart + word cloud | E | 5.4.3 |
| Wikipedia backlinks per language edition | scraper | Bar chart | F | 5.4.4 |
| Wiktionary lexical citations per language | scraper | Bar chart | F | 5.4.5 |
| Google Scholar mentions per year | manual quarterly + `scholarly` | Time-series | G | 5.4.6 |
| Semantic Scholar citation graph | API | Network | G | 5.4.7 |
| Stargazers/forks growth | GitHub API (already partially fetched) | Stacked area | A | 5.4.8 |

### 1.5 The "epic scale without funding" headline (3 derived KPIs)

| KPI | Derivation | Viz | Phase | Paper § |
|---|---|---|---|---|
| Total volunteer-hours (sensitivity range) | ∑ (commits × time-per-commit-class) | Bar with low/mid/high range | A | 5.5.1 |
| Equivalent commercial cost (3 rate scenarios) | hours × {€45, €80, €150} | Big-number ticker + table | A | 5.5.2 |
| Print-page commercial-OCR equivalent | pages × €15-€80 per professionally-OCR'd page | Big-number with sources | B | 5.5.3 |

---

## 2. Implementation phasing

Each phase is independently shippable and produces one or more dashboard pages plus matching paper paragraphs.

### Phase A — Activity grain + epic-scale framing (1 week)
**Outputs**:
- New columns on commits.csv: `+lines`, `-lines` (requires `?per_page=100&` + per-commit fetches)
- `data/file_churn.csv` — top files per repo
- `data/activity_heatmap.csv` — 7×24 grid per repo
- `data/volunteer_hours.csv` — sensitivity table
- New dashboard pages: `/scale.md` (the headline)
- Updates to `/activity.md`

**Paper paragraphs produced**:
- §5.1.4–5.1.8 (5 paragraphs of Activity Results)
- §5.5 (the epic-scale section, ~3 paragraphs)

### Phase B — Source mining (top 8 dictionaries, 1 week)
**Outputs**:
- Clone PWG, PWK, MWS, MD, AP, AP90, GRA, FRI (~200MB total)
- `observatory/mine_source.py` — parses `<L>...</LEND>` blocks
- `data/dict_content.csv` — per-dict: headwords, defs, citations, cross-refs
- `data/dict_encoding.csv` — roundtrip pass rates
- New dashboard page: `/content.md`

**Paper paragraphs produced**:
- §5.2 (8 paragraphs of Coverage Results)
- Half of §5.5.3 (print-page equivalent)

### Phase C — Network analysis (3-5 days)
**Outputs**:
- `observatory/network.py` — builds co-authorship + mention graphs
- `data/coauthor_edges.csv`, `data/mention_edges.csv`
- `data/cross_org.csv` — overlap with Pandanus, DCS, Heritage
- New dashboard pages: `/networks.md`

**Paper paragraphs produced**:
- §5.3.4–5.3.6 (3 paragraphs of Community Results)

### Phase D — Cohort analysis (2-3 days)
**Outputs**:
- `data/cohorts.csv` — year-of-joining × subsequent-year activity
- `data/specialization.csv` — (login, repo) commit matrix
- Updates to `/community.md`

**Paper paragraphs produced**:
- §5.3.7–5.3.9 (3 paragraphs)

### Phase E — Cologne Matomo ingest (2-3 days, blocking on access)
**Outputs**:
- `observatory/fetch_matomo.py` — pulls page views, geographic, top entries
- `data/matomo_*.csv` — multiple datasets
- New dashboard page: `/usage.md`

**Paper paragraphs produced**:
- §5.4.1–5.4.3 (3 paragraphs of Ecosystem Results)

### Phase F — Wikipedia + Wiktionary backlinks (3-5 days)
**Outputs**:
- `observatory/fetch_wiki.py` — uses MediaWiki external-link API across all language editions
- `data/wiki_backlinks.csv`, `data/wiktionary_citations.csv`
- New section in `/usage.md` or `/impact.md`

**Paper paragraphs produced**:
- §5.4.4–5.4.5 (2 paragraphs)

### Phase G — Academic citation tracking (1 week)
**Outputs**:
- `observatory/fetch_scholar.py` — Semantic Scholar API + Google Scholar quarterly
- `data/citations.csv`
- New section in `/impact.md`

**Paper paragraphs produced**:
- §5.4.6–5.4.7 (2 paragraphs)

### Phase H — Paper 1 manuscript draft (continuous, finalised after F+G)
- I draft all sections per the [Paper 1 outline](PAPER_1_OUTLINE.md)
- You rewrite for voice and academic tone
- Iterate until WSC 2028 deadline

---

## 3. Volunteer-hours methodology (Phase A detail)

This is the headline number. Method must be defensible.

### Step 1: Classify commits by effort class

Heuristic (per `subject` regex + size):

| Class | Heuristic | Median time |
|---|---|---|
| trivial | merge, typo, formatting | 5 min |
| small | < 50 lines diff, single file | 15 min |
| medium | 50–500 lines diff, ≤5 files | 60 min |
| large | > 500 lines, > 5 files | 180 min |
| huge | > 5000 lines, > 20 files | 480 min |

### Step 2: Add issue/PR effort

| Activity | Median time |
|---|---|
| Issue triage (read, label) | 5 min |
| Issue authored (write, formatting) | 15 min |
| Issue resolved (investigation + close) | 45 min |
| PR review | 30 min |
| Comment | 5 min |

### Step 3: Apply 3 cost scenarios

| Scenario | Rate | Notes |
|---|---|---|
| Low: PhD researcher (Germany, fully-loaded) | €45/hr | Reflects actual labor type |
| Mid: senior software engineer (Germany, market) | €80/hr | Standard tech rate |
| High: Sanskrit-specialist consulting | €150/hr | Reflects rarity of skill |

### Step 4: Report as sensitivity table

```
                      Low (€45/hr)  Mid (€80/hr)  High (€150/hr)
Total hours: 12,500   €562,500     €1,000,000    €1,875,000
```

### Step 5: Honest disclosure

Caveats published in same paragraph:
- Time-per-commit estimates are conjectural (cite source: e.g. Beller et al. 2017)
- No accounting for unpaid issue-reading-but-not-acted-on time
- No accounting for offline correspondence
- Sensitivity range is the contribution; point estimates would be misleading

---

## 4. Source-mining plan (Phase B detail)

### Repos to mine (top 8 already-processed, alphabetised)

| Repo | Source file | Est. headwords | Print pages | Language |
|---|---|---|---|---|
| AP | `csl-orig/v02/ap/ap.txt` | ~30,000 | ~1,200 | Skt→Eng |
| AP90 | `csl-orig/v02/ap90/ap90.txt` | ~50,000 | ~1,800 | Skt→Eng |
| FRI | `csl-orig/v02/fri/fri.txt` | ~5,000 | ~300 | Skt→Lat |
| GRA | `csl-orig/v02/gra/gra.txt` | ~13,000 | ~600 | Skt→Lat |
| MD | `csl-orig/v02/md/md.txt` | ~50,000 | ~3,000 | Skt→Eng (mahābhārata) |
| MWS | `csl-orig/v02/mw/mw.txt` | ~180,000 | ~5,500 | Skt→Eng (1899) |
| PWG | `csl-orig/v02/pwg/pwg.txt` | ~115,000 | ~7,000 | Skt→Ger |
| PWK | `csl-orig/v02/pwk/pwk.txt` | ~50,000 | ~3,000 | Skt→Ger |

(Numbers are estimates; the script will replace them with measured values.)

### Parsing

```
<L>NNNN
<k1>headword
<lex>category
... body lines ...
<ls>citation 1.2.3
<ls>citation 4.5.6
<LEND>
```

Per-entry extraction:
- count `<L>` blocks → headword count
- length of body in chars → definition density
- count `<ls>` tags → citation density
- count `<k2>` (variants), `<k1>` recurrences in body → cross-references
- presence of `{#...#}` → SLP1 content count
- run transcoder roundtrip on a 1% sample → encoding pass rate

### Output schema (one row per dict)

```
repo, headwords, total_def_chars, mean_def_chars, total_citations,
mean_citations_per_entry, cross_refs, print_pages_estimated,
print_pages_actual, encoding_pass_rate_pct, snapshot_date
```

### Effort

- Cloning 8 repos: ~5 minutes (small files, depth=1 fine)
- Parsing: ~5 minutes (Python streaming)
- One-time validation against published estimates: 1 hour

---

## 5. Wikipedia + Wiktionary backlinks plan (Phase F detail)

Strategy: query MediaWiki **`exturlusage`** API across all language editions. This returns every page that links to a given external domain.

```
GET https://en.wikipedia.org/w/api.php
    ?action=query
    &list=exturlusage
    &euquery=sanskrit-lexicon.uni-koeln.de
    &eulimit=500
    &euprotocol=https
    &format=json
```

Iterate over:
- All Wikipedias: `en, de, sa, fr, ru, ja, hi, zh, pl, it, pt, es, ...` (top ~50 languages)
- All Wiktionaries: same language codes
- Domains to query:
  - `sanskrit-lexicon.uni-koeln.de`
  - `www.sanskrit-lexicon.uni-koeln.de`
  - `cologne-sanskrit-dictionaries.org` (if exists)
  - GitHub repo URLs (`github.com/sanskrit-lexicon/...`)

### Output schema

```
language, project (wp/wt), page_title, link_url, snapshot_date
```

### Aggregations
- backlinks per language (bar chart)
- backlinks per project (Wikipedia vs Wiktionary)
- top 50 cited Cologne URLs (bar chart) — what do users link to most?

### Effort
- Initial scrape: ~5 hours (rate-limited to be polite to Wikipedia)
- Subsequent runs: incremental, ~1 hour
- One-time setup: 1 day

---

## 6. Roadmap timeline (assuming 3 hours/week pace)

| Month | Phase | Dashboard page added | Paper section drafted |
|---|---|---|---|
| 2026-06 | A | `/scale.md` + activity updates | §5.1, §5.5 |
| 2026-07 | B | `/content.md` | §5.2 |
| 2026-08 | C | `/networks.md` | §5.3.4–5.3.6 |
| 2026-09 | D | `/community.md` updates | §5.3.7–5.3.9 |
| 2026-10 | E | `/usage.md` (Matomo) | §5.4.1–5.4.3 |
| 2026-11 | F | `/impact.md` (backlinks) | §5.4.4–5.4.5 |
| 2026-12 | G | `/impact.md` (Scholar) | §5.4.6–5.4.7 |
| 2027-Q1 | H first draft | benchmark study | §1, §2, §3, §4 |
| 2027-Q2 | H peer-review-ready | full polish | all sections |
| 2027-Q3 | H submit | final figures | abstract, conclusion |
| 2027-Q4 | revisions | live + frozen archive | revision rounds |
| 2028-Q1 | camera-ready | DOI mint | final |
| 2028 | WSC presentation | live demo | poster + slides |

This is conservative; faster pace possible.

---

## 7. Risks and mitigations specific to expansion

| Risk | Mitigation |
|---|---|
| GitHub rate limits when fetching per-commit diffs | Background script with 60s sleeps on 403; ETag caching |
| Source XML parsing edge-cases (BOM, encoding, ill-formed) | Per-line streaming with try/except; report parse errors as KPI |
| Wikipedia API change or block | Cache aggressively; respect robots.txt; user-agent string |
| Matomo access pending | Phase E becomes optional / delayed; rest of the paper stands |
| Volunteer-hour numbers seem too high (reviewer scepticism) | Sensitivity range + published time-per-commit references |
| Heritage/Pandanus comparison data is patchy | Honest disclosure in benchmark section; "limited public data" caveat |

---

## 8. Open questions (next planning round)

1. **Scholar API**: do you have an institutional Semantic Scholar API key, or use anonymous?
2. **Matomo URL**: which exact Cologne instance? `https://matomo.uni-koeln.de`?
3. **Cross-org partner repos** to fetch for §5.3.6: confirm list (Pandanus, DCS, Heritage, others?)
4. **Time-per-commit defaults**: are my heuristics in §3 plausible to you, or do you want to override the medians?
