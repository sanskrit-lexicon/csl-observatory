# Cross-Repo Decisions Needed — Master Index

_Created: 14-06-2026 · Last updated: 06-08-2026_

Consolidated list of every item across the Sanskrit Lexicon repos that is
blocked on a human decision, a credential/access grant, or a scholarly
review. This is the **org-wide** companion to the observatory-scoped
[`DECISIONS_NEEDED.md`](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/docs/DECISIONS_NEEDED.md).
For open PRs / merges / deploys awaiting a maintainer (rather than decisions),
see [`MAINTAINER_ACTIONS.md`](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/docs/MAINTAINER_ACTIONS.md).

**Edition of 2026-08-04 (July re-adjudication)** — H1875, Fable 5
(`claude-fable-5`): every item of the 2026-07-02 edition re-checked against
what actually shipped in July, via seven read-only evidence sweeps over the
live clones (csl-observatory, MWS, csl-atlas, WhitneyRoots, RuWritingStyles,
CommentaryStrategies, SanskritKaraoke, IndologyScholars, BookIndex,
csl-apidev, csl-corrections) plus the
[Uprava GTD](https://github.com/gasyoun/Uprava/blob/main/GTD_NEXT_ACTIONS.md).
Each surviving item now carries a **➡ 04-08 verdict** — **still-correct** /
**overtaken** (struck, with a pointer to what superseded it) /
**contradicted** (the July wording disagreed with repo reality; the evidence
and the ruling are given in place). Tally over the 02-07 edition's 33 items:
**14 still-correct · 10 overtaken · 9 contradicted** (mixed items counted by
their dominant half). Rulings here establish only whether an item still
describes reality — no decision is re-opened on the merits. Where a repo-local
journal disagrees with the hub, the wrong journal line is named explicitly.

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

## D — Ruled decisions graduated from Uprava CONTRADICTIONS (binding; do not re-litigate)

The [Uprava CONTRADICTIONS](https://github.com/gasyoun/Uprava/blob/main/CONTRADICTIONS.md)
registry holds *unresolved* disagreements between two sources. Its stated
graduation path is that a **ruled** contradiction becomes a `D##` here and leaves a
tombstone there. This section is that landing surface, opened 06-08-2026 with the
first graduation.

**Numbering.** `D01`, `D02`, … — zero-padded, this file's own append-only sequence,
never renumbered. It is **distinct** from the observatory-scoped `D1`–`D4` in
[`DECISIONS_NEEDED.md`](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/docs/DECISIONS_NEEDED.md)
and from the `D2`–`D5` finding ids in
[`PERFORMANCE_AUDIT_2026-07.md`](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/docs/PERFORMANCE_AUDIT_2026-07.md);
the zero-padding is what keeps the three apart at a glance.

### D01 — A measurement of a third-party tool is scoped to the VERSION it was taken on (06-08-2026)

**Ruling.** A standing truth derived from measuring someone else's tool records a
property of **that version**, not a permanent property of the route. When a later
run contradicts it, the first question is *did the dependency change under us*, and
the deciding evidence is a **knob-by-knob diff of the two rigs' source** — not a
third measurement. Where the two rigs agree on every knob that could produce the
effect, the newer reading wins and the standing truth is **rewritten, not
re-confirmed**.

**The case that established it.** Whether a one-shot `claude -p` subprocess can
amortise its own system prompt across calls. Measured **cannot** on CLI v1.127.0
(02-08-2026, two identical back-to-back calls each re-creating ~49 k cache tokens);
measured **can** on v2.1.223 (06-08-2026, purpose-built 7-call sequence — cold call
wrote 26 243 + read 28 882 = 55 125, five later calls created **0** and read 55 125
exactly, at gaps of 34/94/120/128/557 s). Both runs were right about their own
version. The rigs differ in exactly one knob — spawn cwd — which changes how *large*
the created prefix is and cannot change whether call #2 reuses call #1's.

**Binding consequences.**

| | |
|---|---|
| Operational home of the rewritten truth | [PROMPT_CACHING_PWG_RU §1](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/PROMPT_CACHING_PWG_RU.md) + [RUN_FREQ_MAX](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/RUN_FREQ_MAX.md) — where executors actually read it |
| Route consequence | the Messages-API port loses its cache argument; it is re-based on wall-clock and turn-count, not on turning `create` into `read` |
| Standing requirement | **every cache/cost measurement records the CLI version next to the numbers** — a number without a version cannot be re-adjudicated later, only re-run |
| Not established | behaviour past the 1 h TTL gap (deliberately unmeasured); amortisation for *agentic* (multi-turn) calls, whose envelope sums a variable turn count and so is not a comparable quantity |
| Evidence | [re-measure memo](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/h2250/CLI_CACHE_AMORTISATION_REMEASURE_06-08-2026.md) · [raw envelopes](https://github.com/gasyoun/SanskritLexicography/tree/master/RussianTranslation/pwg_ru/h2250/raw) · [PR #1148](https://github.com/gasyoun/SanskritLexicography/pull/1148) |
| Provenance | H2250, Opus 5 (`claude-opus-5[1m]`); probe calls on Sonnet 5 (`claude-sonnet-5`). Graduated from [Uprava CONTRADICTIONS §7](https://github.com/gasyoun/Uprava/blob/main/CONTRADICTIONS.md); generalised as [Uprava FINDINGS §326](https://github.com/gasyoun/Uprava/blob/main/FINDINGS.md) |

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

1. ~~**⭐ Recruit ONE second annotator — the single highest-leverage act in the
   org.** One person covers four blocked publication gates at once: OBS-T
   Cohen κ, MWS A16 G5 gold double-annotation, A44 IRR, and IndologyScholars
   IRR (44-row blind sheet). **Decide (who):** Funderburk and Patel are the
   natural candidates.~~
   ➡ **04-08 verdict: OVERTAKEN — struck.** M.G. **overruled this one day
   after it was written**: PARKED 03-07-2026, "no candidate yet; do not
   resurface as an action item during 2026"
   ([GTD](https://github.com/gasyoun/Uprava/blob/main/GTD_NEXT_ACTIONS.md)
   rows 192/764/1361). Three of the four gates then closed by LLM/agent
   substitution, not recruitment: **A44 IRR** closed 10-07 (H453, Opus 4.8
   blind ×10 over 122 rows, κ=0.336 five-way / 99.2 % binary,
   [SanskritSpellCheck PR #28](https://github.com/gasyoun/SanskritSpellCheck/pull/28));
   **A16 G5** ran as two isolated Sonnet 5 passes + Fable adjudication (see
   Tier 5); **OBS-T κ** cleared 21-07 as *cross-model* IAA κ=0.906 (H1385,
   [csl-observatory PR #102](https://github.com/sanskrit-lexicon/csl-observatory/pull/102)).
   Still genuinely open: **IndologyScholars IRR** (the blind sheet is
   **100 rows**, not the 44 claimed here — count corrected per
   [`interrater_sample_blind.csv`](https://github.com/gasyoun/IndologyScholars/blob/main/analytics_output/interrater_sample_blind.csv))
   and the OBS-T *human* ~66-row pass, itself PARKED 2026 (Tier 2 #1).
2. ~~**RuWritingStyles — `DEEPSEEK_API_KEY` in `.env`.** Unchanged @DO … the
   only open judgment is the diff-fidelity threshold (calibrate
   `max_char_delta_ratio` by input length vs tighten the revision prompt).~~
   ➡ **04-08 verdict: OVERTAKEN — struck.** Key resolved 03-07 (reuse the
   key already in `../IndologyScholars/.env` — no new credential; GTD row
   186). The diff-fidelity fork was resolved by a **third option neither
   listed**: span-patch reconstruction + growth governor (commit `14a4fae`,
   03-07, H073) — diff-ok went 1/5 → 25/25 and `max_char_delta_ratio` stays a
   flat 0.5. Four real-provider benchmark waves followed (03-07 → 18-07,
   GOLD_DICTIONARY 37/40 = 0.925;
   [`docs/benchmark.md`](https://github.com/gasyoun/RuWritingStyles/blob/main/docs/benchmark.md)).
3. ~~**CommentaryStrategies — annotation-backend key** (`ANTHROPIC_API_KEY` or
   OpenAI-compat). Unchanged @DO; an agent runs the kalyanov trial the moment
   the key exists.~~
   ➡ **04-08 verdict: OVERTAKEN — struck.** Resolved 04-07 (H134): the n=50
   trial ran and committed (84 %/92 %, GTD rows 189/577/1411) and the standing
   policy is now **no `ANTHROPIC_API_KEY` will ever be added to these repos**
   — future runs use DeepSeek via `--backend openai` + `LLM_API_KEY`. The
   repo journal line
   [`CommentaryStrategies/.ai_state.md`](https://github.com/gasyoun/CommentaryStrategies/blob/main/.ai_state.md)
   line 143 still showing the key + kalyanov trial as an open checkbox is
   **the wrong journal** (hub authoritative); its lines 86–87 (duplicated
   Tolchelnikov «ЖДЕМ») and 142 (asking for a script that shipped 01-07) are
   the same registry rot. Logged as an unresolved positions-row in
   [Uprava CONTRADICTIONS §B](https://github.com/gasyoun/Uprava/blob/main/CONTRADICTIONS.md)
   because the repo carries no committed n=50 results file to witness the
   hub's numbers.
4. **SanskritKaraoke — audio files.** Still the repo's terminal blocker —
   but the July inventory line was wrong.
   ➡ **04-08 verdict: STILL-CORRECT as blocker; count CONTRADICTED.** The
   claim "21 `drive_file_id = "TODO"` across 10 verse files" is false: the
   true count is **6 TODOs across 3 files** (`bhg_2_47/48/49.json`, one
   `audio` + one `session` slot each); the 10 `subh_*.json` verses carry no
   `drive_file_id` field at all. Zero audio files anywhere in the tree; no
   audio added since 02-07. H1858 (04-08,
   [SanskritKaraoke PR #65](https://github.com/gasyoun/SanskritKaraoke/pull/65))
   added RU renderings for the 10 subhāṣitas as own-work — it sidesteps
   Sementsov licensing for those verses but touches no audio. The
   "record/collect the first 3–5 verses only" recommendation stands.

---

## Tier 2 — scholarly review packets (need eyes; ordered by publication leverage)

*Standing rule unchanged: any new review artifact must be an interactive
`/review-sheet` HTML (vote → `decisions.json`), never a markdown checklist.*

1. **csl-observatory — OBS-T human κ** (~66 borderline rows + second-annotator
   `gold_component_2`). The July wording said "Blocks A12 submission … DOI
   minted, venue chosen … this is the only gate."
   ➡ **04-08 verdict: CONTRADICTED on "DOI minted" + OVERTAKEN on the κ
   framing.** The recorded DOI `10.5281/zenodo.15834721` **was never A12's
   DOI** — it resolves to an unrelated topology preprint and was scrubbed
   org-wide 20-07 (H1364,
   [csl-observatory PR #99](https://github.com/sanskrit-lexicon/csl-observatory/pull/99);
   [`CITATION.cff`](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/CITATION.cff)
   line 7 says "was a false DOI"). A genuine mint is still owed (M.G.). The κ
   gate was cleared 21-07 as **cross-model** IAA (H1385, PR #102: κ=0.906
   [0.872–0.938] on the location axis) and carried into the manuscript by the
   H1759 reconciliation (28-07,
   [PR #125](https://github.com/sanskrit-lexicon/csl-observatory/pull/125);
   canonical manuscript is now root `paper-obs-t-error-typology.md`). The
   *human* ~66-row pass and human `gold_component_2` (still only 4/390 rows
   filled) are **PARKED 2026** per
   [`.ai_state.md`](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/.ai_state.md)
   line 41. Remaining human gates on A12: byline, genuine DOI mint,
   LREC-COLING submission itself. One more wrong journal: the same
   `.ai_state.md` WIP block still says "Zenodo DOI ✅ minted 2026-07-01" —
   the exact claim the H1364 scrub disproved; the hub ruling here is
   authoritative.
2. **MWS — Packets A / B / C** (verdict columns blank).
   ➡ **04-08 verdict: STILL-CORRECT (blank: 0/50, 0/167, 0/26) — but the
   "convert to /review-sheet, ~2 h of M.G. time" recommendation is
   OVERTAKEN** by the H966 kill-gate ruling (18-07,
   [`review_packets/H966_KILL_GATE_FINDING.md`](https://github.com/sanskrit-lexicon/MWS/blob/master/review_packets/H966_KILL_GATE_FINDING.md)):
   every verdict is a genuine Sanskritist judgement, **not agent-fillable**,
   and the packets stay blank by ruling rather than by neglect. The only
   review-sheet HTML shipped since (PR #229, 04-07) is the adjacent A18
   sense-verify sheet, not a conversion of A/B/C.
3. **csl-atlas — H4 (89 rows) + Xref (40 rows).**
   ➡ **04-08 verdict: OVERTAKEN on both halves.** ~~H4 89-row human
   review~~ — **agent-adjudicated 24-07** (H1621, Grok 4.5,
   [csl-atlas PR #297](https://github.com/sanskrit-lexicon/csl-atlas/pull/297));
   [`H4_REVIEW_WORKSHEET.md`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/H4_REVIEW_WORKSHEET.md)
   now reads "human vote not required", CI queue count flipped 89 → 0. The
   Xref 40-edge sheet **is** now proper `/review-sheet` HTML (H1646 25-07 +
   H1648 26-07) but has **0/40 verdicts** — and its founding premise was
   **retracted 26-07** (H1648): a shared MW/PWG edge is *not* two independent
   witnesses (MW leans on PW/PWG; 21.8 % target coincidence vs 0.007 %
   random), so any pre-retraction votes would have answered the wrong
   question. Note the atlas's **new top human ask is the SKD *iti* sheet
   (102 decisions)** after H1684 cut the human queue 221 → 61
   ([`H1684_B2_ADJUDICATION.md`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/H1684_B2_ADJUDICATION.md));
   Xref queues behind it.
4. **WhitneyRoots — Queue A, 16 pending class additions.**
   ➡ **04-08 verdict: STILL-CORRECT — nothing applied.** All 16 rows sit
   `PENDING_REVIEW` / `decision: null` in
   [`queue_a.json`](https://github.com/gasyoun/WhitneyRoots/blob/main/docs/queue_candidates/queue_a.json)
   (generated 19-07, H975); ṛdh +I and stan +VII are still the two
   `NEEDS ZALIZNIAK` rows; the additions are live-but-unratified in
   `app_data.json`. The Dhātupāṭha third witness (SCL pilot 4, MG-approved
   02-07) **was never run** — the GTD row is still open and no artifact
   exists in the repo.
5. **WhitneyRoots — Phase-0 audit flags (7 GAP + 16 SMEAR).**
   ➡ **04-08 verdict: STILL-CORRECT — unapplied and not even queued.** The
   H975 queue lettering does not cover DECISIONS_NEEDED §2 (its `queue_b` is
   the 12 SUSPICIOUS PPP, a different list); spot-checked GAP roots (kath,
   kḷp, snā, spand, smṛ) all still `"classes": []`.
6. **WhitneyRoots — Phase-2, 52 ambiguous homonym links.**
   ➡ **04-08 verdict: STILL-CORRECT — untouched since 13-06.**
   [`alignment_review.json`](https://github.com/gasyoun/WhitneyRoots/blob/main/crosswalk/alignment_review.json)
   unchanged; not covered by the A–E review-sheet builder, so still no
   `/review-sheet`. Minor journal drift: `.ai_state.md:46` says "45
   ambiguous" for the artifact that renders as 52 — the journal is wrong.
7. **IndologyScholars — three unfilled sheets.**
   ➡ **04-08 verdict: STILL-CORRECT (all three 100 % unfilled) — counts
   CONTRADICTED.** True sizes: IRR blind **100 rows** (not 44), gender 60 ✓,
   OpenAlex **496 rows / 492 `todo`** (not 122). Nothing touched since
   12-06; the repo's own journal carries the correct numbers and explicitly
   defers human IRR to 2026
   ([`IndologyScholars/.ai_state.md`](https://github.com/gasyoun/IndologyScholars/blob/main/.ai_state.md)
   line 16). Order recommendation (gender + IRR before OpenAlex) stands.
8. ~~**CommentaryStrategies — Article 2 residue: only Tolchelnikov's full
   name + publication data remain.**~~
   ➡ **04-08 verdict: CONTRADICTED — struck as written.** The publication
   data was supplied **16-05-2026** (commit `128b07e`, before the July
   edition was written):
   [`article2_vf.md`](https://github.com/gasyoun/CommentaryStrategies/blob/main/articles/article2_vf.md)
   line 572 carries the full bibliography entry (course manuscript,
   samskrtam.ru, М., 2023–2025). Genuine residue is narrower: full
   given-name/patronymic (only «И.Е.» anywhere), page numbers for the
   Вопросы философии 2025 № 5 entry (line 598), and Blinderman's выходные
   данные verification. The `.ai_state.md` «ЖДЕМ» lines 86–87 are stale rot.
9. **CommentaryStrategies — Article 1 (ВЯ).**
   ➡ **04-08 verdict: IRR half OVERTAKEN; Petrov half STILL-CORRECT.**
   ~~axis-4 IRR second coder ≥85 %~~ — measured 24-07 (H1469, blind LLM
   Pass B = DeepSeek Chat on the full 300-note gold): κ axis_2=0.648, axis_4
   =0.521, agreement 77 % — the ≥85 % target was **missed and closed as an
   honest negative finding** (v1.13.0/v1.13.1, folded into the manuscript
   §2.3/§7.5). Petrov 1788 archival verification: no movement — still the
   one human @DO gate to 5/5.
10. **csl-observatory — B2 bibliography (BUR Leupol/Maisonneuve; BOP 1847).**
    ➡ **04-08 verdict: STILL-CORRECT — zero progress since 14-06.** The
    "reassign to an agent" recommendation was never executed. (Do not
    misread
    [`OBSERVATORY_ROADMAP.md`](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/docs/OBSERVATORY_ROADMAP.md)
    "B2 … done" — that is a roadmap-numbering collision, a different B2.)

---

## Tier 3 — policy / naming decisions (each quick; Fable verdict attached)

1. **MWS — W1(c) scan-link layer.**
   ➡ **04-08 verdict: OVERTAKEN — the decision was taken and promptly
   hard-blocked.** SPEC-1
   ([`planning/specs/2026-07/SPEC-1-w1c-scanlink.md`](https://github.com/sanskrit-lexicon/MWS/blob/master/planning/specs/2026-07/SPEC-1-w1c-scanlink.md),
   02-07) executed and **BLOCKED 08-07 at step 1**: MW's front matter names
   no edition for *any* cited work (Suśr./Kathās./ŚBr.), so the edition
   cannot be confirmed (commit `e2269bb`, analysis in
   [MWS #234](https://github.com/sanskrit-lexicon/MWS/issues/234)). The July
   row's issue pointer was also wrong: **#218 is W1(b), closed ✅ 30-06** —
   the live blocker is **#234**. "Commission the page index first" is moot
   until the edition question gets an @DECIDE.
2. **MWS — Pāṇini sūtra-linking (8,607 `<ls>` cites).**
   ➡ **04-08 verdict: STILL-CORRECT — deliberately deferred to the "August
   sūtra-scheme decision"**
   ([`planning/PLANNING_2026-07.md`](https://github.com/sanskrit-lexicon/MWS/blob/master/planning/PLANNING_2026-07.md)
   line 45, naming this doc's ashtadhyayi.com recommendation as the working
   one). The decision window is now open; nothing has landed.
3. **WhitneyRoots — √dā 349/350/351 `ppp` `dātta` vs `datta`.**
   ➡ **04-08 verdict: STILL-CORRECT (unresolved in data) — but the July
   aside "`PPP_CORRECTION_PROPOSAL.md` does not exist in the tree" is
   CONTRADICTED.**
   [`docs/PPP_CORRECTION_PROPOSAL.md`](https://github.com/gasyoun/WhitneyRoots/blob/main/docs/PPP_CORRECTION_PROPOSAL.md)
   has existed since 15-06 (commit `753429a`) and already rules
   `dātta → DROP` (corpus: `datta` 1471×, `dātta` 0×), blaming
   `apply_ppp_corrections.py:76-86` for manufacturing the form. All three
   entries still carry `["data","datta","dātta"]` — the decisive proposal
   awaits application; its PR gate lapsed in mid-June.
4. **WhitneyRoots — Queue D exception spot-check.**
   ➡ **04-08 verdict: OVERTAKEN — the denominator was reconciled and the
   queue adjudicated.** True counts: **101** `"type": "exception"` records
   in `app_data.json` / **1,467** exception section-tags in
   `grammar_refs.json`; the July "18,684" was a naive whole-word grep
   miscount reproducible from neither. Queue D shipped 28-07 (H1686,
   [WhitneyRoots PR #54](https://github.com/gasyoun/WhitneyRoots/pull/54)):
   101 total → 62 agent-resolved, **39 human residue**. Residual defect:
   [`REVIEWER_GUIDE.md`](https://github.com/gasyoun/WhitneyRoots/blob/main/docs/REVIEWER_GUIDE.md)
   lines 58/182 still attribute "101 exception tags" to `grammar_refs.json`
   — the exact mislabel that produced the confusion.
5. **SanskritKaraoke — publisher credentials.**
   ➡ **04-08 verdict: STILL-CORRECT — parked until audio, unchanged**
   (Telegram named the cheapest first unlock; IG/TikTok/YT app review stays
   parked).
6. **csl-observatory — C3 DNS.**
   ➡ **04-08 verdict: STILL-CORRECT — parked, no counterpart engaged, no
   CNAME in the tree.** (Same numbering-collision caveat: the roadmap's
   "C3 … done" is a different C3.)
7. ~~**csl-atlas — issue #30 tails** (`di0`/`sO0` gaṇa short-forms; YAT
   transitivity/seṭ probe). Unchanged, low priority, awaiting maintainer
   input. Keep parked.~~
   ➡ **04-08 verdict: CONTRADICTED — struck.** Issue
   [#30](https://github.com/sanskrit-lexicon/csl-atlas/issues/30) was
   **closed 17-07 as superseded** (v0.2.0 publication). Neither tail was
   worked (`MICROSTRUCTURE_DECISIONS.md` untouched since 10-06, the YAT
   "not systematically decoded" line stands verbatim) — the tails are now
   **unowned rather than parked**: they survive only in an archived state
   file. If they still matter, they need a new home; nothing tracks them.
8. ~~**csl-atlas — H5 maker correction `divaraTa → diviraTa`** … route it
   through `/cologne-correction-queue` into the monthly consolidated
   csl-orig batch PR.~~
   ➡ **04-08 verdict: CONTRADICTED — struck.** It was **closed 03-07 as
   no-csl-orig-edit** (Fable 5): both source records are *faithful
   apparatus entries* (MW `w.r. for divi-`; PWG "falsche Form für
   diviraTa") — the wrong reading is printed intentionally, so a
   "correction" would violate the printchange discipline; nothing to queue
   upstream (archived state file
   [`AI_STATE_2026-07-17.md`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/archive/AI_STATE_2026-07-17.md)
   line 83, mirrored in GTD). Stale live docs still listing submission as
   pending (`HYPOTHESIS_INDEX.md:58`, `RESEARCH_LAYER_ROADMAP.md:69/133/284`,
   `REVIEW_QUEUE_PROOFS.md:37`, `MICROSTRUCTURE_FINDINGS.md:58`) are the
   wrong journals and need a rot sweep.

---

## Tier 4 — release / citability mechanics

| Repo | State (02-07 → 04-08) | ➡ 04-08 verdict |
|---|---|---|
| BookIndex | ~~ORCID commented out; no Zenodo deposit; latest release v4.2.0~~ | **OVERTAKEN (mostly).** Concept DOI **minted 27-07**: `10.5281/zenodo.21630473` (H1601, v4.3.0/v4.3.1); **13 releases** since, through v4.11.0 (02-08); colophon unblocked. Residue STILL-CORRECT: [`CITATION.cff`](https://github.com/gasyoun/BookIndex/blob/main/CITATION.cff) ORCID is *still* the commented `0000-0000-…` placeholder — the real value (`0000-0003-4513-884X`) sits in IndologyScholars' file and was never wired here. |
| IndologyScholars | v1.5.0 cut 31-07; deposit package ready since 17-07 (`article/zenodo_metadata.json`) | **STILL-CORRECT.** No `identifiers:` block, no `.zenodo.json`, draft still `10.5281/zenodo.PENDING` ×2 — the human Zenodo toggle never fired; v1.5.0 was cut *without* DOIs. |
| RuWritingStyles | ~~no release ever cut~~; GC request unsent | **SPLIT.** Releases OVERTAKEN: v2.15.0 → **v2.22.0** (04-08), CITATION.cff current. Zenodo DOI STILL-CORRECT: placeholder `10.5281/zenodo.XXXXXXX` (the one real DOI in the repo belongs to the ARS donor). GC support ticket STILL-CORRECT: unsent — its 15-07 unfreeze date passed with no follow-through. |
| CommentaryStrategies | ~~remaining blocker is the Gemini-Pro OCR session (M.G., heavy)~~ | **CONTRADICTED — struck.** H370 (the OCR ask) was **closed by suppression 08-07**: prior-art gate found the lever already delivered better — all 7 traditional commentaries were *scraped* 01-07 (no commentary scans exist to OCR; [`SUNDARA_OCR_PHASE2_SUPERSEDED.md`](https://github.com/gasyoun/CommentaryStrategies/blob/main/docs/SUNDARA_OCR_PHASE2_SUPERSEDED.md)). Since then: all 58 Sundarakāṇḍa sargas drafted, **1889 queued cards agent-adjudicated** (H1685, 27-07, v1.14.0), rights cleared CC BY 4.0 (01-07 grant). Permanent limits stand: Yuddhakāṇḍa commentaries = 0, dharmakūṭam/tanisloki = 0, ruled do-not-rescrape. |

---

## Tier 5 — waiting on others / agent handoffs (not M.G. decisions)

| Owner | Item | ➡ 04-08 verdict |
|---|---|---|
| Jim | csl-apidev v1.2 M1–M5 per [`roadmap_v1.2.md`](https://github.com/sanskrit-lexicon/csl-apidev/blob/main/simple-search/roadmap_v1.2.md) | **STILL-CORRECT — zero Jim commits since 21-06** (post-02-07 authors: MG 120, Dhaval Patel 13, dependabot 3). One M2 fragment (Fix I, DCS-2026 wf1 default ranking) landed 24-07 **by MG, not Jim** (`b6d4fc5`, H1562). No `v1.2/` directory exists. |
| Jim | Archive `temp_corrections_ap90` + `temp_corrections_mw` | **STILL-CORRECT** — deliberately left for funderburkjim (each holds one open scholarly issue), pinged 21-06, unamended in [`csl-observatory/.ai_state.md`](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/.ai_state.md) line 37. Live GitHub archive flags unverifiable this session (API TLS timeouts). |
| Cologne | C2 server access / D1 `redo_xampp_selective.sh` cron | **STILL-CORRECT — zero movement**; the GTD @WAITING row is verbatim unchanged. |
| external | IndologyScholars Phase-5 `.ru` enrichment | **STILL-CORRECT — still blocked on a clean-egress host** (RKN block from the automation host; no enrichment-tool commits since 02-07; last attempt 20-06). |
| agent | ~~csl-atlas VisualDCS adapter — now UNBLOCKED … a plain agent task — moved out of the waiting list~~ | **CONTRADICTED — struck.** The adapter was **already built in June**, before the July edition wrote this: consumption contract 09-06, adapter stub + frequency chip 10-06, reader lookup wired 20-06; `dcs_lemma_summary.json` (83,239 lemmas, generated 13-06) was in place. Nothing was left to unblock — the item described done work as pending. Consumers kept accruing (ghost-stock, 25-07). |
| agent | ~~MWS W2 G5 gold sample — spec ✅; two annotation passes speced as Sonnet-tier, adjudication Fable-tier; IJL target end of August~~ | **OVERTAKEN — executed in full 02–03 July**, the day after the spec: Pass A ([MWS PR #221](https://github.com/sanskrit-lexicon/MWS/pull/221)) + genuine-reading Pass B (PR #222, first script-based B replaced), 146 disagreements Fable-adjudicated, scored macro F1 0.876 / mean κ 0.817 ([`G5_SCORES.md`](https://github.com/sanskrit-lexicon/MWS/blob/master/review_packets/g5/G5_SCORES.md)); A16 hit 5/5 on 03-07 (H079). IJL end-of-August verdict "HOLDS". **New breach the hub missed:** [MWS #195](https://github.com/sanskrit-lexicon/MWS/issues/195) `docs-pass` merge was ruled "end-of-July default absent maintainer objection" and is **still unmerged** (19 commits stranded, incl. the A16 draft + review), 4 days past its own deadline. Stale doc: `review_packets/README.md` still calls G5 "spec only". |
| M.G. | SanskritKaraoke SK-LIC-2026-001/-002 blanks | **STILL-CORRECT** — licensor blocks still bracketed placeholders (`make_sementsov_agreement.js:104/:156`), Telang BG 2.48/2.49 verification still open (only 2.47 fetch-confirmed). H1858's own-work RU subhāṣita renderings (04-08) narrow Sementsov exposure but resolve nothing here. |

---

_Dr. Mārcis Gasūns_
