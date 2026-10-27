# Ruff baseline (H5800, 2026-10-04)

csl-observatory carried 106 .py files / ~30k LOC with **no linting at all** when
H5800 bootstrapped pytest + ruff into CI. Bootstrapping with the whole legacy
surface clean was out of scope, so ruff starts from a **documented baseline
count that can only move down** — never a silent zero.

## The numbers (baseline as recorded)

| Fact | Value |
|---|---|
| Baseline violation count | **702** (machine mirror: `.ruff-baseline`) — was 731 at the 2026-10-19 re-record, see *Re-record 2026-10-27* below |
| Ruleset | `ruff.toml`: `E4, E7, E9, F, I, B, S, C4` (+ per-file-ignores for `tests/**` and the gate script) |
| Ruff version | **pinned 0.17.1** (`requirements-dev.txt`); the count is version-sensitive, so the pin and the baseline move together |
| Command | `ruff check . --output-format concise` |
| Live census | 2026-10-27, worktree off `origin/main` @ `83bbb2b`, 702 violations |

### Re-record 2026-10-19 (bughunt §1)

The 685 recorded here was measured **before** this repo's own `ruff.toml` landed
(it arrived in the same commit as the baseline, `41eac8f`, PR #250), so the gate
has failed on every run it ever made — measured on that commit the count was
already 716, and 731 on today's `main`. Two lessons, both now enforced:

1. re-measure with the ruleset you ship, and
2. pin the ruff version — at `844046a` ruff 0.16.5 counts 694 where 0.16.10
   counted 685, so an unpinned runner upgrade can redden the gate with no
   commit at all (`ruff>=0.8` → `ruff==0.17.1`).

The 731 is a **re-record, not a regression budget**: the delta is the 46
violations the bootstrap window itself introduced, mostly `I001`/`E401`/`E702`
in the legacy surface. Fixing them is a separate, reviewable sweep — the gate's
job until then is to stop new ones from landing.


Top offenders at bootstrap: `I001` unsorted imports (66), `F541` f-string
without placeholders (48), `F401` unused imports (12), `S110` try-except-pass
(10), `F841` unused locals (6), `E722` bare except (6), `B023` loop-variable
binding (6). The H5800 test suite and gate script themselves ship lint-clean —
the baseline covers the legacy surface only.

### Re-record 2026-10-27 (dedup + bug-class hygiene)

731 → 702. The three bug-class rules the bootstrap census called out are
emptied: `E722` bare except (6 — narrowed to `json.JSONDecodeError`/`OSError`,
with a stderr warning where jq output was silently swallowed), `B023`
loop-variable binding (6 — the two `pq()` closures in `lowm_estimators.py` now
bind via default args, same-iteration behaviour preserved), `F841` unused
locals (8 — dead assignments removed). The other 9 of the delta (S603 ×3,
S607 ×1, S110 ×5) died with the four byte-identical `gh api` retry helpers in
`rh1_put_file`/`rh1_apply_dual`/`rh1_infra_probe`/`rh1_mixed_probe`, which now
share `scripts/_common.py::gh_api()` — the retry core lives in one place; the
15 remaining private `gh`/`git`/`run` wrappers are semantic variants, not
copies (distinct retry/rate-limit/return contracts), and stay local by design.
Measured with the pinned 0.17.1.

## The gate

`scripts/ruff_baseline_gate.py` (wired into `.github/workflows/smoke-tests.yml`):

- **PASS** when live count `<=` `.ruff-baseline`.
- **FAIL** when live count `>` baseline, with refresh instructions.
- **FAIL (fail-closed)** when ruff produces no parsable output (dead/missing
  ruff must never read as a clean repo — negative-controlled locally).

## Refreshing the baseline

Only after review, and only downward in spirit:

```sh
python scripts/ruff_baseline_gate.py --refresh
```

…then update this doc's table and say WHY the count moved (fixes, new files,
ruleset change) in the commit message. A count that grows because new code was
added is a normal event — bump the baseline and keep the delta visible here.
