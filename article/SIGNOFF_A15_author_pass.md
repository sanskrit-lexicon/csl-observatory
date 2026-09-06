# SIGNOFF A15 — author-voice pass

_Created: 06-09-2026 · Last updated: 06-09-2026_

**Scope.** Manuscript: [article/A15_github_ecosystem.md](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/article/A15_github_ecosystem.md) (*Measuring the Cologne Digital Sanskrit Dictionaries as a GitHub Maintenance Ecosystem*, paper A15). Handoff: [H3857](https://github.com/gasyoun/Uprava/blob/main/handoffs/H3857-Fable_Uprava_all-articles-author-voice-pass-workflow_01.09.26.md). Pass by Fable 5.1 (`claude-fable-5-1`), 06-09-2026. Voice, register and framing only; no number, claim or citation altered; mechanical drift gate ([tools/voice_drift_check.py](https://github.com/gasyoun/Uprava/blob/main/tools/voice_drift_check.py) against `origin/main`) CLEAN — numbers 489/489, URLs 58/58, IAST 4/4, headings 22/22, table rows 45/45.

## 1. Voice calls made — each may be vetoed

| # | Location | Call | Rationale |
|---|---|---|---|
| 1 | Header | `Last updated` bumped to 06-09-2026; status paragraph gains "Passes: author-voice pass 06-09-2026 (SIGNOFF link)" | Brief's manuscript-header rule; the status already lists the H672 pass |
| 2 | Draft byline | "Mārcis Gasūns" → "Mārcis Gasūns, independent scholar (ORCID 0000-0003-4513-884X), gasyoun@ya.ru" | Byline block was a bare name; the ORCID is written as a plain identifier, not a link, so the drift gate's URL multiset stays stable — add the `https://orcid.org/…` link at camera-ready. The status line "Byline: pending MG ruling" is kept |
| 3 | Abstract | "we find a paradoxical profile" → "I find"; "We argue that" → "I argue that" | Single-author paper; first-person singular where the venue allows |
| 4 | §1, end of para 3 | Added one sentence: "The contribution of this article is a single one: the seventh instrument — correction throughput measured over the dictionary text rather than over the platform — and the reading it forces of the six platform instruments beside it." | One explicit singular contribution statement; it restates what the abstract already claims ("new to this class of study") and what §3.7 delivers, adds no new claim |
| 5 | §3.2 | "Notably, **zero repositories are stale**" → "**Zero repositories are stale**" | Empty opener |
| 6 | §3.2 | "a point we return to" → "a point I return to" | First-person singular |
| 7 | §3.4 | "for a three-person volunteer operation, remarkably fast. But the distribution is savagely long-tailed" → "fast for a three-person volunteer operation. But the distribution is heavy-tailed" | Filler intensifier "remarkably"; grand epithet "savagely" |
| 8 | §3.7 | "2020 was literally a single-corrector year" → "2020 was a single-corrector year" | Filler "literally"; the parenthesis (269 commits, one person) already carries the fact |
| 9 | §5, opener | Added: "The introduction asked what it costs to keep the corpus alive and whether that work is sustainable; the profile answers in two halves." before "Measured as a software organisation…" | The question posed in §1 is the question the discussion answers; the transition names it |
| 10 | §5 | "The honest framing is that agents convert" → "In effect, agents convert" | Fake-candour opener |
| 11 | §5 | "We also make no labour-valuation claims" → "I also…"; "We conjecture" → "I conjecture" | First-person singular |

Left deliberately: "robust and fragile" in §5 is a substantive antonym pair, not decoration; "keep the reading honest" in §4.4 is a claim about the instruments, not candour; the heading "rising throughput on non-rising shoulders" (§3.5) is the author's own figure and headings were not touched.

## 2. Substance flags carried (not fixed)

1. **65 vs 67 bus-factor-1 repositories.** §3.1 body, the abstract and appendix row 3 say **67 of 76** (88%) have a bus factor of 1; the §3.1 heading says "sixty-five times over" and §5 says "65 repositories would lose their majority maintainer to a single departure". One of the two numbers is stale against [reports/bus_factor.md](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/reports/bus_factor.md).
2. **"At most five content correctors in any year" (§4.3)** contradicts §3.7 ("no year had more than four distinct content correctors"), §4.2 ("≤4 in any single year") and §5 ("at most four content correctors in any year"). The abstract's "five" is the git-era total of distinct appliers, which is compatible; §4.3's per-year "five" is not.
3. **Zero ORCIDs (§3.1, appendix row 3).** "None of the 16 human contributors has a registered ORCID" — the author (gasyoun) holds ORCID 0000-0003-4513-884X, now printed in the byline of the same paper. Either the claim means "no ORCID recorded on the GitHub profile / in the identity worksheet", in which case the wording should say so, or [reports/contributor_identity.md](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/reports/contributor_identity.md) is out of date.
4. **17 vs 16 contributors** is already flagged in the text as a generator defect in the bus-factor report; unchanged, but it stays open until the generator is repaired.
5. **Status paragraph** still carries "Venue: TBD (@DECIDE …)" and "Byline: pending MG ruling" — both need a ruling before any readiness bump; the byline block added here is the standard EN form, not the ruling.
6. **Appendix row 15 (117 agent-authored README PRs)** is ⬜, outside the reproducibility envelope by the paper's own account; a reviewer may ask for the ledger or a script that recounts from the PR API.
7. **§3.6 downstream-project union (18 = 10 curated ∪ 17 code-search, 9 shared)** is arithmetic the reader must do; a reviewer may ask for the list.

## 3. Read-and-sign

About 30 minutes: read the abstract, §1 para 3 (the added contribution sentence), §3.1 heading against its body, §4.3's "five", and §5's opener. Proposed readiness: 4/5 (propose only) — the manuscript is full-draft complete with a claim→artifact inventory, but flags 1–3 are internal inconsistencies a referee will catch, and the venue and byline rulings are open. Venue recommendation: none beyond the status line's own (LREC/JOHD family, after A13/A14 outcomes); the paper's data-availability section already meets JOHD's data-paper expectations. Submission freeze until 2026-11-01 applies.

_Dr. Mārcis Gasūns_
