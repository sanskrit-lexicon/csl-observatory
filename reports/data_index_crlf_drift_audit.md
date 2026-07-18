# data_index.csv byte-count drift — cause audit and fix (G17 / H1223)

_Created: 18-07-2026 · Last updated: 18-07-2026_

Org goal **G17** ("green observatory refresh") sat 🔴 RED since 14-07-2026: on a fresh checkout,
[scripts/refresh_observatory.py](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/scripts/refresh_observatory.py)
`--check-only` failed at `data-index-check`, with every catalogued file measuring ~0.7–3 % **smaller**
than the bytes recorded in
[observatory/site/src/data/data_index.csv](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/observatory/site/src/data/data_index.csv)
(e.g. `commits.csv` expected 1,330,401, got 1,320,523). After PR
[#92](https://github.com/sanskrit-lexicon/csl-observatory/pull/92) registered the 4 hand-curated
`data/` files, a fresh clone failed in the mirror direction instead: `catalog entries without public
files` — those files only appear in the site data dir after the refresh workflow's "Copy data into
site" step. Both failure modes share one root: **the check measured environment state, not committed
content.** Audited and fixed 18-07-2026 by Fable 5 (`claude-fable-5`), handoff
[H1223](https://github.com/gasyoun/Uprava/blob/main/handoffs/H1223-Fable_csl-observatory_g17-data-index-bytecount-drift_18.07.26.md).

## Verdict — CONFIRMED: CRLF inflation, one byte per line, no content loss

The byte drift is Python's `csv` module default: the generator scripts (e.g.
[observatory/transform.py](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/observatory/transform.py),
line 61) call `csv.writer` without `lineterminator`, which writes `\r\n` **on every OS, including
Linux CI**. A regeneration therefore leaves CRLF files in the working tree;
[scripts/data_index.py](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/scripts/data_index.py)
recorded their `st_size` (inflated by one byte per line); git then normalized the committed blobs to
LF per [.gitattributes](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/.gitattributes)
(`* text=auto eol=lf`), so every fresh checkout measured smaller than recorded by exactly the line
count. Row/content loss is positively excluded: at the poisoned baseline commit `6f573f1`
(17-06-2026), **all 43 catalogued files** satisfy `recorded − blob == line count` exactly:

| file | recorded | blob | delta | lines | verdict |
|---|---:|---:|---:|---:|---|
| bus_factor.csv | 2794 | 2717 | 77 | 77 | crlf-exact |
| commits.csv | 1330401 | 1320523 | 9878 | 9878 | crlf-exact |
| contributor_identity.csv | 1146 | 1126 | 20 | 20 | crlf-exact |
| contributors.csv | 6145 | 5935 | 210 | 210 | crlf-exact |
| correction_events.csv | 11202281 | 11177839 | 24442 | 24442 | crlf-exact |
| correction_events.meta.json | 2911 | 2734 | 177 | 177 | crlf-exact |
| correction_events_all.csv | 57768167 | 57715668 | 52499 | 52499 | crlf-exact |
| correction_events_final.csv | 61222247 | 61169748 | 52499 | 52499 | crlf-exact |
| correction_events_final.meta.json | 4629 | 4374 | 255 | 255 | crlf-exact |
| correction_events_git.csv | 46566153 | 46538095 | 28058 | 28058 | crlf-exact |
| correction_events_git.meta.json | 3237 | 3058 | 179 | 179 | crlf-exact |
| correction_events_release.csv | 61511036 | 61458537 | 52499 | 52499 | crlf-exact |
| correction_events_release.meta.json | 1334 | 1275 | 59 | 59 | crlf-exact |
| correction_events_typed.csv | 59011475 | 58958976 | 52499 | 52499 | crlf-exact |
| correction_events_typed.meta.json | 2757 | 2623 | 134 | 134 | crlf-exact |
| issue_typology_annual.csv | 2804 | 2663 | 141 | 141 | crlf-exact |
| issues.csv | 750181 | 744767 | 5414 | 5414 | crlf-exact |
| obs_q_annual.csv | 398 | 389 | 9 | 9 | crlf-exact |
| obs_q_latency.csv | 17216 | 16971 | 245 | 245 | crlf-exact |
| obs_q_per_dict.csv | 1704 | 1657 | 47 | 47 | crlf-exact |
| obs_t_baselines.json | 982 | 941 | 41 | 41 | crlf-exact |
| obs_t_campaigns.csv | 53107 | 52745 | 362 | 362 | crlf-exact |
| obs_t_component.csv | 4664 | 4439 | 225 | 225 | crlf-exact |
| obs_t_confusion.csv | 148615 | 143595 | 5020 | 5020 | crlf-exact |
| obs_t_corrector.csv | 4363 | 4302 | 61 | 61 | crlf-exact |
| obs_t_crosswalk.csv | 2372 | 2287 | 85 | 85 | crlf-exact |
| obs_t_dict.csv | 1536 | 1492 | 44 | 44 | crlf-exact |
| obs_t_rigor.json | 5835 | 5546 | 289 | 289 | crlf-exact |
| obs_t_robustness.json | 727 | 684 | 43 | 43 | crlf-exact |
| obs_t_silver.json | 2268 | 2131 | 137 | 137 | crlf-exact |
| obs_t_summary.json | 6834 | 6372 | 462 | 462 | crlf-exact |
| obs_t_timeline.csv | 1688 | 1610 | 78 | 78 | crlf-exact |
| obs_t_timeline_monthly.csv | 9976 | 9471 | 505 | 505 | crlf-exact |
| obs_t_translit.json | 4126 | 3947 | 179 | 179 | crlf-exact |
| people_summary.csv | 906 | 887 | 19 | 19 | crlf-exact |
| repo_health.csv | 5416 | 5339 | 77 | 77 | crlf-exact |
| repo_metadata.csv | 15599 | 15522 | 77 | 77 | crlf-exact |
| repos.csv | 14195 | 14118 | 77 | 77 | crlf-exact |
| taxonomy_adoption.csv | 799 | 785 | 14 | 14 | crlf-exact |
| timeseries_annual.csv | 10714 | 10331 | 383 | 383 | crlf-exact |
| timeseries_monthly.csv | 41609 | 40267 | 1342 | 1342 | crlf-exact |
| velocity_timeline.csv | 577 | 563 | 14 | 14 | crlf-exact |
| workflow_health.csv | 14775 | 14698 | 77 | 77 | crlf-exact |

_43 crlf-exact · 0 other._ Reproduce with
[scripts/g17_historical_check.py](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/scripts/g17_historical_check.py);
the current-state audit is
[scripts/g17_delta_audit.py](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/scripts/g17_delta_audit.py)
(all 54 committed files match recorded bytes exactly as of this fix — the 13-07-2026 H817 WS1.3
regeneration happened to run against checked-out LF files and silently healed the numbers, but the
poisoning vector remained: the next CI refresh, unblocked by #92, would have re-recorded CRLF sizes
on Monday's run).

## Canonical-form ruling and fix

**Recorded bytes are the LF-normalized content size** — identical to what git stores under the
repo-wide `eol=lf` policy — never `st_size`. This makes record and check agree on any OS, in any
checkout state (freshly written CRLF or freshly checked-out LF). Implemented in `data_index.py`
(`measured_bytes()`); verified by simulation: rewriting `commits.csv` with CRLF reproduces the
historical 1,330,401 on disk while `--check` stays green, and stays green again after restore.

Two companion determinism fixes in the same pass: the 4 hand-curated files
(`contributor_repo_heatmap.csv`, `contributor_specialisation.csv`, `etymology_marker_preliminary.csv`,
`wil_nirukta_tokens.csv`) are now resolved from their canonical committed home in
[data/](https://github.com/sanskrit-lexicon/csl-observatory/tree/main/data) whether or not the
workflow's copy step has run, and `data_index.csv` itself is written with `newline="\n"`.

## Residuals (not built here)

- `generated_date` is still `st_mtime`-based, hence checkout-dependent; it is deliberately excluded
  from `--check`. A `git log -1 --format=%cs`-based date would make the whole row deterministic.
- The `site-build` phase needs the Observable CDN; it is network-gated on offline hosts (verified
  green in CI context by [#92](https://github.com/sanskrit-lexicon/csl-observatory/pull/92) the same
  day). All six repo-validation phases pass locally after this fix.
- Sibling generators that write CRLF (`csv.writer` without `lineterminator="\n"`) still do so;
  harmless now for the catalog, but any future size-baselining check in the org must measure
  normalized content, not `st_size` — the class of error, not the instance, is the lesson.

_Dr. Mārcis Gasūns_
