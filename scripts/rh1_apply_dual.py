#!/usr/bin/env python3
"""Apply the RH1 dual-license layout to a 'mixed code+data' repo.

Layout (approved by MG 2026-06-18):
  LICENSE              = CC-BY-SA-4.0  (canonical text; GitHub detects this)
  licenses/GPL-3.0.txt = GPL-3.0       (canonical text; covers the source code)
  README.md            = a "## License" section explaining the split (appended once)

Network-resilient (retries reads; rechecks live state after a failed write so a
timed-out PUT can't double-apply). Idempotent: skips a step already in place.

Usage:
  python scripts/rh1_apply_dual.py MWinflect --dry-run
  python scripts/rh1_apply_dual.py MWinflect
  python scripts/rh1_apply_dual.py mw-dev csl-devanagari csl-json csl-lslink
"""
import argparse
import base64
import json
import subprocess
import sys
import time

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

OWNER = "sanskrit-lexicon"
STAMP = "RH1 dual-license, approved 2026-06-18"

# The code license lives in a subdirectory: GitHub's license detector only scans
# the repo root, so a root-level second license file (e.g. LICENSE-CODE) collides
# with the LICENSE* glob and makes detection ambiguous. Keeping only LICENSE at
# the root lets GitHub detect CC-BY-SA-4.0 cleanly.
CODE_LICENSE_PATH = "licenses/GPL-3.0.txt"

README_SECTION = """
## License

This repository contains both source code and dictionary/data files, which are
licensed separately:

- **Source code** (e.g. `*.py`, `*.php`, `*.js`, `*.sh`) is licensed under the
  **GNU General Public License v3.0** — see
  [`licenses/GPL-3.0.txt`](licenses/GPL-3.0.txt).
- **Dictionary and data files** are licensed under **Creative Commons
  Attribution-ShareAlike 4.0 International (CC-BY-SA-4.0)** — see
  [`LICENSE`](LICENSE).
"""


def gh(args, tries=5):
    last = ""
    for i in range(tries):
        r = subprocess.run(["gh", "api", *args], capture_output=True, encoding="utf-8")
        if r.returncode == 0:
            return 0, r.stdout
        last = (r.stderr or "").strip()
        if "Not Found" in last or '"status":"404"' in last:
            return 1, "404"
        time.sleep(2 * (i + 1))
    return 2, f"TRANSIENT:{last[:100]}"


def license_text(key):
    code, out = gh([f"licenses/{key}", "--jq", ".body"])
    if code != 0 or not out.strip():
        raise SystemExit(f"could not fetch license text for {key}")
    return out


def default_branch(repo):
    code, out = gh([f"repos/{OWNER}/{repo}", "--jq", ".default_branch"])
    return out.strip() if code == 0 else None


def get_file(repo, path):
    """Return (sha, decoded_text) or (None, None) if absent."""
    code, out = gh([f"repos/{OWNER}/{repo}/contents/{path}",
                    "--jq", "{sha:.sha, content:.content}"])
    if code != 0:
        return None, None
    j = json.loads(out)
    text = base64.b64decode(j.get("content", "")).decode("utf-8", "replace")
    return j.get("sha"), text


def spdx(repo):
    code, out = gh([f"repos/{OWNER}/{repo}", "--jq", ".license.spdx_id // \"NONE\""])
    return out.strip() if code == 0 else None


def put_file(repo, path, text, branch, message, sha=None, tries=4):
    content_b64 = base64.b64encode(text.encode("utf-8")).decode("ascii")
    last = "unknown"
    for i in range(tries):
        payload = {"message": message, "content": content_b64, "branch": branch}
        if sha:
            payload["sha"] = sha
        r = subprocess.run(
            ["gh", "api", "--method", "PUT",
             f"repos/{OWNER}/{repo}/contents/{path}", "--input", "-"],
            input=json.dumps(payload), capture_output=True, encoding="utf-8",
        )
        if r.returncode == 0:
            return json.loads(r.stdout)["commit"]["sha"][:8], None
        last = (r.stderr or "").strip()[:160]
        time.sleep(3 * (i + 1))
        cur_sha, cur_text = get_file(repo, path)
        if cur_text is not None and cur_text == text:  # write actually landed
            return "verified", None
        if cur_sha:
            sha = cur_sha  # refresh before retry
    return None, last


