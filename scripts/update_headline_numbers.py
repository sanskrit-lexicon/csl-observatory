"""
update_headline_numbers.py — regenerate OR VERIFY the headline numbers the repo
quotes, from the snapshot that owns each one (H5424, H7122).

Reads:
  data/summary.json                                    (legacy pipeline: repos_count,
                                                          total_issues, total_pull_requests,
                                                          total_commits, snapshot_date)
  data/contributors.json                                (is_bot flag -> human contributor count)
  data/manifest.json                                    (dataset_ids.correction-events.rows)
  observatory/site/src/data/correction_events_release.csv (distinct `dict` column -> dictionary count)
  data/headline_claims.json                            (H7122: every quoted number → its snapshot)

Writes: README.md (the "Tracking ..." summary line + headline table), STATUS.md
(the headline numbers table + "Current status (YYYY-MM-DD)" heading). Both carry the
snapshot ID and as-of date, so a reader can tell which of the repo's two
snapshots a number came from. Beyond README/STATUS, every OTHER registered
live-snapshot claim (docs/ANTHOLOGY_ALIGNMENT_2026Q4.md,
reports/snapshot_divergence.md) is re-quoted in place by requote_live_claims()
— the write half used to stop at README/STATUS, so those surfaces needed a
hand-sync PR after every live refresh (#310, 51b13b7), whose own commits then
moved the live counts again and re-reddened the gate (H7879).

  python scripts/update_headline_numbers.py           # rewrite (refresh pipeline)
  python scripts/update_headline_numbers.py --check   # verify only; exit 1 naming
                                                      # the exact mismatched claim

--check never writes. It is the CI gate: see .github/workflows/headline-claims.yml
and docs/SNAPSHOT_AUTHORITY.md.

Run after scripts/render_reports.py (i.e. as the last step of the refresh.yml
pipeline) so README.md/STATUS.md never drift from the snapshot that produced
data/summary.json (H5424).
"""
import csv
import json
import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')

sys.path.insert(0, str(Path(__file__).resolve().parent))
import headline_claims as hc  # noqa: E402 — sibling module, path set above

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / 'data'


def load(name):
    return json.loads((DATA / name).read_text(encoding='utf-8'))


def human_contributor_count():
    contributors = load('contributors.json')
    return sum(1 for c in contributors if not c.get('is_bot'))


