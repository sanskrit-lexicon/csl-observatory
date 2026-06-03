# L0 / lexicography-genealogy stream — handoff (start here)

**Date**: 2026-06-03 · **Model used**: Opus · **Stream**: the dictionary-genealogy research
(separate from the measurement/Paper-1 stream). Consolidated cross-stream handoff:
[`SESSION_HANDOFF.md`](SESSION_HANDOFF.md); open human decisions: [`DECISIONS_NEEDED.md`](DECISIONS_NEEDED.md).

---

## 1. State — Phase L0 is fully built and validated

The convention-fingerprint cladogram (L0_DESIGN) and all four post-L0 decisions are done.

| Phase | What | Status |
|---|---|---|
| L0 | convention fingerprint → distances → UPGMA/NJ trees + RF + bootstrap + validation | ✅ |
| (gold) | Patel 2016 PDF ingested — his per-dict assignments for conventions 1–7 | ✅ |
| L0.7 | content↔convention **reformatting residual** | ✅ |
| L0.9 | Patel's open conventions (dims 31–33) + **hwnorm1#21** contribution | ✅ |
| L0-rigor | **Bayesian Mk MCMC** + NJ bootstrap; three-algorithm comparison | ✅ |

Read in order: [`L0_DESIGN.md`](L0_DESIGN.md) → [`L0_RESULTS.md`](L0_RESULTS.md) →
[`refs/fingerprint_conventions.md`](refs/fingerprint_conventions.md) +
[`refs/concordance.md`](refs/concordance.md). Live dashboard page: **`/conventions`**.

### Headline finding (the publishable result)
**Convention-lineage ≠ content-lineage.** The convention fingerprint recovers *formatting*
genealogy (who adopted whose house style): PWG→PW→SCH and WIL→SHS are razor-sharp (bootstrap
0.79/0.70/0.81; Bayesian 1.00/1.00). It does **not** recover *content* lineages where the heir
reformatted: PWG→MW, MW72→MW score ~0. Monier-Williams imported the Petersburg lexicon but
recoded its conventions (ṛ-stems `-ṛ` not `-ar`, etc.). Quantified as the **reformatting
residual** = content_containment − convention_similarity (top: CAE→MW 0.68, MD→MW 0.65,
CCS→MW 0.62, WIL→YAT 0.54). Robust across UPGMA/NJ/Bayesian (L0_RESULTS §4b). → **Paper H §5**
([`articles/paper_H_convention_vs_content_lineage.md`](articles/paper_H_convention_vs_content_lineage.md))
+ **standalone methods note, PUBLICATIONS Article 20**.

## 2. Scripts & data map

Pipeline order (all under `scripts/L0/`, outputs under `data/L0/`):
```
s2_fingerprint.py    dims 9–30 auto-extracted from csl-orig sources
s2b_patel_auto.py    dims 2,4 mechanical (for dicts Patel doesn't cover: LRV/FRI)
s2d_patel_gold.py    dims 1–7 from Patel 2016 gold → patel2016_assignments.csv
s2e_patel_open.py    dims 31–33 (takārānta/sakārānta/rephānta) → patel_open_assignments.csv
s3_cladogram.py      encodings × metrics → UPGMA+NJ (8 trees) + RF + bootstrap + validation
s4_residual.py       content↔convention reformatting residual + scatter
s5_bayesian.py       NJ/UPGMA bootstrap + Bayesian Mk MCMC; algorithm_support_comparison.csv
```
Key data: `convention_fingerprint.csv`, `distances/B_whamming.csv`,
`trees/canonical_consensus.{newick,png}`, `bootstrap_support.csv`,
`content_convention_residual.csv`, `algorithm_support_comparison.csv`, `validation_report.json`,
`bayesian_report.json`. Dashboard data is CI-copied (`refresh-observatory.yml`), not committed in `src/data/`.

## 3. ⚠️ The MW "content-absorption" precision problem (KEY open issue)

Paper-H/L0_RESULTS state MW "absorbed 89–94% of PWG/MW72 content (sanhw1 containment)".
**This number is size-confounded and must not be read as content-copying.** Evidence
(`data/sanhw1_inheritance_edges.csv`, all edges → MW):

| source→MW | containment | source size | lineage? |
|---|---|---|---|
| BOP→MW | **0.94** | 8,505 | unrelated (Latin etymological) |
| BEN→MW | 0.94 | 17,036 | weak |
| MD→MW | 0.93 | 20,103 | — |
| CCS→MW | 0.90 | 28,751 | German |
| MW72→MW | 0.90 | 51,159 | direct (same author) |
| PWG→MW | 0.89 | 106,083 | direct |
| PW→MW | 0.85 | 151,349 | direct |

