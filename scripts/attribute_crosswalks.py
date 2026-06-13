#!/usr/bin/env python3
"""OBS-T Phase 4 — crosswalk typologies (ERRANT / OCR / textual-criticism).

The canonical typology is the microstructure component (Phase 3). This phase adds
three *secondary* views over the same events, each derived deterministically from
the typed edit-op trace, so reviewers from any tradition can read the corpus:

* **errant_type**  — ERRANT-style operation x linguistic unit (e.g. R:DIACRITIC,
  M:CONSONANT, U:WHITESPACE), the dominant edit of the event.
* **ocr_class**    — OCR/digitization: substitution / insertion / deletion /
  segmentation / transposition.
* **textcrit_class** — textual criticism (Katre): substitution / addition /
  omission / metathesis, refined to dittography / haplography where detectable.

Also emits the **character-confusion matrix** (which char was mistaken for which)
— the signature linguistic artifact for the paper.

Input : observatory/site/src/data/correction_events_typed.csv  (needs edit_ops)
Outputs: observatory/site/src/data/correction_events_final.csv  (+ 3 columns)
         observatory/site/src/data/obs_t_confusion.csv          (from,to,unit,count)
         observatory/site/src/data/obs_t_crosswalk.csv          (errant/ocr/textcrit dists)
         observatory/site/src/data/correction_events_final.meta.json

Usage:  python scripts/attribute_crosswalks.py
"""
import csv, json, os, sys, unicodedata
from collections import Counter
from datetime import datetime, timezone
sys.stdout.reconfigure(encoding='utf-8'); sys.stderr.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DATA = os.path.join(ROOT, 'observatory', 'site', 'src', 'data')
IN_CSV = os.path.join(DATA, 'correction_events_typed.csv')
OUT_CSV = os.path.join(DATA, 'correction_events_final.csv')
OUT_CONF = os.path.join(DATA, 'obs_t_confusion.csv')
OUT_CROSS = os.path.join(DATA, 'obs_t_crosswalk.csv')
OUT_META = os.path.join(DATA, 'correction_events_final.meta.json')
csv.field_size_limit(10_000_000)

ERRANT_OP = {'sub': 'R', 'ins': 'M', 'del': 'U', 'transpose': 'R'}
OCR_OP = {'sub': 'substitution', 'ins': 'insertion', 'del': 'deletion'}
TC_OP = {'sub': 'substitution', 'ins': 'addition', 'del': 'omission'}


def dominant(ops):
    """The most frequent (op, unit) pair in an event's edit trace."""
    c = Counter((o['op'], o['unit']) for o in ops)
    return c.most_common(1)[0][0]


def scribal_refine(old, new):
    """Detect dittography (erroneous doubling) / haplography (lost doubling)."""
    o = unicodedata.normalize('NFC', old)
    n = unicodedata.normalize('NFC', new)
    if len(n) == len(o) + 1:
        for i in range(len(n) - 1):
            if n[i] == n[i + 1] and n[:i] + n[i + 1:] == o:
                return 'dittography'
    if len(o) == len(n) + 1:
        for i in range(len(o) - 1):
            if o[i] == o[i + 1] and o[:i] + o[i + 1:] == n:
                return 'haplography'
    return None


# EDIT-TYPE axis (what kind of change), orthogonal to the location component.
_UNIT2TYPE = {'diacritic': 'diacritic', 'case': 'case', 'whitespace': 'spacing',
              'punctuation': 'punctuation', 'digit': 'digit',
              'consonant': 'spelling', 'vowel': 'spelling', 'latin': 'spelling',
              'other': 'spelling'}


def edit_type_of(ops):
    """Primary edit TYPE from the dominant op/unit (spelling / diacritic / case /
    spacing / punctuation / transposition). The axis the corpus was missing."""
    if not ops:
        return 'none'
    if any(o['op'] == 'transpose' for o in ops):
        return 'transposition'
    if any(o['unit'] == 'whitespace' for o in ops):
        return 'spacing'
    _op, unit = dominant(ops)
    return _UNIT2TYPE.get(unit, 'spelling')


def classify(ops, old, new):
    """Return (errant_type, ocr_class, textcrit_class)."""
    if not ops:
        return 'none', 'unknown', 'unknown'
    op, unit = dominant(ops)
    errant = f'{ERRANT_OP.get(op, "R")}:{unit.upper()}' if op != 'transpose' \
        else f'R:TRANSP-{unit.upper()}'
    units = {o['unit'] for o in ops}
    haswsp = 'whitespace' in units
    hastr = any(o['op'] == 'transpose' for o in ops)
    if haswsp:
        ocr = 'segmentation'
    elif hastr:
        ocr = 'transposition'
    else:
        ocr = OCR_OP.get(op, 'substitution')
    if hastr:
        tc = 'metathesis'
    elif op in ('ins', 'del'):
        tc = scribal_refine(old, new) or TC_OP[op]
    else:
        tc = TC_OP.get(op, 'substitution')
    return errant, ocr, tc


