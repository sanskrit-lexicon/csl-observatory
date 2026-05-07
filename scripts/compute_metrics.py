"""
compute_metrics.py — derive cross-cutting metrics from a CDSL snapshot.

Reads:  data/{repos,issues,commits}.json + scripts/contributors_map.json
Writes: data/{contributors,repo_metrics,timeline,cross_repo}.json
"""
import json, sys
from pathlib import Path
from collections import defaultdict, Counter

sys.stdout.reconfigure(encoding='utf-8')

DATA = Path(__file__).resolve().parent.parent / 'data'
SCRIPTS = Path(__file__).resolve().parent

TYPE_LABELS = {'link-target','link-splitting','markup','text-correction',
               'content-enhancement','encoding','scan-quality','bug','question'}
SEV_LABELS = {'minor','medium','hard'}
MS_TITLES = {'Dictionary to Book','Digitization Quality','Structured Data','Major Enhancements'}


def load(name): return json.loads((DATA / name).read_text(encoding='utf-8'))


def compute_contributors(commits_by_repo, issues_by_repo, contributors_map):
    # Build alias → canonical map from contributors_map
    alias_index = {}
    for canonical, meta in contributors_map.items():
        if canonical.startswith('_'): continue
        alias_index[canonical] = canonical
        for alias in (meta.get('aliases') or []):
            alias_index[alias] = canonical

    def canonical(login):
        return alias_index.get(login, login) if login else None

    by_login = {}
    def row(login):
        if login not in by_login:
            by_login[login] = {
                'login': login,
                'commits_total': 0, 'commits_per_repo': defaultdict(int),
                'additions_total': 0, 'deletions_total': 0,
                'first_commit': None, 'last_commit': None,
                'repos_touched': set(),
                'issues_created': 0, 'issues_per_repo': defaultdict(int),
                'comments_aggregate': 0,
                'merged_aliases': set(),
            }
        return by_login[login]

    for repo, commits in commits_by_repo.items():
        for c in commits:
            raw_login = c.get('author_login') or c.get('author_email') or c.get('author_name')
            if not raw_login: continue
            login = canonical(raw_login)
            r = row(login)
            if raw_login != login:
                r['merged_aliases'].add(raw_login)
            r['commits_total'] += 1
            r['commits_per_repo'][repo] += 1
            r['additions_total'] += c.get('additions') or 0
            r['deletions_total'] += c.get('deletions') or 0
            r['repos_touched'].add(repo)
            d = c.get('date')
            if d:
                if not r['first_commit'] or d < r['first_commit']: r['first_commit'] = d
                if not r['last_commit']  or d > r['last_commit']:  r['last_commit']  = d

    for repo, issues in issues_by_repo.items():
        for i in issues:
            if i.get('is_pull_request'): continue
            raw_login = i.get('user')
            if not raw_login: continue
            login = canonical(raw_login)
            r = row(login)
            if raw_login != login:
                r['merged_aliases'].add(raw_login)
            r['issues_created'] += 1
            r['issues_per_repo'][repo] += 1
            r['comments_aggregate'] += i.get('comments') or 0

    out = []
    for login, r in by_login.items():
        meta = contributors_map.get(login, {})
        r['real_name'] = meta.get('real_name')
        r['orcid'] = meta.get('orcid')
        r['role'] = meta.get('role') or 'contributor'
        r['affiliation'] = meta.get('affiliation')
        r['notes'] = meta.get('notes')
        r['is_bot'] = bool(meta.get('is_bot'))
        r['merged_aliases'] = sorted(r['merged_aliases'])
        if r['first_commit'] and r['last_commit']:
            r['span_first'] = r['first_commit'][:10]
            r['span_last'] = r['last_commit'][:10]
            try:
                r['span_years'] = int(r['span_last'][:4]) - int(r['span_first'][:4]) + 1
            except ValueError:
                r['span_years'] = None
        r['commits_per_repo'] = dict(sorted(r['commits_per_repo'].items(), key=lambda kv: -kv[1]))
        r['issues_per_repo']  = dict(sorted(r['issues_per_repo'].items(),  key=lambda kv: -kv[1]))
        r['repos_touched']    = sorted(r['repos_touched'])
        r['repos_touched_count'] = len(r['repos_touched'])
        out.append(r)
    out.sort(key=lambda r: -r['commits_total'])
    return out


