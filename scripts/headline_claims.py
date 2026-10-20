"""
headline_claims.py — one registry of every headline number the repo quotes, and
the snapshot each one must re-derive from (H7122).

Two snapshots live in this repo and they do not agree:

  csl-obs/org-live@1.0.0   data/summary.json (+ data/contributors.json), written by
                           the live-API pipeline (refresh.yml). Not reproducible
                           offline: re-running it hits the GitHub API.
  csl-obs/org@1.0.0        data/manifest.json + observatory/site/src/data/*.csv,
                           written by the offline transform. Reproducible from the
                           committed CSVs alone (reports/README.md's promise).

Historical vintages quoted in narrative docs are pinned as
`csl-obs/org@hist-YYYY-MM-DD`: their values are NOT re-derivable from the current
data/ tree, so the registry carries the values and the checker only enforces that
the quoted number matches the pin and that the surface names the snapshot + as-of.

`docs/SNAPSHOT_AUTHORITY.md` is the human-readable companion of
`data/headline_claims.json`: every surface → snapshot → as-of → dataset ID.

Usage (through the generator, which owns README/STATUS):
    python scripts/update_headline_numbers.py --check
"""
from __future__ import annotations

import csv
import json
import re
from dataclasses import dataclass, field
from pathlib import Path

LIVE_ID = 'csl-obs/org-live@1.0.0'
OFFLINE_ID = 'csl-obs/org@1.0.0'
REGISTRY = 'data/headline_claims.json'

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / 'data'
SITE_DATA = ROOT / 'observatory/site/src/data'

# Surfaces the uncovered-number guard sweeps. A number that is a known headline
# value may not appear anywhere in these files unless a registry claim covers
# the line (or an explicitly reasoned allowlist entry does).
SWEPT_GLOBS = (
    'README.md',
    'STATUS.md',
    'reports/*.md',
    'article/*.md',
    'docs/OBSERVATORY_ROADMAP.md',
    'docs/ANTHOLOGY_ALIGNMENT_2026Q4.md',
    'docs/SNAPSHOT_AUTHORITY.md',
)


@dataclass
class Snapshot:
    id: str
    as_of: str
    values: dict
    derived: bool = True


@dataclass
class Finding:
    claim_id: str
    file: str
    line: int
    message: str
    severity: str = 'fail'

    def __str__(self) -> str:
        where = f'{self.file}:{self.line}' if self.line else self.file
        return f'{self.severity.upper()}: [{self.claim_id}] {where}: {self.message}'


@dataclass
class Claim:
    id: str
    file: str
    pattern: str
    snapshot: str
    note: str = ''
    expected: dict = field(default_factory=dict)
    label_required: bool = False


# --------------------------------------------------------------------------- #
# snapshot derivation
# --------------------------------------------------------------------------- #
def _load_json(path: Path):
    return json.loads(path.read_text(encoding='utf-8'))


def _csv_rows(path: Path) -> int:
    with path.open(newline='', encoding='utf-8') as f:
        return sum(1 for _ in csv.DictReader(f))


def _issue_kind_split(path: Path) -> tuple[int, int]:
    issues = prs = 0
    with path.open(newline='', encoding='utf-8') as f:
        for row in csv.DictReader(f):
            if (row.get('kind') or '').upper() == 'PR':
                prs += 1
            else:
                issues += 1
    return issues, prs


def _correction_corpus(root: Path) -> tuple[int, int | None, str]:
    """(event rows, distinct dictionaries, dataset id).

    The release CSV is a 62 MB Git LFS object. CI checkouts that skip LFS get the
    pointer file, so the dictionary count comes back as None and the registry's
    pinned value is used instead — never a crash, never a fabricated count.
    """
    manifest = _load_json(root / 'data/manifest.json')
    entry = manifest['dataset_ids']['correction-events']
    csv_path = root / entry['file']
    head = csv_path.read_text(encoding='utf-8', errors='replace')[:80]
    if head.startswith('version https://git-lfs'):
        return entry['rows'], None, entry['id']
    with csv_path.open(newline='', encoding='utf-8') as f:
        dictionaries = {row['dict'] for row in csv.DictReader(f)}
    return entry['rows'], len(dictionaries), entry['id']


def _offline_contributors(root: Path) -> int:
    """Distinct humans with commit contributions (the bus-factor basis).

    Reuses scripts/bus_factor.py's bot-override logic so the number cannot drift
    from reports/bus_factor.md.
    """
    import sys

    scripts = str(root / 'scripts')
    if scripts not in sys.path:
        sys.path.insert(0, scripts)
    import bus_factor  # noqa: PLC0415 — deliberate late import, module runs no work at import

    per_repo, is_bot = bus_factor.load_contrib()
    humans = {login for repo in per_repo.values() for login in repo if not is_bot.get(login)}
    return len(humans)


