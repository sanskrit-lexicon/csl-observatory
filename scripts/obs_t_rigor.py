#!/usr/bin/env python3
"""OBS-T Phase 7b/8 — statistical rigor for the TWO-AXIS hypotheses.

After the Phase 7i finding, the typology is two orthogonal axes:
  * LOCATION (microstructure component, derived): where in the entry — `error_component`
  * EDIT-TYPE (from edit-ops, all events): what kind of change — `edit_type`

Tested claims, stdlib-only:

1. **H1 micro-edit dominance** — corrections are tiny surface-form edits, not content
   rewrites, and this holds *across locations* (even sense/headword). Edit-distance
   distribution + edit_type shares + per-location minor-edit rate (Wilson CIs).
2. **H2 cross-dictionary** — chi-square independence of LOCATION × dictionary on the
   derived labels, with Cramer's V.
3. **H3 diachronic** — Mann-Kendall trends per location and per edit_type.
4. **Location × edit-type cross** — the headline two-axis table.

Input : observatory/site/src/data/correction_events_final.csv  (needs edit_type)
Output: reports/obs_t_rigor.md, observatory/site/src/data/obs_t_rigor.json

Usage:  python scripts/obs_t_rigor.py
"""
import csv, json, math, os, sys
from collections import Counter, defaultdict
from datetime import datetime, timezone
sys.stdout.reconfigure(encoding='utf-8'); sys.stderr.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DATA = os.path.join(ROOT, 'observatory', 'site', 'src', 'data')
IN_CSV = os.path.join(DATA, 'correction_events_final.csv')
OUT_MD = os.path.join(ROOT, 'reports', 'obs_t_rigor.md')
OUT_JSON = os.path.join(DATA, 'obs_t_rigor.json')
csv.field_size_limit(10_000_000)

MINOR_TYPES = {'spelling', 'diacritic', 'case', 'spacing', 'punctuation', 'digit'}


# ----------------------------------------------------------------- statistics
def wilson(k, n, z=1.96):
    if n == 0:
        return 0.0, 0.0, 0.0
    p = k / n
    d = 1 + z * z / n
    center = (p + z * z / (2 * n)) / d
    half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return p, max(0.0, center - half), min(1.0, center + half)


def _phi(z):
    return 0.5 * (1 + math.erf(z / math.sqrt(2)))


def mann_kendall(vals):
    n = len(vals)
    if n < 3:
        return 0.0, 0.0, 1.0
    s = sum((vals[j] > vals[i]) - (vals[j] < vals[i])
            for i in range(n - 1) for j in range(i + 1, n))
    var = n * (n - 1) * (2 * n + 5) / 18
    z = (s - 1) / math.sqrt(var) if s > 0 else (s + 1) / math.sqrt(var) if s < 0 else 0.0
    tau = s / (n * (n - 1) / 2)
    return round(tau, 3), round(z, 2), round(2 * (1 - _phi(abs(z))), 4)


def _gammq(a, x):
    if x < 0 or a <= 0:
        return 1.0
    if x < a + 1:
        ap, summ, term = a, 1.0 / a, 1.0 / a
        for _ in range(200):
            ap += 1; term *= x / ap; summ += term
            if abs(term) < abs(summ) * 1e-12:
                break
        return 1.0 - summ * math.exp(-x + a * math.log(x) - math.lgamma(a))
    b, c = x + 1 - a, 1e30
    d = 1.0 / b; h = d
    for i in range(1, 200):
        an = -i * (i - a); b += 2
        d = an * d + b
        if abs(d) < 1e-30:
            d = 1e-30
        c = b + an / c
        if abs(c) < 1e-30:
            c = 1e-30
        d = 1.0 / d; delta = d * c; h *= delta
        if abs(delta - 1) < 1e-12:
            break
    return h * math.exp(-x + a * math.log(x) - math.lgamma(a))


def chi2_sf(x, k):
    return _gammq(k / 2.0, x / 2.0)


def chi2_independence(table):
    rows = sorted({r for r, _ in table}); cols = sorted({c for _, c in table})
    rt = Counter(); ct = Counter(); n = 0
    for (r, c), v in table.items():
        rt[r] += v; ct[c] += v; n += v
    chi2 = 0.0
    for r in rows:
        for c in cols:
            e = rt[r] * ct[c] / n
            if e > 0:
                chi2 += (table.get((r, c), 0) - e) ** 2 / e
    dof = (len(rows) - 1) * (len(cols) - 1)
    p = chi2_sf(chi2, dof) if dof > 0 else 1.0
    v = math.sqrt(chi2 / (n * (min(len(rows), len(cols)) - 1))) if n and min(len(rows), len(cols)) > 1 else 0.0
    return round(chi2, 1), dof, p, round(v, 3)


