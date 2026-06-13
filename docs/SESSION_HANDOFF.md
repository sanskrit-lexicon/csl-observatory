# Session Handoff

Date: 2026-06-03

Read this first when resuming `csl-observatory`.

`csl-observatory` is now the GitHub/org observatory only. Its live scope is
measurement, dashboards, contribution analytics, repo health, issue
taxonomy, release/process documentation, and organization-level governance
for the Cologne Digital Sanskrit Lexicon ecosystem.

Boundary cleanup status: merged on 2026-06-04 in
[`csl-observatory` PR #14](https://github.com/sanskrit-lexicon/csl-observatory/pull/14).

## Start Here

1. Read `docs/DECISIONS_NEEDED.md` and surface the open human blockers.
2. Read `docs/BOUNDARY_RULES.md` before adding or moving material.
3. Use `docs/OBSERVATORY_DESIGN.md`, `docs/OBSERVATORY_ROADMAP.md`, and
   `docs/ROADMAP.md` for the active observatory program.
4. Use `docs/CONTRIBUTOR_STATS.md`, `docs/RUNBOOK_NOTES.md`, and
   `docs/PAPER_1_OUTLINE.md` for current evidence and publication framing.

## Current Open Items

- B2: verify bibliography for the 6 documented repos, especially BUR and BOP.
- C1: GitHub token with workflow + `read:project` scope for refresh automation.
- C2: Cologne server / analytics access for usage metrics and artifact refresh.
- C3: DNS / Cologne mirror handover for observatory hosting.
- D1: Cologne admin confirmation for `redo_xampp_selective.sh` propagation.

## Boundary Pointers

- Dictionary evidence, dictionary comparison, dictionary genealogy, Patel
  conventions, L0, R2, and microstructure/macrostructure work now belong in
  `csl-atlas`.
- The former mixed handoff was preserved as
  `csl-atlas/docs/SESSION_HANDOFF.md`.
- A local pointer is kept at `docs/DICTIONARY_STRUCTURE_MOVED.md`.
- TEI/OntoLex/FrAC/SHACL/RDF export and validation work belongs in
  [`csl-standards`](https://github.com/sanskrit-lexicon/csl-standards).
- DCS/corpus data belongs in [`VisualDCS`](https://github.com/gasyoun/VisualDCS);
  the atlas handoff material is in `docs/csl-atlas-migration/`. Grammar needs
  a future separate repo.

## Agent Rules

- Do not add new dictionary-structure research to this repo.
- Do not add TEI/OntoLex/FrAC standards work to this repo.
- Do not add DCS/corpus dashboards here.
- Observatory pages may link to those external paths, but they should start
  from repos, issues, contributors, workflows, governance, metrics, or
  organization-level publication planning.
