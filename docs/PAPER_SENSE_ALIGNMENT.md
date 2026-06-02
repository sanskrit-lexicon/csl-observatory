# Paper (methods) — Sanskrit-Anchored Cross-Language Sense Alignment

**Status**: outline · decided as a standalone paper 2026-05-31 · feeds Paper L.
**Type**: short computational-lexicography / digital-humanities methods paper.
**Owner**: M. Gasūns + Claude. **Evidence base**: [R2_FINDINGS.md](R2_FINDINGS.md), `scripts/lexico/`, `data/lexico/`.

## Working title

*Anchoring on Sanskrit: deterministic cross-language sense alignment across 15 historical Sanskrit dictionaries.*

## Thesis / abstract

Historical Sanskrit dictionaries gloss the **same** Sanskrit headwords into different metalanguages — German (Petersburg, Schmidt), English (Wilson, Monier-Williams, Apte, Benfey), French (Stchoupak), and Sanskrit itself (Vācaspatya, Śabdakalpadruma). Comparing their **senses** has therefore required translation. We show this is unnecessary: because every tradition exposes Sanskrit material *inside* each sense — cited forms, synonyms, cognates, and citation sigla — senses can be aligned **deterministically, with no translation**, by the Sanskrit they share ("anchor on Sanskrit"). We split each dictionary's entries into senses with per-tradition heuristic grammars, fingerprint each sense by its Sanskrit tokens + `<ls>` citations, and align by fingerprint overlap. Applied to 15 CDSL dictionaries (1822–1957), the method aligns German↔English↔Sanskrit senses and yields three results on dictionary genealogy.

## Contributions

1. **A deterministic, translation-free sense-alignment method** for multilingual historical lexicography (reproducible; no LLM), with per-tradition sense-splitter grammars (Western / indigenous-quotation / reverse English→Sanskrit).
2. **H1** — sense granularity is a **lexicographic-tradition trait, not temporal** (full corpus, 11 dicts; year-trend r = 0.06). A covariate to control for, correcting the "later = finer" intuition.
3. **H2** — **citation density predicts a sense's survival** into descendant dictionaries (cited 70% vs uncited 54%).
4. **H3** — derivatives **copy or condense, they do not net-add** senses; forensic centerpiece: Śabda-Sāgara (1900) reproduces Wilson (1832) sense glosses **82% word-identical**, a microstructure-level confirmation of the lemma-overlap edge (WIL ⊆ SHS ≈ 0.953).

## Structure (provisional)

1. Introduction — the multilingual-metalanguage problem; why translation-based comparison is brittle.
2. Data — the CDSL `csl-orig` corpus; the four structural clusters.
3. Method — per-tradition sense splitting; the Sanskrit fingerprint; alignment.
4. Validation — within-edition (Apte 1890/1957) and cross-language (PWG↔Apte) alignments.
5. Results — H1 (granularity×tradition), H2 (citation→survival), H3 (copy/condense).
6. The interactive explorer (reproducibility + a practitioner artifact).
7. Limitations — coarse indigenous/verb grammars; AE reverse over-match; headword-splitting confound.
8. Conclusion — Sanskrit as the language-agnostic alignment anchor for the whole CDSL family.

## Reproducibility

All deterministic, stdlib-only, reads sibling `csl-orig`:
`sense_split.py` (splitter + alignment), `h1_analysis.py` (granularity×year), `h2h3_analysis.py`
(survival + drift), `r2_explorer.py` (interactive figure). Data: `data/lexico/`.

## Open before submission

- Fixed simple-lemma panel to fully de-confound H1 (headword-splitting).
- Finer indigenous (VCP/SKD) splitting + verb grammar for completeness of the cross-tradition claim.
- Co-author (per the PUBLICATIONS Russian-co-author convention) + target venue.