def correction_corpus():
    manifest = load('manifest.json')
    rows = manifest['dataset_ids']['correction-events']['rows']
    csv_path = ROOT / 'observatory/site/src/data/correction_events_release.csv'
    with csv_path.open(newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        dicts = {row['dict'] for row in reader}
    return rows, len(dicts)


def span_years(snapshot_date, start_year=2014):
    end_year = int(snapshot_date[:4])
    return end_year - start_year + 1


def label(snapshot_id, as_of):
    """The provenance suffix every generated headline number carries (H7122)."""
    return f'snapshot {snapshot_id}, as of {as_of}'


def write():
    summary = load('summary.json')
    repos = summary['repos_count']
    issues_prs = summary['total_issues'] + summary['total_pull_requests']
    commits = summary['total_commits']
    snapshot_date = summary['snapshot_date']
    snapshot_month = snapshot_date[:7]
    contributors = human_contributor_count()
    obst_events, obst_dicts = correction_corpus()
    years = span_years(snapshot_date)
    prov = label(hc.LIVE_ID, snapshot_date)
    heading = f'## Headline numbers ({prov})'
    month_cell = f'{snapshot_month} · {prov}'

    readme_path = ROOT / 'README.md'
    readme = readme_path.read_text(encoding='utf-8')
    # Anchor to end-of-line, never to the first period: the provenance label itself
    # contains dots (csl-obs/org-live@1.0.0), and a `[^.\n]*\.` anchor appended the
    # label a second time on every re-run.
    readme = re.sub(
        r'> Tracking [\d,]+ repos, [\d,]+ issues\+PRs, [\d,]+ commits, and '
        r'[\d,]+ contributors since 2014.*',
        f'> Tracking {repos} repos, {issues_prs:,} issues+PRs, {commits:,} commits, '
        f'and {contributors} contributors since 2014 — {prov}.',
        readme,
        count=1,
        flags=re.MULTILINE,
    )
    # README's own "Headline numbers" table duplicates four of STATUS.md's
    # rows (plus several report-sourced rows this script cannot derive from
    # summary.json alone — bus-factor, most-active-repo, peak years, dominant
    # work type — those come from the separate refresh-observatory.yml
    # pipeline's reports and are left untouched here).
    readme = re.sub(
        r'## Headline numbers \([^)]*\)',
        heading,
        readme,
    )
    readme = re.sub(
        r'\| Repos tracked \| [\d,]+ \|',
        f'| Repos tracked | {repos} |',
        readme,
    )
    readme = re.sub(
        r'\| Issues \+ PRs \(lifetime\) \| [\d,]+ \|',
        f'| Issues + PRs (lifetime) | {issues_prs:,} |',
        readme,
    )
    readme = re.sub(
        r'\| Commits since 2014 \| [\d,]+ \|',
        f'| Commits since 2014 | {commits:,} |',
        readme,
    )
    readme = re.sub(
        r'\| Distinct human contributors \| [\d,]+ \|',
        f'| Distinct human contributors | {contributors} |',
        readme,
    )
    readme_path.write_text(readme, encoding='utf-8')

    status_path = ROOT / 'STATUS.md'
    status = status_path.read_text(encoding='utf-8')
    status = re.sub(
        r'> \*\*Current status \([^)]*\)\.\*\*',
        f'> **Current status ({month_cell}).**',
        status,
    )
    status = re.sub(
        r'## Headline numbers \([^)]*\)',
        heading,
        status,
    )
    status = re.sub(
        r'\| Repositories tracked \| [\d,]+ \|',
        f'| Repositories tracked | {repos} |',
        status,
    )
    status = re.sub(
        r'\| Issues \+ PRs \(lifetime\) \| [\d,]+ \|',
        f'| Issues + PRs (lifetime) | {issues_prs:,} |',
        status,
    )
    status = re.sub(
        r'\| Commits since 2014 \| [\d,]+ \|',
        f'| Commits since 2014 | {commits:,} |',
        status,
    )
    status = re.sub(
        r'\| Distinct human contributors \| [\d,]+ \|',
        f'| Distinct human contributors | {contributors} |',
        status,
    )
    status = re.sub(
        r'\| Span \| \d+ years \(2014–\d{4}\) \|',
        f'| Span | {years} years (2014–{snapshot_date[:4]}) |',
        status,
    )
    status = re.sub(
        r'\| OBS-T correction corpus \| [\d,]+ events across \d+ dictionaries \|',
        f'| OBS-T correction corpus | {obst_events:,} events across {obst_dicts} dictionaries |',
        status,
    )
    status_path.write_text(status, encoding='utf-8')

    requoted = requote_live_claims()
    if requoted:
        print('requoted live claims on: ' + ', '.join(requoted))

    print(f'repos={repos} issues_prs={issues_prs} commits={commits} '
          f'contributors={contributors} obst_events={obst_events} obst_dicts={obst_dicts} '
          f'snapshot={snapshot_date} label={prov}')


def requote_live_claims(root: Path = ROOT, claims=None, snaps=None) -> list[str]:
    """Re-quote every registered LIVE-snapshot claim's numbers on its surface.

    The check half (headline_claims.check) verifies claims across 17 surfaces;
    this is its write twin: for each claim owned by csl-obs/org-live@1.0.0,
    every match's named-group numbers are replaced with the derived live
    values, and a bare ISO date inside the match span follows the live
    as-of (snapshot_divergence.md's "As of" column). Pinned-only claims
    (no group derivable from the live snapshot, e.g. hand-written prose
    counts) are deliberately left alone — the gate verifies them against
    their pins, but a pin is registry truth, not something to rewrite prose
    toward. reports/snapshot_divergence.md's delta line is a derived
    restatement of the two rows above it, so it is recomputed here too.

    Returns the surfaces that changed (empty list on a clean tree — running
    this on an already-synced tree is a no-op).
    """
    snaps = snaps if snaps is not None else hc.snapshots(root)
    live = snaps[hc.LIVE_ID]
    offline = snaps[hc.OFFLINE_ID]
    changed: list[str] = []

    for claim in (claims if claims is not None else hc.load_claims(root)):
        if claim.snapshot != hc.LIVE_ID:
            continue
        path = root / claim.file
        if not path.exists():
            continue
        regex = re.compile(claim.pattern)
        lines = path.read_text(encoding='utf-8').splitlines()
        touched = False
        for i, line in enumerate(lines):
            # (start, end, replacement) in line coordinates; spliced
            # right-to-left so earlier offsets stay valid. Offsets come from
            # the ORIGINAL line, and matches never overlap.
            edits: list[tuple[int, int, str]] = []
            for m in regex.finditer(line):
                for metric, raw in m.groupdict().items():
                    if raw is None or metric not in live.values:
                        continue  # pinned-only metrics are not rewritten
                    expected = live.values[metric]
                    if hc._as_int(raw) != expected:
                        s, e = m.span(metric)
                        edits.append((s, e, f'{expected:,}'))
                # The live as-of rides along: an ISO date inside the match
                # span (divergence.live_row's second column) moves with the
                # snapshot it labels. Dates are context, never claim groups —
                # _as_int cannot parse them — so this is span-local, not
                # metric-driven.
                for dm in re.finditer(r'\d{4}-\d{2}-\d{2}', m.group(0)):
                    if dm.group(0) != live.as_of:
                        edits.append((m.start() + dm.start(), m.start() + dm.end(),
                                      live.as_of))
            if edits:
                out = line
                for s, e, rep in sorted(edits, key=lambda t: t[0], reverse=True):
                    out = out[:s] + rep + out[e:]
                lines[i] = out
                touched = True
        if touched:
            path.write_text('\n'.join(lines) + '\n', encoding='utf-8')
            if claim.file not in changed:
                changed.append(claim.file)

    # The divergence report's delta line restates the two rows above it; it is
    # derived by definition (live − offline), so it is recomputed rather than
    # left to rot between hand-syncs. [\s\S]*? crosses the sentence's hard
    # wrap; non-greedy stops at the sentence-ending "contributors." and leaves
    # the trailing parenthetical note intact.
    div_path = root / 'reports' / 'snapshot_divergence.md'
    if div_path.exists():
        delta = {
            'repositories': live.values['repos'] - offline.values['repos'],
            'issues': live.values['issues'] - offline.values['issues'],
            'prs': live.values['prs'] - offline.values['prs'],
            'issues+prs': live.values['issues_prs'] - offline.values['issues_prs'],
            'commits': live.values['commits'] - offline.values['commits'],
            'contributors': live.values['contributors'] - offline.values['contributors'],
        }

        def signed(v: int) -> str:
            return f'{v:,}' if v >= 0 else f'−{abs(v):,}'

        fresh = (f'**Delta** (live − offline): {signed(delta["repositories"])} '
                 f'repositories, {signed(delta["issues"])} issues, {signed(delta["prs"])} PRs, '
                 f'{signed(delta["issues+prs"])} issues+PRs, {signed(delta["commits"])} commits, '
                 f'{signed(delta["contributors"])} contributors.')
        text = div_path.read_text(encoding='utf-8')
        # Value-gate the rewrite: parse the numbers out of the existing
        # sentence (it may hard-wrap) and only reflow when a VALUE actually
        # moved. A clean tree must leave this file byte-untouched —
        # idempotence is what makes "requote then --check" safe in CI.
        m = re.search(r'\*\*Delta\*\* \(live − offline\): ([\s\S]*?)contributors\.', text)
        if m:
            # tokens must START with a digit (a bare comma between numbers is
            # not a value); a trailing comma before a separator is stripped.
            quoted = [t.rstrip(',') for t in re.findall(r'[−\-]?\d[\d,]*', m.group(1))]
            computed = [signed(delta[k]) for k in
                        ('repositories', 'issues', 'prs', 'issues+prs',
                         'commits', 'contributors')]
            if quoted == computed:
                m = None  # values already current; do not touch the wrap
        if m:
            new_text, _n = re.subn(r'\*\*Delta\*\* \(live − offline\): [\s\S]*?contributors\.',
                                   fresh, text, count=1)
            if new_text != text:
                div_path.write_text(new_text, encoding='utf-8')
                if 'reports/snapshot_divergence.md' not in changed:
                    changed.append('reports/snapshot_divergence.md')

    return changed


def check() -> int:
    """Verify every registered headline claim; never writes."""
    print(hc.summary_line())
    findings = hc.check()
    if not findings:
        claims = hc.load_claims()
        surfaces = len({c.file for c in claims})
        print(f'PASS: {len(claims)} headline claim(s) across {surfaces} surface(s) '
              f're-derive from their registered snapshots')
        return 0
    for finding in findings:
        print(finding)
    print(f'FAIL: {len(findings)} headline claim(s) do not match their snapshot')
    return 1


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    if '--check' in argv:
        return check()
    unknown = [a for a in argv if a not in ('--write', '-w')]
    if unknown:
        print(f'unknown argument(s): {" ".join(unknown)}', file=sys.stderr)
        print('usage: update_headline_numbers.py [--check]', file=sys.stderr)
        return 2
    write()
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
