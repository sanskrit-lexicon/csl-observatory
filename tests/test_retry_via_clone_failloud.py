"""retry_via_clone.py must FAIL LOUD on partial coverage (21-11 regression).

The two refresh dispatches on 21-11 differed by 1,820 commits. The landed run
never re-cloned csl-orig because autodetect_failed() only sees `commits == []`
and GraphQL had returned 200 of 2,295 — a partial page accepted as a full
history. The other silent path was fetch_commits_via_clone() returning [] on a
clone/log failure and main() committing that empty list. Both paths are pinned
here with positive (red) and negative (green) controls.
"""
import json
import subprocess
import sys

import pytest
from conftest import REPO_ROOT

sys.path.insert(0, str(REPO_ROOT / "scripts"))

import retry_via_clone as rc  # noqa: E402


@pytest.fixture()
def data(tmp_path):
    d = tmp_path / 'data'
    snap = d / 'snapshots' / '2026-11-18'
    snap.mkdir(parents=True)
    prior = {
        'csl-orig': [{'oid': str(i)} for i in range(1000)],
        'stable': [{'oid': str(i)} for i in range(50)],
    }
    current = {
        'csl-orig': [{'oid': str(i)} for i in range(200)],  # 80% drop
        'stable': [{'oid': str(i)} for i in range(49)],     # jitter, ignore
    }
    (snap / 'commits.json').write_text(json.dumps(prior), encoding='utf-8')
    (d / 'commits.json').write_text(json.dumps(current), encoding='utf-8')
    (d / 'repos.json').write_text(json.dumps([
        {'name': 'csl-orig', 'size': 900000, 'fork': False, 'archived': False},
        {'name': 'stable', 'size': 100, 'fork': False, 'archived': False},
    ]), encoding='utf-8')
    (d / 'summary.json').write_text(json.dumps(
        {'snapshot_date': '2026-11-18', 'total_commits': 249}), encoding='utf-8')
    return d


def test_partial_coverage_detects_material_drop(data):
    bad = rc.partial_coverage_repos(data)
    assert 'csl-orig' in bad, bad
    assert bad['csl-orig'] == (200, 1000)
    assert 'stable' not in bad, 'a one-commit jitter must not trip the guard'


def test_clone_failure_raises_instead_of_returning_empty(monkeypatch):
    monkeypatch.setattr(rc, 'run', lambda *a, **k: subprocess.CompletedProcess(
        [], 128, stdout='', stderr='fatal: unable to access repo'))
    with pytest.raises(RuntimeError, match='clone failed'):
        rc.fetch_commits_via_clone('csl-orig')


def test_git_log_failure_raises_instead_of_returning_empty(monkeypatch):
    calls = []

    def fake_run(cmd, **kw):
        calls.append(cmd)
        if calls and cmd[1] == '--git-dir':
            return subprocess.CompletedProcess(cmd, 128, stdout='', stderr='bad log')
        return subprocess.CompletedProcess(cmd, 0, stdout='', stderr='')

    monkeypatch.setattr(rc, 'run', fake_run)
    with pytest.raises(RuntimeError, match='git log failed'):
        rc.fetch_commits_via_clone('csl-orig')


def test_main_refuses_all_writes_on_clone_failure(data, monkeypatch):
    monkeypatch.setattr(rc, 'DATA', data)
    monkeypatch.setattr(sys, 'argv', ['retry_via_clone.py', 'csl-orig'])

    def boom(name):
        raise RuntimeError('simulated clone failure')

    monkeypatch.setattr(rc, 'fetch_commits_via_clone', boom)
    before = (data / 'commits.json').read_text(encoding='utf-8')
    summary_before = (data / 'summary.json').read_text(encoding='utf-8')
    with pytest.raises(SystemExit) as e:
        rc.main()
    assert e.value.code == 1
    assert (data / 'commits.json').read_text(encoding='utf-8') == before
    assert (data / 'summary.json').read_text(encoding='utf-8') == summary_before
    assert not (data / 'snapshots' / __import__('datetime').date.today().isoformat()).exists()


def test_main_recovers_partial_repo_and_writes(data, monkeypatch):
    monkeypatch.setattr(rc, 'DATA', data)
    monkeypatch.setattr(sys, 'argv', ['retry_via_clone.py', 'csl-orig'])
    monkeypatch.setattr(rc, 'fetch_commits_via_clone',
                        lambda name: [{'oid': str(i)} for i in range(1000)])
    rc.main()
    written = json.loads((data / 'commits.json').read_text(encoding='utf-8'))
    assert len(written['csl-orig']) == 1000
    summary = json.loads((data / 'summary.json').read_text(encoding='utf-8'))
    assert summary['retry_via_clone'] == {'csl-orig': 1000}
