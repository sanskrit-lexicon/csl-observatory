#!/usr/bin/env python3
"""
csl-observatory Phase 1 — historical data fetcher.

Fetches:
  - All issues (state=all, all pages) per repo
  - All pull requests
  - All commits (since 2014)
  - Repo metadata (size, language, contributors)

Stores as JSONL under observatory/snapshots/YYYY-MM/<topic>/<repo>.jsonl.
Append-only, idempotent, resumable. Uses gh CLI for auth.

Usage:
  python fetch.py                    # full backfill, all repos
  python fetch.py --repos PWG,MWS    # specific repos
  python fetch.py --since 2024-01-01 # incremental
"""

import subprocess
import json
import sys
import argparse
import time
from pathlib import Path
from datetime import datetime, timezone

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

ORG = "sanskrit-lexicon"

# Configured observatory repo inventory.
DICTIONARY_REPOS = [
    "PWG", "PWK", "MWS", "MD", "AP", "AP90", "GRA", "FRI",
    "SCH", "DCS", "VCP", "ApteES", "SKD", "MCI", "CORRECTIONS", "WIL",
    "BHS", "VEI", "ACC", "KRM", "BUR", "CAE", "CCS", "STC", "BEN",
    "BOR", "INM", "BOP", "LRV", "AMAR", "SHS", "KNA", "KOW", "PUI",
    "csl-observatory"  # was processed as dict initially
]

TOOLING_REPOS = [
    "COLOGNE", "GreekInSanskrit", "hwnorm1", "alternateheadwords",
    "cologne-stardict", "rvlinks", "MWinflect", "csl-doc", "csl-apidev",
    "csl-homepage", "csl-websanlexicon", "csl-pywork", "csl-orig",
    "csl-westergaard", "csl-kale", "csl-inflect", "csl-corrections",
    "hwnorm2", "avlinks", "csl-devanagari", "csl-newsletter", "csl-lnum",
    "csl-ldev", "literarysource", "mw-dev", "csl-app", "csl-lslink",
    # archives + meta
    "ArabicInSanskrit", "Wil-YAT", "MW72", "csl-json", "csl-sqlite",
    "csl-whitroot", "cologne-hugo", "sanskrit-fonts",
    "sanskrit-lexicon.github.io", "santamlegacy",
    "temp_corrections_ae", "temp_corrections_ap90", "temp_corrections_acc",
    "temp_corrections_mw", "test_cologne_push"
]

ALL_REPOS = DICTIONARY_REPOS + TOOLING_REPOS

REPO_ROOT = Path(__file__).parent
SNAPSHOT_DATE = datetime.now(timezone.utc).strftime("%Y-%m")
SNAPSHOT_DIR = REPO_ROOT / "snapshots" / SNAPSHOT_DATE
LOG_FILE = REPO_ROOT / "snapshots" / f"fetch_{SNAPSHOT_DATE}.log"

# Ensure dirs exist (gitignored on CI, so first run creates them)
SNAPSHOT_DIR.mkdir(parents=True, exist_ok=True)
LOG_FILE.parent.mkdir(parents=True, exist_ok=True)

def log(msg):
    line = f"[{datetime.now(timezone.utc).strftime('%H:%M:%S')}] {msg}"
    print(line, flush=True)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(line + "\n")

def gh(*args, timeout=120):
    """Run gh with arg list (no shell). Returns stdout, success."""
    try:
        result = subprocess.run(
            ["gh"] + list(args),
            capture_output=True, text=True, timeout=timeout, encoding='utf-8'
        )
        return result.stdout.strip(), result.returncode == 0, result.stderr
    except subprocess.TimeoutExpired:
        return "", False, "TIMEOUT"
    except Exception as e:
        return "", False, str(e)

def fetch_paginated(endpoint, repo, jq_filter=None):
    """Fetch a paginated endpoint, return (all items, success)."""
    items = []
    page = 1
    while True:
        url = f"repos/{ORG}/{repo}/{endpoint}?per_page=100&page={page}&state=all"
        if "issues" in endpoint or "pulls" in endpoint:
            url += "&direction=asc"
        out, ok, err = gh("api", url)
        if not ok:
            if "403" in err and "rate limit" in err.lower():
                log(f"  RATE LIMIT — sleeping 60s")
                time.sleep(60)
                continue
            log(f"  ERROR fetching {endpoint} page {page}: {err[:100]}")
            return items, False
        try:
            page_items = json.loads(out)
            if not isinstance(page_items, list) or len(page_items) == 0:
                break
            items.extend(page_items)
            if len(page_items) < 100:
                break
            page += 1
        except json.JSONDecodeError as e:
            log(f"  JSON error on page {page}: {e}")
            return items, False
    return items, True