def do_repo(repo, dry, branch=None):
    branch = branch or default_branch(repo)
    if not branch:
        print(f"{repo}: ERROR could not resolve branch (404/network) — skipped")
        return False
    print(f"{repo} (branch {branch}):")
    ok = True

    # 1) LICENSE = CC-BY-SA-4.0
    cur = spdx(repo)
    if cur == "CC-BY-SA-4.0":
        print("  LICENSE       SKIP (already CC-BY-SA-4.0)")
    else:
        sha, _ = get_file(repo, "LICENSE")
        if dry:
            print(f"  LICENSE       would {'replace' if sha else 'add'} CC-BY-SA-4.0")
        else:
            c, err = put_file(repo, "LICENSE", CC, branch,
                              f"Add CC-BY-SA-4.0 for data files ({STAMP})", sha)
            print(f"  LICENSE       {'OK @ '+c if not err else 'ERROR '+err}")
            ok = ok and not err

    # 2) licenses/GPL-3.0.txt = GPL-3.0 (subdir: not seen by GitHub's detector)
    sha, text = get_file(repo, CODE_LICENSE_PATH)
    if text and "GNU GENERAL PUBLIC LICENSE" in text and "Version 3" in text:
        print(f"  {CODE_LICENSE_PATH}  SKIP (already GPL-3.0)")
    elif dry:
        print(f"  {CODE_LICENSE_PATH}  would {'replace' if sha else 'add'} GPL-3.0")
    else:
        c, err = put_file(repo, CODE_LICENSE_PATH, GPL, branch,
                          f"Add GPL-3.0 for source code ({STAMP})", sha)
        print(f"  {CODE_LICENSE_PATH}  {'OK @ '+c if not err else 'ERROR '+err}")
        ok = ok and not err

    # 3) README "## License" section (append once)
    sha, text = get_file(repo, "README.md")
    if text is None:
        if dry:
            print("  README.md     would CREATE with License section")
        else:
            c, err = put_file(repo, "README.md",
                              f"# {repo}\n{README_SECTION}", branch,
                              f"Add License section ({STAMP})")
            print(f"  README.md     {'CREATED @ '+c if not err else 'ERROR '+err}")
            ok = ok and not err
    elif "LICENSE-CODE" in text:
        # stale section from the earlier (broken) layout — repoint to the subdir
        if dry:
            print("  README.md     would FIX stale LICENSE-CODE link")
        else:
            fixed = text.replace("[`LICENSE-CODE`](LICENSE-CODE)",
                                 "[`licenses/GPL-3.0.txt`](licenses/GPL-3.0.txt)")
            fixed = fixed.replace("LICENSE-CODE", "licenses/GPL-3.0.txt")
            c, err = put_file(repo, "README.md", fixed, branch,
                              f"Fix code-license link ({STAMP})", sha)
            print(f"  README.md     {'FIXED @ '+c if not err else 'ERROR '+err}")
            ok = ok and not err
    elif "## License" in text or "## Licensing" in text:
        print("  README.md     SKIP (already has a License section)")
    elif dry:
        print("  README.md     would append License section")
    else:
        new = text.rstrip() + "\n" + README_SECTION
        c, err = put_file(repo, "README.md", new, branch,
                          f"Add License section ({STAMP})", sha)
        print(f"  README.md     {'OK @ '+c if not err else 'ERROR '+err}")
        ok = ok and not err
    return ok


def main():
    global CC, GPL
    ap = argparse.ArgumentParser()
    ap.add_argument("repos", nargs="+")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    CC = license_text("cc-by-sa-4.0")
    GPL = license_text("gpl-3.0")
    print(f"Dual layout: LICENSE=CC-BY-SA-4.0 + {CODE_LICENSE_PATH}=GPL-3.0 + README note"
          f"{'  [DRY-RUN]' if args.dry_run else ''}\n")
    ok_all = True
    for spec in args.repos:
        repo, _, br = spec.partition(":")
        ok_all = do_repo(repo, args.dry_run, branch=br or None) and ok_all
        print()
    if not ok_all:
        sys.exit(1)


if __name__ == "__main__":
    main()
