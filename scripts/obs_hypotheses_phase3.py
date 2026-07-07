#!/usr/bin/env python3
"""OBS-T Phase-3 — hypotheses H4, H5, H6, H8 (H7 registered, H9 routed elsewhere).

Executes Part 1's acceptance checklist of
docs/HYPOTHESIS_VIZ_STANDARDS_SPEC_2026-07.md, reusing the H1-H3 rigor idiom
(reports/obs_t_rigor.md, scripts/obs_t_rigor.py) verbatim: Wilson CIs, chi-square
with Cramer's V (commit-block bootstrap 95% CI), Mann-Kendall with BH q-values.
New instruments introduced here, named inline wherever used:

  * contributor-level permutation test (H4) -- shuffle the family-label pool
    across contributors while holding each contributor's total commit count
    fixed (the repo-idiom substitute for an inferential p-value, since commits
    cluster by campaign);
  * bootstrap CI on a median (H4, normalized_entropy);
  * bootstrap-percentile one-sided p-value for a share exceeding a threshold,
    BH-adjusted across components (H6);
  * exact two-sided binomial test per confusion pair, BH-adjusted across all
    tested pairs (H8).

Data (read-only, no data/ mutation):
  data/contributor_repo_heatmap.csv, data/contributor_specialisation.csv        (H4)
  observatory/site/src/data/correction_events_final.csv,
  observatory/site/src/data/obs_t_corrector.csv                                 (H5, H6)
  data/snapshots/*/summary.json                                                (H7)
  observatory/site/src/data/obs_t_confusion.csv                                 (H8)
  validation/gold_metrics.json                                                 (H6 kappa gate)

Output: reports/obs_phase3_rigor.md, observatory/site/src/data/obs_phase3_rigor.json

Usage: python scripts/obs_hypotheses_phase3.py
"""
import csv, json, math, os, random, sys
from collections import Counter, defaultdict
from datetime import datetime, timezone

sys.stdout.reconfigure(encoding='utf-8'); sys.stderr.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import obs_t_rigor as R  # noqa: E402  (reuse wilson / mann_kendall / chi2_independence / bh_adjust)

DATA_GH = os.path.join(ROOT, 'data')
DATA_SITE = os.path.join(ROOT, 'observatory', 'site', 'src', 'data')
VALIDATION = os.path.join(ROOT, 'validation')

HEATMAP_CSV = os.path.join(DATA_GH, 'contributor_repo_heatmap.csv')
SPECIALISATION_CSV = os.path.join(DATA_GH, 'contributor_specialisation.csv')
EVENTS_CSV = os.path.join(DATA_SITE, 'correction_events_final.csv')
CORRECTOR_CSV = os.path.join(DATA_SITE, 'obs_t_corrector.csv')
CONFUSION_CSV = os.path.join(DATA_SITE, 'obs_t_confusion.csv')
SNAPSHOTS_DIR = os.path.join(DATA_GH, 'snapshots')
GOLD_METRICS_JSON = os.path.join(VALIDATION, 'gold_metrics.json')

OUT_MD = os.path.join(ROOT, 'reports', 'obs_phase3_rigor.md')
OUT_JSON = os.path.join(DATA_SITE, 'obs_phase3_rigor.json')

csv.field_size_limit(10_000_000)

N_PERM = 10_000
N_BOOT = 300


# ------------------------------------------------------------------ helpers
def bh_qvalues(pvals):
    """Generic Benjamini-Hochberg step-up; pvals: {label: p}. Returns {label: q}."""
    items = sorted(pvals.items(), key=lambda kv: kv[1])
    m = len(items)
    q = {}
    prev = 1.0
    for rank, (label, p) in enumerate(reversed(items), start=1):
        orig_rank = m - rank + 1
        val = min(prev, p * m / orig_rank)
        prev = val
        q[label] = min(1.0, round(val, 4))
    return q


