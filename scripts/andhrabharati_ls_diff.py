# -*- coding: utf-8 -*-
"""Compare PWG-ls.txt (distinct <ls> values in PWG) against the CDSL pwgauth list.

CDSL list = csl-pywork/v02/distinctfiles/pwg/pywork/pwgauth/pwgbib_input.txt
Field 2 (tab-delimited) is the abbreviation code.

Outputs (data/pwg_scan_index_tracker/andhrabharati_ls_diff/):
  pwg_ls_vs_cdsl_added.tsv    ls values with NO bib entry  (candidates to ADD)
  pwg_ls_vs_cdsl_deleted.tsv  bib entries with NO ls cite  (candidates to DELETE)
  pwg_ls_vs_cdsl_report.md    numbers + method
"""
import csv
import sys
import unicodedata
from collections import Counter
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

DATA = Path(__file__).parent.parent / "data" / "pwg_scan_index_tracker" / "andhrabharati_ls_diff"
HERE = DATA
LS_FILE = HERE / "PWG-ls.txt"
BIB_FILE = Path(r"C:\Users\user\Documents\GitHub\csl-pywork\v02\distinctfiles\pwg\pywork\pwgauth\pwgbib_input.txt")


def norm(s: str) -> str:
    """NFC + collapse internal whitespace + strip. Case preserved (case is
    meaningful in this bibliography — S. vs s. are different works)."""
    s = unicodedata.normalize("NFC", s)
    return " ".join(s.split())


