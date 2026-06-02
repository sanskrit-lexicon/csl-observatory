#!/usr/bin/env python3
"""R1/R2 — interactive sense-alignment explorer (self-contained HTML).

Reads the R2 outputs (data/lexico/senses_<dict>.jsonl + r2_align_<lemma>.json)
and emits a single self-contained, client-side page: pick a lemma -> see its
senses across every dictionary (coloured by cluster) and the Sanskrit-anchored
cross-dictionary sense alignments, with cross-cluster matches highlighted.

No build step, no dependencies, no network — the data is embedded inline.
Linked from the dashboard's Lexicography page (the "main dashboard page"
hosting decision). Productizes the micro/sense layer for students + makers.

Usage:  python scripts/lexico/r2_explorer.py   (run after sense_split.py)
Output: data/lexico/r2_explorer.html
"""
import os, sys, re, json, html
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sense_split as S
sys.stdout.reconfigure(encoding='utf-8')

OUTDIR = S.OUTDIR
LABEL = {'mw': 'MW 1899', 'mw72': 'MW 1872', 'pwg': 'PWG 1855', 'pwk': 'PWK',
         'ap': 'Apte 1957', 'ap90': 'Apte 1890', 'ben': 'Benfey 1866', 'sch': 'Schmidt 1928',
         'bhs': 'Edgerton BHS 1953', 'wil': 'Wilson 1832', 'cae': 'Cappeller 1891',
         'vcp': 'Vācaspatya 1873', 'skd': 'Śabdakalpadruma 1822', 'ae': 'Apte EN→SA 1884'}
CAP = 30  # max senses per dict per lemma shown


def cluster_of(code):
    if code in S.INDIGENOUS: return 'indigenous'
    if code in S.REVERSE: return 'reverse'
    return 'western'


