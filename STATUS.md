# Status

> **Current status (2026-06).** The observatory is live and reproducible.
> Five org-process findings + a synthesis are on the
> [dashboard](https://sanskrit-lexicon.github.io/csl-observatory/), and the
> standalone **OBS-T error-typology** track (a 50,953-event correction corpus,
> two-axis typology, datasheet, and baselines) has a draft paper in
> [`paper-obs-t-error-typology.md`](paper-obs-t-error-typology.md).

## Where to start

1. **[`README.md`](README.md)** — what this is, the headline numbers, and the repo map.
2. **[`reports/README.md`](reports/README.md)** — the reproducible findings, each script → report → site page.
3. **[`reports/synthesis.md`](reports/synthesis.md)** — *State of the observatory*, the findings tied into one picture.
4. **[Dashboard](https://sanskrit-lexicon.github.io/csl-observatory/)** — the live, downloadable charts.

## Headline numbers (snapshot 2026-06)

| Metric | Value |
|---|---:|
| Repositories tracked | 76 |
| Issues + PRs (lifetime) | 5,413 |
| Commits since 2014 | 9,877 |
| Distinct human contributors | 16 |
| Span | 13 years (2014–2026) |
| OBS-T correction corpus | 50,953 events across 43 dictionaries |

These are computed from the committed snapshot; the dashboard and
[`data/manifest.json`](data/manifest.json) are the source of truth.

## Open work

- **Findings & hygiene follow-ups** are filed as issues #15–#25 on
  [Tooling Roadmap project #9](https://github.com/orgs/sanskrit-lexicon/projects/9)
  (most need a maintainer decision or credential — see
  [`docs/DECISIONS_NEEDED.md`](docs/DECISIONS_NEEDED.md)).
- **OBS-T paper** awaits human gold-sample annotation + a second annotator
  (for an inter-annotator κ) before submission; tooling is ready in
  [`scripts/obs_t_gold.py`](scripts/obs_t_gold.py) and
  [`validation/`](validation/).
- **Citability**: register ORCIDs and mint a Zenodo DOI (the citation block
  still reads "DOI: pending mint").

---

*Provenance: this repo grew out of autonomous build sessions in 2026-05/06.
The original 2026-05-07 session log (with its then-current, now-superseded
numbers) is preserved in git history rather than reproduced here.*
