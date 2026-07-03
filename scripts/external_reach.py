#!/usr/bin/env python3
"""External impact & reach (scholar-framed) for the sanskrit-lexicon org.

Measures *scholarly footprint* — who builds on, clones, ships, and cites the
Cologne Digital Sanskrit Lexicon (CDSL) — rather than funder-facing vanity
metrics (MG 2026-07-03, Workstream G6). Four evidence tiers, each with
per-line provenance and a fetch date:

  1. GitHub stars/forks   — OFFLINE from ``repos.csv``. Near-zero *by itself* is
                            the finding: the org is used as infrastructure (via
                            the Cologne site and bulk clones), not starred.
  2. GitHub traffic        — views/clones (14-day rolling window, needs push
                            auth) for a core set of infrastructure repos. The
                            clone counts are the strongest reach signal.
  3. Downstream dependents — GitHub code-search hits for raw ``sanskrit-lexicon``
                            / ``uni-koeln.de`` consumption + a curated list of
                            known ecosystem consumers (PyCDSL, Ambuda, Digital
                            Pali Dictionary, StarDict-Sanskrit, ...), each with a
                            URL.
  4. Scholarly citations   — REPRESENTATIVE, not exhaustive (web/Scholar). No
                            completeness claim.

The report separates MEASURED (tiers 1-3, every line with a URL and/or fetch
date) from ESTIMATED (tier 4).

Zenodo (OBS-T dataset views/downloads) is a PLANNED fifth tier but is currently
**BLOCKED**: the DOI recorded across the repo (10.5281/zenodo.15834721) does not
resolve to the OBS-T dataset — it resolves to an unrelated topology preprint
("A Non-Surgical ... Proof of Topological Sphericity ...", created 2025-07-08,
a year before OBS-T's claimed 2026-07-01 mint). Rather than attribute a
stranger's 1,261 downloads to CDSL, the script fetches the record, verifies its
title/creator against expected tokens, and reports the mismatch as a status row
for MG to resolve. See ``docs`` / GTD and ``.ai_state.md``.

API parts run only under ``--fetch`` and are cached under
``reports/external_reach_cache/<YYYY-MM>/`` (a *committed* cache — small JSON) so
the report regenerates offline from a fresh clone with no network.

Outputs:
  * reports/external_reach.md
  * observatory/site/src/data/external_reach.csv

Usage:
  python scripts/external_reach.py            # offline: regenerate from cache
  python scripts/external_reach.py --fetch    # refresh API caches, then build
"""

from __future__ import annotations

import argparse
import csv
import json
import subprocess
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "observatory" / "site" / "src" / "data"
REPOS_CSV = DATA / "repos.csv"
OUT_MD = ROOT / "reports" / "external_reach.md"
OUT_CSV = DATA / "external_reach.csv"
SNAPSHOT_MONTH = datetime.now(timezone.utc).strftime("%Y-%m")
# Committed (tracked) cache — small JSON, so the report regenerates offline from
# a fresh clone. NB: observatory/snapshots/ is gitignored (large, regenerable),
# so this reproducible cache lives under reports/ instead.
CACHE_DIR = ROOT / "reports" / "external_reach_cache" / SNAPSHOT_MONTH

OWNER = "sanskrit-lexicon"

# Core infrastructure repos sampled for GitHub traffic (14-day views/clones).
# Not all 76 — a curated high-signal set (top-star + core pipeline repos). The
# org-wide caveat is stated in the report; this is a documented sample, not a
# silent cap.
CORE_REPOS = [
    "csl-orig", "MWS", "COLOGNE", "CORRECTIONS", "cologne-stardict",
    "csl-pywork", "csl-websanlexicon", "csl-observatory", "csl-inflect",
    "PWK", "GRA", "ApteES", "csl-apidev", "csl-atlas",
]

