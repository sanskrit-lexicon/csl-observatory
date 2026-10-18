#!/usr/bin/env python3
"""Six-dictionary pairwise sense-sequence concordance matrix — A61 §7.2 extension (H6051).

Extends the MW↔PWG measurement of `a61-mwpwg-sense-seq-2026-10-04` (H5916) to ALL 15
unordered pairs of the six dictionaries of the A61 verification base, same protocol:
PWG  Böhtlingk & Roth, Sanskrit-Wörterbuch (1855–1875, the large Petersburg)
PW   Böhtlingk, Sanskrit-Wörterbuch in kürzerer Fassung (1879–1889)
MW   Monier-Williams (1899)
SCH  Schmidt, Nachträge zum Sanskrit-Wörterbuch (1928)
ACC  Aufrecht, Catalogus Catalogorum
PWKVN  Böhtlingk kürzerer Fassung — Nachträge und Verbesserungen

Meaning order is proxied by the sequence of cited source works (<ls> sigla) inside each
entry (cross-language sense matching is impractical at this scale): for every headword
common to both dictionaries (exact k1 match), the first-occurrence ranks of works cited
by BOTH entries are correlated (Spearman ρ, Kendall τ); pairs with <3 shared works are
excluded.  Controls per pair: within-entry permutation null (first side shuffled) and a
cross-lemma null (entry of lemma X vs entry of a different lemma Y — detects global
siglum-order conventions such as "Vedic sources first").  PW×PWG doubles as the
condensation control (the same author abridging his own large dictionary).

ACC carries no <ls> markup at all (its citations are plain text — it is a bio-
bibliographic catalog, not a sense dictionary), so every ACC pair is a structural null:
the method's precondition fails, and the matrix reports it as such rather than by
inventing a second, non-comparable tokenizer.

Usage:  python3 sixdict_sense_seq_matrix.py <csl-orig-v02-dir> <outdir>
Writes: matrix.csv, summary.json, metrics/<A>-<B>.csv (one per pair).  Deterministic
(sorted iteration; per-pair seeded RNGs).
"""
import json, math, random, re, sys
from collections import defaultdict
from pathlib import Path

LS_RE = re.compile(r'<ls(?:\s+n="([^"]*)")?[^>]*>(.*?)</ls>', re.S)
FIRST_TOK_RE = re.compile(r'\s*([^\s,;:()]+)')
HAS_LETTER_RE = re.compile(r'[A-Za-zĀĪŪĒōṚṜṢŚṆṄḤṬḌḶāīūēṅñṭḍṇśṣṝṛḥṁ]')

DICTS = [
    ('PWG', 'pwg', 'Böhtlingk & Roth 1855–1875'),
    ('PW', 'pw', 'Böhtlingk kürzerer Fassung 1879–1889'),
    ('MW', 'mw', 'Monier-Williams 1899'),
    ('SCH', 'sch', 'Schmidt Nachträge 1928'),
    ('ACC', 'acc', 'Aufrecht Catalogus Catalogorum'),
    ('PWKVN', 'pwkvn', 'PW kürzerer Fassung, Nachträge und Verbesserungen'),
]
MIN_SHARED = 3
SEED = 20261004
CROSS_NULL_N = 5000


def work_token(n_attr: str | None, text: str) -> str | None:
    src = (n_attr or '').strip() or (text or '').strip()
    m = FIRST_TOK_RE.match(src)
    if not m:
        return None
    tok = m.group(1).rstrip('.,;:')
    if not tok or not HAS_LETTER_RE.search(tok):
        return None
    if re.fullmatch(r'[0-9IVXLC]+', tok):   # bare passage numbers / book nums
        return None
    if len(tok) > 24:                        # prose, not a siglum
        return None
    return tok.upper()


def parse_dict(path: Path) -> dict[str, dict]:
    """k1 -> {'tokens': [...], 'semis': int, 'chars': int} (homonym bodies concatenated in file order)."""
    out: dict[str, dict] = {}
    k1, body, in_entry = None, [], False
    with path.open(encoding='utf-8', errors='replace') as fh:
        for line in fh:
            if line.startswith('<L>'):
                m = re.search(r'<k1>([^<\n]*)', line)
                k1 = m.group(1).strip() if m else ''
                body, in_entry = [], bool(k1)
            elif in_entry:
                if line.startswith('<LEND>'):
                    text = ''.join(body)
                    toks = []
                    for n_attr, txt in LS_RE.findall(text):
                        t = work_token(n_attr, txt)
                        if t:
                            toks.append(t)
                    rec = out.setdefault(k1, {'tokens': [], 'semis': 0, 'chars': 0})
                    rec['tokens'].extend(toks)
                    rec['semis'] += text.count(';')
                    rec['chars'] += len(text)
                    in_entry = False
                else:
                    body.append(line)
    return out


def first_ranks(tokens: list[str]) -> dict[str, float]:
    seen = {}
    for i, t in enumerate(tokens):
        if t not in seen:
            seen[t] = i
    n = max(len(tokens), 1)
    return {t: i / n for t, i in seen.items()}


