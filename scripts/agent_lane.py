#!/usr/bin/env python3
"""Agent-lane census over the org PR snapshot (H7123).

Splits every org pull request into three lanes — `bot`, `agent`
(human-via-agent, marker-based), and `human` (direct) — and measures per
lane: merge rate, time-to-merge, review latency (stratified committed
sample), CI first-run failure rate (stratified committed sample), revert
rate, and follow-up-defect rate. Also renders a measured policy verdict on
whether the `no-bot` label and the weekly human-activity feed kept
maintainer threads clean.

Inputs  (all committed, offline):
  observatory/site/src/data/pulls.csv                    (build_pulls_snapshot.py)
  observatory/site/src/data/issues.csv                   (label census context)
  reports/agent_lane_review_sample.csv                   (optional, review latency)
  reports/agent_lane_ci_sample.csv                       (optional, CI first-run)
Outputs:
  reports/agent_lane.md          — the report
  reports/agent_lane.csv         — per-lane metrics (the regression-gate artefact)

Attribution rule (ordered, first match wins; calibrated on the hand-checked
30-PR stratified sample `reports/agent_lane_adjudication.csv` — the initial
`h\\d{4}`-based rule misclassified 6/30, all agent→human undercounts from
3-digit early-2026 handoff IDs, body-only markers, and batch-deploy branches):
  1. bot     — author login ends with `[bot]` (dependabot, renovate, …).
  2. agent   — human author AND an explicit agent marker:
       a. head branch carries a handoff ID  — `h\\d{3,5}` (e.g. `h5602-drain`,
          `h543-yo-sweep`, `docs/h2012-t4-acc`), the worktree convention, or
       b. head branch uses an agent-tool / batch-deploy prefix (`codex/`,
          `claude/`, `copilot/`, `gemini/`, `cursor/`, `aider/`,
          `cologne-batch-deploy/`), or
       c. PR title carries a handoff ID `(H\\d{3,5})`, or
       d. PR title names an AI model/agent (Claude, Codex, Fable, Opus,
          Sonnet, Gemini, GLM, DeepSeek), or
       e. the PR body carries an agent marker (`agent_marker_body` boolean in
          the snapshot: handoff refs, co-author trailers, "generated with",
          model names).
  3. human   — everything else (default; unmarked human work).

The rule is marker-based and defaults to `human`, so its residual error is
one-sided: agent PRs whose branch, title, and body all lack markers (e.g.
plain typo fixes pushed straight from a checkout) still undercount the agent
lane. The measured misclassification rate on the hand-checked sample is
committed beside the rule and quoted in the report header.
"""

from __future__ import annotations

import argparse
import csv
import statistics
import sys
from collections import Counter, defaultdict
from datetime import datetime, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "observatory" / "site" / "src" / "data"
REPORTS = ROOT / "reports"

PULLS = DATA / "pulls.csv"
REVIEW_SAMPLE = REPORTS / "agent_lane_review_sample.csv"
CI_SAMPLE = REPORTS / "agent_lane_ci_sample.csv"
OUT_CSV = REPORTS / "agent_lane.csv"

LANES = ("human", "agent", "bot")

BRANCH_HANDOFF = __import__("re").compile(r"h\d{3,5}", __import__("re").IGNORECASE)
BRANCH_TOOL_PREFIX = ("codex/", "claude/", "copilot/", "gemini/", "cursor/",
                      "aider/", "cologne-batch-deploy/")
TITLE_HANDOFF = __import__("re").compile(r"\bh\d{3,5}\b", __import__("re").IGNORECASE)
TITLE_MODEL = __import__("re").compile(
    r"\b(claude|codex|copilot|fable|opus\b|sonnet|gemini|glm|deepseek|openai)\b",
    __import__("re").IGNORECASE)
REVERT_TITLE = __import__("re").compile(r"^\s*revert\b", __import__("re").IGNORECASE)


def lane_of(row: dict) -> str:
    """Ordered attribution rule — see module docstring."""
    author = (row.get("author") or "").strip()
    if author.endswith("[bot]"):
        return "bot"
    branch = (row.get("head_ref") or "")
    title = (row.get("title") or "")
    if BRANCH_HANDOFF.search(branch):
        return "agent"
    if branch.lower().startswith(BRANCH_TOOL_PREFIX):
        return "agent"
    if TITLE_HANDOFF.search(title):
        return "agent"
    if TITLE_MODEL.search(title):
        return "agent"
    if (row.get("agent_marker_body") or "").strip() == "true":
        return "agent"
    return "human"


def _dt(s: str) -> datetime | None:
    if not s:
        return None
    try:
        return datetime.fromisoformat(s.replace("Z", "+00:00"))
    except ValueError:
        return None


def _hours_between(a: str, b: str) -> float | None:
    da, db = _dt(a), _dt(b)
    if da is None or db is None:
        return None
    return (db - da).total_seconds() / 3600.0