# GitHub code-search queries probing external consumption of org data/URLs.
CODE_SEARCH_QUERIES = [
    "sanskrit-lexicon raw.githubusercontent.com",
    "sanskrit-lexicon.uni-koeln.de",
    "github.com/sanskrit-lexicon",
]

# Repos owned by the project itself (org + maintainer personal) — excluded from
# the *external*-dependent count so the reach number is genuinely third-party.
INTERNAL_OWNERS = {"sanskrit-lexicon", "sanskrit-lexicon-scans", "gasyoun",
                   "funderburkjim", "drdhaval2785"}

# Curated known downstream consumers (from Uprava/PROJECT_INTERLINKS.md + the
# code-search sweep). Each is a real third-party project shipping or wrapping
# CDSL data. `kind`: software = library/app consuming the API/data; data =
# ships CDSL dictionary files; style = a browser userstyle over the Cologne site.
KNOWN_CONSUMERS = [
    ("PyCDSL", "software", "Python interface to the CDSL — on PyPI",
     "https://pypi.org/project/PyCDSL/"),
    ("Ambuda", "software", "Sanskrit reading platform bundling CDSL dictionaries",
     "https://github.com/ambuda-org/ambuda"),
    ("ambuda-org/dictionaries", "data", "CDSL dictionaries packaged for Ambuda",
     "https://github.com/ambuda-org/dictionaries"),
    ("Digital Pali Dictionary (dpd-db)", "data",
     "References the Cologne site among its dictionary sources",
     "https://github.com/digitalpalidictionary/dpd-db"),
    ("indic-dict/stardict-sanskrit", "data",
     "StarDict builds of Sanskrit dictionaries incl. CDSL sources",
     "https://github.com/indic-dict/stardict-sanskrit"),
    ("bhaddacak/paliplatform", "software",
     "Pali reading platform listing sanskrit-lexicon dictionary URLs",
     "https://github.com/bhaddacak/paliplatform"),
    ("ashtadhyayi-com/data", "data",
     "Ashtadhyayi.com ships CDSL-derived dictionary JSON (pd.json, snp.json)",
     "https://github.com/ashtadhyayi-com/data"),
    ("Samskrita-Bharati/zat.am", "software",
     "Samskrita Bharati resource referencing the Cologne lexicon",
     "https://github.com/Samskrita-Bharati/zat.am"),
    ("koeln-sanskrit-dictionary userstyle", "style",
     "Community userstyle restyling the Cologne dictionary site",
     "https://github.com/rramphal/browser-customizations"),
    ("Dictionaryphile/All_Dictionaries", "data",
     "Aggregated dictionary collection referencing the Cologne site",
     "https://github.com/Dictionaryphile/All_Dictionaries"),
]

# Representative scholarly citations (NOT exhaustive — web/Scholar, 2020-2026).
# Each is a published work that uses or cites the Cologne dictionaries/lexicon.
CITATIONS = [
    ("Transforming the Cologne Digital Sanskrit Dictionaries into OntoLex-Lemon",
     "2020", "LDL / ACL Anthology", "https://aclanthology.org/2020.ldl-1.2/"),
    ("PyCDSL: a Python interface to the Cologne Digital Sanskrit Lexicon",
     "2021", "software / PyPI", "https://github.com/hrishikeshrt/PyCDSL"),
    ("Sanskrit Knowledge-based Systems: Annotation and Computational Tools",
     "2024", "arXiv:2406.18276", "https://arxiv.org/abs/2406.18276"),
    ("One Model is All You Need: ByT5-Sanskrit, a Unified Model for Sanskrit NLP",
     "2024", "arXiv:2409.13920", "https://arxiv.org/abs/2409.13920"),
    ("Cologne Sanskrit Lexicon (managed resource entry)",
     "ongoing", "Uni Köln CCeH / DCH",
     "https://dch.phil-fak.uni-koeln.de/en/ressources/managed-resources/cologne-sanskrit-lexicon"),
]

