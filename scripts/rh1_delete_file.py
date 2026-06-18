#!/usr/bin/env python3
"""Delete a file from an org repo via the GitHub contents API, tolerant of the
flaky network. Used to remove a superseded LICENSE.md after a canonical LICENSE
has been committed.

Retries transient failures; if the file is already gone, treats it as success
(so a timed-out DELETE can't error spuriously). A real 404 = already-deleted.

Usage:
  python scripts/rh1_delete_file.py LICENSE.md MWS Wil-YAT --dry-run
  python scripts/rh1_delete_file.py LICENSE.md MWS Wil-YAT
"""
import argparse
import json
import subprocess
import sys
import time

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

OWNER = "sanskrit-lexicon"


def gh(args, tries=5):
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


def file_meta(repo, path):
    code, out, _ = gh([f"repos/{OWNER}/{repo}/contents/{path}", "--jq", "{sha:.sha}"])
    if code != 0:
        return None  # 404 => already gone; transient handled by retries above
    return json.loads(out).get("sha")


def default_branch(repo):
    code, out, _ = gh([f"repos/{OWNER}/{repo}", "--jq", ".default_branch"])
    return out.strip() if code == 0 else None


def delete_file(repo, path, sha, branch, message, tries=4):
    body = json.dumps({"message": message, "sha": sha, "branch": branch})
    last = "unknown"
    for i in range(tries):
        r = subprocess.run(
            ["gh", "api", "--method", "DELETE",
             f"repos/{OWNER}/{repo}/contents/{path}", "--input", "-"],
            input=body, capture_output=True, encoding="utf-8",
        )
        if r.returncode == 0:
            return json.loads(r.stdout)["commit"]["sha"][:8], None
        last = (r.stderr or "").strip()[:200]
        time.sleep(3 * (i + 1))
        if file_meta(repo, path) is None:  # already gone -> the delete landed
            return "verified-gone", None
    return None, last


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("path", help="file path to delete, e.g. LICENSE.md")
    ap.add_argument("repos", nargs="+")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    msg = f"Remove superseded {args.path} (RH1: canonical LICENSE now present)"
    for repo in args.repos:
        branch = default_branch(repo)
        if not branch:
            print(f"  {repo:14} ERROR: could not resolve branch (404/network) — skipped")
            continue
        sha = file_meta(repo, args.path)
        if sha is None:
            print(f"  {repo:14} SKIP: {args.path} not present (nothing to delete)")
            continue
        if args.dry_run:
            print(f"  {repo:14} would delete {args.path} on '{branch}' (sha {sha[:8]})")
            continue
        out, err = delete_file(repo, args.path, sha, branch, msg)
        if err:
            print(f"  {repo:14} ERROR: {err}")
        else:
            print(f"  {repo:14} OK  {args.path} deleted on '{branch}' @ {out}")


if __name__ == "__main__":
    main()
