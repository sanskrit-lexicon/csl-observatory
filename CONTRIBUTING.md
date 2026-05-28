# Contributing to csl-observatory


> Inherits the [Sanskrit Lexicon org-wide contribution standard](https://github.com/sanskrit-lexicon/COLOGNE/blob/master/CONTRIBUTING.md). This file documents anything **repo-specific** on top of it.

The csl-observatory is the **measurement-and-analysis layer** for the Cologne Digital Sanskrit Lexicon (CDSL) project. We welcome contributions from Sanskritists, software engineers, lexicographers, digital humanists, and historians of linguistics.

## Three ways to contribute

### 1. Specific open roles

The observatory has standing positions for collaborators with focused expertise. Open an issue tagged `role-application` if you want to take any of these on:

| Role | What you'd do | Skill / time |
|---|---|---|
| **Annotator** (lexicography fingerprint) | Help annotate the 27 fingerprint dimensions × 41 dictionaries (some cells from Patel 2016, some auto-extracted, some need expert eye). Inter-rater agreement reported in publications. | Sanskrit lexicography knowledge; ~1-3 hours per dimension batch |
| **Validator** (cladogram results) | Review predicted inheritance edges against your own historical knowledge; flag false positives and missing true positives | Domain expertise; ad-hoc, ~30 min per review |
| **Dict miner** | Extend source-XML mining to additional dictionaries (especially scan-only PD, MWE, AE, IEG, PE, PGN, SNP, YAT, KOW, KNA) | Python + XML; per-dict 1-3 days |
| **Translator** (cross-language alignment) | Help align bilingual gloss data — e.g. PWG German↔MW English or KOW Russian↔WIL English | Bilingual fluency in any of: German, French, Latin, Russian, Sanskrit; per-batch 2-4 hours |
| **Paper co-author** | Co-author one of the planned papers (M, L, H) — bring domain expertise + writing | Academic experience; 4-6 months for a long paper |
| **Web/dashboard developer** | Improve the Observable Framework site, add new charts, refine the UX | JS/D3/Plot; ad-hoc |

### 2. General contributions

If you don't fit a specific role but want to help:

- **Open issues** for bugs, factual errors in the dashboard, missing data sources, or methodology suggestions
- **Submit pull requests** for any of the above
- **Comment on existing issues** with corrections, examples, or domain context
- **Cite our data** in your work — the public CSV/Parquet exports under `/data/` are CC-BY-SA-4.0 licensed; please credit and link the snapshot date

### 3. Acknowledgement and authorship policy

Contributions are credited transparently:

| Contribution level | Credit |
|---|---|
| ≤2 commits / annotations / minor PRs | Listed in `data/people.yaml` and the dashboard's **Community** page |
| ≥3 commits / a non-trivial component / non-trivial annotation batch (≥50 cells) | Named in the relevant paper's **Acknowledgements** |
| Substantial intellectual contribution to a paper's methodology, framing, or content | **Co-authorship** on that paper, with ORCID and affiliation |
| Lead role on a paper section or focused study (e.g. Phase L1.5 KOW⇄WIL) | First co-authorship on the resulting paper or section |

The line between "contribution" and "co-authorship" is a judgment call by the project lead (M. Gasūns) in consultation with the other named maintainers. We err on the side of crediting people; if you've done substantial work, ask.

## Process

### For data corrections / methodology fixes

1. Open an issue describing the error or improvement
2. Wait for triage (typically <1 week)
3. Submit a PR if you have a fix; we'll review

### For new analyses or charts

1. Open an issue with the proposal (one paragraph: what you'd like to compute, what chart, what insight)
2. Discuss in the issue thread
3. If accepted: implement as a script in `observatory/`, add data files to `data/`, add a page or chart to `observatory/site/src/`
4. Submit PR; reviewer (M. Gasūns or designated maintainer) merges

### For paper co-authorship interest

1. Email M. Gasūns directly (gasyoun@gmail.com) with a brief paragraph about what you'd want to contribute
2. Or open an issue tagged `paper-coauthor-interest`
3. We'll discuss scope, timing, division of labor

## What we DON'T accept

- Contributions that misrepresent the state of CDSL or any individual dictionary
- Removal of contributor credits without their consent
- Changes to license terms (CC-BY-SA-4.0 for data, GPL-3.0 for code) without organisational approval
- Speculation presented as empirical fact (mark hypotheses clearly)

## Data and code licenses

- **Data** (CSV, Parquet, JSON, snapshots): **CC-BY-SA-4.0**
- **Code** (Python, JS, scripts): **GPL-3.0**
- **Papers** (drafts and published versions): **CC-BY-4.0** unless the publishing venue requires otherwise

## Reproducibility & archival policy

Every published analysis is reproducible from public artifacts:

- Source data: GitHub API (live) + monthly snapshots in `observatory/snapshots/`
- Transformer code: `observatory/transform.py` and related scripts
- Analysis code: in `observatory/` (one script per major output)
- Data exports: in `data/` (CSV + Parquet)
- Annual snapshots will be deposited to **Zenodo** with DOI mint (auto via GitHub-Zenodo integration on release tags)
- Code preserved at **Software Heritage** (auto-saved via SWH's GitHub crawler)
- Papers will receive **Crossref DOIs** at publication

## Code of Conduct

Adheres to the [Contributor Covenant 2.1](CODE_OF_CONDUCT.md). Be respectful, inclusive, and professional. The CDSL community spans many countries, languages, and academic traditions; treat that diversity as a strength.

## Recognising existing contributors

Major credit to the foundational CDSL maintainers and contributors whose work this observatory is built on:
- **Jim Funderburk** (funderburkjim) — the project's longest-serving engineer
- **Dr Dhaval Patel** (drdhaval2785) — author of the headword normalisation framework + many tools
- **Mārcis Gasūns** (gasyoun) — project lead
- All named contributors in [`data/people.yaml`](data/people.yaml)

---

For full project plans, see:
- [`docs/OBSERVATORY_DESIGN.md`](docs/OBSERVATORY_DESIGN.md) — overall architecture
- [`docs/OBSERVATORY_ROADMAP.md`](docs/OBSERVATORY_ROADMAP.md) — measurement framework roadmap
- [`docs/LEXICOGRAPHY_ROADMAP.md`](docs/LEXICOGRAPHY_ROADMAP.md) — dictionary inheritance studies
- [`docs/L0_DESIGN.md`](docs/L0_DESIGN.md) — convention-fingerprint cladogram design
- [`docs/METALEXICOGRAPHY_ROADMAP.md`](docs/METALEXICOGRAPHY_ROADMAP.md) — data-richness typology + Paper E content
- [`docs/PAPER_1_OUTLINE.md`](docs/PAPER_1_OUTLINE.md) — Paper 1 (Quantifying) outline

Welcome aboard.