# Zenodo record recorded (in the repo) as the OBS-T dataset, plus tokens we
# expect a genuine OBS-T record's title to contain. A miss = DOI mismatch.
ZENODO_RECORD_ID = "15834721"
ZENODO_EXPECT_TOKENS = ("sanskrit", "cologne", "obs-t", "correction", "lexicon",
                        "dictionary")

_TRANSIENT = ("502", "503", "504", "timed out", "timeout", "connection reset",
              "temporarily unavailable", "bad gateway")


# --------------------------------------------------------------------------- #
# Fetch helpers (only used under --fetch)
# --------------------------------------------------------------------------- #
def _gh_json(endpoint: str, args: list[str], retries: int = 2):
    """Run `gh api <endpoint> <args>` and parse JSON, with bounded retry."""
    last = "unknown gh api error"
    for attempt in range(retries + 1):
        try:
            res = subprocess.run(
                ["gh", "api", endpoint, *args],
                cwd=ROOT, text=True, encoding="utf-8", errors="replace",
                stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                timeout=60, check=False,
            )
        except (subprocess.TimeoutExpired, OSError) as exc:
            last = f"gh api failed: {exc}"
            if attempt < retries:
                time.sleep(2 ** attempt)
                continue
            return None, last
        if res.returncode != 0:
            last = (res.stderr.strip() or res.stdout.strip()
                    or "unknown gh api error").replace("\n", " ")
            if any(t in last.lower() for t in _TRANSIENT) and attempt < retries:
                time.sleep(2 ** attempt)
                continue
            return None, last
        try:
            return json.loads(res.stdout), ""
        except json.JSONDecodeError as exc:
            return None, f"invalid JSON from gh api: {exc}"
    return None, last


def _http_json(url: str, retries: int = 2):
    """Fetch a JSON URL with the stdlib and bounded retry."""
    last = "unknown http error"
    for attempt in range(retries + 1):
        try:
            req = urllib.request.Request(
                url, headers={"Accept": "application/json",
                              "User-Agent": "csl-observatory-external-reach"})
            with urllib.request.urlopen(req, timeout=60) as resp:
                return json.loads(resp.read().decode("utf-8")), ""
        except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
            last = f"http failed: {exc}"
            if attempt < retries:
                time.sleep(2 ** attempt)
                continue
            return None, last
    return None, last


