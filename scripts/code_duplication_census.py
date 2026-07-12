#!/usr/bin/env python3
"""Code-duplication census across the canonical Sanskrit-Lexicon repos (H688).

Re-measures the 2026-06-14 SHARED_CODE.md duplication census (transcoder.py x62,
digentry.py x170, ...) to quantify what the sanskrit-util extraction actually
changed, plus a LOC / language-mix table per repo.

Method (kept deliberately identical to the two prior censuses so numbers compare):
  * Repo set: top-level dirs under the GitHub root that contain a .git DIRECTORY.
    Linked worktrees (.git is a file) and the DATA_LAYERS_CENSUS scratch/backup/
    utility exclusion list are dropped, as are `<name>-h###` handoff clones.
  * Walk exclusions: .git node_modules vendor .graymatter dist build __pycache__
    .venv venv .observablehq (same as the SHARED_CODE.md appendix query).
  * Duplication: group every .py/.sh/.php by basename and by MD5 content hash
    (copies = file count, versions = distinct hashes) — the exact 2026-06-14 method.
  * Classification per tracked family: canonical (lives in the family's template
    repo) / template-instance (hash identical to a canonical copy — vendored,
    EXPECTED per MEGABOOK §7.11) / drifted (hash differs from every canonical copy).
  * sanskrit-util payoff: the 19 hand-rolled donor/consumer sites named in
    SHARED_CODE.md §1-2 are probed for delegation (imports/mentions sanskrit_util).

Output: reports/code_duplication_census.md + reports/code_duplication_census.json
Run:    python scripts/code_duplication_census.py [--root C:/Users/user/Documents/GitHub]
"""

import argparse
import hashlib
import json
import re
import sys
from collections import defaultdict
from datetime import date
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

# --- repo-set exclusions (DATA_LAYERS_CENSUS.md § Method, 06-07-2026) -----------
EXCLUDED_REPOS = {
    # scratch/backup clones
    "MWS-h079", "SanskritLexicography-h191", "SanskritLexicography-knobcalib",
    "SanskritLexicography-pwglayers-doc", "Uprava-h201", "SSC-a37a44",
    "csl-app-pr47", "csl-atlas-qw", "csl-obs-fix", "csl-observatory-verify",
    "wsl-pr74", "RuWritingStyles-backup.git", "RuWritingStyles-recover",
    "SL-wt-findings", "_tmp_pybin", "files", "tools",
    # utility (non-Sanskrit)
    "Retrieval-based-Voice-Conversion-WebUI", "SOCKS5-VPS",
}
HANDOFF_CLONE_RE = re.compile(r"-(h\d{3,}|wt-[a-z0-9-]+)$", re.IGNORECASE)

# --- walk exclusions (SHARED_CODE.md appendix) -----------------------------------
EXCLUDED_DIRS = {
    ".git", "node_modules", "vendor", ".graymatter", "dist", "build",
    "__pycache__", ".venv", "venv", ".observablehq",
}

# --- language mix ----------------------------------------------------------------
LANG_BY_EXT = {
    ".py": "Python", ".sh": "Shell", ".php": "PHP",
    ".js": "JavaScript", ".mjs": "JavaScript", ".cjs": "JavaScript",
    ".ts": "TypeScript", ".tsx": "TypeScript",
    ".dart": "Dart", ".pl": "Perl", ".r": "R", ".R": "R",
    ".css": "CSS", ".html": "HTML", ".htm": "HTML",
}
DUP_EXTS = {".py", ".sh", ".php"}

