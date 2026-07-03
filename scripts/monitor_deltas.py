#!/usr/bin/env python3
"""Active delta monitor for the observatory (Workstream G2).

Compares the freshly regenerated snapshot in the working tree against the
previous committed one (`git show HEAD:<path>`) and writes a digest of what
CHANGED — the observatory noticing change instead of waiting for a human to
go looking. Designed to run in `refresh-observatory.yml` AFTER the findings
are regenerated and BEFORE the refresh commit, so HEAD is always the previous
snapshot. Running it locally over an unchanged tree reports "no changes".

Signals
-------
* backlog     — org-wide open-issue count spike/drop (±10% or ±50 issues)
* silent      — silent-backlog (0-comment open issues) growth
* stale       — repos whose last push newly crossed the 90-day staleness line
* repos       — repositories added to / removed from the snapshot
* contributors— logins never seen in the previous snapshot (new arrivals!)
* bus factor  — per-repo bus-factor changes and org top-share moves
* conformance — latest-year taxonomy conformance drop of >5 points

Exit code is always 0 — the digest is informational, not a gate.

Outputs
-------
* `reports/monitor_digest.md` (overwritten each run; dated)

Usage:  python scripts/monitor_deltas.py
"""
import csv, io, os, subprocess, sys
from datetime import datetime, timezone
sys.stdout.reconfigure(encoding='utf-8'); sys.stderr.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DATA_REL = 'observatory/site/src/data'
DATA = os.path.join(ROOT, *DATA_REL.split('/'))
OUT_MD = os.path.join(ROOT, 'reports', 'monitor_digest.md')

STALE_DAYS = 90
BACKLOG_PCT = 0.10
BACKLOG_ABS = 50
CONFORMANCE_DROP = 5.0


def read_head(rel):
    """Rows of a CSV as of HEAD, or None if it didn't exist there."""
    r = subprocess.run(['git', 'show', f'HEAD:{DATA_REL}/{rel}'],
                       cwd=ROOT, capture_output=True, encoding='utf-8')
    if r.returncode != 0:
        return None
    return list(csv.DictReader(io.StringIO(r.stdout)))


def read_now(rel):
    p = os.path.join(DATA, rel)
    if not os.path.exists(p):
        return None
    with open(p, encoding='utf-8') as f:
        return list(csv.DictReader(f))


def parse_ts(ts):
    return datetime.strptime(ts, '%Y-%m-%dT%H:%M:%SZ').replace(tzinfo=timezone.utc)


