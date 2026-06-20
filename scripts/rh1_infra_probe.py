#!/usr/bin/env python3
"""Read-only deep probe of the RH1 infrastructure/web repos. Beyond license +
composition, it scans the root tree for THIRD-PARTY rights markers (font files,
OFL/Apache/MIT license files, vendor dirs) so a blanket license isn't applied
over assets that carry their own terms.

Usage: python scripts/rh1_infra_probe.py [repo ...]
"""
import json
import re
import subprocess
import sys
import time

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

OWNER = "sanskrit-lexicon"
REPOS = sys.argv[1:] or ["COLOGNE", "csl-homepage", "sanskrit-fonts",
                         "sanskrit-lexicon.github.io"]

# names that hint at third-party / non-default licensing
FLAG = re.compile(r"(?i)(licen[cs]e|ofl|copying|notice|font|vendor|node_modules|"
                  r"third[_-]?party|\.ttf$|\.otf$|\.woff2?$|\.eot$)")


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


def main():
    for repo in REPOS:
        code, meta = gh(f"repos/{OWNER}/{repo}",
                        "{spdx:(.license.spdx_id // \"NONE\"), br:.default_branch, "
                        "lang:.language, size:.size}")
        print(f"\n===== {repo} =====")
        if code != 0:
            print(f"  <{meta}>")
            continue
        m = json.loads(meta)
        _, langs = gh(f"repos/{OWNER}/{repo}/languages")
        try:
            lj = json.loads(langs); t = sum(lj.values()) or 1
            langstr = ", ".join(f"{k} {v*100//t}%" for k, v in
                                sorted(lj.items(), key=lambda kv: -kv[1])) or "(no code)"
        except Exception:
            langstr = "(none)"
        print(f"  spdx={m['spdx']}  branch={m['br']}  primary_lang={m['lang']}  "
              f"size={m['size']}KB")
        print(f"  languages: {langstr}")
        # root tree listing
        code, tree = gh(f"repos/{OWNER}/{repo}/contents", ".[].name")
        if code != 0:
            print(f"  root listing: <{tree}>")
            continue
        names = [n for n in tree.splitlines() if n.strip()]
        flagged = [n for n in names if FLAG.search(n)]
        print(f"  root entries ({len(names)}): {', '.join(names[:25])}"
              + (" ..." if len(names) > 25 else ""))
        print(f"  >>> third-party/license markers at root: "
              f"{', '.join(flagged) if flagged else 'none at root'}")
        # search the repo for Open Font License text (catches fonts in subdirs)
        code, hits = gh(f"search/code?q=repo:{OWNER}/{repo}+%22Open+Font+License%22",
                        ".total_count")
        if code == 0:
            print(f"  >>> 'Open Font License' code-search hits: {hits.strip()}")


if __name__ == "__main__":
    main()
