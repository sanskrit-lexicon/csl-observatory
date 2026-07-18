#!/usr/bin/env python3
"""Build the immutable evidence bundle for history paper A61.

The bundle deliberately keeps unlike populations separate.  A GitHub account,
an OBS-T corrector label, and a historically attested person are not the same
unit and must never be collapsed into one headline "contributors" count.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import subprocess
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "publication" / "a61-history-v1.0"
SITE_DATA = ROOT / "observatory" / "site" / "src" / "data"

INPUTS = [
    Path("data/manifest.json"),
    Path("data/summary.json"),
    Path("observatory/site/src/data/obs_t_summary.json"),
    Path("observatory/site/src/data/obs_q_annual.csv"),
    Path("observatory/site/src/data/bus_factor.csv"),
    Path("observatory/site/src/data/contributor_identity.csv"),
    Path("observatory/site/src/data/stats_census_register.csv"),
]


def read_json(rel: str) -> object:
    return json.loads((ROOT / rel).read_text(encoding="utf-8"))


def read_csv(rel: str) -> list[dict[str, str]]:
    with (ROOT / rel).open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def csv_text(rows: list[dict[str, object]], fields: list[str]) -> str:
    stream = io.StringIO()
    writer = csv.DictWriter(stream, fieldnames=fields, lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    return stream.getvalue()


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def git_source_base() -> str:
    result = subprocess.run(
        ["git", "rev-parse", "origin/main"], cwd=ROOT, capture_output=True,
        text=True, encoding="utf-8", check=True,
    )
    return result.stdout.strip()


def census_value(rows: list[dict[str, str]], statistic: str) -> dict[str, str]:
    matches = [row for row in rows if row["statistic"] == statistic]
    if len(matches) != 1:
        raise SystemExit(f"expected one stats-census row for {statistic!r}; got {len(matches)}")
    return matches[0]


def build() -> dict[str, str]:
    manifest = read_json("data/manifest.json")
    legacy = read_json("data/summary.json")
    obs_t = read_json("observatory/site/src/data/obs_t_summary.json")
    obs_q = read_csv("observatory/site/src/data/obs_q_annual.csv")
    bus = read_csv("observatory/site/src/data/bus_factor.csv")
    identities = read_csv("observatory/site/src/data/contributor_identity.csv")
    census = read_csv("observatory/site/src/data/stats_census_register.csv")

    humans = [row for row in identities if row["status"] != "bot"]
    bf1 = [row for row in bus if row["bus_factor"] == "1"]
    max_correctors = max(int(row["correctors"]) for row in obs_q)
    lead_shares = [float(row["lead_share"]) for row in obs_q]

    dictionaries = census_value(census, "Dictionaries digitized")
    union = census_value(census, "Union headwords (15-dict)")
    markup = census_value(census, "Markup-tag frequency census")
    citations = census_value(census, "<ls> citation-frequency graph")

    metrics: list[dict[str, object]] = [
        {"metric_id": "ORG-REPOS-API", "value": legacy["repos_count"], "unit": "repositories", "population": "repositories returned by the legacy June 2026 GitHub organisation snapshot", "as_of": legacy["snapshot_date"], "source": "data/summary.json", "status": "verified", "caveat": "Not the same population as transformed activity tables."},
        {"metric_id": "ORG-REPOS-TRANSFORMED", "value": manifest["files"]["repos.csv"], "unit": "repositories", "population": "repositories represented in the transformed June 2026 activity tables", "as_of": manifest["snapshot_date"], "source": "data/manifest.json", "status": "verified", "caveat": "Use for denominators derived from data/repos.csv."},
        {"metric_id": "ORG-ISSUE-PR-ROWS", "value": manifest["files"]["issues.csv"], "unit": "issue-or-pull-request rows", "population": "transformed GitHub issue and pull-request records", "as_of": manifest["snapshot_date"], "source": "data/manifest.json", "status": "verified", "caveat": "A record count, not the sum of the legacy summary's separately fetched totals."},
        {"metric_id": "ORG-HUMAN-COMMIT-IDS", "value": len(humans), "unit": "normalized Git identities", "population": "non-bot logins in the committed contributor snapshot after maintainer-reviewed bot overrides", "as_of": manifest["snapshot_date"], "source": "observatory/site/src/data/contributor_identity.csv", "status": "verified", "caveat": "Git identities are neither all historical participants nor OBS-T correction submitters."},
        {"metric_id": "ORG-BF1-REPOS", "value": len(bf1), "unit": "repositories", "population": f"repositories with bus factor 1 among {len(bus)} repositories with human contribution rows", "as_of": manifest["snapshot_date"], "source": "observatory/site/src/data/bus_factor.csv", "status": "verified", "caveat": "GitHub contribution counts; automation excluded through the curated identity map."},
        {"metric_id": "OBST-EVENTS", "value": obs_t["events"], "unit": "correction events", "population": "OBS-T form and git layers", "as_of": obs_t["dateRange"][1], "source": "observatory/site/src/data/obs_t_summary.json", "status": "verified", "caveat": "Documented events, not an exhaustive history of every edit."},
        {"metric_id": "OBST-DICTIONARIES", "value": obs_t["dictionaries"], "unit": "dictionaries", "population": "dictionaries represented in OBS-T", "as_of": obs_t["dateRange"][1], "source": "observatory/site/src/data/obs_t_summary.json", "status": "verified", "caveat": "One fewer than the current collection inventory."},
        {"metric_id": "OBST-CORRECTOR-IDS", "value": obs_t["correctors"], "unit": "corrector labels", "population": "distinct release-safe corrector identities/labels in OBS-T", "as_of": obs_t["dateRange"][1], "source": "observatory/site/src/data/obs_t_summary.json", "status": "verified", "caveat": "Do not describe these labels as 208 people without identity adjudication."},
        {"metric_id": "OBST-DERIVED-PCT", "value": obs_t["derivedPct"], "unit": "percent", "population": "OBS-T events whose component was derived rather than left inferred/unattributed", "as_of": obs_t["dateRange"][1], "source": "observatory/site/src/data/obs_t_summary.json", "status": "verified", "caveat": "A provenance proportion, not an accuracy score."},
        {"metric_id": "OBSQ-MAX-ANNUAL-CORRECTORS", "value": max_correctors, "unit": "correctors per year", "population": "content-correction commit authors in csl-orig, 2019–2026", "as_of": max(row["year"] for row in obs_q), "source": "observatory/site/src/data/obs_q_annual.csv", "status": "verified", "caveat": "Measures implementers in git history, not form-era submitters."},
        {"metric_id": "OBSQ-LEAD-SHARE-RANGE", "value": f"{min(lead_shares)*100:.0f}–{max(lead_shares)*100:.0f}", "unit": "percent", "population": "annual lead corrector share of csl-orig content-correction commits, 2019–2026", "as_of": max(row["year"] for row in obs_q), "source": "observatory/site/src/data/obs_q_annual.csv", "status": "verified", "caveat": "Annual concentration range; not a share of all project labour."},
        {"metric_id": "CDSL-DICTIONARIES", "value": dictionaries["value_numeric"], "unit": "dictionary/reference works", "population": "current CDSL collection inventory", "as_of": dictionaries["as_of_date"], "source": dictionaries["source_url"], "status": dictionaries["status"], "caveat": "Collection count includes reference works; OBS-T covers 43."},
        {"metric_id": "CDSL-UNION-HW", "value": union["value_numeric"], "unit": "normalized headwords", "population": "union over the fifteen-dictionary comparison set", "as_of": union["as_of_date"], "source": union["source_url"], "status": union["status"], "caveat": "Not a union over all 44 works."},
        {"metric_id": "CDSL-MARKUP", "value": markup["value_display"], "unit": "tag inventory and instances", "population": "markup census over the collection", "as_of": markup["as_of_date"], "source": markup["source_url"], "status": markup["status"], "caveat": "The rounded 17.5M display is not an exact instance count."},
        {"metric_id": "CDSL-CITATIONS", "value": citations["value_display"], "unit": "citation instances and canonical texts", "population": "dictionaries with usable <ls> citation markup", "as_of": citations["as_of_date"], "source": citations["source_url"], "status": citations["status"], "caveat": "Only tagged/canonicalisable citations are represented."},
    ]

    milestones: list[dict[str, object]] = [
        {"event_id": "HIST-1985-CHICAGO", "date_start": "1985", "date_end": "1985", "event_type": "prehistory", "event": "A University of Chicago attempt to digitise Sanskrit lexical resources included Monier-Williams but ended for lack of funding.", "actors": "University of Chicago project", "places": "Chicago", "evidence_tier": "published-primary", "source_locator": "Kapp and Malten 1997, CDSL report", "confidence": "high", "publication_targets": "A61", "status": "verified"},
        {"event_id": "HIST-1994-FOUNDING", "date_start": "1994", "date_end": "1994", "event_type": "institutional", "event": "Thomas Malten initiated CDSL at the University of Cologne.", "actors": "Thomas Malten; University of Cologne IITS", "places": "Cologne; Azhivaikkal", "evidence_tier": "published-primary", "source_locator": "Kapp and Malten 1997, CDSL report", "confidence": "high", "publication_targets": "A61;A13", "status": "verified"},
        {"event_id": "HIST-1997-PROGRAMME", "date_start": "1997", "date_end": "1997", "event_type": "programme", "event": "Kapp and Malten presented the digitise-and-integrate programme at the 10th World Sanskrit Conference.", "actors": "Dieter B. Kapp; Thomas Malten", "places": "Bangalore", "evidence_tier": "published-primary", "source_locator": "Kapp and Malten 1997, CDSL report", "confidence": "high", "publication_targets": "A61;A13", "status": "verified"},
        {"event_id": "HIST-2004-COLLAB", "date_start": "2004", "date_end": "2008", "event_type": "collaboration", "event": "The Cologne, Brown/Sanskrit Library, and Funderburk collaboration converted the project from character-coded text toward XML and a shared correction practice.", "actors": "Thomas Malten; Peter Scharf; Malcolm Hyman; Jim Funderburk", "places": "Cologne; Providence; distributed", "evidence_tier": "archival-attributed", "source_locator": "Scharf 2025 review and project files; Cologne call 2026-06-27", "confidence": "medium", "publication_targets": "A61;A13", "status": "verified-attributed"},
        {"event_id": "HIST-2008-SLP1", "date_start": "2008", "date_end": "2009", "event_type": "technical", "event": "The internal transliteration moved to SLP1 and the XML/markup conventions were documented.", "actors": "Peter Scharf; Malcolm Hyman; Jim Funderburk; collaborators", "places": "distributed", "evidence_tier": "published-and-archival", "source_locator": "Scharf and Hyman 2009; May 2008 project materials", "confidence": "high", "publication_targets": "A61", "status": "verified"},
        {"event_id": "HIST-2013-DCH", "date_start": "2013", "date_end": "2013", "event_type": "institutional", "event": "After the Cologne Indology programme ended, stewardship moved to the Data Center for the Humanities.", "actors": "Thomas Malten; Felix Rau; University of Cologne DCH", "places": "Cologne", "evidence_tier": "archival-attributed", "source_locator": "Scharf 2025 review; institutional documentation to be attached", "confidence": "medium", "publication_targets": "A61;A13", "status": "needs-primary-locator"},
        {"event_id": "HIST-2014-GITHUB", "date_start": "2014", "date_end": "2014", "event_type": "governance", "event": "The sanskrit-lexicon GitHub organisation made issue coordination and version history public.", "actors": "Mārcis Gasūns; CDSL collaborators", "places": "distributed", "evidence_tier": "committed-record", "source_locator": "data/issues.csv; GitHub organisation/repository creation records", "confidence": "high", "publication_targets": "A61;A13", "status": "verified"},
        {"event_id": "HIST-2019-FIRST-PRS", "date_start": "2019", "date_end": "2019", "event_type": "workflow", "event": "Pull requests first appear in the committed organisation activity snapshot; Git and public issues predate this milestone.", "actors": "sanskrit-lexicon contributors", "places": "GitHub", "evidence_tier": "committed-record", "source_locator": "data/issues.csv; reports/velocity_timeline.md", "confidence": "high", "publication_targets": "A61;A13", "status": "verified"},
        {"event_id": "HIST-2026-SUCCESSION", "date_start": "2026-06-27", "date_end": "2026-06-27", "event_type": "succession", "event": "Jim Funderburk publicly announced retirement and described the maintenance succession.", "actors": "Jim Funderburk; Dhaval Patel; volunteer group", "places": "online; Cologne infrastructure", "evidence_tier": "public-oral-history", "source_locator": "Cologne volunteer call recording, 2026-06-27", "confidence": "high", "publication_targets": "A61;A13", "status": "verified-attributed"},
        {"event_id": "HIST-EMAIL-TECH", "date_start": "2007", "date_end": "2013", "event_type": "technical-deliberation", "event": "Email evidence may refine the chronology of TEI, merge, headword, and morphology decisions.", "actors": "CDSL collaborators", "places": "distributed", "evidence_tier": "archival-pending", "source_locator": "historical email archive to be supplied by the author", "confidence": "pending", "publication_targets": "A61", "status": "evidence_pending"},
        {"event_id": "HIST-EMAIL-RIGHTS", "date_start": "2004", "date_end": "2005", "event_type": "rights", "event": "Email evidence may document the transition from restricted scan circulation toward later open distribution.", "actors": "Thomas Malten; Mārcis Gasūns", "places": "Cologne; distributed", "evidence_tier": "archival-pending", "source_locator": "historical email archive to be supplied by the author", "confidence": "pending", "publication_targets": "A61;A13", "status": "evidence_pending"},
    ]

    claims: list[dict[str, object]] = [
        {"claim_id": "A61-ARG-01", "article": "A61", "section": "abstract;1;3;9", "claim": "CDSL endured by repeatedly converting fragile personal scholarship into maintainable shared infrastructure.", "evidence_tier": "synthesis", "evidence_ids": "HIST-1994-FOUNDING;HIST-2004-COLLAB;HIST-2013-DCH;HIST-2014-GITHUB;HIST-2026-SUCCESSION", "status": "argument-to-develop"},
        {"claim_id": "A61-DATA-01", "article": "A61", "section": "abstract;3.4", "claim": "The June snapshot has two legitimate repository populations: 78 API inventory records and 76 transformed activity-table records.", "evidence_tier": "computed", "evidence_ids": "ORG-REPOS-API;ORG-REPOS-TRANSFORMED", "status": "verified"},
        {"claim_id": "A61-DATA-02", "article": "A61", "section": "abstract;5.3", "claim": "OBS-T contains 52,498 documented events across 43 dictionaries and 208 corrector labels.", "evidence_tier": "computed", "evidence_ids": "OBST-EVENTS;OBST-DICTIONARIES;OBST-CORRECTOR-IDS", "status": "verified-with-identity-caveat"},
        {"claim_id": "A61-DATA-03", "article": "A61", "section": "8.1;9.7", "claim": "Correction implementation is highly concentrated: at most four implementers per year and a 64–100% annual lead share.", "evidence_tier": "computed", "evidence_ids": "OBSQ-MAX-ANNUAL-CORRECTORS;OBSQ-LEAD-SHARE-RANGE", "status": "verified"},
        {"claim_id": "A61-HIST-01", "article": "A61", "section": "3", "claim": "1994 is the founding milestone; 2014 is the public-GitHub governance milestone; 2019 is only the first-PR milestone.", "evidence_tier": "published-and-computed", "evidence_ids": "HIST-1994-FOUNDING;HIST-2014-GITHUB;HIST-2019-FIRST-PRS", "status": "verified"},
        {"claim_id": "A13-METHOD-01", "article": "A13", "section": "proposed", "claim": "Repository records reveal public workflow but systematically under-record pre-2014 correspondence, informal labour, and identity.", "evidence_tier": "methodological", "evidence_ids": "HIST-EMAIL-TECH;HIST-EMAIL-RIGHTS;OBST-CORRECTOR-IDS;ORG-HUMAN-COMMIT-IDS", "status": "argument-to-develop"},
    ]

    contradictions: list[dict[str, object]] = [
        {"contradiction_id": "C-REPOS", "forms": "76 repositories vs 78 repositories", "resolution": "Keep both with named populations: transformed activity tables (76) and API inventory (78).", "status": "resolved", "article_action": "Define the denominator at every use."},
        {"contradiction_id": "C-CORRECTORS", "forms": "208 correctors vs 210 contributors", "resolution": "The canonical OBS-T summary has 208 release-safe corrector labels. 210 is stale/unsupported and must not be described as people.", "status": "resolved", "article_action": "Use 208 corrector identities/labels with an identity caveat."},
        {"contradiction_id": "C-GIT-HUMANS", "forms": "17 human Git contributors vs 16", "resolution": "actions-user is automation despite GitHub API type=User; curated bot override gives 16.", "status": "resolved", "article_action": "Use 16 only for the June Git contributor snapshot."},
        {"contradiction_id": "C-BUS-FACTOR", "forms": "65 of 76 vs 67 of 76 bus-factor-1 repositories", "resolution": "After the bot override is applied consistently, the regenerated value is 67 of 76.", "status": "resolved", "article_action": "Regenerate reports and stats census."},
        {"contradiction_id": "C-PERIOD", "forms": "2014–2016 founding vs project founded 1994", "resolution": "1994 is founding; 2014–2016 is the public correction-ledger/GitHub phase.", "status": "resolved", "article_action": "Rename the story-page period."},
        {"contradiction_id": "C-GIT-ARRIVES", "forms": "2019 Git arrives vs organisation active since 2014", "resolution": "2019 is the first pull-request year in the snapshot, not the arrival of Git.", "status": "resolved", "article_action": "Rename the story-page milestone."},
        {"contradiction_id": "C-COMPLETENESS", "forms": "every edit/issue/commit vs documented snapshot", "resolution": "The ledger is reconstructable within its source layers but incomplete before 2014 and for unlogged batches.", "status": "resolved", "article_action": "Remove universal completeness language."},
        {"contradiction_id": "C-OLD-OBST", "forms": "50,953 vs 52,498 correction events", "resolution": "52,498 is the current release total; older generated prose must be refreshed or labelled as a superseded snapshot.", "status": "resolved", "article_action": "Update cited reports and prompts."},
    ]

    source_rows = []
    for rel in INPUTS:
        path = ROOT / rel
        source_rows.append({
            "path": rel.as_posix(),
            "sha256": sha256(path),
            "bytes": path.stat().st_size,
        })

    files = {
        "metrics.csv": csv_text(metrics, ["metric_id", "value", "unit", "population", "as_of", "source", "status", "caveat"]),
        "milestones.csv": csv_text(milestones, ["event_id", "date_start", "date_end", "event_type", "event", "actors", "places", "evidence_tier", "source_locator", "confidence", "publication_targets", "status"]),
        "claim_registry.csv": csv_text(claims, ["claim_id", "article", "section", "claim", "evidence_tier", "evidence_ids", "status"]),
        "contradictions.csv": csv_text(contradictions, ["contradiction_id", "forms", "resolution", "status", "article_action"]),
        "source_artifacts.csv": csv_text(source_rows, ["path", "sha256", "bytes"]),
    }
    release_manifest = {
        "release_id": "a61-history-v1.0",
        "calendar_alias": "2026-07",
        "status": "verified-frozen",
        "built_from_csl_observatory_commit": git_source_base(),
        "github_snapshot_cutoff": legacy["snapshot_date"],
        "obs_t_cutoff": obs_t["dateRange"][1],
        "policy": "Per-metric cutoffs and population definitions are authoritative; no generic contributor total is defined.",
        "files": {},
    }
    for name, text in files.items():
        release_manifest["files"][name] = {
            "sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
            "bytes": len(text.encode("utf-8")),
        }
    files["manifest.json"] = json.dumps(release_manifest, ensure_ascii=False, indent=2) + "\n"
    return files


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Verify the committed bundle without rewriting it")
    args = parser.parse_args()
    expected = build()
    if args.check:
        drift = []
        for name, text in expected.items():
            path = OUT / name
            if not path.exists() or path.read_text(encoding="utf-8") != text:
                drift.append(name)
        if drift:
            raise SystemExit("article snapshot drift: " + ", ".join(drift))
        print(f"OK: a61-history-v1.0 ({len(expected)} files)")
        return 0
    OUT.mkdir(parents=True, exist_ok=True)
    for name, text in expected.items():
        (OUT / name).write_text(text, encoding="utf-8", newline="\n")
    print(f"wrote {OUT.relative_to(ROOT)} ({len(expected)} files)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
