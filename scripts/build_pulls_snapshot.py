#!/usr/bin/env python3
"""Build the enriched PR snapshot `observatory/site/src/data/pulls.csv` (H7123).

Unlike `issues.csv` (state + closed_at only), this snapshot carries `merged_at`
and a `merged` boolean so merged and closed-unmerged pull requests are
distinguishable, plus the head branch name needed by the agent-lane
attribution rule (scripts/agent_lane.py).

Source : GitHub REST `repos/sanskrit-lexicon/<repo>/pulls?state=all` via
         `gh api`, with on-disk caching (reports/agent_lane_cache/, gitignored)
         and bounded retry — same discipline as the other snapshot fetchers.
Output : observatory/site/src/data/pulls.csv          (one row per org PR)
         observatory/site/src/data/pulls.meta.json   (fetch provenance)
         reports/agent_lane_review_sample.csv        (--samples: first review per sampled PR)
         reports/agent_lane_ci_sample.csv            (--samples: first check-run conclusion per sampled PR)

Offline analysis never calls this script; it only reads the committed CSV.
"""

from __future__ import annotations

import argparse
import csv
import json
import random
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _gh  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "observatory" / "site" / "src" / "data"
REPORTS = ROOT / "reports"
CACHE = REPORTS / "agent_lane_cache"
ORG = "sanskrit-lexicon"

FIELDS = [
    "repo", "number", "author", "title", "state", "draft",
    "created_at", "closed_at", "merged_at", "merged", "merged_by",
    "head_ref", "head_sha", "base_ref", "labels", "agent_marker_body",
    "comments", "review_comments", "commits", "additions", "deletions",
    "changed_files",
]

# Body-side agent markers (committed as a boolean only; raw bodies stay in the
# gitignored cache): handoff references (H###-H#####), co-author trailers,
# "generated with <tool>", and model names. Calibrated on the H7123
# 30-PR hand-checked adjudication sample.
BODY_MARKER = __import__("re").compile(
    r"(h\d{3,5}\b|handoff|generated with|co-authored-by:\s*(claude|copilot|gemini)"
    r"|claude code|claude bot|copilot|fable|opus|sonnet|gemini|deepseek|\bglm\b|grok)",
    __import__("re").IGNORECASE)


def pull_repos_from_issues() -> list[str]:
    with open(DATA / "issues.csv", newline="", encoding="utf-8") as fh:
        repos = {r["repo"] for r in csv.DictReader(fh) if r["kind"] == "PR"}
    return sorted(repos)


def fetch_repo_pulls(repo: str) -> tuple[list[dict], str]:
    """Fetch every PR page for one repo through the shared cached gh helper."""
    out: list[dict] = []
    page = 1
    while True:
        endpoint = (f"repos/{ORG}/{repo}/pulls?state=all"
                    f"&per_page=100&page={page}")
        data, warn = _gh.run_gh(endpoint, cache_dir=CACHE, cache_repo=repo,
                                cache_topic="pulls", retries=2, sleep=time.sleep)
        if data is None:
            return out, f"{repo}: {warn}"
        rows = data if isinstance(data, list) else []
        out.extend(rows)
        if len(rows) < 100:
            return out, ""
        page += 1
        if page > 20:  # 2000 PRs per repo — far beyond org reality
            return out, f"{repo}: page cap hit"


def to_row(repo: str, pr: dict) -> dict:
    def ts(v: object) -> str:
        return v if isinstance(v, str) else ""

    head = pr.get("head") or {}
    base = pr.get("base") or {}
    merged_by = pr.get("merged_by") or {}
    labels = "|".join(sorted(lb.get("name", "") for lb in pr.get("labels", [])
                             if lb.get("name")))
    return {
        "repo": repo,
        "number": pr.get("number", ""),
        "author": (pr.get("user") or {}).get("login", ""),
        "title": (pr.get("title") or "").replace("\r", " ").replace("\n", " "),
        "state": pr.get("state", ""),
        "draft": str(bool(pr.get("draft"))).lower(),
        "created_at": ts(pr.get("created_at")),
        "closed_at": ts(pr.get("closed_at")),
        "merged_at": ts(pr.get("merged_at")),
        "merged": str(bool(pr.get("merged_at"))).lower(),
        "merged_by": merged_by.get("login", "") if merged_by else "",
        "head_ref": head.get("ref", "") if head else "",
        "head_sha": head.get("sha", "") if head else "",
        "base_ref": base.get("ref", "") if base else "",
        "labels": labels,
        "agent_marker_body": str(bool(
            BODY_MARKER.search(pr.get("body") or ""))).lower(),
        "comments": pr.get("comments", ""),
        "review_comments": pr.get("review_comments", ""),
        "commits": pr.get("commits", ""),
        "additions": pr.get("additions", ""),
        "deletions": pr.get("deletions", ""),
        "changed_files": pr.get("changed_files", ""),
    }


def fetch_json(endpoint: str, cache_repo: str, topic: str):
    return _gh.run_gh(endpoint, cache_dir=CACHE, cache_repo=cache_repo,
                      cache_topic=topic, retries=2, sleep=time.sleep)


