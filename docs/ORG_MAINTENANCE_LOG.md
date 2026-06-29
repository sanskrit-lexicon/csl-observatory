# Org Maintenance Log

Cross-repo repo-health, CI, and security work spanning the Sanskrit Lexicon /
gasyoun ecosystem. Newest first. Per-repo detail lives in each repo's PRs; this
is the org-level index for work that does not belong to a single repo.

---

## 2026-06-14 — Org-wide security + CI hardening sweep

**Scope.** Eliminate the red `Analyze (php)` checks, clear red default-branch CI,
triage the Security tab across repos, and review two active dev surfaces.

### `Analyze (php)` eliminated org-wide
CodeQL has **no PHP analyzer**, so any `php` in a CodeQL matrix is permanent red.
Removed it from the last repo carrying it and fixed the source so it can't recur.
- RuWritingStyles: [PR #15](https://github.com/gasyoun/RuWritingStyles/pull/15) (drop `php`).
- Local tooling `.deploy_codeql.py` + the `cologne-codeql-all` skill doc corrected:
  `composer.json`/`*.php` no longer map to a CodeQL language; PHP SAST routes to Semgrep.

### Red default-branch CI cleared
- GitHub Pages "Deploy from a branch" was running Jekyll over whole repos and dying
  on stray Liquid in Markdown → added `.nojekyll`: MWS
  [#208](https://github.com/sanskrit-lexicon/MWS/pull/208), PWG
  [#185](https://github.com/sanskrit-lexicon/PWG/pull/185), CommentaryStrategies
  [#14](https://github.com/gasyoun/CommentaryStrategies/pull/14), SamudraManthanam
  [#3](https://github.com/gasyoun/SamudraManthanam/pull/3).
- SanskritKaraoke "Verse Library CI" 403 on `git push` → added `permissions: contents: write`
  ([#10](https://github.com/gasyoun/SanskritKaraoke/pull/10)).
- RuWritingStyles CI: FastAPI `TestClient` needed `httpx`
  ([#16](https://github.com/gasyoun/RuWritingStyles/pull/16)).
- Remaining org red: RVC-WebUI `Unit Test` only — a vendored fork, upstream.

### Security tab triage
- **csl-websanlexicon**: 679/687 Semgrep alerts were noise in an archived `webbackup/`
  dir → `.semgrepignore` ([#66](https://github.com/sanskrit-lexicon/csl-websanlexicon/pull/66)).
- **Dict-frontend reflected-XSS (real)**: validated JSONP callbacks / escaped `$_GET`
  reflections — GRA [#44](https://github.com/sanskrit-lexicon/GRA/pull/44), MWS
  [#210](https://github.com/sanskrit-lexicon/MWS/pull/210); `servepdf.php` assessed as a
  false positive (filename from trusted `pdffiles.txt`).
- **AP90**: real char-range typo `[a-zA-z]`→`[a-zA-Z]`
  ([#35](https://github.com/sanskrit-lexicon/AP90/pull/35)).
- **csl-apidev (44 alerts)**: all in non-served sample/dev/test/trial code; canonical
  endpoints already guarded → dismissed with justifications.
- CodeQL false-positives / won't-fix dismissed with written reasons: csl-atlas (2),
  PWK (2), COLOGNE (5). Every reviewed repo's Security tab now at 0 (bar 2 informational
  csl-websanlexicon mako notes).

### Salt-API Phase 1 review (csl-apidev)
- [PR #46](https://github.com/sanskrit-lexicon/csl-apidev/pull/46) reviewed: clean —
  callbacks whitelisted + `htmlentities`, table name whitelisted `[a-z0-9_]+`, all values
  bound, GraphQL `json_decode`-only. Fixed one REST/GraphQL validation divergence; verdict
  posted on the PR.

### CI hygiene
- `codeql-action` bumped v3→v4 (+ `build-mode: none`, checkout@v5): csl-websanlexicon
  [#69](https://github.com/sanskrit-lexicon/csl-websanlexicon/pull/69), RuWritingStyles
  [#18](https://github.com/gasyoun/RuWritingStyles/pull/18); 14 other repos already v4 via
  Dependabot. `.deploy_codeql.py` updated to emit the v4 pattern.

### WhitneyRoots data-integrity review
- IAST `form_key` verified length-preserving; crosswalk alignment sound (0 dangling refs).
- **Real bug fixed**: 3 corpus-only `{I,VI}` accent-collapse class additions (pṛṇ, mṛṇ,
  sphur) had leaked into `src/app_data.json`; the earlier revert filter missed the pair
  form. [PR #9](https://github.com/gasyoun/WhitneyRoots/pull/9) broadens the filter and
  reverts exactly those 3.

### Observatory
- Tooling Roadmap audit drift cleared: 8 untracked open issues added to board #9; audit
  now green. (`TOOLING_AUDIT_TOKEN` was already set — earlier "missing secret" reading was
  a misread of the runner log.)

### Open follow-ups (for human / DECISIONS_NEEDED)
- **WhitneyRoots**: `ṛdh` (+I) and `stan` (+VII) remain in `review_queue.json` — a
  scholarly call (grammar/Zaliznyak), not auto-reverted. The token disambiguation is a
  single-gloss-keyword bind, not the documented "two-gate gaṇa+present" — characterization
  to correct. Stale crosswalk totals to refresh (ambiguous 45→52, edges 7315→9878, roots
  785→790); `app_data.json` carries 5 roots absent from the crosswalk spine.
- **csl-apidev**: confirm/harden the canonical Salt-API served surface as the API finalizes.
