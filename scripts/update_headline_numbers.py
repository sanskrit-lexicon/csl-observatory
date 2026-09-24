"""
update_headline_numbers.py — regenerate the README.md / STATUS.md headline
numbers from the committed data snapshot instead of hand-typed copies.

Reads:
  data/summary.json                                    (legacy pipeline: repos_count,
                                                          total_issues, total_pull_requests,
                                                          total_commits, snapshot_date)
  data/contributors.json                                (is_bot flag -> human contributor count)
  data/manifest.json                                    (dataset_ids.correction-events.rows)
  observatory/site/src/data/correction_events_release.csv (distinct `dict` column -> dictionary count)

Writes: README.md (the "Tracking ..." summary line), STATUS.md (the headline
numbers table + "Current status (YYYY-MM)" heading).

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


def main():
    summary = load('summary.json')
    repos = summary['repos_count']
    issues_prs = summary['total_issues'] + summary['total_pull_requests']
    commits = summary['total_commits']
    snapshot_date = summary['snapshot_date']
    snapshot_month = snapshot_date[:7]
    contributors = human_contributor_count()
    obst_events, obst_dicts = correction_corpus()
    years = span_years(snapshot_date)

    readme_path = ROOT / 'README.md'
    readme = readme_path.read_text(encoding='utf-8')
    readme = re.sub(
        r'> Tracking [\d,]+ repos, [\d,]+ issues\+PRs, [\d,]+ commits, and '
        r'[\d,]+ contributors since 2014\.',
        f'> Tracking {repos} repos, {issues_prs:,} issues+PRs, {commits:,} commits, '
        f'and {contributors} contributors since 2014.',
        readme,
    )
    # README's own "Headline numbers" table duplicates four of STATUS.md's
    # rows (plus several report-sourced rows this script cannot derive from
    # summary.json alone — bus-factor, most-active-repo, peak years, dominant
    # work type — those come from the separate refresh-observatory.yml
    # pipeline's reports and are left untouched here).
    readme = re.sub(
        r'## Headline numbers \(snapshot \d{4}-\d{2}\)',
        f'## Headline numbers (snapshot {snapshot_month})',
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
        r'> \*\*Current status \(\d{4}-\d{2}\)\.\*\*',
        f'> **Current status ({snapshot_month}).**',
        status,
    )
    status = re.sub(
        r'## Headline numbers \(snapshot \d{4}-\d{2}\)',
        f'## Headline numbers (snapshot {snapshot_month})',
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

    print(f'repos={repos} issues_prs={issues_prs} commits={commits} '
          f'contributors={contributors} obst_events={obst_events} obst_dicts={obst_dicts} '
          f'snapshot={snapshot_date}')


if __name__ == '__main__':
    main()
