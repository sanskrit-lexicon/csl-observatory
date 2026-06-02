# Decisions needed from the maintainer

Consolidated list of items that are **blocked on a human** (a decision, a credential, or an action only you can take). Maintained so an agent can resurface it at the start of a session. Last updated 2026-05-31 (pruned resolved; research round-2).

> Agent note: when M.G. asks "what's next?" or resumes, **surface this list first**.

---

## A. Decisions (pick an option)

| # | Decision | Options / recommendation | Source |
|---|---|---|---|
| A1 | **KRM license** | Its `LICENSE` is GPL-3.0 but `CITATION.cff` says CC-BY-SA-4.0. Align which way? *Rec: CC-BY-SA-4.0 (it's dictionary data).* | Roadmap M7 / KRM/CLAUDE.md |
| A3 | **LICENSE full text vs pointer** | The 6 documented dict repos got pointer-style CC-BY-SA-4.0 LICENSEs. Want the full legalcode (for GitHub auto-detection)? | Handoff full-runbook gaps |
| A4 | **Scan-only dicts** (AE, IEG, MWE, PD, PE, PGN, SNP, YAT — 8, not on GitHub) | Ingest via Cologne web-scrape (~1 day each) or omit with a "future work" note? | LEXICOGRAPHY_ROADMAP §11.1 |
| A5 | **Add PD** (Deccan College encyclopedic dict, 1976) | Major modern dict; would strengthen Paper L; needs Cologne coordination. Include? | LEXICOGRAPHY_ROADMAP §11.2 |

*(A2, A6, A7, A8 resolved — see "Recently resolved" below.)*

## B. Identifications / facts only you can confirm

| # | Item | Source |
|---|---|---|
| B1 | Identify **KNA** — still unidentified (Sanskrit–Russian per handoff). *Resolved this session: **LRV** = Vaidya, *The Standard Sanskrit-English Dictionary* (1889); **FRI** = Frish's Sanskrit Reader (Cologne 2015); **KOW** = Kossowich Sanskrit–Russian.* | LEXICOGRAPHY_ROADMAP §11.5 |
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

## ✅ Recently resolved (2026-05-31)

| # | Resolution | Documented in |
|---|---|---|
| A2 | Taxonomy rollout done — 24 dict repos (786 issues) + 4 tooling repos (153 issues), all verified all-clean. | SESSION_HANDOFF.md; csl-corrections `.ai_state.md` |
| A6 | Cross-language sense alignment **anchors on Sanskrit** (SLP1 fingerprints) — no gloss translation. | RESEARCH_LAYER_ROADMAP §5.1 |
| A7 | **Full-corpus** measurement; anchor lemmas `gam`/`dharma`/`rāma`/`iti`/`bodhisattva`. | RESEARCH_LAYER_ROADMAP §5.1 |
| A8 | R2 sense-splitter = **heuristic per-dict**, deterministic, no LLM. | RESEARCH_LAYER_ROADMAP §5.1 |
| B4 | SHS author = **Kulapati Jibananda Vidyāsāgara**. | SHS README/CLAUDE; M3 docs |
| B5 | ApteES = reverse-direction English→Sanskrit docs built (`{@en@}`/`<s>skt</s>`/Ⓐ-Ⓑ). | ApteES README/CLAUDE; M3 docs |
| Research round-2 | Frequency join = **DCS** (local dump `GitHub/DCS`); practitioner hosting = **main dashboard page**; first hypothesis = **H1**; semantic fields = **Amarakośa-native**. | RESEARCH_LAYER_ROADMAP §7 |

---

*Engineering items trace to [`ROADMAP.md`](ROADMAP.md) + the [csl-corrections handoff](https://github.com/sanskrit-lexicon/csl-corrections/blob/master/.ai_state.md). Research items trace to [`LEXICOGRAPHY_ROADMAP.md`](LEXICOGRAPHY_ROADMAP.md) §11 and [`MICROSTRUCTURE-MACROSTRUCTURE.md`](MICROSTRUCTURE-MACROSTRUCTURE.md) §6.*
