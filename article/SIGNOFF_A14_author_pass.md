# SIGNOFF A14 — author-voice pass, empirical companion

_Created: 06-09-2026 · Last updated: 06-09-2026_

**Scope.** Manuscript: [article/01-empirical-companion.md](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/article/01-empirical-companion.md) ("Methodological infrastructure of the Cologne Digital Sanskrit Dictionaries", the quantitative companion to the narrative report, ~6,000 words, EN, four authors). Handoff: [H3857](https://github.com/gasyoun/Uprava/blob/main/handoffs/H3857-Fable_Uprava_all-articles-author-voice-pass-workflow_01.09.26.md). Pass run 06-09-2026 by Fable 5.1 (`claude-fable-5-1`). Voice, register and framing only; no number, claim or citation altered; mechanical drift gate ([voice_drift_check.py](https://github.com/gasyoun/Uprava/blob/main/tools/voice_drift_check.py) against `origin/main`) CLEAN: 545 numbers, 6 URLs, 9 citations, 22 IAST tokens, 28 headings, 138 table rows count-identical before and after.

The paper is co-authored (Funderburk, Patel, Kālepu, Gasūns), so the plural "we" stays throughout; first-person singular would misattribute the work. The existing YAML byline block (name, affiliation, ORCID, email) was left untouched — see flags 1 and 2 below.

## 1. Voice calls made — each may be vetoed

| # | Location | Call | Rationale |
|---|---|---|---|
| 1 | §1, first sentence | "The Cologne Digital Sanskrit Dictionaries are presented in two voices in the present pair of articles." → "The present pair of articles presents the Cologne Digital Sanskrit Dictionaries in two voices." | Active voice; the articles are the agent. |
| 2 | §1, before the numbered list | "We focus on four contributions." → "The question this companion asks is whether the report's narrative claims survive an independent recount. Its one contribution is a dated, reproducible measurement of the ecosystem against which that recount can be repeated by anyone; we deliver it in four parts." | The pass asks for one explicit singular contribution statement and a question the conclusion answers. The four numbered items are unchanged; they are now parts of one contribution rather than four contributions. The "question" is the paper's own reconciliation programme (§2, §4.8), not a new claim. **Reverted after adversarial verify: substance — the added question/single-contribution framing is a claim the abstract does not make; original "We focus on four contributions." restored.** |
| 3 | §3, opening paragraph | "motivated by precisely this observation" → "motivated by this observation" | Filler intensifier. |
| 4 | §4.3 | "Three observations are warranted." → "Three points follow." | Empty opener; the three points are unchanged. |
| 5 | §4.5, after the contributor table | "The picture is striking: a single contributor (Funderburk) has authored…" → "A single contributor (Funderburk) has authored…" | "Striking" is a decorative intensifier; the 60.7 percent figure speaks for itself. |
| 6 | §4.5, Malten caveat | "We note one caveat: the very low commit count…" → "One caveat: the very low commit count…" | Empty opener. |
| 7 | §4.7 | "The headword integrity is excellent: in all 43 counted dictionaries…" → "Headword integrity holds throughout: in all 43 counted dictionaries…" | Grand epithet replaced by the observation itself (marker counts balance in every dictionary); the claim and the count are unchanged. **Reverted after adversarial verify: meaning — "holds throughout" is not the same claim as "is excellent"; original wording restored.** |
| 8 | §4.8, closing paragraph | "The discrepancies are not errors; they are different valid measures…" → "The discrepancies are not errors but different valid measures…"; bold removed from "figure of merit for cross-dictionary work" | The "not X; it's Y" two-clause pattern collapsed into one sentence; mid-sentence bold for emphasis dropped. Wording of the recommendation ("in our view, should standardise on the lemma") unchanged. **Partially reverted after adversarial verify: bold on "figure of merit for cross-dictionary work" restored (emphasis carried meaning); the one-sentence collapse stands.** |
| 9 | §7, opening line | "Three limitations of the present analysis are explicit." → "We make three limitations of the present analysis explicit." | Active voice; the authors are the ones making them explicit. |
| 10 | §8, last paragraph | Appended: "It also answers the question posed in the introduction: the report's figures survive an independent recount once the unit behind each figure is named." | Closes the loop opened by call 2. Restates §4.8's finding ("mutually consistent once the relevant unit is identified") in the same hedging strength; nothing new is claimed. **Reverted after adversarial verify: substance — the appended sentence asserted a recount verdict the paper does not make; sentence deleted.** |
| 11 | Header line | `Last updated` bumped 05-09-2026 → 06-09-2026 | Per the pass contract. The manuscript has no status paragraph listing prior passes, so no pass note was added inside it. |

Not touched, deliberately: the abstract's four-item enumeration ("its founders, its disputes, its lost archives, its hopes") is a real list, not rhythm padding; the em dashes are parenthetical, not copular; the three §4.6 regime bullets carry distinct openers.

## 2. Substance flags carried (not fixed)

1. **Byline email.** The YAML block gives `gasyoun@gmail.com`; the standing academic byline is `gasyoun@ya.ru`. A human should decide which address goes on this paper (the co-authored YAML block was not edited).
2. **Affiliation string.** `Sanskrit Zealots's Society / Russia, Obninsk` carries a doubled possessive (`Zealots's`); the intended form is probably `Sanskrit Zealots' Society` or the current independent-scholar wording. Not changed: it is inside the shared author block.
3. **Co-author ORCIDs are placeholders** (`PLACEHOLDER-FUNDERBURK`, `PLACEHOLDER-PATEL`, `PLACEHOLDER-RAO`) and §5.4 says "ORCIDs are placeholders pending registration". These must be filled or the lines dropped before any submission.
4. **Contributor table vs Figure 1 count.** §4.6 states Figure 1 covers n = 16 commit-author identities after alias merge; the §4.5 table lists 9 humans and excludes 3 named bots (12 identities). The four remaining identities are neither listed nor described. A human should confirm the table's "top human contributors" cut-off (it goes down to a single commit for Malten, yet omits four identities) or add a sentence stating what was omitted.
5. **§2 vs §4.5 spans for Rao.** §2 quotes the report's span for Kālepu as 2021–2025; the §4.5 table gives his commit span as 2021–2023. The difference is explained implicitly (commit record vs report's membership span) but not stated; one clause would settle it.
6. **Two different report figures for issue counts.** §2 and §4.1 both reconcile the report's "over 5,400 issues and pull requests across 76 repositories" with the snapshot's 5,172, attributing the gap to June-2026 growth and the two-fork census difference. The reconciliation paragraph appears twice with near-identical content (§2 and §4.1); a human should decide whether one instance should be cut. Not touched: cutting it would remove numbers.
7. **§4.7 "approximately 3.8×" is stated as a hypothesis to be tested** ("should be empirically tested… see `csl-observatory` issue queue") but no issue number is given, unlike §7's "issue #20". Consider naming the issue or dropping the pointer.
8. **§4.8 table, "MW: 110 vs. PWG: 245" row.** The explanation "the report measures a different unit (likely character count of definition text, excluding tags)" is a guess flagged as such ("likely"). Fine as hedged; noted only because the abstract claims that every figure is regenerable, and this one is not.
9. **Date drift is documented, but the YAML `date: 2026-07-11` predates the licence-remediation data (June 2026) it already cites** — consistent — while the header line now says 06-09-2026. Harmless, but a submission pack should carry one date.
10. **Report title.** The subtitle and abstract cite "Gasūns, *Report on Cologne Digital Sanskrit Lexicon Project* (forthcoming)". The sibling file in this folder is `00-report-narrative.md`; make sure the final title of the report matches before the two are submitted as a pair.

## 3. Read-and-sign

About 30 minutes: read §1 (calls 1–2) and the last paragraph of §8 (call 10) as the only framing changes; skim §4.5–§4.8 for calls 5–8; rule on flags 1–4 (byline, affiliation, ORCIDs, Figure 1 count) since those are the ones a referee will notice.

Proposed readiness: 4/5 (proposal only; not set). The prose is clean and every number is reconciled; what blocks 5/5 is the shared author block (flags 1–3) and the Figure 1 / table mismatch (flag 4), both of which need the co-authors.

Venue: no change recommended. The paper is written against the Indo-Iranian Journal CSL and pairs with the narrative report; a digital-humanities data-paper venue (e.g. Journal of Open Humanities Data) would also fit the infrastructure sections, but that is a recommendation only. No submission before 2026-11-01.

_Dr. Mārcis Gasūns_
