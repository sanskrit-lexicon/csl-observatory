# Snapshot authority — which snapshot each public surface quotes

_Created: 20-10-2026 (H7122) · Last updated: 20-10-2026_

Two snapshots of the `sanskrit-lexicon` organisation live in this repo and they
do not agree — they are produced by different pipelines, over different hour-long
API runs, with different definitions. This page says, per public surface, which
snapshot that surface quotes, its as-of date and its dataset ID. The numbers
themselves are not restated here (restating them is how the divergence started);
the corresponding values are printed by
`python scripts/headline_claims.py` and verified by
`python scripts/update_headline_numbers.py --check`.

Companion reading: [`reports/snapshot_divergence.md`](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/reports/snapshot_divergence.md)
(why the two snapshots differ and why that is a finding), and the machine registry
[`data/headline_claims.json`](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/data/headline_claims.json)
(every quoted number → its snapshot → its metric).

## The two live snapshots

| Dataset ID | Written by | Source of truth | Reproducible offline? |
|---|---|---|---|
| `csl-obs/org-live@1.0.0` | `refresh.yml` (live GitHub API) | `data/summary.json` + `data/contributors.json` | **No** — re-running means new API calls, so a reviewer cannot re-derive it from the checkout |
| `csl-obs/org@1.0.0` | `refresh-observatory.yml` (offline transform) | `data/manifest.json` + `observatory/site/src/data/*.csv` | **Yes** — the CSVs are committed; `reports/README.md`'s "no live API calls" promise holds for these numbers only |

Historical vintages quoted in narrative docs are pinned as
`csl-obs/org@hist-YYYY-MM-DD`. Their values are **not** re-derivable from the
current `data/` tree; the registry carries the pin, and the checker enforces both
the number and the presence of the snapshot ID on the surface that quotes it.

## Authority per surface

| Surface | Snapshot quoted | As-of | Dataset ID |
|---|---|---|---|
| `README.md` line 6 summary line | live-API pipeline | `data/summary.json` → `snapshot_date` | `csl-obs/org-live@1.0.0` |
| `README.md` "Headline numbers" table | live-API pipeline | same | `csl-obs/org-live@1.0.0` |
| `README.md` "Findings" table (report headlines) | offline transform | `data/manifest.json` → `transformed_at` | `csl-obs/org@1.0.0` |
| `STATUS.md` headline numbers table + "Current status" line | live-API pipeline | `snapshot_date` | `csl-obs/org-live@1.0.0` |
| `STATUS.md` OBS-T correction-corpus row | offline transform | `manifest.transformed_at` | `csl-obs/org@1.0.0` (dataset `csl-obs/correction-events@1.0.0`) |
| `reports/dashboard.md` | live-API pipeline | `snapshot_date` | `csl-obs/org-live@1.0.0` |
| `reports/velocity_timeline.md` | offline transform | `manifest.transformed_at` | `csl-obs/org@1.0.0` |
| `reports/taxonomy_adoption.md` | offline transform | `manifest.transformed_at` | `csl-obs/org@1.0.0` |
| `reports/issue_lifecycle.md` | offline transform | `manifest.transformed_at` | `csl-obs/org@1.0.0` |
| `reports/bus_factor.md` | offline transform | `manifest.transformed_at` | `csl-obs/org@1.0.0` |
| `reports/repo_health.md`, `reports/contributor_identity.md`, other `reports/*.md` | offline transform | `manifest.transformed_at` | `csl-obs/org@1.0.0` |
| `docs/OBSERVATORY_ROADMAP.md` — completion log rows | historical pin | dated in the pin | `csl-obs/org@hist-2026-06-17`, `hist-2026-07-18`, `hist-2026-07-03` |
| `docs/OBSERVATORY_ROADMAP.md` — any new row | offline transform | `manifest.transformed_at` | `csl-obs/org@1.0.0` |
| `docs/ANTHOLOGY_ALIGNMENT_2026Q4.md` | both, quoted side by side and labelled inline | as stated per number | `csl-obs/org-live@1.0.0` + `csl-obs/org@1.0.0` |
| `article/*.md` | offline transform | `manifest.transformed_at` | `csl-obs/org@1.0.0` (currently quotes no headline number; the guard is live) |
| `observatory/site/` pages | whatever the page's own data import says — see the page | — | `csl-obs/org@1.0.0` |

Rule of thumb:

- **Front page** (`README` line 6, both "Headline numbers" tables, the dashboard)
  quotes the **live** snapshot. It is the freshest, and its job is to advertise
  the current size of the organisation.
- **Findings and reports** quote the **offline** snapshot. Their job is
  reproducibility: a reviewer must be able to re-derive every figure from the
  committed CSVs.
- A surface that mixes both must label each number. A bare number on a swept
  surface fails the gate.

## The gate

```bash
python scripts/headline_claims.py                     # print snapshot census + verdict
python scripts/update_headline_numbers.py --check     # the command CI runs
python scripts/update_headline_numbers.py             # rewrite README/STATUS (refresh pipeline)
```

`--check` exits 0 on a clean tree and 1 on any of:

- a registered claim whose number no longer matches its snapshot (message names
  the claim id, the file and line, the quoted value and the snapshot's value);
- a registered claim whose pattern matches nothing (the surface was rewritten and
  the claim rotted);
- a headline number on a swept surface with **no** registry claim — this is how a
  hand-typed number gets reintroduced; and
- an allowlist entry that no longer excuses anything (stale exemption).

CI: `.github/workflows/headline-claims.yml` runs it on every push and pull
request. Adding a claim means editing `data/headline_claims.json` in the same PR
as the surface — a number cannot enter the repo without naming its snapshot.

_Dr. Mārcis Gasūns_
