# Question Research Findings — 2026-06-27 Sweep

Agent sweep of all `question`-labeled open issues across the `sanskrit-lexicon` org.
**Policy (from 2026-06-27):** agents post to GitHub only when there is concrete, actionable data (line numbers, counts, a definitive answer). Inconclusive findings, pending items, and well-answered threads are collected here instead.

---

## Summary

| Repo | Issues covered | Comments posted | Skipped (already answered) | Pending (network failure) |
|---|---|---|---|---|
| COLOGNE | 46 | ~28 | ~18 | — |
| MWinflect | 8 | 8 | — | — |
| CORRECTIONS | 7 | 7 | — | — |
| PWK | 5 | 5 | — | — |
| ACC | 4 | 4 | — | — |
| csl-orig | 12 | 0 | — | 12 |
| MWS | 5 | 0 | — | 5 |
| VCP | 5 | 0 | — | 5 |
| alternateheadwords | 3 | 0 | — | 3 |
| AP90 | 3 | 0 | — | 3 |
| SKD | 3 | 0 | — | 3 |
| PWG | 3 | 0 | — | 3 |
| 20 small repos | ~25 | 0 | — | ~25 |

---

## COLOGNE — key actionable findings (not obvious from issue title)

| Issue | Finding | Next step |
|---|---|---|
| [#191](https://github.com/sanskrit-lexicon/COLOGNE/issues/191) CAE meta-line | 2,669 `firstalt` markers present; alternate-entry coalescence not done | Human: decide scope of coalescence |
| [#194](https://github.com/sanskrit-lexicon/COLOGNE/issues/194) PWG ls | All `?` markers resolved in pwg.txt; pwgbib expansion + edge cases remain | Agent can finish expansion with existing pwgbib data |
| [#197](https://github.com/sanskrit-lexicon/COLOGNE/issues/197) PWG ab | 179,930 `<ab>` occurrences present; 242/791 UNCHECKED entries in pwgab_input.txt | Human: review 242 UNCHECKED lines |
| [#316](https://github.com/sanskrit-lexicon/COLOGNE/issues/316) ACC abbreviations | 2017 `<ab>`/`<ls>` markup by Dhaval never merged; zips on Cologne server | Human: decide whether to merge; 0 ab/ls tags in current acc.txt |
| [#334](https://github.com/sanskrit-lexicon/COLOGNE/issues/334) Bibliography | CITATION.cff exists but skeletal (no authors, no DOI) | Agent can complete CITATION.cff once Zenodo DOI is minted |
| [#356](https://github.com/sanskrit-lexicon/COLOGNE/issues/356) Credit | Homepage text added 2021; CITATION.cff still skeletal | Same fix as #334 |
| [#388](https://github.com/sanskrit-lexicon/COLOGNE/issues/388) Expand "id." | 5,000+ `id.`/`the same` instances across 20+ dicts; no automation exists | Human policy decision: expand or keep terse |
| [#408](https://github.com/sanskrit-lexicon/COLOGNE/issues/408) Kosha XML | ABCH implements `syns`/`eid` in txt side (4,619 entries); make_xml.py gap | Agent can implement make_xml.py for kosha format |
| [#418](https://github.com/sanskrit-lexicon/COLOGNE/issues/418) Print changes | `<chg src="...">` format in GRA (380 elements); display layer in csl-websanlexicon not implemented | Agent can implement display in websanlexicon |
| [#450](https://github.com/sanskrit-lexicon/COLOGNE/issues/450) Prakrit | `indic-dict/stardict-prakrit` has Sheth+Dhanapāla; none in csl-orig | Human: scope decision (CDSL vs. indic-dict) |

---

## MWinflect — open sub-questions per paradigm class

All 8 issues partially answerable; main paradigms are settled. Open gaps per issue:

| Issue | Open sub-question |
|---|---|
| [#6](https://github.com/sanskrit-lexicon/MWinflect/issues/6) m_a pada | M-anusvara edge in 69 compounds; `grahāhvaya` unmarked-pada unresolved |
| [#37](https://github.com/sanskrit-lexicon/MWinflect/issues/37) -an stems | `sīman` feminine irregular; 16 `han`/non-han edge words need per-case decisions |
| [#42](https://github.com/sanskrit-lexicon/MWinflect/issues/42) gutturals | `valṅgi` neuter plural for `lg` cluster flagged speculative |
| [#43](https://github.com/sanskrit-lexicon/MWinflect/issues/43) cerebrals | `w`/`W`/`q` cases lack published authority |
| [#44](https://github.com/sanskrit-lexicon/MWinflect/issues/44) labials | `gardabh` nom irregular; `gṛbh` Grassmann shift; `prāśām` neuter typo? |
| [#45](https://github.com/sanskrit-lexicon/MWinflect/issues/45) palatals | `khaṅj` B-ending unconfirmed; `viśva-sṛj` Kale vs. MW/PW disagreement |
| [#46](https://github.com/sanskrit-lexicon/MWinflect/issues/46) semivowels | `div` neuter unconfirmed; `janāv` and `dīv` have no declension (defective) |
| [#48](https://github.com/sanskrit-lexicon/MWinflect/issues/48) h-endings | `-sah`/`-zah` A-lengthening scope beyond nom.sg. unresolved |

---

## CORRECTIONS — findings

| Issue | Finding | Actionable? |
|---|---|---|
| [#14](https://github.com/sanskrit-lexicon/CORRECTIONS/issues/14) MD Addenda | Archive.org pages are from a later MD edition, not MW; edition identification needed | Human: identify edition |
| [#126](https://github.com/sanskrit-lexicon/CORRECTIONS/issues/126) MW feminine forms | All interpretations answered in thread; MWlexnorm updated | Ready to close |
| [#244](https://github.com/sanskrit-lexicon/CORRECTIONS/issues/244) STC SreAMs | Uses comparative stem `śreyāṃs-` as headword (Renou tradition); confirmed in stc.txt L137583 | Ready to close |
| [#292](https://github.com/sanskrit-lexicon/CORRECTIONS/issues/292) Multi-word headwords | Join-words vs. underscore for key1 — unresolved cross-dict scope | Human decision |
| [#314](https://github.com/sanskrit-lexicon/CORRECTIONS/issues/314) mw72 markup | `{%...%}` for italics is correct regardless of language; Sa extraction deferred by all | Ready to close |
| [#414](https://github.com/sanskrit-lexicon/CORRECTIONS/issues/414) Russian in PWG | All 82-entry audit completed by @SergeA in 2018 | Ready to close |
| [#441](https://github.com/sanskrit-lexicon/CORRECTIONS/issues/441) GRA thank-you | Form-letter workflow answered | Ready to close |

---

## PWK — findings

| Issue | Finding |
|---|---|
| [#39](https://github.com/sanskrit-lexicon/PWK/issues/39) Commentary study | 2,710 `Comm.` instances; commleft.txt exists but needs re-validation; deferred since 2016 |
| [#50](https://github.com/sanskrit-lexicon/PWK/issues/50) WILSON references | All 11 WILSON cases handled in PWK #48; ready to close |
| [#66](https://github.com/sanskrit-lexicon/PWK/issues/66) s.u. markup | `s.u.` = *sub voce* confirmed; `plīyā` encoding correct; display needs verification |
| [#98](https://github.com/sanskrit-lexicon/PWK/issues/98) RV citations | ~140 `zu <ls>ṚV.</ls>` cases agreed to be retagged as `<ls>SĀY. zu ṚV. N,N</ls>` |
| [#108](https://github.com/sanskrit-lexicon/PWK/issues/108) Roadmap | Items 1–3, 5–7 and secondary HW task need prioritization by @funderburkjim |

---

## ACC — findings

| Issue | Finding |
|---|---|
| [#2](https://github.com/sanskrit-lexicon/ACC/issues/2) Non-English words | 272,898 non-ASCII chars in 92,845 lines; top tokens: Sanskrit author names (Rādh 2,177; Bhaṭṭa 1,605) + subject tags (vedānta 1,395); two German-umlaut tokens (Bühler 486, Tüb 296) |
| [#4](https://github.com/sanskrit-lexicon/ACC/issues/4) `<HI>` tag | 5,271 total; 5,207 = `<HI>--` (correct); 11 `<HI>{#...#}` missed-headword cases never converted since 2017 |
| [#5](https://github.com/sanskrit-lexicon/ACC/issues/5) Non-English non-headwords | ~20,440 untagged `<HI1>` lines; 0 `<ab>` tags; blocked on acc6 merge (issue #17) |
| [#17](https://github.com/sanskrit-lexicon/ACC/issues/17) acc6 review | acc6 markup (ab/ls tags) approved 2017 but never merged; XML validation step never completed |

---

## Pending — network failures (not yet researched)

These repos/issues were queued but agents hit TLS/connection errors. Retry once network is stable.

### csl-orig (12 issues)
[#174](https://github.com/sanskrit-lexicon/csl-orig/issues/174) SKD verb headwords · [#631](https://github.com/sanskrit-lexicon/csl-orig/issues/631) IAST ऌ vs ळ · [#923](https://github.com/sanskrit-lexicon/csl-orig/issues/923) mw:12831 · [#1060](https://github.com/sanskrit-lexicon/csl-orig/issues/1060) MW data without meaning · [#1173](https://github.com/sanskrit-lexicon/csl-orig/issues/1173) pwg:7452 · [#1780](https://github.com/sanskrit-lexicon/csl-orig/issues/1780) MW 4112.1 'in comp' · [#1788](https://github.com/sanskrit-lexicon/csl-orig/issues/1788) MW 592.2 akṣara · [#1790](https://github.com/sanskrit-lexicon/csl-orig/issues/1790) MW 669 akṣan-vat · [#2811](https://github.com/sanskrit-lexicon/csl-orig/issues/2811) MW avadhāraṇa · [#2817](https://github.com/sanskrit-lexicon/csl-orig/issues/2817) MW near-blank entries · [#2824](https://github.com/sanskrit-lexicon/csl-orig/issues/2824) LRV 7287.1 double listing · [#2843](https://github.com/sanskrit-lexicon/csl-orig/issues/2843) Duplicate compound headwords

### MWS (5) · VCP (5)
MWS: [#45](https://github.com/sanskrit-lexicon/MWS/issues/45) cf. · [#179](https://github.com/sanskrit-lexicon/MWS/issues/179) RV poet · [#183](https://github.com/sanskrit-lexicon/MWS/issues/183) tādṛśī headword · [#189](https://github.com/sanskrit-lexicon/MWS/issues/189) Mn. links · [#192](https://github.com/sanskrit-lexicon/MWS/issues/192) kararudh  
VCP: [#12](https://github.com/sanskrit-lexicon/VCP/issues/12) vac-vcp-cmp2 · [#15](https://github.com/sanskrit-lexicon/VCP/issues/15) Meld diff viewer · [#22](https://github.com/sanskrit-lexicon/VCP/issues/22) patterns later · [#23](https://github.com/sanskrit-lexicon/VCP/issues/23) debatable items · [#25](https://github.com/sanskrit-lexicon/VCP/issues/25) addenda/corrigenda

### alternateheadwords (3) · AP90 (3) · SKD (3) · PWG (3)
alternateheadwords: [#2](https://github.com/sanskrit-lexicon/alternateheadwords/issues/2) WIL anubandhas · [#11](https://github.com/sanskrit-lexicon/alternateheadwords/issues/11) VCP anubandha · [#25](https://github.com/sanskrit-lexicon/alternateheadwords/issues/25) usage  
AP90: [#21](https://github.com/sanskrit-lexicon/AP90/issues/21) spelling errors · [#27](https://github.com/sanskrit-lexicon/AP90/issues/27) bālhakāḥ · [#28](https://github.com/sanskrit-lexicon/AP90/issues/28) dvāja  
SKD: [#6](https://github.com/sanskrit-lexicon/SKD/issues/6) Wikisource edition · [#12](https://github.com/sanskrit-lexicon/SKD/issues/12) dhātu comparison · [#18](https://github.com/sanskrit-lexicon/SKD/issues/18) Arlo Griffiths  
PWG: [#44](https://github.com/sanskrit-lexicon/PWG/issues/44) preverbs · [#107](https://github.com/sanskrit-lexicon/PWG/issues/107) commentary citation · [#194](https://github.com/sanskrit-lexicon/PWG/issues/194) underscore v1e

### Small repos (~25 issues)
AP · BOR · csl-corrections · csl-devanagari · csl-inflect · csl-ldev · csl-newsletter · DCS · GRA · hwnorm1 · IEG · INM · LRV · MCI · mw-dev · MW72 · SCH · SHS · temp_corrections_ap90 · temp_corrections_mw

---

## Issues where agent comments are ready to close (no PR needed)

Based on findings — human can close with one click:

- [CORRECTIONS #126](https://github.com/sanskrit-lexicon/CORRECTIONS/issues/126) — already resolved
- [CORRECTIONS #244](https://github.com/sanskrit-lexicon/CORRECTIONS/issues/244) — confirmed correct
- [CORRECTIONS #314](https://github.com/sanskrit-lexicon/CORRECTIONS/issues/314) — already resolved
- [CORRECTIONS #414](https://github.com/sanskrit-lexicon/CORRECTIONS/issues/414) — audit completed 2018
- [CORRECTIONS #441](https://github.com/sanskrit-lexicon/CORRECTIONS/issues/441) — workflow answered
- [PWK #50](https://github.com/sanskrit-lexicon/PWK/issues/50) — handled in #48
- [COLOGNE #272](https://github.com/sanskrit-lexicon/COLOGNE/issues/272) — by design, can close
- [COLOGNE #287](https://github.com/sanskrit-lexicon/COLOGNE/issues/287) — archival record only
- [ACC #17](https://github.com/sanskrit-lexicon/ACC/issues/17) — pending acc6 merge decision
