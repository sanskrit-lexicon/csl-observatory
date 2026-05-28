# Stage 6 — publish (dashboard page + results draft)

**Goal**: render the dashboard page and produce a ≤100-line prose draft for Claude/M.G. review. Final paper prose is **not** in scope.
**Estimated time**: ~1 hour.
**Architecture**: [ARCHITECTURE.md](ARCHITECTURE.md)

## Preflight

- `data/L0/validation_report.json` exists.
- `canonical_bayes_consensus.newick` exists.

## Inputs

- Everything under `data/L0/`.
- Existing dashboard pages under `observatory/` (read 2-3 sibling pages first to mimic structure).

## Outputs

- `observatory/lexicography/conventions.md` — 7-section dashboard page per L0_DESIGN.md §7.2:
  1. Method (2-3 short paragraphs)
  2. Per-dict fingerprint table (interactive, sortable, 35 × 30)
  3. Distance heatmap (35 × 35; dropdown switches encoding+metric)
  4. **Lead chart**: canonical Bayes-consensus cladogram
  5. Small-multiples grid of 27 trees (~270px per panel)
  6. Validation panel (recovery + LOO + bootstrap CIs)
  7. Discussion (3 short paragraphs)
- `docs/handoffs/L0_RESULTS_DRAFT.md` — ≤100-line prose draft for review. Sections:
  - Headline (1 paragraph)
  - Key empirical findings (3-5 bullets, numbers from `validation_report.json` verbatim)
  - Notable failures or limitations
  - Recommended next phases (cross-link to L0.5, L0.6, L0.7)

## Steps

1. Read 2-3 existing `observatory/` pages to learn the project's conventions (chart libraries, frontmatter, data-import patterns). Mimic — do not invent new patterns.
2. Build `conventions.md`. Embed:
   - canonical Newick string in a small `tree.js` block, rendered via the chart lib already used in the repo (likely `d3-hierarchy` or `phylotree.js`).
   - the 9 distance matrices for the heatmap dropdown.
   - all 27 trees for the small-multiples grid.
   - `validation_report.json` for the validation panel; show pass/fail flags from Stage 5.
3. Write prose: method ≤ 300 words, discussion ≤ 500 words. Every numeric claim must trace to `validation_report.json` exactly.
4. Write `L0_RESULTS_DRAFT.md` (≤ 100 lines). Pull bullet findings from `validation_report.json`. Cross-link to next-phase docs.
5. Commit: `L0/stage6: dashboard page + results draft`.

## Acceptance criteria

- `observatory/lexicography/conventions.md` exists; all 7 sections present.
- Page renders without errors locally (`yarn dev` / Observable equivalent — if not runnable in your env, do a syntactic lint and log the gap).
- All numeric claims in prose match `validation_report.json` exactly.
- `L0_RESULTS_DRAFT.md` ≤ 100 lines.

## Final handoff

After Stage 6: open a PR titled `Phase L0 — execution complete (stages 1-6)`. Body links to EXECUTION_LOG.md. M.G. + Claude take over for the paper-final pass.

## Report

```
### Stage 6 — publish   [<UTC ISO>]
status: ok | fail
commit: <sha>
dashboard_page: observatory/lexicography/conventions.md
sections_present: 7
results_draft: docs/handoffs/L0_RESULTS_DRAFT.md
results_draft_lines: <n>
pr_url: <if opened>
notes: <≤1 paragraph>
open_questions: []
```
