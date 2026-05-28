# Stage 4 — cluster (27 trees + canonical consensus)

**Goal**: produce 27 candidate phylogenetic trees (3 algos × 9 distance matrices) plus a canonical Bayesian consensus over the 9 Bayes trees.
**Estimated time**: UPGMA + NJ ~5 min; Bayes heuristic ~30 min.
**Architecture**: [ARCHITECTURE.md](ARCHITECTURE.md)

## Preflight

- 9 CSVs in `data/L0/distances/`, each 35 × 35, symmetric, diag = 0.

## Inputs

- `data/L0/distances/*.csv` (9)
- `data/L0/inventory_subset.csv` — for ASCII dict labels.

## Outputs

- `data/L0/trees/<enc>_<metric>_<algo>.newick` — 27 trees
  - Algos: `upgma`, `nj`, `bayes`
- `data/L0/trees/canonical_bayes_consensus.newick` — 1 consensus tree (majority-rule over the 9 Bayes trees).
- `data/L0/trees/tree_comparison_rf.csv` — 27 × 27 Robinson-Foulds matrix.

## Steps

1. **UPGMA**: `scipy.cluster.hierarchy.linkage(method='average')` on each of 9 distance matrices. Convert linkage matrices to Newick via BioPython `Phylo` or a custom 20-line converter.
2. **Neighbor-Joining**: `skbio.tree.nj` on each of 9 matrices.
3. **Bayesian heuristic** per L0_DESIGN.md §9: stochastic NN-interchange (SPR moves) with Metropolis acceptance; likelihood ∝ `exp(-distance_fit_score)`.
   - 100 iters per non-canonical config (8 of 9).
   - 1000 iters for the canonical run. Canonical config = the first encoding+metric pair sorted alphabetically (`A_hamming`). Record which config is canonical in the report.
4. **Canonical consensus**: majority-rule consensus over the 9 Bayes trees → `canonical_bayes_consensus.newick`.
5. **Robinson-Foulds matrix**: `dendropy.calculate.treecompare.symmetric_difference` for all 27 × 27 pairs.
6. Provenance sidecars on every Newick.
7. Commit: `L0/stage4: 27 trees + canonical Bayes consensus`.

## Acceptance criteria

- Exactly 27 Newick files in `data/L0/trees/`.
- `canonical_bayes_consensus.newick` parses and has 35 leaves.
- All Newick files use ASCII dict labels (no Unicode); labels match `inventory_subset.csv`.
- RF matrix is 27 × 27, symmetric, diag = 0, integer-valued.

## Report

```
### Stage 4 — cluster   [<UTC ISO>]
status: ok | fail
commit: <sha>
trees_produced: 27
canonical_consensus: present
rf_matrix_shape: 27 × 27
bayes_iters_canonical: 1000
bayes_iters_other: 100
canonical_config: <enc>_<metric>
notes: <≤1 paragraph>
open_questions: []
```
