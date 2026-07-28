# A61/A13 history-evidence plan

Status: active, 18 July 2026. Primary paper: A61. Complementary paper: A13.

## Outcome

A61 becomes the canonical historical synthesis. Its main causal claim is that
CDSL endured because it repeatedly converted fragile personal scholarship into
maintainable shared infrastructure. A13 is not a memoir derivative: it will
examine what repository evidence cannot recover and the transition from a
founder-led project to community infrastructure in greater methodological
depth.

The first gate is a verified A61 argument/evidence packet routed to the FABLE
pipeline within 24 hours. The remaining argument budget is 30 hours. A broad
observatory hardening pass follows after one month; only article-critical
repairs belong to this first wave.

## Prior-art verdict: partial reuse

Do not build another observatory or correction corpus. Reuse:

- OBS-T for documented correction events;
- OBS-Q for correction-implementation concentration;
- the existing repository, issue, and contributor snapshots;
- A13, A14, A15, and the current A61 draft;
- the cross-repository statistics census.

The missing artifact is narrower: one frozen article snapshot with explicit
populations, a claim registry, a contradiction ledger, and a sourced milestone
layer. This plan supplies that layer at
`data/publication/a61-history-v1.1/`; the preceding v1.0 release remains
immutable.

## Work order

1. Resolve contradictions and provenance defects.
2. Freeze the versioned evidence snapshot (`a61-history-v1.1`, alias
   `2026-07`).
3. Rewrite A61 around the causal argument and evidence limits.
4. Run a hostile referee pass and route the verified packet to FABLE.
5. Develop A13's complementary methodological argument.
6. After one month, harden the entire scheduled observatory refresh and all
   stale consumers.

## Scope decisions

- A61 owns the synthesis and exact, defined measures.
- A13 may use ranges where historical identity or collection completeness is
  irreducibly uncertain.
- Shared claim IDs and evidence are reused; prose is written separately.
- Later historical email enters through `milestones.csv` rows currently marked
  `evidence_pending`. No current load-bearing claim depends on those rows.
- Private quotations, byline choices, permissions, and strong personal
  judgments remain human decisions.

## v1.1 evidence, legal, venue, and build rulings

- Evidence: every retained empirical/project number in A61 through the
  conclusion (excluding references) is inventoried in `claim_registry.csv`.
  Retained M10 figures are hash-locked; removed stale figures are labelled
  removed/superseded. The two email milestones remain `evidence_pending`.
- Legal: do not infer Apte 1957 public-domain status from editor/publisher death
  dates. State only observed 2025 availability until a documented rights
  determination exists. Treat the 2004 database-right language as attributed
  history, not present legal advice.
- Venue: the official IIT Bombay page (checked 18 July 2026) sets the abstract
  deadline at 1 February 2027 and headline/Important Dates at 10–14 December
  2027; its footer says 10–15 December. Plan on 10–14 pending clarification.
  No word limit is currently published.
- Build: snapshot generation/check, data index, workspace, OBS-T and
  repository-health regressions are mandatory. The Observable build is best
  effort with three attempts for external `npm:d3*` CDN timeouts.

## Linked execution documents

- [Roadmap](ROADMAP.md)
- [Architecture](ARCHITECTURE.md)
- [Implementation](IMPLEMENTATION.md)
- [Verification](VERIFICATION.md)
