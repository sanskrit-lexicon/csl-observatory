#!/usr/bin/env python3
"""
check_coverage.py — guard against the automated refresh silently dropping a
large repository's commit history.

The dashboard pipeline is fetch.py (REST) -> transform.py, reading the JSONL
snapshots under observatory/snapshots/YYYY-MM/. The REST commits API is
normally complete (the committed data has csl-orig, cologne-stardict, etc.),
but a transient failure -- a timeout or 5xx mid-pagination -- makes
fetch.py break out of fetch_repo_commits_since() with a partial or empty
commits file for that repo. transform.py would then rebuild the dashboard
CSVs with that repo's history missing and ship the undercount with no error.

This guard runs after fetch.py and fails the run instead, so the last-good
committed data stays live and a maintainer is alerted. It uses the same
"sized but empty" heuristic that retry_via_clone.autodetect_failed() uses
for the legacy GraphQL path, but reads fetch.py's JSONL snapshots.

Only repos at or above --min-size-kb are treated as hard failures (a large
repo returning zero commits is an unambiguous regression); smaller empty
repos are reported as warnings, never failing the build.

Exit codes: 0 = ok (or only sub-threshold gaps, warned), 1 = a large repo
came back empty or an attempted repo is missing, 2 = no snapshot to check.

Usage:
    python observatory/check_coverage.py                 # current month
    python observatory/check_coverage.py --snapshot 2026-06
    python observatory/check_coverage.py --min-size-kb 1000
"""
import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

REPO_ROOT = Path(__file__).resolve().parent  # observatory/
SNAP_BASE = REPO_ROOT / "snapshots"
SKIP = {"csl-observatory"}
DEFAULT_MIN_SIZE_KB = 1000  # 1 MB — only large repos are unambiguous regressions


def count_commits(commits_dir, repo):
    """Return number of commit lines for a repo, or None if no snapshot file."""
    f = commits_dir / f"{repo}.jsonl"
    if not f.exists():
        return None
    with open(f, encoding="utf-8") as fh:
        return sum(1 for line in fh if line.strip())


def load_manifest(snap):
    path = snap / "manifest.json"
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        print(f"::warning::commit-coverage: invalid snapshot manifest at {path}")
        return {}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--snapshot", default=datetime.now(timezone.utc).strftime("%Y-%m"),
                    help="Snapshot month dir under observatory/snapshots/ (default: current YYYY-MM)")
    ap.add_argument("--min-size-kb", type=int, default=DEFAULT_MIN_SIZE_KB,
                    help="Repos this size or larger with zero commits fail the build (default: 1000)")
    args = ap.parse_args()

    snap = SNAP_BASE / args.snapshot
    meta_dir = snap / "metadata"
    commits_dir = snap / "commits"
    if not meta_dir.exists():
        print(f"ERROR: no metadata snapshot at {meta_dir}", file=sys.stderr)
        return 2

    manifest = load_manifest(snap)
    attempted = manifest.get("repo_names_attempted") or []
    if attempted and not isinstance(attempted, list):
        attempted = []
    recorded_failed = manifest.get("repo_failures") or manifest.get("repos_failed") or []
    if recorded_failed:
        print("::error::commit-coverage: fetch manifest records failed repo(s); "
              "refusing to transform a partial snapshot.")
        for item in recorded_failed:
            if isinstance(item, dict):
                print(f"  - {item.get('repo')}: {item.get('reason', 'unknown')}")
            else:
                print(f"  - {item}")
        return 1

    failures, warnings = [], []
    metadata_repos = set()
    for meta_file in sorted(meta_dir.glob("*.jsonl")):
        lines = meta_file.read_text(encoding="utf-8").splitlines()
        if not lines:
            continue
        try:
            meta = json.loads(lines[0])
        except json.JSONDecodeError:
            continue
        repo = meta.get("name") or meta_file.stem
        metadata_repos.add(repo)
        if repo in SKIP or meta.get("archived"):
            continue
        size_kb = meta.get("size") or 0  # GitHub reports repo size in KB
        n = count_commits(commits_dir, repo)
        if size_kb > 0 and n in (None, 0):
            captured = "no commits file" if n is None else "0 commits"
            entry = f"{repo} (size {size_kb:,} KB, {captured})"
            (failures if size_kb >= args.min_size_kb else warnings).append(entry)

    missing_metadata = sorted(repo for repo in attempted if repo not in metadata_repos)
    if missing_metadata:
        print("::error::commit-coverage: attempted repo(s) are missing metadata "
              "and would disappear from repos.csv.")
        for repo in missing_metadata:
            print(f"  - {repo}")
        return 1

    for w in warnings:
        print(f"::warning::commit-coverage: small repo returned no commits — {w}")

    if failures:
        print(f"::error::commit-coverage: {len(failures)} sized repo(s) returned ZERO commits "
              "(likely a transient fetch failure). Refusing to ship undercounted data.")
        for fl in failures:
            print(f"  - {fl}")
        print("\nRecover, then re-run transform.py:")
        print("  python observatory/fetch.py --repos <repo>   # retry the REST fetch for that repo")
        print("  (legacy GraphQL path only: scripts/retry_via_clone.py <repo> — writes data/commits.json)")
        return 1

    print("commit-coverage OK: every sized repo captured at least one commit.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
