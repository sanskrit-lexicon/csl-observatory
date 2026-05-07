"""
pull_data.py — fetch a complete CDSL ecosystem snapshot.

Outputs to ../data/:
  repos.json         all org repos with metadata
  issues.json        all issues across all repos, normalised
  commits.json       commit history per repo (sha, author, date, +/-, file count)
  summary.json       counts at this snapshot
  snapshots/<date>/  immutable copies of the four files above

Run: python scripts/pull_data.py
"""
import json, sys, datetime, subprocess, time
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

ORG = 'sanskrit-lexicon'
DATA = Path(__file__).resolve().parent.parent / 'data'


def gh(*args, retries=3, backoff=2.0):
    """Run a gh api call with retry-on-5xx backoff."""
    for attempt in range(retries):
        r = subprocess.run(['gh', 'api', *args], capture_output=True, encoding='utf-8')
        if r.returncode == 0:
            return r.stdout
        # GitHub HTTP 5xx errors and timeouts → retry
        retriable = any(s in (r.stderr or '') for s in ['HTTP 502', 'HTTP 503', 'HTTP 504', 'timeout', 'EOF'])
        if not retriable or attempt == retries - 1:
            print(f'  ! gh api error: {(r.stderr or "")[:200].strip()}', file=sys.stderr)
            return None
        wait = backoff ** (attempt + 1)
        print(f'  … retrying in {wait:.1f}s (attempt {attempt+2}/{retries})', file=sys.stderr)
        time.sleep(wait)
    return None


def parse_jsonl(out):
    if not out:
        return []
    return [json.loads(line) for line in out.strip().split('\n') if line.strip()]


def fetch_repos():
    out = gh('--paginate', f'orgs/{ORG}/repos?per_page=100',
             '--jq', '.[] | {name, full_name, description, default_branch, '
                     'created_at, updated_at, pushed_at, size, language, '
                     'license: .license.spdx_id, archived, fork, '
                     'open_issues_count, has_issues, topics, '
                     'stargazers_count, forks_count}')
    return parse_jsonl(out)


def fetch_issues(repo):
    out = gh('--paginate', f'repos/{ORG}/{repo}/issues?state=all&per_page=100',
             '--jq', '.[] | {number, title, state, '
                     'labels: [.labels[].name], '
                     'milestone: .milestone.title, '
                     'user: .user.login, '
                     'assignees: [.assignees[].login], '
                     'created_at, updated_at, closed_at, comments, '
                     'is_pull_request: (.pull_request != null)}')
    return parse_jsonl(out)


def fetch_commits(repo):
    query = '''
    query($cursor: String) {
      repository(owner: "%s", name: "%s") {
        defaultBranchRef {
          target {
            ... on Commit {
              history(first: 100, after: $cursor) {
                pageInfo { hasNextPage endCursor }
                nodes {
                  oid
                  committedDate
                  author { name email user { login } }
                  additions
                  deletions
                  changedFilesIfAvailable
                  message
                }
              }
            }
          }
        }
      }
    }
    ''' % (ORG, repo)
    commits = []
    cursor = None
    pages = 0
    while True:
        args = ['graphql', '-f', f'query={query}']
        if cursor:
            args += ['-f', f'cursor={cursor}']
        out = gh(*args)
        if not out:
            break
        try:
            d = json.loads(out)
        except json.JSONDecodeError:
            break
        ref = (d.get('data') or {}).get('repository', {}).get('defaultBranchRef')
        if not ref or not ref.get('target'):
            break
        h = ref['target'].get('history', {})
        for n in h.get('nodes', []):
            commits.append({
                'oid': n['oid'],
                'date': n['committedDate'],
                'author_name': (n.get('author') or {}).get('name'),
                'author_email': (n.get('author') or {}).get('email'),
                'author_login': ((n.get('author') or {}).get('user') or {}).get('login'),
                'additions': n.get('additions') or 0,
                'deletions': n.get('deletions') or 0,
                'changed_files': n.get('changedFilesIfAvailable'),
                'message': (n.get('message') or '').split('\n')[0][:240],
            })
        page = h.get('pageInfo', {})
        if not page.get('hasNextPage'):
            break
        cursor = page['endCursor']
        pages += 1
        if pages >= 100:  # safety cap: 10k commits per repo
            print(f'  ! {repo}: hit 10k commit cap', file=sys.stderr)
            break
    return commits


def main():
    DATA.mkdir(parents=True, exist_ok=True)
    snap = datetime.date.today().isoformat()
    snap_dir = DATA / 'snapshots' / snap
    snap_dir.mkdir(parents=True, exist_ok=True)

    t0 = time.time()
    print(f'[{snap}] fetching repo list...')
    repos = fetch_repos()
    print(f'  {len(repos)} repos')

    all_issues = {}
    all_commits = {}
    for i, r in enumerate(repos, 1):
        name = r['name']
        if r.get('fork'):
            continue
        prefix = f'  [{i:>2}/{len(repos)}] {name:<28}'
        issues = fetch_issues(name) if r.get('has_issues') else []
        all_issues[name] = issues
        commits = fetch_commits(name)
        all_commits[name] = commits
        print(f'{prefix} issues={len(issues):>4} commits={len(commits):>5}', flush=True)

    summary = {
        'snapshot_date': snap,
        'org': ORG,
        'fetched_at': datetime.datetime.utcnow().isoformat() + 'Z',
        'duration_seconds': round(time.time() - t0, 1),
        'repos_count': len(repos),
        'repos_with_issues': sum(1 for r in repos if r.get('has_issues')),
        'archived_count': sum(1 for r in repos if r.get('archived')),
        'fork_count': sum(1 for r in repos if r.get('fork')),
        'total_issues': sum(len(v) for v in all_issues.values()),
        'total_pull_requests': sum(
            sum(1 for i in v if i.get('is_pull_request'))
            for v in all_issues.values()),
        'total_commits': sum(len(v) for v in all_commits.values()),
    }

    for fname, content in [
        ('repos.json', repos),
        ('issues.json', all_issues),
        ('commits.json', all_commits),
        ('summary.json', summary),
    ]:
        body = json.dumps(content, indent=2, ensure_ascii=False)
        (DATA / fname).write_text(body, encoding='utf-8')
        (snap_dir / fname).write_text(body, encoding='utf-8')

    print(f'\nDONE in {summary["duration_seconds"]}s')
    print(f'  {summary["repos_count"]} repos, '
          f'{summary["total_issues"]} issues '
          f'({summary["total_pull_requests"]} PRs), '
          f'{summary["total_commits"]} commits')


if __name__ == '__main__':
    main()
