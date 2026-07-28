# Datasheet Template — [Dataset Name]

_Created: 27-07-2026 · Last updated: 27-07-2026_

> Following Gebru et al., *Datasheets for Datasets* (2018/2021):
> <https://arxiv.org/abs/1803.09010>. To use: copy this file to the releasing repo as
> `docs/DATASHEET.md` (or a dataset-specific filename if the repo releases more than one
> dataset), fill every bracketed prompt below, and delete this instructional blockquote plus
> any section that is genuinely not applicable (state why, don't just omit it silently). See the
> filled OBS-T instance for a worked example:
> [docs/DATASHEET.md](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/docs/DATASHEET.md).
>
> **Release gate.** Per the `/data-release` discipline: no derived dataset release ships without
> a filled datasheet using this template (or an equivalent superset covering every mandatory
> section below).

Describes the released resource `[path/to/released.csv]` and its derivation. Snapshot:
`[YYYY-MM-DD]`. Regenerate with the pipeline in *Maintenance and Reproduction* below.

## Motivation

- **Purpose.** [Why was this dataset created? What task(s) is it intended to support?]
- **Created by.** [Who assembled it — person(s)/team, repo, and the source records/pipeline it
  draws from.]
- **Funding / sponsor.** [If applicable; otherwise state "None" explicitly rather than omitting
  the bullet.]

## Composition

- **Instances.** [What does one row represent? Total count.]
- **Layers / provenance mix.** [If instances come from more than one source layer (e.g. form
  submissions vs. mined git history), name each layer and its row count.]
- **Coverage.** [Temporal range, number of distinct sources (dictionaries/repos/contributors),
  and any other coverage dimension worth stating.]
- **Source edition + page range.** [Where applicable: which printed/digitized edition, volume,
  and page range the instances derive from. If the dataset has no print-edition lineage, state
  "Not applicable — [reason]" rather than leaving this blank.]
- **Fields.** [List every column/field with a one-line description; point to a JSON Schema file
  if one exists.]
- **Labels.** [For each labeled axis: name, the label set (enumerate values), and whether labels
  are mechanical/derived or human-adjudicated/inferred.]
- **Sampling.** [Is this the full population under some reconstruction rule, or an actual
  sample? If a sample, state the sampling frame and rate.]
- **Sensitive data.** [Any personal data (emails, names)? What is withheld vs. released, and
  under what pseudonymization rule?]

## Encoding & Transliteration Regime

- **Character encoding.** [e.g. UTF-8/NFC; note any BOM policy.]
- **Script / romanization scheme(s) in use.** [e.g. SLP1, IAST, Devanagari — name every scheme
  present in any field, and which field uses which.]
- **Conversion provenance.** [If fields were transliterated from one scheme to another, name the
  converter/pipeline step and whether raw source strings are retained alongside the converted
  form.]

## Collection Process

- **How.** [Export/scrape/mining method, per source layer if there is more than one.]
- **Who.** [Data collectors / instruments used.]
- **Timeframe.** [Collection window vs. the timeframe the content itself covers, if they
  differ.]

## Preprocessing, Cleaning, and Labeling

- [Normalization rules applied (script/case/whitespace). State what is preserved in raw form
  alongside any normalized field.]
- [Any deterministic vs. heuristic labeling/attribution routes, and how uncertain cases are
  flagged rather than silently promoted to a confident label.]
- [Any audit sample produced for QA, and where it lives.]

## Known Gaps & Label-Quality State

- **Evaluation harness.** [Name the gold/κ harness, if one exists, and the file(s) it
  reads/writes.]
- **Cohen's κ.** [Current value, annotator count, and whether it is "meaningful" (an adequate
  gold-sample size) or still pending.]
- **Per-class P/R/F1.** [Where reported; link the metrics file.]
- **Evidence-level split.** [If labels are split by derived vs. inferred (or an equivalent
  confidence stratification), give the current percentage split and which stratum is safe to use
  for high-stakes claims.]
- **Known gaps.** [Anything explicitly NOT yet validated — e.g. a label axis with too few gold
  rows to compute κ meaningfully.]

## Uses

- **Intended.** [Concrete tasks/research this data is meant to support.]
- **Caveats.** [What NOT to over-interpret — e.g. shares are over corrected events, not the
  latent error rate in the source material.]
- **Discouraged.** [Explicit misuse cases to warn against.]

## Evaluation Lineage

*(Optional — include only if this dataset's validation follows a named shared-task/benchmark
convention; delete the section otherwise.)*

- **Statement.** [Which established evaluation framework (e.g. MWSA) this dataset's label
  validation follows, and why.]
- **Scope.** [What does/doesn't change about the release because of this framing.]
- **Sources.** [Links.]

## Distribution

- **Where.** [Repo, and any intended archival deposit — Zenodo DOI status: concept + version
  DOI, or "pending".]
- **Data license.** [e.g. CC-BY-4.0; point to the `DATA_LICENSE.md`/`LICENSE-DATA` file.]
- **Code license.** [If the producing pipeline's code license differs from the data license,
  state both and point to `LICENSE`/`CITATION.cff`.]
- **Splits.** [Train/dev/test or other splits, and the rule used to construct them.]

## Maintenance and Reproduction

- **Maintainer.** [Repo/team responsible for updates.]
- **Updates.** [Cadence and what to check before publishing a refreshed release.]
- **Automated pipeline.**

```bash
[ordered list of scripts that regenerate the release from source]
```

- **Human-gated validation.** [Any steps that must NOT run unattended — e.g. gold-sample
  creation/scoring — listed explicitly so an agent doesn't invoke them by mistake.]

_Dr. Mārcis Gasūns_
