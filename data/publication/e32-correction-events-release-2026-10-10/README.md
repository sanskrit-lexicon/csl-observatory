# e32-correction-events-release-2026-10-10 — the E32 public release of the CDSL correction-event corpus

_Created: 10-10-2026 · Last updated: 10-10-2026_

The versioned, digest-pinned public release of **E32** — the correction-event
corpus of the Cologne Digital Sanskrit Lexicon (CDSL) — cut for the ISCLS-9
resource paper «Correction-event mining as annotation-error-detection corpus
release» (A73). E32 is the release-only view of the OBS-T correction-event
corpus (52,498 typed events, 43 dictionaries, 208 corrector aliases,
2014-03-18 → 2026-05-30), registered in
[SanskritLexicography FEATURES_INDEX row E32](https://github.com/gasyoun/SanskritLexicography/blob/master/FEATURES_INDEX.md).
The underlying file is
[`observatory/site/src/data/correction_events_release.csv`](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/observatory/site/src/data/correction_events_release.csv)
(52,498 rows × 31 columns, one row = one old→new correction event), described by
[`docs/DATASHEET.md`](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/docs/DATASHEET.md)
and [`data/schema/correction-event.schema.json`](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/data/schema/correction-event.schema.json).

## Frozen cut — digest lines

`SHA256SUMS` in this directory pins the exact bytes the release describes. Short
digests (full values in `SHA256SUMS`):

| Artifact | SHA-256 (first 12 hex) |
|---|---|
| `observatory/site/src/data/correction_events_release.csv` | `a27fec9e6a5b` |
| `observatory/site/src/data/correction_events_release.meta.json` | `1dec6baf8dd0` |
| `data/schema/correction-event.schema.json` | `c3cd6fa333c6` |
| `observatory/site/src/data/obs_t_rigor.json` | `6727bfcfdaf4` |
| `observatory/site/src/data/obs_t_baselines.json` | `70c123544026` |

The CSV is a growing working artifact (weekly refresh crons); this release is
the frozen 52,498-row cut of 2026-10-10. If any digest check fails, the working
file has moved on — cut `v1.1` with `python3 e32_canary.py --sums && python3
e32_canary.py --recompute` rather than quoting drifted numbers.

## Numeric canary

Every number the A73 paper quotes re-derives from committed artifacts by one
command (25 corpus numbers recomputed live from the CSV + 65 pins read from the
committed OBS-T rigor/baseline tables, the a61-sixdict matrix release and the
NWS pin):

```bash
python3 data/publication/e32-correction-events-release-2026-10-10/e32_canary.py
# ALL PASS — 25 corpus + 65 pinned numbers verified against the frozen cut
```

Status at cut: **ALL PASS (2026-10-10)**, see `expected.json` for the frozen
values.

## License

- **The E32 corpus data is CC BY 4.0** — [`DATA_LICENSE.md`](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/DATA_LICENSE.md)
  (in force 2026-06-17; the same files shipped in the OBS-T Zenodo deposit,
  concept DOI [10.5281/zenodo.21346705](https://doi.org/10.5281/zenodo.21346705),
  version v1.14.0).
- **Repository code is GPL-3.0** — [`LICENSE`](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/LICENSE).
- This release directory (README, canary, pins) is part of the repository code
  release (GPL-3.0); the numbers and pins it carries are facts about the CC BY 4.0 data.

## Attribution and license audit (against the CDSL source dictionaries)

- **Source texts.** The corrected content comes from the 43 digitized
  dictionaries of the CDSL canon; the digitized dictionary texts are maintained
  in [`csl-orig`](https://github.com/sanskrit-lexicon/csl-orig) under
  **CC BY-SA 4.0**. E32 rows carry only event metadata plus the short old/new
  snippet of the single corrected entry line (not full entries, not full
  dictionaries) — an analytical derivative released under CC BY 4.0 per the
  standing estate license decision above. The ShareAlike interaction between a
  BY-SA source and a BY analytical derivative is recorded as a known residual
  question for the A73 go/no-go; the same licensing shape has been public since
  the June 2026 Zenodo deposit.
- **Community attribution.** The corpus is a record of twelve years of
  volunteer proofreading of the Cologne digitization. When citing the data,
  attribute the **CDSL / sanskrit-lexicon community and the OBS-T
  correction-event corpus** (`DATA_LICENSE.md`).
- **Corrector privacy.** Released identities are stable public aliases or
  pseudonyms; raw form-submit email addresses are not released
  (`correction_events_release.meta.json` assumptions).
- **Third-party material.** The NWS (Nachtragswörterbuch des Sanskrit, Halle)
  overlap numbers are pinned values only (`nws_intersections_pinned.json`); the
  NWS base layer itself is **not redistributed** — texts are usable with MLU
  Halle-Wittenberg attribution, the layer stays private pending the accession
  decision (H5932/H5939).

## Citation

```bibtex
@dataset{gasuns2026e32,
  title  = {E32: Correction-Event Corpus of the Cologne Digital Sanskrit
            Lexicon (release e32-correction-events-release-2026-10-10)},
  author = {Gas{\=u}ns, M{\=a}rcis and the CDSL / sanskrit-lexicon community},
  year   = {2026},
  doi    = {10.5281/zenodo.21346705},
  note   = {52,498 typed correction events, 43 dictionaries, 2014--2026;
            frozen cut 2026-10-10, SHA-256-pinned; data CC BY 4.0}
}
```

Cross-references: the full three-view log (all/typed/final, 52,498 rows each) is
registered as the kosha dataset
[`correction-events-log`](https://github.com/gasyoun/kosha/blob/main/docs/data-statements/correction-events-log.meta.md)
(E41 in FEATURES_INDEX); the typology analyses are
[`reports/obs_t_typology.md`](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/reports/obs_t_typology.md)
with rigor and baseline tables under `observatory/site/src/data/obs_t_*`; the
sense-sequence concordance release is
[`a61-sixdict-sense-seq-matrix-2026-10-04`](https://github.com/sanskrit-lexicon/csl-observatory/tree/main/data/publication/a61-sixdict-sense-seq-matrix-2026-10-04).

Provenance: H6410 (Uprava), executed by GLM-5.3-Flash
(`account:zai-individual-coding-plan/GLM-5.3-Flash`) via ZCode, 2026-10-10.

_Dr. Mārcis Gasūns_
