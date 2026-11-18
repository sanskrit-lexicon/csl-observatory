"""H7879 — the write half must cover every registered LIVE claim, not just
README/STATUS.

The 2026-11-18 dispatch proved the gap end-to-end: the fetch lane was repaired,
pull_data + compute_metrics + render_reports ran green, README/STATUS were
re-quoted — and --check still refused the commit with 16 findings, because
docs/ANTHOLOGY_ALIGNMENT_2026Q4.md and reports/snapshot_divergence.md carry
registered live claims that nothing rewrote (past cycles synced them by hand:
#310, 51b13b7 — and the sync PR's own commits moved the live counts again).
requote_live_claims() is the write twin of headline_claims.check(); these pins
fail on the pre-fix state (no such function) and hold it to its contract.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / 'scripts'))

import update_headline_numbers as uhn  # noqa: E402

ANTHOLOGY = 'docs/ANTHOLOGY_ALIGNMENT_2026Q4.md'
DIVERGENCE = 'reports/snapshot_divergence.md'

LIVE_ROW = ('| `csl-obs/org-live@1.0.0` | 2026-09-28 | 86 | 7,877 | 2,162 | '
            '10,039 | 13,810 | 72 |')
ANTH_QUOTED = '86 repos, 10,039 issues+PRs, 13,810 commits, 72 contributors'
ANTH_PAREN = '(snapshot 2026-09-28: 86 repos, 7,877 issues + 2,162 PRs, 13,810 commits)'
DELTA_TAIL = '−132 commits, 56 contributors.'


@pytest.fixture()
def restore():
    """Restore every touched repo file byte-exactly after one test."""
    originals: dict[Path, str] = {}
    yield originals
    for path, text in originals.items():
        path.write_text(text, encoding='utf-8')


def _keep(restore, rel: str) -> Path:
    path = ROOT / rel
    if path not in restore:
        restore[path] = path.read_text(encoding='utf-8')
    return path


def test_clean_tree_is_a_no_op(restore):
    """Idempotence: on an already-synced tree nothing is rewritten — not even
    the divergence delta line's hard wrap (the first implementation reflowed
    it and churned a clean commit)."""
    assert uhn.requote_live_claims() == []


def test_stale_live_claim_is_requoted(restore):
    p = _keep(restore, ANTHOLOGY)
    stale = '84 repos, 9,999 issues+PRs, 13,000 commits, 71 contributors'
    p.write_text(p.read_text(encoding='utf-8').replace(ANTH_QUOTED, stale, 1),
                 encoding='utf-8')
    changed = uhn.requote_live_claims()
    assert ANTHOLOGY in changed
    assert ANTH_QUOTED in p.read_text(encoding='utf-8')


def test_stale_parenthetical_restatement_is_requoted(restore):
    """alignment.quoted.live_split (extended in H7879) covers the parenthetical
    "(snapshot <date>: N repos, X issues + Y PRs, Z commits)" — including the
    repos group, which the pre-extension pattern left stale and unchecked."""
    p = _keep(restore, ANTHOLOGY)
    stale = ('(snapshot 2026-08-01: 80 repos, 7,000 issues + 2,000 PRs, '
             '13,000 commits)')
    p.write_text(p.read_text(encoding='utf-8').replace(ANTH_PAREN, stale, 1),
                 encoding='utf-8')
    changed = uhn.requote_live_claims()
    assert ANTHOLOGY in changed
    assert ANTH_PAREN in p.read_text(encoding='utf-8')


def test_divergence_live_row_and_as_of_are_requoted(restore):
    p = _keep(restore, DIVERGENCE)
    stale = (LIVE_ROW.replace('2026-09-28', '2026-08-01')
             .replace('86', '80').replace('7,877', '7,000')
             .replace('2,162', '2,000').replace('10,039', '9,000')
             .replace('13,810', '13,000').replace('72', '70'))
    p.write_text(p.read_text(encoding='utf-8').replace(LIVE_ROW, stale, 1),
                 encoding='utf-8')
    changed = uhn.requote_live_claims()
    assert DIVERGENCE in changed
    assert LIVE_ROW in p.read_text(encoding='utf-8')


def test_stale_delta_line_is_recomputed(restore):
    """The delta line is derived by definition (live − offline); a stale one
    is recomputed, a current one is left byte-untouched."""
    p = _keep(restore, DIVERGENCE)
    stale_tail = '−999 commits, 55 contributors.'
    assert DELTA_TAIL in p.read_text(encoding='utf-8')
    p.write_text(p.read_text(encoding='utf-8').replace(DELTA_TAIL, stale_tail, 1),
                 encoding='utf-8')
    changed = uhn.requote_live_claims()
    assert DIVERGENCE in changed
    assert DELTA_TAIL in p.read_text(encoding='utf-8')


def test_pinned_collision_claims_pass_the_gate():
    """The three H7879 collision pins must hold on the committed tree: the
    values the 2026-11-18 refresh turned into sweep tokens (68 contributors_all
    vs README's prose "68 repos"; 12,106 total_commits vs the mw form-recapture
    estimate; 65 contributors vs A15's frozen "65 repositories") are registered
    with their true provenance, so the gate stays green after a live refresh."""
    import headline_claims as hc  # noqa: PLC0415 — sibling import
    findings = [f for f in hc.check(ROOT) if f.claim_id in (
        'readme.agent_roadmap_repos',
        'corrector_recapture.mw_form_estimate',
        'article.a15.single_departure_repos',
    )]
    assert findings == [], findings
