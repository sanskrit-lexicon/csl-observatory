#!/usr/bin/env python3
"""R2 — heuristic per-dict sense splitter (Western-tagged cluster; first slice).

Splits each dictionary entry into individual senses using that dictionary's OWN
sense markers (deterministic, no LLM — see RESEARCH_LAYER_ROADMAP §5.1), then
gives each sense a *Sanskrit fingerprint* (SLP1 tokens in {#..#}/<s>..</s> plus
<ls> citation sigla) and aligns senses across dictionaries by fingerprint
overlap (A6 = "anchor on Sanskrit", no gloss translation).

Per-dict sense-marker grammars (read off real entries):
  ap    ∙²N (and €N for verb sub-senses)
  ap90  {@N@} / {@--N@}
  ben   {@N.@}            (compound section {@ -- Comp.@} is cut off)
  bhs   ({@N@})
  pwg   <div n="N"> N) / a)         (German {%..%} glosses)
  wil   .²N
  mw,mw72,sch  — unmarked: the gloss is a run-on ';'-list bundle (they LUMP);
                we record the ';'-clause count as a low-confidence proxy.

Outputs (data/lexico/):
  senses_<dict>.jsonl       one record per sense, all lemmas
  r2_align_<lemma>.json     cross-dict sense alignment + H1 sense-count table
  r2_summary.json           sense-count x year per (lemma, dict)  -> H1

Usage:  python scripts/lexico/sense_split.py
Reads sibling csl-orig; stdlib only.
"""
import os, sys, re, json, itertools
sys.stdout.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))                 # csl-observatory/
CSLORIG = os.path.join(os.path.dirname(ROOT), 'csl-orig', 'v02')
OUTDIR = os.path.join(ROOT, 'data', 'lexico')

# anchor lemmas (SLP1): dharma=Darma, rama=rAma, bodhisattva=boDisattva
LEMMAS = [('gam', 'gam'), ('dharma', 'Darma'), ('rama', 'rAma'),
          ('iti', 'iti'), ('bodhisattva', 'boDisattva')]
DICTS = ['mw', 'mw72', 'pwg', 'ap', 'ap90', 'ben', 'sch', 'bhs']
YEARS = {'wil': 1832, 'pwg': 1855, 'mw72': 1872, 'ben': 1866, 'ap90': 1890,
         'mw': 1899, 'sch': 1928, 'bhs': 1953, 'ap': 1957}

MARKERS = {
    'ap':   re.compile(r'[∙.·]\s*²\s*(\d+)|€\s*(\d+)'),
    'ap90': re.compile(r'\{@\s*-*\s*(\d+)\s*@\}'),
    'ben':  re.compile(r'\{@\s*(\d+)\.\s*@\}'),
    'bhs':  re.compile(r'\(\{@\s*(\d+)\s*@\}\)'),
    'pwg':  re.compile(r'<div n="\d+">\s*((?:\d+|[a-z])\))'),
    'wil':  re.compile(r'\.\s*²\s*(\d+)'),
}
LUMP_DICTS = {'mw', 'mw72', 'sch'}                 # no per-sense marker -> lumped
# compound section start (cut main senses here): BEN {@ -- Comp@}, Apte <ab>Comp.</ab> / "Comp."
COMP_CUT = re.compile(r'\{@\s*-+\s*Comp|<ab>\s*Comp\b|\bComp\.')
CUT_DICTS = {'ap', 'ap90', 'ben'}                  # dicts whose entries run into a compound list

SLP1 = re.compile(r'\{#([^#]*)#\}|<s>([^<]*)</s>')
LS = re.compile(r'<ls[^>]*>([^<]*)</ls>')
SIG = re.compile(r'^\s*([A-Za-zĀĪŪṚṜḶṢŚṆṬḌÑṄṂāīūṛṝḷṣśṇṭḍñṅṃ]+\.)')


