#!/usr/bin/env python3
"""Generate docs/CONTRIBUTOR_STATS.md — org-wide contributor & work statistics
for the sanskrit-lexicon GitHub org.

Data sources:
  * Commits, tenure, time-series  -> GitHub REST `GET /repos/{o}/{r}/commits`
    (paginated, default branch) for every non-fork org repo.
  * Issues & PRs (by opener)      -> issues API (state=all).
  * Line churn                    -> local `git log --numstat`, for whichever
    org repos are present as sibling clones next to csl-observatory.

Why git for churn: GitHub's `/stats/contributors` and `/stats/code_frequency`
endpoints are computed asynchronously and frequently return HTTP 202 for an
extended period across a 77-repo burst, so they are not relied on here.

Usage:  python scripts/contributor_stats.py      (requires an authenticated `gh`)
"""
import subprocess, json, os, sys, re
from collections import defaultdict
from datetime import datetime, timezone
sys.stdout.reconfigure(encoding='utf-8'); sys.stderr.reconfigure(encoding='utf-8')

ORG = 'sanskrit-lexicon'
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)            # csl-observatory/
SIB = os.path.dirname(ROOT)             # parent holding sibling clones
OUT = os.path.join(ROOT, 'docs', 'CONTRIBUTOR_STATS.md')

# Consolidate git author names that have no linked GitHub account.
ALIAS = {
    'funderburkjim': 'funderburkjim', 'Jim Funderburk': 'funderburkjim', 'James Funderburk': 'funderburkjim',
    'Dhaval Patel': 'drdhaval2785', 'Dhavalkumar Patel': 'drdhaval2785', 'drdhaval2785': 'drdhaval2785',
    'Mārcis Gasūns': 'gasyoun', 'Marcis Gasuns': 'gasyoun', 'gasyoun': 'gasyoun',
    'AnnaRybakovaT': 'AnnaRybakovaT', 'Andhrabharati': 'Andhrabharati',
}

def gh(p):
    return subprocess.run(['gh', 'api', p], capture_output=True, encoding='utf-8')

def who_of(login, name):
    if login:
        return login
    return ALIAS.get((name or '').strip(), 'name:' + (name or '?'))

def list_repos():
    r = subprocess.run(['gh', 'api', '--paginate', f'orgs/{ORG}/repos?per_page=100'],
                       capture_output=True, encoding='utf-8')
    return [x for x in json.loads(r.stdout) if not x['fork']]

def fetch_commits(repo, br):
    rows = []
    for page in range(1, 61):
        r = gh(f'repos/{ORG}/{repo}/commits?sha={br}&per_page=100&page={page}')
        try:
            j = json.loads(r.stdout or '[]')
        except Exception:
            break
        if not isinstance(j, list) or not j:
            break
        for c in j:
            ca = (c.get('commit') or {}).get('author') or {}
            rows.append([who_of((c.get('author') or {}).get('login'), ca.get('name')), ca.get('date')])
        if len(j) < 100:
            break
    return rows

def fetch_issues(repo):
    r = subprocess.run(['gh', 'api', '--paginate', f'repos/{ORG}/{repo}/issues?state=all&per_page=100'],
                       capture_output=True, encoding='utf-8')
    out = []
    try:
        for it in json.loads(r.stdout or '[]'):
            out.append((it.get('user', {}).get('login') if it.get('user') else None,
                        it['created_at'], 'pull_request' in it))
    except Exception:
        pass
    return out

def git_churn(path):
    r = subprocess.run(['git', '-C', path, 'log', '--no-merges', '--numstat', '--date=short',
                        '--format=C|%H|%an|%ad'], capture_output=True, encoding='utf-8', errors='replace')
    per = defaultdict(lambda: {'commits': 0, 'add': 0, 'del': 0, 'files': 0})
    cur = None
    for line in r.stdout.splitlines():
        if line.startswith('C|'):
            _, _h, an, _ad = line.split('|', 3)
            cur = ALIAS.get(an.strip(), an.strip()); per[cur]['commits'] += 1
        elif line.strip() and cur:
            p = line.split('\t')
            if len(p) == 3:
                per[cur]['add'] += int(p[0]) if p[0].isdigit() else 0
                per[cur]['del'] += int(p[1]) if p[1].isdigit() else 0
                per[cur]['files'] += 1
    return per

def pie(title, pairs, topn=12):
    pairs = sorted([(k, v) for k, v in pairs if v > 0], key=lambda x: -x[1])
    out = ['```mermaid', 'pie showData', f'  title {title}']
    for k, v in pairs[:topn]:
        out.append(f'  "{str(k)[:40]}" : {v}')
    rest = sum(v for _, v in pairs[topn:])
    if rest:
        out.append(f'  "others ({len(pairs)-topn} more)" : {rest}')
    out.append('```'); return '\n'.join(out)

