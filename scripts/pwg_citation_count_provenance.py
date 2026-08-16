#!/usr/bin/env python3
"""Provenance of the PWG scan-index tracker's `Citation count`, and the denominator contract (H2874).

H1706 committed the volunteer tracker as data and recorded its `Citation count` column as
having **unresolved provenance**: it reproduced neither the bare cleaned-string counts nor a
leading-abbreviation rollup of the `sortedcrefs.txt` extraction, the sheet/extraction ratio
ranged 1.2x-433x, and the caveat was "rank with it, never divide by it".

That provenance is now recovered. The column is the per-abbreviation total from
`lsextract_all.txt` as committed in sanskrit-lexicon/PWG `pwgissues/issue74/`, dated
**2024-09-11**, `ALL = 739,056`: a longest-prefix rollup of every `<ls>` element in `pwg.txt`
onto the bibliography abbreviations of `pwgbib_input.txt`. 66 of the 67 rows that carry a
value match that table exactly; the 67th (`NAIGH.`) is a near-miss carried below with its
evidence rather than smoothed away.

Why H1706 could not find it: it compared against a *different* extraction --
`pwg_ls/pwg_dhaval/abbrvwork/abbrvoutput/sortedcrefs.txt`, which keys on the cleaned citation
string (`MED.`, `MED. k.`, `MED. kh.` are three keys) and applies a restrictive "proper
reference" filter, totalling 344,229. The tracker's source keys on the *book*. The two were
never the same measurement, and the ratio spread H1706 measured is exactly that difference.

Outputs:

1. `data/pwg_scan_index_tracker/pwg_citation_count_provenance.tsv` -- one row per tracked
   source: the tracker value, the source-table bucket it came from, how the key matched, the
   provenance verdict, and the independently regenerated current count.
2. `reports/pwg_citation_count_provenance.md` -- the memo, including the hypothesis log.

`--check` is the contract gate. It fails on:

* a tracker value with no established provenance;
* a row whose key joins case-insensitively into a citation-bearing case-variant group
  (the join would silently pick one of two real works);
* two rows of the same bibliography family both carrying a value (summing them double-counts
  the family, because the source field is a family-level prefix rollup);
* a total over the tracker column exceeding its own denominator, which would prove the above.

Run:  python scripts/pwg_citation_count_provenance.py
      python scripts/pwg_citation_count_provenance.py --check
"""

import argparse
import csv
import json
import sys
from collections import defaultdict
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from pwg_ls_counts import (  # noqa: E402
    CURRENT_TABLE, TRACKER_ERA_TABLE, ambiguous_case_groups, fold, read_table)

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parents[1]
TRACKER_DIR = ROOT / "data" / "pwg_scan_index_tracker"
REGISTRY = TRACKER_DIR / "pwg_scan_index.tsv"
OUT_TSV = TRACKER_DIR / "pwg_citation_count_provenance.tsv"
OUT_MD = ROOT / "reports" / "pwg_citation_count_provenance.md"

REPO_BLOB = "https://github.com/sanskrit-lexicon/csl-observatory/blob/main"
PWG_BLOB = "https://github.com/sanskrit-lexicon/PWG/blob/master"

# The one row that does not match the source table exactly. Kept as data, not as a fix:
# NAIGH. reads 1,477 in the sheet against 1,417 in the 2024-09-11 table. No committed
# snapshot of the count carries 1,477 (2023-01-13: 1,378; 2024-09-11: 1,417; 2026-06-24:
# 1,456), so a later re-read cannot explain it and a single-digit slip 1417 -> 1477 is the
# only reading the evidence supports. It is recorded as a near-miss, never corrected.
NEAR_MISS_TOLERANCE = 100

STATUS_EXACT = "exact"
STATUS_NEAR = "near-miss"
STATUS_INHERITED = "inherited-family"
STATUS_UNMATCHED = "unmatched"

FIELDS = [
    "sheet_row_no", "ls_code", "ls_code_raw", "in_pwgbib", "status",
    "tracker_value", "source_key", "source_match", "source_value", "citation_count_safe",
    "provenance", "delta", "confidence",
    "canonical_value", "canonical_denominator", "drift_since_source", "evidence",
]


def load_registry():
    with REGISTRY.open(encoding="utf-8") as fh:
        return list(csv.DictReader(fh, delimiter="\t"))


