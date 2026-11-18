# OBS-T external validity — frozen instrument, not yet a result

_Created: 18-11-2026 · Last updated: 18-11-2026_

**Status:** INSTRUMENT ONLY. The 400-row sample is drawn; **no row has been annotated** and no error-incidence number is claimed here. Human adjudication is a genuine gate and is parked in GTD.
**Artifacts:** [`scripts/obs_t_external_validity.py`](../scripts/obs_t_external_validity.py) · [`validation/external_validity_sample.csv`](../validation/external_validity_sample.csv) · [`validation/external_validity_manifest.json`](../validation/external_validity_manifest.json).
**Executes:** acl-uplift shape 3 (annotator validity), agenda move 4 of [`docs/ANTHOLOGY_ALIGNMENT_2026Q4.md`](../docs/ANTHOLOGY_ALIGNMENT_2026Q4.md), handoff H8444.

## 1. The question this answers

The 2026-06 probe (120 raw entries) found **0/120** entries with an error — see [`reports/obs_t_errorbench.md`](obs_t_errorbench.md). That null cannot be read as "there are no errors", because the sample was small and uncontrolled. A reviewer's real objection is different: the OBS-T corpus measures *what was corrected*, not *what was wrong*. This instrument settles whether the correction profile tracks true error incidence, with a stated denominator and a pre-registered verdict rule.

## 2. Sampling, frozen before any label

| Item | Frozen choice |
|---|---|
| Source | SHA-256-pinned E32 release CSV (52,498 rows), no live API, no re-cut |
| Size | 400 rows, inside the pre-declared 300–500 band |
| Seed | `20261118`, one stdlib `random.Random` in sorted-key order |
| Strata | OBS-T `error_component` (the location axis), proportional to corpus share with a floor of 20 per stratum |
| Unit key | `event_id#row-ordinal` — see the finding below |
| Replacement | none; one row per sampled unit |
| Annotation columns | written **empty** by the generator; `human_error`, `human_component`, `human_notes` are for a human only |

Determinism is a command, not a claim: `python scripts/obs_t_external_validity.py --check` re-derives the input digest, stratum floors, seed and uniqueness from the pinned source and refuses on drift. The generator's `--selftest` covers floor enforcement, draw determinism, the N band and the empty-label invariant.

### Finding surfaced while building the instrument

`event_id` is **not a primary key** in the frozen E32 cut: 52,498 rows carry only **44,550 distinct** values; 1,935 ids repeat, with the most frequent occurring **912** times. Any analysis that treats `event_id` as a unique join key will silently collapse hundreds of events. The instrument therefore keys on `event_id` plus the row ordinal from the pinned CSV and retains `event_id` only as a source foreign key. This is a durable data fact, not a sampling artifact.

## 3. Verdict rule, registered before the data exist

Let `p̂ = k/400` be the human-adjudicated found-error rate and `r` the correction share of the same component stratum in the released corpus. Compute a 95% Wilson interval for `p̂`.

- **Under-correction** if the Wilson lower bound exceeds `r` for a stratum.
- **Over-representation** if the Wilson upper bound falls below `r`.
- **Indeterminate** if the interval contains `r` — report it as such; do not promote a descriptive association into a claim about the error population.
- A **0/400** result is indeterminate, not proof of zero errors: report the upper bound, which is approximately 0.9% at 95% confidence.

No threshold was chosen after seeing a result. No model-generated label may be used in `human_*` columns.

## 4. Honest channel labels

| Channel | Label to report | Allowed in `human_*` columns? |
|---|---|---|
| A human reading the raw entry and its correction | **human × release** | yes |
| A model pass over the same sample | **model × release** | no — separate file, never relabeled as human |
| Two model passes compared | **model × model** | no — never reported as human × human |

The existing κ=0.906 figure in the paper is a **cross-model** agreement result (Opus 4.8 × Sonnet 5, n=390, 8-value location axis). It is not evidence of human agreement, and this instrument does not re-label it.

## 5. Caveats stated here, not buried

- The sample is stratified by **location**, so its aggregate error rate is not an unbiased estimate of org-wide error incidence; use per-stratum rates with the stratum denominator.
- The unvalidated-instrument caveat: Wilson intervals assume independent Bernoulli draws. Corrections from the same headword or campaign may be correlated; the estimator is a triangulation aid, not a definitive population estimate.
- This pass does not change A12's headline numbers, the E32 pins or the 25+65 canary. Both gates were re-run green (`e32_canary.py` → ALL PASS; the sampler's `--check` → OK).
- Human adjudication is **not** performed here. Anyone filling the annotation columns must record adjudicator identity and date in the manifest before the numbers become quotable.

## 6. Reproduction

```bash
python scripts/obs_t_external_validity.py --selftest
python scripts/obs_t_external_validity.py --check
python3 data/publication/e32-correction-events-release-2026-10-10/e32_canary.py
```

---

_Dr. Mārcis Gasūns_
