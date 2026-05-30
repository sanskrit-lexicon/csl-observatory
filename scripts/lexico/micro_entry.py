#!/usr/bin/env python3
"""MICRO visualization prototype — one lemma across many dictionaries.

For a given headword, extracts that entry from each dictionary's canonical
csl-orig source, detects which microstructure features are present, and emits:
  * data/lexico/micro_<lemma>.json   (entries + detected features)
  * data/lexico/micro_<lemma>.html   (self-contained: feature heatmap +
                                       side-by-side entry text)

Audience: students (see one word across all dicts at a glance), dictionary
makers (spot which dicts carry which structure), researchers (microstructure
comparison, cf. MICROSTRUCTURE-MACROSTRUCTURE.md §1).

Usage:  python scripts/lexico/micro_entry.py [lemma]    (default: gam)
Reads sibling csl-orig; no network, no deps beyond the stdlib.
"""
import os, sys, re, json, html
sys.stdout.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))          # csl-observatory/
CSLORIG = os.path.join(os.path.dirname(ROOT), 'csl-orig', 'v02')
OUTDIR = os.path.join(ROOT, 'data', 'lexico')

LEMMA = sys.argv[1] if len(sys.argv) > 1 else 'gam'

# dict code -> display label (subset with rich entries; skipped if source/entry absent)
DICTS = [
    ('mw', 'MW 1899'), ('mw72', 'MW 1872'), ('ap', 'Apte'), ('ap90', 'Apte 1890'),
    ('pwg', 'PWG (Böhtlingk-Roth)'), ('pwk', 'PWK'), ('wil', 'Wilson'),
    ('ben', 'Benfey'), ('bop', 'Bopp'), ('gra', 'Grassmann'), ('vcp', 'Vācaspatya'),
    ('skd', 'Śabdakalpadruma'),
]

# microstructure feature -> regex on the entry text
FEATURES = [
    ('homonym',      re.compile(r'<hom>')),
    ('verb class',   re.compile(r'\bcl\.')),
    ('citation',     re.compile(r'<ls>')),
    ('causative',    re.compile(r'\bCaus\.')),
    ('desiderative', re.compile(r'\bDesid\.')),
    ('intens./freq.',re.compile(r'\bInten|\bFreq')),
    ('passive',      re.compile(r'\bPass\.')),
    ('etymology',    re.compile(r'\[cf\.|βα|Goth|\bLat\.|\bGk\.|\bGr\.|\.E\.|Lith|Slav')),
    ('cross-ref',    re.compile(r'\bcf\.|\bq\.v\.|\bsee ')),
    ('gram. marker', re.compile(r'<lex>|\b[mfn]fn?\.|\bind\.')),
    ('preverb sub',  re.compile(r'(?:^|\n)\s*[—-]\s*(?:anu|aBi|ati|vi|upa|pra|sam|aDi|api|apa)')),
    ('info tag',     re.compile(r'<info')),
]


def extract_entry(path, lemma):
    """Return the first <L> entry whose <k1> equals lemma, as raw text (or None)."""
    key = f'<k1>{lemma}<'
    with open(path, 'r', encoding='utf-8-sig', errors='replace') as f:
        lines = [l.rstrip('\n') for l in f]
    start = None
    for i, line in enumerate(lines):
        if line.startswith('<L>') and key in line:
            start = i
            break
    if start is None:
        return None
    body = [lines[start]]
    for line in lines[start + 1:]:
        if line.startswith('<L>'):
            break
        body.append(line)
    return '\n'.join(body)


