_Created: 27-07-2026 · Last updated: 05-09-2026_

# Encoding/XML Guard — design (RH5)

Catch encoding regressions on dictionary-source change paths before they land
— a BOM re-introduced by an editor's tool, a non-NFC accented character, a
malformed XML edit — instead of relying on manual review to notice
([`../CLAUDE.md`](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/CLAUDE.md) "Encoding — BOM is inconsistent, check before
editing" already documents how easy this is to get wrong by hand).

## What already exists (don't duplicate)

| Piece | Covers | Trigger |
|---|---|---|
| [`scripts/dict_runbook.py`](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/scripts/dict_runbook.py) / [`dict-audit.yml`](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/.github/workflows/dict-audit.yml) | issue taxonomy completeness | weekly cron + dispatch |
| [`runbook/templates/taxonomy-drift.yml`](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/runbook/templates/taxonomy-drift.yml) | per-issue taxonomy drift | issue events (draft template) |

Neither checks file *content* hygiene — this is a new, third piece, modelled
on the same two-layer shape as [`DRIFT_WATCH.md`](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/docs/DRIFT_WATCH.md) rather than
reinventing it.

## The guard

[`scripts/encoding_xml_guard.py`](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/scripts/encoding_xml_guard.py) `check
<path>...` — four rules per file:

1. **no-bom** — file does not start with a UTF-8 BOM, unless explicitly
   allowlisted (`--allow-bom`; some legitimate exports carry one — see
   CLAUDE.md, never strip silently).
2. **utf8** — decodes as UTF-8.
3. **nfc** — decoded text is already Unicode NFC-normalized.
4. **xml-parse** — `.xml` files parse with `xml.etree.ElementTree`.

CI-friendly contract, same shape as `dict_runbook.py`/`tooling_runbook.py`
`audit`: one `FAIL [rule] file: message` line per violation, a final
`violations: N` line, exit 0 iff N == 0.

## The two layers

**1. Pilot (this repo).** [`.github/workflows/encoding-guard.yml`](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/.github/workflows/encoding-guard.yml)
runs `encoding_xml_guard.py self-test` against bundled fixtures
([`runbook/fixtures/encoding_guard/`](../runbook/fixtures/encoding_guard))
on every push/PR touching the guard or its fixtures, plus `workflow_dispatch`.
`self-test` asserts every `good/*` fixture passes clean and every `bad/*`
fixture (one BOM, one non-NFC, one invalid-UTF-8, one malformed-XML) is
caught — the job's red/green state is driven by actually running the guard
against injected bad files, not just unit-testing the logic in the abstract.
This satisfies RH5's "piloted on csl-orig or the owning tooling repo"
acceptance clause via the *owning tooling repo* branch: csl-observatory owns
this CI template, so the pilot lives here rather than in csl-orig (agents
never commit to csl-orig directly, per `../CLAUDE.md`).

**2. Event-driven guard (per-repo, fan-out).**
[`runbook/templates/encoding-xml-guard.yml`](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/runbook/templates/encoding-xml-guard.yml)
— a **draft template**, mirroring `taxonomy-drift.yml`'s shape: fetches
`encoding_xml_guard.py` from csl-observatory via sparse checkout, runs it on
a PR's changed files within that repo's dictionary-source change paths, and
blocks the PR with a red check on any violation. Not deployed anywhere yet —
fanned out to specific repos by a future `cologne-encoding-guard-all` batch
skill, once a pilot repo + its actual change paths are chosen (analogous to
`DRIFT_WATCH.md`'s step 3).

## Apply mode — detect only, never rewrite

The guard never modifies a file. A violation is a red CI check; the fix stays
a human/agent edit reviewed the normal way. This mirrors `DRIFT_WATCH.md`'s
"Apply mode" stance and the org rule against silently stripping/adding a BOM.

## Tokens

None. `contents: read` + the default `GITHUB_TOKEN` is enough for both layers
— no PAT, unlike the taxonomy audits' `TOOLING_AUDIT_TOKEN` (which needs
`read:project`).

## Rollout

1. ✅ `encoding_xml_guard.py` (`check` / `self-test`) — self-test passes
   (2 good + 4 bad fixtures), verified 27-07-2026.
2. ✅ `encoding-guard.yml` pilot, live in this repo.
3. Pick a pilot repo + its real dictionary-source change paths (e.g. a
   `csl-corrections` batch directory) for the fan-out template; edit
   `CHANGE_PATHS_PLACEHOLDER` in `encoding-xml-guard.yml` and deploy.
4. Fan out via a `cologne-encoding-guard-all` batch skill (mirrors
   `cologne-drift-watch-all`).

## Open decisions

- Which repo(s) get the event-driven fan-out first, and what their actual
  `CHANGE_PATHS_PLACEHOLDER` change paths are.
- Whether any dictionary repo has a *legitimate* BOM-carrying export that
  needs a standing `--allow-bom` entry before the fan-out (per CLAUDE.md's
  "some HeadwordLists exports have one, some don't" note) — audit before
  deploying, don't assume clean.

_Dr. Mārcis Gasūns_
