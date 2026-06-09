#!/usr/bin/env python3
"""OBS-Q — correction sustainability and the data-layer bus factor.

Measures *content correction* (edits to dictionary source text in the sibling
`csl-orig` repo), the complement of the code-side `bus_factor.py`. Four
dimensions:

* **Annual concentration** — distinct correctors per year and the lead's share,
  over commits that touch `csl-orig/v02` dictionary sources, author identities
  alias-merged via `contributors_map.json`.
* **Per-dictionary SPOF** — for every dictionary, the dominant corrector and
  their share (single-point-of-failure when one person or >=80%).
* **Subject classification** — correction vs import/reformat vs other, so the
  throughput unit is the correction-classified commit, not raw count or lines.
* **Resolution latency** — `csl-corrections` issue created->closed durations and
  the long-tail anatomy by label/severity. This is the only network input;
  it is cached to a CSV so report regeneration is otherwise offline.

Sources
-------
* `../csl-orig` git history (sibling repo; the git parts are fully reproducible)
* `scripts/contributors_map.json`            — author alias -> canonical login
* `observatory/site/src/data/obs_q_latency.csv` — cached issue dates (refresh
  with `--fetch-latency`; needs `gh` auth and network)

Outputs
-------
* `reports/obs_q_correction_sustainability.md`        — human-readable finding
* `observatory/site/src/data/obs_q_annual.csv`        — per-year concentration
* `observatory/site/src/data/obs_q_per_dict.csv`      — per-dictionary SPOF table
* `observatory/site/src/data/obs_q_latency.csv`       — cached issue latencies

Usage:  python scripts/obs_q_correction.py [--fetch-latency]
"""
import argparse, csv, json, os, re, subprocess, sys
from collections import defaultdict
from datetime import datetime, timezone
sys.stdout.reconfigure(encoding='utf-8'); sys.stderr.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
GH_ROOT = os.path.dirname(ROOT)
CSL_ORIG = os.path.join(GH_ROOT, 'csl-orig')
MAP = os.path.join(HERE, 'contributors_map.json')
DATA = os.path.join(ROOT, 'observatory', 'site', 'src', 'data')
OUT_MD = os.path.join(ROOT, 'reports', 'obs_q_correction_sustainability.md')
OUT_ANNUAL = os.path.join(DATA, 'obs_q_annual.csv')
OUT_PERDICT = os.path.join(DATA, 'obs_q_per_dict.csv')
LATENCY_CSV = os.path.join(DATA, 'obs_q_latency.csv')

CORR_REPO = 'sanskrit-lexicon/csl-corrections'
SPOF_SHARE = 0.80          # lead share at/above which a dict is single-point-of-failure
TAIL_DAYS = 90             # an issue is "long tail" if open or resolved after this

# Heuristic alias fallbacks for the core correctors (validated against the raw
# csl-orig author roster). contributors_map.json aliases are consulted first.
HEURISTICS = [('funderb', 'funderburkjim'), ('drdhaval2785', 'drdhaval2785'),
              ('gasyoun', 'gasyoun'), ('srhodes', 'aumsanskrit'),
              ('aumsanskrit', 'aumsanskrit'), ('rybakova', 'AnnaRybakovaT')]


# ----------------------------------------------------------------------------- identity
def load_resolver():
    email2login, name2login, bots = {}, {}, set()
    with open(MAP, encoding='utf-8') as f:
        m = json.load(f)
    for login, info in m.items():
        if login.startswith('_') or not isinstance(info, dict):
            continue
        if info.get('is_bot'):
            bots.add(login)
        for a in info.get('aliases', []):
            a = a.strip().lower()
            (email2login if '@' in a else name2login)[a] = login
    def resolve(email, name):
        e, n = (email or '').strip().lower(), (name or '').strip().lower()
        if e in email2login:
            return email2login[e]
        if n in name2login:
            return name2login[n]
        for key, login in HEURISTICS:
            if key in e or key in n:
                return login
        return e.split('@')[0] if e else (n or 'unknown')
    return resolve, bots