def offline_as_of(root: Path = ROOT) -> str:
    manifest = _load_json(root / 'data/manifest.json')
    transformed = manifest.get('transformed_at', '')
    return transformed[:10] if transformed else manifest['snapshot_date']


def offline_stamp(root: Path = ROOT) -> str:
    """The provenance marker an offline-generated report carries in its header."""
    return f'`{OFFLINE_ID}` (as of {offline_as_of(root)})'


def live_stamp(root: Path = ROOT) -> str:
    """The provenance marker a live-pipeline-generated surface carries."""
    summary = _load_json(root / 'data/summary.json')
    return f'`{LIVE_ID}` (as of {summary["snapshot_date"]})'


def live_snapshot(root: Path = ROOT) -> Snapshot:
    summary = _load_json(root / 'data/summary.json')
    contributors = _load_json(root / 'data/contributors.json')
    obst_events, obst_dicts, _ = _correction_corpus(root)
    as_of = summary['snapshot_date']
    issues = summary['total_issues']
    prs = summary['total_pull_requests']
    values = {
        'repos': summary['repos_count'],
        'issues': issues,
        'prs': prs,
        'issues_prs': issues + prs,
        'commits': summary['total_commits'],
        'contributors': sum(1 for c in contributors if not c.get('is_bot')),
        'contributors_all': len(contributors),
        'span_years': int(as_of[:4]) - 2014 + 1,
        'span_end_year': int(as_of[:4]),
        'obst_events': obst_events,
    }
    if obst_dicts is not None:
        values['obst_dicts'] = obst_dicts
    return Snapshot(LIVE_ID, as_of, values)


def offline_snapshot(root: Path = ROOT) -> Snapshot:
    manifest = _load_json(root / 'data/manifest.json')
    files = manifest['files']
    site = root / 'observatory/site/src/data'
    issues, prs = _issue_kind_split(site / 'issues.csv')
    obst_events, obst_dicts, _ = _correction_corpus(root)
    as_of = offline_as_of(root)
    values = {
        'repos': files['repos.csv'],
        'issues': issues,
        'prs': prs,
        'issues_prs': files['issues.csv'],
        'commits': files['commits.csv'],
        'contributors': _offline_contributors(root),
        'obst_events': obst_events,
        'span_end_year': int(as_of[:4]),
        'span_years': int(as_of[:4]) - 2014 + 1,
    }
    if obst_dicts is not None:
        values['obst_dicts'] = obst_dicts
    # The manifest's own row counts must agree with the CSVs they describe.
    if values['issues'] + values['prs'] != values['issues_prs']:
        raise ValueError('issues.csv kind split does not match manifest.files[issues.csv]')
    return Snapshot(OFFLINE_ID, as_of, values)


_SNAPSHOT_CACHE: dict[str, dict[str, Snapshot]] = {}


def snapshots(root: Path = ROOT) -> dict[str, Snapshot]:
    """Both snapshots, derived once per process (the CSVs are read several times
    per check and the values cannot change under a single run)."""
    key = str(Path(root).resolve())
    if key not in _SNAPSHOT_CACHE:
        _SNAPSHOT_CACHE[key] = {LIVE_ID: live_snapshot(root), OFFLINE_ID: offline_snapshot(root)}
    return _SNAPSHOT_CACHE[key]


# --------------------------------------------------------------------------- #
# registry
# --------------------------------------------------------------------------- #
def load_claims(root: Path = ROOT) -> list[Claim]:
    raw = _load_json(root / REGISTRY)
    return [
        Claim(
            id=c['id'],
            file=c['file'],
            pattern=c['pattern'],
            snapshot=c['snapshot'],
            note=c.get('note', ''),
            expected={k: int(v) for k, v in (c.get('expected') or {}).items()},
            label_required=bool(c.get('label_required')),
        )
        for c in raw['claims']
    ]


def load_allowlist(root: Path = ROOT) -> list[dict]:
    raw = _load_json(root / REGISTRY)
    return raw.get('allow_uncovered', [])


def load_file_snapshots(root: Path = ROOT) -> list[dict]:
    """Files frozen on one vintage: their numbers may go claim-less, but only numbers
    belonging to THAT snapshot. A live-snapshot number inside a frozen article is still
    a failure — that cross-contamination is the bug this gate exists for."""
    raw = _load_json(root / REGISTRY)
    return raw.get('allow_file_snapshot', [])


# --------------------------------------------------------------------------- #
# checking
# --------------------------------------------------------------------------- #
def _as_int(text: str) -> int:
    return int(text.replace(',', '').strip())


