#!/usr/bin/env python3
"""Does `recapture_sensitivity.py --selftest` catch model mutations? (H5221)

Review 3 of H5072 ran sixteen mutations of the statistical content; ten passed the
whole suite. `reports/recapture_sensitivity.md` section 9 item 6 names three of them.
This harness re-applies those three (plus two companions) to a temporary copy of the
script, runs its selftest, and reports CAUGHT (selftest failed) or SURVIVED.

Exit 0 when every named mutation is caught and the unmutated copy passes.

Usage:  python scripts/recapture_mutation_check.py
"""
import os, shutil, subprocess, sys, tempfile

sys.stdout.reconfigure(encoding='utf-8'); sys.stderr.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
TARGET = os.path.join(HERE, 'recapture_sensitivity.py')

# (name, named-in-section-9-item-6?, old text, new text, expected occurrences)
MUTATIONS = (
    ('era-2 survival exponent altered in BOTH joint derivations', True,
     'b = (1.0 - a) * (q2 * th)', 'b = (1.0 - a) ** 2 * (q2 * th)', 2),
    ('Petersen substituted for Chapman in the simulated point estimate', True,
     '        n_hat, se, lo, hi = ER.chapman(n1, n2, m)\n',
     '        n_hat, se, lo, hi = ER.chapman(n1, n2, m)\n'
     '        n_hat = n1 * n2 / m\n', 1),
    ('log-likelihood negated', True,
     'll = (math.lgamma(n + 1)', 'll = -(math.lgamma(n + 1)', 1),
    ('sequential-only era-2 survival exponent altered', False,
     'c2 = b + ((1 - q1) ** k) * (1 - (1 - q2) ** k)',
     'c2 = b + ((1 - q1) ** (k + 1)) * (1 - (1 - q2) ** k)', 1),
    ('removal dropped from both joint derivations (era 2 sees fixed errors)', False,
     'b = (1.0 - a) * (q2 * th)', 'b = (q2 * th)', 2),
)


def run_selftest(src_text, workdir):
    """Write `src_text` beside a copy of the sibling modules and run its selftest."""
    path = os.path.join(workdir, 'scripts', 'recapture_sensitivity.py')
    with open(path, 'w', encoding='utf-8') as f:
        f.write(src_text)
    r = subprocess.run([sys.executable, path, '--selftest'], capture_output=True,
                       text=True, encoding='utf-8')
    fails = [ln for ln in r.stdout.splitlines() if ln.startswith('FAIL')]
    return r.returncode, fails


def main():
    with open(TARGET, encoding='utf-8') as f:
        base = f.read()
    ok = True
    with tempfile.TemporaryDirectory() as tmp:
        # the script imports its siblings and reads data relative to ROOT
        shutil.copytree(HERE, os.path.join(tmp, 'scripts'),
                        ignore=shutil.ignore_patterns('__pycache__'))
        data_src = os.path.join(os.path.dirname(HERE), 'observatory')
        if os.path.isdir(data_src):
            os.symlink(data_src, os.path.join(tmp, 'observatory'))
        rc, fails = run_selftest(base, tmp)
        print(f"{'PASS' if rc == 0 else 'FAIL'}  unmutated selftest"
              + (f" — {len(fails)} failing check(s)" if rc else ''))
        ok &= rc == 0
        for name, named, old, new, count in MUTATIONS:
            found = base.count(old)
            if found != count:
                print(f'ERROR {name}: expected {count} occurrence(s), found {found}')
                ok = False
                continue
            rc, fails = run_selftest(base.replace(old, new), tmp)
            caught = rc != 0
            tag = 'named §9.6' if named else 'companion'
            print(f"{'CAUGHT  ' if caught else 'SURVIVED'} [{tag}] {name}")
            for ln in fails:
                print(f'          {ln[:150]}')
            if named and not caught:
                ok = False
    print('\nmutation check', 'PASSED' if ok else 'FAILED')
    return 0 if ok else 1


if __name__ == '__main__':
    sys.exit(main())