def save_jsonl(topic, repo, items):
    """Save items as JSONL to snapshots/YYYY-MM/<topic>/<repo>.jsonl."""
    target_dir = SNAPSHOT_DIR / topic
    target_dir.mkdir(parents=True, exist_ok=True)
    target_file = target_dir / f"{repo}.jsonl"
    with open(target_file, "w", encoding="utf-8") as f:
        for item in items:
            f.write(json.dumps(item, ensure_ascii=False) + "\n")
    return target_file

def fetch_repo_metadata(repo):
    """Fetch repo metadata: size, language, default branch, dates."""
    out, ok, _ = gh("api", f"repos/{ORG}/{repo}",
                     "--jq", "{name, full_name, description, language, size, "
                     "created_at, updated_at, pushed_at, default_branch, "
                     "stargazers_count, forks_count, open_issues_count, "
                     "has_issues, archived, disabled, license: (.license.spdx_id // null)}")
    if ok and out:
        try:
            return json.loads(out)
        except json.JSONDecodeError as e:
            print(f"warning: {repo}: repo meta jq output is not JSON: {e}",
                  file=sys.stderr)
    return None


def fetch_repo_languages(repo):
    """Fetch language byte counts."""
    out, ok, _ = gh("api", f"repos/{ORG}/{repo}/languages")
    if ok and out:
        try:
            return json.loads(out)
        except json.JSONDecodeError as e:
            print(f"warning: {repo}: languages jq output is not JSON: {e}",
                  file=sys.stderr)
    return {}


def fetch_repo_contributors(repo):
    """Fetch contributors."""
    out, ok, _ = gh("api", f"repos/{ORG}/{repo}/contributors?per_page=100",
                     "--jq", "[.[] | {login, contributions, type}]")
    if ok and out:
        try:
            data = json.loads(out)
            return data if isinstance(data, list) else []
        except json.JSONDecodeError as e:
            print(f"warning: {repo}: contributors jq output is not JSON: {e}",
                  file=sys.stderr)
    return []


def fetch_repo_releases(repo):
    """Fetch releases / tags."""
    out, ok, _ = gh("api", f"repos/{ORG}/{repo}/releases?per_page=100",
                     "--jq", "[.[] | {tag_name, name, published_at, draft, prerelease}]")
    if ok and out:
        try:
            data = json.loads(out)
            return data if isinstance(data, list) else []
        except json.JSONDecodeError as e:
            print(f"warning: {repo}: releases jq output is not JSON: {e}",
                  file=sys.stderr)
    return []

def slim_issue(issue):
    """Strip an issue down to fields we need."""
    return {
        "number": issue.get("number"),
        "title": issue.get("title"),
        "state": issue.get("state"),
        "created_at": issue.get("created_at"),
        "updated_at": issue.get("updated_at"),
        "closed_at": issue.get("closed_at"),
        "user": (issue.get("user") or {}).get("login"),
        "assignees": [a.get("login") for a in (issue.get("assignees") or [])],
        "labels": [l.get("name") for l in (issue.get("labels") or [])],
        "milestone": (issue.get("milestone") or {}).get("title"),
        "comments": issue.get("comments", 0),
        "is_pr": "pull_request" in issue,
        "body_len": len(issue.get("body") or "")
    }

def slim_pull(pull):
    """Strip a pull request (REST /pulls item) into the issues-file shape."""
    s = slim_issue(pull)
    s["is_pr"] = True  # /pulls items carry no pull_request marker key
    return s

def slim_commit(c):
    """Strip a commit."""
    cm = c.get("commit") or {}
    author = cm.get("author") or {}
    return {
        "sha": c.get("sha", "")[:12],
        "author_login": (c.get("author") or {}).get("login"),
        "author_name": author.get("name"),
        "author_email": author.get("email"),
        "date": author.get("date"),
        "message_subject": (cm.get("message") or "").split("\n")[0][:200]
    }

# Actions App-token pathology (2026-10-29 and 2026-11-02 refreshes): REST
# /issues?state=all returned PRs for every repo while silently dropping all
# 7,006 issues — same code, same URL works fine for a user token. When that
# signature shows up, rebuild the dataset from REST /pulls + GraphQL issues
# instead of shipping a PR-only issues.csv.
_prev_issue_counts = None

def previous_issue_count(repo):
    """Issue count for repo in the last committed data/issues.csv; 0 when the
    repo has no baseline there (new repo, or nothing committed yet)."""
    global _prev_issue_counts
    if _prev_issue_counts is None:
        _prev_issue_counts = {}
        path = REPO_ROOT.parent / "data" / "issues.csv"
        if path.exists():
            import csv as _csv
            with open(path, encoding="utf-8") as f:
                for row in _csv.DictReader(f):
                    if row.get("kind") == "issue":
                        _prev_issue_counts[row["repo"]] = \
                            _prev_issue_counts.get(row["repo"], 0) + 1
    return _prev_issue_counts.get(repo, 0)