def _expected_value(claim: Claim, metric: str, snaps: dict[str, Snapshot]) -> int | None:
    """A derived snapshot value always beats a pinned one; pins are for metrics the
    current tree cannot derive (historical vintages) or cannot see (LFS pointers)."""
    snap = snaps.get(claim.snapshot)
    if snap is not None and metric in snap.values:
        return snap.values[metric]
    return claim.expected.get(metric)


def check(root: Path = ROOT) -> list[Finding]:
    """Return every violation; empty list == clean."""
    snaps = snapshots(root)
    findings: list[Finding] = []
    # Covered = the CHARACTER SPANS of captured numbers, not whole lines: a claim
    # excusing line 40 must not also excuse an unrelated stale number typed beside it.
    covered: dict[str, dict[int, list[tuple[int, int]]]] = {}

    for claim in load_claims(root):
        path = root / claim.file
        if not path.exists():
            findings.append(Finding(claim.id, claim.file, 0, 'claim surface does not exist'))
            continue
        lines = path.read_text(encoding='utf-8').splitlines()
        regex = re.compile(claim.pattern)
        hits = 0
        for idx, line in enumerate(lines, start=1):
            match = regex.search(line)
            if not match:
                continue
            hits += 1
            line_spans = covered.setdefault(claim.file, {}).setdefault(idx, [])
            groups = match.groupdict()
            for metric, raw_value in groups.items():
                if raw_value is None:
                    continue
                line_spans.append(match.span(metric))
                expected = _expected_value(claim, metric, snaps)
                if expected is None:
                    findings.append(Finding(
                        claim.id, claim.file, idx,
                        f'metric {metric!r} has no value in snapshot {claim.snapshot} '
                        f'and no pinned expected value'))
                    continue
                found = _as_int(raw_value)
                if found != expected:
                    findings.append(Finding(
                        claim.id, claim.file, idx,
                        f'{metric} quotes {raw_value} but snapshot {claim.snapshot} '
                        f'says {expected:,} (as of {snaps[claim.snapshot].as_of if claim.snapshot in snaps else "pinned"})'))
            if claim.label_required:
                surface = '\n'.join(lines)
                snap_id = claim.snapshot
                snap = snaps.get(snap_id)
                as_of = snap.as_of if snap else (claim.expected.get('as_of') or '')
                if snap_id not in surface:
                    findings.append(Finding(
                        claim.id, claim.file, idx,
                        f'historical claim must name its snapshot {snap_id!r} '
                        f'(as of {as_of or "pinned historical vintage"}) on the surface'))
        if hits == 0:
            findings.append(Finding(
                claim.id, claim.file, 0,
                'pattern matches nothing — the claim rotted or the surface was rewritten'))

    findings.extend(_uncovered_numbers(root, covered))
    return findings


# Count metrics only. Years (span_end_year) and dates are not counts: they appear
# in prose constantly and would drown the guard in false positives.
# obst_events is deliberately absent: the OBS-T correction corpus is one dataset
# shared by both pipeline families (data/manifest.json dataset_ids), so it can
# never be a LIVE-vs-OFFLINE divergence. It is still claim-checked where it is a
# headline (STATUS.md, README.md) — just not swept as a cross-snapshot token.
COUNT_METRICS = (
    'repos', 'issues', 'prs', 'issues_prs', 'commits', 'contributors',
    'contributors_all', 'obst_dicts',
)


def _headline_tokens(root: Path = ROOT) -> list[re.Pattern]:
    """Every number a headline claim could legitimately quote, as a boundary-anchored regex."""
    tokens: set[str] = set()
    snaps = snapshots(root)
    for snap in snaps.values():
        for metric, value in snap.values.items():
            if metric not in COUNT_METRICS:
                continue
            tokens.add(f'{value:,}')
            tokens.add(str(value))
    raw = _load_json(root / REGISTRY)
    for claim in raw['claims']:
        for metric, value in (claim.get('expected') or {}).items():
            if metric not in COUNT_METRICS:
                continue
            tokens.add(f'{int(value):,}')
            tokens.add(str(int(value)))
    # Repo counts are small and appear in prose constantly; only match them when
    # they are attached to the word "repos"/"repositories".
    small = {t for t in tokens if len(t.replace(',', '')) <= 2}
    big = sorted(tokens - small, key=len, reverse=True)
    patterns = [
        re.compile(r'(?<![\d,])' + re.escape(t) + r'(?![\d,])') for t in big
    ]
    if small:
        alt = '|'.join(sorted((re.escape(t) for t in small), key=len, reverse=True))
        # lookahead, not a consuming group: the match must cover the digits only, so
        # a claim capturing those digits covers this occurrence.
        patterns.append(re.compile(
            rf'(?<![\d,])(?:{alt})(?=\s+(?:repos|repositories)\b)'))
    return patterns


