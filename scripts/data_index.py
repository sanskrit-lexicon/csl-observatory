#!/usr/bin/env python3
"""Build the public Observable data-file catalog."""

from __future__ import annotations

import argparse
import csv
import io
import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "observatory" / "site" / "src" / "data"
OUT = DATA_DIR / "data_index.csv"


@dataclass(frozen=True)
class Entry:
    category: str
    source_script: str
    description: str
    caveat: str


CATALOG: dict[str, Entry] = {
    "bus_factor.csv": Entry(
        "sustainability",
        "scripts/bus_factor.py",
        "Repository-level contributor concentration and bus-factor indicators.",
        "Computed from committed contributor snapshots; merged identities depend on the maintainer-reviewed map.",
    ),
    "commits.csv": Entry(
        "github snapshot",
        "observatory/fetch.py; observatory/transform.py",
        "Slim commit snapshot by repository, SHA, date, author, and subject.",
        "Author names/emails reflect Git metadata in the snapshot and should not be treated as a curated identity authority.",
    ),
    "contributor_identity.csv": Entry(
        "sustainability",
        "scripts/contributor_identity.py",
        "Maintainer-reviewed contributor identity and ORCID readiness summary.",
        "Identity fields are conservative; unknown or unconfirmed identities remain unresolved until the maintainer confirms them.",
    ),
    "contributors.csv": Entry(
        "github snapshot",
        "observatory/fetch.py; observatory/transform.py",
        "Repository/login contribution counts from the GitHub snapshot.",
        "Counts are GitHub contribution signals, not a complete scholarly credit model.",
    ),
    "correction_events.csv": Entry(
        "obs-t",
        "scripts/build_correction_events.py",
        "Base OBS-T correction-event table before later component and release enrichments.",
        "Intermediate research artifact; cite the release table for stable OBS-T reuse.",
    ),
    "correction_events.meta.json": Entry(
        "obs-t",
        "scripts/build_correction_events.py",
        "Metadata sidecar for the base OBS-T correction-event table.",
        "Sidecar describes the local generated artifact and should be read with the matching CSV.",
    ),
    "correction_events_all.csv": Entry(
        "obs-t",
        "scripts/build_correction_events.py",
        "Combined OBS-T event table across form and git-derived correction layers.",
        "Intermediate aggregate; use the release CSV for the citable public dataset.",
    ),
    "correction_events_final.csv": Entry(
        "obs-t",
        "scripts/obs_t_release.py",
        "Final typed OBS-T event table before release split annotation.",
        "Intermediate artifact retained for auditability; release-specific consumers should use correction_events_release.csv.",
    ),
    "correction_events_final.meta.json": Entry(
        "obs-t",
        "scripts/obs_t_release.py",
        "Metadata sidecar for correction_events_final.csv.",
        "Sidecar describes the generated final table and should be read with the matching CSV.",
    ),
    "correction_events_git.csv": Entry(
        "obs-t",
        "scripts/reconstruct_git_events.py",
        "Git-derived OBS-T correction events mined from dictionary entry files.",
        "Git reconstruction is conservative and should be audited through source_path and commit_sha.",
    ),
    "correction_events_git.meta.json": Entry(
        "obs-t",
        "scripts/reconstruct_git_events.py",
        "Metadata sidecar for git-derived OBS-T correction events.",
        "Sidecar reports reconstruction scope and hunk accounting for the matching CSV.",
    ),
    "correction_events_release.csv": Entry(
        "obs-t release",
        "scripts/obs_t_release.py",
        "Citable OBS-T release table with typed correction events and split labels.",
        "Released identity fields use the repository identity policy; raw private contact data is not a release interface.",
    ),
    "correction_events_release.meta.json": Entry(
        "obs-t release",
        "scripts/obs_t_release.py",
        "Metadata sidecar for the citable OBS-T release table.",
        "Read with correction_events_release.csv for schema, counts, and release caveats.",
    ),
    "correction_events_typed.csv": Entry(
        "obs-t",
        "scripts/attribute_components.py",
        "OBS-T correction events with component and attribution-route annotations.",
        "Intermediate table; component attribution includes conservative and fuzzy routes that require caveat-aware interpretation.",
    ),
    "correction_events_typed.meta.json": Entry(
        "obs-t",
        "scripts/attribute_components.py",
        "Metadata sidecar for correction_events_typed.csv.",
        "Sidecar includes attribution-route counts and should be read with the matching CSV.",
    ),
    "pwg_citation_coverage.json": Entry(
        "citation coverage",
        "PWG repo pwg_ls/pwg_ru_coverage (imported summary)",
        "Summary of PWG <ls> citation link coverage: scan vs HTML targets over the translated article subset.",
        "Derived in the PWG repo, not regenerated here; see reports/pwg_citation_coverage.md for the live sources.",
    ),
    "error_recapture.csv": Entry(
        "obs-t recapture",
        "scripts/error_recapture.py",
        "Chapman capture-recapture estimates of error-prone records remaining per dictionary, from two-era overlap.",
        "Order-of-magnitude only: sequential occasions and heterogeneous catchability violate Chapman assumptions in opposite directions; estimates capped at record counts.",
    ),
    "external_reach.csv": Entry(
        "external reach",
        "scripts/external_reach.py",
        "Scholar-framed external reach: GitHub stars/forks, 14-day clone/view traffic for core repos, downstream dependents (known consumers + code-search hits), and representative citations, in one tidy long table.",
        "Mixed measured/estimated: traffic is a sliding 14-day sample of core repos (not all 76); dependents from code search are a floor; citations are representative, not exhaustive. Zenodo tier is blocked pending a DOI correction.",
    ),
    "issue_lifecycle_survival.csv": Entry(
        "issue lifecycle",
        "scripts/issue_lifecycle.py",
        "Cohort survival: % of each opening-year cohort still open after 30/90/180/365/730/1460 days.",
        "Right-censored: a cohort only reports horizons its issues have had time to reach at the snapshot date.",
    ),
    "issue_lifecycle_backlog.csv": Entry(
        "issue lifecycle",
        "scripts/issue_lifecycle.py",
        "Backlog age pyramid: currently-open issues bucketed by age, with silent (zero-comment) counts.",
        "Ages are computed at the snapshot as-of date, not at page-view time.",
    ),
    "issue_lifecycle_close.csv": Entry(
        "issue lifecycle",
        "scripts/issue_lifecycle.py",
        "Time-to-close percentiles (median/p25/p75/p90) per closing year, issues and PRs separately.",
        "Closed-at is GitHub close time; PRs are few (89 total) so annual PR rows are small samples.",
    ),
    "issue_lifecycle_repo.csv": Entry(
        "issue lifecycle",
        "scripts/issue_lifecycle.py",
        "Per-repository responsiveness: open/closed counts, close-latency percentiles, open-age median, silent-open count.",
        "Latency percentiles are blank for repos with fewer than 20 closed issues.",
    ),
    "issue_typology_annual.csv": Entry(
        "issue taxonomy",
        "observatory/transform.py",
        "Annual issue counts by taxonomy/type label.",
        "Labels reflect the current taxonomy snapshot; historical issue labels may have been normalized after the fact.",
    ),
    "issues.csv": Entry(
        "github snapshot",
        "observatory/fetch.py; observatory/transform.py",
        "Slim issue and pull-request snapshot used by issue and taxonomy dashboards.",
        "Labels are pipe-separated and may combine type, severity, workflow, and legacy labels.",
    ),
    "manifest.json": Entry(
        "github snapshot",
        "observatory/transform.py",
        "Snapshot manifest with data row counts and the current observatory snapshot date.",
        "Counts describe the committed transformed files; rerun the refresh pipeline before citing newer live GitHub state.",
    ),
    "obs_q_annual.csv": Entry(
        "correction sustainability",
        "scripts/obs_q_correction.py",
        "Annual correction-sustainability aggregates by commits, correctors, and leading contributor share.",
        "Probe-level OBS-Q artifact; it summarizes process signals, not dictionary-content quality.",
    ),
    "obs_q_latency.csv": Entry(
        "correction sustainability",
        "scripts/obs_q_correction.py",
        "Correction issue open/close latency inputs.",
        "Latency depends on GitHub issue closure practice and may not equal actual correction deployment time.",
    ),
    "obs_q_per_dict.csv": Entry(
        "correction sustainability",
        "scripts/obs_q_correction.py",
        "Per-dictionary correction-sustainability aggregates.",
        "Dictionary-level process signal; small dictionaries and burst campaigns can dominate rates.",
    ),
    "obs_t_baselines.json": Entry(
        "obs-t analysis",
        "scripts/obs_t_baselines.py",
        "OBS-T baseline model metrics for detection, correction, and location classification.",
        "Baseline metrics are descriptive and depend on the current release split and feature set.",
    ),
    "obs_t_campaigns.csv": Entry(
        "obs-t analysis",
        "scripts/obs_t_campaigns.py",
        "Documented OBS-T correction campaigns by date, magnitude, category, and dictionaries.",
        "Campaign detection is rule-based and intended for context, not as a complete editorial history.",
    ),
    "obs_t_component.csv": Entry(
        "obs-t analysis",
        "scripts/obs_t_typology.py",
        "OBS-T component counts by layer and dictionary.",
        "Component labels are typology abstractions and should be interpreted with the datasheet.",
    ),
    "obs_t_confusion.csv": Entry(
        "obs-t analysis",
        "scripts/obs_t_typology.py",
        "OBS-T edit confusion counts by changed unit, layer, and edit space.",
        "Raw source-space edits are separated from Sanskrit-bearing edit spaces where possible.",
    ),
    "obs_t_corrector.csv": Entry(
        "obs-t analysis",
        "scripts/obs_t_typology.py",
        "OBS-T release-safe corrector summary by alias/name, event count, component, and date span.",
        "Identity display follows the release identity policy and should not be used to deanonymize contributors.",
    ),
    "obs_t_crosswalk.csv": Entry(
        "obs-t analysis",
        "scripts/obs_t_typology.py",
        "Crosswalk counts from OBS-T components into external classification schemes.",
        "Crosswalks are approximate mappings for comparison, not replacement labels.",
    ),
    "obs_t_dict.csv": Entry(
        "obs-t analysis",
        "scripts/obs_t_typology.py",
        "Dictionary-level OBS-T event density and dominant component summary.",
        "Entry denominators and event density are best used for comparison, not ranking dictionary quality.",
    ),
    "obs_t_rigor.json": Entry(
        "obs-t analysis",
        "scripts/obs_t_rigor.py",
        "OBS-T hypothesis statistics, effect sizes, bootstrap checks, and trend summaries.",
        "Statistical tests are descriptive for the generated corpus and should be cited with limitations.",
    ),
    "obs_t_robustness.json": Entry(
        "obs-t analysis",
        "scripts/obs_t_robustness.py",
        "OBS-T robustness and sensitivity checks.",
        "Sensitivity outputs are diagnostic and should be read with the main rigor report.",
    ),
    "obs_t_silver.json": Entry(
        "obs-t analysis",
        "scripts/obs_t_silver.py",
        "OBS-T silver-validation summary.",
        "Silver validation is automated and does not replace the human-gated gold/error samples.",
    ),
    "obs_t_summary.json": Entry(
        "obs-t analysis",
        "scripts/obs_t_typology.py",
        "OBS-T headline counts and distribution summaries used by the site.",
        "Summary is derived from the current generated tables and changes when the release pipeline is rerun.",
    ),
    "obs_t_timeline.csv": Entry(
        "obs-t analysis",
        "scripts/obs_t_typology.py",
        "Annual OBS-T event counts by layer and component.",
        "Timeline reflects event dates available in source layers and documented campaigns.",
    ),
    "obs_t_timeline_monthly.csv": Entry(
        "obs-t analysis",
        "scripts/obs_t_typology.py",
        "Monthly OBS-T event counts by component.",
        "Month-level trends are sensitive to large campaigns and should be filtered by component/layer where relevant.",
    ),
    "obs_t_translit.json": Entry(
        "obs-t analysis",
        "scripts/obs_t_translit_check.py",
        "OBS-T transliteration validation and sensitivity summary.",
        "Validation compares conventions and includes known sibilant/convention ambiguity caveats.",
    ),
    "people_summary.csv": Entry(
        "github snapshot",
        "observatory/build_people.py",
        "Curated people summary used by contributor dashboards.",
        "ORCID and identity fields depend on maintainer review and contributor consent.",
    ),
    "repo_health.csv": Entry(
        "repository health",
        "scripts/repo_health.py",
        "Repository health flags for license, branch, activity, description, and cleanup risk.",
        "Repository-health flags are decision support; external repo changes still require maintainer approval.",
    ),
    "repo_metadata.csv": Entry(
        "repository metadata",
        "scripts/repo_metadata_snapshot.py",
        "Repository metadata-completeness snapshot for README, citation, templates, workflows, releases, Dependabot, and CodeQL.",
        "Live fields depend on GitHub API access; check fetch_warning and unknown flags after each refresh.",
    ),
    "repos.csv": Entry(
        "github snapshot",
        "observatory/fetch.py; observatory/transform.py",
        "Repository inventory with description, language, size, dates, branch, license, and archive state.",
        "Snapshot excludes external facts not exposed by GitHub repository metadata.",
    ),
    "taxonomy_adoption.csv": Entry(
        "issue taxonomy",
        "scripts/taxonomy_adoption.py",
        "Annual taxonomy adoption metrics: typed, one-type, severity, milestone, and conformance rates.",
        "Conformance is measured against the current taxonomy rules and may change as labels are cleaned.",
    ),
    "timeseries_annual.csv": Entry(
        "activity",
        "observatory/transform.py",
        "Annual repository activity aggregates for issues, pull requests, commits, and authors.",
        "Aggregates come from the committed GitHub snapshot and inherit its refresh date.",
    ),
    "timeseries_monthly.csv": Entry(
        "activity",
        "observatory/transform.py",
        "Monthly repository activity aggregates for issues, pull requests, commits, and authors.",
        "Monthly buckets support operational trends and should not be over-read for inactive or archived repos.",
    ),
    "velocity_timeline.csv": Entry(
        "activity",
        "scripts/velocity_timeline.py",
        "Organization-level yearly velocity and backlog summary.",
        "Backlog is based on issue open/close state in the snapshot and can change after label/issue cleanup.",
    ),
    "workflow_health.csv": Entry(
        "workflow reliability",
        "scripts/workflow_health.py",
        "Repository workflow/release reliability baseline covering workflows, scheduled jobs, artifact refresh, Dependabot, CodeQL, and releases.",
        "Workflow classification is read-only and keyword-based for artifact/deploy/refresh categories; fetch warnings should be reviewed before citing.",
    ),
    "data_index.csv": Entry(
        "catalog",
        "scripts/data_index.py",
        "Catalog of public CSV/JSON data files with source scripts, generated dates, and caveats.",
        "Generated from tracked public data files; use it as the site index, not as a data source for analysis.",
    ),
}


