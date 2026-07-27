# How the PWG scan indexes were made — a crowd-sourced page-indexing campaign, 2025–2026

_Created: 27-07-2026 · Last updated: 27-07-2026_

Between January 2025 and July 2026, eight volunteers page-indexed fifty-five printed
editions cited by the Böhtlingk-Roth *Sanskrit-Wörterbuch* (PWG) — about 29,000 pages —
so that a `<ls>` citation in the dictionary could be turned into a link to the exact page
of the exact edition it cites. The work was coordinated entirely in public GitHub issues.

This document reconstructs the workflow from that issue trail: forty issues across
[sanskrit-lexicon/PWG](https://github.com/sanskrit-lexicon/PWG/issues) and
[sanskrit-lexicon/PWK](https://github.com/sanskrit-lexicon/PWK/issues), read in full.
Everything below is grounded in what those threads literally say. Quotations are verbatim;
where the record is thin or contradictory, this document says so rather than smoothing it
over. The measured output of the campaign is
[`reports/pwg_scan_index.md`](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/reports/pwg_scan_index.md);
the registry is
[`data/pwg_scan_index_tracker/`](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/data/pwg_scan_index_tracker).

## 1 · Who did what

The division of labour is never written down as a rule anywhere in the trail. It is
simply enacted, identically, across all forty issues.

| Role | Who | What the record shows them doing |
|---|---|---|
| Verification, integration, closure | [@funderburkjim](https://github.com/funderburkjim) | Checks every submitted index against its PDF and against the dictionary text; assigns the scan-repository name; builds and installs the lookup apps; edits the dictionary markup; activates links across `pwg`, `pw`, `pwkvn`, `sch`, `mw`; commits the working files; closes the issue. |
| Philological adjudication | [@Andhrabharati](https://github.com/Andhrabharati) | Identifies *which printed edition* a citation series actually follows; decodes each work's reference mode; supplies PDFs and missing scan pages; corrects print errors — and corrects corrections. Makes cost-benefit calls on whether a work is worth indexing at all. |
| Scan-repository construction | [@grigoriyt1](https://github.com/grigoriyt1) | Splits the PDF into per-page files, creates and populates the `sanskrit-lexicon-scans` repository, replies `repo is ready: <url>`. Also relays the Russian volunteer group, and indexed several works of their own. |
| Recruitment and record-keeping | [@gasyoun](https://github.com/gasyoun) | Opens issues, recruits and briefs the volunteers, chases stalled threads, keeps the status sheet. |
| Independent implementer | [@drdhaval2785](https://github.com/drdhaval2785) | Ran the full integration on several works and created a repository directly. |
| Indexing | [@angalinde](https://github.com/angalinde), [@Azanuka2412](https://github.com/Azanuka2412), [@grigoriyt1](https://github.com/grigoriyt1), [@IrinaKonstant](https://github.com/IrinaKonstant), [@OFar0101](https://github.com/OFar0101), [@ramray](https://github.com/ramray), [@sofia28000](https://github.com/sofia28000), [@AnnaRybakovaT](https://github.com/AnnaRybakovaT) | Produce the per-page indexes. |

**One correction to how this campaign is usually described.** It is natural to call the
effort "Andhrabharati-guided", and that role is genuinely load-bearing — without the
edition identifications the indexes would have targeted the wrong books, and several
did before those interventions. But the coordinating and implementing role in the issue
trail is @funderburkjim's, in every one of the forty issues: setting the format, checking
the work, naming the repositories, building the apps, closing. The two roles are distinct
and both are essential; the record does not support collapsing them into one.

## 2 · What an index actually is

A plain tab-separated table, one row per printed page:

```
page	tantram	fromv	tov	ipage
17	0	1	4	3
18	0	5	10	4
19	0	11	11	5
20	1	1	8a	6
21	1	8b	16	7
```

That template is from [PWG#86](https://github.com/sanskrit-lexicon/PWG/issues/86), posted
with three rules attached:

> * tantram = 0 for the 'prastAva'
> * Use the 'a/b' marking for verses (shlokas) spanning 2 pages
> * document skew pages, if any
> * document pages with NO verses (if any)

The columns vary by work — the division level is whatever the text uses (`tantram`,
`sarga`, `pañcika, adhyāya, kaṇḍikā`, `kāṇḍa`), and multi-volume works prefix a volume
column — but the shape is invariant: **printed page → verse range → `ipage`**, where
`ipage` is the page's position inside the PDF. That last distinction carries the whole
workflow, and mismatches between the printed page and the PDF page are the single
commonest mechanical defect.

**There was never a standing specification.** The format is stated three different ways
across the trail — as a template with sample rows, as a corrective rule issued *after* a
violation ("The format of the index files should be 'tab-separated values'. For
indische_spr, each line should have exactly 5 values with a tab-character between each
value.", [PWG#87](https://github.com/sanskrit-lexicon/PWG/issues/87)), and as a question
from the volunteer that the coordinators confirm ("the structure looks like: volume -
page - from. v. - to v. - ipage, right?", the same issue). In one late case the column
headers were supplied privately and only surfaced in the thread afterwards: "I gave those
names to Olga" ([PWG#134](https://github.com/sanskrit-lexicon/PWG/issues/134)).

## 3 · The pipeline — a four-beat ritual

Repeated near-verbatim in every issue:

1. **Open.** A templated body: the PWG bibliography line (id, abbreviation, expanded
   German title) in a code fence, then "We begin preparing a link target (ultimately as a
   new repository hosted in the sanskrit-lexicon-scans Github organization)". The 2025
   cohort adds a recruitment sentence — "we now want to train a group of Russian
   volunteers, students of mine, who would drastically improve the number of indexes
   prepared for linking purposes."
2. **Claim and deliver.** Reservation is by announcement, not assignment: "I will handle
   Abhidhānacintāmaṇi of Hemacandra.", "Will handle Medinikosha.", "I took up this work."
   There is no assignee field and no label. @funderburkjim made the convention explicit:
   "Whoever accepts the indexing task, please make comment here so we'll know index is
   being worked on." The volunteer then attaches the index (`.xlsx` with a `.docx` notes
   file, or `.txt` with a `.txt` comments file) and a link to the PDF.
3. **Check and clear.** A short verdict, then the repository name in backticks: "Index is
   good to go.", "Index is found OK.", "not even one tiny problem noticed. Excellent!",
   followed by "Ready for … repo in sanskrit-lexicon-scans. Use repo name `X`". Rejections
   are equally terse and always cite a concrete counter-example from the PDF.
4. **Build and publish.** @grigoriyt1 creates the repository, uploads the page images, and
   replies "repo is ready: <url>". @funderburkjim installs the apps, edits `basicadjust.php`
   in `csl-websanlexicon`, copies to `csl-apidev`, regenerates the displays for each
   dictionary, updates the Cologne server, and closes.

The public artifact is a GitHub Pages app whose URL encodes the citation directly —
`https://sanskrit-lexicon-scans.github.io/<repo>/app1/?<params>`. A second app,
`app0`/`app2`, takes a raw page number instead.

Two conventions are worth recording because they are decided in-thread and easy to lose:
**one physical book gets one repository even when it serves several dictionary
abbreviations** (`medini` carries Medinīkoṣa, Trikāṇḍaśeṣa and Hārāvalī; `bchrest1`
carries four separate PWG abbreviations, one app each), and **page-image filenames are
specified before the build** for multi-volume works, precisely to avoid page-number
collisions (`ram-VNNN.pdf`, `tai1-NNNN`).

## 4 · How the checking was done

The method is sampling-based and was stated repeatedly but never centralised:

> generate 10 or so random selections of the link in pwg.txt and be sure that the index
> points to the right place in the pdf

with a stated pass criterion — "The linking between mw ref and pdf text is considered
successful exactly when the word W (in some form) is found `in` the pdf text" — and, in
[PWG#87](https://github.com/sanskrit-lexicon/PWG/issues/87), a documented and committed
instance: ten random verses per volume, each checked against the PDF page the index gives,
each additionally cross-checked by taking a word from `pwg.txt` that cites that verse and
confirming it appears on that page. The procedure was written up as
`readme_checkindex_vol1.txt`.

Later a stronger, exhaustive check appeared: generate every dictionary reference to the
work, look each one up in the index, and list the misses — the "**pagerec not found**"
report. Its first real use was the Mahābhārata
([PWK#84](https://github.com/sanskrit-lexicon/PWK/issues/84)), where it surfaced 69
unmatched references and drove them to zero. @Andhrabharati then proposed applying it
retroactively to every work already linked. **Every issue has a committed working
directory** — `pwgissues/issue<N>/` in the PWG repository — holding the accepted index,
the diagnostic files (`check_sample.txt`, `change_notes.txt`, `check_<kosha>_ALL.txt`) and
the dictionary change files.

## 5 · What the review actually caught

The striking finding: **the review loop mostly did not catch volunteer errors.** Across
the whole trail only a handful of submitted indexes needed revision — one full redo
(volume 2 of the *Indische Sprüche*, whose verse numbers were incompatible with the PDF),
one systematic `ipage` off-by-40 across a run of lines, one surplus column, one omitted
section. Most works passed with zero correction rounds.

What the loop caught instead, in volume, were **errors in the dictionaries themselves** —
recorded in a consistent line format `L-number : headword : old : new : reason`, with the
reason token distinguishing a modern `typo` from a `printchange` in the source edition:

```
4422 : kARqavastra : CAURAP. (A.) 31 : CAURAP. (A.) 51 : pwkvn typo
189174 : vastuka : Mālav. i, 6/7 : Mālav. i, 5/6  printchange
97002 : SaMsa :  AIT. BR. 2,2,4 :  AIT. BR. 2,4 :  PRINT CHANGE
```

Corrections were themselves reviewable and were sometimes reverted — "Here are some
corrections to 'corrections' in PWG--", and, on one of their own, "My bad here! It
should've been 197, and not 196 at these citations." One proposed change was declined
outright and the disagreement left open at close.

Three further defect classes recur:

- **Edition identity.** The expensive failure, every time. The long threads are not the
  ones with sloppy indexes but the ones where the dictionary's citations turned out to
  follow a different printed edition than the one indexed. The Amarakośa issue ran two
  and a half years on this question alone.
- **The PDF was not identified.** An index cannot be reviewed without the exact scan it
  was built from — "Where is the pdf from which the index was created?" is asked
  repeatedly, once twice in the same thread. In one case three near-identical scans were
  circulating and only the third matched.
- **Commentary citations.** A citation pointing at a commentary rather than the main text
  produces a "NOT FOUND" at the generated link. This appears in at least four issues and
  was never solved: "This has been discussed at quite a few issues in MW as well as
  PWG/pwk repos."

Where a clean index still would not match the dictionary, the fallbacks were explicit:
restrict the link range, ship a written caveat in the app's `info.html`, or deactivate the
links (205 Pañcatantra references in MW were deactivated this way).

## 6 · The status vocabulary — and the limits of the evidence

The tracker's `Index Status` column uses `done`, `on-going`, `to do/open`, `page-wise`
and `NR`. Only one of these is defined anywhere in the issue trail, and it is the one that
matters most for reading the coverage numbers correctly.

In [PWG#86](https://github.com/sanskrit-lexicon/PWG/issues/86), @funderburkjim found a
work "classified as 'Not required'" in the team's sheet and asked whether that meant no
link target. @Andhrabharati answered that the *target* is required but an *index file* is
not, because such works are cited by page:

> if you are going to link the pages by offset manner (offset value = pdf page no. of the
> first i.page), no full indexing (for the whole book) is required. A single liner stating
> on which pdf page the first print page starts should be sufficient.

and added, "there are sizeable no. of books coming in this category, i.e. with page-wise
referencing." So `page-wise` is a ruling that per-entry indexing is the wrong instrument —
**not backlog**. Any coverage figure that counts those fourteen works as "remaining"
misreads the campaign.

`on-going` appears once, meaning claimed and under way. For `to do/open` and the two `NR`
variants, a literal search across all forty issues finds nothing: the vocabulary lives in
the sheet, not in the trail. This document does not invent definitions for them.

## 7 · Where the process was thin

Recorded because a future campaign will hit the same walls, not as criticism of anyone.

- **One reviewer was the throughput limit.** Not indexing. Waits from submitted index to
  clearance ran 10, 20, 22 days and once three months, prompting "Why not linkup this
  'single pending' indexed work". Indexes usually arrived within minutes of the issue
  being opened — the work was already done; the issue was the delivery vehicle.
- **The builder role was a single point of failure too.** In July 2025 the trail records
  "this is the last repo to be made by Grigory for now", as @grigoriyt1 took a break for
  a final graduation year, with the choice put to the reviewer: populate the scan
  repositories in-house, or pause.
- **The documentation gap was known and argued about.** @Andhrabharati pressed repeatedly
  for a written procedure instead of the coordinator doing the work in-house — "I request
  you to prepare a step-by-step process … so that it can be passed on to the team", "We
  have to use your time ONLY in essential matters" — and, when it was done in-house
  anyway, "So, you are not helping me make people help you, but do it all yourself; is
  it?" The answer was candid: "Working on the transition from 'do it all myself' --
  Requires a different mindset." What came out of it are two written artefacts:
  `sanskrit-lexicon-scans/linktarget_howto` issue 1, and `pwgissues/issue98/readme_linktarget.txt`.
  On per-repository documentation of what a citation's parameters mean, the assessment
  was "This kind of documentation has been done by me for only a few of the link target
  repos."
- **Closure lags completion by up to ten months.** Several issues were technically
  finished in mid-2025 and closed in June 2026, each prompted by @Andhrabharati asking
  whether it was closable. One still carries a `wontfix` label from an early decision,
  although the app shipped.
- **Go-live was never systematically recorded.** @gasyoun asked directly — "should we keep
  a separate index on what link started working on what day with URLs?" — and got no
  answer. The sheet's `Public Link` column is the closest thing that exists, and this
  registry is the first time it has been committed anywhere.

## 8 · The Mahābhārata, as the extreme case

[PWK#84](https://github.com/sanskrit-lexicon/PWK/issues/84) is worth reading on its own:
80 comments, opened February 2022, **still open** as of 27-07-2026 even though the tracker
marks all six volumes `done` and the scan repository (`mbhbomb`, 1.7 GB — the largest in
the org) has been live since June 2025. Three years passed between @Andhrabharati
confirming ownership of the volumes and the first index file appearing, filled with attempts
to hand the task over: "I had done 4-5 already, but Jim is not anywhere around to take
them and do the linking."

Whether it was worth doing at all was contested for over a year — "is it worth putting
effort to link these to pdf pages (the pages count about 4500!)?" against the observation
that 4,000-plus PWK citations use precisely that edition.

The six volumes were split without any plan being announced; the split is visible only in
the upload order, and the tracker's attribution matches the issue trail exactly —
volume 1 @ramray, volumes 2 and 3 by Roman (posted on their behalf by @grigoriyt1),
volumes 4 and 5 @Azanuka2412, volume 6 @angalinde. The last comment is a note that the
builder is busy until July; the requested final verification never followed. The work is
finished. The issue is not closed. Both statements are true, and the registry records the
first while this document records the second.

## 9 · The campaign in numbers

| | |
|---|--:|
| Works tracked | 82 |
| Indexed (`done`) | 55 |
| Pages indexed | 28,963 |
| Volunteers | 8 |
| Coordinating GitHub issues read for this history | 40 |
| Scan repositories built | 37 |
| Page images published | ~11.2 GB |
| Median lag, index posted → scan public | 12 days |
| First index finished | 30-01-2025 |
| Most recent scan published | 05-07-2026 |

Sources for every figure:
[`reports/pwg_scan_index.md`](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/reports/pwg_scan_index.md)
and
[`data/pwg_scan_index_tracker/`](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/data/pwg_scan_index_tracker).

## 10 · What is still open

- **Seven works unclaimed**, five of them Vedic, carrying 10,998 citations across 6,033
  pages. The kāvya and kośa material — which indexes quickly — is finished; what remains
  is long texts with awkward reference schemes.
- **One index is done but genuinely unwired**: the Ṛgveda-Prātiśākhya (`rvps`). Worse than
  unwired — a Prātiśākhya reference currently resolves to an Ṛgveda *hymn* anchor, a
  different text. Detail in
  [`reports/pwg_scan_index.md`](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/reports/pwg_scan_index.md) §7.
- **The commentary-citation problem** has been open across PWG, PWK and MW for years and
  has no agreed design.
- **The retroactive `pagerec not found` sweep** that @Andhrabharati proposed after the
  Mahābhārata — running the exhaustive cross-check against every work already linked —
  does not appear to have been carried out.
- **Every finished index is a full-text extraction candidate.** The per-page index is
  exactly the segmentation anchor a page-image OCR pass needs, and 11.2 GB of page images
  are already public. The ranked queue is
  [`pwg_etext_candidate_queue.tsv`](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/data/pwg_scan_index_tracker/pwg_etext_candidate_queue.tsv).

## Sources

Forty issues, read in full via the GitHub API on 27-07-2026:
[PWG](https://github.com/sanskrit-lexicon/PWG/issues) #62, #75, #86, #87, #92, #93, #95,
#96, #97, #98, #100, #101, #104, #105, #109, #110, #121, #122, #123, #124, #125, #129,
#134, #135, #136, #137, #139, #143, #144, #146, #147, #148, #149, #152, #153, #157, #159,
#167, #173; [PWK](https://github.com/sanskrit-lexicon/PWK/issues) #84. Plus the
`pwgissues/issue<N>/` working directories in the
[PWG repository](https://github.com/sanskrit-lexicon/PWG) and the
[sanskrit-lexicon-scans](https://github.com/sanskrit-lexicon-scans) organization
(101 repositories, 37 of them built by this campaign).

_Dr. Mārcis Gasūns_
