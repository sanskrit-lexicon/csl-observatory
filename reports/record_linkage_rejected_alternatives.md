# Record linkage for the OBS-T estimator: the alternatives that were rejected

_Created: 27-07-2026 · Last updated: 27-07-2026_

Companion to [`reports/error_recapture.md`](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/reports/error_recapture.md)
and [`scripts/headword_linkage.py`](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/scripts/headword_linkage.py)
(Workstream G3, paper A48). The shipped linkage ladder records why `form_key` was
adopted. This file records the keys that were tried and **rejected**, so the next
session does not re-derive them — including two that were measured only on a parallel
implementation of H1477 that never merged.

Handoff H1477 was implemented twice, concurrently and independently: the version that
shipped as [PR #120](https://github.com/sanskrit-lexicon/csl-observatory/pull/120), and
a second one left uncommitted in a worktree when its session ended. The second is
preserved, unmerged, on branch
[`h1477-recapture-fuzzy-linkage`](https://github.com/sanskrit-lexicon/csl-observatory/tree/h1477-recapture-fuzzy-linkage)
(commit `ad05df6`) with its own disposition note. Its linkage proposal lost on
measurement; two of its negative results did not, and are recorded here.

## Rejected: edit distance 1 — measured twice, independently

The handoff's headline request was an ed1 port. Both implementations built it and both
rejected it, never having seen each other:

| Implementation | Evidence |
|---|---|
| PR #120 | 606 of 863 pw links and 474 of 616 mw links join real but distinct lemmas (`nāman`/`yāman`, `kṛṣ`/`tṛṣ`, `nīla`/`nīca`) |
| branch `h1477-recapture-fuzzy-linkage` | 63.4% measured false-match rate over the same corpus |

Sanskrit headword space is dense at edit distance 1 because the distinctions folded are
phonemic. An estimator whose N̂ is driven by m cannot consume a key that manufactures m.
Treat this as settled: a third implementation is not owed.

## Rejected: full diacritic folding

`norm` (drop every combining mark) makes roughly one pw record in nine ambiguous against
the dictionary's own `<k1>` inventory; the parallel implementation's equivalent `fold`
measured 34.3% false matches. `kāla`/`kala`, `aṇu`/`anu`, `kuṇḍa`/`kunda`, `aś`/`as` are
different lemmas with their own records. This is exactly the boundary `form_key` was
built to respect — it folds anusvāra and homorganic nasals while **keeping vowel length
and retroflexion**.

## Rejected: joining on the csl-orig `<L>` number — and the drift measurement behind it

The `<L>` number looks like the strongest available key (~99% populated in both eras,
and it is an identifier rather than a string) and is in fact the weakest. Measured on
the parallel branch: **64% of resolvable form-era `<L>` codes — 14,403 of 22,466 — no
longer resolve, in current csl-orig, to a record carrying that event's headword.** The
git-era numbers resolve ~100% of the time because they were read out of csl-orig; the
2014 form-era numbers have drifted. Where an L-number is stale it typically points at an
*alphabetically adjacent* record, so a stale-vs-stale collision looks plausible and is
silent.

Share of form-era events whose own `<L>` still resolves to a record carrying that
headword (diacritic-folded comparison; dictionaries with ≥100 resolvable events):

| Dict | Resolvable form-era events | L-codes still valid |
|---|---:|---:|
| pw | 11,768 | 53.9% |
| mw | 1,311 | 52.4% |
| pui | 643 | 38.1% |
| bur | 674 | 33.8% |
| pwg | 146 | 26.7% |
| ben | 462 | 16.9% |
| ap90 | 406 | 11.6% |
| gra | 210 | 8.6% |
| ccs | 2,227 | 6.2% |
| vcp | 317 | 5.0% |
| mw72 | 110 | 4.5% |
| shs | 159 | 3.8% |
| skd | 280 | 3.2% |
| yat | 207 | 1.9% |
| wil | 1,128 | 1.6% |
| ap | 495 | 1.2% |
| cae | 1,296 | 0.2% |

Full 26-dictionary table, including the small-sample rows, is in
`reports/error_recapture_linkage.md` on the archived branch. This measurement is
independent of which headword key wins, so it stands regardless of the branch's
superseded linkage verdict — and it is reusable well beyond this estimator: **any join
of 2014 form-era OBS-T data onto csl-orig by `<L>` number is unsafe outside pw and mw.**

## Not adopted as primary: anchoring both eras on the current csl-orig record

Resolving both eras onto a *current* csl-orig record (exact headword where attested,
else a folded key unique in the full dictionary vocabulary) is the cleanest match to the
estimand — "current records harbouring an error". It was rejected as the operating key
because it drops every form-era event whose headword is not attested in the dictionary
at all, which is **40–97% of them** depending on the dictionary. That is a change of
population, not a linkage decision, and it cannot be assumed independent of
error-proneness: a headword mangled beyond recognition plausibly sits in a more corrupt
entry, not a random one. Worth revisiting only as a sensitivity row.

## Measured and dismissed: the SLP1 repair also fires on English prose

`repair` decodes any cell containing `f`/`q`/`w`/`x`/`z`, which are impossible in IAST.
The `headword_iast` field also carries occasional free-text English, so the rule rewrites
`work` → `ṭork` and `river help us in many ways` → `... many ṭays`. Measured: **14 cells
of 4,176 firings (0.3%), concentrated in `apes`, and zero counted recaptures affected.**
Cosmetic, not a data-integrity problem — recorded so it is not mistaken for one later.

_Dr. Mārcis Gasūns_
