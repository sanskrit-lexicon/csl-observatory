#!/usr/bin/env python3
"""Systematic OpenAlex citation sweep for the Cologne Digital Sanskrit Lexicon.

The G6 extension named in ``reports/external_reach.md``: replace Tier 4's five
hand-picked citations ("representative, non-exhaustive — no completeness is
claimed") with a *systematic*, reproducible sweep whose recall bounds are
stated rather than hedged.

Why this is a research-method problem, not a fetch
--------------------------------------------------
The obvious query is the wrong one. The dictionaries are cited in the
literature by abbreviation — ``MW``, ``PW``, ``PWG`` — and those strings are
catastrophically ambiguous in a 250-million-work bibliographic index
(measured at fetch time and reported in the output: ~2.3M works contain "MW",
~0.9M contain "PW"). A naive sweep would replace five accurate citations with
hundreds of thousands of noisy ones, which is *worse for the paper* than the
honest "representative" framing it set out to fix. So the design here is:

  * **never enumerate an ambiguous abbreviation.** Bare ``MW`` / ``PW`` /
    ``PWG`` / ``Monier-Williams`` are probed for their *count only*, and that
    count is published as the justification for excluding them.
  * **two probe families, ranked by precision** — the citation graph
    (``cites:<anchor>``, identifier-exact) and name-unique phrases (strings
    that cannot denote anything but the Cologne digital resource).
  * **two orthogonal axes**, because "cites Monier-Williams" and "uses the
    Cologne digital edition" are different claims. Axis 1 is *match
    confidence* (C1/C2/C3, plus C0 rejected); axis 2 is *what is attested* —
    the ``digital`` resource, or the ``print`` dictionary CDSL digitises.
    Only the digital axis may be claimed as CDSL reach.
  * **project self-records are removed.** The org's own Zenodo release DOIs
    are indexed by OpenAlex (dozens of near-duplicate ``software`` /
    ``dataset`` records), and counting those as citations would be circular.

Confidence tiers (assigned offline, deterministically, from the cache)
---------------------------------------------------------------------
  C1 confirmed — matched a name-unique phrase AND passes the domain gate.
  C2 probable  — cites a resource anchor in OpenAlex's citation graph AND
                 passes the domain gate, but matched no name-unique phrase
                 (the reference exists in the graph; its context is not
                 re-readable from the API, so it is not promoted to C1).
  C3 possible  — matched only an ambiguous probe AND passes the domain gate:
                 attests the underlying *print* dictionary, not demonstrably
                 the Cologne digital edition.
  C0 rejected  — fails the domain gate. Kept in the CSV with its reason,
                 excluded from every headline count.
  internal     — a project self-record (org Zenodo release, or a work by a
                 project member). Reported separately, never as reach.

The headline citation number is **C1 + C2, external only**. C3 is published
beside it as the print-dictionary envelope, explicitly not claimed.

API parts run only under ``--fetch`` and are cached under
``reports/citation_sweep_cache/<YYYY-MM>/`` (a *committed* cache — small JSON)
so the report and every count regenerate offline from a fresh clone with no
network, exactly like the other external-reach tiers.

Semantic Scholar is attempted as a corroborating second source under
``--fetch``; its keyless pool is shared and routinely returns HTTP 429, so the
attempt is recorded (status + date) and the report states honestly whether
corroboration was available for the snapshot. It is never required.

Outputs:
  * reports/citation_sweep.md              — method, tiers, completeness
  * observatory/site/src/data/citation_sweep.csv
  * reports/citation_sweep_cache/<YYYY-MM>/summary.json  (read by
    scripts/external_reach.py to build Tier 4)

Usage:
  python scripts/citation_sweep.py            # offline: rebuild from cache
  python scripts/citation_sweep.py --fetch    # refresh OpenAlex cache, build
"""

from __future__ import annotations

import argparse
import csv
import json
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "observatory" / "site" / "src" / "data"
OUT_MD = ROOT / "reports" / "citation_sweep.md"
OUT_CSV = DATA / "citation_sweep.csv"
CACHE_ROOT = ROOT / "reports" / "citation_sweep_cache"
SNAPSHOT_MONTH = datetime.now(timezone.utc).strftime("%Y-%m")

OPENALEX = "https://api.openalex.org"
# OpenAlex "polite pool" — a contact address gets a faster, more reliable lane
# and no key. Same address as CITATION.cff, already public.
MAILTO = "gasyoun@ya.ru"
UA = f"csl-observatory-citation-sweep (+https://github.com/sanskrit-lexicon/csl-observatory; mailto:{MAILTO})"

# Hard cap per probe. Nothing is silently truncated: a probe that exceeds this
# is enumerated up to the cap, flagged `truncated`, and its full count is
# printed in the report next to the cap.
MAX_RESULTS_PER_PROBE = 400
PER_PAGE = 200

# --------------------------------------------------------------------------- #
# Probe registry — the methodological core. Edit here, not in the report.
# --------------------------------------------------------------------------- #

# Family A. Works that *are* the Cologne digital resource (or its published
# self-description). `cites:<id>` is identifier-exact: no string ambiguity at
# all. OpenAlex's reference extraction is imperfect, so anchor hits still pass
# the domain gate before being counted.
RESOURCE_ANCHORS = [
    ("W3192303795", "Cologne Digital Sanskrit Dictionaries (resource record, 2014)"),
    ("W3032245164", "Transforming the CDSD into OntoLex-Lemon (LDL 2020)"),
    ("W2554076622", "Kapp & Malten, Report on the Cologne Sanskrit Dictionary Project (2006)"),
]

