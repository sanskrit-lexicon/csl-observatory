#!/usr/bin/env python3
"""PWG `<ls>` citation counts per bibliography abbreviation -- the denominator-safe count (H2874).

This is the count the PWG scan-index tracker's `Citation count` column was taken from,
and the canonical regeneration of it against current dictionary data.

**The definition, stated once.** For every `<ls ...>...</ls>` element in the PWG
digitization (`csl-orig/v02/pwg/pwg.txt`):

* if the element carries an `n="..."` attribute, that value plus one space is prepended
  to the element text before matching;
* an element whose (so-composed) text begins with a digit counts as `NUMBER`;
* otherwise the element is attributed to the **longest bibliography abbreviation in
  `pwgbib_input.txt` that is a prefix of the element text** -- so `MED. k. 12` and
  `MED. kh.` both count towards `MED.`;
* an element with no such prefix counts as `UNKNOWN`.

The total is therefore a **work-family prefix rollup**, not a count of a citation
string, and every element in the dictionary lands in exactly one bucket. `ALL` is the
sum over all buckets and is the only legitimate dictionary-wide denominator for these
numbers.

**Provenance of the definition.** This module is a faithful port of
`lsextract_all.py` in the sanskrit-lexicon/PWG repository
(https://github.com/sanskrit-lexicon/PWG/blob/master/pwgissues/issue94/lsextract_all.py,
E. Fitzgerald, first used in `pwg_ls2/ak/`). `--verify-port` runs the upstream script
and this port on the same inputs and requires byte-identical output apart from the
generated date line; that check is what licenses the port to stand in for the original
in an offline repository.

Run:
    python scripts/pwg_ls_counts.py --recount           # rebuild the current table
    python scripts/pwg_ls_counts.py --verify-port       # port == upstream script
    python scripts/pwg_ls_counts.py --check             # committed tables self-consistent

Without `--recount` the script is stdlib-only, offline, and reads only committed data.
"""

import argparse
import csv
import hashlib
import json
import re
import shutil
import subprocess
import sys
import tempfile
from datetime import date
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parents[1]
COUNTS_DIR = ROOT / "data" / "pwg_scan_index_tracker" / "ls_counts"

DEFAULT_PWG_REPO = Path(r"C:\Users\user\Documents\GitHub\PWG")
DEFAULT_CSL_ORIG = Path(r"C:\Users\user\Documents\GitHub\csl-orig")

# The tracker-era table: the file the sheet's `Citation count` column was read off.
TRACKER_ERA_TABLE = COUNTS_DIR / "pwg_ls_counts_2024-09-11.tsv"
# The canonical, independently regenerated table used for denominators.
CURRENT_TABLE = COUNTS_DIR / "pwg_ls_counts_current.tsv"

UPSTREAM_SCRIPT = "pwgissues/issue94/lsextract_all.py"
UPSTREAM_BIB = "pwgissues/issue94/pwgbib_input.txt"
TRACKER_ERA_UPSTREAM = "pwgissues/issue74/lsextract_all.txt"
TRACKER_ERA_BIB = "pwgissues/issue74/pwgbib_input.txt"

LS_RE = re.compile(r"<ls([^>]*)>([^<]*)</ls>")
N_RE = re.compile(r' +n="(.*?)"')

NUMBER = "NUMBER"
UNKNOWN = "UNKNOWN"


# ------------------------------------------------------------------ the count itself

def load_tooltips(bib_path: Path):
    """pwgbib_input.txt -> [(bib_code, abbrev, gloss)] in file order."""
    tips = []
    with bib_path.open(encoding="utf-8") as fh:
        for lineno, line in enumerate(fh, 1):
            parts = line.rstrip("\r\n").split("\t")
            if len(parts) != 4:
                raise ValueError(f"{bib_path}:{lineno}: expected 4 tab-separated fields")
            code, abbrev, _abbrevlo, gloss = parts
            tips.append((code, abbrev, gloss))
    return tips


def count_ls(pwg_path: Path, bib_path: Path):
    """Count every `<ls>` in pwg.txt into its longest-prefix bibliography abbreviation.

    Returns (tips, totals, n_number, n_unknown) with `totals` parallel to `tips`.
    """
    tips = load_tooltips(bib_path)
    # Longest abbreviation first, bucketed by first character -- upstream's `dfirstchar`.
    order = sorted(range(len(tips)), key=lambda i: len(tips[i][1]), reverse=True)
    buckets = {}
    for i in order:
        buckets.setdefault(tips[i][1][0], []).append(i)

    totals = [0] * len(tips)
    n_number = n_unknown = 0
    with pwg_path.open(encoding="utf-8") as fh:
        for iline, line in enumerate(fh):
            if iline == 0:
                continue
            line = line.rstrip("\r\n")
            if not line or line == "<LEND>" or line.startswith("<L>") or line.startswith("[Page"):
                continue
            for m in LS_RE.finditer(line):
                elt = m.group(2)
                m1 = N_RE.search(m.group(1))
                if m1:
                    elt = m1.group(1) + " " + elt
                if not elt:
                    n_unknown += 1
                    continue
                if elt[0] in "0123456789":
                    n_number += 1
                    continue
                hit = None
                for i in buckets.get(elt[0], ()):
                    if elt.startswith(tips[i][1]):
                        hit = i
                        break
                if hit is None:
                    n_unknown += 1
                else:
                    totals[hit] += 1
    return tips, totals, n_number, n_unknown


