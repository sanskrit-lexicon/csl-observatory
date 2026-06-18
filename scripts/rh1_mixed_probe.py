#!/usr/bin/env python3
"""Probe the 'mixed code+data' RH1 repos: current license, default branch,
language/byte composition, and whether a README/LICENSE already exists — so a
sensible dual-license layout (which SPDX is primary) can be proposed per repo.

Read-only, retried against the flaky network.
"""
import json
import subprocess
import sys
import time

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

OWNER = "sanskrit-lexicon"
REPOS = ["MWinflect", "mw-dev", "csl-devanagari", "csl-json",
         "csl-ldev", "csl-lnum", "csl-lslink"]


def gh(path, jq=None, tries=5):
    args = ["gh", "api", path] + (["--jq", jq] if jq else [])
    last = ""
    for i in range(tries):
        r = subprocess.run(args, capture_output=True, encoding="utf-8")
        if r.returncode == 0:
            return 0, r.stdout
        last = (r.stderr or "").strip()
        if "Not Found" in last or '"status":"404"' in last:
            return 1, "404"
        time.sleep(2 * (i + 1))
    return 2, f"TRANSIENT:{last[:80]}"


def has(repo, path):
    code, _ = gh(f"repos/{OWNER}/{repo}/contents/{path}", ".sha")
    return code == 0


def main():
    for repo in REPOS:
        code, meta = gh(f"repos/{OWNER}/{repo}",
                        "{spdx:(.license.spdx_id // \"NONE\"), br:.default_branch, "
                        "lang:.language, size:.size}")
        if code != 0:
            print(f"\n{repo}: <{meta}>")
            continue
        m = json.loads(meta)
        _, langs = gh(f"repos/{OWNER}/{repo}/languages")
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