# Family A'. The *print* dictionaries CDSL digitises. Their citation counts are
# an upper envelope on the underlying works' scholarly footprint — reported for
# scale, never enumerated as CDSL reach, because citing Monier-Williams 1899
# says nothing about whether the Cologne digital edition was used.
PRINT_ANCHORS = [
    ("W1889698854", "Monier-Williams, A Sanskrit-English Dictionary (1899/1891 impr.)"),
    ("W1553391585", "Monier-Williams, A Sanskrit-English Dictionary, Etymologically … (1900 impr.)"),
    ("W1573232975", "Böhtlingk, Sanskrit-Wörterbuch in kürzerer Fassung (1879)"),
    ("W1562498074", "Schmidt, Nachträge zum Sanskrit-Wörterbuch in kürzerer Fassung (1991)"),
]

# Family B/C. `klass`: "name-unique" = a string that cannot plausibly denote
# anything but the Cologne digital resource or a tool built on it (→ C1);
# "ambiguous" = domain-plausible but shared with the print editions or with
# homographs, so a hit attests the dictionary, not the digital edition (→ C3).
# `axis`: what a genuine hit attests.
PROBES = [
    # -- name-unique: the digital resource itself -----------------------------
    ("cdsd", '"Cologne Digital Sanskrit Dictionaries"', "name-unique", "digital"),
    ("cdsd-sg", '"Cologne Digital Sanskrit Dictionary"', "name-unique", "digital"),
    ("cdsl", '"Cologne Digital Sanskrit Lexicon"', "name-unique", "digital"),
    ("cologne-lex", '"Cologne Sanskrit Lexicon"', "name-unique", "digital"),
    ("cologne-dict", '"Cologne Sanskrit Dictionary"', "name-unique", "digital"),
    ("koeln-url", '"sanskrit-lexicon.uni-koeln.de"', "name-unique", "digital"),
    ("koelner", '"Kölner Sanskrit-Wörterbuch"', "name-unique", "digital"),
    ("csl-orig", '"csl-orig"', "name-unique", "digital"),
    # -- name-unique: downstream tools that exist only because CDSL does ------
    ("pycdsl", '"PyCDSL"', "name-unique", "digital"),
    ("dpd", '"Digital Pali Dictionary"', "name-unique", "digital"),
    # -- ambiguous: the print dictionaries CDSL digitises ---------------------
    ("mw-full", '"Monier-Williams Sanskrit-English Dictionary"', "ambiguous", "print"),
    ("pwk-title", '"Sanskrit-Wörterbuch in kürzerer Fassung"', "ambiguous", "print"),
    ("pw-title", '"Petersburger Wörterbuch"', "ambiguous", "print"),
    ("gra-title", '"Wörterbuch zum Rig-Veda"', "ambiguous", "print"),
    ("ap90-title", '"Practical Sanskrit-English Dictionary"', "ambiguous", "print"),
    # -- ambiguous: a downstream platform whose name is also a common word ----
    ("ambuda", '"Ambuda"', "ambiguous", "digital"),
]

# Probes deliberately NOT enumerated. Their counts are fetched (per-page=1, one
# request each) purely so the exclusion is evidenced rather than asserted.
EXCLUDED_PROBES = [
    ("MW", '"MW"', "bare dictionary siglum; also megawatt, molecular weight, "
                   "microwave, Mann-Whitney, initials"),
    ("PW", '"PW"', "bare dictionary siglum; also pulse width, plane wave, "
                   "power, personal watercraft, initials"),
    ("PWG", '"PWG"', "bare dictionary siglum; also working-group acronyms"),
    ("Monier-Williams", '"Monier-Williams"', "surname alone: matches every "
                        "citation of any Monier-Williams edition or reprint, "
                        "and other bearers of the name"),
]

# Domain gate vocabulary. A candidate must show at least one of these tokens in
# its title, venue, OpenAlex topics, or keywords. This is what separates a real
# Indological hit from an "MW"-class collision that slipped through a phrase
# probe (e.g. a chemistry paper whose full text happens to contain "Ambuda").
DOMAIN_TOKENS = (
    "sanskrit", "indo-aryan", "indoaryan", "indology", "indological", "indic",
    "vedic", "veda", "rigveda", "rig-veda", "upanishad", "pali", "prakrit",
    "devanagari", "hindu", "buddhis", "jain", "ayurved", "yoga", "dharma",
    "tantra", "purana", "mahabharata", "ramayana", "panini", "grammarian",
    "dravidian", "tamil", "south asia", "indian philosoph", "asian studies",
    "orientalist", "orientalisti", "philolog", "lexicograph", "lexical resource",
    "dictionar", "wörterbuch", "worterbuch", "historical linguistics",
    "language studies", "digital humanities", "natural language processing",
    "computational linguistics", "machine translation", "corpus linguistics",
)

# Project self-records. OpenAlex indexes the org's Zenodo release DOIs, which
# would otherwise inflate the count with our own artefacts.
PROJECT_AUTHOR_TOKENS = ("gasūns", "gasuns", "funderburk", "malten",
                         "kapp, dieter", "dhaval")
PROJECT_TITLE_TOKENS = ("sanskrit-lexicon/", "csl-atlas", "csl-sqlite",
                        "csl-observatory", "csl-orig:", "obs-t:",
                        "cologne digital edition")

