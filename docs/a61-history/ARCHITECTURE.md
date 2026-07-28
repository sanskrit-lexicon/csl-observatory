# Evidence architecture for A61 and A13

## Ownership

A61 is the canonical synthesis. A13 is a complementary analytical paper. The
single factual authority shared by both is the article snapshot, not either
paper's prose.

```text
committed source datasets
        |
        v
a61-history-v1.1
  metrics.csv -------- exact populations and cutoffs
  milestones.csv ----- sourced events and pending archival slots
  claim_registry.csv - paper claims joined to evidence IDs
  contradictions.csv - rejected/stale forms and resolutions
  source_artifacts.csv + manifest.json - content locks
        |                           |
        v                           v
 A61 synthesis              A13 methodological depth
```

## Evidence tiers

1. **Computed/committed:** reproducible datasets, scripts, and repository
   records. These support exact counts.
2. **Archival or attributed testimony:** published reports, correspondence,
   project files, and recorded oral history with a precise locator. These may
   support historical statements with attribution.
3. **Contextual inference:** interpretation assembled from tiers 1–2. It must be
   labelled as argument and cannot silently become an exact historical fact.

Pending email rows form a fourth workflow state, not a fourth evidence tier:
they cannot support prose until reviewed.

## Population model

The architecture prohibits a generic `contributors` metric. It distinguishes:

- repository inventory records;
- repositories in transformed activity tables;
- Git identities after bot normalization;
- OBS-T corrector labels;
- OBS-Q correction implementers;
- historically attested people.

Joins between these populations require an explicit identity crosswalk and
human adjudication. No such full crosswalk exists in v1.1.

## Versioning

The immutable article release is `a61-history-v1.1`; `2026-07` is its calendar
alias. Each row retains its own cutoff because the bundle combines a June
GitHub snapshot, an OBS-T cutoff of 30 May 2026, and cross-repository statistics
verified in July. Future corrections produce v1.2 or v2.0; they do not rewrite
the meaning of v1.1. The preceding v1.0 directory remains immutable.

## v1.1 ruling layers

- **Evidence:** `claim_registry.csv` inventories A61 empirical/project numbers
  through the conclusion, excluding references. Hash-locked M10 sources are in
  `source_artifacts.csv`; unsupported or stale numbers remain visible only with
  removed/superseded statuses. The two email milestones remain
  `evidence_pending`.
- **Legal:** the Apte 1957 status remains an open rights determination; EU
  database-right language is attributed history, not a current legal opinion.
- **Venue:** official WSC metadata checked 18 July 2026 gives the 1 February
  2027 deadline and 10–14 December headline/table, while the footer says
  10–15 December; no word limit is published.
- **Build:** the generator validates evidence references and the protected A13
  hash. Site build receives three best-effort attempts for external CDN failure.