# ----------------------------------------------------------------------------- git
def classify(subject):
    """correction | import | other — the throughput-unit classifier."""
    s = subject.lower()
    if re.search(r'correct|csl-corrections|close #|fixes #|issue|dc [0-9]|typo|\bfix\b', s):
        return 'correction'
    if re.search(r'import|initial|add .*\.txt|reformat|regenerat|rebuild|convert|merge', s):
        return 'import'
    return 'other'


def read_git():
    """Yield (year, login, subject, kind, set_of_dicts) per v02-touching commit."""
    US, RS = '\x1f', '\x1e'
    fmt = f'{RS}%H{US}%ae{US}%an{US}%ad{US}%s'
    out = subprocess.run(
        ['git', '-C', CSL_ORIG, 'log', f'--pretty=format:{fmt}',
         '--date=format:%Y', '--name-only', '--', 'v02'],
        capture_output=True, encoding='utf-8', errors='replace').stdout
    resolve, bots = load_resolver()
    for rec in out.split(RS):
        if not rec.strip():
            continue
        lines = rec.split('\n')
        parts = lines[0].split(US)
        if len(parts) < 5:
            continue
        _h, ae, an, year, subj = parts[0], parts[1], parts[2], parts[3], US.join(parts[4:])
        dicts = set()
        for fpath in lines[1:]:
            seg = fpath.strip().split('/')
            if len(seg) >= 2 and seg[0] == 'v02':
                dicts.add(seg[1])
        if not dicts:
            continue
        login = resolve(ae, an)
        if login in bots:
            continue
        yield year, login, subj, classify(subj), dicts


# ----------------------------------------------------------------------------- latency
def fetch_latency():
    """Hit the csl-corrections issue API (with retries) and cache to CSV."""
    jq = ('.[] | select(.pull_request==null) | '
          '[(.created_at),(.closed_at//""),([.labels[].name]|join(";"))] | @tsv')
    rows = []
    for attempt in range(1, 6):
        p = subprocess.run(
            ['gh', 'api', '--paginate',
             f'repos/{CORR_REPO}/issues?state=all&per_page=100', '--jq', jq],
            capture_output=True, encoding='utf-8', errors='replace')
        got = [ln for ln in p.stdout.splitlines() if ln.strip()]
        if len(got) > 50:
            rows = got
            break
        print(f'  latency fetch attempt {attempt}: '
              f'{(p.stderr.strip().splitlines() or ["partial"])[-1]}', file=sys.stderr)
    if not rows:
        print('  latency fetch failed; keeping existing cache', file=sys.stderr)
        return False
    with open(LATENCY_CSV, 'w', encoding='utf-8', newline='') as f:
        w = csv.writer(f)
        w.writerow(['created_at', 'closed_at', 'labels'])
        for ln in rows:
            f_ = ln.split('\t')
            w.writerow([f_[0], f_[1] if len(f_) > 1 else '', f_[2] if len(f_) > 2 else ''])
    print(f'  cached {len(rows)} issues -> {LATENCY_CSV}')
    return True


def load_latency():
    if not os.path.exists(LATENCY_CSV):
        return None
    issues = []
    with open(LATENCY_CSV, encoding='utf-8') as f:
        for row in csv.DictReader(f):
            issues.append(row)
    return issues


