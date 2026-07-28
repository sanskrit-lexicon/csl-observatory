# A12 (OBS-T) manuscript reconciliation — editorial ruling

_Created: 28-07-2026 · Last updated: 28-07-2026_

Executed under handoff
[H1759](https://github.com/gasyoun/Uprava/blob/main/handoffs/H1759-Fable_csl-observatory_a12-obs-t-manuscript-reconciliation_27.07.26.md)
by Fable 5 (`claude-fable-5`), 28-07-2026.

## The defect

Two rival A12 manuscripts coexisted with different titles, framings and headline
numbers:

| | [`reports/obs_t_paper_draft.md`](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/reports/obs_t_paper_draft.md) | [`paper-obs-t-error-typology.md`](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/paper-obs-t-error-typology.md) |
|---|---|---|
| Title | "OBS-T: A Longitudinal Error-Typology Corpus" | "Surface, Not Substance: A Two-Axis Error Typology" |
| Framing | nine one-axis labels, incl. the orthography/encoding confound | Phase-8 two-axis reframe (location × edit-type) |
| Events | 50,953 (stale snapshot) | 52,498 (released snapshot) |
| IAA | fresh cross-model κ = 0.906 section | "awaits a second annotator … we report no kappa here" |
| DOI | corrected false-DOI status | no DOI statement |

## The ruling

**The survivor is [`paper-obs-t-error-typology.md`](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/paper-obs-t-error-typology.md)
(repo root). [`reports/obs_t_paper_draft.md`](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/reports/obs_t_paper_draft.md)
is retired to a tombstone stub.** Grounds:

1. **The framing was already ruled.** The repo's own record
   ([`.ai_state.md`](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/.ai_state.md)
   Dev Notes) declares the Phase-8 two-axis reframe RESOLVED — "Author chose two clean
   axes". A one-axis manuscript cannot be the paper of record for a two-axis corpus.
2. **Its numbers are the released numbers.** Every headline figure in the two-axis
   manuscript re-verifies against the released snapshot and generated reports
   (table below). The one-axis draft's 50,953-event figures come from a superseded
   snapshot its own header says "must not be cited without a full manuscript
   regeneration".
3. **The pointers already lean this way.**
   [`STATUS.md`](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/STATUS.md)
   and [`docs/ERROR_TYPOLOGY_DESIGN.md`](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/docs/ERROR_TYPOLOGY_DESIGN.md)
   both named the root file as the manuscript; only
   [`Uprava/ARTICLES.md`](https://github.com/gasyoun/Uprava/blob/main/ARTICLES.md) and
   [`article/A15_github_ecosystem.md`](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/article/A15_github_ecosystem.md)
   still pointed at the retired draft (both repointed in this pass).

## What was carried across into the survivor

- **Byline block** (Gasūns, ORCID, email) — final byline confirmation stays a human call.
- **Abstract**: one validation sentence (cross-model κ, with its caveat).
- **§2**: the related-work survey (GEC corpora, OCR gold standards, DH correction
  logs, lexicographic formalisms, Sanskrit NLP/DCS).
- **§3.1**: deduplication + bulk-commit exclusion + identity-resolution notes,
  restated to the 208 release-safe corrector labels of the released snapshot.
- **§4.6 (new)**: gold-sample provenance in accurate wording (machine first pass, no
  human annotation, 0.29 = consistency of two heuristic processes on the historical
  hybrid axis); the full cross-model IAA block (κ = 0.906 [0.872–0.938], raw 92.8 %,
  4-group κ = 0.896, flip-rates 4.4 %/5.6 %, pre-registered, artifacts linked;
  explicitly cross-model, NOT human-validated); the 0/120 error-sample benchmark.
- **§6**: the DOI status warning (previously recorded DOI is false; nothing minted;
  do not submit with a placeholder).
- **§8**: "awaits a second annotator … we report no κ here" replaced with the
  measured cross-model result and the honest residue (no human adjudication yet;
  ~66 encoding ↔ orthography boundary rows).
- **References**: 16 entries carried (Bond & Paik, Bryant et al. 2019, Clematide,
  Haaf, Hellwig ×2, Kendall, Levenshtein, Mann, McCrae, Ng, Norvig, Piotrowski,
  Reul, Springmann, Yannakoudakis); "draft — author to finalise" and TODO markers
  removed.

Deliberately NOT carried: the one-axis §5 statistics tables (superseded axis and
snapshot), the stale baseline figures (0.388/7-class vs the released 0.638/6-class),
and the 210-corrector/33,561-derived counts (stale snapshot).

## Number verification (released snapshot, re-derived 28-07-2026)

Source of truth: `observatory/site/src/data/correction_events_release.csv`
(62,140,440 B) recounted directly, plus the generated reports and
[`validation/component_kappa_stats.json`](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/validation/component_kappa_stats.json).
Model: Fable 5 (`claude-fable-5`).

| Claim in survivor | Recounted value | Verdict |
|---|---|---|
| 52,498 events, 2014-03-18 → 2026-05-30 | 52,498; same span ([`obs_t_typology.md`](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/reports/obs_t_typology.md)) | ✅ |
| 33,755 derived / 18,743 inferred (64.3 %) | 33,755 / 18,743 | ✅ |
| 208 named correctors | 208 distinct `corrector_name` | ✅ |
| sense 17,778 (52.7 % of derived); markup 5,902; headword 5,823; citation 3,335; meta 624; grammar 293 | identical | ✅ |
| edit-type table (spelling 11,683 … transposition 491) | identical, all 9 rows | ✅ |
| median edit distance 2; 63 % ≤ 2; p90 20; max 508 | [`obs_t_rigor.md`](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/reports/obs_t_rigor.md) | ✅ |
| minor-edit rates (headword 85.6 %, sense 38.2 %, markup 5.2 %) + Wilson CIs | identical | ✅ |
| χ² = 26,192.5, dof 70, V = 0.432 [0.407, 0.482] | identical | ✅ |
| H3 trend rows (τ, p, q, first→last) | identical to rigor report | ✅ |
| density: PGN 160.8, BUR 91.4, PW 13,662 @ 80.1 | 160.82 / 91.37 / 13,662 @ 80.1 | ✅ |
| crosswalks: OCR sub 14,815, ins 14,713, del 11,018, seg 10,253; Katre add 20,546, sub 15,246, om 14,260, metath/haplo/ditto 491/496/231; b→v 341 | identical | ✅ |
| correctors: Funderburk 35,057, Patel 8,248, Gasūns 445 | identical | ✅ |
| latency median 12 / p90 73 / max 447 days | identical | ✅ |
| baselines 0.516 / 0.059 / 0.638 (macro-F1 0.453, majority 0.402) | [`obs_t_baselines.md`](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/reports/obs_t_baselines.md) | ✅ |
| κ = 0.906 [0.872–0.938], raw 92.8 % (362/390); 4-group 0.896 [0.855–0.935]; flips 4.4 %/5.6 % | `component_kappa_stats.json` | ✅ |
| 0/120 error-sample rate | [`obs_t_errorbench.md`](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/reports/obs_t_errorbench.md) | ✅ |

One fact was corrected during the merge rather than carried: the retired draft's
"28 aliases → 16 canonical identities, 210 correctors" does not describe the release
(which keeps unattested aliases like `dhaval_ejf` as separate labels, 208 total); the
survivor states the release behaviour.

## Open human decisions (NOT closed by this ruling)

- **§4.3/§4.6 gold-provenance wording** — accurate phrasing is now in the manuscript,
  but the H1272 `@DECIDE` in
  [`Uprava/GTD_NEXT_ACTIONS.md`](https://github.com/gasyoun/Uprava/blob/main/GTD_NEXT_ACTIONS.md)
  stays open for a human ruling on the final submission wording.
- **Byline** ("M. Gasūns and the CDSL community" vs sole author) — the survivor
  carries the sole-author block the retired draft used; final call is a human's.
- **Zenodo DOI mint** and **read-and-sign** — downstream, untouched.

_Dr. Mārcis Gasūns_