def fetch_graphql_issues(repo):
    """Fetch all real issues via GraphQL, returning (slimmed, success).
    Mirrors slim_issue's field shapes so transform.py sees one schema."""
    items = []
    cursor = None
    while True:
        query = (
            "query($owner:String!,$name:String!,$cursor:String){"
            "repository(owner:$owner,name:$name){"
            "issues(first:100,after:$cursor,orderBy:{field:CREATED_AT,direction:ASC}){"
            "pageInfo{hasNextPage endCursor}"
            "nodes{number title state createdAt updatedAt closedAt"
            " author{login} assignees(first:20){nodes{login}}"
            " labels(first:50){nodes{name}} milestone{title}"
            " comments{totalCount} body}}}}"
        )
        args = ["api", "graphql", "-f", f"query={query}",
                "-f", f"owner={ORG}", "-f", f"name={repo}"]
        if cursor:
            args += ["-f", f"cursor={cursor}"]
        out, ok, err = gh(*args)
        if not ok:
            log(f"  graphql issues err: {err[:100]}")
            return items, False
        try:
            conn = json.loads(out)["data"]["repository"]["issues"]
        except (json.JSONDecodeError, KeyError) as e:
            log(f"  graphql issues parse err: {e}")
            return items, False
        for n in conn["nodes"]:
            items.append({
                "number": n.get("number"),
                "title": n.get("title"),
                "state": (n.get("state") or "").lower(),
                "created_at": n.get("createdAt"),
                "updated_at": n.get("updatedAt"),
                "closed_at": n.get("closedAt"),
                "user": (n.get("author") or {}).get("login"),
                "assignees": [asg.get("login")
                              for asg in (n.get("assignees") or {}).get("nodes") or []],
                "labels": [lab.get("name")
                           for lab in (n.get("labels") or {}).get("nodes") or []],
                "milestone": (n.get("milestone") or {}).get("title"),
                "comments": (n.get("comments") or {}).get("totalCount", 0),
                "is_pr": False,
                "body_len": len(n.get("body") or "")
            })
        if not conn["pageInfo"]["hasNextPage"]:
            break
        cursor = conn["pageInfo"]["endCursor"]
    return items, True

def fetch_issues_and_prs(repo, meta):
    """Fetch issues + PRs into issues/<repo>.jsonl. Returns (success, reason).

    REST /issues carries both kinds, but under the Actions App token it can
    silently return PRs only. On that signature (PRs present, zero issues),
    fall back to REST /pulls + GraphQL issues; refuse to write a PR-only
    dataset when the repo has a committed history of real issues.
    """
    if meta.get("has_issues") is False:
        log(f"  issues: skipped (has_issues=false)")
        save_jsonl("issues", repo, [])
        return True, ""
    issues_raw, ok = fetch_paginated("issues", repo)
    if not ok:
        return False, "issues fetch failed"
    slimmed = [slim_issue(i) for i in issues_raw]
    n_issues = sum(1 for s in slimmed if not s["is_pr"])
    n_prs = len(slimmed) - n_issues
    if n_issues == 0 and n_prs > 0:
        log("  issues: REST /issues returned PRs but zero issues — App-token "
            "pathology; falling back to /pulls + GraphQL issues")
        gql, gql_ok = fetch_graphql_issues(repo)
        pulls_raw, pulls_ok = fetch_paginated("pulls", repo)
        if not gql_ok or not pulls_ok:
            return False, "issues fallback fetch failed"
        slimmed = sorted(gql + [slim_pull(p) for p in pulls_raw],
                         key=lambda s: s["number"] or 0)
        n_issues = sum(1 for s in slimmed if not s["is_pr"])
        n_prs = len(slimmed) - n_issues
        if n_issues == 0 and n_prs > 0 and previous_issue_count(repo) > 0:
            return False, ("issues pathology: PRs fetched but zero issues via "
                           "REST and GraphQL (repo had issues in the last snapshot)")
    save_jsonl("issues", repo, slimmed)
    log(f"  issues: {n_issues} issues + {n_prs} PRs = {len(slimmed)} total")
    return True, ""

def fetch_repo_commits_since(repo, since="2014-01-01"):
    """Fetch commits since a date, returning (items, success)."""
    items = []
    page = 1
    while True:
        url = f"repos/{ORG}/{repo}/commits?per_page=100&page={page}&since={since}T00:00:00Z"
        out, ok, err = gh("api", url, timeout=180)
        if not ok:
            if "403" in err and "rate" in err.lower():
                log(f"  RATE LIMIT — sleep 60s")
                time.sleep(60)
                continue
            if "409" in err:  # empty repo
                return items, True
            log(f"  commits err p{page}: {err[:100]}")
            return items, False
        try:
            page_items = json.loads(out)
            if not isinstance(page_items, list) or len(page_items) == 0:
                break
            items.extend(page_items)
            if len(page_items) < 100:
                break
            page += 1
        except json.JSONDecodeError as e:
            log(f"  commits JSON error on page {page}: {e}")
            return items, False
    return items, True

