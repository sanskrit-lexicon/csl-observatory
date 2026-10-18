# Ruff baseline (H5800, 2026-10-04)

csl-observatory carried 106 .py files / ~30k LOC with **no linting at all** when
H5800 bootstrapped pytest + ruff into CI. Bootstrapping with the whole legacy
surface clean was out of scope, so ruff starts from a **documented baseline
count that can only move down** — never a silent zero.

## The numbers at bootstrap

| Fact | Value |
|---|---|
| Baseline violation count | **685** (machine mirror: `.ruff-baseline`) |
| Ruleset | `ruff.toml`: `E4, E7, E9, F, I, B, S, C4` (+ per-file-ignores for `tests/**` and the gate script) |
| Ruff version | 0.16.10 (any ≥0.8 per requirements-dev.txt) |
| Command | `ruff check . --output-format concise` |
| Live census | 2026-10-04, worktree off `origin/main` @ `844046a`, verified in a CI-equivalent venv |

Top offenders at bootstrap: `I001` unsorted imports (66), `F541` f-string
without placeholders (48), `F401` unused imports (12), `S110` try-except-pass
(10), `F841` unused locals (6), `E722` bare except (6), `B023` loop-variable
binding (6). The H5800 test suite and gate script themselves ship lint-clean —
the baseline covers the legacy surface only.

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
