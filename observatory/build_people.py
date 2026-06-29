#!/usr/bin/env python3
"""
csl-observatory Phase 3 — people.yaml builder.

Consolidates contributor information by:
1. Reading the current repo inventory from data/repos.csv
2. Fetching CITATION.cff from those repos
3. Extracting authors (name, ORCID, affiliation, email)
4. Cross-referencing with GitHub commit/issue contributors
5. Producing data/people.yaml with one entry per person
6. Flagging entries with missing data for maintainer enrichment

Output schema:
  - login: github_username           # canonical key
    name: "Real Name"                # from CITATION.cff or null
    orcid: "0000-0000-0000-0000"     # null if unknown
    affiliation: "Cologne University" # null if unknown
    email: "..."                      # null or anonymized
    aliases: [git_email_1, git_email_2]  # for matching commits
    repos_authored: [PWG, MWS, ...]   # CITATION.cff appearance
    repos_contributed: [...]          # commits + issues
    enrichment_status: "complete" | "needs_name" | "needs_orcid" | "needs_all"
"""

import subprocess
import json
import sys
import csv
import yaml  # pip install pyyaml if missing
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

ORG = "sanskrit-lexicon"
REPO_ROOT = Path(__file__).parent
DATA_DIR = REPO_ROOT.parent / "data"


def load_repo_inventory():
    """Read the current observatory repo inventory from data/repos.csv."""
    repos_csv = DATA_DIR / "repos.csv"
    if not repos_csv.exists():
        raise SystemExit(
            f"repo inventory missing: {repos_csv}. Run transform.py before build_people.py."
        )
    repos = []
    seen = set()
    with open(repos_csv, encoding="utf-8", newline="") as f:
        for row in csv.DictReader(f):
            repo = (row.get("repo") or "").strip()
            if repo and repo not in seen:
                repos.append(repo)
                seen.add(repo)
    if not repos:
        raise SystemExit(f"repo inventory had no repo rows: {repos_csv}")
    return repos

def gh(*args, timeout=60):
    """Run gh with arg list."""
    try:
        r = subprocess.run(["gh"] + list(args), capture_output=True, text=True,
                          timeout=timeout, encoding='utf-8')
        return r.stdout.strip(), r.returncode == 0
    except Exception:
        return "", False

def fetch_citation(repo):
    """Fetch CITATION.cff content from a repo."""
    out, ok = gh("api", f"repos/{ORG}/{repo}/contents/CITATION.cff",
                 "--jq", ".content")
    if not ok or not out:
        return None
    try:
        import base64
        decoded = base64.b64decode(out.replace("\\n", "")).decode('utf-8')
        return decoded
    except Exception as e:
        print(f"  decode error for {repo}: {e}")
        return None

def parse_citation(content):
    """Parse CITATION.cff YAML and extract authors."""
    if not content:
        return []
    try:
        data = yaml.safe_load(content)
        return data.get("authors", []) if data else []
    except yaml.YAMLError as e:
        print(f"    yaml parse error: {e}")
        return []

def fetch_contributors(repo):
    """Fetch contributors for a repo."""
    out, ok = gh("api", f"repos/{ORG}/{repo}/contributors?per_page=100",
                 "--jq", "[.[] | {login, contributions, type}]")
    if not ok or not out:
        return []
    try:
        return json.loads(out)
    except:
        return []