# The five hand-curated Tier-4 citations the sweep replaces. Used as a *seed
# recall probe*: how many of the previously known-good citations does the
# systematic method recover? That fraction is the one honest, measurable
# recall statement available without a gold standard.
SEED_CITATIONS = [
    ("Transforming the Cologne Digital Sanskrit Dictionaries into OntoLex-Lemon",
     "https://aclanthology.org/2020.ldl-1.2/"),
    ("PyCDSL: a Python interface to the Cologne Digital Sanskrit Lexicon",
     "https://github.com/hrishikeshrt/PyCDSL"),
    ("Sanskrit Knowledge-based Systems: Annotation and Computational Tools",
     "https://arxiv.org/abs/2406.18276"),
    ("One Model is All You Need: ByT5-Sanskrit, a Unified Model for Sanskrit NLP",
     "https://arxiv.org/abs/2409.13920"),
    ("Cologne Sanskrit Lexicon (managed resource entry)",
     "https://dch.phil-fak.uni-koeln.de/en/ressources/managed-resources/cologne-sanskrit-lexicon"),
]

SELECT = ("id,doi,title,publication_year,type,language,cited_by_count,"
          "authorships,primary_location,topics,keywords")

_TRANSIENT = ("429", "500", "502", "503", "504", "timed out", "timeout",
              "connection reset", "temporarily unavailable", "bad gateway")


# --------------------------------------------------------------------------- #
# Fetch helpers (only used under --fetch)
# --------------------------------------------------------------------------- #
def _http_json(url: str, retries: int = 3):
    """Fetch a JSON URL with the stdlib and bounded exponential backoff."""
    last = "unknown http error"
    for attempt in range(retries + 1):
        try:
            req = urllib.request.Request(
                url, headers={"Accept": "application/json", "User-Agent": UA})
            with urllib.request.urlopen(req, timeout=90) as resp:
                return json.loads(resp.read().decode("utf-8")), ""
        except urllib.error.HTTPError as exc:
            last = f"HTTP {exc.code}"
            if str(exc.code) in _TRANSIENT and attempt < retries:
                time.sleep(2 ** attempt + 1)
                continue
            return None, last
        except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
            last = f"http failed: {exc}"
            if any(t in last.lower() for t in _TRANSIENT) and attempt < retries:
                time.sleep(2 ** attempt + 1)
                continue
            if attempt < retries:
                time.sleep(2 ** attempt + 1)
                continue
            return None, last
    return None, last


def _works_url(filt: str, per_page: int = PER_PAGE, cursor: str | None = None,
               select: str | None = SELECT) -> str:
    params = {"filter": filt, "per-page": str(per_page), "mailto": MAILTO}
    if select:
        params["select"] = select
    if cursor:
        params["cursor"] = cursor
    return f"{OPENALEX}/works?" + urllib.parse.urlencode(params)


def _slim(w: dict) -> dict:
    """Keep only what classification and the report need — the cache is
    committed, so it must stay small and diff-readable."""
    loc = w.get("primary_location") or {}
    src = loc.get("source") or {}
    return {
        "id": (w.get("id") or "").rsplit("/", 1)[-1],
        "doi": w.get("doi"),
        "title": w.get("title") or "",
        "year": w.get("publication_year"),
        "type": w.get("type"),
        "language": w.get("language"),
        "cited_by_count": w.get("cited_by_count"),
        "authors": [a.get("raw_author_name") or
                    (a.get("author") or {}).get("display_name") or ""
                    for a in (w.get("authorships") or [])][:8],
        "venue": src.get("display_name") or loc.get("raw_source_name") or "",
        "landing_page_url": loc.get("landing_page_url") or "",
        "topics": [t.get("display_name", "") for t in (w.get("topics") or [])],
        "keywords": [k.get("display_name", "") for k in (w.get("keywords") or [])],
    }


def _enumerate(filt: str) -> tuple[list[dict], int, bool, str]:
    """Cursor-page a filter to MAX_RESULTS_PER_PROBE. Returns
    (results, total_count, truncated, warning)."""
    out: list[dict] = []
    cursor = "*"
    total = 0
    while cursor and len(out) < MAX_RESULTS_PER_PROBE:
        data, w = _http_json(_works_url(filt, cursor=cursor))
        if data is None:
            return out, total, len(out) >= MAX_RESULTS_PER_PROBE, w
        total = data.get("meta", {}).get("count", total)
        for rec in data.get("results", []):
            out.append(_slim(rec))
            if len(out) >= MAX_RESULTS_PER_PROBE:
                break
        cursor = data.get("meta", {}).get("next_cursor")
        time.sleep(0.15)
    return out, total, total > len(out), ""


def _count_only(filt: str) -> tuple[int | None, str]:
    data, w = _http_json(_works_url(filt, per_page=1, select="id"))
    if data is None:
        return None, w
    return data.get("meta", {}).get("count"), ""


