# Hypotheses, Visualizations & Standards Spec — 2026-07 (Phase-3 layer)

_Created: 07-07-2026 · Last updated: 07-07-2026_

> **What this is.** The design/spec deliverable of handoff **H269** (Fable 5, `claude-fable-5`,
> 07-07-2026). One planning document, four parts: (1) new falsifiable hypotheses over data already
> on disk, (2) buildable visualization specs for the computed-but-never-rendered ("idle") layers,
> (3) one unmined layer routed or designed end-to-end, (4) the interoperability/standards spine
> (persistent IDs, DOIs + datasheets, MWSA framing, OntoLex/TEI Lex-0 routing, citation-graph
> extension). **No dashboard pages, chart code, pipeline runs, or `data/` mutations ship with this
> spec** — each part ends in an acceptance checklist a future build session executes without the
> authoring session.
>
> **Boundary compliance.** Everything here respects
> [`docs/BOUNDARY_RULES.md`](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/docs/BOUNDARY_RULES.md):
> the primary object of every in-repo item is the GitHub org, its repos, contributors, workflows,
> or the OBS-T correction corpus (an in-repo language resource). Every dictionary-*content* item is
> expressed as a **cross-repo routing contract** (→ [`csl-atlas`](https://github.com/sanskrit-lexicon/csl-atlas)),
> and every RDF/TEI item as a routing contract (→ [`csl-standards`](https://github.com/sanskrit-lexicon/csl-standards)) —
> never as an in-observatory build.

---

## 0. Ground truth this spec is built on (verified 07-07-2026)

Two corrections to received assumptions, so build sessions don't chase ghosts:

1. **Data layering.** The org/GitHub-metrics layer lives in
   [`data/`](https://github.com/sanskrit-lexicon/csl-observatory/tree/main/data)
   (`contributor_specialisation.csv`, `contributor_repo_heatmap.csv`, `snapshots/`,
   `etymology_marker_preliminary.csv`, `wil_nirukta_tokens.csv`, …). The **OBS-T
   correction-event layer lives in
   [`observatory/site/src/data/`](https://github.com/sanskrit-lexicon/csl-observatory/tree/main/observatory/site/src/data)**
   (`correction_events_final.csv` + all `obs_t_*` derivatives). There are **no**
   `data/obs_t_*.csv` files — any doc citing that path is stale.
2. **There is no `palette.css` today.** The site theme is Observable Framework's built-in
   `theme: ["air", "alt", "wide"]` in
   [`observatory/site/observablehq.config.js`](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/observatory/site/observablehq.config.js),
   plus a single `#3a5f7d` theme-color meta. Part 2 therefore **introduces** the token file
   `observatory/site/src/palette.css` as its first build step; it does not edit an existing one.

Existing rigor idiom (to be reused verbatim in Part 1): the OBS-T report
[`reports/obs_t_rigor.md`](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/reports/obs_t_rigor.md)
states hypotheses H1–H3 with Wilson 95% CIs for proportions, χ² + **Cramér's V with a
commit-block bootstrap 95% CI** for contingency structure (row p-values deliberately not treated
as inferential, because events cluster by commit/campaign), and **Mann-Kendall τ with
Benjamini-Hochberg q-values** for temporal trends. New hypotheses below continue the numbering
(H4–H9) and reuse exactly these instruments.

---

## Part 1 — New falsifiable hypotheses (H4–H9)

Rules applied to every hypothesis: an explicit null, a named test statistic, a named
multiple-comparison / clustering correction, and the **exact data file** read. Where human-labeled
data is the ground truth, the hypothesis is **gated on the gold/κ harness**
([`scripts/obs_t_gold.py`](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/scripts/obs_t_gold.py))
— see the κ gate note after H6. Shares are over *corrected events* (curatorial attention), not raw
error rates — the standing OBS-T caveat carries over.

### H4 — Correction labor is specialised beyond repo size

- **Claim.** Contributors concentrate commits on specific repos/families more than a
  size-proportional allocation would produce.
- **Null.** The contributor × repo commit matrix is consistent with independence: each
  contributor distributes commits across repos in proportion to the repos' total commit mass.
- **Test statistic.** χ² on the login × `family` contingency table; effect size **Cramér's V**;
  robustness via a contributor-level permutation test (shuffle repo assignments within total
  commit counts, 10,000 permutations) — the repo-idiom substitute for inferential p-values, since
  commits cluster by campaign. Secondary descriptive: distribution of `normalized_entropy`
  (already computed per login) with a bootstrap 95% CI on its median.
- **Correction.** Single planned test — no family-wise correction needed; permutation p reported.
- **Data.** [`data/contributor_repo_heatmap.csv`](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/data/contributor_repo_heatmap.csv)
  (`login,repo,family,commits`, 202 rows) and
  [`data/contributor_specialisation.csv`](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/data/contributor_specialisation.csv)
  (`login,…,shannon_entropy,max_entropy,normalized_entropy,top_repo,…,dominant_family_share`, 17 logins).
- **Status.** Fully answerable from disk today.

### H5 — Edit-type profiles are corrector-invariant

- **Claim.** The distribution over the EDIT-TYPE axis (`spelling | diacritic | case | spacing |
  punctuation | digit | transposition | source-raw`) is the same for every major corrector — i.e.
  the typology reflects the *material*, not the *person*.
- **Null.** `edit_type` ⫫ `corrector` (independence) among the top-k correctors (k = correctors
  with ≥ 500 events; per
  [`observatory/site/src/data/obs_t_corrector.csv`](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/observatory/site/src/data/obs_t_corrector.csv)
  that is a handful of logins out of 60, led by `funderburkjim` at 35,057 events).
- **Test statistic.** χ² on corrector × edit_type; **Cramér's V with commit-block bootstrap 95%
  CI** (exactly the H2 idiom — resample commits, not events, because a single campaign commit can
  contribute thousands of same-type events).
- **Correction.** If per-cell standardized residuals are inspected, BH across cells; the headline
  is the single V + CI.
- **Data.** [`observatory/site/src/data/correction_events_final.csv`](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/observatory/site/src/data/correction_events_final.csv)
  (fields `edit_type`, `corrector`, `commit_sha` per
  [`data/schema/correction-event.schema.json`](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/data/schema/correction-event.schema.json)).
- **Status.** Answerable from disk. `edit_type` is derived mechanically from edit-ops (not a human
  judgment), so no κ gate; restrict to rows where `edit_type != 'none'`.

### H6 — Correction labor is Pareto-concentrated within every error component

- **Claim.** For each LOCATION component (`headword`, `sense`, `citation`, `markup`, …), the top-2
  correctors account for ≥ 80% of events — concentration is a property of every component, not
  just the corpus aggregate.
- **Null.** For at least one component, the top-2 corrector share is < 0.80.
- **Test statistic.** Per-component top-2 share with a commit-block bootstrap 95% CI (Wilson CIs
  are inappropriate here because the share is of a ranked pair, not a fixed category); plus a
  per-component Gini coefficient as the descriptive companion.
- **Correction.** BH across the 8 components for the per-component CI exclusion tests.
- **Data.** `correction_events_final.csv` (`error_component` × `corrector`), aggregate check
  against `obs_t_corrector.csv` (`corrector,name,events,top_component,first,last`).
- **Status.** Answerable from disk, **but κ-gated**: `error_component` labels are 64.3%
  `derived` / rest `inferred`, and the gold pass showed derived-vs-inferred accuracy 0.486 vs
  0.061 under the *old* taxonomy. Run on `evidence_level == "derived"` rows only until the κ gate
  (below) clears; report both strata.

> **The κ gate (MWSA-style evaluation discipline).** Every hypothesis whose answer depends on a
> human-adjudicated label (`error_component` today; any future sense/alignment label) must specify:
> a **frozen gold sample** (the existing stratified SEED-42 sheet
> [`validation/gold_sample.csv`](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/validation/gold_sample.csv),
> 390 annotated rows), **Cohen's κ** between two annotators, and **per-class P/R/F1** — all
> produced by `scripts/obs_t_gold.py --score` into
> [`validation/gold_metrics.json`](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/validation/gold_metrics.json).
> Current state: `gold_component_2` is filled for only 4 rows (κ not yet meaningful), and the
> stored accuracy (0.29) predates the two-axis reframe. **Unblock action (not done here): a second
> annotator fills `gold_component_2`, then re-score under the current taxonomy.** This is a
> standing gate, already tracked; the spec names it, it does not chase it.

### H7 — Org backlog shape is stationary week-over-week (monitor-grade)

- **Claim.** Weekly org-level aggregates (open issues, open PRs, total commits) show no trend
  across snapshots — the backlog is in steady state.
- **Null.** No monotonic trend: Mann-Kendall τ = 0 per series.
- **Test statistic.** **Mann-Kendall τ** per series with exact small-n p-values; **BH q-values**
  across the three series (the H3 idiom).
- **Correction.** BH across series. **Power caveat stated up front:** only 5 weekly snapshots
  exist (`2026-05-07 … 2026-06-01`), so MK is underpowered (min two-sided p at n=5 is ≈ 0.028 and
  only for a perfectly monotonic series). The hypothesis is registered now, with the verdict
  deferred until ≥ 10 snapshots have accumulated via the weekly refresh; until then the dashboard
  view (Part 2, V3) renders the series descriptively.
- **Data.** `data/snapshots/<date>/summary.json` (keys `total_issues`, `total_pull_requests`,
  `total_commits`, `repos_count`) across
  [`data/snapshots/`](https://github.com/sanskrit-lexicon/csl-observatory/tree/main/data/snapshots).
- **Status.** Registered now; decidable after ~5 more weekly snapshots. API-gated only in the
  sense that snapshots keep accruing via the existing refresh workflow.

### H8 — Character confusions are asymmetric (case/diacritic errors have a dominant direction)

- **Claim.** High-frequency confusion pairs are directional — e.g. `P→p` (2,945 events) is not
  matched by a comparable `p→P` flow — because the error source (OCR, case-folding, encoding) has
  a preferred direction.
- **Null.** For each unordered pair {a, b}, the direction is symmetric: counts(a→b) ~
  Binomial(n = counts(a→b) + counts(b→a), p = 0.5).
- **Test statistic.** Exact two-sided binomial test per pair, for all pairs with total ≥ 30
  events; effect size reported as the directional share with a Wilson 95% CI.
- **Correction.** **BH across all tested pairs** (the pair list is data-driven, so this is a
  genuine multiple-comparison setting).
- **Data.** [`observatory/site/src/data/obs_t_confusion.csv`](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/observatory/site/src/data/obs_t_confusion.csv)
  (`from,to,unit,layer,edit_space,count`, 5,019 rows), stratified by `edit_space` (`iast` vs raw
  spaces analysed separately — mixing them conflates encoding regimes).
- **Status.** Fully answerable from disk today. No κ gate (`from`/`to` are mechanical).

### H9 — Etymology-style drift across dictionaries (CONTENT — routed, not run here)

- **Claim (for the record).** Dictionary etymological practice shifts from Nirukta-style native
  affix notation (WIL 1832: 88.9% `nirukta_E_pct`) to Western comparative `cf.` style (MW72 1872:
  9,296 `cf_count`) over the 19th century.
- **Why it does not run in observatory.** Its primary object is *dictionary microstructure*
  (etymology sections), which
  [`docs/BOUNDARY_RULES.md`](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/docs/BOUNDARY_RULES.md)
  routes to **csl-atlas**. The two probe CSVs were computed here as exploratory spikes and are
  the "unmined layer" of Part 3, where the full routing contract is written. Any test design
  (e.g. χ² over dict × etym_style, MK over `year`) belongs in csl-atlas's rigor docs, citing these
  files as a *witness feed*.
- **Data (feed only).** [`data/etymology_marker_preliminary.csv`](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/data/etymology_marker_preliminary.csv),
  [`data/wil_nirukta_tokens.csv`](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/data/wil_nirukta_tokens.csv).

### Part 1 acceptance checklist (for the build session)

- [ ] H4, H5, H8 executed as a new script `scripts/obs_hypotheses_phase3.py` (stdlib +
      existing bootstrap helpers; UTF-8 reconfigure per org Windows rule), emitting
      `reports/obs_phase3_rigor.md` in the exact H1–H3 table idiom.
- [ ] H6 executed on `evidence_level == "derived"` stratum; both strata reported; result flagged
      "κ-gated" until `gold_metrics.json` shows a meaningful two-annotator κ under the current
      taxonomy.
- [ ] H7 registered in the report with its power caveat; verdict deferred until ≥ 10 snapshots.
- [ ] H9 NOT executed here; Part 3 contract committed instead.
- [ ] Every reported statistic names its correction (bootstrap / permutation / BH) inline.

---

## Part 2 — Visualizations for the idle layers

**Design constraints (from the live smoke gate).**
[`scripts/site_visualization_smoke.py`](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/scripts/site_visualization_smoke.py)
requires each registered page to contain **≥ 5 `Plot.plot(` calls**, registration in the
module-level `PAGES` list, and a `path: "/<page>"` entry in
[`observatory/site/observablehq.config.js`](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/observatory/site/observablehq.config.js).
The four required visualizations therefore ship as **two new pages** (each a coherent story with
≥ 5 marks), not four thin pages that would each fail the gate.

**Palette (build step 0).** Create `observatory/site/src/palette.css`, imported by both new pages
(and progressively adopted by existing ones): CSS custom properties layered over the Framework
`air`/`alt` themes — `--obs-seq-*` (sequential ramp for heatmap fills), `--obs-accent`
(`#3a5f7d`, the existing theme-color), `--obs-good`/`--obs-warn`/`--obs-bad`, each with a
`@media (prefers-color-scheme: dark)` override block. Charts reference tokens via
`getComputedStyle`/Plot `scheme` config rather than hard-coded hexes.

### Page A — `observatory/site/src/correction-anatomy.md` (route `/correction-anatomy`)

The OBS-T corpus's "who fixes what, and how letters break" page. Data: all via
`FileAttachment` from the co-located `observatory/site/src/data/` files — no loader needed.

| # | Chart | Data file | Mark & encoding | The one finding it makes legible |
|---|---|---|---|---|
| V1 | **Confusion-matrix heatmap** | `obs_t_confusion.csv` | `Plot.cell`: x = `from`, y = `to`, fill = log₁₀(`count`) on the `--obs-seq-*` ramp; faceted or toggled by `edit_space` (`iast` default); top-40 characters by marginal count, rest binned to "·other" | Case-folding (`P→p`, 2,945) and punctuation swaps dominate the character-level error space — corrections are typographic, not lexical (H1's micro-edit finding, now visible) |
| V2 | **Confusion asymmetry** (H8 companion) | `obs_t_confusion.csv` | `Plot.dot` / arrow: for each pair with total ≥ 30, x = total volume (log), y = directional share a→b with Wilson CI whiskers; color `--obs-accent`, BH-significant pairs emphasized | Confusions have a dominant direction — the error source is systematic (OCR/case-folding), not noise |
| V3 | **Corrector Pareto curve** | `obs_t_corrector.csv` | `Plot.line` cumulative share of `events` over correctors ranked desc. + `Plot.ruleY([0.8])`; companion `Plot.barX` top-10 correctors | 2 of 60 correctors (`funderburkjim` 35,057 + `drdhaval2785` 8,248) carry ~83% of 52k events — the bus-factor finding restated at event level |
| V4 | **Corrector × component matrix** (H5/H6 companion) | `obs_t_corrector.csv` + a small pre-aggregated `obs_t_corrector_component.csv` (build step adds it to the OBS-T aggregation script) | `Plot.cell`: x = `error_component`, y = top-8 correctors, fill = row-normalized share | Whether specialists exist *within* the corpus (Dhaval on markup vs Jim on sense) or everyone fixes everything |
| V5 | **Corrector tenure spans** | `obs_t_corrector.csv` (`first`, `last`) | `Plot.barX` ranged: x1 = `first`, x2 = `last`, y = corrector (top-20 by events), stroke width ∝ log events | Correction labor is long-tenure, few-hands — 2014–2026 spans for the core pair vs drive-by correctors |

### Page B — `observatory/site/src/org-shape.md` (route `/org-shape`)

The org/GitHub-metrics idle layer. Data: `contributor_*.csv` and a **new data loader**
`observatory/site/src/data/snapshot_drift.csv.py` (Observable Framework Python loader) that reads
`data/snapshots/*/summary.json` at build time and emits a tidy
`snapshot_date,metric,value` table — snapshots stay canonical in `data/`, the site consumes a
derived view (no `data/` mutation).

| # | Chart | Data file | Mark & encoding | The one finding it makes legible |
|---|---|---|---|---|
| V6 | **Contributor-specialisation heatmap** | `data/contributor_repo_heatmap.csv` (via loader copy) | `Plot.cell`: x = repo (grouped by `family`), y = `login` (17), fill = log(`commits`), `--obs-seq-*` | Who works where: the org's labor map, computed 2026-06 and never rendered |
| V7 | **Specialisation index dot plot** (H4 companion) | `data/contributor_specialisation.csv` | `Plot.dot`: x = `normalized_entropy` (0 = specialist, 1 = generalist), y = `login` sorted, size = `total_commits`, color = `dominant_family` | Whether the org runs on generalists (Jim: 0.69 over 58 repos) or specialists — H4's verdict as a picture |
| V8 | **Dominant-family share bars** | `data/contributor_specialisation.csv` | `Plot.barX`: x = `dominant_family_share`, y = `login`, fill = `dominant_family`, `Plot.ruleX([0.5])` | How captured each contributor is by one repo family |
| V9 | **Snapshot drift small-multiples** (H7 companion) | new `snapshot_drift.csv` loader | `Plot.line` + `Plot.dot`, faceted by metric (`total_issues`, `total_pull_requests`, `total_commits`, `repos_count`), x = `snapshot_date` | Week-over-week org trajectory; today only a text digest (`reports/monitor_digest.md`) exists |
| V10 | **Backlog composition slope** | same loader | `Plot.line` slope view: issues vs PRs share per snapshot | Whether the backlog is aging in place or churning |

### Part 2 acceptance checklist (for the build session)

- [ ] `observatory/site/src/palette.css` created (light + dark token blocks); both new pages
      import it.
- [ ] `correction-anatomy.md` and `org-shape.md` ship with ≥ 5 `Plot.plot(` calls each
      (V1–V5, V6–V10 above).
- [ ] `path: "/correction-anatomy"` and `path: "/org-shape"` added to `observablehq.config.js`
      nav.
- [ ] Both page names appended to `PAGES` in `scripts/site_visualization_smoke.py`; smoke passes
      (per-page ≥ 5, aggregate ≥ 25, nav check).
- [ ] The `snapshot_drift.csv.py` loader reads `data/snapshots/` read-only; V4's
      `obs_t_corrector_component.csv` is emitted by the existing OBS-T aggregation script, not a
      new pipeline.
- [ ] No hard-coded hex colors in the new pages except via `palette.css` tokens.

---

## Part 3 — The unmined layer: etymology/nirukta probes → csl-atlas routing contract

**Chosen layer:** [`data/etymology_marker_preliminary.csv`](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/data/etymology_marker_preliminary.csv)
together with its companion token inventory
[`data/wil_nirukta_tokens.csv`](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/data/wil_nirukta_tokens.csv).

**Honest conclusion: route out, do not build here.** These two files measure *dictionary
microstructure* (etymology-section style: Nirukta affix notation vs Western `cf.` comparativism).
Under [`docs/BOUNDARY_RULES.md`](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/docs/BOUNDARY_RULES.md)
that is csl-atlas's object, full stop. Building an observatory dashboard section over them would
re-open exactly the scope the 2026-06-03 boundary decision closed (and PR #14 cleaned up). The
deliverable is therefore an explicit **witness-feed contract**:

| Contract field | Value |
|---|---|
| Source files (frozen witnesses) | `data/etymology_marker_preliminary.csv` (schema `dict,year,entries,nirukta_E_pct,cf_count,caus,pass,desid,freq,bopp,etym_style`; 5 dictionaries) · `data/wil_nirukta_tokens.csv` (schema `token,count,meaning`; 16 WIL affix tokens, e.g. `aff.` 14,665) |
| Producing repo | `csl-observatory` (exploratory spike; **frozen** — observatory will not extend these files) |
| Consuming repo | [`csl-atlas`](https://github.com/sanskrit-lexicon/csl-atlas) — dictionary-structure / genealogy research home |
| Transfer form | csl-atlas vendors a copy under its own `data/` with a provenance header naming the source commit; or re-derives with its own extractor using these files as the acceptance fixture. csl-atlas's choice. |
| Research design that moves with it | H9 (Part 1): etymology-style drift 1832→1900; candidate tests χ² dict × `etym_style`, MK over `year`; per-dict marker P/R against a hand-checked entry sample (κ-gated in atlas, not here) |
| What observatory keeps | Nothing rendered. A one-line pointer in [`docs/DICTIONARY_STRUCTURE_MOVED.md`](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/docs/DICTIONARY_STRUCTURE_MOVED.md) recording the handover. |

**Runner-up (recorded, not chosen):** a "correction-corpus dossier" page unifying the scattered
OBS-T signals (summary, rigor, robustness, silver, baselines JSONs) into one page. In-boundary and
legitimate, but Part 2's two pages already render the highest-value OBS-T layers; the dossier is a
consolidation, not a new surface. Queue it behind Part 2 if appetite remains.

### Part 3 acceptance checklist

- [ ] Contract row above appended to `docs/DICTIONARY_STRUCTURE_MOVED.md` (observatory side) and
      mirrored into csl-atlas's intake doc (or an issue on csl-atlas) with the source blob URLs +
      commit SHA.
- [ ] `Uprava/PROJECT_INTERLINKS.md` gains the feed edge: observatory `etymology_marker` CSVs →
      csl-atlas.
- [ ] Both CSVs marked frozen (comment in the producing script or a README note) — no further
      observatory-side extension.

---

## Part 4 — Interoperability / standards spine (the ACL-Anthology lessons, as artifacts)

Each lesson lands as a named artifact with a path. None of them is prose aspiration.

### 4.1 Persistent IDs — `data/schema/correction-event.schema.json` extension

The schema already requires `event_id` but does not constrain its form, and re-runs of the
extraction pipeline are not guaranteed to reproduce it. Specify:

- **Event ID scheme:** `obst:v1:<source_layer>:<dict>:<h12>` where `<h12>` = first 12 hex chars of
  SHA-256 over the canonical tuple `(source_layer, dict, source_path, commit_sha, date, old_iast,
  new_iast)` — every field already required or present in the schema, so the ID is **derivable and
  invariant across re-runs** (same evidence ⇒ same ID; the `v1` segment versions the recipe).
- **Schema change:** add `"pattern": "^obst:v1:(form|git|printchange|batch):[a-z0-9]+:[0-9a-f]{12}$"`
  to `event_id` in
  [`data/schema/correction-event.schema.json`](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/data/schema/correction-event.schema.json),
  plus a `$comment` documenting the hash recipe.
- **Dataset-level IDs:** every derived release is identified as
  `csl-obs/<dataset>@<semver>` (e.g. `csl-obs/correction-events@1.0.0`), recorded in
  [`data/manifest.json`](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/data/manifest.json)
  and in the kosha data-hub manifest row when released.
- **Migration:** one-off script maps current `event_id`s to the new scheme with an old→new
  crosswalk CSV committed alongside (IDs already cited in reports must stay resolvable).

### 4.2 DOIs + datasheets — template + the deferred Zenodo dependency

- **Artifact:** `docs/DATASHEET_TEMPLATE.md` — generalized from the existing, already
  Gebru-style [`docs/DATASHEET.md`](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/docs/DATASHEET.md)
  (OBS-T corpus: 52,498 events, 43 dictionaries, CC-BY-4.0). Mandatory sections: motivation;
  composition; source edition + page range (where applicable); **encoding (SLP1/IAST/deva) and
  transliteration regime**; collection process; known gaps & label-quality state (κ, P/R/F1,
  evidence-level split); license; intended use; maintenance. **Rule: no derived dataset release
  (`/data-release`) without a filled datasheet.**
- **DOI dependency (recorded, not chased):** the OBS-T DOI `10.5281/zenodo.15834721` currently
  resolves to an unrelated preprint; the fix sweep is armed
  ([`scripts/fix_obs_t_doi.py`](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/scripts/fix_obs_t_doi.py),
  verify-first, refuses to write until the new record's title/creator match OBS-T). **Deferred
  until 17-07-2026 per standing decision — no Zenodo action before that date.** The persistent-ID
  scheme (4.1) is deliberately DOI-independent so it can ship first.

### 4.3 MWSA framing — evaluation discipline, adopted not invented

- **Statement (normative):** OBS-T label validation, its confusion/alignment analysis, and any
  future cross-dictionary sense/headword mapping are instances of the ELEXIS/GlobaLex
  **Monolingual Word Sense Alignment** shared-task family. Observatory adopts the MWSA evaluation
  contract — **frozen gold sample, two annotators, Cohen's κ, per-class P/R/F1** — rather than a
  bespoke method. The harness already exists (`scripts/obs_t_gold.py` implements stratified
  sampling, blind sheets, κ, P/R/F1); what the framing adds is (a) naming the lineage in the paper
  and datasheet, and (b) adopting the MWSA data-format conventions if a cross-dict sense-alignment
  dataset is ever emitted — at which point the *alignment content itself* routes to csl-atlas, with
  observatory keeping only the process metrics.
- **Artifact:** a "Evaluation lineage" subsection in `docs/DATASHEET.md` + the paper draft, citing
  the MWSA benchmark (links in §4.6).

### 4.4 OntoLex-Lemon + TEI Lex-0 — routing contract to csl-standards

**Not built here.** RDF/TEI implementation is csl-standards' object per the boundary rules. The
artifact is the **field-mapping contract** the standards repo consumes:

| Observatory field (correction-event schema) | OntoLex-Lemon target | TEI Lex-0 target |
|---|---|---|
| `headword_iast` (+ `dict`, `lcode`) | `ontolex:LexicalEntry` / `ontolex:canonicalForm` → `ontolex:Form` with `ontolex:writtenRep@sa-Latn` | `<entry>` / `<form type="lemma">` / `<orth>` |
| `old_iast` → `new_iast` correction pair | `ontolex:Form` variant statements; the correction event itself as a `prov:Activity` revising the Form (FrAC/prov-o pattern — csl-standards' call) | `<orth>` with `@corresp` + revision noted in `<revisionDesc>`/`@change` |
| `error_component = sense` events | anchor to `ontolex:LexicalSense` of the affected entry | `<sense>` |
| `dict` | `lime:Lexicon` per dictionary | one TEI document per dictionary, `<titleStmt>` |
| `event_id` (4.1) | minted as a resolvable IRI `https://…/obst/v1/<id>` — namespace choice is csl-standards' | `@xml:id` |
| `corrector` / `date` | `prov:wasAssociatedWith` / `prov:endedAtTime` | `<change who="#…" when="…">` |

- **Artifact:** this table shipped as `docs/ONTOLEX_TEI_ROUTING_CONTRACT.md` (or folded into
  csl-standards' intake doc — csl-standards' choice), plus an issue on
  [`csl-standards`](https://github.com/sanskrit-lexicon/csl-standards) handing it across the
  boundary. Observatory commits to keeping the schema fields named above stable (4.1's versioned
  IDs make that enforceable).

### 4.5 Citation-graph mining — the org surface only

Observatory owns the **org** citation/reference surface; the dictionary `<ls>` citation graph
(source-text citations inside entries) is csl-atlas's and is not duplicated here.

- **Existing base:** the `/network` page (Workstream G4, D3 force map + adjacency matrix over
  contributor↔repo) and the external-reach layer (`scripts/external_reach.py` → `/reach`).
- **Specified extension (AAN/ACL-ARC-style, as a publishable DH artifact):** a
  **cross-repo reference graph** — nodes = repos + issues/PRs; edges = cross-repo issue/PR
  references (`org/repo#N` mentions in issue bodies and commit messages, already present in
  `data/issues.json` / `data/commits.json`) — released as a node/edge CSV pair
  (`data/org_reference_graph_nodes.csv`, `data/org_reference_graph_edges.csv`) with its own
  datasheet (4.2), dataset ID (4.1), and a `/network` page section rendering in/out-degree and the
  bridge repos. This is the AAN move: turn the community's own referential behavior into a citable
  network resource.
- **Boundary note (explicit):** if the edge extractor ever encounters dictionary-content citations
  (`<ls>` abbreviations, source-text refs), they are out of scope here — csl-atlas territory.

### 4.6 Sources (all four lessons)

- ELEXIS MWSA shared task: <https://elex.is/mwsa2020/> · data/format:
  <https://github.com/elexis-eu/MWSA>
- OntoLex-Lemon lexicography (lexicog) module: <https://www.w3.org/2019/09/lexicog/> · core
  OntoLex-Lemon: <https://www.w3.org/2016/05/ontolex/>
- TEI Lex-0: <https://dariah-eric.github.io/lexicalresources/pages/TEILex0/TEILex0.html>
- Gebru et al., *Datasheets for Datasets* (2018/2021): <https://arxiv.org/abs/1803.09010>
- ACL ARC / AAN citation networks: <https://aclanthology.org/L08-1005/> (ACL ARC) ·
  <https://aclanthology.org/J13-3006/> (AAN)
- ACL Anthology metadata corpus: <https://github.com/acl-org/acl-anthology>

### Part 4 acceptance checklist

- [ ] `event_id` pattern + `$comment` recipe added to `data/schema/correction-event.schema.json`;
      old→new ID crosswalk committed; `data/manifest.json` rows carry `csl-obs/<dataset>@<semver>`
      IDs.
- [ ] `docs/DATASHEET_TEMPLATE.md` created; `/data-release` discipline references it; Zenodo DOI
      fix executed **only after 17-07-2026** via `scripts/fix_obs_t_doi.py --record … --apply`.
- [ ] MWSA lineage subsection added to `docs/DATASHEET.md` + paper draft, with citations.
- [ ] `docs/ONTOLEX_TEI_ROUTING_CONTRACT.md` committed and handed to csl-standards via issue;
      no RDF/TEI code in this repo.
- [ ] Org reference-graph node/edge CSVs specified in `data/manifest.json`; extractor reads only
      GitHub-evidence files; `<ls>`-shaped content explicitly skipped.

---

## Build order (recommendation for the next sessions)

1. **Part 2 first** (cheapest wins, all data on disk): `palette.css` + `correction-anatomy.md` +
   `org-shape.md` + smoke registration. One session, Sonnet-tier.
2. **Part 1** H4/H5/H8 script + report (H6 derived-stratum only; H7 registered). One session.
3. **Part 4.1 + 4.2** (IDs + datasheet template) — small, unblocks releases.
4. **Part 3 + 4.4** contracts (issues on csl-atlas / csl-standards + interlinks row).
5. **Part 4.5** reference graph — after 1–3; it mints a new dataset and should land with its
   datasheet and IDs already in force.

Gates that stay parked: second annotator for κ (standing, tracked); Zenodo DOI (deferred until
17-07-2026).

_Dr. Mārcis Gasūns_
