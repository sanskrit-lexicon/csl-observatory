#!/usr/bin/env python3
"""OBS-T Phase 7 — gold-annotation harness for validating component labels.

Two modes:

  --make   draw a blind, stratified sample (by component x evidence level) for a
           human to annotate. The auto label and evidence level are HIDDEN so the
           annotation is independent. Writes validation/gold_sample.csv.

  --score  read the annotated sheet back (the `gold_component` column filled),
           join to the automatic labels, and report accuracy overall, **by
           evidence level** (derived vs inferred — the key reviewer question),
           per-component precision/recall/F1, and the confusion matrix. If a
           second annotator filled `gold_component_2`, also report Cohen's kappa.

Stratifying by (component x evidence) guarantees enough *inferred* rows to test
whether the heuristic fallback labels are materially worse than the derived ones.

Input : observatory/site/src/data/correction_events_final.csv
I/O   : validation/gold_sample.csv          (blind sheet to annotate)
        validation/COMPONENT_GUIDE.md        (the label definitions)
        reports/obs_t_validation.md          (--score output)
        validation/gold_metrics.json         (--score output)

Usage:  python scripts/obs_t_gold.py --make [N_PER_CELL]
        python scripts/obs_t_gold.py --score
"""
import csv, json, os, random, sys
from collections import Counter, defaultdict
from datetime import datetime, timezone
sys.stdout.reconfigure(encoding='utf-8'); sys.stderr.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DATA = os.path.join(ROOT, 'observatory', 'site', 'src', 'data')
FINAL = os.path.join(DATA, 'correction_events_final.csv')
VDIR = os.path.join(ROOT, 'validation')
SHEET = os.path.join(VDIR, 'gold_sample.csv')
GUIDE = os.path.join(VDIR, 'COMPONENT_GUIDE.md')
OUT_MD = os.path.join(ROOT, 'reports', 'obs_t_validation.md')
OUT_JSON = os.path.join(VDIR, 'gold_metrics.json')
csv.field_size_limit(10_000_000)

SEED = 42
CAP_PER_CELL = 30

SHEET_COLS = ['row_id', 'event_id', 'source_layer', 'dict', 'date',
              'headword_iast', 'old_iast', 'new_iast', 'old_raw', 'new_raw',
              'comment_raw', 'gold_component', 'gold_component_2', 'notes']

COMPONENTS = ['headword', 'grammar', 'citation', 'sense', 'crossref', 'meta',
              'encoding', 'markup', 'orthography', 'unknown']

GUIDE_TEXT = """# Component annotation guide

Label each correction by the dictionary-entry **component it repairs** — *where*
the error was, not its surface form. Put one value in `gold_component`. If two
seem to fit, pick the most specific; use `notes` for doubts. A second annotator
(for inter-annotator agreement) fills `gold_component_2` independently.

| value | what it means | typical locus |
|---|---|---|
| `headword` | lemma / headword / homonym index | `<k1> <k2> <h>` |
| `grammar` | gender / part-of-speech | `<lex>` |
| `citation` | source reference / siglum / page | `<ls>`, `<pc>` |
| `sense` | gloss / definition / meaning content | definition prose, `<s>` |
| `crossref` | cross-reference / link target | `<lb>` |
| `meta` | record id / structural metadata | `<L> <e>` |
| `encoding` | transliteration / diacritic of a Sanskrit form | any Sanskrit text |
| `markup` | XML/tag structure itself (delimiters, tag names) | `< >`, `{ }` |
| `orthography` | plain spelling typo, capitalization, whitespace in non-tag text | body text |
| `unknown` | cannot tell from the evidence shown | — |

Tips:
- For **git-layer** rows, read `old_raw`/`new_raw` (the tagged source line) to see
  which tag's content changed.
- For **form-layer** rows, judge from `old_iast`→`new_iast` and the `headword`.
- `encoding` vs `orthography`: `encoding` = a Sanskrit diacritic/transliteration
  fix; `orthography` = a plain Latin/case/spacing typo.
- Do not look at any auto-generated label; this sheet hides it on purpose.
"""


