# BUGHUNT — csl-observatory — 19.10.2026

_Created: 19-10-2026 · /bughunt interactive day hunt · executor DeepSeek Flash (`deepseek-flash`) · fresh worktree off `origin/main`, never the shared main tree_

Hunted on `origin/main` **[96db6e1](https://github.com/sanskrit-lexicon/csl-observatory/commit/96db6e1)**. Elapsed 13 min (16:16–16:29 MSK), including two independent scoped audit passes run in parallel (measurement layer; validation/κ pipeline), every reported finding re-run by hand here. First report for this repo.

## Verdict first

**Eighteen defects: four HIGH, seven MEDIUM, seven LOW.** The four HIGH are fixed here (§1–§3, §18 — the last surfaced only when §1's fix let CI reach the next step). The repeating pattern is the one this repo's own design notes keep naming — **a gate is correct about the artifact it was written for and wrong about the artifact it is pointed at**: a lint gate whose baseline predates the ruleset it ships with, so its CI workflow has **never passed** (§1); a commit guard whose protected path is a hard-coded `C:/Users/user/...` string, so here it **never fires** (§2); a scorer that `round()`s a value its own helper documents as possibly `None`, so a degenerate sheet **loses the whole scoring run** (§3).

Then a family where **the number is right and the stated population is not** (§4, §7, §10), two **fail-open paths in the κ driver** that publish a statistic at exit 0 after an input went missing (§8, §9), and one **mis-named statistic**: `krippendorff_alpha_nominal` computes Scott's π — on Krippendorff's published example it returns 0.8935 where the paper says 0.743 (§5).

## What verified green (baseline)

| Check | Result |
|---|---|
| `python3 -m pytest tests -q` (minus the matplotlib-dependent import smoke) | **18 passed** |
| `python3 scripts/ruff_baseline_gate.py` after this run's refresh | `PASS` (live 731 = baseline 731) |
| `token_size_gate.py --staged`, scratch repo, 20 001-byte file | refused, exit 1, split plan printed |
| `.githooks/pre-commit` in main tree / in this worktree | exit 1 `BLOCKED` / exit 0 (after §2's fix) |
| `data_index.guard_lfs_smudged()` vs a synthetic 133-byte pointer | `SystemExit`, pointer's real size reported |
| κ = 0.906 [0.872, 0.938], flip 0.044/0.056 | re-derived (intersection denominator, sklearn 6 dp, 20 000-resample bootstrap 0.871–0.937) |

---

## §1 — HIGH · The ruff baseline gate has failed on every run since the workflow shipping it was merged

[`.ruff-baseline`](https://github.com/sanskrit-lexicon/csl-observatory/blob/96db6e1/.ruff-baseline) says `685`; [`scripts/ruff_baseline_gate.py`](https://github.com/sanskrit-lexicon/csl-observatory/blob/96db6e1/scripts/ruff_baseline_gate.py) runs in [`smoke-tests.yml`](https://github.com/sanskrit-lexicon/csl-observatory/blob/96db6e1/.github/workflows/smoke-tests.yml) with `ruff>=0.8`.

**Mechanism.** Workflow, `.ruff-baseline` and `ruff.toml` all arrived in the H5800 bootstrap commit `41eac8f` (PR #250), but the baseline was recorded **before** that commit's `ruff.toml` (`select = E4,E7,E9,F,I,B,S,C4`). On that very commit the count is already 716, on today's `main` 731. Every run has concluded `failure`; the repo merged through a permanently red check.

```
$ gh run list --workflow smoke-tests.yml --limit 25
2026-10-19T11:18:45 failure 96db6e12
2026-10-19T11:16:45 failure 95eb6208
2026-10-19T10:15:25 failure 29ee91e3      # 13 consecutive, no success ever
$ git archive 41eac8f | tar -x -C /tmp/atboot && cd /tmp/atboot && ruff check . --output-format concise --exit-zero | tail -1
Found 716 errors.
$ ruff check . --output-format concise --exit-zero | tail -1     # today's main
Found 731 errors.
```

Compounding defect: the count is **ruff-version-sensitive** and ruff is floored, not pinned — at the documented commit `844046a` this box's 0.16.5 counts 694 where the doc records 685 under 0.16.10, so a runner upgrade alone can redden the gate with no commit.

**Fix (applied).** `ruff==0.17.1` pinned with the reason; `.ruff-baseline` refreshed to the measured 731; `docs/RUFF_BASELINE.md` records the re-record. Verified: `PASS` at 731, and still `FAIL` when the baseline is lowered (negative control).

## §2 — HIGH · The shared-main-tree commit guard protects a path that does not exist on this machine

[`.githooks/pre-commit:34`](https://github.com/sanskrit-lexicon/csl-observatory/blob/96db6e1/.githooks/pre-commit#L34): `CANONICAL_MAIN_TREE="C:/Users/user/Documents/GitHub/csl-observatory"`.

**Mechanism.** The guard compares normalized `git rev-parse --show-toplevel` against one hard-coded Windows path. Every other clone — including the shared `/Users/mac/Documents/GitHub/csl-observatory` this hunt started from — never matches, so the hook exits 0 and the commit proceeds. The comment above it claims the guard "binds BOTH tools identically"; its purpose is preventing H214/H685-close tree-intermix (one session sweeping another's staged changes into its commit).

```
$ git rev-parse --show-toplevel
/Users/mac/Documents/GitHub/csl-observatory
$ bash .githooks/pre-commit ; echo exit=$?
exit=0                      # expected BLOCKED
```

**Fix (applied).** `CANONICAL_MAIN_TREE="${CANONICAL_MAIN_TREE:-$HOME/Documents/GitHub/csl-observatory}"` — same location on Windows Git Bash and macOS/Linux, overridable. Both controls verified: main tree `BLOCKED` exit 1, worktree exit 0.

## §3 — HIGH · `obs_t_gold.py --score` dies on a degenerate second-annotator sheet, losing every artifact

[`scripts/obs_t_gold.py:376`](https://github.com/sanskrit-lexicon/csl-observatory/blob/96db6e1/scripts/obs_t_gold.py#L376): `alpha = round(krippendorff_alpha_nominal(iaa_pairs), 3) if iaa_pairs else None`.

**Mechanism.** The helper returns `None` by contract when `D_e` is degenerate (all pairable values agree on one label, or <2 pairable values) — its docstring says so, and `obs_t_baselines.py:248` guards the identical call. This caller does not: `round(None, 3)` raises `TypeError` **before** `gold_metrics.json` / `obs_t_validation.md` are written, so a sheet whose second annotator used one location value across the sample loses the entire run (the κ path already special-cases that shape and returns 1.0).

```
$ python3 -c "import sys;sys.path.insert(0,'scripts');import obs_t_gold as G;print(G.krippendorff_alpha_nominal([('headword','headword')]*10));round(G.krippendorff_alpha_nominal([('headword','headword')]*10),3)"
None
TypeError: type NoneType doesn't define __round__ method
```

**Fix (applied).** `alpha_raw = … if iaa_pairs else None` / `alpha = round(alpha_raw, 3) if alpha_raw is not None else None`; `null` stays in the JSON. Verified: reproduction no longer raises, `py_compile` OK, suite green.

## §4 — MEDIUM · Gold accuracy is computed over the unresolved population while the artifact says it is not

[`scripts/obs_t_gold.py:384`](https://github.com/sanskrit-lexicon/csl-observatory/blob/96db6e1/scripts/obs_t_gold.py#L384) (`'accuracy': round(correct / n, 3)`) against the caveat at [`:436`](https://github.com/sanskrit-lexicon/csl-observatory/blob/96db6e1/scripts/obs_t_gold.py#L436): "accuracy and the evidence split cover the resolved subset only".

**Mechanism.** `n` and `by_ev` cover every annotated row; a row whose `event_id` did not join gets auto label `?` (line 355) and is scored wrong. The committed artifact publishes 0.221 = 86/390 while asserting it covers the 377 resolved rows, whose value is 0.228, and the evidence split carries the `?` bucket the prose says is excluded.

```
$ python3 -c "import json;m=json.load(open('validation/gold_metrics.json'));print(m['annotated'],m['accuracy'],m['eventIdJoin']['resolved'],m['countsByEvidence'])"
390 0.221 377 {'derived': 191, 'inferred': 186, '?': 13}
```

**Fix.** Filter the accuracy/evidence population to resolvable ids and print the excluded count, or change the caveat to say unresolved rows count as errors. Not applied — which sentence is true is a reporting decision.

## §5 — MEDIUM · `krippendorff_alpha_nominal` is not Krippendorff's alpha

[`scripts/obs_t_baselines.py:116`](https://github.com/sanskrit-lexicon/csl-observatory/blob/96db6e1/scripts/obs_t_baselines.py#L116) (mirrored in `obs_t_gold.py:178`).

**Mechanism.** Two departures from Krippendorff (2004, §11.3): `D_o` is divided by `n-1` instead of `n`, and coincidence counts omit the per-unit `1/(m_u-1)` normalisation, so units with more than two labels are overweighted. The result is Scott's-π-shaped: for two complete raters it equals π exactly (the function's own self-test asserts that at `:418`), whereas α = 1 − (n−1)/n·(1−π). On Krippendorff's published worked example (12 units, 2–4 coders, α = 0.743):

```
$ python3 /tmp/kalpha_canon.py
  repo implementation      : 0.8935
  standard (o/n, /(m_u-1)) : 0.7434
```

**Honest scope.** Both production call sites pass 2-tuples, where only the `n` vs `n−1` factor differs (~1e-4 here), so **no published 3-dp value changes today**; wrong are the name, the general-k docstring and the self-test pinning the wrong identity. **Fix.** Divide `D_o` by `n`, divide each unit by `(m_u−1)`, replace the π-identity assertion with an asymptotic check plus the 0.743 fixture.

## §6 — MEDIUM · `workflow_health.py` fail-open: an unknown `--repo` overwrites the published CSV with a header and exits 0

[`scripts/workflow_health.py:293`](https://github.com/sanskrit-lexicon/csl-observatory/blob/96db6e1/scripts/workflow_health.py#L293) filters metadata by `set(args.repo or [])`; a name matching nothing yields `rows = []`, which the writer at `:449` serialises over the committed `observatory/site/src/data/workflow_health.csv` while printing success. No unknown-name validation, no empty-set refusal.

```
$ python3 scripts/workflow_health.py --offline --repo notarepo --out /tmp/wf.csv --report /tmp/wf.md; echo exit=$?; wc -l /tmp/wf.csv
  repos: 0
exit=0
       1 /tmp/wf.csv              # header only
```

**Fix.** Refuse unknown names (`selected - {m['repo'] for m in metadata}`) and refuse to write an empty row set.

## §7 — MEDIUM · The OBS-Q headline counts all commits but is labeled "correction commits"

[`scripts/obs_q_correction.py:296`](https://github.com/sanskrit-lexicon/csl-observatory/blob/96db6e1/scripts/obs_q_correction.py#L296) → [`reports/obs_q_correction_sustainability.md:15`](https://github.com/sanskrit-lexicon/csl-observatory/blob/96db6e1/reports/obs_q_correction_sustainability.md#L15). `total_commits` sums the all-commits column (imports, reformats included) while the row label and per-year header say "correction commits". The same CSV carries the classification in `corrections`, and the report's own §3 says the correction-classified commit is the reliable unit.

```
$ python3 -c "import csv;r=list(csv.DictReader(open('observatory/site/src/data/obs_q_annual.csv')));print(sum(int(x['commits']) for x in r), sum(int(x['corrections']) for x in r))"
2067 1413
```

654 of the 2,067 are not correction commits.

**Fix.** Relabel 2,067 as "v02 commits analysed" and add `correction-classified commits | 1,413`, or sum `corrections`; rename the per-year header.

## §8 — MEDIUM · A dropped annotation batch silently shrinks the κ denominator; the run still exits 0

[`validation/compute_component_kappa.py:110`](https://github.com/sanskrit-lexicon/csl-observatory/blob/96db6e1/validation/compute_component_kappa.py#L110). The intersection `set(a) & set(b)` is right, but the symmetric difference is only `print`ed: nothing enters `component_kappa_stats.json`, nothing raises, exit 0, and the artifact is indistinguishable from a clean run — a reader cannot tell the pre-registered n=390 from a partial n.

```
$ python3 compute_component_kappa.py; echo exit=$?    # /tmp copy, one 60-row batch removed
WARN: 60 rows present in only one pass: [9, 14, 15, …]
n=330  L0 kappa=0.909 CI=[0.872, 0.941] agree=0.93
exit=0                      # nothing in the JSON records the 60 missing rows
```

**Fix.** `SystemExit` on a non-empty `set(a) ^ set(b)` unless an explicit `--allow-partial`, and record `n_missing` / `missing_row_ids`.

## §9 — MEDIUM · A missing flip-run file turns a numeric field of the κ artifact into a filename string

[`validation/compute_component_kappa.py:92`](https://github.com/sanskrit-lexicon/csl-observatory/blob/96db6e1/validation/compute_component_kappa.py#L92), consumed at `:151` (`stats[f"flip_rate_{ann}"] = fr if err is None else err`). `flip_rate()` returns `(None, "missing <file>")`; main stores the error **string** in a field every consumer reads as a float in 0..1, and exits 0.

```
$ python3 compute_component_kappa.py; echo exit=$?      # passA_run2.json removed
flip A=missing flip_runs/passA_run2.json  flip B=0.056
exit=0
$ python3 -c "import json;print(repr(json.load(open('component_kappa_stats.json'))['flip_rate_A']))"
'missing flip_runs/passA_run2.json'
```

**Fix.** The flip files are committed artifacts — absence is a broken instrument, so raise; or write `null` plus `"status": "incomplete"`.

## §10 — MEDIUM · The denominator label for the mirror class names the wrong population

[`scripts/obs_t_baselines.py:223`](https://github.com/sanskrit-lexicon/csl-observatory/blob/96db6e1/scripts/obs_t_baselines.py#L223) → [`reports/obs_t_baselines_field_metrics.md:42`](https://github.com/sanskrit-lexicon/csl-observatory/blob/96db6e1/reports/obs_t_baselines_field_metrics.md#L42). The loop feeds the mirror tuple `('correct', tn, fn, fp)` and then labels precision's denominator `all flagged tokens (tp+fp=…, 3,163)`. For class `correct` that is 3,163 **unflagged** tokens; the flagged count is 3,091, and 1,645/3,091 = 0.532 does not reproduce the published 0.52.

**Fix.** Label per class ("all flagged" for erroneous, "all unflagged" for correct) or use a neutral `tp+fp`.

## §11 — LOW · `obs_t_errorsample.py` promises a chi-square the scorer never computes

[`scripts/obs_t_errorsample.py:11`](https://github.com/sanskrit-lexicon/csl-observatory/blob/96db6e1/scripts/obs_t_errorsample.py#L11) docstring promises "chi-square + side-by-side shares"; `score()` emits only the shares and `grep -n chi scripts/obs_t_errorsample.py` matches the docstring alone. Fix: implement the 2×k test with an expected-cell guard, or drop the claim.

## §12 — LOW · Both LFS hooks are non-executable, and `core.hooksPath` bypasses the ones `git lfs install` writes

`.githooks/post-checkout` and `post-merge` are mode `0644`, so git ignores them (it says so at checkout: "The '.githooks/post-checkout' hook was ignored because it's not set as executable"), and with `core.hooksPath=.githooks` the standard hooks `git lfs install` writes into `.git/hooks` are bypassed too. `.gitattributes:30` LFS-tracks `observatory/site/src/data/correction_events*.csv`. Latent today (files are smudged, 11–62 MB), but a fresh clone silently gets stubs — the population `data_index.py` grew `guard_lfs_smudged()` for after #127. Fix: `chmod +x` both, assert the mode in a test.

## §13 — LOW · The duplicate-`row_id` guard in the κ driver cannot fire for string ids

[`validation/compute_component_kappa.py:67`](https://github.com/sanskrit-lexicon/csl-observatory/blob/96db6e1/validation/compute_component_kappa.py#L67) asserts `r["row_id"] not in out` while `out` is keyed by `int(r["row_id"])`. An exporter emitting `"row_id": "1"` walks past it; verified in /tmp — a duplicate row-1 label was accepted, κ moved 0.906 → 0.903, exit 0. Fix: normalise once, assert on `rid`.

## §14 — LOW · The blind-batch builder never clears stale batches

[`validation/build_blind_sample.py:51`](https://github.com/sanskrit-lexicon/csl-observatory/blob/96db6e1/validation/build_blind_sample.py#L51) writes `batch_01..NN` into a directory it never cleans, so a smaller re-draw leaves higher-numbered batches from the old draw behind, indistinguishable to anything globbing `blind_batches/batch_0*.json`. Only the hard `assert len(rows) == 390` prevents it today; on a 300-row draw, 6 batches were written and `batch_07.json` (60 stale rows) stayed live. Fix: unlink `batch_*.json` first (leave `gap_*.json`).

## §15 — LOW · `test_pyfloor_write_read_roundtrip_preserves_newlines` cannot fail on the platform it runs on

[`tests/test_helpers_smoke.py:30`](https://github.com/sanskrit-lexicon/csl-observatory/blob/96db6e1/tests/test_helpers_smoke.py#L30) claims the CRLF contract byte-for-byte, but `"a\r\nb\r\nc\r\n"` round-trips identically whether or not `write_text` passes `newline="\n"` (`os.linesep == "\n"` here), so dropping the kwarg stays green; only the read side is proven. Fix: include a bare `\n` in the body and assert raw bytes, or assert the kwarg with `mock.patch("io.open")`.

## §16 — LOW · The component guide's column contract is unsatisfiable on the blind path

[`validation/COMPONENT_GUIDE.md:9`](https://github.com/sanskrit-lexicon/csl-observatory/blob/96db6e1/validation/COMPONENT_GUIDE.md#L9) tells annotators to write `gold_component`, `notes`, `gold_component_2`; the artifact they receive carries none of the three (`BLIND_COLS` strips them) and the HTML sheet exports `location`/`edit_type`/`note`. Fix: state the write-back per path.

## §17 — MEDIUM · The new token gate has no grandfathering: 42 already-committed files become unmaintainable

`.githooks/token_size_gate.py` (shipped 19-10-2026) measures **staged** blobs, which is right for new files but also refuses any edit to a file that was already over budget before the gate existed. Found the hard way — this hunt's own two-line fix to `obs_t_gold.py` was refused:

```
$ python3 .githooks/token_size_gate.py --staged
  • scripts/obs_t_gold.py
    24 819 Б ≈ 6 205 токенов · превышение ×1.2 · нужно ≥ 2 части по ≤ 20 000 Б
```

42 tracked text files are over the 20 000 B budget and outside `.token-gate-ignore` — `scripts/recapture_sensitivity.py` 118 KB, `pre_push_stale_base_check.py` 107 KB, `obs_t_gold.py` 24.8 KB, plus docs and `CHANGELOG.md`. Each is now edit-blocked unless the agent splits it mid-fix, adds an ignore entry, or takes the `TOKEN_GATE_ALLOW=1` hatch (which this commit did, logged). **Fix.** Grandfather by HEAD — skip a staged file whose HEAD blob is already over budget; the gate's job is to stop *growth*.

## §18 — HIGH · Fixing §1 exposed a second CI blocker the workflow had never reached: an import-smoke test that cannot pass on CI

`tests/test_entry_point_imports.py` imports every script; `scripts/obs_t_gold_rekey.py:91` `sys.exit()`s at module level when no `csl-orig` sibling checkout exists — always true on CI. The file's own named-skip census exists for exactly this, but this script was never added. It was invisible until now because the ruff step runs first and always failed, so pytest never executed.

```
FAILED tests/test_entry_point_imports.py::test_script_imports_cleanly[scripts/obs_t_gold_rekey.py]
SystemExit: csl-orig not found (looked: env OBS_T_CSL_ORIG, sibling, ~/Documents/GitHub/csl-orig)
==================== 1 failed, 122 passed, 2 skipped in 1.62s ====================
```

**Fix (applied).** A named skip with its reason; `test_named_skips_still_exist` keeps the entry honest. With it, the workflow's ruff gate and pytest step both pass for the first time.

---

## Fixed in this run

§1, §2, §3 and §18 are fixed in this commit, each with its verification inline above. Not applied deliberately: §4, §7, §8, §9, §10 are reporting-contract decisions (which sentence/population is true) and belong to the owner; §5 changes a published statistic's definition; §6 and §11–§17 are report-only per the night ruling.

_Every finding here was re-executed by hand; audit-pass candidates that failed re-run are excluded rather than repeated. Severities: HIGH = wrong published number / data loss / crash; MEDIUM = misleading but bounded; LOW = cosmetic or latent._
