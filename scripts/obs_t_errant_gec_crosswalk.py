#!/usr/bin/env python3
"""OBS-T <-> ERRANT/GEC + historical-text-normalization per-cell crosswalk (H6389).

Reporting transform only — no system re-run, no labels recomputed. Reads the
released correction-event corpus and re-expresses every occupied (location x
edit-type) cell of the two-axis typology in published shared-task terms:

* nearest ERRANT / GEC error-type category (Bryant, Felice & Briscoe 2017,
  aclanthology.org/P17-1074; ERRANT v3, github.com/chrisjbryant/errant)
* nearest historical-text-normalization reporting term (Bollmann 2019,
  aclanthology.org/N19-1389; Baron & Rayson 2008 VARD2)

Mismatched cells are flagged UNPLACEABLE / PARTIAL, never forced. The location
axis itself has no published analogue: ERRANT/GEC/normalization are
location-blind — every cell therefore carries the location dimension on OBS-T
alone, and that is reported as the structural mismatch it is.

Writes the generated per-cell table into
docs/OBST_ERRANT_GEC_CROSSWALK.md between the GENERATED markers (idempotent;
--check exits 1 on drift). Narrative sections of that doc are hand-authored.

Usage:
    python scripts/obs_t_errant_gec_crosswalk.py            # regenerate
    python scripts/obs_t_errant_gec_crosswalk.py --check    # verify byte-identical
"""
import csv, os, re, sys
from collections import Counter

sys.stdout.reconfigure(encoding="utf-8"); sys.stderr.reconfigure(encoding="utf-8")
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DOC = os.path.join(ROOT, "docs", "OBST_ERRANT_GEC_CROSSWALK.md")
DATA = os.path.join(ROOT, "observatory", "site", "src", "data",
                    "correction_events_release.csv")

BEGIN = "<!-- BEGIN GENERATED per-cell table (scripts/obs_t_errant_gec_crosswalk.py) -- DO NOT HAND-EDIT -->"
END = "<!-- END GENERATED per-cell table -->"

# --- the committed judgment: nearest published category per edit-type --------
# status: PLACEABLE (direct nearest category) / PARTIAL (nearest category with
# a named caveat) / UNPLACEABLE (no published category; mismatch is reported,
# not papered over).
EDIT_TYPE_MAP = {
    # edit-type: (nearest ERRANT/GEC category, normalization term, status, caveat)
    "spelling": ("R:SPELL", "word-form variant (normalization target)", "PLACEABLE",
                 "ERRANT R:SPELL covers letter-changing misspellings (README worked example); OBS-T spelling edits over romanised Sanskrit are the same class of surface letter repair."),
    "diacritic": ("R:SPELL", "character-level variant (diacritic recovery)", "PARTIAL",
                 "ERRANT has no dedicated diacritic class (English-centric); a combining-mark fix is a letter-level substitution nearest R:SPELL. Historical-normalization evaluation counts these as character-level variants."),
    "case": ("R:ORTH", "not a normalization category (orthography fixed in the target language)", "PLACEABLE",
                 "R:ORTH is ERRANT's orthographic (case-preserving-letters) class; OBS-T case edits on romanised forms map to it directly."),
    "spacing": ("M:/R:/U:PUNCT (token-boundary operation)", "segmentation (word merge/split)", "PARTIAL",
                 "ERRANT expresses merges/splits as punctuation-adjacent M/R/U operations on the token boundary; the exact v3 subcategory for pure whitespace was not verified against the full category table in this pass, so the assignment is stated at operation level."),
    "punctuation": ("M:/R:/U:PUNCT", "not a normalization category (punctuation modernisation is reported separately)", "PLACEABLE",
                 "Direct map to ERRANT's punctuation class."),
    "digit": ("R:/M:OTHER", "not a normalization category", "PARTIAL",
                 "ERRANT has no dedicated numeric class; nearest is OTHER. Kept visible rather than folded into spelling."),
    "transposition": ("R:SPELL / R:OTHER", "metathesis (classical scribal category)", "PARTIAL",
                 "ERRANT has no transposition operation; a token-internal letter swap lands in SPELL/OTHER. Textual criticism (Katre) and OBS-T's own OCR class name it metathesis/transposition — the honest home."),
    "source-raw": ("—", "—", "UNPLACEABLE",
                 "Edits typed in the raw SLP1/markup character space are transliteration- or markup-space operations, not natural-language surface errors; neither ERRANT/GEC nor historical normalization has a category for them."),
    "none": ("—", "—", "UNPLACEABLE",
                 "No typed edit operation in the trace (identity/metadata events); no external scheme places an empty edit."),
}

