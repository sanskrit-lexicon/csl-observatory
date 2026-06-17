#!/usr/bin/env python3
"""Build a workflow/release reliability baseline for active repositories."""

from __future__ import annotations

import argparse
import base64
import csv
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

from _gh import run_gh


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "observatory" / "site" / "src" / "data"
METADATA_CSV = DATA / "repo_metadata.csv"
OUT_CSV = DATA / "workflow_health.csv"
OUT_REPORT = ROOT / "reports" / "workflow_health.md"
OWNER = "sanskrit-lexicon"
SNAPSHOT_MONTH = datetime.now(timezone.utc).strftime("%Y-%m")
DEFAULT_CACHE_DIR = ROOT / "observatory" / "snapshots" / SNAPSHOT_MONTH / "workflow_health"

FIELDS = [
    "repo",
    "archived",
    "default_branch",
    "license_class",
    "workflow_count",
    "active_workflow_count",
    "disabled_workflow_count",
    "scheduled_workflow_count",
    "artifact_refresh_workflow_count",
    "deploy_workflow_count",
    "ci_workflow_count",
    "has_dependabot",
    "has_codeql",
    "release_count",
    "latest_release",
    "workflow_health_score",
    "workflow_flags",
    "workflow_names",
    "fetched_at",
    "fetch_warning",
]


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def workflow_list(
    repo: str,
    owner: str,
    cache_dir: Path | None,
    refresh_cache: bool,
) -> tuple[list[dict[str, str]], str]:
    data, warning = run_gh(
        f"repos/{owner}/{repo}/actions/workflows?per_page=100",
        cache_dir=cache_dir,
        cache_repo=repo,
        cache_topic="workflows",
        refresh_cache=refresh_cache,
    )
    if warning and data is None:
        return [], warning
    if not isinstance(data, dict) or not isinstance(data.get("workflows"), list):
        return [], "unexpected workflows API shape"
    workflows = [item for item in data["workflows"] if isinstance(item, dict)]
    return workflows, warning


def workflow_content(
    repo: str,
    owner: str,
    branch: str,
    path: str,
    cache_dir: Path | None,
    refresh_cache: bool,
) -> tuple[str, str]:
    endpoint = f"repos/{owner}/{repo}/contents/{path}?ref={branch}"
    data, warning = run_gh(
        endpoint,
        cache_dir=cache_dir,
        cache_repo=repo,
        cache_topic="content",
        refresh_cache=refresh_cache,
    )
    if warning and data is None:
        return "", warning
    if not isinstance(data, dict):
        return "", "unexpected workflow content API shape"
    encoded = str(data.get("content") or "").replace("\n", "")
    if not encoded:
        return "", "workflow content missing"
    try:
        return base64.b64decode(encoded).decode("utf-8", errors="replace"), warning
    except (ValueError, OSError) as exc:
        return "", f"workflow content decode failed: {exc}"


def yes(value: str) -> bool:
    return str(value).strip().lower() == "yes"


def count_value(value: str) -> int:
    try:
        return int(str(value).strip())
    except ValueError:
        return 0


def content_has_schedule(content: str) -> bool:
    lower = content.lower()
    return bool(re.search(r"(?m)^\s*-\s*cron\s*:", lower) or re.search(r"(?m)^\s*cron\s*:", lower))


def classify_workflow(name: str, path: str, content: str) -> dict[str, bool]:
    text = f"{name} {path} {content}".lower()
    return {
        "scheduled": content_has_schedule(content),
        "artifact_refresh": any(token in text for token in [
            "stardict",
            "artifact",
            "refresh",
            "xampp",
            "homepage",
            "pages",
            "json",
            "deploy",
        ]),
        "deploy": any(token in text for token in ["deploy", "pages", "gh-pages", "homepage"]),
        "ci": any(token in text for token in ["ci", "test", "pytest", "build", "lint", "check"]),
    }


