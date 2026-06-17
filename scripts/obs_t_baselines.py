#!/usr/bin/env python3
"""OBS-T Phase 6b — reproducible baselines for the error corpus.

Three stdlib-only, deterministic baselines that define the tasks the released
resource supports and give non-trivial reference scores for the paper:

1. **Error detection** (form layer) — is a token erroneous? A character-trigram
   language model trained on the *correct* (new) forms; flag low-likelihood
   tokens. Threshold tuned on dev, reported on test. P/R/F1/accuracy.
2. **Error correction** (form layer) — propose the correct form of an erroneous
   token by nearest training-lexicon neighbour (edit distance, length+initial
   blocking). Accuracy@1.
3. **Location classification** (all derived events) — predict the microstructure
   `error_component` from edit-op features with a categorical Naive Bayes.
   Accuracy + macro-F1 vs the majority-class baseline.

Detection/correction use clean single-word IAST pairs from the FORM layer with a
within-form temporal split (train <=2016, dev 2017, test >=2018), since the form
era is 2014-2019. The classifier uses the global release split.

Input : observatory/site/src/data/correction_events_release.csv  (needs `split`)
Output: reports/obs_t_baselines.md
        observatory/site/src/data/obs_t_baselines.json

Usage:  python scripts/obs_t_baselines.py
"""
import csv, json, math, os, sys
from collections import Counter, defaultdict
from datetime import datetime, timezone
sys.stdout.reconfigure(encoding='utf-8'); sys.stderr.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DATA = os.path.join(ROOT, 'observatory', 'site', 'src', 'data')
IN_CSV = os.path.join(DATA, 'correction_events_release.csv')
OUT_JSON = os.path.join(DATA, 'obs_t_baselines.json')
OUT_MD = os.path.join(ROOT, 'reports', 'obs_t_baselines.md')
csv.field_size_limit(10_000_000)


# ---------------------------------------------------------------- shared utils
def is_token(s):
    s = s.strip()
    return s and ' ' not in s and len(s) >= 2 and any(c.isalpha() for c in s)


def levenshtein(a, b, cap=3):
    la, lb = len(a), len(b)
    if abs(la - lb) > cap:
        return cap + 1
    prev = list(range(lb + 1))
    for i in range(1, la + 1):
        cur = [i] + [0] * lb
        best = cur[0]
        for j in range(1, lb + 1):
            cost = 0 if a[i - 1] == b[j - 1] else 1
            cur[j] = min(prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + cost)
            best = min(best, cur[j])
        if best > cap:
            return cap + 1
        prev = cur
    return prev[lb]


def form_year(r):
    return int(r['date'][:4]) if r['date'] else 0


def chrono_split(rows, train_frac=0.7, dev_frac=0.15):
    """Chronological 70/15/15 split. The form era is concentrated in 2015-2016, so
    a calendar-year cutoff leaves a tiny tail; a percentile-by-date split keeps the
    train-before-test ordering while giving a substantial test set."""
    rows = sorted(rows, key=lambda r: (r['date'], r['event_id']))
    n = len(rows)
    a, b = int(n * train_frac), int(n * (train_frac + dev_frac))
    return rows[:a], rows[a:b], rows[b:]


# ----------------------------------------------------------- shared char-LM
def trigrams(tok):
    t = '^^' + tok + '$$'
    return [t[i:i + 3] for i in range(len(t) - 2)]


def build_charlm(tokens):
    """Character-trigram LM over correct forms. Returns (score, alphabet)."""
    counts = Counter()
    alphabet = set()
    for tok in tokens:
        alphabet.update(tok)
        for g in trigrams(tok):
            counts[g] += 1
    V = len(counts) or 1
    total = sum(counts.values()) or 1

    def score(tok):
        gs = trigrams(tok)
        return sum(math.log((counts.get(g, 0) + 1) / (total + V)) for g in gs) / len(gs)
    return score, alphabet


# --------------------------------------------------------------- 1. detection
def detection(form_rows):
    """Minimal-pair ranking: does the char-LM assign higher likelihood to the
    corrected form than to the erroneous one? Chance = 0.5. (An absolute-threshold
    classifier is uninformative here because old/new differ by a single character.)"""
    train, _dev, test = chrono_split(form_rows)
    score, _ = build_charlm([r['new_iast'].strip() for r in train])
    n = correct = ties = 0
    for r in test:
        old, new = r['old_iast'].strip(), r['new_iast'].strip()
        if not (is_token(old) and is_token(new)) or old == new:
            continue
        n += 1
        so, sn = score(old), score(new)
        if sn > so:
            correct += 1
        elif sn == so:
            ties += 1
    return {'train_tokens': len(train), 'test_pairs': n,
            'pairwise_accuracy': round(correct / n, 3) if n else 0,
            'tie_rate': round(ties / n, 3) if n else 0}


