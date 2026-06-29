---
title: Conclusions index
toc: true
---

# Conclusions index

One-paragraph summaries of what each visualisation in the observatory tells us, grouped by page. Follow the section links to see the underlying charts and data.

---

## Overview ([/](/))

**How the work changed over 13 years.** The org's issue history is a direct readout of its digitisation roadmap — first correct the text, then build the links, then improve the structure. The recent growth of `enhancement` and `bug` issues reflects a mature project that is now maintaining and improving a stable infrastructure rather than racing to complete a corpus.

**Annual throughput.** The opened/closed gap is largest in 2020–2022, the peak of the correction campaigns, and narrows in 2023–2025 as those campaigns wound down. The 2026 data shows closings keeping pace with openings — a healthier balance, consistent with the backlog-reduction trend on the Activity page.

**Top 10 most active repositories.** The top-10 list is heavily skewed towards csl-orig and a handful of high-correction dictionaries, confirming that the project's activity is driven by content work rather than infrastructure churn. A tooling repo appearing in the top 10 is a signal worth investigating — it may indicate fragile tooling that requires frequent fixes, or an actively developed capability.

---

## Tech stack ([/tech-stack](/tech-stack))

**Repos by primary language.** Python's dominance reflects the correction and generation pipeline that forms the project's backbone. Most HTML repos are dictionary display pages produced by csl-pywork rather than hand-written front-ends. The language mix has stayed stable over 13 years — the project never shifted to a new stack.

**Repos by size.** The size distribution is driven almost entirely by content rather than code: the two or three largest repos hold years of accumulated correction files and dictionary source text, while the rest of the tooling ecosystem is compact. Contributors cloning the full org for the first time should expect a heavily skewed download — most repos are small, but a few dominate total disk footprint.

**Repo creation timeline.** The three-wave pattern reveals how the project evolved — from a raw corpus upload, through infrastructure consolidation, to a mature and self-monitoring toolset. Dictionary repos named by abbreviation cluster at the earliest dates; tooling repos with the `csl-` prefix accumulate most recently, making repo-naming a proxy for both age and purpose.

---

## Activity ([/activity](/activity))

**Org-wide throughput (commits, issues, PRs).** Commit and issue volume peaked together in 2020–2022, driven by bulk correction campaigns on csl-orig. Pull requests barely register before 2026 — the org operated through direct commits and issue threads for its first decade, a workflow shaped by the small trusted-core team structure and the high throughput of individually-applied dictionary fixes.

**Open-issue backlog.** The backlog's single large peak-and-drop confirms that the 2025 correction campaign was a coordinated, finite effort rather than chronic accumulation — the project opened thousands of issues deliberately as a tracking mechanism, then resolved them in bulk. This is a sign of good campaign hygiene, not of growing technical debt.

**Issues opened per month.** Issue volume is dominated by a handful of high-activity repos (csl-orig, MWS) with sporadic bursts from the rest; the org does not have uniformly distributed activity across its 76 repositories. The stacked chart makes visible what summary statistics hide: the correction campaigns are discrete, high-intensity episodes, not continuous background work.

**Commits per month.** Commit volume is more concentrated than issue volume: csl-orig and csl-corrections account for a disproportionate share of all commits. This confirms the bus-factor finding — not only is the contributor base tiny, but the work itself is physically concentrated in a small number of repositories whose history is dominated by one or two authors.

**Activity heatmap.** A handful of repos — csl-orig, MWS, csl-pywork — light up the heatmap across multiple years; the large majority show at most one or two active years. This is a "build-it-once, then maintain-lightly" pattern driven by the dictionary digitisation model: a repo is created for one dictionary, heavily worked during its correction campaign, then settles into low-volume maintenance.

**Annual distinct commit-authors.** The org has never had more than ~15 distinct commit-authors in a year, and the trend is flat rather than growing. Volume-per-person has increased, but the team itself has not. This is the single most important context for reading any activity metric: high throughput does not indicate a large community — it indicates a small group of extremely productive, highly committed individuals.

---

## Community ([/community](/community))