def match_key(candidates, table):
    """Resolve a tracker row's abbreviation onto a count table.

    Returns (key, kind) where kind is verbatim / case-fold, or (None, "") if nothing matched.
    Deliberately no fuzzy or prefix fallback: a wrong bucket here is a wrong number.
    """
    lower = {k.lower(): k for k in table}
    for cand in candidates:
        if not cand:
            continue
        if cand in table:
            return cand, "verbatim"
    for cand in candidates:
        if cand and cand.lower() in lower:
            return lower[cand.lower()], "case-fold"
    return None, ""


def build():
    src_rows, src_meta = read_table(TRACKER_ERA_TABLE)
    cur_rows, cur_meta = read_table(CURRENT_TABLE)
    src, cur = fold(src_rows), fold(cur_rows)
    src_all = src_meta["totals"]["ALL"]
    cur_all = cur_meta["totals"]["ALL"]
    src_ambiguous = ambiguous_case_groups(src_rows)

    out = []
    for r in load_registry():
        cands = [r["in_pwgbib"].strip(), r["ls_code_base"].strip(), r["ls_code"].strip()]
        key, kind = match_key(cands, src)
        ckey, _ = match_key(cands, cur)
        raw = r["citation_count"].strip().replace(",", "")
        value = int(raw) if raw.isdigit() else None
        source_value = src.get(key) if key else None
        canonical = cur.get(ckey) if ckey else None

        if value is None:
            provenance, delta, confidence = STATUS_INHERITED, "", "certain"
        elif source_value is None:
            provenance, delta, confidence = STATUS_UNMATCHED, "", "unresolved"
        elif value == source_value:
            provenance, delta, confidence = STATUS_EXACT, 0, "certain"
        elif abs(value - source_value) <= NEAR_MISS_TOLERANCE:
            provenance, delta, confidence = STATUS_NEAR, value - source_value, "probable"
        else:
            provenance, delta, confidence = STATUS_UNMATCHED, value - source_value, "unresolved"

        out.append({
            "sheet_row_no": r["sheet_row_no"],
            "ls_code": r["ls_code"],
            "ls_code_raw": r["ls_code_raw"],
            "in_pwgbib": r["in_pwgbib"],
            "status": r["status"],
            "tracker_value": value if value is not None else "",
            "source_key": key or "",
            "source_match": kind,
            "source_value": source_value if source_value is not None else "",
            # The only value a consumer may put in a numerator or a denominator: the
            # source table's own number, present exactly when this row asserts a count
            # AND that count is traceable. A near-miss contributes its *source* value,
            # never the sheet's transcription of it; an unresolved row contributes
            # nothing at all.
            "citation_count_safe": (source_value if (value is not None
                                                     and source_value is not None
                                                     and provenance != STATUS_UNMATCHED)
                                    else ""),
            "provenance": provenance,
            "delta": delta,
            "confidence": confidence,
            "canonical_value": canonical if canonical is not None else "",
            "canonical_denominator": cur_all,
            "drift_since_source": (canonical - source_value)
                                  if (canonical is not None and source_value is not None) else "",
            "evidence": f"{REPO_BLOB}/data/pwg_scan_index_tracker/ls_counts/{TRACKER_ERA_TABLE.name}",
        })
    return out, src_meta, cur_meta, src_all, cur_all, src_ambiguous


# ------------------------------------------------------------------------ the contract

def safe_total(rows) -> int:
    return sum(int(r["citation_count_safe"]) for r in rows if r["citation_count_safe"] != "")


def check(rows, src_all, src_ambiguous) -> list:
    """The denominator contract. Returns a list of failures; empty means the gate passes."""
    fails = []

    unproven = [r for r in rows if r["tracker_value"] != "" and r["confidence"] == "unresolved"]
    if unproven:
        fails.append("tracker values with no established provenance: "
                     + ", ".join(f"{r['ls_code']}={r['tracker_value']}" for r in unproven))

    for r in rows:
        if r["source_match"] == "case-fold" and r["source_key"].lower() in src_ambiguous:
            fails.append(f"{r['ls_code']}: case-insensitive join onto the citation-bearing "
                         f"case-variant group {src_ambiguous[r['source_key'].lower()]}")

    # The source field is a family-level prefix rollup: `AK. Deslongchamps ed.` and
    # `AK. Colebrooke ed.` both read AK.'s total. The sheet already guards this by writing
    # the value on one row of a family only; if that ever breaks, every family total is
    # double-counted downstream.
    families = defaultdict(list)
    for r in rows:
        if r["tracker_value"] != "" and r["in_pwgbib"]:
            families[r["in_pwgbib"]].append(r["ls_code"])
    dupes = {k: v for k, v in families.items() if len(v) > 1}
    if dupes:
        fails.append(f"bibliography families carrying a value on more than one row: {dupes}")

    for r in rows:
        if r["tracker_value"] != "" and r["citation_count_safe"] == "" \
                and r["confidence"] != "unresolved":
            fails.append(f"{r['ls_code']}: asserts a count but exposes no safe value")

    total = safe_total(rows)
    if total > src_all:
        fails.append(f"safe counts sum to {total}, above their own denominator {src_all} "
                     "-- the column is being double-counted")

    return fails