def disp(w):
    return w[5:] + ' *(no GH acct)*' if w.startswith('name:') else w

def main():
    repos = list_repos()
    auth = defaultdict(lambda: {'c': 0, 'repos': set(), 'months': set(), 'first': None, 'last': None, 'by_year': defaultdict(int)})
    org_year = defaultdict(lambda: {'c': 0, 'iss': 0, 'pr': 0})
    grid = defaultdict(lambda: defaultdict(int))
    repo_sum = {}; issue_auth = defaultdict(lambda: {'iss': 0, 'pr': 0})
    churn = {}; all_dates = []; tot_iss = tot_pr = 0
    for i, rp in enumerate(repos, 1):
        name, br = rp['name'], rp['default_branch']
        cms = fetch_commits(name, br)
        rc = 0; ra = set(); rf = rl = None
        for who, date in cms:
            if not date:
                continue
            y = int(date[:4]); m = int(date[5:7])
            auth[who]['c'] += 1; auth[who]['repos'].add(name); auth[who]['months'].add(date[:7]); auth[who]['by_year'][y] += 1
            auth[who]['first'] = date if auth[who]['first'] is None else min(auth[who]['first'], date)
            auth[who]['last'] = date if auth[who]['last'] is None else max(auth[who]['last'], date)
            org_year[y]['c'] += 1; grid[y][m] += 1; rc += 1; ra.add(who); rf = date if rf is None else min(rf, date); rl = date if rl is None else max(rl, date); all_dates.append(date)
        ic = pc = 0
        for u, created, is_pr in fetch_issues(name):
            u = u or '(unknown)'; y = int(created[:4])
            if is_pr: pc += 1; issue_auth[u]['pr'] += 1; org_year[y]['pr'] += 1
            else: ic += 1; issue_auth[u]['iss'] += 1; org_year[y]['iss'] += 1
        tot_iss += ic; tot_pr += pc
        repo_sum[name] = {'c': rc, 'authors': len(ra), 'first': rf, 'last': rl, 'iss': ic, 'pr': pc}
        sib = os.path.join(SIB, name)
        if os.path.isdir(os.path.join(sib, '.git')):
            shallow = subprocess.run(['git', '-C', sib, 'rev-parse', '--is-shallow-repository'],
                                     capture_output=True, encoding='utf-8').stdout.strip()
            if shallow == 'false':            # full clones only — shallow shells give misleading churn
                churn[name] = git_churn(sib)
        print(f'[{i}/{len(repos)}] {name}: {rc} commits, {ic} issues, {pc} PRs', flush=True)

    tot_c = sum(a['c'] for a in auth.values())
    span = f"{min(all_dates)[:7]} – {max(all_dates)[:7]}" if all_dates else 'n/a'
    gen = datetime.now(tz=timezone.utc).strftime('%Y-%m-%d')
    L = []; A = L.append
    A('# Sanskrit Lexicon — Contributor & Work Statistics'); A('')
    A(f'_Generated {gen} across the **{len(repos)} non-fork repositories** of the [`sanskrit-lexicon`](https://github.com/sanskrit-lexicon) org. Commit & issue data from the GitHub API; line-churn from local git for {len(churn)} locally-cloned repos (see Methodology)._'); A('')
    A('## Overview'); A('')
    A('| Metric | Value |'); A('|---|---:|')
    A(f'| Repositories analyzed | {len(repos)} |'); A(f'| Distinct commit authors | {len(auth)} |')
    A(f'| Total commits | {tot_c:,} |'); A(f'| Issues opened | {tot_iss:,} |'); A(f'| Pull requests opened | {tot_pr:,} |')
    A(f'| Activity span | {span} |'); A('')
    A('## Commits & issues by year (org-wide)'); A(''); A('| Year | Commits | Issues opened | PRs opened |'); A('|---|---:|---:|---:|')
    for y in sorted(org_year):
        o = org_year[y]; A(f'| {y} | {o["c"]:,} | {o["iss"]:,} | {o["pr"]:,} |')
    A(''); A(pie('Commits by year', [(str(y), org_year[y]['c']) for y in sorted(org_year)], 25)); A('')
    A('## Commit-activity grid (commits per month)'); A(''); A('| Year | Jan | Feb | Mar | Apr | May | Jun | Jul | Aug | Sep | Oct | Nov | Dec | Total |'); A('|---|' + '---:|' * 13)
    for y in sorted(grid):
        A(f'| {y} | ' + ' | '.join(str(grid[y].get(m, 0)) for m in range(1, 13)) + f' | {sum(grid[y].values())} |')
    A('')
    A('## Contributor leaderboard (all-time, by commits)'); A(''); A('| Contributor | Commits | Repos | First | Last | Active months |'); A('|---|---:|---:|---|---|---:|')
    for w, a in sorted(auth.items(), key=lambda kv: -kv[1]['c']):
        A(f'| {disp(w)} | {a["c"]:,} | {len(a["repos"])} | {a["first"][:7] if a["first"] else "—"} | {a["last"][:7] if a["last"] else "—"} | {len(a["months"])} |')
    A(''); A(pie('Commits by contributor', [(disp(k), v['c']) for k, v in auth.items()], 10)); A('')
    years = sorted(org_year); topa = [k for k, _ in sorted(auth.items(), key=lambda kv: -kv[1]['c'])[:15]]
    A('## Contributor commits by year (top 15)'); A(''); A('| Contributor | ' + ' | '.join(map(str, years)) + ' |'); A('|---|' + '---:|' * len(years))
    for w in topa:
        A(f'| {disp(w)} | ' + ' | '.join(str(auth[w]['by_year'].get(y, 0)) for y in years) + ' |')
    A('')
    A('## Issues & PRs opened, by contributor'); A(''); A('| Contributor | Issues | PRs |'); A('|---|---:|---:|')
    for u, v in sorted(issue_auth.items(), key=lambda kv: -(kv[1]['iss'] + kv[1]['pr'])):
        if v['iss'] or v['pr']:
            A(f'| {u} | {v["iss"]:,} | {v["pr"]:,} |')
    A('')
    A('## Per-repository summary (by commits)'); A(''); A('| Repository | Commits | Authors | First | Last | Issues | PRs |'); A('|---|---:|---:|---|---|---:|---:|')
    for repo, s in sorted(repo_sum.items(), key=lambda kv: -kv[1]['c']):
        A(f'| {repo} | {s["c"]:,} | {s["authors"]} | {s["first"][:7] if s["first"] else "—"} | {s["last"][:7] if s["last"] else "—"} | {s["iss"]} | {s["pr"]} |')
    A(''); A(pie('Commits by repository', [(k, v['c']) for k, v in repo_sum.items()], 12)); A('')
    if churn:
        A(f'## Line churn — {len(churn)} locally-cloned repositories'); A('')
        A('From local `git log --numstat`. **These line counts are dominated by bulk/auto-generated commits** (full-file digitization, regeneration, transcoding) — read them as *data volume*, not human effort.'); A('')
        ca = defaultdict(lambda: {'add': 0, 'del': 0, 'files': 0, 'commits': 0})
        for _r, ad in churn.items():
            for w, v in ad.items():
                t = ca[w]; t['add'] += v['add']; t['del'] += v['del']; t['files'] += v['files']; t['commits'] += v['commits']
        A('### By contributor'); A(''); A('| Contributor | Commits | Lines + | Lines − | File-changes |'); A('|---|---:|---:|---:|---:|')
        for w, v in sorted(ca.items(), key=lambda kv: -(kv[1]['add'] + kv[1]['del'])):
            A(f'| {w} | {v["commits"]:,} | {v["add"]:,} | {v["del"]:,} | {v["files"]:,} |')
        A(''); A('### By repository'); A(''); A('| Repository | Lines + | Lines − | File-changes |'); A('|---|---:|---:|---:|')
        for repo, ad in sorted(churn.items()):
            A(f'| {repo} | {sum(v["add"] for v in ad.values()):,} | {sum(v["del"] for v in ad.values()):,} | {sum(v["files"] for v in ad.values()):,} |')
        A('')
    A('## Methodology & caveats'); A('')
    A('- **Commits/tenure/time-series**: GitHub REST commits API (paginated, default branch) for all non-fork repos. Identity uses the linked GitHub login; unlinked commits are mapped to a known contributor by name where possible, else shown as `name:… (no GH acct)`.')
    A('- **Issues & PRs**: issues API (state=all), by *opener* and creation date; PRs identified by the `pull_request` field. Review/close/comment activity not counted.')
    A('- **Line churn**: local `git log --numstat`, for repos present as sibling clones only. Org-wide churn via GitHub `/stats/*` is unavailable (those endpoints stay HTTP 202 across a large burst).')
    A('- Forks are excluded (their history includes upstream contributors).')
    A(''); A('*Generated by `scripts/contributor_stats.py`.*')
    with open(OUT, 'w', encoding='utf-8', newline='\n') as f:
        f.write('\n'.join(L) + '\n')
    print('wrote', OUT)

if __name__ == '__main__':
    main()
