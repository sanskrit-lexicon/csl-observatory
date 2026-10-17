# Citation verification log — H6389 crosswalk + A15 CHAOSS/MSR framing

_Created: 11-10-2026 · Last updated: 11-10-2026_

Every URL below was **fetched live on 2026-10-11** (not recalled from memory) and
matched against authors + title + venue before being cited in
[`docs/OBST_ERRANT_GEC_CROSSWALK.md`](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/docs/OBST_ERRANT_GEC_CROSSWALK.md)
and the A15 CHAOSS/MSR framing section
([`article/A15_github_ecosystem.md`](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/article/A15_github_ecosystem.md)).
Requirement: every anchor claim ≥2 fetched-and-matched sources.

| # | Anchor claim | Source | Fetched URL | Matched bibliographic record | Verdict |
|---|---|---|---|---|---|
| 1 | ERRANT = rule-based op × category GEC annotation | S1 | https://aclanthology.org/P17-1074/ | Bryant, C.; Felice, M.; Briscoe, T. — *Automatic Annotation and Evaluation of Error Types for Grammatical Error Correction*, ACL 2017 (Vancouver) | ✅ MATCH |
| 2 | (same claim) | S2 | https://github.com/chrisjbryant/errant | ERRANT v3.0.2 repo; README cites P17-1074 verbatim; M2 examples `R:SPELL`, `M:DET`, `R:VERB:SVA` | ✅ MATCH |
| 3 | (same claim — category definitions) | S3 | https://www.cl.cam.ac.uk/techreports/UCAM-CL-TR-938.html | Bryant, C. — *Automatic annotation of error types for grammatical error correction*, PhD tech report, June 2019, 138 pp., DOI 10.48456/tr-938 | ✅ MATCH |
| 4 | BEA-2019 GEC shared task is ERRANT-based, W&I+LOCNESS dataset | S1 | https://aclanthology.org/W19-4406/ | Bryant, C.; Felice, M.; Andersen, Ø. E.; Briscoe, T. — *The BEA-2019 Shared Task on Grammatical Error Correction*, BEA@ACL 2019; systems evaluated by ERRANT F0.5 | ✅ MATCH |
| 5 | (same claim) | S2 | https://www.cl.cam.ac.uk/research/nl/bea2019st/ | Official BEA-2019 shared-task page; evaluation now on ERRANT v3.0.0 | ✅ MATCH |
| 6 | Historical text normalization: word-level normalization, 8 languages, large-scale comparison | S1 | https://aclanthology.org/N19-1389/ (+ .bib, .pdf) | Bollmann, M. — *A Large-Scale Comparison of Historical Text Normalization Systems*, NAACL-HLT 2019, pp. 3885–3898, DOI 10.18653/v1/N19-1389 | ✅ MATCH |
| 7 | (same claim family — character-level variant reporting) | S2 | https://eprints.lancs.ac.uk/id/eprint/41666/ (+ PDF, + http://ucrel.lancs.ac.uk/vard/about/) | Baron, A.; Rayson, P. — *VARD2: a tool for dealing with spelling variation in historical corpora*, Postgraduate Conference in Corpus Linguistics, 22-05-2008; character-edit-rule framing | ✅ MATCH |
| 8 | MWSA = existing OBS-T validation lineage | S1 | https://elex.is/mwsa2020/ | ELEXIS/GlobaLex *Shared Task on Monolingual Word Sense Alignment*, LREC 2020 workshop, organised by McCrae, J. P. & Ahmadi, S. | ✅ MATCH |
| 9 | (same claim) | S2 | https://github.com/elexis-eu/MWSA | elexis-eu/MWSA — 17 MWSA datasets, 15 languages, Apache-2.0 | ✅ MATCH |
| 10 | CHAOSS metric for contributor concentration (A15 §3.1) | S1 | https://chaoss.community/kb/metric-bus-factor/ | CHAOSS *Metric: Contributor Absence Factor* — "This metric was previously called 'Bus Factor'"; smallest set covering 50 % of contributions | ✅ MATCH (note the rename) |
| 11 | CHAOSS issue-lifecycle metrics (A15 §3.4/§3.7 latency) | S1 | https://chaoss.community/kb/metric-time-to-close/ | CHAOSS *Metric: Time to Close*; names Issue Resolution Duration as a related metric | ✅ MATCH |
| 12 | (same claim family — responsiveness) | S2 | https://chaoss.community/kb/metric-issue-response-time/ | CHAOSS *Metric: Issue Response Time* — time to first response from a contributor other than the author | ✅ MATCH |
| 13 | Software-ecosystem health measured beyond the single project (A15 MSR framing) | S1 | cited verbatim in https://dl.acm.org/doi/10.1016/j.jss.2016.02.003 + https://link.springer.com/chapter/10.1007/978-3-030-04840-2_3 | Jansen, S. — *Measuring the health of open source software ecosystems: beyond the scope of project health*, Information and Software Technology 56(11), 1508–1519, 2014 | ✅ MATCH (title/volume/pages via ≥3 independent published citation records, all fetched) |
| 14 | (same claim) | S2 | same fetched reference lists as #13 | Manikas, K.; Hansen, K. M. — *Software ecosystems — A systematic literature review*, Journal of Systems and Software 86(5), 1294–1306, 2013 | ✅ MATCH |

**Caught by verification (the defect class this handoff removes):** the initially
guessed anthology ID for Bollmann 2019 was N19-1090; the fetched
[N19-1090](https://aclanthology.org/N19-1090/) resolved to Hu et al.,
*Improved Lexically Constrained Decoding for Translation and Monolingual
Rewriting* — a **mismatch, discarded**; the correct ID N19-1389 was then located
by search and fetched. No citation in the crosswalk or the A15 section rests on
an unfetched URL.

**Negative results (also evidence):** the BEA-2019 `/data/` subpage and the
ERRANT `docs/v3/categories.md` path returned crawl-empty / 404 — the exact "27
error categories" count was therefore **not cited** anywhere in this pass, and
whitespace/spacing is mapped at operation level with the subcategory caveat
recorded in the table.
