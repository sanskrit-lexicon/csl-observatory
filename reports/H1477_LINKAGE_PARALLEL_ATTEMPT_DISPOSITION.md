# H1477 record linkage — disposition of the parallel (superseded) attempt

_Created: 27-07-2026 · Last updated: 27-07-2026_

**Status: SUPERSEDED — archival branch, do not merge.** This branch is a second,
independent implementation of handoff H1477 that ran concurrently with the one that
shipped as [PR #120](https://github.com/sanskrit-lexicon/csl-observatory/pull/120)
(commit [7980a9b](https://github.com/sanskrit-lexicon/csl-observatory/commit/7980a9b194c80da3b8c625f25f68c37b18c34287),
merged 27-07-2026 21:24). Neither session saw the other. The branch is preserved
because two of its results are additive and survive the supersession; its core
linkage proposal does not.

Branch base is [d46d4c6](https://github.com/sanskrit-lexicon/csl-observatory/commit/d46d4c6),
i.e. *before* #120 merged, so a diff of this branch against `main` reads as deleting
the merged work. That is an artefact of the base, not a proposal. Diff against
`d46d4c6` to see what this session actually did.

## Why it is superseded, measured rather than asserted

Both sessions built a ladder of linkage keys and scored it for false matches. They
adopted different keys. Re-running both key families over the same corpus
(`correction_events_final.csv`, 51,902 events with a headword) gives:

| Key | pw | mw | bur | cae | Total m |
|---|---:|---:|---:|---:|---:|
| `exact` (previously published) | 169 | 105 | 23 | 1 | 316 |
| `scheme_repair` — **this branch's adopted key** | 172 | 107 | 26 | 1 | 328 |
| `repair` — #120 (SLP1 decode) | 192 | 125 | 32 | 2 | 374 |
| `form_key` — **#120's adopted key** | 196 | 128 | 33 | 9 | 396 |
| union of both repairs | 192 | 124 | 33 | 2 | 374 |
| union + `form_key` | 196 | 127 | 34 | 9 | 397 |

The two repairs fire on almost disjoint cells (4,122 decoded by #120 only, 506 by this
branch only, 0 where both fire and agree), so the union looked promising. It is not:
it wins **+1 recapture** over #120 alone (397 vs 396) and *loses* one in mw. The 506
cells this branch decodes and #120 does not are overwhelmingly not Sanskrit — the rule
decodes *any* pure-ASCII cell as Harvard-Kyoto, so `God` → `ṅod`, `Happy` → `ḥappy`,
`She` → `ṣhe`, `Derive` → `ḍerive`. Those mangle into strings that match nothing, which
is why the branch's own report could truthfully say the key "links no non-identical
pair" while still being the weaker key. #120's `form_key` is better on every
dictionary and is the one to keep.

Reproduce: `scripts/error_recapture_linkage.py` (this branch) and
`scripts/headword_linkage.py` (`main`) both regenerate their outputs deterministically;
all seven outputs on this branch were re-run and reproduce byte-for-byte.

## What survives and is worth porting

1. **L-code drift, measured.** 64% of resolvable form-era `<L>` codes (14,403 of
   22,466) no longer resolve to a csl-orig record carrying that event's headword,
   with a per-dictionary table over 26 dictionaries (pw 53.9% still valid, cae 0.2%).
   #120 never examined L-codes. This is a reusable statement about corpus quality,
   independent of which linkage key wins, and it is the reason `lcode` is not the free
   recall it appears to be. See `reports/error_recapture_linkage.md` § L-code drift.
2. **The `anchored` rule as a negative result.** Resolving both eras onto *current*
   csl-orig records is the cleanest match to the estimand, but it drops 40–97% of
   form-era events per dictionary — a change of population, not of linkage, and not
   safely assumed independent of error-proneness. #120 has no equivalent sensitivity
   row.
3. **Edit-distance-1 rejected twice, independently.** The handoff asked for the ed1
   port. This branch measured 63.4% false matches; #120 measured 606 of 863 pw links
   and 474 of 616 mw links joining distinct lemmas. Two implementations that never saw
   each other reached the same verdict on the handoff's headline request — a
   replication worth more than either measurement alone.

## Not a defect worth filing

#120's SLP1 repair also fires on English prose sitting in the headword field
(`work` → `ṭork`, `river help us in many ways` → `... many ṭays`). Measured: 14 cells
of 4,176 firings (0.3%), concentrated in `apes`, and **zero counted recaptures are
affected**. Cosmetic, not a data-integrity problem; recorded here so the next session
does not re-derive it and mistake it for one.

_Dr. Mārcis Gasūns_
