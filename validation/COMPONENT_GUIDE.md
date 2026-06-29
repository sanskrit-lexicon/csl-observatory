# Location annotation guide (axis A)

Label each correction by **where in the dictionary entry** it repairs — the
LOCATION axis. This is independent of the *edit type* (spelling/diacritic/case),
which is a separate axis handled automatically. So a spelling typo inside a
definition is `sense` (location), not "orthography". Put one value in
`gold_component`; use `notes` for doubts. A second annotator (for inter-annotator
agreement) fills `gold_component_2` independently.

| value | what it means | typical locus |
|---|---|---|
| `headword` | lemma / headword / homonym index | `<k1> <k2> <h>` |
| `grammar` | gender / part-of-speech | `<lex>` |
| `citation` | source reference / siglum / page | `<ls>`, `<pc>` |
| `sense` | gloss / definition / meaning content (incl. Sanskrit words in the gloss) | definition prose, `<s>` |
| `crossref` | cross-reference / link target | `<lb>` |
| `meta` | record id / structural metadata | `<L> <e>` |
| `markup` | the XML/tag structure itself (delimiters, tag names) | `< >`, `{ }` |
| `unattributed` | cannot tell where from the evidence shown | — |

Tips:
- Judge the **location**, not the kind of edit. A diacritic fix on a headword =
  `headword`; the same fix in a gloss word = `sense`.
- For **git-layer** rows, read `old_raw`/`new_raw` (the tagged source line) to see
  which tag's content changed.
- For **form-layer** rows, judge from `old_iast`→`new_iast` and the `headword`.
- Do not look at any auto-generated label; this sheet hides it on purpose.