def fetch_all() -> None:
    """Refresh every API cache under CACHE_DIR. Partial failures are recorded
    as warnings so an offline rebuild still works from whatever was cached."""
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    fetched_at = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    warnings: list[str] = []

    # --- traffic (views + clones) per core repo ---
    traffic = {}
    for repo in CORE_REPOS:
        views, vw = _gh_json(f"repos/{OWNER}/{repo}/traffic/views", [])
        clones, cw = _gh_json(f"repos/{OWNER}/{repo}/traffic/clones", [])
        entry = {}
        if views is not None:
            entry["views_count"] = views.get("count", 0)
            entry["views_uniques"] = views.get("uniques", 0)
        else:
            warnings.append(f"traffic/views {repo}: {vw}")
        if clones is not None:
            entry["clones_count"] = clones.get("count", 0)
            entry["clones_uniques"] = clones.get("uniques", 0)
        else:
            warnings.append(f"traffic/clones {repo}: {cw}")
        if entry:
            traffic[repo] = entry
    (CACHE_DIR / "traffic.json").write_text(
        json.dumps(traffic, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    # --- code search: external raw-URL / site consumption ---
    code_search = {}
    for q in CODE_SEARCH_QUERIES:
        data, w = _gh_json("search/code", ["-X", "GET", "-f", f"q={q}",
                                           "-f", "per_page=50"])
        if data is None:
            warnings.append(f"search/code '{q}': {w}")
            continue
        repos = sorted({i["repository"]["full_name"] for i in data.get("items", [])})
        code_search[q] = {"total_count": data.get("total_count", 0), "repos": repos}
    (CACHE_DIR / "code_search.json").write_text(
        json.dumps(code_search, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    # --- Zenodo record (evidence for the DOI-mismatch check) ---
    zen, zw = _http_json(f"https://zenodo.org/api/records/{ZENODO_RECORD_ID}")
    if zen is not None:
        slim = {
            "id": zen.get("id"),
            "doi": zen.get("doi"),
            "conceptdoi": zen.get("conceptdoi"),
            "title": zen.get("title") or zen.get("metadata", {}).get("title"),
            "created": zen.get("created"),
            "creators": [c.get("name") for c in
                         zen.get("metadata", {}).get("creators", [])],
            "files": [f.get("key") for f in zen.get("files", [])],
            "stats": zen.get("stats"),
        }
        (CACHE_DIR / f"zenodo_{ZENODO_RECORD_ID}.json").write_text(
            json.dumps(slim, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    else:
        warnings.append(f"zenodo {ZENODO_RECORD_ID}: {zw}")

    (CACHE_DIR / "meta.json").write_text(
        json.dumps({"fetched_at": fetched_at, "warnings": warnings},
                   ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"fetched → {CACHE_DIR}")
    if warnings:
        print(f"  {len(warnings)} warning(s):")
        for w in warnings:
            print(f"   - {w}")


# --------------------------------------------------------------------------- #
# Offline build
# --------------------------------------------------------------------------- #
def load_cache(name: str):
    path = CACHE_DIR / name
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def zenodo_status(zen: dict | None) -> tuple[str, str]:
    """Return (status, detail). status ∈ {ok, mismatch, unavailable}."""
    if zen is None:
        return "unavailable", "no Zenodo cache — run --fetch"
    title = (zen.get("title") or "").lower()
    if any(tok in title for tok in ZENODO_EXPECT_TOKENS):
        return "ok", f"title matches OBS-T tokens: {zen.get('title')!r}"
    return "mismatch", (
        f"DOI {zen.get('doi')} resolves to an UNRELATED record "
        f"(title={zen.get('title')!r}, created={zen.get('created')}, "
        f"files={zen.get('files')}) — not the OBS-T dataset")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--fetch", action="store_true",
                    help="Refresh API caches before building (network).")
    args = ap.parse_args()
    if args.fetch:
        fetch_all()

    meta = load_cache("meta.json") or {}
    fetched_at = meta.get("fetched_at", "(no fetch — offline cache)")

    # ---- tier 1: stars / forks (offline) ----
    repos = list(csv.DictReader(REPOS_CSV.open(encoding="utf-8")))
    for r in repos:
        r["stars"] = int(r.get("stars") or 0)
        r["forks"] = int(r.get("forks") or 0)
    total_stars = sum(r["stars"] for r in repos)
    total_forks = sum(r["forks"] for r in repos)
    zero_star = sum(1 for r in repos if r["stars"] == 0)
    top = sorted(repos, key=lambda r: (-r["stars"], -r["forks"]))[:10]

    # ---- tier 2: traffic ----
    traffic = load_cache("traffic.json") or {}
    traffic_rows = []
    for repo, e in traffic.items():
        traffic_rows.append({
            "repo": repo,
            "views": e.get("views_count", ""),
            "views_uniq": e.get("views_uniques", ""),
            "clones": e.get("clones_count", ""),
            "clones_uniq": e.get("clones_uniques", ""),
        })
    traffic_rows.sort(key=lambda r: -(r["clones"] if isinstance(r["clones"], int) else 0))
    total_clones = sum(r["clones"] for r in traffic_rows if isinstance(r["clones"], int))
    total_uniq_cloners = sum(r["clones_uniq"] for r in traffic_rows
                             if isinstance(r["clones_uniq"], int))

    # ---- tier 3: dependents ----
    code_search = load_cache("code_search.json") or {}
    external_repos: set[str] = set()
    for q, res in code_search.items():
        for full in res.get("repos", []):
            owner = full.split("/", 1)[0]
            if owner not in INTERNAL_OWNERS:
                external_repos.add(full)

    # ---- Zenodo status ----
    zen = load_cache(f"zenodo_{ZENODO_RECORD_ID}.json")
    zstatus, zdetail = zenodo_status(zen)

    # ---- write CSV (tidy long form) ----
    csv_rows = []

    def add(signal, subject, metric, value, url, tier, note=""):
        csv_rows.append({"signal_type": signal, "subject": subject,
                         "metric": metric, "value": value, "url": url,
                         "tier": tier, "fetched_at": fetched_at, "note": note})

    add("stars_forks", "sanskrit-lexicon org (76 repos)", "total_stars",
        total_stars, "https://github.com/sanskrit-lexicon", "measured",
        f"{zero_star}/76 repos have zero stars")
    add("stars_forks", "sanskrit-lexicon org (76 repos)", "total_forks",
        total_forks, "https://github.com/sanskrit-lexicon", "measured", "")
    for r in traffic_rows:
        add("traffic", r["repo"], "clones_14d", r["clones"],
            f"https://github.com/{OWNER}/{r['repo']}", "measured",
            f"{r['clones_uniq']} unique cloners; {r['views']} views/"
            f"{r['views_uniq']} unique (14-day window)")
    for name, kind, desc, url in KNOWN_CONSUMERS:
        add("dependent", name, kind, "", url, "measured", desc)
    for full in sorted(external_repos):
        add("dependent_codesearch", full, "raw_url_or_site_reference", "",
            f"https://github.com/{full}", "measured",
            "GitHub code-search hit for CDSL raw-URL / site consumption")
    for title, year, venue, url in CITATIONS:
        add("citation", title, "scholarly_citation", year, url, "estimated",
            f"venue: {venue}")
    add("zenodo", f"record {ZENODO_RECORD_ID}", "status", zstatus,
        f"https://doi.org/10.5281/zenodo.{ZENODO_RECORD_ID}", "blocked", zdetail)

    with OUT_CSV.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["signal_type", "subject", "metric",
                                          "value", "url", "tier", "fetched_at",
                                          "note"])
        w.writeheader()
        w.writerows(csv_rows)

    # ---- write report ----
    L: list[str] = []
    A = L.append
    A("# External impact & reach (scholar-framed)")
    A("")
    A(f"_Generated by [`scripts/external_reach.py`](https://github.com/sanskrit-lexicon/"
      f"csl-observatory/blob/main/scripts/external_reach.py). API tiers cached "
      f"under `reports/external_reach_cache/{SNAPSHOT_MONTH}/` (committed); the "
      f"report regenerates offline. Last API fetch: {fetched_at}._")
    A("")
    A("Reach here means **scholarly footprint** — who builds on, clones, ships, "
      "and cites the Cologne Digital Sanskrit Lexicon (CDSL) — not funder-facing "
      "vanity metrics (Workstream G6, MG 2026-07-03). **Measured** tiers "
      "(stars/forks, traffic, dependents) carry a URL and/or fetch date; the "
      "**estimated** citation tier is representative, with no completeness claim.")
    A("")

    A("## Headline")
    A("")
    A("| Signal | Value | Reading |")
    A("|---|---:|---|")
    A(f"| GitHub stars (whole org, 76 repos) | **{total_stars}** | "
      f"{zero_star}/76 repos have **zero** stars |")
    A(f"| GitHub forks (whole org) | {total_forks} | |")
    A(f"| 14-day clones (core {len(traffic_rows)} repos) | **{total_clones:,}** | "
      f"~{total_uniq_cloners:,} unique cloners in two weeks |")
    A(f"| Third-party dependent repos (code-search) | {len(external_repos)} | "
      "distinct external repos referencing org raw-URLs / the Cologne site |")
    A(f"| Curated known consumers | {len(KNOWN_CONSUMERS)} | "
      "libraries/apps/data packages shipping or wrapping CDSL |")
    A(f"| Representative scholarly citations | {len(CITATIONS)} | "
      "NOT exhaustive — see caveat |")
    A(f"| Zenodo OBS-T download stats | **{zstatus.upper()}** | see blocker below |")
    A("")
    A("**The stars-vs-clones gap is the finding.** The org collects ~"
      f"{total_stars} stars in total, yet its core repositories are cloned "
      f"**{total_clones:,} times in a single 14-day window**. CDSL is consumed "
      "as *infrastructure* — cloned, mirrored, and served through the Cologne "
      "website — not favourited on GitHub. Star count badly understates reach.")
    A("")

    A("## Tier 1 — Stars & forks (measured, offline)")
    A("")
    A("Baseline from [`repos.csv`](https://github.com/sanskrit-lexicon/"
      "csl-observatory/blob/main/observatory/site/src/data/repos.csv). Top repos:")
    A("")
    A("| Repository | Stars | Forks |")
    A("|---|---:|---:|")
    for r in top:
        A(f"| [{r['repo']}](https://github.com/{OWNER}/{r['repo']}) | "
          f"{r['stars']} | {r['forks']} |")
    A("")

    A("## Tier 2 — GitHub traffic (measured, 14-day window)")
    A("")
    A(f"Views and clones for a curated core of {len(traffic_rows)} infrastructure "
      "repositories (top-star + core pipeline). GitHub only exposes a rolling "
      "14-day window and only to accounts with push access; this is a **sample**, "
      "not all 76 repos, and the window slides — treat as a spot reading, not a "
      "cumulative total.")
    A("")
    A("| Repository | Clones (14d) | Unique cloners | Views | Unique viewers |")
    A("|---|---:|---:|---:|---:|")
    for r in traffic_rows:
        A(f"| [{r['repo']}](https://github.com/{OWNER}/{r['repo']}) | "
          f"{r['clones']} | {r['clones_uniq']} | {r['views']} | {r['views_uniq']} |")
    A(f"| **Total (sample)** | **{total_clones:,}** | ~{total_uniq_cloners:,} | | |")
    A("")

    A("## Tier 3 — Downstream dependents (measured, URL-cited)")
    A("")
    A("### Known consumers (curated)")
    A("")
    A("Third-party projects that ship, wrap, or serve CDSL data, from "
      "[`Uprava/PROJECT_INTERLINKS.md`](https://github.com/gasyoun/Uprava/blob/"
      "main/PROJECT_INTERLINKS.md) and the code-search sweep:")
    A("")
    A("| Consumer | Kind | What it does |")
    A("|---|---|---|")
    for name, kind, desc, url in KNOWN_CONSUMERS:
        A(f"| [{name}]({url}) | {kind} | {desc} |")
    A("")
    A(f"### Code-search dependents ({len(external_repos)} external repos)")
    A("")
    A("Distinct third-party (non-org, non-maintainer) repositories whose code "
      "references org raw-URLs or the Cologne site. Queries: "
      + "; ".join(f"`{q}`" for q in CODE_SEARCH_QUERIES) + ". GitHub code search "
      "indexes only a subset of public code, so this is a **floor**, not a census.")
    A("")
    for full in sorted(external_repos):
        A(f"- [{full}](https://github.com/{full})")
    if not external_repos:
        A("- _(no external hits in the current cache)_")
    A("")

    A("## Tier 4 — Scholarly citations (estimated, representative)")
    A("")
    A("A **representative, non-exhaustive** set of published works that use or "
      "cite the Cologne dictionaries/lexicon (web + Scholar, 2020-2026). This is "
      "not a systematic citation count — no completeness is claimed.")
    A("")
    A("| Work | Year | Venue | Link |")
    A("|---|---|---|---|")
    for title, year, venue, url in CITATIONS:
        A(f"| {title} | {year} | {venue} | [link]({url}) |")
    A("")

    A("## Zenodo OBS-T download stats — BLOCKED (DOI mismatch)")
    A("")
    if zstatus == "mismatch":
        A("> ⚠️ **The OBS-T Zenodo DOI recorded in this repository is wrong.** "
          f"`10.5281/zenodo.{ZENODO_RECORD_ID}` — cited as the OBS-T dataset "
          "concept DOI in `CITATION.cff`, `reports/obs_t_paper_draft.md`, the "
          "roadmap, and `.ai_state.md` — resolves to an **unrelated topology "
          "preprint**, not the OBS-T Sanskrit dataset.")
        A("")
        A(f"- **Fetched title:** {zen.get('title')!r}")
        A(f"- **Fetched files:** {zen.get('files')}")
        A(f"- **Fetched creators:** {zen.get('creators')}")
        A(f"- **Record created:** {zen.get('created')} — a year *before* OBS-T's "
          "claimed 2026-07-01 mint, so the number is a transcription error, not a "
          "reassignment.")
        A(f"- **Its download/view stats** ({(zen.get('stats') or {}).get('downloads')} "
          f"downloads / {(zen.get('stats') or {}).get('views')} views) therefore "
          "belong to a stranger's paper and are **not reported as CDSL reach**.")
        A("")
        A("A Zenodo search for the OBS-T dataset under the maintainer's name "
          "returned no match, so the dataset may never have been minted, or was "
          "minted under a different (unknown) DOI. **This is an MG decision** "
          "(re-mint / correct the DOI across all files) — tracked in "
          "[`Uprava/GTD_NEXT_ACTIONS.md`](https://github.com/gasyoun/Uprava/blob/"
          "main/GTD_NEXT_ACTIONS.md). Once the correct record exists, add its id "
          "to `ZENODO_RECORD_ID` and re-run `--fetch` to populate this tier.")
    elif zstatus == "ok":
        st = zen.get("stats") or {}
        A(f"Record verified. Downloads: {st.get('downloads')} "
          f"({st.get('unique_downloads')} unique); views: {st.get('views')} "
          f"({st.get('unique_views')} unique). Fetched {fetched_at}.")
    else:
        A(f"Zenodo record unavailable in cache ({zdetail}). Run `--fetch`.")
    A("")

    A("## Reading")
    A("")
    A("- **Reach is real but invisible on GitHub's vanity surface.** ~"
      f"{total_stars} stars, yet {total_clones:,} clones in two weeks and "
      f"{len(KNOWN_CONSUMERS)} named downstream projects (PyCDSL, Ambuda, the "
      "Digital Pali Dictionary, StarDict-Sanskrit, Ashtadhyayi.com, ...). The "
      "audience is builders and scholars pulling data, not stargazers.")
    A("- **The dependents are the strongest scholar-facing evidence** — each is a "
      "URL-checkable project that chose CDSL as its lexical backbone.")
    A("- **Citations are under-counted here by design**; a systematic Scholar / "
      "OpenAlex sweep (API-gated) is the natural G6 extension.")
    A("- **Fix the OBS-T DOI before the paper ships** — the current DOI points at "
      "someone else's work.")
    A("")
    A("*Object of analysis: repository metadata, GitHub traffic, third-party code "
      "references, and publication citations of the org's output — in scope per "
      "`docs/BOUNDARY_RULES.md`. Roadmap: Workstream G6.*")

    OUT_MD.write_text("\n".join(L) + "\n", encoding="utf-8", newline="\n")

    print(f"wrote {OUT_MD}")
    print(f"wrote {OUT_CSV}")
    print(f"  stars {total_stars}  forks {total_forks}  "
          f"clones(sample) {total_clones}  dependents(ext) {len(external_repos)}  "
          f"consumers {len(KNOWN_CONSUMERS)}  citations {len(CITATIONS)}")
    print(f"  zenodo: {zstatus} — {zdetail}")
    if meta.get("warnings"):
        print(f"  cache warnings: {len(meta['warnings'])}")


if __name__ == "__main__":
    main()
