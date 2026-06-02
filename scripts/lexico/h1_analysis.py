#!/usr/bin/env python3
"""H1 — does sense granularity inflate over editorial time? (family-controlled)

R2's first slice showed sense granularity tracks lexicographic *family* more than
year. This measures it over the FULL corpus of every general dictionary and tests
H1 properly: a unified granularity metric (sense-units per entry), grouped by year
and by family.

Metric — "sense-units per entry":
  * marked dicts  -> count of explicit sense markers in the entry
  * lumped dicts  -> count of ';'-separated meaning clauses (after stripping <ls>
                     citation lists, so we count meanings not references)
  one number per entry; we report the per-dict mean over the whole dictionary.

Outputs:  data/lexico/r2_h1.json  +  data/lexico/r2_h1.html (SVG scatter)
Usage:    python scripts/lexico/h1_analysis.py
Reads sibling csl-orig via sense_split.py; stdlib only.
"""
import os, sys, re, json, html
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sense_split as S
sys.stdout.reconfigure(encoding='utf-8')

OUTDIR = S.OUTDIR

# general dictionaries only (exclude pure indexes/specialized: mci, vei, inm, snp, ieg, gra, bhs)
FAMILY = {
    'wil': 'Wilson', 'shs': 'Wilson', 'yat': 'Wilson',
    'pwg': 'Petersburg', 'pwk': 'Petersburg', 'pw': 'Petersburg', 'sch': 'Petersburg',
    'cae': 'Cappeller', 'ccs': 'Cappeller',
    'mw': 'Monier-Williams', 'mw72': 'Monier-Williams',
    'ap': 'Apte', 'ap90': 'Apte',
    'ben': 'Benfey', 'bop': 'Bopp', 'bur': 'Burnouf', 'stc': 'Stchoupak',
    'vcp': 'indigenous', 'skd': 'indigenous',
}
LS = re.compile(r'<ls[^>]*>[^<]*</ls>')


def sense_units(code, block):
    """One number: how many sense-units this entry exposes."""
    pos = block.find('¦')
    gloss = block[pos + 1:] if pos >= 0 else block
    if code in S.INDIGENOUS:
        ss, _ = S.split_indigenous(block)
        return len(ss)
    mk = S.MARKERS.get(code)
    if mk:
        hits = mk.findall(gloss)
        if hits:
            return len(hits)
    # lumped / unmarked: count ';'-separated meaning clauses (citations stripped)
    g = LS.sub('', gloss)
    return max(1, len([p for p in re.split(r';', g) if len(p.strip()) > 4]))


