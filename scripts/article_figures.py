"""article_figures.py — figures for article/01-empirical-companion.md (A14).

Figure 1: contributor activity-span chart ("gantt") — each commit-author
identity's first-to-last commit interval over the archived 2026-05-07
snapshot, after alias merge, coloured by role.

Reads:  data/snapshots/2026-05-07/commits.json + scripts/contributors_map.json
Writes: article/figures/contributor-gantt.png (300 dpi)

Reuses the alias-merge logic of scripts/compute_metrics.py (same map, same
canonicalisation) so the figure and the paper's SS4.5 table share one basis.
Colours follow the org data-viz palette contract (categorical slots validated
for CVD separation on the light surface; bots are rendered as a de-emphasised
neutral, not a categorical series, and carry a "(bot)" text suffix so the
distinction is never colour-alone).
"""
import json
import sys
from datetime import date
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
from matplotlib.patches import Patch

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

ROOT = Path(__file__).resolve().parent.parent
SNAP = ROOT / 'data' / 'snapshots' / '2026-05-07'
OUT = ROOT / 'article' / 'figures' / 'contributor-gantt.png'

SNAPSHOT_DATE = '2026-05-07'

ROLE_COLORS = {           # validated categorical slots, fixed order
    'maintainer': '#2a78d6',
    'core': '#1baf7a',
    'lead': '#eda100',
    'occasional': '#008300',
    'contributor': '#4a3aa7',
    'bot': '#898781',     # de-emphasised neutral, not a categorical slot
}
SURFACE = '#fcfcfb'
INK = '#0b0b0b'
INK_2 = '#52514e'
MUTED = '#898781'
GRID = '#e1e0d9'
BASELINE = '#c3c2b7'


def load_contributor_spans():
    commits_by_repo = json.loads((SNAP / 'commits.json').read_text(encoding='utf-8'))
    cmap = json.loads((Path(__file__).parent / 'contributors_map.json').read_text(encoding='utf-8'))

    alias_index = {}
    for canonical, meta in cmap.items():
        if canonical.startswith('_'):
            continue
        alias_index[canonical] = canonical
        for alias in (meta.get('aliases') or []):
            alias_index[alias] = canonical

    rows = {}
    for repo, commits in commits_by_repo.items():
        for c in commits:
            raw = c.get('author_login') or c.get('author_email') or c.get('author_name')
            if not raw:
                continue
            login = alias_index.get(raw, raw)
            r = rows.setdefault(login, {'commits': 0, 'first': None, 'last': None})
            r['commits'] += 1
            d = c.get('date')
            if d:
                d = d[:10]
                if not r['first'] or d < r['first']:
                    r['first'] = d
                if not r['last'] or d > r['last']:
                    r['last'] = d

    out = []
    for login, r in rows.items():
        meta = cmap.get(login, {})
        if not isinstance(meta, dict):
            meta = {}
        role = 'bot' if meta.get('is_bot') else (meta.get('role') or 'contributor')
        if role == 'bot':
            # logins stay unique; the shared real_name "GitHub Actions (bot)"
            # would collapse two distinct bot identities into one label
            label = login if '[bot]' in login else f'{login} (bot)'
        else:
            label = meta.get('real_name') or login
        out.append({
            'login': login, 'label': label, 'role': role,
            'commits': r['commits'],
            'first': date.fromisoformat(r['first']),
            'last': date.fromisoformat(r['last']),
        })
    out.sort(key=lambda r: (r['first'], r['last']))
    return out


def main():
    rows = load_contributor_spans()
    n = len(rows)
    print(f'{n} commit-author identities (post-alias-merge):')
    for r in rows:
        print(f"  {r['label']:<38} {r['role']:<12} {r['commits']:>5}  "
              f"{r['first']} .. {r['last']}")

    plt.rcParams.update({
        'font.family': 'sans-serif',
        'font.size': 8.5,
        'text.color': INK,
        'axes.edgecolor': BASELINE,
        'xtick.color': INK_2,
        'ytick.color': INK,
    })
    fig, ax = plt.subplots(figsize=(8.4, 4.6), dpi=300)
    fig.patch.set_facecolor(SURFACE)
    ax.set_facecolor(SURFACE)

    min_width_days = 25  # single-commit identities still get a visible tick
    for i, r in enumerate(rows):
        start = mdates.date2num(r['first'])
        width = max(mdates.date2num(r['last']) - start, min_width_days)
        ax.barh(i, width, left=start, height=0.62,
                color=ROLE_COLORS[r['role']],
                edgecolor=(0.043, 0.043, 0.043, 0.10), linewidth=0.5)
        ax.annotate(f"{r['commits']:,}",
                    xy=(start + width, i), xytext=(4, 0),
                    textcoords='offset points', va='center', ha='left',
                    fontsize=7, color=INK_2)

    ax.set_yticks(range(n))
    ax.set_yticklabels([r['label'] for r in rows])
    ax.invert_yaxis()
    ax.xaxis.set_major_locator(mdates.YearLocator(2))
    ax.xaxis.set_minor_locator(mdates.YearLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
    ax.set_xlim(mdates.date2num(date(2013, 9, 1)), mdates.date2num(date(2026, 12, 31)))
    ax.grid(axis='x', which='both', color=GRID, linewidth=0.6)
    ax.set_axisbelow(True)
    for spine in ('top', 'right', 'left'):
        ax.spines[spine].set_visible(False)
    ax.tick_params(axis='y', length=0)
    ax.tick_params(axis='x', which='both', length=3, color=BASELINE)

    legend_roles = [r for r in ROLE_COLORS
                    if any(row['role'] == r for row in rows)]
    ax.legend(handles=[Patch(facecolor=ROLE_COLORS[r], label=r) for r in legend_roles],
              loc='lower left', frameon=False, fontsize=7.5, ncol=2,
              handlelength=1.2, handleheight=0.9, labelcolor=INK_2)

    fig.text(0.01, 0.01,
             f'Source: data/snapshots/{SNAPSHOT_DATE} (GitHub commit history, '
             f'post-alias-merge) · n = {n} commit-author identities · '
             f'bar label = captured commit count',
             fontsize=6.5, color=MUTED)

    fig.tight_layout(rect=(0, 0.03, 1, 1))
    OUT.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUT, facecolor=SURFACE)
    print(f'\nwrote {OUT.relative_to(ROOT)}')


if __name__ == '__main__':
    main()
