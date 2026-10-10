#!/usr/bin/env python3
"""E32 numeric canary — one command that re-derives every number the A73 paper quotes.

Cuts/verifies the frozen E32 correction-events release:
  1. verifies SHA256SUMS over the pinned upstream artifacts,
  2. recomputes every corpus statistic live from the committed
     correction_events_release.csv,
  3. asserts each recomputed/pinned number against expected.json (frozen at cut),
  4. reads the committed OBS-T rigor/baseline tables and the a61-sixdict matrix
     release for the cross-referenced numbers.

Usage:
  python3 e32_canary.py                 # verify (exit 0 = all PASS)
  python3 e32_canary.py --recompute     # print live numbers + rewrite expected.json

Every FAIL names the number; a digest mismatch fails loudly before anything else.
"""
import argparse
import csv
import hashlib
import json
import math
import sys
from collections import Counter
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent.parent  # data/publication/<this>/ -> repo root

CSV_PATH = REPO / "observatory/site/src/data/correction_events_release.csv"
META_PATH = REPO / "observatory/site/src/data/correction_events_release.meta.json"
SCHEMA_PATH = REPO / "data/schema/correction-event.schema.json"
RIGOR_PATH = REPO / "observatory/site/src/data/obs_t_rigor.json"
BASELINES_PATH = REPO / "observatory/site/src/data/obs_t_baselines.json"
MATRIX_PATH = REPO / "data/publication/a61-sixdict-sense-seq-matrix-2026-10-04/matrix.csv"
EXPECTED_PATH = HERE / "expected.json"
NWS_PIN_PATH = HERE / "nws_intersections_pinned.json"
SUMS_PATH = HERE / "SHA256SUMS"

DERIVED_COMPONENTS = ["sense", "markup", "headword", "citation", "meta", "grammar"]


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


PINNED_FILES = [
    "observatory/site/src/data/correction_events_release.csv",
    "observatory/site/src/data/correction_events_release.meta.json",
    "data/schema/correction-event.schema.json",
    "observatory/site/src/data/obs_t_rigor.json",
    "observatory/site/src/data/obs_t_baselines.json",
]


def write_sums():
    lines = [f"{sha256(REPO / rel)}  {rel}" for rel in PINNED_FILES]
    SUMS_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"SHA256SUMS written ({len(lines)} files)")


def check_digests(failures):
    for line in SUMS_PATH.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        digest, rel = line.split(maxsplit=1)
        rel = rel.strip()
        target = REPO / rel
        if not target.exists():
            failures.append(f"digest: missing file {rel}")
            continue
        actual = sha256(target)
        if actual != digest:
            failures.append(f"digest: {rel} changed since the cut ({actual[:12]}... != {digest[:12]}...)")


