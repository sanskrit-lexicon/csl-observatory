#!/usr/bin/env python3
"""Chandas (Sanskrit metre) detector + corpus profiler. H6257.

Detector: syllabify DCS CoNLL-U `# text` lines (IAST), mark each syllable
guru (heavy) / laghu (light) by the classical rules, group lines into stanzas
(DCS sent_counter groups; a bare line when a text has no sent_counter), and
classify the stanza by its syllable-count signature against a pinned table of
classical vṛtta metres.

Modes:
  --validate  precision/recall against text-level weak labels
              (data/chandas_validation_labels_2026-11-16.tsv)
  --canary    agreement against 20 hand-labelled stanzas
              (data/chandas_canary_manual_2026-11-16.tsv)
  --corpus    classify every DCS text, emit the poetic-layer meter
              distribution (data/chandas_meter_distribution_2026-11-16.tsv)
  --selftest  unit checks on hand-counted specimen lines

Meter table (syllables per stanza -> class). vṛtta only; mātrā-chandas
(āryā family, e.g. Amaruśataka) is out of scope in v1 and reported as
'unclassified' — see reports/chandas_corpus_profile_2026-11-16.md.
"""

from __future__ import annotations

import argparse
import collections
import csv
import os
import re
import sys
from pathlib import Path

# ---------------------------------------------------------------- phonetics

VOWELS = set("aiuṛḷāīūṝḹeoA")  # A = merged diphthong ai/au
SHORT = set("aiuṛḷ")

# IAST two-letter consonants collapse to one phoneme so that cluster size is
# counted in phonemes, not letters ("budha" bu- is light, "madhya" ma- heavy).
DIGRAPHS = ("kh", "gh", "ch", "ṭh", "ḍh", "th", "dh", "ph", "bh")
PUNCT = re.compile(r"[^a-zāīūṛṝḷḹeoaiuṃḥṁśṣñṅṭḍ’'\s-]")


def _normalise(line: str) -> str:
    s = line.lower().strip()
    # apostrophes/avagraha = elided vowel: drop them entirely
    s = s.replace("’", "").replace("'", "").replace("-", " ")
    s = PUNCT.sub("", s)
    # one-syllable diphthongs ai/au (never cross a space)
    out: list[str] = []
    i = 0
    while i < len(s):
        c = s[i]
        if c == "a" and i + 1 < len(s) and s[i + 1] in "iu":
            out.append("A")
            i += 2
        else:
            out.append(c)
            i += 1
    return "".join(out)


def _phonemes(s: str) -> str:
    """Collapse IAST digraphs so consonant clusters count phonemically."""
    for d in DIGRAPHS:
        s = s.replace(d, d[0])  # kh -> k, dh -> d, ... (count = 1)
    return s


def syllabify(line: str) -> list[bool]:
    """Return one bool per syllable: True = guru (heavy), False = laghu."""
    s = _phonemes(_normalise(line))
    # nucleus positions
    idxs = [i for i, c in enumerate(s) if c in VOWELS]
    if not idxs:
        return []
    flags: list[bool] = []
    for k, pos in enumerate(idxs):
        v = s[pos]
        end = idxs[k + 1] if k + 1 < len(idxs) else len(s)
        run = s[pos + 1 : end]
        if v in ("A",) or v not in SHORT:
            heavy = True  # long vowel or diphthong
        else:
            cons_all = [c for c in run if c not in VOWELS and c != " "]
            if len(cons_all) >= 2:
                heavy = True  # closed syllable (consonant cluster)
            elif " " in run:
                # word-final consonant closes the syllable; an open word end
                # before the next word's onset stays light
                pre = [c for c in run.split(" ")[0] if c not in VOWELS]
                heavy = bool(pre)
            else:
                heavy = False  # single consonant = onset of next syllable
        flags.append(heavy)
    return flags


def count_syllables(line: str) -> int:
    return len(syllabify(line))


# ---------------------------------------------------------------- meters

# syllable total per stanza -> meter class (vṛtta, equal-pāda families)
METER_TABLE: dict[int, str] = {
    24: "gayatri (3x8)",
    30: "usnih-class",
    32: "anustubh/sloka (4x8)",
    44: "tristubh (4x11)",
    52: "jagati (4x13)",
    68: "17x4 mandakranta/indravajra",
}
UNCLASSIFIED = "unclassified"


def classify(stanza_lines: list[str]) -> str:
    total = sum(count_syllables(ln) for ln in stanza_lines)
    return METER_TABLE.get(total, UNCLASSIFIED)


# ---------------------------------------------------------------- DCS input

CONLLU_ROOT = Path(
    os.environ.get(
        "DCS_CONLLU_ROOT",
        "/Users/mac/Documents/GitHub/VisualDCS/src/DCS-data-2026/conllu/files",
    )
)


