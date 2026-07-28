#!/usr/bin/env python3
"""build_blind_sample.py — blind input for the H1385 A12 location-axis κ pilot.

Implements §2.3 (blindness as a build step) of the org protocol
docs/PROTOCOL_BLIND_LLM_SECOND_ANNOTATOR_RELIABILITY_2026.md (Uprava):

  - reads validation/gold_sample.csv (390 rows, pinned commit stated in the
    pre-registration) and STRIPS gold_component, gold_component_2 and notes
    (labels + pass-1 reasoning must not reach either annotator);
  - SHUFFLES rows with the pre-registered seed 20260721 — the sheet was drawn
    stratified by (auto component x evidence), so original ordering could leak
    the auto label grouping ("not inferable from row ordering");
  - writes validation/gold_sample_blind.json (all 390 blind rows, shuffled
    order) and validation/blind_batches/batch_01.json .. batch_07.json.
    batch_01 is exactly the 30-row flip-rate subsample (first 30 shuffled
    rows), so repeated stability runs reuse a byte-identical payload;
    batches 02-07 carry 60 rows each.

Deterministic; stdlib only.
"""
import csv
import json
import random
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

HERE = Path(__file__).resolve().parent
SHEET = HERE / "gold_sample.csv"
OUT_ALL = HERE / "gold_sample_blind.json"
OUT_DIR = HERE / "blind_batches"
SEED = 20260721
FLIP_N = 30
BATCH_N = 60

BLIND_COLS = ["row_id", "source_layer", "dict", "headword_iast",
              "old_iast", "new_iast", "old_raw", "new_raw", "comment_raw"]

def main():
    csv.field_size_limit(10_000_000)
    with SHEET.open(encoding="utf-8", newline="") as fh:
        rows = list(csv.DictReader(fh))
    assert len(rows) == 390, f"expected 390 rows, got {len(rows)}"
    blind = [{c: r[c] for c in BLIND_COLS} for r in rows]
    rng = random.Random(SEED)
    rng.shuffle(blind)

    OUT_ALL.write_text(json.dumps(blind, ensure_ascii=False, indent=1),
                       encoding="utf-8")
    OUT_DIR.mkdir(exist_ok=True)
    batches = [blind[:FLIP_N]]
    rest = blind[FLIP_N:]
    for i in range(0, len(rest), BATCH_N):
        batches.append(rest[i:i + BATCH_N])
    for i, b in enumerate(batches, 1):
        (OUT_DIR / f"batch_{i:02d}.json").write_text(
            json.dumps(b, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"blind rows: {len(blind)}  batches: {len(batches)} "
          f"(batch_01={len(batches[0])} = flip subsample; rest "
          f"{[len(b) for b in batches[1:]]})")

if __name__ == "__main__":
    main()
