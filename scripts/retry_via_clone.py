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
import json, sys, datetime, tempfile, shutil, argparse
from pathlib import Path

from _common import run

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

DATA = Path(__file__).resolve().parent.parent / 'data'
ORG = 'sanskrit-lexicon'

DELIM = '<<<CSL_FIELD>>>'  # safe, unlikely-to-collide field separator

# Commit history is append-only. A material drop against the last committed
# snapshot is a partial fetch, not new data: the 21-11 dispatches showed
# csl-orig 2,295 -> 200 silently accepted while clone recovery never ran.
PARTIAL_DROP_FRACTION = 0.05   # >5% fewer commits than the prior snapshot
MIN_PARTIAL_DROP = 5           # ignore tiny pagination jitter (718 -> 717)


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
        shutil.rmtree(tmp, ignore_errors=True)
        raise RuntimeError(f'clone failed: {(r.stderr or "")[:200]}')

    fmt = DELIM.join(['%H', '%aI', '%ae', '%an', '%s'])
    r = run(['git', '--git-dir', str(repo_dir), 'log', '--all',
             f'--pretty=format:{fmt}',
             f'--max-count={max_commits}'], timeout=180)
    if r.returncode != 0:
        shutil.rmtree(tmp, ignore_errors=True)
        raise RuntimeError(f'git log failed: {(r.stderr or "")[:200]}')

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


def prior_commit_counts(data=DATA):
    """Per-repo commit counts from the newest committed snapshot that is not
    today's (the script writes today's snapshot at the end of a successful
    run, so it must not become its own baseline on a second run same day)."""
    today = datetime.date.today().isoformat()
    for path in sorted((data / 'snapshots').glob('*/commits.json'), reverse=True):
        if path.parent.name == today:
            continue
        counts = json.loads(path.read_text(encoding='utf-8'))
        return {name: len(commits) for name, commits in counts.items()}
    return {}


def _material_drop(current, prior):
    return current < prior - max(MIN_PARTIAL_DROP, int(prior * PARTIAL_DROP_FRACTION))


def partial_coverage_repos(data=DATA):
    """Repos whose current commit count is materially below the last committed
    snapshot. autodetect_failed() only sees `commits == []`, so a GraphQL call
    that paged out early (csl-orig 2,295 -> 200 on 21-11) sailed through and
    got committed as a smaller 'live' snapshot. History is append-only: a drop
    is a fetch defect until proven otherwise, and must be re-cloned."""
    current = json.loads((data / 'commits.json').read_text(encoding='utf-8'))
    prior = prior_commit_counts(data)
    bad = {}
    for name, old in prior.items():
        new = len(current.get(name, []))
        if _material_drop(new, old):
            bad[name] = (new, old)
    return bad


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('repos', nargs='*')
    args = ap.parse_args()
    partial = partial_coverage_repos()
    for name, (new, old) in sorted(partial.items()):
        print(f'  ! {name}: {new:,} commits vs {old:,} in last snapshot '
              f'— partial fetch, re-cloning', file=sys.stderr)
    targets = list(dict.fromkeys([*args.repos, *autodetect_failed(), *partial]))
    print(f'Targets ({len(targets)}): {targets}\n')

    all_commits = json.loads((DATA / 'commits.json').read_text(encoding='utf-8'))
    recovered = {}
    failed = []
    for i, name in enumerate(targets, 1):
        print(f'[{i}/{len(targets)}] {name}', flush=True)
        try:
            commits = fetch_commits_via_clone(name)
            if name in partial and _material_drop(len(commits), partial[name][1]):
                raise RuntimeError(
                    f'clone recovered only {len(commits):,} commits, prior snapshot '
                    f'has {partial[name][1]:,}')
        except RuntimeError as exc:
            print(f'    !! {name}: {exc}', file=sys.stderr)
            failed.append(name)
            continue
        all_commits[name] = commits
        recovered[name] = len(commits)
        print(f'    → {len(commits):,} commits')

    if failed:
        # Fail BEFORE any write: a snapshot with a silently truncated history
        # is worse than no snapshot (it poisons every headline number and the
        # append-only invariant that lets the next run detect the problem).
        print(f'FATAL: clone recovery failed for {len(failed)} repo(s): '
              f'{", ".join(failed)}. No files written — partial coverage is '
              f'not a valid live snapshot.', file=sys.stderr)
        raise SystemExit(1)

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