Containment **falls monotonically with source size** and is *highest* for the unrelated BOP.
MW (194k lemmas) contains almost any older dict's mostly-common-core vocabulary regardless of
descent. So raw containment measures *MW's coverage × the source's rarity profile*, **not**
inheritance. The convention≠content finding is unaffected (it never relied on the %), but the
magnitude claim needs replacing.

### What's needed to make "MW absorbed PWG content" precise — a ladder (cheap → strong)

1. **Size-corrected association** (cheap, sanhw1 only): replace raw containment with **lift**
   = observed overlap ÷ expected-given-sizes (hypergeometric / PMI), or a coverage-null. Needs
   per-dict lemma *sets* (sanhw1.txt, ~10 MB, at `hwnorm1/sanhw1` — fetch; not in repo locally).
2. **Rare/exclusive-lemma containment** (cheap): restrict to the source's *rare* lemmas (drop
   the common core). If MW contains PWG's idiosyncratic/rare lemmas, that *is* lineage evidence.
   This is the single highest-value next computation.
3. **Citation-set overlap** (Phase L6, needs corpus parse): do MW and PWG cite the *same* `<ls>`
   references for the same lemma? Language-neutral, strong copy signal.
4. **Entry-text similarity** (Phase L4): for shared lemmas, definition/gloss string similarity
   (post-normalisation) — distinguishes "both list *gam*" from "MW copied PWG's *gam* entry".
5. **Forensic** (Phase L3): shared rare typos / idiosyncratic abbreviations / **citation
   truncation** (PWG `Rv. 1.22.16` → MW `RV.` is one-directional evidence of flow).
6. **Per-volume temporal restriction**: PWG is 7 vols (1855–75); MW72 (1872) could use only
   vols 1–4 (≈ letters a–p). Compute PWG→MW72 containment *restricted to PWG's pre-1872 letters*
   (L0_DESIGN §13). Makes the directed claim historically exact.

Until (1)–(2) land, phrase results as **"X% of PWG's *headwords* recur in MW"** (lemma-set
presence), never "absorbed X% of content".

## 4. Queued next work (pick up here)

- **(A) Sharpen the content claim** — implement ladder steps 1–2 (size-corrected lift +
  rare-lemma containment) using sanhw1.txt. Fast, high-value, directly answers this handoff.
- **(B) Write Article 20 / Paper H §5 in full** — all convention-side numbers are in hand;
  the content side should use (A)'s corrected numbers, not raw containment.
- **(C) Complete the dict set** — LRV/FRI are gated (not in Patel's 36; annotate from source);
  KNA/KOW/AMAR need local sources from Cologne. Then re-run s2*→s3→s5 for the all-37 tree.
- **(D) Phases L3/L4/L6** — forensic + entry-similarity + citation-set: the real content-copy
  evidence (and Paper M's spine).

## 5. Conventions & norms (do not relearn)

- **Document first**: update `.ai_state.md` (csl-corrections) + touched docs and commit as each
  deliverable lands. Commit trailers: infra repos (csl-observatory) use `Co-Authored-By: Claude`;
  dictionary repos use **none**.
- **Comment-noise**: Cologne maintainers dislike bot noise on dict repos; keep issue comments
  minimal, edit-in-place. The hwnorm1#21 contribution was one substantive issue as gasyoun — that's the bar.
- **Push pattern (Windows/PowerShell)**: `git pull origin <branch> --rebase` then push; native
  `git push` stderr trips PS error-detection harmlessly. No script-blocks/subexpressions in PS.
- **Site builds**: `cd observatory/site; npm run build` — needs `cp data/*.csv src/data/` first
  (CI does it); verify exit 0 + the page has no missing-reference warnings.
- **csl-orig** sources are at `../csl-orig/v02/<code>/<code>.txt`; 32 of 37 present locally
  (KNA/KOW/AMAR absent). Scan FULL files for mid/late-alphabet probe lemmas (the s2e CAP lesson).
- **Validate detectors against real entries** before trusting numbers (the recurring lesson —
  it caught the s2e CAP bug and the s5 exact-cherry-metric issue).

## 6. Decisions

Resolved 2026-06-03 (DECISIONS_NEEDED "Post-L0"): next=L0.7 ✅ · Patel-open→hwnorm1 ✅ ·
paper=both (Article 20 + Paper H §5) ✅ · rigor=Bayesian MCMC+NJ ✅.
Open/human: complete-dict-set sourcing (Cologne); whether to gate the paper-final tree on all 37.