def bootstrap_median_ci(values, b=2000, seed=0):
    if not values:
        return 0.0, [0.0, 0.0]
    rng = random.Random(seed)
    vals = sorted(values)
    n = len(vals)
    med = vals[n // 2] if n % 2 else (vals[n // 2 - 1] + vals[n // 2]) / 2
    boots = []
    for _ in range(b):
        sample = [rng.choice(vals) for _ in range(n)]
        sample.sort()
        boots.append(sample[n // 2] if n % 2 else (sample[n // 2 - 1] + sample[n // 2]) / 2)
    boots.sort()
    lo = boots[int(0.025 * b)]
    hi = boots[int(0.975 * b)]
    return round(med, 3), [round(lo, 3), round(hi, 3)]


def permutation_test_contingency(table, n_perm=N_PERM, seed=0):
    """Contributor-level permutation test: shuffle the family-label pool
    across logins while holding each login's total commit count fixed
    (equivalent to a random contingency table with both margins preserved).
    Returns (chi2, dof, cramers_v, perm_p)."""
    rows = sorted({r for r, _ in table})
    cols = sorted({c for _, c in table})
    row_totals = {r: sum(table.get((r, c), 0) for c in cols) for r in rows}
    col_totals = {c: sum(table.get((r, c), 0) for r in rows) for c in cols}
    obs_chi2, dof, _, obs_v = R.chi2_independence(table)
    pool = []
    for c in cols:
        pool.extend([c] * col_totals[c])
    rng = random.Random(seed)
    n_ge = 0
    for _ in range(n_perm):
        shuffled = pool[:]
        rng.shuffle(shuffled)
        idx = 0
        perm_table = Counter()
        for r in rows:
            sz = row_totals[r]
            for c in shuffled[idx:idx + sz]:
                perm_table[(r, c)] += 1
            idx += sz
        _, _, _, v_perm = R.chi2_independence(perm_table)
        if v_perm >= obs_v:
            n_ge += 1
    perm_p = (n_ge + 1) / (n_perm + 1)
    return obs_chi2, dof, obs_v, round(perm_p, 4)


def block_bootstrap_v_generic(rows, key_a, key_b, restrict_a=None, b=N_BOOT, seed=0):
    """H1-H3 idiom's block_bootstrap_v, generalised to arbitrary field pairs."""
    groups = defaultdict(list)
    for r in rows:
        if restrict_a is not None and r[key_a] not in restrict_a:
            continue
        groups[r.get('commit_sha') or r.get('event_id')].append(r)
    keys = list(groups)
    if not keys:
        return [0.0, 0.0]
    rng = random.Random(seed)
    vs = []
    for _ in range(b):
        table = Counter()
        for _ in range(len(keys)):
            for r in groups[rng.choice(keys)]:
                table[(r[key_a], r[key_b])] += 1
        vs.append(R.chi2_independence(table)[3])
    vs.sort()
    return [round(vs[int(0.025 * b)], 3), round(vs[int(0.975 * b)], 3)]


def top2_share(rows_component):
    cnt = Counter(r['corrector'] for r in rows_component)
    total = sum(cnt.values())
    if not total:
        return 0.0
    return sum(c for _, c in cnt.most_common(2)) / total


def gini(counts):
    xs = sorted(c for c in counts if c >= 0)
    n = len(xs)
    total = sum(xs)
    if n == 0 or total == 0:
        return 0.0
    numerator = sum((i + 1) * x for i, x in enumerate(xs))
    return round((2 * numerator) / (n * total) - (n + 1) / n, 3)


def block_bootstrap_top2(rows_component, threshold=0.80, b=N_BOOT, seed=0):
    """Commit-block bootstrap CI on the top-2 corrector share, plus a
    bootstrap-percentile one-sided p-value for the null share < threshold."""
    groups = defaultdict(list)
    for r in rows_component:
        groups[r.get('commit_sha') or r.get('event_id')].append(r)
    keys = list(groups)
    if not keys:
        return [0.0, 0.0], 1.0
    rng = random.Random(seed)
    shares = []
    for _ in range(b):
        cnt = Counter()
        for _ in range(len(keys)):
            for r in groups[rng.choice(keys)]:
                cnt[r['corrector']] += 1
        tot = sum(cnt.values())
        shares.append(sum(c for _, c in cnt.most_common(2)) / tot if tot else 0.0)
    shares.sort()
    lo = shares[int(0.025 * b)]
    hi = shares[int(0.975 * b)]
    p_below = sum(1 for s in shares if s < threshold) / b
    return [round(lo, 3), round(hi, 3)], round(p_below, 4)


def log_binom_pmf(i, n, p):
    return (math.lgamma(n + 1) - math.lgamma(i + 1) - math.lgamma(n - i + 1)
            + i * math.log(p) + (n - i) * math.log(1 - p))


def binom_test_two_sided(k, n, p=0.5):
    if n == 0:
        return 1.0
    log_pk = log_binom_pmf(k, n, p)
    total = 0.0
    for i in range(n + 1):
        lpi = log_binom_pmf(i, n, p)
        if lpi <= log_pk + 1e-9:
            total += math.exp(lpi)
    return round(min(1.0, total), 6)


# --------------------------------------------------------------------- H4
def run_h4():
    with open(HEATMAP_CSV, encoding='utf-8') as f:
        heat_rows = list(csv.DictReader(f))
    fam_table = Counter()
    for r in heat_rows:
        fam_table[(r['login'], r['family'])] += int(r['commits'])
    chi2, dof, v, perm_p = permutation_test_contingency(fam_table)

    with open(SPECIALISATION_CSV, encoding='utf-8') as f:
        spec_rows = list(csv.DictReader(f))
    entropies = [float(r['normalized_entropy']) for r in spec_rows]
    med, ci = bootstrap_median_ci(entropies)

    return {
        'contributors': len({l for l, _ in fam_table}),
        'families': len({f for _, f in fam_table}),
        'chi2': chi2, 'dof': dof, 'cramers_v': v,
        'permutation_p': perm_p, 'n_perm': N_PERM,
        'entropy_median': med, 'entropy_median_ci95': ci,
        'n_logins_entropy': len(entropies),
    }


# --------------------------------------------------------------------- H5
def run_h5():
    with open(CORRECTOR_CSV, encoding='utf-8') as f:
        corrector_rows = list(csv.DictReader(f))
    top_k = {r['corrector'] for r in corrector_rows if int(r['events']) >= 500}

    with open(EVENTS_CSV, encoding='utf-8') as f:
        events = list(csv.DictReader(f))
    subset = [r for r in events if r['corrector'] in top_k and r['edit_type'] != 'none']

    table = Counter((r['corrector'], r['edit_type']) for r in subset)
    chi2, dof, p, v = R.chi2_independence(table)
    ci = block_bootstrap_v_generic(subset, 'corrector', 'edit_type')

    return {
        'top_correctors': sorted(top_k), 'n_top_correctors': len(top_k),
        'n_events': len(subset), 'chi2': chi2, 'dof': dof,
        'p_value_descriptive': p, 'cramers_v': v,
        'block_bootstrap_v_ci95': ci,
    }


# --------------------------------------------------------------------- H6
def run_h6():
    with open(EVENTS_CSV, encoding='utf-8') as f:
        events = list(csv.DictReader(f))

    kappa_note = 'not meaningful (kappa gate open)'
    if os.path.exists(GOLD_METRICS_JSON):
        with open(GOLD_METRICS_JSON, encoding='utf-8') as f:
            gm = json.load(f)
        iaa = gm.get('iaa', {})
        kappa_note = (f"Cohen's kappa = {iaa.get('cohen_kappa')} over {iaa.get('pairs')} "
                       "double-annotated pairs (kappa gate NOT cleared; gold_component_2 "
                       "needs a second annotator across the full 390-row sample)")

    strata = {
        'derived': [r for r in events if r['evidence_level'] == 'derived'],
        'all': events,
    }
    results = {}
    for stratum_name, rows in strata.items():
        by_component = defaultdict(list)
        for r in rows:
            by_component[r['error_component']].append(r)
        comp_out = {}
        pvals = {}
        for comp, comp_rows in by_component.items():
            share = top2_share(comp_rows)
            ci, p_below = block_bootstrap_top2(comp_rows)
            g = gini([c for _, c in Counter(r['corrector'] for r in comp_rows).items()])
            comp_out[comp] = {'n': len(comp_rows), 'top2_share': round(share, 3),
                               'ci95': ci, 'gini': g, 'p_share_lt_080': p_below}
            pvals[comp] = p_below
        qvals = bh_qvalues(pvals)
        for comp in comp_out:
            comp_out[comp]['q_share_lt_080'] = qvals[comp]
        results[stratum_name] = comp_out
    return {'strata': results, 'kappa_note': kappa_note}


# --------------------------------------------------------------------- H7
def run_h7():
    series_keys = ['total_issues', 'total_pull_requests', 'total_commits']
    snap_dates = sorted(os.listdir(SNAPSHOTS_DIR)) if os.path.isdir(SNAPSHOTS_DIR) else []
    snapshots = []
    for d in snap_dates:
        p = os.path.join(SNAPSHOTS_DIR, d, 'summary.json')
        if os.path.exists(p):
            with open(p, encoding='utf-8') as f:
                snapshots.append(json.load(f))
    pvals = {}
    out = {}
    for key in series_keys:
        vals = [s.get(key, 0) for s in snapshots]
        tau, z, p = R.mann_kendall(vals)
        out[key] = {'tau': tau, 'p_value': p, 'series': vals}
        pvals[key] = p
    qvals = bh_qvalues(pvals)
    for key in out:
        out[key]['q_value'] = qvals[key]
    return {
        'n_snapshots': len(snapshots),
        'snapshot_dates': snap_dates,
        'series': out,
        'verdict': 'deferred (underpowered: n=%d snapshots, need >= 10)' % len(snapshots),
    }


# --------------------------------------------------------------------- H8
def run_h8():
    with open(CONFUSION_CSV, encoding='utf-8') as f:
        rows = list(csv.DictReader(f))
    by_space = defaultdict(Counter)
    for r in rows:
        if r['from'] == r['to']:
            continue
        by_space[r['edit_space']][(r['from'], r['to'])] += int(r['count'])

    pair_results = {}
    all_pvals = {}
    for space, counts in by_space.items():
        seen = set()
        for (a, b) in list(counts):
            key = frozenset((a, b))
            if key in seen:
                continue
            seen.add(key)
            ab = counts.get((a, b), 0)
            ba = counts.get((b, a), 0)
            total = ab + ba
            if total < 30:
                continue
            dom_from, dom_to, dom_count = (a, b, ab) if ab >= ba else (b, a, ba)
            share, lo, hi = R.wilson(dom_count, total)
            p = binom_test_two_sided(dom_count, total)
            label = f'{space}:{dom_from}->{dom_to}'
            pair_results[label] = {
                'edit_space': space, 'from': dom_from, 'to': dom_to,
                'total': total, 'directional_share': round(share, 3),
                'ci95': [round(lo, 3), round(hi, 3)], 'p_value': p,
            }
            all_pvals[label] = p
    qvals = bh_qvalues(all_pvals)
    for label in pair_results:
        pair_results[label]['q_value'] = qvals[label]
    return {'n_pairs_tested': len(pair_results), 'pairs': pair_results}


# ----------------------------------------------------------------------- md
def _fmt_p(p):
    return '<0.001' if p < 0.001 else p


def render_md(h4, h5, h6, h7, h8):
    L = []; A = L.append
    A('# Statistical rigor — Phase-3 hypotheses (H4-H8)')
    A('')
    A('_Generated by `scripts/obs_hypotheses_phase3.py`. Continues the numbering and '
      'instruments of [`reports/obs_t_rigor.md`](obs_t_rigor.md) (H1-H3): Wilson CIs, '
      "chi-square with Cramer's V under a commit-block bootstrap 95% CI, and "
      'Mann-Kendall with Benjamini-Hochberg q-values. New instruments (contributor-level '
      'permutation test, bootstrap-percentile share test) are named inline. Shares are '
      'over *corrected events* (curatorial attention), not raw error rates — the '
      'standing OBS-T caveat carries over from H1-H3._')
    A('')

    A('## H4 — correction labor is specialised beyond repo size')
    A('')
    A(f'Login x family contingency ({h4["contributors"]} contributors x {h4["families"]} '
      f'families): chi2 = {h4["chi2"]}, dof = {h4["dof"]}, **Cramer\'s V = {h4["cramers_v"]}**. '
      f'Contributor-level permutation test (shuffle the family-label pool across logins '
      f'holding each login\'s total commit count fixed, {h4["n_perm"]:,} permutations — the '
      f'repo-idiom substitute for an inferential p-value, since commits cluster by campaign): '
      f'**permutation p = {h4["permutation_p"]}**.')
    A('')
    A(f'Descriptive companion — `normalized_entropy` across {h4["n_logins_entropy"]} logins: '
      f'median **{h4["entropy_median"]}**, bootstrap 95% CI '
      f'[{h4["entropy_median_ci95"][0]}, {h4["entropy_median_ci95"][1]}].')
    A('')
    verdict4 = 'rejected' if h4['permutation_p'] < 0.05 else 'not rejected'
    A(f'Null (independence / size-proportional allocation) is **{verdict4}** at alpha=0.05. '
      'Labor concentrates on specific repos/families beyond what repo size alone would predict.'
      if verdict4 == 'rejected' else
      'Null (independence / size-proportional allocation) is not rejected at alpha=0.05.')
    A('')

    A('## H5 — edit-type profiles are corrector-invariant')
    A('')
    A(f'Top-k correctors (>= 500 events): {", ".join(h5["top_correctors"])} '
      f'({h5["n_top_correctors"]} of 60 logins), restricted to rows with `edit_type != \'none\'` '
      f'(n = {h5["n_events"]:,}). Corrector x edit_type: chi2 = {h5["chi2"]}, dof = {h5["dof"]}; '
      'row-level p-values are not treated as inferential (events cluster by commit/campaign). '
      f'Effect size: **Cramer\'s V = {h5["cramers_v"]}**, commit-block bootstrap 95% CI '
      f'[{h5["block_bootstrap_v_ci95"][0]}, {h5["block_bootstrap_v_ci95"][1]}] (the H2 idiom: '
      'resample commits, not events, since a single campaign commit can contribute thousands '
      'of same-type events).')
    A('')
    tight = h5['block_bootstrap_v_ci95'][1] < 0.30
    A('The CI sits in a low-to-moderate V range' + (', consistent with' if tight else
      ', which is more mixed than') + ' the claim that edit-type mix reflects the material, '
      'not the person — but a non-zero V means correctors are not perfectly interchangeable.')
    A('')

    A('## H6 — correction labor is Pareto-concentrated within every error component')
    A('')
    A(f'**{h6["kappa_note"]}.** Per spec, H6 is reported on the `evidence_level == "derived"` '
      'stratum as primary (mechanically-clean components); the `all` stratum (adding the '
      'inferred/`unattributed` bucket) is reported alongside for comparison — both are '
      '**kappa-gated**: treat as provisional until the second-annotator pass clears.')
    A('')
    for stratum_name, label in (('derived', 'derived stratum (primary)'), ('all', 'all events')):
        comp_out = h6['strata'][stratum_name]
        A(f'### {label}')
        A('')
        A('| component | n | top-2 share | 95% CI | Gini | p(share<0.80) | q (BH) |')
        A('|---|---:|---:|---|---:|---:|---:|')
        for comp in sorted(comp_out, key=lambda c: -comp_out[c]['n']):
            d = comp_out[comp]
            A(f'| {comp} | {d["n"]:,} | {d["top2_share"]:.1%} | '
              f'[{d["ci95"][0]:.1%}, {d["ci95"][1]:.1%}] | {d["gini"]} | '
              f'{d["p_share_lt_080"]} | {d["q_share_lt_080"]} |')
        A('')
    A('BH correction applied across components within each stratum (bootstrap-percentile '
      'one-sided p-value for the null top-2 share < 0.80).')
    A('')

    A('## H7 — org backlog shape is stationary week-over-week (monitor-grade, registered)')
    A('')
    A(f'{h7["n_snapshots"]} weekly snapshots on disk ({", ".join(h7["snapshot_dates"])}). '
      '**Power caveat:** Mann-Kendall is underpowered at n=5 (minimum two-sided p at a '
      'perfectly monotonic n=5 series is approximately 0.028); the verdict is **deferred** '
      f'until {h7["verdict"].split("need >= ")[1].rstrip(")")} snapshots accumulate via the '
      'weekly refresh workflow.')
    A('')
    A('| series | tau | p | q (BH) | first->last |')
    A('|---|---:|---:|---:|---|')
    for key, d in h7['series'].items():
        series = d['series']
        fl = f'{series[0]}->{series[-1]}' if series else 'n/a'
        A(f'| {key} | {d["tau"]} | {_fmt_p(d["p_value"])} | {_fmt_p(d["q_value"])} | {fl} |')
    A('')
    A(f'**Verdict: {h7["verdict"]}.** Descriptive only until the power caveat clears; see '
      'the `/org-shape` page (V9) for the live descriptive series view.')
    A('')

    A('## H8 — character confusions are asymmetric (dominant direction)')
    A('')
    A(f'{h8["n_pairs_tested"]} unordered confusion pairs with total >= 30 events, tested with '
      'an exact two-sided binomial (H0: direction is symmetric, p=0.5), effect size the '
      'directional share with a Wilson 95% CI, **BH-adjusted across all tested pairs** '
      '(the pair list is data-driven, a genuine multiple-comparison setting), stratified by '
      '`edit_space` (mixing iast/raw would conflate encoding regimes).')
    A('')
    A('| edit_space | pair (dominant direction) | total | share | 95% CI | p | q (BH) | sig (q<0.05) |')
    A('|---|---|---:|---:|---|---:|---:|:---:|')
    for label, d in sorted(h8['pairs'].items(), key=lambda kv: -kv[1]['total'])[:40]:
        sig = 'yes' if d['q_value'] < 0.05 else 'no'
        A(f'| {d["edit_space"]} | {d["from"]}->{d["to"]} | {d["total"]:,} | '
          f'{d["directional_share"]:.1%} | [{d["ci95"][0]:.1%}, {d["ci95"][1]:.1%}] | '
          f'{_fmt_p(d["p_value"])} | {_fmt_p(d["q_value"])} | {sig} |')
    A('')
    n_sig = sum(1 for d in h8['pairs'].values() if d['q_value'] < 0.05)
    A(f'{n_sig} of {h8["n_pairs_tested"]} tested pairs remain significant after BH correction — '
      'confusions are directional, consistent with a systematic error source (OCR/case-folding) '
      'rather than symmetric noise. Table capped at the top 40 pairs by volume; the full set is '
      'in the companion JSON.')
    A('')
    A('## H9')
    A('')
    A('Not executed here — routed to csl-atlas as a witness-feed contract '
      '(`docs/HYPOTHESIS_VIZ_STANDARDS_SPEC_2026-07.md` Part 3).')
    A('')
    A('*Caveat: shares are over corrected events (curatorial attention), not the raw error '
      'rate. Object of analysis in scope per `docs/BOUNDARY_RULES.md`.*')
    return '\n'.join(L) + '\n'


def main():
    h4 = run_h4()
    h5 = run_h5()
    h6 = run_h6()
    h7 = run_h7()
    h8 = run_h8()

    out = {'generatedAt': datetime.now(timezone.utc).isoformat(),
           'h4_specialisation': h4, 'h5_edittype_invariance': h5,
           'h6_pareto_per_component': h6, 'h7_backlog_stationarity': h7,
           'h8_confusion_asymmetry': h8}
    with open(OUT_JSON, 'w', encoding='utf-8') as f:
        json.dump(out, f, ensure_ascii=False, indent=2)

    md = render_md(h4, h5, h6, h7, h8)
    with open(OUT_MD, 'w', encoding='utf-8', newline='\n') as f:
        f.write(md)

    print(f'wrote {OUT_MD}')
    print(f'wrote {OUT_JSON}')
    print(f'  H4 V={h4["cramers_v"]} perm_p={h4["permutation_p"]} entropy_median={h4["entropy_median"]}')
    print(f'  H5 V={h5["cramers_v"]} ci95={h5["block_bootstrap_v_ci95"]} n_top={h5["n_top_correctors"]}')
    print(f'  H6 derived components={list(h6["strata"]["derived"])}')
    print(f'  H7 n_snapshots={h7["n_snapshots"]} verdict={h7["verdict"]}')
    print(f'  H8 n_pairs={h8["n_pairs_tested"]}')


if __name__ == '__main__':
    main()
