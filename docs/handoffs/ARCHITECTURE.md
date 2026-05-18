# Phase L0 — architecture for Gemini Flash execution

**Date**: 2026-05-16
**Design source**: [docs/L0_DESIGN.md](../L0_DESIGN.md)
**Executor**: Gemini Flash
**Reporter**: append one entry per stage to [EXECUTION_LOG.md](EXECUTION_LOG.md)
**Reviewer (human)**: M. Gasūns + Claude (next session)

---

## Goal (one sentence)

Produce the first convention-fingerprint phylogenetic tree of 35 CDSL dictionaries with multi-encoding × multi-metric × multi-algorithm sensitivity and three-method validation, per L0_DESIGN.md.

## Pipeline — six stages, six handoff docs

```
Stage 1  bootstrap     repo dirs, deps, inputs fetched
Stage 2  fingerprint   35×30 matrix; src: patel|auto|annot|consensus
Stage 3  distance      9 pairwise matrices (3 enc × 3 metric)
Stage 4  cluster       27 Newick trees (× 3 algos: UPGMA, NJ, Bayes)
Stage 5  validate      known-edge recovery + LOO + 1000-bootstrap CIs
Stage 6  publish       /lexicography/conventions.md + draft prose
```

Each stage has its own ≤100-line handoff: `STAGE_<n>_<NAME>.md`. Read only the stage you are executing — this architecture doc is the only cross-stage reference.

## Data contracts

| Stage | reads | writes |
|---|---|---|
| 1 | repo root | `data/L0/`, `scripts/L0/`, `dist/L0/` (empty) |
| 2 | `data/dictionary_inventory.csv`, Patel PDF, dict XMLs | `data/L0/convention_fingerprint.csv`, `annotation_todo.csv` |
| 3 | `convention_fingerprint.csv` | `distances/<enc>_<metric>.csv` (9) |
| 4 | `distances/*.csv` | `trees/<enc>_<metric>_<algo>.newick` (27) + canonical consensus |
| 5 | `trees/*.newick` | `validation_report.json`, `bootstrap_support.csv` |
| 6 | all of above | `observatory/lexicography/conventions.md`, `L0_RESULTS_DRAFT.md` |

## Repo conventions

- Code: `scripts/L0/` — one module per stage (`s1_bootstrap.py`, …, `s6_publish.py`)
- Data: `data/L0/` — all outputs here; no temp scratch elsewhere
- Built artefacts: `dist/L0/` — gitignored
- Python ≥ 3.10; pinned `scripts/L0/requirements.txt`
- CSVs: UTF-8, comma-delimited, header row required
- Newick: ASCII labels matching `inventory_subset.csv` dict codes; no Unicode

## Reporting (single tracking doc)

After each stage, append exactly **one** Markdown block to `EXECUTION_LOG.md`. Block schema is defined at the top of EXECUTION_LOG.md and shown in each stage's "Report" section. **Do not edit prior entries.**

## Hard rules

1. **No mutation of human-annotated cells** without a `--reannotate` flag from a reviewer.
2. **Stop on stage failure.** If acceptance criteria fail, write the failure block to EXECUTION_LOG.md and exit non-zero. Do not start the next stage.
3. **No silent rewrites.** Every script-produced CSV gets a `_source` sidecar via `scripts/L0/_provenance.py` (1-line JSON: `{stage, commit, utc_iso, script}`).
4. **One commit per stage.** Message: `L0/stage<n>: <one-line summary>`. Body links to the stage doc.
5. **Idempotency.** Re-running a stage on the same inputs produces identical outputs (modulo timestamps in sidecars).

## Resumption

You may start at any stage whose preflight passes. Check EXECUTION_LOG.md to see which stages have a status block. Stage 2 has a **human gate** — it ends with `status: awaiting_human_annotation`; resume from Stage 3 once `annotation_todo.csv` is filled and merged back into `convention_fingerprint.csv`.

## Out of scope

- Phase L0.5 (Nirukta), L0.6 (subentry), L0.7 (hapax) — separate handoffs
- Final paper prose (M.G. + Claude write the final pass)
- Dashboard pages outside `/lexicography/conventions.md`

## When in doubt

Re-read the stage's handoff doc. Do not improvise beyond what is specified. If a step is ambiguous, log the question in `EXECUTION_LOG.md` under that stage's `open_questions` field and stop.
