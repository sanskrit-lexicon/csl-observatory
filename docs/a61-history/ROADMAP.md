# A61/A13 roadmap

## Gate 1 — evidence integrity

- Apply maintainer-reviewed bot overrides consistently.
- Make the data catalog checkout-platform independent.
- Distinguish 78 API repositories from 76 transformed repositories.
- Replace “210 contributors” with the canonical 208 OBS-T corrector labels and
  its identity caveat.
- Correct the story-page periodisation: founding is 1994; 2019 is the first-PR
  milestone, not the arrival of Git.
- Freeze and validate `a61-history-v1.0`.

Acceptance: every A61 headline number has a metric ID, population definition,
source locator, cutoff, and caveat.

## Gate 2 — 24-hour FABLE packet

- Revise the abstract, introduction, history, correction, people, limitations,
  and conclusion/future sections around the causal thesis.
- Add a claim-to-evidence appendix and data-release citation.
- Write a hostile-referee memo with every Major/Minor finding marked applied or
  open.
- Create an explicit FABLE preparation handoff. A61 is a substantive 3/5 paper,
  so it enters the referee/preparation lane; it must not be falsely ticked as a
  completed author-voice pass.

Acceptance: the packet exists, its snapshot check passes, and the routing state
names the correct next workflow.

## Gate 3 — 30-hour argument development

- Test the causal thesis against technical-determinist, institutional-hosting,
  and heroic-individual rival explanations.
- Remove teleology: each transition must be described as contingent, with the
  losses and exclusions it introduced.
- Distinguish preservation of data from continuity of active maintenance.
- Give correction sociology to A61; give repository-evidence limits and the
  founder-to-community transition to A13.

Acceptance: the thesis survives the counterargument section and every causal
verb is backed by a mechanism, not chronology alone.

## Gate 4 — one-month observatory hardening

- Restore reliable scheduled refresh with retry/cache/freshness guards.
- Recompute all live snapshots from clean full-history sources.
- Regenerate every stale report, prompt, hub, and statistics-census row.
- Add CI tests for metric definitions and snapshot consumers.

This gate is intentionally not a blocker for the first article handoff.

