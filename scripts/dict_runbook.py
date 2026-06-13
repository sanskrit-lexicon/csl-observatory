"""Cologne dictionary-repo verifier / auditor.

The dictionary-side analog of [`scripts/tooling_runbook.py`](tooling_runbook.py).
It does **not** apply the taxonomy (that stays the human-run
[cologne-issue-runbook](../runbook/cologne-issue-runbook.md)); it only checks
per-issue completeness so drift can be detected after a repo is "done".

Completeness = every issue (pull requests excluded) has exactly 1 type label
+ exactly 1 severity label + 1 milestone + membership in the org project that
matches that milestone:

    Dictionary to Book = 1   Digitization Quality = 2
    Structured Data    = 3   Major Enhancements   = 4     (MWS uses 5-8)

Subcommands:
  verify <repo>            per-issue gate for one repo; exits 2 on any gap.
  audit  <repo,repo,...>   org-wide table + a 'mismatches: N' line (CI-friendly,
                           same contract as tooling_runbook.py audit).
  issue  <repo> <number>   single-issue check for the per-repo event guard;
                           pass --no-project when the runner token lacks
                           read:project (e.g. the default GITHUB_TOKEN).

Mirrors the pagination + PR-exclusion proven in _verify_clean.py, via the
GraphQL `issues` connection (PRs excluded by construction; paginates fully).
"""
import argparse
import json
import subprocess
import sys

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

ORG = "sanskrit-lexicon"
TYPE = {"link-target", "link-splitting", "markup", "text-correction",
        "content-enhancement", "encoding", "scan-quality", "bug", "question"}
SEV = {"minor", "medium", "hard"}
# milestone TITLE -> org project number
PROJ = {"Dictionary to Book": 1, "Digitization Quality": 2,
        "Structured Data": 3, "Major Enhancements": 4}
PROJ_MWS = {"Dictionary to Book": 5, "Digitization Quality": 6,
            "Structured Data": 7, "Major Enhancements": 8}

# Auto-generated log issues (e.g. "Daily Corrections - <date>") are not
# triageable work — exclude them from the checks (parity with tooling_runbook.py).
EXEMPT_LABELS = {"daily-corrections"}


def gh(args):
    for _ in range(3):
        r = subprocess.run(["gh"] + args, capture_output=True, encoding="utf-8")
        if r.returncode == 0:
            return r
    return r


def pmap(repo):
    return PROJ_MWS if repo == "MWS" else PROJ


_ALL = """query($o:String!,$n:String!,$c:String){repository(owner:$o,name:$n){
  issues(first:100,after:$c,states:[OPEN,CLOSED]){pageInfo{hasNextPage endCursor}
  nodes{number labels(first:30){nodes{name}} milestone{title}
        projectItems(first:10){nodes{project{number}}}}}}}"""

_ONE = """query($o:String!,$n:String!,$num:Int!){repository(owner:$o,name:$n){
  issue(number:$num){number labels(first:30){nodes{name}} milestone{title}
        projectItems(first:10){nodes{project{number}}}}}}"""


def _node(x):
    return {"number": x["number"],
            "labels": [l["name"] for l in x["labels"]["nodes"]],
            "milestone": (x["milestone"] or {}).get("title"),
            "projects": [p["project"]["number"] for p in x["projectItems"]["nodes"]]}


def fetch_issues(repo):
    """Every issue (open+closed), all pages, PRs excluded."""
    out, cur = [], None
    while True:
        a = ["api", "graphql", "-f", "query=" + _ALL, "-f", "o=" + ORG, "-f", "n=" + repo]
        if cur:
            a += ["-f", "c=" + cur]
        r = gh(a)
        if r.returncode:
            raise SystemExit(f"ERROR querying {repo}: {r.stderr[:200]}")
        repo_data = json.loads(r.stdout)["data"]["repository"]
        if repo_data is None:
            raise SystemExit(f"ERROR: repository {ORG}/{repo} not found")
        d = repo_data["issues"]
        out += [_node(x) for x in d["nodes"]]
        if d["pageInfo"]["hasNextPage"]:
            cur = d["pageInfo"]["endCursor"]
        else:
            break
    return out


