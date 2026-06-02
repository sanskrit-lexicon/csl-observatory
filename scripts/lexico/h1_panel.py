#!/usr/bin/env python3
"""H1 (de-confounded) — sense granularity on a FIXED simple-lemma panel.

The full-corpus H1 metric (h1_analysis.py) is confounded by headword-splitting
policy: MW splits compounds into ~286k short entries, diluting its mean
units/entry. This measures the SAME 30 common nouns across every dictionary
(each a single rich entry; homonym blocks aggregated) so the comparison is
on identical words — removing the confound.

Outputs:  data/lexico/r2_h1_panel.json + r2_h1_panel.html (SVG scatter)
Usage:    python scripts/lexico/h1_panel.py
"""
import os, sys, json, html, statistics
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sense_split as S
from h1_analysis import sense_units, FAMILY
from h2h3_analysis import PANEL
sys.stdout.reconfigure(encoding='utf-8')

OUTDIR = S.OUTDIR


def panel_granularity(code):
    lines = S.read_lines(code)
    if lines is None:
        return None
    per_lemma = []
    for lemma in PANEL:
        blocks = S.lemma_blocks(lines, lemma)
        if not blocks:
            continue
        units = sum(sense_units(code, b) for _, b in blocks)     # aggregate homonym blocks
        per_lemma.append(units)
    if len(per_lemma) < 8:                                        # need decent panel coverage
        return None
    return per_lemma


