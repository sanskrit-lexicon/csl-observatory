# Taxonomy Drift Watch — design

Keep every repo **taxonomy-complete after** the 2026-05 rollout, by catching
regressions (new unlabelled issues, multi-type labels, missing milestone /
project) instead of trusting that "done" stays done. This is a **detector**, not
an auto-fixer — see *Apply mode* below.

## What already exists (don't duplicate)

| Piece | Covers | Trigger |
|---|---|---|
| [`scripts/tooling_runbook.py`](../scripts/tooling_runbook.py) `verify` / `audit` | tooling repos (per-issue gate + project reconciliation) | manual |
| [`.github/workflows/tooling-audit.yml`](../.github/workflows/tooling-audit.yml) | tooling repos | weekly cron + dispatch |

The **dictionary** side had no equivalent. This change adds it, modelled on the
tooling pieces rather than reinventing them.

## The two layers

**1. Backstop audit (cron + dispatch).**
[`scripts/dict_runbook.py`](../scripts/dict_runbook.py) `audit` over the 34
dictionary repos, driven by [`.github/workflows/dict-audit.yml`](../.github/workflows/dict-audit.yml)
weekly (Mon 03:30 UTC) and on demand. A nonzero `mismatches:` count fails the
job — a red check is the per-run signal. Tooling repos keep their existing
weekly audit.

**2. Event-driven guard (per-repo).**
[`runbook/templates/taxonomy-drift.yml`](../runbook/templates/taxonomy-drift.yml)
re-checks the *changed* issue on every `issues` event and toggles a
`needs-triage` label. Immediate; needs no PAT (uses `--no-project` +
`GITHUB_TOKEN`). Currently a **draft template** — fanned out per-repo by a future
`cologne-drift-watch-all` skill after the pilot.

## Detection contract

Per-issue, paginated, PRs excluded (GraphQL `issues` connection). An issue is
complete when it has exactly **1 type** + **1 severity** + **1 milestone** +
membership in the **org project matching that milestone** (Dictionary to Book=1,
Digitization Quality=2, Structured Data=3, Major Enhancements=4; **MWS uses
5–8**). Tooling repos use the tooling taxonomy (17 types, 4 severities,
`discussion` is milestone-exempt). This is the logic proven in
`_verify_clean.py`, promoted into `dict_runbook.py`.

## Apply mode — PR-only, never push to default

The watch **never auto-applies taxonomy** and never pushes to a default branch.
Actual fixes stay the human-run [cologne-issue-runbook](../runbook/cologne-issue-runbook.md)
/ `tooling_runbook.py classify`, which open their own changes for review. The
guard's only write is the `needs-triage` label (issue metadata, not a commit).
(Taxonomy assignments are label/milestone/project API calls, so they can't be a
PR; detection-only is the coherent reading of "PR-only".)

## Tokens

- Cron audits need org **projectV2 read**, which `GITHUB_TOKEN` lacks → reuse the
  existing **`TOOLING_AUDIT_TOKEN`** PAT (`read:project` + `repo`), credential
  **C1** in [DECISIONS_NEEDED.md](DECISIONS_NEEDED.md). No new token.
- The event guard needs no PAT (project dimension deferred to the cron via
  `--no-project`).

## Audit trail

Per-run: the workflow's red/green check + `GITHUB_STEP_SUMMARY` table (same as
`tooling-audit.yml`). Open decisions / credentials: `DECISIONS_NEEDED.md`.
(`.ai_state.md` in this repo is dedicated to the L0 cladogram research and is
**not** used for drift.)

## Out of scope — meta repos

`COLOGNE`, `CORRECTIONS`, and `temp_corrections_*` are cross-dictionary
issue-tracker / coordination repos, **not watched** — skipped as legacy/meta per
DECISIONS_NEEDED.md A2.

## Rollout

1. ✅ `dict_runbook.py` (`verify` / `audit` / `issue`) — live-tested 2026-05-31
   (34/34 dict repos clean; MWS verified under 5–8).
2. `dict-audit.yml` backstop — **needs `TOOLING_AUDIT_TOKEN`** present (already
   set for tooling-audit). Then enable.
3. Pilot the event guard on one low-traffic repo (e.g. `GRA`) + create its
   `needs-triage` label; confirm it's quiet and correct.
4. Fan out the guard via a `cologne-drift-watch-all` batch skill.
5. Document the skill in the runbook.

## Open decisions (tracked in DECISIONS_NEEDED.md)

- Pilot repo + whether to enable the event guard fan-out (vs cron-only).
- Whether to add a single-issue mode to `tooling_runbook.py` so the guard also
  covers tooling repos.
- Whether the cron audit should additionally append a drift list to a dated
  report (current default: red check + step summary only, to stay low-noise).
