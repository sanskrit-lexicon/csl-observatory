#!/usr/bin/env python3
"""Bus-factor & contributor-concentration analysis for the sanskrit-lexicon org.

Operates offline on the already-extracted observatory data
(`observatory/site/src/data/contributors.csv` and `repos.csv`) — no GitHub
calls, fully reproducible. Complements `contributor_stats.py` (which is the
live-API leaderboard) by quantifying *risk*: how concentrated the work is and
how many repositories depend on a single person.

Definitions
-----------
* **Bus factor (per repo)** — the smallest number of contributors whose summed
  contributions exceed 50 % of that repo's total. A bus factor of 1 means a
  single person accounts for the majority of work — a single point of failure.
* **Top share** — the largest single contributor's fraction of a repo's total.
* **Gini** — inequality of the org-wide per-person contribution distribution
  (0 = perfectly even, 1 = one person does everything).

Outputs
-------
* `reports/bus_factor.md`                       — human-readable finding
* `observatory/site/src/data/bus_factor.csv`    — per-repo metrics for the site

Usage:  python scripts/bus_factor.py
"""
import csv, os, sys
from collections import defaultdict
sys.stdout.reconfigure(encoding='utf-8'); sys.stderr.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DATA = os.path.join(ROOT, 'observatory', 'site', 'src', 'data')
CONTRIB = os.path.join(DATA, 'contributors.csv')
REPOS = os.path.join(DATA, 'repos.csv')
PEOPLE = os.path.join(DATA, 'people_summary.csv')
OUT_MD = os.path.join(ROOT, 'reports', 'bus_factor.md')
OUT_CSV = os.path.join(DATA, 'bus_factor.csv')

# The three core maintainers, by GitHub login.
CORE = ['funderburkjim', 'drdhaval2785', 'gasyoun']


def load_contrib():
    """repo -> {login: contributions}, and is-bot flag per login."""
    per_repo = defaultdict(dict)
    is_bot = {}
    with open(CONTRIB, encoding='utf-8') as f:
        for row in csv.DictReader(f):
            login = row['login']
            n = int(row['contributions'])
            per_repo[row['repo']][login] = per_repo[row['repo']].get(login, 0) + n
            is_bot[login] = (row['type'].strip().lower() == 'bot')
    return per_repo, is_bot


def bus_factor(shares):
    """shares: list of contribution counts (any order). Returns (bf, top_share)."""
    s = sorted(shares, reverse=True)
    total = sum(s)
    if total == 0:
        return 0, 0.0
    cum = 0
    bf = 0
    for v in s:
        cum += v
        bf += 1
        if cum * 2 > total:        # strictly more than 50 %
            break
    return bf, s[0] / total


def gini(values):
    v = sorted(x for x in values if x > 0)
    n = len(v)
    if n == 0:
        return 0.0
    cum = 0
    for i, x in enumerate(v, 1):
        cum += i * x
    return (2 * cum) / (n * sum(v)) - (n + 1) / n


def load_repo_meta():
    meta = {}
    if os.path.exists(REPOS):
        with open(REPOS, encoding='utf-8') as f:
            for row in csv.DictReader(f):
                meta[row['repo']] = row
    return meta


