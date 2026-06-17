#!/usr/bin/env python3
"""Check the local csl-observatory workspace and required sibling repos.

The observatory assumes a sibling layout:

    GitHub/
      csl-observatory/
      csl-orig/
      CORRECTIONS/

This script is deliberately read-only. It verifies that the required repos are
real working trees, that source files needed by the report pipelines are
present, and that repos with history-sensitive pipelines are not shallow.

Usage:
    python scripts/check_workspace.py
    python scripts/check_workspace.py --json
    python scripts/check_workspace.py --parent C:\\Users\\user\\Documents\\GitHub
"""
import argparse
import json
import os
import subprocess
import sys

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DEFAULT_PARENT = os.path.dirname(ROOT)


REPOS = [
    {
        'name': 'csl-observatory',
        'path': lambda parent: os.path.join(parent, 'csl-observatory'),
        'min_commits': 10,
        'require_full_history': True,
        'required_paths': [
            'scripts',
            os.path.join('observatory', 'site', 'src', 'data'),
            os.path.join('docs', 'ROADMAP.md'),
        ],
        'why': 'observatory reports, dashboard data, roadmap docs',
    },
    {
        'name': 'csl-orig',
        'path': lambda parent: os.path.join(parent, 'csl-orig'),
        'min_commits': 100,
        'require_full_history': True,
        'required_paths': [
            'v02',
            os.path.join('v02', 'mw', 'mw.txt'),
            os.path.join('v02', 'pw', 'pw.txt'),
        ],
        'why': 'OBS-T/OBS-Q git-history mining and dictionary entry counts',
    },
    {
        'name': 'CORRECTIONS',
        'path': lambda parent: os.path.join(parent, 'CORRECTIONS'),
        'min_commits': 1,
        'require_full_history': False,
        'required_paths': [
            'cfr.tsv',
            'history.txt',
        ],
        'why': 'correction form export and campaign history inputs',
    },
]


def run_git(path, *args):
    return subprocess.run(
        ['git', '-C', path, *args],
        capture_output=True,
        encoding='utf-8',
    )


def scalar_git(path, *args):
    result = run_git(path, *args)
    if result.returncode:
        return None, result.stderr.strip() or result.stdout.strip()
    return result.stdout.strip(), None


def check_repo(spec, parent, strict_clean=False):
    path = os.path.abspath(spec['path'](parent))
    failures = []
    warnings = []
    info = {
        'name': spec['name'],
        'path': path,
        'why': spec['why'],
        'exists': os.path.isdir(path),
        'is_worktree': False,
        'is_shallow': None,
        'commit_count': None,
        'head': None,
        'branch': None,
        'dirty_count': None,
        'missing_paths': [],
        'warnings': warnings,
        'failures': failures,
    }

    if not info['exists']:
        failures.append('directory missing')
        return info

    inside, err = scalar_git(path, 'rev-parse', '--is-inside-work-tree')
    if err or inside != 'true':
        failures.append(f'not a git working tree ({err or inside})')
        return info
    info['is_worktree'] = True

    shallow, err = scalar_git(path, 'rev-parse', '--is-shallow-repository')
    if err:
        failures.append(f'cannot determine shallow state: {err}')
    else:
        info['is_shallow'] = (shallow == 'true')
        if info['is_shallow'] and spec['require_full_history']:
            failures.append('shallow clone but full history is required')
        elif info['is_shallow']:
            warnings.append('shallow clone; acceptable for current file-only inputs')

    count, err = scalar_git(path, 'rev-list', '--count', 'HEAD')
    if err:
        failures.append(f'cannot count commits: {err}')
    else:
        try:
            info['commit_count'] = int(count)
            if info['commit_count'] < spec['min_commits']:
                failures.append(
                    f'only {info["commit_count"]} commits; expected at least {spec["min_commits"]}'
                )
        except ValueError:
            failures.append(f'non-numeric commit count: {count}')

    head, err = scalar_git(path, 'rev-parse', '--short', 'HEAD')
    if not err:
        info['head'] = head

    branch, err = scalar_git(path, 'branch', '--show-current')
    if not err:
        info['branch'] = branch or '(detached)'

    status, err = scalar_git(path, 'status', '--short')
    if err:
        warnings.append(f'cannot read dirty state: {err}')
    else:
        dirty = [line for line in status.splitlines() if line.strip()]
        info['dirty_count'] = len(dirty)
        if dirty and strict_clean:
            failures.append(f'working tree has {len(dirty)} changed paths')
        elif dirty:
            warnings.append(f'working tree has {len(dirty)} changed paths')

    for rel in spec['required_paths']:
        if not os.path.exists(os.path.join(path, rel)):
            info['missing_paths'].append(rel.replace(os.sep, '/'))
    if info['missing_paths']:
        failures.append(f'missing required paths: {", ".join(info["missing_paths"])}')

    return info


def print_text(results, parent):
    print(f'Workspace parent: {os.path.abspath(parent)}')
    print('')
    for r in results:
        status = 'FAIL' if r['failures'] else ('WARN' if r['warnings'] else 'OK')
        print(f'[{status}] {r["name"]}')
        print(f'  path: {r["path"]}')
        print(f'  use : {r["why"]}')
        if r['is_worktree']:
            print(f'  git : branch={r["branch"]} head={r["head"]} commits={r["commit_count"]} shallow={r["is_shallow"]}')
            print(f'  dirty paths: {r["dirty_count"]}')
        for msg in r['warnings']:
            print(f'  warning: {msg}')
        for msg in r['failures']:
            print(f'  failure: {msg}')
        print('')


def main():
    parser = argparse.ArgumentParser(description='Check csl-observatory workspace prerequisites.')
    parser.add_argument('--parent', default=DEFAULT_PARENT,
                        help='Parent directory containing csl-observatory, csl-orig, and CORRECTIONS.')
    parser.add_argument('--json', action='store_true', help='Emit machine-readable JSON.')
    parser.add_argument('--strict-clean', action='store_true',
                        help='Fail if any checked repo has uncommitted changes.')
    args = parser.parse_args()

    parent = os.path.abspath(args.parent)
    results = [check_repo(spec, parent, strict_clean=args.strict_clean) for spec in REPOS]
    ok = not any(r['failures'] for r in results)

    payload = {
        'ok': ok,
        'parent': parent,
        'results': results,
    }
    if args.json:
        json.dump(payload, sys.stdout, ensure_ascii=False, indent=2)
        print()
    else:
        print_text(results, parent)
        if ok:
            print('OK: workspace has the required local inputs.')
        else:
            print('FAIL: workspace is missing required local inputs.', file=sys.stderr)

    return 0 if ok else 1


if __name__ == '__main__':
    raise SystemExit(main())

