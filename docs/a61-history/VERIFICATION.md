# A61/A13 verification contract

## Automated gates

Run from `csl-observatory`:

```powershell
python scripts/build_article_snapshot.py --check
python scripts/data_index.py --check
python scripts/repo_health_regression.py
python scripts/obs_t_regression.py
python scripts/site_visualization_smoke.py
```

Run the site build when dependencies are installed. Run the clean-sibling
workspace check before recomputing OBS-T/OBS-Q.

## Claim gate

For every quantitative sentence in A61:

- identify a metric ID;
- verify value, unit, population, cutoff, and source;
- reproduce it from the locked input or classify it as externally sourced;
- ensure the prose does not change “labels/accounts/rows” into “people”.

For every historical milestone:

- require a source locator;
- distinguish published record, attributed archive/oral history, and inference;
- reject any `evidence_pending` row as current support.

## Hostile-referee tests

The review must try to falsify:

1. **The heroic-maintainer alternative:** perhaps CDSL survived because of a
   few exceptional individuals, not because of infrastructure. The paper must
   show how individual labour and infrastructural conversion interact.
2. **The institutional-hosting alternative:** perhaps University of Cologne
   custody alone explains survival. The public Git correction and forkability
   record must show what hosting does not explain.
3. **The technical-determinist alternative:** XML/Git did not cause community;
   the paper must identify governance and labour mechanisms.
4. **Survivorship bias:** repository evidence sees what was committed and
   systematically loses unsuccessful work, private negotiation, and informal
   correction.
5. **Teleology:** the 1997 programme did not mechanically unfold into the 2026
   system; abandoned merge/TEI paths and the incomplete corpus link must remain
   visible.

## Acceptance decision

The first packet passes when all automated gates are green, all Major findings
are either applied or explicitly open, and the FABLE handoff points to the
snapshot and referee memo. Readiness can move from 3/5 to 4/5 only after no
unresolved Major evidence or argument finding remains.

