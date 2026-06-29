---
title: Repository Benchmarks
toc: false
---

# Repository Benchmarks

How CSL compares to peer projects at the repository and project-governance
level. This page does not compare dictionary content, corpus data, lookup
traffic, or publication impact.

## Comparison Matrix

Eight digital-humanities lexicon and corpus projects are compared across five repository-governance dimensions: domain, founding year, open-source status, public issue tracking, and number of public repositories. The CDSL project's distinguishing characteristics are its fully public GitHub-tracked issue workflow and its large number of per-dictionary repositories — features that are rare among peer humanities digitisation efforts. Most comparable projects either have no public repository tracking or have consolidated their content into a small number of monolithic repositories rather than per-dictionary repos.

> **How to read:** Each row is one project; columns capture five repository-level governance attributes. Cells with "n/a" mean the dimension is not applicable (e.g. a commercial platform that has no public repos). "~N" estimates are approximate pending validation. **Example 1:** TLG, the oldest and most comprehensive Greek lexicography project, scores "No" on both open source and public issue tracking — it is a commercial subscription resource with no public repository governance. **Example 2:** CDSL's 76 repos vs. Perseus's ~30 and CDLI's ~10 illustrates that CDSL deliberately splits content into many small per-dictionary repos rather than one or a few large monoliths — a structural choice that enables per-dictionary issue tracking but increases governance overhead.

| Project | Domain | Started | Open source | Issues tracked publicly | Repos |
|---|---|---:|---|---|---:|
| **CDSL** (this) | Sanskrit lexicography | 2014 | Yes (CC-BY-SA + GPL) | Yes (GitHub) | 76 |
| Thesaurus Linguae Graecae (TLG) | Greek lexicography | 1972 | No | No | n/a |
| Perseus Digital Library | Greek + Latin lexicon + corpus | 1985 | Yes | Partial (issues on GitHub) | ~30 |
| Cuneiform Digital Library Initiative (CDLI) | Sumerian / Akkadian | 2000 | Yes | Yes (GitHub) | ~10 |
| DDBDP (Duke Databank Documentary Papyri) | Papyrology | 1982 | Yes | Yes (papyri.info) | ~5 |
| Pandanus (Czech Sanskrit dict) | Sanskrit lexicography | 2002 | Yes | No | ~3 |
| Sanskrit Heritage (G. Huet) | Sanskrit morphology | 1995 | Yes (LGPL) | Personal site | ~8 |
| Digital Corpus of Sanskrit (DCS) | Sanskrit corpus + lexicon | 2007 | Yes | Yes | ~5 |

Numbers in cells like "~30" are estimates pending validation. They are used
only as project-level metadata, not as claims about corpus or dictionary
coverage.

> **Conclusion:** CDSL is the only Sanskrit lexicography project in the comparison with both fully open content and fully public repository-level issue governance. The closest structural peer is Perseus, which has public GitHub issues but far fewer repos and less systematic per-dictionary tracking. This positioning supports the claim that CDSL's build-meta infrastructure is genuinely novel in this domain — the observatory itself is tracking a governance model that has no obvious peer to benchmark against.

## Positioning Chart

A future chart may place CDSL on repository-level axes:

- Openness: license and public access.
- Throughput: issues, PRs, and commits per active year where public.
- Contributor diversity: commit and issue participation where public.
- Repository documentation completeness.
- Release and workflow visibility.

If a comparator lacks public repository evidence, it should be shown as
`unknown` rather than filled from content, corpus, lookup, or citation sources.

[back to overview](/)
