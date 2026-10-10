#!/usr/bin/env python3
"""nws_halle_intersections.py — reproducible evidence script for the NWS (Halle)
× Cologne-dictionaries intersection table (H5932 baseline, ported per H5939).

Reproduces, from raw inputs only, the table pinned in
Uprava/papers/A61_wsc/NWS_HALLE_ANALYSIS_2026-10-04.md:

    NWS ∩ PWG                                  20 268   12.1%
    NWS ∩ PW                                   26 508   15.8%
    NWS ∩ MW                                   23 144   13.8%
    NWS outside PWG∪PW∪MW                     140 316   83.5%
    NWS outside PWG∪PW∪MW∪SCH∪ACC∪PWKVN      138 976   82.7%

Inputs (both required at their defaults, sibling checkouts of this repo):
  --nws-tar   pwg-ru-data/layers/nws.tar.gz  (167,991 lemma JSON, sha256 054b05da…)
  --csl-orig  csl-orig @ f4c08c5             (k1 sets from the six dictionary txt)

METHOD (session-exact, H5932 04-10-2026):
  - NWS keys are the tar member FILENAME STEMS (`nws/<stem>.json` -> `<stem>`,
    leading '-' stripped); NOT the JSON `key1` field. A key1-based comparison
    yields far higher overlaps (~90% vs 12-16%) and is NOT the pinned baseline —
    keep the two vintages apart when citing.
  - dictionary keys are the `<k1>` values on `<L>`-lines of
    csl-orig/v02/<dict>/<dict>.txt, whitespace-stripped, leading '-' stripped.
  - H5938 (fuzzy normalization pass) supersedes this exact-match baseline for
    refinement; `--json` emits machine-readable results so the fuzzy delta can
    be diffed against it.

  python scripts/nws_halle_intersections.py [--selftest] [--json]
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
import tarfile
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

REPO = Path(__file__).resolve().parent.parent


def _github_roots() -> list[Path]:
    """Candidate roots holding the sibling checkouts (main clone or worktree)."""
    roots = [REPO.parent, REPO.parent.parent, Path.home() / "Documents" / "GitHub"]
    seen, out = set(), []
    for r in roots:
        if r not in seen and r.is_dir():
            seen.add(r)
            out.append(r)
    return out


def _default_sibling(rel: str) -> Path:
    for root in _github_roots():
        p = root / rel
        if p.exists():
            return p
    return _github_roots()[0] / rel


DEF_TAR = _default_sibling("pwg-ru-data/layers/nws.tar.gz")
DEF_CSL_ORIG = _default_sibling("csl-orig")
DEFAULT_DICTS = ["pwg", "pw", "mw", "sch", "acc", "pwkvn"]
HEAD_DICTS = ["pwg", "pw", "mw"]  # per-dict rows in the printed table

TAR_SHA256 = "054b05da96df2f1af2c95c02b7e15d87f8a616d4eaa339f93e3ed7430e07f00c"
CSL_ORIG_PIN = "f4c08c5"  # revision used by the H5932 measurement

# Pinned H5932 numbers (04-10-2026) — checked by --selftest.
PINNED = {
    "nws_lemmas": 167991,
    "n_pwg": 20268,
    "n_pw": 26508,
    "n_mw": 23144,
    "union3": 219778,
    "absent3": 140316,
    "union_sch": 228933,
    "absent_sch": 138977,
    "union_acc": 243137,
    "absent_acc": 138977,
    "union_pwkv": 243157,
    "absent_pwkvn": 138976,
}

K1_RE = re.compile(r"<k1>([^<\n]*)")


def nws_keys(tar_path: Path) -> set[str]:
    """NWS key set = tar member filename stems (session-exact H5932 method)."""
    keys: set[str] = set()
    with tarfile.open(tar_path, "r:gz") as tf:
        for m in tf.getmembers():
            if not m.isfile():
                continue
            base = m.name.rsplit("/", 1)[-1]
            if base.startswith(".") or "/." in m.name or not base.endswith(".json"):
                continue
            keys.add(base[:-5].lstrip("-"))
    return keys


def dict_k1_keys(csl_orig: Path, dict_code: str) -> set[str]:
    """k1 set of one Cologne dictionary (values on <L> lines, H5932 method)."""
    txt = csl_orig / "v02" / dict_code / f"{dict_code}.txt"
    out: set[str] = set()
    with open(txt, encoding="utf-8", errors="replace") as f:
        for line in f:
            if not line.startswith("<L>"):
                continue
            m = K1_RE.search(line)
            if m and m.group(1).strip():
                out.add(m.group(1).strip().lstrip("-"))
    return out


def sha256_of(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def csl_orig_head(csl_orig: Path) -> str:
    try:
        return subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            cwd=csl_orig, capture_output=True, text=True, check=True,
        ).stdout.strip()
    except Exception:
        return "(not a git checkout)"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--nws-tar", type=Path, default=DEF_TAR)
    ap.add_argument("--csl-orig", type=Path, default=DEF_CSL_ORIG)
    ap.add_argument("--dicts", default=",".join(DEFAULT_DICTS))
    ap.add_argument("--selftest", action="store_true",
                    help="fail (exit 1) unless every pinned H5932 number reproduces")
    ap.add_argument("--json", action="store_true", help="machine-readable output")
    args = ap.parse_args()

    if not args.nws_tar.is_file():
        sys.exit(f"FAIL: NWS tar not found: {args.nws_tar}")
    if not (args.csl_orig / "v02").is_dir():
        sys.exit(f"FAIL: csl-orig checkout not found: {args.csl_orig}")

    dicts = [d.strip() for d in args.dicts.split(",") if d.strip()]
    tar_sha = sha256_of(args.nws_tar)
    head = csl_orig_head(args.csl_orig)

    nws = nws_keys(args.nws_tar)
    K = {d: dict_k1_keys(args.csl_orig, d) for d in dicts}

    res: dict = {
        "method": "H5932 session-exact: NWS keys = tar filename stems; dict keys = <L>-line <k1>",
        "nws_tar": str(args.nws_tar),
        "nws_tar_sha256": tar_sha,
        "csl_orig_head": head,
        "csl_orig_pin": CSL_ORIG_PIN,
        "nws_lemmas": len(nws),
        "dict_sizes": {d: len(K[d]) for d in dicts},
        "intersections": {d: len(nws & K[d]) for d in HEAD_DICTS if d in K},
    }
    base3 = set()
    for d in HEAD_DICTS:
        if d in K:
            base3 |= K[d]
    ladder = [{"added": "pwg∪pw∪mw", "union": len(base3), "absent": len(nws - base3)}]
    union = set(base3)
    for d in [x for x in dicts if x not in HEAD_DICTS]:
        union |= K[d]
        ladder.append({"added": d, "union": len(union), "absent": len(nws - union)})
    res["ladder"] = ladder

    if not args.json:
        print(f"NWS tar        : {args.nws_tar}")
        print(f"tar sha256     : {tar_sha}")
        print(f"csl-orig HEAD  : {head} (pin {CSL_ORIG_PIN})")
        print(f"NWS lemmas     : {len(nws)}")
        print()
        N = len(nws)
        for d in HEAD_DICTS:
            n = len(nws & K[d])
            print(f"NWS ∩ {d.upper():<4}: {n:>7,}  ({n / N * 100:.1f}% of NWS)")
        print()
        for row in ladder:
            print(f"∪{row['added']:<6}: union={row['union']:>7,}  absent={row['absent']:>7,}"
                  f"  ({row['absent'] / N * 100:.1f}%)")

    if args.json:
        print(json.dumps(res, ensure_ascii=False, indent=1))

    if args.selftest:
        bad = []
        if res["nws_lemmas"] != PINNED["nws_lemmas"]:
            bad.append(f"nws_lemmas {res['nws_lemmas']} != {PINNED['nws_lemmas']}")
        for d in HEAD_DICTS:
            got = res["intersections"].get(d)
            want = PINNED[f"n_{d}"]
            if got != want:
                bad.append(f"n_{d} {got} != {want}")
        for row, (ukey, akey) in zip(ladder, [
                ("union3", "absent3"), ("union_sch", "absent_sch"),
                ("union_acc", "absent_acc"), ("union_pwkv", "absent_pwkvn")]):
            if row["union"] != PINNED[ukey]:
                bad.append(f"{ukey} {row['union']} != {PINNED[ukey]}")
            if row["absent"] != PINNED[akey]:
                bad.append(f"{akey} {row['absent']} != {PINNED[akey]}")
        if tar_sha != TAR_SHA256:
            bad.append(f"tar sha256 drifted: {tar_sha}")
        if bad:
            print("SELFTEST FAIL: " + "; ".join(bad), file=sys.stderr)
            return 1
        print("SELFTEST PASS: all pinned H5932 numbers reproduce exactly.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
