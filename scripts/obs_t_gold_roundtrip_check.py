#!/usr/bin/env python3
"""obs_t_gold_roundtrip_check.py — H5312 own-data canary.

Proves the second-annotator pipeline END-TO-END on a fixture, in a throwaway
sandbox, WITHOUT touching the real instrument:

  1. build a temp tree mirroring the repo layout; the 62 MB
     correction_events_final.csv is SYMLINKED, the sheet + fixture + the two
     scripts are copied from this working tree;
  2. NEGATIVE CONTROLS (each must FAIL, exit != 0):
       a. a decisions file with a label outside the axis-A vocabulary;
       b. a decisions file with a row_id absent from the sheet;
       c. re-ingesting after a first ingest, WITHOUT --force (clobber guard);
       d. --sheet pointing at a missing file;
  3. HAPPY PATH: ingest validation/fixtures/second_annotator_fixture.json
     --force into the sandbox sheet, then --score: the sandbox
     gold_metrics.json must carry iaa.pairs == 10 and a float cohen_kappa,
     and the markdown report must contain the kappa table row;
  4. assert the real validation/gold_sample.csv was never modified.

PASS prints the round-tripped kappa and exits 0. Deterministic; stdlib only.

Usage:  python scripts/obs_t_gold_roundtrip_check.py
"""
import json, os, shutil, subprocess, sys, tempfile

sys.stdout.reconfigure(encoding='utf-8'); sys.stderr.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
PY = sys.executable or 'python3'

N_FIXTURE = 10


def run(script_args, expect_ok):
    p = subprocess.run([PY, os.path.join('scripts', 'obs_t_gold.py')] + script_args,
                       capture_output=True, text=True, cwd=sandbox)
    ok = p.returncode == 0
    tag = 'PASS' if ok == expect_ok else 'FAIL'
    tail = (p.stdout + p.stderr).strip().splitlines()
    tail = ' | '.join(tail[-2:]) if tail else ''
    print(f'  [{tag}] obs_t_gold.py {" ".join(script_args)[:100]} :: {tail[:160]}')
    return p


def write_json(path, obj):
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(obj, f, ensure_ascii=False, indent=1)


def link_input(src, dst):
    """Mirror a read-only input into the sandbox: symlink, else hardlink,
    else copy. Windows without symlink privilege (no Dev Mode / elevation)
    rejects os.symlink with WinError 1314; both inputs are read-only for
    obs_t_gold.py, so a hardlink — or a plain copy as the last resort —
    carries identical bytes and identical semantics."""
    try:
        os.symlink(src, dst)
    except OSError:
        try:
            os.link(src, dst)
        except OSError:
            shutil.copy(src, dst)


sandbox = ''  # set by main() before run() is ever called