def main():
    per_repo, is_bot = load_contrib()
    meta = load_repo_meta()

    # Per-repo metrics (human contributors only — bots aren't a continuity risk).
    rows = []
    for repo, d in per_repo.items():
        humans = {k: v for k, v in d.items() if not is_bot.get(k)}
        if not humans:
            continue
        bf, top = bus_factor(humans.values())
        top_login = max(humans, key=humans.get)
        rows.append({
            'repo': repo,
            'contributors': len(humans),
            'total_contributions': sum(humans.values()),
            'bus_factor': bf,
            'top_login': top_login,
            'top_share': round(top, 4),
        })
    rows.sort(key=lambda r: (r['bus_factor'], -r['top_share']))

    # Org-wide person totals.
    person_total = defaultdict(int)
    person_repos = defaultdict(int)
    for repo, d in per_repo.items():
        for login, n in d.items():
            if is_bot.get(login):
                continue
            person_total[login] += n
            person_repos[login] += 1
    grand = sum(person_total.values())
    g = gini(person_total.values())

    bf1 = [r for r in rows if r['bus_factor'] == 1]
    solo = [r for r in rows if r['contributors'] == 1]
    core_total = sum(person_total[c] for c in CORE)

    # Concentration: how many people for 50 % / 80 % / 90 % of all contributions.
    ranked = sorted(person_total.values(), reverse=True)
    def people_for(frac):
        cum = 0
        for i, v in enumerate(ranked, 1):
            cum += v
            if cum >= frac * grand:
                return i
        return len(ranked)

    # Identity gap from people_summary.
    n_people = n_missing_orcid = 0
    if os.path.exists(PEOPLE):
        with open(PEOPLE, encoding='utf-8') as f:
            for row in csv.DictReader(f):
                if not row['login']:
                    continue
                n_people += 1
                if not row['orcid'].strip():
                    n_missing_orcid += 1

    # ---- write per-repo CSV ----
    with open(OUT_CSV, 'w', encoding='utf-8', newline='') as f:
        w = csv.DictWriter(f, fieldnames=['repo', 'contributors', 'total_contributions',
                                          'bus_factor', 'top_login', 'top_share'])
        w.writeheader()
        for r in rows:
            w.writerow(r)

    # ---- write report ----
    L = []; A = L.append
    A('# Bus factor & contributor concentration')
    A('')
    A('_Generated by `scripts/bus_factor.py` from `observatory/site/src/data/'
      'contributors.csv` (offline, reproducible). Bots excluded from continuity'
      ' risk; contributions = GitHub commit-contribution counts per repo._')
    A('')
    A('## Headline')
    A('')
    A('| Metric | Value |')
    A('|---|---:|')
    A(f'| Repositories with human contributors | {len(rows)} |')
    A(f'| Distinct human contributors | {len(person_total)} |')
    A(f'| **Repos with bus factor = 1** | **{len(bf1)} / {len(rows)}** ({100*len(bf1)//len(rows)}%) |')
    A(f'| Repos with a single contributor | {len(solo)} |')
    A(f'| Gini of contribution distribution | {g:.3f} |')
    A(f'| People for 50% / 80% / 90% of all work | {people_for(0.5)} / {people_for(0.8)} / {people_for(0.9)} |')
    A(f'| Core trio share (funderburkjim, drdhaval2785, gasyoun) | {100*core_total/grand:.1f}% |')
    A(f'| Contributors missing an ORCID | {n_missing_orcid} / {n_people} |')
    A('')
    A('## Org-wide contributor concentration')
    A('')
    A('| Contributor | Total contributions | Share | Repos touched |')
    A('|---|---:|---:|---:|')
    for login, n in sorted(person_total.items(), key=lambda kv: -kv[1]):
        A(f'| {login} | {n:,} | {100*n/grand:.1f}% | {person_repos[login]} |')
    A('')
    A('## Single-point-of-failure repositories (bus factor = 1)')
    A('')
    A('Repositories where one person accounts for more than half of all '
      'contributions. Sorted by that person\'s share (highest risk first).')
    A('')
    A('| Repository | Top contributor | Top share | Contributors | Total |')
    A('|---|---|---:|---:|---:|')
    for r in sorted(bf1, key=lambda r: -r['top_share']):
        A(f'| {r["repo"]} | {r["top_login"]} | {100*r["top_share"]:.0f}% | '
          f'{r["contributors"]} | {r["total_contributions"]:,} |')
    A('')
    A('## All repositories by bus factor')
    A('')
    A('| Repository | Bus factor | Contributors | Top contributor | Top share |')
    A('|---|---:|---:|---|---:|')
    for r in rows:
        A(f'| {r["repo"]} | {r["bus_factor"]} | {r["contributors"]} | '
          f'{r["top_login"]} | {100*r["top_share"]:.0f}% |')
    A('')
    A('## Reading')
    A('')
    A(f'- The ecosystem is highly centralised: **{people_for(0.5)} '
      f'{"person" if people_for(0.5)==1 else "people"} account{"s" if people_for(0.5)==1 else ""} '
      f'for half of all recorded contributions**, and the core trio carries '
      f'{100*core_total/grand:.0f}% of the total. A Gini of {g:.2f} confirms a '
      'long tail of one-off contributors behind a tiny active core.')
    A(f'- **{len(bf1)} of {len(rows)} repositories have a bus factor of 1** — a '
      'single maintainer could be lost and the majority of that repo\'s history '
      'has no second author. These are the continuity-risk repos to prioritise '
      'for documentation and onboarding.')
    A(f'- Identity metadata is unfilled: **{n_missing_orcid} of {n_people} '
      'contributors have no ORCID**, limiting scholarly-credit attribution for '
      'this digitisation work.')
    A('')
    A('*Object of analysis: GitHub contributors and repositories — in scope per '
      '`docs/BOUNDARY_RULES.md`.*')

    with open(OUT_MD, 'w', encoding='utf-8', newline='\n') as f:
        f.write('\n'.join(L) + '\n')

    print(f'wrote {OUT_MD}')
    print(f'wrote {OUT_CSV}')
    print(f'  repos with human contributors: {len(rows)}')
    print(f'  bus factor = 1: {len(bf1)}  ({100*len(bf1)//len(rows)}%)')
    print(f'  Gini: {g:.3f}   core trio share: {100*core_total/grand:.1f}%')
    print(f'  people for 50/80/90%: {people_for(0.5)}/{people_for(0.8)}/{people_for(0.9)}')


if __name__ == '__main__':
    main()
