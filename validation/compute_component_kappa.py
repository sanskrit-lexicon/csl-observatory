#!/usr/bin/env python3
"""compute_component_kappa.py — Cohen's κ for the H1385 A12 location-axis pilot.

Adaptation of the A65 reference implementation
(SanskritGrammar/verdict_validation/compute_verdict_kappa.py) to the OBS-T
component-location instrument, per the org protocol
docs/PROTOCOL_BLIND_LLM_SECOND_ANNOTATOR_RELIABILITY_2026.md (Uprava) §5 step 7.

Inputs (same directory):
  component_passA.json — [{"row_id": int, "label": str}, ...]  Pass A (Opus 4.8)
  component_passB.json — same shape, Pass B (Sonnet 5), blind to Pass A
  flip_runs/passA_run2.json, passA_run3.json, passB_run2.json, passB_run3.json
      — repeated runs over the 30-row flip subsample (batch_01)
  blind_batches/batch_01.json — defines the flip subsample row_ids

Outputs:
  component_kappa_stats.json — κ + 95% bootstrap CI (2,000 resamples, seed
      20260721) at L0 (8 labels) and L1 (4 pre-registered groups), raw
      agreement at both levels, per-label agreement, confusion matrix,
      per-annotator flip-rates, model provenance.
  component_kappa_disagreements.csv — every L0 disagreement row (the codebook-
      repair artifact).

Pure stdlib; deterministic.
"""
import argparse
import csv
import json
import random
import sys
from collections import Counter
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

HERE = Path(__file__).resolve().parent
SEED = 20260721
N_BOOT = 2000

L0 = ["headword", "grammar", "citation", "sense", "crossref", "meta",
      "markup", "unattributed"]
# Pre-registered L1 ladder (protocol §6): content / reference / structure / unattributed
L1_MAP = {"headword": "content", "grammar": "content", "sense": "content",
          "citation": "reference", "crossref": "reference",
          "meta": "structure", "markup": "structure",
          "unattributed": "unattributed"}
L1 = ["content", "reference", "structure", "unattributed"]


def cohen_kappa(pairs, cats):
    n = len(pairs)
    if n == 0:
        return float("nan")
    po = sum(1 for a, b in pairs if a == b) / n
    ca, cb = Counter(a for a, _ in pairs), Counter(b for _, b in pairs)
    pe = sum((ca[c] / n) * (cb[c] / n) for c in cats)
    if pe == 1.0:
        return 1.0
    return (po - pe) / (1 - pe)


def load_pass(name):
    rows = json.loads((HERE / name).read_text(encoding="utf-8"))
    out = {}
    for r in rows:
        lab = str(r["label"]).strip().lower()
        # Normalise the id ONCE and key/assert on the same value (H7108,
        # bughunt §13): a string-id exporter ("row_id": "1") walked past the
        # old guard because `out` was keyed by int while the assert compared
        # the raw value.
        rid = int(r["row_id"])
        assert lab in L0, f"{name}: illegal label {lab!r} on row {rid}"
        assert rid not in out, f"{name}: duplicate row_id {rid}"
        out[rid] = lab
    return out


def kappa_block(pairs, cats):
    n = len(pairs)
    k = cohen_kappa(pairs, cats)
    agree = sum(1 for a, b in pairs if a == b) / n
    rng = random.Random(SEED)
    boots = sorted(cohen_kappa([pairs[rng.randrange(n)] for _ in range(n)], cats)
                   for _ in range(N_BOOT))
    return {
        "n": n,
        "kappa": round(k, 3),
        "kappa_ci95": [round(boots[int(0.025 * N_BOOT)], 3),
                       round(boots[int(0.975 * N_BOOT)], 3)],
        "raw_agreement": round(agree, 3),
    }


def flip_rate(files, subsample_ids):
    """Fraction of (row x run-pair) label changes across the runs of one annotator.

    A missing flip-run file is a BROKEN INSTRUMENT, not a missing measurement:
    the runs are committed artifacts defining the stability statistic, so the
    pre-H7108 behaviour of storing "missing <file>" in a numeric 0..1 field
    (bughunt §9) is now a hard stop.
    """
    runs = []
    for f in files:
        p = HERE / f
        if not p.exists():
            raise SystemExit(
                f"ERROR: flip-rate instrument is incomplete — {f} is missing. "
                "The flip runs are committed artifacts; restore the file "
                "instead of publishing a stats JSON without a flip rate.")
        runs.append(load_pass(f))
    flips = total = 0
    for rid in subsample_ids:
        labs = [r[rid] for r in runs if rid in r]
        for i in range(len(labs)):
            for j in range(i + 1, len(labs)):
                total += 1
                if labs[i] != labs[j]:
                    flips += 1
    return round(flips / total, 3) if total else None


