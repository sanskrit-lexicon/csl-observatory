#!/usr/bin/env python3
"""
Enrich CITATION.cff in all 35 dictionary repos with publication-year + author
data from the canonical inventory CSV.

Reads: data/dictionary_inventory.csv
Writes: CITATION.cff in each dict repo with year + author embedded.

For each dict, also adds a "preferred-citation" entry that cites the printed
source the dict digitises.
"""

import subprocess
import sys
import csv
import base64
import tempfile
import os
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

ORG = "sanskrit-lexicon"
REPO_ROOT = Path(__file__).parent.parent
INVENTORY = REPO_ROOT / "data" / "dictionary_inventory.csv"

DICT_REPOS = [
    "PWG", "PWK", "MWS", "MD", "AP", "AP90", "GRA", "FRI",
    "SCH", "DCS", "VCP", "ApteES", "SKD", "MCI", "CORRECTIONS", "WIL",
    "BHS", "VEI", "ACC", "KRM", "BUR", "CAE", "CCS", "STC", "BEN",
    "BOR", "INM", "BOP", "LRV", "AMAR", "SHS", "KNA", "KOW", "PUI"
]
# csl-observatory excluded (not a dict per se)

def gh(*args, timeout=60):
    try:
        r = subprocess.run(["gh"] + list(args),
                          capture_output=True, text=True, timeout=timeout, encoding='utf-8')
        return r.stdout.strip(), r.returncode == 0
    except Exception as e:
        return str(e), False

def get_default_branch(repo):
    out, ok = gh("api", f"repos/{ORG}/{repo}", "--jq", ".default_branch")
    return out if ok and out else "master"

def push_file(repo, filepath, content, message, branch):
    sha_out, ok = gh("api", f"repos/{ORG}/{repo}/contents/{filepath}", "--jq", ".sha")
    sha = sha_out if ok and sha_out and len(sha_out) > 10 and not sha_out.startswith('{') else None

    with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', suffix='.txt', delete=False) as f:
        b64 = base64.b64encode(content.encode('utf-8')).decode('utf-8')
        f.write(b64)
        temp_path = f.name

    try:
        args = ["api", f"repos/{ORG}/{repo}/contents/{filepath}", "-X", "PUT",
                "-F", f"message={message}",
                "-F", f"content=@{temp_path}",
                "-F", f"branch={branch}"]
        if sha:
            args.extend(["-F", f"sha={sha}"])
        out, _ = gh(*args)
        return '"sha"' in out and '"path"' in out
    finally:
        try: os.unlink(temp_path)
        except: pass

def parse_authors(author_str):
    """Parse 'V.S. Apte (rev. P.K. Gode et al.)' or 'Böhtlingk + Roth' into list."""
    if not author_str or author_str == "?" or author_str == "community":
        return []
    # Remove parenthetical notes
    base = author_str.split('(')[0].strip()
    # Split on +, &, "and"
    import re
    names = re.split(r'[+&]| and ', base)
    return [n.strip() for n in names if n.strip()]

def make_cff(code, year, full_name, language_pair, author_str, notes):
    """Generate enriched CITATION.cff content."""
    authors_list = parse_authors(author_str)

    cff = "cff-version: 1.2.0\n"
    cff += "type: dataset\n"
    cff += f"title: {full_name}\n"
    cff += "message: If you use this dataset, please cite both the digital edition and the printed source it digitises.\n"
    cff += "license: CC-BY-SA-4.0\n"
    cff += f"repository-code: https://github.com/{ORG}/{code}\n"
    if year and str(year) != "n/a":
        cff += f"date-released: {year}-01-01\n"
    cff += "version: 1.0.0\n"
    cff += "keywords:\n"
    cff += "  - sanskrit\n"
    cff += "  - lexicon\n"
    cff += "  - cdsl\n"
    cff += "  - cologne-digital-sanskrit-lexicon\n"
    cff += "  - dictionary\n"
    cff += f"  - {language_pair.lower()}\n"
    cff += "authors:\n"
    cff += "  - name: \"Cologne Digital Sanskrit Lexicon project contributors\"\n"
    cff += "    website: https://www.sanskrit-lexicon.uni-koeln.de/\n"

    if authors_list:
        cff += "preferred-citation:\n"
        cff += "  type: book\n"
        cff += f"  title: {full_name}\n"
        if year and str(year) != "n/a":
            cff += f"  year: {year}\n"
        cff += "  authors:\n"
        for name in authors_list:
            # Try to split family / given
            parts = name.split()
            if len(parts) == 1:
                cff += f"    - family-names: \"{parts[0]}\"\n"
            else:
                given = " ".join(parts[:-1])
                family = parts[-1]
                cff += f"    - family-names: \"{family}\"\n"
                cff += f"      given-names: \"{given}\"\n"
        if notes:
            # Strip CSV escaping from notes
            cff += f"  notes: \"{notes}\"\n"

    return cff

def main():
    print(f"\n{'='*60}")
    print(f"ENRICHING CITATION.cff for 35 dict repos")
    print(f"Source: {INVENTORY}")
    print(f"{'='*60}\n")

    # Load inventory
    inv = {}
    with open(INVENTORY, encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            code = row['code']
            inv[code] = row

    success = 0
    failed = []
    for repo in DICT_REPOS:
        if repo not in inv:
            print(f"  ✗ {repo}: not in inventory CSV")
            failed.append(repo)
            continue

        row = inv[repo]
        year = row['year']
        full_name = row['full_name']
        lang_pair = row['language_pair']
        author = row['author_or_compiler']
        notes = row['notes']

        cff = make_cff(repo, year, full_name, lang_pair, author, notes)

        branch = get_default_branch(repo)

        if push_file(repo, "CITATION.cff", cff,
                    f"docs(cff): enrich with publication-year + author from inventory ({year}, {author[:40]})",
                    branch):
            print(f"  ✓ {repo} ({year}, {author[:50]})")
            success += 1
        else:
            print(f"  ✗ {repo}")
            failed.append(repo)

    print(f"\n{'='*60}")
    print(f"COMPLETE: {success}/{len(DICT_REPOS)} repos enriched")
    if failed:
        print(f"Failed: {', '.join(failed)}")
    print(f"{'='*60}\n")

if __name__ == "__main__":
    main()
