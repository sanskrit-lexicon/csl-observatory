# Stage 2 — fingerprint matrix

**Goal**: produce a 35 × 30 fingerprint matrix where every cell has a value or explicit `unknown`, plus a provenance column per cell (`patel | auto | annotator | consensus | unknown`).
**Estimated time**: scripted ~30 min; then **human gate** before Stage 3.
**Architecture**: [ARCHITECTURE.md](ARCHITECTURE.md)

## Inputs

- `data/L0/inventory_subset.csv` (35 dicts)
- Patel 2016 PDF (if present from Stage 1)
- Per-dict source XML — fetch on demand from `raw.githubusercontent.com/sanskrit-lexicon/<DICT>/master/<dict>.xml`. Stream-read; do not persist the XMLs.
- Canonical dim list: [`L0_DESIGN.md §2`](../L0_DESIGN.md) — 30 dims, each categorical with 2-6 options.

## Outputs

- `data/L0/dim_schema.json` — `[{dim_id, name, options: [str]}]` × 30. Transcribe verbatim from L0_DESIGN.md §2; do not improvise options.
- `data/L0/convention_fingerprint.csv` — 35 rows × 90 cols (30 dims × 3: value, source, confidence).
- `data/L0/annotation_todo.csv` — every cell where `source=unknown` after auto-fill. Columns: `dict, dim_id, dim_name, options_available`.
- `data/L0/fingerprint_summary.json` — coverage per dim.

## Steps

1. Write `dim_schema.json` from L0_DESIGN.md §2.
2. **Patel pass** (if PDF present): extract dims 1-7 per dict from the PDF tables. Set `source=patel`, `confidence=1.0`. If PDF absent, dim-1..7 cells stay `unknown`.
3. **Auto-extract pass** — mechanically detectable dims from each dict's XML:
   - dim 10: `<k2>` variant-headword rate
   - dim 11: sense-numbering (regex `<s>1</s>` vs Roman vs alpha)
   - dim 14: citation depth (longest-numeric-tail of bracketed citations)
   - dim 17: grammar markers (proportion of `m\.|f\.|n\.` vs `masc\.|fem\.|neut\.`)
   - dim 22: Vedic accent (SLP1 accent markers in body)
   - dim 28: etymology presence (dict-specific patterns from L0_DESIGN.md §15)
   Use **adaptive sampling** per L0_DESIGN.md §11: sample until per-convention assignment converges at 95% confidence; cap at 500 entries per dict.
4. Set `source=auto`, `confidence ∈ [0.5, 1.0]` based on convergence margin.
5. Remaining cells: `source=unknown`, value empty. Enumerate in `annotation_todo.csv`.
6. Write `fingerprint_summary.json` with per-dim coverage breakdown.
7. Commit: `L0/stage2: fingerprint auto-fill (Patel + 6 auto dims)`.
8. **STOP**. Append `status: awaiting_human_annotation` to EXECUTION_LOG.md. Do **not** start Stage 3.

## Human gate

M.G. + Claude annotate the unknown cells (target: all of them) in a follow-up session, per L0_DESIGN.md §12 (co-annotation workflow with Cohen's κ on a 10% overlap sample). The completed `convention_fingerprint.csv` is committed back; Stage 3's preflight detects `cells_unknown=0` and proceeds.

## Acceptance criteria

- 35 rows × 90 cols (30 dims × {value, source, confidence}).
- ≥ 40% of value cells filled (≥ 420 of 1050) after auto pass.
- `annotation_todo.csv` row count = number of `unknown` cells.
- All Patel-source cells have `confidence = 1.0`.
- `dim_schema.json` validates against L0_DESIGN.md §2 (manual spot-check; if any dim option diverges, log in `open_questions` and stop).

## Report

```
### Stage 2 — fingerprint   [<UTC ISO>]
status: awaiting_human_annotation | fail
commit: <sha>
cells_total: 1050
cells_filled_patel: <n>
cells_filled_auto:  <n>
cells_unknown:      <n>
annotation_todo_rows: <n>
notes: <≤1 paragraph>
open_questions: []
```