def check_denominator(a, b, allow_partial=False):
    """Rows present in exactly one pass; stop unless the loss was accepted.

    The pre-registered instrument is n=390. A dropped annotation batch used to
    shrink the kappa denominator silently (a WARN line and exit 0), so a
    partial run was indistinguishable from a clean one in the artifact
    (H7108, bughunt §8). `--allow-partial` is the explicit opt-in, and the
    loss is then recorded in the JSON by the caller.
    """
    missing = sorted(set(a) ^ set(b))
    if missing and not allow_partial:
        raise SystemExit(
            f"ERROR: {len(missing)} rows are present in only one pass: "
            f"{missing[:10]}{' …' if len(missing) > 10 else ''}. "
            "A dropped annotation batch shrinks the kappa denominator; re-run "
            "with --allow-partial to publish a knowingly partial denominator.")
    return missing


def parse_args(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--allow-partial", action="store_true",
                    help="publish even when rows are missing from one pass; "
                         "the loss is recorded as n_missing/missing_row_ids")
    return ap.parse_args(argv)


def main(argv=None):
    args = parse_args(argv)
    a = load_pass("component_passA.json")
    b = load_pass("component_passB.json")
    ids = sorted(set(a) & set(b))
    missing = check_denominator(a, b, args.allow_partial)
    if missing:
        print(f"WARN: {len(missing)} rows present in only one pass "
              f"(accepted via --allow-partial): {missing[:10]}")
    pairs0 = [(a[i], b[i]) for i in ids]
    pairs1 = [(L1_MAP[x], L1_MAP[y]) for x, y in pairs0]

    stats = {
        "instrument": "OBS-T component location axis (validation/gold_sample.csv, "
                      "csl-observatory pinned 259544be0e0f8f5b8dfa5e2804a3fc90c888d469)",
        "protocol": "Uprava docs/PROTOCOL_BLIND_LLM_SECOND_ANNOTATOR_RELIABILITY_2026.md",
        "preregistration_commit": "ddd1d0b4608d918d399634fdb87b1947a2996d36 (Uprava main, 21-07-2026)",
        "annotators": {
            "A": "Opus 4.8 (claude-opus-4-8), blind batches, 21-07-2026",
            "B": "Sonnet 5 (claude-sonnet-5), blind batches, 21-07-2026",
        },
        "L0_8label": kappa_block(pairs0, L0),
        "L1_4group": kappa_block(pairs1, L1),
        "bootstrap": {"resamples": N_BOOT, "seed": SEED},
        "n_missing": len(missing),
        "missing_row_ids": missing,
        "label_distribution": {"A": dict(Counter(a[i] for i in ids).most_common()),
                               "B": dict(Counter(b[i] for i in ids).most_common())},
    }

    per_label = {}
    for c in L0:
        cp = [(x, y) for x, y in pairs0 if x == c]
        per_label[c] = {"n_A": len(cp),
                        "B_agrees": round(sum(1 for x, y in cp if x == y) / len(cp), 3)
                        if cp else None}
    stats["per_label_A_base"] = per_label
    conf = {x: {y: 0 for y in L0} for x in L0}
    for x, y in pairs0:
        conf[x][y] += 1
    stats["confusion_A_rows_B_cols"] = conf

    sub_ids = [int(r["row_id"]) for r in json.loads(
        (HERE / "blind_batches" / "batch_01.json").read_text(encoding="utf-8"))]
    for ann, main_file in (("A", "component_passA.json"), ("B", "component_passB.json")):
        stats[f"flip_rate_{ann}"] = flip_rate(
            [main_file, f"flip_runs/pass{ann}_run2.json", f"flip_runs/pass{ann}_run3.json"],
            sub_ids)

    (HERE / "component_kappa_stats.json").write_text(
        json.dumps(stats, ensure_ascii=False, indent=1), encoding="utf-8")

    dis = [i for i in ids if a[i] != b[i]]
    csv.field_size_limit(10_000_000)
    with (HERE / "gold_sample.csv").open(encoding="utf-8", newline="") as fh:
        sheet = {int(r["row_id"]): r for r in csv.DictReader(fh)}
    with (HERE / "component_kappa_disagreements.csv").open(
            "w", encoding="utf-8", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["row_id", "passA_opus48", "passB_sonnet5", "source_layer",
                    "dict", "headword_iast", "old_iast", "new_iast", "comment_raw"])
        for i in dis:
            r = sheet[i]
            w.writerow([i, a[i], b[i], r["source_layer"], r["dict"],
                        r["headword_iast"], r["old_iast"], r["new_iast"],
                        r["comment_raw"]])

    print(f"n={len(pairs0)}  L0 kappa={stats['L0_8label']['kappa']} "
          f"CI={stats['L0_8label']['kappa_ci95']} agree={stats['L0_8label']['raw_agreement']}")
    print(f"          L1 kappa={stats['L1_4group']['kappa']} "
          f"CI={stats['L1_4group']['kappa_ci95']} agree={stats['L1_4group']['raw_agreement']}")
    print(f"flip A={stats['flip_rate_A']}  flip B={stats['flip_rate_B']}  "
          f"disagreements={len(dis)}")


if __name__ == "__main__":
    main()
