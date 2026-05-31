# Decisions needed from the maintainer

Consolidated list of items that are **blocked on a human** (a decision, a credential, or an action only you can take). Maintained so an agent can resurface it at the start of a session. Last updated 2026-05-31.

> Agent note: when M.G. asks "what's next?" or resumes, **surface this list first**.

---

## A. Decisions (pick an option)

| # | Decision | Options / recommendation | Source |
|---|---|---|---|
| A1 | **KRM license** | Its `LICENSE` is GPL-3.0 but `CITATION.cff` says CC-BY-SA-4.0. Align which way? *Rec: CC-BY-SA-4.0 (it's dictionary data).* | Roadmap M7 / KRM/CLAUDE.md |
| A2 | **Taxonomy rollout scope** | ✅ **Done 2026-05-31** — dict-issue taxonomy (1 type + 1 severity + 1 milestone + matching project) applied & verified **all-clean** across **24 dictionary repos** (786 issues): the 14 rec'd dicts + the AP, AP90, FRI, GRA, MD, MWS, PWG, PWK, Wil-YAT stragglers (previously-run repos that had accumulated unlabeled issues). 238 issues newly labelled, 400 project memberships added (incl. backfill of older milestoned-but-unassigned issues). **Still open:** categorize the non-dictionary repos **csl-apidev, cologne-stardict, GreekInSanskrit, ArabicInSanskrit** under the *tooling* taxonomy (`/cologne-tooling-runbook`) — separate batch, different label set. | Roadmap Q7 / audit 2026-05-30 |
| A3 | **LICENSE full text vs pointer** | The 6 documented dict repos got pointer-style CC-BY-SA-4.0 LICENSEs. Want the full legalcode (for GitHub auto-detection)? | Handoff full-runbook gaps |
| A4 | **Scan-only dicts** (AE, IEG, MWE, PD, PE, PGN, SNP, YAT — 8, not on GitHub) | Ingest via Cologne web-scrape (~1 day each) or omit with a "future work" note? | LEXICOGRAPHY_ROADMAP §11.1 |
| A5 | **Add PD** (Deccan College encyclopedic dict, 1976) | Major modern dict; would strengthen Paper L; needs Cologne coordination. Include? | LEXICOGRAPHY_ROADMAP §11.2 |
| A6 | **Translation method (Phase L7)** | LLM-assisted (fast, fuzzy) vs strict bilingual-dictionary (slow, deterministic)? | LEXICOGRAPHY_ROADMAP §11.6 |
| A7 | **Microstructure sampling** | Measure every entry, or sample (10% / specific letter-bands / a fixed lemma set)? Which test lemmas beyond `gam` (e.g. `rāma`, `iti`, a BHS term)? | MICROSTRUCTURE-MACROSTRUCTURE §6 |

## B. Identifications / facts only you can confirm

| # | Item | Source |
|---|---|---|
| B1 | Identify **FRI, KNA, KOW, LRV** (codes present, full titles unclear; KOW = Kossowich per memory) | LEXICOGRAPHY_ROADMAP §11.5 |
| B2 | Verify **bibliography** I filled for the 6 documented repos — esp. BUR (Leupol / Maisonneuve) and BOP (1847 edition) | Handoff full-runbook gaps |
| B3 | Source for `.github/ISSUE_TEMPLATE/*.yml` (templates dir has only the 3 community files) | Handoff full-runbook gaps |

## C. Credentials / access needed

| # | Need | For |
|---|---|---|
| C1 | **GitHub token** (workflow + read:project scope) as a repo secret | Automate observatory refresh (M4 / csl-observatory#12); Tooling Roadmap audit |
| C2 | **Cologne server / analytics access** (Matomo/GA/logs; ability to run `redo_xampp_selective.sh`) | Public-artefact refresh; OBSERVATORY_DESIGN Phase 12 |
| C3 | **DNS** for `observatory.sanskrit-lexicon.org` + Cologne `uni-koeln.de/observatory` handover | Observatory mirrors |

## D. Confirmations (likely yes, just need a nod)

| # | Item |
|---|---|
| D1 | A Cologne admin will run / let the cron run `redo_xampp_selective.sh` so the 2026-05 csl-orig fixes propagate to Stardict/JSON/homepage. |
| D2 | OK to do the **M1** refresh-script modernization as a *backward-compatible* refactor (parameterise path with a default), even though python2→3 of `make_babylon.py`/`json_from_babylon.py` still needs the server to test. |
| D3 | OK to wire the full `make_xml` XML-parse check into CI (heavier), or is the source-level BOM/UTF-8/`<L>`-balance guard enough? (csl-pywork#51) |

---

*Engineering items trace to [`ROADMAP.md`](ROADMAP.md) + the [csl-corrections handoff](https://github.com/sanskrit-lexicon/csl-corrections/blob/master/.ai_state.md). Research items trace to [`LEXICOGRAPHY_ROADMAP.md`](LEXICOGRAPHY_ROADMAP.md) §11 and [`MICROSTRUCTURE-MACROSTRUCTURE.md`](MICROSTRUCTURE-MACROSTRUCTURE.md) §6.*
