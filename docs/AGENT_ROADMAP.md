# Agent Roadmap — Sanskrit Lexicon Issue Automation

_Canonical location: [`csl-observatory/docs/AGENT_ROADMAP.md`](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/docs/AGENT_ROADMAP.md). Last compiled: 2026-06-27 (revised after P1+P2+P3 execution). Re-compile when new issues are opened or a skill ships._

**Scope:** 821 open issues across 68 repos in the `sanskrit-lexicon` org, surveyed 2026-06-26.
**Goal:** Map which issues agents can supply data for (humans close after), which need a new skill first, and in what order.

---

## Corrected picture (post P1/P2 audit)

The original counts treated label names as agent-readiness signals. They are not. Auditing the actual issue bodies revealed:

- `markup` issues (67) = editorial design discussions, not grep-and-replace patterns. **0 batch-ready.**
- `text-correction` issues (31) = mostly questions or already-applied corrections mislabeled as pending. **2 genuinely actionable** identified.
- `encoding` issues partially actionable; 5 in COLOGNE are SLP1 display questions, not source-file fixes.
- `question` and `bug` not yet audited body-by-body — counts stand but actionability unknown.

---

## Summary counts (org-wide, revised)

| Label | Count | Agent can supply data? |
|---|---|---|
| `content-enhancement` | ~200 | No — design/new-feature requests, human scope |
| `question` | 85 | Yes, with `cologne-question-research` skill (P3) |
| `bug` | 78 | Partially, with `cologne-bug-triage` skill (P4) |
| `markup` | 67 | No — all editorial discussions; `markup-batch` skill premature |
| `text-correction` | 31 (reclassified) | 2 of 31 agent-ready; rest are questions or already done |
| `link-target` | 23 | Semi — DTB pipeline, requires PDF-page index |
| `minor` (severity) | 361 | Severity ≠ actionability; ignore as readiness signal |
| `encoding` | 11 | ~5 in source files; rest are display/policy questions |
| `hard` | 10 | Human required before agents act |
| `scan-quality` | 3 | Human (physical scan) |
| `link-splitting` | 2 | DTB pipeline |
| unlabeled | 11 | CORRECTIONS repo — intentionally skipped (A2 decision pending) |

---

## Consolidated map: agent-supply-ready vs. skill-needed vs. blocked

### Tier A — Agent supplies fix, opens PR, human merges and closes (no new skill)

These have exact old→new text in the issue body or are trivially greppable. Agent writes the change file, runs XML/ET validation, opens PR, and posts a comment linking it. Human merges + closes.

