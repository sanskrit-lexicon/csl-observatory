Apply the full Sanskrit Lexicon issue-taxonomy runbook to every unprocessed repo in the org.

## Step 1 — Discover unprocessed repos

A repo is **processed** only when **every one of its issues** carries exactly one type label, exactly one severity label, one milestone, and is in the GitHub project matching that milestone. It is **unprocessed** if it has ≥ 1 issue and *any* issue falls short. Repos with 0 issues are skipped (nothing to do).

> ⚠️ **Never decide this from label *definitions*.** The old check —
> `gh api repos/ORG/REPO/labels -q '[.[].name] | contains(["minor"])'` — only tests whether the `minor` label is *defined* in the repo, not whether issues carry it. On 2026-05-31 it marked ~20 dictionary repos "done" while they still held ~165 unlabelled issues. Decide per-issue, and never trust a hardcoded "already processed" list.

Three pitfalls the detection must avoid:

1. **Per-issue completeness, not label presence.** Confirm *each* issue has exactly 1 type + 1 severity + 1 milestone + a matching project — not merely that those labels exist in the repo.
2. **Paginate.** REST `…/issues?per_page=100` returns only the *first* page, so repos with > 100 issues (PWG = 175, plus PWK and MWS) hide their low-numbered issues — some of which already carry *multiple* type labels and must be caught. Loop GraphQL `repository.issues(first:100, after:$cur)` on `pageInfo.hasNextPage`.
3. **Exclude pull requests.** REST `/issues` mixes in PRs (dependabot bumps, docs/Pages-fix PRs), inflating counts and tripping checks. GraphQL's `issues` connection excludes PRs by construction — use it.

Detection script (per-issue, paginated, PR-free — mirrors the org-wide verifier `_verify_clean.py`):

```python
import subprocess, json, sys
sys.stdout.reconfigure(encoding='utf-8'); sys.stderr.reconfigure(encoding='utf-8')

ORG  = "sanskrit-lexicon"
TYPE = {"link-target","link-splitting","markup","text-correction",
        "content-enhancement","encoding","scan-quality","bug","question"}
SEV  = {"minor","medium","hard"}
# milestone TITLE -> project number (MWS uses 5-8; every other dict uses 1-4)
PROJ     = {"Dictionary to Book":1,"Digitization Quality":2,"Structured Data":3,"Major Enhancements":4}
PROJ_MWS = {"Dictionary to Book":5,"Digitization Quality":6,"Structured Data":7,"Major Enhancements":8}

# non-dictionary / archive repos belong to cologne-tooling-runbook.md, never this one
SKIP = {"COLOGNE","CORRECTIONS","alternateheadwords","avlinks","rvlinks","literarysource",
        "hwnorm1","hwnorm2","mw-dev","MWinflect","cologne-stardict","sanskrit-fonts",
        "sanskrit-lexicon.github.io","santamlegacy","test_cologne_push","Wil-YAT","MW72",
        "ArabicInSanskrit","GreekInSanskrit"}
def skip(r): return r in SKIP or r.startswith("csl-") or r.startswith("temp_corrections_")

def gh(a):
    for _ in range(3):
        r = subprocess.run(["gh","api"]+a, capture_output=True, encoding="utf-8")
        if r.returncode == 0: return r
    return r

# GraphQL's issues connection excludes PRs by construction (pitfall 3)
Q = '''query($owner:String!,$name:String!,$cur:String){
 repository(owner:$owner,name:$name){
  issues(first:100,after:$cur,states:[OPEN,CLOSED]){
   pageInfo{hasNextPage endCursor}
   nodes{number labels(first:30){nodes{name}} milestone{title}
         projectItems(first:10){nodes{project{number}}}}}}}'''

def status(repo):
    pmap = PROJ_MWS if repo == "MWS" else PROJ
    cur, seen, gaps = None, 0, 0
    while True:                                          # pitfall 2: page to the end
        a = ["graphql","-f","query="+Q,"-f","owner="+ORG,"-f","name="+repo]
        if cur: a += ["-f","cur="+cur]
        r = gh(a)
        if r.returncode: return "ERROR — inspect manually"
        d = json.loads(r.stdout)["data"]["repository"]["issues"]
        for nd in d["nodes"]:
            seen += 1
            lbls = {l["name"] for l in nd["labels"]["nodes"]}
            ms   = nd["milestone"]
            ok   = len(lbls & TYPE) == 1 and len(lbls & SEV) == 1 and ms is not None
            if ok:                                       # milestone present -> check project
                tgt  = pmap.get(ms["title"])
                have = {pi["project"]["number"] for pi in nd["projectItems"]["nodes"]}
                if tgt and tgt not in have: ok = False
            if not ok: gaps += 1
        if d["pageInfo"]["hasNextPage"]: cur = d["pageInfo"]["endCursor"]
        else: break
    if seen == 0: return "empty — skip"
    return "PROCESSED" if gaps == 0 else f"UNPROCESSED ({gaps}/{seen} issues incomplete)"

names = subprocess.run(
    ["gh","api","--paginate","orgs/%s/repos?per_page=100" % ORG,
     "-q",".[]|select(.has_issues==true).name"],
    capture_output=True, encoding="utf-8").stdout.splitlines()
for repo in sorted(n for n in names if n and not skip(n)):
    print(f"{repo:18} {status(repo)}")
```

