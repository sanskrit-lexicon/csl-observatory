# Refresh Script Modernization Plan

Date: 2026-06-12
Status: D2 implementation plan only; no `csl-pywork` files changed from this
document.

This plan covers the repository/process side of modernizing
`csl-pywork/v02/redo_xampp_selective.sh`, tracked by
[`csl-pywork#53`](https://github.com/sanskrit-lexicon/csl-pywork/issues/53).
It is intentionally backward-compatible with the current Cologne server flow and
does not authorize deployment or external repository mutations by itself.

## Current Behavior

Source files read for this plan:

- `csl-pywork/v02/redo_xampp_selective.sh`
- `csl-pywork/v02/readme_selective.md`
- `csl-pywork/v02/xmlchk_xampp.sh`

The current shell script:

- runs from the XAMPP-style `cologne/` layout, defaulting to
  `/var/www/html/cologne` with a `CSL_BASE` override;
- pulls `csl-pywork`, `csl-homepage`, `csl-websanlexicon`, `hwnorm1`,
  `csl-json`, `cologne-stardict`, and `csl-orig`;
- computes changed dictionary codes from `csl-orig` since
  `csl-orig/v02/.xampp_last_run`;
- runs `generate_dict.sh` for each changed dictionary;
- rebuilds Stardict output with `python2 make_babylon.py`;
- copies Stardict output into `indic-dict/stardict-sanskrit` and pushes it;
- rebuilds JSON output with `python2 json_from_babylon.py`;
- updates `csl-orig/v02/.xampp_last_run`, writes `csl-orig/.version`, and runs
  `csl-homepage/redo_xampp.sh`.

## Risks To Remove

| Risk | Why it matters | Modernization response |
|---|---|---|
| Python 2 calls remain in Stardict/JSON phases. | Python 2 blocks reproducible maintenance and CI smoke tests. | Port or wrap `make_babylon.py` and `json_from_babylon.py` under Python 3 before making the selective driver the canonical path. |
| Push-capable phases have no dry-run. | A maintainer cannot safely preview affected repos, commits, and pushes. | Add `--dry-run`, `--no-push`, and a generated phase plan before any write. |
| State is updated late but not transactionally. | A partial failure could leave generated repos changed while `.xampp_last_run` remains old, or a rerun could duplicate commits. | Update state only after all selected phases succeed; record a manifest with old/new commit, dictionaries, commands, and pushed repos. |
| No explicit clean-worktree guard. | Local uncommitted changes can be swept into generated commits. | Preflight every target repo; fail unless dirty paths are explicitly allowed per repo. |
| No lock around cron execution. | A reboot or manual run could overlap with another refresh. | Add a lock file or OS lock with stale-lock detection. |
| Path assumptions are partly hardcoded. | Server layout differs from local test layout and future CI. | Parameterize `--base`, `--indic-base`, `--state-file`, `--workdir`, and repo branch names. |
| Temporary files live in `csl-orig/v02`. | Helper files can leak into diffs or confuse future audits. | Use a temporary directory and write only the committed state file intentionally. |
| No structured summary. | Monthly reviews cannot tell what changed without reading logs. | Emit JSON and Markdown summaries for observatory review. |

## Target Interface

Keep the existing shell entry point as a compatibility wrapper:

```bash
bash v02/redo_xampp_selective.sh
```

Add a Python 3 driver, for example:

```bash
python3 v02/redo_xampp_selective.py \
  --base /var/www/html/cologne \
  --indic-base /var/www/html/indic-dict \
  --state-file csl-orig/v02/.xampp_last_run \
  --manifest refresh-manifest.json
```

Required options:

| Option | Purpose |
|---|---|
| `--base` | Parent directory for `csl-orig`, `csl-pywork`, `csl-homepage`, `csl-websanlexicon`, `hwnorm1`, `csl-json`, and `cologne-stardict`. |
| `--indic-base` | Parent directory for `stardict-sanskrit`. |
| `--state-file` | Last-successful `csl-orig` commit marker. |
| `--since` | Override the state file for one manual run. |
| `--dict` | Limit a run to one or more dictionary codes after diff detection. |
| `--dry-run` | Print phases, commands, repos, and commits without writing or pushing. |
| `--no-push` | Commit locally where needed but skip pushes. |
| `--skip-pull` | Use current local checkout state for offline tests. |
| `--strict-clean` | Fail if any participating repo has uncommitted changes. |
| `--allow-dirty REPO` | Permit known dirty repos during manual testing. |
| `--stop-after PHASE` | Stop after preflight, diff, generate, stardict, json, or homepage. |
| `--manifest PATH` | Write a machine-readable run summary. |

## Phase Design

| Phase | Writes | Pushes | Acceptance |
|---|---|---|---|
| Preflight | no | no | Required repos exist, expected branches/remotes are visible, Python 3 tools are importable, state commit exists, and clean-worktree policy is satisfied. |
| Pull | yes | no | Participating repos are updated or the run explains why `--skip-pull` was used. |
| Diff | temp only | no | Changed dictionaries are limited to valid `csl-orig/v02/<dict>/<dict>.txt` entry files unless manually supplied. |
| Generate display | yes | no | `generate_dict.sh <dict> ../../<dict>` succeeds for each dictionary; XML validation runs when XML exists. |
| Stardict | yes | optional | Python 3 Stardict generation succeeds; commits are created only when output changed. |
| Stardict sync | yes | optional | `stardict-sanskrit` receives copied output and commits only when changed. |
| JSON | yes | optional | Python 3 JSON generation succeeds; commits are created only when output changed. |
| Homepage/version | yes | optional | Version and homepage date update only after prior phases succeeded. |
| State update | yes | optional | `.xampp_last_run` advances to the exact processed `csl-orig` commit after all enabled phases succeed. |

## Implementation Sequence

1. Add Python 3 preflight in `csl-pywork` without changing the shell behavior.
2. Add `--dry-run` diff detection that prints the dictionaries and planned
   commands from the current state file.
3. Port or confirm Python 3 compatibility for Stardict and JSON generation.
4. Add phase execution with `--no-push` and no state update.
5. Add manifests and Markdown summary output.
6. Switch `redo_xampp_selective.sh` to call the Python 3 driver with the same
   default server paths.
7. Run one manual dry-run on the Cologne layout.
8. Run one `--no-push` rehearsal and inspect generated diffs.
9. Enable push-capable run only after maintainer/server confirmation.
10. Update `readme_selective.md` and observatory continuity docs with the final
    command.

## Validation Checklist

- `python3 v02/redo_xampp_selective.py --dry-run` works without git pushes.
- `--skip-pull --since <commit> --dict mw --stop-after diff` is deterministic.
- Invalid dictionary codes fail before generation.
- Empty diff produces no commits and does not push.
- Dirty target repos fail under `--strict-clean`.
- A failed generation phase does not update `.xampp_last_run`.
- Generated manifest records old commit, new commit, dictionaries, phases,
  changed repos, pushed repos, and failures.
- Human-facing README states cron usage, local dry-run usage, credentials,
  rollback limits, and which repos are written.

## Open Confirmations

| Question | Why it matters | Status |
|---|---|---|
| Should the canonical driver live in `csl-pywork/v02/redo_xampp_selective.py`? | Keeps it beside the current shell script and generation helpers. | recommended |
| Can `make_babylon.py` and `json_from_babylon.py` run under Python 3 today? | Determines whether D3 starts with dependency porting. | needs test in `csl-pywork` |
| Should pushes be split by repo or held until all generated outputs are ready? | Affects partial-failure recovery. | recommend split commits, push after all local commits succeed |
| Can the Cologne cron be changed to the wrapper after rehearsal? | Deployment requires server access and maintainer/admin approval. | blocked on C2/D1 |

No external repository mutation is authorized until the maintainer explicitly
starts the `csl-pywork#53` implementation step.
