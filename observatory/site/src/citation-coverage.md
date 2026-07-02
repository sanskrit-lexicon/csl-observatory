---
title: PWG citation coverage
toc: false
---

# PWG citation link coverage

How much of the PWG `<ls>` literary-source citation apparatus is **clickable** —
i.e. resolves to a Cologne **scan** (page image) or **HTML** (digital text)
target. A dictionary-content metric that complements the org/process metrics.

```js
const cov = await FileAttachment("data/pwg_citation_coverage.json").json();
```

<div class="grid grid-cols-4">
  <div class="card">
    <h2>Citation occurrences</h2>
    <span class="big">${cov.occurrences_total.toLocaleString()}</span>
  </div>
  <div class="card">
    <h2>Covered (link out)</h2>
    <span class="big">${cov.occurrence_coverage_pct}%</span>
  </div>
  <div class="card">
    <h2>Scan / HTML</h2>
    <span class="big">${cov.occurrences_scan.toLocaleString()} / ${cov.occurrences_html.toLocaleString()}</span>
  </div>
  <div class="card">
    <h2>Un-digitised works</h2>
    <span class="big">${cov.uncovered_works}</span>
  </div>
</div>

:::note
**Scope:** measured over the ~51 PWG roots translated so far for the RU/EN
[article site](https://gasyoun.github.io/SanskritLexicography/) — a subset, **not**
the whole dictionary. Snapshot: ${cov.as_of}.
:::

Of the **${cov.occurrences_total.toLocaleString()}** citation occurrences,
**${cov.occurrence_coverage_pct}%** link out
(**${cov.occurrences_scan.toLocaleString()}** to page scans +
**${cov.occurrences_html.toLocaleString()}** to HTML digital text). The remaining
**${cov.uncovered_works}** cited works have no Cologne target — chiefly
un-digitised texts (Suśruta, the Upaniṣads, the Śrauta/Gṛhya sūtras) — so they
cannot be linked from anywhere. Coverage is therefore **target-limited**, not
resolver-limited: the covered works are the heavily-cited backbone (Mahābhārata,
Ṛg-Veda, Rāmāyaṇa, Bhāgavata-Purāṇa …).

## Source

The source-of-truth reports live in the PWG repository, next to the rest of the
literary-source work, and are regenerated from the RussianTranslation pipeline:

- [`PWG/pwg_ls/pwg_ru_coverage/`](https://github.com/sanskrit-lexicon/PWG/tree/main/pwg_ls/pwg_ru_coverage)
  — [coverage index](https://github.com/sanskrit-lexicon/PWG/blob/main/pwg_ls/pwg_ru_coverage/CITATION_SOURCES.md)
  · [uncovered works](https://github.com/sanskrit-lexicon/PWG/blob/main/pwg_ls/pwg_ru_coverage/UNCOVERED_SOURCES.md)
  · [covered vs uncovered + frontier](https://github.com/sanskrit-lexicon/PWG/blob/main/pwg_ls/pwg_ru_coverage/COVERAGE_COMPARISON.md)
- data: [`pwg_citation_coverage.json`](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/observatory/site/src/data/pwg_citation_coverage.json)
- generator: [`build_citation_index.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/build_citation_index.py)
