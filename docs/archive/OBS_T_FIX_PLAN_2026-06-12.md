# OBS-T Fix Plan (Archived)

Status: implemented and verified, then archived on 2026-06-12.

This tracker records the Codex-review fixes needed to make OBS-T paper-ready.
Priority order is correctness and release safety first, then claim polishing.

## Review Baseline

The review was run against the pre-fix OBS-T release:

| Metric | Pre-fix value |
|---|---:|
| Released events | 50,953 |
| Form rows | 24,441 |
| Git rows | 26,512 |
| Derived share | 65.9% |
| Git rows from non-entry `v02` paths | 725 |
| Unequal hunk runs at risk of truncation | 1,069 |
| Email-shaped released identity cells | 1,124 |
| High-risk value-headword joins | 284 short keys; 1,329 multi-record keys |

## Implementation Tracker

| Phase | Fix | Status | Verification |
|---|---|---|---|
| 1 | Restrict git mining to `v02/<dict>/<dict>.txt`; add `source_path` and `commit_sha`. | Implemented in `scripts/reconstruct_git_events.py`. | `scripts/obs_t_regression.py` checks all git `source_path` values. |
| 1 | Replace `zip(dels, adds)` truncation with replacement/insertion/deletion events and hunk counters. | Implemented in `scripts/reconstruct_git_events.py`. | `correction_events_git.meta.json` records `diffPairing` counters. |
| 2 | Add `edit_space` and compute Sanskrit edit types only over IAST Sanskrit spans. | Implemented in `scripts/reconstruct_git_events.py` and `scripts/attribute_crosswalks.py`. | Raw source/markup edits produce `source-raw`, spacing, punctuation, or digit rather than Sanskrit case/spelling. |
| 3 | Harden form-layer attribution and downgrade weak value-headword shortcuts. | Implemented in `scripts/attribute_components.py`. | Metadata records attribution routes; `validation/form_join_audit_sample.csv` samples high-risk joins. |
| 4 | Remove raw form-submit email addresses from released identities. | Implemented in `scripts/build_correction_events.py`. | `scripts/obs_t_regression.py` scans `corrector` and `corrector_name`. |
| 4 | Align data license and citation metadata. | Implemented via `DATA_LICENSE.md`, `CITATION.cff`, and datasheet updates. | Manual review plus regression/datasheet checks. |
| 5 | Rephrase H1/H2/H3 and baseline claims. | Implemented in OBS-T report generators. | Regenerated `reports/obs_t_*.md` after pipeline rerun. |

## Count Deltas

Observed after the full pipeline rerun:

- Git rows increased because the new insertion/deletion rows more than offset the
  removal of non-entry-path rows.
- Derived share fell from 65.9% to 64.3% after weak form joins were left
  `unattributed`.
- Released email-shaped identity cells fell to zero.
- `source-raw` is now an explicit edit type (7,852 events), preventing raw SLP1 or
  markup changes from being counted as Sanskrit spelling/case changes.

| Metric | Post-fix value | Delta vs baseline |
|---|---:|---:|
| Released events | 52,498 | +1,545 |
| Form rows | 24,441 | 0 |
| Git rows | 28,057 | +1,545 |
| Derived share | 64.3% | -1.6 pp |
| Git rows from non-entry `v02` paths | 0 | -725 |
| Unequal hunk runs counted | 4,237 | +4,237 counted |
| Unmatched hunk lines emitted | 9,505 | +9,505 counted |
| Email-shaped released identity cells | 0 | -1,124 |
| Form attribution routes | segment_exact 706; segment_fuzzy 2,440; value_headword_unique 2,552; value_headword_weak 1,351; unattributed 17,392 | tracked |
| Top edit types | spelling 11,683; spacing 10,233; punctuation 9,506; source-raw 7,852; diacritic 4,785; case 3,813; digit 2,907 | source-raw added |

## Test Plan

- Run the full OBS-T pipeline from `build_correction_events.py` through generated reports.
- Run `python scripts/obs_t_regression.py`.
- Run `python scripts/obs_t_translit_check.py` and keep the sibilant-ambiguity note in the generated report.
- Keep `scripts/obs_t_gold.py --make`, `scripts/obs_t_gold.py --score`, `scripts/obs_t_errorsample.py --make`, and `scripts/obs_t_errorsample.py --score` human-gated; do not run them in the automated pipeline.
- Inspect the headline count deltas above before using the release in a paper draft.
