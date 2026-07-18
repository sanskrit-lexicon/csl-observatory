#!/usr/bin/env python3
"""Build the immutable evidence bundle for history paper A61 (release v1.1).

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
OUT = ROOT / "data" / "publication" / "a61-history-v1.1"
SITE_DATA = ROOT / "observatory" / "site" / "src" / "data"
A13_PATH = ROOT / "article" / "00-report-narrative.md"
A13_SHA256 = "05fbe656224d93e46921614b2a609631c6769f761c8832e84ac84a3c991c9f00"
A61_SOURCE_BASE_COMMIT = "94a2de46a31891621cc7ec009850670d8e5ebdd7"
A61_SOURCE_REVISION = "frozen-working-tree-2026-07-18"
A61_SOURCE_BASE = "sibling:SanskritGrammar/TolchelnikovTalmud_2026/papers/MumbaiWSC_2027"

INPUTS = [
    Path("data/manifest.json"),
    Path("data/summary.json"),
    Path("observatory/site/src/data/obs_t_summary.json"),
    Path("observatory/site/src/data/obs_q_annual.csv"),
    Path("observatory/site/src/data/bus_factor.csv"),
    Path("observatory/site/src/data/contributor_identity.csv"),
    Path("observatory/site/src/data/stats_census_register.csv"),
]

# Source files were read from local siblings on 2026-07-18.  The hashes make the
# audit reproducible without making those repositories CI dependencies.  The
# A61 manuscript was frozen for this gate as a working-tree revision based on
# A61_SOURCE_BASE_COMMIT; do not misdescribe the frozen bytes as that commit.
LOCKED_EXTERNAL_SOURCES = [
    (f"{A61_SOURCE_BASE}/00-front-matter.mdx@{A61_SOURCE_REVISION}", "b2956ebd8cb17ff14161200e3644d6b189064193e02a01c35fed79ca94c07041", 4289),
    (f"{A61_SOURCE_BASE}/01-introduction.mdx@{A61_SOURCE_REVISION}", "e2d20ea3f5ae719c212464e17e3a9c9b2b4060c2dab11701ede39fc78490e3e2", 5933),
    (f"{A61_SOURCE_BASE}/02-dictionary-collection.mdx@{A61_SOURCE_REVISION}", "b3ad7c695eb3f46e5dee6a7cfb2d08280b0cb73a479b50f44b3aabb0a38c94ec", 7901),
    (f"{A61_SOURCE_BASE}/03-history.mdx@{A61_SOURCE_REVISION}", "ed3fe7774027100f6c9af800006f6a11bae9323487a2d3e07b9cf24a5d797f9a", 10076),
    (f"{A61_SOURCE_BASE}/04-data-architecture.mdx@{A61_SOURCE_REVISION}", "b3deefae3cae05ba3d12f0d84298f1d2ee9c2ec5e4cacc24e4f3b72041667c52", 7928),
    (f"{A61_SOURCE_BASE}/05-corrections.mdx@{A61_SOURCE_REVISION}", "5489ab920835034f5d3b3997d4b5c8de3efa26d6d659ec9567601aa3e86cb41d", 5879),
    (f"{A61_SOURCE_BASE}/06-corpus-linking.mdx@{A61_SOURCE_REVISION}", "d9b95bef18d528d49e7f34ad41a876d735834e0a03fba783954babff76a058a9", 6226),
    (f"{A61_SOURCE_BASE}/07-measurements.mdx@{A61_SOURCE_REVISION}", "edd8e5954374ed77e2af50cbe4d2afed4f64d0c8f234219fb9c88224b78d29c1", 4322),
    (f"{A61_SOURCE_BASE}/08-people.mdx@{A61_SOURCE_REVISION}", "89f279ecbcb73e8412e88c5870e6f634c05e8e76b20f8b6c3dac598b1d686337", 6529),
    (f"{A61_SOURCE_BASE}/09-limitations.mdx@{A61_SOURCE_REVISION}", "c85f67fbf1dae4b2ed6189e98d889ea642f84afe2b5335b833428692e8d1c8b0", 2299),
    (f"{A61_SOURCE_BASE}/09-future-plans.mdx@{A61_SOURCE_REVISION}", "2ae235d22604fb05c29a3f2fafa3e0c98f64abdb6aa9d0aac224f952783efbb9", 7221),
    (f"{A61_SOURCE_BASE}/11-conclusion.mdx@{A61_SOURCE_REVISION}", "9f2018c83da1b11a3dd1dd31d2e27f0b70c8ab1ccb43acebd074ab86b79b9489", 1955),
    ("sibling:SanskritLexicography/HeadwordLists/union/union_headwords.tsv", "4d5d35311e26c7d175ffd93486b5dc18feaefeb64b751a603b8a298434643e09", 12397253),
    ("sibling:SanskritLexicography/data/headword_overlap_matrix.tsv", "8ee827adb969b0690fec11b562712a8ef57c3989109f5da7cedbbb55d424fb0b", 2897),
    ("sibling:SanskritLexicography/data/headword_unique_counts.tsv", "ab3c66cb7a6746ace564657c2ce4603e3f9143643ecdcd4d8bcd70653c31d4f6", 386),
    ("sibling:SanskritLexicography/data/markup_tag_census.tsv", "1123c0ca10ec6a3566f007279d47a60c89da9d7a7f5f9093fa571561ba0a4022", 18492),
    ("sibling:SanskritLexicography/HeadwordLists/mw_heritage_crosswalk.tsv", "97b8b862115c2ed126d722b95f541cd7c9594f3bb5a30ce4a0073081072b2df6", 3263954),
    ("sibling:csl-atlas/src/data/etymology-oracle.json", "78c2853149cbd4c4c59e16ba4c16534349586f7c35703fd4a3cbecadf32f29aa", 23135),
    ("sibling:csl-atlas/data/citations/ls_citation_edges.tsv", "ce663622dbe3884b6108660892c8be6616a940808f63ae2e654f731391cd61fb", 47930),
    ("sibling:csl-atlas/data/citations/ls_citation_nodes.tsv", "af2c418e06c51b2e14719419d2978ba88de3fbda2ff66c684ff47308639020f3", 48478),
    ("sibling:MWS/root_crosswalk/root_crosswalk.csv", "079641692daabd822d09dfbc4f102601c082a59cb99a14de95082a08602c2238", 37160),
    ("sibling:csl-orig/v02/mw/mw_roots.tsv", "688273a435b4e824836d0287fb78a9ffc6ccb8f1071690efedf849cb46269f41", 77094),
    ("sibling:CORRECTIONS/nochange/testedfiles/hiatusmw.txt@643fd6df", "5602fb3a1a79227bfe5c0760768c13d83266a21646cd2aa6ee090a32d5cf3530", 3821),
    ("sibling:CORRECTIONS/dictionaries/MW/mw_printchange.txt@643fd6df", "ba755710a18cc0bd11ce99bbc710bdb1a50e1146d91aa0b0afddc4079a2febb0", 43276),
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
        {"metric_id": "CDSL-DICTIONARIES", "value": dictionaries["value_numeric"], "unit": "dictionary/reference works", "population": "current CDSL collection inventory", "as_of": dictionaries["as_of_date"], "source": dictionaries["source_url"], "status": "verified", "caveat": "Collection count includes reference works; OBS-T covers 43; stats-census workflow status is done."},
        {"metric_id": "CDSL-UNION-HW", "value": union["value_numeric"], "unit": "normalized headwords", "population": "union over the fifteen-dictionary comparison set", "as_of": union["as_of_date"], "source": union["source_url"], "status": "verified", "caveat": "Not a union over all 44 works; stats-census workflow status is done."},
        {"metric_id": "CDSL-MARKUP", "value": markup["value_display"], "unit": "tag inventory and instances", "population": "markup census over the collection", "as_of": markup["as_of_date"], "source": markup["source_url"], "status": markup["status"], "caveat": "The rounded 17.5M display is not an exact instance count."},
        {"metric_id": "CDSL-CITATIONS", "value": citations["value_display"], "unit": "citation instances and canonical texts", "population": "dictionaries with usable <ls> citation markup", "as_of": citations["as_of_date"], "source": citations["source_url"], "status": "verified", "caveat": "Only tagged/canonicalisable citations are represented; stats-census workflow status is done."},
        {"metric_id": "M10-PAIRWISE-PAIRS", "value": 105, "unit": "dictionary pairs", "population": "all unordered pairs among the fifteen-dictionary union set", "as_of": "2026-07-12", "source": "sibling:SanskritLexicography/data/headword_overlap_matrix.tsv", "status": "verified", "caveat": "Method: count matrix rows; equivalently 15 choose 2."},
        {"metric_id": "M10-BHS-UNIQUE-PCT", "value": 58.7, "unit": "percent", "population": "BHS normalized headwords unique within the fifteen-dictionary set", "as_of": "2026-07-12", "source": "sibling:SanskritLexicography/data/headword_unique_counts.tsv", "status": "verified-rounded", "caveat": "10,434 / 17,761 = 58.75%; manuscript rounds to one decimal."},
        {"metric_id": "M10-CCS-UNIQUE-PCT", "value": 0.6, "unit": "percent", "population": "CCS normalized headwords unique within the fifteen-dictionary set", "as_of": "2026-07-12", "source": "sibling:SanskritLexicography/data/headword_unique_counts.tsv", "status": "verified-rounded", "caveat": "178 / 28,743 = 0.62%; manuscript rounds to one decimal."},
        {"metric_id": "M10-MW-PWG-SHARED", "value": 94753, "unit": "normalized headwords", "population": "MW/PWG intersection in the fifteen-dictionary matrix", "as_of": "2026-07-12", "source": "sibling:SanskritLexicography/data/headword_overlap_matrix.tsv", "status": "verified", "caveat": "Method: read the unique MW-PWG matrix row; matrix uses normalized k1 headwords."},
        {"metric_id": "M10-MW-HEADWORDS-CURRENT", "value": 193852, "unit": "normalized headwords", "population": "MW headwords in the fifteen-dictionary matrix", "as_of": "2026-07-12", "source": "sibling:SanskritLexicography/data/headword_unique_counts.tsv", "status": "verified-current", "caveat": "A former draft's unexplained 168,633 population was removed; this current total is not retained in A61."},
        {"metric_id": "M10-PWG-HEADWORDS-CURRENT", "value": 106054, "unit": "normalized headwords", "population": "PWG headwords in the fifteen-dictionary matrix", "as_of": "2026-07-12", "source": "sibling:SanskritLexicography/data/headword_unique_counts.tsv", "status": "verified-current", "caveat": "A former draft's 106,169 total was removed; this current total is not retained in A61."},
        {"metric_id": "M10-ENTRY-LENGTH-BLOCK", "value": "110;245;30000;15%;819", "unit": "characters, entries, percent", "population": "claimed MW/PWG entry-length comparison", "as_of": "unknown", "source": "none located", "status": "unsupported", "caveat": "No committed local source, method, or cutoff was found; soften or delete the entire block."},
        {"metric_id": "M10-CITATION-OVERLAP-BLOCK", "value": "485;330;41.6%", "unit": "source abbreviations and percent", "population": "claimed MW/PWG source/locus overlap", "as_of": "unknown", "source": "none located", "status": "unsupported", "caveat": "Not the 828,505-edge canonical citation graph; soften or delete unless the older computation is recovered."},
        {"metric_id": "M10-ETYMO-DICTS", "value": 10, "unit": "dictionaries", "population": "dictionaries represented in the etymology oracle", "as_of": "2026-06-26", "source": "sibling:csl-atlas/src/data/etymology-oracle.json", "status": "verified", "caveat": "Method: dictionaryCount in the frozen JSON."},
        {"metric_id": "M10-ETYMO-ROWS-CURRENT", "value": 67172, "unit": "etymology records", "population": "all rows in the ten-dictionary etymology oracle", "as_of": "2026-06-26", "source": "sibling:csl-atlas/src/data/etymology-oracle.json", "status": "verified-current", "caveat": "The former 62,558 figure was removed; the current source reports 64,896 headwords with roots and 67,172 rows, neither retained in A61."},
        {"metric_id": "M10-ETYMO-AGREEMENT", "value": "90–100", "unit": "percent", "population": "claimed indigenous-tradition agreement on shared items", "as_of": "unknown", "source": "none located", "status": "unsupported", "caveat": "No exact selection rule or local result table was attached; soften to a qualitative statement or cite the method."},
        {"metric_id": "M10-MW-ROOTS", "value": "750 genuine + 1363 other = 2113", "unit": "root records", "population": "canonical MW root table grouped by verb_type", "as_of": "2026-07-12", "source": "sibling:csl-orig/v02/mw/mw_roots.tsv", "status": "verified-superseded-manuscript-figure", "caveat": "The former exact total was removed from A61; 1,363 is only the non-genuineroot class and the current total is 2,113."},
        {"metric_id": "M10-HERITAGE-CROSSWALK", "value": "185803 total;25140 covered;24549 anchors;97.65% of covered", "unit": "MW rows and percent", "population": "MW-to-Heritage crosswalk", "as_of": "2026-07-03", "source": "sibling:SanskritLexicography/HeadwordLists/mw_heritage_crosswalk.tsv", "status": "verified-superseded-manuscript-figure", "caveat": "Former insufficiently framed exact totals were removed from A61; 25,140 rows are Heritage-covered and 24,549 resolve to anchors."},
        {"metric_id": "M10-WHITNEY-HUB-CURRENT", "value": 935, "unit": "Whitney root records", "population": "rows in the current MW-Whitney-DCS root crosswalk", "as_of": "2026-07-12", "source": "sibling:MWS/root_crosswalk/root_crosswalk.csv", "status": "verified-current", "caveat": "The former 939 figure was removed; the current 935-row total is not retained in A61."},
        {"metric_id": "A61-HIATUS-ROWS", "value": 190, "unit": "nonblank rows", "population": "MW hiatus exception list", "as_of": "CORRECTIONS commit 643fd6df", "source": "sibling:CORRECTIONS/nochange/testedfiles/hiatusmw.txt@643fd6df", "status": "verified", "caveat": "Method: count nonblank physical rows; 190/190 rows are nonblank data rows."},
        {"metric_id": "A61-MW-PRINTCHANGE-ITEMS", "value": 137, "unit": "top-level numbered items", "population": "MW print-change audit file", "as_of": "CORRECTIONS commit 643fd6df", "source": "sibling:CORRECTIONS/dictionaries/MW/mw_printchange.txt@643fd6df", "status": "verified-superseded-manuscript-figure", "caveat": "Method: regex ^\\d+\\. over 1,011 physical lines; the former 'over 700 entries' claim was removed from A61."},
    ]

    milestones: list[dict[str, object]] = [
        {"event_id": "HIST-1985-CHICAGO", "date_start": "1985", "date_end": "1985", "event_type": "prehistory", "event": "A University of Chicago attempt to digitise Sanskrit lexical resources included Monier-Williams but ended for lack of funding.", "actors": "University of Chicago project", "places": "Chicago", "evidence_tier": "published-primary", "source_locator": "Kapp and Malten 1997, CDSL report", "confidence": "high", "publication_targets": "A61", "status": "verified"},
        {"event_id": "HIST-1994-FOUNDING", "date_start": "1994", "date_end": "1994", "event_type": "institutional", "event": "Thomas Malten initiated CDSL at the University of Cologne.", "actors": "Thomas Malten; University of Cologne IITS", "places": "Cologne; Azhivaikkal", "evidence_tier": "published-primary", "source_locator": "Kapp and Malten 1997, CDSL report", "confidence": "high", "publication_targets": "A61;A13", "status": "verified"},
        {"event_id": "HIST-1997-PROGRAMME", "date_start": "1997", "date_end": "1997", "event_type": "programme", "event": "Kapp and Malten presented the digitise-and-integrate programme at the 10th World Sanskrit Conference.", "actors": "Dieter B. Kapp; Thomas Malten", "places": "Bangalore", "evidence_tier": "published-primary", "source_locator": "Kapp and Malten 1997, CDSL report", "confidence": "high", "publication_targets": "A61;A13", "status": "verified"},
        {"event_id": "HIST-2004-COLLAB", "date_start": "2004", "date_end": "2008", "event_type": "collaboration", "event": "The Cologne, Brown/Sanskrit Library, and Funderburk collaboration converted the project from character-coded text toward XML and a shared correction practice.", "actors": "Thomas Malten; Peter Scharf; Malcolm Hyman; Jim Funderburk", "places": "Cologne; Providence; distributed", "evidence_tier": "archival-attributed", "source_locator": "Scharf 2025 review and project files; Cologne call 2026-06-27", "confidence": "medium", "publication_targets": "A61;A13", "status": "verified-attributed"},
        {"event_id": "HIST-2008-SLP1", "date_start": "2008", "date_end": "2009", "event_type": "technical", "event": "The internal transliteration moved to SLP1 and the XML/markup conventions were documented.", "actors": "Peter Scharf; Malcolm Hyman; Jim Funderburk; collaborators", "places": "distributed", "evidence_tier": "published-and-archival", "source_locator": "Scharf and Hyman 2009; May 2008 project materials", "confidence": "high", "publication_targets": "A61", "status": "verified"},
        {"event_id": "HIST-2013-DCH", "date_start": "2013", "date_end": "2013", "event_type": "institutional", "event": "After Malten retired, stewardship moved to the University of Cologne Data Center for the Humanities.", "actors": "Thomas Malten; Felix Rau; University of Cologne DCH", "places": "Cologne", "evidence_tier": "institutional-primary", "source_locator": "https://dch.phil-fak.uni-koeln.de/sites/dch/Materialien_Aktivitaeten/2016/The_Cologne_Sanskrit_Lexicon_2016-11-11.pdf (timeline); https://cceh.uni-koeln.de/en/portfolio/lazarus/ (2013-12 to 2015-01 project)", "confidence": "high", "publication_targets": "A61;A13", "status": "verified"},
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
        {"claim_id": "A61-DATA-03", "article": "A61", "section": "abstract;3.5;5.3;8;11", "claim": "Correction implementation is highly concentrated: at most five implementers per year and a 64–100% annual lead share.", "evidence_tier": "computed", "evidence_ids": "OBSQ-MAX-ANNUAL-CORRECTORS;OBSQ-LEAD-SHARE-RANGE", "status": "verified"},
        {"claim_id": "A61-HIST-01", "article": "A61", "section": "3", "claim": "1994 is the founding milestone; 2014 is the public-GitHub governance milestone; 2019 is only the first-PR milestone.", "evidence_tier": "published-and-computed", "evidence_ids": "HIST-1994-FOUNDING;HIST-2014-GITHUB;HIST-2019-FIRST-PRS", "status": "verified"},
        {"claim_id": "A61-NUM-00-ORG", "article": "A61", "section": "00-front-matter", "claim": "The retained organisation and correction figures are 78 API repositories, 76 transformed-table repositories, 5,413 issue/PR rows, 52,498 events, 43 dictionaries, 208 release-safe corrector labels, at most five annual implementers, and a 64–100% annual lead share.", "evidence_tier": "numeric-inventory", "evidence_ids": "ORG-REPOS-API;ORG-REPOS-TRANSFORMED;ORG-ISSUE-PR-ROWS;OBST-EVENTS;OBST-DICTIONARIES;OBST-CORRECTOR-IDS;OBSQ-MAX-ANNUAL-CORRECTORS;OBSQ-LEAD-SHARE-RANGE", "status": "verified"},
        {"claim_id": "A61-NUM-02-COLLECTION", "article": "A61", "section": "2", "claim": "The manuscript retains four founding dictionaries, 44 current works, eight correction/linking priorities, and two DDSA Sanskrit dictionaries.", "evidence_tier": "numeric-inventory", "evidence_ids": "CDSL-DICTIONARIES;HIST-1994-FOUNDING", "status": "44-verified;other-counts-published-or-descriptive"},
        {"claim_id": "A61-LEGAL-01", "article": "A61", "section": "2.4", "claim": "The former inference that Apte 1957 was public domain from editor and publisher death dates was removed; the manuscript now reports access history without a jurisdiction-specific legal conclusion.", "evidence_tier": "legal-review", "evidence_ids": "HIST-EMAIL-RIGHTS", "status": "removed-from-manuscript-v1.1"},
        {"claim_id": "A61-NUM-03-HISTORY", "article": "A61", "section": "3", "claim": "The retained chronology includes 1985, 1994, 2004–2013, 2008, 2013, 2014, 2016, 2018 and 2026; the June 2026 repository evidence retains 78 API repositories, 76 transformed repositories and 5,413 issue/PR rows, and the succession evidence retains at most five annual implementers with a 64–100% lead share.", "evidence_tier": "numeric-inventory", "evidence_ids": "HIST-1985-CHICAGO;HIST-1994-FOUNDING;HIST-2004-COLLAB;HIST-2008-SLP1;HIST-2013-DCH;HIST-2014-GITHUB;HIST-2026-SUCCESSION;ORG-REPOS-API;ORG-REPOS-TRANSFORMED;ORG-ISSUE-PR-ROWS;OBSQ-MAX-ANNUAL-CORRECTORS;OBSQ-LEAD-SHARE-RANGE", "status": "verified-or-verified-attributed"},
        {"claim_id": "A61-NUM-04-ARCH", "article": "A61", "section": "4", "claim": "The empirical collection count retained in the architecture chapter is 44 works; aggregate tag totals from the earlier draft are explicitly not used.", "evidence_tier": "numeric-inventory", "evidence_ids": "CDSL-DICTIONARIES", "status": "verified"},
        {"claim_id": "A61-NUM-05-CORRECTIONS", "article": "A61", "section": "5", "claim": "The retained correction figures are 52,498 documented events over twelve years (2014–2026), 43 dictionaries, 208 release-safe corrector labels, sixteen non-bot Git identities, no more than five annual implementers, a 64–100% annual lead share, 5,413 issue/PR rows and 76 transformed repositories.", "evidence_tier": "numeric-inventory", "evidence_ids": "OBST-EVENTS;OBST-DICTIONARIES;OBST-CORRECTOR-IDS;ORG-HUMAN-COMMIT-IDS;OBSQ-MAX-ANNUAL-CORRECTORS;OBSQ-LEAD-SHARE-RANGE;ORG-ISSUE-PR-ROWS;ORG-REPOS-TRANSFORMED", "status": "verified"},
        {"claim_id": "A61-NUM-06-CITATIONS", "article": "A61", "section": "6", "claim": "The retained citation graph has 828,505 canonicalised citations resolving to 912 distinct texts; the comparison denominator is the 323,425-headword union.", "evidence_tier": "numeric-inventory", "evidence_ids": "CDSL-CITATIONS;CDSL-UNION-HW", "status": "verified"},
        {"claim_id": "A61-M10-01", "article": "A61", "section": "7.1", "claim": "The fifteen-dictionary union has 323,425 normalized headwords and 105 pairs; BHS unique share is 58.7% and CCS unique share is 0.6%.", "evidence_tier": "computed-locked-local", "evidence_ids": "CDSL-UNION-HW;M10-PAIRWISE-PAIRS;M10-BHS-UNIQUE-PCT;M10-CCS-UNIQUE-PCT", "status": "verified"},
        {"claim_id": "A61-M10-02", "article": "A61", "section": "7.2", "claim": "The retained MW–PWG comparison establishes 94,753 common normalized lemmas.", "evidence_tier": "computed-locked-local", "evidence_ids": "M10-MW-PWG-SHARED", "status": "verified"},
        {"claim_id": "A61-M10-03", "article": "A61", "section": "7.2", "claim": "The former entry-length and citation-overlap exact blocks were removed because no locked source and method were located.", "evidence_tier": "secondary-exact-figure", "evidence_ids": "M10-ENTRY-LENGTH-BLOCK;M10-CITATION-OVERLAP-BLOCK", "status": "removed-from-manuscript-v1.1"},
        {"claim_id": "A61-M10-04", "article": "A61", "section": "7.3", "claim": "The former stale etymology and root exact totals were removed; the manuscript retains only qualitative claims supported by the current oracle.", "evidence_tier": "computed-locked-local", "evidence_ids": "M10-ETYMO-DICTS;M10-ETYMO-ROWS-CURRENT;M10-ETYMO-AGREEMENT;M10-MW-ROOTS", "status": "removed-or-superseded-in-manuscript-v1.1"},
        {"claim_id": "A61-M10-05", "article": "A61", "section": "7.4", "claim": "The former exact Heritage and Whitney alignment totals were removed because their populations were stale or insufficiently framed.", "evidence_tier": "computed-locked-local", "evidence_ids": "M10-HERITAGE-CROSSWALK;M10-WHITNEY-HUB-CURRENT", "status": "removed-from-manuscript-v1.1"},
        {"claim_id": "A61-NUM-08-PEOPLE", "article": "A61", "section": "8", "claim": "The retained measured populations are 208 OBS-T labels, sixteen normalized non-bot Git identities, at most five annual correction implementers and a 64–100% annual lead share; the approximately thirty Andhrabharati dictionaries and 70% Telugu estimate remain attributed testimony.", "evidence_tier": "numeric-inventory", "evidence_ids": "OBST-CORRECTOR-IDS;ORG-HUMAN-COMMIT-IDS;OBSQ-MAX-ANNUAL-CORRECTORS;OBSQ-LEAD-SHARE-RANGE;HIST-2026-SUCCESSION", "status": "measured-values-verified;testimony-attributed"},
        {"claim_id": "A61-NUM-10-PLANS", "article": "A61", "section": "10", "claim": "The retained descriptive plan counts are five Sanskrit–Russian dictionaries, two Dhātupāṭhas, three headword-programme items and one proposed reverse dictionary; former traffic and archive-file exact totals were removed.", "evidence_tier": "numeric-inventory", "evidence_ids": "HIST-EMAIL-TECH", "status": "descriptive-project-counts;removed-figures-not-retained"},
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
        {"contradiction_id": "C-IMPLEMENTERS", "forms": "at most four vs computed maximum five implementers per year", "resolution": "The locked OBS-Q annual table has a maximum of five.", "status": "resolved", "article_action": "Use five in A61/A15 and the registry."},
        {"contradiction_id": "C-M10-HEADWORDS", "forms": "MW 168,633 / PWG 106,169 vs current matrix 193,852 / 106,054", "resolution": "The unexplained totals were removed; the reproducible 94,753 intersection remains.", "status": "resolved-removed", "article_action": "No further manuscript action."},
        {"contradiction_id": "C-M10-ETYMOLOGY", "forms": "62,558 records vs current etymology-oracle 67,172", "resolution": "The stale exact total was removed and the current discussion is qualitative.", "status": "resolved-removed", "article_action": "No further manuscript action."},
        {"contradiction_id": "C-M10-HERITAGE", "forms": "185,803 aligned at 97.6% vs 185,803 total MW rows / 25,140 covered / 24,549 anchors", "resolution": "The insufficiently framed exact alignment totals were removed.", "status": "resolved-removed", "article_action": "No further manuscript action."},
        {"contradiction_id": "C-M10-WHITNEY", "forms": "939 root records vs current 935-row crosswalk", "resolution": "The stale exact crosswalk total was removed.", "status": "resolved-removed", "article_action": "No further manuscript action."},
        {"contradiction_id": "C-APTE-RIGHTS", "forms": "public-domain conclusion from editor/publisher death dates", "resolution": "The legal conclusion was deleted; the manuscript reports access history only.", "status": "resolved-removed", "article_action": "A documented rights determination is still required before any future public-domain assertion."},
        {"contradiction_id": "C-MW-PRINTCHANGE", "forms": "over 700 entries vs 137 top-level numbered items", "resolution": "The unsupported count was removed; the registry preserves the 137-item audit result without presenting it as a retained manuscript claim.", "status": "resolved-removed", "article_action": "No further manuscript action."},
    ]

    metric_ids = {str(row["metric_id"]) for row in metrics}
    event_ids = {str(row["event_id"]) for row in milestones}
    known_ids = metric_ids | event_ids
    claim_ids = [str(row["claim_id"]) for row in claims]
    if len(claim_ids) != len(set(claim_ids)):
        raise SystemExit("duplicate claim_id in A61 claim registry")
    for claim in claims:
        unknown = set(str(claim["evidence_ids"]).split(";")) - known_ids
        if unknown:
            raise SystemExit(f"unknown evidence ids for {claim['claim_id']}: {sorted(unknown)}")
    pending = {str(row["event_id"]) for row in milestones if row["status"] == "evidence_pending"}
    if pending != {"HIST-EMAIL-TECH", "HIST-EMAIL-RIGHTS"}:
        raise SystemExit(f"email milestone gate drift: {sorted(pending)}")
    if any("at most four implementers" in str(row["claim"]).lower() for row in claims):
        raise SystemExit("stale four-implementer claim remains in registry")
    numeric_sections = {str(row["section"]).split(".")[0] for row in claims if str(row["claim_id"]).startswith("A61-NUM-")}
    if not {"00-front-matter", "2", "3", "4", "5", "6", "8", "10"}.issubset(numeric_sections):
        raise SystemExit("A61 numeric inventory is missing a manuscript chapter")
    retained_rows = [row for row in claims if "removed" not in str(row["status"]) and "superseded" not in str(row["status"])]
    stale_retained_forms = ("210 claimed", "over 700", "482,400", "62,558", "81.4%")
    for row in retained_rows:
        if any(form in str(row["claim"]) for form in stale_retained_forms):
            raise SystemExit(f"stale form is still described as retained: {row['claim_id']}")

    source_rows = []
    for rel in INPUTS:
        path = ROOT / rel
        source_rows.append({
            "path": rel.as_posix(),
            "sha256": sha256(path),
            "bytes": path.stat().st_size,
        })
    for path, digest, size in LOCKED_EXTERNAL_SOURCES:
        source_rows.append({"path": path, "sha256": digest, "bytes": size})

    files = {
        "metrics.csv": csv_text(metrics, ["metric_id", "value", "unit", "population", "as_of", "source", "status", "caveat"]),
        "milestones.csv": csv_text(milestones, ["event_id", "date_start", "date_end", "event_type", "event", "actors", "places", "evidence_tier", "source_locator", "confidence", "publication_targets", "status"]),
        "claim_registry.csv": csv_text(claims, ["claim_id", "article", "section", "claim", "evidence_tier", "evidence_ids", "status"]),
        "contradictions.csv": csv_text(contradictions, ["contradiction_id", "forms", "resolution", "status", "article_action"]),
        "source_artifacts.csv": csv_text(source_rows, ["path", "sha256", "bytes"]),
    }
    release_manifest = {
        "release_id": "a61-history-v1.1",
        "calendar_alias": "2026-07",
        "status": "verified-frozen",
        "built_from_csl_observatory_commit": git_source_base(),
        "github_snapshot_cutoff": legacy["snapshot_date"],
        "obs_t_cutoff": obs_t["dateRange"][1],
        "a61_manuscript_base_commit": A61_SOURCE_BASE_COMMIT,
        "a61_manuscript_revision": A61_SOURCE_REVISION,
        "a61_numeric_inventory_scope": "00-front-matter.mdx through 11-conclusion.mdx, excluding references; empirical/project numbers retained; headings, section references, illustrative source identifiers, bibliography and edition years excluded unless historically load-bearing",
        "wsc_venue_checked": "2026-07-18",
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
    if sha256(A13_PATH) != A13_SHA256:
        raise SystemExit("A13 byte fence changed: article/00-report-narrative.md")
    expected = build()
    if args.check:
        drift = []
        for name, text in expected.items():
            path = OUT / name
            if not path.exists() or path.read_text(encoding="utf-8") != text:
                drift.append(name)
        if drift:
            raise SystemExit("article snapshot drift: " + ", ".join(drift))
        print(f"OK: a61-history-v1.1 ({len(expected)} files; A13 byte fence intact)")
        return 0
    OUT.mkdir(parents=True, exist_ok=True)
    for name, text in expected.items():
        (OUT / name).write_text(text, encoding="utf-8", newline="\n")
    print(f"wrote {OUT.relative_to(ROOT)} as a61-history-v1.1 ({len(expected)} files)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
