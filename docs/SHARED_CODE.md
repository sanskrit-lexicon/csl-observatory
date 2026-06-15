# SHARED_CODE.md — canonical sources across the Sanskrit-Lexicon / CDSL repos

> **Reading the paths in this file.** All paths below (e.g. `csl-pywork/v02/...`,
> `WhitneyRoots/scripts/...`) are **relative to the local multi-repo clone root** — the parent
> directory that holds every Sanskrit-Lexicon / CDSL repo checked out side by side. This is a
> *working-tree map*, not a set of GitHub-resolvable links: most repos live under
> [github.com/sanskrit-lexicon](https://github.com/sanskrit-lexicon) (the `csl-*` tooling repos,
> the dictionary repos `AP`/`AP90`/`MWS`/`PWG`/`PWK`/`GRA`/…, and `sanskrit-util`), while a few
> personal projects (`WhitneyRoots`, `BookIndex`, `SamudraManthanam`, …) live under
> [github.com/gasyoun](https://github.com/gasyoun). A handful of references (`ci_templates/`,
> `coc_templates/`, `CLAUDE.md`) are root-level working-tree artifacts with no single repo home.
> Canonical home for this file: [`csl-observatory/docs/SHARED_CODE.md`](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/docs/SHARED_CODE.md).

**Purpose.** ~90 repos live under this GitHub root and many solve the *same* small problems
(transliteration, normalization keys, line-based corrections, PDF link-serving …). This file
records the **one canonical place** each shared concern should come from, so a future session
**reuses** it instead of re-implementing a 20th copy. Before writing any Sanskrit string helper,
correction applier, or dict-web endpoint, check the table below first.

> Census method (2026-06-14): grouped every `.py/.sh/.php` under the GitHub root by basename and
> by content hash. Headline duplication: `transcoder.py` = **62 copies / 7 distinct versions**,
> `digentry.py` = 170/5, `updateByLine.py` = 17 repos, `parseheadline.py` = 47/3, plus ~12
> independently hand-rolled `to_slp1`/`norm`/`form_key`/`slug`/`hwnorm` functions. To refresh,
> re-run the grouping in the appendix.

## Canonical-source map (read this first)

| # | Concern | Canonical source | Status | Rule |
|---|---|---|---|---|
| 1 | IAST ⇄ SLP1 ⇄ Devanāgarī transcode | [`sanskrit-util/`](sanskrit-util/) (**new**) | extracted, tested | `import`/require it; don't re-type the SLP1 table |
| 2 | Sanskrit normalization keys (`norm`/`nfold`/`form_key`) | [`sanskrit-util/`](sanskrit-util/) (**new**) | extracted, tested | same package; pick the documented key |
| 3 | Dict correction pipeline (`updateByLine`, `diff_to_changes*`, `make_xml`, `parseheadline`, `digentry`) | [`csl-pywork/v02/makotemplates/pywork/`](csl-pywork/v02/makotemplates/pywork/) | already shared (vendored) | copy from csl-pywork; never fork-and-edit |
| 4 | `<ls>` citation linking + verb/preverb morphology | [MWS `link_candidates.py`](MWS/mwauthorities/link_candidates/link_candidates.py) + `verbs01/` | **15 forks, no shared module** | see §4 before writing a new link-splitter |
| 5 | PHP dict-web endpoints (`getword`/`servepdf`/`serveimg`) | [`csl-websanlexicon/v02/makotemplates/web/webtc/`](csl-websanlexicon/v02/makotemplates/web/webtc/) | shared template; ~37 copies drift | fix the **template**, then regenerate |
| 6 | Repo hygiene / CI (CodeQL, dependabot, pre-commit, CoC, CONTRIBUTING) | [`ci_templates/`](ci_templates/) + `cologne-*` skills | automated | run the skill; don't hand-write per repo |
| 7 | RU translation kits (`mw_ru` / `pwg_ru`) | [`SanskritLexicography/RussianTranslation/`](SanskritLexicography/RussianTranslation/) | shared scaffold | parameterize the one kit |
| 8 | DCS corpus / morphology ingest | [VisualDCS `import_dcs_conllu.py`](VisualDCS/src/DCS-data-2026/import_dcs_conllu.py) | 5 forks | see §8 |
| 9 | Generic helpers (`levenshtein`, `compare`, `unixify`, `util_mw`) | *copied* | low priority | lift into `sanskrit-util` or a `csl-pyutil` |

---

## 1–2. Transliteration & normalization → `sanskrit-util/` (new, this session)

