# Runbook

This folder contains the canonical, version-controlled source of the
**Cologne issue-taxonomy runbook** — the multi-phase procedure that
applies the project's unified issue taxonomy (nine type labels, three
severity labels, four milestones, four GitHub Projects) to a CDSL
dictionary repository.

The runbook is invoked as a Claude Code custom slash command. Authorised
users with Claude Code installed can run it as:

```
/cologne-issue-runbook <REPO>          # one repo
/cologne-runbook-all                   # detect-and-process all unprocessed repos
```

The two `.md` files in this folder are also installed at
`~/.claude/commands/` on the project lead's workstation.

## Files

| File | Role |
|---|---|
| [`cologne-issue-runbook.md`](cologne-issue-runbook.md) | The full sixteen-phase runbook for a single repository |
| [`cologne-runbook-all.md`](cologne-runbook-all.md) | Wrapper that fans out the runbook to every unprocessed repo |

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

## Status (2026-05-07)

Eight of the active dictionary repositories have completed Phases 0–10:
**AP, AP90, FRI, GRA, MD, MWS, PWG, PWK**.

Phase 16 (community files) was completed for these eight repos via
`scripts/propagate_templates.py`.

Phases 11–15 (citation, source bibliography, data dictionary, encoding,
pipeline DAG) are specified in this runbook but have not yet been
executed; they are scheduled for 2026 Q3.

The remaining 14 dictionary repositories with significant issue volume
(ACC, AMAR, ApteES, BEN, BHS, BOP, BOR, BUR, CAE, CCS, INM, KOW, KRM,
LRV, MCI, PUI, SHS, SKD, STC, VCP, VEI, WIL) are queued for triage.

## Citation

If you cite this runbook directly, please use the entry in
[`../CITATION.cff`](../CITATION.cff) and the BibTeX entry
`runbook2026` in [`../article/refs.bib`](../article/refs.bib).