**Top contributors by total commits.** The contribution distribution is sharply unequal: a single contributor accounts for more than half of all recorded commits, with the next two forming a tight core trio — everyone else trails far behind. This is the primary sustainability risk for the org: not low activity, but extreme concentration in individuals who cannot easily be replaced.

**Repo coverage per contributor.** The same core trio that dominates commit totals also has the widest repo coverage — they are not just prolific but spread across the entire org. Their absence would create gaps not in one dictionary but across every layer of the stack, from source data to web display to CI infrastructure.

**New contributors per year.** Contributor acquisition is sparse and sporadic — some years add zero new people, and the trend shows no growth in the onboarding pipeline. This amplifies the long-term sustainability risk: the project depends on its existing core indefinitely, with no observed mechanism for refreshing the contributor base as founding members age or step back.

**Bus factor & contributor concentration.** Of the tracked repositories with human contributors, the large majority depend on a single maintainer for the majority of their history. Just one person accounts for half of all recorded contributions, and the core trio carries roughly 97% — a Gini coefficient well above 0.8 confirms a long tail of one-off contributors behind a tiny active core. This is a critical finding for the project's long-term governance.

---

## Issue taxonomy ([/coverage](/coverage))

**Issue typology evolution.** `text-correction` dominated the issue base for most of the project's life, but since 2022 `markup`, `link-target`, and `enhancement` have all grown, signalling a shift from raw correction work towards structural improvement and web-display feature development. The project's issue history is a direct readout of its digitisation roadmap.

**Taxonomy adoption and conformance.** The taxonomy rollout was effectively complete by 2024–2025, with conformance near 92% at peak. The 2026 dip is expected — newly opened issues are not yet milestoned — and is not a sign of declining standards. Retroactive label application via the runbook was largely successful in bringing the historical issue base into conformance.

**Issue type distribution (all-time).** `text-correction` and `link-target` together account for the majority of the project's entire issue history, directly mirroring its two dominant workflow phases: correcting OCR errors in dictionary text, then building clickable links to scanned PDF pages. The distribution is the project's work log turned into a bar chart.

**Open vs closed by repo.** The correction-heavy repositories (csl-orig, MWS) carry the most issues in absolute terms but also show high closure rates — their campaigns ran to completion. The current open backlog is concentrated in a smaller number of repos where correction campaigns are still in progress or triaging has not kept pace. Amber-heavy bars are the next places to focus review effort.

---

## Repository health ([/repo-health](/repo-health))

**Licensing.** The RH1 license rollout materially improved the org's licensing posture — the no-license and NOASSERTION backlogs are cleared except for a small number of archive/temp candidates blocked on the RH3 cleanup decision. The org's data is now legally usable by scholars who need a clear license to build on CDSL materials.

**Default branch.** Branch naming is the largest remaining hygiene gap after the license rollout: a substantial share of repos still default to `master`, complicating CI defaults and runbook scripts that assume `main`. Unlike licensing, this is a low-risk rename that can be done one repo at a time without touching content — the main barrier is maintainer time, not technical complexity.

**Repositories by flag count.** Most repositories cluster at one or two hygiene flags; the licensing gap was the most common single-flag source and was largely resolved by RH1. Only a handful of repos are fully clean on every dimension. The dominant remaining gaps are the legacy `master` branch (46 repos) and the small number of archive/temp candidates awaiting the RH3 decision.

---

## Cross-page synthesis

Three findings recur across every page and reinforce each other:

1. **Concentration** — one person carries more than half of all contributions; 65 of 76 repos have a bus factor of 1; the annual author count has never exceeded 15. The project's output is extraordinary for its team size, but its continuity depends on a tiny core.

2. **Campaign structure** — activity is not continuous background work but a series of discrete, intensive correction campaigns. Issue spikes and backlogs follow the campaigns precisely; the stacked charts on every activity page make this visible.

3. **Improving hygiene** — from near-zero licensing in 2014 to 90%+ recognised SPDX in 2026; from ~25% taxonomy conformance pre-2019 to 92% peak in 2025. The project has systematically improved its own governance metadata even as it continued high-volume content work.

Full narrative write-up: [synthesis report](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/reports/synthesis.md).

[← back to overview](/)
