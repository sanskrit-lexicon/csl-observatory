#!/usr/bin/env python3
"""Reliable current-license snapshot for the RH1 repos, with retries.

Read-only. Reports the REAL `.license.spdx_id` and whether a LICENSE file
exists, retrying through the session's flaky TLS so transient failures are
never mistaken for 'no license' / 'repo not found'.
"""
import json
import sys

from _common import gh_api_state

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


def repo_state(repo):
    ok, out = gh_api_state(f"repos/{OWNER}/{repo}", ".license.spdx_id // \"NONE\"")
    spdx = out.strip() if ok else f"<{out}>"
    ok2, br = gh_api_state(f"repos/{OWNER}/{repo}", ".default_branch")
    branch = br.strip() if ok2 else "?"
    files = []
    for name in ("LICENSE", "LICENSE.md", "LICENSE.txt", "COPYING"):
        okf, _ = gh_api_state(f"repos/{OWNER}/{repo}/contents/{name}", ".sha")
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
