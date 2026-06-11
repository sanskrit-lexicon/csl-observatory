#!/usr/bin/env python3
"""OBS-T Phase 7b — statistical rigor for the three core hypotheses.

Replaces raw counts with tested claims, stdlib-only:

1. **Typology dominance** — share of *meaning* edits (sense + grammar) vs *surface*
   edits (everything else), with Wilson 95% CIs, reported overall and per layer
   and for derived-only events (robustness to the heuristic labels).
2. **Cross-dictionary differences** — a chi-square test of independence on the
   component x dictionary table (top dictionaries) with Cramer's V effect size,
   showing the error *profile* differs by dictionary beyond mere volume.
3. **Diachronic shifts** — a Mann-Kendall monotonic-trend test on each component's
   yearly share, flagging components that significantly rise or fall over 2014-2026.

Input : observatory/site/src/data/correction_events_final.csv
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

MEANING = {'sense', 'grammar'}            # content/semantic edits
# everything else = surface (orthography, encoding, markup, citation, meta,
# crossref, headword) — repair to form/structure rather than meaning.


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
    """Monotonic-trend test on a time-ordered series. Returns (tau, z, p_two)."""
    n = len(vals)
    if n < 3:
        return 0.0, 0.0, 1.0
    s = sum((vals[j] > vals[i]) - (vals[j] < vals[i])
            for i in range(n - 1) for j in range(i + 1, n))
    var = n * (n - 1) * (2 * n + 5) / 18
    if s > 0:
        z = (s - 1) / math.sqrt(var)
    elif s < 0:
        z = (s + 1) / math.sqrt(var)
    else:
        z = 0.0
    tau = s / (n * (n - 1) / 2)
    p = 2 * (1 - _phi(abs(z)))
    return round(tau, 3), round(z, 2), round(p, 4)


def _gammq(a, x):
    """Regularized upper incomplete gamma Q(a,x) (Numerical Recipes gser/gcf)."""
    if x < 0 or a <= 0:
        return 1.0
    if x < a + 1:                          # series for P, return 1-P
        ap, summ, term = a, 1.0 / a, 1.0 / a
        for _ in range(200):
            ap += 1
            term *= x / ap
            summ += term
            if abs(term) < abs(summ) * 1e-12:
                break
        return 1.0 - summ * math.exp(-x + a * math.log(x) - math.lgamma(a))
    b, c = x + 1 - a, 1e30                  # continued fraction for Q
    d = 1.0 / b
    h = d
    for i in range(1, 200):
        an = -i * (i - a)
        b += 2
        d = an * d + b
        if abs(d) < 1e-30:
            d = 1e-30
        c = b + an / c
        if abs(c) < 1e-30:
            c = 1e-30
        d = 1.0 / d
        delta = d * c
        h *= delta
        if abs(delta - 1) < 1e-12:
            break
    return h * math.exp(-x + a * math.log(x) - math.lgamma(a))


def chi2_sf(x, k):
    return _gammq(k / 2.0, x / 2.0)


def chi2_independence(table):
    """table: dict[(row,col)] = count. Returns (chi2, dof, p, cramers_v)."""
    rows = sorted({r for r, _ in table})
    cols = sorted({c for _, c in table})
    rt = Counter(); ct = Counter(); n = 0
    for (r, c), v in table.items():
        rt[r] += v; ct[c] += v; n += v
    chi2 = 0.0
    for r in rows:
        for c in cols:
            e = rt[r] * ct[c] / n
            o = table.get((r, c), 0)
            if e > 0:
                chi2 += (o - e) ** 2 / e
    dof = (len(rows) - 1) * (len(cols) - 1)
    p = chi2_sf(chi2, dof) if dof > 0 else 1.0
    v = math.sqrt(chi2 / (n * (min(len(rows), len(cols)) - 1))) if n and min(len(rows), len(cols)) > 1 else 0.0
    return round(chi2, 1), dof, p, round(v, 3)


# ----------------------------------------------------------------------- main
def meaning_share(rows):
    k = sum(1 for r in rows if r['error_component'] in MEANING)
    return wilson(k, len(rows)), k, len(rows)


def main():
    with open(IN_CSV, encoding='utf-8') as f:
        rows = list(csv.DictReader(f))

    # ---- H1: typology dominance (surface >> meaning) ----
    subsets = {
        'all': rows,
        'form': [r for r in rows if r['source_layer'] == 'form'],
        'git': [r for r in rows if r['source_layer'] == 'git'],
        'derived_only': [r for r in rows if r['evidence_level'] == 'derived'],
    }
    h1 = {}
    for name, sub in subsets.items():
        (p, lo, hi), k, n = meaning_share(sub)
        h1[name] = {'n': n, 'meaning_share': round(p, 4),
                    'ci95': [round(lo, 4), round(hi, 4)],
                    'surface_share': round(1 - p, 4)}

    # ---- H2: cross-dictionary profile differences ----
    dcount = Counter(r['dict'] for r in rows)
    top_dicts = [d for d, _ in dcount.most_common(15)]
    table = Counter()
    for r in rows:
        if r['dict'] in top_dicts:
            table[(r['dict'], r['error_component'])] += 1
    chi2, dof, p2, v = chi2_independence(table)
    h2 = {'dicts_tested': len(top_dicts), 'chi2': chi2, 'dof': dof,
          'p_value': p2, 'cramers_v': v,
          'interpretation': ('profiles differ by dictionary beyond volume'
                             if p2 < 0.05 else 'no significant profile difference')}

    # ---- H3: diachronic trends per component ----
    years = sorted({r['date'][:4] for r in rows if r['date']})
    comps = sorted({r['error_component'] for r in rows})
    yr_tot = Counter(r['date'][:4] for r in rows if r['date'])
    yr_comp = Counter((r['date'][:4], r['error_component']) for r in rows if r['date'])
    h3 = {}
    for c in comps:
        series = [yr_comp.get((y, c), 0) / yr_tot[y] for y in years if yr_tot[y]]
        tau, z, p = mann_kendall(series)
        h3[c] = {'tau': tau, 'z': z, 'p_value': p,
                 'direction': 'rising' if tau > 0 and p < 0.05 else
                              'falling' if tau < 0 and p < 0.05 else 'flat',
                 'first_year_share': round(series[0], 3) if series else 0,
                 'last_year_share': round(series[-1], 3) if series else 0}

    out = {'generatedAt': datetime.now(timezone.utc).isoformat(),
           'h1_typology_dominance': h1, 'h2_cross_dictionary': h2,
           'h3_diachronic_trends': h3, 'years': years}
    with open(OUT_JSON, 'w', encoding='utf-8') as f:
        json.dump(out, f, ensure_ascii=False, indent=2)

    # ---- report ----
    L = []; A = L.append
    A('# Statistical rigor for the OBS-T hypotheses')
    A('')
    A('_Generated by `scripts/obs_t_rigor.py`. Tests the three core claims with '
      'Wilson confidence intervals, a chi-square test of independence (Cramer\'s V), '
      'and Mann-Kendall trend tests — all stdlib, deterministic._')
    A('')
    A('## H1 — surface repair dominates over meaning edits')
    A('')
    A('Share of **meaning** edits (`sense` + `grammar`) vs **surface** edits '
      '(orthography, encoding, markup, citation, meta, crossref, headword), with '
      'Wilson 95% CIs. The hypothesis predicts surface >> meaning, robustly across '
      'layers and on derived-only labels.')
    A('')
    A('| subset | n | meaning share (95% CI) | surface share |')
    A('|---|---:|---|---:|')
    for name in ('all', 'form', 'git', 'derived_only'):
        d = h1[name]
        A(f'| {name} | {d["n"]:,} | {d["meaning_share"]:.3f} '
          f'[{d["ci95"][0]:.3f}, {d["ci95"][1]:.3f}] | {d["surface_share"]:.3f} |')
    A('')
    A(f'Surface repair dominates the record as a whole '
      f'({h1["all"]["surface_share"]:.1%}) and overwhelmingly in the 2014–2019 form '
      f'era ({h1["form"]["surface_share"]:.1%}). The 2019–2026 git era, however, is '
      f'near parity (surface {h1["git"]["surface_share"]:.1%}, meaning '
      f'{h1["git"]["meaning_share"]:.1%}): meaning edits rise to roughly half as the '
      'orthography stabilizes. So the honest claim is **not** uniform dominance, but '
      'a maturation shift — surface repair dominates overall and early, while the '
      'modern era moves toward meaning. This is corroborated by H3 (headword edits '
      'collapse, sense edits rise) and is the more defensible framing.')
    A('')
    A('## H2 — the error profile differs by dictionary')
    A('')
    A(f'Chi-square test of independence on the component × dictionary table '
      f'(top {h2["dicts_tested"]} dictionaries): χ² = {h2["chi2"]}, '
      f'dof = {h2["dof"]}, p {"< 0.001" if h2["p_value"] < 0.001 else f"= {h2["p_value"]:.3f}"}, '
      f'**Cramér\'s V = {h2["cramers_v"]}**. The profile difference is '
      f'{"statistically significant" if h2["p_value"] < 0.05 else "not significant"} '
      'and of non-trivial effect size — dictionaries differ in *what kind* of error '
      'they accumulate, not only in how many.')
    A('')
    A('## H3 — diachronic trends (Mann-Kendall on yearly component share)')
    A('')
    A('| component | τ | p | trend | first→last yr share |')
    A('|---|---:|---:|---|---|')
    for c in sorted(h3, key=lambda c: h3[c]['tau']):
        d = h3[c]
        A(f'| {c} | {d["tau"]} | {"<0.001" if d["p_value"] < 0.001 else d["p_value"]} '
          f'| {d["direction"]} | {d["first_year_share"]:.2f}→{d["last_year_share"]:.2f} |')
    A('')
    rising = [c for c in h3 if h3[c]['direction'] == 'rising']
    falling = [c for c in h3 if h3[c]['direction'] == 'falling']
    A(f'Significantly **rising**: {", ".join(rising) or "none"}. '
      f'Significantly **falling**: {", ".join(falling) or "none"}. '
      'These are the maturation signatures the diachronic claim predicts.')
    A('')
    A('*Caveat: shares are over corrected events, i.e. curatorial attention, not '
      'the raw error rate (see the maintenance-profile framing). Object of analysis '
      'in scope per `docs/BOUNDARY_RULES.md`.*')
    with open(OUT_MD, 'w', encoding='utf-8', newline='\n') as f:
        f.write('\n'.join(L) + '\n')

    print(f'wrote {OUT_MD}')
    print(f'wrote {OUT_JSON}')
    print(f'  H1 meaning share (all): {h1["all"]["meaning_share"]:.3f} '
          f'CI {h1["all"]["ci95"]}  surface {h1["all"]["surface_share"]:.3f}')
    print(f'  H2 chi2={chi2} dof={dof} p={p2:.2e} Cramer-V={v}')
    print(f'  H3 rising={rising} falling={falling}')


if __name__ == '__main__':
    main()
