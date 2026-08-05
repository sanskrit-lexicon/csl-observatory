# Indexing 29,000 pages so a dictionary can cite them: the PWG scan-index campaign, 2025–2026

_Created: 05-08-2026 · Last updated: 05-08-2026_

**Status:** full draft (A69, readiness 3/5) — complete prose, needs human revision, byline
and venue decisions. Drafted by Fable 5 (`claude-fable-5`) under
[H1863](https://github.com/gasyoun/Uprava/blob/main/handoffs/H1863-Fable_csl-observatory_pwg-scan-index-campaign-paper-draft_29.07.26.md);
every number in this draft is traced to committed campaign data in this repository (§ Data
availability), none is newly computed here.

## Abstract

The Böhtlingk–Roth *Sanskrit-Wörterbuch* (PWG, 1855–1875) supports its definitions with a
citation apparatus of 344,229 `<ls>` source references. A digital edition can only make
those references clickable if the printed editions they cite are page-indexed: for each
printed page, which verses does it carry, and which PDF page image shows it. Between
January 2025 and July 2026, eight volunteers — coordinated entirely in public GitHub
issues — page-indexed 55 printed editions, 28,963 pages in all, covering 73.7% of the
citation mass the campaign tracked. This paper describes the campaign as a measured
object: its coverage weighted by citation mass rather than page count, its per-volunteer
throughput, its velocity and publication lag, the wiring status of the resulting 37
public scan repositories, and the defects a static audit of the citation resolver found.
Two process findings stand out. First, the quality-review loop caught almost no volunteer
errors; what it caught, in volume, were errors in the dictionaries themselves, making the
indexing campaign an unplanned dictionary-proofreading instrument. Second, the expensive
failure mode was never a bad index but a wrong *edition* — citations that turned out to
follow a different printed edition than the one indexed. We state plainly what the data
cannot support: the sheet's own citation counts have undocumented provenance and are used
only as an internal ranking, never as a share of a dictionary-wide denominator.

## 1 · Introduction

A scholarly dictionary earns trust through its citations. The PWG cites its sources with
an abbreviation and a reference — `ŚĀK. 31, 14`, `TS. 1,2,3` — resolvable by a
nineteenth-century reader who owned the same printed editions. A twenty-first-century
reader does not, and a digital edition that merely reproduces the abbreviation has
preserved the letter of the apparatus while losing its function.

The Cologne Digital Sanskrit Dictionaries project (CDSL) restores that function by
linking each citation to the page image of the edition it cites. The mechanism needs
three artifacts per work: a public scan of the right edition, a per-page *index* mapping
printed page → verse range → PDF page, and resolver code that turns a citation string
into a URL. The scans and resolver are infrastructure; the index is labour — someone must
leaf through every page of a 2,420-page Brāhmaṇa and record where each section begins.

This paper documents the campaign that produced those indexes for the PWG: who did what,
how much got done, what it cost in review effort, what broke, and what the resulting
infrastructure can and cannot yet do. It is a descriptive study of a completed (in its
kāvya and kośa portion) volunteer campaign, written against committed, cross-validated
data rather than against recollection.

## 2 · Data and methods

### 2.1 Sources

Three committed artifacts ground every claim:

1. **The campaign registry** —
   [`data/pwg_scan_index_tracker/`](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/data/pwg_scan_index_tracker)
   (TSV + JSON), derived by
   [`scripts/pwg_scan_index.py`](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/scripts/pwg_scan_index.py)
   from a snapshot of the coordinator's tracking spreadsheet (all four tabs committed
   verbatim under
   [`snapshot/`](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/data/pwg_scan_index_tracker/snapshot)),
   cross-validated against the PWG repository's own abbreviation bibliography and
   citation extraction. Measured output:
   [`reports/pwg_scan_index.md`](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/reports/pwg_scan_index.md)
   (27-07-2026).
