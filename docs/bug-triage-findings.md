# Bug Triage Findings — 2026-06-27 Sweep

Agent sweep of all `bug`-labeled open issues across the `sanskrit-lexicon` org (84 issues, 22 repos).
**Excluded:** CORRECTIONS (A2 decision pending), issues with active threads.
**Policy:** post only with concrete data (line numbers, counts, file locations); never post "inconclusive".

---

## Summary

| Repo | Issues triaged | Comments posted | Tier A found | Already fixed | Skipped/Network |
|---|---|---|---|---|---|
| csl-orig | 11 | 4 | 2 | 0 | 3 (already triaged) + 2 (network) |
| COLOGNE | 18 | 10 | 4 | 2 | 2 (network) + 2 (display/no data) |
| csl-devanagari | 4 | 1 | 1 | 1 | 1 (active) + 1 (network) |
| csl-ldev | 6 | 2 | 1 | 0 | 2 (network) + 1 (display/no data) |
| csl-websanlexicon | 3 | 1 | 0 | 0 | 1 (network) + 1 (mixed) |
| csl-apidev | 2 | 1 | 0 | 0 | 1 (network) |
| BEN | 1 | 1 | 0 | 1 | — |
| AP90 | 1 | 0 | 0 | 1 | — |
| hwnorm1 | 2 | 1 | 0 | 2 | — |
| GreekInSanskrit | 1 | 1 | 0 | 1 | — |
| MWS | 2 | 1 | 1 | 0 | — |
| GRA | 1 | 0 | 0 | 0 | mislabeled (feature request) |
| PWG | 1 | 0 | 0 | 0 | active thread |
| PWK | 1 | 0 | 0 | 0 | scholarly discussion, Jim deferred |
| VCP | 2 | 0 | 0 | 0 | "not anytime soon" per reporter |
| WIL | 1 | 0 | 0 | 0 | server-side HTTP 500 |
| alternateheadwords | 1 | 0 | 0 | 0 | scholarly design discussion (2016) |
| DCS | 1 | 0 | 0 | 0 | external server (Heidelberg) |
| csl-app | 1 | 0 | 1 | 0 | network failure (Tier A finding recorded) |
| rvlinks | 1 | 1 | 0 | 0 | content-enhancement, not a bug |
| mw-dev | 1 | 0 | 0 | 1 | already resolved in thread |
| **Total** | **62 triaged** | **~24 posted** | **~10 Tier A** | **~8 already-fixed** | **~18 skipped/network** |

---

## New Tier A bugs discovered (agent-fixable with local source)

These were not in the original Tier A list and should be queued for the text-correction-pr skill:

