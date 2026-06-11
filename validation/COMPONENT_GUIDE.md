# Component annotation guide

Label each correction by the dictionary-entry **component it repairs** — *where*
the error was, not its surface form. Put one value in `gold_component`. If two
seem to fit, pick the most specific; use `notes` for doubts. A second annotator
(for inter-annotator agreement) fills `gold_component_2` independently.

| value | what it means | typical locus |
|---|---|---|
| `headword` | lemma / headword / homonym index | `<k1> <k2> <h>` |
| `grammar` | gender / part-of-speech | `<lex>` |
| `citation` | source reference / siglum / page | `<ls>`, `<pc>` |
| `sense` | gloss / definition / meaning content | definition prose, `<s>` |
| `crossref` | cross-reference / link target | `<lb>` |
| `meta` | record id / structural metadata | `<L> <e>` |
| `encoding` | transliteration / diacritic of a Sanskrit form | any Sanskrit text |
| `markup` | XML/tag structure itself (delimiters, tag names) | `< >`, `{ }` |
| `orthography` | plain spelling typo, capitalization, whitespace in non-tag text | body text |
| `unknown` | cannot tell from the evidence shown | — |

Tips:
- For **git-layer** rows, read `old_raw`/`new_raw` (the tagged source line) to see
  which tag's content changed.
- For **form-layer** rows, judge from `old_iast`→`new_iast` and the `headword`.
- `encoding` vs `orthography`: `encoding` = a Sanskrit diacritic/transliteration
  fix; `orthography` = a plain Latin/case/spacing typo.
- Do not look at any auto-generated label; this sheet hides it on purpose.
