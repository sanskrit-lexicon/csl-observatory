# Cologne maintainers call — 27 June 2026

**Attendees:** Gasūns · Jim Funderburk ([@funderburkjim](https://github.com/funderburkjim)) · Dhaval Patel · Andhrabharati
**Format:** verbal talking-points card — one number per bullet, glance and speak.
**Premise:** Jim has seen *only the noise*. The metrics pipeline, the roadmap, and the noise-gate are all news to him.
**One decision to get:** how does Jim want to mark a repo/thread *off-limits* to agents.

---

## 1. Lead with the number Jim has never seen

- There is a live metrics dashboard now — reproducible, monthly auto-refresh: **[csl-observatory dashboard](https://sanskrit-lexicon.github.io/csl-observatory/)**.
- The headline: **for 11 years (2014–2024) the backlog grew ~70 issues/year. 2026 is the first year it shrinks — net −833 in six months** (1,199 closed vs 366 opened). Source: [`data/timeseries_annual.csv`](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/data/timeseries_annual.csv) · [`reports/dashboard.md`](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/reports/dashboard.md).
- *"You've only seen the noise. Here's the thing the noise is attached to."*

## 2. Name the noise before Jim does — and show it is already gated

- 2025 looked like a flood (**+956 net**) — that was the one-time [issue-taxonomy labeling sweep](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/reports/dashboard.md), not content spam.
- As of **2026-06-27** there is a hard rule: agents post **only with concrete data** — line numbers, counts, a definitive answer. Documented in **[AI_CONTRIBUTION_POLICY.md](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/docs/AI_CONTRIBUTION_POLICY.md)**.
- Inconclusive findings go to **off-GitHub digest files**, never the threads: [question-research-findings.md](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/docs/question-research-findings.md) · [bug-triage-findings.md](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/docs/bug-triage-findings.md).
- Every agent comment is wrapped in a **collapsible `<details>`** so it can never bury a human reply.
- Last sweep: **130 question-issues reviewed, only 73 posted — 57 deliberately skipped**, including your active [PWG #44 preverbs](https://github.com/sanskrit-lexicon/PWG/issues/44) and [PWG #107 commentary](https://github.com/sanskrit-lexicon/PWG/issues/107) threads (Andhrabharati's).

## 3. The "good > harm" proof — for Andhrabharati

- He's fine with agents *if they prove more good than harm.* The ledger:
- **130 question-issues** got evidence comments; **9 are one-click ready-to-close** — see the ["ready to close" list](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/docs/question-research-findings.md).
- **84 bug-issues triaged → 10 new fixable bugs surfaced, 8 found already-fixed** (closeable now): [bug-triage-findings.md](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/docs/bug-triage-findings.md).
- Data assets built *for* the dictionaries, not just about them: Whitney–Grammar–DCS crosswalk (**24k triples**), 10-dict [etymology extraction dashboard](https://sanskrit-lexicon.github.io/csl-orig/), SCH+MW preface OCR with EN/RU translation.
- One correction already shipped end-to-end: AP90 `{#(X)#}`→`({#X#})`, **14 instances**, [csl-orig PR #2863](https://github.com/sanskrit-lexicon/csl-orig/pull/2863).

## 4. How it stays clean — *the real ask*

- Tiered model in **[AGENT_ROADMAP.md](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/docs/AGENT_ROADMAP.md)**:
  - **Tier A** — agent opens a PR with the exact diff; *you merge & close*.
  - **Tier B** — agent posts "still-present / already-fixed" verification; *you close*.
  - **Tier C / D** — needs your editorial decision first; agent never touches.
- Agents **never** close a question issue, and **never** act on `hard` / markup-design / editorial issues autonomously (**67 markup + ~200 content-enhancement** are off-limits by rule).
- **Ask Jim:** how do you want to flag a repo or thread as off-limits — a `no-agent` label? a list? *This is the one decision I need.*

## 5. Joint planning — what to point agents at next

- Ready to ship now, zero new tooling: **12 Tier-A bugs with exact diffs** — [csl-devanagari #41](https://github.com/sanskrit-lexicon/csl-devanagari/issues/41) / [#42](https://github.com/sanskrit-lexicon/csl-devanagari/issues/42) / [#43](https://github.com/sanskrit-lexicon/csl-devanagari/issues/43), [csl-orig #1537](https://github.com/sanskrit-lexicon/csl-orig/issues/1537) / [#1788](https://github.com/sanskrit-lexicon/csl-orig/issues/1788), [PWK #12](https://github.com/sanskrit-lexicon/PWK/issues/12), [VCP #20](https://github.com/sanskrit-lexicon/VCP/issues/20).
- Bigger question for the three of you: which backlog drains first — the **2,887 text-corrections** (70.2% of all typed issues, mostly [csl-corrections](https://github.com/sanskrit-lexicon/csl-corrections)) or the question/bug long tail?
- Decisions still blocking automation are tracked in [CROSS_REPO_DECISIONS.md](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/docs/CROSS_REPO_DECISIONS.md).

## 6. Close on the one decision you need

- *"I'm not asking you to trust the bot. I'm asking: where's the line you want it never to cross, and what do you want drained first?"*

---

## Numbers cheat-sheet (say these, don't read them)

| Number | Means | Source |
|---:|---|---|
| **−833** | net issues in 2026 H1 (first shrinking year ever) | [timeseries_annual.csv](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/data/timeseries_annual.csv) |
| **~70/yr** | net backlog growth 2014–2024 | [dashboard.md](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/reports/dashboard.md) |
| **+956** | 2025 net (the labeling-sweep spike, one-time) | [dashboard.md](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/reports/dashboard.md) |
| **78 / 5,365 / 51** | repos / total issues / contributors | [dashboard.md](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/reports/dashboard.md) |
| **2,887 (70.2%)** | text-correction = the dominant issue type | [dashboard.md](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/reports/dashboard.md) |
| **130 / 73 / 57** | question-issues reviewed / posted / skipped | [question-research-findings.md](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/docs/question-research-findings.md) |
| **84 / 10 / 8** | bugs triaged / new-fixable / already-fixed | [bug-triage-findings.md](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/docs/bug-triage-findings.md) |
| **2,801 / 1,291 / 957** | commits: Jim / Dhaval / Gasūns | [dashboard.md](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/reports/dashboard.md) |

---

## Link index — everything in one place

**Live dashboards**
- [csl-observatory — org metrics](https://sanskrit-lexicon.github.io/csl-observatory/)
- [csl-orig — etymology extraction](https://sanskrit-lexicon.github.io/csl-orig/)
- [csl-guides — CDSL user docs](https://sanskrit-lexicon.github.io/csl-guides/)

**Strategy & policy docs**
- [AGENT_ROADMAP.md](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/docs/AGENT_ROADMAP.md) — Tier A–D map of 820+ open issues
- [AI_CONTRIBUTION_POLICY.md](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/docs/AI_CONTRIBUTION_POLICY.md) — the noise-gate rules
- [question-research-findings.md](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/docs/question-research-findings.md) — 2026-06-27 question sweep
- [bug-triage-findings.md](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/docs/bug-triage-findings.md) — bug sweep
- [OBSERVATORY_ROADMAP.md](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/docs/OBSERVATORY_ROADMAP.md) — metrics strategy
- [RESEARCH_LAYER_ROADMAP.md](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/docs/RESEARCH_LAYER_ROADMAP.md) — paper pipeline
- [CROSS_REPO_DECISIONS.md](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/docs/CROSS_REPO_DECISIONS.md) — open editorial decisions
- [MAINTAINER_CONTINUITY_PACKET.md](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/docs/MAINTAINER_CONTINUITY_PACKET.md) — bus-factor / handoff
- [ORG_MAINTENANCE_LOG.md](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/docs/ORG_MAINTENANCE_LOG.md) — running change log

**Release artifacts (cut 2026-06-27)**
- [CHANGELOG.md](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/CHANGELOG.md)
- [Release v1.1.0](https://github.com/sanskrit-lexicon/csl-observatory/releases/tag/v1.1.0) — bundles the bot-noise policy (citable artifact for Jim)
- [Release v1.0.0](https://github.com/sanskrit-lexicon/csl-observatory/releases/tag/v1.0.0) · [Release v0.1.0](https://github.com/sanskrit-lexicon/csl-observatory/releases/tag/v0.1.0)

**Cross-repo hubs (Uprava — private, internal)**
- **GTD_NEXT_ACTIONS.md** — human DO / DECIDE / WAITING rollup
- **PROJECT_INTERLINKS.md** — data-flow dependency map
- **ARTICLES.md** — 33+ paper pipeline with readiness scores

**Ready-to-ship Tier-A issues**
- [csl-devanagari #41](https://github.com/sanskrit-lexicon/csl-devanagari/issues/41) · [#42](https://github.com/sanskrit-lexicon/csl-devanagari/issues/42) · [#43](https://github.com/sanskrit-lexicon/csl-devanagari/issues/43)
- [csl-orig #1537](https://github.com/sanskrit-lexicon/csl-orig/issues/1537) · [#1788](https://github.com/sanskrit-lexicon/csl-orig/issues/1788) · [PR #2863 (shipped)](https://github.com/sanskrit-lexicon/csl-orig/pull/2863)
- [PWK #12](https://github.com/sanskrit-lexicon/PWK/issues/12) · [VCP #20](https://github.com/sanskrit-lexicon/VCP/issues/20)