def spearman(xs, ys):
    n = len(xs)
    if n < 2:
        return None
    def _r(v):
        order = sorted(range(n), key=lambda i: v[i])
        rk = [0.0] * n
        i = 0
        while i < n:
            j = i
            while j + 1 < n and v[order[j + 1]] == v[order[i]]:
                j += 1
            avg = (i + j) / 2 + 1
            for k2 in range(i, j + 1):
                rk[order[k2]] = avg
            i = j + 1
        return rk
    rx, ry = _r(xs), _r(ys)
    mx, my = sum(rx) / n, sum(ry) / n
    num = sum((a - mx) * (b - my) for a, b in zip(rx, ry))
    den = math.sqrt(sum((a - mx) ** 2 for a in rx) * sum((b - my) ** 2 for b in ry))
    return num / den if den else None


def kendall(xs, ys):
    n = len(xs)
    if n < 2:
        return None
    c = d = 0
    for i in range(n):
        for j in range(i + 1, n):
            s = (xs[i] - xs[j]) * (ys[i] - ys[j])
            if s > 0:
                c += 1
            elif s < 0:
                d += 1
    return (c - d) / (c + d) if (c + d) else None


def concordance(a: dict, b: dict, min_shared: int = MIN_SHARED):
    rows = []
    for k in sorted(a.keys() & b.keys()):
        ra, rb = first_ranks(a[k]['tokens']), first_ranks(b[k]['tokens'])
        shared = sorted(ra.keys() & rb.keys())
        if len(shared) < min_shared:
            continue
        xs = [ra[t] for t in shared]
        ys = [rb[t] for t in shared]
        rho, tau = spearman(xs, ys), kendall(xs, ys)
        if rho is None:
            continue
        rows.append({
            'k1': k, 'n_shared': len(shared),
            'shared_jaccard': len(shared) / len(ra.keys() | rb.keys()),
            'rho': round(rho, 4),
            'tau': round(tau, 4) if tau is not None else '',
            'semis_a': a[k]['semis'], 'semis_b': b[k]['semis'],
        })
    return rows