A single Python + JS package, behaviour-identical across the two languages (346 shared golden
vectors assert `JS == Python`; the Python is regression-locked against the
`WhitneyRoots/scripts/sanskrit_util.py` donor). Public API and "which key do I want" guidance:
[`sanskrit-util/README.md`](sanskrit-util/README.md).

| Was re-implemented in | As | Now |
|---|---|---|
| 20+ dict repos + ~50 [CORRECTIONS/dictionaries/*/transcoder.py](CORRECTIONS/dictionaries/) | `import transcoder` (Dhaval's FSM engine, 62 copies) | keep for **dict-build** work; for app code use `sanskrit-util` |
| [WhitneyRoots/scripts/sanskrit_util.py](WhitneyRoots/scripts/sanskrit_util.py) | `to_slp1`/`from_slp1`/`form_key`/`norm`/`nfold` | **donor → now a shim re-exporting the package** ✅ |
| [WhitneyRoots/reader/reader.js](WhitneyRoots/reader/reader.js) | inline `deva2iast`/`norm`/`nfold` | folded into the package (JS port) |
| [WhitneyRoots/src/utils/linguistics.js](WhitneyRoots/src/utils/linguistics.js) | `normalizeSanskrit` (lossy) / `iastToDevanagari` | folded in as `normalize_sanskrit` / `iast_to_devanagari` |
| [**BookIndex**/src/utils/linguistics.js](BookIndex/src/utils/linguistics.js) | **a direct copy of WhitneyRoots' linguistics.js** | next consumer — highest-value dedup (verbatim fork) |
| [csl-atlas/src/lib/lookup-normalize.js](csl-atlas/src/lib/lookup-normalize.js) + [scripts/lib/dict-normalize.mjs](csl-atlas/scripts/lib/dict-normalize.mjs) | own JS normalizers | **transcoders migrated** (csl-atlas PR #119); `dict-normalize` stays local (CDSL SLP1-headword-specific). (No `csl-atlas-gpu` repo exists as of 2026-06-15 — earlier mention was speculative.) |
| [GRA/vn/gra-dev/web/webtc1/transcoderjs/transcoder3.js](GRA/vn/gra-dev/web/webtc1/transcoderjs/transcoder3.js) | a JS FSM transcoder | next consumer (JS build) |
| [csl-app/lib/core/transliteration_service.dart](csl-app/lib/core/transliteration_service.dart) | **Dart** `indic_transliteration_dart` wrapper | leave as-is (Dart; no shared port) |
| [SanskritSpellCheck/detectors/slp1util.py](SanskritSpellCheck/detectors/slp1util.py) | SLP1 alphabet + confusion model | next consumer (share alphabet, keep model local) |
| [SamudraManthanam/.../morph_service.py](SamudraManthanam/web/app/services/morph_service.py), [slug.py](SamudraManthanam/web/app/services/slug.py), [corpus_builder/html_to_canonical.py](SamudraManthanam/web/corpus_builder/html_to_canonical.py) | own translit + normalize | next consumers |
| [RussianRamayana/web/transliterate_filenames.py](RussianRamayana/web/transliterate_filenames.py), [VCP/meld_regex/convert_transliteration.py](VCP/meld_regex/convert_transliteration.py), [csl-observatory/scripts/obs_t_translit_check.py](csl-observatory/scripts/obs_t_translit_check.py), [RWS-plugin/.../translit_lint.py](RWS-plugin/src/ruwritingstyles/translit_lint.py) | mixed (own / `indic_transliteration`) | next consumers |
| [ApteES/.../hwnorm1.py](ApteES/ae_saninvert/hwnorm1/hwnorm1.py), [CORRECTIONS/.../hwchk_iast.py](CORRECTIONS/dictionaries/PD/issue-108/prep/hwchk_iast.py), [csl-apidev/.../word_frequency_norm.py](csl-apidev/simple-search/wf0/word_frequency_norm.py), [IndologyScholars/keyword_filtering.py](IndologyScholars/keyword_filtering.py) | headword/key normalizers | next consumers |

The census counted **four** transliteration ecosystems in play: (a) Dhaval's `transcoder.py` FSM
(Python *and* a JS twin `transcoder3.js`), (b) `indic_transliteration` (Python; also a Dart port
in csl-app), (c) hand-rolled IAST/Devanāgarī char-maps (`linguistics.js`, `slp1util.py`, the
`*-normalize.*` files), and now (d) **`sanskrit-util`** — the canonical home for (c) and for new
app code. (a) stays for dict builds, (b) for exotic schemes, (d)-Dart stays in csl-app.

**Why a package and not "just reuse transcoder.py":** `transcoder.py` is the dictionary-build
toolchain's own vendored engine (SLP1↔Devanāgarī for XML generation). New app/normalization
code wants the small, tested, JS-mirrored key functions (`norm`/`form_key`) that `transcoder.py`
does not provide. The two coexist: `transcoder.py` for build pipelines, `sanskrit-util` for keys
and app transcode. The third option, [`indic_transliteration`](https://pypi.org/project/indic-transliteration/)
(already used in BOP, csl-apidev, CommentaryStrategies, COLOGNE/makemd), remains the right pick
when you need exotic schemes the package doesn't cover.

### The traps this package centralizes (do not re-derive these)
- `ś` = `s` + U+0301 — the **same codepoint as the acute pitch accent**. A naive "strip accents"
  pass silently deletes the sibilant. `form_key` walks back to the base letter to tell them apart.
- NFD-then-strip-combining-marks **destroys vowel length** (`ā`→`a`) and **retroflex dots**
  (`ṣ`→`s`). That is fine for `norm` (search) but **wrong for form comparison** — hence the
  separate length-preserving `form_key`.
- anusvāra (`ṃ`) vs homorganic nasal (`ṅ/ñ/ṇ/n`): folded in `form_key`/`nfold`, kept distinct on
  the exact `norm` key so `am` ≠ `an`.

### Consumer migration queue (in priority order)
1. ~~**BookIndex**~~ — **NOT APPLICABLE** (verified 2026-06-15, empirical diff). `src/utils/linguistics.js`
   is NOT a WhitneyRoots copy: it was rewritten to Russian-only helpers (`stemRussian`,
   `normalizeHeadForMatch`, `compareHeadsRu`, Leipzig-gloss parse, page clamps) with **zero Sanskrit
   transcode**. The one near-analog (`normalizeHeadForMatch`) is 35% divergent from `norm`/`normalize_sanskrit`
   over 2047 real strings (it folds Cyrillic punctuation + ё, not IAST) — a swap would break Russian search.
   The census name-match was a false positive.
2. **SanskritSpellCheck** `detectors/slp1util.py` — **BLOCKED** (verified 2026-06-15). It is **SLP1-centric**:
   SLP1 `ALPHABET`/`VOWELS`/`CONSONANTS`/`MARKS` sets, an OCR Devanāgarī→SLP1 reader, a confusion model, a
   `sanhw1` sort key, data loaders. sanskrit-util is IAST/Devanāgarī-centric and exports **none** of those
   SLP1 sets / SLP1 collation / SLP1-case-preserving normalizer, and its one overlap (`devanagari_to_slp1`)
   fails the gate (danda→space tokenization; `ळ`→`x` wrong-char). Nothing safely shareable **until sanskrit-util
   gains an SLP1-side API** (see the SLP1-gap note after this list).
3. **csl-atlas** ✅ done (PR #119): `src/lib/lookup-normalize.js` `iastToSlp1`/`slp1ToIast` now delegate to the package, **vendored as [`src/lib/sanskrit-util.js`](csl-atlas/src/lib/sanskrit-util.js)** with a drift-guard test. Behaviour-identical over 197k real lemmas except a Vedic-`L`→ḻ **bug fix**. `scripts/lib/dict-normalize.mjs` stays local (CDSL SLP1-headword normalizer, no generic equivalent). (There is **no `csl-atlas-gpu` repo** — checked sanskrit-lexicon + gasyoun + gh search 2026-06-15; the earlier "(also in csl-atlas-gpu)" was speculative and has been dropped.)
   - ⚠️ **Observable Framework gotcha** (also hits #1 BookIndex / #6 WhitneyRoots if Observable-based): vendor the JS as **`.js`, not `.mjs`** — Observable's dev server 404s `.mjs` under `src/` at runtime (the static `observable build` silently tolerates it, so it only shows up in-browser). Verify a consumer page actually loads, not just that the build exits 0.
4. **SamudraManthanam** `slug.py` + `morph_service.py` + `corpus_builder/html_to_canonical.py` — **DEFER**
   (verified 2026-06-15). Only SLP1→IAST maps cleanly (`from_slp1`, 0/168652 word-level). But `morph_service.py`
   is **Dockerized runtime** code with `indic-transliteration==2.3.56` pinned: a relative-path shim `ImportError`s
   in the container (the image copies only `web/`, not the sibling), and **sanscript must stay** (sanskrit-util has
   no Devanāgarī→SLP1 and only an approximate display-only `iast_to_devanagari`). Adopting it for one function =
   a 2nd translit lib for **zero consolidation**. Viable only after sanskrit-util gains a real Devanāgarī
   round-trip + the `ṁ`(U+1E41)→`M` handling, then sanscript can be dropped wholesale. (`slug.py` is Cyrillic→Latin
   BGN/PCGN — out of sanskrit-util scope entirely.)

> **SLP1-gap unlock (the real blocker, 2026-06-15).** The queue was built from a name/hash census; behaviour +
> deploy analysis shows the remaining JS/Py app consumers mostly need things sanskrit-util doesn't expose yet.
> sanskrit-util is **IAST/Devanāgarī-centric**; the CDSL dictionary world is **SLP1-native**. To unlock real dedup
> (SanskritSpellCheck #2, the dict-repo `hwnorm`/`word_frequency_norm` consumers, and csl-atlas's still-local
> `dict-normalize.normalizeLemma`), sanskrit-util needs an **SLP1-side API**: SLP1 alphabet/vowel/consonant sets,
> an SLP1-input `form_key`/normalizer (case-preserving), and a proper Devanāgarī⇄SLP1 round-trip. That package
> enhancement — not the per-repo swaps — is the high-value next step.
5. **RussianRamayana** `transliterate_filenames.py`; **CORRECTIONS** `hwchk_iast*.py` (×4 dicts);
   **ApteES/AP** `hwnorm1*.py`; **csl-apidev** `word_frequency_norm.py`.
6. **WhitneyRoots JS** `reader.js`/`linguistics.js` — ship an IIFE/global build of `sanskrit-util`
   so the browser readers (WhitneyRoots + BookIndex) can drop their inline copies (deferred: both
   are deployed; do it with a verified build, not a hand-edit).

---

## 3. Dict correction pipeline → already shared in `csl-pywork`

`updateByLine.py` (**84 copies / 5 variants**), `parseheadline.py` (**39 / 2**),
`diff_to_changes_dict.py` / `diff_to_changes.py`, `make_change*.py`, `make_xml.py`,
`generate_dict.sh`, `digentry.py` (170 / 5). These are **vendored copies** of the csl-pywork
makotemplates originals and follow the [csl-orig correction workflow](CLAUDE.md)
(copy → edit → copy back → XML-validate → audit change file).

**Rule:** pull the script from csl-pywork — [`v00/makotemplates/`](csl-pywork/v00/makotemplates/)
for `updateByLine.py` / `parseheadline.py`, and [`v02/`](csl-pywork/v02/) for `generate_dict.sh` /
`xmlchk_xampp.sh`. Do not fork-and-tweak per repo. Note `redo.sh` (101 copies / **97 distinct**)
and `make_xml.py` (44 / 38) are genuinely **per-issue** regeneration scripts off a shared template
— those are meant to be copied and customized, not unified.

## 4. `<ls>` citation linking + verb/preverb morphology → consolidation candidate

**15 distinct implementations** recur across PWG / PWK / MWS / GRA / AP90 / BUR / KRM / VCP / SCH:
`lsextract_all.py`, `link_prelim*.py`, `link_expand.py`, `preverb1.py` / `analyze_preverb.py` /
`mwverb.py` / `mwverbs1.py`, and the `verbs01/` dirs. All solve "split `SOURCE N,N` refs into
per-page links" or "segment preverb+root". The most-evolved copies — the de-facto canonical to
lift from — are [MWS `link_candidates.py`](MWS/mwauthorities/link_candidates/link_candidates.py)
and [MWS `link_expand.py`](MWS/mwsissues/issue182/link_expand.py) for linking, and
[PWG `verbs01/mwverb.py`](PWG/verbs01/mwverb.py) / [`preverb1.py`](PWG/verbs01/preverb1.py) for verb
morphology. **No shared module yet** — before writing another link-splitter, lift the common core
(and abstract the dict-specific `*_verb_filter_map.py`) into a `csl-pyutil` module.

## 5. PHP dict-web endpoints → fix the makotemplates source, not the copies

`getword.php` / `getwordClass.php` / `servepdf.php` / `serveimg.php` / `displaylink.php` exist
**once per dictionary** under [csl-websanlexicon/webbackup/](csl-websanlexicon/webbackup/) (40+
dicts) plus [csl-apidev](csl-apidev/getword.php) and [GRA/vn](GRA/vn/gra-dev/web/webtc/getword.php).
The JSONP-XSS / SQLi hardening done across these belongs in the **template**
[csl-websanlexicon/v02/makotemplates/web/webtc/](csl-websanlexicon/v02/makotemplates/web/webtc/)
so a regenerate propagates it. (Reminder from prior work: the "echoed-request" Semgrep rule is
taint-mode — only `htmlspecialchars`/`htmlentities` on the echoed value clears it; a whitelist or
`preg_match` guard does not.)

## 6. Repo hygiene / CI → `ci_templates/` + `cologne-*` skills (already solved)

CodeQL, dependabot, dependabot auto-merge, pre-commit, CODE_OF_CONDUCT, CONTRIBUTING, branch
protection are deployed org-wide by the `cologne-*` skills from [`ci_templates/`](ci_templates/)
(`generic-ci.yml`, `dictionary-ci.yml`, `python-tool-ci.yml`, `laravel-ci.yml`) and
[`coc_templates/`](coc_templates/), via the root `.deploy_*.py` scripts. The census still found
drift to clean up: **38 CONTRIBUTING variants, 15 codeql variants, 23 pre-commit variants, 10
auto-merge variants**. **Rule:** run the skill; never hand-write these per repo.
(CodeQL has no PHP analyzer → PHP repos use Semgrep, not a `php` CodeQL matrix.)

## 7. RU translation kits → one parameterized kit

[`SanskritLexicography/RussianTranslation/`](SanskritLexicography/RussianTranslation/) holds the
`pwg_ru` kit, scaffolded as a deliberate clone of `mw_ru`: the prompt sets are parallel
(`1_perevod` / `2_qa_sudya_opus` / `2_qa_sudya_yandexgpt` / `3_pereperevod_opus`, with `pwg_ru`
adding `4_korpus_proverka`) over one [`src/build_src.py`](SanskritLexicography/RussianTranslation/src/build_src.py).
**Also note** a stray top-level [`pwg_ru_prompts/`](pwg_ru_prompts/) at the GitHub root that
duplicates the in-repo copy — collapse it. **Rule:** consolidate the prompt sets into one
JSON+Jinja2 template framework parameterized by dictionary, rather than cloning a third kit.

## 8. DCS corpus / morphology ingest → consolidation candidate

**5 distinct ingest paths.** The de-facto canonical CoNLL-U → SQLite build is
[VisualDCS `import_dcs_conllu.py`](VisualDCS/src/DCS-data-2026/import_dcs_conllu.py), with
[`gen_dcs_lemma_summary.py`](VisualDCS/gen_dcs_lemma_summary.py) producing the lemma-frequency
table that other repos vendor. Re-ingesters to consolidate onto it:
[WhitneyRoots/scripts/dcs/extract_dcs.py](WhitneyRoots/scripts/dcs/extract_dcs.py),
[MWS `ls_L_dcs2026.py`](MWS/lexicographer_dcs/ls_L_dcs2026.py) + [`register_b_dcs.py`](MWS/papers/p3_citation_registers/register_b/register_b_dcs.py),
[csl-atlas `import-dharmamitra-morphology.py`](csl-atlas/scripts/import-dharmamitra-morphology.py),
[csl-apidev `build_wf_from_dcs.py`](csl-apidev/simple-search/wf1/build_wf_from_dcs.py) + `dcs_xref/build_xref.py`.
**Rule:** consume the VisualDCS master + `dcs_lemma_summary.json` rather than re-parsing CoNLL-U.

## 9. Generic helpers → low-priority lift

`levenshtein.py` (**6 copies**, all in VCP + COLOGNE), `util_mw.py` (**7**, the verb-pipeline dict
repos AP90/BUR/GRA/MD/PWG/PWK), `util_dump_lines.py` (**7**, same repos), `unixify.py` (2 identical),
`compare.py` (3 — actually *distinct* implementations, check before merging). Copied wholesale. Lift
`levenshtein.py` + the `verbs01/` `util_*` into a shared `csl-pyutil` (or `sanskrit-util` for string
distance) when convenient. Keep genuinely dict-specific helpers (`util_hw.py`, `util_find_nasal.py`) local.

---

## Appendix — refresh the census

```powershell
$root = "C:\Users\user\Documents\GitHub"
$exclude = '\\(\.git|node_modules|vendor|\.graymatter|dist|build|__pycache__|\.venv|venv)\\'
Get-ChildItem -Path $root -Recurse -File -Include *.py,*.sh,*.php -ErrorAction SilentlyContinue |
  Where-Object { $_.FullName -notmatch $exclude } |
  ForEach-Object { [pscustomobject]@{ Name=$_.Name; Repo=($_.FullName.Substring($root.Length+1) -split '\\')[0] } } |
  Group-Object Name |
  Where-Object { ($_.Group.Repo | Sort-Object -Unique).Count -ge 4 } |
  Sort-Object { ($_.Group.Repo | Sort-Object -Unique).Count } -Descending
```
Hash a single basename to tell vendored-identical copies from real forks:
```powershell
Get-ChildItem $root -Recurse -File -Filter transcoder.py | Get-FileHash -Algorithm MD5 | Group-Object Hash
```