def process_repo(repo, idx, total, since):
    """Fetch all data for one repo. Returns (success, reason)."""
    log(f"[{idx}/{total}] {repo}")

    # Metadata
    meta = fetch_repo_metadata(repo)
    if meta:
        save_jsonl("metadata", repo, [meta])
    log(f"  metadata: {'✓' if meta else '✗'}")
    if not meta:
        return False, "metadata fetch failed"

    # Languages
    langs = fetch_repo_languages(repo)
    save_jsonl("languages", repo, [langs] if langs else [])
    log(f"  languages: {len(langs)} languages")

    # Contributors
    contribs = fetch_repo_contributors(repo)
    save_jsonl("contributors", repo, contribs)
    log(f"  contributors: {len(contribs)}")

    # Releases
    rels = fetch_repo_releases(repo)
    save_jsonl("releases", repo, rels)
    log(f"  releases: {len(rels)}")

    # Issues + PRs (both normally come from /issues endpoint)
    ok, reason = fetch_issues_and_prs(repo, meta)
    if not ok:
        return False, reason

    # Commits
    commits_raw, ok = fetch_repo_commits_since(repo, since)
    if not ok:
        return False, "commits fetch failed"
    slim_commits = [slim_commit(c) for c in commits_raw]
    save_jsonl("commits", repo, slim_commits)
    log(f"  commits: {len(slim_commits)}")

    return True, ""

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--repos", help="Comma-separated repo list (default: all)")
    parser.add_argument("--since", default="2014-01-01", help="Earliest date (default: 2014-01-01)")
    parser.add_argument("--skip-existing", action="store_true",
                       help="Skip repos that already have a snapshot in this month's dir")
    args = parser.parse_args()

    if args.repos:
        repos = [repo.strip() for repo in args.repos.split(",") if repo.strip()]
    else:
        repos = ALL_REPOS

    log(f"=" * 60)
    log(f"csl-observatory FETCHER — Phase 1 backfill")
    log(f"Snapshot: {SNAPSHOT_DATE}")
    log(f"Repos: {len(repos)}")
    log(f"Since: {args.since}")
    log(f"Output: {SNAPSHOT_DIR}")
    log(f"=" * 60)

    # Rate limit check
    out, ok, _ = gh("api", "rate_limit", "--jq", ".resources.core")
    if ok:
        log(f"Initial rate limit: {out}")

    success = 0
    failed = []
    skipped = []
    start = time.time()

    for i, repo in enumerate(repos, 1):
        # Skip if already done in this month
        if args.skip_existing:
            issues_file = SNAPSHOT_DIR / "issues" / f"{repo}.jsonl"
            commits_file = SNAPSHOT_DIR / "commits" / f"{repo}.jsonl"
            if issues_file.exists() and commits_file.exists():
                log(f"[{i}/{len(repos)}] {repo} — SKIP (exists)")
                success += 1
                skipped.append(repo)
                continue

        try:
            ok, reason = process_repo(repo, i, len(repos), args.since)
            if ok:
                success += 1
            else:
                log(f"  FAILED: {reason}")
                failed.append({"repo": repo, "reason": reason})
        except Exception as e:
            log(f"  ERROR: {e}")
            failed.append({"repo": repo, "reason": str(e)})

        # Brief pause every 10 repos to spread API load
        if i % 10 == 0:
            elapsed = time.time() - start
            log(f"  [progress] {i}/{len(repos)} repos in {elapsed:.0f}s")

    elapsed = time.time() - start
    log(f"\n" + "=" * 60)
    log(f"COMPLETE: {success}/{len(repos)} repos in {elapsed:.0f}s")
    if failed:
        log(f"Failed: {', '.join(f['repo'] for f in failed)}")
    log(f"=" * 60)

    # Final rate limit
    out, ok, _ = gh("api", "rate_limit", "--jq", ".resources.core")
    if ok:
        log(f"Final rate limit: {out}")

    # Manifest
    manifest = {
        "snapshot_date": SNAPSHOT_DATE,
        "fetched_at": datetime.now(timezone.utc).isoformat(),
        "repos_attempted": len(repos),
        "repo_names_attempted": repos,
        "repos_succeeded": success,
        "repos_skipped": skipped,
        "repos_failed": [f["repo"] for f in failed],
        "repo_failures": failed,
        "since": args.since,
        "duration_seconds": int(elapsed)
    }
    with open(SNAPSHOT_DIR / "manifest.json", "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)
    log(f"Manifest: {SNAPSHOT_DIR / 'manifest.json'}")
    if failed:
        sys.exit(1)

if __name__ == "__main__":
    main()
