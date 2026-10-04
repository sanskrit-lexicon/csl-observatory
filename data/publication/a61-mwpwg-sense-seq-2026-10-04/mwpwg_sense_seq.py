#!/usr/bin/env python3
"""MW↔PWG sense-sequence concordance — A61 §7.2 open measurement (H5916).

Question (Kapp–Malten 1997, p. 6, fn.): "It may be surmised that MW has largely
followed the order of meanings in PW1."  Cross-language sense matching is not
directly cheap, so order is proxied by the sequence of cited source works
(<ls> sigla) inside each entry: if MW followed PWG's meaning order, citations
to the SAME works should appear at correlated positions in the two entries.

Method: for every headword common to MW and PWG (exact k1 match), extract the
ordered list of citation-work tokens from both entries; for pairs sharing ≥3
distinct works, compute Spearman rho and Kendall tau between first-occurrence
ranks of the shared works.  Controls: (a) permutation null (one side shuffled);
(b) MW(1899) × MW(1872) — same dictionary, two editions — as the method's
high-concordance control; (c) semicolon "sense-count" and length correlations.

Usage:  python3 mwpwg_sense_seq.py <csl-orig-v02-dir> <outdir>
Writes: metrics.csv, summary.json.  Deterministic (seeded).
"""
import json, math, random, re, sys
from collections import Counter, defaultdict
from pathlib import Path

LS_RE = re.compile(r'<ls(?:\s+n="([^"]*)")?[^>]*>(.*?)</ls>', re.S)
FIRST_TOK_RE = re.compile(r'\s*([^\s,;:()]+)')
HAS_LETTER_RE = re.compile(r'[A-Za-zĀĪŪĒōṚṜṢŚṆṄḤṬḌḶāīūēṅñṭḍṇśṣṝṛḥṁ]')


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
    r, seen = {}, {}
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


def concordance(a: dict, b: dict, min_shared: int = 3):
    rows = []
    common = a.keys() & b.keys()
    for k in common:
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


def summarize(rows, label):
    rhos = sorted(r['rho'] for r in rows)
    if not rhos:
        return {'label': label, 'n_pairs': 0}
    n = len(rhos)
    med = rhos[n // 2] if n % 2 else (rhos[n // 2 - 1] + rhos[n // 2]) / 2
    return {
        'label': label, 'n_pairs': len(rows),
        'rho_median': round(med, 4),
        'rho_mean': round(sum(rhos) / n, 4),
        'rho_q25': round(rhos[n // 4], 4), 'rho_q75': round(rhos[(3 * n) // 4], 4),
        'share_rho_gt_0.5': round(sum(1 for r in rhos if r > 0.5) / n, 4),
        'share_rho_lt_neg0.5': round(sum(1 for r in rhos if r < -0.5) / n, 4),
    }


def pearson(pairs):
    n = len(pairs)
    if n < 2:
        return None
    mx = sum(p[0] for p in pairs) / n
    my = sum(p[1] for p in pairs) / n
    num = sum((x - mx) * (y - my) for x, y in pairs)
    den = math.sqrt(sum((x - mx) ** 2 for x, _ in pairs) * sum((y - my) ** 2 for _, y in pairs))
    return round(num / den, 4) if den else None


def main():
    v02, outdir = Path(sys.argv[1]), Path(sys.argv[2])
    outdir.mkdir(parents=True, exist_ok=True)
    rng = random.Random(20261004)

    mw = parse_dict(v02 / 'mw' / 'mw.txt')
    pwg = parse_dict(v02 / 'pwg' / 'pwg.txt')
    pw = parse_dict(v02 / 'pw' / 'pw.txt')

    common = mw.keys() & pwg.keys()
    rows = concordance(mw, pwg)
    ctrl_ed = concordance(pw, pwg)

    # permutation null on the MW×PWG pairs (one side's token order shuffled)
    null_rows = []
    for r in rows:
        k = r['k1']
        toks = list(mw[k]['tokens'])
        rng.shuffle(toks)
        ra, rb = first_ranks(toks), first_ranks(pwg[k]['tokens'])
        shared = sorted(ra.keys() & rb.keys())
        if len(shared) < 3:
            continue
        rho = spearman([ra[t] for t in shared], [rb[t] for t in shared])
        if rho is not None:
            null_rows.append(rho)

    # cross-pair null: MW entry of lemma X vs PWG entry of a DIFFERENT lemma Y
    # (catches global citation-order conventions, e.g. 'Vedic sources first')
    keys = [r['k1'] for r in rows]
    cross = []
    tries = 0
    while len(cross) < min(5000, len(rows)) and tries < 60000:
        tries += 1
        kx = keys[rng.randrange(len(keys))]
        ky = keys[rng.randrange(len(keys))]
        if kx == ky:
            continue
        ra, rb = first_ranks(mw[kx]['tokens']), first_ranks(pwg[ky]['tokens'])
        shared = sorted(ra.keys() & rb.keys())
        if len(shared) < 3:
            continue
        rho = spearman([ra[t] for t in shared], [rb[t] for t in shared])
        if rho is not None:
            cross.append(rho)

    semi_pairs = [(mw[k]['semis'], pwg[k]['semis']) for k in common
                  if mw[k]['semis'] >= 1 and pwg[k]['semis'] >= 1]
    summary = {
        'method': 'citation-siglum first-occurrence rank concordance over k1-exact common headwords; >=3 shared works per pair',
        'counts': {
            'mw_entries': len(mw), 'pwg_entries': len(pwg), 'pw_entries': len(pw),
            'common_k1': len(common), 'pairs_ge3_shared': len(rows),
        },
        'mwpwg': summarize(rows, 'MW(1899) x PWG'),
        'control_same_dict_editions': summarize(ctrl_ed, 'PW(1879) x PWG — same-author condensation control'),
        'null_permutation': {
            'n': len(null_rows),
            'rho_mean': round(sum(null_rows) / len(null_rows), 4) if null_rows else None,
        },
        'null_crosspair': {
            'n': len(cross),
            'rho_median': (lambda v: round(sorted(v)[len(v)//2], 4) if v else None)(cross),
            'rho_mean': round(sum(cross) / len(cross), 4) if cross else None,
            'note': 'MW lemma X vs PWG lemma Y!=X; detects global siglum-order conventions',
        },
        'semis_pearson_mwpwg': pearson(semi_pairs),
        'seed': 20261004,
    }
    (outdir / 'summary.json').write_text(json.dumps(summary, indent=1, ensure_ascii=False))
    with (outdir / 'metrics.csv').open('w', encoding='utf-8') as fh:
        fh.write('k1,n_shared,shared_jaccard,rho,tau,semis_mw,semis_pwg\n')
        for r in sorted(rows, key=lambda r: r['k1']):
            fh.write(f"{r['k1']},{r['n_shared']},{r['shared_jaccard']},{r['rho']},{r['tau']},{r['semis_a']},{r['semis_b']}\n")
    print(json.dumps(summary['counts']))
    print(json.dumps(summary['mwpwg']))
    print(json.dumps(summary['control_same_dict_editions']))
    print(json.dumps(summary['null_permutation']), json.dumps(summary['null_crosspair']), 'semis_pearson:', summary['semis_pearson_mwpwg'])


if __name__ == '__main__':
    main()