2. **The issue-trail reconstruction** —
   [`docs/PWG_SCAN_INDEX_CAMPAIGN_HISTORY_2025_2026.md`](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/docs/PWG_SCAN_INDEX_CAMPAIGN_HISTORY_2025_2026.md),
   built from forty coordinating issues across
   [sanskrit-lexicon/PWG](https://github.com/sanskrit-lexicon/PWG/issues) and
   [sanskrit-lexicon/PWK](https://github.com/sanskrit-lexicon/PWK/issues), read in full
   via the GitHub API on 27-07-2026. Quotations in §5 are verbatim from that trail.
3. **The resolver wiring audit** —
   [`scan_target_audit.tsv`](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/data/pwg_scan_index_tracker/scan_target_audit.tsv),
   a dated static audit of the citation-resolver source against the live
   [sanskrit-lexicon-scans](https://github.com/sanskrit-lexicon-scans) GitHub
   organization.

### 2.2 Why citation mass, not page count

The campaign's natural size metric is pages indexed (28,963), but pages measure effort,
not payoff. A 159-page *Kumārasaṃbhava* and a 2,420-page *Taittirīyabrāhmaṇa* are not
equal work, and neither are they equal payoff: what matters to a dictionary user is how
much of the *citation apparatus* becomes resolvable. Coverage is therefore weighted by
each work's citation count — its **citation mass** — with an explicit caveat carried
through this paper: the tracking sheet's citation-count column has undocumented
provenance (§6.1) and is used only as a consistent internal ranking, never as a share of
the dictionary's total.

### 2.3 Cross-validation

Two independent checks tie the human work-log to the dictionary's own data. Every tracked
abbreviation was resolved against the PWG abbreviation bibliography
([`pwgbib_input.txt`](https://github.com/sanskrit-lexicon/PWG/blob/main/pwg_ls1/pwgauth/pwgbib_input.txt),
2,661 abbreviations): 62 rows match verbatim, 1 differs in case only, 19 match after
dropping the sheet's edition/volume qualifier, and **0 are unresolved** — every tracked
row names a work the dictionary's bibliography lists. The sheet's citation counts were
then compared against the full-dictionary `<ls>` extraction
([`sortedcrefs.txt`](https://github.com/sanskrit-lexicon/PWG/blob/main/pwg_ls/pwg_dhaval/abbrvwork/abbrvoutput/sortedcrefs.txt));
§6.1 reports why that comparison shows the two count different objects and cannot be
reconciled row by row.

### 2.4 Privacy

The snapshot's `Team` tab maps volunteers' real personal names to their GitHub handles.
The handles are public — they appear on every coordinating issue — but the name-to-handle
linkage is not, and the repository is. The name column was redacted at fetch time; every
credit and count below uses handles only.

## 3 · Results: what got built

### 3.1 Coverage

| metric | value |
|---|--:|
| works tracked | 82 |
| indexed (`done`) | 55 |
| in progress (`on-going`) | 3 |
| unclaimed (`to-do`) | 7 |
| cited page-wise (no per-entry index needed) | 14 |
| not required (indirect / alternate name) | 3 |
| volunteers | 8 |
| pages indexed | 28,963 |
| citation mass of tracked works | 268,425 |
| citation mass now indexed | 197,876 (73.7% of tracked) |

**73.7% is coverage of the tracked set, not of the dictionary.** The denominator is the
sheet's own citation-count column, which is not commensurable with the dictionary-wide
`<ls>` extraction (344,229 occurrences over 9,321 distinct cleaned citation strings;
§6.1). The long tail of thousands of once-cited works was never in scope.

Fourteen works classified `page-wise` and three `not required` are **not backlog**: they
are rulings that a per-entry index is the wrong instrument. The `page-wise` category was
defined in-thread by the campaign's philological adjudicator — works cited by page can be
linked by a constant offset from a single anchor, so "no full indexing (for the whole
book) is required" ([PWG#86](https://github.com/sanskrit-lexicon/PWG/issues/86)). A
coverage figure that counts those seventeen works as remaining misreads the campaign.

### 3.2 What remains

Seven works are unclaimed, carrying 10,998 citations (4.1% of tracked mass) across 6,033
pages. Ranked by citation payoff: Āśvalāyana-Śrautasūtra (1,835 citations),
Pañcaviṃśabrāhmaṇa (1,729), Chāndogyopaniṣad (1,696), (Mahā)Vyutpatti (1,670),
Āśvalāyana-Gṛhyasūtra (1,453), Kāṭhaka recension (1,316), Śiśupālavadha (1,299). Three
more are reserved and in progress (Dhātupāṭha, Śāṅkhāyana-Śrautasūtra,
Vājasaneyi-Prātiśākhya; 5,898 citations together).

**The backlog is Vedic.** Five of the seven unclaimed works belong to the saṃhitā /
brāhmaṇa / upaniṣad / śrauta- and gṛhya-sūtra / prātiśākhya group — long texts with dense
citation and awkward reference schemes. The kāvya and kośa material, which indexes fast,
is essentially finished. This is the expected shape of a volunteer campaign: work sorts
itself by tractability, and what remains at the end is precisely what no volunteer chose.

### 3.3 Throughput and velocity

Eight volunteers carried very unequal loads — the top three (13, 15 and 8 works;
61,664, 58,955 and 35,099 citation mass) account for 79% of indexed citation mass.
Velocity was front-loaded: of 56 monthly index-completion events, 42 fall in
February–April 2025, with a long tail of single completions through 2026-01. Publication
of the scan directory is a separate pipeline (upload, review, publish) with its own
queue; the median lag from index posted to scan public was **12 days**, range 1–177,
over 56 works.

### 3.4 The frontier: published, wired, and what the audit found

An index pays off only after three gates: the index is finished, the scan directory is
public, and the citation resolver emits a link to it. As of 27-07-2026 all 55 finished
works have public scan directories — 37 repositories under
[sanskrit-lexicon-scans](https://github.com/sanskrit-lexicon-scans) (one physical book
can serve several dictionary abbreviations), each serving a page-lookup GitHub Pages app,
together holding about 11.2 GB of page images. After defect fixes landed on 27-07-2026,
35 of the 37 directories are fully wired in the audited Python resolver, one is partially
wired (`pancar`: 2-parameter citations have no natural viewer target — a limitation the
canonical Dart resolver shares, so not treated as a live gap), and one is mis-keyed by
design (`amara_col`: unreachable from the bare `AK.` abbreviation, which the tracker
shows always denoting the paired `amara_dlc` edition).

The static audit that produced those numbers found five concrete defect classes worth
recording, because each is a *checkable claim about a specific line of resolver code or a
specific tracker cell*, not a heuristic guess:

- **A silent wrong answer.** A Ṛgveda-Prātiśākhya citation did not fail — it resolved to
  an Ṛgveda *hymn* anchor, a different text. A visible gap invites repair; a plausible
  wrong link does not. This was filed as an integrity defect, not backlog, and fixed.
- **Unreachable arities.** Taittirīyasaṃhitā and Taittirīyabrāhmaṇa citations resolved
  only at 4-parameter arity; the 3-parameter helper existed but its dispatch branch was
  unreachable (a prefix-map value never equalled the tested literal). Fixed.
- **Case-sensitivity at the seam.** The tracker spells one directory `rAjatar`; GitHub
  Pages paths are case-sensitive and the repository is `rajatar`, so a viewer link built
  from the tracker spelling 404s. A tracker defect, not a wiring gap.
- **Key mismatch by design** (`amara_col`, above) — confirmed intentional, but only after
  an audit pass that initially read it as a defect.
- **Shared-limitation partial wiring** (`pancar`, above).

### 3.5 The e-text dividend

Every finished index is a candidate for full-text extraction: the per-page index is
exactly the segmentation anchor a page-image OCR pass needs, and 11.2 GB of page images
are already public. The ranked candidate queue is committed
([`pwg_etext_candidate_queue.tsv`](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/data/pwg_scan_index_tracker/pwg_etext_candidate_queue.tsv));
its head is the kośa block (Amarakoṣa Deslongchamps ed., 16,151 citations; Hemacandra's
Abhidhānacintāmaṇi, 16,148; Medinīkoṣa, 12,990). A separate pilot on the
Abhidhānacintāmaṇi ruled OCR-from-scratch out — local Tesseract 5 `san` scored 17.8%
valid tokens against the work's own committed e-text while the Bayerische
Staatsbibliothek already publishes per-page hOCR of the same edition at 43.8% — so the
head of the queue is re-scoped to harvest-and-correct
([`reports/pwg_kosa_etext_pilot.md`](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/reports/pwg_kosa_etext_pilot.md)).

## 4 · Results: how the work was organized

The organizational findings are drawn from the forty-issue trail; the full reconstruction
with verbatim quotations is committed as
[`docs/PWG_SCAN_INDEX_CAMPAIGN_HISTORY_2025_2026.md`](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/docs/PWG_SCAN_INDEX_CAMPAIGN_HISTORY_2025_2026.md).

### 4.1 A four-beat ritual with no standing specification

Every work followed the same in-thread pipeline: **open** (templated issue with the
bibliography line), **claim and deliver** (reservation by announcement — "Will handle
Medinikosha." — with no assignee field or label), **check and clear** (a terse verdict
plus a repository name), **build and publish** (page images uploaded, apps installed,
links activated across five dictionaries). The index format itself — printed page → verse
range → PDF page — was never written down as a standing specification; it was stated as
a template, as a corrective rule issued after a violation, and as a volunteer's question
that the coordinators confirmed. The format survived by imitation, not documentation.

### 4.2 The review loop caught dictionary errors, not volunteer errors

The striking process finding: across the whole trail, only a handful of submitted indexes
needed revision — one full redo, one systematic off-by-40, one surplus column, one
omitted section. Most works passed with zero correction rounds. What the loop caught in
volume were **errors in the dictionaries themselves**, recorded in a consistent
`L-number : headword : old : new : reason` format distinguishing modern typos from print
changes in the source edition. Indexing every citation of a work against its printed
pages is, operationally, a proofreading pass over that work's citation apparatus — an
instrument nobody designed but the campaign's most transferable by-product.

### 4.3 The expensive failure was edition identity

The long threads are not the ones with sloppy indexes but the ones where the dictionary's
citations turned out to follow a different printed edition than the one indexed. The
Amarakoṣa issue ran two and a half years on this question alone. Related recurring costs:
the exact source PDF not being identified ("Where is the pdf from which the index was
created?" is asked repeatedly), and citations pointing at a commentary rather than the
main text — a problem discussed across three dictionary repositories and never solved.

### 4.4 Two single points of failure

Review concentrated in one person, and waits from submitted index to clearance ran 10–22
days and once three months — while the indexes themselves usually arrived within minutes
of the issue opening (the work was already done; the issue was the delivery vehicle).
Scan-repository construction likewise ran through one builder, whose availability pause
in July 2025 put the pipeline to a choice between in-house building and waiting. The
trail also records the disagreement about this: the adjudicator pressed repeatedly for
written procedure ("We have to use your time ONLY in essential matters"), the coordinator
answered candidly — "Working on the transition from 'do it all myself' -- Requires a
different mindset."

### 4.5 The extreme case

The Mahābhārata thread ([PWK#84](https://github.com/sanskrit-lexicon/PWK/issues/84)): 80
comments, opened February 2022, still open as of 27-07-2026 — even though all six volumes
are indexed, the 1.7 GB scan repository has been live since June 2025, and the tracker
marks the work `done`. The work is finished; the issue is not closed; both statements are
true. Closure lagged completion by up to ten months elsewhere in the trail too, and
go-live dates were never systematically recorded — the committed registry is the first
place the sheet's `Public Link` dates exist outside the sheet.

## 5 · Limitations

### 5.1 The citation counts have open provenance

Which extraction produced the sheet's citation-count column is not documented anywhere
reachable from the sheet, and it reproduces neither the bare-string counts of the
dictionary's own `<ls>` extraction nor a leading-abbreviation rollup of them: over the 56
rows where both numbers exist, the sheet/extraction ratio ranges from 1.2× to 433.0×
(median 2.09×) — the two count different objects (the extraction keys on cleaned citation
*strings*, the sheet on *books*). Until the provenance is established by the coordinator
who built the column, the counts support internal ranking only. Every percentage in this
paper therefore has the tracked set, not the dictionary, as its denominator, and the
73.7% headline cannot be restated as "73.7% of the PWG's citations now resolve".

### 5.2 Per-volume masses are floors

Fifteen tracked rows carry no citation count of their own (multi-volume works whose count
sits on the first volume), so per-volume mass figures are floors, not exact values.

### 5.3 One committed artifact disagrees with another — recorded, not averaged

The dashboard summary
([`observatory/site/src/data/pwg_scan_index_summary.json`](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/observatory/site/src/data/pwg_scan_index_summary.json))
records `scan_dirs_observed_wired: 32`, while the report's frontier table (§3.4 here)
counts 35 fully wired directories. Both artifacts are dated 27-07-2026. The explanation
is sequencing, not measurement: the resolver fixes that flipped `rvps`,
`taittiriyas` and `taittiriyabr` to fully wired landed the same day
([gasyoun/SanskritLexicography#840](https://github.com/gasyoun/SanskritLexicography/pull/840)),
and the report table was updated while the summary JSON was not regenerated. Per this
project's convention the disagreement is a finding to record, not a pair of numbers to
average; the post-fix count (35) is current, and the JSON should be regenerated at the
next dashboard refresh.

### 5.4 What the issue trail cannot show

The reconstruction in §4 is grounded in what forty issue threads literally say. Work
coordinated off-GitHub — the Russian volunteer group's internal channel, private handoffs
of column headers ("I gave those names to Olga") — enters the record only where the trail
mentions it. Status vocabulary beyond `page-wise` (`to do/open`, the two `NR` variants)
appears nowhere in the trail and is taken from the sheet without inventing definitions.
Attribution follows the sheet's `Reserved/Indexed by` column (first handle where a row
carries two), which slightly under-credits paired work.

### 5.5 What this paper does not claim

No novelty is claimed for crowd-sourced indexing as such, nor for linking dictionary
citations to facsimiles — both exist elsewhere in digital lexicography. The contribution
is descriptive and infrastructural: a measured, cross-validated account of one completed
campaign over a citation apparatus of unusual density, its committed registry, and the
process findings (§4.2, §4.3) that a successor campaign — for the PW, the MW, or the
remaining Vedic backlog — would otherwise rediscover at full price.

## 6 · Future work

Four items are open and committed as such: (i) the seven-work Vedic backlog (10,998
citations); (ii) the retroactive exhaustive cross-check — generating every dictionary
reference to every linked work and listing the misses — proposed after it drove the
Mahābhārata's 69 unmatched references to zero, but never run campaign-wide; (iii) the
commentary-citation problem, open across three dictionary repositories with no agreed
design; (iv) the e-text extraction queue (§3.5), where the indexes themselves become the
segmentation scaffold for OCR-correction work.

## Data availability

All data underlying every table and figure is committed in
[sanskrit-lexicon/csl-observatory](https://github.com/sanskrit-lexicon/csl-observatory):
the registry (
[`pwg_scan_index.tsv`](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/data/pwg_scan_index_tracker/pwg_scan_index.tsv) ·
[`pwg_scan_index.json`](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/data/pwg_scan_index_tracker/pwg_scan_index.json)),
the verbatim four-tab sheet snapshot
([`snapshot/`](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/data/pwg_scan_index_tracker/snapshot)),
the wiring audit
([`scan_target_audit.tsv`](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/data/pwg_scan_index_tracker/scan_target_audit.tsv)),
the e-text queue
([`pwg_etext_candidate_queue.tsv`](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/data/pwg_scan_index_tracker/pwg_etext_candidate_queue.tsv)),
and the derivation script
([`scripts/pwg_scan_index.py`](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/scripts/pwg_scan_index.py)),
which regenerates the report and summary from the snapshot deterministically. Data is
licensed CC BY 4.0 (see
[`DATA_LICENSE.md`](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/DATA_LICENSE.md)).
The campaign's primary record is public: forty issues in
[sanskrit-lexicon/PWG](https://github.com/sanskrit-lexicon/PWG/issues) and
[sanskrit-lexicon/PWK](https://github.com/sanskrit-lexicon/PWK/issues), and 37 scan
repositories under [sanskrit-lexicon-scans](https://github.com/sanskrit-lexicon-scans).

## Acknowledgements

The campaign's work is its volunteers': @angalinde, @AnnaRybakovaT, @Azanuka2412,
@grigoriyt1, @IrinaKonstant, @OFar0101, @ramray, @sofia28000 — with verification,
integration and app construction by @funderburkjim, philological adjudication by
@Andhrabharati, scan-repository construction by @grigoriyt1, independent implementation
by @drdhaval2785, and recruitment and record-keeping by @gasyoun.

_Dr. Mārcis Gasūns_
