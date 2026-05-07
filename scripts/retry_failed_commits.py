"""
retry_failed_commits.py — re-fetch commit history for repos that returned 0
commits in the previous snapshot (typically due to GraphQL HTTP 502 errors).

Usage: python scripts/retry_failed_commits.py
"""
import json, sys, datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from pull_data import fetch_commits, DATA  # reuse fetch + retry logic

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')


def main():
    repos = json.loads((DATA / 'repos.json').read_text(encoding='utf-8'))
    commits_by_repo = json.loads((DATA / 'commits.json').read_text(encoding='utf-8'))

    failed = []
    for r in repos:
        if r.get('fork') or r.get('archived'):
            continue
        name = r['name']
        if name == 'csl-observatory':
            continue
        if commits_by_repo.get(name, []) == [] and r.get('size', 0) > 0:
            failed.append(name)

    print(f'Retrying {len(failed)} repos: {failed}')
    recovered = {}
    for i, name in enumerate(failed, 1):
        print(f'  [{i:>2}/{len(failed)}] {name:<28}', end='', flush=True)
        commits = fetch_commits(name)
        commits_by_repo[name] = commits
        recovered[name] = len(commits)
        print(f' commits={len(commits)}')

    body = json.dumps(commits_by_repo, indent=2, ensure_ascii=False)
    (DATA / 'commits.json').write_text(body, encoding='utf-8')

    snap = datetime.date.today().isoformat()
    snap_dir = DATA / 'snapshots' / snap
    snap_dir.mkdir(parents=True, exist_ok=True)
    (snap_dir / 'commits.json').write_text(body, encoding='utf-8')

    # Update summary
    summary = json.loads((DATA / 'summary.json').read_text(encoding='utf-8'))
    summary['total_commits'] = sum(len(v) for v in commits_by_repo.values())
    summary['retry_recovered'] = recovered
    summary['retried_at'] = datetime.datetime.utcnow().isoformat() + 'Z'
    sbody = json.dumps(summary, indent=2)
    (DATA / 'summary.json').write_text(sbody, encoding='utf-8')
    (snap_dir / 'summary.json').write_text(sbody, encoding='utf-8')

    print(f'\nRecovered {sum(recovered.values())} commits.')
    print(f'New total: {summary["total_commits"]}')


if __name__ == '__main__':
    main()
