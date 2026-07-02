# A13 «CDSL report (narrative)» — go/no-go review

_Created: 02-07-2026 · Last updated: 02-07-2026_

Reviewed by Fable 5 (`claude-fable-5`), 02-07-2026, against
[`article/00-report-narrative.md`](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/article/00-report-narrative.md)
(1,522 lines, ~11k words), the
[`article/README.md`](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/article/README.md)
build notes, [`article/refs.bib`](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/article/refs.bib),
observatory data ([`manifest.json`](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/data/manifest.json)),
and the published
[Indo-Iranian Journal author instructions](https://brill.com/fileasset/downloads_products/Author_Instructions/IIJ.pdf).

## Verdict: **GO — conditional**

The paper should be sent to the Indo-Iranian Journal. Its core value is
irreplaceable: a first-person, primary-source history of CDSL 1994–2025 by the
founder of the sanskrit-lexicon organisation, with dates, names, private
correspondence, and institutional detail that exist nowhere else and that no
reviewer can supply from the literature. Nothing structural needs to change —
the voice, the arc (1997 report → point-by-point 2025 audit → future plans),
and the length (~11k words, IIJ publishes longer) are all right for a
review-article/report genre piece.

It is **not sendable today**. The blockers are bounded: one agent
copy-edit + bibliography session, then four decisions only M.G. can make.
Estimated distance to submission: **one agent session + ~2 h of M.G.**

---

## What M.G. must do to send it (the exact list)

1. **Decouple from A14 (recommended) — or state the pairing in the cover
   letter.** ARTICLES.md gates A13 on companion A14, which sits at 3/5 with
   all four co-author ORCIDs placeholder and 9 contributors unresolved — and
   multi-author consent for A14 is an external dependency with no date. IIJ
   reviews each manuscript on its own; the narrative explicitly "may also be
   read independently" (article README). **Recommendation: submit A13 alone
   now, cite the companion as "in preparation".** Waiting for A14 is the
   single biggest schedule risk on this paper.
2. **Decide the private-correspondence quotes (§3.2, §3.5.3, §4.2.1).** The
   draft quotes verbatim: two 2005 letters by Thomas Malten (one addressed to
   a third party), a 2013 personal email, and Scott Rhodes from an internal
   volunteer call. Letters and emails are the writer's copyright, and IIJ
   reviewers will ask. Options: (a) obtain one-line permissions from Malten
   and Rhodes — cheap, both reachable; (b) paraphrase with "(personal
   communication, 2005/2013)"; (c) keep verbatim and accept the risk. **(a)
   for Malten, (b) elsewhere is the recommended mix.**
3. **Decide the four sharp passages** — keep (it is your voice and your
   record) or soften: Poona as *kūpamaṇḍūka* + "no support … to come from
   Poona" (§5.1.3); "Baroda is out of the game" (§5.1.2); Manipal project
   "discontinued" (§5.1.3 — verify before asserting); derived sites as "some
   just a knockoff" (§2.3.1). Recommendation: keep the judgments, ground each
   in one verifiable fact, drop the epithets that name living colleagues'
   institutions without evidence in the text.
4. **Confirm the byline block**: "Sanskrit Zealots's Society" is
   ungrammatical (Zealots' or Zealot's — and consider whether IIJ should
   carry this affiliation or "Independent scholar, Obninsk"); the draft uses
   gasyoun@gmail.com while the canonical manuscript byline uses
   gasyoun@ya.ru; ORCID 0000-0003-4513-884X is absent and should be added.
5. After the agent pass (below): **read the diff, then email** the Word/RTF +
   fonts-embedded PDF to the IIJ Editors-in-Chief (IIJ takes submissions by
   email, not a portal).

## Agent fix pass (one session, before the email)

**A. Verifiable-number corrections — these would be caught in review:**
- Abstract claims "**6400+ issues by 2025**" — the observatory's own
  `manifest.json` records **5,413 issues** (5,324 excluding PRs) as of the
  2026-06 snapshot. Correct the figure or re-scope the claim (e.g. "over
  5,400 issues and pull requests across 76 repositories"). Use
  `manifest.json`, not `summary.json`.
- "**392600+ normalized entries**" — attach the source (hwnorm1) or drop the
  digit precision.
- §3.6.2: "P.K. Gode, the last surviving editor, passed away in **2021**" —
  P. K. Gode the Apte-edition editor died in **1961**; the 2021 date is
  almost certainly wrong, and the public-domain argument (60 years from
  Y. G. Joshi's death in 1963 → 2023) must be restated with verified dates,
  since it underwrites the announcement that AP is now served publicly.
- §2.3.2 vs §5.1.6: the 41,6 % figure is used for two different denominators
  (identical citation sources vs "cases covered in MW") — reconcile, and use
  a decimal point (41.6 %) throughout.
- "482,400 visitors in 2019" — add the source (server analytics) in a
  footnote.

**B. Bibliography (the largest single work item).** In-text author-year cites
do not resolve: *Jachertz 1983* (cited 3×) is absent from the reference list;
*(Gasūns 2006)* and *(Gasūns 2024)* cannot be matched against the undated
conference-talk list in §7.1; *(Kretov and Leonchenko 2021/2022)* omits
Gasūns, who is a co-author in the listed entries; *(Böhtlingk 2007)* is
actually Brückner & Zeller (eds.) 2007 and appears twice under different
forms. Convert §7.1 to a single alphabetised, IIJ-style reference list;
conference talks without published proceedings move to footnotes. Note
`refs.bib` currently serves only the companion and contains two entries still
marked "Reference TBD" (`malten1997`, `kapp2009`) — resolve or remove if the
narrative switches to the .bib.

**C. IIJ formatting:** headings must be **text, not numbers** (whole draft is
numbered, and the numbering is itself broken: §5.2.2 precedes §5.2.1, there is
no §5.2, references are numbered "7.1/7.2" outside any §7); add 4–6
**keywords** after the abstract; assemble in IIJ order (title page → abstract
→ keywords → body → acknowledgements → references).

**D. Copy-edit garbles** (surgical, do not touch the voice): "AI **alove**",
"**doen't**", "**Hardvard**-Kyoto", "**Atharhaveda**", "21^th^", "Zealots's",
"compiled in the last millennia" (abstract — presumably "the last two
centuries"), "dictionaries took him as a hostage", normalise
"typoe/typoes" → "typo/typos" (used inconsistently against §4.2.3's own
'typos'), and complete or visibly ellipsize the truncated German lines in the
§5.1.4 quotation table ("…herausg. von R. ROT", "…ein sys", "…is be").

**E. Build plumbing:** `article/indo-iranian-journal.csl` referenced by the
README **does not exist**; the README build command covers only the
companion. Add the CSL (Brill provides one) and a build line for the
narrative so the submission PDF is reproducible.

## What is genuinely strong (leave alone)

The 1997-report audit frame (§3.1); the three-types-of-changes taxonomy
(§4.2.3) — citable and new; the link-target typology (§5.1.5) with live
URLs; the contributor chronology (§3.5.2); the honest treatment of the
Malten copyright episode as lived history; the Nāgabhūṣaṇarāvu portrait; the
MW/PWG lemma-overlap numbers (once sourced to Gasūns 2024). The Himalayas
simile in the abstract is a signature line — keep it.

---

_Dr. Mārcis Gasūns_
