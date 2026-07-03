#!/usr/bin/env python3
"""Issue lifecycle & responsiveness analysis for the sanskrit-lexicon org.

Operates offline on the already-extracted observatory data
(`observatory/site/src/data/issues.csv`) — no GitHub calls, fully
reproducible. First Workstream-G (Phase-2) finding: where earlier findings
count *volume* (velocity_timeline) and *labels* (taxonomy_adoption), this one
measures *time*: how long issues live, what fraction of each opening cohort
survives unresolved, how old the current backlog is, and which repositories
close fastest/slowest.

Definitions
-----------
* **Cohort survival** — for issues opened in year Y, the fraction still open
  H days after creation. Right-censored: an issue only counts at horizon H if
  the snapshot extends at least H days past its creation (or it closed
  within H). This is the discrete Kaplan–Meier reading of the data.
* **Backlog age pyramid** — currently-open issues bucketed by age at the
  snapshot date.
* **Silent backlog** — open issues with zero comments: opened, never answered.
* **Time-to-close** — days from created_at to closed_at (closed issues only).

Time-to-FIRST-response is NOT computable offline (issues.csv carries a
comment *count*, not comment timestamps); it is an API-gated extension.

Outputs
-------
* `reports/issue_lifecycle.md`                                — finding
* `observatory/site/src/data/issue_lifecycle_survival.csv`    — cohort × horizon
* `observatory/site/src/data/issue_lifecycle_backlog.csv`     — age pyramid
* `observatory/site/src/data/issue_lifecycle_close.csv`       — annual latency
* `observatory/site/src/data/issue_lifecycle_repo.csv`        — per-repo stats

Usage:  python scripts/issue_lifecycle.py
"""
import csv, os, sys
from collections import defaultdict
from datetime import datetime, timezone
sys.stdout.reconfigure(encoding='utf-8'); sys.stderr.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DATA = os.path.join(ROOT, 'observatory', 'site', 'src', 'data')
ISSUES = os.path.join(DATA, 'issues.csv')
OUT_MD = os.path.join(ROOT, 'reports', 'issue_lifecycle.md')
OUT_SURV = os.path.join(DATA, 'issue_lifecycle_survival.csv')
OUT_BACK = os.path.join(DATA, 'issue_lifecycle_backlog.csv')
OUT_CLOSE = os.path.join(DATA, 'issue_lifecycle_close.csv')
OUT_REPO = os.path.join(DATA, 'issue_lifecycle_repo.csv')

# Survival horizons in days (~1m, 3m, 6m, 1y, 2y, 4y).
HORIZONS = [30, 90, 180, 365, 730, 1460]

# Backlog age buckets: (label, min_days_inclusive, max_days_exclusive).
BUCKETS = [
    ('<1 month', 0, 30),
    ('1–3 months', 30, 90),
    ('3–6 months', 90, 180),
    ('6–12 months', 180, 365),
    ('1–2 years', 365, 730),
    ('2–4 years', 730, 1460),
    ('4+ years', 1460, 10 ** 9),
]

MIN_REPO_CLOSED = 20   # per-repo latency stats need at least this many closed


def parse(ts):
    return datetime.strptime(ts, '%Y-%m-%dT%H:%M:%SZ').replace(tzinfo=timezone.utc)


def pctl(sorted_vals, p):
    """Nearest-rank percentile over a pre-sorted list."""
    if not sorted_vals:
        return None
    k = max(0, min(len(sorted_vals) - 1, int(round(p * (len(sorted_vals) - 1)))))
    return sorted_vals[k]


def load():
    rows = []
    with open(ISSUES, encoding='utf-8') as f:
        for r in csv.DictReader(f):
            created = parse(r['created_at'])
            closed = parse(r['closed_at']) if r['closed_at'] else None
            rows.append({
                'repo': r['repo'],
                'kind': r['kind'],            # 'issue' | 'PR'
                'state': r['state'],
                'created': created,
                'closed': closed,
                'comments': int(r['comments'] or 0),
            })
    return rows


