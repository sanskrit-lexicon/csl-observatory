# Runbook

This folder contains the canonical, version-controlled source of the
**Cologne issue-taxonomy runbooks** — multi-phase procedures that
apply unified issue taxonomies to repositories in the
`sanskrit-lexicon` GitHub organisation.

There are **two distinct runbooks** because the org has two distinct
kinds of repository, and forcing them through one taxonomy creates
noise:

1. **Dictionary repos** (PWG, MW, AP, …): each digitises a printed
   source. Issues are corrections, scan replacements, markup
   normalisations, etc. — narrow problem space, tight taxonomy.
2. **Tool / infrastructure repos** (csl-apidev, csl-orig, hwnorm1,
   csl-app, …): software engineering work. Issues are bugs, features,
   dependency upgrades, performance, infrastructure, cross-repo
   coordination — broad problem space, broader taxonomy.

The runbooks are invoked as Claude Code custom slash commands.
Authorised users with Claude Code installed can run them as:

```
# Dictionary repos
/cologne-issue-runbook <REPO>          # one repo
/cologne-runbook-all                   # detect-and-process all unprocessed dict repos

# Tool / infrastructure repos
/cologne-tooling-runbook <REPO>        # one tool repo
/cologne-tooling-all                   # detect-and-process all unprocessed tool repos
```

The four `.md` files in this folder are also installed at
`~/.claude/commands/` on the project lead's workstation.

## Files

| File | Role |
|---|---|
| [`cologne-issue-runbook.md`](cologne-issue-runbook.md) | Sixteen-phase **dictionary**-repo runbook (single repo) |
| [`cologne-runbook-all.md`](cologne-runbook-all.md) | Wrapper for batch-processing dictionary repos |
| [`cologne-tooling-runbook.md`](cologne-tooling-runbook.md) | Seventeen-phase **tooling**-repo runbook (single repo) |
| [`cologne-tooling-all.md`](cologne-tooling-all.md) | Wrapper for batch-processing tooling repos |

## Taxonomy comparison

|  | Dictionary runbook | Tooling runbook |
|---|---|---|
| Type labels | 9 (link-target, text-correction, …) | 17 across 5 categories |
| Severity levels | 3 (minor, medium, hard) | 4 (trivial, minor, major, critical) |
| Milestones | 4 (Dictionary→Book, Digitization Quality, Structured Data, Major Enhancements) | 5 (API Stability, UX, Data Quality, DevX, Community) |
| Org Projects | 4 (one per milestone) | 2 (Stability & Quality, Capabilities & Roadmap) |
| Domain labels | — | Yes, scoped to repo category |
| Cross-repo coordination | implicit | explicit `cross-repo` label + `CROSS_REPO_INDEX.md` |
| License default | CC-BY-SA-4.0 (data) | GPL-3.0 (software) |
| Phases | 16 | 17 (extra: cross-repo registry) |

## Phases (v2, 2026-05-07)

| Phase | Action |
|---|---|
| 0 | Set repo variables; verify access |
| 1 | Audit existing issues, labels, milestones |
| 2 | Create the 9 type labels and 3 severity labels with canonical colours |
| 3 | Assign exactly one type label per issue; remove conflicting GitHub-default labels |
| 4 | Assign exactly one severity label per issue |
| 5 | Create the 4 milestones; assign each issue to its milestone |
| 6 | Add each issue to the corresponding GitHub Project |
| 7 | Verify (5 integrity checks must all reach 0) |
| 8 | Generate `CLAUDE.md` |
| 9 | Generate `README.md` with live counts and Mermaid charts |
| 10 | Commit and push |
| 11 | Add citation infrastructure (`CITATION.cff`, `LICENSE`, `CHANGELOG.md`, Zenodo wiring) |
| 12 | Add printed-source bibliography block |
| 13 | Add data dictionary + annotated example entry |
| 14 | Declare encoding policy (UTF-8 NFC, SLP1 boundaries, round-trip status) |
| 15 | Generate pipeline DAG (Mermaid flowchart) |
| 16 | Drop community files (`CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`, `.github/ISSUE_TEMPLATE/`, PR template) |

Phase 7 is a **hard gate**: all five integrity checks (missing type
label, missing severity, missing milestone, multi-type, milestone-type
mismatch) must reach zero before the runbook proceeds to documentation.

## Status (2026-05-29)

### Dictionary runbook

Eight active dictionary repositories have completed Phases 0–10:
**AP, AP90, FRI, GRA, MD, MWS, PWG, PWK**.

Phase 16 (community files) was completed for these eight repos via
`scripts/propagate_templates.py`.

Phases 11–15 (citation, source bibliography, data dictionary, encoding,
pipeline DAG) are specified in this runbook but have not yet been
executed; they are scheduled for 2026 Q3.

The remaining dictionary repositories with significant issue volume
(ACC, AMAR, ApteES, BEN, BHS, BOP, BOR, BUR, CAE, CCS, INM, KOW, KRM,
LRV, MCI, PUI, SHS, SKD, STC, VCP, VEI, WIL) are queued for triage.

### Tooling runbook

All 33 tooling repositories have completed Phases 0–10. The unified
taxonomy is enforced (24-label set + 5 milestones each) and every open
issue (~312 across the org) is tracked in the org-level
[Tooling Roadmap](https://github.com/orgs/sanskrit-lexicon/projects/9).

Processed in two waves:

- **2026-05-07 (initial)**: `csl-apidev`, `csl-websanlexicon`,
  `csl-corrections`, `cologne-stardict`.
- **2026-05-28/29 (full sweep)**: `csl-observatory`, `MWinflect`,
  `alternateheadwords`, `hwnorm1`, `csl-devanagari`, `mw-dev`,
  `csl-inflect`, `csl-ldev`, `csl-pywork`, `csl-homepage`, `hwnorm2`,
  `csl-app`, `literarysource`, `csl-doc`, `csl-newsletter`,
  `csl-westergaard`, `csl-kale`, `csl-lnum`, `csl-lslink`, `csl-sqlite`,
  `avlinks`, `rvlinks`, `csl-whitroot`, `csl-json`, `csl-atlas`,
  `csl-santam`, `sanskrit-fonts`, `cologne-hugo`,
  `sanskrit-lexicon.github.io`, `csl-orig`.

The runbook is now codified as
[`scripts/tooling_runbook.py`](../scripts/tooling_runbook.py) — eight
subcommands (`setup`, `classify`, `verify`, `project`, `refresh`,
`milestones`, `sha`, `audit`) that implement Phases 2–9 mechanically.

## Citation

If you cite this runbook directly, please use the entry in
[`../CITATION.cff`](../CITATION.cff) and the BibTeX entry
`runbook2026` in [`../article/refs.bib`](../article/refs.bib).