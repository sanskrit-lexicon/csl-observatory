#!/usr/bin/env python3
"""Issue-taxonomy adoption / conformance over time for the sanskrit-lexicon org.

Operates offline on the already-extracted observatory data
(`observatory/site/src/data/issues.csv`) — no GitHub calls, fully
reproducible. Measures how well the issue corpus conforms to the Cologne
taxonomy (one type label + one severity label + one milestone per issue),
broken down by issue-creation year.

Because the taxonomy was applied retroactively via the runbook, this is a
*coverage* measure across the historical issue base — what fraction of
issues created in year Y now carry a conformant label set — rather than a
real-time "adopted on date D" measure.

Taxonomy (union of the dictionary-repo and tooling-repo label sets defined
in the org CLAUDE.md files):

* TYPE     — link-target, link-splitting, markup, text-correction,
             content-enhancement, encoding, scan-quality, bug, question,
             feature, enhancement, performance, tech-debt, security,
             documentation, infrastructure
* SEVERITY — trivial, minor, medium, major, hard, critical

A label not in either set is "stray" (e.g. GitHub defaults like `duplicate`
or ad-hoc notes like `not now`).

Outputs
-------
* `reports/taxonomy_adoption.md`                     — human-readable finding
* `observatory/site/src/data/taxonomy_adoption.csv`  — per-year metrics

Usage:  python scripts/taxonomy_adoption.py
"""
import csv, os, sys
from collections import Counter, defaultdict
sys.stdout.reconfigure(encoding='utf-8'); sys.stderr.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DATA = os.path.join(ROOT, 'observatory', 'site', 'src', 'data')
ISSUES = os.path.join(DATA, 'issues.csv')
OUT_MD = os.path.join(ROOT, 'reports', 'taxonomy_adoption.md')
OUT_CSV = os.path.join(DATA, 'taxonomy_adoption.csv')

TYPE = {'link-target', 'link-splitting', 'markup', 'text-correction',
        'content-enhancement', 'encoding', 'scan-quality', 'bug', 'question',
        'feature', 'enhancement', 'performance', 'tech-debt', 'security',
        'documentation', 'infrastructure'}
SEVERITY = {'trivial', 'minor', 'medium', 'major', 'hard', 'critical'}