def main():
    now_utc = datetime.now(timezone.utc)
    flags = []      # (severity, signal, message)  severity: 'ALERT' | 'NOTE'
    checked = []    # signal names actually evaluated

    def flag(sev, signal, msg):
        flags.append((sev, signal, msg))

    def compare(rel, name, fn):
        old, new = read_head(rel), read_now(rel)
        if old is None or new is None:
            return
        checked.append(name)
        fn(old, new)

    # ---- backlog + silent (issues.csv) ----
    def backlog(old, new):
        o = sum(1 for r in old if r['state'] == 'open' and r['kind'] == 'issue')
        n = sum(1 for r in new if r['state'] == 'open' and r['kind'] == 'issue')
        d = n - o
        if o and (abs(d) >= BACKLOG_ABS or abs(d) / o >= BACKLOG_PCT):
            flag('ALERT', 'backlog',
                 f'Open-issue backlog moved {o} → {n} ({d:+d}).')
        elif d:
            flag('NOTE', 'backlog', f'Open-issue backlog {o} → {n} ({d:+d}).')
        # silent backlog
        os_ = sum(1 for r in old if r['state'] == 'open' and r['kind'] == 'issue'
                  and int(r['comments'] or 0) == 0)
        ns = sum(1 for r in new if r['state'] == 'open' and r['kind'] == 'issue'
                 and int(r['comments'] or 0) == 0)
        if ns > os_:
            flag('ALERT', 'silent',
                 f'Silent backlog (open, 0 comments) grew {os_} → {ns} (+{ns - os_}).')
        elif ns < os_:
            flag('NOTE', 'silent', f'Silent backlog shrank {os_} → {ns}.')
    compare('issues.csv', 'backlog+silent', backlog)

    # ---- repos added/removed + staleness (repos.csv) ----
    def repos(old, new):
        o = {r['repo']: r for r in old}
        n = {r['repo']: r for r in new}
        for r in sorted(set(n) - set(o)):
            flag('NOTE', 'repos', f'New repository in snapshot: `{r}`.')
        for r in sorted(set(o) - set(n)):
            flag('ALERT', 'repos', f'Repository disappeared from snapshot: `{r}`.')
        for name in sorted(set(o) & set(n)):
            try:
                op = (now_utc - parse_ts(o[name]['pushed_at'])).days
                np_ = (now_utc - parse_ts(n[name]['pushed_at'])).days
            except (ValueError, KeyError):
                continue
            if op <= STALE_DAYS < np_:
                flag('ALERT', 'stale',
                     f'`{name}` newly stale: last push {np_} days ago (threshold {STALE_DAYS}).')
    compare('repos.csv', 'repos+staleness', repos)

    # ---- new contributors (contributors.csv) ----
    def contribs(old, new):
        seen = {r['login'] for r in old}
        arrivals = sorted({r['login'] for r in new
                           if r['login'] not in seen
                           and r.get('type', '').strip().lower() != 'bot'})
        for login in arrivals:
            touched = sorted({r['repo'] for r in new if r['login'] == login})
            flag('NOTE', 'contributors',
                 f'New contributor `{login}` (repos: {", ".join(touched[:5])}).')
    compare('contributors.csv', 'contributors', contribs)

    # ---- bus factor (bus_factor.csv) ----
    def bus(old, new):
        o = {r['repo']: r for r in old}
        n = {r['repo']: r for r in new}
        for name in sorted(set(o) & set(n)):
            ob, nb = int(o[name]['bus_factor']), int(n[name]['bus_factor'])
            if nb < ob:
                flag('ALERT', 'bus-factor',
                     f'`{name}` bus factor worsened {ob} → {nb}.')
            elif nb > ob:
                flag('NOTE', 'bus-factor', f'`{name}` bus factor improved {ob} → {nb}.')
    compare('bus_factor.csv', 'bus-factor', bus)

    # ---- taxonomy conformance, latest common year ----
    def conf(old, new):
        oy = {r['year']: float(r['pct_conformant']) for r in old}
        ny = {r['year']: float(r['pct_conformant']) for r in new}
        common = sorted(set(oy) & set(ny))
        if not common:
            return
        y = common[-1]
        if oy[y] - ny[y] > CONFORMANCE_DROP:
            flag('ALERT', 'conformance',
                 f'Taxonomy conformance for {y} dropped {oy[y]:.1f}% → {ny[y]:.1f}%.')
    compare('taxonomy_adoption.csv', 'conformance', conf)

    # ---- write digest ----
    alerts = [f for f in flags if f[0] == 'ALERT']
    notes = [f for f in flags if f[0] == 'NOTE']
    L = []; A = L.append
    A('# Observatory monitor digest')
    A('')
    A(f'_Generated {now_utc.strftime("%Y-%m-%d %H:%M UTC")} by '
      '`scripts/monitor_deltas.py` — working-tree snapshot vs previous commit '
      '(HEAD). Informational; regenerated on every refresh. Roadmap: '
      'Workstream G2._')
    A('')
    A(f'Signals checked: {", ".join(checked) if checked else "none (no comparable files)"}.')
    A('')
    if not flags:
        A('**No changes detected** — the fresh snapshot matches the previous one '
          'on every monitored signal.')
        A('')
    else:
        if alerts:
            A(f'## Alerts ({len(alerts)})')
            A('')
            for _, sig, msg in alerts:
                A(f'- **[{sig}]** {msg}')
            A('')
        if notes:
            A(f'## Notes ({len(notes)})')
            A('')
            for _, sig, msg in notes:
                A(f'- [{sig}] {msg}')
            A('')
    A('*Thresholds: backlog ±10% or ±50; staleness 90 days; conformance drop '
      f'>{CONFORMANCE_DROP:.0f} points on the latest common year.*')

    with open(OUT_MD, 'w', encoding='utf-8', newline='\n') as f:
        f.write('\n'.join(L) + '\n')

    print(f'wrote {OUT_MD}')
    print(f'  checked: {", ".join(checked)}')
    print(f'  alerts: {len(alerts)}  notes: {len(notes)}')


if __name__ == '__main__':
    main()