# ----------------------------------------------------------------------- main
def _dist(r):
    try:
        return int(r['edit_distance'])
    except (ValueError, KeyError):
        return None


def main():
    with open(IN_CSV, encoding='utf-8') as f:
        rows = list(csv.DictReader(f))
    derived = [r for r in rows if r['evidence_level'] == 'derived']

    # ---- H1: micro-edit dominance ----
    dists = [d for d in (_dist(r) for r in rows) if d is not None]
    dists.sort()
    nd = len(dists)
    le2 = sum(1 for d in dists if d <= 2)
    et = Counter(r['edit_type'] for r in rows)
    tot = sum(et.values())
    # location-invariance: minor-edit rate within each derived location
    loc_minor = {}
    by_loc = defaultdict(list)
    for r in derived:
        by_loc[r['error_component']].append(r)
    for loc, evs in by_loc.items():
        k = sum(1 for r in evs if r['edit_type'] in MINOR_TYPES and (_dist(r) or 9) <= 3)
        p, lo, hi = wilson(k, len(evs))
        loc_minor[loc] = {'n': len(evs), 'minor_rate': round(p, 3),
                          'ci95': [round(lo, 3), round(hi, 3)]}
    h1 = {
        'edit_distance': {'median': dists[nd // 2] if nd else 0,
                          'pct_le2': round(le2 / nd, 3) if nd else 0,
                          'p90': dists[min(nd - 1, int(nd * 0.9))] if nd else 0,
                          'max': dists[-1] if nd else 0},
        'edit_type_share': {k: round(v / tot, 3) for k, v in et.most_common()},
        'minor_rate_by_location': loc_minor,
    }

    # ---- H2: cross-dictionary on LOCATION (derived) ----
    dcount = Counter(r['dict'] for r in derived)
    top_dicts = [d for d, _ in dcount.most_common(15)]
    table = Counter((r['dict'], r['error_component']) for r in derived
                    if r['dict'] in top_dicts)
    chi2, dof, p2, v = chi2_independence(table)
    h2 = {'dicts_tested': len(top_dicts), 'chi2': chi2, 'dof': dof,
          'p_value': p2, 'cramers_v': v}

    # ---- H3: trends per location (derived) and per edit_type (all) ----
    years = sorted({r['date'][:4] for r in rows if r['date']})

    def trends(subset, key):
        yr_tot = Counter(r['date'][:4] for r in subset if r['date'])
        yr_k = Counter((r['date'][:4], r[key]) for r in subset if r['date'])
        out = {}
        for c in sorted({r[key] for r in subset}):
            series = [yr_k.get((y, c), 0) / yr_tot[y] for y in years if yr_tot.get(y)]
            tau, z, p = mann_kendall(series)
            out[c] = {'tau': tau, 'p_value': p,
                      'direction': 'rising' if tau > 0 and p < 0.05 else
                                   'falling' if tau < 0 and p < 0.05 else 'flat',
                      'first': round(series[0], 3) if series else 0,
                      'last': round(series[-1], 3) if series else 0}
        return out
    h3_loc = trends(derived, 'error_component')
    h3_type = trends(rows, 'edit_type')

    # ---- location x edit_type cross (derived) ----
    cross = Counter((r['error_component'], r['edit_type']) for r in derived)
    locs = sorted({l for l, _ in cross})
    types = [t for t, _ in Counter(r['edit_type'] for r in derived).most_common()]
    cross_tbl = {l: {t: cross.get((l, t), 0) for t in types} for l in locs}

    out = {'generatedAt': datetime.now(timezone.utc).isoformat(),
           'h1_micro_edit': h1, 'h2_cross_dictionary': h2,
           'h3_location_trends': h3_loc, 'h3_edittype_trends': h3_type,
           'location_x_edittype': cross_tbl, 'years': years}
    with open(OUT_JSON, 'w', encoding='utf-8') as f:
        json.dump(out, f, ensure_ascii=False, indent=2)

    # ---- report ----
    L = []; A = L.append
    A('# Statistical rigor — two-axis typology (OBS-T)')
    A('')
    A('_Generated by `scripts/obs_t_rigor.py`. The typology is two orthogonal axes: '
      '**location** (where in the entry, derived labels) and **edit-type** (what kind '
      'of change, from edit-ops). Tested with Wilson CIs, chi-square (Cramér\'s V), '
      'and Mann-Kendall trends._')
    A('')
    A('## H1 — corrections are micro surface edits, at every location')
    A('')
    A(f'Edit distance: **median {h1["edit_distance"]["median"]}**, '
      f'**{h1["edit_distance"]["pct_le2"]:.0%} are ≤ 2 characters** '
      f'(p90 {h1["edit_distance"]["p90"]}, max {h1["edit_distance"]["max"]}). '
      'Edit-type shares:')
    A('')
    A('| edit type | share |')
    A('|---|---:|')
    for t, s in h1['edit_type_share'].items():
        A(f'| {t} | {s:.1%} |')
    A('')
    A('Every type is a surface change — there is no "content rewrite" category. '
      'Crucially this holds **across locations**: the minor-edit rate (a small '
      'surface edit) is high even where meaning lives.')
    A('')
    A('| location | n | minor-edit rate (95% CI) |')
    A('|---|---:|---|')
    for loc in sorted(loc_minor, key=lambda l: -loc_minor[l]['n']):
        d = loc_minor[loc]
        A(f'| {loc} | {d["n"]:,} | {d["minor_rate"]:.1%} '
          f'[{d["ci95"][0]:.1%}, {d["ci95"][1]:.1%}] |')
    A('')
    A('So even corrections **located in the sense/definition and headword** are '
      'overwhelmingly small form fixes, not redefinitions — the honest, two-axis '
      'restatement of the old "surface dominates" claim.')
    A('')
    A('## H2 — the LOCATION profile differs by dictionary (derived labels)')
    A('')
    A(f'Chi-square independence of location × dictionary (top {h2["dicts_tested"]}, '
      f'derived only): χ² = {h2["chi2"]}, dof = {h2["dof"]}, '
      f'p {"< 0.001" if h2["p_value"] < 0.001 else f"= {h2["p_value"]:.3f}"}, '
      f'**Cramér\'s V = {h2["cramers_v"]}**. Dictionaries differ in *where* their '
      'errors sit, not only how many — now on clean location labels.')
    A('')
    A('## H3 — diachronic trends')
    A('')
    A('Location (derived) — Mann-Kendall on yearly share:')
    A('')
    A('| location | τ | p | trend | first→last |')
    A('|---|---:|---:|---|---|')
    for c in sorted(h3_loc, key=lambda c: h3_loc[c]['tau']):
        d = h3_loc[c]
        A(f'| {c} | {d["tau"]} | {"<0.001" if d["p_value"]<0.001 else d["p_value"]} '
          f'| {d["direction"]} | {d["first"]:.2f}→{d["last"]:.2f} |')
    A('')
    A('Edit-type (all):')
    A('')
    A('| edit type | τ | p | trend | first→last |')
    A('|---|---:|---:|---|---|')
    for c in sorted(h3_type, key=lambda c: h3_type[c]['tau']):
        d = h3_type[c]
        A(f'| {c} | {d["tau"]} | {"<0.001" if d["p_value"]<0.001 else d["p_value"]} '
          f'| {d["direction"]} | {d["first"]:.2f}→{d["last"]:.2f} |')
    A('')
    A('## Location × edit-type (derived) — the two-axis picture')
    A('')
    A('| location \\\\ type | ' + ' | '.join(types) + ' |')
    A('|---' * (len(types) + 1) + '|')
    for l in sorted(locs, key=lambda l: -sum(cross_tbl[l].values())):
        A(f'| {l} | ' + ' | '.join(str(cross_tbl[l][t]) for t in types) + ' |')
    A('')
    A('*Caveat: shares are over corrected events (curatorial attention), not the raw '
      'error rate. Object of analysis in scope per `docs/BOUNDARY_RULES.md`.*')
    with open(OUT_MD, 'w', encoding='utf-8', newline='\n') as f:
        f.write('\n'.join(L) + '\n')

    print(f'wrote {OUT_MD}')
    print(f'wrote {OUT_JSON}')
    print(f'  H1 median dist {h1["edit_distance"]["median"]}  ≤2 {h1["edit_distance"]["pct_le2"]:.0%}  '
          f'types {list(h1["edit_type_share"])[:4]}')
    print(f'  H2 location×dict V={v} p={p2:.1e}')
    print(f'  H3 loc rising={[c for c in h3_loc if h3_loc[c]["direction"]=="rising"]} '
          f'falling={[c for c in h3_loc if h3_loc[c]["direction"]=="falling"]}')


if __name__ == '__main__':
    main()
