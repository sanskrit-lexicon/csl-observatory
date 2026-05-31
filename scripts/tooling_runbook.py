"""Cologne tooling-repo runbook executor.

Applies the [Cologne tooling-repo taxonomy](../runbook/cologne-tooling-runbook.md)
to a single repo or a batch.

Phases handled here:
  setup      Phase 2 + 5      create / update 17 type + 4 severity + 3-4 domain
                              labels; create 5 milestones.
  classify   Phase 3 + 4 + 5  add type+severity+milestone (+ optional domain)
                              to each issue, optionally strip stale labels.
  verify     Phase 7          hard gate: missing/multi type, severity, milestone.
  project    Phase 6          add every open issue to org Project #9
                              (Tooling Roadmap).
  refresh    Phase 9          rewrite README with live counts + Mermaid pies,
                              validating each mermaid block via the GitHub API
                              before committing.
  audit                       reconcile project items vs per-repo open counts.

Usage:
  python scripts/tooling_runbook.py setup     <repo> <category>
  python scripts/tooling_runbook.py classify  <repo> <plan.json> [<domain-label>]
  python scripts/tooling_runbook.py verify    <repo>
  python scripts/tooling_runbook.py project   <repo>
  python scripts/tooling_runbook.py refresh   <repo> <category>
  python scripts/tooling_runbook.py milestones <repo>
  python scripts/tooling_runbook.py sha       <repo>
  python scripts/tooling_runbook.py audit     <repo>[,<repo>,...]

Categories: web-backend, web-frontend, data-store, converter, linking-tool,
            processing-tool, scanned-book, build-meta, archive.

A `plan.json` for `classify` maps issue-number-string -> { type, sev, ms,
strip?: [labels-to-delete] }.
"""
import argparse
import base64
import json
import re
import subprocess
import sys
from collections import Counter

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

ORG = "sanskrit-lexicon"
PROJECT_ID = "PVT_kwDOAGGnOc4BXy9n"          # Tooling Roadmap (org project #9)
PROJECT_NUMBER = 9

DOMAIN_MAP = {
    "web-backend":     [("api","API endpoint / contract"),
                        ("auth","Authentication / authorization"),
                        ("db","Database / persistence"),
                        ("caching","Caching layer")],
    "web-frontend":    [("ui","UI components / interaction"),
                        ("routing","Routes / navigation"),
                        ("i18n","Internationalization / localization"),
                        ("rendering","Rendering / display")],
    "data-store":      [("schema","Schema / structure"),
                        ("migration","Migrations / data moves"),
                        ("integrity","Data integrity / validation"),
                        ("storage","Storage / format")],
    "converter":       [("transcoding","Transcoding / encoding conversion"),
                        ("roundtrip","Round-trip correctness"),
                        ("edge-cases","Edge cases / rare inputs")],
    "linking-tool":    [("link-resolution","Linking / target resolution"),
                        ("source-mapping","Source-to-output mapping / extraction"),
                        ("coverage","Coverage / completeness")],
    "processing-tool": [("morphology","Morphological generation / declension"),
                        ("normalization","Headword / form normalization"),
                        ("lookup","Lookup / matching / retrieval")],
    "scanned-book":    [("ocr","OCR / text extraction"),
                        ("image-quality","Image quality / replacement"),
                        ("metadata","Page metadata / TOC")],
    "build-meta":      [("ci","CI / CD pipeline"),
                        ("packaging","Package / distribution build"),
                        ("publishing","Publishing pipeline / artifacts")],
    "archive":         [],
}

