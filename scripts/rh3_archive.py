#!/usr/bin/env python3
"""Archive RH3-approved repositories on GitHub (sets archived=true, making the
repo read-only — reversible via unarchive). Network-resilient; refuses to
archive a repo that still has OPEN ISSUES unless --allow-open is given, so the
issue-migration gate can't be skipped by accident.

Usage:
  python scripts/rh3_archive.py santamlegacy temp_corrections_ae --dry-run
  python scripts/rh3_archive.py santamlegacy temp_corrections_ae
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
            return 0, r.stdout
        last = (r.stderr or "").strip()
        if "Not Found" in last or '"status":"404"' in last:
            return 1, "404"
        time.sleep(2 * (i + 1))
    return 2, f"TRANSIENT:{last[:120]}"


def state(repo):
    code, out = gh([f"repos/{OWNER}/{repo}",
                    "--jq", "{arch:.archived, open:.open_issues_count}"])
    if code != 0:
        return None
    return json.loads(out)


def archive(repo, tries=4):
    last = "unknown"
    for i in range(tries):
        r = subprocess.run(
            ["gh", "api", "--method", "PATCH", f"repos/{OWNER}/{repo}",
             "-F", "archived=true"], capture_output=True, encoding="utf-8")
        if r.returncode == 0:
            return True, None
        last = (r.stderr or "").strip()[:160]
        time.sleep(3 * (i + 1))
        st = state(repo)
        if st and st["arch"]:           # a timed-out PATCH may still have landed
            return True, None
    return False, last


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("repos", nargs="+")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--allow-open", action="store_true",
                    help="archive even if the repo still has open issues")
    args = ap.parse_args()

    for repo in args.repos:
        st = state(repo)
        if st is None:
            print(f"  {repo:24} ERROR: not found / persistent network failure — skipped")
            continue
        if st["arch"]:
            print(f"  {repo:24} SKIP: already archived")
            continue
        if st["open"] and not args.allow_open:
            print(f"  {repo:24} BLOCKED: {st['open']} open issue(s) — migrate/close "
                  f"first (or pass --allow-open). NOT archived.")
            continue
        if args.dry_run:
            print(f"  {repo:24} would archive (open issues: {st['open']})")
            continue
        ok, err = archive(repo)
        if ok:
            vs = state(repo)
            tag = "verified" if (vs and vs["arch"]) else "PATCH ok (verify pending)"
            print(f"  {repo:24} ARCHIVED ({tag})")
        else:
            print(f"  {repo:24} ERROR: {err}")


if __name__ == "__main__":
    main()
