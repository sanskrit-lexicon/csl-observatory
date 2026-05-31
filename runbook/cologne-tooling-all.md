Apply the **Cologne tooling-repo runbook** to every uncategorized non-dictionary repo in the org.

## Step 1 — Discover unprocessed tool repos

A tool repo is **processed** only when **every one of its issues** carries exactly one type label, exactly one severity label, and a milestone (`discussion`-tagged issues are milestone-exempt). It is **unprocessed** if it has ≥ 1 issue and *any* issue falls short. Repos with 0 issues are skipped.

> ⚠️ **Decide per-issue, never from label definitions.** `gh api repos/ORG/REPO/labels -q '[.[].name] | contains(["tech-debt"])'` only tells you the `tech-debt` label *exists* in the repo — not that issues carry the taxonomy. The dictionary rollout hit exactly this on 2026-05-31: a label-definition check marked ~20 repos "done" over ~165 unlabelled issues.

Three pitfalls the detection must avoid:

1. **Per-issue completeness, not label presence.** Confirm *each* issue has exactly 1 type + 1 severity + 1 milestone (`discussion` exempt) — not merely that the labels exist.
2. **Paginate.** REST `…/issues?per_page=100` returns only the first page; large tool repos (`COLOGNE`, `csl-orig`: 200+ issues) hide everything past issue 100 — including issues that already carry *multiple* type labels. Loop GraphQL `repository.issues(first:100, after:$cur)` on `pageInfo.hasNextPage`.
3. **Exclude PRs.** REST `/issues` includes pull requests (dependabot bumps, docs/Pages-fix PRs). GraphQL's `issues` connection excludes them by construction — use it.

Detection script (per-issue, paginated, PR-free — mirrors the org-wide verifier `_verify_clean.py`):

```python
import subprocess, json, sys
sys.stdout.reconfigure(encoding='utf-8'); sys.stderr.reconfigure(encoding='utf-8')

ORG  = "sanskrit-lexicon"
TYPE = {"bug","regression","tech-debt","dependency","security","feature","enhancement",
        "performance","documentation","docs-api","infrastructure","data-pipeline",
        "cross-repo","build-tooling","question","proposal","discussion"}
SEV  = {"trivial","minor","major","critical"}

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
   nodes{number labels(first:30){nodes{name}} milestone{title}}}}}'''

def status(repo):
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
            ok = (len(lbls & TYPE) == 1 and len(lbls & SEV) == 1
                  and (nd["milestone"] is not None or "discussion" in lbls))
            if not ok: gaps += 1
        if d["pageInfo"]["hasNextPage"]: cur = d["pageInfo"]["endCursor"]
        else: break
    if seen == 0: return "empty — skip"
    return "PROCESSED" if gaps == 0 else f"UNPROCESSED ({gaps}/{seen} issues incomplete)"

# all repos with issues; cross-reference the skip lists below to route dictionary/archive repos
names = subprocess.run(
    ["gh","api","--paginate","orgs/%s/repos?per_page=100" % ORG,
     "-q",".[]|select(.has_issues==true).name"],
    capture_output=True, encoding="utf-8").stdout.splitlines()
for repo in sorted(n for n in names if n):
    print(f"{repo:28} {status(repo)}")
```

Queue every repo printed `UNPROCESSED` (after routing dictionary/archive repos via the skip lists below). Trust the verdict over any "already-processed" assumption — `csl-observatory` in particular must be re-checked (it carries mistaken dictionary labels; see below).

### Skip these (dictionary repos — use `cologne-issue-runbook.md` instead)
`PWG`, `PWK`, `MWS`, `MD`, `AP`, `AP90`, `GRA`, `FRI`, `SCH`, `DCS`, `VCP`, `ApteES`, `SKD`, `MCI`, `CORRECTIONS`, `WIL`, `BHS`, `VEI`, `ACC`, `KRM`, `BUR`, `CAE`, `CCS`, `STC`, `BEN`, `BOR`, `INM`, `BOP`, `LRV`, `AMAR`, `SHS`, `KNA`, `KOW`, `PUI`

### Skip these (archives, no triage needed)
`santamlegacy`, `temp_corrections_*`, `test_cologne_push`, `Wil-YAT`, `MW72` (legacy 1872 dict, low activity)

### Already-processed (skip)
`csl-observatory` (was processed under the dictionary runbook by accident — needs **re-processing** with the tooling runbook to swap label sets).

### Tool repo categories and processing order

Process in this order (most foundational first):

1. **Data stores** (foundational): `csl-orig`, `csl-corrections`, `csl-pywork`, `csl-sqlite`
2. **Converters** (depend on data stores): `csl-devanagari`, `csl-json`, `csl-ldev`, `csl-lnum`, `cologne-stardict`
3. **Processing tools**: `hwnorm1`, `hwnorm2`, `csl-inflect`, `MWinflect`
4. **Linking tools**: `csl-lslink`, `alternateheadwords`, `literarysource`, `avlinks`, `rvlinks`
5. **Scanned books**: `csl-kale`, `csl-westergaard`, `csl-whitroot`
6. **Web backend**: `csl-apidev`, `mw-dev`
7. **Web frontend**: `csl-app`, `csl-websanlexicon`, `csl-homepage`, `csl-doc`, `sanskrit-lexicon.github.io`
8. **Build/meta**: `cologne-hugo`, `sanskrit-fonts`, `csl-newsletter`, `COLOGNE`
9. **Cross-script add-ons**: `ArabicInSanskrit`, `GreekInSanskrit`

Plus the special meta repo: `csl-observatory` (re-process with tooling labels).

## Step 2 — Spawn one sub-agent per repo

Sub-agent prompt template:

```
You are applying the Cologne tooling-repo runbook to the repo `sanskrit-lexicon/REPO_NAME`.

First, read the full runbook:
  File: C:\Users\user\Documents\GitHub\csl-observatory\runbook\cologne-tooling-runbook.md

Then execute every phase for `REPO_NAME`:
- ORG = sanskrit-lexicon
- REPO = REPO_NAME
- Detect category (Phase 0) — use the table in the runbook
- Apply the category-specific domain labels
- Proceed through all 17 phases
- Use C:\Users\user\Documents\GitHub\PWG\ for temp scripts named REPO_NAME_label.py, etc.
- Delete temp scripts after use

The shared tooling taxonomy lives in the runbook. All tools are pre-approved — proceed without asking.
```

## Step 3 — Monitor and report

After spawning all sub-agents, report:
- Repos dispatched (with detected category)
- Repos skipped (with reason)
- Wait for all agents to complete
- Summarise: total tool issues labeled, breakdown by category, any errors

## Notes

- GitHub API rate limit is 5,000 req/hour per token. Stagger spawns by ~30s if 403s appear.
- Tool repos vary widely in size — some have 200+ issues (`COLOGNE`, `csl-orig`), others have 1–2.
- The two **org-level tooling projects** (Stability & Quality, Capabilities & Roadmap) only need to be created once (Phase 6). After the first repo creates them, subsequent repos reuse them.
- For `cross-repo` issues, the assigned sub-agent links companion issues in the body before assigning the label. The next runbook iteration auto-updates `CROSS_REPO_INDEX.md` in each repo.
- `csl-observatory` is special: it was processed earlier with **dictionary** labels (mistakenly). Phase 0 should detect this and Phase 3 should remove the dictionary type labels (`link-target`, `text-correction`, etc.) before applying tool labels.