Queue every repo printed `UNPROCESSED` for Step 2; `empty` and `PROCESSED` are skipped. **Trust the script's verdict, not a list** — the former "already processed: PWG, MWS, PWK, GRA, FRI, AP90, AP, MD" assumption is exactly what let the false "done" reading through.

## Step 2 — Spawn one sub-agent per unprocessed repo

For each unprocessed repo found in Step 1, spawn an Agent (in parallel where possible) using this prompt template:

---

**Sub-agent prompt template** (fill in REPO_NAME):

```
You are applying the Sanskrit Lexicon issue-taxonomy runbook to the repo `sanskrit-lexicon/REPO_NAME`.

First, read the full runbook instructions:
  File: C:\Users\user\.claude\commands\cologne-issue-runbook.md

Then execute every phase in that file for `REPO_NAME`:
- ORG = sanskrit-lexicon
- REPO = REPO_NAME
- Clone the repo to C:\Users\user\Documents\GitHub\REPO_NAME if it is not already there
- Proceed through all 10 phases (audit → labels → type labels → severity → milestones → batch script → projects → verification → CLAUDE.md → README.md → commit → push)
- Use C:\Users\user\Documents\GitHub\PWG\ as the working directory for any temp scripts, named REPO_NAME_label.py, REPO_NAME_projects.py, etc.
- Delete temp scripts after use

The global CLAUDE.md at C:\Users\user\Documents\GitHub\CLAUDE.md contains the shared taxonomy reference.
All tools are pre-approved — proceed without asking for confirmation.
```

---

## Step 3 — Monitor

After spawning all sub-agents, report:
- Which repos were dispatched
- Any repos skipped and why
- Wait for all agents to complete, then summarise: repos processed, total issues labelled, any errors

## Notes

- GitHub API rate limit is 5,000 requests/hour per token. With many repos in parallel, stagger spawns by ~30 seconds if you see 403 rate-limit errors.
- Each sub-agent writes temp scripts to `C:\Users\user\Documents\GitHub\PWG\` with a repo-specific prefix to avoid collisions.
- Project node IDs (projects 1–4) are the same across all repos:
  - Project 1 (DTB): `PVT_kwDOAGGnOc4BW400`
  - Project 2 (DQ):  `PVT_kwDOAGGnOc4BW402`
  - Project 3 (SD):  `PVT_kwDOAGGnOc4BW404`
  - Project 4 (ME):  `PVT_kwDOAGGnOc4BW405`
