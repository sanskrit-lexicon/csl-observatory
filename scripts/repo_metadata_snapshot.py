#!/usr/bin/env python3
"""Build repository metadata-completeness snapshot rows.

The offline mode validates the target schema from committed `repos.csv` and
`repo_health.csv` without calling GitHub. The live mode uses `gh api` to inspect
repository trees and releases, then writes the same schema.

Examples:
    python scripts/repo_metadata_snapshot.py --offline
    python scripts/repo_metadata_snapshot.py --repo csl-observatory --out tmp.csv
"""

from __future__ import annotations

import argparse
import csv
import sys
from datetime import datetime, timezone
from pathlib import Path

from _gh import run_gh


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "observatory" / "site" / "src" / "data"
REPOS_CSV = DATA / "repos.csv"
HEALTH_CSV = DATA / "repo_health.csv"
OUT_CSV = DATA / "repo_metadata.csv"
OWNER = "sanskrit-lexicon"
SNAPSHOT_MONTH = datetime.now(timezone.utc).strftime("%Y-%m")
DEFAULT_CACHE_DIR = ROOT / "observatory" / "snapshots" / SNAPSHOT_MONTH / "repo_metadata"

FIELDS = [
    "repo",
    "archived",
    "default_branch",
    "license_class",
    "license",
    "has_description",
    "has_readme",
    "has_citation",
    "has_issue_template",
    "has_pr_template",
    "workflow_count",
    "has_workflows",
    "has_dependabot",
    "has_codeql",
    "release_count",
    "latest_release",
    "metadata_score",
    "metadata_flags",
    "fetched_at",
    "fetch_warning",
]

CORE_SCORE_FIELDS = [
    "has_description",
    "has_readme",
    "has_citation",
    "has_issue_template",
    "has_pr_template",
    "has_workflows",
    "has_dependabot",
    "has_codeql",
]


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def path_set_from_tree(
    repo: str,
    branch: str,
    owner: str,
    cache_dir: Path | None,
    refresh_cache: bool,
) -> tuple[set[str], str]:
    data, warning = run_gh(
        f"repos/{owner}/{repo}/git/trees/{branch}?recursive=1",
        cache_dir=cache_dir,
        cache_repo=repo,
        cache_topic="tree",
        refresh_cache=refresh_cache,
    )
    if warning and data is None:
        return set(), warning
    if not isinstance(data, dict) or not isinstance(data.get("tree"), list):
        return set(), "unexpected tree API shape"
    paths = {
        str(item.get("path", "")).strip()
        for item in data["tree"]
        if isinstance(item, dict) and item.get("type") == "blob"
    }
    return {path for path in paths if path}, ""


def release_info(
    repo: str,
    owner: str,
    cache_dir: Path | None,
    refresh_cache: bool,
) -> tuple[int | str, str, str]:
    # The releases endpoint is paginated at per_page=100; follow pages until a
    # short page so the count is not silently capped for repos with >100
    # releases. Bound the walk to avoid unbounded work on pathological repos.
    per_page, max_pages = 100, 20
    releases: list[object] = []
    latest = ""
    for page in range(1, max_pages + 1):
        data, warning = run_gh(
            f"repos/{owner}/{repo}/releases?per_page={per_page}&page={page}",
            cache_dir=cache_dir,
            cache_repo=repo,
            cache_topic="releases",
            refresh_cache=refresh_cache,
        )
        if warning and data is None:
            if releases:
                return len(releases), latest, f"partial release pagination: {warning}"
            return "unknown", "unknown", warning
        if not isinstance(data, list):
            if releases:
                return len(releases), latest, "unexpected releases API shape on later page"
            return "unknown", "unknown", "unexpected releases API shape"
        if page == 1 and data and isinstance(data[0], dict):
            latest = str(data[0].get("tag_name") or data[0].get("name") or "")
        releases.extend(data)
        if len(data) < per_page:
            return len(releases), latest, ""
    return len(releases), latest, f"release count truncated at {max_pages * per_page}"


def yes_no_unknown(value: bool | None) -> str:
    if value is None:
        return "unknown"
    return "yes" if value else "no"