CORE_LABELS = [
    ("bug",           "0e8a16", "Code defect (wrong output, broken contract)"),
    ("regression",    "0e8a16", "Previously working behavior, now broken"),
    ("tech-debt",     "0e8a16", "Refactoring, cleanup, modernization"),
    ("dependency",    "0e8a16", "Library upgrade, vendor swap, runtime bump"),
    ("security",      "0e8a16", "CVE, credential exposure, auth issue"),
    ("feature",       "0075ca", "Net-new capability"),
    ("enhancement",   "0075ca", "Improvement to existing capability"),
    ("performance",   "0075ca", "Speed, memory, throughput optimization"),
    ("documentation", "d4c5f9", "Prose docs, README, comments"),
    ("docs-api",      "d4c5f9", "API contract / schema / endpoint docs"),
    ("infrastructure","f9d0c4", "CI/CD, deploy, env setup"),
    ("data-pipeline", "f9d0c4", "ETL, batch jobs, scheduled processing"),
    ("cross-repo",    "f9d0c4", "Changes required across 2+ repos"),
    ("build-tooling", "f9d0c4", "Build scripts, package generation, release"),
    ("question",      "e99695", "Needs research/clarification"),
    ("proposal",      "e99695", "Architecture/design proposal"),
    ("discussion",    "e99695", "Open-ended, not yet a proposal"),
    ("trivial",       "c2e0c6", "Cosmetic, < 1 hour"),
    ("minor",         "e4e669", "Single function/component"),
    ("major",         "fbca04", "Multiple files, design decision"),
    ("critical",      "b60205", "Blocks users, data loss, CVE"),
]
MILESTONES = ["API Stability", "User Experience", "Data Quality",
              "Developer Experience", "Community"]

TYPE_SET = {n for n, _, _ in CORE_LABELS
            if n not in ("trivial", "minor", "major", "critical")}
SEV_SET = {"trivial", "minor", "major", "critical"}

# Auto-generated log issues (e.g. csl-corrections "Daily Corrections - <date>")
# are not triageable work — exclude them from verify + audit.
EXEMPT_LABELS = {"daily-corrections"}


def gh(args, **kw):
    return subprocess.run(["gh"] + args, capture_output=True, encoding="utf-8", **kw)


def setup(repo, category):
    domain_labels = [(f"domain:{n}", "5319e7", d) for n, d in DOMAIN_MAP.get(category, [])]
    for name, color, desc in CORE_LABELS + domain_labels:
        r = gh(["api", f"repos/{ORG}/{repo}/labels", "-X", "POST",
                "-f", f"name={name}", "-f", f"color={color}", "-f", f"description={desc}"])
        if r.returncode == 0:
            print(f"+ {name}", flush=True)
            continue
        r2 = gh(["api", f"repos/{ORG}/{repo}/labels/{name}", "-X", "PATCH",
                 "-f", f"new_name={name}", "-f", f"color={color}", "-f", f"description={desc}"])
        if r2.returncode == 0:
            print(f"~ {name}", flush=True)
        else:
            print(f"! {name}: {r.stderr[:80]} / {r2.stderr[:80]}", flush=True)
    for title in MILESTONES:
        gh(["api", f"repos/{ORG}/{repo}/milestones", "-X", "POST", "-f", f"title={title}"])
    print("DONE")


def _fetch_issues(repo, state="open"):
    r = gh(["api", f"repos/{ORG}/{repo}/issues?state={state}&per_page=100", "--paginate",
            "--jq", "[.[] | select(.pull_request==null) | "
                    "{n:.number, id:.node_id, labels:[.labels[].name], milestone:.milestone.title}]"])
    issues = []
    for chunk in re.findall(r"\[[\s\S]*?\](?=\s*(?:\[|$))", r.stdout):
        try:
            issues += json.loads(chunk)
        except json.JSONDecodeError:
            pass
    if not issues:
        try:
            issues = json.loads(r.stdout)
        except json.JSONDecodeError:
            pass
    return issues