# --- tracked duplication families (SHARED_CODE.md, baseline 2026-06-14) ----------
# family -> (basenames, canonical PATH PREFIX (root-relative, '/'-terminated),
#            baseline copies, baseline versions, expected?)
# The prefix matters: csl-websanlexicon/webbackup/ holds per-dict deployment
# snapshots — only v02/makotemplates/ is the template.
FAMILIES = {
    "transcoder.py":     (["transcoder.py"], "csl-pywork/", 62, 7, True),
    "digentry.py":       (["digentry.py"], "csl-pywork/", 170, 5, True),
    "updateByLine.py":   (["updateByLine.py"], "csl-pywork/", 84, 5, True),
    "parseheadline.py":  (["parseheadline.py"], "csl-pywork/", 47, 3, True),
    "make_xml.py":       (["make_xml.py"], "csl-pywork/", 44, 38, True),
    "redo.sh":           (["redo.sh"], "csl-pywork/", 101, 97, True),
    "generate_dict.sh":  (["generate_dict.sh"], "csl-pywork/", None, None, True),
    "php endpoints":     (["getword.php", "getwordClass.php", "servepdf.php",
                           "serveimg.php", "displaylink.php"],
                          "csl-websanlexicon/v02/makotemplates/", None, None, True),
    "levenshtein.py":    (["levenshtein.py"], None, 6, None, False),
    "util_mw.py":        (["util_mw.py"], None, 7, None, False),
    "util_dump_lines.py": (["util_dump_lines.py"], None, 7, None, False),
    "unixify.py":        (["unixify.py"], None, 2, None, False),
    "compare.py":        (["compare.py"], None, 3, None, False),
}

# --- sanskrit-util donor/consumer sites (SHARED_CODE.md §1-2) ---------------------
# (repo-relative path, note). Delegation = file text mentions sanskrit_util/sanskrit-util.
SANSKRIT_UTIL_SITES = [
    ("WhitneyRoots/scripts/sanskrit_util.py", "Python donor"),
    ("WhitneyRoots/reader/reader.js", "inline deva2iast/norm"),
    ("WhitneyRoots/src/utils/linguistics.js", "normalizeSanskrit"),
    ("BookIndex/src/utils/linguistics.js", "census false positive (Russian-only)"),
    ("csl-atlas/src/lib/lookup-normalize.js", "JS normalizer"),
    ("csl-atlas/scripts/lib/dict-normalize.mjs", "stays local by design"),
    ("GRA/vn/gra-dev/web/webtc1/transcoderjs/transcoder3.js", "JS FSM transcoder"),
    ("SanskritSpellCheck/detectors/slp1util.py", "SLP1 alphabet/confusion"),
    ("SamudraManthanam/web/app/services/morph_service.py", "Dockerized runtime"),
    ("SamudraManthanam/web/app/services/slug.py", "Cyrillic->Latin, out of scope"),
    ("SamudraManthanam/web/corpus_builder/html_to_canonical.py", "own translit"),
    ("RussianRamayana/web/transliterate_filenames.py", "own translit"),
    ("VCP/meld_regex/convert_transliteration.py", "own translit"),
    ("csl-observatory/scripts/obs_t_translit_check.py", "own translit"),
    ("RWS-plugin/src/ruwritingstyles/translit_lint.py", "own translit"),
    ("ApteES/ae_saninvert/hwnorm1/hwnorm1.py", "headword normalizer"),
    ("CORRECTIONS/dictionaries/PD/issue-108/prep/hwchk_iast.py", "headword check"),
    ("csl-apidev/simple-search/wf0/word_frequency_norm.py", "key normalizer"),
    ("IndologyScholars/keyword_filtering.py", "key normalizer"),
]
# expected vendored copies of the package itself (payoff infrastructure, not defects)
SANSKRIT_UTIL_VENDORED = [
    "csl-apidev/app/vendor/sanskrit-util.global.js",
    "csl-guides/src/vendor/sanskrit-util.js",
    "csl-atlas/src/lib/sanskrit-util.js",
    "SanskritSpellCheck/detectors/sanskrit_util.py",
    "WhitneyRoots/scripts/sanskrit_util.py",
]


