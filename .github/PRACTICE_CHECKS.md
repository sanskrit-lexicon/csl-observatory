# Practice Checks For csl-observatory

Use these checks for observatory datasets, typology work, generated reports, and stacked research PRs.

## Schema invariants
Why this is needed here:
- Recent OBS-T work found that one field mixed location and edit-type semantics.
- Derived, silver, heuristic, and unknown labels must remain distinguishable in generated data and docs.

Before merge, add to the PR:
- Field contract for every changed data/schema field.
- Axis split check for fields that could mix location, edit type, source, confidence, or processing status.
- Negative examples that should fail or remain `unattributed` / unknown.
- Before/after distribution guard for top values and unknown/fallback counts.

## PR slicing
Use a split when one PR combines:
- validation/instrumentation,
- model or schema decision,
- regenerated data,
- site/report output,
- final documentation.

Preferred sequence:
- evidence or validator,
- schema/model decision,
- regeneration,
- docs/site index.

## Stacked PR hygiene
Use this when a PR is based on another work branch.

Before merging the parent:
- Confirm child PR will not auto-close when the parent branch is deleted.
- Retarget child PR after parent merge.
- Recheck diff after retarget so reviewers see only the child delta.

## Narrow review prompt
Suggested prompt:

```md
Please check whether the changed OBS fields still mix two axes. Focus on field contracts, negative examples, and distribution movement; ignore generated formatting churn unless values changed.
```

## PR checklist
- [ ] Changed fields have a one-concept contract.
- [ ] Gold/silver/heuristic/unknown labels are not collapsed.
- [ ] Generated artifacts cite the generator command.
- [ ] Stacked PRs include merge and retarget plan.
- [ ] Review request asks one falsifiable question.
