#!/usr/bin/env python3
"""Run the csl-observatory refresh pipeline with a manifest.

The default run refreshes local report/data artifacts, including read-only
GitHub metadata/workflow snapshots through ``gh api``. Use the explicit offline
flags when credentials are unavailable or a placeholder refresh is intentional.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "observatory" / "site"
DEFAULT_MANIFEST = ROOT / "reports" / "refresh_observatory_manifest.json"
DEFAULT_SUMMARY = ROOT / "reports" / "refresh_observatory_summary.md"
NPM = "npm.cmd" if os.name == "nt" else "npm"


@dataclass(frozen=True)
class Phase:
    name: str
    command: list[str]
    cwd: Path = ROOT
    check_only: bool = False


def base_phases(args: argparse.Namespace) -> list[Phase]:
    metadata_command = [
        sys.executable,
        "scripts/repo_metadata_snapshot.py",
        "--out",
        "observatory/site/src/data/repo_metadata.csv",
    ]
    if args.offline_metadata:
        metadata_command.insert(2, "--offline")
    workflow_command = [sys.executable, "scripts/workflow_health.py"]
    if args.offline_workflows:
        workflow_command.insert(2, "--offline")

    phases = [
        Phase("bus-factor", [sys.executable, "scripts/bus_factor.py"]),
        Phase("repo-health", [sys.executable, "scripts/repo_health.py"]),
        Phase("taxonomy-adoption", [sys.executable, "scripts/taxonomy_adoption.py"]),
        Phase("velocity-timeline", [sys.executable, "scripts/velocity_timeline.py"]),
        Phase("contributor-identity", [sys.executable, "scripts/contributor_identity.py"]),
        Phase("repo-metadata", metadata_command),
        Phase("workflow-health", workflow_command),
        Phase("data-index", [sys.executable, "scripts/data_index.py"]),
        Phase("repo-metadata-check",
              [sys.executable, "scripts/repo_metadata_snapshot.py", "--check",
               "--out", "observatory/site/src/data/repo_metadata.csv"], check_only=True),
        Phase("workflow-health-check", [sys.executable, "scripts/workflow_health.py", "--check"], check_only=True),
        Phase("data-index-check", [sys.executable, "scripts/data_index.py", "--check"], check_only=True),
        Phase("repo-health-regression", [sys.executable, "scripts/repo_health_regression.py"], check_only=True),
        Phase("obs-t-regression", [sys.executable, "scripts/obs_t_regression.py"], check_only=True),
        Phase("site-visualization-smoke", [sys.executable, "scripts/site_visualization_smoke.py"], check_only=True),
    ]
    if not args.skip_site_build:
        phases.append(Phase("site-build", [NPM, "run", "build"], cwd=SITE, check_only=True))
    return phases


def run_text(command: list[str], cwd: Path = ROOT) -> tuple[int, str]:
    try:
        result = subprocess.run(
            command,
            cwd=cwd,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            check=False,
        )
    except OSError as exc:
        return 127, f"failed to start command: {exc}\n"
    return result.returncode, result.stdout


def git_status() -> list[str]:
    code, output = run_text(["git", "status", "--short"])
    if code != 0:
        return [f"git status failed: {output.strip()}"]
    return output.splitlines()


def select_phases(phases: list[Phase], args: argparse.Namespace) -> list[Phase]:
    by_name = {phase.name: phase for phase in phases}
    if args.list_phases:
        for phase in phases:
            print(phase.name)
        raise SystemExit(0)
    if args.phase:
        missing = [name for name in args.phase if name not in by_name]
        if missing:
            raise SystemExit(f"unknown phase(s): {', '.join(missing)}")
        phases = [by_name[name] for name in args.phase]
    if args.check_only:
        phases = [phase for phase in phases if phase.check_only]
    if args.stop_after:
        names = [phase.name for phase in phases]
        if args.stop_after not in names:
            raise SystemExit(f"--stop-after must name a selected phase: {args.stop_after}")
        phases = phases[: names.index(args.stop_after) + 1]
    if not phases:
        # e.g. `--phase <writer> --check-only`: the check-only filter removes the
        # named writer phase, leaving nothing. Fail loudly instead of reporting
        # success on a run that executed zero phases.
        raise SystemExit(
            "no phases selected; check the --phase / --check-only combination"
        )
    return phases


def command_display(phase: Phase) -> str:
    prefix = "" if phase.cwd == ROOT else f"(cd {phase.cwd.relative_to(ROOT)} && "
    suffix = "" if phase.cwd == ROOT else ")"
    return prefix + " ".join(phase.command) + suffix


def write_manifest(path: Path, manifest: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def write_summary(path: Path, manifest: dict[str, object]) -> None:
    lines = [
        "# Observatory Refresh Summary",
        "",
        f"Generated: {manifest['generated_at']}",
        f"Mode: {manifest['mode']}",
        f"Metadata mode: {manifest['metadata_mode']}",
        f"Workflow mode: {manifest['workflow_mode']}",
        f"Overall status: {manifest['status']}",
        "",
        "## Phases",
        "",
        "| Phase | Status | Seconds | Command |",
        "|---|---:|---:|---|",
    ]
    for phase in manifest["phases"]:
        lines.append(
            f"| {phase['name']} | {phase['status']} | {phase['seconds']:.2f} | `{phase['command']}` |"
        )
    lines.extend(
        [
            "",
            "## Git Status Delta",
            "",
            f"- Before: {len(manifest['git_status_before'])} changed entries.",
            f"- After: {len(manifest['git_status_after'])} changed entries.",
            "",
            "Review `refresh_observatory_manifest.json` for full command output.",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def run_pipeline(args: argparse.Namespace) -> int:
    phases = select_phases(base_phases(args), args)
    if args.dry_run:
        print("Refresh plan:")
        for phase in phases:
            print(f"- {phase.name}: {command_display(phase)}")
        return 0
    manifest_path = args.manifest
    summary_path = args.summary
    if not args.check_only:
        manifest_path = manifest_path or DEFAULT_MANIFEST
        summary_path = summary_path or DEFAULT_SUMMARY

    manifest: dict[str, object] = {
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "mode": "check-only" if args.check_only else "refresh",
        "metadata_mode": "offline" if args.offline_metadata else "live",
        "workflow_mode": "offline" if args.offline_workflows else "live",
        "status": "running",
        "git_status_before": git_status(),
        "git_status_after": [],
        "phases": [],
    }

    overall_status = "success"
    for phase in phases:
        started = time.monotonic()
        code, output = run_text(phase.command, phase.cwd)
        seconds = time.monotonic() - started
        status = "success" if code == 0 else "failed"
        manifest["phases"].append(
            {
                "name": phase.name,
                "command": command_display(phase),
                "cwd": str(phase.cwd.relative_to(ROOT) if phase.cwd != ROOT else "."),
                "returncode": code,
                "status": status,
                "seconds": seconds,
                "output": output,
            }
        )
        print(f"[{status}] {phase.name} ({seconds:.1f}s)")
        if code != 0:
            overall_status = "failed"
            if not args.keep_going:
                break

    manifest["status"] = overall_status
    manifest["git_status_after"] = git_status()
    if manifest_path is not None:
        write_manifest(manifest_path, manifest)
        print(f"manifest: {manifest_path}")
    if summary_path is not None:
        write_summary(summary_path, manifest)
        print(f"summary: {summary_path}")
    if overall_status == "failed" and args.check_only:
        print(
            "note: --check-only validates committed artifacts without rebuilding "
            "them; a failure here often means a stale artifact (e.g. repos.csv "
            "changed) rather than a code regression — rerun the matching writer phase."
        )
    return 0 if overall_status == "success" else 1


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true", help="Print selected phases without running them")
    parser.add_argument("--check-only", action="store_true", help="Run only read-only checks and site build")
    parser.add_argument("--live-metadata", action="store_true", help="Deprecated compatibility flag; live metadata is now the default")
    parser.add_argument("--offline-metadata", action="store_true", help="Write repo_metadata.csv in placeholder/unknown offline mode")
    parser.add_argument("--offline-workflows", action="store_true", help="Write workflow_health.csv with unknown live-only workflow details")
    parser.add_argument("--skip-site-build", action="store_true", help="Skip npm run build")
    parser.add_argument("--keep-going", action="store_true", help="Continue after a failed phase")
    parser.add_argument("--phase", action="append", help="Run only a named phase; repeatable")
    parser.add_argument("--stop-after", help="Stop after the named selected phase")
    parser.add_argument("--list-phases", action="store_true", help="Print phase names and exit")
    parser.add_argument(
        "--manifest",
        type=Path,
        default=None,
        help="JSON manifest output path; defaults to reports/refresh_observatory_manifest.json in refresh mode only",
    )
    parser.add_argument(
        "--summary",
        type=Path,
        default=None,
        help="Markdown summary output path; defaults to reports/refresh_observatory_summary.md in refresh mode only",
    )
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    return run_pipeline(parse_args(argv))


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
