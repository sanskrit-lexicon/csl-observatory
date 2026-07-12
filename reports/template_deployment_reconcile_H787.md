# Template vs deployment reconcile — the 5 census-flagged pipeline families (H787)

_Created: 12-07-2026 · Last updated: 12-07-2026_

_Companion to [reports/code_duplication_census.md](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/reports/code_duplication_census.md) §1 (H688, [PR #85](https://github.com/sanskrit-lexicon/csl-observatory/pull/85)). Per-family verdicts by Opus 4.8 (`claude-opus-4-8`), H787. Diffs run against the census's own modal-cluster representatives — re-derivable via [scripts/code_duplication_census.py](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/reports/code_duplication_census.json)._

## Why this doc exists

The H688 census raised two ⚠️ on the build-pipeline families whose canonical home is
[csl-pywork](https://github.com/sanskrit-lexicon/csl-pywork) `makotemplates` ([SHARED_CODE.md §3](https://github.com/gasyoun/github-spine/blob/main/SHARED_CODE.md)):

1. **"Template lags deployment"** — the canonical copy is not the modal deployed version for
   `transcoder.py`, `updateByLine.py`, `parseheadline.py`, `redo.sh`, php endpoints.
2. **"Headless"** — `digentry.py` has no copy in csl-pywork at all; every copy is a leaf.

`canonical_is_modal = False` (flag 1) is only a *hash mismatch* signal — it does not say which
side is newer. This pass diffs each canonical against the modal deployed representative and
rules the direction. **The headline correction: for every `.py`/php family the csl-pywork
template LEADS deployment (it is the newer/cleaner code) — flag 1's "lags" wording is
inverted.** The one genuine defect is the headless family.

## Verdict table

| Family | csl-pywork canonical | Modal deployed cohort | Diff direction | Verdict | csl-pywork action |
|---|---|---|--:|---|---|
| `transcoder.py` | [`v02/distinctfiles/mw/pywork/`](https://github.com/sanskrit-lexicon/csl-pywork/blob/main/v02/distinctfiles/mw/pywork/transcoder.py) (1 copy) | `AMAR/transcoder.py`-style, 53 copies | **template newer** | template-is-newer — deployment lags | none |
| `updateByLine.py` | [`v02/makotemplates/pywork/`](https://github.com/sanskrit-lexicon/csl-pywork/blob/main/v02/makotemplates/pywork/updateByLine.py) (newest of 3) | 75/54 bimodal (differ by 1 line) | **template newer** | template-is-newer; the "75/57 split" is one `sys.stdout.reconfigure` line, **not** a real fork | none |
| `parseheadline.py` | [`v02/makotemplates/pywork/`](https://github.com/sanskrit-lexicon/csl-pywork/blob/main/v02/makotemplates/pywork/parseheadline.py) (newest of 3) | `AP/issue16`-style, 67 copies | **template newer** | template-is-newer — deployment lags | none |
| `digentry.py` | **none — headless** | `AP90/issue26`-style, 183/193 (95%) | n/a — no head | **add modal as canonical** | **ADD** `v02/makotemplates/pywork/digentry.py` |
| php endpoints | [`csl-websanlexicon/v02/makotemplates/web/webtc/`](https://github.com/sanskrit-lexicon/csl-websanlexicon/tree/main/v02/makotemplates/web/webtc) | `webbackup/**/webtc/` snapshots | **template newer** | template-is-newer; the family-level "modal" is a lumped-basename artifact, and webbackup ≠ live deployment | none (and out of csl-pywork scope) |

## Evidence per family

**`transcoder.py` — template newer.** Canonical vs the 53-copy modal (`AMAR/transcoder.py`):
canonical uses `if outval is None` (modal: `if (outval == None)`), `open(…, encoding='utf-8')`
(modal: `codecs.open`), and drops unused `import sys`/`codecs`/`normalize` plus dead
`regexpairs`/`best` code. The canonical is a deliberate modernization/cleanup of the modal —
i.e. the template is ahead; deployments will pick it up on next regeneration.

**`updateByLine.py` — template newer; the bimodal split is one line.** The census's
"bimodal 75/57" resolves to: modal-A (75, `ApteES`) = modal-B (54, `AP`) **plus a single
`sys.stdout.reconfigure(encoding='utf-8')` line** — both are the same old `codecs`-era
generation. The canonical `v02` template is newer than both (`open(encoding=)` /
`except Exception:` vs `codecs.open` / bare `except:`). Not a `@DECIDE`. (Note: csl-pywork's
own `v00/makotemplates/updateByLine.py` is a stale older copy than its `v02` sibling —
internal version skew, not load-bearing here.)

**`parseheadline.py` — template newer.** Canonical `v02` vs the 67-copy modal
(`AP/issue16`): canonical uses `except Exception:` (modal: bare `except:`) and tidier imports.
Template ahead.

**`digentry.py` — headless, add the modal.** 193 leaf copies, **183 byte-identical** (95%),
zero in csl-pywork. The modal cohort (working-copy md5 `a4f5e7c0…`; its LF-normalized,
repo-convention form is `b3bb9d71…`) is the de-facto template. Fix: add it verbatim to
`v02/makotemplates/pywork/digentry.py` so the family regains a head. It is old-style
(`codecs`), matching the deployed reality — canonicalize as-deployed; a later modernization
pass (as done for the other three families) is separate work.

**php endpoints — template newer; "modal" is an artifact.** The census family lumps 5 distinct
basenames, so its "modal cluster" is merely `servepdf.php`×13 — all in
`csl-websanlexicon/webbackup/`, which are per-dict **deployment snapshots, not templates**
(the census excludes `webbackup/` from "canonical" by construction). Per-basename, the
canonical `v02/makotemplates/web/webtc/` files are the **newer, class-refactored** versions
(`servepdf.php` → `require_once('servepdfClass.php')`, 2019 refactor; `getword.php` carries a
JSONP-callback XSS guard the old `webbackup` monolith lacks). Template ahead; nothing to
reconcile, and php lives in csl-websanlexicon, outside the csl-pywork correction-pipeline
family anyway.

## Actions taken

- **csl-pywork PR** — adds the single missing `v02/makotemplates/pywork/digentry.py`
  (modal version, LF-normalized to repo convention). No behavioural change to any generated
  dictionary. This is the only source change the reconcile requires.
- **No change** for `transcoder.py` / `updateByLine.py` / `parseheadline.py` / php — the
  template already leads; "fix the template, then regenerate" is exactly correct for them and
  will bring deployments up to current.
- `redo.sh` / `make_xml.py` remain **exempt** (per-issue copies by design, SHARED_CODE §3).

## Correction to the census wording

The census §1 ⚠️ "Template lags deployment — … 'fix the template, then regenerate' silently
regenerates from a version nobody deploys" is **inverted** for `transcoder.py` /
`updateByLine.py` / `parseheadline.py` / php: the template is *newer*, so regenerating from it
is the right action, not a hazard. The accurate residual risk is narrower — only that a fix
authored by eye against an *old deployed copy* could look different from the newer template;
always edit the csl-pywork template, never a deployed leaf.

_Dr. Mārcis Gasūns_
