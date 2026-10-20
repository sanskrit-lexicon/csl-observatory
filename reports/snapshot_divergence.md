# Snapshot divergence — the repo quotes two organisation snapshots as one truth

_Created: 20-10-2026 (H7122) · Last updated: 20-10-2026_

**Finding.** `csl-observatory` publishes two independent snapshots of the
`sanskrit-lexicon` organisation. They are produced by different pipelines, they
disagree on every count, and until now no surface said which one it was quoting.
The front page and the reproducible reports therefore described different
organisations, and a reviewer who re-derived a number from the committed CSVs got
a different answer from the one on the front page.

This report states the divergence instead of resolving it by fiat. Which snapshot
is authoritative for which surface is recorded in
[`docs/SNAPSHOT_AUTHORITY.md`](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/docs/SNAPSHOT_AUTHORITY.md);
every quoted number is registered in
[`data/headline_claims.json`](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/data/headline_claims.json)
and re-derived by `python scripts/update_headline_numbers.py --check`.

## The two snapshots side by side

| Snapshot | As of | Repos | Issues | PRs | Issues+PRs | Commits | Human contributors |
|---|---|---|---|---|---|---|---|
| `csl-obs/org-live@1.0.0` | 2026-09-28 | 86 | 7,877 | 2,162 | 10,039 | 13,810 | 72 |
| `csl-obs/org@1.0.0` | 2026-09-28 | 77 | 5,667 | 1,339 | 7,006 | 13,299 | 16 |

**Delta** (live − offline): 9 repositories, 2,210 issues, 823 PRs, 3,033
issues+PRs, 511 commits, 56 contributors.

The contributor row is *not* a delta of the same quantity: the live figure counts
every `contributors.json` row that is not a bot, the offline figure counts humans
who actually contributed a commit to a repo (the bus-factor basis), and
`reports/dashboard.md` prints a third number — every `contributors.json` row,
bots included. Three definitions of "contributor" are in play. The registry keys
them apart (`contributors`, `contributors_all`) so a cross-contamination shows up
as a failed claim rather than as a plausible-looking figure.

## Why they differ

1. **Different runs.** `refresh.yml` queries the live API; `refresh-observatory.yml`
   applies the offline transform. Both stamp `2026-09-28`, which is what made the
   divergence invisible: the dates agree, the numbers do not.
2. **Different repo sets.** The live pipeline lists the organisation directly and
   sees the archived repos and forks; the transform filters its working set before
   writing `repos.csv`. This accounts for the repository gap and drags every other
   count with it.
3. **Different windows.** Issue, PR and commit collection does not cover the same
   set of repositories in the two pipelines, which is why the commit gap (small)
   and the issue gap (large) differ in size.
4. **Different contributor definitions**, as above.

## What this cost

- The front page promised more than the reproducible layer could show: a reviewer
  following `reports/README.md`'s "no live API calls" promise lands on the
  offline numbers, which are all lower, with no note that another snapshot exists.
- `README.md` itself mixed both: its summary line and headline table came from the
  live snapshot while the Findings table underneath summarised offline reports.
  Same file, same page, two organisations.
- The generator was write-only (`scripts/update_headline_numbers.py` had no
  `--check`), so nothing failed when a hand-typed number drifted, and it only
  covered `README.md` / `STATUS.md` — the reports, the dashboard, the roadmap and
  the articles were unguarded.
- `docs/OBSERVATORY_ROADMAP.md` carried two more vintages: a repository-health
  ratio from the 2026-06-17 vintage and a bus-factor ratio from the 2026-07-18
  vintage, both on a 76-repo base that no longer exists in `data/`. The current
  reproducible report disagrees with the roadmap row on method as well as on
  numbers (declared-missing licences vs. declared-missing **plus** unrecognised
  licence files), so the roadmap rows are pinned as historical vintages rather
  than silently overwritten — see below.

## Disposition

| Surface | Now quotes | Mechanism |
|---|---|---|
| `README.md` summary line + headline table, `STATUS.md` table, `reports/dashboard.md` | `csl-obs/org-live@1.0.0` | generated with an explicit snapshot ID + as-of suffix |
| `README.md` Findings table, `reports/*.md` | `csl-obs/org@1.0.0` | generated headers name the snapshot; claims pinned in the registry |
| `docs/OBSERVATORY_ROADMAP.md` completion-log rows | `csl-obs/org@hist-2026-06-17`, `hist-2026-07-18`, `hist-2026-07-03` | rows relabelled in place as historical, with a pointer here; not re-derivable, so values are pinned in the registry |
| `docs/ANTHOLOGY_ALIGNMENT_2026Q4.md` | both, side by side | already labelled inline; now mechanically checked as a mixed-reference surface |
| `article/*.md` | `csl-obs/org@1.0.0` | no headline number currently; the uncovered-number guard is live |

## Residual work (not done here)

- **Reconcile the snapshots, don't just label them.** The right end state is one
  organisation snapshot with one repo-set rule, and the live pipeline reporting a
  delta against it. Labelling stops the lying; it does not merge the pipelines.
- **Reconcile the repo-health method.** The historical roadmap row and the
  current `reports/repo_health.md` disagree about what "no licence" means
  (declared-missing vs. declared-missing plus unrecognised file). One of the two
  methods should win and the loss should be documented.
- **One contributor definition.** Three are in play (non-bot rows, commit authors,
  all rows). Pick one per surface and say so in the report that quotes it.
- **Offline reproducibility of the live snapshot.** If the front page is to keep
  quoting a live-API figure, the pipeline should commit the raw API captures that
  produced it, so "as of" is auditable without a network call.
- **`reports/obs_t_issuelabel.md` is frozen on the 2026-06 vintage.** Its generator
  (`scripts/obs_t_issuelabel.py`) is deterministic, but re-running it today drops the
  dated `_Created:` header and the byline, so regenerating would fix the numbers and
  break the doc contract. The stale figures are pinned in the claim registry and the
  generator needs the house header before it can be re-run.

_Dr. Mārcis Gasūns_
