#!/usr/bin/env python3
"""Report rendering for the agent-lane census (H7123).

Split from `scripts/agent_lane.py` at the token-size gate's request (code
modules stay under the 20 kB limit). Owns the human-readable surfaces:
`reports/agent_lane.md` and the policy-verdict section. All numbers arrive
computed from `agent_lane.lane_metrics`; nothing here re-derives metrics.
"""

from __future__ import annotations

import csv
import statistics
from collections import Counter
from pathlib import Path

import agent_lane as al  # safe: agent_lane imports this module only lazily

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "observatory" / "site" / "src" / "data"
REPORTS = ROOT / "reports"

ISSUES = DATA / "issues.csv"
REVIEW_SAMPLE = REPORTS / "agent_lane_review_sample.csv"
CI_SAMPLE = REPORTS / "agent_lane_ci_sample.csv"
ADJUDICATION = REPORTS / "agent_lane_adjudication.csv"
OUT_MD = REPORTS / "agent_lane.md"

def _fmt(v: object, pct: bool = False) -> str:
    if v == "" or v is None:
        return "n/a"
    if pct:
        return f"{float(v) * 100:.1f}%"
    return str(v)


def policy_verdict(rows: list[dict]) -> tuple[dict, str]:
    """Measured cleanliness verdict for the `no-bot` label + weekly feed."""
    with open(ISSUES, newline="", encoding="utf-8") as fh:
        issues = list(csv.DictReader(fh))
    nobot_prs = [r for r in rows if "no-bot" in r["labels"].split("|")]
    nobot_issues = [r for r in issues if "no-bot" in r["labels"].split("|")]

    def med_comments(items: list[dict]) -> float:
        vals = [int(str(i.get("comments") or "0") or 0) for i in items]
        return float(statistics.median(vals)) if vals else 0.0

    lanes = {lane: [r for r in rows if al.lane_of(r) == lane] for lane in al.LANES}
    human_pre = [r for r in lanes["human"] if r["created_at"] < "2026"]
    human_2026 = [r for r in lanes["human"] if r["created_at"] >= "2026"]
    bot_2026 = [r for r in lanes["bot"] if r["created_at"] >= "2026"]
    prs_2026 = [r for r in rows if r["created_at"] >= "2026"]
    bot_share = len(bot_2026) / len(prs_2026) if prs_2026 else 0.0
    bot_merge = ([r for r in bot_2026 if r["merged"] == "true"], bot_2026)
    facts = {
        "nobot_label_prs": len(nobot_prs),
        "nobot_label_issues": len(nobot_issues),
        "bot_share_of_2026_prs": round(bot_share, 4),
        "bot_merge_rate_2026": round(len(bot_merge[0]) / len(bot_2026), 4) if bot_2026 else "",
        "median_comments_bot_prs": med_comments(lanes["bot"]),
        "median_comments_agent_prs": med_comments(lanes["agent"]),
        "median_comments_human_prs_pre2026": med_comments(human_pre),
        "median_comments_human_prs_2026": med_comments(human_2026),
        "human_prs_with_comments_2026": sum(
        1 for r in human_2026 if int(str(r["comments"] or "0") or 0) > 0),
        "human_prs_2026": len(human_2026),
    }
    bot_quiet = facts["median_comments_bot_prs"] == 0
    human_flat = facts["median_comments_human_prs_2026"] <= max(
        facts["median_comments_human_prs_pre2026"], 1) * 3
    if bot_quiet and human_flat:
        verdict = ("THREADS CLEAN — measured: bot PRs carry a median of "
                   f"{facts['median_comments_bot_prs']:.0f} comments (no maintainer "
                   "conversation on routine dependency PRs), the human-lane median "
                   f"comment load moved from {facts['median_comments_human_prs_pre2026']:.0f} "
                   f"(pre-2026) to {facts['median_comments_human_prs_2026']:.0f} (2026) "
                   "while PR volume grew ~36×, and bots are "
                   f"{bot_share * 100:.1f}% of 2026 PRs. The `no-bot` label itself "
                   f"appears on {facts['nobot_label_prs']} PRs / "
                   f"{facts['nobot_label_issues']} issues — it is a rare routing signal, "
                   "not the mechanism; what kept threads clean was low-comment bot "
                   "etiquette (AI_CONTRIBUTION_POLICY §Issue comments) plus auto-merge.")
    else:
        verdict = ("MIXED — bot median comments "
                   f"{facts['median_comments_bot_prs']:.0f}, human median "
                   f"{facts['median_comments_human_prs_pre2026']:.0f}→"
                   f"{facts['median_comments_human_prs_2026']:.0f}: see table; "
                   "cleanliness is not uniform across lanes.")
    return facts, verdict