FIELDNAMES = [
    "file",
    "format",
    "category",
    "bytes",
    "rows",
    "generated_date",
    "source_script",
    "description",
    "caveat",
]


def public_data_files() -> list[Path]:
    return sorted(
        path
        for path in DATA_DIR.iterdir()
        if path.is_file() and path.suffix.lower() in {".csv", ".json"}
    )


def csv_rows(path: Path) -> str:
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.reader(handle)
        try:
            next(reader)
        except StopIteration:
            return "0"
        return str(sum(1 for _ in reader))


def json_rows(path: Path) -> str:
    with path.open(encoding="utf-8") as handle:
        data = json.load(handle)
    if isinstance(data, list):
        return str(len(data))
    return ""


def generated_date(path: Path) -> str:
    return datetime.fromtimestamp(path.stat().st_mtime, timezone.utc).date().isoformat()


def row_for(path: Path, entry: Entry, *, rows: str | None = None, size: int | None = None) -> dict[str, str]:
    if path.suffix.lower() == ".csv":
        row_count = csv_rows(path) if rows is None else rows
        fmt = "csv"
    else:
        row_count = json_rows(path) if rows is None else rows
        fmt = "json"
    return {
        "file": path.name,
        "format": fmt,
        "category": entry.category,
        "bytes": str(path.stat().st_size if size is None else size),
        "rows": row_count,
        "generated_date": generated_date(path),
        "source_script": entry.source_script,
        "description": entry.description,
        "caveat": entry.caveat,
    }