# Locations the external tasks cannot see (entry-microstructure semantics).
LOCATION_BLIND = ("ERRANT/GEC/normalization annotate sentence-internal edits and carry no "
                  "entry-microstructure semantics: the location dimension of every cell "
                  "rides on OBS-T alone.")


def cell_label(loc, et):
    """Nearest published category for one (location x edit-type) cell."""
    cat, norm, status, caveat = EDIT_TYPE_MAP[et]
    return cat, norm, status, caveat


def build_rows():
    cells = Counter(); total = 0
    with open(DATA, encoding="utf-8") as f:
        for r in csv.DictReader(f):
            cells[(r["error_component"], r["edit_type"])] += 1
            total += 1
    rows = []
    for (loc, et), n in cells.most_common():
        cat, norm, status, caveat = cell_label(loc, et)
        rows.append({
            "location": loc, "edit_type": et, "events": n,
            "share": f"{n / total * 100:.1f}%", "errant_gec": cat,
            "normalization": norm, "status": status, "caveat": caveat,
        })
    return total, rows


def render_table(total, rows):
    out = [BEGIN, "",
           f"Per-cell crosswalk over the released corpus — {total:,} events, "
           f"{len(rows)} occupied (location × edit-type) cells "
           "(the full label vocabulary admits 8 locations × 9 edit-types = 72 cells; "
           "`crossref` occurs 0 times in the release and is reported absent rather "
           "than invented, leaving 63 addressable cells, of which 57 are occupied). "
           "Ordered by event volume.", "",
           "| location | edit-type | events | share | nearest ERRANT/GEC category | nearest historical-normalization term | placement | caveat |",
           "|---|---|---:|---:|---|---|---|---|"]
    for r in rows:
        out.append(f"| {r['location']} | {r['edit_type']} | {r['events']:,} | {r['share']} "
                   f"| {r['errant_gec']} | {r['normalization']} | **{r['status']}** "
                   f"| {r['caveat']} |")
    out += ["", f"**Structural mismatch, stated once for all cells.** {LOCATION_BLIND} "
            f"`unattributed`-location cells ({sum(r['events'] for r in rows if r['location'] == 'unattributed'):,} "
            "events) additionally have no location at all — they are reported here for the "
            "edit-type half of the cell only.", "",
            f"Status rollup: **PLACEABLE {sum(1 for r in rows if r['status'] == 'PLACEABLE')}"
            f" · PARTIAL {sum(1 for r in rows if r['status'] == 'PARTIAL')}"
            f" · UNPLACEABLE {sum(1 for r in rows if r['status'] == 'UNPLACEABLE')}** cells; "
            f"by events: PLACEABLE {sum(r['events'] for r in rows if r['status'] == 'PLACEABLE'):,}"
            f" / PARTIAL {sum(r['events'] for r in rows if r['status'] == 'PARTIAL'):,}"
            f" / UNPLACEABLE {sum(r['events'] for r in rows if r['status'] == 'UNPLACEABLE'):,}.", "",
            END]
    return "\n".join(out)


def main():
    check = "--check" in sys.argv
    total, rows = build_rows()
    rendered = render_table(total, rows)
    if not os.path.exists(DOC):
        sys.exit(f"missing {DOC}; the hand-authored narrative must exist first")
    with open(DOC, encoding="utf-8") as f:
        text = f.read()
    pattern = re.compile(re.escape(BEGIN) + r".*?" + re.escape(END), re.DOTALL)
    if not pattern.search(text):
        sys.exit("GENERATED markers not found in doc")
    new_text = pattern.sub(lambda m: rendered, text, count=1)
    if check:
        if new_text == text:
            print(f"CHECK PASS: {DOC} generated table is byte-identical ({len(rows)} cells over {total:,} events)")
        else:
            print(f"CHECK FAIL: {DOC} is stale — rerun without --check")
            sys.exit(1)
        return
    with open(DOC, "w", encoding="utf-8") as f:
        f.write(new_text)
    print(f"wrote {DOC} ({len(rows)} cells over {total:,} events)")
    st = Counter(r["status"] for r in rows)
    print(f"  status: {dict(st)}")


if __name__ == "__main__":
    main()
