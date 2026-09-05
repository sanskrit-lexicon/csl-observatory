# CLAUDE.md

_Created: 15-05-2026 · Last updated: 05-09-2026_

`csl-observatory` is the **build-meta / org-observability** repo for the
Cologne Digital Sanskrit Lexicon: it measures the `sanskrit-lexicon` GitHub
organisation (repos, issues, PRs, commits, workflows, OBS-T correction
typology) and publishes a live dashboard. It is not a dictionary and not a
corpus site.

Org conventions live in [`../CLAUDE.md`](https://github.com/gasyoun/github-spine/blob/main/CLAUDE.md).
Before encodings or corpus data, read the
[Sanskrit context primer](https://github.com/gasyoun/github-spine/blob/main/SANSKRIT_CONTEXT_PRIMER.md).
Tooling-repo category conventions:
[cologne-tooling-runbook](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/runbook/cologne-tooling-runbook.md).

## How to run

```powershell
python scripts/check_workspace.py
python scripts/pwg_citation_count_provenance.py --check
cd observatory\site
npm ci
npm run build
```

Offline findings read committed CSVs in
[`observatory/site/src/data/`](https://github.com/sanskrit-lexicon/csl-observatory/tree/main/observatory/site/src/data)
— no live API. Reproduce a named report with its script under
[`scripts/`](https://github.com/sanskrit-lexicon/csl-observatory/tree/main/scripts)
(`bus_factor.py`, `repo_health.py`, `taxonomy_adoption.py`, …). Index:
[`reports/README.md`](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/reports/README.md).
Reviewer path:
[`docs/REVIEWER_REPRODUCIBILITY.md`](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/docs/REVIEWER_REPRODUCIBILITY.md).

OBS-T regression: `python scripts/obs_t_regression.py`. Gold / error-sample
sheets are human-gated (`obs_t_gold.py --make` / `--score`). Live dashboard:
[sanskrit-lexicon.github.io/csl-observatory](https://sanskrit-lexicon.github.io/csl-observatory/).

CI that matters: `deploy.yml` (Pages), `refresh.yml` / `refresh-observatory.yml`
(data refresh), `dict-audit.yml`, `tooling-audit.yml`, `encoding-guard.yml`.

## PWG citation counts — the non-obvious rule

Anything numeric about how much of PWG a literary source carries goes through
[`data/pwg_scan_index_tracker/ls_counts/`](https://github.com/sanskrit-lexicon/csl-observatory/tree/main/data/pwg_scan_index_tracker/ls_counts).
Enforced by `python scripts/pwg_citation_count_provenance.py --check`:

1. Consume `citation_count_safe`, never `citation_count`.
2. Fold by `in_pwgbib` before summing (work-*family* rollup).
3. Divide only by the `ALL` of the same snapshot (`citation_mass_denominator`).

Changing the tracker snapshot means re-running `pwg_citation_count_provenance.py`
*before* `pwg_scan_index.py` in the same PR. Never regenerate
`pwg_ls_counts_2024-09-11.tsv`; `--recount` writes the `_current` table only.
Argument: [`reports/pwg_citation_count_provenance.md`](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/reports/pwg_citation_count_provenance.md).

## Do not touch

- Dictionary-structure research — [`csl-atlas`](https://github.com/sanskrit-lexicon/csl-atlas).
- TEI / OntoLex / standards — [`csl-standards`](https://github.com/sanskrit-lexicon/csl-standards).
- DCS / corpus dashboards — [`VisualDCS`](https://github.com/gasyoun/VisualDCS).
- Frozen `pwg_ls_counts_2024-09-11.tsv`.
- `csl-orig` — never commit or push dictionary source.

Issues use the Cologne tooling taxonomy — see
[`/cologne-issue-runbook`](https://github.com/gasyoun/claude-config/blob/main/commands/cologne-issue-runbook.md)
and the [Tooling Roadmap](https://github.com/orgs/sanskrit-lexicon/projects/9).
Do not recopy type/severity/milestone tables into this file.

Start-of-session map:
[`docs/AGENT_ROADMAP.md`](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/docs/AGENT_ROADMAP.md).
Boundary:
[`docs/BOUNDARY_RULES.md`](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/docs/BOUNDARY_RULES.md).

Danger facts:
[Uprava DANGER_FACTS.md](https://github.com/gasyoun/Uprava/blob/main/DANGER_FACTS.md)
and the generated block of
[AGENTS.md](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/AGENTS.md).

_Dr. Mārcis Gasūns_