def iter_texts(root: Path = CONLLU_ROOT):
    """Yield (text_name, [(sent_counter_or_None, line), ...])."""
    for textdir in sorted(p for p in root.iterdir() if p.is_dir()):
        rows: list[tuple[str | None, str]] = []
        pending: str | None = None
        for f in sorted(textdir.glob("*.conllu")):
            with open(f, encoding="utf-8") as fh:
                for line in fh:
                    line = line.rstrip("\n")
                    if line.startswith("# text = "):
                        pending = line[len("# text = ") :]
                    elif line.startswith("# sent_counter = ") and pending is not None:
                        rows.append((line.split("= ", 1)[1], pending))
                        pending = None
                    elif line.startswith("#") or not line.strip():
                        continue
                    elif pending is not None and not line[:1].isdigit():
                        pass
                if pending is not None:
                    rows.append((None, pending))
                    pending = None
        if rows:
            yield textdir.name, rows


def stanza_groups(rows: list[tuple[str | None, str]]) -> list[list[str]]:
    """Group consecutive rows by sent_counter; counter-less rows = own stanza."""
    out: list[list[str]] = []
    cur_key: object = object()
    cur: list[str] = []
    for key, line in rows:
        if key is None:
            if cur:
                out.append(cur)
                cur = []
            out.append([line])
            cur_key = object()
            continue
        if key != cur_key:
            if cur:
                out.append(cur)
            cur = [line]
            cur_key = key
        else:
            cur.append(line)
    if cur:
        out.append(cur)
    return out


def classify_text(text: str, rows) -> tuple[int, int, collections.Counter]:
    stanzas = stanza_groups(rows)
    counts: collections.Counter = collections.Counter()
    classified = 0
    for st in stanzas:
        m = classify(st)
        counts[m] += 1
        if m != UNCLASSIFIED:
            classified += 1
    return len(stanzas), classified, counts


# ---------------------------------------------------------------- labels

REPO = Path(__file__).resolve().parent.parent
VALIDATION_LABELS = REPO / "data" / "chandas_validation_labels_2026-11-16.tsv"
CANARY = REPO / "data" / "chandas_canary_manual_2026-11-16.tsv"
EPOCHS = REPO / "data" / "chandas_text_epochs_2026-11-16.tsv"
DISTRIBUTION = REPO / "data" / "chandas_meter_distribution_2026-11-16.tsv"


def read_tsv(path: Path) -> list[dict]:
    with open(path, encoding="utf-8") as fh:
        return list(csv.DictReader(fh, delimiter="\t"))


def load_text_rows(text: str) -> list[list[str]]:
    for name, rows in iter_texts():
        if name == text:
            return stanza_groups(rows)
    raise SystemExit(f"text not found in DCS: {text}")


def cmd_validate(_args) -> int:
    labels = read_tsv(VALIDATION_LABELS)
    # predictions cached per text
    tp: collections.Counter = collections.Counter()
    fp: collections.Counter = collections.Counter()
    fn: collections.Counter = collections.Counter()
    per_text = []
    n_total = 0
    for row in labels:
        text = row["text"]
        gold = row["expected_class"]
        limit = int(row.get("max_stanzas") or 0) or 10**9
        stanzas = load_text_rows(text)[:limit]
        t_tp = t_fn = t_fp = 0
        for st in stanzas:
            pred = classify(st)
            n_total += 1
            if pred == gold:
                tp[gold] += 1
                t_tp += 1
            else:
                fn[gold] += 1
                t_fn += 1
                if pred != UNCLASSIFIED:
                    fp[pred] += 1
                    t_fp += 1
        per_text.append((text, gold, len(stanzas), t_tp, t_fn, t_fp))
    classes = sorted(set(tp) | set(fn))
    print(f"Validation set: {n_total} labelled stanzas, {len(labels)} texts\n")
    print(f"{'class':32} {'gold':>6} {'TP':>6} {'FN':>6} {'prec':>7} {'rec':>7} {'F1':>7}")
    for c in classes:
        gold_n = tp[c] + fn[c]
        # precision for class c: of all predictions of c, how many gold c
        pred_c = tp[c] + fp.get(c, 0)
        prec = tp[c] / pred_c if pred_c else 0.0
        rec = tp[c] / gold_n if gold_n else 0.0
        f1 = 2 * prec * rec / (prec + rec) if (prec + rec) else 0.0
        print(f"{c:32} {gold_n:6} {tp[c]:6} {fn[c]:6} {prec:7.3f} {rec:7.3f} {f1:7.3f}")
    print("\nPer text:")
    for text, gold, n, a, b, c in per_text:
        print(f"  {text:32} gold={gold:28} n={n:5} match={a:5} off={b:4} as-other-class={c}")
    return 0


