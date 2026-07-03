# Cologne dictionaries — page-speed / performance audit (July 2026)

_Created: 03-07-2026 · Last updated: 03-07-2026_

Audit of [www.sanskrit-lexicon.uni-koeln.de](https://www.sanskrit-lexicon.uni-koeln.de/) page speed: live HTTP measurements (03-07-2026, remote client) plus a code review of the [csl-websanlexicon](https://github.com/sanskrit-lexicon/csl-websanlexicon) v02 templates that generate every dictionary's web interface. Audit by Fable 5 (`claude-fable-5`); code sweep by an Explore subagent (inherited `claude-fable-5`), load-bearing claims re-verified by hand.

## What is already good — no action needed

- HTTP/2 (ALPN h2), TLS 1.3, and gzip compression are all enabled on the server.
- Total page weight of the MW search interface is only ~45 KB compressed.
- The SQLite `key` column is indexed; lookups use prepared statements.
- Search fires only on Enter ([webtc/main_webtc.js](https://github.com/sanskrit-lexicon/csl-websanlexicon/blob/main/v02/makotemplates/web/webtc/main_webtc.js) lines 100–104) — there is no per-keystroke request storm.
- Mako templates are pre-rendered at generation time by [csl-pywork](https://github.com/sanskrit-lexicon/csl-pywork) — no per-request template cost.

## Defects, ranked by win-per-effort

| # | Defect | Evidence | Fix | Status |
|---|---|---|---|---|
| D1 | **No `Cache-Control`/`Expires` on any static asset** (jQuery, keyboard.js, CSS, images) — only weak ETags, so every repeat pageview revalidates every asset at a full round trip to Cologne (~0.6 s each from India/US) | Live headers on `webtc/main.css`, `js/jquery.min.js` etc.: `ETag` + `Last-Modified` only | `mod_expires`/`Header set Cache-Control` block — shipped `.htaccess` in the web template, or httpd.conf if `AllowOverride` is off under `/scans` | 🔧 **Queued PR** (quick-wins batch); httpd.conf fallback is a maintainer action |
| D2 | **Render-blocking JavaScript** — all JS loads synchronously in `<head>` with no `defer`/`async`; webtc1 additionally blocks on 118 KB `keyboard.js` + 37 KB `transcoderJson.js` | [webtc/indexcaller.php](https://github.com/sanskrit-lexicon/csl-websanlexicon/blob/main/v02/makotemplates/web/webtc/indexcaller.php) lines 11–13 | Add `defer` to the template script tags (safe: all handlers bind inside `$(document).ready`) | 🔧 **Queued PR** (quick-wins batch) |
| D3 | **Transliteration FSM re-parsed from XML per request**, cache is per-PHP-process only | [utilities/transcoder.php](https://github.com/sanskrit-lexicon/csl-websanlexicon/blob/main/v02/makotemplates/web/utilities/transcoder.php) lines 24–89 | APCu cache (guarded by `function_exists`) with serialized-file fallback; saves 50–200 ms on cold transliteration pairs | 🔧 **Queued PR** (quick-wins batch) |
| D4 | **webtc2 advanced search linearly regex-scans a flat `query_dump.txt`** — 500 ms–10 s per query on large dictionaries (MW, PWG) | [webtc2/querymodel.php](https://github.com/sanskrit-lexicon/csl-websanlexicon/blob/main/v02/makotemplates/web/webtc2/querymodel.php) lines 141–206 | SQLite FTS5 table built at generation time in csl-pywork | 🟡 **Not in the quick-wins batch** — larger effort, needs its own scoped PR to both repos |
| D5 | **Geographic latency** — ~0.6 s of every cold TTFB is TCP+TLS round trips to the Cologne origin; the audience is largely India/US | Measured: cold TTFB 0.6–0.9 s, warm-connection server time only ~150–350 ms | A CDN in front of the origin | ⛔ **Parked — costs money.** Not fixable by code or wishing; requires funding plus a University of Cologne infrastructure decision. Listed for completeness only |
| D6 | **MW homonym gap-filling fan-out** — a single MW lookup can trigger 10–20 extra SQLite queries walking adjacent records by `lnum` to assemble the homonym display group | `get1_mwalt_prev` in [webtc/dal.php](https://github.com/sanskrit-lexicon/csl-websanlexicon/blob/main/v02/makotemplates/web/webtc/dal.php) lines 383–572 | **The fix already exists upstream but never shipped:** since 01-2020, `get1_mwalt` (line 377) prefers a precomputed `keydoc.sqlite` lookup (headword → document range, one query) — but the keydoc connection is gated on `?dev=yes` (lines 39–42 + 93), so production always runs the legacy per-record loop | ⏸️ **Parked — upstream verify-and-decide, not new code.** (a) Unprofiled win: the extra queries are single-row indexed LIMIT-1 SELECTs, likely only a few ms of the ~150–350 ms warm server time; (b) the loop's group-membership rules (hcode `HnA/HnB/HnC` prefix matching, four distinct break conditions) are correctness-sensitive display logic in MW's trap-laden homonym area — a rewrite that returns different records in edge cases costs more than the ms it saves; (c) promoting keydoc out of dev mode is the maintainer's call: it needs `keydoc.sqlite` present for MW plus an A/B that `?dev=yes` and production return identical records, and the reason it stayed dev-only since 2020 is unknown — ask Jim before flipping |

## Delivery path

D1–D3 are covered by a queued quick-wins working session (tracked privately as handoff H087) that will arrive as **one PR to csl-websanlexicon**; changes reach the live site at the next per-dictionary regeneration ([csl-pywork](https://github.com/sanskrit-lexicon/csl-pywork) `redo_xampp_selective.sh`) — no server access needed unless `AllowOverride` turns out to be off (then D1 becomes a one-block httpd.conf maintainer action). D4 is a separate future PR. D5 is parked (money). D6 is parked (the keydoc fast path already exists dev-gated in dal.php — profiling + an identical-output A/B + the maintainer's ruling on why it never shipped come before any code).

_Dr. Mārcis Gasūns_
