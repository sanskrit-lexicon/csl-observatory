"""
pull_data.py — fetch a complete CDSL ecosystem snapshot.

Outputs to ../data/:
  repos.json         all org repos with metadata
  issues.json        all issues across all repos, normalised, each carrying
                      project_fields (Tooling Roadmap project #9 board values,
                      when the issue/PR is on the board)
  commits.json       commit history per repo (sha, author, date, +/-, file count)
  summary.json       counts at this snapshot
  snapshots/<date>/  immutable copies of the four files above

Rate limits: every `gh api`/`gh api graphql` call goes through gh(), which
retries HTTP 5xx/timeouts with backoff AND detects GitHub's primary/secondary
rate-limit responses explicitly — on a rate-limit hit it logs the condition,
reads the reset time off `gh api rate_limit`, sleeps (capped), and retries a
bounded number of times before giving up and logging the failure.

Run: python scripts/pull_data.py
"""
import json, sys, datetime, subprocess, time
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

ORG = 'sanskrit-lexicon'
DATA = Path(__file__).resolve().parent.parent / 'data'

# Tooling Roadmap project #9 (org project) — see .ai_state.md for how this
# node id / field-value shape was discovered.
PROJECT_NODE_ID = 'PVT_kwDOAGGnOc4BXy9n'


def _rate_limit_wait_seconds(cap=120.0):
    """Read the primary rate-limit reset time off GitHub; cap the wait so a
    single call never blocks the script for a full hour."""
    r = subprocess.run(['gh', 'api', 'rate_limit', '--jq', '.rate.reset'],
                        capture_output=True, encoding='utf-8')
    try:
        reset_epoch = int(r.stdout.strip())
        return max(1.0, min(reset_epoch - time.time() + 1, cap))
    except (ValueError, AttributeError):
        return cap


def gh(*args, retries=3, backoff=2.0, rate_limit_retries=3):
    """Run a gh api call with retry-on-5xx backoff and explicit rate-limit handling.

    Rate-limit hits (primary "API rate limit exceeded" or GitHub's secondary
    rate limit) have their own retry budget, separate from the 5xx/backoff
    one, since waiting for a reset is a different failure mode than a
    transient server error.
    """
    attempt = 0
    rl_attempt = 0
    while True:
        r = subprocess.run(['gh', 'api', *args], capture_output=True, encoding='utf-8')
        if r.returncode == 0:
            return r.stdout
        stderr = r.stderr or ''
        if 'rate limit' in stderr.lower() and rl_attempt < rate_limit_retries:
            rl_attempt += 1
            wait = _rate_limit_wait_seconds()
            print(f'  ! rate limit hit — waiting {wait:.0f}s for reset '
                  f'(rate-limit retry {rl_attempt}/{rate_limit_retries})', file=sys.stderr)
            time.sleep(wait)
            continue
        # GitHub HTTP 5xx errors and timeouts → retry
        retriable = any(s in stderr for s in ['HTTP 502', 'HTTP 503', 'HTTP 504', 'timeout', 'EOF'])
        if not retriable or attempt >= retries - 1:
            print(f'  ! gh api error: {stderr[:200].strip()}', file=sys.stderr)
            return None
        wait = backoff ** (attempt + 1)
        print(f'  … retrying in {wait:.1f}s (attempt {attempt+2}/{retries})', file=sys.stderr)
        time.sleep(wait)
        attempt += 1


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


def fetch_project_fields():
    """Fetch Tooling Roadmap project #9 field values for every item on the
    board, keyed by (repo_name, issue/PR number). Uses the batched-pagination
    GraphQL pattern documented in .ai_state.md (per-item calls were unbearably
    slow under this org's TLS-timeout flakiness).
    """
    query = '''
    query($project: ID!, $cursor: String) {
      node(id: $project) {
        ... on ProjectV2 {
          items(first: 100, after: $cursor) {
            pageInfo { hasNextPage endCursor }
            nodes {
              content {
                ... on Issue { number repository { name } }
                ... on PullRequest { number repository { name } }
              }
              fieldValues(first: 20) {
                nodes {
                  ... on ProjectV2ItemFieldSingleSelectValue {
                    name
                    field { ... on ProjectV2SingleSelectField { name } }
                  }
                  ... on ProjectV2ItemFieldTextValue {
                    text
                    field { ... on ProjectV2FieldCommon { name } }
                  }
                  ... on ProjectV2ItemFieldNumberValue {
                    number
                    field { ... on ProjectV2FieldCommon { name } }
                  }
                  ... on ProjectV2ItemFieldDateValue {
                    date
                    field { ... on ProjectV2FieldCommon { name } }
                  }
                }
              }
            }
          }
        }
      }
    }
    '''
    fields_by_item = {}
    cursor = None
    while True:
        args = ['graphql', '-f', f'query={query}', '-f', f'project={PROJECT_NODE_ID}']
        if cursor:
            args += ['-f', f'cursor={cursor}']
        out = gh(*args)
        if not out:
            break
        try:
            d = json.loads(out)
        except json.JSONDecodeError:
            break
        node = (d.get('data') or {}).get('node') or {}
        items = node.get('items') or {}
        for item in items.get('nodes', []):
            content = item.get('content') or {}
            repo = (content.get('repository') or {}).get('name')
            number = content.get('number')
            if not repo or number is None:
                continue  # draft items / items with no linked issue-or-PR
            values = {}
            for fv in (item.get('fieldValues') or {}).get('nodes', []):
                fname = (fv.get('field') or {}).get('name')
                if not fname:
                    continue
                value = fv.get('name')
                if value is None:
                    value = fv.get('text')
                if value is None:
                    value = fv.get('number')
                if value is None:
                    value = fv.get('date')
                if value is not None:
                    values[fname] = value
            if values:
                fields_by_item[(repo, number)] = values
        page = items.get('pageInfo', {})
        if not page.get('hasNextPage'):
            break
        cursor = page['endCursor']
    return fields_by_item


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

    print('  fetching Tooling Roadmap project #9 field values...')
    project_fields = fetch_project_fields()
    print(f'  {len(project_fields)} items carry project-board fields')

    all_issues = {}
    all_commits = {}
    for i, r in enumerate(repos, 1):
        name = r['name']
        if r.get('fork'):
            continue
        prefix = f'  [{i:>2}/{len(repos)}] {name:<28}'
        issues = fetch_issues(name) if r.get('has_issues') else []
        matched = 0
        for issue in issues:
            pf = project_fields.get((name, issue['number']))
            if pf:
                issue['project_fields'] = pf
                matched += 1
        all_issues[name] = issues
        commits = fetch_commits(name)
        all_commits[name] = commits
        suffix = f' project_fields={matched}' if matched else ''
        print(f'{prefix} issues={len(issues):>4} commits={len(commits):>5}{suffix}', flush=True)

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
        'total_project_board_items': len(project_fields),
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
