#!/usr/bin/env python3
"""Read-only regression checks for repository-health generated artifacts.

The repository-health report is generated from the committed GitHub snapshot in
``observatory/site/src/data/repos.csv``. This script checks that the generated
CSV and Markdown report still match the expected schema and policy-derived
flags. It does not call GitHub and it does not rewrite any files.

Usage:
    python scripts/repo_health_regression.py
"""

from __future__ import annotations

import csv
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
# Single source of truth: reuse the generator's license/cleanup/staleness policy
# so the regression checker cannot silently drift from repo_health.py.
from repo_health import (  # noqa: E402
    CLEANUP_NAMES,
    CLEANUP_PREFIXES,
    STALE_DAYS,
    license_class,
)


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "observatory" / "site" / "src" / "data"
REPOS_CSV = DATA / "repos.csv"
HEALTH_CSV = DATA / "repo_health.csv"
REPORT_MD = ROOT / "reports" / "repo_health.md"

# After the RH3 archiving (2026-06-19), 4 of the 6 cleanup candidates are
# archived and so no longer carry the `cleanup-candidate` flag. Only the two
# still-live repos (open issues pending funderburkjim) remain candidates.
EXPECTED_CLEANUP_CANDIDATES = {
    "temp_corrections_ap90",
    "temp_corrections_mw",
}

REPOS_FIELDS = [
    "repo",
    "description",
    "primary_language",
    "size_kb",
    "created_at",
    "updated_at",
    "pushed_at",
    "default_branch",
    "stars",
    "forks",
    "open_issues",
    "archived",
    "license",
    "all_languages",
]

HEALTH_FIELDS = [
    "repo",
    "license_class",
    "license",
    "default_branch",
    "open_issues",
    "days_since_push",
    "has_description",
    "archived",
    "flag_count",
    "flags",
]

REQUIRED_REPORT_SECTIONS = [
    "## Headline",
    "## Licensing",
    "## Default branch",
    "## Missing a description",
    "## Cleanup candidates (live, not archived)",
    "## Staleness",
    "## Repositories by flag count",
]


class CheckResult:
    def __init__(self) -> None:
        self.failures: list[str] = []

    def fail(self, message: str) -> None:
        self.failures.append(message)

    @property
    def ok(self) -> bool:
        return not self.failures