def detect_metadata(paths: set[str]) -> dict[str, str | int]:
    lower_paths = {path.lower() for path in paths}
    root_lower = {path.lower() for path in paths if "/" not in path}
    workflow_paths = [
        path for path in lower_paths
        if path.startswith(".github/workflows/")
        and (path.endswith(".yml") or path.endswith(".yaml"))
    ]
    has_issue_template = any(
        path.startswith(".github/issue_template/") for path in lower_paths
    ) or ".github/issue_template.md" in lower_paths or "issue_template.md" in root_lower
    has_pr_template = (
        ".github/pull_request_template.md" in lower_paths
        or "pull_request_template.md" in root_lower
        or any(path.startswith(".github/pull_request_template/") for path in lower_paths)
    )
    has_codeql = any("codeql" in path for path in workflow_paths) or any(
        path.startswith(".github/codeql/") for path in lower_paths
    )
    return {
        "has_readme": yes_no_unknown(any(path.startswith("readme") for path in root_lower)),
        "has_citation": yes_no_unknown("citation.cff" in root_lower),
        "has_issue_template": yes_no_unknown(has_issue_template),
        "has_pr_template": yes_no_unknown(has_pr_template),
        "workflow_count": len(workflow_paths),
        "has_workflows": yes_no_unknown(bool(workflow_paths)),
        "has_dependabot": yes_no_unknown(
            ".github/dependabot.yml" in lower_paths
            or ".github/dependabot.yaml" in lower_paths
        ),
        "has_codeql": yes_no_unknown(has_codeql),
    }


def offline_metadata() -> dict[str, str | int]:
    return {
        "has_readme": "unknown",
        "has_citation": "unknown",
        "has_issue_template": "unknown",
        "has_pr_template": "unknown",
        "workflow_count": "unknown",
        "has_workflows": "unknown",
        "has_dependabot": "unknown",
        "has_codeql": "unknown",
        "release_count": "unknown",
        "latest_release": "unknown",
    }


def metadata_flags(row: dict[str, str]) -> str:
    flags: list[str] = []
    if row["has_description"] == "no":
        flags.append("missing-description")
    if row["license_class"] == "none":
        flags.append("no-license")
    elif row["license_class"] == "unrecognised":
        flags.append("license-unrecognised")
    if row["default_branch"] == "master":
        flags.append("legacy-branch")
    elif row["default_branch"] not in ("main", "master"):
        flags.append(f"branch:{row['default_branch']}")

    for field, flag in [
        ("has_readme", "missing-readme"),
        ("has_citation", "missing-citation"),
        ("has_issue_template", "missing-issue-template"),
        ("has_pr_template", "missing-pr-template"),
        ("has_workflows", "no-workflows"),
        ("has_dependabot", "missing-dependabot"),
        ("has_codeql", "missing-codeql"),
    ]:
        if row[field] == "no":
            flags.append(flag)
        elif row[field] == "unknown":
            flags.append(flag.replace("missing-", "").replace("no-", "") + "-unknown")

    if row["release_count"] == "0":
        flags.append("no-releases")
    elif row["release_count"] == "unknown":
        flags.append("releases-unknown")

    return "|".join(flags)


def metadata_score(row: dict[str, str]) -> int:
    score = sum(1 for field in CORE_SCORE_FIELDS if row[field] == "yes")
    if row["license_class"] == "recognised":
        score += 1
    if row["default_branch"] == "main":
        score += 1
    return score


