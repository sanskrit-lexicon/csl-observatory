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

  --ingest apply a second-annotator decisions file (downloaded from the blind
           review sheet built by scripts/obs_t_second_sheet.py) onto the sheet's
           `gold_component_2` column. Validates the schema, the location
           vocabulary and the row ids, and refuses to clobber any existing
           gold_component_2 value without --force. Never touches gold_component
           or notes. `--sheet PATH` redirects the target (fixture round-trips
           run against a sandbox copy, never the real instrument).

Stratifying by (component x evidence) guarantees enough *inferred* rows to test
whether the heuristic fallback labels are materially worse than the derived ones.

Input : observatory/site/src/data/correction_events_final.csv
I/O   : validation/gold_sample.csv          (blind sheet to annotate)
        validation/COMPONENT_GUIDE.md        (the label definitions)
        reports/obs_t_validation.md          (--score output)
        validation/gold_metrics.json         (--score output)

--make refuses to overwrite a sheet that already carries hand annotations (it
would discard them); pass --force to draw a fresh sample anyway.

Usage:  python scripts/obs_t_gold.py --make [N_PER_CELL] [--force]
        python scripts/obs_t_gold.py --score
        python scripts/obs_t_gold.py --ingest DECISIONS.json [--sheet PATH] [--force]
"""
import csv, json, os, random, sys
from collections import Counter, defaultdict
from datetime import datetime, timezone
from typing import NoReturn
sys.stdout.reconfigure(encoding='utf-8'); sys.stderr.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DATA = os.path.join(ROOT, 'observatory', 'site', 'src', 'data')
FINAL = os.path.join(DATA, 'correction_events_final.csv')
CROSSWALK = os.path.join(DATA, 'event_id_crosswalk_v1.csv')
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
              'markup', 'unattributed']

GUIDE_TEXT = """# Location annotation guide (axis A)

Label each correction by **where in the dictionary entry** it repairs — the
LOCATION axis. This is independent of the *edit type* (spelling/diacritic/case),
which is a separate axis handled automatically. So a spelling typo inside a
definition is `sense` (location), not "orthography". Put one value in
`gold_component`; use `notes` for doubts. A second annotator (for inter-annotator
agreement) fills `gold_component_2` independently.

| value | what it means | typical locus |
|---|---|---|
| `headword` | lemma / headword / homonym index | `<k1> <k2> <h>` |
| `grammar` | gender / part-of-speech | `<lex>` |
| `citation` | source reference / siglum / page | `<ls>`, `<pc>` |
| `sense` | gloss / definition / meaning content (incl. Sanskrit words in the gloss) | definition prose, `<s>` |
| `crossref` | cross-reference / link target | `<lb>` |
| `meta` | record id / structural metadata | `<L> <e>` |
| `markup` | the XML/tag structure itself (delimiters, tag names) | `< >`, `{ }` |
| `unattributed` | cannot tell where from the evidence shown | — |

Tips:
- Judge the **location**, not the kind of edit. A diacritic fix on a headword =
  `headword`; the same fix in a gloss word = `sense`.
- For **git-layer** rows, read `old_raw`/`new_raw` (the tagged source line) to see
  which tag's content changed.
