#!/usr/bin/env python3
"""obs_t_second_sheet.py — blind second-annotator review sheet over the OBS-T
gold sample (H5312).

Consumes the ALREADY-BLIND input validation/gold_sample_blind.json (built by
validation/build_blind_sample.py: labels stripped, rows shuffled with the
pre-registered seed 20260721) and renders a self-contained HTML annotation
sheet validation/second_annotator_sheet.html.

The sheet covers EVERY gold row and presents the correction evidence plus BOTH
typology axes as annotation targets:

  axis A (location)   headword / grammar / citation / sense / crossref /
                      meta / markup / unattributed        -> fills gold_component_2
  axis B (edit type)  spelling / diacritic / case / spacing / punctuation /
                      digit / transposition / source-raw / none  (recorded in
                      the decisions file; kappa is scored on axis A, which is
                      what scripts/obs_t_gold.py --score measures)

The FIRST annotator's labels (gold_component) never enter this script — the
blind input physically lacks them, and the builder asserts that no label or
notes payload can leak (greps the rendered HTML for annotation-column values).

The annotator works through the sheet in a browser, then clicks
"Download decisions.json". The downloaded file is ingested with:

    python scripts/obs_t_gold.py --ingest <decisions.json>

which fills the gold_component_2 column of validation/gold_sample.csv, after
which scripts/obs_t_gold.py --score reports Cohen's kappa. DO NOT annotate on
MG's behalf: this unit ships the apparatus only.

Usage:  python scripts/obs_t_second_sheet.py            # build the sheet
"""
import csv, html, json, os, sys
from datetime import datetime, timezone

sys.stdout.reconfigure(encoding='utf-8'); sys.stderr.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
VDIR = os.path.join(ROOT, 'validation')
BLIND = os.path.join(VDIR, 'gold_sample_blind.json')
SHEET = os.path.join(VDIR, 'gold_sample.csv')
OUT = os.path.join(VDIR, 'second_annotator_sheet.html')

SHEET_ID = 'obs-t-gold-second-annotator-v1'
SCHEMA = 'obs-t-second-annotator-decisions-v1'

LOCATIONS = ['headword', 'grammar', 'citation', 'sense', 'crossref', 'meta',
             'markup', 'unattributed']
EDIT_TYPES = ['spelling', 'diacritic', 'case', 'spacing', 'punctuation',
              'digit', 'transposition', 'source-raw', 'none']

LOCATION_HELP = {
    'headword': 'lemma / headword / homonym index — <k1> <k2> <h>',
    'grammar': 'gender / part-of-speech — <lex>',
    'citation': 'source reference / siglum / page — <ls>, <pc>',
    'sense': 'gloss / definition / meaning content (incl. Sanskrit words in the gloss)',
    'crossref': 'cross-reference / link target — <lb>',
    'meta': 'record id / structural metadata — <L> <e>',
    'markup': 'the XML/tag structure itself (delimiters, tag names)',
    'unattributed': 'cannot tell where from the evidence shown',
}

