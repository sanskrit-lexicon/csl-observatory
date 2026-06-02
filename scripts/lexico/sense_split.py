#!/usr/bin/env python3
"""R2 — heuristic per-dict sense splitter (full clusters).

Splits dictionary entries into senses using each dict's OWN markers
(deterministic, no LLM; RESEARCH_LAYER_ROADMAP §5.1), gives each sense a
*Sanskrit fingerprint*, and aligns senses across dicts by fingerprint overlap
(A6 = anchor on Sanskrit, no gloss translation).

Four parser families (the §1.2 structural clusters):
  western  — explicit sense markers; fingerprint = {#..#}/<s> SLP1 + <ls> sigla
             ap ∙²N | ap90/ben/bhs {@N@} | pwg <div> N)/a) | wil .²N | mw,mw72,sch,cae lumped
  indigenous — vcp, skd: raw-SLP1 scholastic prose; senses ≈ `iti.`-closed units;
             fingerprint = `…0` authority sigla + "…"-quoted forms + content tokens
  reverse  — ae (ApteES): English-keyed; reverse-indexed by its <s> Sanskrit
             equivalents, so a Sanskrit lemma finds the English senses that gloss it
  index    — acc/vei/mci/inm/snp/ieg: references, not word-senses — OUT OF SCOPE

Homonyms: ALL <L> blocks whose <k1> equals a lemma variant are aggregated
(MW splits a lemma across many blocks).

Modes:
  python sense_split.py             anchor lemmas across all clusters + alignment
  python sense_split.py --corpus    + full-corpus scale pass on SCALE_DICTS
Reads sibling csl-orig; stdlib only.
"""
import os, sys, re, json, itertools, glob
sys.stdout.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
CSLORIG = os.path.join(os.path.dirname(ROOT), 'csl-orig', 'v02')
OUTDIR = os.path.join(ROOT, 'data', 'lexico')

LEMMAS = [('gam', 'gam'), ('dharma', 'Darma'), ('rama', 'rAma'),
          ('iti', 'iti'), ('bodhisattva', 'boDisattva')]
WESTERN = ['mw', 'mw72', 'pwg', 'ap', 'ap90', 'ben', 'sch', 'bhs', 'wil', 'cae']
INDIGENOUS = ['vcp', 'skd']
REVERSE = ['ae']
DICTS = WESTERN + INDIGENOUS
SCALE_DICTS = ['cae', 'ben', 'mci', 'vei']            # smaller dicts for the scale demo
YEARS = {'skd': 1822, 'wil': 1832, 'pwg': 1855, 'ben': 1866, 'vcp': 1873, 'mw72': 1872,
         'ae': 1884, 'ap90': 1890, 'cae': 1891, 'mw': 1899, 'sch': 1928, 'bhs': 1953, 'ap': 1957}

MARKERS = {
    'ap':   re.compile(r'[∙.·]\s*²\s*(\d+)|€\s*(\d+)'),
    'ap90': re.compile(r'\{@\s*-*\s*(\d+)\s*@\}'),
    'ben':  re.compile(r'\{@\s*(\d+)\.\s*@\}'),
    'bhs':  re.compile(r'\(\{@\s*(\d+)\s*@\}\)'),
    'pwg':  re.compile(r'<div n="\d+">\s*((?:\d+|[a-z])\))'),
    'wil':  re.compile(r'\.\s*²\s*(\d+)'),
}
LUMP_DICTS = {'mw', 'mw72', 'sch', 'cae'}
CUT_DICTS = {'ap', 'ap90', 'ben'}
COMP_CUT = re.compile(r'\{@\s*-+\s*Comp|<ab>\s*Comp\b|\bComp\.')

