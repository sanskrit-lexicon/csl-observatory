# Tooling-runbook operating notes

Conventions and gotchas that aren't captured in the runbook spec itself
([runbook/cologne-tooling-runbook.md](../runbook/cologne-tooling-runbook.md))
but matter when applying it to live repos. Started 2026-05-29 after the
full-sweep pass.

---

## Canonical executor

Use **[`scripts/tooling_runbook.py`](../scripts/tooling_runbook.py)** —
do not reinvent the phases per repo.

| Subcommand | Phase | Purpose |
|---|---|---|
| `setup <repo> <category>` | 2 + 5 | Create/update 17 type + 4 severity + per-category domain labels; create 5 milestones |
| `classify <repo> <plan.json> [<domain>]` | 3 + 4 + 5 | Apply type/severity/milestone (+ optional `domain:*`) per issue; `plan.json` may include `strip` to delete stale labels |
| `verify <repo>` | 7 | Hard gate: missing/multi type, severity, milestone |
| `project <repo>` | 6 | Add every open issue to Tooling Roadmap (org project #9) |
| `refresh <repo> <category>` | 9 | Rewrite README with live counts + Mermaid pies; validates each Mermaid block via `gh api markdown` before commit |
| `audit <repos-csv>` | — | Reconcile project items vs per-repo open-issue counts |
| `milestones <repo>` | helper | Dump milestone numbers (used to build `plan.json`) |
| `sha <repo>` | helper | Get current README sha for Contents-API PUT |

`plan.json` format:

```json
{
  "<issue-number>": {"type": "...", "sev": "...", "ms": <ms-number>,
                     "strip": ["<stale-label>", ...]}
}
```

The category determines which `domain:*` labels exist for the repo;
the full mapping lives in `DOMAIN_MAP` inside the script.

---

## Phase 6 is mandatory, not optional

Org Project #9 **Tooling Roadmap** is the canonical aggregate view of
every open issue across every processed tooling repo. After any runbook
application, run `project <repo>` before declaring the repo done.

The 2026-05-29 audit caught a 71-issue gap from the initial 2026-05-07
wave: `csl-apidev`, `csl-websanlexicon`, `csl-corrections`, and
`cologne-stardict` had labels + milestones applied but their open
issues were never added to the project. Backfilled the same day.

Whenever new tooling repos come online (the org reference table in
[runbook/README.md](../runbook/README.md) tracks candidates), they
should be processed end-to-end — labels, classify, gate-pass, project,
README refresh — before being treated as onboarded.

---

## csl-orig is hybrid — layer both taxonomies

`csl-orig` hosts the source XML/text for every CDSL dictionary, so its
issue stream is dominated by dictionary-correction tickets
(`text-correction`, `markup`, `encoding`, `scan-quality`,
`content-enhancement`, `link-target` / `link-splitting`), not tooling
work. When applying the tooling-repo runbook to it:

- **Do not strip** the existing dictionary-runbook labels — they remain
  semantically valuable (e.g. `text-correction` vs `markup` is finer
  than tooling's `bug` vs `tech-debt`).
- Add tooling type + severity + milestone **alongside** the dictionary
  labels. The verifier only checks membership in the tooling type set,
  so the dictionary labels never trigger `multi_type`.

Useful mappings (dictionary label → tooling type / milestone):

| Dictionary label | Tooling type | Milestone |
|---|---|---|
| `text-correction`, `encoding`, `scan-quality` | `bug` | Data Quality |
| `markup` | `tech-debt` | Data Quality |
| `content-enhancement` | `feature` | User Experience |
| `link-target`, `link-splitting` | `enhancement` | User Experience |
| `bug` (data) | `bug` | Data Quality |
| `question` | `question` | Community |
| `dependencies` | `dependency` | Developer Experience |
| `github_actions` | `infrastructure` | Developer Experience |

Severity: `medium` (dict) ≈ `minor` (tooling); `hard` ≈ `major`.

After classify, expect some pre-existing default `enhancement` labels
on issues newly classified as `bug` or `feature` — strip those to
satisfy the single-type gate. The 2026-05-29 csl-orig pass had 17 such
collisions on the type axis and 13 on the severity axis after the
initial batch; all resolved by targeted DELETE calls.

---

## Windows / encoding hygiene

When extending the script or writing helper scripts:

- Add `sys.stdout.reconfigure(encoding='utf-8')` and
  `sys.stderr.reconfigure(encoding='utf-8')` at the top.
- Pass `encoding='utf-8'` to every `subprocess.run` that reads `gh api`
  output.
- Prefer per-script `.py` files over inline shell heredocs.

For PowerShell command construction, avoid script blocks `{}` and
subexpressions `$()`; use native command parameters
(`Get-ChildItem -File`, not `Where-Object { -not $_.PSIsContainer }`).

---

## Mermaid pies must be validated

The `refresh` subcommand sends each mermaid block to
`gh api markdown` and aborts the README commit if the block doesn't
render. Don't bypass this check — broken pies look fine in plain text
but render as a literal code block on GitHub, silently hiding the
issue-type/severity breakdown.

---

## Weekly audit workflow

[`.github/workflows/tooling-audit.yml`](../.github/workflows/tooling-audit.yml)
runs the `audit` subcommand every Monday 03:00 UTC and fails the job on
any nonzero mismatch count. The workflow needs a repo secret
**`TOOLING_AUDIT_TOKEN`** — a PAT with `read:project` and `repo`
scopes. The default `GITHUB_TOKEN` does not have `read:project` for
org-level projectV2 items, so leaving the secret unset is detected
early and fails with a clear message.

If you add a newly processed tooling repo, append its name to the
`REPOS` env var in the workflow so it's included in the weekly check.

## Status snapshot (2026-05-29)

- **34 tooling repos** processed end-to-end (Phases 0–10).
- **312 open issues** classified and tracked in Tooling Roadmap.
- Audit: `312 in project ≡ 312 open across 34 repos`, **0 mismatches**.

Largest backlogs at snapshot: `csl-orig` 68, `MWinflect` 48,
`csl-websanlexicon` 25, `csl-apidev` 22, `csl-corrections` 21,
`alternateheadwords` 19, `hwnorm1` / `csl-devanagari` / `mw-dev` 17
each, `csl-inflect` 12.
