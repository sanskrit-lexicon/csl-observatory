# Stage 3 — encode & compute 9 pairwise distance matrices

**Goal**: produce 9 distance matrices (3 encodings × 3 metrics) over the 35 dicts.
**Estimated time**: ~30 min.
**Architecture**: [ARCHITECTURE.md](ARCHITECTURE.md)

## Preflight (halts if not satisfied)

- `data/L0/convention_fingerprint.csv` exists.
- No `source=unknown` rows. Verify by scanning the source columns.
- Latest Stage 2 block in EXECUTION_LOG.md has `cells_unknown: 0`.

If preflight fails: log block with `status: blocked_preflight`, exit non-zero.

## Inputs

- `data/L0/convention_fingerprint.csv` (35 × 90)
- `data/L0/dim_schema.json`

## Outputs

- `data/L0/encoded/encoding_A_setmember.csv` — 35 × ~100 binary (one column per dim-option).
- `data/L0/encoded/encoding_B_primary_secondary.csv` — 35 × 60 (primary + secondary per dim).
- `data/L0/encoded/encoding_C_inconsistency.csv` — 35 × 60 (primary + consistency score per dim).
- `data/L0/distances/<enc>_<metric>.csv` — 9 files, each 35 × 35 symmetric:
  - `A_hamming.csv`, `A_weighted_hamming.csv`, `A_jaccard.csv`
  - `B_hamming.csv`, `B_weighted_hamming.csv`, `B_spearman.csv`
  - `C_hamming.csv`, `C_weighted_hamming.csv`, `C_jaccard.csv`
- `data/L0/distances/_summary.json` — min/max/mean/std per matrix.

## Steps

1. **Encoding A — set-membership**: for each (dict, dim), emit one binary column per option. If a dict uses options {1, 5}, bits 1 and 5 are set.
2. **Encoding B — primary + secondary**: two columns per dim — primary option index, secondary option index (NaN if only one).
3. **Encoding C — inconsistency-flagged**: primary option index + consistency score in [0, 1] derived from sampling spread (use the `confidence` field from Stage 2; if a cell's source is `patel` or `annotator`, treat consistency as 1.0).
4. **Metrics** per L0_DESIGN.md §4:
   - **Hamming**: count of differing cells.
   - **Weighted Hamming**: weight = `-log(P(option))` over the 35-dict frequency of that option.
   - **Jaccard**: `1 − |A ∩ B| / |A ∪ B|` on the binary set-membership encoding.
   - **Spearman** (for Encoding B): rank correlation per dim → `1 − mean_rho`.
5. Compute the 9 matrices. Round to 4 decimals.
6. Verify each: symmetric (`max |M − Mᵀ| < 1e-9`), diag = 0, no NaN, no negatives.
7. Write `_summary.json`. Run `_provenance.write_source(...)` on every CSV.
8. Commit: `L0/stage3: 3 encodings + 9 pairwise distance matrices`.

## Acceptance criteria

- 9 distance CSVs exist; each is 35 × 35.
- All are symmetric; diag = 0; no NaN/negatives.
- 3 encoding CSVs exist; row count = 35.
- `_summary.json` lists 9 entries.

## Report

```
### Stage 3 — distance   [<UTC ISO>]
status: ok | fail | blocked_preflight
commit: <sha>
encoded_files: 3
distance_matrices: 9
shape: 35 × 35
matrix_stats_path: data/L0/distances/_summary.json
notes: <≤1 paragraph>
open_questions: []
```
