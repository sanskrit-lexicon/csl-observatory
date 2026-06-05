# Status

> **Current status (2026-06-05).** The observatory build-out is complete:
> four reproducible findings + synthesis + a contributor-identity worksheet,
> all on the [dashboard](https://sanskrit-lexicon.github.io/csl-observatory/),
> with actionable follow-ups filed as issues #15–#25 on
> [Tooling Roadmap project #9](https://github.com/orgs/sanskrit-lexicon/projects/9).
> To catch up, read **[`README.md`](README.md)** → **[`reports/README.md`](reports/README.md)**
> → **[`reports/synthesis.md`](reports/synthesis.md)**. Live working state is in
> [`.ai_state.md`](.ai_state.md).
>
> The section below is the **historical** record of the 2026-05-07 session,
> retained for provenance.

---

## Historical — autonomous work session 2026-05-07

This file summarises what was built during the two-hour autonomous session
on 2026-05-07.

## Strategic decision taken without confirmation

The user's instruction was: *"The article you are working on should become a
part of the report.md or continue in detail some of its aspects."* Given
that the existing `gasuns-cologne-30-report.md` is a 1,521-line first-person
scholarly narrative in Mārcis Gasūns' distinctive voice, and that
duplicating it in a different voice would be wasteful, I chose **option B
(continue in detail)** and pivoted the article scaffold into a formal
empirical/methodological *companion* paper. The two papers are now paired
in `article/`, with shared abstract structure and explicit cross-references.

If the user prefers option A (integration into the report itself, in the
same voice), the companion paper can be merged in as new sections; the
data tables and visualisations are fully transferable.

## Completed deliverables (chronological)

1. **Cloned and saved** Gasūns' report to the repo (`gasuns-cologne-30-report.md`
   at root, also mirrored at `article/00-report-narrative.md`).
2. **Pivoted article.md → `article/01-empirical-companion.md`** as a formal
   third-person companion paper with eight sections, including:
   - 2026 issue taxonomy and runbook (§3)
   - Ecosystem snapshot in numbers (§4) — including a per-dictionary
     entry-count table (§4.7) and reconciliation with the report's
     headline figures (§4.8)
   - Standards alignment: FAIR, TEI Lex-0 round-trip, OntoLex-Lemon RDF,
     FORCE11 software citation (§5)
   - The csl-observatory infrastructure (§6)
3. **`scripts/count_headwords.py`** counts `<L>` markers across
   `csl-orig/v02/`. Result: **1,495,422 entries across 43 dictionaries,
   all `<L>`/`<LEND>` balanced** — a strong integrity finding.
4. **`scripts/retry_failed_commits.py`** with backoff retry recovered 273
   commits (VCP, AP, mw-dev). Persistent 502/504s remain on csl-orig and
   eight other large repos; documented as a known limitation.
5. **`scripts/pull_data.py`** updated with retry-on-5xx exponential backoff.
6. **Community files templated and propagated** to all 8 triaged
   dictionary repositories (AP, AP90, FRI, GRA, MD, MWS, PWG, PWK):
   - `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`, `SECURITY.md`
   - `.github/PULL_REQUEST_TEMPLATE.md`
   - 6 × `.github/ISSUE_TEMPLATE/*.yml` (text-correction, markup,
     link-target, encoding, bug, question) + `config.yml`
   - 11 files per repo, 88 files total, all committed and pushed
7. **Tracking issue #1** filed at
   <https://github.com/sanskrit-lexicon/csl-observatory/issues/1>
   inviting nine unidentified contributors to self-identify.
8. **Runbook v2** with phases 11–16 added at
   `~/.claude/commands/cologne-issue-runbook.md`:
   - Phase 11: CITATION.cff + LICENSE + CHANGELOG + Zenodo wiring
   - Phase 12: source-bibliography block
   - Phase 13: data dictionary + annotated example
   - Phase 14: encoding declaration block
   - Phase 15: pipeline DAG (Mermaid flowchart)
   - Phase 16: community files (templated by `propagate_templates.py`)

## Numbers worth remembering

| Metric | Value |
|---|---:|
| Repositories in `sanskrit-lexicon` | 78 |
| Total issues (open + closed) | 5,172 |
| Pull requests | 37 |
| Commits captured | 3,979 (after retry; was 3,706) |
| Distinct contributors after alias merge | 49 |
| Triaged dictionary repos | 8 |
| Typed issues across triaged repos | 608 |
| **Total dictionary entries (`<L>` count)** | **1,495,422** |
| **Dictionaries with balanced `<L>/<LEND>`** | **43 / 43** ✓ |

## Top contributors (after alias merge)

| | Commits | Repos | Span |
|---|---:|---:|---|
| Jim Funderburk | 2,314 + retried | 50 | 2014–2026 |
| Dhaval Patel | 1,088 + retried | 26 | 2015–2026 |
| Mārcis Gasūns | 119 | 19 | 2014–2026 |
| Anna Rybakova | 70 | 10 | 2020–2023 |
| Nagabhushana Rao | 12 | 2 | 2021–2022 |

## What needs the user's attention on return

1. **ORCIDs** — placeholders in `CITATION.cff`, `article/01-empirical-companion.md`,
   and `scripts/contributors_map.json` should be replaced with real ORCIDs
   for Gasūns, Funderburk, Patel, Rao.
2. **Strategic confirmation** — does the article-as-companion choice work?
   Or merge into `report.md`? (See top of this doc.)
3. **Persistent 502s** — csl-orig and 8 other repos cannot be commit-fetched
   via GraphQL. We need either: (a) accept the limitation and note in
   article §7; or (b) add a `git clone --bare && git log` fallback to
   `pull_data.py` for repos that exceed GraphQL pagination limits.
4. **Issue #1 (contributor identification)** — invite the listed people
   to self-identify when they next visit the project.
5. **Article narrative** — section 1 (Introduction) is drafted; sections
   2.1–3.6 of the report itself contain TBD placeholders that you may
   wish to fill. The companion paper covers methodology and data; the
   report covers narrative.
6. **Pandoc build** — to typeset the companion paper:
   ```sh
   cd article && pandoc 01-empirical-companion.md \
     --citeproc --bibliography refs.bib \
     -o 01-empirical-companion.pdf
   ```
   (Requires the Indo-Iranian Journal CSL stylesheet, not yet committed.)

## Files added this session

```
csl-observatory/
├── STATUS.md                                 ← this file
├── gasuns-cologne-30-report.md               ← user wrote earlier
├── article/
│   ├── README.md                              (new)
│   ├── 00-report-narrative.md                 (mirror of root)
│   ├── 01-empirical-companion.md              (was article.md)
│   └── refs.bib                               (extended)
├── data/
│   └── headwords.json                         (new — 1.5M entries)
├── reports/
│   └── coverage.md                            (now substantive)
├── scripts/
│   ├── count_headwords.py                     (new)
│   ├── retry_failed_commits.py                (new)
│   ├── propagate_templates.py                 (new)
│   ├── pull_data.py                           (retry logic added)
│   └── render_reports.py                      (coverage rendering)
└── templates/                                 (new — 11 community files)
    ├── CONTRIBUTING.md
    ├── CODE_OF_CONDUCT.md
    ├── SECURITY.md
    └── .github/
        ├── PULL_REQUEST_TEMPLATE.md
        └── ISSUE_TEMPLATE/
            ├── bug.yml
            ├── encoding.yml
            ├── link-target.yml
            ├── markup.yml
            ├── question.yml
            ├── text-correction.yml
            └── config.yml
```

## Time budget

~110 minutes of autonomous work. Five priority items completed in order.
The article narrative (priority 5) was extended substantially but not
exhaustively; the report's existing TBD placeholders remain TBD.
