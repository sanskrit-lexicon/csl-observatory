# A61/A13 implementation contract

## Article-critical code changes

1. `scripts/bus_factor.py` treats `scripts/contributors_map.json` as the
   authoritative bot override when GitHub reports automation as `User`.
2. `scripts/data_index.py` measures canonical LF content so Windows checkouts
   match Linux CI.
3. `scripts/build_article_snapshot.py` derives and validates the versioned
   evidence bundle.
4. The story page uses historically accurate labels and bounded completeness
   language.
5. The statistics census and all A61 uses adopt the snapshot's metric IDs and
   definitions.
6. The v1.1 builder validates claim evidence IDs, preserves exactly two
   `evidence_pending` email milestones, rejects the stale four-implementer form,
   and enforces the protected A13 SHA-256.

## Manuscript changes

- Abstract: state the causal thesis and replace the undifferentiated
  contributor count.
- Introduction: pose the paper as an explanation of endurance, not a catalogue
  of assets.
- History: periodise by changes in custody and corrigibility—1994 institutional
  production, 2004 collaborative formalisation, 2013 archival transfer, 2014
  public versioning, 2026 succession.
- Corrections: distinguish submitter labels, implementers, and completeness;
  remove untraceable locus/batch figures unless they receive snapshot metrics.
- People: present geography as a shift in the organisation of labour, not a
  national-character explanation.
- Limitations: state repository survival bias, pre-2014 archival opacity,
  identity ambiguity, snapshot staleness, and the difference between preserved
  data and maintained services.
- Conclusion: argue that endurance came from serial institutional conversion,
  while noting that each conversion left a new single point of failure.

## FABLE routing

The current FABLE disposition index does not assign A61 to the author-voice
lane. Therefore the compliant route is:

1. finish the substantive/referee packet;
2. record an A61 preparation handoff with exact evidence prerequisites;
3. leave the later author-voice pass unticked until A61 reaches the appropriate
   post-referee state.

No remote push or PR is performed in this pass; the user selected isolated
local branches and commits without pushing.

## v1.1 rulings implemented

- **Evidence:** the frozen A61 manuscript uses 208 OBS-T labels and five annual
  implementers. Each M10 disposition is applied in the registry: retained
  values are verified, while unsupported or stale exact figures are explicitly
  removed/superseded. The canonical MW print-change and hiatus audits remain
  hash-locked as audit evidence, not retained manuscript claims.
- **Legal:** remove the causal public-domain conclusion for Apte 1957 unless a
  rights determination identifies relevant authorship and term. Keep the
  database-right episode only as attributed historical evidence.
- **Venue:** official deadline 1 February 2027; headline/table dates 10–14
  December 2027; official footer contradiction 10–15 December; no published
  word limit as of 18 July 2026.
- **Build:** run snapshot write/check, data-index check, workspace, OBS-T and
  repository-health regressions. Attempt the site build three times; repeated
  external CDN failure is reported separately from deterministic regressions.
