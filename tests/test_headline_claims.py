"""H7122 — the headline-claims gate must pass on a clean tree and REFUSE a
mutated one. A gate that only ever passes proves nothing, so every refusal path
gets a positive control here."""
import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / 'scripts'))

import headline_claims as hc  # noqa: E402


@pytest.fixture()
def mutate():
    """Rewrite a repo file for the duration of one test, then restore it byte-exactly."""
    originals: dict[Path, str] = {}

    def _mutate(rel: str, old: str, new: str) -> Path:
        path = ROOT / rel
        if path not in originals:
            originals[path] = path.read_text(encoding='utf-8')
        text = originals[path]
        assert old in text, f'mutation anchor not found in {rel}: {old!r}'
        path.write_text(text.replace(old, new, 1), encoding='utf-8')
        return path

    yield _mutate
    for path, text in originals.items():
        path.write_text(text, encoding='utf-8')


def test_clean_tree_passes():
    """The committed tree must be claim-clean — otherwise the gate is noise."""
    assert hc.check(ROOT) == []


def test_registry_covers_every_surfaced_number():
    """Every claim points at a real file and actually matches something."""
    claims = hc.load_claims(ROOT)
    assert claims, 'registry is empty'
    for claim in claims:
        path = ROOT / claim.file
        assert path.exists(), f'{claim.id}: missing surface {claim.file}'
        text = path.read_text(encoding='utf-8')
        assert __import__('re').search(claim.pattern, text), (
            f'{claim.id}: pattern matches nothing in {claim.file}')


def test_snapshots_disagree_which_is_why_the_gate_exists():
    """The two snapshots are genuinely different — if they ever converge, the
    authority document and the divergence report need revisiting."""
    snaps = hc.snapshots(ROOT)
    live, offline = snaps[hc.LIVE_ID], snaps[hc.OFFLINE_ID]
    assert live.values['repos'] != offline.values['repos']
    assert live.values['issues_prs'] != offline.values['issues_prs']
    for snap in (live, offline):
        assert snap.values['issues'] + snap.values['prs'] == snap.values['issues_prs']


def test_mutated_number_is_refused_and_named(mutate):
    """Cross-snapshot contamination: the offline report quoting the live commit count."""
    mutate('reports/velocity_timeline.md',
           '| Commits (all repos, all years) | 13,299 |',
           '| Commits (all repos, all years) | 13,810 |')
    findings = hc.check(ROOT)
    assert any(f.claim_id == 'velocity.headline.commits' and f.line == 9 for f in findings), findings
    message = str(next(f for f in findings if f.claim_id == 'velocity.headline.commits'))
    assert '13,810' in message and '13,299' in message
    assert 'csl-obs/org@1.0.0' in message


def test_unregistered_number_is_refused(mutate):
    """A hand-typed headline number on a swept surface, with no claim behind it."""
    mutate('article/00-report-narrative.md',
           'same population as the 76 repositories',
           'same population as the 86 repos, 13,810 commits, and the 76 repositories')
    findings = hc.check(ROOT)
    assert any(f.claim_id == 'uncovered-number' and f.file == 'article/00-report-narrative.md'
               for f in findings), findings


def test_missing_claim_pattern_is_refused(mutate):
    """A surface rewritten so the claim no longer matches must fail, not silently pass."""
    mutate('reports/bus_factor.md',
           '| Distinct human contributors |',
           '| Human beings who contributed |')
    findings = hc.check(ROOT)
    assert any(f.claim_id == 'busfactor.headline.contributors' for f in findings), findings


def test_stale_allowlist_entry_is_refused(monkeypatch):
    """An exemption that no longer excuses anything is dead weight and must fail."""
    monkeypatch.setattr(hc, 'load_allowlist', lambda root=ROOT: [
        {'file': 'README.md', 'contains': 'text that appears nowhere in the repo',
         'reason': 'stale test fixture'}])
    findings = hc.check(ROOT)
    assert any(f.claim_id == 'stale-allowlist' for f in findings), findings


def test_pinned_historical_claim_requires_its_label(mutate):
    """A historical vintage that loses its snapshot ID must fail — that is the
    relabel half of the handoff, enforced."""
    mutate('docs/OBSERVATORY_ROADMAP.md',
           '*(historical vintage `csl-obs/org@hist-2026-06-17`)* ',
           '')
    findings = hc.check(ROOT)
    assert any(f.claim_id == 'roadmap.repo_health.historical'
               and 'must name its snapshot' in f.message for f in findings), findings


def test_check_cli_exit_codes():
    """--check is exit 0 on the clean tree and 1 on a mutation (the CI contract)."""
    clean = subprocess.run([sys.executable, 'scripts/update_headline_numbers.py', '--check'],
                           cwd=ROOT, capture_output=True, text=True)
    assert clean.returncode == 0, clean.stdout + clean.stderr
    assert 'PASS' in clean.stdout

    victim = ROOT / 'STATUS.md'
    original = victim.read_text(encoding='utf-8')
    try:
        mutated = original.replace('| Issues + PRs (lifetime) | 10,039 |',
                                   '| Issues + PRs (lifetime) | 7,006 |', 1)
        assert mutated != original
        victim.write_text(mutated, encoding='utf-8')
        red = subprocess.run([sys.executable, 'scripts/update_headline_numbers.py', '--check'],
                             cwd=ROOT, capture_output=True, text=True)
        assert red.returncode == 1, red.stdout + red.stderr
        assert 'FAIL' in red.stdout and 'status.headline.issues_prs' in red.stdout
    finally:
        victim.write_text(original, encoding='utf-8')


def test_registry_is_valid_json_and_claims_are_unique():
    raw = json.loads((ROOT / 'data/headline_claims.json').read_text(encoding='utf-8'))
    ids = [c['id'] for c in raw['claims']]
    assert len(ids) == len(set(ids)), 'duplicate claim ids'
    assert 'claims' in raw and 'allow_uncovered' in raw
