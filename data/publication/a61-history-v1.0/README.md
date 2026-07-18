# A61 history evidence snapshot v1.0

This directory is the immutable evidence contract for article A61, *The
Cologne Digital Sanskrit Lexicon Project (1994–2027): History,
Infrastructure, and a Quantitative Audit*. Its calendar alias is `2026-07`;
individual metrics retain their actual source cutoffs.

The central rule is that unlike populations stay unlike. In particular:

- 78 repositories is the June GitHub API inventory; 76 repositories is the
  transformed activity-table population.
- 208 is a count of OBS-T corrector labels, not 208 adjudicated people.
- 16 is a normalized non-bot Git identity count for the June snapshot, not a
  count of all historical participants.
- 44 works is the collection inventory; 43 dictionaries appear in OBS-T.

Files:

- `metrics.csv`: defined, sourced quantitative claims.
- `milestones.csv`: the major historical-event layer. Rows marked
  `evidence_pending` are placeholders for the later email archive and cannot
  support load-bearing prose.
- `claim_registry.csv`: article claims joined to metric/event identifiers.
- `contradictions.csv`: contradictory forms and their editorial resolution.
- `source_artifacts.csv`: SHA-256 locks for every local input.
- `manifest.json`: release identity, cutoffs, and hashes.

Rebuild or verify:

```powershell
python scripts/build_article_snapshot.py
python scripts/build_article_snapshot.py --check
```

The event layer is intentionally narrower than a general project chronology.
It records only milestones required by A61/A13 and expands when the historical
email archive can be reviewed.