- For **form-layer** rows, judge from `old_iast`→`new_iast` and the `headword`.
- Do not look at any auto-generated label; this sheet hides it on purpose.
"""


# Columns a human fills in by hand; never clobber these without --force.
ANNOTATION_COLS = ('gold_component', 'gold_component_2', 'notes')


def count_annotations(path, cols):
    """How many rows in an existing sheet carry hand-entered annotations."""
    if not os.path.exists(path):
        return 0
    try:
        with open(path, encoding='utf-8') as f:
            rows = list(csv.DictReader(f))
    except Exception:
        return 0
    return sum(1 for r in rows if any((r.get(c) or '').strip() for c in cols))


def make(cap, force=False):
    # The sheet is git-tracked and gets hand-annotated (gold_component). Drawing a
    # fresh blind sample would discard that work, so refuse unless --force.
    existing = count_annotations(SHEET, ANNOTATION_COLS)
    if existing and not force:
        sys.exit(
            f'refusing to overwrite {os.path.relpath(SHEET, ROOT)}: it carries '
            f'{existing} hand-annotated row(s). Re-drawing the blind sample would '
            f'discard them. Use --score to read the current sheet, or back it up '
            f'and pass --force to draw a new sample.'
        )
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


# Second-annotator decisions files (H5312) — produced by the blind sheet
# validation/second_annotator_sheet.html (built by scripts/obs_t_second_sheet.py).
DECISIONS_SCHEMA = 'obs-t-second-annotator-decisions-v1'
SHEET_ID = 'obs-t-gold-second-annotator-v1'
EDIT_TYPES = ['spelling', 'diacritic', 'case', 'spacing', 'punctuation',
              'digit', 'transposition', 'source-raw', 'none']


def _fail(msg) -> NoReturn:
    sys.exit(f'ingest refused: {msg}')


def ingest(decisions_path, sheet_path=SHEET, force=False):
    """Apply a blind-sheet decisions file onto the sheet's gold_component_2 column.

    Fail-closed: schema/vocabulary/row-id mismatches abort WITHOUT writing.
    Existing gold_component_2 values are never clobbered without --force; the
    first-annotator columns (gold_component, notes) are never touched.
    """
    try:
        with open(decisions_path, encoding='utf-8') as f:
            dec = json.load(f)
    except (OSError, json.JSONDecodeError) as e:
        _fail(f'cannot read decisions file {decisions_path}: {e}')
    if not isinstance(dec, dict) or not isinstance(dec.get('decisions'), list):
        _fail('decisions file must be an object with a "decisions" list')
    if dec.get('schema') != DECISIONS_SCHEMA:
        _fail(f'schema mismatch: expected {DECISIONS_SCHEMA!r}, '
              f'got {dec.get("schema")!r}')
    if dec.get('sheet_id') != SHEET_ID:
        _fail(f'sheet_id mismatch: expected {SHEET_ID!r}, got {dec.get("sheet_id")!r}')

    try:
        with open(sheet_path, encoding='utf-8') as f:
            rows = list(csv.DictReader(f))
    except OSError as e:
        _fail(f'cannot read sheet {sheet_path}: {e}')
    by_id = {r['row_id']: r for r in rows}

    seen, would_clobber = set(), []
    for d in dec['decisions']:
        if not isinstance(d, dict):
            _fail('decision entry is not an object')
        rid = str(d.get('row_id', '')).strip()
        if rid not in by_id:
            _fail(f'row_id {rid!r} is not in the sheet')
        if rid in seen:
            _fail(f'duplicate row_id {rid!r} in decisions file')
        seen.add(rid)
        loc = (d.get('location') or '').strip()
        if loc not in COMPONENTS:
            _fail(f'row {rid}: location {loc!r} not in the axis-A vocabulary {COMPONENTS}')
        et = (d.get('edit_type') or '').strip()
        if et and et not in EDIT_TYPES:
            _fail(f'row {rid}: edit_type {et!r} not in the axis-B vocabulary {EDIT_TYPES}')
        if by_id[rid]['gold_component_2'].strip() and rid not in would_clobber:
            would_clobber.append(rid)
    if not seen:
        _fail('decisions file carries zero decided rows')

    if would_clobber and not force:
        _fail(f'{len(would_clobber)} row(s) already carry a gold_component_2 value '
              f'(first: {would_clobber[0]}). Re-running --ingest with --force '
              f'overwrites them knowingly.')
    if dec.get('fixture'):
        print('  WARNING: decisions file is marked fixture:true — synthetic '
              'round-trip data, NOT annotations.')
    stale_labels = Counter(r['gold_component'].strip() for r in rows
                           if r['gold_component'].strip() not in COMPONENTS)
    if stale_labels:
        print('  WARNING: the sheet\'s gold_component column carries RETIRED '
              f'one-axis labels ({dict(stale_labels)}) — the kappa this enables '
              'is NOT interpretable until that column is re-based (H5312 '
              'follow-up decision).')

    applied = 0
    for d in dec['decisions']:
        rid = str(d['row_id'])
        by_id[rid]['gold_component_2'] = d['location'].strip()
        applied += 1
    with open(sheet_path, 'w', encoding='utf-8', newline='') as f:
        w = csv.DictWriter(f, fieldnames=SHEET_COLS); w.writeheader()
        w.writerows(rows)
    print(f'ingested {applied} decision(s) into '
          f'{os.path.relpath(sheet_path, ROOT)} '
          f'(clobbered {len(would_clobber)} existing value(s))')
    print('  -> run --score to see the kappa')


def score():
    with open(FINAL, encoding='utf-8') as f:
        auto = {r['event_id']: (r['error_component'], r['evidence_level'])
                for r in csv.DictReader(f)}
    # H1494 migrated correction_events*.csv event_ids to the obst:v1 scheme; the
    # gold sheet still carries the OLD hex ids. Resolve old->new at read time via
    # the migration crosswalk so the auto-join (accuracy / evidence split) keeps
    # working; ids already obst:v1 and unresolvable ids pass through unchanged.
    xwalk = {}
    if os.path.exists(CROSSWALK):
        with open(CROSSWALK, encoding='utf-8') as f:
            xwalk = {r['old_event_id']: r['new_event_id'] for r in csv.DictReader(f)}
    with open(SHEET, encoding='utf-8') as f:
        sheet = [r for r in csv.DictReader(f) if r['gold_component'].strip()]
    if not sheet:
        sys.exit('no annotated rows yet — fill gold_component in '
                 f'{os.path.relpath(SHEET, ROOT)} and re-run --score')
    unresolved_join = sum(1 for r in sheet
                          if xwalk.get(r['event_id'], r['event_id']) not in auto)
    # H5312 finding: a gold_component value outside the Phase-8 location axis
    # (e.g. 'encoding' / 'orthography') proves the first-annotator column still
    # carries the RETIRED one-axis typology. Kappa between that column and a
    # current-axis gold_component_2 is arithmetically computable but NOT
    # interpretable — flag it wherever the numbers go.
    stale_labels = Counter(r['gold_component'].strip() for r in sheet
                           if r['gold_component'].strip() not in COMPONENTS)
    stale_axis = bool(stale_labels)

    n = correct = 0
    by_ev = defaultdict(lambda: [0, 0])      # evidence -> [correct, total]
    per = defaultdict(lambda: [0, 0, 0])     # label -> [tp, fp, fn]
    confusion = Counter()
    for r in sheet:
        gold = r['gold_component'].strip()
        eid = xwalk.get(r['event_id'], r['event_id'])
        a_comp, ev = auto.get(eid, ('?', '?'))
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
        'eventIdJoin': {'resolved': n - unresolved_join, 'unresolved': unresolved_join},
        'firstAnnotatorColumn': (
            {'status': 'stale-axis (retired one-axis labels)',
             'labelsOutsideLocationAxis': dict(stale_labels)}
            if stale_axis else {'status': 'ok (location axis)'}),
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
    if stale_axis:
        A('> 🔴 **KAPPA NOT INTERPRETABLE AS-IS:** the sheet\'s `gold_component` '
          'column still carries the RETIRED one-axis labels ('
          + ', '.join(f'`{k}`×{v}' for k, v in stale_labels.most_common()) +
          ') — it predates the Phase-8 location axis. A kappa between this column '
          'and a current-axis `gold_component_2` measures a vocabulary mismatch, '
          'not annotator agreement. Re-base the first-annotator column (adopt the '
          'H1385 pass-A labels, or a fresh human pass) before quoting any kappa '
          'from this table. Tracked as a follow-up decision.')
        A('')
    if unresolved_join:
        A(f'> ⚠️ **Partial auto-join:** {unresolved_join} of {n} sheet event_ids no '
          'longer resolve to `correction_events_final.csv` (the H1494 obst:v1 id '
          'migration left the gold sheet on old hex ids; the crosswalk recovers '
          f'only {n - unresolved_join}). Accuracy and the evidence split cover the '
          'resolved subset only; **the kappa below is unaffected** — it compares '
          'the two annotator columns on the sheet itself. Re-keying the sheet is '
          'a tracked follow-up.')
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
    if unresolved_join:
        print(f'  WARNING: {unresolved_join}/{n} event_ids did not join to the final '
              f'csv (obst:v1 migration desync) — accuracy/evidence cover the resolved '
              f'subset only; kappa is unaffected.')
    if stale_axis:
        print(f'  WARNING: gold_component carries RETIRED one-axis labels '
              f'({dict(stale_labels)}) — any kappa vs gold_component_2 is NOT '
              f'interpretable until the first-annotator column is re-based '
              f'(H5312 follow-up decision).')


def main():
    if '--make' in sys.argv:
        i = sys.argv.index('--make')
        cap = int(sys.argv[i + 1]) if len(sys.argv) > i + 1 and sys.argv[i + 1].isdigit() else CAP_PER_CELL
        make(cap, force='--force' in sys.argv)
    elif '--score' in sys.argv:
        score()
    elif '--ingest' in sys.argv:
        i = sys.argv.index('--ingest')
        if len(sys.argv) <= i + 1:
            sys.exit('usage: obs_t_gold.py --ingest DECISIONS.json [--sheet PATH] [--force]')
        sheet_path = SHEET
        if '--sheet' in sys.argv:
            sheet_path = sys.argv[sys.argv.index('--sheet') + 1]
        ingest(sys.argv[i + 1], sheet_path=sheet_path, force='--force' in sys.argv)
    else:
        sys.exit('usage: obs_t_gold.py --make [N_PER_CELL] | --score | '
                 '--ingest DECISIONS.json [--sheet PATH] [--force]')


if __name__ == '__main__':
    main()