def main():
    print(f"\n{'='*60}")
    print(f"BUILDING people.yaml")
    print(f"{'='*60}")

    repos = load_repo_inventory()
    people = {}  # key: login (or name if no login), value: dict

    print(f"\nStep 1: Fetching CITATION.cff from {len(repos)} repos...")
    citation_authors_by_repo = {}
    for i, repo in enumerate(repos, 1):
        print(f"  [{i}/{len(repos)}] {repo}", end=" ")
        content = fetch_citation(repo)
        if not content:
            print("(no CITATION.cff)")
            continue
        authors = parse_citation(content)
        citation_authors_by_repo[repo] = authors
        print(f"({len(authors)} authors)")

    print(f"\nStep 2: Fetching contributors from {len(repos)} repos...")
    contributors_by_repo = {}
    for i, repo in enumerate(repos, 1):
        contribs = fetch_contributors(repo)
        contributors_by_repo[repo] = contribs
        if i % 10 == 0:
            print(f"  [{i}/{len(repos)}]...")

    print(f"\nStep 3: Consolidating people index...")

    # Pass 1: Add CITATION.cff authors (richer metadata)
    for repo, authors in citation_authors_by_repo.items():
        for author in authors:
            if not isinstance(author, dict):
                continue
            family = author.get("family-names", "")
            given = author.get("given-names", "")
            full_name = f"{given} {family}".strip()
            login = author.get("alias")  # GitHub username if recorded
            orcid = author.get("orcid", "")
            affiliation = author.get("affiliation")
            email = author.get("email")

            # Use login as key, fallback to name
            key = login or full_name or "unknown"
            if key not in people:
                people[key] = {
                    "login": login,
                    "name": full_name or None,
                    "orcid": orcid or None,
                    "affiliation": affiliation,
                    "email": email,
                    "aliases": [],
                    "repos_authored": [],
                    "repos_contributed": [],
                    "enrichment_status": "tbd"
                }
            entry = people[key]
            if repo not in entry["repos_authored"]:
                entry["repos_authored"].append(repo)
            if email and email not in entry["aliases"]:
                entry["aliases"].append(email)

    # Pass 2: Add GitHub contributors (may not be in CITATION.cff)
    for repo, contribs in contributors_by_repo.items():
        for c in contribs:
            login = c.get("login")
            if not login or c.get("type") == "Bot":
                continue
            if login not in people:
                people[login] = {
                    "login": login,
                    "name": None,
                    "orcid": None,
                    "affiliation": None,
                    "email": None,
                    "aliases": [],
                    "repos_authored": [],
                    "repos_contributed": [],
                    "enrichment_status": "tbd"
                }
            entry = people[login]
            if repo not in entry["repos_contributed"]:
                entry["repos_contributed"].append(repo)

    # Pass 3: Determine enrichment status
    for key, entry in people.items():
        missing = []
        if not entry.get("name"):
            missing.append("name")
        if not entry.get("orcid"):
            missing.append("orcid")
        if not entry.get("affiliation"):
            missing.append("affiliation")

        if not missing:
            entry["enrichment_status"] = "complete"
        elif missing == ["affiliation"]:
            entry["enrichment_status"] = "needs_affiliation"
        elif "name" in missing and "orcid" in missing:
            entry["enrichment_status"] = "needs_name_and_orcid"
        elif "name" in missing:
            entry["enrichment_status"] = "needs_name"
        elif "orcid" in missing:
            entry["enrichment_status"] = "needs_orcid"
        else:
            entry["enrichment_status"] = "incomplete"

    # Sort: by enrichment_status (complete first), then by name
    sorted_people = sorted(
        people.values(),
        key=lambda p: (p["enrichment_status"] != "complete",
                      (p.get("name") or p.get("login") or "").lower())
    )

    # Write YAML
    output_yaml = DATA_DIR / "people.yaml"
    output_yaml.parent.mkdir(parents=True, exist_ok=True)

    yaml_content = """# csl-observatory contributors index
# Auto-generated by observatory/build_people.py
# Manually curated additions: edit any 'name', 'orcid', 'affiliation' field below
# Re-run build_people.py to refresh from latest CITATION.cff and GitHub data
#
# Schema:
#   - login: github_username (canonical key)
#     name: "Full Name" or null
#     orcid: "0000-0000-0000-0000" or null
#     affiliation: "Institution" or null
#     repos_authored: [list of repos where this person is in CITATION.cff]
#     repos_contributed: [list of repos with commits]
#     enrichment_status: complete | needs_name | needs_orcid | needs_affiliation | needs_name_and_orcid

people:
"""

    for entry in sorted_people:
        # Inline YAML for compactness
        login = entry.get("login") or "null"
        name = json.dumps(entry["name"]) if entry["name"] else "null"
        orcid = f'"{entry["orcid"]}"' if entry["orcid"] else "null"
        affil = json.dumps(entry["affiliation"]) if entry["affiliation"] else "null"
        repos_a = json.dumps(entry["repos_authored"])
        repos_c = json.dumps(entry["repos_contributed"])
        status = entry["enrichment_status"]

        yaml_content += f"""  - login: {login}
    name: {name}
    orcid: {orcid}
    affiliation: {affil}
    repos_authored: {repos_a}
    repos_contributed: {repos_c}
    enrichment_status: {status}
"""

    with open(output_yaml, "w", encoding="utf-8") as f:
        f.write(yaml_content)

    # Stats
    by_status = {}
    for p in sorted_people:
        s = p["enrichment_status"]
        by_status[s] = by_status.get(s, 0) + 1

    print(f"\n{'='*60}")
    print(f"Total people: {len(sorted_people)}")
    print(f"Output: {output_yaml}")
    print(f"\nEnrichment status breakdown:")
    for status, count in sorted(by_status.items()):
        print(f"  {status}: {count}")
    print(f"{'='*60}")

    # Write a CSV summary too
    output_csv = DATA_DIR / "people_summary.csv"
    with open(output_csv, "w", encoding="utf-8") as f:
        f.write("login,name,orcid,affiliation,n_repos_authored,n_repos_contributed,status\n")
        for p in sorted_people:
            f.write(f'{p.get("login") or ""},'
                    f'"{p.get("name") or ""}",'
                    f'"{p.get("orcid") or ""}",'
                    f'"{p.get("affiliation") or ""}",'
                    f'{len(p["repos_authored"])},'
                    f'{len(p["repos_contributed"])},'
                    f'{p["enrichment_status"]}\n')

    print(f"\nCSV summary: {output_csv}")

if __name__ == "__main__":
    main()
