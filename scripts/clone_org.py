#!/usr/bin/env python3
"""Clone every non-fork sanskrit-lexicon repo as a full sibling — idempotent and
non-destructive.

  * Missing repo   -> full `git clone`.
  * Shallow clone  -> `git fetch --unshallow` (deepens history; does NOT touch
                      the working tree or refs).
  * Full clone     -> left untouched.

It never runs `reset`/`checkout`, so uncommitted work is never at risk.

Why: ad-hoc shallow clones leave `.git`-only shells (1 commit, empty working
tree) that silently break churn/doc tooling — exactly what bit the 2026-05
analytics + documentation work until the repos were un-shallowed by hand.
Roadmap item M5.

Usage:
    python scripts/clone_org.py [TARGET_DIR]
        TARGET_DIR defaults to the parent directory of csl-observatory
        (i.e. the conventional siblings layout).

Note: cloning the whole org from scratch pulls several GB (some repos hold
large binary/generated data). On an existing layout only the missing/shallow
repos are touched. Requires an authenticated `gh`.
"""
import subprocess, json, os, sys
sys.stdout.reconfigure(encoding='utf-8')

ORG = 'sanskrit-lexicon'
HERE = os.path.dirname(os.path.abspath(__file__))
TARGET = sys.argv[1] if len(sys.argv) > 1 else os.path.dirname(os.path.dirname(HERE))


def run(*args):
    return subprocess.run(args, capture_output=True, encoding='utf-8')


def main():
    raw = run('gh', 'api', '--paginate', f'orgs/{ORG}/repos?per_page=100').stdout
    repos = [r for r in json.loads(raw) if not r['fork']]
    print(f'{len(repos)} non-fork repos -> {TARGET}\n')
    cloned = deepened = full = failed = 0
    for r in sorted(repos, key=lambda x: x['name']):
        name = r['name']
        d = os.path.join(TARGET, name)
        if not os.path.isdir(os.path.join(d, '.git')):
            rc = run('git', 'clone', '--quiet', f'https://github.com/{ORG}/{name}', d).returncode
            if rc == 0:
                cloned += 1; print(f'  cloned        {name}')
            else:
                failed += 1; print(f'  CLONE-FAILED  {name}')
            continue
        shallow = run('git', '-C', d, 'rev-parse', '--is-shallow-repository').stdout.strip()
        if shallow == 'true':
            run('git', '-C', d, 'fetch', '--quiet', '--unshallow')
            deepened += 1
            print(f'  unshallowed   {name}  (if its working tree is empty, run: git -C {name} checkout .)')
        else:
            full += 1
    print(f'\nDONE: {cloned} cloned, {deepened} unshallowed, {full} already full, {failed} failed')


if __name__ == '__main__':
    main()
