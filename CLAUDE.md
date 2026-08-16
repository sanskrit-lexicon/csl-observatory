# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**csl-observatory** is a Sanskrit Lexicon **build-meta** repository — part of the Cologne Digital Sanskrit Lexicon (CDSL) infrastructure.

## Repo Category

`build-meta` — see the [tooling runbook](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/runbook/cologne-tooling-runbook.md) for category-specific conventions.

## GitHub Issue Conventions

This repository uses the **Cologne tooling-repo taxonomy**. All issues must have:
- **Exactly one type label** (9 options)
- **Exactly one severity label** (4 levels)
- **One milestone** (5 options)

### Type Labels
- `bug` — Code defect (wrong output, broken contract)
- `feature` — Net-new capability
- `enhancement` — Improvement to existing capability
- `performance` — Speed, memory, throughput optimization
- `tech-debt` — Refactoring, cleanup, dependency updates
- `security` — CVE, auth issue, credential exposure
- `documentation` — Prose docs, API docs, comments
- `infrastructure` — CI/CD, deploy, data pipelines, build tooling
- `question` — Research, proposals, open discussions

### Severity Labels
- `trivial` — Cosmetic, < 1 hour
- `minor` — Single function/component
- `major` — Multiple files, design decision
- `critical` — Blocks users, data loss/security CVE

### Milestones
- **API Stability** — performance, security, regressions
- **User Experience** — bugs, features, enhancements
- **Data Quality** — data-pipeline issues, integrity
- **Developer Experience** — tech-debt, infrastructure, docs
- **Community** — questions, proposals, discussions

## Cross-Repo Coordination

The org-level project [Tooling Roadmap](https://github.com/orgs/sanskrit-lexicon/projects/9) tracks tool work across all repositories.

## PWG citation counts — the one rule that is not obvious

Anything numeric about how much of PWG a literary source carries goes through
[`data/pwg_scan_index_tracker/ls_counts/`](https://github.com/sanskrit-lexicon/csl-observatory/tree/main/data/pwg_scan_index_tracker/ls_counts).
Three rules, all enforced by
`python scripts/pwg_citation_count_provenance.py --check`:

1. **Consume `citation_count_safe`, never `citation_count`.** The latter is the
   spreadsheet's transcription and is kept only as evidence.
2. **Fold by `in_pwgbib` before summing.** The count is a work-*family* rollup, so
   `AK. Deslongchamps ed.` and `AK. Colebrooke ed.` share one total.
3. **Divide only by the `ALL` of the same snapshot** (`citation_mass_denominator` in the
   summary JSON). The cleaned-string totals in PWG's `sortedcrefs.txt` count a different
   object and are never a denominator for these.

**Sync rule:** changing the tracker snapshot means re-running
`pwg_citation_count_provenance.py` *before* `pwg_scan_index.py` in the same PR — the
registry reads its provenance columns from that dataset. Never regenerate
`pwg_ls_counts_2024-09-11.tsv`; `--recount` writes the `_current` table only. Full
argument: [`reports/pwg_citation_count_provenance.md`](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/reports/pwg_citation_count_provenance.md).

## Operational hazard notes

Destructive-risk facts for this repo (do-not-rerun scripts, decoys, traps) are
registered centrally in an org-private hub
([Uprava DANGER_FACTS.md](https://github.com/gasyoun/Uprava/blob/main/DANGER_FACTS.md),
org members only); the public-safe subset is mirrored in the generated block of
[AGENTS.md](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/AGENTS.md). Check them
before running anything that writes.
