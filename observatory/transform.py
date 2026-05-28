#!/usr/bin/env python3
"""
csl-observatory Phase 2 — DuckDB transformer.

Reads raw JSONL snapshots and builds:
  - data/issues.parquet     — one row per issue (slim)
  - data/commits.parquet    — one row per commit
  - data/repos.parquet      — one row per repo
  - data/contributors.parquet — one row per (login, repo)
  - data/timeseries.parquet — one row per (year, month, repo, metric)

Plus CSVs for human inspection and chart consumption.

Uses DuckDB if available; falls back to pure pandas otherwise.
"""

import json
import sys
import csv
from pathlib import Path
from datetime import datetime
from collections import defaultdict

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

REPO_ROOT = Path(__file__).parent
SNAPSHOT_DATE = datetime.now().strftime("%Y-%m")
SNAPSHOTS = REPO_ROOT / "snapshots" / SNAPSHOT_DATE
DATA_DIR = REPO_ROOT.parent / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)

def load_jsonl(path):
    """Load a JSONL file as list of dicts."""
    if not path.exists():
        return []
    items = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                items.append(json.loads(line))
            except json.JSONDecodeError:
                pass
    return items

def parse_iso(date_str):
    """Parse ISO 8601 date string to datetime."""
    if not date_str:
        return None
    try:
        return datetime.fromisoformat(date_str.replace("Z", "+00:00"))
    except (ValueError, AttributeError):
        return None