def classify(repo, plan_path, domain=None):
    plan = json.load(open(plan_path, encoding="utf-8"))
    errors = []
    total = len(plan)
    done = 0
    for n_str, spec in plan.items():
        n = int(n_str)
        for stale in spec.get("strip", []):
            gh(["api", f"repos/{ORG}/{repo}/issues/{n}/labels/{stale}", "-X", "DELETE"])
        labels_to_add = [spec["type"], spec["sev"]]
        if domain:
            labels_to_add.append(domain)
        for label in labels_to_add:
            r = gh(["api", f"repos/{ORG}/{repo}/issues/{n}/labels", "-X", "POST",
                    "-f", f"labels[]={label}"])
            if r.returncode != 0 and "422" not in r.stderr:
                errors.append(f"add {label} on #{n}: {r.stderr[:80].strip()}")
        if spec.get("ms"):
            r = gh(["api", f"repos/{ORG}/{repo}/issues/{n}", "-X", "PATCH",
                    "-F", f"milestone={spec['ms']}"])
            if r.returncode != 0:
                errors.append(f"milestone #{n}: {r.stderr[:80].strip()}")
        done += 1
        if done % 10 == 0 or done == total:
            print(f"  {done}/{total}", flush=True)
    if errors:
        print("ERRORS:\n  " + "\n  ".join(errors))
    else:
        print("DONE no errors.")


def verify(repo):
    issues = _fetch_issues(repo, "open")
    mt, ms_, mm, mut, mus = [], [], [], [], []
    for i in issues:
        n, lbls, ms = i["n"], set(i["labels"]), i["milestone"]
        if lbls & EXEMPT_LABELS:
            continue
        ts = lbls & TYPE_SET
        ss = lbls & SEV_SET
        if not ts:
            mt.append(n)
        elif len(ts) > 1:
            mut.append((n, sorted(ts)))
        if not ss:
            ms_.append(n)
        elif len(ss) > 1:
            mus.append((n, sorted(ss)))
        if ms is None and "discussion" not in lbls:
            mm.append(n)
    print(f"open={len(issues)} mt={mt} ms={ms_} mm={mm} multi_t={mut} multi_s={mus}")
    gate = not (mt or ms_ or mut or mus or mm)
    print("GATE PASS" if gate else "GATE FAIL")
    return gate


def project(repo):
    issues = _fetch_issues(repo, "open")
    errors = []
    for i in issues:
        q = (f'mutation {{ addProjectV2ItemById(input: '
             f'{{projectId: "{PROJECT_ID}", contentId: "{i["id"]}"}}) {{ item {{ id }} }} }}')
        r = gh(["api", "graphql", "-f", f"query={q}"])
        if r.returncode != 0:
            errors.append(f"#{i['n']}: {r.stderr[:120].strip()}")
    print(f"added {len(issues) - len(errors)}/{len(issues)}")
    for e in errors:
        print(" ", e)
    print("DONE")


def _fetch_milestones(repo):
    r = gh(["api", f"repos/{ORG}/{repo}/milestones?state=all",
            "--jq", "[.[] | {n:.number, title, open:.open_issues, closed:.closed_issues}]"])
    try:
        return json.loads(r.stdout)
    except json.JSONDecodeError:
        return []


def _fetch_repo_meta(repo):
    r = gh(["api", f"repos/{ORG}/{repo}",
            "--jq", "{description, language, default_branch}"])
    try:
        return json.loads(r.stdout)
    except json.JSONDecodeError:
        return {}


def _fetch_total_counts(repo):
    r_open = gh(["api", f"repos/{ORG}/{repo}/issues?state=open&per_page=100", "--paginate",
                 "--jq", "[.[] | select(.pull_request==null)] | length"])
    r_closed = gh(["api", f"repos/{ORG}/{repo}/issues?state=closed&per_page=100", "--paginate",
                   "--jq", "[.[] | select(.pull_request==null)] | length"])
    o = sum(int(x) for x in re.findall(r"\d+", r_open.stdout) or ["0"])
    c = sum(int(x) for x in re.findall(r"\d+", r_closed.stdout) or ["0"])
    return o, c


def _fetch_readme_sha(repo):
    r = gh(["api", f"repos/{ORG}/{repo}/contents/README.md", "--jq", ".sha"])
    s = r.stdout.strip()
    return s if s and "not found" not in s.lower() else None


def _validate_mermaid(block_text):
    r = gh(["api", "markdown", "-X", "POST", "-f", f"text={block_text}", "-f", "mode=markdown"])
    return "highlight-source-mermaid" in r.stdout


