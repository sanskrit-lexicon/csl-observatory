#!/usr/bin/env python3
"""
Contributor specialisation study.

Reads:  data/contributors.csv  (login, repo, contributions, type)
        data/dictionary_inventory.csv  (code, family)

Computes per-contributor:
  - n_repos: # of distinct repos contributed to
  - total_commits: sum of contributions across repos
  - shannon_entropy: Shannon entropy of repo-distribution (high = spread out, low = focused)
  - top_repo: most-committed-to repo
  - dominant_family: language family with most commits (German / English / Russian / Skt-Skt / Specialised / Tooling)

Plus heatmap data: contributor x repo commit counts.

Output:
  - data/contributor_specialisation.csv
  - data/contributor_repo_heatmap.csv
"""

import sys
import csv
import math
from pathlib import Path
from collections import defaultdict

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

REPO_ROOT = Path(__file__).parent.parent
DATA = REPO_ROOT / "data"

# Load inventory family mapping
inv = {}
try:
    with open(DATA / "dictionary_inventory.csv", encoding='utf-8') as f:
        for row in csv.DictReader(f):
            inv[row['code']] = row.get('family', 'Unknown')
except FileNotFoundError:
    pass

# Tooling repos (mapped to "Tooling" family)
TOOLING_REPOS = {
    "COLOGNE", "csl-apidev", "csl-app", "csl-corrections", "csl-devanagari",
    "csl-doc", "csl-homepage", "csl-inflect", "csl-json", "csl-kale",
    "csl-ldev", "csl-lnum", "csl-lslink", "csl-newsletter", "csl-orig",
    "csl-pywork", "csl-sqlite", "csl-websanlexicon", "csl-westergaard",
    "csl-whitroot", "csl-observatory",
    "alternateheadwords", "avlinks", "rvlinks", "literarysource",
    "hwnorm1", "hwnorm2", "MWinflect", "mw-dev",
    "cologne-stardict", "cologne-hugo", "sanskrit-fonts",
    "sanskrit-lexicon.github.io", "santamlegacy",
    "GreekInSanskrit", "ArabicInSanskrit"
}

def repo_family(repo):
    if repo in TOOLING_REPOS:
        return "Tooling"
    if repo == "FRI":
        return "Specialized"  # Frish reader
    return inv.get(repo, "Unknown")

def main():
    # Load contributors
    contribs = []
    with open(DATA / "contributors.csv", encoding='utf-8') as f:
        for row in csv.DictReader(f):
            try:
                row['contributions'] = int(row['contributions'])
            except (ValueError, KeyError):
                continue
            if row.get('type') == 'Bot':
                continue
            contribs.append(row)

    print(f"Loaded {len(contribs)} (login, repo) pairs")

    # Per-contributor aggregation
    by_login = defaultdict(list)
    for c in contribs:
        by_login[c['login']].append(c)

    print(f"Distinct contributors: {len(by_login)}")

    # Compute per-contributor metrics
    rows = []
    for login, cs in by_login.items():
        n_repos = len(cs)
        total = sum(c['contributions'] for c in cs)
        if total == 0:
            continue

        # Shannon entropy of commit distribution
        probs = [c['contributions'] / total for c in cs if c['contributions'] > 0]
        H = -sum(p * math.log2(p) for p in probs if p > 0)

        # Top repo
        top = max(cs, key=lambda c: c['contributions'])

        # Family breakdown
        fam_commits = defaultdict(int)
        for c in cs:
            fam_commits[repo_family(c['repo'])] += c['contributions']
        dominant = max(fam_commits.items(), key=lambda x: x[1]) if fam_commits else ("Unknown", 0)
        fam_share = dominant[1] / total if total > 0 else 0

        rows.append({
            'login': login,
            'n_repos': n_repos,
            'total_commits': total,
            'shannon_entropy': round(H, 3),
            'max_entropy': round(math.log2(n_repos), 3) if n_repos > 1 else 0,
            'normalized_entropy': round(H / math.log2(n_repos), 3) if n_repos > 1 else 0,
            'top_repo': top['repo'],
            'top_repo_commits': top['contributions'],
            'top_repo_share': round(top['contributions'] / total, 3),
            'dominant_family': dominant[0],
            'dominant_family_commits': dominant[1],
            'dominant_family_share': round(fam_share, 3),
        })

    # Sort by total commits desc
    rows.sort(key=lambda r: -r['total_commits'])

    out_path = DATA / "contributor_specialisation.csv"
    with open(out_path, 'w', encoding='utf-8', newline='') as f:
        w = csv.DictWriter(f, fieldnames=rows[0].keys())
        w.writeheader()
        for r in rows:
            w.writerow(r)
    print(f"\n✓ {out_path}")

    # Heatmap: contributor x repo (only top-15 contributors x repos with >0 contributions)
    top15 = [r['login'] for r in rows[:15]]
    heatmap = []
    for c in contribs:
        if c['login'] in top15:
            heatmap.append({
                'login': c['login'],
                'repo': c['repo'],
                'family': repo_family(c['repo']),
                'commits': c['contributions']
            })

    heat_path = DATA / "contributor_repo_heatmap.csv"
    with open(heat_path, 'w', encoding='utf-8', newline='') as f:
        w = csv.DictWriter(f, fieldnames=['login', 'repo', 'family', 'commits'])
        w.writeheader()
        for r in heatmap:
            w.writerow(r)
    print(f"✓ {heat_path}")

    # Print summary
    print(f"\n{'='*70}")
    print(f"Top 10 contributors by reach (n_repos) and concentration (entropy)")
    print(f"{'='*70}")
    print(f"{'Login':<25} {'Repos':>5} {'Commits':>10} {'Entropy':>8} {'Norm':>6} {'Dominant family':<25} {'Share':>6}")
    for r in rows[:10]:
        print(f"  {r['login']:<23} {r['n_repos']:>5} {r['total_commits']:>10} "
              f"{r['shannon_entropy']:>8.2f} {r['normalized_entropy']:>6.2f} "
              f"{r['dominant_family']:<25} {r['dominant_family_share']:>6.2f}")

    print(f"\n=== Family-focus distribution ===")
    family_counts = defaultdict(int)
    for r in rows:
        family_counts[r['dominant_family']] += 1
    for fam, n in sorted(family_counts.items(), key=lambda x: -x[1]):
        print(f"  {fam}: {n} contributors")

if __name__ == "__main__":
    main()