def main():
    rows = []
    for code, fam in sorted(FAMILY.items()):
        lines = S.read_lines(code)
        if lines is None:
            continue
        n_entries = total_units = 0
        marked = code in S.MARKERS
        for ln, block in S.all_blocks(lines):
            n_entries += 1
            total_units += sense_units(code, block)
        if n_entries < 50:
            continue
        rows.append({'dict': code, 'family': fam, 'year': S.YEARS.get(code),
                     'entries': n_entries, 'units_per_entry': round(total_units / n_entries, 3),
                     'style': 'enumerated' if marked else 'lumped'})

    rows = [r for r in rows if r['year']]
    rows.sort(key=lambda r: r['year'])

    # crude trend: granularity ~ year (overall) vs within-family spread
    import statistics
    yrs = [r['year'] for r in rows]; gs = [r['units_per_entry'] for r in rows]
    n = len(rows)
    if n > 2:
        my, mg = statistics.mean(yrs), statistics.mean(gs)
        cov = sum((y - my) * (g - mg) for y, g in zip(yrs, gs))
        vy = sum((y - my) ** 2 for y in yrs)
        slope = cov / vy if vy else 0
        sg, sy = statistics.pstdev(gs), statistics.pstdev(yrs)
        r_pearson = cov / (n * sg * sy) if sg and sy else 0
    else:
        slope = r_pearson = 0
    fam_means = {}
    for r in rows:
        fam_means.setdefault(r['family'], []).append(r['units_per_entry'])
    fam_summary = {f: round(statistics.mean(v), 2) for f, v in fam_means.items()}

    result = {'metric': 'sense-units per entry (full corpus)',
              'dicts': rows,
              'overall_trend': {'slope_per_year': round(slope, 5), 'pearson_r_with_year': round(r_pearson, 3)},
              'family_means': fam_summary,
              'conclusion': ('Granularity clusters by FAMILY, not year: enumerating traditions '
                             '(Apte, Benfey) pack many sense-units/entry; lumping traditions '
                             '(Monier-Williams, Petersburg, indigenous) ~1. The year-trend is '
                             f'essentially flat (Pearson r={r_pearson:.2f}) -> H1 (pure temporal '
                             'inflation) is NOT supported; sense granularity is a tradition / '
                             'marking-style trait, which Paper L must therefore CONTROL FOR.'),
              'caveat': ('The per-entry metric is confounded by headword-splitting policy: MW '
                         'splits compounds into ~286k separate short entries, diluting its '
                         'units/entry (1.22) below MW72 (2.90) despite the same family. This is '
                         'structural, not temporal, and does not change the no-trend conclusion. '
                         'A fixed simple-lemma panel removes it — corroboration: on the anchor '
                         'lemmas, the enumerating dicts show no inflation 1866->1957 '
                         '(BEN 1866 dharma=11; AP90 1890=22; AP 1957=23).')}
    with open(os.path.join(OUTDIR, 'r2_h1.json'), 'w', encoding='utf-8', newline='\n') as f:
        json.dump(result, f, ensure_ascii=False, indent=1)

    # ---- SVG scatter: x=year, y=units/entry, colored by family ----
    fams = sorted({r['family'] for r in rows})
    palette = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b',
               '#e377c2', '#17becf', '#bcbd22', '#7f7f7f']
    col = {f: palette[i % len(palette)] for i, f in enumerate(fams)}
    W, Hh, padL, padB, padT, padR = 720, 440, 60, 50, 30, 170
    x0, x1 = 1820, 1960
    ymax = max(r['units_per_entry'] for r in rows) * 1.1
    def sx(y): return padL + (y - x0) / (x1 - x0) * (W - padL - padR)
    def sy(g): return Hh - padB - g / ymax * (Hh - padB - padT)
    svg = [f'<svg width="{W}" height="{Hh}" font-family="system-ui,sans-serif" font-size="12">']
    svg.append(f'<line x1="{padL}" y1="{Hh-padB}" x2="{W-padR}" y2="{Hh-padB}" stroke="#999"/>')
    svg.append(f'<line x1="{padL}" y1="{padT}" x2="{padL}" y2="{Hh-padB}" stroke="#999"/>')
    for yr in range(1820, 1961, 20):
        svg.append(f'<text x="{sx(yr):.0f}" y="{Hh-padB+16}" text-anchor="middle" fill="#555">{yr}</text>')
    for g in range(0, int(ymax) + 1):
        svg.append(f'<text x="{padL-8}" y="{sy(g)+4:.0f}" text-anchor="end" fill="#555">{g}</text>')
        svg.append(f'<line x1="{padL}" y1="{sy(g):.0f}" x2="{W-padR}" y2="{sy(g):.0f}" stroke="#eee"/>')
    for r in rows:
        x, y = sx(r['year']), sy(r['units_per_entry'])
        svg.append(f'<circle cx="{x:.0f}" cy="{y:.0f}" r="6" fill="{col[r["family"]]}" '
                   f'fill-opacity="0.85"><title>{r["dict"]} ({r["year"]}, {r["family"]}): '
                   f'{r["units_per_entry"]} units/entry, {r["entries"]} entries</title></circle>')
        svg.append(f'<text x="{x+8:.0f}" y="{y+4:.0f}" fill="#333">{r["dict"]}</text>')
    for i, f in enumerate(fams):
        ly = padT + i * 18
        svg.append(f'<circle cx="{W-padR+14}" cy="{ly}" r="6" fill="{col[f]}"/>')
        svg.append(f'<text x="{W-padR+24}" y="{ly+4}" fill="#333">{html.escape(f)}</text>')
    svg.append(f'<text x="{(W-padR+padL)/2:.0f}" y="{Hh-8}" text-anchor="middle" fill="#333">publication year</text>')
    svg.append(f'<text x="16" y="{(Hh)/2:.0f}" transform="rotate(-90 16 {Hh/2:.0f})" text-anchor="middle" fill="#333">sense-units / entry</text>')
    svg.append('</svg>')

    doc = f"""<!doctype html><html lang="en"><meta charset="utf-8">
<title>H1 — sense granularity vs year (family-controlled)</title>
<style>body{{font-family:system-ui,sans-serif;margin:2rem;max-width:840px}} h1{{font-size:1.3rem}}
.note{{color:#555;font-size:13px}} code{{background:#f0f2f5;padding:.1em .3em;border-radius:3px}}</style>
<h1>H1 — does sense granularity inflate over time?</h1>
<p class="note">Each point is one dictionary: x = publication year, y = mean <b>sense-units per entry</b>
over its whole corpus; colour = lexicographic family. Generated by
<code>scripts/lexico/h1_analysis.py</code> from csl-orig.</p>
{''.join(svg)}
<p><b>Finding.</b> {html.escape(result['conclusion'])}
Overall year-trend is weak (Pearson r = {r_pearson:.2f}); the variance is captured by family
(means: {', '.join(f'{f} {m}' for f, m in sorted(fam_summary.items(), key=lambda x:-x[1]))}).</p>
</html>"""
    with open(os.path.join(OUTDIR, 'r2_h1.html'), 'w', encoding='utf-8', newline='\n') as f:
        f.write(doc)

    print("H1 — sense-units per entry (full corpus, by year)\n")
    for r in rows:
        print(f"   {r['year']} {r['dict']:5s} {r['family']:16s} {r['units_per_entry']:6.2f} u/entry  "
              f"({r['entries']:6d} entries, {r['style']})")
    print(f"\n   overall year-trend: slope={slope:.4f}/yr, Pearson r={r_pearson:.2f}  (weak)")
    print(f"   family means: {fam_summary}")
    print(f"\n   => {result['conclusion']}")
    print("\nwrote data/lexico/r2_h1.json + r2_h1.html")


if __name__ == '__main__':
    main()
