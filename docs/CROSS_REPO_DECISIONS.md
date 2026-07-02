# Cross-Repo Decisions Needed — Master Index

_Created: 14-06-2026 · Last updated: 02-07-2026_

Consolidated list of every item across the Sanskrit Lexicon repos that is
blocked on a human decision, a credential/access grant, or a scholarly
review. This is the **org-wide** companion to the observatory-scoped
[`DECISIONS_NEEDED.md`](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/docs/DECISIONS_NEEDED.md).

**Edition of 2026-07-02** — full re-adjudication by Fable 5 (`claude-fable-5`),
verified against live repo state (six read-only sweeps over MWS, csl-atlas,
VisualDCS, WhitneyRoots, csl-apidev/csl-standards/csl-corrections,
IndologyScholars/BookIndex/RuWritingStyles, SanskritKaraoke/CommentaryStrategies,
csl-observatory) plus the 2026-07-02
[Uprava GTD](https://github.com/gasyoun/Uprava/blob/main/GTD_NEXT_ACTIONS.md).
Of the 2026-06-14 edition's items, **12 are closed** (§0 below) and the
survivors are re-ranked. Every surviving item now carries a **Fable verdict**:
**Recommend** (an agent may proceed on this basis), **Decide** (genuinely
M.G.'s call, options priced), or **Drop/Park** (premise stale or premature).

> Agent note: when M.G. asks "what's next?", surface this list. Items are
> ordered by leverage — Tier 1 unblocks the most with the least effort.

---

## 0. Closed since 14-06-2026 (12 items — do not re-litigate)

| # | Item (14-06 wording) | Resolution + pointer |
|---|---|---|
| 1 | csl-observatory C1 — `TOOLING_AUDIT_TOKEN` | **Premise was a misread** — the secret was set all along; downgraded 2026-06-29 (ORG_MAINTENANCE_LOG via GTD). Residual: M.G. glances at the Actions tab once to confirm green. |
| 2 | csl-apidev — network blocked v1.2 feedback comment | **Posted** 2026-06-11 by @gasyoun on [csl-apidev#26](https://github.com/sanskrit-lexicon/csl-apidev/issues/26). |
| 3 | csl-atlas — R2 checkpoint, 10 rows | **Reviewed-ok ×10** (reviewer gasyoun, 2026-06-12) in [`r2-checkpoint-review.json`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/src/data/review/r2-checkpoint-review.json); applied via PR #88. |
| 4 | csl-atlas — [PR #88](https://github.com/sanskrit-lexicon/csl-atlas/pull/88) canonical-packet decision | **Merged 2026-06-14** (commit `4122230`) — decided the same day the 14-06 edition was written. |
| 5 | CommentaryStrategies — C0.3 specimens → D2 model choice | **Decided by M.G. 2026-07-01**: Model II, two-tier hybrid («модель II — двухъярусный гибрид», [`.ai_state.md`](https://github.com/gasyoun/CommentaryStrategies/blob/main/.ai_state.md)). |
| 6 | csl-observatory A4 — license decision matrix | **Approved 2026-06-17**; RH1 rollout **complete** across ~36 repos ([`RH1_LICENSE_ROLLOUT_LOG.md`](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/docs/RH1_LICENSE_ROLLOUT_LOG.md)): none 41→6, NOASSERTION 21→0. |
| 7 | csl-observatory A7 — bus-factor accepted-risk (DCS, KNA, KOW, MCI, santamlegacy) | **Accepted-risk recorded** per repo in [`BUS_FACTOR_ACTION_PLAN.md`](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/docs/BUS_FACTOR_ACTION_PLAN.md). |
| 8 | csl-corrections — KRM license mismatch | **No mismatch exists** any more: KRM `LICENSE` + `CITATION.cff` both CC-BY-SA-4.0; csl-corrections both GPL-3.0 (RH1 normalisation). |
| 9 | Salt Q6 — real apidev controller path | **Live** at `/scans/awork/apidev/api1/` (`salt_entries/ids/graphql.php`), run-verified against real `mw.sqlite` (csl-apidev CHANGELOG 2026-06-14). |
| 10 | csl-apidev — clean-URL permalink decision | **Design settled 2026-06-11** in `cleanurl.md` §0: `/{DICT}/{ref}` unified with the Salt permalink; `Accept`-header content negotiation; dict-code whitelist. Implementation → Jim (Tier 5). |
| 11 | RuWritingStyles — F2/F5 | **Decided 2026-06-13**: F2 "reframed, not forced" (the 5 generic passports are genuine voices); F5 de-regioned (`get_cluster_weights` geography boost removed); method-regroup consciously deferred as author's call. |
| 12 | SanskritKaraoke — PR #9 hardening | **Merged 2026-06-13**. |

Also closed as a *decision* though listed under Tier 3 before: **Salt Q4**
(GraphQL lib) — deferred **by design**: a hand-rolled minimal dispatcher ships
now; `webonyx/graphql-php` waits for Phase 2 / Cologne-host Composer
confirmation. No action until then.

---

## Tier 1 — one ask unblocks a pipeline (M.G., each minor)

1. **⭐ Recruit ONE second annotator — the single highest-leverage act in the
   org.** One person covers four blocked publication gates at once: OBS-T
   Cohen κ (`gold_component_2` in
   [`validation/gold_sample.csv`](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/validation/gold_sample.csv)
   — the **last** gate on A12), MWS A16 G5 gold double-annotation, A44 IRR, and
   IndologyScholars IRR (44-row blind sheet). **Decide (who):** Funderburk and
   Patel are the natural candidates for the Cologne-side sheets; the Russian-side
   IRR (A44, IndologyScholars) may need a second person. Fable verdict: this
   replaces the four separate "second coder" rows of the 14-06 edition — treat
   as one recruiting email, not four tasks.
2. **RuWritingStyles — `DEEPSEEK_API_KEY` in `.env`.** Unchanged @DO. The label
   mismatch was fixed 2026-06-30 (183 tests pass); after the key lands, the only
   open judgment is the **diff-fidelity threshold** (calibrate
   `max_char_delta_ratio` by input length vs tighten the revision prompt —
   [`docs/benchmark.md`](https://github.com/gasyoun/RuWritingStyles/blob/main/docs/benchmark.md),
   0/5→3/5 variance). **Recommend:** calibrate by input length — it fixes the
   measured failure mode (short stubs) without perturbing the prompt that long
   inputs already pass.
3. **CommentaryStrategies — annotation-backend key** (`ANTHROPIC_API_KEY` or
   OpenAI-compat). Unchanged @DO; the pipeline was re-pointed in PR #12 and an
   agent runs the kalyanov trial the moment the key exists.
4. **SanskritKaraoke — audio files.** Still the repo's terminal blocker:
   **21 `drive_file_id = "TODO"` across 10 verse files**. Nothing downstream
   (render → publish) can move without audio. **Recommend:** record/collect the
   first 3–5 verses only (per the locked first-drop plan) rather than filling
   all 21.

---

## Tier 2 — scholarly review packets (need eyes; ordered by publication leverage)

*All verdict columns below were verified blank/pending on 2026-07-02 unless
stated. Standing rule: any new review artifact must be an interactive
`/review-sheet` HTML (vote → `decisions.json`), never a markdown checklist.*

1. **csl-observatory — OBS-T human κ** (~66 borderline encoding↔orthography
   rows + second-annotator `gold_component_2`). Blocks **A12 submission to
   LREC-COLING** — DOI minted, venue chosen, revision done; this is the only
   gate. **Decide/DO:** the ~66-row pass is M.G.'s own; the κ pass is Tier 1
   item 1.
2. **MWS — Packets A / B / C** (all sheets delivered, all verdict columns
   blank): A = 50 `ib.` resolvability checks
   ([`PACKET_A_ib.csv`](https://github.com/sanskrit-lexicon/MWS/blob/main/review_packets/PACKET_A_ib.csv),
   backs the 74.7 % resolvability claim), B = 167 DCS-sentence checks
   ([`PACKET_B_band3.csv`](https://github.com/sanskrit-lexicon/MWS/blob/main/review_packets/PACKET_B_band3.csv),
   P3 core), C = class conflicts (deduped 32→26,
   [`PACKET_C_classconflicts.csv`](https://github.com/sanskrit-lexicon/MWS/blob/main/review_packets/PACKET_C_classconflicts.csv),
   P4). **Recommend:** convert the three CSVs into one combined `/review-sheet`
   HTML session (~2 h of M.G. time total) — the CSV format is itself friction.
3. **csl-atlas — H4 (89 rows) + Xref (40 rows).** Reshaped since 14-06: H4
   105→16 auto-resolved + 89 human; Xref 50→10 auto-resolved (prefix
   conventions) + 40 shared-core edges. Worksheets generated 2026-07-01
   ([`H4_REVIEW_WORKSHEET.md`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/H4_REVIEW_WORKSHEET.md),
   [`XREF_REVIEW_WORKSHEET.md`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/XREF_REVIEW_WORKSHEET.md)).
   **Recommend:** regenerate both as `/review-sheet` HTML before M.G. touches
   them (markdown worksheets violate the review-artifact rule), then review H4
   first (blocks the H4 write-up; Xref blocks only the lineage-paper claim).
4. **WhitneyRoots — Queue A, 16 pending class additions.** 14 of 16 carry an
   explicit Whitney *Grammar* § citation
   ([`DECISIONS_NEEDED.md`](https://github.com/gasyoun/WhitneyRoots/blob/main/docs/DECISIONS_NEEDED.md) §1).
   **Recommend:** let an agent apply those 14 with the Grammar § as recorded
   authority — the evidence bar the queue was waiting for is already met.
   Only **ṛdh +I** and **stan +VII** stay human: check Zalizniak; the
   MG-approved SCL pilot 4 (02-07) adds the Dhātupāṭha as a validation-only
   third witness for exactly these.
5. **WhitneyRoots — Phase-0 audit flags (7 GAP + 16 SMEAR).** Adoption
   proposal already written in DECISIONS_NEEDED §2 but never applied.
   **Recommend:** apply the proposed warnemyr-class adoption for the 7 GAP
   roots (agent, with provenance tags); the 16 SMEAR stay behind the homonym
   review below.
6. **WhitneyRoots — Phase-2, 52 ambiguous homonym links**
   ([`crosswalk/alignment_review.json`](https://github.com/gasyoun/WhitneyRoots/blob/main/crosswalk/alignment_review.json),
   untouched since 13-06). **Decide:** genuinely a Sanskritist pass — but only
   after conversion to a `/review-sheet`; the raw JSON is unreviewable.
7. **IndologyScholars — three unfilled sheets:** IRR blind (44 rows,
   `coder_2_*` empty), gender validation (60 rows), OpenAlex candidates
   (122 rows, all `manual_status="todo"`). Unchanged. Gender + IRR block the
   data paper; OpenAlex blocks LOD enrichment only — **Recommend** doing them
   in that order and letting OpenAlex wait.
8. **CommentaryStrategies — Article 2 residue:** Tables 5–7 ✅ verified
   (29-06), Blinderman ✅; **only Tolchelnikov's full name + publication data
   remain** (M.G. supplies from his own records — nobody else can).
9. **CommentaryStrategies — Article 1 (ВЯ):** axis-4 IRR second coder ≥85 %
   (folds into Tier 1 item 1) + archival verification of Petrov 1788 (a
   library/archive errand, M.G. or a Moscow proxy).
10. **csl-observatory — B2 bibliography (BUR Leupol/Maisonneuve; BOP 1847).**
    Unchanged since 14-06 — but **Recommend reassigning to an agent**: this is
    a scan-and-catalogue research task (verify imprint data against the
    csldoc scans), not an M.G. decision. It was mis-filed as a human item.

---

## Tier 3 — policy / naming decisions (each quick; Fable verdict attached)

1. **MWS — W1(c) scan-link layer.** W1(a) ✅ 620/877 sigla; W1(b) ✅ 568/568
   `<expandNorm>` (commit `4c20222`). **Decide:** whether to invest in
   `<scanlink>` URLs for the 568 authority records — the blocker is factual
   (no MW PDF page-URL pattern / scan index yet, issue
   [#218](https://github.com/sanskrit-lexicon/MWS/issues/218)). Priced: with a
   page index it is one agent session; without one it is a manual mapping
   effort nobody should start. **Recommend:** commission the page index first,
   decide after.
2. **MWS — Pāṇini sūtra-linking (8,607 `<ls>` cites).** **Recommend — a
   concrete scheme exists:** link sūtra citations to
   `https://ashtadhyayi.com/sutraani/{a}/{p}/{s}` — the exact pattern the CDSL
   link-target typology already uses for P. 4,2,126 (A13 draft §5.1.5, type
   2.2). Deterministic mapping from the citation string, agent-doable, no
   scan-page scheme needed. The open sub-question (external-site dependency
   vs Cologne-hosted scan) is small enough to accept: ashtadhyayi.com is
   stable, and a scan fallback can be added later.
3. **WhitneyRoots — √dā 349/350/351 `ppp` `dātta` vs `datta`.**
   **Recommend collapse to `datta`:** the canonical PPP of √dā is *dattá*
   (Whitney *Roots* s.v.; long-ā *dātta* appears in no Grammar § cited by the
   queue and looks like script output). Keep `dātta` only if a Whitney §
   citation can be produced; note the referenced `PPP_CORRECTION_PROPOSAL.md`
   from commit `753429a` **does not exist in the tree** (broken pointer —
   agent should regenerate or fix the reference in the same pass).
4. **WhitneyRoots — Queue D exception spot-check.** Inventory drift found:
   the queue says "101 exception tags", the live
   [`grammar_refs.json`](https://github.com/gasyoun/WhitneyRoots/blob/main/src/grammar_refs.json)
   carries 18,684 `"type": "exception"` occurrences. **Recommend:** an agent
   first reconciles the two counts (distinct tags vs raw occurrences) and
   regenerates a ~20-row sample sheet; no human time until the denominator is
   trustworthy.
5. **SanskritKaraoke — publisher credentials (Telegram/Instagram/YouTube/
   TikTok).** **Park:** creds before content is backwards; revisit when the
   first 3–5 verses have audio. (Removed from Tier 1.)
6. **csl-observatory — C3 DNS (`observatory.sanskrit-lexicon.org` /
   uni-koeln.de handover).** No progress, no counterpart engaged. **Park:**
   the GitHub Pages URL is live, indexed, and now SEO-complete; DNS is
   cosmetic until Cologne (Felix Rau) engages. Keep only as a line in the
   next Cologne email.
7. **csl-atlas — issue [#30](https://github.com/sanskrit-lexicon/csl-atlas/issues/30)
   tails** (`di0`/`sO0` gaṇa short-forms; YAT transitivity/seṭ probe).
   Unchanged, low priority, awaiting maintainer input. Keep parked.
8. **csl-atlas — H5 maker correction `divaraTa → diviraTa`.** Proposal packet
   complete with source pointers (MW L92243, PWG L32945), `submittedBy: null`.
   **Recommend:** do **not** treat as an M.G. form-submission errand — route it
   through `/cologne-correction-queue` into the monthly consolidated csl-orig
   batch PR (agent-doable end-to-end under the 02-07 cadence).

---

## Tier 4 — release / citability mechanics

| Repo | State (02-07) | Fable verdict |
|---|---|---|
| BookIndex | ORCID **still commented out** in `CITATION.cff` (placeholder `0000-0000-…`); no Zenodo deposit; latest release v4.2.0 (17-04) predates all of this | **Recommend:** agent fills ORCID `0000-0003-4513-884X` + preps `.zenodo.json` and release notes; M.G. only flips the Zenodo GitHub toggle, then `/cut-release` mints the DOI. |
| IndologyScholars | v1.0.0 frozen 31-05; `CITATION.cff` has version + ORCID but **no DOI identifiers block** | **Recommend:** same pattern — M.G. enables Zenodo integration; agent backfills the concept DOI into CITATION.cff/README. |
| RuWritingStyles | Corpus repo ✅ seeded; **no release ever cut, no DOI**; GitHub-Support GC request for the purged history still unsent | **DO (M.G.):** send the GC support ticket (5 min, security hygiene for the purged corpus). Release + DOI wait for the benchmark to stabilise (Tier 1 item 2 first). |
| CommentaryStrategies | `sources/` ✅ holds the Russian translators' notes (12 JSON) — the 14-06 wording is satisfied; but the **five Sanskrit commentaries still need OCR** (only Sundarakāṇḍa scraped; 14 🟡 sargas extraction is agent-ready) | **Recommend:** reword the item — the remaining blocker is the Gemini-Pro OCR session (M.G., heavy), not file placement. |

---

## Tier 5 — waiting on others / agent handoffs (not M.G. decisions)

| Owner | Item | State (02-07) |
|---|---|---|
| Jim | csl-apidev v1.2 M1–M5 per [`roadmap_v1.2.md`](https://github.com/sanskrit-lexicon/csl-apidev/blob/main/simple-search/roadmap_v1.2.md) + [#47](https://github.com/sanskrit-lexicon/csl-apidev/issues/47) | Spec + 10 §15 questions delivered; **no implementation commits yet**. |
| Jim | Archive `temp_corrections_ap90` + `temp_corrections_mw` (last 2 of 6; each holds one open scholarly issue) | Pinged 2026-06-21; ball in his court; re-run `rh3_archive.py` after. |
| Cologne | C2 server access / D1 — `redo_xampp_selective.sh` cron so 2026-05 csl-orig fixes propagate | Unchanged @WAITING. |
| external | IndologyScholars Phase-5 `.ru` enrichment | Blocked on the residential runner (GTD "Waiting on Me", heavy). |
| agent | **csl-atlas VisualDCS adapter — now UNBLOCKED**: VisualDCS emits [`dcs_lemma_summary.json`](https://github.com/gasyoun/VisualDCS/blob/main/dcs_lemma_summary.json) (commit `88c245b`) | Atlas-side lookup UI / nav / frequency-chip wiring is a plain agent task — moved out of the waiting list. |
| agent | **MWS W2 G5 gold sample — spec ✅ (commit `654c3a8`)**: two independent annotation passes are speced as Sonnet-tier work, adjudication Fable-tier | Agent-runnable now; only the (optional) human gold pass ties back to Tier 1 item 1. IJL target: end of August 2026. |
| M.G. | SanskritKaraoke SK-LIC-2026-001/-002 blanks (heir's name, letter date, scope; Telang BG 2.48/2.49 wording) | Only M.G. holds these facts; verses already marked cleared pending the licensor block. |

---

_Dr. Mārcis Gasūns_
