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

The v1.1 generator additionally asserts that the only pending milestone IDs are
`HIST-EMAIL-TECH` and `HIST-EMAIL-RIGHTS`, all claim evidence IDs resolve, the
stale four-implementer form is absent, the chapter number inventory is present,
and the A13 SHA-256 remains
`05fbe656224d93e46921614b2a609631c6769f761c8832e84ac84a3c991c9f00`.

## Legal and venue verification

- Apte 1957: no public-domain assertion without a documented determination of
  relevant authorship/work and term; observed 2025 availability can be reported
  independently.
- Database rights: historical attribution only, not a current legal conclusion.
- WSC official page, checked 18 July 2026: abstract deadline 1 February 2027;
  headline/table 10–14 December; footer 10–15 December (contradiction logged);
  no published word limit: <https://www.hss.iitb.ac.in/wsc2027/>.

## Build ruling

The data and regression gates are required. Run `npm run build` from
`observatory/site` up to three times. If every attempt fails only while fetching
external `npm:d3*` modules, record the CDN blocker; any deterministic local
failure remains a release blocker.

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