def recompute():
    rows = 0
    dicts = set()
    correctors = Counter()
    dates = []
    layer = Counter()
    evidence = Counter()
    split = Counter()
    comp_derived = Counter()
    etype = Counter()
    espace = Counter()
    lat = []
    loci = Counter()
    lcode_empty = 0
    years = Counter()
    with open(CSV_PATH, encoding="utf-8", newline="") as f:
        for r in csv.DictReader(f):
            rows += 1
            dicts.add(r["dict"])
            correctors[r["corrector"]] += 1
            if r["date"]:
                dates.append(r["date"])
                years[r["date"][:4]] += 1
            layer[r["source_layer"]] += 1
            evidence[r["evidence_level"]] += 1
            split[r["split"]] += 1
            if r["error_component"] in DERIVED_COMPONENTS:
                comp_derived[r["error_component"]] += 1
            etype[r["edit_type"]] += 1
            espace[r["edit_space"]] += 1
            if r["latency_days"]:
                try:
                    lat.append(int(float(r["latency_days"])))
                except ValueError:
                    pass
            if r["lcode"]:
                loci[(r["dict"], r["lcode"])] += 1
            else:
                lcode_empty += 1
    dates.sort()
    lat.sort()
    n = len(lat)
    total_derived = sum(comp_derived.values())
    ranked = correctors.most_common()
    multi = sum(1 for c in loci.values() if c >= 2)
    return {
        "rows": rows,
        "dicts": len(dicts),
        "correctors": len(correctors),
        "date_min": dates[0],
        "date_max": dates[-1],
        "layer": dict(layer),
        "evidence": dict(evidence),
        "derived_share": round(evidence["derived"] / rows, 3),
        "split": dict(split),
        "component_derived": {k: comp_derived[k] for k in DERIVED_COMPONENTS},
        "component_derived_share": {
            k: round(comp_derived[k] / total_derived, 3) for k in DERIVED_COMPONENTS
        },
        "edit_type_share": {k: round(v / rows, 3) for k, v in etype.most_common()},
        "edit_space": dict(espace),
        "latency_n": n,
        "latency_median": lat[n // 2],
        "latency_p90": lat[math.ceil(n * 0.9) - 1],
        "latency_max": lat[-1],
        "lcode_empty": lcode_empty,
        "loci_total": len(loci),
        "loci_multi": multi,
        "loci_multi_share": round(multi / len(loci), 3),
        "events_in_multi_loci_share": round(
            sum(c for c in loci.values() if c >= 2) / rows, 3
        ),
        "top1_corrector_share": round(ranked[0][1] / rows, 3),
        "top5_corrector_share": round(
            sum(c for _, c in ranked[:5]) / rows, 3
        ),
        "years": dict(sorted(years.items())),
    }


def read_pins():
    pins = {}
    # sixdict rho matrix
    with open(MATRIX_PATH, encoding="utf-8", newline="") as f:
        for r in csv.DictReader(f):
            key = f"rho_{r['pair_a'].lower()}_{r['pair_b'].lower()}"
            pins[key] = r["rho_median"]
            pins[key + "_n"] = r["n_pairs_ge3"]
    # schema + meta
    pins["schema_columns"] = str(len(json.load(open(SCHEMA_PATH))["properties"]))
    meta = json.load(open(META_PATH))
    pins["meta_record_count"] = str(meta["recordCount"])
    # OBS-T rigor table (committed)
    rigor = json.load(open(RIGOR_PATH))
    h2 = rigor["h2_cross_dictionary"]
    pins["chi2"] = str(h2["chi2"])
    pins["chi2_dof"] = str(h2["dof"])
    pins["cramers_v"] = str(h2["cramers_v"])
    me = rigor["h1_micro_edit"]["edit_distance"]
    pins["edit_distance_median"] = str(me["median"])
    pins["edit_distance_pct_le2"] = str(me["pct_le2"])
    pins["edit_distance_p90"] = str(me["p90"])
    rates = rigor["h1_micro_edit"]["minor_rate_by_location"]
    for loc in ("headword", "sense", "grammar"):
        pins[f"minor_rate_{loc}"] = str(rates[loc]["minor_rate"])
    # AED baselines (committed)
    base = json.load(open(BASELINES_PATH))
    pins["loccls_accuracy"] = str(base["location_classification"]["accuracy"])
    pins["loccls_macro_f1"] = str(base["location_classification"]["macro_f1"])
    pins["loccls_majority"] = str(base["location_classification"]["majority_baseline_accuracy"])
    pins["detection_pairwise"] = str(base["detection"]["pairwise_accuracy"])
    pins["correction_acc1"] = str(base["correction"]["accuracy_at_1"])
    # NWS pins (private base, frozen at the 04-10 run)
    nws = json.load(open(NWS_PIN_PATH))
    for k, v in nws["values"].items():
        pins[f"nws_{k}"] = str(v)
    return pins


def compare(expected, live, pins, failures, recompute_mode):
    if recompute_mode:
        out = {"corpus": live, "pins": pins}
        EXPECTED_PATH.write_text(
            json.dumps(out, ensure_ascii=False, indent=1, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        print(f"expected.json rewritten ({len(live)} corpus + {len(pins)} pinned numbers)")
        for name, val in live.items():
            if name != "years":
                print(f"  {name} = {val}")
        return

    def eq(name, got, want, fmt="{}"):
        got_n = json.dumps(got, sort_keys=True) if isinstance(got, dict) else str(got)
        want_n = json.dumps(want, sort_keys=True) if isinstance(want, dict) else str(want)
        if got_n != want_n:
            failures.append(f"{name}: got {got!r}, expected.json pins {want!r}")
        else:
            print(f"  PASS {name} = {fmt.format(got)}")

    for name, want in expected.get("corpus", {}).items():
        eq(f"corpus.{name}", live[name], want)
    for name, want in expected.get("pins", {}).items():
        eq(f"pin.{name}", pins[name], want)
    if not failures:
        print(f"ALL PASS — {len(expected['corpus'])} corpus + {len(expected['pins'])} pinned numbers verified against the frozen cut")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--recompute", action="store_true",
                    help="print live numbers and rewrite expected.json (a new cut)")
    ap.add_argument("--sums", action="store_true",
                    help="regenerate SHA256SUMS over the pinned upstream files")
    args = ap.parse_args()

    if args.sums:
        write_sums()
        return

    failures = []
    if SUMS_PATH.exists():
        check_digests(failures)
        if failures and not args.recompute:
            print("DIGEST FAILURES — the pinned upstream files changed since the cut:")
            for f in failures:
                print("  " + f)
            sys.exit(1)
        if not failures:
            print(f"digests OK ({sum(1 for l in SUMS_PATH.read_text().splitlines() if l.strip())} files)")
    elif not args.recompute:
        print("SHA256SUMS missing — run once with --sums before verifying")
        sys.exit(1)

    live = recompute()
    pins = read_pins()

    if args.recompute:
        compare(None, live, pins, failures, recompute_mode=True)
        sys.exit(0)

    expected = json.load(open(EXPECTED_PATH, encoding="utf-8"))
    compare(expected, live, pins, failures, recompute_mode=False)
    if failures:
        print(f"{len(failures)} FAILURES:")
        for f in failures:
            print("  FAIL " + f)
        sys.exit(1)


if __name__ == "__main__":
    main()
