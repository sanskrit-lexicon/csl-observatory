# Cologne tooling codebase — adversarial audit: call graph + silent-failure census (August 2026)

_Created: 28-08-2026 · Last updated: 05-09-2026_

Fresh-eyes adversarial audit of the Cologne **tooling** codebase — trust nothing, read from code, not docs. Executed as [Uprava handoff H3487](https://github.com/gasyoun/Uprava/blob/main/handoffs/H3487-OxAlpha_csl-observatory_cologne-codebase-adversarial-audit_25.08.26.md); audit by OxAlpha (`opencode/z-ai/glm-5.3-flash`). Cross-references [PERFORMANCE_AUDIT_2026-07.md](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/docs/PERFORMANCE_AUDIT_2026-07.md) and [AGENT_ROADMAP.md](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/docs/AGENT_ROADMAP.md); does not blindly contradict them — every prior-audit item was re-verified against current tips (table in §6).

**Read-only pass.** The only artifact is this memo (+ its PR). No findings were "fixed" here; §7 turns the highest-yield ones into launchable gap specs.

## 1. Clone manifest (audited tips)

| Repo | Commit audited | Role |
|---|---|---|
| [csl-pywork](https://github.com/sanskrit-lexicon/csl-pywork/tree/e460545) | `e460545c98d93872b3d615027ba9d1cde7a0f35a` | Python/shell generation toolchain (45-dict pipeline) |
| [csl-orig](https://github.com/sanskrit-lexicon/csl-orig/tree/dee5a03) | `dee5a0358b694ecedf98d8911f96a45cedc9be9b` | Dictionary data + encoding/generation guard scripts + pre-commit hook |
| [csl-websanlexicon](https://github.com/sanskrit-lexicon/csl-websanlexicon/tree/45b0d30) | `45b0d30ff2df21350d543f0829400b58de74d049` | Mako template source of the public web faces (v02); PR #83 already merged |
| [csl-apidev](https://github.com/sanskrit-lexicon/csl-apidev/tree/6f1b720) | `6f1b72063f49641ca700cf62292fdce7e22c6b20` | Flat-root API/display PHP (twin-served from the websanlexicon templates) |

Local clones under `GitHub/`, fetched and fast-forwarded to `origin/main` before the audit; the two initially-behind clones (websanlexicon, apidev) were updated precisely so already-fixed defects are not re-listed. Line numbers below are valid at these pins; all links pin the commit.

**Classification legend:** `CONFIRMED` = the cited lines were read and the failure path is real as written; `SUSPECT` = real lines, but triggering depends on runtime state (schema, lock, deploy layout) — each says what to check. Classes: `swallow` (exception/notice suppressed, execution proceeds) · `exitcode` (status of a stage/validator never checked) · `destroy` (previous good output deleted/truncated before replacement is validated) · `blank200` (error rendered as a normal HTTP-200 page/body) · `encode` (BOM/UTF-8/key1-key2 metaline hazard) · `scan` (unbounded linear work per request/hot loop) · `input` (unvalidated parameter silently falls back) · `sql` (string-concatenated SQL).

## 2. Reconstructed call graph — csl-pywork (from code)

Repo-level shell orchestration:

- `redo.sh` → per-dict `*Scan/2020/pywork/redo_hw.sh` + `redo_xml.sh` (v00 lane; [redo.sh:54-59](https://github.com/sanskrit-lexicon/csl-pywork/blob/e460545/redo.sh))
- `v02/redo_xampp_selective.sh` → [redo_xampp_selective.py](https://github.com/sanskrit-lexicon/csl-pywork/blob/e460545/v02/redo_xampp_selective.py) → `git pull` ×7 siblings → `sh generate_dict.sh <dict> ../../<dict>` → cologne-stardict/stardict-sanskrit/csl-json/csl-homepage scripts (by name, inside sibling repos)
- `v02/redo_cologne_all.sh` / `redo_xampp_all.sh` → `generate_dict.sh` ×41 hardcoded dicts
- `v02/regenerate-hwnorm1-sqlite.sh` → 6 pulls → redo chains → 3 pushes; `v02/refresh_csl.sh` → 13 pulls; `v02/xmlchk_xampp.sh` → a **server-tree copy** of `xmlvalidate.py`, not this repo's `v02/utilities/` one
- CI: [.github/workflows/xml-parse.yml](https://github.com/sanskrit-lexicon/csl-pywork/blob/e460545/.github/workflows/xml-parse.yml) checks out csl-orig + csl-websanlexicon and runs `generate_dict.sh mci` — the **only** CI exercise of the real pipeline, one dictionary

`generate_dict.sh` stage decomposition (the core):

`generate_dict.sh` → `generate_orig.sh` → `generate.py <dict> … ../../csl-orig/v02/<dict>` → `generate_pywork.sh` → `generate.py … makotemplates distinctfiles/<dict>` → `generate_ab_bib_ls.sh` → **csl-websanlexicon** `v02/generate_web.sh` → `<outdir>/pywork/redo_hw.sh` (`hw.py`/`hw2.py`/`hw0.py` → `hwparse` → `parseheadline`) → `redo_xml.sh` (`make_xml.py` → `xmllint` advisory → `redo_postxml.sh`) → `redo_postxml.sh` → `sqlite/redo.sh` (`sqlite.py`) + `webtc2/redo.sh` (`init_query.py` → `query_dump.txt`) + dict-conditional ab/bib/auth `redo` scripts → `downloads/redo_all.sh` (txt/xml/web zips).

Notable non-calla: `updateByLine.py` is invoked by **no script in the repo** (manual CLI / vendored into dictionary repos per docs/GENERATION_MANUAL.md); `digentry.py` appears in neither inventory — dead in the v02 lane despite the README. Tests cover `dictparms.py`, `updateByLine.py`, `redo_xampp_selective.py` — **zero** tests cover the production core (`make_xml.py`, `hw*.py`, `hwparse.py`, `sqlite.py`, `sqlite_txt.py`, `init_query.py`, `xmlvalidate.py`, `generate.py`), and `.coveragerc` omits `makotemplates/**` + `utilities/**`, so the "70% coverage" CI gate effectively measures `dictparms.py` alone.

## 3. Reconstructed call graph — csl-orig build/validation scripts

- [scripts/install-hooks.sh](https://github.com/sanskrit-lexicon/csl-orig/blob/dee5a03/scripts/install-hooks.sh) → symlinks `hooks/pre-commit` into `.git/hooks/` — **opt-in**; a fresh clone has only `pre-commit.sample` (verified in the audited clone: the entire guard is dormant unless installed)
- `hooks/pre-commit` → stage 1 [scripts/check_encoding.py](https://github.com/sanskrit-lexicon/csl-orig/blob/dee5a03/scripts/check_encoding.py) (BOM / invalid-UTF-8 / `<L>`≠`<LEND>` on canonical `v02/<dict>/<dict>.txt`) → stage 2 [scripts/check_generate_dict.sh](https://github.com/sanskrit-lexicon/csl-orig/blob/dee5a03/scripts/check_generate_dict.sh) → **csl-pywork** `v02/generate_dict.sh` via relative sibling path `../csl-pywork/v02` (hard-fails closed if absent — the one loud guard)
- `scripts/check_generate_dict.sh` failure channel = **ANSI red-line grep** on captured output (`grep -F $'\033[31m'`); the pipeline's exit status is discarded (`|| true`)
- CI mirrors: `encoding-guard.yml` (scan-all), `generate-dict.yml`
- key1/key2: **no in-repo validation tooling at all** — `v02/<dict>/{althws,update,…}/*.py` are historical one-off transformation scripts, wired into nothing. Metaline parsing lives transitively in csl-pywork `hw.py`/`hwparse.py`/`parseheadline.py`; org-level normalization in hwnorm1/hwnorm2. A committer without the hook installed has zero key1/key2 validation anywhere in the loop.
- `reorg/reorg1_all.sh` → `sh reorg1.sh <dict>` ×34 — see O8-O9 (broken as shipped)

## 4. Reconstructed call graph — csl-websanlexicon v02 templates (per-request)

Generated copies under `v02/distinctfiles/**` (46 dict dirs) are build output; the hand-maintained surface is `v02/makotemplates/web/**`:

- **Entry A (basic display):** [indexcaller.php](https://github.com/sanskrit-lexicon/csl-websanlexicon/blob/45b0d30/v02/makotemplates/web/webtc/indexcaller.php) → `parm.php` (`Parm` → `dictcode.php` → `DictInfo` → `transcoder.php`) → JS GET [getword.php](https://github.com/sanskrit-lexicon/csl-websanlexicon/blob/45b0d30/v02/makotemplates/web/webtc/getword.php) → `getwordClass.php` → `getword_data.php` (`Dal` → `dal.php`; `get1_mwalt` → keydoc fast path or `get1_mwalt_prev` gap-fill loops; `BasicAdjust` (`basicadjust.php`, ~4700 lines; `getABdata` → `dal->getgeneral`; per-`<ls>` abbr queries) → `BasicDisplay` (`basicdisplay.php`, expat `xml_parse`)) → `dispitem.php` → transcode → JSONP/HTML
- **Entry B (list):** `webtc1/index.php` → `listhier.php` → `ListParm` → `ListHierModel` (`list1a/b` → dal) → `ListHierView`; `disphier.php` re-enters Entry A
- **Entry C (advanced search):** `webtc2/index.php` → [query.php](https://github.com/sanskrit-lexicon/csl-websanlexicon/blob/45b0d30/v02/makotemplates/web/webtc2/query.php) → `queryparm.php` → [querymodel.php](https://github.com/sanskrit-lexicon/csl-websanlexicon/blob/45b0d30/v02/makotemplates/web/webtc2/querymodel.php) (`openfile` on `query_dump.txt`; `matchkey`/`smatchkey` fgets loops); POST `query_gather1.php` → one full `GetwordClass` per key
- **Entry D (scans):** `servepdf.php` → `servepdfClass.php` → `pdffiles.txt` linear scan → `DictInfo::get_pdfpages_url` → `dictinfowhich.php` map
- **Entry E (mobile):** `mobile1/index.php` → same `getword.php` endpoint. `security_headers.php` required at every entry.

## 5. Reconstructed call graph — csl-apidev (per-request)

Flat-root; endpoints → class files → `dal.php`:

- [getword.php](https://github.com/sanskrit-lexicon/csl-apidev/blob/6f1b720/getword.php) → `getwordClass.php` → `getword_data.php` → `Dal` (`dal.php`) + `BasicAdjust` (opens 2 more Dal handles: `"ab"`, `"bib"`/`"authtooltips"`) + `BasicDisplay` → `dispitem.php`
- [getword_xml.php](https://github.com/sanskrit-lexicon/csl-apidev/blob/6f1b720/getword_xml.php) → `getwordXmlClass.php` → transcoder/dal/parm/`accent_adjust.php`/`basic_xml_html.php`
- `getsuggest.php` → `getsuggestClass.php` (`get3a`, `get1`); `getword_batch.php` → up to 200 × full `GetwordClass` per request; `api_trial.php` → up to 34 × `GetwordXmlClass` for `dict=all`; `listview.php` → `getword.php` + `listhier.php` → `listhierClass.php`; `dalglob.php` → `dalglobClass.php`; `cleanurl.php` → `api1/salt_common.php`
- `servepdf.php` → `servepdfClass.php` (api mode + hardened `getImagefiles`, twin of the simple websanlexicon variant)
- `htmlwork/makeassets/*.php` generators `require_once("../../web/webtc/disp.php")` — a path that **does not exist** in this flat repo (legacy Cologne-layout offline tools; dead code, see A-note below) — and produce the `key1⇥L⇥<info>…` lines that `dal.php` reads and `dispitem.php` parses
- Vendored: `phpQuery-onefile.php` v0.9.5 (~2010 vintage) — noted, not audited

## 6. Silent-failure census

71 candidate sites were surveyed; the 71st is the enabling layer itself (A1). All rows have `file:line` evidence at the pinned commits.

### 6a. csl-pywork (P1-P21)

| ID | file:line | class | verdict | failure scenario |
|---|---|---|---|---|
| P1 | [redo_xml.sh:13-21](https://github.com/sanskrit-lexicon/csl-pywork/blob/e460545/v02/makotemplates/pywork/redo_xml.sh#L13-L21) | exitcode | CONFIRMED | DTD-invalid XML is printed red, then the pipeline immediately builds sqlite/query_dump/downloads from it — the single validation gate in the whole pipeline is advisory (no `set -e`, no exit) |
| P2 | [xmlvalidate.py:18-27](https://github.com/sanskrit-lexicon/csl-pywork/blob/e460545/v02/utilities/xmlvalidate.py#L18-L27) | exitcode | CONFIRMED | Standalone validator prints "Problem validating" and falls off the end → **exit 0**. `xmlchk_xampp.sh:12` claims "Exits with a non-zero status if validation fails" — the code cannot do that |
| P3 | [make_xml.py:1352-1382](https://github.com/sanskrit-lexicon/csl-pywork/blob/e460545/v02/makotemplates/pywork/make_xml.py#L1352-L1382) | swallow+exitcode | CONFIRMED | Malformed records counted, written into `<dict>.xml` anyway, one WARNING line, exit 0. If xmllint is absent (documented common), that one line is the only signal |
| P4 | [make_xml.py:1326](https://github.com/sanskrit-lexicon/csl-pywork/blob/e460545/v02/makotemplates/pywork/make_xml.py#L1326) (+ raise at :676) | destroy | CONFIRMED | Output opened `'w'` before the record loop; a mid-loop crash truncates the previous good `<dict>.xml` and leaves half-written XML — and the caller ignores the exit (P5), so downstream stages build from the corpse |
| P5 | [generate_dict.sh:41-148](https://github.com/sanskrit-lexicon/csl-pywork/blob/e460545/v02/generate_dict.sh) | exitcode | CONFIRMED | All four stage invocations capture output via `$(…)` and never inspect `$?`; a dead stage only reprints text, execution falls through to the next stage on a half-assembled tree |
| P6 | [generate.py:184-189](https://github.com/sanskrit-lexicon/csl-pywork/blob/e460545/v02/generate.py#L184-L189) | destroy | CONFIRMED | `C` category copies with no try/except (the `CD` branch exits 1): a missing source file crashes generation mid-inventory, leaving `pywork/` partially populated — with P5 the pipeline keeps running |
| P7 | [generate.py:58-65](https://github.com/sanskrit-lexicon/csl-pywork/blob/e460545/v02/generate.py#L58-L65) | swallow | CONFIRMED | `except Exception: pass` around `os.makedirs` swallows permission errors too → silently empty generation target |
| P8 | [sqlite_txt.py:211-215](https://github.com/sanskrit-lexicon/csl-pywork/blob/e460545/v02/makotemplates/pywork/sqlite/sqlite_txt.py#L211-L215) | swallow+exitcode | CONFIRMED | Tab-count mismatch → row silently dropped, exit 0; built abbreviation/tooltip/bib sqlite is short rows with no signal the callers gate on |
| P9 | [sqlite/redo.sh:4-6](https://github.com/sanskrit-lexicon/csl-pywork/blob/e460545/v02/makotemplates/pywork/sqlite/redo.sh) + [sqlite.py:137](https://github.com/sanskrit-lexicon/csl-pywork/blob/e460545/v02/makotemplates/pywork/sqlite/sqlite.py#L137) | destroy+exitcode | CONFIRMED | Old `<dict>.sqlite` removed before parse; on parse failure (`sqlite.py` exits 1) `redo.sh` has no `set -e` → the **stale** sqlite stays in `web/sqlite/` while `<dict>.xml` is already new — web display silently disagrees with the XML |
| P10 | [init_query.py:22-57](https://github.com/sanskrit-lexicon/csl-pywork/blob/e460545/v02/makotemplates/pywork/webtc2/init_query.py#L22-L57) | destroy | CONFIRMED | `keysanskrit` initialized only inside the first matching branch; zero regex matches → `NameError` after the output file is open → empty/partial `query_dump.txt`, which `webtc2/redo.sh` (no `set -e`) ships anyway |
| P11 | [init_query.py:58](https://github.com/sanskrit-lexicon/csl-pywork/blob/e460545/v02/makotemplates/pywork/webtc2/init_query.py#L58) | swallow | CONFIRMED | `fpout.write("prevkey :: keysanskrit\tkeydata\n")` — a plain string literal (lost `%` formatting) appends a junk data row to every shipped `query_dump.txt` |
| P12 | [downloads/redo_txt.sh:5-19](https://github.com/sanskrit-lexicon/csl-pywork/blob/e460545/v02/makotemplates/downloads/redo_txt.sh) (same in redo_xml/redo_web) | destroy+exitcode | CONFIRMED | Old zip deleted before inputs are copied; missing input or absent `zip` binary → **no public download archive**, no gating (callers ignore status, P13) |
| P13 | [downloads/redo_all.sh:2-32](https://github.com/sanskrit-lexicon/csl-pywork/blob/e460545/v02/makotemplates/downloads/redo_all.sh) + [redo_postxml.sh](https://github.com/sanskrit-lexicon/csl-pywork/blob/e460545/v02/makotemplates/pywork/redo_postxml.sh) | exitcode | CONFIRMED | Every postxml/downloads sub-stage is `output=$(sh … 2>&1)` fire-and-forget; any failure does not stop the next |
| P14 | [refresh_csl.sh:6-39](https://github.com/sanskrit-lexicon/csl-pywork/blob/e460545/v02/refresh_csl.sh) | exitcode | CONFIRMED | 12 × `git pull` with no `set -e`/status checks; a failed pull on repo 3 is indistinguishable from success while the remaining pulls still "update" |
| P15 | [regenerate-hwnorm1-sqlite.sh:79-124](https://github.com/sanskrit-lexicon/csl-pywork/blob/e460545/v02/regenerate-hwnorm1-sqlite.sh#L79-L124) | exitcode | CONFIRMED | `git diff --quiet` sees only tracked files: brand-new generated files yield "No changes to commit" and are never pushed — hwnorm1/hwnorm2/apidev silently stale despite a green run |
| P16 | [cologne_test.sh:25-58](https://github.com/sanskrit-lexicon/csl-pywork/blob/e460545/v02/cologne_test.sh#L25-L58) | input | CONFIRMED | For any post-2014 dict (armh, pwkvn, lrv, abch, acph, acsj, fri, nmmb) `dictyear` stays `0` → diff runs against a nonexistent `XXXScan/0` path and the "test" reports the error text as its diff-count |
| P17 | [redo.sh:54-59](https://github.com/sanskrit-lexicon/csl-pywork/blob/e460545/redo.sh) | input+exitcode | CONFIRMED | Typo'd dict code fails `cd "$dict"Scan/2020/pywork/`, loop continues, `sh redo_hw.sh` runs in the wrong directory — no aggregate failure signal |
| P18 | [make_xml.py:1336-1338](https://github.com/sanskrit-lexicon/csl-pywork/blob/e460545/v02/makotemplates/pywork/make_xml.py#L1336-L1338) | swallow | CONFIRMED | Dead-debug guard `if ihwrec > 1000000: print("debug stopping"); break` still live — a future >1M-headword dictionary silently truncates, exit 0 |
| P19 | [make_xml.py:926-933](https://github.com/sanskrit-lexicon/csl-pywork/blob/e460545/v02/makotemplates/pywork/make_xml.py#L926-L933) | swallow | CONFIRMED | abch/acph/acsj/nmmb path: malformed `<eid>` becomes an XML comment, non-matching syns silently dropped — data loss recorded only as an embedded comment |
| P20 | [hw.py:95](https://github.com/sanskrit-lexicon/csl-pywork/blob/e460545/v02/makotemplates/pywork/hw.py#L95) vs [make_xml.py:1321](https://github.com/sanskrit-lexicon/csl-pywork/blob/e460545/v02/makotemplates/pywork/make_xml.py#L1321) | encode | SUSPECT | BOM handling inconsistent: `hw.py` reads `utf-8-sig`, `make_xml.py`/`hwparse.py`/`sqlite*.py`/`updateByLine.py` plain `utf-8`. Harm currently contained by metaline layout; one refactor away from silent first-record corruption. Check: feed a BOM'd `xxxhw.txt` through `redo_hw.sh` |
| P21 | [parseheadline.py:20-26](https://github.com/sanskrit-lexicon/csl-pywork/blob/e460545/v02/makotemplates/pywork/parseheadline.py#L20-L26) | encode | SUSPECT | `<`/`>` inside a headword or metadata value silently truncates that key's value (regex split); `hw.py` catches missing keys, not truncated ones. Check: a `<k1>a<b>c</k1>` metaline |

### 6b. csl-orig build scripts (O1-O9)

| ID | file:line | class | verdict | failure scenario |
|---|---|---|---|---|
| O1 | [check_generate_dict.sh:69](https://github.com/sanskrit-lexicon/csl-orig/blob/dee5a03/scripts/check_generate_dict.sh#L69) | exitcode | CONFIRMED | `pipeline_output=$(… sh generate_dict.sh … 2>&1) \|\| true` — a pipeline that dies with **no** ANSI-red output yields "OK: no red lines" and the commit passes with nothing validated |
| O2 | csl-pywork [generate_dict.sh:62,76,143,148](https://github.com/sanskrit-lexicon/csl-pywork/blob/e460545/v02/generate_dict.sh) | exitcode | CONFIRMED | The failure channel the hook depends on is incomplete: `cd` errors and the `redo_postxml.sh`/`downloads/redo_all.sh` stages print raw, never red — so O1's gate cannot see them |
| O3 | [hooks/pre-commit:21](https://github.com/sanskrit-lexicon/csl-orig/blob/dee5a03/hooks/pre-commit#L21) | exitcode | CONFIRMED | `--diff-filter=ACM`: **deleting or renaming** `v02/<dict>/<dict>.txt` runs neither stage; any `git diff` failure is `|| true`-swallowed to empty → exit 0 |
| O4 | [check_encoding.py:41-51](https://github.com/sanskrit-lexicon/csl-orig/blob/dee5a03/scripts/check_encoding.py#L41-L51) | swallow | CONFIRMED | `if os.path.exists(p)` silently skips a missing canonical file (count just shrinks); deletion + O3 = the loss is invisible to every gate |
| O5 | [check_encoding.py:71](https://github.com/sanskrit-lexicon/csl-orig/blob/dee5a03/scripts/check_encoding.py#L71) | exitcode | CONFIRMED | `if nLEND and nL != nLEND` — a file with zero `<LEND>` lines passes vacuously (`nLEND=0` short-circuits). Currently no file triggers it; the hole is structural |
| O6 | [check_encoding.py:55](https://github.com/sanskrit-lexicon/csl-orig/blob/dee5a03/scripts/check_encoding.py#L55) + [hooks/pre-commit:14-15](https://github.com/sanskrit-lexicon/csl-orig/blob/dee5a03/hooks/pre-commit#L14-L15) | swallow | CONFIRMED | Both stages validate **worktree** bytes, never the staged blob (`git show :v02/…` used nowhere) — `git add -p` partial staging commits bytes that were never checked |
| O7 | [check_generate_dict.sh:54-69](https://github.com/sanskrit-lexicon/csl-orig/blob/dee5a03/scripts/check_generate_dict.sh#L54-L69) | destroy | CONFIRMED | A mere `git commit` regenerates the downstream sibling install `../<dict>/{orig,pywork,web,downloads}`; on failure the half-regenerated sibling stays dirty — validation mutates before verdict |
| O8 | [reorg/reorg1.sh:2](https://github.com/sanskrit-lexicon/csl-orig/blob/dee5a03/reorg/reorg1.sh#L2) + [reorg1_all.sh:7](https://github.com/sanskrit-lexicon/csl-orig/blob/dee5a03/reorg/reorg1_all.sh#L7) | exitcode | CONFIRMED | `${dictlo^^}` bashism invoked via `sh` → "bad substitution" on every iteration; loop (no `set -e`) grinds through all 34 dicts failing. Live-tested on macOS this pass |
| O9 | [reorg/reorg1.sh:3-7](https://github.com/sanskrit-lexicon/csl-orig/blob/dee5a03/reorg/reorg1.sh#L3-L7) | destroy+input | CONFIRMED | `cd ../` assumes cwd = `reorg/` (from repo root it lands in the repo's **parent**); `mkdir` runs before source validation; `v00/csl-data/...` source no longer exists → `mv` fails, stray empty dir remains, exit 0 |
| O10 | [scripts/install-hooks.sh:29](https://github.com/sanskrit-lexicon/csl-orig/blob/dee5a03/scripts/install-hooks.sh#L29) | swallow | CONFIRMED | Absolute symlink breaks when the clone moves; git silently skips a missing hook. State today: hooks **not installed** in the audited clone — the whole safety layer is dormant, and `--no-verify` always bypasses |

### 6c. csl-websanlexicon v02 templates (W1-W14)

| ID | file:line | class | verdict | failure scenario |
|---|---|---|---|---|
| W1 | [querymodel.php:35-40](https://github.com/sanskrit-lexicon/csl-websanlexicon/blob/45b0d30/v02/makotemplates/web/webtc2/querymodel.php#L35-L40) | blank200 | CONFIRMED | Missing `query_dump.txt` → errmsg echoed by `query.php:19` as page body with **HTTP 200**; error looks like success |
| W2 | [getword_data.php:124-134](https://github.com/sanskrit-lexicon/csl-websanlexicon/blob/45b0d30/v02/makotemplates/web/webtc/getword_data.php#L124-L134), [:193](https://github.com/sanskrit-lexicon/csl-websanlexicon/blob/45b0d30/v02/makotemplates/web/webtc/getword_data.php#L193) | blank200 | CONFIRMED | Malformed MW page-ref → `exit(1)` mid-JSON → truncated/empty response, HTTP 200 (headers already sent) |
| W3 | [dal.php:589-591](https://github.com/sanskrit-lexicon/csl-websanlexicon/blob/45b0d30/v02/makotemplates/web/webtc/dal.php#L589-L591) | swallow | SUSPECT | `getgeneral` prepare/execute with no try/catch under ERRMODE_EXCEPTION → schema mismatch or locked DB = uncaught PDOException = blank 500. Check: rename the authtooltips table in a scratch copy |
| W4 | [basicadjust.php:382-384](https://github.com/sanskrit-lexicon/csl-websanlexicon/blob/45b0d30/v02/makotemplates/web/webtc/basicadjust.php#L382-L384) | sql | SUSPECT | `… where $fieldname LIKE '$key1'` — `$key1` interpolated raw (data-derived, second-order, from `<ls>` XML body, not user); uncaught throw on error |
| W5 | [servepdfClass.php:15,107,152-154](https://github.com/sanskrit-lexicon/csl-websanlexicon/blob/45b0d30/v02/makotemplates/web/webtc/servepdfClass.php) | input+swallow | CONFIRMED | Missing `page` param + missing `pdffiles.txt` (`file()` → false, warning suppressed) → silent fallback to scan page 1, HTTP 200 |
| W6 | [dictinfo.php:174](https://github.com/sanskrit-lexicon/csl-websanlexicon/blob/45b0d30/v02/makotemplates/web/webtc/dictinfo.php#L174) | input | CONFIRMED | Dict absent from pdfpages map → null URL → broken PDF link rendered as a normal page |
| W7 | [listhiermodel.php:16](https://github.com/sanskrit-lexicon/csl-websanlexicon/blob/45b0d30/v02/makotemplates/web/webtc1/listhiermodel.php#L16) | swallow | CONFIRMED | `list($key1,$lnum1,$data1) = $matches[0];` on possibly-empty match → null destructure (notices suppressed) → `get2(null,null)` → empty list page, HTTP 200 |
| W8 | [listhiermodel.php:58-68](https://github.com/sanskrit-lexicon/csl-websanlexicon/blob/45b0d30/v02/makotemplates/web/webtc1/listhiermodel.php#L58-L68) | input | CONFIRMED | Unknown key → `$key = "a"; // sure to match` → silently renders a list centered at "a" — wrong content as success |
| W9 | [queryparm.php:104-106](https://github.com/sanskrit-lexicon/csl-websanlexicon/blob/45b0d30/v02/makotemplates/web/webtc2/queryparm.php#L104-L106) vs [index.php:113-120](https://github.com/sanskrit-lexicon/csl-websanlexicon/blob/45b0d30/v02/makotemplates/web/webtc2/index.php#L113-L120) | input | CONFIRMED | UI offers max 200/500/1000; API clamps `$max > 100 → 100` — user picks 1000, silently gets 100 |
| W10 | [querymodel.php:142-308](https://github.com/sanskrit-lexicon/csl-websanlexicon/blob/45b0d30/v02/makotemplates/web/webtc2/querymodel.php#L142-L308) | scan | CONFIRMED | Every webtc2 request linearly `fgets`-scans `query_dump.txt` from byte offset; no FTS/index exists anywhere in template tree or docs — prior-audit D4 **still open** (see §7) |
| W11 | [transcoder.php:40,328-331](https://github.com/sanskrit-lexicon/csl-websanlexicon/blob/45b0d30/v02/makotemplates/web/utilities/transcoder.php#L40) | blank200 | CONFIRMED | Missing FSM XML → `return $line` — input returned **untranscoded**: SLP1 shown inside a Devanagari page, zero error |
| W12 | [transcoder.php:180](https://github.com/sanskrit-lexicon/csl-websanlexicon/blob/45b0d30/v02/makotemplates/web/utilities/transcoder.php#L180) | swallow | CONFIRMED | PR #83's fallback cache write is `@file_put_contents(...)` — read-only `transcoder/` dir (hardened docroot) → write fails silently **every request**; the PR #83 perf win silently evaporates with no log line. Read path self-heals (`@file_get_contents`+`@unserialize` :158-159) |
| W13 | [transcoder.php:454-489](https://github.com/sanskrit-lexicon/csl-websanlexicon/blob/45b0d30/v02/makotemplates/web/utilities/transcoder.php#L454-L489) + [parm.php:74-75](https://github.com/sanskrit-lexicon/csl-websanlexicon/blob/45b0d30/v02/makotemplates/web/webtc/parm.php#L74-L75) | input | CONFIRMED | `?transLit=garbage` silently becomes `slp1`; unknown bytes pass through the FSM verbatim → wrong "translations", not errors |
| W14 | [dal.php:39-43](https://github.com/sanskrit-lexicon/csl-websanlexicon/blob/45b0d30/v02/makotemplates/web/webtc/dal.php#L39-L43) + [:91-93](https://github.com/sanskrit-lexicon/csl-websanlexicon/blob/45b0d30/v02/makotemplates/web/webtc/dal.php#L91-L93) | scan | CONFIRMED | keydoc.sqlite fast path opened **only** under `?dev=yes` → production always runs the `get1_mwalt_prev` nested gap-fill loops — prior-audit D6 **still open** (see §7) |

### 6d. csl-apidev (A1-A25)

| ID | file:line | class | verdict | failure scenario |
|---|---|---|---|---|
| A1 | [getword.php:4](https://github.com/sanskrit-lexicon/csl-apidev/blob/6f1b720/getword.php#L4) (same layer in ~16 entries: parm, basicdisplay, basicadjust, servepdf, getsuggest, listhier, listview, api0/*, transcoder…) | swallow | CONFIRMED | `error_reporting(E_ALL & ~E_NOTICE & ~E_WARNING);` — the enabling layer: every undefined index / fopen-false below is silenced request-wide |
| A2 | [dal.php:77-88](https://github.com/sanskrit-lexicon/csl-apidev/blob/6f1b720/dal.php#L77-L88) | swallow | CONFIRMED | Corrupt/missing `.sqlite` → `file_db=null, status=false`; **no caller of Getword_data checks status** → `get()` returns `[]` → "not found" rendered as a normal page |
| A3 | [dal.php:126-149](https://github.com/sanskrit-lexicon/csl-apidev/blob/6f1b720/dal.php#L126-L149), [:307-312](https://github.com/sanskrit-lexicon/csl-apidev/blob/6f1b720/dal.php#L307-L312) | swallow | CONFIRMED | Any PDOException in `get`/`get_xml`/`get3c_helper` → silently empty array → blank result, HTTP 200 |
| A4 | [dal.php:634-636](https://github.com/sanskrit-lexicon/csl-apidev/blob/6f1b720/dal.php#L634-L636) | swallow | CONFIRMED | `getgeneral` (xab/authtooltips) has **no** try/catch under exception mode → missing/renamed abbreviation table = uncaught PDOException = HTTP 500 blank |
| A5 | [dal.php:195-196](https://github.com/sanskrit-lexicon/csl-apidev/blob/6f1b720/dal.php#L195-L196), [:361-362](https://github.com/sanskrit-lexicon/csl-apidev/blob/6f1b720/dal.php#L361-L362) | swallow | CONFIRMED | `get3a_keydoc`/`get3b` unchecked prepare/execute → uncaught throw in the keydoc paths |
| A6 | [servepdfClass.php:50,119,341](https://github.com/sanskrit-lexicon/csl-apidev/blob/6f1b720/servepdfClass.php) | swallow | CONFIRMED | Missing `pdffiles.txt` → `file()` false (warning suppressed) → `foreach(false)` → empty `$pagearr` → line 316 `list(…) = $pagearr[$ncur]` undefined-offset **fatal**, blank |
| A7 | [servepdfClass.php:295,305,309](https://github.com/sanskrit-lexicon/csl-apidev/blob/6f1b720/servepdfClass.php) | input | CONFIRMED | PWG/GRA page not in hash → undefined index suppressed → `$ncur=null` → falls to `$ncur=1` → **wrong scan page rendered silently** |
| A8 | [servepdfClass.php:122](https://github.com/sanskrit-lexicon/csl-apidev/blob/6f1b720/servepdfClass.php#L122) | blank200 | CONFIRMED | `list($status,…)` from `getImagefiles` — `$status` never checked → page-not-found renders **page 1 scan with HTTP 200** |
| A9 | [listhierClass.php:43](https://github.com/sanskrit-lexicon/csl-apidev/blob/6f1b720/listhierClass.php#L43) | swallow | CONFIRMED | Same empty-match destructure as W7; comment at :187 claims "guaranteed" — undefined offset fatal on missing/empty sqlite |
| A10 | [listhierClass.php:38](https://github.com/sanskrit-lexicon/csl-apidev/blob/6f1b720/listhierClass.php#L38) + [getword_data.php:126-193](https://github.com/sanskrit-lexicon/csl-apidev/blob/6f1b720/getword_data.php) + [basic_xml_html.php:65-141](https://github.com/sanskrit-lexicon/csl-apidev/blob/6f1b720/basic_xml_html.php) | blank200 | CONFIRMED | Hard `exit(1)` mid-request on data anomalies → blank HTTP 200; diagnostics sit behind hardcoded-false `dbgprint(false, …)` — invisible |
| A11 | [basicdisplay.php:636](https://github.com/sanskrit-lexicon/csl-apidev/blob/6f1b720/basicdisplay.php#L636) | swallow | CONFIRMED | `<mark>` handler appends to local `$row` instead of `$this->row` → **`<mark>` section markers (skd H/P) silently never rendered** — real display bug, twin websanlexicon copy renders them correctly (drifted fix) |
| A12 | [basicdisplay.php:128-139](https://github.com/sanskrit-lexicon/csl-apidev/blob/6f1b720/basicdisplay.php#L128-L139) + [getword_data.php:96-100](https://github.com/sanskrit-lexicon/csl-apidev/blob/6f1b720/getword_data.php#L96-L100) | blank200 | CONFIRMED | Malformed record degrades to stripped text; `BasicDisplay->status=false` is **never read** by the caller → silent degradation |
| A13 | [dalglobClass.php:121](https://github.com/sanskrit-lexicon/csl-apidev/blob/6f1b720/dalglobClass.php#L121) | sql | CONFIRMED | `…where key='$keynorm'` concatenated; `parm.php:112` strips `"` but **not `'`** — injection surface; failure swallowed by false-check → silent 404 envelope |
| A14 | [basicadjust.php:382-384](https://github.com/sanskrit-lexicon/csl-apidev/blob/6f1b720/basicadjust.php#L382-L384) | sql | CONFIRMED | Same interpolated-SQL + unchecked query under exception mode → uncaught throw → 500 (second-order input) |
| A15 | [parm.php:83-88](https://github.com/sanskrit-lexicon/csl-apidev/blob/6f1b720/parm.php#L83-L88) | input | CONFIRMED | Missing `key` → **silently serves the entry for 'guru'**; also masks the servepdf empty-request path |
| A16 | [transcoder.php:426-430](https://github.com/sanskrit-lexicon/csl-apidev/blob/6f1b720/utilities/transcoder.php#L426-L430) | input | CONFIRMED | Unknown `input=`/`output=` silently coerced to slp1 (undefined-index suppressed) |
| A17 | [transcoder.php:282-284,37](https://github.com/sanskrit-lexicon/csl-apidev/blob/6f1b720/utilities/transcoder.php#L282-L284) | blank200 | CONFIRMED | Missing FSM XML → input returned untranslated, silently (apidev twin of W11) |
| A18 | [api_trial.php:122-123](https://github.com/sanskrit-lexicon/csl-apidev/blob/6f1b720/api_trial.php#L122-L123) | input | CONFIRMED | `hw`/`reg` undefined on lnum/reg routes → null key → empty result set, HTTP 200 |
| A19 | [getwordXmlClass.php:38](https://github.com/sanskrit-lexicon/csl-apidev/blob/6f1b720/getwordXmlClass.php#L38) + [getword_xml.php:31](https://github.com/sanskrit-lexicon/csl-apidev/blob/6f1b720/getword_xml.php#L31) | blank200 | CONFIRMED | not-found and dict-error reported **inside a 200 body** (`$ans['status']=404`) — no `http_response_code()` on any JSON endpoint |
| A20 | [dictinfo.php:22,60-66](https://github.com/sanskrit-lexicon/csl-apidev/blob/6f1b720/dictinfo.php#L60-L66) | input | CONFIRMED | ABCH/ACPH/ACSJ/NMMB/FRI exist in `$dictyear` but **not** in `$dictyear_older` → null year → `…Scan//web` paths → silent blank render under `version=1` |
| A21 | [getsuggestClass.php:94-96](https://github.com/sanskrit-lexicon/csl-apidev/blob/6f1b720/getsuggestClass.php#L94-L96) | blank200 | CONFIRMED | No Dal status check → missing sqlite silently becomes a `term??` suggestion, HTTP 200 |
| A22 | [listhierClass.php:445](https://github.com/sanskrit-lexicon/csl-apidev/blob/6f1b720/listhierClass.php#L445) (+ accent_adjust.php:32, getword_data.php:140, servepdfClass.php:201) | swallow | CONFIRMED | `list($pginfo,$hcode,$key2,$hom) = preg_split('/:/',$info);` — <4 colon fields → undefined offsets silently nulled → wrong/blank metadata |
| A23 | [download_hwnorm1c_sqlite.sh:16-27](https://github.com/sanskrit-lexicon/csl-apidev/blob/6f1b720/download_hwnorm1c_sqlite.sh#L16-L27) | exitcode | CONFIRMED | Network failure/rate-limit → empty `LATEST_TAG` equals empty `LOCAL_TAG` → "Already up-to-date", exit 0, nothing staged; no checksum on the downloaded zip |
| A24 | basicdisplay.php:websan tip has a `nybj` dict branch in `sthndl_div`, apidev copy does not (see §7 G4) | drift | CONFIRMED | Same input renders differently per repo; the canonical sync vehicle is `v02/apidev_copy.sh`, run by hand — a fix landed in one tree silently never reaches the other |
| A25 | apidev `utilities/transcoder.php` (465 ln) vs websan twin (522 ln) | drift | CONFIRMED | The twin carries the PR #83 APCu cache; apidev re-parses the transcoder XML per request — the perf fix never propagated, no mechanism would have flagged it |

**Dead code note (apidev):** `htmlwork/makeassets/*.php` generators `require_once("../../web/webtc/disp.php")` — a path that does not exist in this flat repo (legacy Cologne server layout). Either dead or broken; either way they are documented as the producers of the `data` column format `dispitem.php` parses — worth a one-line README status instead of silence. `phpQuery-onefile.php` is vendored v0.9.5 (~2010), unaudited.

## 7. Cross-reference vs prior audits (re-verified on current tips)

| Prior item | Claim at the time | Status on audited tips (2026-08-28) | Evidence |
|---|---|---|---|
| PERF D1 — no Cache-Control on static assets | Queued PR | **FIXED** — `.htaccess` (mod_expires + Cache-Control) in v02 template tree, wired into generation | [websan .htaccess:12-29](https://github.com/sanskrit-lexicon/csl-websanlexicon/blob/45b0d30/v02/makotemplates/web/.htaccess), inventory.txt:137; PR #83 |
| PERF D2 — render-blocking JS | Queued PR | **FIXED** — `defer` on script tags in webtc/webtc1/webtc2 index templates (mobile1 deliberately not, CDN jQuery) | indexcaller.php:12-14, webtc1/index.php:12-18, webtc2/index.php:10-11; PR #83 |
| PERF D3 — transcoder FSM re-parse per request | Queued PR | **FIXED** in websanlexicon (APCu + serialized fallback) — but see W12: the fallback write is `@`-swallowed, and **apidev never got the fix at all** (A25) | transcoder.php:137-181; PR #83 |
| PERF D4 — webtc2 linear `query_dump.txt` scan | 🟡 separate PR | **STILL OPEN** (W10). Partial mitigations landed via H1523 (max clamp 1-100, lastLnum clamp, word ≤200 chars, `preg_quote` in exact mode only) | querymodel.php:142-308 |
| PERF D5 — geographic latency | ⛔ parked (money/infra) | unchanged, out of code scope | — |
| PERF D6 — MW keydoc fast path dev-gated | ⏸️ parked (upstream verify) | **STILL OPEN** (W14): gate intact at dal.php:39-43 + :91-93 | dal.php |
| AGENT_ROADMAP apidev #45 — servepdf page-routing root cause "identified; no fix yet" | Tier B row (compiled 28-07-2026) | **FIXED 2026-07-23** — commit `f65c13f` (PR #85): `tNN` title-page branch + `^Page\s*` strip; hand-ported to the websan twin. The roadmap row is stale and should be flipped | [servepdfClass.php:226-241](https://github.com/sanskrit-lexicon/csl-apidev/blob/6f1b720/servepdfClass.php) |
| AGENT_ROADMAP csl-pywork PR #62 (COLOGNE #331) | merged | consistent — CAE `v.` expansion present in generator | — |
| AGENT_ROADMAP registry rows (csl-orig #2865/#2867/#2872/#2874 etc.) | issue-data tracking | out of this audit's code scope; not re-verified | — |

New findings **not** in any prior audit: the entire §6a/§6b pipeline/exit-code class (P1-P21, O1-O10), all apidev rows, W1-W9/W11-W13, the twin-drift pair A24/A25, and the PR #83 follow-up W12.

## 8. Ranked gap specs (launchable future handoffs)

Rank = correctness-per-effort, top first. Each spec is self-contained enough to mint as an H###.

| # | Spec | Repo(s) | Scope + acceptance | Effort |
|---|---|---|---|---|
| G1 | **Fail-closed validation in the generation pipeline** | csl-pywork (+csl-orig hook) | `xmlvalidate.py` exits nonzero on failure; `redo_xml.sh` gates postxml on xmllint+make_xml status; `generate_dict.sh` checks each stage's `$?` (set -e or explicit); csl-orig `check_generate_dict.sh` checks the pipeline **exit status** instead of (or in addition to) red-line grep, dropping `\|\| true`. Acceptance: injecting a malformed record into a scratch dict copy makes every layer exit nonzero; green path unchanged for all 45 dicts in CI (extend xml-parse.yml beyond `mci`) | medium |
| G2 | **Hook hardening: staged-blob validation + deletion guard + install-by-default** | csl-orig | Validate `git show :v02/<path>` blobs not worktree bytes; include `D`/`R` in the diff filter (deletion of a canonical file must fail or require explicit ack); make `<LEND>`=0 a failure; switch docs to `git config core.hooksPath .githooks` (survives clone moves); CI backstop replicating both stages so hook-less clones are still gated. Acceptance: partial-staging and deletion scenarios fail closed in tests | medium |
| G3 | **webtc2 search index (D4)** | csl-pywork + csl-websanlexicon | Generation-time index (SQLite FTS5 or sorted prefix-table) replacing the per-request `query_dump.txt` linear scan; keep the flat file as fallback. Acceptance: identical top-100 results vs current implementation on MW/PWG sample queries; p95 query time recorded before/after | hard |
| G4 | **Twin-drift CI guard for apidev ↔ websanlexicon** | csl-apidev + csl-websanlexicon | A workflow diffing the twin set (apidev_copy.sh manifest: basicdisplay, basicadjust, getword_data, transcoder, dal, parm, dispitem, security_headers…) and failing on drift beyond an allowlist, or auto-opening a sync PR. Fixes to land first: `nybj` branch (A24), transcoder APCu (A25). Acceptance: a one-line edit in one twin makes CI red with a named action | medium |
| G5 | **Transcoder error surfacing** | csl-websanlexicon (+apidev twin) | Drop `@` on the cache write (log once per deploy via dbgprint/error_log); fail loud (or header-flag) when the FSM XML is missing instead of silent passthrough (W11/W12/A17). Acceptance: read-only `transcoder/` dir produces one visible log line; missing XML produces an explicit error, not untranscoded text | small |
| G6 | **HTTP semantics pass on apidev endpoints** | csl-apidev | `http_response_code()` on JSON envelopes (A19); replace `exit(1)` blanks with error envelopes (A10); surface `BasicDisplay->status` to callers (A12); guard the empty-match destructures (A9, A22); check `getImagefiles` status (A8). Acceptance: curl suite asserting 4xx/5xx codes for each injected anomaly | medium |
| G7 | **Two one-line display bugs** | csl-apidev | `basicdisplay.php:636` `<mark>` → `$this->row` (A11, silent loss of skd H/P markers); `dictinfo.php` `$dictyear_older` entries for ABCH/ACPH/ACSJ/NMMB/FRI (A20). Acceptance: skd sample entry shows markers; `version=1` renders for all five new dicts | trivial |
| G8 | **Regenerator bookkeeping fixes** | csl-pywork | `regenerate-hwnorm1-sqlite.sh`: use `git status --porcelain` (catches untracked) instead of `git diff --quiet` (P15); `refresh_csl.sh`: aggregate pull failures and report which repos failed (P14); remove the `make_xml.py:1336` debug cutoff and the literal junk row in `init_query.py:58` (P11, P18). Acceptance: untracked-file scenario commits and pushes | small |
| G9 | **dalglob/basicadjust SQL hygiene** | csl-apidev (+websan twin) | Parameterize the two concatenated queries (A13/A14/W4); strip `'` alongside `"` in parm normalization. Low urgency (data-derived input, whitelisted entrypoints) but cheap. Acceptance: `key=guru'` no longer reaches SQL as syntax | small |
| G10 | **reorg scripts: fix or delete** | csl-orig | `reorg1.sh` is broken as shipped (bashism O8, cwd assumption O9, nonexistent v00 source) and the reorg it automates happened years ago. Recommend deletion + README tombstone, or fix with bash shebang + `set -euo pipefail` + cwd independence. Acceptance: no executable path that silently no-ops | trivial |
| G11 | **download_hwnorm1c_sqlite.sh robustness** | csl-apidev | Fail on empty `LATEST_TAG` (A23); verify the zip (checksum or tag-signed release asset); keep the tag file update transactional (download → verify → stage → record tag). Acceptance: airplane-mode run exits nonzero with a clear message | small |

## 9. Spot-check protocol (re-derive 5 findings mechanically)

From fresh clones at the pinned commits:

```bash
git clone -q https://github.com/sanskrit-lexicon/csl-pywork && cd csl-pywork && git checkout -q e460545
sed -n '13,21p' v02/makotemplates/pywork/redo_xml.sh     # P1: xmllint error printed, then 'sh redo_postxml.sh' runs unconditionally
sed -n '55,59p' v02/makotemplates/pywork/webtc2/init_query.py  # P11: literal junk row, no % formatting

git clone -q https://github.com/sanskrit-lexicon/csl-orig && cd ../csl-orig && git checkout -q dee5a03
sed -n '69,71p' scripts/check_generate_dict.sh           # O1: '|| true' discards the pipeline exit status

git clone -q https://github.com/sanskrit-lexicon/csl-websanlexicon && cd ../csl-websanlexicon && git checkout -q 45b0d30
sed -n '180p' v02/makotemplates/web/utilities/transcoder.php  # W12: '@file_put_contents' swallows cache-write failure

git clone -q https://github.com/sanskrit-lexicon/csl-apidev && cd ../csl-apidev && git checkout -q 6f1b720
sed -n '634,638p' basicdisplay.php                       # A11: '$row .=' inside the mark branch — should be '$this->row'
```

Expected observations are stated in the comments; each contradicts the surrounding code's intent within 3 lines.

## 10. Scope and limits

- Audited: the live toolchain (csl-pywork v02 lane + root drivers), csl-orig scripts/hooks, websanlexicon `v02/makotemplates/**` (+PR #83 delta), apidev root PHP + scripts. **Not** audited: csl-pywork `v00/`, websanlexicon `v00/` (legacy; shares ≥7 defect classes with v02 per a lighter pass), the 46 generated `distinctfiles/**` output copies, csl-orig dictionary data itself, the Dart/Flutter csl-app, phpQuery vendored code.
- `SUSPECT` rows name their runtime check; nothing was executed against production or live data.
- No secrets/credentials were found or quoted.
- A drift-hazard census note: 32 frozen `unused_make_xml.py` per-dict copies exist under csl-pywork `v02/distinctfiles/<dict>/pywork/` — dead weight that invites accidental edits; candidate for a cleanup spec if the org wants one.

_Dr. Mārcis Gasūns_
