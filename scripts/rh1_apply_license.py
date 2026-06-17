#!/usr/bin/env python3
"""Apply an approved RH1 license to org repositories.

RH1 license policy (approved by MG 2026-06-17, see
docs/REPOSITORY_HEALTH_DECISION_PACKET.md):
  - code/tooling repos     -> gpl-3.0
  - dictionary-data repos  -> cc-by-sa-4.0
  - mixed repos            -> dual split (handled separately)

Safety rules baked in:
  - NEVER overwrite an existing LICENSE file (skips the repo and reports it),
    so an intentional recognized license is never clobbered.
  - Commits a LICENSE file directly to the repo's default branch via the
    GitHub contents API, using the canonical license text GitHub itself ships
    (so GitHub's licensee auto-detects the SPDX id).
  - --dry-run shows exactly what would happen and mutates nothing.

Usage:
  python scripts/rh1_apply_license.py gpl-3.0 csl-doc avlinks --dry-run
  python scripts/rh1_apply_license.py gpl-3.0 csl-doc
  python scripts/rh1_apply_license.py cc-by-sa-4.0 ACC BEN --dry-run

Each repo arg may be "repo" (default branch auto-detected) or "repo:branch".
"""
import argparse
import base64
import json
import subprocess
import sys

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

OWNER = "sanskrit-lexicon"

# SPDX id GitHub should report once the canonical text is committed.
EXPECTED_SPDX = {
    "gpl-3.0": "GPL-3.0",
    "cc-by-sa-4.0": "CC-BY-SA-4.0",
    "cc-by-4.0": "CC-BY-4.0",
    "mit": "MIT",
}


def gh_json(args):
    r = subprocess.run(["gh", "api", *args], capture_output=True, encoding="utf-8")
    return r.returncode, r.stdout, r.stderr


def license_text(key):
    code, out, err = gh_json([f"licenses/{key}", "--jq", ".body"])
    if code != 0 or not out.strip():
        raise SystemExit(f"could not fetch license text for '{key}': {err.strip()}")
    return out


def default_branch(repo):
    code, out, _ = gh_json([f"repos/{OWNER}/{repo}", "--jq", ".default_branch"])
    return out.strip() if code == 0 else None


def existing_license(repo):
    """Return (has_license_file, spdx_id_or_None)."""
    code, _, _ = gh_json([f"repos/{OWNER}/{repo}/contents/LICENSE"])
    has_file = code == 0
    code2, spdx, _ = gh_json([f"repos/{OWNER}/{repo}", "--jq", ".license.spdx_id // \"\""])
    spdx = spdx.strip() or None
    if spdx in (None, "NOASSERTION"):
        # NOASSERTION still means a LICENSE-ish file exists that we must not clobber.
        pass
    return has_file, spdx


def put_license(repo, branch, text, message):
    body = json.dumps({
        "message": message,
        "content": base64.b64encode(text.encode("utf-8")).decode("ascii"),
        "branch": branch,
    })
    r = subprocess.run(
        ["gh", "api", "--method", "PUT",
         f"repos/{OWNER}/{repo}/contents/LICENSE", "--input", "-"],
        input=body, capture_output=True, encoding="utf-8",
    )
    if r.returncode != 0:
        return None, r.stderr.strip()[:300]
    sha = json.loads(r.stdout)["commit"]["sha"][:8]
    return sha, None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("license", choices=sorted(EXPECTED_SPDX), help="license key")
    ap.add_argument("repos", nargs="+", help="repo or repo:branch")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    text = license_text(args.license)
    msg = (f"Add {EXPECTED_SPDX[args.license]} license "
           f"(RH1 license policy, approved 2026-06-17)")
    print(f"License: {args.license} -> {EXPECTED_SPDX[args.license]} "
          f"({len(text)} bytes){'  [DRY-RUN]' if args.dry_run else ''}\n")

    applied, skipped, errored = [], [], []
    for spec in args.repos:
        repo, _, br = spec.partition(":")
        branch = br or default_branch(repo)
        if not branch:
            print(f"  {repo:18} ERROR: repo not found / no default branch")
            errored.append(repo)
            continue
        has_file, spdx = existing_license(repo)
        if has_file or (spdx and spdx != "NOASSERTION"):
            print(f"  {repo:18} SKIP: already has a license "
                  f"(file={has_file}, spdx={spdx}) — not overwriting")
            skipped.append(repo)
            continue
        if args.dry_run:
            print(f"  {repo:18} would add LICENSE on '{branch}'")
            applied.append(repo)
            continue
        sha, err = put_license(repo, branch, text, msg)
        if err:
            print(f"  {repo:18} ERROR on '{branch}': {err}")
            errored.append(repo)
        else:
            print(f"  {repo:18} OK  LICENSE committed on '{branch}' @ {sha}")
            applied.append(repo)

    print(f"\nSummary: {len(applied)} applied/would-apply, "
          f"{len(skipped)} skipped, {len(errored)} errored")
    if errored:
        sys.exit(1)


if __name__ == "__main__":
    main()
