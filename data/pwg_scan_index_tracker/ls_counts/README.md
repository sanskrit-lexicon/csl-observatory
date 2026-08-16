# ls_counts — PWG `<ls>` citation counts per bibliography abbreviation

_Created: 16-08-2026 · Last updated: 16-08-2026_

Two count tables over the PWG dictionary's literary-source apparatus. Both answer one
question — *how many `<ls>` citations does this work carry?* — and they are kept apart
because they answer it about two different days.

| File | What it is | Use it for |
|---|---|---|
| [`pwg_ls_counts_2024-09-11.tsv`](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/data/pwg_scan_index_tracker/ls_counts/pwg_ls_counts_2024-09-11.tsv) | The table the volunteer tracker's `Citation count` column was read off. Frozen evidence. | Explaining, auditing, or reproducing a tracker number. |
| [`pwg_ls_counts_current.tsv`](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/data/pwg_scan_index_tracker/ls_counts/pwg_ls_counts_current.tsv) | The same count regenerated against current dictionary data. | Any citation mass, share, or ranking computed today. |

Each has a sibling `.meta.json` with input hashes, source commits, and the `ALL` /
`NUMBER` / `UNKNOWN` totals.

## The count, precisely

For every `<ls …>…</ls>` element in `csl-orig/v02/pwg/pwg.txt`:

1. an `n="…"` attribute value, where present, is prepended to the element text;
2. text beginning with a digit goes to `NUMBER`;
3. otherwise the element goes to the **longest abbreviation in `pwgbib_input.txt` that is
   a prefix of that text** — `MED. k. 12` and `MED. kh.` both count towards `MED.`;
4. text with no such prefix goes to `UNKNOWN`.

Every element lands in exactly one bucket, so `ALL` is the one legitimate
dictionary-wide denominator for these numbers, and only against its own snapshot.

## Three things that will bite you

1. **The number is a work family, not a citation string.** The cleaned-string extraction
   in [`sortedcrefs.txt`](https://github.com/sanskrit-lexicon/PWG/blob/master/pwg_ls/pwg_dhaval/abbrvwork/abbrvoutput/sortedcrefs.txt)
   counts a different object and disagrees by 1.2×–433×. Neither is wrong; they are not
   comparable.
2. **Siblings of a family share one total.** `AK. Deslongchamps ed.` and
   `AK. Colebrooke ed.` both read `AK.`'s number. Summing rows without folding by family
   double-counts.
3. **Case is meaningful.** `Ś.` and `ś.` are different works, and both are cited. A
   case-insensitive lookup is a silent wrong answer for the groups the checker lists.

## Regenerating

```sh
python scripts/pwg_ls_counts.py --verify-port   # port == upstream PWG generator
python scripts/pwg_ls_counts.py --recount       # rewrite pwg_ls_counts_current.tsv
python scripts/pwg_ls_counts.py --check         # offline self-consistency
```

`--recount` needs sibling checkouts of
[sanskrit-lexicon/PWG](https://github.com/sanskrit-lexicon/PWG) and
[sanskrit-lexicon/csl-orig](https://github.com/sanskrit-lexicon/csl-orig); everything
else is offline over committed data.

**Never regenerate `pwg_ls_counts_2024-09-11.tsv` against newer dictionary data.** It is
dated evidence for a column a human wrote in a spreadsheet, not a derivation. Between the
two snapshots `an.` falls from 1,797 to 1 while `H. an.` rises by 2,075 — a re-tagging, not
a recount — so a silent refresh would rewrite the campaign's own history.

## Provenance

Ported from `lsextract_all.py` in
[sanskrit-lexicon/PWG](https://github.com/sanskrit-lexicon/PWG/blob/master/pwgissues/issue94/lsextract_all.py)
(E. Fitzgerald), which is also the generator of the 2024-09-11 table. The port is held to
byte-identical output by `--verify-port`. Analysis:
[`reports/pwg_citation_count_provenance.md`](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/reports/pwg_citation_count_provenance.md)
(H2874).

_Dr. Mārcis Gasūns_
