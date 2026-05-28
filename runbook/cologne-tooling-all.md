Apply the **Cologne tooling-repo runbook** to every uncategorized non-dictionary repo in the org.

## Step 1 — Discover unprocessed tool repos

A tool repo is **unprocessed** if it has at least one issue AND none of its issues carry the `tech-debt`, `data-pipeline`, or `domain:*` labels (these are added only by the tooling runbook).

```sh
gh api "orgs/sanskrit-lexicon/repos?per_page=100" -q '.[] | select(.has_issues==true) | {name,open_issues:.open_issues_count}'

# For each candidate
gh api repos/sanskrit-lexicon/REPO/labels -q '[.[].name] | contains(["tech-debt"])'
# true = already processed; false = needs runbook
```

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