| Issue | Dict | Fix type | Size |
|---|---|---|---|
| [csl-orig #1537](https://github.com/sanskrit-lexicon/csl-orig/issues/1537) | MW | `ruci` → `Ruci` at L=179760 | 1 line |
| [csl-orig #1788](https://github.com/sanskrit-lexicon/csl-orig/issues/1788) | MW | erase plant name, change `sup`→`rev` at line 592 | 1 line |
| [csl-orig #2821](https://github.com/sanskrit-lexicon/csl-orig/issues/2821) | STC | broken line-break in `s.v.` ref; grep stc.txt | ~2 lines |
| [csl-devanagari #43](https://github.com/sanskrit-lexicon/csl-devanagari/issues/43) | SKD | `£` → `ꣳ` (U+A8F3); line numbers given | exact |
| [csl-devanagari #42](https://github.com/sanskrit-lexicon/csl-devanagari/issues/42) | PWG | `~\` → `\~` at line 23689 | 1 line |
| [csl-devanagari #41](https://github.com/sanskrit-lexicon/csl-devanagari/issues/41) | MW | trailing space + duplicate `<e>` field; 3 exact diffs | 3 lines |
| [csl-apidev #24](https://github.com/sanskrit-lexicon/csl-apidev/issues/24) | all | old URL → new URL in `orphus.customized.js` | 1 line |
| [csl-apidev #10](https://github.com/sanskrit-lexicon/csl-apidev/issues/10) | all | wrong path for `<pic>` in `basicdisplay.php`; greppable | ~1 line |
| [csl-websanlexicon #60](https://github.com/sanskrit-lexicon/csl-websanlexicon/issues/60) | MW | malformed `<chg>` XML at L=592; body shows snippet | 1–2 lines |
| [SKD #13](https://github.com/sanskrit-lexicon/SKD/issues/13) | SKD | bracket mismatches; lines verifiable in skd.txt | ~10 lines |
| [PWK #12](https://github.com/sanskrit-lexicon/PWK/issues/12) | PW | `<ls>(X</ls>)` → `<ls>X</ls>`; regex given, 304 matches in pw.xml | 304 lines |
| [VCP #20](https://github.com/sanskrit-lexicon/VCP/issues/20) | VCP | `pUrbb` → `pUrvv`; 1474+236 occurrences in vcp2/vac2 | bulk |

**Status:** None of these have open PRs yet (except AP90 PR #2863 already open). All can start immediately.

---

### Tier B — Agent verifies current state, posts findings comment, human closes

These have diff lists or patterns in the issue body but the issue may already be partially fixed, or the exact scope needs confirmation. Agent greps source file, posts structured "still present / already fixed / N occurrences remain" comment.

| Issue | Dict | Verification task |
|---|---|---|
| [csl-orig #2811](https://github.com/sanskrit-lexicon/csl-orig/issues/2811) | MW | grep mw.txt for `avaDAra`; confirm `{as}`/`{am}` tags absent |
| [csl-orig #1762](https://github.com/sanskrit-lexicon/csl-orig/issues/1762) | MW | grep L=8622.1 in mw.txt; confirm supplemental insertion symbol |
| [csl-orig #630](https://github.com/sanskrit-lexicon/csl-orig/issues/630) | PD | grep pd.txt for flagged headwords from body diff list |
| [csl-orig #628](https://github.com/sanskrit-lexicon/csl-orig/issues/628) | MD | same — verify current state of md.txt against diff list |
| [csl-orig #627](https://github.com/sanskrit-lexicon/csl-orig/issues/627) | BEN | same — ben.txt diff list verification |
| [csl-orig #606](https://github.com/sanskrit-lexicon/csl-orig/issues/606) | multi | grep for `॥॥॥` and stray punctuation in Devanagari fields |
| [csl-apidev #45](https://github.com/sanskrit-lexicon/csl-apidev/issues/45) | all | read `servepdf.php`; check if `t`-prefix page convention is handled |
| SKD #1, #3; PWK #76, #77 | multi | already fixed; agent confirms + posts rationale for human to close |

---

### Tier C — Needs new skill before agents can help

| Skill | Issues unlocked | What it does |
|---|---|---|
| `cologne-question-research` | ~85 `question` issues | Fetch issue → classify question type (citation / morphology / encoding / policy) → gather evidence from csl-lslink / WhitneyRoots / FINDINGS.md → post structured findings comment |
| `cologne-bug-triage` | ~26 remaining `bug` issues above "needs-human" | Reproduce → classify → delegate to Tier A fixer or post "needs-server/rendering" comment |

The `cologne-question-research` skill has the higher ROI: 85 issues, all data assets already exist (Grammar+corpus crosswalk, csl-lslink, SanskritLexicography/FINDINGS.md), and even partial answers unblock human review.

---

### Tier D — Blocked; human editorial decision required first

| Category | Count | Why blocked |
|---|---|---|
| `markup` issues | 67 | All are editorial design discussions; no patterns settled |
| `content-enhancement` | ~200 | New-feature scoping — requires human prioritization |
| `hard` | 10 | Multi-file scope; human must define the work unit |
| `scan-quality` | 3 | Physical scan replacement |
| `link-target` / `link-splitting` | 25 | DTB pipeline needs PDF-page index (maintained separately) |
| `needs-human` bugs | 26 of 46 surveyed | Display rendering, browser UI, or unresolved editorial questions |

---

## Execution order

```
NOW (no skill needed):
  1. Tier A — ship PRs for the 12 agent-fixable bugs listed above
     Start with: csl-devanagari #41/#42/#43 (3 exact diffs, one PR each)
                 then csl-orig #1537, #1788
                 then PWK #12 (bulk substitution)
                 then VCP #20 (bulk substitution)
                 then csl-apidev #24, #10
                 then csl-websanlexicon #60
                 then SKD #13, csl-orig #2821
  2. Tier B — post verification comments on 8 already-greppable bugs
     Closes the loop so Jim/Dhaval can close without re-reading old issues.

SKILL BUILD:
  3. Build `cologne-question-research` → run on 85 question issues
     (highest ROI; all data exists; no PR noise — just comments)
  4. Build `cologne-bug-triage` → sweep remaining bugs
     (depends on text-correction PR skill being functional)

BLOCKED (await human):
  5. All markup/content-enhancement/hard issues — no agent action until editorial decisions land
```

---

## Execution plan

### P0 — Triage unlabeled issues (no new skill needed)

**Tool:** `/cologne-issue-runbook <REPO>` for dictionary repos; `/cologne-tooling-runbook <REPO>` for tooling / infrastructure repos (canonical files live in `csl-observatory/runbook/` and are installed under `~/.claude/commands/` on this machine).
**Issues remaining:** 11 currently open unlabeled issues, all in `CORRECTIONS` (`gh api "/search/issues?q=org%3Asanskrit-lexicon%20is%3Aissue%20is%3Aopen%20no%3Alabel&per_page=100"` after the IEG/LRV/PWG/csl-lslink/csl-websanlexicon/hwnorm1/temp repo slices on 2026-06-26).
**Repos to run on (in order):**

| Repo | Unlabeled |
|---|---|
| [CORRECTIONS](https://github.com/sanskrit-lexicon/CORRECTIONS) | 11 — intentionally skipped meta/cross-dictionary coordination repo |

**Status:** Inventory refreshed 2026-06-26. `COLOGNE` no longer appears in the open unlabeled search. IEG is processed: #1 = `content-enhancement`/`medium`/Major Enhancements/Project 4; #2 = `question`/`minor`/Structured Data/Project 3. LRV #31 is processed as `text-correction`/`minor`/Digitization Quality/Project 2; the repo still has older legacy multi-label cleanup separate from this unlabeled queue. PWG is processed: #186/#191 = `content-enhancement`/`medium`/Major Enhancements/Project 4; #194 = `question`/`minor`/Structured Data/Project 3. csl-lslink #3 is processed as `data-pipeline`/`major`/`domain:link-resolution`/Data Quality/Tooling Roadmap. csl-websanlexicon is processed: #72 = `infrastructure`/`minor`/Developer Experience/Tooling Roadmap; #73 = `bug`/`minor`/`domain:ui`/User Experience/Tooling Roadmap. hwnorm1 #21 is processed as `proposal`/`trivial`/`domain:normalization`/Community/Tooling Roadmap. temp_corrections_mw #2 and temp_corrections_ap90 #2 are processed as `question`/`trivial`/Community/Tooling Roadmap. Only CORRECTIONS remains in the open unlabeled search; `csl-observatory/runbook/cologne-tooling-all.md` explicitly says CORRECTIONS is a meta repo skipped under A2 and should be left untouched unless that decision is revisited.

---

### P1 — Text-correction PRs (skill: `cologne-text-correction-pr`)

**Issues cleared:** ~31 (`text-correction`) + ~11 (`encoding`)
**Top target repos:**

| Repo | text-correction | encoding |
|---|---|---|
| [csl-orig](https://github.com/sanskrit-lexicon/csl-orig) | 13 | 1 |
| [SKD](https://github.com/sanskrit-lexicon/SKD) | 4 | 1 |
| [MWS](https://github.com/sanskrit-lexicon/MWS) | 2 | 2 |
| [PWK](https://github.com/sanskrit-lexicon/PWK) | 2 | 0 |
| [VCP](https://github.com/sanskrit-lexicon/VCP) | 2 | 1 |
| [AP90](https://github.com/sanskrit-lexicon/AP90) | 2 | 0 |
| [PWG](https://github.com/sanskrit-lexicon/PWG) | 2 | 0 |

**Skill spec:**

```
Input:  repo name + issue number
Steps:
  1. Fetch issue body (gh issue view)
  2. Parse: locate the line number, old text, new text
  3. Identify source file (csl-orig/v02/<dict>/<dict>.txt or per-repo)
  4. Apply fix via updateByLine.py change file
  5. XML validate (make_xml.py — "All records parsed by ET" = pass)
  6. Open PR with: issue reference, before/after diff, validation result
  7. Post comment on issue linking the PR
Output: PR URL or "could not parse — needs human"
Fallback: if issue body is ambiguous, post a structured comment asking for
          clarification (old-line / new-line format) rather than guessing.
```

**Acceptance criteria:** PR passes XML validation, diff matches issue intent, issue is cross-linked.

**Status:** Skill scaffolded locally 2026-06-26 at `~/.codex/skills/cologne-text-correction-pr` with a CDSL correction workflow, `references/cdsl-correction-workflow.md`, and read-only `scripts/inspect_issue.py`. `quick_validate.py` passes. Smoke test on LRV #31 extracted line-level correction clues; dry forward-test on MWS #192 initially found no clues, then the inspector was improved to surface `ID=44378`, `ID=44050`, and quoted headword clues from prose/screenshot issues. MWS #192 was inspected locally and is **not** the first safe patch target: it requires semantic relocation wording from screenshots rather than exact old/new lines, and the MWS checkout has unrelated untracked preface work. csl-orig #2811 was also probed and is **not** a clean first patch: it is a broader print-consistent nominal-ending policy question (`as`, `am`, maybe `is`/`us`) rather than one exact correction. Next: use the skill on one cleaner correction branch before running a csl-orig batch.

---

### P2 — Markup normalisation batch

**Audited 2026-06-27.** Swept PWK (15), MWS (8), AP (7), AP90 (5), ACC (5) = 40 issues.

**Finding: 0 batch-ready issues** across all five repos. The `markup` label is used for:
- Bibliography/metadata work (PWK — pwbib*.txt, abbrev resolution)
- Ongoing design discussions (MWS — AB3 alternates, hwalt display, titular `<ls>`)
- Editorial decisions not yet settled (AP, ACC — homonym numbering, NLP rewrites)
- Already-done tracking issues left open

**One mechanical fix shipped:** AP90 `{#(X)#}` → `({#X#})` — 14 residual instances, PR [csl-orig #2863](https://github.com/sanskrit-lexicon/csl-orig/pull/2863). Did not require a skill.

**Issues to reclassify (markup → question or hard):** Most PWK/MWS issues are editorial discussions mislabeled as `markup`. Defer reclassification triage to a future pass.

**`cologne-markup-batch` skill: premature.** Markup issues in this org are design/editorial blockers, not grep-and-replace patterns. Build the skill only when a settled pattern with >50 instances emerges from an editorial decision.

**Status:** P2 complete as far as agents can take it without human editorial decisions.

---

### P3 — Research agent for `question` issues (new skill: `cologne-question-research`)

**Issues to address:** ~85 (`question`)
**Top target repos:**

| Repo | question | Character |
|---|---|---|
| [COLOGNE](https://github.com/sanskrit-lexicon/COLOGNE) | 20 | File conventions, editorial policy |
| [MWinflect](https://github.com/sanskrit-lexicon/MWinflect) | 8 | Morphology/paradigm — needs Grammar+corpus crosswalk |
| [CORRECTIONS](https://github.com/sanskrit-lexicon/CORRECTIONS) | 7 | Community corrections needing verification |
| [PWK](https://github.com/sanskrit-lexicon/PWK) | 5 | Source citation markup (BHĀGAVATAPURĀṆA, ṚV) |
| [ACC](https://github.com/sanskrit-lexicon/ACC) | 4 | Bibliography questions |

**Skill spec:**

```
Input:  repo name + issue number
Steps:
  1. Fetch issue body — classify question type:
     (a) citation/source — check csl-lslink, literarysource, ACC
     (b) morphology — check Whitney crosswalk, DCS CoNLL-U, MWinflect
     (c) encoding — check SLP1/IAST tables in sanskrit-util
     (d) editorial policy — check COLOGNE wiki / CORRECTIONS readme
     (e) text variant — check csl-orig + scan image if available
  2. Gather evidence from appropriate data source
  3. Post structured comment:
     - Question type + evidence found
     - Proposed answer or "evidence inconclusive — human decision needed"
     - If actionable: link to the code change it implies
Output: GitHub comment posted; issue tagged `question` (if not already).
Note:  Never close a `question` issue autonomously — post findings only.
```

**Status:** Skill not built. Depends on Grammar+corpus crosswalk (complete per memory) and csl-lslink data.

---

### P4 — Bug triage (new skill: `cologne-bug-triage`)

**Issues to address:** ~78 (`bug`)
**Top target repos:** csl-orig (21), csl-apidev (5), csl-devanagari (7), csl-websanlexicon (3)

**Skill spec:**

```
Input:  repo name + issue number
Steps:
  1. Fetch issue — classify bug type:
     (a) XML-structural — malformed tag, unclosed element
     (b) broken-link — dead <ls> target
     (c) encoding — wrong SLP1/IAST character
     (d) display — CSS/rendering glitch (csl-websanlexicon / csl-devanagari)
     (e) download — broken generated file
  2. Reproduce: for (a)/(b)/(c) scan the source; for (d)/(e) note as needs-server
  3. If (a)/(b)/(c): generate fix + open PR (delegates to cologne-text-correction-pr)
  4. If (d)/(e): post structured comment + label with correct milestone
Output: PR or structured triage comment.
```

**Status:** Skill not built. Depends on P1 (`cologne-text-correction-pr`) for the fix step.

---

## Dependency graph

```
P0 (triage unlabeled)       ← no deps, run now
P1 (text-correction-pr)     ← no deps, build next
P2 (markup-batch)           ← no deps (extends /cologne-markup-fix)
P3 (question-research)      ← no deps (data assets already exist)
P4 (bug-triage)             ← depends on P1
```

All four skills are independent of each other except P4→P1.

---

## What agents CANNOT close (human decision required)

- All `hard` issues (10) — large multi-file efforts; need scoping
- `scan-quality` issues (3) — require physical scan replacement
- `link-target` / `link-splitting` (25 combined) — DTB pipeline requires PDF-page index that is maintained separately; semi-automatable at best
- Any `question` issue where evidence is inconclusive — post findings, leave open
- Issues in [CORRECTIONS](https://github.com/sanskrit-lexicon/CORRECTIONS) that are community-submitted but editorially contested

---

## Files to read before building each skill

| Skill | Read first |
|---|---|
| `cologne-text-correction-pr` | `CLAUDE.md` §csl-orig workflow; `updateByLine.py`; `make_xml.py`; existing `/cologne-markup-fix` skill |
| `cologne-markup-batch` | `~/.claude/commands/cologne-markup-fix.md`; per-dict `<ls>` abbreviation lists in `csl-lslink` |
| `cologne-question-research` | `WhitneyRoots/` crosswalk; `csl-lslink`; `SanskritLexicography/FINDINGS.md`; `MWinflect` readme |
| `cologne-bug-triage` | `csl-orig` XML schema; `csl-websanlexicon` issue taxonomy |