SLP1 = re.compile(r'\{#([^#]*)#\}|<s>([^<]*)</s>')
LS = re.compile(r'<ls[^>]*>([^<]*)</ls>')
SIG = re.compile(r'^\s*([A-Za-zĀĪŪṚṜḶṢŚṆṬḌÑṄṂāīūṛṝḷṣśṇṭḍñṅṃ]+\.)')
SIGLA0 = re.compile(r'\b([a-zA-Zfvr]{1,8}0)\b')              # indigenous authority sigla: jE0, BA0
QUOTED = re.compile(r'“([^”]*)”')
STOP = {'iti', 'ca', 'vA', 'tu', 'hi', 'sa', 'tat', 'tasya', 'tatra', 'asya', 'eva',
        'na', 'naH', 'me', 'syAt', 'yaTA', 'taTA', 'atra', 'api', 'yA', 'yaH', 'saH'}


def variants(lemma):
    v = {lemma}
    v.add(re.sub(r'r([kgGNcjJYwWqQtTdDpPbBmnyrlvzSsh])', r'r\1\1', lemma))
    for base in list(v):
        v.add(base + 'H'); v.add(base + 'M')
    return v


def read_lines(code):
    src = os.path.join(CSLORIG, code, code + '.txt')
    if not os.path.exists(src):
        return None
    with open(src, 'r', encoding='utf-8-sig', errors='replace') as f:
        return [l.rstrip('\n') for l in f]


def all_blocks(lines):
    """Yield (lnum, block_text) for every <L>..</L> entry."""
    i, n = 0, len(lines)
    while i < n:
        if lines[i].startswith('<L>'):
            m = re.match(r'<L>(\S+?)<', lines[i])
            body = [lines[i]]; j = i + 1
            while j < n and not lines[j].startswith('<L>'):
                body.append(lines[j]); j += 1
            yield (m.group(1) if m else '?', '\n'.join(body)); i = j
        else:
            i += 1


def lemma_blocks(lines, lemma):
    keys = {f'<k1>{v}<' for v in variants(lemma)}
    return [(ln, b) for ln, b in all_blocks(lines) if any(k in b.split('\n', 1)[0] for k in keys)]


def fingerprint_western(text, exclude):
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


def fingerprint_indigenous(text, exclude):
    """Indigenous text is raw SLP1; anchor on `…0` sigla + quoted forms + rare content words."""
    toks = set()
    for sig in SIGLA0.findall(text):
        toks.add('sig:' + sig)
    for q in QUOTED.findall(text):
        for w in re.split(r'[\s,;.()]+', q):
            w = w.strip("-˚'’")
            if len(w) >= 3 and w not in exclude and w not in STOP:
                toks.add('s:' + w)
    return toks


def clean(text, limit=140):
    t = re.sub(r'<[^>]+>', '', text)
    t = t.replace('{#', '').replace('#}', '').replace('{%', '').replace('%}', '')
    t = re.sub(r'\{@[^}]*@\}', '', t)
    t = re.sub(r'[Ⓐ-Ⓩ]', '', t)
    t = re.sub(r'\s+', ' ', t).strip(' ,;¦')
    return t[:limit]


def split_western(code, block):
    pos = block.find('¦')
    gloss = block[pos + 1:] if pos >= 0 else block
    if code in CUT_DICTS:
        cm = COMP_CUT.search(gloss)
        if cm:
            gloss = gloss[:cm.start()]
    mk = MARKERS.get(code)
    if mk:
        hits = list(mk.finditer(gloss))
        if hits:
            out = []
            for idx, h in enumerate(hits):
                num = next((g for g in h.groups() if g), str(idx + 1))
                end = hits[idx + 1].start() if idx + 1 < len(hits) else len(gloss)
                out.append((num, gloss[h.end():end]))
            return out, 'marked'
    if code in LUMP_DICTS:
        return [('bundle', gloss)], 'lumped'
    return [('1', gloss)], 'single'


def split_indigenous(block):
    pos = block.find('¦')
    gloss = block[pos + 1:] if pos >= 0 else block
    units = [u for u in re.split(r'iti\s*\.', gloss) if len(u.strip()) > 20]
    if len(units) >= 2:
        return [(str(i + 1), u) for i, u in enumerate(units)], 'iti-units'
    return [('1', gloss)], 'single'


