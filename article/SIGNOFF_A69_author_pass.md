# SIGNOFF A69 — author-voice pass

_Created: 06-09-2026 · Last updated: 06-09-2026_

**Scope.** Manuscript
[article/A69_pwg_scan_index_campaign.md](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/article/A69_pwg_scan_index_campaign.md)
(A69, readiness 3/5 at pass start), passed under
[H3857](https://github.com/gasyoun/Uprava/blob/main/handoffs/H3857-Fable_Uprava_all-articles-author-voice-pass-workflow_01.09.26.md)
by Fable 5.1 (`claude-fable-5-1`) on 06-09-2026. Voice, register and framing only; no
number, claim or citation altered; mechanical drift gate
([tools/voice_drift_check.py](https://github.com/gasyoun/Uprava/blob/main/tools/voice_drift_check.py)
against `origin/main`) CLEAN: numbers 155/155, URLs 33/33, citations 2/2, IAST 42/42,
headings 29/29, table rows 12/12.

## 1. Voice calls made — each may be vetoed

| # | Location | Call | Rationale |
|---|---|---|---|
| 1 | Header + status paragraph | `Last updated` bumped to 06-09-2026; status paragraph gains "Author-voice pass 06-09-2026 (SIGNOFF link)". | Brief's manuscript-header rule. |
| 2 | After status paragraph | Academic byline block added: `Mārcis Gasūns, independent scholar (ORCID 0000-0003-4513-884X), gasyoun@ya.ru`. | The status line itself listed "byline" as an open decision; the block is the standing EN form. Affiliation wording is a human call. |
| 3 | Abstract | "This paper describes the campaign as a measured object" → "I describe the campaign as a measured object". | First-person singular where the venue allows; no claim moved. |
| 4 | Abstract | "We state plainly what the data cannot support" → "I state plainly …". | Single-author paper carried a plural "we" in one sentence only; the rest of the paper is singular or impersonal. |
| 5 | §1, third paragraph | "This paper documents the campaign" → "I document the campaign"; the parenthetical "a completed (in its kāvya and kośa portion) volunteer campaign" unpacked into its own sentence: "The campaign is complete in its kāvya and kośa portion; the account is written against committed, cross-validated data rather than against recollection." | Same scope qualifier, same strength, readable without the mid-phrase bracket. |
| 6 | §1, third paragraph | One explicit contribution sentence inserted: "The contribution is a single one: a measured, cross-validated account of that campaign, with its registry committed so that every number below can be traced to it." | Assembled only from what the abstract ("describes the campaign as a measured object"), the status paragraph ("every number … is traced to committed campaign data") and §5.5 ("a measured, cross-validated account of one completed campaign … its committed registry") already say, at the same strength. The introduction previously had no contribution statement; §5.5 carried it alone. |
| 7 | §4.2, first sentence | "The striking process finding:" → "The first process finding:". | "Striking" is a filler intensifier; "first" ties the sentence to the abstract's "Two process findings stand out. First, … Second, …" (§4.2 = first, §4.3 = second). |
| 8 | §5.5 | "No novelty is claimed for … — both exist elsewhere" → "I claim no novelty for … ; both exist elsewhere". | Passive to first-person singular; em-dash as copula replaced by a semicolon. Hedge unchanged. |
| 9 | §6, opening | Prefixed "The introduction asked what the resulting infrastructure cannot yet do." before "Four items are open and committed as such:". | The introduction poses five questions; the paper has no conclusion section (adding a heading is out of scope), so the last question is answered where the open items are listed. No new section reference introduced. |

Not touched on purpose: the five bolded defect bullets in §3.4 (a real enumeration, each
item a checkable claim), the em-dash appositions elsewhere (they carry content, not
copula), the "not X but Y" sentences in §4.1 and §4.3 (they are comparative claims, not
rhythm), and every heading including the title (see flag 4).

## 2. Substance flags carried (not fixed)

1. **Stale provenance statement.** The abstract ("the sheet's own citation counts have
   undocumented provenance") and §2.2 ("the tracking sheet's citation-count column has
   undocumented provenance") say one thing; §5.1 (updated 16-08-2026) says the provenance
   is recovered — the column is the per-abbreviation total of `lsextract_all.txt`, 66 of 67
   rows matching exactly. The abstract and §2.2 need to be rewritten to the §5.1 state, or
   §5.1's "still" logic needs to be reconciled with them. A claim change: a human decides.
2. **Dangling section cross-references.** §2.2, §2.3 and §3.1 point to "§6.1" for the
   provenance discussion; the paper's §6 is "Future work" and the provenance subsection is
   §5.1. In the other direction, §5.1 says the dictionary-level shares are in "§2"; they
   are in §3.1. Mechanical, but a numbered reference, so left for a human.
3. **55 works vs 56 events.** §3.1 counts 55 works `done`; §3.3 reports "56 monthly
   index-completion events (done status)" and a publication-lag median "over 56 works".
   If a multi-volume work contributes two events the text should say so; if not, one of
   the two counts is off by one.
4. **Title vs. subject (recommendation only).** "Indexing 29,000 pages so a dictionary can
   cite them" — the dictionary already cites these pages; the campaign makes the existing
   citations resolvable. A title closer to the abstract would be "Indexing 29,000 pages so
   a dictionary's citations can be followed: the PWG scan-index campaign, 2025–2026".
   Heading text is untouchable in this pass.
5. **Status paragraph vs. body dates.** The header said `Last updated: 05-08-2026` while
   §5.1 and §5.3 cite artifacts dated 16-08-2026 and a regeneration after draft freeze;
   the status line still reads "full draft … every number … none is newly computed here".
   The header date is now bumped by this pass, but the status paragraph does not record
   the 16-08-2026 substance update that §5.1 documents.
6. **Byline vs. acknowledgements.** The acknowledgements credit @gasyoun with
   "recruitment and record-keeping" and name @funderburkjim, @Andhrabharati and
   @drdhaval2785 for verification, adjudication and implementation. A single-author
   byline over a campaign paper of this shape is a venue and authorship decision the
   status line already flags; the added block only supplies the standing form.

## 3. Read-and-sign

About 30 minutes: read the abstract and §1 against §5.1 (flag 1), fix the four §-references
(flag 2), settle the 55/56 count (flag 3), rule on the title (flag 4), then read the nine
voice calls above in the diff and veto any.

Proposed readiness after those rulings: 4/5 (propose only; 5/5 is a human bump). Venue
recommendation: none added — the status line's "venue decisions" remain open; the paper's
shape (measured account of a volunteer infrastructure campaign, committed data, CC BY 4.0)
suits a digital-humanities or lexicographic-infrastructure venue rather than a philology
journal, but that is a human choice.

_Dr. Mārcis Gasūns_