def main():
    data = {}
    for lemma_disp, _ in S.LEMMAS:
        ap = os.path.join(OUTDIR, f'r2_align_{lemma_disp}.json')
        if not os.path.exists(ap):
            continue
        align = json.load(open(ap, encoding='utf-8'))
        senses = {}
        for d in align['sense_counts']:
            p = os.path.join(OUTDIR, f'senses_{d}.jsonl')
            if not os.path.exists(p):
                continue
            recs = [json.loads(l) for l in open(p, encoding='utf-8') if l.strip()]
            recs = [r for r in recs if r['lemma'] == lemma_disp][:CAP]
            if recs:
                senses[d] = [{'sense': r['sense'], 'text': r['text'], 'cluster': cluster_of(d),
                              'n_anchor': len([t for t in r['fp'] if t.startswith(('ls:', 'sig:', 's:'))])}
                             for r in recs]
        aligns = []
        for p in align['top_aligned'][:30]:
            da = p['a'].split('#')[0]; db = p['b'].split('#')[0]
            aligns.append({'a': p['a'], 'b': p['b'], 'j': p['jaccard'], 'shared': p['shared'],
                           'cross': cluster_of(da) != cluster_of(db)})
        data[lemma_disp] = {'senses': senses, 'aligns': aligns}

    payload = json.dumps(data, ensure_ascii=False)
    labels = json.dumps(LABEL, ensure_ascii=False)
    lemmas = [l for l, _ in S.LEMMAS if l in data]

    doc = """<!doctype html><html lang="en"><meta charset="utf-8">
<title>Sanskrit sense-alignment explorer</title>
<style>
 body{font-family:system-ui,sans-serif;margin:1.5rem;max-width:1100px;color:#1b1b1b}
 h1{font-size:1.3rem} h2{font-size:1rem;margin:1.2rem 0 .4rem;color:#444}
 .controls{margin:.5rem 0 1rem} select{font-size:1rem;padding:.25rem}
 .grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(250px,1fr));gap:.6rem}
 .dict{border:1px solid #e3e6ea;border-radius:7px;padding:.5rem .6rem;font-size:12px}
 .dict h3{margin:0 0 .3rem;font-size:13px;display:flex;justify-content:space-between}
 .pill{font-size:10px;padding:.05em .4em;border-radius:8px;color:#fff}
 .western{background:#1f77b4}.indigenous{background:#2ca02c}.reverse{background:#9467bd}
 .sense{margin:.15rem 0;padding-left:1.3em;text-indent:-1.3em}
 .num{color:#888;font-weight:600;margin-right:.3em}
 table{border-collapse:collapse;font-size:12px;width:100%}
 td,th{border-bottom:1px solid #eee;padding:.3rem .4rem;text-align:left;vertical-align:top}
 .chip{display:inline-block;background:#eef1f4;border-radius:6px;padding:.05em .4em;margin:1px;font-size:11px}
 .chip.cite{background:#fde9c8}.chip.sig{background:#d7f0d7}
 .cross{background:#fff7e6} .crosslbl{color:#b9770e;font-weight:600;font-size:10px}
 .note{color:#666;font-size:12.5px}
</style>
<h1>Sanskrit sense-alignment explorer</h1>
<p class="note">Pick a headword. Each card is one dictionary's senses (colour = tradition cluster).
Below, the <b>Sanskrit-anchored cross-dictionary alignments</b>: two senses link when they share
Sanskrit material (SLP1 forms <span class="chip">s:…</span>, citations <span class="chip cite">ls:…</span>,
or indigenous sigla <span class="chip sig">sig:…</span>) — <b>no translation used</b>.
<span class="crosslbl">Highlighted</span> rows align senses <i>across</i> traditions/languages.
Built by <code>scripts/lexico/r2_explorer.py</code> from R2 data
(<a href="https://github.com/sanskrit-lexicon/csl-observatory/blob/main/docs/R2_FINDINGS.md">R2_FINDINGS.md</a>).</p>
<div class="controls">Headword: <select id="sel"></select></div>
<h2>Senses by dictionary</h2><div class="grid" id="senses"></div>
<h2>Cross-dictionary sense alignments (Sanskrit-anchored)</h2><div id="aligns"></div>
<script>
const DATA = %PAYLOAD%; const LABEL = %LABELS%;
const sel = document.getElementById('sel');
%LEMMAS%.forEach(l => { const o=document.createElement('option'); o.value=l; o.textContent=l; sel.appendChild(o); });
function esc(s){const d=document.createElement('div');d.textContent=s;return d.innerHTML;}
function chip(t){let c='chip';if(t.startsWith('ls:'))c+=' cite';else if(t.startsWith('sig:'))c+=' sig';
  return '<span class="'+c+'">'+esc(t)+'</span>';}
function render(lemma){
  const d=DATA[lemma]; const S=document.getElementById('senses'); S.innerHTML='';
  const order=Object.keys(d.senses).sort((a,b)=>(LABEL[a]||a).slice(-4).localeCompare((LABEL[b]||b).slice(-4)));
  for(const code of order){
    const recs=d.senses[code]; const cl=recs[0].cluster;
    let h='<div class="dict"><h3>'+esc(LABEL[code]||code)+
          ' <span class="pill '+cl+'">'+cl+'</span></h3>';
    for(const r of recs) h+='<div class="sense"><span class="num">'+esc(String(r.sense))+'</span>'+esc(r.text||'')+'</div>';
    h+='</div>'; S.insertAdjacentHTML('beforeend',h);
  }
  const A=document.getElementById('aligns');
  if(!d.aligns.length){A.innerHTML='<p class="note">No fingerprint-backed alignments for this lemma.</p>';return;}
  let t='<table><tr><th>sense A</th><th>sense B</th><th>Jaccard</th><th>shared Sanskrit anchors</th></tr>';
  for(const p of d.aligns){
    t+='<tr class="'+(p.cross?'cross':'')+'"><td>'+esc(p.a)+(p.cross?' <span class="crosslbl">cross-tradition</span>':'')+
       '</td><td>'+esc(p.b)+'</td><td>'+p.j+'</td><td>'+p.shared.map(chip).join(' ')+'</td></tr>';
  }
  A.innerHTML=t+'</table>';
}
sel.addEventListener('change',()=>render(sel.value));
render(sel.value=%FIRST%);
</script>
</html>"""
    doc = (doc.replace('%PAYLOAD%', payload).replace('%LABELS%', labels)
              .replace('%LEMMAS%', json.dumps(lemmas)).replace('%FIRST%', json.dumps(lemmas[0] if lemmas else '')))
    out = os.path.join(OUTDIR, 'r2_explorer.html')
    with open(out, 'w', encoding='utf-8', newline='\n') as f:
        f.write(doc)
    print(f"wrote data/lexico/r2_explorer.html  ({len(doc)} bytes, {len(lemmas)} lemmas)")
    for l in lemmas:
        print(f"  {l}: {len(data[l]['senses'])} dicts, {len(data[l]['aligns'])} alignments")


if __name__ == '__main__':
    main()