def build_reverse_index(code):
    """ae: map each Sanskrit-equivalent token -> list of (english_hw, sense_no, all_equivs)."""
    lines = read_lines(code)
    if lines is None:
        return {}
    idx = {}
    SENSE = re.compile(r'\{@\s*-*\s*(\d+|[A-Za-z]+)\.?\s*@\}')
    for ln, block in all_blocks(lines):
        hwm = re.search(r'<k1>([^<]*)<', block.split('\n', 1)[0])
        hw = hwm.group(1) if hwm else '?'
        pos = block.find('¦')
        gloss = block[pos + 1:] if pos >= 0 else block
        hits = list(SENSE.finditer(gloss)) or [None]
        for k, h in enumerate(hits):
            seg = gloss if h is None else gloss[h.end():(hits[k + 1].start() if k + 1 < len(hits) else len(gloss))]
            equivs = set()
            for m in re.finditer(r'<s>([^<]*)</s>', seg):
                for w in re.split(r'[\s,;]+', m.group(1)):
                    w = w.strip("-˚'’")
                    if len(w) >= 2:
                        equivs.add(w)
            for w in equivs:
                idx.setdefault(w, []).append({'hw': hw, 'sense': (h.group(1) if h else '1'),
                                              'equivs': sorted(equivs), 'ln': ln})
    return idx