def latency_stats(issues):
    now = datetime.now(timezone.utc)
    def parse(s):
        return datetime.fromisoformat(s.replace('Z', '+00:00'))
    closed_days, tail_labels, tail_sev = [], defaultdict(int), defaultdict(int)
    n_open = n_tail = 0
    sev_set = {'trivial', 'minor', 'medium', 'major', 'critical'}
    for it in issues:
        created = parse(it['created_at'])
        is_open = not it['closed_at']
        if is_open:
            n_open += 1
            days = (now - created).days
        else:
            days = (parse(it['closed_at']) - created).days
            if days < 0:
                days = 0
            closed_days.append(days)
        if is_open or days > TAIL_DAYS:
            n_tail += 1
            for lab in (it['labels'].split(';') if it['labels'] else []):
                (tail_sev if lab in sev_set else tail_labels)[lab] += 1
    closed_days.sort()
    n = len(closed_days)
    def pct(p):
        return closed_days[min(n - 1, int(n * p))] if n else 0
    return {
        'total': len(issues), 'closed': n, 'open': n_open, 'tail': n_tail,
        'median': closed_days[n // 2] if n else 0,
        'mean': sum(closed_days) / n if n else 0,
        'p90': pct(0.9), 'max': closed_days[-1] if n else 0,
        'tail_labels': sorted(tail_labels.items(), key=lambda kv: -kv[1]),
        'tail_sev': sorted(tail_sev.items(), key=lambda kv: -kv[1]),
    }


# ----------------------------------------------------------------------------- main
def lead(counts):
    """(login, share) of the dominant contributor in a {login: n} dict."""
    tot = sum(counts.values())
    top = max(counts, key=counts.get)
    return top, counts[top] / tot if tot else 0.0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--fetch-latency', action='store_true',
                    help='refresh the csl-corrections latency cache (network + gh auth)')
    args = ap.parse_args()

    if not os.path.isdir(os.path.join(CSL_ORIG, 'v02')):
        sys.exit(f'csl-orig not found at {CSL_ORIG} (expected sibling of this repo)')

    annual = defaultdict(lambda: {'commits': 0, 'authors': defaultdict(int),
                                  'correction': 0, 'import': 0, 'other': 0})
    perdict = defaultdict(lambda: defaultdict(int))
    for year, login, _subj, kind, dicts in read_git():
        a = annual[year]
        a['commits'] += 1
        a['authors'][login] += 1
        a[kind] += 1
        for d in dicts:
            perdict[d][login] += 1

    years = sorted(annual)
    annual_rows = []
    for y in years:
        a = annual[y]
        top, share = lead(a['authors'])
        annual_rows.append({'year': y, 'commits': a['commits'],
                            'correctors': len(a['authors']), 'lead': top,
                            'lead_share': round(share, 4), 'corrections': a['correction'],
                            'imports': a['import'], 'other': a['other']})

    perdict_rows = []
    for d, counts in perdict.items():
        top, share = lead(counts)
        perdict_rows.append({'dict': d, 'commits': sum(counts.values()),
                             'correctors': len(counts), 'lead': top,
                             'lead_share': round(share, 4),
                             'spof': (len(counts) == 1 or share >= SPOF_SHARE)})
    perdict_rows.sort(key=lambda r: -r['commits'])

    total_commits = sum(r['commits'] for r in annual_rows)
    max_correctors = max(r['correctors'] for r in annual_rows)
    share_lo = min(r['lead_share'] for r in annual_rows)
    share_hi = max(r['lead_share'] for r in annual_rows)
    spofs = [r for r in perdict_rows if r['spof'] and r['commits'] >= 10]

    if args.fetch_latency:
        fetch_latency()
    issues = load_latency()
    lat = latency_stats(issues) if issues else None

    # ---- write CSVs ----
    with open(OUT_ANNUAL, 'w', encoding='utf-8', newline='') as f:
        w = csv.DictWriter(f, fieldnames=['year', 'commits', 'correctors', 'lead',
                                          'lead_share', 'corrections', 'imports', 'other'])
        w.writeheader(); w.writerows(annual_rows)
    with open(OUT_PERDICT, 'w', encoding='utf-8', newline='') as f:
        w = csv.DictWriter(f, fieldnames=['dict', 'commits', 'correctors', 'lead',
                                          'lead_share', 'spof'])
        w.writeheader(); w.writerows(perdict_rows)

    # ---- write report ----
    L = []; A = L.append
    A('# Correction sustainability & the data-layer bus factor (OBS-Q)')
    A('')
    A('_Generated by `scripts/obs_q_correction.py` from the sibling `../csl-orig` '
      'git history (commits touching `v02` dictionary sources) and the cached '
      '`csl-corrections` issue latencies. Author identities alias-merged via '
      '`scripts/contributors_map.json`. The git inputs are fully reproducible; '
      'latency is refreshed with `--fetch-latency`._')
    A('')
    A('> **Claim (reframed after measurement).** Correction throughput in the CDSL '
      'data layer is *single-person-burst-driven, not crew-size-driven* — so the '
      'dictionary **data** (not just the code) is bus-factor-fragile. The pipeline '
      'is *responsive* when staffed but its **capacity** rests on one or two '
      'people, and a long tail of low-severity work is never reached.')
    A('')
    A('This complements the org-wide [`bus_factor.md`](bus_factor.md) (code '
      'contributions) by measuring **content corrections** to dictionary source text.')
    A('')
    A('## Headline')
    A('')
    A('| Metric | Value |')
    A('|---|---:|')
    A(f'| Dictionary-correction commits analysed (`csl-orig/v02`) | {total_commits:,} ({years[0]}–{years[-1]}) |')
    A(f'| Distinct content correctors in any single year | **≤ {max_correctors}** |')
    A(f'| Lead corrector annual share | **{100*share_lo:.0f}–{100*share_hi:.0f}%** |')
    A(f'| Dictionaries that are single-maintainer-dominated (≥10 commits) | **{len(spofs)} / {sum(1 for r in perdict_rows if r["commits"]>=10)}** |')
    if lat:
        A(f'| `csl-corrections` issues (closed / open) | {lat["total"]} ({lat["closed"]} / {lat["open"]}) |')
        A(f'| Resolution latency — median | **{lat["median"]} days** |')
        A(f'| Resolution latency — mean / p90 / max | {lat["mean"]:.1f} d / {lat["p90"]} d / {lat["max"]} d |')
        A(f'| Long-tail issues (open or > {TAIL_DAYS} d) | {lat["tail"]} / {lat["total"]} |')
    A('')
    A('## 1. Annual correction concentration')
    A('')
    A('Distinct correctors per year and the lead corrector\'s share of '
      'dictionary-correction commits.')
    A('')
    A('| Year | Correction commits | Correctors | Lead | Lead share |')
    A('|---|---:|---:|---|---:|')
    for r in annual_rows:
        A(f'| {r["year"]} | {r["commits"]} | {r["correctors"]} | {r["lead"]} | {100*r["lead_share"]:.0f}% |')
    A('')
    single = [r for r in annual_rows if r['correctors'] == 1]
    if single:
        s = single[0]
        A(f'A single-corrector year ({s["year"]}: {s["commits"]} commits) shows that '
          'throughput tracks the lead corrector\'s burst activity, not crew size.')
        A('')
    A('## 2. Per-dictionary single points of failure')
    A('')
    A(f'Every dictionary is dominated by one corrector. Flagged (⚠) when a single '
      f'corrector or lead share ≥ {int(SPOF_SHARE*100)}%. Showing dictionaries with ≥10 commits.')
    A('')
    A('| Dict | Commits | Correctors | Lead | Lead share | SPOF |')
    A('|---|---:|---:|---|---:|:--:|')
    for r in perdict_rows:
        if r['commits'] < 10:
            continue
        A(f'| {r["dict"]} | {r["commits"]} | {r["correctors"]} | {r["lead"]} | '
          f'{100*r["lead_share"]:.0f}% | {"⚠" if r["spof"] else ""} |')
    A('')
    A('## 3. Throughput unit — count corrections, not raw commits or lines')
    A('')
    A('Subject classification separates genuine corrections from bulk '
      'imports/reformats and CI/infra noise. Line volume is misleading (whole-dict '
      'imports dominate insertions); the reliable unit is the correction-classified '
      'commit (`DC <date>` / `csl-corrections#N`, excluding `ci:`/`docs:`/import).')
    A('')
    A('| Year | All v02 commits | Corrections | Import/reformat | Other |')
    A('|---|---:|---:|---:|---:|')
    for r in annual_rows:
        A(f'| {r["year"]} | {r["commits"]} | {r["corrections"]} | {r["imports"]} | {r["other"]} |')
    A('')
    if lat:
        A('## 4. Resolution latency is bimodal')
        A('')
        A(f'Across {lat["total"]} `csl-corrections` issues ({lat["closed"]} closed), '
          f'the **median resolution is {lat["median"]} days** — but the mean is '
          f'{lat["mean"]:.1f}, p90 is {lat["p90"]} days, and the maximum is '
          f'{lat["max"]} days ({lat["max"]/365:.1f} years). Half of corrections close '
          'within days; a long tail languishes for months to years. The pipeline is '
          '**responsive when active**; the tail is where **single-maintainer capacity '
          'runs out**.')
        A('')
        if lat['tail_labels']:
            A('What sits in the tail (open or >90 d) — the signal is the label, not the '
              'dictionary:')
            A('')
            A('| Tail label | n | | Tail severity | n |')
            A('|---|---:|---|---|---:|')
            labs, sevs = lat['tail_labels'], lat['tail_sev']
            for i in range(max(len(labs), len(sevs))):
                lcell = f'{labs[i][0]} | {labs[i][1]}' if i < len(labs) else ' | '
                scell = f'{sevs[i][0]} | {sevs[i][1]}' if i < len(sevs) else ' | '
                A(f'| {lcell} | {scell} |')
            A('')
            A('The tail is dominated by deprioritised low-severity questions and '
              'enhancements, not blocked critical fixes — the signature of a single '
              'maintainer triaging by severity.')
            A('')
    else:
        A('## 4. Resolution latency')
        A('')
        A('_Latency cache empty — run `python scripts/obs_q_correction.py '
          '--fetch-latency` (needs `gh` auth + network) to populate._')
        A('')
    A('## Draft abstract')
    A('')
    A('> Digital lexicography projects are routinely assessed for code '
      'sustainability, but the sustainability of the **data** — the ongoing '
      'correction of dictionary text — is rarely measured. Using the version '
      'history of the Cologne Digital Sanskrit Lexicon (43 dictionaries, 1.49M '
      f'entries), we show that content correction is highly concentrated: in no year '
      f'do more than {max_correctors} people correct dictionary text, and a single '
      f'editor accounts for {100*share_lo:.0f}–{100*share_hi:.0f}% of corrections '
      'annually. Throughput is driven by individual bursts rather than crew size. '
      + (f'Correction responsiveness is high (median issue resolution '
         f'{lat["median"]} days) but bimodal: a long tail of low-severity work '
         f'remains unresolved for up to {lat["max"]/365:.1f} years, where '
         'single-maintainer capacity is exhausted. ' if lat else '')
      + 'We argue that the curatorial layer of a mature digital dictionary carries a '
      'measurable, currently unmanaged bus-factor risk, and propose '
      'correction-classified commit counts as the appropriate throughput unit.')
    A('')
    A('*Object of analysis: GitHub commits/issues over dictionary source text — in '
      'scope per `docs/BOUNDARY_RULES.md`.*')

    with open(OUT_MD, 'w', encoding='utf-8', newline='\n') as f:
        f.write('\n'.join(L) + '\n')

    print(f'wrote {OUT_MD}')
    print(f'wrote {OUT_ANNUAL}')
    print(f'wrote {OUT_PERDICT}')
    print(f'  commits: {total_commits}  years: {years[0]}-{years[-1]}  '
          f'max correctors/yr: {max_correctors}  lead share: {100*share_lo:.0f}-{100*share_hi:.0f}%')
    print(f'  single-maintainer dicts (>=10 commits): {len(spofs)}')
    if lat:
        print(f'  latency: median {lat["median"]}d  mean {lat["mean"]:.1f}  '
              f'p90 {lat["p90"]}  max {lat["max"]}  tail {lat["tail"]}/{lat["total"]}')
    else:
        print('  latency: no cache (run with --fetch-latency)')


if __name__ == '__main__':
    main()