def build_rows(args: argparse.Namespace) -> list[dict[str, str]]:
    repos = read_csv(REPOS_CSV)
    health = {row["repo"]: row for row in read_csv(HEALTH_CSV)}
    selected = set(args.repo or [])
    fetched_at = datetime.now(timezone.utc).isoformat(timespec="seconds")
    rows: list[dict[str, str]] = []

    for repo_row in repos:
        repo = repo_row["repo"]
        if selected and repo not in selected:
            continue
        health_row = health.get(repo, {})
        row: dict[str, str] = {
            "repo": repo,
            "archived": repo_row["archived"].strip().lower(),
            "default_branch": repo_row["default_branch"].strip(),
            "license_class": health_row.get("license_class", ""),
            "license": (repo_row.get("license") or "").strip(),
            "has_description": health_row.get("has_description", "yes" if repo_row["description"].strip() else "no"),
            "fetched_at": fetched_at,
            "fetch_warning": "",
        }

        warnings: list[str] = []
        if args.offline:
            row.update({key: str(value) for key, value in offline_metadata().items()})
            warnings.append("offline mode; live metadata not fetched")
        else:
            paths, warning = path_set_from_tree(
                repo,
                row["default_branch"],
                args.owner,
                args.cache_dir,
                args.refresh_cache,
            )
            if warning:
                row.update({key: str(value) for key, value in offline_metadata().items()})
                warnings.append(f"tree: {warning}")
            else:
                row.update({key: str(value) for key, value in detect_metadata(paths).items()})
                count, latest, release_warning = release_info(
                    repo,
                    args.owner,
                    args.cache_dir,
                    args.refresh_cache,
                )
                row["release_count"] = str(count)
                row["latest_release"] = latest
                if release_warning:
                    warnings.append(f"releases: {release_warning}")

        row["fetch_warning"] = "; ".join(warnings)
        row["metadata_score"] = str(metadata_score(row))
        row["metadata_flags"] = metadata_flags(row)
        rows.append(row)

    return rows


def write_rows(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        writer.writeheader()
        for row in sorted(rows, key=lambda item: (-int(item["metadata_score"]), item["repo"])):
            writer.writerow(row)


# live fields that may legitimately be "unknown"; if any is unknown the row must
# carry a matching flag, otherwise an unfetched repo would look fully populated.
_UNKNOWN_CAPABLE = (
    "has_readme", "has_citation", "has_issue_template", "has_pr_template",
    "workflow_count", "has_workflows", "has_dependabot", "has_codeql", "release_count",
)


def check_existing(args: argparse.Namespace) -> int:
    """Read-only schema/policy validation of an existing repo_metadata.csv."""
    if not args.out.exists():
        raise SystemExit(f"{args.out} does not exist")
    with args.out.open(encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        fieldnames = reader.fieldnames
    if fieldnames != FIELDS:
        raise SystemExit(f"repo_metadata.csv schema mismatch: {fieldnames}")
    repo_set = {row["repo"] for row in read_csv(REPOS_CSV)}
    row_repos = {row["repo"] for row in rows}
    if row_repos != repo_set:
        missing = sorted(repo_set - row_repos)
        extra = sorted(row_repos - repo_set)
        raise SystemExit(
            f"repo_metadata.csv repo mismatch vs repos.csv; missing={missing}; extra={extra}"
        )
    for row in rows:
        int(row["metadata_score"])
        if row["workflow_count"] != "unknown":
            int(row["workflow_count"])
        if row["release_count"] != "unknown":
            int(row["release_count"])
        flags = [flag for flag in row["metadata_flags"].split("|") if flag]
        unknown_fields = [field for field in _UNKNOWN_CAPABLE if row[field] == "unknown"]
        if unknown_fields and not flags:
            raise SystemExit(
                f"{row['repo']} has unknown fields {unknown_fields} but no metadata flags"
            )
    print(f"OK: repo_metadata rows={len(rows)}")
    return 0


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--owner", default=OWNER, help="GitHub owner/org to query")
    parser.add_argument("--out", type=Path, default=OUT_CSV, help="CSV output path")
    parser.add_argument("--repo", action="append", help="Limit to a repository name; repeatable")
    parser.add_argument("--offline", action="store_true", help="Do not call GitHub; emit schema with unknown live fields")
    parser.add_argument(
        "--cache-dir",
        type=Path,
        default=DEFAULT_CACHE_DIR,
        help="Directory for raw live metadata responses",
    )
    parser.add_argument(
        "--refresh-cache",
        action="store_true",
        help="Ignore existing cache files and refresh them through gh api",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Validate an existing repo_metadata.csv against repos.csv without rewriting it",
    )
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    if args.check:
        return check_existing(args)
    rows = build_rows(args)
    write_rows(args.out, rows)
    warnings = sum(1 for row in rows if row["fetch_warning"])
    print(f"wrote {args.out}")
    print(f"  repos: {len(rows)}")
    print(f"  rows with warnings: {warnings}")
    if args.offline:
        print("  mode: offline")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