def _build_readme(repo, category, meta, issues, milestones, total_open, total_closed):
    cat = category
    domains = [f"domain:{n}" for n, _ in DOMAIN_MAP.get(cat, [])]
    type_counts = Counter()
    sev_counts = Counter()
    for i in issues:
        lbls = set(i["labels"])
        ts = lbls & TYPE_SET
        ss = lbls & SEV_SET
        if ts:
            type_counts[next(iter(ts))] += 1
        if ss:
            sev_counts[next(iter(ss))] += 1

    desc = meta.get("description") or f"CDSL {cat} repository in the Sanskrit Lexicon project."
    lang = meta.get("language") or "—"

    md = [f"# {repo}\n",
          f"CDSL **{cat}** repository in the Sanskrit Lexicon project.",
          desc, "",
          "## Tech Stack", "",
          f"- **Runtime**: {lang}",
          "- **Build**: per-repo workflow",
          "- **Pipeline**: see [csl-observatory tooling runbook]"
          "(https://github.com/sanskrit-lexicon/csl-observatory/blob/main/runbook/cologne-tooling-runbook.md)",
          "",
          "## Issues Overview", "",
          f"Snapshot: **{total_open}** open, **{total_closed}** closed.", "",
          "### By Milestone", "",
          "| Milestone | Open | Closed | Total |",
          "|---|---:|---:|---:|"]
    by_title = {m["title"]: m for m in milestones}
    for title in MILESTONES:
        m = by_title.get(title, {"open": 0, "closed": 0})
        md.append(f"| {title} | {m['open']} | {m['closed']} | {m['open'] + m['closed']} |")
    md.append("")
    if type_counts:
        md += ["### By Type", "", "```mermaid", "pie title Open issues by type"]
        for t, n in sorted(type_counts.items(), key=lambda x: -x[1]):
            md.append(f'    "{t}" : {n}')
        md += ["```", ""]
    if sev_counts:
        md += ["### By Severity", "", "```mermaid", "pie title Open issues by severity"]
        for s, n in sorted(sev_counts.items(), key=lambda x: -x[1]):
            md.append(f'    "{s}" : {n}')
        md += ["```", ""]
    md += ["## GitHub Issue Conventions", "",
           "Follows the [Cologne tooling-repo taxonomy]"
           "(https://github.com/sanskrit-lexicon/csl-observatory/blob/main/runbook/cologne-tooling-runbook.md):",
           "",
           "- **17 type labels** across 5 categories",
           "- **4 severity levels**: trivial, minor, major, critical",
           "- **5 milestones**: API Stability, User Experience, Data Quality, Developer Experience, Community",
           f"- **Domain labels** scoped to {cat}: " + ", ".join(f"`{d}`" for d in domains),
           "- **Org Project**: [Tooling Roadmap](https://github.com/orgs/sanskrit-lexicon/projects/9)",
           "",
           "---",
           "*Generated by Cologne Tooling Runbook.*",
           ""]
    return "\n".join(md)


def refresh(repo, category):
    print(f"=== {repo} ({category}) ===", flush=True)
    meta = _fetch_repo_meta(repo)
    issues = _fetch_issues(repo, "open")
    milestones = _fetch_milestones(repo)
    total_open, total_closed = _fetch_total_counts(repo)
    body = _build_readme(repo, category, meta, issues, milestones, total_open, total_closed)
    for block in re.findall(r"```mermaid\n[\s\S]*?\n```", body):
        if not _validate_mermaid(block):
            print(f"  ABORT mermaid validation failed:\n{block[:120]}")
            return False
    sha = _fetch_readme_sha(repo)
    content_b64 = base64.b64encode(body.encode("utf-8")).decode("ascii")
    args = ["api", f"repos/{ORG}/{repo}/contents/README.md", "-X", "PUT",
            "-f", "message=docs(runbook): refresh tooling-repo README with live counts",
            "-f", f"content={content_b64}"]
    if sha:
        args += ["-f", f"sha={sha}"]
    args += ["--jq", ".commit.sha"]
    r = gh(args)
    if r.returncode == 0:
        print(f"  committed {r.stdout.strip()[:8]} ({len(issues)} open)")
        return True
    print(f"  FAILED: {r.stderr[:200]}")
    return False


