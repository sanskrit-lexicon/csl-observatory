# PWG tracker `Citation count` — provenance recovered, and the denominator contract

_Created: 16-08-2026 · Last updated: 16-08-2026_

H1706 committed the PWG scan-index tracker as data and recorded its `Citation count` column as having unresolved provenance — usable for ranking, barred from any denominator. This pass resolves it against committed evidence and replaces the ban with a contract.

## 1 · The verdict

The column is the per-abbreviation total of [`pwgissues/issue74/lsextract_all.txt`](https://github.com/sanskrit-lexicon/PWG/blob/master/pwgissues/issue74/lsextract_all.txt) in sanskrit-lexicon/PWG, the count table dated **2024-09-11** with `ALL = 739,056`. Of the 67 tracked rows that carry a value, **66 match that table exactly**, 1 is a near-miss, 0 are unresolved. The remaining 15 rows carry no value of their own because the sheet writes a family's count once and `- - -` on its sibling volumes.

The table is committed here as the input of record, so this claim is checkable offline: [`ls_counts/pwg_ls_counts_2024-09-11.tsv`](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/data/pwg_scan_index_tracker/ls_counts/pwg_ls_counts_2024-09-11.tsv).

## 2 · What the number counts

Per [`lsextract_all.py`](https://github.com/sanskrit-lexicon/PWG/blob/master/pwgissues/issue94/lsextract_all.py), for every `<ls …>…</ls>` element in the PWG digitization:

1. an `n="…"` attribute value, where present, is prepended to the element text;
2. text beginning with a digit counts as `NUMBER`;
3. otherwise the element goes to the **longest bibliography abbreviation in `pwgbib_input.txt` that is a prefix of that text** — `MED. k. 12` and `MED. kh.` both count towards `MED.`;
4. text with no such prefix counts as `UNKNOWN`.

Every element lands in exactly one bucket, so the buckets partition the dictionary and `ALL` is a real denominator. Three consequences follow, and they are the whole of the contract:

- The number is a **work family**, not a citation string. That is why H1706's comparison against the cleaned-string extraction diverged by 1.2×–433×: `MED.` has 30 bare-string occurrences and 12,990 family occurrences, and both are correct counts of different objects.
- Sibling rows of one family (`AK. Deslongchamps ed.` / `AK. Colebrooke ed.`, the six `MBh. (Bomb.)` volumes) share **one** total. Summing them double-counts, which is why the sheet writes the value once per family and the contract check below enforces exactly that.
- A percentage is only meaningful against the `ALL` of the **same snapshot**. Mixing the 2024-09-11 column with a 2026 denominator understates by the drift measured in §5.

## 3 · Per-row provenance

Full dataset: [`pwg_citation_count_provenance.tsv`](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/data/pwg_scan_index_tracker/pwg_citation_count_provenance.tsv) (82 rows). Summary:

| provenance | rows | meaning |
|---|--:|---|
| `exact` | 66 | the tracker value is the source table's value for that abbreviation, digit for digit |
| `near-miss` | 1 | within 100 of the source value and matched by no other snapshot; a transcription slip |
| `unmatched` | 0 | value present, source value not reproduced |
| `inherited-family` | 15 | no value in the sheet; the family's count sits on another row |

The rows that are not exact:

| LS code | tracker | source table | delta | reading |
|---|--:|--:|--:|---|
| `NAIGH.` | 1,477 | 1,417 | 60 | single-digit transcription slip; no committed snapshot of the count carries the tracker's value |

## 4 · The denominator contract

`python scripts/pwg_citation_count_provenance.py --check` is the gate, and it fails on any of:

| # | rejected | why |
|---|---|---|
| 1 | a tracker value whose provenance is unresolved | an unproven number must not reach a report, let alone a denominator |
| 2 | a row whose abbreviation joins case-insensitively onto a citation-bearing case-variant group | the PWG bibliography distinguishes `Ś.` from `ś.`; a case-folded join silently picks one of two real works (15 such groups exist) |
| 3 | two rows of one bibliography family both carrying a value | the field is a family rollup; the pair double-counts |
| 4 | a row asserting a count but exposing no safe value | the two columns have drifted apart and downstream would read the wrong one |
| 5 | the safe counts summing above their own `ALL` | proof that 3 has already happened |

The field a consumer may divide by is **`citation_count_safe`**, never `tracker_value`. It carries the source table's own number, blank wherever a row's provenance is unresolved, so an unproven value has no arithmetic path into a coverage percentage.

Today the safe counts sum to **268,365** against a denominator of **739,056** — 36.3% of the dictionary's `<ls>` apparatus sits on a tracked source.

## 5 · The canonical field, and drift

The tracker column is frozen evidence from 2024-09-11. For anything computed today, `canonical_value` in the dataset is regenerated from current dictionary data by [`scripts/pwg_ls_counts.py --recount`](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/scripts/pwg_ls_counts.py) into [`ls_counts/pwg_ls_counts_current.tsv`](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/data/pwg_scan_index_tracker/ls_counts/pwg_ls_counts_current.tsv), `ALL = 799,500` as of 2026-08-16. That regeneration is a port of the upstream generator, and `--verify-port` runs both on identical inputs and requires byte-identical output.

81 of 82 rows moved between the two snapshots — the ls-tag correction campaigns are visible in the counts. Largest movements:

| LS code | 2024-09-11 | current | drift |
|---|--:|--:|--:|
| `SUŚR.` | 12,442 | 20,305 | +7,863 |
| `VARĀH. BṚH. S.` | 9,174 | 14,312 | +5,138 |
| `RĀJA-TAR.` | 7,784 | 10,308 | +2,524 |
| `Spr. vol.1 (1st ed.)` | 10,494 | 12,850 | +2,356 |
| `Spr. vol.2 (1st ed.)` | 10,494 | 12,850 | +2,356 |
| `Spr. vol.3 (1st ed.)` | 10,494 | 12,850 | +2,356 |
| `H. an.` | 9,781 | 11,856 | +2,075 |
| `KĀTY. ŚR.` | 6,734 | 8,667 | +1,933 |
| `an.` | 1,797 | 1 | -1,796 |
| `R. (Bomb.)` | 37,762 | 39,395 | +1,633 |

## 6 · Hypotheses tested

Recorded so the next session does not re-run them.

| # | hypothesis | verdict |
|---|---|---|
| 1 | bare cleaned-citation-string counts (`sortedcrefs.txt`) | rejected — H1706; 1.2×–433× spread |
| 2 | leading-abbreviation rollup of those same cleaned strings | rejected — H1706 |
| 3 | rollup of the `pwgls.txt` abbreviation database by bibliography code | rejected — reproduces the ordering but not one value; ratios 1.03×–650× |
| 4 | one of the dated `lsextract_pwg_*.txt` tables in `pwg_ls2/` (2022–2023 runs) | rejected — 2 of 67 rows match, by coincidence of small numbers |
| 5 | the `lsextract_all.txt` table committed under `pwgissues/issue74/`, 2024-09-11 | **confirmed** — 66/67 exact |

Hypothesis 5 was reached by comparing the tracker column against every count table in the PWG repository mechanically, rather than by reasoning about which extraction *ought* to have been used — the reasoning path is what failed in H1706.

## 7 · What this does not settle

- **Which human ran that extraction, and when they pasted it into the sheet**, is still unrecorded. The provenance established here is of the *number*, from committed artefacts; it does not need the coordinator's testimony, and it does not replace it.
- **`NAIGH.`** stays a near-miss. The count reads 1,378 (2023-01-13), 1,417 (2024-09-11) and 1,456 (2026-06-24) across committed snapshots; the sheet's 1,477 matches none of them.
- **The 2024-09-11 pwg.txt itself** is not re-derivable here: the local `csl-orig` checkout is shallow and does not reach that date. The recovery rests on the committed *output* table, not on re-running the generator against era-matched input.

_Dr. Mārcis Gasūns_