def offline_row(meta: dict[str, str], fetched_at: str) -> dict[str, str]:
    workflow_count = meta.get("workflow_count", "unknown")
    row = {
        "repo": meta["repo"],
        "archived": meta["archived"],
        "default_branch": meta["default_branch"],
        "license_class": meta["license_class"],
        "workflow_count": workflow_count,
        "active_workflow_count": "unknown",
        "disabled_workflow_count": "unknown",
        "scheduled_workflow_count": "unknown",
        "artifact_refresh_workflow_count": "unknown",
        "deploy_workflow_count": "unknown",
        "ci_workflow_count": "unknown",
        "has_dependabot": meta.get("has_dependabot", "unknown"),
        "has_codeql": meta.get("has_codeql", "unknown"),
        "release_count": meta.get("release_count", "unknown"),
        "latest_release": meta.get("latest_release", ""),
        "workflow_health_score": "0",
        "workflow_flags": "",
        "workflow_names": "",
        "fetched_at": fetched_at,
        "fetch_warning": "offline mode; workflow list/content not fetched",
    }
    row["workflow_health_score"] = str(workflow_score(row))
    row["workflow_flags"] = workflow_flags(row)
    return row


def workflow_score(row: dict[str, str]) -> int:
    score = 0
    if count_value(row["workflow_count"]) > 0:
        score += 2
    if count_value(row["active_workflow_count"]) > 0:
        score += 1
    if count_value(row["scheduled_workflow_count"]) > 0:
        score += 1
    if count_value(row["artifact_refresh_workflow_count"]) > 0:
        score += 1
    if yes(row["has_dependabot"]):
        score += 1
    if yes(row["has_codeql"]):
        score += 1
    if count_value(row["release_count"]) > 0:
        score += 1
    return score


def workflow_flags(row: dict[str, str]) -> str:
    flags: list[str] = []
    if row["archived"] == "true":
        flags.append("archived")
    if row["workflow_count"] == "unknown":
        flags.append("workflows-unknown")
    elif count_value(row["workflow_count"]) == 0:
        flags.append("no-workflows")
    if row["active_workflow_count"] == "unknown":
        flags.append("active-workflows-unknown")
    elif count_value(row["active_workflow_count"]) == 0 and count_value(row["workflow_count"]) > 0:
        flags.append("no-active-workflows")
    if count_value(row["disabled_workflow_count"]) > 0:
        flags.append("disabled-workflows")
    for field, flag in [
        ("scheduled_workflow_count", "no-scheduled-workflows"),
        ("artifact_refresh_workflow_count", "no-artifact-refresh-workflow"),
    ]:
        if row[field] == "unknown":
            flags.append(flag.replace("no-", "") + "-unknown")
        elif count_value(row[field]) == 0:
            flags.append(flag)
    if row["has_dependabot"] == "no":
        flags.append("missing-dependabot")
    elif row["has_dependabot"] == "unknown":
        flags.append("dependabot-unknown")
    if row["has_codeql"] == "no":
        flags.append("missing-codeql")
    elif row["has_codeql"] == "unknown":
        flags.append("codeql-unknown")
    if row["release_count"] == "unknown":
        flags.append("releases-unknown")
    elif count_value(row["release_count"]) == 0:
        flags.append("no-releases")
    return "|".join(flags)


def build_row(
    meta: dict[str, str],
    args: argparse.Namespace,
    fetched_at: str,
) -> dict[str, str]:
    if args.offline:
        return offline_row(meta, fetched_at)

    repo = meta["repo"]
    warnings: list[str] = []
    workflows, warning = workflow_list(repo, args.owner, args.cache_dir, args.refresh_cache)
    if warning:
        warnings.append(f"workflows: {warning}")
    if warning and not workflows:
        row = offline_row(meta, fetched_at)
        row["fetch_warning"] = "; ".join(warnings)
        return row

    active = [item for item in workflows if str(item.get("state") or "") == "active"]
    disabled = [item for item in workflows if str(item.get("state") or "") != "active"]
    classifications = []
    names = []

    for workflow in workflows:
        name = str(workflow.get("name") or "")
        path = str(workflow.get("path") or "")
        names.append(name or path)
        content = ""
        if path and not path.startswith("dynamic/"):
            content, content_warning = workflow_content(
                repo,
                args.owner,
                meta["default_branch"],
                path,
                args.cache_dir,
                args.refresh_cache,
            )
            if content_warning:
                warnings.append(f"{path}: {content_warning}")
        classifications.append(classify_workflow(name, path, content))

    row = {
        "repo": repo,
        "archived": meta["archived"],
        "default_branch": meta["default_branch"],
        "license_class": meta["license_class"],
        "workflow_count": str(len(workflows)),
        "active_workflow_count": str(len(active)),
        "disabled_workflow_count": str(len(disabled)),
        "scheduled_workflow_count": str(sum(1 for item in classifications if item["scheduled"])),
        "artifact_refresh_workflow_count": str(sum(1 for item in classifications if item["artifact_refresh"])),
        "deploy_workflow_count": str(sum(1 for item in classifications if item["deploy"])),
        "ci_workflow_count": str(sum(1 for item in classifications if item["ci"])),
        "has_dependabot": meta.get("has_dependabot", "unknown"),
        "has_codeql": meta.get("has_codeql", "unknown"),
        "release_count": meta.get("release_count", "unknown"),
        "latest_release": meta.get("latest_release", ""),
        "workflow_health_score": "0",
        "workflow_flags": "",
        "workflow_names": "|".join(sorted(name for name in names if name)),
        "fetched_at": fetched_at,
        "fetch_warning": "; ".join(warnings),
    }
    row["workflow_health_score"] = str(workflow_score(row))
    row["workflow_flags"] = workflow_flags(row)
    return row


