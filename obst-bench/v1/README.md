# obst-bench v1 — a frozen, enterable benchmark over the E32 correction-event release

_Created: 24-10-2026 · Last updated: 24-10-2026_

**Benchmark of record:** this directory (`obst-bench/v1/`). **Corpus of record:**
[`data/publication/e32-correction-events-release-2026-10-10/`](../../data/publication/e32-correction-events-release-2026-10-10/README.md)
— SHA-256 pinned, 52,498 correction events, CC BY 4.0. **Scorer:**
[`scripts/obst_bench.py`](../../scripts/obst_bench.py). **Datasheet:**
[`docs/DATASHEET_OBST_BENCH.md`](../../docs/DATASHEET_OBST_BENCH.md).

E32 releases a corpus. This directory turns the same bytes into a *benchmark*
anyone can enter: the split is frozen by digest, the submission format is
fixed, and the scorer is a stdlib-only script that ships two reference
baselines whose numbers it reproduces exactly.

**No E32 byte is re-cut.** The benchmark is a *view* over
`observatory/site/src/data/correction_events_release.csv` pinned at
`a27fec9e…faaf` (the E32 release digest). If the working CSV moves, the digest
check fails and a new benchmark version is cut — v1 stays fixed.

## Tasks

| task | rows | input | submission | primary metric |
|---|---|---|---|---|
| `detection` | 3,127 test pairs (6,254 tokens) | `form_a`, `form_b` of one correction event (order frozen by seed, so position carries no signal); no `event_id` | `pair_id<TAB>A\|B\|tie` — which form is the erroneous (pre-correction) one | per-class P/R/F0.5 on the erroneous flag, FPR, Krippendorff's α |
| `location` | 9,729 test rows | edit-op features of one derived event (`op=… / unit=… / dist=… / script=… / edit_space=… / cl=…`) | `row_id<TAB><error_component class>` | accuracy, macro-F1, per-class P/R/F0.5, α |

Both tasks come from the task definitions the published OBS-T baselines
already score (`scripts/obs_t_baselines.py`); this benchmark freezes them so
the numbers are comparable across entrants.

## Split

| file | rows | contents |
|---|---:|---|
| `detection/train.tsv` | 14,670 | form-layer pairs, gold included (`-` marks the 79 identity pairs) — the chronological 70 % head |
| `detection/dev.tsv` | 3,144 | next 15 % — the tuning split; **tune here, never on test** |
| `detection/test.tsv` | 3,127 | last 15 %, inputs only (no `event_id`, no gold); identity pairs (`old == new`, 17) are excluded because they are unscorable |
| `location/train.tsv` | 15,788 | release `split=train` rows, gold included |
| `location/test.tsv` | 9,729 | release `split=test` rows, inputs only (no `event_id`, no gold) |
| `scoring_only/detection_test_gold.tsv` | 3,127 | test gold — **scoring only** |
| `scoring_only/location_test_gold.tsv` | 9,729 | test gold — **scoring only** |
| `SPLITS.json` | — | source pin, split rule, per-file SHA-256 + row counts |

The detection split is chronological over `(date, event_id)` — train on the
past, test on the most recent edits — exactly as in
`scripts/obs_t_baselines.py`. The A/B presentation order is
`sha256("obst-bench-v1" + "|" + event_id)` parity, so the erroneous form is
equally often in column A or B and a position prior scores at chance. The
location split is the release's own `train`/`test` column, unchanged: the
release has no dev split, so the tuning fence for `location` is the frozen
test digest itself, not a separate dev file.

The test split is committed **as inputs + gold digests + a scoring-only gold
copy**: the inputs are public (they are view rows of a CC BY 4.0 release), the
gold lives in `scoring_only/` and every file's SHA-256 is in `SPLITS.json`, so
a leaked, edited or silently re-cut gold is detectable rather than trusted.

Two deliberate non-leaks in the test inputs: the release's `event_id` — a
foreign key into the public `correction_events_release.csv` — is **not**
published on test rows (a one-line join on it would return the gold), and row
ids are prefixed per split (`DTR`/`DDV`/`DTE`, `LTR`/`LTE`) so a bare `D00001`
cannot silently cross-join train onto test.

**Honour code, stated plainly.** Because the corpus itself is public (CC BY
4.0), the gold of any v1 test row is still *derivable* by matching the row
against the release — the two surface forms for `detection`, the
`(date, features)` pair for `location` — no version of a view over a public corpus
can hide it. obst-bench v1 is therefore an *enterable but not sealed*
benchmark: a score is meaningful only under the rule "do not look up the
release (or any of its derivatives) at test time". Submissions that follow the
rule are comparable; one that joins the release gets 1.0 and has measured
nothing. Every published score should say which side of that line it is on.