def main():
    with open(IN_CSV, encoding='utf-8') as f:
        rows = list(csv.DictReader(f))
    if 'edit_ops' not in rows[0]:
        sys.exit('input lacks edit_ops; run Phase 1-3 first')

    fields = list(rows[0].keys())
    for col in ('edit_type', 'errant_type', 'ocr_class', 'textcrit_class'):
        if col not in fields:
            fields.insert(fields.index('error_component') + 1, col)

    confusion = Counter()
    for r in rows:
        ops = json.loads(r['edit_ops']) if r['edit_ops'] else []
        r['errant_type'], r['ocr_class'], r['textcrit_class'] = \
            classify(ops, r['old_iast'], r['new_iast'])
        r['edit_type'] = edit_type_of(ops)
        for o in ops:
            if o['op'] == 'sub' and len(o['from']) == 1 and len(o['to']) == 1:
                # layer matters: form ops are over IAST (clean Sanskrit), git ops
                # are over SLP1 source lines (markup/English noise) — keep separable
                confusion[(o['from'], o['to'], o['unit'], r['source_layer'])] += 1

    with open(OUT_CSV, 'w', encoding='utf-8', newline='') as f:
        w = csv.DictWriter(f, fieldnames=fields); w.writeheader(); w.writerows(rows)

    # confusion matrix (layer-tagged: form = IAST Sanskrit, git = SLP1 source)
    with open(OUT_CONF, 'w', encoding='utf-8', newline='') as f:
        w = csv.writer(f); w.writerow(['from', 'to', 'unit', 'layer', 'count'])
        for (a, b, u, lyr), n in sorted(confusion.items(), key=lambda kv: -kv[1]):
            w.writerow([a, b, u, lyr, n])

    # crosswalk distributions (one tidy table for figures)
    with open(OUT_CROSS, 'w', encoding='utf-8', newline='') as f:
        w = csv.writer(f); w.writerow(['scheme', 'label', 'layer', 'count'])
        for scheme, col in (('errant', 'errant_type'), ('ocr', 'ocr_class'),
                            ('textcrit', 'textcrit_class')):
            c = Counter((r[col], r['source_layer']) for r in rows)
            for (label, layer), n in sorted(c.items(), key=lambda kv: -kv[1]):
                w.writerow([scheme, label, layer, n])

    meta = {
        'schemaVersion': '1.0.0',
        'generatedAt': datetime.now(timezone.utc).isoformat(),
        'sourcePath': 'correction_events_typed.csv',
        'recordCount': len(rows),
        'assumptions': [
            'Crosswalks are secondary views derived from the typed edit-op trace; '
            'the canonical typology remains the microstructure component.',
            'Event-level label = the dominant (op, unit) of the edit trace.',
            'dittography/haplography detected only for clean single-char in/del.',
            'Confusion matrix counts single-char substitutions over NFD chars.',
        ],
        'warnings': [],
        'stats': {
            'ocr': Counter(r['ocr_class'] for r in rows).most_common(),
            'textcrit': Counter(r['textcrit_class'] for r in rows).most_common(),
            'errantTop': Counter(r['errant_type'] for r in rows).most_common(15),
            'confusionTopForm': [
                {'from': a, 'to': b, 'unit': u, 'count': n}
                for (a, b, u, lyr), n in sorted(confusion.items(), key=lambda kv: -kv[1])
                if lyr == 'form'][:20],
        },
    }
    with open(OUT_META, 'w', encoding='utf-8') as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)

    print(f'wrote {OUT_CSV}  ({len(rows)} events, +3 crosswalk columns)')
    print(f'wrote {OUT_CONF}  ({len(confusion)} distinct confusions)')
    print(f'wrote {OUT_CROSS}')
    print(f'  ocr: {meta["stats"]["ocr"]}')
    print(f'  textcrit: {meta["stats"]["textcrit"]}')
    formconf = [(a + "->" + b, n) for (a, b, u, lyr), n in
                sorted(confusion.items(), key=lambda kv: -kv[1]) if lyr == 'form'][:12]
    print(f'  top FORM (IAST) confusions: {formconf}')


if __name__ == '__main__':
    main()