# --------------------------------------------------------------------------- rendering

def fmt(n):
    return f"{n:,}" if isinstance(n, int) else str(n)


def write_tsv(rows):
    with OUT_TSV.open("w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=FIELDS, delimiter="\t", lineterminator="\n")
        w.writeheader()
        w.writerows(rows)
    print(f"wrote {OUT_TSV.relative_to(ROOT)} ({len(rows)} rows)")


def write_report(rows, src_meta, cur_meta, src_all, cur_all, src_ambiguous):
    today = date.today().strftime("%d-%m-%Y")
    valued = [r for r in rows if r["tracker_value"] != ""]
    exact = [r for r in valued if r["provenance"] == STATUS_EXACT]
    near = [r for r in valued if r["provenance"] == STATUS_NEAR]
    unres = [r for r in valued if r["provenance"] == STATUS_UNMATCHED]
    inherited = [r for r in rows if r["provenance"] == STATUS_INHERITED]
    total = safe_total(rows)

    lines = []
    A = lines.append
    A("# PWG tracker `Citation count` — provenance recovered, and the denominator contract")
    A("")
    A(f"_Created: {today} · Last updated: {today}_")
    A("")
    A("H1706 committed the PWG scan-index tracker as data and recorded its `Citation count` "
      "column as having unresolved provenance — usable for ranking, barred from any "
      "denominator. This pass resolves it against committed evidence and replaces the ban "
      "with a contract.")
    A("")
    A("## 1 · The verdict")
    A("")
    A(f"The column is the per-abbreviation total of [`pwgissues/issue74/lsextract_all.txt`]"
      f"({PWG_BLOB}/pwgissues/issue74/lsextract_all.txt) in sanskrit-lexicon/PWG, the count "
      f"table dated **{src_meta.get('as_of')}** with `ALL = {fmt(src_all)}`. Of the "
      f"{len(valued)} tracked rows that carry a value, **{len(exact)} match that table "
      f"exactly**, {len(near)} is a near-miss, {len(unres)} are unresolved. The remaining "
      f"{len(inherited)} rows carry no value of their own because the sheet writes a "
      "family's count once and `- - -` on its sibling volumes.")
    A("")
    A("The table is committed here as the input of record, so this claim is checkable "
      f"offline: [`ls_counts/{TRACKER_ERA_TABLE.name}`]"
      f"({REPO_BLOB}/data/pwg_scan_index_tracker/ls_counts/{TRACKER_ERA_TABLE.name}).")
    A("")
    A("## 2 · What the number counts")
    A("")
    A("Per [`lsextract_all.py`](" + PWG_BLOB + "/pwgissues/issue94/lsextract_all.py), for every "
      "`<ls …>…</ls>` element in the PWG digitization:")
    A("")
    A("1. an `n=\"…\"` attribute value, where present, is prepended to the element text;")
    A("2. text beginning with a digit counts as `NUMBER`;")
    A("3. otherwise the element goes to the **longest bibliography abbreviation in "
      "`pwgbib_input.txt` that is a prefix of that text** — `MED. k. 12` and `MED. kh.` "
      "both count towards `MED.`;")
    A("4. text with no such prefix counts as `UNKNOWN`.")
    A("")
    A("Every element lands in exactly one bucket, so the buckets partition the dictionary "
      f"and `ALL` is a real denominator. Three consequences follow, and they are the whole "
      "of the contract:")
    A("")
    A("- The number is a **work family**, not a citation string. That is why H1706's "
      "comparison against the cleaned-string extraction diverged by 1.2×–433×: `MED.` has "
      "30 bare-string occurrences and 12,990 family occurrences, and both are correct "
      "counts of different objects.")
    A("- Sibling rows of one family (`AK. Deslongchamps ed.` / `AK. Colebrooke ed.`, the six "
      "`MBh. (Bomb.)` volumes) share **one** total. Summing them double-counts, which is "
      "why the sheet writes the value once per family and the contract check below "
      "enforces exactly that.")
    A("- A percentage is only meaningful against the `ALL` of the **same snapshot**. Mixing "
      "the 2024-09-11 column with a 2026 denominator understates by the drift measured in "
      "§5.")
    A("")
    A("## 3 · Per-row provenance")
    A("")
    A("Full dataset: [`pwg_citation_count_provenance.tsv`]"
      f"({REPO_BLOB}/data/pwg_scan_index_tracker/pwg_citation_count_provenance.tsv) "
      f"({len(rows)} rows). Summary:")
    A("")
    A("| provenance | rows | meaning |")
    A("|---|--:|---|")
    A(f"| `{STATUS_EXACT}` | {len(exact)} | the tracker value is the source table's value for "
      "that abbreviation, digit for digit |")
    A(f"| `{STATUS_NEAR}` | {len(near)} | within {NEAR_MISS_TOLERANCE} of the source value and "
      "matched by no other snapshot; a transcription slip |")
    A(f"| `{STATUS_UNMATCHED}` | {len(unres)} | value present, source value not reproduced |")
    A(f"| `{STATUS_INHERITED}` | {len(inherited)} | no value in the sheet; the family's count "
      "sits on another row |")
    A("")
    if near or unres:
        A("The rows that are not exact:")
        A("")
        A("| LS code | tracker | source table | delta | reading |")
        A("|---|--:|--:|--:|---|")
        for r in near + unres:
            reading = ("single-digit transcription slip; no committed snapshot of the count "
                       "carries the tracker's value") if r["provenance"] == STATUS_NEAR else \
                      "unresolved — do not use this row's value for anything but ordering"
            A(f"| `{r['ls_code']}` | {fmt(int(r['tracker_value']))} | "
              f"{fmt(int(r['source_value'])) if r['source_value'] != '' else '—'} | "
              f"{r['delta']} | {reading} |")
        A("")
    A("## 4 · The denominator contract")
    A("")
    A("`python scripts/pwg_citation_count_provenance.py --check` is the gate, and it fails "
      "on any of:")
    A("")
    A("| # | rejected | why |")
    A("|---|---|---|")
    A("| 1 | a tracker value whose provenance is unresolved | an unproven number must not "
      "reach a report, let alone a denominator |")
    A("| 2 | a row whose abbreviation joins case-insensitively onto a citation-bearing "
      "case-variant group | the PWG bibliography distinguishes `Ś.` from `ś.`; a case-folded "
      f"join silently picks one of two real works ({len(src_ambiguous)} such groups exist) |")
    A("| 3 | two rows of one bibliography family both carrying a value | the field is a "
      "family rollup; the pair double-counts |")
    A("| 4 | a row asserting a count but exposing no safe value | the two columns have "
      "drifted apart and downstream would read the wrong one |")
    A("| 5 | the safe counts summing above their own `ALL` | proof that 3 has already "
      "happened |")
    A("")
    A("The field a consumer may divide by is **`citation_count_safe`**, never "
      "`tracker_value`. It carries the source table's own number, blank wherever a row's "
      "provenance is unresolved, so an unproven value has no arithmetic path into a "
      "coverage percentage.")
    A("")
    A(f"Today the safe counts sum to **{fmt(total)}** against a denominator of "
      f"**{fmt(src_all)}** — {100.0 * total / src_all:.1f}% of the dictionary's `<ls>` "
      "apparatus sits on a tracked source.")
    A("")
    A("## 5 · The canonical field, and drift")
    A("")
    A("The tracker column is frozen evidence from 2024-09-11. For anything computed today, "
      f"`canonical_value` in the dataset is regenerated from current dictionary data by "
      f"[`scripts/pwg_ls_counts.py --recount`]({REPO_BLOB}/scripts/pwg_ls_counts.py) into "
      f"[`ls_counts/{CURRENT_TABLE.name}`]"
      f"({REPO_BLOB}/data/pwg_scan_index_tracker/ls_counts/{CURRENT_TABLE.name}), "
      f"`ALL = {fmt(cur_all)}` as of {cur_meta.get('generated')}. That regeneration is a port "
      "of the upstream generator, and `--verify-port` runs both on identical inputs and "
      "requires byte-identical output.")
    A("")
    drifted = [r for r in rows if r["drift_since_source"] not in ("", 0)]
    if drifted:
        top = sorted(drifted, key=lambda r: -abs(int(r["drift_since_source"])))[:10]
        A(f"{len(drifted)} of {len(rows)} rows moved between the two snapshots — the ls-tag "
          "correction campaigns are visible in the counts. Largest movements:")
        A("")
        A("| LS code | 2024-09-11 | current | drift |")
        A("|---|--:|--:|--:|")
        for r in top:
            A(f"| `{r['ls_code']}` | {fmt(int(r['source_value']))} | "
              f"{fmt(int(r['canonical_value']))} | {int(r['drift_since_source']):+,} |")
        A("")
    A("Two of those movements are not growth. `an.` falls from 1,797 to 1 while `H. an.` "
      "rises by 2,075: the bibliography entry for `an.` is byte-identical in both eras, so "
      "the citations were **re-tagged** in the dictionary, not recounted. A tracker refresh "
      "that silently replaced the 2024 column with today's numbers would therefore report a "
      "finished index as having almost nothing left to serve. This is the concrete reason "
      "the frozen column is kept as evidence and the canonical field is carried beside it "
      "rather than over it.")
    A("")
    A("Drift also mixes two causes: the dictionary changed, and so did `pwgbib_input.txt` "
      "(the newer table carries additional buckets, and its case-variant inventory differs). "
      "Attribute a movement to re-tagging only after "
      "checking the bibliography entry on both sides, as was done for `an.` above.")
    A("")
    A("## 6 · Hypotheses tested")
    A("")
    A("Recorded so the next session does not re-run them.")
    A("")
    A("| # | hypothesis | verdict |")
    A("|---|---|---|")
    A("| 1 | bare cleaned-citation-string counts (`sortedcrefs.txt`) | rejected — H1706; "
      "1.2×–433× spread |")
    A("| 2 | leading-abbreviation rollup of those same cleaned strings | rejected — H1706 |")
    A("| 3 | rollup of the `pwgls.txt` abbreviation database by bibliography code | rejected "
      "— reproduces the ordering but not one value; ratios 1.03×–650× |")
    A("| 4 | one of the dated `lsextract_pwg_*.txt` tables in `pwg_ls2/` (2022–2023 runs) | "
      "rejected — 2 of 67 rows match, by coincidence of small numbers |")
    A("| 5 | the `lsextract_all.txt` table committed under `pwgissues/issue74/`, 2024-09-11 | "
      f"**confirmed** — {len(exact)}/{len(valued)} exact |")
    A("")
    A("Hypothesis 5 was reached by comparing the tracker column against every count table "
      "in the PWG repository mechanically, rather than by reasoning about which extraction "
      "*ought* to have been used — the reasoning path is what failed in H1706.")
    A("")
    A("## 7 · What this does not settle")
    A("")
    A("- **Which human ran that extraction, and when they pasted it into the sheet**, is "
      "still unrecorded. The provenance established here is of the *number*, from committed "
      "artefacts; it does not need the coordinator's testimony, and it does not replace it.")
    A(f"- **`NAIGH.`** stays a near-miss. The count reads 1,378 (2023-01-13), 1,417 "
      "(2024-09-11) and 1,456 (2026-06-24) across committed snapshots; the sheet's 1,477 "
      "matches none of them.")
    A("- **The 2024-09-11 pwg.txt itself** is not re-derivable here: the local `csl-orig` "
      "checkout is shallow and does not reach that date. The recovery rests on the "
      "committed *output* table, not on re-running the generator against era-matched input.")
    A("")
    A("_Dr. Mārcis Gasūns_")
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"wrote {OUT_MD.relative_to(ROOT)}")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--check", action="store_true", help="run the contract gate only")
    args = ap.parse_args()

    rows, src_meta, cur_meta, src_all, cur_all, src_ambiguous = build()
    fails = check(rows, src_all, src_ambiguous)

    if not args.check:
        write_tsv(rows)
        write_report(rows, src_meta, cur_meta, src_all, cur_all, src_ambiguous)

    for f in fails:
        print(f"FAIL {f}", file=sys.stderr)
    if fails:
        return 1
    valued = [r for r in rows if r["tracker_value"] != ""]
    print(f"PASS denominator contract: {len(rows)} rows, {len(valued)} valued, "
          f"safe sum={safe_total(rows):,} of {src_all:,}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
