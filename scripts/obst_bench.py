#!/usr/bin/env python3
"""obst-bench v1 — a frozen, enterable benchmark view over the E32 release.

E32 (``correction_events_release.csv``, SHA-256 pinned) is a *corpus*: it is
released, citable and described. This script turns it into a *benchmark* — a
fixed train/dev/test view over the same bytes, a documented submission format
and a scorer a third party can run without touching the release:

    build      write the frozen split files + ``obst-bench/v1/SPLITS.json``
               (digests of every emitted file, source pin, split rule)
    baselines  re-run the two reference baselines on the frozen split and
               write their prediction files + score JSONs
    score      score a submission TSV against the frozen gold
    check      canary: re-derive the splits from the pinned release and
               re-score the committed baselines, byte-for-byte
    selftest   metric-arithmetic fixtures (exit 0 == green)

Subcommands and data layout are documented in ``obst-bench/v1/README.md``.

Tasks (both are views over rows of the E32 release — no row is invented and
no release byte is re-cut):

* ``detection`` — minimal-pair ranking, form layer. One test row = two surface
  forms (``form_a``, ``form_b``) of one correction event; the submission says
  which one is the erroneous (pre-correction) form. This is the H6388
  pairwise/char-LM task: per-class P/R/F0.5 over the two-token flagging view,
  FPR of the erroneous flag, Krippendorff's alpha (nominal) gold vs model.
* ``location`` — microstructure location classification. One test row = one
  derived event with its edit-op features; the submission names the
  ``error_component`` class.

Reuse: token filter, char-trigram LM, chronological split, Krippendorff's
alpha and Cohen's kappa are imported from ``scripts/obs_t_baselines.py``
(their definitions are what the published E32 numbers were computed with —
a re-implementation would be a second source of truth).
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import sys
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import obs_t_baselines as otb  # noqa: E402  (path insert above)

csv.field_size_limit(10_000_000)

VERSION = 'v1'
SEED = 'obst-bench-v1'
SRC_CSV = os.path.join(ROOT, 'observatory', 'site', 'src', 'data',
                       'correction_events_release.csv')
BENCH = os.path.join(ROOT, 'obst-bench', VERSION)
SITE_JSON = os.path.join(ROOT, 'observatory', 'site', 'src', 'data',
                         'obst_bench_v1.json')

# Full SHA-256 of the E32 release of record (10-10-2026). The benchmark is a
# view over exactly these bytes; a different digest means the working CSV has
# moved on and the split must not silently follow it.
E32_PIN = 'a27fec9e6a5b0a4d641d8c95078823c8606f8d5c31a85b88e5196a50abccfaaf'

DET_COLS = ['pair_id', 'event_id', 'date', 'form_a', 'form_b']
# Test inputs carry no event_id: it is a foreign key into the public E32
# CSV and would hand any reader the gold by one lookup (H7124 verifier).
DET_TEST_COLS = ['pair_id', 'date', 'form_a', 'form_b']
LOC_COLS = ['row_id', 'event_id', 'date', 'features']
LOC_TEST_COLS = ['row_id', 'date', 'features']
TASKS = ('detection', 'location')


class BenchError(SystemExit):
    """A scoring/verification failure (exit code 1, message on stderr)."""


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(1 << 20), b''):
            h.update(chunk)
    return h.hexdigest()


def true_digest(path):
    """sha256 of a text artifact as the repo stores it: git normalises CRLF
    to LF on checkout, so hash the LF-normalised bytes or the digest is
    platform-dependent (Windows checkout vs Linux CI)."""
    with open(path, 'rb') as f:
        return hashlib.sha256(f.read().replace(b'\r\n', b'\n')).hexdigest()


def write_tsv(path, cols, rows):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8', newline='\n') as f:
        w = csv.writer(f, delimiter='\t', lineterminator='\n')
        w.writerow(cols)
        w.writerows(rows)
    return len(rows)


def read_tsv(path):
    with open(path, encoding='utf-8', newline='') as f:
        return list(csv.DictReader(f, delimiter='\t'))


# ------------------------------------------------------------------ split view
def load_release():
    with open(SRC_CSV, encoding='utf-8') as f:
        return list(csv.DictReader(f))


def form_rows(rows):
    """The form-layer population, filtered exactly as scripts/obs_t_baselines.py
    does (its docstring defines the published detection numbers)."""
    return [r for r in rows
            if r['source_layer'] == 'form'
            and otb.is_token(r['old_iast']) and otb.is_token(r['new_iast'])]


def loc_rows(rows):
    """The location-classification population, filtered exactly as
    obs_t_baselines.classify() does."""
    return [r for r in rows
            if r['evidence_level'] == 'derived'
            and r['error_component'] != 'unknown'
            and r['split'] in ('train', 'test')]


def side_order(event_id):
    """Frozen A/B presentation order. Deterministic on (seed, event_id) so the
    position of the erroneous form carries no signal and every rebuild is
    byte-identical."""
    h = hashlib.sha256(f'{SEED}|{event_id}'.encode()).hexdigest()
    return int(h[:8], 16) % 2 == 0  # True -> old form is form_a


def pair_fields(rid, r):
    """One detection row as a field dict; the caller writes only the columns its
    split publishes (test inputs omit `event_id`, see DET_TEST_COLS)."""
    old, new = r['old_iast'].strip(), r['new_iast'].strip()
    a_first = side_order(r['event_id'])
    form_a, form_b = (old, new) if a_first else (new, old)
    # '-' = identity pair (old == new): uninformative, kept in train/dev only
    gold = ('A' if a_first else 'B') if old != new else '-'
    return {'pair_id': rid, 'event_id': r['event_id'], 'date': r['date'],
            'form_a': form_a, 'form_b': form_b, 'gold': gold}


def build(out_dir=None):
    bench = out_dir or BENCH
    rows = load_release()
    got = sha256_file(SRC_CSV)
    if got != E32_PIN:
        raise BenchError(f'source release digest mismatch: {got} != {E32_PIN} '
                         f'— the working CSV moved; cut a new benchmark version '
                         f'instead of re-freezing v1')
    files, counts = {}, {}

    # ---- detection: chronological 70/15/15 over the form layer (the published
    # split); the test file carries only scorable pairs (old != new).
    form = form_rows(rows)
    train, dev, test = otb.chrono_split(form)
    scorable_test = [r for r in test if r['old_iast'].strip() != r['new_iast'].strip()]
    # ids are prefixed per split (DTR/DDV/DTE, LTR/LTE): a bare D00001 repeats in
    # every file and would let an entrant silently cross-join train onto test.
    det_specs = [
        ('detection/train.tsv', train, True, 'DTR'),
        ('detection/dev.tsv', dev, True, 'DDV'),
        ('detection/test.tsv', scorable_test, False, 'DTE'),
    ]
    for rel, rs, with_gold, prefix in det_specs:
        cols = DET_COLS if with_gold else DET_TEST_COLS
        if with_gold:
            cols = cols + ['gold']
        out = []
        for i, r in enumerate(rs, 1):
            f = pair_fields(f'{prefix}{i:05d}', r)
            out.append([f[c] for c in cols])
        path = os.path.join(bench, rel)
        counts[rel] = write_tsv(path, cols, out)
        files[rel] = {'sha256': true_digest(path), 'rows': counts[rel],
                      'bytes': os.path.getsize(path)}
    gold_rows = [[f'DTE{i:05d}', pair_fields(f'DTE{i:05d}', r)['gold']]
                 for i, r in enumerate(scorable_test, 1)]
    path = os.path.join(bench, 'scoring_only', 'detection_test_gold.tsv')
    counts['scoring_only/detection_test_gold.tsv'] = write_tsv(path, ['pair_id', 'gold'], gold_rows)
    files['scoring_only/detection_test_gold.tsv'] = {
        'sha256': true_digest(path), 'rows': len(gold_rows), 'bytes': os.path.getsize(path)}

    # ---- location: the release's own train/test split (no dev split exists in
    # the release; the tuning fence is the frozen test digest, see README).
    loc = loc_rows(rows)
    loc_train = [r for r in loc if r['split'] == 'train']
    loc_test = [r for r in loc if r['split'] == 'test']
    for rel, rs, with_gold, prefix in (('location/train.tsv', loc_train, True, 'LTR'),
                                       ('location/test.tsv', loc_test, False, 'LTE')):
        out = []
        cols = LOC_COLS if with_gold else LOC_TEST_COLS
        for i, r in enumerate(rs, 1):
            row = [f'{prefix}{i:05d}']
            if with_gold:                     # traceability stays on train only
                row.append(r['event_id'])
            row += [r['date'], '|'.join(otb.feats(r))]
            if with_gold:
                row.append(r['error_component'])
            out.append(row)
        path = os.path.join(bench, rel)
        counts[rel] = write_tsv(path, cols + (['gold'] if with_gold else []), out)
        files[rel] = {'sha256': true_digest(path), 'rows': counts[rel],
                      'bytes': os.path.getsize(path)}
    path = os.path.join(bench, 'scoring_only', 'location_test_gold.tsv')
    gold_rows = [[f'LTE{i:05d}', r['error_component']] for i, r in enumerate(loc_test, 1)]
    counts['scoring_only/location_test_gold.tsv'] = write_tsv(path, ['row_id', 'gold'], gold_rows)
    files['scoring_only/location_test_gold.tsv'] = {
        'sha256': true_digest(path), 'rows': len(gold_rows), 'bytes': os.path.getsize(path)}

    manifest = {
        'benchmark': 'obst-bench',
        'version': VERSION,
        'frozen_at': '24-10-2026',
        'source_release': {
            'path': 'observatory/site/src/data/correction_events_release.csv',
            'sha256': E32_PIN,
            'release': 'e32-correction-events-release-2026-10-10',
            'rows': len(rows),
        },
        'seed': SEED,
        'split_rule': {
            'detection': ('form layer (source_layer=form, both sides single '
                          'tokens); chronological 70/15/15 over (date, '
                          'event_id) as in scripts/obs_t_baselines.py; A/B '
                          'presentation order = sha256(seed|event_id) parity; '
                          'test rows are the scorable pairs (old != new)'),
            'location': ("release 'split' column unchanged (train/test); "
                         'evidence_level=derived and error_component != '
                         'unknown, as in obs_t_baselines.classify()'),
        },
        'counts': {k: counts[k] for k in sorted(counts)},
        'files': {k: files[k] for k in sorted(files)},
    }
    path = os.path.join(bench, 'SPLITS.json')
    with open(path, 'w', encoding='utf-8', newline='\n') as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2, sort_keys=False)
        f.write('\n')
    print(f'wrote {os.path.relpath(path, ROOT) if out_dir is None else path}')
    for k in sorted(files):
        print(f'  {k:44s} {files[k]["rows"]:6d} rows  {files[k]["sha256"][:12]}')
    return manifest


# ---------------------------------------------------------------------- scoring
def _prf(tp, fp, fn, beta2=0.25):
    p = tp / (tp + fp) if tp + fp else 0.0
    r = tp / (tp + fn) if tp + fn else 0.0
    f = ((1 + beta2) * p * r) / (beta2 * p + r) if (beta2 * p + r) else 0.0
    return p, r, f


def load_predictions(path, id_col, valid):
    preds = {}
    for r in read_tsv(path):
        rid = r[id_col]
        if rid in preds:
            raise BenchError(f'{path}: duplicate id {rid}')
        val = r['prediction'].strip()
        if valid is not None and val not in valid:
            raise BenchError(f'{path}: {rid} has prediction {val!r}, '
                             f'expected one of {sorted(valid)}')
        preds[rid] = val
    if not preds:
        raise BenchError(f'{path}: no predictions')
    return preds


def _align(gold, preds, name):
    if set(gold) != set(preds):
        missing = sorted(set(gold) - set(preds))[:5]
        extra = sorted(set(preds) - set(gold))[:5]
        raise BenchError(f'{name}: submission does not match the frozen test '
                         f'set (missing {len(set(gold) - set(preds))}: '
                         f'{missing}; unknown {len(set(preds) - set(gold))}: '
                         f'{extra})')


def score_detection(preds, gold, name='detection'):
    """Score predictions against the frozen detection gold.

    Predictions are per pair: ``A``/``B`` (which form is the erroneous one) or
    ``tie`` (abstain). Metrics are read off the two-token flagging view of the
    same decision, exactly as H6388 defines it: a correct pick flags the
    erroneous token (TP) and leaves the correct one unflagged (TN); a wrong
    pick is FP+FN; a tie is FN+TN. Confusion always sums to 2n.
    """
    _align(gold, preds, name)
    tp = fp = fn = tn = correct = ties = 0
    units = []
    for rid, g in gold.items():
        p = preds[rid]
        gold_flags = ('erroneous', 'correct') if g == 'A' else ('correct', 'erroneous')
        if p == 'tie':
            ties += 1
            pred_flags = (None, None)
            fn += 1
            tn += 1
        else:
            pred_flags = ('erroneous', 'correct') if p == 'A' else ('correct', 'erroneous')
            if p == g:
                correct += 1
                tp += 1
                tn += 1
            else:
                fp += 1
                fn += 1
        units.append((gold_flags[0], pred_flags[0]))
        units.append((gold_flags[1], pred_flags[1]))
    n = len(gold)
    if tp + fp + fn + tn != 2 * n:            # H6388 gate: the confusion is 2n
        raise BenchError(f'confusion {tp + fp + fn + tn} does not sum to 2n={2 * n}')
    per_class = {}
    for cls, a, b, c in (('erroneous', tp, fp, fn), ('correct', tn, fn, fp)):
        p_, r_, f_ = _prf(a, b, c)
        per_class[cls] = {
            'precision': round(p_, 3), 'recall': round(r_, 3), 'f0_5': round(f_, 3),
            'precision_denominator': f'all flagged tokens (tp+fp={a + b:,})',
            'recall_denominator': f'all gold-{cls} tokens (tp+fn={a + c:,})',
        }
    fpr = fp / (fp + tn) if fp + tn else 0.0
    non_tie = [(g, m) for g, m in units if m is not None]
    alpha = otb.krippendorff_alpha_nominal(units)
    kappa = otb.cohen_kappa(non_tie)
    return {
        'task': 'detection',
        'test_pairs': n,
        'test_tokens': 2 * n,
        'pairwise_accuracy': round(correct / n, 3) if n else 0.0,
        'tie_pairs': ties,
        'tie_rate': round(ties / n, 3) if n else 0.0,
        'flagging_confusion': {'tp': tp, 'fp': fp, 'fn': fn, 'tn': tn},
        'per_class': per_class,
        'fpr_erroneous_flag': round(fpr, 3),
        'fpr_denominator': f'all gold-correct tokens (fp+tn={fp + tn:,})',
        'krippendorff_alpha_nominal': round(alpha, 3) if alpha is not None else None,
        'krippendorff_alpha_pairable_values': 2 * n - 2 * ties,
        'cohen_kappa_non_tie': round(kappa, 3) if kappa is not None else None,
        'cohen_kappa_units': len(non_tie),
    }


def score_location(preds, gold, train_gold=None, name='location'):
    _align(gold, preds, name)
    n = len(gold)
    correct = sum(1 for rid, g in gold.items() if preds[rid] == g)
    per = {}
    for rid, g in gold.items():
        p = preds[rid]
        per.setdefault(g, [0, 0, 0])[0 if p == g else 2] += 1
        if p != g:
            per.setdefault(p, [0, 0, 0])[1] += 1
    per_class, f1s = {}, []
    for cls in sorted(per):
        a, b, c = per[cls]
        p_, r_, f_ = _prf(a, b, c)
        f1s.append(2 * p_ * r_ / (p_ + r_) if p_ + r_ else 0.0)
        per_class[cls] = {
            'precision': round(p_, 3), 'recall': round(r_, 3), 'f0_5': round(f_, 3),
            'support': sum(1 for g in gold.values() if g == cls),
            'precision_denominator': f'all predicted {cls} (tp+fp={a + b:,})',
            'recall_denominator': f'all gold {cls} (tp+fn={a + c:,})',
        }
    labels = sorted(set(gold.values()) | set(preds.values()))
    units = [(g, preds[rid]) for rid, g in gold.items()]
    alpha = otb.krippendorff_alpha_nominal(units)
    kappa = otb.cohen_kappa(units)
    out = {
        'task': 'location',
        'test_rows': n,
        'accuracy': round(correct / n, 3) if n else 0.0,
        'macro_f1': round(sum(f1s) / len(f1s), 3) if f1s else 0.0,
        'classes': len(labels),
        'per_class': per_class,
        'krippendorff_alpha_nominal': round(alpha, 3) if alpha is not None else None,
        'krippendorff_alpha_pairable_values': n,
        'cohen_kappa': round(kappa, 3) if kappa is not None else None,
        'agreement_denominator': f'all test rows, gold vs prediction (n={n:,})',
    }
    if train_gold:
        maj = Counter(train_gold).most_common(1)[0][0]
        maj_correct = sum(1 for g in gold.values() if g == maj)
        out['train_majority_class'] = maj
        out['majority_baseline_accuracy'] = round(maj_correct / n, 3) if n else 0.0
    return out


def read_gold(task):
    rel = {'detection': ('scoring_only/detection_test_gold.tsv', 'pair_id'),
           'location': ('scoring_only/location_test_gold.tsv', 'row_id')}[task]
    return {r[rel[1]]: r['gold'] for r in read_tsv(os.path.join(BENCH, rel[0]))}


def read_train_labels():
    return [r['gold'] for r in read_tsv(os.path.join(BENCH, 'location', 'train.tsv'))]


def cmd_score(args):
    gold = read_gold(args.task)
    if args.task == 'location':
        valid = set(read_train_labels()) | set(gold.values())
    else:
        valid = {'A', 'B', 'tie'}
    preds = load_predictions(args.pred, 'pair_id' if args.task == 'detection' else 'row_id',
                             valid)
    if args.task == 'location':
        metrics = score_location(preds, gold, read_train_labels())
    else:
        metrics = score_detection(preds, gold)
    text = json.dumps(metrics, ensure_ascii=False, indent=2)
    if args.json:
        with open(args.json, 'w', encoding='utf-8', newline='\n') as f:
            f.write(text + '\n')
        print(f'wrote {args.json}')
    print(text)
    return metrics


# -------------------------------------------------------------------- baselines
def correct_forms(train_rows):
    return [r['form_b'] if r['gold'] == 'A' else r['form_a'] for r in train_rows]


def cmd_baselines(args):
    # B1 — pairwise character-trigram LM (the published OBS-T pairwise baseline).
    det_train = read_tsv(os.path.join(BENCH, 'detection', 'train.tsv'))
    det_test = read_tsv(os.path.join(BENCH, 'detection', 'test.tsv'))
    score_fn, _ = otb.build_charlm(correct_forms(det_train))
    b1 = {}
    for r in det_test:
        sa, sb = score_fn(r['form_a']), score_fn(r['form_b'])
        if sa == sb:
            label = 'tie'
        elif sa < sb:                    # a is less likely than b -> a is erroneous
            label = 'A'
        else:
            label = 'B'
        b1[r['pair_id']] = label
    write_tsv(os.path.join(BENCH, 'baselines', 'b1_charlm_detection.predictions.tsv'),
              ['pair_id', 'prediction'], sorted(b1.items()))

    # B2 — trivial majority/prior classifier on location.
    loc_train = read_tsv(os.path.join(BENCH, 'location', 'train.tsv'))
    loc_test = read_tsv(os.path.join(BENCH, 'location', 'test.tsv'))
    maj = Counter(r['gold'] for r in loc_train).most_common(1)[0][0]
    b2 = {r['row_id']: maj for r in loc_test}
    write_tsv(os.path.join(BENCH, 'baselines', 'b2_majority_location.predictions.tsv'),
              ['row_id', 'prediction'], sorted(b2.items()))

    m1 = score_detection(b1, read_gold('detection'))
    m2 = score_location(b2, read_gold('location'),
                        [r['gold'] for r in loc_train])
    for rel, metrics in (('baselines/b1_charlm_detection.scores.json', m1),
                         ('baselines/b2_majority_location.scores.json', m2)):
        path = os.path.join(BENCH, rel)
        with open(path, 'w', encoding='utf-8', newline='\n') as f:
            f.write(json.dumps(metrics, ensure_ascii=False, indent=2) + '\n')
        print(f'wrote {rel}')

    # Site-visible summary (the /data page row points here).
    manifest = json.load(open(os.path.join(BENCH, 'SPLITS.json'), encoding='utf-8'))
    site = {
        'benchmark': 'obst-bench',
        'version': VERSION,
        'frozen_at': manifest['frozen_at'],
        'source_release': manifest['source_release'],
        'split_digests': {k: v['sha256'] for k, v in manifest['files'].items()},
        'counts': manifest['counts'],
        'baselines': {
            'b1_charlm_detection': {
                'description': 'pairwise char-trigram LM (the published OBS-T '
                               'pairwise baseline)',
                'predictions': 'obst-bench/v1/baselines/b1_charlm_detection.predictions.tsv',
                'numbers': m1},
            'b2_majority_location': {
                'description': 'trivial majority/prior classifier on location',
                'predictions': 'obst-bench/v1/baselines/b2_majority_location.predictions.tsv',
                'numbers': m2},
        },
        'scorer': 'scripts/obst_bench.py',
        'submission_format': 'pair_id<TAB>A|B|tie (detection); '
                             'row_id<TAB>error_component (location)',
    }
    with open(SITE_JSON, 'w', encoding='utf-8', newline='\n') as f:
        f.write(json.dumps(site, ensure_ascii=False, indent=2) + '\n')
    print(f'wrote {os.path.relpath(SITE_JSON, ROOT)}')
    print(f"  B1 detection  P {m1['per_class']['erroneous']['precision']} / "
          f"R {m1['per_class']['erroneous']['recall']} / "
          f"F0.5 {m1['per_class']['erroneous']['f0_5']} / "
          f"FPR {m1['fpr_erroneous_flag']} / alpha {m1['krippendorff_alpha_nominal']}")
    print(f"  B2 location   accuracy {m2['accuracy']} "
          f"(majority {m2['majority_baseline_accuracy']}) macro-F1 {m2['macro_f1']}")
    return 0


# ------------------------------------------------------------------------ check
def cmd_check(args):
    """Canary: rebuild the splits into a scratch dir and compare every digest
    with the committed manifest, then re-score the committed baseline
    prediction files and compare with the committed score JSONs."""
    ok = True
    committed = json.load(open(os.path.join(BENCH, 'SPLITS.json'), encoding='utf-8'))
    for rel, meta in sorted(committed['files'].items()):
        path = os.path.join(BENCH, rel)
        if not os.path.exists(path):
            print(f'FAIL missing {rel}')
            ok = False
            continue
        got = true_digest(path)
        if got != meta['sha256']:
            ok = False
            print(f'FAIL digest {rel}: {got[:12]} != {meta["sha256"][:12]}')
        else:
            print(f'OK digest {rel} {got[:12]}')
    got_src = sha256_file(SRC_CSV)
    if got_src != committed['source_release']['sha256']:
        ok = False
        print(f'FAIL source release digest {got_src[:12]} — the working CSV '
              f'moved since the freeze; cut a new benchmark version')
    else:
        print('OK source release digest (E32 pin)')

    import tempfile
    rebuild_ok = True
    with tempfile.TemporaryDirectory() as tmp:
        rebuilt = os.path.join(tmp, 'v1')
        build(out_dir=rebuilt)
        for rel, meta in sorted(committed['files'].items()):
            got = true_digest(os.path.join(rebuilt, rel))
            if got != meta['sha256']:
                rebuild_ok = False
                ok = False
                print(f'FAIL rebuild {rel}: {got[:12]} != {meta["sha256"][:12]}')
        if rebuild_ok:
            print('OK rebuild reproduces every split digest')

    for rel, task in (('baselines/b1_charlm_detection.scores.json', 'detection'),
                      ('baselines/b2_majority_location.scores.json', 'location')):
        path = os.path.join(BENCH, rel)
        committed_scores = json.load(open(path, encoding='utf-8'))
        pred_rel = rel.replace('.scores.json', '.predictions.tsv')
        preds = load_predictions(os.path.join(BENCH, pred_rel),
                                 'pair_id' if task == 'detection' else 'row_id',
                                 {'A', 'B', 'tie'} if task == 'detection' else None)
        gold = read_gold(task)
        fresh = (score_detection(preds, gold) if task == 'detection'
                 else score_location(preds, gold, read_train_labels()))
        if fresh == committed_scores:
            print(f'OK rescore {pred_rel} reproduces the committed numbers')
        else:
            ok = False
            print(f'FAIL rescore {pred_rel} drifted from the committed JSON')
    if not ok:
        raise BenchError('obst-bench v1 check FAILED')
    print('ALL PASS — obst-bench v1 digests + baseline numbers reproduce')
    return 0


# --------------------------------------------------------------------- selftest
def selftest():
    """Metric-arithmetic fixtures. Exit 0 == every assertion holds."""
    checks = []

    def eq(name, got, want):
        ok = got == want
        checks.append((name, ok, got, want))

    # 1. Perfect detection: P = R = F0.5 = 1, FPR = 0, alpha = 1.
    gold = {'p1': 'A', 'p2': 'B', 'p3': 'A'}
    perfect = dict(gold)
    m = score_detection(perfect, gold)
    eq('perfect precision', m['per_class']['erroneous']['precision'], 1.0)
    eq('perfect recall', m['per_class']['erroneous']['recall'], 1.0)
    eq('perfect f0.5', m['per_class']['erroneous']['f0_5'], 1.0)
    eq('perfect fpr', m['fpr_erroneous_flag'], 0.0)
    eq('perfect pairwise acc', m['pairwise_accuracy'], 1.0)
    eq('perfect alpha', m['krippendorff_alpha_nominal'], 1.0)
    eq('perfect confusion sums to 2n', sum(m['flagging_confusion'].values()), 6)

    # 2. Hand-computed mixed confusion: 2 right, 1 wrong over 3 pairs.
    m = score_detection({'p1': 'B', 'p2': 'B', 'p3': 'A'}, gold)
    eq('mixed confusion', m['flagging_confusion'],
       {'tp': 2, 'fp': 1, 'fn': 1, 'tn': 2})
    eq('mixed precision', m['per_class']['erroneous']['precision'], 0.667)
    eq('mixed recall', m['per_class']['erroneous']['recall'], 0.667)
    eq('mixed fpr', m['fpr_erroneous_flag'], 0.333)
    eq('mixed pairwise acc', m['pairwise_accuracy'], 0.667)

    # 3. Full abstention: nothing flagged, nothing pairable, alpha undefined.
    m = score_detection(dict.fromkeys(gold, 'tie'), gold)
    eq('abstain confusion', m['flagging_confusion'],
       {'tp': 0, 'fp': 0, 'fn': 3, 'tn': 3})
    eq('abstain precision', m['per_class']['erroneous']['precision'], 0.0)
    eq('abstain fpr', m['fpr_erroneous_flag'], 0.0)
    eq('abstain tie rate', m['tie_rate'], 1.0)
    eq('abstain alpha undefined', m['krippendorff_alpha_nominal'], None)

    # 4. Submission alignment: a missing / unknown id is an error, not a zero.
    for bad, why in (({'p1': 'A', 'p2': 'B'}, 'missing'),
                     ({'p1': 'A', 'p2': 'B', 'p3': 'A', 'p9': 'A'}, 'unknown')):
        try:
            score_detection(bad, gold)
            checks.append((f'{why} id rejected', False, 'no error', 'BenchError'))
        except BenchError:
            checks.append((f'{why} id rejected', True, '', ''))

    # 5. Location: perfect predictions, macro-F1 over both classes, majority
    #    baseline read off the frozen train labels.
    loc_gold = {'r1': 'sense', 'r2': 'sense', 'r3': 'markup'}
    m = score_location(dict(loc_gold), loc_gold, ['sense', 'sense', 'markup'])
    eq('location accuracy', m['accuracy'], 1.0)
    eq('location macro f1', m['macro_f1'], 1.0)
    eq('location alpha', m['krippendorff_alpha_nominal'], 1.0)
    eq('location majority baseline', m['majority_baseline_accuracy'], 0.667)

    m = score_location({'r1': 'markup', 'r2': 'markup', 'r3': 'markup'},
                       loc_gold, ['sense', 'sense', 'markup'])
    eq('majority-only accuracy', m['accuracy'], 0.333)
    eq('majority-only per-class recall', m['per_class']['markup']['recall'], 1.0)

    # 6. Alpha/kappa primitives on a known-agreement pair.
    eq('alpha identical raters', round(otb.krippendorff_alpha_nominal(
        [('x', 'x'), ('y', 'y'), ('x', 'x')]), 3), 1.0)
    eq('kappa identical raters', round(otb.cohen_kappa([('x', 'x'), ('y', 'y')]), 3), 1.0)
    eq('kappa single disagreement', round(otb.cohen_kappa([('x', 'y')]), 3), 0.0)

    failed = [c for c in checks if not c[1]]
    for name, ok, got, want in checks:
        print(f"{'PASS' if ok else 'FAIL'} {name}"
              + ('' if ok else f' — got {got!r}, want {want!r}'))
    print(f'{len(checks) - len(failed)}/{len(checks)} checks passed')
    if failed:
        raise BenchError(f'{len(failed)} selftest check(s) failed')
    return 0


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    # The handoff contract and the repo convention both spell this `--selftest`
    # (scripts/obs_t_baselines.py --selftest); accept it as a flag as well as a
    # subcommand so the documented command cannot silently become an argparse
    # error.
    if '--selftest' in argv:
        argv = [a for a in argv if a != '--selftest'] or ['selftest']
    ap = argparse.ArgumentParser(
        prog='obst_bench.py', description='obst-bench v1 build/score/canary')
    sub = ap.add_subparsers(dest='cmd', required=True)

    p = sub.add_parser('build', help='freeze the split files + digest manifest')
    p.set_defaults(func=lambda a: build())

    p = sub.add_parser('baselines', help='re-run the two reference baselines')
    p.set_defaults(func=cmd_baselines)

    p = sub.add_parser('score', help='score a submission TSV')
    p.add_argument('--task', required=True, choices=TASKS)
    p.add_argument('--pred', required=True, help='submission TSV')
    p.add_argument('--json', help='also write the metrics JSON here')
    p.set_defaults(func=cmd_score)

    p = sub.add_parser('check', help='canary: digests + committed baseline numbers')
    p.set_defaults(func=cmd_check)

    p = sub.add_parser('selftest', help='metric-arithmetic fixtures')
    p.set_defaults(func=lambda a: selftest())

    args = ap.parse_args(argv)
    res = args.func(args)
    return res if isinstance(res, int) else 0


if __name__ == '__main__':
    sys.exit(main())