def make(cap):
    with open(FINAL, encoding='utf-8') as f:
        rows = list(csv.DictReader(f))
    cells = defaultdict(list)
    for r in rows:
        # only sample rows a human can actually judge (some content to see)
        if not any(r[c].strip() for c in ('old_iast', 'new_iast', 'old_raw', 'new_raw')):
            continue
        cells[(r['error_component'], r['evidence_level'])].append(r)
    rng = random.Random(SEED)
    picked = []
    for cell, items in sorted(cells.items()):
        rng.shuffle(items)
        picked.extend(items[:cap])
    rng.shuffle(picked)
    os.makedirs(VDIR, exist_ok=True)
    with open(SHEET, 'w', encoding='utf-8', newline='') as f:
        w = csv.DictWriter(f, fieldnames=SHEET_COLS); w.writeheader()
        for i, r in enumerate(picked, 1):
            w.writerow({'row_id': i, 'event_id': r['event_id'],
                        'source_layer': r['source_layer'], 'dict': r['dict'],
                        'date': r['date'], 'headword_iast': r['headword_iast'],
                        'old_iast': r['old_iast'], 'new_iast': r['new_iast'],
                        'old_raw': r['old_raw'], 'new_raw': r['new_raw'],
                        'comment_raw': r['comment_raw'],
                        'gold_component': '', 'gold_component_2': '', 'notes': ''})
    with open(GUIDE, 'w', encoding='utf-8', newline='\n') as f:
        f.write(GUIDE_TEXT)
    cellcount = Counter((r['error_component'], r['evidence_level']) for r in picked)
    print(f'wrote {SHEET}  ({len(picked)} rows, cap {cap}/cell)')
    print(f'wrote {GUIDE}')
    print('  cells:', dict(sorted(cellcount.items())))
    print('  -> fill the gold_component column, then run --score')


def cohen_kappa(pairs):
    labels = sorted({x for p in pairs for x in p})
    n = len(pairs)
    if not n:
        return 0.0
    po = sum(1 for a, b in pairs if a == b) / n
    ca = Counter(a for a, _ in pairs); cb = Counter(b for _, b in pairs)
    pe = sum((ca[l] / n) * (cb[l] / n) for l in labels)
    return (po - pe) / (1 - pe) if pe != 1 else 1.0


