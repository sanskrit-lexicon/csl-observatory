"""
propagate_templates.py — copy community files from templates/ into each
target CDSL dictionary repository, commit, and push.

Usage:
    python scripts/propagate_templates.py [--dry-run] [REPO ...]

If no repo names are passed, the script targets the eight triaged repos
(AP AP90 FRI GRA MD MWS PWG PWK). Pass repo names to override:

    python scripts/propagate_templates.py PWG MWS

Files copied:
  - CONTRIBUTING.md
  - CODE_OF_CONDUCT.md
  - SECURITY.md
  - .github/PULL_REQUEST_TEMPLATE.md
  - .github/ISSUE_TEMPLATE/*.yml

The script SKIPS overwriting any file that already exists in the target repo.
This is the conservative default; pass `--force` to overwrite.

Each target repo is expected to be cloned at ../<REPO>/ (sibling to
csl-observatory). The script aborts if a repo is missing.
"""
import shutil, subprocess, sys, argparse
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

OBS = Path(__file__).resolve().parent.parent
TEMPLATES = OBS / 'templates'
PARENT = OBS.parent  # …/Documents/GitHub

DEFAULT_REPOS = ['AP', 'AP90', 'FRI', 'GRA', 'MD', 'MWS', 'PWG', 'PWK']


def files_to_copy():
    """Yield (relative_path, source_absolute_path) pairs."""
    for src in TEMPLATES.rglob('*'):
        if src.is_file():
            rel = src.relative_to(TEMPLATES)
            yield rel, src


def run(cmd, cwd):
    r = subprocess.run(cmd, cwd=str(cwd), capture_output=True, encoding='utf-8')
    return r.returncode, r.stdout, r.stderr


def propagate(repo_name, force=False, dry_run=False):
    repo_dir = PARENT / repo_name
    if not repo_dir.exists():
        print(f'  ! {repo_name}: repo not cloned at {repo_dir}', file=sys.stderr)
        return False
    if not (repo_dir / '.git').exists():
        print(f'  ! {repo_name}: not a git repository', file=sys.stderr)
        return False

    copied = []
    skipped = []
    for rel, src in files_to_copy():
        dst = repo_dir / rel
        if dst.exists() and not force:
            skipped.append(rel)
            continue
        if dry_run:
            copied.append(rel)
            continue
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
        copied.append(rel)

    print(f'  {repo_name}: copied {len(copied)} files'
          + (f', skipped {len(skipped)} pre-existing' if skipped else ''))

    if dry_run or not copied:
        return True

    # Stage and commit
    rc, out, err = run(['git', 'add', '-A'], repo_dir)
    if rc != 0:
        print(f'    ! git add failed: {err[:200]}', file=sys.stderr)
        return False
    rc, out, err = run(['git', 'diff', '--cached', '--quiet'], repo_dir)
    if rc == 0:
        print(f'    (no staged changes)')
        return True
    msg = ('docs: add community files (CONTRIBUTING, CoC, SECURITY, '
           'ISSUE_TEMPLATE, PR template) from csl-observatory templates\n\n'
           'Propagated by scripts/propagate_templates.py from\n'
           'github.com/sanskrit-lexicon/csl-observatory templates/.\n\n'
           'Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>')
    rc, out, err = run(['git', 'commit', '-m', msg], repo_dir)
    if rc != 0:
        print(f'    ! git commit failed: {err[:200]}', file=sys.stderr)
        return False
    print(f'    committed')
    return True


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('repos', nargs='*', default=DEFAULT_REPOS)
    ap.add_argument('--force', action='store_true', help='Overwrite existing files')
    ap.add_argument('--dry-run', action='store_true')
    ap.add_argument('--push', action='store_true', help='Run git push after commit')
    args = ap.parse_args()

    print(f'Propagating templates to {len(args.repos)} repos: {args.repos}')
    print(f'  templates source: {TEMPLATES}')
    print(f'  force={args.force} dry_run={args.dry_run} push={args.push}')
    print()

    success = 0
    for r in args.repos:
        if propagate(r, force=args.force, dry_run=args.dry_run):
            success += 1
            if args.push and not args.dry_run:
                rc, out, err = run(['git', 'push'], PARENT / r)
                if rc == 0:
                    print(f'    pushed')
                else:
                    print(f'    ! git push failed: {err[:200]}', file=sys.stderr)

    print(f'\nDone: {success}/{len(args.repos)} succeeded')


if __name__ == '__main__':
    main()
