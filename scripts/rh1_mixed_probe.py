#!/usr/bin/env python3
"""Probe the 'mixed code+data' RH1 repos: current license, default branch,
language/byte composition, and whether a README/LICENSE already exists — so a
sensible dual-license layout (which SPDX is primary) can be proposed per repo.

Read-only, retried against the flaky network.
"""
import json
import sys

from _common import gh_api

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

OWNER = "sanskrit-lexicon"
DEFAULT_REPOS = ["MWinflect", "mw-dev", "csl-devanagari", "csl-json",
                 "csl-ldev", "csl-lnum", "csl-lslink"]
REPOS = sys.argv[1:] or DEFAULT_REPOS


def has(repo, path):
    code, _ = gh_api([f"repos/{OWNER}/{repo}/contents/{path}", "--jq", ".sha"],
                     err_max=80)
    return code == 0


def main():
    for repo in REPOS:
        code, meta = gh_api([f"repos/{OWNER}/{repo}",
                             "--jq", "{spdx:(.license.spdx_id // \"NONE\"), br:.default_branch, "
                             "lang:.language, size:.size}"], err_max=80)
        if code != 0:
            print(f"\n{repo}: <{meta}>")
            continue
        m = json.loads(meta)
        _, langs = gh_api([f"repos/{OWNER}/{repo}/languages"], err_max=80)
        try:
            lj = json.loads(langs)
            total = sum(lj.values()) or 1
            langstr = ", ".join(f"{k} {v*100//total}%" for k, v in
                                sorted(lj.items(), key=lambda kv: -kv[1]))
        except Exception:
            langstr = "(none / data-only)"
        files = [f for f in ("LICENSE", "LICENSE.md", "LICENSE.txt", "README.md",
                             "README", "readme.txt") if has(repo, f)]
        print(f"\n{repo}")
        print(f"  spdx={m['spdx']}  branch={m['br']}  primary_lang={m['lang']}  "
              f"size={m['size']}KB")
        print(f"  languages: {langstr or '(data-only, no code detected)'}")
        print(f"  files: {', '.join(files) or '(no LICENSE/README)'}")


if __name__ == "__main__":
    main()