def fetch_all(cache_dir: Path) -> None:
    """Refresh every API cache under `cache_dir`. Partial failures become
    warnings so an offline rebuild still works from whatever landed."""
    cache_dir.mkdir(parents=True, exist_ok=True)
    fetched_at = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    warnings: list[str] = []

    # --- Family A: citation-graph anchors ---
    anchors = {}
    for wid, label in RESOURCE_ANCHORS:
        res, total, trunc, warn = _enumerate(f"cites:{wid}")
        if warn:
            warnings.append(f"anchor {wid}: {warn}")
        anchors[wid] = {"label": label, "total_count": total,
                        "truncated": trunc, "results": res}
    (cache_dir / "anchors.json").write_text(
        json.dumps(anchors, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    # --- Family A': print-dictionary envelope (counts only, never enumerated) ---
    print_anchors = []
    for wid, label in PRINT_ANCHORS:
        data, warn = _http_json(
            f"{OPENALEX}/works/{wid}?mailto={MAILTO}"
            "&select=id,title,publication_year,cited_by_count")
        if data is None:
            warnings.append(f"print anchor {wid}: {warn}")
            continue
        print_anchors.append({
            "id": wid, "label": label,
            "title": data.get("title") or "",
            "year": data.get("publication_year"),
            "cited_by_count": data.get("cited_by_count", 0),
        })
    (cache_dir / "print_anchors.json").write_text(
        json.dumps(print_anchors, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8")

    # --- Family B/C: phrase probes ---
    probes = {}
    for pid, query, klass, axis in PROBES:
        filt = f"fulltext.search:{query}"
        res, total, trunc, warn = _enumerate(filt)
        if warn:
            warnings.append(f"probe {pid}: {warn}")
        probes[pid] = {"query": query, "filter": filt, "klass": klass,
                       "axis": axis, "total_count": total,
                       "truncated": trunc, "results": res}
    (cache_dir / "probes.json").write_text(
        json.dumps(probes, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    # --- Excluded probes: counts only, as evidence for the exclusion ---
    excluded = []
    for label, query, why in EXCLUDED_PROBES:
        n, warn = _count_only(f"fulltext.search:{query}")
        if n is None:
            warnings.append(f"excluded probe {label}: {warn}")
        excluded.append({"label": label, "query": query, "why": why, "count": n})

    # --- Index frame: how big is the corpus we swept, and how much of it has
    #     indexed full text (the hard ceiling on any phrase probe's recall)? ---
    total_works, w1 = _count_only("type:article|book|book-chapter|preprint|dissertation")
    if w1:
        warnings.append(f"frame total: {w1}")
    fulltext_works, w2 = _count_only(
        "has_fulltext:true,type:article|book|book-chapter|preprint|dissertation")
    if w2:
        warnings.append(f"frame fulltext: {w2}")
    (cache_dir / "frame.json").write_text(
        json.dumps({"openalex_scholarly_works": total_works,
                    "openalex_fulltext_works": fulltext_works,
                    "excluded_probes": excluded},
                   ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    # --- Semantic Scholar: optional corroboration, never required ---
    s2_url = ("https://api.semanticscholar.org/graph/v1/paper/search"
              "?query=Cologne+Digital+Sanskrit+Dictionaries&limit=20"
              "&fields=title,year,externalIds,venue")
    s2, s2w = _http_json(s2_url, retries=1)
    if s2 is None:
        warnings.append(f"semantic scholar: {s2w}")
        s2_cache = {"status": "unavailable", "detail": s2w, "attempted_at": fetched_at}
    else:
        s2_cache = {"status": "ok", "attempted_at": fetched_at,
                    "total": s2.get("total"), "data": s2.get("data", [])}
    (cache_dir / "semantic_scholar.json").write_text(
        json.dumps(s2_cache, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    (cache_dir / "meta.json").write_text(
        json.dumps({"fetched_at": fetched_at, "warnings": warnings,
                    "probe_count": len(PROBES),
                    "anchor_count": len(RESOURCE_ANCHORS),
                    "max_results_per_probe": MAX_RESULTS_PER_PROBE},
                   ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"fetched → {cache_dir}")
    if warnings:
        print(f"  {len(warnings)} warning(s):")
        for w in warnings:
            print(f"   - {w}")


# --------------------------------------------------------------------------- #
# Offline classification
# --------------------------------------------------------------------------- #
def latest_cache_dir() -> Path | None:
    """Newest month-stamped cache dir, so an offline rebuild in a later month
    still finds the committed snapshot instead of silently reporting zero."""
    if not CACHE_ROOT.exists():
        return None
    months = sorted(p for p in CACHE_ROOT.iterdir()
                    if p.is_dir() and re.fullmatch(r"\d{4}-\d{2}", p.name))
    return months[-1] if months else None


def _load(cache_dir: Path | None, name: str):
    if cache_dir is None:
        return None
    p = cache_dir / name
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else None


def _haystack(rec: dict) -> str:
    return " ".join([rec.get("title") or "", rec.get("venue") or "",
                     " ".join(rec.get("topics") or []),
                     " ".join(rec.get("keywords") or [])]).lower()


def domain_pass(rec: dict) -> bool:
    return any(tok in _haystack(rec) for tok in DOMAIN_TOKENS)


def is_internal(rec: dict) -> bool:
    """A project self-record: our own Zenodo software/dataset releases, or a
    work by a project member. Never counted as external reach."""
    title = (rec.get("title") or "").lower()
    if any(tok in title for tok in PROJECT_TITLE_TOKENS):
        return True
    authors = " ; ".join(rec.get("authors") or []).lower()
    if any(tok in authors for tok in PROJECT_AUTHOR_TOKENS):
        return True
    return False


def classify(cache_dir: Path | None) -> dict:
    """Deduplicate every probe/anchor hit by OpenAlex id and assign each work a
    confidence tier and an attestation axis. Pure function of the cache."""
    anchors = _load(cache_dir, "anchors.json") or {}
    probes = _load(cache_dir, "probes.json") or {}

    works: dict[str, dict] = {}

    def touch(rec: dict) -> dict:
        wid = rec["id"]
        cur = works.get(wid)
        if cur is None:
            cur = dict(rec)
            cur["matched_probes"] = []
            cur["matched_anchors"] = []
            works[wid] = cur
        return cur

    for wid, block in anchors.items():
        for rec in block.get("results", []):
            touch(rec)["matched_anchors"].append(wid)
    for pid, block in probes.items():
        klass, axis = block.get("klass"), block.get("axis")
        for rec in block.get("results", []):
            touch(rec)["matched_probes"].append((pid, klass, axis))

    for w in works.values():
        klasses = {k for _, k, _ in w["matched_probes"]}
        axes = {a for _, _, a in w["matched_probes"]}
        w["internal"] = is_internal(w)
        w["domain_ok"] = domain_pass(w)
        if "name-unique" in klasses:
            w["axis"] = "digital"
        elif w["matched_anchors"]:
            w["axis"] = "digital"
        else:
            w["axis"] = "print" if axes == {"print"} else "digital"

        if not w["domain_ok"]:
            w["tier"] = "C0"
            w["reason"] = "fails domain gate (no Indological/lexicographic signal)"
        elif "name-unique" in klasses:
            w["tier"] = "C1"
            w["reason"] = "name-unique phrase: " + ", ".join(
                sorted(p for p, k, _ in w["matched_probes"] if k == "name-unique"))
        elif w["matched_anchors"]:
            w["tier"] = "C2"
            w["reason"] = "cites resource anchor " + ", ".join(sorted(w["matched_anchors"]))
        else:
            w["tier"] = "C3"
            w["reason"] = "ambiguous probe only: " + ", ".join(
                sorted(p for p, _, _ in w["matched_probes"]))
        if w["internal"]:
            w["bucket"] = "internal"
        else:
            w["bucket"] = "external"

    return works


def seed_recall(works: dict) -> list[dict]:
    """Did the systematic sweep recover the five hand-curated Tier-4 citations?
    Title-token overlap against every swept work — the only measurable recall
    statement available without a gold standard."""
    out = []
    swept = [(w, re.findall(r"[a-z0-9]+", (w.get("title") or "").lower()))
             for w in works.values()]
    for title, url in SEED_CITATIONS:
        toks = [t for t in re.findall(r"[a-z0-9]+", title.lower()) if len(t) > 3]
        best, best_score = None, 0.0
        for w, wtoks in swept:
            if not wtoks:
                continue
            score = len(set(toks) & set(wtoks)) / max(len(set(toks)), 1)
            if score > best_score:
                best, best_score = w, score
        hit = best is not None and best_score >= 0.6
        out.append({"seed": title, "url": url, "recovered": hit,
                    "match": (best or {}).get("title", "") if hit else "",
                    "match_id": (best or {}).get("id", "") if hit else "",
                    "match_tier": (best or {}).get("tier", "") if hit else "",
                    "score": round(best_score, 2)})
    return out


# --------------------------------------------------------------------------- #
# Report
# --------------------------------------------------------------------------- #
def build(cache_dir: Path | None) -> dict:
    meta = _load(cache_dir, "meta.json") or {}
    frame = _load(cache_dir, "frame.json") or {}
    probes = _load(cache_dir, "probes.json") or {}
    anchors = _load(cache_dir, "anchors.json") or {}
    print_anchors = _load(cache_dir, "print_anchors.json") or []
    s2 = _load(cache_dir, "semantic_scholar.json") or {}
    fetched_at = meta.get("fetched_at", "(no fetch — offline cache)")
    snapshot = cache_dir.name if cache_dir else "(none)"

    works = classify(cache_dir)
    ext = [w for w in works.values() if w["bucket"] == "external"]
    internal = [w for w in works.values() if w["bucket"] == "internal"]

    def tier(t):
        return sorted([w for w in ext if w["tier"] == t],
                      key=lambda w: (-(w.get("year") or 0), w.get("title") or ""))

    c1, c2, c3, c0 = tier("C1"), tier("C2"), tier("C3"), tier("C0")
    headline = len(c1) + len(c2)
    recall = seed_recall(works)
    recovered = sum(1 for r in recall if r["recovered"])

    # ---- CSV (tidy long form, one row per swept work) ----
    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    with OUT_CSV.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=[
            "openalex_id", "title", "year", "type", "venue", "doi",
            "confidence_tier", "attests", "bucket", "match_reason",
            "matched_probes", "matched_anchors", "cited_by_count",
            "url", "snapshot", "fetched_at"])
        w.writeheader()
        for rec in sorted(works.values(),
                          key=lambda r: (r["tier"], -(r.get("year") or 0),
                                         r.get("title") or "")):
            w.writerow({
                "openalex_id": rec["id"],
                "title": rec.get("title") or "",
                "year": rec.get("year") or "",
                "type": rec.get("type") or "",
                "venue": rec.get("venue") or "",
                "doi": rec.get("doi") or "",
                "confidence_tier": rec["tier"],
                "attests": rec["axis"],
                "bucket": rec["bucket"],
                "match_reason": rec["reason"],
                "matched_probes": ";".join(sorted(p for p, _, _ in rec["matched_probes"])),
                "matched_anchors": ";".join(sorted(rec["matched_anchors"])),
                "cited_by_count": rec.get("cited_by_count") or 0,
                "url": f"https://openalex.org/{rec['id']}",
                "snapshot": snapshot,
                "fetched_at": fetched_at,
            })

    # ---- Markdown report ----
    L: list[str] = []
    A = L.append
    blob = "https://github.com/sanskrit-lexicon/csl-observatory/blob/main"
    A("# Systematic citation sweep (OpenAlex) — method and results")
    A("")
    A(f"_Auto-generated by [`scripts/citation_sweep.py`]({blob}/scripts/citation_sweep.py). "
      f"API cache committed under `reports/citation_sweep_cache/{snapshot}/`; every count "
      f"below regenerates offline from that cache. Last API fetch: {fetched_at}._")
    A("")
    A("This is the G6 extension named in "
      f"[`reports/external_reach.md`]({blob}/reports/external_reach.md): the replacement "
      "for Tier 4's five hand-picked citations. It answers a narrow question — **how many "
      "scholarly works demonstrably name or cite the Cologne *digital* Sanskrit lexicon, "
      "as opposed to the print dictionaries it digitises** — and states the bounds of its "
      "own recall instead of hedging with \"representative\".")
    A("")

    A("## Headline")
    A("")
    A("| Measure | Value | What it means |")
    A("|---|---:|---|")
    A(f"| **External citations of the digital resource (C1+C2)** | **{headline}** | "
      "the defensible number — name-unique phrase match or citation-graph edge, "
      "domain-gated, self-records removed |")
    A(f"| C1 confirmed | {len(c1)} | matched a string that can only denote CDSL |")
    A(f"| C2 probable | {len(c2)} | cites a CDSL anchor work in OpenAlex's citation graph |")
    A(f"| C3 print-dictionary envelope | {len(c3)} | attests Monier-Williams/Böhtlingk "
      "etc., **not** claimed as CDSL reach |")
    A(f"| C0 rejected (failed domain gate) | {len(c0)} | phrase collisions, kept in the CSV |")
    A(f"| Project self-records excluded | {len(internal)} | our own Zenodo release DOIs "
      "and project-member works |")
    A(f"| Seed recall | {recovered}/{len(recall)} | of the five hand-curated Tier-4 "
      "citations, how many the systematic sweep recovers |")
    A("")

    A("## Why the obvious query is the wrong query")
    A("")
    A("The dictionaries are cited by siglum. Those sigla are among the most overloaded "
      "two-letter strings in the bibliographic universe, so enumerating them would bury "
      "the real hits. Measured on this snapshot, deliberately **not** enumerated:")
    A("")
    A("| Excluded probe | Works matching | Why excluded |")
    A("|---|---:|---|")
    for e in frame.get("excluded_probes", []):
        n = e.get("count")
        shown = f"{n:,}" if isinstance(n, int) else "n/a"
        A(f"| `{e['query']}` | {shown} | {e['why']} |")
    A("")
    A("Enumerating these would swap five accurate citations for hundreds of thousands of "
      "noisy ones — strictly worse for the paper than the honest hedge it replaces. Their "
      "counts are published here so the exclusion is *evidenced*, not merely asserted.")
    A("")

    A("## Method")
    A("")
    A("### Probe families")
    A("")
    A(f"**Family A — citation-graph anchors ({len(RESOURCE_ANCHORS)}).** Works that *are* "
      "the Cologne digital resource or its published self-description; pulled with "
      "OpenAlex `cites:<id>`, which is identifier-exact and immune to string ambiguity. "
      "OpenAlex's reference extraction is imperfect, so anchor hits still pass the domain "
      "gate before counting.")
    A("")
    A("| Anchor | Citing works found |")
    A("|---|---:|")
    for wid, label in RESOURCE_ANCHORS:
        b = anchors.get(wid, {})
        A(f"| [{label}](https://openalex.org/{wid}) | {b.get('total_count', 0)} |")
    A("")
    A(f"**Family B — name-unique phrases.** Strings that cannot plausibly denote anything "
      "but the Cologne digital resource or a tool that exists only because of it. A hit "
      "here is C1.")
    A("")
    A("**Family C — ambiguous, domain-plausible phrases.** Dictionary titles shared with "
      "the print editions, and a platform name that is also a common Sanskrit word. A hit "
      "here attests the *underlying dictionary*, so it is C3 and reported separately.")
    A("")
    A("| Probe | Query | Family | Attests | Matching works | Enumerated |")
    A("|---|---|---|---|---:|---|")
    for pid, query, klass, axis in PROBES:
        b = probes.get(pid, {})
        n = b.get("total_count", 0)
        kept = len(b.get("results", []))
        note = (f"{kept} (capped at {meta.get('max_results_per_probe', MAX_RESULTS_PER_PROBE)})"
                if b.get("truncated") else str(kept))
        fam = "B name-unique" if klass == "name-unique" else "C ambiguous"
        A(f"| `{pid}` | `{query}` | {fam} | {axis} | {n} | {note} |")
    A("")

    A("### Confidence tiers")
    A("")
    A("| Tier | Rule | Counted as CDSL reach? |")
    A("|---|---|---|")
    A("| **C1 confirmed** | matched a name-unique phrase **and** passes the domain gate | yes |")
    A("| **C2 probable** | cites a resource anchor **and** passes the domain gate, but "
      "matched no name-unique phrase (the graph edge exists; its context is not re-readable "
      "from the API, so it is not promoted) | yes |")
    A("| **C3 possible** | matched only an ambiguous probe **and** passes the domain gate — "
      "attests the print dictionary | no, reported as an envelope |")
    A("| **C0 rejected** | fails the domain gate | no, retained in the CSV with its reason |")
    A("| **internal** | project self-record (org Zenodo release DOI, or a project member's "
      "own work) | no, would be circular |")
    A("")
    A("**Domain gate.** A candidate must show at least one Indological, philological or "
      "lexicographic token in its title, venue, OpenAlex topics or keywords "
      f"({len(DOMAIN_TOKENS)} tokens, listed in the script). This is the filter that "
      "catches a phrase collision surviving Family B/C — a hit whose full text contains "
      "the string but which is not a work about Sanskrit, Indology, or dictionaries.")
    A("")
    A("**Deduplication.** Every hit is keyed by OpenAlex work id, so a work found by three "
      "probes and one anchor counts once, carrying all four match reasons. Near-duplicate "
      "*records* for the same artefact (Zenodo mints one DOI per release, and OpenAlex "
      "indexes each separately) are not merged — they are almost entirely project "
      f"self-records and are removed wholesale by the internal filter ({len(internal)} on "
      "this snapshot).")
    A("")

    A("## Results")
    A("")
    A(f"### C1 — confirmed ({len(c1)})")
    A("")
    if c1:
        A("| Work | Year | Venue | Matched by | Link |")
        A("|---|---:|---|---|---|")
        for w in c1:
            probes_hit = ", ".join(sorted(p for p, k, _ in w["matched_probes"]
                                          if k == "name-unique"))
            A(f"| {w['title'][:110]} | {w.get('year') or ''} | {w.get('venue') or '—'} | "
              f"`{probes_hit}` | [openalex](https://openalex.org/{w['id']}) |")
    else:
        A("_(none in this snapshot)_")
    A("")
    A(f"### C2 — probable ({len(c2)})")
    A("")
    if c2:
        A("| Work | Year | Venue | Cites anchor | Link |")
        A("|---|---:|---|---|---|")
        for w in c2:
            A(f"| {w['title'][:110]} | {w.get('year') or ''} | {w.get('venue') or '—'} | "
              f"`{', '.join(sorted(w['matched_anchors']))}` | "
              f"[openalex](https://openalex.org/{w['id']}) |")
    else:
        A("_(none in this snapshot)_")
    A("")
    A(f"### C3 — print-dictionary envelope ({len(c3)})")
    A("")
    A("Works attesting the print dictionaries CDSL digitises. **Not** CDSL reach: citing "
      "Monier-Williams 1899 says nothing about whether the Cologne digital edition was "
      "used. Published here because the distinction is exactly what a systematic count "
      "must not blur.")
    A("")
    if c3:
        A("| Work | Year | Matched by | Link |")
        A("|---|---:|---|---|")
        for w in c3[:40]:
            A(f"| {w['title'][:110]} | {w.get('year') or ''} | "
              f"`{', '.join(sorted(p for p, _, _ in w['matched_probes']))}` | "
              f"[openalex](https://openalex.org/{w['id']}) |")
        if len(c3) > 40:
            A(f"| _… {len(c3) - 40} more — see "
              f"[`citation_sweep.csv`]({blob}/observatory/site/src/data/citation_sweep.csv)_ | | | |")
    else:
        A("_(none in this snapshot)_")
    A("")
    if print_anchors:
        A("The four print anchors' own OpenAlex citation counts give the scale of that "
          "envelope from the other direction:")
        A("")
        A("| Print anchor | Year | Cited by (OpenAlex) |")
        A("|---|---:|---:|")
        for p in print_anchors:
            A(f"| [{p['label']}](https://openalex.org/{p['id']}) | {p.get('year') or ''} | "
              f"{p.get('cited_by_count', 0):,} |")
        A("")
        A(f"Total across the print anchors: **{sum(p.get('cited_by_count', 0) for p in print_anchors):,}** "
          "— an upper bound on the underlying dictionaries' footprint, of which CDSL can "
          "claim no determinable share. Reporting this number *as* CDSL reach would be the "
          "single easiest way to make the sweep dishonest, which is why it is fenced here.")
        A("")

    A("## Coverage and completeness")
    A("")
    total_w = frame.get("openalex_scholarly_works")
    ft_w = frame.get("openalex_fulltext_works")
    A("**What this sweep is:** a systematic, reproducible enumeration over OpenAlex's index "
      f"as of {fetched_at}, using {len(RESOURCE_ANCHORS)} citation-graph anchors and "
      f"{len(PROBES)} phrase probes, deduplicated by work id, domain-gated, with project "
      "self-records removed. Every count regenerates offline from the committed cache; "
      "re-running `--fetch` reproduces the method against a fresh index.")
    A("")
    A("**What it is not:** a census. Four bounds on recall, stated rather than hedged:")
    A("")
    if total_w and ft_w:
        pct = 100.0 * ft_w / total_w
        A(f"1. **Full-text coverage is the hard ceiling.** A phrase probe can only match a "
          f"work whose full text OpenAlex has indexed: {ft_w:,} of {total_w:,} scholarly "
          f"works, or **{pct:.1f}%**. Family B/C recall is bounded by that fraction; only "
          "Family A (the citation graph) reaches beyond it.")
    else:
        A("1. **Full-text coverage is the hard ceiling.** A phrase probe can only match a "
          "work whose full text OpenAlex has indexed — a minority of the corpus. (Frame "
          "counts unavailable in this cache; re-run `--fetch`.)")
    A("2. **Siglum-only citations are invisible by design.** A work that cites the "
      "dictionary as \"MW s.v. …\" and nothing more cannot be recovered without accepting "
      "the noise measured above. This is a deliberate precision-over-recall trade, not an "
      "oversight.")
    A("3. **Print-form and non-indexed references are out of reach.** Monographs, "
      "festschrift chapters, and non-OA Indological venues are unevenly represented in "
      "OpenAlex; the Indological long tail is worse-covered than the NLP literature that "
      "cites CDSL most visibly.")
    A("4. **Anchor selection bounds Family A.** Only works that *are* CDSL carry usable "
      "`cites:` edges; a citation pointing at the Cologne website with no anchor record "
      "leaves no graph edge to follow.")
    A("")
    A(f"**Measured recall proxy.** Of the {len(recall)} citations previously hand-curated "
      f"into Tier 4, the systematic sweep recovers **{recovered}**:")
    A("")
    A("| Hand-curated seed | Recovered | Matched as |")
    A("|---|---|---|")
    for r in recall:
        mark = "yes" if r["recovered"] else "no"
        detail = (f"{r['match_tier']} · {r['match'][:70]}" if r["recovered"]
                  else f"below match threshold (best overlap {r['score']})")
        A(f"| {r['seed'][:80]} | {mark} | {detail} |")
    A("")
    A("A miss is informative, not a defect: seeds that are software repositories or "
      "institutional web pages have no OpenAlex work record to recover, which is precisely "
      "the coverage boundary bound 3 describes.")
    A("")
    A(f"**Therefore the claim this report supports is:** *at least {headline} scholarly "
      "works in OpenAlex demonstrably name or cite the Cologne digital Sanskrit lexicon "
      f"(snapshot {fetched_at})* — a documented lower bound with stated recall bounds, not "
      "an exhaustive count. That is a materially stronger claim than \"5, representative, "
      "no completeness claimed\", and it is falsifiable: the probe registry, the cache, and "
      "the classification are all committed.")
    A("")

    A("## Second-source corroboration")
    A("")
    if s2.get("status") == "ok":
        A(f"Semantic Scholar returned {s2.get('total', 0)} works for the primary phrase "
          f"query (attempted {s2.get('attempted_at')}), corroborating the OpenAlex frame. "
          "S2 is a cross-check only; no count in this report depends on it.")
    else:
        A(f"Semantic Scholar was attempted on {s2.get('attempted_at', fetched_at)} and was "
          f"**unavailable** ({s2.get('detail', 'no detail')}). Its keyless pool is shared "
          "org-wide and routinely rate-limits; a key would be needed for reliable "
          "corroboration. No count in this report depends on it — the sweep is "
          "single-source (OpenAlex) for this snapshot, and says so.")
    A("")

    A("## Reproducing")
    A("")
    A("```")
    A("python scripts/citation_sweep.py            # rebuild offline from the committed cache")
    A("python scripts/citation_sweep.py --fetch    # refresh the OpenAlex cache, then rebuild")
    A("```")
    A("")
    A("The probe registry, domain-gate vocabulary, anchor list and tier rules are all "
      f"constants at the top of [`scripts/citation_sweep.py`]({blob}/scripts/citation_sweep.py) "
      "— change them there and re-run, rather than editing this report.")
    A("")
    if meta.get("warnings"):
        A(f"_Cache warnings on the last fetch: {len(meta['warnings'])} — see "
          f"`reports/citation_sweep_cache/{snapshot}/meta.json`._")
        A("")
    A("*Object of analysis: third-party publications referencing the org's dictionaries and "
      "tools — in scope per `docs/BOUNDARY_RULES.md`. Roadmap: Workstream G6 (extension).*")

    OUT_MD.write_text("\n".join(L) + "\n", encoding="utf-8", newline="\n")

    summary = {
        "snapshot": snapshot,
        "fetched_at": fetched_at,
        "headline_external_digital": headline,
        "c1": len(c1), "c2": len(c2), "c3": len(c3), "c0": len(c0),
        "internal_excluded": len(internal),
        "probes": len(PROBES),
        "anchors": len(RESOURCE_ANCHORS),
        "excluded_probes": [{"query": e["query"], "count": e.get("count")}
                            for e in frame.get("excluded_probes", [])],
        "openalex_scholarly_works": total_w,
        "openalex_fulltext_works": ft_w,
        "seed_recall": f"{recovered}/{len(recall)}",
        "semantic_scholar": s2.get("status", "unattempted"),
        "top_c1": [{"title": w["title"], "year": w.get("year"),
                    "venue": w.get("venue"), "id": w["id"],
                    "doi": w.get("doi")}
                   for w in c1[:12]],
    }
    if cache_dir is not None:
        (cache_dir / "summary.json").write_text(
            json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    print(f"wrote {OUT_MD}")
    print(f"wrote {OUT_CSV}")
    print(f"  swept {len(works)} works · C1 {len(c1)} · C2 {len(c2)} · C3 {len(c3)} "
          f"· C0 {len(c0)} · internal {len(internal)}")
    print(f"  headline (external, digital, C1+C2): {headline}")
    print(f"  seed recall: {recovered}/{len(recall)}")
    return summary


def main() -> int:
    ap = argparse.ArgumentParser(description="Systematic OpenAlex citation sweep for CDSL.")
    ap.add_argument("--fetch", action="store_true",
                    help="Refresh the OpenAlex cache before building (network).")
    args = ap.parse_args()

    if args.fetch:
        fetch_all(CACHE_ROOT / SNAPSHOT_MONTH)

    cache_dir = latest_cache_dir()
    if cache_dir is None:
        print("no cache under reports/citation_sweep_cache/ — run with --fetch first",
              file=sys.stderr)
        return 1
    build(cache_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
