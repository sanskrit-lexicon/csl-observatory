Apply the full Sanskrit Lexicon issue-taxonomy runbook to every unprocessed repo in the org.

## Step 1 — Discover unprocessed repos

Fetch all repos in the org and identify which ones still need the runbook. A repo is **unprocessed** if it has at least one issue AND none of its issues carry the `minor`, `medium`, or `hard` severity labels (these are added only by the runbook).

```sh
# List all org repos with issue counts
gh api "orgs/sanskrit-lexicon/repos?per_page=100" -q '.[] | select(.has_issues==true) | {name,open_issues:.open_issues_count}'

# For each candidate, check if taxonomy labels exist
gh api repos/sanskrit-lexicon/REPO/labels -q '[.[].name] | contains(["minor"])'
# Returns true = already processed, false = needs runbook
```

Skip repos with 0 issues. Skip repos that already have `minor` label (already processed). Also skip these known non-dictionary repos: `COLOGNE`, `csl-*`, `alternateheadwords`, `avlinks`, `rvlinks`, `literarysource`, `hwnorm1`, `hwnorm2`, `mw-dev`, `sanskrit-fonts`, `sanskrit-lexicon.github.io`, `santamlegacy`, `temp_corrections_*`, `test_cologne_push`, `Wil-YAT`, `ArabicInSanskrit`, `GreekInSanskrit`.

Already processed (skip): `PWG`, `MWS`, `PWK`, `GRA`, `FRI`, `AP90`, `AP`, `MD`.

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
