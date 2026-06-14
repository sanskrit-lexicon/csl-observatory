# Cross-Repo Decisions Needed — Master Index

Consolidated list of every item across the Sanskrit Lexicon repos that is
blocked on a human decision, a credential/access grant, or a scholarly
review. This is the **org-wide** companion to the observatory-scoped
[`DECISIONS_NEEDED.md`](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/docs/DECISIONS_NEEDED.md).

Last updated: 2026-06-14. **33 open items across 10 repos.**

> Agent note: when M.G. asks "what's next?", surface this list. Items are
> ordered by leverage — Tier 1 unblocks the most with the least effort.

---

## Tier 1 — Credentials / access (each unblocks an automated pipeline)

| Repo | Need | Unblocks |
|---|---|---|
| csl-observatory | GitHub token with `workflow` + `read:project` scope as a repo secret / durable credential (C1) | Automated observatory refresh ([#12](https://github.com/sanskrit-lexicon/csl-observatory/issues/12)); no-interactive live metadata fetch |
| RuWritingStyles | Real `DEEPSEEK_API_KEY` in `.env` | P2 quality measurement, P3 real-paper case study |
| CommentaryStrategies | API key for the annotation backend (already re-pointed to a pluggable OpenAI-compat backend in PR #12 — just needs a key) | Automated corpus annotation; H1–H4 quantitative verification for Article 2 |
| SanskritKaraoke | **Audio files** — every `drive_file_id = TODO` in the verse library | The entire render/publish pipeline; first public karaoke drop |
| SanskritKaraoke | Publisher creds: Telegram Bot API, Instagram, YouTube, TikTok | `tools/schedule_drops.py` live social automation |
| csl-observatory | Cologne server access for `redo_xampp_selective.sh` (C2) | Tracking public-artifact refresh as process evidence |
| csl-observatory | DNS for `observatory.sanskrit-lexicon.org` + Cologne `uni-koeln.de/observatory` handover (C3) | Observatory mirrors going live |
| csl-apidev | An `api.github.com`-reachable network (blocked on local host) | Posting the drafted v1.2 feedback comment to [csl-apidev#26](https://github.com/sanskrit-lexicon/csl-apidev/issues/26) |

## Tier 2 — Scholarly review packets (need a Sanskritist's yes/no pass)

| Repo | Item | Blocks |
|---|---|---|
| MWS | Packet B — 167 DCS-sentence checks (`review_packets/`) | P3 publication core |
| MWS | Packet A — 50 `ib.` resolvability checks | "verified vs resolvable" claim |
| MWS | Packet C — 32 class conflicts (Dhātupāṭha tiebreaker) | P4 grammar findings |
| MWS | W2 — G5 gold-sample spec (200 entries, double annotation) | Empirical basis for P1 publication |
| WhitneyRoots | Queue A — 19 kept class additions; `ṛdh +I` & `stan +VII` have no Grammar support → **need Zalizniak** | `app_data.json` authority for those 19 |
| WhitneyRoots | Phase-2 — 52 ambiguous homonym links (`crosswalk/alignment_review.json`) | Crosswalk homonym edges |
| WhitneyRoots | Phase-0 — 23 audit flags (7 GAP, 16 SMEAR) | Spine completeness |
| WhitneyRoots | Queue B/C — √dā ids 349/350/351 `ppp`: keep `dātta` or collapse to `datta` | PPP data quality |
| WhitneyRoots | Queue D — spot-check ~20 of 101 `exception` tags | Grammar-ref quality |
| csl-atlas | R2 checkpoint — 10 rows (`src/data/review/r2-checkpoint-review.json`) | Any parser-label promotion |
| csl-atlas | H4 semantic-field — 105 rows | H4 hypothesis write-up |
| csl-atlas | H5 — submit maker correction `divaraTa → diviraTa` | H5 write-up |
| csl-atlas | Xref — 40 shared-core + 10 prefix-control rows | Xref-lineage paper claim |
| CommentaryStrategies | C0.3 — distribute Sundara-kāṇḍa specimens to Leonov & Kostina (without the key), collect ratings → resolve D2 model choice | Entire Workstream C |
| CommentaryStrategies | Article 2 (ВФ) — verify Tables 5–7; Blinderman pub data; Tolchelnikov full name | Article 2 final draft |
| CommentaryStrategies | Article 1 (ВЯ) — IRR second coder (≥85%); archival verify Petrov 1788 | Article 1 submission |
| IndologyScholars | IRR second coder for `interrater_sample_blind.csv` (G2/G3 boundary weak) | κ in the data paper |
| IndologyScholars | Gender validation — fill 60 rows (`gender_validation_sample.csv`) | Error-rate claim on `findings/gender.html` |
| IndologyScholars | Manual review of 122 OpenAlex candidates → QuickStatements batch | Authority-ID enrichment / LOD publication |
| csl-observatory | OBS-T validation — annotate gold/error samples; second annotator (Funderburk/Patel) for IAA | OBS-T paper draft; PR #33 |
| csl-observatory | B2 — verify bibliography for BUR (Leupol/Maisonneuve) and BOP (1847) | Closing handoff gaps |

## Tier 3 — Policy / naming decisions (your call, each quick)

| Repo | Decision |
|---|---|
| csl-observatory | A4 — approve/revise the license decision matrix (code, data, mixed, archive) → unblocks license-hygiene sweep of ~21 NOASSERTION repos |
| csl-observatory | A5 — archive-or-retain `santamlegacy`, `temp_corrections_{acc,ae,ap90,mw}`, `test_cologne_push` |
| csl-observatory | A7 — bus-factor accepted-risk review for DCS, KNA, KOW, MCI, santamlegacy |
| csl-corrections | **KRM license mismatch** — `LICENSE` says GPL-3.0, `CITATION.cff` says CC-BY-SA-4.0; pick one |
| MWS | W1 layer priority — the "589 orphans" is a measurement artifact; choose layer (a) link 171 variants, (b) add `<expandNorm>` to 338, or (c) scan-link targets |
| MWS | Pāṇ. sūtra-linking scheme (8607 `<ls>` cites can't page-link like text cites) |
| csl-standards / csl-apidev | Salt Q4 (GraphQL lib: `webonyx/graphql-php`?) and Q6 (real `apidev` controller path for `api1/`) |
| csl-apidev | Clean-URL permalink (#249) — content-negotiation trigger + dict-code whitelist |
| csl-apidev | 10 open v1.2 questions in roadmap §14 (DELTA policy, x→kṣ vs x→z, sh→ś bias, etc.) |
| RuWritingStyles | F2 — sharpen/relabel 5 generic passport voices; F5 — regroup `ling_mss`/`ling_mts` by method? |
| csl-atlas | Issue #30 tails — `di0`/`sO0` gaṇa short-forms (VCP key); YAT transitivity/seṭ source probe |
| csl-atlas | **[PR #88](https://github.com/sanskrit-lexicon/csl-atlas/pull/88) blocked** — decide which `src/data/review/source-siglum-review.json` packet is canonical (PR's 12-dict expansion vs main's 4-dict, 158 vs 149 records); once chosen, the other 16 conflicts are mechanical |

## Tier 4 — Release / citability mechanics

| Repo | Item |
|---|---|
| BookIndex | Provide a real ORCID; enable Zenodo + cut a release to mint the DOI |
| IndologyScholars | Zenodo DOI + CITATION.cff bump at first freeze |
| RuWritingStyles | Mint Zenodo DOI on first release; seed the private `RuWritingStyles-corpus`; ask GitHub Support to GC dangling objects |
| CommentaryStrategies | Place the 5 source files in `sources/` |

## Tier 5 — Implementation handoffs (not M.G. decisions — tracked for completeness)

| Repo | Item |
|---|---|
| csl-apidev | Jim to implement v1.2 (M1→M5) per `simple-search/roadmap_v1.2.md` and [#47](https://github.com/sanskrit-lexicon/csl-apidev/issues/47) |
| IndologyScholars | Phase 5 `.ru` enrichment — run scrapers from a `.ru`-accessible machine |
| SanskritKaraoke | PR #9 (`review/core-extraction-and-hardening-jun-2026`) awaiting review/merge |
| SanskritKaraoke | SK-LIC-2026-002 — heir's name, letter date, granted scope; SK-LIC-2026-001 open blanks; Telang BG 2.48/2.49 wording check |
| csl-observatory | D1 — Cologne admin runs/cron `redo_xampp_selective.sh` so 2026-05 csl-orig fixes propagate |
| csl-atlas | VisualDCS adapter wiring — blocked until VisualDCS emits `dcs_lemma_summary.json` |
