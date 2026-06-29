#!/usr/bin/env python3
"""Robustly create/update a text file in an org repo via the GitHub contents
API (retries reads; rechecks live content after a failed PUT so a timed-out
write can't double-apply). Used to add NOTICE files for third-party assets.

Usage:
  python scripts/rh1_put_file.py REPO:BRANCH DEST_PATH --from local.txt -m "msg"
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


def get_file(repo, path):
    code, out = gh([f"repos/{OWNER}/{repo}/contents/{path}",
                    "--jq", "{sha:.sha, content:.content}"])
    if code != 0:
        return None, None
    j = json.loads(out)
    return j.get("sha"), base64.b64decode(j.get("content", "")).decode("utf-8", "replace")


def put(repo, path, text, branch, message, sha=None, tries=4):
    b64 = base64.b64encode(text.encode("utf-8")).decode("ascii")
    last = "unknown"
    for i in range(tries):
        payload = {"message": message, "content": b64, "branch": branch}
        if sha:
            payload["sha"] = sha
        r = subprocess.run(
            ["gh", "api", "--method", "PUT",
             f"repos/{OWNER}/{repo}/contents/{path}", "--input", "-"],
            input=json.dumps(payload), capture_output=True, encoding="utf-8")
        if r.returncode == 0:
            return json.loads(r.stdout)["commit"]["sha"][:8], None
        last = (r.stderr or "").strip()[:160]
        time.sleep(3 * (i + 1))
        cur_sha, cur_text = get_file(repo, path)
        if cur_text is not None and cur_text == text:
            return "verified", None
        if cur_sha:
            sha = cur_sha
    return None, last


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("repo")          # REPO or REPO:BRANCH
    ap.add_argument("dest")          # path in the repo
    ap.add_argument("--from", dest="src", required=True)
    ap.add_argument("-m", "--message", required=True)
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    repo, _, branch = args.repo.partition(":")
    if not branch:
        _, br = gh([f"repos/{OWNER}/{repo}", "--jq", ".default_branch"])
        branch = br.strip()
    with open(args.src, encoding="utf-8") as f:
        text = f.read()
    sha, existing = get_file(repo, args.dest)
    if existing == text:
        print(f"{repo}: {args.dest} SKIP (already identical)")
        return
    if args.dry_run:
        print(f"{repo}: would {'update' if sha else 'create'} {args.dest} on {branch}")
        return
    out, err = put(repo, args.dest, text, branch, args.message, sha)
    print(f"{repo}: {args.dest} {'OK @ '+out if not err else 'ERROR '+err}")
    if err:
        sys.exit(1)


if __name__ == "__main__":
    main()