def canonical_repos(root: Path):
    repos = []
    for d in sorted(root.iterdir()):
        if not d.is_dir() or d.name in EXCLUDED_REPOS:
            continue
        if HANDOFF_CLONE_RE.search(d.name):
            continue
        git = d / ".git"
        if not git.is_dir():  # no repo, or a linked worktree (.git file)
            continue
        repos.append(d)
    return repos


def walk_code_files(repo: Path):
    stack = [repo]
    while stack:
        cur = stack.pop()
        try:
            entries = list(cur.iterdir())
        except OSError:
            continue
        for e in entries:
            if e.is_dir():
                if e.name not in EXCLUDED_DIRS:
                    stack.append(e)
            elif e.suffix in LANG_BY_EXT or e.suffix in DUP_EXTS:
                yield e


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=r"C:\Users\user\Documents\GitHub")
    ap.add_argument("--outdir", default=str(Path(__file__).resolve().parent.parent / "reports"))
    args = ap.parse_args()
    root = Path(args.root)
    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    repos = canonical_repos(root)
    print(f"Repos in census: {len(repos)}", flush=True)

    loc = defaultdict(lambda: defaultdict(lambda: [0, 0]))  # repo -> lang -> [files, lines]
    dup = defaultdict(list)  # basename -> [(repo, relpath, md5)]

    for repo in repos:
        for f in walk_code_files(repo):
            try:
                data = f.read_bytes()
            except OSError:
                continue
            lang = LANG_BY_EXT.get(f.suffix)
            if lang:
                c = loc[repo.name][lang]
                c[0] += 1
                c[1] += data.count(b"\n") + (1 if data and not data.endswith(b"\n") else 0)
            if f.suffix in DUP_EXTS:
                dup[f.name].append((repo.name, f.relative_to(root).as_posix(),
                                    hashlib.md5(data).hexdigest()))

    # --- family classification ---
    # A family's copies are generation-time vendored instances. Reference set for
    # "expected identical copy" = the canonical repo's own hashes when the family
    # actually HAS a copy there, else the modal version cluster (the majority
    # cohort of identical copies). Copies outside the reference set = drift
    # (version skew or a local fork). A declared-canonical family with ZERO
    # copies in its canonical repo is flagged — that is itself a defect finding.
    families_out = {}
    for fam, (basenames, canon_prefix, base_copies, base_versions, expected) in FAMILIES.items():
        hits = [h for b in basenames for h in dup.get(b, [])]
        clusters = defaultdict(int)
        for _, _, md5 in hits:
            clusters[md5] += 1
        canon_hashes = {h[2] for h in hits
                        if canon_prefix and h[1].startswith(canon_prefix)}
        no_canonical = bool(canon_prefix) and not canon_hashes
        modal = max(clusters.items(), key=lambda kv: kv[1])[0] if clusters else None
        # Reference set = canonical copies UNION the modal deployed cohort: the
        # canonical copy can itself lag the widely-deployed version, and 50+
        # byte-identical copies are one template instance, not 50 forks.
        ref_hashes = set(canon_hashes)
        if modal:
            ref_hashes.add(modal)
        n_canon = n_instance = 0
        drifted_paths, drifted_repos = [], set()
        for repo_name, rel, md5 in hits:
            if canon_prefix and rel.startswith(canon_prefix):
                n_canon += 1
            elif md5 in ref_hashes:
                n_instance += 1
            else:
                drifted_paths.append(rel)
                drifted_repos.add(repo_name)
        families_out[fam] = {
            "copies": len(hits), "versions": len(clusters),
            "cluster_sizes": sorted(clusters.values(), reverse=True),
            "baseline_copies": base_copies, "baseline_versions": base_versions,
            "canonical_prefix": canon_prefix, "expected_vendored": expected,
            "no_canonical_on_disk": no_canonical,
            "canonical_is_modal": (modal in canon_hashes) if canon_hashes else None,
            "canonical": n_canon,
            "template_instance": n_instance,
            "drifted": len(drifted_paths),
            "drifted_paths": sorted(drifted_paths),
            "drifted_repos": sorted(drifted_repos),
            "repos": sorted({h[0] for h in hits}),
        }

    # --- top duplicated basenames overall (>=4 repos, census threshold) ---
    top = []
    for name, hits in dup.items():
        repos_n = len({h[0] for h in hits})
        if repos_n >= 4:
            top.append({"basename": name, "copies": len(hits),
                        "versions": len({h[2] for h in hits}), "repos": repos_n})
    top.sort(key=lambda r: -r["copies"])

    # --- sanskrit-util payoff probe ---
    # Delegation = a real import/require of the package, not a mere comment mention
    # (WhitneyRoots reader.js says "Mirror of sanskrit_util.py" in a comment while
    # still carrying the inline copy — that is NOT delegation).
    # Three delegation shapes: a normal import, a require(), or an importlib
    # path-load referencing the quoted 'sanskrit-util' package dir (the
    # WhitneyRoots shim pattern — spec_from_file_location over the sibling repo).
    import_re = re.compile(
        r"^\s*(?:from|import)\s+[^#\n]*sanskrit[-_]util"
        r"|require\([^)]*sanskrit[-_]util"
        r"|['\"]sanskrit-util['\"]", re.MULTILINE)
    sites = []
    for rel, note in SANSKRIT_UTIL_SITES:
        p = root / rel
        status = "missing"
        if p.exists():
            try:
                text = p.read_text(encoding="utf-8", errors="replace")
                if import_re.search(text):
                    status = "delegates"
                elif "sanskrit_util" in text or "sanskrit-util" in text:
                    status = "hand-rolled (mentions only)"
                else:
                    status = "hand-rolled"
            except OSError:
                status = "unreadable"
        sites.append({"path": rel, "note": note, "status": status})
    vendored = [{"path": rel, "present": (root / rel).exists()}
                for rel in SANSKRIT_UTIL_VENDORED]

    result = {
        "date": date.today().isoformat(),
        "root": str(root),
        "repos_in_census": len(repos),
        "repo_names": [r.name for r in repos],
        "loc": {r: {l: {"files": v[0], "lines": v[1]} for l, v in langs.items()}
                for r, langs in loc.items()},
        "families": families_out,
        "top_duplicated_basenames": top[:40],
        "sanskrit_util_sites": sites,
        "sanskrit_util_vendored": vendored,
    }
    (outdir / "code_duplication_census.json").write_text(
        json.dumps(result, indent=1, ensure_ascii=False), encoding="utf-8")
    write_report(outdir / "code_duplication_census.md", result)
    print(f"Wrote {outdir / 'code_duplication_census.json'}")
    print(f"Wrote {outdir / 'code_duplication_census.md'}")


