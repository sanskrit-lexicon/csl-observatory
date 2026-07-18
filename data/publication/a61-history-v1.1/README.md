# A61 history evidence snapshot v1.1

This immutable evidence contract supports article A61, *The Cologne Digital
Sanskrit Lexicon Project (1994–2027): History, Infrastructure, and a
Quantitative Audit*. Release v1.0 remains unchanged. The calendar alias is
`2026-07`; each metric retains its actual cutoff.

Unlike populations remain unlike: 78 API inventory repositories are not 76
transformed repositories; 208 OBS-T labels are not 208 adjudicated people; 16
non-bot Git identities are not all historical participants; 44 collection works
are not the 43 dictionaries in OBS-T. Five is the observed annual maximum of
correction implementers; four is stale manuscript prose.

## Number inventory and M10 ruling

`claim_registry.csv` inventories every empirical/project number retained in
A61 chapters `00-front-matter.mdx` through `11-conclusion.mdx`, excluding the
references chapter. Section
numbers, cross-references, illustrative entry identifiers, bibliography years,
and dictionary edition years are excluded unless the date itself carries a
historical claim. Every inventory row is joined to evidence IDs and marked
verified, attributed, or explicitly removed/superseded.

The locally reproducible retained M10 subset is hash-locked: 323,425 union headwords;
105 dictionary pairs; BHS 58.7% unique; CCS 0.6% unique; 94,753 shared MW/PWG
headwords; and 828,505 canonical citations resolving to 912 texts. The retained
organisation evidence also locks 5,413 issue/PR rows, sixteen normalized
non-bot Git identities, 44 collection works, 208 OBS-T labels, and a maximum of
five annual correction implementers.

No committed source, method, and cutoff was located for the former entry-length/
15%/819 or 485/330/41.6% blocks. Other unsupported figures are listed in the
registry as removed or superseded, including stale MW/PWG and etymology totals,
the Heritage and Whitney exact totals, print-change counts, Apte percentages,
annual issue arithmetic, detailed citation subtotals, and site traffic.
Private-archive counts remain attributed until hash-locked.

## Venue and legal rulings

The official IIT Bombay WSC page, checked 18 July 2026, gives the abstract
deadline as **1 February 2027** and gives **10–14 December 2027** in both the
headline and Important Dates table. Its footer contradicts this with
**10–15 December 2027**. Planning uses the headline/table dates pending
clarification. No abstract or paper word limit was published:
<https://www.hss.iitb.ac.in/wsc2027/>.

Indian copyright term rules attach to the author and relevant work. The deaths
of an editor and publisher alone do not establish that Apte 1957 is public
domain. A61 should report only observed 2025 Cologne availability unless a
documented rights determination is supplied. The 2004 EU database-right passage
is historical attribution, not a present legal opinion.

## Files and verification

- `metrics.csv`: defined quantitative claims, including correction/unsupported
  statuses.
- `milestones.csv`: sourced events; exactly two email rows remain
  `evidence_pending` and cannot support load-bearing prose.
- `claim_registry.csv`: A61 numeric inventory joined to evidence IDs.
- `contradictions.csv`: stale forms and editorial rulings.
- `source_artifacts.csv`: SHA-256 locks for repository and sibling inputs.
- `manifest.json`: release identity, manuscript base commit plus frozen
  working-tree revision, cutoffs, scope, and hashes.

```powershell
python scripts/build_article_snapshot.py
python scripts/build_article_snapshot.py --check
```

The build validates evidence references, the two pending email milestones, the
five-implementer correction, chapter coverage, and the A13 byte fence at
SHA-256 `05fbe656224d93e46921614b2a609631c6769f761c8832e84ac84a3c991c9f00`.