def median(v):
    v = sorted(v)
    if not v:
        return None
    n = len(v)
    return v[n // 2] if n % 2 else (v[n // 2 - 1] + v[n // 2]) / 2


def summarize(rows, label):
    rhos = [r['rho'] for r in rows]
    taus = [r['tau'] for r in rows if r['tau'] != '']
    if not rhos:
        return {'label': label, 'n_pairs': 0}
    rhos_sorted = sorted(rhos)
    n = len(rhos_sorted)
    out = {
        'label': label, 'n_pairs': len(rows),
        'rho_median': round(median(rhos), 4),
        'rho_mean': round(sum(rhos) / n, 4),
        'rho_q25': round(rhos_sorted[n // 4], 4), 'rho_q75': round(rhos_sorted[(3 * n) // 4], 4),
        'share_rho_gt_0.5': round(sum(1 for r in rhos if r > 0.5) / n, 4),
        'share_rho_lt_neg0.5': round(sum(1 for r in rhos if r < -0.5) / n, 4),
    }
    if taus:
        out['tau_median'] = round(median(taus), 4)
    return out


def pearson(pairs):
    n = len(pairs)
    if n < 2:
        return None
    mx = sum(p[0] for p in pairs) / n
    my = sum(p[1] for p in pairs) / n
    num = sum((x - mx) * (y - my) for x, y in pairs)
    den = math.sqrt(sum((x - mx) ** 2 for x, _ in pairs) * sum((y - my) ** 2 for _, y in pairs))
    return round(num / den, 4) if den else None


def pair_study(a: dict, b: dict, code_a: str, code_b: str, rng: random.Random):
    """Observed concordance + both nulls for one unordered pair (a = first side; nulls shuffle a)."""
    common = a.keys() & b.keys()
    rows = concordance(a, b)

    null_rows = []
    for r in rows:                       # rows are k1-sorted -> deterministic rng order
        toks = list(a[r['k1']]['tokens'])
        rng.shuffle(toks)
        ra, rb = first_ranks(toks), first_ranks(b[r['k1']]['tokens'])
        shared = sorted(ra.keys() & rb.keys())
        if len(shared) < MIN_SHARED:
            continue
        rho = spearman([ra[t] for t in shared], [rb[t] for t in shared])
        if rho is not None:
            null_rows.append(rho)

    keys = [r['k1'] for r in rows]
    cross = []
    tries = 0
    while keys and len(cross) < min(CROSS_NULL_N, len(rows)) and tries < 60000:
        tries += 1
        kx = keys[rng.randrange(len(keys))]
        ky = keys[rng.randrange(len(keys))]
        if kx == ky:
            continue
        ra, rb = first_ranks(a[kx]['tokens']), first_ranks(b[ky]['tokens'])
        shared = sorted(ra.keys() & rb.keys())
        if len(shared) < MIN_SHARED:
            continue
        rho = spearman([ra[t] for t in shared], [rb[t] for t in shared])
        if rho is not None:
            cross.append(rho)

    semi_pairs = [(a[k]['semis'], b[k]['semis']) for k in common
                  if a[k]['semis'] >= 1 and b[k]['semis'] >= 1]
    return {
        'n_common_k1': len(common),
        'observed': summarize(rows, f'{code_a} x {code_b}'),
        'null_permutation': {
            'n': len(null_rows),
            'rho_mean': round(sum(null_rows) / len(null_rows), 4) if null_rows else None,
        },
        'null_crosspair': {
            'n': len(cross),
            'rho_median': round(median(cross), 4) if cross else None,
            'rho_mean': round(sum(cross) / len(cross), 4) if cross else None,
            'note': f'{code_a} lemma X vs {code_b} lemma Y!=X; detects global siglum-order conventions',
        },
        'semis_pearson': pearson(semi_pairs),
        '_rows': rows,
    }


def main():
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')
    v02, outdir = Path(sys.argv[1]), Path(sys.argv[2])
    (outdir / 'metrics').mkdir(parents=True, exist_ok=True)

    dicts = {}
    for code, slug, label in DICTS:
        dicts[code] = parse_dict(v02 / slug / f'{slug}.txt')
        print(f'parsed {code}: {len(dicts[code])} k1 keys', file=sys.stderr)

    pairs_summary = {}
    for idx in range(len(DICTS)):
        for jdx in range(idx + 1, len(DICTS)):
            code_a, _, label_a = DICTS[idx]
            code_b, _, label_b = DICTS[jdx]
            rng = random.Random(SEED + idx * 10 + jdx)
            res = pair_study(dicts[code_a], dicts[code_b], code_a, code_b, rng)
            rows = res.pop('_rows')
            pairs_summary[f'{code_a}x{code_b}'] = res
            with (outdir / 'metrics' / f'{code_a.lower()}-{code_b.lower()}.csv').open('w', encoding='utf-8') as fh:
                fh.write('k1,n_shared,shared_jaccard,rho,tau,semis_a,semis_b\n')
                for r in rows:
                    fh.write(f"{r['k1']},{r['n_shared']},{r['shared_jaccard']},{r['rho']},{r['tau']},{r['semis_a']},{r['semis_b']}\n")
            obs = res['observed']
            print(f"{code_a}x{code_b}: common={res['n_common_k1']} pairs={obs.get('n_pairs', 0)}"
                  f" rho_med={obs.get('rho_median', 'NA')} perm={res['null_permutation']['rho_mean']}"
                  f" cross={res['null_crosspair']['rho_median']}", file=sys.stderr)

    with (outdir / 'matrix.csv').open('w', encoding='utf-8') as fh:
        fh.write('pair_a,pair_b,label_a,label_b,n_common_k1,n_pairs_ge3,'
                 'rho_median,rho_mean,rho_q25,rho_q75,share_rho_gt_0.5,share_rho_lt_neg0.5,tau_median,'
                 'perm_null_mean,cross_null_n,cross_null_median,cross_null_mean,semis_pearson\n')
        for idx in range(len(DICTS)):
            for jdx in range(idx + 1, len(DICTS)):
                code_a, _, label_a = DICTS[idx]
                code_b, _, label_b = DICTS[jdx]
                r = pairs_summary[f'{code_a}x{code_b}']
                o = r['observed']
                fh.write(f"{code_a},{code_b},\"{label_a}\",\"{label_b}\",{r['n_common_k1']},"
                         f"{o.get('n_pairs', 0)},{o.get('rho_median', '')},{o.get('rho_mean', '')},"
                         f"{o.get('rho_q25', '')},{o.get('rho_q75', '')},{o.get('share_rho_gt_0.5', '')},"
                         f"{o.get('share_rho_lt_neg0.5', '')},{o.get('tau_median', '')},"
                         f"{r['null_permutation']['rho_mean']},{r['null_crosspair']['n']},"
                         f"{r['null_crosspair']['rho_median']},{r['null_crosspair']['rho_mean']},"
                         f"{r['semis_pearson'] if r['semis_pearson'] is not None else ''}\n")

    summary = {
        'method': 'citation-siglum first-occurrence rank concordance over k1-exact common headwords; '
                  f'>={MIN_SHARED} shared works per pair; extends a61-mwpwg-sense-seq-2026-10-04 (H5916) to all 15 pairs',
        'dictionaries': {code: {'entries_k1': len(dicts[code]), 'label': label}
                         for code, _, label in DICTS},
        'pairs': pairs_summary,
        'condensation_control': 'PWxPWG — same-author abridgement; H5916 anchor median rho 0.30',
        'structural_null': 'ACC carries no <ls> markup (bio-bibliographic catalog, plain-text citations): '
                           'every ACC pair has 0 measurable rows under this protocol',
        'seed': SEED,
    }
    (outdir / 'summary.json').write_text(json.dumps(summary, indent=1, ensure_ascii=False))
    print('done', file=sys.stderr)


if __name__ == '__main__':
    main()