def fmt_delta(cur, base):
    if base is None:
        return "—"
    d = cur - base
    return f"{d:+d}"


def write_report(path: Path, r: dict):
    L = []
    today = date.today().strftime("%d-%m-%Y")
    L.append("# Code-duplication census — the sanskrit-util dedup payoff, measured\n")
    L.append(f"_Created: {today} · Last updated: {today}_\n")
    L.append(f"_Auto-generated by [scripts/code_duplication_census.py](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/scripts/code_duplication_census.py) — Fable 5 (`claude-fable-5`), H688. Baseline: the 2026-06-14 census in [SHARED_CODE.md](https://github.com/gasyoun/github-spine/blob/main/SHARED_CODE.md)._\n")
    L.append(f"\nRepos in census: **{r['repos_in_census']}** (top-level git clones under `{r['root']}`, "
             "minus the [DATA_LAYERS_CENSUS](https://github.com/gasyoun/Uprava/blob/main/DATA_LAYERS_CENSUS.md) "
             "scratch/backup/utility exclusions and linked worktrees).\n")

    # verdict
    sites0 = r["sanskrit_util_sites"]
    delegated0 = sum(1 for s in sites0 if s["status"] == "delegates")
    L.append("\n## 0 · Verdict — where the sanskrit-util payoff is (and isn't)\n")
    L.append("The ×62/×170 headline numbers **did not shrink and were never going to**: "
             "`transcoder.py`/`digentry.py` copies are generation-time vendored instances of "
             "the dict-build toolchain — sanskrit-util explicitly left that lane alone "
             "([SHARED_CODE.md](https://github.com/gasyoun/github-spine/blob/main/SHARED_CODE.md) §1–2: "
             "\"transcoder.py for build pipelines, sanskrit-util for keys and app transcode\"). "
             f"The measurable payoff lives in the app-code lane: **{delegated0} of {len(sites0)}** "
             "named hand-rolled transliteration/normalization sites now delegate to the package "
             f"(§2), plus {sum(1 for v in r['sanskrit_util_vendored'] if v['present'])} byte-synced "
             "vendored copies/shims of the package itself. The rest of the "
             "queue is Wave-2 work, most of it explicitly deferred/blocked in SHARED_CODE.md.\n")

    # families
    L.append("\n## 1 · Tracked duplication families vs the 2026-06-14 baseline\n")
    L.append("| Family | Copies (was) | Δ | Versions (was) | Cluster sizes | In canon repo | Identical vendored | Drifted | Expected? |")
    L.append("|---|--:|--:|--:|---|--:|--:|--:|---|")
    for fam, f in r["families"].items():
        was_c = f["baseline_copies"]
        was_v = f["baseline_versions"]
        sizes = f.get("cluster_sizes", [])
        sizes_s = ", ".join(str(s) for s in sizes[:6]) + ("…" if len(sizes) > 6 else "")
        canon_cell = ("**0 ⚠️**" if f.get("no_canonical_on_disk") else str(f["canonical"]))
        L.append(f"| `{fam}` | {f['copies']} ({was_c if was_c is not None else '?'}) "
                 f"| {fmt_delta(f['copies'], was_c)} "
                 f"| {f['versions']} ({was_v if was_v is not None else '?'}) "
                 f"| {sizes_s} "
                 f"| {canon_cell} | {f['template_instance']} | {f['drifted']} "
                 f"| {'vendored by design' if f['expected_vendored'] else 'true clone'} |")
    L.append("\nClassification: **in canon repo** = copies under the family's declared template path "
             "(csl-pywork / csl-websanlexicon `v02/makotemplates/` — NOT its per-dict `webbackup/` "
             "snapshots); **identical vendored** = byte-identical to a canonical copy or to the modal "
             "deployed cohort — an EXPECTED duplicate per MEGABOOK §7.11; **drifted** = outside that "
             "reference set (version skew or local fork). **Cluster sizes** = copies per distinct "
             "content hash, largest first: a shape like `120, 40, …` is version skew of one template, "
             "not 120 independent forks.\n")
    lagging = [fam for fam, f in r["families"].items()
               if f.get("canonical_is_modal") is False]
    if lagging:
        L.append(f"\n⚠️ **Template lags deployment** — the canonical copy is NOT the modal deployed "
                 f"version for: {', '.join('`'+x+'`' for x in lagging)}. "
                 "\"Fix the template, then regenerate\" silently regenerates from a version nobody "
                 "deploys; reconcile the template with the deployed cohort before the next fix lands.\n")
    flagged = [fam for fam, f in r["families"].items() if f.get("no_canonical_on_disk")]
    if flagged:
        L.append(f"\n⚠️ **Headless families — declared canonical repo holds NO copy on disk:** "
                 f"{', '.join('`'+x+'`' for x in flagged)}. "
                 "[SHARED_CODE.md](https://github.com/gasyoun/github-spine/blob/main/SHARED_CODE.md) §3 "
                 "names csl-pywork makotemplates as their origin, but the local csl-pywork clone "
                 "carries no such file — every copy is a leaf; there is no master to regenerate from. "
                 "Classification for these falls back to the modal version cluster.\n")
    L.append("\n**Comparability caveats.** (a) The 2026-06-14 baseline did not record its exact repo "
             "set; this census covers every canonical clone present today, so part of each Δ is "
             "repos cloned since June (e.g. mw-dev, hwnorm1/hwnorm2), part genuinely new "
             "per-issue vendored copies (CORRECTIONS/csl-corrections issue dirs). Treat Δ as an "
             "upper bound on growth, not a measured trend. (b) `redo.sh`/`make_xml.py` are "
             "**meant** to be copied per issue and customized (SHARED_CODE.md §3) — their high "
             "distinct-version counts are the intended workflow, not decay.\n")

    # sanskrit-util payoff
    sites = r["sanskrit_util_sites"]
    delegated = sum(1 for s in sites if s["status"] == "delegates")
    hand = sum(1 for s in sites if s["status"].startswith("hand-rolled"))
    gone = sum(1 for s in sites if s["status"] == "missing")
    L.append("\n## 2 · sanskrit-util payoff — the SHARED_CODE §1–2 donor/consumer sites\n")
    L.append(f"Of the **{len(sites)}** hand-rolled transliteration/normalization sites the "
             f"2026-06-14 census named: **{delegated} now delegate** to `sanskrit-util`, "
             f"**{hand} remain hand-rolled**, {gone} no longer on disk.\n")
    L.append("| Site | Status | Note |")
    L.append("|---|---|---|")
    for s in sites:
        L.append(f"| `{s['path']}` | {s['status']} | {s['note']} |")
    L.append("\nVendored copies of the package itself (expected, kept byte-synced on release):\n")
    for v in r["sanskrit_util_vendored"]:
        L.append(f"- `{v['path']}` — {'present' if v['present'] else 'ABSENT'}")

    # top duplicated basenames
    L.append("\n## 3 · Top duplicated basenames (≥4 repos, census threshold)\n")
    L.append("| Basename | Copies | Distinct versions | Repos |")
    L.append("|---|--:|--:|--:|")
    for t in r["top_duplicated_basenames"][:25]:
        L.append(f"| `{t['basename']}` | {t['copies']} | {t['versions']} | {t['repos']} |")

    # LOC table
    L.append("\n## 4 · LOC & language mix per repo (code files only)\n")
    L.append("HTML dominates the 'Other' column in the site-bearing repos (BookIndex, "
             "SamudraManthanam, SanskritLexicography, …) because committed **generated/prerendered "
             "site output** counts as code files here — read the Python/JS/PHP columns for "
             "authored-code weight.\n")
    L.append("| Repo | Total LOC | Dominant | Python | JS/TS | PHP | Shell | Other |")
    L.append("|---|--:|---|--:|--:|--:|--:|--:|")
    rows = []
    for repo, langs in r["loc"].items():
        total = sum(v["lines"] for v in langs.values())
        py = langs.get("Python", {}).get("lines", 0)
        js = (langs.get("JavaScript", {}).get("lines", 0)
              + langs.get("TypeScript", {}).get("lines", 0))
        php = langs.get("PHP", {}).get("lines", 0)
        sh = langs.get("Shell", {}).get("lines", 0)
        other = total - py - js - php - sh
        dom = max(langs.items(), key=lambda kv: kv[1]["lines"])[0] if langs else "—"
        rows.append((total, repo, dom, py, js, php, sh, other))
    rows.sort(reverse=True)
    for total, repo, dom, py, js, php, sh, other in rows:
        L.append(f"| {repo} | {total:,} | {dom} | {py:,} | {js:,} | {php:,} | {sh:,} | {other:,} |")

    L.append("\n_Auto-generated by `scripts/code_duplication_census.py`. Re-run to refresh; "
             "see the JSON companion for drifted-path detail._\n")
    path.write_text("\n".join(L), encoding="utf-8")


if __name__ == "__main__":
    main()