def compute_repo_metrics(repos, issues_by_repo, commits_by_repo):
    out = []
    for r in repos:
        name = r['name']
        issues = issues_by_repo.get(name, [])
        commits = commits_by_repo.get(name, [])
        non_pr = [i for i in issues if not i.get('is_pull_request')]
        type_counter = Counter()
        sev_counter = Counter()
        ms_counter = Counter()
        for i in non_pr:
            for lbl in i.get('labels', []):
                if lbl in TYPE_LABELS: type_counter[lbl] += 1
                if lbl in SEV_LABELS: sev_counter[lbl] += 1
            if i.get('milestone'): ms_counter[i['milestone']] += 1
        contributors = sorted({c['author_login'] for c in commits if c.get('author_login')})
        first_commit = min((c['date'] for c in commits if c.get('date')), default=None)
        last_commit = max((c['date'] for c in commits if c.get('date')), default=None)
        out.append({
            'name': name,
            'description': r.get('description'),
            'language': r.get('language'),
            'license': r.get('license'),
            'archived': r.get('archived'),
            'created_at': r.get('created_at'),
            'pushed_at': r.get('pushed_at'),
            'commits_count': len(commits),
            'contributors_count': len(contributors),
            'contributors': contributors,
            'issues_total': len(non_pr),
            'issues_open': sum(1 for i in non_pr if i.get('state') == 'open'),
            'issues_closed': sum(1 for i in non_pr if i.get('state') == 'closed'),
            'first_commit': first_commit,
            'last_commit': last_commit,
            'type_counts': dict(type_counter),
            'severity_counts': dict(sev_counter),
            'milestone_counts': dict(ms_counter),
            'triaged': bool(sev_counter),
        })
    return out


def compute_timeline(commits_by_repo, issues_by_repo):
    by_year = Counter()
    by_year_repo = defaultdict(lambda: defaultdict(int))
    for repo, commits in commits_by_repo.items():
        for c in commits:
            d = c.get('date')
            if d:
                year = d[:4]
                by_year[year] += 1
                by_year_repo[year][repo] += 1
    issues_year = Counter()
    closed_year = Counter()
    for repo, issues in issues_by_repo.items():
        for i in issues:
            if i.get('is_pull_request'): continue
            if i.get('created_at'): issues_year[i['created_at'][:4]] += 1
            if i.get('closed_at'):  closed_year[i['closed_at'][:4]] += 1
    return {
        'commits_by_year': dict(sorted(by_year.items())),
        'commits_by_year_per_repo': {y: dict(sorted(reps.items(), key=lambda kv: -kv[1]))
                                     for y, reps in sorted(by_year_repo.items())},
        'issues_created_by_year': dict(sorted(issues_year.items())),
        'issues_closed_by_year':  dict(sorted(closed_year.items())),
    }


def compute_cross_repo(repos_metrics):
    # Triaged-only: counts that reflect the runbook's taxonomy
    type_total_triaged = Counter()
    type_x_repo = {}
    triaged = [rm for rm in repos_metrics if rm['triaged']]
    for rm in triaged:
        for t, n in rm['type_counts'].items():
            type_total_triaged[t] += n
            type_x_repo.setdefault(t, {})[rm['name']] = n
    # All-repos: includes pre-existing GitHub default labels (bug, question, etc.)
    type_total_all = Counter()
    for rm in repos_metrics:
        for t, n in rm['type_counts'].items():
            type_total_all[t] += n
    return {
        'type_totals': dict(type_total_triaged),
        'type_totals_all_repos': dict(type_total_all),
        'type_x_repo': type_x_repo,
        'triaged_repos': sorted([rm['name'] for rm in triaged]),
        'untriaged_with_issues': sorted([
            rm['name'] for rm in repos_metrics
            if not rm['triaged'] and rm['issues_total'] > 0]),
    }


def main():
    repos = load('repos.json')
    issues_by_repo = load('issues.json')
    commits_by_repo = load('commits.json')
    contributors_map = json.loads(
        (SCRIPTS / 'contributors_map.json').read_text(encoding='utf-8'))

    contributors = compute_contributors(commits_by_repo, issues_by_repo, contributors_map)
    repos_metrics = compute_repo_metrics(repos, issues_by_repo, commits_by_repo)
    timeline = compute_timeline(commits_by_repo, issues_by_repo)
    cross = compute_cross_repo(repos_metrics)

    for fname, content in [
        ('contributors.json', contributors),
        ('repo_metrics.json', repos_metrics),
        ('timeline.json', timeline),
        ('cross_repo.json', cross),
    ]:
        (DATA / fname).write_text(json.dumps(content, indent=2, ensure_ascii=False), encoding='utf-8')

    print(f'Contributors: {len(contributors)} unique logins/identities')
    print(f'Top 12 by commits:')
    for c in contributors[:12]:
        name = c.get('real_name') or c['login']
        sf = (c.get('span_first') or '-')[:7]; sl = (c.get('span_last') or '-')[:7]
        print(f'  {c["commits_total"]:>5} commits | {len(c["repos_touched"]):>2} repos | '
              f'{sf} → {sl} | {c.get("role", "-"):<12} | {name}')
    print(f'\nRepos: {len(repos_metrics)}; triaged: {len(cross["triaged_repos"])}')
    print(f'Triaged: {cross["triaged_repos"]}')
    print(f'Untriaged with issues: {cross["untriaged_with_issues"][:15]}...')

if __name__ == '__main__':
    main()