def variants(lemma):
    v = {lemma}
    v.add(re.sub(r'r([kgGNcjJYwWqQtTdDpPbBmnyrlvzSsh])', r'r\1\1', lemma))
    for base in list(v):
        v.add(base + 'H'); v.add(base + 'M')
    return v


def extract_blocks(path, lemma):
    keys = {f'<k1>{v}<' for v in variants(lemma)}
    with open(path, 'r', encoding='utf-8-sig', errors='replace') as f:
        lines = [l.rstrip('\n') for l in f]
    out, i, n = [], 0, len(lines)
    while i < n:
        if lines[i].startswith('<L>') and any(k in lines[i] for k in keys):
            lnum = re.match(r'<L>(\S+?)<', lines[i])
            body = [lines[i]]; j = i + 1
            while j < n and not lines[j].startswith('<L>'):
                body.append(lines[j]); j += 1
            out.append((lnum.group(1) if lnum else '?', '\n'.join(body))); i = j
        else:
            i += 1
    return out


def fingerprint(text, exclude=frozenset()):
    """SLP1 tokens (from {#..#}/<s>) + <ls> citation sigla. The headword's own
    variants are excluded — they appear in every sense and don't discriminate."""
    toks = set()
    for m in SLP1.finditer(text):
        s = m.group(1) or m.group(2) or ''
        for w in re.split(r'[\s,;.()<>/]+', s):
            w = w.strip("-˚'’")
            if len(w) >= 2 and w not in exclude:
                toks.add('s:' + w)
    for m in LS.finditer(text):
        sm = SIG.match(m.group(1))
        if sm:
            toks.add('ls:' + sm.group(1))
    return toks


def clean(text, limit=140):
    t = re.sub(r'<[^>]+>', '', text)
    t = t.replace('{#', '').replace('#}', '').replace('{%', '').replace('%}', '')
    t = re.sub(r'\{@[^}]*@\}', '', t)
    t = re.sub(r'\s+', ' ', t).strip(' ,;¦')
    return t[:limit]


def split_senses(code, block):
    """Return [(sense_label, raw_text)] for one <L> block."""
    pos = block.find('¦')
    gloss = block[pos + 1:] if pos >= 0 else block
    if code in CUT_DICTS:                    # drop the compound section (keep head-senses)
        cm = COMP_CUT.search(gloss)
        if cm:
            gloss = gloss[:cm.start()]
    mk = MARKERS.get(code)
    if mk:
        hits = list(mk.finditer(gloss))
        if hits:
            senses = []
            for idx, h in enumerate(hits):
                num = next((g for g in h.groups() if g), str(idx + 1))
                end = hits[idx + 1].start() if idx + 1 < len(hits) else len(gloss)
                senses.append((num, gloss[h.end():end]))
            return senses, 'marked'
    if code in LUMP_DICTS:
        # MW-family lumps senses into one run-on gloss with no per-sense markers.
        # That IS the finding — keep it as a single bundle; record clause granularity
        # separately (see gloss_clauses in main) rather than faking a sense count.
        return [('bundle', gloss)], 'lumped'
    return [('1', gloss)], 'single'