# -------------------------------------------------------------- 2. correction
def edits1(word, alphabet):
    """All strings at edit distance 1 (Norvig): delete/transpose/replace/insert."""
    splits = [(word[:i], word[i:]) for i in range(len(word) + 1)]
    out = set()
    for L, R in splits:
        if R:
            out.add(L + R[1:])                       # delete
            if len(R) > 1:
                out.add(L + R[1] + R[0] + R[2:])     # transpose
            for c in alphabet:
                out.add(L + c + R[1:])               # replace
        for c in alphabet:
            out.add(L + c + R)                       # insert
    out.discard(word)
    return out


def correction(form_rows):
    """Noisy-channel baseline: for an erroneous token, pick the edit-1 candidate the
    char-LM scores highest (Norvig-style). Open-vocabulary — no lexicon recurrence
    required, unlike a nearest-neighbour lookup (which scores ~0 on Sanskrit)."""
    train_, dev_, test = chrono_split(form_rows)
    train = train_ + dev_
    score, alphabet = build_charlm([r['new_iast'].strip() for r in train])
    lex = {r['new_iast'].strip() for r in train if is_token(r['new_iast'].strip())}

    def propose(tok):
        cands = [c for c in edits1(tok, alphabet) if c]
        if not cands:
            return None
        # prefer candidates in the training lexicon; else best LM score
        known = [c for c in cands if c in lex]
        pool = known or cands
        return max(pool, key=score)

    n = hit = d1 = 0
    for r in test:
        old, new = r['old_iast'].strip(), r['new_iast'].strip()
        if not (is_token(old) and is_token(new)) or old == new:
            continue
        n += 1
        if levenshtein(old, new, cap=2) == 1:
            d1 += 1
        if propose(old) == new:
            hit += 1
    return {'train_lexicon': len(lex), 'test_pairs': n,
            'accuracy_at_1': round(hit / n, 3) if n else 0,
            'dist1_share': round(d1 / n, 3) if n else 0}


# ----------------------------------------------------- 3. location classification
def feats(r, include_empirical=True):
    ops = json.loads(r['edit_ops']) if r['edit_ops'] else []
    if ops:
        dom = Counter((o['op'], o['unit']) for o in ops).most_common(1)[0][0]
    else:
        dom = ('none', 'none')
    try:
        dist = min(int(r['edit_distance']), 5)
    except ValueError:
        dist = 0
    out = [f'op={dom[0]}', f'unit={dom[1]}', f'dist={dist}',
           f'script={r["script_new"]}', f'edit_space={r.get("edit_space", "")}']
    if include_empirical:
        out.append(f'cl={r["error_type_empirical"]}')
    return tuple(out)


def classify(rows, include_empirical=True):
    train, test = [], []
    for r in rows:
        if r['evidence_level'] != 'derived' or r['error_component'] == 'unknown':
            continue
        sample = (feats(r, include_empirical=include_empirical), r['error_component'])
        if r['split'] == 'train':
            train.append(sample)
        elif r['split'] == 'test':
            test.append(sample)
    if not train or not test:
        return {'note': 'insufficient train/test'}
    labels = Counter(y for _, y in train)
    prior = {y: math.log(c / len(train)) for y, c in labels.items()}
    fcount = defaultdict(Counter)        # label -> feature -> count
    ftot = Counter()
    vocab = set()
    for f, y in train:
        for x in f:
            fcount[y][x] += 1; ftot[y] += 1; vocab.add(x)
    V = len(vocab) or 1

    def predict(f):
        best, bestp = None, -1e18
        for y in labels:
            p = prior[y]
            for x in f:
                p += math.log((fcount[y].get(x, 0) + 1) / (ftot[y] + V))
            if p > bestp:
                best, bestp = y, p
        return best

    maj = labels.most_common(1)[0][0]
    correct = maj_correct = 0
    per = defaultdict(lambda: [0, 0, 0])   # label -> [tp, fp, fn]
    for f, y in test:
        pred = predict(f)
        correct += pred == y
        maj_correct += maj == y
        if pred == y:
            per[y][0] += 1
        else:
            per[pred][1] += 1; per[y][2] += 1
    f1s = []
    for y, (tp, fp, fn) in per.items():
        pr = tp / (tp + fp) if tp + fp else 0
        rc = tp / (tp + fn) if tp + fn else 0
        f1s.append(2 * pr * rc / (pr + rc) if pr + rc else 0)
    return {'train': len(train), 'test': len(test),
            'accuracy': round(correct / len(test), 3),
            'macro_f1': round(sum(f1s) / len(f1s), 3) if f1s else 0,
            'majority_baseline_accuracy': round(maj_correct / len(test), 3),
            'majority_class': maj, 'classes': len(labels)}


