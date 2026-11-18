_Created: 18-11-2026 · Last updated: 18-11-2026_

# CLLG comparison — re-snapshot cadence

_Dr. Mārcis Gasūns_

This document records how the CLLG comparison is refreshed. It is the procedure, not a scorecard: the frozen [`18-11-2026` snapshot](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/docs/CLLG_VS_SANSKRIT_ESTATE_18-11-2026.md) is never edited in place. A refresh produces a **new dated document**; a silent edit of the old one is not a refresh.

## When to re-snapshot

No timer and no auto-refresh. Re-snapshot only when a primary source materially changes (the [CLLG landing page](https://cllg-project.github.io/), a publication record, a dataset release) or when evidence refutes a scored cell. All eight axes are re-scored against the new evidence; verdicts may move in either direction, and a binary "we lead" claim is never permitted without per-cell evidence. The terms of the comparison are defined in [`CONTEXT.md`](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/CONTEXT.md).

## Procedure

1. **Freeze a new dated internal doc** `docs/CLLG_VS_SANSKRIT_ESTATE_<DD-MM-YYYY>.md`, copying the structure of the 18-11-2026 source, including the three marked blocks (`PUBLIC-CAVEATS`, `PUBLIC-SCORE`, `PUBLIC-MOVES`). Bump the dated header and title, and open with a short re-snapshot note naming what changed and why. The verdict scale stays LEADS / PARITY / TRAILS / NO COMPARABLE DATA.
2. **Move the generator's pinned literals in the same PR.** [`scripts/gen_cllg_comparison_page.py`](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/scripts/gen_cllg_comparison_page.py) currently hard-codes `SOURCE`, `TARGET`, the `18-11-2026` title/intro date and `SOURCE_URL`. Update all of them together with the new doc; never point the generator at a moved doc while leaving a stale date in the public page.
3. **Regenerate and verify locally:** `--emit` writes the derived page, `--check` must report byte parity, and `--selftest` must report 4/4 controls. If the scorecard column schema changes, update `redact()` and the header assertion in the same PR and add a matching control — internal-only evidence must be omitted from the derived page (the source doc is public and still carries it).
4. **Let the CI gate prove it.** [`.github/workflows/cllg-page-parity.yml`](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/.github/workflows/cllg-page-parity.yml) runs `--selftest` and `--check` on every push, PR and dispatch. Both must be green before merge; a stale page is a release blocker, not a follow-up.
5. **Land additions-only.** Queue a `changelog_queue/*.md` fragment, land through a claimed worktree and a PR, merge, then cut the release. Mint a new handoff for the re-snapshot itself — do not reuse H8426 or H8430.
6. **Retire, never overwrite.** When the new doc is live, `git mv` the superseded dated doc into `docs/archive/` and leave a one-line tombstone pointing at its replacement. The old snapshot remains inspectable; its numbers are not silently refreshed.

## Guardrails

- A dated snapshot's "Last updated" line may change only for apparatus repairs around the frozen data; any verdict or number change requires step 1's new document.
- The generated public page is never hand-edited. It is rebuilt by `--emit` from the canonical doc, with the `Internal evidence` column withheld and a generic `internal-only — not published` label substituted.
- Closest-analogue mappings stay interpretive and labelled; proprietary comparators stay NO COMPARABLE DATA unless primary evidence says otherwise.

_Dr. Mārcis Gasūns_