def upstream_format(tips, totals, n_number, n_unknown, as_of: str):
    """Render exactly as upstream `write_tips` does, for the port-fidelity check."""
    def fmt(total, abbrev, gloss):
        gloss = re.sub(r"^.*? = ", "", gloss).replace("[Cologne Addition]", "")
        return "%05d\t%s\t%s" % (total, abbrev, gloss[0:40])

    recs = [""]
    recs.append(fmt(n_number, NUMBER, "ls starts with number"))
    recs.append(fmt(n_unknown, UNKNOWN, "ls is unknown"))
    tot = n_number + n_unknown
    for i in sorted(range(len(tips)), key=lambda i: totals[i], reverse=True):
        recs.append(fmt(totals[i], tips[i][1], tips[i][2]))
        tot += totals[i]
    recs[0] = "%05d\t%s\tAs of %s" % (tot, "ALL", as_of)
    return recs


# ---------------------------------------------------------------- committed TSV form

FIELDS = ["total", "abbrev", "bib_code", "gloss"]


def write_table(path: Path, rows, meta: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as fh:
        w = csv.writer(fh, delimiter="\t", lineterminator="\n")
        w.writerow(FIELDS)
        for r in rows:
            w.writerow([r["total"], r["abbrev"], r["bib_code"], r["gloss"]])
    path.with_suffix(".meta.json").write_text(
        json.dumps(meta, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {path.relative_to(ROOT)} ({len(rows)} rows) + .meta.json")


def read_table(path: Path):
    """-> (rows, meta). `rows` keeps duplicate abbrevs; use `fold()` for lookups."""
    with path.open(encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh, delimiter="\t"))
    for r in rows:
        r["total"] = int(r["total"])
    meta_path = path.with_suffix(".meta.json")
    meta = json.loads(meta_path.read_text(encoding="utf-8")) if meta_path.exists() else {}
    return rows, meta


def fold(rows):
    """abbrev -> total. Duplicate abbrevs in pwgbib_input.txt are summed.

    Only the longest-prefix winner is ever incremented, so at most one member of a
    duplicate group is non-zero and the sum is that member's total.
    """
    out = {}
    for r in rows:
        out[r["abbrev"]] = out.get(r["abbrev"], 0) + r["total"]
    return out


def ambiguous_case_groups(rows):
    """casefolded abbrev -> {abbrev: total} where >1 case variant carries citations.

    Case is meaningful in the PWG bibliography (`Ś.` and `ś.` are different works), so a
    case-variant pair is normal. It only becomes a hazard when both variants are cited:
    any case-insensitive lookup onto such a group silently picks one of two real answers.
    """
    groups = {}
    for r in rows:
        groups.setdefault(r["abbrev"].lower(), []).append(r)
    return {k: {r["abbrev"]: r["total"] for r in v}
            for k, v in groups.items()
            if len({r["abbrev"] for r in v}) > 1 and sum(1 for r in v if r["total"]) > 1}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def git_commit(repo: Path) -> str:
    try:
        r = subprocess.run(["git", "-C", str(repo), "rev-parse", "HEAD"],
                           capture_output=True, encoding="utf-8", check=True)
        return r.stdout.strip()
    except Exception:  # noqa: BLE001 -- a missing sibling checkout is not fatal
        return ""


# ------------------------------------------------------------------------- the modes

def do_recount(pwg_repo: Path, csl_orig: Path) -> int:
    pwg_txt = csl_orig / "v02" / "pwg" / "pwg.txt"
    bib = pwg_repo / UPSTREAM_BIB
    for p in (pwg_txt, bib):
        if not p.exists():
            print(f"ERROR: missing input {p}", file=sys.stderr)
            return 2
    tips, totals, n_number, n_unknown = count_ls(pwg_txt, bib)
    rows = [{"total": n_number, "abbrev": NUMBER, "bib_code": "", "gloss": "ls starts with number"},
            {"total": n_unknown, "abbrev": UNKNOWN, "bib_code": "", "gloss": "ls is unknown"}]
    for i in sorted(range(len(tips)), key=lambda i: (-totals[i], tips[i][0])):
        code, abbrev, gloss = tips[i]
        rows.append({"total": totals[i], "abbrev": abbrev, "bib_code": code,
                     "gloss": re.sub(r"^.*? = ", "", gloss).replace("[Cologne Addition]", "")[:80]})
    total_all = sum(r["total"] for r in rows)
    meta = {
        "table": CURRENT_TABLE.name,
        "what": "PWG <ls> elements per bibliography abbreviation, longest-prefix rollup",
        "generated": date.today().isoformat(),
        "generator": "scripts/pwg_ls_counts.py (port of PWG lsextract_all.py)",
        "inputs": {
            "pwg_txt": {"path": "csl-orig/v02/pwg/pwg.txt", "sha256": sha256(pwg_txt),
                        "csl_orig_commit": git_commit(csl_orig)},
            "pwgbib_input": {"path": f"PWG/{UPSTREAM_BIB}", "sha256": sha256(bib),
                             "pwg_commit": git_commit(pwg_repo)},
        },
        "totals": {"ALL": total_all, "NUMBER": n_number, "UNKNOWN": n_unknown,
                   "attributed": total_all - n_number - n_unknown},
        "denominator_note": ("ALL is the only dictionary-wide denominator these counts "
                             "support; attributed excludes NUMBER and UNKNOWN buckets."),
    }
    write_table(CURRENT_TABLE, rows, meta)
    print(f"  ALL={total_all} NUMBER={n_number} UNKNOWN={n_unknown}")
    return 0


def do_verify_port(pwg_repo: Path, csl_orig: Path) -> int:
    """Run the upstream script and this port on identical inputs; require identity."""
    pwg_txt = csl_orig / "v02" / "pwg" / "pwg.txt"
    script = pwg_repo / UPSTREAM_SCRIPT
    bib = pwg_repo / UPSTREAM_BIB
    for p in (pwg_txt, script, bib):
        if not p.exists():
            print(f"ERROR: missing input {p}", file=sys.stderr)
            return 2
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        shutil.copy(script, tmp / "lsextract_all.py")
        shutil.copy(bib, tmp / "pwgbib_input.txt")
        shutil.copy(pwg_txt, tmp / "pwg.txt")
        r = subprocess.run([sys.executable, "lsextract_all.py", "pwg.txt",
                            "pwgbib_input.txt", "out.txt"],
                           cwd=tmp, capture_output=True, encoding="utf-8")
        if not (tmp / "out.txt").exists():
            print("ERROR: upstream script produced no output\n" + (r.stderr or "")[:2000],
                  file=sys.stderr)
            return 2
        theirs = (tmp / "out.txt").read_text(encoding="utf-8").splitlines()
    tips, totals, n_number, n_unknown = count_ls(pwg_txt, bib)
    mine = upstream_format(tips, totals, n_number, n_unknown, "X")
    ok = (len(mine) == len(theirs)
          and mine[0].split("\t")[0] == theirs[0].split("\t")[0]
          and mine[1:] == theirs[1:])
    if ok:
        print(f"PASS port == upstream lsextract_all.py on {len(mine)} lines "
              f"(ALL={mine[0].split(chr(9))[0]})")
        return 0
    print("FAIL port diverges from upstream", file=sys.stderr)
    for i, (a, b) in enumerate(zip(mine, theirs)):
        if a != b and i:
            print(f"  line {i}: port={a!r} upstream={b!r}", file=sys.stderr)
    return 1


def do_import_tracker_era(pwg_repo: Path) -> int:
    """Commit the 2024-09-11 upstream table -- the one the sheet's column was read off.

    Upstream writes three columns and drops the bibliography code; the code is rejoined
    here from the same era's `pwgbib_input.txt` so alias/case drift is checkable later.
    """
    src = pwg_repo / TRACKER_ERA_UPSTREAM
    bib = pwg_repo / TRACKER_ERA_BIB
    for p in (src, bib):
        if not p.exists():
            print(f"ERROR: missing input {p}", file=sys.stderr)
            return 2
    code_by_abbrev = {}
    for code, abbrev, _gloss in load_tooltips(bib):
        code_by_abbrev.setdefault(abbrev, code)

    rows = []
    as_of = ""
    total_all = None
    with src.open(encoding="utf-8") as fh:
        for line in fh:
            parts = line.rstrip("\n").split("\t")
            if len(parts) < 2 or not parts[0].strip().isdigit():
                continue
            total, abbrev = int(parts[0]), parts[1].strip()
            gloss = parts[2] if len(parts) > 2 else ""
            if abbrev == "ALL":
                total_all = total
                m = re.search(r"As of (\d{4}-\d{2}-\d{2})", gloss)
                as_of = m.group(1) if m else ""
                continue
            rows.append({"total": total, "abbrev": abbrev,
                         "bib_code": code_by_abbrev.get(abbrev, ""), "gloss": gloss})
    summed = sum(r["total"] for r in rows)
    meta = {
        "table": TRACKER_ERA_TABLE.name,
        "what": ("PWG <ls> elements per bibliography abbreviation, longest-prefix rollup -- "
                 "the table the scan-index tracker's `Citation count` column was read off"),
        "as_of": as_of,
        "generated_by_upstream": f"PWG/{TRACKER_ERA_UPSTREAM}",
        "upstream_sha256": sha256(src),
        "pwgbib_input": {"path": f"PWG/{TRACKER_ERA_BIB}", "sha256": sha256(bib)},
        "pwg_commit": git_commit(pwg_repo),
        "totals": {"ALL": summed,
                   "ALL_stated_upstream": total_all,
                   "NUMBER": next((r["total"] for r in rows if r["abbrev"] == NUMBER), None),
                   "UNKNOWN": next((r["total"] for r in rows if r["abbrev"] == UNKNOWN), None)},
        "note": ("Verbatim copy of the upstream count table, plus the bibliography code "
                 "rejoined by abbreviation. Never regenerate this file against newer "
                 "dictionary data -- it is the dated evidence for the tracker column."),
    }
    write_table(TRACKER_ERA_TABLE, rows, meta)
    print(f"  as_of={as_of} rows={len(rows)} ALL(sum)={summed} ALL(upstream)={total_all}")
    return 0


def do_check() -> int:
    """Offline self-consistency of the two committed tables."""
    fails = []
    for path in (TRACKER_ERA_TABLE, CURRENT_TABLE):
        if not path.exists():
            fails.append(f"missing committed table {path.relative_to(ROOT)}")
            continue
        rows, meta = read_table(path)
        stated = meta.get("totals", {}).get("ALL")
        actual = sum(r["total"] for r in rows)
        if stated is not None and stated != actual:
            fails.append(f"{path.name}: meta ALL={stated} but rows sum to {actual}")
        if not any(r["abbrev"] == NUMBER for r in rows):
            fails.append(f"{path.name}: no {NUMBER} bucket -- table is not a full partition")
        if not any(r["abbrev"] == UNKNOWN for r in rows):
            fails.append(f"{path.name}: no {UNKNOWN} bucket -- table is not a full partition")
        # Case is meaningful in this bibliography (`Ś.` and `ś.` are different works),
        # so case-variant abbreviations are expected, not a defect. What IS a defect is
        # a case-variant group where more than one member actually carries citations:
        # any case-insensitive join onto that group is then silently ambiguous.
        variants = {k for k, v in
                    {k: [r for r in rows if r["abbrev"].lower() == k] for k in
                     {r["abbrev"].lower() for r in rows}}.items()
                    if len({r["abbrev"] for r in v}) > 1}
        ambiguous = ambiguous_case_groups(rows)
        # Reported, not failed: the ambiguity lives in the upstream bibliography and is
        # not this repository's to resolve. The enforceable half of the rule is in
        # `pwg_citation_count_provenance.py`, which refuses a *tracker row* that joins
        # case-insensitively into one of these groups.
        print(f"  {path.name}: {len(rows)} buckets, {len(variants)} case-variant groups, "
              f"{len(ambiguous)} of them citation-bearing on both sides")
    for f in fails:
        print(f"FAIL {f}", file=sys.stderr)
    if fails:
        return 1
    print("PASS committed ls-count tables are self-consistent")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--recount", action="store_true",
                    help="regenerate the canonical current count table from pwg.txt")
    ap.add_argument("--verify-port", action="store_true",
                    help="run the upstream PWG script and require identical output")
    ap.add_argument("--import-tracker-era", action="store_true",
                    help="re-commit the dated 2024-09-11 upstream table (evidence, not a rebuild)")
    ap.add_argument("--check", action="store_true",
                    help="offline self-consistency check of the committed tables")
    ap.add_argument("--pwg-repo", type=Path, default=DEFAULT_PWG_REPO)
    ap.add_argument("--csl-orig", type=Path, default=DEFAULT_CSL_ORIG)
    args = ap.parse_args()

    if not (args.recount or args.verify_port or args.check or args.import_tracker_era):
        args.check = True
    rc = 0
    if args.verify_port:
        rc |= do_verify_port(args.pwg_repo, args.csl_orig)
    if args.import_tracker_era:
        rc |= do_import_tracker_era(args.pwg_repo)
    if args.recount:
        rc |= do_recount(args.pwg_repo, args.csl_orig)
    if args.check:
        rc |= do_check()
    return rc


if __name__ == "__main__":
    sys.exit(main())