def main():
    os.makedirs(OUTDIR, exist_ok=True)
    summary, jsonl = [], {}
    per_lemma = {}                                    # lemma -> {dict -> [sense recs]}
    ae_index = build_reverse_index('ae')

    for lemma_disp, lemma_slp in LEMMAS:
        per_lemma[lemma_disp] = {}
        exclude = variants(lemma_slp)
        # western + indigenous
        for code in DICTS:
            lines = read_lines(code)
            if lines is None:
                continue
            blocks = lemma_blocks(lines, lemma_slp)
            if not blocks:
                continue
            recs, method = [], 'single'
            for ln, block in blocks:                  # homonym aggregation: ALL blocks
                if code in INDIGENOUS:
                    ss, method = split_indigenous(block)
                    fp_fn = fingerprint_indigenous
                else:
                    ss, method = split_western(code, block)
                    fp_fn = fingerprint_western
                for num, raw in ss:
                    fp = fp_fn(raw, exclude)
                    recs.append({'dict': code, 'lemma': lemma_disp, 'lnum': ln, 'sense': num,
                                 'method': method, 'text': clean(raw), 'fp': sorted(fp)})
            per_lemma[lemma_disp][code] = recs
            jsonl.setdefault(code, []).extend(recs)
            n_marked = len([r for r in recs if r['method'] in ('marked', 'iti-units')])
            summary.append({'lemma': lemma_disp, 'dict': code, 'cluster':
                            'indigenous' if code in INDIGENOUS else 'western',
                            'year': YEARS.get(code), 'n_blocks': len(blocks),
                            'n_senses': len(recs), 'n_marked': n_marked, 'method': method})
        # reverse (ae): English senses whose <s> equivalents include the lemma
        ae_hits = []
        for v in exclude:
            ae_hits += ae_index.get(v, [])
        seen = set(); ae_recs = []
        for h in ae_hits:
            kk = (h['hw'], h['sense'])
            if kk in seen:
                continue
            seen.add(kk)
            fp = {'s:' + w for w in h['equivs'] if w not in exclude}
            ae_recs.append({'dict': 'ae', 'lemma': lemma_disp, 'lnum': h['ln'],
                            'sense': f"{h['hw']}#{h['sense']}", 'method': 'reverse',
                            'text': f"EN '{h['hw']}' = " + ', '.join(h['equivs'][:8]), 'fp': sorted(fp)})
        if ae_recs:
            per_lemma[lemma_disp]['ae'] = ae_recs
            jsonl.setdefault('ae', []).extend(ae_recs)
            summary.append({'lemma': lemma_disp, 'dict': 'ae', 'cluster': 'reverse',
                            'year': YEARS['ae'], 'n_blocks': len(ae_recs),
                            'n_senses': len(ae_recs), 'n_marked': len(ae_recs), 'method': 'reverse'})

    for d, recs in jsonl.items():
        with open(os.path.join(OUTDIR, f'senses_{d}.jsonl'), 'w', encoding='utf-8', newline='\n') as f:
            for r in recs:
                f.write(json.dumps(r, ensure_ascii=False) + '\n')

    # alignment per lemma (cross-cluster, fingerprint Jaccard)
    for lemma_disp, _ in LEMMAS:
        bydict = per_lemma.get(lemma_disp, {})
        flat = [(d, s) for d, sl in bydict.items() for s in sl]
        pairs = []
        for (d1, s1), (d2, s2) in itertools.combinations(flat, 2):
            if s1['dict'] == s2['dict']:
                continue
            f1, f2 = set(s1['fp']), set(s2['fp'])
            inter = f1 & f2
            if not inter:
                continue
            jac = len(inter) / len(f1 | f2)
            pairs.append({'a': f"{s1['dict']}#{s1['sense']}", 'b': f"{s2['dict']}#{s2['sense']}",
                          'jaccard': round(jac, 3), 'shared': sorted(inter)[:6],
                          'a_text': s1['text'][:55], 'b_text': s2['text'][:55]})
        # keep only alignments backed by a STRONG shared anchor: a citation, an
        # indigenous siglum, or a real content word (>=4 SLP1 chars) — drops the
        # short inflectional-ending noise (maH/maM/eka).
        def strong(p):
            return any(t.startswith(('ls:', 'sig:')) or len(t) > 6 for t in p['shared'])
        pairs = [p for p in pairs if strong(p)]
        pairs.sort(key=lambda p: -p['jaccard'])
        with open(os.path.join(OUTDIR, f'r2_align_{lemma_disp}.json'), 'w', encoding='utf-8', newline='\n') as f:
            json.dump({'lemma': lemma_disp, 'sense_counts': {d: len(sl) for d, sl in bydict.items()},
                       'top_aligned': pairs[:30]}, f, ensure_ascii=False, indent=1)

    with open(os.path.join(OUTDIR, 'r2_summary.json'), 'w', encoding='utf-8', newline='\n') as f:
        json.dump(summary, f, ensure_ascii=False, indent=1)

    # ---- report ----
    print("R2 sense splitter — full clusters (homonym-aggregated)\n")
    for lemma_disp, _ in LEMMAS:
        rows = [s for s in summary if s['lemma'] == lemma_disp]
        if not rows:
            continue
        print(f"== {lemma_disp} ==")
        for s in sorted(rows, key=lambda r: r['year'] or 0):
            tag = (f"{s['n_senses']} senses" if s['method'] != 'lumped'
                   else f"LUMPED bundle x{s['n_blocks']} blocks")
            print(f"   {s['year']} {s['dict']:4s} [{s['cluster'][:4]}] {tag} ({s['method']}, {s['n_blocks']} blk)")
        al = json.load(open(os.path.join(OUTDIR, f'r2_align_{lemma_disp}.json'), encoding='utf-8'))
        for p in al['top_aligned'][:3]:
            print(f"     align {p['a']} ~ {p['b']}  J={p['jaccard']}  shared={p['shared'][:4]}")
        print()

    if '--corpus' in sys.argv:
        print("== full-corpus scale pass ==")
        for code in SCALE_DICTS:
            lines = read_lines(code)
            if lines is None:
                print(f"   {code}: no source"); continue
            n_entries = n_senses = 0
            for ln, block in all_blocks(lines):
                n_entries += 1
                if code in INDIGENOUS:
                    ss, _ = split_indigenous(block)
                else:
                    ss, _ = split_western(code, block)
                n_senses += len(ss)
            print(f"   {code:4s}: {n_entries:6d} entries -> {n_senses:6d} senses "
                  f"({n_senses / max(n_entries,1):.2f}/entry)")
    print("wrote senses_<dict>.jsonl, r2_align_<lemma>.json, r2_summary.json")


if __name__ == '__main__':
    main()