def cmd_canary(_args) -> int:
    rows = read_tsv(CANARY)
    agree = 0
    print(f"{'#':>3} {'text':20} {'manual':30} {'detector':30} ok")
    for i, row in enumerate(rows, 1):
        text = row["text"]
        idx = int(row["stanza_index"])
        manual = row["manual_class"]
        stanzas = load_text_rows(text)
        if idx >= len(stanzas):
            print(f"{i:3} {text:20} STANZA INDEX OUT OF RANGE")
            return 1
        pred = classify(stanzas[idx])
        ok = pred == manual
        agree += ok
        print(f"{i:3} {text:20} {manual:30} {pred:30} {'Y' if ok else 'N'}")
    print(f"\nCanary agreement: {agree}/{len(rows)} (gate >= 18/20)")
    return 0 if agree >= 18 and len(rows) >= 20 else 1


def cmd_corpus(_args) -> int:
    epochs: dict[str, tuple[str, str]] = {}
    if EPOCHS.exists():
        for row in read_tsv(EPOCHS):
            epochs[row["text"]] = (row["epoch"], row["dating_basis"])
    poetic_rows = []
    census = []
    for text, rows in iter_texts():
        n, cls, counts = classify_text(text, rows)
        census.append((text, n, cls))
        if n >= 50 and cls / n >= 0.5:
            epoch, basis = epochs.get(text, ("unmapped", ""))
            for meter, cnt in counts.most_common():
                if meter == UNCLASSIFIED:
                    continue
                poetic_rows.append((text, epoch, meter, cnt, cls))
    with open(DISTRIBUTION, "w", encoding="utf-8", newline="") as fh:
        w = csv.writer(fh, delimiter="\t")
        w.writerow(["text", "epoch", "meter", "stanzas", "classified_total"])
        w.writerows(poetic_rows)
    print(f"DCS texts scanned: {len(census)}")
    print(f"Poetic-layer texts (>=50 stanzas, >=50% classified): "
          f"{len({r[0] for r in poetic_rows})}")
    print(f"Distribution rows: {len(poetic_rows)} -> {DISTRIBUTION.name}")
    unmapped = sorted({r[0] for r in poetic_rows if r[1] == "unmapped"})
    if unmapped:
        print(f"unmapped epochs: {', '.join(unmapped)}")
    return 0


# ---------------------------------------------------------------- selftest

SELFTEST_LINES = [
    # (line, expected syllables) — counted by hand from published text
    ("agnim īḍe purohitam yajñasya devam ṛtvijam hotāram ratna dhātamam", 24),
    ("asty uttarasyāṃ diśi devatātmā himālayo nāma nagādhirājaḥ", 22),
    ("siddhiḥ sādhye satām astu prasādāt tasya dhūrjaṭeḥ", 16),
    (
        "kaścit kāntāvirahaguruṇā svādhikārāt pramattaḥ "
        "śāpenāstaṃgamitamahimā varṣabhogyeṇa bhartuḥ",
        34,
    ),
    ("dikkālādyanavacchinnānantacinmātramūrtaye", 16),
]
SELFTEST_WEIGHTS = [
    # (line, expected guru pattern 1/0 per syllable) — hand-checked
    # e/o are naturally guru (bha-guru) in classical prosody
    ("jāhnavīphenalekheva yanmūrdhni śaśinaḥ kalā", "1011011011000101"),
    ("vācāṃ sarvatra vaicitryaṃ nītividyāṃ dadāti ca", "1111011110110100"),
]


def cmd_selftest(_args) -> int:
    fails = 0
    for line, want in SELFTEST_LINES:
        got = count_syllables(line)
        if got != want:
            fails += 1
            print(f"FAIL count: want {want} got {got}: {line[:60]}")
    for line, want in SELFTEST_WEIGHTS:
        got = "".join("1" if h else "0" for h in syllabify(line))
        if got != want:
            fails += 1
            print(f"FAIL weight: want {want} got {got}: {line[:60]}")
    # negative control: nonsense prose must not classify
    prose = classify(["yadā yadā hi dharmasya glānir bhavati bhārata"])
    if prose != UNCLASSIFIED:
        fails += 1
        print(f"FAIL control: prose classified as {prose}")
    print("selftest:", "FAIL" if fails else "PASS", f"({fails} failures)")
    return 1 if fails else 0


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--validate", action="store_true")
    ap.add_argument("--canary", action="store_true")
    ap.add_argument("--corpus", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args(argv)
    if args.validate:
        return cmd_validate(args)
    if args.canary:
        return cmd_canary(args)
    if args.corpus:
        return cmd_corpus(args)
    if args.selftest:
        return cmd_selftest(args)
    ap.print_help()
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