def main():
    os.makedirs(OUTDIR, exist_ok=True)
    rows = []
    for code, label in DICTS:
        src = os.path.join(CSLORIG, code, code + '.txt')
        if not os.path.exists(src):
            continue
        entry = extract_entry(src, LEMMA)
        if not entry:
            continue
        feats = {name: bool(rx.search(entry)) for name, rx in FEATURES}
        rows.append({
            'dict': code, 'label': label, 'chars': len(entry),
            'citations': len(re.findall(r'<ls>', entry)),
            'features': feats, 'entry': entry,
        })
    if not rows:
        print(f'no "{LEMMA}" entry found in any source'); return

    with open(os.path.join(OUTDIR, f'micro_{LEMMA}.json'), 'w', encoding='utf-8', newline='\n') as f:
        json.dump({'lemma': LEMMA, 'dicts': rows}, f, ensure_ascii=False, indent=1)

    # ---- self-contained HTML (inline SVG heatmap + entries) ----
    fnames = [n for n, _ in FEATURES]
    cell, pad, top, left = 26, 4, 130, 200
    W = left + len(fnames) * (cell + pad) + 40
    H = top + len(rows) * (cell + pad) + 20
    svg = [f'<svg width="{W}" height="{H}" font-family="system-ui,sans-serif" font-size="12">']
    for j, fn in enumerate(fnames):
        x = left + j * (cell + pad) + cell / 2
        svg.append(f'<text x="{x}" y="{top-8}" transform="rotate(-45 {x} {top-8})" fill="#333">{html.escape(fn)}</text>')
    maxc = max(r['chars'] for r in rows)
    for i, r in enumerate(rows):
        y = top + i * (cell + pad)
        svg.append(f'<text x="{left-10}" y="{y+cell*0.7}" text-anchor="end" fill="#111">{html.escape(r["label"])}</text>')
        for j, fn in enumerate(fnames):
            x = left + j * (cell + pad)
            on = r['features'][fn]
            color = '#1f6feb' if on else '#eef1f4'
            svg.append(f'<rect x="{x}" y="{y}" width="{cell}" height="{cell}" rx="3" fill="{color}"><title>{html.escape(r["label"])} — {html.escape(fn)}: {"yes" if on else "no"}</title></rect>')
        # entry-size bar to the right
        bx = left + len(fnames) * (cell + pad) + 6
        bw = 30 * r['chars'] / maxc
        svg.append(f'<rect x="{bx}" y="{y+4}" width="{bw:.0f}" height="{cell-8}" fill="#999"><title>{r["chars"]} chars, {r["citations"]} citations</title></rect>')
    svg.append('</svg>')

    entries_html = []
    for r in rows:
        entries_html.append(
            f'<details><summary><b>{html.escape(r["label"])}</b> '
            f'({r["chars"]} chars, {r["citations"]} citations)</summary>'
            f'<pre>{html.escape(r["entry"])}</pre></details>')

    doc = f"""<!doctype html><html lang="en"><meta charset="utf-8">
<title>Micro: {html.escape(LEMMA)} across dictionaries</title>
<style>body{{font-family:system-ui,sans-serif;margin:2rem;max-width:1000px}}
pre{{white-space:pre-wrap;background:#f6f8fa;padding:.6rem;border-radius:6px;font-size:12px}}
summary{{cursor:pointer;margin:.2rem 0}} h1{{font-size:1.4rem}} .legend{{color:#555;font-size:13px}}</style>
<h1>Microstructure of <i>{html.escape(LEMMA)}</i> across {len(rows)} dictionaries</h1>
<p class="legend">Blue = feature present in that dictionary's <code>{html.escape(LEMMA)}</code> entry; grey bar = relative entry size.
Generated by <code>scripts/lexico/micro_entry.py</code> from csl-orig. See
<a href="../../docs/MICROSTRUCTURE-MACROSTRUCTURE.md">MICROSTRUCTURE-MACROSTRUCTURE.md</a>.</p>
{''.join(svg)}
<h2>Entries</h2>
{''.join(entries_html)}
</html>"""
    with open(os.path.join(OUTDIR, f'micro_{LEMMA}.html'), 'w', encoding='utf-8', newline='\n') as f:
        f.write(doc)

    print(f'{LEMMA}: {len(rows)} dicts')
    for r in rows:
        present = [n for n in fnames if r['features'][n]]
        print(f'  {r["dict"]:5s} {r["chars"]:6d} chars  {r["citations"]:3d} cites  feats: {", ".join(present)}')
    print(f'wrote data/lexico/micro_{LEMMA}.json + .html')


if __name__ == '__main__':
    main()