def _value_index(root: Path = ROOT) -> dict[int, dict[str, set[str]]]:
    """int value -> {snapshot id: {metric}} for every count metric and pinned value."""
    index: dict[int, dict[str, set[str]]] = {}
    for snap in snapshots(root).values():
        for metric, value in snap.values.items():
            if metric not in COUNT_METRICS:
                continue
            index.setdefault(int(value), {}).setdefault(snap.id, set()).add(metric)
    raw = _load_json(root / REGISTRY)
    for claim in raw['claims']:
        for metric, value in (claim.get('expected') or {}).items():
            if metric not in COUNT_METRICS:
                continue
            index.setdefault(int(value), {}).setdefault(claim['snapshot'], set()).add(metric)
    return index


def _uncovered_numbers(root: Path, covered: dict[str, set[int]]) -> list[Finding]:
    findings: list[Finding] = []
    allow = load_allowlist(root)
    file_snapshots = load_file_snapshots(root)
    value_index = _value_index(root)
    used_allow: set[int] = set()
    used_frozen: set[int] = set()
    patterns = _headline_tokens(root)

    files: list[Path] = []
    for pattern in SWEPT_GLOBS:
        files.extend(sorted(root.glob(pattern)))

    for path in files:
        rel = path.relative_to(root).as_posix()
        for idx, line in enumerate(path.read_text(encoding='utf-8').splitlines(), start=1):
            line_spans = covered.get(rel, {}).get(idx, [])
            hits = [(p.search(line)) for p in patterns]
            hits = [m for m in hits if m]
            if not hits:
                continue
            uncovered = [
                m for m in hits
                if not any(start <= m.start() and m.end() <= end for start, end in line_spans)
            ]
            if not uncovered:
                continue
            allowed = False
            for pos, entry in enumerate(allow):
                if entry['file'] == rel and entry['contains'] in line:
                    used_allow.add(pos)
                    allowed = True
                    break
            if not allowed:
                for pos, entry in enumerate(file_snapshots):
                    if entry['file'] != rel:
                        continue
                    if all(entry['snapshot'] in value_index.get(_as_int(m.group(0)), {})
                           for m in uncovered):
                        used_frozen.add(pos)
                        allowed = True
                        break
            if not allowed:
                findings.append(Finding(
                    'uncovered-number', rel, idx,
                    f'quotes {uncovered[0].group(0)!r} with no registry claim — add a claim in '
                    'data/headline_claims.json or label the line and record why'))

    for pos, entry in enumerate(file_snapshots):
        if pos not in used_frozen:
            findings.append(Finding(
                'stale-frozen-file', entry['file'], 0,
                f'frozen-file allowance for {entry["snapshot"]} excused nothing in this run — '
                f'the file no longer quotes that vintage; delete the entry'))

    for pos, entry in enumerate(allow):
        if pos not in used_allow:
            findings.append(Finding(
                'stale-allowlist', entry['file'], 0,
                f'allowlist entry matched nothing (contains={entry["contains"]!r}) — '
                f'the line it excused is gone; delete the entry'))
    return findings


def summary_line(root: Path = ROOT) -> str:
    """One-line snapshot census, printed by both --write and --check runs."""
    snaps = snapshots(root)
    live, offline = snaps[LIVE_ID], snaps[OFFLINE_ID]
    return (
        f'{LIVE_ID} (as of {live.as_of}): {live.values["repos"]} repos, '
        f'{live.values["issues"]:,} issues + {live.values["prs"]:,} PRs = '
        f'{live.values["issues_prs"]:,}, {live.values["commits"]:,} commits, '
        f'{live.values["contributors"]} human contributors · '
        f'{OFFLINE_ID} (as of {offline.as_of}): {offline.values["repos"]} repos, '
        f'{offline.values["issues"]:,} issues + {offline.values["prs"]:,} PRs = '
        f'{offline.values["issues_prs"]:,}, {offline.values["commits"]:,} commits'
    )


def main(argv: list[str] | None = None) -> int:
    import sys

    argv = list(sys.argv[1:] if argv is None else argv)
    print(summary_line())
    findings = check()
    if not findings:
        print('PASS: every quoted headline number re-derives from its registered snapshot')
        return 0
    for finding in findings:
        print(finding)
    print(f'FAIL: {len(findings)} headline claim(s) do not match their snapshot')
    return 1


if __name__ == '__main__':
    raise SystemExit(main())
