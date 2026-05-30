#!/usr/bin/env python3
"""Validate ```mermaid``` blocks in Markdown files via GitHub's markdown API.

Usage:
    python scripts/validate_mermaid.py FILE [FILE ...]

Exits non-zero if any ```mermaid``` block is not recognised as Mermaid by
GitHub's renderer (i.e. the rendered HTML lacks `highlight-source-mermaid`
with `pl-*` syntax spans). Requires an authenticated `gh`.

Use this before committing generated docs/READMEs that embed Mermaid. Stick to
diagram types GitHub renders (`pie`, `flowchart`, `graph`, `sequenceDiagram`,
`gantt`); never use `xychart-beta` (unsupported).
"""
import subprocess, sys, re
sys.stdout.reconfigure(encoding='utf-8')


def check_file(path):
    text = open(path, encoding='utf-8').read()
    blocks = re.findall(r'```mermaid\n(.*?)```', text, re.DOTALL)
    ok = True
    for i, b in enumerate(blocks, 1):
        r = subprocess.run(
            ['gh', 'api', 'markdown', '-X', 'POST', '-f', f'text=```mermaid\n{b}```', '-f', 'mode=markdown'],
            capture_output=True, encoding='utf-8')
        valid = ('highlight-source-mermaid' in r.stdout) and ('pl-' in r.stdout)
        title = next((ln.strip() for ln in b.strip().splitlines() if ln.strip()), '')[:48]
        print(f'  {path} [block {i}: {title}]: {"VALID" if valid else "INVALID"}')
        ok = ok and valid
    return ok, len(blocks)


def main(paths):
    all_ok, total = True, 0
    for p in paths:
        ok, n = check_file(p)
        total += n
        all_ok = all_ok and ok
    print(f'{total} mermaid block(s) across {len(paths)} file(s): {"ALL VALID" if all_ok else "INVALID present"}')
    sys.exit(0 if all_ok else 1)


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('usage: validate_mermaid.py FILE [FILE ...]', file=sys.stderr)
        sys.exit(2)
    main(sys.argv[1:])
