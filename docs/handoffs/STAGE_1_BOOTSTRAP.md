# Stage 1 — bootstrap

**Goal**: prepare the L0 working tree so all subsequent stages run without setup steps.
**Estimated time**: 15 minutes.
**Architecture**: [ARCHITECTURE.md](ARCHITECTURE.md)

## Inputs

- Repo root: `csl-observatory`
- Existing: `data/dictionary_inventory.csv` (47 dicts)
- Patel PDF: env `PATEL_PDF` or `data/sources/patel_2016.pdf` (optional at this stage)

## Outputs

- Directories: `scripts/L0/`, `data/L0/`, `data/L0/distances/`, `data/L0/encoded/`, `data/L0/trees/`, `dist/L0/`
- Files:
  - `scripts/L0/requirements.txt`
  - `scripts/L0/__init__.py` (empty)
  - `scripts/L0/_provenance.py`
  - `data/L0/inventory_subset.csv` — 35 in-scope dicts
- `.gitignore`: add `/dist/L0/` if missing

## Steps

1. Create directories (idempotent: `mkdir -p` semantics).
2. Write `requirements.txt`:
   ```
   numpy>=1.26
   pandas>=2.1
   scipy>=1.11
   scikit-bio>=0.6        # neighbour-joining
   biopython>=1.83        # tree IO
   dendropy>=4.6          # Robinson-Foulds
   matplotlib>=3.8        # static-chart fallback
   ```
3. Write `_provenance.py` with one function:
   ```python
   def write_source(out_path: str, script: str, stage: int) -> None: ...
   ```
   It writes `<out_path>.source.json` containing `{"stage": stage, "commit": <git rev-parse HEAD>, "utc_iso": <now>, "script": script}`.
4. Add `/dist/L0/` to `.gitignore` (no-op if already present).
5. Filter `dictionary_inventory.csv` → in-scope rows. The L0 scope is `in_github == "yes"` ∧ `in_sanhw1 == "yes"`. Write `data/L0/inventory_subset.csv` preserving columns. Target row count: 35.
6. Verify Patel PDF path; record presence/absence in the report. Do not fail if absent.
7. `pip install --dry-run -r scripts/L0/requirements.txt` — verify the spec parses.
8. `python -c "import numpy, pandas, scipy"` — sanity-check the env.
9. Commit: `L0/stage1: bootstrap working tree`. Body cites this doc.

## Acceptance criteria

- `inventory_subset.csv` has exactly 35 rows.
- All 6 new directories exist.
- `requirements.txt` parses (dry-run succeeds).
- Sanity import succeeds.

If any criterion fails: write failure block, exit non-zero, do not proceed.

## Report (append one block to EXECUTION_LOG.md)

```
### Stage 1 — bootstrap   [<UTC ISO>]
status: ok | fail
commit: <sha>
inventory_subset_rows: <n>
patel_status: present | pending
dirs_created: 6
notes: <≤1 paragraph>
open_questions: []
```
