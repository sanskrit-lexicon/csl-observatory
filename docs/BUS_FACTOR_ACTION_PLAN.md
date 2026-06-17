# Bus-Factor Action Plan

Date: 2026-06-12
Status: roadmap SC3 action plan; no external repository changes or GitHub
mutations have been made from this file.

This plan turns the bus-factor finding into maintainer actions. It does not
assign new maintainers, archive repositories, open issues, or change licenses.
Anything that requires a person or organization commitment stays blocked until
MG or the sanskrit-lexicon organization confirms it.

## Source Evidence

- `reports/bus_factor.md`: 65 of 76 repositories have bus factor 1; one
  contributor accounts for 51.8% of all recorded work; the core trio accounts
  for 97.6%.
- `reports/contributor_identity.md`: 0 of 16 human contributors have a
  registered ORCID in the contributor map; 7 named contributors need ORCID
  entries; 9 logins still need identification.
- `observatory/site/src/data/repos.csv`: current open-issue counts, push dates,
  descriptions, license fields, and archive flags.
- `docs/REPOSITORY_HEALTH_DECISION_PACKET.md`: license and cleanup decisions
  that overlap with continuity risk.
- Existing tracking references: `csl-observatory` issue #1 for unidentified
  contributors and `docs/hygiene_issues_draft.md` issues #19 and #20 for
  cleanup and ORCID/identity work.

## Selection Rule

Use two views together:

1. Report-order top risks: repositories with bus factor 1 and a 100% top
   contributor share.
2. Impact-weighted risks: repositories or repo classes that carry active source,
   correction, release, dashboard, or public artifact workflows.

The first view prevents the smallest one-person repositories from being
forgotten. The second view keeps maintenance effort focused on workflows whose
failure would block releases or daily work.

## Top-Five Report Rows

These are the first five single-person rows surfaced by `reports/bus_factor.md`.
They now have explicit mitigation or accepted-risk notes.

| Repository | Evidence | Mitigation or accepted-risk note | Status |
|---|---|---|---|
| `DCS` | 1 contributor; 100% top share; 23 contributions; 6 open issues; pushed 2026-05-29; `NOASSERTION` license. | Treat as a high-risk one-person data/research-adjacent repository. Mitigate through license normalization after RH1 and a short retention/owner note before public release surfaces rely on it. | blocked on RH1 and maintainer owner note |
| `KNA` | 1 contributor; 100% top share; 4 contributions; 1 open issue; pushed 2026-05-29; no license. | Accepted as a small-repo continuity risk unless MG marks it active. Mitigate by resolving license policy and adding a short status note if retained as active. | blocked on RH1 |
| `KOW` | 1 contributor; 100% top share; 4 contributions; 1 open issue; pushed 2026-05-29; no license. | Accepted as a small-repo continuity risk unless MG marks it active. Mitigate by resolving license policy and adding a short status note if retained as active. | blocked on RH1 |
| `MCI` | 1 contributor; 100% top share; 8 contributions; 1 open issue; pushed 2026-05-22; no license. | Accepted as a small-repo continuity risk unless MG marks it active. Mitigate by resolving license policy and documenting whether this is data, research support, or archive material. | blocked on RH1 and maintainer classification |
| `santamlegacy` | 1 contributor; 100% top share; 0 open issues; cleanup candidate; no license. | Do not invest onboarding effort unless retained. Mitigation is the RH3 archive/retain decision; archive only after MG confirms no deployment depends on it. | blocked on RH3 |

## Impact-Weighted Continuity Risks