def main():
    with open(IN_CSV, encoding='utf-8') as f:
        rows = list(csv.DictReader(f))
    form_rows = [r for r in rows if r['source_layer'] == 'form'
                 and is_token(r['old_iast']) and is_token(r['new_iast'])]
    det = detection(form_rows)
    cor = correction(form_rows)
    cls = classify(rows, include_empirical=True)
    cls_no_emp = classify(rows, include_empirical=False)

    out = {'generatedAt': datetime.now(timezone.utc).isoformat(),
           'detection': det, 'correction': cor,
           'location_classification': cls,
           'location_classification_no_empirical': cls_no_emp,
           'classification': cls}
    with open(OUT_JSON, 'w', encoding='utf-8') as f:
        json.dump(out, f, ensure_ascii=False, indent=2)

    L = []; A = L.append
    A('# Baselines for the CDSL correction corpus (OBS-T)')
    A('')
    A('_Generated by `scripts/obs_t_baselines.py` from '
      '`correction_events_release.csv`. Stdlib-only, deterministic; these are '
      'reference baselines that define the tasks, not tuned systems._')
    A('')
    A('Three tasks the released resource supports, on a temporal split (train on '
      'the past, test on recent edits).')
    A('')
    A('## 1. Error detection (form layer)')
    A('')
    A('Minimal-pair ranking: does a character-trigram LM (trained on correct forms) '
      'assign higher likelihood to the corrected form than to the erroneous one? '
      'Chance = 0.5. An absolute-threshold classifier is uninformative because '
      '`old`/`new` differ by a single character.')
    A('')
    A('| metric | value |')
    A('|---|---:|')
    A(f'| train tokens | {det["train_tokens"]:,} |')
    A(f'| test pairs | {det["test_pairs"]:,} |')
    A(f'| **pairwise accuracy** (chance 0.5) | **{det["pairwise_accuracy"]}** |')
    A(f'| tie rate | {det["tie_rate"]} |')
    A('')
    A('## 2. Error correction (form layer)')
    A('')
    A('Noisy-channel: pick the edit-1 candidate the character-LM scores highest '
      '(Norvig-style), preferring training-lexicon forms. Open-vocabulary, so it '
      'does not require the corrected form to have been seen before.')
    A('')
    A('| metric | value |')
    A('|---|---:|')
    A(f'| train lexicon | {cor["train_lexicon"]:,} forms |')
    A(f'| test pairs | {cor["test_pairs"]:,} |')
    A(f'| **accuracy@1** | **{cor["accuracy_at_1"]}** |')
    A(f'| share of test errors at edit-distance 1 | {cor["dist1_share"]} (model\'s reach) |')
    A('')
    A('## 3. Location classification (all derived events)')
    A('')
    A('Predict the microstructure `error_component` from edit-op features '
      '(dominant operation, unit, edit-distance bucket, script, edit space, and '
      'optionally empirical cluster) with categorical Naive Bayes.')
    A('')
    if 'accuracy' in cls:
        A('| metric | value |')
        A('|---|---:|')
        A(f'| train / test | {cls["train"]:,} / {cls["test"]:,} |')
        A(f'| classes | {cls["classes"]} |')
        A(f'| **accuracy** | **{cls["accuracy"]}** |')
        A(f'| macro-F1 | {cls["macro_f1"]} |')
        A(f'| majority baseline ({cls["majority_class"]}) | {cls["majority_baseline_accuracy"]} |')
        if 'accuracy' in cls_no_emp:
            A(f'| ablation: no `error_type_empirical` accuracy | {cls_no_emp["accuracy"]} |')
            A(f'| ablation: no `error_type_empirical` macro-F1 | {cls_no_emp["macro_f1"]} |')
    else:
        A(f'_{cls.get("note","n/a")}_')
    A('')
    A('*Reference baselines only — the paper compares these against neural '
      'sequence models. Object of analysis in scope per `docs/BOUNDARY_RULES.md`.*')
    with open(OUT_MD, 'w', encoding='utf-8', newline='\n') as f:
        f.write('\n'.join(L) + '\n')

    print(f'wrote {OUT_JSON}')
    print(f'wrote {OUT_MD}')
    print(f'  detection pair-acc={det["pairwise_accuracy"]}  '
          f'correction acc@1={cor["accuracy_at_1"]}  '
          f'location acc={cls.get("accuracy","?")} '
          f'no-emp={cls_no_emp.get("accuracy","?")} '
          f'(maj {cls.get("majority_baseline_accuracy","?")})')


if __name__ == '__main__':
    main()