def load_pulls(path: Path = PULLS) -> list[dict]:
    with open(path, newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def lane_counts(rows: list[dict]) -> Counter:
    return Counter(lane_of(r) for r in rows)


def followup_flagged(rows: list[dict]) -> set[tuple[str, str]]:
    """Merged PRs referenced as `#N` in a later same-repo PR title within 30 days
    whose title smells of repair (revert/fix/repair/follow-up). Lower bound —
    titles are the only committed referencing surface."""
    by_repo: dict[str, list[dict]] = defaultdict(list)
    for r in rows:
        by_repo[r["repo"]].append(r)
    flagged: set[tuple[str, str]] = set()
    for repo, prs in by_repo.items():
        prs.sort(key=lambda r: int(r["number"]))
        for pr in prs:
            merged_at = _dt(pr["merged_at"])
            if pr["merged"] != "true" or not merged_at:
                continue
            tag = f"#{pr['number']}"
            for later in prs:
                if int(later["number"]) <= int(pr["number"]):
                    continue
                created = _dt(later["created_at"])
                if not created:
                    continue
                within = timedelta(0) <= created - merged_at <= timedelta(days=30)
                title_l = (later["title"] or "").lower()
                refers = tag in (later["title"] or "")
                repairish = bool(REVERT_TITLE.match(later["title"] or "")) or any(
                    w in title_l for w in ("fix", "repair", "follow-up", "followup"))
                if within and refers and repairish:
                    flagged.add((repo, str(pr["number"])))
                    break
    return flagged


def lane_metrics(rows: list[dict]) -> list[dict]:
    flagged = followup_flagged(rows)
    review_sample: dict[str, list[float]] = defaultdict(list)
    ci_sample: dict[str, list[int]] = defaultdict(lambda: [0, 0])  # lane -> [fail, n]
    if REVIEW_SAMPLE.exists():
        with open(REVIEW_SAMPLE, newline="", encoding="utf-8") as fh:
            for s in csv.DictReader(fh):
                h = _hours_between(s["created_at"], s["first_review_at"])
                if h is not None and h >= 0:
                    review_sample[s["lane"]].append(h)
    if CI_SAMPLE.exists():
        with open(CI_SAMPLE, newline="", encoding="utf-8") as fh:
            for s in csv.DictReader(fh):
                concl = (s.get("first_check_conclusion") or "").strip()
                if not concl:
                    continue
                ok = concl in ("success", "neutral", "skipped")
                ci_sample[s["lane"]][1] += 1
                if not ok:
                    ci_sample[s["lane"]][0] += 1

    out = []
    for lane in LANES:
        sub = [r for r in rows if lane_of(r) == lane]
        merged = [r for r in sub if r["merged"] == "true"]
        ttm = sorted(h for h in (
            _hours_between(r["created_at"], r["merged_at"]) for r in merged) if h is not None)
        reverts = [r for r in merged if REVERT_TITLE.match(r["title"] or "")]
        flag_n = sum(1 for r in merged if (r["repo"], str(r["number"])) in flagged)
        fails, n_ci = ci_sample[lane]
        out.append({
            "lane": lane,
            "n_prs": len(sub),
            "merged": len(merged),
            "merge_rate": round(len(merged) / len(sub), 4) if sub else "",
            "median_hours_to_merge": round(statistics.median(ttm), 2) if ttm else "",
            "p90_hours_to_merge": round(ttm[int(0.9 * (len(ttm) - 1))], 1) if ttm else "",
            "revert_rate": round(len(reverts) / len(merged), 4) if merged else "",
            "followup_rate": round(flag_n / len(merged), 4) if merged else "",
            "n_review_sample": len(review_sample[lane]),
            "median_hours_to_first_review": round(statistics.median(review_sample[lane]), 2)
            if review_sample[lane] else "",
            "n_ci_sample": n_ci,
            "ci_first_run_failure_rate": round(fails / n_ci, 4) if n_ci else "",
        })
    return out




# report rendering lives in the sibling module (token-size split); imported
# lazily so `import agent_lane` alone never pulls it in during selftest.
def recompute_csv_text() -> str:
    import io
    metrics = lane_metrics(load_pulls())
    buf = io.StringIO()
    w = csv.DictWriter(buf, fieldnames=list(metrics[0].keys()), lineterminator="\n")
    w.writeheader()
    w.writerows(metrics)
    return buf.getvalue()


def _check(cond: bool, msg: str) -> None:
    """Selftest assertion without the `assert` keyword (ruff S101 scope: tests/)."""
    if not cond:
        raise SystemExit(f"selftest FAIL: {msg}")


def selftest() -> int:
    """Deterministic fixture: known lanes, known metric arithmetic."""
    row = lambda **kw: {  # noqa: E731
        "repo": "T", "number": "1", "author": "a", "title": "t", "state": "closed",
        "draft": "false", "created_at": "", "closed_at": "", "merged_at": "",
        "merged": "false", "merged_by": "", "head_ref": "main", "head_sha": "",
        "base_ref": "main", "labels": "", "comments": "0", "review_comments": "0",
        "commits": "", "additions": "", "deletions": "", "changed_files": "",
    } | kw
    cases = [
        (row(author="dependabot[bot]"), "bot"),
        (row(author="renovate[bot]"), "bot"),
        (row(author="gasyoun", head_ref="h5602-drain"), "agent"),
        (row(author="gasyoun", head_ref="h543-yo-sweep"), "agent"),  # 3-digit ID
        (row(author="gasyoun", head_ref="docs/h2012-t4-acc"), "agent"),
        (row(author="gasyoun", head_ref="codex/landing"), "agent"),
        (row(author="gasyoun", head_ref="cologne-batch-deploy/gitattr"), "agent"),
        (row(author="gasyoun", head_ref="main", title="fix(H1736): repair pages"), "agent"),
        (row(author="gasyoun", head_ref="main", title="apply Fable 5 review fix-ups"), "agent"),
        (row(author="gasyoun", head_ref="markup-fix-audit", title="markup: land fix",
             agent_marker_body="true"), "agent"),  # body-side marker
        (row(author="gasyoun", head_ref="markup-fix-audit", title="markup: land fix"), "human"),
        (row(author="vvasuki", head_ref="main", title="Add dictionary"), "human"),
        # negative controls: hex-ish / version strings must NOT match
        (row(author="gasyoun", head_ref="h5x-drain", title="sha a1b2c3"), "human"),
    ]
    for r, want in cases:
        got = lane_of(r)
        _check(got == want,
               f"lane_of({r['head_ref']!r},{r['title']!r})={got}, want {want}")

    fixture = [
        row(number="1", author="gasyoun", head_ref="h1000-drain", merged="true",
            created_at="2026-01-01T00:00:00Z", merged_at="2026-01-02T00:00:00Z"),
        row(number="2", author="gasyoun", head_ref="main", merged="true",
            created_at="2026-01-01T00:00:00Z", merged_at="2026-01-08T00:00:00Z"),
        row(number="3", author="dependabot[bot]", merged="true",
            created_at="2026-01-01T00:00:00Z", merged_at="2026-01-01T12:00:00Z"),
        row(number="4", author="dependabot[bot]", merged="false", state="closed",
            created_at="2026-01-01T00:00:00Z", closed_at="2026-01-01T13:00:00Z"),
        row(number="5", author="gasyoun", head_ref="h1001", merged="true",
            created_at="2026-01-05T00:00:00Z", merged_at="2026-01-06T00:00:00Z",
            title="Revert \"landing\" #1"),
    ]
    metrics = {m["lane"]: m for m in lane_metrics(fixture)}
    _check(metrics["agent"]["n_prs"] == 2 and metrics["agent"]["merged"] == 2,
           "agent lane fixture counts")
    _check(metrics["human"]["n_prs"] == 1 and metrics["human"]["merge_rate"] == 1.0,
           "human lane fixture counts")
    _check(metrics["bot"]["n_prs"] == 2 and metrics["bot"]["merge_rate"] == 0.5,
           "bot lane merge rate")
    _check(metrics["agent"]["median_hours_to_merge"] == 24.0, "agent median ttm (24, 24)")
    _check(metrics["agent"]["revert_rate"] == 0.5, "agent revert rate (PR 5 reverts, /2 merged)")
    # follow-up: PR 5 references #1 within 30d of PR 1 merge -> PR 1 flagged
    _check(("T", "1") in followup_flagged(fixture), "follow-up detection")

    # regression-gate round trip: committed CSV must equal recomputation
    if OUT_CSV.exists():
        committed = OUT_CSV.read_text(encoding="utf-8")
        recomputed = recompute_csv_text()
        _check(committed == recomputed,
               "agent_lane.csv drifted from pulls.csv — rerun scripts/agent_lane.py")

    print(f"selftest OK: {len(cases)} lane-rule cases, metric arithmetic, follow-up detection"
          + (", regression gate" if OUT_CSV.exists() else ""))
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=(__doc__ or "").splitlines()[0])
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--check", action="store_true",
                    help="regression gate: recompute metrics and diff against "
                         "the committed reports/agent_lane.csv")
    args = ap.parse_args()

    if args.selftest:
        return selftest()
    if args.check:
        committed = OUT_CSV.read_text(encoding="utf-8") if OUT_CSV.exists() else ""
        recomputed = recompute_csv_text()
        if committed != recomputed:
            sys.stderr.write("REGRESSION: reports/agent_lane.csv does not re-derive "
                             "from observatory/site/src/data/pulls.csv\n")
            return 1
        print("check OK: agent_lane.csv re-derives from the committed snapshot")
        return 0

    rows = load_pulls()
    metrics = lane_metrics(rows)
    import agent_lane_report  # noqa: PLC0415 — deliberate late import (token-size split)

    agent_lane_report.write_report(rows, metrics)
    out_md = REPORTS / "agent_lane.md"
    print(f"wrote {out_md.relative_to(ROOT)} and {OUT_CSV.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
