# AI / Bot Contribution Policy

Norms for AI-assisted and automated contributions across the [`sanskrit-lexicon`](https://github.com/sanskrit-lexicon) org, after maintainer feedback (e.g. MWS#194) on the value and volume of bot-attributed activity. The goal: keep AI assistance useful and auditable without adding noise that burdens reviewers.

## Commits

- **Dictionary repos** (dictionary data + per-dict development repos): use plain conventional-commit messages with **no AI co-author trailer**. Match the repo's existing convention.
- **Infrastructure / tooling repos** (`csl-observatory`, `csl-pywork`, `csl-corrections`, …): a `Co-Authored-By: Claude …` trailer is fine — it is already the convention there.

## Issue comments

- Prefer the **lowest-noise** option. On dictionary repos especially: **edit an existing comment in place** rather than posting a new one; keep comments terse and substantive (cite the fix commit + any audit-trail link — nothing more).
- Do **not** re-comment on already-resolved issues, and do not post a fresh comment where an edit will do.
- Batch any required questions and ask at most once per session.

## Pull requests & changes to canonical tooling

- Changes to shared pipeline code (e.g. `csl-pywork` generation scripts) should reference an issue and, where practical, go through review rather than silent direct commits.

## Rationale

Maintainers have flagged that high-volume bot/AI-attributed commits and comments add noise and dilute signal. These norms preserve the auditability of AI assistance (clear commit references, recorded rationale) while minimising reviewer burden.

## Scope

Applies to all automation and AI agents operating on the org — Claude Code / Agent SDK runs, CI bots, and the daily-corrections updater.

---
*Roadmap item Q6. See [`ROADMAP.md`](ROADMAP.md).*