def build_samples(pull_rows: list[dict], per_lane: int, seed: int) -> None:
    """Stratified samples: first-review timestamp and first check-run conclusion.

    Lane labels here use the same ordered rule as agent_lane.py (imported
    lazily to keep this script standalone-safe). Bounded: `per_lane` PRs per
    lane, merged or closed only (metrics need resolved outcomes).
    """
    import agent_lane

    labelled = [r for r in pull_rows
                if r["merged"] == "true" or (r["state"] == "closed" and r["merged"] != "true")]
    by_lane: dict[str, list[dict]] = {}
    for r in labelled:
        by_lane.setdefault(agent_lane.lane_of(r), []).append(r)

    rng = random.Random(seed)  # noqa: S311 — measurement sampling, not cryptography
    sample = []
    for lane in ("human", "agent", "bot"):
        pool = sorted(by_lane.get(lane, []), key=lambda r: (r["repo"], int(r["number"])))
        sample.extend(rng.sample(pool, min(per_lane, len(pool))))

    review_rows, ci_rows = [], []
    with ThreadPoolExecutor(max_workers=6) as ex:
        review_futs = {ex.submit(fetch_json,
                                 f"repos/{ORG}/{r['repo']}/pulls/{r['number']}/reviews",
                                 r["repo"], f"reviews{r['number']}"): r for r in sample}
        ci_futs = {ex.submit(fetch_json,
                             f"repos/{ORG}/{r['repo']}/commits/{r['head_sha']}/check-runs?per_page=100",
                             r['repo'], f"checks{r['number']}"): r for r in sample
                   if r["head_sha"]}
        for fut, r in review_futs.items():
            data, warn = fut.result()
            first = ""
            if isinstance(data, list) and data:
                first = min((x.get("submitted_at") or "") for x in data if isinstance(x, dict))
            review_rows.append({**{k: r[k] for k in ("repo", "number", "author", "head_ref")},
                                "lane": agent_lane.lane_of(r), "created_at": r["created_at"],
                                "merged": r["merged"], "first_review_at": first,
                                "n_reviews": len(data) if isinstance(data, list) else "",
                                "warning": warn[:120]})
        for fut, r in ci_futs.items():
            data, warn = fut.result()
            first_conclusion, first_name, first_started = "", "", ""
            if isinstance(data, dict):
                runs = data.get("check_runs") or []
                if runs:
                    first_run = min(runs, key=lambda x: x.get("started_at") or "~")
                    first_conclusion = first_run.get("conclusion") or ""
                    first_name = first_run.get("name") or ""
                    first_started = first_run.get("started_at") or ""
            ci_rows.append({**{k: r[k] for k in ("repo", "number", "author", "head_ref")},
                            "lane": agent_lane.lane_of(r), "merged": r["merged"],
                            "first_check": first_name, "first_check_started_at": first_started,
                            "first_check_conclusion": first_conclusion,
                            "n_checks": data.get("total_count", "") if isinstance(data, dict) else "",
                            "warning": warn[:120]})

    for path, rows in ((REPORTS / "agent_lane_review_sample.csv", review_rows),
                       (REPORTS / "agent_lane_ci_sample.csv", ci_rows)):
        if rows:
            with open(path, "w", newline="", encoding="utf-8") as fh:
                w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
                w.writeheader()
                w.writerows(rows)
            print(f"wrote {path.relative_to(ROOT)} ({len(rows)} rows)")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--samples", type=int, default=0, metavar="N",
                    help="also fetch stratified samples of N PRs per lane "
                         "for review-latency and CI first-run measurement")
    ap.add_argument("--sample-seed", type=int, default=20261022)
    ap.add_argument("--refresh-cache", action="store_true")
    args = ap.parse_args()

    if args.refresh_cache and CACHE.exists():
        for f in CACHE.glob("*.json"):
            f.unlink()

    repos = pull_repos_from_issues()
    print(f"fetching PRs for {len(repos)} repos …")
    warnings: list[str] = []
    rows: list[dict] = []
    with ThreadPoolExecutor(max_workers=6) as ex:
        for repo, (prs, warn) in zip(repos, ex.map(fetch_repo_pulls, repos), strict=True):
            if warn:
                warnings.append(warn)
            rows.extend(to_row(repo, pr) for pr in prs)

    rows.sort(key=lambda r: (r["repo"], int(r["number"])))
    pulls_path = DATA / "pulls.csv"
    with open(pulls_path, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=FIELDS)
        w.writeheader()
        w.writerows(rows)
    print(f"wrote {pulls_path.relative_to(ROOT)} ({len(rows)} PRs)")

    # cross-check against issues.csv PR rows
    with open(DATA / "issues.csv", newline="", encoding="utf-8") as fh:
        issue_prs = {(r["repo"], r["number"]) for r in csv.DictReader(fh) if r["kind"] == "PR"}
    pull_keys = {(r["repo"], str(r["number"])) for r in rows}
    missing = sorted(issue_prs - pull_keys)
    extra = sorted(pull_keys - issue_prs)
    if missing:
        warnings.append(f"{len(missing)} issues.csv PRs missing from pulls.csv "
                        f"(e.g. {missing[:3]})")
    if extra:
        warnings.append(f"{len(extra)} pulls.csv rows absent from issues.csv "
                        f"(e.g. {extra[:3]})")

    meta = {
        "file": "pulls.csv",
        "rows": len(rows),
        "source": f"github rest: repos/{ORG}/<repo>/pulls?state=all via gh api",
        "fetched_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "purpose": "H7123 agent-lane census: merged_at/merged distinction + head branch for attribution",
        "warnings": warnings,
    }
    (DATA / "pulls.meta.json").write_text(
        json.dumps(meta, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {DATA / 'pulls.meta.json'}")
    for w in warnings:
        print(f"WARN {w}", file=sys.stderr)

    if args.samples:
        build_samples(rows, args.samples, args.sample_seed)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