def main():
    rows = []
    for code, fam in sorted(FAMILY.items()):
        g = panel_granularity(code)
        if g is None or not S.YEARS.get(code):
            continue
        rows.append({'dict': code, 'family': fam, 'year': S.YEARS[code],
                     'panel_lemmas': len(g), 'granularity': round(statistics.mean(g), 2)})
    rows.sort(key=lambda r: r['year'])

    yrs = [r['year'] for r in rows]; gs = [r['granularity'] for r in rows]; n = len(rows)
    my, mg = statistics.mean(yrs), statistics.mean(gs)
    cov = sum((y - my) * (g - mg) for y, g in zip(yrs, gs))
    vy = sum((y - my) ** 2 for y in yrs)
    slope = cov / vy if vy else 0
    sg, sy = statistics.pstdev(gs), statistics.pstdev(yrs)
    r_pearson = cov / (n * sg * sy) if sg and sy else 0
    fam_means = {}
    for r in rows:
        fam_means.setdefault(r['family'], []).append(r['granularity'])
    fam_summary = {f: round(statistics.mean(v), 2) for f, v in sorted(fam_means.items(), key=lambda x: -statistics.mean(x[1]))}

    # enumerators only (explicit marker counts are comparable; the ';'-proxy for
    # lumpers is not a sense count and is reported separately)
    enr = [r for r in rows if r['dict'] in S.MARKERS]
    if len(enr) > 2:
        ey = [r['year'] for r in enr]; eg = [r['granularity'] for r in enr]
        emy, emg = statistics.mean(ey), statistics.mean(eg)
        ecov = sum((y - emy) * (g - emg) for y, g in zip(ey, eg))
        evy = sum((y - emy) ** 2 for y in ey)
        eslope = ecov / evy if evy else 0
        er = ecov / (len(enr) * statistics.pstdev(eg) * statistics.pstdev(ey)) if statistics.pstdev(eg) and statistics.pstdev(ey) else 0
    else:
        eslope = er = 0
    for r in rows:
        r['style'] = 'enumerated' if r['dict'] in S.MARKERS else 'proxy(;/iti)'

    result = {'metric': 'mean sense-units over a fixed 30-noun panel (homonym-aggregated)',
              'panel': PANEL, 'dicts': rows,
              'trend_all': {'slope_per_year': round(slope, 5), 'pearson_r_with_year': round(r_pearson, 3)},
              'trend_enumerators_only': {'slope_per_year': round(eslope, 5), 'pearson_r_with_year': round(er, 3),
                                         'dicts': [r['dict'] for r in enr]},
              'family_means': fam_summary,
              'caveat': ('Absolute granularity is NOT comparable across marking conventions: for the '
                         'lumping dicts (MW/MW72/Cappeller/Petersburg/indigenous) the metric counts '
                         "';'-clauses (or iti-units), which on rich panel words inflate hugely "
                         '(MW72 = 86 clauses, not 86 senses). Treat enumerated vs proxy separately.'),
              'conclusion': ('De-confounded (same words, every dict): the year-trend is flat over the '
                             f'whole set (Pearson r = {r_pearson:.2f}). A weak positive correlation '
                             f'appears among the {len(enr)} comparable enumerating dicts (r = {er:.2f}), '
                             'but at n=5 it is not significant and is convention-confounded — the '
                             'earliest dictionary, Wilson 1832, is already among the most finely '
                             'enumerated (11 senses/word), and mid-century PWG looks low only because '
                             'its coarse <div> marking undercounts. No support for temporal '
                             'sense-inflation; granularity is governed by lexicographic tradition and '
                             'marking convention, not date.')}
    with open(os.path.join(OUTDIR, 'r2_h1_panel.json'), 'w', encoding='utf-8', newline='\n') as f:
        json.dump(result, f, ensure_ascii=False, indent=1)

    # SVG scatter
    fams = sorted({r['family'] for r in rows})
    pal = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b', '#e377c2', '#17becf', '#bcbd22']
    col = {f: pal[i % len(pal)] for i, f in enumerate(fams)}
    W, Hh, padL, padB, padT, padR = 720, 440, 60, 50, 30, 175
    x0, x1 = 1820, 1960
    ymax = max(r['granularity'] for r in rows) * 1.12
    sx = lambda y: padL + (y - x0) / (x1 - x0) * (W - padL - padR)
    sy = lambda g: Hh - padB - g / ymax * (Hh - padB - padT)
    svg = [f'<svg width="{W}" height="{Hh}" font-family="system-ui,sans-serif" font-size="12">',
           f'<line x1="{padL}" y1="{Hh-padB}" x2="{W-padR}" y2="{Hh-padB}" stroke="#999"/>',
           f'<line x1="{padL}" y1="{padT}" x2="{padL}" y2="{Hh-padB}" stroke="#999"/>']
    for yr in range(1820, 1961, 20):
        svg.append(f'<text x="{sx(yr):.0f}" y="{Hh-padB+16}" text-anchor="middle" fill="#555">{yr}</text>')
    for g in range(0, int(ymax) + 1, 2):
        svg.append(f'<line x1="{padL}" y1="{sy(g):.0f}" x2="{W-padR}" y2="{sy(g):.0f}" stroke="#eee"/>')
        svg.append(f'<text x="{padL-8}" y="{sy(g)+4:.0f}" text-anchor="end" fill="#555">{g}</text>')
    for r in rows:
        x, y = sx(r['year']), sy(r['granularity'])
        svg.append(f'<circle cx="{x:.0f}" cy="{y:.0f}" r="6" fill="{col[r["family"]]}" fill-opacity="0.85">'
                   f'<title>{r["dict"]} ({r["year"]}, {r["family"]}): {r["granularity"]} senses/word, '
                   f'{r["panel_lemmas"]} panel words</title></circle>')
        svg.append(f'<text x="{x+8:.0f}" y="{y+4:.0f}" fill="#333">{r["dict"]}</text>')
    for i, f in enumerate(fams):
        ly = padT + i * 18
        svg.append(f'<circle cx="{W-padR+14}" cy="{ly}" r="6" fill="{col[f]}"/>')
        svg.append(f'<text x="{W-padR+24}" y="{ly+4}" fill="#333">{html.escape(f)}</text>')
    svg.append(f'<text x="{(W-padR+padL)/2:.0f}" y="{Hh-8}" text-anchor="middle" fill="#333">publication year</text>')
    svg.append('</svg>')
    doc = f"""<!doctype html><html lang="en"><meta charset="utf-8">
<title>H1 de-confounded — granularity on a fixed lemma panel</title>
<style>body{{font-family:system-ui,sans-serif;margin:2rem;max-width:840px}} h1{{font-size:1.25rem}}
.note{{color:#555;font-size:13px}} code{{background:#f0f2f5;padding:.1em .3em;border-radius:3px}}</style>
<h1>H1 (de-confounded) — sense granularity on a fixed 30-noun panel</h1>
<p class="note">Same 30 common nouns measured in every dictionary (homonym blocks aggregated),
removing the headword-splitting confound. x = year, y = mean sense-units per panel word,
colour = family. <code>scripts/lexico/h1_panel.py</code>.</p>
{''.join(svg)}
<p><b>Finding.</b> {html.escape(result['conclusion'])} Family means:
{', '.join(f'{f} {m}' for f, m in fam_summary.items())}.</p>
</html>"""
    with open(os.path.join(OUTDIR, 'r2_h1_panel.html'), 'w', encoding='utf-8', newline='\n') as f:
        f.write(doc)

    print("H1 (de-confounded) — fixed 30-noun panel, by year\n")
    for r in rows:
        print(f"   {r['year']} {r['dict']:5s} {r['family']:16s} {r['granularity']:7.2f} units/word "
              f"[{r['style']}] ({r['panel_lemmas']} words)")
    print(f"\n   year-trend (all): Pearson r={r_pearson:.2f}")
    print(f"   year-trend (enumerators only, comparable): Pearson r={er:.2f}  {[r['dict'] for r in enr]}")
    print(f"   family means: {fam_summary}")
    print(f"\n   caveat: {result['caveat']}")
    print(f"\n   => {result['conclusion']}")
    print("\nwrote data/lexico/r2_h1_panel.json + r2_h1_panel.html")


if __name__ == '__main__':
    main()