def audit(repos):
    """Reconcile project items vs per-repo open-issue counts."""
    cursor = None
    items = []
    while True:
        after = f', after:"{cursor}"' if cursor else ""
        q = f'''{{
          organization(login:"{ORG}") {{
            projectV2(number:{PROJECT_NUMBER}) {{
              items(first:100{after}) {{
                pageInfo {{ endCursor hasNextPage }}
                nodes {{
                  content {{
                    __typename
                    ... on Issue        {{ number state labels(first:20){{nodes{{name}}}} repository {{ name }} }}
                    ... on PullRequest  {{ number state repository {{ name }} }}
                  }}
                }}
              }}
            }}
          }}
        }}'''
        r = gh(["api", "graphql", "-f", f"query={q}"])
        d = json.loads(r.stdout)
        page = d["data"]["organization"]["projectV2"]["items"]
        items += page["nodes"]
        if not page["pageInfo"]["hasNextPage"]:
            break
        cursor = page["pageInfo"]["endCursor"]

    by_repo = Counter()
    for it in items:
        c = it.get("content") or {}
        # count only OPEN, non-exempt issues on the board — closed issues / PRs and
        # exempt auto-logs would otherwise skew the board count vs the triage set
        if (c.get("__typename") == "Issue" and c.get("state") == "OPEN"
                and c.get("repository")):
            lbls = {l["name"] for l in c.get("labels", {}).get("nodes", [])}
            if lbls & EXEMPT_LABELS:
                continue
            by_repo[c["repository"]["name"]] += 1

    print(f"total OPEN issues on project #{PROJECT_NUMBER}: {sum(by_repo.values())}")
    print(f"{'Repo':30} {'OnBoard':>10} {'Triageable':>12} {'Diff':>6}")
    mismatches = []
    for repo in repos:
        in_proj = by_repo.get(repo, 0)
        # triageable = open, PR-free, minus exempt auto-log issues (daily-corrections)
        actual = sum(1 for i in _fetch_issues(repo, "open")
                     if not (set(i["labels"]) & EXEMPT_LABELS))
        diff = in_proj - actual
        flag = "" if diff == 0 else "MISS"
        if diff != 0:
            mismatches.append((repo, in_proj, actual, diff))
        print(f"{repo:30} {in_proj:>10} {actual:>12} {diff:>+6} {flag}")
    print(f"\nmismatches: {len(mismatches)}")


def main():
    parser = argparse.ArgumentParser(prog="tooling_runbook")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("setup");     p.add_argument("repo"); p.add_argument("category")
    p = sub.add_parser("classify");  p.add_argument("repo"); p.add_argument("plan");    p.add_argument("domain", nargs="?")
    p = sub.add_parser("verify");    p.add_argument("repo")
    p = sub.add_parser("project");   p.add_argument("repo")
    p = sub.add_parser("refresh");   p.add_argument("repo"); p.add_argument("category")
    p = sub.add_parser("milestones");p.add_argument("repo")
    p = sub.add_parser("sha");       p.add_argument("repo")
    p = sub.add_parser("audit");     p.add_argument("repos", help="comma-separated repo names")

    args = parser.parse_args()
    if args.cmd == "setup":
        setup(args.repo, args.category)
    elif args.cmd == "classify":
        classify(args.repo, args.plan, args.domain)
    elif args.cmd == "verify":
        verify(args.repo)
    elif args.cmd == "project":
        project(args.repo)
    elif args.cmd == "refresh":
        refresh(args.repo, args.category)
    elif args.cmd == "milestones":
        print(json.dumps(_fetch_milestones(args.repo), indent=2))
    elif args.cmd == "sha":
        print(_fetch_readme_sha(args.repo) or "NO_README")
    elif args.cmd == "audit":
        audit(args.repos.split(","))


if __name__ == "__main__":
    main()