def gaps(issue, repo, check_project=True):
    """List of gap strings for one issue ([] == complete)."""
    lbls = set(issue["labels"])
    g = []
    t = lbls & TYPE
    s = lbls & SEV
    if not t:
        g.append("no-type")
    elif len(t) > 1:
        g.append("multi-type:" + ",".join(sorted(t)))
    if not s:
        g.append("no-severity")
    elif len(s) > 1:
        g.append("multi-severity")
    if issue["milestone"] is None:
        g.append("no-milestone")
    elif check_project:
        tgt = pmap(repo).get(issue["milestone"])
        if tgt and tgt not in issue["projects"]:
            g.append(f"not-in-project-{tgt}")
    return g


def verify(repo):
    issues = fetch_issues(repo)
    bad = {i["number"]: gaps(i, repo) for i in issues
           if not (set(i["labels"]) & EXEMPT_LABELS)}
    bad = {n: g for n, g in bad.items() if g}
    if bad:
        print(f"{repo}: {len(issues)} issues, {len(bad)} incomplete")
        for n, g in sorted(bad.items()):
            print(f"  #{n}: {', '.join(g)}")
        print("GATE FAIL")
        return False
    print(f"{repo}: {len(issues)} issues, all complete  GATE PASS")
    return True


def audit(repos):
    print(f"{'repo':12} {'iss':>4} {'gaps':>5}  status")
    print("-" * 40)
    mismatches = 0
    for repo in repos:
        issues = fetch_issues(repo)
        n_bad = sum(1 for i in issues
                    if not (set(i["labels"]) & EXEMPT_LABELS) and gaps(i, repo))
        status = "empty" if not issues else ("OK" if n_bad == 0 else "GAPS")
        if n_bad:
            mismatches += 1
        print(f"{repo:12} {len(issues):>4} {n_bad:>5}  {status}")
    print(f"\nmismatches: {mismatches}")
    return mismatches


def issue(repo, number, check_project=True):
    r = gh(["api", "graphql", "-f", "query=" + _ONE, "-f", "o=" + ORG,
            "-f", "n=" + repo, "-F", "num=" + str(number)])
    if r.returncode:
        raise SystemExit(f"ERROR querying {repo}#{number}: {r.stderr[:200]}")
    x = json.loads(r.stdout)["data"]["repository"]["issue"]
    if x is None:
        raise SystemExit(f"ERROR: {repo}#{number} not found (or is a PR)")
    it = _node(x)
    if set(it["labels"]) & EXEMPT_LABELS:
        print(f"{repo}#{number}: exempt (auto-log) — not triaged")
        return True
    g = gaps(it, repo, check_project=check_project)
    if g:
        print(f"{repo}#{number}: " + ", ".join(g) + "  DRIFT")
        return False
    print(f"{repo}#{number}: complete")
    return True


def main():
    p = argparse.ArgumentParser(prog="dict_runbook")
    sub = p.add_subparsers(dest="cmd", required=True)
    sp = sub.add_parser("verify"); sp.add_argument("repo")
    sp = sub.add_parser("audit"); sp.add_argument("repos", help="comma-separated repo names")
    sp = sub.add_parser("issue")
    sp.add_argument("repo"); sp.add_argument("number", type=int)
    sp.add_argument("--no-project", action="store_true",
                    help="skip the project-membership check (use when the token lacks read:project)")
    a = p.parse_args()
    if a.cmd == "verify":
        sys.exit(0 if verify(a.repo) else 2)
    elif a.cmd == "audit":
        sys.exit(0 if audit(a.repos.split(",")) == 0 else 2)
    elif a.cmd == "issue":
        sys.exit(0 if issue(a.repo, a.number, check_project=not a.no_project) else 2)


if __name__ == "__main__":
    main()
