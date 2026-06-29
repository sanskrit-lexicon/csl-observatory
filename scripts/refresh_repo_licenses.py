#!/usr/bin/env python3
"""Refresh ONLY the `license` and `archived` columns of repos.csv from live
GitHub, so the repository-health dashboard reflects the RH1/RH3 rollout. All
other columns are left as the committed snapshot.

Network-resilient: if a repo's live state can't be fetched after retries, its
existing values are KEPT (never blanked) and the repo is reported, so a flaky
network can't corrupt the snapshot.

Usage:  python scripts/refresh_repo_licenses.py [--dry-run]
"""
import csv
import json
import os
import subprocess
import sys
import time

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

OWNER = "sanskrit-lexicon"
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
REPOS = os.path.join(ROOT, "observatory", "site", "src", "data", "repos.csv")


def gh_state(repo, tries=6):
    for i in range(tries):
        r = subprocess.run(
            ["gh", "api", f"repos/{OWNER}/{repo}",
             "--jq", '{lic:(.license.spdx_id // ""), arch:.archived}'],
            capture_output=True, encoding="utf-8")
        if r.returncode == 0:
            j = json.loads(r.stdout)
            return j.get("lic", ""), bool(j.get("arch")), None
        err = (r.stderr or "").strip()
        if "Not Found" in err or '"status":"404"' in err:
            return None, None, "404"
        time.sleep(2 * (i + 1))
    return None, None, "TRANSIENT"


def main():
    dry = "--dry-run" in sys.argv
    with open(REPOS, encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        fields = reader.fieldnames
        rows = list(reader)

    changed, failed = [], []
    for row in rows:
        repo = row["repo"]
        lic, arch, err = gh_state(repo)
        if err:
            failed.append(f"{repo}({err})")
            continue
        new_lic = lic or ""
        new_arch = "true" if arch else "false"
        if (new_lic, new_arch) != (row["license"], row["archived"]):
            changed.append(f"{repo}: license {row['license']!r}->{new_lic!r} "
                           f"archived {row['archived']}->{new_arch}")
            if not dry:
                row["license"] = new_lic
                row["archived"] = new_arch

    # Write even if some repos failed: failed rows keep their old values, so the
    # write is safe and reruns converge (each pass fills more gaps).
    if not dry:
        with open(REPOS, "w", encoding="utf-8", newline="") as f:
            w = csv.DictWriter(f, fieldnames=fields)
            w.writeheader()
            w.writerows(rows)

    print(f"{'[DRY-RUN] ' if dry else ''}{len(changed)} row(s) changed:")
    for c in changed:
        print(f"  {c}")
    if failed:
        print(f"\nWARNING: {len(failed)} repo(s) could not be refreshed "
              f"(kept old values; re-run to retry): {', '.join(failed)}")
        sys.exit(1)
    if dry:
        print("\n(dry-run: repos.csv not modified)")
    else:
        print(f"\nwrote {REPOS}")


if __name__ == "__main__":
    main()
