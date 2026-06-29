#!/usr/bin/env python3
"""Fingerprint the existing LICENSE of NOASSERTION repos so a human can decide
whether each is an intentional custom license or malformed-but-standard text
safe to replace with the canonical RH1 license.

Read-only: makes no changes.
"""
import base64
import hashlib
import json
import subprocess
import sys

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

OWNER = "sanskrit-lexicon"

CODE = ["csl-pywork", "csl-websanlexicon"]
DICT = ["AP", "ApteES", "BOP", "BOR", "BUR", "DCS", "FRI", "GRA", "INM", "MD",
        "MW72", "MWS", "PWG", "PWK", "SCH", "VCP", "Wil-YAT"]
SOURCE = ["csl-orig"]


def gh(path, jq=None):
    args = ["gh", "api", path]
    if jq:
        args += ["--jq", jq]
    r = subprocess.run(args, capture_output=True, encoding="utf-8")
    return r.returncode, r.stdout, r.stderr


def classify(text):
    t = text.lower()
    if "gnu general public license" in t and "version 3" in t:
        return "GPL-3.0-like"
    if "gnu general public license" in t and "version 2" in t:
        return "GPL-2.0-like"
    if "gnu general public license" in t:
        return "GPL-unspecified"
    if "creative commons" in t and "attribution-sharealike" in t and "4.0" in t:
        return "CC-BY-SA-4.0-like"
    if "creative commons" in t and "attribution" in t and "4.0" in t:
        return "CC-BY-4.0-like"
    if "creative commons" in t:
        return "CC-other"
    if "permission is hereby granted, free of charge" in t:
        return "MIT-like"
    if "apache license" in t:
        return "Apache-like"
    return "CUSTOM/UNKNOWN"


def inspect(repo):
    code, out, err = gh(f"repos/{OWNER}/{repo}/license")
    if code != 0:
        return repo, None, "(no license endpoint / not found)", 0, "", ""
    j = json.loads(out)
    name = j.get("name", "?")
    spdx = (j.get("license") or {}).get("spdx_id", "?")
    raw = base64.b64decode(j.get("content", "")).decode("utf-8", "replace")
    sha = hashlib.sha256(raw.encode("utf-8", "replace")).hexdigest()[:10]
    lines = [ln.strip() for ln in raw.splitlines() if ln.strip()]
    head = " / ".join(lines[:3])[:160]
    return repo, name, head, len(raw), classify(raw), sha


def main():
    groups = [("CODE/TOOLING", CODE), ("DICTIONARY", DICT), ("SOURCE", SOURCE)]
    by_sha = {}
    for label, repos in groups:
        print(f"\n===== {label} =====")
        for repo in repos:
            r, name, head, size, kind, sha = inspect(repo)
            by_sha.setdefault(sha, []).append(r)
            print(f"\n{r}  [file={name}, spdx=detected-NOASSERTION, {size}B, "
                  f"sha={sha}]")
            print(f"  classify: {kind}")
            print(f"  head: {head}")
    print("\n===== identical-text clusters (same sha) =====")
    for sha, repos in sorted(by_sha.items(), key=lambda kv: -len(kv[1])):
        if len(repos) > 1:
            print(f"  {sha}: {', '.join(repos)}")


if __name__ == "__main__":
    main()