def main():
    rows = load()
    as_of = max(max(r['created'] for r in rows),
                max(r['closed'] for r in rows if r['closed']))
    issues = [r for r in rows if r['kind'] == 'issue']
    prs = [r for r in rows if r['kind'] == 'PR']

    # ---- cohort survival (issues only; PRs are too few for cohorts) ----
    surv = []  # cohort, horizon_days, observable, still_open, pct_open
    by_cohort = defaultdict(list)
    for r in issues:
        by_cohort[r['created'].year].append(r)
    for year in sorted(by_cohort):
        cohort = by_cohort[year]
        for h in HORIZONS:
            observable = [r for r in cohort
                          if (as_of - r['created']).days >= h
                          or (r['closed'] and (r['closed'] - r['created']).days <= h)]
            if len(observable) < 10:
                continue
            still = sum(1 for r in observable
                        if not r['closed'] or (r['closed'] - r['created']).days > h)
            surv.append({'cohort': year, 'horizon_days': h,
                         'observable': len(observable), 'still_open': still,
                         'pct_open': round(100 * still / len(observable), 1)})

    # ---- backlog age pyramid (open issues at snapshot) ----
    open_issues = [r for r in issues if r['state'] == 'open']
    back = []
    for label, lo, hi in BUCKETS:
        in_bucket = [r for r in open_issues if lo <= (as_of - r['created']).days < hi]
        back.append({'bucket': label,
                     'count': len(in_bucket),
                     'silent': sum(1 for r in in_bucket if r['comments'] == 0)})

    # ---- annual time-to-close (issues and PRs separately) ----
    close_rows = []
    for kind, pool in (('issue', issues), ('PR', prs)):
        by_year = defaultdict(list)
        for r in pool:
            if r['closed']:
                by_year[r['closed'].year].append((r['closed'] - r['created']).days)
        for year in sorted(by_year):
            d = sorted(by_year[year])
            close_rows.append({'year': year, 'kind': kind, 'n_closed': len(d),
                               'median_days': pctl(d, 0.5), 'p25': pctl(d, 0.25),
                               'p75': pctl(d, 0.75), 'p90': pctl(d, 0.9)})

    # ---- per-repo responsiveness ----
    repo_rows = []
    by_repo = defaultdict(list)
    for r in issues:
        by_repo[r['repo']].append(r)
    for repo in sorted(by_repo):
        pool = by_repo[repo]
        closed_days = sorted((r['closed'] - r['created']).days
                             for r in pool if r['closed'])
        opens = [r for r in pool if r['state'] == 'open']
        repo_rows.append({
            'repo': repo,
            'issues': len(pool),
            'open': len(opens),
            'closed': len(closed_days),
            'median_days_to_close': pctl(closed_days, 0.5) if len(closed_days) >= MIN_REPO_CLOSED else '',
            'p90_days_to_close': pctl(closed_days, 0.9) if len(closed_days) >= MIN_REPO_CLOSED else '',
            'open_median_age_days': pctl(sorted((as_of - r['created']).days for r in opens), 0.5) if opens else '',
            'silent_open': sum(1 for r in opens if r['comments'] == 0),
        })

    # ---- headline numbers ----
    closed_all = sorted((r['closed'] - r['created']).days for r in issues if r['closed'])
    silent_total = sum(1 for r in open_issues if r['comments'] == 0)
    old2y = sum(1 for r in open_issues if (as_of - r['created']).days >= 730)
    # 1-year survival, all cohorts pooled (observable only).
    obs1y = [r for r in issues if (as_of - r['created']).days >= 365
             or (r['closed'] and (r['closed'] - r['created']).days <= 365)]
    open1y = sum(1 for r in obs1y
                 if not r['closed'] or (r['closed'] - r['created']).days > 365)

    # ---- write CSVs ----
    def write(path, fieldnames, rws):
        with open(path, 'w', encoding='utf-8', newline='') as f:
            w = csv.DictWriter(f, fieldnames=fieldnames)
            w.writeheader()
            for r in rws:
                w.writerow(r)
    write(OUT_SURV, ['cohort', 'horizon_days', 'observable', 'still_open', 'pct_open'], surv)
    write(OUT_BACK, ['bucket', 'count', 'silent'], back)
    write(OUT_CLOSE, ['year', 'kind', 'n_closed', 'median_days', 'p25', 'p75', 'p90'], close_rows)
    write(OUT_REPO, ['repo', 'issues', 'open', 'closed', 'median_days_to_close',
                     'p90_days_to_close', 'open_median_age_days', 'silent_open'], repo_rows)

    # ---- write report ----
    L = []; A = L.append
    A('# Issue lifecycle & responsiveness')
    A('')
    A('_Generated by `scripts/issue_lifecycle.py` from `observatory/site/src/data/'
      'issues.csv` (offline, reproducible). Snapshot as-of '
      f'{as_of.date().isoformat()}. PRs analysed separately where volume allows; '
      'time-to-first-response is API-gated (no comment timestamps offline)._')
    A('')
    A('## Headline')
    A('')
    A('| Metric | Value |')
    A('|---|---:|')
    A(f'| Issues analysed (PRs) | {len(issues):,} ({len(prs)}) |')
    A(f'| Open issues at snapshot | {len(open_issues):,} |')
    A(f'| Median time-to-close (all closed issues) | {pctl(closed_all, 0.5)} days |')
    A(f'| 90th-percentile time-to-close | {pctl(closed_all, 0.9):,} days |')
    A(f'| Issues still open 1 year after opening (pooled, observable) | {100*open1y/len(obs1y):.0f}% |')
    A(f'| **Open issues older than 2 years** | **{old2y} / {len(open_issues)}** ({100*old2y/len(open_issues):.0f}%) |')
    A(f'| **Silent backlog (open, zero comments)** | **{silent_total}** ({100*silent_total/len(open_issues):.0f}% of open) |')
    A('')
    A('## Cohort survival — % of each opening year still open after N days')
    A('')
    A('Right-censored: a cohort only reports a horizon its issues have all had '
      'time to reach. Cells are % still open among observable issues.')
    A('')
    hdr = ' | '.join(f'{h}d' for h in HORIZONS)
    A(f'| Cohort | N | {hdr} |')
    A('|---|---:|' + '---:|' * len(HORIZONS))
    surv_by = defaultdict(dict)
    cohort_n = {}
    for s in surv:
        surv_by[s['cohort']][s['horizon_days']] = s['pct_open']
        cohort_n[s['cohort']] = max(cohort_n.get(s['cohort'], 0), s['observable'])
    for year in sorted(surv_by):
        cells = ' | '.join(
            f"{surv_by[year][h]:.0f}%" if h in surv_by[year] else '·'
            for h in HORIZONS)
        A(f'| {year} | {cohort_n[year]:,} | {cells} |')
    A('')
    A('## Backlog age pyramid (open issues at snapshot)')
    A('')
    A('| Age | Open issues | of which silent (0 comments) |')
    A('|---|---:|---:|')
    for b in back:
        A(f"| {b['bucket']} | {b['count']} | {b['silent']} |")
    A('')
    A('## Time-to-close by closing year')
    A('')
    A('| Year | Kind | Closed | Median days | p25 | p75 | p90 |')
    A('|---|---|---:|---:|---:|---:|---:|')
    for c in close_rows:
        A(f"| {c['year']} | {c['kind']} | {c['n_closed']} | {c['median_days']} "
          f"| {c['p25']} | {c['p75']} | {c['p90']} |")
    A('')
    A('## Per-repository responsiveness')
    A('')
    A(f'Latency columns only for repos with ≥{MIN_REPO_CLOSED} closed issues.')
    A('')
    A('| Repository | Issues | Open | Median close (d) | p90 close (d) | Open median age (d) | Silent open |')
    A('|---|---:|---:|---:|---:|---:|---:|')
    for r in sorted(repo_rows, key=lambda r: -r['issues']):
        A(f"| {r['repo']} | {r['issues']} | {r['open']} | {r['median_days_to_close']} "
          f"| {r['p90_days_to_close']} | {r['open_median_age_days']} | {r['silent_open']} |")
    A('')
    A('## Reading')
    A('')
    med = pctl(closed_all, 0.5)
    A(f'- Half of all issues that get closed are closed within **{med} days** — '
      f'but the distribution has a very long tail (p90 = {pctl(closed_all, 0.9):,} '
      'days): what is not handled quickly tends to sit for years.')
    A(f'- **{100*open1y/len(obs1y):.0f}% of issues are still open one year after '
      'opening** (pooled cohorts, censoring-adjusted); the survival table shows '
      'whether recent cohorts fare better or worse than the 2014–2018 era.')
    A(f'- The backlog is old: {100*old2y/len(open_issues):.0f}% of currently-open '
      f'issues are more than two years old, and **{silent_total} open issues have '
      'never received a single comment** — the silent backlog is the natural '
      'first target for triage (close, label, or answer).')
    A('- Per-repo medians differ by an order of magnitude; the slowest large '
      'repos are where a scholar-contributor\'s issue is most likely to die '
      'unanswered.')
    A('')
    A('*Object of analysis: GitHub issues and pull requests — in scope per '
      '`docs/BOUNDARY_RULES.md`. Roadmap: Workstream G1.*')

    with open(OUT_MD, 'w', encoding='utf-8', newline='\n') as f:
        f.write('\n'.join(L) + '\n')

    print(f'wrote {OUT_MD}')
    for p in (OUT_SURV, OUT_BACK, OUT_CLOSE, OUT_REPO):
        print(f'wrote {p}')
    print(f'  as_of {as_of.date()}  issues {len(issues)}  open {len(open_issues)}')
    print(f'  median close {med}d  p90 {pctl(closed_all, 0.9)}d  '
          f'1y-open {100*open1y/len(obs1y):.0f}%  silent {silent_total}')


if __name__ == '__main__':
    main()
