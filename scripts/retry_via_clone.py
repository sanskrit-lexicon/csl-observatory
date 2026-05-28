"""
retry_via_clone.py — re-fetch commit history for repos that the GraphQL
endpoint cannot serve (typically due to history size). Bare-clones the
repo with --filter=blob:none, parses `git log --numstat`, and merges
into data/commits.json.

Trade-off vs GraphQL: the clone-based fetch does NOT yield GitHub
`author_login` (only email and name), so commits land in
contributors_map under email-based keys until aliases catch up. This is
acceptable because the alias-merge logic in compute_metrics.py already
folds those keys onto canonical logins where the email matches.

Usage:
    python scripts/retry_via_clone.py             # auto-detect failed repos
    python scripts/retry_via_clone.py csl-orig    # specific repo(s)
"""
import json, sys, datetime, subprocess, tempfile, shutil, argparse
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

DATA = Path(__file__).resolve().parent.parent / 'data'
ORG = 'sanskrit-lexicon'

DELIM = '<<<CSL_FIELD>>>'  # safe, unlikely-to-collide field separator


def run(cmd, cwd=None, timeout=600):
    return subprocess.run(cmd, cwd=cwd, capture_output=True,
                          encoding='utf-8', errors='replace', timeout=timeout)


def fetch_commits_via_clone(repo, max_commits=200000):
    """Bare-clone the repo with --filter=blob:none and parse `git log --all`.
    Returns commits in the same shape as pull_data.fetch_commits().

    Trade-offs:
    - author_login is always None (git log has no GitHub login concept).
      compute_metrics.py's alias-merge logic folds email-keyed records onto
      canonical GitHub logins, so this is acceptable.
    - additions / deletions / changed_files are always 0. Computing them
      requires --shortstat or --numstat, which trigger lazy blob fetches
      against a partial clone — making the log run for many minutes on
      large repos. We accept the missing per-commit stats as a documented
      trade-off; what matters for the article is commit count, dates,
      authors, and messages, all of which are recovered fully.
    - --filter=blob:none means the clone is small (a few MB) even for
      multi-GB repos like cologne-stardict (2.1 GB) and csl-orig (870 MB).
    """
    tmp = Path(tempfile.mkdtemp(prefix=f'csl-{repo}-'))
    repo_dir = tmp / 'repo.git'
    url = f'https://github.com/{ORG}/{repo}.git'

    print(f'    cloning {url} (--bare --filter=blob:none, metadata only)...', flush=True)
    r = run(['git', 'clone', '--bare', '--filter=blob:none', '--no-tags',
             url, str(repo_dir)], timeout=600)
    if r.returncode != 0:
        print(f'    ! clone failed: {(r.stderr or "")[:200]}', file=sys.stderr)
        shutil.rmtree(tmp, ignore_errors=True)
        return []

    fmt = DELIM.join(['%H', '%aI', '%ae', '%an', '%s'])
    r = run(['git', '--git-dir', str(repo_dir), 'log', '--all',
             f'--pretty=format:{fmt}',
             f'--max-count={max_commits}'], timeout=180)
    if r.returncode != 0:
        print(f'    ! git log failed: {(r.stderr or "")[:200]}', file=sys.stderr)
        shutil.rmtree(tmp, ignore_errors=True)
        return []

    commits = []
    for line in r.stdout.splitlines():
        if not line.strip(): continue
        parts = line.split(DELIM, 4)
        if len(parts) < 5: continue
        oid, date, email, name, msg = parts
        commits.append({
            'oid': oid,
            'date': date,
            'author_name': name,
            'author_email': email,
            'author_login': None,
            'additions': 0,
            'deletions': 0,
            'changed_files': 0,
            'message': msg.replace('\n', ' ')[:240],
            'fetch_method': 'clone-metadata-only',
        })

    shutil.rmtree(tmp, ignore_errors=True)
    return commits


def autodetect_failed():
    """Repos that have 0 commits captured but non-zero size."""
    repos = json.loads((DATA / 'repos.json').read_text(encoding='utf-8'))
    commits = json.loads((DATA / 'commits.json').read_text(encoding='utf-8'))
    failed = []
    for r in repos:
        if r.get('fork') or r.get('archived'): continue
        if r['name'] == 'csl-observatory': continue
        if commits.get(r['name'], []) == [] and (r.get('size') or 0) > 0:
            failed.append(r['name'])
    return failed


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('repos', nargs='*')
    args = ap.parse_args()
    targets = args.repos or autodetect_failed()
    print(f'Targets ({len(targets)}): {targets}\n')

    all_commits = json.loads((DATA / 'commits.json').read_text(encoding='utf-8'))
    recovered = {}
    for i, name in enumerate(targets, 1):
        print(f'[{i}/{len(targets)}] {name}', flush=True)
        commits = fetch_commits_via_clone(name)
        all_commits[name] = commits
        recovered[name] = len(commits)
        print(f'    → {len(commits):,} commits')

    body = json.dumps(all_commits, indent=2, ensure_ascii=False)
    (DATA / 'commits.json').write_text(body, encoding='utf-8')

    snap = datetime.date.today().isoformat()
    snap_dir = DATA / 'snapshots' / snap
    snap_dir.mkdir(parents=True, exist_ok=True)
    (snap_dir / 'commits.json').write_text(body, encoding='utf-8')

    summary = json.loads((DATA / 'summary.json').read_text(encoding='utf-8'))
    summary['total_commits'] = sum(len(v) for v in all_commits.values())
    summary['retry_via_clone'] = recovered
    summary['retry_via_clone_at'] = datetime.datetime.now(datetime.timezone.utc).isoformat()
    sbody = json.dumps(summary, indent=2)
    (DATA / 'summary.json').write_text(sbody, encoding='utf-8')
    (snap_dir / 'summary.json').write_text(sbody, encoding='utf-8')

    print(f'\nRecovered {sum(recovered.values()):,} commits via clone.')
    print(f'New total: {summary["total_commits"]:,}')


if __name__ == '__main__':
    main()