def main():
    by_year = defaultdict(lambda: {'total': 0, 'typed': 0, 'one_type': 0,
        'multi_type': 0, 'sev': 0, 'one_sev': 0, 'milestone': 0,
        'conformant': 0, 'stray': 0})
    stray_labels = Counter()
    pr_count = 0
    untyped_examples = []

    with open(ISSUES, encoding='utf-8') as f:
        for row in csv.DictReader(f):
            if row['kind'].strip() != 'issue':       # taxonomy applies to issues, not PRs
                pr_count += 1
                continue
            year = row['created_at'][:4]
            labels = [x.strip() for x in row['labels'].split('|') if x.strip()]
            type_hits = [l for l in labels if l in TYPE]
            sev_hits = [l for l in labels if l in SEVERITY]
            stray = [l for l in labels if l not in TYPE and l not in SEVERITY]
            has_ms = bool(row['milestone'].strip())
            conformant = (len(type_hits) == 1 and len(sev_hits) == 1
                          and has_ms and not stray)

            b = by_year[year]
            b['total'] += 1
            if type_hits: b['typed'] += 1
            if len(type_hits) == 1: b['one_type'] += 1
            if len(type_hits) > 1: b['multi_type'] += 1
            if sev_hits: b['sev'] += 1
            if len(sev_hits) == 1: b['one_sev'] += 1
            if has_ms: b['milestone'] += 1
            if conformant: b['conformant'] += 1
            if stray: b['stray'] += 1
            for s in stray:
                stray_labels[s] += 1
            if not type_hits and len(untyped_examples) < 15:
                untyped_examples.append((row['repo'], row['number'], row['title'][:60]))

    years = sorted(by_year)
    tot = sum(b['total'] for b in by_year.values())
    typed = sum(b['typed'] for b in by_year.values())
    one_type = sum(b['one_type'] for b in by_year.values())
    multi = sum(b['multi_type'] for b in by_year.values())
    sev = sum(b['sev'] for b in by_year.values())
    ms = sum(b['milestone'] for b in by_year.values())
    conf = sum(b['conformant'] for b in by_year.values())
    strayc = sum(b['stray'] for b in by_year.values())

    def pct(a, b):
        return f'{100*a/b:.0f}%' if b else '—'

    # ---- per-year CSV ----
    with open(OUT_CSV, 'w', encoding='utf-8', newline='') as f:
        w = csv.writer(f)
        w.writerow(['year', 'issues', 'typed', 'one_type', 'multi_type',
                    'has_severity', 'has_milestone', 'conformant',
                    'pct_typed', 'pct_severity', 'pct_milestone', 'pct_conformant'])
        for y in years:
            b = by_year[y]
            t = b['total']
            w.writerow([y, t, b['typed'], b['one_type'], b['multi_type'],
                        b['sev'], b['milestone'], b['conformant'],
                        round(100*b['typed']/t, 1), round(100*b['sev']/t, 1),
                        round(100*b['milestone']/t, 1), round(100*b['conformant']/t, 1)])

    # ---- report ----
    L = []; A = L.append
    A('# Issue-taxonomy adoption & conformance')
    A('')
    A(f'_Generated by `scripts/taxonomy_adoption.py` from '
      f'`observatory/site/src/data/issues.csv` (offline, reproducible). '
      f'{tot:,} issues across {len(years)} years ({years[0]}–{years[-1]}); '
      f'{pr_count:,} pull requests excluded — the taxonomy applies to issues._')
    A('')
    A('Conformance = exactly one **type** label **and** exactly one **severity** '
      'label **and** a **milestone**, with no stray labels — the rule stated in '
      'the org `CLAUDE.md`. Labels were applied retroactively by the runbook, so '
      'these are coverage figures across the historical issue base, bucketed by '
      'the year each issue was opened.')
    A('')
    A('## Headline')
    A('')
    A('| Metric | Value |')
    A('|---|---:|')
    A(f'| Issues classified | {tot:,} |')
    A(f'| Carry a type label | {typed:,} ({pct(typed, tot)}) |')
    A(f'| Exactly one type label | {one_type:,} ({pct(one_type, tot)}) |')
    A(f'| More than one type label | {multi:,} ({pct(multi, tot)}) |')
    A(f'| Carry a severity label | {sev:,} ({pct(sev, tot)}) |')
    A(f'| Assigned a milestone | {ms:,} ({pct(ms, tot)}) |')
    A(f'| Carry a stray (non-taxonomy) label | {strayc:,} ({pct(strayc, tot)}) |')
    A(f'| **Fully conformant** | **{conf:,} ({pct(conf, tot)})** |')
    A('')
    A('## Conformance by year opened')
    A('')
    A('| Year | Issues | Typed | Severity | Milestone | Conformant |')
    A('|---|---:|---:|---:|---:|---:|')
    for y in years:
        b = by_year[y]; t = b['total']
        A(f'| {y} | {t:,} | {pct(b["typed"], t)} | {pct(b["sev"], t)} | '
          f'{pct(b["milestone"], t)} | {pct(b["conformant"], t)} |')
    A('')
    A('## Stray (non-taxonomy) labels')
    A('')
    if stray_labels:
        A('Labels appearing on issues that are neither a recognised type nor '
          'severity — GitHub defaults applied before the taxonomy, or ad-hoc '
          'notes. Candidates to delete or fold into the taxonomy.')
        A('')
        A('| Stray label | Issues |')
        A('|---|---:|')
        for lab, c in stray_labels.most_common():
            A(f'| `{lab}` | {c} |')
    else:
        A('None — every label maps to the type or severity taxonomy.')
    A('')
    A('## Untyped issues (sample)')
    A('')
    A('Issues carrying no recognised type label — the gap to close for full '
      'coverage.')
    A('')
    if untyped_examples:
        A('| Repo | # | Title |')
        A('|---|---:|---|')
        for repo, num, title in untyped_examples:
            A(f'| {repo} | {num} | {title} |')
    else:
        A('None — every issue carries a type label.')
    A('')
    A('## Reading')
    A('')
    A(f'- Of {tot:,} issues, **{pct(typed, tot)} carry a type label** and '
      f'**{pct(conf, tot)} are fully conformant** (one type + one severity + a '
      'milestone). The taxonomy is broadly but not completely applied across '
      'the 13-year corpus.')
    A(f'- **{multi:,} issues carry more than one type label** ({pct(multi, tot)}) '
      '— a conformance violation under the one-type rule, worth a cleanup pass.')
    A(f'- **{strayc:,} issues still carry a stray label** ({pct(strayc, tot)}); '
      'see the inventory above for delete/fold candidates.')
    A('')
    A('See [`reports/issue_typology_annual`](../observatory/site/src/data/issue_typology_annual.csv) '
      'for the type-mix composition by year (e.g. the steep rise of '
      '`text-correction` and the 2025 surge in `link-target`).')
    A('')
    A('*Object of analysis: GitHub issues and their labels — in scope per '
      '`docs/BOUNDARY_RULES.md`.*')

    with open(OUT_MD, 'w', encoding='utf-8', newline='\n') as f:
        f.write('\n'.join(L) + '\n')

    print(f'wrote {OUT_MD}')
    print(f'wrote {OUT_CSV}')
    print(f'  issues: {tot:,}   PRs excluded: {pr_count:,}')
    print(f'  typed: {pct(typed, tot)}   severity: {pct(sev, tot)}   '
          f'milestone: {pct(ms, tot)}   conformant: {pct(conf, tot)}')
    print(f'  multi-type: {multi:,}   stray: {strayc:,}   '
          f'distinct stray labels: {len(stray_labels)}')


if __name__ == '__main__':
    main()