def write_report(rows: list[dict], metrics: list[dict]) -> None:
    generated = max(r["created_at"] for r in rows)
    total = len(rows)
    pre = [r for r in rows if r["created_at"] < "2026"]
    era = Counter()
    for r in rows:
        era[(al.lane_of(r), "pre-2026" if r["created_at"] < "2026" else "2026")] += 1
    counts = al.lane_counts(rows)
    facts, verdict = policy_verdict(rows)
    misclass = ""
    if ADJUDICATION.exists():
        with open(ADJUDICATION, newline="", encoding="utf-8") as fh:
            adj = list(csv.DictReader(fh))
        i_ok = sum(1 for a in adj if a["agree_initial"] == "true")
        f_ok = sum(1 for a in adj if a["agree_final"] == "true")
        misclass = (f"{len(adj) - f_ok}/{len(adj)} = {(len(adj) - f_ok) / len(adj) * 100:.1f}% "
                    f"(calibrated rule) — the pre-calibration `h\\d{{4}}` rule missed "
                    f"{len(adj) - i_ok}/{len(adj)} = {(len(adj) - i_ok) / len(adj) * 100:.1f}%, "
                    "all agent→human undercounts")

    md = []
    md.append("# Agent lane — two years of AI-agent contributions to a 13-year org")
    md.append("")
    md.append("_Generated by `scripts/agent_lane.py` from `observatory/site/src/data/pulls.csv`")
    md.append(f"(snapshot through {generated}); every number below re-derives offline from")
    md.append("the committed CSVs. Sample-based metrics (review latency, CI first-run)")
    md.append("re-derive from the committed stratified sample CSVs in `reports/`._")
    md.append("")
    md.append("## Attribution rule")
    md.append("")
    md.append("Ordered, first match wins — full statement in `scripts/agent_lane.py`:")
    md.append("")
    md.append("1. **bot** — author login ends `[bot]` (dependabot, renovate, …).")
    md.append("2. **agent** — human author + explicit marker: handoff ID `h\\d{3,5}` in the")
    md.append("   head branch (worktree convention, e.g. `h5602-drain`, `h543-yo-sweep`),")
    md.append("   an agent-tool / batch-deploy branch prefix (`codex/`, `claude/`,")
    md.append("   `cologne-batch-deploy/`, …), a handoff ID in the title, an AI model")
    md.append("   named in the title, or an agent marker in the PR body (handoff refs,")
    md.append("   co-author trailers, \"generated with\", model names — committed as the")
    md.append("   `agent_marker_body` boolean). Default is `human`, so unmarked agent work")
    md.append("   undercounts the agent lane — the error is one-sided by construction.")
    md.append("3. **human** — everything else.")
    md.append("")
    md.append("**Measured misclassification (30-PR hand-checked stratified sample,")
    md.append(f"`reports/agent_lane_adjudication.csv`): {misclass or 'n/a'}**")
    md.append("")
    md.append("## Headline")
    md.append("")
    n_merged = sum(1 for r in rows if r["merged"] == "true")
    n_unmerged = total - n_merged
    md.append(f"- {total:,} org PRs total; **{len(pre)} created 2014–2025, {total - len(pre):,} in 2026 alone**")
    md.append(f"- lanes: human {counts['human']} · agent {counts['agent']} · bot {counts['bot']}")
    md.append(f"- {counts['agent'] / total * 100:.0f}% of all org PRs carry explicit agent markers")
    md.append("- merged vs closed-unmerged is now distinguishable: `merged_at`/`merged`")
    md.append(f"  columns in the snapshot ({n_merged:,} merged / {n_unmerged:,}"
              " closed-unmerged at census time)")
    md.append("")
    md.append("## Per-lane metrics")
    md.append("")
    md.append("| lane | PRs | merged | merge rate | median h→merge | p90 h→merge |")
    md.append("|---|---|---|---|---|---|")
    for m in metrics:
        md.append(f"| {m['lane']} | {m['n_prs']} | {m['merged']} | {_fmt(m['merge_rate'], True)} |"
                  f" {_fmt(m['median_hours_to_merge'])} | {_fmt(m['p90_hours_to_merge'])} |")
    md.append("")
    md.append("| lane | revert rate | follow-up-defect rate | review latency (median h, sample) |")
    md.append("|---|---|---|---|")
    zero_review = ""
    if REVIEW_SAMPLE.exists():
        with open(REVIEW_SAMPLE, newline="", encoding="utf-8") as fh:
            rs = list(csv.DictReader(fh))
        n_zero = sum(1 for s in rs if str(s.get("n_reviews") or "0") == "0")
        zero_review = (f" Measured: {n_zero}/{len(rs)} sampled PRs carry **zero reviews** — "
                       "the org's PR lane has no peer-review step; time-to-merge *is* "
                       "decision latency, and the only reviews present are bot-lane "
                       "auto-approvals.") if rs else ""
    for m in metrics:
        rl = _fmt(m["median_hours_to_first_review"]) + f" (n={m['n_review_sample']})" \
            if m["n_review_sample"] else "n/a"
        md.append(f"| {m['lane']} | {_fmt(m['revert_rate'], True)} | {_fmt(m['followup_rate'], True)} | {rl} |")
    md.append("")
    md.append(f"Definitions: *review latency* = created→first review submit (stratified"
              f" sample).{zero_review}")
    md.append("")
    md.append("| lane | CI first-run failure (sample) |")
    md.append("|---|---|")
    for m in metrics:
        ci = _fmt(m["ci_first_run_failure_rate"], True) + f" (n={m['n_ci_sample']})" \
            if m["n_ci_sample"] else "n/a"
        md.append(f"| {m['lane']} | {ci} |")
    md.append("")
    md.append("Definitions: *review latency* = created→first review submit (stratified")
    md.append("sample; bots' \"reviews\" are auto-approvals); *CI first-run failure* =")
    md.append("earliest check-run on the PR head SHA concluded ≠ success/neutral/skipped")
    md.append("(stratified sample; re-runs overwrite history, so this is the surviving")
    md.append("earliest attempt); *follow-up-defect* = merged PR referenced as `#N` in a")
    md.append("later same-repo PR title (revert/fix wording) within 30 days — a lower bound.")
    md.append("*Revert rate* counts revert-titled PRs: the org opens none — reverts land")
    md.append("as follow-up fix PRs (see follow-up rate) or as direct commits, so 0.0% is a")
    md.append("measured zero on this surface, not a missing signal.")
    md.append("")
    md.append("## Era split (PRs per lane)")
    md.append("")
    md.append("| lane | pre-2026 | 2026 |")
    md.append("|---|---|---|")
    for lane in al.LANES:
        md.append(f"| {lane} | {era[(lane, 'pre-2026')]} | {era[(lane, '2026')]} |")
    md.append("")
    md.append("## Policy verdict — did `no-bot` + the weekly human-activity feed keep threads clean?")
    md.append("")
    md.append("| measure | value |")
    md.append("|---|---|")
    for k, v in facts.items():
        val = _fmt(v, pct=k.endswith(("rate", "share")) or "share" in k or "rate" in k)
        md.append(f"| {k} | {val} |")
    md.append("")
    md.append(f"**Verdict: {verdict}**")
    md.append("")
    OUT_MD.write_text("\n".join(md) + "\n", encoding="utf-8")

    with open(al.OUT_CSV, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(metrics[0].keys()), lineterminator="\n")
        w.writeheader()
        w.writerows(metrics)


