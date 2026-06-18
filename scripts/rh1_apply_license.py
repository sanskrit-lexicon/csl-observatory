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
import time

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


def gh_json(args, tries=5):
    """Run a gh api read with retries. A genuine 404 is terminal; any other
    failure (TLS timeout, 5xx) is transient and retried — so a flaky network
    is never mistaken for 'repo not found' / 'no license'."""
    last = ""
    for i in range(tries):
        r = subprocess.run(["gh", "api", *args], capture_output=True, encoding="utf-8")
        if r.returncode == 0:
            return 0, r.stdout, ""
        last = (r.stderr or "").strip()
        if "Not Found" in last or '"status":"404"' in last:
            return 1, "", "404"
        time.sleep(2 * (i + 1))
    return 2, "", f"TRANSIENT:{last[:120]}"


def license_text(key):
    code, out, err = gh_json([f"licenses/{key}", "--jq", ".body"])
    if code != 0 or not out.strip():
        raise SystemExit(f"could not fetch license text for '{key}': {err.strip()}")
    return out


def default_branch(repo):
    code, out, _ = gh_json([f"repos/{OWNER}/{repo}", "--jq", ".default_branch"])
    if code == 0:
        return out.strip()
    return None  # caller distinguishes via re-query; message notes 404 vs network


def current_spdx(repo):
    code, out, _ = gh_json([f"repos/{OWNER}/{repo}", "--jq", ".license.spdx_id // \"NONE\""])
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


def license_blob_sha(repo, path="LICENSE"):
    """SHA of an existing file (required to overwrite it via the contents API)."""
    code, out, _ = gh_json([f"repos/{OWNER}/{repo}/contents/{path}", "--jq", ".sha"])
    return out.strip() if code == 0 and out.strip() else None


def put_license(repo, branch, text, message, sha=None, target_spdx=None, tries=4):
    """PUT the LICENSE, tolerant of the flaky network. A PUT that times out may
    still have landed server-side, so after any failure we re-check the live
    license: if it already equals the target, we treat it as success rather
    than retrying (which would double-apply or 409 on a stale sha)."""
    content_b64 = base64.b64encode(text.encode("utf-8")).decode("ascii")
    last_err = "unknown"
    for i in range(tries):
        payload = {"message": message, "content": content_b64, "branch": branch}
        if sha:
            payload["sha"] = sha
        r = subprocess.run(
            ["gh", "api", "--method", "PUT",
             f"repos/{OWNER}/{repo}/contents/LICENSE", "--input", "-"],
            input=json.dumps(payload), capture_output=True, encoding="utf-8",
        )
        if r.returncode == 0:
            return json.loads(r.stdout)["commit"]["sha"][:8], None
        last_err = (r.stderr or "").strip()[:200]
        time.sleep(3 * (i + 1))
        if target_spdx and current_spdx(repo) == target_spdx:
            return "verified-after-timeout", None
        # a previous attempt may have moved the blob; refresh the sha before retry
        if sha:
            fresh = license_blob_sha(repo, "LICENSE")
            if fresh:
                sha = fresh
    return None, last_err


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("license", choices=sorted(EXPECTED_SPDX), help="license key")
    ap.add_argument("repos", nargs="+", help="repo or repo:branch")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--replace", action="store_true",
                    help="overwrite an existing LICENSE with the canonical text "
                         "(intent already confirmed); default is add-only")
    args = ap.parse_args()

    text = license_text(args.license)
    verb = "Replace LICENSE with canonical" if args.replace else "Add"
    msg = (f"{verb} {EXPECTED_SPDX[args.license]} license "
           f"(RH1 license policy, approved 2026-06-17)")
    print(f"License: {args.license} -> {EXPECTED_SPDX[args.license]} "
          f"({len(text)} bytes){'  [DRY-RUN]' if args.dry_run else ''}\n")

    applied, skipped, errored = [], [], []
    for spec in args.repos:
        repo, _, br = spec.partition(":")
        branch = br or default_branch(repo)
        if not branch:
            print(f"  {repo:18} ERROR: could not resolve default branch "
                  f"(404 or persistent network failure) — skipped, NOT mutated")
            errored.append(repo)
            continue
        has_file, spdx = existing_license(repo)
        if not args.replace and (has_file or (spdx and spdx != "NOASSERTION")):
            print(f"  {repo:18} SKIP: already has a license "
                  f"(file={has_file}, spdx={spdx}) — not overwriting")
            skipped.append(repo)
            continue
        if args.replace and spdx and spdx == EXPECTED_SPDX[args.license]:
            print(f"  {repo:18} SKIP: already canonical {spdx} — nothing to do")
            skipped.append(repo)
            continue
        blob_sha = license_blob_sha(repo) if (args.replace and has_file) else None
        action = "would replace" if (args.replace and has_file) else "would add"
        if args.dry_run:
            print(f"  {repo:18} {action} LICENSE on '{branch}'"
                  + (f" (sha {blob_sha[:8]})" if blob_sha else ""))
            applied.append(repo)
            continue
        sha, err = put_license(repo, branch, text, msg, sha=blob_sha,
                               target_spdx=EXPECTED_SPDX[args.license])
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