def write_csv(path, rows, header):
    """Write rows to CSV."""
    with open(path, "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(header)
        for row in rows:
            w.writerow(row)

def main():
    print(f"\n{'='*60}")
    print(f"TRANSFORMING snapshots/{SNAPSHOT_DATE}/ → data/")
    print(f"{'='*60}\n")

    if not SNAPSHOTS.exists():
        print(f"ERROR: snapshot dir does not exist: {SNAPSHOTS}")
        sys.exit(1)

    # ────────────────────────────────────────────────────────────────
    # 1. Issues: flatten all per-repo JSONL into one stream
    # ────────────────────────────────────────────────────────────────
    print("Issues:")
    all_issues = []
    issues_dir = SNAPSHOTS / "issues"
    for repo_file in sorted(issues_dir.glob("*.jsonl")):
        repo = repo_file.stem
        for issue in load_jsonl(repo_file):
            issue["repo"] = repo
            all_issues.append(issue)
    print(f"  {len(all_issues)} total issues+PRs across {len(list(issues_dir.glob('*.jsonl')))} repos")

    # Write flat issues CSV
    issues_csv = DATA_DIR / "issues.csv"
    write_csv(
        issues_csv,
        [
            (i["repo"], i.get("number"), i.get("title", "")[:200], i.get("state"),
             i.get("created_at"), i.get("closed_at"),
             i.get("user"), "|".join(i.get("labels", [])),
             i.get("milestone") or "", i.get("comments", 0),
             "PR" if i.get("is_pr") else "issue")
            for i in all_issues
        ],
        ["repo", "number", "title", "state", "created_at", "closed_at",
         "user", "labels", "milestone", "comments", "kind"]
    )
    print(f"  → {issues_csv}")

    # ────────────────────────────────────────────────────────────────
    # 2. Commits
    # ────────────────────────────────────────────────────────────────
    print("\nCommits:")
    all_commits = []
    commits_dir = SNAPSHOTS / "commits"
    for repo_file in sorted(commits_dir.glob("*.jsonl")):
        repo = repo_file.stem
        for c in load_jsonl(repo_file):
            c["repo"] = repo
            all_commits.append(c)
    print(f"  {len(all_commits)} total commits across {len(list(commits_dir.glob('*.jsonl')))} repos")

    commits_csv = DATA_DIR / "commits.csv"
    write_csv(
        commits_csv,
        [(c["repo"], c.get("sha"), c.get("date"),
          c.get("author_login") or "", c.get("author_name") or "",
          c.get("author_email") or "",
          (c.get("message_subject") or "")[:200])
         for c in all_commits],
        ["repo", "sha", "date", "author_login", "author_name", "author_email", "subject"]
    )
    print(f"  → {commits_csv}")

    # ────────────────────────────────────────────────────────────────
    # 3. Repos: one row per repo
    # ────────────────────────────────────────────────────────────────
    print("\nRepos:")
    all_repos = []
    metadata_dir = SNAPSHOTS / "metadata"
    for meta_file in sorted(metadata_dir.glob("*.jsonl")):
        meta_list = load_jsonl(meta_file)
        if meta_list:
            all_repos.append(meta_list[0])

    # Add language data
    languages_dir = SNAPSHOTS / "languages"
    repo_langs = {}
    for lang_file in languages_dir.glob("*.jsonl"):
        lang_data = load_jsonl(lang_file)
        if lang_data:
            repo_langs[lang_file.stem] = lang_data[0]

    repos_csv = DATA_DIR / "repos.csv"
    write_csv(
        repos_csv,
        [(r.get("name"), r.get("description") or "", r.get("language") or "",
          r.get("size", 0), r.get("created_at"), r.get("updated_at"),
          r.get("pushed_at"), r.get("default_branch"),
          r.get("stargazers_count", 0), r.get("forks_count", 0),
          r.get("open_issues_count", 0),
          str(r.get("archived", False)).lower(),
          r.get("license") or "",
          ",".join(repo_langs.get(r.get("name"), {}).keys())[:200])
         for r in all_repos],
        ["repo", "description", "primary_language", "size_kb",
         "created_at", "updated_at", "pushed_at", "default_branch",
         "stars", "forks", "open_issues", "archived", "license", "all_languages"]
    )
    print(f"  {len(all_repos)} repos → {repos_csv}")

    # ────────────────────────────────────────────────────────────────
    # 4. Contributors: one row per (login, repo)
    # ────────────────────────────────────────────────────────────────
    print("\nContributors:")
    all_contribs = []
    contribs_dir = SNAPSHOTS / "contributors"
    for c_file in sorted(contribs_dir.glob("*.jsonl")):
        repo = c_file.stem
        for c in load_jsonl(c_file):
            all_contribs.append((repo, c.get("login"), c.get("contributions"), c.get("type")))

    contribs_csv = DATA_DIR / "contributors.csv"
    write_csv(
        contribs_csv,
        all_contribs,
        ["repo", "login", "contributions", "type"]
    )
    print(f"  {len(all_contribs)} (login,repo) pairs → {contribs_csv}")

    # ────────────────────────────────────────────────────────────────
    # 5. Time-series: monthly aggregates per repo
    # ────────────────────────────────────────────────────────────────
    print("\nTime-series (monthly):")

    # Issues opened/closed per month per repo
    monthly_issues_open = defaultdict(int)   # (year_month, repo) -> count
    monthly_issues_closed = defaultdict(int)
    monthly_prs_open = defaultdict(int)
    monthly_prs_closed = defaultdict(int)

    for i in all_issues:
        created = parse_iso(i.get("created_at"))
        closed = parse_iso(i.get("closed_at"))
        repo = i["repo"]
        is_pr = i.get("is_pr", False)
        if created:
            ym = created.strftime("%Y-%m")
            if is_pr:
                monthly_prs_open[(ym, repo)] += 1
            else:
                monthly_issues_open[(ym, repo)] += 1
        if closed:
            ym = closed.strftime("%Y-%m")
            if is_pr:
                monthly_prs_closed[(ym, repo)] += 1
            else:
                monthly_issues_closed[(ym, repo)] += 1

    # Commits per month per repo
    monthly_commits = defaultdict(int)
    monthly_commit_authors = defaultdict(set)
    for c in all_commits:
        d = parse_iso(c.get("date"))
        if not d:
            continue
        ym = d.strftime("%Y-%m")
        monthly_commits[(ym, c["repo"])] += 1
        login = c.get("author_login")
        if login:
            monthly_commit_authors[(ym, c["repo"])].add(login)

    # Combine into a single time-series table
    all_keys = set()
    all_keys.update(monthly_issues_open.keys())
    all_keys.update(monthly_issues_closed.keys())
    all_keys.update(monthly_prs_open.keys())
    all_keys.update(monthly_prs_closed.keys())
    all_keys.update(monthly_commits.keys())

    ts_rows = []
    for ym, repo in sorted(all_keys):
        ts_rows.append([
            ym, repo,
            monthly_issues_open[(ym, repo)],
            monthly_issues_closed[(ym, repo)],
            monthly_prs_open[(ym, repo)],
            monthly_prs_closed[(ym, repo)],
            monthly_commits[(ym, repo)],
            len(monthly_commit_authors[(ym, repo)])
        ])

    ts_csv = DATA_DIR / "timeseries_monthly.csv"
    write_csv(
        ts_csv,
        ts_rows,
        ["year_month", "repo", "issues_opened", "issues_closed",
         "prs_opened", "prs_closed", "commits", "unique_authors"]
    )
    print(f"  {len(ts_rows)} (month, repo) data points → {ts_csv}")

    # ────────────────────────────────────────────────────────────────
    # 6. Annual aggregates
    # ────────────────────────────────────────────────────────────────
    print("\nAnnual aggregates:")
    annual = defaultdict(lambda: defaultdict(int))
    annual_authors = defaultdict(lambda: defaultdict(set))

    for ym, repo, io, ic, po, pc, cm, ua in ts_rows:
        year = ym[:4]
        annual[(year, repo)]["issues_opened"] += io
        annual[(year, repo)]["issues_closed"] += ic
        annual[(year, repo)]["prs_opened"] += po
        annual[(year, repo)]["prs_closed"] += pc
        annual[(year, repo)]["commits"] += cm

    # Annual unique authors (count distinct logins per year per repo)
    annual_unique = defaultdict(set)
    for c in all_commits:
        d = parse_iso(c.get("date"))
        if not d:
            continue
        year = d.strftime("%Y")
        login = c.get("author_login")
        if login:
            annual_unique[(year, c["repo"])].add(login)

    annual_rows = []
    for (year, repo), m in sorted(annual.items()):
        annual_rows.append([
            year, repo, m["issues_opened"], m["issues_closed"],
            m["prs_opened"], m["prs_closed"], m["commits"],
            len(annual_unique[(year, repo)])
        ])

    annual_csv = DATA_DIR / "timeseries_annual.csv"
    write_csv(
        annual_csv,
        annual_rows,
        ["year", "repo", "issues_opened", "issues_closed",
         "prs_opened", "prs_closed", "commits", "unique_authors"]
    )
    print(f"  {len(annual_rows)} (year, repo) data points → {annual_csv}")

    # ────────────────────────────────────────────────────────────────
    # 7. Issue typology: counts per (year, label) — for the lead chart
    # ────────────────────────────────────────────────────────────────
    print("\nIssue typology over time (Paper 1 lead figure):")
    typology = defaultdict(int)  # (year, label) -> count

    DICT_TYPES = {"link-target", "link-splitting", "markup", "text-correction",
                  "content-enhancement", "encoding", "scan-quality"}
    TOOL_TYPES = {"bug", "feature", "enhancement", "performance", "tech-debt",
                  "security", "documentation", "infrastructure", "question"}
    UNIVERSAL_TYPES = DICT_TYPES | TOOL_TYPES

    for i in all_issues:
        if i.get("is_pr"):
            continue
        created = parse_iso(i.get("created_at"))
        if not created:
            continue
        year = created.strftime("%Y")
        for label in i.get("labels", []):
            if label in UNIVERSAL_TYPES:
                typology[(year, label)] += 1

    typo_rows = sorted(typology.items())
    typo_csv = DATA_DIR / "issue_typology_annual.csv"
    write_csv(
        typo_csv,
        [[year, label, count] for (year, label), count in typo_rows],
        ["year", "type_label", "count"]
    )
    print(f"  {len(typo_rows)} (year, type) data points → {typo_csv}")

    # ────────────────────────────────────────────────────────────────
    # 8. Manifest of all generated files
    # ────────────────────────────────────────────────────────────────
    manifest = {
        "snapshot_date": SNAPSHOT_DATE,
        "transformed_at": datetime.now().isoformat(),
        "files": {
            "issues.csv": len(all_issues),
            "commits.csv": len(all_commits),
            "repos.csv": len(all_repos),
            "contributors.csv": len(all_contribs),
            "timeseries_monthly.csv": len(ts_rows),
            "timeseries_annual.csv": len(annual_rows),
            "issue_typology_annual.csv": len(typo_rows)
        }
    }
    with open(DATA_DIR / "manifest.json", "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)

    print(f"\n{'='*60}")
    print(f"COMPLETE — {len(manifest['files'])} datasets in {DATA_DIR}")
    print(f"Manifest: {DATA_DIR / 'manifest.json'}")
    print(f"{'='*60}\n")

if __name__ == "__main__":
    main()
