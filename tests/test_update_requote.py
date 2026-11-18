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

Anchors are DERIVED from the committed snapshots, never literal: every value
below moves on every live refresh, and a literal anchor rots the suite at the
next snapshot (the 2026-11-18 landing rotted this file's own first draft and
two controls in test_headline_claims.py — same failure class, now structural).
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / 'scripts'))

import headline_claims as hc  # noqa: E402
import update_headline_numbers as uhn  # noqa: E402

ANTHOLOGY = 'docs/ANTHOLOGY_ALIGNMENT_2026Q4.md'
DIVERGENCE = 'reports/snapshot_divergence.md'


def _live():
    return hc.snapshots(ROOT)[hc.LIVE_ID]


def _live_row(live) -> str:
    v = live.values
    return (f'| `csl-obs/org-live@1.0.0` | {live.as_of} | {v["repos"]:,} | '
            f'{v["issues"]:,} | {v["prs"]:,} | {v["issues_prs"]:,} | '
            f'{v["commits"]:,} | {v["contributors"]} |')


def _anth_quoted(live) -> str:
    v = live.values
    return (f'{v["repos"]} repos, {v["issues_prs"]:,} issues+PRs, '
            f'{v["commits"]:,} commits, {v["contributors"]} contributors')


def _anth_paren(live) -> str:
    v = live.values
    return (f'(snapshot {live.as_of}: {v["repos"]} repos, {v["issues"]:,} issues '
            f'+ {v["prs"]:,} PRs, {v["commits"]:,} commits)')


def _delta_tail(live, offline) -> str:
    def signed(x):
        return f'{x:,}' if x >= 0 else f'−{abs(x):,}'

    c = live.values['commits'] - offline.values['commits']
    k = live.values['contributors'] - offline.values['contributors']
    return f'{signed(c)} commits, {signed(k)} contributors.'


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
    live = _live()
    fresh, stale = _anth_quoted(live), _anth_quoted(live).replace('9', '8')
    p = _keep(restore, ANTHOLOGY)
    text = p.read_text(encoding='utf-8')
    assert fresh in text, 'anchor rotted: derive from the committed snapshot'
    p.write_text(text.replace(fresh, stale, 1), encoding='utf-8')
    changed = uhn.requote_live_claims()
    assert ANTHOLOGY in changed
    assert fresh in p.read_text(encoding='utf-8')


def test_stale_parenthetical_restatement_is_requoted(restore):
    """alignment.quoted.live_split (extended in H7879) covers the parenthetical
    "(snapshot <date>: N repos, X issues + Y PRs, Z commits)" — including the
    repos group, which the pre-extension pattern left stale and unchecked."""
    live = _live()
    fresh = _anth_paren(live)
    stale = re.sub(r'\d', lambda m: str(max(1, int(m.group(0)) - 1)), fresh)
    p = _keep(restore, ANTHOLOGY)
    text = p.read_text(encoding='utf-8')
    assert fresh in text, 'anchor rotted: derive from the committed snapshot'
    p.write_text(text.replace(fresh, stale, 1), encoding='utf-8')
    changed = uhn.requote_live_claims()
    assert ANTHOLOGY in changed
    assert fresh in p.read_text(encoding='utf-8')


def test_divergence_live_row_and_as_of_are_requoted(restore):
    live = _live()
    fresh = _live_row(live)
    stale = fresh.replace(live.as_of, '2026-01-01')
    p = _keep(restore, DIVERGENCE)
    text = p.read_text(encoding='utf-8')
    assert fresh in text, 'anchor rotted: derive from the committed snapshot'
    p.write_text(text.replace(fresh, stale, 1), encoding='utf-8')
    changed = uhn.requote_live_claims()
    assert DIVERGENCE in changed
    assert fresh in p.read_text(encoding='utf-8')


def test_stale_delta_line_is_recomputed(restore):
    """The delta line is derived by definition (live − offline); a stale one
    is recomputed, a current one is left byte-untouched."""
    live, offline = _live(), hc.snapshots(ROOT)[hc.OFFLINE_ID]
    fresh = _delta_tail(live, offline)
    stale = fresh.replace(fresh.split(' ')[0], '−999', 1)
    p = _keep(restore, DIVERGENCE)
    text = p.read_text(encoding='utf-8')
    assert fresh in text, 'anchor rotted: derive from the committed snapshots'
    p.write_text(text.replace(fresh, stale, 1), encoding='utf-8')
    changed = uhn.requote_live_claims()
    assert DIVERGENCE in changed
    assert fresh in p.read_text(encoding='utf-8')


def test_pinned_collision_claims_pass_the_gate():
    """The three H7879 collision pins must hold on the committed tree: the
    values the 2026-11-18 refresh turned into sweep tokens (68 contributors_all
    vs README's prose "68 repos"; 12,106 total_commits vs the mw form-recapture
    estimate; 65 contributors vs A15's frozen "65 repositories") are registered
    with their true provenance, so the gate stays green after a live refresh."""
    findings = [f for f in hc.check(ROOT) if f.claim_id in (
        'readme.agent_roadmap_repos',
        'corrector_recapture.mw_form_estimate',
        'article.a15.single_departure_repos',
    )]
    assert findings == [], findings