def main():
    os.makedirs(OUTDIR, exist_ok=True)
    summary = []                            # (lemma, dict, year, n_senses, method)
    per_lemma_senses = {}                   # lemma -> {dict -> [sense dict]}
    jsonl = {d: [] for d in DICTS}

    for lemma_disp, lemma_slp in LEMMAS:
        per_lemma_senses[lemma_disp] = {}
        for code in DICTS:
            src = os.path.join(CSLORIG, code, code + '.txt')
            if not os.path.exists(src):
                continue
            blocks = extract_blocks(src, lemma_slp)
            if not blocks:
                continue
            exclude = variants(lemma_slp)
            senses_all, method, clauses = [], 'single', None
            for lnum, block in blocks[:1]:          # primary entry (first homonym block)
                ss, method = split_senses(code, block)
                for num, raw in ss:
                    fp = fingerprint(raw, exclude)
                    if method == 'lumped':          # implicit-sense proxy: ';'-separated sub-meanings
                        clauses = len([p for p in re.split(r';', clean(raw, 100000)) if len(p.strip()) > 3])
                    rec = {'dict': code, 'lemma': lemma_disp, 'lnum': lnum,
                           'sense': num, 'method': method, 'text': clean(raw),
                           'slp1': sorted(t[2:] for t in fp if t.startswith('s:')),
                           'cites': sorted(t[3:] for t in fp if t.startswith('ls:')),
                           'fp': sorted(fp)}
                    senses_all.append(rec)
                    jsonl[code].append(rec)
            per_lemma_senses[lemma_disp][code] = senses_all
            summary.append({'lemma': lemma_disp, 'dict': code, 'year': YEARS.get(code),
                            'n_senses': len(senses_all), 'method': method, 'clauses': clauses})

    # ---- write per-dict JSONL ----
    for d in DICTS:
        if jsonl[d]:
            with open(os.path.join(OUTDIR, f'senses_{d}.jsonl'), 'w', encoding='utf-8', newline='\n') as f:
                for rec in jsonl[d]:
                    f.write(json.dumps(rec, ensure_ascii=False) + '\n')

    # ---- alignment per lemma (Sanskrit-fingerprint Jaccard across dicts) ----
    for lemma_disp, _ in LEMMAS:
        bydict = per_lemma_senses.get(lemma_disp, {})
        pairs = []
        for (d1, s1), (d2, s2) in itertools.combinations(
                [(d, s) for d, sl in bydict.items() for s in sl], 2):
            if s1['dict'] == s2['dict']:
                continue
            f1, f2 = set(s1['fp']), set(s2['fp'])
            if not f1 or not f2:
                continue
            inter = f1 & f2
            if not inter:
                continue
            jac = len(inter) / len(f1 | f2)
            pairs.append({'a': f"{s1['dict']}#{s1['sense']}", 'b': f"{s2['dict']}#{s2['sense']}",
                          'jaccard': round(jac, 3), 'shared': sorted(inter),
                          'a_text': s1['text'][:60], 'b_text': s2['text'][:60]})
        pairs.sort(key=lambda p: -p['jaccard'])
        align = {'lemma': lemma_disp,
                 'sense_counts': {d: len(sl) for d, sl in bydict.items()},
                 'top_aligned': pairs[:25]}
        with open(os.path.join(OUTDIR, f'r2_align_{lemma_disp}.json'), 'w', encoding='utf-8', newline='\n') as f:
            json.dump(align, f, ensure_ascii=False, indent=1)

    with open(os.path.join(OUTDIR, 'r2_summary.json'), 'w', encoding='utf-8', newline='\n') as f:
        json.dump(summary, f, ensure_ascii=False, indent=1)

    # ---- console report ----
    print("R2 sense splitter — first slice (Western-tagged cluster)\n")
    for lemma_disp, _ in LEMMAS:
        rows = [s for s in summary if s['lemma'] == lemma_disp]
        if not rows:
            continue
        print(f"== {lemma_disp} ==  (explicit senses by dict, ordered by year — H1 signal)")
        for s in sorted(rows, key=lambda r: r['year'] or 0):
            if s['method'] == 'lumped':
                tag = f"LUMPED (one run-on gloss, ~{s['clauses']} clauses)"
            else:
                tag = f"{s['n_senses']:3d} explicit senses [{s['method']}]"
            print(f"   {s['year']}  {s['dict']:5s}  {tag}")
        ap = os.path.join(OUTDIR, f'r2_align_{lemma_disp}.json')
        al = json.load(open(ap, encoding='utf-8'))
        if al['top_aligned']:
            best = al['top_aligned'][0]
            print(f"   top cross-dict alignment: {best['a']} ~ {best['b']}  "
                  f"(J={best['jaccard']}, shared={best['shared'][:4]})")
        print()
    print(f"wrote senses_<dict>.jsonl, r2_align_<lemma>.json, r2_summary.json to data/lexico/")


if __name__ == '__main__':
    main()