## Run the scorer

```bash
# 1. write a submission TSV: header `pair_id<TAB>prediction` (or row_id for location)
python scripts/obst_bench.py score --task detection --pred my_predictions.tsv
python scripts/obst_bench.py score --task location  --pred my_locations.tsv --json scores.json

# 2. the two reference baselines (predictions are committed, numbers reproduce)
python scripts/obst_bench.py baselines

# 3. canary: rebuild the split from the pinned release and re-score the baselines
python scripts/obst_bench.py check

# 4. metric arithmetic on fixtures (`--selftest` is accepted too, as in
#    scripts/obs_t_baselines.py)
python scripts/obst_bench.py selftest
```

Every metric carries its denominator in the output JSON. The detection view is
the two-token flagging view of the pairwise decision: a correct pick flags the
erroneous token (TP) and leaves the correct one unflagged (TN); a wrong pick
is FP+FN; a `tie` abstains (FN+TN), and tie tokens carry a missing model label
for α. The confusion matrix always sums to 2n.

## Reference baselines (reproduced on the frozen split)

| baseline | task | numbers |
|---|---|---|
| `b1_charlm_detection` — pairwise character-trigram LM (the published OBS-T pairwise baseline) | detection | P 0.521 · R 0.515 · F0.5 0.519 · FPR 0.474 · α 0.041 · pairwise acc 0.515 |
| `b2_majority_location` — trivial majority/prior classifier | location | accuracy 0.402 (= majority 0.402) · macro-F1 0.096 |

Both were re-run on the frozen v1 split and match the H6388 field metrics
([`reports/obs_t_baselines_field_metrics.md`](../../reports/obs_t_baselines_field_metrics.md))
exactly; the committed prediction files are re-scored by
`obst_bench.py check`. The honest FPR of 0.474 — the baseline flags almost
half of the correct tokens — is the room a leaderboard needs to be entered.

## Contamination caveat — read before quoting a score

**The corpus is mined from the same public git history a model may have
memorised.** Every E32 row is an old→new correction event reconstructed from
committed edits to the CDSL dictionaries (`csl-orig`) — public repositories
with public commit messages, public diffs and public issue threads. A model
trained on GitHub code-before-2026 has plausibly seen the *corrected* side of
these very lines, and some may have seen the correction commit itself. A
benchmark score on this split is therefore **not** a clean generalisation
estimate: it can reward memorisation of the source repositories rather than
annotation-error detection.

Mitigations, none of which fully removes the risk:

* the split is **chronological** (test = the most recent edits), so the test
  window is the least likely part to be inside a fixed cut-off training corpus
  — but a model with a later cut-off is not protected by this;
* the test **inputs** are public while the gold is scoring-only and
  digest-pinned, so a submission cannot be edited after the fact undetected;
* the dev split exists precisely so that tuning never touches test.

Report a score with the caveat: *"obst-bench v1, contamination-exposed
(source repo is public)"*. A temporal-external or held-out-source evaluation
is future work, not a property of v1.

## Reproduction

```bash
python scripts/obst_bench.py build      # rewrites obst-bench/v1/** from the pinned E32 CSV
python scripts/obst_bench.py check      # rebuild in a scratch dir, compare digests, re-score baselines
```

`build` refuses to run if the working CSV no longer matches the E32 digest.
Rebuild output is byte-identical (LF newlines, fixed row order, hashes only in
`SPLITS.json` — no timestamps beyond the freeze date).

## License and citation

Data: **CC BY 4.0** ([`DATA_LICENSE.md`](../../DATA_LICENSE.md)) — the same
terms as the E32 release; the benchmark adds no new data, only a view.
Code (`scripts/obst_bench.py`): **GPL-3.0** ([`LICENSE`](../../LICENSE)).
Attribute the CDSL / sanskrit-lexicon community and the OBS-T correction-event
corpus, and cite the release DOI
[10.5281/zenodo.21346705](https://doi.org/10.5281/zenodo.21346705).

## Note for the A73 ISCLS-9 submission

The submission should point at this benchmark, not propose a new experiment:
*the CDSL correction-event corpus (E32) ships with obst-bench v1 — a frozen,
digest-pinned test split, a documented prediction format and a scorer whose
two reference baselines reproduce the reported field metrics, so the resource
can be entered and compared rather than only described.* One sentence, one
link to `obst-bench/v1/`, and the honest FPR of 0.474 stated as the headroom.
The benchmark is a pinned view over the already-cut release; it re-cuts
nothing and adds no experiment the paper has to defend.

_Dr. Mārcis Gasūns_
