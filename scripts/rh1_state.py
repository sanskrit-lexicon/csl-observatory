#!/usr/bin/env python3
"""Reliable current-license snapshot for the RH1 repos, with retries.

Read-only. Reports the REAL `.license.spdx_id` and whether a LICENSE file
exists, retrying through the session's flaky TLS so transient failures are
never mistaken for 'no license' / 'repo not found'.
"""
import json
import subprocess
import sys
import time

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

OWNER = "sanskrit-lexicon"

REPOS = [
    # cluster 1 (thought unlicensed)
    "AP", "DCS", "FRI", "MW72",
    # cluster 2 (thought non-canonical CC-BY-SA)
    "ApteES", "BOR", "BUR", "INM", "SCH", "VCP", "GRA", "PWG", "PWK",
    # cluster 3 (GPL stubs)
    "csl-pywork", "csl-websanlexicon", "csl-orig",
    # cluster 5 (messy)
    "MWS", "Wil-YAT", "MD",
    # already-correct reference
    "BOP",
]


def gh(path, jq=None, tries=5):
    args = ["gh", "api", path] + (["--jq", jq] if jq else [])
    last = ""
    for i in range(tries):
        r = subprocess.run(args, capture_output=True, encoding="utf-8")
        if r.returncode == 0:
            return True, r.stdout
        last = (r.stderr or "").strip()
        # a genuine 404 is terminal; anything else is transient -> retry
        if "Not Found" in last or "404" in last:
            return False, "404"
        time.sleep(2 * (i + 1))
    return False, f"FAIL:{last[:80]}"


def repo_state(repo):
    ok, out = gh(f"repos/{OWNER}/{repo}", ".license.spdx_id // \"NONE\"")
    spdx = out.strip() if ok else f"<{out}>"
    ok2, br = gh(f"repos/{OWNER}/{repo}", ".default_branch")
    branch = br.strip() if ok2 else "?"
    files = []
    for name in ("LICENSE", "LICENSE.md", "LICENSE.txt", "COPYING"):
        okf, _ = gh(f"repos/{OWNER}/{repo}/contents/{name}", ".sha")
        if okf:
            files.append(name)
    return spdx, branch, files


def main():
    print(f"{'repo':18} {'spdx':16} {'branch':8} license-files")
    print("-" * 60)
    for repo in REPOS:
        spdx, branch, files = repo_state(repo)
        print(f"{repo:18} {spdx:16} {branch:8} {', '.join(files) or '(none)'}")


if __name__ == "__main__":
    main()