def score():
    with open(FINAL, encoding='utf-8') as f:
        auto = {r['event_id']: (r['error_component'], r['evidence_level'])
                for r in csv.DictReader(f)}
    with open(SHEET, encoding='utf-8') as f:
        sheet = [r for r in csv.DictReader(f) if r['gold_component'].strip()]
    if not sheet:
        sys.exit('no annotated rows yet — fill gold_component in '
                 f'{os.path.relpath(SHEET, ROOT)} and re-run --score')

    n = correct = 0
    by_ev = defaultdict(lambda: [0, 0])      # evidence -> [correct, total]
    per = defaultdict(lambda: [0, 0, 0])     # label -> [tp, fp, fn]
    confusion = Counter()
    for r in sheet:
        gold = r['gold_component'].strip()
        a_comp, ev = auto.get(r['event_id'], ('?', '?'))
        n += 1
        ok = a_comp == gold
        correct += ok
        by_ev[ev][0] += ok; by_ev[ev][1] += 1
        confusion[(a_comp, gold)] += 1
        if ok:
            per[gold][0] += 1
        else:
            per[a_comp][1] += 1; per[gold][2] += 1

    f1s = {}
    for lab, (tp, fp, fn) in per.items():
        pr = tp / (tp + fp) if tp + fp else 0
        rc = tp / (tp + fn) if tp + fn else 0
        f1s[lab] = (round(pr, 3), round(rc, 3),
                    round(2 * pr * rc / (pr + rc), 3) if pr + rc else 0)

    iaa_pairs = [(r['gold_component'].strip(), r['gold_component_2'].strip())
                 for r in sheet if r['gold_component_2'].strip()]
    kappa = round(cohen_kappa(iaa_pairs), 3) if iaa_pairs else None

    metrics = {
        'generatedAt': datetime.now(timezone.utc).isoformat(),
        'annotated': n, 'accuracy': round(correct / n, 3),
        'accuracyByEvidence': {ev: round(c / t, 3) for ev, (c, t) in by_ev.items()},
        'countsByEvidence': {ev: t for ev, (c, t) in by_ev.items()},
        'perComponent': f1s,
        'iaa': {'pairs': len(iaa_pairs), 'cohen_kappa': kappa},
        'topConfusions': [{'auto': a, 'gold': g, 'n': c}
                          for (a, g), c in confusion.most_common(15) if a != g],
    }
    os.makedirs(VDIR, exist_ok=True)
    with open(OUT_JSON, 'w', encoding='utf-8') as f:
        json.dump(metrics, f, ensure_ascii=False, indent=2)

    L = []; A = L.append
    A('# Validation of the microstructure component labels (OBS-T)')
    A('')
    A(f'_Generated by `scripts/obs_t_gold.py --score` over {n} human-annotated '
      'events (blind stratified sample). Accuracy = agreement of the automatic '
      '`error_component` with the human gold label._')
    A('')
    A('| metric | value |')
    A('|---|---:|')
    A(f'| annotated events | {n} |')
    A(f'| **overall accuracy** | **{metrics["accuracy"]}** |')
    for ev in ('derived', 'inferred'):
        if ev in metrics['accuracyByEvidence']:
            A(f'| accuracy ({ev}, n={metrics["countsByEvidence"][ev]}) | '
              f'{metrics["accuracyByEvidence"][ev]} |')
    if kappa is not None:
        A(f'| inter-annotator agreement (Cohen κ, n={len(iaa_pairs)}) | {kappa} |')
    A('')
    A('The derived/inferred split is the key result: it shows whether the heuristic '
      'fallback labels can be trusted, or should be reported separately.')
    A('')
    A('## Per-component precision / recall / F1 (auto vs gold)')
    A('')
    A('| component | precision | recall | F1 |')
    A('|---|---:|---:|---:|')
    for lab in COMPONENTS:
        if lab in f1s:
            p, r, fr = f1s[lab]
            A(f'| {lab} | {p} | {r} | {fr} |')
    A('')
    if metrics['topConfusions']:
        A('## Top confusions (auto → gold)')
        A('')
        A('| auto label | true (gold) | n |')
        A('|---|---|---:|')
        for c in metrics['topConfusions']:
            A(f'| {c["auto"]} | {c["gold"]} | {c["n"]} |')
        A('')
    A('*Validation artifact; object of analysis in scope per `docs/BOUNDARY_RULES.md`.*')
    with open(OUT_MD, 'w', encoding='utf-8', newline='\n') as f:
        f.write('\n'.join(L) + '\n')
    print(f'wrote {OUT_MD}')
    print(f'wrote {OUT_JSON}')
    print(f'  accuracy {metrics["accuracy"]} (n={n})  byEvidence {metrics["accuracyByEvidence"]}'
          + (f'  kappa {kappa}' if kappa is not None else '  (no 2nd annotator yet)'))


def main():
    if '--make' in sys.argv:
        i = sys.argv.index('--make')
        cap = int(sys.argv[i + 1]) if len(sys.argv) > i + 1 and sys.argv[i + 1].isdigit() else CAP_PER_CELL
        make(cap)
    elif '--score' in sys.argv:
        score()
    else:
        sys.exit('usage: obs_t_gold.py --make [N_PER_CELL] | --score')


if __name__ == '__main__':
    main()
