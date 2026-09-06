# H3487 audit census — full disposition crosswalk (71 sites, tips of 06-09-2026)

_Created: 06-09-2026 · Last updated: 06-09-2026_

Companion to [CODEBASE_ADVERSARIAL_AUDIT_2026-08.md](CODEBASE_ADVERSARIAL_AUDIT_2026-08.md) (H3487) and [CODEBASE_IMPROVEMENT_MAP_2026-09.md](CODEBASE_IMPROVEMENT_MAP_2026-09.md) (H3884). Produced by a «doubt everything» pass: every census finding from the August audit is dispositioned against the **current `main` tips** of csl-pywork / csl-orig / csl-websanlexicon / csl-apidev, not against registry claims.

## 1. Why this exists

The H3487 remediation claimed completion twice — once by the fix waves (H3631–H3641, all ✅ in the registry), once by the residual pass ([H4227](https://github.com/gasyoun/Uprava/blob/main/handoffs/H4227-OxAlpha_multi_audit-residuals-a1-a15-o1-p8_06.09.26.md), «four still-standing residuals»). A per-finding crosswalk had never been written. This doc is that crosswalk. Headline corrections it establishes:

1. **H4227's «9 of 11 gap specs shipped» undercounts.** Per the H3884 sweep plus this pass: **G2–G11 (10 of 11) shipped merged**; only **G1 is partial** — its csl-pywork leg landed ([PR #84](https://github.com/sanskrit-lexicon/csl-pywork/pull/84)), but the csl-orig leg (O1, `check_generate_dict.sh` `|| true`) stayed broken until [PR #2896](https://github.com/sanskrit-lexicon/csl-orig/pull/2896) (open at this writing).
2. **The census residue is larger than four sites.** Verifying every one of the 71 census rows at tips finds **~20 sites still open or partial** (§3), concentrated in: the websan twins of already-fixed apidev findings (servepdf/listhier/dictinfo are twin-drift *allowlisted*, so apidev fixes never propagated), dal.php exception-surfacing, and the pywork downloads/test scripts that no gap spec ever covered.
3. **Nothing is live on Cologne production.** All fixes exist at repo tips only. apidev (flat-root) activates on server pull; **websanlexicon production is generated PHP** ([serving manual §2](https://github.com/gasyoun/Uprava/blob/main/docs/COLOGNE_SERVING_DISPLAY_API_AUTHORITY_OPS_MANUAL.md)): template merges activate only after a server-side regeneration run.

Counts: **45 fixed · 3 fixed-in-open-PR (A1+A15 → apidev #168; O1 → orig #2896; P8 → pywork #88) · 20 open/partial · 2 parked · 2 unverified-at-tip.**

## 2. Gap-spec ledger (H3487 §8 → waves)

| Spec | Findings | Disposition | Vehicle |
|---|---|---|---|
| G1 fail-closed pipeline | P1–P5, O1–O2 | **partial** | pywork leg [PR #84](https://github.com/sanskrit-lexicon/csl-pywork/pull/84) merged; O1 leg [PR #2896](https://github.com/sanskrit-lexicon/csl-orig/pull/2896) open; O7 (validation mutates siblings) never addressed |
| G2 hook hardening | O3–O6, O10 | fixed | csl-orig [PR #2894](https://github.com/sanskrit-lexicon/csl-orig/pull/2894) |
| G3 webtc2 index (D4) | W10 | fixed | [pywork #87](https://github.com/sanskrit-lexicon/csl-pywork/pull/87) + [websan #153](https://github.com/sanskrit-lexicon/csl-websanlexicon/pull/153); live effect awaits Cologne regeneration |
| G4 twin-drift guard | A24, A25 | fixed | [apidev #155](https://github.com/sanskrit-lexicon/csl-apidev/pull/155); guard is one-directional + PHP-only (map rank #7) |
| G5 transcoder surfacing | W11, W12, A17 | fixed | [websan #150](https://github.com/sanskrit-lexicon/csl-websanlexicon/pull/150) + [apidev #156](https://github.com/sanskrit-lexicon/csl-apidev/pull/156) |
| G6 HTTP semantics | A8–A12, A19, A22 | fixed | [apidev #159](https://github.com/sanskrit-lexicon/csl-apidev/pull/159)/[#161](https://github.com/sanskrit-lexicon/csl-apidev/pull/161); websan mirror via twin guard #152 |
| G7 display one-liners | A11, A20 | fixed | [apidev #162](https://github.com/sanskrit-lexicon/csl-apidev/pull/162) + [websan #154](https://github.com/sanskrit-lexicon/csl-websanlexicon/pull/154) |
| G8 bookkeeping | P11, P14, P15, P18 | fixed | [pywork #85](https://github.com/sanskrit-lexicon/csl-pywork/pull/85) |
| G9 SQL hygiene | A13, A14, W4 | fixed | [apidev #157](https://github.com/sanskrit-lexicon/csl-apidev/pull/157) + [websan #151](https://github.com/sanskrit-lexicon/csl-websanlexicon/pull/151) |
| G10 reorg scripts | O8, O9 | fixed | [orig #2895](https://github.com/sanskrit-lexicon/csl-orig/pull/2895) deleted + tombstone |
| G11 download robustness | A23 | fixed | [apidev #158](https://github.com/sanskrit-lexicon/csl-apidev/pull/158) |
| — (never spec'd) | A1, A15 | fixed-in-open-PR | [apidev #168](https://github.com/sanskrit-lexicon/csl-apidev/pull/168) (H4227) |
| — (never spec'd) | P8 | fixed-in-open-PR | [pywork #88](https://github.com/sanskrit-lexicon/csl-pywork/pull/88) (H4227) |

## 3. Census crosswalk — status at tips 06-09-2026

Legend: ✅ fixed (merged) · 🟡 fixed in open PR · 🔴 open at tip (evidence = direct read of `main` this pass unless noted) · ⏸️ parked · ❓ unverified this pass.

### csl-pywork (P1–P21)

| ID | Status | Evidence / vehicle |
|---|---|---|
| P1 xmllint advisory gate | ✅ | H3631 #84: redo_xml.sh status gates, STOP+exit 1 |
| P2 xmlvalidate exit 0 | ✅ | #84: `sys.exit(1)` after "Problem validating" |
| P3 malformed records exit 0 | ✅ | #84: make_xml.py `sys.exit(1)` on malformed |
| P4 truncate-before-validate | ✅ | #84: write `fileout+'.tmp'` → `os.replace` |
| P5 stage status unchecked | ✅ | #84: `fail_exit()` + per-stage checks |
| P6 C-category copy crash | 🔴 | generate.py unverified at tip; spot-check shows 3 `except Exception` sites (:62,:102,:196) of unproven scope |
| P7 makedirs swallow | 🔴 | read 06-09: `except Exception: pass` still at generate.py:58–65 |
| P8 sqlite_txt row-drop | 🟡 | [pywork #88](https://github.com/sanskrit-lexicon/csl-pywork/pull/88) open |
| P9 stale sqlite on failure | ❓ | sqlite/redo.sh `set -e` not re-derived this pass (G1 evidence covers redo_xml/redo_postxml gates) |
| P10 init_query NameError | ✅ | H3633: `keysanskrit=''` init |
| P11 junk literal row | ✅ | H3638 #85 junk-row guard |
| P12 downloads delete-before-copy | 🔴 | read 06-09: redo_txt.sh still `rm` first, unchecked `cp`/`zip`, no `set -e` |
| P13 downloads fire-and-forget | 🔴 | same family, unchanged |
| P14 pull failures aggregated | ✅ | #85 per-repo OK/FAIL + exit 1 |
| P15 untracked outputs missed | ✅ | #85 `git status --porcelain` |
| P16 cologne_test dictyear=0 | 🔴 | read 06-09: dictyear still 0/2013/2014 branches; post-2014 dicts diff nonexistent path |
| P17 typo'd dict wrong-dir run | 🔴 | read 06-09: root redo.sh `cd "$dict"Scan/…` unchecked, loop continues |
| P18 dead >1M debug cutoff | ✅ | #85 removed |
| P19 eid/syns silent drop | 🔴 | read 06-09: `re.search` at make_xml.py:925 without guard |
| P20 BOM inconsistency (SUSPECT) | 🔴 | no wave touched encodings; still one refactor from corruption |
| P21 parseheadline `<` truncation (SUSPECT) | 🔴 | read 06-09: regex split unchanged |

### csl-orig (O1–O10)

| ID | Status | Evidence / vehicle |
|---|---|---|
| O1 `\|\| true` exit discard | 🟡 | [orig #2896](https://github.com/sanskrit-lexicon/csl-orig/pull/2896) open |
| O2 incomplete red channel | ✅ | #84 covers all stages incl. postxml/downloads |
| O3 deletion/rename bypass | ✅ | #2894 deletion guard + ack |
| O4 missing-file silent skip | ✅ | #2894 staged-blob validation |
| O5 zero-LEND vacuous pass | ✅ | #2894 fail-closed |
| O6 worktree-not-staged bytes | ✅ | #2894 `git show :v02/…` |
| O7 validation mutates siblings | 🔴 | never addressed by any wave; commit still regenerates downstream siblings pre-verdict |
| O8/O9 reorg broken | ✅ | #2895 deleted + tombstone |
| O10 absolute symlink hook | ✅ | #2894 `core.hooksPath .githooks` |

### csl-websanlexicon (W1–W14)

| ID | Status | Evidence / vehicle |
|---|---|---|
| W1 query_dump missing → 200 | ✅ | read 06-09: query.php `htmlspecialchars` + `http_response_code(400)` |
| W2 exit(1) mid-JSON blank 200 | ✅ | G6 apidev fix + twin mirror [websan #152](https://github.com/sanskrit-lexicon/csl-websanlexicon/pull/152) |
| W3 getgeneral no try/catch | 🔴 partial | read 06-09: SQL now prepared + table charset guard, **but still no try/catch** — locked DB/missing table = blank 500 |
| W4 interpolated LIKE SQL | ✅ | G9 `:pat` binding |
| W5 servepdf unchecked pdffiles | 🔴 | read 06-09: `file($filename)` unchecked — apidev's H4212 hardening never reached the websan twin (servepdf* is twin-drift *allowlisted*) |
| W6 null pdfpages URL | ❓ | path present at dictinfo.php:72; null-URL branch not re-derived this pass |
| W7 listhier empty-match destructure | 🔴 | read 06-09: `list(...) = $matches[0];` unchanged at listhiermodel.php:16 |
| W8 unknown key → "a" fallback | 🔴 | read 06-09: `$key = "a"; // sure to match` unchanged |
| W9 UI offers >100, API clamps | 🔴 partial | H1523 clamp confirmed; UI/offering side not reconciled |
| W10 linear query_dump scan | ✅ | G3 #153 index + fallback |
| W11/W12 transcoder silent failures | ✅ | G5 #150 |
| W13 garbage translit silently slp1 | 🔴 | read 06-09: `transcoder_standardize_filter` maps unknown → default silently |
| W14 keydoc fast path dev-gated (D6) | ⏸️ | parked pending upstream verify (H3884 D6 row); gate intact both twins |

### csl-apidev (A1–A25 + dead-code note)

| ID | Status | Evidence / vehicle |
|---|---|---|
| A1 blanket error_reporting suppression | 🟡 | [apidev #168](https://github.com/sanskrit-lexicon/csl-apidev/pull/168) open (17 files) |
| A2 corrupt sqlite → "not found" 200 | 🔴 | read 06-09: null-db → empty array unchanged; status still unchecked by callers |
| A3 PDOException → empty array | 🔴 | read 06-09: `catch (PDOException $e) { return $ansarr; }` at dal.php:129 — prepared statements landed, the swallow remains |
| A4 getgeneral no try/catch | 🔴 | read 06-09: charset guard + binding landed; try/catch absent (dal.php:626+) |
| A5 keydoc-path unchecked prepare | ❓ | get() now wraps prepare/execute (:124–130); :195/:361 call sites not re-derived |
| A6 servepdf pdffiles fatal | ✅ | H4212 #165: missing page+key → 400 |
| A7 wrong scan page silent | ✅ | H4212 pagehash isset guards |
| A8 page-not-found → page 1 | ✅ | G6 404 |
| A9/A22 destructure guards | ✅ | G6 |
| A10 exit(1) blanks | ✅ | G6 throws + envelopes |
| A11 `<mark>` markers lost | ✅ | G7 `$this->row` |
| A12 BasicDisplay status unread | ✅ | G6 surfaced |
| A13/A14 interpolated SQL | ✅ | G9 prepared statements |
| A15 missing key → guru | 🟡 | [apidev #168](https://github.com/sanskrit-lexicon/csl-apidev/pull/168) open; confirmed still on main 06-09 (parm.php:87 `$tempkey='guru'`) |
| A16 unknown transcoder params → slp1 | 🔴 | never spec'd; G5 covered missing-FSM only, not param coercion |
| A17 missing FSM silent passthrough | ✅ | G5 RuntimeException |
| A18 api_trial undefined hw/reg | ✅ | read 06-09: route + missing-value validation returns False |
| A19 status-in-200-body | ✅ | G6 `http_response_code` |
| A20 dictyear_older gaps | ✅ | G7 fallback |
| A21 getsuggest no status check | 🔴 | read 06-09: dal calls unchecked, missing sqlite → `term??` suggestion 200 |
| A23 download script | ✅ | G11 |
| A24/A25 twin drift | ✅ | G4 sync + CI guard |
| Dead code (htmlwork/makeassets, phpQuery) | ❓ | one-line README status still absent (not a code risk) |

## 4. Activation ledger — what makes any of this real on Cologne

1. **Merge** the open PRs: [apidev #168](https://github.com/sanskrit-lexicon/csl-apidev/pull/168), [orig #2896](https://github.com/sanskrit-lexicon/csl-orig/pull/2896), [pywork #88](https://github.com/sanskrit-lexicon/csl-pywork/pull/88) — human-gated (Jim).
2. **Server pull csl-apidev** → apidev fixes (#159–#162, #165, #168) go live immediately (flat-root, served directly).
3. **Server pull csl-pywork + csl-websanlexicon, then run the generation chain** (`v02/redo_xampp_selective.py` or per-dict `generate_web.sh`) → websan fixes (#150–#154) go live. **Pull alone is not enough** — production serves generated copies ([serving manual §2](https://github.com/gasyoun/Uprava/blob/main/docs/COLOGNE_SERVING_DISPLAY_API_AUTHORITY_OPS_MANUAL.md)).
4. csl-orig hook changes affect future commits only (dev-side, no serving impact).

## 5. Method + limits

Tips read directly via GitHub raw at `main` on 06-09-2026 (grep/sed evidence per row). Rows marked ❓ were not re-derived this pass and carry the exact check to run. SUSPECT-class rows (P20/P21) remain code-true but untriggered. Live-HTTP behaviour was not probed (no server access from this pass); «fixed» means merged at tip, verified by code read and/or the executing handoff's evidence, not by production probe. Sequel wave for the 🔴 rows: tracked as Uprava GTD `@DO` (audit-census residual wave 2, OxAlpha, ~medium).

_Dr. Mārcis Gasūns_