| Issue | Dict | Fix | Size |
|---|---|---|---|
| [csl-orig #2824](https://github.com/sanskrit-lexicon/csl-orig/issues/2824) | LRV | Add `<h>` homonymy discriminators to lines 26971 and 26980 in `v02/lrv/lrv.txt` (both `k1=fjvI`/`k2=fjvI` with no `<h>N`) | 2 lines |
| [csl-orig #1060](https://github.com/sanskrit-lexicon/csl-orig/issues/1060) | MW | Merge stub L>1308 (body-less) with continuation L>1309 in mw.txt lines 4777–4782 | ~6 lines |
| [COLOGNE #430](https://github.com/sanskrit-lexicon/COLOGNE/issues/430) | SHS | Fix k1/k2 metaline inconsistency: 844 metalines have `k2=...(` where k1 is truncated at `(` — deterministic strip-at-paren rule | 844 lines |
| [COLOGNE #331](https://github.com/sanskrit-lexicon/COLOGNE/issues/331) | CAE | Add `v.` to caeab_input.txt — 425 `<ab>v.</ab>` occurrences in cae.txt have no expansion entry | 1 line |
| [COLOGNE #179](https://github.com/sanskrit-lexicon/COLOGNE/issues/179) | INM | Truncated k1/k2 at inm.txt line 30302 — `Khastta-rAkzasa` key truncated to `Khastta` | 1 line |
| [COLOGNE #181](https://github.com/sanskrit-lexicon/COLOGNE/issues/181) | SHS | 840 metalines with `<k2>...(` bracket-closure truncation (subset of #430 pattern) | 840 lines |
| [csl-devanagari #27](https://github.com/sanskrit-lexicon/csl-devanagari/issues/27) | SCH | 4 double-space instances in `csl-orig/v02/sch/sch.txt` (k2 conversion issue already resolved) | 4 lines |
| [csl-ldev #12](https://github.com/sanskrit-lexicon/csl-ldev/issues/12) | SKD | SKD entry L=22342 (`pfzadAjyaM`) missing Sāyaṇa attribution — agent-fixable in csl-orig/v02/skd/skd.txt | ~1 line |
| [MWS #86](https://github.com/sanskrit-lexicon/MWS/issues/86) | MW | `&c.` needs `<ab>&c.</ab>` wrapping — mechanically fixable but **blocked** on source-vs-display editorial decision from 2021 | bulk |
| [csl-app #38](https://github.com/sanskrit-lexicon/csl-app/issues/38) | — | Dart accent toggle logic bug — pure code fix, no server needed; **not posted** (network failure) |  |

---

## Already-fixed (ready to close)

| Issue | Repo | Evidence |
|---|---|---|
| [COLOGNE #273](https://github.com/sanskrit-lexicon/COLOGNE/issues/273) | COLOGNE | PHP `%F1` → `\xf1` fix confirmed in csl-websanlexicon |
| [COLOGNE #122](https://github.com/sanskrit-lexicon/COLOGNE/issues/122) | COLOGNE | `L=8908` pseudo-headword cleaned in source; live XML may be stale |
| [AP90 #6](https://github.com/sanskrit-lexicon/AP90/issues/6) | AP90 | `funderburkjim` confirmed fix in basicadjust.php 2021; reporter confirmed |
| [BEN #7](https://github.com/sanskrit-lexicon/BEN/issues/7) | BEN | `oM` encoding fixed in csl-devanagari/v02/ben/ben.txt |
| [GreekInSanskrit #13](https://github.com/sanskrit-lexicon/GreekInSanskrit/issues/13) | GreekInSanskrit | 0 occurrences of broken `<lang n="greek">α</lang>):` pattern |
| [hwnorm1 #15](https://github.com/sanskrit-lexicon/hwnorm1/issues/15) | hwnorm1 | sqlite auto-build now integrated |
| [hwnorm1 #1](https://github.com/sanskrit-lexicon/hwnorm1/issues/1) | hwnorm1 | `dArddura` fix in YAT source 2020-01-20 |
| [csl-devanagari #4](https://github.com/sanskrit-lexicon/csl-devanagari/issues/4) | csl-devanagari | `drdhaval2785` posted "Resolved." 2021-09-03 |
| [mw-dev #18](https://github.com/sanskrit-lexicon/mw-dev/issues/18) | mw-dev | Thread ends "Pushed the update now." 2023-02 |

---

## Display/server layer (Tier D) — confirmed not source bugs

Comments posted with Tier D confirmation (no source fix possible):

| Issue | Repo | Bug class | Detail |
|---|---|---|---|
| [COLOGNE #379](https://github.com/sanskrit-lexicon/COLOGNE/issues/379) | COLOGNE | display-rendering | Web-font loading latency; no source defect |
| [COLOGNE #370](https://github.com/sanskrit-lexicon/COLOGNE/issues/370) | COLOGNE | display-rendering | RV file-not-found; display/server layer |
| [COLOGNE #254](https://github.com/sanskrit-lexicon/COLOGNE/issues/254) | COLOGNE | display-rendering | AP90 subheadword indentation; source correct at line 1 |
| [COLOGNE #109](https://github.com/sanskrit-lexicon/COLOGNE/issues/109) | COLOGNE | broken-link | Server-hosted static HTML only; no git-tracked source |
| [COLOGNE #75](https://github.com/sanskrit-lexicon/COLOGNE/issues/75) | COLOGNE | search-broken | Hyphenated-word search; `querymodel.php` matchkey() fix |
| [csl-ldev #8](https://github.com/sanskrit-lexicon/csl-ldev/issues/8) | csl-ldev | display-rendering | Vedic accent `^`/`\` rendering; PWG source correct |
| [csl-ldev #17](https://github.com/sanskrit-lexicon/csl-ldev/issues/17) | csl-ldev | source-error | Encoding convention; needs editorial decision first |
| [csl-websanlexicon #73](https://github.com/sanskrit-lexicon/csl-websanlexicon/issues/73) | csl-websanlexicon | display-rendering | Phonetic keyboard JS intercepting AE/MWE/BOR keystrokes |
| [csl-apidev #34](https://github.com/sanskrit-lexicon/csl-apidev/issues/34) | csl-apidev | display-rendering | List-mode input widget; frontend only |
| [MWS #61](https://github.com/sanskrit-lexicon/MWS/issues/61) | MWS | display-rendering | PDF in Firefox; intermittent browser issue |
| [rvlinks #3](https://github.com/sanskrit-lexicon/rvlinks/issues/3) | rvlinks | content-enhancement | 921 verses missing Russian, 72 missing English, 61 missing German |

---

## Not posted — Tier D without concrete source data (no comment warranted)

| Issue | Reason |
|---|---|
| [COLOGNE #349](https://github.com/sanskrit-lexicon/COLOGNE/issues/349) | Source correct; Advanced Search display — browser-side; couldn't reproduce |
| [COLOGNE #300](https://github.com/sanskrit-lexicon/COLOGNE/issues/300) | PDF browser compatibility; display layer only |
| [csl-ldev #9](https://github.com/sanskrit-lexicon/csl-ldev/issues/9) | Vedic accent ambiguity (^ used for 2 systems); fundamental encoding design |
| [csl-websanlexicon #15](https://github.com/sanskrit-lexicon/csl-websanlexicon/issues/15) | Title already updated; remaining items are display/font; mixed |
| [COLOGNE #180](https://github.com/sanskrit-lexicon/COLOGNE/issues/180) | Original apIcya bug already fixed; systematic IAST/Dev comparison = ongoing |
| [COLOGNE #178](https://github.com/sanskrit-lexicon/COLOGNE/issues/178) | 11 missing MW72 alternate keys confirmed locally; **needs fix-approach decision** |
| [csl-orig #2857](https://github.com/sanskrit-lexicon/csl-orig/issues/2857) | Missing cakra diagram tables; PNG scan needed for reconstruction |
| [csl-orig #2854](https://github.com/sanskrit-lexicon/csl-orig/issues/2854) | Unknown `<ab n="???">M. or N.</ab>` — needs Macdonell print verification |
| [csl-orig #1617](https://github.com/sanskrit-lexicon/csl-orig/issues/1617) | `<e>` value bugs: specific triggering instance already fixed; broader sweep = Tier D |
| [csl-orig #613](https://github.com/sanskrit-lexicon/csl-orig/issues/613) | `^` marks cleaned up (0 remaining); `<sup>` vs `<F>` = structural redesign |
| [csl-orig #174](https://github.com/sanskrit-lexicon/csl-orig/issues/174) | Feature/enhancement (anubandha markers in SKD HWs); not a bug |
| [WIL #14](https://github.com/sanskrit-lexicon/WIL/issues/14) | Server-side HTTP 500 on WILScan/web/ path; not in git-tracked source |
| [DCS #1](https://github.com/sanskrit-lexicon/DCS/issues/1) | External server (Heidelberg kjc-fs-cluster); 2014 issue |
| [GRA #22](https://github.com/sanskrit-lexicon/GRA/issues/22) | Mislabeled — is a feature request for RV sūkta display format |
| [alternateheadwords #15](https://github.com/sanskrit-lexicon/alternateheadwords/issues/15) | Scholarly design discussion (parini vs pariRi); 2016 thread, no open action |
| [PWK #6](https://github.com/sanskrit-lexicon/PWK/issues/6) | Jim explicitly deferred corrections in 2014; scholarly discussion not a bug |
| [VCP #29](https://github.com/sanskrit-lexicon/VCP/issues/29) | Reporter: "should not venture into it anytime soon"; 28 double-spaces in 290k-line file |
| [VCP #19](https://github.com/sanskrit-lexicon/VCP/issues/19) | Data quality discussion; ~200 lines from Tirupati digitization; no single fix |
| [PWG #199](https://github.com/sanskrit-lexicon/PWG/issues/199) | Active thread (2026-06-24); Andhrabharati + drdhaval2785 working it |
| [csl-devanagari #32](https://github.com/sanskrit-lexicon/csl-devanagari/issues/32) | Active thread (2026-06-26) |

---

## Network failures — need re-run

These agents hit TLS handshake timeouts and could not post (GitHub connectivity was intermittent):

| Issue | Repo | Finding (from local grep) | Should post? |
|---|---|---|---|
| [COLOGNE #381](https://github.com/sanskrit-lexicon/COLOGNE/issues/381) | COLOGNE | search-broken (HK encoding mismatch in search suggestions) | Yes — Tier D |
| [COLOGNE #286](https://github.com/sanskrit-lexicon/COLOGNE/issues/286) | COLOGNE | unknown — could not fetch | Re-run |
| [COLOGNE #153](https://github.com/sanskrit-lexicon/COLOGNE/issues/153) | COLOGNE | display-rendering (PDF Firefox Android) | Yes — Tier D |
| [csl-devanagari #38](https://github.com/sanskrit-lexicon/csl-devanagari/issues/38) | csl-devanagari | unknown | Re-run |
| [csl-ldev #11](https://github.com/sanskrit-lexicon/csl-ldev/issues/11) | csl-ldev | unknown | Re-run |
| [csl-ldev #10](https://github.com/sanskrit-lexicon/csl-ldev/issues/10) | csl-ldev | unknown | Re-run |
| [csl-websanlexicon #25](https://github.com/sanskrit-lexicon/csl-websanlexicon/issues/25) | csl-websanlexicon | unknown | Re-run |
| [csl-apidev #21](https://github.com/sanskrit-lexicon/csl-apidev/issues/21) | csl-apidev | unknown | Re-run |
| [csl-app #38](https://github.com/sanskrit-lexicon/csl-app/issues/38) | csl-app | Dart accent toggle — **Tier A** code fix | Post when network returns |
| [csl-orig #2817](https://github.com/sanskrit-lexicon/csl-orig/issues/2817) | csl-orig | unknown | Re-run |