def build_rows(args: argparse.Namespace) -> list[dict[str, str]]:
    metadata = read_csv(args.metadata)
    selected = set(args.repo or [])
    fetched_at = datetime.now(timezone.utc).isoformat(timespec="seconds")
    rows = [
        build_row(meta, args, fetched_at)
        for meta in metadata
        if not selected or meta["repo"] in selected
    ]
    return sorted(rows, key=lambda row: (-int(row["workflow_health_score"]), row["repo"]))


def write_rows(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)


def pct(numerator: int, denominator: int) -> str:
    if denominator == 0:
        return "0.0%"
    return f"{numerator / denominator * 100:.1f}%"


def write_report(path: Path, rows: list[dict[str, str]]) -> None:
    active = [row for row in rows if row["archived"] != "true"]
    active_count = len(active)
    with_workflows = sum(1 for row in active if count_value(row["workflow_count"]) > 0)
    scheduled = sum(1 for row in active if count_value(row["scheduled_workflow_count"]) > 0)
    artifact = sum(1 for row in active if count_value(row["artifact_refresh_workflow_count"]) > 0)
    dependabot = sum(1 for row in active if yes(row["has_dependabot"]))
    codeql = sum(1 for row in active if yes(row["has_codeql"]))
    releases = sum(1 for row in active if count_value(row["release_count"]) > 0)
    warnings = [row for row in rows if row["fetch_warning"]]
    top_queue = sorted(
        active,
        key=lambda row: (
            int(row["workflow_health_score"]),
            -len([flag for flag in row["workflow_flags"].split("|") if flag]),
            row["repo"],
        ),
    )[:15]

    lines = [
        "# Workflow Health",
        "",
        "Read-only workflow/release reliability baseline for the `sanskrit-lexicon` organization.",
        "",
        "## Summary",
        "",
        f"- Active repositories: {active_count}",
        f"- Active repos with workflows: {with_workflows}/{active_count} ({pct(with_workflows, active_count)})",
        f"- Active repos with scheduled workflows: {scheduled}/{active_count} ({pct(scheduled, active_count)})",
        f"- Active repos with artifact/deploy/refresh workflows: {artifact}/{active_count} ({pct(artifact, active_count)})",
        f"- Active repos with Dependabot config: {dependabot}/{active_count} ({pct(dependabot, active_count)})",
        f"- Active repos with CodeQL signal: {codeql}/{active_count} ({pct(codeql, active_count)})",
        f"- Active repos with releases: {releases}/{active_count} ({pct(releases, active_count)})",
        f"- Rows with fetch warnings: {len(warnings)}",
        "",
        "## Lowest-Score Active Queue",
        "",
        "| Repo | Score | Workflows | Scheduled | Artifact/refresh | Dependabot | CodeQL | Releases | Flags |",
        "|---|---:|---:|---:|---:|---|---|---:|---|",
    ]
    for row in top_queue:
        lines.append(
            "| {repo} | {workflow_health_score} | {workflow_count} | "
            "{scheduled_workflow_count} | {artifact_refresh_workflow_count} | "
            "{has_dependabot} | {has_codeql} | {release_count} | {workflow_flags} |".format(**row)
        )

    lines.extend(
        [
            "",
            "## Caveats",
            "",
            "- This report does not mutate any repository.",
            "- `artifact_refresh_workflow_count` is keyword-based and should be treated as a queueing signal.",
            "- Scheduled workflow detection scans workflow YAML content for cron entries.",
            "- Dependabot, CodeQL, and release fields come from `repo_metadata.csv`.",
            "- Rows with fetch warnings are retained with explicit warning text rather than failing the whole run.",
            "",
            "Generated data: `observatory/site/src/data/workflow_health.csv`.",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def check_existing(args: argparse.Namespace) -> int:
    metadata_repos = {row["repo"] for row in read_csv(args.metadata)}
    if not args.out.exists():
        raise SystemExit(f"{args.out.relative_to(ROOT)} does not exist")
    rows = read_csv(args.out)
    with args.out.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames != FIELDS:
            raise SystemExit(f"workflow_health.csv schema mismatch: {reader.fieldnames}")
    row_repos = {row["repo"] for row in rows}
    if row_repos != metadata_repos:
        missing = sorted(metadata_repos - row_repos)
        extra = sorted(row_repos - metadata_repos)
        raise SystemExit(f"workflow_health.csv repo mismatch; missing={missing}; extra={extra}")
    for row in rows:
        int(row["workflow_health_score"])
        split_flags = [flag for flag in row["workflow_flags"].split("|") if flag]
        if row["workflow_count"] != "unknown":
            int(row["workflow_count"])
        if row["release_count"] != "unknown":
            int(row["release_count"])
        # A row whose data could not be fetched must advertise that with an
        # *-unknown flag. A fully-healthy repo can legitimately have zero flags
        # even with a benign fetch_warning (e.g. a cache-write failure), so key
        # the guard on actual unknown values rather than on fetch_warning.
        unknown_fields = [
            field for field in (
                "workflow_count", "active_workflow_count", "scheduled_workflow_count",
                "artifact_refresh_workflow_count", "has_dependabot", "has_codeql",
                "release_count",
            )
            if row[field] == "unknown"
        ]
        if unknown_fields and not split_flags:
            raise SystemExit(
                f"{row['repo']} has unknown fields {unknown_fields} but no workflow flags"
            )
    if not args.report.exists():
        raise SystemExit(f"{args.report.relative_to(ROOT)} does not exist")
    report_text = args.report.read_text(encoding="utf-8")
    if "Workflow Health" not in report_text or "Generated data:" not in report_text:
        raise SystemExit("workflow_health.md missing expected headings")
    warnings = sum(1 for row in rows if row["fetch_warning"])
    print(f"OK: workflow_health rows={len(rows)} warnings={warnings}")
    return 0


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--owner", default=OWNER, help="GitHub owner/org to query")
    parser.add_argument("--metadata", type=Path, default=METADATA_CSV, help="Input repo_metadata.csv path")
    parser.add_argument("--out", type=Path, default=OUT_CSV, help="CSV output path")
    parser.add_argument("--report", type=Path, default=OUT_REPORT, help="Markdown report output path")
    parser.add_argument("--repo", action="append", help="Limit to a repository name; repeatable")
    parser.add_argument("--offline", action="store_true", help="Do not call GitHub; preserve unknown workflow details")
    parser.add_argument("--cache-dir", type=Path, default=DEFAULT_CACHE_DIR, help="Raw GitHub response cache directory")
    parser.add_argument("--refresh-cache", action="store_true", help="Ignore cache and refresh through gh api")
    parser.add_argument("--check", action="store_true", help="Validate existing workflow CSV/report without rewriting")
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    if args.check:
        return check_existing(args)
    rows = build_rows(args)
    write_rows(args.out, rows)
    write_report(args.report, rows)
    warnings = sum(1 for row in rows if row["fetch_warning"])
    print(f"wrote {args.out}")
    print(f"wrote {args.report}")
    print(f"  repos: {len(rows)}")
    print(f"  rows with warnings: {warnings}")
    if args.offline:
        print("  mode: offline")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
