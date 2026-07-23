#!/usr/bin/env python3
"""Smoke checks for maintainer Observable visualisation pages."""

from __future__ import annotations

import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "observatory" / "site"
SRC = SITE / "src"
DIST = SITE / "dist"

PAGES = [
    "ops-command",
    "repository-risk",
    "metadata-readiness",
    "taxonomy-triage",
    "community-continuity",
    "obs-t-maintenance",
    "correction-anatomy",
    "org-shape",
    "pos-by-text",
    "paradigm-cell-coverage",
    "sense-polysemy",
]


def fail(message: str) -> None:
    raise SystemExit(f"ERROR: {message}")


def main() -> int:
    total_plots = 0
    for page in PAGES:
        source = SRC / f"{page}.md"
        if not source.exists():
            fail(f"missing page {source}")
        text = source.read_text(encoding="utf-8")
        plot_count = len(re.findall(r"\bPlot\.plot\s*\(", text))
        if plot_count < 5:
            fail(f"{page} has {plot_count} Plot.plot calls, expected at least 5")
        total_plots += plot_count

        rendered = DIST / f"{page}.html"
        if rendered.exists():
            rendered_plot_count = rendered.read_text(encoding="utf-8").count("Plot.plot")
            if rendered_plot_count < 5:
                fail(
                    f"{page} has {rendered_plot_count} Plot.plot definitions in dist, "
                    "expected at least 5"
                )

    if total_plots < 25:
        fail(f"new visualisation pages have {total_plots} Plot.plot calls, expected at least 25")

    config = (SITE / "observablehq.config.js").read_text(encoding="utf-8")
    for page in PAGES:
        if f'path: "/{page}"' not in config:
            fail(f"missing navigation entry for /{page}")

    coverage = (SRC / "coverage.md").read_text(encoding="utf-8")
    if "d.labels.split" in coverage or "labels.split" in coverage:
        fail("coverage.md still calls labels.split directly")

    print(f"OK: {len(PAGES)} maintainer pages, {total_plots} Plot.plot calls")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