| ID | Risk class | Evidence | Mitigation | Owner | Target | Status |
|---|---|---|---|---|---|---|
| BF1 | Source and correction backbone: `csl-orig`, `csl-corrections`, `CORRECTIONS`. | `csl-orig` has 74 open issues and 62% top share; `csl-corrections` has 24 open issues and 52% top share; `CORRECTIONS` has 90 open issues and 70% top share. | Build the SC2 continuity packet around source refresh, correction intake, issue triage, and release-sensitive commands. Add accepted-risk notes where a second maintainer is not currently available. | MG + Codex | 2026-09-30 | next |
| BF2 | Public artifact and conversion tooling: `cologne-stardict`, `csl-json`, `csl-app`, `csl-websanlexicon`, `csl-pywork`. | `cologne-stardict` is 99% top-share; `csl-json` 98%; `csl-app` 96%; `csl-websanlexicon` 83%; `csl-pywork` 66%. | Create runbook notes for build, smoke test, release, and rollback steps. Prefer automation and documented commands before recruiting backup reviewers. | Codex | 2026-10-31 | scheduled |
| BF3 | Observatory maintenance itself: `csl-observatory`. | 99% top share, 9 open issues, and generated reports/site data that now steer the roadmap. | Keep `docs/MAINTAINER_REVIEW_CHECKLIST.md` as the monthly operating ritual; add one-command refresh and generated-output regression checks through AR3/AR5. | Codex | ongoing | active |
| BF4 | Small single-author data/research repos: `DCS`, `KNA`, `KOW`, `MCI`. | Each has bus factor 1 and 100% top share; all were pushed in May 2026. | Use the top-five notes above as the initial accepted-risk record. Revisit after RH1 and metadata cleanup; do not create extra process unless MG says these are active work surfaces. | MG | 2026-08-31 | decision needed |
| BF5 | Temporary and legacy repositories: `santamlegacy`, `temp_corrections_*`, `test_cologne_push`. | Six cleanup candidates remain live; several are also bus-factor 1. | Follow RH3: archive only after MG confirms merged/superseded status. Until then, count them separately from active continuity planning. | MG + Org | 2026-07-15 | blocked on RH3 |

## Existing Tracking Links

| Area | Link | How it mitigates bus-factor risk |
|---|---|---|
| Unknown contributor identities | `https://github.com/sanskrit-lexicon/csl-observatory/issues/1` | Lets occasional contributors be credited and contacted, where appropriate. |
| ORCID and identity backlog | `https://github.com/sanskrit-lexicon/csl-observatory/issues/20` via `docs/hygiene_issues_draft.md` | Makes scholarly credit and contributor continuity less dependent on memory. |
| Cleanup candidates | `https://github.com/sanskrit-lexicon/csl-observatory/issues/19` via `docs/hygiene_issues_draft.md` | Removes temporary repositories from continuity metrics once MG confirms they are superseded. |
| License backlog | `https://github.com/sanskrit-lexicon/csl-observatory/issues/15` and `https://github.com/sanskrit-lexicon/csl-observatory/issues/16` via `docs/hygiene_issues_draft.md` | Clarifies reuse rights so future maintainers and contributors can safely continue work. |

## Monthly Review Prompts

Use these during the last-Friday review in
`docs/MAINTAINER_REVIEW_CHECKLIST.md`:

1. Did any top-five report-row repository gain a second meaningful contributor?
2. Did any active backbone repo gain a runbook, smoke test, or backup reviewer?
3. Did any contributor provide an ORCID or identity confirmation?
4. Did RH1 or RH3 decisions unblock license or archive actions?
5. Did generated reports change the top-five risk rows or the impact-weighted
   queue?

Commands to rerun before updating this file:

```bash
python scripts/bus_factor.py
python scripts/contributor_identity.py
python scripts/repo_health.py
```

## Next Implementation Hooks

- SC2 should start with BF1 and BF3: document how to refresh observatory data,
  process corrections, and rebuild release-sensitive reports.
- AR1/AR3 should start with BF2: make public artifact refresh commands
  repeatable outside one person's local memory.
- SC1 should use the existing issue #1 and issue #20 references to close the
  contributor identity and ORCID backlog.
- RH1/RH3 must be resolved before this plan treats licenses or cleanup
  candidates as complete.
