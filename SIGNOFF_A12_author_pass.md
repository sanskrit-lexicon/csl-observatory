# SIGNOFF A12 — author-voice pass, read-and-sign

_Created: 06-09-2026 · Last updated: 06-09-2026_

**Scope.** Manuscript: [paper-obs-t-error-typology.md](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/paper-obs-t-error-typology.md) (A12, "Surface, Not Substance: A Two-Axis Error Typology of Twelve Years of Correction to the Cologne Digital Sanskrit Lexicon"). Handoff: [H3857](https://github.com/gasyoun/Uprava/blob/main/handoffs/H3857-Fable_Uprava_all-articles-author-voice-pass-workflow_01.09.26.md). Pass run 06-09-2026 by Fable 5.1 (`claude-fable-5-1`). Voice, register and framing only; no number, claim or citation altered; mechanical drift gate ([tools/voice_drift_check.py](https://github.com/gasyoun/Uprava/blob/main/tools/voice_drift_check.py) against `origin/main`) CLEAN on all eight categories (422 numbers, 30 URLs, 4 DOIs, 1 citation, 7 IAST tokens, 29 headings, 42 table rows).

## 1. Voice calls made — each may be vetoed

| # | Location | Call | Rationale |
|---|---|---|---|
| 1 | Byline | ~~Contact email `sanskrit.research.institute@gmail.com` → `gasyoun@ya.ru`~~ — **reverted after adversarial verify:** a contact-address change is the author's call, not a voice call; original address restored, carried as flag §2.1 instead | Affiliation and ORCID line were never touched |
| 2 | Whole paper (23 sites) | First-person plural (we/our) → first-person singular (I/my) | Single-author paper; the author's standing voice is first-person singular where the venue allows (LREC-COLING and IJL both do). Reverting is a mechanical `I`→`we` sweep if a reviewer-facing plural is preferred |
| 3 | Abstract | "The two axes are genuinely orthogonal" → "The two axes are orthogonal" | Filler intensifier; the 0.1 % figure carries the claim |
| 4 | Abstract | "The central interpretive caveat is stated plainly:" → "One caveat governs every reading:" | "Stated plainly" is a candour tic (also removed at §4.6) |
| 5 | §1 Contributions | ~~Added one sentence after the (i)–(iv) list ("Of the four, the contribution I stake the paper on is the second: …")~~ — **reverted after adversarial verify:** the added sentence ranks the contributions and asserts a consequence ("measuring its own fallback heuristic") the abstract does not claim; sentence deleted | Meaning drift, not voice |
| 6 | §2 Adjacent corpora | "though our errors arise from OCR" → "though the errors here arise from OCR" | The errors are the corpus's, not the author's |
| 7 | §2 (Piotrowski) | "— exactly the CDSL record type" → ", which is the CDSL record type" | Repeated "exactly"/"precisely" (six sites); one kept in §4.2's sense, five trimmed |
| 8 | §2 Post-correction lineage | "converged on exactly the error granularity" → "converged on the error granularity"; "directly comparable in spirit" → "comparable in spirit"; "I read this lineage specifically as" → "I read this lineage as" | Intensifier trim; "directly ... in spirit" was self-cancelling |
| 9 | §3.1 | ~~"No figure in this paper hides that label." → "Every figure in this paper carries that label."~~ — **reverted after adversarial verify:** "carries" asserts every figure displays the label, a stronger claim than "does not hide"; original restored | Meaning drift, not voice |
| 10 | §4.2 | "for two legacy-data reasons we report rather than hide:" → "for two legacy-data reasons:" | Fake-candour clause |
| 11 | §4.3 | "is thus not a data-quality failure but the measurement that justifies…" → "is thus the measurement that justifies…, not a data-quality failure" | Leads with the positive reading; the "not X but Y" cliché demoted to a tail |
| 12 | §4.4 | "One corpus, four readings." → "One corpus thus admits four readings." | Verb restored to a telegram tagline |
| 13 | §4.6 | "Its provenance is stated plainly:" → "Its provenance is as follows:"; "Label stability was measured, not assumed:" → "Label stability was also measured:" | Candour tics |
| 14 | §5.5 | "Dictionaries differ in *where* their errors sit, not merely how many they have — a fingerprint, not just a count." → "Dictionaries differ in *where* their errors sit and not merely in how many they have; the location profile is a fingerprint, not just a count." — **partly reverted after adversarial verify:** "rather than a count" narrowed the scope (it excludes the count); the original "not just a count" is kept, the em-dash-to-semicolon restructuring stands | Double "not X, just Y" trimmed once; comparison and scope preserved |
| 15 | §5.8 | "— exactly the confusions a Sanskrit OCR…" → ": the confusions a Sanskrit OCR…" | Intensifier trim |
| 16 | §5.9 | "(the present author among them at 445, mostly headword)" → "(I am among them, at 445, mostly headword)" | Third-person self-reference is the plural voice's residue |
| 17 | §6 baselines | "the task is hard precisely because" → "the task is hard because" | Intensifier trim |
| 18 | §6 DOI | Removed the "✅" emoji from "**DOI.** ✅ Minted:" | Decorative emoji in manuscript prose; the paragraph's content is untouched (see flag 2) |
| 19 | §7 QA lesson | "is **not** semantic — it is spelling…" → "is not semantic; it is spelling…"; "reach it — which is precisely the class of corrector" → "reach it, which is the class of corrector" | Bold-for-emphasis and em-dash-as-copula |
| 20 | §8 Coverage gaps | "so its dense density figure is real" → "so its density figure is real" | Doubled word |
| 21 | §9 Conclusion | "resolve into a clear and slightly surprising picture: the corrections cluster exactly where meaning lives" → "answer the question the introduction posed (what was wrong, where, and how that changed) with one picture: the corrections cluster where meaning lives" | The conclusion now names the introduction's question before answering it; "clear and slightly surprising" was self-grading |
| 22 | §9 Conclusion | "a different and more human thing than a list" → "a different and more human record than a list" | Keeps the author's closing turn, drops "thing" |
| 23 | Header + footer | `Last updated` bumped to 06-09-2026; footer status paragraph gains "author-voice pass 06-09-2026 (SIGNOFF_A12_author_pass.md)" | Brief's header-note rule |

Not touched on purpose: "differs sharply"/"vary sharply" (magnitude wording, left as the author's comparison strength); the bold-lead paragraph style of §2 and §7 (house style for the venue); the title's "Surface, Not Substance" (a title trope, but §8 already fences it; venue call, not a voice call).

## 2. Substance flags carried (not fixed)

1. **Byline confirmation is still open.** The footer's "Pending human steps" names it. The manuscript keeps the original contact address `sanskrit.research.institute@gmail.com` (call #1, which swapped it to `gasyoun@ya.ru`, was reverted after adversarial verify). A human should confirm which address goes to the venue; a contact change is the author's call.
2. **§6 DOI paragraph reads as a repo log, not manuscript prose.** It records that a previously cited DOI (`10.5281/zenodo.15834721`) was false, the date of the live Zenodo check, the date the repo sweep landed, and a script filename (`scripts/fix_obs_t_doi.py`). For submission only the concept and version DOIs belong in the paper; the correction history belongs in the datasheet or the repo changelog.
3. **Footer is stale on the DOI.** "Pending human steps: … genuine Zenodo DOI mint (§6)" contradicts §6 itself, which states the DOI was minted 2026-08-16. Also the whole italic header paragraph (handoff ids, "single canonical A12 manuscript", retired-draft pointer) and the footer are editorial state, not submission text; strip both for the venue copy.
4. **§4.5 points to the wrong section.** "the gold-annotation gate described in §8" — the gate (frozen sample, two annotators, κ, P/R/F1) is described in §4.6; §8 only lists the outstanding human steps. Cross-reference not changed because it is a section reference.
5. **§4.3 link label vs target.** The text says [`obs_t_silver.json`] but the URL resolves to `reports/obs_t_silver.md`. Either the label or the target is wrong.
6. **§5.7 orphan comparison.** "with PUI (~56) nowhere near the bottom of the range" answers a question the paper never asks; it reads as a residue of an earlier revision that once ranked PUI last. Either motivate it or drop it.
7. **§1 "several hundred contributors" vs 208 named correctors.** Consistent only if the "several hundred" counts pre-merge aliases; §3.1 says aliases were merged onto 208 identities and unattested ones kept separate. A reviewer will ask which number is the population.
8. **Uncited reference entries.** Hartmann and James (1998), Svensén (2009), Wiegand (1998–), Kendall (1948), Mann (1945), Levenshtein (1966), Kapp and Malten (n.d.), Gebru et al. (2021) and Norvig (2007) are in the list but not cited by name in the body (Mann–Kendall, Damerau–Levenshtein, "Gebru-style datasheet" and "Norvig-style" appear as method names only). Either cite in place or trim the list to what LREC-COLING will accept as cited.
9. **Abstract vs §5.6 on H3.** The abstract says "the corrected trend table reports BH-adjusted q-values"; §5.6 says that after BH the series is "best reported as directional rather than as a set of significant trend claims" (all q > 0.05 in Table 5). The abstract's phrasing lets a reader assume significance; the body does not claim it. Wording of a claim's strength, so flagged rather than fixed.
10. **§4.6 first paragraph's "0.29 agreement" and "roughly 66 boundary rows"** are the only figures in the paper without a linked artifact; every other figure points at a report or CSV.
11. **Title claim vs §8 caveat.** "Surface, Not Substance" is defended in §8 as a claim about edit size and location only; a referee may still read it as "no correction changes meaning". Consider a subtitle-level hedge or keeping the §8 sentence in the abstract.

## 3. Read-and-sign

1. Reading time: about 30 minutes for the diff (23 voice calls, one paragraph added in §1, one sentence reworked in §9) plus the eleven flags above.
2. Proposed readiness after a human signs off on calls #1, #2 and #5 and rules on flags 2, 3 and 9: 4/5 (propose only; not set). The 5/5 bump waits on the human expert pass over the boundary rows that §8 already names.
3. Venue recommendation (recommendation only): LREC-COLING remains the right first target for a resource-plus-baselines paper of this shape; the IJL alternate would need the §2 lexicographic-structure paragraph expanded and the baselines section shortened. No submission action before 2026-11-01.

_Dr. Mārcis Gasūns_