TPL_HEADER = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>%(title)s</title>
<style>
:root { --bg:#f6f6f4; --fg:#1c1c1c; --card:#fff; --mut:#6b6b6b; --line:#ddd;
        --acc:#1a5fb4; --chip:#eee; --chipon:#1a5fb4; --chiponfg:#fff; }
@media (prefers-color-scheme: dark) {
  :root { --bg:#17181c; --fg:#e8e8e8; --card:#22242a; --mut:#9a9a9a; --line:#3a3d45;
          --acc:#62a0ea; --chip:#2e3138; --chipon:#62a0ea; --chiponfg:#10131a; }
}
* { box-sizing:border-box; }
body { margin:0; background:var(--bg); color:var(--fg);
       font:15px/1.45 -apple-system,"Segoe UI",Roboto,Helvetica,Arial,sans-serif; }
header { position:sticky; top:0; z-index:5; background:var(--card);
         border-bottom:1px solid var(--line); padding:10px 16px; }
header h1 { font-size:17px; margin:0 0 2px; }
header .sub { color:var(--mut); font-size:13px; }
.bar { display:flex; flex-wrap:wrap; gap:8px; align-items:center; margin-top:8px; }
.bar button, .bar select { font:inherit; padding:5px 12px; border-radius:7px;
  border:1px solid var(--line); background:var(--bg); color:var(--fg); cursor:pointer; }
.bar button.dl { background:var(--acc); color:var(--chiponfg); border-color:var(--acc); font-weight:600; }
.progress { flex:1; min-width:180px; font-size:13px; color:var(--mut); }
.progress b { color:var(--fg); }
.guide { max-width:980px; margin:14px auto 0; padding:0 16px; font-size:13px; color:var(--mut); }
.guide details summary { cursor:pointer; color:var(--acc); }
.guide table { border-collapse:collapse; margin:8px 0; font-size:12.5px; }
.guide td, .guide th { border:1px solid var(--line); padding:3px 8px; text-align:left; }
main { max-width:980px; margin:14px auto 60px; padding:0 16px;
       display:flex; flex-direction:column; gap:14px; }
article.card { background:var(--card); border:1px solid var(--line);
               border-radius:10px; padding:12px 14px; }
article.card.done { border-color:var(--acc); }
.chead { display:flex; flex-wrap:wrap; gap:6px; align-items:baseline; margin-bottom:6px; }
.chead .rid { font-weight:700; }
.badge { font-size:11.5px; padding:1px 8px; border-radius:9px;
         background:var(--chip); color:var(--mut); }
.hw { font-weight:600; }
table.diff { width:100%%; border-collapse:collapse; font:12.5px/1.5 ui-monospace,SFMono-Regular,Menlo,Consolas,monospace; }
table.diff td { border:1px solid var(--line); padding:4px 8px; vertical-align:top;
                word-break:break-all; white-space:pre-wrap; }
table.diff td:first-child { width:64px; color:var(--mut); font-family:inherit; white-space:nowrap; }
td.del { background:rgba(220,50,50,.07); } td.add { background:rgba(40,160,70,.07); }
.cmt { color:var(--mut); font-size:12.5px; margin:6px 0; word-break:break-word; }
.axis { margin-top:8px; }
.axis .alabel { font-size:12.5px; font-weight:700; margin-bottom:4px; }
.chips { display:flex; flex-wrap:wrap; gap:6px; }
.chips label { font-size:12.5px; padding:3px 10px; border-radius:14px;
  border:1px solid var(--line); background:var(--chip); cursor:pointer; user-select:none; }
.chips input { display:none; }
.chips input:checked + span { color:var(--chiponfg); }
.chips label:has(input:checked) { background:var(--chipon); border-color:var(--chipon); color:var(--chiponfg); }
.note { margin-top:8px; width:100%%; font:inherit; font-size:13px; padding:5px 8px;
        border:1px solid var(--line); border-radius:7px; background:var(--bg); color:var(--fg); }
footer { text-align:center; color:var(--mut); font-size:12px; padding:20px; }
</style>
</head>
<body>
<header>
  <h1>%(title)s</h1>
  <div class="sub">%(subtitle)s</div>
  <div class="bar">
    <button class="dl" id="dl">Download decisions.json</button>
    <select id="fdict"><option value="">dict: all</option>%(dict_opts)s</select>
    <select id="flayer"><option value="">layer: all</option>%(layer_opts)s</select>
    <select id="fstate"><option value="">state: all</option>
      <option value="todo">undecided</option><option value="done">decided</option></select>
    <span class="progress">decided <b id="ndone">0</b> / %(ntotal)s</span>
  </div>
</header>
<div class="guide">
  <details open><summary>How to annotate (location-axis guide, validation/COMPONENT_GUIDE.md)</summary>
  <p>Judge <b>where in the entry</b> the correction repairs (axis A). Ignore what
  KIND of edit it is — that is axis B, asked separately below. Read
  <code>old_raw &rarr; new_raw</code> (tagged source line) for git-layer rows;
  <code>old_iast &rarr; new_iast</code> for form-layer rows. The sheet is blind:
  the first annotator's labels are not in it — keep it that way, do not consult
  pass-A material while annotating.</p>
  %(loc_table)s
  <p>Axis B (edit type) describes the KIND of change: spelling, diacritic, case,
  spacing, punctuation, digit, transposition, source-raw (raw SLP1/markup edit),
  none (no surface change, e.g. definition added).</p>
  </details>
</div>
<main id="cards">
"""

CARD = """<article class="card" id="c%(row_id)s" data-dict="%(dict)s" data-layer="%(source_layer)s">
  <div class="chead"><span class="rid">row %(row_id)s</span>
    <span class="badge">%(dict)s</span><span class="badge">%(source_layer)s</span>
    <span class="badge">%(date)s</span><span class="hw">%(headword_iast)s</span></div>
  <table class="diff">
    <tr><td>IAST</td><td class="del">%(old_iast)s</td></tr>
    <tr><td></td><td class="add">%(new_iast)s</td></tr>
    <tr><td>raw</td><td class="del">%(old_raw)s</td></tr>
    <tr><td></td><td class="add">%(new_raw)s</td></tr>
  </table>
  <div class="cmt">comment: %(comment_raw)s</div>
  <div class="axis"><div class="alabel">Axis A — location (fills gold_component_2)</div>
    <div class="chips">%(loc_chips)s</div></div>
  <div class="axis"><div class="alabel">Axis B — edit type (recorded, not scored)</div>
    <div class="chips">%(et_chips)s</div></div>
  <input class="note" type="text" placeholder="note (optional)" data-note="%(row_id)s">
</article>
"""

TPL_FOOTER = """</main>
<footer>%(sheet_id)s · blind second annotator · generated %(generated)s ·
decisions ingest: <code>python scripts/obs_t_gold.py --ingest &lt;decisions.json&gt;</code></footer>
<script>
'use strict';
var SHEET_ID = %(sheet_id_js)s, TOTAL = %(ntotal)s;
var STORE_KEY = 'review-sheet:' + SHEET_ID;
var state = {};
try { state = JSON.parse(localStorage.getItem(STORE_KEY) || '{}') || {}; } catch (e) { state = {}; }
function save() { try { localStorage.setItem(STORE_KEY, JSON.stringify(state)); } catch (e) {} tally(); }
function chosen(r) { var s = state[r]; return !!(s && s.location); }
function tally() {
  var n = 0;
  for (var k in state) if (chosen(k)) n++;
  document.getElementById('ndone').textContent = n;
  document.querySelectorAll('article.card').forEach(function (c) {
    var r = c.id.slice(1);
    c.classList.toggle('done', chosen(r));
  });
}
document.getElementById('cards').addEventListener('change', function (ev) {
  var t = ev.target, card = t.closest('article.card');
  if (!card) return;
  var r = card.id.slice(1);
  if (!state[r]) state[r] = {};
  if (t.name === 'loc') state[r].location = t.value;
  if (t.name === 'et') state[r].edit_type = t.value;
  save();
});
document.getElementById('cards').addEventListener('input', function (ev) {
  var t = ev.target;
  if (!t.hasAttribute('data-note')) return;
  var r = t.getAttribute('data-note');
  if (!state[r]) state[r] = {};
  state[r].note = t.value;
  clearTimeout(window.__nt); window.__nt = setTimeout(save, 400);
});
function applyFilters() {
  var d = document.getElementById('fdict').value,
      l = document.getElementById('flayer').value,
      s = document.getElementById('fstate').value;
  document.querySelectorAll('article.card').forEach(function (c) {
    var r = c.id.slice(1), show = true;
    if (d && c.dataset.dict !== d) show = false;
    if (l && c.dataset.layer !== l) show = false;
    if (s === 'done' && !chosen(r)) show = false;
    if (s === 'todo' && chosen(r)) show = false;
    c.style.display = show ? '' : 'none';
  });
}
['fdict', 'flayer', 'fstate'].forEach(function (id) {
  document.getElementById(id).addEventListener('change', applyFilters);
});
document.getElementById('dl').addEventListener('click', function () {
  var out = { sheet_id: SHEET_ID, schema: %(schema_js)s,
              exported: new Date().toISOString(),
              blind_input: 'validation/gold_sample_blind.json',
              annotated: 0, total: TOTAL, decisions: [] };
  Object.keys(state).sort(function (a, b) { return a - b; }).forEach(function (r) {
    if (!chosen(r)) return;
    out.decisions.push({ row_id: parseInt(r, 10), location: state[r].location,
                         edit_type: state[r].edit_type || '', note: state[r].note || '' });
  });
  out.annotated = out.decisions.length;
  var blob = new Blob([JSON.stringify(out, null, 1)], { type: 'application/json' });
  var a = document.createElement('a');
  a.href = URL.createObjectURL(blob);
  a.download = SHEET_ID + '_decisions.json';
  document.body.appendChild(a); a.click(); a.remove();
});
/* restore */
document.querySelectorAll('article.card').forEach(function (c) {
  var r = c.id.slice(1), s = state[r];
  if (!s) return;
  if (s.location) { var i = c.querySelector('input[name=loc][value="' + s.location + '"]'); if (i) i.checked = true; }
  if (s.edit_type) { var j = c.querySelector('input[name=et][value="' + s.edit_type + '"]'); if (j) j.checked = true; }
  if (s.note) c.querySelector('[data-note]').value = s.note;
});
tally();
</script>
</body>
</html>
"""


def chips(name, values, help_map=None):
    out = []
    for v in values:
        title = (' title="%s"' % html.escape(help_map[v], quote=True)) if help_map and v in help_map else ''
        out.append('<label%s><input type="radio" name="%s" value="%s"><span>%s</span></label>'
                   % (title, name, v, v))
    return ''.join(out)


def build():
    with open(SHEET, encoding='utf-8') as f:
        sheet = list(csv.DictReader(f))
    with open(BLIND, encoding='utf-8') as f:
        blind = json.load(f)

    # Coverage: the blind input must cover exactly the gold rows (by row_id).
    sheet_ids = {int(r['row_id']) for r in sheet}
    blind_ids = {int(r['row_id']) for r in blind}
    if sheet_ids != blind_ids:
        sys.exit('blind input does not cover the gold sample: missing %d, extra %d'
                 % (len(sheet_ids - blind_ids), len(blind_ids - sheet_ids)))
    # Blindness: no annotation-column payload may reach the sheet.
    for r in blind:
        for banned in ('gold_component', 'gold_component_2', 'notes', 'event_id'):
            if banned in r:
                sys.exit('blind input leaked field %r' % banned)

    dicts = sorted({r['dict'] for r in blind})
    layers = sorted({r['source_layer'] for r in blind})

    loc_table = '<table><tr><th>value</th><th>what it means</th></tr>' + ''.join(
        '<tr><td><code>%s</code></td><td>%s</td></tr>' % (k, html.escape(v))
        for k, v in LOCATION_HELP.items()) + '</table>'

    parts = [TPL_HEADER % {
        'title': 'OBS-T gold sample — second annotator (blind)',
        'subtitle': '390 gold rows · label where each correction repairs (axis A) and '
                    'what kind of edit it is (axis B) · first-annotator labels hidden · '
                    'H5312',
        'dict_opts': ''.join('<option>%s</option>' % d for d in dicts),
        'layer_opts': ''.join('<option>%s</option>' % l for l in layers),
        'ntotal': len(blind),
        'loc_table': loc_table,
    }]
    for r in blind:
        parts.append(CARD % {
            'row_id': html.escape(str(r['row_id'])),
            'dict': html.escape(r['dict']),
            'source_layer': html.escape(r['source_layer']),
            'date': html.escape(str(r.get('date', ''))),
            'headword_iast': html.escape(r['headword_iast']),
            'old_iast': html.escape(r['old_iast']),
            'new_iast': html.escape(r['new_iast']),
            'old_raw': html.escape(r['old_raw']),
            'new_raw': html.escape(r['new_raw']),
            'comment_raw': html.escape(r.get('comment_raw', '')),
            'loc_chips': chips('loc', LOCATIONS, LOCATION_HELP),
            'et_chips': chips('et', EDIT_TYPES),
        })
    parts.append(TPL_FOOTER % {
        'sheet_id': SHEET_ID,
        'sheet_id_js': json.dumps(SHEET_ID),
        'schema_js': json.dumps(SCHEMA),
        'ntotal': len(blind),
        'generated': datetime.now(timezone.utc).strftime('%Y-%m-%d'),
    })
    doc = ''.join(parts)
    # Leak check on the RENDERED sheet: no chip may be pre-selected (a checked
    # attribute would mean a first-annotator label reached the annotator). The
    # word also appears in CSS (:checked) and JS (.checked =), so match only a
    # real HTML attribute occurrence.
    import re
    if re.search(r'(?<![\w.:])checked(?=[\s=>])', doc):
        sys.exit('rendered sheet contains a pre-selected chip (leak)')
    with open(OUT, 'w', encoding='utf-8', newline='\n') as f:
        f.write(doc)
    kb = os.path.getsize(OUT) // 1024
    print(f'wrote {OUT}  ({len(blind)} cards, {kb} KB)')
    print(f'  coverage: {len(blind_ids)}/{len(sheet_ids)} gold rows')
    print(f'  blind: gold_component/gold_component_2/notes absent from payload OK')
    print(f'  -> open in a browser, annotate, "Download decisions.json", then:')
    print(f'     python scripts/obs_t_gold.py --ingest <decisions.json> [--force]')
    print(f'     python scripts/obs_t_gold.py --score   # kappa appears in gold_metrics.json')


if __name__ == '__main__':
    build()
