# Stage 5 — validation

**Goal**: report known-edge recovery, LOO accuracy, and 1000-bootstrap CIs for the canonical Bayes-consensus tree, plus a recovery-only pass on the 26 alternative trees.
**Estimated time**: ~45 min.
**Architecture**: [ARCHITECTURE.md](ARCHITECTURE.md)

## Preflight

- 27 trees in `data/L0/trees/`.
- `canonical_bayes_consensus.newick` exists.

## Inputs

- All `data/L0/trees/*.newick` (27 + 1 canonical)
- `data/L0/known_edges.csv` — fixed file written at this stage's start; see Step 1.

## Outputs

- `data/L0/known_edges.csv` — the canonical edge list.
- `data/L0/validation_report.json` — per-tree recovery score; canonical also: LOO accuracy, bootstrap CIs.
- `data/L0/bootstrap_support.csv` — per-edge bootstrap support for the canonical tree.

## Steps

1. **Write `known_edges.csv`** from L0_DESIGN.md §6.1 + MICROSTRUCTURE-MACROSTRUCTURE.md §5.2 (Round-1 captured edges). Columns: `source, target, evidence_tier (1=confirmed, 2=likely, 3=hypothesis), notes`. Edges:
   - tier 1 (confirmed): WIL→YAT, WIL→SHS, ARMH→MW, ABCH→MW, PWG→PW, MW72→MW, AP→AP90, CCS→CAE
   - tier 2 (Round-1 hypotheses): PW→MW, PWG→MW72, PWG→SHS, CCS→KCH
2. **Recovery score** per tree: fraction of edges where target's nearest predicted ancestor matches source (or source's predicted descendant). Per L0_DESIGN.md §6.1.
3. **Leave-one-out** (canonical only): per edge, mask the source-target pair from the distance matrix, rebuild Bayes consensus, check whether target's nearest neighbour in the rebuilt tree is source (or descendant).
4. **Bootstrap** (canonical only): 1000 resamples of the fingerprint dims (sample-with-replacement on columns), rebuild Bayes consensus per resample, compute per-edge frequency over the 1000 trees.
5. Build `bootstrap_support.csv` — every internal edge of canonical tree + support fraction in [0, 1].
6. **Recovery-only** pass on the 26 non-canonical trees (no LOO, no bootstrap — too expensive).
7. Pass/fail flags per L0_DESIGN.md §6.4:
   - canonical_recovery ≥ 0.70
   - canonical_loo ≥ 0.60
   - "strongest" edges (PWG→PW, MW72→MW, AP→AP90) ≥ 0.80 bootstrap support
   If any "strongest" fails: do **not** fail the stage. Record in `failure_modes` block; Stage 6 narrates the limitation.
8. Commit: `L0/stage5: validation (recovery + LOO + bootstrap)`.

## Acceptance criteria

- `validation_report.json` has one entry per tree (27 + canonical).
- `bootstrap_support.csv` row count ≥ canonical internal-edge count.
- Pass/fail flags computed and recorded.
- Stage does **not** fail on edge-support shortfall — only on missing/malformed outputs.

## Report

```
### Stage 5 — validate   [<UTC ISO>]
status: ok | fail
commit: <sha>
canonical_recovery: <0..1>
canonical_loo: <0..1>
strongest_edges_support:
  "PWG->PW": <0..1>
  "MW72->MW": <0..1>
  "AP->AP90": <0..1>
acceptance_overall: pass | partial | fail
notes: <≤1 paragraph>
open_questions: []
```