def main() -> None:
    # --- load ls values -------------------------------------------------
    ls_raw = [ln.rstrip("\n").rstrip("\r") for ln in LS_FILE.read_text("utf-8").splitlines()]
    ls_vals = [v for v in (norm(x) for x in ls_raw) if v]
    ls_counter = Counter(ls_vals)
    dup_ls = {v: c for v, c in ls_counter.items() if c > 1}
    ls_set = set(ls_counter)

    # --- load bib codes -------------------------------------------------
    rows = []
    with BIB_FILE.open("r", encoding="utf-8") as f:
        for rec in csv.reader(f, delimiter="\t", quoting=csv.QUOTE_NONE):
            if not rec or not rec[0].strip():
                continue
            rows.append(rec)
    codes = [norm(r[1]) for r in rows if len(r) >= 2]
    code_counter = Counter(codes)
    dup_codes = {v: c for v, c in code_counter.items() if c > 1}
    code_set = set(code_counter)

    # --- exact set ops ---------------------------------------------------
    added = sorted(ls_set - code_set)      # cited in dictionary, no bib entry
    deleted = sorted(code_set - ls_set)    # bib entry, never cited in PWG-ls
    common = ls_set & code_set

    # --- how much residue is just case noise? ----------------------------
    lower_code = {v.casefold(): v for v in code_set}
    lower_ls = {v.casefold(): v for v in ls_set}
    added_case_resolved = []   # ls value whose casefold IS a bib code's casefold
    added_real = []
    for a in added:
        if a.casefold() in lower_code:
            added_case_resolved.append((a, lower_code[a.casefold()]))
        else:
            added_real.append(a)
    deleted_case_resolved = []  # bib code whose casefold IS an ls value's casefold
    deleted_real = []
    for d in deleted:
        if d.casefold() in lower_ls:
            deleted_case_resolved.append((d, lower_ls[d.casefold()]))
        else:
            deleted_real.append(d)

    # --- prefix attribution (CDSL longest-prefix method) ------------------
    def longest_prefix(s: str, pool: set) -> str | None:
        best = None
        for c in pool:
            if s.startswith(c) and (best is None or len(c) > len(best)):
                best = c
        return best

    added_pref = []     # added string extends some bib code (qualifier/volume/comm.)
    added_unknown = []  # no bib code prefixes it
    for a in added_real:
        p = longest_prefix(a, code_set)
        (added_pref if p else added_unknown).append((a, p))
    deleted_pref = [d for d in deleted_real
                    if any(l.startswith(d) and l != d for l in ls_set)]
    deleted_uncited = [d for d in deleted_real if d not in set(deleted_pref)]

    # --- write TSVs -------------------------------------------------------
    with (HERE / "pwg_ls_vs_cdsl_added.tsv").open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f, delimiter="\t")
        w.writerow(["ls_value", "case_match_to_bib_code", "times_cited_in_ls_file",
                    "extends_bib_code_prefix", "class"])
        pref_map = dict(added_pref)
        for a in added:
            cm = dict(added_case_resolved).get(a, "")
            p = pref_map.get(a, "")
            cls = "extends-known-code" if p else ("case-variant" if cm else "unknown")
            w.writerow([a, cm, ls_counter[a], p, cls])
    with (HERE / "pwg_ls_vs_cdsl_unknown.tsv").open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f, delimiter="\t")
        w.writerow(["ls_value", "times_cited"])
        for a, _ in added_unknown:
            w.writerow([a, ls_counter[a]])

    with (HERE / "pwg_ls_vs_cdsl_deleted.tsv").open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f, delimiter="\t")
        w.writerow(["bib_code", "pwgab_id"])
        id_by_code = {}
        for r in rows:
            if len(r) >= 2:
                id_by_code.setdefault(norm(r[1]), []).append(r[0])
        for d in deleted:
            w.writerow([d, ";".join(id_by_code.get(d, []))])

    # --- report -----------------------------------------------------------
    rep = []
    rep.append("# PWG-ls vs CDSL pwgauth — comparison report")
    rep.append("")
    rep.append("_Generated: 24-09-2026 · comparison script `pwg_ls_vs_cdsl_compare.py`, this pass._")
    rep.append("")
    rep.append("## Inputs")
    rep.append("")
    rep.append(f"- `PWG-ls.txt`: {len(ls_raw)} lines → {len(ls_counter)} distinct non-empty normalized values"
               f" ({len(dup_ls)} duplicated values, max repeat {max(ls_counter.values()) if ls_counter else 0})")
    rep.append(f"- `pwgbib_input.txt` (CDSL pwgauth): {len(rows)} records → {len(code_set)} distinct codes"
               f" ({len(dup_codes)} codes appearing on 2+ records)")
    rep.append("- Normalization: NFC + whitespace collapse; case PRESERVED (case is meaningful in this bibliography).")
    rep.append("")
    rep.append("## Provenance & interpretation (MG ruling, grill 24-09-2026)")
    rep.append("")
    rep.append("- `PWG-ls.txt` is **Andhrabharati's update to CDSL** (MG: «The .txt file give is what Andhrabharati")
    rep.append("  made, it's an update to CDSL»), sha256")
    rep.append("  `f44ae1bbccca1ceb508e9da0c1c389dcb93910fb570d0a4d962819cf756b5fd0`.")
    rep.append("- So ADDED = abbreviations **new in the Andhrabharati update**, DELETED = abbreviations **present in")
    rep.append("  CDSL pwgbib but dropped by Andhrabharati**. No deletion queues are built from this report —")
    rep.append("  «No need to delete … No hand queue, do full auto comparison» (MG 24-09-2026).")
    rep.append("")
    rep.append("## Headline numbers (exact match)")
    rep.append("")
    rep.append(f"- Matched (in both): **{len(common)}**")
    rep.append(f"- ADDED candidates (cited as `<ls>` in PWG-ls, NO pwgbib code): **{len(added)}**")
    rep.append(f"- DELETED candidates (pwgbib code, never appears in PWG-ls): **{len(deleted)}**")
    rep.append("")
    rep.append("## Case-only residue")
    rep.append("")
    rep.append(f"- of the ADDED set, {len(added_case_resolved)} differ from some bib code only by letter case")
    rep.append(f"- of the DELETED set, {len(deleted_case_resolved)} have a case-variant present in PWG-ls")
    rep.append(f"- true ADDED after case pass: **{len(added_real)}** · true DELETED after case pass: **{len(deleted_real)}**")
    rep.append("")
    rep.append("## Prefix attribution (CDSL longest-prefix method)")
    rep.append("")
    rep.append(f"- ADDED: {len(added_pref)} of {len(added_real)} extend a known bib code (volume/edition/commentary/"
               f"qualifier suffixes) — true UNKNOWN residue: **{len(added_unknown)}**")
    rep.append(f"- DELETED: {len(deleted_pref)} of {len(deleted_real)} are prefixes of longer cited ls values "
               f"(cited in extended form) — totally uncited: **{len(deleted_uncited)}**")
    rep.append("")
    rep.append("## Duplicates inside each list")
    rep.append("")
    if dup_codes:
        rep.append(f"- pwgbib_input duplicate codes: {len(dup_codes)} — {sorted(dup_codes)[:10]} …")
    if dup_ls:
        rep.append(f"- PWG-ls duplicated values: {len(dup_ls)} — {sorted(dup_ls)[:10]} …")
    rep.append("")
    rep.append("## Samples")
    rep.append("")
    rep.append("### first 25 ADDED candidates")
    for a in added[:25]:
        rep.append(f"- `{a}` (×{ls_counter[a]})")
    rep.append("")
    rep.append("### first 25 DELETED candidates")
    for d in deleted[:25]:
        rep.append(f"- `{d}`")
    rep.append("")
    rep.append("### first 25 truly-UNKNOWN added candidates (no bib prefix)")
    for a, _ in added_unknown[:25]:
        rep.append(f"- `{a}` (×{ls_counter[a]})")
    rep.append("")
    rep.append("### first 25 added that extend a known bib code")
    for a, p in added_pref[:25]:
        rep.append(f"- `{a}` ← extends `{p}`")
    rep.append("")
    rep.append("### first 25 totally-uncited deleted candidates")
    for d in deleted_uncited[:25]:
        rep.append(f"- `{d}`")
    (HERE / "pwg_ls_vs_cdsl_report.md").write_text("\n".join(rep) + "\n", encoding="utf-8")

    print(f"ls distinct: {len(ls_counter)}  |  bib codes distinct: {len(code_set)}")
    print(f"matched: {len(common)}  added: {len(added)} (true after case: {len(added_real)})  deleted: {len(deleted)} (true after case: {len(deleted_real)})")
    print(f"added prefix-resolved: {len(added_pref)}  unknown: {len(added_unknown)}  |  deleted prefix-cited: {len(deleted_pref)}  uncited: {len(deleted_uncited)}")


if __name__ == "__main__":
    main()