def read_csv(path: Path, expected_fields: list[str], check: CheckResult) -> list[dict[str, str]]:
    if not path.exists():
        check.fail(f"Missing required file: {path.relative_to(ROOT)}")
        return []

    with path.open(encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        if reader.fieldnames != expected_fields:
            check.fail(
                f"{path.relative_to(ROOT)} schema drift: expected {expected_fields}, "
                f"found {reader.fieldnames}"
            )
            return list(reader)
        return list(reader)


def parse_int(value: str, field: str, repo: str, check: CheckResult) -> int | None:
    text = (value or "").strip()
    if not text:
        return None
    try:
        return int(text)
    except ValueError:
        check.fail(f"{repo}: {field} is not an integer: {value!r}")
        return None


def expected_flags(repo_row: dict[str, str], health_row: dict[str, str], check: CheckResult) -> list[str]:
    repo = repo_row["repo"]
    branch = repo_row["default_branch"].strip()
    archived = repo_row["archived"].strip().lower()
    flags: list[str] = []

    lic = license_class(repo_row["license"])
    if lic == "none":
        flags.append("no-license")
    elif lic == "unrecognised":
        flags.append("license-unrecognised")

    if branch == "master":
        flags.append("legacy-branch")
    elif branch not in ("main", "master"):
        flags.append(f"branch:{branch}")

    if not repo_row["description"].strip():
        flags.append("no-description")

    cleanup = repo.startswith(CLEANUP_PREFIXES) or repo in CLEANUP_NAMES
    if cleanup and archived != "true":
        flags.append("cleanup-candidate")

    days_since_push = parse_int(
        health_row["days_since_push"], "days_since_push", repo, check
    )
    if days_since_push is not None and days_since_push < 0:
        check.fail(f"{repo}: days_since_push is negative: {days_since_push}")
    if days_since_push is not None and days_since_push > STALE_DAYS:
        flags.append("stale")

    return flags


def check_repo_sets(
    repos_rows: list[dict[str, str]],
    health_rows: list[dict[str, str]],
    check: CheckResult,
) -> tuple[dict[str, dict[str, str]], dict[str, dict[str, str]]]:
    repos_by_name = {row["repo"]: row for row in repos_rows}
    health_by_name = {row["repo"]: row for row in health_rows}

    if len(repos_by_name) != len(repos_rows):
        check.fail("observatory/site/src/data/repos.csv has duplicate repo names")
    if len(health_by_name) != len(health_rows):
        check.fail("observatory/site/src/data/repo_health.csv has duplicate repo names")

    missing = sorted(set(repos_by_name) - set(health_by_name))
    extra = sorted(set(health_by_name) - set(repos_by_name))
    if missing:
        check.fail(f"repo_health.csv is missing repos from repos.csv: {', '.join(missing)}")
    if extra:
        check.fail(f"repo_health.csv has repos not present in repos.csv: {', '.join(extra)}")

    return repos_by_name, health_by_name


def check_health_rows(
    repos_by_name: dict[str, dict[str, str]],
    health_rows: list[dict[str, str]],
    check: CheckResult,
) -> None:
    for health_row in health_rows:
        repo = health_row["repo"]
        repo_row = repos_by_name.get(repo)
        if repo_row is None:
            continue

        expected_license_class = license_class(repo_row["license"])
        comparisons = {
            "license_class": expected_license_class,
            "license": repo_row["license"].strip(),
            "default_branch": repo_row["default_branch"].strip(),
            "open_issues": str(int(repo_row["open_issues"] or 0)),
            "has_description": "yes" if repo_row["description"].strip() else "no",
            "archived": repo_row["archived"].strip().lower(),
        }
        for field, expected in comparisons.items():
            if health_row[field] != expected:
                check.fail(
                    f"{repo}: {field} mismatch in repo_health.csv: "
                    f"expected {expected!r}, found {health_row[field]!r}"
                )

        flags = expected_flags(repo_row, health_row, check)
        expected_flag_text = "|".join(flags)
        if health_row["flags"] != expected_flag_text:
            check.fail(
                f"{repo}: flags mismatch: expected {expected_flag_text!r}, "
                f"found {health_row['flags']!r}"
            )

        expected_flag_count = str(len(flags))
        if health_row["flag_count"] != expected_flag_count:
            check.fail(
                f"{repo}: flag_count mismatch: expected {expected_flag_count}, "
                f"found {health_row['flag_count']!r}"
            )

    sorted_repos = [
        row["repo"]
        for row in sorted(
            health_rows,
            key=lambda row: (-int(row["flag_count"] or 0), row["repo"]),
        )
    ]
    actual_repos = [row["repo"] for row in health_rows]
    if actual_repos != sorted_repos:
        check.fail("repo_health.csv is not sorted by (-flag_count, repo)")


def split_flags(row: dict[str, str]) -> list[str]:
    return [flag for flag in row["flags"].split("|") if flag]


def expected_report_lines(health_rows: list[dict[str, str]]) -> list[str]:
    n = len(health_rows)
    license_counts = Counter(row["license_class"] for row in health_rows)
    legacy_count = sum(1 for row in health_rows if row["default_branch"] == "master")
    no_desc_count = sum(1 for row in health_rows if row["has_description"] == "no")
    cleanup_count = sum(
        1 for row in health_rows if "cleanup-candidate" in split_flags(row)
    )
    stale_count = sum(1 for row in health_rows if "stale" in split_flags(row))
    clean_count = sum(1 for row in health_rows if row["flag_count"] == "0")
    no_license = license_counts["none"]
    pct = 100 * no_license // n if n else 0

    return [
        f"| Repositories audited | {n} |",
        f"| **No license at all** | **{no_license} / {n}** ({pct}%) |",
        f"| License file unrecognised (`NOASSERTION`) | {license_counts['unrecognised']} / {n} |",
        f"| Recognised SPDX license | {license_counts['recognised']} / {n} |",
        f"| Default branch `master` (legacy) | {legacy_count} / {n} |",
        f"| Missing a description | {no_desc_count} / {n} |",
        f"| Live cleanup candidates (`temp_*`/`test_*`/legacy) | {cleanup_count} |",
        f"| Stale (no push in {STALE_DAYS}+ days) | {stale_count} |",
        f"| Clean (no flags) | {clean_count} / {n} |",
    ]


def check_cleanup_candidates(health_rows: list[dict[str, str]], check: CheckResult) -> None:
    actual = {
        row["repo"]
        for row in health_rows
        if "cleanup-candidate" in split_flags(row)
    }
    if actual != EXPECTED_CLEANUP_CANDIDATES:
        check.fail(
            "Cleanup candidate set changed: expected "
            f"{sorted(EXPECTED_CLEANUP_CANDIDATES)}, found {sorted(actual)}"
        )


def check_report(
    health_rows: list[dict[str, str]],
    check: CheckResult,
) -> None:
    if not REPORT_MD.exists():
        check.fail(f"Missing required file: {REPORT_MD.relative_to(ROOT)}")
        return

    text = REPORT_MD.read_text(encoding="utf-8")
    for section in REQUIRED_REPORT_SECTIONS:
        if section not in text:
            check.fail(f"reports/repo_health.md is missing section {section!r}")

    for line in expected_report_lines(health_rows):
        if line not in text:
            check.fail(f"reports/repo_health.md is missing expected headline line: {line}")

    branch_counts = Counter(row["default_branch"] for row in health_rows)
    for branch, count in branch_counts.items():
        line = f"| `{branch}` | {count} |"
        if line not in text:
            check.fail(f"reports/repo_health.md is missing branch-count line: {line}")


def main() -> int:
    check = CheckResult()
    repos_rows = read_csv(REPOS_CSV, REPOS_FIELDS, check)
    health_rows = read_csv(HEALTH_CSV, HEALTH_FIELDS, check)

    repos_by_name, _health_by_name = check_repo_sets(repos_rows, health_rows, check)
    check_health_rows(repos_by_name, health_rows, check)
    check_cleanup_candidates(health_rows, check)
    check_report(health_rows, check)

    if not check.ok:
        print("Repository-health regression failed:", file=sys.stderr)
        for failure in check.failures:
            print(f"  - {failure}", file=sys.stderr)
        return 1

    license_counts = Counter(row["license_class"] for row in health_rows)
    cleanup = sorted(
        row["repo"]
        for row in health_rows
        if "cleanup-candidate" in split_flags(row)
    )
    print("OK: repository-health artifacts passed regression checks.")
    print(f"  repos: {len(health_rows)}")
    print(
        "  licenses: "
        f"none={license_counts['none']} "
        f"NOASSERTION={license_counts['unrecognised']} "
        f"recognised={license_counts['recognised']}"
    )
    print(f"  cleanup candidates: {', '.join(cleanup)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
