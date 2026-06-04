# CDSL Ecosystem — Improvement & Optimization Roadmap

_Engineering/quality roadmap for the [`sanskrit-lexicon`](https://github.com/sanskrit-lexicon) organisation (77 repos). Drafted 2026-05-30, grounded in concrete issues observed during the 2026-05 correction + documentation + analytics cycle. After the 2026-06 boundary decision, this roadmap is limited to GitHub/org maintenance work. Dictionary content, standards/export, DCS/corpus, and broad publication planning live elsewhere._

## How to read

- **Lens**: 🛡 reliability/tech-debt · 📖 data-quality · ⚙ automation/CI · 📚 docs/governance
- **Impact** / **Effort**: H / M / L. "Start here" = high impact, low effort.
- **Evidence** ties each item to something actually hit this cycle, so nothing here is speculative.

---

## 1 · Quick wins (high value, low effort — start here)

| # | Item | Lens | Impact | Effort | Why / evidence |
|---|---|---|---|---|---|
| Q1 | **BOM-tolerant `hw.py` / `make_xml.py`** (`utf-8-sig`) | 🛡 | H | S | A stray UTF-8 BOM masqueraded as a cryptic `init_entries Error 2` and cost real diagnosis time. **Filed: [csl-pywork#50](https://github.com/sanskrit-lexicon/csl-pywork/issues/50).** |
| Q2 | **CI guard on `csl-orig` changes**: no-BOM + UTF-8-NFC + `ElementTree` XML-parse | 🛡⚙ | H | S | The BOM regression reached `origin` before detection. A pre-merge check stops the whole class of encoding/markup breakage. |
| Q3 | **`.gitattributes` (`* text=auto eol=lf`) across repos** | 🛡 | M | S | Every Windows commit this cycle warned *"LF will be replaced by CRLF"*; normalising EOL removes the noise and avoids accidental whole-file diffs. |
| Q4 | **Canonical contributor-identity map** (`contributors_map.json`) | 📚 | M | S | Stats showed the same person split as `drdhaval2785` / "Dr. Dhaval Patel", `funderburkjim` / "James Funderburk", plus "Your Name". One map fixes every downstream metric. |
| Q5 | **Shared Mermaid-validation CI step** for generated READMEs | ⚙ | M | S | Validated 21 diagrams by hand this cycle via `gh api markdown`; a reusable step makes it automatic. |
| Q6 | **Bot / AI commit + comment policy** (in `CONTRIBUTING`) | 📚 | M | S | Maintainers pushed back on the value of bot-attributed commits/comments (MWS#194). A short written norm (edit-in-place, no attribution noise on dict repos) prevents friction. |
| Q7 | **Finish issue-taxonomy on remaining repos** (`/cologne-runbook-all`) | 📚 | M | M | 6 milestone-less dict repos were brought to full taxonomy this cycle; the rest of the org still needs the pass. |

## 2 · Medium-term

| # | Item | Lens | Impact | Effort | Why / evidence |
|---|---|---|---|---|---|
| M1 | **Modernise `redo_xampp_selective.sh`**: python2→3, parameterise the hardcoded `/var/www/html/cologne` path, document prereqs | 🛡⚙ | H | M | The artefact-refresh is unrunnable off the one server (hardcoded paths, python2, cross-org push, 5 sibling repos). Blocks anyone but the server from refreshing Stardict/JSON/homepage. |
| M2 | **Encoding audit + round-trip validation** (SLP1 ↔ IAST ↔ Devanāgarī); finish AS→SLP1 | 📖⚙ | H | M | MW72 still carries legacy AS-scheme forms (issues #3/#4); a round-trip CI check would flag lossy entries org-wide. |
| M3 | **README/`CLAUDE.md` + citation/community files for all remaining repos** (runbook phases 8–16) | 📚 | M | M | 6 dict repos were fully documented this cycle; ~30 dict + ~20 tooling repos remain (many have only stub READMEs). |
| M4 | **Automate the observatory refresh** (monthly CI) on the commits-API + git-churn path | ⚙ | M | M | `/stats/contributors` & `/stats/code_frequency` returned HTTP 202 across the whole org and never resolved; [`scripts/contributor_stats.py`](../scripts/contributor_stats.py) already replaces them — wire it into the dashboard build. |
| M5 | **Local-clone hygiene**: a setup script that full-clones siblings | 🛡 | M | S | Several repos sat locally as shallow `.git`-only shells (1 commit, no working tree), silently breaking churn and doc generation until un-shallowed. |
| M6 | **Markup-normalisation sweep across all dicts** (extend the 10-dict whitespace pass; `/cologne-markup-fix`) | 📖 | M | M | The 2026-05 batch fixed 10 dicts; the same `<ls>`/`<lex>`/whitespace classes exist elsewhere. |
| M7 | **Licensing + FAIR standardisation**: fix KRM's GPL-vs-cff mismatch; LICENSE + CITATION.cff + Zenodo DOI on every repo | 📚 | M | M | KRM ships GPL-3.0 while its `CITATION.cff` declares CC BY-SA 4.0; licensing is inconsistent across repos. |

## 3 · Strategic / long-term

| # | Item | Lens | Impact | Effort | Why / evidence |
|---|---|---|---|---|---|
| S1 | **Migrate the generation/refresh pipeline off the single Cologne server** (containerise; CI/CD; drop hardcoded paths, python2, cross-org push) | 🛡⚙ | H | L | The whole public-artefact pipeline is a single-host cron with hardcoded assumptions — a resilience and bus-factor risk. |
| S2 | **Org-wide repository health baseline**: README, license, citation, issue-template, PR-template, workflow, and release metadata coverage | 📚 | H | M | Keeps the observatory on repository evidence and gives maintainers a concrete cleanup queue. |
| S3 | **Workflow reliability baseline**: CI, cron, Dependabot, release, and artifact-refresh workflow status across active repos | ⚙ | H | M | Turns maintenance risk into measurable repository/process evidence without owning dictionary or standards pipelines. |
| S4 | **Unified CI/CD + pre-commit + CodeQL + Dependabot org-wide** (skills exist) | ⚙ | M | M | One source of truth for conventions; today each repo is configured ad hoc. |
| S5 | **Reusable observatory report package** on the GitHub/org backbone | 📚 | M | M | Formalise reproducible, citable repository metrics. Keep broad publication planning outside this repo. See [`OBSERVATORY_DESIGN.md`](OBSERVATORY_DESIGN.md). |

---

## Suggested first sprint

Q1 (filed) → **Q2 + Q3** (one CI workflow + `.gitattributes` template, deployable org-wide) → **Q4** (identity map, unblocks all analytics) → **M1** (un-hardcode the refresh, the biggest single operational risk).

## Tracking

Top items are mirrored as GitHub issues on the relevant tooling repos (labelled per the tooling-repo taxonomy) and on the org [Tooling Roadmap](https://github.com/orgs/sanskrit-lexicon/projects/9). Data-quality items that target dictionary text are tracked on those dictionaries' own issue trackers to keep this list engineering-focused.

---
*Drafted 2026-05-30 from the 2026-05 observation cycle. Companion data: [`docs/CONTRIBUTOR_STATS.md`](CONTRIBUTOR_STATS.md).*