def serialize(rows: list[dict[str, str]]) -> str:
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=FIELDNAMES, lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    return output.getvalue()


def build_rows() -> list[dict[str, str]]:
    files = [path for path in public_data_files() if path.name != OUT.name]
    rows = [row_for(path, CATALOG[path.name]) for path in files]

    index_entry = CATALOG[OUT.name]
    index_date = max(
        (row["generated_date"] for row in rows),
        default=datetime.now(timezone.utc).date().isoformat(),
    )
    index_row = {
        "file": OUT.name,
        "format": "csv",
        "category": index_entry.category,
        "bytes": "0",
        "rows": str(len(rows) + 1),
        "generated_date": index_date,
        "source_script": index_entry.source_script,
        "description": index_entry.description,
        "caveat": index_entry.caveat,
    }
    rows.append(index_row)

    for _ in range(8):
        text = serialize(sorted(rows, key=lambda row: row["file"]))
        size = len(text.encode("utf-8"))
        if index_row["bytes"] == str(size):
            break
        index_row["bytes"] = str(size)
    return sorted(rows, key=lambda row: row["file"])


def validate_catalog() -> None:
    actual = {path.name for path in public_data_files()}
    cataloged = set(CATALOG)
    missing = sorted(actual - cataloged)
    stale = sorted(name for name in cataloged - actual if name != OUT.name)
    if missing or stale:
        messages = []
        if missing:
            messages.append("missing catalog entries: " + ", ".join(missing))
        if stale:
            messages.append("catalog entries without public files: " + ", ".join(stale))
        raise SystemExit("; ".join(messages))


