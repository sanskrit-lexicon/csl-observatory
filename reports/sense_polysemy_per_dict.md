# Sense / polysemy distribution per dict (H817 WS1.2, L1 census row)

_Created: 13-07-2026 · Last updated: 13-07-2026_

Written by Sonnet 5 (`claude-sonnet-5`), H817, to close the L1 "sense-count / polysemy
distribution per dict" row in
[ROADMAP_STATISTICS_ORG_CENSUS_2026_2027.md](https://github.com/gasyoun/SanskritLexicography/blob/master/ROADMAP_STATISTICS_ORG_CENSUS_2026_2027.md).

## 0 · Prior-art check — this was already computed, just not registered

Before building anything, this session verified whether sense-counting per dict already
existed. It does: [csl-atlas `docs/articles/paper_sense_inheritance.md`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/articles/paper_sense_inheritance.md)
(the A02 paper, "Condensation, Not Inflation: Sense Inheritance in the Sanskrit Dictionary
Family, 1822–1957") computes a calibrated senses-per-entry figure for **11 of the 44**
CDSL dictionaries, backed by committed data
([`csl-atlas/data/lexico/r2_h1.json`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/lexico/r2_h1.json)).
This report does not recompute that work — it mirrors the per-dict table (with
attribution) into the observatory's census register so it appears alongside the other
WS1.2 rows, and documents the scope boundary honestly rather than fabricating coverage
for the other 33 dicts.

[`SanskritLexicography/FINDINGS.md` §27](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md#27-sense-granularity-is-a-family-trait-not-a-diachronic-trend)
already carries the headline result and an explicit warning this report repeats: **never
read sense counts as lexicographic "progress"** — granularity is a family/school trait
(Benfey 2.42 senses/entry vs the indigenous lexica ≈1.00 by construction), not a
diachronic trend (r = 0.036 against publication year, 1822–1957).

## 1 · The 11-dict table (mirrored from `r2_h1.json`)

| Dict | Year | Family | Senses/entry | Entries |
|---|--:|---|--:|--:|
| skd | 1822 | indigenous | 1.002 | 42,531 |
| wil | 1832 | Wilson | 1.706 | 44,577 |
| pwg | 1855 | Petersburg | 1.129 | 123,366 |
| ben | 1866 | Benfey | 2.42 | 17,310 |
| mw72 | 1872 | Monier-Williams | 2.852 | 55,390 |
| vcp | 1873 | indigenous | 1.0 | 50,135 |
| ap90 | 1890 | Apte | 2.517 | 34,882 |
| cae | 1891 | Cappeller | 1.355 | 40,069 |
| mw | 1899 | Monier-Williams | 1.15 | 286,525 |
| sch | 1928 | Petersburg | 1.139 | 29,125 |
| ap | 1957 | Apte | 1.724 | 90,843 |

Full machine-readable copy: [`data/sense_polysemy_per_dict.tsv`](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/data/sense_polysemy_per_dict.tsv).

**Method (not re-derived here — see the paper §3.1 for the full account).** No single
splitting rule fits all 44 dicts; the csl-atlas parser uses four convention-specific
families: explicit Western sense-markers (Apte, Benfey, Wilson numbered/bulleted senses;
Petersburg structural `<div>`); lumped-gloss dicts with **no** sense marking at all
(Monier-Williams both editions, Schmidt, Cappeller), where semicolon-delimited
meaning-clauses (citations stripped) serve as a **calibrated proxy, flagged as such**;
indigenous prose dicts (SKD, VCP), split on the *iti*-quotative closing particle; and
Apte's reverse English→Sanskrit volume, handled separately by rank-band.

## 2 · Why the other 33 dicts are NOT in this table — verified, not assumed

This session verified directly (rather than assuming the `<L>` record-ID field could be
repurposed as a cheap sense-count proxy for the remaining dicts) that:

- **`<L>` is a Cologne database record ID, not a sense index.** Documented per-dict in
  every `<dict>-meta2.txt` (e.g.
  [`csl-orig/v02/mw/mw-meta2.txt`](https://github.com/sanskrit-lexicon/csl-orig/blob/main/v02/mw/mw-meta2.txt)).
  Decimal-suffixed `<L>` IDs (`4.1`, `4.2` …) are NOT an ordered per-headword sense count:
  in MW, seven different decimal `<L>` records (`4.1`–`4.7`) share one `<e>1A` subentry
  code, and large/non-sequential suffixes (`19869.805`) look like synthetic
  etymology/parenthetical-child records, not senses. **This is now a documented dead end**
  — recorded here so a future session does not re-attempt the `<L>`-decimal shortcut.
- **Most dicts mark no senses structurally at all.** `SanskritLexicography/FINDINGS.md` §22
  reports MW carries **zero** `<div n="m">` sense markers across 286,526 `<L>` records —
  senses are separated only by `¦` inside the gloss body. This is exactly why the A02
  paper had to build the four-family calibrated-proxy splitter above instead of reading a
  structural tag.
- **The `<h>`/homonym field is not uniform either.** Format and even presence vary per
  dict (digit `<h>` in MW/PW/PWG/BHS/CAE/CCS/STC; roman numerals in GST/PE/PUI; the field
  is undocumented or zero-instance in ~15 of the 44 `*-meta2.txt` specs) — it distinguishes
  homonymous headwords, not sense count, and can't be used as a uniform 44-dict proxy
  either.

**Verdict:** extending this row to the remaining 33 dicts is real, dict-specific parser
work (one more convention-family splitter per dict or per small dict-cluster, each
needing its own calibration check like the A02 paper's reviewed checkpoint) — not a
mechanical census pass. Marking this row done for the **11-dict general-lexica scope**
(where the work already exists and is paper-published) is the honest state; the L1
Part-0 row is flipped to **◐ partial (11/44)**, not ✅, to keep that boundary visible.

## 3 · Registration

- [`FEATURES_INDEX.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/FEATURES_INDEX.md) —
  cross-referenced under the data-assets section (this report + the A02 paper).
- [`ROADMAP_STATISTICS_ORG_CENSUS_2026_2027.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/ROADMAP_STATISTICS_ORG_CENSUS_2026_2027.md)
  Part 0, L1 row "Sense-count / polysemy distribution per dict" — flipped `○` → `◐ partial (11/44 general lexica; A02 paper) — see csl-observatory sense_polysemy_per_dict report for the scope boundary`.

_Dr. Mārcis Gasūns_