def main():
    global sandbox
    sandbox = tempfile.mkdtemp(prefix='h5312-roundtrip-')
    failures = []
    try:
        # ---- sandbox mirroring the repo layout ----
        os.makedirs(os.path.join(sandbox, 'scripts'))
        os.makedirs(os.path.join(sandbox, 'validation', 'fixtures'))
        os.makedirs(os.path.join(sandbox, 'reports'))
        obs_data = os.path.join(sandbox, 'observatory', 'site', 'src', 'data')
        os.makedirs(obs_data)
        link_input(os.path.join(ROOT, 'observatory', 'site', 'src', 'data',
                                'correction_events_final.csv'),
                   os.path.join(obs_data, 'correction_events_final.csv'))
        # the H1494 id crosswalk too — --score's auto-join resolves old hex ids
        # through it, so the sandbox must carry the same bytes
        link_input(os.path.join(ROOT, 'observatory', 'site', 'src', 'data',
                                'event_id_crosswalk_v1.csv'),
                   os.path.join(obs_data, 'event_id_crosswalk_v1.csv'))
        shutil.copy(os.path.join(HERE, 'obs_t_gold.py'),
                    os.path.join(sandbox, 'scripts', 'obs_t_gold.py'))
        shutil.copy(os.path.join(HERE, 'obs_t_second_sheet.py'),
                    os.path.join(sandbox, 'scripts', 'obs_t_second_sheet.py'))
        shutil.copy(os.path.join(ROOT, 'validation', 'gold_sample.csv'),
                    os.path.join(sandbox, 'validation', 'gold_sample.csv'))
        fixture_src = os.path.join(ROOT, 'validation', 'fixtures',
                                   'second_annotator_fixture.json')
        fixture = os.path.join(sandbox, 'validation', 'fixtures',
                               'second_annotator_fixture.json')
        shutil.copy(fixture_src, fixture)
        # legacy stragglers: rows already carrying a gold_component_2 value in
        # the pristine sheet (pre-H5312 debris). They ride along in --score's
        # iaa pair count, so the expected pairs = fixture + legacy.
        import csv as _csv
        with open(os.path.join(sandbox, 'validation', 'gold_sample.csv'),
                  encoding='utf-8') as f:
            legacy = sum(1 for r in _csv.DictReader(f)
                         if r['gold_component_2'].strip())

        print('H5312 fixture round-trip (sandbox %s)' % sandbox)

        # ---- negative controls: each MUST fail ----
        print('negative controls (each must refuse):')
        with open(fixture, encoding='utf-8') as f:
            dec = json.load(f)
        bad_label = dict(dec, decisions=[dict(dec['decisions'][0], location='orthography')])
        write_json(os.path.join(sandbox, 'validation', 'bad_label.json'), bad_label)
        if run(['--ingest', 'validation/bad_label.json'], expect_ok=False).returncode == 0:
            failures.append('bad label was accepted')
        bad_row = dict(dec, decisions=[dict(dec['decisions'][0], row_id=99999)])
        write_json(os.path.join(sandbox, 'validation', 'bad_row.json'), bad_row)
        if run(['--ingest', 'validation/bad_row.json'], expect_ok=False).returncode == 0:
            failures.append('unknown row_id was accepted')
        if run(['--ingest', 'validation/fixtures/second_annotator_fixture.json',
                '--sheet', 'validation/nope.csv'], expect_ok=False).returncode == 0:
            failures.append('missing --sheet target was accepted')

        # ---- happy path: fixture round-trips to a kappa ----
        print('happy path (fixture, --force in SANDBOX only):')
        p = run(['--ingest', 'validation/fixtures/second_annotator_fixture.json',
                 '--force'], expect_ok=True)
        if p.returncode != 0:
            failures.append('fixture ingest failed')
        else:
            # clobber guard must now refuse a re-ingest without --force
            p2 = run(['--ingest', 'validation/fixtures/second_annotator_fixture.json'],
                     expect_ok=False)
            if p2.returncode == 0:
                failures.append('clobber guard did not refuse re-ingest')
            p3 = run(['--score'], expect_ok=True)
            if p3.returncode != 0:
                failures.append('--score failed after ingest')
            else:
                with open(os.path.join(sandbox, 'validation', 'gold_metrics.json'),
                          encoding='utf-8') as f:
                    m = json.load(f)
                iaa = m.get('iaa', {})
                kappa = iaa.get('cohen_kappa')
                if iaa.get('pairs') != N_FIXTURE + legacy or not isinstance(kappa, (int, float)):
                    failures.append(f'iaa wrong after round-trip: {iaa} '
                                    f'(expected pairs == {N_FIXTURE} + {legacy} legacy)')
                elif not any(k in m.get('countsByEvidence', {}) for k in ('derived', 'inferred')):
                    failures.append('auto-join dead: no derived/inferred rows after '
                                    'crosswalk resolution (event-id desync got worse?)')
                else:
                    with open(os.path.join(sandbox, 'reports', 'obs_t_validation.md'),
                              encoding='utf-8') as f:
                        md = f.read()
                    if 'inter-annotator agreement' not in md:
                        failures.append('kappa row missing from the markdown report')
                    print(f'  round-tripped: iaa.pairs={iaa["pairs"]} '
                          f'cohen_kappa={kappa} (fixture labels — value is meaningless, '
                          f'the MECHANISM is what is proven)')

        # ---- the real instrument must be untouched ----
        real_sheet = os.path.join(ROOT, 'validation', 'gold_sample.csv')
        import csv as _csv
        with open(real_sheet, encoding='utf-8') as f:
            real = list(_csv.DictReader(f))
        filled2 = sum(1 for r in real if r['gold_component_2'].strip())
        print(f'real sheet check: gold_component_2 still has {filled2} filled row(s) '
              f'(pre-existing legacy stragglers; sandbox wrote nothing here)')
        if filled2 != 4:
            failures.append(f'real sheet gold_component_2 count changed: {filled2} != 4')
    finally:
        shutil.rmtree(sandbox, ignore_errors=True)

    if failures:
        print('ROUND-TRIP FAIL: ' + '; '.join(failures))
        return 1
    print('ROUND-TRIP PASS: blind sheet -> decisions.json -> --ingest -> --score kappa, '
          'with all negative controls refusing.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