def check_existing(rows: list[dict[str, str]]) -> None:
    if not OUT.exists():
        raise SystemExit(f"{OUT.relative_to(ROOT)} does not exist")
    with OUT.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        existing = list(reader)
        fieldnames = reader.fieldnames
    # Validate the header first: a drifted/missing "file" column otherwise makes
    # the row["file"] comprehensions below KeyError instead of reporting drift.
    if fieldnames != FIELDNAMES:
        raise SystemExit(f"data_index.csv schema mismatch: {fieldnames}")
    actual_files = {row["file"] for row in existing}
    expected_files = {row["file"] for row in rows}
    if actual_files != expected_files:
        missing = sorted(expected_files - actual_files)
        extra = sorted(actual_files - expected_files)
        raise SystemExit(f"data_index.csv file mismatch; missing={missing}; extra={extra}")
    # Validate the content-derived columns (stable across checkouts); skip
    # generated_date, which tracks file mtime and changes on a fresh clone.
    existing_by_file = {row["file"]: row for row in existing}
    drift = []
    for expected in rows:
        got = existing_by_file[expected["file"]]
        for col in ("bytes", "rows"):
            if got.get(col) != expected[col]:
                drift.append(f"{expected['file']}.{col}: expected {expected[col]}, found {got.get(col)}")
    if drift:
        raise SystemExit("data_index.csv content drift; rerun scripts/data_index.py: " + "; ".join(drift))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Validate catalog coverage without rewriting output")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    validate_catalog()
    rows = build_rows()
    if args.check:
        check_existing(rows)
        print(f"OK: {len(rows)} public data files cataloged")
        return 0
    OUT.write_text(serialize(rows), encoding="utf-8")
    print(f"wrote {OUT.relative_to(ROOT)} ({len(rows)} rows)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
