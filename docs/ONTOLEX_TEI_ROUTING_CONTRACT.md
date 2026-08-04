# OntoLex-Lemon + TEI Lex-0 — routing contract to csl-standards

_Created: 27-07-2026 · Last updated: 27-07-2026_

**Not built here.** RDF/TEI implementation is [csl-standards](https://github.com/sanskrit-lexicon/csl-standards)'
object per the boundary rules. This document is the **field-mapping contract**
the standards repo consumes — it commits observatory to keeping the schema
fields named below stable, and lets csl-standards implement OntoLex-Lemon/TEI
Lex-0 output without re-deriving the mapping. Source:
[`docs/HYPOTHESIS_VIZ_STANDARDS_SPEC_2026-07.md`](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/docs/HYPOTHESIS_VIZ_STANDARDS_SPEC_2026-07.md)
§4.4, staged via [H1495](https://github.com/gasyoun/Uprava/blob/main/handoffs/archive/H1495-Sonnet_csl-observatory_obs-t-ontolex-tei-routing-contract_22.07.26.md).

## Field mapping

| Observatory field (correction-event schema) | OntoLex-Lemon target | TEI Lex-0 target |
|---|---|---|
| `headword_iast` (+ `dict`, `lcode`) | `ontolex:LexicalEntry` / `ontolex:canonicalForm` → `ontolex:Form` with `ontolex:writtenRep@sa-Latn` | `<entry>` / `<form type="lemma">` / `<orth>` |
| `old_iast` → `new_iast` correction pair | `ontolex:Form` variant statements; the correction event itself as a `prov:Activity` revising the Form (FrAC/prov-o pattern — csl-standards' call) | `<orth>` with `@corresp` + revision noted in `<revisionDesc>`/`@change` |
| `error_component = sense` events | anchor to `ontolex:LexicalSense` of the affected entry | `<sense>` |
| `dict` | `lime:Lexicon` per dictionary | one TEI document per dictionary, `<titleStmt>` |
| `event_id` (persistent-ID scheme, `docs/HYPOTHESIS_VIZ_STANDARDS_SPEC_2026-07.md` §4.1) | minted as a resolvable IRI `https://…/obst/v1/<id>` — namespace choice is csl-standards' | `@xml:id` |
| `corrector` / `date` | `prov:wasAssociatedWith` / `prov:endedAtTime` | `<change who="#…" when="…">` |

## Stability commitment

Observatory commits to keeping the schema fields named above stable across
releases. The `event_id` scheme (§4.1 of the spec, pattern
`^obst:v1:(form|git|printchange|batch):[a-z0-9]+:[0-9a-f]{12}$`) is versioned
and invariant across re-runs, so downstream IRI minting in csl-standards stays
resolvable.

## Boundary

- No RDF/TEI code lands in `csl-observatory`. Observatory owns the
  correction-event schema and its evolution; csl-standards owns the OntoLex-Lemon
  / TEI Lex-0 serialization and any RDF/XML tooling.
- Handoff tracked by an issue on
  [`csl-standards`](https://github.com/sanskrit-lexicon/csl-standards) (filed
  alongside this doc).

## Sources

- OntoLex-Lemon lexicography (lexicog) module: <https://www.w3.org/2019/09/lexicog/>
  · core OntoLex-Lemon: <https://www.w3.org/2016/05/ontolex/>
- TEI Lex-0: <https://dariah-eric.github.io/lexicalresources/pages/TEILex0/TEILex0.html>

_Dr. Mārcis Gasūns_
