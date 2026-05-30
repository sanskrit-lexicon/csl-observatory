#!/usr/bin/env python3
"""MACRO visualization prototype — structural profile of every dictionary.

Samples the first N entries of each canonical csl-orig source and computes
aggregate microstructure metrics (entry size, citation density, etymology /
cross-ref / homonym / grammar-marker rates). Emits:
  * data/lexico/dict_profiles.csv    (raw per-dict metrics)
  * data/lexico/dict_profiles.html   (self-contained heatmap, dicts x metrics)

Audience: researchers (structural fingerprint of each dict; cf.
MICROSTRUCTURE-MACROSTRUCTURE.md §3), dictionary makers (which dicts are
citation-rich vs sparse — where to enrich), students (which dict to consult
for what).

Usage:  python scripts/lexico/macro_profile.py [N]      (default N=3000 entries/dict)
Streams each source (stops after N entries), so even the largest dicts are fast.
"""
import os, sys, re, csv, html
sys.stdout.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
CSLORIG = os.path.join(os.path.dirname(ROOT), 'csl-orig', 'v02')
OUTDIR = os.path.join(ROOT, 'data', 'lexico')
N = int(sys.argv[1]) if len(sys.argv) > 1 else 3000

RX_LS = re.compile(r'<ls>')
RX_ETY = re.compile(r'\[cf\.|βα|Goth|\bLat\.|\bGk\.|\bGr\.|\.E\.|Lith|Slav')
RX_XREF = re.compile(r'\bcf\.|\bq\.v\.|\bsee ')
RX_HOM = re.compile(r'<hom>')
RX_GRAM = re.compile(r'<lex>|\b[mfn]fn?\.|\bind\.')


def sample_entries(path, n):
    """Yield up to n entry texts (each <L>..next <L>) by streaming."""
    cur, count = [], 0
    with open(path, 'r', encoding='utf-8-sig', errors='replace') as f:
        for line in f:
            line = line.rstrip('\n')
            if line.startswith('<L>'):
                if cur:
                    yield '\n'.join(cur)
                    count += 1
                    if count >= n:
                        return
                cur = [line]
            elif cur:
                cur.append(line)
    if cur and count < n:
        yield '\n'.join(cur)


def profile(path, n):
    e = 0
    chars = cites = 0
    ety = xref = hom = gram = withcite = 0
    for entry in sample_entries(path, n):
        e += 1
        chars += len(entry)
        c = len(RX_LS.findall(entry)); cites += c
        if c: withcite += 1
        if RX_ETY.search(entry): ety += 1
        if RX_XREF.search(entry): xref += 1
        if RX_HOM.search(entry): hom += 1
        if RX_GRAM.search(entry): gram += 1
    if e == 0:
        return None
    return {
        'n': e,
        'mean_chars': chars / e,
        'cites_per_entry': cites / e,
        'pct_cited': 100 * withcite / e,
        'pct_etymology': 100 * ety / e,
        'pct_crossref': 100 * xref / e,
        'pct_homonym': 100 * hom / e,
        'pct_gram': 100 * gram / e,
    }


METRICS = ['mean_chars', 'cites_per_entry', 'pct_cited', 'pct_etymology',
           'pct_crossref', 'pct_homonym', 'pct_gram']


def main():
    os.makedirs(OUTDIR, exist_ok=True)
    rows = []
    for d in sorted(os.listdir(CSLORIG)):
        src = os.path.join(CSLORIG, d, d + '.txt')
        if not os.path.exists(src):
            continue
        p = profile(src, N)
        if p and p['n'] >= 50:           # skip near-empty sources
            p['dict'] = d
            rows.append(p)
    if not rows:
        print('no sources profiled'); return

    rows.sort(key=lambda r: -r['mean_chars'])
    with open(os.path.join(OUTDIR, 'dict_profiles.csv'), 'w', encoding='utf-8', newline='') as f:
        w = csv.writer(f)
        w.writerow(['dict', 'n_sampled'] + METRICS)
        for r in rows:
            w.writerow([r['dict'], r['n']] + [f'{r[m]:.2f}' for m in METRICS])

    # per-metric min/max for normalization
    rng = {m: (min(r[m] for r in rows), max(r[m] for r in rows)) for m in METRICS}

    def norm(m, v):
        lo, hi = rng[m]
        return 0.0 if hi == lo else (v - lo) / (hi - lo)

    cell, pad, top, left = 30, 4, 150, 120
    W = left + len(METRICS) * (cell + pad) + 40
    H = top + len(rows) * (cell + pad) + 20
    svg = [f'<svg width="{W}" height="{H}" font-family="system-ui,sans-serif" font-size="12">']
    for j, m in enumerate(METRICS):
        x = left + j * (cell + pad) + cell / 2
        svg.append(f'<text x="{x}" y="{top-8}" transform="rotate(-45 {x} {top-8})" fill="#333">{m}</text>')
    for i, r in enumerate(rows):
        y = top + i * (cell + pad)
        svg.append(f'<text x="{left-8}" y="{y+cell*0.7}" text-anchor="end" fill="#111">{html.escape(r["dict"])}</text>')
        for j, m in enumerate(METRICS):
            x = left + j * (cell + pad)
            t = norm(m, r[m])
            # white -> blue scale
            cr = int(247 - 216 * t); cg = int(249 - 138 * t); cb = int(252 - 33 * t)
            svg.append(f'<rect x="{x}" y="{y}" width="{cell}" height="{cell}" rx="3" fill="rgb({cr},{cg},{cb})">'
                       f'<title>{html.escape(r["dict"])} — {m}: {r[m]:.1f}</title></rect>')
    svg.append('</svg>')

    doc = f"""<!doctype html><html lang="en"><meta charset="utf-8">
<title>Macro: structural profile of CDSL dictionaries</title>
<style>body{{font-family:system-ui,sans-serif;margin:2rem;max-width:1000px}}
h1{{font-size:1.4rem}} .legend{{color:#555;font-size:13px}}</style>
<h1>Structural profile of {len(rows)} CDSL dictionaries (first {N} entries each)</h1>
<p class="legend">Darker = higher (each column min-max normalized across dicts; hover for raw values).
Rows sorted by mean entry size. Generated by <code>scripts/lexico/macro_profile.py</code> from csl-orig.
Heuristic detectors (citation = <code>&lt;ls&gt;</code>; rates are % of sampled entries) — citation-format
differences across dicts mean cross-dict citation numbers are indicative, not exact. See
<a href="../../docs/MICROSTRUCTURE-MACROSTRUCTURE.md">MICROSTRUCTURE-MACROSTRUCTURE.md</a>.</p>
{''.join(svg)}
</html>"""
    with open(os.path.join(OUTDIR, 'dict_profiles.html'), 'w', encoding='utf-8', newline='\n') as f:
        f.write(doc)

    print(f'profiled {len(rows)} dicts (first {N} entries each)')
    print(f'{"dict":8s} {"chars":>7s} {"cite/e":>7s} {"%cited":>7s} {"%etym":>6s} {"%xref":>6s} {"%hom":>6s} {"%gram":>6s}')
    for r in rows:
        print(f'{r["dict"]:8s} {r["mean_chars"]:7.0f} {r["cites_per_entry"]:7.1f} {r["pct_cited"]:7.1f} '
              f'{r["pct_etymology"]:6.1f} {r["pct_crossref"]:6.1f} {r["pct_homonym"]:6.1f} {r["pct_gram"]:6.1f}')
    print('wrote data/lexico/dict_profiles.csv + .html')


if __name__ == '__main__':
    main()
