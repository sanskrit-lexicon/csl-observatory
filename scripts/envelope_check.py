#!/usr/bin/env python3
"""Verify one release envelope against the bytes it pins (V6 verification).

The envelope (data/manifest/envelopes/*.envelope.json, schema
release-envelope-v1) is the object dashboards and papers pin. This script is
the rerun side of that contract: it re-derives every digest the envelope
declares from the bytes actually on disk and reports PASS/FAIL/SKIP per
check. It never repairs, never rewrites, never trusts a recorded digest it
could not recompute. Reference implementation: kosha scripts/envelope_check.py
(Uprava docs/SPEC_RELEASE_ENVELOPE_V6_PORTFOLIO_2026.md).

Checks:
  CHK-1  envelope schema + required fields present
  CHK-2  each pinned_artifacts entry's sha256 recomputes from the file's bytes
         (lf-canonical or raw, per its own sha256_form)
  CHK-3  output_digests.datasets sha256/rows/size_bytes match a direct
         recompute of the pinned release CSV
  CHK-4  each source pin's blob (git show <pin_commit>:<source_path>)
         digests to the recorded sha256 (SKIP when the source repo's clone
         is absent on this box; this repo's own history always resolves)
  CHK-5  code_revision.commit exists in this repo and (when the envelope
         pins a tag) resolves to the same commit as that tag

Exit 0 when every run check passes (SKIP allowed); exit 1 on any FAIL.

Usage:
    python scripts/envelope_check.py --envelope data/manifest/envelopes/v1.13.3.envelope.json
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent

SCHEMA = "release-envelope-v1"
REQUIRED = (
    "schema",
    "envelope_id",
    "release_tag",
    "created",
    "code_revision",
    "pinned_artifacts",
    "source_pins",
    "output_digests",
    "config",
    "licence",
    "checks",
    "review",
    "citation",
    "publication_state",
)

csv.field_size_limit(10_000_000)


def sha256_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def canonical(b: bytes) -> bytes:
    """LF-canonical form — the same normalisation the release pipeline assumes."""
    return b.replace(b"\r\n", b"\n")


def digest_for(b: bytes, form: str) -> str:
    return sha256_bytes(canonical(b) if "lf-canonical" in form else b)


def git(repo: Path, *args, binary: bool = False):
    out = subprocess.run(["git", "-C", str(repo)] + list(args), capture_output=True)
    if out.returncode != 0:
        return None
    return out.stdout if binary else out.stdout.decode("utf-8", "replace").strip()


def report(results, fatal: str = None, extra=None) -> str:
    lines = []
    if fatal:
        lines.append("FATAL: " + fatal)
    for cid, res, detail in results:
        lines.append("  [{}] {} — {}".format(res.rjust(4), cid, detail))
    for e in extra or []:
        lines.append("         · " + e)
    passed = sum(1 for _, r, _ in results if r == "pass")
    skipped = sum(1 for _, r, _ in results if r == "SKIP")
    failed = sum(1 for _, r, _ in results if r == "FAIL")
    lines.append(
        "envelope_check: {} pass, {} skip, {} fail — {}".format(
            passed, skipped, failed, "PASS" if failed == 0 else "FAIL"
        )
    )
    return "\n".join(lines)


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--envelope", required=True)
    args = ap.parse_args()

    env_path = Path(args.envelope)
    if not env_path.is_absolute():
        env_path = REPO / env_path
    env = json.loads(canonical(env_path.read_bytes()))

    results = []

    def record(cid: str, ok: bool, detail: str, skipped: bool = False):
        results.append((cid, "SKIP" if skipped else ("pass" if ok else "FAIL"), detail))

    # CHK-1 schema + required fields
    missing = [k for k in REQUIRED if k not in env or env[k] in (None, "", [], {})]
    record(
        "CHK-1-schema",
        not missing,
        "schema={}".format(env.get("schema"))
        + ("" if not missing else "; missing/empty: {}".format(", ".join(missing))),
    )
    if env.get("schema") != SCHEMA:
        print(report(results, fatal="schema is {}, expected {}".format(env.get("schema"), SCHEMA)))
        return 1

    # CHK-2 pinned_artifacts digests
    pin_ok = True
    for p in env["pinned_artifacts"]:
        fp = REPO / p["path"]
        if not fp.is_file():
            record("CHK-2-pin:{}".format(p["path"]), False, "file not found")
            pin_ok = False
            continue
        dig = digest_for(fp.read_bytes(), p.get("sha256_form", ""))
        ok = dig == p["sha256"]
        record("CHK-2-pin:{}".format(p["path"]), ok, "{} ({})".format(dig[:16], p.get("sha256_form")))
        pin_ok = pin_ok and ok
    record("CHK-2-pinned-artifacts", pin_ok, "{} artifact(s)".format(len(env["pinned_artifacts"])))

    # CHK-3 output_digests.datasets parity against a direct recompute
    declared = env["output_digests"]["datasets"]
    drift = []
    for ds_id, out in sorted(declared.items()):
        asset_name = out["release_asset"]
        match = next(
            (p for p in env["pinned_artifacts"] if Path(p["path"]).name == asset_name),
            None,
        )
        if match is None:
            drift.append("{}: release_asset {} not among pinned_artifacts".format(ds_id, asset_name))
            continue
        fp = REPO / match["path"]
        b = fp.read_bytes()
        dig = digest_for(b, out.get("sha256_form", match.get("sha256_form", "lf-canonical")))
        if dig != out["sha256"]:
            drift.append("{}: sha256 {} != declared {}".format(ds_id, dig[:16], out["sha256"][:16]))
        if out.get("size_bytes") != len(b):
            drift.append("{}: size_bytes {} != actual {}".format(ds_id, out.get("size_bytes"), len(b)))
        if asset_name.endswith(".csv") and "rows" in out:
            with fp.open(encoding="utf-8", newline="") as f:
                n = sum(1 for _ in csv.reader(f)) - 1
            if n != out["rows"]:
                drift.append("{}: rows {} != actual {}".format(ds_id, out["rows"], n))
    record("CHK-3-output-parity", not drift, "{} dataset(s)".format(len(declared)))
    if drift:
        print(report(results, extra=drift))

    # CHK-4 source pins re-derived
    tag_ok = True
    pin_drift = []
    repo_url = env["code_revision"]["repo_url"].rstrip("/")
    for sp in env["source_pins"]:
        ds_id = sp["dataset"]
        source_repo = sp["source_repo"].rstrip("/")
        if source_repo == repo_url:
            repo = REPO
        else:
            guess = REPO.parent / source_repo.rsplit("/", 1)[-1]
            repo = guess if guess.is_dir() else None
        if repo is None:
            record("CHK-4-source-pin:{}".format(ds_id), True, "sibling clone absent on this box", skipped=True)
            continue
        rev = git(Path(repo), "cat-file", "-t", sp["pin_commit"])
        if rev != "commit":
            pin_drift.append("{}: pin_commit {} not a commit in {}".format(ds_id, sp["pin_commit"][:12], repo))
            record("CHK-4-source-pin:{}".format(ds_id), False, "pin_commit not found")
            tag_ok = False
            continue
        blob = git(Path(repo), "show", "{}:{}".format(sp["pin_commit"], sp["source_path"]), binary=True)
        if blob is None:
            pin_drift.append("{}: blob unresolvable at pin".format(ds_id))
            record("CHK-4-source-pin:{}".format(ds_id), False, "blob unresolvable")
            tag_ok = False
            continue
        if blob.startswith(b"version https://git-lfs.github.com/spec/v1"):
            # The committed blob is an LFS pointer, not the real content — the
            # pointer's own `oid sha256:...` line IS the content digest.
            oid_line = next((l for l in blob.split(b"\n") if l.startswith(b"oid sha256:")), b"")
            dig = oid_line.decode("ascii", "replace").split(":", 1)[-1].strip()
        else:
            dig = digest_for(blob, sp.get("sha256_form", "lf-canonical"))
        ok = dig == sp["sha256"]
        record(
            "CHK-4-source-pin:{}".format(ds_id),
            ok,
            "pin {} digests {} (match: {})".format(sp["pin_commit"][:12], dig[:16], ok),
        )
        tag_ok = tag_ok and ok
    record("CHK-4-source-pins", tag_ok and not pin_drift, "summary")

    # CHK-5 code_revision.commit exists and matches the pinned tag
    rev = git(REPO, "cat-file", "-t", env["code_revision"]["commit"])
    commit_ok = rev == "commit"
    tag = env["code_revision"].get("tag")
    tag_detail = ""
    if commit_ok and tag:
        tag_commit = git(REPO, "rev-list", "-n1", tag)
        tag_match = tag_commit == env["code_revision"]["commit"]
        commit_ok = commit_ok and tag_match
        tag_detail = " tag {} -> {} (match: {})".format(tag, (tag_commit or "?")[:12], tag_match)
    record(
        "CHK-5-code-revision",
        commit_ok,
        "{} ({}){}".format(env["code_revision"]["commit"][:12], rev, tag_detail),
    )

    print(report(results))
    return 0 if all(r != "FAIL" for _, r, _ in results) else 1


if __name__ == "__main__":
    sys.exit(main())
